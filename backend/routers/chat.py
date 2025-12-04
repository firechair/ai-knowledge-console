from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Depends
from pydantic import BaseModel
from typing import Optional, List
import json

from services.llm_service import LLMService
from services.api_tools import APIToolsService
from services.conversation_service import ConversationService
from services.vector_store import VectorStoreService
from dependencies import (
    get_llm_service,
    get_api_tools,
    get_conversation_service,
    get_vector_store
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    use_documents: bool = True
    tools: Optional[List[str]] = None  # e.g., ["github", "crypto", "weather"]
    tool_params: Optional[dict] = None
    conversation_id: Optional[str] = None  # Track conversation for history

@router.post("/query")
async def chat_query(
    chat_request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    conversation_service: ConversationService = Depends(get_conversation_service),
    api_tools: APIToolsService = Depends(get_api_tools)
):
    """Non-streaming chat endpoint"""
    # Get or create conversation ID
    conv_id = chat_request.conversation_id or conversation_service.create_conversation()

    # Retrieve conversation history
    history = conversation_service.get_history(conv_id, limit=10)

    # Save user message
    conversation_service.add_message(conv_id, "user", chat_request.message)

    # Retrieve relevant context
    context_chunks = []
    if chat_request.use_documents:
        context_chunks = vector_store.search(chat_request.message, n_results=5)

    # Fetch external API data if requested
    api_data = {}
    if chat_request.tools:
        api_data = await _fetch_tool_data(
            chat_request.tools,
            chat_request.tool_params or {},
            api_tools
        )

    # Build RAG prompt with history
    prompt = llm_service.build_rag_prompt(
        chat_request.message, context_chunks, api_data if api_data else None, history
    )

    # Generate response
    system_prompt = (
        "You are an AI assistant with access to documents and external data. "
        "Provide accurate, helpful answers based on the context provided."
    )

    response = await llm_service.generate(prompt, system_prompt)

    # Save assistant response
    conversation_service.add_message(conv_id, "assistant", response)

    return {
        "response": response,
        "sources": [c["metadata"]["filename"] for c in context_chunks],
        "api_data_used": list(api_data.keys()) if api_data else [],
        "conversation_id": conv_id,
    }

@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    llm_service: LLMService = Depends(get_llm_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    conversation_service: ConversationService = Depends(get_conversation_service),
    api_tools: APIToolsService = Depends(get_api_tools)
):
    """WebSocket endpoint for streaming chat"""
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")
            use_documents = message_data.get("use_documents", True)
            tools = message_data.get("tools", [])
            tool_params = message_data.get("tool_params", {})
            conv_id = message_data.get("conversation_id")

            # Get or create conversation
            if not conv_id:
                conv_id = conversation_service.create_conversation()

            # Get conversation history
            history = conversation_service.get_history(conv_id, limit=10)

            # Save user message
            conversation_service.add_message(conv_id, "user", user_message)

            # Retrieve context
            context_chunks = []
            if use_documents:
                context_chunks = vector_store.search(user_message, n_results=5)

            # Fetch API data
            api_data = {}
            if tools:
                api_data = await _fetch_tool_data(tools, tool_params, api_tools)
                # Send API data first
                await websocket.send_json({"type": "api_data", "data": api_data})

            # Build prompt with history
            prompt = llm_service.build_rag_prompt(
                user_message, context_chunks, api_data if api_data else None, history
            )

            system_prompt = (
                "You are an AI assistant with access to documents and external data. "
                "Provide accurate, helpful answers based on the context provided."
            )

            # Stream response
            await websocket.send_json({"type": "start"})

            full_response = ""
            async for token in llm_service.generate_stream(prompt, system_prompt):
                full_response += token
                await websocket.send_json({"type": "token", "content": token})

            # Save assistant response
            conversation_service.add_message(conv_id, "assistant", full_response)

            # Send completion signal with sources and conversation ID
            await websocket.send_json(
                {
                    "type": "end",
                    "sources": [c["metadata"]["filename"] for c in context_chunks],
                    "conversation_id": conv_id,
                }
            )

    except WebSocketDisconnect:
        print("Client disconnected")


async def _fetch_tool_data(
    tools: List[str],
    params: dict,
    api_tools: APIToolsService
) -> dict:
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
            elif tool == "drive":
                data["drive"] = {"error": "Drive connector requires configuration"}
            elif tool == "slack":
                data["slack"] = {"error": "Slack connector requires configuration"}
        except Exception as e:
            data[tool] = {"error": str(e)}

    return data


@router.get("/conversations")
async def list_conversations(
    search: Optional[str] = None,
    limit: int = 50,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    List or search conversations.
    
    Query Parameters:
        search: Optional search term to filter conversations
        limit: Maximum number of conversations to return (default: 50)
    
    Returns:
        List of conversations with id, title, preview, and created_at
    """
    if search:
        conversations = conversation_service.search_conversations(search, limit)
    else:
        conversations = conversation_service.list_conversations(limit)

    return {"conversations": conversations}

