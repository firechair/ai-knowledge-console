"""
Cloud Provider Registry
Defines available cloud providers and their configurations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CloudProviderDefinition:
    """Definition of a cloud provider"""
    id: str
    name: str
    description: str
    base_url: str
    required_fields: List[str]
    optional_fields: List[str]
    supports_model_list: bool
    has_free_tier: bool


# Registry of available cloud providers
CLOUD_PROVIDERS: Dict[str, CloudProviderDefinition] = {
    "openrouter": CloudProviderDefinition(
        id="openrouter",
        name="OpenRouter",
        description="Access 200+ AI models through a unified API. Free tier available.",
        base_url="https://openrouter.ai/api/v1",
        required_fields=["model"],
        optional_fields=["temperature", "max_tokens", "top_p", "frequency_penalty",
                        "presence_penalty", "repetition_penalty"],
        supports_model_list=True,
        has_free_tier=True
    ),
    "openai": CloudProviderDefinition(
        id="openai",
        name="OpenAI",
        description="Official OpenAI API for GPT-4, GPT-3.5, and more.",
        base_url="https://api.openai.com/v1",
        required_fields=["model"],
        optional_fields=["temperature", "max_tokens", "top_p", "frequency_penalty",
                        "presence_penalty"],
        supports_model_list=False,
        has_free_tier=False
    ),
    "custom": CloudProviderDefinition(
        id="custom",
        name="Custom OpenAI-Compatible",
        description="Any OpenAI-compatible API endpoint (LM Studio, Ollama, etc.)",
        base_url="",  # User provides
        required_fields=["base_url", "model"],
        optional_fields=["temperature", "max_tokens"],
        supports_model_list=False,
        has_free_tier=False
    )
}


# Popular OpenRouter models (could be fetched from API in future)
OPENROUTER_MODELS = [
    {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "name": "Meta Llama 3.3 70B Instruct (Free)",
        "context_length": 8192,
        "is_free": True
    },
    {
        "id": "google/gemini-2.0-flash-exp:free",
        "name": "Google Gemini 2.0 Flash (Free)",
        "context_length": 1048576,
        "is_free": True
    },
    {
        "id": "x-ai/grok-2-1212",
        "name": "xAI Grok 2",
        "context_length": 131072,
        "is_free": False
    },
    {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Anthropic Claude 3.5 Sonnet",
        "context_length": 200000,
        "is_free": False
    },
    {
        "id": "openai/gpt-4o",
        "name": "OpenAI GPT-4o",
        "context_length": 128000,
        "is_free": False
    },
    {
        "id": "mistralai/mistral-large-2411",
        "name": "Mistral Large 2411",
        "context_length": 128000,
        "is_free": False
    }
]


def get_cloud_provider(provider_id: str) -> Optional[CloudProviderDefinition]:
    """Get cloud provider definition by ID"""
    return CLOUD_PROVIDERS.get(provider_id)


def get_all_cloud_providers() -> List[Dict]:
    """Get all cloud providers as dictionaries"""
    return [
        {
            "id": provider.id,
            "name": provider.name,
            "description": provider.description,
            "base_url": provider.base_url,
            "required_fields": provider.required_fields,
            "optional_fields": provider.optional_fields,
            "supports_model_list": provider.supports_model_list,
            "has_free_tier": provider.has_free_tier
        }
        for provider in CLOUD_PROVIDERS.values()
    ]


def get_openrouter_models(api_key: Optional[str] = None) -> List[Dict]:
    """Get list of popular OpenRouter models"""
    if api_key:
        return fetch_openrouter_models(api_key)
    return OPENROUTER_MODELS


def validate_provider_config(provider_id: str, config: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate provider configuration
    Returns: (is_valid, error_message)
    """
    provider = get_cloud_provider(provider_id)
    if not provider:
        return False, f"Unknown provider: {provider_id}"

    # Check required fields
    for field in provider.required_fields:
        if field not in config or not config[field]:
            return False, f"Missing required field: {field}"

    return True, None


def fetch_openrouter_models(api_key: str) -> List[Dict]:
    """
    Fetch popular models from OpenRouter API
    """
    import requests
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/firechair/ai-knowledge-console",
                "X-Title": "AI Knowledge Console"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Transform and sort
            models = []
            if "data" in data:
                for m in data["data"]:
                    models.append({
                        "id": m["id"],
                        "name": m["name"],
                        "context_length": m.get("context_length", 4096),
                        "is_free": "free" in m["id"] or "free" in m.get("pricing", {}).get("prompt", "")
                    })
            
            # Sort: free first, then by name
            models.sort(key=lambda x: (not x["is_free"], x["name"]))
            return models
            
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
    
    # Fallback to local list
    return OPENROUTER_MODELS
