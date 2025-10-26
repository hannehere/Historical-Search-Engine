"""
DocumentChunker.py
Advanced Document Chunking Strategy for Vietnamese Documents

Chịu trách nhiệm: Chia nhỏ documents thành chunks có nghĩa
- Semantic chunking based on structure
- Sliding window with overlap
- Hierarchical chunking
- Metadata preservation
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ChunkingStrategy(Enum):
    """Các chiến lược chunking khác nhau"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"
    HYBRID = "hybrid"


@dataclass
class DocumentChunk:
    """Data class cho một chunk document"""
    chunk_id: str
    content: str
    metadata: Dict
    parent_doc_id: int
    chunk_index: int
    chunk_type: str  # 'header', 'paragraph', 'list', etc.
    level: int  # Hierarchy level (0=top)
    start_pos: int
    end_pos: int


class VietnameseDocumentChunker:
    """
    Advanced Document Chunker cho Vietnamese text
    
    Features:
    - Multi-level chunking (section, paragraph, sentence)
    - Markdown structure awareness
    - Vietnamese linguistic features support
    - Overlap preservation for context
    - Metadata enrichment
    """
    
    def __init__(self, 
                 strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
                 chunk_size: int = 512,
                 overlap_size: int = 50,
                 min_chunk_size: int = 50,
                 preserve_structure: bool = True):
        """
        Args:
            strategy: Chiến lược chunking
            chunk_size: Kích thước chunk tối đa (tokens)
            overlap_size: Kích thước overlap giữa chunks
            min_chunk_size: Kích thước chunk tối thiểu
            preserve_structure: Có giữ cấu trúc markdown không
        """
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        self.preserve_structure = preserve_structure
        
        # Regex patterns cho Vietnamese markdown
        self.patterns = {
            'headers': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'paragraphs': re.compile(r'\n\s*\n'),
            'sentences': re.compile(r'[.!?]\s+'),
            'lists': re.compile(r'^[-*+]\s+|^\d+\.\s+', re.MULTILINE),
            'code_blocks': re.compile(r'```[\s\S]*?```'),
            'inline_code': re.compile(r'`[^`]+`'),
            'bold_italic': re.compile(r'\*\*[^*]+\*\*|\*[^*]+\*'),
        }
    
    def chunk_document(self, 
                      doc_id: int, 
                      content: str, 
                      file_name: str) -> List[DocumentChunk]:
        """
        Main chunking function
        
        Args:
            doc_id: ID của document gốc
            content: Nội dung document
            file_name: Tên file
            
        Returns:
            List[DocumentChunk]: Danh sách chunks
        """
        if self.strategy == ChunkingStrategy.SEMANTIC:
            return self._semantic_chunking(doc_id, content, file_name)
        elif self.strategy == ChunkingStrategy.HIERARCHICAL:
            return self._hierarchical_chunking(doc_id, content, file_name)
        elif self.strategy == ChunkingStrategy.HYBRID:
            return self._hybrid_chunking(doc_id, content, file_name)
        else:  # FIXED_SIZE
            return self._fixed_size_chunking(doc_id, content, file_name)
    
    def _semantic_chunking(self, 
                          doc_id: int, 
                          content: str, 
                          file_name: str) -> List[DocumentChunk]:
        """
        Chunking dựa trên semantic structure của markdown
        """
        chunks = []
        sections = self._extract_sections(content)
        
        for section_idx, section in enumerate(sections):
            # Mỗi section thành một chunk
            if len(section['content'].strip()) >= self.min_chunk_size:
                chunk = DocumentChunk(
                    chunk_id=f"{doc_id}_{section_idx}",
                    content=section['content'],
                    metadata={
                        'file_name': file_name,
                        'section_title': section['title'],
                        'section_level': section['level'],
                        'chunk_strategy': 'semantic',
                        'total_sections': len(sections)
                    },
                    parent_doc_id=doc_id,
                    chunk_index=section_idx,
                    chunk_type='section',
                    level=section['level'],
                    start_pos=section['start_pos'],
                    end_pos=section['end_pos']
                )
                chunks.append(chunk)
        
        return chunks
    
    def _hierarchical_chunking(self, 
                              doc_id: int, 
                              content: str, 
                              file_name: str) -> List[DocumentChunk]:
        """
        Multi-level hierarchical chunking
        Level 0: Entire document
        Level 1: Sections (H1, H2)
        Level 2: Subsections (H3, H4)
        Level 3: Paragraphs
        """
        chunks = []
        
        # Level 0: Document overview (first paragraph + headers)
        overview = self._create_document_overview(content, file_name)
        chunks.append(DocumentChunk(
            chunk_id=f"{doc_id}_overview",
            content=overview,
            metadata={
                'file_name': file_name,
                'chunk_type': 'overview',
                'chunk_strategy': 'hierarchical'
            },
            parent_doc_id=doc_id,
            chunk_index=0,
            chunk_type='overview',
            level=0,
            start_pos=0,
            end_pos=len(overview)
        ))
        
        # Level 1-3: Sections and paragraphs
        sections = self._extract_sections(content)
        chunk_idx = 1
        
        for section in sections:
            # Level 1-2: Section chunks
            if section['level'] <= 2:
                chunks.append(DocumentChunk(
                    chunk_id=f"{doc_id}_section_{chunk_idx}",
                    content=section['content'],
                    metadata={
                        'file_name': file_name,
                        'section_title': section['title'],
                        'section_level': section['level']
                    },
                    parent_doc_id=doc_id,
                    chunk_index=chunk_idx,
                    chunk_type='section',
                    level=1,
                    start_pos=section['start_pos'],
                    end_pos=section['end_pos']
                ))
                chunk_idx += 1
            
            # Level 3: Paragraph chunks
            paragraphs = self._extract_paragraphs(section['content'])
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) >= self.min_chunk_size:
                    chunks.append(DocumentChunk(
                        chunk_id=f"{doc_id}_para_{chunk_idx}_{para_idx}",
                        content=paragraph,
                        metadata={
                            'file_name': file_name,
                            'parent_section': section['title'],
                            'paragraph_index': para_idx
                        },
                        parent_doc_id=doc_id,
                        chunk_index=chunk_idx,
                        chunk_type='paragraph',
                        level=2,
                        start_pos=0,  # Relative to section
                        end_pos=len(paragraph)
                    ))
                    chunk_idx += 1
        
        return chunks
    
    def _hybrid_chunking(self, 
                        doc_id: int, 
                        content: str, 
                        file_name: str) -> List[DocumentChunk]:
        """
        Hybrid approach: Semantic + Fixed size với overlap
        """
        chunks = []
        sections = self._extract_sections(content)
        chunk_idx = 0
        
        for section in sections:
            section_content = section['content']
            
            # Nếu section nhỏ, giữ nguyên
            if len(section_content.split()) <= self.chunk_size:
                chunks.append(DocumentChunk(
                    chunk_id=f"{doc_id}_hybrid_{chunk_idx}",
                    content=section_content,
                    metadata={
                        'file_name': file_name,
                        'section_title': section['title'],
                        'chunk_strategy': 'hybrid_whole_section'
                    },
                    parent_doc_id=doc_id,
                    chunk_index=chunk_idx,
                    chunk_type='section',
                    level=section['level'],
                    start_pos=section['start_pos'],
                    end_pos=section['end_pos']
                ))
                chunk_idx += 1
            
            else:
                # Section lớn -> chia nhỏ với overlap
                sub_chunks = self._sliding_window_chunk(
                    section_content, 
                    self.chunk_size, 
                    self.overlap_size
                )
                
                for sub_idx, sub_chunk in enumerate(sub_chunks):
                    chunks.append(DocumentChunk(
                        chunk_id=f"{doc_id}_hybrid_{chunk_idx}_{sub_idx}",
                        content=sub_chunk,
                        metadata={
                            'file_name': file_name,
                            'section_title': section['title'],
                            'chunk_strategy': 'hybrid_sliding_window',
                            'sub_chunk_index': sub_idx,
                            'total_sub_chunks': len(sub_chunks)
                        },
                        parent_doc_id=doc_id,
                        chunk_index=chunk_idx,
                        chunk_type='sub_section',
                        level=section['level'] + 1,
                        start_pos=0,
                        end_pos=len(sub_chunk)
                    ))
                    chunk_idx += 1
        
        return chunks
    
    def _fixed_size_chunking(self, 
                            doc_id: int, 
                            content: str, 
                            file_name: str) -> List[DocumentChunk]:
        """
        Simple fixed-size chunking với overlap
        """
        chunks = []
        sub_chunks = self._sliding_window_chunk(content, self.chunk_size, self.overlap_size)
        
        for idx, chunk_content in enumerate(sub_chunks):
            chunks.append(DocumentChunk(
                chunk_id=f"{doc_id}_fixed_{idx}",
                content=chunk_content,
                metadata={
                    'file_name': file_name,
                    'chunk_strategy': 'fixed_size',
                    'chunk_index': idx,
                    'total_chunks': len(sub_chunks)
                },
                parent_doc_id=doc_id,
                chunk_index=idx,
                chunk_type='fixed_chunk',
                level=0,
                start_pos=idx * (self.chunk_size - self.overlap_size),
                end_pos=(idx + 1) * (self.chunk_size - self.overlap_size)
            ))
        
        return chunks
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections based on markdown headers"""
        sections = []
        lines = content.split('\n')
        current_section = {'title': '', 'content': '', 'level': 0, 'start_pos': 0, 'end_pos': 0}
        start_pos = 0
        
        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Save previous section
                if current_section['content'].strip():
                    current_section['end_pos'] = start_pos
                    sections.append(current_section.copy())
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                current_section = {
                    'title': title,
                    'content': line + '\n',
                    'level': level,
                    'start_pos': start_pos,
                    'end_pos': 0
                }
            else:
                current_section['content'] += line + '\n'
            
            start_pos += len(line) + 1
        
        # Add last section
        if current_section['content'].strip():
            current_section['end_pos'] = start_pos
            sections.append(current_section)
        
        return sections
    
    def _extract_paragraphs(self, content: str) -> List[str]:
        """Extract paragraphs from content"""
        paragraphs = re.split(r'\n\s*\n', content)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _sliding_window_chunk(self, 
                             text: str, 
                             chunk_size: int, 
                             overlap_size: int) -> List[str]:
        """
        Sliding window chunking với overlap
        """
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [text]
        
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunks.append(' '.join(chunk_words))
            
            if end >= len(words):
                break
            
            start += chunk_size - overlap_size
        
        return chunks
    
    def _create_document_overview(self, content: str, file_name: str) -> str:
        """
        Tạo overview của document bằng cách extract headers và first paragraph
        """
        lines = content.split('\n')
        overview_parts = [f"Document: {file_name}\n"]
        
        # Extract all headers
        headers = []
        first_paragraph = ""
        
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                headers.append(line)
            elif not first_paragraph and line.strip() and not line.startswith('#'):
                # First non-header paragraph
                paragraph_lines = []
                for subsequent_line in lines[lines.index(line):]:
                    if subsequent_line.strip() and not subsequent_line.startswith('#'):
                        paragraph_lines.append(subsequent_line)
                    else:
                        break
                first_paragraph = ' '.join(paragraph_lines)[:300] + "..."
                break
        
        if headers:
            overview_parts.append("Structure:\n" + '\n'.join(headers))
        
        if first_paragraph:
            overview_parts.append(f"\nContent Preview:\n{first_paragraph}")
        
        return '\n\n'.join(overview_parts)


# Factory pattern cho easy instantiation
class ChunkerFactory:
    """Factory class để tạo chunker instances"""
    
    @staticmethod
    def create_chunker(chunking_type: str, **kwargs) -> VietnameseDocumentChunker:
        """
        Factory method để tạo chunker
        
        Args:
            chunking_type: 'semantic', 'hierarchical', 'hybrid', 'fixed'
            **kwargs: Additional parameters
        """
        strategy_map = {
            'semantic': ChunkingStrategy.SEMANTIC,
            'hierarchical': ChunkingStrategy.HIERARCHICAL,
            'hybrid': ChunkingStrategy.HYBRID,
            'fixed': ChunkingStrategy.FIXED_SIZE
        }
        
        strategy = strategy_map.get(chunking_type, ChunkingStrategy.HYBRID)
        return VietnameseDocumentChunker(strategy=strategy, **kwargs)