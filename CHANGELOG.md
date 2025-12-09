# Changelog

## 2025-12-01 (Latest)

### Features
- **OpenRouter Integration**
  - Added OpenRouter as LLM provider alternative to local llama.cpp
  - Streaming via Server-Sent Events (SSE) forwarded to WebSocket
  - Configurable generation parameters: temperature, top_p, penalties, max_tokens
  - Support for multiple models via single API key (GPT-4, Claude, Gemini, etc.)
  - Complete implementation in `llm_service.py` with both streaming and non-streaming modes

### Improvements
- Conversations Management
  - Backend: added router with list/get/messages/create/rename/delete/bulk delete endpoints
  - Frontend: Conversations tab with list, open, rename, delete, and Delete All
  - DB: `title` column added with safe migration
- Chat Persistence
  - Hydrate state from `localStorage` using lazy initializers; removed mount rehydration effect
  - Chat can load selected conversation messages from backend
- External Data Prompting
  - System prompt updated to use provided tool data (e.g., Hacker News) and avoid browsing disclaimers
- Startup Responsiveness
  - Vector store lazily loads the embedding model on first use
- Dev WebSocket Stability
  - Cleanup guards only closing `OPEN` sockets to reduce dev-mode errors
- Bug Fixes
  - Fixed missing React `useState` import in Conversations
  - Fixed preview truncation string in conversations service

## 2025-11-30
- Initial documentation and architecture setup
- RAG pipeline (documents → vectorstore → retrieval → LLM)
