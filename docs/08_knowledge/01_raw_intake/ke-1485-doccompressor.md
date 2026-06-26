---
module_id: KE-1395---doccompressor-000
status: active
title: 11.3 修改DocCompressor
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11.3 修改DocCompressor

11.3 修改DocCompressor

```
DocCompressor遵循CL-018 RI扩展模式:
- CompressionPolicy为Immutable Core(Pydantic frozen)→修改需Human-Gated
- compress()实现可AI-Modified→修改后运行test_doc_compressor.py
```

---
