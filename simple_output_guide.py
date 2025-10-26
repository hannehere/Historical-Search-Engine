"""
simple_output_guide.py
Hướng dẫn đơn giản để hiểu output
"""

def explain_build_output():
    """Giải thích output khi build index"""
    print("🔧 GIẢI THÍCH OUTPUT BUILD INDEX")
    print("="*50)
    
    print("\n📋 CÁC BƯỚC BUILD:")
    print("1️⃣ [1/4] Loading documents and creating chunks:")
    print("   - Đọc file JSON: ✓ Đã load 207 documents từ data_content.json")
    print("   - Tạo chunks: An Dương Vương.md: 10 chunks")
    print("   - Mỗi document được chia thành nhiều chunks nhỏ")
    print("   - Số chunks phụ thuộc vào độ dài document")
    
    print("\n2️⃣ [2/4] Tokenizing chunks:")
    print("   - ✓ Tokenized 5968 chunks")
    print("   - Chuyển text thành từ (tokens)")
    print("   - Loại bỏ stopwords, chuẩn hóa tiếng Việt")
    
    print("\n3️⃣ [3/4] Indexing chunks:")
    print("   - 🔍 Indexing 5968 chunks...")
    print("   - ✓ BM25 indexed 5968 chunks")
    print("   - Tạo index để tìm kiếm nhanh")
    
    print("\n4️⃣ [4/4] Performance Analysis:")
    print("   - Total chunks: 5,968 (tổng số đoạn văn)")
    print("   - Total documents: 207 (tổng số tài liệu)")
    print("   - Avg chunks/doc: 28.8 (trung bình chunks mỗi document)")
    print("   - Chunk sizes: 35-256 words (kích thước chunks)")

def explain_search_output():
    """Giải thích output khi search"""
    print("\n🔍 GIẢI THÍCH OUTPUT SEARCH")
    print("="*50)
    
    print("\n📄 DOCUMENT MODE OUTPUT:")
    print("   [1] Chiến tranh Việt Nam.md (Score: 2.011)")
    print("       Preview: [Chiến tranh Việt Nam Chiến tranh...] ")
    print("   👆 Giải thích:")
    print("     - File name: Tên tài liệu")
    print("     - Score: Độ liên quan (2.011 = rất liên quan)")
    print("     - Preview: Đoạn đầu của nội dung")
    
    print("\n🧩 CHUNK MODE OUTPUT:")
    print("   [1] Chiến tranh Việt Nam.md - sub_section")
    print("       Score: 2.011")
    print("       Content: 7, nhân vật chính là một cựu binh...")
    print("   👆 Giải thích:")
    print("     - File name: Tên tài liệu")
    print("     - Chunk type: Loại đoạn (sub_section, section, paragraph)")
    print("     - Score: Độ liên quan")
    print("     - Content: Nội dung cụ thể của đoạn")

def explain_scores():
    """Giải thích về scores"""
    print("\n📊 HIỂU VỀ SCORES")
    print("="*50)
    
    print("\n🎯 SCORE LÀ GÌ?")
    print("   - Đo độ liên quan giữa query và kết quả")
    print("   - Càng cao = càng liên quan")
    
    print("\n📈 THANG ĐIỂM:")
    print("   Score > 2.0   = Rất liên quan ⭐⭐⭐")
    print("   Score 1.0-2.0 = Liên quan cao ⭐⭐")
    print("   Score 0.5-1.0 = Liên quan trung bình ⭐")
    print("   Score < 0.5   = Liên quan thấp")
    
    print("\n🔢 VÍ DỤ:")
    print("   Query: 'Bà Triệu'")
    print("   [1] Bà Triệu.md (Score: 2.528) ← Perfect match!")
    print("   [2] Việt Nam.md (Score: 2.189) ← Có đề cập đến Bà Triệu")
    print("   [3] Thăng Long.md (Score: 1.780) ← Ít liên quan hơn")

def explain_chunk_types():
    """Giải thích về chunk types"""
    print("\n🏷️ CHUNK TYPES")
    print("="*50)
    
    print("\n📝 CÁC LOẠI CHUNKS:")
    print("   📄 overview     = Tổng quan document (quan trọng nhất)")
    print("   📑 section      = Phần chính (H1, H2 headers)")
    print("   📰 sub_section  = Phần phụ (H3, H4 headers)")
    print("   📝 paragraph    = Đoạn văn thường")
    print("   🔲 fixed_chunk  = Chunks có kích thước cố định")
    
    print("\n🎯 ĐỘ ƯU TIÊN:")
    print("   overview > section > sub_section > paragraph > fixed_chunk")
    print("   (Hệ thống sẽ boost score cho chunks quan trọng hơn)")

def explain_search_modes():
    """Giải thích các search modes"""
    print("\n🎮 SEARCH MODES")
    print("="*50)
    
    print("\n📄 DOCUMENT MODE:")
    print("   - Tìm tài liệu liên quan")
    print("   - Kết quả: Tên file + score + preview")
    print("   - Dùng khi: Muốn tìm tài liệu tổng quan")
    
    print("\n🧩 CHUNK MODE:")
    print("   - Tìm đoạn văn cụ thể")
    print("   - Kết quả: File + chunk type + score + content")
    print("   - Dùng khi: Muốn tìm thông tin chi tiết")
    
    print("\n🌐 CONTEXT MODE:")
    print("   - Tìm với ngữ cảnh xung quanh")
    print("   - Kết quả: File + score + total chunks")
    print("   - Dùng khi: Muốn hiểu context đầy đủ")

def show_real_examples():
    """Hiển thị ví dụ thực tế"""
    print("\n💡 VÍ DỤ THỰC TẾ")
    print("="*50)
    
    print("\n🔍 Query: 'Hồ Chí Minh'")
    print("📄 Document Mode Result:")
    print("   [1] Hồ Chí Minh.md (Score: 1.867)")
    print("       → Tài liệu chính về Hồ Chí Minh")
    print("   [2] Ngô Đình Diệm.md (Score: 1.790)")
    print("       → Có nhắc đến Hồ Chí Minh")
    
    print("\n🧩 Chunk Mode Result:")
    print("   [1] Hồ Chí Minh.md - sub_section (Score: 1.867)")
    print("       Content: được chọn là tên gọi chính thức...")
    print("       → Đoạn cụ thể về tên gọi của Hồ Chí Minh")
    
    print("\n🔍 Query: 'chiến tranh Việt Nam'")
    print("📄 Document Mode Result:")
    print("   [1] Chiến tranh Việt Nam.md (Score: 2.011)")
    print("       → Perfect match với query")
    print("   [2] Việt Nam hóa chiến tranh.md (Score: 1.918)")
    print("       → Chủ đề liên quan")

def interactive_commands():
    """Hướng dẫn các lệnh interactive"""
    print("\n💬 LỆNH INTERACTIVE MODE")
    print("="*50)
    
    print("\n🎮 CÁC LỆNH CƠ BẢN:")
    print("   Gõ query        → Tìm kiếm")
    print("   :mode document  → Chuyển document mode")
    print("   :mode chunk     → Chuyển chunk mode")
    print("   :mode context   → Chuyển context mode")
    print("   :explain on     → Bật giải thích chi tiết")
    print("   :stats          → Xem thống kê hệ thống")
    print("   :quit           → Thoát")
    
    print("\n📝 VÍ DỤ SESSION:")
    print("   [document] Search: Bà Triệu")
    print("   → Hiển thị kết quả document mode")
    print("   ")
    print("   [document] Search: :mode chunk")
    print("   ✓ Search mode changed to: chunk")
    print("   ")
    print("   [chunk] Search: Bà Triệu")
    print("   → Hiển thị kết quả chunk mode")

def main():
    """Hàm chính"""
    print("🎯 HƯỚNG DẪN ĐỌC HIỂU OUTPUT ENHANCED SEARCH ENGINE")
    print("="*70)
    
    explain_build_output()
    explain_search_output() 
    explain_scores()
    explain_chunk_types()
    explain_search_modes()
    show_real_examples()
    interactive_commands()
    
    print("\n" + "="*70)
    print("✅ HOÀN TẤT HƯỚNG DẪN!")
    print("🚀 BẠN ĐÃ HIỂU CÁCH ĐỌC OUTPUT!")
    print("💡 Hãy thử chạy: python simple_test.py")

if __name__ == "__main__":
    main()