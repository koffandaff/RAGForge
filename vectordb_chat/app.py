"""
Main Streamlit App - VectorDB Chat
Entry point that sets up the multi-page app structure
"""
import streamlit as st

st.set_page_config(
    page_title="VectorDB Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
) 

st.title("🤖 VectorDB Chat with Local LLM")
st.markdown("""
Welcome to your personal RAG (Retrieval Augmented Generation) system!
This app lets you:
- 📁 **Upload** documents under unique titles
-  **Chat** with your documents using local LLM
-  **Search** across different knowledge bases

Navigate using the sidebar to get started!
""")

# Display current setup info
if "titles" in st.session_state:
    st.sidebar.subheader("Available Titles")
    for title in st.session_state.titles:
        st.sidebar.info(f" {title}")
else:
    st.sidebar.info("No titles yet. Go to Upload page to create one!")

# Add some helpful tips
with st.expander(" Quick Tips"):
    st.markdown("""
    1. **Start with Upload page** to create your first knowledge base
    2. **Use descriptive titles** like "Cybersecurity Notes" or "Python Documentation"
    3. **Chunk size matters** - 300-500 tokens works best
    4. **Select relevant titles** when chatting for better context
    5. **Experiment** with different queries to see RAG in action!
    """)
