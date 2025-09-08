"""
Advanced Assignment Parser - Intelligent parsing of assignment documents
Extracts structured questions, requirements, and generates tutoring prompts
"""

import streamlit as st
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import PyPDF2
import io
import os
from docx import Document

class AssignmentParser:
    """Intelligent parsing of assignment documents to extract structured questions"""
    
    def __init__(self):
        self.bloom_keywords = {
            "remember": ["define", "list", "identify", "name", "state", "describe", "recall"],
            "understand": ["explain", "summarize", "interpret", "classify", "compare", "contrast"],
            "apply": ["use", "apply", "demonstrate", "solve", "implement", "execute"],
            "analyze": ["analyze", "examine", "investigate", "categorize", "differentiate", "distinguish"],
            "evaluate": ["evaluate", "assess", "critique", "judge", "justify", "defend"],
            "create": ["create", "design", "construct", "develop", "formulate", "synthesize"]
        }
        
        self.evidence_indicators = [
            "cite", "reference", "quote", "evidence", "support", "example", "data",
            "figure", "table", "study", "research", "findings", "results"
        ]
        
        self.question_patterns = [
            r'(?i)(?:question\s*\d+[\.:)]?\s*)(.*?)(?=\n\s*(?:question\s*\d+|$))',
            r'(?i)(?:\d+[\.:)]\s*)(.*?)(?=\n\s*\d+[\.:)]|$)',
            r'(?i)(?:^|\n)\s*([A-Z][^.!?]*\?)',
            r'(?i)(?:^|\n)\s*([^.!?]*(?:analyze|explain|describe|discuss|evaluate)[^.!?]*\.?)'
        ]
    
    def parse_assignment_document(self, file_content: bytes, filename: str, 
                                assignment_type: str = "socratic_analysis") -> Dict[str, Any]:
        """
        Parse uploaded assignment files into structured format
        
        Args:
            file_content: Raw file content as bytes
            filename: Name of the uploaded file
            assignment_type: Type of assignment (socratic_analysis, essay, etc.)
            
        Returns:
            Structured assignment data with parsed questions and metadata
        """
        try:
            # Extract text based on file type
            text_content = self._extract_text_from_file(file_content, filename)
            
            if not text_content.strip():
                return self._create_error_result("Could not extract text from file")
            
            # Parse the text content
            parsed_data = self._parse_text_content(text_content, assignment_type)
            
            # Add metadata
            parsed_data.update({
                'filename': filename,
                'file_type': self._get_file_extension(filename),
                'parsed_at': datetime.now().isoformat(),
                'total_questions': len(parsed_data.get('questions', [])),
                'assignment_type': assignment_type
            })
            
            return parsed_data
            
        except Exception as e:
            st.error(f"Error parsing assignment: {str(e)}")
            return self._create_error_result(f"Parsing error: {str(e)}")
    
    def _extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text content from various file formats"""
        file_extension = self._get_file_extension(filename).lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_content)
        elif file_extension == '.docx':
            return self._extract_from_docx(file_content)
        elif file_extension in ['.txt', '.md']:
            return file_content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            raise ValueError(f"Could not extract text from PDF: {str(e)}")
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise ValueError(f"Could not extract text from DOCX: {str(e)}")
    
    def _parse_text_content(self, text: str, assignment_type: str) -> Dict[str, Any]:
        """Parse extracted text into structured assignment data"""
        
        # Extract basic assignment information
        assignment_info = self._extract_assignment_metadata(text)
        
        # Extract questions using multiple patterns
        questions = self._extract_questions(text)
        
        # Process each question
        processed_questions = []
        for i, question_text in enumerate(questions, 1):
            question_data = self._analyze_question(question_text, f"Q{i}")
            processed_questions.append(question_data)
        
        # Generate workflow steps
        workflow_steps = self._generate_workflow_steps(processed_questions, assignment_type)
        
        return {
            'assignment_title': assignment_info.get('title', 'Parsed Assignment'),
            'assignment_type': assignment_type,
            'total_word_count': assignment_info.get('word_count', '600-900 words'),
            'learning_objectives': assignment_info.get('objectives', []),
            'questions': processed_questions,
            'workflow_steps': workflow_steps,
            'raw_text': text[:1000] + "..." if len(text) > 1000 else text  # Store excerpt
        }
    
    def _extract_assignment_metadata(self, text: str) -> Dict[str, Any]:
        """Extract assignment title, word count, and objectives from text"""
        metadata = {}
        
        # Look for title patterns
        title_patterns = [
            r'(?i)(?:assignment|homework|quiz|exam)[\s:]*([^\n]+)',
            r'(?i)^(.+?)(?:due|assignment|homework)',
            r'^([A-Z][^.\n]{10,50})(?:\n|$)'  # First capitalized line
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text[:500])  # Search in first 500 chars
            if match:
                metadata['title'] = match.group(1).strip()
                break
        
        # Look for word count requirements
        word_count_pattern = r'(?i)(\d+[-–]\d+)\s*words?|(\d+)\s*words?'
        word_match = re.search(word_count_pattern, text)
        if word_match:
            metadata['word_count'] = word_match.group(1) or f"{word_match.group(2)} words"
        
        # Extract learning objectives
        objectives_pattern = r'(?i)(?:objectives?|goals?|aims?)[\s:]*\n?(.+?)(?=\n\n|\n[A-Z]|\n\d+\.)'
        obj_match = re.search(objectives_pattern, text, re.DOTALL)
        if obj_match:
            objectives_text = obj_match.group(1)
            # Split on bullet points, numbers, or line breaks
            objectives = re.split(r'\n[-•*]\s*|\n\d+\.\s*|\n', objectives_text)
            metadata['objectives'] = [obj.strip() for obj in objectives if obj.strip()]
        
        return metadata
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from text using multiple patterns"""
        questions = []
        
        # Try each pattern and collect unique questions
        for pattern in self.question_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                question = match.strip() if isinstance(match, str) else match[0].strip()
                if len(question) > 20 and question not in questions:  # Avoid duplicates and too short
                    questions.append(question)
        
        # If no structured questions found, try to find question sentences
        if not questions:
            sentences = re.split(r'[.!]\s+', text)
            for sentence in sentences:
                if ('?' in sentence or 
                    any(word in sentence.lower() for word in ['analyze', 'explain', 'describe', 'discuss', 'evaluate', 'compare'])):
                    if len(sentence.strip()) > 20:
                        questions.append(sentence.strip())
        
        return questions[:10]  # Limit to 10 questions to avoid overwhelming
    
    def _analyze_question(self, question_text: str, question_id: str) -> Dict[str, Any]:
        """Analyze individual question and extract requirements"""
        
        # Classify by Bloom's taxonomy
        bloom_level = self._classify_bloom_level(question_text)
        
        # Extract evidence requirements
        evidence_required = self._extract_evidence_requirements(question_text)
        
        # Estimate word target based on complexity
        word_target = self._estimate_word_target(question_text, bloom_level)
        
        # Extract key concepts
        key_concepts = self._extract_key_concepts(question_text)
        
        # Generate tutoring prompts
        tutoring_prompts = self._generate_tutoring_prompts(question_text, bloom_level)
        
        return {
            'id': question_id,
            'title': self._generate_question_title(question_text),
            'prompt': question_text,
            'bloom_level': bloom_level,
            'required_evidence': evidence_required,
            'word_target': word_target,
            'key_concepts': key_concepts,
            'tutoring_prompts': tutoring_prompts,
            'learning_objectives': self._extract_learning_objectives_from_question(question_text)
        }
    
    def _classify_bloom_level(self, question_text: str) -> str:
        """Classify question by Bloom's taxonomy level"""
        question_lower = question_text.lower()
        
        # Score each level based on keyword presence
        scores = {}
        for level, keywords in self.bloom_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[level] = score
        
        if not scores:
            # Default classification based on question structure
            if '?' in question_text and ('what' in question_lower or 'who' in question_lower):
                return 'remember'
            elif any(word in question_lower for word in ['analyze', 'examine', 'investigate']):
                return 'analyze'
            elif any(word in question_lower for word in ['explain', 'describe', 'discuss']):
                return 'understand'
            else:
                return 'apply'
        
        # Return the highest scoring level
        return max(scores, key=scores.get)
    
    def _extract_evidence_requirements(self, question_text: str) -> str:
        """Extract what type of evidence the question requires"""
        question_lower = question_text.lower()
        evidence_types = []
        
        if any(word in question_lower for word in ['cite', 'reference', 'quote']):
            evidence_types.append("Direct citations from text")
        
        if any(word in question_lower for word in ['data', 'figure', 'table', 'statistics']):
            evidence_types.append("Quantitative data and figures")
        
        if any(word in question_lower for word in ['example', 'instance', 'case']):
            evidence_types.append("Specific examples")
        
        if any(word in question_lower for word in ['study', 'research', 'findings']):
            evidence_types.append("Research findings and studies")
        
        return "; ".join(evidence_types) if evidence_types else "Supporting evidence from the article"
    
    def _estimate_word_target(self, question_text: str, bloom_level: str) -> str:
        """Estimate appropriate word count for question response"""
        base_words = {
            'remember': 50,
            'understand': 100,
            'apply': 150,
            'analyze': 200,
            'evaluate': 250,
            'create': 300
        }
        
        base = base_words.get(bloom_level, 150)
        
        # Adjust based on question complexity
        if len(question_text) > 200:  # Complex question
            base += 50
        if 'compare' in question_text.lower():
            base += 75
        if 'multiple' in question_text.lower() or 'several' in question_text.lower():
            base += 50
        
        return f"{base-25}-{base+50} words"
    
    def _extract_key_concepts(self, question_text: str) -> List[str]:
        """Extract key concepts mentioned in the question"""
        # Common landscape ecology concepts
        concepts = [
            'fragmentation', 'connectivity', 'habitat', 'landscape', 'scale',
            'spatial', 'temporal', 'pattern', 'process', 'disturbance',
            'corridor', 'patch', 'matrix', 'edge effect', 'metapopulation'
        ]
        
        question_lower = question_text.lower()
        found_concepts = [concept for concept in concepts if concept in question_lower]
        
        # Also look for capitalized terms (likely to be technical concepts)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', question_text)
        found_concepts.extend([term for term in capitalized_terms if len(term) > 3])
        
        return list(set(found_concepts))[:5]  # Limit to 5 most relevant
    
    def _generate_tutoring_prompts(self, question_text: str, bloom_level: str) -> List[str]:
        """Generate specific tutoring prompts for guiding students through this question"""
        prompts = []
        
        # Base prompts by Bloom level
        if bloom_level == 'remember':
            prompts.extend([
                "What key terms or concepts does this question ask you to identify?",
                "Can you find the specific information in the article that directly answers this?",
                "What section of the article is most relevant to this question?"
            ])
        elif bloom_level == 'understand':
            prompts.extend([
                "How would you explain this concept in your own words?",
                "What examples from the article help illustrate this point?",
                "What's the main relationship or pattern being described?"
            ])
        elif bloom_level == 'analyze':
            prompts.extend([
                "What evidence supports the authors' conclusions about this?",
                "How do different parts of the data or argument connect?",
                "What patterns or relationships do you see in the information presented?"
            ])
        elif bloom_level == 'evaluate':
            prompts.extend([
                "What criteria should we use to judge the strength of this argument?",
                "What are the strengths and weaknesses of the approach described?",
                "How convincing do you find the evidence presented, and why?"
            ])
        
        # Add question-specific prompts
        if 'compare' in question_text.lower():
            prompts.append("What are the key similarities and differences you need to address?")
        
        if any(word in question_text.lower() for word in ['why', 'how', 'explain']):
            prompts.append("What causal relationships or mechanisms are involved here?")
        
        return prompts[:4]  # Limit to 4 most relevant prompts
    
    def _extract_learning_objectives_from_question(self, question_text: str) -> List[str]:
        """Extract implied learning objectives from question content"""
        objectives = []
        question_lower = question_text.lower()
        
        if any(word in question_lower for word in ['analyze', 'examine']):
            objectives.append("Develop analytical thinking skills")
        
        if any(word in question_lower for word in ['compare', 'contrast']):
            objectives.append("Practice comparative analysis")
        
        if any(word in question_lower for word in ['evaluate', 'assess']):
            objectives.append("Build critical evaluation skills")
        
        if any(word in question_lower for word in ['evidence', 'support']):
            objectives.append("Learn to identify and use supporting evidence")
        
        return objectives
    
    def _generate_question_title(self, question_text: str) -> str:
        """Generate a concise title for the question"""
        # Try to extract the main topic
        question_lower = question_text.lower()
        
        # Look for key concepts
        if 'fragmentation' in question_lower:
            return "Habitat Fragmentation Analysis"
        elif 'connectivity' in question_lower:
            return "Landscape Connectivity"
        elif 'scale' in question_lower:
            return "Scale Effects"
        elif 'disturbance' in question_lower:
            return "Disturbance Patterns"
        else:
            # Use first few meaningful words
            words = question_text.split()[:6]
            return " ".join(words).rstrip('.,!?:')
    
    def _generate_workflow_steps(self, questions: List[Dict], assignment_type: str) -> List[str]:
        """Generate workflow steps for completing the assignment"""
        steps = [
            "Read and annotate the assigned article carefully",
            "Identify key concepts and main arguments",
        ]
        
        if questions:
            steps.append(f"Work through each of the {len(questions)} questions systematically")
            steps.append("Gather specific evidence from the article for each question")
            steps.append("Develop analysis that goes beyond simple description")
        
        steps.extend([
            "Organize your responses to show connections between questions",
            "Review and refine your analysis for clarity and depth",
            "Ensure all responses meet the specified word count requirements"
        ])
        
        return steps
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1]
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            'error': True,
            'error_message': error_message,
            'assignment_title': 'Parse Error',
            'questions': [],
            'workflow_steps': [],
            'parsed_at': datetime.now().isoformat()
        }
    
    def validate_parsed_assignment(self, parsed_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that parsed assignment data is complete and usable"""
        issues = []
        
        if parsed_data.get('error'):
            return False, [parsed_data.get('error_message', 'Unknown error')]
        
        if not parsed_data.get('questions'):
            issues.append("No questions were found in the document")
        
        if len(parsed_data.get('questions', [])) < 2:
            issues.append("Assignment should contain at least 2 questions")
        
        for i, question in enumerate(parsed_data.get('questions', [])):
            if not question.get('prompt'):
                issues.append(f"Question {i+1} has no prompt text")
            if len(question.get('prompt', '')) < 10:
                issues.append(f"Question {i+1} prompt is too short")
        
        return len(issues) == 0, issues
    
    def generate_assignment_preview(self, parsed_data: Dict[str, Any]) -> str:
        """Generate a formatted preview of the parsed assignment"""
        if parsed_data.get('error'):
            return f"❌ **Error:** {parsed_data.get('error_message')}"
        
        preview = f"## {parsed_data.get('assignment_title', 'Untitled Assignment')}\n\n"
        preview += f"**Type:** {parsed_data.get('assignment_type', 'Unknown')}\n"
        preview += f"**Target Length:** {parsed_data.get('total_word_count', 'Not specified')}\n"
        preview += f"**Questions Found:** {len(parsed_data.get('questions', []))}\n\n"
        
        questions = parsed_data.get('questions', [])
        for question in questions:
            preview += f"### {question.get('id', 'Q')}: {question.get('title', 'Untitled')}\n"
            preview += f"**Bloom Level:** {question.get('bloom_level', 'Unknown').title()}\n"
            preview += f"**Word Target:** {question.get('word_target', 'Not specified')}\n"
            preview += f"**Question:** {question.get('prompt', 'No prompt')[:200]}...\n\n"
        
        return preview