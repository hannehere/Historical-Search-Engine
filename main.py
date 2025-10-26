from typing import List, Dict, Tuple
from DataHandler import DataHandler
from Tokenizer import VietnameseTokenizer
from DataRetrieval import DataRetrieval


class SearchEngine:
    """
    Lớp chính điều phối search engine.
    
    Kiến trúc loose coupling:
    - Mỗi component độc lập
    - Giao tiếp qua interface rõ ràng
    - Dễ dàng thay thế hoặc nâng cấp từng component
    """
    
    def __init__(self, data_path: str, config: Dict = None):
        """
        Khởi tạo Search Engine
        
        Args:
            data_path: Đường dẫn đến file JSON dataset
            config: Cấu hình cho các components
        """
        self.config = config or self._default_config()
        
        # Khởi tạo các components
        print("=" * 60)
        print("KHỞI TẠO SEARCH ENGINE")
        print("=" * 60)
        
        # 1. Data Handler
        print("\n[1/4] Khởi tạo DataHandler...")
        self.data_handler = DataHandler(data_path)
        
        # 2. Tokenizer
        print("\n[2/4] Khởi tạo Tokenizer...")
        self.tokenizer = VietnameseTokenizer(
            use_stopwords=self.config['use_stopwords'],
            library=self.config['tokenizer_library']
        )
        
        # 3. Data Retrieval
        print("\n[3/4] Khởi tạo DataRetrieval...")
        self.retrieval = DataRetrieval(
            embedding_model=self.config['embedding_model'],
            use_bm25=self.config['use_bm25'],
            use_embedding=self.config['use_embedding'],
            bm25_weight=self.config['bm25_weight']
        )
        
        # 4. Storage cho documents
        self.documents = []
        self.tokenized_documents = []
        
        print("\n✓ Khởi tạo hoàn tất!")
    
    def _default_config(self) -> Dict:
        """
        Cấu hình mặc định
        
        Returns:
            Dict: Cấu hình mặc định
        """
        return {
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',  # hoặc 'pyvi'
            'embedding_model': 'keepitreal/vietnamese-sbert',
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.5,
            'top_k_results': 10
        }
    
    def build_index(self):
        """
        Xây dựng index cho toàn bộ documents
        
        Quy trình:
        1. Load documents từ DataHandler
        2. Tokenize documents
        3. Tạo index với DataRetrieval
        """
        print("\n" + "=" * 60)
        print("XÂY DỰNG INDEX")
        print("=" * 60)
        
        # Bước 1: Load documents
        print("\n[1/3] Đang load documents...")
        self.documents = self.data_handler.load_data()
        
        # Trích xuất content
        contents = [doc['content'] for doc in self.documents]
        
        # Bước 2: Tokenize
        print("\n[2/3] Đang tokenize documents...")
        self.tokenized_documents = self.tokenizer.tokenize_documents(contents)
        print(f"✓ Đã tokenize {len(self.tokenized_documents)} documents")
        
        # Bước 3: Index
        print("\n[3/3] Đang tạo index...")
        self.retrieval.index_documents(
            tokenized_docs=self.tokenized_documents,
            raw_docs=contents
        )
        
        print("\n✓ Hoàn tất xây dựng index!")
        print("=" * 60)
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Tìm kiếm documents liên quan đến query
        
        Args:
            query: Câu truy vấn
            top_k: Số kết quả trả về
            
        Returns:
            List[Dict]: Danh sách documents kết quả với score
        """
        if top_k is None:
            top_k = self.config['top_k_results']
        
        # Tokenize query
        query_tokens = self.tokenizer.tokenize(query)
        
        # Retrieve
        results = self.retrieval.retrieve(
            query=query,
            query_tokens=query_tokens,
            top_k=top_k
        )
        
        # Format kết quả
        formatted_results = []
        for doc_id, score in results:
            doc = self.documents[doc_id]
            formatted_results.append({
                'doc_id': doc_id,
                'score': score,
                'file_name': doc['file_name'],
                'content': doc['content'][:500] + '...' if len(doc['content']) > 500 else doc['content']
            })
        
        return formatted_results
    
    def print_results(self, query: str, results: List[Dict]):
        """
        In kết quả tìm kiếm ra console
        
        Args:
            query: Câu truy vấn
            results: Danh sách kết quả
        """
        print("\n" + "=" * 60)
        print(f"KẾT QUẢ TÌM KIẾM: '{query}'")
        print("=" * 60)
        
        if not results:
            print("\nKhông tìm thấy kết quả nào.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Score: {result['score']:.4f}")
            print(f"File: {result['file_name']}")
            print(f"Content: {result['content'][:200]}...")
            print("-" * 60)


def main():
    """
    Hàm main để chạy search engine
    """
    # Đường dẫn đến dataset
    DATA_PATH = "data_content.json"
    
    # Cấu hình tùy chỉnh (optional)
    config = {
        'use_stopwords': True,
        'tokenizer_library': 'underthesea',
        'embedding_model': 'keepitreal/vietnamese-sbert',
        'use_bm25': True,
        'use_embedding': True,
        'bm25_weight': 0.5,
        'top_k_results': 5
    }
    
    # Khởi tạo search engine
    engine = SearchEngine(DATA_PATH, config)
    
    # Xây dựng index
    engine.build_index()
    
    # # Ví dụ tìm kiếm
    # queries = [
    #     "Hồ Chí Minh",
    #     "Điện Biên Phủ",
    #     "trên không"
    # ]
    
    # for query in queries:
    #     results = engine.search(query, top_k=5)
    #     engine.print_results(query, results)
    
    # Interactive search
    print("\n" + "=" * 60)
    print("INTERACTIVE SEARCH MODE")
    print("=" * 60)
    print("Nhập 'quit' để thoát\n")
    
    while True:
        query = input("Nhập query: ").strip()

        if query.lower() == 'quit':
            print("Tạm biệt!")
            break
        
        if not query:
            continue
        
        import os
        os.system('cls')
        results = engine.search(query)
        engine.print_results(query, results)


if __name__ == "__main__":
    main()
