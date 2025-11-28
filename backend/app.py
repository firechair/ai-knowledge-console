from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time, uuid, json, logging

from routers import documents, chat, connectors, settings
from services.vector_store import VectorStoreService

# Initialize services on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize vector store
    app.state.vector_store = VectorStoreService()
    yield
    # Shutdown: Cleanup if needed

app = FastAPI(
    title="AI Knowledge Console",
    description="RAG + External APIs unified AI assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
from config import get_settings
cfg = get_settings()
origins = [o.strip() for o in cfg.allowed_origins.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.INFO)
_requests = {}

@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    rid = str(uuid.uuid4())
    start = time.time()
    if cfg.rate_limit_enabled:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = cfg.rate_limit_window_sec
        limit = cfg.rate_limit_requests
        items = _requests.get(ip, [])
        items = [t for t in items if now - t < window]
        if len(items) >= limit:
            from starlette.responses import JSONResponse
            return JSONResponse({"detail": "rate limit"}, status_code=429)
        items.append(now)
        _requests[ip] = items
    response = await call_next(request)
    duration = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = rid
    log = {
        "request_id": rid,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration,
    }
    logger.info(json.dumps(log))
    return response

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
