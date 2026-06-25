---
doc_type: domain_architecture_diagram
title: D-GOV-DOCS architecture_docs架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 32_d_gov_docs / architecture_docs 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示architecture_docs（D-GOV-DOCS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 architecture_docs（D-GOV-DOCS）的模块分布。共 151 个模块 / 151 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (151 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   docs/01_policies_and_standards/_registry/schemas/session_lo... │
│   docs/01_policies_and_standards/rules/_index.yaml  [production] │
│   docs/01_policies_and_standards/rules/trae_001_file_operatio... │
│   docs/01_policies_and_standards/rules/trae_002_anti_orphan_s... │
│   docs/01_policies_and_standards/rules/trae_003_task_granular... │
│   docs/01_policies_and_standards/rules/trae_004_parallel_atom... │
│   docs/01_policies_and_standards/rules/trae_005_modification_... │
│   docs/01_policies_and_standards/rules/trae_006_anti_hallucin... │
│   docs/01_policies_and_standards/rules/trae_007_anti_hallucin... │
│   docs/01_policies_and_standards/rules/trae_008_anti_hallucin... │
│   docs/01_policies_and_standards/rules/trae_009_anti_hallucin... │
│   docs/01_policies_and_standards/rules/trae_010_code_naming_o... │
│   docs/01_policies_and_standards/rules/trae_011_code_type_imp... │
│   docs/01_policies_and_standards/rules/trae_012_code_test_sec... │
│   docs/01_policies_and_standards/rules/trae_013_arch_cross_pa... │
│   docs/01_policies_and_standards/rules/trae_014_arch_blueprin... │
│   docs/01_policies_and_standards/rules/trae_015_arch_path_reg... │
│   docs/01_policies_and_standards/rules/trae_016_arch_drift_de... │
│   ...还有 133 个模块 / 133 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 151 个模块 / 151 modules）。

### L1 基础层 / Foundation Layer (151 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/01_policies_and_standards/_registry/schemas/session_... | docs/01_policies_and_standards/_regis... | production | deprecated |
| 2 | docs/01_policies_and_standards/rules/_index.yaml | docs/01_policies_and_standards/rules/... | production | deprecated |
| 3 | docs/01_policies_and_standards/rules/trae_001_file_operat... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 4 | docs/01_policies_and_standards/rules/trae_002_anti_orphan... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 5 | docs/01_policies_and_standards/rules/trae_003_task_granul... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 6 | docs/01_policies_and_standards/rules/trae_004_parallel_at... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 7 | docs/01_policies_and_standards/rules/trae_005_modificatio... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 8 | docs/01_policies_and_standards/rules/trae_006_anti_halluc... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 9 | docs/01_policies_and_standards/rules/trae_007_anti_halluc... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 10 | docs/01_policies_and_standards/rules/trae_008_anti_halluc... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 11 | docs/01_policies_and_standards/rules/trae_009_anti_halluc... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 12 | docs/01_policies_and_standards/rules/trae_010_code_naming... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 13 | docs/01_policies_and_standards/rules/trae_011_code_type_i... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 14 | docs/01_policies_and_standards/rules/trae_012_code_test_s... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 15 | docs/01_policies_and_standards/rules/trae_013_arch_cross_... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 16 | docs/01_policies_and_standards/rules/trae_014_arch_bluepr... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 17 | docs/01_policies_and_standards/rules/trae_015_arch_path_r... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 18 | docs/01_policies_and_standards/rules/trae_016_arch_drift_... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 19 | docs/01_policies_and_standards/rules/trae_017_arch_govern... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 20 | docs/01_policies_and_standards/rules/trae_018_behavior_co... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 21 | docs/01_policies_and_standards/rules/trae_019_behavior_se... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 22 | docs/01_policies_and_standards/rules/trae_020_behavior_go... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 23 | docs/01_policies_and_standards/rules/trae_021_behavior_ot... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 24 | docs/01_policies_and_standards/rules/trae_022_behavior_co... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 25 | docs/01_policies_and_standards/rules/trae_023_behavior_co... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 26 | docs/01_policies_and_standards/rules/trae_024_methodology... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 27 | docs/01_policies_and_standards/rules/trae_025_methodology... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 28 | docs/01_policies_and_standards/rules/trae_026_methodology... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 29 | docs/01_policies_and_standards/rules/trae_027_methodology... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 30 | docs/01_policies_and_standards/rules/trae_028_doc_structu... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 31 | docs/01_policies_and_standards/rules/trae_029_doc_operati... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 32 | docs/01_policies_and_standards/rules/trae_030_doc_numberi... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 33 | docs/01_policies_and_standards/rules/trae_031_security_ke... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 34 | docs/01_policies_and_standards/rules/trae_032_module_life... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 35 | docs/01_policies_and_standards/rules/trae_033_module_regi... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 36 | docs/01_policies_and_standards/rules/trae_034_task_card_s... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 37 | docs/01_policies_and_standards/rules/trae_035_task_constr... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 38 | docs/01_policies_and_standards/rules/trae_036_arch_gate_t... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 39 | docs/01_policies_and_standards/rules/trae_037_arch_qualif... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 40 | docs/01_policies_and_standards/rules/trae_038_arch_ctr_in... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 41 | docs/01_policies_and_standards/rules/trae_039_ai_hallucin... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 42 | docs/01_policies_and_standards/rules/trae_040_ai_model_ro... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 43 | docs/01_policies_and_standards/rules/trae_041_meta_rule_c... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 44 | docs/01_policies_and_standards/rules/trae_042_meta_rule_s... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 45 | docs/01_policies_and_standards/rules/trae_043_meta_rule_m... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 46 | docs/01_policies_and_standards/rules/trae_044_compliance_... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 47 | docs/01_policies_and_standards/rules/trae_045_data_qualit... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 48 | docs/01_policies_and_standards/rules/trae_046_engineering... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 49 | docs/01_policies_and_standards/rules/trae_047_engineering... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 50 | docs/01_policies_and_standards/rules/trae_048_ops_vibe_co... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 51 | docs/01_policies_and_standards/rules/trae_049_ops_domain_... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 52 | docs/01_policies_and_standards/rules/trae_050_domain_poli... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 53 | docs/01_policies_and_standards/rules/trae_051_domain_poli... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 54 | docs/01_policies_and_standards/rules/trae_052_cross_bluep... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 55 | docs/01_policies_and_standards/rules/trae_053_automation_... | docs/01_policies_and_standards/rules/... | production | deprecated |
| 56 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 57 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 58 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 59 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 60 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 61 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 62 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 63 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 64 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 65 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 66 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 67 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 68 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 69 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 70 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 71 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 72 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 73 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 74 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 75 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 76 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 77 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 78 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 79 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 80 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 81 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 82 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 83 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 84 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 85 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 86 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | deprecated |
| 87 | docs/03_modules/_cross_layer/mcp_servers/changes/MOD_INF_... | docs/03_modules/_cross_layer/mcp_serv... | production | deprecated |
| 88 | docs/03_modules/_domain_autonomy_core/agent_rbac/adversar... | docs/03_modules/_domain_autonomy_core... | production | deprecated |
| 89 | docs/03_modules/_domain_autonomy_core/agent_spec/blind_sp... | docs/03_modules/_domain_autonomy_core... | production | deprecated |
| 90 | docs/03_modules/_domain_autonomy_core/agent_spec/decision... | docs/03_modules/_domain_autonomy_core... | production | deprecated |
| 91 | docs/03_modules/_domain_autonomy_core/agent_spec/phase_tr... | docs/03_modules/_domain_autonomy_core... | production | deprecated |
| 92 | docs/03_modules/_domain_autonomy_core/agent_spec/risk_tra... | docs/03_modules/_domain_autonomy_core... | production | deprecated |
| 93 | docs/03_modules/_domain_infra_ops/a2a_protocol/a2a_anomal... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 94 | docs/03_modules/_domain_infra_ops/a2a_protocol/arbitratio... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 95 | docs/03_modules/_domain_infra_ops/a2a_protocol/blind_spot... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 96 | docs/03_modules/_domain_infra_ops/a2a_protocol/phase_plan... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 97 | docs/03_modules/_domain_infra_ops/a2a_protocol/pre_mortem... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 98 | docs/03_modules/_domain_infra_ops/a2a_protocol/trigger_co... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 99 | docs/03_modules/_domain_infra_ops/a2a_protocol/version_tr... | docs/03_modules/_domain_infra_ops/a2a... | production | deprecated |
| 100 | docs/03_modules/path_ownership_map.yaml | docs/03_modules/path_ownership_map.yaml | production | deprecated |
| 101 | src/zephyr/governance/kb/__init__.py | src/zephyr/governance/kb/__init__.py | prototype | generated |
| 102 | src/zephyr/governance/kb/_backend_protocol.py | src/zephyr/governance/kb/_backend_pro... | prototype | generated |
| 103 | src/zephyr/governance/kb/activate.py | src/zephyr/governance/kb/activate.py | prototype | generated |
| 104 | src/zephyr/governance/kb/analyze.py | src/zephyr/governance/kb/analyze.py | prototype | generated |
| 105 | src/zephyr/governance/kb/batch_ingest.py | src/zephyr/governance/kb/batch_ingest.py | prototype | generated |
| 106 | src/zephyr/governance/kb/bootstrap.py | src/zephyr/governance/kb/bootstrap.py | prototype | generated |
| 107 | src/zephyr/governance/kb/chromadb_init.py | src/zephyr/governance/kb/chromadb_ini... | prototype | generated |
| 108 | src/zephyr/governance/kb/embedding_migrate.py | src/zephyr/governance/kb/embedding_mi... | prototype | generated |
| 109 | src/zephyr/governance/kb/extract.py | src/zephyr/governance/kb/extract.py | prototype | generated |
| 110 | src/zephyr/governance/kb/filing_nlp_engine/__init__.py | src/zephyr/governance/kb/filing_nlp_e... | prototype | generated |
| 111 | src/zephyr/governance/kb/filing_nlp_engine/extract.py | src/zephyr/governance/kb/filing_nlp_e... | prototype | generated |
| 112 | src/zephyr/governance/kb/freeze.py | src/zephyr/governance/kb/freeze.py | prototype | generated |
| 113 | src/zephyr/governance/kb/graph_validator.py | src/zephyr/governance/kb/graph_valida... | prototype | generated |
| 114 | src/zephyr/governance/kb/ingest.py | src/zephyr/governance/kb/ingest.py | prototype | generated |
| 115 | src/zephyr/governance/kb/integrity.py | src/zephyr/governance/kb/integrity.py | prototype | generated |
| 116 | src/zephyr/governance/kb/kb_engine/__init__.py | src/zephyr/governance/kb/kb_engine/__... | prototype | generated |
| 117 | src/zephyr/governance/kb/kb_engine/chromadb_init.py | src/zephyr/governance/kb/kb_engine/ch... | prototype | generated |
| 118 | src/zephyr/governance/kb/kb_engine/embedding_migrate.py | src/zephyr/governance/kb/kb_engine/em... | prototype | generated |
| 119 | src/zephyr/governance/kb/kb_engine/kb_gate_task.py | src/zephyr/governance/kb/kb_engine/kb... | prototype | generated |
| 120 | src/zephyr/governance/kb/kb_gate_task.py | src/zephyr/governance/kb/kb_gate_task.py | prototype | generated |
| 121 | src/zephyr/governance/kb/kb_repo.py | src/zephyr/governance/kb/kb_repo.py | prototype | generated |
| 122 | src/zephyr/governance/kb/ke_tombstone.py | src/zephyr/governance/kb/ke_tombstone.py | prototype | generated |
| 123 | src/zephyr/governance/kb/load_bearing.py | src/zephyr/governance/kb/load_bearing.py | prototype | generated |
| 124 | src/zephyr/governance/kb/migration/__init__.py | src/zephyr/governance/kb/migration/__... | prototype | generated |
| 125 | src/zephyr/governance/kb/migration/embedding_migrate.py | src/zephyr/governance/kb/migration/em... | prototype | generated |
| 126 | src/zephyr/governance/kb/migration/kb_gate_task.py | src/zephyr/governance/kb/migration/kb... | prototype | generated |
| 127 | src/zephyr/governance/kb/pipeline/__init__.py | src/zephyr/governance/kb/pipeline/__i... | prototype | generated |
| 128 | src/zephyr/governance/kb/pipeline/activate.py | src/zephyr/governance/kb/pipeline/act... | prototype | generated |
| 129 | src/zephyr/governance/kb/pipeline/analyze.py | src/zephyr/governance/kb/pipeline/ana... | prototype | generated |
| 130 | src/zephyr/governance/kb/pipeline/batch_ingest.py | src/zephyr/governance/kb/pipeline/bat... | prototype | generated |
| 131 | src/zephyr/governance/kb/pipeline/extract.py | src/zephyr/governance/kb/pipeline/ext... | prototype | generated |
| 132 | src/zephyr/governance/kb/pipeline/ingest.py | src/zephyr/governance/kb/pipeline/ing... | prototype | generated |
| 133 | src/zephyr/governance/kb/pipeline/triage.py | src/zephyr/governance/kb/pipeline/tri... | prototype | generated |
| 134 | src/zephyr/governance/kb/quiet_period_monitor.py | src/zephyr/governance/kb/quiet_period... | prototype | generated |
| 135 | src/zephyr/governance/kb/reranker.py | src/zephyr/governance/kb/reranker.py | prototype | generated |
| 136 | src/zephyr/governance/kb/safety_brake.py | src/zephyr/governance/kb/safety_brake.py | prototype | generated |
| 137 | src/zephyr/governance/kb/self_test.py | src/zephyr/governance/kb/self_test.py | prototype | generated |
| 138 | src/zephyr/governance/kb/sentiment_engine/__init__.py | src/zephyr/governance/kb/sentiment_en... | prototype | generated |
| 139 | src/zephyr/governance/kb/sentiment_engine/analyze.py | src/zephyr/governance/kb/sentiment_en... | prototype | generated |
| 140 | src/zephyr/governance/kb/storage/__init__.py | src/zephyr/governance/kb/storage/__in... | prototype | generated |
| 141 | src/zephyr/governance/kb/storage/_backend_protocol.py | src/zephyr/governance/kb/storage/_bac... | prototype | generated |
| 142 | src/zephyr/governance/kb/storage/chromadb_init.py | src/zephyr/governance/kb/storage/chro... | prototype | generated |
| 143 | src/zephyr/governance/kb/storage/graph_validator.py | src/zephyr/governance/kb/storage/grap... | prototype | generated |
| 144 | src/zephyr/governance/kb/storage/kb_repo.py | src/zephyr/governance/kb/storage/kb_r... | prototype | generated |
| 145 | src/zephyr/governance/kb/storage/unified_memory_api.py | src/zephyr/governance/kb/storage/unif... | prototype | generated |
| 146 | src/zephyr/governance/kb/supply_chain_graph_engine/__init... | src/zephyr/governance/kb/supply_chain... | prototype | generated |
| 147 | src/zephyr/governance/kb/supply_chain_graph_engine/graph_... | src/zephyr/governance/kb/supply_chain... | prototype | generated |
| 148 | src/zephyr/governance/kb/triage.py | src/zephyr/governance/kb/triage.py | prototype | generated |
| 149 | src/zephyr/governance/kb/unified_memory_api.py | src/zephyr/governance/kb/unified_memo... | prototype | generated |
| 150 | src/zephyr/governance/kb/verify.py | src/zephyr/governance/kb/verify.py | prototype | generated |
| 151 | src/zephyr/governance/kb/vms_memory_backend.py | src/zephyr/governance/kb/vms_memory_b... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 16 条 / 16 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 16 条 / 16 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 16 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (16 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   freeze.py → __init__.py                                        │
│   integrity.py → __init__.py                                     │
│   ke_tombstone.py → __init__.py                                  │
│   load_bearing.py → __init__.py                                  │
│   quiet_period_monitor.py → __init__.py                          │
│   reranker.py → __init__.py                                      │
│   safety_brake.py → __init__.py                                  │
│   verify.py → __init__.py                                        │
│   _backend_protocol.py → __init__.py                             │
│   __init__.py → extract.py                                       │
│   __init__.py → embedding_migrate.py                             │
│   __init__.py → embedding_migrate.py                             │
│   __init__.py → activate.py                                      │
│   __init__.py → analyze.py                                       │
│   _backend_protocol.py → __init__.py                             │
│   __init__.py → graph_validator.py                               │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `32_d_gov_docs_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
