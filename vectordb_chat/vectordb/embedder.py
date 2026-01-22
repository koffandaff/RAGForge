"""
Embedding model wrapper for Sentence Transformers
Loads once and reuses across the app
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class Embedder:
    """
    Singleton-like embedding model manager.
    Loads model once and provides embedding methods.
    """
    _instance = None
    _model = None
    _model_name = "all-MiniLM-L6-v2"  # Small, fast, good quality
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance
    
    def _initialize_model(self):
        """Initialize the SentenceTransformer model"""
        try:
            logger.info(f"Loading embedding model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts into vectors.
        
        Args:
            texts: List of text strings
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Clean texts
        texts = [text.strip() for text in texts if text.strip()]
        
        if not texts:
            return np.array([])
        
        try:
            embeddings = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,  # Important for cosine similarity
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        
        Args:
            query: Query text
            
        Returns:
            numpy array of shape (1, embedding_dim)
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            embedding = self._model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            # Reshape to 2D array for consistency
            return embedding.reshape(1, -1)
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise
    
    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension of the model"""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 384  # Default for all-MiniLM-L6-v2
