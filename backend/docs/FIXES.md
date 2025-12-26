# Fixes & Implementations

## PDF Generation & Download
- Problem: 404 on `POST /api/files/generate`, “Retry” not working, and downloads failing
- Fixes:
  - Router prefix corrected to avoid double `/api/files` (`backend/routers/files.py:8`)
  - Absolute URLs returned for generated files:
    - Markdown (`backend/services/file_service.py:47`)
    - HTML (`backend/services/file_service.py:63`)
    - PDF (`backend/services/file_service.py:111`)
  - Deps added to `requirements.txt`: `pypdf`, `python-docx`

## LLM Service Reliability
- Provider detection aligned with env overrides:
  - `provider_type` respects env `llm_provider` (`backend/services/llm_service.py:18`)
  - `cloud_provider` returns `None` when env is local (`backend/services/llm_service.py:27`)
  - `base_url` prefers env local base when `llm_provider=local` (`backend/services/llm_service.py:78`)
  - `model` uses env `openrouter_model` when OpenRouter selected (`backend/services/llm_service.py:92`)
- Streaming fix:
  - Added `return` after cloud stream loop to prevent falling-through to local (`backend/services/llm_service.py:248`)

## Testing Improvements
- Installed `pytest`, `pytest-asyncio`, `pytest-cov`
- Fixed failing tests due to JSON serialization of `Mock` responses and provider selection mismatch
- Full suite passing: 86 passed, 2 skipped

## Developer Notes
- Static files are mounted at `/static`; serving absolute URLs prevents frontend proxy issues
- Vite proxy only covers `/api`, not `/static` — returning absolute URLs is necessary in dev

