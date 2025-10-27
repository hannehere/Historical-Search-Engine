"""
ThreeStageRetrieval.py
Implementation of Three-Stage Retrieval Architecture

Based on paper approach:
Stage 1: BM25 keyword retrieval (fast filtering)
Stage 2: Embedding-based semantic retrieval (context understanding)  
Stage 3: Cross-encoder reranking (final precision)

This improves upon current hybrid approach by separating stages
and adding dedicated reranking step.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import math
import torch

from DocumentChunker import DocumentChunk


class ThreeStageRetrieval:
    """
    Three-Stage Retrieval System
    
    Stage 1: BM25 Retrieval (Keyword matching - Fast filtering)
    Stage 2: Dense Retrieval (Embedding similarity - Semantic understanding)
    Stage 3: Reranking (Cross-encoder - Final precision)
    """
    
    def __init__(self,
                 # Stage 1: BM25 settings
                 use_bm25: bool = True,
                 stage1_top_k: int = 100,  # Larger initial retrieval pool
                 
                 # Stage 2: Dense retrieval settings
                 embedding_model: str = 'keepitreal/vietnamese-sbert',
                 use_dense_retrieval: bool = True,
                 stage2_top_k: int = 50,   # Reduced after BM25 filtering
                 
                 # Stage 3: Reranking settings
                 reranker_model: str = 'keepitreal/vietnamese-reranker',
                 use_reranking: bool = True,
                 stage3_top_k: int = 20,   # Final results
                 
                 # Fusion settings
                 bm25_weight: float = 0.3,
                 dense_weight: float = 0.4,
                 rerank_weight: float = 0.3):
        """
        Initialize Three-Stage Retrieval System
        
        Args:
            stage1_top_k: Number of candidates from BM25
            stage2_top_k: Number of candidates after dense retrieval
            stage3_top_k: Final number of results after reranking
        """
        
        # Stage configuration
        self.use_bm25 = use_bm25
        self.use_dense_retrieval = use_dense_retrieval
        self.use_reranking = use_reranking
        
        self.stage1_top_k = stage1_top_k
        self.stage2_top_k = stage2_top_k  
        self.stage3_top_k = stage3_top_k
        
        # Weight configuration
        total_weight = bm25_weight + dense_weight + rerank_weight
        self.bm25_weight = bm25_weight / total_weight
        self.dense_weight = dense_weight / total_weight
        self.rerank_weight = rerank_weight / total_weight
        
        # Initialize models
        print("🚀 Initializing Three-Stage Retrieval System...")
        
        # Stage 1: BM25
        self.bm25 = None
        self.tokenized_chunks = []
        
        # Stage 2: Dense retrieval  
        if use_dense_retrieval:
            print(f"  📊 Loading dense retrieval model: {embedding_model}")
            self.dense_model = SentenceTransformer(embedding_model)
            self.chunk_embeddings = None
        else:
            self.dense_model = None
            
        # Stage 3: LLM-based reranking (paper approach)
        if use_reranking:
            print(f"  🎯 Loading reranker model: {reranker_model}")
            try:
                # Try CrossEncoder first (traditional approach)
                self.reranker = CrossEncoder(reranker_model)
                self._reranker_type = 'cross_encoder'
            except:
                try:
                    # Try LLM-based reranker (paper approach)
                    from transformers import AutoTokenizer, AutoModelForCausalLM
                    self.reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model)
                    self.reranker_model = AutoModelForCausalLM.from_pretrained(reranker_model)
                    self._reranker_type = 'llm_generator'
                    print(f"  ✓ Using LLM-based reranker (generative approach)")
                except:
                    # Fallback to sentence transformer
                    print(f"  ⚠️  LLM reranker failed, using SentenceTransformer for reranking")
                    self.reranker = SentenceTransformer(reranker_model)
                    self._reranker_type = 'sentence_transformer'
        else:
            self.reranker = None
            self._reranker_type = None
            
        # Data storage
        self.chunks = []
        self.chunk_to_doc_map = {}
        
        print("✅ Three-Stage Retrieval System initialized!")
    
    def index_chunks(self,
                    chunks: List[DocumentChunk],
                    tokenized_chunks: List[List[str]],
                    chunk_to_doc_map: Dict[str, int]):
        """Index chunks for three-stage retrieval"""
        
        self.chunks = chunks
        self.tokenized_chunks = tokenized_chunks
        self.chunk_to_doc_map = chunk_to_doc_map
        
        print(f"🔍 Indexing {len(chunks)} chunks for three-stage retrieval...")
        
        # Stage 1: Index BM25
        if self.use_bm25:
            print("  [Stage 1] Creating BM25 index...")
            self.bm25 = BM25Okapi(tokenized_chunks)
            print(f"  ✓ BM25 indexed {len(tokenized_chunks)} chunks")
        
        # Stage 2: Index dense embeddings
        if self.use_dense_retrieval:
            print("  [Stage 2] Creating dense embeddings...")
            chunk_contents = [chunk.content for chunk in chunks]
            self.chunk_embeddings = self.dense_model.encode(
                chunk_contents,
                show_progress_bar=True,
                convert_to_numpy=True,
                batch_size=32
            )
            print(f"  ✓ Created dense embeddings for {len(chunk_contents)} chunks")
        
        # Stage 3: No pre-indexing needed for reranker
        if self.use_reranking:
            print("  [Stage 3] Reranker ready for inference")
            
        print("✅ Three-stage indexing complete!")
    
    def retrieve_three_stage(self,
                           query: str,
                           query_tokens: List[str],
                           final_top_k: int = 10,
                           return_stage_details: bool = False) -> Union[List[Tuple], Dict]:
        """
        Execute three-stage retrieval pipeline
        
        Args:
            query: Query text
            query_tokens: Tokenized query  
            final_top_k: Final number of results
            return_stage_details: Return intermediate stage results
            
        Returns:
            List[Tuple] or Dict with stage details
        """
        
        stage_results = {}
        candidate_pool = list(range(len(self.chunks)))  # Start with all chunks
        
        # ==================== STAGE 1: BM25 Retrieval ====================
        if self.use_bm25 and self.bm25:
            print(f"[Stage 1] BM25 retrieval from {len(candidate_pool)} chunks...")
            
            bm25_scores = self.bm25.get_scores(query_tokens)
            
            # Get top-k from BM25
            bm25_results = [
                (idx, score) for idx, score in enumerate(bm25_scores)
                if idx in candidate_pool
            ]
            bm25_results.sort(key=lambda x: x[1], reverse=True)
            bm25_top = bm25_results[:self.stage1_top_k]
            
            # Update candidate pool
            candidate_pool = [idx for idx, _ in bm25_top]
            
            stage_results['stage1_bm25'] = {
                'candidates': len(candidate_pool),
                'top_scores': [score for _, score in bm25_top[:5]],
                'method': 'BM25 keyword matching'
            }
            
            print(f"  ✓ Stage 1 filtered to {len(candidate_pool)} candidates")
        
        # ==================== STAGE 2: Dense Retrieval ====================
        if self.use_dense_retrieval and self.chunk_embeddings is not None:
            print(f"[Stage 2] Dense retrieval from {len(candidate_pool)} chunks...")
            
            # Get query embedding
            query_embedding = self.dense_model.encode([query], convert_to_numpy=True)
            
            # Calculate similarities only for candidate pool
            candidate_embeddings = self.chunk_embeddings[candidate_pool]
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Get top-k from dense retrieval
            dense_results = [
                (candidate_pool[i], sim_score) 
                for i, sim_score in enumerate(similarities)
            ]
            dense_results.sort(key=lambda x: x[1], reverse=True)
            dense_top = dense_results[:self.stage2_top_k]
            
            # Update candidate pool
            candidate_pool = [idx for idx, _ in dense_top]
            
            stage_results['stage2_dense'] = {
                'candidates': len(candidate_pool),
                'top_scores': [score for _, score in dense_top[:5]],
                'method': 'Dense embedding similarity'
            }
            
            print(f"  ✓ Stage 2 filtered to {len(candidate_pool)} candidates")
        
        # ==================== STAGE 3: Reranking ====================
        final_results = []
        
        if self.use_reranking and self.reranker and len(candidate_pool) > 0:
            print(f"[Stage 3] Reranking {len(candidate_pool)} chunks...")
            
            # Prepare query-chunk pairs for reranking
            rerank_pairs = []
            for chunk_idx in candidate_pool:
                chunk_content = self.chunks[chunk_idx].content
                rerank_pairs.append([query, chunk_content])
            
            # Get reranking scores based on reranker type
            if self._reranker_type == 'llm_generator':
                # LLM-based generative reranking (paper approach)
                rerank_scores = self._llm_generative_rerank(query, rerank_pairs)
            elif self._reranker_type == 'cross_encoder':
                # Traditional CrossEncoder
                rerank_scores = self.reranker.predict(rerank_pairs)
            else:
                # Fallback: sentence similarity
                rerank_scores = self._sentence_transformer_rerank(query, rerank_pairs)
            
            # Combine with candidate pool
            rerank_results = [
                (candidate_pool[i], score) 
                for i, score in enumerate(rerank_scores)
            ]
            rerank_results.sort(key=lambda x: x[1], reverse=True)
            rerank_top = rerank_results[:min(self.stage3_top_k, final_top_k)]
            
            # Final results with chunks
            for chunk_idx, rerank_score in rerank_top:
                chunk = self.chunks[chunk_idx]
                final_results.append((chunk, rerank_score))
            
            stage_results['stage3_rerank'] = {
                'candidates': len(final_results),
                'top_scores': [score for _, score in rerank_top[:5]],
                'method': 'Cross-encoder reranking'
            }
            
            print(f"  ✓ Stage 3 final {len(final_results)} results")
            
        else:
            # No reranking - use stage 2 results
            for chunk_idx in candidate_pool[:final_top_k]:
                chunk = self.chunks[chunk_idx]
                # Use last available score (dense or BM25)
                score = 1.0  # Placeholder
                final_results.append((chunk, score))
        
        # Return results
        if return_stage_details:
            return {
                'final_results': final_results,
                'stage_details': stage_results,
                'pipeline_summary': {
                    'initial_candidates': len(self.chunks),
                    'after_stage1': stage_results.get('stage1_bm25', {}).get('candidates', len(self.chunks)),
                    'after_stage2': stage_results.get('stage2_dense', {}).get('candidates', len(candidate_pool)),
                    'final_results': len(final_results)
                }
            }
        else:
            return final_results
    
    def _llm_generative_rerank(self, query: str, rerank_pairs: List[List[str]]) -> List[float]:
        """
        LLM-based generative reranking (paper approach)
        
        Uses LLM to generate relevance scores for query-document pairs
        This is the true "Stage 3" from the paper - using LLM to generate final shortlist
        """
        import torch
        
        scores = []
        
        for query_text, doc_text in rerank_pairs:
            # Create prompt for LLM to assess relevance
            prompt = f"""<|system|>Bạn là một chuyên gia đánh giá độ liên quan của tài liệu lịch sử Việt Nam. 
Hãy đánh giá độ liên quan giữa câu hỏi và đoạn văn từ 0.0 đến 1.0.

<|user|>
Câu hỏi: {query_text}

Đoạn văn: {doc_text[:500]}...

Độ liên quan (0.0-1.0): <|assistant|>"""

            try:
                # Tokenize and generate
                inputs = self.reranker_tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
                
                with torch.no_grad():
                    outputs = self.reranker_model.generate(
                        **inputs,
                        max_new_tokens=10,
                        temperature=0.1,
                        do_sample=False,
                        pad_token_id=self.reranker_tokenizer.eos_token_id
                    )
                
                # Decode response
                response = self.reranker_tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
                
                # Extract score from response
                try:
                    score = float(response.strip())
                    score = max(0.0, min(1.0, score))  # Clamp to [0,1]
                except:
                    score = 0.5  # Default score if parsing fails
                    
                scores.append(score)
                
            except Exception as e:
                print(f"LLM reranking failed for pair: {e}")
                scores.append(0.5)  # Default score
        
        return scores
    
    def _sentence_transformer_rerank(self, query: str, rerank_pairs: List[List[str]]) -> List[float]:
        """Fallback reranking using sentence transformer"""
        query_embedding = self.reranker.encode([query], convert_to_numpy=True)
        
        chunk_contents = [pair[1] for pair in rerank_pairs]
        chunk_embeddings = self.reranker.encode(chunk_contents, convert_to_numpy=True)
        
        similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
        return similarities.tolist()
    
    def retrieve_documents_three_stage(self,
                                     query: str,
                                     query_tokens: List[str],
                                     top_k_documents: int = 10) -> List[Tuple[int, float, List[DocumentChunk]]]:
        """
        Document-level retrieval using three-stage approach
        """
        # Get chunk results
        chunk_results = self.retrieve_three_stage(
            query, query_tokens, 
            final_top_k=50  # Get more chunks for document aggregation
        )
        
        # Group by document
        doc_chunks = defaultdict(list)
        for chunk, score in chunk_results:
            doc_id = self.chunk_to_doc_map.get(chunk.chunk_id)
            if doc_id is not None:
                doc_chunks[doc_id].append((chunk, score))
        
        # Aggregate document scores (using max strategy)
        doc_results = []
        for doc_id, chunk_score_pairs in doc_chunks.items():
            doc_score = max(score for _, score in chunk_score_pairs)
            best_chunks = sorted(chunk_score_pairs, key=lambda x: x[1], reverse=True)[:3]
            best_chunks = [chunk for chunk, _ in best_chunks]
            
            doc_results.append((doc_id, doc_score, best_chunks))
        
        # Sort and return top documents
        doc_results.sort(key=lambda x: x[1], reverse=True)
        return doc_results[:top_k_documents]
    
    def compare_with_current_system(self,
                                  query: str, 
                                  query_tokens: List[str],
                                  current_system_results: List,
                                  top_k: int = 10) -> Dict:
        """
        Compare three-stage results with current hybrid system
        """
        # Get three-stage results with details
        three_stage_results = self.retrieve_three_stage(
            query, query_tokens, 
            final_top_k=top_k,
            return_stage_details=True
        )
        
        comparison = {
            'query': query,
            'three_stage_pipeline': three_stage_results['pipeline_summary'],
            'three_stage_results': len(three_stage_results['final_results']),
            'current_system_results': len(current_system_results),
            'stage_breakdown': three_stage_results['stage_details']
        }
        
        return comparison
    
    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the three-stage pipeline"""
        stats = {
            'total_chunks': len(self.chunks),
            'stage1_enabled': self.use_bm25,
            'stage2_enabled': self.use_dense_retrieval,
            'stage3_enabled': self.use_reranking,
            'stage1_top_k': self.stage1_top_k,
            'stage2_top_k': self.stage2_top_k,
            'stage3_top_k': self.stage3_top_k,
            'weights': {
                'bm25': self.bm25_weight,
                'dense': self.dense_weight,
                'rerank': self.rerank_weight
            }
        }
        
        return stats


def create_three_stage_config(use_case: str = 'balanced') -> Dict:
    """
    Create configuration for different use cases
    
    Args:
        use_case: 'fast', 'balanced', 'accurate'
    """
    
    if use_case == 'fast':
        return {
            'use_bm25': True,
            'use_dense_retrieval': False,  # Skip dense retrieval
            'use_reranking': False,        # Skip reranking
            'stage1_top_k': 20,
            'bm25_weight': 1.0
        }
    
    elif use_case == 'balanced':
        return {
            'use_bm25': True,
            'use_dense_retrieval': True,
            'use_reranking': False,        # Skip expensive reranking
            'stage1_top_k': 100,
            'stage2_top_k': 20,
            'bm25_weight': 0.4,
            'dense_weight': 0.6
        }
    
    elif use_case == 'accurate':
        return {
            'use_bm25': True,
            'use_dense_retrieval': True,
            'use_reranking': True,         # Full three-stage pipeline
            'stage1_top_k': 100,
            'stage2_top_k': 50,
            'stage3_top_k': 20,
            'bm25_weight': 0.3,
            'dense_weight': 0.4,
            'rerank_weight': 0.3
        }
    
    else:
        raise ValueError(f"Unknown use_case: {use_case}")