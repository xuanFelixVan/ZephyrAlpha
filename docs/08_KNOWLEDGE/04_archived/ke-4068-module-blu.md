---
module_id: KE-4068
title: 15. 关键关联
category: module_blueprint
---

# 15. 关键关联

15. 关键关联

| 关联文档 | 说明 |
|---------|------|
| `ai-autonomy-authority-registry.md` | 新组件权限的单一真源 |
| `vibe-coding-pipelines/blueprint.md` | 双管线 + 脚本系统蓝图 |
| `context-engine/blueprint.md` | Token 预算管理器（context_budget_tracker.py）的归属蓝图 |
| `gate-engine/blueprint.md` | 熔断器（circuit_breaker.py）的归属蓝图 |
| `mcp-servers/blueprint.md` | MCP 工具限流（tool_contracts.yaml）的归属蓝图 |
| `infrastructure-registry.md` | 基础设施组件 SLA 声明 |
| `ai-risk-registry.md` | AI 操作风险登记 |
| Google SRE Workbook | Error Budget 五级响应 + 四黄金信号 + Burn Rate + Blameless Postmortem |
| OpenTelemetry GenAI Semantic Conventions | AI Agent 可观测性标准 |
| VictoriaMetrics Vibe Coding Blog (2026-01) | Vibe Coding 工具可观测性方案 |

> **历史溯源**：原始施工图 Wave 0 终审产出（2026-04-27），三轮审计 GLM/Kimi/Qwen + Opus-4.7 裁决 5 条争议 + 兜底 V-11/V-12/V-13。2026-05-01 迁入 `03_modules/infra_ops/capacity-assurance/blueprint.md`。2026-05-03 v2.0.0 升级——对齐专业机构实践与 Vibe Coding 社区前沿，新增 M-21~M-27 共 7 个模块，纳入 7 项蓝图外已有实现，修正路径与状态。2026-05-03 v2.1.0 升级——补齐施工前置设计：Error Budget 三级→五级 + 灾难恢复策略 + 容量预测模型 + 跨模块集成设计。

---
