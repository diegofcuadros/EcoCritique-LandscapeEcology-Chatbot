"""
Evidence Guidance System for EcoCritique
Provides targeted coaching for finding and using evidence effectively in academic writing
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

class EvidenceGuidanceSystem:
    """
    Advanced system for guiding students to find, analyze, and use evidence effectively.
    Provides targeted coaching based on current evidence quality and assignment requirements.
    """
    
    def __init__(self):
        self.evidence_types = {
            'quantitative_data': {
                'patterns': [r'\d+%', r'\d+\.\d+', r'significant.*difference', r'correlation', 
                           r'p\s*[<>=]\s*0\.\d+', r'n\s*=\s*\d+', r'statistical', r'data shows'],
                'quality_weight': 0.9,
                'description': 'Numerical data, statistics, measurements'
            },
            'study_results': {
                'patterns': [r'study found', r'research shows', r'experiment', r'trial', 
                           r'observed', r'measured', r'demonstrated', r'investigation'],
                'quality_weight': 0.8,
                'description': 'Research findings and experimental results'
            },
            'examples': {
                'patterns': [r'for example', r'for instance', r'such as', r'including', 
                           r'case study', r'exemplified by'],
                'quality_weight': 0.6,
                'description': 'Concrete examples and case studies'
            },
            'citations': {
                'patterns': [r'\(.*\d{4}.*\)', r'according to', r'as noted by', 
                           r'page \d+', r'p\. \d+', r'et al\.'],
                'quality_weight': 0.7,
                'description': 'Proper academic citations and references'
            },
            'definitions': {
                'patterns': [r'defined as', r'definition', r'refers to', r'means', 
                           r'is described as', r'can be understood as'],
                'quality_weight': 0.5,
                'description': 'Definitions and conceptual explanations'
            }
        }
        
        self.evidence_quality_indicators = {
            'high_quality': [
                'specific numbers', 'peer-reviewed', 'controlled study', 'significant results',
                'multiple sources', 'meta-analysis', 'longitudinal study', 'sample size'
            ],
            'medium_quality': [
                'case study', 'observational', 'preliminary', 'suggests', 'indicates',
                'correlation', 'comparison', 'survey data'
            ],
            'needs_improvement': [
                'general statement', 'opinion', 'unsupported claim', 'vague reference',
                'no citation', 'personal belief', 'common knowledge'
            ]
        }
        
        self.coaching_strategies = {
            'no_evidence': {
                'strategy': 'evidence_seeking',
                'prompts': [
                    "What specific information from the article supports your point?",
                    "Can you find any data or examples that relate to this concept?",
                    "Look for concrete evidence - numbers, study results, or specific examples."
                ]
            },
            'weak_evidence': {
                'strategy': 'evidence_strengthening',
                'prompts': [
                    "Can you find more specific details to support this point?",
                    "What quantitative data does the article provide about this?",
                    "Are there any study results that demonstrate this concept?"
                ]
            },
            'good_evidence': {
                'strategy': 'analysis_deepening',
                'prompts': [
                    "How does this evidence specifically answer the question?",
                    "What implications does this data have for the broader concept?",
                    "How might you connect this evidence to other parts of the article?"
                ]
            },
            'strong_evidence': {
                'strategy': 'synthesis_promotion',
                'prompts': [
                    "How does this evidence compare to other findings in the article?",
                    "What patterns do you see across different pieces of evidence?",
                    "How might you use this evidence to build your argument?"
                ]
            }
        }
    
    def analyze_evidence_quality(self, user_input: str, chat_history: List[Dict], 
                                current_question: Dict) -> Dict[str, Any]:
        """
        Analyze the quality and completeness of evidence in student's response.
        
        Returns comprehensive analysis of evidence use and suggestions for improvement.
        """
        evidence_analysis = {
            'evidence_found': [],
            'evidence_types': [],
            'quality_score': 0.0,
            'completeness_score': 0.0,
            'specific_gaps': [],
            'strengths': [],
            'improvement_areas': []
        }
        
        # Detect evidence types in current input
        total_weight = 0
        weighted_score = 0
        
        for evidence_type, config in self.evidence_types.items():
            matches = []
            for pattern in config['patterns']:
                found_matches = re.findall(pattern, user_input.lower())
                matches.extend(found_matches)
            
            if matches:
                evidence_analysis['evidence_types'].append(evidence_type)
                evidence_analysis['evidence_found'].extend(matches[:3])  # Limit to 3 examples
                weighted_score += config['quality_weight'] * min(len(matches), 3) / 3
                total_weight += config['quality_weight']
        
        # Calculate overall quality score
        if total_weight > 0:
            evidence_analysis['quality_score'] = weighted_score / total_weight
        
        # Assess evidence quality indicators
        high_quality_count = sum(1 for indicator in self.evidence_quality_indicators['high_quality']
                               if indicator in user_input.lower())
        medium_quality_count = sum(1 for indicator in self.evidence_quality_indicators['medium_quality']
                                 if indicator in user_input.lower())
        low_quality_count = sum(1 for indicator in self.evidence_quality_indicators['needs_improvement']
                              if indicator in user_input.lower())
        
        # Assess completeness based on question requirements
        question_requirements = current_question.get('required_evidence', '').lower()
        required_elements = self._extract_required_evidence_elements(question_requirements)
        
        completeness_score = 0
        if required_elements:
            found_elements = sum(1 for element in required_elements
                               if any(element in user_input.lower() for element in required_elements))
            completeness_score = found_elements / len(required_elements)
        else:
            # General completeness heuristics
            completeness_score = min(1.0, len(evidence_analysis['evidence_types']) / 3)
        
        evidence_analysis['completeness_score'] = completeness_score
        
        # Identify strengths and gaps
        if high_quality_count > 0:
            evidence_analysis['strengths'].append("Uses high-quality evidence")
        if 'quantitative_data' in evidence_analysis['evidence_types']:
            evidence_analysis['strengths'].append("Includes numerical data")
        if 'citations' in evidence_analysis['evidence_types']:
            evidence_analysis['strengths'].append("Provides proper citations")
        
        # Identify improvement areas
        if evidence_analysis['quality_score'] < 0.3:
            evidence_analysis['improvement_areas'].append("Need more specific evidence")
        if 'quantitative_data' not in evidence_analysis['evidence_types']:
            evidence_analysis['improvement_areas'].append("Consider including numerical data")
        if completeness_score < 0.5:
            evidence_analysis['improvement_areas'].append("Address all parts of the question")
        if low_quality_count > high_quality_count + medium_quality_count:
            evidence_analysis['improvement_areas'].append("Use more academic evidence")
        
        return evidence_analysis
    
    def _extract_required_evidence_elements(self, requirements_text: str) -> List[str]:
        """Extract specific evidence requirements from question text."""
        elements = []
        
        # Common evidence requirements
        requirement_patterns = {
            'citations': ['citation', 'reference', 'page'],
            'data': ['data', 'numbers', 'statistics', 'percentage'],
            'examples': ['example', 'case', 'instance'],
            'comparison': ['compare', 'contrast', 'difference'],
            'analysis': ['analyze', 'explain', 'interpret']
        }
        
        for element, patterns in requirement_patterns.items():
            if any(pattern in requirements_text for pattern in patterns):
                elements.append(element)
        
        return elements
    
    def generate_evidence_coaching(self, evidence_analysis: Dict[str, Any], 
                                 current_question: Dict, assignment_context: Dict) -> str:
        """
        Generate targeted coaching based on evidence analysis.
        
        Provides specific guidance for finding and improving evidence use.
        """
        quality_score = evidence_analysis['quality_score']
        completeness_score = evidence_analysis['completeness_score']
        
        # Determine coaching strategy
        if quality_score < 0.2 or not evidence_analysis['evidence_found']:
            strategy = self.coaching_strategies['no_evidence']
            coaching_level = 'foundational'
        elif quality_score < 0.5:
            strategy = self.coaching_strategies['weak_evidence'] 
            coaching_level = 'developing'
        elif quality_score < 0.8:
            strategy = self.coaching_strategies['good_evidence']
            coaching_level = 'proficient'
        else:
            strategy = self.coaching_strategies['strong_evidence']
            coaching_level = 'advanced'
        
        # Build coaching response
        coaching_response = ""
        
        # Acknowledge strengths first
        if evidence_analysis['strengths']:
            coaching_response += "**Good work:** " + ", ".join(evidence_analysis['strengths'][:2]) + ".\n\n"
        
        # Provide targeted guidance based on gaps
        if evidence_analysis['improvement_areas']:
            coaching_response += "**To strengthen your analysis:**\n"
            for i, area in enumerate(evidence_analysis['improvement_areas'][:3]):
                coaching_response += f"{i+1}. {area}\n"
            coaching_response += "\n"
        
        # Add specific coaching prompt
        import random
        coaching_prompt = random.choice(strategy['prompts'])
        coaching_response += f"**Guiding question:** {coaching_prompt}\n\n"
        
        # Add context-specific suggestions
        question_type = current_question.get('bloom_level', 'understand').lower()
        
        if question_type in ['analyze', 'evaluate', 'create']:
            coaching_response += "**For this analytical question:** Look for cause-and-effect relationships, patterns, or comparisons in the article.\n"
        elif question_type in ['apply', 'understand']:
            coaching_response += "**For this question:** Focus on finding concrete examples and clear explanations from the text.\n"
        else:
            coaching_response += "**Research tip:** Look for specific details, data, or examples that directly address the question.\n"
        
        return coaching_response.strip()
    
    def suggest_evidence_search_strategies(self, current_question: Dict, 
                                         article_context: str) -> Dict[str, Any]:
        """
        Provide specific strategies for finding relevant evidence in the article.
        
        Returns targeted search suggestions based on question type and content.
        """
        question_text = current_question.get('prompt', '').lower()
        question_type = current_question.get('bloom_level', 'understand').lower()
        
        strategies = {
            'search_terms': [],
            'section_recommendations': [],
            'evidence_types_to_find': [],
            'specific_guidance': []
        }
        
        # Extract key concepts from question
        key_concepts = current_question.get('key_concepts', [])
        if key_concepts:
            strategies['search_terms'].extend(key_concepts[:4])
        
        # Add question-specific search terms
        question_words = re.findall(r'\b\w{4,}\b', question_text)
        strategies['search_terms'].extend(question_words[:6])
        
        # Recommend evidence types based on question
        if any(word in question_text for word in ['how many', 'percentage', 'rate', 'number']):
            strategies['evidence_types_to_find'].append('quantitative_data')
            strategies['specific_guidance'].append("Look for numbers, percentages, or statistical data")
        
        if any(word in question_text for word in ['compare', 'contrast', 'difference', 'similar']):
            strategies['evidence_types_to_find'].append('study_results')
            strategies['specific_guidance'].append("Find examples that show similarities or differences")
        
        if question_type in ['analyze', 'evaluate']:
            strategies['evidence_types_to_find'].extend(['study_results', 'quantitative_data'])
            strategies['specific_guidance'].append("Look for research findings and data that support analysis")
        
        # Section recommendations based on article structure
        if 'method' in article_context.lower():
            strategies['section_recommendations'].append("Methods section for study details")
        if 'result' in article_context.lower():
            strategies['section_recommendations'].append("Results section for findings and data")
        if 'discussion' in article_context.lower():
            strategies['section_recommendations'].append("Discussion section for interpretation")
        
        return strategies
    
    def track_evidence_progression(self, chat_history: List[Dict], 
                                 current_question: Dict) -> Dict[str, Any]:
        """
        Track how student's evidence use has improved throughout the conversation.
        
        Provides insights into learning progression and areas still needing work.
        """
        progression_analysis = {
            'initial_quality': 0.0,
            'current_quality': 0.0,
            'improvement_trend': 'stable',
            'evidence_type_progression': {},
            'coaching_effectiveness': 'unknown',
            'next_development_area': ''
        }
        
        if len(chat_history) < 2:
            return progression_analysis
        
        # Analyze first few and recent messages
        early_messages = [msg for msg in chat_history[:3] if msg.get('role') == 'user']
        recent_messages = [msg for msg in chat_history[-3:] if msg.get('role') == 'user']
        
        if early_messages:
            early_analysis = self.analyze_evidence_quality(
                ' '.join(msg.get('content', '') for msg in early_messages),
                [], current_question
            )
            progression_analysis['initial_quality'] = early_analysis['quality_score']
        
        if recent_messages:
            recent_analysis = self.analyze_evidence_quality(
                ' '.join(msg.get('content', '') for msg in recent_messages),
                [], current_question
            )
            progression_analysis['current_quality'] = recent_analysis['quality_score']
        
        # Determine improvement trend
        quality_change = progression_analysis['current_quality'] - progression_analysis['initial_quality']
        if quality_change > 0.15:
            progression_analysis['improvement_trend'] = 'improving'
            progression_analysis['coaching_effectiveness'] = 'effective'
        elif quality_change < -0.1:
            progression_analysis['improvement_trend'] = 'declining'
            progression_analysis['coaching_effectiveness'] = 'needs_adjustment'
        else:
            progression_analysis['improvement_trend'] = 'stable'
            
        # Recommend next development area
        if progression_analysis['current_quality'] < 0.3:
            progression_analysis['next_development_area'] = 'finding_basic_evidence'
        elif progression_analysis['current_quality'] < 0.6:
            progression_analysis['next_development_area'] = 'evidence_quality'
        elif progression_analysis['current_quality'] < 0.8:
            progression_analysis['next_development_area'] = 'evidence_analysis'
        else:
            progression_analysis['next_development_area'] = 'evidence_synthesis'
        
        return progression_analysis
    
    def generate_evidence_feedback_summary(self, evidence_analysis: Dict[str, Any], 
                                         progression_analysis: Dict[str, Any]) -> str:
        """
        Generate a comprehensive summary of evidence use for assignment completion.
        
        Provides actionable feedback for writing preparation.
        """
        summary = "## Evidence Use Summary\n\n"
        
        # Overall performance
        quality_score = evidence_analysis['quality_score']
        if quality_score >= 0.8:
            summary += "**Overall Evidence Quality: Excellent** ✅\n"
        elif quality_score >= 0.6:
            summary += "**Overall Evidence Quality: Good** ⚠️\n"
        elif quality_score >= 0.4:
            summary += "**Overall Evidence Quality: Developing** ⚠️\n"
        else:
            summary += "**Overall Evidence Quality: Needs Improvement** ❌\n"
        
        # Strengths
        if evidence_analysis['strengths']:
            summary += f"\n**Strengths:**\n"
            for strength in evidence_analysis['strengths']:
                summary += f"- {strength}\n"
        
        # Areas for improvement
        if evidence_analysis['improvement_areas']:
            summary += f"\n**Focus Areas for Writing:**\n"
            for area in evidence_analysis['improvement_areas']:
                summary += f"- {area}\n"
        
        # Progress tracking
        if progression_analysis['improvement_trend'] == 'improving':
            summary += f"\n**Progress:** Your evidence use has improved during our discussion! 📈\n"
        elif progression_analysis['improvement_trend'] == 'declining':
            summary += f"\n**Note:** Let's refocus on finding stronger evidence sources. 📉\n"
        
        # Next steps
        next_area = progression_analysis.get('next_development_area', '')
        if next_area:
            summary += f"\n**Next Development Focus:** {next_area.replace('_', ' ').title()}\n"
        
        return summary