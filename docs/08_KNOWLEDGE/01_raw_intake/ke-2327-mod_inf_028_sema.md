---
module_id: KE-2232-----------mod-inf-028-sema-000
status: active
title: 4.3 语义审计 — 调度 MOD-INF-028 SemanticAuditor
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.3 语义审计 — 调度 MOD-INF-028 SemanticAuditor

4.3 语义审计 — 调度 MOD-INF-028 SemanticAuditor

> **语义审计已升格为 MOD-INF-028 SemanticAuditor 平级独立服务（v4.0.0, belongs_to: null）。** Orchestrator 通过 Phase 2 TRIAGE 检测规则文档变更后，经由 `references` 链路 dispatch 到 SemanticAuditor。审计判定逻辑、触发条件（F+G）、安全边界、LLM 桥接等全部在 [MOD-INF-028 蓝图](./semantic-auditor/blueprint.md) v4.0.0 中。DIM-SEMANTIC-001 已在 v4.0.0 移除。

Orchestrator v4.0.0 的角色：Phase 2 TRIAGE 检测到规则文档变更 → 通过 `references` 链路 dispatch 到 SemanticAuditor（平级独立服务，belongs_to: null），而非作为内部维度调度。DIM-SEMANTIC-001 已移除。

```yaml
