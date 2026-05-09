---
task_id: "OPS-44298"
source_blueprint: "MOD-INF-005"
source_section: "auto-FIND-D3-20260506-ed8e6597eae2"
title: "修复 CRITICAL Finding: [CR-005] MOD-LSG-001 的 priority 字段跨表不一致"
description: "从 CRITICAL Finding 自动生成。

原 Finding: FIND-D3-20260506-ed8e6597eae2
维度: D3
目标文件: docs/03_modules/_cross_layer/llm-security/blueprint.md
描述: [CR-005] MOD-LSG-001 的 priority 字段跨表不一致
证据: 不一致的值:
  REG-001:priority = P0 ← SSoT
  physical:priority = P2

修复建议: 无
建议类型: needs_review
建议动作: create_task"
priority: "P0"
upstream_files:
  - "docs/03_modules/_cross_layer/llm-security/blueprint.md"
downstream_outputs:
  - path: "docs/03_modules/_cross_layer/llm-security/blueprint.md"
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
  - "目标文件 docs/03_modules/_cross_layer/llm-security/blueprint.md 的违规已修复"
  - "D3 维度重新扫描无该 Finding 重现"
rollback_instructions: "git checkout -- docs/03_modules/_cross_layer/llm-security/blueprint.md"
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

# 修复 CRITICAL Finding: [CR-005] MOD-LSG-001 的 priority 字段跨表不一致

## 目标
从 CRITICAL Finding 自动生成。

原 Finding: FIND-D3-20260506-ed8e6597eae2
维度: D3
目标文件: docs/03_modules/_cross_layer/llm-security/blueprint.md
描述: [CR-005] MOD-LSG-001 的 priority 字段跨表不一致
证据: 不一致的值:
  REG-001:priority = P0 ← SSoT
  physical:priority = P2

修复建议: 无
建议类型: needs_review
建议动作: create_task

## 触发条件
- 来自 Finding 自动生成

## 执行步骤

### 读
- docs/03_modules/_cross_layer/llm-security/blueprint.md

### 做
- 按 applicable_rules 修复违规

### 产
- docs/03_modules/_cross_layer/llm-security/blueprint.md

### 检
- 运行对应审计重新扫描

## 验收标准
- 目标文件 docs/03_modules/_cross_layer/llm-security/blueprint.md 的违规已修复
- D3 维度重新扫描无该 Finding 重现

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 回滚 | git checkout -- docs/03_modules/_cross_layer/llm-security/blueprint.md |

---
*创建: 2026-05-09 09:42 | 更新: 2026-05-09 09:42*
*本文件由 create_task_from_finding.py 自动生成（MOD-INF-006 TaskCard 格式）。*
