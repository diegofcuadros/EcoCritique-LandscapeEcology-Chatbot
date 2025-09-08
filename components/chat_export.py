"""
Chat Export System - Export student conversations to text and markdown formats
"""

import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import io
from components.database import DATABASE_PATH

class ChatExportSystem:
    """Export student chat conversations to various text formats"""
    
    def __init__(self):
        self.database_path = DATABASE_PATH
    
    def export_individual_chat_transcript(self, session_id: str, format_type: str = "markdown") -> str:
        """Export a single chat session to text or markdown format"""
        
        conn = sqlite3.connect(self.database_path)
        
        try:
            # Get session info
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.user_id, s.article_title, s.start_time, s.duration_minutes,
                       s.message_count, s.max_level_reached
                FROM chat_sessions s
                WHERE s.session_id = ?
            """, (session_id,))
            
            session_info = cursor.fetchone()
            if not session_info:
                return "Session not found."
            
            user_id, article_title, start_time, duration, msg_count, max_level = session_info
            
            # Get messages
            cursor.execute("""
                SELECT role, content, timestamp
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY message_order
            """, (session_id,))
            
            messages = cursor.fetchall()
            
            if not messages:
                return "No messages found for this session."
            
            # Format the transcript
            if format_type.lower() == "markdown":
                return self._format_markdown_transcript(session_info, messages)
            else:  # text format
                return self._format_text_transcript(session_info, messages)
                
        except Exception as e:
            return f"Error exporting transcript: {str(e)}"
        finally:
            conn.close()
    
    def export_student_all_chats(self, student_id: str, format_type: str = "markdown") -> str:
        """Export all chat sessions for a specific student"""
        
        conn = sqlite3.connect(self.database_path)
        
        try:
            # Get all sessions for the student
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, article_title, start_time, duration_minutes,
                       message_count, max_level_reached
                FROM chat_sessions
                WHERE user_id = ? AND user_type = 'Student'
                ORDER BY start_time DESC
            """, (student_id,))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                return f"No chat sessions found for student: {student_id}"
            
            # Export each session
            all_transcripts = []
            
            if format_type.lower() == "markdown":
                all_transcripts.append(f"# Complete Chat History for {student_id}\n")
                all_transcripts.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                all_transcripts.append(f"**Total Sessions:** {len(sessions)}\n\n")
                all_transcripts.append("---\n\n")
            else:
                all_transcripts.append(f"COMPLETE CHAT HISTORY FOR {student_id.upper()}\n")
                all_transcripts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                all_transcripts.append(f"Total Sessions: {len(sessions)}\n\n")
                all_transcripts.append("="*60 + "\n\n")
            
            for session_id, article_title, start_time, duration, msg_count, max_level in sessions:
                transcript = self.export_individual_chat_transcript(session_id, format_type)
                all_transcripts.append(transcript)
                all_transcripts.append("\n\n")
                
                if format_type.lower() == "markdown":
                    all_transcripts.append("---\n\n")
                else:
                    all_transcripts.append("="*60 + "\n\n")
            
            return "".join(all_transcripts)
            
        except Exception as e:
            return f"Error exporting student chats: {str(e)}"
        finally:
            conn.close()
    
    def export_class_summary(self, article_title: str = None, format_type: str = "markdown") -> str:
        """Export a summary of all student interactions"""
        
        conn = sqlite3.connect(self.database_path)
        
        try:
            # Build query
            query = """
                SELECT s.user_id, s.article_title, s.start_time, s.duration_minutes,
                       s.message_count, s.max_level_reached, COUNT(*) as session_count
                FROM chat_sessions s
                WHERE s.user_type = 'Student'
            """
            
            params = []
            if article_title:
                query += " AND s.article_title = ?"
                params.append(article_title)
            
            query += """
                GROUP BY s.user_id, s.article_title
                ORDER BY s.user_id, s.start_time DESC
            """
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            sessions = cursor.fetchall()
            
            if not sessions:
                return "No student sessions found."
            
            # Create summary
            if format_type.lower() == "markdown":
                return self._format_markdown_class_summary(sessions, article_title)
            else:
                return self._format_text_class_summary(sessions, article_title)
                
        except Exception as e:
            return f"Error creating class summary: {str(e)}"
        finally:
            conn.close()
    
    def _format_markdown_transcript(self, session_info: tuple, messages: List[tuple]) -> str:
        """Format a single chat transcript as markdown"""
        
        user_id, article_title, start_time, duration, msg_count, max_level = session_info
        
        transcript = []
        transcript.append(f"## Chat Transcript: {user_id}")
        transcript.append(f"**Article:** {article_title}")
        transcript.append(f"**Date:** {start_time}")
        transcript.append(f"**Duration:** {duration:.1f} minutes")
        transcript.append(f"**Messages:** {msg_count}")
        transcript.append(f"**Max Cognitive Level Reached:** {max_level}/4")
        transcript.append("\n### Conversation\n")
        
        for role, content, timestamp in messages:
            if role == 'student':
                transcript.append(f"**🧑‍🎓 Student:** {content}\n")
            else:
                transcript.append(f"**🤖 AI Tutor:** {content}\n")
        
        return "\n".join(transcript)
    
    def _format_text_transcript(self, session_info: tuple, messages: List[tuple]) -> str:
        """Format a single chat transcript as plain text"""
        
        user_id, article_title, start_time, duration, msg_count, max_level = session_info
        
        transcript = []
        transcript.append(f"CHAT TRANSCRIPT: {user_id.upper()}")
        transcript.append(f"Article: {article_title}")
        transcript.append(f"Date: {start_time}")
        transcript.append(f"Duration: {duration:.1f} minutes")
        transcript.append(f"Messages: {msg_count}")
        transcript.append(f"Max Cognitive Level Reached: {max_level}/4")
        transcript.append("\nCONVERSATION:")
        transcript.append("-" * 40)
        
        for role, content, timestamp in messages:
            if role == 'student':
                transcript.append(f"\nSTUDENT: {content}")
            else:
                transcript.append(f"\nAI TUTOR: {content}")
        
        transcript.append("\n" + "-" * 40)
        
        return "\n".join(transcript)
    
    def _format_markdown_class_summary(self, sessions: List[tuple], article_filter: str = None) -> str:
        """Format class summary as markdown"""
        
        summary = []
        
        if article_filter:
            summary.append(f"# Class Summary - {article_filter}")
        else:
            summary.append("# Class Summary - All Articles")
        
        summary.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"**Total Student Sessions:** {len(sessions)}")
        summary.append("\n## Student Overview\n")
        
        summary.append("| Student | Article | Sessions | Duration (min) | Max Level | Last Activity |")
        summary.append("|---------|---------|----------|----------------|-----------|---------------|")
        
        for user_id, article_title, start_time, duration, msg_count, max_level, session_count in sessions:
            summary.append(f"| {user_id} | {article_title[:30]}... | {session_count} | {duration:.1f} | {max_level}/4 | {start_time} |")
        
        # Summary statistics
        total_sessions = sum(row[6] for row in sessions)
        avg_duration = sum(row[3] for row in sessions) / len(sessions) if sessions else 0
        avg_max_level = sum(row[5] for row in sessions) / len(sessions) if sessions else 0
        
        summary.append(f"\n## Class Statistics")
        summary.append(f"- **Total Students:** {len(set(row[0] for row in sessions))}")
        summary.append(f"- **Total Sessions:** {total_sessions}")
        summary.append(f"- **Average Session Duration:** {avg_duration:.1f} minutes")
        summary.append(f"- **Average Max Level Reached:** {avg_max_level:.1f}/4")
        
        return "\n".join(summary)
    
    def _format_text_class_summary(self, sessions: List[tuple], article_filter: str = None) -> str:
        """Format class summary as plain text"""
        
        summary = []
        
        if article_filter:
            summary.append(f"CLASS SUMMARY - {article_filter.upper()}")
        else:
            summary.append("CLASS SUMMARY - ALL ARTICLES")
        
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total Student Sessions: {len(sessions)}")
        summary.append("\nSTUDENT OVERVIEW:")
        summary.append("-" * 50)
        
        for user_id, article_title, start_time, duration, msg_count, max_level, session_count in sessions:
            summary.append(f"\nStudent: {user_id}")
            summary.append(f"  Article: {article_title}")
            summary.append(f"  Sessions: {session_count}")
            summary.append(f"  Duration: {duration:.1f} minutes")
            summary.append(f"  Max Level: {max_level}/4")
            summary.append(f"  Last Activity: {start_time}")
        
        # Summary statistics
        total_sessions = sum(row[6] for row in sessions)
        avg_duration = sum(row[3] for row in sessions) / len(sessions) if sessions else 0
        avg_max_level = sum(row[5] for row in sessions) / len(sessions) if sessions else 0
        
        summary.append(f"\nCLASS STATISTICS:")
        summary.append(f"Total Students: {len(set(row[0] for row in sessions))}")
        summary.append(f"Total Sessions: {total_sessions}")
        summary.append(f"Average Session Duration: {avg_duration:.1f} minutes")
        summary.append(f"Average Max Level Reached: {avg_max_level:.1f}/4")
        
        return "\n".join(summary)
    
    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all available chat sessions"""
        
        conn = sqlite3.connect(self.database_path)
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, user_id, article_title, start_time, duration_minutes, message_count
                FROM chat_sessions
                WHERE user_type = 'Student'
                ORDER BY start_time DESC
            """)
            
            sessions = cursor.fetchall()
            
            return [
                {
                    "session_id": row[0],
                    "user_id": row[1],
                    "article_title": row[2],
                    "start_time": row[3],
                    "duration_minutes": row[4],
                    "message_count": row[5],
                    "display_name": f"{row[1]} - {row[2][:30]}... ({row[3]})"
                }
                for row in sessions
            ]
            
        except Exception as e:
            st.error(f"Error getting sessions: {e}")
            return []
        finally:
            conn.close()
    
    def get_student_list(self) -> List[str]:
        """Get list of all students with chat sessions"""
        
        conn = sqlite3.connect(self.database_path)
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT user_id
                FROM chat_sessions
                WHERE user_type = 'Student'
                ORDER BY user_id
            """)
            
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            st.error(f"Error getting student list: {e}")
            return []
        finally:
            conn.close()