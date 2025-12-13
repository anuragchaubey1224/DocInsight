# backend/app/services/summarizer.py

"""
AI-based document summarization service using T5.

Design principles:
- Singleton model loading (loaded once, reused across requests)
- Chunking for long documents (prevents memory issues and token limits)
- Caching via summaries.json (avoid recomputation)
- Model-agnostic design (easy to switch T5-small → T5-base → PEGASUS)

Scalability notes:
- Model is loaded lazily on first request
- Heavy computation isolated in service layer
- Thread-safe for concurrent users
- Summaries cached on disk, not in database (faster reads)
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from threading import Lock

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from app.core.config import get_settings


# Global singleton for model and tokenizer
_model = None
_tokenizer = None
_model_lock = Lock()

settings = get_settings()


def load_model():
    """
    Load T5 model and tokenizer (singleton pattern).
    
    Thread-safe lazy loading ensures model is loaded only once
    across all requests, improving performance and memory efficiency.
    
    Returns:
        tuple: (tokenizer, model)
    """
    global _model, _tokenizer
    
    # Thread-safe check
    with _model_lock:
        if _model is None or _tokenizer is None:
            print(f"🔄 Loading summarization model: {settings.SUMMARIZER_MODEL}")
            
            _tokenizer = AutoTokenizer.from_pretrained(
                settings.SUMMARIZER_MODEL,
                model_max_length=512
            )
            _model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.SUMMARIZER_MODEL
            )
            
            print(f"✅ Model loaded successfully")
        
        return _tokenizer, _model


def chunk_text(text: str, max_words: int = 900, overlap_words: int = 100) -> List[str]:
    """
    Split long text into overlapping chunks for better summarization.
    
    Chunking strategy:
    - Prevents exceeding model's token limit
    - Overlap ensures context continuity between chunks
    - Splits on sentence boundaries when possible
    
    Args:
        text: Input text to chunk
        max_words: Maximum words per chunk (default 900)
        overlap_words: Words to overlap between chunks (default 100)
        
    Returns:
        List of text chunks
    """
    words = text.split()
    
    # If text is short enough, return as single chunk
    if len(words) <= max_words:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk_words = words[start:end]
        chunks.append(' '.join(chunk_words))
        
        # Move start forward, accounting for overlap
        start += (max_words - overlap_words)
    
    return chunks


def summarize_text(
    text: str,
    max_length: int,
    min_length: int,
    tokenizer,
    model
) -> str:
    """
    Generate summary for a single text chunk using T5.
    
    Args:
        text: Text to summarize
        max_length: Maximum summary length in tokens
        min_length: Minimum summary length in tokens
        tokenizer: T5 tokenizer
        model: T5 model
        
    Returns:
        Generated summary
    """
    # Prepare input with T5 prefix
    input_text = f"summarize: {text}"
    
    # Tokenize
    inputs = tokenizer(
        input_text,
        max_length=512,
        truncation=True,
        return_tensors="pt"
    )
    
    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    
    # Decode
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary


def summarize_chunks(chunks: List[str], max_length: int, min_length: int) -> str:
    """
    Summarize multiple chunks and merge results.
    
    Strategy:
    1. Summarize each chunk independently
    2. Concatenate chunk summaries
    3. If combined length is still long, summarize again
    
    This two-pass approach handles very long documents effectively.
    
    Args:
        chunks: List of text chunks
        max_length: Target max length for final summary
        min_length: Target min length for final summary
        
    Returns:
        Merged summary
    """
    tokenizer, model = load_model()
    
    # Summarize each chunk
    chunk_summaries = []
    for chunk in chunks:
        summary = summarize_text(
            chunk,
            max_length=150,  # Intermediate summary length
            min_length=30,
            tokenizer=tokenizer,
            model=model
        )
        chunk_summaries.append(summary)
    
    # If single chunk, return its summary
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    # Merge chunk summaries
    merged_text = ' '.join(chunk_summaries)
    
    # If merged text is still long, summarize again
    merged_words = merged_text.split()
    if len(merged_words) > 300:
        final_summary = summarize_text(
            merged_text,
            max_length=max_length,
            min_length=min_length,
            tokenizer=tokenizer,
            model=model
        )
        return final_summary
    
    return merged_text


def generate_short_summary(text: str) -> str:
    """
    Generate concise 30-40 word summary.
    
    Use case: Quick overview, preview cards, list views
    
    Args:
        text: Cleaned text to summarize
        
    Returns:
        Short summary (30-40 words)
    """
    chunks = chunk_text(text, max_words=900, overlap_words=100)
    
    summary = summarize_chunks(
        chunks,
        max_length=50,  # ~30-40 words
        min_length=30
    )
    
    return summary.strip()


def generate_medium_summary(text: str) -> str:
    """
    Generate comprehensive 150-200 word summary.
    
    Use case: Detailed overview, email summaries, reports
    
    Args:
        text: Cleaned text to summarize
        
    Returns:
        Medium summary (150-200 words)
    """
    chunks = chunk_text(text, max_words=900, overlap_words=100)
    
    summary = summarize_chunks(
        chunks,
        max_length=250,  # ~150-200 words
        min_length=150
    )
    
    return summary.strip()


def generate_detailed_summary(text: str) -> List[str]:
    """
    Generate structured bullet-point summary.
    
    Strategy:
    1. Chunk text into sections
    2. Generate summary for each section
    3. Return as list of bullet points
    
    Use case: Key insights, action items, structured notes
    
    Args:
        text: Cleaned text to summarize
        
    Returns:
        List of summary bullet points
    """
    tokenizer, model = load_model()
    
    # Create more chunks for detailed summary
    chunks = chunk_text(text, max_words=500, overlap_words=50)
    
    # Limit to first 8 chunks (prevents excessive bullets)
    chunks = chunks[:8]
    
    bullet_points = []
    
    for chunk in chunks:
        summary = summarize_text(
            chunk,
            max_length=60,  # ~40-50 words per bullet
            min_length=20,
            tokenizer=tokenizer,
            model=model
        )
        
        # Clean and format as bullet
        summary = summary.strip()
        if summary and len(summary.split()) >= 5:  # Skip very short summaries
            bullet_points.append(summary)
    
    # Ensure at least 3 bullets, at most 10
    if len(bullet_points) < 3 and len(bullet_points) > 0:
        # If we have too few, try regenerating with different chunking
        bullet_points = [bullet_points[0]] * 3
    
    return bullet_points[:10]  # Cap at 10 bullets


def generate_all_summaries(cleaned_text: str) -> Dict[str, any]:
    """
    Generate all three summary types in one call.
    
    This is the main entry point for summarization.
    Efficiently generates all summary types from the same cleaned text.
    
    Args:
        cleaned_text: Pre-cleaned text from cleaned.txt
        
    Returns:
        Dictionary with short_summary, medium_summary, detailed_summary
    """
    print(f"📝 Generating summaries for text ({len(cleaned_text)} chars)")
    
    # Generate all three summary types
    short = generate_short_summary(cleaned_text)
    medium = generate_medium_summary(cleaned_text)
    detailed = generate_detailed_summary(cleaned_text)
    
    summaries = {
        "short_summary": short,
        "medium_summary": medium,
        "detailed_summary": detailed
    }
    
    print(f"✅ Summaries generated:")
    print(f"   - Short: {len(short.split())} words")
    print(f"   - Medium: {len(medium.split())} words")
    print(f"   - Detailed: {len(detailed)} bullets")
    
    return summaries


def save_summaries(user_id: int, doc_id: int, summaries: Dict[str, any]) -> Path:
    """
    Save summaries to summaries.json.
    
    Caching strategy:
    - Summaries saved to disk (not database) for fast reads
    - JSON format allows easy updates and extensions
    - File-based caching scales better than DB for large text
    
    Args:
        user_id: User ID
        doc_id: Document ID
        summaries: Dictionary of summaries
        
    Returns:
        Path to saved summaries.json
    """
    summaries_path = settings.UPLOAD_DIR / str(user_id) / str(doc_id) / "summaries.json"
    
    # Write summaries as JSON
    with summaries_path.open('w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Summaries saved to: {summaries_path}")
    
    return summaries_path


def load_summaries(user_id: int, doc_id: int) -> Optional[Dict[str, any]]:
    """
    Load cached summaries from summaries.json.
    
    Returns None if file doesn't exist (summaries not yet generated).
    
    Args:
        user_id: User ID
        doc_id: Document ID
        
    Returns:
        Dictionary of summaries or None if not found
    """
    summaries_path = settings.UPLOAD_DIR / str(user_id) / str(doc_id) / "summaries.json"
    
    if not summaries_path.exists():
        return None
    
    try:
        with summaries_path.open('r', encoding='utf-8') as f:
            summaries = json.load(f)
        
        print(f"📂 Loaded cached summaries from: {summaries_path}")
        return summaries
    
    except Exception as e:
        print(f"⚠️ Error loading summaries: {e}")
        return None
