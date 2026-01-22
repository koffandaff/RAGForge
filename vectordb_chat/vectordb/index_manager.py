"""
FAISS index manager for storing and retrieving document embeddings
Each title gets its own FAISS index
"""
import faiss
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path

from vectordb.embedder import Embedder

logger = logging.getLogger(__name__)

class IndexManager:
    """
    Manages FAISS indices for different titles.
    Each title = separate vector space.
    """
    
    def __init__(self, storage_dir: str = "storage"):
        """
        Initialize index manager.
        
        Args:
            storage_dir: Root directory for storage
        """
        self.storage_dir = Path(storage_dir)
        self.faiss_dir = self.storage_dir / "faiss"
        self.titles_file = self.storage_dir / "titles.json"
        
        # Create directories if they don't exist
        self.faiss_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedder
        self.embedder = Embedder()
        
        # Load existing titles
        self.titles = self._load_titles()
    
    def _load_titles(self) -> Dict:
        """Load titles from JSON file"""
        if self.titles_file.exists():
            try:
                with open(self.titles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading titles: {e}")
                return {}
        return {}
    
    def _save_titles(self):
        """Save titles to JSON file"""
        try:
            with open(self.titles_file, 'w') as f:
                json.dump(self.titles, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving titles: {e}")
    
    def create_title(self, title: str) -> bool:
        """
        Create a new title with empty FAISS index.
        
        Args:
            title: Title name (case-insensitive, normalized)
            
        Returns:
            True if created successfully
        """
        # Normalize title
        normalized = title.strip().lower()
        display_title = title.strip()
        
        # Check if title already exists
        if normalized in self.titles:
            logger.warning(f"Title '{display_title}' already exists")
            return False
        
        # Create FAISS index
        index_path = self.faiss_dir / f"{normalized}.index"
        
        # Create empty index
        dimension = self.embedder.embedding_dim
        index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
        
        # Save index
        faiss.write_index(index, str(index_path))
        
        # Create chunk storage
        chunks_path = self.faiss_dir / f"{normalized}_chunks.json"
        with open(chunks_path, 'w') as f:
            json.dump([], f)  # Empty list for chunks
        
        # Update titles mapping
        self.titles[normalized] = {
            "display_name": display_title,
            "index_file": str(index_path),
            "chunks_file": str(chunks_path),
            "chunk_count": 0
        }
        
        self._save_titles()
        logger.info(f"Created title: {display_title}")
        return True
    
    def add_documents(self, title: str, chunks: List[str]) -> int:
        """
        Add document chunks to a title's index.
        
        Args:
            title: Title name
            chunks: List of text chunks
            
        Returns:
            Number of chunks added
        """
        normalized = title.strip().lower()
        
        if normalized not in self.titles:
            raise ValueError(f"Title '{title}' does not exist")
        
        if not chunks:
            return 0
        
        # Load existing chunks
        chunks_path = Path(self.titles[normalized]["chunks_file"])
        with open(chunks_path, 'r') as f:
            existing_chunks = json.load(f)
        
        # Load existing index
        index_path = Path(self.titles[normalized]["index_file"])
        index = faiss.read_index(str(index_path))
        
        # Embed new chunks
        embeddings = self.embedder.embed_texts(chunks)
        
        if len(embeddings) == 0:
            return 0
        
        # Add to index
        index.add(embeddings)
        
        # Update chunks
        existing_chunks.extend(chunks)
        
        # Save everything
        faiss.write_index(index, str(index_path))
        
        with open(chunks_path, 'w') as f:
            json.dump(existing_chunks, f, indent=2)
        
        # Update metadata
        self.titles[normalized]["chunk_count"] = len(existing_chunks)
        self._save_titles()
        
        logger.info(f"Added {len(chunks)} chunks to title '{title}'")
        return len(chunks)
    
    def search(self, title: str, query: str, k: int = 4) -> List[Tuple[str, float]]:
        """
        Search for similar chunks in a title.
        
        Args:
            title: Title name
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (chunk_text, similarity_score) tuples
        """
        normalized = title.strip().lower()
        
        if normalized not in self.titles:
            raise ValueError(f"Title '{title}' does not exist")
        
        # Load chunks
        chunks_path = Path(self.titles[normalized]["chunks_file"])
        with open(chunks_path, 'r') as f:
            all_chunks = json.load(f)
        
        if not all_chunks:
            return []
        
        # Load index
        index_path = Path(self.titles[normalized]["index_file"])
        index = faiss.read_index(str(index_path))
        
        # Embed query
        query_embedding = self.embedder.embed_query(query)
        
        # Search
        k = min(k, len(all_chunks))
        distances, indices = index.search(query_embedding, k)
        
        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(all_chunks):  # Safety check
                # FAISS returns similarity scores (higher = more similar)
                results.append((all_chunks[idx], float(dist)))
        
        return results
    
    def get_all_titles(self) -> List[str]:
        """Get list of all title display names"""
        return [info["display_name"] for info in self.titles.values()]
    
    def get_title_info(self, title: str) -> Optional[Dict]:
        """Get information about a title"""
        normalized = title.strip().lower()
        return self.titles.get(normalized)
    
    def delete_title(self, title: str) -> bool:
        """Delete a title and all its data"""
        normalized = title.strip().lower()
        
        if normalized not in self.titles:
            return False
        
        # Delete files
        try:
            index_path = Path(self.titles[normalized]["index_file"])
            chunks_path = Path(self.titles[normalized]["chunks_file"])
            
            if index_path.exists():
                index_path.unlink()
            if chunks_path.exists():
                chunks_path.unlink()
            
            # Remove from titles
            del self.titles[normalized]
            self._save_titles()
            
            logger.info(f"Deleted title: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting title '{title}': {e}")
            return False
