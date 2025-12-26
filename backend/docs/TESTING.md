# Testing

## Test Suite
- Runner: `pytest` with `pytest-asyncio` and `pytest-cov`
- Config: `backend/pytest.ini` defines markers and coverage addopts
- Layout:
  - `tests/unit/*`: unit tests
  - `tests/integration/*`: API integration tests
  - `tests/test_health.py`: health endpoint

## Commands
- Create and activate venv:
  - `python3 -m venv .venv && source .venv/bin/activate`
- Install backend deps:
  - `pip install -r requirements.txt`
- Run all tests:
  - `pytest -q`
- Run focused tests:
  - `pytest -vv tests/unit/test_llm_service.py::TestLLMService::test_generate_stream_openrouter`
- Show coverage HTML:
  - `pytest --cov=. --cov-report=html`

## Common Issues
- Missing `pytest-cov`: install with `pip install pytest-cov`
- Async tests failing: ensure `pytest-asyncio` installed
- External deps for file processing:
  - `pypdf` and `python-docx` required for PDF/DOCX support (`backend/requirements.txt`)

## CI Tips
- Use markers:
  - `-m unit` or `-m integration` to filter
- Keep `settings.json` minimal for reproducibility; tests mock env via `get_settings`

