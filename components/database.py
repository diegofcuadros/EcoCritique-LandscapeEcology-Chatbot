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
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
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

def delete_article(article_id: int) -> bool:
    """Delete an article from the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        st.error(f"Error deleting article from database: {e}")
        return False
    finally:
        conn.close()

def update_article_status(article_id: int, is_active: bool) -> bool:
    """Update article active status"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE articles SET is_active = ? WHERE id = ?", 
            (is_active, article_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        st.error(f"Error updating article status: {e}")
        return False
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


# Assignment Questions Management Functions
def save_assignment_questions(article_id: int, assignment_title: str, questions_data: dict) -> int:
    """Save assignment questions for an article"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert assignment record
        cursor.execute("""
            INSERT INTO assignment_questions 
            (article_id, assignment_title, assignment_type, total_word_count, workflow_steps)
            VALUES (?, ?, ?, ?, ?)
        """, (
            article_id,
            assignment_title,
            questions_data.get('assignment_type', 'socratic_reading_analysis'),
            questions_data.get('total_word_count', '600-900 words'),
            json.dumps(questions_data.get('workflow_steps', []))
        ))
        
        assignment_id = cursor.lastrowid
        
        # Insert individual questions
        for question in questions_data.get('questions', []):
            cursor.execute("""
                INSERT INTO assignment_question_details
                (assignment_id, question_number, question_title, question_prompt, 
                 learning_objectives, required_evidence, word_target, bloom_level, key_concepts,
                 tutoring_prompts, evidence_guidance, complexity_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment_id,
                question.get('id', ''),
                question.get('title', ''),
                question.get('prompt', ''),
                json.dumps(question.get('learning_objectives', [])),
                question.get('required_evidence', ''),
                question.get('word_target', ''),
                question.get('bloom_level', ''),
                json.dumps(question.get('key_concepts', [])),
                json.dumps(question.get('tutoring_prompts', [])),
                question.get('evidence_guidance', ''),
                question.get('complexity_score', 0.5)
            ))
        
        conn.commit()
        return assignment_id
        
    except Exception as e:
        st.error(f"Error saving assignment questions: {e}")
        return 0
    finally:
        conn.close()


def get_assignment_questions(article_id: int) -> dict:
    """Get assignment questions for a specific article"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Get assignment info
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assignment_id, assignment_title, assignment_type, 
                   total_word_count, workflow_steps
            FROM assignment_questions
            WHERE article_id = ?
        """, (article_id,))
        
        assignment_result = cursor.fetchone()
        if not assignment_result:
            return {}
        
        assignment_id, title, assignment_type, word_count, workflow_steps = assignment_result
        
        # Get individual questions
        cursor.execute("""
            SELECT question_number, question_title, question_prompt, 
                   learning_objectives, required_evidence, word_target, 
                   bloom_level, key_concepts, tutoring_prompts, evidence_guidance, complexity_score
            FROM assignment_question_details
            WHERE assignment_id = ?
            ORDER BY question_number
        """, (assignment_id,))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'title': row[1],
                'prompt': row[2],
                'learning_objectives': json.loads(row[3]) if row[3] else [],
                'required_evidence': row[4],
                'word_target': row[5],
                'bloom_level': row[6],
                'key_concepts': json.loads(row[7]) if row[7] else [],
                'tutoring_prompts': json.loads(row[8]) if row[8] else [],
                'evidence_guidance': row[9] or '',
                'complexity_score': row[10] or 0.5
            })
        
        return {
            'assignment_id': assignment_id,
            'assignment_title': title,
            'assignment_type': assignment_type,
            'total_word_count': word_count,
            'workflow_steps': json.loads(workflow_steps) if workflow_steps else [],
            'questions': questions
        }
        
    except Exception as e:
        st.error(f"Error getting assignment questions: {e}")
        return {}
    finally:
        conn.close()


def update_student_assignment_progress(student_id: str, assignment_id: int, 
                                     current_question: str = None,
                                     completed_question: str = None,
                                     evidence_item: str = None) -> bool:
    """Update student progress on assignment"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get existing progress
        cursor.execute("""
            SELECT questions_completed, evidence_found
            FROM student_assignment_progress
            WHERE student_id = ? AND assignment_id = ?
        """, (student_id, assignment_id))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing progress
            questions_completed = json.loads(result[0]) if result[0] else []
            evidence_found = json.loads(result[1]) if result[1] else []
            
            if completed_question and completed_question not in questions_completed:
                questions_completed.append(completed_question)
            
            if evidence_item and evidence_item not in evidence_found:
                evidence_found.append(evidence_item)
            
            cursor.execute("""
                UPDATE student_assignment_progress
                SET current_question = ?, questions_completed = ?, 
                    evidence_found = ?, last_updated = ?
                WHERE student_id = ? AND assignment_id = ?
            """, (
                current_question or result[0],
                json.dumps(questions_completed),
                json.dumps(evidence_found),
                datetime.now().isoformat(),
                student_id, assignment_id
            ))
        else:
            # Create new progress record
            questions_completed = [completed_question] if completed_question else []
            evidence_found = [evidence_item] if evidence_item else []
            
            cursor.execute("""
                INSERT INTO student_assignment_progress
                (student_id, assignment_id, current_question, questions_completed, 
                 evidence_found, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id, assignment_id, current_question,
                json.dumps(questions_completed),
                json.dumps(evidence_found),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error updating assignment progress: {e}")
        return False
    finally:
        conn.close()


def get_student_assignment_progress(student_id: str, assignment_id: int) -> dict:
    """Get student's progress on a specific assignment"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT current_question, questions_completed, evidence_found, 
                   writing_readiness_score, last_updated
            FROM student_assignment_progress
            WHERE student_id = ? AND assignment_id = ?
        """, (student_id, assignment_id))
        
        result = cursor.fetchone()
        if not result:
            return {
                'current_question': None,
                'questions_completed': [],
                'evidence_found': [],
                'writing_readiness_score': 0,
                'last_updated': None
            }
        
        return {
            'current_question': result[0],
            'questions_completed': json.loads(result[1]) if result[1] else [],
            'evidence_found': json.loads(result[2]) if result[2] else [],
            'writing_readiness_score': result[3] or 0,
            'last_updated': result[4]
        }
        
    except Exception as e:
        st.error(f"Error getting student progress: {e}")
        return {}
    finally:
        conn.close()
