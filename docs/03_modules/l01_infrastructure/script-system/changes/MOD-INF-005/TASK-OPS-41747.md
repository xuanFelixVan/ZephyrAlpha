---
task_id: "OPS-41747"
source_blueprint: "MOD-INF-005"
source_section: "auto-FIND-D3-20260506-3a4997d61dfc"
title: "修复 CRITICAL Finding: [CR-004] MOD-MCP-001 的 status 字段跨表不一致"
description: "从 CRITICAL Finding 自动生成。

原 Finding: FIND-D3-20260506-3a4997d61dfc
维度: D3
目标文件: docs/03_modules/_cross_layer/mcp-servers/blueprint.md
描述: [CR-004] MOD-MCP-001 的 status 字段跨表不一致
证据: 不一致的值:
  REG-001:status = Active ← SSoT
  physical:status = Draft

修复建议: 无
建议类型: needs_review
建议动作: create_task"
priority: "P0"
upstream_files:
  - "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"
downstream_outputs:
  - path: "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"
    description: "修复后的目标文件"
allowed_touch:
  - []
forbidden_touch:
  - []
assigned_model: "deepseek"
assigned_pipeline: "A"
estimated_tokens: 4000
timeout_minutes: 30
acceptance_criteria:
  - "目标文件 docs/03_modules/_cross_layer/mcp-servers/blueprint.md 的违规已修复"
  - "D3 维度重新扫描无该 Finding 重现"
rollback_instructions: "git checkout -- docs/03_modules/_cross_layer/mcp-servers/blueprint.md"
depends_on:
  - []
blocked_by:
  - []
status: "PENDING"
tags_fn:
  - finding-fix
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-005"
completed_gates: []
blocked_gates: {}
artifact_paths:
  - []
ai_autonomy_level: "review_required"
---

# 修复 CRITICAL Finding: [CR-004] MOD-MCP-001 的 status 字段跨表不一致

## 目标
从 CRITICAL Finding 自动生成。

原 Finding: FIND-D3-20260506-3a4997d61dfc
维度: D3
目标文件: docs/03_modules/_cross_layer/mcp-servers/blueprint.md
描述: [CR-004] MOD-MCP-001 的 status 字段跨表不一致
证据: 不一致的值:
  REG-001:status = Active ← SSoT
  physical:status = Draft

修复建议: 无
建议类型: needs_review
建议动作: create_task

## 触发条件
- 来自 Finding 自动生成

## 执行步骤

### 读
- docs/03_modules/_cross_layer/mcp-servers/blueprint.md

### 做
- 按 applicable_rules 修复违规

### 产
- docs/03_modules/_cross_layer/mcp-servers/blueprint.md

### 检
- 运行对应审计重新扫描

## 验收标准
- 目标文件 docs/03_modules/_cross_layer/mcp-servers/blueprint.md 的违规已修复
- D3 维度重新扫描无该 Finding 重现

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 回滚 | git checkout -- docs/03_modules/_cross_layer/mcp-servers/blueprint.md |

---
*创建: 2026-05-09 08:40 | 更新: 2026-05-09 08:40*
*本文件由 create_task_from_finding.py 自动生成（MOD-INF-006 TaskCard 格式）。*
