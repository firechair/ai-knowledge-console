import pytest
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Ensure backend directory is in sys.path
backend_dir = os.path.join(os.path.dirname(__file__), "..")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from services.api_tools import APIToolsService
from services.llm_service import LLMService
from services.conversation_service import ConversationService
# Import directly from the file if package import fails
try:
    from routers.auth import get_google_auth_url
except ImportError:
    # Fallback: try adding routers to path
    sys.path.append(os.path.join(backend_dir, "routers"))
    from auth import get_google_auth_url

# Load environment variables
load_dotenv()

@pytest.mark.asyncio
class TestE2EReal:
    
    async def test_1_github_token_validation(self):
        """Test GitHub API with the provided token"""
        print("\n--- Test 1: GitHub Token Validation ---")
        token = os.getenv("GITHUB_TOKEN")
        print(f"Testing Token: {token[:4]}...{token[-4:]}")
        
        service = APIToolsService()
        try:
            data = await service.github_search_commits("facebook/react")
            assert "commits" in data
            print(f"✅ SUCCESS: Fetched {len(data['commits'])} commits.")
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            pytest.fail(f"GitHub API failed: {e}")

    async def test_2_google_oauth_flow(self):
        """Test Google OAuth URL Generation"""
        print("\n--- Test 2: Google OAuth Flow ---")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        print(f"Client ID: {client_id[:10]}...")
        
        auth_url = get_google_auth_url()
        print(f"Generated Auth URL: {auth_url}")
        
        assert "accounts.google.com" in auth_url
        assert client_id in auth_url
        assert "redirect_uri" in auth_url
        assert "scope" in auth_url
        print("✅ SUCCESS: Auth URL generated correctly.")

    async def test_3_rag_llm_weather(self):
        """Test RAG + Weather API with Real LLM"""
        print("\n--- Test 3: RAG + Weather + Real LLM ---")
        
        # 1. Get Weather Data
        api_service = APIToolsService()
        weather = await api_service.get_weather("London")
        print(f"Weather Data: {weather}")
        
        # 2. Generate LLM Response
        llm_service = LLMService()
        prompt = f"""
        Context: The user is asking about the weather.
        External Data: {weather}
        User Query: "What is the weather in London and should I take an umbrella?"
        """
        
        print("Generating LLM response (this may take time)...")
        try:
            response = await llm_service.generate(prompt)
            print(f"\n🤖 LLM Response:\n{response}")
            
            assert len(response) > 10
            assert "London" in response
            # Check for reasoning about umbrella based on description
            if "rain" in str(weather).lower() or "drizzle" in str(weather).lower():
                assert "umbrella" in response.lower()
            
            print("✅ SUCCESS: LLM generated relevant response.")
        except Exception as e:
            print(f"❌ FAILED: LLM generation failed. Is the server running? Error: {e}")
            # Don't fail the test if LLM is offline, just report it
            if "Connection refused" in str(e):
                pytest.skip("LLM Server not running at localhost:8080")
            else:
                raise e

    async def test_4_multi_source_reasoning(self):
        """Test Multi-source Reasoning (GitHub + HN)"""
        print("\n--- Test 4: Multi-source Reasoning ---")
        
        api_service = APIToolsService()
        
        # Fetch Data
        github_data = await api_service.github_search_commits("facebook/react")
        hn_data = await api_service.get_hacker_news_top(limit=3)
        
        # Generate Prompt
        prompt = f"""
        You are a tech analyst.
        
        GitHub Data (React): {str(github_data)[:500]}...
        Hacker News Top Stories: {str(hn_data)}
        
        Query: "Summarize the recent activity in React and top tech news."
        """
        
        llm_service = LLMService()
        try:
            response = await llm_service.generate(prompt)
            print(f"\n🤖 LLM Response:\n{response}")
            assert len(response) > 20
            print("✅ SUCCESS: Multi-source reasoning complete.")
        except Exception as e:
             if "Connection refused" in str(e):
                pytest.skip("LLM Server not running")
             raise e
