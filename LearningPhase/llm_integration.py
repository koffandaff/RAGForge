"""
LEARNING PHASE: LLM Integration (RAG)
---------------------------------------
This file explains how we take the retrieved context and ask the LLM
to generate a grounded answer. We use Ollama.
"""

import requests
import json

class EducationalLLM:
    """
    Client helper to talk to local Ollama server.
    """
    
    def __init__(self, model: str = "deepseek-coder:6.7b"):
        # Ollama usually runs on port 11434
        self.url = "http://localhost:11434/api/chat"
        self.model = model
        print(f"--- LLM Setup: Using model '{model}' via Ollama ---")

    def ask_with_context(self, user_question: str, context: str):
        """
        The core RAG generation logic.
        """
        
        # 1. BUILD THE SYSTEM INSTRUCTION
        # We tell the AI how it should behave.
        # This is where we force it to be 'grounded' in the context.
        system_prompt = (
            "You are a strictly grounded AI assistant. "
            "1. Use ONLY the provided Context to answer the Question. "
            "2. If the answer is not in the context, say 'I cannot find that in the documents.' "
            "3. Do not use your own prior knowledge."
        )
        
        # 2. FORMAT THE USER MESSAGE
        # We combine the retrieved facts with the actual question.
        user_prompt = (
            f"Here is the context I found in my database:\n\n"
            f"{context}\n\n"
            f"Question: {user_question}"
        )
        
        # 3. CONSTRUCT THE CHAT PAYLOAD
        # Ollama's /api/chat expects a list of messages with 'roles'.
        # role: 'system' -> Instructions
        # role: 'user'   -> The query
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False # Set to True for streaming
        }
        
        print("Finalizing prompt and sending to LLM...")
        
        # 4. SEND THE REQUEST
        try:
            response = requests.post(self.url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # The actual AI answer is in result['message']['content']
                ai_answer = result.get('message', {}).get('content', '')
                return ai_answer
            else:
                return f"Error from Ollama: {response.text}"
                
        except Exception as e:
            return f"Connection Failed: Ensure Ollama is running. Error: {str(e)}"

# --- WHAT IS 'GROUNDING'? ---
# Grounding is anchoring the AI's 'imagination' to 'real facts' provided in the prompt.
# Without grounding, AI 'hallucinates' (makes up stuff that sounds true).
# With RAG context, the AI acts more like a search assistant than a creative writer.

if __name__ == "__main__":
    pass
