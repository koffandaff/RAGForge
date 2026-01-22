"""
LEARNING PHASE: Chunking Logic
--------------------------------
This file explains how long text is split into pieces (chunks) so the AI can process it.
We use an "Overlapping Window" strategy.
"""

import re
from typing import List

def educational_chunk_logic(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    """
    An educational implementation of text chunking.
    
    Args:
        text: The long raw string extracted from a file
        size: Target number of words per chunk
        overlap: How many words to repeat in the next chunk (context preservation)
    """

    # 1. CLEANING THE TEXT
    # We use Regular Expressions (re) to find sequences of whitespace (\s+) 
    # and replace them with a single space ' '.
    # This prevents 'empty chunks' caused by too many empty lines.
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. CONVERTING TO WORDS
    # .split() splits the string by spaces, creating a list of individual words.
    words = clean_text.split()
    total_words = len(words)
    
    print(f"--- Chunking Strategy: Size {size}, Overlap {overlap} ---")
    print(f"Total Words in Document: {total_words}")
    
    chunks = []
    
    # 3. THE LOOPING LOGIC
    # We iterate through the list of words using a 'step' size.
    # The step is (size - overlap). 
    # Example: Size 100, Overlap 20. Step is 80.
    # Chunk 1 starts at 0, goes to 100.
    # Chunk 2 starts at 80, goes to 180. (Words 80-100 are the 'overlap')
    
    for i in range(0, total_words, size - overlap):
        # Slice the list from index 'i' to 'i + size'
        chunk_words = words[i : i + size]
        
        # Join the words back together with spaces into a single string
        chunk_text = " ".join(chunk_words)
        
        # Add this new chunk to our list
        chunks.append(chunk_text)
        
        # SAFETY BREAK
        # If the next starting point is beyond the list, we stop.
        if i + size >= total_words:
            break
            
    print(f"Chunks Created: {len(chunks)}")
    return chunks

# --- WHY DO WE OVERLAP? ---
# Imagine a sentence like: "The password for the secret server is 12345."
# Without overlap, a chunk might end at "password for the secret" 
# and the next starts at "server is 12345."
# The AI would never see the connection!
# With overlap, BOTH chunks see the key connection.

if __name__ == "__main__":
    # Test text
    sample_text = "This is a long sentence repeated many times. " * 100
    my_chunks = educational_chunk_logic(sample_text, size=30, overlap=5)
    
    # Show first 2 chunks to see overlap
    for idx, c in enumerate(my_chunks[:2]):
        print(f"Chunk {idx+1}: {c[:100]}...")
