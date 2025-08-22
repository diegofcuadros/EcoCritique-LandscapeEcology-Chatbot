import streamlit as st
import os
from typing import List, Dict
import sqlite3
import pickle
from datetime import datetime
import re

class LandscapeEcologyRAG:
    def __init__(self):
        self.knowledge_base = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load landscape ecology knowledge base"""
        try:
            # Load from text file
            with open('data/landscape_ecology_kb.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into chunks (paragraphs or sections)
            chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            self.knowledge_base = chunks
            
            # Initialize simple text search indices
            self._build_search_index()
                
        except FileNotFoundError:
            st.warning("Knowledge base file not found. Using minimal default knowledge.")
            self._create_default_knowledge()
    
    def _create_default_knowledge(self):
        """Create a minimal default knowledge base"""
        self.knowledge_base = [
            "Landscape ecology studies the relationship between spatial patterns and ecological processes across multiple scales.",
            "Habitat fragmentation refers to the breaking up of continuous habitats into smaller, isolated patches.",
            "Connectivity describes the degree to which landscapes facilitate or impede movement of organisms and ecological flows.",
            "Spatial heterogeneity is the uneven distribution of habitats, resources, or conditions across space.",
            "Edge effects are changes in population or community structures that occur at the boundary of habitat patches.",
            "Metapopulation theory describes populations of the same species connected by migration and dispersal.",
            "Landscape metrics are quantitative measures used to characterize landscape structure and composition.",
            "Scale dependency means that ecological patterns and processes vary depending on the spatial and temporal scale of observation.",
            "Patch dynamics refers to the mosaic of patches in different stages of succession across a landscape.",
            "Corridors are linear habitat features that connect otherwise fragmented habitats and facilitate movement."
        ]
        self._build_search_index()
    
    def _build_search_index(self):
        """Build simple keyword search index for the knowledge base"""
        self.search_index = {}
        for i, chunk in enumerate(self.knowledge_base):
            # Extract keywords from each chunk
            words = re.findall(r'\b\w+\b', chunk.lower())
            for word in words:
                if len(word) > 3:  # Only index words longer than 3 characters
                    if word not in self.search_index:
                        self.search_index[word] = []
                    if i not in self.search_index[word]:
                        self.search_index[word].append(i)
    
    def retrieve_relevant_knowledge(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve most relevant knowledge chunks for a query using keyword search"""
        if not self.knowledge_base:
            return []
        
        # Extract query keywords
        query_words = re.findall(r'\b\w+\b', query.lower())
        query_words = [word for word in query_words if len(word) > 3]
        
        if not query_words:
            return []
        
        # Score chunks based on keyword matches
        chunk_scores = {}
        for word in query_words:
            if word in self.search_index:
                for chunk_idx in self.search_index[word]:
                    if chunk_idx not in chunk_scores:
                        chunk_scores[chunk_idx] = 0
                    chunk_scores[chunk_idx] += 1
        
        # Get top-k chunks by score
        if not chunk_scores:
            return []
        
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        top_chunks = [self.knowledge_base[idx] for idx, score in sorted_chunks[:top_k] if score > 0]
        
        return top_chunks
    
    def add_to_knowledge_base(self, new_content: str):
        """Add new content to the knowledge base"""
        chunks = [chunk.strip() for chunk in new_content.split('\n\n') if chunk.strip()]
        
        if chunks:
            self.knowledge_base.extend(chunks)
            # Rebuild search index
            self._build_search_index()
    
    def search_knowledge(self, query: str) -> str:
        """Search knowledge base and return formatted results"""
        relevant_chunks = self.retrieve_relevant_knowledge(query, top_k=5)
        
        if not relevant_chunks:
            return "No directly relevant information found in the knowledge base."
        
        # Format the results
        formatted_result = "Relevant landscape ecology concepts:\n\n"
        for i, chunk in enumerate(relevant_chunks, 1):
            formatted_result += f"{i}. {chunk}\n\n"
        
        return formatted_result

class ArticleProcessor:
    def __init__(self):
        self.current_article = None
        self.article_summary = ""
        self.key_concepts = []
    
    def process_article_text(self, article_text: str, article_title: str = ""):
        """Process article text and extract key information"""
        self.current_article = {
            "title": article_title,
            "content": article_text,
            "processed_date": datetime.now().isoformat()
        }
        
        # Create a summary (first few paragraphs or abstract)
        paragraphs = article_text.split('\n\n')
        if len(paragraphs) > 0:
            # Try to find abstract or use first few paragraphs
            self.article_summary = ' '.join(paragraphs[:3])[:1000] + "..."
        
        # Extract potential key concepts (this is simplified)
        self.key_concepts = self._extract_key_concepts(article_text)
        
        # Store in session state
        st.session_state.current_article = self.current_article
        st.session_state.article_summary = self.article_summary
        st.session_state.key_concepts = self.key_concepts
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key landscape ecology concepts from article text"""
        # Common landscape ecology terms
        key_terms = [
            "landscape", "habitat", "fragmentation", "connectivity", "corridor",
            "patch", "matrix", "edge effect", "scale", "spatial pattern",
            "heterogeneity", "disturbance", "succession", "metapopulation",
            "dispersal", "migration", "biodiversity", "conservation",
            "land use", "land cover", "remote sensing", "GIS"
        ]
        
        found_concepts = []
        text_lower = text.lower()
        
        for term in key_terms:
            if term in text_lower:
                found_concepts.append(term)
        
        return found_concepts[:10]  # Limit to top 10
    
    def get_article_context(self) -> str:
        """Get formatted article context for the chatbot"""
        if not self.current_article:
            return "No article currently loaded."
        
        context = f"Article Title: {self.current_article['title']}\n\n"
        context += f"Summary: {self.article_summary}\n\n"
        
        if self.key_concepts:
            context += f"Key Concepts: {', '.join(self.key_concepts)}"
        
        return context

# Initialize global instances
@st.cache_resource
def get_rag_system():
    """Get or create RAG system instance"""
    return LandscapeEcologyRAG()

@st.cache_resource
def get_article_processor():
    """Get or create article processor instance"""
    return ArticleProcessor()
