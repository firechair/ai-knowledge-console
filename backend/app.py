from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time, uuid, json, logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import documents, chat, connectors, settings
from services.vector_store import VectorStoreService
from middleware.error_handler import register_exception_handlers
from logging_config import setup_logging

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize services on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    logger = setup_logging(level="INFO")
    logger.info("Application starting up", version="1.0.0")
    
    # Startup: Initialize vector store
    app.state.vector_store = VectorStoreService()
    logger.info("Vector store initialized")
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Application shutting down")

app = FastAPI(
    title="AI Knowledge Console",
    description="RAG + External APIs unified AI assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Register custom exception handlers
register_exception_handlers(app)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

    # Rate limiting
    if cfg.rate_limit_enabled:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = cfg.rate_limit_window_sec
        limit = cfg.rate_limit_requests
        items = _requests.get(ip, [])
        items = [t for t in items if now - t < window]

        if len(items) >= limit:
            from starlette.responses import JSONResponse
            response = JSONResponse(
                {"detail": "Rate limit exceeded. Please try again later."},
                status_code=429
            )
            response.headers["X-Request-ID"] = rid
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(items[0] + window))
            response.headers["Retry-After"] = str(int(items[0] + window - now))
            return response

        items.append(now)
        _requests[ip] = items

    response = await call_next(request)
    duration = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = rid

    # Add rate limit headers to successful responses
    if cfg.rate_limit_enabled:
        ip = request.client.host if request.client else "unknown"
        items = _requests.get(ip, [])
        response.headers["X-RateLimit-Limit"] = str(cfg.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, cfg.rate_limit_requests - len(items)))
        if items:
            response.headers["X-RateLimit-Reset"] = str(int(items[0] + cfg.rate_limit_window_sec))

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
