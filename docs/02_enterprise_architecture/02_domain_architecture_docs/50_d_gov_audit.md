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
| 模块数 | 123 | Module Count | 123 |
| 域内依赖 | 103 | Internal Dependencies | 103 |
| 跨域入边 | 69 | Cross-domain Incoming | 69 |
| 跨域出边 | 107 | Cross-domain Outgoing | 107 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 121 | Production Modules | 121 |
| 容量 | 121/150 (正常) | Capacity | 121/150 (正常) |
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

> 展示全部 123 个模块（生产态 121 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图（blueprint.md）<br/>文件: audit_orchestrator/blueprint.md<br/>⛔ 该域，设计已就绪，等待开发排期"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图（blueprint.md）<br/>文件: audit_trail/blueprint.md<br/>⛔ 该域，设计已就绪，等待开发排期"]
    scripts_governance_repair_audit_design_completeness_py["(生产态 / production) 审计designcompleteness /<br/>audit_design_completeness<br/>(INVARIANTS) 按path精确匹配+按功能名模糊匹配;<br/>输出差距报告; 提取所有ID格式<br/>文件: repair/audit_design_completeness.py"]
    scripts_governance_repair_red_blue_test_py["(生产态 / production) (INVARIANTS)<br/>20项红蓝对抗测试 / red_blue_test<br/>(INVARIANTS) 20项红蓝对抗测试<br/>文件: repair/red_blue_test.py"]
    scripts_governance_repair_rollback_depgraph_py["(生产态 / production) 回滚依赖图 / rollback_<br/>depgraph<br/>(INVARIANTS) 仅接受depgraph.backup.*路径;<br/>回滚前自动备份当前depgraph<br/>文件: repair/rollback_depgraph.py"]
    scripts_governance_test_remediation_progress_smoke_py["(生产态 / production) 测试修复进度smoke / test_<br/>remediation_progress_smoke<br/>测试修复进度smoke.1 治本进度 reconciler<br/>end-to-end smoke test。<br/>文件: governance/test_remediation_progress_<br/>smoke.py"]
    src_zephyr_gov_audit_orchestrator_compat_py["(生产态 / production) 编排器兼容 / _<br/>orchestrator_compat<br/>audit-orchestrator 兼容重导出层（ARCH-042 阶段4<br/>修复双 MODULE，ARCH-043 Risk3 改名）<br/>文件: gov_audit/_orchestrator_compat.py"]
    src_zephyr_gov_audit_action_history_py["(生产态 / production) 行为历史 / action_history<br/>ActionHistory — 操作历史持久化审计 + 去重 +<br/>循环检测<br/>文件: gov_audit/action_history.py"]
    src_zephyr_gov_audit_api_lifecycle_py["(生产态 / production) API生命周期 / api_<br/>lifecycle<br/>API生命周期，审计的状态机，管理状态流转。<br/>文件: gov_audit/api_lifecycle.py"]
    src_zephyr_gov_audit_audit_schema_py["(生产态 / production) 审计模式 / audit_schema<br/>audit_schema — 审计视图与查询入口（SH-DB-001<br/>v2.0）<br/>文件: gov_audit/audit_schema.py"]
    src_zephyr_gov_audit_audit_write_failure_protector_py["(生产态 / production) 审计write故障protector /<br/>audit_write_failure_protector<br/>Audit Write Failure Protector — v0.13.0<br/>审计写入失败保护器。<br/>文件: gov_audit/audit_write_failure_protector.py"]
    src_zephyr_gov_audit_bridges_audit_anomaly_py["(生产态 / production) 审计异常 / audit_anomaly<br/>G-CT-002 Audit 异常检测器 — AnomalyEvent<br/>Pydantic V2 BaseModel.<br/>文件: bridges/audit_anomaly.py"]
    src_zephyr_gov_audit_bridges_audit_contracts_py["(生产态 / production) 审计契约 / audit_contracts<br/>G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: bridges/audit_contracts.py"]
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["(生产态 / production) 审计delegation桥接 /<br/>audit_delegation_bridge<br/>Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: bridges/audit_delegation_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py["(生产态 / production) 审计漂移桥接 / audit_<br/>drift_bridge<br/>G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔<br/>MOD-INF-023<br/>文件: bridges/audit_drift_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["(生产态 / production) 审计反馈桥接 / audit_<br/>feedback_bridge<br/>Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: bridges/audit_feedback_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["(生产态 / production) 审计tiered存储桥接 /<br/>audit_tiered_storage_bridge<br/>Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: bridges/audit_tiered_storage_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py["(生产态 / production) 审计信任桥接 / audit_<br/>trust_bridge<br/>Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: bridges/audit_trust_bridge.py"]
    src_zephyr_gov_audit_changelog_manager_py["(生产态 / production) changelog管理器 /<br/>changelog_manager<br/>changelog管理器，审计的日志器，记录运行日志。<br/>文件: gov_audit/changelog_manager.py"]
    src_zephyr_gov_audit_cli_py["(生产态 / production) 命令行 / cli<br/>命令行，供End users; CI/CD; MCP tool wra使用<br/>文件: gov_audit/cli.py"]
    src_zephyr_gov_audit_code_archaeology_py["(生产态 / production) 代码archaeology / code_<br/>archaeology<br/>代码archaeology，审计的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: gov_audit/code_archaeology.py"]
    src_zephyr_gov_audit_cold_start_py["(生产态 / production) 冷启动 / cold_start<br/>BootstrapCache — 审计冷启动共享单例缓存。<br/>文件: gov_audit/cold_start.py"]
    src_zephyr_gov_audit_compliance_map_py["(生产态 / production) 合规map / compliance_map<br/>合规map.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: gov_audit/compliance_map.py"]
    src_zephyr_gov_audit_corporate_actions_py["(生产态 / production) 公司行为 / corporate_<br/>actions<br/>公司行为，审计的类型，定义数据类型和枚举。<br/>文件: gov_audit/corporate_actions.py"]
    src_zephyr_gov_audit_delegation_auditor_py["(生产态 / production) delegation审计器 /<br/>delegation_auditor<br/>委托链升级类型 -- str+Enum 使 == 'string_value'<br/>可用.<br/>文件: gov_audit/delegation_auditor.py"]
    src_zephyr_gov_audit_dora_metrics_py["(生产态 / production) dora指标 / dora_metrics<br/>dora指标，供MOD-INF-027;MOD-INF-015;MOD-FE使用<br/>文件: gov_audit/dora_metrics.py"]
    src_zephyr_gov_audit_evidence_pack_py["(生产态 / production) 证据包 / evidence_pack<br/>证据包.evidence_pack — MOD-INF-020 ·<br/>证据包导出器<br/>文件: gov_audit/evidence_pack.py"]
    src_zephyr_gov_audit_external_tool_audit_py["(生产态 / production) externaltool审计 /<br/>external_tool_audit<br/>外部tool审计，主要提供审计tool、审计模块、摘要等<br/>功能，供audit-orchestrator.pipeline_ru使用<br/>文件: gov_audit/external_tool_audit.py"]
    src_zephyr_gov_audit_feedback_policy_py["(生产态 / production) 反馈策略 / feedback_<br/>policy.py — Audit-findings → policy<br/>recommendation<br/>反馈策略，审计的策略，定义决策规则。<br/>文件: gov_audit/feedback_policy.py"]
    src_zephyr_gov_audit_feedback_self_audit_py["(生产态 / production) 反馈自审计 / feedback_<br/>self_audit<br/>反馈自审计.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: gov_audit/feedback_self_audit.py"]
    src_zephyr_gov_audit_forensic_package_py["(生产态 / production) 取证包 / forensic_package<br/>Forensic Package — v0.8.0 取证就绪: escalation<br/>event bundle+hash chain+timestamp。<br/>文件: gov_audit/forensic_package.py"]
    src_zephyr_gov_audit_genesis_py["(生产态 / production) audit-trail.genesis —<br/>MOD-INF-020 · 创世块管 / genesis<br/>audit-trail.genesis — MOD-INF-020 ·<br/>创世块管.genesis — MOD-INF-020 ·<br/>创世块管.genesis — MOD-INF-020 · 创世块管理<br/>文件: gov_audit/genesis.py"]
    src_zephyr_gov_audit_glossary_matrix_py["(生产态 / production) 词汇表矩阵 / glossary_<br/>matrix<br/>词汇表矩阵，供MOD-INF-027;MOD-INF-015;MOD-FE使用<br/>文件: gov_audit/glossary_matrix.py"]
    src_zephyr_gov_audit_incremental_review_py["(生产态 / production) incremental审查 /<br/>incremental_review<br/>incremental审查，供MOD-INF-027;MOD-INF-015;MOD-F<br/>E使用<br/>文件: gov_audit/incremental_review.py"]
    src_zephyr_gov_audit_integrity_verifier_py["(生产态 / production) 完整性验证器 / integrity_<br/>verifier<br/>Integrity Verifier — v0.8.0 代码完整性验证器:<br/>hash校验+diff detection+rollback。<br/>文件: gov_audit/integrity_verifier.py"]
    src_zephyr_gov_audit_kb_gate_py["(生产态 / production) 知识库门禁 / kb_gate<br/>知识库门禁.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: gov_audit/kb_gate.py"]
    src_zephyr_gov_audit_log_rotation_py["(生产态 / production) 日志rotation / log_<br/>rotation<br/>审计日志轮转管理器——按天轮转<br/>events.jsonl，支持压缩和过期清理。<br/>文件: gov_audit/log_rotation.py"]
    src_zephyr_gov_audit_merkle_audit_py["(生产态 / production) merkle审计 / merkle_audit<br/>Merkle Audit — 兼容别名，SSoT已迁移至<br/>zephyr.gov_audit (MOD-INF-020).<br/>文件: gov_audit/merkle_audit.py"]
    src_zephyr_gov_audit_observability_dashboard_py["(生产态 / production) 可观测性仪表盘 /<br/>observability_dashboard<br/>可观测性仪表盘，供MOD-INF-027;MOD-INF-015;MOD-FE<br/>使用<br/>文件: gov_audit/observability_dashboard.py"]
    src_zephyr_gov_audit_pipeline_runner_py["(生产态 / production) 管线运行器 / pipeline_<br/>runner<br/>管线运行器，审计的结果，封装操作结果的数据结构。<br/>文件: gov_audit/pipeline_runner.py"]
    src_zephyr_gov_audit_privacy_py["(生产态 / production) 审计轨迹·隐私模块 /<br/>privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: gov_audit/privacy.py"]
    src_zephyr_gov_audit_provenance_tracker_py["(生产态 / production) 溯源追踪器 / provenance_<br/>tracker<br/>provenance追踪器，审计的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: gov_audit/provenance_tracker.py"]
    src_zephyr_gov_audit_replay_engine_py["(生产态 / production) 重放快照<br/>（补全测试期望接口）。 / replay_engine<br/>重放快照（补全测试期望接口）。<br/>文件: gov_audit/replay_engine.py"]
    src_zephyr_gov_audit_retention_py["(生产态 / production) 保留策略<br/>（补全测试期望接口）。 / retention<br/>保留策略（补全测试期望接口）。<br/>文件: gov_audit/retention.py"]
    src_zephyr_gov_audit_sbom_generator_py["(生产态 / production) sbom生成器 / sbom_<br/>generator<br/>LicenseType 枚举——许可证类型定义（P3<br/>价值审判退役残留）。<br/>文件: gov_audit/sbom_generator.py"]
    src_zephyr_gov_audit_spec_auditor_py["(生产态 / production) spec审计器 / spec_auditor<br/>spec审计器，供zephyr.gov_audit使用<br/>文件: gov_audit/spec_auditor.py"]
    src_zephyr_gov_audit_supply_chain_py["(生产态 / production) supply链 / supply_chain<br/>supply链.supply_chain — MOD-INF-020 · 供应链审计<br/>文件: gov_audit/supply_chain.py"]
    src_zephyr_gov_audit_supply_chain_security_py["(生产态 / production) supplychain安全 / supply_<br/>chain_security<br/>supplychain安全，供MOD-INF-027;MOD-INF-015;MOD-F<br/>E使用<br/>文件: gov_audit/supply_chain_security.py"]
    src_zephyr_gov_audit_trust_ring_manager_py["(生产态 / production) trustring管理器 / trust_<br/>ring_manager<br/>trustring管理器，提供包入口和模块加载功能<br/>文件: gov_audit/trust_ring_manager.py"]
    src_zephyr_gov_audit_wqa_scorer_py["(生产态 / production) wqa评分器 / wqa_scorer<br/>wqa评分器，主要提供composite、rating等功能<br/>文件: gov_audit/wqa_scorer.py"]
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["(生产态 / production) ai代码standards / ai_code_<br/>standards<br/>ai代码standards（ai_code_standards.py）<br/>文件: behavioral_admission/ai_code_standards.py"]
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["(生产态 / production) MCP结果推送 / mcp_result_<br/>push<br/>MCP结果推送，治理执行的异常，定义本模块的异常类<br/>型。<br/>文件: behavioral_admission/mcp_result_push.py"]
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py["(生产态 / production) 提交进程 / post_process<br/>— AI 生成代码后处理管道（Phase 13 / 盲点 B31）<br/>文件: behavioral_admission/post_process.py"]
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["(生产态 / production) vibecoding执行器 / vibe_<br/>coding_enforcer<br/>vibecoding执行器，治理执行的核心类，封装VibeRule<br/>Level相关逻辑。<br/>文件: behavioral_admission/vibe_coding_<br/>enforcer.py"]
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["(生产态 / production) 审计链验证器 / audit_<br/>chain_verifier<br/>审计链验证工具——独立重放门禁判定+Hash链完整性校<br/>验（beta）<br/>文件: rule_enforcement/audit_chain_verifier.py"]
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["(生产态 / production) sys主合规 /<br/>SYS-MASTER-001 Compliance Checker<br/>sys主合规。SYS-MASTER-001 Compliance Checker<br/>文件: rule_enforcement/sys_master_compliance.py"]
    src_zephyr_governance_audit_trail_contracts_py["(生产态 / production) 契约 / contracts<br/>契约.py — G-CT-002 Audit 契约（re-export）。<br/>文件: audit-trail/contracts.py"]
    src_zephyr_governance_audit_ai_error_pattern_library_py["(生产态 / production) AI错误模式库 / ai_error_<br/>pattern_library<br/>AI 错误模式库（只读查询接口）。<br/>文件: audit/ai_error_pattern_library.py"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py["(生产态 / production) 蓝图状态转换协调器 /<br/>blueprint_status_transition_reconciler<br/>蓝图状态单调推进 reconciler<br/>（P1-d，2026-07-21）。<br/>文件: audit/blueprint_status_transition_<br/>reconciler.py"]
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py["(生产态 / production)<br/>跨layercontractsignature对账器 / cross_layer_<br/>contract_signature_reconciler<br/>跨层契约签名漂移检测 reconciler<br/>（P1-b，2026-07-21）。<br/>文件: audit/cross_layer_contract_signature_<br/>reconciler.py"]
    src_zephyr_governance_audit_default_attribution_engine_py["(生产态 / production) 默认attribution引擎 /<br/>Re-export wrapper: default_attribution_engine<br/>canonical at z<br/>默认attribution引擎。Re-export wrapper: default_<br/>attribution_engine canonical at<br/>zephyr.reporting.default_attribution_engi<br/>文件: audit/default_attribution_engine.py"]
    src_zephyr_governance_audit_default_tca_engine_py["(生产态 / production) 默认tca引擎 / Re-export<br/>wrapper: default_tca_engine canonical at<br/>zephyr.re<br/>默认tca引擎。Re-export wrapper: default_tca_<br/>engine canonical at zephyr.reporting.default_<br/>tca_engine.<br/>文件: audit/default_tca_engine.py"]
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py["(生产态 / production) Git绩效监控协调器 / git_<br/>performance_monitor_reconciler<br/>git 性能持续监控 + 早期预警<br/>（ARCH-GIT-CALL-BUDGET P3.5，2026-07-19）。<br/>文件: audit/git_performance_monitor_<br/>reconciler.py"]
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py["(生产态 / production) 运行时违规快照协调器 /<br/>runtime_violation_snapshot_reconciler<br/>trae_060 §5 evidence 运行时快照 post-commit<br/>reconciler。<br/>文件: audit/runtime_violation_snapshot_<br/>reconciler.py"]
    src_zephyr_governance_audit_snapshot_manager_py["(生产态 / production) 快照管理器 / snapshot_<br/>manager<br/>SnapshotManager — Event Sourcing 快照管理<br/>（DW-0005）<br/>文件: audit/snapshot_manager.py"]
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py["(生产态 / production) 工作区hygiene对账器 /<br/>workspace_hygiene_reconciler<br/>工作区卫生自动清理 reconciler<br/>（DEBT-WORKSPACE-001/002 消除，2026-07-20）。<br/>文件: audit/workspace_hygiene_reconciler.py"]
    src_zephyr_governance_financial_governance_financial_compliance_py["(生产态 / production) 金融合规 / financial_<br/>compliance<br/>financial合规，治理的核心类，封装ComplianceLayer<br/>相关逻辑。<br/>文件: financial_governance/financial_<br/>compliance.py"]
    src_zephyr_governance_semantic_audit_compliance_map_py["(生产态 / production) 合规map / compliance_map<br/>合规map.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: semantic_audit/compliance_map.py"]
    src_zephyr_governance_semantic_audit_feedback_self_audit_py["(生产态 / production) 反馈自审计 / feedback_<br/>self_audit<br/>反馈自审计.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: semantic_audit/feedback_self_audit.py"]
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["(生产态 / production) 修复结果prioritizer / fix_<br/>prioritizer — MOD-INF-028 §3.1 Stage 8<br/>修复结果prioritizer。fix_prioritizer —<br/>MOD-INF-028 §3.1 Stage 8<br/>文件: semantic_audit/fix_result_prioritizer.py"]
    src_zephyr_governance_semantic_audit_orchestrator_py["(生产态 / production) 编排器 / orchestrator<br/>SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: semantic_audit/orchestrator.py"]
    src_zephyr_governance_semantic_audit_privacy_py["(生产态 / production) 审计轨迹·隐私模块 /<br/>privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: semantic_audit/privacy.py"]
    src_zephyr_governance_semantic_audit_semantic_cache_py["(生产态 / production) semantic缓存 / semantic_<br/>cache<br/>semantic缓存，审计的缓存，暂存常用数据加速访问。<br/>文件: semantic_audit/semantic_cache.py"]
    src_zephyr_governance_semantic_audit_spec_auditor_py["(生产态 / production) spec审计器 / spec_auditor<br/>G-CT-007 — Audit.record_agent_spec() 记录 Agent<br/>Spec 注册与变更.<br/>文件: semantic_audit/spec_auditor.py"]
    tests_governance_audit_test_error_pattern_id_column_py["(生产态 / production) 测试错误patternidcolumn /<br/>test_error_pattern_id_column<br/>测试错误patternidcolumn.error_pattern_id<br/>列幂等迁移单测（P4-1a）<br/>文件: audit/test_error_pattern_id_column.py"]
    tests_governance_audit_test_p3_integration_smoke_py["(生产态 / production) 测试p3集成smoke / test_p3_<br/>integration_smoke<br/>Phase 3 全链路集成 smoke test<br/>文件: audit/test_p3_integration_smoke.py"]
    tests_governance_audit_test_reconcile_async_py["(生产态 / production) 测试对账异步 / test_<br/>reconcile_async<br/>P2-3 reconciler 链路异步化测试<br/>文件: audit/test_reconcile_async.py"]
    tests_governance_audit_test_reconcile_worker_selfheal_py["(生产态 / production) 测试对账工作进程selfheal<br/>/ test_reconcile_worker_selfheal<br/>#ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 测试<br/>文件: audit/test_reconcile_worker_selfheal.py"]
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py["(生产态 / production)<br/>测试trae069thresholdsyncsmoke / test_trae_069_<br/>threshold_sync_smoke<br/>trae_069 YAML 真源→代码常量同步 smoke test<br/>文件: audit/test_trae_069_threshold_sync_<br/>smoke.py"]
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py["(生产态 / production) 测试会话worktree异步对账<br/>/ test_session_worktree_async_reconcile<br/>_run_reconcilers_after_merge 异步化测试。<br/>文件: rule_bridge/test_session_worktree_async_<br/>reconcile.py"]
    tests_governance_test_workspace_telemetry_shared_py["(生产态 / production) 测试工作区遥测共享 / test_<br/>workspace_telemetry_shared<br/>shared workspace_telemetry 公共 API 单测<br/>文件: governance/test_workspace_telemetry_<br/>shared.py"]
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
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py ~~~ src_zephyr_governance_audit_default_attribution_engine_py
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
    src_zephyr_gov_audit_anomaly_py["(生产态 / production) 异常 / anomaly<br/>异常签名枚举——治本（裁定#18 G3）：转为真 Enum<br/>对齐 test_audit_anomaly.py 契约。<br/>文件: gov_audit/anomaly.py"]
    src_zephyr_gov_audit_audit_admission_controller_py["(生产态 / production) 审计准入控制器 / audit_<br/>admission_controller<br/>审计准入控制器，审计的结果，封装操作结果的数据结<br/>构。<br/>文件: gov_audit/audit_admission_controller.py"]
    src_zephyr_gov_audit_bridge_py["(生产态 / production) 写入核心审计链——治本<br/>（裁定#18 G7 + 5.37.1） / bridge<br/>写入核心审计链——治本（裁定#18 G7 +<br/>5.37.1）：真实落盘 events.jsonl。<br/>文件: gov_audit/bridge.py"]
    src_zephyr_gov_audit_event_store_py["(生产态 / production) 事件存储 / event_store<br/>EventStore — Event Sourcing 事件追加与回放<br/>（DW-0002）<br/>文件: gov_audit/event_store.py"]
    src_zephyr_gov_audit_query_py["(生产态 / production) 旧版查询引擎<br/>（保留以兼容现有调用方）。 / query<br/>旧版查询引擎（保留以兼容现有调用方）。<br/>文件: gov_audit/query.py"]
    src_zephyr_gov_audit_resource_aware_pool_py["(生产态 / production) 资源感知池 / resource_<br/>aware_pool<br/>资源感知池，供audit_admission_controller; or使用<br/>文件: gov_audit/resource_aware_pool.py"]
    src_zephyr_gov_audit_text_to_finding_adapter_py["(生产态 / production) texttofinding适配器 /<br/>text_to_finding_adapter<br/>textto发现适配器，审计的解析器，把文本<br/>/数据解析成结构化对象。<br/>文件: gov_audit/text_to_finding_adapter.py"]
    src_zephyr_governance_audit_git_helpers_py["(生产态 / production) Git辅助 / _git_helpers<br/>审计 reconciler 共享 git 工具模块<br/>文件: audit/_git_helpers.py"]
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py["(生产态 / production)<br/>commitgatewayabuse监控器对账器 / commit_gateway_<br/>abuse_monitor_reconciler<br/>commit gateway 持续滥用监控<br/>（ARCH-TOOL-HEALTH-V1 Phase 5b，2026-07-19）。<br/>文件: audit/commit_gateway_abuse_monitor_<br/>reconciler.py"]
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py["(生产态 / production) 错误模式消费者协调器 /<br/>error_pattern_consumer_reconciler<br/>AI 行为遥测 JSONL 错误事件聚合 consumer。<br/>文件: audit/error_pattern_consumer_reconciler.py"]
    src_zephyr_governance_audit_reconcile_worker_py["(生产态 / production) 对账工作器 / reconcile_<br/>worker<br/>异步 reconciler worker<br/>（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）<br/>文件: audit/reconcile_worker.py"]
    src_zephyr_governance_audit_remediation_progress_reconciler_py["(生产态 / production) 修复进度对账器 /<br/>remediation_progress_reconciler<br/>治本进度持久化 + 新鲜度对账<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.1）。<br/>文件: audit/remediation_progress_reconciler.py"]
    src_zephyr_governance_audit_runtime_violation_snapshot_py["(生产态 / production) 运行时违规快照 / runtime_<br/>violation_snapshot<br/>trae_060 §5 evidence 运行时快照<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.4b）。<br/>文件: audit/runtime_violation_snapshot.py"]
    src_zephyr_governance_semantic_audit_alignment_engine_py["(生产态 / production) 对齐引擎 / alignment_<br/>engine<br/>三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs<br/>import 引用链。<br/>文件: semantic_audit/alignment_engine.py"]
    src_zephyr_governance_semantic_audit_fix_prioritizer_py["(生产态 / production) 修复prioritizer / fix_<br/>prioritizer<br/>按 severity -> certainty -> blast_radius<br/>三级排序,分组输出批次。<br/>文件: semantic_audit/fix_prioritizer.py"]
    src_zephyr_governance_semantic_audit_issue_aggregator_py["(生产态 / production)<br/>收集各阶段审计结果，去重合并排序输出。 / issue_<br/>aggregator<br/>收集各阶段审计结果，去重合并排序输出。<br/>文件: semantic_audit/issue_aggregator.py"]
    src_zephyr_governance_semantic_audit_kb_gate_py["(生产态 / production) 知识库门禁 / kb_gate<br/>知识库门禁.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: semantic_audit/kb_gate.py"]
    src_zephyr_governance_semantic_audit_llm_bridge_py["(生产态 / production) 接收 RED<br/>问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成 / llm_<br/>bridge<br/>接收 RED 问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成。<br/>文件: semantic_audit/llm_bridge.py"]
    src_zephyr_governance_semantic_audit_safety_boundary_py["(生产态 / production) 安全boundary / safety_<br/>boundary<br/>禁碰规则过滤 + 置信度阈值。输入 TriggerResult<br/>列表,输出 SafetyDecision 分类。<br/>文件: semantic_audit/safety_boundary.py"]
    src_zephyr_governance_semantic_audit_self_healer_py["(生产态 / production) self愈合器 / self_healer<br/>Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: semantic_audit/self_healer.py"]
    src_zephyr_governance_semantic_audit_self_health_py["(生产态 / production) 7 SLI + 5 容量 SLI +<br/>退化检测。定时自检,输出 HEALTHY/ / self_health<br/>7 SLI + 5 容量 SLI + 退化检测。定时自检,输出<br/>HEALTHY/DEGRADED/CRITICAL。<br/>文件: semantic_audit/self_health.py"]
    src_zephyr_governance_semantic_audit_trigger_engine_py["(生产态 / production)<br/>监听文件变更，判定是否触发语义审计。 / trigger_<br/>engine<br/>监听文件变更，判定是否触发语义审计。<br/>文件: semantic_audit/trigger_engine.py"]
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
    src_zephyr_gov_audit_delegation_bridge_py["(生产态 / production) delegation桥接 /<br/>delegation_bridge<br/>delegation桥接，主要提供报告delegationfailure、<br/>报告delegation超时、isavailable等功能，供audit-o<br/>rchestrator.delegation_使用<br/>文件: gov_audit/delegation_bridge.py"]
    src_zephyr_gov_audit_feedback_bridge_py["(生产态 / production) 反馈桥接 / feedback_bridge<br/>反馈桥接。Bridge between audit-trail anomaly<br/>findings and the Feedback Loop Engine.<br/>文件: gov_audit/feedback_bridge.py"]
    src_zephyr_gov_audit_finding_ingest_py["(生产态 / production) 发现ingest / finding_<br/>ingest<br/>发现ingest，审计的结果，封装操作结果的数据结构。<br/>文件: gov_audit/finding_ingest.py"]
    src_zephyr_gov_audit_indexer_py["(生产态 / production) 索引重建结果——治本<br/>（裁定#18 G5）：对齐 testa / indexer<br/>索引重建结果——治本（裁定#18 G5）：对齐 test_<br/>audit_indexer.py 契约。<br/>文件: gov_audit/indexer.py"]
    src_zephyr_gov_audit_merkle_hourly_py["(生产态 / production) audit-trail.merkle每小时<br/>/ merkle_hourly<br/>audit-trail.merkle每小时.merkle每小时· 每小时<br/>Merkle 聚合<br/>文件: gov_audit/merkle_hourly.py"]
    src_zephyr_gov_audit_models_py["(生产态 / production) 审计事件类型枚举——治本<br/>（裁定#18 G2）：转为真 Enu / models<br/>审计事件类型枚举——治本（裁定#18 G2）：转为真<br/>Enum，values 全部小写。<br/>文件: gov_audit/models.py"]
    src_zephyr_gov_audit_tiered_storage_bridge_py["(生产态 / production) tiered存储桥接 / tiered_<br/>storage_bridge<br/>tieredstorage桥接，主要提供find报告、migrate、st<br/>ats等功能，供audit-orchestrator.bridge; ret使用<br/>文件: gov_audit/tiered_storage_bridge.py"]
    src_zephyr_gov_audit_trust_bridge_py["(生产态 / production) 信任桥接 / trust_bridge<br/>信任桥接，主要提供评估、记录、获取趋势等功能，供<br/>audit-orchestrator.bridge; int使用<br/>文件: gov_audit/trust_bridge.py"]
    src_zephyr_governance_audit_health_score_calculator_py["(生产态 / production) 健康评分计算器 / health_<br/>score_calculator<br/>commit gateway 滥用 6 维加权健康度评分<br/>（P3-2，#ARCH-PREVENTABILITY-LAYER-001 Phase<br/>3）。<br/>文件: audit/health_score_calculator.py"]
    src_zephyr_governance_audit_reconcile_runner_py["(生产态 / production) 对账运行器 / reconcile_<br/>runner<br/>Reconciler 链路异步化<br/>（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）<br/>文件: audit/reconcile_runner.py"]
    src_zephyr_governance_semantic_audit_reference_extractor_py["(生产态 / production) AST 解析文件，提取 9<br/>个维度的引用信息。 / reference_extractor<br/>AST 解析文件，提取 9 个维度的引用信息。<br/>文件: semantic_audit/reference_extractor.py"]
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
    src_zephyr_gov_audit_contracts_py["(生产态 / production) 契约 / contracts<br/>核心审计链写入器——桥接 contracts 层到 writer<br/>实现。<br/>文件: gov_audit/contracts.py"]
    src_zephyr_gov_audit_finding_model_py["(生产态 / production) 发现模型 / finding_model<br/>发现模型，审计的模型，定义数据结构和字段。<br/>文件: gov_audit/finding_model.py"]
    src_zephyr_gov_audit_integrity_py["(生产态 / production) 完整性 / integrity<br/>完整性.integrity — MOD-INF-020 ·<br/>密码学完整性验证器<br/>文件: gov_audit/integrity.py"]
    src_zephyr_gov_audit_tiered_storage_py["(生产态 / production) 旧版分层存储<br/>（保留以兼容现有调用方）。 / tiered_storage<br/>旧版分层存储（保留以兼容现有调用方）。<br/>文件: gov_audit/tiered_storage.py"]
    src_zephyr_gov_audit_trust_engine_py["(生产态 / production) 信任评分调整记录<br/>（补全测试期望接口）。 / trust_engine<br/>信任评分调整记录（补全测试期望接口）。<br/>文件: gov_audit/trust_engine.py"]
    src_zephyr_gov_audit_writer_py["(生产态 / production) 不可变审计写入器——JSONL<br/>追加 + SHA-256 哈 / writer<br/>不可变审计写入器——JSONL 追加 + SHA-256 哈希链 +<br/>HMAC-SHA256 签名 + Lamport 时钟。<br/>文件: gov_audit/writer.py"]
    src_zephyr_governance_audit_reconciliation_registry_py["(生产态 / production) 对账注册表 /<br/>reconciliation_registry<br/>GitCommitGateway post-commit 漂移对账注册表<br/>文件: audit/reconciliation_registry.py"]
    src_zephyr_governance_semantic_audit_models_py["(生产态 / production) 语义审计管线数据模型 —<br/>MOD-INF-028 §4.2 / models<br/>语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: semantic_audit/models.py"]
    src_zephyr_gov_audit_contracts_py ~~~ src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_model_py ~~~ src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_integrity_py ~~~ src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_tiered_storage_py ~~~ src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_trust_engine_py ~~~ src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_writer_py ~~~ src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconciliation_registry_py ~~~ src_zephyr_governance_semantic_audit_models_py
    src_zephyr_gov_audit_agent_signer_py["(生产态 / production) 代理signer / agent_signer<br/>代理signer.agent_signer — MOD-INF-020 · Agent<br/>Ed25519 签名器<br/>文件: gov_audit/agent_signer.py"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_ai_error_pattern_library_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_runner_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_trail_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_llm_bridge_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_safety_boundary_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_reference_extractor_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_write_failure_protector_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_delegation_auditor_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_agent_signer_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_merkle_audit_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_tiered_storage_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_text_to_finding_adapter_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_trust_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_error_pattern_id_column_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_SCRIPTS["(生产态 / production) 脚本治理 / Script<br/>Governance<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>跨域节点 / cross-domain"]
    src_zephyr_governance_audit_reconciliation_registry_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    scripts_governance_repair_red_blue_test_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle<br/>Management<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_audit_spec_auditor_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial<br/>Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| D_SECURITY
    D_GOV_DRIFT["(生产态 / production) 漂移检测 / Drift Detection<br/>漂移检测，负责架构漂移检测和漂移告警<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_audit_reconcile_runner_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_repair_rollback_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_semantic_audit_kb_gate_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_audit_event_store_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_repair_rollback_depgraph_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) 规则执行 / Rule<br/>Enforcement<br/>规则执行，负责治理规则执行和门禁拦截<br/>跨域节点 / cross-domain"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_TRADING["(生产态 / production) 交易运营 / Trading<br/>Operations<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>跨域节点 / cross-domain"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) 运维弹性治理 / Ops<br/>Resilience Governance<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>跨域节点 / cross-domain"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_ai_error_pattern_library_py
    D_INTEGRATION["(生产态 / production) 管线路由 / Pipeline<br/>Routing<br/>管线路由，负责跨域数据流路由、管道编排和集成适配<br/>跨域节点 / cross-domain"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py
    D_GOV_DRIFT -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py,src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_resource_aware_pool_py,src_zephyr_gov_audit_retention_py,src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_trail_contracts_py,src_zephyr_governance_audit_git_helpers_py,src_zephyr_governance_audit_ai_error_pattern_library_py,src_zephyr_governance_audit_blueprint_status_transition_reconciler_py,src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py,src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_error_pattern_consumer_reconciler_py,src_zephyr_governance_audit_git_performance_monitor_reconciler_py,src_zephyr_governance_audit_health_score_calculator_py,src_zephyr_governance_audit_reconcile_runner_py,src_zephyr_governance_audit_reconcile_worker_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_audit_runtime_violation_snapshot_py,src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_audit_workspace_hygiene_reconciler_py,src_zephyr_governance_financial_governance_financial_compliance_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py,src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_semantic_cache_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py,tests_governance_audit_test_error_pattern_id_column_py,tests_governance_audit_test_p3_integration_smoke_py,tests_governance_audit_test_reconcile_async_py,tests_governance_audit_test_reconcile_worker_selfheal_py,tests_governance_audit_test_trae_069_threshold_sync_smoke_py,tests_governance_rule_bridge_test_session_worktree_async_reconcile_py,tests_governance_test_workspace_telemetry_shared_py production
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
    class D_GOV_SCRIPTS,D_SHARED,D_GOVERNANCE,D_SECURITY,D_GOV_DRIFT,D_GOV_ENFORCEMENT,D_TRADING,D_GOV_OPS_RESILIENCE,D_INTEGRATION external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 121 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_repair_audit_design_completeness_py["(生产态 / production) 审计designcompleteness /<br/>audit_design_completeness<br/>(INVARIANTS) 按path精确匹配+按功能名模糊匹配;<br/>输出差距报告; 提取所有ID格式<br/>文件: repair/audit_design_completeness.py"]
    scripts_governance_repair_red_blue_test_py["(生产态 / production) (INVARIANTS)<br/>20项红蓝对抗测试 / red_blue_test<br/>(INVARIANTS) 20项红蓝对抗测试<br/>文件: repair/red_blue_test.py"]
    scripts_governance_repair_rollback_depgraph_py["(生产态 / production) 回滚依赖图 / rollback_<br/>depgraph<br/>(INVARIANTS) 仅接受depgraph.backup.*路径;<br/>回滚前自动备份当前depgraph<br/>文件: repair/rollback_depgraph.py"]
    scripts_governance_test_remediation_progress_smoke_py["(生产态 / production) 测试修复进度smoke / test_<br/>remediation_progress_smoke<br/>测试修复进度smoke.1 治本进度 reconciler<br/>end-to-end smoke test。<br/>文件: governance/test_remediation_progress_<br/>smoke.py"]
    src_zephyr_gov_audit_orchestrator_compat_py["(生产态 / production) 编排器兼容 / _<br/>orchestrator_compat<br/>audit-orchestrator 兼容重导出层（ARCH-042 阶段4<br/>修复双 MODULE，ARCH-043 Risk3 改名）<br/>文件: gov_audit/_orchestrator_compat.py"]
    src_zephyr_gov_audit_action_history_py["(生产态 / production) 行为历史 / action_history<br/>ActionHistory — 操作历史持久化审计 + 去重 +<br/>循环检测<br/>文件: gov_audit/action_history.py"]
    src_zephyr_gov_audit_api_lifecycle_py["(生产态 / production) API生命周期 / api_<br/>lifecycle<br/>API生命周期，审计的状态机，管理状态流转。<br/>文件: gov_audit/api_lifecycle.py"]
    src_zephyr_gov_audit_audit_schema_py["(生产态 / production) 审计模式 / audit_schema<br/>audit_schema — 审计视图与查询入口（SH-DB-001<br/>v2.0）<br/>文件: gov_audit/audit_schema.py"]
    src_zephyr_gov_audit_audit_write_failure_protector_py["(生产态 / production) 审计write故障protector /<br/>audit_write_failure_protector<br/>Audit Write Failure Protector — v0.13.0<br/>审计写入失败保护器。<br/>文件: gov_audit/audit_write_failure_protector.py"]
    src_zephyr_gov_audit_bridges_audit_anomaly_py["(生产态 / production) 审计异常 / audit_anomaly<br/>G-CT-002 Audit 异常检测器 — AnomalyEvent<br/>Pydantic V2 BaseModel.<br/>文件: bridges/audit_anomaly.py"]
    src_zephyr_gov_audit_bridges_audit_contracts_py["(生产态 / production) 审计契约 / audit_contracts<br/>G-CT-001 契约消费端 — Audit.write() 公共接口.<br/>文件: bridges/audit_contracts.py"]
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py["(生产态 / production) 审计delegation桥接 /<br/>audit_delegation_bridge<br/>Audit ↔ DelegationManager 委托链审计桥接.<br/>文件: bridges/audit_delegation_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py["(生产态 / production) 审计漂移桥接 / audit_<br/>drift_bridge<br/>G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔<br/>MOD-INF-023<br/>文件: bridges/audit_drift_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py["(生产态 / production) 审计反馈桥接 / audit_<br/>feedback_bridge<br/>Audit ↔ Feedback Loop 三角闭环桥接.<br/>文件: bridges/audit_feedback_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py["(生产态 / production) 审计tiered存储桥接 /<br/>audit_tiered_storage_bridge<br/>Audit ↔ WarmHotGate 三层存储桥接.<br/>文件: bridges/audit_tiered_storage_bridge.py"]
    src_zephyr_gov_audit_bridges_audit_trust_bridge_py["(生产态 / production) 审计信任桥接 / audit_<br/>trust_bridge<br/>Audit ↔ ContinuousTrust 信任分数桥接.<br/>文件: bridges/audit_trust_bridge.py"]
    src_zephyr_gov_audit_changelog_manager_py["(生产态 / production) changelog管理器 /<br/>changelog_manager<br/>changelog管理器，审计的日志器，记录运行日志。<br/>文件: gov_audit/changelog_manager.py"]
    src_zephyr_gov_audit_cli_py["(生产态 / production) 命令行 / cli<br/>命令行，供End users; CI/CD; MCP tool wra使用<br/>文件: gov_audit/cli.py"]
    src_zephyr_gov_audit_code_archaeology_py["(生产态 / production) 代码archaeology / code_<br/>archaeology<br/>代码archaeology，审计的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: gov_audit/code_archaeology.py"]
    src_zephyr_gov_audit_cold_start_py["(生产态 / production) 冷启动 / cold_start<br/>BootstrapCache — 审计冷启动共享单例缓存。<br/>文件: gov_audit/cold_start.py"]
    src_zephyr_gov_audit_compliance_map_py["(生产态 / production) 合规map / compliance_map<br/>合规map.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: gov_audit/compliance_map.py"]
    src_zephyr_gov_audit_corporate_actions_py["(生产态 / production) 公司行为 / corporate_<br/>actions<br/>公司行为，审计的类型，定义数据类型和枚举。<br/>文件: gov_audit/corporate_actions.py"]
    src_zephyr_gov_audit_delegation_auditor_py["(生产态 / production) delegation审计器 /<br/>delegation_auditor<br/>委托链升级类型 -- str+Enum 使 == 'string_value'<br/>可用.<br/>文件: gov_audit/delegation_auditor.py"]
    src_zephyr_gov_audit_dora_metrics_py["(生产态 / production) dora指标 / dora_metrics<br/>dora指标，供MOD-INF-027;MOD-INF-015;MOD-FE使用<br/>文件: gov_audit/dora_metrics.py"]
    src_zephyr_gov_audit_evidence_pack_py["(生产态 / production) 证据包 / evidence_pack<br/>证据包.evidence_pack — MOD-INF-020 ·<br/>证据包导出器<br/>文件: gov_audit/evidence_pack.py"]
    src_zephyr_gov_audit_external_tool_audit_py["(生产态 / production) externaltool审计 /<br/>external_tool_audit<br/>外部tool审计，主要提供审计tool、审计模块、摘要等<br/>功能，供audit-orchestrator.pipeline_ru使用<br/>文件: gov_audit/external_tool_audit.py"]
    src_zephyr_gov_audit_feedback_policy_py["(生产态 / production) 反馈策略 / feedback_<br/>policy.py — Audit-findings → policy<br/>recommendation<br/>反馈策略，审计的策略，定义决策规则。<br/>文件: gov_audit/feedback_policy.py"]
    src_zephyr_gov_audit_feedback_self_audit_py["(生产态 / production) 反馈自审计 / feedback_<br/>self_audit<br/>反馈自审计.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: gov_audit/feedback_self_audit.py"]
    src_zephyr_gov_audit_forensic_package_py["(生产态 / production) 取证包 / forensic_package<br/>Forensic Package — v0.8.0 取证就绪: escalation<br/>event bundle+hash chain+timestamp。<br/>文件: gov_audit/forensic_package.py"]
    src_zephyr_gov_audit_genesis_py["(生产态 / production) audit-trail.genesis —<br/>MOD-INF-020 · 创世块管 / genesis<br/>audit-trail.genesis — MOD-INF-020 ·<br/>创世块管.genesis — MOD-INF-020 ·<br/>创世块管.genesis — MOD-INF-020 · 创世块管理<br/>文件: gov_audit/genesis.py"]
    src_zephyr_gov_audit_glossary_matrix_py["(生产态 / production) 词汇表矩阵 / glossary_<br/>matrix<br/>词汇表矩阵，供MOD-INF-027;MOD-INF-015;MOD-FE使用<br/>文件: gov_audit/glossary_matrix.py"]
    src_zephyr_gov_audit_incremental_review_py["(生产态 / production) incremental审查 /<br/>incremental_review<br/>incremental审查，供MOD-INF-027;MOD-INF-015;MOD-F<br/>E使用<br/>文件: gov_audit/incremental_review.py"]
    src_zephyr_gov_audit_integrity_verifier_py["(生产态 / production) 完整性验证器 / integrity_<br/>verifier<br/>Integrity Verifier — v0.8.0 代码完整性验证器:<br/>hash校验+diff detection+rollback。<br/>文件: gov_audit/integrity_verifier.py"]
    src_zephyr_gov_audit_kb_gate_py["(生产态 / production) 知识库门禁 / kb_gate<br/>知识库门禁.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: gov_audit/kb_gate.py"]
    src_zephyr_gov_audit_log_rotation_py["(生产态 / production) 日志rotation / log_<br/>rotation<br/>审计日志轮转管理器——按天轮转<br/>events.jsonl，支持压缩和过期清理。<br/>文件: gov_audit/log_rotation.py"]
    src_zephyr_gov_audit_merkle_audit_py["(生产态 / production) merkle审计 / merkle_audit<br/>Merkle Audit — 兼容别名，SSoT已迁移至<br/>zephyr.gov_audit (MOD-INF-020).<br/>文件: gov_audit/merkle_audit.py"]
    src_zephyr_gov_audit_observability_dashboard_py["(生产态 / production) 可观测性仪表盘 /<br/>observability_dashboard<br/>可观测性仪表盘，供MOD-INF-027;MOD-INF-015;MOD-FE<br/>使用<br/>文件: gov_audit/observability_dashboard.py"]
    src_zephyr_gov_audit_pipeline_runner_py["(生产态 / production) 管线运行器 / pipeline_<br/>runner<br/>管线运行器，审计的结果，封装操作结果的数据结构。<br/>文件: gov_audit/pipeline_runner.py"]
    src_zephyr_gov_audit_privacy_py["(生产态 / production) 审计轨迹·隐私模块 /<br/>privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: gov_audit/privacy.py"]
    src_zephyr_gov_audit_provenance_tracker_py["(生产态 / production) 溯源追踪器 / provenance_<br/>tracker<br/>provenance追踪器，审计的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: gov_audit/provenance_tracker.py"]
    src_zephyr_gov_audit_replay_engine_py["(生产态 / production) 重放快照<br/>（补全测试期望接口）。 / replay_engine<br/>重放快照（补全测试期望接口）。<br/>文件: gov_audit/replay_engine.py"]
    src_zephyr_gov_audit_retention_py["(生产态 / production) 保留策略<br/>（补全测试期望接口）。 / retention<br/>保留策略（补全测试期望接口）。<br/>文件: gov_audit/retention.py"]
    src_zephyr_gov_audit_sbom_generator_py["(生产态 / production) sbom生成器 / sbom_<br/>generator<br/>LicenseType 枚举——许可证类型定义（P3<br/>价值审判退役残留）。<br/>文件: gov_audit/sbom_generator.py"]
    src_zephyr_gov_audit_spec_auditor_py["(生产态 / production) spec审计器 / spec_auditor<br/>spec审计器，供zephyr.gov_audit使用<br/>文件: gov_audit/spec_auditor.py"]
    src_zephyr_gov_audit_supply_chain_py["(生产态 / production) supply链 / supply_chain<br/>supply链.supply_chain — MOD-INF-020 · 供应链审计<br/>文件: gov_audit/supply_chain.py"]
    src_zephyr_gov_audit_supply_chain_security_py["(生产态 / production) supplychain安全 / supply_<br/>chain_security<br/>supplychain安全，供MOD-INF-027;MOD-INF-015;MOD-F<br/>E使用<br/>文件: gov_audit/supply_chain_security.py"]
    src_zephyr_gov_audit_trust_ring_manager_py["(生产态 / production) trustring管理器 / trust_<br/>ring_manager<br/>trustring管理器，提供包入口和模块加载功能<br/>文件: gov_audit/trust_ring_manager.py"]
    src_zephyr_gov_audit_wqa_scorer_py["(生产态 / production) wqa评分器 / wqa_scorer<br/>wqa评分器，主要提供composite、rating等功能<br/>文件: gov_audit/wqa_scorer.py"]
    src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py["(生产态 / production) ai代码standards / ai_code_<br/>standards<br/>ai代码standards（ai_code_standards.py）<br/>文件: behavioral_admission/ai_code_standards.py"]
    src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py["(生产态 / production) MCP结果推送 / mcp_result_<br/>push<br/>MCP结果推送，治理执行的异常，定义本模块的异常类<br/>型。<br/>文件: behavioral_admission/mcp_result_push.py"]
    src_zephyr_gov_enforcement_behavioral_admission_post_process_py["(生产态 / production) 提交进程 / post_process<br/>— AI 生成代码后处理管道（Phase 13 / 盲点 B31）<br/>文件: behavioral_admission/post_process.py"]
    src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py["(生产态 / production) vibecoding执行器 / vibe_<br/>coding_enforcer<br/>vibecoding执行器，治理执行的核心类，封装VibeRule<br/>Level相关逻辑。<br/>文件: behavioral_admission/vibe_coding_<br/>enforcer.py"]
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py["(生产态 / production) 审计链验证器 / audit_<br/>chain_verifier<br/>审计链验证工具——独立重放门禁判定+Hash链完整性校<br/>验（beta）<br/>文件: rule_enforcement/audit_chain_verifier.py"]
    src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py["(生产态 / production) sys主合规 /<br/>SYS-MASTER-001 Compliance Checker<br/>sys主合规。SYS-MASTER-001 Compliance Checker<br/>文件: rule_enforcement/sys_master_compliance.py"]
    src_zephyr_governance_audit_trail_contracts_py["(生产态 / production) 契约 / contracts<br/>契约.py — G-CT-002 Audit 契约（re-export）。<br/>文件: audit-trail/contracts.py"]
    src_zephyr_governance_audit_ai_error_pattern_library_py["(生产态 / production) AI错误模式库 / ai_error_<br/>pattern_library<br/>AI 错误模式库（只读查询接口）。<br/>文件: audit/ai_error_pattern_library.py"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py["(生产态 / production) 蓝图状态转换协调器 /<br/>blueprint_status_transition_reconciler<br/>蓝图状态单调推进 reconciler<br/>（P1-d，2026-07-21）。<br/>文件: audit/blueprint_status_transition_<br/>reconciler.py"]
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py["(生产态 / production)<br/>跨layercontractsignature对账器 / cross_layer_<br/>contract_signature_reconciler<br/>跨层契约签名漂移检测 reconciler<br/>（P1-b，2026-07-21）。<br/>文件: audit/cross_layer_contract_signature_<br/>reconciler.py"]
    src_zephyr_governance_audit_default_attribution_engine_py["(生产态 / production) 默认attribution引擎 /<br/>Re-export wrapper: default_attribution_engine<br/>canonical at z<br/>默认attribution引擎。Re-export wrapper: default_<br/>attribution_engine canonical at<br/>zephyr.reporting.default_attribution_engi<br/>文件: audit/default_attribution_engine.py"]
    src_zephyr_governance_audit_default_tca_engine_py["(生产态 / production) 默认tca引擎 / Re-export<br/>wrapper: default_tca_engine canonical at<br/>zephyr.re<br/>默认tca引擎。Re-export wrapper: default_tca_<br/>engine canonical at zephyr.reporting.default_<br/>tca_engine.<br/>文件: audit/default_tca_engine.py"]
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py["(生产态 / production) Git绩效监控协调器 / git_<br/>performance_monitor_reconciler<br/>git 性能持续监控 + 早期预警<br/>（ARCH-GIT-CALL-BUDGET P3.5，2026-07-19）。<br/>文件: audit/git_performance_monitor_<br/>reconciler.py"]
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py["(生产态 / production) 运行时违规快照协调器 /<br/>runtime_violation_snapshot_reconciler<br/>trae_060 §5 evidence 运行时快照 post-commit<br/>reconciler。<br/>文件: audit/runtime_violation_snapshot_<br/>reconciler.py"]
    src_zephyr_governance_audit_snapshot_manager_py["(生产态 / production) 快照管理器 / snapshot_<br/>manager<br/>SnapshotManager — Event Sourcing 快照管理<br/>（DW-0005）<br/>文件: audit/snapshot_manager.py"]
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py["(生产态 / production) 工作区hygiene对账器 /<br/>workspace_hygiene_reconciler<br/>工作区卫生自动清理 reconciler<br/>（DEBT-WORKSPACE-001/002 消除，2026-07-20）。<br/>文件: audit/workspace_hygiene_reconciler.py"]
    src_zephyr_governance_financial_governance_financial_compliance_py["(生产态 / production) 金融合规 / financial_<br/>compliance<br/>financial合规，治理的核心类，封装ComplianceLayer<br/>相关逻辑。<br/>文件: financial_governance/financial_<br/>compliance.py"]
    src_zephyr_governance_semantic_audit_compliance_map_py["(生产态 / production) 合规map / compliance_map<br/>合规map.compliance_map — MOD-INF-020 ·<br/>合规框架映射<br/>文件: semantic_audit/compliance_map.py"]
    src_zephyr_governance_semantic_audit_feedback_self_audit_py["(生产态 / production) 反馈自审计 / feedback_<br/>self_audit<br/>反馈自审计.feedback_self_audit — MOD-INF-020 ·<br/>反馈自审计<br/>文件: semantic_audit/feedback_self_audit.py"]
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py["(生产态 / production) 修复结果prioritizer / fix_<br/>prioritizer — MOD-INF-028 §3.1 Stage 8<br/>修复结果prioritizer。fix_prioritizer —<br/>MOD-INF-028 §3.1 Stage 8<br/>文件: semantic_audit/fix_result_prioritizer.py"]
    src_zephyr_governance_semantic_audit_orchestrator_py["(生产态 / production) 编排器 / orchestrator<br/>SemanticAuditor 编排器——9阶段管道统一调度.<br/>文件: semantic_audit/orchestrator.py"]
    src_zephyr_governance_semantic_audit_privacy_py["(生产态 / production) 审计轨迹·隐私模块 /<br/>privacy<br/>audit-trail.privacy — MOD-INF-020 · PII<br/>检测与脱敏<br/>文件: semantic_audit/privacy.py"]
    src_zephyr_governance_semantic_audit_semantic_cache_py["(生产态 / production) semantic缓存 / semantic_<br/>cache<br/>semantic缓存，审计的缓存，暂存常用数据加速访问。<br/>文件: semantic_audit/semantic_cache.py"]
    src_zephyr_governance_semantic_audit_spec_auditor_py["(生产态 / production) spec审计器 / spec_auditor<br/>G-CT-007 — Audit.record_agent_spec() 记录 Agent<br/>Spec 注册与变更.<br/>文件: semantic_audit/spec_auditor.py"]
    tests_governance_audit_test_error_pattern_id_column_py["(生产态 / production) 测试错误patternidcolumn /<br/>test_error_pattern_id_column<br/>测试错误patternidcolumn.error_pattern_id<br/>列幂等迁移单测（P4-1a）<br/>文件: audit/test_error_pattern_id_column.py"]
    tests_governance_audit_test_p3_integration_smoke_py["(生产态 / production) 测试p3集成smoke / test_p3_<br/>integration_smoke<br/>Phase 3 全链路集成 smoke test<br/>文件: audit/test_p3_integration_smoke.py"]
    tests_governance_audit_test_reconcile_async_py["(生产态 / production) 测试对账异步 / test_<br/>reconcile_async<br/>P2-3 reconciler 链路异步化测试<br/>文件: audit/test_reconcile_async.py"]
    tests_governance_audit_test_reconcile_worker_selfheal_py["(生产态 / production) 测试对账工作进程selfheal<br/>/ test_reconcile_worker_selfheal<br/>#ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 测试<br/>文件: audit/test_reconcile_worker_selfheal.py"]
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py["(生产态 / production)<br/>测试trae069thresholdsyncsmoke / test_trae_069_<br/>threshold_sync_smoke<br/>trae_069 YAML 真源→代码常量同步 smoke test<br/>文件: audit/test_trae_069_threshold_sync_<br/>smoke.py"]
    tests_governance_rule_bridge_test_session_worktree_async_reconcile_py["(生产态 / production) 测试会话worktree异步对账<br/>/ test_session_worktree_async_reconcile<br/>_run_reconcilers_after_merge 异步化测试。<br/>文件: rule_bridge/test_session_worktree_async_<br/>reconcile.py"]
    tests_governance_test_workspace_telemetry_shared_py["(生产态 / production) 测试工作区遥测共享 / test_<br/>workspace_telemetry_shared<br/>shared workspace_telemetry 公共 API 单测<br/>文件: governance/test_workspace_telemetry_<br/>shared.py"]
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
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py ~~~ src_zephyr_governance_audit_default_attribution_engine_py
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
    src_zephyr_gov_audit_anomaly_py["(生产态 / production) 异常 / anomaly<br/>异常签名枚举——治本（裁定#18 G3）：转为真 Enum<br/>对齐 test_audit_anomaly.py 契约。<br/>文件: gov_audit/anomaly.py"]
    src_zephyr_gov_audit_audit_admission_controller_py["(生产态 / production) 审计准入控制器 / audit_<br/>admission_controller<br/>审计准入控制器，审计的结果，封装操作结果的数据结<br/>构。<br/>文件: gov_audit/audit_admission_controller.py"]
    src_zephyr_gov_audit_bridge_py["(生产态 / production) 写入核心审计链——治本<br/>（裁定#18 G7 + 5.37.1） / bridge<br/>写入核心审计链——治本（裁定#18 G7 +<br/>5.37.1）：真实落盘 events.jsonl。<br/>文件: gov_audit/bridge.py"]
    src_zephyr_gov_audit_event_store_py["(生产态 / production) 事件存储 / event_store<br/>EventStore — Event Sourcing 事件追加与回放<br/>（DW-0002）<br/>文件: gov_audit/event_store.py"]
    src_zephyr_gov_audit_query_py["(生产态 / production) 旧版查询引擎<br/>（保留以兼容现有调用方）。 / query<br/>旧版查询引擎（保留以兼容现有调用方）。<br/>文件: gov_audit/query.py"]
    src_zephyr_gov_audit_resource_aware_pool_py["(生产态 / production) 资源感知池 / resource_<br/>aware_pool<br/>资源感知池，供audit_admission_controller; or使用<br/>文件: gov_audit/resource_aware_pool.py"]
    src_zephyr_gov_audit_text_to_finding_adapter_py["(生产态 / production) texttofinding适配器 /<br/>text_to_finding_adapter<br/>textto发现适配器，审计的解析器，把文本<br/>/数据解析成结构化对象。<br/>文件: gov_audit/text_to_finding_adapter.py"]
    src_zephyr_governance_audit_git_helpers_py["(生产态 / production) Git辅助 / _git_helpers<br/>审计 reconciler 共享 git 工具模块<br/>文件: audit/_git_helpers.py"]
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py["(生产态 / production)<br/>commitgatewayabuse监控器对账器 / commit_gateway_<br/>abuse_monitor_reconciler<br/>commit gateway 持续滥用监控<br/>（ARCH-TOOL-HEALTH-V1 Phase 5b，2026-07-19）。<br/>文件: audit/commit_gateway_abuse_monitor_<br/>reconciler.py"]
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py["(生产态 / production) 错误模式消费者协调器 /<br/>error_pattern_consumer_reconciler<br/>AI 行为遥测 JSONL 错误事件聚合 consumer。<br/>文件: audit/error_pattern_consumer_reconciler.py"]
    src_zephyr_governance_audit_reconcile_worker_py["(生产态 / production) 对账工作器 / reconcile_<br/>worker<br/>异步 reconciler worker<br/>（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）<br/>文件: audit/reconcile_worker.py"]
    src_zephyr_governance_audit_remediation_progress_reconciler_py["(生产态 / production) 修复进度对账器 /<br/>remediation_progress_reconciler<br/>治本进度持久化 + 新鲜度对账<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.1）。<br/>文件: audit/remediation_progress_reconciler.py"]
    src_zephyr_governance_audit_runtime_violation_snapshot_py["(生产态 / production) 运行时违规快照 / runtime_<br/>violation_snapshot<br/>trae_060 §5 evidence 运行时快照<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.4b）。<br/>文件: audit/runtime_violation_snapshot.py"]
    src_zephyr_governance_semantic_audit_alignment_engine_py["(生产态 / production) 对齐引擎 / alignment_<br/>engine<br/>三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs<br/>import 引用链。<br/>文件: semantic_audit/alignment_engine.py"]
    src_zephyr_governance_semantic_audit_fix_prioritizer_py["(生产态 / production) 修复prioritizer / fix_<br/>prioritizer<br/>按 severity -> certainty -> blast_radius<br/>三级排序,分组输出批次。<br/>文件: semantic_audit/fix_prioritizer.py"]
    src_zephyr_governance_semantic_audit_issue_aggregator_py["(生产态 / production)<br/>收集各阶段审计结果，去重合并排序输出。 / issue_<br/>aggregator<br/>收集各阶段审计结果，去重合并排序输出。<br/>文件: semantic_audit/issue_aggregator.py"]
    src_zephyr_governance_semantic_audit_kb_gate_py["(生产态 / production) 知识库门禁 / kb_gate<br/>知识库门禁.kb_gate — MOD-INF-020 · KB 审计门控<br/>文件: semantic_audit/kb_gate.py"]
    src_zephyr_governance_semantic_audit_llm_bridge_py["(生产态 / production) 接收 RED<br/>问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成 / llm_<br/>bridge<br/>接收 RED 问题,生成修复文本。LLM<br/>只润色不做判断。不可用时降级为模板生成。<br/>文件: semantic_audit/llm_bridge.py"]
    src_zephyr_governance_semantic_audit_safety_boundary_py["(生产态 / production) 安全boundary / safety_<br/>boundary<br/>禁碰规则过滤 + 置信度阈值。输入 TriggerResult<br/>列表,输出 SafetyDecision 分类。<br/>文件: semantic_audit/safety_boundary.py"]
    src_zephyr_governance_semantic_audit_self_healer_py["(生产态 / production) self愈合器 / self_healer<br/>Stage 7 自愈闭环 — 修复->自测->回滚.<br/>文件: semantic_audit/self_healer.py"]
    src_zephyr_governance_semantic_audit_self_health_py["(生产态 / production) 7 SLI + 5 容量 SLI +<br/>退化检测。定时自检,输出 HEALTHY/ / self_health<br/>7 SLI + 5 容量 SLI + 退化检测。定时自检,输出<br/>HEALTHY/DEGRADED/CRITICAL。<br/>文件: semantic_audit/self_health.py"]
    src_zephyr_governance_semantic_audit_trigger_engine_py["(生产态 / production)<br/>监听文件变更，判定是否触发语义审计。 / trigger_<br/>engine<br/>监听文件变更，判定是否触发语义审计。<br/>文件: semantic_audit/trigger_engine.py"]
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
    src_zephyr_gov_audit_delegation_bridge_py["(生产态 / production) delegation桥接 /<br/>delegation_bridge<br/>delegation桥接，主要提供报告delegationfailure、<br/>报告delegation超时、isavailable等功能，供audit-o<br/>rchestrator.delegation_使用<br/>文件: gov_audit/delegation_bridge.py"]
    src_zephyr_gov_audit_feedback_bridge_py["(生产态 / production) 反馈桥接 / feedback_bridge<br/>反馈桥接。Bridge between audit-trail anomaly<br/>findings and the Feedback Loop Engine.<br/>文件: gov_audit/feedback_bridge.py"]
    src_zephyr_gov_audit_finding_ingest_py["(生产态 / production) 发现ingest / finding_<br/>ingest<br/>发现ingest，审计的结果，封装操作结果的数据结构。<br/>文件: gov_audit/finding_ingest.py"]
    src_zephyr_gov_audit_indexer_py["(生产态 / production) 索引重建结果——治本<br/>（裁定#18 G5）：对齐 testa / indexer<br/>索引重建结果——治本（裁定#18 G5）：对齐 test_<br/>audit_indexer.py 契约。<br/>文件: gov_audit/indexer.py"]
    src_zephyr_gov_audit_merkle_hourly_py["(生产态 / production) audit-trail.merkle每小时<br/>/ merkle_hourly<br/>audit-trail.merkle每小时.merkle每小时· 每小时<br/>Merkle 聚合<br/>文件: gov_audit/merkle_hourly.py"]
    src_zephyr_gov_audit_models_py["(生产态 / production) 审计事件类型枚举——治本<br/>（裁定#18 G2）：转为真 Enu / models<br/>审计事件类型枚举——治本（裁定#18 G2）：转为真<br/>Enum，values 全部小写。<br/>文件: gov_audit/models.py"]
    src_zephyr_gov_audit_tiered_storage_bridge_py["(生产态 / production) tiered存储桥接 / tiered_<br/>storage_bridge<br/>tieredstorage桥接，主要提供find报告、migrate、st<br/>ats等功能，供audit-orchestrator.bridge; ret使用<br/>文件: gov_audit/tiered_storage_bridge.py"]
    src_zephyr_gov_audit_trust_bridge_py["(生产态 / production) 信任桥接 / trust_bridge<br/>信任桥接，主要提供评估、记录、获取趋势等功能，供<br/>audit-orchestrator.bridge; int使用<br/>文件: gov_audit/trust_bridge.py"]
    src_zephyr_governance_audit_health_score_calculator_py["(生产态 / production) 健康评分计算器 / health_<br/>score_calculator<br/>commit gateway 滥用 6 维加权健康度评分<br/>（P3-2，#ARCH-PREVENTABILITY-LAYER-001 Phase<br/>3）。<br/>文件: audit/health_score_calculator.py"]
    src_zephyr_governance_audit_reconcile_runner_py["(生产态 / production) 对账运行器 / reconcile_<br/>runner<br/>Reconciler 链路异步化<br/>（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）<br/>文件: audit/reconcile_runner.py"]
    src_zephyr_governance_semantic_audit_reference_extractor_py["(生产态 / production) AST 解析文件，提取 9<br/>个维度的引用信息。 / reference_extractor<br/>AST 解析文件，提取 9 个维度的引用信息。<br/>文件: semantic_audit/reference_extractor.py"]
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
    src_zephyr_gov_audit_contracts_py["(生产态 / production) 契约 / contracts<br/>核心审计链写入器——桥接 contracts 层到 writer<br/>实现。<br/>文件: gov_audit/contracts.py"]
    src_zephyr_gov_audit_finding_model_py["(生产态 / production) 发现模型 / finding_model<br/>发现模型，审计的模型，定义数据结构和字段。<br/>文件: gov_audit/finding_model.py"]
    src_zephyr_gov_audit_integrity_py["(生产态 / production) 完整性 / integrity<br/>完整性.integrity — MOD-INF-020 ·<br/>密码学完整性验证器<br/>文件: gov_audit/integrity.py"]
    src_zephyr_gov_audit_tiered_storage_py["(生产态 / production) 旧版分层存储<br/>（保留以兼容现有调用方）。 / tiered_storage<br/>旧版分层存储（保留以兼容现有调用方）。<br/>文件: gov_audit/tiered_storage.py"]
    src_zephyr_gov_audit_trust_engine_py["(生产态 / production) 信任评分调整记录<br/>（补全测试期望接口）。 / trust_engine<br/>信任评分调整记录（补全测试期望接口）。<br/>文件: gov_audit/trust_engine.py"]
    src_zephyr_gov_audit_writer_py["(生产态 / production) 不可变审计写入器——JSONL<br/>追加 + SHA-256 哈 / writer<br/>不可变审计写入器——JSONL 追加 + SHA-256 哈希链 +<br/>HMAC-SHA256 签名 + Lamport 时钟。<br/>文件: gov_audit/writer.py"]
    src_zephyr_governance_audit_reconciliation_registry_py["(生产态 / production) 对账注册表 /<br/>reconciliation_registry<br/>GitCommitGateway post-commit 漂移对账注册表<br/>文件: audit/reconciliation_registry.py"]
    src_zephyr_governance_semantic_audit_models_py["(生产态 / production) 语义审计管线数据模型 —<br/>MOD-INF-028 §4.2 / models<br/>语义审计管线数据模型 — MOD-INF-028 §4.2<br/>文件: semantic_audit/models.py"]
    src_zephyr_gov_audit_contracts_py ~~~ src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_model_py ~~~ src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_integrity_py ~~~ src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_tiered_storage_py ~~~ src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_trust_engine_py ~~~ src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_writer_py ~~~ src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconciliation_registry_py ~~~ src_zephyr_governance_semantic_audit_models_py
    src_zephyr_gov_audit_agent_signer_py["(生产态 / production) 代理signer / agent_signer<br/>代理signer.agent_signer — MOD-INF-020 · Agent<br/>Ed25519 签名器<br/>文件: gov_audit/agent_signer.py"]
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_blueprint_status_transition_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_error_pattern_consumer_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_ai_error_pattern_library_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_error_pattern_consumer_reconciler_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_health_score_calculator_py
    src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_git_helpers_py
    src_zephyr_governance_audit_git_performance_monitor_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconcile_runner_py
    src_zephyr_governance_audit_reconcile_worker_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_runtime_violation_snapshot_py
    src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_snapshot_manager_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_event_store_py
    src_zephyr_governance_audit_remediation_progress_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_reconcile_runner_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_workspace_hygiene_reconciler_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    src_zephyr_governance_audit_trail_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_governance_semantic_audit_fix_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_governance_semantic_audit_issue_aggregator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_alignment_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_fix_prioritizer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_issue_aggregator_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_alignment_engine_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_llm_bridge_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_safety_boundary_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_health_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_self_healer_py
    src_zephyr_governance_semantic_audit_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_trigger_engine_py
    src_zephyr_governance_semantic_audit_fix_result_prioritizer_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_llm_bridge_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_safety_boundary_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_reference_extractor_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_models_py
    src_zephyr_governance_semantic_audit_trigger_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_reference_extractor_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_audit_admission_controller_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_ingest_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_merkle_hourly_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_bridge_py
    src_zephyr_gov_audit_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_audit_write_failure_protector_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_compliance_map_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_governance_semantic_audit_kb_gate_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_audit_admission_controller_py
    src_zephyr_gov_audit_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_resource_aware_pool_py
    src_zephyr_gov_audit_delegation_auditor_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_audit_feedback_policy_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_feedback_bridge_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_finding_ingest_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_indexer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_agent_signer_py
    src_zephyr_gov_audit_integrity_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_merkle_hourly_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_merkle_audit_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_pipeline_runner_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_text_to_finding_adapter_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_query_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_tiered_storage_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_tiered_storage_py
    src_zephyr_gov_audit_text_to_finding_adapter_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_finding_model_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_bridge_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_indexer_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_orchestrator_compat_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_trust_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_trust_engine_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_contracts_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_integrity_py
    src_zephyr_gov_audit_writer_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_models_py
    src_zephyr_gov_audit_bridges_audit_drift_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_contracts_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_anomaly_py
    src_zephyr_gov_audit_bridges_audit_feedback_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_query_py
    src_zephyr_gov_audit_bridges_audit_delegation_bridge_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_delegation_bridge_py
    src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py -->|导入依赖 / import_depends| src_zephyr_gov_audit_writer_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_remediation_progress_reconciler_py
    scripts_governance_test_remediation_progress_smoke_py -->|导入依赖 / import_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_error_pattern_id_column_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_p3_integration_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_worker_selfheal_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py
    tests_governance_audit_test_trae_069_threshold_sync_smoke_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_health_score_calculator_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_worker_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconcile_runner_py
    tests_governance_audit_test_reconcile_async_py -->|测试依赖 / test_depends| src_zephyr_governance_audit_reconciliation_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_repair_audit_design_completeness_py,scripts_governance_repair_red_blue_test_py,scripts_governance_repair_rollback_depgraph_py,scripts_governance_test_remediation_progress_smoke_py,src_zephyr_gov_audit_orchestrator_compat_py,src_zephyr_gov_audit_action_history_py,src_zephyr_gov_audit_agent_signer_py,src_zephyr_gov_audit_anomaly_py,src_zephyr_gov_audit_api_lifecycle_py,src_zephyr_gov_audit_audit_admission_controller_py,src_zephyr_gov_audit_audit_schema_py,src_zephyr_gov_audit_audit_write_failure_protector_py,src_zephyr_gov_audit_bridge_py,src_zephyr_gov_audit_bridges_audit_anomaly_py,src_zephyr_gov_audit_bridges_audit_contracts_py,src_zephyr_gov_audit_bridges_audit_delegation_bridge_py,src_zephyr_gov_audit_bridges_audit_drift_bridge_py,src_zephyr_gov_audit_bridges_audit_feedback_bridge_py,src_zephyr_gov_audit_bridges_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_bridges_audit_trust_bridge_py,src_zephyr_gov_audit_changelog_manager_py,src_zephyr_gov_audit_cli_py,src_zephyr_gov_audit_code_archaeology_py,src_zephyr_gov_audit_cold_start_py,src_zephyr_gov_audit_compliance_map_py,src_zephyr_gov_audit_contracts_py,src_zephyr_gov_audit_corporate_actions_py,src_zephyr_gov_audit_delegation_auditor_py,src_zephyr_gov_audit_delegation_bridge_py,src_zephyr_gov_audit_dora_metrics_py,src_zephyr_gov_audit_event_store_py,src_zephyr_gov_audit_evidence_pack_py,src_zephyr_gov_audit_external_tool_audit_py,src_zephyr_gov_audit_feedback_bridge_py,src_zephyr_gov_audit_feedback_policy_py,src_zephyr_gov_audit_feedback_self_audit_py,src_zephyr_gov_audit_finding_ingest_py,src_zephyr_gov_audit_finding_model_py,src_zephyr_gov_audit_forensic_package_py,src_zephyr_gov_audit_genesis_py,src_zephyr_gov_audit_glossary_matrix_py,src_zephyr_gov_audit_incremental_review_py,src_zephyr_gov_audit_indexer_py,src_zephyr_gov_audit_integrity_py,src_zephyr_gov_audit_integrity_verifier_py,src_zephyr_gov_audit_kb_gate_py,src_zephyr_gov_audit_log_rotation_py,src_zephyr_gov_audit_merkle_audit_py,src_zephyr_gov_audit_merkle_hourly_py,src_zephyr_gov_audit_models_py,src_zephyr_gov_audit_observability_dashboard_py,src_zephyr_gov_audit_pipeline_runner_py,src_zephyr_gov_audit_privacy_py,src_zephyr_gov_audit_provenance_tracker_py,src_zephyr_gov_audit_query_py,src_zephyr_gov_audit_replay_engine_py,src_zephyr_gov_audit_resource_aware_pool_py,src_zephyr_gov_audit_retention_py,src_zephyr_gov_audit_sbom_generator_py,src_zephyr_gov_audit_spec_auditor_py,src_zephyr_gov_audit_supply_chain_py,src_zephyr_gov_audit_supply_chain_security_py,src_zephyr_gov_audit_text_to_finding_adapter_py,src_zephyr_gov_audit_tiered_storage_py,src_zephyr_gov_audit_tiered_storage_bridge_py,src_zephyr_gov_audit_trust_bridge_py,src_zephyr_gov_audit_trust_engine_py,src_zephyr_gov_audit_trust_ring_manager_py,src_zephyr_gov_audit_wqa_scorer_py,src_zephyr_gov_audit_writer_py,src_zephyr_gov_enforcement_behavioral_admission_ai_code_standards_py,src_zephyr_gov_enforcement_behavioral_admission_mcp_result_push_py,src_zephyr_gov_enforcement_behavioral_admission_post_process_py,src_zephyr_gov_enforcement_behavioral_admission_vibe_coding_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_audit_chain_verifier_py,src_zephyr_gov_enforcement_rule_enforcement_sys_master_compliance_py,src_zephyr_governance_audit_trail_contracts_py,src_zephyr_governance_audit_git_helpers_py,src_zephyr_governance_audit_ai_error_pattern_library_py,src_zephyr_governance_audit_blueprint_status_transition_reconciler_py,src_zephyr_governance_audit_commit_gateway_abuse_monitor_reconciler_py,src_zephyr_governance_audit_cross_layer_contract_signature_reconciler_py,src_zephyr_governance_audit_default_attribution_engine_py,src_zephyr_governance_audit_default_tca_engine_py,src_zephyr_governance_audit_error_pattern_consumer_reconciler_py,src_zephyr_governance_audit_git_performance_monitor_reconciler_py,src_zephyr_governance_audit_health_score_calculator_py,src_zephyr_governance_audit_reconcile_runner_py,src_zephyr_governance_audit_reconcile_worker_py,src_zephyr_governance_audit_reconciliation_registry_py,src_zephyr_governance_audit_remediation_progress_reconciler_py,src_zephyr_governance_audit_runtime_violation_snapshot_py,src_zephyr_governance_audit_runtime_violation_snapshot_reconciler_py,src_zephyr_governance_audit_snapshot_manager_py,src_zephyr_governance_audit_workspace_hygiene_reconciler_py,src_zephyr_governance_financial_governance_financial_compliance_py,src_zephyr_governance_semantic_audit_alignment_engine_py,src_zephyr_governance_semantic_audit_compliance_map_py,src_zephyr_governance_semantic_audit_feedback_self_audit_py,src_zephyr_governance_semantic_audit_fix_prioritizer_py,src_zephyr_governance_semantic_audit_fix_result_prioritizer_py,src_zephyr_governance_semantic_audit_issue_aggregator_py,src_zephyr_governance_semantic_audit_kb_gate_py,src_zephyr_governance_semantic_audit_llm_bridge_py,src_zephyr_governance_semantic_audit_models_py,src_zephyr_governance_semantic_audit_orchestrator_py,src_zephyr_governance_semantic_audit_privacy_py,src_zephyr_governance_semantic_audit_reference_extractor_py,src_zephyr_governance_semantic_audit_safety_boundary_py,src_zephyr_governance_semantic_audit_self_healer_py,src_zephyr_governance_semantic_audit_self_health_py,src_zephyr_governance_semantic_audit_semantic_cache_py,src_zephyr_governance_semantic_audit_spec_auditor_py,src_zephyr_governance_semantic_audit_trigger_engine_py,tests_governance_audit_test_error_pattern_id_column_py,tests_governance_audit_test_p3_integration_smoke_py,tests_governance_audit_test_reconcile_async_py,tests_governance_audit_test_reconcile_worker_selfheal_py,tests_governance_audit_test_trae_069_threshold_sync_smoke_py,tests_governance_rule_bridge_test_session_worktree_async_reconcile_py,tests_governance_test_workspace_telemetry_shared_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图（blueprint.md）<br/>文件: audit_orchestrator/blueprint.md<br/>⛔ 该域，设计已就绪，等待开发排期"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) 蓝图 / blueprint<br/>蓝图（blueprint.md）<br/>文件: audit_trail/blueprint.md<br/>⛔ 该域，设计已就绪，等待开发排期"]
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
| 1 | 反馈桥接 / feedback_bridge (gov_audit/feedback_bridge.py) | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 2 | 审计模式 / audit_schema (gov_audit/audit_schema.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 3 | 审计信任桥接 / audit_trust_bridge (bridges/audit_trust_br... | → | D_GOVERNANCE 生命周期管理: continuous信任 / continuous_trust (intelligence_governanc... | 导入依赖 / import_depends |
| 4 | 事件存储 / event_store (gov_audit/event_store.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 5 | 证据包 / evidence_pack (gov_audit/evidence_pack.py) | → | D_GOVERNANCE 生命周期管理: 证据包 / evidence_pack (governance/evidence_pack.py) | 导入依赖 / import_depends |
| 6 | 知识库门禁 / kb_gate (gov_audit/kb_gate.py) | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 7 | 审计轨迹·隐私模块 / privacy (gov_audit/privacy.py) | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 8 | spec审计器 / spec_auditor (gov_audit/spec_auditor.py) | → | D_GOVERNANCE 生命周期管理: 注册表 / registry (agent_spec/registry.py) | 导入依赖 / import_depends |
| 9 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 10 | 快照管理器 / snapshot_manager (audit/snapshot_manager.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 11 | 知识库门禁 / kb_gate (semantic_audit/kb_gate.py) | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 12 | 审计轨迹·隐私模块 / privacy (semantic_audit/privacy.py) | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 13 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookup绕过策略 / capability_lookup_bypass_polic... | 导入依赖 / import_depends |
| 14 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 导入依赖 / import_depends |
| 15 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_CODE_QUALITY 代码质量治理: 脚本导入完整性门禁 / scripts_import_integrity_gate (commi... | 导入依赖 / import_depends |
| 16 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_CODE_QUALITY 代码质量治理: undefinedname门禁 / undefined_name_gate (commit_gates/und... | 导入依赖 / import_depends |
| 17 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_CODE_QUALITY 代码质量治理: 门禁自动registrar / gate_auto_registrar (rule_bridge/gate... | 导入依赖 / import_depends |
| 18 | 编排器兼容 / _orchestrator_compat (gov_audit/_orchestrato... | → | D_GOV_DRIFT 漂移检测: 自监控 / self_monitor (gov_audit/self_monitor.py) | 导入依赖 / import_depends |
| 19 | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | → | D_GOV_DRIFT 漂移检测: 漂移桥接 / drift_bridge (gov_audit/drift_bridge.py) | 导入依赖 / import_depends |
| 20 | 审计漂移桥接 / audit_drift_bridge (bridges/audit_drift_br... | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 21 | 审计漂移桥接 / audit_drift_bridge (bridges/audit_drift_br... | → | D_GOV_DRIFT 漂移检测: 漂移模型 / drift_models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 22 | 命令行 / cli (gov_audit/cli.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 23 | 命令行 / cli (gov_audit/cli.py) | → | D_GOV_DRIFT 漂移检测: 完整性 / integrity (governance/integrity.py) | 导入依赖 / import_depends |
| 24 | Git绩效监控协调器 / git_performance_monitor_reconciler (a... | → | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | 导入依赖 / import_depends |
| 25 | 对账工作器 / reconcile_worker (audit/reconcile_worker.py) | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 导入依赖 / import_depends |
| 26 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 27 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | 导入依赖 / import_depends |
| 28 | 测试对账异步 / test_reconcile_async (audit/test_reconcile... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 29 | 测试对账工作进程selfheal / test_reconcile_worker_selfheal... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 30 | 测试会话worktree异步对账 / test_session_worktree_async_re... | → | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | 测试依赖 / test_depends |
| 31 | delegation桥接 / delegation_bridge (gov_audit/delegation_... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine — MOD-INF-022 (escalation/e... | 导入依赖 / import_depends |
| 32 | 管线运行器 / pipeline_runner (gov_audit/pipeline_runner.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | 导入依赖 / import_depends |
| 33 | 审计链验证器 / audit_chain_verifier (rule_enforcement/aud... | → | D_GOV_RULE 规则治理: 门禁上下文传播 / Gate Context (gate_engine/gate_context.py) | 导入依赖 / import_depends |
| 34 | commitgatewayabuse监控器对账器 / commit_gateway_abuse_mon... | → | D_GOV_RULE 规则治理: 自适应阈值 / Adaptive Threshold (rule_enforcement/adaptiv... | 导入依赖 / import_depends |
| 35 | 测试p3集成smoke / test_p3_integration_smoke (audit/test_p... | → | D_GOV_RULE 规则治理: 自适应阈值 / Adaptive Threshold (rule_enforcement/adaptiv... | 测试依赖 / test_depends |
| 36 | 审计designcompleteness / audit_design_completeness (repai... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 37 | [INVARIANTS] 20项红蓝对抗测试 / red_blue_test (repair/red... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 38 | 回滚依赖图 / rollback_depgraph (repair/rollback_depgraph.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 39 | 测试修复进度smoke / test_remediation_progress_smoke (gove... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 40 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_SCRIPTS 脚本治理: 校验模块idnaming / validate_module_id_naming (d3_metadata... | 导入依赖 / import_depends |
| 41 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_GOV_SCRIPTS 脚本治理: check门禁inventory漂移 / check_gate_inventory_drift (gene... | 导入依赖 / import_depends |
| 42 | 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | → | D_INFRA_RUNTIME 运行时集成: Git批处理 / git_batcher (infrastructure/git_batcher.py) | 导入依赖 / import_depends |
| 43 | 默认attribution引擎 / Re-export wrapper: default_attribut... | → | D_REPORTING 报告: 默认attribution引擎 / D_REPORTING — Default Attribution ... | 导入依赖 / import_depends |
| 44 | 默认tca引擎 / Re-export wrapper: default_tca_engine canon... | → | D_REPORTING 报告: 默认tca引擎 / D_REPORTING — Default TCA Engine (reportin... | 导入依赖 / import_depends |
| 45 | 命令行 / cli (gov_audit/cli.py) | → | D_SECURITY 对抗验证: 判定 / judge (orphan_judge/judge.py) | 导入依赖 / import_depends |
| 46 | 命令行 / cli (gov_audit/cli.py) | → | D_SECURITY 对抗验证: 校验器 / validator (adversarial_validation/validator.py) | 导入依赖 / import_depends |
| 47 | 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 48 | 对账工作器 / reconcile_worker (audit/reconcile_worker.py) | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 49 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 50 | [INVARIANTS] 20项红蓝对抗测试 / red_blue_test (repair/red... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 51 | 回滚依赖图 / rollback_depgraph (repair/rollback_depgraph.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 52 | 代理signer / agent_signer (gov_audit/agent_signer.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 53 | 审计模式 / audit_schema (gov_audit/audit_schema.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 54 | 审计模式 / audit_schema (gov_audit/audit_schema.py) | → | D_SHARED 共享服务: sqlite工厂 / sqlite_factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 55 | 审计漂移桥接 / audit_drift_bridge (bridges/audit_drift_br... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 56 | 命令行 / cli (gov_audit/cli.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 57 | 命令行 / cli (gov_audit/cli.py) | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 58 | 冷启动 / cold_start (gov_audit/cold_start.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 59 | 冷启动 / cold_start (gov_audit/cold_start.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 60 | 事件存储 / event_store (gov_audit/event_store.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 61 | 证据包 / evidence_pack (gov_audit/evidence_pack.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 62 | externaltool审计 / external_tool_audit (gov_audit/externa... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 63 | 反馈桥接 / feedback_bridge (gov_audit/feedback_bridge.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 64 | 发现ingest / finding_ingest (gov_audit/finding_ingest.py) | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 65 | 发现模型 / finding_model (gov_audit/finding_model.py) | → | D_SHARED 共享服务: 基类配置 / base_config (schema/base_config.py) | 导入依赖 / import_depends |
| 66 | 取证包 / forensic_package (gov_audit/forensic_package.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 67 | 索引重建结果——治本（裁定#18 G5）：对齐 testa / indexer ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 68 | 索引重建结果——治本（裁定#18 G5）：对齐 testa / indexer ... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 69 | 完整性 / integrity (gov_audit/integrity.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 70 | 完整性 / integrity (gov_audit/integrity.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 71 | 日志rotation / log_rotation (gov_audit/log_rotation.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 72 | audit-trail.merkle每小时 / merkle_hourly (gov_audit/merkl... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 73 | 管线运行器 / pipeline_runner (gov_audit/pipeline_runner.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 74 | 管线运行器 / pipeline_runner (gov_audit/pipeline_runner.py) | → | D_SHARED 共享服务: 基类配置 / base_config (schema/base_config.py) | 导入依赖 / import_depends |
| 75 | 旧版查询引擎（保留以兼容现有调用方）。 / query (gov_audit... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 76 | 保留策略（补全测试期望接口）。 / retention (gov_audit/ret... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 77 | supply链 / supply_chain (gov_audit/supply_chain.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 78 | texttofinding适配器 / text_to_finding_adapter (gov_audit/... | → | D_SHARED 共享服务: 基类配置 / base_config (schema/base_config.py) | 导入依赖 / import_depends |
| 79 | 旧版分层存储（保留以兼容现有调用方）。 / tiered_storage (... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 80 | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 81 | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | → | D_SHARED 共享服务: 会话审计 / session_audit (session/session_audit.py) | 导入依赖 / import_depends |
| 82 | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 83 | MCP结果推送 / mcp_result_push (behavioral_admission/mcp_r... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 84 | 提交进程 / post_process (behavioral_admission/post_proces... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 85 | 审计链验证器 / audit_chain_verifier (rule_enforcement/aud... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 86 | sys主合规 / SYS-MASTER-001 Compliance Checker (rule_enfor... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 87 | sys主合规 / SYS-MASTER-001 Compliance Checker (rule_enfor... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 88 | Git辅助 / _git_helpers (audit/_git_helpers.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 89 | 蓝图状态转换协调器 / blueprint_status_transition_reconcil... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 90 | commitgatewayabuse监控器对账器 / commit_gateway_abuse_mon... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 91 | 跨layercontractsignature对账器 / cross_layer_contract_sig... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 92 | Git绩效监控协调器 / git_performance_monitor_reconciler (a... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 93 | 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 94 | 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 95 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 96 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 97 | 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 98 | 修复进度对账器 / remediation_progress_reconciler (audit/r... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 99 | 运行时违规快照 / runtime_violation_snapshot (audit/runtim... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 100 | 快照管理器 / snapshot_manager (audit/snapshot_manager.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 101 | 快照管理器 / snapshot_manager (audit/snapshot_manager.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 102 | 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 103 | 收集各阶段审计结果，去重合并排序输出。 / issue_aggregator... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 104 | self愈合器 / self_healer (semantic_audit/self_healer.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 105 | self愈合器 / self_healer (semantic_audit/self_healer.py) | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 106 | 测试工作区遥测共享 / test_workspace_telemetry_shared (gov... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 测试依赖 / test_depends |
| 107 | 测试工作区遥测共享 / test_workspace_telemetry_shared (gov... | → | D_SHARED 共享服务: 工作区遥测 / workspace_telemetry (io/workspace_telemetry.py) | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: 技能执行器 / skill_executor (skills/skill_executor.py) | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_CORE 自治核心: 技能沙箱 / MOD-INF-019: Agent Spec — Skill Sandbox (skil... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_CORE 自治核心: spec引擎 / spec_engine (autonomy_core/spec_engine.py) | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 4 | D_FBL_VERIFICATION 反馈验证: 安全门禁l66l67 / Safety Gates L66-L67 — Financial Pruden... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: Git提交 / git_commit (scripts/git_commit.py) | → | 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: projection引擎 / projection_engine (observability_governa... | → | 事件存储 / event_store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: 数据库管理器 / database_manager (persistence/database_man... | → | 审计模式 / audit_schema (gov_audit/audit_schema.py) | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: 治理服务端 / governance_server (mcp/governance_server.py) | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 9 | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 10 | D_GOV_CODE_QUALITY 代码质量治理: 协调器健康门禁 / reconciler_health_gate (commit_gates/rec... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 11 | D_GOV_DRIFT 漂移检测: 漂移桥接 / drift_bridge (gov_audit/drift_bridge.py) | → | 异常 / anomaly (gov_audit/anomaly.py) | 导入依赖 / import_depends |
| 12 | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | → | 发现ingest / finding_ingest (gov_audit/finding_ingest.py) | 导入依赖 / import_depends |
| 13 | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | → | 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 14 | D_GOV_DRIFT 漂移检测: truth数据源校验器 / truth_source_validator (rule_enforcem... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 15 | D_GOV_DRIFT 漂移检测: 完整性 / integrity (governance/integrity.py) | → | audit-trail.merkle每小时 / merkle_hourly (gov_audit/merkl... | 导入依赖 / import_depends |
| 16 | D_GOV_DRIFT 漂移检测: 完整性 / integrity (governance/integrity.py) | → | 审计事件类型枚举——治本（裁定#18 G2）：转为真 Enu / mode... | 导入依赖 / import_depends |
| 17 | D_GOV_DRIFT 漂移检测: 完整性 / integrity (governance/integrity.py) | → | 信任桥接 / trust_bridge (gov_audit/trust_bridge.py) | 导入依赖 / import_depends |
| 18 | D_GOV_ENFORCEMENT 规则执行: 指标数量漂移协调器 / metric_count_drift_reconciler (d8_do... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 19 | D_GOV_ENFORCEMENT 规则执行: readme版本sync对账器 / readme_version_sync_reconciler (d8... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 20 | D_GOV_ENFORCEMENT 规则执行: requirements版本sync对账器 / requirements_version_sync_re... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 21 | D_GOV_ENFORCEMENT 规则执行: 包入口 / __init__ (behavioral_admission/__init__.py) | → | MCP结果推送 / mcp_result_push (behavioral_admission/mcp_r... | 导入依赖 / import_depends |
| 22 | D_GOV_ENFORCEMENT 规则执行: 包入口 / __init__ (behavioral_admission/__init__.py) | → | 提交进程 / post_process (behavioral_admission/post_proces... | 导入依赖 / import_depends |
| 23 | D_GOV_ENFORCEMENT 规则执行: 包入口 / __init__ (behavioral_admission/__init__.py) | → | vibecoding执行器 / vibe_coding_enforcer (behavioral_admis... | 导入依赖 / import_depends |
| 24 | D_GOV_ENFORCEMENT 规则执行: 门禁事件适配器 / gate_event_adapter (behavioral_admission... | → | 事件存储 / event_store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 25 | D_GOV_ENFORCEMENT 规则执行: 裁定引擎 / verdict_engine (behavioral_admission/verdict_e... | → | 审计事件类型枚举——治本（裁定#18 G2）：转为真 Enu / mode... | 导入依赖 / import_depends |
| 26 | D_GOV_ENFORCEMENT 规则执行: 紧急提交 / emergency_commit (rule_bridge/emergency_commit... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 27 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 蓝图状态转换协调器 / blueprint_status_transition_reconcil... | 导入依赖 / import_depends |
| 28 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | commitgatewayabuse监控器对账器 / commit_gateway_abuse_mon... | 导入依赖 / import_depends |
| 29 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 跨layercontractsignature对账器 / cross_layer_contract_sig... | 导入依赖 / import_depends |
| 30 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 错误模式消费者协调器 / error_pattern_consumer_reconciler ... | 导入依赖 / import_depends |
| 31 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | Git绩效监控协调器 / git_performance_monitor_reconciler (a... | 导入依赖 / import_depends |
| 32 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 33 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 34 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 修复进度对账器 / remediation_progress_reconciler (audit/r... | 导入依赖 / import_depends |
| 35 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 运行时违规快照协调器 / runtime_violation_snapshot_reconci... | 导入依赖 / import_depends |
| 36 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 37 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | AI错误模式库 / ai_error_pattern_library (audit/ai_error_p... | 导入依赖 / import_depends |
| 38 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 39 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 40 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 41 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 完整性 / integrity (gov_audit/integrity.py) | 导入依赖 / import_depends |
| 42 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 旧版查询引擎（保留以兼容现有调用方）。 / query (gov_audit... | 导入依赖 / import_depends |
| 43 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 44 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | sys主合规 / SYS-MASTER-001 Compliance Checker (rule_enfor... | 导入依赖 / import_depends |
| 45 | D_GOV_OPS_RESILIENCE 运维弹性治理: 爆炸半径 / blast_radius — MOD-INF-028 §3.1 Stage 9 (res... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 / models (seman... | 导入依赖 / import_depends |
| 46 | D_GOV_OPS_RESILIENCE 运维弹性治理: tamperevident日志 / tamper_evident_log (security_governan... | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 47 | D_GOV_RULE 规则治理: 能力检查器 / Capability Checker (rule_enforcement/capabil... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 48 | D_GOV_RULE 规则治理: 门禁紧急旁路 / Gate Override (gate_engine/gate_override.py) | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 49 | D_GOV_SCRIPTS 脚本治理: 对抗sys主测试 / Red/Blue Team Adversarial Test v3: SYS-MA... | → | sys主合规 / SYS-MASTER-001 Compliance Checker (rule_enfor... | 导入依赖 / import_depends |
| 50 | D_GOV_SCRIPTS 脚本治理: rebuild审计索引 / rebuild_audit_index (prototype/rebuild_... | → | 索引重建结果——治本（裁定#18 G5）：对齐 testa / indexer ... | 导入依赖 / import_depends |
| 51 | D_GOV_SCRIPTS 脚本治理: 架构健康仪表盘 / architecture_health_dashboard (governanc... | → | 运行时违规快照 / runtime_violation_snapshot (audit/runtim... | 导入依赖 / import_depends |
| 52 | D_GOV_SCRIPTS 脚本治理: 会话启动健康检查 / session_startup_health_check (governan... | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 53 | D_INFRASTRUCTURE 跨层契约基础设施: 备份协调器 / backup_reconciler (backup/backup_reconciler.py) | → | 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 54 | D_INFRA_RECOVERY 回滚恢复: 审计器 / auditor (rollback/auditor.py) | → | 契约 / contracts (gov_audit/contracts.py) | 导入依赖 / import_depends |
| 55 | D_INFRA_RECOVERY 回滚恢复: 回滚abuse检测器 / rollback_abuse_detector (rollback/rollb... | → | 旧版查询引擎（保留以兼容现有调用方）。 / query (gov_audit... | 导入依赖 / import_depends |
| 56 | D_INFRA_RECOVERY 回滚恢复: 回滚审计nexus / rollback_audit_nexus (rollback/rollback_a... | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 57 | D_INFRA_RECOVERY 回滚恢复: 回滚执行器 / rollback_executor (rollback/rollback_executo... | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 58 | D_INFRA_RUNTIME 运行时集成: 生命周期 / lifecycle (asset_inventory/lifecycle.py) | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 59 | D_INFRA_RUNTIME 运行时集成: 引擎 / engine (auto_fix_engine/engine.py) | → | 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 60 | D_INFRA_RUNTIME 运行时集成: 资源优化 / resource_optimization.py - MAPE-K autonomic re... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 61 | D_INTEGRATION 管线路由: 接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时... | → | 语义审计管线数据模型 — MOD-INF-028 §4.2 / models (seman... | 导入依赖 / import_depends |
| 62 | D_INTEGRATION 管线路由: 审计日志器 / audit_logger (mcp/audit_logger.py) | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 63 | D_INTEGRATION 管线路由: 管线编排器 / pipeline_orchestrator (integration/pipeline_... | → | 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 64 | D_SECURITY 对抗验证: 契约 / contracts (access_control/contracts.py) | → | 契约 / contracts (gov_audit/contracts.py) | 导入依赖 / import_depends |
| 65 | D_SECURITY 对抗验证: 判定 / judge (orphan_judge/judge.py) | → | 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 66 | D_SECURITY 对抗验证: 防御运行器 / defense_runner (adversarial_validation/defen... | → | 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 67 | D_SECURITY 对抗验证: 行为审计日志器 / behavior_audit_logger (llm_security/beha... | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 68 | D_SECURITY 对抗验证: LSG 自身隔离策略. / isolation (self_protection/isolation.py) | → | 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 69 | D_TRADING 交易运营: 裁定引擎 / verdict_engine (trading/verdict_engine.py) | → | 审计事件类型枚举——治本（裁定#18 G2）：转为真 Enu / mode... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 18 个外部域直接连接（出边 107 条 + 入边 69 条 = 176 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
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
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_AUDIT -->|5条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_AUDIT -->|5条 导入依赖 / import_depends| D_SECURITY
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_RULE
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_REPORTING
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOV_ENFORCEMENT -->|23条 导入依赖 / import_depends| D_GOV_AUDIT
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
