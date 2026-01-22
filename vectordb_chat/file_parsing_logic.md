# File Parsing Logic and Encoding

This document explains how different file formats are processed and converted into clean text strings before they reach the embedding model.

## 1. Multi-Format Handling Architecture

The system uses a unified interface in `utils/text_utils.py` to handle various mime-types.

### Library Justification:
- **python-docx**: Excellent for extracting hierarchical text from modern Word documents (.docx).
- **PyPDF2**: Lightweight and efficient for extracting raw text from PDF pages without complex heavy-weight dependencies.

## 2. Text-Based Encoding (.txt, .md, .py, etc.)

For code and markdown files, the system uses standard UTF-8 decoding.

### Code Logic:
```python
if file_name.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml')):
    return file_content.decode('utf-8')
```
**Fallback**: If UTF-8 fails (e.g., legacy Windows files), it falls back to `latin-1` with error ignoring to ensure the system doesn't crash on slightly non-standard character sets.

## 3. PDF Parsing Logic

PDFs are complex binary formats. Text isn't stored as a single stream but as positioned tokens on a page.

### Code Logic:
```python
pdf_file = io.BytesIO(file_content)
reader = PyPDF2.PdfReader(pdf_file)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"
```
- **io.BytesIO**: We convert the raw bytes from Streamlit into a file-like object so the library can seek through it.
- **Page Extraction**: We iterate through every page in the document, extracting the text layer and appending it with newlines to preserve structural separation.

## 4. DOCX Parsing Logic

DOCX files are actually zipped XML structures. `python-docx` handles the unzipping and XML traversal.

### Code Logic:
```python
doc = docx.Document(docx_file)
return "\n".join([para.text for para in doc.paragraphs])
```
- **Paragraphs**: Word documents are primarily structured as a collection of paragraphs.
- **Extraction**: We extract the `.text` property of every paragraph object, ignoring complex styling but retaining the readable content.

## Summary Table of Encoding Processes

| File Type | Library | Method | Key Challenge |
| :--- | :--- | :--- | :--- |
| **Plain Text** | Native Python | `utf-8.decode()` | Character set mismatches |
| **PDF** | `PyPDF2` | Page-by-page extraction | Multi-column layouts/metadata |
| **Word** | `python-docx` | Paragraph iteration | Tables/Bullet points |
| **Code** | Native Python | `utf-8.decode()` | Special characters |

By normalizing all these formats into a single `UTF-8` string, we provide a consistent input for the **Chunking Logic**.
