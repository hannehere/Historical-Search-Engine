#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 QUICK START GUIDE - Enhanced Vietnamese Search Engine
"""

def print_quick_start_guide():
    """In hướng dẫn nhanh để bắt đầu"""
    
    print("=" * 70)
    print("🚀 ENHANCED VIETNAMESE SEARCH ENGINE - QUICK START")
    print("=" * 70)
    
    print("\n📋 BƯỚC 1: KIỂM TRA CÀI ĐẶT")
    print("-" * 40)
    
    # Check if basic files exist
    import os
    required_files = [
        'data_content.json',
        'EnhancedSearchEngine_Fixed.py',
        'CompoundWordSearchEngine.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} - OK")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Thiếu files: {missing_files}")
        print("   → Hãy đảm bảo bạn ở đúng thư mục project!")
        return False
    
    print("\n📦 BƯỚC 2: CÀI ĐẶT PACKAGES (nếu chưa có)")
    print("-" * 40)
    print("   Chạy lệnh sau để cài đặt:")
    print("   pip install sentence-transformers rank-bm25 underthesea pyvi scikit-learn numpy")
    print("   \n   Hoặc nếu gặp lỗi, dùng:")
    print("   pip install --upgrade pip")
    print("   pip install sentence-transformers rank-bm25 scikit-learn numpy")
    
    print("\n🎯 BƯỚC 3: CHỌN PHIÊN BẢN SỬ DỤNG")
    print("-" * 40)
    print("   📄 SIMPLE VERSION (Khuyến nghị cho bắt đầu):")
    print("      python EnhancedSearchEngine_Fixed.py")
    print("      → Nhanh, ít dependencies, dễ sử dụng")
    print("      → Phù hợp test và học")
    
    print("\n   🇻🇳 COMPOUND VERSION (Cho tiếng Việt tốt hơn):")
    print("      python CompoundWordSearchEngine.py")
    print("      → Xử lý từ ghép tiếng Việt tốt hơn")
    print("      → Phù hợp cho production")
    
    print("\n   🔬 ENHANCED VERSION (Đầy đủ tính năng):")
    print("      python EnhancedSearchEngine.py")
    print("      → Cần nhiều dependencies")
    print("      → Có semantic search, embeddings")
    
    print("\n🎮 BƯỚC 4: SỬ DỤNG CƠ BẢN")
    print("-" * 40)
    print("   1. Mở terminal/command prompt")
    print("   2. cd vào thư mục project")  
    print("   3. Chạy: python EnhancedSearchEngine_Fixed.py")
    print("   4. Đợi build index (~1 phút)")
    print("   5. Gõ query để tìm kiếm!")
    
    print("\n💡 BƯỚC 5: CÁC LỆNH HỮU ÍCH")
    print("-" * 40)
    print("   Trong interactive mode:")
    print("   • Gõ query bình thường: 'Bà Triệu'")
    print("   • :mode chunk    → Chuyển chunk mode")
    print("   • :mode document → Chuyển document mode")
    print("   • :stats         → Xem thống kê")
    print("   • :quit          → Thoát")
    
    print("\n🔍 VÍ DỤ QUERIES HAY:")
    print("-" * 40)
    print("   • 'Việt Nam'")
    print("   • 'Hồ Chí Minh'")
    print("   • 'Bà Triệu sinh năm nao'") 
    print("   • 'khởi nghĩa Hai Bà Trưng'")
    print("   • 'chiến dịch Điện Biên Phủ'")
    print("   • 'cách mạng tháng tám'")
    
    return True


def quick_demo():
    """Demo nhanh với FixedEnhancedSearchEngine"""
    
    print("\n🎬 DEMO NHANH")
    print("=" * 40)
    
    try:
        from EnhancedSearchEngine_Fixed import FixedEnhancedSearchEngine
        
        print("📋 Initializing search engine...")
        engine = FixedEnhancedSearchEngine('data_content.json')
        
        print("🔧 Building index (vui lòng đợi...)...")
        engine.build_index()
        
        # Test queries
        test_queries = ["Việt Nam", "Hồ Chí Minh", "Bà Triệu"]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            results = engine.search(query, top_k=2)
            
            for i, result in enumerate(results[:2], 1):
                score = result['score']
                filename = result['file_name']
                preview = result['preview'][:100]
                print(f"   [{i}] {filename} (Score: {score:.3f})")
                print(f"       {preview}...")
        
        print("\n✅ Demo completed successfully!")
        print("   → Bây giờ bạn có thể chạy: python EnhancedSearchEngine_Fixed.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   → Hãy cài đặt dependencies trước")
    except FileNotFoundError:
        print("❌ File data_content.json không tìm thấy")
        print("   → Hãy đảm bảo file data ở đúng thư mục")
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_help():
    """Hướng dẫn sử dụng interactive mode"""
    
    print("\n📚 HƯỚNG DẪN INTERACTIVE MODE")
    print("=" * 50)
    
    print("🎯 CÁC LỆNH CƠ BẢN:")
    print("   Gõ query bình thường    → Tìm kiếm")
    print("   :mode document          → Document mode")
    print("   :mode chunk             → Chunk mode") 
    print("   :mode context           → Context mode")
    print("   :explain on/off         → Bật/tắt giải thích")
    print("   :stats                  → Thống kê hệ thống")
    print("   :help                   → Hiển thị help")
    print("   :quit hoặc :exit        → Thoát")
    
    print("\n🔍 SEARCH MODES:")
    print("   📄 Document Mode:")
    print("      → Tìm documents liên quan")
    print("      → Giống như Google search")
    print("      → Tốt cho overview")
    
    print("\n   🧩 Chunk Mode:")
    print("      → Tìm đoạn văn cụ thể")
    print("      → Chính xác hơn")
    print("      → Tốt cho thông tin chi tiết")
    
    print("\n   🌐 Context Mode:")
    print("      → Hiển thị context xung quanh")
    print("      → Tốt cho hiểu ngữ cảnh")
    
    print("\n💡 TIPS SỬ DỤNG:")
    print("   • Dùng từ khóa tiếng Việt có dấu")
    print("   • Thử cả tên đầy đủ và viết tắt")
    print("   • Chunk mode cho câu hỏi cụ thể")
    print("   • Document mode cho tìm hiểu chung")
    
    print("\n🎯 VÍ DỤ SESSION:")
    print("   [document] Search: Việt Nam")
    print("   → Hiển thị documents về Việt Nam")
    print("   ")
    print("   [document] Search: :mode chunk")
    print("   ✓ Search mode changed to: chunk")
    print("   ")
    print("   [chunk] Search: Bà Triệu sinh năm nao")
    print("   → Hiển thị đoạn văn về năm sinh Bà Triệu")


def troubleshooting_guide():
    """Hướng dẫn khắc phục sự cố"""
    
    print("\n🔧 KHẮC PHỤC SỰ CỐ")
    print("=" * 40)
    
    print("❌ LỖI: ModuleNotFoundError")
    print("   Giải pháp:")
    print("   pip install sentence-transformers rank-bm25 scikit-learn numpy")
    print("   hoặc:")
    print("   pip install --user [package_name]")
    
    print("\n❌ LỖI: FileNotFoundError: data_content.json")
    print("   Giải pháp:")
    print("   • Kiểm tra file data_content.json có trong thư mục không")
    print("   • Chạy lệnh: ls (Linux/Mac) hoặc dir (Windows)")
    print("   • Đảm bảo đang ở đúng thư mục project")
    
    print("\n❌ LỖI: Build index quá chậm")
    print("   Giải pháp:")
    print("   • Dùng FixedEnhancedSearchEngine (nhanh hơn)")
    print("   • Chờ lần đầu build (~1-2 phút)")
    print("   • Lần sau sẽ dùng cache (nhanh)")
    
    print("\n❌ LỖI: Kết quả search không hay")
    print("   Giải pháp:")
    print("   • Dùng từ khóa tiếng Việt có dấu")
    print("   • Thử CompoundWordSearchEngine")
    print("   • Thử các search modes khác nhau")
    print("   • Dùng :explain on để hiểu scoring")
    
    print("\n❌ LỖI: Python version")
    print("   Giải pháp:")
    print("   • Cần Python 3.6+")
    print("   • Chạy: python --version")
    print("   • Nếu cũ, cài Python mới từ python.org")
    
    print("\n✅ KIỂM TRA NHANH:")
    print("   python -c \"import json; print('JSON OK')\"")
    print("   python -c \"from EnhancedSearchEngine_Fixed import *; print('Import OK')\"")


if __name__ == "__main__":
    # Print complete guide
    success = print_quick_start_guide()
    
    if success:
        # Run quick demo
        print("\n" + "="*70)
        quick_demo()
        
        # Interactive help
        interactive_help()
        
        # Troubleshooting
        troubleshooting_guide()
        
        print("\n" + "="*70)
        print("🎯 READY TO START!")
        print("   → Chạy: python EnhancedSearchEngine_Fixed.py")
        print("   → Hoặc: python CompoundWordSearchEngine.py")
        print("="*70)