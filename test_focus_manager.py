"""
Test script for the Advanced Focus Manager
Tests rabbit-hole detection and contextual redirection
"""

import sys

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")

sys.modules['streamlit'] = MockStreamlit()

from components.focus_manager import FocusManager

def create_test_scenarios():
    """Create test scenarios for different types of conversations"""
    
    # Sample assignment question context
    sample_question = {
        'id': 'Q1',
        'title': 'Fragmentation vs Connectivity Analysis',
        'prompt': 'Define and contrast fragmentation versus connectivity using specific examples from the article.',
        'bloom_level': 'analyze',
        'key_concepts': ['fragmentation', 'connectivity', 'patch', 'corridor'],
        'required_evidence': 'Direct citations from text with page references',
        'tutoring_prompts': [
            'What specific evidence from the article supports your definition?',
            'How do these concepts differ in their ecological impacts?',
            'What examples demonstrate the relationship between these concepts?'
        ]
    }
    
    assignment_context = {
        'assignment_title': 'Landscape Fragmentation Analysis',
        'current_question': 'Q1',
        'total_word_count': '600-800 words',
        'completed_questions': [],
        'all_questions': [sample_question]
    }
    
    # Test scenarios with different drift types
    test_scenarios = [
        {
            "name": "Focused Response",
            "input": "The article defines fragmentation as the breaking up of continuous habitat. On page 15, the authors show that fragmented patches have 30% lower bird diversity.",
            "expected_drift_score": "low",
            "expected_recommendation": "continue",
            "chat_history": [
                {"role": "assistant", "content": "Let's start with Q1 about fragmentation vs connectivity."},
                {"role": "user", "content": "I'm looking at the definitions in the article."}
            ]
        },
        {
            "name": "Curiosity-Driven Rabbit Hole",
            "input": "Generally speaking, what about climate change? Tell me about how global warming affects all ecosystems in general.",
            "expected_drift_score": "high", 
            "expected_recommendation": "redirect",
            "chat_history": [
                {"role": "assistant", "content": "Let's focus on Q1 about fragmentation vs connectivity."},
                {"role": "user", "content": "I understand fragmentation breaks up habitat."},
                {"role": "assistant", "content": "Good! Now can you find specific evidence?"}
            ]
        },
        {
            "name": "Definition Seeking (Moderate)",
            "input": "What does biodiversity mean exactly? Can you define it for me?",
            "expected_drift_score": "moderate",
            "expected_recommendation": "gentle_nudge",
            "chat_history": [
                {"role": "assistant", "content": "We're working on fragmentation vs connectivity."},
                {"role": "user", "content": "I found some data about species diversity."}
            ]
        },
        {
            "name": "Meta-Question Avoidance",
            "input": "Why should I care about this? Does this even matter? What's the point of studying fragmentation anyway?",
            "expected_drift_score": "high",
            "expected_recommendation": "motivational_redirect",
            "chat_history": [
                {"role": "assistant", "content": "Let's analyze the evidence about fragmentation."},
                {"role": "user", "content": "This seems really complicated."}
            ]
        },
        {
            "name": "Circular Questioning",
            "input": "What about connectivity again? How does connectivity work? What is connectivity exactly?",
            "expected_drift_score": "moderate",
            "expected_recommendation": "progress_redirect",
            "chat_history": [
                {"role": "assistant", "content": "Connectivity refers to how patches are linked."},
                {"role": "user", "content": "What does connectivity mean?"},
                {"role": "assistant", "content": "It's about linkages between habitats."},
                {"role": "user", "content": "How does connectivity function?"},
                {"role": "assistant", "content": "It allows species movement between patches."}
            ]
        },
        {
            "name": "Bridge Opportunity",
            "input": "I'm curious about urban planning applications. How might this apply to city design?",
            "expected_drift_score": "moderate",
            "expected_recommendation": "bridge_redirect",
            "chat_history": [
                {"role": "assistant", "content": "Good work on finding fragmentation evidence."},
                {"role": "user", "content": "The article shows corridors help maintain connectivity."}
            ]
        }
    ]
    
    return test_scenarios, sample_question, assignment_context

def run_drift_analysis_tests():
    """Test the drift analysis functionality"""
    print("Testing Advanced Focus Manager - Drift Analysis")
    print("=" * 60)
    
    focus_manager = FocusManager()
    test_scenarios, sample_question, assignment_context = create_test_scenarios()
    
    results = {
        "total_tests": len(test_scenarios),
        "passed": 0,
        "failed": 0,
        "results": []
    }
    
    for scenario in test_scenarios:
        print(f"\nTesting: {scenario['name']}")
        print("-" * 40)
        print(f"Input: '{scenario['input'][:80]}...'")
        
        # Run drift analysis
        drift_analysis = focus_manager.analyze_conversation_drift(
            user_input=scenario['input'],
            chat_history=scenario['chat_history'],
            current_question=sample_question,
            assignment_context=assignment_context
        )
        
        print(f"Results:")
        print(f"  Drift Score: {drift_analysis['drift_score']:.3f}")
        print(f"  Drift Type: {drift_analysis['drift_type']}")
        print(f"  Recommendation: {drift_analysis['recommendation']}")
        print(f"  Confidence: {drift_analysis['confidence']:.3f}")
        
        # Show top indicators
        if drift_analysis['indicators']:
            print(f"  Top Indicators: {drift_analysis['indicators'][:2]}")
        if drift_analysis['focus_signals']:
            print(f"  Focus Signals: {drift_analysis['focus_signals'][:2]}")
        
        # Check if results match expectations
        score_category = "low" if drift_analysis['drift_score'] < 0.4 else "moderate" if drift_analysis['drift_score'] < 0.7 else "high"
        expected_score = scenario['expected_drift_score']
        expected_rec = scenario['expected_recommendation']
        actual_rec = drift_analysis['recommendation']
        
        score_match = score_category == expected_score
        rec_match = actual_rec == expected_rec or actual_rec in ['gentle_nudge', 'redirect', 'firm_redirect'] and expected_rec in ['redirect']
        
        if score_match and rec_match:
            print(f"  PASS: Score category and recommendation match expectations")
            results["passed"] += 1
        else:
            print(f"  FAIL: Expected {expected_score} score & {expected_rec}, got {score_category} & {actual_rec}")
            results["failed"] += 1
        
        results["results"].append({
            "name": scenario['name'],
            "expected_score": expected_score,
            "actual_score": score_category,
            "expected_rec": expected_rec,
            "actual_rec": actual_rec,
            "passed": score_match and rec_match
        })
    
    return results

def test_redirection_responses():
    """Test the redirection response generation"""
    print("\n\nTesting Redirection Response Generation")
    print("=" * 60)
    
    focus_manager = FocusManager()
    test_scenarios, sample_question, assignment_context = create_test_scenarios()
    
    # Test different redirection scenarios
    redirection_tests = [
        {
            "name": "Gentle Nudge Response",
            "drift_analysis": {
                "drift_score": 0.35,
                "drift_type": "slightly_unfocused", 
                "recommendation": "gentle_nudge",
                "confidence": 0.6,
                "indicators": ["curiosity_driven: what about"],
                "focus_signals": ["evidence_seeking: evidence"]
            }
        },
        {
            "name": "Strong Redirect Response",
            "drift_analysis": {
                "drift_score": 0.85,
                "drift_type": "rabbit_hole",
                "recommendation": "strong_redirect", 
                "confidence": 0.8,
                "indicators": ["meta_questions: why should i", "curiosity_driven: generally"],
                "focus_signals": []
            }
        },
        {
            "name": "Motivational Redirect",
            "drift_analysis": {
                "drift_score": 0.75,
                "drift_type": "significantly_off_topic",
                "recommendation": "motivational_redirect",
                "confidence": 0.7,
                "indicators": ["meta_questions: does this matter"],
                "focus_signals": []
            }
        }
    ]
    
    for test in redirection_tests:
        print(f"\nTesting: {test['name']}")
        print("-" * 30)
        
        response = focus_manager.generate_redirection_response(
            drift_analysis=test['drift_analysis'],
            current_question=sample_question,
            assignment_context=assignment_context,
            student_progress={'evidence_found': ['habitat fragmentation definition']}
        )
        
        print(f"Generated Response:")
        print(f"  Length: {len(response)} characters")
        print(f"  Contains Question ID: {'Q1' in response}")
        print(f"  Contains Assignment Context: {'fragmentation' in response.lower()}")
        print(f"  First 100 chars: '{response[:100]}...'")
        
        # Check response quality
        has_context = any(word in response.lower() for word in ['question', 'assignment', 'fragmentation', 'evidence'])
        appropriate_length = 50 < len(response) < 500
        
        if has_context and appropriate_length:
            print(f"  Response quality: Good")
        else:
            print(f"  Response quality: Needs improvement")

def test_intervention_logic():
    """Test the intervention decision logic"""
    print("\n\nTesting Intervention Decision Logic")
    print("=" * 60)
    
    focus_manager = FocusManager()
    
    intervention_tests = [
        {"drift_score": 0.2, "confidence": 0.8, "should_intervene": False, "urgency": "none"},
        {"drift_score": 0.4, "confidence": 0.5, "should_intervene": True, "urgency": "low"},
        {"drift_score": 0.6, "confidence": 0.7, "should_intervene": True, "urgency": "medium"},
        {"drift_score": 0.8, "confidence": 0.8, "should_intervene": True, "urgency": "high"},
        {"drift_score": 0.9, "confidence": 0.3, "should_intervene": False, "urgency": "none"},  # Low confidence
    ]
    
    passed = 0
    total = len(intervention_tests)
    
    for test in intervention_tests:
        analysis = {
            "drift_score": test["drift_score"],
            "confidence": test["confidence"],
            "recommendation": "redirect" if test["should_intervene"] else "continue"
        }
        
        should_intervene = focus_manager.should_intervene(analysis)
        urgency = focus_manager.get_intervention_urgency(analysis)
        
        intervention_match = should_intervene == test["should_intervene"]
        urgency_match = urgency == test["urgency"]
        
        status = "PASS" if intervention_match and urgency_match else "FAIL"
        print(f"{status}: Score {test['drift_score']:.1f}, Confidence {test['confidence']:.1f} -> "
              f"Intervene: {should_intervene}, Urgency: {urgency}")
        
        if intervention_match and urgency_match:
            passed += 1
    
    print(f"\nIntervention Logic: {passed}/{total} tests passed ({100*passed/total:.1f}%)")

def main():
    """Run all focus manager tests"""
    print("Advanced Focus Manager Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Drift Analysis
        results = run_drift_analysis_tests()
        
        # Test 2: Redirection Responses  
        test_redirection_responses()
        
        # Test 3: Intervention Logic
        test_intervention_logic()
        
        # Summary
        print(f"\n\nTEST SUMMARY")
        print("=" * 40)
        print(f"Drift Analysis Tests: {results['passed']}/{results['total_tests']} passed")
        print(f"Success Rate: {100 * results['passed'] / results['total_tests']:.1f}%")
        
        if results['passed'] >= results['total_tests'] * 0.8:  # 80% pass rate
            print("Focus Manager is working well!")
        else:
            print("Some improvements needed.")
            
        print("\nIndividual Test Results:")
        for result in results['results']:
            status = "PASS" if result['passed'] else "FAIL"
            print(f"  {status} {result['name']}")
        
    except Exception as e:
        print(f"\nTest suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()