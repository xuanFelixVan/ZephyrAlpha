---
doc_type: domain_architecture_diagram
title: D-GOV_AUDIT 审计追踪架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 26_d_gov_audit / 审计追踪 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示审计追踪（D-GOV_AUDIT）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 审计追踪（D-GOV_AUDIT）的模块分布。共 217 个模块 / 217 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (213 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   docs/01_policies_and_standards/_registry/vocabularies/compl... │
│   docs/01_policies_and_standards/_registry/vocabularies/prove... │
│   docs/01_policies_and_standards/rules/trae_044_compliance_au... │
│   docs/02_enterprise_architecture/target_architecture/archite... │
│   docs__03_modules___cross_layer__audit_orchestrator__bluepri... │
│   docs__03_modules___domain_governance__audit_trail__blueprin... │
│   scripts/_archive/governance/repair/ensure_dep_cycles_view.p... │
│   scripts/_archive/governance/repair/list_source_md_files.py ... │
│   scripts/governance/meta/compliance_framework_map.yaml  [pro... │
│   scripts/governance/repair/audit_design_completeness.py  [pr... │
│   scripts/governance/repair/backup_db.py  [prototype]            │
│   scripts/governance/repair/red_blue_test.py  [prototype]        │
│   scripts/governance/repair/rollback_depgraph.py  [prototype]    │
│   src/zephyr/governance/audit_orchestration/__init__.py  [pro... │
│   src/zephyr/governance/audit_orchestration/agent_health_moni... │
│   src/zephyr/governance/audit_orchestration/agent_orchestrato... │
│   src/zephyr/governance/audit_orchestration/agent_quality.py ... │
│   src/zephyr/governance/audit_orchestration/autonomy_guard.py... │
│   ...还有 195 个模块 / 195 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (4 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   Audit Chain Domain 审计链域  [design]                          │
│   Audit Orchestrator 审计编排器  [design]                        │
│   Decision Audit Trail 决策审计追踪  [design]                    │
│   审计链6W模型 Audit Chain 6W Model  [design]                    │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 217 个模块 / 217 modules）。

### L1 基础层 / Foundation Layer (213 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/01_policies_and_standards/_registry/vocabularies/com... | docs/01_policies_and_standards/_regis... | production | orphan |
| 2 | docs/01_policies_and_standards/_registry/vocabularies/pro... | docs/01_policies_and_standards/_regis... | production | orphan |
| 3 | docs/01_policies_and_standards/rules/trae_044_compliance_... | docs/01_policies_and_standards/rules/... | production | orphan |
| 4 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 5 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | docs__03_modules___cross_layer__audit... | design | design_only |
| 6 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | docs__03_modules___domain_governance_... | design | design_only |
| 7 | scripts/_archive/governance/repair/ensure_dep_cycles_view.py | scripts/_archive/governance/repair/en... | prototype | draft |
| 8 | scripts/_archive/governance/repair/list_source_md_files.py | scripts/_archive/governance/repair/li... | prototype | draft |
| 9 | scripts/governance/meta/compliance_framework_map.yaml | scripts/governance/meta/compliance_fr... | production | orphan |
| 10 | scripts/governance/repair/audit_design_completeness.py | scripts/governance/repair/audit_desig... | prototype | draft |
| 11 | scripts/governance/repair/backup_db.py | scripts/governance/repair/backup_db.py | prototype | draft |
| 12 | scripts/governance/repair/red_blue_test.py | scripts/governance/repair/red_blue_te... | prototype | draft |
| 13 | scripts/governance/repair/rollback_depgraph.py | scripts/governance/repair/rollback_de... | prototype | draft |
| 14 | src/zephyr/governance/audit_orchestration/__init__.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 15 | src/zephyr/governance/audit_orchestration/agent_health_mo... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 16 | src/zephyr/governance/audit_orchestration/agent_orchestra... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 17 | src/zephyr/governance/audit_orchestration/agent_quality.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 18 | src/zephyr/governance/audit_orchestration/autonomy_guard.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 19 | src/zephyr/governance/audit_orchestration/backup_manager.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 20 | src/zephyr/governance/audit_orchestration/batch_orchestra... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 21 | src/zephyr/governance/audit_orchestration/benchmark_runne... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 22 | src/zephyr/governance/audit_orchestration/blind_spot_clos... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 23 | src/zephyr/governance/audit_orchestration/blueprint_healt... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 24 | src/zephyr/governance/audit_orchestration/blueprint_score... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 25 | src/zephyr/governance/audit_orchestration/bulkhead_manage... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 26 | src/zephyr/governance/audit_orchestration/canary_manager.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 27 | src/zephyr/governance/audit_orchestration/capacity_budget.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 28 | src/zephyr/governance/audit_orchestration/chaos_engine.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 29 | src/zephyr/governance/audit_orchestration/config_manager.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 30 | src/zephyr/governance/audit_orchestration/construction_gu... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 31 | src/zephyr/governance/audit_orchestration/contract_regist... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 32 | src/zephyr/governance/audit_orchestration/contract_router.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 33 | src/zephyr/governance/audit_orchestration/core/__init__.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 34 | src/zephyr/governance/audit_orchestration/core/agent_orch... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 35 | src/zephyr/governance/audit_orchestration/core/task_queue.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 36 | src/zephyr/governance/audit_orchestration/core/trigger_ro... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 37 | src/zephyr/governance/audit_orchestration/core/wave_gener... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 38 | src/zephyr/governance/audit_orchestration/data_lifecycle.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 39 | src/zephyr/governance/audit_orchestration/deferred_queue.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 40 | src/zephyr/governance/audit_orchestration/degrade_cascade.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 41 | src/zephyr/governance/audit_orchestration/dependency_lock.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 42 | src/zephyr/governance/audit_orchestration/design_decision... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 43 | src/zephyr/governance/audit_orchestration/disk_guard.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 44 | src/zephyr/governance/audit_orchestration/dlq_manager.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 45 | src/zephyr/governance/audit_orchestration/failure_matcher.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 46 | src/zephyr/governance/audit_orchestration/feature_flag.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 47 | src/zephyr/governance/audit_orchestration/file_task_mappe... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 48 | src/zephyr/governance/audit_orchestration/finding_bridge.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 49 | src/zephyr/governance/audit_orchestration/hallucination_d... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 50 | src/zephyr/governance/audit_orchestration/housekeeping.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 51 | src/zephyr/governance/audit_orchestration/incident_postmo... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 52 | src/zephyr/governance/audit_orchestration/incremental_rev... | src/zephyr/governance/audit_orchestra... | production | draft |
| 53 | src/zephyr/governance/audit_orchestration/ke_quality.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 54 | src/zephyr/governance/audit_orchestration/knowledge_fresh... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 55 | src/zephyr/governance/audit_orchestration/lean_scanner.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 56 | src/zephyr/governance/audit_orchestration/model_registry.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 57 | src/zephyr/governance/audit_orchestration/network_partiti... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 58 | src/zephyr/governance/audit_orchestration/path_index.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 59 | src/zephyr/governance/audit_orchestration/phase_executor.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 60 | src/zephyr/governance/audit_orchestration/prompt_version.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 61 | src/zephyr/governance/audit_orchestration/reconciliation_... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 62 | src/zephyr/governance/audit_orchestration/resilience/__in... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 63 | src/zephyr/governance/audit_orchestration/resilience/defe... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 64 | src/zephyr/governance/audit_orchestration/resilience/fail... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 65 | src/zephyr/governance/audit_orchestration/resilience/hall... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 66 | src/zephyr/governance/audit_orchestration/resilience/roll... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 67 | src/zephyr/governance/audit_orchestration/risk_registry.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 68 | src/zephyr/governance/audit_orchestration/rollback_manage... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 69 | src/zephyr/governance/audit_orchestration/rolling_upgrade.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 70 | src/zephyr/governance/audit_orchestration/schema_migratio... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 71 | src/zephyr/governance/audit_orchestration/session_conflic... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 72 | src/zephyr/governance/audit_orchestration/session_handoff.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 73 | src/zephyr/governance/audit_orchestration/session_manager.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 74 | src/zephyr/governance/audit_orchestration/stability_guard.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 75 | src/zephyr/governance/audit_orchestration/startup_sequenc... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 76 | src/zephyr/governance/audit_orchestration/state/__init__.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 77 | src/zephyr/governance/audit_orchestration/state/agent_hea... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 78 | src/zephyr/governance/audit_orchestration/state/file_task... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 79 | src/zephyr/governance/audit_orchestration/state/session_m... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 80 | src/zephyr/governance/audit_orchestration/state/state_syn... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 81 | src/zephyr/governance/audit_orchestration/state_propagati... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 82 | src/zephyr/governance/audit_orchestration/state_synchroni... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 83 | src/zephyr/governance/audit_orchestration/system_transfer.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 84 | src/zephyr/governance/audit_orchestration/task_queue.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 85 | src/zephyr/governance/audit_orchestration/teardown_manage... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 86 | src/zephyr/governance/audit_orchestration/trigger_router.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 87 | src/zephyr/governance/audit_orchestration/version_manifes... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 88 | src/zephyr/governance/audit_orchestration/wave_generator.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 89 | src/zephyr/governance/audit_orchestrator/__init__.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 90 | src/zephyr/governance/audit_orchestrator/__main__.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 91 | src/zephyr/governance/audit_orchestrator/anomaly.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 92 | src/zephyr/governance/audit_orchestrator/audit_admission_... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 93 | src/zephyr/governance/audit_orchestrator/bridge.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 94 | src/zephyr/governance/audit_orchestrator/cli.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 95 | src/zephyr/governance/audit_orchestrator/cold_start.py | src/zephyr/governance/audit_orchestra... | production | draft |
| 96 | src/zephyr/governance/audit_orchestrator/contracts.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 97 | src/zephyr/governance/audit_orchestrator/delegation_audit... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 98 | src/zephyr/governance/audit_orchestrator/delegation_bridg... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 99 | src/zephyr/governance/audit_orchestrator/drift_bridge.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 100 | src/zephyr/governance/audit_orchestrator/evidence_pack.py | src/zephyr/governance/audit_orchestra... | production | draft |
| 101 | src/zephyr/governance/audit_orchestrator/external_tool_au... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 102 | src/zephyr/governance/audit_orchestrator/feedback_bridge.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 103 | src/zephyr/governance/audit_orchestrator/feedback_policy.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 104 | src/zephyr/governance/audit_orchestrator/genesis.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 105 | src/zephyr/governance/audit_orchestrator/indexer.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 106 | src/zephyr/governance/audit_orchestrator/log_rotation.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 107 | src/zephyr/governance/audit_orchestrator/merkle_hourly.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 108 | src/zephyr/governance/audit_orchestrator/models.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 109 | src/zephyr/governance/audit_orchestrator/pipeline_runner.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 110 | src/zephyr/governance/audit_orchestrator/query.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 111 | src/zephyr/governance/audit_orchestrator/replay_engine.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 112 | src/zephyr/governance/audit_orchestrator/resource_aware_p... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 113 | src/zephyr/governance/audit_orchestrator/retention.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 114 | src/zephyr/governance/audit_orchestrator/self_monitor.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 115 | src/zephyr/governance/audit_orchestrator/text_to_finding_... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 116 | src/zephyr/governance/audit_orchestrator/tiered_storage.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 117 | src/zephyr/governance/audit_orchestrator/tiered_storage_b... | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 118 | src/zephyr/governance/audit_orchestrator/trust_bridge.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 119 | src/zephyr/governance/audit_orchestrator/trust_engine.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 120 | src/zephyr/governance/audit_orchestrator/writer.py | src/zephyr/governance/audit_orchestra... | prototype | draft |
| 121 | src/zephyr/governance/audit_trail/__init__.py | src/zephyr/governance/audit_trail/__i... | production | draft |
| 122 | src/zephyr/governance/audit_trail/__main__.py | src/zephyr/governance/audit_trail/__m... | prototype | draft |
| 123 | src/zephyr/governance/audit_trail/agent_signer.py | src/zephyr/governance/audit_trail/age... | production | draft |
| 124 | src/zephyr/governance/audit_trail/anomaly.py | src/zephyr/governance/audit_trail/ano... | production | draft |
| 125 | src/zephyr/governance/audit_trail/api_lifecycle.py | src/zephyr/governance/audit_trail/api... | production | draft |
| 126 | src/zephyr/governance/audit_trail/audit_admission_control... | src/zephyr/governance/audit_trail/aud... | prototype | draft |
| 127 | src/zephyr/governance/audit_trail/bridge.py | src/zephyr/governance/audit_trail/bri... | production | draft |
| 128 | src/zephyr/governance/audit_trail/bridges/__init__.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 129 | src/zephyr/governance/audit_trail/bridges/anomaly.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 130 | src/zephyr/governance/audit_trail/bridges/contracts.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 131 | src/zephyr/governance/audit_trail/bridges/delegation_brid... | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 132 | src/zephyr/governance/audit_trail/bridges/drift_bridge.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 133 | src/zephyr/governance/audit_trail/bridges/feedback_bridge.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 134 | src/zephyr/governance/audit_trail/bridges/spec_auditor.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 135 | src/zephyr/governance/audit_trail/bridges/tiered_storage_... | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 136 | src/zephyr/governance/audit_trail/bridges/trust_bridge.py | src/zephyr/governance/audit_trail/bri... | prototype | draft |
| 137 | src/zephyr/governance/audit_trail/changelog_manager.py | src/zephyr/governance/audit_trail/cha... | production | draft |
| 138 | src/zephyr/governance/audit_trail/cli.py | src/zephyr/governance/audit_trail/cli.py | production | draft |
| 139 | src/zephyr/governance/audit_trail/code_archaeology.py | src/zephyr/governance/audit_trail/cod... | production | draft |
| 140 | src/zephyr/governance/audit_trail/cold_start.py | src/zephyr/governance/audit_trail/col... | prototype | draft |
| 141 | src/zephyr/governance/audit_trail/compliance_map.py | src/zephyr/governance/audit_trail/com... | production | draft |
| 142 | src/zephyr/governance/audit_trail/contracts.py | src/zephyr/governance/audit_trail/con... | production | draft |
| 143 | src/zephyr/governance/audit_trail/corporate_actions.py | src/zephyr/governance/audit_trail/cor... | production | draft |
| 144 | src/zephyr/governance/audit_trail/delegation_auditor.py | src/zephyr/governance/audit_trail/del... | production | draft |
| 145 | src/zephyr/governance/audit_trail/delegation_bridge.py | src/zephyr/governance/audit_trail/del... | production | draft |
| 146 | src/zephyr/governance/audit_trail/dora_metrics.py | src/zephyr/governance/audit_trail/dor... | production | draft |
| 147 | src/zephyr/governance/audit_trail/evidence_pack.py | src/zephyr/governance/audit_trail/evi... | prototype | draft |
| 148 | src/zephyr/governance/audit_trail/external_tool_audit.py | src/zephyr/governance/audit_trail/ext... | production | draft |
| 149 | src/zephyr/governance/audit_trail/feedback_bridge.py | src/zephyr/governance/audit_trail/fee... | production | draft |
| 150 | src/zephyr/governance/audit_trail/feedback_policy.py | src/zephyr/governance/audit_trail/fee... | production | draft |
| 151 | src/zephyr/governance/audit_trail/feedback_self_audit.py | src/zephyr/governance/audit_trail/fee... | production | draft |
| 152 | src/zephyr/governance/audit_trail/financial_compliance.py | src/zephyr/governance/audit_trail/fin... | prototype | draft |
| 153 | src/zephyr/governance/audit_trail/finding_model.py | src/zephyr/governance/audit_trail/fin... | prototype | draft |
| 154 | src/zephyr/governance/audit_trail/genesis.py | src/zephyr/governance/audit_trail/gen... | production | draft |
| 155 | src/zephyr/governance/audit_trail/glossary_matrix.py | src/zephyr/governance/audit_trail/glo... | production | draft |
| 156 | src/zephyr/governance/audit_trail/incremental_review.py | src/zephyr/governance/audit_trail/inc... | production | draft |
| 157 | src/zephyr/governance/audit_trail/indexer.py | src/zephyr/governance/audit_trail/ind... | production | draft |
| 158 | src/zephyr/governance/audit_trail/integrity.py | src/zephyr/governance/audit_trail/int... | prototype | draft |
| 159 | src/zephyr/governance/audit_trail/kb_gate.py | src/zephyr/governance/audit_trail/kb_... | production | draft |
| 160 | src/zephyr/governance/audit_trail/log_rotation.py | src/zephyr/governance/audit_trail/log... | production | draft |
| 161 | src/zephyr/governance/audit_trail/merkle_hourly.py | src/zephyr/governance/audit_trail/mer... | prototype | draft |
| 162 | src/zephyr/governance/audit_trail/models.py | src/zephyr/governance/audit_trail/mod... | production | draft |
| 163 | src/zephyr/governance/audit_trail/observability_dashboard.py | src/zephyr/governance/audit_trail/obs... | production | draft |
| 164 | src/zephyr/governance/audit_trail/orchestrator.py | src/zephyr/governance/audit_trail/orc... | production | draft |
| 165 | src/zephyr/governance/audit_trail/pipeline_runner.py | src/zephyr/governance/audit_trail/pip... | production | draft |
| 166 | src/zephyr/governance/audit_trail/privacy.py | src/zephyr/governance/audit_trail/pri... | production | draft |
| 167 | src/zephyr/governance/audit_trail/provenance_tracker.py | src/zephyr/governance/audit_trail/pro... | production | draft |
| 168 | src/zephyr/governance/audit_trail/query.py | src/zephyr/governance/audit_trail/que... | production | draft |
| 169 | src/zephyr/governance/audit_trail/replay_engine.py | src/zephyr/governance/audit_trail/rep... | production | draft |
| 170 | src/zephyr/governance/audit_trail/resource_aware_pool.py | src/zephyr/governance/audit_trail/res... | prototype | draft |
| 171 | src/zephyr/governance/audit_trail/retention.py | src/zephyr/governance/audit_trail/ret... | production | draft |
| 172 | src/zephyr/governance/audit_trail/sbom_generator.py | src/zephyr/governance/audit_trail/sbo... | production | draft |
| 173 | src/zephyr/governance/audit_trail/spec_auditor.py | src/zephyr/governance/audit_trail/spe... | production | draft |
| 174 | src/zephyr/governance/audit_trail/supply_chain.py | src/zephyr/governance/audit_trail/sup... | production | draft |
| 175 | src/zephyr/governance/audit_trail/supply_chain_security.py | src/zephyr/governance/audit_trail/sup... | production | draft |
| 176 | src/zephyr/governance/audit_trail/tiered_storage.py | src/zephyr/governance/audit_trail/tie... | production | draft |
| 177 | src/zephyr/governance/audit_trail/tiered_storage_bridge.py | src/zephyr/governance/audit_trail/tie... | production | draft |
| 178 | src/zephyr/governance/audit_trail/trust_bridge.py | src/zephyr/governance/audit_trail/tru... | production | draft |
| 179 | src/zephyr/governance/audit_trail/trust_engine.py | src/zephyr/governance/audit_trail/tru... | production | draft |
| 180 | src/zephyr/governance/audit_trail/wqa_scorer.py | src/zephyr/governance/audit_trail/wqa... | production | draft |
| 181 | src/zephyr/governance/audit_trail/writer.py | src/zephyr/governance/audit_trail/wri... | production | draft |
| 182 | src/zephyr/governance/behavioral_admission/ai_code_standa... | src/zephyr/governance/behavioral_admi... | production | draft |
| 183 | src/zephyr/governance/behavioral_admission/mcp_result_pus... | src/zephyr/governance/behavioral_admi... | production | draft |
| 184 | src/zephyr/governance/behavioral_admission/post_process.py | src/zephyr/governance/behavioral_admi... | production | draft |
| 185 | src/zephyr/governance/behavioral_admission/vibe_coding_en... | src/zephyr/governance/behavioral_admi... | production | draft |
| 186 | src/zephyr/governance/compliance_gate_a6/default_security... | src/zephyr/governance/compliance_gate... | production | draft |
| 187 | src/zephyr/governance/financial_compliance.py | src/zephyr/governance/financial_compl... | production | draft |
| 188 | src/zephyr/governance/merkle_hourly.py | src/zephyr/governance/merkle_hourly.py | production | draft |
| 189 | src/zephyr/governance/persistence/audit_schema.py | src/zephyr/governance/persistence/aud... | production | draft |
| 190 | src/zephyr/governance/rule_enforcement/admission/mad_001_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 191 | src/zephyr/governance/rule_enforcement/admission/mad_002_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 192 | src/zephyr/governance/rule_enforcement/admission/mad_003_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 193 | src/zephyr/governance/rule_enforcement/admission/mad_004_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 194 | src/zephyr/governance/rule_enforcement/admission/mad_005_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 195 | src/zephyr/governance/rule_enforcement/audit_chain_verifi... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 196 | src/zephyr/governance/rule_enforcement/g6_blueprint_compl... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 197 | src/zephyr/governance/rule_enforcement/g6_ctr_compliance.... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 198 | src/zephyr/governance/rule_enforcement/sys_master_complia... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 199 | src/zephyr/governance/rule_enforcement/sys_master_complia... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 200 | src/zephyr/governance/self_healer.py | src/zephyr/governance/self_healer.py | prototype | draft |

> (仅显示前 200 个模块，共 213 个)

### 未分类 / Unclassified (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-GOVERNANCE/Audit Chain Domain 审计链域 | Audit Chain Domain 审计链域 | design | design_only |
| 2 | D-GOVERNANCE/Audit Orchestrator 审计编排器 | Audit Orchestrator 审计编排器 | design | design_only |
| 3 | D-GOVERNANCE/Decision Audit Trail 决策审计追踪 | Decision Audit Trail 决策审计追踪 | design | design_only |
| 4 | D-GOVERNANCE/审计链6W模型 Audit Chain 6W Model | 审计链6W模型 Audit Chain 6W Model | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 193 条 / 193 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 193 条 / 193 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 3                               │
│   [import_depends]: 132 条 / edges                               │
│   [config_depends]: 53 条 / edges                                │
│   [test_depends]: 8 条 / edges                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (132 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   agent_health_monitor.py → agent_orchestrator.py                │
│   contract_router.py → contract_registry.py                      │
│   state_synchronizer.py → file_task_mapper.py                    │
│   trigger_router.py → blueprint_scorer.py                        │
│   task_queue.py → task_queue.py                                  │
│   trigger_router.py → blueprint_scorer.py                        │
│   __init__.py → trigger_router.py                                │
│   __init__.py → deferred_queue.py                                │
│   __init__.py → failure_matcher.py                               │
│   agent_health_monitor.py → agent_orchestrator.py                │
│   state_synchronizer.py → file_task_mapper.py                    │
│   __init__.py → session_manager.py                               │
│   audit_admission_controlle... → finding_model.py                │
│   audit_admission_controlle... → __init__.py                     │
│   bridge.py → merkle_hourly.py                                   │
│   bridge.py → delegation_bridge.py                               │
│   bridge.py → feedback_bridge.py                                 │
│   bridge.py → tiered_storage_bridge.py                           │
│   bridge.py → trust_bridge.py                                    │
│   delegation_auditor.py → delegation_bridge.py                   │
│   cli.py → audit_admission_controlle...                          │
│   cli.py → kb_gate.py                                            │
│   cli.py → resource_aware_pool.py                                │
│   contracts.py → models.py                                       │
│   feedback_policy.py → feedback_bridge.py                        │
│   pipeline_runner.py → text_to_finding_adapter.py                │
│   query.py → models.py                                           │
│   merkle_hourly.py → merkle_hourly.py                            │
│   trust_bridge.py → trust_engine.py                              │
│   writer.py → models.py                                          │
│   text_to_finding_adapter.py → finding_model.py                  │
│   tiered_storage_bridge.py → tiered_storage.py                   │
│   __init__.py → evidence_pack.py                                 │
│   __init__.py → merkle_hourly.py                                 │
│   __init__.py → text_to_finding_adapter.py                       │
│   __init__.py → audit_admission_controlle...                     │
│   __init__.py → anomaly.py                                       │
│   __init__.py → bridge.py                                        │
│   __init__.py → cli.py                                           │
│   __init__.py → delegation_auditor.py                            │
│   __init__.py → contracts.py                                     │
│   __init__.py → cold_start.py                                    │
│   __init__.py → delegation_bridge.py                             │
│   __init__.py → feedback_bridge.py                               │
│   __init__.py → external_tool_audit.py                           │
│   __init__.py → feedback_policy.py                               │
│   __init__.py → genesis.py                                       │
│   __init__.py → log_rotation.py                                  │
│   __init__.py → indexer.py                                       │
│   ...还有 83 条 / 83 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (53 条 / edges) — 已达显示上限，省略 / limit reached

**[test_depends]** (8 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 193 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `26_d_gov_audit_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
