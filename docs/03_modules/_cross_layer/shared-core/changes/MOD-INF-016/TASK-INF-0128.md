---
task_id: "TASK-INF-0128"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §19 测试策略——集成测试 + 性能回归 + 漂移检测"

title: "§19 测试策略——集成测试 + 性能基准回归 + Policy 漂移检测"
description: |
  按蓝图 §19 的 Shared Layer 测试策略补充非单元测试层：
  1. 集成测试——consumer 模块（task-system/scripts/governance/etc.）与 shared/ 集成。
  2. 性能基准回归——pytest-benchmark 基准测试 retry/circuit_breaker/fallback 的 cpu/profile。
  3. Policy 漂移检测——每天两次 cron 日程跑 auto_contract_tester，验证契约与规约一致。
  4. metrics 可视化——所有性能/cost metrics 聚合可视化（--cov 默认输出 term → CSV）。
  实现要求：
  - 新增 `tests/integration/test_shared_integration.py`——测试 task-system 的 shared/ 消费。
  - 新增 `tests/benchmark/test_resilience_perf.py`——pytest-benchmark 性能回归。
  - 新增 `scripts/governance/policy_drift_detector.py`——cron 每日两次的 contract 漂移检查。
  专业对标：pytest-benchmark + ZephyrAlpha contract_auto_tester + Netflix ChaosMonkey drift detection。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fallback.py"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_shared_integration.py"
    description: "集成测试——task-system + scripts 与 shared/ 交互"
  - path: "D:\\ZephyrAlpha\\tests\\benchmark\\test_resilience_perf.py"
    description: "性能基准——retry/circuit_breaker/fallback 的 cpu 指标"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\policy_drift_detector.py"
    description: "漂移检测器——cron 每日两次 contract 漂移检查"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\integration\\test_shared_integration.py"
  - "D:\\ZephyrAlpha\\tests\\benchmark\\test_resilience_perf.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\policy_drift_detector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "GOV-TSK-004"
    section: "§3.1"
    reason: "集成测试门禁——所有集成测试必须通过才可推进"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §19——集成/性能/漂移检测策略"
  - file_path: "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
    reason: "test_import_chain.py——集成测试的 contract 依赖"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "test_shared_integration.py: 验证 task-system → shared/core/models 的 import 集成"
  - "test_shared_integration.py: 验证 scripts/governance/ 对 shared/ 的 ssot_agent + observer 消费"
  - "test_resilience_perf.py: pytest-benchmark 测试 run -> mean time <1ms & p95 <2ms"
  - "test_resilience_perf.py: 逐模块 perf——retry/circuit_breaker/fallback 独立基测"
  - "policy_drift_detector.py: 每日两次 cron 运行 + drift_alert 通知（max 2 alerts/day）"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\integration\test_shared_integration.py
  2. 删除 D:\ZephyrAlpha\tests\benchmark\test_resilience_perf.py
  3. 删除 D:\ZephyrAlpha\scripts\governance\policy_drift_detector.py

depends_on: ["TASK-INF-0127"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
