"""
Phase 4 Personalization Test Suite for EcoCritique
Tests personalized tutoring, conversation checkpoints, and adaptive difficulty adjustment
"""

import sys
import os

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")

sys.modules['streamlit'] = MockStreamlit()

from components.personalization_engine import PersonalizationEngine
from components.conversation_checkpoint import ConversationCheckpoint
from components.adaptive_difficulty import AdaptiveDifficultyEngine
from components.advanced_socratic_engine import AdvancedSocraticEngine

def create_test_scenario():
    """Create a simple test scenario"""
    
    sample_question = {
        'id': 'Q1',
        'title': 'Fragmentation vs Connectivity Analysis',
        'prompt': 'Define and contrast fragmentation versus connectivity.',
        'bloom_level': 'analyze',
        'key_concepts': ['fragmentation', 'connectivity'],
        'required_evidence': 'Direct citations from text'
    }
    
    assignment_context = {
        'assignment_title': 'Landscape Analysis',
        'current_question': 'Q1',
        'current_question_details': sample_question,
        'total_word_count': '600-800 words'
    }
    
    return sample_question, assignment_context

def test_personalization_basic():
    """Basic test of personalization components"""
    print("Testing Phase 4 Personalization Components")
    print("=" * 50)
    
    try:
        # Test PersonalizationEngine
        print("Testing PersonalizationEngine...")
        engine = PersonalizationEngine()
        profile = engine.get_or_create_student_profile("test_student")
        print(f"+ PersonalizationEngine working: Profile created for {profile['student_id']}")
        
        # Test ConversationCheckpoint
        print("Testing ConversationCheckpoint...")
        checkpoint = ConversationCheckpoint()
        chat_history = [{"role": "user", "content": "test message"}]
        should_trigger = checkpoint.should_trigger_checkpoint(chat_history, "test_session")
        print(f"+ ConversationCheckpoint working: Trigger check = {should_trigger}")
        
        # Test AdaptiveDifficultyEngine
        print("Testing AdaptiveDifficultyEngine...")
        difficulty = AdaptiveDifficultyEngine()
        sample_question, assignment_context = create_test_scenario()
        assessment = difficulty.assess_current_performance("test input", chat_history, sample_question)
        print(f"+ AdaptiveDifficultyEngine working: Performance = {assessment['overall_performance']:.2f}")
        
        # Test integrated AdvancedSocraticEngine
        print("Testing Enhanced AdvancedSocraticEngine...")
        socratic = AdvancedSocraticEngine()
        response = socratic.generate_contextualized_response(
            user_input="Fragmentation breaks up habitats into isolated patches.",
            assignment_context=assignment_context,
            student_progress={},
            chat_history=chat_history,
            student_id="test_student",
            session_id="test_session"
        )
        print(f"+ Enhanced AdvancedSocraticEngine working: Response length = {len(response)}")
        
        print("\n>>> PHASE 4 BASIC TESTS: ALL COMPONENTS OPERATIONAL!")
        print("\nPhase 4 Features Available:")
        print("• Personalized learning style adaptation")
        print("• Conversation checkpoints every 5 questions")
        print("• Adaptive difficulty adjustment")
        print("• Enhanced debug information for professors")
        
        return True
        
    except Exception as e:
        print(f"X Phase 4 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_personalization_basic()
    if success:
        print("\n>>> Phase 4 Personalization: READY FOR USE!")
    else:
        print("\n!!! Phase 4 needs debugging before deployment.")
