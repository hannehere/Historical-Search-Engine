# 🔬 Three-Stage Retrieval Engine - Hướng Dẫn Chi Tiết

## 📚 **Paper Gốc**
**"Text Retrieval with Multi-Stage Re-Ranking Models"**  
*Yuichi Sasazawa, Kenichi Yokote, Osamu Imaichi, Yasuhiro Sogawa*  
*Hitachi, Ltd. Research and Development Group*  
*arXiv:2311.07994v1 [cs.IR] 14 Nov 2023*

## 🎯 Tổng Quan

**Three-Stage Retrieval** là một kiến trúc tìm kiếm tiên tiến được implement theo paper học thuật từ Hitachi, chia quá trình retrieval thành 3 giai đoạn tuần tự để tối ưu hóa cả tốc độ và độ chính xác.

### 📊 **Quy Trình 3 Giai Đoạn (Theo Paper Hitachi):**

```
📄 Corpus (a₀ documents - toàn bộ corpus)
         ↓
🔍 Stage 1: BM25 Retrieval → a₁ candidates (thường 100-1000)
         ↓
🧠 Stage 2: Language Model → a₂ candidates (thường 10-50)  
         ↓
🎯 Stage 3: High-Performance Model → final results (top 10-20)
```

**Mục Tiêu Paper:** Cải thiện độ chính xác tìm kiếm while minimizing search delay bằng cách chỉ áp dụng expensive models cho limited number of highly relevant documents.

## 🏗️ Kiến Trúc Chi Tiết (Theo Paper Hitachi)

### **🔍 Stage 1: BM25 Retrieval**
```python
Purpose: Fast vocabulary-based search (low accuracy, high speed)
Input: a₀ documents (toàn bộ corpus)
Algorithm: BM25 (Robertson et al., 1995) 
Output: a₁ documents (thường 100-1000)
Speed: ~0.0178s/query (fastest)
Strength: Fast filtering, good cho exact keyword matches
```

**Paper Implementation:**
- Sử dụng Pyserini toolkit để tính BM25 similarity
- BM25 calculates similarity cho ALL documents trong corpus
- Ranks documents theo similarity order
- Output: top a₁ documents with highest similarity

### **🧠 Stage 2: Language Model (Cross-Encoder)**  
```python
Purpose: Medium accuracy, medium speed re-ranking
Input: a₁ candidates từ Stage 1 (100-1000 docs)
Algorithm: Cross-encoder Language Model (MiniLM)
Model: MiniLM (30M parameters, 6 layers, 384 hidden size)
Output: a₂ documents (thường 10-50)
Speed: ~0.1939s/query (moderate)
Strength: Better understanding của query-document relationships
```

**Paper Implementation:**
- Cross-encoder nhận concatenation của query và document
- Model outputs hidden state of [CLS] token → classification layer
- Training: binary classification với cross-entropy loss
- Inference: scalar value từ classification layer = similarity score
- Re-ranks chỉ top a₁ documents (không phải toàn bộ corpus)

### **🎯 Stage 3: High-Performance Model**
```python
Purpose: Highest accuracy, lowest speed (chỉ cho top candidates)
Input: a₂ candidates từ Stage 2 (10-50 docs)
Algorithm: Model Ensemble HOẶC Larger Model HOẶC Pairwise Model
Output: Final ranked results (top 10-20)
Speed: Varies by method (1.39x - 4.00x slower than Stage 2)
Strength: Maximum precision cho final ranking
```

**Paper Methods:**

#### **🎯 Model Ensemble (Paper's Best Method)**
```python
- Multiple MiniLM models (same architecture, different random seeds)
- Average similarity scores across ensemble members
- 3 models in ensemble (paper experiment)
- Performance: NDCG@10 = 0.5922 (out-of-domain average)
- Speed: 1.50x slower than BM25+LM
```

#### **🎯 Larger Model (Paper's Highest Accuracy)**
```python
- Larger MiniLM: 81M parameters, 6 layers, 768 hidden size
- Same architecture as Stage 2 nhưng more parameters
- Performance: NDCG@10 = 0.6176 (out-of-domain average)
- Speed: 1.39x slower than BM25+LM
```

#### **🎯 Pairwise Model (Existing Method - Paper Comparison)**
```python
- Takes query + 2 documents, predicts which is more relevant
- Requires a₂×(a₂-1) inferences (quadratic complexity!)
- Example: top 10 docs require 10×9 = 90 inferences
- Problems: Very slow, poor zero-shot performance, token length limits
- Performance: Poor on out-of-domain (0.5105 average)
- Speed: 4.00x slower than BM25+LM
```

## 🚀 Cách Sử Dụng

### **1️⃣ Basic Usage**
```python
from ThreeStageRetrieval import ThreeStageRetrieval

# Initialize với config balanced
retriever = ThreeStageRetrieval(
    use_bm25=True,
    use_dense_retrieval=True, 
    use_reranking=True,
    stage1_top_k=100,
    stage2_top_k=50,
    stage3_top_k=20
)

# Index chunks
retriever.index_chunks(chunks, tokenized_chunks, chunk_to_doc_map)

# Search với detailed results
results = retriever.retrieve_three_stage(
    query="Bà Triệu sinh năm nao",
    query_tokens=['bà', 'triệu', 'sinh', 'năm', 'nao'],
    final_top_k=10,
    return_stage_details=True
)

# In kết quả
print("🔍 Pipeline Summary:")
print(f"Initial: {results['pipeline_summary']['initial_candidates']} chunks")
print(f"Stage 1: {results['pipeline_summary']['after_stage1']} candidates")  
print(f"Stage 2: {results['pipeline_summary']['after_stage2']} candidates")
print(f"Final: {results['pipeline_summary']['final_results']} results")
```

### **2️⃣ Paper-based Configurations**
```python
from ThreeStageRetrieval import create_three_stage_config

# Paper's best method: BM25 + LM + Large Model
best_config = create_three_stage_config('accurate')
retriever_best = ThreeStageRetrieval(
    use_bm25=True,
    use_dense_retrieval=True,  # This acts as Language Model stage
    use_reranking=True,        # Large model reranking
    stage1_top_k=100,          # a₁ = 100 (paper setting)
    stage2_top_k=20,           # a₂ = 20 (paper setting)
    stage3_top_k=10,           # Final top-10 results
    embedding_model='keepitreal/vietnamese-sbert',  # Stage 2
    reranker_model='keepitreal/vietnamese-reranker'  # Stage 3
)

# Paper's stable method: BM25 + LM + Ensemble  
ensemble_config = ThreeStageRetrieval(
    use_bm25=True,
    use_dense_retrieval=True,
    use_reranking=True,
    stage1_top_k=100,
    stage2_top_k=20, 
    stage3_top_k=10,
    # Ensemble of 3 models (paper approach)
    ensemble_size=3
)

# Baseline comparison: BM25 + LM only
baseline_config = ThreeStageRetrieval(
    use_bm25=True,
    use_dense_retrieval=True,
    use_reranking=False,  # Skip Stage 3
    stage1_top_k=100,
    stage2_top_k=10      # Direct to final results
)
```

### **3️⃣ Chạy Demo Script**
```bash
# Nếu có demo script cho Three-Stage
python demo_three_stage.py

# Hoặc tích hợp vào enhanced search engine
python EnhancedSearchEngine.py
# → Chọn mode "three_stage" trong interactive interface
```

## 📊 Performance Results (Paper Experimental Data)

### **🎯 Datasets Used:**
- **Training:** MS-MARCO (502,939 queries, 8.8M documents)
- **Testing:** Zero-shot evaluation on BEIR datasets:
  - FiQA-2018, SciFact, HotpotQA
  - Evaluation metric: NDCG@10

### **📈 Paper Results (NDCG@10 Scores):**

| Method | In-domain | Out-of-domain | Speed | Delay vs |
|--------|-----------|---------------|-------|----------|
|  | MS-MARCO | Average | (sec/query) | BM25+LM |
| **BM25** | 0.2294 | 0.5434 | 0.0178 | 0.01x |
| **BM25 + LM** | 0.3714 | 0.5761 | 0.1939 | 1.00x |
| **BM25 + LM + Pairwise** | 0.3889 | 0.5105 | 0.7759 | 4.00x |
| **BM25 + LM + Ensemble** | 0.3761 | 0.5922 | 0.2910 | 1.50x |
| **BM25 + LM + Large** | 0.3845 | 0.6176 | 0.2693 | 1.39x |

### **🏆 Key Insights từ Paper:**

#### **✅ Best Method: BM25 + LM + Large Model**
```python
- Highest out-of-domain accuracy: 0.6176 NDCG@10
- Only 1.39x slower than BM25+LM baseline
- Best trade-off between accuracy và speed
- Consistently good across all test datasets
```

#### **⭐ Good Alternative: BM25 + LM + Ensemble**
```python
- Stable performance: 0.5922 NDCG@10 
- Exceeds BM25+LM on ALL datasets
- 1.50x slower than baseline (reasonable)
- More robust than pairwise approach
```

#### **❌ Poor Performer: Pairwise Model**
```python
- Good in-domain (0.3889) but poor out-of-domain (0.5105)
- 4.00x slower than baseline (too expensive!)
- Problems: token length limits, quadratic complexity
- Poor zero-shot generalization
```

### **📊 Speed vs Accuracy Trade-off:**
```python
🔍 BM25 Only:
- Speed: ⚡⚡⚡ Fastest (0.0178s)
- Accuracy: 📊 Basic (0.5434)
- Use: Initial filtering, very fast searches

🧠 BM25 + Language Model:
- Speed: ⭐⭐ Fast (0.1939s) 
- Accuracy: 📈 Good (0.5761)
- Use: Standard production baseline

🎯 BM25 + LM + Large Model:
- Speed: ⭐ Moderate (0.2693s)
- Accuracy: 🏆 Best (0.6176)
- Use: High-quality search, research applications

🐌 BM25 + LM + Pairwise:
- Speed: ❌ Slow (0.7759s)
- Accuracy: 📉 Poor out-of-domain (0.5105)
- Use: Không khuyến nghị (existing method comparison)
```

## 🔧 Configuration Options

### **🎛️ Stage Configuration:**
```python
retriever = ThreeStageRetrieval(
    # Stage 1: BM25 settings
    use_bm25=True,
    stage1_top_k=100,           # Candidates sau BM25
    
    # Stage 2: Dense retrieval settings  
    embedding_model='keepitreal/vietnamese-sbert',
    use_dense_retrieval=True,
    stage2_top_k=50,            # Candidates sau Dense
    
    # Stage 3: Reranking settings
    reranker_model='keepitreal/vietnamese-reranker',
    use_reranking=True,
    stage3_top_k=20,            # Final results
    
    # Weight fusion
    bm25_weight=0.3,
    dense_weight=0.4,
    rerank_weight=0.3
)
```

### **⚖️ Weight Tuning:**
```python
# Keyword-focused (tốt cho exact matches)
weights = {'bm25_weight': 0.6, 'dense_weight': 0.3, 'rerank_weight': 0.1}

# Semantic-focused (tốt cho conceptual queries)  
weights = {'bm25_weight': 0.2, 'dense_weight': 0.5, 'rerank_weight': 0.3}

# Precision-focused (tốt cho research)
weights = {'bm25_weight': 0.2, 'dense_weight': 0.3, 'rerank_weight': 0.5}
```

## 📋 Expected Output

### **🔍 Stage Details Output:**
```python
🔍 SEARCH RESULTS WITH STAGE BREAKDOWN:
========================================
Query: "Bà Triệu sinh năm nao"

Pipeline Summary:
- Initial candidates: 5,968 chunks
- After Stage 1 (BM25): 100 candidates  
- After Stage 2 (Dense): 50 candidates
- Final results: 10 results

Stage 1 (BM25 Keyword):
- Method: BM25 keyword matching
- Candidates: 100
- Top scores: [8.42, 7.89, 7.23, 6.78, 6.45]
- Time: 0.05s

Stage 2 (Dense Semantic):  
- Method: Dense embedding similarity
- Candidates: 50
- Top scores: [0.89, 0.87, 0.84, 0.82, 0.79]
- Time: 0.20s

Stage 3 (LLM Reranking):
- Method: Cross-encoder reranking  
- Candidates: 10
- Top scores: [0.95, 0.91, 0.87, 0.83, 0.78]
- Time: 1.10s

Final Results:
[1] Bà Triệu.md (Score: 0.95) ⭐⭐⭐
    Content: # Bà Triệu Bà Triệu (chữ Hán: 趙婆, còn gọi là Triệu Trinh Nương...
    
[2] Triệu Thị Trinh.md (Score: 0.91) ⭐⭐⭐
    Content: ## Tiểu sử Triệu Thị Trinh sinh năm 225, mất năm 248...
```

## 💡 Best Practices

### **🎯 Khi Nào Dùng Three-Stage:**
```python
✅ Excellent for:
- Research queries cần độ chính xác cao
- Complex semantic queries: "bối cảnh lịch sử khởi nghĩa"  
- Multi-aspect queries: "ảnh hưởng kinh tế chiến tranh"
- When precision > speed requirements

⚠️ Consider alternatives for:
- Simple keyword queries: "Hồ Chí Minh"
- Real-time applications cần < 0.1s response  
- Large-scale concurrent queries (resource intensive)
- When BM25-only results are sufficient
```

### **⚡ Performance Optimization:**
```python
# 1. Adjust stage sizes based on corpus
small_corpus = {'stage1_top_k': 50, 'stage2_top_k': 25, 'stage3_top_k': 10}
large_corpus = {'stage1_top_k': 200, 'stage2_top_k': 100, 'stage3_top_k': 30}

# 2. Skip stages for speed
fast_search = {'use_reranking': False}  # Skip expensive Stage 3
keyword_only = {'use_dense_retrieval': False, 'use_reranking': False}

# 3. Batch processing cho multiple queries
# Process queries in batches để optimize GPU usage
```

### **📊 Quality Evaluation:**
```python
# Test với known relevant queries
test_queries = [
    ("Bà Triệu sinh năm nao", ["Bà Triệu.md", "Triệu Thị Trinh.md"]),
    ("Điện Biên Phủ chiến dịch", ["Điện Biên Phủ.md", "Chiến dịch 1954.md"]),
    ("Hồ Chí Minh cách mạng", ["Hồ Chí Minh.md", "Cách mạng tháng 8.md"])
]

# Evaluate precision@k for each stage
for query, expected_docs in test_queries:
    results = retriever.retrieve_three_stage(query, ..., return_stage_details=True)
    precision = calculate_precision_at_k(results['final_results'], expected_docs)
    print(f"Query: {query} → Precision@5: {precision:.3f}")
```

## 🔬 Advanced Features

### **🧠 Paper's Training Details:**
```python
# Model Architecture (Paper specifications)
Language Model (Stage 2):
- Base: MiniLM (distilled from RoBERTa-Large)
- Parameters: 30M 
- Layers: 6, Hidden size: 384
- Training: Binary classification với cross-entropy loss

Large Model (Stage 3):  
- Base: MiniLM architecture
- Parameters: 81M
- Layers: 6, Hidden size: 768
- Same training approach as Stage 2

Ensemble (Stage 3):
- 3 identical MiniLM models (30M each)
- Same hyperparameters, different random seeds
- Average similarity scores across models

# Training Configuration (Paper settings)
Optimizer: Adam (β₁=0.9, β₂=0.999, ε=10⁻⁶)
L2 regularization: 0.01
Learning rate: {1×10⁻⁵, 2×10⁻⁵, 5×10⁻⁵}
Epochs: {5, 10, 20, 30}
Batch size: 64
Dropout: 0.1
Max tokens: 512 (training), 256/512 (inference)
```

### **📈 Adaptive Pipeline:**
```python
# Tự động adjust stage sizes dựa trên query complexity
def adaptive_config(query: str) -> Dict:
    query_complexity = analyze_query_complexity(query)
    
    if query_complexity == 'simple':
        return create_three_stage_config('fast')
    elif query_complexity == 'medium':
        return create_three_stage_config('balanced')  
    else:
        return create_three_stage_config('accurate')
```

### **🔄 Pipeline Comparison:**
```python
# So sánh với hệ thống hiện tại
comparison = retriever.compare_with_current_system(
    query="Bà Triệu khởi nghĩa",
    query_tokens=['bà', 'triệu', 'khởi', 'nghĩa'],
    current_system_results=current_results,
    top_k=10
)

print("📊 System Comparison:")
print(f"Three-stage results: {comparison['three_stage_results']}")
print(f"Current system results: {comparison['current_system_results']}")
print(f"Pipeline efficiency: {comparison['three_stage_pipeline']}")
```

## 🎯 Kết Luận từ Paper

### **📊 Paper's Main Contributions:**

1. **🔍 Multi-stage architecture** giải quyết trade-off giữa accuracy và speed
2. **🧠 Alternative to pairwise models** với better zero-shot performance  
3. **🎯 Practical deployment** với minimal speed reduction (1.39x vs 4.00x)

### **🏆 Paper's Key Findings:**

#### **✅ What Works Well:**
```python
✅ BM25 + Language Model + Large Model:
   - Best overall performance (0.6176 NDCG@10)
   - Only 39% speed penalty vs baseline
   - Consistent across all test datasets
   - Good zero-shot generalization

✅ Model Ensemble approach:
   - Stable performance improvement
   - Minimal computational overhead
   - Robust alternative to complex models
```

#### **❌ What Doesn't Work:**
```python
❌ Pairwise Models (existing approach):
   - Poor zero-shot performance (0.5105 vs 0.5761 baseline)
   - 4x speed penalty (too expensive)
   - Token length limitations với long documents
   - Quadratic complexity (a₂² inferences)
```

### **🚀 Practical Recommendations:**

#### **📈 For Production Systems:**
```python
Recommended: BM25 + LM + Large Model
- Setting: a₁=100, a₂=20, final=10
- Expected: 7% accuracy improvement, 39% speed cost
- Best for: Quality-focused applications

Alternative: BM25 + LM + Ensemble  
- Setting: 3-model ensemble
- Expected: 3% accuracy improvement, 50% speed cost
- Best for: Robust, stable performance
```

#### **⚡ For Speed-Critical Applications:**
```python
Baseline: BM25 + Language Model only
- Skip Stage 3 entirely  
- Still 58% better than BM25-only
- Reasonable accuracy-speed balance
```

#### **🔬 For Research/High-Precision:**
```python
Full Pipeline: All 3 stages with tuned parameters
- Experiment với different a₁, a₂ values
- Consider domain-specific model fine-tuning
- Monitor convergence points (Figure 4 in paper)
```

### **💡 Implementation Insights:**

1. **📊 Parameter Tuning:** Paper shows accuracy converges at a₂=30 (ensemble) or a₂=50 (large model)
2. **🎯 Trade-off Flexibility:** Easy to adjust ai parameters based on accuracy/speed requirements  
3. **🧠 Zero-shot Performance:** Critical for practical deployment where domain-specific training data is expensive
4. **⚖️ Ensemble Benefits:** Simple approach (same model, different seeds) provides stable improvements

### **🔮 Future Developments (Paper Mentions):**
- Replace BM25 với embedding methods (DPR)
- Explore other module combinations
- Domain adaptation techniques
- More sophisticated ensemble strategies

**📋 Citation:**
```
@article{sasazawa2023text,
  title={Text Retrieval with Multi-Stage Re-Ranking Models},
  author={Sasazawa, Yuichi and Yokote, Kenichi and Imaichi, Osamu and Sogawa, Yasuhiro},
  journal={arXiv preprint arXiv:2311.07994},
  year={2023}
}
```