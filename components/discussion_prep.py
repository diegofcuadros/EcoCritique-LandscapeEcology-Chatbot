"""
Discussion Preparation System - Generates class discussion points from student interactions
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import streamlit as st
import re
from collections import Counter
from components.database import DATABASE_PATH

class DiscussionPrepSystem:
    """Generates discussion points for in-class sessions based on student chat interactions"""
    
    def __init__(self):
        self.database_path = DATABASE_PATH
        
        # Key themes for landscape ecology discussions
        self.discussion_themes = {
            "spatial_scale": {
                "keywords": ["scale", "resolution", "extent", "grain", "hierarchy", "multi-scale"],
                "icon": "📏",
                "description": "Scale effects and spatial hierarchy"
            },
            "connectivity": {
                "keywords": ["connectivity", "corridor", "movement", "dispersal", "gene flow", "barrier"],
                "icon": "🔗", 
                "description": "Landscape connectivity and wildlife movement"
            },
            "fragmentation": {
                "keywords": ["fragmentation", "fragment", "patch", "isolation", "edge effect"],
                "icon": "🧩",
                "description": "Habitat fragmentation and edge effects"
            },
            "gis_methods": {
                "keywords": ["gis", "remote sensing", "satellite", "spatial analysis", "mapping"],
                "icon": "🗺️",
                "description": "GIS and spatial analysis methods"
            },
            "disturbance": {
                "keywords": ["disturbance", "fire", "flood", "human impact", "land use"],
                "icon": "⚡",
                "description": "Disturbance regimes and human impacts"
            },
            "conservation": {
                "keywords": ["conservation", "management", "restoration", "protected area", "planning"],
                "icon": "🌿",
                "description": "Conservation and management applications"
            },
            "modeling": {
                "keywords": ["model", "simulation", "prediction", "scenario", "statistical"],
                "icon": "📊",
                "description": "Modeling and statistical approaches"
            }
        }
    
    def generate_discussion_prep(self, article_title: str = None, days_back: int = 7) -> Dict[str, Any]:
        """Generate comprehensive discussion preparation based on recent student interactions"""
        
        # Get student interactions
        student_sessions = self._get_recent_sessions(article_title, days_back)
        
        if student_sessions.empty:
            return self._create_empty_discussion_prep(article_title)
        
        # Analyze student responses
        conversation_analysis = self._analyze_student_conversations(student_sessions)
        
        # Generate discussion points
        discussion_points = self._generate_discussion_points(conversation_analysis, article_title)
        
        # Identify controversial or challenging topics
        challenging_topics = self._identify_challenging_topics(conversation_analysis)
        
        # Create student engagement summary
        engagement_summary = self._create_engagement_summary(student_sessions)
        
        # Generate talking points for professor
        professor_talking_points = self._generate_professor_talking_points(conversation_analysis, article_title)
        
        return {
            'article_title': article_title,
            'generated_at': datetime.now().isoformat(),
            'student_count': len(student_sessions['user_id'].unique()),
            'total_sessions': len(student_sessions),
            'discussion_points': discussion_points,
            'challenging_topics': challenging_topics,
            'engagement_summary': engagement_summary,
            'professor_talking_points': professor_talking_points,
            'theme_distribution': self._analyze_theme_distribution(conversation_analysis)
        }
    
    def _get_recent_sessions(self, article_title: str, days_back: int) -> pd.DataFrame:
        """Get recent student sessions for the specified article"""
        conn = sqlite3.connect(self.database_path)
        
        query = """
            SELECT s.session_id, s.user_id, s.article_title, s.start_time,
                   s.duration_minutes, s.message_count, s.max_level_reached,
                   GROUP_CONCAT(m.content, ' | ') as all_messages
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.session_id = m.session_id
            WHERE s.user_type = 'Student'
            AND s.start_time >= datetime('now', '-{} days')
        """.format(days_back)
        
        if article_title:
            query += f" AND s.article_title = '{article_title}'"
        
        query += " GROUP BY s.session_id ORDER BY s.start_time DESC"
        
        try:
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Error retrieving sessions: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def _analyze_student_conversations(self, sessions_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze student conversations to identify patterns and themes"""
        
        all_messages = []
        theme_mentions = {theme: 0 for theme in self.discussion_themes.keys()}
        student_insights = []
        common_questions = []
        misconceptions = []
        
        for _, session in sessions_df.iterrows():
            if pd.isna(session['all_messages']):
                continue
                
            messages = session['all_messages'].split(' | ')
            student_messages = [msg for i, msg in enumerate(messages) if i % 2 == 0]  # Assume student messages are even-indexed
            
            all_messages.extend(student_messages)
            
            # Analyze themes mentioned
            for theme, config in self.discussion_themes.items():
                for keyword in config['keywords']:
                    theme_mentions[theme] += sum(keyword.lower() in msg.lower() for msg in student_messages)
            
            # Extract potential insights (messages with certain indicators)
            for msg in student_messages:
                if self._is_potential_insight(msg):
                    student_insights.append({
                        'student_id': session['user_id'],
                        'insight': msg[:200] + "..." if len(msg) > 200 else msg,
                        'session_id': session['session_id']
                    })
                
                if self._is_question(msg):
                    common_questions.append(msg[:150] + "..." if len(msg) > 150 else msg)
                
                if self._indicates_misconception(msg):
                    misconceptions.append({
                        'student_id': session['user_id'],
                        'misconception': msg[:200] + "..." if len(msg) > 200 else msg
                    })
        
        return {
            'theme_mentions': theme_mentions,
            'student_insights': student_insights[:10],  # Top 10 insights
            'common_questions': common_questions[:8],   # Top 8 questions
            'misconceptions': misconceptions[:5],       # Top 5 potential misconceptions
            'total_messages': len(all_messages),
            'unique_concepts': self._extract_unique_concepts(all_messages)
        }
    
    def _is_potential_insight(self, message: str) -> bool:
        """Identify messages that might contain student insights"""
        insight_indicators = [
            'i think', 'i believe', 'it seems', 'this suggests', 'this means',
            'because', 'therefore', 'however', 'but', 'although', 'connects to',
            'relates to', 'similar to', 'different from', 'compared to'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in insight_indicators) and len(message.split()) > 8
    
    def _is_question(self, message: str) -> bool:
        """Identify student questions"""
        question_words = ['what', 'why', 'how', 'when', 'where', 'which', 'who']
        message_lower = message.lower()
        
        return (message.strip().endswith('?') or 
                any(message_lower.startswith(word) for word in question_words)) and len(message.split()) > 4
    
    def _indicates_misconception(self, message: str) -> bool:
        """Identify potential misconceptions (simplified heuristic)"""
        misconception_indicators = [
            'all fragments are bad', 'edges are always negative', 'bigger is always better',
            'corridors solve everything', 'gis shows everything', 'models are always right'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in misconception_indicators)
    
    def _extract_unique_concepts(self, messages: List[str]) -> List[str]:
        """Extract unique landscape ecology concepts mentioned by students"""
        
        concept_patterns = [
            'habitat fragmentation', 'edge effect', 'connectivity', 'corridor',
            'patch size', 'landscape metric', 'gis', 'remote sensing',
            'spatial analysis', 'scale', 'resolution', 'metapopulation',
            'source-sink', 'disturbance', 'conservation', 'restoration'
        ]
        
        found_concepts = set()
        all_text = ' '.join(messages).lower()
        
        for concept in concept_patterns:
            if concept in all_text:
                found_concepts.add(concept)
        
        return list(found_concepts)
    
    def _generate_discussion_points(self, analysis: Dict[str, Any], article_title: str) -> List[Dict[str, str]]:
        """Generate specific discussion points for class"""
        
        discussion_points = []
        
        # Theme-based discussion points
        sorted_themes = sorted(analysis['theme_mentions'].items(), key=lambda x: x[1], reverse=True)
        
        for theme, mention_count in sorted_themes[:4]:  # Top 4 themes
            if mention_count > 0:
                theme_config = self.discussion_themes[theme]
                
                discussion_points.append({
                    'type': 'theme_discussion',
                    'icon': theme_config['icon'],
                    'title': theme_config['description'],
                    'point': f"Students showed high interest in {theme_config['description'].lower()}. "
                            f"Build on their {mention_count} mentions to explore applications and limitations.",
                    'suggested_questions': self._get_theme_questions(theme, article_title),
                    'priority': 'high' if mention_count > 5 else 'medium'
                })
        
        # Student insight-based discussions
        if analysis['student_insights']:
            discussion_points.append({
                'type': 'insight_discussion',
                'icon': '💡',
                'title': 'Student Insights to Explore',
                'point': f"Students generated {len(analysis['student_insights'])} notable insights. "
                        "Use these as starting points for deeper class discussion.",
                'insights': analysis['student_insights'][:3],  # Show top 3
                'priority': 'high'
            })
        
        # Question-based discussions
        if analysis['common_questions']:
            discussion_points.append({
                'type': 'question_discussion', 
                'icon': '❓',
                'title': 'Common Student Questions',
                'point': "Address these frequently asked questions through class dialogue:",
                'questions': analysis['common_questions'][:4],
                'priority': 'medium'
            })
        
        return discussion_points
    
    def _get_theme_questions(self, theme: str, article_title: str) -> List[str]:
        """Generate theme-specific discussion questions"""
        
        theme_questions = {
            'spatial_scale': [
                f"How might the conclusions in '{article_title}' change at different spatial scales?",
                "What scale of analysis would be most appropriate for management decisions?",
                "How do grain and extent affect the patterns we observe?"
            ],
            'connectivity': [
                "What evidence do you see for functional vs. structural connectivity?",
                "How might climate change affect the connectivity patterns described?",
                "What are the trade-offs in corridor design for different species?"
            ],
            'fragmentation': [
                "Are all edge effects necessarily negative? Provide examples.",
                "How do patch size and isolation interact to affect species persistence?",
                "What landscape metrics best capture fragmentation effects?"
            ],
            'gis_methods': [
                "What are the limitations of the GIS methods used in this study?",
                "How might new remote sensing technologies change these analyses?",
                "What ground-truthing would strengthen these spatial analyses?"
            ],
            'disturbance': [
                "How do natural and anthropogenic disturbances differ in their effects?",
                "What role does disturbance history play in current patterns?",
                "How might disturbance frequency and intensity interact?"
            ],
            'conservation': [
                "How do these findings inform reserve design principles?",
                "What are the social-ecological considerations not addressed?",
                "How might ecosystem services fit into this conservation framework?"
            ],
            'modeling': [
                "What are the key assumptions underlying these models?",
                "How might uncertainty affect the management recommendations?",
                "What additional data would improve model predictions?"
            ]
        }
        
        return theme_questions.get(theme, ["Discuss the implications of this theme for landscape management."])
    
    def _identify_challenging_topics(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify topics that students found challenging"""
        
        challenging_topics = []
        
        # Topics with misconceptions need attention
        if analysis['misconceptions']:
            challenging_topics.append({
                'type': 'misconception',
                'icon': '⚠️',
                'title': 'Address Misconceptions',
                'description': f"{len(analysis['misconceptions'])} potential misconceptions identified",
                'action': 'Clarify these concepts through guided discussion',
                'examples': analysis['misconceptions'][:2]
            })
        
        # Topics with few mentions might be difficult
        low_mention_themes = [(theme, count) for theme, count in analysis['theme_mentions'].items() if 0 < count < 3]
        
        if low_mention_themes:
            challenging_topics.append({
                'type': 'low_engagement',
                'icon': '🤔',
                'title': 'Topics Needing More Attention',
                'description': f"Some themes had limited student engagement",
                'themes': [self.discussion_themes[theme]['description'] for theme, count in low_mention_themes],
                'action': 'Provide additional scaffolding and examples'
            })
        
        return challenging_topics
    
    def _create_engagement_summary(self, sessions_df: pd.DataFrame) -> Dict[str, Any]:
        """Create summary of student engagement patterns"""
        
        if sessions_df.empty:
            return {'total_students': 0, 'avg_duration': 0, 'avg_messages': 0}
        
        return {
            'total_students': len(sessions_df['user_id'].unique()),
            'avg_duration': round(sessions_df['duration_minutes'].mean(), 1),
            'avg_messages': round(sessions_df['message_count'].mean(), 1),
            'max_level_distribution': dict(sessions_df['max_level_reached'].value_counts()),
            'highly_engaged_students': len(sessions_df[sessions_df['duration_minutes'] > 20]),
            'deep_thinkers': len(sessions_df[sessions_df['max_level_reached'] >= 3])
        }
    
    def _generate_professor_talking_points(self, analysis: Dict[str, Any], article_title: str) -> List[str]:
        """Generate specific talking points for the professor"""
        
        talking_points = []
        
        # Based on student engagement
        if analysis['student_insights']:
            talking_points.append(
                f"Build on student insight: '{analysis['student_insights'][0]['insight']}' "
                "by asking the class to evaluate this perspective."
            )
        
        # Based on common themes
        top_theme = max(analysis['theme_mentions'].items(), key=lambda x: x[1])[0]
        talking_points.append(
            f"Students are most interested in {self.discussion_themes[top_theme]['description'].lower()}. "
            "Use this as an entry point to connect to other concepts."
        )
        
        # Based on questions
        if analysis['common_questions']:
            talking_points.append(
                f"Address the question: '{analysis['common_questions'][0]}' "
                "by turning it back to the class for peer learning."
            )
        
        # Encourage concept connections
        if len(analysis['unique_concepts']) > 3:
            talking_points.append(
                f"Help students connect these {len(analysis['unique_concepts'])} concepts: "
                f"{', '.join(analysis['unique_concepts'][:4])}."
            )
        
        return talking_points
    
    def _analyze_theme_distribution(self, analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze how themes are distributed across student conversations"""
        
        theme_distribution = {}
        total_mentions = sum(analysis['theme_mentions'].values())
        
        for theme, count in analysis['theme_mentions'].items():
            percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
            
            theme_distribution[theme] = {
                'count': count,
                'percentage': round(percentage, 1),
                'icon': self.discussion_themes[theme]['icon'],
                'description': self.discussion_themes[theme]['description'],
                'engagement_level': 'high' if count > 5 else 'medium' if count > 2 else 'low'
            }
        
        return theme_distribution
    
    def _create_empty_discussion_prep(self, article_title: str) -> Dict[str, Any]:
        """Create empty discussion prep when no student data available"""
        
        return {
            'article_title': article_title,
            'generated_at': datetime.now().isoformat(),
            'student_count': 0,
            'total_sessions': 0,
            'discussion_points': [{
                'type': 'general',
                'icon': '📋',
                'title': 'General Discussion Preparation',
                'point': 'No student interactions available yet. Use standard article discussion questions.',
                'priority': 'medium'
            }],
            'challenging_topics': [],
            'engagement_summary': {'total_students': 0, 'avg_duration': 0, 'avg_messages': 0},
            'professor_talking_points': [
                f"Begin with open-ended questions about '{article_title}'",
                "Use think-pair-share activities to generate initial engagement",
                "Focus on connecting article content to course concepts"
            ],
            'theme_distribution': {}
        }

    def display_discussion_prep(self, prep_data: Dict[str, Any]):
        """Display discussion preparation in Streamlit interface"""
        
        st.markdown("## 🎯 Class Discussion Preparation")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Students Engaged", prep_data['student_count'])
        with col2:
            st.metric("Total Sessions", prep_data['total_sessions'])
        with col3:
            avg_duration = prep_data['engagement_summary'].get('avg_duration', 0)
            st.metric("Avg Session Time", f"{avg_duration} min")
        with col4:
            deep_thinkers = prep_data['engagement_summary'].get('deep_thinkers', 0)
            st.metric("Deep Thinkers", deep_thinkers)
        
        # Discussion points
        st.markdown("### 💬 Key Discussion Points")
        for point in prep_data['discussion_points']:
            priority_color = {'high': '🔥', 'medium': '⭐', 'low': '💡'}
            priority_icon = priority_color.get(point.get('priority', 'medium'), '⭐')
            
            with st.expander(f"{point['icon']} {point['title']} {priority_icon}"):
                st.write(point['point'])
                
                if 'suggested_questions' in point:
                    st.markdown("**Suggested Questions:**")
                    for q in point['suggested_questions']:
                        st.markdown(f"• {q}")
                
                if 'insights' in point:
                    st.markdown("**Student Insights to Build On:**")
                    for insight in point['insights']:
                        st.markdown(f"• *{insight['insight']}* - {insight['student_id']}")
        
        # Professor talking points
        if prep_data['professor_talking_points']:
            st.markdown("### 🎤 Professor Talking Points")
            for i, point in enumerate(prep_data['professor_talking_points'], 1):
                st.markdown(f"{i}. {point}")
        
        # Theme distribution
        if prep_data['theme_distribution']:
            st.markdown("### 📊 Student Interest Distribution")
            
            # Create visual representation
            theme_data = []
            for theme, data in prep_data['theme_distribution'].items():
                if data['count'] > 0:
                    theme_data.append({
                        'Theme': f"{data['icon']} {data['description']}",
                        'Mentions': data['count'],
                        'Percentage': data['percentage']
                    })
            
            if theme_data:
                theme_df = pd.DataFrame(theme_data)
                st.dataframe(theme_df, hide_index=True)