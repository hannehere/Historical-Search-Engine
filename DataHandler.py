import json
from typing import List, Dict, Optional
from pathlib import Path


class DataHandler:
    """
    Nguyên tắc loose coupling:
    - Không phụ thuộc vào các module khác
    - Chỉ làm nhiệm vụ đọc/ghi dữ liệu
    - Trả về dữ liệu dạng chuẩn (List[Dict])
    """
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.documents: List[Dict] = []
        
    def load_data(self) -> List[Dict]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            
            print(f"✓ Đã load {len(self.documents)} documents từ {self.data_path}")
            return self.documents
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"File JSON không hợp lệ: {e.msg}", 
                e.doc, 
                e.pos
            )
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """
        Args:
            doc_id: ID của document (index trong list)
            
        Returns:
            Dict hoặc None nếu không tìm thấy
        """
        if 0 <= doc_id < len(self.documents):
            return self.documents[doc_id]
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """
        Returns:
            List[Dict]: Danh sách tất cả documents
        """
        return self.documents
    
    def get_documents_count(self) -> int:
        """
        Returns:
            int: Số lượng documents
        """
        return len(self.documents)
    
    def save_data(self, output_path: str):
        """
        Args:
            output_path: Đường dẫn file output
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Đã lưu {len(self.documents)} documents vào {output_path}")
