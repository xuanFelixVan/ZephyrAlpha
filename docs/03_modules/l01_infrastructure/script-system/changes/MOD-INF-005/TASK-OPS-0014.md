---
task_id: TASK-OPS-0014
module_id: MOD-INF-005
title: "关键阈值配置与变更审计 — §15 thresholds.yaml SSoT + 8大阈值组 + validate_threshold_changes.py"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - thresholds
  - configuration
  - audit
  - ai-autonomy
description: |
  验证蓝图 §15 的关键阈值外置配置体系完整性。
  
  - §15.1 设计原则：所有阈值集中在 thresholds.yaml——不硬编码在任何脚本中
  - §15.2 八大阈值组：scanning / finding_quality / error_budget / sla_timers / shadow_mode / script_health / ast_similarity / blueprint_sync
  - §15.3 变更审计：每次修改→validate_threshold_changes.py→meta/threshold_changes_audit.jsonl
  - §15.4 AI自治权限：AI可读不可写——修改需Owner审批，纳入D11合规审计

acceptance_criteria:
  - "thresholds.yaml 包含 8 大阈值组的完整结构"
  - "sh/thresholds.py get() 函数能按路径读取任意阈值"
  - "validate_threshold_changes.py 能在 thresholds.yaml 变更后自动生成审计 JSONL"
  - "任一治理脚本硬编码阈值（如 if rate > 0.05）→ detect_hardcoded_thresholds.py 报告"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\thresholds.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_threshold_changes.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\threshold_changes_audit.jsonl"

rollback_instructions: "git checkout -- scripts/governance/_shared/thresholds.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§15.1", "§15.2", "§15.3", "§15.4"]

phase: phase_2_extend
effort_estimate: S
risk_level: LOW
depends_on_task: ["TASK-OPS-0013"]
blocks_task: ["TASK-OPS-0015"]
related_blind_spots: ["B9", "B16", "B104"]
related_risks: []
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0014: 关键阈值配置与变更审计 — §15 thresholds.yaml 8大阈值组

## 1. 任务概述

蓝图 §15 要求所有关键阈值外置于 thresholds.yaml（已实现），变更审计自动生成 JSONL。需要验证 8 大阈值组完整性和 AI 自治权限落地。

## 2. 施工步骤

### Step 1: 8 大阈值组结构完整性验证
读取 thresholds.yaml，验证 8 组结构完整：
- scanning / finding_quality / error_budget / sla_timers / shadow_mode / script_health / ast_similarity / blueprint_sync

### Step 2: thresholds.py get() 功能验证
```python
from thresholds import get
assert get("shadow_mode.auto_rollback_fpr_threshold") == 0.20
```

### Step 3: threshold_changes_audit.jsonl 生成
手动修改 thresholds.yaml→validate_threshold_changes.py→验证 jsonl 包含 old→new diff。

## 3. 验收标准
- [ ] 8 大阈值组结构完整
- [ ] get() 可读取任意路径
- [ ] 变更审计 JSONL 自动生成
- [ ] AI 只读协议 → thresholds.yaml 纳入 D11 检查
