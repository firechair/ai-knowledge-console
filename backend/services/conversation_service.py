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
            
            # Add indexes for performance
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

    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search conversations by message content.
        
        Args:
            query: Search term to find in message content
            limit: Maximum number of results to return
            
        Returns:
            List of conversations with matching content, including preview
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT DISTINCT
                    c.id,
                    c.created_at,
                    m.content as preview
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.content LIKE ?
                ORDER BY c.created_at DESC
                LIMIT ?
            """,
                (f"%{query}%", limit),
            )

            results = []
            for row in cursor.fetchall():
                preview = row[2]
                results.append({
                    "id": row[0],
                    "created_at": row[1],
                    "preview": preview[:100] if preview else "New Conversation",  # First 100 chars
                    "title": preview[:50] if preview else "New Conversation"  # First 50 chars for title
                })

            return results

    def list_conversations(self, limit: int = 50) -> List[Dict]:
        """
        List all conversations with preview from first user message.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations ordered by creation date (newest first)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
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
            """,
                (limit,),
            )

            results = []
            for row in cursor.fetchall():
                first_msg = row[2]
                results.append({
                    "id": row[0],
                    "created_at": row[1],
                    "title": first_msg[:50] if first_msg else "New Conversation",
                    "preview": first_msg[:100] if first_msg else "New Conversation"
                })

            return results
