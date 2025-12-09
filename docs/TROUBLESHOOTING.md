# Troubleshooting

## Infinite Spinner on Documents or Conversations
- Check backend health: `curl http://localhost:8000/health` should return `{status:"healthy"}`.
- First-time embedding model load: initial add/search lazily loads the model; allow time.
- Ensure Python deps installed: `sentence-transformers`, `chromadb` in the venv.
- Confirm CORS `allowed_origins` includes `http://localhost:5173`.

## Port 8000 Unresponsive
- Inspect backend logs for syntax errors.
- Activate venv and run `uvicorn app:app --reload --port 8000`.
- Retry health: `curl http://localhost:8000/health`.

## WebSocket Error: "closed before established" in dev
- React Strict Mode can double-invoke effects; cleanup guards only close `OPEN` sockets.
- This reduces noise; functional streaming should proceed.

## External Tools Not Returning Data
- Verify the connector is enabled in `Connectors`.
- If a key is required, check `.env` for `GITHUB_TOKEN`, `OPENWEATHER_API_KEY`.
- For OAuth tools (Gmail, Drive, Slack, Notion), authorize via the UI.

## OAuth Authorization opens provider but returns JSON or stalls
- Ensure frontend is started with a backend URL: `VITE_API_URL=http://localhost:8000 npm run dev`.
- Check `.env` has valid client credentials and exact redirect URIs:
  - `APP_BASE_URL=http://localhost:8000`
  - `FRONTEND_BASE_URL=http://localhost:5173`
- The app includes a `state` with `return_url` to bring you back to the Connectors tab; callbacks redirect there on success.

## Documents Not Listed
- Confirm vectorstore path `CHROMA_PERSIST_DIR` exists and is writable.
- Check `backend/services/vector_store.py` configuration.

## Conversations Not Loading
- List via `curl http://localhost:8000/api/conversations/` to confirm data is present.
- Check SQLite file `backend/conversations.db` exists and is accessible.
