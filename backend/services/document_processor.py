from pypdf import PdfReader
from docx import Document
from typing import List, Dict, Tuple
from config import get_settings
import io

class DocumentProcessor:
    def __init__(self):
        self.settings = get_settings()
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file"""
        extension = filename.lower().split(".")[-1]
        
        if extension == "pdf":
            return self._extract_pdf(file_content)
        elif extension == "docx":
            return self._extract_docx(file_content)
        elif extension == "txt":
            return file_content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _extract_pdf(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_docx(self, content: bytes) -> str:
        doc = Document(io.BytesIO(content))
        return "\n".join(para.text for para in doc.paragraphs)
    
    def chunk_text(self, text: str, filename: str) -> Tuple[List[str], List[Dict]]:
        """Split text into overlapping chunks"""
        chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        
        chunks = []
        metadata = []
        
        # Simple chunking by character count with overlap
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            metadata.append({
                "filename": filename,
                "chunk_index": chunk_index,
                "start_char": start
            })
            
            start = end - overlap
            chunk_index += 1
        
        return chunks, metadata
