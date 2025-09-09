"""
Educational Summary Generation System for EcoCritique
Advanced pedagogical summary creation with multi-level complexity and concept mapping
"""

import json
import sqlite3
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import hashlib

class EducationalSummarySystem:
    """
    Advanced educational summary generation system that creates pedagogically-structured,
    multi-level summaries to enhance student learning and comprehension.
    """
    
    def __init__(self, database_path: str = "ecocritique.db"):
        self.database_path = database_path
        self.initialize_summary_database()
        
        # Educational summary frameworks by complexity level
        self.summary_frameworks = {
            'foundational': {
                'structure': ['definition', 'key_concepts', 'basic_examples', 'why_important'],
                'language_complexity': 'simple',
                'length_target': 200,
                'bloom_levels': ['remember', 'understand'],
                'pedagogical_approach': 'building_blocks'
            },
            'intermediate': {
                'structure': ['overview', 'key_findings', 'methods_used', 'implications', 'connections'],
                'language_complexity': 'moderate',
                'length_target': 400,
                'bloom_levels': ['apply', 'analyze'],
                'pedagogical_approach': 'guided_analysis'
            },
            'advanced': {
                'structure': ['synthesis', 'critical_evaluation', 'research_gaps', 'future_directions', 'broader_context'],
                'language_complexity': 'sophisticated',
                'length_target': 600,
                'bloom_levels': ['evaluate', 'create'],
                'pedagogical_approach': 'independent_thinking'
            }
        }
        
        # Pedagogical summary templates for landscape ecology
        self.pedagogical_templates = {
            'research_study_summary': {
                'sections': ['research_question', 'methodology', 'key_findings', 'significance', 'limitations'],
                'student_guidance': {
                    'foundational': 'Focus on what the researchers discovered and why it matters',
                    'intermediate': 'Analyze how the methods led to the findings and their implications',
                    'advanced': 'Evaluate the study\'s contribution to the field and identify research gaps'
                }
            },
            'concept_explanation_summary': {
                'sections': ['definition', 'key_characteristics', 'examples', 'applications', 'related_concepts'],
                'student_guidance': {
                    'foundational': 'Understand the basic meaning and recognize examples',
                    'intermediate': 'Apply the concept to new situations and make connections',
                    'advanced': 'Critically evaluate the concept\'s role in broader theories'
                }
            },
            'comparative_analysis_summary': {
                'sections': ['comparison_framework', 'similarities', 'differences', 'implications', 'synthesis'],
                'student_guidance': {
                    'foundational': 'Identify what is being compared and the main differences',
                    'intermediate': 'Analyze patterns in similarities and differences',
                    'advanced': 'Synthesize comparisons to develop new insights'
                }
            }
        }
        
        # Concept relationship types for mapping
        self.concept_relationships = {
            'causal': ['causes', 'leads to', 'results in', 'affects', 'influences'],
            'hierarchical': ['is a type of', 'includes', 'contains', 'encompasses'],
            'temporal': ['precedes', 'follows', 'occurs during', 'develops into'],
            'spatial': ['adjacent to', 'within', 'surrounds', 'connects'],
            'correlational': ['correlates with', 'associated with', 'related to', 'corresponds to'],
            'oppositional': ['contrasts with', 'opposes', 'differs from', 'conflicts with']
        }
    
    def initialize_summary_database(self):
        """Initialize database tables for educational summary management"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Educational summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS educational_summaries (
                    summary_id TEXT PRIMARY KEY,
                    content_source_ids TEXT,
                    summary_level TEXT,
                    summary_type TEXT,
                    generated_summary TEXT,
                    concept_map TEXT,
                    pedagogical_notes TEXT,
                    student_context TEXT,
                    effectiveness_rating REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Summary feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summary_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    summary_id TEXT,
                    student_id TEXT,
                    session_id TEXT,
                    helpfulness_rating INTEGER,
                    clarity_rating INTEGER,
                    relevance_rating INTEGER,
                    student_comments TEXT,
                    improvement_suggestions TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (summary_id) REFERENCES educational_summaries (summary_id)
                )
            ''')
            
            # Concept relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS concept_relationships (
                    relationship_id TEXT PRIMARY KEY,
                    concept_a TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    concept_b TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    context_domain TEXT,
                    source_count INTEGER DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing summary database: {e}")
    
    def generate_educational_summary(self, knowledge_sources: List[Dict], 
                                   summary_context: Dict, complexity_level: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate comprehensive educational summary from multiple knowledge sources
        
        Args:
            knowledge_sources: List of knowledge entries to summarize
            summary_context: Context including assignment details, student level, etc.
            complexity_level: 'foundational', 'intermediate', or 'advanced'
            
        Returns:
            Dict containing structured educational summary with metadata
        """
        
        if not knowledge_sources:
            return self._create_empty_summary(summary_context, complexity_level)
        
        # Determine summary type based on content analysis
        summary_type = self._determine_summary_type(knowledge_sources, summary_context)
        
        # Select appropriate framework and template
        framework = self.summary_frameworks[complexity_level]
        template = self.pedagogical_templates.get(summary_type, self.pedagogical_templates['concept_explanation_summary'])
        
        # Extract and organize content
        organized_content = self._organize_content_by_template(knowledge_sources, template, framework)
        
        # Generate concept map
        concept_map = self._generate_concept_map(knowledge_sources, summary_context)
        
        # Create structured summary
        structured_summary = self._create_structured_summary(
            organized_content, template, framework, summary_context, complexity_level
        )
        
        # Generate pedagogical guidance
        pedagogical_guidance = self._generate_pedagogical_guidance(
            structured_summary, template, complexity_level, summary_context
        )
        
        # Create final summary package
        summary_package = {
            'summary_id': self._generate_summary_id(knowledge_sources, summary_context),
            'summary_level': complexity_level,
            'summary_type': summary_type,
            'structured_content': structured_summary,
            'concept_map': concept_map,
            'pedagogical_guidance': pedagogical_guidance,
            'learning_objectives': self._generate_learning_objectives(summary_context, complexity_level),
            'follow_up_questions': self._generate_follow_up_questions(organized_content, complexity_level),
            'metadata': {
                'source_count': len(knowledge_sources),
                'word_count': len(structured_summary.split()),
                'complexity_indicators': self._assess_complexity_indicators(structured_summary),
                'generated_date': datetime.now().isoformat()
            }
        }
        
        # Store summary for future reference
        self._store_educational_summary(summary_package)
        
        return summary_package
    
    def _determine_summary_type(self, knowledge_sources: List[Dict], context: Dict) -> str:
        """Determine the most appropriate summary type based on content analysis"""
        
        # Analyze content patterns
        research_indicators = 0
        concept_indicators = 0
        comparison_indicators = 0
        
        for source in knowledge_sources:
            content = source.get('content', '').lower()
            
            # Research study indicators
            if any(term in content for term in ['study', 'research', 'findings', 'methodology', 'results']):
                research_indicators += 1
            
            # Concept explanation indicators  
            if any(term in content for term in ['defined', 'definition', 'concept', 'characterized by']):
                concept_indicators += 1
            
            # Comparison indicators
            if any(term in content for term in ['compared', 'versus', 'different', 'similar', 'contrast']):
                comparison_indicators += 1
        
        # Determine primary type
        if research_indicators > len(knowledge_sources) * 0.6:
            return 'research_study_summary'
        elif comparison_indicators > len(knowledge_sources) * 0.4:
            return 'comparative_analysis_summary'
        else:
            return 'concept_explanation_summary'
    
    def _organize_content_by_template(self, knowledge_sources: List[Dict], 
                                    template: Dict, framework: Dict) -> Dict[str, List[str]]:
        """Organize content according to the selected pedagogical template"""
        
        organized_content = defaultdict(list)
        
        for source in knowledge_sources:
            content = source.get('content', '')
            
            # Extract content for each template section
            for section in template['sections']:
                section_content = self._extract_section_content(content, section)
                if section_content:
                    organized_content[section].append(section_content)
        
        return dict(organized_content)
    
    def _extract_section_content(self, content: str, section: str) -> str:
        """Extract relevant content for a specific summary section"""
        
        section_keywords = {
            'research_question': ['question', 'hypothesis', 'aim', 'objective', 'investigate'],
            'methodology': ['method', 'approach', 'technique', 'procedure', 'analysis'],
            'key_findings': ['found', 'discovered', 'results', 'showed', 'demonstrated'],
            'significance': ['important', 'significant', 'implications', 'matters', 'relevant'],
            'limitations': ['limitation', 'constraint', 'challenge', 'weakness', 'caveat'],
            'definition': ['defined', 'definition', 'refers to', 'means', 'is characterized'],
            'key_characteristics': ['characteristic', 'feature', 'property', 'attribute'],
            'examples': ['example', 'instance', 'case', 'illustration', 'such as'],
            'applications': ['application', 'used', 'applied', 'practice', 'implementation'],
            'related_concepts': ['related', 'connected', 'associated', 'linked', 'similar']
        }
        
        keywords = section_keywords.get(section, [])
        
        # Find sentences containing section keywords
        sentences = content.split('. ')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            return '. '.join(relevant_sentences[:2])  # Return up to 2 most relevant sentences
        
        return ""
    
    def _generate_concept_map(self, knowledge_sources: List[Dict], context: Dict) -> Dict[str, Any]:
        """Generate concept map showing relationships between key concepts"""
        
        # Extract key concepts from all sources
        all_concepts = []
        for source in knowledge_sources:
            concepts = source.get('metadata', {}).get('concepts', [])
            all_concepts.extend(concepts)
        
        # Add concepts from assignment context
        assignment_concepts = context.get('key_concepts', [])
        all_concepts.extend(assignment_concepts)
        
        # Remove duplicates and normalize
        unique_concepts = list(set([concept.lower().strip() for concept in all_concepts]))
        
        # Identify relationships between concepts
        concept_relationships = self._identify_concept_relationships(knowledge_sources, unique_concepts)
        
        # Create concept map structure
        concept_map = {
            'central_concepts': unique_concepts[:5],  # Top 5 most important concepts
            'relationships': concept_relationships,
            'concept_definitions': self._get_concept_definitions(unique_concepts, knowledge_sources),
            'visual_structure': self._create_visual_concept_structure(unique_concepts, concept_relationships)
        }
        
        return concept_map
    
    def _identify_concept_relationships(self, knowledge_sources: List[Dict], concepts: List[str]) -> List[Dict]:
        """Identify relationships between concepts using content analysis"""
        
        relationships = []
        
        # Combine all content for analysis
        all_content = ' '.join([source.get('content', '') for source in knowledge_sources]).lower()
        
        # Check for relationships between concept pairs
        for i, concept_a in enumerate(concepts):
            for concept_b in concepts[i+1:]:
                
                # Look for relationship indicators in content
                for rel_type, indicators in self.concept_relationships.items():
                    for indicator in indicators:
                        # Check if concepts appear near relationship indicators
                        pattern = f"{concept_a}.{{0,50}}{indicator}.{{0,50}}{concept_b}|{concept_b}.{{0,50}}{indicator}.{{0,50}}{concept_a}"
                        
                        if re.search(pattern, all_content):
                            relationships.append({
                                'concept_a': concept_a,
                                'relationship_type': rel_type,
                                'concept_b': concept_b,
                                'strength': self._calculate_relationship_strength(concept_a, concept_b, all_content),
                                'evidence': indicator
                            })
                            break
        
        # Sort by strength and return top relationships
        relationships.sort(key=lambda x: x['strength'], reverse=True)
        return relationships[:10]  # Return top 10 relationships
    
    def _calculate_relationship_strength(self, concept_a: str, concept_b: str, content: str) -> float:
        """Calculate the strength of relationship between two concepts"""
        
        # Count co-occurrences
        concept_a_count = content.count(concept_a)
        concept_b_count = content.count(concept_b)
        
        # Simple co-occurrence measure
        window_size = 100  # Characters
        cooccurrence_count = 0
        
        # Find all positions of concept_a
        positions_a = [m.start() for m in re.finditer(concept_a, content)]
        
        for pos_a in positions_a:
            # Check if concept_b appears within window
            window_start = max(0, pos_a - window_size)
            window_end = min(len(content), pos_a + window_size)
            window_content = content[window_start:window_end]
            
            if concept_b in window_content:
                cooccurrence_count += 1
        
        # Calculate strength (normalized co-occurrence)
        if concept_a_count > 0 and concept_b_count > 0:
            strength = cooccurrence_count / min(concept_a_count, concept_b_count)
        else:
            strength = 0.0
        
        return min(strength, 1.0)  # Cap at 1.0
    
    def _get_concept_definitions(self, concepts: List[str], knowledge_sources: List[Dict]) -> Dict[str, str]:
        """Extract definitions for key concepts from knowledge sources"""
        
        definitions = {}
        all_content = ' '.join([source.get('content', '') for source in knowledge_sources])
        
        for concept in concepts:
            # Look for definition patterns
            definition_patterns = [
                f"{concept} is defined as ([^.]+)",
                f"{concept} refers to ([^.]+)",
                f"{concept} means ([^.]+)",
                f"{concept} is ([^.]+)"
            ]
            
            for pattern in definition_patterns:
                match = re.search(pattern, all_content, re.IGNORECASE)
                if match:
                    definitions[concept] = match.group(1).strip()
                    break
        
        return definitions
    
    def _create_visual_concept_structure(self, concepts: List[str], relationships: List[Dict]) -> Dict[str, Any]:
        """Create a visual structure representation for concept mapping"""
        
        # Simple hierarchical structure based on relationship frequency
        concept_connections = defaultdict(int)
        
        for rel in relationships:
            concept_connections[rel['concept_a']] += 1
            concept_connections[rel['concept_b']] += 1
        
        # Sort concepts by connection count (centrality)
        sorted_concepts = sorted(concept_connections.items(), key=lambda x: x[1], reverse=True)
        
        visual_structure = {
            'central_node': sorted_concepts[0][0] if sorted_concepts else concepts[0] if concepts else "main_concept",
            'primary_connections': [concept for concept, _ in sorted_concepts[1:4]],
            'secondary_connections': [concept for concept, _ in sorted_concepts[4:8]],
            'relationship_clusters': self._group_relationships_by_type(relationships)
        }
        
        return visual_structure
    
    def _group_relationships_by_type(self, relationships: List[Dict]) -> Dict[str, List[Dict]]:
        """Group relationships by type for visual organization"""
        
        clusters = defaultdict(list)
        
        for rel in relationships:
            rel_type = rel['relationship_type']
            clusters[rel_type].append({
                'concepts': [rel['concept_a'], rel['concept_b']],
                'strength': rel['strength'],
                'evidence': rel['evidence']
            })
        
        return dict(clusters)
    
    def _create_structured_summary(self, organized_content: Dict[str, List[str]], 
                                 template: Dict, framework: Dict, 
                                 context: Dict, complexity_level: str) -> str:
        """Create the final structured summary text"""
        
        summary_parts = []
        student_guidance = template['student_guidance'][complexity_level]
        
        # Add guidance header
        summary_parts.append(f"**Learning Guide:** {student_guidance}\n")
        
        # Build summary sections according to template
        for section in template['sections']:
            if section in organized_content and organized_content[section]:
                
                section_title = section.replace('_', ' ').title()
                summary_parts.append(f"## {section_title}")
                
                # Combine and synthesize content for this section
                section_content = self._synthesize_section_content(
                    organized_content[section], complexity_level, framework
                )
                
                summary_parts.append(section_content)
                summary_parts.append("")  # Empty line for spacing
        
        return "\n".join(summary_parts)
    
    def _synthesize_section_content(self, content_list: List[str], 
                                  complexity_level: str, framework: Dict) -> str:
        """Synthesize multiple content pieces into coherent section"""
        
        if not content_list:
            return "*Content not available for this section*"
        
        # Remove duplicates and combine
        unique_content = []
        seen_content = set()
        
        for content in content_list:
            content_lower = content.lower()
            if content_lower not in seen_content:
                unique_content.append(content)
                seen_content.add(content_lower)
        
        # Adapt language complexity based on level
        if complexity_level == 'foundational':
            return self._simplify_language(' '.join(unique_content[:2]))
        elif complexity_level == 'intermediate':
            return self._moderate_language(' '.join(unique_content[:3]))
        else:  # advanced
            return self._sophisticated_language(' '.join(unique_content))
    
    def _simplify_language(self, content: str) -> str:
        """Simplify language for foundational level"""
        
        # Replace complex terms with simpler alternatives
        simplifications = {
            'demonstrate': 'show',
            'methodology': 'methods',
            'implications': 'what this means',
            'significant': 'important',
            'comprehensive': 'complete',
            'furthermore': 'also',
            'consequently': 'as a result'
        }
        
        simplified = content
        for complex_term, simple_term in simplifications.items():
            simplified = simplified.replace(complex_term, simple_term)
        
        return simplified
    
    def _moderate_language(self, content: str) -> str:
        """Maintain moderate complexity for intermediate level"""
        return content  # Keep original complexity
    
    def _sophisticated_language(self, content: str) -> str:
        """Enhance language sophistication for advanced level"""
        
        # Add transitional phrases and analytical language
        enhancements = {
            '. ': '. Furthermore, ',
            'shows': 'demonstrates',
            'found': 'discovered',
            'important': 'significant',
            'different': 'distinct'
        }
        
        enhanced = content
        for basic, sophisticated in enhancements.items():
            enhanced = enhanced.replace(basic, sophisticated)
        
        return enhanced
    
    def _generate_pedagogical_guidance(self, summary: str, template: Dict, 
                                     complexity_level: str, context: Dict) -> Dict[str, Any]:
        """Generate pedagogical guidance for effective summary use"""
        
        guidance = {
            'how_to_use': self._generate_usage_guidance(complexity_level, context),
            'learning_strategies': self._generate_learning_strategies(complexity_level, template),
            'connection_prompts': self._generate_connection_prompts(context, complexity_level),
            'self_assessment': self._generate_self_assessment_questions(complexity_level, template),
            'next_steps': self._generate_next_steps(complexity_level, context)
        }
        
        return guidance
    
    def _generate_usage_guidance(self, complexity_level: str, context: Dict) -> str:
        """Generate guidance on how to use the summary effectively"""
        
        assignment_title = context.get('assignment_title', 'your assignment')
        
        guidance_by_level = {
            'foundational': f"""Use this summary to build your foundational understanding before diving into {assignment_title}. 
            Focus on understanding the key concepts and definitions first.""",
            
            'intermediate': f"""This summary provides analytical context for {assignment_title}. 
            Use it to identify patterns and make connections with your primary readings.""",
            
            'advanced': f"""This synthesis offers critical perspective for {assignment_title}. 
            Use it to evaluate different viewpoints and develop original insights."""
        }
        
        return guidance_by_level[complexity_level]
    
    def _generate_learning_strategies(self, complexity_level: str, template: Dict) -> List[str]:
        """Generate specific learning strategies based on complexity level"""
        
        strategies_by_level = {
            'foundational': [
                "Read the summary section by section",
                "Look up any unfamiliar terms",
                "Create simple concept maps",
                "Relate examples to your own experience"
            ],
            'intermediate': [
                "Compare findings across different sections",
                "Identify cause-and-effect relationships", 
                "Question the evidence presented",
                "Make connections to your course readings"
            ],
            'advanced': [
                "Critically evaluate the research methods",
                "Identify gaps and limitations in the literature",
                "Synthesize multiple perspectives",
                "Develop original research questions"
            ]
        }
        
        return strategies_by_level[complexity_level]
    
    def _generate_connection_prompts(self, context: Dict, complexity_level: str) -> List[str]:
        """Generate prompts to help students connect summary to their assignment"""
        
        key_concepts = context.get('key_concepts', ['main concepts'])
        question_focus = context.get('question_focus', 'the assignment question')
        
        base_prompts = [
            f"How does this information relate to {question_focus}?",
            f"What evidence here supports your analysis of {key_concepts[0] if key_concepts else 'the main concept'}?",
            "What new questions does this summary raise for you?"
        ]
        
        if complexity_level == 'advanced':
            base_prompts.extend([
                "How might you challenge or extend these findings?",
                "What alternative explanations could be considered?"
            ])
        
        return base_prompts[:3]  # Return top 3 prompts
    
    def _generate_self_assessment_questions(self, complexity_level: str, template: Dict) -> List[str]:
        """Generate self-assessment questions for learning verification"""
        
        questions_by_level = {
            'foundational': [
                "Can you explain the key concepts in your own words?",
                "What examples help you understand these concepts?",
                "Which parts need more clarification?"
            ],
            'intermediate': [
                "How do the different findings connect to each other?",
                "What patterns do you see across the research?",
                "How confident are you in applying these concepts?"
            ],
            'advanced': [
                "What are the strengths and limitations of this research?",
                "How does this challenge your existing understanding?",
                "What original insights can you develop from this synthesis?"
            ]
        }
        
        return questions_by_level[complexity_level]
    
    def _generate_next_steps(self, complexity_level: str, context: Dict) -> List[str]:
        """Generate suggested next steps for continued learning"""
        
        next_steps_by_level = {
            'foundational': [
                "Review your primary course readings with this context in mind",
                "Look for examples of these concepts in your textbook",
                "Discuss key concepts with classmates or instructor"
            ],
            'intermediate': [
                "Apply these analytical frameworks to your assignment",
                "Seek additional sources that support or challenge these findings",
                "Begin drafting your analysis using this foundation"
            ],
            'advanced': [
                "Identify primary sources referenced in this summary",
                "Develop original research questions based on identified gaps",
                "Consider methodological approaches for further investigation"
            ]
        }
        
        return next_steps_by_level[complexity_level]
    
    def _generate_learning_objectives(self, context: Dict, complexity_level: str) -> List[str]:
        """Generate specific learning objectives for the summary"""
        
        bloom_levels = self.summary_frameworks[complexity_level]['bloom_levels']
        key_concepts = context.get('key_concepts', ['key concepts'])
        
        objectives = []
        
        for bloom_level in bloom_levels:
            if bloom_level == 'remember':
                objectives.append(f"Recall key definitions and facts about {', '.join(key_concepts[:2])}")
            elif bloom_level == 'understand':
                objectives.append(f"Explain the relationships between {', '.join(key_concepts[:2])}")
            elif bloom_level == 'apply':
                objectives.append(f"Apply knowledge of {key_concepts[0] if key_concepts else 'these concepts'} to new situations")
            elif bloom_level == 'analyze':
                objectives.append(f"Analyze patterns and relationships in research about {key_concepts[0] if key_concepts else 'the topic'}")
            elif bloom_level == 'evaluate':
                objectives.append(f"Critically evaluate research methods and conclusions")
            elif bloom_level == 'create':
                objectives.append(f"Synthesize information to develop original insights")
        
        return objectives[:3]  # Return top 3 objectives
    
    def _generate_follow_up_questions(self, organized_content: Dict[str, List[str]], 
                                    complexity_level: str) -> List[str]:
        """Generate follow-up questions to encourage deeper thinking"""
        
        questions = []
        
        # Generate questions based on available content sections
        if 'key_findings' in organized_content:
            questions.append("What additional research would strengthen these findings?")
        
        if 'methodology' in organized_content:
            questions.append("How might different research methods change these results?")
        
        if 'implications' in organized_content:
            questions.append("What are the practical applications of these insights?")
        
        # Add complexity-appropriate questions
        if complexity_level == 'advanced':
            questions.extend([
                "What assumptions underlie this research?",
                "How might these findings be challenged or extended?"
            ])
        
        return questions[:4]  # Return top 4 questions
    
    def _create_empty_summary(self, context: Dict, complexity_level: str) -> Dict[str, Any]:
        """Create empty summary structure when no sources are available"""
        
        return {
            'summary_id': 'empty_summary',
            'summary_level': complexity_level,
            'summary_type': 'unavailable',
            'structured_content': "No external sources available for summary generation at this time.",
            'concept_map': {'central_concepts': [], 'relationships': [], 'concept_definitions': {}},
            'pedagogical_guidance': {
                'how_to_use': "Focus on your primary course readings and assignment materials.",
                'learning_strategies': ["Review course materials carefully", "Take detailed notes", "Ask questions in class"],
                'connection_prompts': ["What do you already know about this topic?"],
                'self_assessment': ["What concepts are you most confident about?"],
                'next_steps': ["Review lecture notes and textbook chapters"]
            },
            'learning_objectives': ["Build foundational understanding from primary sources"],
            'follow_up_questions': ["What questions do you have about the assignment?"],
            'metadata': {
                'source_count': 0,
                'word_count': 0,
                'complexity_indicators': {},
                'generated_date': datetime.now().isoformat()
            }
        }
    
    def _generate_summary_id(self, knowledge_sources: List[Dict], context: Dict) -> str:
        """Generate unique ID for summary"""
        
        # Create ID from source content and context
        content_hash = hashlib.md5()
        
        for source in knowledge_sources:
            content_hash.update(source.get('content', '').encode())
        
        context_str = json.dumps(context, sort_keys=True)
        content_hash.update(context_str.encode())
        
        return f"edu_summary_{content_hash.hexdigest()[:12]}"
    
    def _store_educational_summary(self, summary_package: Dict[str, Any]):
        """Store educational summary in database for reuse and analysis"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO educational_summaries 
                (summary_id, summary_level, summary_type, generated_summary, 
                 concept_map, pedagogical_notes, student_context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary_package['summary_id'],
                summary_package['summary_level'],
                summary_package['summary_type'],
                summary_package['structured_content'],
                json.dumps(summary_package['concept_map']),
                json.dumps(summary_package['pedagogical_guidance']),
                json.dumps(summary_package.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing educational summary: {e}")
    
    def _assess_complexity_indicators(self, content: str) -> Dict[str, Any]:
        """Assess complexity indicators in generated summary"""
        
        words = content.split()
        sentences = content.split('.')
        
        # Calculate readability metrics
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        long_words = len([word for word in words if len(word) > 6])
        long_word_percentage = long_words / max(len(words), 1) * 100
        
        # Identify academic language patterns
        academic_terms = ['demonstrate', 'analysis', 'significant', 'methodology', 'implications']
        academic_term_count = sum(1 for term in academic_terms if term.lower() in content.lower())
        
        return {
            'avg_words_per_sentence': round(avg_words_per_sentence, 1),
            'long_word_percentage': round(long_word_percentage, 1),
            'academic_term_count': academic_term_count,
            'total_words': len(words),
            'total_sentences': len(sentences)
        }
    
    def get_summary_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on summary generation and usage"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get summary statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_summaries,
                    AVG(effectiveness_rating) as avg_effectiveness,
                    summary_level,
                    COUNT(*) as level_count
                FROM educational_summaries 
                WHERE created_date >= datetime('now', '-{} days')
                GROUP BY summary_level
            '''.format(days))
            
            level_stats = cursor.fetchall()
            
            # Get feedback statistics
            cursor.execute('''
                SELECT 
                    AVG(helpfulness_rating) as avg_helpfulness,
                    AVG(clarity_rating) as avg_clarity,
                    AVG(relevance_rating) as avg_relevance,
                    COUNT(*) as feedback_count
                FROM summary_feedback 
                WHERE created_date >= datetime('now', '-{} days')
            '''.format(days))
            
            feedback_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'summary_generation': {
                    'total_summaries': sum(stat[3] for stat in level_stats),
                    'by_level': {stat[2]: stat[3] for stat in level_stats},
                    'avg_effectiveness': sum(stat[1] or 0 for stat in level_stats) / max(len(level_stats), 1)
                },
                'feedback_analysis': {
                    'avg_helpfulness': feedback_stats[0] or 0,
                    'avg_clarity': feedback_stats[1] or 0,
                    'avg_relevance': feedback_stats[2] or 0,
                    'total_feedback': feedback_stats[3] or 0
                }
            }
            
        except Exception as e:
            return {
                'error': f"Analytics unavailable: {e}",
                'summary_generation': {'total_summaries': 0},
                'feedback_analysis': {'total_feedback': 0}
            }