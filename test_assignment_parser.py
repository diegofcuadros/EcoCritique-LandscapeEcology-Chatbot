#!/usr/bin/env python3
"""
Test script for the AssignmentParser component
Tests parsing of sample assignment documents
"""

import os
import sys

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")

class MockDocx:
    class Document:
        def __init__(self, *args): pass
        @property
        def paragraphs(self): return [MockParagraph()]

class MockParagraph:
    text = "Sample paragraph text"

class MockPyPDF2:
    class PdfReader:
        def __init__(self, *args): 
            self.pages = [MockPage()]
    
class MockPage:
    def extract_text(self): return "Sample PDF text content"

# Add mocks to sys.modules
sys.modules['streamlit'] = MockStreamlit()
sys.modules['docx'] = MockDocx()
sys.modules['docx.Document'] = MockDocx.Document
sys.modules['PyPDF2'] = MockPyPDF2()

from components.assignment_parser import AssignmentParser

def create_sample_assignment_text():
    """Create a sample assignment document for testing"""
    return """
Assignment: Landscape Fragmentation Analysis
Word Count: 600-800 words

Learning Objectives:
- Understand the impacts of habitat fragmentation
- Analyze landscape connectivity patterns
- Evaluate conservation strategies

Questions:

1. Define and contrast fragmentation versus connectivity. 
   Using specific examples from the article, explain how these concepts differ and why both are important for landscape ecology. Support your answer with evidence from the text.

2. Analyze the relationship between patch size and species diversity described in the study. 
   What patterns did the researchers find? How do you evaluate the strength of their evidence? Discuss potential limitations of their approach.

3. The authors suggest several conservation strategies for fragmented landscapes. 
   Compare and contrast at least two approaches mentioned. Which do you think would be most effective in your local area and why?

4. How does this study relate to broader landscape ecology principles we've discussed in class? 
   Synthesize the findings with at least two other concepts from our course materials.

Evaluation Criteria:
- Use specific evidence from the article
- Demonstrate critical thinking 
- Make connections between concepts
- Write clearly and concisely
"""

def test_assignment_parser():
    """Test the assignment parser with sample data"""
    print("Testing Assignment Parser...")
    print("=" * 50)
    
    # Initialize parser
    parser = AssignmentParser()
    
    # Create sample content
    sample_text = create_sample_assignment_text()
    
    # Test text parsing
    print("\nSample Assignment Text:")
    print("-" * 30)
    print(sample_text[:300] + "..." if len(sample_text) > 300 else sample_text)
    
    # Parse the content
    try:
        print("\nParsing assignment...")
        parsed_data = parser._parse_text_content(sample_text, "socratic_analysis")
        
        print(f"Parsing successful!")
        print(f"Results Summary:")
        print(f"   - Title: {parsed_data.get('assignment_title', 'N/A')}")
        print(f"   - Word Count: {parsed_data.get('total_word_count', 'N/A')}")
        print(f"   - Questions Found: {len(parsed_data.get('questions', []))}")
        print(f"   - Workflow Steps: {len(parsed_data.get('workflow_steps', []))}")
        
        # Test question analysis
        print("\nQuestion Analysis:")
        print("-" * 30)
        for i, question in enumerate(parsed_data.get('questions', []), 1):
            print(f"Question {i}: {question.get('id', 'N/A')}")
            print(f"   Title: {question.get('title', 'N/A')}")
            print(f"   Bloom Level: {question.get('bloom_level', 'N/A')}")
            print(f"   Word Target: {question.get('word_target', 'N/A')}")
            print(f"   Evidence Required: {question.get('required_evidence', 'N/A')}")
            print(f"   Key Concepts: {', '.join(question.get('key_concepts', []))}")
            
            # Show tutoring prompts
            prompts = question.get('tutoring_prompts', [])
            if prompts:
                print(f"   Tutoring Prompts:")
                for prompt in prompts[:2]:  # Show first 2
                    print(f"     • {prompt}")
                if len(prompts) > 2:
                    print(f"     ... and {len(prompts)-2} more")
            print()
        
        # Test validation
        print("🔍 Validating parsed data...")
        is_valid, issues = parser.validate_parsed_assignment(parsed_data)
        
        if is_valid:
            print("✅ Validation passed!")
        else:
            print("⚠️ Validation issues:")
            for issue in issues:
                print(f"   • {issue}")
        
        # Test preview generation
        print("\n📋 Generated Preview:")
        print("-" * 30)
        preview = parser.generate_assignment_preview(parsed_data)
        print(preview[:500] + "..." if len(preview) > 500 else preview)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during parsing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_bloom_classification():
    """Test Bloom's taxonomy classification"""
    print("\n🎯 Testing Bloom's Taxonomy Classification...")
    print("=" * 50)
    
    parser = AssignmentParser()
    
    test_questions = [
        ("Define habitat fragmentation", "remember"),
        ("Explain the relationship between patch size and diversity", "understand"),
        ("Apply conservation principles to your local area", "apply"),
        ("Analyze the patterns found in the research data", "analyze"),  
        ("Evaluate the effectiveness of different conservation strategies", "evaluate"),
        ("Design a new landscape management approach", "create")
    ]
    
    correct = 0
    for question, expected in test_questions:
        classified = parser._classify_bloom_level(question)
        status = "✅" if classified == expected else "❌"
        print(f"{status} '{question[:40]}...' → {classified} (expected: {expected})")
        if classified == expected:
            correct += 1
    
    print(f"\n📊 Classification Accuracy: {correct}/{len(test_questions)} ({100*correct/len(test_questions):.1f}%)")

def test_evidence_extraction():
    """Test evidence requirement extraction"""
    print("\n🔍 Testing Evidence Extraction...")
    print("=" * 50)
    
    parser = AssignmentParser()
    
    test_cases = [
        "Cite specific examples from the text to support your argument",
        "Use data from Figure 3 to analyze the patterns",
        "Reference at least two studies mentioned in the article",
        "Provide quotes from the authors to demonstrate their position"
    ]
    
    for case in test_cases:
        evidence = parser._extract_evidence_requirements(case)
        print(f"Question: {case[:50]}...")
        print(f"Evidence Required: {evidence}")
        print()

if __name__ == "__main__":
    print("🚀 Assignment Parser Test Suite")
    print("=" * 60)
    
    # Run all tests
    success = True
    
    try:
        success &= test_assignment_parser()
        test_bloom_classification()
        test_evidence_extraction()
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("📄 Assignment parser is ready for use.")
        else:
            print("\n⚠️ Some tests had issues. Check the output above.")
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()