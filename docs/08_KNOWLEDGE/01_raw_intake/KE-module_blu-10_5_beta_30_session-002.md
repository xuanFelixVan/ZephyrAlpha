---
module_id: KE-module_blu-10_5_beta_30_session-002
title: 10.5 beta 30 Session 模拟结果
category: module_blueprint
---

# 10.5 beta 30 Session 模拟结果

10.5 beta 30 Session 模拟结果

| 指标 | experimental | beta |
|------|:--:|:--:|
| PASS | 20 | 20 |
| WARNING / REJECT | 10 (WARNING) | 10 (REJECT) |
| 违规率 | 33.3% | 33.3% |
| 违规严重度 | P1 (提醒) | **P0 (阻断)** |
| 门禁类型 | GATE-16 (模拟) | **G6 (生产)** |
| MCP 返回策略 | top-5, SHOULD read | **top-3, MUST read** |

> **注**：beta 模拟使用与 experimental 完全相同的 30 个 scenario（18 full/6 partial/6 none）以建立可比基线。
> 违规率不变但严重度升级——同样的 10 个违规从"提醒"变为"阻断"。
> 关键词修复和 cross_read_hint 的效果将在后续真实 AI session 中体现，需要生产数据验证。
