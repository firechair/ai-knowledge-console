from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from services.model_manager import get_model_manager, ModelManager
from services.config_service import ConfigService
from dependencies import get_config

router = APIRouter(prefix="/api/models", tags=["models"])

class LLMModelDownloadRequest(BaseModel):
    repo_id: str
    filename: str
    token: str = ""

class EmbeddingModelDownloadRequest(BaseModel):
    model_name: str

@router.get("/llm")
async def list_llm_models(manager: ModelManager = Depends(get_model_manager)):
    """List locally available GGUF models"""
    models = manager.list_local_llm_models()
    return {"status": "ok", "models": models}

@router.get("/embedding")
async def list_embedding_models(
    manager: ModelManager = Depends(get_model_manager),
    config: ConfigService = Depends(get_config)
):
    """List cached embedding models and current active model"""
    models = manager.list_local_embedding_models()
    active_model = config.get_embedding_config().get("model", "all-MiniLM-L6-v2")
    return {
        "status": "ok", 
        "models": models,
        "active_model": active_model
    }

@router.post("/llm/download")
async def download_llm_model(
    request: LLMModelDownloadRequest,
    background_tasks: BackgroundTasks,
    manager: ModelManager = Depends(get_model_manager)
):
    """Trigger GGUF model download from HuggingFace"""
    download_id = f"{request.repo_id}/{request.filename}"

    # Check if already downloading
    status = manager.get_download_status(download_id)
    if status and status["status"] == "downloading":
        return {"status": "already_downloading", "download_id": download_id}

    # Start download in background
    async def download_task():
        try:
            await manager.download_gguf_model(
                repo_id=request.repo_id,
                filename=request.filename,
                token=request.token or None
            )
        except Exception as e:
            print(f"Download failed: {e}")

    background_tasks.add_task(download_task)

    return {
        "status": "started",
        "download_id": download_id,
        "message": "Download started in background"
    }

@router.post("/embedding/download")
async def download_embedding_model(
    request: EmbeddingModelDownloadRequest,
    background_tasks: BackgroundTasks,
    manager: ModelManager = Depends(get_model_manager)
):
    """Trigger embedding model download from HuggingFace"""
    # Check if already downloading
    status = manager.get_download_status(request.model_name)
    if status and status["status"] == "downloading":
        return {"status": "already_downloading", "download_id": request.model_name}

    # Start download in background
    async def download_task():
        try:
            await manager.download_embedding_model(request.model_name)
        except Exception as e:
            print(f"Download failed: {e}")

    background_tasks.add_task(download_task)

    return {
        "status": "started",
        "download_id": request.model_name,
        "message": "Download started in background"
    }

@router.get("/downloads/{download_id:path}")
async def get_download_status(
    download_id: str,
    manager: ModelManager = Depends(get_model_manager)
):
    """Get status of a download"""
    status = manager.get_download_status(download_id)
    if not status:
        raise HTTPException(404, "Download not found")
    return {"status": "ok", "download": status}

@router.get("/downloads")
async def list_downloads(manager: ModelManager = Depends(get_model_manager)):
    """List all tracked downloads"""
    downloads = manager.list_downloads()
    return {"status": "ok", "downloads": downloads}
