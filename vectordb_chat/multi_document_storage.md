# Multi-Document Storage Organization

This document details how the system organizes and maintains multiple distinct document collections (titles) on disk.

## 1. Directory Structure

The system uses a hierarchical file structure located in the `storage/` directory.

```
storage/
├── titles.json           # Global registry of all titles
└── faiss/                # Vector space storage
    ├── cybersecurity.index      # Binary vector data
    ├── cybersecurity_chunks.json # Text fragments
    ├── my_notes.index
    └── my_notes_chunks.json
```

## 2. The Global Registry: `titles.json`

This file is the "Brain" of the storage system. It maps display names (like "Cybersecurity") to their internal file paths.

### Sample Structure:
```json
{
  "cybersecurity": {
    "display_name": "Cybersecurity",
    "index_file": "storage\\faiss\\cybersecurity.index",
    "chunks_file": "storage\\faiss\\cybersecurity_chunks.json",
    "chunk_count": 142
  }
}
```
- **Normalization**: Keys are lower-cased and stripped to prevent duplicate titles (e.g., "AI" and "ai" are treated as the same).
- **Metadata**: Storing `chunk_count` allows the UI to display statistics without needing to load and count every vector in the index.

## 3. Title Lifecycle Logic

In `vectordb/index_manager.py`, we implement a full CRUD lifecycle for these documents.

### Creation (`create_title`)
- Initialized with an empty `IndexFlatIP`.
- Creates a placeholder JSON array `[]` for chunks.
- Writes metadata to `titles.json`.

### Modification (`add_documents`)
- Reads existing index and JSON.
- Appends new data.
- Increments `chunk_count`.
- Writes back to disk.

### Deletion (`delete_title`)
- Removes the specific `.index` and `_chunks.json` files.
- Purges the entry from `titles.json`.
- This ensures that no "ghost" documents remain in the system.

## 4. Why Distant Indices?

Instead of putting all documents into one giant index, we keep them separate.

| Pros of Separate Indices | Why it matters |
| :--- | :--- |
| **Speed** | Smaller indices are faster to scan and faster to load from disk. |
| **User Control** | Users can choose exactly which "context" the AI should use for each question. |
| **Maintenance** | Deleting one document doesn't require rebuilding or re-indexing others. |
| **Collision Avoidance** | Prevents unrelated documents from diluting the relevance of specific searches. |

This organization makes the RAG system modular and user-centric, allowing for personalized knowledge "compartments".
