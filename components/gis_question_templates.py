"""
GIS and Spatial Analysis Question Templates - Dynamic question generation based on article content
"""

import json
import re
from typing import Dict, List, Any, Optional
import streamlit as st

class GISQuestionTemplateSystem:
    """Generates article-specific questions focused on GIS and spatial analysis concepts"""
    
    def __init__(self):
        # GIS method categories and their associated concepts
        self.gis_method_categories = {
            "remote_sensing": {
                "keywords": ["satellite", "landsat", "modis", "sentinel", "aerial", "lidar", "radar", "multispectral", "hyperspectral"],
                "concepts": ["image classification", "change detection", "vegetation indices", "spectral signatures", "pixel-based analysis"],
                "scales": ["fine resolution", "coarse resolution", "temporal resolution", "radiometric resolution"]
            },
            "vector_analysis": {
                "keywords": ["polygon", "point", "line", "shapefile", "topology", "buffer", "overlay", "intersection", "union"],
                "concepts": ["spatial joins", "proximity analysis", "network analysis", "geocoding", "digitizing"],
                "scales": ["parcel level", "watershed level", "administrative boundaries"]
            },
            "raster_analysis": {
                "keywords": ["raster", "grid", "cell", "dem", "interpolation", "kriging", "idw", "surface analysis"],
                "concepts": ["map algebra", "focal operations", "zonal statistics", "cost-distance", "viewshed"],
                "scales": ["cell size", "pixel resolution", "grid extent"]
            },
            "landscape_metrics": {
                "keywords": ["fragstats", "patch", "connectivity", "fragmentation", "landscape index", "contagion"],
                "concepts": ["patch size distribution", "edge effects", "core area", "shape complexity", "aggregation"],
                "scales": ["patch scale", "class scale", "landscape scale"]
            },
            "spatial_statistics": {
                "keywords": ["autocorrelation", "clustering", "hotspot", "getis-ord", "moran", "semivariogram"],
                "concepts": ["spatial dependence", "spatial heterogeneity", "scale effects", "modifiable areal unit problem"],
                "scales": ["neighborhood effects", "regional patterns", "spatial lag"]
            }
        }
        
        # Question templates organized by cognitive level
        self.question_templates = {
            "comprehension": {
                "data_identification": [
                    "What type of spatial data was used in this study: {data_types}?",
                    "Can you identify the spatial resolution of the {data_source} used?",
                    "What coordinate system or projection was mentioned for the {study_area}?",
                    "How was the study area boundary defined in this research?"
                ],
                "method_identification": [
                    "What GIS operations were performed on the {data_type} data?",
                    "Can you describe the {gis_method} approach used by the researchers?",
                    "What software or tools were mentioned for the spatial analysis?",
                    "How did the authors define their spatial units of analysis?"
                ],
                "scale_identification": [
                    "At what spatial scale was this analysis conducted?",
                    "What temporal scale does this study cover?",
                    "How does the grain size relate to the ecological processes studied?",
                    "What is the extent of the study area in relation to the research question?"
                ]
            },
            "analysis": {
                "method_evaluation": [
                    "Why do you think the researchers chose {gis_method} over other spatial analysis techniques?",
                    "How might the choice of {spatial_resolution} have influenced the results?",
                    "What are the advantages and limitations of using {data_source} for this type of analysis?",
                    "How does the {spatial_scale} of analysis relate to the ecological processes being studied?"
                ],
                "pattern_analysis": [
                    "What spatial patterns do you observe in the {landscape_feature} data?",
                    "How do the {landscape_metrics} values relate to the ecological patterns described?",
                    "What might explain the spatial distribution of {ecological_variable} shown in the maps?",
                    "How do edge effects manifest in the spatial patterns you see?"
                ],
                "scale_effects": [
                    "How might the results change if the analysis was conducted at a finer spatial resolution?",
                    "What scale-dependent relationships do you identify in this study?",
                    "How does the modifiable areal unit problem potentially affect these findings?",
                    "What would happen if the temporal scale of analysis was extended or reduced?"
                ]
            },
            "synthesis": {
                "method_integration": [
                    "How do the GIS methods used here complement the field data collection?",
                    "Can you connect the {spatial_analysis} results to landscape ecology theory?",
                    "How might these spatial analysis techniques be combined with {other_methods}?",
                    "What role does {gis_concept} play in understanding landscape connectivity?"
                ],
                "cross_scale_synthesis": [
                    "How do local-scale processes observed here scale up to landscape-level patterns?",
                    "Can you synthesize the fine-scale and broad-scale findings in this study?",
                    "How do the spatial patterns relate to the temporal dynamics described?",
                    "What connections do you see between {spatial_pattern} and ecological function?"
                ],
                "concept_integration": [
                    "How does this spatial analysis inform habitat fragmentation theory?",
                    "Can you relate these GIS findings to metapopulation dynamics?",
                    "How do the landscape metrics connect to conservation planning principles?",
                    "What implications do these spatial patterns have for ecosystem services?"
                ]
            },
            "evaluation": {
                "methodological_critique": [
                    "What are the key limitations of the GIS methodology used in this study?",
                    "How might uncertainty in the {spatial_data} affect the conclusions?",
                    "What alternative spatial analysis approaches could strengthen this research?",
                    "How would you validate the accuracy of the {gis_analysis} results?"
                ],
                "assumption_evaluation": [
                    "What assumptions about spatial relationships are embedded in this analysis?",
                    "How realistic is the assumption that {spatial_assumption}?",
                    "What ecological processes might be oversimplified by this spatial model?",
                    "How might spatial autocorrelation affect the statistical analyses?"
                ],
                "application_evaluation": [
                    "How transferable are these GIS methods to other landscape types?",
                    "What modifications would be needed to apply this approach in {different_context}?",
                    "How could these spatial analysis results inform landscape management decisions?",
                    "What additional spatial data would strengthen the management recommendations?"
                ]
            }
        }
        
        # Context-specific question modifiers
        self.context_modifiers = {
            "forest": {
                "features": ["canopy cover", "forest fragments", "edge density", "old-growth patches"],
                "processes": ["succession", "disturbance", "carbon storage", "biodiversity"]
            },
            "urban": {
                "features": ["built area", "green spaces", "impervious surfaces", "urban heat islands"], 
                "processes": ["urban sprawl", "habitat fragmentation", "pollution", "microclimate"]
            },
            "agricultural": {
                "features": ["field boundaries", "crop types", "hedgerows", "drainage networks"],
                "processes": ["land use change", "erosion", "runoff", "pesticide drift"]
            },
            "wetland": {
                "features": ["water bodies", "wetland boundaries", "hydrological connectivity", "vegetation zones"],
                "processes": ["hydrology", "water quality", "waterfowl habitat", "flood control"]
            },
            "coastal": {
                "features": ["shoreline", "dunes", "estuaries", "tidal zones"],
                "processes": ["sea level rise", "erosion", "storm surge", "habitat migration"]
            }
        }
    
    def generate_article_questions(self, article_content: str, article_title: str, 
                                 cognitive_level: str = "analysis") -> List[Dict[str, Any]]:
        """Generate article-specific GIS questions based on content analysis"""
        
        # Analyze article content for GIS methods and concepts
        content_analysis = self._analyze_gis_content(article_content)
        
        # Identify landscape context
        landscape_context = self._identify_landscape_context(article_content)
        
        # Generate targeted questions
        questions = []
        
        if content_analysis["gis_methods"]:
            questions.extend(self._generate_method_questions(
                content_analysis, cognitive_level, landscape_context, article_title
            ))
        
        if content_analysis["spatial_concepts"]:
            questions.extend(self._generate_concept_questions(
                content_analysis, cognitive_level, landscape_context
            ))
        
        if content_analysis["scale_indicators"]:
            questions.extend(self._generate_scale_questions(
                content_analysis, cognitive_level
            ))
        
        # Add landscape-specific questions
        if landscape_context:
            questions.extend(self._generate_landscape_specific_questions(
                landscape_context, cognitive_level, content_analysis
            ))
        
        # Ensure we have a good mix of questions
        if not questions:
            questions = self._generate_fallback_questions(cognitive_level, article_title)
        
        return questions[:8]  # Return up to 8 targeted questions
    
    def _analyze_gis_content(self, content: str) -> Dict[str, List[str]]:
        """Analyze article content for GIS methods and concepts"""
        
        content_lower = content.lower()
        analysis = {
            "gis_methods": [],
            "spatial_concepts": [],
            "scale_indicators": [],
            "data_sources": [],
            "software_mentioned": []
        }
        
        # Identify GIS methods
        for method_category, method_info in self.gis_method_categories.items():
            for keyword in method_info["keywords"]:
                if keyword in content_lower:
                    analysis["gis_methods"].append(method_category)
                    break
        
        # Identify spatial concepts
        spatial_concept_patterns = [
            "spatial pattern", "spatial distribution", "spatial autocorrelation",
            "landscape fragmentation", "connectivity", "patch size", "edge effect",
            "spatial scale", "resolution", "extent", "grain size"
        ]
        
        for concept in spatial_concept_patterns:
            if concept in content_lower:
                analysis["spatial_concepts"].append(concept)
        
        # Identify scale indicators
        scale_patterns = [
            r"(\d+)\s*m\s+resolution", r"(\d+)\s*km\s*x\s*(\d+)\s*km",
            r"(\d+)\s*meter", r"(\d+)\s*kilometer", "fine scale", "broad scale",
            "local scale", "regional scale", "landscape scale"
        ]
        
        for pattern in scale_patterns:
            matches = re.finditer(pattern, content_lower)
            for match in matches:
                analysis["scale_indicators"].append(match.group())
        
        # Identify data sources
        data_source_patterns = [
            "landsat", "modis", "sentinel", "lidar", "aerial photography",
            "digital elevation model", "dem", "land cover", "field survey"
        ]
        
        for source in data_source_patterns:
            if source in content_lower:
                analysis["data_sources"].append(source)
        
        # Identify software
        software_patterns = ["arcgis", "qgis", "grass", "r", "erdas", "envi", "fragstats"]
        
        for software in software_patterns:
            if software in content_lower:
                analysis["software_mentioned"].append(software)
        
        return analysis
    
    def _identify_landscape_context(self, content: str) -> Optional[str]:
        """Identify the primary landscape context of the study"""
        
        content_lower = content.lower()
        context_scores = {}
        
        for context, context_info in self.context_modifiers.items():
            score = 0
            for feature in context_info["features"]:
                if feature in content_lower:
                    score += 1
            for process in context_info["processes"]:
                if process in content_lower:
                    score += 1
            
            if score > 0:
                context_scores[context] = score
        
        # Return the context with the highest score
        if context_scores:
            return max(context_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _generate_method_questions(self, content_analysis: Dict, cognitive_level: str, 
                                 landscape_context: Optional[str], article_title: str) -> List[Dict[str, Any]]:
        """Generate questions focused on GIS methods"""
        
        questions = []
        templates = self.question_templates.get(cognitive_level, {})
        
        for method in content_analysis["gis_methods"][:3]:  # Top 3 methods
            method_info = self.gis_method_categories[method]
            
            # Method identification/evaluation questions
            if "method_identification" in templates:
                for template in templates["method_identification"][:2]:
                    question = template.format(
                        gis_method=method.replace("_", " "),
                        data_type="spatial",
                        study_area=landscape_context or "study area"
                    )
                    questions.append({
                        "question": question,
                        "category": "gis_methods",
                        "method_focus": method,
                        "cognitive_level": cognitive_level
                    })
            
            if "method_evaluation" in templates:
                for template in templates["method_evaluation"][:2]:
                    question = template.format(
                        gis_method=method.replace("_", " "),
                        spatial_resolution="spatial resolution",
                        data_source="remote sensing data" if method == "remote_sensing" else "GIS data",
                        spatial_scale="landscape scale"
                    )
                    questions.append({
                        "question": question,
                        "category": "method_evaluation", 
                        "method_focus": method,
                        "cognitive_level": cognitive_level
                    })
        
        return questions[:4]  # Limit to 4 method questions
    
    def _generate_concept_questions(self, content_analysis: Dict, cognitive_level: str,
                                  landscape_context: Optional[str]) -> List[Dict[str, Any]]:
        """Generate questions focused on spatial concepts"""
        
        questions = []
        templates = self.question_templates.get(cognitive_level, {})
        
        # Pattern analysis questions
        if "pattern_analysis" in templates and content_analysis["spatial_concepts"]:
            for template in templates["pattern_analysis"][:2]:
                concept = content_analysis["spatial_concepts"][0]
                landscape_feature = "habitat" if landscape_context else "landscape feature"
                
                question = template.format(
                    landscape_feature=landscape_feature,
                    landscape_metrics="connectivity metrics",
                    ecological_variable="species distribution"
                )
                questions.append({
                    "question": question,
                    "category": "spatial_concepts",
                    "concept_focus": concept,
                    "cognitive_level": cognitive_level
                })
        
        # Concept integration questions
        if "concept_integration" in templates:
            for template in templates["concept_integration"][:2]:
                questions.append({
                    "question": template,
                    "category": "concept_integration",
                    "cognitive_level": cognitive_level
                })
        
        return questions
    
    def _generate_scale_questions(self, content_analysis: Dict, cognitive_level: str) -> List[Dict[str, Any]]:
        """Generate questions focused on spatial and temporal scale"""
        
        questions = []
        templates = self.question_templates.get(cognitive_level, {})
        
        if "scale_identification" in templates:
            for template in templates["scale_identification"][:2]:
                questions.append({
                    "question": template,
                    "category": "scale_analysis",
                    "cognitive_level": cognitive_level
                })
        
        if "scale_effects" in templates and content_analysis["scale_indicators"]:
            for template in templates["scale_effects"][:2]:
                questions.append({
                    "question": template,
                    "category": "scale_effects",
                    "cognitive_level": cognitive_level
                })
        
        return questions
    
    def _generate_landscape_specific_questions(self, landscape_context: str, cognitive_level: str,
                                             content_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate questions specific to the landscape context"""
        
        questions = []
        context_info = self.context_modifiers[landscape_context]
        
        # Context-specific spatial questions
        context_questions = {
            "forest": [
                "How do the spatial patterns of forest fragmentation relate to edge effects?",
                "What role does canopy cover spatial variability play in habitat quality?",
                "How might forest patch connectivity affect species dispersal?"
            ],
            "urban": [
                "How does the spatial configuration of green spaces affect urban biodiversity?",
                "What spatial factors influence urban heat island intensity?",
                "How do impervious surface patterns relate to stormwater management?"
            ],
            "agricultural": [
                "How does field size and shape affect edge-to-area ratios?",
                "What spatial factors influence pesticide drift between fields?",
                "How do hedgerow networks provide landscape connectivity?"
            ],
            "wetland": [
                "How does wetland spatial connectivity affect water quality functions?",
                "What spatial factors determine waterfowl habitat quality?",
                "How do hydrological networks influence nutrient transport?"
            ],
            "coastal": [
                "How might sea level rise affect the spatial distribution of coastal habitats?",
                "What spatial factors influence dune stability and migration?",
                "How does shoreline configuration affect storm surge impacts?"
            ]
        }
        
        if landscape_context in context_questions:
            for question in context_questions[landscape_context][:3]:
                questions.append({
                    "question": question,
                    "category": "landscape_specific",
                    "landscape_context": landscape_context,
                    "cognitive_level": cognitive_level
                })
        
        return questions
    
    def _generate_fallback_questions(self, cognitive_level: str, article_title: str) -> List[Dict[str, Any]]:
        """Generate general GIS questions when specific content analysis is limited"""
        
        fallback_questions = {
            "comprehension": [
                f"What spatial data types were used in the '{article_title}' study?",
                "Can you identify any spatial scales mentioned in this research?",
                "What GIS software or tools were referenced in the methodology?",
                "How was the study area spatially defined and bounded?"
            ],
            "analysis": [
                "How do the spatial analysis methods relate to the research questions?",
                "What spatial relationships are explored in this study?",
                "How might the choice of spatial resolution affect the results?",
                "What spatial patterns emerge from the analysis?"
            ],
            "synthesis": [
                "How do the spatial findings connect to landscape ecology principles?",
                "Can you integrate the GIS results with the ecological theory discussed?",
                "How might these spatial analysis techniques apply to other landscape types?",
                "What role does spatial scale play in interpreting the results?"
            ],
            "evaluation": [
                "What are the limitations of the spatial analysis approach used?",
                "How might spatial uncertainty affect the study conclusions?",
                "What alternative GIS methods could strengthen this research?",
                "How transferable are these spatial analysis results to other contexts?"
            ]
        }
        
        questions = []
        for question in fallback_questions.get(cognitive_level, fallback_questions["analysis"]):
            questions.append({
                "question": question,
                "category": "general_gis",
                "cognitive_level": cognitive_level
            })
        
        return questions
    
    def get_question_by_context(self, gis_method: str, landscape_context: str, 
                               cognitive_level: str = "analysis") -> Dict[str, Any]:
        """Get a specific question based on GIS method and landscape context"""
        
        method_info = self.gis_method_categories.get(gis_method, {})
        context_info = self.context_modifiers.get(landscape_context, {})
        templates = self.question_templates.get(cognitive_level, {})
        
        if not method_info or not templates:
            return self._generate_fallback_questions(cognitive_level, "current article")[0]
        
        # Generate a context-specific question
        if cognitive_level == "analysis" and "pattern_analysis" in templates:
            template = templates["pattern_analysis"][0]
            landscape_feature = context_info.get("features", ["landscape feature"])[0]
            
            question = template.format(
                landscape_feature=landscape_feature,
                landscape_metrics="connectivity index",
                ecological_variable="species abundance"
            )
            
            return {
                "question": question,
                "category": "contextual",
                "method_focus": gis_method,
                "landscape_context": landscape_context,
                "cognitive_level": cognitive_level
            }
        
        return self._generate_fallback_questions(cognitive_level, "current article")[0]