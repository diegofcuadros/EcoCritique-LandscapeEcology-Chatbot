"""
Conversation Checkpoint System for EcoCritique
Monitors conversation quality and provides regular assessment and reorientation opportunities
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import re

class ConversationCheckpoint:
    """
    System that monitors conversation flow, generates summaries every 5 questions,
    and provides opportunities for reorientation and strategy adjustment.
    """
    
    def __init__(self, database_path: str = "ecocritique.db"):
        self.database_path = database_path
        self.initialize_database()
        
        # Conversation quality indicators
        self.quality_indicators = {
            'focus_maintenance': {
                'positive_signals': [
                    'evidence from article', 'page', 'according to', 'the study shows',
                    'data indicates', 'author states', 'research demonstrates'
                ],
                'negative_signals': [
                    'in general', 'overall', 'what about', 'tell me about',
                    'explain everything', 'broadly speaking'
                ]
            },
            'progress_indicators': {
                'evidence_gathering': [
                    'found', 'article says', 'page', 'data', 'study', 'research',
                    'example', 'statistics', 'measurement'
                ],
                'analysis_development': [
                    'because', 'therefore', 'this means', 'implies', 'suggests',
                    'indicates', 'demonstrates', 'shows that'
                ],
                'synthesis_formation': [
                    'connect', 'relationship', 'similar', 'different', 'overall',
                    'in conclusion', 'synthesis', 'brings together'
                ]
            },
            'engagement_signals': {
                'high_engagement': [
                    'interesting', 'i see', 'that makes sense', 'good point',
                    'i understand', 'clear', 'helpful'
                ],
                'confusion_signals': [
                    'confused', 'unclear', 'don\'t understand', 'not sure',
                    'difficult', 'help', 'what does this mean'
                ],
                'disengagement_signals': [
                    'i don\'t know', 'whatever', 'sure', 'ok', 'fine',
                    'i guess', 'maybe'
                ]
            }
        }
        
        # Checkpoint response templates
        self.checkpoint_templates = {
            'progress_good': """## 📋 Progress Check - You're doing well! 

**What we've accomplished:**
{progress_summary}

**Your learning shows:**
{learning_indicators}

**This discussion is helping you {progress_description}.**

**Quick check:** Is this approach working for you?
• ✅ **Yes, keep going** - This is helping me understand the assignment
• 🔄 **Adjust focus** - Let's concentrate more on specific assignment requirements  
• 📚 **Change approach** - I'd learn better with a different strategy
• ❓ **I have questions** about something we discussed

Your response will help me tailor our discussion to your learning needs.""",
            
            'needs_refocus': """## 📋 Progress Check - Let's refocus

**What we've covered:**
{progress_summary}

**I notice we may be drifting from the core assignment question.** 

**The assignment asks:** {assignment_focus}

**Let's realign our discussion:**
• 🎯 **Refocus on assignment** - Get back to the specific question requirements
• 📖 **Find more evidence** - Look for concrete support from the article
• 🔍 **Clarify the question** - Make sure we understand what's being asked
• 💡 **Different approach** - Try a new strategy to tackle this question

How would you like to proceed?""",
            
            'struggling_support': """## 📋 Progress Check - Let's adjust our approach

**I can see you're working hard on this!** Here's what we've covered:
{progress_summary}

**It seems like you might benefit from:**
{support_suggestions}

**What would help you most right now?**
• 🔧 **Simpler approach** - Break this down into smaller, clearer steps
• 📚 **More examples** - See additional examples to understand the concept
• 🎯 **Specific guidance** - Get direct help finding the right evidence
• 🔄 **Start over** - Approach this question from a completely different angle

I'm here to support your learning in whatever way works best for you.""",
            
            'ready_to_advance': """## 📋 Progress Check - Great work!

**Your understanding is developing well:**
{progress_summary}

**You've shown strong:**
{strengths_identified}

**You seem ready for the next level:**
• 📝 **Writing preparation** - Start organizing your ideas for writing
• 🔬 **Deeper analysis** - Explore more complex aspects of this topic
• 🔗 **Making connections** - Link this to broader ecological concepts
• ➡️ **Next question** - Move forward to the next assignment question

Which direction interests you most?"""
        }
    
    def initialize_database(self):
        """Initialize database tables for checkpoint data"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Conversation checkpoints table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_checkpoints (
                    checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    session_id TEXT,
                    checkpoint_number INTEGER,
                    questions_since_last INTEGER,
                    conversation_summary TEXT,
                    quality_assessment TEXT,
                    student_response TEXT,
                    effectiveness_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Session question tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_questions (
                    session_id TEXT,
                    student_id TEXT,
                    question_number INTEGER,
                    question_content TEXT,
                    response_quality REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, question_number)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing checkpoint database: {e}")
    
    def should_trigger_checkpoint(self, chat_history: List[Dict], session_id: str) -> bool:
        """
        Determine if a checkpoint should be triggered based on conversation length.
        
        Returns: True if checkpoint should be triggered (every 5 user questions)
        """
        # Count user questions in current session
        user_questions = [msg for msg in chat_history if msg.get('role') == 'user']
        
        # Get the last checkpoint for this session
        last_checkpoint_question_count = self._get_last_checkpoint_question_count(session_id)
        
        # Trigger every 5 questions since last checkpoint
        questions_since_checkpoint = len(user_questions) - last_checkpoint_question_count
        
        return questions_since_checkpoint >= 5
    
    def _get_last_checkpoint_question_count(self, session_id: str) -> int:
        """Get the number of questions at the time of last checkpoint"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT MAX(checkpoint_number * 5) as last_question_count
                FROM conversation_checkpoints 
                WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result[0] else 0
            
        except Exception as e:
            print(f"Error getting last checkpoint: {e}")
            return 0
    
    def generate_conversation_summary(self, chat_history: List[Dict], 
                                   current_question: Dict, assignment_context: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive summary of conversation progress and quality.
        
        Returns: Summary data including progress, quality metrics, and recommendations
        """
        # Get user messages since last checkpoint
        user_messages = [msg for msg in chat_history if msg.get('role') == 'user']
        recent_messages = user_messages[-5:] if len(user_messages) >= 5 else user_messages
        
        # Analyze conversation quality
        quality_assessment = self._assess_conversation_quality(recent_messages, current_question)
        
        # Generate progress summary
        progress_summary = self._generate_progress_summary(recent_messages, current_question)
        
        # Identify learning indicators
        learning_indicators = self._identify_learning_indicators(recent_messages)
        
        # Determine conversation effectiveness
        effectiveness_score = self._calculate_effectiveness_score(quality_assessment)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(quality_assessment, effectiveness_score)
        
        return {
            'checkpoint_number': len(user_messages) // 5,
            'questions_analyzed': len(recent_messages),
            'progress_summary': progress_summary,
            'quality_assessment': quality_assessment,
            'learning_indicators': learning_indicators,
            'effectiveness_score': effectiveness_score,
            'recommendations': recommendations,
            'conversation_state': self._determine_conversation_state(effectiveness_score, quality_assessment)
        }
    
    def _assess_conversation_quality(self, messages: List[Dict], current_question: Dict) -> Dict[str, Any]:
        """Assess various aspects of conversation quality"""
        
        quality = {
            'focus_score': 0.0,
            'progress_score': 0.0,
            'engagement_score': 0.0,
            'evidence_score': 0.0,
            'analysis_score': 0.0
        }
        
        if not messages:
            return quality
        
        combined_text = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Focus maintenance score
        focus_positive = sum(1 for signal in self.quality_indicators['focus_maintenance']['positive_signals']
                           if signal in combined_text)
        focus_negative = sum(1 for signal in self.quality_indicators['focus_maintenance']['negative_signals']
                           if signal in combined_text)
        quality['focus_score'] = max(0, min(1, (focus_positive - focus_negative) / max(1, len(messages))))
        
        # Progress score (evidence → analysis → synthesis)
        evidence_count = sum(1 for signal in self.quality_indicators['progress_indicators']['evidence_gathering']
                           if signal in combined_text)
        analysis_count = sum(1 for signal in self.quality_indicators['progress_indicators']['analysis_development']
                           if signal in combined_text)
        synthesis_count = sum(1 for signal in self.quality_indicators['progress_indicators']['synthesis_formation']
                            if signal in combined_text)
        
        quality['evidence_score'] = min(1, evidence_count / max(1, len(messages)))
        quality['analysis_score'] = min(1, analysis_count / max(1, len(messages)))
        quality['progress_score'] = (quality['evidence_score'] + quality['analysis_score']) / 2
        
        # Engagement score
        high_engagement = sum(1 for signal in self.quality_indicators['engagement_signals']['high_engagement']
                            if signal in combined_text)
        confusion = sum(1 for signal in self.quality_indicators['engagement_signals']['confusion_signals']
                      if signal in combined_text)
        disengagement = sum(1 for signal in self.quality_indicators['engagement_signals']['disengagement_signals']
                          if signal in combined_text)
        
        engagement_raw = high_engagement - (confusion * 0.5) - (disengagement * 0.8)
        quality['engagement_score'] = max(0, min(1, engagement_raw / max(1, len(messages))))
        
        return quality
    
    def _generate_progress_summary(self, messages: List[Dict], current_question: Dict) -> str:
        """Generate human-readable progress summary"""
        
        if not messages:
            return "Just getting started with the discussion."
        
        # Analyze what has been accomplished
        combined_text = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        accomplishments = []
        
        # Evidence gathering
        evidence_indicators = ['found', 'article says', 'page', 'data', 'study']
        if any(indicator in combined_text for indicator in evidence_indicators):
            accomplishments.append("✅ Found relevant evidence from the article")
        
        # Analysis development  
        analysis_indicators = ['because', 'therefore', 'this means', 'implies']
        if any(indicator in combined_text for indicator in analysis_indicators):
            accomplishments.append("✅ Developed analytical insights")
        
        # Concept understanding
        concept_indicators = ['understand', 'clear', 'makes sense', 'definition']
        if any(indicator in combined_text for indicator in concept_indicators):
            accomplishments.append("✅ Grasped key concepts")
        
        # Connections and synthesis
        synthesis_indicators = ['connect', 'relationship', 'similar', 'different']
        if any(indicator in combined_text for indicator in synthesis_indicators):
            accomplishments.append("✅ Making connections between ideas")
        
        if not accomplishments:
            accomplishments = ["🔄 Working on understanding the question requirements"]
        
        return '\n'.join(accomplishments)
    
    def _identify_learning_indicators(self, messages: List[Dict]) -> List[str]:
        """Identify specific learning behaviors and progress indicators"""
        
        indicators = []
        combined_text = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Evidence-based reasoning
        if any(phrase in combined_text for phrase in ['according to', 'the article shows', 'evidence indicates']):
            indicators.append("Strong evidence-based reasoning")
        
        # Critical thinking
        if any(phrase in combined_text for phrase in ['however', 'although', 'in contrast', 'on the other hand']):
            indicators.append("Critical thinking and evaluation")
        
        # Depth of analysis
        if any(phrase in combined_text for phrase in ['implications', 'significance', 'broader context']):
            indicators.append("Deep analytical thinking")
        
        # Synthesis abilities
        if any(phrase in combined_text for phrase in ['overall', 'in conclusion', 'bringing together']):
            indicators.append("Synthesis and integration skills")
        
        # Active engagement
        if any(phrase in combined_text for phrase in ['i think', 'i believe', 'my understanding']):
            indicators.append("Active intellectual engagement")
        
        # Question asking (good learning behavior)
        question_count = combined_text.count('?')
        if question_count >= 2:
            indicators.append("Asking clarifying questions")
        
        return indicators if indicators else ["Working on foundational understanding"]
    
    def _calculate_effectiveness_score(self, quality_assessment: Dict[str, float]) -> float:
        """Calculate overall conversation effectiveness score"""
        
        weights = {
            'focus_score': 0.3,
            'progress_score': 0.3,
            'engagement_score': 0.2,
            'evidence_score': 0.1,
            'analysis_score': 0.1
        }
        
        effectiveness = sum(quality_assessment[key] * weight 
                          for key, weight in weights.items()
                          if key in quality_assessment)
        
        return min(1.0, max(0.0, effectiveness))
    
    def _generate_recommendations(self, quality_assessment: Dict, effectiveness_score: float) -> List[str]:
        """Generate specific recommendations based on conversation analysis"""
        
        recommendations = []
        
        # Focus-related recommendations
        if quality_assessment['focus_score'] < 0.4:
            recommendations.append("Refocus discussion on specific assignment requirements")
        
        # Evidence-related recommendations
        if quality_assessment['evidence_score'] < 0.3:
            recommendations.append("Spend more time finding concrete evidence from the article")
        
        # Analysis-related recommendations
        if quality_assessment['analysis_score'] < 0.3:
            recommendations.append("Work on developing deeper analytical insights")
        
        # Engagement-related recommendations
        if quality_assessment['engagement_score'] < 0.4:
            recommendations.append("Try a different approach to increase engagement")
        
        # Progress-related recommendations
        if quality_assessment['progress_score'] < 0.4:
            recommendations.append("Break down the question into smaller, manageable parts")
        elif quality_assessment['progress_score'] > 0.7:
            recommendations.append("Consider advancing to writing preparation or next question")
        
        return recommendations if recommendations else ["Continue current approach - it's working well"]
    
    def _determine_conversation_state(self, effectiveness_score: float, 
                                   quality_assessment: Dict[str, float]) -> str:
        """Determine overall conversation state for template selection"""
        
        if effectiveness_score >= 0.7:
            return 'ready_to_advance'
        elif effectiveness_score >= 0.5:
            return 'progress_good'
        elif quality_assessment.get('focus_score', 0) < 0.4:
            return 'needs_refocus'
        else:
            return 'struggling_support'
    
    def generate_checkpoint_response(self, summary_data: Dict[str, Any], 
                                   current_question: Dict, assignment_context: Dict) -> str:
        """
        Generate the actual checkpoint response that will be shown to the student.
        
        Returns: Formatted checkpoint message
        """
        conversation_state = summary_data['conversation_state']
        template = self.checkpoint_templates.get(conversation_state, self.checkpoint_templates['progress_good'])
        
        # Prepare template variables
        template_vars = {
            'progress_summary': summary_data['progress_summary'],
            'learning_indicators': '\n'.join(f"• {indicator}" for indicator in summary_data['learning_indicators']),
            'assignment_focus': current_question.get('title', 'the current question'),
            'progress_description': self._get_progress_description(summary_data),
            'support_suggestions': self._get_support_suggestions(summary_data),
            'strengths_identified': self._get_strengths_summary(summary_data)
        }
        
        # Format template
        formatted_response = template.format(**template_vars)
        
        return formatted_response
    
    def _get_progress_description(self, summary_data: Dict) -> str:
        """Get description of current progress level"""
        effectiveness = summary_data['effectiveness_score']
        
        if effectiveness >= 0.8:
            return "develop strong understanding and analytical skills"
        elif effectiveness >= 0.6:
            return "build solid comprehension of the concepts"
        elif effectiveness >= 0.4:
            return "work through the learning process step by step"
        else:
            return "explore the topic and find your footing"
    
    def _get_support_suggestions(self, summary_data: Dict) -> str:
        """Get specific support suggestions for struggling students"""
        recommendations = summary_data['recommendations']
        
        if not recommendations:
            return "• Breaking concepts into smaller pieces\n• More concrete examples and guidance"
        
        return '\n'.join(f"• {rec}" for rec in recommendations[:3])
    
    def _get_strengths_summary(self, summary_data: Dict) -> str:
        """Get summary of identified student strengths"""
        indicators = summary_data['learning_indicators']
        
        if not indicators:
            return "• Persistence and willingness to engage with challenging material"
        
        return '\n'.join(f"• {indicator}" for indicator in indicators[:3])
    
    def record_checkpoint(self, student_id: str, session_id: str, summary_data: Dict[str, Any]):
        """Record checkpoint data to database for analysis"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_checkpoints 
                (student_id, session_id, checkpoint_number, questions_since_last,
                 conversation_summary, quality_assessment, effectiveness_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id, session_id, summary_data['checkpoint_number'], 
                summary_data['questions_analyzed'], json.dumps(summary_data['progress_summary']),
                json.dumps(summary_data['quality_assessment']), summary_data['effectiveness_score']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording checkpoint: {e}")
    
    def record_student_checkpoint_response(self, student_id: str, session_id: str, 
                                         checkpoint_number: int, student_response: str):
        """Record student's response to checkpoint for learning"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE conversation_checkpoints 
                SET student_response = ?
                WHERE student_id = ? AND session_id = ? AND checkpoint_number = ?
            ''', (student_response, student_id, session_id, checkpoint_number))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording student response: {e}")
    
    def get_checkpoint_analytics(self, student_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics about student's checkpoint patterns"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get recent checkpoints
            cursor.execute('''
                SELECT effectiveness_score, quality_assessment, timestamp
                FROM conversation_checkpoints 
                WHERE student_id = ? AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days), (student_id,))
            
            checkpoints = cursor.fetchall()
            conn.close()
            
            if not checkpoints:
                return {'total_checkpoints': 0, 'average_effectiveness': 0.0}
            
            # Analyze patterns
            effectiveness_scores = [cp[0] for cp in checkpoints if cp[0]]
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
            
            return {
                'total_checkpoints': len(checkpoints),
                'average_effectiveness': avg_effectiveness,
                'improvement_trend': self._calculate_improvement_trend(effectiveness_scores),
                'most_recent_effectiveness': effectiveness_scores[0] if effectiveness_scores else 0
            }
            
        except Exception as e:
            print(f"Error getting checkpoint analytics: {e}")
            return {'total_checkpoints': 0, 'average_effectiveness': 0.0}
    
    def _calculate_improvement_trend(self, scores: List[float]) -> str:
        """Calculate if student is improving, stable, or declining"""
        if len(scores) < 3:
            return 'insufficient_data'
        
        recent_avg = sum(scores[:3]) / 3
        older_avg = sum(scores[-3:]) / 3
        
        if recent_avg > older_avg + 0.1:
            return 'improving'
        elif recent_avg < older_avg - 0.1:
            return 'declining'
        else:
            return 'stable'