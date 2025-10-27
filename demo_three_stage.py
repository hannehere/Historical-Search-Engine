"""
demo_three_stage.py
Demo comparing Current Hybrid vs Three-Stage Retrieval

Demonstrates the paper-based Three-Stage approach:
1. BM25 filtering (fast keyword matching)
2. Dense retrieval (semantic understanding)  
3. Cross-encoder reranking (final precision)
"""

import time
from EnhancedSearchEngine import EnhancedSearchEngine
from ThreeStageRetrieval import ThreeStageRetrieval, create_three_stage_config


def demo_three_stage_comparison():
    """Demo comparing current system vs three-stage retrieval"""
    
    print("=" * 80)
    print("🚀 THREE-STAGE RETRIEVAL vs CURRENT HYBRID DEMO")
    print("=" * 80)
    
    # Initialize current enhanced system
    print("\n[1/3] 🔧 Initializing Current Hybrid System...")
    current_engine = EnhancedSearchEngine("data_content.json")
    
    # Build current system
    start_time = time.time()
    current_engine.build_index()
    current_build_time = time.time() - start_time
    
    # Initialize three-stage system
    print("\n[2/3] 🔧 Initializing Three-Stage Retrieval System...")
    
    # Try different configurations
    configs = {
        'fast': create_three_stage_config('fast'),
        'balanced': create_three_stage_config('balanced'),
        'accurate': create_three_stage_config('accurate')
    }
    
    three_stage_systems = {}
    
    for config_name, config in configs.items():
        print(f"\n  📋 Setting up {config_name.upper()} configuration...")
        
        three_stage = ThreeStageRetrieval(**config)
        
        # Index chunks (reuse from current system)
        three_stage.index_chunks(
            chunks=current_engine.chunks,
            tokenized_chunks=current_engine.tokenized_chunks,
            chunk_to_doc_map=current_engine.chunk_to_doc_map
        )
        
        three_stage_systems[config_name] = three_stage
        print(f"  ✓ {config_name.upper()} system ready")
    
    # Test queries
    test_queries = [
        "Bà Triệu khởi nghĩa",
        "Hồ Chí Minh lãnh tụ",
        "chiến tranh Việt Nam",
        "Điện Biên Phủ thắng lợi"
    ]
    
    print("\n[3/3] 🔍 Running Comparative Tests...")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n🔍 QUERY: '{query}'")
        print("-" * 60)
        
        # Tokenize query
        query_tokens = current_engine.tokenizer.tokenize(query)
        
        # Current system results
        print("\n📊 CURRENT HYBRID SYSTEM:")
        start_time = time.time()
        current_results = current_engine.search(query, search_mode='chunk', top_k=5)
        current_search_time = time.time() - start_time
        
        print(f"  ⏱️  Search time: {current_search_time:.3f}s")
        print(f"  📋 Results: {len(current_results)}")
        
        if current_results:
            for i, (chunk, score) in enumerate(current_results[:3], 1):
                print(f"  [{i}] Score: {score:.3f} | {chunk.source_file}")
                print(f"      Preview: {chunk.content[:80]}...")
        
        # Three-stage system results
        for config_name, three_stage in three_stage_systems.items():
            print(f"\n🎯 THREE-STAGE ({config_name.upper()}):")
            
            start_time = time.time()
            three_stage_results = three_stage.retrieve_three_stage(
                query, query_tokens, 
                final_top_k=5, 
                return_stage_details=True
            )
            three_stage_search_time = time.time() - start_time
            
            print(f"  ⏱️  Search time: {three_stage_search_time:.3f}s")
            print(f"  📋 Results: {len(three_stage_results['final_results'])}")
            
            # Pipeline breakdown
            pipeline = three_stage_results['pipeline_summary']
            print(f"  🔄 Pipeline: {pipeline['initial_candidates']} → " + 
                  f"{pipeline['after_stage1']} → " + 
                  f"{pipeline['after_stage2']} → " +
                  f"{pipeline['final_results']}")
            
            # Show top results
            final_results = three_stage_results['final_results']
            if final_results:
                for i, (chunk, score) in enumerate(final_results[:3], 1):
                    print(f"  [{i}] Score: {score:.3f} | {chunk.source_file}")
                    print(f"      Preview: {chunk.content[:80]}...")
            
            # Stage details
            stage_details = three_stage_results['stage_details']
            for stage_name, stage_info in stage_details.items():
                print(f"  📊 {stage_name}: {stage_info['candidates']} candidates, " +
                      f"top score: {stage_info['top_scores'][0]:.3f}")
        
        print("-" * 60)
    
    # System comparison summary
    print("\n" + "=" * 80)
    print("📈 SYSTEM COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"\n🏗️  ARCHITECTURE COMPARISON:")
    print(f"  Current Hybrid: BM25 + Embeddings (simultaneous)")
    print(f"  Three-Stage: BM25 → Dense → Rerank (sequential)")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"  Current build time: {current_build_time:.1f}s")
    print(f"  Three-stage setup: Similar (reuses current index)")
    
    print(f"\n🎯 CONFIGURATION OPTIONS:")
    for config_name, config in configs.items():
        system = three_stage_systems[config_name]
        stats = system.get_pipeline_stats()
        
        print(f"  {config_name.upper()}:")
        print(f"    • Stages: BM25={stats['stage1_enabled']}, " +
              f"Dense={stats['stage2_enabled']}, Rerank={stats['stage3_enabled']}")
        print(f"    • Pipeline: {stats['stage1_top_k']} → " + 
              f"{stats['stage2_top_k']} → {stats['stage3_top_k']}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  • Use FAST for quick keyword searches")
    print(f"  • Use BALANCED for general semantic search") 
    print(f"  • Use ACCURATE for critical/research queries")
    print(f"  • Current Hybrid good for real-time applications")
    print(f"  • Three-Stage better for batch processing")


def demo_interactive_three_stage():
    """Interactive demo for three-stage retrieval"""
    
    print("=" * 80)
    print("🎮 INTERACTIVE THREE-STAGE RETRIEVAL DEMO")
    print("=" * 80)
    
    # Initialize systems
    print("\n🔧 Initializing systems...")
    current_engine = EnhancedSearchEngine("data_content.json")
    current_engine.build_index()
    
    # Initialize three-stage with balanced config
    three_stage = ThreeStageRetrieval(**create_three_stage_config('balanced'))
    three_stage.index_chunks(
        chunks=current_engine.chunks,
        tokenized_chunks=current_engine.tokenized_chunks,
        chunk_to_doc_map=current_engine.chunk_to_doc_map
    )
    
    print("✅ Systems ready!")
    
    print("\n📝 Commands:")
    print("  • Enter query to search")
    print("  • :mode [fast|balanced|accurate] - Switch three-stage mode")
    print("  • :current - Use current hybrid system")
    print("  • :compare - Compare both systems")
    print("  • :quit - Exit")
    
    current_mode = 'balanced'
    use_current = False
    
    while True:
        try:
            user_input = input(f"\n[{current_mode if not use_current else 'current'}] Search: ").strip()
            
            if user_input.lower() in [':quit', ':exit', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            elif user_input.startswith(':mode '):
                new_mode = user_input[6:].strip()
                if new_mode in ['fast', 'balanced', 'accurate']:
                    current_mode = new_mode
                    config = create_three_stage_config(current_mode)
                    three_stage = ThreeStageRetrieval(**config)
                    three_stage.index_chunks(
                        chunks=current_engine.chunks,
                        tokenized_chunks=current_engine.tokenized_chunks,
                        chunk_to_doc_map=current_engine.chunk_to_doc_map
                    )
                    use_current = False
                    print(f"✓ Switched to THREE-STAGE {current_mode.upper()} mode")
                else:
                    print("❌ Invalid mode. Use: fast, balanced, accurate")
                continue
            
            elif user_input == ':current':
                use_current = True
                print("✓ Switched to CURRENT HYBRID system")
                continue
            
            elif user_input == ':compare':
                query = input("Enter query to compare: ").strip()
                if not query:
                    continue
                
                print(f"\n🔍 COMPARING: '{query}'")
                print("-" * 50)
                
                # Current system
                current_results = current_engine.search(query, search_mode='chunk', top_k=3)
                print(f"\n📊 CURRENT HYBRID ({len(current_results)} results):")
                for i, (chunk, score) in enumerate(current_results, 1):
                    print(f"  [{i}] {score:.3f} | {chunk.source_file}")
                
                # Three-stage
                query_tokens = current_engine.tokenizer.tokenize(query)
                three_results = three_stage.retrieve_three_stage(
                    query, query_tokens, final_top_k=3, return_stage_details=True
                )
                print(f"\n🎯 THREE-STAGE {current_mode.upper()} ({len(three_results['final_results'])} results):")
                for i, (chunk, score) in enumerate(three_results['final_results'], 1):
                    print(f"  [{i}] {score:.3f} | {chunk.source_file}")
                
                # Pipeline info
                pipeline = three_results['pipeline_summary']
                print(f"\n🔄 Pipeline: {pipeline['initial_candidates']} → " +
                      f"{pipeline['after_stage1']} → " +
                      f"{pipeline['after_stage2']} → " +
                      f"{pipeline['final_results']}")
                
                continue
            
            elif not user_input:
                continue
            
            # Regular search
            query_tokens = current_engine.tokenizer.tokenize(user_input)
            
            if use_current:
                # Current system search
                results = current_engine.search(user_input, search_mode='chunk', top_k=5)
                print(f"\n📊 CURRENT HYBRID RESULTS ({len(results)}):")
                
                for i, (chunk, score) in enumerate(results, 1):
                    print(f"[{i}] Score: {score:.3f}")
                    print(f"    📄 File: {chunk.source_file}")
                    print(f"    📝 Content: {chunk.content[:120]}...")
                    print()
            
            else:
                # Three-stage search
                results = three_stage.retrieve_three_stage(
                    user_input, query_tokens, 
                    final_top_k=5, 
                    return_stage_details=True
                )
                
                print(f"\n🎯 THREE-STAGE {current_mode.upper()} RESULTS ({len(results['final_results'])}):")
                
                # Pipeline summary
                pipeline = results['pipeline_summary']
                print(f"🔄 Pipeline: {pipeline['initial_candidates']} candidates → " +
                      f"{pipeline['after_stage1']} → " +
                      f"{pipeline['after_stage2']} → " +
                      f"{pipeline['final_results']} final")
                
                # Results
                for i, (chunk, score) in enumerate(results['final_results'], 1):
                    print(f"[{i}] Score: {score:.3f}")
                    print(f"    📄 File: {chunk.source_file}")
                    print(f"    📝 Content: {chunk.content[:120]}...")
                    print()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Comparison Demo (automatic)")
    print("2. Interactive Demo") 
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        demo_three_stage_comparison()
    elif choice == "2":
        demo_interactive_three_stage()
    else:
        print("Invalid choice. Running comparison demo...")
        demo_three_stage_comparison()