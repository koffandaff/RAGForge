# Relevance Search and Indexing Logic

This document provides a deep dive into how the system performs vector similarity search and manages document indexing.

## 1. Indexing Strategy

When a new knowledge base (Title) is created, the system initializes a **FAISS Index**.

### Library: `faiss-cpu`
We use FAISS (Facebook AI Similarity Search) because it is highly optimized for searching vectors in high-dimensional spaces.

### Code Explanation: `IndexManager.create_title`
```python
# dimension is 384 for all-MiniLM-L6-v2
dimension = self.embedder.embedding_dim
index = faiss.IndexFlatIP(dimension)  # IndexFlatIP means Inner Product
```
- **IndexFlatIP**: This index type calculates the Inner Product. Since our embeddings are normalized by the `Embedder`, the Inner Product is equivalent to **Cosine Similarity**.
- **Normalization**: In `Embedder.embed_texts`, we set `normalize_embeddings=True`. This ensures all vectors have a length of 1, placing them on a unit hypersphere.

### Mathematical Logic: Cosine Similarity
For two normalized vectors $A$ and $B$, their Cosine Similarity is:
$$\text{similarity} = A \cdot B = \sum_{i=1}^{n} A_i B_i$$
This is exactly what `IndexFlatIP` calculates.

## 2. Document Addition

When chunks are added, they are converted to vectors and appended to the index.

### Code Explanation: `IndexManager.add_documents`
```python
embeddings = self.embedder.embed_texts(chunks)
index.add(embeddings) # Vectors are added to the flat index
```
The index maintains a direct 1-to-1 mapping between the vector ID (0, 1, 2...) and the order in which chunks were added. We store the actual text chunks in a separate JSON file (`{title}_chunks.json`) to retrieve them later using these IDs.

## 3. Relevance Search

### Code Explanation: `IndexManager.search`
```python
# 1. Encode query
query_embedding = self.embedder.embed_query(query)

# 2. Search index
# distances: similarity scores (higher is better for IP)
# indices: the IDs of the matching chunks
distances, indices = index.search(query_embedding, k)
```

### Search Workflow:
1.  **Query Encoding**: The user's query is transformed into a 384-dimensional vector.
2.  **Top-K Retrieval**: FAISS scans all stored vectors and finds the $k$ closest vectors to the query vector based on the Inner Product.
3.  **Result Mapping**: The system uses the returned `indices` to lookup the corresponding text in the JSON chunk store.

### Library Choice: Why FAISS?
- **Speed**: Even for thousands of documents, the search is sub-millisecond.
- **Memory Efficiency**: The flat index stores raw vectors without complex trees, striking a good balance for local app usage.
