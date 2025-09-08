"""
Simple test for Assignment Parser core functionality
"""
import json
import re

class SimpleAssignmentParser:
    def __init__(self):
        self.bloom_keywords = {
            "remember": ["define", "list", "identify", "name", "state", "describe", "recall"],
            "understand": ["explain", "summarize", "interpret", "classify", "compare", "contrast"],
            "apply": ["use", "apply", "demonstrate", "solve", "implement", "execute"],
            "analyze": ["analyze", "examine", "investigate", "categorize", "differentiate", "distinguish"],
            "evaluate": ["evaluate", "assess", "critique", "judge", "justify", "defend"],
            "create": ["create", "design", "construct", "develop", "formulate", "synthesize"]
        }
        
        self.question_patterns = [
            r'(?i)(?:\d+[\.:)]\s*)(.*?)(?=\n\s*\d+[\.:)]|$)',
            r'(?i)(?:^|\n)\s*([^.!?]*(?:analyze|explain|describe|discuss|evaluate)[^.!?]*\.?)'
        ]
    
    def extract_questions(self, text):
        questions = []
        for pattern in self.question_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                question = match.strip() if isinstance(match, str) else match[0].strip()
                if len(question) > 20 and question not in questions:
                    questions.append(question)
        return questions[:10]
    
    def classify_bloom_level(self, question_text):
        question_lower = question_text.lower()
        scores = {}
        for level, keywords in self.bloom_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[level] = score
        
        if not scores:
            if '?' in question_text and ('what' in question_lower or 'who' in question_lower):
                return 'remember'
            elif any(word in question_lower for word in ['analyze', 'examine', 'investigate']):
                return 'analyze'
            elif any(word in question_lower for word in ['explain', 'describe', 'discuss']):
                return 'understand'
            else:
                return 'apply'
        
        return max(scores, key=scores.get)

def test_parsing():
    print("Testing Assignment Parser Core Functions")
    print("=" * 50)
    
    sample_text = """
Assignment: Landscape Fragmentation Analysis

1. Define and contrast fragmentation versus connectivity. 
   Using specific examples from the article, explain how these concepts differ.

2. Analyze the relationship between patch size and species diversity described in the study. 
   What patterns did the researchers find? How do you evaluate their evidence?

3. The authors suggest several conservation strategies for fragmented landscapes. 
   Compare and contrast at least two approaches mentioned.

4. How does this study relate to broader landscape ecology principles? 
   Synthesize the findings with at least two other concepts.
"""
    
    parser = SimpleAssignmentParser()
    
    # Test question extraction
    print("\nExtracting questions...")
    questions = parser.extract_questions(sample_text)
    print(f"Found {len(questions)} questions:")
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}:")
        print(f"  Text: {question[:100]}...")
        
        # Test Bloom classification
        bloom_level = parser.classify_bloom_level(question)
        print(f"  Bloom Level: {bloom_level}")
        
    # Test specific classifications
    print("\nTesting Bloom Classification:")
    print("-" * 30)
    
    test_cases = [
        ("Define habitat fragmentation", "remember"),
        ("Explain the relationship between patch size and diversity", "understand"), 
        ("Analyze the patterns found in the research data", "analyze"),
        ("Evaluate the effectiveness of different strategies", "evaluate")
    ]
    
    correct = 0
    for question, expected in test_cases:
        classified = parser.classify_bloom_level(question)
        status = "PASS" if classified == expected else "FAIL"
        print(f"  {status}: '{question}' -> {classified} (expected: {expected})")
        if classified == expected:
            correct += 1
    
    print(f"\nClassification Accuracy: {correct}/{len(test_cases)} ({100*correct/len(test_cases):.1f}%)")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    test_parsing()