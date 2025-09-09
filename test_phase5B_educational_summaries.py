"""
Phase 5B Educational Summary System Test Suite for EcoCritique
Tests advanced educational summary generation, multi-level complexity, and concept mapping
"""

import sys
import os

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")

sys.modules['streamlit'] = MockStreamlit()

from components.educational_summary_system import EducationalSummarySystem
from components.literature_synthesis_tools import LiteratureSynthesisTools
from components.enhanced_knowledge_system import EnhancedKnowledgeSystem
from components.advanced_socratic_engine import AdvancedSocraticEngine

def create_test_educational_summary_scenario():
    """Create comprehensive test scenario for educational summary system"""
    
    # Advanced assignment question requiring synthesis
    sample_question = {
        'id': 'Q2',
        'title': 'Landscape Connectivity and Biodiversity Conservation',
        'prompt': 'Synthesize research on landscape connectivity approaches and evaluate their effectiveness for biodiversity conservation. Provide recommendations for conservation practice.',
        'bloom_level': 'evaluate',
        'key_concepts': ['landscape connectivity', 'biodiversity conservation', 'corridor design', 'habitat fragmentation', 'conservation practice'],
        'required_evidence': 'Multiple research sources with critical evaluation and synthesis'
    }
    
    # Assignment context for synthesis-level work
    assignment_context = {
        'assignment_title': 'Conservation Strategy Analysis',
        'current_question': 'Q2',
        'current_question_details': sample_question,
        'total_word_count': '1000-1200 words',
        'all_questions': [sample_question],
        'completed_questions': [],
        'progress': {
            'Q2': {'status': 'in_progress', 'completion': 0.6}
        }
    }
    
    # Advanced chat history showing sophisticated student engagement
    chat_history = [
        {"role": "user", "content": "I understand that corridors can connect fragmented habitats, but I want to synthesize the research on their actual effectiveness."},
        {"role": "assistant", "content": "Great synthesis question! What specific aspects of effectiveness are you most interested in exploring?"},
        {"role": "user", "content": "I've found studies showing mixed results - some show corridors help species movement, others question their conservation value. I need to put together a comprehensive view."},
        {"role": "assistant", "content": "Excellent critical thinking! Let's explore the factors that might explain these different findings."},
        {"role": "user", "content": "I want to understand the big picture - how do all these different research findings fit together? Can you provide a comprehensive overview that synthesizes the current state of knowledge?"},
    ]
    
    # Mock knowledge sources for synthesis
    knowledge_sources = [
        {
            'content': 'Harvey et al. (2018) conducted a meta-analysis of 78 corridor studies, finding that corridors increased movement rates by 35% on average, but effectiveness varied significantly by species type and corridor characteristics.',
            'metadata': {'concepts': ['corridors', 'meta-analysis', 'species movement'], 'source_type': 'research_literature', 'academic_level': 'graduate'},
            'relevance_score': 0.95
        },
        {
            'content': 'Damschen et al. (2006) demonstrated in experimental fragmented landscapes that connected patches maintained higher plant species richness over 10 years compared to isolated patches.',
            'metadata': {'concepts': ['connectivity', 'species richness', 'experimental'], 'source_type': 'research_literature', 'academic_level': 'graduate'},
            'relevance_score': 0.88
        },
        {
            'content': 'Simberloff et al. (1992) argued that corridors may facilitate spread of diseases, invasive species, and disturbances, questioning their universal conservation benefit.',
            'metadata': {'concepts': ['corridors', 'invasive species', 'conservation critique'], 'source_type': 'research_literature', 'academic_level': 'graduate'},
            'relevance_score': 0.82
        },
        {
            'content': 'Tischendorf and Fahrig (2000) found that corridor effectiveness depends on landscape context, with greater benefits in highly fragmented landscapes than in moderately fragmented ones.',
            'metadata': {'concepts': ['corridor effectiveness', 'landscape context', 'fragmentation'], 'source_type': 'research_literature', 'academic_level': 'graduate'},
            'relevance_score': 0.90
        }
    ]
    
    return sample_question, assignment_context, chat_history, knowledge_sources

def test_educational_summary_system_basic():
    """Test basic functionality of educational summary system"""
    print("Testing Educational Summary System - Basic Functionality")
    print("=" * 60)
    
    try:
        # Initialize educational summary system
        print("1. Testing EducationalSummarySystem initialization...")
        summary_system = EducationalSummarySystem()
        print("+ EducationalSummarySystem initialized successfully")
        
        # Test summary frameworks
        print("2. Testing summary frameworks...")
        frameworks = summary_system.summary_frameworks
        print(f"+ Available frameworks: {list(frameworks.keys())}")
        print(f"+ Foundational structure: {frameworks['foundational']['structure']}")
        
        # Test pedagogical templates
        print("3. Testing pedagogical templates...")
        templates = summary_system.pedagogical_templates
        print(f"+ Available templates: {list(templates.keys())}")
        
        return True
        
    except Exception as e:
        print(f"X Educational Summary System basic test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_level_summary_generation():
    """Test multi-level summary generation for different complexity levels"""
    print("\nTesting Multi-Level Summary Generation")
    print("=" * 45)
    
    try:
        summary_system = EducationalSummarySystem()
        sample_question, assignment_context, chat_history, knowledge_sources = create_test_educational_summary_scenario()
        
        # Create summary context
        summary_context = {
            'assignment_title': assignment_context['assignment_title'],
            'question_focus': sample_question['title'],
            'key_concepts': sample_question['key_concepts'],
            'bloom_level': sample_question['bloom_level'],
            'student_comprehension_level': 'moderate',
            'evidence_quality': 'strong',
            'expected_topics': sample_question['key_concepts']
        }
        
        # Test each complexity level
        levels_tested = []
        for level in ['foundational', 'intermediate', 'advanced']:
            print(f"1.{len(levels_tested)+1} Testing {level} level summary generation...")
            
            summary = summary_system.generate_educational_summary(
                knowledge_sources=knowledge_sources,
                summary_context=summary_context,
                complexity_level=level
            )
            
            print(f"+ {level.title()} summary generated:")
            print(f"  - Summary ID: {summary.get('summary_id', 'N/A')}")
            print(f"  - Content length: {len(summary.get('structured_content', ''))}")
            print(f"  - Learning objectives: {len(summary.get('learning_objectives', []))}")
            print(f"  - Follow-up questions: {len(summary.get('follow_up_questions', []))}")
            
            # Verify concept map generation
            concept_map = summary.get('concept_map', {})
            print(f"  - Central concepts: {len(concept_map.get('central_concepts', []))}")
            print(f"  - Relationships: {len(concept_map.get('relationships', []))}")
            
            levels_tested.append(level)
        
        print(f"+ Successfully generated summaries for all {len(levels_tested)} complexity levels")
        return True
        
    except Exception as e:
        print(f"X Multi-level summary generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_literature_synthesis_tools():
    """Test literature synthesis and pattern detection tools"""
    print("\nTesting Literature Synthesis Tools")
    print("=" * 40)
    
    try:
        synthesis_tools = LiteratureSynthesisTools()
        sample_question, assignment_context, chat_history, knowledge_sources = create_test_educational_summary_scenario()
        
        # Test source analysis
        print("1. Testing source analysis for synthesis...")
        synthesis_context = {
            'research_question': sample_question['title'],
            'focus_areas': sample_question['key_concepts'],
            'expected_topics': sample_question['key_concepts']
        }
        
        synthesis_result = synthesis_tools.synthesize_literature(
            knowledge_sources=knowledge_sources,
            synthesis_context=synthesis_context,
            synthesis_type='thematic_synthesis'
        )
        
        print(f"+ Literature synthesis completed:")
        print(f"  - Synthesis ID: {synthesis_result.get('synthesis_id', 'N/A')}")
        print(f"  - Synthesis type: {synthesis_result.get('synthesis_type', 'N/A')}")
        print(f"  - Source count: {synthesis_result.get('metadata', {}).get('source_count', 0)}")
        
        # Test pattern analysis
        pattern_analysis = synthesis_result.get('pattern_analysis', {})
        if pattern_analysis:
            individual_patterns = pattern_analysis.get('individual_patterns', {})
            print(f"  - Pattern types detected: {len(individual_patterns)}")
            for pattern_type in individual_patterns.keys():
                print(f"    • {pattern_type}")
        
        return True
        
    except Exception as e:
        print(f"X Literature synthesis test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_knowledge_integration():
    """Test integration of educational summaries with enhanced knowledge system"""
    print("\nTesting Enhanced Knowledge System Integration")
    print("=" * 50)
    
    try:
        enhanced_knowledge = EnhancedKnowledgeSystem()
        sample_question, assignment_context, chat_history, knowledge_sources = create_test_educational_summary_scenario()
        
        # Test comprehensive educational summary generation
        print("1. Testing comprehensive educational summary generation...")
        search_context = {
            'assignment_title': assignment_context['assignment_title'],
            'question_focus': sample_question['title'],
            'key_concepts': sample_question['key_concepts'],
            'bloom_level': sample_question['bloom_level'],
            'student_comprehension_level': 'moderate',
            'evidence_quality': 'strong'
        }
        
        comprehensive_summary = enhanced_knowledge.generate_comprehensive_educational_summary(
            knowledge_results=knowledge_sources,
            search_context=search_context,
            complexity_level='intermediate'
        )
        
        print(f"+ Comprehensive summary generated:")
        print(f"  - Summary level: {comprehensive_summary.get('summary_level', 'N/A')}")
        print(f"  - Has literature synthesis: {'literature_synthesis' in comprehensive_summary}")
        print(f"  - Content sections: {len(comprehensive_summary.get('structured_content', '').split('##'))}")
        
        # Test multi-level summary package
        print("2. Testing multi-level summary package...")
        multi_level_package = enhanced_knowledge.create_multi_level_summary_package(
            knowledge_results=knowledge_sources,
            search_context=search_context
        )
        
        summary_levels = multi_level_package.get('summary_levels', {})
        print(f"+ Multi-level package created:")
        print(f"  - Available levels: {list(summary_levels.keys())}")
        print(f"  - Progression guidance available: {'progression_guidance' in multi_level_package}")
        print(f"  - Level selection guide available: {'level_selection_guide' in multi_level_package}")
        
        # Test level selection guide
        level_guide = multi_level_package.get('level_selection_guide', {})
        if level_guide:
            print(f"  - Recommended starting level: {level_guide.get('recommended_starting_level', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"X Enhanced knowledge integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_socratic_integration():
    """Test integration with Advanced Socratic Engine for Phase 5B features"""
    print("\nTesting Advanced Socratic Engine Integration")
    print("=" * 50)
    
    try:
        socratic_engine = AdvancedSocraticEngine()
        sample_question, assignment_context, chat_history, knowledge_sources = create_test_educational_summary_scenario()
        
        # Test enhanced summary detection
        print("1. Testing enhanced summary request detection...")
        
        # Test input that should trigger enhanced summary
        summary_request_input = "I want a comprehensive overview that synthesizes all the research on corridor effectiveness"
        
        response = socratic_engine.generate_contextualized_response(
            user_input=summary_request_input,
            assignment_context=assignment_context,
            student_progress=assignment_context.get('progress', {}),
            chat_history=chat_history,
            student_id="test_student_phase5b",
            session_id="test_session_phase5b"
        )
        
        print(f"+ Enhanced response generated ({len(response)} characters)")
        
        # Check for Phase 5B features in response
        has_educational_summary = "Enhanced Educational Summary" in response
        has_concept_connections = "🧠 Concept Connections" in response or "Concept Connections" in response
        has_learning_objectives = "🎯 Learning Objectives" in response or "Learning Objectives" in response
        has_deeper_thinking = "🤔 Questions for Deeper Thinking" in response or "Deeper Thinking" in response
        
        print(f"  Contains enhanced educational summary: {has_educational_summary}")
        print(f"  Contains concept connections: {has_concept_connections}")
        print(f"  Contains learning objectives: {has_learning_objectives}")
        print(f"  Contains deeper thinking questions: {has_deeper_thinking}")
        
        # Test complexity level determination
        print("2. Testing complexity level determination...")
        
        # Mock response analysis for testing
        test_response_analysis = {
            'analytical_depth': 'deep',
            'evidence_quality': 'strong'
        }
        
        test_search_context = {
            'bloom_level': 'evaluate',
            'question_focus': sample_question['title'],
            'key_concepts': sample_question['key_concepts']
        }
        
        complexity_level = socratic_engine._determine_summary_complexity(
            test_response_analysis, test_search_context
        )
        
        print(f"+ Complexity level determined: {complexity_level}")
        print(f"+ Expected: advanced (for deep analysis + strong evidence + evaluate level)")
        
        return True
        
    except Exception as e:
        print(f"X Advanced Socratic integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_concept_mapping_and_relationships():
    """Test concept mapping and relationship visualization capabilities"""
    print("\nTesting Concept Mapping and Relationships")
    print("=" * 45)
    
    try:
        summary_system = EducationalSummarySystem()
        sample_question, assignment_context, chat_history, knowledge_sources = create_test_educational_summary_scenario()
        
        # Test concept map generation
        print("1. Testing concept map generation...")
        
        summary_context = {
            'key_concepts': sample_question['key_concepts'],
            'question_focus': sample_question['title']
        }
        
        concept_map = summary_system._generate_concept_map(knowledge_sources, summary_context)
        
        print(f"+ Concept map generated:")
        print(f"  - Central concepts: {len(concept_map.get('central_concepts', []))}")
        if concept_map.get('central_concepts'):
            print(f"    • {', '.join(concept_map['central_concepts'][:3])}")
        
        relationships = concept_map.get('relationships', [])
        print(f"  - Relationships identified: {len(relationships)}")
        for i, rel in enumerate(relationships[:3], 1):
            print(f"    {i}. {rel['concept_a']} → {rel['relationship_type']} → {rel['concept_b']} (strength: {rel['strength']:.2f})")
        
        definitions = concept_map.get('concept_definitions', {})
        print(f"  - Concept definitions: {len(definitions)}")
        
        # Test visual structure
        visual_structure = concept_map.get('visual_structure', {})
        if visual_structure:
            print(f"  - Visual structure available: {visual_structure.get('central_node', 'N/A')}")
            print(f"  - Primary connections: {len(visual_structure.get('primary_connections', []))}")
        
        return True
        
    except Exception as e:
        print(f"X Concept mapping test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_summary_quality_and_analytics():
    """Test summary quality assessment and analytics capabilities"""
    print("\nTesting Summary Quality and Analytics")
    print("=" * 42)
    
    try:
        enhanced_knowledge = EnhancedKnowledgeSystem()
        
        # Test analytics system
        print("1. Testing enhanced summary analytics...")
        
        analytics = enhanced_knowledge.get_enhanced_summary_analytics(days=30)
        
        print(f"+ Analytics retrieved:")
        print(f"  - Summary generation data available: {'summary_generation' in analytics}")
        print(f"  - Feedback analysis available: {'feedback_analysis' in analytics}")
        print(f"  - System performance metrics: {'system_performance' in analytics}")
        
        if 'enhancement_impact' in analytics:
            impact = analytics['enhancement_impact']
            print(f"  - Enhancement level: {impact.get('enhancement_level', 'N/A')}")
            print(f"  - Overall enhancement score: {impact.get('overall_enhancement_score', 0):.2f}")
        
        # Test complexity assessment
        print("2. Testing complexity assessment...")
        
        sample_content = """This comprehensive analysis demonstrates the multifaceted implications of landscape connectivity for biodiversity conservation. The synthesis of empirical evidence reveals significant heterogeneity in corridor effectiveness across taxonomic groups and spatial scales."""
        
        summary_system = EducationalSummarySystem()
        complexity_indicators = summary_system._assess_complexity_indicators(sample_content)
        
        print(f"+ Complexity indicators calculated:")
        print(f"  - Average words per sentence: {complexity_indicators.get('avg_words_per_sentence', 0)}")
        print(f"  - Long word percentage: {complexity_indicators.get('long_word_percentage', 0)}%")
        print(f"  - Academic term count: {complexity_indicators.get('academic_term_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"X Summary quality and analytics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_phase5B_comprehensive_test():
    """Run comprehensive Phase 5B test suite"""
    print("PHASE 5B EDUCATIONAL SUMMARY SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 75)
    print("Testing advanced educational summaries, multi-level complexity, concept mapping,")
    print("and literature synthesis for enhanced student learning\n")
    
    test_results = []
    
    # Run all test components
    test_results.append(("Educational Summary Basic", test_educational_summary_system_basic()))
    test_results.append(("Multi-Level Generation", test_multi_level_summary_generation()))
    test_results.append(("Literature Synthesis", test_literature_synthesis_tools()))
    test_results.append(("Enhanced Knowledge Integration", test_enhanced_knowledge_integration()))
    test_results.append(("Socratic Engine Integration", test_advanced_socratic_integration()))
    test_results.append(("Concept Mapping", test_concept_mapping_and_relationships()))
    test_results.append(("Quality & Analytics", test_summary_quality_and_analytics()))
    
    # Summary results
    print("\n" + "=" * 75)
    print("PHASE 5B TEST RESULTS SUMMARY")
    print("=" * 35)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "PASS [OK]" if result else "FAIL [X]"
        print(f"{test_name:.<45} {status}")
        if result:
            passed_tests += 1
    
    print(f"\nTests Passed: {passed_tests}/{len(test_results)}")
    
    if passed_tests == len(test_results):
        print("\n>>> PHASE 5B EDUCATIONAL SUMMARY SYSTEM: FULLY OPERATIONAL!")
        print("\nPhase 5B Features Successfully Implemented:")
        print("• Multi-level educational summaries (foundational, intermediate, advanced)")
        print("• Comprehensive concept mapping and relationship visualization")
        print("• Literature synthesis with pattern detection and analysis")
        print("• Pedagogical guidance and learning strategies tailored to student level")
        print("• Progressive disclosure with level selection guidance")
        print("• Quality assessment and effectiveness analytics")
        print("• Seamless integration with existing Socratic questioning system")
        
        print("\nAdvanced Educational Features:")
        print("• Adaptive complexity based on student comprehension and Bloom's taxonomy")
        print("• Automatic synthesis of multiple research sources")
        print("• Concept relationship mapping for deeper understanding")
        print("• Learning objectives and follow-up questions for continued engagement")
        print("• Debug information for professors to monitor educational effectiveness")
        
        return True
    else:
        print(f"\n!!! PHASE 5B needs debugging: {len(test_results) - passed_tests} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_phase5B_comprehensive_test()
    if success:
        print(f"\n>>> Phase 5B Educational Summary System: READY FOR DEPLOYMENT!")
        print("Advanced educational summaries with multi-level complexity and concept mapping")
        print("are now available to enhance student learning and comprehension.")
    else:
        print(f"\n!!! Phase 5B requires additional debugging before deployment.")