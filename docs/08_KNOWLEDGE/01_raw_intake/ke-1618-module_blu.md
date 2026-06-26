---
module_id: KE-1528
title: 15. 风险与缓解
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 15. 风险与缓解

15. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| **Doom Loop**——修复→新问题→修复→循环 | 中 | 高 | max_passes 硬上限 + NonConvergenceHandler 降级 YELLOW + max_global_rounds=3 |
| **孤儿误判**——有价值文件被判为"删除" | 中 | 高 | Git pre-tag 可回滚 + 判定置信度阈值 + 人工复核高风险判定 |
| **语义审计误报**——触发条件过于宽泛 | 中 | 中 | 触发条件是机械的（文件存在性/数值比对/ID匹配），误报率天然低 |
| **红方攻击不完全**——攻击场景遗漏导致虚假安全感 | 高 | 中 | 攻击场景库持续扩充 + 每次绕过自动录入新场景 |
| **审计自身性能**——24373 资产扫描耗时 | 中 | 中 | 增量扫描 + ThreadPoolExecutor（RULE-SEVEN） |
| **收敛不了**——设计权衡问题 | 高 | 低 | YELLOW 可接受 + 人工最终裁决 |

---
