#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from EnhancedSearchEngine_Fixed import FixedEnhancedSearchEngine

def test_scoring():
    engine = FixedEnhancedSearchEngine('data_content.json')
    
    # Build index
    print("Building index...")
    engine.build_index()
    
    # Test scoring with different queries
    queries = [
        "Bà Triệu sinh năm nao",
        "Bà Triệu", 
        "khởi nghĩa",
        "Việt Nam lịch sử"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"🔍 QUERY: '{query}'")
        print(f"{'='*60}")
        
        results = engine.search(query, top_k=3)
        
        for i, result in enumerate(results[:3]):
            print(f"\n[{i+1}] Score: {result['score']:.6f}")
            print(f"    File: {result['file_name']}")
            print(f"    Preview: {result['preview'][:120]}...")
            
            # Show token matching info
            query_tokens = engine.tokenizer.tokenize(query)
            chunk_tokens = engine.tokenizer.tokenize(result['preview'])
            
            matches = set(query_tokens) & set(chunk_tokens)
            print(f"    Query tokens: {query_tokens}")  
            print(f"    Matching terms: {list(matches)} ({len(matches)}/{len(query_tokens)})")
            
            # Calculate manual score for verification
            score = 0.0
            chunk_token_counts = {}
            for token in chunk_tokens:
                chunk_token_counts[token] = chunk_token_counts.get(token, 0) + 1
                    
            for query_token in query_tokens:
                if query_token in chunk_token_counts:
                    tf = chunk_token_counts[query_token]
                    normalized_tf = tf / len(chunk_tokens) if len(chunk_tokens) > 0 else 0
                    score += normalized_tf
                    print(f"    Term '{query_token}': tf={tf}, normalized_tf={normalized_tf:.6f}")
            
            print(f"    Manual calculated score: {score:.6f}")
            print(f"    Chunk length: {len(chunk_tokens)} tokens")

if __name__ == "__main__":
    test_scoring()