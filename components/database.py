import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Any
import os

DATABASE_PATH = "data/chatbot_interactions.db"

def initialize_database():
    """Initialize SQLite database for storing chat interactions"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            article_title TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_minutes REAL,
            message_count INTEGER,
            max_level_reached INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_order INTEGER,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            file_path TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            week_number INTEGER,
            learning_objectives TEXT,
            key_concepts TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            article_id INTEGER,
            session_count INTEGER DEFAULT 0,
            total_duration_minutes REAL DEFAULT 0,
            average_level_reached REAL DEFAULT 0,
            last_interaction TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_chat_session(session_id: str, user_id: str, user_type: str, 
                     messages: List[Dict], article_title: str = "",
                     duration_minutes: float = 0, max_level: int = 1):
    """Save a complete chat session to the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert session record
        cursor.execute("""
            INSERT OR REPLACE INTO chat_sessions 
            (session_id, user_id, user_type, article_title, start_time, end_time, 
             duration_minutes, message_count, max_level_reached)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
            user_id or "unknown_user", 
            user_type, 
            article_title,
            messages[0]["timestamp"] if messages else datetime.now().isoformat(),
            messages[-1]["timestamp"] if messages else datetime.now().isoformat(),
            duration_minutes, len(messages), max_level
        ))
        
        # Clear existing messages for this session
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",))
        
        # Insert messages
        for i, message in enumerate(messages):
            cursor.execute("""
                INSERT INTO chat_messages 
                (session_id, role, content, timestamp, message_order)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                message["role"], message["content"], 
                message["timestamp"], i
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error saving chat session: {e}")
        return False
    finally:
        conn.close()

def get_chat_sessions(user_id: str | None = None, limit: int = 100) -> pd.DataFrame:
    """Retrieve chat sessions from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = """
        SELECT session_id, user_id, user_type, article_title, 
               start_time, duration_minutes, message_count, max_level_reached,
               created_at
        FROM chat_sessions
    """
    
    params = []
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error retrieving chat sessions: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_chat_messages(session_id: str) -> List[Dict]:
    """Retrieve messages for a specific chat session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT role, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY message_order
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        return messages
        
    except Exception as e:
        st.error(f"Error retrieving messages: {e}")
        return []
    finally:
        conn.close()

def save_article(title: str, file_path: str, week_number: int, 
                learning_objectives: str = "", key_concepts: str = ""):
    """Save article information to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO articles 
            (title, file_path, week_number, learning_objectives, key_concepts)
            VALUES (?, ?, ?, ?, ?)
        """, (title, file_path, week_number, learning_objectives, key_concepts))
        
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        st.error(f"Error saving article: {e}")
        return None
    finally:
        conn.close()

def get_articles(active_only: bool = True) -> pd.DataFrame:
    """Retrieve articles from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = """
        SELECT id, title, file_path, week_number, learning_objectives, 
               key_concepts, upload_date, is_active
        FROM articles
    """
    
    if active_only:
        query += " WHERE is_active = 1"
    
    query += " ORDER BY week_number, upload_date DESC"
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error retrieving articles: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_student_analytics() -> Dict[str, Any]:
    """Get analytics data for professor dashboard"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Total students
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM chat_sessions WHERE user_type = 'Student'")
        total_students = cursor.fetchone()[0]
        
        # Average session duration
        cursor.execute("SELECT AVG(duration_minutes) FROM chat_sessions WHERE user_type = 'Student'")
        avg_duration = cursor.fetchone()[0] or 0
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM chat_sessions WHERE user_type = 'Student'")
        total_sessions = cursor.fetchone()[0]
        
        # Active students (last 7 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) 
            FROM chat_sessions 
            WHERE user_type = 'Student' 
            AND created_at > datetime('now', '-7 days')
        """)
        active_students = cursor.fetchone()[0]
        
        return {
            "total_students": total_students,
            "avg_duration": round(avg_duration, 1),
            "total_sessions": total_sessions,
            "active_students": active_students
        }
        
    except Exception as e:
        st.error(f"Error getting analytics: {e}")
        return {
            "total_students": 0,
            "avg_duration": 0,
            "total_sessions": 0,
            "active_students": 0
        }
    finally:
        conn.close()

def export_interactions_csv(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    """Export chat interactions to CSV format"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = """
        SELECT s.session_id, s.user_id, s.article_title, s.start_time,
               s.duration_minutes, s.message_count, s.max_level_reached,
               m.role, m.content, m.timestamp
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON s.session_id = m.session_id
        WHERE s.user_type = 'Student'
    """
    
    params = []
    if start_date:
        query += " AND s.start_time >= ?"
        params.append(start_date)
    if end_date:
        query += " AND s.start_time <= ?"
        params.append(end_date)
    
    query += " ORDER BY s.start_time DESC, m.message_order"
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
