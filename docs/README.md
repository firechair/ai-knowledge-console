# AI Knowledge Console Documentation

Welcome to the AI Knowledge Console documentation! This directory contains comprehensive guides for users, developers, and contributors.

## Quick Links

### For Users

- 📖 **[Configuration Guide](CONFIGURATION.md)** - Complete reference for environment variables and settings
- 🎯 **[Usage Guide](USAGE_GUIDE.md)** - Practical examples and workflows for common use cases
- 🔐 **[OAuth Setup Guide](oauth_setup.md)** - Step-by-step instructions for Gmail, Drive, Slack, and Notion integration

### For Developers

- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - System design, technical decisions, and design patterns
- 💻 **[Developer Guide](DEVELOPER_GUIDE.md)** - API reference, development setup, and implementation guides
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute code, documentation, and bug reports

---

## Documentation Structure

```
docs/
├── README.md                  # This file - documentation hub
├── ARCHITECTURE.md            # System architecture and design decisions
├── CONFIGURATION.md           # Complete configuration reference
├── DEVELOPER_GUIDE.md         # Developer setup and complete API reference
├── CONTRIBUTING.md            # Contribution guidelines and workflows
├── oauth_setup.md             # OAuth integration setup guide
├── USAGE_GUIDE.md            # Usage examples and practical workflows
└── media/                     # Screenshots, demo videos, and assets
```

---

## Getting Started

### New Users

1. **Installation:** See main [README.md](../README.md) for quick start instructions
2. **Configuration:** Read [CONFIGURATION.md](CONFIGURATION.md) to customize your setup
3. **Usage:** Explore [USAGE_GUIDE.md](USAGE_GUIDE.md) for practical examples

### New Developers

1. **Architecture:** Understand the system design in [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Setup:** Follow development setup in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#getting-started)
3. **API:** Browse the complete API reference in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#api-reference)
4. **Contributing:** Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes

---

## Documentation by Topic

### Installation & Setup

- [Quick Start](../README.md#quick-start-works-immediately) - Get running in 5 minutes
- [LLM Setup Guide](../README.md#llm-setup-guide) - Configure local or cloud LLM
- [Docker Setup](../README.md#quickstart-docker-macos-windows) - Docker Compose installation
- [Local Development](../README.md#local-development-without-docker) - Run without Docker

### Configuration

- [Environment Variables](CONFIGURATION.md) - All `.env` options explained
- [Settings.json](CONFIGURATION.md#settings-management-new-in-v20) - UI-driven configuration
- [LLM Providers](CONFIGURATION.md) - Configure local, OpenRouter, OpenAI, or custom
- [OAuth Credentials](oauth_setup.md) - Set up Gmail, Drive, Slack, Notion

### Features & Usage

- [Core RAG Features](USAGE_GUIDE.md) - Document upload, chat, context control
- [Model Management](USAGE_GUIDE.md#model-management-workflows) - Download and manage models
- [External Tools](USAGE_GUIDE.md) - Crypto, Weather, GitHub, Hacker News
- [File Generation](USAGE_GUIDE.md#exporting-conversations) - Export as PDF, Markdown, HTML

### Architecture & Design

- [System Overview](ARCHITECTURE.md#overview) - High-level architecture
- [Backend Architecture](ARCHITECTURE.md#backend-architecture) - FastAPI, services, routers
- [Frontend Architecture](ARCHITECTURE.md#frontend-architecture) - React component structure
- [Data Flow](ARCHITECTURE.md#configuration--data-flow) - RAG pipeline, configuration precedence
- [Docker Optimization](ARCHITECTURE.md#docker-optimization) - CPU-first strategy, GPU enablement

### Development

- [Development Setup](DEVELOPER_GUIDE.md#getting-started) - Backend and frontend setup
- [API Reference](DEVELOPER_GUIDE.md#api-reference) - Complete endpoint documentation
- [Adding Features](DEVELOPER_GUIDE.md#adding-new-features) - Create routers and services
- [Testing](DEVELOPER_GUIDE.md#testing) - Running and writing tests
- [Code Standards](CONTRIBUTING.md#code-standards) - Python and JavaScript style guides

### Deployment

- [Docker Deployment](../README.md#quickstart-docker-macos-windows) - Docker Compose setup
- [GHCR Images](../README.md#deploy-from-ghcr) - Pre-built container images
- [Traefik TLS](../README.md#tls-with-traefik) - HTTPS with Let's Encrypt
- [Single-VM Deployment](../README.md#single-vm-deployment) - Systemd service setup

---

## Key Concepts

### RAG (Retrieval-Augmented Generation)

The AI Knowledge Console implements a complete RAG pipeline:

1. **Document Upload:** Users upload PDF, DOCX, or TXT files
2. **Chunking:** Documents split into manageable chunks
3. **Embedding:** Text chunks converted to vector embeddings
4. **Storage:** Embeddings stored in ChromaDB vector database
5. **Retrieval:** User queries matched against stored embeddings
6. **Augmentation:** Relevant chunks provided as context to LLM
7. **Generation:** LLM generates answer based on retrieved context

**Learn More:** [Architecture - RAG Pipeline](ARCHITECTURE.md#rag-pipeline)

### Multi-Provider LLM Support

Switch between providers without code changes:

- **Local:** llama.cpp (private, no API costs)
- **OpenRouter:** 200+ models via unified API
- **OpenAI:** Direct GPT-4, GPT-3.5 access
- **Custom:** Any OpenAI-compatible endpoint

**Learn More:** [Configuration - LLM Providers](CONFIGURATION.md), [Architecture - LLMService](ARCHITECTURE.md#llmservice-backendservicesllm_servicepy)

### Granular Context Control

Select specific documents for RAG retrieval:

- Filter by filename (e.g., only use CV.pdf)
- Combine multiple documents
- Or use all uploaded documents

**Learn More:** [Usage Guide](USAGE_GUIDE.md)

### Settings Management

Configure the app via UI or environment variables:

- **settings.json:** UI-driven configuration
- **.env:** Environment variables (takes precedence)
- **ConfigService:** Automatically merges both

**Learn More:** [Configuration - Settings Management](CONFIGURATION.md#settings-management-new-in-v20)

---

## Common Tasks

### For Users

**Upload and Chat with Documents:**
1. See [Usage Guide - Basic Document Chat](USAGE_GUIDE.md)

**Configure Cloud LLM Provider:**
1. See [Usage Guide - Switching LLM Providers](USAGE_GUIDE.md#switching-llm-providers)

**Set Up OAuth Integrations:**
1. See [OAuth Setup Guide](oauth_setup.md)

**Export Conversations:**
1. See [Usage Guide - Exporting Conversations](USAGE_GUIDE.md#exporting-conversations)

### For Developers

**Set Up Development Environment:**
1. See [Developer Guide - Getting Started](DEVELOPER_GUIDE.md#getting-started)

**Add a New API Endpoint:**
1. See [Developer Guide - Creating a New Router](DEVELOPER_GUIDE.md#creating-a-new-router)

**Add a New Service:**
1. See [Developer Guide - Implementing a Service](DEVELOPER_GUIDE.md#implementing-a-service)

**Run Tests:**
1. See [Developer Guide - Testing](DEVELOPER_GUIDE.md#testing)

**Submit a Pull Request:**
1. See [Contributing Guide - Development Workflow](CONTRIBUTING.md#development-workflow)

---

## Troubleshooting

### Common Issues

**Backend not responding:**
- Check `curl http://localhost:8000/health`
- Verify LLM server is running (if using local)
- Check logs: `docker compose logs -f backend`

**Frontend can't reach backend:**
- Ensure `VITE_API_URL` is set correctly
- Check CORS configuration in `.env`
- Verify backend is accessible at configured URL

**Document upload fails:**
- Check file format (PDF, DOCX, TXT only)
- Verify file size under limit (see `max_upload_mb` in config)
- Check backend logs for errors

**OAuth redirect issues:**
- Ensure `APP_BASE_URL` and `FRONTEND_BASE_URL` match actual URLs
- Check OAuth app settings in provider console
- Verify redirect URIs are correctly configured

**For More Help:**
- [Main README - Troubleshooting](../README.md#troubleshooting)
- [GitHub Issues](https://github.com/firechair/ai-knowledge-console/issues)
- [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Read [CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines
2. **Check [Issues](https://github.com/firechair/ai-knowledge-console/issues)** for tasks
3. **Join [Discussions](https://github.com/firechair/ai-knowledge-console/discussions)** for questions

**Ways to Contribute:**
- Fix bugs or implement features
- Improve documentation
- Write tests
- Help other users

---

## Additional Resources

### External Links

- **GitHub Repository:** [github.com/firechair/ai-knowledge-console](https://github.com/firechair/ai-knowledge-console)
- **Docker Images:** [GHCR Package](https://github.com/firechair/ai-knowledge-console/pkgs/container/ai-knowledge-console)
- **Issue Tracker:** [GitHub Issues](https://github.com/firechair/ai-knowledge-console/issues)
- **Discussions:** [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)

### Related Technologies

- **FastAPI:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **React:** [react.dev](https://react.dev/)
- **ChromaDB:** [docs.trychroma.com](https://docs.trychroma.com/)
- **llama.cpp:** [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)
- **OpenRouter:** [openrouter.ai](https://openrouter.ai/)

---

## Questions?

- 📚 **Check the documentation first** (you're in the right place!)
- 🔍 **Search [existing issues](https://github.com/firechair/ai-knowledge-console/issues)** for similar questions
- 💬 **Ask in [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)** for general questions
- 🐛 **Report bugs** via [Issues](https://github.com/firechair/ai-knowledge-console/issues/new) with details

---

## Document Changelog

- **2025-12-26:** Created comprehensive documentation hub (v2.0)
- Previous documentation was scattered across root and backend/docs/

---

This documentation is maintained by the AI Knowledge Console team. Contributions and improvements are welcome via pull requests!
