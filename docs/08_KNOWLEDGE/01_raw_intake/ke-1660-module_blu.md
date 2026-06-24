---
module_id: KE-1570
title: 17.1 预测维度
category: module_blueprint
---

# 17.1 预测维度

17.1 预测维度

| 维度 | 指标 | 数据来源 | 预测方法 | 预测周期 |
|------|------|---------|---------|:---:|
| 模块增长 | 模块数 | `module-registry.yaml` / `git log` | 线性回归 + 指数平滑 | 1 周 / 1 月 / 3 月 |
| 内存占用 | RSS / VIRT | `psutil` 采样（M-23 sandbox_executor） | 线性回归 | 1 月 / 3 月 |
| Token 消耗 | tokens/day | `token_budget_usage` 表 | 移动平均 + 趋势外推 | 1 周 / 1 月 |
| 成本消耗 | cost/day | `token_budget_usage` 表 cost_usd | 同上 | 1 周 / 1 月 |
| 测试时长 | 全量测试耗时 | pytest --durations | 线性回归 | 1 月 / 3 月 |
| 类型检查时长 | dmypy 耗时 | dmypy 基准测试 | 同上 | 1 月 |
