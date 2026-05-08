---
task_id: TASK-OPS-0016
module_id: MOD-INF-005
title: "Shadow Mode 渐进激活验证 — §17 Phase1-3三阶段 + 自动回退20%FPR + sleeper attack防御(B98)"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - shadow-mode
  - progressive-rollout
  - auto-rollback
description: |
  验证蓝图 §17 Shadow Mode 渐进激活机制（B19）。
  
  - §17.1 三阶段流程：Phase1(Shadow,7d,exit 0,不阻断)→Phase2(Warn,7d,exit 1,不阻断)→Phase3(Active,永久,按实际,阻断)
  - §17.2 自动回退：假阳性>20%→回退Phase1→rollback_count+1→连续3次→自动禁用(Kill Switch)
  - §17.3 管理工具：manage_shadow_mode.py --register / --promote / --check-health --auto-promote / --rollback
  - 额外防御：B98 Shadow Mode 定时炸弹（sleeper attack）→ Phase3激活后检测脚本逻辑变更频率

acceptance_criteria:
  - "manage_shadow_mode.py --register 后新脚本进入 Phase1——产出 [SHADOW] 标记"
  - "manage_shadow_mode.py --promote ×2 → Phase3——正式阻断"
  - "--check-health --auto-promote 可在满足条件时自动晋级"
  - "假阳性 > 20% → 自动回退 + rollback_count 增加——3次→自动禁用"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\manage_shadow_mode.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\shadow_mode_state.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.yaml"

downstream_outputs: []

rollback_instructions: "python scripts/governance/meta/manage_shadow_mode.py --rollback <script> --reason '手动回退'"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§17.1", "§17.2", "§17.3"]

phase: phase_2_extend
effort_estimate: M
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0015"]
blocks_task: ["TASK-OPS-0017"]
related_blind_spots: ["B19", "B98"]
related_risks: []
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0016: Shadow Mode 渐进激活验证 — §17 端到端测试

## 1. 任务概述

Shadow Mode 机制（已施工 B19）必须经过端到端验证——register→promote→check-health→rollback 四步骤全链路。

## 2. 施工步骤

### Step 1: register→promote 全流程
模拟一个脚本的三阶段晋升流程。

### Step 2: 假阳性触发自动回退
模拟假阳性率 > 20% → 验证自动回退到 Phase1。

### Step 3: 连续回退 3 次→Kill Switch
验证 rollback_count 累加→3 次→自动 Kill Switch per-script。

## 3. 验收标准
- [ ] Phase1/2/3 行为差异正确（Shadow/Warn/Active 三种 exit 策略）
- [ ] 自动回退在假阳性 > 20% 时触发
- [ ] 连续 3 次回退→自动禁用
