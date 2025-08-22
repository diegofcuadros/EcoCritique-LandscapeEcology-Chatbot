import streamlit as st
import PyPDF2
import io
import os
from datetime import datetime
from typing import List, Dict, Optional
import re

class ArticleProcessor:
    """
    Handles processing and management of academic articles for the Socratic chatbot.
    This class provides functionality to extract text from PDFs, identify key concepts,
    and prepare article content for AI-guided discussions.
    """
    
    def __init__(self):
        self.current_article = None
        self.article_summary = ""
        self.key_concepts = []
        self.learning_objectives = []
        self.processed_text = ""
    
    def process_uploaded_file(self, uploaded_file, article_title: str = "") -> bool:
        """
        Process an uploaded PDF file and extract relevant information.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            article_title: Optional title for the article
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Reset previous state
            self._reset_state()
            
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            
            if len(pdf_reader.pages) == 0:
                st.error("The uploaded PDF appears to be empty.")
                return False
            
            # Extract text from all pages
            full_text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            if not full_text.strip():
                st.error("Could not extract readable text from the PDF. Please ensure the PDF contains selectable text.")
                return False
            
            # Process the extracted text
            return self._process_text_content(full_text, article_title, len(pdf_reader.pages))
            
        except Exception as e:
            st.error(f"Error processing PDF file: {str(e)}")
            return False
    
    def process_article_from_file(self, file_path: str, article_title: str = "") -> bool:
        """
        Process an article from a file path.
        
        Args:
            file_path: Path to the PDF file
            article_title: Optional title for the article
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                st.error(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                full_text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                if not full_text.strip():
                    st.error("Could not extract readable text from the PDF.")
                    return False
                
                # Process the extracted text
                return self._process_text_content(full_text, article_title, len(pdf_reader.pages))
                
        except Exception as e:
            st.error(f"Error processing file {file_path}: {str(e)}")
            return False
    
    def _process_text_content(self, text: str, title: str, page_count: int) -> bool:
        """
        Process extracted text content and identify key components.
        
        Args:
            text: Raw text extracted from PDF
            title: Article title
            page_count: Number of pages in the PDF
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Clean and normalize text
            self.processed_text = self._clean_text(text)
            
            # Extract title if not provided
            if not title.strip():
                title = self._extract_title_from_text(self.processed_text)
            
            # Create article metadata
            self.current_article = {
                "title": title,
                "content": self.processed_text,
                "page_count": page_count,
                "processed_date": datetime.now().isoformat(),
                "word_count": len(self.processed_text.split())
            }
            
            # Generate summary (abstract or first few paragraphs)
            self.article_summary = self._extract_summary(self.processed_text)
            
            # Extract key landscape ecology concepts
            self.key_concepts = self._extract_key_concepts(self.processed_text)
            
            # Extract or generate learning objectives
            self.learning_objectives = self._extract_learning_objectives(self.processed_text)
            
            # Store in session state for access by other components
            st.session_state.current_article = self.current_article
            st.session_state.article_summary = self.article_summary
            st.session_state.key_concepts = self.key_concepts
            st.session_state.learning_objectives = self.learning_objectives
            st.session_state.processed_text = self.processed_text
            
            return True
            
        except Exception as e:
            st.error(f"Error processing text content: {str(e)}")
            return False
    
    def _reset_state(self):
        """Reset the processor state for new article."""
        self.current_article = None
        self.article_summary = ""
        self.key_concepts = []
        self.learning_objectives = []
        self.processed_text = ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that might be page numbers or headers
            if len(line) < 3:
                continue
            # Skip lines that are just numbers (page numbers)
            if line.isdigit():
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_title_from_text(self, text: str) -> str:
        """
        Attempt to extract article title from text.
        
        Args:
            text: Article text
            
        Returns:
            str: Extracted or default title
        """
        lines = text.split('\n')
        
        # Look for title in first few lines
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            # Title is often the first substantial line
            if len(line) > 20 and len(line) < 200:
                # Check if it looks like a title (not starting with common article words)
                if not line.lower().startswith(('abstract', 'introduction', 'keywords', 'author')):
                    return line
        
        return "Untitled Article"
    
    def _extract_summary(self, text: str) -> str:
        """
        Extract article summary/abstract.
        
        Args:
            text: Article text
            
        Returns:
            str: Article summary
        """
        # Look for abstract section
        text_lower = text.lower()
        abstract_start = text_lower.find('abstract')
        
        if abstract_start != -1:
            # Find the end of abstract (next section or paragraph break)
            abstract_text = text[abstract_start:]
            
            # Look for common section headers that might follow abstract
            end_markers = ['introduction', 'keywords', 'background', '1.', 'methods']
            end_pos = len(abstract_text)
            
            for marker in end_markers:
                marker_pos = abstract_text.lower().find(marker, 100)  # Skip first 100 chars
                if marker_pos != -1:
                    end_pos = min(end_pos, marker_pos)
            
            abstract = abstract_text[:end_pos].replace('abstract', '', 1).strip()
            if len(abstract) > 50:
                return abstract[:1000] + "..." if len(abstract) > 1000 else abstract
        
        # If no abstract found, use first few paragraphs
        paragraphs = text.split('\n\n')
        summary_paragraphs = []
        char_count = 0
        
        for para in paragraphs:
            para = para.strip()
            if para and char_count < 800:
                summary_paragraphs.append(para)
                char_count += len(para)
            elif char_count >= 800:
                break
        
        return ' '.join(summary_paragraphs) + "..."
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """
        Extract key landscape ecology concepts from article text.
        
        Args:
            text: Article text
            
        Returns:
            List[str]: List of key concepts found
        """
        # Comprehensive list of landscape ecology terms
        landscape_terms = {
            'landscape ecology': 'landscape ecology',
            'habitat fragmentation': 'habitat fragmentation',
            'connectivity': 'connectivity',
            'corridor': 'corridor',
            'patch dynamics': 'patch dynamics',
            'edge effect': 'edge effect',
            'spatial pattern': 'spatial pattern',
            'spatial scale': 'spatial scale',
            'heterogeneity': 'spatial heterogeneity',
            'metapopulation': 'metapopulation',
            'dispersal': 'dispersal',
            'migration': 'migration',
            'landscape matrix': 'landscape matrix',
            'habitat patch': 'habitat patch',
            'landscape metric': 'landscape metrics',
            'disturbance': 'disturbance regime',
            'succession': 'ecological succession',
            'biodiversity': 'biodiversity',
            'conservation': 'conservation biology',
            'land use': 'land use change',
            'land cover': 'land cover',
            'remote sensing': 'remote sensing',
            'gis': 'GIS',
            'fragmentation': 'fragmentation',
            'percolation': 'percolation theory',
            'graph theory': 'graph theory',
            'network analysis': 'network analysis',
            'functional connectivity': 'functional connectivity',
            'structural connectivity': 'structural connectivity',
            'source-sink': 'source-sink dynamics',
            'stepping stone': 'stepping stone',
            'landscape genetics': 'landscape genetics',
            'gene flow': 'gene flow',
            'population viability': 'population viability',
            'minimum viable population': 'minimum viable population',
            'critical threshold': 'critical threshold',
            'percolation threshold': 'percolation threshold'
        }
        
        found_concepts = []
        text_lower = text.lower()
        
        for term, concept_name in landscape_terms.items():
            if term in text_lower:
                if concept_name not in found_concepts:
                    found_concepts.append(concept_name)
        
        # Also look for some methodology terms common in landscape ecology
        method_terms = {
            'patch size': 'patch size analysis',
            'edge density': 'edge density',
            'core area': 'core area',
            'nearest neighbor': 'nearest neighbor distance',
            'contagion': 'contagion index',
            'shannon diversity': 'Shannon diversity',
            'landscape diversity': 'landscape diversity',
            'fragmentation index': 'fragmentation index'
        }
        
        for term, concept_name in method_terms.items():
            if term in text_lower:
                if concept_name not in found_concepts:
                    found_concepts.append(concept_name)
        
        return found_concepts[:15]  # Limit to most relevant concepts
    
    def _extract_learning_objectives(self, text: str) -> List[str]:
        """
        Extract or generate learning objectives from article content.
        
        Args:
            text: Article text
            
        Returns:
            List[str]: List of learning objectives
        """
        objectives = []
        
        # Look for explicit objectives in the text
        text_lower = text.lower()
        obj_keywords = ['objective', 'aim', 'goal', 'purpose']
        
        for keyword in obj_keywords:
            keyword_pos = text_lower.find(keyword)
            if keyword_pos != -1:
                # Extract surrounding context
                start = max(0, keyword_pos - 50)
                end = min(len(text), keyword_pos + 200)
                context = text[start:end]
                
                # Simple extraction of sentence containing objective
                sentences = context.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 20:
                        objectives.append(sentence.strip())
                        break
        
        # If no explicit objectives found, generate based on content and concepts
        if not objectives:
            if self.key_concepts:
                objectives.append(f"Understand the application of {', '.join(self.key_concepts[:3])} in landscape ecology research")
            
            # Check for methodology focus
            if any(term in text_lower for term in ['method', 'analysis', 'model']):
                objectives.append("Analyze the methodology and approaches used in landscape ecology research")
            
            # Check for conservation focus
            if any(term in text_lower for term in ['conservation', 'management', 'restoration']):
                objectives.append("Evaluate conservation and management implications of landscape patterns")
            
            # Check for spatial analysis focus
            if any(term in text_lower for term in ['spatial', 'gis', 'remote sensing', 'mapping']):
                objectives.append("Examine spatial analysis techniques and their applications in landscape studies")
        
        return objectives[:5]  # Limit to 5 objectives
    
    def get_article_context_for_ai(self) -> str:
        """
        Get formatted article context for AI chatbot.
        
        Returns:
            str: Formatted context string
        """
        if not self.current_article:
            return "No article currently loaded for discussion."
        
        context = f"Article Title: {self.current_article['title']}\n\n"
        
        if self.article_summary:
            context += f"Article Summary: {self.article_summary}\n\n"
        
        if self.key_concepts:
            context += f"Key Landscape Ecology Concepts: {', '.join(self.key_concepts)}\n\n"
        
        if self.learning_objectives:
            context += f"Learning Objectives: {'; '.join(self.learning_objectives)}\n\n"
        
        context += f"Article Length: {self.current_article.get('word_count', 0)} words, {self.current_article.get('page_count', 0)} pages"
        
        return context
    
    def get_article_metadata(self) -> Dict:
        """
        Get article metadata for display or storage.
        
        Returns:
            Dict: Article metadata
        """
        if not self.current_article:
            return {}
        
        return {
            'title': self.current_article['title'],
            'summary': self.article_summary,
            'key_concepts': self.key_concepts,
            'learning_objectives': self.learning_objectives,
            'word_count': self.current_article.get('word_count', 0),
            'page_count': self.current_article.get('page_count', 0),
            'processed_date': self.current_article.get('processed_date', '')
        }
    
    def search_article_content(self, query: str) -> str:
        """
        Search for specific content within the current article.
        
        Args:
            query: Search query
            
        Returns:
            str: Relevant excerpts from the article
        """
        if not self.processed_text:
            return "No article content available for search."
        
        query_lower = query.lower()
        text_lower = self.processed_text.lower()
        
        # Find sentences containing the query terms
        sentences = self.processed_text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(term.strip() in sentence.lower() for term in query_lower.split() if len(term.strip()) > 2):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Return up to 3 most relevant sentences
            return '. '.join(relevant_sentences[:3]) + '.'
        else:
            return f"No specific content found for '{query}' in the current article."
    
    def validate_article_quality(self) -> Dict[str, Any]:
        """
        Validate the quality and suitability of the processed article.
        
        Returns:
            Dict: Validation results with scores and recommendations
        """
        if not self.current_article:
            return {"valid": False, "message": "No article loaded"}
        
        validation = {
            "valid": True,
            "score": 0,
            "max_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check word count
        word_count = self.current_article.get('word_count', 0)
        if word_count < 500:
            validation["issues"].append("Article appears too short for meaningful discussion")
            validation["score"] += 10
        elif word_count < 2000:
            validation["issues"].append("Article is quite short - consider supplementary materials")
            validation["score"] += 20
        else:
            validation["score"] += 25
        
        # Check for key concepts
        if len(self.key_concepts) < 3:
            validation["issues"].append("Few landscape ecology concepts detected")
            validation["recommendations"].append("Ensure article focuses on landscape ecology topics")
            validation["score"] += 15
        else:
            validation["score"] += 25
        
        # Check for summary/abstract
        if len(self.article_summary) < 100:
            validation["issues"].append("No clear abstract or summary found")
            validation["recommendations"].append("Articles with clear abstracts work better for discussion")
            validation["score"] += 20
        else:
            validation["score"] += 25
        
        # Check for learning objectives
        if len(self.learning_objectives) == 0:
            validation["issues"].append("No clear learning objectives identified")
            validation["recommendations"].append("Consider adding explicit learning objectives")
            validation["score"] += 15
        else:
            validation["score"] += 25
        
        # Overall assessment
        if validation["score"] < 60:
            validation["valid"] = False
            validation["message"] = "Article may not be suitable for Socratic discussion"
        elif validation["score"] < 80:
            validation["message"] = "Article is suitable but could be improved"
        else:
            validation["message"] = "Article is well-suited for Socratic discussion"
        
        return validation

# Global function to get cached article processor instance
@st.cache_resource
def get_article_processor():
    """Get or create article processor instance."""
    return ArticleProcessor()
