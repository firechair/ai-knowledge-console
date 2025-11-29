import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ConversationService:
    """Service for managing conversation history with SQLite storage"""

    def __init__(self, db_path: str = "backend/conversations.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """
            )
            conn.commit()

    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (id) VALUES (?)", (conversation_id,)
            )
            conn.commit()

        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            # Create conversation if it doesn't exist
            conn.execute(
                "INSERT OR IGNORE INTO conversations (id) VALUES (?)",
                (conversation_id,),
            )
            # Add message
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content),
            )
            conn.commit()

    def get_history(
        self, conversation_id: str, limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation history (most recent first)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (conversation_id, limit),
            )
            messages = [dict(row) for row in cursor.fetchall()]

        # Reverse to get chronological order
        return list(reversed(messages))

    def clear_conversation(self, conversation_id: str):
        """Delete all messages in a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
            )
            conn.commit()

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM conversations WHERE id = ? LIMIT 1", (conversation_id,)
            )
            return cursor.fetchone() is not None
