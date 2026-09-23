"""
Document Chunking Utility for AI StudyMate.

Provides word-based and sentence-based chunking with overlap
for efficient retrieval and semantic search.
"""

from typing import List, Dict
import re

class TextChunker:
    """
    Utility class for splitting documents into smaller chunks
    while preserving context through overlap.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        
        print(f"✨ TextChunker initialized!")
        print(f"   Chunk size: {chunk_size} words")
        print(f"   Overlap: {overlap} words")
        print(f"   Strategy: Preserve context with intelligent overlap")
    
    def split_into_sentences(self, text: str) -> List[str]:
        
       
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        
        clean_sentences = [s.strip() for s in sentences if s.strip()]
        
        return clean_sentences
    
    def count_words(self, text: str) -> int:
        
        
        return len(text.split())
    
    def chunk_by_words(self, text: str) -> List[Dict]:
        
        
        words = text.split()
        chunks = []
        chunk_id = 0
        start = 0
        
        
        while start < len(words):
           
            end = min(start + self.chunk_size, len(words))
            
           
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'start_word': start,
                'end_word': end,
                'word_count': len(chunk_words),
                'method': 'word-based'
            })
            
            chunk_id += 1
            
            
            start = end - self.overlap
            
            
            if start <= chunks[-1]['start_word']:
                break
        
        return chunks
    
    def chunk_by_sentences(self, text: str) -> List[Dict]:
        """
        Initialize the chunker.

        Args:
            chunk_size: Maximum words per chunk.
            overlap: Number of overlapping words.
        """
        
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_word_count = self.count_words(sentence)
            
           
            if current_word_count + sentence_word_count > self.chunk_size and current_chunk:
                
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': ' '.join(current_chunk),
                    'sentence_count': len(current_chunk),
                    'word_count': current_word_count,
                    'method': 'sentence-based'
                })
                
                
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences
                current_word_count = sum(self.count_words(s) for s in current_chunk)
                
                chunk_id += 1
            
            
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
        
        
        if current_chunk:
            chunks.append({
                'chunk_id': chunk_id,
                'text': ' '.join(current_chunk),
                'sentence_count': len(current_chunk),
                'word_count': current_word_count,
                'method': 'sentence-based'
            })
        
        return chunks
    
    def chunk_text(self, text: str, method: str = 'sentences') -> List[Dict]:
        """
    
        Args:
            text (str): Text to chunk
            method (str): 'words' or 'sentences' (default: 'sentences')
        
        Returns:
            List of chunk dictionaries
            
        Recommendation: Use 'sentences' for RAG systems!
        
        HINT: Use if/elif/else to check method and call the right function
        """
        
        if method == 'words':
            return self.chunk_by_words(text)
        elif method == 'sentences':
            return self.chunk_by_sentences(text)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'words' or 'sentences'")
    
    def get_chunk_stats(self, chunks: List[Dict]) -> Dict:
        """
        
        
        TASK: Calculate useful statistics from the chunks list.
        
        Useful for optimizing chunk_size and overlap!
        
        HINT: Extract word_count from each chunk, then calculate:
        - total_chunks
        - avg_words_per_chunk
        - min_words
        - max_words
        - total_words
        - method (from first chunk)
        """
        if not chunks:
            return {'error': 'No chunks provided'}
        
       
        word_counts = [chunk['word_count'] for chunk in chunks]
        
        
        return {
            'total_chunks': len(chunks),
            'avg_words_per_chunk': sum(word_counts) / len(word_counts),
            'min_words': min(word_counts),
            'max_words': max(word_counts),
            'total_words': sum(word_counts),
            'method': chunks[0].get('method', 'unknown')
        }


