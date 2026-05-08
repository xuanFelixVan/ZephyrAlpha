---
task_id: TASK-OPS-0004
module_id: MOD-INF-005
title: "脚本分类体系落地 — §3 三轴分类（维度×退出码×触发方式）+ 前缀+层级+标签"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - classification
  - dimensions
  - exit-codes
  - taxonomy
description: |
  将蓝图 §3 的多轴脚本分类体系落地为 script_manifest.yaml 的可验证字段和 run_all.py 的调度逻辑。
  
  分类体系包含 6 层分类轴：
  - §3.1 审计维度（D1-D12 + Root + Meta + Gen）：主分类轴，14 个分类节点
  - §3.2 退出码分类（0/1/2/3）：四档退出码约定 + 混合四档/三档模型
  - §3.3 触发方式（pre-commit/run_all/独立/CI）：4 种触发方式
  - §3.4 前缀约定（validate_/detect_/audit_/check_/register_）：5 种前缀
  - §3.5 自动化层级（L1/L2/L3）：ITIL 对齐的三级递进
  - §3.6 标签分类（Quick/Security/Disruptive/Critical/AI-Generated/Periodic）：6 种标签

acceptance_criteria:
  - "script_manifest.yaml 中每个脚本条目包含 dimension/exit_code_convention/trigger/prefix/automation_level/tags 六个字段"
  - "run_all.py --dimensions d1,d3,d5 能按维度过滤执行"
  - "run_all.py --tags Security,Quick 能按标签过滤执行"
  - "run_all.py --depth quick 只执行 Quick 标签脚本"
  - "validate_script_prefix.py 检测脚本文件名是否遵守前缀约定"
  - "script_manifest.yaml 中每个脚本条目包含 version 字段（§3.6 待办项——对标 OWASP ASVS 唯一标识符+版本追溯）"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.yaml"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\d1_structure\\validate_index_reality.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d3_metadata\\check_naming_convention.py"

rollback_instructions: "git checkout -- scripts/governance/script_manifest.yaml scripts/governance/run_all.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§3.1", "§3.2", "§3.3", "§3.4", "§3.5", "§3.6"]
  - source: "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
    sections: ["全部条目"]

phase: phase_1_core
effort_estimate: L
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0002"]
blocks_task: ["TASK-OPS-0005"]
related_blind_spots: ["B95", "B106"]
related_risks: ["R1", "R6"]
related_contracts: ["CT-Plugin-v1.0"]
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0004: 脚本分类体系落地 — §3 三轴分类 + 前缀 + 层级 + 标签

## 1. 任务概述

蓝图 §3 定义了脚本的多层分类体系。当前 script_manifest.yaml 已包含 dimensions 字段，但缺少 §3.2 退出码约定映射、§3.5 L1/L2/L3 自动化层级标注、§3.6 标签体系。需要补全 manifest schema 并确保 run_all.py 能按所有分类轴过滤执行。

## 2. 施工步骤

### Step 1: manifest schema 扩展
在 script_manifest.yaml 的条目 schema 中新增字段：
- `version`: string（§3.6待办——对标OWASP ASVS每个需求有唯一标识符+版本追溯）
- `automation_level`: enum(L1/L2/L3) — §3.5 ITIL 对齐
- `tags`: list[str] — §3.6 六种标签
- `exit_code_convention`: enum(three_tier/four_tier) — §3.2 混合模型
- `trigger`: list[enum] — §3.3 触发方式

### Step 2: run_all.py 多轴过滤
扩展 run_all.py 参数：
- `--dimensions d1,d3,d5` —已有
- `--tags Security,Quick` —新增（对标 §3.6）
- `--depth quick/full/deep` —新增（对标 §3.5 L1/L2/L3）
- `--trigger pre-commit` —新增

### Step 3: 前缀验证脚本
新建 `D:\ZephyrAlpha\scripts\governance\d1_structure\validate_script_prefix.py`：
- 扫描 scripts/governance/d*/ 下所有 .py 文件
- 验证文件名匹配 5 种前缀（validate_/detect_/audit_/check_/register_）之一
- 不符合 → exit 2 阻断

### Step 4: 维度覆盖自检
在 `status.py --json` 中新增维度覆盖率输出：
- D1-D12 各维度的脚本数 + 覆盖率百分比
- D10（0 个脚本）标记为 `dimension_vacant`

## 3. 验收标准
- [ ] manifest schema 包含 6 个新字段（version + automation_level + tags + exit_code_convention + trigger）
- [ ] run_all.py --tags 和 --depth 参数有效
- [ ] validate_script_prefix.py 对所有脚本 exit 0
- [ ] status.py --json 输出维度覆盖率
- [ ] 新 manifest 字段由 generate_script_manifest.py 自动生成
