"""
LEARNING PHASE: Text Extraction
--------------------------------
This file explains how we extract raw text from different file formats.
Each line of code is explained in detail.
"""

import io
import os

# We use 'docx' library to handle Word files (.docx)
# If not installed, we provide a fallback
try:
    import docx
except ImportError:
    docx = None

# We use 'PyPDF2' to handle PDF files
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_file_educational(file_path: str) -> str:
    """
    Learning function to show how file parsing works.
    
    Args:
        file_path: Absolute path to the file on disk
    """
    
    # 1. Get the file extension (the part after the dot, e.g., '.pdf')
    # os.path.splitext splits '/path/to/file.pdf' into ('/path/to/file', '.pdf')
    file_name = os.path.basename(file_path)
    extension = os.path.splitext(file_name)[1].lower()
    
    print(f"--- Processing file: {file_name} ---")
    
    try:
        # 2. Open the file in binary mode ('rb')
        # We use binary mode because PDFs and Word files are not plain text
        with open(file_path, 'rb') as f:
            file_content = f.read() # Read all raw bytes into memory
            
        # 3. Handle Plain Text files (.txt, .md, .py, etc.)
        if extension in ['.txt', '.md', '.py', '.js', '.csv', '.json']:
            # For these files, we just need to decode bytes into a UTF-8 string
            # .decode('utf-8') turns machine binary into human-readable characters
            return file_content.decode('utf-8')
            
        # 4. Handle PDF files
        elif extension == '.pdf':
            # Check if the library is available
            if PyPDF2 is None:
                return "Error: PyPDF2 not installed."
            
            # We create a 'BytesIO' stream which looks like a file but is in RAM
            # PyPDF2 needs a file-like object to navigate through the PDF structure
            pdf_stream = io.BytesIO(file_content)
            
            # PdfReader is the main class that 'understands' PDF internal objects
            reader = PyPDF2.PdfReader(pdf_stream)
            
            # We extract text page-by-page and join them
            text = ""
            for page_num in range(len(reader.pages)):
                # Obtain the page object
                page = reader.pages[page_num]
                # Page objects have a built-in method to find text tokens
                text += page.extract_text() + "\n"
                
            return text
            
        # 5. Handle Word files (.docx)
        elif extension == '.docx':
            if docx is None:
                return "Error: python-docx not installed."
                
            # Similar to PDF, we use a BytesIO stream
            word_stream = io.BytesIO(file_content)
            
            # docx.Document opens the XML-based word document
            doc = docx.Document(word_stream)
            
            # Word documents are made of 'paragraphs'
            # We iterate through all of them and join their text content
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
                
            # Join with newlines to keep the original formatting style
            return "\n".join(full_text)
            
        else:
            # If we don't know the format, we try a generic decode
            # 'latin-1' is more forgiving than 'utf-8' and won't crash on binary
            return file_content.decode('latin-1', errors='ignore')
            
    except Exception as e:
        # Log any errors (e.g., file not found, corrupted file)
        return f"Extraction Error: {str(e)}"

# --- SAMPLE USAGE (Optional) ---
if __name__ == "__main__":
    # If this file were run directly, you could test it like this:
    # result = extract_text_from_file_educational("sample.txt")
    # print(result[:500]) # Preview first 500 characters
    pass
