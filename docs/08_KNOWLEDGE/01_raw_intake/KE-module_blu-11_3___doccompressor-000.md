---
module_id: KE-module_blu-11_3___doccompressor-000
title: 11.3 修改DocCompressor
category: module_blueprint
---

# 11.3 修改DocCompressor

11.3 修改DocCompressor

```
DocCompressor遵循CL-018 RI扩展模式:
- CompressionPolicy为Immutable Core(Pydantic frozen)→修改需Human-Gated
- compress()实现可AI-Modified→修改后运行test_doc_compressor.py
```

---
