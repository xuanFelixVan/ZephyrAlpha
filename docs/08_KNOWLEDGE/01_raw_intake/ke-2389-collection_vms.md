---
module_id: KE-2294-----collection---------vms-005
title: 5.2 过渡期 Collection 映射（现有 → VMS 终态）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5.2 过渡期 Collection 映射（现有 → VMS 终态）

5.2 过渡期 Collection 映射（现有 → VMS 终态）

> **⚠️ 路径澄清 (v0.6.0 修复 D3)**：kb/ 当前 ChromaDB 路径为 `.audit_cache/vector_index/`（由 `shared/paths.py` 集中管理，非硬编码，`kb/chromadb_init.py` 已使用集中式路径）。VMS 投产路径为 `data/vector_db/`。Phase 2 迁移时 `BridgeLayer` 负责从 `.audit_cache/vector_index/` 读取 → 写入 `data/vector_db/`。迁移完成后 `.audit_cache/vector_index/` 归档保留 30 天作为回滚保险。

| 现有 Collection（kb/） | 嵌入模型 | 维度 | → VMS 终态 Collection | 迁移操作 |
|------|:---:|:---:|------|------|
| `ke_entries` | bge-small-zh-v1.5 | 512d | `knowledge` | 迁移数据 + 重命名 + 可选重嵌入至 1024d |
| `vibe_rules` | bge-small-zh-v1.5 | 512d | `rules` | 迁移数据 + 重命名 + **强制重嵌入至 1024d**（治理级精度要求） |
| `blueprints` | bge-small-zh-v1.5 | 512d | `blueprints` | 保留 512d + 重命名 |
| `failure_patterns` | bge-small-zh-v1.5 | 512d | `lessons` | 迁移数据 + 重命名 + 重嵌入至 1024d |
| `unified_memory` | bge-small-zh-v1.5 | 512d | 按 topic 拆分到对应 Collection | 解析 topic → 路由到目标 Collection |
