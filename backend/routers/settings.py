from fastapi import APIRouter, Request
from pydantic import BaseModel

class EmbeddingModelRequest(BaseModel):
    name: str

router = APIRouter()

@router.post("/embedding_model")
async def set_embedding_model(request: Request, body: EmbeddingModelRequest):
    vector_store = request.app.state.vector_store
    vector_store.reload_embedding_model(body.name)
    return {"status": "ok", "embedding_model": body.name}

