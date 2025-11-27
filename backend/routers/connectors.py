from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()

class ConnectorConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    enabled: bool = True

# In-memory storage (use database in production)
connectors_store = {
    "github": {"enabled": False, "configured": False},
    "weather": {"enabled": False, "configured": False},
    "crypto": {"enabled": True, "configured": True},  # No API key needed
    "hackernews": {"enabled": True, "configured": True}  # No API key needed
}

@router.get("/")
async def list_connectors():
    """List all available connectors and their status"""
    return {"connectors": connectors_store}

@router.post("/configure")
async def configure_connector(config: ConnectorConfig):
    """Configure an API connector"""
    if config.name not in connectors_store:
        raise HTTPException(status_code=404, detail=f"Connector {config.name} not found")
    
    # In production, encrypt and store API keys securely
    if config.api_key:
        os.environ[f"{config.name.upper()}_API_KEY"] = config.api_key
        connectors_store[config.name]["configured"] = True
    
    connectors_store[config.name]["enabled"] = config.enabled
    
    return {"status": "configured", "connector": config.name}

@router.post("/{name}/toggle")
async def toggle_connector(name: str):
    """Enable/disable a connector"""
    if name not in connectors_store:
        raise HTTPException(status_code=404, detail=f"Connector {name} not found")
    
    connectors_store[name]["enabled"] = not connectors_store[name]["enabled"]
    return connectors_store[name]
