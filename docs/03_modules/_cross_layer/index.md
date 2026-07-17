---
module_id: GOV-CROSS-LAYER-INDEX-001
title: cross_layer 模块蓝图索引
doc_type: index
status: Active
version: "1.4.0"
date: "2026-06-22"
layer: L1_foundation
summary: >
  cross_layer 模块物理真源位于 _cross_layer/（早期架构升级迁移完成）。
  行为审计（MOD-INF-033 BehavioralAuditor）等模块已纳入索引。
  命名规范：统一下划线（snake_case）。
ttl: permanent
---

# cross_layer 模块蓝图索引

> **命名规范**：全项目统一下划线（snake_case），禁止连字符。
> **v1.4.0（2026-06-22）**：统一下划线命名，修正蓝图路径。

## 模块清单

### AuditOrchestrator 子系统（三审计架构）

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-INF-027 | Audit Orchestrator | [blueprint](audit_orchestrator/blueprint.md) |
| MOD-INF-028 | Semantic Auditor | [blueprint](semantic_auditor/blueprint.md) |
| MOD-INF-033 | **Behavioral Auditor** | [blueprint](behavioral_auditor/blueprint.md) |

### 跨层基础设施模块

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-GATE_ENGINE | Gate Engine | [blueprint](gate_engine/blueprint.md) |
| MOD-CONTEXT_ENGINE | Context Engine | [blueprint](context_engine/blueprint.md) |
| MOD-INF-009 | Pipeline | [blueprint](pipeline/blueprint.md) |
| MOD-FEEDBACK_LOOP | Feedback Loop | [blueprint](feedback_loop/blueprint.md) |
| MOD-DATABASE | Database | [blueprint](database/blueprint.md) |
| MOD-INF-013 | MCP Servers | [blueprint](model_context_protocol_servers/blueprint.md) |
| MOD-LLM_SECURITY | LLM Security | [blueprint](large_language_model_security/blueprint.md) |
| MOD-INF-016 | Shared + Core | [blueprint](shared_core/blueprint.md) |

### 治理与质量模块

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-INF-029 | Orphan Judge | [blueprint](orphan_judge/blueprint.md) |
| MOD-INF-030 | RedBlue Validator | [blueprint](red_blue_validator/blueprint.md) |
| MOD-INF-031 | AutoFix Engine | [blueprint](auto_fix_engine/blueprint.md) |

## 迁移记录

- **2026-06-22 v1.4.0**：统一下划线命名，修正蓝图路径连字符→下划线。
- **2026-05-08 v1.3.0**：补充 AuditOrchestrator 三审计子系统（027/028/033）+ 治理模块（029/030/031）。
- **早期迁移**：物理目录现为 `_cross_layer/`（原 `infra_ops/` 路径不再使用）。
