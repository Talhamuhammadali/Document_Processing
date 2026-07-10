# App Development Plan

## Phase 1: Core Setup
- [ ] Complete the Docling exploration
- [done] Setup app dependencies (async-first architecture)

## Phase 2: API Endpoints
Build 4 main endpoints:

1. **Health Check**
   - [done] Basic health/status endpoint

2. **Document Upload & Processing** _(mock backend)_
   - [done] File upload handler (matches upload to a precomputed Docling mock)
   - [done] Normalization pipeline: docling -> flat top-left chunks, embed, picture images, describe (stubs)
   - [ ] Real processing pipeline (OCR/extraction) — deferred

3. **Chat with Document (SSE)**
   - [ ] SSE endpoint setup
   - [ ] AsyncIO background tasks for streaming responses

4. **Fetch Processed Chunks**
   - [done] GET /documents, /documents/{id}, /documents/{id}/chunks
   - [done] GET /documents/{id}/file (original PDF), /documents/{id}/chunks/{chunk_id}/image
   - [done] POST /documents/search (RAG KNN vector search over chunks)

Storage: Redis Stack (RedisJSON docs + image blobs + RediSearch vector index); Mongo left as placeholder.
See spec: docs/superpowers/specs/2026-07-09-document-viewer-backend-design.md

## Phase 3: Model Integration
- [ ] Model inference experiment

---

## Alternative Document Processing Backends
Explore once done with Docling:

- **DeepSeekOCR Pipeline**
- **Mistral-OCR API Service** (not available in model form like DeepSeek)
- **Landing AI Agentic Document Extraction**

