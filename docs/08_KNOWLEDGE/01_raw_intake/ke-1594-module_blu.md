---
module_id: KE-1504
title: 14. 当前缺失清单
category: module_blueprint
ttl: permanent
---

# 14. 当前缺失清单

14. 当前缺失清单

| # | 缺失项 | 对标 | 严重度 | 说明 |
|---|---|---|---|---|
| 1 | Context Rot 显式建模 | Anthropic | 🔴 P0 | n² attention 衰减函数 |
| 2 | Context Provenance 溯源 | Anthropic | 🔴 P0 | {blueprint_id, §, ke_id} |
| 3 | Multi-Turn Curation Loop | Anthropic | 🔴 P0 | per-turn 增量注入 |
| 4 | Eviction Chain 逐出链 | 两者 | 🟡 P1 | 超预算"什么先丢" |
| 5 | Context Effectiveness Eval | Anthropic | 🟡 P1 | 检测 AI 实际引用率 |
| 6 | Persistent Memory Bank | Vibe Coding | 🟡 P1 | AI 自动读写 memory-bank |
| 7 | XML Tag 强制分区 | Anthropic | 🟡 P1 | 四层分区注入 |
| 8 | Dynamic Relevance Scoring | Windsurf | 🟡 P1 | intent 驱动动态分数 |
| 9 | Context Conflict Resolution | — | 🟢 P2 | 矛盾源仲裁 |
| 10 | Cost-Aware Budget | Anthropic | 🟢 P2 | Token → 成本换算 |

---
