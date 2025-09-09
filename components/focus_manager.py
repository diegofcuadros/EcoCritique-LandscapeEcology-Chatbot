"""
Advanced Focus Manager - Intelligent system to keep students focused on assignment goals
Prevents rabbit-hole conversations through multi-factor analysis and contextual redirection
"""

import streamlit as st
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import math

class FocusManager:
    """Advanced system to keep students focused on assignment goals"""
    
    def __init__(self):
        # Enhanced rabbit-hole indicators by category
        self.divergence_indicators = {
            "curiosity_driven": {
                "keywords": ["generally", "in general", "what about", "tell me about", "by the way", 
                           "speaking of", "on a related note", "i'm curious about", "what if"],
                "patterns": [r"(?i)what.*generally", r"(?i)tell me about.*in general", 
                           r"(?i)i wonder.*about", r"(?i)can you explain.*overall"],
                "weight": 0.7
            },
            "definition_seeking": {
                "keywords": ["define", "what is", "what are", "what does", "meaning of", 
                           "definition", "terminology"],
                "patterns": [r"(?i)what (is|are|does|do).*mean", r"(?i)define.*for me",
                           r"(?i)can you explain what.*is"],
                "weight": 0.5  # Lower weight - definitions can be relevant
            },
            "comparison_distraction": {
                "keywords": ["vs", "versus", "compared to", "difference between", "similar to",
                           "like in", "as opposed to"],
                "patterns": [r"(?i)how does.*compare to", r"(?i)what.*difference.*between",
                           r"(?i)is.*similar to"],
                "weight": 0.6
            },
            "hypothesis_speculation": {
                "keywords": ["i think", "maybe", "perhaps", "possibly", "what if", "suppose"],
                "patterns": [r"(?i)what if.*were to", r"(?i)i think.*might",
                           r"(?i)maybe we could"],
                "weight": 0.4  # Speculation can be valuable
            },
            "meta_questions": {
                "keywords": ["why should i", "do i have to", "is this important", "does this matter",
                           "relevance", "point of"],
                "patterns": [r"(?i)why (should|do) (i|we).*", r"(?i)what.*point of.*",
                           r"(?i)does this.*matter"],
                "weight": 0.8  # High weight - clear avoidance
            },
            "broad_scope": {
                "keywords": ["always", "never", "all", "every", "everywhere", "everything",
                           "in all cases", "universally"],
                "patterns": [r"(?i)(always|never).*true", r"(?i)in all.*cases",
                           r"(?i)does this apply.*everywhere"],
                "weight": 0.6
            }
        }
        
        # Evidence-seeking positive indicators (reduce divergence score)
        self.focus_indicators = {
            "evidence_seeking": ["evidence", "data", "study shows", "research indicates", 
                               "according to", "the article states", "findings"],
            "specific_references": ["page", "figure", "table", "section", "paragraph", 
                                  "author mentions", "study", "example"],
            "analytical_language": ["because", "therefore", "however", "although", "whereas",
                                  "demonstrates", "suggests", "indicates"],
            "assignment_terms": ["question asks", "assignment", "requirement", "analyze",
                               "evaluate", "compare", "synthesize"]
        }
        
        # Conversation flow patterns that indicate good progression
        self.productive_patterns = [
            "building_on_previous",  # References earlier discussion
            "seeking_clarification",  # Asks for clarification on complex points  
            "connecting_concepts",    # Links ideas together
            "evidence_synthesis",     # Combines multiple pieces of evidence
            "critical_evaluation"     # Shows evaluative thinking
        ]
        
    def analyze_conversation_drift(self, user_input: str, chat_history: List[Dict], 
                                 current_question: Dict, assignment_context: Dict) -> Dict[str, Any]:
        """
        Multi-factor analysis of conversation relevance and focus
        
        Returns:
            Dict with drift analysis including score, type, and recommended action
        """
        analysis = {
            "drift_score": 0.0,  # 0.0 = perfectly focused, 1.0 = completely off-topic
            "drift_type": "focused",
            "confidence": 0.0,
            "indicators": [],
            "focus_signals": [],
            "recommendation": "continue",
            "context_factors": {}
        }
        
        # Factor 1: Semantic relevance to current question
        semantic_score = self._calculate_semantic_relevance(user_input, current_question)
        analysis["context_factors"]["semantic_relevance"] = semantic_score
        
        # Factor 2: Divergence indicators analysis
        divergence_analysis = self._analyze_divergence_indicators(user_input)
        analysis["indicators"] = divergence_analysis["indicators"]
        analysis["drift_score"] += divergence_analysis["weighted_score"] * 0.4
        
        # Factor 3: Focus indicators (reduce drift score)
        focus_analysis = self._analyze_focus_indicators(user_input, current_question)
        analysis["focus_signals"] = focus_analysis["signals"]
        analysis["drift_score"] -= focus_analysis["focus_strength"] * 0.3
        
        # Factor 4: Conversation flow analysis
        flow_analysis = self._analyze_conversation_flow(user_input, chat_history, current_question)
        analysis["context_factors"]["conversation_flow"] = flow_analysis
        analysis["drift_score"] += flow_analysis["stagnation_score"] * 0.2
        
        # Factor 5: Progress stalling detection
        stalling_analysis = self._detect_progress_stalling(chat_history, assignment_context)
        analysis["context_factors"]["progress_stalling"] = stalling_analysis
        analysis["drift_score"] += stalling_analysis["stalling_score"] * 0.1
        
        # Ensure drift score stays in valid range
        analysis["drift_score"] = max(0.0, min(1.0, analysis["drift_score"]))
        
        # Classify drift type and determine recommendation
        analysis["drift_type"], analysis["recommendation"] = self._classify_drift_and_recommend(
            analysis["drift_score"], analysis["indicators"], analysis["context_factors"]
        )
        
        # Calculate confidence based on multiple signal agreement
        analysis["confidence"] = self._calculate_confidence(analysis)
        
        return analysis
    
    def _calculate_semantic_relevance(self, user_input: str, current_question: Dict) -> float:
        """Calculate semantic similarity between user input and current question"""
        if not current_question:
            return 0.5  # Neutral when no question context
        
        question_text = current_question.get('prompt', '')
        question_concepts = current_question.get('key_concepts', [])
        
        # Simple word overlap approach (could be enhanced with embeddings)
        input_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        question_words = set(re.findall(r'\b\w+\b', question_text.lower()))
        
        # Calculate overlap
        overlap_score = len(input_words.intersection(question_words)) / max(len(input_words), 1)
        
        # Boost score if key concepts are mentioned
        concept_boost = 0
        for concept in question_concepts:
            if concept.lower() in user_input.lower():
                concept_boost += 0.1
        
        return min(1.0, overlap_score + concept_boost)
    
    def _analyze_divergence_indicators(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for various types of divergence indicators"""
        result = {
            "indicators": [],
            "weighted_score": 0.0,
            "category_scores": {}
        }
        
        input_lower = user_input.lower()
        
        for category, indicators in self.divergence_indicators.items():
            category_score = 0.0
            found_indicators = []
            
            # Check keywords
            for keyword in indicators["keywords"]:
                if keyword in input_lower:
                    found_indicators.append(f"keyword: {keyword}")
                    category_score += 0.3
            
            # Check patterns
            for pattern in indicators["patterns"]:
                if re.search(pattern, user_input):
                    match = re.search(pattern, user_input).group()
                    found_indicators.append(f"pattern: {match}")
                    category_score += 0.4
            
            if found_indicators:
                weighted_contribution = min(1.0, category_score) * indicators["weight"]
                result["weighted_score"] += weighted_contribution
                result["category_scores"][category] = {
                    "score": category_score,
                    "weight": indicators["weight"],
                    "contribution": weighted_contribution,
                    "indicators": found_indicators
                }
                result["indicators"].extend([f"{category}: {ind}" for ind in found_indicators])
        
        # Normalize weighted score
        result["weighted_score"] = min(1.0, result["weighted_score"])
        
        return result
    
    def _analyze_focus_indicators(self, user_input: str, current_question: Dict) -> Dict[str, Any]:
        """Analyze positive indicators that show student is focused"""
        result = {
            "signals": [],
            "focus_strength": 0.0,
            "category_scores": {}
        }
        
        input_lower = user_input.lower()
        
        for category, indicators in self.focus_indicators.items():
            category_score = 0.0
            found_signals = []
            
            for indicator in indicators:
                if indicator in input_lower:
                    found_signals.append(indicator)
                    category_score += 0.2
            
            if found_signals:
                result["category_scores"][category] = {
                    "score": min(1.0, category_score),
                    "signals": found_signals
                }
                result["signals"].extend([f"{category}: {sig}" for sig in found_signals])
                result["focus_strength"] += min(1.0, category_score) * 0.25
        
        # Special boost for question-specific terms
        if current_question:
            question_title = current_question.get('title', '').lower()
            question_concepts = [c.lower() for c in current_question.get('key_concepts', [])]
            
            for concept in question_concepts:
                if concept in input_lower:
                    result["signals"].append(f"question_concept: {concept}")
                    result["focus_strength"] += 0.1
        
        result["focus_strength"] = min(1.0, result["focus_strength"])
        return result
    
    def _analyze_conversation_flow(self, user_input: str, chat_history: List[Dict], 
                                 current_question: Dict) -> Dict[str, Any]:
        """Analyze how well conversation is flowing toward assignment goals"""
        result = {
            "stagnation_score": 0.0,
            "flow_pattern": "normal",
            "recent_progress": False,
            "repetition_detected": False
        }
        
        if len(chat_history) < 3:
            return result  # Need some history to analyze
        
        # Get recent messages (last 6)
        recent_messages = chat_history[-6:]
        recent_user_messages = [msg for msg in recent_messages if msg.get("role") == "user"]
        
        if len(recent_user_messages) < 2:
            return result
        
        # Check for repetitive questioning patterns
        user_texts = [msg.get("content", "").lower() for msg in recent_user_messages]
        
        # Simple repetition detection
        for i, text1 in enumerate(user_texts):
            for j, text2 in enumerate(user_texts[i+1:], i+1):
                similarity = self._calculate_text_similarity(text1, text2)
                if similarity > 0.7:  # High similarity threshold
                    result["repetition_detected"] = True
                    result["stagnation_score"] += 0.3
                    break
        
        # Check for progress indicators in recent conversation
        progress_keywords = ["understand", "clear", "makes sense", "so then", "therefore", 
                           "building on", "following up", "next"]
        
        for msg in recent_messages:
            msg_content = msg.get("content", "").lower()
            if any(keyword in msg_content for keyword in progress_keywords):
                result["recent_progress"] = True
                break
        
        if not result["recent_progress"]:
            result["stagnation_score"] += 0.2
        
        # Detect circular questioning pattern
        if self._detect_circular_questioning(recent_user_messages):
            result["flow_pattern"] = "circular"
            result["stagnation_score"] += 0.4
        
        result["stagnation_score"] = min(1.0, result["stagnation_score"])
        return result
    
    def _detect_progress_stalling(self, chat_history: List[Dict], 
                                assignment_context: Dict) -> Dict[str, Any]:
        """Detect if student is stalling on making assignment progress"""
        result = {
            "stalling_score": 0.0,
            "evidence_gathering": False,
            "analysis_depth": "surface",
            "question_engagement": "low"
        }
        
        if not assignment_context or len(chat_history) < 5:
            return result
        
        # Analyze last 10 messages for evidence of productive work
        recent_messages = chat_history[-10:]
        user_messages = [msg for msg in recent_messages if msg.get("role") == "user"]
        
        evidence_keywords = ["evidence", "data", "study", "research", "findings", "results", 
                           "figure", "table", "page", "author states"]
        analysis_keywords = ["because", "therefore", "suggests", "indicates", "demonstrates",
                           "implies", "pattern", "relationship", "significant"]
        
        evidence_count = 0
        analysis_count = 0
        
        for msg in user_messages:
            content = msg.get("content", "").lower()
            evidence_count += sum(1 for kw in evidence_keywords if kw in content)
            analysis_count += sum(1 for kw in analysis_keywords if kw in content)
        
        # Evaluate evidence gathering
        if evidence_count >= 2:
            result["evidence_gathering"] = True
        elif evidence_count == 0:
            result["stalling_score"] += 0.3
        
        # Evaluate analysis depth
        if analysis_count >= 3:
            result["analysis_depth"] = "deep"
        elif analysis_count >= 1:
            result["analysis_depth"] = "moderate"
        else:
            result["analysis_depth"] = "surface"
            result["stalling_score"] += 0.2
        
        # Evaluate question engagement
        current_question_id = assignment_context.get('current_question')
        if current_question_id:
            question_mentions = sum(1 for msg in user_messages 
                                  if current_question_id.lower() in msg.get("content", "").lower())
            if question_mentions >= 2:
                result["question_engagement"] = "high"
            elif question_mentions == 1:
                result["question_engagement"] = "moderate"
            else:
                result["stalling_score"] += 0.4
        
        result["stalling_score"] = min(1.0, result["stalling_score"])
        return result
    
    def _classify_drift_and_recommend(self, drift_score: float, indicators: List[str], 
                                    context_factors: Dict) -> Tuple[str, str]:
        """Classify the type of drift and recommend appropriate action"""
        
        # Determine drift type based on score and indicators
        if drift_score < 0.2:
            drift_type = "focused"
            recommendation = "continue"
        elif drift_score < 0.4:
            drift_type = "slightly_unfocused"
            recommendation = "gentle_nudge"
        elif drift_score < 0.6:
            drift_type = "moderately_divergent"
            recommendation = "redirect"
        elif drift_score < 0.8:
            drift_type = "significantly_off_topic"
            recommendation = "firm_redirect"
        else:
            drift_type = "rabbit_hole"
            recommendation = "strong_redirect"
        
        # Adjust based on specific indicators
        meta_questions = any("meta_questions" in ind for ind in indicators)
        if meta_questions and drift_score > 0.5:
            recommendation = "motivational_redirect"
        
        curiosity_driven = any("curiosity_driven" in ind for ind in indicators)
        if curiosity_driven and drift_score < 0.6:
            recommendation = "bridge_redirect"  # Connect curiosity back to assignment
        
        # Consider conversation flow
        if context_factors.get("conversation_flow", {}).get("repetition_detected"):
            recommendation = "progress_redirect"
        
        return drift_type, recommendation
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in the drift analysis based on signal agreement"""
        # More signals = higher confidence
        num_indicators = len(analysis["indicators"])
        num_focus_signals = len(analysis["focus_signals"])
        
        # Agreement between different factors
        semantic_relevance = analysis["context_factors"].get("semantic_relevance", 0.5)
        drift_score = analysis["drift_score"]
        
        # If semantic relevance is high but drift score is high, confidence is lower
        agreement_penalty = abs(semantic_relevance - (1 - drift_score)) * 0.3
        
        base_confidence = min(1.0, (num_indicators + num_focus_signals) * 0.1)
        final_confidence = max(0.1, base_confidence - agreement_penalty)
        
        return final_confidence
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation using word overlap"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_circular_questioning(self, messages: List[Dict]) -> bool:
        """Detect if student is asking circular questions without progress"""
        if len(messages) < 3:
            return False
        
        # Look for pattern of asking similar questions repeatedly
        question_patterns = []
        for msg in messages:
            content = msg.get("content", "").lower()
            if "?" in content or any(word in content for word in ["what", "how", "why", "when", "where"]):
                # Extract key question words
                question_words = re.findall(r'\b(what|how|why|when|where|can|could|would|should)\b', content)
                if question_words:
                    question_patterns.append(question_words[0])
        
        # If more than half the questions use the same question word, likely circular
        if len(question_patterns) >= 3:
            most_common = max(set(question_patterns), key=question_patterns.count)
            frequency = question_patterns.count(most_common) / len(question_patterns)
            return frequency > 0.6
        
        return False
    
    def generate_redirection_response(self, drift_analysis: Dict, current_question: Dict, 
                                    assignment_context: Dict, student_progress: Dict) -> str:
        """Generate context-aware response to redirect student back on track"""
        
        recommendation = drift_analysis["recommendation"]
        drift_type = drift_analysis["drift_type"]
        confidence = drift_analysis["confidence"]
        
        # Get context information
        question_id = current_question.get('id', 'this question')
        question_title = current_question.get('title', 'the current question')
        evidence_required = current_question.get('required_evidence', 'supporting evidence')
        
        # Base response templates by recommendation type
        if recommendation == "continue":
            return ""  # No redirection needed
        
        elif recommendation == "gentle_nudge":
            return self._generate_gentle_nudge(current_question, drift_analysis)
        
        elif recommendation == "redirect":
            return self._generate_standard_redirect(current_question, assignment_context, drift_analysis)
        
        elif recommendation == "firm_redirect":
            return self._generate_firm_redirect(current_question, assignment_context, drift_analysis)
        
        elif recommendation == "strong_redirect":
            return self._generate_strong_redirect(current_question, assignment_context)
        
        elif recommendation == "bridge_redirect":
            return self._generate_bridge_redirect(current_question, drift_analysis)
        
        elif recommendation == "motivational_redirect":
            return self._generate_motivational_redirect(current_question, assignment_context)
        
        elif recommendation == "progress_redirect":
            return self._generate_progress_redirect(current_question, assignment_context, student_progress)
        
        else:
            return self._generate_standard_redirect(current_question, assignment_context, drift_analysis)
    
    def _generate_gentle_nudge(self, current_question: Dict, drift_analysis: Dict) -> str:
        """Generate gentle guidance back to focus"""
        question_title = current_question.get('title', 'the current question')
        
        return f"""That's an interesting point! Let's connect it back to **{question_title}** to make sure we're building toward your assignment response.

What specific evidence from the article helps answer this question? Let's focus on finding concrete examples or data that support your analysis."""
    
    def _generate_standard_redirect(self, current_question: Dict, assignment_context: Dict, 
                                  drift_analysis: Dict) -> str:
        """Generate standard redirection response"""
        question_id = current_question.get('id', 'Q')
        question_title = current_question.get('title', 'Current Question')
        evidence_required = current_question.get('required_evidence', 'specific evidence from the article')
        
        return f"""I understand your curiosity, but let's stay focused on your assignment to make the most of our time together.

**Current Focus: {question_id} - {question_title}**

Your assignment asks you to work with {evidence_required.lower()}. What specific information from the article addresses this question? Let's gather that evidence systematically."""
    
    def _generate_firm_redirect(self, current_question: Dict, assignment_context: Dict, 
                              drift_analysis: Dict) -> str:
        """Generate firm but supportive redirection"""
        question_id = current_question.get('id', 'Q')
        question_title = current_question.get('title', 'the current question')
        
        indicators = drift_analysis.get('indicators', [])
        drift_reason = ""
        if any('curiosity_driven' in ind for ind in indicators):
            drift_reason = "I know you're curious about the broader topic, but "
        elif any('meta_questions' in ind for ind in indicators):
            drift_reason = "I understand you might be questioning the relevance, but "
        else:
            drift_reason = "While that's an interesting direction, "
        
        return f"""{drift_reason}we need to focus on your assignment requirements to help you succeed.

**Let's refocus on {question_id}: {question_title}**

This question is designed to help you develop specific analytical skills. What concrete evidence from the article can you use to build your response? I'm here to guide you through finding and analyzing that evidence."""
    
    def _generate_strong_redirect(self, current_question: Dict, assignment_context: Dict) -> str:
        """Generate strong redirection for significant drift"""
        question_id = current_question.get('id', 'Q')
        question_title = current_question.get('title', 'the current question')
        word_target = current_question.get('word_target', '150-200 words')
        
        return f"""We've moved quite far from your assignment focus. Let me help you get back on track.

**Assignment Requirement: {question_id} - {question_title}**
**Target Response: {word_target}**

Your success depends on addressing this question directly with evidence from the assigned article. Let's start fresh:

1. What does this question specifically ask you to do?
2. What evidence from the article is most relevant?

I'll guide you step by step to build a strong response."""
    
    def _generate_bridge_redirect(self, current_question: Dict, drift_analysis: Dict) -> str:
        """Generate response that bridges curiosity back to assignment"""
        question_title = current_question.get('title', 'the current question')
        
        return f"""Your curiosity is great for learning! Let's channel that into your assignment work.

The question about **{question_title}** actually connects to what you're wondering about. If we can find solid evidence from the article first, we can then explore how it relates to the broader concepts you're interested in.

What specific data or examples from the article caught your attention? Let's start there and build your analysis."""
    
    def _generate_motivational_redirect(self, current_question: Dict, assignment_context: Dict) -> str:
        """Generate motivational response for students questioning relevance"""
        question_title = current_question.get('title', 'this question')
        bloom_level = current_question.get('bloom_level', 'analytical')
        
        return f"""I understand it might not be immediately clear why this matters. Let me explain how **{question_title}** develops important skills:

This question builds your {bloom_level} thinking abilities, which are essential for landscape ecology work. By working through the evidence systematically, you're learning to think like an ecologist.

The skills you develop here apply directly to real-world environmental challenges. Let's dive in - what's the first piece of evidence from the article that relates to this question?"""
    
    def _generate_progress_redirect(self, current_question: Dict, assignment_context: Dict, 
                                  student_progress: Dict) -> str:
        """Generate response to break circular patterns and promote progress"""
        question_id = current_question.get('id', 'Q')
        evidence_found = student_progress.get('evidence_found', [])
        
        if evidence_found:
            return f"""I notice we've been circling around similar questions. Let's make concrete progress on **{question_id}**.

You've already identified some evidence: {', '.join(evidence_found[:2])}{'...' if len(evidence_found) > 2 else ''}

Now let's take the next step: How does this evidence specifically answer the question? What's your analysis of what it means?"""
        else:
            return f"""Let's break out of this pattern and make real progress on **{question_id}**.

Instead of asking more questions right now, let's focus on finding concrete evidence. Look through the article and identify ONE specific example, quote, or data point that relates to this question.

Once you find it, tell me what it says and where it's located in the article."""
    
    def should_intervene(self, drift_analysis: Dict) -> bool:
        """Determine if intervention is needed based on analysis"""
        return (drift_analysis["drift_score"] > 0.3 and 
                drift_analysis["confidence"] > 0.4 and
                drift_analysis["recommendation"] != "continue")
    
    def get_intervention_urgency(self, drift_analysis: Dict) -> str:
        """Get urgency level for intervention"""
        score = drift_analysis["drift_score"]
        confidence = drift_analysis["confidence"]
        
        if score > 0.7 and confidence > 0.6:
            return "high"
        elif score > 0.5 and confidence > 0.5:
            return "medium"
        elif score > 0.3 and confidence > 0.4:
            return "low"
        else:
            return "none"