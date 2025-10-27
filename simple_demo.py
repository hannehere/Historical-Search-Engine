#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 SIMPLE INTERACTIVE DEMO - Test ngay!
"""

def run_simple_demo():
    """Demo đơn giản để test ngay"""
    
    print("🎮 SIMPLE VIETNAMESE SEARCH DEMO")
    print("=" * 50)
    
    try:
        from EnhancedSearchEngine_Fixed import FixedEnhancedSearchEngine
        
        print("📋 Starting engine...")
        engine = FixedEnhancedSearchEngine('data_content.json')
        
        print("🔧 Building index...")
        engine.build_index()
        
        print("\n✅ Ready to search!")
        print("💡 Try: 'Việt Nam', 'Hồ Chí Minh', 'quit' to exit")
        print("-" * 50)
        
        while True:
            query = input("\n🔍 Search: ").strip()
            
            if not query or query.lower() in ['quit', 'exit', 'q']:
                print("👋 Bye!")
                break
                
            results = engine.search(query, top_k=3)
            
            if results:
                print(f"\n📊 Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"[{i}] {result['file_name']} ({result['score']:.3f})")
                    print(f"    {result['preview'][:120]}...")
            else:
                print("❌ No results found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have the required files and packages")

if __name__ == "__main__":
    run_simple_demo()