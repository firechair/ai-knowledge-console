# Troubleshooting Guide

This guide consolidates all troubleshooting information for the AI Knowledge Console. Find solutions to common issues organized by category.

## Table of Contents

- [Setup & Installation Issues](#setup--installation-issues)
- [Configuration Issues](#configuration-issues)
- [OAuth & External API Issues](#oauth--external-api-issues)
- [Runtime Issues](#runtime-issues)
- [Document & RAG Issues](#document--rag-issues)
- [Getting Additional Help](#getting-additional-help)

---

## Setup & Installation Issues

### Docker daemon not running

**Symptoms**: Docker commands fail, containers won't start

**Solution**:
- **macOS/Windows**: Start Docker Desktop application
- **Linux**: Ensure Docker Engine service is active: `sudo systemctl start docker`

### Backend not responding

**Symptoms**: Frontend shows infinite spinner, API requests timeout

**Check**:
1. Verify backend health endpoint:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. Check backend logs:
   ```bash
   docker compose logs -f backend
   ```

3. Verify LLM server is running (if using local provider):
   ```bash
   curl http://localhost:8080/health
   ```

**Common Causes**:
- First-time embedding model load is lazy - allow time for download/initialization on first document add/search
- Missing dependencies: Ensure `sentence-transformers` and `chromadb` are installed (if running locally)
- CORS misconfiguration: Verify `allowed_origins` in `.env` includes your frontend URL (e.g., `http://localhost:5173`)

### Frontend can't reach backend

**Symptoms**: API calls fail, network errors in browser console

**Check**:
1. Ensure `VITE_API_URL` is set correctly in frontend environment
2. Verify CORS configuration in backend `.env` file
3. Confirm backend is accessible at configured URL:
   ```bash
   curl http://localhost:8000/health
   ```

### Linux LLM connectivity issues

**Symptoms**: Backend can't connect to local LLM server on host

**Solution**:
- Use `host-gateway` mapping (already configured in docker-compose.yml)
- Confirm host LLM server is listening on all interfaces: `--host 0.0.0.0`
- Check LLM server is on port 8080 (or update `LLM_BASE_URL` in `.env`)

---

## Configuration Issues

### LLM not responding

**Symptoms**: Chat messages timeout, no responses generated

**Check**:

1. **Verify provider setting**:
   - Ensure `LLM_PROVIDER` matches your setup (`local`, `openrouter`, `openai`, or `custom`)

2. **For local provider**:
   - Confirm llama.cpp server is running and accessible
   - Check server URL: `curl http://localhost:8080/health`
   - Verify model is loaded (check llama.cpp logs)

3. **For OpenRouter provider**:
   - Verify API key is valid: `OPENROUTER_API_KEY` in `.env`
   - Check account has credits: [OpenRouter dashboard](https://openrouter.ai/)
   - Review backend logs for authentication errors

4. **For OpenAI provider**:
   - Verify API key is valid: `OPENAI_API_KEY` in `.env`
   - Check account status and billing
   - Review backend logs for rate limit errors

5. **Backend logs**:
   ```bash
   docker compose logs -f backend | grep -i error
   ```

### Environment variables not taking effect

**Symptoms**: Changes to `.env` file don't apply

**Solution**:
1. Restart backend after changing `.env` file:
   ```bash
   docker compose restart backend
   ```

2. For Docker deployments, rebuild if variables are build-time:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

3. Verify variable is loaded - check backend logs on startup

### Settings.json vs .env conflicts

**Symptoms**: Configuration behaves unexpectedly

**Important**: Environment variables in `.env` take precedence over `settings.json`

**Solution**:
- If a variable is set in `.env`, it will override the same setting in `settings.json`
- To use UI-driven settings, ensure the variable is NOT set in `.env`
- Check `ConfigService` logs to see which source is used for each setting

---

## OAuth & External API Issues

### OAuth redirect URI mismatch

**Symptoms**: Error message "Redirect URI mismatch" during OAuth flow

**Solution**:
1. Ensure `APP_BASE_URL` in `.env` matches OAuth app callback URL exactly
2. Check for trailing slashes - must match exactly (include or exclude consistently)
3. Verify HTTP vs HTTPS matches exactly
4. Update redirect URI in provider console:
   - Gmail/Drive: `https://console.cloud.google.com/apis/credentials`
   - Slack: `https://api.slack.com/apps`
   - Notion: `https://www.notion.so/my-integrations`

### Invalid client error

**Symptoms**: OAuth flow shows "Invalid client" or "Client authentication failed"

**Solution**:
1. Double-check `CLIENT_ID` in `.env` matches OAuth app ID exactly
2. Double-check `CLIENT_SECRET` in `.env` matches OAuth app secret exactly
3. Ensure no extra spaces or quotes in `.env` values
4. Restart backend after updating credentials

### OAuth access denied

**Symptoms**: User sees "Access denied" during OAuth authorization

**Causes**:
- User clicked "Deny" or "Cancel" during permission request
- OAuth app lacks required scopes

**Solution**:
- User needs to re-initiate authorization flow
- Check OAuth app scopes in provider console match required permissions
- See [OAUTH_SETUP.md](OAUTH_SETUP.md) for required scopes per provider

### OAuth redirect returns JSON or doesn't return to UI

**Symptoms**: After OAuth authorization, browser shows JSON response instead of redirecting to frontend

**Solution**:
1. Ensure frontend was launched with `VITE_API_URL` pointing to backend:
   ```bash
   VITE_API_URL=http://localhost:8000 npm run dev
   ```

2. Verify `FRONTEND_BASE_URL` in `.env` is set correctly and accessible from browser

3. Check that OAuth state includes `return_url` parameter

4. Backend callbacks should redirect to `FRONTEND_BASE_URL` after token exchange

### External tools not returning data

**Symptoms**: Tools appear in UI but don't return results

**Checklist**:
1. Is the tool enabled in Connectors tab?
2. Is the API key configured (for tools that require it)?
3. Are parameters set correctly in Sidebar?
4. For OAuth tools: Is authorization status "Authorized"?
5. Check backend logs for API errors:
   ```bash
   docker compose logs -f backend | grep -i "tool\|connector"
   ```

### Tokens not working after configuration

**Symptoms**: OAuth tokens appear expired or invalid immediately after setup

**Solution**:
- Restart backend after changing `.env` to reload OAuth settings:
  ```bash
  docker compose restart backend
  ```

---

## Runtime Issues

### Data persistence problems

#### Documents missing after restart

**Check**:
1. `CHROMA_PERSIST_DIR` path exists and is writable
2. In Docker: volume is mounted correctly in `docker-compose.yml`
3. Disk space is available: `df -h`

**Solution**:
```bash
# Check ChromaDB directory
ls -la backend/chromadb

# Verify Docker volume
docker volume inspect ai-knowledge-console_chromadb-data
```

#### Conversations missing after restart

**Check**:
1. `CONVERSATIONS_DB_PATH` directory exists
2. File `backend/conversations.db` has write permissions
3. SQLite is installed (should be built-in to Python)

**Solution**:
```bash
# Check database file
ls -la backend/conversations.db

# Test SQLite
sqlite3 backend/conversations.db ".tables"
```

### WebSocket streaming issues

#### WebSocket closed warnings in development

**Symptoms**: Console shows "WebSocket closed" logs during development

**Explanation**: This is normal in React Strict Mode (dev mode) due to double-invocation of effects

**Solution**: No action needed - this is expected behavior in development

#### Repetitive or stuttering responses

**Symptoms**: Output like `HiHi!! How How can can I I help help...`

**Cause**: Streaming deltas can duplicate initial tokens; some models stutter without penalties

**Solutions**:
1. **Client-side normalization**: Already implemented to collapse duplicate words/punctuation
2. **Tune LLM parameters** (for OpenRouter/OpenAI) in backend `.env`:
   - `OPENROUTER_FREQUENCY_PENALTY` (0.0-2.0, default 0.0)
   - `OPENROUTER_PRESENCE_PENALTY` (0.0-2.0, default 0.0)
   - `OPENROUTER_REPETITION_PENALTY` (0.0-2.0, default 1.0)
   - `OPENROUTER_TEMPERATURE` (0.0-2.0, default 0.7)
   - `OPENROUTER_TOP_P` (0.0-1.0, default 1.0)

---

## Document & RAG Issues

### Document upload fails

**Symptoms**: Upload button doesn't work, files rejected, errors in UI

**Check**:
1. **File format**: Only PDF, DOCX, TXT are supported
2. **File size**: Check backend logs for size limit (see `max_upload_mb` in config)
3. **Backend errors**: Check logs for processing errors:
   ```bash
   docker compose logs -f backend | grep -i upload
   ```

**Common Causes**:
- Corrupted PDF files
- Password-protected documents
- Documents with unsupported encodings

### Can't find information that's definitely in documents

**Symptoms**: RAG doesn't retrieve information you know is in uploaded documents

**Possible Causes**:
1. Document wasn't fully indexed (check Documents page)
2. Query doesn't match vocabulary used in document
3. Chunk size too small - information split across multiple chunks
4. Embedding model doesn't capture semantic similarity well

**Solutions**:
1. **Verify document is indexed**:
   - Go to Documents page
   - Check document shows "Ready" status
   - View chunk count

2. **Rephrase query**:
   - Use exact terms from document
   - Try more specific queries with page numbers or section names
   - Ask: "What topics are covered in my documents?"

3. **Adjust RAG settings** (in backend configuration):
   - Increase `TOP_K` for more retrieved chunks
   - Adjust chunk size/overlap if repeatedly problematic

### Answers are generic and don't use documents

**Symptoms**: LLM provides general knowledge answers instead of using uploaded documents

**Diagnosis**: Retrieval isn't finding relevant chunks

**Solutions**:
1. **Check Documents page**: Are files successfully uploaded and indexed?
2. **Test retrieval**: Ask "List all documents you have access to"
3. **Use specific queries**: Match vocabulary and terms from your documents
4. **Check document selection**: In chat settings, verify correct documents are selected for retrieval

---

## Getting Additional Help

### Check logs

**Backend logs**:
```bash
# All logs
docker compose logs -f backend

# Error logs only
docker compose logs -f backend | grep -i error

# Recent logs
docker compose logs --tail=100 backend
```

**Frontend logs**:
- Open browser Developer Tools (F12)
- Check Console tab for errors
- Check Network tab for failed API requests

### Search existing issues

Before reporting a bug, search existing issues:
- [GitHub Issues](https://github.com/firechair/ai-knowledge-console/issues)
- [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)

### Report a bug

If you've found a new issue:
1. Go to [GitHub Issues](https://github.com/firechair/ai-knowledge-console/issues/new)
2. Use the bug report template
3. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Docker version)
   - Relevant logs

See [CONTRIBUTING.md](CONTRIBUTING.md#reporting-bugs) for detailed bug report guidelines.

### Ask for help

For questions and general help:
- [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions) - Community support
- [Developer Guide](DEVELOPER_GUIDE.md) - Technical reference
- [Configuration Guide](CONFIGURATION.md) - All settings explained

---

## Quick Reference

### Health checks

```bash
# Backend health
curl http://localhost:8000/health

# LLM server health (local)
curl http://localhost:8080/health

# ChromaDB
curl http://localhost:8000/api/documents/list

# Database
sqlite3 backend/conversations.db ".tables"
```

### Common fixes

**Most issues resolve with**:
```bash
# Restart services
docker compose restart

# Rebuild and restart
docker compose down
docker compose up -d --build

# View logs
docker compose logs -f
```

**For local development**:
```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn app:app --reload

# Frontend
cd frontend
VITE_API_URL=http://localhost:8000 npm run dev
```

---

## Additional Resources

- [Configuration Guide](CONFIGURATION.md) - Complete environment variable reference
- [Usage Guide](USAGE_GUIDE.md) - Practical examples and workflows
- [OAuth Setup Guide](OAUTH_SETUP.md) - Detailed OAuth configuration
- [Developer Guide](DEVELOPER_GUIDE.md) - API reference and development setup
- [Architecture Guide](ARCHITECTURE.md) - System design and technical details

---

**Last Updated**: 2025-12-27
