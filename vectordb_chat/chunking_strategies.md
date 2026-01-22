# Chunking Strategies and Logic

Chunking is the process of breaking long documents into smaller, manageable fragments. This document explains the math and logic behind our implementation in `utils/text_utils.py`.

## 1. Why Chunk?

LLMs (like those in Ollama) and Embedding models (like `all-MiniLM-L6-v2`) have **Context Windows**.
- **Embedding limit**: Usually 256 or 512 tokens.
- **LLM limit**: usually 4k-32k tokens.
- **Precision**: Searching for a small relevant paragraph is more accurate than searching for a 50-page book.

## 2. The Logic: Paragraph-Aware Chunking

Our implementation doesn't just cut text at random characters; it respects paragraph boundaries.

### Multi-Step Process:
1.  **Cleaning**: Remove redundant whitespace using Regex `\s+`.
2.  **Splitting**: Divide text by `\n` to find natural breaks.
3.  **Aggregation**: Group paragraphs together until the `chunk_size` is reached.

### Code Logic:
```python
for para in paragraphs:
    para_tokens = len(para.split()) # Approximate tokens by word count
    
    # Check if adding this paragraph exceeds chunk size
    if current_length + para_tokens > chunk_size and current_chunk:
        chunks.append('\n'.join(current_chunk))
        
        # Start new chunk with overlap
        if overlap > 0:
            last_sentences = current_chunk[-2:] # Keep last 2 paragraphs
            current_chunk = last_sentences.copy()
```

## 3. The Math of Overlap

We use **Sliding Window** chunking with a defined overlap.

### Variables:
- $L$: Total length of document
- $C$: Chunk size (e.g., 500 words)
- $O$: Overlap (e.g., 50 words)

### Chunk Distribution:
The starting point of chunk $n$ is:
$$\text{Start}_n = n \times (C - O)$$
This ensures that if a key sentence is split between Chunk 1 and Chunk 2, the overlapping area captures it in its entirety in at least one (or both) chunks, preserving semantic meaning.

## 4. Edge Case Handling: Long Paragraphs

If a single paragraph is longer than the `chunk_size`, the system switches to a strict word-count split:

```python
if para_tokens > chunk_size:
    words = para.split()
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunks.append(' '.join(chunk_words))
```

## Parameter Impact

| Parameter | High Value | Low Value |
| :--- | :--- | :--- |
| **Chunk Size** | More context per result, but less specific matches. | Very specific matches, but might lose surrounding nuance. |
| **Overlap** | Better continuity, but more redundant data in DB. | Less redundancy, but higher risk of cutting sentences in half. |

In this application, we default to **500 words** with **50 words overlap** as a proven "sweet spot" for general documentation.
