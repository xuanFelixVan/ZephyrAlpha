---
task_id: TASK-OPS-0011
module_id: MOD-INF-005
title: "风险矩阵 R1-R12 缓解方案落地 — §12+§26 全部12项风险逐一缓解任务卡"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - risks
  - mitigation
  - r1-r12
description: |
  将蓝图 §12.1（R1-R6）和 §26（R6-R12）的全部 12 项风险逐一转化为可验证的缓解任务。
  
  R1: 审计疲劳 — 严重度分级 + CRITICAL 24h处理
  R2: 沉默失败 — exit 3阻断（已施工于B10）
  R3: 审计脚本自身bug — 三件套入库验证
  R4: AI自我修改 — Immutable层（Finding Schema只读）
  R5: 单人项目瓶颈 — 多模型交叉验证（Claude审GLM、Opus审Claude）
  R6: 过度工程 — 分阶段rollout（P0→P1→P2）
  R7: Excessive Agency — trust_tier_policy.yaml + validate_trust_tier.py
  R8: Slopsquatting — detect_hallucinated_packages.py PyPI验证
  R9: 脚本静默失效 — detect_script_rot.py 每扫描周期
  R10: Finding矛盾 — arbitrate_findings.py 5规则
  R11: 系统退化 — validate_end_to_end_benchmark.py
  R12: Token费用失控 — track_script_costs.py per-call tracking

acceptance_criteria:
  - "R1-R12 每条风险在 meta/risk_mitigation_matrix.yaml 中有缓解脚本映射"
  - "R7-R12 的缓解脚本在 script_manifest.yaml 中全部已注册"
  - "run_all.py --tags Critical 包含全部 P0 风险缓解脚本"
  - "R5 多模型交叉验证有 session log 记录"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\risk_mitigation_matrix.yaml"

rollback_instructions: "git checkout -- scripts/governance/meta/risk_mitigation_matrix.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§12.1", "§26"]

phase: phase_2_extend
effort_estimate: M
risk_level: HIGH
depends_on_task: ["TASK-OPS-0010"]
blocks_task: ["TASK-OPS-0012"]
related_blind_spots: ["B2", "B10", "B92", "B93"]
related_risks: ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12"]
related_contracts: []
card_type: risk
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0011: 风险矩阵 R1-R12 缓解方案落地

## 1. 任务概述

蓝图共定义了 12 项风险（§12.1 的 R1-R6 + §26 的 R6-R12）。R6 在两处均有出现——§12.1 聚焦"过度工程"、§26 聚焦"Rules File Backdoor"。每项风险必须有 ≥1 条缓解策略和 ≥1 个可运行的缓解脚本。

## 2. 施工步骤

### Step 1: risk_mitigation_matrix.yaml
新建 `D:\ZephyrAlpha\scripts\governance\meta\risk_mitigation_matrix.yaml`，逐项记录：
- R1→validate_finding_severity.py（严重度强制分级）
- R2→run_all.py exit-code约定（已内置）
- R3→validate_script_onboarding.py（TASK-OPS-0005）
- R4→validate_automation_boundary.py（TASK-OPS-0002）
- R5→validate_cross_model_consensus.py（B53已施工）
- R6(过度工程)→phase rollout gating（TASK-OPS-0010 miletone gates）
- R6(供应链)→validate_rules_file_backdoor.py + validate_rules_integrity.py
- R7→trust_tier_policy.yaml + validate_trust_tier.py
- R8→detect_hallucinated_packages.py
- R9→detect_script_rot.py
- R10→arbitrate_findings.py
- R11→validate_end_to_end_benchmark.py
- R12→track_script_costs.py

### Step 2: R7-R12 缓解脚本注册验证
逐项检查 §26 中声明的 6 个缓解脚本是否在 script_manifest.yaml 中已注册。

## 3. 验收标准
- [ ] 12 条风险逐条有缓解脚本映射
- [ ] R7-R12 缓解脚本已在 manifest 注册
- [ ] risk_mitigation_matrix.yaml 存在且内容完整
