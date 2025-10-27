"""
EnhancedSearchEngine_Fixed.py
Fixed version of Enhanced Search Engine for testing

This version includes fallbacks and error handling to avoid dependency issues
"""

from typing import List, Dict, Tuple, Optional
import json
import time
import os


class SimpleVietnameseTokenizer:
    """Simple Vietnamese tokenizer fallback"""
    
    def __init__(self, use_stopwords=True):
        self.use_stopwords = use_stopwords
        self.stopwords = {
            'và', 'của', 'có', 'cho', 'với', 'được', 'từ', 'trong',
            'là', 'một', 'các', 'để', 'theo', 'này', 'đó', 'những',
            'nhưng', 'hoặc', 'nếu', 'thì', 'khi', 'vì', 'do', 'bởi'
        } if use_stopwords else set()
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Basic cleaning
        text = text.lower()
        import re
        text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Split by whitespace
        tokens = text.split()
        
        # Remove stopwords
        if self.use_stopwords:
            tokens = [t for t in tokens if t not in self.stopwords and len(t) >= 2]
        
        return tokens
    
    def tokenize_documents(self, documents: List[str]) -> List[List[str]]:
        return [self.tokenize(doc) for doc in documents]


class SimpleDocumentChunker:
    """Simple document chunker"""
    
    def __init__(self, chunk_size=256, overlap_size=32):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.tokenizer = SimpleVietnameseTokenizer(use_stopwords=False)
    
    def chunk_document(self, content: str, source_file: str) -> List[Dict]:
        """Simple chunking by word count"""
        words = content.split()
        chunks = []
        
        start_idx = 0
        chunk_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_content = ' '.join(chunk_words)
            
            chunk = {
                'chunk_id': f"{source_file}_{chunk_idx}",
                'content': chunk_content,
                'source_file': source_file,
                'chunk_index': chunk_idx,
                'chunk_type': 'paragraph',
                'level': 0,
                'metadata': {}
            }
            
            chunks.append(chunk)
            
            # Move start position with overlap
            start_idx = end_idx - self.overlap_size
            chunk_idx += 1
            
            if end_idx >= len(words):
                break
        
        return chunks


class SimpleBM25Retrieval:
    """Simple BM25-style retrieval"""
    
    def __init__(self):
        self.chunks = []
        self.tokenized_chunks = []
        self.chunk_to_doc_map = {}
    
    def index_chunks(self, chunks, tokenized_chunks, chunk_to_doc_map):
        """Index chunks for retrieval"""
        self.chunks = chunks
        self.tokenized_chunks = tokenized_chunks
        self.chunk_to_doc_map = chunk_to_doc_map
        print(f"✓ Indexed {len(chunks)} chunks for simple BM25 retrieval")
    
    def retrieve_chunks(self, query: str, query_tokens: List[str], top_k_chunks: int = 20):
        """Simple keyword-based retrieval"""
        chunk_scores = []
        
        for i, (chunk, tokenized_chunk) in enumerate(zip(self.chunks, self.tokenized_chunks)):
            score = self._calculate_simple_score(query_tokens, tokenized_chunk)
            chunk_scores.append((chunk, score))
        
        # Sort by score
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        return chunk_scores[:top_k_chunks]
    
    def retrieve_documents(self, query: str, query_tokens: List[str], top_k_documents: int = 10, top_k_chunks_per_search: int = 50):
        """Document-level retrieval"""
        chunk_results = self.retrieve_chunks(query, query_tokens, top_k_chunks_per_search)
        
        # Group by document
        doc_chunks = {}
        for chunk, score in chunk_results:
            doc_id = self.chunk_to_doc_map.get(chunk['chunk_id'])
            if doc_id is not None:
                if doc_id not in doc_chunks:
                    doc_chunks[doc_id] = []
                doc_chunks[doc_id].append((chunk, score))
        
        # Calculate document scores
        doc_results = []
        for doc_id, chunk_score_pairs in doc_chunks.items():
            doc_score = max(score for _, score in chunk_score_pairs)
            best_chunks = sorted(chunk_score_pairs, key=lambda x: x[1], reverse=True)[:3]
            best_chunks = [chunk for chunk, _ in best_chunks]
            
            doc_results.append((doc_id, doc_score, best_chunks))
        
        # Sort and return top documents
        doc_results.sort(key=lambda x: x[1], reverse=True)
        return doc_results[:top_k_documents]
    
    def _calculate_simple_score(self, query_tokens: List[str], chunk_tokens: List[str]) -> float:
        """Simple TF-based scoring"""
        score = 0.0
        chunk_token_counts = {}
        
        # Count tokens in chunk
        for token in chunk_tokens:
            chunk_token_counts[token] = chunk_token_counts.get(token, 0) + 1
        
        # Calculate score
        for query_token in query_tokens:
            if query_token in chunk_token_counts:
                tf = chunk_token_counts[query_token]
                score += tf / len(chunk_tokens)  # Normalized term frequency
        
        return score


class FixedEnhancedSearchEngine:
    """
    Fixed Enhanced Search Engine với fallbacks
    """
    
    def __init__(self, data_path: str, config: Dict = None):
        """Initialize with fallback components"""
        self.config = config or self._default_config()
        self.data_path = data_path
        
        print("=" * 70)
        print("🚀 FIXED ENHANCED SEARCH ENGINE INITIALIZATION")
        print("=" * 70)
        
        # Initialize simple components
        print("\n[1/4] 📄 Initializing Simple Tokenizer...")
        self.tokenizer = SimpleVietnameseTokenizer(use_stopwords=self.config['use_stopwords'])
        
        print("\n[2/4] 🧩 Initializing Simple Chunker...")
        self.chunker = SimpleDocumentChunker(
            chunk_size=self.config['chunk_size'],
            overlap_size=self.config['overlap_size']
        )
        
        print("\n[3/4] 🔍 Initializing Simple Retrieval...")
        self.retrieval = SimpleBM25Retrieval()
        
        # Storage
        self.documents = []
        self.chunks = []
        self.chunk_to_doc_map = {}
        self.tokenized_chunks = []
        
        print("\n✅ Fixed Enhanced SearchEngine initialized successfully!")
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'chunk_size': 256,
            'overlap_size': 32,
            'use_stopwords': True,
            'top_k_results': 10,
            'top_k_chunks_per_search': 50,
            'enable_caching': False  # Disabled for simplicity
        }
    
    def build_index(self):
        """Build search index"""
        print("\n" + "=" * 70)
        print("🔧 BUILDING FIXED SEARCH INDEX")
        print("=" * 70)
        
        start_time = time.time()
        
        # Load documents
        print("\n[1/4] 📋 Loading documents...")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        print(f"✓ Loaded {len(self.documents)} documents")
        
        # Create chunks
        print(f"\n[2/4] 🧩 Creating chunks...")
        all_chunks = []
        chunk_to_doc_map = {}
        
        for doc_id, doc in enumerate(self.documents):
            filename = doc.get('filename', f'doc_{doc_id}')
            content = doc.get('content', '')
            
            doc_chunks = self.chunker.chunk_document(content, filename)
            
            for chunk in doc_chunks:
                chunk_to_doc_map[chunk['chunk_id']] = doc_id
                all_chunks.append(chunk)
        
        self.chunks = all_chunks
        self.chunk_to_doc_map = chunk_to_doc_map
        print(f"✓ Created {len(self.chunks)} chunks")
        
        # Tokenize chunks
        print(f"\n[3/4] 🔤 Tokenizing chunks...")
        chunk_contents = [chunk['content'] for chunk in self.chunks]
        self.tokenized_chunks = self.tokenizer.tokenize_documents(chunk_contents)
        print(f"✓ Tokenized {len(self.tokenized_chunks)} chunks")
        
        # Index chunks
        print(f"\n[4/4] 🔍 Indexing chunks...")
        self.retrieval.index_chunks(
            chunks=self.chunks,
            tokenized_chunks=self.tokenized_chunks,
            chunk_to_doc_map=self.chunk_to_doc_map
        )
        
        build_time = time.time() - start_time
        
        # Report performance
        avg_chunks_per_doc = len(self.chunks) / len(self.documents)
        print(f"\n📊 Performance Analysis:")
        print(f"   📋 Total chunks: {len(self.chunks)}")
        print(f"   📄 Total documents: {len(self.documents)}")
        print(f"   🔢 Avg chunks per doc: {avg_chunks_per_doc:.1f}")
        
        print(f"\n✅ Index building completed in {build_time:.2f}s")
        print("=" * 70)
    
    def search(self, query: str, top_k: int = None, search_mode: str = 'document') -> List[Dict]:
        """Enhanced search"""
        if top_k is None:
            top_k = self.config['top_k_results']
        
        query_tokens = self.tokenizer.tokenize(query)
        
        if search_mode == 'chunk':
            return self._search_chunks(query, query_tokens, top_k)
        else:  # document mode
            return self._search_documents(query, query_tokens, top_k)
    
    def _search_documents(self, query: str, query_tokens: List[str], top_k: int) -> List[Dict]:
        """Document-level search"""
        doc_results = self.retrieval.retrieve_documents(
            query=query,
            query_tokens=query_tokens,
            top_k_documents=top_k,
            top_k_chunks_per_search=self.config['top_k_chunks_per_search']
        )
        
        formatted_results = []
        for doc_id, score, best_chunks in doc_results:
            doc = self.documents[doc_id]
            
            # Create preview
            preview_parts = []
            for chunk in best_chunks[:2]:
                content = chunk['content'][:150] + "..." if len(chunk['content']) > 150 else chunk['content']
                preview_parts.append(content)
            
            result = {
                'doc_id': doc_id,
                'score': score,
                'file_name': doc.get('filename', f'Document {doc_id}'),
                'preview': " | ".join(preview_parts),
                'best_chunks_count': len(best_chunks),
                'search_mode': 'document'
            }
            
            formatted_results.append(result)
        
        return formatted_results
    
    def _search_chunks(self, query: str, query_tokens: List[str], top_k: int) -> List[Dict]:
        """Chunk-level search"""
        chunk_results = self.retrieval.retrieve_chunks(
            query=query,
            query_tokens=query_tokens,
            top_k_chunks=top_k
        )
        
        formatted_results = []
        for chunk, score in chunk_results:
            doc_id = self.chunk_to_doc_map.get(chunk['chunk_id'])
            doc = self.documents[doc_id] if doc_id is not None else {}
            
            result = {
                'chunk_id': chunk['chunk_id'],
                'doc_id': doc_id,
                'score': score,
                'file_name': doc.get('filename', 'Unknown'),
                'content': chunk['content'],
                'chunk_type': chunk['chunk_type'],
                'search_mode': 'chunk'
            }
            
            formatted_results.append(result)
        
        return formatted_results
    
    def print_results(self, query: str, results: List[Dict]):
        """Print search results"""
        print("\n" + "=" * 70)
        print(f"🔍 SEARCH RESULTS FOR: '{query}'")
        print("=" * 70)
        
        if not results:
            print("\nNo results found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Score: {result['score']:.4f} | Mode: {result.get('search_mode', 'N/A')}")
            print(f"📄 File: {result.get('file_name', 'Unknown')}")
            
            if 'preview' in result:
                print(f"💡 Preview: {result['preview']}")
            elif 'content' in result:
                content = result['content']
                if len(content) > 300:
                    content = content[:300] + "..."
                print(f"📝 Content: {content}")
            
            print("-" * 70)
    
    def interactive_search(self):
        """Interactive search interface"""
        print("\n" + "=" * 70)
        print("💬 INTERACTIVE SEARCH MODE")
        print("=" * 70)
        print("Commands:")
        print("  - Type your query to search")
        print("  - ':mode [document|chunk]' to change search mode")
        print("  - ':quit' to exit")
        print()
        
        search_mode = 'document'
        
        while True:
            try:
                user_input = input(f"[{search_mode}] Search: ").strip()
                
                if user_input.lower() in [':quit', ':exit', 'quit']:
                    print("Thank you for using Fixed Enhanced Search Engine! 👋")
                    break
                
                # Handle commands
                if user_input.startswith(':mode'):
                    parts = user_input.split()
                    if len(parts) > 1 and parts[1] in ['document', 'chunk']:
                        search_mode = parts[1]
                        print(f"✓ Search mode changed to: {search_mode}")
                    else:
                        print("❌ Valid modes: document, chunk")
                    continue
                
                if not user_input:
                    continue
                
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Perform search
                results = self.search(
                    query=user_input,
                    search_mode=search_mode
                )
                
                self.print_results(user_input, results)
                
            except KeyboardInterrupt:
                print("\n\nBye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function"""
    DATA_PATH = "data_content.json"
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found: {DATA_PATH}")
        return
    
    # Initialize fixed engine
    engine = FixedEnhancedSearchEngine(DATA_PATH)
    engine.build_index()
    
    # Start interactive search
    engine.interactive_search()


if __name__ == "__main__":
    main()