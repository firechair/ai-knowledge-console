"""
Pydantic schemas for LLM configuration validation
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator


class CloudProviderConfig(BaseModel):
    """Configuration for a specific cloud provider"""
    model: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=100000)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=0.2, ge=0.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=0.0, le=2.0)
    repetition_penalty: Optional[float] = Field(default=1.1, ge=0.0, le=2.0)


class CustomProviderConfig(BaseModel):
    """Configuration for custom OpenAI-compatible provider"""
    base_url: str = Field(..., description="Base URL of the API")
    model: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=100000)


class LocalProviderConfig(BaseModel):
    """Configuration for local llama.cpp server"""
    base_url: str = Field(default="http://localhost:8080", description="Local server URL")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=100000)


class LLMSettings(BaseModel):
    """Main LLM settings structure"""
    provider_type: Literal["cloud", "local"] = Field(..., description="Provider type")
    cloud_provider: Optional[Literal["openrouter", "openai", "custom"]] = Field(
        default=None,
        description="Cloud provider (required if provider_type is 'cloud')"
    )
    cloud_service_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cloud provider configurations"
    )
    local: Optional[LocalProviderConfig] = Field(
        default=None,
        description="Local provider configuration"
    )

    @validator('cloud_provider', always=True)
    def validate_cloud_provider(cls, v, values):
        """Ensure cloud_provider is set when provider_type is 'cloud'"""
        if values.get('provider_type') == 'cloud' and not v:
            raise ValueError("cloud_provider is required when provider_type is 'cloud'")
        return v

    @validator('cloud_service_config', always=True)
    def validate_cloud_config(cls, v, values):
        """Ensure cloud_service_config exists when provider_type is 'cloud'"""
        if values.get('provider_type') == 'cloud' and not v:
            raise ValueError("cloud_service_config is required when provider_type is 'cloud'")
        return v

    @validator('local', always=True)
    def validate_local_config(cls, v, values):
        """Ensure local config exists when provider_type is 'local'"""
        if values.get('provider_type') == 'local' and not v:
            raise ValueError("local configuration is required when provider_type is 'local'")
        return v


class APIKeysConfig(BaseModel):
    """API keys for various services"""
    openrouter: Optional[str] = Field(default=None, description="OpenRouter API key")
    openai: Optional[str] = Field(default=None, description="OpenAI API key")
    github_token: Optional[str] = Field(default=None, description="GitHub token for API")
    openweather_api_key: Optional[str] = Field(default=None, description="OpenWeather API key")
    crypto_api_key: Optional[str] = Field(default=None, description="Cryptocurrency API key")


class SettingsUpdate(BaseModel):
    """Schema for updating settings"""
    llm: Optional[LLMSettings] = None
    api_keys: Optional[APIKeysConfig] = None
    embedding: Optional[Dict[str, Any]] = None
    rag: Optional[Dict[str, Any]] = None
