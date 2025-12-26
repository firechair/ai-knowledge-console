"""
Dependency injection functions for FastAPI.

This module provides dependency functions that create and manage service instances.
Using FastAPI's dependency injection system improves testability and maintainability.
"""

from functools import lru_cache
from services.llm_service import LLMService
from services.vector_store import VectorStoreService
from services.conversation_service import ConversationService
from services.api_tools import APIToolsService
from services.config_service import get_config_service, ConfigService
from services.model_manager import get_model_manager, ModelManager
from config import get_settings


@lru_cache()
def get_llm_service() -> LLMService:
    """
    Dependency for LLM service.

    Returns a cached instance of LLMService to ensure singleton behavior.
    The @lru_cache decorator ensures only one instance is created.

    Returns:
        LLMService: Singleton instance of the LLM service
    """
    return LLMService()


@lru_cache()
def get_vector_store() -> VectorStoreService:
    """
    Dependency for vector store service.

    Returns a cached instance of VectorStoreService configured with application settings.

    Returns:
        VectorStoreService: Singleton instance of the vector store service
    """
    return VectorStoreService()


@lru_cache()
def get_conversation_service() -> ConversationService:
    """
    Dependency for conversation service.

    Returns a cached instance of ConversationService for managing chat history.

    Returns:
        ConversationService: Singleton instance of the conversation service
    """
    return ConversationService()


@lru_cache()
def get_api_tools() -> APIToolsService:
    """
    Dependency for API tools service.

    Returns a cached instance of APIToolsService for external API integrations.

    Returns:
        APIToolsService: Singleton instance of the API tools service
    """
    return APIToolsService()


@lru_cache()
def get_config() -> ConfigService:
    """
    Dependency for configuration service.

    Returns a cached instance of ConfigService for managing user settings.
    The service merges settings.json with .env defaults.

    Returns:
        ConfigService: Singleton instance of the configuration service
    """
    return get_config_service()


def get_model_manager_dep() -> ModelManager:
    """
    Dependency for model manager service.

    Returns the singleton instance of ModelManager for managing model downloads.

    Returns:
        ModelManager: Singleton instance of the model manager service
    """
    return get_model_manager()
