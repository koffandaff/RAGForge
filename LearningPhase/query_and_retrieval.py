"""
LEARNING PHASE: Query and Retrieval
------------------------------------
This file explains the logic of taking a user's question,
finding the right documents, and preparing them for the AI.
"""

# This file would typically import the previous modules
# from embedding_model import EducationalEmbedder
# from vector_storage import EducationalVectorDB

def educational_retrieval_flow(user_query: str, embedder, vector_db, k: int = 3):
    """
    Shows the step-by-step logic of how a query is handled.
    """
    
    print(f"\n--- Processing User Query: '{user_query}' ---")
    
    # STEP 1: VECTORIZE THE QUESTION
    # We can't search for the word 'Python' in a database of numbers.
    # We must turn the word 'Python' into its own 384D number vector.
    print("Step 1: Embedding the question...")
    query_vector = embedder.create_vector(user_query)
    
    # STEP 2: SEARCH THE VECTOR DB
    # We ask the index: "Which documents are mathematically 'closest' to this coordinate?"
    print(f"Step 2: Searching top {k} relevant documents in FAISS index...")
    raw_results = vector_db.search_nearest(query_vector, top_k=k)
    
    # STEP 3: RELEVANCE FILTERING
    # Sometimes search returns items that aren't very similar.
    # Scores > 0.6 are usually 'good' matches for this model.
    print("Step 3: Filtering and formatting context...")
    filtered_context = []
    for res in raw_results:
        # Higher score = more relevant
        if res['similarity'] > 0.4:  # Adjust threshold as needed
            filtered_context.append(res['text'])
            print(f"   [FOUND] Score: {res['similarity']:.3f} | Text: {res['text'][:60]}...")
            
    # STEP 4: BUILDING THE PROMPT CONTEXT
    # We join all found information into a single string to feed the LLM.
    context_string = "\n\n".join(filtered_context)
    
    return context_string

# --- THE GOAL OF RETRIEVAL ---
# The goal is not 'finding the file'. 
# The goal is 'minimizing noise'. 
# By only picking the top-K chunks, we save the LLM from reading irrelevant data
# and prevent it from getting confused by off-topic information.

if __name__ == "__main__":
    pass
