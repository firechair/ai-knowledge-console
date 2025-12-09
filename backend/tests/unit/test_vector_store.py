"""
Unit tests for VectorStoreService.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np

from services.vector_store import VectorStoreService


@pytest.mark.unit
class TestVectorStoreService:
    """Test suite for VectorStoreService."""

    @patch('services.vector_store.get_settings')
    @patch('services.vector_store.SentenceTransformer')
    @patch('services.vector_store.chromadb.PersistentClient')
    def test_init(self, mock_chroma, mock_transformer, mock_settings):
        """Test VectorStoreService initialization."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        service = VectorStoreService()

        assert service.client == mock_client
        assert service.collection == mock_collection
        assert service.embedding_model is None  # Lazy loading - not loaded yet
        assert service.embedding_model_name == "test-model"
        mock_chroma.assert_called_once()
        # SentenceTransformer should NOT be called during init (lazy loading)
        mock_transformer.assert_not_called()

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_add_documents(self, mock_settings, mock_transformer, mock_chroma):
        """Test adding documents to vector store."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_model = Mock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_model.encode.return_value = mock_embeddings
        mock_transformer.return_value = mock_model

        service = VectorStoreService()

        chunks = ["First chunk", "Second chunk"]
        metadata = [
            {"filename": "test.txt", "chunk_index": 0},
            {"filename": "test.txt", "chunk_index": 1}
        ]

        result = service.add_documents(chunks, metadata)

        assert result == 2
        mock_model.encode.assert_called_once_with(chunks)
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[1]
        assert call_args["documents"] == chunks
        assert call_args["metadatas"] == metadata
        assert len(call_args["ids"]) == 2
        assert len(call_args["embeddings"]) == 2

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_search(self, mock_settings, mock_transformer, mock_chroma):
        """Test searching for relevant documents."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_model = Mock()
        mock_query_embedding = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = mock_query_embedding
        mock_transformer.return_value = mock_model

        # Mock search results
        mock_collection.query.return_value = {
            "documents": [["Result 1", "Result 2"]],
            "metadatas": [[{"filename": "doc1.txt"}, {"filename": "doc2.txt"}]],
            "distances": [[0.1, 0.2]]
        }

        service = VectorStoreService()
        results = service.search("test query", n_results=2)

        assert len(results) == 2
        assert results[0]["content"] == "Result 1"
        assert results[0]["metadata"]["filename"] == "doc1.txt"
        assert results[0]["score"] == 0.9  # 1 - 0.1
        assert results[1]["score"] == 0.8  # 1 - 0.2

        mock_model.encode.assert_called_once_with(["test query"])
        mock_collection.query.assert_called_once()

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_delete_document(self, mock_settings, mock_transformer, mock_chroma):
        """Test deleting a document."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        service = VectorStoreService()
        service.delete_document("test.txt")

        mock_collection.delete.assert_called_once_with(where={"filename": "test.txt"})

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_list_documents(self, mock_settings, mock_transformer, mock_chroma):
        """Test listing all documents."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        # Mock collection get() to return multiple chunks from different files
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "doc1.txt"},
                {"filename": "doc1.txt"},
                {"filename": "doc2.pdf"},
                {"filename": "doc3.txt"}
            ]
        }

        service = VectorStoreService()
        documents = service.list_documents()

        assert len(documents) == 3
        assert "doc1.txt" in documents
        assert "doc2.pdf" in documents
        assert "doc3.txt" in documents

        mock_collection.get.assert_called_once_with(include=["metadatas"])

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_list_documents_empty(self, mock_settings, mock_transformer, mock_chroma):
        """Test listing documents when collection is empty."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_collection.get.return_value = {"metadatas": []}

        service = VectorStoreService()
        documents = service.list_documents()

        assert documents == []

    @patch('services.vector_store.get_settings')
    @patch('services.vector_store.SentenceTransformer')
    @patch('services.vector_store.chromadb.PersistentClient')
    def test_reload_embedding_model(self, mock_chroma, mock_transformer, mock_settings):
        """Test reloading embedding model."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        # Create service - model not loaded yet (lazy loading)
        service = VectorStoreService()
        assert mock_transformer.call_count == 0  # Not called during init

        # Reload with different model - this triggers the first load
        service.reload_embedding_model("new-model")

        # Check that SentenceTransformer was called once (only in reload)
        assert mock_transformer.call_count == 1
        mock_transformer.assert_called_with("new-model")

    @patch('services.vector_store.chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('services.vector_store.get_settings')
    def test_search_no_results(self, mock_settings, mock_transformer, mock_chroma):
        """Test search with no results."""
        mock_settings.return_value.chroma_persist_dir = "/tmp/chroma"
        mock_settings.return_value.embedding_model = "test-model"

        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_model = Mock()
        mock_query_embedding = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = mock_query_embedding
        mock_transformer.return_value = mock_model

        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

        service = VectorStoreService()
        results = service.search("test query")

        assert results == []
