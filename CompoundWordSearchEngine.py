#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Vietnamese Search Engine với Compound Word Support
"""

import json
import time
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from VietnameseCompoundTokenizer import VietnameseCompoundTokenizer

class CompoundWordSearchEngine:
    """
    Search Engine với hỗ trợ đặc biệt cho từ ghép tiếng Việt
    """
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents = []
        self.chunks = []
        self.tokenizer = VietnameseCompoundTokenizer()
        
        # Index structures
        self.chunk_to_doc_map = {}
        self.term_to_chunks = defaultdict(list)  # inverted index
        self.compound_to_chunks = defaultdict(list)  # compound word index
        
    def load_documents(self):
        """Load documents từ JSON file"""
        print("📋 Loading documents...")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        print(f"   ✓ Loaded {len(self.documents)} documents")
    
    def create_chunks(self, chunk_size: int = 200):
        """Tạo chunks từ documents"""
        print("🧩 Creating chunks...")
        
        chunk_id = 0
        for doc_id, doc in enumerate(self.documents):
            content = doc.get('content', '')
            filename = doc.get('filename', f'Document {doc_id}')
            
            # Simple chunking by sentences/words
            words = content.split()
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_content = ' '.join(chunk_words)
                
                if len(chunk_content.strip()) > 20:  # Skip very short chunks
                    chunk = {
                        'chunk_id': chunk_id,
                        'doc_id': doc_id,
                        'content': chunk_content,
                        'filename': filename,
                        'start_word': i,
                        'end_word': min(i + chunk_size, len(words))
                    }
                    
                    self.chunks.append(chunk)
                    self.chunk_to_doc_map[chunk_id] = doc_id
                    chunk_id += 1
        
        print(f"   ✓ Created {len(self.chunks)} chunks")
    
    def build_compound_index(self):
        """Xây dựng index với compound word support"""
        print("🔍 Building compound word index...")
        
        for chunk in self.chunks:
            chunk_id = chunk['chunk_id']
            content = chunk['content']
            
            # Enhanced tokenization
            enhanced = self.tokenizer.tokenize_enhanced(content)
            
            # Index individual tokens
            for token in enhanced['tokens']:
                if len(token) > 2:  # Skip very short tokens
                    self.term_to_chunks[token].append(chunk_id)
            
            # Index compound words (higher priority)
            for compound in enhanced['compounds']:
                self.compound_to_chunks[compound].append(chunk_id)
                # Also add to term index với boost
                self.term_to_chunks[compound].append(chunk_id)
            
            # Index bigrams (for fallback)
            for bigram in enhanced['bigrams']:
                if bigram not in enhanced['compounds']:  # Avoid duplicates
                    self.term_to_chunks[bigram].append(chunk_id)
        
        # Statistics
        total_terms = len(self.term_to_chunks)
        total_compounds = len(self.compound_to_chunks)
        
        print(f"   ✓ Indexed {total_terms} terms")
        print(f"   ✓ Indexed {total_compounds} compound words")
    
    def calculate_compound_score(self, query_terms: List[str], chunk: Dict) -> float:
        """
        Tính score với compound word boost
        
        Strategy:
        - Compound words get higher weight
        - Exact phrase matches get boost
        - Individual tokens get standard weight
        """
        content = chunk['content'].lower()
        content_enhanced = self.tokenizer.tokenize_enhanced(content)
        
        score = 0.0
        matches = []
        
        for term in query_terms:
            # Check if term is a compound word
            is_compound = ' ' in term
            
            if term in content.lower():
                if is_compound:
                    # Compound word exact match: high score
                    boost = 3.0
                    score += boost
                    matches.append(f"compound:{term}")
                else:
                    # Individual token match: standard score
                    boost = 1.0
                    term_count = content.lower().count(term)
                    score += boost * term_count / len(content.split())
                    matches.append(f"token:{term}({term_count})")
            
            # Partial compound matching
            elif is_compound:
                compound_tokens = term.split()
                partial_matches = 0
                for token in compound_tokens:
                    if token in content.lower():
                        partial_matches += 1
                
                if partial_matches > 0:
                    # Partial compound match: medium score
                    partial_score = (partial_matches / len(compound_tokens)) * 1.5
                    score += partial_score
                    matches.append(f"partial:{term}({partial_matches}/{len(compound_tokens)})")
        
        # Normalize by content length
        normalized_score = score / max(len(content.split()), 10)
        
        return normalized_score, matches
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search với compound word support"""
        
        # Get enhanced search terms
        search_terms = self.tokenizer.create_search_terms(query)
        
        print(f"🔍 Query: '{query}'")
        print(f"   Search terms: {search_terms}")
        
        # Collect candidate chunks
        candidate_chunks = set()
        
        for term in search_terms:
            # From compound index
            if term in self.compound_to_chunks:
                candidate_chunks.update(self.compound_to_chunks[term])
            
            # From regular term index
            if term in self.term_to_chunks:
                candidate_chunks.update(self.term_to_chunks[term])
        
        # Score candidates
        scored_chunks = []
        
        for chunk_id in candidate_chunks:
            chunk = self.chunks[chunk_id]
            score, matches = self.calculate_compound_score(search_terms, chunk)
            
            if score > 0:
                scored_chunks.append({
                    'chunk_id': chunk_id,
                    'doc_id': chunk['doc_id'],
                    'filename': chunk['filename'], 
                    'content': chunk['content'],
                    'score': score,
                    'matches': matches
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Group by document và lấy best chunks
        doc_results = defaultdict(list)
        for chunk_result in scored_chunks:
            doc_id = chunk_result['doc_id']
            doc_results[doc_id].append(chunk_result)
        
        # Create final results
        final_results = []
        
        for doc_id, chunk_list in doc_results.items():
            # Sort chunks by score
            chunk_list.sort(key=lambda x: x['score'], reverse=True)
            best_chunk = chunk_list[0]
            
            # Document score = max chunk score
            doc_score = best_chunk['score']
            
            final_results.append({
                'doc_id': doc_id,
                'filename': best_chunk['filename'],
                'score': doc_score,
                'best_chunk': best_chunk,
                'total_chunks': len(chunk_list),
                'preview': best_chunk['content'][:200] + "..." if len(best_chunk['content']) > 200 else best_chunk['content']
            })
        
        # Sort final results
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        return final_results[:top_k]
    
    def print_results(self, query: str, results: List[Dict]):
        """In kết quả search một cách đẹp"""
        
        print(f"\n🎯 COMPOUND SEARCH RESULTS FOR: '{query}'")
        print("=" * 70)
        
        if not results:
            print("   No results found.")
            return
        
        for i, result in enumerate(results, 1):
            score = result['score']
            filename = result['filename']
            preview = result['preview']
            matches = result['best_chunk']['matches']
            
            print(f"\n[{i}] Score: {score:.4f} | File: {filename}")
            print(f"    Preview: {preview}")
            print(f"    Matches: {', '.join(matches)}")
            print(f"    Chunks found: {result['total_chunks']}")


def test_compound_search():
    """Test compound search engine"""
    
    print("🚀 COMPOUND WORD SEARCH ENGINE TEST")
    print("=" * 70)
    
    # Initialize
    engine = CompoundWordSearchEngine('data_content.json')
    
    # Build index
    start_time = time.time()
    engine.load_documents()
    engine.create_chunks()
    engine.build_compound_index()
    build_time = time.time() - start_time
    
    print(f"\n✅ Index built in {build_time:.2f}seconds")
    print(f"   📄 Documents: {len(engine.documents)}")
    print(f"   🧩 Chunks: {len(engine.chunks)}")
    print(f"   🔤 Terms: {len(engine.term_to_chunks)}")
    print(f"   📝 Compounds: {len(engine.compound_to_chunks)}")
    
    # Test queries
    test_queries = [
        "Việt Nam",
        "Hồ Chí Minh", 
        "Bà Triệu sinh năm nao",
        "khởi nghĩa Hai Bà Trưng",
        "chiến dịch Điện Biên Phủ",
        "cách mạng tháng tám"
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        
        start = time.time()
        results = engine.search(query, top_k=3)
        search_time = time.time() - start
        
        engine.print_results(query, results)
        print(f"\n⏱️ Search time: {search_time:.3f}s")


def compare_with_simple_search():
    """So sánh với simple search"""
    
    print("\n" + "="*70)
    print("📊 COMPARISON: Compound vs Simple Search")
    print("=" * 70)
    
    from EnhancedSearchEngine_Fixed import FixedEnhancedSearchEngine
    
    # Initialize engines
    compound_engine = CompoundWordSearchEngine('data_content.json')
    compound_engine.load_documents()
    compound_engine.create_chunks()
    compound_engine.build_compound_index()
    
    simple_engine = FixedEnhancedSearchEngine('data_content.json')
    simple_engine.build_index()
    
    # Test cases
    test_cases = ["Việt Nam", "Hồ Chí Minh", "Điện Biên Phủ"]
    
    for query in test_cases:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 50)
        
        # Compound search
        compound_results = compound_engine.search(query, top_k=3)
        print("📝 Compound Search:")
        for i, result in enumerate(compound_results[:3], 1):
            print(f"   [{i}] {result['filename']} (Score: {result['score']:.4f})")
        
        # Simple search  
        simple_results = simple_engine.search(query, top_k=3)
        print("📄 Simple Search:")
        for i, result in enumerate(simple_results[:3], 1):
            print(f"   [{i}] {result['file_name']} (Score: {result['score']:.4f})")


if __name__ == "__main__":
    test_compound_search()
    compare_with_simple_search()