"""
Personalization Engine for EcoCritique
Adapts tutoring approach based on individual student learning patterns and preferences
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re

class PersonalizationEngine:
    """
    Advanced personalization system that learns from student interactions
    and adapts tutoring strategies to individual learning styles and needs.
    """
    
    def __init__(self, database_path: str = "ecocritique.db"):
        self.database_path = database_path
        self.initialize_database()
        
        # Learning style indicators
        self.learning_style_indicators = {
            'visual': {
                'keywords': ['see', 'show', 'picture', 'diagram', 'figure', 'image', 'looks like', 'visualize'],
                'question_preferences': ['examples', 'diagrams', 'spatial_relationships'],
                'evidence_types': ['visual_examples', 'spatial_data']
            },
            'quantitative': {
                'keywords': ['data', 'numbers', 'statistics', 'percentage', 'measurement', 'calculate', 'compare'],
                'question_preferences': ['data_analysis', 'calculations', 'comparisons'],
                'evidence_types': ['quantitative_data', 'statistics', 'measurements']
            },
            'conceptual': {
                'keywords': ['theory', 'concept', 'principle', 'framework', 'understand', 'explain', 'why'],
                'question_preferences': ['theoretical', 'cause_effect', 'principles'],
                'evidence_types': ['definitions', 'theoretical_frameworks']
            },
            'applied': {
                'keywords': ['apply', 'use', 'practical', 'real-world', 'solution', 'management', 'conservation'],
                'question_preferences': ['applications', 'case_studies', 'solutions'],
                'evidence_types': ['case_studies', 'applications', 'management_examples']
            }
        }
        
        # Performance tracking categories
        self.performance_categories = {
            'evidence_finding': {
                'indicators': ['found evidence', 'article says', 'page', 'data shows', 'study found'],
                'weight': 0.3
            },
            'analysis_depth': {
                'indicators': ['because', 'therefore', 'this means', 'implies', 'suggests', 'indicates'],
                'weight': 0.25
            },
            'critical_thinking': {
                'indicators': ['however', 'although', 'in contrast', 'alternatively', 'on the other hand'],
                'weight': 0.25
            },
            'synthesis': {
                'indicators': ['connect', 'relationship', 'similar', 'different', 'overall', 'in conclusion'],
                'weight': 0.2
            }
        }
        
        # Difficulty indicators
        self.difficulty_indicators = {
            'struggle_signals': [
                'confused', 'don\'t understand', 'not sure', 'unclear', 'difficult',
                'can\'t find', 'help me', 'what does this mean'
            ],
            'confidence_signals': [
                'understand', 'clear', 'makes sense', 'I think', 'I believe',
                'evidence shows', 'the article explains'
            ],
            'advanced_signals': [
                'furthermore', 'additionally', 'in contrast', 'this suggests',
                'implications', 'broader context', 'synthesis'
            ]
        }
    
    def initialize_database(self):
        """Initialize database tables for personalization data"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Student profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_profiles (
                    student_id TEXT PRIMARY KEY,
                    learning_style TEXT DEFAULT 'mixed',
                    evidence_preference TEXT DEFAULT 'mixed',
                    question_complexity TEXT DEFAULT 'moderate',
                    scaffolding_need TEXT DEFAULT 'medium',
                    performance_metrics TEXT DEFAULT '{}',
                    concept_mastery TEXT DEFAULT '{}',
                    session_patterns TEXT DEFAULT '{}',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_interactions (
                    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    session_id TEXT,
                    interaction_type TEXT,
                    content TEXT,
                    performance_score REAL,
                    learning_indicators TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_profiles (student_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing personalization database: {e}")
    
    def get_or_create_student_profile(self, student_id: str) -> Dict[str, Any]:
        """Get existing student profile or create new one with defaults"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM student_profiles WHERE student_id = ?', (student_id,))
            result = cursor.fetchone()
            
            if result:
                # Parse existing profile
                profile = {
                    'student_id': result[0],
                    'learning_preferences': {
                        'style': result[1],
                        'evidence_preference': result[2],
                        'question_complexity': result[3],
                        'scaffolding_need': result[4]
                    },
                    'performance_history': json.loads(result[5]) if result[5] else {},
                    'concept_mastery': json.loads(result[6]) if result[6] else {},
                    'session_patterns': json.loads(result[7]) if result[7] else {},
                    'last_updated': result[8]
                }
            else:
                # Create new profile with defaults
                profile = {
                    'student_id': student_id,
                    'learning_preferences': {
                        'style': 'mixed',
                        'evidence_preference': 'mixed',
                        'question_complexity': 'moderate',
                        'scaffolding_need': 'medium'
                    },
                    'performance_history': {
                        'evidence_finding_score': 0.5,
                        'analysis_depth_score': 0.5,
                        'critical_thinking_score': 0.5,
                        'synthesis_score': 0.5
                    },
                    'concept_mastery': {},
                    'session_patterns': {
                        'average_questions_per_concept': 0,
                        'evidence_gathering_speed': 'medium',
                        'preferred_question_types': [],
                        'struggle_indicators': []
                    },
                    'last_updated': datetime.now().isoformat()
                }
                
                # Insert new profile
                cursor.execute('''
                    INSERT INTO student_profiles 
                    (student_id, learning_style, evidence_preference, question_complexity, 
                     scaffolding_need, performance_metrics, concept_mastery, session_patterns)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student_id,
                    profile['learning_preferences']['style'],
                    profile['learning_preferences']['evidence_preference'],
                    profile['learning_preferences']['question_complexity'],
                    profile['learning_preferences']['scaffolding_need'],
                    json.dumps(profile['performance_history']),
                    json.dumps(profile['concept_mastery']),
                    json.dumps(profile['session_patterns'])
                ))
                conn.commit()
            
            conn.close()
            return profile
            
        except Exception as e:
            print(f"Error managing student profile: {e}")
            return self._get_default_profile(student_id)
    
    def _get_default_profile(self, student_id: str) -> Dict[str, Any]:
        """Return default profile when database operations fail"""
        return {
            'student_id': student_id,
            'learning_preferences': {
                'style': 'mixed',
                'evidence_preference': 'mixed',
                'question_complexity': 'moderate',
                'scaffolding_need': 'medium'
            },
            'performance_history': {
                'evidence_finding_score': 0.5,
                'analysis_depth_score': 0.5,
                'critical_thinking_score': 0.5,
                'synthesis_score': 0.5
            },
            'concept_mastery': {},
            'session_patterns': {
                'average_questions_per_concept': 0,
                'evidence_gathering_speed': 'medium',
                'preferred_question_types': [],
                'struggle_indicators': []
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def analyze_learning_style(self, chat_history: List[Dict], current_profile: Dict) -> str:
        """
        Analyze student's learning style based on conversation patterns.
        
        Returns: Detected learning style ('visual', 'quantitative', 'conceptual', 'applied', 'mixed')
        """
        style_scores = defaultdict(float)
        
        # Get user messages from chat history
        user_messages = [msg.get('content', '') for msg in chat_history 
                        if msg.get('role') == 'user']
        
        if not user_messages:
            return current_profile['learning_preferences']['style']
        
        # Analyze language patterns for each style
        for style, indicators in self.learning_style_indicators.items():
            style_score = 0
            
            for message in user_messages:
                message_lower = message.lower()
                
                # Count style-specific keywords
                keyword_matches = sum(1 for keyword in indicators['keywords'] 
                                    if keyword in message_lower)
                style_score += keyword_matches
                
                # Bonus for evidence type preferences
                if any(evidence_type in message_lower for evidence_type in indicators['evidence_types']):
                    style_score += 2
            
            # Normalize by number of messages
            style_scores[style] = style_score / len(user_messages) if user_messages else 0
        
        # Determine dominant style (require minimum threshold)
        max_score = max(style_scores.values()) if style_scores else 0
        if max_score >= 0.3:  # Minimum confidence threshold
            dominant_style = max(style_scores, key=style_scores.get)
        else:
            dominant_style = 'mixed'
        
        return dominant_style
    
    def assess_current_performance(self, chat_history: List[Dict], current_question: Dict) -> Dict[str, float]:
        """
        Assess student's performance in current session across key categories.
        
        Returns: Performance scores for evidence finding, analysis, critical thinking, synthesis
        """
        performance_scores = {}
        
        # Get recent user messages (last 10 for current context)
        recent_messages = [msg.get('content', '') for msg in chat_history[-20:] 
                          if msg.get('role') == 'user']
        
        if not recent_messages:
            return {cat: 0.5 for cat in self.performance_categories}
        
        # Analyze performance in each category
        for category, config in self.performance_categories.items():
            category_score = 0
            total_possible = len(recent_messages)
            
            for message in recent_messages:
                message_lower = message.lower()
                
                # Count indicators for this category
                indicator_count = sum(1 for indicator in config['indicators']
                                    if indicator in message_lower)
                
                if indicator_count > 0:
                    category_score += min(1.0, indicator_count / 2)  # Cap per message
            
            # Normalize score (0-1 range)
            performance_scores[category] = min(1.0, category_score / total_possible) if total_possible else 0.5
        
        return performance_scores
    
    def detect_difficulty_level_need(self, chat_history: List[Dict]) -> str:
        """
        Detect if student needs easier, same, or harder difficulty level.
        
        Returns: 'easier', 'maintain', 'harder'
        """
        if len(chat_history) < 6:  # Need some history
            return 'maintain'
        
        recent_messages = [msg.get('content', '') for msg in chat_history[-10:]
                          if msg.get('role') == 'user']
        
        struggle_count = 0
        confidence_count = 0
        advanced_count = 0
        
        for message in recent_messages:
            message_lower = message.lower()
            
            # Count different signal types
            struggle_count += sum(1 for signal in self.difficulty_indicators['struggle_signals']
                                if signal in message_lower)
            confidence_count += sum(1 for signal in self.difficulty_indicators['confidence_signals']
                                  if signal in message_lower)
            advanced_count += sum(1 for signal in self.difficulty_indicators['advanced_signals']
                                if signal in message_lower)
        
        # Decision logic
        if struggle_count > confidence_count + advanced_count:
            return 'easier'
        elif advanced_count > 0 and confidence_count > struggle_count:
            return 'harder'
        else:
            return 'maintain'
    
    def update_concept_mastery(self, student_profile: Dict, concepts: List[str], 
                             performance_score: float) -> Dict[str, float]:
        """
        Update student's mastery level for specific concepts based on performance.
        
        Args:
            student_profile: Current student profile
            concepts: List of concepts covered in current interaction
            performance_score: Overall performance score (0-1)
            
        Returns: Updated concept mastery dictionary
        """
        concept_mastery = student_profile.get('concept_mastery', {})
        
        for concept in concepts:
            current_mastery = concept_mastery.get(concept, 0.5)
            
            # Update mastery with weighted average (70% history, 30% current)
            new_mastery = (current_mastery * 0.7) + (performance_score * 0.3)
            concept_mastery[concept] = min(1.0, max(0.0, new_mastery))
        
        return concept_mastery
    
    def generate_personalized_strategy(self, student_profile: Dict, current_question: Dict, 
                                     chat_history: List[Dict]) -> Dict[str, Any]:
        """
        Generate personalized tutoring strategy based on student profile and current context.
        
        Returns: Strategy configuration for the Socratic engine
        """
        learning_style = student_profile['learning_preferences']['style']
        performance_history = student_profile['performance_history']
        
        # Assess current session
        current_performance = self.assess_current_performance(chat_history, current_question)
        difficulty_need = self.detect_difficulty_level_need(chat_history)
        
        # Generate strategy based on learning style
        strategy = self._get_base_strategy_for_style(learning_style)
        
        # Adjust based on performance
        strategy = self._adjust_strategy_for_performance(strategy, current_performance, performance_history)
        
        # Adjust difficulty
        strategy = self._adjust_strategy_difficulty(strategy, difficulty_need)
        
        return strategy
    
    def _get_base_strategy_for_style(self, learning_style: str) -> Dict[str, Any]:
        """Get base tutoring strategy for specific learning style"""
        
        strategies = {
            'visual': {
                'question_types': ['spatial_relationships', 'visual_examples', 'pattern_recognition'],
                'evidence_focus': ['diagrams', 'figures', 'spatial_data', 'visual_patterns'],
                'language_style': 'descriptive_visual',
                'scaffolding_approach': 'visual_scaffolding'
            },
            'quantitative': {
                'question_types': ['data_analysis', 'quantitative_comparison', 'statistical_interpretation'],
                'evidence_focus': ['statistics', 'measurements', 'quantitative_data', 'calculations'],
                'language_style': 'analytical_precise',
                'scaffolding_approach': 'step_by_step_analysis'
            },
            'conceptual': {
                'question_types': ['theoretical_understanding', 'cause_effect', 'principle_application'],
                'evidence_focus': ['definitions', 'theoretical_frameworks', 'conceptual_explanations'],
                'language_style': 'theoretical_exploratory',
                'scaffolding_approach': 'concept_building'
            },
            'applied': {
                'question_types': ['real_world_application', 'case_studies', 'problem_solving'],
                'evidence_focus': ['case_studies', 'management_examples', 'practical_applications'],
                'language_style': 'practical_contextual',
                'scaffolding_approach': 'scenario_based'
            },
            'mixed': {
                'question_types': ['varied_approach', 'adaptive_questioning'],
                'evidence_focus': ['multi_type_evidence', 'comprehensive_support'],
                'language_style': 'adaptive_varied',
                'scaffolding_approach': 'flexible_support'
            }
        }
        
        return strategies.get(learning_style, strategies['mixed'])
    
    def _adjust_strategy_for_performance(self, strategy: Dict, current_perf: Dict, 
                                       historical_perf: Dict) -> Dict[str, Any]:
        """Adjust strategy based on performance patterns"""
        
        # Identify strongest and weakest areas
        all_scores = {**current_perf, **historical_perf}
        if all_scores:
            weakest_area = min(all_scores, key=all_scores.get)
            strongest_area = max(all_scores, key=all_scores.get)
            
            # Adjust focus based on weaknesses
            if weakest_area == 'evidence_finding':
                strategy['priority_focus'] = 'evidence_discovery'
                strategy['scaffolding_level'] = 'high'
            elif weakest_area == 'analysis_depth':
                strategy['priority_focus'] = 'deeper_analysis'
                strategy['scaffolding_level'] = 'medium'
            elif weakest_area == 'critical_thinking':
                strategy['priority_focus'] = 'critical_evaluation'
                strategy['scaffolding_level'] = 'medium'
            elif weakest_area == 'synthesis':
                strategy['priority_focus'] = 'connections_synthesis'
                strategy['scaffolding_level'] = 'low'
        
        return strategy
    
    def _adjust_strategy_difficulty(self, strategy: Dict, difficulty_need: str) -> Dict[str, Any]:
        """Adjust strategy difficulty based on student signals"""
        
        if difficulty_need == 'easier':
            strategy['complexity_level'] = 'simplified'
            strategy['scaffolding_level'] = 'high'
            strategy['question_pacing'] = 'slower'
        elif difficulty_need == 'harder':
            strategy['complexity_level'] = 'advanced'
            strategy['scaffolding_level'] = 'low'
            strategy['question_pacing'] = 'faster'
        else:  # maintain
            strategy['complexity_level'] = 'moderate'
            strategy['scaffolding_level'] = strategy.get('scaffolding_level', 'medium')
            strategy['question_pacing'] = 'normal'
        
        return strategy
    
    def record_learning_interaction(self, student_id: str, session_id: str, 
                                  interaction_type: str, content: str, 
                                  performance_score: float, learning_indicators: List[str]):
        """Record learning interaction for future analysis"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_interactions 
                (student_id, session_id, interaction_type, content, performance_score, learning_indicators)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                student_id, session_id, interaction_type, content,
                performance_score, json.dumps(learning_indicators)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording learning interaction: {e}")
    
    def update_student_profile(self, student_profile: Dict, session_data: Dict) -> Dict[str, Any]:
        """
        Update student profile based on current session performance and patterns.
        
        Args:
            student_profile: Current profile
            session_data: Data from current session including performance, concepts, interactions
            
        Returns: Updated profile
        """
        # Update learning style based on recent patterns
        if session_data.get('chat_history'):
            new_style = self.analyze_learning_style(session_data['chat_history'], student_profile)
            student_profile['learning_preferences']['style'] = new_style
        
        # Update performance history (weighted average)
        if session_data.get('current_performance'):
            for category, score in session_data['current_performance'].items():
                if category in student_profile['performance_history']:
                    old_score = student_profile['performance_history'][category]
                    # 70% history, 30% current session
                    new_score = (old_score * 0.7) + (score * 0.3)
                    student_profile['performance_history'][category] = new_score
        
        # Update concept mastery
        if session_data.get('concepts_covered'):
            student_profile['concept_mastery'] = self.update_concept_mastery(
                student_profile, 
                session_data['concepts_covered'],
                session_data.get('overall_performance', 0.5)
            )
        
        # Update session patterns
        if session_data.get('session_metrics'):
            patterns = student_profile['session_patterns']
            metrics = session_data['session_metrics']
            
            # Update averages
            if 'questions_per_concept' in metrics:
                current_avg = patterns.get('average_questions_per_concept', 0)
                new_avg = (current_avg * 0.8) + (metrics['questions_per_concept'] * 0.2)
                patterns['average_questions_per_concept'] = new_avg
        
        # Update timestamp
        student_profile['last_updated'] = datetime.now().isoformat()
        
        # Save to database
        self._save_profile_to_database(student_profile)
        
        return student_profile
    
    def _save_profile_to_database(self, profile: Dict):
        """Save updated profile to database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE student_profiles SET
                    learning_style = ?,
                    evidence_preference = ?,
                    question_complexity = ?,
                    scaffolding_need = ?,
                    performance_metrics = ?,
                    concept_mastery = ?,
                    session_patterns = ?,
                    last_updated = ?
                WHERE student_id = ?
            ''', (
                profile['learning_preferences']['style'],
                profile['learning_preferences']['evidence_preference'],
                profile['learning_preferences']['question_complexity'],
                profile['learning_preferences']['scaffolding_need'],
                json.dumps(profile['performance_history']),
                json.dumps(profile['concept_mastery']),
                json.dumps(profile['session_patterns']),
                profile['last_updated'],
                profile['student_id']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving profile to database: {e}")
    
    def get_personalization_summary(self, student_profile: Dict) -> str:
        """
        Generate a human-readable summary of student's personalization profile.
        
        Returns: Formatted summary string
        """
        style = student_profile['learning_preferences']['style']
        performance = student_profile['performance_history']
        
        # Find strengths and areas for improvement
        strengths = [k for k, v in performance.items() if v > 0.7]
        improvements = [k for k, v in performance.items() if v < 0.5]
        
        summary = f"""**Learning Profile for {student_profile['student_id']}**

**Learning Style**: {style.title().replace('_', ' ')}
**Strengths**: {', '.join(s.replace('_', ' ').title() for s in strengths) if strengths else 'Developing across all areas'}
**Focus Areas**: {', '.join(i.replace('_', ' ').title() for i in improvements) if improvements else 'Well-rounded performance'}

**Concepts Mastered**: {len([c for c, m in student_profile.get('concept_mastery', {}).items() if m > 0.7])}
**Scaffolding Level**: {student_profile['learning_preferences']['scaffolding_need'].title()}"""
        
        return summary