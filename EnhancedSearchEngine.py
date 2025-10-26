"""
EnhancedSearchEngine.py
Advanced Search Engine với chunk-based retrieval

Main orchestrator cho enhanced search system
"""

from typing import List, Dict, Tuple, Optional
from EnhancedDataHandler import EnhancedDataHandler, analyze_chunking_performance
from Tokenizer import VietnameseTokenizer
from EnhancedDataRetrieval import EnhancedDataRetrieval
from DocumentChunker import DocumentChunk
import time


class EnhancedSearchEngine:
    """
    Enhanced Search Engine với chunk-based architecture
    
    Features:
    - Document chunking với multiple strategies
    - Chunk-level indexing và retrieval
    - Multi-stage ranking
    - Context-aware results
    - Performance analytics
    - Flexible configuration
    """
    
    def __init__(self, 
                 data_path: str,
                 config: Dict = None):
        """
        Initialize Enhanced Search Engine
        
        Args:
            data_path: Path to JSON dataset
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.data_path = data_path
        
        # Initialize components
        print("=" * 70)
        print("🚀 ENHANCED SEARCH ENGINE INITIALIZATION")
        print("=" * 70)
        
        # 1. Enhanced Data Handler với chunking
        print("\n[1/4] 📄 Initializing Enhanced DataHandler...")
        self.data_handler = EnhancedDataHandler(
            data_path=data_path,
            chunking_strategy=self.config['chunking_strategy'],
            chunk_size=self.config['chunk_size'],
            overlap_size=self.config['overlap_size'],
            enable_caching=self.config['enable_caching']
        )
        
        # 2. Tokenizer
        print("\n[2/4] 🔤 Initializing Vietnamese Tokenizer...")
        self.tokenizer = VietnameseTokenizer(
            use_stopwords=self.config['use_stopwords'],
            library=self.config['tokenizer_library']
        )
        
        # 3. Enhanced Data Retrieval
        print("\n[3/4] 🔍 Initializing Enhanced DataRetrieval...")
        self.retrieval = EnhancedDataRetrieval(
            embedding_model=self.config['embedding_model'],
            use_bm25=self.config['use_bm25'],
            use_embedding=self.config['use_embedding'],
            bm25_weight=self.config['bm25_weight'],
            embedding_weight=self.config['embedding_weight'],
            chunk_boost_factor=self.config['chunk_boost_factor'],
            document_aggregation=self.config['document_aggregation']
        )
        
        # 4. Storage
        self.documents = []
        self.chunks = []
        self.chunk_to_doc_map = {}
        self.tokenized_chunks = []
        
        print("\n✅ Enhanced SearchEngine initialized successfully!")
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            # Chunking settings
            'chunking_strategy': 'hybrid',      # 'semantic', 'hierarchical', 'hybrid', 'fixed'
            'chunk_size': 256,                  # Smaller chunks for better precision
            'overlap_size': 32,                 # Overlap for context preservation
            'enable_caching': True,
            
            # Tokenizer settings
            'use_stopwords': True,
            'tokenizer_library': 'underthesea',
            
            # Retrieval settings
            'embedding_model': 'keepitreal/vietnamese-sbert',
            'use_bm25': True,
            'use_embedding': True,
            'bm25_weight': 0.4,
            'embedding_weight': 0.6,
            'chunk_boost_factor': 1.2,
            'document_aggregation': 'max',      # 'max', 'mean', 'weighted_sum'
            
            # Search settings
            'top_k_results': 10,
            'top_k_chunks_per_search': 50,
            'include_context': True,
            'context_window': 1,
            'min_score_threshold': 0.1
        }
    
    def build_index(self):
        """Build search index from documents"""
        print("\n" + "=" * 70)
        print("🔧 BUILDING ENHANCED SEARCH INDEX")
        print("=" * 70)
        
        start_time = time.time()
        
        # Step 1: Load documents và create chunks
        print("\n[1/4] 📋 Loading documents and creating chunks...")
        self.documents, self.chunks = self.data_handler.load_data()
        self.chunk_to_doc_map = self.data_handler.chunk_to_doc_map
        
        # Step 2: Tokenize chunks
        print(f"\n[2/4] 🔤 Tokenizing {len(self.chunks)} chunks...")
        chunk_contents = [chunk.content for chunk in self.chunks]
        self.tokenized_chunks = self.tokenizer.tokenize_documents(chunk_contents)
        print(f"✓ Tokenized {len(self.tokenized_chunks)} chunks")
        
        # Step 3: Index chunks
        print(f"\n[3/4] 🔍 Indexing chunks for retrieval...")
        self.retrieval.index_chunks(
            chunks=self.chunks,
            tokenized_chunks=self.tokenized_chunks,
            chunk_to_doc_map=self.chunk_to_doc_map
        )
        
        # Step 4: Performance analysis
        print(f"\n[4/4] 📊 Analyzing performance...")
        self._analyze_and_report_performance()
        
        build_time = time.time() - start_time
        print(f"\n✅ Index building completed in {build_time:.2f}s")
        print("=" * 70)
    
    def search(self, 
              query: str, 
              top_k: int = None,
              search_mode: str = 'document',  # 'document', 'chunk', 'context'
              explain: bool = False) -> List[Dict]:
        """
        Enhanced search with multiple modes
        
        Args:
            query: Search query
            top_k: Number of results
            search_mode: 'document', 'chunk', or 'context'
            explain: Include ranking explanations
            
        Returns:
            List[Dict]: Search results
        """
        if top_k is None:
            top_k = self.config['top_k_results']
        
        # Tokenize query
        query_tokens = self.tokenizer.tokenize(query)
        
        if search_mode == 'chunk':
            return self._search_chunks(query, query_tokens, top_k, explain)
        elif search_mode == 'context':
            return self._search_with_context(query, query_tokens, top_k, explain)
        else:  # document mode
            return self._search_documents(query, query_tokens, top_k, explain)
    
    def _search_documents(self, 
                         query: str, 
                         query_tokens: List[str], 
                         top_k: int,
                         explain: bool = False) -> List[Dict]:
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
            
            # Create preview from best chunks
            preview_parts = []
            for chunk in best_chunks[:2]:  # Top 2 chunks for preview
                content = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                if 'section_title' in chunk.metadata:
                    preview_parts.append(f"[{chunk.metadata['section_title']}] {content}")
                else:
                    preview_parts.append(content)
            
            result = {
                'doc_id': doc_id,
                'score': score,
                'file_name': doc['file_name'],
                'preview': " | ".join(preview_parts),
                'best_chunks_count': len(best_chunks),
                'search_mode': 'document'
            }
            
            if explain:
                # Add explanation for top chunk
                if best_chunks:
                    top_chunk = best_chunks[0]
                    result['explanation'] = self.retrieval.explain_ranking(
                        query, query_tokens, top_chunk
                    )
            
            formatted_results.append(result)
        
        return formatted_results
    
    def _search_chunks(self, 
                      query: str, 
                      query_tokens: List[str], 
                      top_k: int,
                      explain: bool = False) -> List[Dict]:
        """Chunk-level search"""
        chunk_results = self.retrieval.retrieve_chunks(
            query=query,
            query_tokens=query_tokens,
            top_k_chunks=top_k
        )
        
        formatted_results = []
        for chunk, score in chunk_results:
            doc_id = self.chunk_to_doc_map.get(chunk.chunk_id)
            doc = self.documents[doc_id] if doc_id is not None else {}
            
            result = {
                'chunk_id': chunk.chunk_id,
                'doc_id': doc_id,
                'score': score,
                'file_name': doc.get('file_name', 'Unknown'),
                'content': chunk.content,
                'chunk_type': chunk.chunk_type,
                'level': chunk.level,
                'metadata': chunk.metadata,
                'search_mode': 'chunk'
            }
            
            if explain:
                result['explanation'] = self.retrieval.explain_ranking(
                    query, query_tokens, chunk
                )
            
            formatted_results.append(result)
        
        return formatted_results
    
    def _search_with_context(self, 
                            query: str, 
                            query_tokens: List[str], 
                            top_k: int,
                            explain: bool = False) -> List[Dict]:
        """Context-aware search"""
        context_results = self.retrieval.retrieve_with_context(
            query=query,
            query_tokens=query_tokens,
            top_k=top_k,
            context_window=self.config['context_window']
        )
        
        formatted_results = []
        for result in context_results:
            doc_id = result['doc_id']
            doc = self.documents[doc_id]
            
            # Combine context chunks for richer content
            all_content_parts = []
            for chunk in result['context_chunks']:
                if 'section_title' in chunk.metadata:
                    all_content_parts.append(f"\n## {chunk.metadata['section_title']}\n{chunk.content}")
                else:
                    all_content_parts.append(chunk.content)
            
            combined_content = "\n".join(all_content_parts)
            
            formatted_result = {
                'doc_id': doc_id,
                'score': result['score'],
                'file_name': doc['file_name'],
                'content': combined_content,
                'best_chunks': len(result['best_chunks']),
                'total_chunks': result['total_chunks'],
                'search_mode': 'context'
            }
            
            if explain and result['best_chunks']:
                formatted_result['explanation'] = self.retrieval.explain_ranking(
                    query, query_tokens, result['best_chunks'][0]
                )
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def print_results(self, 
                     query: str, 
                     results: List[Dict],
                     detailed: bool = False):
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
            
            if detailed and 'explanation' in result:
                exp = result['explanation']
                print(f"🔬 Explanation:")
                print(f"   - BM25: {exp['scores'].get('bm25_weighted', 0):.3f}")
                print(f"   - Embedding: {exp['scores'].get('embedding_weighted', 0):.3f}")
                print(f"   - Boost factor: {exp['boosts'].get('total_boost_factor', 1):.3f}")
            
            print("-" * 70)
    
    def get_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        doc_stats = self.data_handler.get_chunk_statistics()
        retrieval_stats = self.retrieval.get_chunk_statistics()
        
        combined_stats = {
            'documents': {
                'total_count': len(self.documents),
                'avg_chunks_per_doc': doc_stats.get('chunks_per_doc', 0)
            },
            'chunks': doc_stats,
            'retrieval': retrieval_stats,
            'config': self.config
        }
        
        return combined_stats
    
    def _analyze_and_report_performance(self):
        """Analyze and report chunking performance"""
        performance = analyze_chunking_performance(self.data_handler)
        
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print(f"   📋 Total chunks: {performance['total_chunks']}")
        print(f"   📄 Total documents: {performance['total_documents']}")
        print(f"   🔢 Avg chunks per doc: {performance['chunks_per_doc']:.1f}")
        print(f"   💬 Avg chunk length: {performance['avg_chunk_length']:.0f} chars")
        
        size_stats = performance.get('chunk_size_stats', {})
        if size_stats:
            print(f"   📏 Chunk sizes (words): {size_stats['min']}-{size_stats['max']} (avg: {size_stats['avg']:.0f})")
        
        print(f"   🏷️ Chunk types: {list(performance['chunk_types'].keys())}")
    
    def interactive_search(self):
        """Interactive search interface"""
        print("\n" + "=" * 70)
        print("💬 INTERACTIVE SEARCH MODE")
        print("=" * 70)
        print("Commands:")
        print("  - Type your query to search")
        print("  - ':mode [document|chunk|context]' to change search mode")
        print("  - ':explain on/off' to toggle explanations")
        print("  - ':stats' to show statistics")
        print("  - ':quit' to exit")
        print()
        
        search_mode = 'document'
        explain = False
        
        while True:
            try:
                user_input = input(f"[{search_mode}] Search: ").strip()
                
                if user_input.lower() in [':quit', ':exit', 'quit']:
                    print("Thank you for using Enhanced Search Engine! 👋")
                    break
                
                # Handle commands
                if user_input.startswith(':'):
                    if user_input.startswith(':mode'):
                        parts = user_input.split()
                        if len(parts) > 1 and parts[1] in ['document', 'chunk', 'context']:
                            search_mode = parts[1]
                            print(f"✓ Search mode changed to: {search_mode}")
                        else:
                            print("❌ Valid modes: document, chunk, context")
                    
                    elif user_input.startswith(':explain'):
                        parts = user_input.split()
                        if len(parts) > 1:
                            explain = parts[1].lower() in ['on', 'true', '1']
                            print(f"✓ Explanations: {'enabled' if explain else 'disabled'}")
                        else:
                            explain = not explain
                            print(f"✓ Explanations: {'enabled' if explain else 'disabled'}")
                    
                    elif user_input == ':stats':
                        stats = self.get_statistics()
                        print(f"\n📊 System Statistics:")
                        print(f"   Documents: {stats['documents']['total_count']}")
                        print(f"   Chunks: {stats['chunks']['total_chunks']}")
                        print(f"   Strategy: {stats['config']['chunking_strategy']}")
                        print(f"   Chunk size: {stats['config']['chunk_size']}")
                    
                    continue
                
                if not user_input:
                    continue
                
                # Perform search
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                
                results = self.search(
                    query=user_input,
                    search_mode=search_mode,
                    explain=explain
                )
                
                self.print_results(user_input, results, detailed=explain)
                
            except KeyboardInterrupt:
                print("\n\nBye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function"""
    DATA_PATH = "data_content.json"
    
    # Custom configuration
    config = {
        'chunking_strategy': 'hybrid',
        'chunk_size': 256,
        'overlap_size': 32,
        'use_stopwords': True,
        'tokenizer_library': 'underthesea',
        'embedding_model': 'keepitreal/vietnamese-sbert',
        'use_bm25': True,
        'use_embedding': True,
        'bm25_weight': 0.4,
        'embedding_weight': 0.6,
        'chunk_boost_factor': 1.2,
        'document_aggregation': 'max',
        'top_k_results': 5,
        'enable_caching': True
    }
    
    # Initialize and build index
    engine = EnhancedSearchEngine(DATA_PATH, config)
    engine.build_index()
    
    # Start interactive search
    engine.interactive_search()


if __name__ == "__main__":
    main()