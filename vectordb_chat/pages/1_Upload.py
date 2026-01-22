"""
Upload Page: Create titles and upload documents
"""
import streamlit as st
import json
from pathlib import Path
import tempfile
import time
import sys
import os

# Add root to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from vectordb.index_manager import IndexManager
from utils.text_utils import chunk_text, extract_text_from_file

# Page config
st.set_page_config(page_title="Upload Documents", page_icon="📁")

st.title("📁 Upload Documents")
st.markdown("Create knowledge bases by uploading documents under unique titles.")

# Initialize IndexManager
@st.cache_resource
def get_index_manager():
    return IndexManager(storage_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage"))

index_manager = get_index_manager()

# Sidebar: Existing titles
st.sidebar.title("📚 Existing Titles")
existing_titles = index_manager.get_all_titles()

if existing_titles:
    for title in existing_titles:
        info = index_manager.get_title_info(title)
        if info:
            with st.sidebar.expander(f" {title}"):
                st.write(f" {info['chunk_count']} chunks")
                if st.button(f"🗑️ Delete {title}", key=f"del_{title}"):
                    if index_manager.delete_title(title):
                        st.success(f"Deleted {title}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed to delete {title}")
else:
    st.sidebar.info("No titles yet. Create your first one!")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Create or Select Title")
    
    # Title input
    new_title = st.text_input(
        "Title Name",
        placeholder="e.g., Cybersecurity Notes, Python Docs",
        help="Create a unique title for your documents"
    )
    
    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["Create New Title", "Add to Existing Title"],
        help="Create a new knowledge base or add to existing one"
    )
    
    selected_title = None
    
    if mode == "Add to Existing Title" and existing_titles:
        selected_title = st.selectbox(
            "Select Existing Title",
            existing_titles,
            help="Choose a title to add more documents to"
        )
    elif mode == "Add to Existing Title" and not existing_titles:
        st.warning("No existing titles. Please create a new one first.")
        mode = "Create New Title"
    
    # Validate title
    if mode == "Create New Title" and new_title:
        normalized = new_title.strip().lower()
        existing_normalized = [t.lower() for t in existing_titles]
        if normalized in existing_normalized:
            st.error(f"Title '{new_title}' already exists!")
            new_title = ""

with col2:
    st.subheader("Upload Content")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method",
        ["Paste Text", "Upload File"],
        horizontal=True
    )
    
    content_text = ""
    
    if input_method == "Paste Text":
        content_text = st.text_area(
            "Paste your text here",
            height=200,
            placeholder="Paste your document content here...",
            help="Text will be automatically chunked into smaller pieces"
        )
        
        # Show chunk preview
        if content_text:
            chunks = chunk_text(content_text)
            st.info(f"Will create approximately {len(chunks)} chunks")
            
            with st.expander("Preview chunks"):
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    st.caption(f"Chunk {i+1} ({len(chunk.split())} words):")
                    st.text(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    
    else:  # Upload File
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml', 'pdf', 'docx', 'doc'],
            accept_multiple_files=True,
            help="Supported: .txt, .md, .py, .js, .html, .css, .json, .xml, .pdf, .docx, .doc"
        )
        
        if uploaded_files:
            all_content = []
            for uploaded_file in uploaded_files:
                file_content = uploaded_file.read()
                text = extract_text_from_file(file_content, uploaded_file.name)
                all_content.append(f"--- File: {uploaded_file.name} ---\n{text}")
            
            content_text = "\n\n".join(all_content)
            st.success(f"Loaded {len(uploaded_files)} file(s)")
            
            # Show preview
            with st.expander("Preview loaded content"):
                st.text(content_text[:500] + "..." if len(content_text) > 500 else content_text)

# Submit button
submit_button = st.button(
    "Process and Add to Vector DB",
    type="primary",
    disabled=not content_text.strip(),
    use_container_width=True
)

# Processing logic
if submit_button:
    with st.spinner("Processing..."):
        try:
            # Determine target title
            if mode == "Create New Title":
                if not new_title.strip():
                    st.error("Please enter a title name")
                    st.stop()
                
                target_title = new_title.strip()
                
                # Create new title
                success = index_manager.create_title(target_title)
                if not success:
                    st.error(f"Failed to create title '{target_title}'")
                    st.stop()
                
                st.success(f"Created new title: {target_title}")
                
            else:  # Add to Existing Title
                if not selected_title:
                    st.error("Please select an existing title")
                    st.stop()
                
                target_title = selected_title
            
            # Chunk and add to index
            chunks = chunk_text(content_text)
            
            if not chunks:
                st.error("No valid chunks extracted from content")
                st.stop()
            
            # Add to index
            added_count = index_manager.add_documents(target_title, chunks)
            
            # Show results
            st.balloons()
            st.success(f"""
            Successfully added {added_count} chunks to **{target_title}**
            
            **Next Steps:**
            1. Go to the Chat page
            2. Select **{target_title}** from the filter
            3. Start asking questions about your documents!
            """)
            
            # Refresh page to show updated titles
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
            st.exception(e)

# Information section
st.markdown("---")
with st.expander(" How to use this page"):
    st.markdown("""
    **Best Practices:**
    
    1. **Use Descriptive Titles**: e.g., "Python ML Tutorial", "Company Policies 2024"
    2. **Group Related Content**: Put similar documents under the same title
    3. **Ideal Chunk Size**: 300-500 words per chunk for best results
    4. **File Support**: Start with .txt or .md files for testing
    
    **What Happens Behind the Scenes:**
    1. Your text is split into overlapping chunks
    2. Each chunk is converted to a vector (number representation)
    3. Vectors are stored in a FAISS index (optimized for similarity search)
    4. When you chat, we find the most relevant chunks to answer your questions
    """)

# Debug section (optional)
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("### Debug Information")
    st.sidebar.json(index_manager.titles)
