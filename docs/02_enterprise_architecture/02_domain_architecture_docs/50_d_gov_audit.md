---
doc_type: architecture_view
title: D_GOV_AUDIT 审计追踪架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 50_d_gov_audit / 审计追踪域 / Audit Trail

> **功能简介 / Overview**: 审计追踪，负责变更审计追踪和操作日志管理

> **文档作用 / Purpose**: 展示 审计追踪（D_GOV_AUDIT）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/50_d_gov_audit.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 50 | Number | 50 |
| 域ID | D_GOV_AUDIT | Domain ID | D_GOV_AUDIT |
| 域名称 | 审计追踪 | Domain Name | Audit Trail |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 124 | Module Count | 124 |
| 域内依赖 | 104 | Internal Dependencies | 104 |
| 跨域入边 | 70 | Cross-domain Incoming | 70 |
| 跨域出边 | 108 | Cross-domain Outgoing | 108 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 122 | Production Modules | 122 |
| 容量 | 122/150 (正常) | Capacity | 122/150 (正常) |
| 描述 | 审计管线编排 | Description | 审计管线编排 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 124 个模块（生产态 122 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["audit_orchestrator/blueprint<br/>audit_orchestrator模块蓝图文档，描述该模块的设计<br/>意图和架构决策<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: audit_orchestrator/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md["audit_trail/blueprint<br/>audit_trail模块蓝图文档，描述该模块的设计意图和<br/>架构决策<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: audit_trail/blueprint.md<br/>(设计态 / design)"]
    scripts_governance_repair_audit_design_completeness_py["repair/audit_design_completeness<br/>(INVARIANTS) 按path精确匹配+按功能名模糊匹配;<br/>输出差距报告; 提取所有ID格式<br/>文件: repair/audit_design_completeness.py<br/>(生产态 / production)"]
    scripts_governance_repair_red_blue_test_py["repair/red_blue_test<br/>(INVARIANTS) 20项红蓝对抗测试<br/>文件: repair/red_blue_test.py<br/>(生产态 / production)"]
    scripts_governance_repair_rollback_depgraph_py["repair/rollback_depgraph<br/>(INVARIANTS) 仅接受depgraph.backup.*路径;<br/>回滚前自动备份当前depgraph<br/>文件: repair/rollback_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_test_remediation_progress_smoke_py["governance/test_remediation_progress_smoke<br/>test_remediation_progress_smoke.py — Phase 3.1<br/>治本进度 reconciler end-to-en...<br/>文件: governance<br/>/test_remediation_progress_smoke.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_orchestrator_compat_py["gov_audit/_orchestrator_compat<br/>audit-orchestrator 兼容重导出层（ARCH-042 阶段4<br/>修复双 MODULE，ARCH-043 Risk3...<br/>文件: gov_audit/_orchestrator_compat.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_action_history_py["gov_audit/action_history<br/>ActionHistory — 操作历史持久化审计 + 去重 +<br/>循环检测<br/>文件: gov_audit/action_history.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_api_lifecycle_py["gov_audit/api_lifecycle<br/>gov audit包的api_lifecycle模块<br/>文件: gov_audit/api_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_schema_py["gov_audit/audit_schema<br/>audit_schema — 审计视图与查询入口（SH-DB-001<br/>v2.0）<br/>文件: gov_audit/audit_schema.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_write_failure_protector_py["gov_audit/audit_write_failure_protector<br/>Audit Write Failure Protector — v0.13.0<br/>审计写入失败保护器。<br/>文件: gov_audit/audit_write_failure_protector.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_anomaly_py["bridges/audit_anomaly<br/>G-CT-002 Audit 异常检测器 — AnomalyEvent<br/>Pydantic V2 BaseModel.<br/>文件: bridges/audit_anomaly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_contracts_py["bridges/audit_contracts<br/>G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: bridges/audit_contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["bridges/audit_delegation_bridge<br/>Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: bridges/audit_delegation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py["bridges/audit_drift_bridge<br/>G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔<br/>MOD-INF-023<br/>文件: bridges/audit_drift_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["bridges/audit_feedback_bridge<br/>Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: bridges/audit_feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["bridges/audit_tiered_storage_bridge<br/>Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: bridges/audit_tiered_storage_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py["bridges/audit_trust_bridge<br/>Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: bridges/audit_trust_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_changelog_manager_py["gov_audit/changelog_manager<br/>gov audit包的changelog_manager模块<br/>文件: gov_audit/changelog_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_cli_py["gov_audit/cli<br/>gov audit包的cli模块<br/>文件: gov_audit/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_code_archaeology_py["gov_audit/code_archaeology<br/>gov audit包的code_archaeology模块<br/>文件: gov_audit/code_archaeology.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_cold_start_py["gov_audit/cold_start<br/>BootstrapCache — 审计冷启动共享单例缓存。<br/>文件: gov_audit/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_compliance_map_py["gov_audit/compliance_map<br/>audit-trail.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: gov_audit/compliance_map.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_corporate_actions_py["gov_audit/corporate_actions<br/>gov audit包的corporate_actions模块<br/>文件: gov_audit/corporate_actions.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_delegation_auditor_py["gov_audit/delegation_auditor<br/>gov audit包的delegation_auditor模块<br/>文件: gov_audit/delegation_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_dora_metrics_py["gov_audit/dora_metrics<br/>gov audit包的dora_metrics模块<br/>文件: gov_audit/dora_metrics.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_evidence_pack_py["gov_audit/evidence_pack<br/>audit-trail.evidence_pack — MOD-INF-020 ·<br/>证据包导出器<br/>文件: gov_audit/evidence_pack.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_external_tool_audit_py["gov_audit/external_tool_audit<br/>gov audit包的external_tool_audit模块<br/>文件: gov_audit/external_tool_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_policy_py["gov_audit/feedback_policy<br/>feedback_policy.py — Audit-findings → policy<br/>recommendation bridge.<br/>文件: gov_audit/feedback_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_self_audit_py["gov_audit/feedback_self_audit<br/>audit-trail.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: gov_audit/feedback_self_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_forensic_package_py["gov_audit/forensic_package<br/>Forensic Package — v0.8.0 取证就绪: escalation<br/>event bundle+hash chain+times...<br/>文件: gov_audit/forensic_package.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_genesis_py["gov_audit/genesis<br/>audit-trail.genesis — MOD-INF-020 · 创世块管理<br/>文件: gov_audit/genesis.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_glossary_matrix_py["gov_audit/glossary_matrix<br/>gov audit包的glossary_matrix模块<br/>文件: gov_audit/glossary_matrix.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_incremental_review_py["gov_audit/incremental_review<br/>gov audit包的incremental_review模块<br/>文件: gov_audit/incremental_review.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_integrity_verifier_py["gov_audit/integrity_verifier<br/>Integrity Verifier — v0.8.0 代码完整性验证器:<br/>hash校验+diff detection+rollback。<br/>文件: gov_audit/integrity_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_kb_gate_py["gov_audit/kb_gate<br/>audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: gov_audit/kb_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_log_rotation_py["gov_audit/log_rotation<br/>gov audit包的log_rotation模块<br/>文件: gov_audit/log_rotation.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_merkle_audit_py["gov_audit/merkle_audit<br/>Merkle Audit — 兼容别名，SSoT已迁移至<br/>zephyr.gov_audit (MOD-INF-020).<br/>文件: gov_audit/merkle_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_observability_dashboard_py["gov_audit/observability_dashboard<br/>gov audit包的observability_dashboard模块<br/>文件: gov_audit/observability_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_pipeline_runner_py["gov_audit/pipeline_runner<br/>gov audit包的pipeline_runner模块<br/>文件: gov_audit/pipeline_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_privacy_py["gov_audit/privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: gov_audit/privacy.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_provenance_tracker_py["gov_audit/provenance_tracker<br/>gov audit包的provenance_tracker模块<br/>文件: gov_audit/provenance_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_replay_engine_py["gov_audit/replay_engine<br/>gov audit包的replay_engine模块<br/>文件: gov_audit/replay_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_retention_py["gov_audit/retention<br/>gov audit包的retention模块<br/>文件: gov_audit/retention.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_sbom_generator_py["gov_audit/sbom_generator<br/>LicenseType 枚举——许可证类型定义（P3<br/>价值审判退役残留）。<br/>文件: gov_audit/sbom_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_spec_auditor_py["gov_audit/spec_auditor<br/>gov audit包的spec_auditor模块<br/>文件: gov_audit/spec_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_supply_chain_py["gov_audit/supply_chain<br/>audit-trail.supply_chain — MOD-INF-020 ·<br/>供应链审计<br/>文件: gov_audit/supply_chain.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_supply_chain_security_py["gov_audit/supply_chain_security<br/>gov audit包的supply_chain_security模块<br/>文件: gov_audit/supply_chain_security.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_ring_manager_py["gov_audit/trust_ring_manager<br/>gov audit包的trust_ring_manager模块<br/>文件: gov_audit/trust_ring_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_wqa_scorer_py["gov_audit/wqa_scorer<br/>gov audit包的wqa_scorer模块<br/>文件: gov_audit/wqa_scorer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["behavioral_admission/ai_code_standards<br/>behavioral admission包的ai_code_standards模块<br/>文件: behavioral_admission/ai_code_standards.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["behavioral_admission/mcp_result_push<br/>behavioral admission包的mcp_result_push模块<br/>文件: behavioral_admission/mcp_result_push.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py["behavioral_admission/post_process<br/>post_process.py —— AI 生成代码后处理管道（Phase<br/>13 / 盲点 B31）<br/>文件: behavioral_admission/post_process.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["behavioral_admission/vibe_coding_enforcer<br/>behavioral admission包的vibe_coding_enforcer模块<br/>文件: behavioral_admission<br/>/vibe_coding_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["rule_enforcement/audit_chain_verifier<br/>审计链验证工具——独立重放门禁判定+Hash链完整性校<br/>验（beta）<br/>文件: rule_enforcement/audit_chain_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["rule_enforcement/sys_master_compliance<br/>SYS-MASTER-001 Compliance Checker<br/>文件: rule_enforcement/sys_master_compliance.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_trail_contracts_py["audit-trail/contracts<br/>py — G-CT-002 Audit 契约（re-export）<br/>文件: audit-trail/contracts.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_ai_error_pattern_library_py["audit/ai_error_pattern_library<br/>ai_error_pattern_library.py — AI 错误模式库<br/>（只读查询接口）。<br/>文件: audit/ai_error_pattern_library.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py["audit/blueprint_status_transition_reconciler<br/>blueprint_status_transition_reconciler.py —<br/>蓝图状态单调推进 reconciler（P1-...<br/>文件: audit<br/>/blueprint_status_transition_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py["audit/cross_layer_contract_signature_reconciler<br/>cross_layer_contract_signature_reconciler.py —<br/>跨层契约签名漂移检测 reconcil...<br/>文件: audit<br/>/cross_layer_contract_signature_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py["audit/dead_public_wrapper_reconciler<br/>dead_public_wrapper_reconciler.py — 死公共<br/>wrapper 自动检测 reconciler.<br/>文件: audit/dead_public_wrapper_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_default_attribution_engine_py["audit/default_attribution_engine<br/>Re-export wrapper: default_attribution_engine<br/>canonical at zephyr.reporting.d...<br/>文件: audit/default_attribution_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_default_tca_engine_py["audit/default_tca_engine<br/>Re-export wrapper: default_tca_engine canonical<br/>at zephyr.reporting.default_t...<br/>文件: audit/default_tca_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py["audit/git_performance_monitor_reconciler<br/>git_performance_monitor_reconciler.py — git<br/>性能持续监控 + 早期预警（ARCH-GI...<br/>文件: audit<br/>/git_performance_monitor_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py["audit/runtime_violation_snapshot_reconciler<br/>runtime_violation_snapshot_reconciler.py —<br/>trae_060 §5 evidence 运行时快照 ...<br/>文件: audit<br/>/runtime_violation_snapshot_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_snapshot_manager_py["audit/snapshot_manager<br/>SnapshotManager — Event Sourcing 快照管理<br/>（DW-0005）<br/>文件: audit/snapshot_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py["audit/workspace_hygiene_reconciler<br/>workspace_hygiene_reconciler.py —<br/>工作区卫生自动清理 reconciler（DEBT-WORKSP...<br/>文件: audit/workspace_hygiene_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_financial_compliance_py["financial_governance/financial_compliance<br/>治理/financial<br/>governance包的financial_compliance模块<br/>文件: financial_governance<br/>/financial_compliance.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_compliance_map_py["semantic_audit/compliance_map<br/>audit-trail.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: semantic_audit/compliance_map.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_feedback_self_audit_py["semantic_audit/feedback_self_audit<br/>audit-trail.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: semantic_audit/feedback_self_audit.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["semantic_audit/fix_result_prioritizer<br/>fix_prioritizer — MOD-INF-028 §3.1 Stage 8<br/>文件: semantic_audit/fix_result_prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_orchestrator_py["semantic_audit/orchestrator<br/>SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: semantic_audit/orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_privacy_py["semantic_audit/privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: semantic_audit/privacy.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_semantic_cache_py["semantic_audit/semantic_cache<br/>治理/semantic audit包的semantic_cache模块<br/>文件: semantic_audit/semantic_cache.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_spec_auditor_py["semantic_audit/spec_auditor<br/>G-CT-007 — Audit.record_agent_spec() 记录 Agent<br/>Spec 注册与变更.<br/>文件: semantic_audit/spec_auditor.py<br/>(生产态 / production)"]
    tests_governance_audit_test_error_pattern_id_column_py["audit/test_error_pattern_id_column<br/>test_error_pattern_id_column.py —<br/>reconcile_execution_log.error_pattern_id ...<br/>文件: audit/test_error_pattern_id_column.py<br/>(生产态 / production)"]
    tests_governance_audit_test_p3_integration_smoke_py["audit/test_p3_integration_smoke<br/>test_p3_integration_smoke.py — Phase 3<br/>全链路集成 smoke test（P3-5）<br/>文件: audit/test_p3_integration_smoke.py<br/>(生产态 / production)"]
    tests_governance_audit_test_reconcile_async_py["audit/test_reconcile_async<br/>test_reconcile_async.py — P2-3 reconciler<br/>链路异步化测试<br/>文件: audit/test_reconcile_async.py<br/>(生产态 / production)"]
    tests_governance_audit_test_reconcile_worker_selfheal_py["audit/test_reconcile_worker_selfheal<br/>test_reconcile_worker_selfheal.py —<br/>#ARCH-RECONCILER-ALERT-SELFHEAL-001 Phas...<br/>文件: audit/test_reconcile_worker_selfheal.py<br/>(生产态 / production)"]
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py["audit/test_trae_069_threshold_sync_smoke<br/>test_trae_069_threshold_sync_smoke.py —<br/>trae_069 YAML 真源→代码常量同步 smo...<br/>文件: audit<br/>/test_trae_069_threshold_sync_smoke.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py["rule_bridge<br/>/test_session_worktree_async_reconcile<br/>test_session_worktree_async_reconcile.py —<br/>_run_reconcilers_after_merge 异步...<br/>文件: rule_bridge<br/>/test_session_worktree_async_reconcile.py<br/>(生产态 / production)"]
    tests_governance_test_workspace_telemetry_shared_py["governance/test_workspace_telemetry_shared<br/>test_workspace_telemetry_shared.py — shared<br/>workspace_telemetry 公共 API 单测<br/>文件: governance<br/>/test_workspace_telemetry_shared.py<br/>(生产态 / production)"]
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md ~~~ docs_03_modules_domain_governance_audit_trail_blueprint_md
    docs_03_modules_domain_governance_audit_trail_blueprint_md ~~~ scripts_governance_repair_audit_design_completeness_py
    scripts_governance_repair_audit_design_completeness_py ~~~ scripts_governance_repair_red_blue_test_py
    scripts_governance_repair_red_blue_test_py ~~~ scripts_governance_repair_rollback_depgraph_py
    scripts_governance_repair_rollback_depgraph_py ~~~ scripts_governance_test_remediation_progress_smoke_py
    scripts_governance_test_remediation_progress_smoke_py ~~~ src_zephyr_gov_audit_orchestrator_compat_py
    src_zephyr_gov_audit_orchestrator_compat_py ~~~ src_zephyr_gov_audit_action_history_py
    src_zephyr_gov_audit_action_history_py ~~~ src_zephyr_gov_audit_api_lifecycle_py
    src_zephyr_gov_audit_api_lifecycle_py ~~~ src_zephyr_gov_audit_audit_schema_py
    src_zephyr_gov_audit_audit_schema_py ~~~ src_zephyr_gov_audit_audit_write_failure_protector_py
    src_zephyr_gov_audit_audit_write_failure_protector_py ~~~ src_zephyr_gov_audit_bridges_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_anomaly_py ~~~ src_zephyr_gov_audit_bridges_audit_contracts_py
    src_zephyr_gov_audit_bridges_audit_contracts_py ~~~ src_zephyr_gov_audit_bridges_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_drift_bridge_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_trust_bridge_py
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py ~~~ src_zephyr_gov_audit_changelog_manager_py
    src_zephyr_gov_audit_changelog_manager_py ~~~ src_zephyr_gov_audit_cli_py
    src_zephyr_gov_audit_cli_py ~~~ src_zephyr_gov_audit_code_archaeology_py
    src_zephyr_gov_audit_code_archaeology_py ~~~ src_zephyr_gov_audit_cold_start_py
    src_zephyr_gov_audit_cold_start_py ~~~ src_zephyr_gov_audit_compliance_map_py
    src_zephyr_gov_audit_compliance_map_py ~~~ src_zephyr_gov_audit_corporate_actions_py
    src_zephyr_gov_audit_corporate_actions_py ~~~ src_zephyr_gov_audit_delegation_auditor_py
    src_zephyr_gov_audit_delegation_auditor_py ~~~ src_zephyr_gov_audit_dora_metrics_py
    src_zephyr_gov_audit_dora_metrics_py ~~~ src_zephyr_gov_audit_evidence_pack_py
    src_zephyr_gov_audit_evidence_pack_py ~~~ src_zephyr_gov_audit_external_tool_audit_py
    src_zephyr_gov_audit_external_tool_audit_py ~~~ src_zephyr_gov_audit_feedback_policy_py
    src_zephyr_gov_audit_feedback_policy_py ~~~ src_zephyr_gov_audit_feedback_self_audit_py
    src_zephyr_gov_audit_feedback_self_audit_py ~~~ src_zephyr_gov_audit_forensic_package_py
    src_zephyr_gov_audit_forensic_package_py ~~~ src_zephyr_gov_audit_genesis_py
    src_zephyr_gov_audit_genesis_py ~~~ src_zephyr_gov_audit_glossary_matrix_py
    src_zephyr_gov_audit_glossary_matrix_py ~~~ src_zephyr_gov_audit_incremental_review_py
    src_zephyr_gov_audit_incremental_review_py ~~~ src_zephyr_gov_audit_integrity_verifier_py
    src_zephyr_gov_audit_integrity_verifier_py ~~~ src_zephyr_gov_audit_kb_gate_py
    src_zephyr_gov_audit_kb_gate_py ~~~ src_zephyr_gov_audit_log_rotation_py
    src_zephyr_gov_audit_log_rotation_py ~~~ src_zephyr_gov_audit_merkle_audit_py
    src_zephyr_gov_audit_merkle_audit_py ~~~ src_zephyr_gov_audit_observability_dashboard_py
    src_zephyr_gov_audit_observability_dashboard_py ~~~ src_zephyr_gov_audit_pipeline_runner_py
    src_zephyr_gov_audit_pipeline_runner_py ~~~ src_zephyr_gov_audit_privacy_py
    src_zephyr_gov_audit_privacy_py ~~~ src_zephyr_gov_audit_provenance_tracker_py
    src_zephyr_gov_audit_provenance_tracker_py ~~~ src_zephyr_gov_audit_replay_engine_py
    src_zephyr_gov_audit_replay_engine_py ~~~ src_zephyr_gov_audit_retention_py
    src_zephyr_gov_audit_retention_py ~~~ src_zephyr_gov_audit_sbom_generator_py
    src_zephyr_gov_audit_sbom_generator_py ~~~ src_zephyr_gov_audit_spec_auditor_py
    src_zephyr_gov_audit_spec_auditor_py ~~~ src_zephyr_gov_audit_supply_chain_py
    src_zephyr_gov_audit_supply_chain_py ~~~ src_zephyr_gov_audit_supply_chain_security_py
    src_zephyr_gov_audit_supply_chain_security_py ~~~ src_zephyr_gov_audit_trust_ring_manager_py
    src_zephyr_gov_audit_trust_ring_manager_py ~~~ src_zephyr_gov_audit_wqa_scorer_py
    src_zephyr_gov_audit_wqa_scorer_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_post_process_py
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py ~~~ src_zephyr_governance_audit_trail_contracts_py
    src_zephyr_governance_audit_trail_contracts_py ~~~ src_zephyr_governance_audit_ai_error_pattern_library_py
    src_zephyr_governance_audit_ai_error_pattern_library_py ~~~ src_zephyr_governance_audit_blueprint_status_transition_reconciler_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py ~~~ src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py ~~~ src_zephyr_governance_audit_dead_public_wrapper_reconciler_py
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py ~~~ src_zephyr_governance_audit_default_attribution_engine_py
    src_zephyr_governance_audit_default_attribution_engine_py ~~~ src_zephyr_governance_audit_default_tca_engine_py
    src_zephyr_governance_audit_default_tca_engine_py ~~~ src_zephyr_governance_audit_git_performance_monitor_reconciler_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py ~~~ src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py ~~~ src_zephyr_governance_audit_snapshot_manager_py
    src_zephyr_governance_audit_snapshot_manager_py ~~~ src_zephyr_governance_audit_workspace_hygiene_reconciler_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py ~~~ src_zephyr_governance_financial_governance_financial_compliance_py
    src_zephyr_governance_financial_governance_financial_compliance_py ~~~ src_zephyr_governance_semantic_audit_compliance_map_py
    src_zephyr_governance_semantic_audit_compliance_map_py ~~~ src_zephyr_governance_semantic_audit_feedback_self_audit_py
    src_zephyr_governance_semantic_audit_feedback_self_audit_py ~~~ src_zephyr_governance_semantic_audit_fix_result_prioritizer_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py ~~~ src_zephyr_governance_semantic_audit_orchestrator_py
    src_zephyr_governance_semantic_audit_orchestrator_py ~~~ src_zephyr_governance_semantic_audit_privacy_py
    src_zephyr_governance_semantic_audit_privacy_py ~~~ src_zephyr_governance_semantic_audit_semantic_cache_py
    src_zephyr_governance_semantic_audit_semantic_cache_py ~~~ src_zephyr_governance_semantic_audit_spec_auditor_py
    src_zephyr_governance_semantic_audit_spec_auditor_py ~~~ tests_governance_audit_test_error_pattern_id_column_py
    tests_governance_audit_test_error_pattern_id_column_py ~~~ tests_governance_audit_test_p3_integration_smoke_py
    tests_governance_audit_test_p3_integration_smoke_py ~~~ tests_governance_audit_test_reconcile_async_py
    tests_governance_audit_test_reconcile_async_py ~~~ tests_governance_audit_test_reconcile_worker_selfheal_py
    tests_governance_audit_test_reconcile_worker_selfheal_py ~~~ tests_governance_audit_test_trae_069_threshold_sync_smoke_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py ~~~ tests_governance_rule_bridge_test_session_worktree_async_reconcile_py
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py ~~~ tests_governance_test_workspace_telemetry_shared_py
    src_zephyr_gov_audit_anomaly_py["gov_audit/anomaly<br/>gov audit包的anomaly模块<br/>文件: gov_audit/anomaly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_admission_controller_py["gov_audit/audit_admission_controller<br/>gov audit包的audit_admission_controller模块<br/>文件: gov_audit/audit_admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridge_py["gov_audit/bridge<br/>gov audit包的bridge模块<br/>文件: gov_audit/bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_event_store_py["gov_audit/event_store<br/>EventStore — Event Sourcing 事件追加与回放<br/>（DW-0002）<br/>文件: gov_audit/event_store.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_query_py["gov_audit/query<br/>gov audit包的query模块<br/>文件: gov_audit/query.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_resource_aware_pool_py["gov_audit/resource_aware_pool<br/>gov audit包的resource_aware_pool模块<br/>文件: gov_audit/resource_aware_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_text_to_finding_adapter_py["gov_audit/text_to_finding_adapter<br/>gov audit包的text_to_finding_adapter模块<br/>文件: gov_audit/text_to_finding_adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_git_helpers_py["audit/_git_helpers<br/>_git_helpers.py — audit reconciler 共享 git<br/>工具模块<br/>文件: audit/_git_helpers.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py["audit/commit_gateway_abuse_monitor_reconciler<br/>commit_gateway_abuse_monitor_reconciler.py —<br/>commit gateway 持续滥用监控（AR...<br/>文件: audit<br/>/commit_gateway_abuse_monitor_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py["audit/error_pattern_consumer_reconciler<br/>error_pattern_consumer_reconciler.py — AI<br/>行为遥测 JSONL 错误事件聚合 consumer。<br/>文件: audit/error_pattern_consumer_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconcile_worker_py["audit/reconcile_worker<br/>reconcile_worker.py — 异步 reconciler worker<br/>（Ruling:100PCT-AI-GOVERNANCE P2...<br/>文件: audit/reconcile_worker.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_remediation_progress_reconciler_py["audit/remediation_progress_reconciler<br/>remediation_progress_reconciler.py —<br/>治本进度持久化 + 新鲜度对账（...<br/>文件: audit/remediation_progress_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_runtime_violation_snapshot_py["audit/runtime_violation_snapshot<br/>runtime_violation_snapshot.py — trae_060 §5<br/>evidence 运行时快照（...<br/>文件: audit/runtime_violation_snapshot.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_alignment_engine_py["semantic_audit/alignment_engine<br/>三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs<br/>import 引用链。<br/>文件: semantic_audit/alignment_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_fix_prioritizer_py["semantic_audit/fix_prioritizer<br/>按 severity -> certainty -> blast_radius<br/>三级排序,分组输出批次。<br/>文件: semantic_audit/fix_prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_issue_aggregator_py["semantic_audit/issue_aggregator<br/>收集各阶段审计结果，去重合并排序输出。<br/>文件: semantic_audit/issue_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_kb_gate_py["semantic_audit/kb_gate<br/>audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: semantic_audit/kb_gate.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_llm_bridge_py["semantic_audit/llm_bridge<br/>接收 RED 问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成。<br/>文件: semantic_audit/llm_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_safety_boundary_py["semantic_audit/safety_boundary<br/>禁碰规则过滤 + 置信度阈值。输入 TriggerResult<br/>列表,输出 SafetyDecision 分类。<br/>文件: semantic_audit/safety_boundary.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_self_healer_py["semantic_audit/self_healer<br/>Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: semantic_audit/self_healer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_self_health_py["semantic_audit/self_health<br/>7 SLI + 5 容量 SLI + 退化检测。定时自检,输出<br/>HEALTHY/DEGRADED/CRITICAL。<br/>文件: semantic_audit/self_health.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_trigger_engine_py["semantic_audit/trigger_engine<br/>监听文件变更，判定是否触发语义审计。<br/>文件: semantic_audit/trigger_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_anomaly_py ~~~ src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_audit_admission_controller_py ~~~ src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_bridge_py ~~~ src_zephyr_gov_audit_event_store_py
    src_zephyr_gov_audit_event_store_py ~~~ src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_query_py ~~~ src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_resource_aware_pool_py ~~~ src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_text_to_finding_adapter_py ~~~ src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_git_helpers_py ~~~ src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py ~~~ src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py ~~~ src_zephyr_governance_audit_reconcile_worker_py
    src_zephyr_governance_audit_reconcile_worker_py ~~~ src_zephyr_governance_audit_remediation_progress_reconciler_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py ~~~ src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_runtime_violation_snapshot_py ~~~ src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_alignment_engine_py ~~~ src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py ~~~ src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py ~~~ src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_governance_semantic_audit_kb_gate_py ~~~ src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_llm_bridge_py ~~~ src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_safety_boundary_py ~~~ src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_self_healer_py ~~~ src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_self_health_py ~~~ src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_gov_audit_delegation_bridge_py["gov_audit/delegation_bridge<br/>gov audit包的delegation_bridge模块<br/>文件: gov_audit/delegation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_bridge_py["gov_audit/feedback_bridge<br/>gov audit包的feedback_bridge模块<br/>文件: gov_audit/feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_finding_ingest_py["gov_audit/finding_ingest<br/>gov audit包的finding_ingest模块<br/>文件: gov_audit/finding_ingest.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_indexer_py["gov_audit/indexer<br/>gov audit包的indexer模块<br/>文件: gov_audit/indexer.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_merkle_hourly_py["gov_audit/merkle_hourly<br/>audit-trail.merkle_hourly — MOD-INF-020 ·<br/>每小时 Merkle 聚合<br/>文件: gov_audit/merkle_hourly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_models_py["gov_audit/models<br/>gov audit包的models模块<br/>文件: gov_audit/models.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_tiered_storage_bridge_py["gov_audit/tiered_storage_bridge<br/>gov audit包的tiered_storage_bridge模块<br/>文件: gov_audit/tiered_storage_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_bridge_py["gov_audit/trust_bridge<br/>gov audit包的trust_bridge模块<br/>文件: gov_audit/trust_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_health_score_calculator_py["audit/health_score_calculator<br/>health_score_calculator.py — commit gateway<br/>滥用 6 维加权健康度评分（P3-2，#...<br/>文件: audit/health_score_calculator.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconcile_runner_py["audit/reconcile_runner<br/>reconcile_runner.py — Reconciler 链路异步化<br/>（Ruling:100PCT-AI-GOVERNANCE P2-...<br/>文件: audit/reconcile_runner.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_reference_extractor_py["semantic_audit/reference_extractor<br/>AST 解析文件，提取 9 个维度的引用信息。<br/>文件: semantic_audit/reference_extractor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_delegation_bridge_py ~~~ src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_feedback_bridge_py ~~~ src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_finding_ingest_py ~~~ src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_indexer_py ~~~ src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_merkle_hourly_py ~~~ src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_models_py ~~~ src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_tiered_storage_bridge_py ~~~ src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_trust_bridge_py ~~~ src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_health_score_calculator_py ~~~ src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_runner_py ~~~ src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_contracts_py["gov_audit/contracts<br/>gov audit包的contracts模块<br/>文件: gov_audit/contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_finding_model_py["gov_audit/finding_model<br/>gov audit包的finding_model模块<br/>文件: gov_audit/finding_model.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_integrity_py["gov_audit/integrity<br/>audit-trail.integrity — MOD-INF-020 ·<br/>密码学完整性验证器<br/>文件: gov_audit/integrity.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_tiered_storage_py["gov_audit/tiered_storage<br/>gov audit包的tiered_storage模块<br/>文件: gov_audit/tiered_storage.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_engine_py["gov_audit/trust_engine<br/>gov audit包的trust_engine模块<br/>文件: gov_audit/trust_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_writer_py["gov_audit/writer<br/>gov audit包的writer模块<br/>文件: gov_audit/writer.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconciliation_registry_py["audit/reconciliation_registry<br/>reconciliation_registry.py — GitCommitGateway<br/>post-commit 漂移对账注册表（P2...<br/>文件: audit/reconciliation_registry.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_models_py["semantic_audit/models<br/>语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: semantic_audit/models.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_contracts_py ~~~ src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_model_py ~~~ src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_integrity_py ~~~ src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_tiered_storage_py ~~~ src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_trust_engine_py ~~~ src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_writer_py ~~~ src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconciliation_registry_py ~~~ src_zephyr_governance_semantic_audit_models_py
    src_zephyr_gov_audit_agent_signer_py["gov_audit/agent_signer<br/>audit-trail.agent_signer — MOD-INF-020 · Agent<br/>Ed25519 签名器<br/>文件: gov_audit/agent_signer.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_ai_error_pattern_library_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_runner_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_trail_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_governance_semantic_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_llm_bridge_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_reference_extractor_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_safety_boundary_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_write_failure_protector_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_delegation_auditor_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_agent_signer_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_merkle_audit_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_text_to_finding_adapter_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_trust_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_tiered_storage_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_bridges_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_error_pattern_id_column_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    D_GOV_CODE_QUALITY["代码质量治理<br/>代码质量治理，负责代码去重引擎、函数重复检测、AS<br/>T语义分析和提交门禁引擎<br/>Code Quality Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_audit_runtime_violation_snapshot_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_repair_rollback_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_repair_red_blue_test_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_spec_auditor_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| D_SECURITY
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    scripts_governance_repair_rollback_depgraph_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_dead_public_wrapper_reconciler_py
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_ai_error_pattern_library_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py,src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_resource_aware_pool_py,src_zephyr_gov_audit_retention_py,src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_trail_contracts_py,src_zephyr_governance_audit_git_helpers_py,src_zephyr_governance_audit_ai_error_pattern_library_py,src_zephyr_governance_audit_blueprint_status_transition_reconciler_py,src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py,src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py,src_zephyr_governance_audit_dead_public_wrapper_reconciler_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_error_pattern_consumer_reconciler_py,src_zephyr_governance_audit_git_performance_monitor_reconciler_py,src_zephyr_governance_audit_health_score_calculator_py,src_zephyr_governance_audit_reconcile_runner_py,src_zephyr_governance_audit_reconcile_worker_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_audit_runtime_violation_snapshot_py,src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_audit_workspace_hygiene_reconciler_py,src_zephyr_governance_financial_governance_financial_compliance_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py,src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_semantic_cache_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py,tests_governance_audit_test_error_pattern_id_column_py,tests_governance_audit_test_p3_integration_smoke_py,tests_governance_audit_test_reconcile_async_py,tests_governance_audit_test_reconcile_worker_selfheal_py,tests_governance_audit_test_trae_069_threshold_sync_smoke_py,tests_governance_rule_bridge_test_session_worktree_async_reconcile_py,tests_governance_test_workspace_telemetry_shared_py production
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
    class D_GOV_CODE_QUALITY,D_GOV_SCRIPTS,D_GOVERNANCE,D_SHARED,D_SECURITY,D_GOV_DRIFT,D_GOV_ENFORCEMENT,D_GOV_OPS_RESILIENCE,D_TRADING,D_AUTONOMY_CORE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 122 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_repair_audit_design_completeness_py["repair/audit_design_completeness<br/>(INVARIANTS) 按path精确匹配+按功能名模糊匹配;<br/>输出差距报告; 提取所有ID格式<br/>文件: repair/audit_design_completeness.py<br/>(生产态 / production)"]
    scripts_governance_repair_red_blue_test_py["repair/red_blue_test<br/>(INVARIANTS) 20项红蓝对抗测试<br/>文件: repair/red_blue_test.py<br/>(生产态 / production)"]
    scripts_governance_repair_rollback_depgraph_py["repair/rollback_depgraph<br/>(INVARIANTS) 仅接受depgraph.backup.*路径;<br/>回滚前自动备份当前depgraph<br/>文件: repair/rollback_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_test_remediation_progress_smoke_py["governance/test_remediation_progress_smoke<br/>test_remediation_progress_smoke.py — Phase 3.1<br/>治本进度 reconciler end-to-en...<br/>文件: governance<br/>/test_remediation_progress_smoke.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_orchestrator_compat_py["gov_audit/_orchestrator_compat<br/>audit-orchestrator 兼容重导出层（ARCH-042 阶段4<br/>修复双 MODULE，ARCH-043 Risk3...<br/>文件: gov_audit/_orchestrator_compat.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_action_history_py["gov_audit/action_history<br/>ActionHistory — 操作历史持久化审计 + 去重 +<br/>循环检测<br/>文件: gov_audit/action_history.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_api_lifecycle_py["gov_audit/api_lifecycle<br/>gov audit包的api_lifecycle模块<br/>文件: gov_audit/api_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_schema_py["gov_audit/audit_schema<br/>audit_schema — 审计视图与查询入口（SH-DB-001<br/>v2.0）<br/>文件: gov_audit/audit_schema.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_write_failure_protector_py["gov_audit/audit_write_failure_protector<br/>Audit Write Failure Protector — v0.13.0<br/>审计写入失败保护器。<br/>文件: gov_audit/audit_write_failure_protector.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_anomaly_py["bridges/audit_anomaly<br/>G-CT-002 Audit 异常检测器 — AnomalyEvent<br/>Pydantic V2 BaseModel.<br/>文件: bridges/audit_anomaly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_contracts_py["bridges/audit_contracts<br/>G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: bridges/audit_contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["bridges/audit_delegation_bridge<br/>Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: bridges/audit_delegation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py["bridges/audit_drift_bridge<br/>G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔<br/>MOD-INF-023<br/>文件: bridges/audit_drift_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["bridges/audit_feedback_bridge<br/>Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: bridges/audit_feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["bridges/audit_tiered_storage_bridge<br/>Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: bridges/audit_tiered_storage_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py["bridges/audit_trust_bridge<br/>Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: bridges/audit_trust_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_changelog_manager_py["gov_audit/changelog_manager<br/>gov audit包的changelog_manager模块<br/>文件: gov_audit/changelog_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_cli_py["gov_audit/cli<br/>gov audit包的cli模块<br/>文件: gov_audit/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_code_archaeology_py["gov_audit/code_archaeology<br/>gov audit包的code_archaeology模块<br/>文件: gov_audit/code_archaeology.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_cold_start_py["gov_audit/cold_start<br/>BootstrapCache — 审计冷启动共享单例缓存。<br/>文件: gov_audit/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_compliance_map_py["gov_audit/compliance_map<br/>audit-trail.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: gov_audit/compliance_map.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_corporate_actions_py["gov_audit/corporate_actions<br/>gov audit包的corporate_actions模块<br/>文件: gov_audit/corporate_actions.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_delegation_auditor_py["gov_audit/delegation_auditor<br/>gov audit包的delegation_auditor模块<br/>文件: gov_audit/delegation_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_dora_metrics_py["gov_audit/dora_metrics<br/>gov audit包的dora_metrics模块<br/>文件: gov_audit/dora_metrics.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_evidence_pack_py["gov_audit/evidence_pack<br/>audit-trail.evidence_pack — MOD-INF-020 ·<br/>证据包导出器<br/>文件: gov_audit/evidence_pack.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_external_tool_audit_py["gov_audit/external_tool_audit<br/>gov audit包的external_tool_audit模块<br/>文件: gov_audit/external_tool_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_policy_py["gov_audit/feedback_policy<br/>feedback_policy.py — Audit-findings → policy<br/>recommendation bridge.<br/>文件: gov_audit/feedback_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_self_audit_py["gov_audit/feedback_self_audit<br/>audit-trail.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: gov_audit/feedback_self_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_forensic_package_py["gov_audit/forensic_package<br/>Forensic Package — v0.8.0 取证就绪: escalation<br/>event bundle+hash chain+times...<br/>文件: gov_audit/forensic_package.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_genesis_py["gov_audit/genesis<br/>audit-trail.genesis — MOD-INF-020 · 创世块管理<br/>文件: gov_audit/genesis.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_glossary_matrix_py["gov_audit/glossary_matrix<br/>gov audit包的glossary_matrix模块<br/>文件: gov_audit/glossary_matrix.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_incremental_review_py["gov_audit/incremental_review<br/>gov audit包的incremental_review模块<br/>文件: gov_audit/incremental_review.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_integrity_verifier_py["gov_audit/integrity_verifier<br/>Integrity Verifier — v0.8.0 代码完整性验证器:<br/>hash校验+diff detection+rollback。<br/>文件: gov_audit/integrity_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_kb_gate_py["gov_audit/kb_gate<br/>audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: gov_audit/kb_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_log_rotation_py["gov_audit/log_rotation<br/>gov audit包的log_rotation模块<br/>文件: gov_audit/log_rotation.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_merkle_audit_py["gov_audit/merkle_audit<br/>Merkle Audit — 兼容别名，SSoT已迁移至<br/>zephyr.gov_audit (MOD-INF-020).<br/>文件: gov_audit/merkle_audit.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_observability_dashboard_py["gov_audit/observability_dashboard<br/>gov audit包的observability_dashboard模块<br/>文件: gov_audit/observability_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_pipeline_runner_py["gov_audit/pipeline_runner<br/>gov audit包的pipeline_runner模块<br/>文件: gov_audit/pipeline_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_privacy_py["gov_audit/privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: gov_audit/privacy.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_provenance_tracker_py["gov_audit/provenance_tracker<br/>gov audit包的provenance_tracker模块<br/>文件: gov_audit/provenance_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_replay_engine_py["gov_audit/replay_engine<br/>gov audit包的replay_engine模块<br/>文件: gov_audit/replay_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_retention_py["gov_audit/retention<br/>gov audit包的retention模块<br/>文件: gov_audit/retention.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_sbom_generator_py["gov_audit/sbom_generator<br/>LicenseType 枚举——许可证类型定义（P3<br/>价值审判退役残留）。<br/>文件: gov_audit/sbom_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_spec_auditor_py["gov_audit/spec_auditor<br/>gov audit包的spec_auditor模块<br/>文件: gov_audit/spec_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_supply_chain_py["gov_audit/supply_chain<br/>audit-trail.supply_chain — MOD-INF-020 ·<br/>供应链审计<br/>文件: gov_audit/supply_chain.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_supply_chain_security_py["gov_audit/supply_chain_security<br/>gov audit包的supply_chain_security模块<br/>文件: gov_audit/supply_chain_security.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_ring_manager_py["gov_audit/trust_ring_manager<br/>gov audit包的trust_ring_manager模块<br/>文件: gov_audit/trust_ring_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_wqa_scorer_py["gov_audit/wqa_scorer<br/>gov audit包的wqa_scorer模块<br/>文件: gov_audit/wqa_scorer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["behavioral_admission/ai_code_standards<br/>behavioral admission包的ai_code_standards模块<br/>文件: behavioral_admission/ai_code_standards.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["behavioral_admission/mcp_result_push<br/>behavioral admission包的mcp_result_push模块<br/>文件: behavioral_admission/mcp_result_push.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py["behavioral_admission/post_process<br/>post_process.py —— AI 生成代码后处理管道（Phase<br/>13 / 盲点 B31）<br/>文件: behavioral_admission/post_process.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["behavioral_admission/vibe_coding_enforcer<br/>behavioral admission包的vibe_coding_enforcer模块<br/>文件: behavioral_admission<br/>/vibe_coding_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["rule_enforcement/audit_chain_verifier<br/>审计链验证工具——独立重放门禁判定+Hash链完整性校<br/>验（beta）<br/>文件: rule_enforcement/audit_chain_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["rule_enforcement/sys_master_compliance<br/>SYS-MASTER-001 Compliance Checker<br/>文件: rule_enforcement/sys_master_compliance.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_trail_contracts_py["audit-trail/contracts<br/>py — G-CT-002 Audit 契约（re-export）<br/>文件: audit-trail/contracts.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_ai_error_pattern_library_py["audit/ai_error_pattern_library<br/>ai_error_pattern_library.py — AI 错误模式库<br/>（只读查询接口）。<br/>文件: audit/ai_error_pattern_library.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py["audit/blueprint_status_transition_reconciler<br/>blueprint_status_transition_reconciler.py —<br/>蓝图状态单调推进 reconciler（P1-...<br/>文件: audit<br/>/blueprint_status_transition_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py["audit/cross_layer_contract_signature_reconciler<br/>cross_layer_contract_signature_reconciler.py —<br/>跨层契约签名漂移检测 reconcil...<br/>文件: audit<br/>/cross_layer_contract_signature_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py["audit/dead_public_wrapper_reconciler<br/>dead_public_wrapper_reconciler.py — 死公共<br/>wrapper 自动检测 reconciler.<br/>文件: audit/dead_public_wrapper_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_default_attribution_engine_py["audit/default_attribution_engine<br/>Re-export wrapper: default_attribution_engine<br/>canonical at zephyr.reporting.d...<br/>文件: audit/default_attribution_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_default_tca_engine_py["audit/default_tca_engine<br/>Re-export wrapper: default_tca_engine canonical<br/>at zephyr.reporting.default_t...<br/>文件: audit/default_tca_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py["audit/git_performance_monitor_reconciler<br/>git_performance_monitor_reconciler.py — git<br/>性能持续监控 + 早期预警（ARCH-GI...<br/>文件: audit<br/>/git_performance_monitor_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py["audit/runtime_violation_snapshot_reconciler<br/>runtime_violation_snapshot_reconciler.py —<br/>trae_060 §5 evidence 运行时快照 ...<br/>文件: audit<br/>/runtime_violation_snapshot_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_snapshot_manager_py["audit/snapshot_manager<br/>SnapshotManager — Event Sourcing 快照管理<br/>（DW-0005）<br/>文件: audit/snapshot_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py["audit/workspace_hygiene_reconciler<br/>workspace_hygiene_reconciler.py —<br/>工作区卫生自动清理 reconciler（DEBT-WORKSP...<br/>文件: audit/workspace_hygiene_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_financial_compliance_py["financial_governance/financial_compliance<br/>治理/financial<br/>governance包的financial_compliance模块<br/>文件: financial_governance<br/>/financial_compliance.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_compliance_map_py["semantic_audit/compliance_map<br/>audit-trail.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: semantic_audit/compliance_map.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_feedback_self_audit_py["semantic_audit/feedback_self_audit<br/>audit-trail.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: semantic_audit/feedback_self_audit.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["semantic_audit/fix_result_prioritizer<br/>fix_prioritizer — MOD-INF-028 §3.1 Stage 8<br/>文件: semantic_audit/fix_result_prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_orchestrator_py["semantic_audit/orchestrator<br/>SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: semantic_audit/orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_privacy_py["semantic_audit/privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: semantic_audit/privacy.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_semantic_cache_py["semantic_audit/semantic_cache<br/>治理/semantic audit包的semantic_cache模块<br/>文件: semantic_audit/semantic_cache.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_spec_auditor_py["semantic_audit/spec_auditor<br/>G-CT-007 — Audit.record_agent_spec() 记录 Agent<br/>Spec 注册与变更.<br/>文件: semantic_audit/spec_auditor.py<br/>(生产态 / production)"]
    tests_governance_audit_test_error_pattern_id_column_py["audit/test_error_pattern_id_column<br/>test_error_pattern_id_column.py —<br/>reconcile_execution_log.error_pattern_id ...<br/>文件: audit/test_error_pattern_id_column.py<br/>(生产态 / production)"]
    tests_governance_audit_test_p3_integration_smoke_py["audit/test_p3_integration_smoke<br/>test_p3_integration_smoke.py — Phase 3<br/>全链路集成 smoke test（P3-5）<br/>文件: audit/test_p3_integration_smoke.py<br/>(生产态 / production)"]
    tests_governance_audit_test_reconcile_async_py["audit/test_reconcile_async<br/>test_reconcile_async.py — P2-3 reconciler<br/>链路异步化测试<br/>文件: audit/test_reconcile_async.py<br/>(生产态 / production)"]
    tests_governance_audit_test_reconcile_worker_selfheal_py["audit/test_reconcile_worker_selfheal<br/>test_reconcile_worker_selfheal.py —<br/>#ARCH-RECONCILER-ALERT-SELFHEAL-001 Phas...<br/>文件: audit/test_reconcile_worker_selfheal.py<br/>(生产态 / production)"]
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py["audit/test_trae_069_threshold_sync_smoke<br/>test_trae_069_threshold_sync_smoke.py —<br/>trae_069 YAML 真源→代码常量同步 smo...<br/>文件: audit<br/>/test_trae_069_threshold_sync_smoke.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py["rule_bridge<br/>/test_session_worktree_async_reconcile<br/>test_session_worktree_async_reconcile.py —<br/>_run_reconcilers_after_merge 异步...<br/>文件: rule_bridge<br/>/test_session_worktree_async_reconcile.py<br/>(生产态 / production)"]
    tests_governance_test_workspace_telemetry_shared_py["governance/test_workspace_telemetry_shared<br/>test_workspace_telemetry_shared.py — shared<br/>workspace_telemetry 公共 API 单测<br/>文件: governance<br/>/test_workspace_telemetry_shared.py<br/>(生产态 / production)"]
    scripts_governance_repair_audit_design_completeness_py ~~~ scripts_governance_repair_red_blue_test_py
    scripts_governance_repair_red_blue_test_py ~~~ scripts_governance_repair_rollback_depgraph_py
    scripts_governance_repair_rollback_depgraph_py ~~~ scripts_governance_test_remediation_progress_smoke_py
    scripts_governance_test_remediation_progress_smoke_py ~~~ src_zephyr_gov_audit_orchestrator_compat_py
    src_zephyr_gov_audit_orchestrator_compat_py ~~~ src_zephyr_gov_audit_action_history_py
    src_zephyr_gov_audit_action_history_py ~~~ src_zephyr_gov_audit_api_lifecycle_py
    src_zephyr_gov_audit_api_lifecycle_py ~~~ src_zephyr_gov_audit_audit_schema_py
    src_zephyr_gov_audit_audit_schema_py ~~~ src_zephyr_gov_audit_audit_write_failure_protector_py
    src_zephyr_gov_audit_audit_write_failure_protector_py ~~~ src_zephyr_gov_audit_bridges_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_anomaly_py ~~~ src_zephyr_gov_audit_bridges_audit_contracts_py
    src_zephyr_gov_audit_bridges_audit_contracts_py ~~~ src_zephyr_gov_audit_bridges_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_drift_bridge_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py ~~~ src_zephyr_gov_audit_bridges_audit_trust_bridge_py
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py ~~~ src_zephyr_gov_audit_changelog_manager_py
    src_zephyr_gov_audit_changelog_manager_py ~~~ src_zephyr_gov_audit_cli_py
    src_zephyr_gov_audit_cli_py ~~~ src_zephyr_gov_audit_code_archaeology_py
    src_zephyr_gov_audit_code_archaeology_py ~~~ src_zephyr_gov_audit_cold_start_py
    src_zephyr_gov_audit_cold_start_py ~~~ src_zephyr_gov_audit_compliance_map_py
    src_zephyr_gov_audit_compliance_map_py ~~~ src_zephyr_gov_audit_corporate_actions_py
    src_zephyr_gov_audit_corporate_actions_py ~~~ src_zephyr_gov_audit_delegation_auditor_py
    src_zephyr_gov_audit_delegation_auditor_py ~~~ src_zephyr_gov_audit_dora_metrics_py
    src_zephyr_gov_audit_dora_metrics_py ~~~ src_zephyr_gov_audit_evidence_pack_py
    src_zephyr_gov_audit_evidence_pack_py ~~~ src_zephyr_gov_audit_external_tool_audit_py
    src_zephyr_gov_audit_external_tool_audit_py ~~~ src_zephyr_gov_audit_feedback_policy_py
    src_zephyr_gov_audit_feedback_policy_py ~~~ src_zephyr_gov_audit_feedback_self_audit_py
    src_zephyr_gov_audit_feedback_self_audit_py ~~~ src_zephyr_gov_audit_forensic_package_py
    src_zephyr_gov_audit_forensic_package_py ~~~ src_zephyr_gov_audit_genesis_py
    src_zephyr_gov_audit_genesis_py ~~~ src_zephyr_gov_audit_glossary_matrix_py
    src_zephyr_gov_audit_glossary_matrix_py ~~~ src_zephyr_gov_audit_incremental_review_py
    src_zephyr_gov_audit_incremental_review_py ~~~ src_zephyr_gov_audit_integrity_verifier_py
    src_zephyr_gov_audit_integrity_verifier_py ~~~ src_zephyr_gov_audit_kb_gate_py
    src_zephyr_gov_audit_kb_gate_py ~~~ src_zephyr_gov_audit_log_rotation_py
    src_zephyr_gov_audit_log_rotation_py ~~~ src_zephyr_gov_audit_merkle_audit_py
    src_zephyr_gov_audit_merkle_audit_py ~~~ src_zephyr_gov_audit_observability_dashboard_py
    src_zephyr_gov_audit_observability_dashboard_py ~~~ src_zephyr_gov_audit_pipeline_runner_py
    src_zephyr_gov_audit_pipeline_runner_py ~~~ src_zephyr_gov_audit_privacy_py
    src_zephyr_gov_audit_privacy_py ~~~ src_zephyr_gov_audit_provenance_tracker_py
    src_zephyr_gov_audit_provenance_tracker_py ~~~ src_zephyr_gov_audit_replay_engine_py
    src_zephyr_gov_audit_replay_engine_py ~~~ src_zephyr_gov_audit_retention_py
    src_zephyr_gov_audit_retention_py ~~~ src_zephyr_gov_audit_sbom_generator_py
    src_zephyr_gov_audit_sbom_generator_py ~~~ src_zephyr_gov_audit_spec_auditor_py
    src_zephyr_gov_audit_spec_auditor_py ~~~ src_zephyr_gov_audit_supply_chain_py
    src_zephyr_gov_audit_supply_chain_py ~~~ src_zephyr_gov_audit_supply_chain_security_py
    src_zephyr_gov_audit_supply_chain_security_py ~~~ src_zephyr_gov_audit_trust_ring_manager_py
    src_zephyr_gov_audit_trust_ring_manager_py ~~~ src_zephyr_gov_audit_wqa_scorer_py
    src_zephyr_gov_audit_wqa_scorer_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_post_process_py
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py ~~~ src_zephyr_governance_audit_trail_contracts_py
    src_zephyr_governance_audit_trail_contracts_py ~~~ src_zephyr_governance_audit_ai_error_pattern_library_py
    src_zephyr_governance_audit_ai_error_pattern_library_py ~~~ src_zephyr_governance_audit_blueprint_status_transition_reconciler_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py ~~~ src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py ~~~ src_zephyr_governance_audit_dead_public_wrapper_reconciler_py
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py ~~~ src_zephyr_governance_audit_default_attribution_engine_py
    src_zephyr_governance_audit_default_attribution_engine_py ~~~ src_zephyr_governance_audit_default_tca_engine_py
    src_zephyr_governance_audit_default_tca_engine_py ~~~ src_zephyr_governance_audit_git_performance_monitor_reconciler_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py ~~~ src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py ~~~ src_zephyr_governance_audit_snapshot_manager_py
    src_zephyr_governance_audit_snapshot_manager_py ~~~ src_zephyr_governance_audit_workspace_hygiene_reconciler_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py ~~~ src_zephyr_governance_financial_governance_financial_compliance_py
    src_zephyr_governance_financial_governance_financial_compliance_py ~~~ src_zephyr_governance_semantic_audit_compliance_map_py
    src_zephyr_governance_semantic_audit_compliance_map_py ~~~ src_zephyr_governance_semantic_audit_feedback_self_audit_py
    src_zephyr_governance_semantic_audit_feedback_self_audit_py ~~~ src_zephyr_governance_semantic_audit_fix_result_prioritizer_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py ~~~ src_zephyr_governance_semantic_audit_orchestrator_py
    src_zephyr_governance_semantic_audit_orchestrator_py ~~~ src_zephyr_governance_semantic_audit_privacy_py
    src_zephyr_governance_semantic_audit_privacy_py ~~~ src_zephyr_governance_semantic_audit_semantic_cache_py
    src_zephyr_governance_semantic_audit_semantic_cache_py ~~~ src_zephyr_governance_semantic_audit_spec_auditor_py
    src_zephyr_governance_semantic_audit_spec_auditor_py ~~~ tests_governance_audit_test_error_pattern_id_column_py
    tests_governance_audit_test_error_pattern_id_column_py ~~~ tests_governance_audit_test_p3_integration_smoke_py
    tests_governance_audit_test_p3_integration_smoke_py ~~~ tests_governance_audit_test_reconcile_async_py
    tests_governance_audit_test_reconcile_async_py ~~~ tests_governance_audit_test_reconcile_worker_selfheal_py
    tests_governance_audit_test_reconcile_worker_selfheal_py ~~~ tests_governance_audit_test_trae_069_threshold_sync_smoke_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py ~~~ tests_governance_rule_bridge_test_session_worktree_async_reconcile_py
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py ~~~ tests_governance_test_workspace_telemetry_shared_py
    src_zephyr_gov_audit_anomaly_py["gov_audit/anomaly<br/>gov audit包的anomaly模块<br/>文件: gov_audit/anomaly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_audit_admission_controller_py["gov_audit/audit_admission_controller<br/>gov audit包的audit_admission_controller模块<br/>文件: gov_audit/audit_admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_bridge_py["gov_audit/bridge<br/>gov audit包的bridge模块<br/>文件: gov_audit/bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_event_store_py["gov_audit/event_store<br/>EventStore — Event Sourcing 事件追加与回放<br/>（DW-0002）<br/>文件: gov_audit/event_store.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_query_py["gov_audit/query<br/>gov audit包的query模块<br/>文件: gov_audit/query.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_resource_aware_pool_py["gov_audit/resource_aware_pool<br/>gov audit包的resource_aware_pool模块<br/>文件: gov_audit/resource_aware_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_text_to_finding_adapter_py["gov_audit/text_to_finding_adapter<br/>gov audit包的text_to_finding_adapter模块<br/>文件: gov_audit/text_to_finding_adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_git_helpers_py["audit/_git_helpers<br/>_git_helpers.py — audit reconciler 共享 git<br/>工具模块<br/>文件: audit/_git_helpers.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py["audit/commit_gateway_abuse_monitor_reconciler<br/>commit_gateway_abuse_monitor_reconciler.py —<br/>commit gateway 持续滥用监控（AR...<br/>文件: audit<br/>/commit_gateway_abuse_monitor_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py["audit/error_pattern_consumer_reconciler<br/>error_pattern_consumer_reconciler.py — AI<br/>行为遥测 JSONL 错误事件聚合 consumer。<br/>文件: audit/error_pattern_consumer_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconcile_worker_py["audit/reconcile_worker<br/>reconcile_worker.py — 异步 reconciler worker<br/>（Ruling:100PCT-AI-GOVERNANCE P2...<br/>文件: audit/reconcile_worker.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_remediation_progress_reconciler_py["audit/remediation_progress_reconciler<br/>remediation_progress_reconciler.py —<br/>治本进度持久化 + 新鲜度对账（...<br/>文件: audit/remediation_progress_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_runtime_violation_snapshot_py["audit/runtime_violation_snapshot<br/>runtime_violation_snapshot.py — trae_060 §5<br/>evidence 运行时快照（...<br/>文件: audit/runtime_violation_snapshot.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_alignment_engine_py["semantic_audit/alignment_engine<br/>三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs<br/>import 引用链。<br/>文件: semantic_audit/alignment_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_fix_prioritizer_py["semantic_audit/fix_prioritizer<br/>按 severity -> certainty -> blast_radius<br/>三级排序,分组输出批次。<br/>文件: semantic_audit/fix_prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_issue_aggregator_py["semantic_audit/issue_aggregator<br/>收集各阶段审计结果，去重合并排序输出。<br/>文件: semantic_audit/issue_aggregator.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_kb_gate_py["semantic_audit/kb_gate<br/>audit-trail.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: semantic_audit/kb_gate.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_llm_bridge_py["semantic_audit/llm_bridge<br/>接收 RED 问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成。<br/>文件: semantic_audit/llm_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_safety_boundary_py["semantic_audit/safety_boundary<br/>禁碰规则过滤 + 置信度阈值。输入 TriggerResult<br/>列表,输出 SafetyDecision 分类。<br/>文件: semantic_audit/safety_boundary.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_self_healer_py["semantic_audit/self_healer<br/>Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: semantic_audit/self_healer.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_self_health_py["semantic_audit/self_health<br/>7 SLI + 5 容量 SLI + 退化检测。定时自检,输出<br/>HEALTHY/DEGRADED/CRITICAL。<br/>文件: semantic_audit/self_health.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_trigger_engine_py["semantic_audit/trigger_engine<br/>监听文件变更，判定是否触发语义审计。<br/>文件: semantic_audit/trigger_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_anomaly_py ~~~ src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_audit_admission_controller_py ~~~ src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_bridge_py ~~~ src_zephyr_gov_audit_event_store_py
    src_zephyr_gov_audit_event_store_py ~~~ src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_query_py ~~~ src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_resource_aware_pool_py ~~~ src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_text_to_finding_adapter_py ~~~ src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_git_helpers_py ~~~ src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py ~~~ src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py ~~~ src_zephyr_governance_audit_reconcile_worker_py
    src_zephyr_governance_audit_reconcile_worker_py ~~~ src_zephyr_governance_audit_remediation_progress_reconciler_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py ~~~ src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_runtime_violation_snapshot_py ~~~ src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_alignment_engine_py ~~~ src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py ~~~ src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py ~~~ src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_governance_semantic_audit_kb_gate_py ~~~ src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_llm_bridge_py ~~~ src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_safety_boundary_py ~~~ src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_self_healer_py ~~~ src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_self_health_py ~~~ src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_gov_audit_delegation_bridge_py["gov_audit/delegation_bridge<br/>gov audit包的delegation_bridge模块<br/>文件: gov_audit/delegation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_feedback_bridge_py["gov_audit/feedback_bridge<br/>gov audit包的feedback_bridge模块<br/>文件: gov_audit/feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_finding_ingest_py["gov_audit/finding_ingest<br/>gov audit包的finding_ingest模块<br/>文件: gov_audit/finding_ingest.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_indexer_py["gov_audit/indexer<br/>gov audit包的indexer模块<br/>文件: gov_audit/indexer.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_merkle_hourly_py["gov_audit/merkle_hourly<br/>audit-trail.merkle_hourly — MOD-INF-020 ·<br/>每小时 Merkle 聚合<br/>文件: gov_audit/merkle_hourly.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_models_py["gov_audit/models<br/>gov audit包的models模块<br/>文件: gov_audit/models.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_tiered_storage_bridge_py["gov_audit/tiered_storage_bridge<br/>gov audit包的tiered_storage_bridge模块<br/>文件: gov_audit/tiered_storage_bridge.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_bridge_py["gov_audit/trust_bridge<br/>gov audit包的trust_bridge模块<br/>文件: gov_audit/trust_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_health_score_calculator_py["audit/health_score_calculator<br/>health_score_calculator.py — commit gateway<br/>滥用 6 维加权健康度评分（P3-2，#...<br/>文件: audit/health_score_calculator.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconcile_runner_py["audit/reconcile_runner<br/>reconcile_runner.py — Reconciler 链路异步化<br/>（Ruling:100PCT-AI-GOVERNANCE P2-...<br/>文件: audit/reconcile_runner.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_reference_extractor_py["semantic_audit/reference_extractor<br/>AST 解析文件，提取 9 个维度的引用信息。<br/>文件: semantic_audit/reference_extractor.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_delegation_bridge_py ~~~ src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_feedback_bridge_py ~~~ src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_finding_ingest_py ~~~ src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_indexer_py ~~~ src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_merkle_hourly_py ~~~ src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_models_py ~~~ src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_tiered_storage_bridge_py ~~~ src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_trust_bridge_py ~~~ src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_health_score_calculator_py ~~~ src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_runner_py ~~~ src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_contracts_py["gov_audit/contracts<br/>gov audit包的contracts模块<br/>文件: gov_audit/contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_finding_model_py["gov_audit/finding_model<br/>gov audit包的finding_model模块<br/>文件: gov_audit/finding_model.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_integrity_py["gov_audit/integrity<br/>audit-trail.integrity — MOD-INF-020 ·<br/>密码学完整性验证器<br/>文件: gov_audit/integrity.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_tiered_storage_py["gov_audit/tiered_storage<br/>gov audit包的tiered_storage模块<br/>文件: gov_audit/tiered_storage.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_trust_engine_py["gov_audit/trust_engine<br/>gov audit包的trust_engine模块<br/>文件: gov_audit/trust_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_writer_py["gov_audit/writer<br/>gov audit包的writer模块<br/>文件: gov_audit/writer.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_reconciliation_registry_py["audit/reconciliation_registry<br/>reconciliation_registry.py — GitCommitGateway<br/>post-commit 漂移对账注册表（P2...<br/>文件: audit/reconciliation_registry.py<br/>(生产态 / production)"]
    src_zephyr_governance_semantic_audit_models_py["semantic_audit/models<br/>语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: semantic_audit/models.py<br/>(生产态 / production)"]
    src_zephyr_gov_audit_contracts_py ~~~ src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_model_py ~~~ src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_integrity_py ~~~ src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_tiered_storage_py ~~~ src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_trust_engine_py ~~~ src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_writer_py ~~~ src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconciliation_registry_py ~~~ src_zephyr_governance_semantic_audit_models_py
    src_zephyr_gov_audit_agent_signer_py["gov_audit/agent_signer<br/>audit-trail.agent_signer — MOD-INF-020 · Agent<br/>Ed25519 签名器<br/>文件: gov_audit/agent_signer.py<br/>(生产态 / production)"]
    src_zephyr_governance_audit_ai_error_pattern_library_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_dead_public_wrapper_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_runner_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_trail_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_governance_semantic_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_llm_bridge_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_reference_extractor_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_safety_boundary_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_write_failure_protector_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_delegation_auditor_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_agent_signer_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_merkle_audit_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_text_to_finding_adapter_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_trust_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_tiered_storage_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_bridges_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_error_pattern_id_column_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py,src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_resource_aware_pool_py,src_zephyr_gov_audit_retention_py,src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_trail_contracts_py,src_zephyr_governance_audit_git_helpers_py,src_zephyr_governance_audit_ai_error_pattern_library_py,src_zephyr_governance_audit_blueprint_status_transition_reconciler_py,src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py,src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py,src_zephyr_governance_audit_dead_public_wrapper_reconciler_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_error_pattern_consumer_reconciler_py,src_zephyr_governance_audit_git_performance_monitor_reconciler_py,src_zephyr_governance_audit_health_score_calculator_py,src_zephyr_governance_audit_reconcile_runner_py,src_zephyr_governance_audit_reconcile_worker_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_audit_runtime_violation_snapshot_py,src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_audit_workspace_hygiene_reconciler_py,src_zephyr_governance_financial_governance_financial_compliance_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py,src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_semantic_cache_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py,tests_governance_audit_test_error_pattern_id_column_py,tests_governance_audit_test_p3_integration_smoke_py,tests_governance_audit_test_reconcile_async_py,tests_governance_audit_test_reconcile_worker_selfheal_py,tests_governance_audit_test_trae_069_threshold_sync_smoke_py,tests_governance_rule_bridge_test_session_worktree_async_reconcile_py,tests_governance_test_workspace_telemetry_shared_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["audit_orchestrator/blueprint<br/>audit_orchestrator模块蓝图文档，描述该模块的设计<br/>意图和架构决策<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: audit_orchestrator/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md["audit_trail/blueprint<br/>audit_trail模块蓝图文档，描述该模块的设计意图和<br/>架构决策<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: audit_trail/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md ~~~ docs_03_modules_domain_governance_audit_trail_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | gov_audit/feedback_bridge.py | → | D_FEEDBACK_LOOP 反馈循环引擎: Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feedback_loop... | 导入依赖 / import_depends |
| 2 | audit_schema — 审计视图与查询入口（SH-DB-001 v2.0） (gov... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + SH-... | 导入依赖 / import_depends |
| 3 | Audit ↔ ContinuousTrust 信任分数桥接. (bridges/audit_tru... | → | D_GOVERNANCE 生命周期管理: Continuous Trust Ledger — 持续信任评估引擎。 (intelligen... | 导入依赖 / import_depends |
| 4 | EventStore — Event Sourcing 事件追加与回放（DW-0002） (g... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + SH-... | 导入依赖 / import_depends |
| 5 | audit-trail.evidence_pack — MOD-INF-020 · 证据包导出器 ... | → | D_GOVERNANCE 生命周期管理: governance/evidence_pack.py | 导入依赖 / import_depends |
| 6 | audit-trail.kb_gate — MOD-INF-020 · KB 审计门控 (gov_au... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (... | 导入依赖 / import_depends |
| 7 | audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏 (gov... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (... | 导入依赖 / import_depends |
| 8 | gov_audit/spec_auditor.py | → | D_GOVERNANCE 生命周期管理: G-CT-003 契约：Agent Spec -> RBAC 能力检查. (agent_spec/r... | 导入依赖 / import_depends |
| 9 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governance/depgraph... | 导入依赖 / import_depends |
| 10 | SnapshotManager — Event Sourcing 快照管理（DW-0005） (au... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-1-02 + SH-... | 导入依赖 / import_depends |
| 11 | audit-trail.kb_gate — MOD-INF-020 · KB 审计门控 (semant... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (... | 导入依赖 / import_depends |
| 12 | audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏 (sem... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (... | 导入依赖 / import_depends |
| 13 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: _reference_helpers.py — 引用检测门禁共享工具函数（ARCH-R... | 导入依赖 / import_depends |
| 14 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: capability_lookup_bypass_policy.py — CAPABILITY-LOOKUP b... | 导入依赖 / import_depends |
| 15 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-o... | 导入依赖 / import_depends |
| 16 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: scripts_import_integrity_gate.py — _shared.constants 符... | 导入依赖 / import_depends |
| 17 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | 导入依赖 / import_depends |
| 18 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 导入依赖 / import_depends |
| 19 | audit-orchestrator 兼容重导出层（ARCH-042 阶段4 修复双 MO... | → | D_GOV_DRIFT 漂移检测: gov_audit/self_monitor.py | 导入依赖 / import_depends |
| 20 | gov_audit/bridge.py | → | D_GOV_DRIFT 漂移检测: gov_audit/drift_bridge.py | 导入依赖 / import_depends |
| 21 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔ MOD-IN... | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (gov_drift/d... | 导入依赖 / import_depends |
| 22 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔ MOD-IN... | → | D_GOV_DRIFT 漂移检测: Drift Detector 数据模型 — drift_models.py (gov_drift/dri... | 导入依赖 / import_depends |
| 23 | gov_audit/cli.py | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (gov_drift/d... | 导入依赖 / import_depends |
| 24 | gov_audit/cli.py | → | D_GOV_DRIFT 漂移检测: governance/integrity.py | 导入依赖 / import_depends |
| 25 | git_performance_monitor_reconciler.py — git 性能持续监控... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 26 | reconcile_worker.py — 异步 reconciler worker（Ruling:100... | → | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 27 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 28 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 29 | test_reconcile_async.py — P2-3 reconciler 链路异步化测试... | → | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 30 | test_reconcile_worker_selfheal.py —... | → | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 31 | test_session_worktree_async_reconcile.py — _run_reconcil... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 32 | gov_audit/delegation_bridge.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Escalation Engine — MOD-INF-022 (escalation/escalation_e... | 导入依赖 / import_depends |
| 33 | gov_audit/pipeline_runner.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | 导入依赖 / import_depends |
| 34 | 审计链验证工具——独立重放门禁判定+Hash链完整性校验（beta... | → | D_GOV_RULE 规则治理: 门禁上下文传播——GateContext 构建/序列化/跨模块注入（bet... | 导入依赖 / import_depends |
| 35 | commit_gateway_abuse_monitor_reconciler.py — commit gate... | → | D_GOV_RULE 规则治理: 自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ ... | 导入依赖 / import_depends |
| 36 | test_p3_integration_smoke.py — Phase 3 全链路集成 smoke ... | → | D_GOV_RULE 规则治理: 自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ ... | 测试依赖 / test_depends |
| 37 | [INVARIANTS] 按path精确匹配+按功能名模糊匹配; 输出差距报... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 38 | [INVARIANTS] 20项红蓝对抗测试 (repair/red_blue_test.py) | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 39 | [INVARIANTS] 仅接受depgraph.backup.*路径; 回滚前自动备份... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 40 | test_remediation_progress_smoke.py — Phase 3.1 治本进度 ... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 41 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_SCRIPTS 脚本治理: module_id / domain_id / submodule_id 格式校验真源... | 导入依赖 / import_depends |
| 42 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_GOV_SCRIPTS 脚本治理: check_gate_inventory_drift.py — commit_gates 模块清单漂... | 导入依赖 / import_depends |
| 43 | workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | → | D_INFRA_RUNTIME 运行时集成: git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | 导入依赖 / import_depends |
| 44 | Re-export wrapper: default_attribution_engine canonical a... | → | D_REPORTING 报告: D_REPORTING — Default Attribution Engine (reporting/defa... | 导入依赖 / import_depends |
| 45 | Re-export wrapper: default_tca_engine canonical at zephyr... | → | D_REPORTING 报告: D_REPORTING — Default TCA Engine (reporting/default_tca_... | 导入依赖 / import_depends |
| 46 | gov_audit/cli.py | → | D_SECURITY 对抗验证: orphan_judge/judge.py | 导入依赖 / import_depends |
| 47 | gov_audit/cli.py | → | D_SECURITY 对抗验证: adversarial_validation/validator.py | 导入依赖 / import_depends |
| 48 | reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 49 | reconcile_worker.py — 异步 reconciler worker（Ruling:100... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 50 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 51 | [INVARIANTS] 20项红蓝对抗测试 (repair/red_blue_test.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 52 | [INVARIANTS] 仅接受depgraph.backup.*路径; 回滚前自动备份... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 53 | audit-trail.agent_signer — MOD-INF-020 · Agent Ed25519 ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 54 | audit_schema — 审计视图与查询入口（SH-DB-001 v2.0） (gov... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 55 | audit_schema — 审计视图与查询入口（SH-DB-001 v2.0） (gov... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 56 | G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔ MOD-IN... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 57 | gov_audit/cli.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 58 | gov_audit/cli.py | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 59 | BootstrapCache — 审计冷启动共享单例缓存。 (gov_audit/col... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 60 | BootstrapCache — 审计冷启动共享单例缓存。 (gov_audit/col... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 61 | EventStore — Event Sourcing 事件追加与回放（DW-0002） (g... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 62 | audit-trail.evidence_pack — MOD-INF-020 · 证据包导出器 ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 63 | gov_audit/external_tool_audit.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 64 | gov_audit/feedback_bridge.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 65 | gov_audit/finding_ingest.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 66 | gov_audit/finding_model.py | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 67 | Forensic Package — v0.8.0 取证就绪: escalation event bun... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 68 | gov_audit/indexer.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 69 | gov_audit/indexer.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 70 | audit-trail.integrity — MOD-INF-020 · 密码学完整性验证... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 71 | audit-trail.integrity — MOD-INF-020 · 密码学完整性验证... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 72 | gov_audit/log_rotation.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 73 | audit-trail.merkle_hourly — MOD-INF-020 · 每小时 Merkle... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 74 | gov_audit/pipeline_runner.py | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 75 | gov_audit/pipeline_runner.py | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 76 | gov_audit/query.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 77 | gov_audit/retention.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 78 | audit-trail.supply_chain — MOD-INF-020 · 供应链审计 (go... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 79 | gov_audit/text_to_finding_adapter.py | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 80 | gov_audit/tiered_storage.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 81 | gov_audit/writer.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 82 | gov_audit/writer.py | → | D_SHARED 共享服务: session_audit.py —— Session 审计轨迹（Phase 12 | 盲点 B... | 导入依赖 / import_depends |
| 83 | gov_audit/writer.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 84 | behavioral_admission/mcp_result_push.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 85 | post_process.py —— AI 生成代码后处理管道（Phase 13 | 盲... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 86 | 审计链验证工具——独立重放门禁判定+Hash链完整性校验（beta... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 87 | SYS-MASTER-001 Compliance Checker (rule_enforcement/sys_m... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 88 | SYS-MASTER-001 Compliance Checker (rule_enforcement/sys_m... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 89 | _git_helpers.py — audit reconciler 共享 git 工具模块 (au... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 90 | blueprint_status_transition_reconciler.py — 蓝图状态单调... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 91 | commit_gateway_abuse_monitor_reconciler.py — commit gate... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 92 | cross_layer_contract_signature_reconciler.py — 跨层契约... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 93 | git_performance_monitor_reconciler.py — git 性能持续监控... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 94 | reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 95 | reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 96 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 97 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 98 | reconciliation_registry.py — GitCommitGateway post-commi... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 99 | remediation_progress_reconciler.py — 治本进度持久化 + 新... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 100 | runtime_violation_snapshot.py — trae_060 §5 evidence 运... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 101 | SnapshotManager — Event Sourcing 快照管理（DW-0005） (au... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 102 | SnapshotManager — Event Sourcing 快照管理（DW-0005） (au... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 103 | workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 104 | 收集各阶段审计结果，去重合并排序输出。 (semantic_audit/is... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 105 | Stage 7 自愈闭环 — 修复->自测->回滚. (semantic_audit/sel... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 106 | Stage 7 自愈闭环 — 修复->自测->回滚. (semantic_audit/sel... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（SSoT 真源... | 导入依赖 / import_depends |
| 107 | test_workspace_telemetry_shared.py — shared workspace_te... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 测试依赖 / test_depends |
| 108 | test_workspace_telemetry_shared.py — shared workspace_te... | → | D_SHARED 共享服务: workspace_telemetry.py — 主工作区文件操作遥测公共 API（.... | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: skills/skill_executor.py | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — Skill Sandbox (skills/skill_sa... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — SpecEngine 蓝图->Skill 升级引... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 4 | D_FBL_VERIFICATION 反馈验证: Safety Gates L66-L67 — Financial Prudence + Full Integra... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: git_commit.py — GitCommitGateway CLI 封装（OPS-202606251... | → | workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: ProjectionEngine — 事件折叠为当前状态（DW-0003） (observ... | → | EventStore — Event Sourcing 事件追加与回放（DW-0002） (g... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: DatabaseManager — 连接池 + 健康检查 + 自动备份 + WAL che... | → | audit_schema — 审计视图与查询入口（SH-DB-001 v2.0） (gov... | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: GovernanceServer: 治理域统一MCP入口 (mcp/governance_serve... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 9 | D_GOV_CODE_QUALITY 代码质量治理: panorama_alignment_gate.py — 三图模块对齐门禁（四图模块... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 10 | D_GOV_CODE_QUALITY 代码质量治理: reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 11 | D_GOV_DRIFT 漂移检测: gov_audit/drift_bridge.py | → | gov_audit/anomaly.py | 导入依赖 / import_depends |
| 12 | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (gov_drift/d... | → | gov_audit/finding_ingest.py | 导入依赖 / import_depends |
| 13 | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (gov_drift/d... | → | gov_audit/finding_model.py | 导入依赖 / import_depends |
| 14 | D_GOV_DRIFT 漂移检测: 真源优先级裁决器（Truth Source Validator） (rule_enforcem... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 15 | D_GOV_DRIFT 漂移检测: governance/integrity.py | → | audit-trail.merkle_hourly — MOD-INF-020 · 每小时 Merkle... | 导入依赖 / import_depends |
| 16 | D_GOV_DRIFT 漂移检测: governance/integrity.py | → | gov_audit/models.py | 导入依赖 / import_depends |
| 17 | D_GOV_DRIFT 漂移检测: governance/integrity.py | → | gov_audit/trust_bridge.py | 导入依赖 / import_depends |
| 18 | D_GOV_ENFORCEMENT 规则执行: metric_count_drift_reconciler.py — dashboard 指标数描述... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 19 | D_GOV_ENFORCEMENT 规则执行: readme_version_sync_reconciler.py — README 版本号派生展... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 20 | D_GOV_ENFORCEMENT 规则执行: requirements_version_sync_reconciler.py — requirements.t... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 21 | D_GOV_ENFORCEMENT 规则执行: behavioral_admission/__init__.py | → | behavioral_admission/mcp_result_push.py | 导入依赖 / import_depends |
| 22 | D_GOV_ENFORCEMENT 规则执行: behavioral_admission/__init__.py | → | post_process.py —— AI 生成代码后处理管道（Phase 13 | 盲... | 导入依赖 / import_depends |
| 23 | D_GOV_ENFORCEMENT 规则执行: behavioral_admission/__init__.py | → | behavioral_admission/vibe_coding_enforcer.py | 导入依赖 / import_depends |
| 24 | D_GOV_ENFORCEMENT 规则执行: GateEventAdapter — GateRepo 事件适配器（DW-0006） (behav... | → | EventStore — Event Sourcing 事件追加与回放（DW-0002） (g... | 导入依赖 / import_depends |
| 25 | D_GOV_ENFORCEMENT 规则执行: behavioral_admission/verdict_engine.py | → | gov_audit/models.py | 导入依赖 / import_depends |
| 26 | D_GOV_ENFORCEMENT 规则执行: emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 27 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | blueprint_status_transition_reconciler.py — 蓝图状态单调... | 导入依赖 / import_depends |
| 28 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | commit_gateway_abuse_monitor_reconciler.py — commit gate... | 导入依赖 / import_depends |
| 29 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | cross_layer_contract_signature_reconciler.py — 跨层契约... | 导入依赖 / import_depends |
| 30 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | dead_public_wrapper_reconciler.py — 死公共 wrapper 自动... | 导入依赖 / import_depends |
| 31 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | error_pattern_consumer_reconciler.py — AI 行为遥测 JSONL... | 导入依赖 / import_depends |
| 32 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | git_performance_monitor_reconciler.py — git 性能持续监控... | 导入依赖 / import_depends |
| 33 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | 导入依赖 / import_depends |
| 34 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 35 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | remediation_progress_reconciler.py — 治本进度持久化 + 新... | 导入依赖 / import_depends |
| 36 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | runtime_violation_snapshot_reconciler.py — trae_060 §5 ... | 导入依赖 / import_depends |
| 37 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | 导入依赖 / import_depends |
| 38 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | ai_error_pattern_library.py — AI 错误模式库（只读查询接... | 导入依赖 / import_depends |
| 39 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | 导入依赖 / import_depends |
| 40 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 41 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | 导入依赖 / import_depends |
| 42 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | audit-trail.integrity — MOD-INF-020 · 密码学完整性验证... | 导入依赖 / import_depends |
| 43 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | gov_audit/query.py | 导入依赖 / import_depends |
| 44 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 45 | D_GOV_OPS_RESILIENCE 运维弹性治理: PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控... | → | SYS-MASTER-001 Compliance Checker (rule_enforcement/sys_m... | 导入依赖 / import_depends |
| 46 | D_GOV_OPS_RESILIENCE 运维弹性治理: blast_radius — MOD-INF-028 §3.1 Stage 9 (resilience_gov... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 (semantic_audit... | 导入依赖 / import_depends |
| 47 | D_GOV_OPS_RESILIENCE 运维弹性治理: security_governance/tamper_evident_log.py | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 48 | D_GOV_RULE 规则治理: 能力检查器（Capability Checker） (rule_enforcement/capabi... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 49 | D_GOV_RULE 规则治理: Owner 紧急旁路——时间限定的门禁临时绕过 + 审计追踪（beta... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 50 | D_GOV_SCRIPTS 脚本治理: Red/Blue Team Adversarial Test v3: SYS-MASTER-001 + MOD-M... | → | SYS-MASTER-001 Compliance Checker (rule_enforcement/sys_m... | 导入依赖 / import_depends |
| 51 | D_GOV_SCRIPTS 脚本治理: scripts/governance/rebuild_audit_index.py — 重建 audit-t... | → | gov_audit/indexer.py | 导入依赖 / import_depends |
| 52 | D_GOV_SCRIPTS 脚本治理: architecture_health_dashboard.py — 架构健康度仪表盘（自... | → | runtime_violation_snapshot.py — trae_060 §5 evidence 运... | 导入依赖 / import_depends |
| 53 | D_GOV_SCRIPTS 脚本治理: session_startup_health_check.py — AI session 启动健康度... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 54 | D_INFRASTRUCTURE 跨层契约基础设施: backup_reconciler.py — 灾备备份系统事件触发器（post-comm... | → | reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 55 | D_INFRA_RECOVERY 回滚恢复: G-CT-004 契约：Rollback -> Audit 记录回滚操作. (rollback/... | → | gov_audit/contracts.py | 导入依赖 / import_depends |
| 56 | D_INFRA_RECOVERY 回滚恢复: RollbackAbuseDetector — 回滚滥用检测。 (rollback/rollbac... | → | gov_audit/query.py | 导入依赖 / import_depends |
| 57 | D_INFRA_RECOVERY 回滚恢复: RollbackAuditNexus — 回滚审计记录聚合到 Nexus AuditLog. ... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 58 | D_INFRA_RECOVERY 回滚恢复: RollbackExecutor — 回滚执行器核心封装。 (rollback/rollba... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 59 | D_INFRA_RUNTIME 运行时集成: AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 60 | D_INFRA_RUNTIME 运行时集成: auto_fix_engine/engine.py | → | gov_audit/finding_model.py | 导入依赖 / import_depends |
| 61 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic resource opti... | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 62 | D_INTEGRATION 管线路由: 接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 (semantic_audit... | 导入依赖 / import_depends |
| 63 | D_INTEGRATION 管线路由: MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。 (mc... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 64 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (integration/pi... | → | gov_audit/writer.py | 导入依赖 / import_depends |
| 65 | D_SECURITY 对抗验证: G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. (access_... | → | gov_audit/contracts.py | 导入依赖 / import_depends |
| 66 | D_SECURITY 对抗验证: orphan_judge/judge.py | → | gov_audit/finding_model.py | 导入依赖 / import_depends |
| 67 | D_SECURITY 对抗验证: adversarial_validation/defense_runner.py | → | gov_audit/finding_model.py | 导入依赖 / import_depends |
| 68 | D_SECURITY 对抗验证: llm_security/behavior_audit_logger.py | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 69 | D_SECURITY 对抗验证: self_protection/isolation.py | → | gov_audit/bridge.py | 导入依赖 / import_depends |
| 70 | D_TRADING 交易运营: trading/verdict_engine.py | → | gov_audit/models.py | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 18 个外部域直接连接（出边 108 条 + 入边 70 条 = 178 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_FBL_VERIFICATION["D_FBL_VERIFICATION<br/>反馈验证"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOV_AUDIT -->|58条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SHARED
    D_GOV_AUDIT -->|11条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_AUDIT -->|7条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_DRIFT
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_AUDIT -->|5条 导入依赖 / import_depends| D_SECURITY
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_RULE
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_REPORTING
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOV_ENFORCEMENT -->|24条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_DRIFT -->|7条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_OPS_RESILIENCE -->|6条 导入依赖 / import_depends| D_GOV_AUDIT
    D_SECURITY -->|5条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RECOVERY -->|4条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_SCRIPTS -->|4条 导入依赖 / import_depends| D_GOV_AUDIT
    D_AUTONOMY_CORE -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_RULE -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRASTRUCTURE -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_FBL_VERIFICATION -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_TRADING -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
