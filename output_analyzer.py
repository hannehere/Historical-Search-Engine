"""
output_analyzer.py
Tool để phân tích và hiểu kết quả output của Enhanced Search Engine
"""

from EnhancedSearchEngine import EnhancedSearchEngine
import json

def analyze_build_output():
    """Phân tích output khi build index"""
    print("🔍 PHÂN TÍCH OUTPUT CỦA BUILD INDEX")
    print("=" * 60)
    
    engine = EnhancedSearchEngine("data_content.json", {
        'chunking_strategy': 'hybrid',
        'chunk_size': 256,
        'overlap_size': 32,
        'use_stopwords': True,
        'tokenizer_library': 'underthesea',
        'embedding_model': 'keepitreal/vietnamese-sbert',
        'use_bm25': True,
        'use_embedding': False,  # Skip heavy model for demo
        'bm25_weight': 1.0,
        'embedding_weight': 0.0,
        'top_k_results': 5,
        'top_k_chunks_per_search': 20,
        'enable_caching': True
    })
    
    print("\n📋 GIẢI THÍCH CÁC BƯỚC BUILD:")
    print("[1/4] Load documents and create chunks:")
    print("  - Đọc file JSON chứa 207 documents")
    print("  - Chia mỗi document thành nhiều chunks nhỏ")
    print("  - Ví dụ: 'Hồ Chí Minh.md' → 101 chunks")
    
    print("\n[2/4] Tokenizing chunks:")
    print("  - Chuyển đổi text thành tokens (từ)")
    print("  - Loại bỏ stopwords (từ không quan trọng)")
    print("  - Chuẩn hóa tiếng Việt")
    
    print("\n[3/4] Indexing chunks:")
    print("  - Tạo BM25 index cho tìm kiếm keyword")
    print("  - Tạo embeddings cho tìm kiếm semantic (nếu enabled)")
    
    print("\n[4/4] Performance Analysis:")
    print("  - Tổng số chunks: Số lượng đoạn văn được tạo")
    print("  - Avg chunks/doc: Trung bình chunks mỗi document")
    print("  - Chunk sizes: Kích thước từ nhỏ nhất đến lớn nhất")
    
    # Build actual index để show real output
    print("\n" + "="*60)
    print("🔧 DEMO THỰC TẾ:")
    engine.build_index()
    
    return engine

def analyze_search_output(engine):
    """Phân tích output khi search"""
    print("\n" + "="*60)
    print("🔍 PHÂN TÍCH OUTPUT CỦA SEARCH")
    print("="*60)
    
    query = "Hồ Chí Minh"
    
    print(f"\n📝 Query: '{query}'")
    print("\n💡 GIẢI THÍCH CÁC SEARCH MODE:")
    
    # Document Mode
    print("\n1️⃣ DOCUMENT MODE:")
    print("   - Tìm documents liên quan nhất")
    print("   - Score cao = liên quan hơn")
    print("   - Best chunks count = số chunks tốt nhất trong document")
    
    doc_results = engine.search(query, top_k=3, search_mode='document')
    
    print("\n📊 KẾT QUẢ DOCUMENT MODE:")
    for i, result in enumerate(doc_results, 1):
        print(f"   [{i}] File: {result['file_name']}")
        print(f"       Score: {result['score']:.3f} (càng cao càng liên quan)")
        print(f"       Chunks: {result.get('best_chunks_count', 'N/A')} chunks tốt nhất")
        print(f"       Preview: {result.get('preview', 'N/A')[:80]}...")
    
    # Chunk Mode
    print("\n2️⃣ CHUNK MODE:")
    print("   - Tìm các đoạn văn cụ thể")
    print("   - Cho thấy chính xác phần nào của document liên quan")
    print("   - Chunk type: loại đoạn (section, sub_section, paragraph)")
    
    chunk_results = engine.search(query, top_k=3, search_mode='chunk')
    
    print("\n📊 KẾT QUẢ CHUNK MODE:")
    for i, result in enumerate(chunk_results, 1):
        print(f"   [{i}] File: {result['file_name']}")
        print(f"       Chunk Type: {result['chunk_type']} (loại đoạn văn)")
        print(f"       Score: {result['score']:.3f}")
        print(f"       Content: {result['content'][:80].replace(chr(10), ' ')}...")
    
    # Context Mode
    print("\n3️⃣ CONTEXT MODE:")
    print("   - Tìm documents với context xung quanh")
    print("   - Total chunks: tổng số chunks liên quan")
    print("   - Best chunks: số chunks tốt nhất")
    
    context_results = engine.search(query, top_k=2, search_mode='context')
    
    print("\n📊 KẾT QUẢ CONTEXT MODE:")
    for i, result in enumerate(context_results, 1):
        print(f"   [{i}] File: {result['file_name']}")
        print(f"       Score: {result['score']:.3f}")
        print(f"       Best chunks: {result['best_chunks']}")
        print(f"       Total chunks: {result['total_chunks']}")
        print(f"       Content: {result['content'][:80].replace(chr(10), ' ')}...")

def analyze_scores_and_ranking():
    """Giải thích về scores và ranking"""
    print("\n" + "="*60)
    print("📈 HIỂU VỀ SCORES VÀ RANKING")
    print("="*60)
    
    print("\n🎯 SCORE LÀ GÌ?")
    print("   - Score = độ liên quan giữa query và document/chunk")
    print("   - Càng cao = càng liên quan")
    print("   - Khoảng từ 0.000 đến ~3.000+")
    
    print("\n🔢 CÁC THÀNH PHẦN SCORE:")
    print("   - BM25 Score: Tìm kiếm từ khóa (keyword matching)")
    print("   - Embedding Score: Hiểu nghĩa (semantic similarity)")
    print("   - Boost Factors: Tăng cường dựa trên:")
    print("     • Chunk type (overview > section > paragraph)")
    print("     • Title matching (query có trong tiêu đề)")
    print("     • Position (đầu document quan trọng hơn)")
    
    print("\n📊 VÍ DỤ SCORE:")
    print("   Score 2.500+: Rất liên quan (exact match)")
    print("   Score 1.500-2.499: Liên quan cao")  
    print("   Score 0.500-1.499: Liên quan trung bình")
    print("   Score 0.000-0.499: Liên quan thấp")

def interactive_output_guide():
    """Hướng dẫn sử dụng interactive mode"""
    print("\n" + "="*60)
    print("💬 HƯỚNG DẪN INTERACTIVE MODE")
    print("="*60)
    
    print("\n🎮 CÁC LỆNH INTERACTIVE:")
    print("   - Gõ query để search: 'Hồ Chí Minh'")
    print("   - :mode document    → Chuyển sang document mode")
    print("   - :mode chunk       → Chuyển sang chunk mode") 
    print("   - :mode context     → Chuyển sang context mode")
    print("   - :explain on       → Bật giải thích chi tiết")
    print("   - :explain off      → Tắt giải thích")
    print("   - :stats            → Xem thống kê hệ thống")
    print("   - :quit             → Thoát")
    
    print("\n📋 KHI NÀO DÙNG MODE NÀO:")
    print("   📄 Document Mode: Tìm tài liệu tổng quan")
    print("   🧩 Chunk Mode: Tìm đoạn văn cụ thể")
    print("   🌐 Context Mode: Tìm với ngữ cảnh xung quanh")
    
    print("\n💡 TIPS ĐỂ TÌM KIẾM TốT:")
    print("   ✅ Dùng từ khóa chính: 'Hồ Chí Minh', 'chiến tranh'")
    print("   ✅ Kết hợp nhiều từ: 'chiến tranh Việt Nam'")
    print("   ✅ Thử các mode khác nhau để so sánh")
    print("   ✅ Dùng :explain on để hiểu tại sao kết quả được rank cao")

def create_sample_search_session():
    """Tạo một session search mẫu"""
    print("\n" + "="*60)
    print("🎬 SESSION SEARCH MẪU")
    print("="*60)
    
    # Simulate một session thực tế
    sample_queries = [
        ("Bà Triệu", "document"),
        ("chiến tranh Điện Biên Phủ", "chunk"), 
        ("Ngô Quyền", "context")
    ]
    
    engine = EnhancedSearchEngine("data_content.json", {
        'chunking_strategy': 'semantic',
        'chunk_size': 256,
        'use_bm25': True,
        'use_embedding': False,
        'top_k_results': 2,
        'top_k_chunks_per_search': 10,
        'enable_caching': True
    })
    
    print("🔧 Building index...")
    engine.build_index()
    
    for query, mode in sample_queries:
        print(f"\n🔍 Query: '{query}' (Mode: {mode})")
        print("-" * 40)
        
        results = engine.search(query, top_k=2, search_mode=mode)
        
        if mode == 'document':
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['file_name']} (Score: {r['score']:.3f})")
        elif mode == 'chunk':
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['file_name']} - {r['chunk_type']} (Score: {r['score']:.3f})")
        else:  # context
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['file_name']} (Score: {r['score']:.3f}, Chunks: {r['total_chunks']})")

def main():
    """Main analysis function"""
    print("🎯 HƯỚNG DẪN ĐỌC HIỂU OUTPUT ENHANCED SEARCH ENGINE")
    print("="*70)
    
    # 1. Analyze build output
    engine = analyze_build_output()
    
    # 2. Analyze search output  
    analyze_search_output(engine)
    
    # 3. Explain scores
    analyze_scores_and_ranking()
    
    # 4. Interactive guide
    interactive_output_guide()
    
    # 5. Sample session
    create_sample_search_session()
    
    print("\n" + "="*70)
    print("✅ HOÀN TẤT HƯỚNG DẪN!")
    print("💡 Bây giờ bạn đã hiểu cách đọc và phân tích output!")
    print("🚀 Hãy thử chạy: python EnhancedSearchEngine.py")

if __name__ == "__main__":
    main()