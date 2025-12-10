"""
Pytest configuration and shared fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.llm_service import LLMService
from services.vector_store import VectorStoreService
from services.conversation_service import ConversationService
from services.api_tools import APIToolsService
from dependencies import (
    get_llm_service,
    get_vector_store,
    get_conversation_service,
    get_api_tools
)


@pytest.fixture
def test_client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    mock = Mock(spec=LLMService)
    mock.generate = AsyncMock(return_value="Test response")
    
    # Mock generate_stream as an async generator
    async def mock_stream(*args, **kwargs):
        yield "Test "
        yield "streaming "
        yield "response"
    
    mock.generate_stream = Mock(return_value=mock_stream())
    mock.build_rag_prompt = Mock(return_value="Test prompt")
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store service for testing."""
    mock = Mock(spec=VectorStoreService)
    mock.search = Mock(return_value=[
        {
            "content": "Test document content",
            "metadata": {"filename": "test.txt"}
        }
    ])
    mock.add_documents = Mock(return_value=5)
    mock.list_documents = Mock(return_value=["test.txt", "example.pdf"])
    mock.delete_document = Mock()
    return mock


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service for testing."""
    mock = Mock(spec=ConversationService)
    mock.create_conversation = Mock(return_value="test-conv-123")
    mock.add_message = Mock()
    mock.get_history = Mock(return_value=[
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"}
    ])
    return mock


@pytest.fixture
def mock_api_tools():
    """Mock API tools service for testing."""
    mock = Mock(spec=APIToolsService)
    mock.github_search_commits = AsyncMock(return_value={"commits": []})
    mock.get_crypto_price = AsyncMock(return_value={"price": 50000})
    mock.get_weather = AsyncMock(return_value={"temp": 72})
    mock.get_hacker_news_top = AsyncMock(return_value={"stories": []})
    return mock


@pytest.fixture
def override_dependencies(
    mock_llm_service,
    mock_vector_store,
    mock_conversation_service,
    mock_api_tools
):
    """Override FastAPI dependencies with mocks."""
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service
    app.dependency_overrides[get_vector_store] = lambda: mock_vector_store
    app.dependency_overrides[get_conversation_service] = lambda: mock_conversation_service
    app.dependency_overrides[get_api_tools] = lambda: mock_api_tools

    yield

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "message": "What is the capital of France?",
        "use_documents": True,
        "tools": None,
        "tool_params": None,
        "conversation_id": None
    }


@pytest.fixture
def sample_document_file():
    """Sample document file for upload testing."""
    from io import BytesIO
    content = b"This is a test document with sample content."
    return BytesIO(content)
