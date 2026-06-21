---
module_id: KE-2128
status: active
title: 3.5 知识衰减模型
category: module_blueprint
---

# 3.5 知识衰减模型

3.5 知识衰减模型

每个 KE 有一个 `half_life_days`（半衰期），用于计算知识"新鲜度"：

```
freshness = 0.5 ^ (days_since_verified / half_life_days)
```

| 分类 | 默认半衰期 | 说明 |
|------|-----------|------|
| `blueprint_decision` | 180d | 蓝图决策相对稳定 |
| `best_practice` | 90d | 最佳实践随工具链演进 |
| `factor` | 365d | 量化因子知识长期有效 |
| `failure_pattern` | 永久 | 失败模式不会过时（只会被覆盖） |
| `guardrail` | 60d | 护栏规则需跟随代码变更 |


> **代码状态联动新鲜度（盲点#45）**：上述半衰期是**纯时间衰减**——它假设知识正确性只随"时间流逝"退化。但在 vibe coding 的实际场景中，知识失效最常见的原因不是"时间到了"而是 **"代码变了"**。例如：`pyproject.toml` 中 ruff 从 0.5 升级到 0.11，所有提及 `ruff v0.5` 的 KE 应该**不等 180 天**，在升级提交的那一刻就立即触发新鲜度重评估。此机制详见 §3.5.1 和 §9.14.4。
