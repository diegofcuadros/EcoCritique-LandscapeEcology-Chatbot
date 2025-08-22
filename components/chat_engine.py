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
            # Use Hugging Face's free inference API with Llama or similar open model
            response = self._call_huggingface_api(messages)
            return response
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I'm having trouble processing that. Could you try rephrasing your question?"
    
    def _call_huggingface_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Hugging Face Inference API with open source model"""
        
        # Format messages into a single prompt for the model
        prompt = self._format_messages_for_prompt(messages)
        
        # Use Microsoft's DialoGPT or similar open model
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        headers = {
            "Authorization": "Bearer hf_placeholder",  # No key needed for free inference
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 300,
                "temperature": 0.7,
                "do_sample": True
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "I need more information to help you.")
                else:
                    return "Let me think about that differently. What specific aspect interests you most?"
            else:
                # Fallback to local processing if API fails
                return self._generate_fallback_response(messages)
                
        except Exception as e:
            return self._generate_fallback_response(messages)
    
    def _format_messages_for_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages into a single prompt"""
        prompt = ""
        for msg in messages[-6:]:  # Use last 6 messages for context
            role = "Human" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant:"
        return prompt
    
    def _generate_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a fallback Socratic response when API fails"""
        fallback_responses = [
            "That's an interesting point. What evidence from the article supports that idea?",
            "Good observation! How do you think this connects to landscape ecology principles?",
            "What patterns are you noticing in the data or methodology?",
            "Can you explain your reasoning behind that conclusion?",
            "How might this finding apply to other landscape types or systems?",
            "What questions does this research raise for you?",
            "What do you think the implications of this study might be?",
            "How does this relate to what we've discussed about spatial patterns?",
            "What methodology choices do you think influenced these results?",
            "Can you identify any assumptions the researchers might be making?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
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
