"""
Database Module
Manages conversation history and session data using SQLite.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDatabase:
    """
    SQLite database for managing conversation history and user sessions.
    """
    
    def __init__(self, db_path: str = "chatbot.db"):
        """
        Initialize the database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Create database and tables if they don't exist"""
        try:
            # Special handling for in-memory database
            if self.db_path == ":memory:":
                conn = sqlite3.connect(self.db_path)
                conn.execute("PRAGMA journal_mode=WAL")
            else:
                conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_info TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    retrieved_docs TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    rating INTEGER,
                    feedback_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def create_session(self, session_id: str, user_info: Dict[str, Any] = None) -> bool:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            user_info: Optional user information
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_info_json = json.dumps(user_info) if user_info else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, user_info)
                VALUES (?, ?)
            ''', (session_id, user_info_json))
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def add_conversation(self, session_id: str, user_message: str,
                        assistant_response: str, retrieved_docs: List[Dict] = None,
                        confidence_score: float = None) -> bool:
        """
        Add a conversation turn to the database.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_response: Chatbot's response
            retrieved_docs: Documents retrieved for this conversation
            confidence_score: Confidence score of the response
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            retrieved_docs_json = json.dumps(retrieved_docs) if retrieved_docs else None
            
            cursor.execute('''
                INSERT INTO conversations
                (session_id, user_message, assistant_response, retrieved_docs, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_message, assistant_response, retrieved_docs_json, confidence_score))
            
            # Update session's updated_at timestamp
            cursor.execute('''
                UPDATE sessions SET updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error adding conversation: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of recent conversations to retrieve
        
        Returns:
            List of conversation records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            conversations = []
            
            for row in rows:
                conv = dict(row)
                if conv['retrieved_docs']:
                    conv['retrieved_docs'] = json.loads(conv['retrieved_docs'])
                conversations.append(conv)
            
            conn.close()
            return list(reversed(conversations))  # Return in chronological order
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                session = dict(row)
                if session['user_info']:
                    session['user_info'] = json.loads(session['user_info'])
                return session
            return None
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving session: {e}")
            return None
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a single conversation.
        
        Args:
            conversation_id: ID of conversation to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete associated feedback
            cursor.execute('DELETE FROM feedback WHERE conversation_id = ?', (conversation_id,))
            
            # Delete conversation
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    def clear_session_history(self, session_id: str) -> bool:
        """
        Clear all conversations for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all conversation IDs for this session
            cursor.execute('SELECT id FROM conversations WHERE session_id = ?', (session_id,))
            conv_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete feedback for these conversations
            for conv_id in conv_ids:
                cursor.execute('DELETE FROM feedback WHERE conversation_id = ?', (conv_id,))
            
            # Delete conversations
            cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error clearing session history: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts of sessions and conversations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sessions')
            session_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversation_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_sessions": session_count,
                "total_conversations": conversation_count
            }
        
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_sessions": 0, "total_conversations": 0}
