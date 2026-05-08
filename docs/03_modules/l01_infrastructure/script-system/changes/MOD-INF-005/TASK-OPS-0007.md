---
task_id: TASK-OPS-0007
module_id: MOD-INF-005
title: "任务系统集成接口落地 — §6 脚本失败→任务阻塞 + Finding→任务卡自动创建 + recommendation字段"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - task-system
  - integration
  - finding
  - recommendation
  - gate
description: |
  将蓝图 §6 的与任务系统（MOD-INF-006）集成接口全部落地。
  
  覆盖子节：
  - §6.1 集成模式：脚本失败→任务阻塞（G0-G7 门禁体系映射）
  - §6.2 状态转换映射：exit 0→正常 / exit 1→WARNING / exit 2→BLOCKED / exit 3→全部BLOCKED
  - §6.3 Finding→任务卡自动创建：CRITICAL→P0自动 / HIGH→P1自动 / MEDIUM→手动
  - §6.4 task_id 格式约定：OPS-{SEQ} 命名空间
  - §6.5 Finding Schema 新增字段：recommendation / recommendation_type / recommended_action

acceptance_criteria:
  - "CRITICAL/HIGH Finding 产生后 60s 内自动创建 OPS-XXX 任务卡"
  - "exit 3（脚本崩溃）触发所有活跃任务 BLOCKED"
  - "Finding Schema JSONL 输出包含 recommendation / recommendation_type / recommended_action 三个字段"
  - "MEDIUM Finding 创建的任务卡包含 recommendation 字段内容"
  - "OPS-{SEQ} 任务卡的 task_id 格式符合 MOD-INF-006 §3.2.1 规范"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\script_system\\finding.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\create_task_from_finding.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\script_system\\finding.py"

rollback_instructions: "git checkout -- scripts/governance/meta/create_task_from_finding.py src/zephyr/l01_infrastructure/script_system/finding.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§6.1", "§6.2", "§6.3", "§6.4", "§6.5"]
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    sections: ["§3.2.1", "§4", "§5"]

phase: phase_1_core
effort_estimate: L
risk_level: HIGH
depends_on_task: ["TASK-OPS-0006"]
blocks_task: ["TASK-OPS-0008"]
related_blind_spots: ["B12", "B63"]
related_risks: ["R1"]
related_contracts: ["CT-Task-Integration"]
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0007: 任务系统集成接口落地 — §6 脚本失败→任务阻塞 + Finding→任务卡自动创建

## 1. 任务概述

蓝图 §6 定义了脚本系统与任务系统 MOD-INF-006 的集成接口——脚本发现违规时自动将关联任务置为 BLOCKED，并为 CRITICAL/HIGH Finding 自动创建修复任务卡。这是闭合整个治理回路的关键环节。

## 2. 施工步骤

### Step 1: create_task_from_finding.py
新建 `D:\ZephyrAlpha\scripts\governance\meta\create_task_from_finding.py`：
- 读取 run_all.py 产出的 findings.jsonl
- CRITICAL Finding → 自动创建 OPS-{SEQ} 任务卡（P0）
- HIGH Finding → 自动创建 OPS-{SEQ} 任务卡（P1）
- MEDIUM Finding → 输出建议但不自动创建
- 任务卡的 description 包含 finding_id + evidence + detected_at

### Step 2: Finding Schema recommendation 字段
在 `finding.py` 的 Finding Schema 中新增三个字段：
- `recommendation`: string — 修复建议
- `recommendation_type`: enum(auto_fixable/manual_only/needs_review)
- `recommended_action`: enum(modify_file/create_task/consult_owner/ignore)

### Step 3: 状态转换映射集成
在 run_all.py 中集成：
- exit 0/1 → 任务系统不操作
- exit 2 → 关联任务 BLOCKED
- exit 3 → 所有活跃任务 BLOCKED

## 3. 验收标准
- [ ] CRITICAL Finding 自动创建 P0 任务卡
- [ ] HIGH Finding 自动创建 P1 任务卡
- [ ] Finding JSONL 包含三个 recommendation 字段
- [ ] exit 3 触发全量 BLOCKED
- [ ] OPS 任务格式符合 MOD-INF-006 规范
