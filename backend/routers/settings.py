from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from services.config_service import ConfigService
from dependencies import get_config
from schemas.llm_config import LLMSettings

class EmbeddingModelRequest(BaseModel):
    name: str

router = APIRouter()

@router.post("/embedding_model")
async def set_embedding_model(request: Request, body: EmbeddingModelRequest):
    vector_store = request.app.state.vector_store
    vector_store.reload_embedding_model(body.name)
    return {"status": "ok", "embedding_model": body.name}

@router.get("/llm")
async def get_llm_settings(config: ConfigService = Depends(get_config)):
    """Get current LLM configuration (without API key)"""
    llm_config = config.get_llm_config()
    # Remove sensitive data
    safe_config = {k: v for k, v in llm_config.items() if k != "api_key"}
    return {"status": "ok", "config": safe_config}

@router.post("/llm")
async def update_llm_settings(
    request: Request,
    config: ConfigService = Depends(get_config)
):
    """Update LLM configuration"""
    body = await request.json()

    # Validate using Pydantic schema if using new format
    if "provider_type" in body:
        try:
            LLMSettings(**body)
        except ValidationError as e:
            raise HTTPException(400, detail=str(e))
    # Backward compatibility: validate old format
    elif "provider" in body:
        if body["provider"] not in ["openrouter", "local", "openai-compatible"]:
            raise HTTPException(400, "Invalid provider")

    # Save to settings.json
    success = config.save_user_settings({"llm": body})
    if not success:
        raise HTTPException(500, "Failed to save settings")

    return {"status": "ok", "message": "Settings updated. Restart backend for changes to take effect."}

@router.get("/cloud-providers")
async def get_cloud_providers(config: ConfigService = Depends(get_config)):
    """Get list of available cloud providers from registry"""
    return {
        "providers": config.get_cloud_providers()
    }

@router.get("/providers")
async def get_providers():
    """List available LLM providers (legacy endpoint for backward compatibility)"""
    return {
        "providers": [
            {
                "id": "openrouter",
                "name": "OpenRouter",
                "description": "Hosted LLM inference with 200+ models",
                "requires": ["api_key", "model"]
            },
            {
                "id": "openai-compatible",
                "name": "OpenAI Compatible",
                "description": "Any OpenAI API-compatible endpoint",
                "requires": ["base_url", "api_key", "model"]
            },
            {
                "id": "local",
                "name": "Local llama.cpp",
                "description": "Self-hosted llama.cpp server",
                "requires": ["base_url"]
            }
        ]
    }

@router.get("/models/openrouter")
async def get_openrouter_models(config: ConfigService = Depends(get_config)):
    """List popular OpenRouter models from registry"""
    return {
        "models": config.get_openrouter_models()
    }

@router.get("/api-keys/status")
async def get_api_keys_status(config: ConfigService = Depends(get_config)):
    """Get API key status (whether they are set, not the keys themselves)"""
    return {
        "status": "ok",
        "api_keys": config.get_api_keys()
    }

