---
module_id: KE-4377--------rfc-2025--002
title: OTel AI Agent 语义约定对齐（RFC 2025-11）
category: module_blueprint
---

# OTel AI Agent 语义约定对齐（RFC 2025-11）

OTel AI Agent 语义约定对齐（RFC 2025-11）

ZephyrAlpha 的 Pipeline/TaskCard 元模型与 AI Agent RFC 定义的 20 种 span 类型存在直接映射关系。Telemetry traces 子系统在采集以下 OTel Agent span 类型时 MUST 使用标准命名：

| OTel Agent Span 类型 | ZephyrAlpha 对应场景 | Span 命名 |
|----------------------|---------------------|---------|
| `gen_ai.agent.invoke` | M1/M6/M8 Agent 执行 | `gen_ai.agent.invoke {agent_name}` |
| `gen_ai.task.create` | TaskCard 创建 | `gen_ai.task.create {task_id}` |
| `gen_ai.task.execute` | TaskCard Pipeline 执行 | `gen_ai.task.execute {task_id}` |
| `gen_ai.task.delegate` | Orc 分配子任务 | `gen_ai.task.delegate` |
| `gen_ai.tool.execute` | Script D1-D12 / 工具调用 | `gen_ai.tool.execute {tool_name}` |
| `gen_ai.workflow.execute` | Pipeline 编排执行 | `gen_ai.workflow.execute {pipeline_id}` |
| `gen_ai.workflow.transition` | Gate G0→G1→...→G7 | `gen_ai.workflow.transition {gate_id}` |
| `gen_ai.session` | AI Session top-level | `gen_ai.session {session_id}` |
| `gen_ai.guardrail.check` | Gate Engine 门禁判定 | `gen_ai.guardrail.check {gate_id}` |
| `gen_ai.human.review` | Human-in-the-loop 审批 | `gen_ai.human.review {review_id}` |
| `gen_ai.memory.retrieve` | CE 上下文检索 | `gen_ai.memory.retrieve` |
| `gen_ai.memory.store` | 知识库写入 | `gen_ai.memory.store {kb_id}` |
| `gen_ai.context.checkpoint` | Session 状态快照 | `gen_ai.context.checkpoint` |
