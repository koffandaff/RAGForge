# Embedding and Storage Logic

This document explains how text is converted into numbers (Embeddings) and how those numbers are stored in our Vector Database.

## 1. What is an Embedding?

An embedding is a vector (a list of numbers) that represents a piece of text. In our system, we use the `all-MiniLM-L6-v2` model.

### Library: `sentence-transformers`
This library provides a high-level API to load state-of-the-art BERT-based models for creating dense vector representations.

### Model Characteristics:
- **Dimensions**: 384. This means every chunk of text is turned into a list of 384 numbers.
- **Language**: Trained on 1B+ sentence pairs, making it excellent for general English documents.
- **Speed**: One of the fastest models available, ideal for local CPU execution.

## 2. Embedding Generation Logic

### Code Explanation: `Embedder.embed_texts`
```python
embeddings = self._model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False
)
```
- **convert_to_numpy**: Ensures we get a NumPy array, which is the required format for FAISS.
- **normalize_embeddings**: This is crucial. It scales every vector so that its magnitude (Euclidean length) is 1.0. This allows us to use **Inner Product** as a measure of **Cosine Similarity**.

## 3. Storage in Vector DB

We utilize a hybrid storage approach combining a binary vector index and a structured metadata store.

### FAISS Binary Storage (`.index`)
The vector index doesn't store the text itself. It only stores the 384 floating-point numbers for each chunk.
- **Logic**: When we call `faiss.write_index`, the optimized C++ data structures are serialized to disk. This is what allows for fast loading on the next app startup.

### JSON Metadata Storage (`_chunks.json`)
Since FAISS only returns integer IDs (0, 1, 2...), we need a way to map those IDs back to the original text.
- **Logic**: We store the chunks in a plain JSON list. If FAISS says the most relevant vector is at index `42`, we simply look up `chunks[42]` in our JSON file.

## 4. Why this Hybrid approach?

| Component | Role | Why? |
| :--- | :--- | :--- |
| **FAISS Index** | Search Engine | Extremely fast mathematical comparisons. |
| **JSON File** | Content Repository | Simple, human-readable, and easy to manage without complex DB overhead. |

This architecture ensures that our "Vector Database" remains portable—just two files per "Title"—making it easy to backup or delete.
