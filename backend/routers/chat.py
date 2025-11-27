from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
from typing import Optional, List
import json

from services.llm_service import LLMService
from services.api_tools import APIToolsService

router = APIRouter()
llm_service = LLMService()
api_tools = APIToolsService()

class ChatRequest(BaseModel):
    message: str
    use_documents: bool = True
    tools: Optional[List[str]] = None  # e.g., ["github", "crypto", "weather"]
    tool_params: Optional[dict] = None

@router.post("/query")
async def chat_query(request: Request, chat_request: ChatRequest):
    """Non-streaming chat endpoint"""
    vector_store = request.app.state.vector_store
    
    # Retrieve relevant context
    context_chunks = []
    if chat_request.use_documents:
        context_chunks = vector_store.search(chat_request.message, n_results=5)
    
    # Fetch external API data if requested
    api_data = {}
    if chat_request.tools:
        api_data = await _fetch_tool_data(chat_request.tools, chat_request.tool_params or {})
    
    # Build RAG prompt
    prompt = llm_service.build_rag_prompt(
        chat_request.message,
        context_chunks,
        api_data if api_data else None
    )
    
    # Generate response
    system_prompt = (
        "You are an AI assistant with access to documents and external data. "
        "Provide accurate, helpful answers based on the context provided."
    )
    
    response = await llm_service.generate(prompt, system_prompt)
    
    return {
        "response": response,
        "sources": [c["metadata"]["filename"] for c in context_chunks],
        "api_data_used": list(api_data.keys()) if api_data else []
    }

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, request: Request = None):
    """WebSocket endpoint for streaming chat"""
    await websocket.accept()
    
    # Get vector store from app state
    # Note: In WebSocket, we need to access it differently
    from services.vector_store import VectorStoreService
    vector_store = VectorStoreService()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            use_documents = message_data.get("use_documents", True)
            tools = message_data.get("tools", [])
            tool_params = message_data.get("tool_params", {})
            
            # Retrieve context
            context_chunks = []
            if use_documents:
                context_chunks = vector_store.search(user_message, n_results=5)
            
            # Fetch API data
            api_data = {}
            if tools:
                api_data = await _fetch_tool_data(tools, tool_params)
                # Send API data first
                await websocket.send_json({
                    "type": "api_data",
                    "data": api_data
                })
            
            # Build prompt
            prompt = llm_service.build_rag_prompt(
                user_message,
                context_chunks,
                api_data if api_data else None
            )
            
            system_prompt = (
                "You are an AI assistant with access to documents and external data. "
                "Provide accurate, helpful answers based on the context provided."
            )
            
            # Stream response
            await websocket.send_json({"type": "start"})
            
            async for token in llm_service.generate_stream(prompt, system_prompt):
                await websocket.send_json({
                    "type": "token",
                    "content": token
                })
            
            # Send completion signal with sources
            await websocket.send_json({
                "type": "end",
                "sources": [c["metadata"]["filename"] for c in context_chunks]
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")

async def _fetch_tool_data(tools: List[str], params: dict) -> dict:
    """Fetch data from requested tools"""
    data = {}
    
    for tool in tools:
        try:
            if tool == "github":
                repo = params.get("github_repo", "facebook/react")
                data["github"] = await api_tools.github_search_commits(repo)
            elif tool == "crypto":
                symbol = params.get("crypto_symbol", "bitcoin")
                data["crypto"] = await api_tools.get_crypto_price(symbol)
            elif tool == "weather":
                city = params.get("weather_city", "London")
                data["weather"] = await api_tools.get_weather(city)
            elif tool == "hackernews":
                data["hackernews"] = await api_tools.get_hacker_news_top()
        except Exception as e:
            data[tool] = {"error": str(e)}
    
    return data
