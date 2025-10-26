"""
quick_test.py
Quick test to demonstrate the difference between original and enhanced search
"""

from main import SearchEngine
from EnhancedSearchEngine import EnhancedSearchEngine
import time

def quick_demo():
    print("🚀 QUICK SEARCH ENGINE COMPARISON")
    print("=" * 60)
    
    query = "Bà Triệu"
    
    # Test Original Engine
    print("\n--- Original Search Engine ---")
    try:
        start_time = time.time()
        original_engine = SearchEngine("data_content.json", {
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',
            'embedding_model': 'keepitreal/vietnamese-sbert',
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.5,
            'top_k_results': 3
        })
        original_engine.build_index()
        build_time = time.time() - start_time
        
        search_start = time.time()
        results = original_engine.search(query, top_k=3)
        search_time = time.time() - search_start
        
        print(f"✓ Build time: {build_time:.2f}s")
        print(f"✓ Search time: {search_time:.3f}s") 
        print(f"✓ Results: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"  [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            
    except Exception as e:
        print(f"❌ Original engine error: {e}")
    
    # Test Enhanced Engine
    print("\n--- Enhanced Search Engine ---")
    try:
        start_time = time.time()
        enhanced_engine = EnhancedSearchEngine("data_content.json", {
            'chunking_strategy': 'hybrid',
            'chunk_size': 256,
            'overlap_size': 32,
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.4,
            'embedding_weight': 0.6,
            'top_k_results': 3,
            'enable_caching': True
        })
        enhanced_engine.build_index()
        build_time = time.time() - start_time
        
        # Document mode search
        search_start = time.time()
        doc_results = enhanced_engine.search(query, top_k=3, search_mode='document')
        search_time = time.time() - search_start
        
        print(f"✓ Build time: {build_time:.2f}s")
        print(f"✓ Search time: {search_time:.3f}s")
        print(f"✓ Document results: {len(doc_results)}")
        
        for i, result in enumerate(doc_results, 1):
            print(f"  [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            if 'best_chunks_count' in result:
                print(f"      Based on {result['best_chunks_count']} relevant chunks")
        
        # Chunk mode search for comparison
        print(f"\n🧩 Chunk-level results for '{query}':")
        chunk_results = enhanced_engine.search(query, top_k=3, search_mode='chunk')
        
        for i, result in enumerate(chunk_results, 1):
            print(f"  [{i}] {result['file_name']} - {result['chunk_type']}")
            print(f"      Score: {result['score']:.3f}")
            print(f"      Content: {result['content'][:100]}...")
            
    except Exception as e:
        print(f"❌ Enhanced engine error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Quick demo completed!")

if __name__ == "__main__":
    quick_demo()