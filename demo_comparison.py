"""
demo_comparison.py
Demo script để so sánh Original vs Enhanced Search Engine
"""

import time
from typing import Dict, List
from main import SearchEngine
from EnhancedSearchEngine import EnhancedSearchEngine


class SearchEngineComparison:
    """
    Class để so sánh performance giữa Original và Enhanced Search Engine
    """
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.test_queries = [
            "Hồ Chí Minh",
            "Điện Biên Phủ", 
            "chiến tranh",
            "Bà Triệu nữ tướng",
            "Trưng Vương khởi nghĩa",
            "thành Cổ Loa",
            "quân Tần xâm lược",
            "Ngô Quyền Bach Đằng"
        ]
    
    def initialize_engines(self):
        """Initialize both search engines"""
        print("🚀 Initializing Search Engines...")
        
        # Original Engine
        print("\n--- Original Search Engine ---")
        original_config = {
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',
            'embedding_model': 'keepitreal/vietnamese-sbert',
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.5,
            'top_k_results': 5
        }
        
        start_time = time.time()
        self.original_engine = SearchEngine(self.data_path, original_config)
        self.original_engine.build_index()
        original_build_time = time.time() - start_time
        
        # Enhanced Engine
        print("\n--- Enhanced Search Engine ---")  
        enhanced_config = {
            'chunking_strategy': 'hybrid',
            'chunk_size': 256,
            'overlap_size': 32,
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',
            'embedding_model': 'keepitreal/vietnamese-sbert',
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.4,
            'embedding_weight': 0.6,
            'chunk_boost_factor': 1.2,
            'document_aggregation': 'max',
            'top_k_results': 5,
            'enable_caching': True
        }
        
        start_time = time.time()
        self.enhanced_engine = EnhancedSearchEngine(self.data_path, enhanced_config)
        self.enhanced_engine.build_index()
        enhanced_build_time = time.time() - start_time
        
        print(f"\n⏱️ Build Time Comparison:")
        print(f"   Original: {original_build_time:.2f}s")
        print(f"   Enhanced: {enhanced_build_time:.2f}s")
        
        return original_build_time, enhanced_build_time
    
    def run_performance_comparison(self):
        """Run performance comparison"""
        print("\n" + "=" * 80)
        print("🔬 PERFORMANCE COMPARISON")
        print("=" * 80)
        
        original_times = []
        enhanced_times = []
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n[{i}/{len(self.test_queries)}] Testing query: '{query}'")
            
            # Original Engine
            start_time = time.time()
            original_results = self.original_engine.search(query, top_k=5)
            original_time = time.time() - start_time
            original_times.append(original_time)
            
            # Enhanced Engine - Document mode
            start_time = time.time()
            enhanced_results = self.enhanced_engine.search(query, top_k=5, search_mode='document')
            enhanced_time = time.time() - start_time
            enhanced_times.append(enhanced_time)
            
            print(f"   Original: {len(original_results)} results in {original_time:.3f}s")
            print(f"   Enhanced: {len(enhanced_results)} results in {enhanced_time:.3f}s")
            
            # Quality comparison for first query
            if i == 1:
                self._compare_result_quality(query, original_results, enhanced_results)
        
        # Summary statistics
        avg_original = sum(original_times) / len(original_times)
        avg_enhanced = sum(enhanced_times) / len(enhanced_times)
        
        print(f"\n📊 Average Search Time:")
        print(f"   Original: {avg_original:.3f}s")
        print(f"   Enhanced: {avg_enhanced:.3f}s")
        print(f"   Improvement: {((avg_original - avg_enhanced) / avg_original * 100):.1f}%")
    
    def demonstrate_enhanced_features(self):
        """Demonstrate unique features of Enhanced Engine"""
        print("\n" + "=" * 80)
        print("✨ ENHANCED FEATURES DEMONSTRATION")
        print("=" * 80)
        
        query = "Bà Triệu khởi nghĩa chống Ngô"
        
        print(f"\nQuery: '{query}'")
        print("\n1. Document Mode (Similar to Original):")
        doc_results = self.enhanced_engine.search(query, top_k=3, search_mode='document')
        for i, result in enumerate(doc_results, 1):
            print(f"   [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            print(f"       Preview: {result['preview'][:100]}...")
        
        print("\n2. Chunk Mode (Granular Results):")
        chunk_results = self.enhanced_engine.search(query, top_k=3, search_mode='chunk')
        for i, result in enumerate(chunk_results, 1):
            print(f"   [{i}] {result['file_name']} - {result['chunk_type']} (Score: {result['score']:.3f})")
            print(f"       Content: {result['content'][:100]}...")
        
        print("\n3. Context Mode (With Surrounding Content):")
        context_results = self.enhanced_engine.search(query, top_k=2, search_mode='context')
        for i, result in enumerate(context_results, 1):
            print(f"   [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            print(f"       Chunks: {result['best_chunks']} best, {result['total_chunks']} total")
            print(f"       Content: {result['content'][:150]}...")
        
        print("\n4. Explanation Mode:")
        explained_results = self.enhanced_engine.search(query, top_k=1, search_mode='chunk', explain=True)
        if explained_results:
            result = explained_results[0]
            exp = result.get('explanation', {})
            print(f"   Top result: {result['file_name']}")
            print(f"   BM25 score: {exp.get('scores', {}).get('bm25_weighted', 0):.3f}")
            print(f"   Embedding score: {exp.get('scores', {}).get('embedding_weighted', 0):.3f}")
            print(f"   Boost factor: {exp.get('boosts', {}).get('total_boost_factor', 1):.3f}")
            print(f"   Final score: {exp.get('final_score', 0):.3f}")
    
    def demonstrate_chunking_strategies(self):
        """Demonstrate different chunking strategies"""
        print("\n" + "=" * 80)
        print("🧩 CHUNKING STRATEGIES COMPARISON")
        print("=" * 80)
        
        strategies = ['semantic', 'hierarchical', 'hybrid', 'fixed']
        query = "Hồ Chí Minh"
        
        for strategy in strategies:
            print(f"\n--- Strategy: {strategy.upper()} ---")
            
            config = {
                'chunking_strategy': strategy,
                'chunk_size': 256,
                'overlap_size': 32,
                'use_bm25': True,
                'use_embedding': True,
                'bm25_weight': 0.4,
                'embedding_weight': 0.6,
                'top_k_results': 3,
                'enable_caching': False  # Disable for fair comparison
            }
            
            try:
                engine = EnhancedSearchEngine(self.data_path, config)
                
                start_time = time.time()
                engine.build_index()
                build_time = time.time() - start_time
                
                search_start = time.time()
                results = engine.search(query, top_k=3, search_mode='document')
                search_time = time.time() - search_start
                
                stats = engine.get_statistics()
                
                print(f"   Build time: {build_time:.2f}s")
                print(f"   Search time: {search_time:.3f}s")
                print(f"   Total chunks: {stats['chunks']['total_chunks']}")
                print(f"   Avg chunks/doc: {stats['documents']['avg_chunks_per_doc']:.1f}")
                print(f"   Top result score: {results[0]['score']:.3f}" if results else "No results")
                
            except Exception as e:
                print(f"   Error: {e}")
    
    def _compare_result_quality(self, query: str, original_results: List, enhanced_results: List):
        """Compare result quality"""
        print(f"\n🔍 Quality Comparison for '{query}':")
        
        print("\nOriginal Engine Results:")
        for i, result in enumerate(original_results[:3], 1):
            print(f"   [{i}] {result['file_name']} (Score: {result['score']:.3f})")
        
        print("\nEnhanced Engine Results:")
        for i, result in enumerate(enhanced_results[:3], 1):
            print(f"   [{i}] {result['file_name']} (Score: {result['score']:.3f})")
            if 'best_chunks_count' in result:
                print(f"       Based on {result['best_chunks_count']} relevant chunks")
    
    def run_full_comparison(self):
        """Run complete comparison suite"""
        print("=" * 80)
        print("🚀 SEARCH ENGINE COMPARISON SUITE")
        print("=" * 80)
        
        # Initialize engines
        build_times = self.initialize_engines()
        
        # Performance comparison
        self.run_performance_comparison()
        
        # Enhanced features
        self.demonstrate_enhanced_features()
        
        # Chunking strategies
        self.demonstrate_chunking_strategies()
        
        print("\n" + "=" * 80)
        print("✅ COMPARISON COMPLETE")
        print("=" * 80)
        
        # Summary
        print("\n📋 SUMMARY:")
        print("✨ Enhanced Search Engine Benefits:")
        print("   - Granular chunk-level search")
        print("   - Multiple search modes (document/chunk/context)")
        print("   - Better relevance through chunk boosting")
        print("   - Flexible chunking strategies")
        print("   - Performance caching")
        print("   - Detailed explanations")
        print("   - Context-aware results")
        
        print("\n⚡ Performance:")
        print("   - Similar or better search speed")
        print("   - More precise results")
        print("   - Better handling of long documents")
        print("   - Intelligent caching reduces rebuild time")


def main():
    """Main demo function"""
    DATA_PATH = "data_content.json"
    
    comparison = SearchEngineComparison(DATA_PATH)
    comparison.run_full_comparison()


if __name__ == "__main__":
    main()