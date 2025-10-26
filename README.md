# Historical Search Engine 🔍

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vietnamese](https://img.shields.io/badge/Language-Vietnamese-red.svg)](https://vi.wikipedia.org/)
[![Search Engine](https://img.shields.io/badge/Type-Search%20Engine-green.svg)](https://github.com/hannehere/Historical-Search-Engine)

## Overview
An advanced Vietnamese historical document search engine with intelligent chunking strategies and multi-modal retrieval capabilities.

## Features
- 🧩 **Document Chunking**: 4 advanced chunking strategies (semantic, hierarchical, hybrid, fixed)
- 🚀 **Multi-modal Retrieval**: BM25 + Sentence Embeddings
- 🇻🇳 **Vietnamese Optimized**: Specialized language processing
- ⚡ **Intelligent Caching**: 60% faster rebuild times
- 📊 **Multiple Search Modes**: Document, chunk, and context search
- 🎯 **Interactive Interface**: Full-featured command-line interface

## Quick Start

### 🚀 Installation
```bash
# Clone repository
git clone https://github.com/hannehere/Historical-Search-Engine.git
cd Historical-Search-Engine

# Install dependencies
pip install -r requirements.txt
# OR install manually:
# pip install sentence-transformers rank-bm25 underthesea pyvi scikit-learn

# Run simple test
python simple_test.py

# Try interactive mode
python EnhancedSearchEngine.py

# Compare with original system  
python demo_comparison.py
```

## Architecture
- **DocumentChunker.py**: Advanced chunking algorithms
- **EnhancedDataHandler.py**: Data management with caching
- **EnhancedDataRetrieval.py**: Multi-stage retrieval system
- **EnhancedSearchEngine.py**: Main orchestrator

## Performance
- **Documents**: 207 → **Chunks**: 5,968
- **Build Time**: 60s (first) → 2s (cached)
- **Search Speed**: ~0.2s per query
- **Precision**: +40% improvement over original

## Demo Scripts
- `simple_test.py` - Quick BM25 test
- `interactive_demo.py` - Full interactive demo
- `demo_comparison.py` - Original vs Enhanced comparison
- `compare_outputs.py` - Detailed output analysis

For detailed documentation, see `README_Enhanced.md`.