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
        self.key_bullet_points = []
        self.key_terminology = {}
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
    
    def process_article_text(self, text: str, title: str) -> bool:
        """
        Process article text directly (for when text is already extracted).
        
        Args:
            text: Extracted text from article
            title: Article title
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Estimate page count from text length (rough approximation)
            estimated_pages = max(1, len(text) // 3000)  # ~3000 chars per page
            
            return self._process_text_content(text, title, estimated_pages)
            
        except Exception as e:
            st.error(f"Error processing article text: {str(e)}")
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
            
            # Generate 10 key bullet points
            self.key_bullet_points = self._generate_bullet_points(self.processed_text)
            
            # Extract key terminology and definitions
            self.key_terminology = self._extract_terminology(self.processed_text)
            
            # Store in session state for access by other components
            st.session_state.current_article = self.current_article
            st.session_state.article_summary = self.article_summary
            st.session_state.key_concepts = self.key_concepts
            st.session_state.learning_objectives = self.learning_objectives
            st.session_state.key_bullet_points = self.key_bullet_points
            st.session_state.key_terminology = self.key_terminology
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
        self.key_bullet_points = []
        self.key_terminology = {}
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
    
    def _generate_bullet_points(self, text: str) -> List[str]:
        """
        Generate 10 key bullet points summarizing the article content.
        
        Args:
            text: Article text
            
        Returns:
            List[str]: List of key bullet points
        """
        bullet_points = []
        text_lower = text.lower()
        
        # Look for explicit results, findings, or conclusions
        key_sections = []
        section_keywords = ['result', 'finding', 'conclusion', 'discussion', 'implication']
        
        for keyword in section_keywords:
            if keyword in text_lower:
                start_pos = text_lower.find(keyword)
                # Extract a good chunk around the keyword
                start = max(0, start_pos - 100)
                end = min(len(text), start_pos + 500)
                section_text = text[start:end]
                key_sections.append(section_text)
        
        # Extract sentences that contain important information
        if key_sections:
            combined_text = ' '.join(key_sections)
        else:
            # Use full text if no specific sections found
            combined_text = text[:3000]  # First 3000 characters
        
        sentences = combined_text.split('.')
        important_sentences = []
        
        # Look for sentences with important indicators
        importance_indicators = [
            'significant', 'important', 'key', 'main', 'primary', 'major',
            'found', 'showed', 'demonstrated', 'revealed', 'indicated',
            'suggest', 'conclude', 'result', 'effect', 'impact',
            'connectivity', 'fragmentation', 'habitat', 'landscape', 'spatial',
            'species', 'ecosystem', 'conservation', 'management'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 200:  # Reasonable length
                score = sum(1 for indicator in importance_indicators 
                          if indicator in sentence.lower())
                if score >= 2:  # At least 2 important terms
                    important_sentences.append((sentence, score))
        
        # Sort by importance score and take top sentences
        important_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to bullet points
        for sentence, score in important_sentences[:10]:
            # Clean up the sentence
            clean_sentence = sentence.strip()
            if not clean_sentence.endswith('.'):
                clean_sentence += '.'
            bullet_points.append(clean_sentence)
        
        # Fill with generic points if not enough found
        while len(bullet_points) < 10:
            if len(bullet_points) == 0:
                bullet_points.append("This article presents landscape ecology research findings.")
            elif len(bullet_points) == 1:
                bullet_points.append("The study examines spatial patterns and ecological processes.")
            elif len(bullet_points) == 2:
                bullet_points.append("Methods include spatial analysis and field data collection.")
            elif len(bullet_points) == 3:
                bullet_points.append("Results show relationships between landscape structure and function.")
            elif len(bullet_points) == 4:
                bullet_points.append("The research has implications for conservation and management.")
            elif len(bullet_points) == 5:
                bullet_points.append("Habitat connectivity plays a key role in the findings.")
            elif len(bullet_points) == 6:
                bullet_points.append("Scale effects are important for understanding the results.")
            elif len(bullet_points) == 7:
                bullet_points.append("The study contributes to landscape ecology theory.")
            elif len(bullet_points) == 8:
                bullet_points.append("Spatial heterogeneity influences ecological patterns.")
            else:
                bullet_points.append("Further research directions are suggested by the authors.")
        
        return bullet_points[:10]
    
    def _extract_terminology(self, text: str) -> Dict[str, str]:
        """
        Extract key terminology and provide definitions for landscape ecology terms.
        
        Args:
            text: Article text
            
        Returns:
            Dict[str, str]: Dictionary of terms and their definitions
        """
        terminology = {}
        text_lower = text.lower()
        
        # Comprehensive landscape ecology terminology with definitions
        landscape_terms = {
            'connectivity': 'The degree to which landscape elements facilitate or impede movement of organisms, materials, or energy between patches.',
            'fragmentation': 'The breaking up of continuous habitat into smaller, isolated patches, often due to human activities.',
            'edge effects': 'Changes in environmental conditions and species composition at the boundaries between different habitats or landscape elements.',
            'patch': 'A discrete area of habitat that differs from its surroundings, forming the basic unit of landscape structure.',
            'corridor': 'Linear landscape elements that connect otherwise isolated habitat patches, facilitating movement of organisms.',
            'matrix': 'The dominant landscape element that surrounds and connects patches, often influencing connectivity and edge effects.',
            'heterogeneity': 'The spatial variation in landscape structure, composition, or function across an area.',
            'metapopulation': 'A group of local populations connected by migration, where local extinctions can be recolonized from other patches.',
            'scale': 'The spatial or temporal dimension of measurement, including both extent (total area) and resolution (grain size).',
            'grain': 'The finest level of spatial resolution in a study, determining the smallest unit that can be distinguished.',
            'extent': 'The overall area encompassed by a study or the largest scale at which patterns are measured.',
            'disturbance': 'Any discrete event that disrupts ecosystem structure or function, creating spatial and temporal heterogeneity.',
            'habitat': 'The environment where an organism lives and meets its life requirements, including food, shelter, and breeding sites.',
            'landscape metrics': 'Quantitative indices that describe the spatial characteristics of landscapes, such as patch size and connectivity.',
            'spatial analysis': 'The examination of spatial patterns and relationships using geographic information systems and statistical methods.',
            'remote sensing': 'The acquisition of information about landscape features from satellite or aerial imagery.',
            'gis': 'Geographic Information Systems used for capturing, storing, analyzing, and displaying spatial data.',
            'buffer zone': 'An area surrounding a habitat patch or feature that provides additional protection or gradual transition.',
            'ecotone': 'A transition area between two different ecosystems or habitat types, often with unique species composition.',
            'landscape pattern': 'The spatial arrangement of landscape elements, including the size, shape, and distribution of patches.'
        }
        
        # Check which terms appear in the text and add them to terminology
        for term, definition in landscape_terms.items():
            # Check for the term and common variations
            variations = [term, term.replace('_', ' '), term.replace(' ', '')]
            
            for variation in variations:
                if variation in text_lower:
                    terminology[term.replace('_', ' ').title()] = definition
                    break
        
        # If fewer than 5 terms found, add the most common landscape ecology terms
        if len(terminology) < 5:
            essential_terms = ['connectivity', 'fragmentation', 'habitat', 'scale', 'heterogeneity', 
                             'patch', 'landscape pattern', 'edge effects', 'spatial analysis']
            for term in essential_terms:
                if len(terminology) >= 8:  # Limit to reasonable number
                    break
                if term.replace('_', ' ').title() not in terminology:
                    terminology[term.replace('_', ' ').title()] = landscape_terms[term]
        
        return terminology
    
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
    
    def get_article_context(self) -> str:
        """
        Get comprehensive article context including full text excerpts for AI analysis.
        Provides more detailed information than get_article_context_for_ai().
        
        Returns:
            str: Detailed article context with text excerpts
        """
        if not self.current_article:
            return "No article currently loaded for discussion."
        
        context = f"Article: {self.current_article['title']}\n\n"
        
        # Add article summary and key information
        if self.article_summary:
            context += f"Summary: {self.article_summary}\n\n"
        
        # Add key concepts
        if self.key_concepts:
            context += f"Key Concepts: {', '.join(self.key_concepts)}\n\n"
        
        # Add substantial text excerpts from the article for context
        if hasattr(self, 'processed_text') and self.processed_text:
            # Extract meaningful sections of text (first 2000 characters as sample)
            text_sample = self.processed_text[:2000] if len(self.processed_text) > 2000 else self.processed_text
            context += f"Article Content (excerpt):\n{text_sample}\n\n"
        
        # Add learning objectives if available
        if self.learning_objectives:
            context += f"Learning Focus: {'; '.join(self.learning_objectives)}"
        
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
