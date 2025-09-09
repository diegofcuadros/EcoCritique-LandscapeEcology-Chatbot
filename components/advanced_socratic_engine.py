"""
Advanced Socratic Engine - Context-aware Socratic questioning with assignment integration
Combines learning stage detection, progressive questioning, and evidence guidance
"""

import streamlit as st
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from components.learning_stage_detector import LearningStageDetector
from components.progressive_questioning import ProgressiveQuestioningSystem
from components.evidence_guidance_system import EvidenceGuidanceSystem
from components.writing_preparation_system import WritingPreparationSystem

class AdvancedSocraticEngine:
    """Context-aware Socratic questioning with assignment integration"""
    
    def __init__(self):
        self.stage_detector = LearningStageDetector()
        self.questioning_system = ProgressiveQuestioningSystem()
        self.evidence_guidance = EvidenceGuidanceSystem()
        self.writing_preparation = WritingPreparationSystem()
        
        # Response generation strategies by learning stage
        self.response_strategies = {
            "comprehension_building": {
                "approach": "foundational_support",
                "question_complexity": "low",
                "focus": "concept_clarification",
                "tone": "supportive_and_encouraging"
            },
            "evidence_gathering": {
                "approach": "guided_discovery", 
                "question_complexity": "medium",
                "focus": "evidence_location_and_relevance",
                "tone": "directive_and_specific"
            },
            "analysis_ready": {
                "approach": "analytical_scaffolding",
                "question_complexity": "medium-high", 
                "focus": "pattern_recognition_and_interpretation",
                "tone": "challenging_and_probing"
            },
            "advanced_ready": {
                "approach": "synthesis_and_evaluation",
                "question_complexity": "high",
                "focus": "critical_thinking_and_connections", 
                "tone": "collaborative_and_exploratory"
            }
        }
        
        # Evidence guidance templates
        self.evidence_guidance = {
            "no_evidence": {
                "guidance": "Let's find specific evidence from the article to support your thinking.",
                "questions": [
                    "What section of the article is most relevant to this question?",
                    "Can you find a specific example or data point that relates?",
                    "Where do the authors discuss this concept directly?"
                ]
            },
            "weak_evidence": {
                "guidance": "You're on the right track. Let's find stronger, more specific evidence.",
                "questions": [
                    "Can you find more detailed information about this in the article?",
                    "What specific data or examples support this point?",
                    "Is there a more direct quote or reference you could use?"
                ]
            },
            "good_evidence": {
                "guidance": "Great evidence! Now let's analyze what it means.",
                "questions": [
                    "What does this evidence tell us about the broader question?",
                    "How does this evidence support or challenge the authors' argument?",
                    "What patterns do you notice in this evidence?"
                ]
            },
            "strong_evidence": {
                "guidance": "Excellent evidence and analysis. Let's connect this to the bigger picture.",
                "questions": [
                    "How does this evidence relate to other concepts we've discussed?",
                    "What implications does this evidence have?",
                    "How might this evidence inform practice or policy?"
                ]
            }
        }
        
        # Tutoring prompt integration patterns
        self.tutoring_prompt_usage = {
            "direct_usage": "Use the exact tutoring prompt when it perfectly fits the context",
            "adapted_usage": "Modify the tutoring prompt to better fit student's current level",
            "combined_usage": "Combine multiple tutoring prompts for comprehensive guidance",
            "contextual_usage": "Use tutoring prompts as inspiration for contextual questions"
        }
    
    def generate_contextualized_response(self, user_input: str, assignment_context: Dict, 
                                       student_progress: Dict, chat_history: List[Dict]) -> str:
        """
        Generate responses aware of assignment requirements and student progress
        
        Args:
            user_input: Student's current message
            assignment_context: Full assignment context including current question
            student_progress: Student's progress through assignment
            chat_history: Complete conversation history
            
        Returns:
            Contextually appropriate Socratic response
        """
        
        # Get current question details
        current_question = assignment_context.get('current_question_details', {})
        
        if not current_question:
            return self._generate_generic_response(user_input, chat_history)
        
        # Assess student's learning stage
        learning_stage = self.stage_detector.get_learning_stage_summary(
            chat_history, current_question, assignment_context
        )
        
        # Analyze student's current response
        response_analysis = self._analyze_student_response(
            user_input, current_question, chat_history
        )
        
        # Determine appropriate questioning strategy
        strategy = self._select_questioning_strategy(
            learning_stage, response_analysis, current_question
        )
        
        # Check for writing preparation readiness
        writing_readiness = self.writing_preparation.assess_writing_readiness(
            chat_history, current_question, assignment_context
        )
        
        # If student shows high readiness and hasn't been offered writing support yet
        if (writing_readiness['completion_score'] >= 0.6 and 
            writing_readiness['current_phase'] in ['outline_creation', 'draft_preparation', 'writing_ready'] and
            not any('outline' in msg.get('content', '').lower() for msg in chat_history[-5:])):
            
            # Offer writing transition support
            response = self.generate_writing_transition_response(
                chat_history, current_question, assignment_context
            )
        
        # Check if student is asking for outline help
        elif any(word in user_input.lower() for word in ['outline', 'organize', 'structure', 'write', 'ready to write']):
            if writing_readiness['completion_score'] >= 0.4:
                response = self.generate_personalized_outline(chat_history, current_question, assignment_context)
            else:
                response = self.generate_writing_transition_response(chat_history, current_question, assignment_context)
        
        else:
            # Generate standard contextual response
            response = self._generate_strategy_based_response(
                user_input, current_question, learning_stage, response_analysis, strategy, assignment_context, chat_history
            )
        
        return response
    
    def select_appropriate_questioning_strategy(self, question_type: str, 
                                              student_competency_level: str, 
                                              assignment_context: Dict) -> Dict[str, Any]:
        """
        Choose tutoring approach based on question complexity and student ability
        
        Args:
            question_type: Type of assignment question (bloom level, complexity)
            student_competency_level: Student's demonstrated competency
            assignment_context: Assignment and question context
            
        Returns:
            Dict with recommended strategy, question types, and approach
        """
        
        strategy = {
            "primary_approach": "guided_discovery",
            "question_complexity": "medium",
            "evidence_focus": "moderate",
            "scaffolding_needed": False,
            "progression_target": question_type
        }
        
        # Get question requirements
        bloom_level = assignment_context.get('current_question_details', {}).get('bloom_level', 'understand')
        question_complexity = self._assess_question_complexity(assignment_context.get('current_question_details', {}))
        
        # Match strategy to competency gap
        competency_levels = ["surface", "developing", "proficient", "advanced"]
        bloom_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        
        try:
            competency_index = competency_levels.index(student_competency_level)
            bloom_index = bloom_levels.index(bloom_level)
        except ValueError:
            competency_index = 1  # Default to developing
            bloom_index = 1       # Default to understand
        
        # Determine if scaffolding is needed
        if bloom_index > competency_index + 1:
            strategy["scaffolding_needed"] = True
            strategy["primary_approach"] = "scaffolded_progression"
        
        # Adjust complexity based on gap
        complexity_gap = bloom_index - competency_index
        if complexity_gap <= 0:
            strategy["question_complexity"] = "maintain_or_increase"
        elif complexity_gap == 1:
            strategy["question_complexity"] = "gradual_increase"
        else:
            strategy["question_complexity"] = "significant_scaffolding"
        
        # Set evidence focus based on question requirements
        required_evidence = assignment_context.get('current_question_details', {}).get('required_evidence', '')
        if 'specific' in required_evidence.lower() or 'cite' in required_evidence.lower():
            strategy["evidence_focus"] = "high_specificity"
        elif 'example' in required_evidence.lower():
            strategy["evidence_focus"] = "concrete_examples"
        else:
            strategy["evidence_focus"] = "general_support"
        
        return strategy
    
    def provide_evidence_guidance(self, current_question: Dict, article_content: str, 
                                user_attempts: List[str]) -> Dict[str, Any]:
        """
        Guide students toward finding and analyzing relevant evidence
        
        Args:
            current_question: Current assignment question details
            article_content: Full article text (if available)
            user_attempts: Student's previous attempts at providing evidence
            
        Returns:
            Dict with evidence assessment and specific guidance
        """
        
        guidance = {
            "evidence_quality": "none",
            "specific_guidance": "",
            "guided_questions": [],
            "article_sections": [],
            "improvement_suggestions": []
        }
        
        if not user_attempts:
            guidance["evidence_quality"] = "none"
            guidance["specific_guidance"] = self.evidence_guidance["no_evidence"]["guidance"]
            guidance["guided_questions"] = self.evidence_guidance["no_evidence"]["questions"]
            return guidance
        
        # Analyze evidence quality in recent attempts
        recent_attempt = user_attempts[-1] if user_attempts else ""
        evidence_quality = self._assess_evidence_quality_in_response(recent_attempt, current_question)
        
        guidance["evidence_quality"] = evidence_quality
        
        # Provide appropriate guidance based on quality
        if evidence_quality in self.evidence_guidance:
            guidance_template = self.evidence_guidance[evidence_quality]
            guidance["specific_guidance"] = guidance_template["guidance"]
            guidance["guided_questions"] = guidance_template["questions"]
        
        # Add question-specific guidance
        required_evidence = current_question.get('required_evidence', '')
        if required_evidence:
            specific_questions = self._generate_evidence_specific_questions(required_evidence, recent_attempt)
            guidance["guided_questions"].extend(specific_questions)
        
        # Generate improvement suggestions
        guidance["improvement_suggestions"] = self._generate_evidence_improvement_suggestions(
            recent_attempt, evidence_quality, current_question
        )
        
        return guidance
    
    def _analyze_student_response(self, user_input: str, current_question: Dict, 
                                chat_history: List[Dict]) -> Dict[str, Any]:
        """Analyze student's response for quality, evidence, and understanding"""
        
        analysis = {
            "response_length": len(user_input),
            "evidence_present": False,
            "evidence_quality": "none",
            "analytical_depth": "surface",
            "question_alignment": "partial",
            "concept_usage": [],
            "improvement_areas": []
        }
        
        # Check for evidence indicators
        evidence_indicators = [
            r"(?i)(page|p\.)\s*\d+", r"(?i)(figure|fig\.)\s*\d+", 
            r"(?i)the article (states|says|mentions)", r"(?i)according to",
            r"(?i)(study|research) (shows|finds|demonstrates)"
        ]
        
        evidence_count = sum(1 for pattern in evidence_indicators if re.search(pattern, user_input))
        analysis["evidence_present"] = evidence_count > 0
        
        if evidence_count >= 2:
            analysis["evidence_quality"] = "strong"
        elif evidence_count == 1:
            analysis["evidence_quality"] = "moderate"
        else:
            analysis["evidence_quality"] = "none"
        
        # Check analytical depth
        analytical_indicators = [
            "because", "therefore", "suggests", "indicates", "demonstrates", 
            "implies", "pattern", "relationship", "significant"
        ]
        
        analytical_count = sum(1 for indicator in analytical_indicators if indicator in user_input.lower())
        
        if analytical_count >= 3:
            analysis["analytical_depth"] = "deep"
        elif analytical_count >= 1:
            analysis["analytical_depth"] = "moderate" 
        else:
            analysis["analytical_depth"] = "surface"
        
        # Check question alignment
        question_concepts = current_question.get('key_concepts', [])
        question_title = current_question.get('title', '').lower()
        
        concept_matches = sum(1 for concept in question_concepts if concept.lower() in user_input.lower())
        title_word_matches = sum(1 for word in question_title.split() 
                               if len(word) > 3 and word in user_input.lower())
        
        if concept_matches >= 2 or title_word_matches >= 2:
            analysis["question_alignment"] = "strong"
        elif concept_matches >= 1 or title_word_matches >= 1:
            analysis["question_alignment"] = "moderate"
        else:
            analysis["question_alignment"] = "weak"
        
        # Record concept usage
        analysis["concept_usage"] = [concept for concept in question_concepts 
                                   if concept.lower() in user_input.lower()]
        
        # Identify improvement areas
        if not analysis["evidence_present"]:
            analysis["improvement_areas"].append("needs_evidence")
        if analysis["analytical_depth"] == "surface":
            analysis["improvement_areas"].append("needs_analysis")
        if analysis["question_alignment"] == "weak":
            analysis["improvement_areas"].append("needs_focus")
        
        return analysis
    
    def _select_questioning_strategy(self, learning_stage: Dict, response_analysis: Dict, 
                                   current_question: Dict) -> str:
        """Select appropriate questioning strategy based on context"""
        
        overall_stage = learning_stage.get("overall_stage", "comprehension_building")
        evidence_quality = response_analysis.get("evidence_quality", "none")
        analytical_depth = response_analysis.get("analytical_depth", "surface")
        
        # Priority 1: Address evidence gaps
        if evidence_quality == "none":
            return "evidence_discovery"
        
        # Priority 2: Develop analysis if evidence is present
        elif evidence_quality in ["moderate", "strong"] and analytical_depth == "surface":
            return "evidence_analysis"
        
        # Priority 3: Build connections and synthesis
        elif evidence_quality == "strong" and analytical_depth in ["moderate", "deep"]:
            return "synthesis_and_connections"
        
        # Priority 4: Stage-based approach
        elif overall_stage == "comprehension_building":
            return "concept_clarification"
        elif overall_stage == "evidence_gathering":
            return "guided_evidence_gathering"
        elif overall_stage == "analysis_ready":
            return "analytical_thinking"
        else:
            return "advanced_synthesis"
    
    def _generate_strategy_based_response(self, user_input: str, current_question: Dict, 
                                        learning_stage: Dict, response_analysis: Dict,
                                        strategy: str, assignment_context: Dict, chat_history: List[Dict] = None) -> str:
        """Generate response based on selected strategy"""
        
        if strategy == "evidence_discovery":
            return self._generate_evidence_discovery_response(current_question, user_input, chat_history)
        
        elif strategy == "evidence_analysis":
            return self._generate_evidence_analysis_response(current_question, user_input, response_analysis, chat_history)
        
        elif strategy == "synthesis_and_connections":
            return self._generate_synthesis_response(current_question, user_input, assignment_context)
        
        elif strategy == "concept_clarification":
            return self._generate_concept_clarification_response(current_question, user_input)
        
        elif strategy == "guided_evidence_gathering":
            return self._generate_guided_evidence_response(current_question, user_input)
        
        elif strategy == "analytical_thinking":
            return self._generate_analytical_thinking_response(current_question, user_input, response_analysis)
        
        else:  # advanced_synthesis
            return self._generate_advanced_synthesis_response(current_question, user_input, assignment_context)
    
    def _generate_evidence_discovery_response(self, current_question: Dict, user_input: str, chat_history: List[Dict] = None) -> str:
        """Generate response focused on helping student find evidence using Evidence Guidance System"""
        
        # Analyze current evidence quality
        evidence_analysis = self.evidence_guidance.analyze_evidence_quality(
            user_input, chat_history or [], current_question
        )
        
        # Generate targeted coaching based on evidence analysis
        if evidence_analysis['quality_score'] < 0.2 or not evidence_analysis['evidence_found']:
            # No evidence found - provide search strategies
            search_strategies = self.evidence_guidance.suggest_evidence_search_strategies(
                current_question, ""  # Article context would be passed in real implementation
            )
            
            coaching_response = f"""I can see you're thinking about this! Now let's find specific evidence from the article to support your analysis.

**Search Strategy:** Look for these key terms in the article: {', '.join(search_strategies['search_terms'][:4])}

{self.evidence_guidance.generate_evidence_coaching(evidence_analysis, current_question, {})}

What concrete information from the article can you find that relates to your point?"""
            
        else:
            # Some evidence found but needs strengthening
            coaching_response = self.evidence_guidance.generate_evidence_coaching(
                evidence_analysis, current_question, {}
            )
            
        return coaching_response
    
    def _generate_evidence_analysis_response(self, current_question: Dict, user_input: str, 
                                           response_analysis: Dict, chat_history: List[Dict] = None) -> str:
        """Generate response focused on analyzing found evidence using Evidence Guidance System"""
        
        # Get comprehensive evidence analysis
        evidence_analysis = self.evidence_guidance.analyze_evidence_quality(
            user_input, chat_history or [], current_question
        )
        
        # Track student's evidence progression
        progression_analysis = self.evidence_guidance.track_evidence_progression(
            chat_history or [], current_question
        )
        
        # Generate analysis-focused coaching
        coaching_response = self.evidence_guidance.generate_evidence_coaching(
            evidence_analysis, current_question, {}
        )
        
        # Add analysis-specific prompts based on evidence quality
        if evidence_analysis['quality_score'] >= 0.6:
            coaching_response += f"""

**Deep Analysis Questions:**
• What specific implications does this evidence have for {current_question.get('title', 'the question')}?
• How does this evidence connect to other findings in the article?
• What patterns or relationships does this evidence reveal?"""
        
        elif evidence_analysis['quality_score'] >= 0.3:
            coaching_response += f"""

**Strengthening Analysis:**
• What specific details in this evidence directly answer the question?
• Can you find additional evidence that supports or challenges this finding?
• How confident are you in the quality of this evidence?"""
        
        return coaching_response
    
    def _generate_synthesis_response(self, current_question: Dict, user_input: str, 
                                   assignment_context: Dict) -> str:
        """Generate response focused on synthesis and connections"""
        
        question_title = current_question.get('title', 'this question')
        all_questions = assignment_context.get('all_questions', [])
        completed_questions = assignment_context.get('completed_questions', [])
        
        synthesis_prompts = []
        
        if len(completed_questions) >= 1:
            synthesis_prompts.append("How does your analysis here connect to your previous responses?")
        
        if len(all_questions) > 1:
            synthesis_prompts.append("What broader patterns are emerging across your assignment work?")
        
        synthesis_prompts.append("How does this analysis contribute to your overall understanding?")
        
        selected_prompts = synthesis_prompts[:2]  # Use first 2
        
        return f"""Outstanding analysis! You're demonstrating strong critical thinking about **{question_title}**.

Now let's connect this to the bigger picture:

{chr(10).join('• ' + prompt for prompt in selected_prompts)}

Your evidence and analysis are solid - now let's see how this contributes to your overall argument for the assignment."""
    
    def _generate_concept_clarification_response(self, current_question: Dict, user_input: str) -> str:
        """Generate response focused on clarifying key concepts"""
        
        key_concepts = current_question.get('key_concepts', [])
        question_title = current_question.get('title', 'this topic')
        
        if key_concepts:
            primary_concept = key_concepts[0]
            return f"""Let's make sure we have a clear understanding of the key concepts before diving deeper.

For **{question_title}**, the concept of **{primary_concept}** is central. 

Based on what you've read in the article:
• How would you define {primary_concept} in your own words?
• What are the key characteristics that make {primary_concept} distinct?
• Can you find where the article explains this concept most clearly?

Once we're clear on the foundational concepts, we can build stronger analysis."""
        
        else:
            return f"""Let's establish a clear foundation for understanding **{question_title}**.

From your reading of the article:
• What are the main concepts or ideas involved in this question?
• Which parts of the article seem most relevant to what's being asked?
• Are there any terms or concepts you'd like to clarify before proceeding?

Building this foundation will make your analysis much stronger."""
    
    def _generate_guided_evidence_response(self, current_question: Dict, user_input: str) -> str:
        """Generate response with specific guidance for evidence gathering"""
        
        question_title = current_question.get('title', 'this question')
        tutoring_prompts = current_question.get('tutoring_prompts', [])
        
        # Use the first tutoring prompt if available
        if tutoring_prompts:
            primary_prompt = tutoring_prompts[0]
            return f"""You're on the right track with your thinking about **{question_title}**. Now let's find specific evidence to support and develop your ideas.

{primary_prompt}

Take some time to look through the article systematically. Focus on finding:
• Specific data, statistics, or measurements
• Concrete examples or case studies  
• Direct quotes that address the question
• Figures or tables that provide relevant information

What specific evidence can you locate that relates to your analysis?"""
        
        else:
            return f"""Good thinking about **{question_title}**! Let's now locate specific evidence from the article.

Here's a systematic approach:
• Scan the article for sections that directly discuss this topic
• Look for data, examples, or studies that relate to your point
• Find quotes or statements from the authors that support your analysis

What specific information from the article can you point to that backs up your thinking?"""
    
    def _generate_analytical_thinking_response(self, current_question: Dict, user_input: str, 
                                             response_analysis: Dict) -> str:
        """Generate response to promote deeper analytical thinking"""
        
        question_title = current_question.get('title', 'this question')
        bloom_level = current_question.get('bloom_level', 'analyze')
        
        analytical_prompts = {
            "analyze": [
                "What patterns do you see in the evidence you've gathered?",
                "How do the different pieces of evidence relate to each other?",
                "What factors seem to be most important in explaining this phenomenon?"
            ],
            "evaluate": [
                "How strong is the evidence for this conclusion?", 
                "What are the limitations of this approach or study?",
                "What alternative explanations might exist?"
            ],
            "create": [
                "How would you design a study to test this hypothesis?",
                "What solutions would you propose based on this evidence?",
                "How would you synthesize these findings into a comprehensive argument?"
            ]
        }
        
        prompts = analytical_prompts.get(bloom_level, analytical_prompts["analyze"])
        selected_prompts = prompts[:2]  # Use first 2 prompts
        
        return f"""You've gathered good evidence for **{question_title}**. Now let's push your analysis further.

{chr(10).join('• ' + prompt for prompt in selected_prompts)}

Don't just describe what the evidence says - analyze what it means, why it's significant, and how it answers the question. Show me your analytical thinking!"""
    
    def _generate_advanced_synthesis_response(self, current_question: Dict, user_input: str, 
                                            assignment_context: Dict) -> str:
        """Generate response for advanced synthesis and evaluation"""
        
        question_title = current_question.get('title', 'this question')
        
        return f"""Excellent work on **{question_title}**! You're demonstrating sophisticated thinking.

Let's take your analysis to the highest level:

• How does your analysis here challenge or confirm existing assumptions?
• What are the broader implications of your findings for the field of landscape ecology?
• If you were to advise researchers or practitioners, what would you tell them based on your analysis?
• What new questions does your work raise that weren't addressed in the original article?

You're ready for advanced critical thinking - show me how this work contributes to the larger conversation in the field."""
    
    def _assess_question_complexity(self, question_details: Dict) -> str:
        """Assess the complexity level of an assignment question"""
        
        bloom_level = question_details.get('bloom_level', 'understand')
        prompt_length = len(question_details.get('prompt', ''))
        key_concepts_count = len(question_details.get('key_concepts', []))
        
        complexity_score = 0
        
        # Bloom level scoring
        bloom_scores = {"remember": 1, "understand": 2, "apply": 3, "analyze": 4, "evaluate": 5, "create": 6}
        complexity_score += bloom_scores.get(bloom_level, 2)
        
        # Length and concept complexity
        if prompt_length > 200:
            complexity_score += 1
        if key_concepts_count > 3:
            complexity_score += 1
        
        if complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _assess_evidence_quality_in_response(self, response: str, current_question: Dict) -> str:
        """Assess the quality of evidence provided in a student response"""
        
        if not response.strip():
            return "none"
        
        # Check for citation indicators
        citation_patterns = [
            r"(?i)(page|p\.)\s*\d+", r"(?i)(figure|fig\.)\s*\d+",
            r"(?i)the article (states|says)", r"(?i)according to"
        ]
        
        citation_count = sum(1 for pattern in citation_patterns if re.search(pattern, response))
        
        # Check for data/study references
        data_patterns = ["data", "study", "research", "findings", "results", "statistics"]
        data_count = sum(1 for pattern in data_patterns if pattern in response.lower())
        
        # Check for specific examples
        example_patterns = ["example", "instance", "case", "specifically"]
        example_count = sum(1 for pattern in example_patterns if pattern in response.lower())
        
        # Calculate overall evidence quality
        total_score = citation_count * 2 + data_count + example_count
        
        if total_score >= 4:
            return "strong"
        elif total_score >= 2:
            return "good"
        elif total_score >= 1:
            return "weak"
        else:
            return "none"
    
    def _generate_evidence_specific_questions(self, required_evidence: str, recent_attempt: str) -> List[str]:
        """Generate questions specific to the type of evidence required"""
        
        questions = []
        evidence_lower = required_evidence.lower()
        
        if "citation" in evidence_lower and "page" not in recent_attempt.lower():
            questions.append("Can you provide specific page numbers or sections for your evidence?")
        
        if "data" in evidence_lower and not any(word in recent_attempt.lower() for word in ["data", "statistics", "number"]):
            questions.append("What specific data or statistics from the article support your point?")
        
        if "example" in evidence_lower and "example" not in recent_attempt.lower():
            questions.append("What concrete examples does the article provide to illustrate this?")
        
        return questions
    
    def _generate_evidence_improvement_suggestions(self, response: str, evidence_quality: str, 
                                                 current_question: Dict) -> List[str]:
        """Generate specific suggestions for improving evidence usage"""
        
        suggestions = []
        
        if evidence_quality == "none":
            suggestions.extend([
                "Look for specific sections in the article that discuss this topic",
                "Find concrete data, examples, or quotes that support your point",
                "Include page numbers or section references for your evidence"
            ])
        
        elif evidence_quality == "weak":
            suggestions.extend([
                "Provide more specific details from the article",
                "Include direct quotes or paraphrases with citations",
                "Look for stronger, more relevant evidence"
            ])
        
        elif evidence_quality in ["good", "strong"]:
            suggestions.extend([
                "Explain how this evidence specifically answers the question",
                "Connect multiple pieces of evidence to build a stronger argument",
                "Consider what this evidence implies beyond its literal meaning"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _generate_generic_response(self, user_input: str, chat_history: List[Dict]) -> str:
        """Generate a generic response when assignment context is not available"""
        
        return """I'd like to help you think through this more systematically. 

What specific evidence from the article supports your point? Let's focus on finding concrete information that directly relates to what you're discussing.

Once you identify that evidence, we can analyze what it means and how it addresses the question at hand."""
    
    def assess_writing_readiness(self, chat_history: List[Dict], current_question: Dict, 
                               assignment_context: Dict) -> Dict[str, Any]:
        """
        Assess student's readiness to transition from discussion to writing.
        
        Uses WritingPreparationSystem to evaluate preparation level and provide guidance.
        """
        return self.writing_preparation.assess_writing_readiness(
            chat_history, current_question, assignment_context
        )
    
    def generate_writing_transition_response(self, chat_history: List[Dict], current_question: Dict,
                                           assignment_context: Dict) -> str:
        """
        Generate response that helps student transition from discussion to writing preparation.
        
        Provides personalized guidance based on preparation level.
        """
        # Assess writing readiness
        readiness_analysis = self.writing_preparation.assess_writing_readiness(
            chat_history, current_question, assignment_context
        )
        
        # Generate transition guidance
        transition_guidance = self.writing_preparation.generate_transition_guidance(
            readiness_analysis, current_question
        )
        
        # If ready for outline, offer to create one
        if readiness_analysis['current_phase'] in ['outline_creation', 'draft_preparation', 'writing_ready']:
            transition_guidance += f"""

**Ready for the next step?** I can help you create a personalized outline for writing your response. This will organize all the evidence and insights you've developed into a clear structure.

Would you like me to create an outline for your writing?"""
        
        return transition_guidance
    
    def generate_personalized_outline(self, chat_history: List[Dict], current_question: Dict,
                                    assignment_context: Dict) -> str:
        """
        Generate a complete personalized outline for student's writing.
        
        Returns formatted outline with evidence mapping and writing guidance.
        """
        outline_data = self.writing_preparation.generate_personalized_outline(
            current_question, chat_history, assignment_context
        )
        
        # Format outline for display
        formatted_outline = f"""# Writing Outline: {outline_data['question_focus']}

**Target Length:** {outline_data['word_target']}  
**Outline Type:** {outline_data['outline_type'].replace('_', ' ').title()}

## Structure:

"""
        
        for i, section in enumerate(outline_data['structure'], 1):
            formatted_outline += f"""### {i}. {section['section_title']} ({section['suggested_length']})

**Writing Guidance:** {section['writing_guidance']}

"""
            if section['assigned_evidence']:
                formatted_outline += f"**Evidence to Include:**\n"
                for evidence in section['assigned_evidence']:
                    formatted_outline += f"• {evidence['type'].title()}: {evidence['content'][:100]}...\n"
                formatted_outline += "\n"
        
        # Add writing tips
        formatted_outline += f"## Writing Tips:\n\n"
        for tip in outline_data['writing_tips']:
            formatted_outline += f"• {tip}\n"
        
        formatted_outline += f"""

**You're well-prepared to write!** Use this outline as your guide, and remember to:
- Expand each section to meet the suggested word count
- Use your evidence to support each main point
- Connect your analysis back to the original question

Good luck with your writing!"""
        
        return formatted_outline
    
    def create_evidence_summary_for_writing(self, chat_history: List[Dict], 
                                          current_question: Dict) -> str:
        """
        Create a formatted evidence summary to help with writing preparation.
        
        Organizes all evidence collected during discussion for easy reference.
        """
        evidence_summary = self.writing_preparation.create_evidence_summary(
            chat_history, current_question
        )
        
        formatted_summary = f"""# Evidence Summary for Writing

**Total Evidence Collected:** {evidence_summary['total_evidence_count']} pieces

## Evidence by Type:

"""
        
        for evidence_type, items in evidence_summary['evidence_by_type'].items():
            formatted_summary += f"**{evidence_type.title()} ({len(items)} items):**\n"
            for item in items[:3]:  # Show first 3 of each type
                formatted_summary += f"• {item['content'][:150]}...\n"
            if len(items) > 3:
                formatted_summary += f"• ... and {len(items) - 3} more\n"
            formatted_summary += "\n"
        
        # Show evidence gaps if any
        if evidence_summary['evidence_gaps']:
            formatted_summary += f"## Evidence Gaps to Address:\n\n"
            for gap in evidence_summary['evidence_gaps']:
                formatted_summary += f"• {gap}\n"
            formatted_summary += "\n"
        
        # Show best evidence for writing
        formatted_summary += f"## Best Evidence for Writing:\n\n"
        for i, evidence in enumerate(evidence_summary['writing_ready_evidence'][:5], 1):
            formatted_summary += f"{i}. **{evidence['type'].title()}:** {evidence['content'][:200]}\n"
            formatted_summary += f"   *Context:* {evidence['context'][:100]}...\n\n"
        
        return formatted_summary