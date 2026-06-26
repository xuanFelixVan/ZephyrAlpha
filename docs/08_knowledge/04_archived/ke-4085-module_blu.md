---
module_id: KE-3931
title: 16. 上下文引擎新设计决策
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 16. 上下文引擎新设计决策

16. 上下文引擎新设计决策

| ID | 决策 | 理由 | 替代方案 | 重评 |
|----|------|------|---------|:---:|
| DD7 | ContextRot 幂函数 n^{-k} | n² 衰减是幂级数—比一刀切精确 | 线性衰减—不反映 n² | k 值校准 |
| DD8 | Provenance 全覆盖 | 上下文致错时唯一追溯链 | 可选—追溯断裂 | — |
| DD9 | Eviction 三维排序 | Token 超预算精准逐出 | FIFO/LRU 语义盲 | 权重校准 |
| DD10 | Per-Turn 增量注入 | Agent 5 轮全量 build = n×5 token 浪费 | 全量 build | — |

---
