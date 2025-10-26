import numpy as np
from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class DataRetrieval:
    """
    Nguyên tắc loose coupling:
    - Nhận tokenized documents làm input
    - Không phụ thuộc vào cách tokenize
    - Trả về ranked list documents
    """
    
    def __init__(self, 
                 embedding_model: str = 'keepitreal/vietnamese-sbert',
                 use_bm25: bool = True,
                 use_embedding: bool = True,
                 bm25_weight: float = 0.5):
        """
        Args:
            embedding_model: Tên model embedding (cho tiếng Việt)
            use_bm25: Có sử dụng BM25 không
            use_embedding: Có sử dụng embedding không
            bm25_weight: Trọng số cho BM25 (0-1), còn lại là embedding
        """
        self.use_bm25 = use_bm25
        self.use_embedding = use_embedding
        self.bm25_weight = bm25_weight
        
        # Khởi tạo BM25
        self.bm25 = None
        self.tokenized_corpus = []
        
        # Khởi tạo embedding model
        if use_embedding:
            print(f"Đang load embedding model: {embedding_model}...")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.document_embeddings = None
        else:
            self.embedding_model = None
    
    def index_documents(self, 
                       tokenized_docs: List[List[str]], 
                       raw_docs: List[str]):
        """
        Args:
            tokenized_docs: Documents đã tokenize
            raw_docs: Documents gốc (cho embedding)
        """
        # Index BM25
        if self.use_bm25:
            print("Đang tạo BM25 index...")
            self.tokenized_corpus = tokenized_docs
            self.bm25 = BM25Okapi(tokenized_docs)
            print(f"✓ Đã index {len(tokenized_docs)} documents với BM25")
        
        # Index Embedding
        if self.use_embedding:
            print("Đang tạo document embeddings...")
            self.document_embeddings = self.embedding_model.encode(
                raw_docs, 
                show_progress_bar=True,
                convert_to_numpy=True
            )
            print(f"✓ Đã tạo embeddings cho {len(raw_docs)} documents")
    
    def retrieve_bm25(self, 
                     query_tokens: List[str], 
                     top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Retrieve documents sử dụng BM25
        
        Args:
            query_tokens: Query đã tokenize
            top_k: Số documents trả về
            
        Returns:
            List[Tuple[int, float]]: [(doc_id, score), ...]
        """
        if self.bm25 is None:
            raise ValueError("BM25 chưa được index. Gọi index_documents() trước.")
        
        # Tính BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Lấy top_k documents
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(int(idx), float(scores[idx])) for idx in top_indices]
        
        return results
    
    def retrieve_embedding(self, 
                          query: str, 
                          top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Retrieve documents sử dụng embedding similarity
        
        Args:
            query: Query text
            top_k: Số documents trả về
            
        Returns:
            List[Tuple[int, float]]: [(doc_id, score), ...]
        """
        if self.document_embeddings is None:
            raise ValueError("Embeddings chưa được tạo. Gọi index_documents() trước.")
        
        # Encode query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Tính cosine similarity
        similarities = cosine_similarity(query_embedding, self.document_embeddings)[0]
        
        # Lấy top_k documents
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        
        return results
    
    def retrieve_hybrid(self, 
                       query: str, 
                       query_tokens: List[str], 
                       top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Retrieve documents kết hợp BM25 và Embedding (Hybrid Retrieval)
        
        Args:
            query: Query text gốc
            query_tokens: Query đã tokenize
            top_k: Số documents trả về
            
        Returns:
            List[Tuple[int, float]]: [(doc_id, score), ...] đã được sắp xếp
        """
        all_scores = {}
        
        # Retrieve với BM25
        if self.use_bm25:
            bm25_results = self.retrieve_bm25(query_tokens, top_k=top_k*2)
            
            # Normalize BM25 scores
            max_bm25_score = max([score for _, score in bm25_results]) if bm25_results else 1.0
            if max_bm25_score > 0:
                for doc_id, score in bm25_results:
                    all_scores[doc_id] = self.bm25_weight * (score / max_bm25_score)
        
        # Retrieve với Embedding
        if self.use_embedding:
            emb_results = self.retrieve_embedding(query, top_k=top_k*2)
            
            # Kết hợp scores
            for doc_id, score in emb_results:
                if doc_id in all_scores:
                    all_scores[doc_id] += (1 - self.bm25_weight) * score
                else:
                    all_scores[doc_id] = (1 - self.bm25_weight) * score
        
        # Sắp xếp và lấy top_k
        sorted_results = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return sorted_results
    
    def retrieve(self, 
                query: str, 
                query_tokens: List[str], 
                top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Main retrieval function - tự động chọn phương pháp phù hợp
        
        Args:
            query: Query text gốc
            query_tokens: Query đã tokenize
            top_k: Số documents trả về
            
        Returns:
            List[Tuple[int, float]]: [(doc_id, score), ...]
        """
        if self.use_bm25 and self.use_embedding:
            return self.retrieve_hybrid(query, query_tokens, top_k)
        elif self.use_bm25:
            return self.retrieve_bm25(query_tokens, top_k)
        elif self.use_embedding:
            return self.retrieve_embedding(query, top_k)
        else:
            raise ValueError("Cần enable ít nhất một phương pháp retrieval")
