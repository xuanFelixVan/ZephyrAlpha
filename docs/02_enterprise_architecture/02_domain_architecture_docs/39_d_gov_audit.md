---
doc_type: architecture_view
title: D_GOV_AUDIT 审计追踪架构文档
version: "1.0"
status: active
date: 2026-07-19
owner: auto-generator
ttl: permanent
---

# 39_d_gov_audit / 审计追踪 / Audit Trail

> **功能简介 / Overview**: 审计追踪，负责变更审计追踪和操作日志管理

> **文档作用 / Purpose**: 展示 审计追踪（D_GOV_AUDIT）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 39 | Number | 39 |
| 域ID | D_GOV_AUDIT | Domain ID | D_GOV_AUDIT |
| 域名称 | 审计追踪 | Domain Name | Audit Trail |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 102 | Module Count | 102 |
| 域内依赖 | 71 | Internal Dependencies | 71 |
| 跨域入边 | 57 | Cross-domain Incoming | 57 |
| 跨域出边 | 74 | Cross-domain Outgoing | 74 |
| 设计态模块 | 2 | Design Modules | 2 |
| 原型态模块 | 34 | Prototype Modules | 34 |
| 生产态模块 | 66 | Production Modules | 66 |
| 容量 | 66/150 (正常) | Capacity | 66/150 (正常) |
| 描述 | 审计管线编排 | Description | 审计管线编排 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 102 个模块 / 102 modules）。

### L0 基础设施层 / Infrastructure Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/governance/audit/default_attribution_engine.py | Re-export wrapper: default_attribution_engine c... | 原型态 / prototype | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |
| 2 | src/zephyr/governance/audit/default_tca_engine.py | Re-export wrapper: default_tca_engine canonical... | 生产态 / production | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |

### L1 基础层 / Foundation Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | docs__03_modules___cross_layer__audit_orchestrator__blueprint_md | 设计态 / design | [MOD-INF-027](../../03_modules/_cross_layer/audit_orchestrator/blueprint.md) |
| 2 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | docs__03_modules___domain_governance__audit_trail__blueprint_md | 设计态 / design | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |

### L2 领域层 / Domain Layer (98 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | scripts/governance/repair/audit_design_completeness.py | [INVARIANTS] 按path精确匹配+按功能名模糊匹配; ... | 原型态 / prototype |  |
| 2 | scripts/governance/repair/red_blue_test.py | red_blue_test.py | 原型态 / prototype |  |
| 3 | scripts/governance/repair/rollback_depgraph.py | [INVARIANTS] 仅接受depgraph.backup.*路径; 回滚... | 原型态 / prototype |  |
| 4 | scripts/governance/test_remediation_progress_smoke.py | test_remediation_progress_smoke.py — Phase 3.1... | 原型态 / prototype |  |
| 5 | src/zephyr/gov_audit/_orchestrator_compat.py | audit-orchestrator 兼容重导出层（ARCH-042 阶段4... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 6 | src/zephyr/gov_audit/action_history.py | ActionHistory — 操作历史持久化审计 + 去重 + 循... | 生产态 / production | [MOD-INF-024](../../03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) |
| 7 | src/zephyr/gov_audit/agent_signer.py | audit-trail.agent_signer — MOD-INF-020 · Agen... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 8 | src/zephyr/gov_audit/anomaly.py | anomaly.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 9 | src/zephyr/gov_audit/api_lifecycle.py | api_lifecycle.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 10 | src/zephyr/gov_audit/audit_admission_controller.py | audit_admission_controller.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 11 | src/zephyr/gov_audit/audit_schema.py | audit_schema — 审计视图与查询入口（SH-DB-001 v... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 12 | src/zephyr/gov_audit/audit_write_failure_protector.py | Audit Write Failure Protector — v0.13.0 审计写... | 生产态 / production | [MOD-INF-022](../../03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md) |
| 13 | src/zephyr/gov_audit/bridge.py | bridge.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 14 | src/zephyr/gov_audit/bridges/audit_anomaly.py | G-CT-002 Audit 异常检测器 — AnomalyEvent Pydan... | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 15 | src/zephyr/gov_audit/bridges/audit_contracts.py | G-CT-001 契约消费端 — Audit.write() 公共接口. | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 16 | src/zephyr/gov_audit/bridges/audit_delegation_bridge.py | Audit ↔ DelegationManager 委托链审计桥接. | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 17 | src/zephyr/gov_audit/bridges/audit_drift_bridge.py | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020... | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 18 | src/zephyr/gov_audit/bridges/audit_feedback_bridge.py | Audit ↔ Feedback Loop 三角闭环桥接. | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 19 | src/zephyr/gov_audit/bridges/audit_tiered_storage_bridge.py | Audit ↔ WarmHotGate 三层存储桥接. | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 20 | src/zephyr/gov_audit/bridges/audit_trust_bridge.py | Audit ↔ ContinuousTrust 信任分数桥接. | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 21 | src/zephyr/gov_audit/changelog_manager.py | changelog_manager.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 22 | src/zephyr/gov_audit/cli.py | cli.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 23 | src/zephyr/gov_audit/code_archaeology.py | code_archaeology.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 24 | src/zephyr/gov_audit/cold_start.py | cold_start.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 25 | src/zephyr/gov_audit/compliance_map.py | audit-trail.compliance_map — MOD-INF-020 · 合... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 26 | src/zephyr/gov_audit/contracts.py | contracts.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 27 | src/zephyr/gov_audit/corporate_actions.py | corporate_actions.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 28 | src/zephyr/gov_audit/delegation_auditor.py | delegation_auditor.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 29 | src/zephyr/gov_audit/delegation_bridge.py | delegation_bridge.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 30 | src/zephyr/gov_audit/dora_metrics.py | dora_metrics.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 31 | src/zephyr/gov_audit/event_store.py | EventStore — Event Sourcing 事件追加与回放（DW... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 32 | src/zephyr/gov_audit/evidence_pack.py | audit-trail.evidence_pack — MOD-INF-020 · 证... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 33 | src/zephyr/gov_audit/external_tool_audit.py | external_tool_audit.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 34 | src/zephyr/gov_audit/feedback_bridge.py | feedback_bridge.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 35 | src/zephyr/gov_audit/feedback_policy.py | feedback_policy.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 36 | src/zephyr/gov_audit/feedback_self_audit.py | audit-trail.feedback_self_audit — MOD-INF-020 ... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 37 | src/zephyr/gov_audit/finding_ingest.py | finding_ingest.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 38 | src/zephyr/gov_audit/finding_model.py | finding_model.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 39 | src/zephyr/gov_audit/forensic_package.py | Forensic Package — v0.8.0 取证就绪: escalation... | 生产态 / production | [MOD-INF-022](../../03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md) |
| 40 | src/zephyr/gov_audit/genesis.py | audit-trail.genesis — MOD-INF-020 · 创世块管理 | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 41 | src/zephyr/gov_audit/glossary_matrix.py | glossary_matrix.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 42 | src/zephyr/gov_audit/incremental_review.py | incremental_review.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 43 | src/zephyr/gov_audit/indexer.py | indexer.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 44 | src/zephyr/gov_audit/integrity.py | audit-trail.integrity — MOD-INF-020 · 密码学... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 45 | src/zephyr/gov_audit/integrity_verifier.py | Integrity Verifier — v0.8.0 代码完整性验证器: ... | 生产态 / production | [MOD-INF-022](../../03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md) |
| 46 | src/zephyr/gov_audit/kb_gate.py | audit-trail.kb_gate — MOD-INF-020 · KB 审计门控 | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 47 | src/zephyr/gov_audit/log_rotation.py | log_rotation.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 48 | src/zephyr/gov_audit/merkle_audit.py | Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.g... | 生产态 / production | [MOD-INF-022](../../03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md) |
| 49 | src/zephyr/gov_audit/merkle_hourly.py | audit-trail.merkle_hourly — MOD-INF-020 · 每... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 50 | src/zephyr/gov_audit/models.py | models.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 51 | src/zephyr/gov_audit/observability_dashboard.py | observability_dashboard.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 52 | src/zephyr/gov_audit/pipeline_runner.py | pipeline_runner.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 53 | src/zephyr/gov_audit/privacy.py | audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏 | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 54 | src/zephyr/gov_audit/provenance_tracker.py | provenance_tracker.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 55 | src/zephyr/gov_audit/query.py | query.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 56 | src/zephyr/gov_audit/replay_engine.py | replay_engine.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 57 | src/zephyr/gov_audit/resource_aware_pool.py | resource_aware_pool.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 58 | src/zephyr/gov_audit/retention.py | retention.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 59 | src/zephyr/gov_audit/sbom_generator.py | LicenseType 枚举——许可证类型定义（P3 价值审判... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 60 | src/zephyr/gov_audit/spec_auditor.py | spec_auditor.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 61 | src/zephyr/gov_audit/supply_chain.py | audit-trail.supply_chain — MOD-INF-020 · 供应... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 62 | src/zephyr/gov_audit/supply_chain_security.py | supply_chain_security.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 63 | src/zephyr/gov_audit/text_to_finding_adapter.py | text_to_finding_adapter.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 64 | src/zephyr/gov_audit/tiered_storage.py | tiered_storage.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 65 | src/zephyr/gov_audit/tiered_storage_bridge.py | tiered_storage_bridge.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 66 | src/zephyr/gov_audit/trust_bridge.py | trust_bridge.py | 原型态 / prototype | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 67 | src/zephyr/gov_audit/trust_engine.py | trust_engine.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 68 | src/zephyr/gov_audit/trust_ring_manager.py | trust_ring_manager.py | 生产态 / production | [MOD-INF-024](../../03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) |
| 69 | src/zephyr/gov_audit/wqa_scorer.py | wqa_scorer.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 70 | src/zephyr/gov_audit/writer.py | writer.py | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 71 | src/zephyr/gov_enforcement/behavioral_admission/ai_code_s... | ai_code_standards.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 72 | src/zephyr/gov_enforcement/behavioral_admission/mcp_resul... | mcp_result_push.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 73 | src/zephyr/gov_enforcement/behavioral_admission/post_proc... | post_process.py —— AI 生成代码后处理管道（Pha... | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 74 | src/zephyr/gov_enforcement/behavioral_admission/vibe_codi... | vibe_coding_enforcer.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 75 | src/zephyr/gov_enforcement/rule_enforcement/audit_chain_v... | 审计链验证工具——独立重放门禁判定+Hash链完整性... | 生产态 / production | [MOD-GATE_ENGINE](../../03_modules/_cross_layer/gate_engine/blueprint.md) |
| 76 | src/zephyr/gov_enforcement/rule_enforcement/sys_master_co... | SYS-MASTER-001 Compliance Checker | 生产态 / production | [MOD-GATE_ENGINE](../../03_modules/_cross_layer/gate_engine/blueprint.md) |
| 77 | src/zephyr/governance/audit/reconciliation_registry.py | reconciliation_registry.py — GitCommitGateway ... | 生产态 / production | [MOD-INF-035](../../03_modules/_cross_layer/auto_runtime_core/blueprint.md) |
| 78 | src/zephyr/governance/audit/remediation_progress_reconcil... | remediation_progress_reconciler.py — 治本进度... | 原型态 / prototype |  |
| 79 | src/zephyr/governance/audit/snapshot_manager.py | SnapshotManager — Event Sourcing 快照管理（DW-... | 生产态 / production | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |
| 80 | src/zephyr/governance/financial_governance/financial_comp... | financial_compliance.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 81 | src/zephyr/governance/semantic_audit/alignment_engine.py | 三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs i... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 82 | src/zephyr/governance/semantic_audit/compliance_map.py | audit-trail.compliance_map — MOD-INF-020 · 合... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 83 | src/zephyr/governance/semantic_audit/feedback_self_audit.py | audit-trail.feedback_self_audit — MOD-INF-020 ... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 84 | src/zephyr/governance/semantic_audit/fix_prioritizer.py | 按 severity -> certainty -> blast_radius 三级排... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 85 | src/zephyr/governance/semantic_audit/fix_result_prioritiz... | fix_prioritizer — MOD-INF-028 §3.1 Stage 8 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 86 | src/zephyr/governance/semantic_audit/issue_aggregator.py | 收集各阶段审计结果，去重合并排序输出。 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 87 | src/zephyr/governance/semantic_audit/kb_gate.py | audit-trail.kb_gate — MOD-INF-020 · KB 审计门控 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 88 | src/zephyr/governance/semantic_audit/llm_bridge.py | 接收 RED 问题,生成修复文本。LLM 只润色不做判断... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 89 | src/zephyr/governance/semantic_audit/models.py | 语义审计管线数据模型 — MOD-INF-028 §4.2 | 生产态 / production | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 90 | src/zephyr/governance/semantic_audit/orchestrator.py | SemanticAuditor 编排器——9阶段管道统一调度. | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 91 | src/zephyr/governance/semantic_audit/privacy.py | audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 92 | src/zephyr/governance/semantic_audit/reference_extractor.py | AST 解析文件，提取 9 个维度的引用信息。 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 93 | src/zephyr/governance/semantic_audit/safety_boundary.py | 禁碰规则过滤 + 置信度阈值。输入 TriggerResult ... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 94 | src/zephyr/governance/semantic_audit/self_healer.py | Stage 7 自愈闭环 — 修复->自测->回滚. | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 95 | src/zephyr/governance/semantic_audit/self_health.py | 7 SLI + 5 容量 SLI + 退化检测。定时自检,输出 HE... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 96 | src/zephyr/governance/semantic_audit/semantic_cache.py | semantic_cache.py | 生产态 / production | [MOD-INF-024](../../03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) |
| 97 | src/zephyr/governance/semantic_audit/spec_auditor.py | G-CT-007 — Audit.record_agent_spec() 记录 Agen... | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |
| 98 | src/zephyr/governance/semantic_audit/trigger_engine.py | 监听文件变更，判定是否触发语义审计。 | 原型态 / prototype | [MOD-INF-028](../../03_modules/_cross_layer/semantic_auditor/blueprint.md) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 102 个模块（生产态 66 + 设计态 2 + 原型态 34），标签标注成熟度。

#### 第 1 页 / 共 4 页

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) docs__03_modules___cross_layer__audit_orchestrator__blueprint_md"]
        docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) docs__03_modules___domain_governance__audit_trail__blueprint_md"]
        scripts_governance_repair_audit_design_completeness_py["(原型态 / prototype) (INVARIANTS) 按path精确匹配+按功能名模糊匹配; ...<br/>文件: audit_design_completeness.py"]
        scripts_governance_repair_red_blue_test_py["(原型态 / prototype) red_blue_test.py"]
        scripts_governance_repair_rollback_depgraph_py["(原型态 / prototype) (INVARIANTS) 仅接受depgraph.backup.*路径; 回滚...<br/>文件: rollback_depgraph.py"]
        scripts_governance_test_remediation_progress_smoke_py["(原型态 / prototype) test_remediation_progress_smoke.py — Phase 3.1...<br/>文件: test_remediation_progress_smoke.py"]
        src_zephyr_gov_audit_orchestrator_compat_py["(生产态 / production) audit-orchestrator 兼容重导出层（ARCH-042 阶段4...<br/>文件: _orchestrator_compat.py"]
        src_zephyr_gov_audit_action_history_py["(生产态 / production) ActionHistory — 操作历史持久化审计 + 去重 + 循...<br/>文件: action_history.py"]
        src_zephyr_gov_audit_agent_signer_py["(生产态 / production) audit-trail.agent_signer — MOD-INF-020 · Agen...<br/>文件: agent_signer.py"]
        src_zephyr_gov_audit_anomaly_py["(生产态 / production) anomaly.py"]
        src_zephyr_gov_audit_api_lifecycle_py["(生产态 / production) api_lifecycle.py"]
        src_zephyr_gov_audit_audit_admission_controller_py["(原型态 / prototype) audit_admission_controller.py"]
        src_zephyr_gov_audit_audit_schema_py["(生产态 / production) audit_schema — 审计视图与查询入口（SH-DB-001 v...<br/>文件: audit_schema.py"]
        src_zephyr_gov_audit_audit_write_failure_protector_py["(生产态 / production) Audit Write Failure Protector — v0.13.0 审计写...<br/>文件: audit_write_failure_protector.py"]
        src_zephyr_gov_audit_bridge_py["(生产态 / production) bridge.py"]
        src_zephyr_gov_audit_bridges_audit_anomaly_py["(原型态 / prototype) G-CT-002 Audit 异常检测器 — AnomalyEvent Pydan...<br/>文件: audit_anomaly.py"]
        src_zephyr_gov_audit_bridges_audit_contracts_py["(原型态 / prototype) G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: audit_contracts.py"]
        src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["(生产态 / production) Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: audit_delegation_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_drift_bridge_py["(原型态 / prototype) G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020...<br/>文件: audit_drift_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["(生产态 / production) Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: audit_feedback_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["(生产态 / production) Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: audit_tiered_storage_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_trust_bridge_py["(生产态 / production) Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: audit_trust_bridge.py"]
        src_zephyr_gov_audit_changelog_manager_py["(生产态 / production) changelog_manager.py"]
        src_zephyr_gov_audit_cli_py["(生产态 / production) cli.py"]
        src_zephyr_gov_audit_code_archaeology_py["(生产态 / production) code_archaeology.py"]
        src_zephyr_gov_audit_cold_start_py["(生产态 / production) cold_start.py"]
        src_zephyr_gov_audit_compliance_map_py["(生产态 / production) audit-trail.compliance_map — MOD-INF-020 · 合...<br/>文件: compliance_map.py"]
        src_zephyr_gov_audit_contracts_py["(生产态 / production) contracts.py"]
        src_zephyr_gov_audit_corporate_actions_py["(生产态 / production) corporate_actions.py"]
        src_zephyr_gov_audit_delegation_auditor_py["(生产态 / production) delegation_auditor.py"]
    end
    src_zephyr_gov_audit_cli_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    D_GOV_DOCS["(设计态 / design) D_GOV_DOCS"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DOCS
    D_GOV_CODE_QUALITY["(原型态 / prototype) D_GOV_CODE_QUALITY"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_CODE_QUALITY
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|contract / contract| D_GOV_DOCS
    D_GOV_DRIFT["(设计态 / design) D_GOV_DRIFT"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DRIFT
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md -.->|runtime / runtime| D_GOV_DOCS
    D_SHARED["(生产态 / production) D_SHARED"]
    scripts_governance_repair_rollback_depgraph_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_agent_signer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_audit_schema_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SECURITY["(原型态 / prototype) D_SECURITY"]
    src_zephyr_gov_audit_cli_py -.->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DRIFT -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    D_GOV_RULE -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_schema_py
    D_GOV_DRIFT -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    D_INFRA_RECOVERY["(原型态 / prototype) D_INFRA_RECOVERY"]
    D_INFRA_RECOVERY -.->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py production
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md,scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py design
    class D_SHARED,D_GOVERNANCE,D_GOV_RULE,D_INFRA_RUNTIME external_prod
    class D_GOV_DOCS,D_GOV_CODE_QUALITY,D_GOV_DRIFT,D_SECURITY,D_INFRA_RECOVERY external_design
```

#### 第 2 页 / 共 4 页

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        src_zephyr_gov_audit_delegation_bridge_py["(原型态 / prototype) delegation_bridge.py"]
        src_zephyr_gov_audit_dora_metrics_py["(生产态 / production) dora_metrics.py"]
        src_zephyr_gov_audit_event_store_py["(生产态 / production) EventStore — Event Sourcing 事件追加与回放（DW...<br/>文件: event_store.py"]
        src_zephyr_gov_audit_evidence_pack_py["(生产态 / production) audit-trail.evidence_pack — MOD-INF-020 · 证...<br/>文件: evidence_pack.py"]
        src_zephyr_gov_audit_external_tool_audit_py["(生产态 / production) external_tool_audit.py"]
        src_zephyr_gov_audit_feedback_bridge_py["(生产态 / production) feedback_bridge.py"]
        src_zephyr_gov_audit_feedback_policy_py["(生产态 / production) feedback_policy.py"]
        src_zephyr_gov_audit_feedback_self_audit_py["(生产态 / production) audit-trail.feedback_self_audit — MOD-INF-020 ...<br/>文件: feedback_self_audit.py"]
        src_zephyr_gov_audit_finding_ingest_py["(原型态 / prototype) finding_ingest.py"]
        src_zephyr_gov_audit_finding_model_py["(原型态 / prototype) finding_model.py"]
        src_zephyr_gov_audit_forensic_package_py["(生产态 / production) Forensic Package — v0.8.0 取证就绪: escalation...<br/>文件: forensic_package.py"]
        src_zephyr_gov_audit_genesis_py["(生产态 / production) audit-trail.genesis — MOD-INF-020 · 创世块管理<br/>文件: genesis.py"]
        src_zephyr_gov_audit_glossary_matrix_py["(生产态 / production) glossary_matrix.py"]
        src_zephyr_gov_audit_incremental_review_py["(生产态 / production) incremental_review.py"]
        src_zephyr_gov_audit_indexer_py["(生产态 / production) indexer.py"]
        src_zephyr_gov_audit_integrity_py["(生产态 / production) audit-trail.integrity — MOD-INF-020 · 密码学...<br/>文件: integrity.py"]
        src_zephyr_gov_audit_integrity_verifier_py["(生产态 / production) Integrity Verifier — v0.8.0 代码完整性验证器: ...<br/>文件: integrity_verifier.py"]
        src_zephyr_gov_audit_kb_gate_py["(原型态 / prototype) audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: kb_gate.py"]
        src_zephyr_gov_audit_log_rotation_py["(生产态 / production) log_rotation.py"]
        src_zephyr_gov_audit_merkle_audit_py["(生产态 / production) Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.g...<br/>文件: merkle_audit.py"]
        src_zephyr_gov_audit_merkle_hourly_py["(生产态 / production) audit-trail.merkle_hourly — MOD-INF-020 · 每...<br/>文件: merkle_hourly.py"]
        src_zephyr_gov_audit_models_py["(生产态 / production) models.py"]
        src_zephyr_gov_audit_observability_dashboard_py["(生产态 / production) observability_dashboard.py"]
        src_zephyr_gov_audit_pipeline_runner_py["(生产态 / production) pipeline_runner.py"]
        src_zephyr_gov_audit_privacy_py["(生产态 / production) audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏<br/>文件: privacy.py"]
        src_zephyr_gov_audit_provenance_tracker_py["(生产态 / production) provenance_tracker.py"]
        src_zephyr_gov_audit_query_py["(生产态 / production) query.py"]
        src_zephyr_gov_audit_replay_engine_py["(生产态 / production) replay_engine.py"]
        src_zephyr_gov_audit_resource_aware_pool_py["(原型态 / prototype) resource_aware_pool.py"]
        src_zephyr_gov_audit_retention_py["(生产态 / production) retention.py"]
    end
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_finding_ingest_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_pipeline_runner_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    src_zephyr_gov_audit_delegation_bridge_py -.->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_audit_finding_ingest_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_finding_model_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_feedback_bridge_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    src_zephyr_gov_audit_feedback_bridge_py -->|导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_evidence_pack_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_evidence_pack_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_forensic_package_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_kb_gate_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_log_rotation_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY"]
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_GOV_SCRIPTS["(原型态 / prototype) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_ENFORCEMENT["(原型态 / prototype) D_GOV_ENFORCEMENT"]
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    D_SECURITY["(生产态 / production) D_SECURITY"]
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_retention_py production
    class src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_resource_aware_pool_py design
    class D_GOV_OPS_RESILIENCE,D_SHARED,D_FEEDBACK_LOOP,D_GOVERNANCE,D_INFRA_RECOVERY,D_TRADING,D_GOV_DRIFT,D_SECURITY,D_INFRA_RUNTIME external_prod
    class D_GOV_SCRIPTS,D_GOV_ENFORCEMENT external_design
```

#### 第 3 页 / 共 4 页

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        src_zephyr_gov_audit_sbom_generator_py["(生产态 / production) LicenseType 枚举——许可证类型定义（P3 价值审判...<br/>文件: sbom_generator.py"]
        src_zephyr_gov_audit_spec_auditor_py["(生产态 / production) spec_auditor.py"]
        src_zephyr_gov_audit_supply_chain_py["(生产态 / production) audit-trail.supply_chain — MOD-INF-020 · 供应...<br/>文件: supply_chain.py"]
        src_zephyr_gov_audit_supply_chain_security_py["(生产态 / production) supply_chain_security.py"]
        src_zephyr_gov_audit_text_to_finding_adapter_py["(原型态 / prototype) text_to_finding_adapter.py"]
        src_zephyr_gov_audit_tiered_storage_py["(生产态 / production) tiered_storage.py"]
        src_zephyr_gov_audit_tiered_storage_bridge_py["(原型态 / prototype) tiered_storage_bridge.py"]
        src_zephyr_gov_audit_trust_bridge_py["(原型态 / prototype) trust_bridge.py"]
        src_zephyr_gov_audit_trust_engine_py["(生产态 / production) trust_engine.py"]
        src_zephyr_gov_audit_trust_ring_manager_py["(生产态 / production) trust_ring_manager.py"]
        src_zephyr_gov_audit_wqa_scorer_py["(生产态 / production) wqa_scorer.py"]
        src_zephyr_gov_audit_writer_py["(生产态 / production) writer.py"]
        src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["(生产态 / production) ai_code_standards.py"]
        src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["(生产态 / production) mcp_result_push.py"]
        src_zephyr_gov_enforcement_behavioral_admission_post_process_py["(生产态 / production) post_process.py —— AI 生成代码后处理管道（Pha...<br/>文件: post_process.py"]
        src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["(生产态 / production) vibe_coding_enforcer.py"]
        src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["(生产态 / production) 审计链验证工具——独立重放门禁判定+Hash链完整性...<br/>文件: audit_chain_verifier.py"]
        src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["(生产态 / production) SYS-MASTER-001 Compliance Checker<br/>文件: sys_master_compliance.py"]
        src_zephyr_governance_audit_default_attribution_engine_py["(原型态 / prototype) Re-export wrapper: default_attribution_engine c...<br/>文件: default_attribution_engine.py"]
        src_zephyr_governance_audit_default_tca_engine_py["(生产态 / production) Re-export wrapper: default_tca_engine canonical...<br/>文件: default_tca_engine.py"]
        src_zephyr_governance_audit_reconciliation_registry_py["(生产态 / production) reconciliation_registry.py — GitCommitGateway ...<br/>文件: reconciliation_registry.py"]
        src_zephyr_governance_audit_remediation_progress_reconciler_py["(原型态 / prototype) remediation_progress_reconciler.py — 治本进度...<br/>文件: remediation_progress_reconciler.py"]
        src_zephyr_governance_audit_snapshot_manager_py["(生产态 / production) SnapshotManager — Event Sourcing 快照管理（DW-...<br/>文件: snapshot_manager.py"]
        src_zephyr_governance_financial_governance_financial_compliance_py["(生产态 / production) financial_compliance.py"]
        src_zephyr_governance_semantic_audit_alignment_engine_py["(原型态 / prototype) 三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs i...<br/>文件: alignment_engine.py"]
        src_zephyr_governance_semantic_audit_compliance_map_py["(原型态 / prototype) audit-trail.compliance_map — MOD-INF-020 · 合...<br/>文件: compliance_map.py"]
        src_zephyr_governance_semantic_audit_feedback_self_audit_py["(原型态 / prototype) audit-trail.feedback_self_audit — MOD-INF-020 ...<br/>文件: feedback_self_audit.py"]
        src_zephyr_governance_semantic_audit_fix_prioritizer_py["(原型态 / prototype) 按 severity -> certainty -> blast_radius 三级排...<br/>文件: fix_prioritizer.py"]
        src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["(原型态 / prototype) fix_prioritizer — MOD-INF-028 §3.1 Stage 8<br/>文件: fix_result_prioritizer.py"]
        src_zephyr_governance_semantic_audit_issue_aggregator_py["(原型态 / prototype) 收集各阶段审计结果，去重合并排序输出。<br/>文件: issue_aggregator.py"]
    end
    src_zephyr_governance_audit_remediation_progress_reconciler_py -.->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_gov_audit_tiered_storage_bridge_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_trust_bridge_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_audit_remediation_progress_reconciler_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_audit_text_to_finding_adapter_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    src_zephyr_governance_semantic_audit_issue_aggregator_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| D_GOV_RULE
    D_REPORTING["(原型态 / prototype) D_REPORTING"]
    src_zephyr_governance_audit_default_tca_engine_py -.->|导入依赖 / import_depends| D_REPORTING
    D_GOV_SCRIPTS["(原型态 / prototype) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY"]
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    D_INFRASTRUCTURE -.->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_financial_governance_financial_compliance_py production
    class src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py design
    class D_GOV_CODE_QUALITY,D_SHARED,D_GOVERNANCE,D_SECURITY,D_GOV_ENFORCEMENT,D_GOV_RULE,D_GOV_OPS_RESILIENCE,D_INFRA_RECOVERY,D_INFRA_RUNTIME,D_INTEGRATION external_prod
    class D_REPORTING,D_GOV_SCRIPTS,D_INFRASTRUCTURE external_design
```

#### 第 4 页 / 共 4 页

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        src_zephyr_governance_semantic_audit_kb_gate_py["(原型态 / prototype) audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: kb_gate.py"]
        src_zephyr_governance_semantic_audit_llm_bridge_py["(原型态 / prototype) 接收 RED 问题,生成修复文本。LLM 只润色不做判断...<br/>文件: llm_bridge.py"]
        src_zephyr_governance_semantic_audit_models_py["(生产态 / production) 语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: models.py"]
        src_zephyr_governance_semantic_audit_orchestrator_py["(原型态 / prototype) SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: orchestrator.py"]
        src_zephyr_governance_semantic_audit_privacy_py["(原型态 / prototype) audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏<br/>文件: privacy.py"]
        src_zephyr_governance_semantic_audit_reference_extractor_py["(原型态 / prototype) AST 解析文件，提取 9 个维度的引用信息。<br/>文件: reference_extractor.py"]
        src_zephyr_governance_semantic_audit_safety_boundary_py["(原型态 / prototype) 禁碰规则过滤 + 置信度阈值。输入 TriggerResult ...<br/>文件: safety_boundary.py"]
        src_zephyr_governance_semantic_audit_self_healer_py["(原型态 / prototype) Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: self_healer.py"]
        src_zephyr_governance_semantic_audit_self_health_py["(原型态 / prototype) 7 SLI + 5 容量 SLI + 退化检测。定时自检,输出 HE...<br/>文件: self_health.py"]
        src_zephyr_governance_semantic_audit_semantic_cache_py["(生产态 / production) semantic_cache.py"]
        src_zephyr_governance_semantic_audit_spec_auditor_py["(原型态 / prototype) G-CT-007 — Audit.record_agent_spec() 记录 Agen...<br/>文件: spec_auditor.py"]
        src_zephyr_governance_semantic_audit_trigger_engine_py["(原型态 / prototype) 监听文件变更，判定是否触发语义审计。<br/>文件: trigger_engine.py"]
    end
    src_zephyr_governance_semantic_audit_llm_bridge_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_reference_extractor_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_safety_boundary_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_governance_semantic_audit_privacy_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_semantic_audit_kb_gate_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_governance_semantic_audit_self_healer_py -.->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(原型态 / prototype) D_INTEGRATION"]
    D_INTEGRATION -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_semantic_cache_py production
    class src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py design
    class D_GOVERNANCE,D_GOV_OPS_RESILIENCE external_prod
    class D_SHARED,D_INTEGRATION external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 66 个，29 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        src_zephyr_gov_audit_orchestrator_compat_py["(生产态 / production) audit-orchestrator 兼容重导出层（ARCH-042 阶段4...<br/>文件: _orchestrator_compat.py"]
        src_zephyr_gov_audit_action_history_py["(生产态 / production) ActionHistory — 操作历史持久化审计 + 去重 + 循...<br/>文件: action_history.py"]
        src_zephyr_gov_audit_agent_signer_py["(生产态 / production) audit-trail.agent_signer — MOD-INF-020 · Agen...<br/>文件: agent_signer.py"]
        src_zephyr_gov_audit_anomaly_py["(生产态 / production) anomaly.py"]
        src_zephyr_gov_audit_api_lifecycle_py["(生产态 / production) api_lifecycle.py"]
        src_zephyr_gov_audit_audit_schema_py["(生产态 / production) audit_schema — 审计视图与查询入口（SH-DB-001 v...<br/>文件: audit_schema.py"]
        src_zephyr_gov_audit_audit_write_failure_protector_py["(生产态 / production) Audit Write Failure Protector — v0.13.0 审计写...<br/>文件: audit_write_failure_protector.py"]
        src_zephyr_gov_audit_bridge_py["(生产态 / production) bridge.py"]
        src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["(生产态 / production) Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: audit_delegation_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["(生产态 / production) Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: audit_feedback_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["(生产态 / production) Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: audit_tiered_storage_bridge.py"]
        src_zephyr_gov_audit_bridges_audit_trust_bridge_py["(生产态 / production) Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: audit_trust_bridge.py"]
        src_zephyr_gov_audit_changelog_manager_py["(生产态 / production) changelog_manager.py"]
        src_zephyr_gov_audit_cli_py["(生产态 / production) cli.py"]
        src_zephyr_gov_audit_code_archaeology_py["(生产态 / production) code_archaeology.py"]
        src_zephyr_gov_audit_cold_start_py["(生产态 / production) cold_start.py"]
        src_zephyr_gov_audit_compliance_map_py["(生产态 / production) audit-trail.compliance_map — MOD-INF-020 · 合...<br/>文件: compliance_map.py"]
        src_zephyr_gov_audit_contracts_py["(生产态 / production) contracts.py"]
        src_zephyr_gov_audit_corporate_actions_py["(生产态 / production) corporate_actions.py"]
        src_zephyr_gov_audit_delegation_auditor_py["(生产态 / production) delegation_auditor.py"]
        src_zephyr_gov_audit_dora_metrics_py["(生产态 / production) dora_metrics.py"]
        src_zephyr_gov_audit_event_store_py["(生产态 / production) EventStore — Event Sourcing 事件追加与回放（DW...<br/>文件: event_store.py"]
        src_zephyr_gov_audit_evidence_pack_py["(生产态 / production) audit-trail.evidence_pack — MOD-INF-020 · 证...<br/>文件: evidence_pack.py"]
        src_zephyr_gov_audit_external_tool_audit_py["(生产态 / production) external_tool_audit.py"]
        src_zephyr_gov_audit_feedback_bridge_py["(生产态 / production) feedback_bridge.py"]
        src_zephyr_gov_audit_feedback_policy_py["(生产态 / production) feedback_policy.py"]
        src_zephyr_gov_audit_feedback_self_audit_py["(生产态 / production) audit-trail.feedback_self_audit — MOD-INF-020 ...<br/>文件: feedback_self_audit.py"]
        src_zephyr_gov_audit_forensic_package_py["(生产态 / production) Forensic Package — v0.8.0 取证就绪: escalation...<br/>文件: forensic_package.py"]
        src_zephyr_gov_audit_genesis_py["(生产态 / production) audit-trail.genesis — MOD-INF-020 · 创世块管理<br/>文件: genesis.py"]
        src_zephyr_gov_audit_glossary_matrix_py["(生产态 / production) glossary_matrix.py"]
        src_zephyr_gov_audit_incremental_review_py["(生产态 / production) incremental_review.py"]
        src_zephyr_gov_audit_indexer_py["(生产态 / production) indexer.py"]
        src_zephyr_gov_audit_integrity_py["(生产态 / production) audit-trail.integrity — MOD-INF-020 · 密码学...<br/>文件: integrity.py"]
        src_zephyr_gov_audit_integrity_verifier_py["(生产态 / production) Integrity Verifier — v0.8.0 代码完整性验证器: ...<br/>文件: integrity_verifier.py"]
        src_zephyr_gov_audit_log_rotation_py["(生产态 / production) log_rotation.py"]
        src_zephyr_gov_audit_merkle_audit_py["(生产态 / production) Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.g...<br/>文件: merkle_audit.py"]
        src_zephyr_gov_audit_merkle_hourly_py["(生产态 / production) audit-trail.merkle_hourly — MOD-INF-020 · 每...<br/>文件: merkle_hourly.py"]
        src_zephyr_gov_audit_models_py["(生产态 / production) models.py"]
        src_zephyr_gov_audit_observability_dashboard_py["(生产态 / production) observability_dashboard.py"]
        src_zephyr_gov_audit_pipeline_runner_py["(生产态 / production) pipeline_runner.py"]
        src_zephyr_gov_audit_privacy_py["(生产态 / production) audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏<br/>文件: privacy.py"]
        src_zephyr_gov_audit_provenance_tracker_py["(生产态 / production) provenance_tracker.py"]
        src_zephyr_gov_audit_query_py["(生产态 / production) query.py"]
        src_zephyr_gov_audit_replay_engine_py["(生产态 / production) replay_engine.py"]
        src_zephyr_gov_audit_retention_py["(生产态 / production) retention.py"]
        src_zephyr_gov_audit_sbom_generator_py["(生产态 / production) LicenseType 枚举——许可证类型定义（P3 价值审判...<br/>文件: sbom_generator.py"]
        src_zephyr_gov_audit_spec_auditor_py["(生产态 / production) spec_auditor.py"]
        src_zephyr_gov_audit_supply_chain_py["(生产态 / production) audit-trail.supply_chain — MOD-INF-020 · 供应...<br/>文件: supply_chain.py"]
        src_zephyr_gov_audit_supply_chain_security_py["(生产态 / production) supply_chain_security.py"]
        src_zephyr_gov_audit_tiered_storage_py["(生产态 / production) tiered_storage.py"]
        src_zephyr_gov_audit_trust_engine_py["(生产态 / production) trust_engine.py"]
        src_zephyr_gov_audit_trust_ring_manager_py["(生产态 / production) trust_ring_manager.py"]
        src_zephyr_gov_audit_wqa_scorer_py["(生产态 / production) wqa_scorer.py"]
        src_zephyr_gov_audit_writer_py["(生产态 / production) writer.py"]
        src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["(生产态 / production) ai_code_standards.py"]
        src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["(生产态 / production) mcp_result_push.py"]
        src_zephyr_gov_enforcement_behavioral_admission_post_process_py["(生产态 / production) post_process.py —— AI 生成代码后处理管道（Pha...<br/>文件: post_process.py"]
        src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["(生产态 / production) vibe_coding_enforcer.py"]
        src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["(生产态 / production) 审计链验证工具——独立重放门禁判定+Hash链完整性...<br/>文件: audit_chain_verifier.py"]
        src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["(生产态 / production) SYS-MASTER-001 Compliance Checker<br/>文件: sys_master_compliance.py"]
        src_zephyr_governance_audit_default_tca_engine_py["(生产态 / production) Re-export wrapper: default_tca_engine canonical...<br/>文件: default_tca_engine.py"]
        src_zephyr_governance_audit_reconciliation_registry_py["(生产态 / production) reconciliation_registry.py — GitCommitGateway ...<br/>文件: reconciliation_registry.py"]
        src_zephyr_governance_audit_snapshot_manager_py["(生产态 / production) SnapshotManager — Event Sourcing 快照管理（DW-...<br/>文件: snapshot_manager.py"]
        src_zephyr_governance_financial_governance_financial_compliance_py["(生产态 / production) financial_compliance.py"]
        src_zephyr_governance_semantic_audit_models_py["(生产态 / production) 语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: models.py"]
        src_zephyr_governance_semantic_audit_semantic_cache_py["(生产态 / production) semantic_cache.py"]
    end
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    src_zephyr_gov_audit_audit_write_failure_protector_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_agent_signer_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    src_zephyr_gov_audit_feedback_bridge_py -->|导入依赖 / import_depends| D_FEEDBACK_LOOP
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_feedback_bridge_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_agent_signer_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS["(原型态 / prototype) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY"]
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    D_INFRASTRUCTURE -.->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py,src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_retention_py,src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_financial_governance_financial_compliance_py,src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_semantic_cache_py production
    class D_GOV_CODE_QUALITY,D_SHARED,D_FEEDBACK_LOOP,D_GOVERNANCE,D_SECURITY,D_GOV_ENFORCEMENT,D_GOV_OPS_RESILIENCE,D_INFRA_RECOVERY,D_INFRA_RUNTIME,D_TRADING external_prod
    class D_GOV_SCRIPTS,D_INFRASTRUCTURE external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) docs__03_modules___cross_layer__audit_orchestrator__blueprint_md"]
        docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) docs__03_modules___domain_governance__audit_trail__blueprint_md"]
    end
    D_GOV_DOCS["(设计态 / design) D_GOV_DOCS"]
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md -.->|runtime / runtime| D_GOV_DOCS
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DOCS
    D_GOV_CODE_QUALITY["(原型态 / prototype) D_GOV_CODE_QUALITY"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_CODE_QUALITY
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|contract / contract| D_GOV_DOCS
    D_GOV_DRIFT["(设计态 / design) D_GOV_DRIFT"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DRIFT
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DRIFT -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DOCS -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
    class D_GOV_DOCS,D_GOV_CODE_QUALITY,D_GOV_DRIFT external_design
```

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 34 个，16 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        scripts_governance_repair_audit_design_completeness_py["(原型态 / prototype) (INVARIANTS) 按path精确匹配+按功能名模糊匹配; ...<br/>文件: audit_design_completeness.py"]
        scripts_governance_repair_red_blue_test_py["(原型态 / prototype) red_blue_test.py"]
        scripts_governance_repair_rollback_depgraph_py["(原型态 / prototype) (INVARIANTS) 仅接受depgraph.backup.*路径; 回滚...<br/>文件: rollback_depgraph.py"]
        scripts_governance_test_remediation_progress_smoke_py["(原型态 / prototype) test_remediation_progress_smoke.py — Phase 3.1...<br/>文件: test_remediation_progress_smoke.py"]
        src_zephyr_gov_audit_audit_admission_controller_py["(原型态 / prototype) audit_admission_controller.py"]
        src_zephyr_gov_audit_bridges_audit_anomaly_py["(原型态 / prototype) G-CT-002 Audit 异常检测器 — AnomalyEvent Pydan...<br/>文件: audit_anomaly.py"]
        src_zephyr_gov_audit_bridges_audit_contracts_py["(原型态 / prototype) G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: audit_contracts.py"]
        src_zephyr_gov_audit_bridges_audit_drift_bridge_py["(原型态 / prototype) G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020...<br/>文件: audit_drift_bridge.py"]
        src_zephyr_gov_audit_delegation_bridge_py["(原型态 / prototype) delegation_bridge.py"]
        src_zephyr_gov_audit_finding_ingest_py["(原型态 / prototype) finding_ingest.py"]
        src_zephyr_gov_audit_finding_model_py["(原型态 / prototype) finding_model.py"]
        src_zephyr_gov_audit_kb_gate_py["(原型态 / prototype) audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: kb_gate.py"]
        src_zephyr_gov_audit_resource_aware_pool_py["(原型态 / prototype) resource_aware_pool.py"]
        src_zephyr_gov_audit_text_to_finding_adapter_py["(原型态 / prototype) text_to_finding_adapter.py"]
        src_zephyr_gov_audit_tiered_storage_bridge_py["(原型态 / prototype) tiered_storage_bridge.py"]
        src_zephyr_gov_audit_trust_bridge_py["(原型态 / prototype) trust_bridge.py"]
        src_zephyr_governance_audit_default_attribution_engine_py["(原型态 / prototype) Re-export wrapper: default_attribution_engine c...<br/>文件: default_attribution_engine.py"]
        src_zephyr_governance_audit_remediation_progress_reconciler_py["(原型态 / prototype) remediation_progress_reconciler.py — 治本进度...<br/>文件: remediation_progress_reconciler.py"]
        src_zephyr_governance_semantic_audit_alignment_engine_py["(原型态 / prototype) 三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs i...<br/>文件: alignment_engine.py"]
        src_zephyr_governance_semantic_audit_compliance_map_py["(原型态 / prototype) audit-trail.compliance_map — MOD-INF-020 · 合...<br/>文件: compliance_map.py"]
        src_zephyr_governance_semantic_audit_feedback_self_audit_py["(原型态 / prototype) audit-trail.feedback_self_audit — MOD-INF-020 ...<br/>文件: feedback_self_audit.py"]
        src_zephyr_governance_semantic_audit_fix_prioritizer_py["(原型态 / prototype) 按 severity -> certainty -> blast_radius 三级排...<br/>文件: fix_prioritizer.py"]
        src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["(原型态 / prototype) fix_prioritizer — MOD-INF-028 §3.1 Stage 8<br/>文件: fix_result_prioritizer.py"]
        src_zephyr_governance_semantic_audit_issue_aggregator_py["(原型态 / prototype) 收集各阶段审计结果，去重合并排序输出。<br/>文件: issue_aggregator.py"]
        src_zephyr_governance_semantic_audit_kb_gate_py["(原型态 / prototype) audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: kb_gate.py"]
        src_zephyr_governance_semantic_audit_llm_bridge_py["(原型态 / prototype) 接收 RED 问题,生成修复文本。LLM 只润色不做判断...<br/>文件: llm_bridge.py"]
        src_zephyr_governance_semantic_audit_orchestrator_py["(原型态 / prototype) SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: orchestrator.py"]
        src_zephyr_governance_semantic_audit_privacy_py["(原型态 / prototype) audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏<br/>文件: privacy.py"]
        src_zephyr_governance_semantic_audit_reference_extractor_py["(原型态 / prototype) AST 解析文件，提取 9 个维度的引用信息。<br/>文件: reference_extractor.py"]
        src_zephyr_governance_semantic_audit_safety_boundary_py["(原型态 / prototype) 禁碰规则过滤 + 置信度阈值。输入 TriggerResult ...<br/>文件: safety_boundary.py"]
        src_zephyr_governance_semantic_audit_self_healer_py["(原型态 / prototype) Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: self_healer.py"]
        src_zephyr_governance_semantic_audit_self_health_py["(原型态 / prototype) 7 SLI + 5 容量 SLI + 退化检测。定时自检,输出 HE...<br/>文件: self_health.py"]
        src_zephyr_governance_semantic_audit_spec_auditor_py["(原型态 / prototype) G-CT-007 — Audit.record_agent_spec() 记录 Agen...<br/>文件: spec_auditor.py"]
        src_zephyr_governance_semantic_audit_trigger_engine_py["(原型态 / prototype) 监听文件变更，判定是否触发语义审计。<br/>文件: trigger_engine.py"]
    end
    src_zephyr_governance_semantic_audit_alignment_engine_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -.->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_audit_admission_controller_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_audit_admission_controller_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_ingest_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_text_to_finding_adapter_py -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    scripts_governance_test_remediation_progress_smoke_py -.->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    D_SHARED["(生产态 / production) D_SHARED"]
    scripts_governance_repair_rollback_depgraph_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_finding_model_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_governance_semantic_audit_privacy_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_semantic_audit_kb_gate_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_audit_remediation_progress_reconciler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_text_to_finding_adapter_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_semantic_audit_issue_aggregator_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_semantic_audit_self_healer_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_finding_ingest_py -.->|导入依赖 / import_depends| D_SHARED
    D_REPORTING["(原型态 / prototype) D_REPORTING"]
    src_zephyr_governance_audit_default_attribution_engine_py -.->|导入依赖 / import_depends| D_REPORTING
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    src_zephyr_gov_audit_delegation_bridge_py -.->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_gov_audit_kb_gate_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    D_SECURITY["(生产态 / production) D_SECURITY"]
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    D_GOV_DRIFT -.->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_bridge_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py,src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_resource_aware_pool_py,src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py,src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py design
    class D_SHARED,D_GOV_DRIFT,D_GOVERNANCE,D_GOV_OPS_RESILIENCE,D_GOV_ENFORCEMENT,D_SECURITY,D_INFRA_RUNTIME external_prod
    class D_REPORTING external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | feedback_bridge.py | → | D_FEEDBACK_LOOP 反馈循环引擎: Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 导入依赖 / import_depends |
| 2 | audit_schema — 审计视图与查询入口（SH-DB-001 v... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 3 | Audit ↔ ContinuousTrust 信任分数桥接. (audit_t... | → | D_GOVERNANCE 生命周期管理: Continuous Trust Ledger — 持续信任评估引擎。 (... | 导入依赖 / import_depends |
| 4 | EventStore — Event Sourcing 事件追加与回放（DW... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 5 | audit-trail.evidence_pack — MOD-INF-020 · 证.... | → | D_GOVERNANCE 生命周期管理: evidence_pack.py | 导入依赖 / import_depends |
| 6 | audit-trail.kb_gate — MOD-INF-020 · KB 审计门... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式... | 导入依赖 / import_depends |
| 7 | audit-trail.privacy — MOD-INF-020 · PII 检测... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式... | 导入依赖 / import_depends |
| 8 | spec_auditor.py | → | D_GOVERNANCE 生命周期管理: G-CT-003 契约：Agent Spec -> RBAC 能力检查. (re... | 导入依赖 / import_depends |
| 9 | reconciliation_registry.py — GitCommitGateway ... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (depgraph_... | 导入依赖 / import_depends |
| 10 | SnapshotManager — Event Sourcing 快照管理（DW-... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 11 | audit-trail.kb_gate — MOD-INF-020 · KB 审计门... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式... | 导入依赖 / import_depends |
| 12 | audit-trail.privacy — MOD-INF-020 · PII 检测... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式... | 导入依赖 / import_depends |
| 13 | blueprint.md | → | D_GOV_CODE_QUALITY 代码质量治理: ch_final_gate.py — ch_writer.query() 直接调用.... | runtime / runtime |
| 14 | reconciliation_registry.py — GitCommitGateway ... | → | D_GOV_CODE_QUALITY 代码质量治理: scripts_import_integrity_gate.py — _shared.con... | 导入依赖 / import_depends |
| 15 | reconciliation_registry.py — GitCommitGateway ... | → | D_GOV_CODE_QUALITY 代码质量治理: undefined_name_gate.py — UNDEFINED-NAME 门禁（... | 导入依赖 / import_depends |
| 16 | blueprint.md | → | D_GOV_DOCS 架构文档治理: blueprint.md | runtime / runtime |
| 17 | blueprint.md | → | D_GOV_DOCS 架构文档治理: blueprint.md | runtime / runtime |
| 18 | blueprint.md | → | D_GOV_DOCS 架构文档治理: blueprint.md | contract / contract |
| 19 | blueprint.md | → | D_GOV_DRIFT 漂移检测: blueprint.md | runtime / runtime |
| 20 | audit-orchestrator 兼容重导出层（ARCH-042 阶段4... | → | D_GOV_DRIFT 漂移检测: self_monitor.py | 导入依赖 / import_depends |
| 21 | bridge.py | → | D_GOV_DRIFT 漂移检测: drift_bridge.py | 导入依赖 / import_depends |
| 22 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020... | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | 导入依赖 / import_depends |
| 23 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020... | → | D_GOV_DRIFT 漂移检测: Drift Detector 数据模型 — drift_models.py (dri... | 导入依赖 / import_depends |
| 24 | cli.py | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | 导入依赖 / import_depends |
| 25 | cli.py | → | D_GOV_DRIFT 漂移检测: integrity.py | 导入依赖 / import_depends |
| 26 | Merkle Audit — 兼容别名，SSoT已迁移至 zephyr.g... | → | D_GOV_DRIFT 漂移检测: integrity.py | 导入依赖 / import_depends |
| 27 | reconciliation_registry.py — GitCommitGateway ... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | 导入依赖 / import_depends |
| 28 | delegation_bridge.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Escalation Engine — MOD-INF-022 (escalation_en... | 导入依赖 / import_depends |
| 29 | pipeline_runner.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | 导入依赖 / import_depends |
| 30 | 审计链验证工具——独立重放门禁判定+Hash链完整性... | → | D_GOV_RULE 规则治理: 门禁上下文传播——GateContext 构建/序列化/跨模.... | 导入依赖 / import_depends |
| 31 | Re-export wrapper: default_attribution_engine c... | → | D_REPORTING 报告: D_REPORTING — Default Attribution Engine (defa... | 导入依赖 / import_depends |
| 32 | Re-export wrapper: default_tca_engine canonical... | → | D_REPORTING 报告: D_REPORTING — Default TCA Engine (default_tca_... | 导入依赖 / import_depends |
| 33 | cli.py | → | D_SECURITY 对抗验证: judge.py | 导入依赖 / import_depends |
| 34 | cli.py | → | D_SECURITY 对抗验证: validator.py | 导入依赖 / import_depends |
| 35 | reconciliation_registry.py — GitCommitGateway ... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (sessio... | 导入依赖 / import_depends |
| 36 | [INVARIANTS] 仅接受depgraph.backup.*路径; 回滚.... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 37 | audit-trail.agent_signer — MOD-INF-020 · Agen... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 38 | audit_schema — 审计视图与查询入口（SH-DB-001 v... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 39 | audit_schema — 审计视图与查询入口（SH-DB-001 v... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (sqlite_factory.py) | 导入依赖 / import_depends |
| 40 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 41 | cli.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 42 | cold_start.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 43 | cold_start.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 44 | EventStore — Event Sourcing 事件追加与回放（DW... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 45 | audit-trail.evidence_pack — MOD-INF-020 · 证.... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 46 | feedback_bridge.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 47 | finding_ingest.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 48 | finding_model.py | → | D_SHARED 共享服务: base_config.py | 导入依赖 / import_depends |
| 49 | Forensic Package — v0.8.0 取证就绪: escalation... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 50 | indexer.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 51 | indexer.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 52 | audit-trail.integrity — MOD-INF-020 · 密码学.... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 53 | audit-trail.integrity — MOD-INF-020 · 密码学.... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 54 | log_rotation.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 55 | audit-trail.merkle_hourly — MOD-INF-020 · 每.... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 56 | pipeline_runner.py | → | D_SHARED 共享服务: base_config.py | 导入依赖 / import_depends |
| 57 | query.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 58 | replay_engine.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 59 | replay_engine.py | → | D_SHARED 共享服务: streaming_reader.py - Memory-efficient streamin... | 导入依赖 / import_depends |
| 60 | replay_engine.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 61 | retention.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 62 | text_to_finding_adapter.py | → | D_SHARED 共享服务: base_config.py | 导入依赖 / import_depends |
| 63 | writer.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 64 | writer.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 65 | mcp_result_push.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 66 | 审计链验证工具——独立重放门禁判定+Hash链完整性... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 67 | SYS-MASTER-001 Compliance Checker (sys_master_c... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 68 | reconciliation_registry.py — GitCommitGateway ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 69 | reconciliation_registry.py — GitCommitGateway ... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 70 | remediation_progress_reconciler.py — 治本进度.... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 71 | SnapshotManager — Event Sourcing 快照管理（DW-... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 72 | SnapshotManager — Event Sourcing 快照管理（DW-... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 73 | 收集各阶段审计结果，去重合并排序输出。 (issue_a... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 74 | Stage 7 自愈闭环 — 修复->自测->回滚. (self_hea... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: skill_executor.py | → | writer.py | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — Skill Sandbox (skill... | → | bridge.py | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski... | → | writer.py | 导入依赖 / import_depends |
| 4 | D_FBL_VERIFICATION 反馈验证: Safety Gates L66-L67 — Financial Prudence + Fu... | → | bridge.py | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: ProjectionEngine — 事件折叠为当前状态（DW-0003... | → | EventStore — Event Sourcing 事件追加与回放（DW... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: DatabaseManager — 连接池 + 健康检查 + 自动备份... | → | audit_schema — 审计视图与查询入口（SH-DB-001 v... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (governance... | → | writer.py | 导入依赖 / import_depends |
| 8 | D_GOV_CODE_QUALITY 代码质量治理: reconciler_health_gate.py — reconciler 健康度.... | → | reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 9 | D_GOV_DOCS 架构文档治理: blueprint.md | → | blueprint.md | contract / contract |
| 10 | D_GOV_DOCS 架构文档治理: blueprint.md | → | blueprint.md | contract / contract |
| 11 | D_GOV_DOCS 架构文档治理: blueprint.md | → | blueprint.md | runtime / runtime |
| 12 | D_GOV_DOCS 架构文档治理: blueprint.md | → | blueprint.md | contract / contract |
| 13 | D_GOV_DOCS 架构文档治理: blueprint.md | → | blueprint.md | runtime / runtime |
| 14 | D_GOV_DRIFT 漂移检测: blueprint.md | → | blueprint.md | runtime / runtime |
| 15 | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | → | finding_ingest.py | 导入依赖 / import_depends |
| 16 | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | → | finding_model.py | 导入依赖 / import_depends |
| 17 | D_GOV_DRIFT 漂移检测: 真源优先级裁决器（Truth Source Validator） (tru... | → | bridge.py | 导入依赖 / import_depends |
| 18 | D_GOV_DRIFT 漂移检测: integrity.py | → | audit-trail.merkle_hourly — MOD-INF-020 · 每.... | 导入依赖 / import_depends |
| 19 | D_GOV_DRIFT 漂移检测: integrity.py | → | models.py | 导入依赖 / import_depends |
| 20 | D_GOV_DRIFT 漂移检测: integrity.py | → | trust_bridge.py | 导入依赖 / import_depends |
| 21 | D_GOV_ENFORCEMENT 规则执行: readme_version_sync_reconciler.py — README 版.... | → | reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 22 | D_GOV_ENFORCEMENT 规则执行: __init__.py | → | mcp_result_push.py | 导入依赖 / import_depends |
| 23 | D_GOV_ENFORCEMENT 规则执行: __init__.py | → | post_process.py —— AI 生成代码后处理管道（Pha... | 导入依赖 / import_depends |
| 24 | D_GOV_ENFORCEMENT 规则执行: __init__.py | → | vibe_coding_enforcer.py | 导入依赖 / import_depends |
| 25 | D_GOV_ENFORCEMENT 规则执行: GateEventAdapter — GateRepo 事件适配器（DW-000... | → | EventStore — Event Sourcing 事件追加与回放（DW... | 导入依赖 / import_depends |
| 26 | D_GOV_ENFORCEMENT 规则执行: verdict_engine.py | → | models.py | 导入依赖 / import_depends |
| 27 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit .... | → | reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 28 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit .... | → | remediation_progress_reconciler.py — 治本进度.... | 导入依赖 / import_depends |
| 29 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | → | reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 30 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | audit-trail.integrity — MOD-INF-020 · 密码学.... | 导入依赖 / import_depends |
| 31 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | query.py | 导入依赖 / import_depends |
| 32 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 .... | → | SYS-MASTER-001 Compliance Checker (sys_master_c... | 导入依赖 / import_depends |
| 33 | D_GOV_OPS_RESILIENCE 运维弹性治理: blast_radius — MOD-INF-028 §3.1 Stage 9 (blas... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 (mode... | 导入依赖 / import_depends |
| 34 | D_GOV_OPS_RESILIENCE 运维弹性治理: tamper_evident_log.py | → | writer.py | 导入依赖 / import_depends |
| 35 | D_GOV_RULE 规则治理: 能力检查器（Capability Checker） (capability_ch... | → | bridge.py | 导入依赖 / import_depends |
| 36 | D_GOV_RULE 规则治理: Owner 紧急旁路——时间限定的门禁临时绕过 + 审计... | → | bridge.py | 导入依赖 / import_depends |
| 37 | D_GOV_SCRIPTS 脚本治理: Red/Blue Team Adversarial Test v3: SYS-MASTER-0... | → | SYS-MASTER-001 Compliance Checker (sys_master_c... | 导入依赖 / import_depends |
| 38 | D_GOV_SCRIPTS 脚本治理: scripts/governance/rebuild_audit_index.py — 重... | → | indexer.py | 导入依赖 / import_depends |
| 39 | D_INFRASTRUCTURE 跨层契约基础设施: backup_reconciler.py — 灾备备份系统事件触发器.... | → | reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 40 | D_INFRA_RECOVERY 回滚恢复: G-CT-004 契约：Rollback -> Audit 记录回滚操作. ... | → | contracts.py | 导入依赖 / import_depends |
| 41 | D_INFRA_RECOVERY 回滚恢复: G-CT-002 Rollback 消费端 — on_audit_anomaly() ... | → | anomaly.py | 导入依赖 / import_depends |
| 42 | D_INFRA_RECOVERY 回滚恢复: RollbackAbuseDetector — 回滚滥用检测。 (rollba... | → | query.py | 导入依赖 / import_depends |
| 43 | D_INFRA_RECOVERY 回滚恢复: RollbackAuditNexus — 回滚审计记录聚合到 Nexus ... | → | writer.py | 导入依赖 / import_depends |
| 44 | D_INFRA_RECOVERY 回滚恢复: RollbackExecutor — 回滚执行器核心封装。 (rollb... | → | writer.py | 导入依赖 / import_depends |
| 45 | D_INFRA_RUNTIME 运行时集成: AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自... | → | writer.py | 导入依赖 / import_depends |
| 46 | D_INFRA_RUNTIME 运行时集成: engine.py | → | finding_model.py | 导入依赖 / import_depends |
| 47 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic res... | → | bridge.py | 导入依赖 / import_depends |
| 48 | D_INTEGRATION 管线路由: 接收 RED 问题,生成修复文本。LLM 只润色不做判断.... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 (mode... | 导入依赖 / import_depends |
| 49 | D_INTEGRATION 管线路由: MCP 全量工具调用审计日志（MOD-INF-013 §12 Step... | → | writer.py | 导入依赖 / import_depends |
| 50 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | writer.py | 导入依赖 / import_depends |
| 51 | D_SECURITY 对抗验证: G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge... | → | contracts.py | 导入依赖 / import_depends |
| 52 | D_SECURITY 对抗验证: judge.py | → | finding_model.py | 导入依赖 / import_depends |
| 53 | D_SECURITY 对抗验证: defense_runner.py | → | finding_model.py | 导入依赖 / import_depends |
| 54 | D_SECURITY 对抗验证: behavior_audit_logger.py | → | bridge.py | 导入依赖 / import_depends |
| 55 | D_SECURITY 对抗验证: isolation.py | → | bridge.py | 导入依赖 / import_depends |
| 56 | D_SHARED 共享服务: session_audit.py —— Session 审计轨迹（Phase 1... | → | writer.py | 导入依赖 / import_depends |
| 57 | D_TRADING 交易运营: verdict_engine.py | → | models.py | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 19 个外部域直接连接（出边 74 条 + 入边 57 条 = 131 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_DOCS["D_GOV_DOCS<br/>架构文档治理"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_FBL_VERIFICATION["D_FBL_VERIFICATION<br/>反馈验证"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOV_AUDIT -->|39条 导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT -->|11条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_AUDIT -->|8条 导入依赖 / import_depends, runtime / runtime| D_GOV_DRIFT
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends, runtime / runtime| D_GOV_CODE_QUALITY
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends| D_SECURITY
    D_GOV_AUDIT -->|3条 contract / contract, runtime / runtime| D_GOV_DOCS
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_REPORTING
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_GOV_RULE
    D_GOV_ENFORCEMENT -->|9条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_DRIFT -->|7条 导入依赖 / import_depends, runtime / runtime| D_GOV_AUDIT
    D_GOV_DOCS -->|5条 contract / contract, runtime / runtime| D_GOV_AUDIT
    D_SECURITY -->|5条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RECOVERY -->|5条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_OPS_RESILIENCE -->|5条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_AUTONOMY_CORE -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_RULE -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_SCRIPTS -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRASTRUCTURE -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_FBL_VERIFICATION -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_SHARED -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_TRADING -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
