import streamlit as st
import json
from datetime import datetime
from typing import List, Dict, Any
import requests
import time
import os
import re
try:
    from anthropic import Anthropic  # Optional
except Exception:
    Anthropic = None
from components.gis_question_templates import get_gis_template

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..'))
PROMPTS_FILE_PATH = os.path.join(_PROJECT_ROOT, 'data', 'socratic_prompts.json')

class SocraticChatEngine:
    """A Socratic chat engine for discussing landscape ecology articles."""
    
    def __init__(self):
        self.conversation_levels = {
            1: "comprehension",
            2: "analysis",
            3: "synthesis",
            4: "evaluation",
        }
        
        try:
            with open(PROMPTS_FILE_PATH, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
        except Exception:
            self.prompts = {}
            
        # self.client = Anthropic(api_key=st.secrets["anthropic"]["api_key"]) # Temporarily commented out for debugging
        self.client = None
        self.model = "claude-3-opus-20240229"
        self.temperature = 0.5
        self.max_tokens = 4000
    
    def load_prompts(self):
        """Load Socratic questioning prompts from JSON file"""
        try:
            with open(PROMPTS_FILE_PATH, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
        except Exception:
            # Default prompts if file doesn't exist
            self.prompts = {
                "comprehension": [
                    "What is the main research question addressed in this article?",
                    "Can you identify the study system or location described?",
                    "What methods did the researchers use to collect their data?"
                ],
                "analysis": [
                    "Why do you think the researchers chose this particular approach?",
                    "What patterns do you notice in the results they present?",
                    "How do the findings relate to the hypothesis they proposed?"
                ],
                "synthesis": [
                    "How does this study connect to landscape ecology principles we've discussed?",
                    "What relationship do you see between this work and previous research?",
                    "How might these findings apply to other landscape types?"
                ],
                "evaluation": [
                    "What assumptions are the authors making that might not be stated?",
                    "How could the methodology be improved or extended?",
                    "What alternative explanations might exist for these results?"
                ]
            }
    
    def get_conversation_level(self, messages: List[Dict]) -> int:
        """Determine current conversation level based on interaction history"""
        if len(messages) < 4:
            return 1
        elif len(messages) < 8:
            return 2
        elif len(messages) < 12:
            return 3
        else:
            return 4
    
    def generate_socratic_response(self, 
                                 user_message: str, 
                                 conversation_history: List[Dict],
                                 article_context: str,
                                 landscape_knowledge: str) -> str:
        """Generate an informed response that balances substantive answers with guided discovery"""
        
        current_level = self.get_conversation_level(conversation_history)
        level_name = self.conversation_levels[current_level]
        
        # Build the system prompt for balanced teaching
        system_prompt = f"""
        You are a knowledgeable Landscape Ecology AI tutor specializing in research article analysis. You use a balanced approach combining informative answers with guided discovery.

        CORE TEACHING PRINCIPLES:
        1. PROVIDE SUBSTANTIVE ANSWERS when students ask direct questions about concepts, methods, or findings
        2. Share relevant information from the article being discussed to enhance understanding
        3. Use guided questions to encourage deeper thinking AFTER providing helpful information
        4. Be an expert source of knowledge while still promoting critical analysis
        5. Balance explanation with exploration - inform first, then guide discovery

        CURRENT CONVERSATION LEVEL: {level_name}
        
        ARTICLE CONTEXT (be very knowledgeable about this):
        {article_context[:1000]}
        
        RELEVANT LANDSCAPE ECOLOGY KNOWLEDGE:
        {landscape_knowledge[:800]}
        
        RESPONSE STRATEGY:
        - When students ask "what is X?" or "how does Y work?" → Provide clear, informative explanations
        - When students show understanding → Ask follow-up questions to deepen analysis
        - When students seem confused → Explain concepts clearly, then check understanding
        - When students make statements → Validate good points and ask them to elaborate or connect to broader concepts
        - Always reference specific details from the article when relevant
        - Connect article findings to broader landscape ecology principles
        
        LEVEL-SPECIFIC FOCUS ({level_name}):
        {self._get_level_guidance(level_name)}
        
        Be conversational, knowledgeable, and genuinely helpful. Provide substantial information while encouraging critical thinking.
        """
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history (last 6 exchanges to keep context manageable)
        recent_history = conversation_history[-12:] if len(conversation_history) > 12 else conversation_history
        for msg in recent_history:
            messages.append({
                "role": "user" if msg["role"] == "student" else "assistant",
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Try LLM API (OpenAI if available, smart local otherwise)
            response = self._call_llm_api(messages)
            return response
            
        except Exception as e:
            # If there's an error, try direct concept recognition as fallback
            user_msg = user_message.lower()
            
            # Provide informative responses with guided follow-ups
            if 'transdisciplin' in user_msg:
                return "Transdisciplinarity goes beyond interdisciplinary work by creating entirely new frameworks that transcend traditional disciplinary boundaries. Unlike interdisciplinary research where ecologists and geographers collaborate while maintaining their disciplinary perspectives, transdisciplinary work develops new conceptual approaches that integrate knowledge systems. In landscape ecology, this might mean creating new theories that combine social, ecological, and technological perspectives. How do you see this approach being applied in the article we're discussing?"
            elif 'interdisciplin' in user_msg:
                return "Interdisciplinary approaches in landscape ecology combine methods and perspectives from multiple fields like ecology, geography, remote sensing, and social sciences. Each discipline brings unique tools - ecologists contribute species-habitat relationships, geographers add spatial analysis skills, and remote sensing specialists provide landscape-scale data. This integration is essential because landscape-scale phenomena can't be understood through any single disciplinary lens. What interdisciplinary elements do you notice in this study's methodology?"
            elif 'connectivity' in user_msg:
                return "Connectivity refers to how landscape elements facilitate or impede movement of organisms, materials, or energy. There are two types: structural connectivity (physical arrangement of landscape elements) and functional connectivity (how organisms actually move through the landscape). Factors like corridors, stepping stones, and matrix permeability affect connectivity. The scale matters too - what's connected for a bird might not be for a beetle. What types of connectivity are discussed in your article?"
            elif 'fragmentation' in user_msg:
                return "Habitat fragmentation breaks continuous habitats into smaller, isolated patches, creating several key effects: reduced patch size (affects carrying capacity), increased edge effects (changing microclimates and species composition), and reduced connectivity (limiting movement and gene flow). This can lead to local extinctions, reduced biodiversity, and altered ecosystem processes. The matrix between fragments also matters - some are more permeable than others. How does the study you're reading address fragmentation impacts?"
            elif 'scale' in user_msg:
                return "Scale is fundamental in landscape ecology, involving both spatial extent (area covered) and resolution (level of detail). Different processes operate at different scales - local succession, landscape-level disturbance regimes, regional climate patterns. What's visible at one scale may not be apparent at another. For example, individual tree mortality might be random at the local scale but show clear patterns at the landscape scale due to environmental gradients. What scales are considered in your article?"
            elif 'edge effect' in user_msg:
                return "Edge effects occur where two different habitats meet, creating unique conditions different from either habitat's interior. Edges typically have increased light, temperature fluctuation, wind exposure, and different species composition. They can extend 10-100+ meters into forest interiors depending on what's being measured. Some species benefit from edges (edge species) while others avoid them (interior species). The edge-to-interior ratio increases dramatically as patches get smaller. What edge effects are mentioned in your study?"
            elif 'metapopulation' in user_msg:
                return "A metapopulation is a group of local populations connected by migration, where local extinctions can be recolonized from other patches. This concept explains how species persist in fragmented landscapes through a balance of extinction and colonization. Key factors include patch size (affects extinction probability), isolation (affects colonization), and population size (affects migration). The 'source-sink' dynamic is crucial - some patches are net producers of migrants while others depend on immigration. Does your article discuss metapopulation dynamics?"
            elif 'disturbance' in user_msg:
                return "Disturbances are discrete events that disrupt ecosystems and create heterogeneity across landscapes. They vary in intensity, frequency, duration, and spatial pattern. Natural disturbances include fire, windstorms, floods, and pest outbreaks, while human disturbances include logging, urbanization, and agriculture. Disturbance regimes (the pattern of disturbances over time) shape landscape patterns and are often more important than individual disturbance events. What disturbances are discussed in your article?"
            elif 'pattern' in user_msg:
                return "Spatial patterns in landscapes result from interactions between environmental gradients, disturbance history, and biological processes. Common patterns include gradients (continuous change), patches (discrete units), corridors (linear features), and mosaics (complex mixtures). Pattern analysis uses metrics like patch size, shape complexity, connectivity, and spatial arrangement. Understanding patterns helps predict ecological processes and species distributions. What spatial patterns does the study describe?"
            elif 'heterogeneity' in user_msg:
                return "Landscape heterogeneity refers to the spatial variation in environmental conditions, resources, or habitats across an area. It can result from topography, climate, soils, disturbance history, and human activities. Heterogeneity is crucial because it creates diverse niches, affects species diversity, influences ecological processes, and provides resilience against environmental changes. Different species perceive and respond to heterogeneity differently based on their life history traits. How does heterogeneity feature in your article?"
            else:
                return "That's an interesting question about landscape ecology. Can you tell me more about what specific aspect you'd like to explore?"
    
    def _call_llm_api(self, messages: List[Dict[str, str]]) -> str:
        """Call open source LLM - try multiple providers for best results"""
        
        # First try Groq (fastest Llama 3 inference, free tier)
        groq_response = self._try_groq_api(messages)
        if groq_response and len(groq_response.strip()) > 10:
            return groq_response
        
        # Then try Together AI (multiple open source models, free tier)
        together_response = self._try_together_api(messages)
        if together_response and len(together_response.strip()) > 10:
            return together_response
        
        # Finally use our ultra-advanced local system as fallback
        return self._generate_llm_like_response(messages)
    
    def _format_messages_for_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages into a single prompt"""
        prompt = ""
        for msg in messages[-6:]:  # Use last 6 messages for context
            role = "Human" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant:"
        return prompt
    
    def _call_open_source_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call open source LLM via Hugging Face Inference API"""
        
        # Convert messages to proper format for the model
        prompt = self._format_messages_for_llm(messages)
        
        # Try multiple open source models in order of preference
        models_to_try = [
            "meta-llama/Llama-2-7b-chat-hf",  # Llama2 Chat
            "mistralai/Mistral-7B-Instruct-v0.1",  # Mistral Instruct
            "microsoft/DialoGPT-large",  # DialoGPT (fallback)
        ]
        
        for model_name in models_to_try:
            try:
                response = self._query_huggingface_model(model_name, prompt)
                if response and len(response.strip()) > 10:  # Valid response
                    return self._clean_model_response(response)
            except Exception as e:
                continue  # Try next model
        
        # If all models fail, raise exception to trigger local fallback
        raise Exception("All open source models unavailable")
    
    def _query_huggingface_model(self, model_name: str, prompt: str) -> str:
        """Query a specific Hugging Face model"""
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        headers = {
            "Authorization": "Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Demo token
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
        
        raise Exception(f"Model {model_name} returned status {response.status_code}")
    
    def _format_messages_for_llm(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation for open source LLM models"""
        
        # Get the system message (first message)
        system_msg = ""
        conversation = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)
        
        # Format for Llama2/Mistral chat format
        prompt = f"<s>[INST] {system_msg}\n\n"
        
        # Add conversation history (keep it manageable)
        recent_conversation = conversation[-6:] if len(conversation) > 6 else conversation
        
        for i, msg in enumerate(recent_conversation[:-1]):  # All but the last message
            if msg["role"] == "user":
                prompt += f"Student: {msg['content']}\n"
            else:
                prompt += f"Tutor: {msg['content']}\n"
        
        # Add the current user message
        if recent_conversation:
            last_msg = recent_conversation[-1]
            prompt += f"\nStudent: {last_msg['content']}\n\nRespond as a Socratic tutor who guides through questions, never gives direct answers: [/INST]"
        
        return prompt
    
    def _clean_model_response(self, response: str) -> str:
        """Clean and format the model response"""
        # Remove common artifacts from model responses
        cleaned = response.strip()
        
        # Remove potential repetition or artifacts
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Student:', 'Tutor:', 'Human:', 'Assistant:')):
                cleaned_lines.append(line)
        
        result = ' '.join(cleaned_lines)
        
        # Ensure it's a reasonable length
        if len(result) > 400:
            result = result[:400] + "..."
        
        # Make sure it ends with a question mark if it's supposed to be a question
        if result and not result.endswith(('?', '.', '!', '...')):
            result += "?"
        
        return result if result else "What aspects of this research would you like to explore further?"
    
    def _generate_smart_socratic_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate intelligent Socratic responses based on conversation context"""
        
        # Get last user message and conversation context
        if messages:
            user_msg = messages[-1]["content"].lower()
            conversation_length = len([m for m in messages if m["role"] == "user"])
        else:
            return "What aspects of this article would you like to explore?"
        
        # Analyze user message for key concepts
        landscape_terms = [
            "habitat", "fragmentation", "connectivity", "patch", "corridor", 
            "edge", "scale", "heterogeneity", "disturbance", "metapopulation",
            "spatial", "pattern", "process", "landscape", "ecology"
        ]
        
        research_terms = [
            "method", "data", "result", "finding", "hypothesis", "conclusion",
            "analysis", "study", "research", "experiment", "observation"
        ]
        
        found_landscape = any(term in user_msg for term in landscape_terms)
        found_research = any(term in user_msg for term in research_terms)
        
        # Check for recent repetition to avoid giving same response
        recent_responses = [m["content"] for m in messages if m["role"] == "assistant"][-3:]
        
        # Generate diverse contextual responses
        responses_pool = self._get_diverse_responses(user_msg, conversation_length, found_landscape, found_research)
        
        # Filter out recently used responses
        available_responses = [r for r in responses_pool if not any(self._responses_too_similar(r, prev) for prev in recent_responses)]
        
        if not available_responses:
            available_responses = responses_pool  # Use all if none available
        
        import random
        return random.choice(available_responses)
    
    def _extract_key_term(self, text: str, terms: List[str]) -> str:
        """Extract the first matching key term from text"""
        for term in terms:
            if term in text:
                return term
        return "this concept"
    
    def _get_diverse_responses(self, user_msg: str, conversation_length: int, found_landscape: bool, found_research: bool) -> List[str]:
        """Generate diverse pool of responses based on context"""
        responses = []
        
        # Scale-specific responses (since user mentioned scales)
        if "scale" in user_msg:
            responses.extend([
                "Interesting point about scale! How do you think the scale of observation might affect what patterns you can detect?",
                "Scale is crucial in landscape ecology. What happens when you zoom in versus zoom out on this system?",
                "You're thinking about scale - how do you think the researchers chose their particular scale of study?",
                "What trade-offs do you see between studying this at a fine scale versus a broad scale?"
            ])
        
        # Connectivity/fragmentation specific responses
        if any(term in user_msg for term in ["connectivity", "fragmentation", "patch", "corridor"]):
            responses.extend([
                "That's a key landscape concept! How do you think connectivity changes as fragmentation increases?",
                "What evidence would you look for to measure connectivity in this landscape?",
                "How might different species experience connectivity differently in this system?",
                "What factors do you think influence how fragments connect to each other?"
            ])
        
        # Pattern-process responses
        if any(term in user_msg for term in ["pattern", "process", "relationship"]):
            responses.extend([
                "Excellent - you're thinking about pattern-process relationships! Can you give a specific example from the article?",
                "How do you think patterns at one scale might influence processes at another scale?",
                "What mechanisms might create the patterns described in this study?",
                "Do you see any feedback loops between patterns and processes here?"
            ])
        
        # General responses based on conversation level
        if conversation_length <= 2:  # Early conversation
            responses.extend([
                "What assumptions are you making as you think about this?",
                "Can you walk me through your reasoning here?",
                "What evidence from your reading supports that idea?",
                "How would you test that hypothesis?"
            ])
        elif conversation_length <= 6:  # Mid conversation
            responses.extend([
                "That raises an interesting question - what alternative explanations might there be?",
                "How does this connect to other landscape ecology principles you know?",
                "What would you expect to see if your thinking is correct?",
                "Can you think of a real-world example that demonstrates this?"
            ])
        else:  # Advanced conversation
            responses.extend([
                "What are the broader implications of what you're describing?",
                "How might this knowledge influence conservation strategies?",
                "What questions does this raise for future research?",
                "How confident are you in this interpretation, and why?"
            ])
        
        # Ensure we have enough responses
        if len(responses) < 3:
            responses.extend([
                "What makes you think that? Can you elaborate on your reasoning?",
                "That's an interesting perspective. How might you investigate that further?",
                "What other factors might be important to consider here?",
                "Can you connect this to any landscape ecology concepts we've discussed?"
            ])
        
        return responses
    
    def _responses_too_similar(self, response1: str, response2: str) -> bool:
        """Check if two responses are too similar (simple similarity check)"""
        if not response1 or not response2:
            return False
        
        # Remove common words and compare key content
        common_words = {"what", "how", "why", "do", "you", "think", "that", "the", "this", "a", "an", "is", "are", "can", "might", "would"}
        
        words1 = set(response1.lower().split()) - common_words
        words2 = set(response2.lower().split()) - common_words
        
        # If more than 60% of content words overlap, consider similar
        if len(words1) == 0 or len(words2) == 0:
            return False
            
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.6
    
    def _generate_intelligent_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate more intelligent responses using enhanced knowledge and context"""
        
        # Get user message and context
        if messages:
            user_msg = messages[-1]["content"].lower()
            conversation_length = len([m for m in messages if m["role"] == "user"])
        else:
            return "What aspects of this article would you like to explore?"
        
        # Extract key concepts from user message
        concepts = self._extract_concepts_from_message(user_msg)
        
        # Get relevant knowledge from enhanced knowledge base
        from components.rag_system import get_rag_system
        rag_system = get_rag_system()
        relevant_knowledge = rag_system.retrieve_relevant_knowledge(user_msg, top_k=3)
        
        # Generate contextually intelligent response
        response = self._create_contextual_response(user_msg, concepts, relevant_knowledge, conversation_length)
        
        # Ensure response hasn't been used recently
        recent_responses = [m["content"] for m in messages if m["role"] == "assistant"][-3:]
        if any(self._responses_too_similar(response, prev) for prev in recent_responses):
            # Generate alternative response
            response = self._create_alternative_response(user_msg, concepts, conversation_length)
        
        return response
    
    def _extract_concepts_from_message(self, message: str) -> List[str]:
        """Extract landscape ecology concepts from user message"""
        concepts = []
        
        concept_mapping = {
            # Scale concepts
            'scale': ['scale', 'spatial', 'temporal', 'hierarchy', 'grain', 'extent'],
            # Pattern concepts  
            'pattern': ['pattern', 'heterogeneity', 'composition', 'configuration', 'structure'],
            # Connectivity concepts
            'connectivity': ['connectivity', 'corridor', 'fragmentation', 'isolation', 'movement'],
            # Disturbance concepts
            'disturbance': ['disturbance', 'fire', 'flood', 'storm', 'succession', 'recovery'],
            # Population concepts
            'population': ['population', 'metapopulation', 'migration', 'dispersal', 'colonization'],
            # Habitat concepts
            'habitat': ['habitat', 'patch', 'matrix', 'edge', 'interior', 'quality'],
            # Methods concepts
            'methods': ['method', 'sampling', 'analysis', 'data', 'gis', 'remote sensing'],
            # Conservation concepts
            'conservation': ['conservation', 'restoration', 'management', 'protected', 'reserve']
        }
        
        for category, terms in concept_mapping.items():
            if any(term in message for term in terms):
                concepts.append(category)
        
        return concepts
    
    def _create_contextual_response(self, user_msg: str, concepts: List[str], knowledge: List[str], conv_length: int) -> str:
        """Create intelligent contextual response"""
        
        responses = []
        
        # Generate concept-specific responses
        if 'scale' in concepts:
            if 'pattern' in concepts or 'process' in user_msg:
                responses.extend([
                    "Excellent question about scale! How do you think the relationship between pattern and process changes when you study this system at different scales?",
                    "Scale is fundamental here. What patterns might be visible at a landscape scale that wouldn't be apparent if you only looked at individual patches?",
                    "That's a key insight about scale. How might the processes that create these patterns differ between local and regional scales?"
                ])
            else:
                responses.extend([
                    "Scale is crucial in landscape ecology. What happens to your understanding of this system when you 'zoom out' to see the bigger picture?",
                    "Interesting point about scale. How do you think the researchers chose their particular scale of observation, and what trade-offs did they make?"
                ])
        
        if 'connectivity' in concepts:
            if 'fragmentation' in user_msg:
                responses.extend([
                    "Great connection! How do you think increasing fragmentation affects the different ways organisms can move through this landscape?",
                    "You're thinking about a key trade-off. As habitats become more fragmented, what strategies might different species use to maintain connectivity?",
                    "That's an important relationship. Can you think of specific examples of how the organisms in this study might experience connectivity differently than the researchers measured it?"
                ])
            else:
                responses.extend([
                    "Connectivity is fascinating! What evidence would convince you that two patches are truly 'connected' for the organisms in this study?",
                    "Good thinking about connectivity. How might functional connectivity (what organisms actually experience) differ from structural connectivity (what we see on maps)?"
                ])
        
        if 'disturbance' in concepts:
            responses.extend([
                "Disturbance creates such interesting patterns! How do you think the timing and frequency of disturbances might influence what the researchers observed?",
                "That's a great observation about disturbance. What role do you think disturbance history plays in creating the current landscape patterns?",
                "Disturbances operate at multiple scales - how might local disturbances interact with landscape-scale disturbance regimes?"
            ])
        
        if 'methods' in concepts:
            responses.extend([
                "Good question about methodology! What assumptions do you think the researchers made when they chose this approach?",
                "Methods are so important. How might their results have differed if they had collected data at a different scale or resolution?",
                "That's a thoughtful point about methods. What are the strengths and limitations of their approach for addressing their research question?"
            ])
        
        # Add knowledge-informed responses if we have relevant knowledge
        if knowledge:
            # Fix: knowledge is a list, so join it first, then take first 200 words
            knowledge_text = ' '.join(knowledge)
            knowledge_words = knowledge_text.split()[:200]
            knowledge_sample = ' '.join(knowledge_words)
            
            if 'source' in knowledge_sample.lower() and 'sink' in knowledge_sample.lower():
                responses.append("I see you're exploring concepts related to source-sink dynamics. How might habitat quality vary across the landscape in this study?")
            if 'metapopulation' in knowledge_sample.lower():
                responses.append("This connects to metapopulation theory. What evidence would you need to determine if the populations in this study function as a metapopulation?")
        
        # Add conversation-level appropriate responses
        if conv_length <= 3:  # Early conversation
            responses.extend([
                "What assumptions might you be making as you think through this?",
                "Can you walk me through the reasoning that led you to that conclusion?",
                "What specific evidence from the article supports your thinking?"
            ])
        elif conv_length <= 8:  # Mid conversation  
            responses.extend([
                "How does this connect to broader landscape ecology principles?",
                "What alternative explanations might account for what you're observing?",
                "Can you think of a real-world management situation where this would be important?"
            ])
        else:  # Advanced conversation
            responses.extend([
                "What are the broader implications of this for conservation or management?",
                "How confident are you in this interpretation? What additional data would strengthen your conclusion?",
                "What questions does this raise for future research in landscape ecology?"
            ])
        
        # Return a random response from available options
        if responses:
            import random
            return random.choice(responses)
        else:
            return "That's an interesting perspective. How might you test that hypothesis using landscape ecological approaches?"
    
    def _create_alternative_response(self, user_msg: str, concepts: List[str], conv_length: int) -> str:
        """Generate alternative response when primary response too similar to recent ones"""
        alternatives = [
            "Let me ask this differently - what would you expect to see if your hypothesis is correct?",
            "That raises an interesting question. How might you approach this from a different angle?",
            "What other factors might be important to consider in this system?",
            "How might this relate to landscape ecology concepts beyond what we've already discussed?",
            "What would happen if you changed one key assumption in your thinking?",
            "Can you think of an analogous situation in a completely different type of landscape?",
            "What questions does this raise about the generalizability of these findings?",
            "How might different stakeholders (researchers, managers, policymakers) view this differently?"
        ]
        
        import random
        return random.choice(alternatives)
    
    def _try_groq_api(self, messages: List[Dict[str, str]]) -> str:
        """Try Groq API for fast Llama 3 inference (free tier)"""
        try:
            import requests
            
            if not messages:
                return ""
            
            user_message = messages[-1]["content"]
            
            # Get relevant knowledge context
            from components.rag_system import get_rag_system
            rag_system = get_rag_system()
            relevant_knowledge = rag_system.retrieve_relevant_knowledge(user_message, top_k=2)
            
            # Build context
            context = ""
            if relevant_knowledge:
                knowledge_text = ' '.join(relevant_knowledge)
                knowledge_words = knowledge_text.split()[:300]
                context = ' '.join(knowledge_words)
            
            # Create messages for Groq API format
            api_messages = [
                {
                    "role": "system",
                    "content": f"""You are a Socratic AI tutor for landscape ecology. Guide students through critical thinking using questions, not direct answers.

Key principles:
- Ask thought-provoking questions that build on student responses
- Connect concepts to landscape ecology principles  
- Handle informal language and typos gracefully
- Be encouraging and intellectually curious
- Use the knowledge context when relevant

{f"Relevant context: {context}" if context else ""}

Always respond with 1-2 engaging questions that help the student explore the concept deeper."""
                }
            ]
            
            # Add recent conversation history
            for msg in messages[-4:]:
                api_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
            
            # Use real Groq API with Llama 3
            import os
            groq_api_key = os.environ.get('GROQ_API_KEY')
            if not groq_api_key:
                try:
                    groq_api_key = st.secrets.get('GROQ_API_KEY')
                except Exception:
                    groq_api_key = None
            
            if groq_api_key:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",  # Fast, high-quality Llama 3.1 model
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 300,  # Increased for more detailed responses
                        "stream": False
                    },
                    timeout=15
                )
            else:
                response = None
            
            if response and response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"].strip()
                    if generated_text and len(generated_text) > 10:
                        return generated_text
            
            return ""
            
        except Exception as e:
            return ""
    
    def _try_together_ai_api(self, messages: List[Dict[str, str]]) -> str:
        """Try Together AI for open source models (free tier)"""
        try:
            import requests
            
            if not messages:
                return ""
            
            user_message = messages[-1]["content"]
            
            # Get knowledge context
            from components.rag_system import get_rag_system
            rag_system = get_rag_system()
            relevant_knowledge = rag_system.retrieve_relevant_knowledge(user_message, top_k=2)
            
            context = ""
            if relevant_knowledge:
                knowledge_text = ' '.join(relevant_knowledge)
                knowledge_words = knowledge_text.split()[:300]
                context = ' '.join(knowledge_words)
            
            # Build prompt for Together AI
            conversation_text = ""
            for msg in messages[-4:]:
                role = "Student" if msg["role"] == "user" else "Tutor"
                conversation_text += f"{role}: {msg['content']}\n"
            
            prompt = f"""You are a Socratic AI tutor for landscape ecology. Guide students with questions.

{f"Knowledge context: {context}" if context else ""}

Conversation:
{conversation_text}

Tutor:"""
            
            # Together AI API call
            response = requests.post(
                "https://api.together.xyz/v1/completions",
                headers={
                    "Authorization": "Bearer dummy_free_key",  # Together AI free tier
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/Llama-2-7b-chat-hf",
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 200,
                    "stop": ["Student:", "Tutor:"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["text"].strip()
                    if generated_text and len(generated_text) > 10:
                        return generated_text
            
            return ""
            
        except Exception as e:
            return ""
    
    def _try_huggingface_api(self, messages: List[Dict[str, str]]) -> str:
        """Try Hugging Face Inference API with open source models"""
        try:
            import requests
            
            # Get the user's latest message
            if not messages:
                return ""
            
            user_message = messages[-1]["content"]
            
            # Get relevant knowledge context
            from components.rag_system import get_rag_system
            rag_system = get_rag_system()
            relevant_knowledge = rag_system.retrieve_relevant_knowledge(user_message, top_k=2)
            
            # Create a comprehensive prompt for the open source model
            context = ""
            if relevant_knowledge:
                # Fix: relevant_knowledge is a list, join it first
                knowledge_text = ' '.join(relevant_knowledge)
                knowledge_words = knowledge_text.split()[:500]
                knowledge_sample = ' '.join(knowledge_words)
                context = f"\nRelevant landscape ecology knowledge:\n{knowledge_sample}"
            
            # Build conversation history
            conversation = ""
            for msg in messages[-4:]:  # Last 4 messages for context
                role = "Student" if msg["role"] == "user" else "Tutor"
                conversation += f"{role}: {msg['content']}\n"
            
            prompt = f"""You are a Socratic AI tutor for landscape ecology. Your role is to guide students through critical thinking using questions, not direct answers.

Key principles:
- Ask thought-provoking questions that build on the student's response
- Connect concepts to landscape ecology principles
- Handle typos and informal language gracefully
- Be encouraging and intellectually curious
- Use the provided knowledge context when relevant

{context}

Conversation:
{conversation}

Provide a thoughtful Socratic response that guides the student's learning. If they ask about a concept (like "transdisciplinarity"), ask questions that help them explore and understand it rather than explaining it directly."""

            # Try multiple Hugging Face models
            models_to_try = [
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "meta-llama/Llama-2-70b-chat-hf", 
                "microsoft/DialoGPT-large"
            ]
            
            for model in models_to_try:
                try:
                    response = self._call_huggingface_model(model, prompt)
                    if response and len(response) > 20:
                        return response
                except:
                    continue
                    
            return ""  # Return empty string instead of None
            
        except Exception as e:
            return ""
    
    def _call_huggingface_model(self, model: str, prompt: str) -> str:
        """Call specific Hugging Face model"""
        import requests
        
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        
        # Hugging Face provides free inference (rate limited)
        headers = {"Authorization": "Bearer hf_dummy"}  # Free tier doesn't need real token
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "").strip()
                if generated_text and len(generated_text) > 10:
                    return generated_text
        
        return ""  # Return empty string instead of None
    
    def _try_together_api(self, messages: List[Dict[str, str]]) -> str:
        """Try Together AI API for open source models"""
        # Use the new Together AI implementation
        return self._try_together_ai_api(messages)
    
    def _use_advanced_local_llm(self, messages: List[Dict[str, str]]) -> str:
        """Use advanced local processing with much better logic"""
        
        if not messages:
            return "What aspects of this article would you like to explore?"
        
        user_message = messages[-1]["content"].lower().strip()
        
        # Handle specific concept questions with intelligence
        concept_responses = {
            'transdisciplin': self._explain_transdisciplinarity,
            'interdisciplin': self._explain_interdisciplinarity, 
            'multiscale': self._explain_scale_concepts,
            'connectivity': self._explain_connectivity,
            'fragmentation': self._explain_fragmentation,
            'edge effect': self._explain_edge_effects,
            'metapopulation': self._explain_metapopulation,
            'disturbance': self._explain_disturbance,
            'succession': self._explain_succession,
            'landscape': self._explain_landscape_concepts,
            'pattern': self._explain_pattern_concepts,
            'heterogeneity': self._explain_heterogeneity,
            'scale': self._explain_scale_concepts
        }
        
        # Check if user is asking about a specific concept
        for concept, handler in concept_responses.items():
            if concept in user_message:
                return handler(user_message, len(messages))
        
        # Use the existing intelligent response system
        return self._generate_intelligent_response(messages)
    
    def _explain_transdisciplinarity(self, user_message: str, conversation_length: int) -> str:
        """Handle transdisciplinarity questions with Socratic approach"""
        responses = [
            "Transdisciplinarity is a fascinating concept! What do you think makes it different from simply having biologists and geographers work together?",
            "Great question about transdisciplinarity. Can you think of a landscape ecology problem that might require knowledge from fields beyond traditional ecology?",
            "Transdisciplinarity goes beyond just combining disciplines. What challenges do you think arise when ecologists need to work with urban planners or economists?",
            "That's an important concept. How might the way an ecologist thinks about a forest differ from how a sociologist or policy expert would approach the same forest?",
            "Excellent question! What do you think happens to our understanding of landscape problems when we include perspectives from local communities alongside scientific approaches?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_interdisciplinarity(self, user_message: str, conversation_length: int) -> str:
        """Handle interdisciplinarity questions"""
        responses = [
            "Interdisciplinarity brings together different fields of study. What disciplines do you think landscape ecology draws from?",
            "Good question about interdisciplinary approaches. How might an ecologist and a geographer look at the same landscape differently?",
            "That's key to landscape ecology! What advantages might there be to combining ecological knowledge with geographic information systems?",
            "Interdisciplinary work is essential in landscape ecology. Can you think of a specific landscape problem that would benefit from multiple scientific perspectives?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_connectivity(self, user_message: str, conversation_length: int) -> str:
        """Handle connectivity questions"""
        responses = [
            "Connectivity is crucial in landscape ecology! What do you think makes two habitat patches 'connected' from an animal's perspective?",
            "Great question about connectivity. How might connectivity for a bird differ from connectivity for a small mammal in the same landscape?",
            "Connectivity can be structural or functional. What factors do you think might make a landscape corridor effective for wildlife movement?",
            "That's a key concept. How do you think human activities might affect landscape connectivity?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_fragmentation(self, user_message: str, conversation_length: int) -> str:
        """Handle fragmentation questions"""  
        responses = [
            "Habitat fragmentation is a major concern in landscape ecology. What do you think happens to wildlife populations when large habitats are broken into smaller pieces?",
            "Good question about fragmentation. Can you think of human activities that might cause habitat fragmentation?",
            "Fragmentation has multiple effects. How might the 'edge' of a forest fragment be different from its interior?",
            "That's an important process to understand. What strategies might help reduce the negative effects of fragmentation?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_scale_concepts(self, user_message: str, conversation_length: int) -> str:
        """Handle scale-related questions"""
        responses = [
            "Scale is fundamental to landscape ecology! What patterns might you see at a landscape scale that wouldn't be visible at a local scale?",
            "Great question about scale. How do you think the processes that shape ecosystems might differ between local and regional scales?",
            "Scale affects everything in ecology. What challenges do you think researchers face when studying processes that operate at multiple scales?",
            "That's a key concept. How might management decisions need to consider multiple spatial scales?"
        ]
        
        import random  
        return random.choice(responses)
    
    def _explain_edge_effects(self, user_message: str, conversation_length: int) -> str:
        """Handle edge effects questions"""
        responses = [
            "Edge effects are fascinating! What differences would you expect to find between the edge and interior of a forest fragment?",
            "Good question about edge effects. How far into a habitat patch do you think edge influences might penetrate?",
            "Edge effects can be physical, biological, or both. What factors create these edge conditions?",
            "That's an important phenomenon. How might edge effects influence wildlife communities?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_metapopulation(self, user_message: str, conversation_length: int) -> str:
        """Handle metapopulation questions"""
        responses = [
            "Metapopulations are a key concept in landscape ecology! What do you think happens when local populations are connected by occasional migration?",
            "Good question about metapopulations. How might the 'rescue effect' help maintain populations in poor-quality habitats?",
            "Metapopulation dynamics involve extinction and recolonization. What landscape features might influence these processes?",
            "That's an important theory. Can you think of a real-world example where populations exist as a metapopulation?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_disturbance(self, user_message: str, conversation_length: int) -> str:
        """Handle disturbance questions"""
        responses = [
            "Disturbance is a fundamental force in landscapes! What different types of disturbances can you think of that affect ecosystems?",
            "Great question about disturbance. How might the size and frequency of disturbances influence landscape patterns?",
            "Disturbance regimes vary across landscapes. What role do you think disturbance plays in maintaining biodiversity?",
            "That's a key concept. How might climate change be altering natural disturbance regimes?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_succession(self, user_message: str, conversation_length: int) -> str:
        """Handle succession questions"""
        responses = [
            "Succession creates temporal changes in landscapes! What factors do you think influence how quickly succession proceeds after a disturbance?",
            "Good question about succession. How might the landscape context around a disturbed area affect the successional process?",
            "Successional stages create different habitat conditions. What advantages might there be to having landscapes with multiple successional stages?",
            "That's an important process. How do you think human activities might alter natural succession patterns?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_landscape_concepts(self, user_message: str, conversation_length: int) -> str:
        """Handle general landscape questions"""
        responses = [
            "Landscapes are complex mosaics of different habitats! What elements do you think make up the landscape you're studying?",
            "Great question about landscapes. How might the same landscape look different to different species?",
            "Landscape structure influences ecological processes. What patterns do you notice in the landscape described in your article?",
            "That's fundamental to landscape ecology. How do you think human activities have changed landscape patterns over time?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_pattern_concepts(self, user_message: str, conversation_length: int) -> str:
        """Handle pattern-related questions"""
        responses = [
            "Spatial patterns are key to understanding landscapes! What patterns do you observe in the study area?",
            "Good question about patterns. How might these patterns have formed over time?",
            "Patterns and processes are linked in landscape ecology. What processes might create the patterns you're observing?",
            "That's an important observation. How might different scales of observation reveal different patterns?"
        ]
        
        import random
        return random.choice(responses)
    
    def _explain_heterogeneity(self, user_message: str, conversation_length: int) -> str:
        """Handle heterogeneity questions"""
        responses = [
            "Heterogeneity is what makes landscapes interesting! What creates the spatial variation you see in this landscape?",
            "Great question about heterogeneity. How might this spatial variation benefit different species?",
            "Landscape heterogeneity can occur at multiple scales. What patterns of variation do you notice at different scales?",
            "That's a fundamental concept. How do you think heterogeneity influences ecological processes across the landscape?"
        ]
        
        import random
        return random.choice(responses)
    
    def _generate_llm_like_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate LLM-quality responses using advanced local processing"""
        
        if not messages:
            return "What aspects of this article would you like to explore?"
        
        user_message = messages[-1]["content"]
        conversation_length = len([m for m in messages if m["role"] == "user"])
        
        # Get comprehensive context from knowledge base
        from components.rag_system import get_rag_system
        rag_system = get_rag_system()
        relevant_knowledge = rag_system.retrieve_relevant_knowledge(user_message, top_k=5)
        
        # Advanced concept and intent analysis
        intent_analysis = self._analyze_student_intent(user_message, messages)
        concepts = self._extract_detailed_concepts(user_message)
        learning_level = self._assess_learning_level(messages)
        
        # Generate contextual response based on analysis
        response = self._craft_intelligent_response(
            user_message, 
            intent_analysis, 
            concepts, 
            relevant_knowledge, 
            learning_level,
            conversation_length
        )
        
        return response
    
    def _analyze_student_intent(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze what the student is actually trying to understand"""
        
        msg_lower = message.lower()
        intent = {
            'type': 'general',
            'confidence': 0.5,
            'specific_focus': None,
            'question_type': 'open'
        }
        
        # Identify question patterns
        if any(word in msg_lower for word in ['what is', 'define', 'explain', 'tell me about']):
            intent['type'] = 'definition_seeking'
            intent['confidence'] = 0.9
            intent['question_type'] = 'definition'
        
        elif any(word in msg_lower for word in ['how does', 'how do', 'how might', 'how would']):
            intent['type'] = 'mechanism_understanding'  
            intent['confidence'] = 0.8
            intent['question_type'] = 'process'
        
        elif any(word in msg_lower for word in ['why', 'what causes', 'what leads to']):
            intent['type'] = 'causal_understanding'
            intent['confidence'] = 0.8
            intent['question_type'] = 'causation'
        
        elif any(word in msg_lower for word in ['example', 'for instance', 'case study']):
            intent['type'] = 'example_seeking'
            intent['confidence'] = 0.7
            intent['question_type'] = 'application'
        
        elif '?' in message:
            intent['type'] = 'explicit_question'
            intent['confidence'] = 0.6
            intent['question_type'] = 'direct'
        
        # Extract specific focus area
        focus_areas = {
            'scale': ['scale', 'spatial', 'temporal', 'hierarchy'],
            'connectivity': ['connect', 'corridor', 'movement', 'dispersal', 'migration'],
            'fragmentation': ['fragment', 'patch', 'isolation', 'break up'],
            'disturbance': ['disturb', 'fire', 'flood', 'storm', 'logging'],
            'pattern': ['pattern', 'structure', 'arrange', 'configuration'],
            'process': ['process', 'mechanism', 'function', 'dynamic'],
            'management': ['manage', 'conservation', 'protect', 'restore'],
            'methods': ['method', 'measure', 'analyze', 'study', 'research']
        }
        
        for area, keywords in focus_areas.items():
            if any(keyword in msg_lower for keyword in keywords):
                intent['specific_focus'] = area
                break
                
        return intent
    
    def _extract_detailed_concepts(self, message: str) -> Dict[str, float]:
        """Extract and weight landscape ecology concepts in the message"""
        
        msg_lower = message.lower()
        concepts = {}
        
        # Comprehensive concept mapping with confidence scores
        concept_patterns = {
            'transdisciplinarity': {
                'patterns': ['transdisciplin', 'trans disciplin', 'interdisciplin', 'multidisciplin', 'cross disciplin'],
                'weight': 1.0
            },
            'scale_effects': {
                'patterns': ['scale', 'spatial', 'temporal', 'hierarchy', 'resolution', 'extent', 'grain'],
                'weight': 0.9
            },
            'connectivity': {
                'patterns': ['connect', 'corridor', 'movement', 'dispersal', 'migration', 'flow', 'network'],
                'weight': 0.9
            },
            'habitat_fragmentation': {
                'patterns': ['fragment', 'patch', 'isolation', 'break up', 'divide', 'separate'],
                'weight': 0.9
            },
            'edge_effects': {
                'patterns': ['edge', 'boundary', 'border', 'margin', 'interface', 'ecotone'],
                'weight': 0.8
            },
            'metapopulation': {
                'patterns': ['metapopulation', 'source', 'sink', 'colonization', 'extinction', 'recolonization'],
                'weight': 0.8
            },
            'disturbance_regime': {
                'patterns': ['disturbance', 'fire', 'flood', 'storm', 'logging', 'grazing', 'succession'],
                'weight': 0.8
            },
            'spatial_pattern': {
                'patterns': ['pattern', 'structure', 'arrangement', 'configuration', 'composition', 'heterogeneity'],
                'weight': 0.7
            },
            'landscape_process': {
                'patterns': ['process', 'mechanism', 'function', 'dynamic', 'interaction', 'relationship'],
                'weight': 0.7
            },
            'conservation_management': {
                'patterns': ['conservation', 'management', 'protection', 'restoration', 'planning', 'strategy'],
                'weight': 0.7
            }
        }
        
        for concept, data in concept_patterns.items():
            for pattern in data['patterns']:
                if pattern in msg_lower:
                    concepts[concept] = data['weight']
                    break
        
        return concepts
    
    def _assess_learning_level(self, conversation_history: List[Dict[str, str]]) -> str:
        """Assess the student's current learning level based on conversation"""
        
        if len(conversation_history) <= 2:
            return 'beginner'
        
        # Count sophisticated vocabulary and concepts mentioned
        sophisticated_terms = 0
        total_words = 0
        
        for msg in conversation_history:
            if msg['role'] == 'user':
                words = msg['content'].lower().split()
                total_words += len(words)
                
                # Check for advanced terminology
                advanced_terms = [
                    'metapopulation', 'heterogeneity', 'stochastic', 'spatial autocorrelation',
                    'landscape metrics', 'connectivity', 'fragmentation', 'edge effects',
                    'hierarchical', 'multiscale', 'ecosystem services', 'biodiversity'
                ]
                
                sophisticated_terms += sum(1 for term in advanced_terms if term in msg['content'].lower())
        
        if sophisticated_terms > 3 or len(conversation_history) > 10:
            return 'advanced'
        elif sophisticated_terms > 1 or len(conversation_history) > 5:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _craft_intelligent_response(self, user_message: str, intent: Dict[str, Any], 
                                  concepts: Dict[str, float], knowledge: List[str], 
                                  learning_level: str, conversation_length: int) -> str:
        """Craft an intelligent, contextual response like a real LLM would"""
        
        # Build response based on intent and concepts
        responses = []
        
        # Handle transdisciplinarity specifically (the example case)
        if 'transdisciplinarity' in concepts or any(term in user_message.lower() for term in ['transdisciplin', 'trans disciplin']):
            if intent['type'] == 'definition_seeking':
                if learning_level == 'beginner':
                    responses.extend([
                        "Transdisciplinarity is fascinating! It goes beyond just having different scientists work together. What do you think makes it different from regular teamwork between, say, an ecologist and a geographer?",
                        "Great question about transdisciplinary approaches! Think about a complex environmental problem - what perspectives beyond just science might be needed to really understand and solve it?",
                        "Transdisciplinarity brings together not just different academic fields, but also community knowledge and real-world experience. Can you think of a landscape issue where local community insights would be as important as scientific data?"
                    ])
                else:
                    responses.extend([
                        "Transdisciplinarity transcends disciplinary boundaries by integrating academic knowledge with stakeholder perspectives and local knowledge systems. How might this approach change the way we frame research questions in landscape ecology?",
                        "Excellent question! Transdisciplinary landscape ecology involves co-production of knowledge between researchers, practitioners, and communities. What methodological challenges do you think this creates for traditional scientific approaches?"
                    ])
        
        # Handle other concepts with similar depth
        if 'connectivity' in concepts:
            responses.extend([
                f"Connectivity is such a rich concept in landscape ecology! Are you thinking about structural connectivity (physical linkages) or functional connectivity (how organisms actually experience the landscape)?",
                f"Great question about connectivity. How might the scale of your analysis change what you consider to be 'connected'?",
                f"Landscape connectivity fascinates me because it's so species-specific. What do you think makes a landscape connected from the perspective of the organisms in your study?"
            ])
        
        if 'habitat_fragmentation' in concepts:
            responses.extend([
                f"Habitat fragmentation involves both habitat loss and habitat subdivision. Which aspect do you think has stronger effects on the species you're studying?",
                f"Fragmentation creates such complex patterns! Are you considering just the physical breaking up of habitat, or also the ecological consequences for species and communities?",
                f"That's a key process in landscape ecology. How might the 'matrix' between habitat patches influence fragmentation effects?"
            ])
        
        # Add knowledge-informed responses
        if knowledge:
            knowledge_text = ' '.join(knowledge)
            if 'yellowstone' in knowledge_text.lower():
                responses.append("This reminds me of classic landscape ecology studies like the Yellowstone wolf reintroduction. How might similar landscape-scale processes be operating in your system?")
            if 'corridor' in knowledge_text.lower():
                responses.append("The research on corridor effectiveness shows such interesting results. What evidence would convince you that a corridor is actually functional for your species of interest?")
        
        # Add level-appropriate follow-ups
        if learning_level == 'beginner':
            responses.extend([
                f"That's a really important concept to understand. What specific aspect of it connects most clearly to what you observed in the article?",
                f"I can see you're working through some complex ideas. What would help you feel more confident about applying this concept?"
            ])
        elif learning_level == 'advanced':
            responses.extend([
                f"You're engaging with sophisticated concepts here. How might this connect to current debates in landscape ecology theory?",
                f"That's an excellent analytical question. What alternative hypotheses might explain the patterns you're observing?"
            ])
        
        # Ensure we have good responses
        if not responses:
            responses.extend([
                f"That's a thoughtful question about landscape ecology. What specific aspect would help you understand the bigger picture of this study?",
                f"I can see you're thinking deeply about this. What connections are you making between this concept and the evidence presented in the article?",
                f"That's an important area to explore. How does this relate to the spatial and temporal scales discussed in your reading?"
            ])
        
        # Select best response based on context
        import random
        selected_response = random.choice(responses)
        
        # Add encouraging, natural language flow
        encouraging_starts = [
            "That's exactly the right kind of question to be asking! ",
            "I love how you're thinking about this - ",
            "You're really getting to the heart of the matter. ",
            "That's such an insightful direction to explore. ",
            ""  # Sometimes no prefix is better
        ]
        
        if random.random() < 0.3:  # 30% chance of encouraging start
            selected_response = random.choice(encouraging_starts) + selected_response
        
        return selected_response
    
    def _get_level_guidance(self, level_name: str) -> str:
        """Get specific guidance for each conversation level"""
        guidance = {
            "comprehension": """
            Focus on basic understanding:
            - Help them identify main ideas and key concepts
            - Ask about what they observed or read
            - Guide them to articulate the research question
            - Ensure they understand the study design
            """,
            "analysis": """
            Deepen their examination:
            - Ask why certain patterns exist
            - Guide them to examine cause-and-effect relationships
            - Help them analyze the methodology choices
            - Encourage interpretation of results
            """,
            "synthesis": """
            Connect to broader concepts:
            - Link findings to landscape ecology theory
            - Connect to previous course material
            - Ask about applications to other systems
            - Explore relationships between concepts
            """,
            "evaluation": """
            Encourage critical assessment:
            - Question assumptions and limitations
            - Explore alternative interpretations
            - Assess the strength of evidence
            - Consider broader implications and future research
            """
        }
        return guidance.get(level_name, "Guide student thinking through questions.")
    
    def detect_answer_seeking(self, user_message: str) -> bool:
        """Detect if student is trying to get direct answers"""
        answer_seeking_phrases = [
            "what is the answer",
            "tell me the answer",
            "what should i write",
            "give me the answer",
            "what is the correct",
            "can you tell me"
        ]
        return any(phrase in user_message.lower() for phrase in answer_seeking_phrases)
    
    def redirect_answer_seeking(self) -> str:
        """Provide response when student seeks direct answers"""
        redirections = [
            "I notice you're looking for a direct answer. Instead, let me ask you: what do you think based on what you've read?",
            "Rather than me telling you, what evidence from the article supports your thinking?",
            "That's a great question to explore! What's your initial thinking about this?",
            "Instead of giving you the answer, let's work through this together. What patterns do you notice?",
            "I'm here to guide your thinking, not provide answers. What connections are you making?"
        ]
        import random
        return random.choice(redirections)

def initialize_chat_session():
    """Initialize a new chat session"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if 'chat_start_time' not in st.session_state:
        st.session_state.chat_start_time = datetime.now()

def add_message(role: str, content: str):
    """Add a message to the chat history"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.chat_messages.append(message)

def get_chat_history():
    """Get the current chat history"""
    return st.session_state.get('chat_messages', [])

def calculate_session_duration():
    """Calculate how long the current session has been active"""
    if 'chat_start_time' in st.session_state:
        duration = datetime.now() - st.session_state.chat_start_time
        return duration.total_seconds() / 60  # Return minutes
    return 0
