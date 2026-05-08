---
module_id: KE-governance-1_5-003
title: 1.5 术语
category: governance_rule
---

# 1.5 术语

1.5 术语

| 术语 | 含义 |
|------|------|
| **分类维度** | 规则的一个分类角度，每个维度有独立的受控词表 |
| **受控词表** | 维度值的合法集合，不允许自由扩展 |
| **规则画像** | 一条规则在五个维度上的取值组合，如 `{domain: document, layer: L1, scope: global, stability: stable, executor: ai_gated}` |
| **推导链** | 冲突发生时，按 stability → layer → scope 顺序链式推导优先级，三步后仍冲突则上报 Owner |
| **终极仲裁** | 推导链失效时，由 Owner 按 MTH-003 目标优先原则手动裁决 |

---
