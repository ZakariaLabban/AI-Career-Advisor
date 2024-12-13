# utils/file_utils.py

import fitz  # PyMuPDF
from docx import Document

def extract_text(file, file_type):
    if file_type == "pdf":
        return extract_text_from_pdf(file)
    elif file_type == "docx":
        return extract_text_from_docx(file)
    else:
        raise ValueError("Unsupported file type.")

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            extracted = page.get_text()
            if extracted:
                text += extracted + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text
