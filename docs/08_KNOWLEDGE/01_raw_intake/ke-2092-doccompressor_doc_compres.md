---
module_id: KE-2001---doc-compres-003
status: active
title: 3. DocCompressor — doc_compressor.py (§5.2 + DD3 + DD5)
category: module_blueprint
ttl: permanent
---

# 3. DocCompressor — doc_compressor.py (§5.2 + DD3 + DD5)

3. DocCompressor — doc_compressor.py (§5.2 + DD3 + DD5)

三级压缩回退：

```
Level 1: Qwen2.5-3B 本地摘要模型 → 语义压缩
Level 2: 规则基摘要 → 关键段落提取
Level 3: 截断 → 超出预算直接截断
```

CompressionPolicy (Pydantic frozen, Immutable Core):
- preserve_structure=true — 保留文档结构
- preserve_provenance=true — 保留溯源信息
- min_chars≥100, max_chars≤10000
- immutable_blocks preserved — 不可变块不被压缩

COMPRESS-C01 不变量校验：
- ALL 5 不变量 PASS → 压缩通过
- 任一不变量 FAIL → CompressionInvariantError → 回退降级策略 beta 本地 LLM
