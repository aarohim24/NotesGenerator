import os
import re
from PyPDF2 import PdfReader
from docx import Document

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path):
        text = ""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        return text

    @staticmethod
    def extract_text_from_docx(file_path):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    
    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    @classmethod
    def extract_text(cls, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            text = cls.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = cls.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")
        return cls.clean_text(text)
