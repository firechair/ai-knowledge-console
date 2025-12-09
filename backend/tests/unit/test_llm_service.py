"""
Unit tests for LLMService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
import json

from services.llm_service import LLMService


@pytest.mark.unit
class TestLLMService:
    """Test suite for LLMService."""

    def test_init_openrouter(self):
        """Test initialization with OpenRouter configuration."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "openrouter"
            mock_settings.return_value.llm_base_url = "https://openrouter.ai/api/v1"
            mock_settings.return_value.openrouter_api_key = "test-key"
            mock_settings.return_value.openrouter_model = "meta-llama/llama-3.1-8b-instruct:free"

            service = LLMService()

            assert service.is_openrouter is True
            assert service.base_url == "https://openrouter.ai/api/v1"
            assert service.model == "meta-llama/llama-3.1-8b-instruct:free"

    def test_init_llamacpp(self):
        """Test initialization with llama.cpp configuration."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "local"
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()

            assert service.is_openrouter is False
            assert service.base_url == "http://localhost:8080"

    async def test_generate_openrouter(self):
        """Test non-streaming generation with OpenRouter."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "openrouter"
            mock_settings.return_value.llm_base_url = "https://openrouter.ai/api/v1"
            mock_settings.return_value.openrouter_api_key = "test-key"
            mock_settings.return_value.app_base_url = "http://localhost:5173"
            mock_settings.return_value.openrouter_temperature = 0.7
            mock_settings.return_value.openrouter_top_p = 1.0
            mock_settings.return_value.openrouter_frequency_penalty = 0.0
            mock_settings.return_value.openrouter_presence_penalty = 0.0
            mock_settings.return_value.openrouter_repetition_penalty = 1.0
            mock_settings.return_value.openrouter_max_tokens = 1024

            service = LLMService()

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}]
            }
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.generate(
                    prompt="Test prompt",
                    system_prompt="Test system",
                    max_tokens=100,
                    temperature=0.7
                )

                assert result == "Test response"
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
                assert "Authorization" in call_args[1]["headers"]

    async def test_generate_llamacpp(self):
        """Test non-streaming generation with llama.cpp."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "local"
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()

            mock_response = Mock()
            mock_response.json.return_value = {"content": "Test response"}
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.generate(
                    prompt="Test prompt",
                    max_tokens=100
                )

                assert result == "Test response"
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert call_args[0][0] == "http://localhost:8080/completion"

    async def test_generate_stream_openrouter(self):
        """Test streaming generation with OpenRouter."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "openrouter"
            mock_settings.return_value.llm_base_url = "https://openrouter.ai/api/v1"
            mock_settings.return_value.openrouter_api_key = "test-key"
            mock_settings.return_value.app_base_url = "http://localhost:5173"
            mock_settings.return_value.openrouter_temperature = 0.7
            mock_settings.return_value.openrouter_top_p = 1.0
            mock_settings.return_value.openrouter_frequency_penalty = 0.0
            mock_settings.return_value.openrouter_presence_penalty = 0.0
            mock_settings.return_value.openrouter_repetition_penalty = 1.0
            mock_settings.return_value.openrouter_max_tokens = 1024

            service = LLMService()

            # Mock streaming response
            async def mock_aiter_lines():
                lines = [
                    'data: {"choices": [{"delta": {"content": "Hello"}}]}',
                    'data: {"choices": [{"delta": {"content": " world"}}]}',
                    'data: [DONE]'
                ]
                for line in lines:
                    yield line

            # Create a mock response object with proper async context manager
            class MockStreamResponse:
                async def aiter_lines(self):
                    async for line in mock_aiter_lines():
                        yield line

            mock_response = MockStreamResponse()

            # Create proper async context manager for stream
            class MockStream:
                async def __aenter__(self):
                    return mock_response
                async def __aexit__(self, *args):
                    pass

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.stream = Mock(return_value=MockStream())
                mock_client_class.return_value = mock_client

                result = []
                async for chunk in service.generate_stream(prompt="Test"):
                    result.append(chunk)

                assert result == ["Hello", " world"]

    def test_format_prompt_with_system(self):
        """Test prompt formatting with system message."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "local"
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            result = service._format_prompt("System message", "User message")

            assert result == "[INST] System message\n\nUser message [/INST]"

    def test_format_prompt_without_system(self):
        """Test prompt formatting without system message."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            result = service._format_prompt("", "User message")

            assert result == "[INST] User message [/INST]"

    def test_build_rag_prompt_basic(self):
        """Test RAG prompt building with basic context."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            context_chunks = [
                {
                    "content": "Paris is the capital of France.",
                    "metadata": {"filename": "geography.txt"}
                }
            ]

            result = service.build_rag_prompt("What is the capital of France?", context_chunks)

            assert "Current Question: What is the capital of France?" in result
            assert "Paris is the capital of France." in result
            assert "geography.txt" in result

    def test_build_rag_prompt_with_history(self):
        """Test RAG prompt building with conversation history."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]

            result = service.build_rag_prompt("How are you?", [], conversation_history=history)

            assert "Conversation History:" in result
            assert "User: Hello" in result
            assert "Assistant: Hi there!" in result

    def test_build_rag_prompt_with_api_data(self):
        """Test RAG prompt building with API data."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            api_data = {"weather": {"temperature": 72, "condition": "sunny"}}

            result = service.build_rag_prompt("What's the weather?", [], api_data=api_data)

            assert "External Data:" in result
            assert "weather" in result
            assert "72" in result

    def test_build_rag_prompt_empty_context(self):
        """Test RAG prompt building with no context."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()
            result = service.build_rag_prompt("Test question", [])

            assert "Current Question: Test question" in result
            assert "Based on the above context" in result

    async def test_generate_http_error(self):
        """Test handling of HTTP errors during generation."""
        with patch('services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "local"
            mock_settings.return_value.llm_base_url = "http://localhost:8080"

            service = LLMService()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = httpx.HTTPError("Connection failed")
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with pytest.raises(httpx.HTTPError):
                    await service.generate(prompt="Test")
