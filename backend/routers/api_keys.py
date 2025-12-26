from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from services.config_service import ConfigService
from dependencies import get_config

router = APIRouter()


class APIKeysUpdate(BaseModel):
    """Schema for updating API keys"""
    openrouter: Optional[str] = None
    openai: Optional[str] = None
    github_token: Optional[str] = None
    openweather_api_key: Optional[str] = None
    crypto_api_key: Optional[str] = None


@router.get("/status")
async def get_api_keys_status(config: ConfigService = Depends(get_config)):
    """Get API key status (whether they are set, not the keys themselves)"""
    return {
        "status": "ok",
        "api_keys": config.get_api_keys()
    }


@router.post("/")
async def update_api_keys(
    keys: APIKeysUpdate,
    config: ConfigService = Depends(get_config)
):
    """Update API keys (only saves non-empty values)"""
    # Convert to dict and filter out None values
    keys_dict = {k: v for k, v in keys.dict().items() if v is not None}

    if not keys_dict:
        raise HTTPException(400, "No API keys provided")

    success = config.save_api_keys(keys_dict)
    if not success:
        raise HTTPException(500, "Failed to save API keys")

    return {
        "status": "ok",
        "message": "API keys updated successfully",
        "updated_keys": list(keys_dict.keys())
    }


@router.delete("/{service}")
async def delete_api_key(
    service: str,
    config: ConfigService = Depends(get_config)
):
    """Delete a specific API key"""
    valid_services = ["openrouter", "openai", "github_token", "openweather_api_key", "crypto_api_key"]

    if service not in valid_services:
        raise HTTPException(400, f"Invalid service. Must be one of: {', '.join(valid_services)}")

    # Load current settings
    current_settings = config.user_settings
    if "api_keys" not in current_settings or service not in current_settings["api_keys"]:
        raise HTTPException(404, f"API key for {service} not found")

    # Remove the key
    del current_settings["api_keys"][service]

    success = config.save_user_settings(current_settings)
    if not success:
        raise HTTPException(500, "Failed to delete API key")

    return {
        "status": "ok",
        "message": f"API key for {service} deleted successfully"
    }
