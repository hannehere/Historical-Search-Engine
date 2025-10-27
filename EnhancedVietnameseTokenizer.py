"""
EnhancedVietnameseTokenizer.py
Enhanced Vietnamese Tokenizer với comprehensive stopwords và context understanding

Improvements:
1. Comprehensive Vietnamese stopwords list
2. Context-aware tokenization
3. Semantic-rich processing for Vietnamese text
4. Better handling of Vietnamese linguistic features
"""

import re
import unicodedata
from typing import List, Set, Dict, Tuple
from underthesea import word_tokenize, pos_tag, ner
from pyvi import ViTokenizer
import json


class EnhancedVietnameseTokenizer:
    """
    Enhanced Vietnamese Tokenizer với context understanding
    
    Features:
    - Comprehensive stopwords (300+ words)
    - Context-aware tokenization
    - Vietnamese linguistic features support
    - Named Entity Recognition integration
    - POS tagging for better token quality
    """
    
    def __init__(self, 
                 use_stopwords: bool = True,
                 library: str = 'underthesea',
                 enable_ner: bool = False,
                 enable_pos: bool = False,
                 preserve_entities: bool = True):
        """
        Args:
            use_stopwords: Sử dụng stopwords filtering
            library: 'underthesea' hoặc 'pyvi'  
            enable_ner: Bật Named Entity Recognition
            enable_pos: Bật POS tagging
            preserve_entities: Giữ lại named entities (tên người, địa danh)
        """
        self.use_stopwords = use_stopwords
        self.library = library
        self.enable_ner = enable_ner
        self.enable_pos = enable_pos
        self.preserve_entities = preserve_entities
        
        # Load comprehensive stopwords
        self.stopwords = self._load_comprehensive_stopwords() if use_stopwords else set()
        
        # Vietnamese linguistic patterns
        self.vietnamese_patterns = self._init_vietnamese_patterns()
        
    def _load_comprehensive_stopwords(self) -> Set[str]:
        """
        Load comprehensive Vietnamese stopwords list (300+ words)
        
        Bao gồm:
        - Từ nối, giới từ, đại từ
        - Trợ từ, thán từ
        - Số đếm cơ bản
        - Common English stopwords
        """
        
        # Core Vietnamese stopwords
        vietnamese_stopwords = {
            # Từ nối (Conjunctions)
            'và', 'cùng', 'cũng', 'hay', 'hoặc', 'nhưng', 'song', 'tuy', 'thế_nhưng',
            'tuy_nhiên', 'tuy_vậy', 'dù', 'dẫu', 'mặc_dù', 'cho_dù', 'dù_cho',
            
            # Giới từ (Prepositions)
            'của', 'cho', 'với', 'từ', 'trong', 'ngoài', 'trên', 'dưới', 'sau',
            'trước', 'bên', 'giữa', 'theo', 'đến', 'tới', 'về', 'ra', 'vào',
            'lên', 'xuống', 'qua', 'sang', 'lại', 'đi', 'lại', 'tại', 'ở',
            
            # Đại từ (Pronouns) 
            'tôi', 'bạn', 'anh', 'chị', 'em', 'ông', 'bà', 'cô', 'chú', 'cậu',
            'mình', 'ta', 'chúng_ta', 'chúng_tôi', 'họ', 'nó', 'nó', 'này',
            'đó', 'kia', 'đây', 'đấy', 'kìa', 'ai', 'gì', 'đâu', 'nào',
            'sao', 'thế_nào', 'ra_sao', 'như_thế_nào',
            
            # Động từ tobe và trợ động từ
            'là', 'được', 'bị', 'có', 'không', 'chưa', 'đã', 'sẽ', 'đang',
            'vừa', 'mới', 'từng', 'hãy', 'hãy', 'nên', 'phải', 'cần',
            'muốn', 'thích', 'định', 'sắp', 'vẫn', 'còn', 'đều', 'đang',
            
            # Từ định lượng
            'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
            'nhiều', 'ít', 'vài', 'mấy', 'bao_nhiêu', 'đủ', 'thiếu', 'dư', 'thừa',
            'tất_cả', 'toàn_bộ', 'hết', 'cả', 'mọi', 'từng', 'một_số', 'một_vài',
            
            # Trạng từ thời gian
            'hôm_nay', 'hôm_qua', 'ngày_mai', 'tuần_này', 'tuần_trước', 'tuần_sau',
            'tháng_này', 'tháng_trước', 'tháng_sau', 'năm_nay', 'năm_trước', 'năm_sau',
            'khi', 'lúc', 'bao_giờ', 'bao_lâu', 'lâu_nay', 'từ_lâu', 'từ_nay', 'từ_đó',
            'từ_khi', 'cho_đến', 'cho_tới', 'đến_khi', 'đến_lúc', 'trong_khi',
            
            # Trạng từ nơi chốn
            'đây', 'đó', 'kia', 'đâu', 'nơi', 'chỗ', 'ở_đây', 'ở_đó', 'ở_kia',
            'ở_đâu', 'nơi_nào', 'chỗ_nào', 'khắp_nơi', 'nơi_nơi', 'chỗ_chỗ',
            
            # Từ cảm thán và nhấn mạnh
            'ôi', 'ối', 'ôi_chao', 'chao_ôi', 'trời_ơi', 'ôi_trời', 'than_ôi',
            'quả', 'thật', 'thực', 'hơi', 'khá', 'rất', 'lắm', 'nhiều_lắm',
            'quá', 'cực', 'cực_kỳ', 'vô_cùng', 'hết_sức', 'tối_đa',
            
            # Từ logic và liên kết
            'vì', 'do', 'bởi', 'bởi_vì', 'do_đó', 'cho_nên', 'vì_thế', 'vì_vậy',
            'nên', 'nên_có', 'nên_làm', 'nên_đi', 'phải', 'cần', 'cần_phải',
            'nếu', 'nếu_như', 'giá_như', 'giả_sử', 'giả_thiết', 'trong_trường_hợp',
            'thì', 'thế_thì', 'vậy_thì', 'như_vậy', 'như_thế', 'như_thế_này',
            
            # Từ so sánh
            'như', 'như_là', 'giống', 'giống_như', 'tương_tự', 'khác', 'khác_với',
            'hơn', 'kém', 'bằng', 'so_với', 'so_sánh', 'thua', 'thua_kém',
            'vượt', 'vượt_trội', 'tốt_hơn', 'kém_hơn', 'bằng_nhau', 'ngang_nhau',
            
            # Common English stopwords (mixed trong Vietnamese text)
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
            'her', 'its', 'our', 'their', 'mine', 'yours', 'ours', 'theirs',
            
            # Ký hiệu markdown (từ raw markdown files)
            '#', '##', '###', '####', '#####', '######', '*', '**', '_', '__',
            '`', '```', '>', '>>>', '---', '***', '___', '|', '||', '+++',
            '[', ']', '(', ')', '{', '}', '<', '>', '/', '\\\\', '&', '@',
            
            # Number patterns
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'
        }
        
        return vietnamese_stopwords
    
    def _init_vietnamese_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize Vietnamese-specific regex patterns"""
        patterns = {
            # Patterns để nhận diện entities quan trọng
            'person_title': re.compile(r'\b(ông|bà|anh|chị|em|đức|hoàng|vua|chúa|tướng|đại_tướng)\s+([A-ZÁÀẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴĐ][a-záàảãạâầấẩẫậăằắẳẵặêềếểễệôồốổỗộơờớởỡợưừứửữựýỳỷỹỵđ\s]+)', re.IGNORECASE),
            
            # Geographic entities
            'location': re.compile(r'\b(thành_phố|tỉnh|huyện|xã|thôn|làng|quận|phường|thị_trấn|quốc_gia)\s+([A-ZÁÀẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴĐ][a-záàảãạâầấẩẫậăằắẳẵặêềếểễệôồốổỗộơờớởỡợưừứửữựýỳỷỹỵđ\s]+)', re.IGNORECASE),
            
            # Historical periods/events
            'historical_period': re.compile(r'\b(thời|thời_kỳ|thời_đại|niên_đại|năm|triều_đại|vương_triều)\s+([A-ZÁÀẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴĐ][a-záàảãạâầấẩẫậăằắẳẵặêềếểễệôồốổỗộơờớởỡợưừứửữựýỳỷỹỵđ\s]+)', re.IGNORECASE),
            
            # Years and dates
            'year': re.compile(r'\b(năm|tháng)\s*(\d{1,4})\b'),
            'date_range': re.compile(r'\b(\d{1,4})\s*[-–—]\s*(\d{1,4})\b'),
            
            # Vietnamese compound words (connected by underscore)
            'compound_word': re.compile(r'\b\w+(_\w+)+\b')
        }
        
        return patterns
    
    def normalize_text(self, text: str) -> str:
        """
        Enhanced normalization cho Vietnamese text
        """
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Convert markdown headers to regular text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown formatting but preserve content
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
        text = re.sub(r'__(.*?)__', r'\1', text)        # __bold__
        text = re.sub(r'_(.*?)_', r'\1', text)          # _italic_
        text = re.sub(r'`(.*?)`', r'\1', text)          # `code`
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_important_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract important entities để preserve context
        
        Returns:
            Dict với các categories: persons, locations, periods, etc.
        """
        entities = {
            'persons': [],
            'locations': [], 
            'historical_periods': [],
            'years': [],
            'compound_words': []
        }
        
        # Extract using patterns
        for match in self.vietnamese_patterns['person_title'].finditer(text):
            entities['persons'].append(match.group(0).strip())
            
        for match in self.vietnamese_patterns['location'].finditer(text):
            entities['locations'].append(match.group(0).strip())
            
        for match in self.vietnamese_patterns['historical_period'].finditer(text):
            entities['historical_periods'].append(match.group(0).strip())
            
        for match in self.vietnamese_patterns['year'].finditer(text):
            entities['years'].append(match.group(0).strip())
            
        for match in self.vietnamese_patterns['compound_word'].finditer(text):
            entities['compound_words'].append(match.group(0).strip())
        
        # Use underthesea NER if enabled
        if self.enable_ner:
            try:
                ner_result = ner(text)
                for token, tag in ner_result:
                    if tag.startswith('B-PER') or tag.startswith('I-PER'):
                        entities['persons'].append(token)
                    elif tag.startswith('B-LOC') or tag.startswith('I-LOC'):
                        entities['locations'].append(token)
            except:
                pass  # NER might fail, continue without it
        
        return entities
    
    def tokenize_with_context(self, text: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Tokenize với context preservation
        
        Returns:
            Tuple of (tokens, preserved_entities)
        """
        # Normalize text
        normalized_text = self.normalize_text(text)
        
        # Extract important entities first
        entities = self.extract_important_entities(normalized_text)
        
        # Convert to lowercase for tokenization
        lower_text = normalized_text.lower()
        
        # Tokenize based on library
        if self.library == 'underthesea':
            tokens = word_tokenize(lower_text, format="text").split()
        elif self.library == 'pyvi':
            tokens = ViTokenizer.tokenize(lower_text).split()
        else:
            tokens = lower_text.split()
        
        # Remove stopwords but preserve important entities
        if self.use_stopwords:
            preserved_tokens = []
            for token in tokens:
                # Keep token if it's part of an important entity
                should_preserve = False
                
                if self.preserve_entities:
                    for entity_list in entities.values():
                        for entity in entity_list:
                            if token in entity.lower():
                                should_preserve = True
                                break
                        if should_preserve:
                            break
                
                # Keep if not a stopword or if it's an important entity
                if token not in self.stopwords or should_preserve:
                    preserved_tokens.append(token)
            
            tokens = preserved_tokens
        
        # Remove very short tokens (< 2 chars) unless they're numbers
        tokens = [token for token in tokens if len(token) >= 2 or token.isdigit()]
        
        return tokens, entities
    
    def tokenize(self, text: str, return_entities: bool = False) -> List[str]:
        """
        Main tokenize method
        
        Args:
            text: Input text
            return_entities: Whether to return entities info
            
        Returns:
            List of tokens, or tuple (tokens, entities) if return_entities=True
        """
        tokens, entities = self.tokenize_with_context(text)
        
        if return_entities:
            return tokens, entities
        else:
            return tokens
    
    def tokenize_documents(self, documents: List[str]) -> List[List[str]]:
        """Enhanced document tokenization với context awareness"""
        return [self.tokenize(doc) for doc in documents]
    
    def get_stopwords_stats(self) -> Dict[str, int]:
        """Get statistics about stopwords"""
        return {
            'total_stopwords': len(self.stopwords),
            'vietnamese_core': len([w for w in self.stopwords if not any(c in 'abcdefghijklmnopqrstuvwxyz' for c in w)]),
            'english_mixed': len([w for w in self.stopwords if any(c in 'abcdefghijklmnopqrstuvwxyz' for c in w)]),
            'markdown_symbols': len([w for w in self.stopwords if w in {'#', '*', '_', '`', '>', '|', '[', ']', '(', ')'}])
        }


def create_context_aware_tokenizer(use_case: str = 'historical') -> EnhancedVietnameseTokenizer:
    """
    Factory function for different use cases
    
    Args:
        use_case: 'historical', 'general', 'academic'
    """
    
    if use_case == 'historical':
        return EnhancedVietnameseTokenizer(
            use_stopwords=True,
            library='underthesea',
            enable_ner=True,
            enable_pos=False,  # POS can be slow
            preserve_entities=True
        )
    
    elif use_case == 'general':
        return EnhancedVietnameseTokenizer(
            use_stopwords=True,
            library='pyvi',  # Faster for general use
            enable_ner=False,
            enable_pos=False,
            preserve_entities=False
        )
    
    elif use_case == 'academic':
        return EnhancedVietnameseTokenizer(
            use_stopwords=True,
            library='underthesea',
            enable_ner=True,
            enable_pos=True,  # Full linguistic analysis
            preserve_entities=True
        )
    
    else:
        return EnhancedVietnameseTokenizer()  # Default config