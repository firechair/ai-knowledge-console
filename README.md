# AI Knowledge Console

[![License: GPL v3 + Non-Commercial](https://img.shields.io/badge/License-GPL%20v3%20%2B%20Non--Commercial-blue.svg)](LICENSE)

## 📚 Documentation

**For detailed documentation, see the [docs/](docs/) directory:**

- 📖 **[Configuration Guide](docs/CONFIGURATION.md)** - Complete environment variable reference
- 🎯 **[Usage Guide](docs/USAGE_GUIDE.md)** - Practical examples and workflows
- 🔐 **[OAuth Setup](docs/OAUTH_SETUP.md)** - Gmail, Drive, Slack, Notion integration
- 💻 **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - API reference and development setup
- 🏗️ **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and technical details
- 🐛 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- 🤝 **[Contributing](docs/CONTRIBUTING.md)** - How to contribute


An end-to-end Retrieval-Augmented Generation (RAG) web application. Upload your documents (PDF, DOCX, TXT), index them into a vector store (ChromaDB) with `SentenceTransformers`, and chat with a local LLM (llama.cpp) enriched by relevant document context and optional external tools (GitHub, Crypto, Weather, Hacker News, Gmail, Drive, Slack, Notion).

## ⚡ Quick Start (Works Immediately)

**The core RAG functionality works out-of-the-box with no API keys required:**
- ✅ Upload documents (PDF, DOCX, TXT)
- ✅ Chat with your documents using RAG
- ✅ **Granular Context Control**: Select specific documents to use as context
- ✅ Conversation memory
- ✅ Streaming responses

**Optional integrations** (configure later if needed):
- 🔧 External APIs (GitHub, Weather, Crypto, Hacker News)
- 🔐 OAuth services (Gmail, Drive, Slack, Notion)

See [Configuration](#optional-enhancements) below to enable optional features.

## Why This Matters for Recruiters

**This project demonstrates production-grade AI engineering:**
- Core RAG system works immediately (no setup friction)
- **Advanced UI/UX**: Responsive design, intuitive settings panels, and real-time feedback
- Optional integrations show OAuth 2.0 implementation skills
- Clean architecture: separation of required vs optional features
- Ready to clone and run - perfect for portfolio demonstration

## Features

### Core RAG System
- **Document Management**: Upload PDF, DOCX, TXT with chunking and ChromaDB indexing
- **Granular Context Control**: Select specific documents for targeted retrieval
- **Smart RAG Chat**: REST and WebSocket streaming with conversation memory
- **Conversation Management**: List, rename, delete, bulk operations with responsive UI

### Advanced Settings (NEW ⭐)
- **Unified Settings Panel**: Centralized configuration for all system settings
- **LLM Provider Selection**: Switch between local and cloud providers in real-time
- **Model Management**: Download GGUF models from HuggingFace with progress tracking
- **API Key Manager**: Secure storage and validation of service credentials
- **Cloud Provider Support**: OpenRouter (200+ models), OpenAI, custom endpoints

### File Generation (NEW ⭐)
- **Multi-Format Export**: Generate PDF, Markdown, or HTML from conversations
- **Direct Download**: One-click download from chat interface
- **Absolute URLs**: Docker-compatible URL generation for file access

### External Integrations
- **Public APIs**: Crypto prices (CoinGecko), Hacker News, GitHub commits, Weather (OpenWeather)
- **OAuth Services**: Gmail, Google Drive, Slack, Notion with unified connector panel
- **Tool Configuration**: Visual status indicators and in-app setup

### Production Ready
- **Docker Support**: Multi-stage builds, health checks, non-root user
- **CI/CD**: GitHub Actions with automated builds to GHCR
- **Deployment Options**: Docker Compose, Traefik reverse proxy, systemd service
- **Security**: CORS, rate limiting, request ID tracking, structured logging

## Quick Demo
<video src="docs/media/Registrazione%20schermo%202025-12-26%20alle%2011.26.52.mov" autoplay loop muted playsinline width="800"></video>

**New Workflow Demonstrated:**
1. **Upload**: Uploading a CV/Resume PDF.
2. **Context Selection**: Opening the **new Settings Panel** (right-aligned) and specifically selecting the uploaded CV.
3. **Chat**: Asking "Can you make a pdf format of these information provided?"
4. **Response**: The LLM generates a structured response based *only* on the selected document.

## 🎉 What's New (v2.0 - December 2025)

This is a major enhancement of the AI Knowledge Console with new enterprise features:

- **🎛️ Advanced Settings Management**: Unified settings UI for configuring LLM providers, API keys, and models
- **☁️ Multi-Provider LLM Support**: Seamlessly switch between local (llama.cpp), OpenRouter, OpenAI, and custom endpoints
- **📦 Model Management**: Download and manage GGUF models from HuggingFace directly in the UI
- **📄 File Generation**: Export conversations as PDF, Markdown, or HTML with one click
- **🏗️ Enhanced Architecture**: Modular component structure with clean separation of concerns
- **⚙️ Settings Persistence**: User preferences saved in settings.json with automatic migration

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## Architecture

> 📖 **Complete Documentation**:
> - [Architecture Guide](docs/ARCHITECTURE.md) - Detailed system design and Docker optimization
> - [Developer Guide](docs/DEVELOPER_GUIDE.md) - Complete API reference and development setup
> - [Contributing Guide](docs/CONTRIBUTING.md) - How to contribute to the project

### Quick Overview

**Backend:**
- FastAPI with modular services (LLM, VectorStore, File, Config, ModelManager)
- Multi-provider LLM abstraction (local/cloud switching)
- ChromaDB for vector storage, SQLite for conversations
- OAuth 2.0 integrations for external services

**Frontend:**
- React + Vite with organized component structure
- Tailwind CSS + Radix UI components
- WebSocket streaming for real-time responses
- Settings management with visual feedback

**Infrastructure:**
- Docker Compose orchestration
- Nginx reverse proxy
- Traefik support with automatic TLS (Let's Encrypt)
- CI/CD via GitHub Actions → GHCR

**Ports:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- LLM (host): `http://localhost:8080`

## Tech Stack
- Backend: Python 3.11, FastAPI, Gunicorn+Uvicorn, httpx
- RAG: ChromaDB, sentence-transformers
- Frontend: React + Vite, Tailwind CSS, React Query, Radix UI (Popover/Dialogs)
- Containerization: Docker, Docker Compose; Nginx production static serving
- CI/CD: GitHub Actions, GHCR (GitHub Container Registry)

## Prerequisites
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- For macOS on Apple Silicon, Colima is supported as an alternative to Docker Desktop
- For local development (optional): Python 3.11+, Node 18+
- **LLM Server**: Choose one of the following options:
  - Local llama.cpp server (recommended for privacy)
  - OpenAI API (fastest to set up)
  - Any OpenAI-compatible API (Ollama, LocalAI, vLLM, etc.)

## LLM Setup Guide

Choose one option to power AI responses:

### Option 1: llama.cpp (Local, Private)

**Best for**: Privacy, no API costs, offline use

1. **Download llama.cpp** and a model:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp && make
   # Download GGUF model from HuggingFace
   ```

2. **Start the server**:
   ```bash
   ./server -m /path/to/model.gguf -c 4096 --port 8080 --host 0.0.0.0
   ```

3. **Configure** `backend/.env`:
   ```env
   LLM_PROVIDER=local
   LLM_BASE_URL=http://localhost:8080
   ```

### Option 2: OpenRouter (Cloud Models)

**Best for**: No local setup, access to GPT-4, Claude, Gemini, etc.

1. **Get API key** from [OpenRouter](https://openrouter.ai/keys)

2. **Configure** `backend/.env`:
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENROUTER_MODEL=x-ai/grok-4.1-fast
   ```

**Popular models**: `anthropic/claude-3.5-sonnet`, `openai/gpt-4-turbo`, `google/gemini-pro-1.5`
See [all models](https://openrouter.ai/models)

### Option 3: Ollama (Easy Local)

**Best for**: Simplicity, automatic model management

```bash
# Install
brew install ollama  # macOS
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull model and start
ollama pull llama3.1:8b
ollama serve
```

**Configure** `backend/.env`:
```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:11434/v1
```

📖 **Complete setup guide**: See [CONFIGURATION.md](docs/CONFIGURATION.md#llm-provider-settings) for advanced options


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

## Usage
1. Start the LLM server on host at port 8080.
2. Start the app (Docker or local dev).
3. Upload documents via the UI; the backend extracts text, chunks and indexes into ChromaDB.
4. Chat:
   - Click the **Settings icon** (next to the input bar) to open the control panel.
   - **Select Documents**: Choose specific files to use as context (or default to all).
   - **Select Tools**: Enable external tools (`github`, `crypto`, `weather`, `hackernews`).
     - *Note*: Unconfigured tools will appear grayed out and prompt for setup.
   - **(Optional)** Authorize OAuth services (`gmail`, `drive`, `slack`, `notion`) via Connectors tab.
   - Streaming responses are available via WebSocket.
   - Click "New" in Conversations to start a fresh conversation; open a conversation to hydrate Chat with its history; rename conversations inline.

## Configuration

### Minimum Setup

**Create `backend/.env`** with LLM provider settings (see [LLM Setup Guide](#llm-setup-guide)):

```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080
```

That's it! Core RAG functionality works with just these two variables.

### Optional Features

**Simple API Tools** (no OAuth required):
```env
GITHUB_TOKEN=your_token           # Repository commit search
OPENWEATHER_API_KEY=your_key      # Weather conditions
```

**OAuth Integrations** (Gmail, Drive, Slack, Notion):
- See complete guide: [OAUTH_SETUP.md](docs/OAUTH_SETUP.md)
- Quick: Create OAuth apps, add credentials to `.env`, authorize in UI

**Quick start**:
```bash
cp backend/.env.example backend/.env
# Edit with your LLM provider settings
```

📖 **Complete configuration reference**: See [CONFIGURATION.md](docs/CONFIGURATION.md) for all environment variables

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
VITE_API_URL=http://localhost:8000 npm run dev
```
Default dev ports: frontend (5173), backend (8000). CORS allows `http://localhost:5173` and `http://localhost:3000`.

## API Overview

> 📖 **Complete API Reference**: See [Developer Guide](docs/DEVELOPER_GUIDE.md#api-reference) for detailed endpoint documentation with examples.

**Key Endpoints:**
- **Documents**: Upload, list, delete indexed documents
- **Chat**: Streaming (WebSocket) and non-streaming query endpoints
- **Conversations**: Full CRUD operations with search and bulk delete
- **Models**: Download and manage GGUF and embedding models
- **API Keys**: Manage service credentials with status validation
- **Files**: Generate and download PDF, Markdown, HTML exports
- **Settings**: Get and update system configuration
- **Connectors**: OAuth integration management
- **Health**: Health check endpoint for monitoring

All endpoints are prefixed with `/api` and documented in the [Developer Guide](docs/DEVELOPER_GUIDE.md).

## Deploy from GHCR
Use the prebuilt images:
```bash
cd deploy
docker compose -f docker-compose.ghcr.yml up -d
```
The compose file pulls:
- `ghcr.io/firechair/ai-knowledge-console/backend:latest`
- `ghcr.io/firechair/ai-knowledge-console/frontend:latest`

## Demo Options
- Build locally and run:
  - `cd docker && docker compose up -d`
  - Frontend: `http://127.0.0.1:3000`, Backend API: `http://127.0.0.1:8000`
- Pull prebuilt images from GHCR (requires public images or `docker login ghcr.io`):
  - `cd deploy && docker compose -f docker-compose.ghcr.yml up -d`
  - Frontend: `http://localhost:3000`, Backend proxied via Nginx
- Traefik local proxy with GHCR images (HTTP only):
  - `cd deploy/traefik && docker compose -f docker-compose.local.yml up -d`
  - App: `http://localhost`, API: `http://localhost/api`
- Traefik local proxy using locally built images (no registry):
  - Build local images via `docker/docker-compose.yml`
  - `cd deploy/traefik && docker compose -f docker-compose.local-built.yml up -d`
  - App: `http://localhost`, API: `http://localhost/api`

## TLS with Traefik
Requirements:
- DNS A/AAAA record for your domain pointing to the server
- `TRAEFIK_EMAIL` and `TRAEFIK_DOMAIN` set

Steps:
```bash
cd deploy/traefik
mkdir -p acme && touch acme/acme.json && chmod 600 acme/acme.json
TRAEFIK_EMAIL=you@example.com TRAEFIK_DOMAIN=console.example.com \
  docker compose -f docker-compose.traefik.yml up -d
```
Routes:
- `https://<domain>/` → frontend (Nginx)
- `https://<domain>/api/...` → backend (FastAPI)
HTTP is redirected to HTTPS automatically.

## Local Reverse Proxy (Traefik)
Run the stack locally with Traefik (HTTP only):
```bash
cd deploy/traefik
docker compose -f docker-compose.local.yml up -d
```
Routes:
- `http://localhost/` → frontend (Nginx)
- `http://localhost/api/...` → backend (FastAPI)

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

## Configuration Guide
Backend (`backend/.env`):
- `LLM_PROVIDER` — e.g. `local`
- `LLM_BASE_URL` — e.g. `http://localhost:8080`
- `CHROMA_PERSIST_DIR` — vectorstore path
- `GITHUB_TOKEN` — GitHub API token (optional)
- `OPENWEATHER_API_KEY` — OpenWeather token (optional)
- `allowed_origins` — comma-separated origins for CORS
- `max_upload_mb` — upload size limit
- `rate_limit_enabled`, `rate_limit_requests`, `rate_limit_window_sec`

Frontend:
- `VITE_API_URL` — defaults to `/api` via Nginx proxy; override if needed

Docker Compose:
- `env_file` — backend reads `../backend/.env`
- `volumes` — mount persistent storage for vectorstore/uploads
- `extra_hosts` — Linux `host-gateway` to reach host LLM

Traefik:
- Local demo: use `docker-compose.local.yml` (HTTP only)
- Production: use the TLS compose with `TRAEFIK_EMAIL` and `TRAEFIK_DOMAIN`

## Troubleshooting

For comprehensive troubleshooting help, see the [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

**Quick checks**:
- Backend health: `curl http://localhost:8000/health`
- View logs: `docker compose logs -f backend`
- Restart services: `docker compose restart`

## Single-VM Deployment
Minimum specs:
- 4 vCPU, 8 GB RAM (more for larger models)
- Persistent storage for `vectorstore` and uploads

Run as a service:
```bash
cd deploy
docker compose -f docker-compose.ghcr.yml up -d
```

Systemd example:
```ini
[Unit]
Description=AI Knowledge Console
After=network.target docker.service
Requires=docker.service

[Service]
WorkingDirectory=/opt/ai-knowledge-console/deploy
Environment=LLM_BASE_URL=http://localhost:8080
ExecStart=/usr/bin/docker compose -f docker-compose.ghcr.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.ghcr.yml down
Restart=always

[Install]
WantedBy=multi-user.target
```
