"""
Writing Preparation Support System for EcoCritique
Helps students transition from discussion to structured academic writing
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

class WritingPreparationSystem:
    """
    System to guide students from Socratic discussion to structured writing.
    Provides outlines, evidence organization, and writing templates.
    """
    
    def __init__(self):
        self.writing_phases = {
            'evidence_compilation': {
                'description': 'Organizing collected evidence and examples',
                'completion_criteria': ['evidence_found', 'evidence_categorized', 'gaps_identified'],
                'next_phase': 'outline_creation'
            },
            'outline_creation': {
                'description': 'Creating structured outline for response',
                'completion_criteria': ['main_points_identified', 'evidence_mapped', 'logical_flow'],
                'next_phase': 'draft_preparation'
            },
            'draft_preparation': {
                'description': 'Preparing to write first draft',
                'completion_criteria': ['thesis_developed', 'paragraph_plan', 'transitions_planned'],
                'next_phase': 'writing_ready'
            },
            'writing_ready': {
                'description': 'Ready to begin writing assignment',
                'completion_criteria': ['comprehensive_preparation'],
                'next_phase': 'complete'
            }
        }
        
        self.outline_templates = {
            'compare_contrast': {
                'structure': [
                    'Introduction with thesis comparing/contrasting concepts',
                    'Point 1: Similarities between concepts',
                    'Point 2: Key differences',
                    'Point 3: Implications of differences',
                    'Conclusion synthesizing analysis'
                ],
                'evidence_requirements': ['comparative_data', 'specific_examples', 'cited_sources']
            },
            'analysis': {
                'structure': [
                    'Introduction defining key concepts',
                    'Analysis Point 1: Primary factor/cause',
                    'Analysis Point 2: Secondary factors',
                    'Analysis Point 3: Broader implications',
                    'Conclusion with synthesis'
                ],
                'evidence_requirements': ['quantitative_data', 'research_findings', 'examples']
            },
            'definition_explanation': {
                'structure': [
                    'Introduction with clear definition',
                    'Point 1: Key characteristics/components',
                    'Point 2: Examples and applications',
                    'Point 3: Significance and implications',
                    'Conclusion reinforcing understanding'
                ],
                'evidence_requirements': ['academic_definitions', 'concrete_examples', 'applications']
            },
            'problem_solution': {
                'structure': [
                    'Introduction identifying the problem',
                    'Problem analysis and causes',
                    'Solution 1: Primary approach',
                    'Solution 2: Alternative approaches',
                    'Conclusion evaluating solutions'
                ],
                'evidence_requirements': ['problem_data', 'case_studies', 'solution_examples']
            }
        }
        
        self.writing_quality_indicators = {
            'thesis_clarity': [
                'clear_position', 'specific_claim', 'arguable_point', 'focused_scope'
            ],
            'evidence_integration': [
                'specific_citations', 'quantitative_data', 'relevant_examples', 'analysis_connection'
            ],
            'academic_style': [
                'formal_tone', 'discipline_vocabulary', 'logical_transitions', 'objective_voice'
            ],
            'critical_thinking': [
                'analysis_depth', 'synthesis_skill', 'evaluation_present', 'original_insight'
            ]
        }
    
    def assess_writing_readiness(self, chat_history: List[Dict], current_question: Dict, 
                               assignment_context: Dict) -> Dict[str, Any]:
        """
        Assess student's readiness to transition from discussion to writing.
        
        Returns comprehensive assessment of preparation level and gaps.
        """
        readiness_analysis = {
            'current_phase': 'evidence_compilation',
            'completion_score': 0.0,
            'evidence_readiness': 0.0,
            'conceptual_readiness': 0.0,
            'structural_readiness': 0.0,
            'gaps_identified': [],
            'strengths': [],
            'recommended_actions': []
        }
        
        # Analyze chat history for evidence collection
        evidence_count = 0
        concept_mastery_indicators = 0
        structure_indicators = 0
        
        for msg in chat_history:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                
                # Count evidence mentions
                evidence_patterns = ['evidence', 'data', 'study', 'example', 'research', 'page', 'article shows']
                evidence_count += sum(1 for pattern in evidence_patterns if pattern in content)
                
                # Count concept mastery indicators
                concept_patterns = ['because', 'therefore', 'this means', 'implies', 'suggests', 'indicates']
                concept_mastery_indicators += sum(1 for pattern in concept_patterns if pattern in content)
                
                # Count structural thinking indicators
                structure_patterns = ['first', 'second', 'furthermore', 'in contrast', 'similarly', 'however']
                structure_indicators += sum(1 for pattern in structure_patterns if pattern in content)
        
        # Calculate readiness scores
        readiness_analysis['evidence_readiness'] = min(1.0, evidence_count / 8)  # Expect ~8 pieces of evidence
        readiness_analysis['conceptual_readiness'] = min(1.0, concept_mastery_indicators / 5)  # Expect ~5 connections
        readiness_analysis['structural_readiness'] = min(1.0, structure_indicators / 3)  # Expect some organization
        
        # Overall completion score
        readiness_analysis['completion_score'] = (
            readiness_analysis['evidence_readiness'] * 0.5 +
            readiness_analysis['conceptual_readiness'] * 0.3 +
            readiness_analysis['structural_readiness'] * 0.2
        )
        
        # Determine current phase
        if readiness_analysis['completion_score'] < 0.3:
            readiness_analysis['current_phase'] = 'evidence_compilation'
        elif readiness_analysis['completion_score'] < 0.6:
            readiness_analysis['current_phase'] = 'outline_creation'
        elif readiness_analysis['completion_score'] < 0.8:
            readiness_analysis['current_phase'] = 'draft_preparation'
        else:
            readiness_analysis['current_phase'] = 'writing_ready'
        
        # Identify gaps and strengths
        if readiness_analysis['evidence_readiness'] < 0.4:
            readiness_analysis['gaps_identified'].append('Insufficient evidence gathered')
            readiness_analysis['recommended_actions'].append('Find more specific examples and data from article')
        else:
            readiness_analysis['strengths'].append('Good evidence collection')
        
        if readiness_analysis['conceptual_readiness'] < 0.4:
            readiness_analysis['gaps_identified'].append('Need deeper conceptual understanding')
            readiness_analysis['recommended_actions'].append('Explore cause-effect relationships and implications')
        else:
            readiness_analysis['strengths'].append('Strong conceptual grasp')
        
        if readiness_analysis['structural_readiness'] < 0.4:
            readiness_analysis['gaps_identified'].append('Need better organization of ideas')
            readiness_analysis['recommended_actions'].append('Practice organizing points logically')
        else:
            readiness_analysis['strengths'].append('Shows organizational thinking')
        
        return readiness_analysis
    
    def generate_personalized_outline(self, current_question: Dict, chat_history: List[Dict], 
                                    assignment_context: Dict) -> Dict[str, Any]:
        """
        Generate a personalized writing outline based on the student's discussion and evidence.
        
        Returns structured outline with evidence mapping and writing guidance.
        """
        # Determine outline type based on question characteristics
        question_text = current_question.get('prompt', '').lower()
        bloom_level = current_question.get('bloom_level', 'understand').lower()
        
        outline_type = self._determine_outline_type(question_text, bloom_level)
        template = self.outline_templates.get(outline_type, self.outline_templates['analysis'])
        
        # Extract evidence from chat history
        evidence_collected = self._extract_evidence_from_discussion(chat_history)
        
        # Create personalized outline
        personalized_outline = {
            'outline_type': outline_type,
            'question_focus': current_question.get('title', 'Question Analysis'),
            'word_target': assignment_context.get('total_word_count', 'Not specified'),
            'structure': [],
            'evidence_mapping': {},
            'writing_tips': []
        }
        
        # Build structured outline with evidence mapping
        for i, section in enumerate(template['structure']):
            section_content = {
                'section_title': section,
                'suggested_length': f"{self._calculate_section_words(i, len(template['structure']), assignment_context)} words",
                'key_points': [],
                'assigned_evidence': [],
                'writing_guidance': self._get_section_guidance(i, outline_type)
            }
            
            # Map evidence to appropriate sections
            relevant_evidence = self._map_evidence_to_section(evidence_collected, section, i)
            section_content['assigned_evidence'] = relevant_evidence
            
            personalized_outline['structure'].append(section_content)
        
        # Add overall writing tips
        personalized_outline['writing_tips'] = self._generate_writing_tips(
            outline_type, current_question, assignment_context
        )
        
        return personalized_outline
    
    def _determine_outline_type(self, question_text: str, bloom_level: str) -> str:
        """Determine the most appropriate outline type based on question characteristics."""
        
        if any(word in question_text for word in ['compare', 'contrast', 'difference', 'similar']):
            return 'compare_contrast'
        elif any(word in question_text for word in ['problem', 'solution', 'solve', 'address']):
            return 'problem_solution'
        elif any(word in question_text for word in ['define', 'definition', 'what is', 'explain']):
            return 'definition_explanation'
        elif bloom_level in ['analyze', 'evaluate', 'create']:
            return 'analysis'
        else:
            return 'analysis'  # Default to analysis
    
    def _extract_evidence_from_discussion(self, chat_history: List[Dict]) -> List[Dict[str, Any]]:
        """Extract and categorize evidence mentioned in the discussion."""
        
        evidence_items = []
        
        for msg in chat_history:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                
                # Look for quantitative evidence
                numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
                for number in numbers:
                    evidence_items.append({
                        'type': 'quantitative',
                        'content': number,
                        'context': content[:100] + '...' if len(content) > 100 else content,
                        'strength': 'high'
                    })
                
                # Look for citations/references
                citations = re.findall(r'page \d+|p\. \d+|\(.*\d{4}.*\)', content)
                for citation in citations:
                    evidence_items.append({
                        'type': 'citation',
                        'content': citation,
                        'context': content[:100] + '...' if len(content) > 100 else content,
                        'strength': 'high'
                    })
                
                # Look for examples
                if any(word in content.lower() for word in ['example', 'instance', 'case', 'such as']):
                    evidence_items.append({
                        'type': 'example',
                        'content': content[:200] + '...' if len(content) > 200 else content,
                        'context': 'Example from discussion',
                        'strength': 'medium'
                    })
        
        return evidence_items
    
    def _map_evidence_to_section(self, evidence_items: List[Dict], section_title: str, section_index: int) -> List[Dict]:
        """Map evidence items to appropriate outline sections."""
        
        mapped_evidence = []
        
        # Introduction section gets definitions and overview evidence
        if section_index == 0:
            for item in evidence_items:
                if item['type'] in ['citation', 'example'] and len(mapped_evidence) < 2:
                    mapped_evidence.append(item)
        
        # Body sections get substantive evidence
        elif section_index < len(evidence_items):
            # Distribute evidence across body sections
            start_idx = max(0, (section_index - 1) * 2)
            end_idx = min(len(evidence_items), start_idx + 3)
            mapped_evidence = evidence_items[start_idx:end_idx]
        
        return mapped_evidence
    
    def _calculate_section_words(self, section_index: int, total_sections: int, 
                                assignment_context: Dict) -> int:
        """Calculate suggested word count for each section."""
        
        total_words = assignment_context.get('total_word_count', '600-800 words')
        
        # Extract numeric target (use middle of range or single number)
        word_numbers = re.findall(r'\d+', str(total_words))
        if len(word_numbers) >= 2:
            target_words = (int(word_numbers[0]) + int(word_numbers[1])) // 2
        elif len(word_numbers) == 1:
            target_words = int(word_numbers[0])
        else:
            target_words = 700  # Default
        
        # Distribute words: intro (15%), body sections (70%), conclusion (15%)
        if section_index == 0:  # Introduction
            return int(target_words * 0.15)
        elif section_index == total_sections - 1:  # Conclusion
            return int(target_words * 0.15)
        else:  # Body sections
            body_sections = total_sections - 2
            return int(target_words * 0.70 / body_sections) if body_sections > 0 else int(target_words * 0.35)
    
    def _get_section_guidance(self, section_index: int, outline_type: str) -> str:
        """Get writing guidance specific to section and outline type."""
        
        guidance = {
            'compare_contrast': {
                0: "Start with definitions and context. Introduce both concepts clearly.",
                1: "Focus on similarities with specific evidence and examples.",
                2: "Highlight key differences with supporting data.",
                3: "Analyze the significance of these differences.",
                -1: "Synthesize findings and state implications."
            },
            'analysis': {
                0: "Define key terms and establish context.",
                1: "Present your primary analytical point with strong evidence.",
                2: "Develop secondary analysis with supporting details.",
                3: "Explore broader implications and connections.",
                -1: "Synthesize your analysis and reinforce main insights."
            }
        }
        
        section_guidance = guidance.get(outline_type, guidance['analysis'])
        return section_guidance.get(section_index, section_guidance.get(-1, "Develop this point with evidence."))
    
    def _generate_writing_tips(self, outline_type: str, current_question: Dict, 
                              assignment_context: Dict) -> List[str]:
        """Generate specific writing tips based on outline type and question."""
        
        tips = [
            f"Target word count: {assignment_context.get('total_word_count', 'As specified')}",
            "Use specific evidence with proper citations (page numbers)",
            "Connect each piece of evidence to your main argument",
            "Use academic vocabulary and formal tone"
        ]
        
        # Add type-specific tips
        if outline_type == 'compare_contrast':
            tips.extend([
                "Use transition words: 'similarly', 'however', 'in contrast'",
                "Balance discussion of both concepts equally",
                "Focus on significance, not just differences"
            ])
        elif outline_type == 'analysis':
            tips.extend([
                "Use analytical language: 'indicates', 'demonstrates', 'suggests'",
                "Explain the 'why' and 'how', not just the 'what'",
                "Connect analysis to broader ecological concepts"
            ])
        
        # Add question-specific guidance
        required_evidence = current_question.get('required_evidence', '')
        if required_evidence:
            tips.append(f"Required evidence type: {required_evidence}")
        
        return tips
    
    def generate_transition_guidance(self, readiness_analysis: Dict[str, Any], 
                                   current_question: Dict) -> str:
        """
        Generate guidance for transitioning from discussion to writing phase.
        
        Provides phase-specific recommendations and encouragement.
        """
        current_phase = readiness_analysis['current_phase']
        completion_score = readiness_analysis['completion_score']
        
        # Phase-specific guidance
        if current_phase == 'evidence_compilation':
            guidance = f"""## Evidence Compilation Phase

**Current Progress:** {completion_score:.0%} ready for writing

You're in the evidence-gathering stage. Before writing, you need:

"""
            for gap in readiness_analysis['gaps_identified']:
                guidance += f"• {gap}\n"
            
            guidance += f"\n**Next Steps:**\n"
            for action in readiness_analysis['recommended_actions']:
                guidance += f"• {action}\n"
            
            guidance += f"\n**Keep discussing:** Find 2-3 more pieces of specific evidence before outlining."
        
        elif current_phase == 'outline_creation':
            guidance = f"""## Outline Creation Phase

**Current Progress:** {completion_score:.0%} ready for writing

Great evidence collection! Now let's organize your ideas:

**Strengths:** {', '.join(readiness_analysis['strengths'])}

**Ready for outlining:** You have good evidence to structure your response.
Would you like me to help create a personalized outline for your writing?"""
        
        elif current_phase == 'draft_preparation':
            guidance = f"""## Draft Preparation Phase

**Current Progress:** {completion_score:.0%} ready for writing

Excellent preparation! You're almost ready to write:

**Strengths:** {', '.join(readiness_analysis['strengths'])}

**Final steps before writing:**
• Review your evidence organization
• Develop your thesis statement
• Plan transitions between main points

You're well-prepared to begin your draft!"""
        
        else:  # writing_ready
            guidance = f"""## Ready to Write! 

**Writing Readiness:** {completion_score:.0%}

Outstanding preparation! You have:
{chr(10).join('• ' + strength for strength in readiness_analysis['strengths'])}

**You're ready to begin writing your response to {current_question.get('title', 'the question')}.**

Would you like a personalized outline to guide your writing?"""
        
        return guidance
    
    def create_evidence_summary(self, chat_history: List[Dict], current_question: Dict) -> Dict[str, Any]:
        """
        Create a comprehensive summary of evidence gathered during discussion.
        
        Organizes evidence for easy reference during writing.
        """
        evidence_summary = {
            'total_evidence_count': 0,
            'evidence_by_type': {},
            'evidence_by_strength': {'high': [], 'medium': [], 'low': []},
            'evidence_gaps': [],
            'writing_ready_evidence': []
        }
        
        # Extract and categorize all evidence
        all_evidence = self._extract_evidence_from_discussion(chat_history)
        evidence_summary['total_evidence_count'] = len(all_evidence)
        
        # Organize by type and strength
        for evidence in all_evidence:
            evidence_type = evidence['type']
            if evidence_type not in evidence_summary['evidence_by_type']:
                evidence_summary['evidence_by_type'][evidence_type] = []
            evidence_summary['evidence_by_type'][evidence_type].append(evidence)
            
            strength = evidence.get('strength', 'medium')
            evidence_summary['evidence_by_strength'][strength].append(evidence)
        
        # Identify gaps based on question requirements
        required_evidence = current_question.get('required_evidence', '').lower()
        if 'quantitative' in required_evidence and 'quantitative' not in evidence_summary['evidence_by_type']:
            evidence_summary['evidence_gaps'].append('Need quantitative data/statistics')
        
        if 'citation' in required_evidence and 'citation' not in evidence_summary['evidence_by_type']:
            evidence_summary['evidence_gaps'].append('Need proper citations with page numbers')
        
        # Select best evidence for writing
        high_quality = evidence_summary['evidence_by_strength']['high']
        medium_quality = evidence_summary['evidence_by_strength']['medium']
        
        evidence_summary['writing_ready_evidence'] = (high_quality + medium_quality)[:6]  # Top 6 pieces
        
        return evidence_summary