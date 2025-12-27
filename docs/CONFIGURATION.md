# Configuration Reference

> 📌 **Canonical Configuration Reference**
> This is the authoritative source for all environment variables and settings.

Complete guide to all configuration options for the AI Knowledge Console.

---

## LLM Provider Settings

### Local (llama.cpp)

For running a local LLM server on your machine.

```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080
```

**Requirements:**
- llama.cpp server running on the specified URL
- GGUF model loaded in the server
- Sufficient RAM for your model size

**Common Issues:**
- Ensure llama.cpp is accessible from Docker with `http://host.docker.internal:8080` if running in containers
- Check firewall settings if server is not reachable

---

### OpenRouter

Cloud-hosted LLM provider with access to multiple models.

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=x-ai/grok-4.1-fast
```

#### Available Models

Popular models accessible through OpenRouter:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `x-ai/grok-4.1-fast` | General chat, fast responses | ⚡⚡⚡ | $$ |
| `anthropic/claude-3.5-sonnet` | Reasoning, analysis | ⚡⚡ | $$$ |
| `openai/gpt-4-turbo` | General purpose, balanced | ⚡⚡ | $$$ |
| `google/gemini-pro-1.5` | Long context, multilingual | ⚡⚡ | $$ |
| `meta-llama/llama-3.1-70b-instruct` | Open source, capable | ⚡ | $ |

See [OpenRouter Models](https://openrouter.ai/models) for the complete list and pricing.

#### Generation Parameters

Fine-tune how the model generates responses:

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `OPENROUTER_TEMPERATURE` | 0.7 | 0.0 - 2.0 | Controls randomness. Lower = more deterministic, higher = more creative |
| `OPENROUTER_MAX_TOKENS` | 1024 | 1 - 8192+ | Maximum response length in tokens |
| `OPENROUTER_TOP_P` | 0.9 | 0.0 - 1.0 | Nucleus sampling threshold (% of probability mass to consider) |
| `OPENROUTER_FREQUENCY_PENALTY` | 0.2 | 0.0 - 2.0 | Reduces word repetition based on frequency |
| `OPENROUTER_PRESENCE_PENALTY` | 0.0 | 0.0 - 2.0 | Encourages discussing new topics |
| `OPENROUTER_REPETITION_PENALTY` | 1.1 | 1.0 - 2.0 | Model-specific repetition control |

**Recommended Presets:**

**Creative Writing:**
```env
OPENROUTER_TEMPERATURE=1.2
OPENROUTER_TOP_P=0.95
OPENROUTER_FREQUENCY_PENALTY=0.3
OPENROUTER_MAX_TOKENS=2048
```

**Factual/Technical:**
```env
OPENROUTER_TEMPERATURE=0.3
OPENROUTER_TOP_P=0.8
OPENROUTER_FREQUENCY_PENALTY=0.1
OPENROUTER_MAX_TOKENS=1024
```

**Balanced (Default):**
```env
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_TOP_P=0.9
OPENROUTER_FREQUENCY_PENALTY=0.2
OPENROUTER_MAX_TOKENS=1024
```

**Cost Optimization:**
- Use `MAX_TOKENS` to limit response length and reduce costs
- Choose models wisely: `grok-4.1-fast` is cheaper than `gpt-4-turbo`
- Monitor usage at [OpenRouter Dashboard](https://openrouter.ai/credits)

---

## Settings Management (New in v2.0)

### settings.json

**Location:** `backend/settings.json`

The application now supports user-configurable settings managed through the UI. These settings are stored in `settings.json` and merged with environment variables at runtime.

**Example settings.json:**

```json
{
  "llm": {
    "provider_type": "cloud",
    "cloud_provider": "openrouter",
    "model": "x-ai/grok-4.1-fast",
    "base_url": "https://openrouter.ai/api/v1",
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "api_keys": {
    "openrouter": "sk-or-v1-...",
    "github_token": "ghp_...",
    "openweather_api_key": "..."
  },
  "embedding": {
    "model": "all-MiniLM-L6-v2"
  }
}
```

### Configuration Precedence

Configuration is loaded in the following order (later sources override earlier):

1. **Application Defaults** - Hardcoded fallback values
2. **settings.json** - User preferences from UI
3. **Environment Variables (.env)** - Highest priority

**Example:** If `LLM_PROVIDER=local` is set in `.env`, it overrides any cloud provider selection in `settings.json`.

### Managing Settings

**Via UI (Recommended):**
1. Navigate to Settings tab in the application
2. Configure LLM provider, API keys, and models
3. Changes are automatically saved to `settings.json`

**Via settings.json directly:**
1. Edit `backend/settings.json`
2. Restart the backend to apply changes
3. Use environment variables for sensitive data in production

### Model Management Settings

**Environment Variables:**
- `MODELS_DIR` - Directory for downloaded GGUF models (default: `./models`)
- `EMBEDDING_MODELS_DIR` - Directory for embedding models (default: `./models/embeddings`)

**UI Configuration:**
- Navigate to Settings → Models tab
- Download models with progress tracking
- Models stored in configured directories

**Example:**

```env
# Custom model directories
MODELS_DIR=/app/data/models
EMBEDDING_MODELS_DIR=/app/data/embeddings
```

### Security Considerations

**Development:**
- `settings.json` is git-ignored (see `.gitignore`)
- Safe to use for local development

**Production:**
- **Recommended:** Use environment variables for sensitive data
- Mount `settings.json` as a Docker secret
- Or use secret management service (AWS Secrets Manager, HashiCorp Vault, etc.)

**Best Practice:**

```env
# Production .env - use environment variables for secrets
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}  # From secret manager
GITHUB_TOKEN=${GITHUB_TOKEN}              # From secret manager

# Non-sensitive config can stay in settings.json
```

---

## Vector Database Settings

### ChromaDB Configuration

```env
CHROMA_PERSIST_DIR=../vectorstore/chroma
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**CHROMA_PERSIST_DIR:**
- Path to store the vector database
- Relative paths are relative to backend directory
- Use absolute paths in production for clarity

**EMBEDDING_MODEL:**
- SentenceTransformer model for document embeddings
- Default `all-MiniLM-L6-v2`: Fast, 384 dimensions, good for English
- Alternatives:
  - `all-mpnet-base-v2`: More accurate, 768 dimensions, slower
  - `paraphrase-multilingual-MiniLM-L12-v2`: Multilingual support

**Production Recommendations:**
```env
# Use absolute paths
CHROMA_PERSIST_DIR=/app/data/vectorstore/chroma

# Or in Docker
CHROMA_PERSIST_DIR=/app/vectorstore/chroma
```

---

## Database Settings

### Conversations Database

```env
CONVERSATIONS_DB_PATH=backend/conversations.db
```

**Default:** `backend/conversations.db` (SQLite file)

**Stores:**
- Conversation metadata (ID, created_at, title)
- Message history (role, content, timestamps)

**Production Recommendations:**
```env
# Use absolute path for production
CONVERSATIONS_DB_PATH=/app/data/conversations.db
```

**Backup:**
```bash
# Simple backup
cp backend/conversations.db backup/conversations-$(date +%Y%m%d).db

# Or use Docker volume backup
docker run --rm -v ai-console-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/conversations-backup.tar.gz /data
```

---

## Security & Performance

### CORS Configuration

```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Format:** Comma-separated list of allowed origins (no spaces)

**Local Development:**
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Production:**
```env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Security Note:** Never use `*` in production - always specify exact origins.

---

### Upload Limits

```env
MAX_UPLOAD_MB=25
```

**Default:** 25 MB per file

**Considerations:**
- Larger files take longer to process
- Memory usage scales with file size
- Chunking happens in memory
- Set based on your server's available RAM

**Recommended by Use Case:**
- Personal use: 25 MB (default)
- Team use: 50 MB
- Enterprise: 100 MB+

---

### Rate Limiting

Protect your API from abuse and excessive usage.

```env
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SEC=60
```

**RATE_LIMIT_ENABLED:**
- `false`: Disabled (default, fine for personal use)
- `true`: Enabled (recommended for public/shared deployments)

**RATE_LIMIT_REQUESTS:**
- Maximum requests allowed per window
- Default: 100 requests

**RATE_LIMIT_WINDOW_SEC:**
- Time window in seconds
- Default: 60 seconds (1 minute)

**Example Configurations:**

**Strict (Public API):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_SEC=60
```

**Moderate (Shared team):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW_SEC=300  # 5 minutes
```

**Response when rate limited:**
```json
{
  "detail": "rate limit"
}
```
HTTP Status: `429 Too Many Requests`

---

## OAuth Settings

Required for Gmail, Drive, Slack, and Notion integrations.

### URLs

```env
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
```

**APP_BASE_URL:**
- Your backend API URL
- Used for OAuth callback URLs
- Must match exactly what's registered in OAuth apps

**FRONTEND_BASE_URL:**
- Your frontend application URL
- Where users are redirected after OAuth flow
- Must be accessible by user's browser

**Local Development:**
```env
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
```

**Production:**
```env
APP_BASE_URL=https://api.yourdomain.com
FRONTEND_BASE_URL=https://yourdomain.com
```

**Important:** Update OAuth app settings in each provider when changing these URLs.

### Client Credentials

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
NOTION_CLIENT_ID=...
NOTION_CLIENT_SECRET=...
```

**Obtaining Credentials:**

See the [OAuth Setup Guide](OAUTH_SETUP.md) for detailed instructions on creating OAuth applications for each provider.

**Security:**
- Never commit credentials to git
- Use `.env` file (gitignored)
- Rotate secrets periodically
- Use different credentials for dev/staging/production

---

## External API Tools

Optional API keys for tool integrations.

### GitHub

```env
GITHUB_TOKEN=ghp_...
```

**Enables:** Repository commit search

**How to get:**
1. Go to [GitHub Settings → Developer settings](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Scope: `repo` (read access)
4. Expiration: 90 days recommended

**Usage:** Fetch recent commits from specified repositories

---

### OpenWeather

```env
OPENWEATHER_API_KEY=...
```

**Enables:** Current weather data

**How to get:**
1. Sign up at [OpenWeatherMap](https://openweathermap.org/)
2. Go to API keys section
3. Copy default key or create new one
4. Wait ~10 minutes for activation

**Free tier:** 1,000 calls/day

---

### Other APIs

**No API key required:**
- CoinGecko (crypto prices)
- Hacker News (tech news)

These APIs are public and work out of the box.

---

## Environment-Specific Configurations

### Development (.env)

```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8080
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
RATE_LIMIT_ENABLED=false
```

### Production (.env)

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
APP_BASE_URL=https://api.yourdomain.com
FRONTEND_BASE_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SEC=60
CONVERSATIONS_DB_PATH=/app/data/conversations.db
CHROMA_PERSIST_DIR=/app/data/vectorstore/chroma
```

### Docker (.env)

```env
LLM_PROVIDER=local
LLM_BASE_URL=http://host.docker.internal:8080
CHROMA_PERSIST_DIR=/app/vectorstore/chroma
CONVERSATIONS_DB_PATH=/app/data/conversations.db
```

---

## Troubleshooting Configuration

For comprehensive troubleshooting help, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

**Common configuration issues**:
- LLM not responding → Check provider settings and API keys
- OAuth redirects failing → Verify URL configuration matches exactly
- Data not persisting → Check directory paths and permissions

---

## Configuration Best Practices

1. **Use .env files** - Never hard-code credentials
2. **Keep .env gitignored** - Prevent accidental commits
3. **Use .env.example** - Document all available options
4. **Absolute paths in production** - Avoid relative path issues
5. **Different credentials per environment** - Dev/staging/production
6. **Rotate secrets regularly** - Especially for production
7. **Monitor API usage** - Avoid unexpected costs
8. **Log configuration on startup** - But not sensitive values
9. **Validate required configs** - Fail fast with clear errors
10. **Document custom settings** - Help future maintainers

---

**Last Updated:** December 1, 2025  
**Related Docs:**
- [OAuth Setup Guide](OAUTH_SETUP.md)
- [Architecture](architecture.md)
