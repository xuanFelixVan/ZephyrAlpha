---
task_id: TASK-OPS-0026
module_id: MOD-INF-005
title: "产出物存放 + 集成目标 + 需更新内容 联合落地 — 蓝图尾部三个标准模板节"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - output-directory
  - integration
  - cross-reference
description: |
  将蓝图尾部三个标准模板节（产出物存放目录 + 集成目标 + 需要更新的相关内容）落地。
  
  **产出物存放**：
  - 蓝图文件: D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\script-system\blueprint.md
  - 业务代码: D:\ZephyrAlpha\src\zephyr\script_system\
  - 治理脚本: D:\ZephyrAlpha\scripts\governance\
  - 脚本注册表: D:\ZephyrAlpha\scripts\governance\script_manifest.yaml
  
  **集成目标 3 项**：
  - Gate Engine (MOD-INF-007): run_all.py→gate_engine.evaluate()
  - Task System (MOD-INF-006): 脚本完成→task_repo.update_status()
  - Drift Detector (MOD-INF-023): 80+脚本→drift_detector 调度
  
  **需更新内容 2 项**：
  - blueprint-registry.yaml: 版本号+完整度
  - script_manifest.yaml: 新脚本注册

acceptance_criteria:
  - "产出物存放的 4 个路径全部在磁盘存在且有效"
  - "3 集成目标在各自模块蓝图中找到对应接口定义"
  - "blueprint-registry.yaml 中 MOD-INF-005 版本号与 blueprint.md frontmatter 一致"
  - "本批次分解后——新治理脚本入库→script_manifest.yaml 更新（TASK-OPS-0037）"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gate-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

rollback_instructions: "git checkout -- docs/03_modules/blueprint-registry.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["产出物存放目录", "集成目标", "需要更新的相关内容"]

phase: phase_3_systematize
effort_estimate: M
risk_level: LOW
depends_on_task: ["TASK-OPS-0025"]
blocks_task: []
related_blind_spots: ["B5", "B65"]
related_risks: []
related_contracts: ["CT-Gate-Engine", "CT-Task-System", "CT-Drift-Detector"]
card_type: verification
upstream_blueprint_version: "5.2.1"
autonomy_level: human_required
---

# TASK-OPS-0026: 产出物存放 + 集成目标 + 需更新内容 联合落地

## 1. 任务概述

蓝图尾部三个标准模板节是 ZephyrAlpha 蓝图体系的固定格式——产出物在哪里、集成到哪里、谁需要被更新。

## 2. 施工步骤

### Step 1: 产出物存放路径验证
逐项确认 4 个目录存在且有效。

### Step 2: 集成目标接口验证
- Gate Engine (MOD-INF-007): 确认其蓝图中定义 gate_engine.evaluate() 接口
- Task System (MOD-INF-006): 确认 task_repo.update_status() 存在
- Drift Detector (MOD-INF-023): 确认其蓝图引用脚本系统作为检测器来源

### Step 3: 需更新内容登记
本批次分解完成后：
- blueprint-registry.yaml 版本号核对
- script_manifest.yaml 新治理脚本注册

## 3. 验收标准
- [ ] 4 个产出物路径有效
- [ ] 3 个集成目标接口对接有效
- [ ] 需更新文件已登记
