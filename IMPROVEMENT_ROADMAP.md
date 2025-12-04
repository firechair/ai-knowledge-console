# AI Knowledge Console - Improvement Roadmap
## For Local Development & Testing Use Case

This roadmap is designed for implementing improvements to make the application robust for local development and testing. Each task is structured to be executed by an LLM agent with specific, actionable steps.

---

## Phase 1: Critical Bug Fixes (Week 1)
**Goal:** Fix breaking bugs that affect user experience

### Task 1.1: Fix Frontend useState Bug in Connectors Component
**Priority:** CRITICAL
**Estimated Time:** 15 minutes
**Files to Modify:** `frontend/src/components/Connectors.jsx`

**Detailed Steps:**
1. Read the file: `frontend/src/components/Connectors.jsx`
2. Locate line ~50 where `useState` is used to trigger side effects
3. Look for this pattern: `useState(() => { onToolsChange?.(enabledTools) })`
4. Replace with proper `useEffect` hook:
   ```javascript
   useEffect(() => {
     onToolsChange?.(enabledTools);
   }, [enabledTools, onToolsChange]);
   ```
5. Verify the dependencies array includes both `enabledTools` and `onToolsChange`
6. Test: Start frontend, navigate to Connectors tab, verify no infinite re-renders

**Acceptance Criteria:**
- No console warnings about setState in render
- Connectors tab loads without freezing
- Tool state changes propagate correctly to parent

---

### Task 1.2: Implement WebSocket Reconnection with Exponential Backoff
**Priority:** CRITICAL
**Estimated Time:** 2 hours
**Files to Modify:** `frontend/src/components/Chat.jsx`

**Detailed Steps:**
1. Read the current WebSocket implementation in `frontend/src/components/Chat.jsx`
2. Identify where WebSocket is created (search for `new WebSocket`)
3. Create a reconnection utility function at the top of the file:
   ```javascript
   const useWebSocketWithReconnect = (url, onMessage, onError) => {
     const [ws, setWs] = useState(null);
     const [reconnectAttempt, setReconnectAttempt] = useState(0);
     const maxReconnectAttempts = 5;
     const baseDelay = 1000; // 1 second

     const connect = useCallback(() => {
       const websocket = new WebSocket(url);

       websocket.onopen = () => {
         console.log('WebSocket connected');
         setReconnectAttempt(0);
       };

       websocket.onmessage = onMessage;

       websocket.onerror = (error) => {
         console.error('WebSocket error:', error);
         onError?.(error);
       };

       websocket.onclose = (event) => {
         console.log('WebSocket closed:', event.code, event.reason);

         if (reconnectAttempt < maxReconnectAttempts) {
           const delay = Math.min(baseDelay * Math.pow(2, reconnectAttempt), 30000);
           console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempt + 1}/${maxReconnectAttempts})`);

           setTimeout(() => {
             setReconnectAttempt(prev => prev + 1);
             connect();
           }, delay);
         } else {
           console.error('Max reconnection attempts reached');
           onError?.(new Error('Failed to connect after multiple attempts'));
         }
       };

       setWs(websocket);
     }, [url, onMessage, onError, reconnectAttempt]);

     useEffect(() => {
       connect();
       return () => {
         if (ws) {
           ws.close();
         }
       };
     }, [connect]);

     return ws;
   };
   ```
4. Replace the current WebSocket creation with the hook:
   ```javascript
   const ws = useWebSocketWithReconnect(
     `ws://localhost:8000/api/chat/ws`,
     handleWebSocketMessage,
     handleWebSocketError
   );
   ```
5. Add UI indicator for connection status:
   ```javascript
   const [connectionStatus, setConnectionStatus] = useState('connecting');
   // Update status based on WebSocket events
   ```
6. Display connection status in the UI (add banner at top of chat)

**Testing Steps:**
1. Start backend and frontend
2. Open chat interface
3. Send a message - verify it works
4. Stop backend (kill uvicorn process)
5. Verify UI shows "Reconnecting..." message
6. Restart backend
7. Verify connection re-establishes automatically
8. Send another message - verify it works

**Acceptance Criteria:**
- WebSocket reconnects automatically on disconnect
- Exponential backoff prevents server hammering
- UI shows connection status clearly
- After 5 failed attempts, user sees clear error message

---

### Task 1.3: Refactor Global Service Instantiation to Dependency Injection
**Priority:** CRITICAL
**Estimated Time:** 3 hours
**Files to Modify:**
- `backend/routers/chat.py`
- `backend/routers/documents.py`
- `backend/routers/connectors.py`

**Detailed Steps:**

**Step 1: Create Dependency Functions (30 min)**
1. Create new file: `backend/dependencies.py`
2. Add dependency functions:
   ```python
   from functools import lru_cache
   from services.llm_service import LLMService
   from services.vector_store import VectorStoreService
   from services.conversation_service import ConversationService
   from services.api_tools import APIToolsService
   from config import get_settings

   @lru_cache()
   def get_llm_service() -> LLMService:
       """Dependency for LLM service"""
       return LLMService()

   @lru_cache()
   def get_vector_store() -> VectorStoreService:
       """Dependency for vector store service"""
       settings = get_settings()
       return VectorStoreService(settings)

   @lru_cache()
   def get_conversation_service() -> ConversationService:
       """Dependency for conversation service"""
       return ConversationService()

   @lru_cache()
   def get_api_tools() -> APIToolsService:
       """Dependency for API tools service"""
       return APIToolsService()
   ```

**Step 2: Refactor chat.py (45 min)**
1. Read `backend/routers/chat.py`
2. Remove global instantiations (lines ~11-14):
   ```python
   # DELETE THESE LINES:
   # llm_service = LLMService()
   # vector_store = VectorStoreService(settings)
   # conversation_service = ConversationService()
   # api_tools = APIToolsService()
   ```
3. Add dependency injection to each endpoint:
   ```python
   from fastapi import APIRouter, Depends
   from dependencies import (
       get_llm_service,
       get_vector_store,
       get_conversation_service,
       get_api_tools
   )

   @router.post("/query")
   async def chat_query(
       request: ChatRequest,
       llm_service: LLMService = Depends(get_llm_service),
       vector_store: VectorStoreService = Depends(get_vector_store),
       conversation_service: ConversationService = Depends(get_conversation_service),
       api_tools: APIToolsService = Depends(get_api_tools)
   ):
       # Function body uses injected services
       ...
   ```
4. Update all functions in the router to use dependencies

**Step 3: Refactor documents.py (30 min)**
1. Read `backend/routers/documents.py`
2. Remove global `vector_store` instantiation
3. Add dependency injection:
   ```python
   @router.post("/upload")
   async def upload_document(
       file: UploadFile = File(...),
       vector_store: VectorStoreService = Depends(get_vector_store)
   ):
       ...
   ```
4. Update all endpoints to use injected dependencies

**Step 4: Refactor connectors.py (30 min)**
1. Read `backend/routers/connectors.py`
2. Remove global `api_tools` instantiation
3. Add dependency injection:
   ```python
   @router.post("/configure")
   async def configure_connector(
       config: ConnectorConfig,
       api_tools: APIToolsService = Depends(get_api_tools)
   ):
       ...
   ```

**Step 5: Update WebSocket Handler (45 min)**
1. In `backend/routers/chat.py`, find the WebSocket endpoint
2. Current implementation creates new services per connection - fix this:
   ```python
   @router.websocket("/ws")
   async def websocket_endpoint(
       websocket: WebSocket,
       llm_service: LLMService = Depends(get_llm_service),
       vector_store: VectorStoreService = Depends(get_vector_store),
       conversation_service: ConversationService = Depends(get_conversation_service),
       api_tools: APIToolsService = Depends(get_api_tools)
   ):
       await websocket.accept()
       # Use injected services instead of creating new ones
       ...
   ```

**Testing Steps:**
1. Run backend: `uvicorn app:app --reload`
2. Verify no errors on startup
3. Test each endpoint:
   - POST /api/chat/query
   - POST /api/documents/upload
   - GET /api/connectors/
   - WebSocket connection to /api/chat/ws
4. Verify services are singletons (only created once)
5. Check logs for proper initialization

**Acceptance Criteria:**
- No global service instantiations remain in routers
- All endpoints use dependency injection
- Services are created once and reused (verify with logging)
- All API endpoints work as before
- WebSocket connections work correctly

---

## Phase 2: Testing Foundation (Week 2)
**Goal:** Establish comprehensive test coverage

### Task 2.1: Set Up Testing Infrastructure
**Priority:** HIGH
**Estimated Time:** 2 hours
**Files to Create/Modify:**
- `backend/pytest.ini`
- `backend/conftest.py`
- `frontend/vitest.config.js`

**Detailed Steps:**

**Step 1: Backend Test Setup (1 hour)**
1. Create `backend/pytest.ini`:
   ```ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts =
       --verbose
       --cov=.
       --cov-report=html
       --cov-report=term-missing
       --cov-config=.coveragerc
   ```

2. Create `backend/.coveragerc`:
   ```ini
   [run]
   omit =
       */tests/*
       */venv/*
       */__pycache__/*
       */conftest.py

   [report]
   exclude_lines =
       pragma: no cover
       def __repr__
       raise AssertionError
       raise NotImplementedError
       if __name__ == .__main__.:
   ```

3. Create `backend/conftest.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   import tempfile
   import os

   @pytest.fixture(scope="function")
   def test_db():
       """Create a temporary SQLite database for testing"""
       db_fd, db_path = tempfile.mkstemp()
       yield db_path
       os.close(db_fd)
       os.unlink(db_path)

   @pytest.fixture(scope="function")
   def test_vector_store():
       """Create a temporary vector store for testing"""
       with tempfile.TemporaryDirectory() as tmpdir:
           yield tmpdir

   @pytest.fixture(scope="module")
   def test_client():
       """Create a test client for API testing"""
       from app import app
       with TestClient(app) as client:
           yield client

   @pytest.fixture
   def mock_llm_response():
       """Mock LLM response for testing"""
       return "This is a test response from the LLM."

   @pytest.fixture
   def sample_pdf_file():
       """Create a sample PDF file for testing"""
       # Create minimal valid PDF
       pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
       return pdf_content
   ```

**Step 2: Frontend Test Setup (1 hour)**
1. Install Vitest: `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
2. Create `frontend/vitest.config.js`:
   ```javascript
   import { defineConfig } from 'vitest/config'
   import react from '@vitejs/plugin-react'

   export default defineConfig({
     plugins: [react()],
     test: {
       globals: true,
       environment: 'jsdom',
       setupFiles: './src/test/setup.js',
       coverage: {
         provider: 'v8',
         reporter: ['text', 'json', 'html'],
         exclude: [
           'node_modules/',
           'src/test/',
         ]
       }
     }
   })
   ```

3. Create `frontend/src/test/setup.js`:
   ```javascript
   import { expect, afterEach } from 'vitest';
   import { cleanup } from '@testing-library/react';
   import * as matchers from '@testing-library/jest-dom/matchers';

   expect.extend(matchers);

   afterEach(() => {
     cleanup();
   });
   ```

4. Update `frontend/package.json` scripts:
   ```json
   {
     "scripts": {
       "test": "vitest",
       "test:ui": "vitest --ui",
       "test:coverage": "vitest --coverage"
     }
   }
   ```

**Acceptance Criteria:**
- `pytest` runs successfully (even with no tests)
- `npm test` runs successfully in frontend
- Coverage reports generate correctly
- Fixtures are importable in tests

---

### Task 2.2: Write Backend Unit Tests for Services
**Priority:** HIGH
**Estimated Time:** 6 hours
**Files to Create:**
- `backend/tests/test_llm_service.py`
- `backend/tests/test_vector_store.py`
- `backend/tests/test_conversation_service.py`
- `backend/tests/test_api_tools.py`

**Detailed Steps:**

**Step 1: Test LLM Service (2 hours)**
1. Create `backend/tests/test_llm_service.py`:
   ```python
   import pytest
   from unittest.mock import Mock, patch, AsyncMock
   from services.llm_service import LLMService
   import httpx

   @pytest.fixture
   def llm_service():
       """Create LLM service instance for testing"""
       return LLMService()

   @pytest.mark.asyncio
   async def test_generate_openrouter_success(llm_service):
       """Test successful generation with OpenRouter"""
       with patch.object(llm_service, 'is_openrouter', True):
           with patch('httpx.AsyncClient') as mock_client:
               mock_response = Mock()
               mock_response.json.return_value = {
                   "choices": [{"message": {"content": "Test response"}}]
               }
               mock_response.raise_for_status = Mock()

               mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                   return_value=mock_response
               )

               result = await llm_service.generate(
                   prompt="Test prompt",
                   system_prompt="You are a test assistant"
               )

               assert result == "Test response"

   @pytest.mark.asyncio
   async def test_generate_llama_cpp_success(llm_service):
       """Test successful generation with llama.cpp"""
       with patch.object(llm_service, 'is_openrouter', False):
           with patch('httpx.AsyncClient') as mock_client:
               mock_response = Mock()
               mock_response.json.return_value = {"content": "Llama response"}
               mock_response.raise_for_status = Mock()

               mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                   return_value=mock_response
               )

               result = await llm_service.generate(prompt="Test")
               assert result == "Llama response"

   @pytest.mark.asyncio
   async def test_generate_handles_api_error(llm_service):
       """Test that API errors are properly raised"""
       with patch('httpx.AsyncClient') as mock_client:
           mock_response = Mock()
           mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
               "API Error", request=Mock(), response=Mock()
           )

           mock_client.return_value.__aenter__.return_value.post = AsyncMock(
               return_value=mock_response
           )

           with pytest.raises(httpx.HTTPStatusError):
               await llm_service.generate(prompt="Test")

   @pytest.mark.asyncio
   async def test_generate_stream_openrouter(llm_service):
       """Test streaming with OpenRouter"""
       with patch.object(llm_service, 'is_openrouter', True):
           with patch('httpx.AsyncClient') as mock_client:
               async def mock_aiter_lines():
                   lines = [
                       'data: {"choices":[{"delta":{"content":"Hello"}}]}',
                       'data: {"choices":[{"delta":{"content":" world"}}]}',
                       'data: [DONE]'
                   ]
                   for line in lines:
                       yield line

               mock_response = Mock()
               mock_response.aiter_lines = mock_aiter_lines

               mock_client.return_value.__aenter__.return_value.stream.return_value.__aenter__.return_value = mock_response

               chunks = []
               async for chunk in llm_service.generate_stream(prompt="Test"):
                   chunks.append(chunk)

               assert chunks == ["Hello", " world"]

   def test_format_prompt_with_system(llm_service):
       """Test prompt formatting with system message"""
       result = llm_service._format_prompt("System message", "User message")
       assert "[INST]" in result
       assert "System message" in result
       assert "User message" in result

   def test_build_rag_prompt(llm_service):
       """Test RAG prompt building"""
       chunks = [
           {"content": "Chunk 1", "metadata": {"filename": "test.pdf"}},
           {"content": "Chunk 2", "metadata": {"filename": "test.pdf"}}
       ]

       prompt = llm_service.build_rag_prompt(
           query="What is this about?",
           context_chunks=chunks
       )

       assert "Chunk 1" in prompt
       assert "Chunk 2" in prompt
       assert "test.pdf" in prompt
       assert "What is this about?" in prompt
   ```

2. Run tests: `cd backend && pytest tests/test_llm_service.py -v`
3. Verify all tests pass

**Step 2: Test Vector Store Service (2 hours)**
1. Create `backend/tests/test_vector_store.py`:
   ```python
   import pytest
   from services.vector_store import VectorStoreService
   from config import Settings
   import tempfile
   import shutil

   @pytest.fixture
   def temp_chroma_dir():
       """Create temporary directory for ChromaDB"""
       tmpdir = tempfile.mkdtemp()
       yield tmpdir
       shutil.rmtree(tmpdir)

   @pytest.fixture
   def vector_store(temp_chroma_dir):
       """Create vector store with temp directory"""
       settings = Settings(chroma_persist_dir=temp_chroma_dir)
       return VectorStoreService(settings)

   def test_add_documents(vector_store):
       """Test adding documents to vector store"""
       chunks = [
           {"content": "Test chunk 1", "metadata": {"filename": "test.txt"}},
           {"content": "Test chunk 2", "metadata": {"filename": "test.txt"}}
       ]

       # Should not raise exception
       vector_store.add_documents("test.txt", chunks)

   def test_search_documents(vector_store):
       """Test searching documents"""
       # Add test documents
       chunks = [
           {"content": "Python programming language", "metadata": {"filename": "python.txt"}},
           {"content": "JavaScript web development", "metadata": {"filename": "js.txt"}}
       ]
       vector_store.add_documents("test_docs", chunks)

       # Search for Python
       results = vector_store.search("Python programming", n_results=1)

       assert len(results) > 0
       assert "Python" in results[0]["content"]

   def test_delete_document(vector_store):
       """Test deleting documents"""
       chunks = [{"content": "Delete me", "metadata": {"filename": "temp.txt"}}]
       vector_store.add_documents("temp.txt", chunks)

       # Delete
       vector_store.delete_by_filename("temp.txt")

       # Verify deleted
       results = vector_store.search("Delete me", n_results=10)
       for result in results:
           assert result["metadata"]["filename"] != "temp.txt"

   def test_list_documents(vector_store):
       """Test listing all documents"""
       chunks = [{"content": "Doc 1", "metadata": {"filename": "doc1.txt"}}]
       vector_store.add_documents("doc1.txt", chunks)

       docs = vector_store.list_documents()
       assert "doc1.txt" in docs

   def test_chunk_text_respects_size(vector_store):
       """Test that chunking respects size limits"""
       text = "word " * 1000  # 1000 words
       chunks = vector_store._chunk_text(text)

       # Each chunk should be roughly chunk_size
       for chunk in chunks:
           word_count = len(chunk.split())
           # Allow some flexibility due to overlap
           assert word_count <= 600  # chunk_size + some buffer
   ```

2. Run tests: `pytest tests/test_vector_store.py -v`

**Step 3: Test Conversation Service (1 hour)**
1. Create `backend/tests/test_conversation_service.py`:
   ```python
   import pytest
   from services.conversation_service import ConversationService
   import tempfile
   import os

   @pytest.fixture
   def conversation_service():
       """Create conversation service with temp database"""
       db_fd, db_path = tempfile.mkstemp()
       service = ConversationService(db_path=db_path)
       yield service
       os.close(db_fd)
       os.unlink(db_path)

   def test_create_conversation(conversation_service):
       """Test creating a new conversation"""
       conv_id = conversation_service.create_conversation()
       assert conv_id is not None
       assert isinstance(conv_id, str)

   def test_add_and_get_message(conversation_service):
       """Test adding and retrieving messages"""
       conv_id = conversation_service.create_conversation()

       # Add user message
       conversation_service.add_message(conv_id, "user", "Hello")

       # Add assistant message
       conversation_service.add_message(conv_id, "assistant", "Hi there!")

       # Retrieve history
       history = conversation_service.get_history(conv_id)

       assert len(history) == 2
       assert history[0]["role"] == "user"
       assert history[0]["content"] == "Hello"
       assert history[1]["role"] == "assistant"
       assert history[1]["content"] == "Hi there!"

   def test_conversation_persistence(conversation_service):
       """Test that conversations persist across service restarts"""
       conv_id = conversation_service.create_conversation()
       conversation_service.add_message(conv_id, "user", "Test message")

       # Get history and verify
       history = conversation_service.get_history(conv_id)
       assert len(history) == 1
       assert history[0]["content"] == "Test message"
   ```

**Step 4: Test API Tools Service (1 hour)**
1. Create `backend/tests/test_api_tools.py`:
   ```python
   import pytest
   from unittest.mock import Mock, patch
   from services.api_tools import APIToolsService

   @pytest.fixture
   def api_tools():
       return APIToolsService()

   @pytest.mark.asyncio
   async def test_github_commits_success(api_tools):
       """Test fetching GitHub commits"""
       api_tools.configure_connector("github", {"api_key": "test_token"})

       with patch('httpx.AsyncClient') as mock_client:
           mock_response = Mock()
           mock_response.json.return_value = [
               {"sha": "abc123", "commit": {"message": "Test commit"}}
           ]
           mock_response.raise_for_status = Mock()

           mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

           result = await api_tools.fetch_github_commits("testuser", "testrepo")

           assert "commits" in result
           assert len(result["commits"]) == 1

   @pytest.mark.asyncio
   async def test_crypto_price_success(api_tools):
       """Test fetching crypto prices"""
       with patch('httpx.AsyncClient') as mock_client:
           mock_response = Mock()
           mock_response.json.return_value = {
               "bitcoin": {"usd": 50000}
           }
           mock_response.raise_for_status = Mock()

           mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

           result = await api_tools.fetch_crypto_price("bitcoin")

           assert "price" in result
           assert result["crypto_id"] == "bitcoin"

   def test_configure_connector(api_tools):
       """Test configuring a connector"""
       api_tools.configure_connector("github", {"api_key": "test_key"})

       status = api_tools.get_connector_status("github")
       assert status["configured"] is True
   ```

**Acceptance Criteria:**
- All test files created and pass
- Coverage > 60% for services
- Tests run in CI pipeline
- No flaky tests (run 3 times, all pass)

---

### Task 2.3: Write Backend API Integration Tests
**Priority:** HIGH
**Estimated Time:** 4 hours
**Files to Create:**
- `backend/tests/test_api_chat.py`
- `backend/tests/test_api_documents.py`
- `backend/tests/test_api_connectors.py`

**Detailed Steps:**

**Step 1: Test Chat API (1.5 hours)**
1. Create `backend/tests/test_api_chat.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from unittest.mock import patch, AsyncMock

   def test_chat_query_endpoint(test_client):
       """Test POST /api/chat/query"""
       with patch('services.llm_service.LLMService.generate') as mock_generate:
           mock_generate.return_value = "Test response"

           response = test_client.post(
               "/api/chat/query",
               json={
                   "message": "Hello",
                   "use_documents": False,
                   "conversation_id": None
               }
           )

           assert response.status_code == 200
           assert "response" in response.json()

   def test_chat_query_with_documents(test_client):
       """Test chat with RAG enabled"""
       with patch('services.llm_service.LLMService.generate') as mock_generate:
           with patch('services.vector_store.VectorStoreService.search') as mock_search:
               mock_generate.return_value = "RAG response"
               mock_search.return_value = [
                   {"content": "Context", "metadata": {"filename": "test.pdf"}}
               ]

               response = test_client.post(
                   "/api/chat/query",
                   json={
                       "message": "What is this about?",
                       "use_documents": True,
                       "conversation_id": None
                   }
               )

               assert response.status_code == 200
               assert "response" in response.json()

   def test_create_conversation(test_client):
       """Test POST /api/chat/conversations"""
       response = test_client.post("/api/chat/conversations")

       assert response.status_code == 200
       assert "conversation_id" in response.json()

   def test_get_conversation_history(test_client):
       """Test GET /api/chat/conversations/{id}"""
       # Create conversation first
       create_response = test_client.post("/api/chat/conversations")
       conv_id = create_response.json()["conversation_id"]

       # Get history
       response = test_client.get(f"/api/chat/conversations/{conv_id}")

       assert response.status_code == 200
       assert "history" in response.json()
   ```

**Step 2: Test Documents API (1.5 hours)**
1. Create `backend/tests/test_api_documents.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from io import BytesIO

   def test_upload_document_success(test_client, sample_pdf_file):
       """Test successful document upload"""
       files = {"file": ("test.pdf", BytesIO(sample_pdf_file), "application/pdf")}

       response = test_client.post("/api/documents/upload", files=files)

       assert response.status_code == 200
       assert "filename" in response.json()
       assert response.json()["filename"] == "test.pdf"

   def test_upload_invalid_file_type(test_client):
       """Test uploading invalid file type"""
       files = {"file": ("test.exe", BytesIO(b"fake exe"), "application/exe")}

       response = test_client.post("/api/documents/upload", files=files)

       assert response.status_code == 400

   def test_list_documents(test_client):
       """Test GET /api/documents/list"""
       response = test_client.get("/api/documents/list")

       assert response.status_code == 200
       assert "documents" in response.json()
       assert isinstance(response.json()["documents"], list)

   def test_delete_document(test_client, sample_pdf_file):
       """Test DELETE /api/documents/{filename}"""
       # Upload first
       files = {"file": ("delete_test.pdf", BytesIO(sample_pdf_file), "application/pdf")}
       test_client.post("/api/documents/upload", files=files)

       # Delete
       response = test_client.delete("/api/documents/delete_test.pdf")

       assert response.status_code == 200
   ```

**Step 3: Test Connectors API (1 hour)**
1. Create `backend/tests/test_api_connectors.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient

   def test_list_connectors(test_client):
       """Test GET /api/connectors/"""
       response = test_client.get("/api/connectors/")

       assert response.status_code == 200
       assert "connectors" in response.json()

   def test_configure_connector(test_client):
       """Test POST /api/connectors/configure"""
       response = test_client.post(
           "/api/connectors/configure",
           json={
               "name": "github",
               "config": {"api_key": "test_key"}
           }
       )

       assert response.status_code == 200

   def test_toggle_connector(test_client):
       """Test POST /api/connectors/{name}/toggle"""
       response = test_client.post(
           "/api/connectors/github/toggle",
           json={"enabled": True}
       )

       assert response.status_code == 200
   ```

**Acceptance Criteria:**
- All API endpoints tested
- Tests cover success and error cases
- Tests use proper mocking for external services
- All tests pass consistently

---

### Task 2.4: Write Frontend Component Tests
**Priority:** HIGH
**Estimated Time:** 4 hours
**Files to Create:**
- `frontend/src/test/Chat.test.jsx`
- `frontend/src/test/DocumentUpload.test.jsx`
- `frontend/src/test/Connectors.test.jsx`

**Detailed Steps:**

**Step 1: Test Chat Component (2 hours)**
1. Create `frontend/src/test/Chat.test.jsx`:
   ```javascript
   import { describe, it, expect, vi, beforeEach } from 'vitest';
   import { render, screen, fireEvent, waitFor } from '@testing-library/react';
   import Chat from '../components/Chat';

   describe('Chat Component', () => {
     beforeEach(() => {
       vi.clearAllMocks();
     });

     it('renders chat interface', () => {
       render(<Chat conversationId="test-123" />);

       expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
       expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
     });

     it('sends message on button click', async () => {
       const mockOnSend = vi.fn();
       render(<Chat conversationId="test-123" onSendMessage={mockOnSend} />);

       const input = screen.getByPlaceholderText(/type your message/i);
       const sendButton = screen.getByRole('button', { name: /send/i });

       fireEvent.change(input, { target: { value: 'Hello' } });
       fireEvent.click(sendButton);

       await waitFor(() => {
         expect(mockOnSend).toHaveBeenCalledWith('Hello');
       });
     });

     it('displays messages in history', () => {
       const messages = [
         { role: 'user', content: 'Hello' },
         { role: 'assistant', content: 'Hi there!' }
       ];

       render(<Chat conversationId="test-123" messages={messages} />);

       expect(screen.getByText('Hello')).toBeInTheDocument();
       expect(screen.getByText('Hi there!')).toBeInTheDocument();
     });

     it('clears input after sending', async () => {
       render(<Chat conversationId="test-123" />);

       const input = screen.getByPlaceholderText(/type your message/i);
       const sendButton = screen.getByRole('button', { name: /send/i });

       fireEvent.change(input, { target: { value: 'Test' } });
       fireEvent.click(sendButton);

       await waitFor(() => {
         expect(input.value).toBe('');
       });
     });
   });
   ```

**Step 2: Test DocumentUpload Component (1 hour)**
1. Create `frontend/src/test/DocumentUpload.test.jsx`:
   ```javascript
   import { describe, it, expect, vi } from 'vitest';
   import { render, screen, fireEvent, waitFor } from '@testing-library/react';
   import DocumentUpload from '../components/DocumentUpload';

   describe('DocumentUpload Component', () => {
     it('renders upload button', () => {
       render(<DocumentUpload />);
       expect(screen.getByText(/upload document/i)).toBeInTheDocument();
     });

     it('accepts file upload', async () => {
       render(<DocumentUpload />);

       const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
       const input = screen.getByLabelText(/upload/i);

       fireEvent.change(input, { target: { files: [file] } });

       await waitFor(() => {
         expect(screen.getByText('test.pdf')).toBeInTheDocument();
       });
     });

     it('shows error for invalid file type', async () => {
       render(<DocumentUpload />);

       const file = new File(['test'], 'test.exe', { type: 'application/exe' });
       const input = screen.getByLabelText(/upload/i);

       fireEvent.change(input, { target: { files: [file] } });

       await waitFor(() => {
         expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
       });
     });
   });
   ```

**Step 3: Test Connectors Component (1 hour)**
1. Create `frontend/src/test/Connectors.test.jsx`:
   ```javascript
   import { describe, it, expect, vi } from 'vitest';
   import { render, screen, fireEvent } from '@testing-library/react';
   import Connectors from '../components/Connectors';

   describe('Connectors Component', () => {
     const mockConnectors = [
       { name: 'github', configured: true, enabled: false },
       { name: 'weather', configured: false, enabled: false }
     ];

     it('renders connector list', () => {
       render(<Connectors connectors={mockConnectors} />);

       expect(screen.getByText(/github/i)).toBeInTheDocument();
       expect(screen.getByText(/weather/i)).toBeInTheDocument();
     });

     it('toggles connector on switch click', async () => {
       const mockOnToggle = vi.fn();
       render(
         <Connectors
           connectors={mockConnectors}
           onToggle={mockOnToggle}
         />
       );

       const toggle = screen.getAllByRole('switch')[0];
       fireEvent.click(toggle);

       expect(mockOnToggle).toHaveBeenCalledWith('github', true);
     });

     it('disables toggle for unconfigured connectors', () => {
       render(<Connectors connectors={mockConnectors} />);

       const toggles = screen.getAllByRole('switch');
       expect(toggles[1]).toBeDisabled();
     });
   });
   ```

**Acceptance Criteria:**
- Component tests cover main functionality
- Tests pass consistently
- Coverage > 50% for components
- Tests can be run with `npm test`

---

## Phase 3: Performance & UX Improvements (Week 3)
**Goal:** Optimize performance and improve user experience

### Task 3.1: Enable Rate Limiting by Default
**Priority:** HIGH
**Estimated Time:** 30 minutes
**Files to Modify:** `backend/config.py`

**Detailed Steps:**
1. Read `backend/config.py`
2. Find line with `rate_limit_enabled: bool = False`
3. Change to `rate_limit_enabled: bool = True`
4. Verify `rate_limit_requests: int = 100` (reasonable default)
5. Verify `rate_limit_window_sec: int = 60` (1 minute window)
6. Test by sending 101 requests in 1 minute - should get 429 error

**Acceptance Criteria:**
- Rate limiting enabled by default
- Returns 429 after limit exceeded
- Configurable via environment variables

---

### Task 3.2: Add Loading States to Frontend
**Priority:** HIGH
**Estimated Time:** 2 hours
**Files to Modify:**
- `frontend/src/components/Chat.jsx`
- `frontend/src/components/DocumentUpload.jsx`
- `frontend/src/components/Connectors.jsx`

**Detailed Steps:**

**Step 1: Add Loading to Chat Component (45 min)**
1. Read `frontend/src/components/Chat.jsx`
2. Add loading state:
   ```javascript
   const [isLoading, setIsLoading] = useState(false);
   ```
3. Set loading when sending message:
   ```javascript
   const handleSend = async () => {
     setIsLoading(true);
     try {
       // ... send message logic
     } finally {
       setIsLoading(false);
     }
   };
   ```
4. Add loading indicator in UI:
   ```javascript
   {isLoading && (
     <div className="flex items-center space-x-2 text-gray-500">
       <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
       <span>Thinking...</span>
     </div>
   )}
   ```
5. Disable send button while loading:
   ```javascript
   <button disabled={isLoading || !message.trim()}>Send</button>
   ```

**Step 2: Add Loading to DocumentUpload (45 min)**
1. Read `frontend/src/components/DocumentUpload.jsx`
2. Add upload progress state:
   ```javascript
   const [uploadProgress, setUploadProgress] = useState(0);
   const [isUploading, setIsUploading] = useState(false);
   ```
3. Show progress bar:
   ```javascript
   {isUploading && (
     <div className="w-full bg-gray-200 rounded-full h-2">
       <div
         className="bg-blue-600 h-2 rounded-full transition-all duration-300"
         style={{ width: `${uploadProgress}%` }}
       />
       <p className="text-sm text-gray-600 mt-1">
         Uploading and processing... {uploadProgress}%
       </p>
     </div>
   )}
   ```

**Step 3: Add Loading to Connectors (30 min)**
1. Read `frontend/src/components/Connectors.jsx`
2. Add loading state for fetching connectors:
   ```javascript
   const { data: connectors, isLoading } = useQuery('connectors', fetchConnectors);

   if (isLoading) {
     return <div className="animate-pulse">Loading connectors...</div>;
   }
   ```

**Acceptance Criteria:**
- Users see loading indicators during async operations
- Buttons disabled while operations in progress
- Clear visual feedback for all loading states

---

### Task 3.3: Add Error Boundary to Frontend
**Priority:** HIGH
**Estimated Time:** 1 hour
**Files to Create:** `frontend/src/components/ErrorBoundary.jsx`
**Files to Modify:** `frontend/src/App.jsx`

**Detailed Steps:**

**Step 1: Create ErrorBoundary Component (30 min)**
1. Create `frontend/src/components/ErrorBoundary.jsx`:
   ```javascript
   import React from 'react';

   class ErrorBoundary extends React.Component {
     constructor(props) {
       super(props);
       this.state = { hasError: false, error: null, errorInfo: null };
     }

     static getDerivedStateFromError(error) {
       return { hasError: true };
     }

     componentDidCatch(error, errorInfo) {
       console.error('Error caught by boundary:', error, errorInfo);
       this.setState({
         error,
         errorInfo
       });
     }

     handleReset = () => {
       this.setState({ hasError: false, error: null, errorInfo: null });
       window.location.reload();
     };

     render() {
       if (this.state.hasError) {
         return (
           <div className="min-h-screen flex items-center justify-center bg-gray-100">
             <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
               <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
                 <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                 </svg>
               </div>
               <h2 className="mt-4 text-xl font-semibold text-center text-gray-900">
                 Something went wrong
               </h2>
               <p className="mt-2 text-sm text-center text-gray-600">
                 We're sorry for the inconvenience. Please try refreshing the page.
               </p>
               {process.env.NODE_ENV === 'development' && this.state.error && (
                 <details className="mt-4 p-4 bg-gray-50 rounded border border-gray-200">
                   <summary className="cursor-pointer text-sm font-medium text-gray-700">
                     Error Details
                   </summary>
                   <pre className="mt-2 text-xs text-red-600 overflow-auto">
                     {this.state.error.toString()}
                     {this.state.errorInfo?.componentStack}
                   </pre>
                 </details>
               )}
               <button
                 onClick={this.handleReset}
                 className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
               >
                 Reload Page
               </button>
             </div>
           </div>
         );
       }

       return this.props.children;
     }
   }

   export default ErrorBoundary;
   ```

**Step 2: Wrap App with ErrorBoundary (30 min)**
1. Read `frontend/src/App.jsx`
2. Import ErrorBoundary:
   ```javascript
   import ErrorBoundary from './components/ErrorBoundary';
   ```
3. Wrap main app content:
   ```javascript
   function App() {
     return (
       <ErrorBoundary>
         {/* existing app content */}
       </ErrorBoundary>
     );
   }
   ```

**Acceptance Criteria:**
- Errors caught and displayed gracefully
- User can reload page from error screen
- Development mode shows error details
- Production mode shows friendly message only

---

### Task 3.4: Add Database Indexes for Performance
**Priority:** HIGH
**Estimated Time:** 1 hour
**Files to Modify:** `backend/services/conversation_service.py`

**Detailed Steps:**
1. Read `backend/services/conversation_service.py`
2. Find `_init_database()` method
3. Add indexes after table creation:
   ```python
   def _init_database(self):
       with self._get_connection() as conn:
           # Existing table creation...

           # Add indexes
           conn.execute("""
               CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
               ON messages(conversation_id)
           """)

           conn.execute("""
               CREATE INDEX IF NOT EXISTS idx_messages_created_at
               ON messages(created_at)
           """)

           conn.execute("""
               CREATE INDEX IF NOT EXISTS idx_conversations_created_at
               ON conversations(created_at)
           """)

           conn.commit()
   ```
4. Test: Query conversations and verify performance

**Acceptance Criteria:**
- Indexes created on first run
- No errors on subsequent runs (IF NOT EXISTS)
- Query performance improved (test with 1000+ conversations)

---

### Task 3.5: Add Centralized Error Handling to Backend
**Priority:** HIGH
**Estimated Time:** 2 hours
**Files to Create:** `backend/exceptions.py`, `backend/middleware/error_handler.py`
**Files to Modify:** `backend/app.py`

**Detailed Steps:**

**Step 1: Create Custom Exceptions (30 min)**
1. Create `backend/exceptions.py`:
   ```python
   class AppException(Exception):
       """Base exception for application errors"""
       def __init__(self, message: str, status_code: int = 500):
           self.message = message
           self.status_code = status_code
           super().__init__(self.message)

   class ValidationError(AppException):
       """Raised when input validation fails"""
       def __init__(self, message: str):
           super().__init__(message, status_code=400)

   class NotFoundError(AppException):
       """Raised when resource not found"""
       def __init__(self, resource: str):
           super().__init__(f"{resource} not found", status_code=404)

   class ConfigurationError(AppException):
       """Raised when service is not configured"""
       def __init__(self, service: str):
           super().__init__(f"{service} requires configuration", status_code=400)

   class ExternalServiceError(AppException):
       """Raised when external API fails"""
       def __init__(self, service: str, details: str = ""):
           message = f"External service {service} failed"
           if details:
               message += f": {details}"
           super().__init__(message, status_code=502)

   class RateLimitError(AppException):
       """Raised when rate limit exceeded"""
       def __init__(self):
           super().__init__("Rate limit exceeded", status_code=429)
   ```

**Step 2: Create Error Handler Middleware (1 hour)**
1. Create `backend/middleware/error_handler.py`:
   ```python
   from fastapi import Request, status
   from fastapi.responses import JSONResponse
   from exceptions import AppException
   import logging
   import traceback

   logger = logging.getLogger(__name__)

   async def error_handler_middleware(request: Request, call_next):
       """Global error handler middleware"""
       try:
           return await call_next(request)
       except AppException as e:
           logger.warning(f"Application error: {e.message}", extra={
               "path": request.url.path,
               "method": request.method,
               "status_code": e.status_code
           })
           return JSONResponse(
               status_code=e.status_code,
               content={
                   "error": e.message,
                   "type": e.__class__.__name__
               }
           )
       except Exception as e:
           logger.error(f"Unhandled error: {str(e)}", extra={
               "path": request.url.path,
               "method": request.method,
               "traceback": traceback.format_exc()
           })
           return JSONResponse(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               content={
                   "error": "An unexpected error occurred",
                   "type": "InternalServerError"
               }
           )

   def register_exception_handlers(app):
       """Register custom exception handlers"""

       @app.exception_handler(AppException)
       async def app_exception_handler(request: Request, exc: AppException):
           logger.warning(f"Application error: {exc.message}")
           return JSONResponse(
               status_code=exc.status_code,
               content={
                   "error": exc.message,
                   "type": exc.__class__.__name__
               }
           )

       @app.exception_handler(Exception)
       async def general_exception_handler(request: Request, exc: Exception):
           logger.error(f"Unhandled error: {str(exc)}\n{traceback.format_exc()}")
           return JSONResponse(
               status_code=500,
               content={
                   "error": "An unexpected error occurred",
                   "type": "InternalServerError"
               }
           )
   ```

**Step 3: Register Error Handlers in App (30 min)**
1. Read `backend/app.py`
2. Import error handlers:
   ```python
   from middleware.error_handler import register_exception_handlers
   ```
3. Register after creating FastAPI app:
   ```python
   app = FastAPI(title="AI Knowledge Console API")
   register_exception_handlers(app)
   ```
4. Update routers to use custom exceptions:
   ```python
   from exceptions import NotFoundError, ConfigurationError

   # In documents.py:
   if not filename_exists:
       raise NotFoundError("Document")

   # In connectors.py:
   if not connector_configured:
       raise ConfigurationError("GitHub connector")
   ```

**Acceptance Criteria:**
- All errors return consistent JSON format
- Custom exceptions used throughout codebase
- Error details logged server-side
- Client receives appropriate HTTP status codes

---

## Phase 4: Advanced Features (Week 4)
**Goal:** Add user-requested features and quality-of-life improvements

### Task 4.1: Add Conversation Search Functionality
**Priority:** MEDIUM
**Estimated Time:** 3 hours
**Files to Modify:**
- `backend/services/conversation_service.py`
- `backend/routers/chat.py`
- `frontend/src/components/ConversationList.jsx` (new)

**Detailed Steps:**

**Step 1: Add Search to Backend (1.5 hours)**
1. Read `backend/services/conversation_service.py`
2. Add search method:
   ```python
   def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
       """Search conversations by message content"""
       with self._get_connection() as conn:
           cursor = conn.execute("""
               SELECT DISTINCT
                   c.id,
                   c.created_at,
                   m.content as first_message
               FROM conversations c
               JOIN messages m ON c.id = m.conversation_id
               WHERE m.content LIKE ?
               ORDER BY c.created_at DESC
               LIMIT ?
           """, (f"%{query}%", limit))

           results = []
           for row in cursor.fetchall():
               results.append({
                   "id": row[0],
                   "created_at": row[1],
                   "preview": row[2][:100]  # First 100 chars
               })

           return results
   ```

3. Add list all conversations method:
   ```python
   def list_conversations(self, limit: int = 50) -> List[Dict]:
       """List all conversations with preview"""
       with self._get_connection() as conn:
           cursor = conn.execute("""
               SELECT
                   c.id,
                   c.created_at,
                   (SELECT content FROM messages
                    WHERE conversation_id = c.id
                    AND role = 'user'
                    ORDER BY created_at ASC
                    LIMIT 1) as first_message
               FROM conversations c
               ORDER BY c.created_at DESC
               LIMIT ?
           """, (limit,))

           results = []
           for row in cursor.fetchall():
               results.append({
                   "id": row[0],
                   "created_at": row[1],
                   "title": row[2][:50] if row[2] else "New Conversation"
               })

           return results
   ```

4. Add API endpoint in `backend/routers/chat.py`:
   ```python
   @router.get("/conversations")
   async def list_conversations(
       search: Optional[str] = None,
       limit: int = 50,
       conversation_service: ConversationService = Depends(get_conversation_service)
   ):
       """List or search conversations"""
       if search:
           conversations = conversation_service.search_conversations(search, limit)
       else:
           conversations = conversation_service.list_conversations(limit)

       return {"conversations": conversations}
   ```

**Step 2: Add Conversation List to Frontend (1.5 hours)**
1. Create `frontend/src/components/ConversationList.jsx`:
   ```javascript
   import { useState } from 'react';
   import { useQuery } from 'react-query';
   import api from '../utils/api';

   export default function ConversationList({ onSelectConversation }) {
     const [searchQuery, setSearchQuery] = useState('');

     const { data, isLoading } = useQuery(
       ['conversations', searchQuery],
       () => api.get('/chat/conversations', { params: { search: searchQuery } }),
       { enabled: true }
     );

     const conversations = data?.data?.conversations || [];

     return (
       <div className="w-64 border-r border-gray-200 p-4">
         <div className="mb-4">
           <input
             type="text"
             placeholder="Search conversations..."
             value={searchQuery}
             onChange={(e) => setSearchQuery(e.target.value)}
             className="w-full px-3 py-2 border border-gray-300 rounded-md"
           />
         </div>

         {isLoading ? (
           <div className="text-gray-500">Loading...</div>
         ) : (
           <div className="space-y-2">
             {conversations.map((conv) => (
               <button
                 key={conv.id}
                 onClick={() => onSelectConversation(conv.id)}
                 className="w-full text-left p-3 rounded hover:bg-gray-100 transition-colors"
               >
                 <div className="font-medium text-sm truncate">
                   {conv.title || conv.preview}
                 </div>
                 <div className="text-xs text-gray-500 mt-1">
                   {new Date(conv.created_at).toLocaleDateString()}
                 </div>
               </button>
             ))}
           </div>
         )}
       </div>
     );
   }
   ```

2. Integrate in `frontend/src/App.jsx`:
   ```javascript
   import ConversationList from './components/ConversationList';

   // In App component:
   const [selectedConversation, setSelectedConversation] = useState(null);

   <div className="flex h-screen">
     <ConversationList onSelectConversation={setSelectedConversation} />
     <Chat conversationId={selectedConversation} />
   </div>
   ```

**Acceptance Criteria:**
- Users can search conversations by content
- Conversation list shows recent conversations
- Clicking conversation loads its history
- Search updates in real-time as user types

---

### Task 4.2: Add Document Preview Before Upload
**Priority:** MEDIUM
**Estimated Time:** 2 hours
**Files to Modify:** `frontend/src/components/DocumentUpload.jsx`

**Detailed Steps:**
1. Read `frontend/src/components/DocumentUpload.jsx`
2. Add preview state:
   ```javascript
   const [previewFile, setPreviewFile] = useState(null);
   const [previewContent, setPreviewContent] = useState('');
   ```

3. Add preview reader:
   ```javascript
   const handleFileSelect = (file) => {
     setPreviewFile(file);

     if (file.type === 'text/plain') {
       const reader = new FileReader();
       reader.onload = (e) => {
         setPreviewContent(e.target.result.substring(0, 500));
       };
       reader.readAsText(file);
     } else if (file.type === 'application/pdf') {
       setPreviewContent('PDF preview not available - click upload to process');
     }
   };
   ```

4. Add preview UI:
   ```javascript
   {previewFile && (
     <div className="mt-4 p-4 border border-gray-300 rounded">
       <div className="flex justify-between items-center mb-2">
         <h3 className="font-semibold">{previewFile.name}</h3>
         <button onClick={() => setPreviewFile(null)}>Cancel</button>
       </div>
       <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded max-h-40 overflow-auto">
         {previewContent}
       </div>
       <button
         onClick={() => handleUpload(previewFile)}
         className="mt-3 px-4 py-2 bg-blue-600 text-white rounded"
       >
         Confirm Upload
       </button>
     </div>
   )}
   ```

**Acceptance Criteria:**
- Text files show first 500 characters
- PDFs show filename and size
- User can cancel before upload
- Confirm button triggers upload

---

### Task 4.3: Add Accessibility Improvements
**Priority:** MEDIUM
**Estimated Time:** 3 hours
**Files to Modify:** All frontend components

**Detailed Steps:**

**Step 1: Add ARIA Labels (1 hour)**
1. Update `frontend/src/components/Chat.jsx`:
   ```javascript
   <input
     type="text"
     aria-label="Chat message input"
     aria-describedby="chat-input-help"
     placeholder="Type your message..."
   />

   <button
     aria-label="Send message"
     disabled={!message.trim()}
   >
     Send
   </button>
   ```

2. Update `frontend/src/components/DocumentUpload.jsx`:
   ```javascript
   <input
     type="file"
     id="file-upload"
     aria-label="Upload document file"
     aria-describedby="file-upload-help"
   />

   <label htmlFor="file-upload" className="...">
     Choose File
   </label>

   <p id="file-upload-help" className="text-sm text-gray-600">
     Supported formats: PDF, DOCX, TXT
   </p>
   ```

**Step 2: Add Keyboard Navigation (1 hour)**
1. Add keyboard shortcuts in `frontend/src/App.jsx`:
   ```javascript
   useEffect(() => {
     const handleKeyPress = (e) => {
       // Cmd/Ctrl + K: Focus search
       if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
         e.preventDefault();
         document.querySelector('[aria-label="Search conversations"]')?.focus();
       }

       // Cmd/Ctrl + N: New conversation
       if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
         e.preventDefault();
         handleNewConversation();
       }

       // Escape: Close modals
       if (e.key === 'Escape') {
         setShowSettings(false);
       }
     };

     window.addEventListener('keydown', handleKeyPress);
     return () => window.removeEventListener('keydown', handleKeyPress);
   }, []);
   ```

2. Add keyboard navigation to lists:
   ```javascript
   <div
     role="listbox"
     aria-label="Conversations"
     onKeyDown={handleKeyNavigation}
   >
     {conversations.map((conv, index) => (
       <div
         key={conv.id}
         role="option"
         tabIndex={0}
         aria-selected={selectedConv === conv.id}
         onKeyPress={(e) => {
           if (e.key === 'Enter' || e.key === ' ') {
             e.preventDefault();
             onSelectConversation(conv.id);
           }
         }}
       >
         {conv.title}
       </div>
     ))}
   </div>
   ```

**Step 3: Add Focus Management (1 hour)**
1. Add focus trap for modals:
   ```javascript
   const modalRef = useRef();

   useEffect(() => {
     if (showSettings) {
       const focusableElements = modalRef.current.querySelectorAll(
         'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
       );

       const firstElement = focusableElements[0];
       const lastElement = focusableElements[focusableElements.length - 1];

       firstElement?.focus();

       const handleTab = (e) => {
         if (e.key === 'Tab') {
           if (e.shiftKey && document.activeElement === firstElement) {
             e.preventDefault();
             lastElement.focus();
           } else if (!e.shiftKey && document.activeElement === lastElement) {
             e.preventDefault();
             firstElement.focus();
           }
         }
       };

       modalRef.current.addEventListener('keydown', handleTab);
       return () => modalRef.current?.removeEventListener('keydown', handleTab);
     }
   }, [showSettings]);
   ```

**Acceptance Criteria:**
- All interactive elements have ARIA labels
- Keyboard shortcuts work (Cmd+K, Cmd+N, Escape)
- Tab navigation works correctly
- Focus visible on all elements
- Screen reader announces state changes

---

## Phase 5: Code Quality & Documentation (Week 5)
**Goal:** Improve code quality and documentation

### Task 5.1: Add Comprehensive Docstrings to Backend
**Priority:** MEDIUM
**Estimated Time:** 4 hours
**Files to Modify:** All Python files in `backend/services/`

**Detailed Steps:**

**Step 1: Document LLM Service (1 hour)**
1. Read `backend/services/llm_service.py`
2. Add module docstring at top:
   ```python
   """
   LLM Service Module

   Provides abstraction layer for interacting with various LLM providers including:
   - Local llama.cpp servers
   - OpenRouter API
   - OpenAI-compatible endpoints

   Supports both streaming and non-streaming generation.
   """
   ```

3. Add docstrings to all methods:
   ```python
   async def generate(
       self,
       prompt: str,
       system_prompt: str = "",
       max_tokens: int = 1024,
       temperature: float = 0.7
   ) -> str:
       """
       Generate a completion from the LLM.

       Args:
           prompt: The user's input prompt
           system_prompt: Optional system prompt to guide behavior
           max_tokens: Maximum tokens to generate (default: 1024)
           temperature: Sampling temperature 0-1 (default: 0.7)

       Returns:
           Generated text response from the LLM

       Raises:
           httpx.HTTPStatusError: If API request fails
           httpx.RequestError: If network error occurs

       Example:
           >>> service = LLMService()
           >>> response = await service.generate("What is Python?")
           >>> print(response)
           'Python is a high-level programming language...'
       """
       ...
   ```

4. Document all remaining methods similarly

**Step 2: Document Vector Store Service (1 hour)**
1. Read `backend/services/vector_store.py`
2. Add comprehensive docstrings:
   ```python
   """
   Vector Store Service Module

   Manages document embeddings and semantic search using ChromaDB.
   Handles document chunking, embedding generation, and similarity search.
   """

   class VectorStoreService:
       """
       Service for managing document embeddings and semantic search.

       Uses SentenceTransformers for embeddings and ChromaDB for storage.
       Supports adding, searching, and deleting documents.

       Attributes:
           settings: Application settings including chunk size and persist directory
           embedding_model: SentenceTransformer model for generating embeddings
           client: ChromaDB client for vector operations
           collection: ChromaDB collection storing document embeddings
       """
   ```

**Step 3: Document Remaining Services (2 hours)**
1. Document `conversation_service.py`
2. Document `api_tools.py`
3. Document all router functions in `routers/`
4. Add type hints where missing

**Acceptance Criteria:**
- All public methods have docstrings
- Docstrings follow Google style guide
- Parameters and return values documented
- Examples provided for complex methods
- Type hints present on all functions

---

### Task 5.2: Create Constants Configuration File
**Priority:** MEDIUM
**Estimated Time:** 2 hours
**Files to Create:** `backend/constants.py`, `frontend/src/constants.js`
**Files to Modify:** Multiple files to use constants

**Detailed Steps:**

**Step 1: Backend Constants (1 hour)**
1. Create `backend/constants.py`:
   ```python
   """Application-wide constants"""

   # LLM Configuration
   DEFAULT_TEMPERATURE = 0.7
   DEFAULT_MAX_TOKENS = 1024
   MIN_TEMPERATURE = 0.0
   MAX_TEMPERATURE = 1.0
   MAX_TOKENS_LIMIT = 4096

   # Vector Store Configuration
   DEFAULT_CHUNK_SIZE = 500
   DEFAULT_CHUNK_OVERLAP = 50
   DEFAULT_SIMILARITY_RESULTS = 5
   MIN_CHUNK_SIZE = 100
   MAX_CHUNK_SIZE = 2000

   # Document Processing
   SUPPORTED_FILE_TYPES = {
       'application/pdf': '.pdf',
       'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
       'text/plain': '.txt'
   }
   MAX_FILE_SIZE_MB = 25
   MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

   # Conversation
   MAX_CONVERSATION_HISTORY = 6  # Last 6 messages (3 turns)
   CONVERSATION_TITLE_LENGTH = 50

   # API Tools
   GITHUB_API_BASE = "https://api.github.com"
   COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
   OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
   HACKERNEWS_API_BASE = "https://hacker-news.firebaseio.com/v0"

   # Rate Limiting
   DEFAULT_RATE_LIMIT = 100
   DEFAULT_RATE_WINDOW_SEC = 60

   # Error Messages
   ERROR_FILE_TOO_LARGE = f"File size exceeds maximum allowed ({MAX_FILE_SIZE_MB}MB)"
   ERROR_UNSUPPORTED_FILE = "Unsupported file type"
   ERROR_LLM_UNAVAILABLE = "LLM service is unavailable"
   ERROR_DOCUMENT_NOT_FOUND = "Document not found"
   ERROR_CONVERSATION_NOT_FOUND = "Conversation not found"
   ```

2. Update services to use constants:
   ```python
   from constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

   # In vector_store.py:
   self.chunk_size = settings.chunk_size or DEFAULT_CHUNK_SIZE
   ```

**Step 2: Frontend Constants (1 hour)**
1. Create `frontend/src/constants.js`:
   ```javascript
   // API Configuration
   export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

   // WebSocket Configuration
   export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';
   export const WS_RECONNECT_DELAY = 1000;
   export const WS_MAX_RECONNECT_ATTEMPTS = 5;

   // File Upload
   export const MAX_FILE_SIZE_MB = 25;
   export const SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.txt'];
   export const SUPPORTED_MIME_TYPES = [
     'application/pdf',
     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
     'text/plain'
   ];

   // UI Configuration
   export const TOAST_DURATION = 3000;
   export const DEBOUNCE_DELAY = 300;
   export const PAGINATION_SIZE = 20;

   // Tool Parameters Defaults
   export const DEFAULT_TOOL_PARAMS = {
     github_user: '',
     github_repo: '',
     crypto_id: 'bitcoin',
     city: 'San Francisco',
     max_stories: 5
   };

   // Keyboard Shortcuts
   export const SHORTCUTS = {
     NEW_CHAT: { key: 'n', ctrlKey: true, description: 'New conversation' },
     SEARCH: { key: 'k', ctrlKey: true, description: 'Search conversations' },
     SETTINGS: { key: ',', ctrlKey: true, description: 'Open settings' }
   };

   // Error Messages
   export const ERROR_MESSAGES = {
     FILE_TOO_LARGE: `File size exceeds ${MAX_FILE_SIZE_MB}MB`,
     UNSUPPORTED_FILE: `Supported formats: ${SUPPORTED_FILE_TYPES.join(', ')}`,
     NETWORK_ERROR: 'Network error - please check your connection',
     SERVER_ERROR: 'Server error - please try again later'
   };
   ```

2. Update components to use constants:
   ```javascript
   import { MAX_FILE_SIZE_MB, ERROR_MESSAGES } from '../constants';

   // In DocumentUpload.jsx:
   if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
     setError(ERROR_MESSAGES.FILE_TOO_LARGE);
   }
   ```

**Acceptance Criteria:**
- All magic numbers replaced with constants
- Error messages centralized
- Configuration values easy to find and modify
- Constants well-documented

---

### Task 5.3: Add Structured Logging
**Priority:** MEDIUM
**Estimated Time:** 2 hours
**Files to Create:** `backend/logging_config.py`
**Files to Modify:** `backend/app.py`, all services

**Detailed Steps:**

**Step 1: Configure Structured Logging (1 hour)**
1. Install required package: Add to `requirements.txt`:
   ```
   python-json-logger==2.0.7
   ```

2. Create `backend/logging_config.py`:
   ```python
   """Logging configuration for structured JSON logging"""
   import logging
   import sys
   from pythonjsonlogger import jsonlogger

   def setup_logging(app_name: str = "ai-knowledge-console", level: str = "INFO"):
       """
       Configure structured JSON logging.

       Args:
           app_name: Application name for log identification
           level: Logging level (DEBUG, INFO, WARNING, ERROR)
       """
       log_level = getattr(logging, level.upper())

       # Create logger
       logger = logging.getLogger()
       logger.setLevel(log_level)

       # Remove existing handlers
       logger.handlers = []

       # Create console handler with JSON formatter
       handler = logging.StreamHandler(sys.stdout)
       handler.setLevel(log_level)

       # JSON formatter
       formatter = jsonlogger.JsonFormatter(
           '%(asctime)s %(name)s %(levelname)s %(message)s',
           rename_fields={
               "asctime": "timestamp",
               "levelname": "level",
               "name": "logger"
           }
       )
       handler.setFormatter(formatter)

       logger.addHandler(handler)

       # Add app name to all logs
       logging.getLogger().addFilter(
           lambda record: setattr(record, 'app', app_name) or True
       )

       return logger

   class RequestLogger:
       """Context manager for request-scoped logging"""

       def __init__(self, request_id: str, path: str, method: str):
           self.logger = logging.getLogger(__name__)
           self.request_id = request_id
           self.path = path
           self.method = method

       def log_info(self, message: str, **kwargs):
           self.logger.info(
               message,
               extra={
                   'request_id': self.request_id,
                   'path': self.path,
                   'method': self.method,
                   **kwargs
               }
           )

       def log_error(self, message: str, error: Exception = None, **kwargs):
           extra = {
               'request_id': self.request_id,
               'path': self.path,
               'method': self.method,
               **kwargs
           }
           if error:
               extra['error_type'] = type(error).__name__
               extra['error_message'] = str(error)

           self.logger.error(message, extra=extra)
   ```

**Step 2: Integrate Logging (1 hour)**
1. Update `backend/app.py`:
   ```python
   from logging_config import setup_logging

   # At startup
   @app.on_event("startup")
   async def startup_event():
       setup_logging(level="INFO")
       logging.info("Application starting up")
   ```

2. Update middleware to use structured logging:
   ```python
   from logging_config import RequestLogger

   @app.middleware("http")
   async def logging_middleware(request: Request, call_next):
       request_id = str(uuid.uuid4())
       request.state.request_id = request_id

       logger = RequestLogger(
           request_id=request_id,
           path=request.url.path,
           method=request.method
       )

       logger.log_info("Request started")

       start_time = time.time()
       response = await call_next(request)
       duration = time.time() - start_time

       logger.log_info(
           "Request completed",
           status_code=response.status_code,
           duration_ms=round(duration * 1000, 2)
       )

       return response
   ```

3. Use in services:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   # In methods:
   logger.info("Generating LLM response", extra={
       "model": self.model,
       "temperature": temperature,
       "max_tokens": max_tokens
   })
   ```

**Acceptance Criteria:**
- All logs output in JSON format
- Request ID propagated through request lifecycle
- Important operations logged with context
- Errors include stack traces in structured format
- Logs easily parseable by log aggregators

---

## Testing & Validation Checklist

After completing each phase, run these validation steps:

### Phase 1 Validation
- [ ] Frontend Connectors component doesn't crash or re-render infinitely
- [ ] WebSocket reconnects after backend restart (test 3 times)
- [ ] All API endpoints work with dependency injection
- [ ] No global service variables remain in routers
- [ ] `pytest` shows no import errors

### Phase 2 Validation
- [ ] Run `pytest --cov` - coverage > 60%
- [ ] All backend tests pass consistently (run 5 times)
- [ ] Frontend tests pass with `npm test`
- [ ] No flaky tests identified
- [ ] CI pipeline runs tests automatically

### Phase 3 Validation
- [ ] Rate limiting blocks after 100 requests in 60 seconds
- [ ] Loading spinners appear during all async operations
- [ ] Error boundary catches and displays errors gracefully
- [ ] Database queries under 100ms (test with 1000+ conversations)
- [ ] All API errors return consistent JSON format

### Phase 4 Validation
- [ ] Conversation search returns relevant results
- [ ] Document preview shows for supported file types
- [ ] All interactive elements accessible via keyboard
- [ ] Screen reader announces all state changes
- [ ] Keyboard shortcuts work (test all: Cmd+K, Cmd+N, Escape)

### Phase 5 Validation
- [ ] All public methods have docstrings
- [ ] No magic numbers remain (all in constants files)
- [ ] Logs output in valid JSON format
- [ ] Log aggregator can parse logs successfully
- [ ] Documentation generated successfully

---

## Maintenance & Monitoring

### After Implementation:
1. **Set up monitoring** (optional but recommended):
   - Add Prometheus metrics endpoint
   - Create Grafana dashboards
   - Set up alerts for error rates

2. **Document the changes**:
   - Update README.md with new features
   - Add CHANGELOG.md entry
   - Update API documentation

3. **Performance baseline**:
   - Measure response times under load
   - Document acceptable performance metrics
   - Set up performance regression tests

4. **User feedback**:
   - Create GitHub issue templates
   - Add feedback mechanism in UI
   - Document common issues and solutions

---

## Success Criteria Summary

The improvements are successfully implemented when:

✅ **Critical Issues Resolved:**
- No infinite re-renders in Connectors
- WebSocket reconnects automatically
- Dependency injection used throughout
- All tests pass consistently

✅ **High Priority Complete:**
- Test coverage > 60%
- Rate limiting enabled
- Error handling consistent
- Loading states on all async operations
- Basic accessibility implemented

✅ **Medium Priority Complete:**
- Conversation search works
- Document preview functional
- Full keyboard navigation
- Docstrings on all functions
- Constants centralized
- Structured logging active

✅ **Quality Metrics:**
- No TypeErrors or runtime errors
- API response times < 500ms (p95)
- Zero breaking changes to existing functionality
- All features work on Chrome, Firefox, Safari

---

## Notes for LLM Implementation

When executing this roadmap:

1. **Read before modifying**: Always read the entire file before making changes
2. **Test after each task**: Run tests after completing each task
3. **Commit frequently**: Make small, focused commits
4. **Handle errors gracefully**: If a task fails, log the error and continue with next task
5. **Ask for clarification**: If requirements are ambiguous, ask the user
6. **Document changes**: Update comments and docstrings as you go
7. **Validate assumptions**: Test edge cases and error conditions
8. **Keep backwards compatibility**: Don't break existing functionality

**Task Completion Verification:**
After each task, verify:
- Code runs without errors
- Tests pass (if applicable)
- Changes don't break existing features
- Documentation updated (if needed)

**If Stuck:**
- Check error messages carefully
- Review the detailed steps again
- Try a simpler approach
- Document the blocker for user review
