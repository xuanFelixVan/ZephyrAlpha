---
module_id: CROSS-LAYER-INDEX
title: cross_layer 模块蓝图索引
doc_type: index
status: active
version: "1.3.0"
date: "2026-05-08"
layer: cross_layer
summary: >
  cross_layer 模块物理真源已从 l01_infrastructure/ 迁移至 _cross_layer/（Phase 5 执行完毕）。
  行为审计（MOD-INF-033 BehavioralAuditor）等新模块已纳入索引（v1.3.0）。
  registry 已同步更新。
---

# cross_layer 模块蓝图索引

> **Phase 5 迁移完成（2026-05-06）**：8 个 `layer: cross_layer` 模块已从 `l01_infrastructure/` 迁移至本目录。
> **v1.3.0（2026-05-08）**：补充 BehavioralAuditor、OrphanJudge 等 audit-orchestrator 子系统模块。

## 模块清单

### AuditOrchestrator 子系统（v4.0.0 三审计架构）

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-INF-027 | Audit Orchestrator | [blueprint](audit-orchestrator/blueprint.md) |
| MOD-INF-028 | Semantic Auditor | [blueprint](semantic-auditor/blueprint.md) |
| MOD-INF-033 | **Behavioral Auditor** | [blueprint](behavioral-auditor/blueprint.md) |

### 跨层基础设施模块

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-INF-007 | Gate Engine | [blueprint](gate-engine/blueprint.md) |
| MOD-INF-008 | Context Engine | [blueprint](context-engine/blueprint.md) |
| MOD-INF-009 | Pipeline | [blueprint](pipeline/blueprint.md) |
| MOD-INF-010 | Feedback Loop | [blueprint](feedback-loop/blueprint.md) |
| MOD-INF-012 | Database | [blueprint](database/blueprint.md) |
| MOD-INF-013 | MCP Servers | [blueprint](mcp-servers/blueprint.md) |
| MOD-INF-014 | LLM Security | [blueprint](llm-security/blueprint.md) |
| MOD-INF-016 | Shared + Core | [blueprint](shared-core/blueprint.md) |

### 治理与质量模块

| module_id | 模块名 | blueprint |
|-----------|--------|-----------|
| MOD-INF-029 | Orphan Judge | [blueprint](orphan-judge/blueprint.md) |
| MOD-INF-030 | RedBlue Validator | [blueprint](redblue-validator/blueprint.md) |
| MOD-INF-031 | AutoFix Engine | [blueprint](auto-fix-engine/blueprint.md) |

## 迁移记录

- **2026-05-08 v1.3.0**：补充 AuditOrchestrator 三审计子系统（027/028/033）+ 治理模块（029/030/031）。
- **2026-05-06 Phase 5**：物理目录从 `l01_infrastructure/` 迁至 `_cross_layer/`。
  操作：① 移动目录；② `sync_registry_from_blueprints.py --write`（file_path 自动更随）；③ 本索引更新。
