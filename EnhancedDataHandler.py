"""
EnhancedDataHandler.py
Advanced Data Handler với chunking support

Chịu trách nhiệm:
- Load và process documents
- Integrate với DocumentChunker
- Quản lý chunk metadata
- Caching và optimization
"""

import json
import pickle
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from DocumentChunker import VietnameseDocumentChunker, DocumentChunk, ChunkerFactory


class EnhancedDataHandler:
    """
    Enhanced DataHandler với chunking capabilities
    
    Features:
    - Document chunking integration
    - Intelligent caching
    - Chunk metadata management
    - Multi-level indexing
    - Performance optimization
    """
    
    def __init__(self, 
                 data_path: str,
                 chunking_strategy: str = 'hybrid',
                 chunk_size: int = 512,
                 overlap_size: int = 50,
                 enable_caching: bool = True,
                 cache_dir: str = "./cache"):
        """
        Args:
            data_path: Đường dẫn đến file JSON dataset
            chunking_strategy: 'semantic', 'hierarchical', 'hybrid', 'fixed'
            chunk_size: Kích thước chunk (tokens)
            overlap_size: Overlap giữa chunks
            enable_caching: Có enable caching không
            cache_dir: Thư mục cache
        """
        self.data_path = Path(data_path)
        self.chunking_strategy = chunking_strategy
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.enable_caching = enable_caching
        self.cache_dir = Path(cache_dir)
        
        # Initialize components
        self.chunker = ChunkerFactory.create_chunker(
            chunking_strategy,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        
        # Data storage
        self.documents: List[Dict] = []
        self.chunks: List[DocumentChunk] = []
        self.chunk_to_doc_map: Dict[str, int] = {}  # chunk_id -> doc_id
        self.doc_to_chunks_map: Dict[int, List[str]] = {}  # doc_id -> [chunk_ids]
        
        # Caching
        if enable_caching:
            self.cache_dir.mkdir(exist_ok=True)
            self._cache_file = self.cache_dir / f"chunks_{self._get_cache_key()}.pkl"
        else:
            self._cache_file = None
    
    def load_data(self) -> Tuple[List[Dict], List[DocumentChunk]]:
        """
        Load documents và tạo chunks
        
        Returns:
            Tuple[List[Dict], List[DocumentChunk]]: (documents, chunks)
        """
        # Load documents
        self._load_documents()
        
        # Load hoặc tạo chunks
        if self._should_use_cache():
            print("📄 Loading chunks from cache...")
            self._load_chunks_from_cache()
        else:
            print("🔧 Creating chunks from documents...")
            self._create_chunks()
            if self.enable_caching:
                self._save_chunks_to_cache()
        
        print(f"✓ Loaded {len(self.documents)} documents và {len(self.chunks)} chunks")
        return self.documents, self.chunks
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get chunk by ID"""
        for chunk in self.chunks:
            if chunk.chunk_id == chunk_id:
                return chunk
        return None
    
    def get_chunks_by_doc_id(self, doc_id: int) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        if doc_id in self.doc_to_chunks_map:
            chunk_ids = self.doc_to_chunks_map[doc_id]
            return [self.get_chunk_by_id(cid) for cid in chunk_ids if self.get_chunk_by_id(cid)]
        return []
    
    def get_parent_document(self, chunk_id: str) -> Optional[Dict]:
        """Get parent document of a chunk"""
        if chunk_id in self.chunk_to_doc_map:
            doc_id = self.chunk_to_doc_map[chunk_id]
            return self.get_document_by_id(doc_id)
        return None
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """Get document by ID"""
        if 0 <= doc_id < len(self.documents):
            return self.documents[doc_id]
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        return self.documents
    
    def get_all_chunks(self) -> List[DocumentChunk]:
        """Get all chunks"""
        return self.chunks
    
    def get_chunks_count(self) -> int:
        """Get total chunks count"""
        return len(self.chunks)
    
    def get_documents_count(self) -> int:
        """Get total documents count"""
        return len(self.documents)
    
    def get_chunk_statistics(self) -> Dict:
        """Get statistics about chunks"""
        stats = {
            'total_chunks': len(self.chunks),
            'total_documents': len(self.documents),
            'chunks_per_doc': len(self.chunks) / len(self.documents) if self.documents else 0,
            'chunk_types': {},
            'chunk_levels': {},
            'avg_chunk_length': 0
        }
        
        total_length = 0
        for chunk in self.chunks:
            # Count by type
            chunk_type = chunk.chunk_type
            stats['chunk_types'][chunk_type] = stats['chunk_types'].get(chunk_type, 0) + 1
            
            # Count by level
            level = chunk.level
            stats['chunk_levels'][level] = stats['chunk_levels'].get(level, 0) + 1
            
            # Calculate length
            total_length += len(chunk.content)
        
        if self.chunks:
            stats['avg_chunk_length'] = total_length / len(self.chunks)
        
        return stats
    
    def search_chunks_by_metadata(self, **metadata_filters) -> List[DocumentChunk]:
        """
        Search chunks by metadata filters
        
        Args:
            **metadata_filters: Key-value pairs to filter by
            
        Returns:
            List[DocumentChunk]: Matching chunks
        """
        matching_chunks = []
        
        for chunk in self.chunks:
            match = True
            for key, value in metadata_filters.items():
                if key not in chunk.metadata or chunk.metadata[key] != value:
                    match = False
                    break
            
            if match:
                matching_chunks.append(chunk)
        
        return matching_chunks
    
    def _load_documents(self):
        """Load documents from JSON file"""
        if not self.data_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            
            print(f"✓ Đã load {len(self.documents)} documents từ {self.data_path}")
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"File JSON không hợp lệ: {e.msg}", 
                e.doc, 
                e.pos
            )
    
    def _create_chunks(self):
        """Create chunks from documents"""
        self.chunks = []
        self.chunk_to_doc_map = {}
        self.doc_to_chunks_map = {}
        
        for doc_id, document in enumerate(self.documents):
            content = document['content']
            file_name = document['file_name']
            
            # Create chunks for this document
            doc_chunks = self.chunker.chunk_document(doc_id, content, file_name)
            
            # Store chunks and mappings
            chunk_ids = []
            for chunk in doc_chunks:
                self.chunks.append(chunk)
                self.chunk_to_doc_map[chunk.chunk_id] = doc_id
                chunk_ids.append(chunk.chunk_id)
            
            self.doc_to_chunks_map[doc_id] = chunk_ids
            
            print(f"  → {file_name}: {len(doc_chunks)} chunks")
    
    def _get_cache_key(self) -> str:
        """Generate cache key based on data file and config"""
        # Hash của file data + config
        with open(self.data_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        
        config_str = f"{self.chunking_strategy}_{self.chunk_size}_{self.overlap_size}"
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        
        return f"{file_hash}_{config_hash}"
    
    def _should_use_cache(self) -> bool:
        """Check if should use cached chunks"""
        return (
            self.enable_caching 
            and self._cache_file 
            and self._cache_file.exists()
        )
    
    def _save_chunks_to_cache(self):
        """Save chunks to cache"""
        if not self._cache_file:
            return
        
        cache_data = {
            'chunks': self.chunks,
            'chunk_to_doc_map': self.chunk_to_doc_map,
            'doc_to_chunks_map': self.doc_to_chunks_map,
            'config': {
                'chunking_strategy': self.chunking_strategy,
                'chunk_size': self.chunk_size,
                'overlap_size': self.overlap_size
            }
        }
        
        with open(self._cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"💾 Cached chunks to {self._cache_file}")
    
    def _load_chunks_from_cache(self):
        """Load chunks from cache"""
        if not self._cache_file or not self._cache_file.exists():
            return False
        
        try:
            with open(self._cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.chunks = cache_data['chunks']
            self.chunk_to_doc_map = cache_data['chunk_to_doc_map']
            self.doc_to_chunks_map = cache_data['doc_to_chunks_map']
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
            return False
    
    def clear_cache(self):
        """Clear cached chunks"""
        if self._cache_file and self._cache_file.exists():
            self._cache_file.unlink()
            print("🗑️ Cache cleared")
    
    def export_chunks_to_json(self, output_path: str):
        """
        Export chunks to JSON for analysis
        
        Args:
            output_path: Đường dẫn output file
        """
        export_data = []
        
        for chunk in self.chunks:
            export_data.append({
                'chunk_id': chunk.chunk_id,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'parent_doc_id': chunk.parent_doc_id,
                'chunk_index': chunk.chunk_index,
                'chunk_type': chunk.chunk_type,
                'level': chunk.level,
                'start_pos': chunk.start_pos,
                'end_pos': chunk.end_pos,
                'content_length': len(chunk.content),
                'word_count': len(chunk.content.split())
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Exported {len(export_data)} chunks to {output_path}")


# Utility functions
def analyze_chunking_performance(data_handler: EnhancedDataHandler) -> Dict:
    """
    Analyze chunking performance và quality
    
    Args:
        data_handler: EnhancedDataHandler instance
        
    Returns:
        Dict: Performance metrics
    """
    stats = data_handler.get_chunk_statistics()
    
    # Additional analysis
    chunks = data_handler.get_all_chunks()
    
    # Chunk size distribution
    sizes = [len(chunk.content.split()) for chunk in chunks]
    stats['chunk_size_stats'] = {
        'min': min(sizes) if sizes else 0,
        'max': max(sizes) if sizes else 0,
        'avg': sum(sizes) / len(sizes) if sizes else 0,
        'median': sorted(sizes)[len(sizes)//2] if sizes else 0
    }
    
    # Content overlap analysis (simple)
    overlap_count = 0
    for i, chunk1 in enumerate(chunks[:10]):  # Sample first 10
        for chunk2 in chunks[i+1:i+6]:  # Compare with next 5
            if chunk1.parent_doc_id == chunk2.parent_doc_id:
                words1 = set(chunk1.content.lower().split())
                words2 = set(chunk2.content.lower().split())
                if words1 & words2:
                    overlap_count += 1
    
    stats['overlap_detected'] = overlap_count
    
    return stats