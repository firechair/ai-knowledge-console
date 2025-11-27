from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import List

from services.document_processor import DocumentProcessor

router = APIRouter()
processor = DocumentProcessor()

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """Upload and process a document"""
    # Validate file type
    allowed_extensions = ["pdf", "docx", "txt"]
    extension = file.filename.lower().split(".")[-1]
    
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {allowed_extensions}"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text
        text = processor.extract_text(content, file.filename)
        
        # Chunk the text
        chunks, metadata = processor.chunk_text(text, file.filename)
        
        # Add to vector store
        vector_store = request.app.state.vector_store
        num_chunks = vector_store.add_documents(chunks, metadata)
        
        return {
            "filename": file.filename,
            "chunks_created": num_chunks,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(request: Request):
    """List all uploaded documents"""
    vector_store = request.app.state.vector_store
    documents = vector_store.list_documents()
    return {"documents": documents}

@router.delete("/{filename}")
async def delete_document(request: Request, filename: str):
    """Delete a document from the vector store"""
    vector_store = request.app.state.vector_store
    vector_store.delete_document(filename)
    return {"status": "deleted", "filename": filename}
