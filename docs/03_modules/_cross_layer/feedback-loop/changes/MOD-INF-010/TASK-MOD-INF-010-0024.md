---
task_id: TASK-MOD-INF-010-0024
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§3 L28-L41 (v0.14.0-v0.20.0)", "§2.206 L36&L37", "§2.210 L38&L39", "§2.222 L40&L41"]
status: pending
priority: P0
created_date: 2026-05-06
assigned_to: null
depends_on: ["TASK-MOD-INF-010-0023"]
blocked_by: []
blocks: ["TASK-MOD-INF-010-0025"]
estimated_effort_hours: 20
actual_effort_hours: null
tags: [safety-gates, L28-L41, DR-readiness, supply-chain, ai-integrity, deterministic, architectural]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_L28_L29.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_L36_L37.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_L38_L39.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_L40_L41.py
acceptance_criteria:
  - AC-0024-01: L28 (DR Readiness): DR drill < 90d → 允许 action, 超期→阻止 REPAIR
  - AC-0024-02: L29 (Supply Chain): active exploit CVE → 仅 NOTIFY_OWNER; skill_trust < 0.5 → 全block
  - AC-0024-03: L36 (AI Code Integrity): context_rot > 35% + dilution > 0.3 → context refresh
  - AC-0024-04: L37 (Vibe Maintainability): worsening > 0.4 → 仅 NOTIFY_OWNER; trust_decay > baseline×1.5 → L0
  - AC-0024-05: L38 (Deterministic Safety): HARD_BLOCK violated → BLOCK; SOFT_BLOCK → NEED_OVERRIDE
  - AC-0024-06: L39 (Architectural Integrity): degradation > 5%/月 → BLOCK SELF_UPGRADE; cyclical_deps > 5 → BLOCK
  - AC-0024-07: L40 (Self-Integrity): immutable core violation → BLOCK; operational_window prohibited → BLOCK
  - AC-0024-08: L41 (Meta-Health): health_composite < TH → OBSERVE_ONLY; edge_case_regression fail → BLOCK UPGRADE
rollback_instructions: |
  1. 删除 4 个 safety gate 文件
  2. 回滚 safety gate pipeline registry
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-§3-L28L41
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§3 L28-L41"]
      description: 扩展安全层——v0.14.0到v0.20.0引入的安全门
  assembly_notes: L28-L41 的代码已在蓝图 §2.206, §2.210, §2.222 中以完整 Python 形式给出。
---

# TASK-MOD-INF-010-0024: Safety Gates L28-L41 实现

## 1. 任务目标
将蓝图 §2.206、§2.210、§2.222 中的 L28-L41 安全门 Python 代码块转化为实际文件。

## 2. 文件-门映射
| 文件 | 门 |
|------|-----|
| safety_gate_L28_L29.py | L28(DR), L29(SupplyChain) |
| safety_gate_L36_L37.py | L36(AI Integrity), L37(Vibe Maintainability) |
| safety_gate_L38_L39.py | L38(Deterministic), L39(Architectural) |
| safety_gate_L40_L41.py | L40(Self-Integrity), L41(Meta-Health) |

## 3. 实现要点
- 直接从蓝图复制代码块并适配 import 路径
- 每层返回 GateVerdict — 一方 REJECT → 阻止 action
