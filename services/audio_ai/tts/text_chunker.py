"""
Text Chunking Service for Long-form TTS
Splits long text into manageable chunks for TTS generation
"""
import re
from typing import List, Tuple


class TextChunker:
    """Service for splitting long text into TTS-friendly chunks."""
    
    def __init__(self, max_chunk_size: int = 800):
        """
        Initialize text chunker.
        
        Args:
            max_chunk_size: Maximum characters per chunk (default 800 for safety margin)
        """
        self.max_chunk_size = max_chunk_size
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks at natural boundaries (sentences, paragraphs).
        
        Args:
            text: Long text to split
            
        Returns:
            List of text chunks
        """
        # If text is short enough, return as-is
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # If paragraph itself is too long, split by sentences
            if len(paragraph) > self.max_chunk_size:
                sentences = self._split_into_sentences(paragraph)
                
                for sentence in sentences:
                    # If adding this sentence exceeds limit, save current chunk
                    if len(current_chunk) + len(sentence) > self.max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                    
                    # If single sentence is too long, force split by words
                    if len(sentence) > self.max_chunk_size:
                        word_chunks = self._split_by_words(sentence)
                        chunks.extend(word_chunks[:-1])  # Add all but last
                        current_chunk = word_chunks[-1]  # Keep last for next iteration
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
            else:
                # Paragraph fits, check if adding it exceeds limit
                if len(current_chunk) + len(paragraph) > self.max_chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = paragraph
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Split on sentence boundaries (., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_by_words(self, text: str) -> List[str]:
        """Force split long text by words when sentence is too long."""
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
            else:
                current_chunk += " " + word if current_chunk else word
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_chunk_info(self, text: str) -> Tuple[int, List[Tuple[int, str]]]:
        """
        Get information about how text will be chunked.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (total_chunks, list of (chunk_length, chunk_preview))
        """
        chunks = self.split_text(text)
        chunk_info = [(len(chunk), chunk[:50] + "..." if len(chunk) > 50 else chunk) 
                      for chunk in chunks]
        return len(chunks), chunk_info
