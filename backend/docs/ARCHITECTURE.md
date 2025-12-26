# Architecture

## Overview
- Framework: FastAPI (`backend/app.py`)
- Routers: `routers/*` included under `/api/*`
- Services: stateless helpers in `services/*`
- Middleware: error handling and access logging
- Config: `config.py` with `.env` loading (pydantic-settings)
- Vector store: `services/vector_store.py`
- Static files: served at `/static` for generated content

## Application Startup
- Lifespan initializes logging and vector store
  - `backend/app.py:21` lifespan context
  - `backend/app.py:24` structured logging
  - `backend/app.py:28` `VectorStoreService()` init

## Routers
- Documents: upload/list/delete (`backend/routers/documents.py`)
- Chat: sync/stream endpoints (`backend/routers/chat.py`)
- Connectors/Settings/Auth/Conversations/Models: respective features
- Files: generate and download (`backend/routers/files.py:8` router; endpoints at `:17` and `:37`)

## Services
- `LLMService`: Cloud/local generation and streaming (`backend/services/llm_service.py`)
- `DocumentProcessor`: PDF/DOCX/TXT extraction and chunking
- `VectorStoreService`: Adds, lists, deletes documents
- `FileService`: PDF/Markdown/HTML generation with absolute URLs
- `ConfigService`: Merges `settings.json` with env for LLM config

## Middleware & Logging
- Access logs with request id and duration (`backend/app.py:60`)
- Basic in-memory rate limiting with headers (`backend/app.py:65`)
- Custom exception handlers (`backend/middleware/error_handler.py`)

## Static Files
- Mounted at `/static` (`backend/app.py:127`)
- Generated output placed under `static/generated`

