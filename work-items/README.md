# Document Processing Learning Roadmap

## Goal
Master document processing pipeline and downstream RAG process through hands-on learning modules.

## Learning Philosophy
- **Incremental:** Build knowledge step-by-step, starting with fundamentals
- **Practical:** Every work item produces working code and insights
- **Observable:** Use Langfuse to understand what's happening under the hood
- **Focused:** Concise tasks with clear "what" and "why"

---

## Module 1: Document Processing Fundamentals 🔍

**Goal:** Master OCR engines, layout analysis, and document parsing techniques.

### [Work Item 1.1: OCR Agent Evaluator](./1.1-ocr-agent-evaluator.md) ⏳
**Status:** In Progress  
**Time:** 6-8 hours  
Build LangGraph agent to systematically compare OCR engines (Tesseract, EasyOCR, PaddleOCR, RapidOCR) using LLM-based quality assessment.

### [Work Item 1.2: Docling Pipeline Deep Dive](./1.2-docling-deep-dive.md) 📋
**Status:** Planned  
**Time:** 3-4 hours  
Explore Docling's RT-DETR layout detection + TableFormer extraction pipeline.

### [Work Item 1.3: Digital vs Scanned PDF Handling](./1.3-pdf-handling-strategies.md) 📋
**Status:** Planned  
**Time:** 2 hours  
Compare processing strategies for digital vs scanned PDFs and create decision tree.

---

## Module 2: RAG Pipeline Construction 🔗

**Goal:** Master chunking strategies, embeddings, vector stores, and modern retrieval techniques.

### Work Item 2.1: Chunking Strategy Experiments 📋
**Status:** Planned  
**Time:** 3-4 hours  
**Prerequisites:** Module 1 complete

### Work Item 2.2: Embedding Model Evaluation 📋
**Status:** Planned  
**Time:** 2-3 hours

### Work Item 2.3: Vector Store Setup 📋
**Status:** Planned  
**Time:** 3-4 hours

### Work Item 2.4: Advanced Retrieval Techniques 📋
**Status:** Planned  
**Time:** 4-5 hours  
**Prerequisites:** 2.1-2.3 complete

---

## Module 3: Observability & Monitoring 📊

**Goal:** Practice debugging and optimizing pipelines with Langfuse tracing.

### Work Item 3.1: Langfuse Integration - Document Processing 📋
**Status:** Planned  
**Time:** 2-3 hours  
**Prerequisites:** Module 1 complete

### Work Item 3.2: Langfuse Integration - RAG Pipeline 📋
**Status:** Planned  
**Time:** 2-3 hours  
**Prerequisites:** Module 2 complete

### Work Item 3.3: Custom Metrics & Dashboards 📋
**Status:** Planned  
**Time:** 2 hours

---

## Module 4: API Integration (Optional) 🚀

**Goal:** Learn async processing patterns for production-ready systems.

### Work Item 4.1: FastAPI Document Upload Endpoint 📋
**Status:** Optional  
**Time:** 3-4 hours

### Work Item 4.2: FastAPI RAG Chat Endpoint (SSE) 📋
**Status:** Optional  
**Time:** 3-4 hours

---

## Current Progress

- ✅ Environment setup (FastAPI, Docling, OCR tools, Langfuse)
- ✅ Initial OCR experiments in `experiments/tesseract_ocr.ipynb`
- ⏳ **Active:** Work Item 1.1 - OCR Agent Evaluator
- 📋 **Next:** Work Item 1.2 - Docling Deep Dive

---

## Legend
- ✅ Complete
- ⏳ In Progress
- 📋 Planned
- ⏸️ Blocked
- ❌ Skipped
