# How It Works

## Config Precedence
- Env-driven settings (from `config.py`) override behavior where tests and legacy flows expect it
- User `settings.json` is merged by `ConfigService` when present
- `LLMService` chooses provider and base URL:
  - Local enforced if `llm_provider=local` (`backend/services/llm_service.py:68`, `:75`)
  - OpenRouter recognized via env or merged config (`backend/services/llm_service.py:49`)
  - Stream fix ensures cloud streaming does not fall through to local (`backend/services/llm_service.py:248`)

## File Generation Flow
1. Frontend component calls `POST /api/files/generate` with `content`, `format`, `title`, `filename`
2. Router delegates to `FileService.generate_file` (`backend/routers/files.py:28`)
3. Service writes to `static/generated` and returns:
   - `filename`, `path`, and absolute `url` (`backend/services/file_service.py:44`, `:60`, `:111`)
4. Frontend automatically triggers client-side download using returned `url`

## Endpoints
- Files:
  - `POST /api/files/generate` creates Markdown, HTML, or PDF (`backend/routers/files.py:17`)
  - `GET /api/files/download/{filename}` returns file stream (`backend/routers/files.py:37`)
- Health:
  - `GET /health` returns `{status: "healthy"}` (`backend/app.py:129`)
- Static:
  - `GET /static/generated/{filename}` serves previously generated files

## Rate Limiting & Headers
- Optional in-memory limiter (`backend/app.py:65`)
- Adds `X-Request-ID` and rate limit headers on responses (`backend/app.py:95`)

