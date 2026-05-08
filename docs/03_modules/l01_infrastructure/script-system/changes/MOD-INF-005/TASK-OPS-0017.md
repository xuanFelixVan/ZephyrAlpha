---
task_id: TASK-OPS-0017
module_id: MOD-INF-005
title: "Baseline Snapshot + Finding 全生命周期 + Error Budget 联合验证 — §18+§20+§21 三节闭环链路"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - baseline
  - finding-lifecycle
  - error-budget
  - sla
  - state-machine
description: |
  联合验证蓝图 §18（Baseline Snapshot）、§20（Finding 全生命周期状态机）、§21（Error Budget+Burn Rate）三条已施工机制的闭环。
  
  §18 Baseline：NEW/RESOLVED/PERSISTENT→PERSISTENT≥30d→升级严重度
  §20 Finding状态机：10状态(OPEN→IN_PROGRESS→FIXED→VERIFIED / FALSE_POSITIVE→CLOSED) + SLA定时器 + OVERDUE
  §21 Error Budget：双预算模型 + Critical/Warning Burn Rate Alert + Feature Freeze联动 + 依赖隔离

acceptance_criteria:
  - "manage_baseline.py --compare 输出 NEW/RESOLVED/PERSISTENT 三态分类"
  - "PERSISTENT MEDIUM≥30天→自动升级为 HIGH Finding"
  - "finding_state_machine.py --check-sla 输出 OVERDUE Finding 清单"
  - "manage_error_budget.py --status 输出当前 Error Budget 剩余 + Burn Rate"
  - "Error Budget耗尽→Feature Freeze→global_freeze(Kill Switch联动)→72h后自动解冻"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\manage_baseline.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\finding_state_machine.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\manage_error_budget.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\error_budget_state.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\kill_switch_state.yaml"

downstream_outputs: []

rollback_instructions: "python scripts/governance/meta/manage_error_budget.py --reset"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§18.1", "§18.2", "§18.3", "§20.1", "§20.2", "§20.3", "§21.1", "§21.2", "§21.3", "§21.4"]

phase: phase_2_extend
effort_estimate: L
risk_level: HIGH
depends_on_task: ["TASK-OPS-0016"]
blocks_task: ["TASK-OPS-0018"]
related_blind_spots: ["B14", "B18", "B20", "B21", "B22", "B55", "B96", "B97"]
related_risks: ["R1", "R2"]
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0017: Baseline+Finding Lifecycle+Error Budget 联合验证 — §18+§20+§21 闭环自洽

## 1. 任务概述

§18/§20/§21 三条机制形成治理闭环：Baseline界定问题范围→Finding状态机追踪修复进度→Error Budget控制修复节奏。已施工但需端到端验证——尤其是 Error Budget→Kill Switch 联动。

## 2. 施工步骤

### Step 1: Baseline Comparison
```bash
python scripts/governance/meta/manage_baseline.py --compare <findings.jsonl> --json
```
验证输出包含 NEW/RESOLVED/PERSISTENT 三态。

### Step 2: Finding SLA 检查
```bash
python scripts/governance/meta/finding_state_machine.py --load <findings.jsonl>
python scripts/governance/meta/finding_state_machine.py --check-sla
```
验证 OVERDUE Finding 被标记且严重度按 §20.2 SLA 定时器递增。

### Step 3: Error Budget → Feature Freeze 联动
```bash
python scripts/governance/meta/manage_error_budget.py --status --json
```
验证 Burn Rate Alert + Feature Freeze + Kill Switch global_freeze 联动。

### Step 4: 依赖隔离验证
验证三维度分池（轻量D1-D4 / 中量D5-D8,D11 / 重量D9,D10,D12）隔离有效性。

## 3. 验收标准
- [ ] Baseline compare 三态输出正确
- [ ] PERSISTENT ≥ 30d → 升级严重度
- [ ] SLA 超时→OVERDUE
- [ ] Error Budget→Kill Switch 联动生效
- [ ] 依赖隔离各池独立运行
