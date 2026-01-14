# Docling Models Exploration

## Goal
Understand what models Docling uses, their performance characteristics, and which ones are needed for your use case.

---

## 1. Local Testing & Profiling

### Test Docling Behavior
- [done] Install Docling and run basic conversion
- [done] Test with digital PDF (has embedded text)
- [] Test with scanned PDF (needs OCR)
- [done] Check logs to see which models actually load

**Output**: Know which models trigger for different document types

### Explore Each OCR Technique/Model 
- [ ] Test Tesseract (An Image Processing Technique)
- [ ] Test EasyOCR 
- [ ] Test RapidOCR 
- [ ] Test RT-DETR (layout)
- [ ] Test TableFormer
- [ ] Test PaddleOCR (A E2E Document extraction pipeline)
- [ ] Test with/without GPU acceleration

**Output**: Identify the bottleneck model(s)

---

## 2. Model Extraction & Format Conversion

### Export Models for Deployment
- [ ] Find cached models in `~/.cache/huggingface`
- [ ] Export RT-DETR to ONNX format
- [ ] Export TableFormer to ONNX format
- [ ] Test ONNX models match PyTorch output

**Output**: ONNX files ready for Triton deployment

---

## 3. VLM Alternative Testing

### Compare Traditional vs VLM Pipeline
- [ ] Test Granite-Docling-258M with vLLM/Transformers
- [ ] Process same document with both pipelines:
  - Traditional: RT-DETR + TableFormer + OCR
  - VLM-only: Granite-Docling-258M
- [ ] Compare accuracy and speed

**Output**: Decision on whether to use VLM or traditional pipeline

---

## 4. Configuration Optimization

### Determine Minimal Model Set
- [ ] Test with OCR disabled (digital PDFs only)
- [ ] Test with table structure disabled
- [ ] Test with picture classification enabled/disabled
- [ ] Document which models are essential vs optional

**Output**: Optimal pipeline configuration for your documents

---

## Success Criteria

✅ Know exactly which models you need  
✅ Have performance benchmarks (CPU vs GPU)  
✅ Have ONNX-exported models ready  
✅ Understand VLM vs traditional tradeoffs
