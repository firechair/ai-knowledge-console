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
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
