"""
interactive_demo.py
Demonstrate the interactive features and different search modes
"""

from EnhancedSearchEngine import EnhancedSearchEngine

def demonstrate_search_modes():
    print("🚀 ENHANCED SEARCH ENGINE DEMO")
    print("=" * 60)
    
    # Initialize with BM25 only for faster demonstration
    engine = EnhancedSearchEngine("data_content.json", {
        'chunking_strategy': 'hybrid',  # Use hybrid for better chunking
        'chunk_size': 256,
        'overlap_size': 32,
        'use_stopwords': True,
        'tokenizer_library': 'underthesea',
        'embedding_model': 'keepitreal/vietnamese-sbert',
        'use_bm25': True,
        'use_embedding': False,  # Skip heavy model for demo
        'bm25_weight': 1.0,
        'embedding_weight': 0.0,
        'chunk_boost_factor': 1.2,
        'document_aggregation': 'max',
        'top_k_results': 3,
        'top_k_chunks_per_search': 20,
        'context_window': 1,
        'enable_caching': True
    })
    
    # Build index (will use cache if available)
    print("Building index...")
    engine.build_index()
    
    # Test different queries
    test_queries = [
        "chiến tranh Việt Nam",
        "Hồ Chí Minh", 
        "Điện Biên Phủ"
    ]
    
    for query in test_queries:
        print(f"\n" + "="*60)
        print(f"🔍 TESTING QUERY: '{query}'")
        print("="*60)
        
        # Document mode
        print(f"\n📄 DOCUMENT MODE:")
        doc_results = engine.search(query, top_k=2, search_mode='document')
        for i, result in enumerate(doc_results, 1):
            print(f"  [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            print(f"      Preview: {result.get('preview', 'N/A')[:100]}...")
        
        # Chunk mode  
        print(f"\n🧩 CHUNK MODE:")
        chunk_results = engine.search(query, top_k=2, search_mode='chunk')
        for i, result in enumerate(chunk_results, 1):
            print(f"  [{i}] {result['file_name']} - {result['chunk_type']}")
            print(f"      Score: {result['score']:.3f}")
            content = result['content'].replace('\n', ' ')[:80]
            print(f"      Content: {content}...")
    
    # Show system statistics
    print(f"\n" + "="*60)
    print("📊 SYSTEM STATISTICS")
    print("="*60)
    stats = engine.get_statistics()
    print(f"Documents: {stats['documents']['total_count']}")
    print(f"Chunks: {stats['chunks']['total_chunks']}")
    print(f"Chunking Strategy: {stats['config']['chunking_strategy']}")
    print(f"Chunk Size: {stats['config']['chunk_size']}")
    print(f"Average Chunks per Document: {stats['documents']['avg_chunks_per_doc']:.1f}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"💡 The Enhanced Search Engine provides:")
    print(f"   - Better granularity with chunk-based search")
    print(f"   - Multiple search modes (document/chunk/context)")
    print(f"   - Intelligent caching for faster rebuilds")
    print(f"   - Vietnamese-optimized processing")

if __name__ == "__main__":
    demonstrate_search_modes()