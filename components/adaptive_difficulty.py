"""
Adaptive Difficulty Engine for EcoCritique
Dynamically adjusts question complexity and support based on student performance and comprehension
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import deque
import statistics

class AdaptiveDifficultyEngine:
    """
    Engine that monitors student performance in real-time and adjusts
    question complexity, scaffolding level, and support intensity accordingly.
    """
    
    def __init__(self):
        # Performance tracking window (last N interactions)
        self.performance_window = deque(maxlen=10)
        
        # Difficulty levels and their characteristics
        self.difficulty_levels = {
            'simplified': {
                'complexity_score': 1,
                'scaffolding_intensity': 'high',
                'question_types': ['recall', 'basic_understanding'],
                'evidence_requirements': 'minimal',
                'cognitive_load': 'low'
            },
            'basic': {
                'complexity_score': 2,
                'scaffolding_intensity': 'medium-high',
                'question_types': ['understanding', 'simple_application'],
                'evidence_requirements': 'guided',
                'cognitive_load': 'medium-low'
            },
            'moderate': {
                'complexity_score': 3,
                'scaffolding_intensity': 'medium',
                'question_types': ['application', 'analysis'],
                'evidence_requirements': 'standard',
                'cognitive_load': 'medium'
            },
            'advanced': {
                'complexity_score': 4,
                'scaffolding_intensity': 'low',
                'question_types': ['analysis', 'synthesis'],
                'evidence_requirements': 'comprehensive',
                'cognitive_load': 'high'
            },
            'expert': {
                'complexity_score': 5,
                'scaffolding_intensity': 'minimal',
                'question_types': ['evaluation', 'creation'],
                'evidence_requirements': 'independent',
                'cognitive_load': 'very_high'
            }
        }
        
        # Performance indicators for difficulty adjustment
        self.performance_indicators = {
            'struggling_signals': {
                'language_patterns': [
                    'i don\'t understand', 'this is confusing', 'i\'m lost',
                    'too difficult', 'can\'t figure out', 'makes no sense',
                    'i don\'t know', 'help me', 'what does this mean'
                ],
                'response_patterns': [
                    'very short responses', 'repeated asking for help',
                    'off-topic responses', 'giving up signals'
                ],
                'evidence_quality': 'poor_or_missing',
                'response_time': 'very_long_or_very_short'
            },
            'optimal_challenge_signals': {
                'language_patterns': [
                    'i think', 'based on', 'this suggests', 'i understand',
                    'makes sense', 'i can see', 'the evidence shows'
                ],
                'response_patterns': [
                    'detailed responses', 'building on previous answers',
                    'asking clarifying questions', 'making connections'
                ],
                'evidence_quality': 'good',
                'response_time': 'appropriate'
            },
            'under_challenged_signals': {
                'language_patterns': [
                    'obviously', 'of course', 'that\'s easy', 'simple',
                    'i already know', 'this is basic', 'too easy'
                ],
                'response_patterns': [
                    'very quick responses', 'minimal elaboration',
                    'asking for harder questions', 'showing advanced understanding'
                ],
                'evidence_quality': 'exceeds_requirements',
                'response_time': 'very_fast'
            }
        }
        
        # Scaffolding strategies by intensity
        self.scaffolding_strategies = {
            'minimal': {
                'guidance_level': 'hint_only',
                'question_structure': 'open_ended',
                'feedback_style': 'brief_confirmatory',
                'error_handling': 'minimal_correction'
            },
            'low': {
                'guidance_level': 'directional_prompts',
                'question_structure': 'guided_discovery',
                'feedback_style': 'confirmatory_with_extension',
                'error_handling': 'gentle_redirection'
            },
            'medium': {
                'guidance_level': 'structured_prompts',
                'question_structure': 'step_by_step',
                'feedback_style': 'explanatory',
                'error_handling': 'corrective_with_explanation'
            },
            'medium-high': {
                'guidance_level': 'detailed_guidance',
                'question_structure': 'highly_structured',
                'feedback_style': 'comprehensive_explanation',
                'error_handling': 'detailed_correction_and_example'
            },
            'high': {
                'guidance_level': 'explicit_instruction',
                'question_structure': 'very_small_steps',
                'feedback_style': 'tutorial_style',
                'error_handling': 'comprehensive_support'
            }
        }
    
    def assess_current_performance(self, user_input: str, chat_history: List[Dict], 
                                 current_question: Dict) -> Dict[str, Any]:
        """
        Assess student's current performance level across multiple dimensions.
        
        Returns: Comprehensive performance assessment
        """
        assessment = {
            'overall_performance': 0.5,
            'comprehension_level': 'moderate',
            'evidence_quality': 'adequate',
            'engagement_level': 'normal',
            'cognitive_load_handling': 'appropriate',
            'performance_trend': 'stable',
            'specific_struggles': [],
            'demonstrated_strengths': []
        }
        
        # Analyze current response
        response_analysis = self._analyze_response_quality(user_input, current_question)
        
        # Analyze conversation patterns
        conversation_analysis = self._analyze_conversation_patterns(chat_history)
        
        # Assess comprehension signals
        comprehension_analysis = self._assess_comprehension_signals(user_input, chat_history)
        
        # Combine analyses
        assessment['overall_performance'] = self._calculate_overall_performance(
            response_analysis, conversation_analysis, comprehension_analysis
        )
        
        assessment['comprehension_level'] = comprehension_analysis['level']
        assessment['evidence_quality'] = response_analysis['evidence_quality']
        assessment['engagement_level'] = conversation_analysis['engagement_level']
        assessment['performance_trend'] = self._calculate_performance_trend()
        
        # Identify specific areas
        assessment['specific_struggles'] = self._identify_struggle_areas(
            response_analysis, conversation_analysis, comprehension_analysis
        )
        assessment['demonstrated_strengths'] = self._identify_strength_areas(
            response_analysis, conversation_analysis, comprehension_analysis
        )
        
        # Update performance tracking
        self.performance_window.append(assessment['overall_performance'])
        
        return assessment
    
    def _analyze_response_quality(self, user_input: str, current_question: Dict) -> Dict[str, Any]:
        """Analyze the quality and complexity of student's response"""
        
        analysis = {
            'length_score': 0.0,
            'evidence_quality': 'none',
            'analytical_depth': 0.0,
            'specificity_score': 0.0,
            'complexity_handling': 0.0
        }
        
        input_lower = user_input.lower()
        word_count = len(user_input.split())
        
        # Length appropriateness (not too short, not excessively long)
        if 10 <= word_count <= 100:
            analysis['length_score'] = 1.0
        elif 5 <= word_count < 10:
            analysis['length_score'] = 0.7
        elif word_count < 5:
            analysis['length_score'] = 0.3
        else:  # Very long responses
            analysis['length_score'] = 0.6
        
        # Evidence quality assessment
        evidence_indicators = {
            'strong': ['according to page', 'data shows', 'study found', 'research indicates'],
            'moderate': ['article says', 'page', 'evidence', 'example'],
            'weak': ['i think', 'maybe', 'probably'],
            'none': []
        }
        
        for quality, indicators in evidence_indicators.items():
            if any(indicator in input_lower for indicator in indicators):
                analysis['evidence_quality'] = quality
                break
        else:
            analysis['evidence_quality'] = 'none'
        
        # Analytical depth
        analytical_signals = [
            'because', 'therefore', 'this means', 'implies', 'suggests',
            'indicates', 'demonstrates', 'leads to', 'results in'
        ]
        analysis['analytical_depth'] = min(1.0, sum(1 for signal in analytical_signals 
                                                   if signal in input_lower) / 3)
        
        # Specificity (concrete vs vague)
        specific_indicators = [
            'specific', 'particular', 'exactly', 'precisely', 'detailed',
            'percentage', 'number', 'measurement', 'data'
        ]
        vague_indicators = [
            'generally', 'overall', 'basically', 'kind of', 'sort of',
            'usually', 'typically', 'often'
        ]
        
        specificity_raw = (sum(1 for ind in specific_indicators if ind in input_lower) -
                          sum(1 for ind in vague_indicators if ind in input_lower))
        analysis['specificity_score'] = max(0, min(1, specificity_raw / 2))
        
        return analysis
    
    def _analyze_conversation_patterns(self, chat_history: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in the conversation flow"""
        
        analysis = {
            'engagement_level': 'normal',
            'question_asking_frequency': 0.0,
            'response_consistency': 0.0,
            'learning_progression': 'stable'
        }
        
        user_messages = [msg.get('content', '') for msg in chat_history 
                        if msg.get('role') == 'user']
        
        if len(user_messages) < 3:
            return analysis
        
        # Engagement analysis
        engagement_positive = 0
        engagement_negative = 0
        
        for message in user_messages[-5:]:  # Look at last 5 messages
            message_lower = message.lower()
            
            # Positive engagement signals
            if any(signal in message_lower for signal in ['interesting', 'makes sense', 'i see', 'understand']):
                engagement_positive += 1
            
            # Negative engagement signals
            if any(signal in message_lower for signal in ['boring', 'difficult', 'confused', 'don\'t care']):
                engagement_negative += 1
        
        if engagement_positive > engagement_negative:
            analysis['engagement_level'] = 'high'
        elif engagement_negative > engagement_positive:
            analysis['engagement_level'] = 'low'
        else:
            analysis['engagement_level'] = 'normal'
        
        # Question asking frequency (good learning behavior)
        total_questions = sum(message.count('?') for message in user_messages)
        analysis['question_asking_frequency'] = min(1.0, total_questions / len(user_messages))
        
        return analysis
    
    def _assess_comprehension_signals(self, user_input: str, chat_history: List[Dict]) -> Dict[str, Any]:
        """Assess level of comprehension based on language patterns"""
        
        analysis = {
            'level': 'moderate',
            'confidence_indicators': 0,
            'confusion_indicators': 0,
            'mastery_indicators': 0
        }
        
        input_lower = user_input.lower()
        
        # Count comprehension signals
        confusion_signals = self.performance_indicators['struggling_signals']['language_patterns']
        confidence_signals = self.performance_indicators['optimal_challenge_signals']['language_patterns']
        mastery_signals = self.performance_indicators['under_challenged_signals']['language_patterns']
        
        analysis['confusion_indicators'] = sum(1 for signal in confusion_signals 
                                             if signal in input_lower)
        analysis['confidence_indicators'] = sum(1 for signal in confidence_signals 
                                              if signal in input_lower)
        analysis['mastery_indicators'] = sum(1 for signal in mastery_signals 
                                           if signal in input_lower)
        
        # Determine comprehension level
        if analysis['confusion_indicators'] > analysis['confidence_indicators'] + analysis['mastery_indicators']:
            analysis['level'] = 'struggling'
        elif analysis['mastery_indicators'] > analysis['confidence_indicators'] + analysis['confusion_indicators']:
            analysis['level'] = 'advanced'
        elif analysis['confidence_indicators'] > 0:
            analysis['level'] = 'good'
        else:
            analysis['level'] = 'moderate'
        
        return analysis
    
    def _calculate_overall_performance(self, response_analysis: Dict, 
                                     conversation_analysis: Dict, 
                                     comprehension_analysis: Dict) -> float:
        """Calculate weighted overall performance score"""
        
        # Weight different aspects
        weights = {
            'response_quality': 0.4,
            'comprehension': 0.3,
            'engagement': 0.2,
            'analytical_thinking': 0.1
        }
        
        # Calculate component scores
        response_score = (
            response_analysis['length_score'] * 0.2 +
            {'none': 0, 'weak': 0.3, 'moderate': 0.6, 'strong': 1.0}.get(response_analysis['evidence_quality'], 0.5) * 0.4 +
            response_analysis['analytical_depth'] * 0.2 +
            response_analysis['specificity_score'] * 0.2
        )
        
        comprehension_score = {
            'struggling': 0.2,
            'moderate': 0.5,
            'good': 0.7,
            'advanced': 0.9
        }.get(comprehension_analysis['level'], 0.5)
        
        engagement_score = {
            'low': 0.3,
            'normal': 0.6,
            'high': 0.9
        }.get(conversation_analysis['engagement_level'], 0.6)
        
        # Combine with weights
        overall = (
            response_score * weights['response_quality'] +
            comprehension_score * weights['comprehension'] +
            engagement_score * weights['engagement'] +
            response_analysis['analytical_depth'] * weights['analytical_thinking']
        )
        
        return min(1.0, max(0.0, overall))
    
    def _calculate_performance_trend(self) -> str:
        """Calculate if performance is improving, stable, or declining"""
        
        if len(self.performance_window) < 3:
            return 'insufficient_data'
        
        recent_scores = list(self.performance_window)
        
        # Compare first half to second half of window
        mid_point = len(recent_scores) // 2
        earlier_avg = statistics.mean(recent_scores[:mid_point]) if recent_scores[:mid_point] else 0.5
        later_avg = statistics.mean(recent_scores[mid_point:]) if recent_scores[mid_point:] else 0.5
        
        difference = later_avg - earlier_avg
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _identify_struggle_areas(self, response_analysis: Dict, 
                               conversation_analysis: Dict, 
                               comprehension_analysis: Dict) -> List[str]:
        """Identify specific areas where student is struggling"""
        
        struggles = []
        
        # Evidence-related struggles
        if response_analysis['evidence_quality'] in ['none', 'weak']:
            struggles.append('finding_relevant_evidence')
        
        # Analysis struggles
        if response_analysis['analytical_depth'] < 0.3:
            struggles.append('developing_analytical_insights')
        
        # Comprehension struggles
        if comprehension_analysis['level'] == 'struggling':
            struggles.append('basic_concept_understanding')
        
        # Engagement struggles
        if conversation_analysis['engagement_level'] == 'low':
            struggles.append('maintaining_engagement')
        
        # Specificity struggles
        if response_analysis['specificity_score'] < 0.3:
            struggles.append('providing_specific_details')
        
        return struggles
    
    def _identify_strength_areas(self, response_analysis: Dict, 
                               conversation_analysis: Dict, 
                               comprehension_analysis: Dict) -> List[str]:
        """Identify areas where student is performing well"""
        
        strengths = []
        
        # Evidence strengths
        if response_analysis['evidence_quality'] in ['moderate', 'strong']:
            strengths.append('evidence_integration')
        
        # Analytical strengths
        if response_analysis['analytical_depth'] > 0.6:
            strengths.append('analytical_thinking')
        
        # Comprehension strengths
        if comprehension_analysis['level'] in ['good', 'advanced']:
            strengths.append('concept_comprehension')
        
        # Engagement strengths
        if conversation_analysis['engagement_level'] == 'high':
            strengths.append('active_engagement')
        
        # Question asking (good learning behavior)
        if conversation_analysis['question_asking_frequency'] > 0.3:
            strengths.append('curiosity_and_inquiry')
        
        return strengths
    
    def recommend_difficulty_adjustment(self, performance_assessment: Dict[str, Any],
                                      current_difficulty: str) -> Dict[str, Any]:
        """
        Recommend difficulty adjustment based on performance assessment.
        
        Returns: Recommended difficulty level and specific adjustments
        """
        recommendation = {
            'new_difficulty_level': current_difficulty,
            'adjustment_reason': 'maintain_current',
            'specific_adjustments': [],
            'scaffolding_changes': [],
            'confidence_score': 0.5
        }
        
        overall_performance = performance_assessment['overall_performance']
        trend = performance_assessment['performance_trend']
        struggles = performance_assessment['specific_struggles']
        strengths = performance_assessment['demonstrated_strengths']
        
        # Get current difficulty score
        current_score = self.difficulty_levels.get(current_difficulty, {}).get('complexity_score', 3)
        
        # Adjustment logic
        if overall_performance < 0.3 or 'basic_concept_understanding' in struggles:
            # Significant struggling - reduce difficulty
            if current_score > 1:
                new_level = self._get_difficulty_by_score(current_score - 1)
                recommendation.update({
                    'new_difficulty_level': new_level,
                    'adjustment_reason': 'struggling_significantly',
                    'confidence_score': 0.8
                })
        
        elif overall_performance > 0.8 and len(strengths) >= 2 and trend == 'improving':
            # Strong performance - consider increasing difficulty
            if current_score < 5:
                new_level = self._get_difficulty_by_score(current_score + 1)
                recommendation.update({
                    'new_difficulty_level': new_level,
                    'adjustment_reason': 'performing_excellently',
                    'confidence_score': 0.7
                })
        
        elif 0.4 <= overall_performance <= 0.6 and trend == 'declining':
            # Declining in optimal range - provide more support
            recommendation.update({
                'adjustment_reason': 'provide_more_support',
                'scaffolding_changes': ['increase_guidance', 'more_examples']
            })
        
        # Specific adjustments based on struggle areas
        if 'finding_relevant_evidence' in struggles:
            recommendation['specific_adjustments'].append('evidence_finding_support')
        
        if 'developing_analytical_insights' in struggles:
            recommendation['specific_adjustments'].append('analytical_scaffolding')
        
        if 'maintaining_engagement' in struggles:
            recommendation['specific_adjustments'].append('engagement_strategies')
        
        return recommendation
    
    def _get_difficulty_by_score(self, score: int) -> str:
        """Get difficulty level name by complexity score"""
        score_to_level = {1: 'simplified', 2: 'basic', 3: 'moderate', 4: 'advanced', 5: 'expert'}
        return score_to_level.get(score, 'moderate')
    
    def generate_adaptive_strategy(self, difficulty_level: str, 
                                 performance_assessment: Dict[str, Any],
                                 learning_style: str = 'mixed') -> Dict[str, Any]:
        """
        Generate comprehensive adaptive strategy based on difficulty level and performance.
        
        Returns: Detailed strategy configuration
        """
        base_config = self.difficulty_levels[difficulty_level]
        struggles = performance_assessment['specific_struggles']
        strengths = performance_assessment['demonstrated_strengths']
        
        strategy = {
            'difficulty_level': difficulty_level,
            'complexity_score': base_config['complexity_score'],
            'scaffolding_intensity': base_config['scaffolding_intensity'],
            'question_types': base_config['question_types'].copy(),
            'evidence_requirements': base_config['evidence_requirements'],
            'cognitive_load': base_config['cognitive_load'],
            'personalized_adjustments': [],
            'support_strategies': []
        }
        
        # Adjust based on specific struggles
        if 'finding_relevant_evidence' in struggles:
            strategy['evidence_requirements'] = 'highly_guided'
            strategy['support_strategies'].append('evidence_location_hints')
        
        if 'developing_analytical_insights' in struggles:
            strategy['scaffolding_intensity'] = self._increase_scaffolding_intensity(
                strategy['scaffolding_intensity']
            )
            strategy['support_strategies'].append('analytical_thinking_prompts')
        
        if 'basic_concept_understanding' in struggles:
            strategy['question_types'] = ['recall', 'basic_understanding']
            strategy['support_strategies'].append('concept_clarification')
        
        # Leverage strengths
        if 'analytical_thinking' in strengths:
            strategy['personalized_adjustments'].append('encourage_deeper_analysis')
        
        if 'evidence_integration' in strengths:
            strategy['personalized_adjustments'].append('challenge_evidence_evaluation')
        
        # Adapt to learning style
        if learning_style == 'visual':
            strategy['support_strategies'].append('visual_examples_emphasis')
        elif learning_style == 'quantitative':
            strategy['support_strategies'].append('data_focused_questions')
        elif learning_style == 'applied':
            strategy['support_strategies'].append('real_world_connections')
        
        return strategy
    
    def _increase_scaffolding_intensity(self, current_intensity: str) -> str:
        """Increase scaffolding intensity by one level"""
        intensity_order = ['minimal', 'low', 'medium', 'medium-high', 'high']
        try:
            current_index = intensity_order.index(current_intensity)
            return intensity_order[min(current_index + 1, len(intensity_order) - 1)]
        except ValueError:
            return 'medium'
    
    def get_difficulty_explanation(self, difficulty_level: str) -> str:
        """Get human-readable explanation of difficulty level"""
        explanations = {
            'simplified': "Using basic questions with lots of guidance to build foundational understanding",
            'basic': "Working with fundamental concepts using structured support", 
            'moderate': "Applying standard academic analysis with balanced guidance",
            'advanced': "Engaging in complex analysis with minimal scaffolding",
            'expert': "Tackling sophisticated evaluation and synthesis independently"
        }
        
        return explanations.get(difficulty_level, "Working at an appropriate challenge level")
    
    def get_performance_insights(self, performance_assessment: Dict[str, Any]) -> str:
        """Generate human-readable insights about student performance"""
        
        performance = performance_assessment['overall_performance']
        trend = performance_assessment['performance_trend']
        struggles = performance_assessment['specific_struggles']
        strengths = performance_assessment['demonstrated_strengths']
        
        insights = []
        
        # Overall performance insight
        if performance >= 0.8:
            insights.append("Demonstrating strong academic performance")
        elif performance >= 0.6:
            insights.append("Showing solid understanding and engagement")
        elif performance >= 0.4:
            insights.append("Making steady progress with room for improvement")
        else:
            insights.append("Working through challenges - additional support recommended")
        
        # Trend insight
        if trend == 'improving':
            insights.append("Performance is improving over time")
        elif trend == 'declining':
            insights.append("May benefit from strategy adjustment")
        
        # Strengths insight
        if strengths:
            insights.append(f"Key strengths: {', '.join(strengths[:2])}")
        
        # Struggles insight
        if struggles:
            insights.append(f"Focus areas: {', '.join(struggles[:2])}")
        
        return " • ".join(insights)