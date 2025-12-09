import sqlite3
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ConversationService:
    """Service for managing conversation history with SQLite storage"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv("CONVERSATIONS_DB_PATH", "backend/conversations.db")
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    title TEXT
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

            try:
                cols = [r[1] for r in conn.execute("PRAGMA table_info(conversations)").fetchall()]
                if "title" not in cols:
                    conn.execute("ALTER TABLE conversations ADD COLUMN title TEXT")
                    conn.commit()
            except Exception:
                pass

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

    def list_conversations(self) -> List[Dict]:
        """List all conversations with metadata and last message preview"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT c.id, c.created_at, c.title,
                       (SELECT content FROM messages m WHERE m.conversation_id = c.id ORDER BY m.created_at DESC LIMIT 1) AS last_message,
                       (SELECT created_at FROM messages m WHERE m.conversation_id = c.id ORDER BY m.created_at DESC LIMIT 1) AS last_message_at
                FROM conversations c
                ORDER BY c.created_at DESC
                """
            )
            rows = [dict(row) for row in cursor.fetchall()]
        # Add preview field truncated
        for r in rows:
            lm = r.get("last_message") or ""
            r["last_message_preview"] = (lm[:140] + ("…" if len(lm) > 140 else "")) if lm else ""
            if not r.get("title"):
                r["title"] = r["last_message_preview"] or r["id"]
        return rows

    def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Return full message history for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_conversation(self, conversation_id: str):
        """Delete conversation and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()

    def delete_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.commit()

    def set_title(self, conversation_id: str, title: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conversation_id))
            conn.commit()
