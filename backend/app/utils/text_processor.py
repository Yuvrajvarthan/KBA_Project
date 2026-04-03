import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Service for text cleaning, normalization, and chunking"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines and replace with single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove common artifacts
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\n]', ' ', text)
        
        # Remove multiple punctuation marks
        text = re.sub(r'([.!?])\1+', r'\1', text)
        
        # Clean up any remaining excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap"""
        if not text:
            return []
        
        if chunk_size <= overlap:
            logger.warning("Chunk size should be larger than overlap. Using chunk_size=500, overlap=100")
            chunk_size = 500
            overlap = 100
        
        chunks = []
        text_length = len(text)
        
        # If text is shorter than chunk size, return as single chunk
        if text_length <= chunk_size:
            return [text] if text.strip() else []
        
        start = 0
        while start < text_length:
            # Calculate end position
            end = min(start + chunk_size, text_length)
            
            # If we're not at the end, try to break at a sentence or word boundary
            if end < text_length:
                # Try to find sentence boundary (., !, ?)
                sentence_boundary = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_boundary > start + chunk_size // 2:  # Found good sentence boundary
                    end = sentence_boundary + 1
                else:
                    # Try to find word boundary (space)
                    word_boundary = text.rfind(' ', start, end)
                    if word_boundary > start + chunk_size // 2:  # Found good word boundary
                        end = word_boundary
                    # else: just cut at chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - overlap)
        
        return chunks
    
    @staticmethod
    def extract_metadata_from_text(text: str) -> dict:
        """Extract basic metadata from text content"""
        if not text:
            return {}
        
        # Basic statistics
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        # Detect language (simple heuristic)
        english_words = set(['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'])
        words = text.lower().split()
        english_word_count = sum(1 for word in words if word in english_words)
        language = "english" if english_word_count > len(words) * 0.05 else "unknown"
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "language": language
        }
    
    @staticmethod
    def validate_text_quality(text: str) -> dict:
        """Validate text quality and return quality metrics"""
        if not text:
            return {
                "is_valid": False,
                "issues": ["Empty text"],
                "score": 0
            }
        
        issues = []
        
        # Check minimum length
        if len(text) < 50:
            issues.append("Text too short (< 50 characters)")
        
        # Check for meaningful content (ratio of alphanumeric characters)
        alnum_ratio = sum(c.isalnum() or c.isspace() for c in text) / len(text)
        if alnum_ratio < 0.7:
            issues.append("Low content quality (many special characters)")
        
        # Check for repetitive content
        words = text.lower().split()
        if len(set(words)) / len(words) < 0.3:  # Less than 30% unique words
            issues.append("Highly repetitive content")
        
        # Check for common boilerplate
        boilerplate_phrases = [
            "404 not found",
            "page not found",
            "access denied",
            "error 404",
            "this page cannot be found"
        ]
        text_lower = text.lower()
        for phrase in boilerplate_phrases:
            if phrase in text_lower:
                issues.append(f"Contains boilerplate: {phrase}")
                break
        
        # Calculate quality score
        score = max(0, 100 - len(issues) * 20)
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": score,
            "length": len(text),
            "word_count": len(words)
        }
