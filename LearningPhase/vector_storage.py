"""
LEARNING PHASE: Vector Storage (FAISS)
---------------------------------------
This file explains how we store millions of vectors and find the closest one.
We use FAISS (Facebook AI Similarity Search).
"""

# FAISS is the industry standard for fast vector search.
# 'faiss-cpu' is our library choice.
try:
    import faiss
except ImportError:
    print("Error: Please run 'pip install faiss-cpu'")

import numpy as np

class EducationalVectorDB:
    """
    Manages the 'Brain' (Index) where knowledge is stored.
    """
    
    def __init__(self, dimension: int):
        """
        Args:
            dimension: How many numbers are in each vector (e.g., 384)
        """
        # 1. Choose the Index Type
        # 'IndexFlatIP' stands for 'Index Flat Inner Product'.
        # Since we use NORMALIZED vectors, Inner Product = Cosine Similarity.
        # 'Flat' means it searches everything (brute force), which is fast enough for local apps.
        self.index = faiss.IndexFlatIP(dimension)
        
        # We also need a way to store the actual text chunks, 
        # because the FAISS index only stores the numbers, not the text!
        self.chunk_repository = [] 
        
        print(f"--- FAISS Index Initialized (Dim: {dimension}) ---")

    def add_data(self, chunks: list, vectors: np.ndarray):
        """
        Saves chunks and their vectors into the index.
        
        Args:
            chunks: List of strings (human text)
            vectors: 2D array of floats (AI numbers)
        """
        # 2. Store the human text in our list
        # We use a simple list where list index (0, 1, 2...) matches FAISS ID
        self.chunk_repository.extend(chunks)
        
        # 3. Add to FAISS index
        # This converts our NumPy math into the highly optimized C++ structure of FAISS
        self.index.add(vectors.astype('float32'))
        
        print(f"Added {len(chunks)} items to the brain.")

    def search_nearest(self, query_vector: np.ndarray, top_k: int = 4):
        """
        Finds the top-K most similar items to a query.
        """
        # 4. Perform the mathematical search
        # query_vector must be 2D, e.g., (1, 384)
        # .search() calculates the inner product between query and every vector in DB.
        
        # D = Distances (How similar it is. Higher = more similar)
        # I = Indices (The IDs of the matching items)
        D, I = self.index.search(query_vector.reshape(1, -1).astype('float32'), top_k)
        
        # 5. Extract results
        results = []
        # distances and indices come as nested lists [[d1, d2...], [i1, i2...]]
        for distance, idx in zip(D[0], I[0]):
            # Use the ID to get the original text from our repo
            text = self.chunk_repository[idx]
            results.append({
                "text": text,
                "similarity": float(distance)
            })
            
        return results

# --- HOW FAISS WORKS ---
# It's basically a massive distance table. 
# When you search, it performs matrix multiplication: 
# [Query] * [Database Matrix] = [Scores]
# It then returns the top results from the Scores list.

if __name__ == "__main__":
    # Test index with 384 dims
    db = EducationalVectorDB(384)
    # result = db.search_nearest(np.random.rand(384), k=2)
    pass
