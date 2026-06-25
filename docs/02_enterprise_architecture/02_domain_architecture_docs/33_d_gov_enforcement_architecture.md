---
doc_type: domain_architecture_diagram
title: D-GOV-ENFORCEMENT rule_enforcement架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 33_d_gov_enforcement / rule_enforcement 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示rule_enforcement（D-GOV-ENFORCEMENT）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 rule_enforcement（D-GOV-ENFORCEMENT）的模块分布。共 107 个模块 / 107 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (107 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/governance/rule_enforcement/__init__.py  [produc... │
│   src/zephyr/governance/rule_enforcement/_template.yaml  [pro... │
│   src/zephyr/governance/rule_enforcement/adaptive_threshold.p... │
│   src/zephyr/governance/rule_enforcement/admission/__init__.p... │
│   src/zephyr/governance/rule_enforcement/admission/mad_001_ar... │
│   src/zephyr/governance/rule_enforcement/admission/mad_002_ph... │
│   src/zephyr/governance/rule_enforcement/admission/mad_003_de... │
│   src/zephyr/governance/rule_enforcement/admission/mad_004_in... │
│   src/zephyr/governance/rule_enforcement/admission/mad_005_de... │
│   src/zephyr/governance/rule_enforcement/adversarial_strategi... │
│   src/zephyr/governance/rule_enforcement/adversarial_validati... │
│   src/zephyr/governance/rule_enforcement/ai_capability_guard.... │
│   src/zephyr/governance/rule_enforcement/anti_pattern_guard.p... │
│   src/zephyr/governance/rule_enforcement/audit_chain_verifier... │
│   src/zephyr/governance/rule_enforcement/breaking_change_dete... │
│   src/zephyr/governance/rule_enforcement/can_i_deploy.py  [pr... │
│   src/zephyr/governance/rule_enforcement/capability_checker.p... │
│   src/zephyr/governance/rule_enforcement/cbac_matrix.py  [pro... │
│   ...还有 89 个模块 / 89 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 107 个模块 / 107 modules）。

### L1 基础层 / Foundation Layer (107 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/governance/rule_enforcement/__init__.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 2 | src/zephyr/governance/rule_enforcement/_template.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 3 | src/zephyr/governance/rule_enforcement/adaptive_threshold.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 4 | src/zephyr/governance/rule_enforcement/admission/__init__.py | src/zephyr/governance/rule_enforcemen... | prototype | deprecated |
| 5 | src/zephyr/governance/rule_enforcement/admission/mad_001_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 6 | src/zephyr/governance/rule_enforcement/admission/mad_002_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 7 | src/zephyr/governance/rule_enforcement/admission/mad_003_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 8 | src/zephyr/governance/rule_enforcement/admission/mad_004_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 9 | src/zephyr/governance/rule_enforcement/admission/mad_005_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 10 | src/zephyr/governance/rule_enforcement/adversarial_strate... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 11 | src/zephyr/governance/rule_enforcement/adversarial_valida... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 12 | src/zephyr/governance/rule_enforcement/ai_capability_guar... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 13 | src/zephyr/governance/rule_enforcement/anti_pattern_guard.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 14 | src/zephyr/governance/rule_enforcement/audit_chain_verifi... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 15 | src/zephyr/governance/rule_enforcement/breaking_change_de... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 16 | src/zephyr/governance/rule_enforcement/can_i_deploy.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 17 | src/zephyr/governance/rule_enforcement/capability_checker.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 18 | src/zephyr/governance/rule_enforcement/cbac_matrix.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 19 | src/zephyr/governance/rule_enforcement/cdc_broker.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 20 | src/zephyr/governance/rule_enforcement/check_types/__init... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 21 | src/zephyr/governance/rule_enforcement/check_types/advers... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 22 | src/zephyr/governance/rule_enforcement/check_types/check_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 23 | src/zephyr/governance/rule_enforcement/check_types/ct_aud... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 24 | src/zephyr/governance/rule_enforcement/check_types/ct_blu... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 25 | src/zephyr/governance/rule_enforcement/check_types/ct_cir... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 26 | src/zephyr/governance/rule_enforcement/check_types/ct_cir... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 27 | src/zephyr/governance/rule_enforcement/check_types/ct_cla... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 28 | src/zephyr/governance/rule_enforcement/check_types/ct_con... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 29 | src/zephyr/governance/rule_enforcement/check_types/ct_con... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 30 | src/zephyr/governance/rule_enforcement/check_types/ct_con... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 31 | src/zephyr/governance/rule_enforcement/check_types/ct_ded... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 32 | src/zephyr/governance/rule_enforcement/check_types/ct_dri... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 33 | src/zephyr/governance/rule_enforcement/check_types/ct_enc... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 34 | src/zephyr/governance/rule_enforcement/check_types/ct_enf... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 35 | src/zephyr/governance/rule_enforcement/check_types/ct_fie... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 36 | src/zephyr/governance/rule_enforcement/check_types/ct_fil... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 37 | src/zephyr/governance/rule_enforcement/check_types/ct_fle... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 38 | src/zephyr/governance/rule_enforcement/check_types/ct_fro... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 39 | src/zephyr/governance/rule_enforcement/check_types/ct_lev... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 40 | src/zephyr/governance/rule_enforcement/check_types/ct_lin... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 41 | src/zephyr/governance/rule_enforcement/check_types/ct_man... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 42 | src/zephyr/governance/rule_enforcement/check_types/ct_pat... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 43 | src/zephyr/governance/rule_enforcement/check_types/ct_pat... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 44 | src/zephyr/governance/rule_enforcement/check_types/ct_pat... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 45 | src/zephyr/governance/rule_enforcement/check_types/ct_pos... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 46 | src/zephyr/governance/rule_enforcement/check_types/ct_ref... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 47 | src/zephyr/governance/rule_enforcement/check_types/ct_reg... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 48 | src/zephyr/governance/rule_enforcement/check_types/ct_res... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 49 | src/zephyr/governance/rule_enforcement/check_types/ct_rol... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 50 | src/zephyr/governance/rule_enforcement/check_types/ct_sco... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 51 | src/zephyr/governance/rule_enforcement/check_types/ct_sec... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 52 | src/zephyr/governance/rule_enforcement/check_types/ct_str... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 53 | src/zephyr/governance/rule_enforcement/check_types/ct_tem... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 54 | src/zephyr/governance/rule_enforcement/check_types/ct_zer... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 55 | src/zephyr/governance/rule_enforcement/circuit_breaker.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 56 | src/zephyr/governance/rule_enforcement/contract_template_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 57 | src/zephyr/governance/rule_enforcement/drift_detector.py | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 58 | src/zephyr/governance/rule_enforcement/end_to_end_walkthr... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 59 | src/zephyr/governance/rule_enforcement/g1_ingest.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 60 | src/zephyr/governance/rule_enforcement/g2_triage.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 61 | src/zephyr/governance/rule_enforcement/g3_evaluate.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 62 | src/zephyr/governance/rule_enforcement/g4_activate.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 63 | src/zephyr/governance/rule_enforcement/g5_extract.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 64 | src/zephyr/governance/rule_enforcement/g6_blueprint_compl... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 65 | src/zephyr/governance/rule_enforcement/g6_ctr_compliance.... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 66 | src/zephyr/governance/rule_enforcement/g6_path_tree_fresh... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 67 | src/zephyr/governance/rule_enforcement/g7_position_limits... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 68 | src/zephyr/governance/rule_enforcement/g8.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 69 | src/zephyr/governance/rule_enforcement/g8_leverage.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 70 | src/zephyr/governance/rule_enforcement/g9.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 71 | src/zephyr/governance/rule_enforcement/g9_strategy_correl... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 72 | src/zephyr/governance/rule_enforcement/g_asset_inventory.... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 73 | src/zephyr/governance/rule_enforcement/gate_context.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 74 | src/zephyr/governance/rule_enforcement/gate_dedup.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 75 | src/zephyr/governance/rule_enforcement/gate_engine.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 76 | src/zephyr/governance/rule_enforcement/gate_health.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 77 | src/zephyr/governance/rule_enforcement/gate_integrity_gua... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 78 | src/zephyr/governance/rule_enforcement/gate_override.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 79 | src/zephyr/governance/rule_enforcement/gate_pipeline.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 80 | src/zephyr/governance/rule_enforcement/gate_simulator.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 81 | src/zephyr/governance/rule_enforcement/gate_types.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 82 | src/zephyr/governance/rule_enforcement/gct_024_budget_enf... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 83 | src/zephyr/governance/rule_enforcement/integration_test_r... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 84 | src/zephyr/governance/rule_enforcement/invariants/__init_... | src/zephyr/governance/rule_enforcemen... | prototype | generated |
| 85 | src/zephyr/governance/rule_enforcement/invariants/en_001_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 86 | src/zephyr/governance/rule_enforcement/invariants/en_001_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 87 | src/zephyr/governance/rule_enforcement/invariants/en_002_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 88 | src/zephyr/governance/rule_enforcement/invariants/en_002_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 89 | src/zephyr/governance/rule_enforcement/invariants/en_003_... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 90 | src/zephyr/governance/rule_enforcement/invariants/en_003_... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 91 | src/zephyr/governance/rule_enforcement/invariants/en_proc... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 92 | src/zephyr/governance/rule_enforcement/invariants/zero_re... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 93 | src/zephyr/governance/rule_enforcement/kiss_enforcer.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 94 | src/zephyr/governance/rule_enforcement/observability_base... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 95 | src/zephyr/governance/rule_enforcement/risk_ssot.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 96 | src/zephyr/governance/rule_enforcement/secrets_guard.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 97 | src/zephyr/governance/rule_enforcement/sys_master_complia... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 98 | src/zephyr/governance/rule_enforcement/sys_master_complia... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 99 | src/zephyr/governance/rule_enforcement/task/__init__.py | src/zephyr/governance/rule_enforcemen... | prototype | deprecated |
| 100 | src/zephyr/governance/rule_enforcement/task/g0_entry.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 101 | src/zephyr/governance/rule_enforcement/task/g0_orc_gate_e... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 102 | src/zephyr/governance/rule_enforcement/task/g7_orc_gate_e... | src/zephyr/governance/rule_enforcemen... | production | deprecated |
| 103 | src/zephyr/governance/rule_enforcement/task_completion_ga... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 104 | src/zephyr/governance/rule_enforcement/task_types.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 105 | src/zephyr/governance/rule_enforcement/triple_alignment.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 106 | src/zephyr/governance/rule_enforcement/truth_source_valid... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 107 | src/zephyr/governance/rule_enforcement/zero_residue.yaml | src/zephyr/governance/rule_enforcemen... | production | deprecated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 138 条 / 138 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 138 条 / 138 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 136 条 / edges                               │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (136 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   audit_chain_verifier.py → gate_context.py                      │
│   capability_checker.py → cbac_matrix.py                         │
│   gate_engine.py → circuit_breaker.py                            │
│   gate_engine.py → gate_types.py                                 │
│   gate_engine.py → risk_ssot.py                                  │
│   gate_engine.py → task_types.py                                 │
│   gate_engine.py → zero_residue_check.py                         │
│   gate_engine.py → en_002_enforcement_valida...                  │
│   gate_engine.py → en_003_contract_compatibi...                  │
│   gate_engine.py → en_001_circular_dependenc...                  │
│   gate_pipeline.py → gate_context.py                             │
│   gate_simulator.py → gate_context.py                            │
│   gate_simulator.py → gate_pipeline.py                           │
│   __init__.py → adaptive_threshold.py                            │
│   __init__.py → ai_capability_guard.py                           │
│   __init__.py → breaking_change_detector.py                      │
│   __init__.py → end_to_end_walkthrough.py                        │
│   __init__.py → gate_override.py                                 │
│   __init__.py → gate_health.py                                   │
│   __init__.py → gate_integrity_guard.py                          │
│   __init__.py → gate_simulator.py                                │
│   __init__.py → kiss_enforcer.py                                 │
│   __init__.py → integration_test_runner.py                       │
│   __init__.py → secrets_guard.py                                 │
│   check_type_registry.py → task_types.py                         │
│   check_type_registry.py → __init__.py                           │
│   adversarial_validation.py → adversarial_validation.py          │
│   adversarial_validation.py → adversarial_strategies.py          │
│   adversarial_validation.py → task_types.py                      │
│   adversarial_validation.py → check_type_registry.py             │
│   ct_circuit_breaker.py → circuit_breaker.py                     │
│   ct_circuit_breaker.py → task_types.py                          │
│   ct_circuit_breaker.py → check_type_registry.py                 │
│   ct_audit_findings_resolve... → task_types.py                   │
│   ct_audit_findings_resolve... → check_type_registry.py          │
│   ct_blueprint_read_check.py → task_types.py                     │
│   ct_blueprint_read_check.py → check_type_registry.py            │
│   ct_classification.py → task_types.py                           │
│   ct_classification.py → check_type_registry.py                  │
│   ct_circular_dependency_sc... → task_types.py                   │
│   ct_circular_dependency_sc... → check_type_registry.py          │
│   ct_circular_dependency_sc... → en_001_circular_dependenc...    │
│   ct_content_length.py → task_types.py                           │
│   ct_content_length.py → check_type_registry.py                  │
│   ct_content_quality.py → task_types.py                          │
│   ct_content_quality.py → check_type_registry.py                 │
│   ct_contract_compatibility... → task_types.py                   │
│   ct_contract_compatibility... → check_type_registry.py          │
│   ct_contract_compatibility... → en_003_contract_compatibi...    │
│   ...还有 87 条 / 87 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (2 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 138 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `33_d_gov_enforcement_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
