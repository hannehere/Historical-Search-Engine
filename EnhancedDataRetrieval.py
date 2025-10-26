"""
EnhancedDataRetrieval.py
Advanced Data Retrieval với chunk-based search

Chịu trách nhiệm:
- Chunk-level retrieval
- Multi-level ranking (chunk -> document)
- Context aggregation
- Advanced scoring algorithms
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import math

from DocumentChunker import DocumentChunk


class EnhancedDataRetrieval:
    """
    Enhanced Data Retrieval System
    
    Features:
    - Chunk-level indexing và retrieval
    - Multi-stage ranking
    - Context aggregation
    - Relevance score propagation
    - Advanced hybrid scoring
    """
    
    def __init__(self, 
                 embedding_model: str = 'keepitreal/vietnamese-sbert',
                 use_bm25: bool = True,
                 use_embedding: bool = True,
                 bm25_weight: float = 0.4,
                 embedding_weight: float = 0.6,
                 chunk_boost_factor: float = 1.2,
                 document_aggregation: str = 'max'):  # 'max', 'mean', 'weighted_sum'
        """
        Args:
            embedding_model: Tên model embedding
            use_bm25: Có sử dụng BM25 không
            use_embedding: Có sử dụng embedding không
            bm25_weight: Trọng số BM25
            embedding_weight: Trọng số embedding
            chunk_boost_factor: Factor boost cho chunk relevance
            document_aggregation: Cách aggregate chunk scores thành document scores
        """
        self.use_bm25 = use_bm25
        self.use_embedding = use_embedding
        self.bm25_weight = bm25_weight
        self.embedding_weight = embedding_weight
        self.chunk_boost_factor = chunk_boost_factor
        self.document_aggregation = document_aggregation
        
        # Ensure weights sum to 1
        total_weight = bm25_weight + embedding_weight
        if total_weight > 0:
            self.bm25_weight = bm25_weight / total_weight
            self.embedding_weight = embedding_weight / total_weight
        
        # Initialize components
        self.bm25 = None
        self.tokenized_chunks = []
        self.chunks = []
        self.chunk_to_doc_map = {}
        
        # Initialize embedding model
        if use_embedding:
            print(f"🤖 Loading embedding model: {embedding_model}...")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.chunk_embeddings = None
        else:
            self.embedding_model = None
    
    def index_chunks(self, 
                    chunks: List[DocumentChunk],
                    tokenized_chunks: List[List[str]],
                    chunk_to_doc_map: Dict[str, int]):
        """
        Index chunks for retrieval
        
        Args:
            chunks: List of DocumentChunk objects
            tokenized_chunks: Tokenized content of chunks
            chunk_to_doc_map: Mapping from chunk_id to doc_id
        """
        self.chunks = chunks
        self.tokenized_chunks = tokenized_chunks
        self.chunk_to_doc_map = chunk_to_doc_map
        
        print(f"🔍 Indexing {len(chunks)} chunks...")
        
        # Index BM25
        if self.use_bm25:
            print("  → Creating BM25 index...")
            self.bm25 = BM25Okapi(tokenized_chunks)
            print(f"  ✓ BM25 indexed {len(tokenized_chunks)} chunks")
        
        # Index Embeddings
        if self.use_embedding:
            print("  → Creating chunk embeddings...")
            chunk_contents = [chunk.content for chunk in chunks]
            self.chunk_embeddings = self.embedding_model.encode(
                chunk_contents,
                show_progress_bar=True,
                convert_to_numpy=True,
                batch_size=32
            )
            print(f"  ✓ Created embeddings for {len(chunk_contents)} chunks")
        
        print("✅ Chunk indexing complete!")
    
    def retrieve_chunks(self, 
                       query: str,
                       query_tokens: List[str],
                       top_k_chunks: int = 20) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve most relevant chunks
        
        Args:
            query: Query text
            query_tokens: Tokenized query
            top_k_chunks: Number of chunks to retrieve
            
        Returns:
            List[Tuple[DocumentChunk, float]]: (chunk, score) pairs
        """
        chunk_scores = {}
        
        # BM25 scoring
        if self.use_bm25 and self.bm25:
            bm25_scores = self.bm25.get_scores(query_tokens)
            max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
            
            if max_bm25 > 0:
                for i, score in enumerate(bm25_scores):
                    normalized_score = score / max_bm25
                    chunk_scores[i] = chunk_scores.get(i, 0) + self.bm25_weight * normalized_score
        
        # Embedding scoring
        if self.use_embedding and self.chunk_embeddings is not None:
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            similarities = cosine_similarity(query_embedding, self.chunk_embeddings)[0]
            
            for i, score in enumerate(similarities):
                chunk_scores[i] = chunk_scores.get(i, 0) + self.embedding_weight * score
        
        # Apply chunk-specific boosts
        for chunk_idx, base_score in chunk_scores.items():
            chunk = self.chunks[chunk_idx]
            boosted_score = self._apply_chunk_boost(chunk, base_score, query)
            chunk_scores[chunk_idx] = boosted_score
        
        # Sort và get top chunks
        top_chunk_indices = sorted(
            chunk_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k_chunks]
        
        # Return chunks with scores
        results = []
        for chunk_idx, score in top_chunk_indices:
            chunk = self.chunks[chunk_idx]
            results.append((chunk, score))
        
        return results
    
    def retrieve_documents(self,
                          query: str,
                          query_tokens: List[str],
                          top_k_documents: int = 10,
                          top_k_chunks_per_search: int = 50) -> List[Tuple[int, float, List[DocumentChunk]]]:
        """
        Retrieve documents with their best chunks
        
        Args:
            query: Query text
            query_tokens: Tokenized query
            top_k_documents: Number of documents to return
            top_k_chunks_per_search: Number of chunks to consider
            
        Returns:
            List[Tuple[int, float, List[DocumentChunk]]]: (doc_id, score, best_chunks)
        """
        # Get relevant chunks
        chunk_results = self.retrieve_chunks(
            query, 
            query_tokens, 
            top_k_chunks_per_search
        )
        
        # Group chunks by document
        doc_chunks = defaultdict(list)
        for chunk, score in chunk_results:
            doc_id = self.chunk_to_doc_map.get(chunk.chunk_id)
            if doc_id is not None:
                doc_chunks[doc_id].append((chunk, score))
        
        # Calculate document scores
        doc_scores = {}
        for doc_id, chunk_score_pairs in doc_chunks.items():
            scores = [score for _, score in chunk_score_pairs]
            
            if self.document_aggregation == 'max':
                doc_score = max(scores)
            elif self.document_aggregation == 'mean':
                doc_score = sum(scores) / len(scores)
            elif self.document_aggregation == 'weighted_sum':
                # Weight by position (higher weight for higher-scoring chunks)
                weights = [math.exp(-i * 0.1) for i in range(len(scores))]
                weighted_scores = [s * w for s, w in zip(scores, weights)]
                doc_score = sum(weighted_scores) / sum(weights)
            else:
                doc_score = max(scores)  # fallback
            
            doc_scores[doc_id] = doc_score
        
        # Sort documents by score
        top_documents = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k_documents]
        
        # Prepare results with best chunks per document
        results = []
        for doc_id, doc_score in top_documents:
            # Get top 3 chunks for this document
            doc_chunk_pairs = doc_chunks[doc_id]
            doc_chunk_pairs.sort(key=lambda x: x[1], reverse=True)
            best_chunks = [chunk for chunk, _ in doc_chunk_pairs[:3]]
            
            results.append((doc_id, doc_score, best_chunks))
        
        return results
    
    def retrieve_with_context(self,
                             query: str,
                             query_tokens: List[str],
                             top_k: int = 10,
                             context_window: int = 1) -> List[Dict]:
        """
        Retrieve với context chunks (chunks before/after)
        
        Args:
            query: Query text
            query_tokens: Tokenized query
            top_k: Number of results
            context_window: Number of surrounding chunks to include
            
        Returns:
            List[Dict]: Results with context
        """
        # Get document results
        doc_results = self.retrieve_documents(query, query_tokens, top_k)
        
        results = []
        for doc_id, doc_score, best_chunks in doc_results:
            # Get all chunks for this document
            all_doc_chunks = [
                chunk for chunk in self.chunks 
                if self.chunk_to_doc_map.get(chunk.chunk_id) == doc_id
            ]
            
            # Sort by chunk_index
            all_doc_chunks.sort(key=lambda x: x.chunk_index)
            
            # Find context for each best chunk
            context_chunks = set()
            for best_chunk in best_chunks:
                chunk_pos = None
                for i, chunk in enumerate(all_doc_chunks):
                    if chunk.chunk_id == best_chunk.chunk_id:
                        chunk_pos = i
                        break
                
                if chunk_pos is not None:
                    # Add context window
                    start_idx = max(0, chunk_pos - context_window)
                    end_idx = min(len(all_doc_chunks), chunk_pos + context_window + 1)
                    
                    for i in range(start_idx, end_idx):
                        context_chunks.add(all_doc_chunks[i])
            
            # Create result
            result = {
                'doc_id': doc_id,
                'score': doc_score,
                'best_chunks': best_chunks,
                'context_chunks': list(context_chunks),
                'total_chunks': len(context_chunks)
            }
            
            results.append(result)
        
        return results
    
    def _apply_chunk_boost(self, 
                          chunk: DocumentChunk, 
                          base_score: float, 
                          query: str) -> float:
        """
        Apply chunk-specific boosting factors
        
        Args:
            chunk: DocumentChunk object
            base_score: Base relevance score
            query: Query text
            
        Returns:
            float: Boosted score
        """
        boost_factor = 1.0
        
        # Boost based on chunk type
        type_boosts = {
            'overview': 1.3,      # Document overviews are important
            'section': 1.2,       # Main sections
            'paragraph': 1.0,     # Regular content
            'sub_section': 0.9,   # Sub-sections
            'fixed_chunk': 0.8    # Fixed chunks might lose context
        }
        
        boost_factor *= type_boosts.get(chunk.chunk_type, 1.0)
        
        # Boost based on hierarchy level
        if chunk.level == 0:  # Top level
            boost_factor *= 1.2
        elif chunk.level == 1:  # Second level
            boost_factor *= 1.1
        
        # Boost if query matches section title
        if 'section_title' in chunk.metadata:
            section_title = chunk.metadata['section_title'].lower()
            query_lower = query.lower()
            
            # Exact match
            if query_lower in section_title:
                boost_factor *= 1.4
            
            # Partial word match
            query_words = set(query_lower.split())
            title_words = set(section_title.split())
            
            overlap = len(query_words & title_words)
            if overlap > 0:
                boost_factor *= (1.0 + 0.1 * overlap)
        
        # Length penalty for very short chunks
        content_length = len(chunk.content.split())
        if content_length < 20:
            boost_factor *= 0.8
        elif content_length > 200:
            boost_factor *= 0.95  # Slight penalty for very long chunks
        
        # Apply global chunk boost factor
        boost_factor *= self.chunk_boost_factor
        
        return base_score * boost_factor
    
    def get_chunk_statistics(self) -> Dict:
        """Get statistics about indexed chunks"""
        if not self.chunks:
            return {}
        
        stats = {
            'total_chunks': len(self.chunks),
            'avg_chunk_length': np.mean([len(chunk.content) for chunk in self.chunks]),
            'chunk_types': {},
            'chunk_levels': {},
            'documents_covered': len(set(self.chunk_to_doc_map.values()))
        }
        
        # Count by type and level
        for chunk in self.chunks:
            chunk_type = chunk.chunk_type
            stats['chunk_types'][chunk_type] = stats['chunk_types'].get(chunk_type, 0) + 1
            
            level = chunk.level
            stats['chunk_levels'][level] = stats['chunk_levels'].get(level, 0) + 1
        
        return stats
    
    def explain_ranking(self, 
                       query: str,
                       query_tokens: List[str],
                       chunk: DocumentChunk) -> Dict:
        """
        Explain tại sao chunk này được rank cao/thấp
        
        Args:
            query: Query text
            query_tokens: Tokenized query
            chunk: DocumentChunk to explain
            
        Returns:
            Dict: Explanation details
        """
        explanation = {
            'chunk_id': chunk.chunk_id,
            'chunk_type': chunk.chunk_type,
            'level': chunk.level,
            'scores': {},
            'boosts': {},
            'final_score': 0
        }
        
        # Find chunk index
        chunk_idx = None
        for i, c in enumerate(self.chunks):
            if c.chunk_id == chunk.chunk_id:
                chunk_idx = i
                break
        
        if chunk_idx is None:
            return explanation
        
        base_score = 0
        
        # BM25 score
        if self.use_bm25 and self.bm25:
            bm25_scores = self.bm25.get_scores(query_tokens)
            bm25_score = bm25_scores[chunk_idx] if chunk_idx < len(bm25_scores) else 0
            max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
            
            normalized_bm25 = bm25_score / max_bm25 if max_bm25 > 0 else 0
            weighted_bm25 = self.bm25_weight * normalized_bm25
            
            explanation['scores']['bm25_raw'] = bm25_score
            explanation['scores']['bm25_normalized'] = normalized_bm25
            explanation['scores']['bm25_weighted'] = weighted_bm25
            
            base_score += weighted_bm25
        
        # Embedding score
        if self.use_embedding and self.chunk_embeddings is not None:
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            similarity = cosine_similarity(query_embedding, self.chunk_embeddings[chunk_idx:chunk_idx+1])[0][0]
            weighted_embedding = self.embedding_weight * similarity
            
            explanation['scores']['embedding_similarity'] = similarity
            explanation['scores']['embedding_weighted'] = weighted_embedding
            
            base_score += weighted_embedding
        
        explanation['scores']['base_score'] = base_score
        
        # Apply boosts
        final_score = self._apply_chunk_boost(chunk, base_score, query)
        boost_factor = final_score / base_score if base_score > 0 else 1.0
        
        explanation['boosts']['total_boost_factor'] = boost_factor
        explanation['final_score'] = final_score
        
        return explanation