from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import documents, chat, connectors
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
