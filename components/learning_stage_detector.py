"""
Learning Stage Detector - Determines student's current learning stage for adaptive questioning
Analyzes conversation patterns to assess comprehension level and guide progressive questioning
"""

import streamlit as st
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

class LearningStageDetector:
    """Determines student's current learning stage for adaptive questioning"""
    
    def __init__(self):
        # Indicators for different comprehension levels
        self.comprehension_indicators = {
            "surface": {
                "keywords": ["what", "who", "when", "where", "define", "list", "identify"],
                "patterns": [r"(?i)what (is|are|does)", r"(?i)can you (tell|explain)", r"(?i)i don't understand"],
                "evidence": ["basic_questions", "confusion_statements", "request_definitions"]
            },
            "developing": {
                "keywords": ["how", "why", "because", "relationship", "connection", "pattern"],
                "patterns": [r"(?i)how does.*work", r"(?i)why (is|does)", r"(?i)the relationship between"],
                "evidence": ["causal_questions", "seeking_explanations", "basic_analysis_attempts"]
            },
            "proficient": {
                "keywords": ["analyze", "compare", "contrast", "evaluate", "significant", "implies"],
                "patterns": [r"(?i)this (suggests|indicates|implies)", r"(?i)compared to", r"(?i)the significance"],
                "evidence": ["analytical_language", "comparisons", "interpretation_attempts"]
            },
            "advanced": {
                "keywords": ["synthesize", "integrate", "critique", "hypothesis", "alternative", "limitation"],
                "patterns": [r"(?i)alternatively", r"(?i)this could mean", r"(?i)however.*might"],
                "evidence": ["critical_thinking", "alternative_explanations", "synthesis_attempts"]
            }
        }
        
        # Evidence-gathering stage indicators
        self.evidence_stages = {
            "not_started": {
                "indicators": ["no_citations", "no_specific_references", "vague_responses"],
                "patterns": [r"(?i)in general", r"(?i)I think", r"(?i)maybe"]
            },
            "initial_gathering": {
                "indicators": ["basic_citations", "page_references", "direct_quotes"],
                "patterns": [r"(?i)(page|p\.)\s*\d+", r"(?i)the article says", r"(?i)according to"]
            },
            "active_analysis": {
                "indicators": ["evidence_interpretation", "pattern_recognition", "data_analysis"],
                "patterns": [r"(?i)this (shows|demonstrates|indicates)", r"(?i)the data (suggests|reveals)"]
            },
            "synthesis_ready": {
                "indicators": ["multiple_evidence_pieces", "cross_referencing", "argument_building"],
                "patterns": [r"(?i)(furthermore|additionally|also)", r"(?i)combining.*evidence"]
            }
        }
        
        # Question engagement quality indicators
        self.engagement_quality = {
            "low": {
                "behaviors": ["minimal_responses", "yes_no_answers", "request_for_answers"],
                "patterns": [r"^(yes|no|ok|sure)\.?$", r"(?i)just tell me", r"(?i)what's the answer"]
            },
            "moderate": {
                "behaviors": ["basic_elaboration", "some_evidence", "follows_guidance"],
                "patterns": [r"(?i)I found", r"(?i)the article mentions", r"(?i)based on"]
            },
            "high": {
                "behaviors": ["detailed_responses", "unprompted_analysis", "question_generation"],
                "patterns": [r"(?i)this makes me wonder", r"(?i)I notice", r"(?i)this connects to"]
            }
        }
        
        # Readiness indicators for advancement
        self.advancement_indicators = {
            "concept_mastery": ["accurate_definitions", "correct_usage", "concept_connections"],
            "evidence_competency": ["relevant_citations", "appropriate_interpretation", "quality_selection"],
            "analytical_thinking": ["causal_reasoning", "pattern_recognition", "critical_evaluation"],
            "communication_clarity": ["organized_thoughts", "clear_explanations", "logical_flow"]
        }
    
    def assess_understanding_level(self, chat_history: List[Dict], current_question: Dict) -> Dict[str, Any]:
        """
        Analyze conversation to determine student's comprehension level
        
        Returns:
            Dict with understanding assessment including level, evidence, and recommendations
        """
        assessment = {
            "primary_level": "surface",
            "confidence": 0.0,
            "evidence_count": 0,
            "level_scores": {},
            "progression_indicators": [],
            "recommendations": []
        }
        
        if not chat_history:
            return assessment
        
        # Get recent user messages (last 6 for current context)
        recent_messages = [msg for msg in chat_history[-12:] if msg.get("role") == "user"]
        
        if not recent_messages:
            return assessment
        
        # Analyze each comprehension level
        for level, indicators in self.comprehension_indicators.items():
            level_score = 0.0
            level_evidence = []
            
            for msg in recent_messages:
                content = msg.get("content", "").lower()
                
                # Check keywords
                keyword_matches = sum(1 for keyword in indicators["keywords"] if keyword in content)
                level_score += keyword_matches * 0.1
                
                # Check patterns
                for pattern in indicators["patterns"]:
                    if re.search(pattern, msg.get("content", "")):
                        level_score += 0.2
                        level_evidence.append(f"pattern: {pattern}")
                
                # Look for evidence types
                for evidence_type in indicators["evidence"]:
                    if self._check_evidence_type(content, evidence_type):
                        level_score += 0.15
                        level_evidence.append(f"evidence: {evidence_type}")
            
            assessment["level_scores"][level] = {
                "score": min(1.0, level_score),
                "evidence": level_evidence[:3]  # Top 3 pieces of evidence
            }
        
        # Determine primary level
        if assessment["level_scores"]:
            primary_level = max(assessment["level_scores"], key=lambda x: assessment["level_scores"][x]["score"])
            primary_score = assessment["level_scores"][primary_level]["score"]
            
            # Only assign level if score is significant
            if primary_score > 0.2:
                assessment["primary_level"] = primary_level
                assessment["confidence"] = min(0.95, primary_score)
                assessment["evidence_count"] = len(assessment["level_scores"][primary_level]["evidence"])
        
        # Generate progression indicators and recommendations
        assessment.update(self._generate_progression_guidance(assessment, current_question))
        
        return assessment
    
    def detect_evidence_gathering_stage(self, messages: List[Dict], question_requirements: Dict) -> Dict[str, Any]:
        """Identify if student is finding, analyzing, or synthesizing evidence"""
        
        analysis = {
            "current_stage": "not_started",
            "stage_confidence": 0.0,
            "evidence_quality": "none",
            "citation_count": 0,
            "analysis_indicators": [],
            "next_stage_readiness": False
        }
        
        if not messages:
            return analysis
        
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        # Analyze evidence-gathering stages
        stage_scores = {}
        
        for stage, indicators in self.evidence_stages.items():
            stage_score = 0.0
            found_indicators = []
            
            for msg in user_messages:
                content = msg.get("content", "")
                
                # Check for stage patterns
                for pattern in indicators["patterns"]:
                    if re.search(pattern, content):
                        stage_score += 0.3
                        found_indicators.append(f"pattern: {re.search(pattern, content).group()}")
                
                # Check for stage-specific indicators
                if self._analyze_evidence_quality(content, stage):
                    stage_score += 0.2
                    found_indicators.append(f"indicator: {stage}_behavior")
            
            stage_scores[stage] = {
                "score": min(1.0, stage_score),
                "indicators": found_indicators[:2]
            }
        
        # Determine current stage
        if stage_scores:
            current_stage = max(stage_scores, key=lambda x: stage_scores[x]["score"])
            if stage_scores[current_stage]["score"] > 0.1:
                analysis["current_stage"] = current_stage
                analysis["stage_confidence"] = stage_scores[current_stage]["score"]
                analysis["analysis_indicators"] = stage_scores[current_stage]["indicators"]
        
        # Count citations and assess quality
        analysis["citation_count"] = self._count_citations(user_messages)
        analysis["evidence_quality"] = self._assess_evidence_quality(user_messages, question_requirements)
        
        # Assess readiness for next stage
        analysis["next_stage_readiness"] = self._assess_next_stage_readiness(
            analysis["current_stage"], analysis["stage_confidence"], analysis["citation_count"]
        )
        
        return analysis
    
    def evaluate_readiness_for_advancement(self, current_progress: Dict, question_goals: Dict) -> Dict[str, Any]:
        """Determine if student is ready for more complex questions"""
        
        readiness = {
            "ready_for_advancement": False,
            "advancement_confidence": 0.0,
            "mastery_areas": [],
            "development_areas": [],
            "recommended_next_level": None,
            "specific_gaps": []
        }
        
        understanding_level = current_progress.get("understanding_level", {})
        evidence_stage = current_progress.get("evidence_stage", {})
        
        # Check mastery indicators
        mastery_scores = {}
        
        for area, indicators in self.advancement_indicators.items():
            area_score = 0.0
            
            # Evaluate based on understanding level
            if understanding_level.get("primary_level") in ["proficient", "advanced"]:
                area_score += 0.3
            
            # Evaluate based on evidence stage
            if evidence_stage.get("current_stage") in ["active_analysis", "synthesis_ready"]:
                area_score += 0.3
            
            # Additional context-specific evaluation
            area_score += self._evaluate_mastery_area(area, current_progress)
            
            mastery_scores[area] = min(1.0, area_score)
            
            if area_score > 0.6:
                readiness["mastery_areas"].append(area)
            elif area_score < 0.4:
                readiness["development_areas"].append(area)
        
        # Calculate overall readiness
        avg_mastery = sum(mastery_scores.values()) / len(mastery_scores) if mastery_scores else 0.0
        readiness["advancement_confidence"] = avg_mastery
        readiness["ready_for_advancement"] = avg_mastery > 0.65
        
        # Recommend next level
        current_level = understanding_level.get("primary_level", "surface")
        level_progression = ["surface", "developing", "proficient", "advanced"]
        
        if readiness["ready_for_advancement"] and current_level in level_progression:
            current_index = level_progression.index(current_level)
            if current_index < len(level_progression) - 1:
                readiness["recommended_next_level"] = level_progression[current_index + 1]
        
        # Identify specific gaps
        readiness["specific_gaps"] = self._identify_learning_gaps(
            mastery_scores, question_goals, current_progress
        )
        
        return readiness
    
    def get_learning_stage_summary(self, chat_history: List[Dict], current_question: Dict, 
                                 assignment_context: Dict) -> Dict[str, Any]:
        """Generate comprehensive learning stage assessment"""
        
        # Assess understanding level
        understanding = self.assess_understanding_level(chat_history, current_question)
        
        # Detect evidence gathering stage  
        evidence_stage = self.detect_evidence_gathering_stage(
            chat_history, current_question
        )
        
        # Evaluate engagement quality
        engagement = self._assess_engagement_quality(chat_history)
        
        # Check advancement readiness
        current_progress = {
            "understanding_level": understanding,
            "evidence_stage": evidence_stage,
            "engagement_quality": engagement
        }
        
        advancement = self.evaluate_readiness_for_advancement(
            current_progress, current_question
        )
        
        return {
            "understanding_level": understanding,
            "evidence_stage": evidence_stage,
            "engagement_quality": engagement,
            "advancement_readiness": advancement,
            "overall_stage": self._determine_overall_stage(understanding, evidence_stage, engagement),
            "tutoring_recommendations": self._generate_tutoring_recommendations(
                understanding, evidence_stage, engagement, current_question
            )
        }
    
    def _check_evidence_type(self, content: str, evidence_type: str) -> bool:
        """Check if content shows specific type of evidence"""
        evidence_patterns = {
            "basic_questions": [r"(?i)what (is|are|does)", r"(?i)can you (tell|explain)"],
            "confusion_statements": [r"(?i)i don't (understand|get)", r"(?i)confused about"],
            "request_definitions": [r"(?i)define", r"(?i)what.*mean", r"(?i)meaning of"],
            "causal_questions": [r"(?i)why (does|is)", r"(?i)how (does|can)"],
            "seeking_explanations": [r"(?i)explain", r"(?i)help me understand"],
            "basic_analysis_attempts": [r"(?i)because", r"(?i)this means", r"(?i)relationship"],
            "analytical_language": [r"(?i)(analyze|significant|implies)", r"(?i)(pattern|trend)"],
            "comparisons": [r"(?i)(compare|contrast)", r"(?i)(similar|different)", r"(?i)(versus|vs)"],
            "interpretation_attempts": [r"(?i)(suggests|indicates)", r"(?i)this shows"],
            "critical_thinking": [r"(?i)(however|although)", r"(?i)(limitation|weakness)"],
            "alternative_explanations": [r"(?i)(alternatively|could also)", r"(?i)another (way|explanation)"],
            "synthesis_attempts": [r"(?i)(combine|integrate)", r"(?i)bringing together"]
        }
        
        if evidence_type not in evidence_patterns:
            return False
        
        return any(re.search(pattern, content) for pattern in evidence_patterns[evidence_type])
    
    def _analyze_evidence_quality(self, content: str, stage: str) -> bool:
        """Analyze if content matches evidence quality for given stage"""
        stage_patterns = {
            "not_started": [r"(?i)in general", r"(?i)I think", r"(?i)maybe"],
            "initial_gathering": [r"(?i)(page|p\.)\s*\d+", r"(?i)the article says"],
            "active_analysis": [r"(?i)this (shows|demonstrates)", r"(?i)the data"],
            "synthesis_ready": [r"(?i)(furthermore|additionally)", r"(?i)combined with"]
        }
        
        if stage not in stage_patterns:
            return False
            
        return any(re.search(pattern, content) for pattern in stage_patterns[stage])
    
    def _count_citations(self, messages: List[Dict]) -> int:
        """Count number of citations or references in messages"""
        citation_patterns = [
            r"(?i)(page|p\.)\s*\d+",
            r"(?i)(figure|fig\.)\s*\d+", 
            r"(?i)(table|tbl\.)\s*\d+",
            r"(?i)the article (states|says|mentions)",
            r"(?i)according to"
        ]
        
        citation_count = 0
        for msg in messages:
            content = msg.get("content", "")
            citation_count += sum(1 for pattern in citation_patterns if re.search(pattern, content))
        
        return citation_count
    
    def _assess_evidence_quality(self, messages: List[Dict], question_requirements: Dict) -> str:
        """Assess overall quality of evidence presented"""
        if not messages:
            return "none"
        
        citation_count = self._count_citations(messages)
        
        # Look for quality indicators
        quality_indicators = 0
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Check for specific, relevant evidence
            if any(word in content for word in ["data", "study", "research", "findings"]):
                quality_indicators += 1
                
            # Check for analysis rather than just description
            if any(word in content for word in ["because", "therefore", "suggests", "indicates"]):
                quality_indicators += 1
        
        if citation_count >= 3 and quality_indicators >= 2:
            return "high"
        elif citation_count >= 1 and quality_indicators >= 1:
            return "moderate"
        elif citation_count >= 1:
            return "low"
        else:
            return "none"
    
    def _assess_next_stage_readiness(self, current_stage: str, confidence: float, citation_count: int) -> bool:
        """Assess if student is ready to advance to next evidence stage"""
        stage_requirements = {
            "not_started": {"min_confidence": 0.0, "min_citations": 0},
            "initial_gathering": {"min_confidence": 0.3, "min_citations": 1},
            "active_analysis": {"min_confidence": 0.5, "min_citations": 2},
            "synthesis_ready": {"min_confidence": 0.7, "min_citations": 3}
        }
        
        if current_stage not in stage_requirements:
            return False
            
        req = stage_requirements[current_stage]
        return confidence >= req["min_confidence"] and citation_count >= req["min_citations"]
    
    def _evaluate_mastery_area(self, area: str, current_progress: Dict) -> float:
        """Evaluate specific mastery area based on progress indicators"""
        understanding = current_progress.get("understanding_level", {})
        evidence = current_progress.get("evidence_stage", {})
        
        area_scores = {
            "concept_mastery": understanding.get("confidence", 0.0) * 0.4,
            "evidence_competency": min(0.4, evidence.get("citation_count", 0) * 0.1),
            "analytical_thinking": 0.3 if understanding.get("primary_level") in ["proficient", "advanced"] else 0.1,
            "communication_clarity": 0.2 if evidence.get("evidence_quality") in ["moderate", "high"] else 0.0
        }
        
        return area_scores.get(area, 0.0)
    
    def _identify_learning_gaps(self, mastery_scores: Dict, question_goals: Dict, 
                              current_progress: Dict) -> List[str]:
        """Identify specific areas where student needs development"""
        gaps = []
        
        # Check each mastery area
        for area, score in mastery_scores.items():
            if score < 0.5:
                if area == "concept_mastery":
                    gaps.append("Need stronger understanding of key concepts")
                elif area == "evidence_competency": 
                    gaps.append("Need more specific evidence from the article")
                elif area == "analytical_thinking":
                    gaps.append("Need deeper analysis beyond description")
                elif area == "communication_clarity":
                    gaps.append("Need clearer organization of ideas")
        
        # Check evidence stage gaps
        evidence_stage = current_progress.get("evidence_stage", {})
        if evidence_stage.get("citation_count", 0) < 2:
            gaps.append("Need more citations and references")
            
        if evidence_stage.get("evidence_quality") == "none":
            gaps.append("Need to find relevant evidence from article")
        
        return gaps[:3]  # Return top 3 most critical gaps
    
    def _assess_engagement_quality(self, chat_history: List[Dict]) -> Dict[str, Any]:
        """Assess student's engagement quality based on conversation patterns"""
        
        user_messages = [msg for msg in chat_history if msg.get("role") == "user"]
        
        if not user_messages:
            return {"level": "low", "indicators": [], "message_count": 0}
        
        quality_scores = {}
        
        for level, indicators in self.engagement_quality.items():
            level_score = 0.0
            found_indicators = []
            
            for msg in user_messages:
                content = msg.get("content", "")
                
                # Check patterns
                for pattern in indicators["patterns"]:
                    if re.search(pattern, content):
                        level_score += 0.2
                        found_indicators.append(f"pattern: {pattern}")
                
                # Check behaviors (simplified)
                if level == "high" and len(content) > 100:  # Detailed responses
                    level_score += 0.1
                elif level == "low" and len(content) < 20:  # Minimal responses
                    level_score += 0.1
            
            quality_scores[level] = {
                "score": min(1.0, level_score),
                "indicators": found_indicators[:2]
            }
        
        # Determine primary engagement level
        primary_level = max(quality_scores, key=lambda x: quality_scores[x]["score"])
        
        return {
            "level": primary_level,
            "indicators": quality_scores[primary_level]["indicators"],
            "message_count": len(user_messages),
            "avg_message_length": sum(len(msg.get("content", "")) for msg in user_messages) / len(user_messages)
        }
    
    def _determine_overall_stage(self, understanding: Dict, evidence_stage: Dict, engagement: Dict) -> str:
        """Determine overall learning stage combining all factors"""
        
        understanding_level = understanding.get("primary_level", "surface")
        evidence_level = evidence_stage.get("current_stage", "not_started")
        engagement_level = engagement.get("level", "low")
        
        # Create composite score
        level_weights = {
            "surface": 1, "developing": 2, "proficient": 3, "advanced": 4,
            "not_started": 1, "initial_gathering": 2, "active_analysis": 3, "synthesis_ready": 4,
            "low": 1, "moderate": 2, "high": 3
        }
        
        understanding_score = level_weights.get(understanding_level, 1)
        evidence_score = level_weights.get(evidence_level, 1)
        engagement_score = level_weights.get(engagement_level, 1)
        
        # Weighted average (understanding is most important)
        composite_score = (understanding_score * 0.5 + evidence_score * 0.3 + engagement_score * 0.2)
        
        if composite_score >= 3.5:
            return "advanced_ready"
        elif composite_score >= 2.5:
            return "analysis_ready"
        elif composite_score >= 1.5:
            return "evidence_gathering"
        else:
            return "comprehension_building"
    
    def _generate_progression_guidance(self, assessment: Dict, current_question: Dict) -> Dict[str, Any]:
        """Generate specific guidance for student progression"""
        
        level = assessment.get("primary_level", "surface")
        confidence = assessment.get("confidence", 0.0)
        
        guidance = {
            "progression_indicators": [],
            "recommendations": []
        }
        
        # Level-specific guidance
        if level == "surface" and confidence > 0.5:
            guidance["progression_indicators"].append("Ready to move beyond basic comprehension")
            guidance["recommendations"].append("Start asking 'how' and 'why' questions")
            
        elif level == "developing" and confidence > 0.6:
            guidance["progression_indicators"].append("Developing analytical thinking")
            guidance["recommendations"].append("Focus on finding specific evidence")
            
        elif level == "proficient" and confidence > 0.7:
            guidance["progression_indicators"].append("Ready for synthesis challenges")
            guidance["recommendations"].append("Begin connecting concepts across evidence")
            
        elif level == "advanced":
            guidance["progression_indicators"].append("Demonstrating critical thinking")
            guidance["recommendations"].append("Encourage evaluation and alternative perspectives")
        
        # Add question-specific recommendations
        if current_question:
            bloom_level = current_question.get("bloom_level", "understand")
            if bloom_level == "analyze" and level in ["surface", "developing"]:
                guidance["recommendations"].append("Build toward analysis with evidence-based reasoning")
        
        return guidance
    
    def _generate_tutoring_recommendations(self, understanding: Dict, evidence_stage: Dict, 
                                         engagement: Dict, current_question: Dict) -> List[str]:
        """Generate specific recommendations for tutoring approach"""
        
        recommendations = []
        
        # Understanding-based recommendations
        level = understanding.get("primary_level", "surface")
        if level == "surface":
            recommendations.append("Use concrete examples and clear definitions")
        elif level == "developing":
            recommendations.append("Guide toward causal relationships and patterns")
        elif level == "proficient":
            recommendations.append("Challenge with comparative analysis")
        elif level == "advanced":
            recommendations.append("Encourage critical evaluation and synthesis")
        
        # Evidence-based recommendations
        evidence_level = evidence_stage.get("current_stage", "not_started")
        if evidence_level == "not_started":
            recommendations.append("Guide to specific sections of the article")
        elif evidence_level == "initial_gathering":
            recommendations.append("Help interpret and analyze found evidence")
        elif evidence_level == "active_analysis":
            recommendations.append("Support synthesis across multiple evidence pieces")
        
        # Engagement-based recommendations  
        engagement_level = engagement.get("level", "low")
        if engagement_level == "low":
            recommendations.append("Use encouraging, supportive questioning")
        elif engagement_level == "high":
            recommendations.append("Allow exploration while maintaining focus")
        
        return recommendations[:4]  # Return top 4 most relevant recommendations