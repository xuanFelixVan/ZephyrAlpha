---
doc_type: architecture_view
title: D_GOV_ENFORCEMENT 规则执行架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 53_d_gov_enforcement / 规则执行域 / Rule Enforcement

> **功能简介 / Overview**: 规则执行，负责治理规则执行和门禁拦截

> **文档作用 / Purpose**: 展示 规则执行（D_GOV_ENFORCEMENT）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/53_d_gov_enforcement.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 53 | Number | 53 |
| 域ID | D_GOV_ENFORCEMENT | Domain ID | D_GOV_ENFORCEMENT |
| 域名称 | 规则执行 | Domain Name | Rule Enforcement |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 120 | Module Count | 120 |
| 域内依赖 | 101 | Internal Dependencies | 101 |
| 跨域入边 | 128 | Cross-domain Incoming | 128 |
| 跨域出边 | 158 | Cross-domain Outgoing | 158 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 118 | Production Modules | 118 |
| 容量 | 118/150 (正常) | Capacity | 118/150 (正常) |
| 描述 | 门禁引擎流程编排(GatePipeline/GateEngine) | Description | 门禁引擎流程编排(GatePipeline/GateEngine) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 120 个模块（生产态 118 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml["catalogs/rule_enforcement_registry<br/>catalogs包的rule_enforcement_registry模块<br/>文件: catalogs/rule_enforcement_registry.yaml<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["d8_doc_sync/metric_count_drift_reconciler<br/>metric_count_drift_reconciler.py — dashboard<br/>指标数描述派生校验 reconciler<br/>文件: d8_doc_sync<br/>/metric_count_drift_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["d8_doc_sync/readme_version_sync_reconciler<br/>readme_version_sync_reconciler.py — README<br/>版本号派生展示校验 reconciler<br/>文件: d8_doc_sync<br/>/readme_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["d8_doc_sync/requirements_version_sync_reconciler<br/>requirements_version_sync_reconciler.py —<br/>requirements.txt ↔ pyproject.toml...<br/>文件: d8_doc_sync<br/>/requirements_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_session_worktree_cli_py["governance/session_worktree_cli<br/>session_worktree_cli.py — session worktree 管理<br/>CLI（治本遗留项#2，2026-07-17）<br/>文件: governance/session_worktree_cli.py<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py["影子金丝雀部署运行器<br/>把 4 个已有零件串成一条命令，做灰度发布的安全网<br/>：先检查能不能上线，再开个影子进程跑同样的输入但<br/>不接真券商，然后比对两边输出是否一致，分歧小就放<br/>行、分歧大就回滚。专门满足 EX-021 那半 CI/CD<br/>灰度门禁。<br/>Shadow Canary Deploy Runner<br/>Shadow Canary deploy runner orchestrating<br/>precheck/shadow/compare/state-machine,<br/>satisfying EX-021 CI/CD gate half<br/>文件: ops/shadow_canary_deploy.py<br/>(设计态 / design)"]
    src_zephyr_gov_enforcement_init_py["zephyr/gov_enforcement 包入口<br/>gov_enforcement package — 执行治理域<br/>（D_GOV_ENFORCEMENT）<br/>文件: gov_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["gov_enforcement/behavioral_admission 包入口<br/>管理gov_enforcement.behavioral_admission子包的加<br/>载和懒导入<br/>文件: behavioral_admission/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["commit_gates/stash_accumulation_gate<br/>stash_accumulation_gate.py — stash<br/>堆积阈值检测门禁（STASH-ACCUMULATION）<br/>文件: commit_gates/stash_accumulation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py["重置网关<br/>统一拦截 git reset/restore/checkout--<br/>危险命令的治理入口，三段式防护：自伤检测→锁冲突<br/>检测→审计落盘，对标 GitCommitGateway 对 commit<br/>的治理<br/>文件: rule_bridge/reset_gateway.py<br/>(设计态 / design)"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["rule_enforcement/approval<br/>G-CT-004 — Backward-compat re-export of<br/>ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["rule_enforcement/compliance_rule<br/>rule enforcement包的compliance_rule模块<br/>文件: rule_enforcement/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["rule_enforcement/default_quality_gate<br/>D_DATA — Default Data Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["rule_enforcement/dlq_retry_policy<br/>DLQ 重试策略 — 对接 shared/events<br/>/dlq.DeadLetterQueue 的真重试。<br/>文件: rule_enforcement/dlq_retry_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["rule_enforcement/output_quality_gate<br/>rule enforcement包的output_quality_gate模块<br/>文件: rule_enforcement/output_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["rule_enforcement/pre_flight_gate<br/>rule enforcement包的pre_flight_gate模块<br/>文件: rule_enforcement/pre_flight_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["rule_engine/rule_canary_manager<br/>Rule Canary Manager — v0.10.0 规则金丝雀:<br/>1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["rule_engine/rule_debt_auditor<br/>Rule Debt Auditor — v0.7.0 规则债务审计器:<br/>分析escalation_rules.yaml维护债务...<br/>文件: rule_engine/rule_debt_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["rule_engine/rule_shadow_runner<br/>Rule Shadow Runner — v0.10.0 规则影子模式:<br/>新规则shadow运行3天->diff old vs ...<br/>文件: rule_engine/rule_shadow_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["rule_engine/rule_watcher<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>文件: rule_engine/rule_watcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["rule_enforcement/slo_contract<br/>SLO-Driven Escalation Contract — D-022-12.<br/>文件: rule_enforcement/slo_contract.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_arch_reference_gate_py["commit_gates/test_arch_reference_gate<br/>test_arch_reference_gate.py — #ARCH-NNN<br/>悬空引用检测门禁单测（ARCH-REFERENCE）<br/>文件: commit_gates/test_arch_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py["commit_gates/test_asyncio_run_in_context_gate<br/>test_asyncio_run_in_context_gate.py — asyncio<br/>API 误用硬阻断门禁单测（ASYNCI...<br/>文件: commit_gates<br/>/test_asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_getenv_gate_py["commit_gates/test_bare_getenv_gate<br/>test_bare_getenv_gate.py — NO-BARE-GETENV<br/>门禁单测<br/>文件: commit_gates/test_bare_getenv_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_sql_gate_py["commit_gates/test_bare_sql_gate<br/>test_bare_sql_gate.py — NO-BARE-SQL 门禁单测<br/>文件: commit_gates/test_bare_sql_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_subprocess_gate_py["commit_gates/test_bare_subprocess_gate<br/>test_bare_subprocess_gate.py — BARE-SUBPROCESS<br/>门禁单测<br/>文件: commit_gates/test_bare_subprocess_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py["commit_gates<br/>/test_blueprint_amodule_consistency_gate<br/>test_blueprint_amodule_consistency_gate.py —<br/>BLUEPRINT-AMODULE-CONSISTENCY ...<br/>文件: commit_gates<br/>/test_blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py["commit_gates<br/>/test_blueprint_amodule_cross_check_gate<br/>test_blueprint_amodule_cross_check_gate.py —<br/>BLUEPRINT-AMODULE-CROSS-CHECK ...<br/>文件: commit_gates<br/>/test_blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_audit_log_py["commit_gates/test_capability_lookup_audit_log<br/>test_capability_lookup_audit_log.py —<br/>capability_lookup audit log 落盘 e2e s...<br/>文件: commit_gates<br/>/test_capability_lookup_audit_log.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py["commit_gates<br/>/test_capability_lookup_bypass_policy<br/>test_capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享...<br/>文件: commit_gates<br/>/test_capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_required_gate_py["commit_gates<br/>/test_capability_lookup_required_gate<br/>test_capability_lookup_required_gate.py —<br/>CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>文件: commit_gates<br/>/test_capability_lookup_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_overlap_gate_py["commit_gates/test_capability_overlap_gate<br/>test_capability_overlap_gate.py —<br/>CAPABILITY-OVERLAP 门禁单测<br/>文件: commit_gates<br/>/test_capability_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_batch_size_gate_py["commit_gates/test_ch_batch_size_gate<br/>test_ch_batch_size_gate.py — CH-BATCH-SIZE<br/>门禁单测<br/>文件: commit_gates/test_ch_batch_size_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_version_col_gate_py["commit_gates/test_ch_version_col_gate<br/>test_ch_version_col_gate.py — CH-VERSION-COL<br/>门禁单测<br/>文件: commit_gates/test_ch_version_col_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_claim_required_gate_py["commit_gates/test_claim_required_gate<br/>test_claim_required_gate.py — claim_files<br/>前置检查门禁单测（CLAIM-REQUIRED，...<br/>文件: commit_gates/test_claim_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_consumers_accuracy_gate_py["commit_gates/test_consumers_accuracy_gate<br/>test_consumers_accuracy_gate.py —<br/>CONSUMERS-ACCURACY 门禁单测（...<br/>文件: commit_gates<br/>/test_consumers_accuracy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_create_guard_py["commit_gates/test_create_guard<br/>test_create_guard.py — CREATE-GUARD<br/>门禁单元测试（2026-06-30 治本补全）<br/>文件: commit_gates/test_create_guard.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_dangling_reference_gate_py["commit_gates/test_dangling_reference_gate<br/>test_dangling_reference_gate.py — AGENTS.md<br/>§X.Y 悬空引用检测门禁单测（DANG...<br/>文件: commit_gates<br/>/test_dangling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py["commit_gates/test_datetime_now_forbidden_gate<br/>test_datetime_now_forbidden_gate.py —<br/>生成器代码 datetime.now() 硬阻断门禁单...<br/>文件: commit_gates<br/>/test_datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_freshness_gate_py["commit_gates/test_depgraph_freshness_gate<br/>test_depgraph_freshness_gate.py —<br/>DEPGRAPH-FRESHNESS 门禁单测<br/>文件: commit_gates<br/>/test_depgraph_freshness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py["commit_gates/test_depgraph_pre_registration_gate<br/>test_depgraph_pre_registration_gate.py —<br/>DEPGRAPH-PRE-REGISTRATION gate 测试<br/>文件: commit_gates<br/>/test_depgraph_pre_registration_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_derived_file_deletion_gate_py["commit_gates/test_derived_file_deletion_gate<br/>test_derived_file_deletion_gate.py —<br/>派生文件删除保护门禁单测（DERIVED-FILE-...<br/>文件: commit_gates<br/>/test_derived_file_deletion_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_diff_helpers_py["commit_gates/test_diff_helpers<br/>test_diff_helpers.py — gate 共享 diff<br/>解析工具模块单测<br/>文件: commit_gates/test_diff_helpers.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_doc_ref_broken_gate_py["commit_gates/test_doc_ref_broken_gate<br/>test_doc_ref_broken_gate.py — DOC-REF-BROKEN<br/>门禁单测<br/>文件: commit_gates/test_doc_ref_broken_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_fk_gate_py["commit_gates/test_domain_fk_gate<br/>test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测<br/>文件: commit_gates/test_domain_fk_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py["commit_gates<br/>/test_domain_name_zh_direct_access_gate<br/>test_domain_name_zh_direct_access_gate.py —<br/>NO-DOMAIN-NAME-ZH-DIRECT-ACCESS ...<br/>文件: commit_gates<br/>/test_domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_empty_handler_gate_py["commit_gates/test_empty_handler_gate<br/>test_empty_handler_gate.py — EMPTY-HANDLER<br/>门禁单测<br/>文件: commit_gates/test_empty_handler_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py["commit_gates/test_exempt_zone_frontmatter_gate<br/>test_exempt_zone_frontmatter_gate.py —<br/>EXEMPT-ZONE-FM 门禁单测<br/>文件: commit_gates<br/>/test_exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_file_copy_gate_py["commit_gates/test_file_copy_gate<br/>test_file_copy_gate.py — FILE-COPY 门禁单测<br/>文件: commit_gates/test_file_copy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_foreign_change_gate_py["commit_gates/test_foreign_change_gate<br/>test_foreign_change_gate.py —<br/>外来变更检测门禁单测<br/>（FOREIGN-CHANGE-DETECTION...<br/>文件: commit_gates/test_foreign_change_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_forged_gw_marker_gate_py["commit_gates/test_forged_gw_marker_gate<br/>test_forged_gw_marker_gate.py — Forged GW<br/>Marker 前置检测门禁单测（...<br/>文件: commit_gates/test_forged_gw_marker_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_function_dup_gate_py["commit_gates/test_function_dup_gate<br/>test_function_dup_gate.py — FUNCTION-DUP<br/>门禁单测<br/>文件: commit_gates/test_function_dup_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_god_class_gate_py["commit_gates/test_god_class_gate<br/>test_god_class_gate.py — NO-GOD-CLASS 门禁单测<br/>文件: commit_gates/test_god_class_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_hardcoded_url_gate_py["commit_gates/test_hardcoded_url_gate<br/>test_hardcoded_url_gate.py — NO-HARDCODED-URL<br/>门禁单测<br/>文件: commit_gates/test_hardcoded_url_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_held_overlap_gate_py["commit_gates/test_held_overlap_gate<br/>test_held_overlap_gate.py — 搭便车防护门禁单测<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/test_held_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_high_complexity_gate_py["commit_gates/test_high_complexity_gate<br/>test_high_complexity_gate.py —<br/>NO-HIGH-COMPLEXITY 门禁单测<br/>文件: commit_gates/test_high_complexity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_id_uniqueness_gate_py["commit_gates/test_id_uniqueness_gate<br/>test_id_uniqueness_gate.py — ID-UNIQUENESS<br/>门禁单测<br/>文件: commit_gates/test_id_uniqueness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_direction_gate_py["commit_gates/test_import_direction_gate<br/>test_import_direction_gate.py —<br/>NO-UPWARD-IMPORT 门禁单测<br/>文件: commit_gates/test_import_direction_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_integrity_gate_py["commit_gates/test_import_integrity_gate<br/>test_import_integrity_gate.py —<br/>IMPORT-INTEGRITY 门禁单测（...<br/>文件: commit_gates/test_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_long_param_list_gate_py["commit_gates/test_long_param_list_gate<br/>test_long_param_list_gate.py —<br/>NO-LONG-PARAM-LIST 门禁单测<br/>文件: commit_gates/test_long_param_list_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py["commit_gates<br/>/test_manual_only_permanent_gate_noqa<br/>test_manual_only_permanent_gate_noqa.py —<br/>MANUAL-ONLY-PERMANENT m11 noqa 豁...<br/>文件: commit_gates<br/>/test_manual_only_permanent_gate_noqa.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mcp_version_field_gate_py["commit_gates/test_mcp_version_field_gate<br/>test_mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁单测（MCP-VER...<br/>文件: commit_gates<br/>/test_mcp_version_field_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_module_id_consistency_gate_py["commit_gates/test_module_id_consistency_gate<br/>test_module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生...<br/>文件: commit_gates<br/>/test_module_id_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_exposure_gate_py["commit_gates/test_msg_exposure_gate<br/>test_msg_exposure_gate.py — MSG-EXPOSURE<br/>门禁单测<br/>文件: commit_gates/test_msg_exposure_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_style_gate_py["commit_gates/test_msg_style_gate<br/>test_msg_style_gate.py — MSG-STYLE 门禁单测<br/>文件: commit_gates/test_msg_style_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py["commit_gates<br/>/test_mutable_const_without_final_gate<br/>test_mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁单...<br/>文件: commit_gates<br/>/test_mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_new_file_depgraph_gate_py["commit_gates/test_new_file_depgraph_gate<br/>test_new_file_depgraph_gate.py —<br/>NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>文件: commit_gates<br/>/test_new_file_depgraph_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_no_import_side_effect_gate_py["commit_gates/test_no_import_side_effect_gate<br/>test_no_import_side_effect_gate.py —<br/>NO-IMPORT-SIDE-EFFECT 门禁单测<br/>文件: commit_gates<br/>/test_no_import_side_effect_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_open_without_with_gate_py["commit_gates/test_open_without_with_gate<br/>test_open_without_with_gate.py — open() 未在<br/>with 内硬阻断门禁单测（OPEN-WIT...<br/>文件: commit_gates<br/>/test_open_without_with_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_orphan_module_gate_py["commit_gates/test_orphan_module_gate<br/>test_orphan_module_gate.py — ORPHAN-MODULE<br/>门禁单测<br/>文件: commit_gates/test_orphan_module_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_panorama_alignment_gate_py["commit_gates/test_panorama_alignment_gate<br/>test_panorama_alignment_gate.py —<br/>四图模块对齐门禁单测（GATE-PANORAMA-ALIGNM...<br/>文件: commit_gates<br/>/test_panorama_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_perm_trigger_gate_py["commit_gates/test_perm_trigger_gate<br/>test_perm_trigger_gate.py — PERM-TRIGGER<br/>门禁单测<br/>文件: commit_gates/test_perm_trigger_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_precommit_offline_gate_py["commit_gates/test_precommit_offline_gate<br/>test_precommit_offline_gate.py —<br/>GATE-PRECOMMIT-OFFLINE 门禁单测<br/>文件: commit_gates<br/>/test_precommit_offline_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_protected_paths_gate_py["commit_gates/test_protected_paths_gate<br/>test_protected_paths_gate.py —<br/>受保护路径写入检测门禁单测（...<br/>文件: commit_gates/test_protected_paths_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["commit_gates/test_r5_digit_suffix_gate<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX<br/>门禁单元测试<br/>文件: commit_gates/test_r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_reconciler_health_gate_py["commit_gates/test_reconciler_health_gate<br/>test_reconciler_health_gate.py —<br/>RECONCILER-HEALTH 门禁单测<br/>文件: commit_gates<br/>/test_reconciler_health_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py["commit_gates/test_rename_depgraph_sync_gate<br/>test_rename_depgraph_sync_gate.py —<br/>RENAME-DEPGRAPH-SYNC 门禁单测<br/>文件: commit_gates<br/>/test_rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py["commit_gates/test_rule_execution_pairing_gate<br/>Tests for RULE-EXECUTION-PAIRING gate (Phase<br/>3.5).<br/>文件: commit_gates<br/>/test_rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py["commit_gates/test_rule_four_way_alignment_gate<br/>test_rule_four_way_alignment_gate.py —<br/>RULE-FOUR-WAY-ALIGN 门禁单测<br/>文件: commit_gates<br/>/test_rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py["commit_gates/test_ruling_commit_verified_gate<br/>test_ruling_commit_verified_gate.py —<br/>RULING-COMMIT-VERIFIED 门禁单测。<br/>文件: commit_gates<br/>/test_ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_reference_gate_py["commit_gates/test_ruling_reference_gate<br/>test_ruling_reference_gate.py — 裁定#NNN<br/>悬空引用检测门禁单测（RULING-REFERE...<br/>文件: commit_gates/test_ruling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_schema_file_exists_gate_py["commit_gates/test_schema_file_exists_gate<br/>test_schema_file_exists_gate.py —<br/>SCHEMA-FILE-EXISTS 门禁单测<br/>文件: commit_gates<br/>/test_schema_file_exists_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py["commit_gates/test_scripts_import_integrity_gate<br/>test_scripts_import_integrity_gate.py —<br/>SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>文件: commit_gates<br/>/test_scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_session_required_gate_py["commit_gates/test_session_required_gate<br/>test_session_required_gate.py —<br/>SESSION-REQUIRED 门禁单测<br/>文件: commit_gates/test_session_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ssot_redefinition_gate_py["commit_gates/test_ssot_redefinition_gate<br/>test_ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁单测（SSOT-REDEF...<br/>文件: commit_gates<br/>/test_ssot_redefinition_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_test_source_consistency_gate_py["commit_gates/test_test_source_consistency_gate<br/>test_test_source_consistency_gate.py —<br/>TEST-SOURCE-CONSISTENCY 门禁单测<br/>文件: commit_gates<br/>/test_test_source_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_translation_coverage_gate_py["commit_gates/test_translation_coverage_gate<br/>test_translation_coverage_gate.py —<br/>TRANSLATION-COVERAGE 门禁单测<br/>文件: commit_gates<br/>/test_translation_coverage_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_undefined_name_gate_py["commit_gates/test_undefined_name_gate<br/>test_undefined_name_gate.py — UNDEFINED-NAME<br/>门禁单测<br/>文件: commit_gates/test_undefined_name_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py["commit_gates/test_unsafe_dict_spread_gate<br/>test_unsafe_dict_spread_gate.py — ``**data``<br/>直接展开 warn 级门禁单测（UNSAF...<br/>文件: commit_gates<br/>/test_unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_vocab_hardcode_gate_py["commit_gates/test_vocab_hardcode_gate<br/>test_vocab_hardcode_gate.py — VOCAB-HARDCODE<br/>门禁单测<br/>文件: commit_gates/test_vocab_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py["commit_gates/test_zephyr_env_direct_access_gate<br/>test_zephyr_env_direct_access_gate.py —<br/>ZEPHYR_ENV 直访硬阻断门禁单测（ZEPHY...<br/>文件: commit_gates<br/>/test_zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["rule_bridge/test_claim_files_for_edit<br/>test_claim_files_for_edit.py — P2-2 并发<br/>session 文件级原子性测试<br/>文件: rule_bridge/test_claim_files_for_edit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_commit_gate_registry_py["rule_bridge/test_commit_gate_registry<br/>test_commit_gate_registry.py —<br/>CommitGateRegistry 单测（架构债务 #AD-001 治本）<br/>文件: rule_bridge/test_commit_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_emergency_commit_py["rule_bridge/test_emergency_commit<br/>test_emergency_commit.py — emergency_commit API<br/>测试（Ruling:100PCT-AI-GOVER...<br/>文件: rule_bridge/test_emergency_commit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_gate_auto_registrar_py["rule_bridge/test_gate_auto_registrar<br/>test_gate_auto_registrar.py —<br/>gate_auto_registrar 单元测试（...<br/>文件: rule_bridge/test_gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["rule_bridge/test_heartbeat_daemon<br/>test_heartbeat_daemon.py — heartbeat daemon +<br/>成本递增 smoke test（Ruling:10...<br/>文件: rule_bridge/test_heartbeat_daemon.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_py["rule_bridge/test_session_worktree<br/>test_session_worktree.py — worktree<br/>物理隔离端到端测试（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/test_session_worktree.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_cli_py["rule_bridge/test_session_worktree_cli<br/>test_session_worktree_cli.py —<br/>session_worktree_cli CLI 测试（治本遗留项#2, ...<br/>文件: rule_bridge/test_session_worktree_cli.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_health_check_py["rule_bridge/test_session_worktree_health_check<br/>test_session_worktree_health_check.py —<br/>session_worktree_start 启动健康度自...<br/>文件: rule_bridge<br/>/test_session_worktree_health_check.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py["rule_bridge<br/>/test_session_worktree_trusted_git_env<br/>test_session_worktree_trusted_git_env.py —<br/>_trusted_git_env 进程级隔离单测（...<br/>文件: rule_bridge<br/>/test_session_worktree_trusted_git_env.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py["rule_bridge<br/>/test_session_worktree_workspace_clean<br/>test_session_worktree_workspace_clean.py —<br/>session lifecycle 工作区 clean 检...<br/>文件: rule_bridge<br/>/test_session_worktree_workspace_clean.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_pool_py["rule_bridge/test_worktree_pool<br/>test_worktree_pool.py — WorktreePool 端到端<br/>smoke test（ARCH-GIT-CALL-BUDGET...<br/>文件: rule_bridge/test_worktree_pool.py<br/>(生产态 / production)"]
    tests_ops_test_shadow_canary_deploy_py["ops/test_shadow_canary_deploy<br/>test_shadow_canary_deploy.py — Shadow Canary<br/>部署运行器单元测试<br/>文件: ops/test_shadow_canary_deploy.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml ~~~ scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py ~~~ scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py ~~~ scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py ~~~ scripts_governance_session_worktree_cli_py
    scripts_governance_session_worktree_cli_py ~~~ scripts_ops_shadow_canary_deploy_py
    scripts_ops_shadow_canary_deploy_py ~~~ src_zephyr_gov_enforcement_init_py
    src_zephyr_gov_enforcement_init_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_init_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py ~~~ src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py ~~~ src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_approval_py
    src_zephyr_gov_enforcement_rule_enforcement_approval_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py ~~~ tests_governance_commit_gates_test_arch_reference_gate_py
    tests_governance_commit_gates_test_arch_reference_gate_py ~~~ tests_governance_commit_gates_test_asyncio_run_in_context_gate_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py ~~~ tests_governance_commit_gates_test_bare_getenv_gate_py
    tests_governance_commit_gates_test_bare_getenv_gate_py ~~~ tests_governance_commit_gates_test_bare_sql_gate_py
    tests_governance_commit_gates_test_bare_sql_gate_py ~~~ tests_governance_commit_gates_test_bare_subprocess_gate_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py ~~~ tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py ~~~ tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py ~~~ tests_governance_commit_gates_test_capability_lookup_audit_log_py
    tests_governance_commit_gates_test_capability_lookup_audit_log_py ~~~ tests_governance_commit_gates_test_capability_lookup_bypass_policy_py
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py ~~~ tests_governance_commit_gates_test_capability_lookup_required_gate_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py ~~~ tests_governance_commit_gates_test_capability_overlap_gate_py
    tests_governance_commit_gates_test_capability_overlap_gate_py ~~~ tests_governance_commit_gates_test_ch_batch_size_gate_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py ~~~ tests_governance_commit_gates_test_ch_version_col_gate_py
    tests_governance_commit_gates_test_ch_version_col_gate_py ~~~ tests_governance_commit_gates_test_claim_required_gate_py
    tests_governance_commit_gates_test_claim_required_gate_py ~~~ tests_governance_commit_gates_test_consumers_accuracy_gate_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py ~~~ tests_governance_commit_gates_test_create_guard_py
    tests_governance_commit_gates_test_create_guard_py ~~~ tests_governance_commit_gates_test_dangling_reference_gate_py
    tests_governance_commit_gates_test_dangling_reference_gate_py ~~~ tests_governance_commit_gates_test_datetime_now_forbidden_gate_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py ~~~ tests_governance_commit_gates_test_depgraph_freshness_gate_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py ~~~ tests_governance_commit_gates_test_depgraph_pre_registration_gate_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py ~~~ tests_governance_commit_gates_test_derived_file_deletion_gate_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py ~~~ tests_governance_commit_gates_test_diff_helpers_py
    tests_governance_commit_gates_test_diff_helpers_py ~~~ tests_governance_commit_gates_test_doc_ref_broken_gate_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py ~~~ tests_governance_commit_gates_test_domain_fk_gate_py
    tests_governance_commit_gates_test_domain_fk_gate_py ~~~ tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py ~~~ tests_governance_commit_gates_test_empty_handler_gate_py
    tests_governance_commit_gates_test_empty_handler_gate_py ~~~ tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py ~~~ tests_governance_commit_gates_test_file_copy_gate_py
    tests_governance_commit_gates_test_file_copy_gate_py ~~~ tests_governance_commit_gates_test_foreign_change_gate_py
    tests_governance_commit_gates_test_foreign_change_gate_py ~~~ tests_governance_commit_gates_test_forged_gw_marker_gate_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py ~~~ tests_governance_commit_gates_test_function_dup_gate_py
    tests_governance_commit_gates_test_function_dup_gate_py ~~~ tests_governance_commit_gates_test_god_class_gate_py
    tests_governance_commit_gates_test_god_class_gate_py ~~~ tests_governance_commit_gates_test_hardcoded_url_gate_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py ~~~ tests_governance_commit_gates_test_held_overlap_gate_py
    tests_governance_commit_gates_test_held_overlap_gate_py ~~~ tests_governance_commit_gates_test_high_complexity_gate_py
    tests_governance_commit_gates_test_high_complexity_gate_py ~~~ tests_governance_commit_gates_test_id_uniqueness_gate_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py ~~~ tests_governance_commit_gates_test_import_direction_gate_py
    tests_governance_commit_gates_test_import_direction_gate_py ~~~ tests_governance_commit_gates_test_import_integrity_gate_py
    tests_governance_commit_gates_test_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_long_param_list_gate_py
    tests_governance_commit_gates_test_long_param_list_gate_py ~~~ tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py ~~~ tests_governance_commit_gates_test_mcp_version_field_gate_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py ~~~ tests_governance_commit_gates_test_module_id_consistency_gate_py
    tests_governance_commit_gates_test_module_id_consistency_gate_py ~~~ tests_governance_commit_gates_test_msg_exposure_gate_py
    tests_governance_commit_gates_test_msg_exposure_gate_py ~~~ tests_governance_commit_gates_test_msg_style_gate_py
    tests_governance_commit_gates_test_msg_style_gate_py ~~~ tests_governance_commit_gates_test_mutable_const_without_final_gate_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py ~~~ tests_governance_commit_gates_test_new_file_depgraph_gate_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py ~~~ tests_governance_commit_gates_test_no_import_side_effect_gate_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py ~~~ tests_governance_commit_gates_test_open_without_with_gate_py
    tests_governance_commit_gates_test_open_without_with_gate_py ~~~ tests_governance_commit_gates_test_orphan_module_gate_py
    tests_governance_commit_gates_test_orphan_module_gate_py ~~~ tests_governance_commit_gates_test_panorama_alignment_gate_py
    tests_governance_commit_gates_test_panorama_alignment_gate_py ~~~ tests_governance_commit_gates_test_perm_trigger_gate_py
    tests_governance_commit_gates_test_perm_trigger_gate_py ~~~ tests_governance_commit_gates_test_precommit_offline_gate_py
    tests_governance_commit_gates_test_precommit_offline_gate_py ~~~ tests_governance_commit_gates_test_protected_paths_gate_py
    tests_governance_commit_gates_test_protected_paths_gate_py ~~~ tests_governance_commit_gates_test_r5_digit_suffix_gate_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py ~~~ tests_governance_commit_gates_test_reconciler_health_gate_py
    tests_governance_commit_gates_test_reconciler_health_gate_py ~~~ tests_governance_commit_gates_test_rename_depgraph_sync_gate_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py ~~~ tests_governance_commit_gates_test_rule_execution_pairing_gate_py
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py ~~~ tests_governance_commit_gates_test_rule_four_way_alignment_gate_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py ~~~ tests_governance_commit_gates_test_ruling_commit_verified_gate_py
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py ~~~ tests_governance_commit_gates_test_ruling_reference_gate_py
    tests_governance_commit_gates_test_ruling_reference_gate_py ~~~ tests_governance_commit_gates_test_schema_file_exists_gate_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py ~~~ tests_governance_commit_gates_test_scripts_import_integrity_gate_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_session_required_gate_py
    tests_governance_commit_gates_test_session_required_gate_py ~~~ tests_governance_commit_gates_test_ssot_redefinition_gate_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py ~~~ tests_governance_commit_gates_test_test_source_consistency_gate_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py ~~~ tests_governance_commit_gates_test_translation_coverage_gate_py
    tests_governance_commit_gates_test_translation_coverage_gate_py ~~~ tests_governance_commit_gates_test_undefined_name_gate_py
    tests_governance_commit_gates_test_undefined_name_gate_py ~~~ tests_governance_commit_gates_test_unsafe_dict_spread_gate_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py ~~~ tests_governance_commit_gates_test_vocab_hardcode_gate_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py ~~~ tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py ~~~ tests_governance_rule_bridge_test_claim_files_for_edit_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py ~~~ tests_governance_rule_bridge_test_commit_gate_registry_py
    tests_governance_rule_bridge_test_commit_gate_registry_py ~~~ tests_governance_rule_bridge_test_emergency_commit_py
    tests_governance_rule_bridge_test_emergency_commit_py ~~~ tests_governance_rule_bridge_test_gate_auto_registrar_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py ~~~ tests_governance_rule_bridge_test_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py ~~~ tests_governance_rule_bridge_test_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_py ~~~ tests_governance_rule_bridge_test_session_worktree_cli_py
    tests_governance_rule_bridge_test_session_worktree_cli_py ~~~ tests_governance_rule_bridge_test_session_worktree_health_check_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py ~~~ tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py ~~~ tests_governance_rule_bridge_test_session_worktree_workspace_clean_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py ~~~ tests_governance_rule_bridge_test_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py ~~~ tests_ops_test_shadow_canary_deploy_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["behavioral_admission/admission_response<br/>behavioral admission包的admission_response模块<br/>文件: behavioral_admission/admission_response.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["behavioral_admission/code_review_ai<br/>behavioral admission包的code_review_ai模块<br/>文件: behavioral_admission/code_review_ai.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["behavioral_admission/gate_event_adapter<br/>GateEventAdapter — GateRepo 事件适配器<br/>（DW-0006）<br/>文件: behavioral_admission/gate_event_adapter.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["behavioral_admission/gpu_consensus_scheduler<br/>behavioral<br/>admission包的gpu_consensus_scheduler模块<br/>文件: behavioral_admission<br/>/gpu_consensus_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["behavioral_admission/protection_index<br/>behavioral admission包的protection_index模块<br/>文件: behavioral_admission/protection_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["rule_bridge/commit_gate_registry<br/>commit_gate_registry.py — GitCommitGateway<br/>pre-commit 门禁注册表（架构债务 #...<br/>文件: rule_bridge/commit_gate_registry.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["rule_bridge/session_worktree<br/>session_worktree.py — AI 对话 worktree 物理隔离<br/>helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["rule_enforcement/quality_gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["behavioral_admission/admission_controller<br/>behavioral admission包的admission_controller模块<br/>文件: behavioral_admission<br/>/admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["behavioral_admission/verdict_engine<br/>behavioral admission包的verdict_engine模块<br/>文件: behavioral_admission/verdict_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["rule_bridge/emergency_commit<br/>emergency_commit.py — 紧急提交通道<br/>（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>文件: rule_bridge/emergency_commit.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["rule_bridge/heartbeat_daemon<br/>heartbeat_daemon.py — session heartbeat<br/>独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>文件: rule_bridge/heartbeat_daemon.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["rule_bridge/session_claim<br/>session_claim.py — AI 对话并发声明 helper<br/>（FP-ISO.4B 件2改，2026-07-01 治本）<br/>文件: rule_bridge/session_claim.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["rule_bridge/worktree_manager<br/>worktree_manager.py — session worktree<br/>物理隔离管理器（阶段3 治本 stash 循环）<br/>文件: rule_bridge/worktree_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["rule_bridge/worktree_pool<br/>worktree_pool.py — Worktree 预创建池<br/>（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>文件: rule_bridge/worktree_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["rule_bridge/git_commit_gateway<br/>GitCommitGateway — 全项目唯一合法 git commit<br/>入口（OPS-2026062512 治本）<br/>文件: rule_bridge/git_commit_gateway.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["rule_bridge/batched_auto_committer<br/>batched_auto_committer.py — Reconciler 批量化<br/>auto-commit 拦截器（ARCH-GIT-C...<br/>文件: rule_bridge/batched_auto_committer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_getenv_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_sql_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_claim_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_version_col_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_empty_handler_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_fk_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_file_copy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_function_dup_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_held_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_high_complexity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_direction_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_god_class_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_long_param_list_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_exposure_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_style_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_open_without_with_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_orphan_module_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_precommit_offline_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_perm_trigger_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_protected_paths_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_reconciler_health_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_session_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_undefined_name_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_translation_coverage_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_rule_bridge_test_commit_gate_registry_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOV_RULE["规则治理<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>Rule Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_GOV_RULE
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_SECURITY
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    tests_ops_test_shadow_canary_deploy_py -->|测试依赖 / test_depends| D_GOV_RULE
    D_GOV_CODE_QUALITY["代码质量治理<br/>代码质量治理，负责代码去重引擎、函数重复检测、AS<br/>T语义分析和提交门禁引擎<br/>Code Quality Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_protected_paths_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    tests_governance_commit_gates_test_derived_file_deletion_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_SHARED
    tests_governance_commit_gates_test_schema_file_exists_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_ML_TRAIN["训练<br/>训练，负责模型训练、特征工程和模型评估<br/>Training<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_ML_TRAIN -.->|data / data| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_arch_reference_gate_py,tests_governance_commit_gates_test_asyncio_run_in_context_gate_py,tests_governance_commit_gates_test_bare_getenv_gate_py,tests_governance_commit_gates_test_bare_sql_gate_py,tests_governance_commit_gates_test_bare_subprocess_gate_py,tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py,tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py,tests_governance_commit_gates_test_capability_lookup_audit_log_py,tests_governance_commit_gates_test_capability_lookup_bypass_policy_py,tests_governance_commit_gates_test_capability_lookup_required_gate_py,tests_governance_commit_gates_test_capability_overlap_gate_py,tests_governance_commit_gates_test_ch_batch_size_gate_py,tests_governance_commit_gates_test_ch_version_col_gate_py,tests_governance_commit_gates_test_claim_required_gate_py,tests_governance_commit_gates_test_consumers_accuracy_gate_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_dangling_reference_gate_py,tests_governance_commit_gates_test_datetime_now_forbidden_gate_py,tests_governance_commit_gates_test_depgraph_freshness_gate_py,tests_governance_commit_gates_test_depgraph_pre_registration_gate_py,tests_governance_commit_gates_test_derived_file_deletion_gate_py,tests_governance_commit_gates_test_diff_helpers_py,tests_governance_commit_gates_test_doc_ref_broken_gate_py,tests_governance_commit_gates_test_domain_fk_gate_py,tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py,tests_governance_commit_gates_test_empty_handler_gate_py,tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py,tests_governance_commit_gates_test_file_copy_gate_py,tests_governance_commit_gates_test_foreign_change_gate_py,tests_governance_commit_gates_test_forged_gw_marker_gate_py,tests_governance_commit_gates_test_function_dup_gate_py,tests_governance_commit_gates_test_god_class_gate_py,tests_governance_commit_gates_test_hardcoded_url_gate_py,tests_governance_commit_gates_test_held_overlap_gate_py,tests_governance_commit_gates_test_high_complexity_gate_py,tests_governance_commit_gates_test_id_uniqueness_gate_py,tests_governance_commit_gates_test_import_direction_gate_py,tests_governance_commit_gates_test_import_integrity_gate_py,tests_governance_commit_gates_test_long_param_list_gate_py,tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py,tests_governance_commit_gates_test_mcp_version_field_gate_py,tests_governance_commit_gates_test_module_id_consistency_gate_py,tests_governance_commit_gates_test_msg_exposure_gate_py,tests_governance_commit_gates_test_msg_style_gate_py,tests_governance_commit_gates_test_mutable_const_without_final_gate_py,tests_governance_commit_gates_test_new_file_depgraph_gate_py,tests_governance_commit_gates_test_no_import_side_effect_gate_py,tests_governance_commit_gates_test_open_without_with_gate_py,tests_governance_commit_gates_test_orphan_module_gate_py,tests_governance_commit_gates_test_panorama_alignment_gate_py,tests_governance_commit_gates_test_perm_trigger_gate_py,tests_governance_commit_gates_test_precommit_offline_gate_py,tests_governance_commit_gates_test_protected_paths_gate_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_commit_gates_test_reconciler_health_gate_py,tests_governance_commit_gates_test_rename_depgraph_sync_gate_py,tests_governance_commit_gates_test_rule_execution_pairing_gate_py,tests_governance_commit_gates_test_rule_four_way_alignment_gate_py,tests_governance_commit_gates_test_ruling_commit_verified_gate_py,tests_governance_commit_gates_test_ruling_reference_gate_py,tests_governance_commit_gates_test_schema_file_exists_gate_py,tests_governance_commit_gates_test_scripts_import_integrity_gate_py,tests_governance_commit_gates_test_session_required_gate_py,tests_governance_commit_gates_test_ssot_redefinition_gate_py,tests_governance_commit_gates_test_test_source_consistency_gate_py,tests_governance_commit_gates_test_translation_coverage_gate_py,tests_governance_commit_gates_test_undefined_name_gate_py,tests_governance_commit_gates_test_unsafe_dict_spread_gate_py,tests_governance_commit_gates_test_vocab_hardcode_gate_py,tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_commit_gate_registry_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_gate_auto_registrar_py,tests_governance_rule_bridge_test_heartbeat_daemon_py,tests_governance_rule_bridge_test_session_worktree_py,tests_governance_rule_bridge_test_session_worktree_cli_py,tests_governance_rule_bridge_test_session_worktree_health_check_py,tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py,tests_governance_rule_bridge_test_session_worktree_workspace_clean_py,tests_governance_rule_bridge_test_worktree_pool_py,tests_ops_test_shadow_canary_deploy_py production
    class scripts_ops_shadow_canary_deploy_py,src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py design
    class D_GOV_RULE,D_GOVERNANCE,D_AUTONOMY_CORE,D_SECURITY,D_GOV_AUDIT,D_GOV_CODE_QUALITY,D_SHARED external_prod
    class D_ML_TRAIN external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 118 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml["catalogs/rule_enforcement_registry<br/>catalogs包的rule_enforcement_registry模块<br/>文件: catalogs/rule_enforcement_registry.yaml<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["d8_doc_sync/metric_count_drift_reconciler<br/>metric_count_drift_reconciler.py — dashboard<br/>指标数描述派生校验 reconciler<br/>文件: d8_doc_sync<br/>/metric_count_drift_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["d8_doc_sync/readme_version_sync_reconciler<br/>readme_version_sync_reconciler.py — README<br/>版本号派生展示校验 reconciler<br/>文件: d8_doc_sync<br/>/readme_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["d8_doc_sync/requirements_version_sync_reconciler<br/>requirements_version_sync_reconciler.py —<br/>requirements.txt ↔ pyproject.toml...<br/>文件: d8_doc_sync<br/>/requirements_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_session_worktree_cli_py["governance/session_worktree_cli<br/>session_worktree_cli.py — session worktree 管理<br/>CLI（治本遗留项#2，2026-07-17）<br/>文件: governance/session_worktree_cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_init_py["zephyr/gov_enforcement 包入口<br/>gov_enforcement package — 执行治理域<br/>（D_GOV_ENFORCEMENT）<br/>文件: gov_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["gov_enforcement/behavioral_admission 包入口<br/>管理gov_enforcement.behavioral_admission子包的加<br/>载和懒导入<br/>文件: behavioral_admission/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["commit_gates/stash_accumulation_gate<br/>stash_accumulation_gate.py — stash<br/>堆积阈值检测门禁（STASH-ACCUMULATION）<br/>文件: commit_gates/stash_accumulation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["rule_enforcement/approval<br/>G-CT-004 — Backward-compat re-export of<br/>ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["rule_enforcement/compliance_rule<br/>rule enforcement包的compliance_rule模块<br/>文件: rule_enforcement/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["rule_enforcement/default_quality_gate<br/>D_DATA — Default Data Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["rule_enforcement/dlq_retry_policy<br/>DLQ 重试策略 — 对接 shared/events<br/>/dlq.DeadLetterQueue 的真重试。<br/>文件: rule_enforcement/dlq_retry_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["rule_enforcement/output_quality_gate<br/>rule enforcement包的output_quality_gate模块<br/>文件: rule_enforcement/output_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["rule_enforcement/pre_flight_gate<br/>rule enforcement包的pre_flight_gate模块<br/>文件: rule_enforcement/pre_flight_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["rule_engine/rule_canary_manager<br/>Rule Canary Manager — v0.10.0 规则金丝雀:<br/>1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["rule_engine/rule_debt_auditor<br/>Rule Debt Auditor — v0.7.0 规则债务审计器:<br/>分析escalation_rules.yaml维护债务...<br/>文件: rule_engine/rule_debt_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["rule_engine/rule_shadow_runner<br/>Rule Shadow Runner — v0.10.0 规则影子模式:<br/>新规则shadow运行3天->diff old vs ...<br/>文件: rule_engine/rule_shadow_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["rule_engine/rule_watcher<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>文件: rule_engine/rule_watcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["rule_enforcement/slo_contract<br/>SLO-Driven Escalation Contract — D-022-12.<br/>文件: rule_enforcement/slo_contract.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_arch_reference_gate_py["commit_gates/test_arch_reference_gate<br/>test_arch_reference_gate.py — #ARCH-NNN<br/>悬空引用检测门禁单测（ARCH-REFERENCE）<br/>文件: commit_gates/test_arch_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py["commit_gates/test_asyncio_run_in_context_gate<br/>test_asyncio_run_in_context_gate.py — asyncio<br/>API 误用硬阻断门禁单测（ASYNCI...<br/>文件: commit_gates<br/>/test_asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_getenv_gate_py["commit_gates/test_bare_getenv_gate<br/>test_bare_getenv_gate.py — NO-BARE-GETENV<br/>门禁单测<br/>文件: commit_gates/test_bare_getenv_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_sql_gate_py["commit_gates/test_bare_sql_gate<br/>test_bare_sql_gate.py — NO-BARE-SQL 门禁单测<br/>文件: commit_gates/test_bare_sql_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_subprocess_gate_py["commit_gates/test_bare_subprocess_gate<br/>test_bare_subprocess_gate.py — BARE-SUBPROCESS<br/>门禁单测<br/>文件: commit_gates/test_bare_subprocess_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py["commit_gates<br/>/test_blueprint_amodule_consistency_gate<br/>test_blueprint_amodule_consistency_gate.py —<br/>BLUEPRINT-AMODULE-CONSISTENCY ...<br/>文件: commit_gates<br/>/test_blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py["commit_gates<br/>/test_blueprint_amodule_cross_check_gate<br/>test_blueprint_amodule_cross_check_gate.py —<br/>BLUEPRINT-AMODULE-CROSS-CHECK ...<br/>文件: commit_gates<br/>/test_blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_audit_log_py["commit_gates/test_capability_lookup_audit_log<br/>test_capability_lookup_audit_log.py —<br/>capability_lookup audit log 落盘 e2e s...<br/>文件: commit_gates<br/>/test_capability_lookup_audit_log.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py["commit_gates<br/>/test_capability_lookup_bypass_policy<br/>test_capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享...<br/>文件: commit_gates<br/>/test_capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_required_gate_py["commit_gates<br/>/test_capability_lookup_required_gate<br/>test_capability_lookup_required_gate.py —<br/>CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>文件: commit_gates<br/>/test_capability_lookup_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_overlap_gate_py["commit_gates/test_capability_overlap_gate<br/>test_capability_overlap_gate.py —<br/>CAPABILITY-OVERLAP 门禁单测<br/>文件: commit_gates<br/>/test_capability_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_batch_size_gate_py["commit_gates/test_ch_batch_size_gate<br/>test_ch_batch_size_gate.py — CH-BATCH-SIZE<br/>门禁单测<br/>文件: commit_gates/test_ch_batch_size_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_version_col_gate_py["commit_gates/test_ch_version_col_gate<br/>test_ch_version_col_gate.py — CH-VERSION-COL<br/>门禁单测<br/>文件: commit_gates/test_ch_version_col_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_claim_required_gate_py["commit_gates/test_claim_required_gate<br/>test_claim_required_gate.py — claim_files<br/>前置检查门禁单测（CLAIM-REQUIRED，...<br/>文件: commit_gates/test_claim_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_consumers_accuracy_gate_py["commit_gates/test_consumers_accuracy_gate<br/>test_consumers_accuracy_gate.py —<br/>CONSUMERS-ACCURACY 门禁单测（...<br/>文件: commit_gates<br/>/test_consumers_accuracy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_create_guard_py["commit_gates/test_create_guard<br/>test_create_guard.py — CREATE-GUARD<br/>门禁单元测试（2026-06-30 治本补全）<br/>文件: commit_gates/test_create_guard.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_dangling_reference_gate_py["commit_gates/test_dangling_reference_gate<br/>test_dangling_reference_gate.py — AGENTS.md<br/>§X.Y 悬空引用检测门禁单测（DANG...<br/>文件: commit_gates<br/>/test_dangling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py["commit_gates/test_datetime_now_forbidden_gate<br/>test_datetime_now_forbidden_gate.py —<br/>生成器代码 datetime.now() 硬阻断门禁单...<br/>文件: commit_gates<br/>/test_datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_freshness_gate_py["commit_gates/test_depgraph_freshness_gate<br/>test_depgraph_freshness_gate.py —<br/>DEPGRAPH-FRESHNESS 门禁单测<br/>文件: commit_gates<br/>/test_depgraph_freshness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py["commit_gates/test_depgraph_pre_registration_gate<br/>test_depgraph_pre_registration_gate.py —<br/>DEPGRAPH-PRE-REGISTRATION gate 测试<br/>文件: commit_gates<br/>/test_depgraph_pre_registration_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_derived_file_deletion_gate_py["commit_gates/test_derived_file_deletion_gate<br/>test_derived_file_deletion_gate.py —<br/>派生文件删除保护门禁单测（DERIVED-FILE-...<br/>文件: commit_gates<br/>/test_derived_file_deletion_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_diff_helpers_py["commit_gates/test_diff_helpers<br/>test_diff_helpers.py — gate 共享 diff<br/>解析工具模块单测<br/>文件: commit_gates/test_diff_helpers.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_doc_ref_broken_gate_py["commit_gates/test_doc_ref_broken_gate<br/>test_doc_ref_broken_gate.py — DOC-REF-BROKEN<br/>门禁单测<br/>文件: commit_gates/test_doc_ref_broken_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_fk_gate_py["commit_gates/test_domain_fk_gate<br/>test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测<br/>文件: commit_gates/test_domain_fk_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py["commit_gates<br/>/test_domain_name_zh_direct_access_gate<br/>test_domain_name_zh_direct_access_gate.py —<br/>NO-DOMAIN-NAME-ZH-DIRECT-ACCESS ...<br/>文件: commit_gates<br/>/test_domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_empty_handler_gate_py["commit_gates/test_empty_handler_gate<br/>test_empty_handler_gate.py — EMPTY-HANDLER<br/>门禁单测<br/>文件: commit_gates/test_empty_handler_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py["commit_gates/test_exempt_zone_frontmatter_gate<br/>test_exempt_zone_frontmatter_gate.py —<br/>EXEMPT-ZONE-FM 门禁单测<br/>文件: commit_gates<br/>/test_exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_file_copy_gate_py["commit_gates/test_file_copy_gate<br/>test_file_copy_gate.py — FILE-COPY 门禁单测<br/>文件: commit_gates/test_file_copy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_foreign_change_gate_py["commit_gates/test_foreign_change_gate<br/>test_foreign_change_gate.py —<br/>外来变更检测门禁单测<br/>（FOREIGN-CHANGE-DETECTION...<br/>文件: commit_gates/test_foreign_change_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_forged_gw_marker_gate_py["commit_gates/test_forged_gw_marker_gate<br/>test_forged_gw_marker_gate.py — Forged GW<br/>Marker 前置检测门禁单测（...<br/>文件: commit_gates/test_forged_gw_marker_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_function_dup_gate_py["commit_gates/test_function_dup_gate<br/>test_function_dup_gate.py — FUNCTION-DUP<br/>门禁单测<br/>文件: commit_gates/test_function_dup_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_god_class_gate_py["commit_gates/test_god_class_gate<br/>test_god_class_gate.py — NO-GOD-CLASS 门禁单测<br/>文件: commit_gates/test_god_class_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_hardcoded_url_gate_py["commit_gates/test_hardcoded_url_gate<br/>test_hardcoded_url_gate.py — NO-HARDCODED-URL<br/>门禁单测<br/>文件: commit_gates/test_hardcoded_url_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_held_overlap_gate_py["commit_gates/test_held_overlap_gate<br/>test_held_overlap_gate.py — 搭便车防护门禁单测<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/test_held_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_high_complexity_gate_py["commit_gates/test_high_complexity_gate<br/>test_high_complexity_gate.py —<br/>NO-HIGH-COMPLEXITY 门禁单测<br/>文件: commit_gates/test_high_complexity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_id_uniqueness_gate_py["commit_gates/test_id_uniqueness_gate<br/>test_id_uniqueness_gate.py — ID-UNIQUENESS<br/>门禁单测<br/>文件: commit_gates/test_id_uniqueness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_direction_gate_py["commit_gates/test_import_direction_gate<br/>test_import_direction_gate.py —<br/>NO-UPWARD-IMPORT 门禁单测<br/>文件: commit_gates/test_import_direction_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_integrity_gate_py["commit_gates/test_import_integrity_gate<br/>test_import_integrity_gate.py —<br/>IMPORT-INTEGRITY 门禁单测（...<br/>文件: commit_gates/test_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_long_param_list_gate_py["commit_gates/test_long_param_list_gate<br/>test_long_param_list_gate.py —<br/>NO-LONG-PARAM-LIST 门禁单测<br/>文件: commit_gates/test_long_param_list_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py["commit_gates<br/>/test_manual_only_permanent_gate_noqa<br/>test_manual_only_permanent_gate_noqa.py —<br/>MANUAL-ONLY-PERMANENT m11 noqa 豁...<br/>文件: commit_gates<br/>/test_manual_only_permanent_gate_noqa.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mcp_version_field_gate_py["commit_gates/test_mcp_version_field_gate<br/>test_mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁单测（MCP-VER...<br/>文件: commit_gates<br/>/test_mcp_version_field_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_module_id_consistency_gate_py["commit_gates/test_module_id_consistency_gate<br/>test_module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生...<br/>文件: commit_gates<br/>/test_module_id_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_exposure_gate_py["commit_gates/test_msg_exposure_gate<br/>test_msg_exposure_gate.py — MSG-EXPOSURE<br/>门禁单测<br/>文件: commit_gates/test_msg_exposure_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_style_gate_py["commit_gates/test_msg_style_gate<br/>test_msg_style_gate.py — MSG-STYLE 门禁单测<br/>文件: commit_gates/test_msg_style_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py["commit_gates<br/>/test_mutable_const_without_final_gate<br/>test_mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁单...<br/>文件: commit_gates<br/>/test_mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_new_file_depgraph_gate_py["commit_gates/test_new_file_depgraph_gate<br/>test_new_file_depgraph_gate.py —<br/>NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>文件: commit_gates<br/>/test_new_file_depgraph_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_no_import_side_effect_gate_py["commit_gates/test_no_import_side_effect_gate<br/>test_no_import_side_effect_gate.py —<br/>NO-IMPORT-SIDE-EFFECT 门禁单测<br/>文件: commit_gates<br/>/test_no_import_side_effect_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_open_without_with_gate_py["commit_gates/test_open_without_with_gate<br/>test_open_without_with_gate.py — open() 未在<br/>with 内硬阻断门禁单测（OPEN-WIT...<br/>文件: commit_gates<br/>/test_open_without_with_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_orphan_module_gate_py["commit_gates/test_orphan_module_gate<br/>test_orphan_module_gate.py — ORPHAN-MODULE<br/>门禁单测<br/>文件: commit_gates/test_orphan_module_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_panorama_alignment_gate_py["commit_gates/test_panorama_alignment_gate<br/>test_panorama_alignment_gate.py —<br/>四图模块对齐门禁单测（GATE-PANORAMA-ALIGNM...<br/>文件: commit_gates<br/>/test_panorama_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_perm_trigger_gate_py["commit_gates/test_perm_trigger_gate<br/>test_perm_trigger_gate.py — PERM-TRIGGER<br/>门禁单测<br/>文件: commit_gates/test_perm_trigger_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_precommit_offline_gate_py["commit_gates/test_precommit_offline_gate<br/>test_precommit_offline_gate.py —<br/>GATE-PRECOMMIT-OFFLINE 门禁单测<br/>文件: commit_gates<br/>/test_precommit_offline_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_protected_paths_gate_py["commit_gates/test_protected_paths_gate<br/>test_protected_paths_gate.py —<br/>受保护路径写入检测门禁单测（...<br/>文件: commit_gates/test_protected_paths_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["commit_gates/test_r5_digit_suffix_gate<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX<br/>门禁单元测试<br/>文件: commit_gates/test_r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_reconciler_health_gate_py["commit_gates/test_reconciler_health_gate<br/>test_reconciler_health_gate.py —<br/>RECONCILER-HEALTH 门禁单测<br/>文件: commit_gates<br/>/test_reconciler_health_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py["commit_gates/test_rename_depgraph_sync_gate<br/>test_rename_depgraph_sync_gate.py —<br/>RENAME-DEPGRAPH-SYNC 门禁单测<br/>文件: commit_gates<br/>/test_rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py["commit_gates/test_rule_execution_pairing_gate<br/>Tests for RULE-EXECUTION-PAIRING gate (Phase<br/>3.5).<br/>文件: commit_gates<br/>/test_rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py["commit_gates/test_rule_four_way_alignment_gate<br/>test_rule_four_way_alignment_gate.py —<br/>RULE-FOUR-WAY-ALIGN 门禁单测<br/>文件: commit_gates<br/>/test_rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py["commit_gates/test_ruling_commit_verified_gate<br/>test_ruling_commit_verified_gate.py —<br/>RULING-COMMIT-VERIFIED 门禁单测。<br/>文件: commit_gates<br/>/test_ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_reference_gate_py["commit_gates/test_ruling_reference_gate<br/>test_ruling_reference_gate.py — 裁定#NNN<br/>悬空引用检测门禁单测（RULING-REFERE...<br/>文件: commit_gates/test_ruling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_schema_file_exists_gate_py["commit_gates/test_schema_file_exists_gate<br/>test_schema_file_exists_gate.py —<br/>SCHEMA-FILE-EXISTS 门禁单测<br/>文件: commit_gates<br/>/test_schema_file_exists_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py["commit_gates/test_scripts_import_integrity_gate<br/>test_scripts_import_integrity_gate.py —<br/>SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>文件: commit_gates<br/>/test_scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_session_required_gate_py["commit_gates/test_session_required_gate<br/>test_session_required_gate.py —<br/>SESSION-REQUIRED 门禁单测<br/>文件: commit_gates/test_session_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ssot_redefinition_gate_py["commit_gates/test_ssot_redefinition_gate<br/>test_ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁单测（SSOT-REDEF...<br/>文件: commit_gates<br/>/test_ssot_redefinition_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_test_source_consistency_gate_py["commit_gates/test_test_source_consistency_gate<br/>test_test_source_consistency_gate.py —<br/>TEST-SOURCE-CONSISTENCY 门禁单测<br/>文件: commit_gates<br/>/test_test_source_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_translation_coverage_gate_py["commit_gates/test_translation_coverage_gate<br/>test_translation_coverage_gate.py —<br/>TRANSLATION-COVERAGE 门禁单测<br/>文件: commit_gates<br/>/test_translation_coverage_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_undefined_name_gate_py["commit_gates/test_undefined_name_gate<br/>test_undefined_name_gate.py — UNDEFINED-NAME<br/>门禁单测<br/>文件: commit_gates/test_undefined_name_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py["commit_gates/test_unsafe_dict_spread_gate<br/>test_unsafe_dict_spread_gate.py — ``**data``<br/>直接展开 warn 级门禁单测（UNSAF...<br/>文件: commit_gates<br/>/test_unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_vocab_hardcode_gate_py["commit_gates/test_vocab_hardcode_gate<br/>test_vocab_hardcode_gate.py — VOCAB-HARDCODE<br/>门禁单测<br/>文件: commit_gates/test_vocab_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py["commit_gates/test_zephyr_env_direct_access_gate<br/>test_zephyr_env_direct_access_gate.py —<br/>ZEPHYR_ENV 直访硬阻断门禁单测（ZEPHY...<br/>文件: commit_gates<br/>/test_zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["rule_bridge/test_claim_files_for_edit<br/>test_claim_files_for_edit.py — P2-2 并发<br/>session 文件级原子性测试<br/>文件: rule_bridge/test_claim_files_for_edit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_commit_gate_registry_py["rule_bridge/test_commit_gate_registry<br/>test_commit_gate_registry.py —<br/>CommitGateRegistry 单测（架构债务 #AD-001 治本）<br/>文件: rule_bridge/test_commit_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_emergency_commit_py["rule_bridge/test_emergency_commit<br/>test_emergency_commit.py — emergency_commit API<br/>测试（Ruling:100PCT-AI-GOVER...<br/>文件: rule_bridge/test_emergency_commit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_gate_auto_registrar_py["rule_bridge/test_gate_auto_registrar<br/>test_gate_auto_registrar.py —<br/>gate_auto_registrar 单元测试（...<br/>文件: rule_bridge/test_gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["rule_bridge/test_heartbeat_daemon<br/>test_heartbeat_daemon.py — heartbeat daemon +<br/>成本递增 smoke test（Ruling:10...<br/>文件: rule_bridge/test_heartbeat_daemon.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_py["rule_bridge/test_session_worktree<br/>test_session_worktree.py — worktree<br/>物理隔离端到端测试（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/test_session_worktree.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_cli_py["rule_bridge/test_session_worktree_cli<br/>test_session_worktree_cli.py —<br/>session_worktree_cli CLI 测试（治本遗留项#2, ...<br/>文件: rule_bridge/test_session_worktree_cli.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_health_check_py["rule_bridge/test_session_worktree_health_check<br/>test_session_worktree_health_check.py —<br/>session_worktree_start 启动健康度自...<br/>文件: rule_bridge<br/>/test_session_worktree_health_check.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py["rule_bridge<br/>/test_session_worktree_trusted_git_env<br/>test_session_worktree_trusted_git_env.py —<br/>_trusted_git_env 进程级隔离单测（...<br/>文件: rule_bridge<br/>/test_session_worktree_trusted_git_env.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py["rule_bridge<br/>/test_session_worktree_workspace_clean<br/>test_session_worktree_workspace_clean.py —<br/>session lifecycle 工作区 clean 检...<br/>文件: rule_bridge<br/>/test_session_worktree_workspace_clean.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_pool_py["rule_bridge/test_worktree_pool<br/>test_worktree_pool.py — WorktreePool 端到端<br/>smoke test（ARCH-GIT-CALL-BUDGET...<br/>文件: rule_bridge/test_worktree_pool.py<br/>(生产态 / production)"]
    tests_ops_test_shadow_canary_deploy_py["ops/test_shadow_canary_deploy<br/>test_shadow_canary_deploy.py — Shadow Canary<br/>部署运行器单元测试<br/>文件: ops/test_shadow_canary_deploy.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml ~~~ scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py ~~~ scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py ~~~ scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py ~~~ scripts_governance_session_worktree_cli_py
    scripts_governance_session_worktree_cli_py ~~~ src_zephyr_gov_enforcement_init_py
    src_zephyr_gov_enforcement_init_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_init_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py ~~~ src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_approval_py
    src_zephyr_gov_enforcement_rule_enforcement_approval_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py ~~~ tests_governance_commit_gates_test_arch_reference_gate_py
    tests_governance_commit_gates_test_arch_reference_gate_py ~~~ tests_governance_commit_gates_test_asyncio_run_in_context_gate_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py ~~~ tests_governance_commit_gates_test_bare_getenv_gate_py
    tests_governance_commit_gates_test_bare_getenv_gate_py ~~~ tests_governance_commit_gates_test_bare_sql_gate_py
    tests_governance_commit_gates_test_bare_sql_gate_py ~~~ tests_governance_commit_gates_test_bare_subprocess_gate_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py ~~~ tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py ~~~ tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py ~~~ tests_governance_commit_gates_test_capability_lookup_audit_log_py
    tests_governance_commit_gates_test_capability_lookup_audit_log_py ~~~ tests_governance_commit_gates_test_capability_lookup_bypass_policy_py
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py ~~~ tests_governance_commit_gates_test_capability_lookup_required_gate_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py ~~~ tests_governance_commit_gates_test_capability_overlap_gate_py
    tests_governance_commit_gates_test_capability_overlap_gate_py ~~~ tests_governance_commit_gates_test_ch_batch_size_gate_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py ~~~ tests_governance_commit_gates_test_ch_version_col_gate_py
    tests_governance_commit_gates_test_ch_version_col_gate_py ~~~ tests_governance_commit_gates_test_claim_required_gate_py
    tests_governance_commit_gates_test_claim_required_gate_py ~~~ tests_governance_commit_gates_test_consumers_accuracy_gate_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py ~~~ tests_governance_commit_gates_test_create_guard_py
    tests_governance_commit_gates_test_create_guard_py ~~~ tests_governance_commit_gates_test_dangling_reference_gate_py
    tests_governance_commit_gates_test_dangling_reference_gate_py ~~~ tests_governance_commit_gates_test_datetime_now_forbidden_gate_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py ~~~ tests_governance_commit_gates_test_depgraph_freshness_gate_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py ~~~ tests_governance_commit_gates_test_depgraph_pre_registration_gate_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py ~~~ tests_governance_commit_gates_test_derived_file_deletion_gate_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py ~~~ tests_governance_commit_gates_test_diff_helpers_py
    tests_governance_commit_gates_test_diff_helpers_py ~~~ tests_governance_commit_gates_test_doc_ref_broken_gate_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py ~~~ tests_governance_commit_gates_test_domain_fk_gate_py
    tests_governance_commit_gates_test_domain_fk_gate_py ~~~ tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py ~~~ tests_governance_commit_gates_test_empty_handler_gate_py
    tests_governance_commit_gates_test_empty_handler_gate_py ~~~ tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py ~~~ tests_governance_commit_gates_test_file_copy_gate_py
    tests_governance_commit_gates_test_file_copy_gate_py ~~~ tests_governance_commit_gates_test_foreign_change_gate_py
    tests_governance_commit_gates_test_foreign_change_gate_py ~~~ tests_governance_commit_gates_test_forged_gw_marker_gate_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py ~~~ tests_governance_commit_gates_test_function_dup_gate_py
    tests_governance_commit_gates_test_function_dup_gate_py ~~~ tests_governance_commit_gates_test_god_class_gate_py
    tests_governance_commit_gates_test_god_class_gate_py ~~~ tests_governance_commit_gates_test_hardcoded_url_gate_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py ~~~ tests_governance_commit_gates_test_held_overlap_gate_py
    tests_governance_commit_gates_test_held_overlap_gate_py ~~~ tests_governance_commit_gates_test_high_complexity_gate_py
    tests_governance_commit_gates_test_high_complexity_gate_py ~~~ tests_governance_commit_gates_test_id_uniqueness_gate_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py ~~~ tests_governance_commit_gates_test_import_direction_gate_py
    tests_governance_commit_gates_test_import_direction_gate_py ~~~ tests_governance_commit_gates_test_import_integrity_gate_py
    tests_governance_commit_gates_test_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_long_param_list_gate_py
    tests_governance_commit_gates_test_long_param_list_gate_py ~~~ tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py ~~~ tests_governance_commit_gates_test_mcp_version_field_gate_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py ~~~ tests_governance_commit_gates_test_module_id_consistency_gate_py
    tests_governance_commit_gates_test_module_id_consistency_gate_py ~~~ tests_governance_commit_gates_test_msg_exposure_gate_py
    tests_governance_commit_gates_test_msg_exposure_gate_py ~~~ tests_governance_commit_gates_test_msg_style_gate_py
    tests_governance_commit_gates_test_msg_style_gate_py ~~~ tests_governance_commit_gates_test_mutable_const_without_final_gate_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py ~~~ tests_governance_commit_gates_test_new_file_depgraph_gate_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py ~~~ tests_governance_commit_gates_test_no_import_side_effect_gate_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py ~~~ tests_governance_commit_gates_test_open_without_with_gate_py
    tests_governance_commit_gates_test_open_without_with_gate_py ~~~ tests_governance_commit_gates_test_orphan_module_gate_py
    tests_governance_commit_gates_test_orphan_module_gate_py ~~~ tests_governance_commit_gates_test_panorama_alignment_gate_py
    tests_governance_commit_gates_test_panorama_alignment_gate_py ~~~ tests_governance_commit_gates_test_perm_trigger_gate_py
    tests_governance_commit_gates_test_perm_trigger_gate_py ~~~ tests_governance_commit_gates_test_precommit_offline_gate_py
    tests_governance_commit_gates_test_precommit_offline_gate_py ~~~ tests_governance_commit_gates_test_protected_paths_gate_py
    tests_governance_commit_gates_test_protected_paths_gate_py ~~~ tests_governance_commit_gates_test_r5_digit_suffix_gate_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py ~~~ tests_governance_commit_gates_test_reconciler_health_gate_py
    tests_governance_commit_gates_test_reconciler_health_gate_py ~~~ tests_governance_commit_gates_test_rename_depgraph_sync_gate_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py ~~~ tests_governance_commit_gates_test_rule_execution_pairing_gate_py
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py ~~~ tests_governance_commit_gates_test_rule_four_way_alignment_gate_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py ~~~ tests_governance_commit_gates_test_ruling_commit_verified_gate_py
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py ~~~ tests_governance_commit_gates_test_ruling_reference_gate_py
    tests_governance_commit_gates_test_ruling_reference_gate_py ~~~ tests_governance_commit_gates_test_schema_file_exists_gate_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py ~~~ tests_governance_commit_gates_test_scripts_import_integrity_gate_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_session_required_gate_py
    tests_governance_commit_gates_test_session_required_gate_py ~~~ tests_governance_commit_gates_test_ssot_redefinition_gate_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py ~~~ tests_governance_commit_gates_test_test_source_consistency_gate_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py ~~~ tests_governance_commit_gates_test_translation_coverage_gate_py
    tests_governance_commit_gates_test_translation_coverage_gate_py ~~~ tests_governance_commit_gates_test_undefined_name_gate_py
    tests_governance_commit_gates_test_undefined_name_gate_py ~~~ tests_governance_commit_gates_test_unsafe_dict_spread_gate_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py ~~~ tests_governance_commit_gates_test_vocab_hardcode_gate_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py ~~~ tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py ~~~ tests_governance_rule_bridge_test_claim_files_for_edit_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py ~~~ tests_governance_rule_bridge_test_commit_gate_registry_py
    tests_governance_rule_bridge_test_commit_gate_registry_py ~~~ tests_governance_rule_bridge_test_emergency_commit_py
    tests_governance_rule_bridge_test_emergency_commit_py ~~~ tests_governance_rule_bridge_test_gate_auto_registrar_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py ~~~ tests_governance_rule_bridge_test_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py ~~~ tests_governance_rule_bridge_test_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_py ~~~ tests_governance_rule_bridge_test_session_worktree_cli_py
    tests_governance_rule_bridge_test_session_worktree_cli_py ~~~ tests_governance_rule_bridge_test_session_worktree_health_check_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py ~~~ tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py ~~~ tests_governance_rule_bridge_test_session_worktree_workspace_clean_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py ~~~ tests_governance_rule_bridge_test_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py ~~~ tests_ops_test_shadow_canary_deploy_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["behavioral_admission/admission_response<br/>behavioral admission包的admission_response模块<br/>文件: behavioral_admission/admission_response.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["behavioral_admission/code_review_ai<br/>behavioral admission包的code_review_ai模块<br/>文件: behavioral_admission/code_review_ai.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["behavioral_admission/gate_event_adapter<br/>GateEventAdapter — GateRepo 事件适配器<br/>（DW-0006）<br/>文件: behavioral_admission/gate_event_adapter.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["behavioral_admission/gpu_consensus_scheduler<br/>behavioral<br/>admission包的gpu_consensus_scheduler模块<br/>文件: behavioral_admission<br/>/gpu_consensus_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["behavioral_admission/protection_index<br/>behavioral admission包的protection_index模块<br/>文件: behavioral_admission/protection_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["rule_bridge/commit_gate_registry<br/>commit_gate_registry.py — GitCommitGateway<br/>pre-commit 门禁注册表（架构债务 #...<br/>文件: rule_bridge/commit_gate_registry.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["rule_bridge/session_worktree<br/>session_worktree.py — AI 对话 worktree 物理隔离<br/>helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["rule_enforcement/quality_gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["behavioral_admission/admission_controller<br/>behavioral admission包的admission_controller模块<br/>文件: behavioral_admission<br/>/admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["behavioral_admission/verdict_engine<br/>behavioral admission包的verdict_engine模块<br/>文件: behavioral_admission/verdict_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["rule_bridge/emergency_commit<br/>emergency_commit.py — 紧急提交通道<br/>（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>文件: rule_bridge/emergency_commit.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["rule_bridge/heartbeat_daemon<br/>heartbeat_daemon.py — session heartbeat<br/>独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>文件: rule_bridge/heartbeat_daemon.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["rule_bridge/session_claim<br/>session_claim.py — AI 对话并发声明 helper<br/>（FP-ISO.4B 件2改，2026-07-01 治本）<br/>文件: rule_bridge/session_claim.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["rule_bridge/worktree_manager<br/>worktree_manager.py — session worktree<br/>物理隔离管理器（阶段3 治本 stash 循环）<br/>文件: rule_bridge/worktree_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["rule_bridge/worktree_pool<br/>worktree_pool.py — Worktree 预创建池<br/>（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>文件: rule_bridge/worktree_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["rule_bridge/git_commit_gateway<br/>GitCommitGateway — 全项目唯一合法 git commit<br/>入口（OPS-2026062512 治本）<br/>文件: rule_bridge/git_commit_gateway.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["rule_bridge/batched_auto_committer<br/>batched_auto_committer.py — Reconciler 批量化<br/>auto-commit 拦截器（ARCH-GIT-C...<br/>文件: rule_bridge/batched_auto_committer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_getenv_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_sql_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_claim_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_version_col_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_empty_handler_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_fk_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_file_copy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_function_dup_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_held_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_high_complexity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_direction_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_god_class_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_long_param_list_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_exposure_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_style_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_open_without_with_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_orphan_module_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_precommit_offline_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_perm_trigger_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_protected_paths_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_reconciler_health_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_session_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_undefined_name_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_translation_coverage_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_rule_bridge_test_commit_gate_registry_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_arch_reference_gate_py,tests_governance_commit_gates_test_asyncio_run_in_context_gate_py,tests_governance_commit_gates_test_bare_getenv_gate_py,tests_governance_commit_gates_test_bare_sql_gate_py,tests_governance_commit_gates_test_bare_subprocess_gate_py,tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py,tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py,tests_governance_commit_gates_test_capability_lookup_audit_log_py,tests_governance_commit_gates_test_capability_lookup_bypass_policy_py,tests_governance_commit_gates_test_capability_lookup_required_gate_py,tests_governance_commit_gates_test_capability_overlap_gate_py,tests_governance_commit_gates_test_ch_batch_size_gate_py,tests_governance_commit_gates_test_ch_version_col_gate_py,tests_governance_commit_gates_test_claim_required_gate_py,tests_governance_commit_gates_test_consumers_accuracy_gate_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_dangling_reference_gate_py,tests_governance_commit_gates_test_datetime_now_forbidden_gate_py,tests_governance_commit_gates_test_depgraph_freshness_gate_py,tests_governance_commit_gates_test_depgraph_pre_registration_gate_py,tests_governance_commit_gates_test_derived_file_deletion_gate_py,tests_governance_commit_gates_test_diff_helpers_py,tests_governance_commit_gates_test_doc_ref_broken_gate_py,tests_governance_commit_gates_test_domain_fk_gate_py,tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py,tests_governance_commit_gates_test_empty_handler_gate_py,tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py,tests_governance_commit_gates_test_file_copy_gate_py,tests_governance_commit_gates_test_foreign_change_gate_py,tests_governance_commit_gates_test_forged_gw_marker_gate_py,tests_governance_commit_gates_test_function_dup_gate_py,tests_governance_commit_gates_test_god_class_gate_py,tests_governance_commit_gates_test_hardcoded_url_gate_py,tests_governance_commit_gates_test_held_overlap_gate_py,tests_governance_commit_gates_test_high_complexity_gate_py,tests_governance_commit_gates_test_id_uniqueness_gate_py,tests_governance_commit_gates_test_import_direction_gate_py,tests_governance_commit_gates_test_import_integrity_gate_py,tests_governance_commit_gates_test_long_param_list_gate_py,tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py,tests_governance_commit_gates_test_mcp_version_field_gate_py,tests_governance_commit_gates_test_module_id_consistency_gate_py,tests_governance_commit_gates_test_msg_exposure_gate_py,tests_governance_commit_gates_test_msg_style_gate_py,tests_governance_commit_gates_test_mutable_const_without_final_gate_py,tests_governance_commit_gates_test_new_file_depgraph_gate_py,tests_governance_commit_gates_test_no_import_side_effect_gate_py,tests_governance_commit_gates_test_open_without_with_gate_py,tests_governance_commit_gates_test_orphan_module_gate_py,tests_governance_commit_gates_test_panorama_alignment_gate_py,tests_governance_commit_gates_test_perm_trigger_gate_py,tests_governance_commit_gates_test_precommit_offline_gate_py,tests_governance_commit_gates_test_protected_paths_gate_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_commit_gates_test_reconciler_health_gate_py,tests_governance_commit_gates_test_rename_depgraph_sync_gate_py,tests_governance_commit_gates_test_rule_execution_pairing_gate_py,tests_governance_commit_gates_test_rule_four_way_alignment_gate_py,tests_governance_commit_gates_test_ruling_commit_verified_gate_py,tests_governance_commit_gates_test_ruling_reference_gate_py,tests_governance_commit_gates_test_schema_file_exists_gate_py,tests_governance_commit_gates_test_scripts_import_integrity_gate_py,tests_governance_commit_gates_test_session_required_gate_py,tests_governance_commit_gates_test_ssot_redefinition_gate_py,tests_governance_commit_gates_test_test_source_consistency_gate_py,tests_governance_commit_gates_test_translation_coverage_gate_py,tests_governance_commit_gates_test_undefined_name_gate_py,tests_governance_commit_gates_test_unsafe_dict_spread_gate_py,tests_governance_commit_gates_test_vocab_hardcode_gate_py,tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_commit_gate_registry_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_gate_auto_registrar_py,tests_governance_rule_bridge_test_heartbeat_daemon_py,tests_governance_rule_bridge_test_session_worktree_py,tests_governance_rule_bridge_test_session_worktree_cli_py,tests_governance_rule_bridge_test_session_worktree_health_check_py,tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py,tests_governance_rule_bridge_test_session_worktree_workspace_clean_py,tests_governance_rule_bridge_test_worktree_pool_py,tests_ops_test_shadow_canary_deploy_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_ops_shadow_canary_deploy_py["影子金丝雀部署运行器<br/>把 4 个已有零件串成一条命令，做灰度发布的安全网<br/>：先检查能不能上线，再开个影子进程跑同样的输入但<br/>不接真券商，然后比对两边输出是否一致，分歧小就放<br/>行、分歧大就回滚。专门满足 EX-021 那半 CI/CD<br/>灰度门禁。<br/>Shadow Canary Deploy Runner<br/>Shadow Canary deploy runner orchestrating<br/>precheck/shadow/compare/state-machine,<br/>satisfying EX-021 CI/CD gate half<br/>文件: ops/shadow_canary_deploy.py<br/>(设计态 / design)"]
    src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py["重置网关<br/>统一拦截 git reset/restore/checkout--<br/>危险命令的治理入口，三段式防护：自伤检测→锁冲突<br/>检测→审计落盘，对标 GitCommitGateway 对 commit<br/>的治理<br/>文件: rule_bridge/reset_gateway.py<br/>(设计态 / design)"]
    scripts_ops_shadow_canary_deploy_py ~~~ src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_ops_shadow_canary_deploy_py,src_zephyr_gov_enforcement_rule_bridge_reset_gateway_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_AUTONOMY_CORE 自治核心: 影子金丝雀 / shadow_canary (context/shadow_canary.py) | 导入依赖 / import_depends |
| 2 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | 导入依赖 / import_depends |
| 3 | behavioral_admission/__init__.py | → | D_GOVERNANCE 生命周期管理: worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | 导入依赖 / import_depends |
| 4 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 5 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 6 | test_capability_lookup_audit_log.py — capability_lookup ... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 7 | test_capability_overlap_gate.py — CAPABILITY-OVERLAP 门... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 8 | test_new_file_depgraph_gate.py — NEW-FILE-DEPGRAPH-ENFOR... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 测试依赖 / test_depends |
| 9 | test_ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 10 | metric_count_drift_reconciler.py — dashboard 指标数描述... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 11 | readme_version_sync_reconciler.py — README 版本号派生展... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 12 | requirements_version_sync_reconciler.py — requirements.t... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 13 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: MCP结果推送 / mcp_result_push (behavioral_admission/mcp_r... | 导入依赖 / import_depends |
| 14 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: 提交进程 / post_process (behavioral_admission/post_proces... | 导入依赖 / import_depends |
| 15 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: vibecoding执行器 / vibe_coding_enforcer (behavioral_admis... | 导入依赖 / import_depends |
| 16 | GateEventAdapter — GateRepo 事件适配器（DW-0006） (behav... | → | D_GOV_AUDIT 审计追踪: 事件存储 / event_store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 17 | behavioral_admission/verdict_engine.py | → | D_GOV_AUDIT 审计追踪: 审计事件类型枚举——治本（裁定#18 G2）：转为真 Enu / mode... | 导入依赖 / import_depends |
| 18 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 19 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 蓝图状态转换协调器 / blueprint_status_transition_reconcil... | 导入依赖 / import_depends |
| 20 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: commitgatewayabuse监控器对账器 / commit_gateway_abuse_mon... | 导入依赖 / import_depends |
| 21 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 跨layercontractsignature对账器 / cross_layer_contract_sig... | 导入依赖 / import_depends |
| 22 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: dead_public_wrapper_reconciler.py — 死公共 wrapper 自动... | 导入依赖 / import_depends |
| 23 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 错误模式消费者协调器 / error_pattern_consumer_reconciler ... | 导入依赖 / import_depends |
| 24 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: git_guard_bypass_reconciler.py — git_guard alias 绕过检... | 导入依赖 / import_depends |
| 25 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: Git绩效监控协调器 / git_performance_monitor_reconciler (a... | 导入依赖 / import_depends |
| 26 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 27 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 28 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 修复进度对账器 / remediation_progress_reconciler (audit/r... | 导入依赖 / import_depends |
| 29 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 运行时违规快照协调器 / runtime_violation_snapshot_reconci... | 导入依赖 / import_depends |
| 30 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: translation_coverage_reconciler.py — 翻译覆盖率存量对账 ... | 导入依赖 / import_depends |
| 31 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 32 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: AI错误模式库 / ai_error_pattern_library (audit/ai_error_p... | 导入依赖 / import_depends |
| 33 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 34 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 35 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 36 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 导入依赖 / import_depends |
| 37 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: 包入口 / __init__ (commit_gates/__init__.py) | 导入依赖 / import_depends |
| 38 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 导入依赖 / import_depends |
| 39 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: test_source_consistency_gate.py — 测试-源码符号一致性门... | 导入依赖 / import_depends |
| 40 | test_arch_reference_gate.py — #ARCH-NNN 悬空引用检测门禁... | → | D_GOV_CODE_QUALITY 代码质量治理: reference辅助 / _reference_helpers (commit_gates/_referen... | 测试依赖 / test_depends |
| 41 | test_arch_reference_gate.py — #ARCH-NNN 悬空引用检测门禁... | → | D_GOV_CODE_QUALITY 代码质量治理: archreference门禁 / arch_reference_gate (commit_gates/arc... | 测试依赖 / test_depends |
| 42 | test_asyncio_run_in_context_gate.py — asyncio API 误用硬... | → | D_GOV_CODE_QUALITY 代码质量治理: asynciorunin上下文门禁 / asyncio_run_in_context_gate (com... | 测试依赖 / test_depends |
| 43 | test_bare_getenv_gate.py — NO-BARE-GETENV 门禁单测 (comm... | → | D_GOV_CODE_QUALITY 代码质量治理: baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | 测试依赖 / test_depends |
| 44 | test_bare_sql_gate.py — NO-BARE-SQL 门禁单测 (commit_gat... | → | D_GOV_CODE_QUALITY 代码质量治理: baresql门禁 / bare_sql_gate (commit_gates/bare_sql_gate.py) | 测试依赖 / test_depends |
| 45 | test_bare_subprocess_gate.py — BARE-SUBPROCESS 门禁单测 ... | → | D_GOV_CODE_QUALITY 代码质量治理: baresubprocess门禁 / bare_subprocess_gate (commit_gates/b... | 测试依赖 / test_depends |
| 46 | test_blueprint_amodule_consistency_gate.py — BLUEPRINT-A... | → | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amoduleconsistency门禁 / blueprint_amodule_consistenc... | 测试依赖 / test_depends |
| 47 | test_blueprint_amodule_cross_check_gate.py — BLUEPRINT-A... | → | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule跨check门禁 / blueprint_amodule_cross_check_ga... | 测试依赖 / test_depends |
| 48 | test_capability_lookup_audit_log.py — capability_lookup ... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 测试依赖 / test_depends |
| 49 | test_capability_lookup_bypass_policy.py — CAPABILITY-LOO... | → | D_GOV_CODE_QUALITY 代码质量治理: 包入口 / __init__ (commit_gates/__init__.py) | 测试依赖 / test_depends |
| 50 | test_capability_lookup_bypass_policy.py — CAPABILITY-LOO... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookup绕过策略 / capability_lookup_bypass_polic... | 测试依赖 / test_depends |
| 51 | test_capability_lookup_required_gate.py — CAPABILITY-LOO... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 测试依赖 / test_depends |
| 52 | test_capability_overlap_gate.py — CAPABILITY-OVERLAP 门... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilityoverlap门禁 / capability_overlap_gate (commit_g... | 测试依赖 / test_depends |
| 53 | test_ch_batch_size_gate.py — CH-BATCH-SIZE 门禁单测 (com... | → | D_GOV_CODE_QUALITY 代码质量治理: ch批次大小门禁 / ch_batch_size_gate (commit_gates/ch_batc... | 测试依赖 / test_depends |
| 54 | test_ch_version_col_gate.py — CH-VERSION-COL 门禁单测 (c... | → | D_GOV_CODE_QUALITY 代码质量治理: ch版本col门禁 / ch_version_col_gate (commit_gates/ch_vers... | 测试依赖 / test_depends |
| 55 | test_claim_required_gate.py — claim_files 前置检查门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: claimrequired门禁 / claim_required_gate (commit_gates/cla... | 测试依赖 / test_depends |
| 56 | test_consumers_accuracy_gate.py — CONSUMERS-ACCURACY 门... | → | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 测试依赖 / test_depends |
| 57 | test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-0... | → | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | 测试依赖 / test_depends |
| 58 | test_dangling_reference_gate.py — AGENTS.md §X.Y 悬空引... | → | D_GOV_CODE_QUALITY 代码质量治理: danglingreference门禁 / dangling_reference_gate (commit_g... | 测试依赖 / test_depends |
| 59 | test_datetime_now_forbidden_gate.py — 生成器代码 datetim... | → | D_GOV_CODE_QUALITY 代码质量治理: datetimenowforbidden门禁 / datetime_now_forbidden_gate (c... | 测试依赖 / test_depends |
| 60 | test_depgraph_freshness_gate.py — DEPGRAPH-FRESHNESS 门... | → | D_GOV_CODE_QUALITY 代码质量治理: depgraphfreshness门禁 / depgraph_freshness_gate (commit_g... | 测试依赖 / test_depends |
| 61 | test_depgraph_pre_registration_gate.py — DEPGRAPH-PRE-RE... | → | D_GOV_CODE_QUALITY 代码质量治理: depgraph_pre_registration_gate.py — depgraph planned→pr... | 测试依赖 / test_depends |
| 62 | test_derived_file_deletion_gate.py — 派生文件删除保护门... | → | D_GOV_CODE_QUALITY 代码质量治理: derived_file_deletion_gate.py — 派生文件删除保护门禁（DE... | 测试依赖 / test_depends |
| 63 | test_diff_helpers.py — gate 共享 diff 解析工具模块单测 (... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 测试依赖 / test_depends |
| 64 | test_doc_ref_broken_gate.py — DOC-REF-BROKEN 门禁单测 (c... | → | D_GOV_CODE_QUALITY 代码质量治理: docrefbroken门禁 / doc_ref_broken_gate (commit_gates/doc_... | 测试依赖 / test_depends |
| 65 | test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测 (commit... | → | D_GOV_CODE_QUALITY 代码质量治理: 域fk门禁 / domain_fk_gate (commit_gates/domain_fk_gate.py) | 测试依赖 / test_depends |
| 66 | test_domain_name_zh_direct_access_gate.py — NO-DOMAIN-NA... | → | D_GOV_CODE_QUALITY 代码质量治理: domainnamezhdirect访问门禁 / domain_name_zh_direct_access... | 测试依赖 / test_depends |
| 67 | test_empty_handler_gate.py — EMPTY-HANDLER 门禁单测 (com... | → | D_GOV_CODE_QUALITY 代码质量治理: empty处理器门禁 / empty_handler_gate (commit_gates/empty_... | 测试依赖 / test_depends |
| 68 | test_exempt_zone_frontmatter_gate.py — EXEMPT-ZONE-FM 门... | → | D_GOV_CODE_QUALITY 代码质量治理: exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | 测试依赖 / test_depends |
| 69 | test_file_copy_gate.py — FILE-COPY 门禁单测 (commit_gate... | → | D_GOV_CODE_QUALITY 代码质量治理: filecopy门禁 / file_copy_gate (commit_gates/file_copy_gat... | 测试依赖 / test_depends |
| 70 | test_foreign_change_gate.py — 外来变更检测门禁单测（FORE... | → | D_GOV_CODE_QUALITY 代码质量治理: foreignchange门禁 / foreign_change_gate (commit_gates/for... | 测试依赖 / test_depends |
| 71 | test_forged_gw_marker_gate.py — Forged GW Marker 前置检... | → | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | 测试依赖 / test_depends |
| 72 | test_function_dup_gate.py — FUNCTION-DUP 门禁单测 (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: 函数dup门禁 / function_dup_gate (commit_gates/function_du... | 测试依赖 / test_depends |
| 73 | test_god_class_gate.py — NO-GOD-CLASS 门禁单测 (commit_g... | → | D_GOV_CODE_QUALITY 代码质量治理: god类门禁 / god_class_gate (commit_gates/god_class_gate.py) | 测试依赖 / test_depends |
| 74 | test_hardcoded_url_gate.py — NO-HARDCODED-URL 门禁单测 (... | → | D_GOV_CODE_QUALITY 代码质量治理: hardcodedurl门禁 / hardcoded_url_gate (commit_gates/hardc... | 测试依赖 / test_depends |
| 75 | test_held_overlap_gate.py — 搭便车防护门禁单测（HELD-OVE... | → | D_GOV_CODE_QUALITY 代码质量治理: heldoverlap门禁 / held_overlap_gate (commit_gates/held_ov... | 测试依赖 / test_depends |
| 76 | test_high_complexity_gate.py — NO-HIGH-COMPLEXITY 门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: highcomplexity门禁 / high_complexity_gate (commit_gates/h... | 测试依赖 / test_depends |
| 77 | test_id_uniqueness_gate.py — ID-UNIQUENESS 门禁单测 (com... | → | D_GOV_CODE_QUALITY 代码质量治理: iduniqueness门禁 / id_uniqueness_gate (commit_gates/id_un... | 测试依赖 / test_depends |
| 78 | test_import_direction_gate.py — NO-UPWARD-IMPORT 门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: importdirection门禁 / import_direction_gate (commit_gates... | 测试依赖 / test_depends |
| 79 | test_import_integrity_gate.py — IMPORT-INTEGRITY 门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | 测试依赖 / test_depends |
| 80 | test_long_param_list_gate.py — NO-LONG-PARAM-LIST 门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: longparamlist门禁 / long_param_list_gate (commit_gates/lo... | 测试依赖 / test_depends |
| 81 | test_manual_only_permanent_gate_noqa.py — MANUAL-ONLY-PE... | → | D_GOV_CODE_QUALITY 代码质量治理: 手册onlypermanent门禁 / manual_only_permanent_gate (commi... | 测试依赖 / test_depends |
| 82 | test_mcp_version_field_gate.py — MCP version 字段缺失硬... | → | D_GOV_CODE_QUALITY 代码质量治理: MCP版本字段门禁 / mcp_version_field_gate (commit_gates/mc... | 测试依赖 / test_depends |
| 83 | test_module_id_consistency_gate.py — module_id 三声明轨... | → | D_GOV_CODE_QUALITY 代码质量治理: 模块id一致性门禁 / module_id_consistency_gate (commit_gat... | 测试依赖 / test_depends |
| 84 | test_msg_exposure_gate.py — MSG-EXPOSURE 门禁单测 (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: msg敞口门禁 / msg_exposure_gate (commit_gates/msg_exposur... | 测试依赖 / test_depends |
| 85 | test_msg_style_gate.py — MSG-STYLE 门禁单测 (commit_gate... | → | D_GOV_CODE_QUALITY 代码质量治理: msgstyle门禁 / msg_style_gate (commit_gates/msg_style_gat... | 测试依赖 / test_depends |
| 86 | test_mutable_const_without_final_gate.py — 可变常量缺 Fi... | → | D_GOV_CODE_QUALITY 代码质量治理: mutableconstwithoutfinal门禁 / mutable_const_without_fina... | 测试依赖 / test_depends |
| 87 | test_new_file_depgraph_gate.py — NEW-FILE-DEPGRAPH-ENFOR... | → | D_GOV_CODE_QUALITY 代码质量治理: 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | 测试依赖 / test_depends |
| 88 | test_no_import_side_effect_gate.py — NO-IMPORT-SIDE-EFFE... | → | D_GOV_CODE_QUALITY 代码质量治理: noimportsideeffect门禁 / no_import_side_effect_gate (comm... | 测试依赖 / test_depends |
| 89 | test_open_without_with_gate.py — open() 未在 with 内硬阻... | → | D_GOV_CODE_QUALITY 代码质量治理: openwithoutwith门禁 / open_without_with_gate (commit_gate... | 测试依赖 / test_depends |
| 90 | test_orphan_module_gate.py — ORPHAN-MODULE 门禁单测 (com... | → | D_GOV_CODE_QUALITY 代码质量治理: 孤儿module门禁 / orphan_module_gate (commit_gates/orphan_... | 测试依赖 / test_depends |
| 91 | test_panorama_alignment_gate.py — 四图模块对齐门禁单测（... | → | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | 测试依赖 / test_depends |
| 92 | test_perm_trigger_gate.py — PERM-TRIGGER 门禁单测 (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: permtrigger门禁 / perm_trigger_gate (commit_gates/perm_tr... | 测试依赖 / test_depends |
| 93 | test_precommit_offline_gate.py — GATE-PRECOMMIT-OFFLINE ... | → | D_GOV_CODE_QUALITY 代码质量治理: precommitoffline门禁 / precommit_offline_gate (commit_gat... | 测试依赖 / test_depends |
| 94 | test_protected_paths_gate.py — 受保护路径写入检测门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: protected_paths_gate.py — 受保护路径写入检测门禁（PROTEC... | 测试依赖 / test_depends |
| 95 | test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元... | → | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | 测试依赖 / test_depends |
| 96 | test_reconciler_health_gate.py — RECONCILER-HEALTH 门禁... | → | D_GOV_CODE_QUALITY 代码质量治理: reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | 测试依赖 / test_depends |
| 97 | test_rename_depgraph_sync_gate.py — RENAME-DEPGRAPH-SYNC... | → | D_GOV_CODE_QUALITY 代码质量治理: rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未... | 测试依赖 / test_depends |
| 98 | Tests for RULE-EXECUTION-PAIRING gate (Phase 3.5). (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE... | 测试依赖 / test_depends |
| 99 | test_rule_four_way_alignment_gate.py — RULE-FOUR-WAY-ALI... | → | D_GOV_CODE_QUALITY 代码质量治理: rule_four_way_alignment_gate.py — 规则四方对齐门禁（RULE... | 测试依赖 / test_depends |
| 100 | test_ruling_commit_verified_gate.py — RULING-COMMIT-VERI... | → | D_GOV_CODE_QUALITY 代码质量治理: ruling_commit_verified_gate.py — 文档"已完成"声明 commit... | 测试依赖 / test_depends |
| 101 | test_ruling_reference_gate.py — 裁定#NNN 悬空引用检测门... | → | D_GOV_CODE_QUALITY 代码质量治理: ruling_reference_gate.py — 裁定#NNN 悬空引用自动检测门禁... | 测试依赖 / test_depends |
| 102 | test_schema_file_exists_gate.py — SCHEMA-FILE-EXISTS 门... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 测试依赖 / test_depends |
| 103 | test_schema_file_exists_gate.py — SCHEMA-FILE-EXISTS 门... | → | D_GOV_CODE_QUALITY 代码质量治理: schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门... | 测试依赖 / test_depends |
| 104 | test_scripts_import_integrity_gate.py — SCRIPTS-IMPORT-I... | → | D_GOV_CODE_QUALITY 代码质量治理: scripts_import_integrity_gate.py — _shared.constants 符... | 测试依赖 / test_depends |
| 105 | test_session_required_gate.py — SESSION-REQUIRED 门禁单... | → | D_GOV_CODE_QUALITY 代码质量治理: session_required_gate.py — session 注册强制门禁（SESSION... | 测试依赖 / test_depends |
| 106 | test_ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断... | → | D_GOV_CODE_QUALITY 代码质量治理: ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁 ... | 测试依赖 / test_depends |
| 107 | test_test_source_consistency_gate.py — TEST-SOURCE-CONSI... | → | D_GOV_CODE_QUALITY 代码质量治理: test_source_consistency_gate.py — 测试-源码符号一致性门... | 测试依赖 / test_depends |
| 108 | test_translation_coverage_gate.py — TRANSLATION-COVERAGE... | → | D_GOV_CODE_QUALITY 代码质量治理: translation_coverage_gate.py — 新建 .py 文件大白话简介覆... | 测试依赖 / test_depends |
| 109 | test_undefined_name_gate.py — UNDEFINED-NAME 门禁单测 (c... | → | D_GOV_CODE_QUALITY 代码质量治理: undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | 测试依赖 / test_depends |
| 110 | test_unsafe_dict_spread_gate.py — ``**data`` 直接展开 wa... | → | D_GOV_CODE_QUALITY 代码质量治理: unsafe_dict_spread_gate.py — ``**data`` 直接展开模式 war... | 测试依赖 / test_depends |
| 111 | test_vocab_hardcode_gate.py — VOCAB-HARDCODE 门禁单测 (c... | → | D_GOV_CODE_QUALITY 代码质量治理: vocab_hardcode_gate.py — 新增 .py 文件词表硬编码阻断门禁... | 测试依赖 / test_depends |
| 112 | test_zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访... | → | D_GOV_CODE_QUALITY 代码质量治理: zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断... | 测试依赖 / test_depends |
| 113 | test_gate_auto_registrar.py — gate_auto_registrar 单元测... | → | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 测试依赖 / test_depends |
| 114 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Phase Manager — ZephyrAlpha 施工阶段门控引擎. (ops_gover... | 导入依赖 / import_depends |
| 115 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_GOV_RULE 规则治理: 预部署门禁 / Can-I-Deploy (rule_enforcement/can_i_deploy.py) | 导入依赖 / import_depends |
| 116 | test_shadow_canary_deploy.py — Shadow Canary 部署运行器... | → | D_GOV_RULE 规则治理: 预部署门禁 / Can-I-Deploy (rule_enforcement/can_i_deploy.py) | 测试依赖 / test_depends |
| 117 | metric_count_drift_reconciler.py — dashboard 指标数描述... | → | D_GOV_SCRIPTS 脚本治理: architecture_health_dashboard.py — 架构健康度仪表盘（自... | 导入依赖 / import_depends |
| 118 | session_worktree_cli.py — session worktree 管理 CLI（治... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 119 | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/compliance_rule.py | 导入依赖 / import_depends |
| 120 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_INFRA_RUNTIME 运行时集成: git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | 导入依赖 / import_depends |
| 121 | G-CT-004 — Backward-compat re-export of ApprovalRequest ... | → | D_INTEGRATION 管线路由: G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请... | 导入依赖 / import_depends |
| 122 | test_capability_lookup_required_gate.py — CAPABILITY-LOO... | → | D_INTEGRATION 管线路由: RuleDiscoveryServer — MCP Server for rule discovery（...... | 测试依赖 / test_depends |
| 123 | rule_enforcement/pre_flight_gate.py | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 124 | rule_enforcement/pre_flight_gate.py | → | D_OPS 反馈循环: Budget Enforcer data models — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 125 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_SECURITY 对抗验证: CanaryRolloutManager — 灰度发布管理器. (access_control/c... | 导入依赖 / import_depends |
| 126 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 127 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SECURITY 对抗验证: CommitTrigger — 事件驱动红蓝对抗触发器 (MOD-INF-030). (a... | 导入依赖 / import_depends |
| 128 | heartbeat_daemon.py — session heartbeat 独立进程（Ruling... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 129 | session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 130 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 131 | test_import_integrity_gate.py — IMPORT-INTEGRITY 门禁单... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 测试依赖 / test_depends |
| 132 | test_claim_files_for_edit.py — P2-2 并发 session 文件级... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 测试依赖 / test_depends |
| 133 | test_session_worktree.py — worktree 物理隔离端到端测试（... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 测试依赖 / test_depends |
| 134 | session_worktree_cli.py — session worktree 管理 CLI（治... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 135 | GateEventAdapter — GateRepo 事件适配器（DW-0006） (behav... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 136 | behavioral_admission/gpu_consensus_scheduler.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 137 | commit_gate_registry.py — GitCommitGateway pre-commit 门... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 138 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 139 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 140 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 141 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 142 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 143 | session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 144 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 145 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 146 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: workspace_telemetry.py — 主工作区文件操作遥测公共 API（.... | 导入依赖 / import_depends |
| 147 | worktree_manager.py — session worktree 物理隔离管理器（... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 148 | worktree_manager.py — session worktree 物理隔离管理器（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 149 | worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDG... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 150 | worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDG... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 151 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: dlq.py —— ZephyrAlpha 死信队列（Dead Letter Queue） (ev... | 导入依赖 / import_depends |
| 152 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emit/unsubscr... | 导入依赖 / import_depends |
| 153 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 154 | RuleWatcher — YAML 规则文件变更检测与自动同步 (rule_engi... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 155 | RuleWatcher — YAML 规则文件变更检测与自动同步 (rule_engi... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 156 | test_gate_auto_registrar.py — gate_auto_registrar 单元测... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 测试依赖 / test_depends |
| 157 | test_session_worktree.py — worktree 物理隔离端到端测试（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 测试依赖 / test_depends |
| 158 | test_worktree_pool.py — WorktreePool 端到端 smoke test（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_DATA 数据接入层: 质量门禁 / quality_gate (data/quality_gate.py) | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 导入依赖 / import_depends |
| 2 | D_DATA 数据接入层: 包入口 / D_DATA Data Source (satellite_geospatial_engine/... | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 导入依赖 / import_depends |
| 3 | D_DATA 数据接入层: #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。 / tes... | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 测试依赖 / test_depends |
| 4 | D_GOVERNANCE 生命周期管理: Git提交 / git_commit (scripts/git_commit.py) | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: 合规管理器 / compliance_manager (compliance_gate_a6/compl... | → | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: 测试会话感知stashredblue / test_session_aware_stash_red_b... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 8 | D_GOVERNANCE 生命周期管理: 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 测试依赖 / test_depends |
| 9 | D_GOVERNANCE 生命周期管理: 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 10 | D_GOVERNANCE 生命周期管理: 测试Gitcommitextreme / test_git_commit_extreme (git/test_... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 11 | D_GOVERNANCE 生命周期管理: 测试Git提交网关 / test_git_commit_gateway (git/test_git_c... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 12 | D_GOVERNANCE 生命周期管理: access_control/test_approval.py | → | G-CT-004 — Backward-compat re-export of ApprovalRequest ... | 测试依赖 / test_depends |
| 13 | D_GOVERNANCE 生命周期管理: test_tests_coverage_gate.py — META-TESTS-COVERAGE meta-g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 测试依赖 / test_depends |
| 14 | D_GOVERNANCE 生命周期管理: Phase E — Akshare 真实数据端到端测试 (data_layer/test_ak... | → | D_DATA — Default Data Quality Gate (rule_enforcement/def... | 测试依赖 / test_depends |
| 15 | D_GOVERNANCE 生命周期管理: integration/test_slo_contract.py | → | SLO-Driven Escalation Contract — D-022-12. (rule_enforce... | 测试依赖 / test_depends |
| 16 | D_GOVERNANCE 生命周期管理: G-CT-004 — Escalation → RBAC 集成测试. (security/test_g... | → | G-CT-004 — Backward-compat re-export of ApprovalRequest ... | 测试依赖 / test_depends |
| 17 | D_GOVERNANCE 生命周期管理: DOM-GOV-001 P0 测试用例 — P0-U1 冒烟测试 + P0-U2 输入校... | → | G-CT-004 — Backward-compat re-export of ApprovalRequest ... | 测试依赖 / test_depends |
| 18 | D_GOVERNANCE 生命周期管理: E2E 集成测试：全流水线贯通测试 (trading/test_e2e_pipeline... | → | D_DATA — Default Data Quality Gate (rule_enforcement/def... | 测试依赖 / test_depends |
| 19 | D_GOVERNANCE 生命周期管理: 测试taskrepogatewaye2e / test_task_repo_gateway_e2e (task... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 20 | D_GOV_AUDIT 审计追踪: Git绩效监控协调器 / git_performance_monitor_reconciler (a... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 21 | D_GOV_AUDIT 审计追踪: 对账工作器 / reconcile_worker (audit/reconcile_worker.py) | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 22 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 23 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 24 | D_GOV_AUDIT 审计追踪: translation_coverage_reconciler.py — 翻译覆盖率存量对账 ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 25 | D_GOV_AUDIT 审计追踪: test_capability_lookup_health_reconciler.py — Phase 4 G6... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 26 | D_GOV_AUDIT 审计追踪: test_integrity_audit_reconciler.py — GATE-INTEGRITY-AUDI... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 27 | D_GOV_AUDIT 审计追踪: 测试对账异步 / test_reconcile_async (audit/test_reconcile... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 28 | D_GOV_AUDIT 审计追踪: 测试对账工作进程selfheal / test_reconcile_worker_selfheal... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 29 | D_GOV_AUDIT 审计追踪: test_stash_lifecycle.py — stash 生命周期治本单测（裁定..... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 30 | D_GOV_AUDIT 审计追踪: 测试会话worktree异步对账 / test_session_worktree_async_re... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 31 | D_GOV_CODE_QUALITY 代码质量治理: reference辅助 / _reference_helpers (commit_gates/_referen... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 32 | D_GOV_CODE_QUALITY 代码质量治理: archreference门禁 / arch_reference_gate (commit_gates/arc... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 33 | D_GOV_CODE_QUALITY 代码质量治理: asynciorunin上下文门禁 / asyncio_run_in_context_gate (com... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 34 | D_GOV_CODE_QUALITY 代码质量治理: baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 35 | D_GOV_CODE_QUALITY 代码质量治理: baresql门禁 / bare_sql_gate (commit_gates/bare_sql_gate.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 36 | D_GOV_CODE_QUALITY 代码质量治理: baresubprocess门禁 / bare_subprocess_gate (commit_gates/b... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 37 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amoduleconsistency门禁 / blueprint_amodule_consistenc... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 38 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule跨check门禁 / blueprint_amodule_cross_check_ga... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 39 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图format门禁 / blueprint_format_gate (commit_gates/blue... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 40 | D_GOV_CODE_QUALITY 代码质量治理: 能力一致性门禁 / capability_consistency_gate (commit_gate... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 41 | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 42 | D_GOV_CODE_QUALITY 代码质量治理: capabilityoverlap门禁 / capability_overlap_gate (commit_g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 43 | D_GOV_CODE_QUALITY 代码质量治理: ch批次大小门禁 / ch_batch_size_gate (commit_gates/ch_batc... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 44 | D_GOV_CODE_QUALITY 代码质量治理: ch最终门禁 / ch_final_gate (commit_gates/ch_final_gate.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 45 | D_GOV_CODE_QUALITY 代码质量治理: ch版本col门禁 / ch_version_col_gate (commit_gates/ch_vers... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 46 | D_GOV_CODE_QUALITY 代码质量治理: claimrequired门禁 / claim_required_gate (commit_gates/cla... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 47 | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 48 | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 49 | D_GOV_CODE_QUALITY 代码质量治理: danglingreference门禁 / dangling_reference_gate (commit_g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 50 | D_GOV_CODE_QUALITY 代码质量治理: 数据taskcompleteness门禁 / data_task_completeness_gate (c... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 51 | D_GOV_CODE_QUALITY 代码质量治理: datetimenowforbidden门禁 / datetime_now_forbidden_gate (c... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 52 | D_GOV_CODE_QUALITY 代码质量治理: depgraphfreshness门禁 / depgraph_freshness_gate (commit_g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 53 | D_GOV_CODE_QUALITY 代码质量治理: depgraph_pre_registration_gate.py — depgraph planned→pr... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 54 | D_GOV_CODE_QUALITY 代码质量治理: depgraphwritepath门禁 / depgraph_write_path_gate (commit_... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: derivationannotation门禁 / derivation_annotation_gate (co... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 56 | D_GOV_CODE_QUALITY 代码质量治理: derived_file_deletion_gate.py — 派生文件删除保护门禁（DE... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 57 | D_GOV_CODE_QUALITY 代码质量治理: directorycontract门禁 / directory_contract_gate (commit_g... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 58 | D_GOV_CODE_QUALITY 代码质量治理: docrefbroken门禁 / doc_ref_broken_gate (commit_gates/doc_... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 59 | D_GOV_CODE_QUALITY 代码质量治理: 域fk门禁 / domain_fk_gate (commit_gates/domain_fk_gate.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 60 | D_GOV_CODE_QUALITY 代码质量治理: domainnamezhdirect访问门禁 / domain_name_zh_direct_access... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 61 | D_GOV_CODE_QUALITY 代码质量治理: empty处理器门禁 / empty_handler_gate (commit_gates/empty_... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 62 | D_GOV_CODE_QUALITY 代码质量治理: encoding门禁 / encoding_gate (commit_gates/encoding_gate.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 63 | D_GOV_CODE_QUALITY 代码质量治理: exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 64 | D_GOV_CODE_QUALITY 代码质量治理: filecopy门禁 / file_copy_gate (commit_gates/file_copy_gat... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 65 | D_GOV_CODE_QUALITY 代码质量治理: fileplacementttl门禁 / file_placement_ttl_gate (commit_ga... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 66 | D_GOV_CODE_QUALITY 代码质量治理: folder容量hardlimit门禁 / folder_capacity_hard_limit_gate... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 67 | D_GOV_CODE_QUALITY 代码质量治理: foreignchange门禁 / foreign_change_gate (commit_gates/for... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 68 | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 69 | D_GOV_CODE_QUALITY 代码质量治理: 函数dup门禁 / function_dup_gate (commit_gates/function_du... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 70 | D_GOV_CODE_QUALITY 代码质量治理: Gitcall预算门禁 / git_call_budget_gate (commit_gates/git_... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 71 | D_GOV_CODE_QUALITY 代码质量治理: god类门禁 / god_class_gate (commit_gates/god_class_gate.py) | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 72 | D_GOV_CODE_QUALITY 代码质量治理: hardcodedurl门禁 / hardcoded_url_gate (commit_gates/hardc... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 73 | D_GOV_CODE_QUALITY 代码质量治理: heldoverlap门禁 / held_overlap_gate (commit_gates/held_ov... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 74 | D_GOV_CODE_QUALITY 代码质量治理: highcomplexity门禁 / high_complexity_gate (commit_gates/h... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 75 | D_GOV_CODE_QUALITY 代码质量治理: iduniqueness门禁 / id_uniqueness_gate (commit_gates/id_un... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 76 | D_GOV_CODE_QUALITY 代码质量治理: importdirection门禁 / import_direction_gate (commit_gates... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 77 | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 78 | D_GOV_CODE_QUALITY 代码质量治理: issueresolved完整性门禁 / issue_resolved_integrity_gate (... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 79 | D_GOV_CODE_QUALITY 代码质量治理: longparamlist门禁 / long_param_list_gate (commit_gates/lo... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 80 | D_GOV_CODE_QUALITY 代码质量治理: 手册onlypermanent门禁 / manual_only_permanent_gate (commi... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 81 | D_GOV_CODE_QUALITY 代码质量治理: MCP版本字段门禁 / mcp_version_field_gate (commit_gates/mc... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 82 | D_GOV_CODE_QUALITY 代码质量治理: 模块id一致性门禁 / module_id_consistency_gate (commit_gat... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 83 | D_GOV_CODE_QUALITY 代码质量治理: msg敞口门禁 / msg_exposure_gate (commit_gates/msg_exposur... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 84 | D_GOV_CODE_QUALITY 代码质量治理: msgstyle门禁 / msg_style_gate (commit_gates/msg_style_gat... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 85 | D_GOV_CODE_QUALITY 代码质量治理: mutableconstwithoutfinal门禁 / mutable_const_without_fina... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 86 | D_GOV_CODE_QUALITY 代码质量治理: 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 87 | D_GOV_CODE_QUALITY 代码质量治理: noimportsideeffect门禁 / no_import_side_effect_gate (comm... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 88 | D_GOV_CODE_QUALITY 代码质量治理: noqa验证门禁 / noqa_validation_gate (commit_gates/noqa_va... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 89 | D_GOV_CODE_QUALITY 代码质量治理: openwithoutwith门禁 / open_without_with_gate (commit_gate... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 90 | D_GOV_CODE_QUALITY 代码质量治理: 孤儿module门禁 / orphan_module_gate (commit_gates/orphan_... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 91 | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 92 | D_GOV_CODE_QUALITY 代码质量治理: permtrigger门禁 / perm_trigger_gate (commit_gates/perm_tr... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 93 | D_GOV_CODE_QUALITY 代码质量治理: precommitoffline门禁 / precommit_offline_gate (commit_gat... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 94 | D_GOV_CODE_QUALITY 代码质量治理: protected_paths_gate.py — 受保护路径写入检测门禁（PROTEC... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 95 | D_GOV_CODE_QUALITY 代码质量治理: pureassertion门禁 / pure_assertion_gate (commit_gates/pur... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 96 | D_GOV_CODE_QUALITY 代码质量治理: pureshim门禁 / pure_shim_gate (commit_gates/pure_shim_gat... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 97 | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 98 | D_GOV_CODE_QUALITY 代码质量治理: reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 99 | D_GOV_CODE_QUALITY 代码质量治理: relative_path_literal_gate.py — 相对路径字面量硬阻断门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 100 | D_GOV_CODE_QUALITY 代码质量治理: rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 101 | D_GOV_CODE_QUALITY 代码质量治理: rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 102 | D_GOV_CODE_QUALITY 代码质量治理: rule_four_way_alignment_gate.py — 规则四方对齐门禁（RULE... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 103 | D_GOV_CODE_QUALITY 代码质量治理: ruling_commit_verified_gate.py — 文档"已完成"声明 commit... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 104 | D_GOV_CODE_QUALITY 代码质量治理: ruling_reference_gate.py — 裁定#NNN 悬空引用自动检测门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 105 | D_GOV_CODE_QUALITY 代码质量治理: schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 106 | D_GOV_CODE_QUALITY 代码质量治理: scripts_import_integrity_gate.py — _shared.constants 符... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 107 | D_GOV_CODE_QUALITY 代码质量治理: session_required_gate.py — session 注册强制门禁（SESSION... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 108 | D_GOV_CODE_QUALITY 代码质量治理: snapshot_drift_gate.py — 运行时违规快照漂移阻断门禁（SNA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 109 | D_GOV_CODE_QUALITY 代码质量治理: ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁 ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 110 | D_GOV_CODE_QUALITY 代码质量治理: table_name_registry_gate.py — TABLE-NAME-REGISTRY block ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 111 | D_GOV_CODE_QUALITY 代码质量治理: test_source_consistency_gate.py — 测试-源码符号一致性门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 112 | D_GOV_CODE_QUALITY 代码质量治理: tests_coverage_gate.py — Gate 测试覆盖率校验 meta-gate（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 113 | D_GOV_CODE_QUALITY 代码质量治理: translation_coverage_gate.py — 新建 .py 文件大白话简介覆... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 114 | D_GOV_CODE_QUALITY 代码质量治理: ttl_gate.py — ttl 字段校验门禁（治本：弥补 --no-verify ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 115 | D_GOV_CODE_QUALITY 代码质量治理: undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 116 | D_GOV_CODE_QUALITY 代码质量治理: unsafe_dict_spread_gate.py — ``**data`` 直接展开模式 war... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 117 | D_GOV_CODE_QUALITY 代码质量治理: vocab_chain_gate.py — SSoT 引用硬编码阻断门禁（VOCAB-CHA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 118 | D_GOV_CODE_QUALITY 代码质量治理: vocab_hardcode_gate.py — 新增 .py 文件词表硬编码阻断门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 119 | D_GOV_CODE_QUALITY 代码质量治理: zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 120 | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 121 | D_GOV_CODE_QUALITY 代码质量治理: rule_enforcement/test_output_quality_gate.py | → | rule_enforcement/output_quality_gate.py | 测试依赖 / test_depends |
| 122 | D_GOV_CODE_QUALITY 代码质量治理: test_audit_worktree_ops_telemetry.py — worktree_ops_log ... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 123 | D_GOV_DRIFT 漂移检测: Tamper-Proof Audit — 防篡改审计 D-023-37 · §6.26。 (go... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 124 | D_GOV_OPS_RESILIENCE 运维弹性治理: D_COMPLIANCE — Governance & Compliance Layer (security_g... | → | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | 导入依赖 / import_depends |
| 125 | D_GOV_OPS_RESILIENCE 运维弹性治理: budget/test_pre_flight_gate.py | → | rule_enforcement/pre_flight_gate.py | 测试依赖 / test_depends |
| 126 | D_GOV_RULE 规则治理: 规则引擎模块集 / Rule Engine Package (rule_engine/__init_... | → | Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规... | config_depends / config_depends |
| 127 | D_GOV_SCRIPTS 脚本治理: concurrent_commit_test.py — 幽灵提交红蓝对抗脚本（OPS-20... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 128 | D_ML_TRAIN 训练: training_dataset_manager/ | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | data / data |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 16 个外部域直接连接（出边 158 条 + 入边 128 条 = 286 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_ENFORCEMENT -->|78条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_GOV_ENFORCEMENT -->|26条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_ENFORCEMENT -->|25条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SHARED
    D_GOV_ENFORCEMENT -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_GOV_ENFORCEMENT -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_RULE
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INTEGRATION
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_OPS
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_CODE_QUALITY -->|92条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|16条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT -->|11条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_DATA -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_OPS_RESILIENCE -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_ML_TRAIN -->|1条 data / data| D_GOV_ENFORCEMENT
    D_GOV_DRIFT -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_RULE -->|1条 config_depends / config_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
