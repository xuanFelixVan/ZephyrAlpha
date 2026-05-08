---
task_id: "TASK-INF-0129"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 治理信息 — SSoT 声明 + 变更记录"

title: "维护版本管理——变更记录更新 + 版本号推进 + SSoT 声明确认"
description: |
  维护蓝图 治理信息中的变更记录和 SSoT 声明。
  变更记录当前的 sparklines 索引正确——5条记录覆盖 v0.1.0→v0.6.0。
  SSoT 声明更新——确认与当前蓝图内容一致。
  合同版本号 0.6.0 确认——契约与蓝图版本对齐。
  确保移除 未检测到的信息（Closed items）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    description: "治理信息 + 变更记录——SSoT 声明更新 + closed items 移除"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "治理信息"
    reason: "变更记录 sparklines—MUST 保持最新"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "治理信息部分——更新目标"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 20

acceptance_criteria:
  - "sparklines 含正确的 5 条变更记录——Δ→v0.6.0"
  - "SSoT 声明前后无矛盾之处"
  - "contract_version '0.6.0' 与契约版本一致"
  - "无 ’ 未检测到的 Closed items '残留"

rollback_instructions: |
  1. git checkout -- blueprint.md 恢复治理信息部分

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 维护版本管理——变更记录 + version + SSoT

## 目标

1. 变更记录 sparklines → 更新至 v0.6.0
2. SSoT 声明确认
3. contract_version 与蓝图版本对齐

## 执行步骤

### 读
- 蓝图治理信息

### 做
1. 更新变更记录——追加 v0.6.0 条目
2. 确认 contract_version = 0.6.0
3. 移除 Closed items

### 产
- blueprint.md（治理信息更新）

### 检
Manually review governance section of blueprint.md

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | diff | 仅修改治理信息 |
| 2 | build | 蓝图格式无损 |
