# App Development Plan

## Phase 1: Core Setup
- [ ] Complete the Docling exploration
- [ ] Setup app dependencies (async-first architecture)

## Phase 2: API Endpoints
Build 4 main endpoints:

1. **Health Check**
   - [ ] Basic health/status endpoint

2. **Document Upload & Processing**
   - [ ] File upload handler
   - [ ] Document processing integration

3. **Chat with Document (SSE)**
   - [ ] SSE endpoint setup
   - [ ] AsyncIO background tasks for streaming responses

4. **Fetch Processed Chunks** _(optional)_
   - [ ] Retrieve processed document chunks

## Phase 3: Model Integration
- [ ] Model inference experiment

---

## Alternative Document Processing Backends
Explore once done with Docling:

- **DeepSeekOCR Pipeline**
- **Mistral-OCR API Service** (not available in model form like DeepSeek)
- **Landing AI Agentic Document Extraction**

