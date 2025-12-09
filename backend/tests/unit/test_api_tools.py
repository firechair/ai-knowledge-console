"""
Unit tests for APIToolsService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from datetime import datetime

from services.api_tools import APIToolsService


@pytest.mark.unit
class TestAPIToolsService:
    """Test suite for APIToolsService."""

    @pytest.mark.asyncio
    async def test_github_search_commits_with_token(self):
        """Test GitHub commit search with authentication token."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.github_token = "test-token"

            service = APIToolsService()

            mock_response = Mock()
            mock_response.json.return_value = [
                {
                    "sha": "abc123def456",
                    "commit": {
                        "message": "Initial commit\nDetailed description",
                        "author": {
                            "name": "John Doe",
                            "date": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            ]
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.github_search_commits("facebook/react", limit=1)

                assert result["repository"] == "facebook/react"
                assert len(result["commits"]) == 1
                assert result["commits"][0]["sha"] == "abc123d"
                assert result["commits"][0]["message"] == "Initial commit"
                assert result["commits"][0]["author"] == "John Doe"

                # Verify token was used
                call_args = mock_client.get.call_args
                assert "Authorization" in call_args[1]["headers"]
                assert call_args[1]["headers"]["Authorization"] == "token test-token"

    @pytest.mark.asyncio
    async def test_github_search_commits_without_token(self):
        """Test GitHub commit search without authentication token."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.github_token = ""

            service = APIToolsService()

            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                await service.github_search_commits("test/repo")

                # Verify no authorization header
                call_args = mock_client.get.call_args
                assert "Authorization" not in call_args[1]["headers"]

    @pytest.mark.asyncio
    async def test_github_search_commits_http_error(self):
        """Test GitHub API HTTP error handling."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.github_token = ""

            service = APIToolsService()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = httpx.HTTPError("404 Not Found")
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with pytest.raises(httpx.HTTPError):
                    await service.github_search_commits("invalid/repo")

    @pytest.mark.asyncio
    async def test_get_crypto_price_success(self):
        """Test successful cryptocurrency price retrieval."""
        with patch('services.api_tools.get_settings'):
            service = APIToolsService()

            mock_response = Mock()
            mock_response.json.return_value = {
                "bitcoin": {
                    "usd": 50000,
                    "eur": 45000,
                    "usd_24h_change": 2.5
                }
            }
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.get_crypto_price("bitcoin")

                assert result["symbol"] == "bitcoin"
                assert result["price_usd"] == 50000
                assert result["price_eur"] == 45000
                assert result["change_24h"] == 2.5
                assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_crypto_price_not_found(self):
        """Test cryptocurrency not found."""
        with patch('services.api_tools.get_settings'):
            service = APIToolsService()

            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.get_crypto_price("invalid_coin")

                assert "error" in result
                assert "invalid_coin" in result["error"]

    @pytest.mark.asyncio
    async def test_get_weather_success(self):
        """Test successful weather retrieval."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.openweather_api_key = "test-api-key"

            service = APIToolsService()

            mock_response = Mock()
            mock_response.json.return_value = {
                "name": "San Francisco",
                "sys": {"country": "US"},
                "main": {
                    "temp": 20.5,
                    "feels_like": 19.0,
                    "humidity": 65
                },
                "weather": [{"description": "clear sky"}]
            }
            mock_response.raise_for_status = Mock()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await service.get_weather("San Francisco")

                assert result["city"] == "San Francisco"
                assert result["country"] == "US"
                assert result["temperature"] == 20.5
                assert result["feels_like"] == 19.0
                assert result["humidity"] == 65
                assert result["description"] == "clear sky"
                assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_weather_no_api_key(self):
        """Test weather retrieval without API key."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.openweather_api_key = ""

            service = APIToolsService()

            result = await service.get_weather("San Francisco")

            assert "error" in result
            assert "not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_get_hacker_news_top_success(self):
        """Test successful Hacker News top stories retrieval."""
        with patch('services.api_tools.get_settings'):
            service = APIToolsService()

            # Mock top stories IDs response
            mock_ids_response = Mock()
            mock_ids_response.json.return_value = [1, 2, 3]

            # Mock individual story responses
            mock_story1 = Mock()
            mock_story1.json.return_value = {
                "title": "Story 1",
                "url": "https://example.com/1",
                "score": 100,
                "descendants": 50
            }

            mock_story2 = Mock()
            mock_story2.json.return_value = {
                "title": "Story 2",
                "url": "https://example.com/2",
                "score": 85,
                "descendants": 30
            }

            mock_story3 = Mock()
            mock_story3.json.return_value = {
                "title": "Story 3",
                "score": 70
                # No URL or descendants
            }

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(
                    side_effect=[mock_ids_response, mock_story1, mock_story2, mock_story3]
                )
                mock_client_class.return_value = mock_client

                result = await service.get_hacker_news_top(limit=3)

                assert "stories" in result
                assert len(result["stories"]) == 3
                assert result["stories"][0]["title"] == "Story 1"
                assert result["stories"][0]["url"] == "https://example.com/1"
                assert result["stories"][0]["score"] == 100
                assert result["stories"][0]["comments"] == 50
                assert result["stories"][2]["url"] == ""
                assert result["stories"][2]["comments"] == 0

    @pytest.mark.asyncio
    async def test_get_hacker_news_top_empty(self):
        """Test Hacker News with no stories."""
        with patch('services.api_tools.get_settings'):
            service = APIToolsService()

            mock_ids_response = Mock()
            mock_ids_response.json.return_value = []

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_client.get = AsyncMock(return_value=mock_ids_response)
                mock_client_class.return_value = mock_client

                result = await service.get_hacker_news_top()

                assert result["stories"] == []

    @pytest.mark.asyncio
    async def test_get_crypto_price_http_error(self):
        """Test cryptocurrency API HTTP error handling."""
        with patch('services.api_tools.get_settings'):
            service = APIToolsService()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = httpx.HTTPError("API Error")
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with pytest.raises(httpx.HTTPError):
                    await service.get_crypto_price("bitcoin")

    @pytest.mark.asyncio
    async def test_get_weather_http_error(self):
        """Test weather API HTTP error handling."""
        with patch('services.api_tools.get_settings') as mock_settings:
            mock_settings.return_value.openweather_api_key = "test-key"

            service = APIToolsService()

            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__.return_value = mock_client
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = httpx.HTTPError("City not found")
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with pytest.raises(httpx.HTTPError):
                    await service.get_weather("InvalidCity")
