---
module_id: KE-3759
title: 1.1 模块身份
category: module_blueprint
---

# 1.1 模块身份

1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-024 |
| 代码落位 | `src/zephyr/budget-enforcer/` |
| 运行时平面 | Hot memory（Pre-flight Gate + In-flight Stream Abort Guard + 调用后 Runtime Enforcer——覆盖调用前→调用中→调用后全生命周期） |
| 核心职责 | 强制执行 Token/Cost 预算——超预算自动降级，零人工介入；事后成本归因 + ROI 分析 |
