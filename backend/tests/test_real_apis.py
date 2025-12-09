import pytest
import os
import sys
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.api_tools import APIToolsService

# Load environment variables
load_dotenv()

@pytest.mark.asyncio
class TestRealAPIs:
    
    async def test_real_github_api(self):
        """Test GitHub API with REAL token"""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not found in .env")
            
        service = APIToolsService()
        # Use a known public repo
        data = await service.github_search_commits("facebook/react")
        
        assert "commits" in data
        commits = data["commits"]
        assert isinstance(commits, list)
        assert len(commits) > 0
        assert "message" in commits[0]
        assert "author" in commits[0]
        print(f"\n✅ GitHub API Success! Fetched {len(commits)} commits from facebook/react")

    async def test_real_weather_api(self):
        """Test OpenWeather API with REAL key"""
        key = os.getenv("OPENWEATHER_API_KEY")
        if not key:
            pytest.skip("OPENWEATHER_API_KEY not found in .env")
            
        service = APIToolsService()
        weather = await service.get_weather("London")
        
        assert "temperature" in weather
        assert "description" in weather
        print(f"\n✅ Weather API Success! Current weather in London: {weather}")

    async def test_real_crypto_api(self):
        """Test CoinGecko API (No key required)"""
        service = APIToolsService()
        price = await service.get_crypto_price("bitcoin")
        
        assert "symbol" in price
        assert price["symbol"] == "bitcoin"
        assert "price_usd" in price
        print(f"\n✅ Crypto API Success! Bitcoin price: ${price['price_usd']}")

    async def test_real_hackernews_api(self):
        """Test Hacker News API (No key required)"""
        service = APIToolsService()
        data = await service.get_hacker_news_top(limit=5)
        
        assert "stories" in data
        stories = data["stories"]
        assert isinstance(stories, list)
        assert len(stories) == 5
        assert "title" in stories[0]
        print(f"\n✅ Hacker News API Success! Top story: {stories[0]['title']}")
