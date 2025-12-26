import chromadb
from chromadb.config import Settings
from typing import List, Dict
import uuid
from config import get_settings

class VectorStoreService:
    def __init__(self):
        settings = get_settings()
        # Initialize ChromaDB (fast, local)
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        # Defer loading the embedding model to first use to avoid blocking app startup
        self.embedding_model = None
        self.embedding_model_name = settings.embedding_model

    def reload_embedding_model(self, model_name: str):
        # Lazy reload
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_model_name = model_name

    def _ensure_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
    
    def add_documents(self, chunks: List[str], metadata: List[Dict]) -> int:
        """Add document chunks to vector store"""
        self._ensure_model()
        embeddings = self.embedding_model.encode(chunks).tolist()
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids
        )
        return len(chunks)
    
    def search(self, query: str, n_results: int = 5, file_filters: List[str] = None) -> List[Dict]:
        """Search for relevant chunks"""
        self._ensure_model()
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        where_clause = None
        if file_filters:
            if len(file_filters) == 1:
                where_clause = {"filename": file_filters[0]}
            else:
                where_clause = {"filename": {"$in": file_filters}}
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"]:
            return []

        return [
            {
                "content": doc,
                "metadata": meta,
                "score": 1 - dist  # Convert distance to similarity
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def delete_document(self, filename: str):
        """Delete all chunks from a document"""
        self.collection.delete(where={"filename": filename})
    
    def list_documents(self) -> List[str]:
        """List all unique document names"""
        results = self.collection.get(include=["metadatas"])
        filenames = set(m.get("filename", "unknown") for m in results["metadatas"])
        return list(filenames)
