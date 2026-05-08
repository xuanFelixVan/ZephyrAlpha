---
task_id: TASK-OPS-0008
module_id: MOD-INF-005
title: "脚本质量标准强制落地 — §7 核心 MUST 条款 + quality-standard.md 引用完整性"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - quality-standards
  - encoding
  - self-consistency
  - integration
description: |
  将蓝图 §7 的脚本质量标准转化为可自动验证的检查。
  
  覆盖：
  - §7.1 引用 SCRIPT-QUALITY-001（8维度×38条款，22 MUST + 16 SHOULD）
  - §7.2 核心 MUST 条款落地（10条 MUST）：
    - ENC-001: 文件 UTF-8
    - ENC-002: sys.stdout.reconfigure(encoding='utf-8')
    - ENC-003: open() 必须 encoding='utf-8'
    - SC-001: 内部路径绝对路径
    - SC-002: docstring 覆盖参数/返回值/副作用
    - SC-007: shebang
    - SC-005: 脚本不修改自己
    - INT-001: 四档退出码
    - INT-002: 异常全捕获→exit 3
    - INT-003: --warn-only → exit 0/1
  - §7.3 质量标准基线的变更控制

acceptance_criteria:
  - "d11_compliance/validate_script_quality.py 覆盖 10 条核心 MUST"
  - "d7_code/detect_missing_encoding.py 检测所有 open() 是否含 encoding='utf-8'"
  - "quality-standard.md 的 22 MUST + 16 SHOULD 均有可追溯的验证脚本"
  - "质量标准变更控制纳入 validate_threshold_changes.py 审计范围"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\quality-standard.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d11_compliance\\validate_script_quality.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\d11_compliance\\validate_script_quality.py"

rollback_instructions: "git checkout -- scripts/governance/d11_compliance/validate_script_quality.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§7.1", "§7.2", "§7.3"]
  - source: "D:\\ZephyrAlpha\\scripts\\governance\\quality-standard.md"
    sections: ["全部"]

phase: phase_1_core
effort_estimate: M
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0007"]
blocks_task: ["TASK-OPS-0009"]
related_blind_spots: ["B88", "B89"]
related_risks: ["R3"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0008: 脚本质量标准强制落地 — §7 核心 MUST 条款验证

## 1. 任务概述

蓝图 §7 引用 SCRIPT-QUALITY-001（quality-standard.md）作为脚本质量的真源。当前 validate_script_quality.py 已实现，但需要确保它与蓝图 §7.2 中列出的 10 条核心 MUST 完全对应，每条有可追溯的检查逻辑。

## 2. 施工步骤

### Step 1: validate_script_quality.py 覆盖审计
- 确认 10 条 MUST 均有对应检查逻辑
- ENC-001/002/003（编码安全 3 条）：detect_missing_encoding.py 覆盖
- SC-001/002/007/005（自身一致 4 条）：validate_script_quality.py 覆盖
- INT-001/002/003（集成接口 3 条）：run_all.py 运行验证覆盖

### Step 2: quality-standard.md 条款索引
生成 quality-standard.md 的 38 条款→验证脚本映射表，写入 `meta/quality_enforcement_matrix.yaml`。

### Step 3: 编码安全检查强化
扩展 `d7_code/detect_missing_encoding.py`：
- 不仅检查 `open()` 调用，还需检查 `Path().write_text()` 等替代 API
- 检查 `[System.IO.File]::WriteAllText` PowerShell 调用中的编码参数

## 3. 验收标准
- [ ] 10 条核心 MUST 全部有验证脚本覆盖
- [ ] quality_enforcement_matrix.yaml 存在且与 quality-standard.md 一致
- [ ] detect_missing_encoding.py 对所有治理脚本 exit 0
- [ ] 新增脚本如违反 MUST → 自动拒绝入库
