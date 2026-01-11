# Model Serving Architecture Exploration

## Goal
Learn vLLM, Triton, and Ray for production model serving. Build scalable inference infrastructure for Docling.

---

## 1. Triton Server (for CV Models)

### Local Deployment
- [ ] Run Triton container with GPU support
- [ ] Create model repository structure
- [ ] Write `config.pbtxt` for RT-DETR layout model
- [ ] Write `config.pbtxt` for TableFormer
- [ ] Test inference via HTTP API

**Output**: Working Triton server serving Docling CV models

### Performance Optimization
- [ ] Enable dynamic batching (test batch sizes: 1, 4, 8)
- [ ] Convert ONNX to TensorRT and benchmark
- [ ] Test concurrent requests and measure throughput
- [ ] Monitor GPU utilization

**Output**: Optimal Triton configuration and performance numbers

---

## 2. vLLM Server (for VLM Models)

### Local Deployment  
- [ ] Run vLLM with Granite-Docling-258M
- [ ] Test OpenAI-compatible API endpoint
- [ ] Send document page for inference
- [ ] Verify output quality

**Output**: Working vLLM server for VLM inference

### Performance Testing
- [ ] Measure single request latency
- [ ] Test concurrent requests (2, 4, 8, 16)
- [ ] Monitor continuous batching behavior
- [ ] Check GPU memory usage and KV cache

**Output**: vLLM throughput/latency benchmarks

---

## 3. Worker Integration

### Build HTTP Clients
- [ ] Create Triton client in ARQ worker
- [ ] Create vLLM client in ARQ worker
- [ ] Implement retry logic with backoff
- [ ] Add comprehensive error handling

**Output**: Workers can call both inference servers

### End-to-End Pipeline
- [ ] Extract PDF pages in worker
- [ ] Call Triton for layout detection
- [ ] Call Triton for table extraction  
- [ ] Call vLLM for document understanding (optional)
- [ ] Assemble final DoclingDocument

**Output**: Complete document processing workflow

---

## 4. Kubernetes Deployment

### Deploy Inference Servers
- [ ] Create Triton Deployment + Service
- [ ] Create vLLM Deployment + Service
- [ ] Configure GPU resource limits
- [ ] Mount model repositories (PVC/ConfigMap)
- [ ] Test in-cluster connectivity from workers

**Output**: Both servers running in K8s

### Autoscaling Setup
- [ ] Configure KEDA for ARQ workers (Redis queue depth)
- [ ] Test scaling behavior under load
- [ ] Set resource requests/limits for all pods

**Output**: Auto-scaling document processing pipeline

---

## 5. Advanced: Ray Integration (Optional)

### Explore Ray Serve
- [ ] Deploy models via Ray Serve
- [ ] Compare Ray vs standalone Triton/vLLM
- [ ] Test Ray's autoscaling
- [ ] Evaluate for complex multi-model pipelines

**Output**: Understanding of when to use Ray vs Triton/vLLM

---

## 6. Production Readiness

### Monitoring & Observability
- [ ] Add Prometheus metrics (latency, throughput)
- [ ] Track GPU utilization per model
- [ ] Monitor queue depth and processing time
- [ ] Set up alerts for failures

**Output**: Production monitoring dashboard

### Cost Analysis
- [ ] Calculate GPU hours per document
- [ ] Compare GPU vs CPU costs
- [ ] Identify optimization opportunities

**Output**: Cost model and optimization strategy

---

## Success Criteria

✅ Triton serving RT-DETR + TableFormer with dynamic batching  
✅ vLLM serving Granite-Docling-258M with continuous batching  
✅ ARQ workers calling both servers successfully  
✅ Full system deployed in Kubernetes with autoscaling  
✅ Performance benchmarks and cost analysis complete

---

## Learning Priorities

**Week 1**: Triton + vLLM local deployment (items 1-2)  
**Week 2**: Worker integration (item 3)  
**Week 3**: K8s deployment (item 4)  
**Week 4**: Production hardening + monitoring (item 6)
