"""
Tokenizer.py
Chịu trách nhiệm: Token hóa văn bản tiếng Việt
"""

import re
import unicodedata
from typing import List, Set
from underthesea import word_tokenize
from pyvi import ViTokenizer


class VietnameseTokenizer:
    """
    Lớp xử lý tokenization cho tiếng Việt.
    
    Nguyên tắc loose coupling:
    - Không phụ thuộc vào DataHandler
    - Có thể hoạt động độc lập
    - Interface đơn giản, dễ thay thế
    """
    
    def __init__(self, 
                 use_stopwords: bool = True,
                 library: str = 'underthesea'):
        """
        Khởi tạo Tokenizer
        
        Args:
            use_stopwords: Có loại bỏ stopwords không
            library: Thư viện sử dụng ('underthesea' hoặc 'pyvi')
        """
        self.use_stopwords = use_stopwords
        self.library = library
        self.stopwords = self._load_stopwords() if use_stopwords else set()
        
    def _load_stopwords(self) -> Set[str]:
        """
        Load danh sách stopwords tiếng Việt
        
        Returns:
            Set[str]: Tập hợp stopwords
        """
        # Danh sách stopwords tiếng Việt cơ bản
        stopwords = {
            'và', 'của', 'có', 'cho', 'với', 'được', 'từ', 'trong',
            'là', 'một', 'các', 'để', 'theo', 'này', 'đó', 'những',
            'nhưng', 'hoặc', 'nếu', 'thì', 'khi', 'vì', 'do', 'bởi',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'
        }
        return stopwords
    
    def normalize_text(self, text: str) -> str:
        """
        Chuẩn hóa văn bản tiếng Việt
        
        Args:
            text: Văn bản cần chuẩn hóa
            
        Returns:
            str: Văn bản đã chuẩn hóa
        """
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Chuyển về lowercase
        text = text.lower()
        
        # Loại bỏ các ký tự đặc biệt, giữ lại chữ cái tiếng Việt và số
        text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str, remove_stopwords: bool = None) -> List[str]:
        """
        Token hóa văn bản tiếng Việt
        
        Args:
            text: Văn bản cần tokenize
            remove_stopwords: Có loại bỏ stopwords không (None = dùng config mặc định)
            
        Returns:
            List[str]: Danh sách các tokens
        """
        # Chuẩn hóa văn bản
        text = self.normalize_text(text)
        
        # Tokenize dựa trên thư viện được chọn
        if self.library == 'underthesea':
            tokens = word_tokenize(text, format="text").split()
        elif self.library == 'pyvi':
            tokens = ViTokenizer.tokenize(text).split()
        else:
            # Fallback: tokenize đơn giản bằng split
            tokens = text.split()
        
        # Loại bỏ stopwords nếu cần
        if remove_stopwords is None:
            remove_stopwords = self.use_stopwords
            
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stopwords]
        
        # Loại bỏ tokens quá ngắn (< 2 ký tự)
        tokens = [token for token in tokens if len(token) >= 2]
        
        return tokens
    
    def tokenize_documents(self, documents: List[str]) -> List[List[str]]:
        """
        Token hóa nhiều documents
        
        Args:
            documents: Danh sách các documents
            
        Returns:
            List[List[str]]: Danh sách các document đã tokenize
        """
        return [self.tokenize(doc) for doc in documents]
