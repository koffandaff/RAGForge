"""
Chat Page: Interact with your documents using RAG
"""
import streamlit as st
from typing import List, Dict
import time
import sys
import os

# Add root to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from vectordb.index_manager import IndexManager
from llm.ollama_client import OllamaClient

# Page config
st.set_page_config(page_title="Chat with Docs", page_icon="💬")

# Initialize components
@st.cache_resource
def get_index_manager():
    return IndexManager(storage_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage"))

@st.cache_resource
def get_ollama_client():
    return OllamaClient()

index_manager = get_index_manager()
ollama_client = get_ollama_client()

# Title
st.title(" Chat with Your Documents")
st.markdown("Ask questions about your uploaded documents using RAG (Retrieval Augmented Generation)")

# Sidebar: Title selection and settings
st.sidebar.title(" Chat Settings")

# Get available titles
available_titles = index_manager.get_all_titles()

if not available_titles:
    st.warning("""
    No documents uploaded yet!
    
    Please go to the **Upload** page first to:
    1. Create a title
    2. Upload some documents
    3. Then come back here to chat
    """)
    if st.button("Go to Upload Page"):
        st.switch_page("pages/1_Upload.py")
    st.stop()

# Title selection (multi-select)
selected_titles = st.sidebar.multiselect(
    "Select Knowledge Base(s)",
    available_titles,
    default=available_titles[:1] if available_titles else [],
    help="Select one or more titles to search across"
)

# Number of context chunks
k_chunks = st.sidebar.slider(
    "Number of context chunks",
    min_value=1,
    max_value=10,
    value=4,
    help="More chunks = more context, but slower responses"
)

# Temperature
temperature = st.sidebar.slider(
    "Creativity (Temperature)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Higher = more creative, Lower = more focused"
)

# Show selected titles info
st.sidebar.markdown("---")
st.sidebar.subheader(" Selected Titles")
for title in selected_titles:
    info = index_manager.get_title_info(title)
    if info:
        st.sidebar.caption(f"**{title}** - {info['chunk_count']} chunks")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Validate selection
    if not selected_titles:
        st.error("Please select at least one title from the sidebar!")
        st.stop()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(" Thinking...")
        
        full_response = ""
        
        try:
            # Step 1: Search across all selected titles
            all_context = []
            
            with st.spinner(" Searching in documents..."):
                for title in selected_titles:
                    try:
                        results = index_manager.search(title, prompt, k=k_chunks)
                        for chunk, score in results:
                            all_context.append({
                                "title": title,
                                "chunk": chunk,
                                "score": score
                            })
                    except Exception as e:
                        st.warning(f"Could not search in '{title}': {str(e)}")
            
            # Sort by similarity score
            all_context.sort(key=lambda x: x["score"], reverse=True)
            
            # Take top k chunks overall
            top_context = all_context[:k_chunks]
            
            if not top_context:
                message_placeholder.markdown("I couldn't find relevant information in the selected documents.")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I couldn't find relevant information in the selected documents."
                })
                st.stop()
            
            # Step 2: Prepare context for LLM
            context_chunks = [item["chunk"] for item in top_context]
            
            # Show context being used (optional)
            with st.expander(" Context being used"):
                for i, item in enumerate(top_context):
                    st.caption(f"**From {item['title']}** (relevance: {item['score']:.3f})")
                    st.text(item['chunk'][:300] + "..." if len(item['chunk']) > 300 else item['chunk'])
                    st.divider()
            
            # Step 3: Generate streaming response with Ollama
            with st.spinner(" Generating response..."):
                context_str = "\n".join([f"- {c.strip()}" for c in context_chunks])
                
                system_msg = {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided context to answer the user's question accurately. If the answer is not in the context, say you don't know."
                }
                
                user_content = f"Context:\n{context_str}\n\nQuestion: {prompt}"
                
                messages = [system_msg]
                if st.session_state.conversation_history:
                    messages.extend(st.session_state.conversation_history[-4:])
                messages.append({"role": "user", "content": user_content})

                # Stream the response
                response_generator = ollama_client.chat_stream(messages, temperature=temperature)
                full_response = st.write_stream(response_generator)
            
            # Add to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error("An error occurred while processing your request.")

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History", type="secondary"):
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.rerun()

# Information section
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    with st.expander(" Tips for Better Results"):
        st.markdown("""
        **Ask Specific Questions:**
        - Instead of "Tell me about Python"
        - Try "What are Python decorators?"
        
        **Use Natural Language:**
        - "Explain how machine learning works"
        - "Summarize the main points"
        - "Compare X and Y"
        
        **Check Context:**
        - Expand the context view above
        - See what documents are being used
        """)

with col2:
    with st.expander(" How RAG Works"):
        st.markdown("""
        **Retrieval Augmented Generation:**
        
        1. **Query**: Your question is converted to a vector
        2. **Search**: Find similar text chunks in vector database
        3. **Context**: Top chunks are sent to LLM as context
        4. **Generation**: LLM answers based on provided context
        
        **Benefits:**
        - More accurate than LLM alone
        - Can cite specific document parts
        - No hallucination from missing knowledge
        """)

# Debug info
if st.sidebar.checkbox("Show Technical Info"):
    st.sidebar.write("### Technical Details")
    st.sidebar.write(f"Ollama Model: {ollama_client.model}")
    st.sidebar.write(f"Selected Titles: {len(selected_titles)}")
    st.sidebar.write(f"Total Chunks Available: {sum(index_manager.get_title_info(t)['chunk_count'] for t in selected_titles if index_manager.get_title_info(t))}")
