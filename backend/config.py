from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # LLM Settings
    llm_provider: str = "local"
    llm_base_url: str = "http://localhost:8080"
    
    # Vector DB
    chroma_persist_dir: str = "../vectorstore/chroma"
    
    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # API Keys (loaded from .env)
    github_token: str = ""
    openweather_api_key: str = ""
    openrouter_api_key: str = ""
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    max_upload_mb: int = 25
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_sec: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
