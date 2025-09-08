"""
Student Engagement Module - Visual Progress, Achievements, and Peer Learning
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import sqlite3
from datetime import datetime
import json
import random
from components.database import DATABASE_PATH

class StudentEngagementSystem:
    def __init__(self):
        self.cognitive_levels = {
            1: {"name": "Comprehension", "icon": "🌱", "color": "#90EE90", "threshold": 2},
            2: {"name": "Analysis", "icon": "🔍", "color": "#87CEEB", "threshold": 4},
            3: {"name": "Synthesis", "icon": "🧩", "color": "#DDA0DD", "threshold": 6},
            4: {"name": "Evaluation", "icon": "💡", "color": "#FFD700", "threshold": 8}
        }
        
        self.achievement_badges = {
            "first_insight": {"name": "First Insight", "icon": "🌟", "description": "Asked your first thoughtful question"},
            "deep_thinker": {"name": "Deep Thinker", "icon": "🧠", "description": "Reached evaluation level"},
            "concept_connector": {"name": "Concept Connector", "icon": "🔗", "description": "Connected 3+ concepts"},
            "persistent_scholar": {"name": "Persistent Scholar", "icon": "📚", "description": "Engaged for 30+ minutes"},
            "critical_analyst": {"name": "Critical Analyst", "icon": "🎯", "description": "Challenged assumptions"},
            "synthesis_master": {"name": "Synthesis Master", "icon": "🏆", "description": "Synthesized ideas from multiple sources"}
        }
        
        self.initialize_engagement_tables()
    
    def initialize_engagement_tables(self):
        """Create tables for engagement tracking"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if student_progress table exists with correct schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_progress'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if it has the correct columns
            cursor.execute("PRAGMA table_info(student_progress)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # If missing required columns, drop and recreate
            required_columns = ['student_id', 'current_level', 'total_interactions', 'badges_earned', 'concepts_explored']
            if not all(col in column_names for col in required_columns):
                cursor.execute("DROP TABLE IF EXISTS student_progress")
                cursor.execute("""
                    CREATE TABLE student_progress (
                        student_id TEXT PRIMARY KEY,
                        current_level INTEGER DEFAULT 1,
                        total_interactions INTEGER DEFAULT 0,
                        badges_earned TEXT DEFAULT '[]',
                        concepts_explored TEXT DEFAULT '[]',
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        else:
            # Create the table
            cursor.execute("""
                CREATE TABLE student_progress (
                    student_id TEXT PRIMARY KEY,
                    current_level INTEGER DEFAULT 1,
                    total_interactions INTEGER DEFAULT 0,
                    badges_earned TEXT DEFAULT '[]',
                    concepts_explored TEXT DEFAULT '[]',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Peer insights - best questions
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
        
        conn.commit()
        conn.close()
    
    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get current progress for a student"""
        # Ensure tables exist
        self.initialize_engagement_tables()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT current_level, total_interactions, badges_earned, concepts_explored
                FROM student_progress
                WHERE student_id = ?
            """, (student_id,))
            
            result = cursor.fetchone()
        except sqlite3.OperationalError:
            # Table doesn't exist, create it and retry
            self.initialize_engagement_tables()
            cursor.execute("""
                SELECT current_level, total_interactions, badges_earned, concepts_explored
                FROM student_progress
                WHERE student_id = ?
            """, (student_id,))
            result = cursor.fetchone()
        finally:
            conn.close()
        
        if result:
            return {
                "current_level": result[0],
                "total_interactions": result[1],
                "badges_earned": json.loads(result[2]),
                "concepts_explored": json.loads(result[3])
            }
        else:
            # Initialize new student
            self.initialize_student(student_id)
            return {
                "current_level": 1,
                "total_interactions": 0,
                "badges_earned": [],
                "concepts_explored": []
            }
    
    def initialize_student(self, student_id: str):
        """Initialize a new student's progress"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO student_progress 
            (student_id, current_level, total_interactions, badges_earned, concepts_explored)
            VALUES (?, 1, 0, '[]', '[]')
        """, (student_id,))
        
        conn.commit()
        conn.close()
    
    def update_progress(self, student_id: str, message_count: int, concepts: List[str] = None):
        """Update student's cognitive level and progress"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get current progress
        progress = self.get_student_progress(student_id)
        
        # Determine cognitive level based on interaction depth
        new_level = 1
        for level, info in self.cognitive_levels.items():
            if message_count >= info["threshold"]:
                new_level = level
        
        # Update concepts explored
        concepts_explored = progress["concepts_explored"]
        if concepts:
            for concept in concepts:
                if concept not in concepts_explored:
                    concepts_explored.append(concept)
        
        # Check for new badges
        badges = progress["badges_earned"]
        new_badges = self.check_achievements(student_id, message_count, new_level, concepts_explored)
        for badge in new_badges:
            if badge not in badges:
                badges.append(badge)
        
        # Update database
        cursor.execute("""
            UPDATE student_progress
            SET current_level = ?, total_interactions = ?, 
                badges_earned = ?, concepts_explored = ?, last_updated = CURRENT_TIMESTAMP
            WHERE student_id = ?
        """, (new_level, message_count, json.dumps(badges), 
              json.dumps(concepts_explored), student_id))
        
        conn.commit()
        conn.close()
        
        return new_level, new_badges
    
    def check_achievements(self, student_id: str, message_count: int, level: int, concepts: List[str]) -> List[str]:
        """Check if student earned new badges"""
        new_badges = []
        
        # First Insight - first interaction
        if message_count == 1:
            new_badges.append("first_insight")
        
        # Deep Thinker - reached evaluation level
        if level == 4:
            new_badges.append("deep_thinker")
        
        # Concept Connector - connected 3+ concepts
        if len(concepts) >= 3:
            new_badges.append("concept_connector")
        
        # Persistent Scholar - check session duration
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(duration_minutes) 
            FROM chat_sessions 
            WHERE user_id = ?
        """, (student_id,))
        max_duration = cursor.fetchone()[0]
        conn.close()
        
        if max_duration and max_duration >= 30:
            new_badges.append("persistent_scholar")
        
        # Critical Analyst - based on question complexity (simplified check)
        if level >= 3 and message_count >= 6:
            new_badges.append("critical_analyst")
        
        # Synthesis Master - reached synthesis level with multiple concepts
        if level >= 3 and len(concepts) >= 5:
            new_badges.append("synthesis_master")
        
        return new_badges
    
    def display_progress_indicator(self, student_id: str, message_count: int):
        """Display visual progress through cognitive levels"""
        progress = self.get_student_progress(student_id)
        current_level = progress["current_level"]
        
        # Update progress
        current_level, new_badges = self.update_progress(student_id, message_count)
        
        # Create progress visualization
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.markdown("### 🎯 Cognitive Journey")
            
            # Progress bar for each level
            for level, info in self.cognitive_levels.items():
                if level <= current_level:
                    progress_pct = 100
                elif level == current_level + 1:
                    # Calculate progress to next level
                    current_threshold = self.cognitive_levels[current_level]["threshold"]
                    next_threshold = info["threshold"]
                    # Ensure we don't get negative values
                    if message_count > current_threshold:
                        progress_pct = min(100, ((message_count - current_threshold) / 
                                               (next_threshold - current_threshold)) * 100)
                    else:
                        progress_pct = 0
                else:
                    progress_pct = 0
                
                # Ensure progress_pct is within valid range [0, 100]
                progress_pct = max(0, min(100, progress_pct))
                
                # Display level with progress
                st.markdown(f"{info['icon']} **{info['name']}**")
                st.progress(progress_pct / 100, text=f"{int(progress_pct)}%")
        
        with col2:
            # Circular progress visualization
            fig = self.create_circular_progress(current_level, message_count)
            st.plotly_chart(fig, use_container_width=True, key="progress_chart")
        
        with col3:
            st.markdown("### 🏆 Achievements")
            badges = progress["badges_earned"]
            
            if badges:
                for badge_key in badges[-3:]:  # Show last 3 badges
                    if badge_key in self.achievement_badges:
                        badge = self.achievement_badges[badge_key]
                        st.markdown(f"{badge['icon']} **{badge['name']}**")
                        st.caption(badge['description'])
            else:
                st.info("Keep engaging to earn badges!")
        
        # Show new badge notification
        if new_badges:
            for badge_key in new_badges:
                if badge_key in self.achievement_badges:
                    badge = self.achievement_badges[badge_key]
                    st.success(f"🎉 New Achievement: {badge['icon']} {badge['name']}!")
    
    def create_circular_progress(self, level: int, messages: int) -> go.Figure:
        """Create a circular progress chart"""
        # Calculate angle for current progress
        max_level = 4
        angle = (level / max_level) * 360
        
        # Create donut chart
        fig = go.Figure(data=[
            go.Pie(
                values=[level, max_level - level],
                hole=0.7,
                marker=dict(colors=[self.cognitive_levels[level]["color"], "#f0f0f0"]),
                textinfo='none',
                hoverinfo='skip'
            )
        ])
        
        # Add center text
        fig.add_annotation(
            text=f"<b>{self.cognitive_levels[level]['icon']}</b><br>{self.cognitive_levels[level]['name']}",
            x=0.5, y=0.5,
            font=dict(size=16),
            showarrow=False
        )
        
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def display_concept_map(self, student_id: str, article_title: str, concepts: List[str]):
        """Display interactive concept map"""
        st.markdown("### 🗺️ Concept Connections")
        
        if not concepts:
            st.info("Concepts will appear as you explore the article")
            return
        
        # Create network graph
        fig = go.Figure()
        
        # Add article as central node
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers+text',
            marker=dict(size=30, color='#FF6B6B'),
            text=[article_title[:20] + "..."],
            textposition="bottom center",
            hoverinfo='text',
            hovertext=article_title
        ))
        
        # Add concept nodes in a circle around the article
        import math
        n_concepts = len(concepts)
        for i, concept in enumerate(concepts[:8]):  # Limit to 8 concepts for clarity
            angle = (2 * math.pi * i) / min(n_concepts, 8)
            x = 2 * math.cos(angle)
            y = 2 * math.sin(angle)
            
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(size=20, color='#4ECDC4'),
                text=[concept.replace('_', ' ').title()],
                textposition="top center",
                hoverinfo='text',
                hovertext=f"Concept: {concept}"
            ))
            
            # Add edge from article to concept
            fig.add_trace(go.Scatter(
                x=[0, x], y=[0, y],
                mode='lines',
                line=dict(width=1, color='rgba(125, 125, 125, 0.3)'),
                hoverinfo='skip'
            ))
        
        # Add connections between related concepts
        self.add_concept_connections(fig, concepts)
        
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True, key="concept_map")
        
        # Save concept connections
        self.save_concept_connections(student_id, concepts, article_title)
    
    def add_concept_connections(self, fig: go.Figure, concepts: List[str]):
        """Add connections between related concepts"""
        # Simple heuristic: connect concepts that share words
        import math
        n_concepts = min(len(concepts), 8)
        
        for i in range(n_concepts):
            for j in range(i + 1, n_concepts):
                # Check if concepts are related (simplified)
                if any(word in concepts[j] for word in concepts[i].split('_')):
                    angle_i = (2 * math.pi * i) / n_concepts
                    angle_j = (2 * math.pi * j) / n_concepts
                    x_i = 2 * math.cos(angle_i)
                    y_i = 2 * math.sin(angle_i)
                    x_j = 2 * math.cos(angle_j)
                    y_j = 2 * math.sin(angle_j)
                    
                    fig.add_trace(go.Scatter(
                        x=[x_i, x_j], y=[y_i, y_j],
                        mode='lines',
                        line=dict(width=0.5, color='rgba(78, 205, 196, 0.3)', dash='dot'),
                        hoverinfo='skip'
                    ))
    
    def save_concept_connections(self, student_id: str, concepts: List[str], article_title: str):
        """Save concept connections to database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Save connections between concepts
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                cursor.execute("""
                    INSERT OR IGNORE INTO concept_connections 
                    (student_id, concept_from, concept_to, article_title)
                    VALUES (?, ?, ?, ?)
                """, (student_id, concepts[i], concepts[j], article_title))
        
        conn.commit()
        conn.close()
    
    def save_peer_insight(self, question: str, article_title: str, cognitive_level: int):
        """Save a good question for peer learning"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO peer_insights (question, article_title, cognitive_level)
            VALUES (?, ?, ?)
        """, (question, article_title, cognitive_level))
        
        conn.commit()
        conn.close()
    
    def display_peer_insights(self, article_title: str = None):
        """Display best questions from peers"""
        st.markdown("### 💭 Peer Insights")
        st.caption("Thoughtful questions from fellow students (anonymous)")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        query = """
            SELECT question, cognitive_level, upvotes, created_at
            FROM peer_insights
            WHERE 1=1
        """
        params = []
        
        if article_title:
            query += " AND article_title = ?"
            params.append(article_title)
        
        query += " ORDER BY upvotes DESC, created_at DESC LIMIT 5"
        
        cursor.execute(query, params)
        insights = cursor.fetchall()
        conn.close()
        
        if insights:
            for insight in insights:
                question, level, upvotes, created_at = insight
                level_info = self.cognitive_levels.get(level, self.cognitive_levels[1])
                
                with st.container():
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.markdown(f"{level_info['icon']} *\"{question}\"*")
                        st.caption(f"Level: {level_info['name']} • {upvotes} found helpful")
                    with col2:
                        if st.button("👍", key=f"upvote_{created_at}"):
                            self.upvote_insight(question)
        else:
            st.info("No peer insights yet. Your thoughtful questions might be featured here!")
    
    def upvote_insight(self, question: str):
        """Upvote a peer insight"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE peer_insights 
            SET upvotes = upvotes + 1
            WHERE question = ?
        """, (question,))
        
        conn.commit()
        conn.close()
    
    def check_question_quality(self, question: str, chat_history: List[Dict]) -> bool:
        """Check if a question is high quality for peer insights"""
        # Simple heuristics for question quality
        quality_indicators = [
            len(question) > 30,  # Substantial question
            '?' in question,  # Actually a question
            any(word in question.lower() for word in 
                ['why', 'how', 'what if', 'could', 'would', 'relationship', 'compare']),
            len(chat_history) > 4  # Not too early in conversation
        ]
        
        return sum(quality_indicators) >= 3