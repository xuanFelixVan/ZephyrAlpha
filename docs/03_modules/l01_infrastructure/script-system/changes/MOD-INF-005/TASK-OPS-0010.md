---
task_id: TASK-OPS-0010
module_id: MOD-INF-005
title: "施工 Phase 执行规划 — §10 MVP固态化 + 扩展覆盖 + 系统化 Phase 门禁"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - phases
  - construction
  - milestones
description: |
  将蓝图 §10 的三层 Phase 规划转化为可跟踪和可验收的里程碑任务卡。
  
  覆盖：
  - §10 最小闭环 MVP（已完成）: D1-D5 Finding Schema统一 + 全部注册 + pre-commit + 四档退出码
  - §10 扩展覆盖（施工中 6项 Backlog）: C2分类器 / D6安全深度 / C3报告生成 / D12幻觉v1 / Finding→任务卡(P0) / C5→C1反馈闭环
  - §10 系统化（5项 Backlog）: C4修复跟踪 / C5知识沉淀 / SQLite存储 / entity-graph / 里程碑门禁(NASA SRR→PD→CDR→TRR→SAR)

acceptance_criteria:
  - "本蓝图全部 37 张分解任务卡的 Phase 归属与 §10 三层规划一致"
  - "扩展覆盖 6 项中 P0（Finding→任务卡）= TASK-OPS-0007 已完成关联"
  - "§10 系统化 5 项在 status.py --json 中有对应的 Backlog 条目"
  - "NASA 里程碑门禁矩阵在 meta/milestone_gate_matrix.yaml 中定义"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\milestone_gate_matrix.yaml"

rollback_instructions: "git checkout -- scripts/governance/meta/milestone_gate_matrix.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§10"]

phase: phase_2_extend
effort_estimate: S
risk_level: LOW
depends_on_task: ["TASK-OPS-0009"]
blocks_task: ["TASK-OPS-0011"]
related_blind_spots: ["B13"]
related_risks: ["R6"]
related_contracts: []
card_type: planning
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0010: 施工 Phase 执行规划 — §10 MVP固态化 + Backlog 门禁

## 1. 任务概述

蓝图 §10 定义了从 MVP→扩展覆盖→系统化的三层施工路径。当前处于 phase_1_partial。需要将三层规划映射到具体任务卡的 Phase 字段，并为系统化层建立 NASA-STD-8739.8B 对齐的里程碑门禁矩阵。

## 2. 施工步骤

### Step 1: 本蓝图全部任务卡 Phase 分类
逐卡验证 phase 字段与 §10 规划一致：
- phase_0_setup → MOD-INF-005 蓝图验证（TASK-OPS-0001/0002/0003）
- phase_1_core → 核心机制（§3-§7）
- phase_2_extend → 扩展覆盖（§8-§15）

### Step 2: §10 P0 项已关联验证
确认 §10 唯一的 P0 项（Finding→任务卡自动创建）已有 TASK-OPS-0007。

### Step 3: milestone_gate_matrix.yaml
新建 `D:\ZephyrAlpha\scripts\governance\meta\milestone_gate_matrix.yaml`：
- 对齐 NASA SRR→PDR→CDR→TRR→SAR 五门禁
- 每门禁定义：触发时机 + 需通过的脚本清单 + 不通过后果

## 3. 验收标准
- [ ] 所有分解任务卡 Phase 归属与 §10 一致
- [ ] §10 P0 项 TASK-OPS-0007 完整关联
- [ ] milestone_gate_matrix.yaml 存在且有效
