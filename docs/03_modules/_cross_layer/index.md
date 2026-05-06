---
module_id: CROSS-LAYER-INDEX
title: cross_layer 模块蓝图索引
doc_type: index
status: active
version: "1.2.0"
date: "2026-05-06"
layer: cross_layer
summary: >
  cross_layer 模块物理真源已从 l01_infrastructure/ 迁移至 _cross_layer/（Phase 5 执行完毕）。
  8 个模块蓝图直放于 _cross_layer/<module>/blueprint.md。
  registry 已同步更新（v1.2.0）。
---

# cross_layer 模块蓝图索引

> **Phase 5 迁移完成（2026-05-06）**：8 个 `layer: cross_layer` 模块已从 `l01_infrastructure/` 迁移至本目录。

## 模块清单

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

## 迁移记录

- **2026-05-06 Phase 5**：物理目录从 `l01_infrastructure/` 迁至 `_cross_layer/`。
  操作：① 移动目录；② `sync_registry_from_blueprints.py --write`（file_path 自动更随）；③ 本索引更新。
