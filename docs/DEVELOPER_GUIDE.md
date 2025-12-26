# Developer Guide

Complete reference for developing, testing, and contributing to the AI Knowledge Console.

## Table of Contents
- [Getting Started](#getting-started)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Recent Fixes & Implementations](#recent-fixes--implementations)

---

## Getting Started

### Prerequisites

- **Backend:** Python 3.11+
- **Frontend:** Node.js 18+
- **LLM Server:** llama.cpp or cloud provider (OpenRouter, OpenAI)
- **Git:** For version control

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn app:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm ci

# Run development server with API proxy
VITE_API_URL=http://localhost:8000 npm run dev
```

Frontend will be available at `http://localhost:5173`

### Development Workflow

1. **Start LLM Server** (if using local)
   ```bash
   # llama.cpp example
   ./server -m /path/to/model.gguf -c 4096 --port 8080 --host 0.0.0.0
   ```

2. **Start Backend** (in one terminal)
   ```bash
   cd backend && source .venv/bin/activate && uvicorn app:app --reload
   ```

3. **Start Frontend** (in another terminal)
   ```bash
   cd frontend && VITE_API_URL=http://localhost:8000 npm run dev
   ```

4. **Access Application**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

---

## Backend Development

### Project Structure

```
backend/
├── app.py                    # Main FastAPI application
├── config.py                 # Environment configuration (pydantic-settings)
├── routers/                  # API endpoints
│   ├── documents.py         # Document management
│   ├── chat.py              # Chat and WebSocket
│   ├── conversations.py     # Conversation CRUD
│   ├── files.py             # File generation
│   ├── models.py            # Model management
│   ├── api_keys.py          # API key management
│   ├── settings.py          # Settings endpoints
│   ├── connectors.py        # External tools
│   └── auth.py              # OAuth flows
├── services/                # Business logic layer
│   ├── llm_service.py       # LLM abstraction
│   ├── vector_store.py      # ChromaDB wrapper
│   ├── file_service.py      # File generation
│   ├── config_service.py    # Settings management
│   ├── model_manager.py     # Model downloads
│   ├── provider_registry.py # Cloud providers
│   ├── conversation_service.py # Conversation storage
│   ├── api_tools.py         # External APIs
│   └── oauth_tokens.py      # OAuth token management
├── schemas/                 # Pydantic models
│   └── llm_config.py        # LLM configuration
├── middleware/              # Middleware
│   └── error_handler.py     # Error handling
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── requirements.txt         # Python dependencies
└── pytest.ini              # Pytest configuration
```

### Services Deep Dive

#### LLMService (`backend/services/llm_service.py`)

**Responsibility:** Multi-provider LLM abstraction

**Key Methods:**
- `generate(prompt, messages, use_documents, tools, ...)` - Non-streaming generation
- `generate_stream(prompt, messages, use_documents, tools, ...)` - Streaming generation
- `_build_prompt(...)` - Construct RAG prompts with context

**Adding a New Provider:**

1. Update `provider_registry.py` with provider definition
2. Add provider-specific logic in `LLMService._get_provider_config()`
3. Implement streaming in `generate_stream()` if supported
4. Add tests in `tests/unit/test_llm_service.py`

#### VectorStoreService (`backend/services/vector_store.py`)

**Responsibility:** Document embedding and search

**Key Methods:**
- `add_document(text, metadata)` - Add document chunks
- `search(query, n_results, file_filters)` - Semantic search
- `list_documents()` - List indexed documents
- `delete_document(filename)` - Remove document

**Embedding Model:**
- Default: `all-MiniLM-L6-v2`
- Lazy-loaded on first use
- Cached in memory

#### ConfigService (`backend/services/config_service.py`)

**Responsibility:** Settings.json management

**Key Methods:**
- `get_llm_config()` - Get merged LLM configuration
- `update_settings(data)` - Update settings.json
- `get_api_keys()` - Get API keys status

**Configuration Precedence:**
1. Application defaults
2. settings.json
3. Environment variables (highest priority)

#### ModelManager (`backend/services/model_manager.py`)

**Responsibility:** Download and manage models

**Key Methods:**
- `download_model(repo, filename, model_type)` - Download from HuggingFace
- `list_models(model_type)` - List local models
- `get_download_status(download_id)` - Check download progress

**Supported Models:**
- GGUF models for llama.cpp
- SentenceTransformer embedding models

#### FileService (`backend/services/file_service.py`)

**Responsibility:** Generate downloadable files

**Key Methods:**
- `generate_markdown(content, filename)` - Generate MD file
- `generate_html(content, title, filename)` - Generate HTML file
- `generate_pdf(content, title, filename)` - Generate PDF file

**Important:** Returns absolute URLs for Docker compatibility

### Adding New Features

#### Creating a New Router

1. **Create router file** in `backend/routers/`:

```python
# backend/routers/my_feature.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

class MyRequest(BaseModel):
    data: str

@router.post("/")
async def my_endpoint(request: MyRequest):
    return {"result": f"Processed: {request.data}"}
```

2. **Register router** in `backend/app.py`:

```python
from routers import my_feature

app.include_router(my_feature.router, prefix="/api")
```

3. **Add tests** in `tests/integration/test_my_feature.py`

#### Implementing a Service

1. **Create service file** in `backend/services/`:

```python
# backend/services/my_service.py
class MyService:
    def __init__(self):
        # Initialize service
        pass

    def process_data(self, data: str) -> str:
        # Business logic
        return f"Processed: {data}"

# Singleton instance
_instance = None

def get_my_service() -> MyService:
    global _instance
    if _instance is None:
        _instance = MyService()
    return _instance
```

2. **Use in router** via dependency injection:

```python
from services.my_service import get_my_service, MyService

@router.post("/")
async def my_endpoint(
    request: MyRequest,
    service: MyService = Depends(get_my_service)
):
    result = service.process_data(request.data)
    return {"result": result}
```

### Database Migrations

**ConversationService** manages SQLite schema automatically.

**Adding a column:**

```python
# In services/conversation_service.py __init__
cursor.execute("PRAGMA table_info(conversations)")
columns = [col[1] for col in cursor.fetchall()]

if "new_column" not in columns:
    cursor.execute("ALTER TABLE conversations ADD COLUMN new_column TEXT")
    conn.commit()
```

---

## Frontend Development

### Project Structure

```
frontend/src/
├── components/
│   ├── layout/              # Application shell
│   │   ├── AppShell.jsx
│   │   ├── Header.jsx
│   │   └── Sidebar.jsx
│   ├── settings/            # Settings panels
│   │   ├── LLMProviderSelector.jsx
│   │   ├── CloudProviderSelector.jsx
│   │   ├── APIKeysManager.jsx
│   │   └── ModelManager.jsx
│   └── ui/                  # Reusable components
│       ├── Button.jsx
│       ├── Input.jsx
│       ├── Card.jsx
│       └── ChatMessage.jsx
├── pages/                   # Main views
│   ├── ChatPage.jsx
│   ├── DocumentsPage.jsx
│   ├── ConversationsPage.jsx
│   ├── ConnectorsPage.jsx
│   └── SettingsPage.jsx
├── hooks/                   # Custom hooks
│   ├── useAPIKeys.js
│   ├── useCloudProviders.js
│   └── useTheme.js
├── utils/
│   └── cn.js               # Class name utility
├── App.jsx                  # Root component
└── main.jsx                 # Entry point
```

### Component Guidelines

#### File Organization

- **layout/**: Application-level layout components
- **settings/**: Feature-specific settings panels
- **ui/**: Reusable, generic UI components
- **pages/**: Top-level route components

#### Props Patterns

**Good:**
```jsx
// Explicit prop types with default values
function Button({ children, variant = 'primary', onClick }) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  );
}
```

**Avoid:**
```jsx
// Spreading all props without validation
function Button(props) {
  return <button {...props} />;
}
```

#### State Management

**Use React Query for server state:**

```jsx
import { useQuery, useMutation } from '@tanstack/react-query';

function DocumentsPage() {
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await fetch('/api/documents/list');
      return res.json();
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (filename) =>
      fetch(`/api/documents/${filename}`, { method: 'DELETE' })
  });

  // ...
}
```

**Use useState for local UI state:**

```jsx
function ChatInput() {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Send message
    setMessage('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={message} onChange={(e) => setMessage(e.target.value)} />
    </form>
  );
}
```

### Adding a New Page

1. **Create page component** in `src/pages/`:

```jsx
// src/pages/MyPage.jsx
export function MyPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold">My Feature</h1>
      {/* Page content */}
    </div>
  );
}
```

2. **Add route** in `src/App.jsx`:

```jsx
import { MyPage } from './pages/MyPage';

function App() {
  return (
    <Routes>
      <Route path="/my-feature" element={<MyPage />} />
      {/* other routes */}
    </Routes>
  );
}
```

3. **Add navigation** in `src/components/layout/Sidebar.jsx`

---

## API Reference

Complete endpoint documentation for the AI Knowledge Console backend.

### Base URL

- **Local Development:** `http://localhost:8000`
- **Production:** `https://your-domain.com`

All endpoints are prefixed with `/api` unless otherwise noted.

---

### Documents API

#### Upload Document

**Endpoint:** `POST /api/documents/upload`

**Description:** Upload and index a document for RAG retrieval.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary) - PDF, DOCX, or TXT file

**Response:**
```json
{
  "status": "ok",
  "filename": "document.pdf",
  "chunks_added": 42
}
```

**Status Codes:**
- `200 OK` - Document uploaded successfully
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File exceeds size limit

#### List Documents

**Endpoint:** `GET /api/documents/list`

**Description:** List all indexed documents.

**Response:**
```json
{
  "documents": [
    {"filename": "document.pdf", "chunks": 42},
    {"filename": "notes.txt", "chunks": 15}
  ]
}
```

#### Delete Document

**Endpoint:** `DELETE /api/documents/{filename}`

**Description:** Delete a document and all its chunks from the vector store.

**Path Parameters:**
- `filename` (string) - Name of the document to delete

**Response:**
```json
{
  "status": "ok",
  "message": "Document 'document.pdf' deleted successfully"
}
```

---

### Chat API

#### Query (Non-Streaming)

**Endpoint:** `POST /api/chat/query`

**Description:** Send a chat query and get a complete response.

**Request:**
```json
{
  "message": "What is RAG?",
  "use_documents": true,
  "file_filters": ["document.pdf"],
  "tools": ["crypto", "hackernews"],
  "tool_params": {
    "crypto": {"coin": "bitcoin"}
  },
  "conversation_id": "uuid-here"
}
```

**Response:**
```json
{
  "response": "RAG stands for Retrieval-Augmented Generation...",
  "conversation_id": "uuid-here"
}
```

#### WebSocket Streaming

**Endpoint:** `WS /api/chat/ws`

**Description:** Streaming chat via WebSocket.

**Client Message:**
```json
{
  "message": "Tell me about...",
  "use_documents": true,
  "file_filters": [],
  "tools": [],
  "tool_params": {},
  "conversation_id": null
}
```

**Server Messages:**
```json
{"type": "token", "content": "Partial "}
{"type": "token", "content": "response"}
{"type": "done", "conversation_id": "uuid"}
{"type": "error", "error": "Error message"}
```

---

### Conversations API

#### List Conversations

**Endpoint:** `GET /api/conversations/`

**Description:** List all conversations with metadata.

**Query Parameters:**
- `search` (optional) - Search by title or message content

**Response:**
```json
[
  {
    "id": "uuid-1",
    "created_at": "2025-12-26T10:00:00",
    "title": "Discussion about RAG",
    "last_message_preview": "What is RAG?",
    "messages_count": 5
  }
]
```

#### Get Conversation Metadata

**Endpoint:** `GET /api/conversations/{id}`

**Response:**
```json
{
  "id": "uuid-1",
  "created_at": "2025-12-26T10:00:00",
  "title": "Discussion about RAG",
  "messages_count": 5
}
```

#### Get Conversation Messages

**Endpoint:** `GET /api/conversations/{id}/messages`

**Response:**
```json
{
  "messages": [
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "RAG stands for..."}
  ]
}
```

#### Create Conversation

**Endpoint:** `POST /api/conversations/`

**Request:**
```json
{
  "title": "New Discussion"
}
```

**Response:**
```json
{
  "id": "uuid-new",
  "created_at": "2025-12-26T11:00:00",
  "title": "New Discussion"
}
```

#### Rename Conversation

**Endpoint:** `POST /api/conversations/{id}/rename`

**Request:**
```json
{
  "title": "Updated Title"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

#### Delete Conversation

**Endpoint:** `DELETE /api/conversations/{id}`

**Response:**
```json
{
  "status": "ok",
  "message": "Conversation deleted"
}
```

#### Delete All Conversations

**Endpoint:** `DELETE /api/conversations/`

**Response:**
```json
{
  "status": "ok",
  "deleted_count": 10
}
```

---

### Models API

#### List LLM Models

**Endpoint:** `GET /api/models/llm`

**Description:** List locally available GGUF models.

**Response:**
```json
{
  "models": [
    {
      "name": "llama-2-7b.Q4_K_M.gguf",
      "size": 4368066560,
      "path": "/models/llama-2-7b.Q4_K_M.gguf"
    }
  ]
}
```

#### List Embedding Models

**Endpoint:** `GET /api/models/embedding`

**Response:**
```json
{
  "models": [
    {
      "name": "all-MiniLM-L6-v2",
      "cached": true
    }
  ]
}
```

#### Download LLM Model

**Endpoint:** `POST /api/models/llm/download`

**Request:**
```json
{
  "repo": "TheBloke/Llama-2-7B-GGUF",
  "filename": "llama-2-7b.Q4_K_M.gguf"
}
```

**Response:**
```json
{
  "download_id": "uuid-download",
  "status": "started"
}
```

#### Download Embedding Model

**Endpoint:** `POST /api/models/embedding/download`

**Request:**
```json
{
  "model_name": "all-MiniLM-L6-v2"
}
```

**Response:**
```json
{
  "status": "started",
  "model_name": "all-MiniLM-L6-v2"
}
```

#### Get Download Status

**Endpoint:** `GET /api/models/downloads/{download_id}`

**Response:**
```json
{
  "status": "downloading",
  "progress": 45.2,
  "downloaded_bytes": 1975000000,
  "total_bytes": 4368066560
}
```

---

### API Keys API

#### Get API Keys Status

**Endpoint:** `GET /api/api-keys/status`

**Description:** Get configuration status for all services.

**Response:**
```json
{
  "openrouter": {"configured": true},
  "github_token": {"configured": false},
  "openweather_api_key": {"configured": true}
}
```

#### Update API Keys

**Endpoint:** `POST /api/api-keys/`

**Request:**
```json
{
  "openrouter": "sk-or-v1-...",
  "github_token": "ghp_..."
}
```

**Response:**
```json
{
  "status": "ok",
  "updated": ["openrouter", "github_token"]
}
```

#### Delete API Key

**Endpoint:** `DELETE /api/api-keys/{service}`

**Path Parameters:**
- `service` - Service name (e.g., "openrouter", "github_token")

**Response:**
```json
{
  "status": "ok",
  "message": "API key for 'openrouter' deleted"
}
```

---

### Files API

#### Generate File

**Endpoint:** `POST /api/files/generate`

**Request:**
```json
{
  "content": "# Heading\n\nContent here...",
  "format": "pdf",
  "title": "My Document",
  "filename": "my-document"
}
```

**Formats:** `"pdf"`, `"html"`, `"markdown"`

**Response:**
```json
{
  "filename": "my-document.pdf",
  "path": "static/generated/my-document.pdf",
  "url": "http://localhost:8000/static/generated/my-document.pdf"
}
```

#### Download File

**Endpoint:** `GET /api/files/download/{filename}`

**Description:** Download a previously generated file.

**Response:** File stream with appropriate Content-Type

---

### Settings API

#### Get Settings

**Endpoint:** `GET /api/settings`

**Response:**
```json
{
  "llm": {
    "provider_type": "cloud",
    "cloud_provider": "openrouter",
    "model": "x-ai/grok-4.1-fast",
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

#### Update Settings

**Endpoint:** `POST /api/settings`

**Request:**
```json
{
  "llm": {
    "provider_type": "local",
    "base_url": "http://localhost:8080"
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Connectors API

#### List Connectors

**Endpoint:** `GET /api/connectors/`

**Response:**
```json
[
  {
    "name": "github",
    "enabled": true,
    "configured": true,
    "requires_oauth": false
  },
  {
    "name": "gmail",
    "enabled": false,
    "configured": false,
    "requires_oauth": true
  }
]
```

#### Configure Connector

**Endpoint:** `POST /api/connectors/configure`

**Request:**
```json
{
  "name": "github",
  "api_key": "ghp_..."
}
```

#### Toggle Connector

**Endpoint:** `POST /api/connectors/{name}/toggle`

**Request:**
```json
{
  "enabled": true
}
```

---

### Health API

#### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Testing

### Test Suite

**Framework:** pytest with pytest-asyncio and pytest-cov

**Configuration:** `backend/pytest.ini`

**Structure:**
```
tests/
├── unit/                    # Unit tests for services
│   ├── test_llm_service.py
│   ├── test_vector_store.py
│   └── test_conversation_service.py
├── integration/             # API integration tests
│   ├── test_documents_api.py
│   ├── test_chat_api.py
│   └── test_connectors_api.py
└── test_health.py
```

### Running Tests

**All tests:**
```bash
cd backend
pytest
```

**With coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Specific test:**
```bash
pytest tests/unit/test_llm_service.py::TestLLMService::test_generate_stream
```

**By marker:**
```bash
pytest -m unit     # Only unit tests
pytest -m integration  # Only integration tests
```

### Writing Tests

**Unit Test Example:**

```python
import pytest
from services.llm_service import LLMService

@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_basic():
    service = LLMService()
    response = await service.generate(
        prompt="Test prompt",
        messages=[],
        use_documents=False
    )
    assert isinstance(response, str)
    assert len(response) > 0
```

**Integration Test Example:**

```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.integration
def test_upload_document():
    with open("test.txt", "rb") as f:
        response = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### Common Issues

**Missing dependencies:**
```bash
pip install pytest pytest-asyncio pytest-cov
```

**Async tests failing:**
- Ensure `pytest-asyncio` is installed
- Mark async tests with `@pytest.mark.asyncio`

**External dependencies:**
- Mock external services in unit tests
- Use `unittest.mock` or `pytest-mock`

---

## Recent Fixes & Implementations

### PDF Generation & Download Fixes

**Problem:** 404 errors on file generation, downloads failing

**Root Causes:**
- Router prefix duplication (`/api/files/files`)
- Relative URLs not working in Docker
- Missing dependencies

**Fixes:**
1. **Router Prefix:** Corrected in `backend/routers/files.py:8`
2. **Absolute URLs:** Implemented in FileService:
   - Markdown: `backend/services/file_service.py:47`
   - HTML: `backend/services/file_service.py:63`
   - PDF: `backend/services/file_service.py:111`
3. **Dependencies:** Added `pypdf` and `python-docx` to requirements.txt

**Why Absolute URLs?**
- Vite dev proxy only covers `/api`, not `/static`
- Docker networking requires full URLs
- Consistent behavior across environments

### LLM Service Reliability

**Problem:** Provider detection inconsistencies

**Fixes:**
1. **Provider Type:** Respects env `llm_provider` (`backend/services/llm_service.py:18`)
2. **Cloud Provider:** Returns `None` when env is local (`backend/services/llm_service.py:27`)
3. **Base URL:** Prefers env local base when `llm_provider=local` (`backend/services/llm_service.py:78`)
4. **Model Selection:** Uses env `openrouter_model` when OpenRouter selected (`backend/services/llm_service.py:92`)
5. **Streaming Fix:** Added `return` after cloud stream to prevent local fallback (`backend/services/llm_service.py:248`)

### Testing Improvements

**Enhancements:**
- Installed `pytest`, `pytest-asyncio`, `pytest-cov`
- Fixed JSON serialization of Mock responses
- Resolved provider selection mismatches
- **Status:** 86 passed, 2 skipped

### Developer Notes

**Static Files:**
- Mounted at `/static` in app.py
- Absolute URLs prevent proxy issues
- Essential for Docker deployments

**Configuration:**
- ConfigService merges settings.json with env
- Env variables always take precedence
- Tests should mock `get_settings()` for reproducibility

---

## Useful Commands

### Backend

```bash
# Start dev server
uvicorn app:app --reload

# Run tests with coverage
pytest --cov=. --cov-report=html

# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

### Frontend

```bash
# Start dev server
VITE_API_URL=http://localhost:8000 npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Format
npm run format
```

### Docker

```bash
# Build and run locally
cd docker && docker compose up --build

# View logs
docker compose logs -f backend

# Rebuild specific service
docker compose build backend
```

---

## Additional Resources

- [Architecture Guide](ARCHITECTURE.md) - System design and patterns
- [Configuration Guide](CONFIGURATION.md) - Environment variables and settings
- [Contributing Guide](CONTRIBUTING.md) - Contribution workflow
- [Usage Guide](USAGE_GUIDE.md) - End-user documentation

---

This developer guide is maintained by the AI Knowledge Console team. For questions or improvements, please open an issue or pull request.
