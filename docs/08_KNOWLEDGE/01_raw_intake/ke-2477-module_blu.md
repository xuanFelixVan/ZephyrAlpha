---
module_id: KE-2382
title: 6.3 蓝图外已有实现（纳入蓝图管理）
category: module_blueprint
---

# 6.3 蓝图外已有实现（纳入蓝图管理）

6.3 蓝图外已有实现（纳入蓝图管理）

| 已有实现 | 实际路径 | 能力 | 蓝图对应 | 管理方式 |
|---------|---------|------|---------|---------|
| Token 预算管理器 | `src/zephyr/context-engine/context_budget_tracker.py` | 三级阈值 L1/L2/L3 | M-21 的 session 级子集 | 由 context-engine 蓝图管理，本蓝图引用 |
| 熔断器 | `src/zephyr/gates/circuit_breaker.py` | 单向熔断 + L08 注册表 | M-13 fault_isolator 的子集 | 由 gate-engine 蓝图管理，本蓝图引用 |
| Agent SLO 监控 | `src/zephyr/orchestrator/agent_health_monitor.py` | 5 项 SLO + 三态健康 | M-18 capacity_slo.yaml 的 Agent 维度 | 由 orchestrator 蓝图管理，本蓝图引用 |
| MCP 工具限流 | `src/zephyr/mcp/tool-contracts.yaml` | 声明式 rate_limit_qps | M-21 的 MCP 层子集 | 由 mcp-servers 蓝图管理，本蓝图引用 |
| 上下文规则 | `config/context-rules.yaml` | 15 条上下文管理规则 | M-18 的上下文维度 | 由 context-engine 蓝图管理，本蓝图引用 |
| 基础设施登记表 | `_registry/catalogs/infrastructure-registry.md` | 8 个组件 SLA | M-18 的基础设施维度 | 由 registry 管理，本蓝图引用 |
| AI 风险登记表 | `_registry/catalogs/ai-risk-registry.md` | 8 项 AI 风险 | M-17 的风险维度 | 由 registry 管理，本蓝图引用 |

---
