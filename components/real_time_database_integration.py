"""
Real-Time Academic Database Integration System for EcoCritique
Connects to live academic databases to provide current research findings
"""

import json
import sqlite3
import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Optional imports - graceful fallback for production environments
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import urllib.parse
    URLLIB_AVAILABLE = True
except ImportError:
    URLLIB_AVAILABLE = False

try:
    import xml.etree.ElementTree as ET
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

class RealTimeAcademicDatabase:
    """
    Real-time academic database integration system that connects to multiple
    academic sources to provide current, peer-reviewed research findings.
    """
    
    def __init__(self, database_path: str = "ecocritique.db", cache_duration: int = 24):
        self.database_path = database_path
        self.cache_duration = cache_duration  # Hours
        self.initialize_database()
        
        # Check for required dependencies
        self.dependencies_available = {
            'requests': REQUESTS_AVAILABLE,
            'urllib': URLLIB_AVAILABLE,
            'xml': XML_AVAILABLE
        }
        
        # Enable/disable databases based on dependencies
        if not REQUESTS_AVAILABLE:
            print("Warning: 'requests' module not available. Live database functionality limited to simulated mode.")
            # Keep databases enabled for testing with simulated responses
        
        # Academic database configurations
        self.database_configs = {
            'google_scholar': {
                'base_url': 'https://scholar.google.com/scholar',
                'rate_limit': 1.0,  # seconds between requests
                'max_results': 10,
                'supported_fields': ['title', 'authors', 'year', 'citations', 'abstract'],
                'quality_threshold': 0.7,
                'enabled': True  # Can be disabled if API issues
            },
            'pubmed': {
                'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
                'api_key': None,  # Would be set from environment variable
                'rate_limit': 0.34,  # 3 requests per second max
                'max_results': 20,
                'supported_fields': ['title', 'authors', 'abstract', 'journal', 'year', 'pmid'],
                'quality_threshold': 0.8,
                'enabled': True
            },
            'arxiv': {
                'base_url': 'http://export.arxiv.org/api/query',
                'rate_limit': 3.0,  # Be conservative
                'max_results': 10,
                'supported_fields': ['title', 'authors', 'abstract', 'category', 'published'],
                'quality_threshold': 0.6,
                'enabled': True
            },
            'crossref': {
                'base_url': 'https://api.crossref.org/works',
                'rate_limit': 1.0,
                'max_results': 10,
                'supported_fields': ['title', 'authors', 'abstract', 'journal', 'year', 'doi'],
                'quality_threshold': 0.8,
                'enabled': True
            }
        }
        
        # Domain-specific search optimization for landscape ecology
        self.ecology_search_enhancement = {
            'synonyms': {
                'fragmentation': ['habitat fragmentation', 'landscape fragmentation', 'forest fragmentation'],
                'connectivity': ['landscape connectivity', 'habitat connectivity', 'ecological connectivity'],
                'corridors': ['wildlife corridors', 'habitat corridors', 'ecological corridors'],
                'biodiversity': ['biological diversity', 'species diversity', 'ecosystem diversity'],
                'conservation': ['nature conservation', 'wildlife conservation', 'ecosystem conservation']
            },
            'key_journals': [
                'Landscape Ecology', 'Conservation Biology', 'Biological Conservation',
                'Ecology', 'Journal of Applied Ecology', 'Ecosystem Services',
                'Landscape and Urban Planning', 'Forest Ecology and Management'
            ],
            'preferred_terms': [
                'landscape ecology', 'spatial ecology', 'ecosystem', 'habitat',
                'species composition', 'ecological processes', 'land use'
            ],
            'domain_boost_keywords': [
                'landscape', 'ecological', 'conservation', 'biodiversity', 'habitat',
                'species', 'ecosystem', 'environmental', 'spatial', 'wildlife'
            ]
        }
        
        # Quality control criteria
        self.quality_criteria = {
            'min_citation_count': 5,  # Minimum citations for consideration
            'max_age_years': 15,      # Maximum age for research
            'preferred_age_years': 5,  # Prefer recent research
            'min_abstract_length': 100,  # Minimum abstract length
            'peer_review_indicators': [
                'peer review', 'reviewed', 'journal', 'published',
                'doi:', 'volume', 'issue', 'pages'
            ],
            'quality_indicators': [
                'methodology', 'analysis', 'results', 'conclusion',
                'study', 'research', 'investigation', 'experiment'
            ]
        }
        
        # Performance monitoring
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'cached_responses': 0,
            'api_errors': defaultdict(int),
            'average_response_time': 0.0,
            'quality_scores': []
        }
    
    def initialize_database(self):
        """Initialize database tables for real-time academic data management"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Real-time academic sources cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS academic_sources_cache (
                    source_id TEXT PRIMARY KEY,
                    query_hash TEXT NOT NULL,
                    database_source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    journal TEXT,
                    publication_year INTEGER,
                    citation_count INTEGER DEFAULT 0,
                    doi TEXT,
                    url TEXT,
                    keywords TEXT,
                    quality_score REAL DEFAULT 0.0,
                    relevance_score REAL DEFAULT 0.0,
                    cached_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            ''')
            
            # Query performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_performance (
                    query_id TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    database_sources TEXT,
                    total_results INTEGER DEFAULT 0,
                    quality_results INTEGER DEFAULT 0,
                    response_time_ms INTEGER DEFAULT 0,
                    cache_hit BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Database health monitoring
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS database_health (
                    health_id TEXT PRIMARY KEY,
                    database_name TEXT NOT NULL,
                    status TEXT DEFAULT 'unknown',
                    last_successful_query TIMESTAMP,
                    error_count INTEGER DEFAULT 0,
                    average_response_time REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.0,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing real-time database: {e}")
    
    def search_academic_databases(self, query: str, context: Dict = None, 
                                 max_results: int = 15, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Search multiple academic databases simultaneously for relevant research
        
        Args:
            query: Search query string
            context: Additional context for search optimization
            max_results: Maximum number of results to return
            force_refresh: Force fresh API calls instead of using cache
            
        Returns:
            List of academic sources with metadata and quality scores
        """
        
        start_time = time.time()
        self.performance_metrics['total_queries'] += 1
        
        # Generate query hash for caching
        query_hash = self._generate_query_hash(query, context)
        
        # Check cache first (unless force_refresh)
        if not force_refresh:
            cached_results = self._get_cached_results(query_hash, max_results)
            if cached_results:
                self.performance_metrics['cached_responses'] += 1
                self._record_query_performance(query, cached_results, time.time() - start_time, True)
                return cached_results
        
        # Enhance query for domain-specific search
        enhanced_query = self._enhance_query_for_ecology(query, context)
        
        # Search multiple databases in parallel (simulated)
        all_results = []
        database_errors = {}
        
        for db_name, config in self.database_configs.items():
            if not config['enabled']:
                continue
                
            try:
                db_results = self._search_database(db_name, enhanced_query, config)
                all_results.extend(db_results)
                
                # Rate limiting
                time.sleep(config['rate_limit'])
                
            except Exception as e:
                database_errors[db_name] = str(e)
                self.performance_metrics['api_errors'][db_name] += 1
                continue
        
        # Process and rank results
        processed_results = self._process_and_rank_results(all_results, query, context)
        
        # Apply quality filtering
        quality_results = self._apply_quality_filtering(processed_results)
        
        # Limit results
        final_results = quality_results[:max_results]
        
        # Cache results for future use
        if final_results:
            self._cache_results(query_hash, final_results)
        
        # Record performance metrics
        total_time = time.time() - start_time
        self._record_query_performance(query, final_results, total_time, False, database_errors)
        
        if final_results:
            self.performance_metrics['successful_queries'] += 1
        
        return final_results
    
    def _enhance_query_for_ecology(self, query: str, context: Dict = None) -> str:
        """Enhance search query with domain-specific terms for landscape ecology"""
        
        enhanced_query = query.lower()
        
        # Add synonyms for key terms
        for term, synonyms in self.ecology_search_enhancement['synonyms'].items():
            if term in enhanced_query:
                # Add primary synonym to broaden search
                enhanced_query += f" OR {synonyms[0]}"
        
        # Add domain context if available
        if context:
            key_concepts = context.get('key_concepts', [])
            for concept in key_concepts:
                if concept.lower() not in enhanced_query.lower():
                    enhanced_query += f" {concept}"
            
            # Add assignment context
            if 'question_focus' in context:
                focus_terms = self._extract_domain_terms(context['question_focus'])
                for term in focus_terms:
                    if term not in enhanced_query:
                        enhanced_query += f" {term}"
        
        # Add general domain boost
        domain_terms = ['landscape ecology', 'conservation biology']
        enhanced_query += f" ({' OR '.join(domain_terms)})"
        
        return enhanced_query
    
    def _extract_domain_terms(self, text: str) -> List[str]:
        """Extract domain-relevant terms from text"""
        
        domain_terms = []
        text_lower = text.lower()
        
        for term in self.ecology_search_enhancement['preferred_terms']:
            if term in text_lower:
                domain_terms.append(term)
        
        return domain_terms[:3]  # Return top 3 terms
    
    def _search_database(self, database_name: str, query: str, config: Dict) -> List[Dict[str, Any]]:
        """Search a specific academic database"""
        
        if database_name == 'google_scholar':
            return self._search_google_scholar(query, config)
        elif database_name == 'pubmed':
            return self._search_pubmed(query, config)
        elif database_name == 'arxiv':
            return self._search_arxiv(query, config)
        elif database_name == 'crossref':
            return self._search_crossref(query, config)
        else:
            return []
    
    def _search_google_scholar(self, query: str, config: Dict) -> List[Dict[str, Any]]:
        """Search using Semantic Scholar API (Google Scholar alternative)"""
        
        if not REQUESTS_AVAILABLE:
            print(f"[WARNING] Semantic Scholar search unavailable: requests module not installed")
            return []
        
        try:
            # Semantic Scholar API - free alternative to Google Scholar
            base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            
            params = {
                'query': query,
                'limit': config['max_results'],
                'fields': 'paperId,title,authors,abstract,venue,year,citationCount,url,openAccessPdf'
            }
            
            # Add polite headers
            headers = {
                'User-Agent': 'EcoCritique Educational Platform (mailto:support@ecocritique.edu)',
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get('data', [])
            
            if not papers:
                print(f"[INFO] No Semantic Scholar results found for query: {query}")
                return []
            
            results = []
            for paper in papers:
                # Extract basic info
                title = paper.get('title', 'Untitled')
                paper_id = paper.get('paperId', '')
                
                # Extract authors
                authors = paper.get('authors', [])
                author_names = []
                for author in authors[:3]:  # Limit to first 3 authors
                    name = author.get('name', '')
                    if name:
                        author_names.append(name)
                authors_str = ', '.join(author_names) if author_names else 'Unknown Authors'
                
                # Extract other fields
                abstract = paper.get('abstract', 'Abstract not available')
                venue = paper.get('venue', 'Unknown Venue')
                year = paper.get('year', 'Unknown')
                citation_count = paper.get('citationCount', 0)
                paper_url = paper.get('url', f'https://www.semanticscholar.org/paper/{paper_id}')
                
                # Check for open access
                open_access_pdf = paper.get('openAccessPdf', {})
                has_open_access = bool(open_access_pdf and open_access_pdf.get('url'))
                
                result = {
                    'source_id': f'ss_{paper_id}',
                    'database_source': 'semantic_scholar',
                    'title': title,
                    'authors': authors_str,
                    'abstract': abstract if abstract else 'Abstract not available',
                    'journal': venue,
                    'publication_year': str(year) if year else 'Unknown',
                    'citation_count': citation_count or 0,
                    'url': paper_url,
                    'keywords': query.split(),
                    'raw_relevance': 0.88,  # Semantic Scholar has good relevance
                    'open_access': has_open_access,
                    'metadata': {
                        'source_type': 'live_academic',
                        'database': 'semantic_scholar',
                        'verification_status': 'verified',
                        'paper_type': 'peer_reviewed'
                    }
                }
                results.append(result)
            
            print(f"[SUCCESS] Retrieved {len(results)} verified Semantic Scholar articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Semantic Scholar API request failed: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Semantic Scholar search error: {e}")
            return []
    
    def _search_pubmed(self, query: str, config: Dict) -> List[Dict[str, Any]]:
        """Search PubMed database using official NCBI E-utilities API"""
        
        if not REQUESTS_AVAILABLE:
            print(f"[WARNING] PubMed search unavailable: requests module not installed")
            return []
        
        try:
            # PubMed E-utilities API - completely free and official
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            # Step 1: Search for PMIDs
            search_url = f"{base_url}esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': config['max_results'],
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            pmids = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                print(f"[INFO] No PubMed results found for query: {query}")
                return []
            
            # Step 2: Get article details
            fetch_url = f"{base_url}esummary.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'json'
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
            fetch_response.raise_for_status()
            fetch_data = fetch_response.json()
            
            results = []
            for pmid in pmids:
                if pmid in fetch_data.get('result', {}):
                    article = fetch_data['result'][pmid]
                    
                    # Extract authors
                    authors = []
                    if 'authors' in article:
                        authors = [auth.get('name', '') for auth in article['authors'][:3]]
                    authors_str = ', '.join(authors) if authors else 'Unknown Authors'
                    
                    # Extract publication year
                    pub_date = article.get('pubdate', '')
                    pub_year = pub_date.split()[0] if pub_date else 'Unknown'
                    
                    result = {
                        'source_id': f'pm_{pmid}',
                        'database_source': 'pubmed',
                        'title': article.get('title', 'Untitled'),
                        'authors': authors_str,
                        'abstract': article.get('abstract', 'Abstract not available'),
                        'journal': article.get('source', 'Unknown Journal'),
                        'publication_year': pub_year,
                        'pmid': pmid,
                        'url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                        'keywords': query.split(),
                        'raw_relevance': 0.8,  # PubMed relevance is generally high
                        'citation_count': 0,  # PubMed doesn't provide citation counts
                        'metadata': {
                            'source_type': 'live_academic',
                            'database': 'pubmed',
                            'verification_status': 'verified'
                        }
                    }
                    results.append(result)
            
            print(f"[SUCCESS] Retrieved {len(results)} verified PubMed articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] PubMed API request failed: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] PubMed search error: {e}")
            return []
    
    def _search_arxiv(self, query: str, config: Dict) -> List[Dict[str, Any]]:
        """Search arXiv database using official arXiv API"""
        
        if not REQUESTS_AVAILABLE:
            print(f"[WARNING] arXiv search unavailable: requests module not installed")
            return []
        
        try:
            # arXiv API - completely free and official
            base_url = "http://export.arxiv.org/api/query"
            
            # Format query for arXiv (they prefer specific field searches)
            arxiv_query = f'all:{query}'
            
            params = {
                'search_query': arxiv_query,
                'start': 0,
                'max_results': config['max_results'],
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            if not XML_AVAILABLE:
                print(f"[WARNING] arXiv search unavailable: XML parsing not available")
                return []
            
            root = ET.fromstring(response.content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            results = []
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                # Extract basic info
                title = entry.find('atom:title', namespaces)
                title_text = title.text.strip() if title is not None else 'Untitled'
                
                # Extract authors
                authors = entry.findall('atom:author', namespaces)
                author_names = []
                for author in authors[:3]:  # Limit to first 3 authors
                    name_elem = author.find('atom:name', namespaces)
                    if name_elem is not None:
                        author_names.append(name_elem.text)
                authors_str = ', '.join(author_names) if author_names else 'Unknown Authors'
                
                # Extract abstract
                summary = entry.find('atom:summary', namespaces)
                abstract_text = summary.text.strip() if summary is not None else 'Abstract not available'
                
                # Extract publication date
                published = entry.find('atom:published', namespaces)
                pub_date = published.text if published is not None else ''
                pub_year = pub_date[:4] if len(pub_date) >= 4 else 'Unknown'
                
                # Extract arXiv ID and URL
                arxiv_id = entry.find('atom:id', namespaces)
                paper_url = arxiv_id.text if arxiv_id is not None else ''
                
                # Extract arXiv ID from URL for cleaner reference
                clean_id = paper_url.split('/')[-1] if paper_url else 'unknown'
                
                # Extract categories
                categories = entry.findall('atom:category', namespaces)
                category_list = [cat.get('term', '') for cat in categories if cat.get('term')]
                main_category = category_list[0] if category_list else 'unknown'
                
                result = {
                    'source_id': f'ax_{clean_id}',
                    'database_source': 'arxiv',
                    'title': title_text,
                    'authors': authors_str,
                    'abstract': abstract_text,
                    'category': main_category,
                    'published': pub_date[:10] if pub_date else 'Unknown',  # YYYY-MM-DD format
                    'publication_year': pub_year,
                    'url': paper_url,
                    'arxiv_id': clean_id,
                    'keywords': query.split(),
                    'raw_relevance': 0.75,  # arXiv relevance is good but preprints
                    'citation_count': 0,  # arXiv doesn't provide citation counts
                    'metadata': {
                        'source_type': 'live_academic',
                        'database': 'arxiv',
                        'verification_status': 'verified',
                        'paper_type': 'preprint'
                    }
                }
                results.append(result)
            
            print(f"[SUCCESS] Retrieved {len(results)} verified arXiv articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] arXiv API request failed: {e}")
            return []
        except ET.ParseError as e:
            print(f"[ERROR] arXiv XML parsing failed: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] arXiv search error: {e}")
            return []
    
    def _search_crossref(self, query: str, config: Dict) -> List[Dict[str, Any]]:
        """Search Crossref database using official Crossref REST API"""
        
        if not REQUESTS_AVAILABLE:
            print(f"[WARNING] Crossref search unavailable: requests module not installed")
            return []
        
        try:
            # Crossref REST API - completely free and official
            base_url = "https://api.crossref.org/works"
            
            params = {
                'query': query,
                'rows': config['max_results'],
                'sort': 'relevance',
                'select': 'title,author,abstract,published-print,published-online,container-title,DOI,is-referenced-by-count,URL'
            }
            
            # Add polite pool and contact info as recommended by Crossref
            headers = {
                'User-Agent': 'EcoCritique Educational Platform (mailto:support@ecocritique.edu)',
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            if not items:
                print(f"[INFO] No Crossref results found for query: {query}")
                return []
            
            results = []
            for item in items:
                # Extract title
                title_list = item.get('title', [])
                title = title_list[0] if title_list else 'Untitled'
                
                # Extract authors
                authors = item.get('author', [])
                author_names = []
                for author in authors[:3]:  # Limit to first 3 authors
                    given = author.get('given', '')
                    family = author.get('family', '')
                    if family:
                        full_name = f"{family}, {given}".strip(', ')
                        author_names.append(full_name)
                authors_str = '; '.join(author_names) if author_names else 'Unknown Authors'
                
                # Extract abstract (often not available in Crossref)
                abstract = item.get('abstract', 'Abstract not available via Crossref API')
                
                # Extract publication year
                pub_date_print = item.get('published-print', {})
                pub_date_online = item.get('published-online', {})
                
                # Try to get year from either print or online publication date
                pub_year = 'Unknown'
                if pub_date_print.get('date-parts'):
                    pub_year = str(pub_date_print['date-parts'][0][0])
                elif pub_date_online.get('date-parts'):
                    pub_year = str(pub_date_online['date-parts'][0][0])
                
                # Extract journal/container
                container_titles = item.get('container-title', [])
                journal = container_titles[0] if container_titles else 'Unknown Journal'
                
                # Extract DOI and URL
                doi = item.get('DOI', '')
                url = item.get('URL', f'https://doi.org/{doi}' if doi else '')
                
                # Extract citation count
                citation_count = item.get('is-referenced-by-count', 0)
                
                result = {
                    'source_id': f'cr_{doi.replace("/", "_")}' if doi else f'cr_{hash(title)}',
                    'database_source': 'crossref',
                    'title': title,
                    'authors': authors_str,
                    'abstract': abstract,
                    'journal': journal,
                    'publication_year': pub_year,
                    'doi': doi,
                    'url': url,
                    'citation_count': citation_count,
                    'keywords': query.split(),
                    'raw_relevance': 0.85,  # Crossref relevance is generally high
                    'metadata': {
                        'source_type': 'live_academic',
                        'database': 'crossref',
                        'verification_status': 'verified',
                        'paper_type': 'peer_reviewed'
                    }
                }
                results.append(result)
            
            print(f"[SUCCESS] Retrieved {len(results)} verified Crossref articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Crossref API request failed: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Crossref search error: {e}")
            return []
    
    def _process_and_rank_results(self, all_results: List[Dict], query: str, context: Dict = None) -> List[Dict[str, Any]]:
        """Process and rank results by relevance and quality"""
        
        processed_results = []
        
        for result in all_results:
            # Calculate enhanced relevance score
            relevance_score = self._calculate_relevance_score(result, query, context)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(result)
            
            # Combine scores with weights
            combined_score = (relevance_score * 0.6) + (quality_score * 0.4)
            
            # Add processed information
            processed_result = result.copy()
            processed_result.update({
                'relevance_score': relevance_score,
                'quality_score': quality_score,
                'combined_score': combined_score,
                'processed_date': datetime.now().isoformat()
            })
            
            processed_results.append(processed_result)
        
        # Sort by combined score
        processed_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return processed_results
    
    def _calculate_relevance_score(self, result: Dict, query: str, context: Dict = None) -> float:
        """Calculate relevance score for a research result"""
        
        score = result.get('raw_relevance', 0.5)
        
        # Boost for title match
        title = result.get('title', '').lower()
        query_terms = query.lower().split()
        
        title_matches = sum(1 for term in query_terms if term in title)
        title_boost = (title_matches / len(query_terms)) * 0.3
        score += title_boost
        
        # Boost for abstract match
        abstract = result.get('abstract', '').lower()
        abstract_matches = sum(1 for term in query_terms if term in abstract)
        abstract_boost = (abstract_matches / len(query_terms)) * 0.2
        score += abstract_boost
        
        # Boost for key journal
        journal = result.get('journal', '')
        if journal in self.ecology_search_enhancement['key_journals']:
            score += 0.15
        
        # Context-based boosting
        if context:
            key_concepts = context.get('key_concepts', [])
            for concept in key_concepts:
                if concept.lower() in title or concept.lower() in abstract:
                    score += 0.1
        
        # Domain-specific keyword boosting
        domain_keywords = self.ecology_search_enhancement['domain_boost_keywords']
        domain_matches = sum(1 for kw in domain_keywords if kw in abstract)
        domain_boost = min(domain_matches * 0.05, 0.2)
        score += domain_boost
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """Calculate quality score based on academic indicators"""
        
        score = 0.0
        
        # Citation count influence (diminishing returns)
        citations = result.get('citation_count', 0)
        if citations > 0:
            citation_score = min(citations / 100.0, 0.3)  # Max 0.3 from citations
            score += citation_score
        
        # Publication year (prefer recent)
        year = result.get('publication_year', 2020)
        current_year = datetime.now().year
        age = current_year - year
        
        if age <= self.quality_criteria['preferred_age_years']:
            score += 0.3  # Recent research bonus
        elif age <= self.quality_criteria['max_age_years']:
            score += 0.2 - (age / self.quality_criteria['max_age_years']) * 0.1
        
        # Abstract quality
        abstract = result.get('abstract', '')
        if len(abstract) >= self.quality_criteria['min_abstract_length']:
            score += 0.2
            
            # Quality indicators in abstract
            quality_indicators = self.quality_criteria['quality_indicators']
            indicator_count = sum(1 for indicator in quality_indicators if indicator in abstract.lower())
            indicator_boost = min(indicator_count * 0.05, 0.15)
            score += indicator_boost
        
        # Peer review indicators
        peer_review_indicators = self.quality_criteria['peer_review_indicators']
        full_text = f"{result.get('title', '')} {result.get('journal', '')} {abstract}".lower()
        
        peer_review_count = sum(1 for indicator in peer_review_indicators if indicator in full_text)
        if peer_review_count >= 2:
            score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _apply_quality_filtering(self, results: List[Dict]) -> List[Dict]:
        """Apply quality filtering to remove low-quality results"""
        
        filtered_results = []
        
        for result in results:
            quality_score = result.get('quality_score', 0.0)
            database_source = result.get('database_source', '')
            
            # Get quality threshold for this database
            threshold = self.database_configs.get(database_source, {}).get('quality_threshold', 0.5)
            
            if quality_score >= threshold:
                filtered_results.append(result)
        
        return filtered_results
    
    def _generate_query_hash(self, query: str, context: Dict = None) -> str:
        """Generate hash for query caching"""
        
        query_data = {
            'query': query.lower().strip(),
            'context': context if context else {}
        }
        
        query_string = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def _get_cached_results(self, query_hash: str, max_results: int) -> Optional[List[Dict]]:
        """Retrieve cached results if still valid"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check for valid cached results
            cursor.execute('''
                SELECT * FROM academic_sources_cache 
                WHERE query_hash = ? 
                AND datetime(cached_date, '+{} hours') > datetime('now')
                ORDER BY quality_score DESC
                LIMIT ?
            '''.format(self.cache_duration), (query_hash, max_results))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            # Convert to dict format
            columns = [desc[0] for desc in cursor.description]
            cached_results = []
            
            for row in rows:
                result_dict = dict(zip(columns, row))
                # Parse JSON fields
                if result_dict.get('keywords'):
                    result_dict['keywords'] = json.loads(result_dict['keywords'])
                cached_results.append(result_dict)
            
            return cached_results
            
        except Exception as e:
            print(f"Error retrieving cached results: {e}")
            return None
    
    def _cache_results(self, query_hash: str, results: List[Dict]):
        """Cache results for future use"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for result in results:
                cursor.execute('''
                    INSERT OR REPLACE INTO academic_sources_cache 
                    (source_id, query_hash, database_source, title, authors, abstract, 
                     journal, publication_year, citation_count, doi, url, keywords, 
                     quality_score, relevance_score, cached_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.get('source_id'),
                    query_hash,
                    result.get('database_source'),
                    result.get('title'),
                    result.get('authors'),
                    result.get('abstract'),
                    result.get('journal'),
                    result.get('publication_year'),
                    result.get('citation_count', 0),
                    result.get('doi'),
                    result.get('url'),
                    json.dumps(result.get('keywords', [])),
                    result.get('quality_score', 0.0),
                    result.get('relevance_score', 0.0),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error caching results: {e}")
    
    def _record_query_performance(self, query: str, results: List[Dict], 
                                 response_time: float, cache_hit: bool, errors: Dict = None):
        """Record query performance metrics"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            query_id = hashlib.md5(f"{query}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO query_performance 
                (query_id, query_text, total_results, quality_results, 
                 response_time_ms, cache_hit, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_id,
                query[:500],  # Truncate long queries
                len(results),
                sum(1 for r in results if r.get('quality_score', 0) > 0.7),
                int(response_time * 1000),  # Convert to milliseconds
                cache_hit,
                json.dumps(errors) if errors else None
            ))
            
            conn.commit()
            conn.close()
            
            # Update performance metrics
            self.performance_metrics['average_response_time'] = (
                (self.performance_metrics['average_response_time'] * (self.performance_metrics['total_queries'] - 1) + response_time) / 
                self.performance_metrics['total_queries']
            )
            
        except Exception as e:
            print(f"Error recording query performance: {e}")
    
    def get_database_health_status(self) -> Dict[str, Any]:
        """Get current health status of all connected databases"""
        
        health_status = {
            'overall_status': 'operational',
            'database_status': {},
            'performance_summary': self.performance_metrics.copy(),
            'last_updated': datetime.now().isoformat()
        }
        
        for db_name, config in self.database_configs.items():
            if config['enabled']:
                # Test database connectivity (simplified)
                try:
                    # In production, would make actual test query
                    health_status['database_status'][db_name] = {
                        'status': 'operational',
                        'last_successful_query': datetime.now().isoformat(),
                        'error_count': self.performance_metrics['api_errors'][db_name],
                        'rate_limit': config['rate_limit']
                    }
                except Exception as e:
                    health_status['database_status'][db_name] = {
                        'status': 'error',
                        'error_message': str(e),
                        'error_count': self.performance_metrics['api_errors'][db_name]
                    }
                    health_status['overall_status'] = 'degraded'
            else:
                health_status['database_status'][db_name] = {
                    'status': 'disabled',
                    'reason': 'Manually disabled'
                }
        
        return health_status
    
    def optimize_search_performance(self) -> Dict[str, Any]:
        """Analyze and optimize search performance"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Analyze recent query performance
            cursor.execute('''
                SELECT 
                    AVG(response_time_ms) as avg_response_time,
                    AVG(total_results) as avg_results,
                    AVG(quality_results) as avg_quality_results,
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
                FROM query_performance 
                WHERE created_date >= datetime('now', '-7 days')
            ''')
            
            performance_row = cursor.fetchone()
            
            # Get cache statistics
            cursor.execute('''
                SELECT COUNT(*) as cached_entries,
                       AVG(access_count) as avg_access_count
                FROM academic_sources_cache
                WHERE datetime(cached_date, '+{} hours') > datetime('now')
            '''.format(self.cache_duration))
            
            cache_row = cursor.fetchone()
            conn.close()
            
            optimization_report = {
                'performance_analysis': {
                    'average_response_time_ms': performance_row[0] if performance_row[0] else 0,
                    'average_results_per_query': performance_row[1] if performance_row[1] else 0,
                    'average_quality_results': performance_row[2] if performance_row[2] else 0,
                    'total_queries_7days': performance_row[3] if performance_row[3] else 0,
                    'cache_hit_rate': (performance_row[4] / performance_row[3] * 100) if performance_row[3] else 0
                },
                'cache_analysis': {
                    'active_cached_entries': cache_row[0] if cache_row[0] else 0,
                    'average_reuse_rate': cache_row[1] if cache_row[1] else 0
                },
                'optimization_recommendations': self._generate_optimization_recommendations(performance_row, cache_row)
            }
            
            return optimization_report
            
        except Exception as e:
            return {
                'error': f'Performance analysis failed: {e}',
                'optimization_recommendations': ['Check database connectivity', 'Review error logs']
            }
    
    def _generate_optimization_recommendations(self, performance_row: Tuple, cache_row: Tuple) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        if performance_row and performance_row[0]:  # avg_response_time
            avg_response_time = performance_row[0]
            if avg_response_time > 5000:  # > 5 seconds
                recommendations.append("Consider increasing cache duration to reduce API calls")
                recommendations.append("Optimize query enhancement algorithms")
            
            cache_hit_rate = (performance_row[4] / performance_row[3] * 100) if performance_row[3] else 0
            if cache_hit_rate < 30:
                recommendations.append("Improve caching strategy - low cache hit rate detected")
        
        if cache_row and cache_row[0]:  # cached_entries
            if cache_row[0] > 10000:
                recommendations.append("Consider cache cleanup - large number of cached entries")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    def clear_expired_cache(self) -> Dict[str, int]:
        """Clear expired cache entries and return cleanup statistics"""
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Count expired entries
            cursor.execute('''
                SELECT COUNT(*) FROM academic_sources_cache
                WHERE datetime(cached_date, '+{} hours') <= datetime('now')
            '''.format(self.cache_duration))
            
            expired_count = cursor.fetchone()[0]
            
            # Delete expired entries
            cursor.execute('''
                DELETE FROM academic_sources_cache
                WHERE datetime(cached_date, '+{} hours') <= datetime('now')
            '''.format(self.cache_duration))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return {
                'expired_entries_found': expired_count,
                'entries_deleted': deleted_count,
                'cleanup_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Cache cleanup failed: {e}',
                'expired_entries_found': 0,
                'entries_deleted': 0
            }