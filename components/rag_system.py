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
        self.knowledge_sources = {}  # Track different knowledge sources
        self.load_knowledge_base()
        self.load_additional_sources()
    
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
    
    def load_additional_sources(self):
        """Load additional knowledge sources to make the chatbot more comprehensive"""
        
        # Add textbook-style content
        textbook_content = self._get_textbook_knowledge()
        if textbook_content:
            self.add_knowledge_source("textbook", textbook_content)
        
        # Add case studies
        case_studies = self._get_case_studies()
        if case_studies:
            self.add_knowledge_source("case_studies", case_studies)
        
        # Add research examples
        research_examples = self._get_research_examples()
        if research_examples:
            self.add_knowledge_source("research", research_examples)
        
        # Add real-world applications
        applications = self._get_real_world_applications()
        if applications:
            self.add_knowledge_source("applications", applications)
    
    def add_knowledge_source(self, source_name: str, content: str):
        """Add a new knowledge source with tracking"""
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        
        # Tag chunks with their source
        tagged_chunks = [f"[{source_name.upper()}] {chunk}" for chunk in chunks]
        
        self.knowledge_base.extend(tagged_chunks)
        self.knowledge_sources[source_name] = len(tagged_chunks)
        
        # Rebuild search index
        self._build_search_index()
    
    def update_embeddings(self):
        """Update embeddings for improved search (rebuilds index)"""
        self._build_search_index()
        return True
    
    def _get_textbook_knowledge(self) -> str:
        """Comprehensive textbook-style landscape ecology knowledge"""
        return """
Landscape Ecology Principles and Applications

Spatial Scale Relationships
The relationship between pattern and process varies with scale. At fine scales, local processes like competition and predation dominate. At broad scales, climate and disturbance regimes become more important. Scale-dependent relationships mean that conclusions drawn at one scale may not apply at another scale.

Habitat Selection and Resource Distribution
Animals select habitats based on resource availability, predation risk, and competition. The spatial distribution of resources creates a mosaic of habitat quality across landscapes. High-quality habitats (sources) can support breeding populations, while low-quality habitats (sinks) depend on immigration for persistence.

Movement Ecology and Dispersal
Animal movement patterns are influenced by landscape structure. Corridors facilitate movement, while barriers impede it. Movement behavior includes daily foraging movements, seasonal migrations, and natal dispersal. The scale of movement varies tremendously among species.

Population Dynamics in Fragmented Landscapes
Small, isolated populations face increased extinction risk due to demographic stochasticity, environmental stochasticity, and genetic drift. Metapopulation dynamics can rescue local populations through recolonization, but require sufficient connectivity between patches.

Community Assembly and Species Interactions
The assembly of ecological communities is influenced by local habitat conditions, regional species pools, and dispersal ability. Species interactions like competition, predation, and mutualism are modified by landscape structure and spatial context.

Disturbance Ecology and Succession
Disturbances create spatial and temporal heterogeneity in landscapes. The size, frequency, and intensity of disturbances influence succession trajectories. Intermediate disturbance can maintain higher diversity by preventing competitive exclusion.

Ecosystem Services and Landscape Function
Ecosystem services flow across landscapes and depend on spatial configuration. For example, pollination services depend on the proximity of natural habitats to agricultural areas. Water regulation services depend on watershed-scale patterns of land use.

Conservation Planning Principles
Effective conservation requires consideration of multiple spatial scales. Reserve networks should include large core areas, buffer zones, and connecting corridors. The complementarity principle suggests that reserves should be selected to maximize conservation of different species and habitats.

Human Impacts and Land Use Change
Human activities create novel landscape patterns and ecosystem types. Urbanization, agriculture, and resource extraction alter natural disturbance regimes and fragment habitats. Understanding these impacts is crucial for sustainable landscape management.

Restoration Ecology at Landscape Scales
Successful restoration requires understanding of reference conditions and restoration targets. Active restoration may be needed to overcome dispersal limitations and degraded site conditions. Restoration should consider landscape context and connectivity.
"""

    def _get_case_studies(self) -> str:
        """Real case studies from landscape ecology research"""
        return """
Case Study Examples in Landscape Ecology

Yellowstone Wolf Reintroduction
The reintroduction of wolves to Yellowstone National Park in 1995 demonstrates landscape-scale trophic cascades. Wolves reduced elk populations and changed their behavior, leading to reduced browsing pressure on willows and aspens. This allowed riparian vegetation to recover, which stabilized stream banks and improved habitat for other species.

Amazon Rainforest Fragmentation
Research in the Amazon has shown that forest fragmentation creates strong edge effects that penetrate 100-300 meters into forest fragments. Small fragments lose many species, especially large mammals and understory birds. Fragments isolated for decades show continued species loss and simplified community structure.

Prairie Restoration in Agricultural Landscapes  
Studies in Iowa show that prairie restoration can increase biodiversity and ecosystem services when strategically placed in agricultural landscapes. Linear prairie strips along contours reduce soil erosion and provide habitat corridors for wildlife. Restored prairies also support pollinators that benefit nearby crops.

Urban Wildlife Corridors
Green corridors in cities facilitate movement of wildlife between parks and natural areas. Studies of urban coyotes show they use riparian corridors to navigate through developed areas. Urban corridors also provide ecosystem services like air quality improvement and stormwater management.

Mountain Pine Beetle Outbreak
Large-scale pine beetle outbreaks in western North America demonstrate how disturbance agents operate at landscape scales. Climate change has enabled beetles to expand their range and increase outbreak frequency. The resulting tree mortality creates complex patterns of dead and living trees across landscapes.

Fire Management in Mediterranean Ecosystems
Fire suppression in Mediterranean ecosystems has led to fuel accumulation and increased risk of large, severe fires. Prescribed burning and fuel reduction treatments are being used to restore natural fire regimes. The spatial pattern of treatments influences fire behavior and ecosystem response.

Corridor Effectiveness for Large Carnivores
Studies of mountain lions in southern California show that wildlife corridors and underpasses can maintain connectivity for large carnivores in fragmented landscapes. GPS collar data reveals how animals use corridors and avoid human development. Genetic studies confirm that corridors maintain gene flow between populations.

Agricultural Landscape Biodiversity
Research in European agricultural landscapes demonstrates the importance of hedgerows, field margins, and small woodlots for maintaining biodiversity. These landscape elements provide habitat for beneficial insects, birds, and small mammals. Agri-environment schemes pay farmers to maintain these features.

Wetland Restoration and Water Quality
Wetland restoration in agricultural watersheds improves water quality by filtering nutrients and sediments. The effectiveness of wetland restoration depends on their position in the landscape and connectivity to water sources. Strategic placement of wetlands maximizes water quality benefits.

Climate Change and Species Range Shifts
Studies of species range shifts document how climate change is causing species to move poleward and upward in elevation. The rate of range shift varies among species and depends on dispersal ability and landscape barriers. Climate corridors may facilitate range shifts.
"""

    def _get_research_examples(self) -> str:
        """Research methodologies and examples"""
        return """
Research Methods in Landscape Ecology

Remote Sensing Applications
Satellite imagery and aerial photography are used to map land cover and track landscape changes over time. Landsat imagery provides 30-meter resolution data dating back to 1972. MODIS data provides daily coverage for monitoring seasonal changes and disturbances. LiDAR provides detailed information about vegetation structure and topography.

Geographic Information Systems (GIS)
GIS is used to analyze spatial patterns and relationships in landscapes. Common analyses include buffer analysis around habitat patches, overlay analysis of multiple map layers, and network analysis of habitat connectivity. Spatial statistics help identify patterns and test hypotheses about landscape structure.

Landscape Metrics and Pattern Analysis
Quantitative metrics describe landscape composition and configuration. Patch-based metrics include patch size, shape complexity, and isolation. Landscape-level metrics include diversity, evenness, and connectivity indices. Metrics must be interpreted carefully because they can be sensitive to data resolution and extent.

Animal Tracking and Movement Analysis
GPS collars and radio telemetry are used to track animal movements across landscapes. Movement data reveals habitat selection patterns, corridor use, and responses to landscape features. Step selection functions and resource selection functions quantify habitat preferences at different scales.

Genetic Analysis of Landscape Connectivity
Molecular markers reveal patterns of gene flow across landscapes. Landscape genetics combines genetic data with landscape maps to identify barriers and corridors to gene flow. Population genetic models estimate effective migration rates and identify landscape features that influence genetic structure.

Experimental Manipulations
Field experiments test hypotheses about landscape effects on ecological processes. Examples include creating experimental forest fragments of different sizes, manipulating corridor width and connectivity, and removing specific landscape features. Natural experiments take advantage of existing landscape patterns.

Modeling and Simulation
Computer models simulate ecological processes across landscapes. Spatially explicit population models project population viability under different landscape scenarios. Metapopulation models predict extinction and colonization dynamics. Landscape change models project future land use patterns.

Multi-scale Sampling Designs
Hierarchical sampling designs collect data at multiple spatial scales. Plots are nested within sites, which are nested within landscapes, which are nested within regions. This design allows partitioning of variation among scales and identification of scale-dependent relationships.

Long-term Monitoring Programs
Long-term studies track changes in landscape structure and ecological processes over decades. Examples include the Long Term Ecological Research (LTER) network and forest inventory plots. These studies reveal trends and cycles that are invisible at shorter time scales.

Comparative Landscape Studies
Comparing landscapes with different structures or histories provides insights into landscape effects. Examples include comparing fragmented versus continuous forests, landscapes with different disturbance histories, or regions with different land use practices. Space-for-time substitutions can reveal potential future changes.
"""

    def _get_real_world_applications(self) -> str:
        """Practical applications and management examples"""
        return """
Real-World Applications of Landscape Ecology

Conservation Corridor Planning
Wildlife corridors connect protected areas and allow animals to move between habitats. The Yellowstone to Yukon Conservation Initiative protects a corridor over 3,000 km long for grizzly bears and other wide-ranging species. Corridors are designed based on species movement patterns and landscape resistance maps.

Urban Green Infrastructure
Cities are incorporating landscape ecological principles into urban planning. Green roofs and walls reduce urban heat islands and provide habitat. Urban forest networks connect parks and natural areas. Rain gardens and constructed wetlands manage stormwater runoff.

Agricultural Landscape Management
Sustainable agriculture integrates production with conservation goals. Agroforestry systems combine crops with trees to provide multiple benefits. Cover crops reduce erosion and improve soil health. Integrated pest management uses landscape patterns to control agricultural pests.

Forest Management and Certification
Sustainable forest management considers landscape-scale patterns and processes. Forest certification programs like FSC require maintenance of wildlife corridors and protection of old-growth forests. Ecosystem-based management considers multiple species and ecosystem services.

Restoration Ecology Projects
Large-scale restoration projects restore ecosystem function across landscapes. The Comprehensive Everglades Restoration Plan aims to restore water flow patterns across south Florida. Prairie restoration programs focus on connecting isolated remnants with new plantings.

Climate Change Adaptation
Landscape planning helps ecosystems adapt to climate change. Climate corridors facilitate species migration to new suitable habitats. Assisted migration programs help species move to appropriate climates. Protected area networks are being expanded to include climate refugia.

Watershed Management
Watershed-scale management protects water quality and quantity. Riparian buffers filter pollutants and reduce erosion. Wetland restoration improves water quality and flood control. Forest management influences hydrological cycles and stream temperatures.

Fire Management Strategies
Landscape fire management reduces wildfire risk and maintains fire-adapted ecosystems. Prescribed burning creates mosaics of different-aged vegetation. Fuel reduction treatments create strategic firebreaks. Community wildfire protection plans integrate fire management with land use planning.

Invasive Species Management
Landscape approaches to invasive species management focus on preventing spread and protecting high-value areas. Early detection and rapid response programs monitor for new invasions. Biological control agents are released at landscape scales. Native species restoration competes with invasives.

Ecotourism and Recreation Planning
Sustainable recreation planning balances human use with ecosystem protection. Trail systems are designed to minimize impacts on sensitive species and habitats. Visitor education programs promote understanding of landscape ecological principles. Recreation impacts are monitored and managed adaptively.

Environmental Impact Assessment
Environmental impact assessments evaluate project effects on landscape-scale patterns and processes. Cumulative effects assessment considers multiple projects across landscapes. Mitigation hierarchies require avoiding, minimizing, and offsetting impacts. Strategic environmental assessments plan for landscape-scale development.

Payment for Ecosystem Services
Economic incentives reward landowners for providing ecosystem services. Carbon offset programs pay for forest conservation and restoration. Water quality trading programs compensate for watershed protection. Biodiversity offset programs require developers to protect equivalent habitats elsewhere.
"""

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
