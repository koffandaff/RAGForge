"""
LEARNING PHASE: Embedding Models
--------------------------------
This file explains how text is converted into numbers (Vectors).
The computer doesn't 'read' words; it calculates 'vectors'.
"""

# We use 'sentence-transformers', which is a library built on top of PyTorch/HuggingFace.
# It makes it very easy to load state-of-the-art BERT models.
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Please run 'pip install sentence-transformers'")

# NumPy is used locally for all mathematical list operations
import numpy as np

class EducationalEmbedder:
    """
    A class that manages our AI model for turning text into vectors.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialization phase.
        
        Args:
            model_name: The name of the AI model on HuggingFace.
                       'all-MiniLM-L6-v2' is small, fast, and has 384 dimensions.
        """
        print(f"--- Loading AI Model: {model_name} ---")
        
        # 1. Load the model from disk (or download if it's the first time)
        # This model is essentially a massive neural network file.
        self.model = SentenceTransformer(model_name)
        
        # 2. Extract the 'dimension'
        # For this model, every sentence becomes a list of 384 numbers.
        self.dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Dimension: {self.dim}")

    def create_vector(self, text: str) -> np.ndarray:
        """
        Turns a single piece of text into a vector.
        """
        # 3. The 'Encoding' process
        # This passes the text THROUGH the neural network.
        # The network outputs a representation of the 'meaning' as a list of numbers.
        
        # normalize_embeddings=True scales the vector so its 'length' is 1.0.
        # This is vital for Cosine Similarity (measuring angles between words).
        vector = self.model.encode(
            [text], # Put in list as model expects batch
            normalize_embeddings=True, 
            convert_to_numpy=True
        )
        
        # Returning index 0 because we only passed one string
        return vector[0]

    def create_batch_vectors(self, texts: list) -> np.ndarray:
        """
        Efficiently turns MANY pieces of text into vectors at once.
        """
        # Models are faster when they process 'batches' instead of one-by-one
        # because they can use parallel math on the CPU/GPU.
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return vectors

# --- WHAT IS A VECTOR? ---
# Think of it as a coordinate. 
# In 2D, (1, 0) is East. (0, 1) is North.
# In 384D, a vector at some specific position might mean 'Technology'.
# A vector near it might mean 'Software'. 
# Distance = Difference in meaning.

if __name__ == "__main__":
    eng = EducationalEmbedder()
    vec = eng.create_vector("Hello World")
    print(f"Vector shape: {vec.shape}") # Should be (384,)
    print(f"First 5 numbers: {vec[:5]}")
