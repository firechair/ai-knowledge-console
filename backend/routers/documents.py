from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from config import get_settings
from typing import List

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStoreService
from dependencies import get_vector_store
from exceptions import ValidationError, NotFoundError

router = APIRouter()
processor = DocumentProcessor()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """Upload and process a document"""
    # Validate file type
    allowed_extensions = ["pdf", "docx", "txt"]
    extension = file.filename.lower().split(".")[-1]

    if extension not in allowed_extensions:
        raise ValidationError(
            f"File type not supported. Allowed: {allowed_extensions}"
        )

    try:
        cfg = get_settings()
        if file.content_type not in [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]:
            raise ValidationError("Unsupported MIME type")
        content = await file.read()
        max_bytes = cfg.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise ValidationError("File too large")

        # Extract text
        text = processor.extract_text(content, file.filename)

        # Chunk the text
        chunks, metadata = processor.chunk_text(text, file.filename)

        # Add to vector store
        num_chunks = vector_store.add_documents(chunks, metadata)

        return {
            "filename": file.filename,
            "chunks_created": num_chunks,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """List all uploaded documents"""
    documents = vector_store.list_documents()
    return {"documents": documents}


@router.delete("/{filename}")
async def delete_document(
    filename: str,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """Delete a document from the vector store"""
    vector_store.delete_document(filename)
    return {"status": "deleted", "filename": filename}
