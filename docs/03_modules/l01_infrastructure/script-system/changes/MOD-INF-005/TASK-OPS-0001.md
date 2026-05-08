---
task_id: TASK-OPS-0001
module_id: MOD-INF-005
title: "模块骨架搭建 — MOD-INF-005 script-system 蓝图合法性验证与注册"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - blueprint
  - module-registration
  - ssot
description: |
  验证 MOD-INF-005 蓝图在模块注册表中的合法性并完成模块骨架搭建。
  
  本任务卡是 script-system 蓝图的零号任务卡——在开始任何脚本系统施工前，必须确认：
  1. module_id MOD-INF-005 在 `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` 中已注册
  2. 蓝图 frontmatter 与 `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` 中定义的 28 字段 TaskCard 真源一致
  3. 蓝图 SSoT 声明与 script_manifest.yaml 一致
  4. 蓝图 dependencies 声明中的 5 个前置模块（MOD-INF-001/003/004/006、MOD-KB-001）均存在
  5. 蓝图版本号 5.2.1 与蓝图注册表 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` 一致
  
  对标蓝图 §1（概述与模块定位）、§2（必备链接与依赖声明）、治理信息（SSoT 声明）。

acceptance_criteria:
  - "module-registry.yaml 中存在 module_id: MOD-INF-005 条目，layer=L01, functional_domain=infra"
  - "blueprint-registry.yaml 中 MOD-INF-005 版本号为 5.2.1"
  - "蓝图 frontmatter 28 字段与 metadata-registry.md META-V 验证通过"
  - "5 个 dependencies 模块在 module-registry.yaml 中均为 Active 状态"
  - "蓝图 SSoT 声明与 script_manifest.yaml 的 total_scripts 值一致"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\module-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

downstream_outputs:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\module-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"

rollback_instructions: "git checkout -- docs/03_modules/module-registry.yaml docs/03_modules/blueprint-registry.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§1.1", "§1.2", "§1.5", "§2.2", "治理信息"]
  - source: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    sections: ["TaskCard 28 字段定义"]
  - source: "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
    sections: ["total_scripts"]

phase: phase_0_setup
effort_estimate: S
risk_level: LOW
depends_on_task: []
blocks_task: ["TASK-OPS-0002", "TASK-OPS-0003"]
related_blind_spots: []
related_risks: []
related_contracts: []
card_type: setup
upstream_blueprint_version: "5.2.1"
autonomy_level: human_required
---

# TASK-OPS-0001: 模块骨架搭建 — MOD-INF-005 script-system 蓝图合法性验证与注册

## 1. 任务概述

验证 MOD-INF-005 蓝图在 ZephyrAlpha 模块注册体系中的合法性。这是所有后续任务卡的前置条件——如果模块注册不合法，后续任务卡均无立足点。

## 2. 施工步骤

### Step 1: module-registry.yaml 验证
运行 `D:\ZephyrAlpha\scripts\governance\d3_metadata\validate_blueprint_registry.py`，确认 MOD-INF-005 存在且状态为 Active。

### Step 2: frontmatter 合规验证
运行 `D:\ZephyrAlpha\scripts\governance\d3_metadata\check_frontmatter_metadata.py` 检查蓝图 frontmatter，确保 28 字段均符合 metadata-registry.md 定义。

### Step 3: depends_on 链验证
运行 `D:\ZephyrAlpha\scripts\governance\d5_architecture\validate_depends_on_format.py` 检查蓝图 frontmatter dependencies 中的 5 个模块是否均在 module-registry.yaml 中。

### Step 4: 版本一致性验证
对比 blueprint.md frontmatter 中的 version: 5.2.1 与 blueprint-registry.yaml 中 MOD-INF-005 的版本号。

## 3. 验收标准
- [ ] module-registry.yaml 中 MOD-INF-005 条目合法
- [ ] 蓝图 frontmatter 通过 META-V 验证
- [ ] 5 个 dependencies 模块存在且 Active
- [ ] blueprint-registry.yaml 版本号 = 5.2.1
- [ ] 所有验证脚本 exit ≤ 1
