# Developer Guide

## Overview
This guide covers local development, runtime behavior, data persistence, and common dev-mode considerations.

## Local Development
- Backend
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r backend/requirements.txt`
  - `uvicorn app:app --reload --port 8000`
- Frontend
  - `npm ci && npm run dev` (default at `http://localhost:5173/`)
- Health check: `GET http://localhost:8000/health`

## Runtime Behavior Changes
- Lazy Embedding Model Load
  - The embedding model in `VectorStoreService` loads on first use (document add/search) instead of at app startup.
  - Improves server responsiveness on port `8000` during development.
- Chat Persistence
  - Frontend initializes chat state from `localStorage` to avoid rehydration races on mount.
  - Opening a conversation hydrates messages from backend.
- WebSocket Cleanup Guard
  - On unmount, the client closes the socket only if it is `OPEN`, reducing dev-mode errors when effects are double-invoked.
- External Data Prompting
  - System prompt instructs the model to use provided “External Data” (e.g., Hacker News) and avoid browsing disclaimers.

## Data Persistence
- SQLite DB: `backend/conversations.db`
  - Tables: `conversations (id, created_at, title)`, `messages` (conversation_id, role, content)
- ChromaDB: `vectorstore/chroma`
  - Persistent collection `documents`
- Frontend State
  - `localStorage` key: `akconsole_chat_state`

## CORS
- Allowed origins: `http://localhost:5173`, `http://localhost:3000` (configurable via `.env`)

## Connectors and Tools
- Enable/disable connectors via `/api/connectors/`.
- Tools invoked by chat include GitHub, Crypto, Weather, and Hacker News.

## Notes for Strict Mode
- React dev Strict Mode may double-invoke effects.
- Guarded WebSocket close mitigates transient “closed before established” logs.

## Verification
- Health: `curl http://localhost:8000/health`
- Conversations list: `curl http://localhost:8000/api/conversations/`
- Documents list: `curl http://localhost:8000/api/documents/list`
