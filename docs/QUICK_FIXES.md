# Quick Fixes for Critical Issues

This document provides immediate fixes for the critical issues identified in the code review.

## 🔴 Fix 1: Update .env.example

**File:** `backend/.env.example`

Replace the entire file with this corrected version:

```env
# ===============================================
# AI Knowledge Console - Environment Configuration
# ===============================================

# LLM Provider Configuration
# Options: "local" (llama.cpp) or "openrouter"
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080

# Vector Database
CHROMA_PERSIST_DIR=../vectorstore/chroma

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ===============================================
# Optional: External API Tools
# ===============================================
GITHUB_TOKEN=
OPENWEATHER_API_KEY=

# ===============================================
# Optional: OAuth Integration URLs
# Required for Gmail, Drive, Slack, Notion
# ===============================================
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173

# ===============================================
# Optional: OAuth Client Credentials
# ===============================================
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
NOTION_CLIENT_ID=
NOTION_CLIENT_SECRET=

# ===============================================
# Optional: OpenRouter Configuration
# Use instead of local LLM for hosted inference
# ===============================================
OPENROUTER_API_KEY=
OPENROUTER_MODEL=x-ai/grok-4.1-fast
OPENROUTER_MAX_TOKENS=1024
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_TOP_P=0.9
OPENROUTER_FREQUENCY_PENALTY=0.2
OPENROUTER_PRESENCE_PENALTY=0.0
OPENROUTER_REPETITION_PENALTY=1.1

# ===============================================
# Optional: Application Settings
# ===============================================
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_UPLOAD_MB=25

# Optional: Rate Limiting
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SEC=60

# Optional: Database Path
CONVERSATIONS_DB_PATH=backend/conversations.db
```

**Changes made:**
- ✅ Removed duplicate `LLM_PROVIDER` entry
- ✅ Added `FRONTEND_BASE_URL`
- ✅ Added all OpenRouter configuration options
- ✅ Added `CONVERSATIONS_DB_PATH`
- ✅ Added `ALLOWED_ORIGINS`, `MAX_UPLOAD_MB`, rate limiting
- ✅ Added clear section comments

---

## 🔴 Fix 2: Update README LLM Options

**File:** `README.md`

**Remove Section (Lines 121-142):** The "Option 2: OpenAI API" section.

**Replace with:**

```markdown
### Option 2: OpenRouter API (Hosted Models)

**Pros**: No local resources needed, access to multiple models, configurable  
**Cons**: Requires API key and internet connection, small cost per request

1. **Get an API key** from [OpenRouter](https://openrouter.ai/keys)

2. **Configure the backend** (`backend/.env`):
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENROUTER_MODEL=x-ai/grok-4.1-fast
   ```

3. **Choose your model**:
   - `x-ai/grok-4.1-fast` - Fast responses, good quality
   - `anthropic/claude-3.5-sonnet` - Excellent reasoning
   - `openai/gpt-4-turbo` - Best general purpose
   - See [OpenRouter Models](https://openrouter.ai/models) for full list

4. **Optional: Fine-tune generation** (in `.env`):
   ```env
   OPENROUTER_TEMPERATURE=0.7      # 0.0-2.0, higher = more creative
   OPENROUTER_MAX_TOKENS=1024      # Max response length
   OPENROUTER_FREQUENCY_PENALTY=0.2 # Reduce repetition
   ```

**How it works:** Backend streams from OpenRouter's SSE endpoint and forwards to frontend WebSocket.

**Note:** If you want to use OpenAI directly, use OpenRouter with model `openai/gpt-4-turbo` - it's the same API under the hood.
```

**Then rename "Option 3: Ollama" to "Option 3"** and **"Option 4: OpenRouter" should be removed** since we moved it to Option 2.

---

## 🔴 Fix 3: Update CHANGELOG

**File:** `CHANGELOG.md`

Add this entry to the top:

```markdown
## 2025-12-01 (Latest)

### Features
- **OpenRouter Integration**
  - Added OpenRouter as LLM provider alternative to local llama.cpp
  - Streaming via Server-Sent Events (SSE) forwarded to WebSocket
  - Configurable generation parameters: temperature, top_p, penalties, max_tokens
  - Support for multiple models via single API key

### Improvements
- Conversations Management
  - Backend: added router with list/get/messages/create/rename/delete/bulk delete endpoints
  - Frontend: Conversations tab with list, open, rename, delete, and Delete All
  - DB: `title` column added with safe migration
- Chat Persistence
  - Hydrate state from `localStorage` using lazy initializers
  - Chat can load selected conversation messages from backend
- External Data Prompting
  - System prompt updated to use provided tool data effectively
- Startup Responsiveness
  - Vector store lazily loads the embedding model on first use

### Bug Fixes
- Fixed missing React `useState` import in Conversations
- Fixed preview truncation string in conversations service
- Dev WebSocket stability: cleanup guards only close `OPEN` sockets

### Configuration
- Enhanced `.env.example` with all available options
- Added `FRONTEND_BASE_URL` for OAuth redirects
- Added all OpenRouter configuration parameters
```

---

## 🟡 Fix 4: Make Database Path Configurable

**File:** `backend/services/conversation_service.py`

**Change line 11 from:**
```python
def __init__(self, db_path: str = "backend/conversations.db"):
```

**To:**
```python
def __init__(self, db_path: str = None):
    import os
    if db_path is None:
        db_path = os.getenv("CONVERSATIONS_DB_PATH", "backend/conversations.db")
```

**Then add to imports at top:**
```python
import os
```

---

## 🟡 Fix 5: Add Configuration Documentation

**Create new file:** `docs/CONFIGURATION.md`

```markdown
# Configuration Reference

## LLM Provider Settings

### Local (llama.cpp)
```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080
```

### OpenRouter
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=x-ai/grok-4.1-fast
```

#### OpenRouter Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `OPENROUTER_TEMPERATURE` | 0.7 | 0.0 - 2.0 | Controls randomness. 0 = deterministic, 2 = very creative |
| `OPENROUTER_MAX_TOKENS` | 1024 | 1 - 4096+ | Maximum response length |
| `OPENROUTER_TOP_P` | 0.9 | 0.0 - 1.0 | Nucleus sampling threshold |
| `OPENROUTER_FREQUENCY_PENALTY` | 0.2 | 0.0 - 2.0 | Reduces word repetition |
| `OPENROUTER_PRESENCE_PENALTY` | 0.0 | 0.0 - 2.0 | Encourages new topics |
| `OPENROUTER_REPETITION_PENALTY` | 1.1 | 1.0 - 2.0 | Model-specific repetition control |

**Recommendations:**
- **Creative writing:** `temperature=1.2, top_p=0.95`
- **Factual/technical:** `temperature=0.3, top_p=0.8`
- **Balanced:** `temperature=0.7, top_p=0.9` (default)

## Database Settings

```env
# SQLite database for conversations
CONVERSATIONS_DB_PATH=backend/conversations.db

# ChromaDB vector store location
CHROMA_PERSIST_DIR=../vectorstore/chroma
```

**Production tip:** Use absolute paths for clarity:
```env
CONVERSATIONS_DB_PATH=/app/data/conversations.db
CHROMA_PERSIST_DIR=/app/data/vectorstore/chroma
```

## Security & Performance

```env
# CORS - comma-separated allowed origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Upload limits (MB)
MAX_UPLOAD_MB=25

# Rate limiting (protect from abuse)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100     # requests per window
RATE_LIMIT_WINDOW_SEC=60    # window duration
```

## OAuth Settings

Required for Gmail, Drive, Slack, Notion integrations:

```env
APP_BASE_URL=http://localhost:8000           # Backend URL for OAuth callbacks
FRONTEND_BASE_URL=http://localhost:5173       # Where to redirect after auth

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
NOTION_CLIENT_ID=...
NOTION_CLIENT_SECRET=...
```

**Production deployment:**
```env
APP_BASE_URL=https://api.yourdomain.com
FRONTEND_BASE_URL=https://yourdomain.com
```

See [OAuth Setup Guide](OAUTH_SETUP.md) for obtaining credentials.
```

---

## ✅ Verification Checklist

After applying fixes, verify:

- [ ] `backend/.env.example` has no duplicate keys
- [ ] `backend/.env.example` includes `FRONTEND_BASE_URL`
- [ ] README no longer mentions unimplemented OpenAI client
- [ ] README Section numbering is correct (Option 1, 2, 3, not 1,2,3,4)
- [ ] CHANGELOG mentions OpenRouter support
- [ ] `conversation_service.py` uses environment variable for DB path
- [ ] New `docs/CONFIGURATION.md` created

## 🚀 Apply All Fixes

```bash
# From project root
cd /Users/mangaproject/Documents/CV/ai-knowledge-console

# Backup current files
cp backend/.env.example backend/.env.example.backup
cp README.md README.md.backup
cp CHANGELOG.md CHANGELOG.md.backup

# Apply fixes (manual editing required, or use the review document as reference)
```

---

**Last Updated:** December 1, 2025
