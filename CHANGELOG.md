# Changelog

All notable changes to AI Knowledge Console are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-12-26

### Added

**Settings & Configuration**
- Unified settings interface with tabbed organization (LLM Config, API Keys, Model Management)
- ConfigService for settings.json management with automatic migration
- ProviderRegistry for cloud provider definitions (OpenRouter, OpenAI, Custom)
- Visual provider configuration with model selection dropdowns
- API key manager with status indicators and validation

**Model Management**
- ModelManager service for downloading and managing models
- Download GGUF models from HuggingFace directly in UI
- Manage embedding models with cache tracking
- Model download progress tracking with status endpoints
- Background download tasks

**File Generation**
- FileService for multi-format exports (PDF, Markdown, HTML)
- Generate downloadable documents from LLM responses
- Absolute URL generation for Docker compatibility
- Static file serving at `/static/generated/`
- Direct download from chat interface

**Frontend Enhancements**
- Modular component structure: layout/, settings/, ui/, pages/, hooks/
- Settings components: CloudProviderSelector, APIKeysManager, ModelManager
- LLM provider configuration panels (Local, OpenRouter, OpenAI, Custom)
- Enhanced settings page with visual feedback

**API Enhancements**
- New routers: api_keys.py, models.py, files.py
- Model management endpoints (list, download, status)
- API key CRUD endpoints with service-specific operations
- File generation and download endpoints

### Changed
- Component organization: Migrated to organized directory structure
- Settings UI: Unified panel replacing scattered configuration
- Documentation: Consolidated backend/docs/ into root docs/
- Frontend structure: Separated concerns into layout, settings, ui, pages

### Fixed
- PDF generation 404 errors with absolute URL generation
- LLM provider detection in ConfigService
- Streaming reliability for cloud providers (OpenRouter)
- WebSocket lifecycle in development mode (React Strict Mode)
- File download paths in Docker environments

### Documentation
- Created comprehensive DEVELOPER_GUIDE.md with complete API reference
- Created CONTRIBUTING.md with contribution guidelines
- Consolidated ARCHITECTURE.md merging backend and root docs
- Created docs/README.md as documentation hub
- Enhanced CHANGELOG.md with detailed version history
- Updated README.md showcasing new features

## [1.0.0] - 2025-12-01

### Added

**OpenRouter Integration**
- OpenRouter as LLM provider alternative to local llama.cpp
- Streaming via Server-Sent Events (SSE) forwarded to WebSocket
- Configurable generation parameters (temperature, top_p, penalties, max_tokens)
- Support for 200+ models via single API key (GPT-4, Claude, Gemini, Llama, etc.)
- Complete implementation in llm_service.py with streaming and non-streaming modes

**Conversations Management**
- Backend router with full CRUD operations
- List, create, rename, delete conversations
- Bulk delete all conversations
- SQLite storage with title column and safe migration
- Message history retrieval

**Frontend Enhancements**
- Conversations tab with list view
- Open conversation to hydrate chat history
- Rename conversations inline
- Delete and Delete All operations
- Responsive UI optimized for desktop and mobile

### Improved
- Chat Persistence: LocalStorage hydration with lazy initializers
- External Data Prompting: Better system prompts for tool data (GitHub, Hacker News, etc.)
- Startup Performance: Lazy vector store initialization (embedding model loads on first use)
- WebSocket Stability: Cleanup guards only closing OPEN sockets in dev mode

### Fixed
- Missing React `useState` import in Conversations component
- Preview truncation in conversations service
- WebSocket double-mount issues in React Strict Mode

## [0.9.0] - 2025-11-30

### Added
- Initial RAG pipeline (documents → vectorstore → retrieval → LLM)
- Document upload with PDF, DOCX, TXT support
- ChromaDB persistent vector store with sentence-transformers
- LLM integration via llama.cpp (OpenAI-compatible API)
- Basic chat interface with streaming responses
- Docker containerization with multi-stage builds
- Nginx reverse proxy for frontend and backend
- FastAPI backend with modular router structure
- React + Vite frontend with Tailwind CSS
- GitHub Actions CI/CD pipeline
- Initial architecture and documentation

---

## Version History Summary

- **2.0.0** (2025-12-26): Settings management, model downloads, file exports, enhanced architecture
- **1.0.0** (2025-12-01): OpenRouter integration, conversations management, improved UX
- **0.9.0** (2025-11-30): Initial release with core RAG functionality

---

## Migration Notes

### Migrating from 1.x to 2.0

**Settings Configuration:**
- Old `.env`-only configuration still works
- New `settings.json` provides UI-driven configuration
- ConfigService automatically merges both sources
- Priority: `.env` overrides `settings.json` overrides defaults

**Component Structure:**
- If extending frontend, note new component locations:
  - Old: `src/components/Chat.jsx`
  - New: `src/pages/ChatPage.jsx`
- Import paths updated for layout, settings, ui components

**API Changes:**
- All existing endpoints remain backwards compatible
- New endpoints added: `/api/models/*`, `/api/api-keys/*`, `/api/files/*`
- No breaking changes to existing routes

**Dependencies:**
- Added: `pypdf`, `python-docx` for file generation
- Frontend: New dependencies for Radix UI components

**What You Need to Do:**
1. Pull latest changes: `git pull origin main`
2. Update dependencies:
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt

   # Frontend
   cd frontend && npm install
   ```
3. (Optional) Configure settings via new Settings UI
4. Review new features in [README.md](README.md#whats-new-v20---december-2025)

### Migrating from 0.9.x to 1.0

**Database Migration:**
- Conversations.db schema automatically updated (title column added)
- No manual migration required

**Configuration:**
- New `LLM_PROVIDER` option: `openrouter`
- Add `OPENROUTER_API_KEY` for cloud LLM access
- Optional: Configure generation parameters in `.env`

**What You Need to Do:**
1. Update dependencies (see above)
2. (Optional) Add OpenRouter API key to `.env`
3. Review OpenRouter configuration in [README.md](README.md#option-2-openrouter-api-hosted-models)

---

## Breaking Changes

### v2.0.0
- **None**: All changes are backwards compatible
- Removed components have equivalent replacements in new structure
- Deprecated: Old flat component structure (still works but reorganized)

### v1.0.0
- **None**: All changes are additive

### v0.9.0
- Initial release (no breaking changes)

---

## Deprecation Notices

### v2.0.0
- **Component Imports**: Old direct component imports deprecated in favor of new structure
  - Deprecated: `import Chat from './components/Chat'`
  - New: `import { ChatPage } from './pages/ChatPage'`
  - Old imports still work but will be removed in v3.0.0

---

## Security

### v2.0.0
- API key storage via settings.json (ensure .gitignore is up to date)
- Recommend using environment variables in production

### v1.0.0
- OAuth token storage in-memory (production should use persistent storage)

### v0.9.0
- Basic CORS configuration
- Rate limiting support (disabled by default)

For security vulnerabilities, please report privately to the maintainers.

---

## Links

- [GitHub Repository](https://github.com/firechair/ai-knowledge-console)
- [Documentation](docs/README.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Issue Tracker](https://github.com/firechair/ai-knowledge-console/issues)

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles. Each version is tagged in git for easy reference.
