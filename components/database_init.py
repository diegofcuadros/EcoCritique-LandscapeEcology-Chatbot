"""
Database Initialization - Ensure all required tables exist with correct schema
"""

import sqlite3
import streamlit as st
import os

def initialize_database():
    """Initialize all required database tables"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/chatbot_interactions.db')
    cursor = conn.cursor()
    
    try:
        # Core chat tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_type TEXT NOT NULL,
                article_title TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes REAL DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                max_level_reached INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_order INTEGER,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        """)
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                week_number INTEGER,
                file_path TEXT,
                learning_objectives TEXT,
                is_active BOOLEAN DEFAULT 1,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Student progress tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_progress (
                student_id TEXT PRIMARY KEY,
                current_level INTEGER DEFAULT 1,
                total_interactions INTEGER DEFAULT 0,
                badges_earned TEXT DEFAULT '[]',
                concepts_explored TEXT DEFAULT '[]',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Peer insights
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peer_insights (
                insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                article_title TEXT,
                cognitive_level INTEGER,
                upvotes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT 0
            )
        """)
        
        # Concept connections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concept_connections (
                connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                concept_from TEXT,
                concept_to TEXT,
                article_title TEXT,
                connection_strength REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Assessment quality tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubric_evaluations (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                session_id TEXT,
                article_title TEXT,
                depth_score REAL,
                integration_score REAL,
                question_score REAL,
                consistency_score REAL,
                progression_score REAL,
                total_score REAL,
                suggested_grade TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                message_id INTEGER,
                thoughtfulness_score REAL,
                critical_thinking_present BOOLEAN,
                synthesis_present BOOLEAN,
                word_count INTEGER,
                question_complexity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                week_start DATE,
                week_end DATE,
                sessions_completed INTEGER,
                avg_quality_score REAL,
                cognitive_progress TEXT,
                strengths TEXT,
                areas_for_improvement TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()

def check_database_health():
    """Check if database exists and has all required tables"""
    
    if not os.path.exists('data/chatbot_interactions.db'):
        return False, "Database file does not exist"
    
    conn = sqlite3.connect('data/chatbot_interactions.db')
    cursor = conn.cursor()
    
    required_tables = [
        'chat_sessions', 'chat_messages', 'articles', 'student_progress',
        'peer_insights', 'concept_connections', 'rubric_evaluations',
        'quality_metrics', 'weekly_reports'
    ]
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            return False, f"Missing tables: {', '.join(missing_tables)}"
        
        return True, "Database is healthy"
        
    except Exception as e:
        return False, f"Error checking database: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    # Can be run standalone to initialize database
    success = initialize_database()
    if success:
        print("Database initialized successfully!")
    else:
        print("Database initialization failed!")