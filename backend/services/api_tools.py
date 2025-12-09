import httpx
from typing import Dict, Any, Optional
from config import get_settings
import os
from datetime import datetime
from services.oauth_tokens import get_token

class APIToolsService:
    def __init__(self):
        self.settings = get_settings()
    
    async def github_search_commits(
        self,
        repo: str,
        query: str = "",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search recent commits in a GitHub repository"""
        headers = {}
        gh_token = os.getenv("GITHUB_TOKEN") or self.settings.github_token
        if gh_token:
            headers["Authorization"] = f"token {gh_token}"
            headers["User-Agent"] = "AI-Knowledge-Console"
        
        # Debug print (safe)
        if gh_token:
            print(f"Using GitHub Token: {gh_token[:4]}...{gh_token[-4:]}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo}/commits",
                headers=headers,
                params={"per_page": limit}
            )
            response.raise_for_status()
            
            commits = response.json()
            return {
                "repository": repo,
                "commits": [
                    {
                        "sha": c["sha"][:7],
                        "message": c["commit"]["message"].split("\n")[0],
                        "author": c["commit"]["author"]["name"],
                        "date": c["commit"]["author"]["date"]
                    }
                    for c in commits
                ]
            }
    
    async def get_crypto_price(self, symbol: str = "bitcoin") -> Dict[str, Any]:
        """Get current cryptocurrency price"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": symbol.lower(),
                    "vs_currencies": "usd,eur",
                    "include_24hr_change": "true"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if symbol.lower() in data:
                return {
                    "symbol": symbol,
                    "price_usd": data[symbol.lower()].get("usd"),
                    "price_eur": data[symbol.lower()].get("eur"),
                    "change_24h": data[symbol.lower()].get("usd_24h_change"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            return {"error": f"Symbol {symbol} not found"}
    
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        api_key = os.getenv("OPENWEATHER_API_KEY") or self.settings.openweather_api_key
        if not api_key:
            return {"error": "Weather API key not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def gmail_search(self, query: str = "") -> Dict[str, Any]:
        token = get_token("google", "default_user")
        if not token:
            return {"error": "Gmail not authorized"}
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers,
                params={"q": query, "maxResults": 10},
            )
            if resp.status_code != 200:
                return {"error": resp.text}
            data = resp.json()
            return {"messages": data.get("messages", [])}

    async def drive_search(self, query: str = "") -> Dict[str, Any]:
        token = get_token("google", "default_user")
        if not token:
            return {"error": "Drive not authorized"}
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params={"q": f"name contains '{query}'", "fields": "files(id,name,mimeType,modifiedTime)", "pageSize": 10},
            )
            if resp.status_code != 200:
                return {"error": resp.text}
            return {"files": resp.json().get("files", [])}

    async def slack_search_messages(self, query: str = "") -> Dict[str, Any]:
        token = get_token("slack", "default_user")
        if not token:
            return {"error": "Slack not authorized"}
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://slack.com/api/search.messages",
                headers=headers,
                params={"query": query, "count": 10},
            )
            data = resp.json()
            if not data.get("ok"):
                return {"error": data.get("error", "unknown_error")}
            return {"messages": data.get("messages", {}).get("matches", [])}

    async def notion_search(self, query: str = "") -> Dict[str, Any]:
        token = get_token("notion", "default_user")
        if not token:
            return {"error": "Notion not authorized"}
        headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.notion.com/v1/search",
                headers=headers,
                json={"query": query, "page_size": 10},
            )
            if resp.status_code != 200:
                return {"error": resp.text}
            return {"results": resp.json().get("results", [])}
    
    async def get_hacker_news_top(self, limit: int = 10) -> Dict[str, Any]:
        """Get top Hacker News stories"""
        async with httpx.AsyncClient() as client:
            # Get top story IDs
            response = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            story_ids = response.json()[:limit]
            
            # Fetch each story
            stories = []
            for sid in story_ids:
                resp = await client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                )
                story = resp.json()
                stories.append({
                    "title": story.get("title"),
                    "url": story.get("url", ""),
                    "score": story.get("score"),
                    "comments": story.get("descendants", 0)
                })
            
            return {"stories": stories}
