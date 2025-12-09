# API Reference

## Health
- `GET /health`
  - Response: `{ "status": "healthy" }`

## Documents
- `POST /api/documents/upload`
  - Form: `file` (PDF, DOCX, TXT)
  - Response: `{ filename, chunks_created, status }`
  - Example:
    ```bash
    curl -F file=@architecture.txt http://localhost:8000/api/documents/upload
    ```
- `GET /api/documents/list`
  - Response: `{ documents: ["filename1", ...] }`
  - Example:
    ```bash
    curl http://localhost:8000/api/documents/list
    ```
- `DELETE /api/documents/{filename}`
  - Response: `{ status: "deleted", filename }`

## Chat
- `POST /api/chat/query`
  - JSON: `{ message, use_documents, tools, tool_params, conversation_id }`
  - Response: `{ response, sources, api_data_used, conversation_id }`
  - Example:
    ```bash
    curl -s -X POST http://localhost:8000/api/chat/query \
      -H 'Content-Type: application/json' \
      -d '{"message":"Top HN?","use_documents":false,"tools":["hackernews"],"tool_params":{}}'
    ```
- `WS /api/chat/ws`
  - Streaming types: `start`, `token`, `end`, `api_data`

## Conversations
- `GET /api/conversations/`
  - Response: `{ conversations: [{ id, created_at, title, last_message_preview, last_message_at }] }`
- `GET /api/conversations/{id}`
  - Response: `{ id, messages_count }`
- `GET /api/conversations/{id}/messages`
  - Response: `{ messages: [{ role, content, created_at }] }`
- `POST /api/conversations/`
  - Response: `{ id }`
- `POST /api/conversations/{id}/rename`
  - JSON: `{ title }`
  - Response: `{ id, title }`
- `DELETE /api/conversations/{id}`
  - Response: `{ status: "deleted", id }`
- `DELETE /api/conversations/`
  - Response: `{ status: "deleted_all" }`

## Connectors
- `GET /api/connectors/`
  - Response: `{ connectors: { hackernews: { enabled, configured }, ... } }`
- `POST /api/connectors/configure`
  - JSON: `{ name, api_key?, enabled? }`
- `POST /api/connectors/{name}/toggle`
  - Response: `{ enabled, configured }`
