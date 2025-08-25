import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import json
import re

class AssessmentQualitySystem:
    """Automated assessment and grading system for student engagement"""
    
    def __init__(self):
        self.rubric_criteria = {
            "depth_of_analysis": {
                "weight": 0.20,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Demonstrates critical thinking with original insights"},
                    "good": {"min_score": 75, "description": "Shows solid understanding with some analysis"},
                    "satisfactory": {"min_score": 60, "description": "Basic comprehension with limited analysis"},
                    "needs_improvement": {"min_score": 0, "description": "Surface-level engagement"}
                }
            },
            "concept_integration": {
                "weight": 0.15,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Connects multiple concepts across articles"},
                    "good": {"min_score": 75, "description": "Makes connections within the article"},
                    "satisfactory": {"min_score": 60, "description": "Identifies key concepts"},
                    "needs_improvement": {"min_score": 0, "description": "Limited concept recognition"}
                }
            },
            "question_quality": {
                "weight": 0.15,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Asks probing, thoughtful questions"},
                    "good": {"min_score": 75, "description": "Asks relevant clarifying questions"},
                    "satisfactory": {"min_score": 60, "description": "Asks basic questions"},
                    "needs_improvement": {"min_score": 0, "description": "Minimal questioning"}
                }
            },
            "engagement_consistency": {
                "weight": 0.15,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Sustained, focused engagement throughout"},
                    "good": {"min_score": 75, "description": "Mostly consistent participation"},
                    "satisfactory": {"min_score": 60, "description": "Some gaps but adequate overall"},
                    "needs_improvement": {"min_score": 0, "description": "Sporadic or minimal engagement"}
                }
            },
            "cognitive_progression": {
                "weight": 0.15,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Reaches evaluation level consistently"},
                    "good": {"min_score": 75, "description": "Achieves synthesis level"},
                    "satisfactory": {"min_score": 60, "description": "Demonstrates analysis"},
                    "needs_improvement": {"min_score": 0, "description": "Remains at comprehension level"}
                }
            },
            "spatial_reasoning": {
                "weight": 0.20,
                "levels": {
                    "excellent": {"min_score": 90, "description": "Demonstrates sophisticated spatial thinking and GIS understanding"},
                    "good": {"min_score": 75, "description": "Shows solid grasp of spatial concepts and scale effects"},
                    "satisfactory": {"min_score": 60, "description": "Basic understanding of spatial patterns"},
                    "needs_improvement": {"min_score": 0, "description": "Limited spatial reasoning evident"}
                }
            }
        }
        
        self.quality_indicators = {
            "critical_thinking_keywords": [
                "however", "although", "nevertheless", "conversely", "alternatively",
                "implies", "suggests", "indicates", "demonstrates", "reveals",
                "compare", "contrast", "evaluate", "assess", "critique"
            ],
            "synthesis_keywords": [
                "therefore", "thus", "consequently", "as a result", "this means",
                "connects to", "relates to", "builds on", "extends", "integrates"
            ],
            "depth_indicators": [
                "because", "evidence", "example", "specifically", "in particular",
                "for instance", "such as", "considering", "given that", "assuming"
            ],
            "spatial_reasoning_keywords": [
                "scale", "resolution", "extent", "grain", "spatial", "pattern",
                "distribution", "connectivity", "fragmentation", "proximity",
                "distance", "buffer", "overlay", "network", "hierarchy",
                "neighborhood", "clustering", "autocorrelation", "hotspot"
            ],
            "gis_methods_keywords": [
                "gis", "remote sensing", "satellite", "landsat", "modis", "lidar",
                "aerial", "mapping", "digitize", "georeferenced", "projection",
                "coordinate", "vector", "raster", "topology", "database",
                "query", "spatial analysis", "interpolation", "classification"
            ],
            "landscape_metrics_keywords": [
                "patch size", "edge density", "shape index", "connectivity index",
                "fragmentation index", "landscape metric", "contagion",
                "diversity index", "evenness", "dominance", "aggregation",
                "proximity index", "core area", "edge to area ratio"
            ]
        }
        
        self.initialize_assessment_tables()
    
    def initialize_assessment_tables(self):
        """Create tables for assessment tracking"""
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        
        # Rubric scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubric_scores (
                score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                session_id INTEGER,
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
        
        # Quality metrics table
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
        
        # Weekly reports table
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
        conn.close()
    
    def calculate_message_quality(self, message: str) -> Dict[str, Any]:
        """Analyze individual message quality including spatial reasoning"""
        message_lower = message.lower()
        
        # Calculate various quality metrics
        word_count = len(message.split())
        
        # Check for critical thinking
        critical_thinking_score = sum(
            1 for keyword in self.quality_indicators["critical_thinking_keywords"]
            if keyword in message_lower
        ) / len(self.quality_indicators["critical_thinking_keywords"])
        
        # Check for synthesis
        synthesis_score = sum(
            1 for keyword in self.quality_indicators["synthesis_keywords"]
            if keyword in message_lower
        ) / len(self.quality_indicators["synthesis_keywords"])
        
        # Check for depth
        depth_score = sum(
            1 for keyword in self.quality_indicators["depth_indicators"]
            if keyword in message_lower
        ) / len(self.quality_indicators["depth_indicators"])
        
        # Check for spatial reasoning
        spatial_reasoning_score = sum(
            1 for keyword in self.quality_indicators["spatial_reasoning_keywords"]
            if keyword in message_lower
        ) / len(self.quality_indicators["spatial_reasoning_keywords"])
        
        # Check for GIS methods understanding
        gis_methods_score = sum(
            1 for keyword in self.quality_indicators["gis_methods_keywords"]
            if keyword in message_lower
        ) / len(self.quality_indicators["gis_methods_keywords"])
        
        # Check for landscape metrics understanding
        landscape_metrics_score = sum(
            1 for keyword in self.quality_indicators["landscape_metrics_keywords"]
            if keyword in message_lower
        ) / len(self.quality_indicators["landscape_metrics_keywords"])
        
        # Combined spatial understanding score
        spatial_understanding = (spatial_reasoning_score + gis_methods_score + landscape_metrics_score) / 3
        
        # Question complexity (0-3 scale)
        question_complexity = 0
        if "?" in message:
            if any(word in message_lower for word in ["why", "how", "what if", "explain"]):
                question_complexity = 3
            elif any(word in message_lower for word in ["when", "where", "who", "which"]):
                question_complexity = 2
            else:
                question_complexity = 1
        
        # Calculate overall thoughtfulness score
        thoughtfulness = (
            (critical_thinking_score * 0.25) +
            (synthesis_score * 0.25) +
            (depth_score * 0.15) +
            (spatial_understanding * 0.25) +
            (min(word_count / 100, 1) * 0.05) +
            (question_complexity / 3 * 0.05)
        ) * 100
        
        return {
            "thoughtfulness_score": thoughtfulness,
            "critical_thinking_present": critical_thinking_score > 0.1,
            "synthesis_present": synthesis_score > 0.1,
            "spatial_reasoning_present": spatial_understanding > 0.1,
            "word_count": word_count,
            "question_complexity": question_complexity,
            "spatial_understanding_score": spatial_understanding * 100,
            "gis_methods_mentioned": gis_methods_score > 0,
            "landscape_metrics_mentioned": landscape_metrics_score > 0
        }
    
    def evaluate_session_rubric(self, student_id: str, session_id: int) -> Dict[str, Any]:
        """Evaluate a complete session using the rubric"""
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        
        # Get session messages
        cursor.execute("""
            SELECT role, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY message_order
        """, (session_id,))
        messages = cursor.fetchall()
        
        # Get session info
        cursor.execute("""
            SELECT article_title, duration_minutes
            FROM chat_sessions
            WHERE session_id = ?
        """, (session_id,))
        session_info = cursor.fetchone()
        
        if not messages or not session_info:
            conn.close()
            return {}
        
        article_title, duration = session_info
        
        # Calculate rubric scores
        scores = {}
        
        # Filter student messages (role = 'user')
        student_messages = [msg[1] for msg in messages if msg[0] == 'user' and msg[1]]
        
        # 1. Depth of Analysis
        if student_messages:
            quality_scores = [self.calculate_message_quality(msg)["thoughtfulness_score"] 
                             for msg in student_messages]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            scores["depth_of_analysis"] = min(100, avg_quality * 1.2)
        else:
            scores["depth_of_analysis"] = 0
        
        # 2. Concept Integration
        unique_concepts = set()
        for msg in student_messages:
            # Extract potential concepts (simplified - could use NLP)
            words = msg.lower().split()
            concepts = [w for w in words if len(w) > 6 and w.isalpha()]
            unique_concepts.update(concepts[:5])
        
        concept_score = min(100, len(unique_concepts) * 5)
        scores["concept_integration"] = concept_score
        
        # 3. Question Quality
        questions = [msg for msg in student_messages if "?" in msg]
        if questions:
            question_qualities = [self.calculate_message_quality(q)["question_complexity"] 
                                 for q in questions]
            avg_question_quality = sum(question_qualities) / len(question_qualities)
            scores["question_quality"] = min(100, (avg_question_quality / 3) * 100)
        else:
            scores["question_quality"] = 40
        
        # 4. Engagement Consistency
        message_gaps = []
        if len(messages) > 1:
            # Check for consistent engagement (simplified)
            avg_words_per_message = sum(len(msg[0].split()) for msg in messages if msg[0]) / len(messages)
            consistency_score = min(100, (avg_words_per_message / 50) * 100)
        else:
            consistency_score = 50
        scores["engagement_consistency"] = consistency_score
        
        # 5. Cognitive Progression
        max_cognitive_level = max((msg[2] for msg in messages if msg[2]), default=1)
        progression_score = (max_cognitive_level / 4) * 100
        scores["cognitive_progression"] = progression_score
        
        # Calculate weighted total
        total_score = sum(
            scores[criterion] * self.rubric_criteria[criterion]["weight"]
            for criterion in scores
        )
        
        # Determine suggested grade
        if total_score >= 90:
            suggested_grade = "A"
        elif total_score >= 80:
            suggested_grade = "B"
        elif total_score >= 70:
            suggested_grade = "C"
        elif total_score >= 60:
            suggested_grade = "D"
        else:
            suggested_grade = "F"
        
        # Store rubric scores
        cursor.execute("""
            INSERT INTO rubric_scores 
            (student_id, session_id, article_title, depth_score, integration_score,
             question_score, consistency_score, progression_score, total_score, suggested_grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, session_id, article_title, scores["depth_of_analysis"],
              scores["concept_integration"], scores["question_quality"],
              scores["engagement_consistency"], scores["cognitive_progression"],
              total_score, suggested_grade))
        
        conn.commit()
        conn.close()
        
        return {
            "scores": scores,
            "total_score": total_score,
            "suggested_grade": suggested_grade,
            "article_title": article_title
        }
    
    def generate_weekly_report(self, student_id: str, week_start: datetime) -> Dict[str, Any]:
        """Generate a weekly progress report for a student"""
        week_end = week_start + timedelta(days=7)
        
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        
        # Get sessions for the week
        cursor.execute("""
            SELECT session_id, article_title, duration_minutes, timestamp
            FROM chat_sessions
            WHERE user_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """, (student_id, week_start, week_end))
        sessions = cursor.fetchall()
        
        if not sessions:
            conn.close()
            return {"error": "No sessions found for this week"}
        
        # Get quality metrics for the week
        cursor.execute("""
            SELECT AVG(thoughtfulness_score), COUNT(*)
            FROM quality_metrics
            WHERE student_id = ? AND created_at BETWEEN ? AND ?
        """, (student_id, week_start, week_end))
        quality_data = cursor.fetchone()
        avg_quality = quality_data[0] if quality_data[0] else 0
        
        # Get cognitive progression
        cursor.execute("""
            SELECT MAX(cognitive_level)
            FROM chat_messages cm
            JOIN chat_sessions cs ON cm.session_id = cs.session_id
            WHERE cs.user_id = ? AND cs.timestamp BETWEEN ? AND ?
        """, (student_id, week_start, week_end))
        max_level = cursor.fetchone()[0] or 1
        
        # Get rubric scores for the week
        cursor.execute("""
            SELECT AVG(total_score), AVG(depth_score), AVG(question_score)
            FROM rubric_scores
            WHERE student_id = ? AND evaluated_at BETWEEN ? AND ?
        """, (student_id, week_start, week_end))
        rubric_data = cursor.fetchone()
        
        # Identify strengths and areas for improvement
        strengths = []
        improvements = []
        
        if rubric_data[1] and rubric_data[1] > 75:
            strengths.append("Strong analytical depth in responses")
        else:
            improvements.append("Develop deeper analysis in discussions")
        
        if rubric_data[2] and rubric_data[2] > 75:
            strengths.append("Excellent questioning skills")
        else:
            improvements.append("Ask more probing questions")
        
        if max_level >= 3:
            strengths.append("Achieved higher-order thinking levels")
        else:
            improvements.append("Work towards synthesis and evaluation levels")
        
        # Generate cognitive progress description
        cognitive_progress = {
            1: "Currently at comprehension level - understanding basic concepts",
            2: "Progressing to analysis - breaking down complex ideas",
            3: "Reaching synthesis - connecting multiple concepts",
            4: "Achieving evaluation - critical assessment of ideas"
        }.get(max_level, "Beginning engagement")
        
        # Store the report
        cursor.execute("""
            INSERT INTO weekly_reports
            (student_id, week_start, week_end, sessions_completed, avg_quality_score,
             cognitive_progress, strengths, areas_for_improvement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, week_start, week_end, len(sessions), avg_quality,
              cognitive_progress, json.dumps(strengths), json.dumps(improvements)))
        
        conn.commit()
        conn.close()
        
        return {
            "student_id": student_id,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "sessions_completed": len(sessions),
            "avg_quality_score": round(avg_quality, 1),
            "cognitive_progress": cognitive_progress,
            "max_cognitive_level": max_level,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "avg_rubric_score": round(rubric_data[0], 1) if rubric_data[0] else 0
        }
    
    def display_rubric_evaluation(self, student_id: str, session_id: int):
        """Display rubric evaluation in Streamlit"""
        evaluation = self.evaluate_session_rubric(student_id, session_id)
        
        if not evaluation:
            st.error("No evaluation data available")
            return
        
        st.markdown("### 📊 Automated Rubric Assessment")
        
        # Overall grade
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Suggested Grade", evaluation["suggested_grade"])
        with col2:
            st.metric("Total Score", f"{evaluation['total_score']:.1f}%")
        with col3:
            st.metric("Article", evaluation["article_title"][:20] + "...")
        
        # Detailed rubric scores
        st.markdown("#### Rubric Criteria Breakdown")
        
        for criterion, score in evaluation["scores"].items():
            criterion_info = self.rubric_criteria[criterion]
            weight = criterion_info["weight"]
            
            # Determine performance level
            level = "needs_improvement"
            for level_name, level_info in criterion_info["levels"].items():
                if score >= level_info["min_score"]:
                    level = level_name
                    break
            
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.markdown(f"**{criterion.replace('_', ' ').title()}**")
                st.caption(f"Weight: {weight*100:.0f}%")
            with col2:
                st.progress(score / 100)
                st.caption(criterion_info["levels"][level]["description"])
            with col3:
                st.metric("Score", f"{score:.0f}%")
    
    def display_quality_metrics(self, student_id: str):
        """Display participation quality metrics"""
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        
        # Get recent quality metrics
        cursor.execute("""
            SELECT 
                AVG(thoughtfulness_score) as avg_thoughtfulness,
                SUM(CASE WHEN critical_thinking_present THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN synthesis_present THEN 1 ELSE 0 END) as synthesis_count,
                AVG(word_count) as avg_words,
                AVG(question_complexity) as avg_question_quality,
                COUNT(*) as total_messages
            FROM quality_metrics
            WHERE student_id = ?
            AND created_at > datetime('now', '-30 days')
        """, (student_id,))
        
        metrics = cursor.fetchone()
        conn.close()
        
        if not metrics or not metrics[5]:
            st.info("No quality metrics available yet")
            return
        
        st.markdown("### 🎯 Participation Quality Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Thoughtfulness",
                f"{metrics[0]:.1f}%",
                help="Overall quality of responses"
            )
        
        with col2:
            critical_pct = (metrics[1] / metrics[5]) * 100 if metrics[5] else 0
            st.metric(
                "Critical Thinking",
                f"{critical_pct:.0f}%",
                help="Responses showing critical analysis"
            )
        
        with col3:
            synthesis_pct = (metrics[2] / metrics[5]) * 100 if metrics[5] else 0
            st.metric(
                "Synthesis",
                f"{synthesis_pct:.0f}%",
                help="Responses connecting ideas"
            )
        
        with col4:
            st.metric(
                "Avg Response Length",
                f"{metrics[3]:.0f} words",
                help="Average words per response"
            )
    
    def display_weekly_reports(self, student_id: str = None):
        """Display weekly progress reports"""
        st.markdown("### 📅 Weekly Progress Reports")
        
        # Generate report for current week if needed
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if student_id:
            report = self.generate_weekly_report(student_id, week_start)
            
            if "error" not in report:
                # Display report card
                st.markdown("#### Current Week Report")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sessions Completed", report["sessions_completed"])
                with col2:
                    st.metric("Avg Quality Score", f"{report['avg_quality_score']}%")
                with col3:
                    st.metric("Rubric Score", f"{report['avg_rubric_score']}%")
                
                # Progress and feedback
                st.markdown("**Cognitive Progress:**")
                st.info(report["cognitive_progress"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Strengths:**")
                    for strength in report["strengths"]:
                        st.success(f"✓ {strength}")
                
                with col2:
                    st.markdown("**Areas for Improvement:**")
                    for improvement in report["areas_for_improvement"]:
                        st.warning(f"→ {improvement}")
        
        # Show historical reports
        conn = sqlite3.connect('data/chatbot_interactions.db')
        query = """
            SELECT student_id, week_start, week_end, sessions_completed,
                   avg_quality_score, cognitive_progress
            FROM weekly_reports
            ORDER BY week_start DESC
            LIMIT 10
        """
        
        if student_id:
            query = query.replace("ORDER BY", f"WHERE student_id = '{student_id}' ORDER BY")
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            st.markdown("#### Historical Reports")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
    
    def get_class_assessment_overview(self) -> pd.DataFrame:
        """Get assessment overview for entire class"""
        conn = sqlite3.connect('data/chatbot_interactions.db')
        
        query = """
            SELECT 
                rs.student_id,
                COUNT(DISTINCT rs.session_id) as sessions_evaluated,
                AVG(rs.total_score) as avg_score,
                AVG(rs.depth_score) as avg_depth,
                AVG(rs.integration_score) as avg_integration,
                AVG(rs.question_score) as avg_questions,
                AVG(rs.consistency_score) as avg_consistency,
                AVG(rs.progression_score) as avg_progression,
                GROUP_CONCAT(DISTINCT rs.suggested_grade) as grades
            FROM rubric_scores rs
            GROUP BY rs.student_id
            ORDER BY avg_score DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df