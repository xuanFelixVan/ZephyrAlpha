---
doc_type: domain_architecture_doc
title: D-GOV_AUDIT audit-trail架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-GOV_AUDIT audit-trail架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-GOV_AUDIT |
| 域名称 | audit-trail |
| 架构层 | L2_domain |
| 模块总数 | 69 |
| 设计态模块 | 0 |
| 原型态模块 | 0 |
| 生产态模块 | 69 |
| 容量 | 69/200 (正常) |
| 描述 | Merkle小时级完整性(merkle_hourly) |

## 模块清单

共 69 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| ...policies_and_standards/_registry/vocabularies/compliance_tags_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...andards/_registry/vocabularies/provenance_audit_chain_verdict_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_044_compliance_audit.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| ...rchitecture/target_architecture/architecture_model/layers/l10_compliance.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| scripts/governance/meta/compliance_framework_map.yaml | MOD-INF-005 | orphan | production | 0 | 0 |
| src/zephyr/governance/audit_orchestration/incremental_review.py | SRC-018 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_orchestrator/cold_start.py | MOD-INF-027 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_orchestrator/evidence_pack.py | MOD-INF-027 | draft | production | 2 | 0 |
| src/zephyr/governance/audit_trail/__init__.py | MOD-INF-027 | draft | production | 11 | 31 |
| src/zephyr/governance/audit_trail/agent_signer.py | MOD-INF-020 | draft | production | 4 | 0 |
| src/zephyr/governance/audit_trail/anomaly.py | MOD-INF-027 | draft | production | 13 | 0 |
| src/zephyr/governance/audit_trail/api_lifecycle.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/bridge.py | MOD-INF-027 | draft | production | 16 | 6 |
| src/zephyr/governance/audit_trail/changelog_manager.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/cli.py | MOD-INF-027 | draft | production | 5 | 7 |
| src/zephyr/governance/audit_trail/code_archaeology.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/compliance_map.py | MOD-INF-020 | draft | production | 1 | 1 |
| src/zephyr/governance/audit_trail/contracts.py | MOD-INF-027 | draft | production | 13 | 1 |
| src/zephyr/governance/audit_trail/corporate_actions.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/delegation_auditor.py | MOD-INF-027 | draft | production | 3 | 1 |
| src/zephyr/governance/audit_trail/delegation_bridge.py | MOD-INF-027 | draft | production | 8 | 1 |
| src/zephyr/governance/audit_trail/dora_metrics.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/external_tool_audit.py | MOD-INF-027 | draft | production | 3 | 0 |
| src/zephyr/governance/audit_trail/feedback_bridge.py | MOD-INF-027 | draft | production | 8 | 1 |
| src/zephyr/governance/audit_trail/feedback_policy.py | MOD-INF-027 | draft | production | 3 | 1 |
| src/zephyr/governance/audit_trail/feedback_self_audit.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/genesis.py | MOD-INF-027 | draft | production | 3 | 0 |
| src/zephyr/governance/audit_trail/glossary_matrix.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/incremental_review.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/indexer.py | MOD-INF-027 | draft | production | 7 | 0 |
| src/zephyr/governance/audit_trail/kb_gate.py | MOD-INF-020 | draft | production | 2 | 1 |
| src/zephyr/governance/audit_trail/log_rotation.py | MOD-INF-027 | draft | production | 4 | 0 |
| src/zephyr/governance/audit_trail/models.py | MOD-INF-027 | draft | production | 35 | 0 |
| src/zephyr/governance/audit_trail/observability_dashboard.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/orchestrator.py | MOD-INF-027 | draft | production | 1 | 9 |
| src/zephyr/governance/audit_trail/pipeline_runner.py | MOD-INF-027 | draft | production | 5 | 2 |
| src/zephyr/governance/audit_trail/privacy.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/provenance_tracker.py | MOD-INF-020 | draft | production | 2 | 0 |
| src/zephyr/governance/audit_trail/query.py | MOD-INF-027 | draft | production | 11 | 1 |
| src/zephyr/governance/audit_trail/replay_engine.py | MOD-INF-027 | draft | production | 3 | 1 |
| src/zephyr/governance/audit_trail/retention.py | MOD-INF-027 | draft | production | 4 | 0 |
| src/zephyr/governance/audit_trail/sbom_generator.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/spec_auditor.py | MOD-INF-020 | draft | production | 6 | 1 |
| src/zephyr/governance/audit_trail/supply_chain.py | MOD-INF-020 | draft | production | 1 | 1 |
| src/zephyr/governance/audit_trail/supply_chain_security.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/tiered_storage.py | MOD-INF-027 | draft | production | 6 | 0 |
| src/zephyr/governance/audit_trail/tiered_storage_bridge.py | MOD-INF-027 | draft | production | 6 | 1 |
| src/zephyr/governance/audit_trail/trust_bridge.py | MOD-INF-027 | draft | production | 8 | 1 |
| src/zephyr/governance/audit_trail/trust_engine.py | MOD-INF-027 | draft | production | 5 | 0 |
| src/zephyr/governance/audit_trail/wqa_scorer.py | MOD-INF-020 | draft | production | 1 | 0 |
| src/zephyr/governance/audit_trail/writer.py | MOD-INF-027 | draft | production | 32 | 1 |
| src/zephyr/governance/behavioral_admission/ai_code_standards.py | SRC-020 | draft | production | 1 | 0 |
| src/zephyr/governance/behavioral_admission/mcp_result_push.py | SRC-022 | draft | production | 3 | 0 |
| src/zephyr/governance/behavioral_admission/post_process.py | SRC-023 | draft | production | 5 | 0 |
| src/zephyr/governance/behavioral_admission/vibe_coding_enforcer.py | SRC-024 | draft | production | 2 | 0 |
| src/zephyr/governance/compliance_gate_a6/default_security_gateway.py | MOD-L10-001 | draft | production | 4 | 5 |
| src/zephyr/governance/financial_compliance.py | SRC-034 | draft | production | 3 | 0 |
| src/zephyr/governance/merkle_hourly.py | MOD-INF-027 | draft | production | 7 | 1 |
| src/zephyr/governance/persistence/audit_schema.py | MOD-GOVERNANCE | draft | production | 3 | 1 |
| ...hyr/governance/rule_enforcement/admission/mad_001_architecture_necessity.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/admission/mad_002_phase_relevance.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| ...phyr/governance/rule_enforcement/admission/mad_003_dependency_compliance.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| ...hyr/governance/rule_enforcement/admission/mad_004_interface_definability.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| .../governance/rule_enforcement/admission/mad_005_dependency_graph_template.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/audit_chain_verifier.py | MOD-INF-007 | draft | production | 2 | 2 |
| src/zephyr/governance/rule_enforcement/g6_blueprint_compliance.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g6_ctr_compliance.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/sys_master_compliance.py | MOD-INF-007 | draft | production | 4 | 0 |
| src/zephyr/governance/rule_enforcement/sys_master_compliance.yaml | MOD-INF-007 | orphan | production | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-GOVERNANCE | 15 | import_depends |
| D-GOV_DRIFT | 6 | import_depends |
| D-SECURITY | 4 | import_depends |
| D-INTEGRATION | 2 | import_depends |
| D-TRADING | 1 | import_depends |
| D-SHARED | 1 | import_depends |
| D-GOV_RULE | 1 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 192 | test_depends,import_depends,config_depends |
| D-INFRA_RUNTIME | 10 | import_depends |
| D-TRADING | 7 | import_depends |
| D-GOV_DRIFT | 6 | import_depends |
| D-SECURITY | 3 | import_depends |
| D-INTEGRATION | 3 | import_depends |
| D-COMPLIANCE | 3 | import_depends |
| D-AUTONOMY_CORE | 3 | import_depends |
| D-GOV_RULE | 2 | import_depends |
| D-SHARED | 1 | import_depends |
| D-OPS | 1 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

## 域内依赖图

详见 [d_gov_audit_dependency.mmd](d_gov_audit_dependency.mmd)
