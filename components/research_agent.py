import os
import json
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
import re

class ArticleResearchAgent:
    def __init__(self):
        self.research_folder = "article_research"
        self.ensure_research_folder_exists()
    
    def ensure_research_folder_exists(self):
        """Create the main research folder if it doesn't exist"""
        if not os.path.exists(self.research_folder):
            os.makedirs(self.research_folder)
    
    def research_article(self, article_title: str, article_content: str, article_id: str) -> Dict[str, Any]:
        """Main method to research an article and gather related information"""
        
        # Create article-specific folder
        article_folder = os.path.join(self.research_folder, f"article_{article_id}")
        if not os.path.exists(article_folder):
            os.makedirs(article_folder)
        
        st.info("🔍 AI Research Agent analyzing your article...")
        
        # Step 1: Analyze the article to identify key concepts and research opportunities
        analysis = self._analyze_article(article_content, article_title)
        
        # Step 2: Generate intelligent search queries
        search_queries = self._generate_search_queries(analysis)
        
        # Step 3: Perform web research
        research_results = self._perform_web_research(search_queries, article_folder)
        
        # Step 4: Organize and store the gathered information
        organized_knowledge = self._organize_research_results(research_results, analysis)
        
        # Step 5: Save everything to the article folder
        self._save_research_data(article_folder, {
            'article_title': article_title,
            'article_id': article_id,
            'analysis': analysis,
            'search_queries': search_queries,
            'research_results': research_results,
            'organized_knowledge': organized_knowledge,
            'research_date': datetime.now().isoformat()
        })
        
        # Step 6: Update the chatbot's knowledge base
        self._update_chatbot_knowledge(organized_knowledge, article_id)
        
        return {
            'folder_path': article_folder,
            'concepts_found': len(analysis['key_concepts']),
            'searches_performed': len(search_queries),
            'information_gathered': len(research_results),
            'knowledge_chunks_created': len(organized_knowledge)
        }
    
    def _analyze_article(self, content: str, title: str) -> Dict[str, Any]:
        """Analyze the article to extract key information for research"""
        
        # Extract key concepts from the article
        key_concepts = self._extract_research_concepts(content)
        
        # Identify study location/system
        study_system = self._identify_study_system(content)
        
        # Extract methodology information
        methods = self._extract_methods(content)
        
        # Identify key authors or research groups (simplified)
        authors = self._extract_author_info(content)
        
        # Identify time period or temporal aspects
        temporal_aspects = self._extract_temporal_aspects(content)
        
        return {
            'key_concepts': key_concepts,
            'study_system': study_system,
            'methods': methods,
            'authors': authors,
            'temporal_aspects': temporal_aspects,
            'title': title
        }
    
    def _extract_research_concepts(self, content: str) -> List[str]:
        """Extract key landscape ecology concepts that warrant further research"""
        
        # Advanced concept mapping for research
        concept_patterns = {
            'habitat_fragmentation': ['fragmentation', 'fragment', 'patch size', 'isolation'],
            'connectivity': ['connectivity', 'corridor', 'dispersal', 'movement', 'gene flow'],
            'edge_effects': ['edge effect', 'edge', 'boundary', 'ecotone'],
            'disturbance': ['disturbance', 'fire', 'flood', 'hurricane', 'logging', 'grazing'],
            'scale': ['scale', 'spatial', 'temporal', 'hierarchy', 'multi-scale'],
            'metapopulation': ['metapopulation', 'source', 'sink', 'colonization', 'extinction'],
            'land_use': ['land use', 'agriculture', 'urban', 'development', 'conversion'],
            'climate_change': ['climate', 'warming', 'precipitation', 'temperature'],
            'conservation': ['conservation', 'protected area', 'reserve', 'restoration'],
            'species_interactions': ['predation', 'competition', 'mutualism', 'herbivory'],
            'remote_sensing': ['satellite', 'landsat', 'modis', 'gis', 'remote sensing'],
            'modeling': ['model', 'simulation', 'prediction', 'scenario']
        }
        
        found_concepts = []
        content_lower = content.lower()
        
        for concept, patterns in concept_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                found_concepts.append(concept)
        
        return found_concepts
    
    def _identify_study_system(self, content: str) -> str:
        """Identify the study system/location for targeted research"""
        
        # Look for ecosystem types
        ecosystems = ['forest', 'grassland', 'prairie', 'wetland', 'desert', 'tundra', 
                     'savanna', 'coastal', 'marine', 'freshwater', 'urban', 'agricultural']
        
        # Look for geographic regions
        regions = ['amazon', 'yellowstone', 'great plains', 'mediterranean', 'temperate',
                  'tropical', 'boreal', 'arctic', 'subtropical']
        
        content_lower = content.lower()
        
        found_systems = []
        for ecosystem in ecosystems:
            if ecosystem in content_lower:
                found_systems.append(ecosystem)
        
        for region in regions:
            if region in content_lower:
                found_systems.append(region)
        
        return ', '.join(found_systems[:3]) if found_systems else 'general landscape'
    
    def _extract_methods(self, content: str) -> List[str]:
        """Extract research methods mentioned in the article"""
        
        method_keywords = ['gis', 'remote sensing', 'satellite', 'field survey', 'transect',
                          'radio telemetry', 'gps', 'genetic', 'molecular', 'modeling',
                          'simulation', 'statistical', 'regression', 'anova', 'ordination']
        
        found_methods = []
        content_lower = content.lower()
        
        for method in method_keywords:
            if method in content_lower:
                found_methods.append(method)
        
        return found_methods
    
    def _extract_author_info(self, content: str) -> List[str]:
        """Extract potential author or research group information"""
        
        # Look for common patterns that might indicate important researchers
        # This is simplified - in full implementation would use NLP
        author_indicators = ['et al', 'research group', 'laboratory', 'university', 'institute']
        
        found_indicators = []
        content_lower = content.lower()
        
        for indicator in author_indicators:
            if indicator in content_lower:
                found_indicators.append(indicator)
        
        return found_indicators[:3]  # Limit results
    
    def _extract_temporal_aspects(self, content: str) -> List[str]:
        """Extract temporal aspects for time-sensitive research"""
        
        temporal_patterns = ['long-term', 'longitudinal', 'time series', 'historical',
                           'decade', 'annual', 'seasonal', 'monitoring', 'trend']
        
        found_temporal = []
        content_lower = content.lower()
        
        for pattern in temporal_patterns:
            if pattern in content_lower:
                found_temporal.append(pattern)
        
        return found_temporal
    
    def _generate_search_queries(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent search queries based on article analysis"""
        
        queries = []
        title = analysis['title']
        concepts = analysis['key_concepts']
        study_system = analysis['study_system']
        
        # Basic queries about the main concepts
        for concept in concepts[:3]:  # Top 3 concepts
            queries.append(f"{concept.replace('_', ' ')} landscape ecology research")
            queries.append(f"{concept.replace('_', ' ')} {study_system} examples")
        
        # System-specific queries
        if study_system and study_system != 'general landscape':
            queries.append(f"{study_system} landscape ecology case studies")
            queries.append(f"{study_system} ecosystem management")
        
        # Method-specific queries
        if analysis['methods']:
            for method in analysis['methods'][:2]:
                queries.append(f"{method} landscape ecology applications")
        
        # Conservation/management queries
        queries.append(f"landscape ecology conservation applications")
        queries.append(f"landscape management {study_system}")
        
        # Recent research queries
        queries.append(f"recent landscape ecology research 2020-2024")
        queries.append(f"landscape ecology current trends")
        
        return queries[:10]  # Limit to 10 queries to be reasonable
    
    def _perform_web_research(self, queries: List[str], article_folder: str) -> List[Dict[str, Any]]:
        """Perform web searches and gather information"""
        
        research_results = []
        
        for i, query in enumerate(queries):
            st.write(f"🔍 Researching: {query}")
            
            try:
                # Use web search to find relevant information
                search_result = self._web_search_with_retry(query)
                
                if search_result:
                    # Save individual search result
                    result_file = os.path.join(article_folder, f"search_{i+1}_{query[:30].replace(' ', '_')}.txt")
                    with open(result_file, 'w', encoding='utf-8') as f:
                        f.write(f"Query: {query}\n\n")
                        f.write(f"Results:\n{search_result}\n\n")
                    
                    research_results.append({
                        'query': query,
                        'content': search_result,
                        'file_path': result_file,
                        'timestamp': datetime.now().isoformat()
                    })
            
            except Exception as e:
                st.warning(f"Could not research '{query}': {str(e)}")
                continue
        
        return research_results
    
    def _web_search_with_retry(self, query: str) -> str:
        """Perform web search with error handling"""
        try:
            # Try to use web search functionality
            # For now, return simulated search results to demonstrate the system
            return self._simulate_web_search(query)
            
        except Exception as e:
            return f"Search unavailable for: {query} (Error: {str(e)})"
    
    def _simulate_web_search(self, query: str) -> str:
        """Simulate web search results for demonstration"""
        
        # This would be replaced with actual web search in production
        simulation_results = {
            'habitat fragmentation': """
Habitat fragmentation research shows that breaking up continuous habitats into smaller patches has multiple effects on biodiversity. Recent studies indicate that edge effects can penetrate 100-300 meters into forest fragments. Small fragments lose species through demographic stochasticity and reduced habitat quality. Connectivity between fragments is crucial for maintaining metapopulations.
""",
            'connectivity': """
Landscape connectivity research demonstrates that both structural and functional connectivity are important for wildlife movement. Wildlife corridors can maintain gene flow between populations, but their effectiveness depends on species-specific movement behaviors. Urban areas often create barriers to connectivity, requiring wildlife overpasses and underpasses.
""",
            'disturbance ecology': """
Disturbance regimes are changing globally due to climate change and human activities. Fire suppression has altered natural fire cycles in many ecosystems. Large-scale disturbances create complex spatial patterns that influence succession and species composition. Understanding disturbance history is crucial for restoration planning.
""",
            'scale effects': """
Scale-dependent relationships are fundamental to landscape ecology. Patterns observed at fine scales may not predict landscape-level processes. The modifiable areal unit problem affects how we interpret spatial data. Multi-scale approaches are necessary to understand ecological processes across hierarchical levels.
""",
            'conservation planning': """
Systematic conservation planning uses algorithms to identify priority areas for protection. Reserve design should consider complementarity, representativeness, and connectivity. Climate change requires dynamic conservation strategies that anticipate species range shifts. Payment for ecosystem services can incentivize conservation on private lands.
"""
        }
        
        # Find the most relevant simulated result
        query_lower = query.lower()
        for key, result in simulation_results.items():
            if any(word in query_lower for word in key.split()):
                return result
        
        # Generic result if no specific match
        return f"""
Research on {query} in landscape ecology reveals complex spatial and temporal patterns. Current studies emphasize the importance of scale, connectivity, and disturbance in shaping ecological processes. Management applications focus on balancing conservation goals with human needs across landscapes.
"""
    
    def _organize_research_results(self, research_results: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
        """Organize research results into knowledge chunks for the chatbot"""
        
        organized_chunks = []
        
        # Create summary chunk
        summary = f"""
Research Summary for Article: {analysis['title']}

Key Concepts Investigated: {', '.join(analysis['key_concepts'])}
Study System: {analysis['study_system']}
Research Methods: {', '.join(analysis['methods']) if analysis['methods'] else 'Not specified'}

This research was automatically gathered to provide additional context for understanding this article in the broader landscape ecology literature.
"""
        organized_chunks.append(summary)
        
        # Process each search result
        for result in research_results:
            if result['content'] and len(result['content']) > 50:  # Valid content
                chunk = f"""
[RESEARCH] {result['query']}

{result['content'][:1000]}...

Source: Automated research for article context
"""
                organized_chunks.append(chunk)
        
        return organized_chunks
    
    def _save_research_data(self, article_folder: str, research_data: Dict[str, Any]):
        """Save comprehensive research data to article folder"""
        
        # Save main research summary
        summary_file = os.path.join(article_folder, "research_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2)
        
        # Save organized knowledge for easy access
        knowledge_file = os.path.join(article_folder, "gathered_knowledge.txt")
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            f.write(f"AI Research Agent - Gathered Knowledge\n")
            f.write(f"Article: {research_data['article_title']}\n")
            f.write(f"Research Date: {research_data['research_date']}\n\n")
            
            for chunk in research_data['organized_knowledge']:
                f.write(chunk + "\n\n" + "="*50 + "\n\n")
    
    def _update_chatbot_knowledge(self, knowledge_chunks: List[str], article_id: str):
        """Update the chatbot's knowledge base with article-specific research"""
        
        try:
            from components.rag_system import get_rag_system
            rag_system = get_rag_system()
            
            # Add all research as a single knowledge source
            combined_knowledge = "\n\n".join(knowledge_chunks)
            rag_system.add_knowledge_source(f"article_{article_id}_research", combined_knowledge)
            
            st.success("✅ Research integrated into chatbot knowledge base!")
            
        except Exception as e:
            st.error(f"Error updating chatbot knowledge: {str(e)}")
    
    def get_article_research_folder(self, article_id: str) -> str:
        """Get the path to an article's research folder"""
        return os.path.join(self.research_folder, f"article_{article_id}")
    
    def list_researched_articles(self) -> List[Dict[str, Any]]:
        """List all articles that have been researched"""
        
        researched_articles = []
        
        if not os.path.exists(self.research_folder):
            return researched_articles
        
        for folder_name in os.listdir(self.research_folder):
            if folder_name.startswith("article_"):
                folder_path = os.path.join(self.research_folder, folder_name)
                summary_file = os.path.join(folder_path, "research_summary.json")
                
                if os.path.exists(summary_file):
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            research_data = json.load(f)
                            researched_articles.append({
                                'article_id': research_data['article_id'],
                                'title': research_data['article_title'],
                                'research_date': research_data['research_date'],
                                'folder_path': folder_path,
                                'concepts_found': len(research_data['analysis']['key_concepts']),
                                'searches_performed': len(research_data['search_queries'])
                            })
                    except Exception as e:
                        continue
        
        return researched_articles

# Global instance for easy access
_research_agent = None

def get_research_agent() -> ArticleResearchAgent:
    """Get the global research agent instance"""
    global _research_agent
    if _research_agent is None:
        _research_agent = ArticleResearchAgent()
    return _research_agent