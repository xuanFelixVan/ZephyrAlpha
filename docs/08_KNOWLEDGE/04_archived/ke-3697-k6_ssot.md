---
module_id: KE-3550
title: 2.7 K6：SSoT 冲突数
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 2.7 K6：SSoT 冲突数

2.7 K6：SSoT 冲突数

| 属性 | 值 |
|------|-----|
| **公式** | `被多次定义的核心概念数`（手动计数） |
| **冲突判定** | 同一概念在 _registry/vocabularies/glossary.yaml 外被 ≥ 2 个文件定义 |
| **数据源** | _registry/vocabularies/glossary.yaml（META-GLS-001）作为仲裁基准 |
| **当前基线** | 待首次度量后建立（已知：`SSoT` 曾在 PS-STD-003 和 PS-STD-001 中被独立定义，现已统一） |
| **告警阈值** | > 3 个冲突 |
| **目标** | 0 |

---
