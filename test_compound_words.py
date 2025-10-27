#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test compound words và multi-word expressions trong tiếng Việt
"""

from EnhancedSearchEngine_Fixed import FixedEnhancedSearchEngine

def test_compound_words():
    """Test các từ ghép tiếng Việt"""
    
    print("🇻🇳 TESTING VIETNAMESE COMPOUND WORDS")
    print("=" * 60)
    
    engine = FixedEnhancedSearchEngine('data_content.json')
    engine.build_index()
    
    # Test cases cho từ ghép tiếng Việt
    test_cases = [
        {
            'query': 'Việt Nam',
            'description': 'Từ ghép có nghĩa đặc biệt (country name)',
            'expected': 'Should find Vietnam-related documents'
        },
        {
            'query': 'việt nam',  # lowercase
            'description': 'Từ ghép viết thường',
            'expected': 'Should match regardless of case'
        },
        {
            'query': 'Việt',
            'description': 'Chỉ nửa từ ghép (fragment)',
            'expected': 'May find documents with Việt Nam or other Việt* words'
        },
        {
            'query': 'Nam',
            'description': 'Chỉ nửa từ ghép (fragment)',
            'expected': 'May find many documents (common word)'
        },
        {
            'query': 'Hồ Chí Minh',
            'description': 'Tên người (3 từ)',
            'expected': 'Should find Ho Chi Minh documents'
        },
        {
            'query': 'Hồ Chí',
            'description': 'Tên không đầy đủ',
            'expected': 'Should still find relevant documents'
        },
        {
            'query': 'khởi nghĩa',
            'description': 'Từ ghép động từ',
            'expected': 'Should find uprising/rebellion documents'
        },
        {
            'query': 'khởi',
            'description': 'Chỉ một phần của từ ghép',
            'expected': 'May miss some contexts where full phrase is important'
        },
        {
            'query': 'Điện Biên Phủ',
            'description': 'Tên địa danh (3 từ)',
            'expected': 'Should find battle/location documents'
        },
        {
            'query': 'Điện Biên',
            'description': 'Tên địa danh không đầy đủ',
            'expected': 'Should still find relevant documents'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] Testing: '{test_case['query']}'")
        print(f"    Description: {test_case['description']}")
        print(f"    Expected: {test_case['expected']}")
        
        # Search with compound word
        results = engine.search(test_case['query'], top_k=3)
        
        print(f"    Results: {len(results)} found")
        for j, result in enumerate(results[:3], 1):
            score = result['score']
            file_name = result['file_name']
            preview = result['preview'][:100]
            
            print(f"      [{j}] {file_name} (Score: {score:.4f})")
            print(f"          Preview: {preview}...")
            
            # Analyze token matching
            query_tokens = engine.tokenizer.tokenize(test_case['query'])
            preview_tokens = engine.tokenizer.tokenize(preview)
            matches = set(query_tokens) & set(preview_tokens)
            
            print(f"          Query tokens: {query_tokens}")
            print(f"          Matching: {list(matches)} ({len(matches)}/{len(query_tokens)})")
        
        print("-" * 50)

def analyze_compound_word_issues():
    """Phân tích các vấn đề với từ ghép"""
    
    print("\n🔍 COMPOUND WORD ANALYSIS")
    print("=" * 60)
    
    engine = FixedEnhancedSearchEngine('data_content.json')
    engine.build_index()
    
    # So sánh từ ghép vs từ riêng lẻ
    comparisons = [
        ('Việt Nam', ['Việt', 'Nam']),
        ('Hồ Chí Minh', ['Hồ', 'Chí', 'Minh']),
        ('khởi nghĩa', ['khởi', 'nghĩa']),
        ('Điện Biên Phủ', ['Điện', 'Biên', 'Phủ']),
        ('chiến tranh', ['chiến', 'tranh']),
        ('cách mạng', ['cách', 'mạng'])
    ]
    
    for compound, components in comparisons:
        print(f"\n📝 Analyzing: '{compound}' vs {components}")
        
        # Test compound word
        compound_results = engine.search(compound, top_k=3)
        compound_scores = [r['score'] for r in compound_results]
        
        print(f"   Compound query '{compound}':")
        print(f"   → Scores: {[f'{s:.4f}' for s in compound_scores[:3]]}")
        
        # Test individual components
        for component in components:
            component_results = engine.search(component, top_k=3)
            component_scores = [r['score'] for r in component_results]
            print(f"   Component '{component}':")
            print(f"   → Scores: {[f'{s:.4f}' for s in component_scores[:3]]}")
        
        # Test combined search (all components)
        combined_query = ' '.join(components)
        combined_results = engine.search(combined_query, top_k=3) 
        combined_scores = [r['score'] for r in combined_results]
        print(f"   Combined '{combined_query}':")
        print(f"   → Scores: {[f'{s:.4f}' for s in combined_scores[:3]]}")
        
        print("-" * 40)

def test_ngram_approach():
    """Test cách tiếp cận n-gram cho từ ghép"""
    
    print("\n🔬 N-GRAM APPROACH TEST")
    print("=" * 60)
    
    # Sample text processing
    sample_texts = [
        "Việt Nam là một quốc gia ở Đông Nam Á",
        "Hồ Chí Minh là lãnh tụ của cách mạng Việt Nam", 
        "Chiến dịch Điện Biên Phủ diễn ra năm 1954",
        "Khởi nghĩa Bà Triệu chống lại quân Nam Hán"
    ]
    
    def extract_bigrams(text, tokenizer):
        """Extract bigrams from text"""
        tokens = tokenizer.tokenize(text.lower())
        bigrams = []
        for i in range(len(tokens) - 1):
            bigrams.append(f"{tokens[i]} {tokens[i+1]}")
        return bigrams
    
    def extract_trigrams(text, tokenizer):
        """Extract trigrams from text"""
        tokens = tokenizer.tokenize(text.lower())
        trigrams = []
        for i in range(len(tokens) - 2):
            trigrams.append(f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}")
        return trigrams
    
    engine = FixedEnhancedSearchEngine('data_content.json')
    
    for text in sample_texts:
        print(f"\nText: '{text}'")
        
        # Regular tokens
        tokens = engine.tokenizer.tokenize(text.lower())
        print(f"Tokens: {tokens}")
        
        # Bigrams
        bigrams = extract_bigrams(text, engine.tokenizer)
        print(f"Bigrams: {bigrams}")
        
        # Trigrams  
        trigrams = extract_trigrams(text, engine.tokenizer)
        print(f"Trigrams: {trigrams}")

if __name__ == "__main__":
    test_compound_words()
    analyze_compound_word_issues()
    test_ngram_approach()