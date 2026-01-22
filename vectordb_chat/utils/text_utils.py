"""
Text processing utilities for chunking and cleaning
"""
import re
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better context retention.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum tokens per chunk (approximate)
        overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Clean the text first
    text = clean_text(text)
    
    # Split by paragraphs (natural breaks)
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para_tokens = len(para.split())  # Approximate token count
        
        # If paragraph itself is too long, split it
        if para_tokens > chunk_size:
            words = para.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunks.append(' '.join(chunk_words))
            continue
        
        # Check if adding this paragraph exceeds chunk size
        if current_length + para_tokens > chunk_size and current_chunk:
            # Save current chunk
            chunks.append('\n'.join(current_chunk))
            
            # Start new chunk with overlap
            if overlap > 0 and current_chunk:
                # Keep last few sentences for overlap
                last_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk[-1:]
                current_chunk = last_sentences.copy()
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk = []
                current_length = 0
        
        # Add paragraph to current chunk
        current_chunk.append(para)
        current_length += para_tokens
    
    # Don't forget the last chunk!
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

import io
try:
    import docx
except ImportError:
    docx = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_file(file_content: bytes, file_name: str) -> str:
    """
    Extract text from uploaded file based on file type.
    Currently supports: .txt, .md, .py, .js, .html, .css, .pdf, .docx
    """
    try:
        # Simple text-based files
        if file_name.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml')):
            return file_content.decode('utf-8')
        
        # PDF Files
        elif file_name.lower().endswith('.pdf'):
            if PyPDF2 is None:
                return "Error: PyPDF2 library not installed. Please run 'pip install PyPDF2'."
            
            pdf_file = io.BytesIO(file_content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        # Word Files (.docx)
        elif file_name.lower().endswith('.docx'):
            if docx is None:
                return "Error: python-docx library not installed. Please run 'pip install python-docx'."
            
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            return "\n".join([para.text for para in doc.paragraphs])
            
        else:
            # For unsupported files, try UTF-8, fallback to latin-1
            try:
                return file_content.decode('utf-8')
            except:
                return file_content.decode('latin-1', errors='ignore')
    except Exception as e:
        return f"Error reading file {file_name}: {str(e)}"
