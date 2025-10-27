"""
demo_enhanced_context.py
Demo enhanced Vietnamese context-aware processing

Demonstrates improvements:
1. Comprehensive Vietnamese stopwords (300+ words)
2. Context-aware chunking with entity preservation
3. LLM-based reranking (true paper approach)
4. Vietnamese semantic understanding
"""

import time
import json
from EnhancedVietnameseTokenizer import EnhancedVietnameseTokenizer, create_context_aware_tokenizer
from ContextAwareChunker import VietnameseContextAwareChunker, create_context_aware_chunker
from ThreeStageRetrieval import ThreeStageRetrieval, create_three_stage_config
from EnhancedSearchEngine import EnhancedSearchEngine


def demo_enhanced_tokenizer():
    """Demo enhanced Vietnamese tokenizer với comprehensive stopwords"""
    
    print("=" * 80)
    print("🔤 ENHANCED VIETNAMESE TOKENIZER DEMO")
    print("=" * 80)
    
    # Sample Vietnamese historical text
    sample_text = """
    # Bà Triệu - Nữ Tướng Anh Hùng
    
    Bà Triệu (chữ Hán: 趙婆, 226-248) là một trong những anh hùng nữ nổi tiếng nhất 
    trong lịch sử Việt Nam. Bà sinh ra tại làng Tây Hưng, huyện Hoành Bố, 
    tỉnh Quảng Ninh ngày nay. Với lòng yêu nước nồng nàn, bà đã lãnh đạo cuộc 
    khởi nghĩa chống lại sự thống trị của nhà Ngô (Trung Quốc) vào năm 248.
    
    Tuy nhiên, cuộc khởi nghĩa của bà chỉ kéo dài được vài tháng. Do lực lượng 
    không cân sức với quân địch, bà đã tự vẫn để giữ danh tiết. Bà Triệu trở thành 
    biểu tượng của tinh thần yêu nước và lòng kiên cường của người phụ nữ Việt Nam.
    """
    
    # Initialize different tokenizers
    tokenizers = {
        'Original': EnhancedVietnameseTokenizer(use_stopwords=False, library='underthesea'),
        'Basic Stopwords': EnhancedVietnameseTokenizer(use_stopwords=True, library='underthesea'),
        'Enhanced Historical': create_context_aware_tokenizer('historical'),
        'Enhanced Academic': create_context_aware_tokenizer('academic')
    }
    
    print("📝 Sample text:")
    print(sample_text[:200] + "...")
    print("\n" + "-" * 80)
    
    for name, tokenizer in tokenizers.items():
        print(f"\n🔤 {name.upper()} TOKENIZER:")
        
        if hasattr(tokenizer, 'tokenize_with_context'):
            # Enhanced tokenizer with context
            tokens, entities = tokenizer.tokenize_with_context(sample_text)
            
            print(f"  📊 Tokens: {len(tokens)}")
            print(f"  🏷️  Entities found:")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    print(f"    • {entity_type}: {', '.join(entity_list[:3])}{'...' if len(entity_list) > 3 else ''}")
            
            print(f"  📝 Sample tokens: {' | '.join(tokens[:10])}{'...' if len(tokens) > 10 else ''}")
            
            if hasattr(tokenizer, 'get_stopwords_stats'):
                stats = tokenizer.get_stopwords_stats()
                print(f"  🚫 Stopwords: {stats['total_stopwords']} total ({stats['vietnamese_core']} VN core)")
        
        else:
            # Basic tokenizer
            tokens = tokenizer.tokenize(sample_text)
            print(f"  📊 Tokens: {len(tokens)}")
            print(f"  📝 Sample tokens: {' | '.join(tokens[:10])}{'...' if len(tokens) > 10 else ''}")
    
    print("\n" + "=" * 80)


def demo_context_aware_chunking():
    """Demo context-aware chunking cho Vietnamese documents"""
    
    print("🧩 CONTEXT-AWARE CHUNKING DEMO")
    print("=" * 80)
    
    # Load sample document
    with open("data_content.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find a good sample document
    sample_doc = None
    for doc in data:
        if "Bà Triệu" in doc.get("content", "") or "Hồ Chí Minh" in doc.get("content", ""):
            sample_doc = doc
            break
    
    if not sample_doc:
        sample_doc = data[0]  # Fallback to first document
    
    print(f"📄 Sample document: {sample_doc['filename']}")
    print(f"📏 Content length: {len(sample_doc['content'])} chars")
    
    # Different chunking strategies
    chunkers = {
        'Basic Fixed': create_context_aware_chunker('historical'),
        'Biographical': create_context_aware_chunker('biographical'),
        'Geographical': create_context_aware_chunker('geographical')
    }
    
    for name, chunker in chunkers.items():
        print(f"\n🧩 {name.upper()} CHUNKING:")
        
        chunks = chunker.chunk_document(sample_doc['content'], sample_doc['filename'])
        
        print(f"  📊 Generated {len(chunks)} chunks")
        
        # Show sample chunk with metadata
        if chunks:
            sample_chunk = chunks[0]
            print(f"  📝 Sample chunk preview: {sample_chunk.content[:100]}...")
            print(f"  🏷️  Chunk type: {sample_chunk.chunk_type}")
            
            if 'entities' in sample_chunk.metadata:
                entities = sample_chunk.metadata['entities']
                print(f"  👤 Persons: {', '.join(entities['persons'][:3]) if entities['persons'] else 'None'}")
                print(f"  📍 Locations: {', '.join(entities['locations'][:3]) if entities['locations'] else 'None'}")
                print(f"  📅 Years: {', '.join(entities['years'][:3]) if entities['years'] else 'None'}")
            
            if 'vietnamese_complexity' in sample_chunk.metadata:
                print(f"  🧠 Vietnamese complexity: {sample_chunk.metadata['vietnamese_complexity']}")
                print(f"  🔗 Semantic coherence: {sample_chunk.metadata['semantic_coherence']:.2f}")
    
    print("\n" + "=" * 80)


def demo_llm_reranking():
    """Demo LLM-based reranking (true paper approach)"""
    
    print("🤖 LLM-BASED RERANKING DEMO")
    print("=" * 80)
    
    print("⚠️  Note: LLM-based reranking requires a generative model")
    print("This demo will show the approach with fallback to similarity-based reranking")
    
    # Initialize systems
    print("\n🔧 Initializing systems...")
    
    # Current enhanced system
    current_engine = EnhancedSearchEngine("data_content.json")
    current_engine.build_index()
    
    # Three-stage with LLM reranking attempt
    llm_config = create_three_stage_config('accurate')
    llm_config.update({
        'reranker_model': 'vinai/phobert-base',  # Will fallback to sentence transformer
        'use_reranking': True
    })
    
    three_stage_llm = ThreeStageRetrieval(**llm_config)
    three_stage_llm.index_chunks(
        chunks=current_engine.chunks,
        tokenized_chunks=current_engine.tokenized_chunks,
        chunk_to_doc_map=current_engine.chunk_to_doc_map
    )
    
    # Test queries
    test_queries = [
        "Bà Triệu khởi nghĩa chống Ngô",
        "Hồ Chí Minh lãnh tụ cách mạng"
    ]
    
    for query in test_queries:
        print(f"\n🔍 QUERY: '{query}'")
        print("-" * 60)
        
        query_tokens = current_engine.tokenizer.tokenize(query)
        
        # Current system
        print("📊 CURRENT HYBRID:")
        current_results = current_engine.search(query, search_mode='chunk', top_k=3)
        for i, (chunk, score) in enumerate(current_results, 1):
            print(f"  [{i}] {score:.3f} | {chunk.source_file}")
            print(f"      {chunk.content[:80]}...")
        
        # Three-stage with reranking
        print("\n🎯 THREE-STAGE + RERANKING:")
        three_stage_results = three_stage_llm.retrieve_three_stage(
            query, query_tokens, final_top_k=3, return_stage_details=True
        )
        
        pipeline = three_stage_results['pipeline_summary']
        print(f"  🔄 Pipeline: {pipeline['initial_candidates']} → {pipeline['after_stage1']} → {pipeline['after_stage2']} → {pipeline['final_results']}")
        
        for i, (chunk, score) in enumerate(three_stage_results['final_results'], 1):
            print(f"  [{i}] {score:.3f} | {chunk.source_file}")
            print(f"      {chunk.content[:80]}...")
        
        # Show reranker type used
        print(f"  🤖 Reranker type: {three_stage_llm._reranker_type}")
    
    print("\n" + "=" * 80)


def demo_complete_enhanced_pipeline():
    """Demo complete enhanced pipeline with all improvements"""
    
    print("🚀 COMPLETE ENHANCED PIPELINE DEMO")
    print("=" * 80)
    
    print("This demo shows the complete enhanced pipeline:")
    print("1. ✅ Enhanced Vietnamese tokenizer (300+ stopwords)")
    print("2. ✅ Context-aware chunking (entity preservation)")
    print("3. ✅ Three-stage retrieval (BM25 → Dense → Rerank)")
    print("4. ✅ Vietnamese semantic understanding")
    
    # Initialize complete system
    print("\n🔧 Initializing complete enhanced system...")
    
    current_engine = EnhancedSearchEngine("data_content.json")
    current_engine.build_index()
    
    # Enhanced tokenizer
    enhanced_tokenizer = create_context_aware_tokenizer('historical')
    
    # Three-stage system
    enhanced_config = create_three_stage_config('balanced')
    three_stage = ThreeStageRetrieval(**enhanced_config)
    three_stage.index_chunks(
        chunks=current_engine.chunks,
        tokenized_chunks=current_engine.tokenized_chunks,
        chunk_to_doc_map=current_engine.chunk_to_doc_map
    )
    
    print("✅ Complete system ready!")
    
    # Interactive demo
    print("\n🎮 Interactive mode:")
    print("  • Enter Vietnamese query")
    print("  • :compare - Compare all approaches")
    print("  • :stats - Show system statistics")
    print("  • :quit - Exit")
    
    while True:
        try:
            user_input = input("\n🔍 Vietnamese query: ").strip()
            
            if user_input.lower() in [':quit', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            elif user_input == ':stats':
                print("\n📊 SYSTEM STATISTICS:")
                print(f"  📄 Documents: {len(current_engine.documents)}")
                print(f"  🧩 Chunks: {len(current_engine.chunks)}")
                
                stats = enhanced_tokenizer.get_stopwords_stats()
                print(f"  🚫 Stopwords: {stats['total_stopwords']} total")
                print(f"      • Vietnamese core: {stats['vietnamese_core']}")
                print(f"      • English mixed: {stats['english_mixed']}")
                print(f"      • Markdown symbols: {stats['markdown_symbols']}")
                
                pipeline_stats = three_stage.get_pipeline_stats()
                print(f"  🎯 Three-stage pipeline: {pipeline_stats['stage1_top_k']} → {pipeline_stats['stage2_top_k']} → {pipeline_stats['stage3_top_k']}")
                
                continue
            
            elif user_input == ':compare':
                query = input("Enter query for comparison: ").strip()
                if not query:
                    continue
                
                print(f"\n🔍 COMPARING ALL APPROACHES: '{query}'")
                print("=" * 60)
                
                # Enhanced tokenization
                tokens, entities = enhanced_tokenizer.tokenize_with_context(query)
                print(f"🔤 Enhanced tokenization:")
                print(f"  • Tokens: {' | '.join(tokens[:5])}...")
                print(f"  • Entities: {sum(len(v) for v in entities.values())} found")
                
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
                print(f"\n🎯 THREE-STAGE ({len(three_results['final_results'])} results):")
                for i, (chunk, score) in enumerate(three_results['final_results'], 1):
                    print(f"  [{i}] {score:.3f} | {chunk.source_file}")
                
                pipeline = three_results['pipeline_summary']
                print(f"🔄 Pipeline: {pipeline['initial_candidates']} → {pipeline['after_stage1']} → {pipeline['after_stage2']} → {pipeline['final_results']}")
                
                continue
            
            elif not user_input:
                continue
            
            # Regular search with enhanced tokenization
            enhanced_tokens, entities = enhanced_tokenizer.tokenize_with_context(user_input)
            
            print(f"\n🔤 Enhanced tokenization:")
            print(f"  • Original: '{user_input}'")
            print(f"  • Tokens: {' | '.join(enhanced_tokens[:8])}{'...' if len(enhanced_tokens) > 8 else ''}")
            if any(entities.values()):
                print(f"  • Entities found:")
                for etype, elist in entities.items():
                    if elist:
                        print(f"    - {etype}: {', '.join(elist[:2])}")
            
            # Search with three-stage
            query_tokens = current_engine.tokenizer.tokenize(user_input)
            results = three_stage.retrieve_three_stage(
                user_input, query_tokens, final_top_k=5, return_stage_details=True
            )
            
            print(f"\n🎯 THREE-STAGE RESULTS ({len(results['final_results'])}):")
            
            pipeline = results['pipeline_summary']
            print(f"🔄 Pipeline: {pipeline['initial_candidates']} → {pipeline['after_stage1']} → {pipeline['after_stage2']} → {pipeline['final_results']}")
            
            for i, (chunk, score) in enumerate(results['final_results'], 1):
                print(f"\n[{i}] Score: {score:.3f}")
                print(f"    📄 File: {chunk.source_file}")
                print(f"    🏷️  Type: {chunk.chunk_type}")
                print(f"    📝 Content: {chunk.content[:150]}...")
                
                # Show chunk metadata if available
                if hasattr(chunk, 'metadata') and 'entities' in chunk.metadata:
                    chunk_entities = chunk.metadata['entities']
                    entity_summary = []
                    for etype, elist in chunk_entities.items():
                        if elist:
                            entity_summary.append(f"{etype}: {len(elist)}")
                    if entity_summary:
                        print(f"    🏷️  Entities: {', '.join(entity_summary)}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Choose enhanced demo:")
    print("1. Enhanced Tokenizer Demo")
    print("2. Context-Aware Chunking Demo") 
    print("3. LLM Reranking Demo")
    print("4. Complete Enhanced Pipeline Demo")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        demo_enhanced_tokenizer()
    elif choice == "2":
        demo_context_aware_chunking()
    elif choice == "3":
        demo_llm_reranking()
    elif choice == "4":
        demo_complete_enhanced_pipeline()
    else:
        print("Invalid choice. Running complete demo...")
        demo_complete_enhanced_pipeline()