---
task_id: TASK-OPS-0013
module_id: MOD-INF-005
title: "蓝图-代码同步验证 — §14 路径索引 80+文件 + validate_blueprint_code_sync.py 零漂移"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - path-index
  - blueprint-code-sync
  - drift-detection
description: |
  验证蓝图 §14（已实现代码完整路径索引）与磁盘实际状态一致。§14.1-§14.6 声明了 ~80 个文件的实现状态（✅已实现/❌未实现/⚠️骨架）。任何不一致 = 蓝图漂移 = 下一个 AI session 被误导。
  
  关键项：
  - §14.1 源码: finding.py ✅
  - §14.4 治理脚本: ~80个（含 d5_architecture/validate_blueprint_overlap.py ❌未实现）
  - §14.5 Meta自检: 19个（全 ✅）
  - §14.6 共享工具: thresholds.yaml + QUICKSTART.md ✅

acceptance_criteria:
  - "validate_blueprint_code_sync.py 对 §14 全部条目 exit 0——每个文件路径的 actual exists 与 ✗/⚠️ status 匹配"
  - "validate_blueprint_implementation_docs.py 对蓝图文件 exit ≤ 1"
  - "validate_three_way_consistency.py 对本蓝图→manifest→磁盘 exit 0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\validate_blueprint_code_sync.py"

downstream_outputs: []

rollback_instructions: "无需回滚——本任务卡仅验证不一致"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§14.1", "§14.4", "§14.5", "§14.6"]

phase: phase_2_extend
effort_estimate: M
risk_level: HIGH
depends_on_task: ["TASK-OPS-0012"]
blocks_task: ["TASK-OPS-0014"]
related_blind_spots: ["B83", "B106"]
related_risks: ["R3"]
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0013: 蓝图-代码同步验证 — §14 80+路径索引零漂移

## 1. 任务概述

蓝图 §14 声明了 ~80 个文件的实现状态。按 AGENTS.md §6.14 蓝图-代码同步强制约定——蓝图声称的文件必须与磁盘实际一致。

## 2. 施工步骤

### Step 1: validate_blueprint_code_sync.py 运行
```bash
python scripts/governance/d5_architecture/validate_blueprint_code_sync.py
```
检查 exit code。如有 ❌→ 标记 Finding。

### Step 2: validate_three_way_consistency.py
```bash
python scripts/governance/d5_architecture/validate_three_way_consistency.py
```
三方（蓝图§14↔script_manifest.yaml↔磁盘）一致性验证。

### Step 3: 标记"未实现"项验证
确认 §14.4 中唯一的 ❌ 项（validate_blueprint_overlap.py）确实不存在：
- d5_architecture/validate_blueprint_overlap.py → ❌ 磁盘不存在 ✓ 蓝图声明正确

但实际上 d11_compliance/validate_blueprint_overlap.py 已实现（§14.4 D11段）。

## 3. 验收标准
- [ ] validate_blueprint_code_sync.py exit 0
- [ ] validate_three_way_consistency.py exit 0
- [ ] 所有 ✅ 文件在磁盘存在
- [ ] 所有 ❌ 文件在磁盘不存在（d5版本）或已替换实现（d11版本）
