from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # LLM Settings
    llm_provider: str = "local"
    llm_base_url: str = "http://localhost:8080"
    openrouter_api_key: str = ""
    openrouter_model: str = "x-ai/grok-4.1-fast"
    openrouter_max_tokens: int = 1024
    openrouter_temperature: float = 0.7
    openrouter_top_p: float = 0.9
    openrouter_frequency_penalty: float = 0.2
    openrouter_presence_penalty: float = 0.0
    openrouter_repetition_penalty: float = 1.1
    
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
    
    # OAuth Credentials
    google_client_id: str = ""
    google_client_secret: str = ""
    slack_client_id: str = ""
    slack_client_secret: str = ""
    notion_client_id: str = ""
    notion_client_secret: str = ""
    
    # App base URL for OAuth redirects
    app_base_url: str = "http://localhost:8000"
    # Frontend base URL for post-OAuth redirects
    frontend_base_url: str = "http://localhost:5173"
    
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    max_upload_mb: int = 25
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window_sec: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
