---
module_id: KE-3207-------b-000
title: 2.2 平台能力层（B 轨横切）
category: documentation
ttl: permanent
---

# 2.2 平台能力层（B 轨横切）

2.2 平台能力层（B 轨横切）

| 模块 | 路径 | 权限 | 判定理由 |
|------|------|------|---------|
| llm-security | `src/zephyr/llm-security/` | Immutable Core | 安全网关核心 |
| vector-memory | `src/zephyr/vector-memory/` | Human-Gated | 检索阈值影响召回 |
| context-engine | `src/zephyr/context-engine/` | Human-Gated | 上下文预算影响所有 AI 调用 |
| orchestrator | `src/zephyr/orchestrator/` | Human-Gated | 路由策略影响 Agent 行为 |
| feedback-loop | `src/zephyr/feedback-loop/` | Human-Gated | 进化策略影响系统演化方向 |
| gates | `src/zephyr/gates/` | Immutable Core | 合规门禁不可由 AI 禁用 |
| db | `src/zephyr/db/` | Human-Gated | Schema 修改需审批 |
| mcp | `src/zephyr/mcp/` | Human-Gated | 协议版本锁定 |
| shared | `src/zephyr/shared/` | Human-Gated | 共享契约修改影响多层 |
