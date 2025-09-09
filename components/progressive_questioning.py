"""
Progressive Questioning System - Manages question complexity progression based on student demonstration
Generates Bloom's taxonomy appropriate questions and scaffolds learning toward assignment goals
"""

import streamlit as st
import re
import random
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

class ProgressiveQuestioningSystem:
    """Manages question complexity progression based on student demonstration"""
    
    def __init__(self):
        # Bloom's taxonomy question templates by level
        self.bloom_question_templates = {
            "remember": {
                "starters": ["What", "Who", "When", "Where", "Which", "List", "Name", "Define"],
                "templates": [
                    "What does {concept} mean according to the article?",
                    "Where in the article do the authors discuss {topic}?", 
                    "What are the key characteristics of {concept} mentioned?",
                    "List the main {elements} described in this section.",
                    "Who conducted the research on {topic}?",
                    "When did the study on {subject} take place?",
                    "Define {term} as presented in the article."
                ],
                "evidence_focus": "direct_quotes_and_definitions"
            },
            "understand": {
                "starters": ["Explain", "Describe", "Summarize", "Interpret", "Compare", "Contrast"],
                "templates": [
                    "How would you explain {concept} in your own words?",
                    "What is the relationship between {concept1} and {concept2}?",
                    "Describe the process of {process} outlined in the article.",
                    "How do the authors interpret the {data/results}?",
                    "What does the evidence suggest about {phenomenon}?",
                    "Summarize the main argument regarding {topic}.",
                    "Compare {concept1} with {concept2} based on the article."
                ],
                "evidence_focus": "examples_and_explanations"
            },
            "apply": {
                "starters": ["How would", "What would happen", "Apply", "Use", "Demonstrate", "Solve"],
                "templates": [
                    "How would you apply {concept} to {scenario}?",
                    "What would happen if {condition} changed in this system?",
                    "How could {method} be used to address {problem}?",
                    "Apply the concept of {concept} to your local area.",
                    "Use the evidence to predict {outcome}.",
                    "How would {principle} work in {different_context}?",
                    "Demonstrate how {concept} applies to {real_world_example}."
                ],
                "evidence_focus": "practical_applications_and_examples"
            },
            "analyze": {
                "starters": ["Why", "How", "What factors", "What patterns", "Analyze", "Examine"],
                "templates": [
                    "Why do you think {phenomenon} occurs according to the evidence?",
                    "What patterns do you notice in {data/results}?",
                    "How do the different pieces of evidence support {conclusion}?",
                    "What factors contribute to {outcome} based on the study?",
                    "Analyze the relationship between {variable1} and {variable2}.",
                    "What evidence supports the authors' claim about {topic}?",
                    "How does {factor} influence {outcome} in this system?"
                ],
                "evidence_focus": "data_patterns_and_relationships"
            },
            "evaluate": {
                "starters": ["Judge", "Critique", "Assess", "Evaluate", "How effective", "How valid"],
                "templates": [
                    "How convincing is the evidence for {claim}?",
                    "What are the strengths and limitations of {approach/method}?",
                    "How valid are the authors' conclusions about {topic}?",
                    "Evaluate the effectiveness of {solution/strategy}.",
                    "What alternative explanations might exist for {results}?",
                    "Judge the quality of evidence presented for {argument}.",
                    "How well does {theory} explain {phenomenon}?"
                ],
                "evidence_focus": "critical_assessment_and_alternatives"
            },
            "create": {
                "starters": ["Design", "Develop", "Create", "Propose", "Generate", "Construct"],
                "templates": [
                    "Design a study to test {hypothesis}.",
                    "Propose an alternative approach to {problem}.",
                    "Create a management plan using {principles}.",
                    "Develop a hypothesis about {phenomenon}.",
                    "Generate solutions for {challenge} based on the evidence.",
                    "Construct an argument that synthesizes {multiple_concepts}.",
                    "Design an experiment to investigate {question}."
                ],
                "evidence_focus": "synthesis_and_innovation"
            }
        }
        
        # Scaffolding question sequences for each level
        self.scaffolding_sequences = {
            "comprehension_to_analysis": [
                "What specific evidence did you find?",
                "How does this evidence relate to the question?",
                "What patterns do you see in this evidence?",
                "Why might these patterns be significant?"
            ],
            "analysis_to_evaluation": [
                "What does your analysis suggest?",
                "How strong is the evidence for this conclusion?", 
                "What limitations or alternative explanations exist?",
                "How would you judge the overall argument?"
            ],
            "evidence_gathering_to_synthesis": [
                "What different pieces of evidence have you collected?",
                "How do these pieces connect to each other?",
                "What larger pattern or argument emerges?",
                "How does this synthesis address the assignment question?"
            ]
        }
        
        # Evidence-focused question types
        self.evidence_question_types = {
            "discovery": [
                "What specific section of the article addresses {topic}?",
                "Where do you see evidence of {concept} in the text?",
                "What data or examples support {claim}?",
                "Find a quote that illustrates {principle}."
            ],
            "interpretation": [
                "What do you think this evidence means?",
                "How would you interpret {data/results}?",
                "What significance do you see in {finding}?",
                "How does this evidence support the authors' argument?"
            ],
            "connection": [
                "How does this evidence relate to {other_evidence}?",
                "What connections do you see between {concept1} and {concept2}?",
                "How does this finding connect to {broader_topic}?",
                "What relationships emerge from combining this evidence?"
            ],
            "evaluation": [
                "How reliable is this evidence?",
                "What makes this evidence convincing or unconvincing?",
                "How does this evidence compare to {other_source}?",
                "What questions does this evidence raise?"
            ]
        }
        
        # Context-specific question modifiers
        self.context_modifiers = {
            "landscape_ecology": {
                "concepts": ["fragmentation", "connectivity", "patch", "corridor", "matrix", "scale", 
                           "disturbance", "habitat", "edge effect", "metapopulation"],
                "processes": ["succession", "dispersal", "migration", "colonization", "extinction"],
                "methods": ["remote sensing", "GIS analysis", "field survey", "modeling"],
                "applications": ["conservation", "restoration", "planning", "management"]
            }
        }
        
        # Question complexity indicators
        self.complexity_levels = {
            "low": {
                "characteristics": ["single_concept", "direct_answer", "factual_recall"],
                "indicators": ["what", "where", "when", "who", "define", "list"]
            },
            "medium": {
                "characteristics": ["concept_relationships", "cause_effect", "comparison"],
                "indicators": ["how", "why", "compare", "relationship", "process"]
            },
            "high": {
                "characteristics": ["multiple_concepts", "evaluation", "synthesis"],
                "indicators": ["evaluate", "critique", "synthesize", "alternative", "implications"]
            }
        }
    
    def generate_bloom_appropriate_questions(self, target_level: str, content_context: Dict, 
                                           current_understanding: Dict) -> List[str]:
        """
        Create questions matching required Bloom's taxonomy level
        
        Args:
            target_level: Bloom's level (remember, understand, apply, analyze, evaluate, create)
            content_context: Context including concepts, article content, assignment details
            current_understanding: Student's current comprehension assessment
            
        Returns:
            List of contextually appropriate questions for the target level
        """
        if target_level not in self.bloom_question_templates:
            target_level = "understand"  # Default fallback
        
        templates = self.bloom_question_templates[target_level]["templates"]
        questions = []
        
        # Extract context information
        key_concepts = content_context.get("key_concepts", [])
        article_topics = content_context.get("topics", [])
        assignment_focus = content_context.get("assignment_focus", "")
        
        # Generate questions using templates
        for template in templates[:4]:  # Use first 4 templates for variety
            try:
                # Fill in template with context-appropriate content
                question = self._fill_question_template(
                    template, key_concepts, article_topics, assignment_focus
                )
                if question and question not in questions:
                    questions.append(question)
            except Exception:
                continue  # Skip if template filling fails
        
        # Add evidence-focused questions
        evidence_focus = self.bloom_question_templates[target_level]["evidence_focus"]
        evidence_questions = self._generate_evidence_focused_questions(
            evidence_focus, content_context, target_level
        )
        questions.extend(evidence_questions[:2])  # Add 2 evidence questions
        
        # Ensure questions are appropriate for current understanding
        questions = self._filter_questions_for_understanding(
            questions, current_understanding, target_level
        )
        
        return questions[:5]  # Return top 5 most appropriate questions
    
    def scaffold_learning_progression(self, current_understanding: str, target_goals: Dict, 
                                    content_context: Dict) -> List[str]:
        """
        Build bridge questions from current level to assignment requirements
        
        Args:
            current_understanding: Student's current comprehension level
            target_goals: Assignment goals and requirements
            content_context: Article and assignment context
            
        Returns:
            List of scaffolding questions to bridge the learning gap
        """
        scaffolding_questions = []
        
        # Determine appropriate scaffolding sequence
        target_level = target_goals.get("bloom_level", "analyze")
        understanding_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        
        try:
            current_index = understanding_levels.index(current_understanding)
            target_index = understanding_levels.index(target_level)
        except ValueError:
            # Default progression if levels not found
            current_index = 1  # understand
            target_index = 3   # analyze
        
        # Generate progression questions
        if target_index > current_index:
            for level_index in range(current_index, min(target_index + 1, len(understanding_levels))):
                level = understanding_levels[level_index]
                level_questions = self.generate_bloom_appropriate_questions(
                    level, content_context, {"primary_level": current_understanding}
                )
                scaffolding_questions.extend(level_questions[:2])  # 2 questions per level
        
        # Add specific scaffolding sequences
        if current_understanding == "understand" and target_level in ["analyze", "evaluate"]:
            sequence_key = "comprehension_to_analysis"
            if sequence_key in self.scaffolding_sequences:
                sequence_questions = self._contextualize_scaffolding_sequence(
                    self.scaffolding_sequences[sequence_key], content_context
                )
                scaffolding_questions.extend(sequence_questions)
        
        return scaffolding_questions[:6]  # Return top 6 scaffolding questions
    
    def adapt_question_complexity(self, student_response_quality: Dict, question_metadata: Dict, 
                                content_context: Dict) -> List[str]:
        """
        Adjust question difficulty based on student performance
        
        Args:
            student_response_quality: Assessment of student's recent responses
            question_metadata: Information about current assignment question
            content_context: Article and assignment context
            
        Returns:
            List of adapted questions appropriate for demonstrated ability
        """
        adapted_questions = []
        
        # Assess demonstrated complexity level
        response_indicators = student_response_quality.get("complexity_indicators", [])
        evidence_quality = student_response_quality.get("evidence_quality", "low")
        analytical_depth = student_response_quality.get("analytical_depth", "surface")
        
        # Determine appropriate complexity adjustment
        if evidence_quality == "high" and analytical_depth in ["deep", "critical"]:
            # Increase complexity
            complexity_adjustment = "increase"
            target_complexity = "high"
        elif evidence_quality == "low" or analytical_depth == "surface":
            # Decrease complexity  
            complexity_adjustment = "decrease"
            target_complexity = "low"
        else:
            # Maintain current level
            complexity_adjustment = "maintain"
            target_complexity = "medium"
        
        # Generate questions with adjusted complexity
        current_bloom_level = question_metadata.get("bloom_level", "understand")
        
        if complexity_adjustment == "increase":
            # Move to next Bloom's level
            next_level = self._get_next_bloom_level(current_bloom_level)
            adapted_questions = self.generate_bloom_appropriate_questions(
                next_level, content_context, {"primary_level": current_bloom_level}
            )
        elif complexity_adjustment == "decrease":
            # Move to previous Bloom's level or provide more scaffolding
            prev_level = self._get_previous_bloom_level(current_bloom_level)
            adapted_questions = self.scaffold_learning_progression(
                prev_level, {"bloom_level": current_bloom_level}, content_context
            )
        else:
            # Generate questions at current level with different focus
            adapted_questions = self.generate_bloom_appropriate_questions(
                current_bloom_level, content_context, {"primary_level": current_bloom_level}
            )
        
        # Add complexity-specific guidance
        if target_complexity == "low":
            guidance_questions = self._generate_foundational_questions(content_context)
            adapted_questions.extend(guidance_questions[:2])
        elif target_complexity == "high":
            advanced_questions = self._generate_advanced_questions(content_context, question_metadata)
            adapted_questions.extend(advanced_questions[:2])
        
        return adapted_questions[:5]
    
    def generate_evidence_focused_questions(self, evidence_type: str, content_context: Dict, 
                                          current_question: Dict) -> List[str]:
        """
        Generate questions specifically focused on evidence gathering and analysis
        
        Args:
            evidence_type: Type of evidence focus (discovery, interpretation, connection, evaluation)
            content_context: Article and assignment context
            current_question: Current assignment question details
            
        Returns:
            List of evidence-focused questions
        """
        if evidence_type not in self.evidence_question_types:
            evidence_type = "discovery"  # Default fallback
        
        question_templates = self.evidence_question_types[evidence_type]
        evidence_questions = []
        
        # Extract relevant context
        key_concepts = content_context.get("key_concepts", [])
        required_evidence = current_question.get("required_evidence", "")
        question_focus = current_question.get("title", "")
        
        # Generate evidence-focused questions
        for template in question_templates:
            try:
                # Contextualize template
                question = self._fill_evidence_template(
                    template, key_concepts, required_evidence, question_focus
                )
                if question and question not in evidence_questions:
                    evidence_questions.append(question)
            except Exception:
                continue
        
        # Add question-specific evidence guidance
        if required_evidence:
            specific_questions = self._generate_specific_evidence_questions(
                required_evidence, content_context
            )
            evidence_questions.extend(specific_questions[:2])
        
        return evidence_questions[:4]
    
    def generate_writing_preparation_questions(self, collected_evidence: List[str], 
                                             assignment_context: Dict, 
                                             current_progress: Dict) -> List[str]:
        """
        Generate questions to help students organize their analysis for writing
        
        Args:
            collected_evidence: Evidence student has gathered so far
            assignment_context: Full assignment context and requirements
            current_progress: Student's current progress through assignment
            
        Returns:
            List of writing preparation questions
        """
        writing_questions = []
        
        # Assess writing readiness
        evidence_count = len(collected_evidence)
        questions_completed = len(current_progress.get("questions_completed", []))
        total_questions = len(assignment_context.get("all_questions", []))
        
        # Generate organization questions
        if evidence_count >= 2:
            writing_questions.extend([
                "How would you organize your evidence to build a coherent argument?",
                "What's the strongest piece of evidence you've found, and why?",
                "How do your different pieces of evidence connect to each other?"
            ])
        
        # Generate synthesis questions
        if questions_completed >= 2:
            writing_questions.extend([
                "What common themes emerge across your responses to different questions?",
                "How do your answers to the previous questions inform this current question?",
                "What overarching argument is developing from your analysis?"
            ])
        
        # Generate completion questions
        if questions_completed / total_questions >= 0.7:  # 70% complete
            writing_questions.extend([
                "How would you summarize your key findings for this assignment?",
                "What conclusions can you draw from your overall analysis?",
                "How does your analysis address the main assignment goals?"
            ])
        
        # Add assignment-specific writing guidance
        word_target = assignment_context.get("total_word_count", "")
        if word_target:
            writing_questions.append(
                f"How would you structure your response to meet the {word_target} requirement?"
            )
        
        return writing_questions[:5]
    
    def _fill_question_template(self, template: str, concepts: List[str], topics: List[str], 
                              focus: str) -> str:
        """Fill question template with contextually appropriate content"""
        
        # Simple template filling - can be enhanced with more sophisticated NLP
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        filled_template = template
        for placeholder in placeholders:
            replacement = self._get_replacement_for_placeholder(
                placeholder, concepts, topics, focus
            )
            filled_template = filled_template.replace(f"{{{placeholder}}}", replacement)
        
        return filled_template
    
    def _get_replacement_for_placeholder(self, placeholder: str, concepts: List[str], 
                                       topics: List[str], focus: str) -> str:
        """Get appropriate replacement for template placeholder"""
        
        placeholder_lower = placeholder.lower()
        
        # Concept-related placeholders
        if "concept" in placeholder_lower and concepts:
            return random.choice(concepts[:3])  # Choose from top 3 concepts
        
        # Topic-related placeholders
        if "topic" in placeholder_lower and topics:
            return random.choice(topics[:3])
        
        # Process-related placeholders
        if "process" in placeholder_lower:
            processes = ["fragmentation", "succession", "dispersal", "colonization"]
            return random.choice(processes)
        
        # Method-related placeholders
        if "method" in placeholder_lower:
            methods = ["field study", "remote sensing", "modeling", "analysis"]
            return random.choice(methods)
        
        # Default fallbacks
        fallbacks = {
            "concept": "ecological pattern",
            "topic": "landscape structure", 
            "phenomenon": "ecological process",
            "data": "research findings",
            "results": "study results"
        }
        
        return fallbacks.get(placeholder_lower.split()[0], "the subject")
    
    def _generate_evidence_focused_questions(self, evidence_focus: str, content_context: Dict, 
                                           target_level: str) -> List[str]:
        """Generate questions focused on specific types of evidence"""
        
        evidence_questions = []
        key_concepts = content_context.get("key_concepts", [])
        
        if evidence_focus == "direct_quotes_and_definitions":
            evidence_questions = [
                f"Find a specific quote that defines {concept}." if key_concepts 
                else "Find a specific quote that defines the main concept.",
                "What exact words do the authors use to describe this phenomenon?",
                "Where in the article is this concept most clearly explained?"
            ]
        
        elif evidence_focus == "examples_and_explanations":
            evidence_questions = [
                "What examples does the article provide to illustrate this concept?",
                "How do the authors explain the mechanism behind this process?",
                "What real-world cases are mentioned to support the argument?"
            ]
        
        elif evidence_focus == "data_patterns_and_relationships":
            evidence_questions = [
                "What patterns do you see in the data presented?",
                "How do the variables relate to each other according to the results?",
                "What trends are evident in the figures or tables?"
            ]
        
        elif evidence_focus == "critical_assessment_and_alternatives":
            evidence_questions = [
                "What limitations do the authors acknowledge in their study?",
                "What alternative explanations might exist for these findings?",
                "How might the results be different under other conditions?"
            ]
        
        return evidence_questions[:3]
    
    def _filter_questions_for_understanding(self, questions: List[str], understanding: Dict, 
                                          target_level: str) -> List[str]:
        """Filter questions to match student's current understanding level"""
        
        understanding_level = understanding.get("primary_level", "surface")
        confidence = understanding.get("confidence", 0.0)
        
        # If confidence is low, prioritize simpler questions
        if confidence < 0.5:
            # Prioritize questions with lower complexity indicators
            simple_questions = []
            complex_questions = []
            
            for question in questions:
                if any(indicator in question.lower() 
                      for indicator in ["what", "where", "when", "define", "list"]):
                    simple_questions.append(question)
                else:
                    complex_questions.append(question)
            
            return simple_questions + complex_questions[:2]  # Prioritize simple questions
        
        return questions  # Return all questions if confidence is adequate
    
    def _contextualize_scaffolding_sequence(self, sequence: List[str], content_context: Dict) -> List[str]:
        """Add context to generic scaffolding questions"""
        
        contextualized = []
        key_concepts = content_context.get("key_concepts", [])
        
        for question in sequence:
            if key_concepts and "{concept}" not in question:
                # Add concept context where appropriate
                if "evidence" in question.lower():
                    concept = key_concepts[0] if key_concepts else "the main concept"
                    contextualized_q = question.replace("evidence", f"evidence about {concept}")
                    contextualized.append(contextualized_q)
                else:
                    contextualized.append(question)
            else:
                contextualized.append(question)
        
        return contextualized
    
    def _get_next_bloom_level(self, current_level: str) -> str:
        """Get the next level in Bloom's taxonomy progression"""
        levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        try:
            current_index = levels.index(current_level)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return "understand"
    
    def _get_previous_bloom_level(self, current_level: str) -> str:
        """Get the previous level in Bloom's taxonomy progression"""
        levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        try:
            current_index = levels.index(current_level)
            return levels[max(current_index - 1, 0)]
        except ValueError:
            return "remember"
    
    def _generate_foundational_questions(self, content_context: Dict) -> List[str]:
        """Generate foundational questions for students who need more basic support"""
        return [
            "What are the main points discussed in this section of the article?",
            "Which concepts seem most important for understanding this topic?",
            "What basic definitions do you need to understand first?"
        ]
    
    def _generate_advanced_questions(self, content_context: Dict, question_metadata: Dict) -> List[str]:
        """Generate advanced questions for students ready for higher-order thinking"""
        return [
            "What implications do these findings have for the broader field?",
            "How might these results influence future research directions?", 
            "What questions does this analysis raise that aren't addressed in the article?"
        ]
    
    def _fill_evidence_template(self, template: str, concepts: List[str], 
                              required_evidence: str, focus: str) -> str:
        """Fill evidence-focused template with specific context"""
        
        filled_template = template
        
        # Replace {topic} with focus or concept
        if "{topic}" in template:
            replacement = focus if focus else (concepts[0] if concepts else "the main topic")
            filled_template = filled_template.replace("{topic}", replacement)
        
        # Replace {concept} with specific concept
        if "{concept}" in template and concepts:
            filled_template = filled_template.replace("{concept}", concepts[0])
        
        return filled_template
    
    def _generate_specific_evidence_questions(self, required_evidence: str, 
                                            content_context: Dict) -> List[str]:
        """Generate questions specific to required evidence type"""
        
        questions = []
        evidence_lower = required_evidence.lower()
        
        if "citation" in evidence_lower or "page" in evidence_lower:
            questions.append("What specific page or section supports your point?")
            
        if "data" in evidence_lower or "figure" in evidence_lower:
            questions.append("What data or figures provide the strongest evidence?")
            
        if "quote" in evidence_lower:
            questions.append("Which specific quote best supports your argument?")
            
        if "example" in evidence_lower:
            questions.append("What concrete examples illustrate this concept?")
        
        return questions