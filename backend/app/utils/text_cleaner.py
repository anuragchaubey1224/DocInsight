# backend/app/utils/text_cleaner.py

"""
Professional-grade text cleaning utilities for NLP pipelines.
Optimized for summarization, embeddings, and RAG systems.
"""

import re
import unicodedata
from typing import Optional


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters and fix encoding issues.
    
    - Converts smart quotes to regular quotes
    - Normalizes accented characters
    - Removes control characters
    
    Args:
        text: Raw text with potential unicode issues
        
    Returns:
        Normalized text
    """
    # Normalize to NFKD form (compatibility decomposition)
    text = unicodedata.normalize('NFKD', text)
    
    # Remove control characters (except newline and tab)
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
    
    # Fix common unicode issues
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Ellipsis
        '\xa0': ' ',    # Non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def remove_urls(text: str) -> str:
    """
    Remove all URLs from text.
    
    Matches:
    - http://example.com
    - https://example.com
    - www.example.com
    - example.com/path
    
    Args:
        text: Text containing URLs
        
    Returns:
        Text with URLs removed
    """
    # Remove HTTP(S) URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove www URLs
    text = re.sub(r'www\.\S+', '', text)
    
    # Remove naked domains (basic pattern)
    text = re.sub(r'\b[a-zA-Z0-9-]+\.(com|org|net|edu|gov|io|co)\b', '', text)
    
    return text


def remove_html_tags(text: str) -> str:
    """
    Remove HTML/XML tags from text.
    
    Args:
        text: Text containing HTML tags
        
    Returns:
        Text with tags removed
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    return text


def remove_emojis(text: str) -> str:
    """
    Remove all emoji characters from text.
    
    Args:
        text: Text containing emojis
        
    Returns:
        Text with emojis removed
    """
    # Emoji unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_pattern.sub('', text)
    
    return text


def remove_special_chars(text: str) -> str:
    """
    Remove special characters while preserving meaningful punctuation.
    
    Keeps: . , ? ! - ( ) ' "
    Removes: @ # $ % ^ & * _ + = < > ~ | { } [ ]
    
    Args:
        text: Text with special characters
        
    Returns:
        Text with noise characters removed
    """
    # Remove specific special characters, preserve meaningful ones
    text = re.sub(r'[@#$%^&*_+=<>~|{}\[\]\\]', '', text)
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    - Multiple spaces → single space
    - Multiple newlines → single newline
    - Remove tabs
    
    Args:
        text: Text with irregular whitespace
        
    Returns:
        Text with normalized whitespace
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Multiple spaces to single space
    text = re.sub(r' +', ' ', text)
    
    # Multiple newlines to single newline
    text = re.sub(r'\n\s*\n+', '\n', text)
    
    return text


def clean_text(text: str) -> Optional[str]:
    """
    Apply full text cleaning pipeline.
    
    Pipeline order:
    1. Normalize unicode
    2. Remove URLs
    3. Remove HTML tags
    4. Remove emojis
    5. Remove special characters
    6. Normalize whitespace
    7. Convert to lowercase
    8. Strip and remove empty lines
    
    Optimized for:
    - Summarization models (T5/PEGASUS)
    - SentenceTransformer embeddings
    - FAISS retrieval
    - RAG + QA systems
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text ready for NLP processing, or None if empty
    """
    if not text or not text.strip():
        return None
    
    # Apply cleaning pipeline in order
    text = normalize_unicode(text)
    text = remove_urls(text)
    text = remove_html_tags(text)
    text = remove_emojis(text)
    text = remove_special_chars(text)
    text = normalize_whitespace(text)
    
    # Convert to lowercase for consistency
    text = text.lower()
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    # Return None if text is empty after cleaning
    return text if text else None
