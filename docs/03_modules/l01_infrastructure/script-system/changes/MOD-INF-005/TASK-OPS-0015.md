---
task_id: TASK-OPS-0015
module_id: MOD-INF-005
title: "Kill Switch 机制验证 — §16 双层保护 + kill_switch_state.yaml + run_all.py 集成点"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - kill-switch
  - global-freeze
  - disaster-recovery
description: |
  验证蓝图 §16 Kill Switch 机制（B25）的完整性。
  
  - §16.1 双层保护：global_freeze（Error Budget耗尽/Owner手动）+ per-script禁用（手动/连续N次失败）
  - §16.2 执行机制：run_all.py→kill_switch_state.yaml→每脚本前检查→global_freeze拒绝新脚本(exit2)/per-script跳过
  - §16.3 管理工具：manage_kill_switch.py --list / --disable / --enable

acceptance_criteria:
  - "manage_kill_switch.py --list 能列出当前 kill_switch_state.yaml 中所有条目"
  - "global_freeze=true 时——run_all.py 拒绝执行所有新脚本（exit 2）——现有脚本仍可执行"
  - "per-script 禁用——脚本被跳过并记录 KILL-SWITCH 事件到 findings"
  - "Kill Switch 联动 Error Budget Feature Freeze（§21.3）"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\manage_kill_switch.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\kill_switch_state.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"

downstream_outputs: []

rollback_instructions: "python scripts/governance/meta/manage_kill_switch.py --enable <script>"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§16.1", "§16.2", "§16.3"]

phase: phase_2_extend
effort_estimate: M
risk_level: HIGH
depends_on_task: ["TASK-OPS-0014"]
blocks_task: ["TASK-OPS-0016"]
related_blind_spots: ["B25", "B66"]
related_risks: ["R5"]
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: human_required
---

# TASK-OPS-0015: Kill Switch 机制验证 — §16 双层保护端到端测试

## 1. 任务概述

Kill Switch 是脚本系统的"紧急刹车"——它必须可工作、可测试、可回退。manage_kill_switch.py 已实现但需验证端到端集成。

## 2. 施工步骤

### Step 1: per-script 禁用→验证跳过
```bash
python scripts/governance/meta/manage_kill_switch.py --disable d7_code/validate_import_style.py --reason "测试"
python scripts/governance/run_all.py --dimensions d7
# 验证 validate_import_style 被跳过 + KILL-SWITCH event 日志输出
python scripts/governance/meta/manage_kill_switch.py --enable d7_code/validate_import_style.py
```

### Step 2: global_freeze→验证拒绝
```bash
python scripts/governance/meta/manage_kill_switch.py --freeze --reason "测试冻结"
python scripts/governance/run_all.py --dry-run
# 验证所有新脚本标记 [FROZEN]
python scripts/governance/meta/manage_kill_switch.py --unfreeze
```

### Step 3: Error Budget→Kill Switch 联动验证
模拟 Error Budget 耗尽 → Feature Freeze → global_freeze 自动设置。

## 3. 验收标准
- [ ] Per-script 禁用生效——脚本被跳过
- [ ] Global freeze 生效——新脚本拒绝执行
- [ ] 解冻后恢复正常
- [ ] KILL-SWITCH 事件记录到 findings JSONL
