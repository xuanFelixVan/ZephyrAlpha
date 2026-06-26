---
doc_type: architecture_view
title: D-AUTONOMY_PERM 自治保护架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 23_d_autonomy_perm / 自治保护 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示自治保护（D-AUTONOMY_PERM）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 自治保护（D-AUTONOMY_PERM）的模块分布。共 70 个模块 / 70 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (70 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/runtime/kill_switch_state.yaml  [production]            │
│   docs__03_modules___domain_autonomy_core__agent_rbac__bluepr... │
│   src/zephyr/autonomy_perm/__init__.py  [prototype]              │
│   src/zephyr/autonomy_perm/_extensions/__init__.py  [prototype]  │
│   src/zephyr/autonomy_perm/api/__init__.py  [prototype]          │
│   src/zephyr/autonomy_perm/core/__init__.py  [prototype]         │
│   src/zephyr/autonomy_perm/infrastructure/__init__.py  [proto... │
│   src/zephyr/autonomy_perm/models/__init__.py  [prototype]       │
│   src/zephyr/autonomy_perm/red_blue_validator/__init__.py  [p... │
│   src/zephyr/autonomy_perm/red_blue_validator/attack_registry... │
│   src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder... │
│   src/zephyr/autonomy_perm/red_blue_validator/constitution_gu... │
│   src/zephyr/autonomy_perm/red_blue_validator/convergence_che... │
│   src/zephyr/autonomy_perm/red_blue_validator/defense_runner.... │
│   src/zephyr/autonomy_perm/red_blue_validator/game_day_runner... │
│   src/zephyr/autonomy_perm/services/__init__.py  [prototype]     │
│   src/zephyr/governance/agent_signer.py  [prototype]             │
│   src/zephyr/security/access_control/governance_bridges/__ini... │
│   ...还有 52 个模块 / 52 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 70 个模块 / 70 modules）。

### L1 基础层 / Foundation Layer (70 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/runtime/kill_switch_state.yaml | config/runtime/kill_switch_state.yaml | production | deprecated |
| 2 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprin... | docs__03_modules___domain_autonomy_co... | design | planned |
| 3 | src/zephyr/autonomy_perm/__init__.py | src/zephyr/autonomy_perm/__init__.py | prototype | deprecated |
| 4 | src/zephyr/autonomy_perm/_extensions/__init__.py | src/zephyr/autonomy_perm/_extensions/... | prototype | deprecated |
| 5 | src/zephyr/autonomy_perm/api/__init__.py | src/zephyr/autonomy_perm/api/__init__.py | prototype | deprecated |
| 6 | src/zephyr/autonomy_perm/core/__init__.py | src/zephyr/autonomy_perm/core/__init_... | prototype | deprecated |
| 7 | src/zephyr/autonomy_perm/infrastructure/__init__.py | src/zephyr/autonomy_perm/infrastructu... | prototype | deprecated |
| 8 | src/zephyr/autonomy_perm/models/__init__.py | src/zephyr/autonomy_perm/models/__ini... | prototype | deprecated |
| 9 | src/zephyr/autonomy_perm/red_blue_validator/__init__.py | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 10 | src/zephyr/autonomy_perm/red_blue_validator/attack_regist... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 11 | src/zephyr/autonomy_perm/red_blue_validator/bypass_record... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 12 | src/zephyr/autonomy_perm/red_blue_validator/constitution_... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 13 | src/zephyr/autonomy_perm/red_blue_validator/convergence_c... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 14 | src/zephyr/autonomy_perm/red_blue_validator/defense_runne... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 15 | src/zephyr/autonomy_perm/red_blue_validator/game_day_runn... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 16 | src/zephyr/autonomy_perm/services/__init__.py | src/zephyr/autonomy_perm/services/__i... | prototype | deprecated |
| 17 | src/zephyr/governance/agent_signer.py | src/zephyr/governance/agent_signer.py | prototype | generated |
| 18 | src/zephyr/security/access_control/governance_bridges/__i... | src/zephyr/security/access_control/go... | prototype | stable |
| 19 | src/zephyr/security/access_control/governance_bridges/a2a... | src/zephyr/security/access_control/go... | prototype | stable |
| 20 | src/zephyr/security/access_control/governance_bridges/app... | src/zephyr/security/access_control/go... | prototype | stable |
| 21 | src/zephyr/security/access_control/governance_bridges/boo... | src/zephyr/security/access_control/go... | production | stable |
| 22 | src/zephyr/security/access_control/governance_bridges/cap... | src/zephyr/security/access_control/go... | prototype | stable |
| 23 | src/zephyr/security/access_control/governance_bridges/con... | src/zephyr/security/access_control/go... | prototype | stable |
| 24 | tests/agent_rbac/__init__.py | tests/agent_rbac/__init__.py | prototype | generated |
| 25 | tests/agent_rbac/conftest.py | tests/agent_rbac/conftest.py | prototype | generated |
| 26 | tests/agent_rbac/test_abac_guard_agent_rbac.py | tests/agent_rbac/test_abac_guard_agen... | prototype | generated |
| 27 | tests/agent_rbac/test_adversarial_agent_rbac.py | tests/agent_rbac/test_adversarial_age... | prototype | generated |
| 28 | tests/agent_rbac/test_blind_spot_coverage.py | tests/agent_rbac/test_blind_spot_cove... | prototype | generated |
| 29 | tests/agent_rbac/test_cross_model_consistency.py | tests/agent_rbac/test_cross_model_con... | prototype | generated |
| 30 | tests/agent_rbac/test_crosscut_d.py | tests/agent_rbac/test_crosscut_d.py | prototype | generated |
| 31 | tests/agent_rbac/test_cybersec_2026.py | tests/agent_rbac/test_cybersec_2026.py | prototype | generated |
| 32 | tests/agent_rbac/test_decision_explainer_agent_rbac.py | tests/agent_rbac/test_decision_explai... | prototype | generated |
| 33 | tests/agent_rbac/test_decisions.py | tests/agent_rbac/test_decisions.py | prototype | generated |
| 34 | tests/agent_rbac/test_derive_rbac.py | tests/agent_rbac/test_derive_rbac.py | prototype | generated |
| 35 | tests/agent_rbac/test_dry_run_agent_rbac.py | tests/agent_rbac/test_dry_run_agent_r... | prototype | generated |
| 36 | tests/agent_rbac/test_engine_degradation_agent_rbac.py | tests/agent_rbac/test_engine_degradat... | prototype | generated |
| 37 | tests/agent_rbac/test_enhanced_security.py | tests/agent_rbac/test_enhanced_securi... | prototype | generated |
| 38 | tests/agent_rbac/test_exceptions_agent_rbac.py | tests/agent_rbac/test_exceptions_agen... | prototype | generated |
| 39 | tests/agent_rbac/test_forensic_a.py | tests/agent_rbac/test_forensic_a.py | prototype | generated |
| 40 | tests/agent_rbac/test_forensic_b.py | tests/agent_rbac/test_forensic_b.py | prototype | generated |
| 41 | tests/agent_rbac/test_forensic_c.py | tests/agent_rbac/test_forensic_c.py | prototype | generated |
| 42 | tests/agent_rbac/test_guard_layers_agent_rbac.py | tests/agent_rbac/test_guard_layers_ag... | prototype | generated |
| 43 | tests/agent_rbac/test_identity.py | tests/agent_rbac/test_identity.py | prototype | generated |
| 44 | tests/agent_rbac/test_immutable_core_agent_rbac.py | tests/agent_rbac/test_immutable_core_... | prototype | generated |
| 45 | tests/agent_rbac/test_input_guard_agent_rbac.py | tests/agent_rbac/test_input_guard_age... | prototype | generated |
| 46 | tests/agent_rbac/test_integration_agent_rbac.py | tests/agent_rbac/test_integration_age... | prototype | generated |
| 47 | tests/agent_rbac/test_integrity_agent_rbac.py | tests/agent_rbac/test_integrity_agent... | prototype | generated |
| 48 | tests/agent_rbac/test_intent_binder_agent_rbac.py | tests/agent_rbac/test_intent_binder_a... | prototype | generated |
| 49 | tests/agent_rbac/test_kill_switch_agent_rbac.py | tests/agent_rbac/test_kill_switch_age... | prototype | generated |
| 50 | tests/agent_rbac/test_novel_attack.py | tests/agent_rbac/test_novel_attack.py | prototype | generated |
| 51 | tests/agent_rbac/test_observability_agent_rbac.py | tests/agent_rbac/test_observability_a... | prototype | generated |
| 52 | tests/agent_rbac/test_output_guard_agent_rbac.py | tests/agent_rbac/test_output_guard_ag... | prototype | generated |
| 53 | tests/agent_rbac/test_permission_guard.py | tests/agent_rbac/test_permission_guar... | prototype | generated |
| 54 | tests/agent_rbac/test_permissions.py | tests/agent_rbac/test_permissions.py | prototype | generated |
| 55 | tests/agent_rbac/test_post_action.py | tests/agent_rbac/test_post_action.py | prototype | generated |
| 56 | tests/agent_rbac/test_rbac_guard_agent_rbac.py | tests/agent_rbac/test_rbac_guard_agen... | prototype | generated |
| 57 | tests/agent_rbac/test_redteam_adversarial.py | tests/agent_rbac/test_redteam_adversa... | prototype | generated |
| 58 | tests/agent_rbac/test_risk_mitigation_agent_rbac.py | tests/agent_rbac/test_risk_mitigation... | prototype | generated |
| 59 | tests/agent_rbac/test_sequence_guard_agent_rbac.py | tests/agent_rbac/test_sequence_guard_... | prototype | generated |
| 60 | tests/agent_rbac/test_toctou_guard_agent_rbac.py | tests/agent_rbac/test_toctou_guard_ag... | prototype | generated |
| 61 | tests/agent_rbac/test_vibe_coding.py | tests/agent_rbac/test_vibe_coding.py | prototype | generated |
| 62 | tests/test_agent_signer.py | tests/test_agent_signer.py | prototype | generated |
| 63 | tests/test_ce_kill_switch.py | tests/test_ce_kill_switch.py | prototype | generated |
| 64 | tests/test_kill_switch_root.py | tests/test_kill_switch_root.py | prototype | generated |
| 65 | tests/test_kill_switch_sim.py | tests/test_kill_switch_sim.py | prototype | generated |
| 66 | tests/test_skill_kill_switch.py | tests/test_skill_kill_switch.py | prototype | generated |
| 67 | tests/test_trading_kill_switch.py | tests/test_trading_kill_switch.py | prototype | generated |
| 68 | tests/unit/agent_rbac/__init__.py | tests/unit/agent_rbac/__init__.py | prototype | generated |
| 69 | tests/unit/agent_rbac/conftest.py | tests/unit/agent_rbac/conftest.py | prototype | generated |
| 70 | tests/unit/agent_rbac/test_rbac_core.py | tests/unit/agent_rbac/test_rbac_core.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 7 条 / 7 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 7 条 / 7 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 7 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (7 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   a2a_check.py → __init__.py                                     │
│   approver_check.py → __init__.py                                │
│   bootstrap_superadmin.py → __init__.py                          │
│   capability_check.py → __init__.py                              │
│   contracts.py → __init__.py                                     │
│   conftest.py → __init__.py                                      │
│   conftest.py → __init__.py                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `23_d_autonomy_perm_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
