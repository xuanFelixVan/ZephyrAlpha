---
module_id: KE-3261
title: 3.2 决策规则
category: documentation
---

# 3.2 决策规则

3.2 决策规则

| 总分 | 决策 | 含义 |
|:---:|:---:|------|
| **≥ 20** | **Buy** | 强制使用开源，禁止自研 |
| **15-19** | **Buy + Wrap** | 用开源 + 薄层封装（OCP adapter），保留替换弹性 |
| **10-14** | **Hybrid** | 用开源作为 reference / inspiration，核心逻辑自研 |
| **< 10** | **Build** | 从零自研 |
