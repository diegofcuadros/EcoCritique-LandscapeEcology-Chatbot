"""
Enhanced Knowledge System for EcoCritique
Advanced semantic search and literature integration for landscape ecology education
"""

import json
import sqlite3
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math
from components.educational_summary_system import EducationalSummarySystem
from components.literature_synthesis_tools import LiteratureSynthesisTools
from components.real_time_database_integration import RealTimeAcademicDatabase

class EnhancedKnowledgeSystem:
    """
    Advanced knowledge retrieval system with semantic understanding,
    literature integration, and context-aware relevance matching.
    """
    
    def __init__(self, database_path: str = "ecocritique.db"):
        self.database_path = database_path
        self.initialize_database()
        
        # Initialize Phase 5B components
        self.educational_summary_system = EducationalSummarySystem(database_path)
        self.literature_synthesis_tools = LiteratureSynthesisTools()
        
        # Initialize Phase 5E components
        self.real_time_database = RealTimeAcademicDatabase(database_path)
        
        # Enhanced knowledge sources with metadata
        self.knowledge_sources = {
            'core_concepts': {
                'description': 'Fundamental landscape ecology concepts and definitions',
                'reliability': 'high',
                'academic_level': 'undergraduate'
            },
            'research_literature': {
                'description': 'Peer-reviewed scientific papers and findings',
                'reliability': 'very_high',
                'academic_level': 'graduate'
            },
            'case_studies': {
                'description': 'Real-world applications and examples',
                'reliability': 'high',
                'academic_level': 'undergraduate'
            },
            'methodological': {
                'description': 'Research methods and analytical techniques',
                'reliability': 'high',
                'academic_level': 'graduate'
            }
        }
        
        # Semantic concept relationships for landscape ecology
        self.concept_relationships = {
            'fragmentation': {
                'synonyms': ['habitat fragmentation', 'landscape fragmentation', 'patch isolation'],
                'related_concepts': ['connectivity', 'edge effects', 'patch size', 'isolation'],
                'broader_concepts': ['landscape structure', 'spatial patterns'],
                'narrower_concepts': ['forest fragmentation', 'urban fragmentation'],
                'opposite_concepts': ['connectivity', 'landscape continuity']
            },
            'connectivity': {
                'synonyms': ['landscape connectivity', 'habitat connectivity', 'ecological connectivity'],
                'related_concepts': ['corridors', 'stepping stones', 'permeability', 'dispersal'],
                'broader_concepts': ['landscape function', 'spatial patterns'],
                'narrower_concepts': ['functional connectivity', 'structural connectivity'],
                'opposite_concepts': ['fragmentation', 'isolation']
            },
            'edge_effects': {
                'synonyms': ['edge influence', 'ecotone effects', 'boundary effects'],
                'related_concepts': ['fragment size', 'shape complexity', 'microclimate'],
                'broader_concepts': ['landscape dynamics', 'spatial heterogeneity'],
                'narrower_concepts': ['forest edge effects', 'urban edge effects'],
                'opposite_concepts': ['core habitat', 'interior conditions']
            },
            'metapopulation': {
                'synonyms': ['metapopulation dynamics', 'population network'],
                'related_concepts': ['migration', 'colonization', 'extinction', 'dispersal'],
                'broader_concepts': ['population ecology', 'landscape ecology'],
                'narrower_concepts': ['source-sink dynamics', 'patch occupancy'],
                'opposite_concepts': ['single population', 'isolated population']
            },
            'scale': {
                'synonyms': ['spatial scale', 'temporal scale', 'scale dependency'],
                'related_concepts': ['hierarchy', 'resolution', 'extent', 'grain'],
                'broader_concepts': ['landscape ecology principles'],
                'narrower_concepts': ['local scale', 'regional scale', 'global scale'],
                'opposite_concepts': ['scale independence']
            }
        }
        
        # Initialize with comprehensive landscape ecology knowledge
        self.load_enhanced_knowledge_base()
    
    def initialize_database(self):
        """Initialize enhanced database tables for knowledge management"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Enhanced knowledge entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    entry_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    concept_tags TEXT,
                    source_type TEXT,
                    academic_level TEXT,
                    reliability_score REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 0.5
                )
            ''')
            
            # Literature sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS literature_sources (
                    source_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT,
                    journal TEXT,
                    year INTEGER,
                    doi TEXT,
                    url TEXT,
                    abstract TEXT,
                    key_findings TEXT,
                    concept_relevance TEXT,
                    citation_count INTEGER DEFAULT 0,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Knowledge relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept_a TEXT,
                    concept_b TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Knowledge retrieval analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_analytics (
                    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    retrieved_entries TEXT,
                    student_id TEXT,
                    assignment_context TEXT,
                    relevance_scores TEXT,
                    student_feedback INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing enhanced knowledge database: {e}")
    
    def load_enhanced_knowledge_base(self):
        """Load comprehensive landscape ecology knowledge base"""
        
        # Core landscape ecology knowledge with enhanced metadata
        core_knowledge = [
            {
                "content": "Landscape ecology is an interdisciplinary field that focuses on the relationship between spatial patterns and ecological processes across multiple scales, from local patches to entire regions.",
                "concept_tags": ["landscape ecology", "spatial patterns", "ecological processes", "scale"],
                "source_type": "core_concepts",
                "academic_level": "undergraduate",
                "reliability_score": 0.95,
                "key_points": ["interdisciplinary", "spatial-process relationships", "multiple scales"]
            },
            {
                "content": "Habitat fragmentation occurs when large, continuous habitats are broken up into smaller, isolated patches, typically due to human activities like agriculture, urbanization, and road construction.",
                "concept_tags": ["fragmentation", "habitat loss", "human impacts", "urbanization"],
                "source_type": "core_concepts", 
                "academic_level": "undergraduate",
                "reliability_score": 0.95,
                "key_points": ["habitat breaking", "isolation", "human causes", "land use change"]
            },
            {
                "content": "Landscape connectivity refers to the degree to which landscapes facilitate or impede the movement of organisms, genes, and ecological processes between habitat patches.",
                "concept_tags": ["connectivity", "movement", "dispersal", "gene flow"],
                "source_type": "core_concepts",
                "academic_level": "undergraduate", 
                "reliability_score": 0.95,
                "key_points": ["movement facilitation", "genetic exchange", "process flow"]
            },
            {
                "content": "Edge effects are changes in biological and physical conditions that occur at patch boundaries and within adjacent patch interiors, typically extending 50-200 meters into forest fragments.",
                "concept_tags": ["edge effects", "microclimate", "boundary conditions", "fragment size"],
                "source_type": "research_literature",
                "academic_level": "undergraduate",
                "reliability_score": 0.9,
                "key_points": ["boundary changes", "physical conditions", "penetration distance"]
            },
            {
                "content": "Metapopulation theory describes a population structure consisting of multiple local populations connected by migration, where local extinctions are balanced by recolonization events.",
                "concept_tags": ["metapopulation", "migration", "extinction", "colonization"],
                "source_type": "core_concepts",
                "academic_level": "graduate",
                "reliability_score": 0.95,
                "key_points": ["population network", "extinction-colonization balance", "migration links"]
            },
            {
                "content": "Corridors are linear habitat features that connect otherwise fragmented habitats, facilitating movement and gene flow between populations while potentially serving as habitat themselves.",
                "concept_tags": ["corridors", "connectivity", "gene flow", "habitat linkage"],
                "source_type": "core_concepts",
                "academic_level": "undergraduate",
                "reliability_score": 0.9,
                "key_points": ["linear features", "connection function", "dual purpose"]
            },
            {
                "content": "Scale dependency in landscape ecology means that ecological patterns and processes vary depending on the spatial and temporal scale of observation, requiring multi-scale approaches for understanding.",
                "concept_tags": ["scale", "spatial scale", "temporal scale", "hierarchy"],
                "source_type": "core_concepts",
                "academic_level": "graduate",
                "reliability_score": 0.95,
                "key_points": ["scale variation", "observation dependency", "multi-scale analysis"]
            },
            {
                "content": "Landscape metrics are quantitative measures used to characterize landscape structure and composition, including patch size distribution, shape complexity, and connectivity indices.",
                "concept_tags": ["landscape metrics", "quantification", "spatial analysis", "indices"],
                "source_type": "methodological",
                "academic_level": "graduate",
                "reliability_score": 0.9,
                "key_points": ["quantitative measures", "structure characterization", "analytical tools"]
            }
        ]
        
        # Research literature with citations and findings
        research_literature = [
            {
                "content": "Haddad et al. (2015) conducted a global analysis showing that habitat fragmentation reduces biodiversity by 13-75% and impairs key ecosystem functions across terrestrial ecosystems worldwide.",
                "concept_tags": ["fragmentation", "biodiversity loss", "ecosystem function", "global patterns"],
                "source_type": "research_literature",
                "academic_level": "graduate",
                "reliability_score": 0.98,
                "citation": "Haddad, N.M. et al. (2015). Habitat fragmentation and its lasting impact on Earth's ecosystems. Science Advances, 1(2), e1500052.",
                "key_findings": ["13-75% biodiversity reduction", "global ecosystem impacts", "function impairment"],
                "journal": "Science Advances",
                "year": 2015
            },
            {
                "content": "Fahrig (2003) distinguished between habitat loss and habitat fragmentation effects, showing that habitat loss has consistently negative effects while fragmentation per se can have positive, negative, or neutral effects.",
                "concept_tags": ["habitat loss", "fragmentation", "ecological effects", "theory"],
                "source_type": "research_literature",
                "academic_level": "graduate",
                "reliability_score": 0.95,
                "citation": "Fahrig, L. (2003). Effects of habitat fragmentation on biodiversity. Annual Review of Ecology, Evolution, and Systematics, 34(1), 487-515.",
                "key_findings": ["habitat loss vs fragmentation", "variable fragmentation effects", "theoretical framework"],
                "journal": "Annual Review of Ecology, Evolution, and Systematics",
                "year": 2003
            },
            {
                "content": "Taylor et al. (1993) defined landscape connectivity as both structural (physical arrangement of habitat) and functional (behavioral response of organisms to landscape structure).",
                "concept_tags": ["connectivity", "structural connectivity", "functional connectivity", "definition"],
                "source_type": "research_literature",
                "academic_level": "graduate",
                "reliability_score": 0.95,
                "citation": "Taylor, P.D. et al. (1993). Connectivity is a vital element of landscape structure. Oikos, 68(3), 571-573.",
                "key_findings": ["dual connectivity types", "organism behavior importance", "landscape structure"],
                "journal": "Oikos",
                "year": 1993
            }
        ]
        
        # Case studies with real-world examples
        case_studies = [
            {
                "content": "The Yellowstone to Yukon Conservation Initiative demonstrates large-scale corridor implementation, connecting protected areas across 3,200 km to maintain wildlife movement and genetic diversity.",
                "concept_tags": ["corridors", "conservation", "wildlife movement", "case study"],
                "source_type": "case_studies",
                "academic_level": "undergraduate",
                "reliability_score": 0.85,
                "location": "North America",
                "key_outcomes": ["3,200 km connection", "wildlife movement", "genetic diversity maintenance"]
            },
            {
                "content": "Urban forest fragmentation in São Paulo, Brazil, shows how rapid urbanization creates small, isolated forest patches with high edge-to-interior ratios and altered species composition.",
                "concept_tags": ["urban fragmentation", "forest patches", "edge effects", "species composition"],
                "source_type": "case_studies", 
                "academic_level": "undergraduate",
                "reliability_score": 0.8,
                "location": "São Paulo, Brazil",
                "key_outcomes": ["urban forest isolation", "high edge ratios", "species changes"]
            }
        ]
        
        # Store all knowledge in database
        self._store_knowledge_entries(core_knowledge + research_literature + case_studies)
        
        # Build semantic search capabilities
        self._build_semantic_index()
    
    def _store_knowledge_entries(self, knowledge_entries: List[Dict]):
        """Store knowledge entries in database with metadata"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for entry in knowledge_entries:
                entry_id = hashlib.md5(entry['content'].encode()).hexdigest()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_entries 
                    (entry_id, content, concept_tags, source_type, academic_level, reliability_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    entry['content'],
                    json.dumps(entry['concept_tags']),
                    entry['source_type'],
                    entry['academic_level'],
                    entry['reliability_score']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing knowledge entries: {e}")
    
    def _build_semantic_index(self):
        """Build enhanced semantic search index"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get all knowledge entries
            cursor.execute('SELECT entry_id, content, concept_tags FROM knowledge_entries')
            entries = cursor.fetchall()
            
            # Build concept-to-entry mapping
            self.concept_index = defaultdict(list)
            self.content_index = {}
            
            for entry_id, content, concept_tags_json in entries:
                concept_tags = json.loads(concept_tags_json) if concept_tags_json else []
                
                # Store content
                self.content_index[entry_id] = content
                
                # Index by concepts
                for concept in concept_tags:
                    self.concept_index[concept.lower()].append(entry_id)
                    
                    # Add semantic relationships
                    if concept.lower() in self.concept_relationships:
                        relationships = self.concept_relationships[concept.lower()]
                        
                        # Add synonyms
                        for synonym in relationships.get('synonyms', []):
                            self.concept_index[synonym.lower()].append(entry_id)
                        
                        # Add related concepts with lower weight
                        for related in relationships.get('related_concepts', []):
                            self.concept_index[related.lower()].append(entry_id)
            
            conn.close()
            
        except Exception as e:
            print(f"Error building semantic index: {e}")
    
    def semantic_search(self, query: str, context: Dict = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search with context awareness and relevance ranking.
        
        Args:
            query: Search query from student or assignment
            context: Assignment context, current question, student profile
            top_k: Number of results to return
            
        Returns:
            List of ranked knowledge entries with metadata
        """
        
        # Extract concepts from query
        query_concepts = self._extract_concepts_from_query(query.lower())
        
        # Get candidate entries
        candidate_entries = self._get_candidate_entries(query_concepts)
        
        # Score and rank entries
        scored_entries = self._score_and_rank_entries(candidate_entries, query, query_concepts, context)
        
        # Return top results with metadata
        return scored_entries[:top_k]
    
    def _extract_concepts_from_query(self, query: str) -> List[str]:
        """Extract landscape ecology concepts from query text"""
        
        concepts_found = []
        
        # Direct concept matching
        for concept in self.concept_relationships.keys():
            if concept in query:
                concepts_found.append(concept)
        
        # Synonym matching
        for concept, relationships in self.concept_relationships.items():
            for synonym in relationships.get('synonyms', []):
                if synonym.lower() in query:
                    concepts_found.append(concept)
        
        # Keyword extraction for broader matching
        important_terms = [
            'habitat', 'species', 'ecosystem', 'conservation', 'biodiversity',
            'population', 'community', 'landscape', 'spatial', 'temporal',
            'pattern', 'process', 'structure', 'function', 'dynamics'
        ]
        
        for term in important_terms:
            if term in query:
                concepts_found.append(term)
        
        return list(set(concepts_found))  # Remove duplicates
    
    def _get_candidate_entries(self, query_concepts: List[str]) -> Dict[str, float]:
        """Get candidate entries based on concept matching"""
        
        entry_scores = defaultdict(float)
        
        for concept in query_concepts:
            if concept in self.concept_index:
                for entry_id in self.concept_index[concept]:
                    # Base score for exact concept match
                    entry_scores[entry_id] += 1.0
                    
                    # Bonus for concept relationships
                    if concept in self.concept_relationships:
                        relationships = self.concept_relationships[concept]
                        
                        # Check if entry contains related concepts
                        entry_content = self.content_index.get(entry_id, '').lower()
                        
                        for related in relationships.get('related_concepts', []):
                            if related in entry_content:
                                entry_scores[entry_id] += 0.3
                        
                        for broader in relationships.get('broader_concepts', []):
                            if broader in entry_content:
                                entry_scores[entry_id] += 0.2
        
        return dict(entry_scores)
    
    def _score_and_rank_entries(self, candidate_entries: Dict[str, float], 
                               query: str, query_concepts: List[str], 
                               context: Dict = None) -> List[Dict[str, Any]]:
        """Score and rank entries based on relevance and context"""
        
        scored_results = []
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for entry_id, base_score in candidate_entries.items():
                # Get entry details
                cursor.execute('''
                    SELECT content, concept_tags, source_type, academic_level, 
                           reliability_score, effectiveness_score, access_count
                    FROM knowledge_entries WHERE entry_id = ?
                ''', (entry_id,))
                
                result = cursor.fetchone()
                if not result:
                    continue
                
                content, concept_tags_json, source_type, academic_level, reliability_score, effectiveness_score, access_count = result
                concept_tags = json.loads(concept_tags_json) if concept_tags_json else []
                
                # Calculate comprehensive relevance score
                relevance_score = self._calculate_relevance_score(
                    content, concept_tags, base_score, query, query_concepts, context
                )
                
                # Apply quality and reliability factors
                quality_score = reliability_score * 0.4 + effectiveness_score * 0.3 + min(1.0, access_count / 10) * 0.3
                
                # Final combined score
                final_score = relevance_score * 0.7 + quality_score * 0.3
                
                scored_results.append({
                    'entry_id': entry_id,
                    'content': content,
                    'concept_tags': concept_tags,
                    'source_type': source_type,
                    'academic_level': academic_level,
                    'reliability_score': reliability_score,
                    'relevance_score': relevance_score,
                    'final_score': final_score,
                    'explanation': self._generate_relevance_explanation(content, query_concepts, context)
                })
            
            conn.close()
            
            # Sort by final score (descending)
            scored_results.sort(key=lambda x: x['final_score'], reverse=True)
            
        except Exception as e:
            print(f"Error scoring entries: {e}")
        
        return scored_results
    
    def _calculate_relevance_score(self, content: str, concept_tags: List[str], 
                                  base_score: float, query: str, 
                                  query_concepts: List[str], context: Dict = None) -> float:
        """Calculate detailed relevance score for an entry"""
        
        relevance = base_score
        content_lower = content.lower()
        
        # Concept coverage score
        concept_matches = sum(1 for concept in query_concepts if concept in content_lower)
        if query_concepts:
            concept_coverage = concept_matches / len(query_concepts)
            relevance += concept_coverage * 0.5
        
        # Query term matching
        query_terms = query.lower().split()
        term_matches = sum(1 for term in query_terms if term in content_lower and len(term) > 3)
        if query_terms:
            term_coverage = term_matches / len(query_terms)
            relevance += term_coverage * 0.3
        
        # Context relevance
        if context:
            # Assignment context matching
            if context.get('current_question'):
                question_text = context['current_question'].get('prompt', '').lower()
                question_concepts = self._extract_concepts_from_query(question_text)
                question_matches = sum(1 for concept in question_concepts if concept in content_lower)
                if question_concepts:
                    context_relevance = question_matches / len(question_concepts)
                    relevance += context_relevance * 0.4
            
            # Academic level matching
            if context.get('student_profile'):
                student_level = context['student_profile'].get('academic_level', 'undergraduate')
                if concept_tags:
                    # Prefer content matching student's academic level
                    for tag in concept_tags:
                        if student_level in tag.lower():
                            relevance += 0.2
        
        return relevance
    
    def _generate_relevance_explanation(self, content: str, query_concepts: List[str], 
                                      context: Dict = None) -> str:
        """Generate explanation for why this content is relevant"""
        
        explanations = []
        
        # Concept matching explanation
        matched_concepts = [concept for concept in query_concepts 
                          if concept in content.lower()]
        if matched_concepts:
            explanations.append(f"Addresses concepts: {', '.join(matched_concepts)}")
        
        # Context explanation
        if context and context.get('current_question'):
            question_title = context['current_question'].get('title', '')
            if question_title:
                explanations.append(f"Relevant to assignment question: {question_title}")
        
        # Source type explanation
        if 'research_literature' in content:
            explanations.append("Provides research-based evidence")
        elif 'case_studies' in content:
            explanations.append("Offers real-world examples")
        
        return " • ".join(explanations) if explanations else "General landscape ecology knowledge"
    
    def get_contextual_knowledge(self, assignment_article: str, current_question: Dict, 
                               student_profile: Dict = None) -> List[Dict[str, Any]]:
        """
        Get knowledge specifically relevant to assignment context.
        
        This is the main method called by the tutoring system.
        """
        
        # Extract concepts from assignment article
        article_concepts = self._extract_concepts_from_query(assignment_article)
        
        # Extract concepts from current question
        question_text = current_question.get('prompt', '') + ' ' + current_question.get('title', '')
        question_concepts = self._extract_concepts_from_query(question_text)
        
        # Combine and prioritize concepts
        combined_concepts = list(set(article_concepts + question_concepts))
        
        # Create context
        context = {
            'current_question': current_question,
            'student_profile': student_profile,
            'article_concepts': article_concepts,
            'question_concepts': question_concepts
        }
        
        # Perform semantic search
        query = f"{question_text} {' '.join(combined_concepts[:5])}"  # Limit to top 5 concepts
        results = self.semantic_search(query, context, top_k=8)
        
        # Record analytics
        self._record_knowledge_retrieval(query, results, student_profile, context)
        
        return results
    
    def _record_knowledge_retrieval(self, query: str, results: List[Dict], 
                                   student_profile: Dict, context: Dict):
        """Record knowledge retrieval for analytics and improvement"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            retrieved_entries = [r['entry_id'] for r in results]
            relevance_scores = [r['final_score'] for r in results]
            student_id = student_profile.get('student_id', 'unknown') if student_profile else 'unknown'
            
            cursor.execute('''
                INSERT INTO knowledge_analytics 
                (query, retrieved_entries, student_id, assignment_context, relevance_scores)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                query,
                json.dumps(retrieved_entries),
                student_id,
                json.dumps(context, default=str),
                json.dumps(relevance_scores)
            ))
            
            # Update access counts for retrieved entries
            for entry_id in retrieved_entries:
                cursor.execute('''
                    UPDATE knowledge_entries 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE entry_id = ?
                ''', (entry_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording knowledge retrieval: {e}")
    
    def update_knowledge_effectiveness(self, entry_id: str, student_feedback: int):
        """Update knowledge effectiveness based on student feedback"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get current effectiveness score
            cursor.execute('SELECT effectiveness_score FROM knowledge_entries WHERE entry_id = ?', (entry_id,))
            result = cursor.fetchone()
            
            if result:
                current_score = result[0]
                # Update with exponential moving average (0.7 weight to history, 0.3 to new feedback)
                new_score = current_score * 0.7 + (student_feedback / 5.0) * 0.3  # Assume 1-5 feedback scale
                
                cursor.execute('''
                    UPDATE knowledge_entries 
                    SET effectiveness_score = ?
                    WHERE entry_id = ?
                ''', (new_score, entry_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating knowledge effectiveness: {e}")
    
    def get_knowledge_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics about knowledge system usage and effectiveness"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get usage statistics
            cursor.execute('''
                SELECT COUNT(*), AVG(json_array_length(relevance_scores))
                FROM knowledge_analytics 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(days))
            
            usage_stats = cursor.fetchone()
            
            # Get most accessed knowledge
            cursor.execute('''
                SELECT entry_id, content, access_count, effectiveness_score
                FROM knowledge_entries 
                ORDER BY access_count DESC 
                LIMIT 10
            ''')
            
            popular_knowledge = cursor.fetchall()
            
            # Get effectiveness distribution
            cursor.execute('''
                SELECT AVG(effectiveness_score), MIN(effectiveness_score), MAX(effectiveness_score)
                FROM knowledge_entries
            ''')
            
            effectiveness_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_queries': usage_stats[0] if usage_stats else 0,
                'avg_results_per_query': usage_stats[1] if usage_stats else 0,
                'popular_knowledge': popular_knowledge,
                'effectiveness_stats': {
                    'average': effectiveness_stats[0] if effectiveness_stats else 0,
                    'min': effectiveness_stats[1] if effectiveness_stats else 0,
                    'max': effectiveness_stats[2] if effectiveness_stats else 0
                }
            }
            
        except Exception as e:
            print(f"Error getting knowledge analytics: {e}")
            return {}
    
    def add_dynamic_knowledge(self, content: str, concept_tags: List[str], 
                            source_type: str = 'dynamic', reliability_score: float = 0.7):
        """Add new knowledge entry dynamically (e.g., from assignment articles)"""
        
        entry_id = hashlib.md5(content.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge_entries 
                (entry_id, content, concept_tags, source_type, academic_level, reliability_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entry_id,
                content,
                json.dumps(concept_tags),
                source_type,
                'undergraduate',  # Default level for dynamic content
                reliability_score
            ))
            
            conn.commit()
            conn.close()
            
            # Rebuild semantic index to include new knowledge
            self._build_semantic_index()
            
            return entry_id
            
        except Exception as e:
            print(f"Error adding dynamic knowledge: {e}")
            return None
    
    def generate_educational_summary(self, knowledge_results: List[Dict], search_context: Dict) -> str:
        """
        Generate educational summary from knowledge search results.
        Tailored to student comprehension level and learning objectives.
        """
        
        if not knowledge_results:
            return "No additional context available from literature at this time."
        
        # Determine appropriate complexity based on context
        bloom_level = search_context.get('bloom_level', 'analyze')
        comprehension_level = search_context.get('student_comprehension_level', 'surface')
        key_concepts = search_context.get('key_concepts', [])
        
        # Select most relevant results based on context
        relevant_results = self._select_most_relevant_for_summary(knowledge_results, search_context)
        
        # Generate summary based on learning level
        if comprehension_level == 'surface' and bloom_level in ['remember', 'understand']:
            return self._generate_foundational_summary(relevant_results, key_concepts)
        elif comprehension_level in ['moderate', 'deep'] and bloom_level in ['apply', 'analyze']:
            return self._generate_analytical_summary(relevant_results, key_concepts)
        else:
            return self._generate_synthesis_summary(relevant_results, key_concepts)
    
    def _select_most_relevant_for_summary(self, results: List[Dict], context: Dict) -> List[Dict]:
        """Select most relevant results for summary based on context"""
        
        # Filter results by relevance score and context appropriateness
        relevant_results = []
        
        for result in results[:5]:  # Consider top 5 results
            relevance = result.get('relevance_score', 0.0)
            academic_level = result.get('metadata', {}).get('academic_level', 'undergraduate')
            
            # Include high relevance results
            if relevance >= 0.7:
                relevant_results.append(result)
            # Include medium relevance if it matches academic level
            elif relevance >= 0.5 and academic_level == 'undergraduate':
                relevant_results.append(result)
        
        return relevant_results[:3]  # Return top 3 most relevant
    
    def _generate_foundational_summary(self, results: List[Dict], key_concepts: List[str]) -> str:
        """Generate summary for foundational learning (remember/understand levels)"""
        
        if not results:
            return "Building strong foundational understanding is key. Focus on the core concepts in your assigned reading."
        
        summary = "**Foundational Context:**\n\n"
        
        # Focus on definitions and basic concepts
        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            if 'defined' in content.lower() or 'definition' in content.lower():
                summary += f"{i}. {content[:200]}...\n\n"
            else:
                # Extract key insight for foundational learners
                summary += f"{i}. {self._extract_key_insight(content, key_concepts, 'foundational')}\n\n"
        
        summary += "**Key Takeaway:** These concepts provide important context for understanding the topic more deeply."
        
        return summary
    
    def _generate_analytical_summary(self, results: List[Dict], key_concepts: List[str]) -> str:
        """Generate summary for analytical learning (apply/analyze levels)"""
        
        if not results:
            return "Strong analysis requires connecting multiple sources. Consider how different studies approach this topic."
        
        summary = "**Research Context & Analysis:**\n\n"
        
        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            key_insight = self._extract_key_insight(content, key_concepts, 'analytical')
            
            summary += f"**Study {i}:** {key_insight}\n"
            
            # Add analytical prompts
            if 'data' in content.lower() or 'results' in content.lower():
                summary += "*Consider: How do these findings compare with your article's results?*\n\n"
            else:
                summary += "*Consider: How does this perspective relate to your current analysis?*\n\n"
        
        summary += "**Analytical Opportunity:** Use these insights to strengthen your evidence-based reasoning and identify patterns across studies."
        
        return summary
    
    def _generate_synthesis_summary(self, results: List[Dict], key_concepts: List[str]) -> str:
        """Generate summary for synthesis learning (evaluate/create levels)"""
        
        if not results:
            return "Advanced synthesis benefits from diverse perspectives. Consider seeking additional scholarly sources."
        
        summary = "**Literature Synthesis & Critical Evaluation:**\n\n"
        
        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            key_insight = self._extract_key_insight(content, key_concepts, 'synthesis')
            
            summary += f"**Research Stream {i}:** {key_insight}\n"
            
            # Add synthesis prompts
            summary += "*Critical Questions: What assumptions underlie this research? How might this challenge or support current thinking?*\n\n"
        
        summary += "**Synthesis Challenge:** Integrate these perspectives with your primary source to develop original insights and evaluate the current state of knowledge in this area."
        
        return summary
    
    def _extract_key_insight(self, content: str, key_concepts: List[str], level: str) -> str:
        """Extract key insight from content appropriate to learning level"""
        
        sentences = content.split('. ')
        
        # Find sentences containing key concepts
        relevant_sentences = []
        for sentence in sentences:
            if any(concept.lower() in sentence.lower() for concept in key_concepts):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            key_sentence = relevant_sentences[0]
        else:
            key_sentence = sentences[0] if sentences else content[:150]
        
        # Adapt based on learning level
        if level == 'foundational':
            return f"{key_sentence}. This establishes important background knowledge."
        elif level == 'analytical':
            return f"{key_sentence}. This provides analytical perspective for comparison."
        else:  # synthesis
            return f"{key_sentence}. This contributes to the broader scholarly conversation."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and performance metrics"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get total knowledge entries
            cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
            total_entries = cursor.fetchone()[0]
            
            # Get recent search performance
            cursor.execute('''
                SELECT query, results_count, search_time 
                FROM knowledge_retrieval_log 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            last_search = cursor.fetchone()
            
            # Get database status
            cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            status = {
                'database_status': 'operational' if table_count >= 2 else 'incomplete',
                'total_entries': total_entries,
                'semantic_search_enabled': hasattr(self, 'concept_index'),
                'last_query_time': last_search[2] if last_search else 'N/A',
                'last_results_count': last_search[1] if last_search else 0,
                'last_extracted_concepts': getattr(self, '_last_concepts', []),
                'top_result_relevance': getattr(self, '_last_top_relevance', 'N/A')
            }
            
            return status
            
        except Exception as e:
            return {
                'database_status': 'error',
                'error_message': str(e),
                'total_entries': 0,
                'semantic_search_enabled': False
            }
    
    # ==================== PHASE 5B: ENHANCED EDUCATIONAL SUMMARIES ====================
    
    def generate_comprehensive_educational_summary(self, knowledge_results: List[Dict], 
                                                 search_context: Dict, 
                                                 complexity_level: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate comprehensive educational summary using Phase 5B advanced capabilities
        
        Args:
            knowledge_results: Results from semantic search
            search_context: Full context including assignment details
            complexity_level: 'foundational', 'intermediate', or 'advanced'
            
        Returns:
            Complete educational summary package with concept maps and synthesis
        """
        
        if not knowledge_results:
            return self.educational_summary_system._create_empty_summary(search_context, complexity_level)
        
        # Prepare summary context from search context
        summary_context = {
            'assignment_title': search_context.get('assignment_title', 'Study Assignment'),
            'question_focus': search_context.get('question_focus', ''),
            'key_concepts': search_context.get('key_concepts', []),
            'bloom_level': search_context.get('bloom_level', 'analyze'),
            'student_comprehension_level': search_context.get('student_comprehension_level', 'moderate'),
            'evidence_quality': search_context.get('evidence_quality', 'moderate'),
            'expected_topics': search_context.get('key_concepts', [])  # Use key concepts as expected topics
        }
        
        # Generate comprehensive educational summary
        educational_summary = self.educational_summary_system.generate_educational_summary(
            knowledge_sources=knowledge_results,
            summary_context=summary_context,
            complexity_level=complexity_level
        )
        
        # Generate literature synthesis if multiple high-quality sources
        if len(knowledge_results) >= 3:
            synthesis_context = {
                'research_question': search_context.get('question_focus', ''),
                'focus_areas': search_context.get('key_concepts', []),
                'expected_topics': search_context.get('key_concepts', [])
            }
            
            literature_synthesis = self.literature_synthesis_tools.synthesize_literature(
                knowledge_sources=knowledge_results,
                synthesis_context=synthesis_context,
                synthesis_type='thematic_synthesis'
            )
            
            educational_summary['literature_synthesis'] = literature_synthesis
        
        return educational_summary
    
    def create_multi_level_summary_package(self, knowledge_results: List[Dict], 
                                         search_context: Dict) -> Dict[str, Any]:
        """
        Create summary package with multiple complexity levels for progressive disclosure
        
        Returns:
            Dict with foundational, intermediate, and advanced summaries
        """
        
        summary_package = {
            'summary_levels': {},
            'progression_guidance': self._generate_progression_guidance(search_context),
            'level_selection_guide': self._generate_level_selection_guide(search_context),
            'metadata': {
                'total_sources': len(knowledge_results),
                'created_date': datetime.now().isoformat(),
                'context_complexity': search_context.get('bloom_level', 'analyze')
            }
        }
        
        # Generate summaries for each complexity level
        for level in ['foundational', 'intermediate', 'advanced']:
            try:
                summary = self.generate_comprehensive_educational_summary(
                    knowledge_results, search_context, level
                )
                summary_package['summary_levels'][level] = summary
            except Exception as e:
                summary_package['summary_levels'][level] = {
                    'error': f"Summary generation failed: {e}",
                    'structured_content': f"Summary at {level} level unavailable"
                }
        
        return summary_package
    
    def _generate_progression_guidance(self, context: Dict) -> Dict[str, str]:
        """Generate guidance for progressing through summary levels"""
        
        return {
            'foundational_to_intermediate': """
            Once you understand the basic concepts and definitions, you're ready to explore 
            how different research studies approach these topics and what patterns emerge.
            """,
            'intermediate_to_advanced': """
            After grasping the research patterns and connections, you can move to critical 
            evaluation of the studies, identification of gaps, and development of original insights.
            """,
            'level_indicators': {
                'foundational': "Start here if concepts are unfamiliar or you need basic understanding",
                'intermediate': "Use this level when ready to analyze relationships and patterns",
                'advanced': "Access this level for critical evaluation and original thinking"
            }
        }
    
    def _generate_level_selection_guide(self, context: Dict) -> Dict[str, Any]:
        """Generate guide for selecting appropriate summary level"""
        
        bloom_level = context.get('bloom_level', 'analyze')
        comprehension_level = context.get('student_comprehension_level', 'moderate')
        
        # Recommend starting level based on context
        if comprehension_level == 'surface' or bloom_level in ['remember', 'understand']:
            recommended_start = 'foundational'
        elif comprehension_level == 'moderate' or bloom_level in ['apply', 'analyze']:
            recommended_start = 'intermediate'
        else:
            recommended_start = 'advanced'
        
        return {
            'recommended_starting_level': recommended_start,
            'level_descriptions': {
                'foundational': 'Basic concepts, definitions, and simple examples',
                'intermediate': 'Research findings, patterns, and analytical connections',
                'advanced': 'Critical evaluation, synthesis, and original insights'
            },
            'progression_pathway': ['foundational', 'intermediate', 'advanced'],
            'time_estimates': {
                'foundational': '5-10 minutes reading',
                'intermediate': '10-15 minutes analysis',
                'advanced': '15-20 minutes critical thinking'
            }
        }
    
    def get_enhanced_summary_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on enhanced summary generation and effectiveness"""
        
        try:
            # Get educational summary analytics
            edu_analytics = self.educational_summary_system.get_summary_analytics(days)
            
            # Get knowledge system analytics
            knowledge_analytics = self.get_knowledge_analytics(days)
            
            # Combine analytics
            combined_analytics = {
                'summary_generation': edu_analytics.get('summary_generation', {}),
                'feedback_analysis': edu_analytics.get('feedback_analysis', {}),
                'knowledge_retrieval': knowledge_analytics.get('usage_patterns', {}),
                'system_performance': {
                    'total_enhanced_summaries': edu_analytics.get('summary_generation', {}).get('total_summaries', 0),
                    'average_effectiveness': edu_analytics.get('summary_generation', {}).get('avg_effectiveness', 0),
                    'user_satisfaction': edu_analytics.get('feedback_analysis', {}).get('avg_helpfulness', 0)
                },
                'enhancement_impact': self._calculate_enhancement_impact(edu_analytics, knowledge_analytics)
            }
            
            return combined_analytics
            
        except Exception as e:
            return {
                'error': f"Enhanced analytics unavailable: {e}",
                'summary_generation': {'total_summaries': 0},
                'system_performance': {'total_enhanced_summaries': 0}
            }
    
    def _calculate_enhancement_impact(self, edu_analytics: Dict, knowledge_analytics: Dict) -> Dict[str, Any]:
        """Calculate the impact of Phase 5B enhancements"""
        
        # Calculate improvement metrics
        total_summaries = edu_analytics.get('summary_generation', {}).get('total_summaries', 0)
        avg_effectiveness = edu_analytics.get('summary_generation', {}).get('avg_effectiveness', 0)
        total_feedback = edu_analytics.get('feedback_analysis', {}).get('total_feedback', 0)
        
        enhancement_impact = {
            'summary_adoption_rate': min(total_summaries / 100.0, 1.0),  # Normalized adoption
            'effectiveness_score': avg_effectiveness,
            'user_engagement': min(total_feedback / 50.0, 1.0),  # Normalized engagement
            'feature_utilization': {
                'multi_level_summaries': total_summaries > 0,
                'concept_mapping': True,  # Always available
                'literature_synthesis': total_summaries > 5  # Available when sufficient usage
            }
        }
        
        # Calculate overall enhancement score
        enhancement_score = (
            enhancement_impact['summary_adoption_rate'] * 0.3 +
            enhancement_impact['effectiveness_score'] * 0.4 +
            enhancement_impact['user_engagement'] * 0.3
        )
        
        enhancement_impact['overall_enhancement_score'] = enhancement_score
        enhancement_impact['enhancement_level'] = (
            'high' if enhancement_score > 0.7 else 
            'moderate' if enhancement_score > 0.4 else 
            'developing'
        )
        
        return enhancement_impact
    
    # ==================== PHASE 5E: REAL-TIME DATABASE INTEGRATION ====================
    
    def search_live_academic_databases(self, query: str, context: Dict = None, 
                                     max_results: int = 10, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search live academic databases for current research findings
        
        Args:
            query: Search query string
            context: Additional context for search optimization
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results (default: True)
            
        Returns:
            List of current academic sources with quality scores
        """
        
        try:
            # Search real-time databases
            live_results = self.real_time_database.search_academic_databases(
                query=query,
                context=context,
                max_results=max_results,
                force_refresh=not use_cache
            )
            
            # Convert to Enhanced Knowledge System format
            formatted_results = []
            for result in live_results:
                formatted_result = {
                    'content': self._format_academic_content(result),
                    'metadata': {
                        'source_type': 'live_academic',
                        'database_source': result.get('database_source'),
                        'title': result.get('title'),
                        'authors': result.get('authors'),
                        'journal': result.get('journal'),
                        'publication_year': result.get('publication_year'),
                        'citation_count': result.get('citation_count', 0),
                        'doi': result.get('doi'),
                        'url': result.get('url'),
                        'academic_level': self._determine_academic_level(result),
                        'concepts': result.get('keywords', [])
                    },
                    'relevance_score': result.get('relevance_score', 0.5),
                    'quality_score': result.get('quality_score', 0.5),
                    'combined_score': result.get('combined_score', 0.5)
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching live databases: {e}")
            # Fallback to static knowledge base
            return self.semantic_search(query, context, max_results)
    
    def _format_academic_content(self, result: Dict) -> str:
        """Format academic result into readable content"""
        
        title = result.get('title', 'Untitled Research')
        authors = result.get('authors', 'Unknown Authors')
        year = result.get('publication_year', 'Unknown Year')
        abstract = result.get('abstract', 'Abstract not available.')
        journal = result.get('journal', '')
        
        # Create formatted content
        content_parts = []
        
        # Add citation-style header
        if journal:
            content_parts.append(f"{authors} ({year}). {title}. {journal}.")
        else:
            content_parts.append(f"{authors} ({year}). {title}.")
        
        # Add abstract
        if abstract and len(abstract) > 50:
            content_parts.append(f"Abstract: {abstract}")
        
        # Add citation information if available
        citations = result.get('citation_count', 0)
        if citations > 0:
            content_parts.append(f"Citations: {citations}")
        
        return " ".join(content_parts)
    
    def _determine_academic_level(self, result: Dict) -> str:
        """Determine academic level based on source characteristics"""
        
        # Check journal prestige and citation count
        citations = result.get('citation_count', 0)
        journal = result.get('journal', '').lower()
        
        # High-impact journals (simplified check)
        high_impact_journals = ['nature', 'science', 'cell', 'pnas', 'ecology']
        
        if any(journal_name in journal for journal_name in high_impact_journals):
            return 'graduate'
        elif citations >= 50:
            return 'graduate'
        elif citations >= 10:
            return 'undergraduate'
        else:
            return 'undergraduate'
    
    def hybrid_search(self, query: str, context: Dict = None, 
                     max_results: int = 15, live_ratio: float = 0.6) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining static knowledge base and live databases
        
        Args:
            query: Search query
            context: Search context
            max_results: Total maximum results
            live_ratio: Proportion of results from live databases (0.0-1.0)
            
        Returns:
            Combined and ranked results from both sources
        """
        
        live_count = int(max_results * live_ratio)
        static_count = max_results - live_count
        
        # Search both sources simultaneously
        try:
            # Get live results
            live_results = self.search_live_academic_databases(query, context, live_count)
            
            # Get static results (fallback to enhanced static search)
            static_results = self.semantic_search(query, context, static_count)
            
            # Combine and re-rank
            all_results = live_results + static_results
            
            # Add source type indicators
            for result in all_results:
                # Handle both live and static result formats
                if 'metadata' in result and result['metadata'].get('source_type') == 'live_academic':
                    result['source_freshness'] = 'current'
                else:
                    result['source_freshness'] = 'curated'
                    # Ensure metadata exists for static results
                    if 'metadata' not in result:
                        result['metadata'] = {'source_type': 'static_knowledge'}
            
            # Re-rank combined results
            hybrid_ranking = self._rank_hybrid_results(all_results, query, context)
            
            return hybrid_ranking[:max_results]
            
        except Exception as e:
            print(f"Hybrid search error: {e}")
            # Fallback to static search
            return self.semantic_search(query, context, max_results)
    
    def _rank_hybrid_results(self, results: List[Dict], query: str, context: Dict = None) -> List[Dict]:
        """Re-rank hybrid results considering both relevance and freshness"""
        
        for result in results:
            base_score = result.get('combined_score', result.get('relevance_score', 0.5))
            
            # Boost for recent publications
            if 'metadata' in result and result['metadata'].get('source_type') == 'live_academic':
                pub_year = result['metadata'].get('publication_year', 2020)
                current_year = datetime.now().year
                age = current_year - pub_year
                
                if age <= 2:  # Very recent
                    freshness_boost = 0.15
                elif age <= 5:  # Recent
                    freshness_boost = 0.10
                else:  # Older
                    freshness_boost = 0.0
                
                result['final_score'] = min(base_score + freshness_boost, 1.0)
            else:
                # Static sources get slight penalty but remain valuable
                result['final_score'] = base_score * 0.95
        
        # Sort by final score
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return results
    
    def get_database_health_status(self) -> Dict[str, Any]:
        """Get comprehensive database health status including live databases"""
        
        try:
            # Get real-time database health
            live_health = self.real_time_database.get_database_health_status()
            
            # Get static system status
            static_status = self.get_system_status()
            
            # Combine health information
            comprehensive_health = {
                'overall_system_health': 'operational',
                'static_knowledge_base': {
                    'status': static_status.get('database_status', 'unknown'),
                    'total_entries': static_status.get('total_entries', 0),
                    'semantic_search_enabled': static_status.get('semantic_search_enabled', False)
                },
                'live_academic_databases': live_health.get('database_status', {}),
                'performance_metrics': {
                    'static_system': static_status,
                    'live_system': live_health.get('performance_summary', {})
                },
                'last_updated': datetime.now().isoformat()
            }
            
            # Determine overall health
            if (static_status.get('database_status') == 'error' and 
                live_health.get('overall_status') == 'error'):
                comprehensive_health['overall_system_health'] = 'critical'
            elif (static_status.get('database_status') == 'error' or 
                  live_health.get('overall_status') in ['error', 'degraded']):
                comprehensive_health['overall_system_health'] = 'degraded'
            
            return comprehensive_health
            
        except Exception as e:
            return {
                'overall_system_health': 'error',
                'error_message': str(e),
                'static_knowledge_base': {'status': 'unknown'},
                'live_academic_databases': {}
            }
    
    def optimize_live_database_performance(self) -> Dict[str, Any]:
        """Optimize performance of live database integration"""
        
        try:
            # Get optimization recommendations from real-time system
            optimization_report = self.real_time_database.optimize_search_performance()
            
            # Add enhanced knowledge system specific optimizations
            enhanced_optimizations = {
                'hybrid_search_optimization': self._analyze_hybrid_search_performance(),
                'cache_optimization': self._optimize_knowledge_cache(),
                'integration_recommendations': self._generate_integration_recommendations()
            }
            
            # Combine reports
            comprehensive_optimization = {
                'live_database_analysis': optimization_report,
                'enhanced_system_analysis': enhanced_optimizations,
                'recommended_actions': self._prioritize_optimization_actions(
                    optimization_report, enhanced_optimizations
                ),
                'analysis_date': datetime.now().isoformat()
            }
            
            return comprehensive_optimization
            
        except Exception as e:
            return {
                'error': f'Optimization analysis failed: {e}',
                'recommended_actions': ['Check system connectivity', 'Review error logs']
            }
    
    def _analyze_hybrid_search_performance(self) -> Dict[str, Any]:
        """Analyze performance of hybrid search combining live and static sources"""
        
        # This would analyze actual usage patterns in production
        return {
            'hybrid_search_usage': 'simulated_data',
            'live_vs_static_preference': 0.65,  # 65% prefer live results
            'response_time_impact': '+200ms average for live integration',
            'quality_improvement': '+15% user satisfaction with live results'
        }
    
    def _optimize_knowledge_cache(self) -> Dict[str, Any]:
        """Optimize caching strategy for combined system"""
        
        return {
            'cache_efficiency': 'analyzing',
            'recommendations': [
                'Increase cache duration for stable academic content',
                'Implement intelligent prefetching for common queries',
                'Separate cache strategies for live vs static content'
            ]
        }
    
    def _generate_integration_recommendations(self) -> List[str]:
        """Generate recommendations for improving live database integration"""
        
        return [
            'Consider implementing query preprocessing for better API efficiency',
            'Add more domain-specific databases for landscape ecology',
            'Implement progressive enhancement: static first, then live enhancement',
            'Add user preference settings for live vs cached content'
        ]
    
    def _prioritize_optimization_actions(self, live_report: Dict, enhanced_report: Dict) -> List[str]:
        """Prioritize optimization actions based on impact and effort"""
        
        high_priority = []
        medium_priority = []
        
        # Analyze live database recommendations
        live_recommendations = live_report.get('optimization_recommendations', [])
        for rec in live_recommendations:
            if 'cache' in rec.lower() or 'response time' in rec.lower():
                high_priority.append(f"Live DB: {rec}")
            else:
                medium_priority.append(f"Live DB: {rec}")
        
        # Add enhanced system recommendations
        enhanced_recommendations = enhanced_report.get('integration_recommendations', [])
        for rec in enhanced_recommendations:
            if 'progressive enhancement' in rec.lower() or 'efficiency' in rec.lower():
                high_priority.append(f"Integration: {rec}")
            else:
                medium_priority.append(f"Integration: {rec}")
        
        # Return prioritized list
        return high_priority + medium_priority[:5]  # Top 5 medium priority
    
    def clear_all_caches(self) -> Dict[str, Any]:
        """Clear all caches (static and live database)"""
        
        try:
            # Clear live database cache
            live_cleanup = self.real_time_database.clear_expired_cache()
            
            # Clear any static caches (if implemented)
            static_cleanup = {'expired_entries_found': 0, 'entries_deleted': 0}  # Placeholder
            
            return {
                'live_database_cleanup': live_cleanup,
                'static_system_cleanup': static_cleanup,
                'total_cleanup': {
                    'total_entries_deleted': live_cleanup.get('entries_deleted', 0) + static_cleanup.get('entries_deleted', 0),
                    'cleanup_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'error': f'Cache cleanup failed: {e}',
                'total_cleanup': {'total_entries_deleted': 0}
            }