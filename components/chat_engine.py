import streamlit as st
import json
from datetime import datetime
from typing import List, Dict, Any
import requests
import time

class SocraticChatEngine:
    def __init__(self):
        self.conversation_levels = {
            1: "comprehension",    # Basic understanding
            2: "analysis",         # Deeper examination  
            3: "synthesis",        # Integration with other concepts
            4: "evaluation"        # Critical assessment
        }
        self.load_prompts()
    
    def load_prompts(self):
        """Load Socratic questioning prompts from JSON file"""
        try:
            with open('data/socratic_prompts.json', 'r') as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
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
        """Generate a Socratic response that guides without giving answers"""
        
        current_level = self.get_conversation_level(conversation_history)
        level_name = self.conversation_levels[current_level]
        
        # Build the system prompt for Socratic questioning
        system_prompt = f"""
        You are a Socratic AI tutor for landscape ecology. Your role is to guide students through critical analysis of research articles using the Socratic method.

        CORE PRINCIPLES:
        1. NEVER provide direct answers to questions
        2. Always respond with questions that lead students to discover insights themselves
        3. Guide students through progressive levels of understanding
        4. Challenge assumptions and encourage critical thinking
        5. Connect findings to broader landscape ecology concepts

        CURRENT CONVERSATION LEVEL: {level_name}
        
        CONVERSATION CONTEXT:
        - Article being discussed: {article_context[:500]}...
        - Relevant landscape ecology concepts: {landscape_knowledge[:300]}...
        
        SOCRATIC GUIDELINES:
        - If student asks for an answer, redirect with "What do you think?" type questions
        - Build on their responses to deepen understanding
        - Use phrases like "What evidence supports that?" or "How might that connect to...?"
        - Encourage them to explain their reasoning
        - Point out contradictions gently through questions
        
        LEVEL-SPECIFIC FOCUS ({level_name}):
        {self._get_level_guidance(level_name)}
        
        Response should be 1-3 questions that guide the student deeper into the topic.
        Keep responses conversational and encouraging.
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
            st.error(f"Error generating response: {str(e)}")
            return "I'm having trouble processing that. Could you try rephrasing your question?"
    
    def _call_llm_api(self, messages: List[Dict[str, str]]) -> str:
        """Call open source LLM - try Llama2/Mistral via Hugging Face, then fallback to local system"""
        
        # For now, use enhanced local system (more reliable than HF free tier)
        # Future: Can add proper HF token or local model hosting
        return self._generate_smart_socratic_response(messages)
    
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
