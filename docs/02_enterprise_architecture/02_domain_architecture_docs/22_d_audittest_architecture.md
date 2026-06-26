---
doc_type: architecture_view
title: D-AUDITTEST audit_test_suite架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 22_d_audittest / audit_test_suite 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示audit_test_suite（D-AUDITTEST）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 audit_test_suite（D-AUDITTEST）的模块分布。共 152 个模块 / 152 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (10 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   tests/test_audit_chain_verifier.py  [prototype]                │
│   tests/test_audit_orchestrator_e2e.py  [prototype]              │
│   tests/test_audit_self_healer_e2e.py  [prototype]               │
│   tests/test_legal_audit_chain.py  [prototype]                   │
│   tests/test_self_heal_agent.py  [prototype]                     │
│   tests/test_self_health_monitor.py  [prototype]                 │
│   tests/unit/audit_trail/__init__.py  [prototype]                │
│   tests/unit/audit_trail/test_audit_core.py  [prototype]         │
│   tests/unit/audit_trail/test_import_smoke_audit_trail.py  [p... │
│   tests/unit/resource_optimization/test_self_healing.py  [pro... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (142 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   tests/agent_rbac/test_rbac_auto_lifecycle.py  [production]     │
│   tests/e2e/test_mcp_full_lifecycle_e2e.py  [production]         │
│   tests/test_adversarial_extreme.py  [production]                │
│   tests/test_arbiter.py  [production]                            │
│   tests/test_auto_fix_autopilot.py  [production]                 │
│   tests/test_auto_fix_phase_manager.py  [production]             │
│   tests/test_auto_fix_red_blue.py  [production]                  │
│   tests/test_auto_runtime_e2e.py  [production]                   │
│   tests/test_auto_runtime_fle_integration.py  [production]       │
│   tests/test_budget_event_driven.py  [production]                │
│   tests/test_budget_lifecycle_e2e.py  [production]               │
│   tests/test_budget_shutdown.py  [production]                    │
│   tests/test_circadian_red_blue_drill.py  [production]           │
│   tests/test_conductor.py  [production]                          │
│   tests/test_f10_red_blue.py  [production]                       │
│   tests/test_f18_automation.py  [production]                     │
│   tests/test_f18_redblue.py  [production]                        │
│   tests/test_f1_event_trigger.py  [production]                   │
│   ...还有 124 个模块 / 124 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 152 个模块 / 152 modules）。

### L1 基础层 / Foundation Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | tests/test_audit_chain_verifier.py | tests/test_audit_chain_verifier.py | prototype | generated |
| 2 | tests/test_audit_orchestrator_e2e.py | tests/test_audit_orchestrator_e2e.py | prototype | deprecated |
| 3 | tests/test_audit_self_healer_e2e.py | tests/test_audit_self_healer_e2e.py | prototype | deprecated |
| 4 | tests/test_legal_audit_chain.py | tests/test_legal_audit_chain.py | prototype | generated |
| 5 | tests/test_self_heal_agent.py | tests/test_self_heal_agent.py | prototype | generated |
| 6 | tests/test_self_health_monitor.py | tests/test_self_health_monitor.py | prototype | generated |
| 7 | tests/unit/audit_trail/__init__.py | tests/unit/audit_trail/__init__.py | prototype | deprecated |
| 8 | tests/unit/audit_trail/test_audit_core.py | tests/unit/audit_trail/test_audit_cor... | prototype | generated |
| 9 | tests/unit/audit_trail/test_import_smoke_audit_trail.py | tests/unit/audit_trail/test_import_sm... | prototype | generated |
| 10 | tests/unit/resource_optimization/test_self_healing.py | tests/unit/resource_optimization/test... | prototype | generated |

### 未分类 / Unclassified (142 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | tests/agent_rbac/test_rbac_auto_lifecycle.py | tests/agent_rbac/test_rbac_auto_lifec... | production | generated |
| 2 | tests/e2e/test_mcp_full_lifecycle_e2e.py | tests/e2e/test_mcp_full_lifecycle_e2e.py | production | generated |
| 3 | tests/test_adversarial_extreme.py | tests/test_adversarial_extreme.py | production | generated |
| 4 | tests/test_arbiter.py | tests/test_arbiter.py | production | generated |
| 5 | tests/test_auto_fix_autopilot.py | tests/test_auto_fix_autopilot.py | production | generated |
| 6 | tests/test_auto_fix_phase_manager.py | tests/test_auto_fix_phase_manager.py | production | generated |
| 7 | tests/test_auto_fix_red_blue.py | tests/test_auto_fix_red_blue.py | production | generated |
| 8 | tests/test_auto_runtime_e2e.py | tests/test_auto_runtime_e2e.py | production | generated |
| 9 | tests/test_auto_runtime_fle_integration.py | tests/test_auto_runtime_fle_integrati... | production | generated |
| 10 | tests/test_budget_event_driven.py | tests/test_budget_event_driven.py | production | generated |
| 11 | tests/test_budget_lifecycle_e2e.py | tests/test_budget_lifecycle_e2e.py | production | generated |
| 12 | tests/test_budget_shutdown.py | tests/test_budget_shutdown.py | production | generated |
| 13 | tests/test_circadian_red_blue_drill.py | tests/test_circadian_red_blue_drill.py | production | generated |
| 14 | tests/test_conductor.py | tests/test_conductor.py | production | generated |
| 15 | tests/test_f10_red_blue.py | tests/test_f10_red_blue.py | production | generated |
| 16 | tests/test_f18_automation.py | tests/test_f18_automation.py | production | generated |
| 17 | tests/test_f18_redblue.py | tests/test_f18_redblue.py | production | generated |
| 18 | tests/test_f1_event_trigger.py | tests/test_f1_event_trigger.py | production | generated |
| 19 | tests/test_f21_auto_run.py | tests/test_f21_auto_run.py | production | generated |
| 20 | tests/test_f21_auto_shutdown.py | tests/test_f21_auto_shutdown.py | production | generated |
| 21 | tests/test_f21_auto_startup.py | tests/test_f21_auto_startup.py | production | generated |
| 22 | tests/test_f21_event_driven.py | tests/test_f21_event_driven.py | production | generated |
| 23 | tests/test_f5_auto_shutdown.py | tests/test_f5_auto_shutdown.py | production | generated |
| 24 | tests/test_f5_auto_startup.py | tests/test_f5_auto_startup.py | production | generated |
| 25 | tests/test_f5_e2e_lifecycle.py | tests/test_f5_e2e_lifecycle.py | production | generated |
| 26 | tests/test_f5_event_startup.py | tests/test_f5_event_startup.py | production | generated |
| 27 | tests/test_f5_red_team_extreme.py | tests/test_f5_red_team_extreme.py | production | generated |
| 28 | tests/test_fl_safety_gate_l28_l29.py | tests/test_fl_safety_gate_l28_l29.py | production | generated |
| 29 | tests/test_fl_safety_gate_l36_l37.py | tests/test_fl_safety_gate_l36_l37.py | production | generated |
| 30 | tests/test_fl_safety_gate_l38_l39.py | tests/test_fl_safety_gate_l38_l39.py | production | generated |
| 31 | tests/test_fl_safety_gate_l40_l41.py | tests/test_fl_safety_gate_l40_l41.py | production | generated |
| 32 | tests/test_fl_safety_gate_l42_l43.py | tests/test_fl_safety_gate_l42_l43.py | production | generated |
| 33 | tests/test_fl_safety_gate_l44_l45.py | tests/test_fl_safety_gate_l44_l45.py | production | generated |
| 34 | tests/test_fl_safety_gate_l46_l47.py | tests/test_fl_safety_gate_l46_l47.py | production | generated |
| 35 | tests/test_fl_safety_gate_l48_l49.py | tests/test_fl_safety_gate_l48_l49.py | production | generated |
| 36 | tests/test_fl_safety_gate_l50_l51.py | tests/test_fl_safety_gate_l50_l51.py | production | generated |
| 37 | tests/test_fl_safety_gate_l52_l53.py | tests/test_fl_safety_gate_l52_l53.py | production | generated |
| 38 | tests/test_fl_safety_gate_l54_l55.py | tests/test_fl_safety_gate_l54_l55.py | production | generated |
| 39 | tests/test_fl_safety_gate_l56_l57.py | tests/test_fl_safety_gate_l56_l57.py | production | generated |
| 40 | tests/test_fl_safety_gate_l58_l59.py | tests/test_fl_safety_gate_l58_l59.py | production | generated |
| 41 | tests/test_fl_safety_gate_l60_l61.py | tests/test_fl_safety_gate_l60_l61.py | production | generated |
| 42 | tests/test_fl_safety_gate_l62_l63.py | tests/test_fl_safety_gate_l62_l63.py | production | generated |
| 43 | tests/test_fl_safety_gate_l64_l65.py | tests/test_fl_safety_gate_l64_l65.py | production | generated |
| 44 | tests/test_fl_safety_gate_l66_l67.py | tests/test_fl_safety_gate_l66_l67.py | production | generated |
| 45 | tests/test_g_trae_003.py | tests/test_g_trae_003.py | production | generated |
| 46 | tests/test_g_trae_004.py | tests/test_g_trae_004.py | production | generated |
| 47 | tests/test_g_trae_006.py | tests/test_g_trae_006.py | production | generated |
| 48 | tests/test_g_trae_007.py | tests/test_g_trae_007.py | production | generated |
| 49 | tests/test_g_trae_008.py | tests/test_g_trae_008.py | production | generated |
| 50 | tests/test_g_trae_009.py | tests/test_g_trae_009.py | production | generated |
| 51 | tests/test_g_trae_010.py | tests/test_g_trae_010.py | production | generated |
| 52 | tests/test_g_trae_011.py | tests/test_g_trae_011.py | production | generated |
| 53 | tests/test_g_trae_012.py | tests/test_g_trae_012.py | production | generated |
| 54 | tests/test_g_trae_016.py | tests/test_g_trae_016.py | production | generated |
| 55 | tests/test_g_trae_017.py | tests/test_g_trae_017.py | production | generated |
| 56 | tests/test_g_trae_018.py | tests/test_g_trae_018.py | production | generated |
| 57 | tests/test_g_trae_020.py | tests/test_g_trae_020.py | production | generated |
| 58 | tests/test_g_trae_021.py | tests/test_g_trae_021.py | production | generated |
| 59 | tests/test_g_trae_022.py | tests/test_g_trae_022.py | production | generated |
| 60 | tests/test_g_trae_023.py | tests/test_g_trae_023.py | production | generated |
| 61 | tests/test_g_trae_024.py | tests/test_g_trae_024.py | production | generated |
| 62 | tests/test_g_trae_025.py | tests/test_g_trae_025.py | production | generated |
| 63 | tests/test_g_trae_026.py | tests/test_g_trae_026.py | production | generated |
| 64 | tests/test_g_trae_027.py | tests/test_g_trae_027.py | production | generated |
| 65 | tests/test_g_trae_028.py | tests/test_g_trae_028.py | production | generated |
| 66 | tests/test_g_trae_029.py | tests/test_g_trae_029.py | production | generated |
| 67 | tests/test_g_trae_030.py | tests/test_g_trae_030.py | production | generated |
| 68 | tests/test_g_trae_031.py | tests/test_g_trae_031.py | production | generated |
| 69 | tests/test_g_trae_032.py | tests/test_g_trae_032.py | production | generated |
| 70 | tests/test_g_trae_033.py | tests/test_g_trae_033.py | production | generated |
| 71 | tests/test_g_trae_034.py | tests/test_g_trae_034.py | production | generated |
| 72 | tests/test_g_trae_035.py | tests/test_g_trae_035.py | production | generated |
| 73 | tests/test_g_trae_036.py | tests/test_g_trae_036.py | production | generated |
| 74 | tests/test_g_trae_037.py | tests/test_g_trae_037.py | production | generated |
| 75 | tests/test_g_trae_038.py | tests/test_g_trae_038.py | production | generated |
| 76 | tests/test_g_trae_039.py | tests/test_g_trae_039.py | production | generated |
| 77 | tests/test_g_trae_040.py | tests/test_g_trae_040.py | production | generated |
| 78 | tests/test_g_trae_041.py | tests/test_g_trae_041.py | production | generated |
| 79 | tests/test_g_trae_042.py | tests/test_g_trae_042.py | production | generated |
| 80 | tests/test_g_trae_043.py | tests/test_g_trae_043.py | production | generated |
| 81 | tests/test_g_trae_044.py | tests/test_g_trae_044.py | production | generated |
| 82 | tests/test_g_trae_045.py | tests/test_g_trae_045.py | production | generated |
| 83 | tests/test_g_trae_046.py | tests/test_g_trae_046.py | production | generated |
| 84 | tests/test_g_trae_047.py | tests/test_g_trae_047.py | production | generated |
| 85 | tests/test_g_trae_048.py | tests/test_g_trae_048.py | production | generated |
| 86 | tests/test_g_trae_049.py | tests/test_g_trae_049.py | production | generated |
| 87 | tests/test_g_trae_050.py | tests/test_g_trae_050.py | production | generated |
| 88 | tests/test_g_trae_051.py | tests/test_g_trae_051.py | production | generated |
| 89 | tests/test_g_trae_052.py | tests/test_g_trae_052.py | production | generated |
| 90 | tests/test_g_trae_053.py | tests/test_g_trae_053.py | production | generated |
| 91 | tests/test_g_trae_054.py | tests/test_g_trae_054.py | production | generated |
| 92 | tests/test_g_trae_055.py | tests/test_g_trae_055.py | production | generated |
| 93 | tests/test_ide_health_daemon.py | tests/test_ide_health_daemon.py | production | generated |
| 94 | tests/test_l00_data_source.py | tests/test_l00_data_source.py | production | generated |
| 95 | tests/test_l02_alpha_factor.py | tests/test_l02_alpha_factor.py | production | generated |
| 96 | tests/test_l03_signal_generation.py | tests/test_l03_signal_generation.py | production | generated |
| 97 | tests/test_l04_risk_management.py | tests/test_l04_risk_management.py | production | generated |
| 98 | tests/test_l05_portfolio_construction.py | tests/test_l05_portfolio_construction.py | production | generated |
| 99 | tests/test_l06_trade_execution.py | tests/test_l06_trade_execution.py | production | generated |
| 100 | tests/test_l07_post_trade_analytics.py | tests/test_l07_post_trade_analytics.py | production | generated |
| 101 | tests/test_l08_human_ai_interface.py | tests/test_l08_human_ai_interface.py | production | generated |
| 102 | tests/test_l09_research_innovation.py | tests/test_l09_research_innovation.py | production | generated |
| 103 | tests/test_l10_compliance.py | tests/test_l10_compliance.py | production | generated |
| 104 | tests/test_l11_ml_platform.py | tests/test_l11_ml_platform.py | production | generated |
| 105 | tests/test_l13_experimentation.py | tests/test_l13_experimentation.py | production | generated |
| 106 | tests/test_lock_release_uncommitted.py | tests/test_lock_release_uncommitted.py | production | generated |
| 107 | tests/test_mcp_launcher.py | tests/test_mcp_launcher.py | production | generated |
| 108 | tests/test_phase_executor_rule_enforcement.py | tests/test_phase_executor_rule_enforc... | production | generated |
| 109 | tests/test_pipeline_orchestrator_auto.py | tests/test_pipeline_orchestrator_auto.py | production | generated |
| 110 | tests/test_post_doc_review.py | tests/test_post_doc_review.py | production | generated |
| 111 | tests/test_red_blue_validator_tests.py | tests/test_red_blue_validator_tests.py | production | generated |
| 112 | tests/test_safety_gate_l28_l29.py | tests/test_safety_gate_l28_l29.py | production | generated |
| 113 | tests/test_safety_gate_l36_l37.py | tests/test_safety_gate_l36_l37.py | production | generated |
| 114 | tests/test_safety_gate_l38_l39.py | tests/test_safety_gate_l38_l39.py | production | generated |
| 115 | tests/test_safety_gate_l40_l41.py | tests/test_safety_gate_l40_l41.py | production | generated |
| 116 | tests/test_safety_gate_l42_l43.py | tests/test_safety_gate_l42_l43.py | production | generated |
| 117 | tests/test_safety_gate_l44_l45.py | tests/test_safety_gate_l44_l45.py | production | generated |
| 118 | tests/test_safety_gate_l46_l47.py | tests/test_safety_gate_l46_l47.py | production | generated |
| 119 | tests/test_safety_gate_l48_l49.py | tests/test_safety_gate_l48_l49.py | production | generated |
| 120 | tests/test_safety_gate_l50_l51.py | tests/test_safety_gate_l50_l51.py | production | generated |
| 121 | tests/test_safety_gate_l52_l53.py | tests/test_safety_gate_l52_l53.py | production | generated |
| 122 | tests/test_safety_gate_l54_l55.py | tests/test_safety_gate_l54_l55.py | production | generated |
| 123 | tests/test_safety_gate_l56_l57.py | tests/test_safety_gate_l56_l57.py | production | generated |
| 124 | tests/test_safety_gate_l58_l59.py | tests/test_safety_gate_l58_l59.py | production | generated |
| 125 | tests/test_safety_gate_l60_l61.py | tests/test_safety_gate_l60_l61.py | production | generated |
| 126 | tests/test_safety_gate_l62_l63.py | tests/test_safety_gate_l62_l63.py | production | generated |
| 127 | tests/test_safety_gate_l64_l65.py | tests/test_safety_gate_l64_l65.py | production | generated |
| 128 | tests/test_safety_gate_l66_l67.py | tests/test_safety_gate_l66_l67.py | production | generated |
| 129 | tests/test_task_repo_auto_commit.py | tests/test_task_repo_auto_commit.py | production | generated |
| 130 | tests/test_trading_session_lifecycle.py | tests/test_trading_session_lifecycle.py | production | generated |
| 131 | tests/test_validate_rule_frontmatter_red_blue.py | tests/test_validate_rule_frontmatter_... | production | generated |
| 132 | tests/unit/feedback_loop/test_scheduler_integration.py | tests/unit/feedback_loop/test_schedul... | production | generated |
| 133 | tests/unit/pipeline/conftest.py | tests/unit/pipeline/conftest.py | production | generated |
| 134 | tests/unit/telemetry/test_l12_telemetry.py | tests/unit/telemetry/test_l12_telemet... | production | generated |
| 135 | tests/unit/test_concurrency_guard.py | tests/unit/test_concurrency_guard.py | production | generated |
| 136 | tests/unit/test_context_pipeline_auto.py | tests/unit/test_context_pipeline_auto.py | production | generated |
| 137 | tests/unit/test_l08_interface.py | tests/unit/test_l08_interface.py | production | generated |
| 138 | tests/unit/test_l12_telemetry_unit.py | tests/unit/test_l12_telemetry_unit.py | production | generated |
| 139 | tests/unit/vector_memory/test_vms_adversarial_hijack.py | tests/unit/vector_memory/test_vms_adv... | production | generated |
| 140 | tests/unit/vector_memory/test_vms_adversarial_injection.py | tests/unit/vector_memory/test_vms_adv... | production | generated |
| 141 | tests/unit/vector_memory/test_vms_automation.py | tests/unit/vector_memory/test_vms_aut... | production | generated |
| 142 | tests/unit/vector_memory/test_vms_lifecycle.py | tests/unit/vector_memory/test_vms_lif... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `22_d_audittest_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
