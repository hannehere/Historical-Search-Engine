"""
ContextAwareChunker.py
Context-aware chunking for Vietnamese semantic-rich text

Focuses on preserving Vietnamese linguistic context and semantic coherence
"""

from typing import List, Dict, Tuple, Optional
from DocumentChunker import DocumentChunk, ChunkingStrategy
from EnhancedVietnameseTokenizer import EnhancedVietnameseTokenizer
import re


class VietnameseContextAwareChunker:
    """
    Context-aware chunker for Vietnamese text
    
    Features:
    - Preserves Vietnamese semantic units
    - Maintains context across chunk boundaries
    - Handles Vietnamese compound sentences
    - Respects Vietnamese paragraph structure
    - Preserves named entities and historical context
    """
    
    def __init__(self,
                 chunk_size: int = 256,
                 overlap_size: int = 64,
                 preserve_sentences: bool = True,
                 preserve_entities: bool = True,
                 min_chunk_size: int = 50):
        """
        Args:
            chunk_size: Target chunk size in words
            overlap_size: Overlap between chunks for context
            preserve_sentences: Don't break sentences in middle
            preserve_entities: Keep named entities together
            min_chunk_size: Minimum acceptable chunk size
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.preserve_sentences = preserve_sentences
        self.preserve_entities = preserve_entities
        self.min_chunk_size = min_chunk_size
        
        # Initialize enhanced tokenizer for context awareness
        self.tokenizer = EnhancedVietnameseTokenizer(
            use_stopwords=False,  # Keep all words for context
            library='underthesea',
            enable_ner=True,
            preserve_entities=True
        )
        
        # Vietnamese sentence patterns
        self.sentence_endings = re.compile(r'[.!?;:](?=\s|$)')
        self.paragraph_breaks = re.compile(r'\n\s*\n')
        
        # Vietnamese semantic boundary markers
        self.semantic_boundaries = {
            'strong': ['Tuy nhiên', 'Tuy vậy', 'Mặc dù', 'Bởi vì', 'Do đó', 'Vì thế', 'Vì vậy'],
            'medium': ['Và', 'Nhưng', 'Song', 'Còn', 'Lại', 'Cũng', 'Ngoài ra'],
            'weak': ['Khi', 'Lúc', 'Trong khi', 'Sau khi', 'Trước khi', 'Để']
        }
    
    def chunk_document(self, content: str, source_file: str) -> List[DocumentChunk]:
        """
        Context-aware chunking for Vietnamese documents
        """
        chunks = []
        
        # Split into paragraphs first
        paragraphs = self.paragraph_breaks.split(content.strip())
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        current_chunk_content = ""
        current_chunk_sentences = []
        chunk_index = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            # Get sentences in paragraph
            sentences = self._split_vietnamese_sentences(paragraph)
            
            for sentence in sentences:
                # Tokenize sentence with context
                tokens, entities = self.tokenizer.tokenize(sentence, return_entities=True)
                
                # Check if adding this sentence would exceed chunk size
                current_tokens = self.tokenizer.tokenize(current_chunk_content)
                
                if len(current_tokens) + len(tokens) > self.chunk_size and current_chunk_content:
                    # Create chunk from current content
                    chunk = self._create_context_chunk(
                        content=current_chunk_content,
                        sentences=current_chunk_sentences,
                        source_file=source_file,
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    overlap_content = self._create_overlap_content(current_chunk_sentences)
                    current_chunk_content = overlap_content
                    current_chunk_sentences = self._get_overlap_sentences(current_chunk_sentences)
                    chunk_index += 1
                
                # Add sentence to current chunk
                current_chunk_content += (" " if current_chunk_content else "") + sentence
                current_chunk_sentences.append({
                    'text': sentence,
                    'tokens': tokens,
                    'entities': entities
                })
        
        # Create final chunk if there's remaining content
        if current_chunk_content.strip():
            chunk = self._create_context_chunk(
                content=current_chunk_content,
                sentences=current_chunk_sentences,
                source_file=source_file,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_vietnamese_sentences(self, paragraph: str) -> List[str]:
        """
        Split paragraph into Vietnamese sentences
        
        Handles Vietnamese sentence patterns and punctuation
        """
        # Basic sentence splitting
        sentences = self.sentence_endings.split(paragraph)
        
        result_sentences = []
        current_sentence = ""
        
        for i, part in enumerate(sentences):
            part = part.strip()
            if not part:
                continue
                
            current_sentence += part
            
            # Check if this looks like end of sentence
            if i < len(sentences) - 1:  # Not the last part
                # Add punctuation back
                next_char_match = self.sentence_endings.search(paragraph[paragraph.find(part) + len(part):])
                if next_char_match:
                    current_sentence += next_char_match.group(0)
                
                # Check if this is really sentence end
                if self._is_sentence_boundary(current_sentence, sentences[i+1] if i+1 < len(sentences) else ""):
                    result_sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Add remaining content
        if current_sentence.strip():
            result_sentences.append(current_sentence.strip())
        
        return [s for s in result_sentences if s.strip()]
    
    def _is_sentence_boundary(self, current: str, next_part: str) -> bool:
        """
        Determine if this is a real sentence boundary
        
        Handles Vietnamese abbreviations and special cases
        """
        current = current.strip()
        next_part = next_part.strip()
        
        # Common Vietnamese abbreviations that shouldn't end sentences
        abbreviations = ['TP.', 'Q.', 'P.', 'TT.', 'Th.', 'CN.', 'GS.', 'PGS.', 'TS.', 'ThS.']
        
        for abbrev in abbreviations:
            if current.endswith(abbrev):
                return False
        
        # If next part starts with lowercase, probably continuation
        if next_part and next_part[0].islower():
            return False
        
        # If current sentence is very short, might be title/heading
        if len(current.split()) < 3:
            return False
        
        return True
    
    def _create_context_chunk(self, 
                            content: str, 
                            sentences: List[Dict], 
                            source_file: str, 
                            chunk_index: int) -> DocumentChunk:
        """
        Create a DocumentChunk with rich Vietnamese context metadata
        """
        # Aggregate entities from all sentences
        all_entities = {
            'persons': [],
            'locations': [],
            'historical_periods': [],
            'years': [],
            'compound_words': []
        }
        
        for sentence in sentences:
            entities = sentence['entities']
            for key in all_entities:
                all_entities[key].extend(entities.get(key, []))
        
        # Remove duplicates
        for key in all_entities:
            all_entities[key] = list(set(all_entities[key]))
        
        # Determine chunk type based on content
        chunk_type = self._determine_vietnamese_chunk_type(content, all_entities)
        
        # Create metadata
        metadata = {
            'entities': all_entities,
            'sentence_count': len(sentences),
            'has_historical_context': bool(all_entities['persons'] or all_entities['historical_periods']),
            'has_geographical_context': bool(all_entities['locations']),
            'has_temporal_context': bool(all_entities['years']),
            'vietnamese_complexity': self._assess_vietnamese_complexity(content),
            'semantic_coherence': self._assess_semantic_coherence(sentences)
        }
        
        return DocumentChunk(
            chunk_id=f"{source_file}_{chunk_index}",
            content=content.strip(),
            source_file=source_file,
            chunk_index=chunk_index,
            chunk_type=chunk_type,
            level=0,
            metadata=metadata
        )
    
    def _determine_vietnamese_chunk_type(self, content: str, entities: Dict) -> str:
        """
        Determine chunk type based on Vietnamese content characteristics
        """
        # Check for title/header patterns
        if re.match(r'^[A-ZÁÀẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴĐ][^.!?]*$', content.strip()):
            return 'title'
        
        # Check for introduction patterns
        intro_patterns = ['giới thiệu', 'tổng quan', 'khái quát', 'đại cương']
        if any(pattern in content.lower() for pattern in intro_patterns):
            return 'introduction'
        
        # Check for historical narrative
        if entities['persons'] and entities['historical_periods']:
            return 'historical_narrative'
        
        # Check for geographical description
        if entities['locations'] and len(entities['locations']) >= 2:
            return 'geographical_description'
        
        # Check for biographical content
        if entities['persons'] and entities['years']:
            return 'biographical'
        
        # Default to regular paragraph
        return 'paragraph'
    
    def _assess_vietnamese_complexity(self, content: str) -> str:
        """
        Assess the linguistic complexity of Vietnamese content
        """
        # Count compound words and complex structures
        compound_words = len(re.findall(r'\w+_\w+', content))
        total_words = len(content.split())
        
        if total_words == 0:
            return 'low'
        
        compound_ratio = compound_words / total_words
        
        # Count complex sentence markers
        complex_markers = ['mặc dù', 'tuy nhiên', 'do đó', 'vì vậy', 'bởi lẽ', 'cho nên']
        complex_count = sum(1 for marker in complex_markers if marker in content.lower())
        
        # Assess complexity
        if compound_ratio > 0.3 or complex_count > 2:
            return 'high'
        elif compound_ratio > 0.1 or complex_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _assess_semantic_coherence(self, sentences: List[Dict]) -> float:
        """
        Assess semantic coherence between sentences in chunk
        """
        if len(sentences) < 2:
            return 1.0
        
        # Simple coherence based on entity overlap
        coherence_score = 0.0
        total_pairs = 0
        
        for i in range(len(sentences) - 1):
            entities1 = sentences[i]['entities']
            entities2 = sentences[i + 1]['entities']
            
            # Calculate entity overlap
            overlap = 0
            total_entities = 0
            
            for key in entities1:
                set1 = set(entities1[key])
                set2 = set(entities2[key])
                overlap += len(set1 & set2)
                total_entities += len(set1 | set2)
            
            if total_entities > 0:
                pair_coherence = overlap / total_entities
                coherence_score += pair_coherence
                total_pairs += 1
        
        return coherence_score / total_pairs if total_pairs > 0 else 0.5
    
    def _create_overlap_content(self, sentences: List[Dict]) -> str:
        """
        Create overlap content for context preservation
        """
        if not sentences or self.overlap_size <= 0:
            return ""
        
        # Take last few sentences for overlap
        overlap_sentences = sentences[-min(len(sentences), 2):]  # Last 2 sentences
        overlap_content = " ".join(s['text'] for s in overlap_sentences)
        
        # Limit by word count
        words = overlap_content.split()
        if len(words) > self.overlap_size:
            overlap_content = " ".join(words[-self.overlap_size:])
        
        return overlap_content
    
    def _get_overlap_sentences(self, sentences: List[Dict]) -> List[Dict]:
        """
        Get sentence structures for overlap
        """
        if not sentences or self.overlap_size <= 0:
            return []
        
        return sentences[-min(len(sentences), 2):]  # Last 2 sentences


def create_context_aware_chunker(document_type: str = 'historical') -> VietnameseContextAwareChunker:
    """
    Factory for different document types
    
    Args:
        document_type: 'historical', 'biographical', 'geographical'
    """
    
    if document_type == 'historical':
        return VietnameseContextAwareChunker(
            chunk_size=300,  # Larger chunks for historical context
            overlap_size=75,
            preserve_sentences=True,
            preserve_entities=True,
            min_chunk_size=100
        )
    
    elif document_type == 'biographical':
        return VietnameseContextAwareChunker(
            chunk_size=256,
            overlap_size=64,
            preserve_sentences=True,
            preserve_entities=True,  # Very important for biographical data
            min_chunk_size=80
        )
    
    elif document_type == 'geographical':
        return VietnameseContextAwareChunker(
            chunk_size=200,  # Smaller chunks for location-specific info
            overlap_size=50,
            preserve_sentences=True,
            preserve_entities=True,
            min_chunk_size=60
        )
    
    else:
        return VietnameseContextAwareChunker()  # Default settings