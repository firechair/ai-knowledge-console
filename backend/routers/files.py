from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
from services.file_service import FileService
from fastapi.responses import FileResponse

router = APIRouter(tags=["Files"])
file_service = FileService()

class GenerateFileRequest(BaseModel):
    content: str
    format: str = "pdf"  # pdf, markdown, html
    title: Optional[str] = None
    filename: Optional[str] = None

@router.post("/generate")
async def generate_file(request: GenerateFileRequest):
    """
    Generate a downloadable file from content.
    """
    try:
        # Prepend title to content if it exists and not already there
        content = request.content
        if request.title and not content.startswith(f"# {request.title}"):
            content = f"# {request.title}\n\n{content}"

        result = file_service.generate_file(
            content=content,
            format=request.format,
            filename=request.filename
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a generated file.
    """
    filepath = file_service.static_dir / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath, filename=filename)
