"""
LEARNING PHASE: Full Vector DB Pipeline
----------------------------------------
This file combines all previous learning modules into one single, 
executable RAG pipeline.

FLOW: File -> Extract -> Chunk -> Embed -> Store -> Query -> Retrieve -> LLM
"""

# We import all the modules we created in the Learning Phase
import os
import sys

# To make sure we can import local files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_extraction import extract_text_from_file_educational
from chunking_logic import educational_chunk_logic
from embedding_model import EducationalEmbedder
from vector_storage import EducationalVectorDB
from query_and_retrieval import educational_retrieval_flow
from llm_integration import EducationalLLM

def run_learning_pipeline(file_to_index: str, question: str):
    """
    Executes the entire RAG pipeline from start to finish.
    """
    
    print("\n" + "="*50)
    print("STARTING FULL RAG PIPELINE")
    print("="*50)

    # PAGE 1: EXTRACTION
    # We take a file and turn it into a long string.
    raw_text = extract_text_from_file_educational(file_to_index)
    if not raw_text or len(raw_text) < 10:
        print("Error: Extraction failed or file too small.")
        return

    # PAGE 2: CHUNKING
    # We cut the long string into smaller overlapping paragraphs.
    chunks = educational_chunk_logic(raw_text, size=500, overlap=50)

    # PAGE 3: EMBEDDING (THE MODEL)
    # Load the AI model that understands language math.
    embedder = EducationalEmbedder()

    # PAGE 4: VECTORIZATION (BATCH)
    # Convert all our text chunks into lists of numbers (vectors).
    print(f"Creating vectors for {len(chunks)} chunks...")
    chunk_vectors = embedder.create_batch_vectors(chunks)

    # PAGE 5: STORAGE (THE DATABASE)
    # Save these vectors and text into a FAISS index.
    vector_db = EducationalVectorDB(dimension=embedder.dim)
    vector_db.add_data(chunks, chunk_vectors)

    # PAGE 6: RETRIEVAL (THE SEARCH)
    # Search for the parts of the document that answer the user's question.
    context = educational_retrieval_flow(question, embedder, vector_db, k=4)
    
    if not context:
        print("Warning: No relevant document context was found for this query.")

    # PAGE 7: GENERATION (THE LLM)
    # Ask the local LLM (Ollama) to answer based on what we found.
    llm = EducationalLLM()
    final_answer = llm.ask_with_context(question, context)

    # FINAL OUTPUT
    print("\n" + "="*50)
    print("FINAL AI RESPONSE:")
    print("-" * 50)
    print(final_answer)
    print("="*50)

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Provide a file you want the AI to read
    # (Create a small .txt file first to test!)
    test_file_path = "e:/AutoRagOfDocs/LearningPhase/my_test_notes.txt"
    
    # Let's create a temporary test file if it doesn't exist
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w", encoding='utf-8') as f:
            f.write("My goal is to become a Full Stack Developer. I am 22 years old. My name is Dhruvil.")
    
    # 2. Ask a question about that file
    user_question = "What is the user's goal and name?"
    
    # 3. Run the pipeline
    run_learning_pipeline(test_file_path, user_question)
