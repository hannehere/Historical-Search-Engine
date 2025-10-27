"""
quick_enhanced_test.py
Quick test for Enhanced Search Engine without heavy dependencies
"""

def test_enhanced_engine():
    """Quick test của Enhanced Search Engine"""
    
    print("🚀 QUICK ENHANCED SEARCH ENGINE TEST")
    print("=" * 60)
    
    try:
        # Test import
        print("📋 Testing imports...")
        
        # Test basic imports first
        import json
        import time
        print("  ✅ Basic imports OK")
        
        # Test if data file exists
        import os
        data_path = "data_content.json"
        if os.path.exists(data_path):
            print(f"  ✅ Data file exists: {data_path}")
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✅ Loaded {len(data)} documents")
        else:
            print(f"  ❌ Data file not found: {data_path}")
            return
        
        # Test enhanced tokenizer
        print("\n📝 Testing Enhanced Vietnamese Tokenizer...")
        try:
            from EnhancedVietnameseTokenizer import EnhancedVietnameseTokenizer
            tokenizer = EnhancedVietnameseTokenizer(use_stopwords=True, enable_ner=False)
            
            test_text = "Bà Triệu là nữ tướng anh hùng của Việt Nam"
            tokens = tokenizer.tokenize(test_text)
            print(f"  ✅ Tokenizer working: '{test_text}' → {len(tokens)} tokens")
            print(f"      Tokens: {' | '.join(tokens[:5])}...")
            
            stats = tokenizer.get_stopwords_stats()
            print(f"  ✅ Stopwords: {stats['total_stopwords']} total")
            
        except Exception as e:
            print(f"  ❌ Enhanced tokenizer failed: {e}")
            print("  🔄 Falling back to basic tokenizer test...")
            
            try:
                from Tokenizer import VietnameseTokenizer
                basic_tokenizer = VietnameseTokenizer()
                tokens = basic_tokenizer.tokenize("Bà Triệu anh hùng")
                print(f"  ✅ Basic tokenizer working: {len(tokens)} tokens")
            except Exception as e2:
                print(f"  ❌ Basic tokenizer also failed: {e2}")
        
        # Test context-aware chunker
        print("\n🧩 Testing Context-Aware Chunker...")
        try:
            from ContextAwareChunker import VietnameseContextAwareChunker
            chunker = VietnameseContextAwareChunker(chunk_size=100, overlap_size=20)
            
            sample_doc = data[0]
            chunks = chunker.chunk_document(sample_doc['content'], sample_doc['filename'])
            print(f"  ✅ Chunker working: {len(chunks)} chunks created")
            
            if chunks:
                sample_chunk = chunks[0]
                print(f"      Sample chunk type: {sample_chunk.chunk_type}")
                print(f"      Sample content: {sample_chunk.content[:80]}...")
                
        except Exception as e:
            print(f"  ❌ Context-aware chunker failed: {e}")
        
        # Test Three-Stage Retrieval
        print("\n🎯 Testing Three-Stage Retrieval...")
        try:
            from ThreeStageRetrieval import create_three_stage_config
            config = create_three_stage_config('fast')  # BM25 only for speed
            print(f"  ✅ Three-stage config created: {config}")
            
        except Exception as e:
            print(f"  ❌ Three-stage retrieval failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ QUICK TEST COMPLETED")
        print("💡 If you see mostly green checkmarks, the system is working!")
        print("❌ If you see errors, check the specific component dependencies")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_simple_search():
    """Test simple search functionality"""
    
    print("\n🔍 SIMPLE SEARCH TEST")
    print("=" * 40)
    
    try:
        # Load data
        import json
        with open("data_content.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Simple text search
        query = "Bà Triệu"
        matches = []
        
        for doc in data:
            content = doc.get('content', '').lower()
            if query.lower() in content:
                matches.append({
                    'filename': doc.get('filename', 'Unknown'),
                    'score': content.count(query.lower()),
                    'preview': content[:200] + "..."
                })
        
        # Sort by relevance
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"🔍 Search for: '{query}'")
        print(f"📋 Found: {len(matches)} matches")
        
        for i, match in enumerate(matches[:3], 1):
            print(f"\n[{i}] {match['filename']} (score: {match['score']})")
            print(f"    {match['preview']}")
        
    except Exception as e:
        print(f"❌ Simple search failed: {e}")


if __name__ == "__main__":
    test_enhanced_engine()
    test_simple_search()