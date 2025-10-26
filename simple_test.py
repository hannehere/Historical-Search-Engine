"""
simple_test.py
Simple test without heavy model downloads
"""

from main import SearchEngine
from EnhancedSearchEngine import EnhancedSearchEngine
import time

def simple_demo():
    print("🚀 SIMPLE SEARCH ENGINE TEST")
    print("=" * 50)
    
    query = "Bà Triệu"
    
    # Test Enhanced Engine with lighter config (BM25 only)
    print("\n--- Enhanced Search Engine (BM25 only) ---")
    try:
        start_time = time.time()
        enhanced_engine = EnhancedSearchEngine("data_content.json", {
            'chunking_strategy': 'semantic',  # Faster chunking
            'chunk_size': 256,
            'overlap_size': 32,
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',
            'embedding_model': 'keepitreal/vietnamese-sbert',  # Required but won't be used
            'use_bm25': True,
            'use_embedding': False,  # Skip heavy embedding model
            'bm25_weight': 1.0,
            'embedding_weight': 0.0,
            'chunk_boost_factor': 1.2,
            'document_aggregation': 'max',
            'top_k_results': 3,
            'top_k_chunks_per_search': 20,
            'context_window': 1,
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
        
        # Show system statistics
        stats = enhanced_engine.get_statistics()
        print(f"\n📊 System Stats:")
        print(f"   Documents: {stats['documents']['total_count']}")
        print(f"   Chunks: {stats['chunks']['total_chunks']}")
        print(f"   Avg chunks/doc: {stats['documents']['avg_chunks_per_doc']:.1f}")
        
        # Chunk mode search for comparison
        print(f"\n🧩 Chunk-level results for '{query}':")
        chunk_results = enhanced_engine.search(query, top_k=3, search_mode='chunk')
        
        for i, result in enumerate(chunk_results, 1):
            print(f"  [{i}] {result['file_name']} - {result['chunk_type']}")
            print(f"      Score: {result['score']:.3f}")
            content = result['content'].replace('\n', ' ')[:80]
            print(f"      Content: {content}...")
            
    except Exception as e:
        print(f"❌ Enhanced engine error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Simple test completed!")

if __name__ == "__main__":
    simple_demo()