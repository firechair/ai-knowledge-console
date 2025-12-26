import os
import markdown
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pathlib import Path
import uuid
from config import get_settings

class FileService:
    def __init__(self, static_dir: str = "static/generated"):
        self.static_dir = Path(static_dir)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self._base_url = get_settings().app_base_url.rstrip("/")

    def generate_file(self, content: str, format: str, filename: str = None) -> dict:
        """
        Generate a file from content.
        Returns dict with filepath and download_url.
        """
        if not filename:
            filename = f"document_{uuid.uuid4().hex[:8]}"

        # Sanitize filename
        filename = os.path.basename(filename)
        base_name, _ = os.path.splitext(filename)

        if format.lower() == "pdf":
            return self._generate_pdf(content, base_name)
        elif format.lower() == "html":
            return self._generate_html(content, base_name)
        else:
            return self._generate_markdown(content, base_name)

    def _generate_markdown(self, content: str, base_name: str) -> dict:
        filename = f"{base_name}.md"
        filepath = self.static_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return {
            "filename": filename,
            "path": str(filepath),
            "url": f"{self._base_url}/static/generated/{filename}",
            "download_url": f"{self._base_url}/api/files/download/{filename}"
        }

    def _generate_html(self, content: str, base_name: str) -> dict:
        filename = f"{base_name}.html"
        filepath = self.static_dir / filename
        
        html = markdown.markdown(content)
        full_html = f"<html><body>{html}</body></html>"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_html)

        return {
            "filename": filename,
            "path": str(filepath),
            "url": f"{self._base_url}/static/generated/{filename}",
            "download_url": f"{self._base_url}/api/files/download/{filename}"
        }

    def _generate_pdf(self, content: str, base_name: str) -> dict:
        filename = f"{base_name}.pdf"
        filepath = self.static_dir / filename

        # Basic PDF generation from text/markdown
        # For better markdown support we would need pypdf or similar, 
        # but reportlab is standard. We'll do a simple conversion.
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Split by newlines and create paragraphs
        # This is basic; complex markdown tables/images won't render perfectly
        # but acceptable for text plans/CVs.
        for line in content.split('\n'):
            if not line.strip():
                story.append(Spacer(1, 12))
            else:
                # Basic header handling
                style = styles["Normal"]
                text = line
                if line.startswith('# '):
                    style = styles["Heading1"]
                    text = line[2:]
                elif line.startswith('## '):
                    style = styles["Heading2"]
                    text = line[3:]
                elif line.startswith('### '):
                    style = styles["Heading3"]
                    text = line[4:]
                
                # Replace minimal markdown bold/italic
                # Bold
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Italic
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                
                story.append(Paragraph(text, style))

        doc.build(story)

        return {
            "filename": filename,
            "path": str(filepath),
            "url": f"{self._base_url}/static/generated/{filename}",
            "download_url": f"{self._base_url}/api/files/download/{filename}"
        }
