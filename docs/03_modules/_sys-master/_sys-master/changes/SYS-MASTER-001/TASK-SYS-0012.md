---

task_id: "TASK-SYS-0012"
source_blueprint: "SYS-MASTER-001"
source_section: "§17 测试策略金字塔 + §48 策略验证与统计严谨性"

title: "6层测试金字塔(Smoke→Chaos) + 策略验证3Gate(WFO/DSR/MTC Bonferroni)体系骨架"
description: |
  将 SYS-MASTER-001 §17 测试策略金字塔与 §48 策略验证统计严谨性工程化落地。
  §17: 6层测试金字塔——
  L0-Smoke(5min) / L1-Unit / L2-Integration / L3-E2E / L4-Regression / L5-Chaos。
  每层 avg_run_time/config/dataset/expected_pass_rate/ci_trigger。
  代码覆盖率目标: L1=80%+ / L2=75%+ / L3=60%+（关键路径非 cheap coverage）。
  §48: 策略验证三道门——
  G1-WFO(Walk-Forward Optimization): 纯 out-of-sample 检验。
  G2-DSR(Deflated Sharpe Ratio): 对多次试验的 Sharpe Ratio 进行校正。
  G3-MTC(Multiple Testing Correction): Bonferroni/Holm-Bonferroni/Benjamini-Hochberg。
  本卡搭建 test_strategy_registry.py + strategy_validator.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-closure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\test_strategy_registry.py"
    description: "§17 6层测试金字塔——每层 run_time/dataset/coverage_target/ci_trigger 配置"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\strategy_validator.py"
    description: "§48 WFO/DSR/MTC 三道门——Bonferroni/Holm-Bonferroni/Benjamini-Hochberg"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\test_strategy_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\strategy_validator.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§17 6层金字塔 L0-L5 + §48 G1-WFO/G2-DSR/G3-MTC 三道门槛"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 40

acceptance_criteria:
  - "TestLevel 枚举 6 成员 L0_SMOKE→L5_CHAOS——每成员含 avg_run_time_seconds/config/dataset/expected_pass_rate/ci_trigger"
  - "strategy_validator.py WFO: split(0.7)→train on [0:split], test on [split:]→out-of-sample Sharpe"
  - "DSR: N_trials×E[max Sharpe]→deflation factor→adjusted p-value"
  - "MTC: multi_comparison_correct(p_values[])—Bonferroni/Holm-Bonferroni/BH 三选项"

rollback_instructions: |
  git rm src/zephyr/governance/test_strategy_registry.py strategy_validator.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0003"
blocked_by: []
status: "created"
tags_fn:
  - "strategy"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
blueprint_id: DOM-GOV-001
---
