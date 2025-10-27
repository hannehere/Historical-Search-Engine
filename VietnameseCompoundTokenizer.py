#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Vietnamese Tokenizer với hỗ trợ compound words và n-grams
"""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class VietnameseCompoundTokenizer:
    """
    Tokenizer đặc biệt cho tiếng Việt với hỗ trợ:
    - Compound words (từ ghép)
    - Named entities (tên riêng) 
    - N-gram extraction
    - Context-aware processing
    """
    
    def __init__(self):
        self.compound_words = self._load_compound_words()
        self.named_entities = self._load_named_entities()
        self.stopwords = self._load_vietnamese_stopwords()
        
    def _load_compound_words(self) -> Set[str]:
        """Load danh sách từ ghép tiếng Việt quan trọng"""
        compound_words = {
            # Địa danh
            'việt nam', 'đông nam á', 'bắc việt', 'nam việt', 
            'trung quốc', 'hoa kỳ', 'liên xô', 'nhật bản',
            'điện biên phủ', 'cao bằng', 'lạng sơn', 'quảng ninh',
            'hà nội', 'tp hồ chí minh', 'sài gòn', 'đà nẵng',
            
            # Tên người (patterns)
            'hồ chí minh', 'nguyễn ái quốc', 'bác hồ', 
            'bà triệu', 'triệu thị trinh', 'hai bà trưng',
            'trần hưng đạo', 'lê lợi', 'nguyễn huệ',
            'võ nguyên giáp', 'phạm văn đồng',
            
            # Sự kiện lịch sử
            'chiến tranh việt nam', 'kháng chiến chống pháp',
            'kháng chiến chống mỹ', 'giải phóng miền nam',
            'thống nhất đất nước', 'cách mạng tháng tám',
            'khởi nghĩa', 'cách mạng', 'giải phóng',
            
            # Tổ chức
            'mặt trận giải phóng', 'việt minh', 'đảng cộng sản',
            'chính phủ', 'quốc hội', 'ủy ban', 'ban chấp hành',
            
            # Khái niệm
            'độc lập', 'tự do', 'hòa bình', 'thống nhất',
            'dân tộc', 'tổ quốc', 'quê hương', 'đất nước',
            'lãnh tụ', 'anh hùng', 'liệt sĩ', 'nhân dân',
            
            # Thời gian
            'thế kỷ', 'thiên niên kỷ', 'triều đại', 'thời kỳ',
            'năm nay', 'năm trước', 'ngày nay', 'thời cổ'
        }
        return compound_words
    
    def _load_named_entities(self) -> Dict[str, List[str]]:
        """Load named entities với các variants"""
        entities = {
            'hồ chí minh': ['hồ chí minh', 'nguyễn ái quốc', 'bác hồ', 'chủ tịch hồ chí minh'],
            'bà triệu': ['bà triệu', 'triệu thị trinh', 'triệu trinh nương', 'triệu quốc trinh'],
            'việt nam': ['việt nam', 'nước việt', 'đại việt', 'annam', 'cochinchina'],
            'điện biên phủ': ['điện biên phủ', 'điện biên', 'dien bien phu'],
            'hai bà trưng': ['hai bà trưng', 'trưng trắc', 'trưng nhị', 'bà trưng'],
            'chiến tranh việt nam': ['chiến tranh việt nam', 'vietnam war', 'kháng chiến chống mỹ']
        }
        return entities
    
    def _load_vietnamese_stopwords(self) -> Set[str]:
        """Load stopwords tiếng Việt cơ bản"""
        return {
            'là', 'của', 'và', 'có', 'được', 'trong', 'với', 'từ', 'về', 'cho',
            'một', 'hai', 'ba', 'này', 'đó', 'những', 'các', 'tất cả', 'mọi',
            'để', 'sẽ', 'đã', 'đang', 'rất', 'rất nhiều', 'nhiều', 'ít'
        }
    
    def extract_compound_words(self, text: str) -> List[str]:
        """Extract compound words từ text"""
        text_lower = text.lower()
        found_compounds = []
        
        for compound in self.compound_words:
            if compound in text_lower:
                found_compounds.append(compound)
        
        # Sort by length (longest first) để avoid conflicts
        found_compounds.sort(key=len, reverse=True)
        return found_compounds
    
    def extract_named_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities và normalize về canonical form"""
        text_lower = text.lower()
        found_entities = []
        
        for canonical, variants in self.named_entities.items():
            for variant in variants:
                if variant in text_lower:
                    found_entities.append((variant, canonical))
        
        return found_entities
    
    def generate_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """Generate n-grams từ token list"""
        if len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
    
    def tokenize_basic(self, text: str) -> List[str]:
        """Basic tokenization (word-level)"""
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        
        # Split by whitespace
        tokens = text.split()
        
        # Filter stopwords
        tokens = [token for token in tokens if token not in self.stopwords]
        
        return tokens
    
    def tokenize_enhanced(self, text: str) -> Dict[str, List[str]]:
        """
        Enhanced tokenization với compound words và n-grams
        
        Returns:
            Dict với keys: 'tokens', 'compounds', 'entities', 'bigrams', 'trigrams'
        """
        # Basic tokens
        basic_tokens = self.tokenize_basic(text)
        
        # Extract compound words
        compounds = self.extract_compound_words(text)
        
        # Extract named entities
        entities = self.extract_named_entities(text)
        
        # Generate n-grams
        bigrams = self.generate_ngrams(basic_tokens, 2)
        trigrams = self.generate_ngrams(basic_tokens, 3)
        
        return {
            'tokens': basic_tokens,
            'compounds': compounds,
            'entities': entities,
            'bigrams': bigrams,
            'trigrams': trigrams
        }
    
    def create_search_terms(self, query: str) -> List[str]:
        """
        Tạo search terms optimized cho compound words
        
        Strategy:
        1. Extract compound words first
        2. Add individual tokens (except those in compounds)
        3. Add relevant bigrams
        4. Normalize entities
        """
        enhanced = self.tokenize_enhanced(query)
        
        search_terms = []
        used_tokens = set()
        
        # 1. Add compound words (highest priority)
        for compound in enhanced['compounds']:
            search_terms.append(compound)
            # Mark component tokens as used
            compound_tokens = compound.split()
            used_tokens.update(compound_tokens)
        
        # 2. Add normalized entities
        for variant, canonical in enhanced['entities']:
            if canonical not in search_terms:
                search_terms.append(canonical)
            # Mark variant tokens as used
            variant_tokens = variant.split()
            used_tokens.update(variant_tokens)
        
        # 3. Add remaining individual tokens
        for token in enhanced['tokens']:
            if token not in used_tokens and len(token) > 2:
                search_terms.append(token)
        
        # 4. Add meaningful bigrams (if no compounds found)
        if len(enhanced['compounds']) == 0 and len(enhanced['bigrams']) > 0:
            # Add top 2 bigrams
            for bigram in enhanced['bigrams'][:2]:
                if bigram not in search_terms:
                    search_terms.append(bigram)
        
        return search_terms


def test_compound_tokenizer():
    """Test compound tokenizer"""
    
    print("🔬 TESTING COMPOUND TOKENIZER")
    print("=" * 60)
    
    tokenizer = VietnameseCompoundTokenizer()
    
    test_queries = [
        "Việt Nam",
        "Hồ Chí Minh", 
        "Bà Triệu sinh năm nao",
        "khởi nghĩa Hai Bà Trưng",
        "chiến dịch Điện Biên Phủ",
        "cách mạng tháng tám",
        "kháng chiến chống Pháp",
        "giải phóng miền Nam"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        # Enhanced tokenization
        enhanced = tokenizer.tokenize_enhanced(query)
        
        print(f"   Basic tokens: {enhanced['tokens']}")
        print(f"   Compounds: {enhanced['compounds']}")
        print(f"   Entities: {enhanced['entities']}")
        print(f"   Bigrams: {enhanced['bigrams']}")
        
        # Search terms
        search_terms = tokenizer.create_search_terms(query)
        print(f"   🎯 Search terms: {search_terms}")
        
        print("-" * 40)


def compare_tokenization_approaches():
    """So sánh các cách tokenize"""
    
    print("\n⚖️ COMPARING TOKENIZATION APPROACHES")
    print("=" * 60)
    
    # Simple tokenizer inline
    class SimpleTokenizer:
        def tokenize(self, text):
            text = text.lower()
            text = re.sub(r'[^\w\s]', ' ', text)
            return text.split()
    
    simple_tokenizer = SimpleTokenizer()
    compound_tokenizer = VietnameseCompoundTokenizer()
    
    test_cases = [
        "Việt Nam là quê hương",
        "Hồ Chí Minh lãnh tụ", 
        "khởi nghĩa Bà Triệu",
        "chiến dịch Điện Biên Phủ"
    ]
    
    for text in test_cases:
        print(f"\n📄 Text: '{text}'")
        
        # Simple approach
        simple_tokens = simple_tokenizer.tokenize(text)
        print(f"   Simple: {simple_tokens}")
        
        # Compound approach
        search_terms = compound_tokenizer.create_search_terms(text)
        print(f"   Compound: {search_terms}")
        
        # Analysis
        simple_score = len([t for t in simple_tokens if len(t) > 2])
        compound_score = len(search_terms)
        
        print(f"   → Simple: {simple_score} meaningful terms")
        print(f"   → Compound: {compound_score} search terms")
        print(f"   → Improvement: {compound_score - simple_score:+d}")


if __name__ == "__main__":
    test_compound_tokenizer()
    compare_tokenization_approaches()