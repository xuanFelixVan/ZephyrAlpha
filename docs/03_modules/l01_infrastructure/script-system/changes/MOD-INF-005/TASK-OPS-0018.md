---
task_id: TASK-OPS-0018
module_id: MOD-INF-005
title: "False Negative 检测引擎落地 — §19 Golden Test Case库 B73 + B75 变异测试"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - false-negative
  - golden-test-case
  - mutation-testing
  - b17-b73-b75
description: |
  将蓝图 §19 False Negative 检测引擎（B17）的 Golden Test Case 库从"声明-未实现"状态落地。
  
  对标 B73（Golden Test Case 覆盖缺口——test_fixtures/ 目录未创建）：
  - D1/D3/D5/D6 四个高密度维度各创建 3 个 known-bad fixture
  - 优先从 P2→P1
  
  对标 B75（脚本变异测试——验证假阴性）：
  - 自动注入已知缺陷到健康文件→验证脚本能否检测
  - 对齐 pitest mutation testing 思想

acceptance_criteria:
  - "D1/D3/D5/D6 每个维度至少 3 个 Golden Test Case 在 meta/false_negative_cases/ 下"
  - "validate_false_negatives.py 对 Golden Test Case 库 exit 2（应检测到缺陷）"
  - "Golden Test Case 假阴性检测率 ≥ 90%"
  - "新增一个变异测试脚本——自动注入缺陷→验证脚本检测能力"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_false_negatives.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\false_negative_cases\\"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_mutation_testing.py"

rollback_instructions: "rm -rf scripts/governance/meta/false_negative_cases/"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§19.1", "§19.2", "§19.3"]

phase: phase_2_extend
effort_estimate: L
risk_level: HIGH
depends_on_task: ["TASK-OPS-0017"]
blocks_task: ["TASK-OPS-0019"]
related_blind_spots: ["B17", "B73", "B75", "B94"]
related_risks: ["R2"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0018: False Negative 检测引擎落地 — §19 Golden Test Case + 变异测试

## 1. 任务概述

B73 明确指出 Golden Test Case 库"尚未创建"——validate_false_negatives.py 的校验能力在空转（没有已知坏用例可验证）。加上 B75 变异测试——被动的假阴性检测（等历史数据异常）不够，需要主动注入缺陷验证检测能力。

## 2. 施工步骤

### Step 1: Golden Test Case 库（D1/D3/D5/D6）
创建 `D:\ZephyrAlpha\scripts\governance\meta\false_negative_cases\`：
- d1_structure_case_01: 目录结构但缺 index.md
- d1_structure_case_02: .py 在根目录（孤立 Python）
- d1_structure_case_03: 嵌套过深目录
- d3_metadata_case_01: frontmatter 缺 version 字段
- d3_metadata_case_02: invalid YAML frontmatter
- d3_metadata_case_03: frontmatter 中 status 值不在 enum
- d5_architecture_case_01: 循环 depends_on
- d5_architecture_case_02: 蓝图版本与注册表版本不匹配
- d5_architecture_case_03: Layer 跨越依赖
- d6_security_case_01: 硬编码 API key
- d6_security_case_02: dangerous shell command
- d6_security_case_03: 文件路径中含 secrets

### Step 2: validate_false_negatives.py 改造
扩展为自动扫描 Golden Test Case 库→逐一验证。

### Step 3: validate_mutation_testing.py
新建变异测试脚本：选取健康文件→自动注入缺陷→验证脚本能否检测。

## 3. 验收标准
- [ ] 12 个 Golden Test Case fixture 文件存在
- [ ] validate_false_negatives.py 检测率 ≥ 90%
- [ ] mutation_testing.py 可运行——健康文件→注入缺陷→检测成功
