# AI Knowledge Console

An end-to-end Retrieval-Augmented Generation (RAG) web application. Upload your documents (PDF, DOCX, TXT), index them into a vector store (ChromaDB) with `SentenceTransformers`, and chat with a local LLM (llama.cpp) enriched by relevant document context and optional external tools (GitHub, Crypto, Weather, Hacker News).

## Why It’s Useful
- Consolidates document ingestion, semantic search, and LLM chat into one console.
- Adds optional real-time external data via tools for more grounded answers.
- Ships with production-ready Docker setup (FastAPI + Gunicorn/Uvicorn, React+Vite served by Nginx) and CI/CD so builds are reproducible and reviewable.

## Features
- Document upload: PDF, DOCX, TXT
- Chunking + ChromaDB persistent vector store
- RAG chat: REST and WebSocket streaming
- External tools: GitHub commits, crypto prices, weather, Hacker News
- Production Docker: multi-stage builds, healthchecks, non-root user
- CI/CD: GitHub Actions building and pushing Docker images to GHCR

## Architecture
- Backend (`/backend`): FastAPI app (`app.py`), served by Gunicorn with Uvicorn workers.
- Embeddings: `SentenceTransformer` model (`all-MiniLM-L6-v2`).
- Vector DB: ChromaDB persistent client (`/vectorstore/chroma`).
- LLM: llama.cpp server running on host at `http://localhost:8080`.
- Frontend (`/frontend`): React + Vite (built and served by Nginx).
- Docker Compose (`/docker`): Orchestrates backend and frontend, proxies `/api` through Nginx to backend.

Ports
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- LLM (host): `http://localhost:8080`

## Tech Stack
- Backend: Python 3.11, FastAPI, Gunicorn+Uvicorn, httpx
- RAG: ChromaDB, sentence-transformers
- Frontend: React + Vite, Tailwind CSS, axios, React Query
- Containerization: Docker, Docker Compose; Nginx production static serving
- CI/CD: GitHub Actions, GHCR (GitHub Container Registry)

## Prerequisites
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- For macOS on Apple Silicon, Colima is supported as an alternative to Docker Desktop
- For local development (optional): Python 3.11+, Node 18+
- A local llama.cpp server listening on `http://localhost:8080`

### Start llama.cpp locally
Ensure you have a model on disk and start the server (example):
```bash
./server -m /path/to/model.gguf -c 4096 --port 8080
```
Consult llama.cpp docs for platform-specific build steps and model selection.

## Quickstart: Docker (macOS/Windows)
1. Start Docker Desktop
2. From the project root:
```bash
cd docker
docker compose up --build -d
```
3. Open `http://localhost:3000`

The frontend talks to backend at `http://backend:8000` via Nginx, and backend reaches the host LLM using `http://host.docker.internal:8080`.

## Quickstart: Docker (Linux)
- `host.docker.internal` is not always available by default. This compose file sets:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```
so the backend can reach the host LLM at `http://host.docker.internal:8080`.
Run:
```bash
cd docker
docker compose up --build -d
```

## Quickstart: Colima (macOS, Apple Silicon)
```bash
brew install colima
colima start
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
cd docker
docker compose up --build -d
```

## Local Development (without Docker)

Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Frontend
```bash
cd frontend
npm ci
npm run dev
```
Default dev ports: frontend (5173), backend (8000). CORS allows `http://localhost:5173` and `http://localhost:3000`.

## Configuration
Backend loads `.env` from `/backend/.env`:
```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080
CHROMA_PERSIST_DIR=../vectorstore/chroma
GITHUB_TOKEN=
OPENWEATHER_API_KEY=
```
When running Docker, backend uses `env_file: ../backend/.env` and internally reaches the LLM at `http://host.docker.internal:8080`.

## Usage
1. Start the LLM server on host at port 8080.
2. Start the app (Docker or local dev).
3. Upload documents via the UI; the backend extracts text, chunks and indexes into ChromaDB.
4. Chat:
   - Toggle “Use documents” to enable RAG.
   - Optionally enable tools (`github`, `crypto`, `weather`, `hackernews`) and provide params.
   - Streaming responses are available via WebSocket.

## API Overview
- Documents
  - `POST /api/documents/upload` — Upload and index a document
  - `GET  /api/documents/list` — List indexed documents
  - `DELETE /api/documents/{filename}` — Delete indexed chunks for a document
- Chat
  - `POST /api/chat/query` — Non-streaming chat; accepts `{ message, use_documents, tools, tool_params }`
  - `WS   /api/chat/ws` — Streaming chat over WebSocket
- Health
  - `GET  /health` — Health probe used by Compose

## CI/CD
- GitHub Actions are included:
  - CI (`.github/workflows/ci.yml`):
    - Backend: Python 3.11; install `backend/requirements.txt`; sanity import checks; compile sources
    - Frontend: Node 18; `npm ci`; `npm run build` (Vite production build)
  - CD (`.github/workflows/docker.yml`):
    - On push to `main`: build and push Docker images to GHCR
    - Image tags:
      - `ghcr.io/firechair/ai-knowledge-console/backend:latest`
      - `ghcr.io/firechair/ai-knowledge-console/frontend:latest`
    - Uses built-in `GITHUB_TOKEN` with `packages: write` permission

This ensures every change is built and validated automatically; main branch produces ready-to-run images.

## Troubleshooting
- Docker daemon not running: start Docker Desktop (macOS/Windows) or ensure Docker Engine service is active (Linux).
- Linux LLM connectivity: use `host-gateway` mapping (already set). Confirm host LLM is listening on `:8080`.
- HuggingFace hub compatibility: repo pins `huggingface_hub==0.25.2` to match `sentence-transformers==2.2.2`.
- SSL warnings (`urllib3`): cosmetic on macOS LibreSSL, does not affect local development.

## License
Add your preferred license (MIT/Apache-2.0) before publishing.
