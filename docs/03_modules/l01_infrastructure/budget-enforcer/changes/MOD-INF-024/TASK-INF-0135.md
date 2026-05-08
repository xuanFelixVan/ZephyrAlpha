---
task_id: "TASK-INF-0135"
module_id: "MOD-INF-024"
title: "Unit Tests + Integration Tests — 30+ 组件全覆盖单元测试 + E2E 集成测试套件"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§4 + §5 (all components must be tested)"
estimated_tokens: 6000
estimated_time_minutes: 180
owner_signal_required: false
depends_on:
  - "TASK-INF-0101~0134"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\tests\\test_budget_tracker.py"
  - "D:\\ZephyrAlpha\\tests\\test_pre_flight_gate.py"
  - "D:\\ZephyrAlpha\\tests\\test_model_router.py"
  - "D:\\ZephyrAlpha\\tests\\test_degradation_manager.py"
  - "D:\\ZephyrAlpha\\tests\\test_action_history.py"
  - "D:\\ZephyrAlpha\\tests\\test_semantic_cache.py"
  - "D:\\ZephyrAlpha\\tests\\test_burn_rate_monitor.py"
  - "D:\\ZephyrAlpha\\tests\\test_cost_attributor.py"
  - "D:\\ZephyrAlpha\\tests\\test_roi_calculator.py"
  - "D:\\ZephyrAlpha\\tests\\test_pricing_sync.py"
  - "D:\\ZephyrAlpha\\tests\\test_stream_abort_guard.py"
  - "D:\\ZephyrAlpha\\tests\\test_output_quality_gate.py"
  - "D:\\ZephyrAlpha\\tests\\test_budget_profile_manager.py"
  - "D:\\ZephyrAlpha\\tests\\test_policy_sandbox.py"
  - "D:\\ZephyrAlpha\\tests\\test_context_waste_detector.py"
  - "D:\\ZephyrAlpha\\tests\\test_instruction_bloat_detector.py"
  - "D:\\ZephyrAlpha\\tests\\test_conversation_tax_detector.py"
  - "D:\\ZephyrAlpha\\tests\\test_timeout_guard.py"
  - "D:\\ZephyrAlpha\\tests\\test_self_budget_tracker.py"
  - "D:\\ZephyrAlpha\\tests\\test_spiral_ews.py"
  - "D:\\ZephyrAlpha\\tests\\test_poison_cascade_detector.py"
  - "D:\\ZephyrAlpha\\tests\\test_parent_child_attributor.py"
  - "D:\\ZephyrAlpha\\tests\\test_think_time_model.py"
  - "D:\\ZephyrAlpha\\tests\\test_trust_ring_manager.py"
  - "D:\\ZephyrAlpha\\tests\\test_tamper_evident_log.py"
  - "D:\\ZephyrAlpha\\tests\\test_ipi_defense.py"
  - "D:\\ZephyrAlpha\\tests\\test_fail_mode_manager.py"
  - "D:\\ZephyrAlpha\\tests\\test_solo_maintainer.py"
  - "D:\\ZephyrAlpha\\tests\\test_budget_enforcer_integration.py"
acceptance_criteria:
  - "AC-01: 每个 src/zephyr/budget_enforcer/*.py 有对应 tests/test_*.py——29 个测试文件创建"
  - "AC-02: 每个 test 文件 ≥ 5 个 unit test cases"
  - "AC-03: BudgetTracker 测试覆盖——七级 consume + remaining + ratio + reset + thread safety"
  - "AC-04: PreFlightGate 测试——all 6 check cases + ALLOW/DENY/DEGRADE/BORROW/NARROW decisions"
  - "AC-05: DegradationManager 测试——6+ 级 chain triggers + anti-spiral + auto-recovery"
  - "AC-06: ModelRouter 测试——tier escalation + least-cost provider + batch eligibility + vendor fallback"
  - "AC-07: SemanticCache 测试——hit/miss for all 3 layers + TTL expiry + LRU eviction"
  - "AC-08: TamperEvidentLog 测试——append + verify + detect tamper + incorrect prev_hash + re-sign"
  - "AC-09: IPIDefense 测试——all 8 IPI patterns trigger correctly + false positive count < 5%"
  - "AC-10: AdversarialTestSuite 测试——5 vectors all pass + system returns to clean state"
  - "AC-11: 所有 unit test 用 pytest 标准 fixture——pytest.ini 配置 budget_enforcer mark"
  - "AC-12: intgration test CHECK 15 模块 connections + artifact written correctly"
  - "AC-13: test_coverage ≥ 85% line coverage——pytest-cov 集成"
  - "AC-14: CI 流水线 MOD-INF-009 Pipeline 集成所有 test suite——pass required for PR merge"
rollback_instructions: "删除 tests/ 目录下所有 budget_enforcer 测试文件。测试失去，但核心组件继续运行（无测试保护——相当于 v0.3.0 之前的状态）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1421-L1455 (§4 File list + §5 Phase planning)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\"
assigned_agent: any
tags: [unit-tests, integration-tests, 30-components, test-coverage, pytest, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0135: Unit Tests + Integration Tests — 30+ 组件全覆盖

## 1. 任务目标

为 Budget Enforcer 的 30 个源码组件编写完整单元测试（每个 ≥ 5 test cases），加上 E2E 集成测试套件验证全系统 15 模块与 Budget Enforcer 的交互正确性。目标覆盖率 ≥ 85%。

## 2. 背景

蓝图 §4 列出 30 个源文件 + 3 个配置文件。蓝图 §15 测试覆盖矩阵定义每种测试类型的覆盖目标。蓝图 §5 Phase 规划指向 MR 质量门禁：`pytest --coverage >= 85%`。

## 3. 产出物清单

| # | 测试文件 | 被测模块 |
|---|---------|---------|
| 1 | `tests/test_budget_tracker.py` | BudgetTracker |
| 2 | `tests/test_pre_flight_gate.py` | PreFlightGate |
| 3 | `tests/test_model_router.py` | ModelRouter |
| 4 | `tests/test_degradation_manager.py` | DegradationManager |
| 5 | `tests/test_action_history.py` | ActionHistory |
| 6 | `tests/test_semantic_cache.py` | SemanticCache |
| 7 | `tests/test_burn_rate_monitor.py` | BurnRateMonitor |
| 8 | `tests/test_cost_attributor.py` | CostAttributor |
| 9 | `tests/test_roi_calculator.py` | ROICalculator |
| 10 | `tests/test_pricing_sync.py` | PricingSync |
| 11 | `tests/test_stream_abort_guard.py` | StreamAbortGuard |
| 12 | `tests/test_output_quality_gate.py` | OutputQualityGate |
| 13 | `tests/test_budget_profile_manager.py` | BudgetProfileManager |
| 14 | `tests/test_policy_sandbox.py` | PolicySandbox |
| 15-28 | ... (14 more) | 其余 14 组件 |
| 29 | `tests/test_budget_enforcer_integration.py` | E2E integration |
