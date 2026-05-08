---
task_id: TASK-OPS-0023
module_id: MOD-INF-005
title: "操作陷阱备忘录落地 — §34 七项工程陷阱逐一防御脚本"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - operational-traps
  - absolute-path
  - dependency-lock
  - import-pollution
description: |
  将蓝图 §34 操作陷阱备忘录的 7 项工程陷阱逐一落地。
  
  §34.1 绝对路径硬编码陷阱：`D:\ZephyrAlpha\...`→换盘符全崩 → detect_absolute_path_hardcoding.py
  §34.2 依赖版本锁定缺口：`pyyaml>=6.0` 非精确 → validate_frozen_requirements.py
  §34.3 同进程import污染：run_all.py→import→全局状态污染 → validate_process_isolation.py
  §34.4 SLA指标"待测量"：已在 TASK-OPS-0009（sla_metrics.jsonl）
  §34.5 部分扫描虚假安全感：[ChainGuard]标签 + run_all.py 部分扫描显式警告
  §34.6 脚本-蓝图版本漂移：generate_script_manifest.py 自动注入 compatible_blueprint_version
  §34.7 AI Session间交接损耗：OPS任务卡 description 含 finding_id+evidence+detected_at+git SHA

acceptance_criteria:
  - "detect_absolute_path_hardcoding.py → grep D:\\\\ZephyrAlpha 所有治理脚本→exit 2 如存在"
  - "validate_frozen_requirements.py → 对比current freeze vs frozen-versions.txt→diff→WARNING"
  - "run_all.py 部分扫描时 → ⚠ PARTIAL SCAN + ⚠ UNCHECKED dimensions 显式警告"
  - "generate_script_manifest.py → 自动读蓝图frontmatter→填入 compatible_blueprint_version → manifest"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\generators\\generate_script_manifest.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\requirements\\"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\d7_code\\detect_absolute_path_hardcoding.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d11_compliance\\validate_frozen_requirements.py"

rollback_instructions: "git checkout -- scripts/governance/d7_code/detect_absolute_path_hardcoding.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§34.1", "§34.2", "§34.3", "§34.4", "§34.5", "§34.6", "§34.7"]

phase: phase_3_systematize
effort_estimate: M
risk_level: LOW
depends_on_task: ["TASK-OPS-0022"]
blocks_task: ["TASK-OPS-0024"]
related_blind_spots: ["B81", "B83", "B87"]
related_risks: []
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0023: 操作陷阱备忘录落地 — §34 七项工程陷阱逐一防御

## 1. 任务概述

§34 的 7 项操作陷阱不是新盲点——而是"实际操作中一定会踩到"的工程陷阱。需要为每项建立预防脚本。

## 2. 施工步骤

### Step 1: §34.1 — 绝对路径硬编码检测
新建 `D:\ZephyrAlpha\scripts\governance\d7_code\detect_absolute_path_hardcoding.py`：
- 扫描 scripts/governance/ 下全部 .py
- grep `D:\\ZephyrAlpha` → 找到硬编码→ report HIGH Finding
- 排除本蓝图引用

### Step 2: §34.2 — 依赖版本锁定
新建 frozen-versions.txt + validate_frozen_requirements.py。

### Step 3: §34.5 — Part Scan Warning
run_all.py --dimensions d1,d3 时自动输出"⚠ UNCHECKED: D5,D6,D7,..." 警告。

### Step 4: §34.6 — 版本漂移预防
generate_script_manifest.py 自动读蓝图 frontmatter version→填入 compatible_blueprint_version。

## 3. 验收标准
- [ ] detect_absolute_path_hardcoding.py 对所有治理脚本 exit 0
- [ ] frozen-versions.txt 存在
- [ ] 部分扫描→显式警告
- [ ] manifest 自动含 compatible_blueprint_version
