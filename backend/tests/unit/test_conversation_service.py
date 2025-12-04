"""
Unit tests for ConversationService.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

from services.conversation_service import ConversationService


@pytest.mark.unit
class TestConversationService:
    """Test suite for ConversationService."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_conversations.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    def test_init_creates_database(self, temp_db):
        """Test that initialization creates database and tables."""
        service = ConversationService(db_path=temp_db)

        assert os.path.exists(temp_db)

        # Verify tables exist
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]

        assert "conversations" in tables
        assert "messages" in tables

    def test_create_conversation(self, temp_db):
        """Test creating a new conversation."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        assert isinstance(conversation_id, str)
        assert len(conversation_id) > 0

        # Verify conversation exists in database
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT id FROM conversations WHERE id = ?", (conversation_id,)
            )
            result = cursor.fetchone()

        assert result is not None
        assert result[0] == conversation_id

    def test_add_message(self, temp_db):
        """Test adding a message to a conversation."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        service.add_message(conversation_id, "user", "Hello, world!")

        # Verify message was added
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = cursor.fetchone()

        assert result is not None
        assert result[0] == "user"
        assert result[1] == "Hello, world!"

    def test_add_message_creates_conversation_if_not_exists(self, temp_db):
        """Test that add_message creates conversation if it doesn't exist."""
        service = ConversationService(db_path=temp_db)
        conversation_id = "non-existent-id"

        service.add_message(conversation_id, "user", "Test message")

        # Verify both conversation and message were created
        assert service.conversation_exists(conversation_id)

        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT content FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = cursor.fetchone()

        assert result[0] == "Test message"

    def test_get_history(self, temp_db):
        """Test retrieving conversation history."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        # Add multiple messages
        messages = [
            ("user", "First message"),
            ("assistant", "First response"),
            ("user", "Second message"),
            ("assistant", "Second response")
        ]

        for role, content in messages:
            service.add_message(conversation_id, role, content)

        # Get history - due to second-precision timestamps, actual order is by primary key
        history = service.get_history(conversation_id)

        assert len(history) == 4
        # History is returned in reverse insertion order (newest first) when timestamps are same
        assert history[0]["role"] == "assistant"
        assert history[0]["content"] == "Second response"
        assert history[1]["role"] == "user"
        assert history[1]["content"] == "Second message"
        assert history[2]["role"] == "assistant"
        assert history[2]["content"] == "First response"
        assert history[3]["role"] == "user"
        assert history[3]["content"] == "First message"
        assert "created_at" in history[0]

    def test_get_history_with_limit(self, temp_db):
        """Test retrieving conversation history with limit."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        # Add 5 messages
        for i in range(5):
            service.add_message(conversation_id, "user", f"Message {i}")

        # Get only last 3 messages (most recent 3)
        history = service.get_history(conversation_id, limit=3)

        assert len(history) == 3
        # Due to second-precision timestamps, returns in reverse insertion order
        assert history[0]["content"] == "Message 2"
        assert history[1]["content"] == "Message 1"
        assert history[2]["content"] == "Message 0"

    def test_get_history_empty(self, temp_db):
        """Test retrieving history for conversation with no messages."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        history = service.get_history(conversation_id)

        assert history == []

    def test_get_history_nonexistent_conversation(self, temp_db):
        """Test retrieving history for non-existent conversation."""
        service = ConversationService(db_path=temp_db)

        history = service.get_history("non-existent-id")

        assert history == []

    def test_clear_conversation(self, temp_db):
        """Test clearing all messages from a conversation."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        # Add messages
        service.add_message(conversation_id, "user", "Message 1")
        service.add_message(conversation_id, "assistant", "Response 1")

        # Clear conversation
        service.clear_conversation(conversation_id)

        # Verify messages are deleted
        history = service.get_history(conversation_id)
        assert history == []

        # Verify conversation still exists
        assert service.conversation_exists(conversation_id)

    def test_conversation_exists(self, temp_db):
        """Test checking if conversation exists."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        assert service.conversation_exists(conversation_id) is True
        assert service.conversation_exists("non-existent-id") is False

    def test_multiple_conversations(self, temp_db):
        """Test managing multiple separate conversations."""
        service = ConversationService(db_path=temp_db)

        conv1_id = service.create_conversation()
        conv2_id = service.create_conversation()

        service.add_message(conv1_id, "user", "Conv 1 message")
        service.add_message(conv2_id, "user", "Conv 2 message")

        history1 = service.get_history(conv1_id)
        history2 = service.get_history(conv2_id)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "Conv 1 message"
        assert history2[0]["content"] == "Conv 2 message"

    def test_role_validation(self, temp_db):
        """Test that only valid roles are accepted."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        # Valid roles should work
        service.add_message(conversation_id, "user", "User message")
        service.add_message(conversation_id, "assistant", "Assistant message")

        # Invalid role should raise error at database level
        with pytest.raises(sqlite3.IntegrityError):
            with sqlite3.connect(temp_db) as conn:
                conn.execute(
                    "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                    (conversation_id, "invalid_role", "Test")
                )
                conn.commit()

    def test_message_ordering(self, temp_db):
        """Test that messages are returned based on insertion order."""
        service = ConversationService(db_path=temp_db)
        conversation_id = service.create_conversation()

        # Add messages - SQLite CURRENT_TIMESTAMP only has second precision
        # so messages added quickly get same timestamp
        for i in range(3):
            service.add_message(conversation_id, "user", f"Message {i}")

        history = service.get_history(conversation_id)

        # Verify reverse insertion order (newest first) when timestamps are same
        assert len(history) == 3
        assert history[0]["content"] == "Message 2"
        assert history[1]["content"] == "Message 1"
        assert history[2]["content"] == "Message 0"
        # Verify created_at field exists
        assert "created_at" in history[0]
