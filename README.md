# DocInsight

**AI-Powered Document Intelligence Backend**

A production-grade backend system for intelligent document processing, summarization, and question answering. Built with FastAPI, FLAN-T5-base, and FAISS for efficient retrieval-augmented generation (RAG).

---

## Project Overview

DocInsight solves the problem of information overload in technical documents, research papers, and lecture notes. Instead of manually reading lengthy PDFs, users can:

- Extract clean, structured summaries at multiple levels of detail
- Ask natural language questions and get answers grounded in document content
- Automatically fall back to web search when document context is insufficient

**Target Users:**
- Students reviewing lecture slides and course materials
- Researchers analyzing technical papers
- Professionals extracting insights from reports and documentation

---

## Key Features

- **Multi-Level Summarization**: Hierarchical summaries (short, medium, detailed) generated using chunk-wise approach to prevent repetition
- **RAG-Based Question Answering**: Ask questions about uploaded documents with context-aware answers powered by FLAN-T5-base
- **Intelligent Web Fallback**: Automatically searches the web when document confidence is low, with graceful degradation on failures
- **Sentence-Aware Chunking**: Preserves semantic boundaries during text segmentation for better retrieval quality
- **Metadata Noise Removal**: Automatically filters repeated headers, dates, instructor names, and slide numbers from lecture PDFs
- **FAISS Vector Search**: Efficient similarity search using exact cosine similarity (IndexFlatIP)
- **CPU-Only Inference**: No GPU required, runs efficiently on standard hardware
- **Production-Ready Design**: Thread-safe singleton models, comprehensive error handling, and structured logging

---

## High-Level Architecture

DocInsight follows a pipeline architecture where each stage processes and enriches document data:

**Data Flow:**
```
PDF Upload → Text Extraction → Cleaning → Chunking → Dual Path Processing
                                                      ↓
                                    ┌─────────────────┴─────────────────┐
                                    ↓                                   ↓
                            Summarization                         Embeddings
                            (FLAN-T5-base)                   (SentenceTransformer)
                                    ↓                                   ↓
                        Short/Medium/Detailed                    FAISS Index
                            Summaries                          (Vector Storage)
                                                                        ↓
                                                              Question Answering
                                                            (Retrieval + Generation)
                                                                        ↓
                                                            Confidence Evaluation
                                                                        ↓
                                                        ┌───────────────┴──────────────┐
                                                        ↓                              ↓
                                                Document Answer                  Web Fallback
                                                (High Confidence)              (Low Confidence)
```

**Core Components:**
- **Text Cleaner**: Removes noise (URLs, metadata, repeated lines) while preserving content
- **Sentence Chunker**: Splits text at sentence boundaries with configurable overlap
- **Summarization Service**: Generates hierarchical summaries using chunk-wise approach
- **Embedding Service**: Creates 768-dimensional vectors using all-mpnet-base-v2
- **FAISS Retriever**: Performs fast similarity search for relevant document chunks
- **QA Service**: Generates answers using T5 with confidence scoring
- **Web Search Service**: Fetches and merges web results via DuckDuckGo when needed

---

## Backend Pipeline (Step-by-Step)

### 1. Document Ingestion
- User uploads PDF or text file via `/upload` endpoint
- File stored with unique user_id and doc_id structure
- Raw text extracted using PyMuPDF (for PDFs) or direct read (for text files)

### 2. Text Cleaning
- Unicode normalization and encoding fixes
- URL, HTML tag, and emoji removal
- **Metadata noise removal**:
  - Repeated instructor names and course codes (frequency-based filtering)
  - Date patterns (e.g., "25 september 2023")
  - Slide numbers (e.g., "ethernet 88")
  - Headers/footers repeated across pages
- Whitespace normalization
- Lowercase conversion for consistency

### 3. Sentence-Aware Chunking
- Text split into chunks at sentence boundaries
- **Configuration**:
  - Max chunk size: 800 characters
  - Overlap: 100 characters (preserves context across chunks)
- Prevents splitting mid-sentence, improving embedding quality
- Stores chunks in `chunks.txt` for retrieval

### 4. Chunk-Wise Summarization
**Why Chunk-Wise?**  
Traditional full-document summarization causes repetition when the same context is summarized multiple times. Chunk-wise summarization solves this by summarizing each chunk once, then hierarchically combining results.

**Process:**
1. **Chunk Summaries**: Each chunk summarized into 2-4 sentences independently
2. **Detailed Summary**: Direct use of chunk summaries (each chunk = one paragraph)
3. **Medium Summary**: Compressed merge of chunk summaries
4. **Short Summary**: Abstract of medium summary (2-3 sentences)

**Why Detailed Summary is Primary:**  
The detailed summary preserves granular information from each section without artificial compression, making it ideal for technical documents where completeness matters.

**Output**: Saved to `summaries.json` for instant retrieval

### 5. Embeddings + FAISS Indexing
- Each chunk converted to 768-dimensional vector using SentenceTransformer
- Vectors stored in FAISS IndexFlatIP (exact cosine similarity)
- Index saved to disk (`faiss_index.bin`) for efficient loading
- Enables sub-100ms retrieval for typical documents

### 6. Question Answering (RAG)
**Query Flow:**
1. User question embedded using same SentenceTransformer model
2. FAISS retrieves top-k most similar chunks (k=5)
3. Confidence computed as average of top-3 similarity scores
4. **Decision logic**:
   - If `confidence >= 0.70 OR confidence >= 0.40`: Use document context
   - If `confidence < 0.40`: Trigger web fallback

**Why Two-Tier Confidence?**  
After upgrading to FLAN-T5-base, confidence scores improved. The 0.40 guardrail prevents false web fallbacks for borderline document-answerable questions, while still allowing true external queries through.

**Answer Generation:**
- FLAN-T5-base with specialized prompt: `"question: <Q> context: <C> answer:"`
- Parameters: `max_new_tokens=120`, `min_new_tokens=40`, `temperature=0.7`, `do_sample=False`
- Deterministic, multi-line answers suitable for technical content

### 7. Web Fallback with Graceful Degradation
**When Triggered:**  
Confidence < 0.40 (indicates question unrelated to document)

**Search Strategy:**
- Uses DuckDuckGo search API
- Retrieves top 5 results
- Merges snippets into unified context
- Generates answer from web context using same T5 model

**Graceful Degradation:**  
If web search fails (rate limit, network error):
- Returns honest message: *"I could not find a confident answer in the document, and web search is temporarily unavailable."*
- Sets `source="none"`, `used_web=false`
- **Never crashes** - API remains stable

---

## Design Decisions

### Why Chunk-Wise Summarization?
**Problem**: Traditional approach summarizes the full document multiple times for different summary lengths, causing repetition.  
**Solution**: Each chunk is summarized once. Long summary uses chunk summaries directly. Medium and short summaries are hierarchical compressions.  
**Result**: No repetition, faster generation, clearer hierarchical differences.

### Why Detailed Summary is Primary?
**Rationale**: Technical documents require completeness. The detailed summary preserves all key points from each section without artificial compression, making it the most useful output for students and researchers.

### Why Confidence-Based Fallback?
**Problem**: RAG systems fail silently when asked unrelated questions.  
**Solution**: Compute confidence from retrieval scores. Low confidence triggers web search, high confidence uses document.  
**Benefit**: System gracefully handles both document-specific and general knowledge questions.

### Why CPU-Only Models?
**Decision**: Use FLAN-T5-base (248M params) instead of larger models requiring GPU.  
**Rationale**: Deployment simplicity, cost efficiency, and accessibility. Performance is sufficient for document Q&A and summarization tasks.

### Why Metadata Removal?
**Problem**: Lecture slides contain repeated instructor names, dates, and slide numbers that pollute summaries.  
**Solution**: Frequency-based line filtering removes metadata while preserving content.  
**Implementation**: Lines repeated >3 times AND ≤6 words are classified as metadata and removed.

---

## API Overview

### Document Management
- `POST /upload` - Upload PDF or text file, returns doc_id
- `GET /document/{doc_id}` - Retrieve document metadata
- `DELETE /document/{doc_id}` - Delete document and all associated data

### Processing
- `POST /summarize/{doc_id}` - Generate all summaries (short, medium, detailed)
- `GET /summaries/{doc_id}` - Retrieve cached summaries

### Search & Retrieval
- `POST /index/{doc_id}` - Create FAISS embeddings and index
- `POST /ask/{doc_id}` - Ask questions about document with RAG

### Response Schema (Q&A)
```json
{
  "answer": "Generated answer text",
  "source": "document | web | none",
  "confidence": 0.85,
  "used_web": false,
  "retrieved_chunks": 5,
  "web_results": null
}
```

---

## Tech Stack

**Framework & API:**
- FastAPI (async Python web framework)
- SQLAlchemy 2.0 (ORM for document metadata)
- Pydantic (data validation)

**ML Models:**
- FLAN-T5-base (summarization and Q&A generation)
- SentenceTransformers (all-mpnet-base-v2 for embeddings)

**Vector Search:**
- FAISS (IndexFlatIP for exact cosine similarity)

**Text Processing:**
- PyMuPDF (PDF text extraction)
- NLTK (sentence tokenization)

**Web Search:**
- duckduckgo-search (fallback search API)

**Infrastructure:**
- Python 3.12
- CPU-only inference (no GPU required)
- Thread-safe singleton pattern for model loading

---

## Current Status

**Completed:**
- Full backend pipeline (upload → summarize → index → Q&A)
- Chunk-wise summarization with hierarchical compression
- RAG with confidence-based web fallback
- Metadata noise removal for lecture PDFs
- Production-grade error handling and logging
- Comprehensive test coverage for core pipeline

**In Progress:**
- Frontend development (planned)
- Cloud deployment (planned)

**Not Yet Implemented:**
- User authentication (JWT ready, not enforced)
- Multi-document cross-referencing
- Advanced web search APIs (Google, Bing)

---

## Limitations

1. **Web Search Rate Limits**: DuckDuckGo may rate-limit requests. System degrades gracefully but cannot guarantee web search availability.

2. **Best Suited for Technical PDFs**: Optimized for structured documents (lectures, papers, reports). May underperform on highly visual content or scanned images.

3. **CPU-Only Performance**: FLAN-T5-base runs on CPU, which is slower than GPU inference. Typical generation time: 2-5 seconds per summary.

4. **English Language Only**: Models trained primarily on English text. Limited support for other languages.

5. **Context Window Limits**: T5 has 512-token input limit. Very long questions or contexts are truncated.

---

## Future Improvements

**Short Term:**
- Frontend web interface for document upload and interaction
- Docker containerization for easier deployment
- Redis caching for frequently asked questions

**Medium Term:**
- Deploy to cloud platform (AWS/GCP/Azure)
- Add user authentication and multi-tenancy
- Integrate better web search APIs (Google Custom Search, Bing)

**Long Term:**
- Support for more file formats (Word, Excel, PowerPoint)
- Multi-document knowledge graph
- Fine-tuned models for domain-specific documents
- GPU acceleration option for faster inference

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- 4GB+ RAM (for model loading)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd DocInsight

# Create virtual environment
python -m venv .venv_doc
source .venv_doc/bin/activate  # On Windows: .venv_doc\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

### Running the Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Project Structure

```
DocInsight/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and settings
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic (summarization, QA, embeddings)
│   │   ├── utils/         # Text processing utilities
│   │   └── main.py        # FastAPI application entry point
│   ├── data/
│   │   ├── uploads/       # User-uploaded documents
│   │   └── index/         # FAISS indices and embeddings
│   └── test_step7_pipeline.py  # Integration tests
├── requirements.txt
└── README.md
```

---

## License

MIT License (to be added)

---

## Contact

For questions or collaboration opportunities, please reach out via GitHub issues or email.
