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
| 模块数 | 122 | Module Count | 122 |
| 域内依赖 | 104 | Internal Dependencies | 104 |
| 跨域入边 | 135 | Cross-domain Incoming | 135 |
| 跨域出边 | 161 | Cross-domain Outgoing | 161 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 121 | Production Modules | 121 |
| 容量 | 121/150 (正常) | Capacity | 121/150 (正常) |
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

> 展示全部 122 个模块（生产态 121 + 设计态 1），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml["Rule Enforcement Registry<br/>catalogs包的rule_enforcement_registry模块<br/>文件: catalogs/rule_enforcement_registry.yaml<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["dashboard 指标数描述派生校验 reconciler<br/>metric_count_drift_reconciler.py — dashboard<br/>指标数描述派生校验 reconciler<br/>Metric Count Drift Reconciler<br/>文件: d8_doc_sync<br/>/metric_count_drift_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["README 版本号派生展示校验 reconciler<br/>readme_version_sync_reconciler.py — README<br/>版本号派生展示校验 reconciler<br/>Readme Version Sync Reconciler<br/>文件: d8_doc_sync<br/>/readme_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["requirements.txt ↔ pyproject.toml<br/>依赖一致性校验 reconciler<br/>requirements_version_sync_reconciler.py —<br/>requirements.txt ↔ pyproject.toml...<br/>Requirements Version Sync Reconciler<br/>文件: d8_doc_sync<br/>/requirements_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_session_worktree_cli_py["session worktree 管理 CLI<br/>session_worktree_cli.py — session worktree 管理<br/>CLI（治本遗留项#2，2026-07-17）<br/>Session Worktree Cli<br/>文件: governance/session_worktree_cli.py<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py["影子金丝雀部署运行器<br/>把 4 个已有零件串成一条命令，做灰度发布的安全网<br/>：先检查能不能上线，再开个影子进程跑同样的输入但<br/>不接真券商，然后比对两边输出是否一致，分歧小就放<br/>行、分歧大就回滚。专门满足 EX-021 那半 CI/CD<br/>灰度门禁。<br/>Shadow Canary Deploy Runner<br/>Shadow Canary deploy runner orchestrating<br/>precheck/shadow/compare/state-machine,<br/>satisfying EX-021 CI/CD gate half<br/>文件: ops/shadow_canary_deploy.py<br/>(设计态 / design)"]
    src_zephyr_gov_enforcement_init_py["执行治理域<br/>gov_enforcement package — 执行治理域<br/>（D_GOV_ENFORCEMENT）<br/>Init<br/>文件: gov_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["Init<br/>管理gov_enforcement.behavioral_admission子包的加<br/>载和懒导入<br/>文件: behavioral_admission/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["stash 堆积阈值检测门禁<br/>stash_accumulation_gate.py — stash<br/>堆积阈值检测门禁（STASH-ACCUMULATION）<br/>Stash Accumulation Gate<br/>文件: commit_gates/stash_accumulation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["Approval<br/>G-CT-004 — Backward-compat re-export of<br/>ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["ComplianceRule 真源已合并至<br/>zephyr.shared.contracts.compliance_rule<br/>rule enforcement包的compliance_rule模块<br/>Compliance Rule<br/>文件: rule_enforcement/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["Default Data Quality Gate<br/>D_DATA — Default Data Quality Gate<br/>Default Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["对接 shared/events/dlq.DeadLetterQueue 的真重试<br/>DLQ 重试策略 — 对接 shared/events<br/>/dlq.DeadLetterQueue 的真重试。<br/>Dlq Retry Policy<br/>文件: rule_enforcement/dlq_retry_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["只读：rules<br/>rule enforcement包的output_quality_gate模块<br/>Output Quality Gate<br/>文件: rule_enforcement/output_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["只读：engine<br/>rule enforcement包的pre_flight_gate模块<br/>Pre Flight Gate<br/>文件: rule_enforcement/pre_flight_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["只读：baseline_metrics<br/>Rule Canary Manager — v0.10.0 规则金丝雀:<br/>1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["Rule Debt Auditor<br/>v0.7.0 规则债务审计器:<br/>分析escalation_rules.yaml维护债务<br/>文件: rule_engine/rule_debt_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["Rule Shadow Runner<br/>v0.10.0 规则影子模式: 新规则shadow运行3天->diff<br/>old vs<br/>文件: rule_engine/rule_shadow_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["mtime 轮询 + 自动同步 + 验证<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>Rule Watcher<br/>文件: rule_engine/rule_watcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["D-022-12.<br/>SLO-Driven Escalation Contract — D-022-12.<br/>Slo Contract<br/>文件: rule_enforcement/slo_contract.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_arch_reference_gate_py["#ARCH-NNN 悬空引用检测门禁单测<br/>test_arch_reference_gate.py — #ARCH-NNN<br/>悬空引用检测门禁单测（ARCH-REFERENCE）<br/>Test Arch Reference Gate<br/>文件: commit_gates/test_arch_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py["asyncio API 误用硬阻断门禁单测<br/>test_asyncio_run_in_context_gate.py — asyncio<br/>API 误用硬阻断门禁单测（ASYNCI...<br/>Test Asyncio Run In Context Gate<br/>文件: commit_gates<br/>/test_asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_getenv_gate_py["NO-BARE-GETENV 门禁单测<br/>test_bare_getenv_gate.py — NO-BARE-GETENV<br/>门禁单测<br/>Test Bare Getenv Gate<br/>文件: commit_gates/test_bare_getenv_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_sql_gate_py["NO-BARE-SQL 门禁单测<br/>test_bare_sql_gate.py — NO-BARE-SQL 门禁单测<br/>Test Bare Sql Gate<br/>文件: commit_gates/test_bare_sql_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_subprocess_gate_py["BARE-SUBPROCESS 门禁单测<br/>test_bare_subprocess_gate.py — BARE-SUBPROCESS<br/>门禁单测<br/>Test Bare Subprocess Gate<br/>文件: commit_gates/test_bare_subprocess_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py["BLUEPRINT-AMODULE-CONSISTENCY 门禁单测<br/>test_blueprint_amodule_consistency_gate.py —<br/>BLUEPRINT-AMODULE-CONSISTENCY ...<br/>Test Blueprint Amodule Consistency Gate<br/>文件: commit_gates<br/>/test_blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py["BLUEPRINT-AMODULE-CROSS-CHECK 门禁单测<br/>test_blueprint_amodule_cross_check_gate.py —<br/>BLUEPRINT-AMODULE-CROSS-CHECK ...<br/>Test Blueprint Amodule Cross Check Gate<br/>文件: commit_gates<br/>/test_blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_audit_log_py["capability_lookup audit log 落盘 e2e smoke test<br/>test_capability_lookup_audit_log.py —<br/>capability_lookup audit log 落盘 e2e s...<br/>Test Capability Lookup Audit Log<br/>文件: commit_gates<br/>/test_capability_lookup_audit_log.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py["CAPABILITY-LOOKUP bypass 策略共享模块单测<br/>test_capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享...<br/>Test Capability Lookup Bypass Policy<br/>文件: commit_gates<br/>/test_capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_required_gate_py["CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>test_capability_lookup_required_gate.py —<br/>CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>Test Capability Lookup Required Gate<br/>文件: commit_gates<br/>/test_capability_lookup_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_overlap_gate_py["CAPABILITY-OVERLAP 门禁单测<br/>test_capability_overlap_gate.py —<br/>CAPABILITY-OVERLAP 门禁单测<br/>Test Capability Overlap Gate<br/>文件: commit_gates<br/>/test_capability_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_batch_size_gate_py["CH-BATCH-SIZE 门禁单测<br/>test_ch_batch_size_gate.py — CH-BATCH-SIZE<br/>门禁单测<br/>Test Ch Batch Size Gate<br/>文件: commit_gates/test_ch_batch_size_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_version_col_gate_py["CH-VERSION-COL 门禁单测<br/>test_ch_version_col_gate.py — CH-VERSION-COL<br/>门禁单测<br/>Test Ch Version Col Gate<br/>文件: commit_gates/test_ch_version_col_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_claim_required_gate_py["claim_files 前置检查门禁单测<br/>test_claim_required_gate.py — claim_files<br/>前置检查门禁单测（CLAIM-REQUIRED，...<br/>Test Claim Required Gate<br/>文件: commit_gates/test_claim_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_consumers_accuracy_gate_py["CONSUMERS-ACCURACY 门禁单测<br/>test_consumers_accuracy_gate.py —<br/>CONSUMERS-ACCURACY 门禁单测（...<br/>Test Consumers Accuracy Gate<br/>文件: commit_gates<br/>/test_consumers_accuracy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_create_guard_py["CREATE-GUARD 门禁单元测试<br/>test_create_guard.py — CREATE-GUARD<br/>门禁单元测试（2026-06-30 治本补全）<br/>Test Create Guard<br/>文件: commit_gates/test_create_guard.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_dangling_reference_gate_py["AGENTS.md §X.Y 悬空引用检测门禁单测<br/>test_dangling_reference_gate.py — AGENTS.md<br/>§X.Y 悬空引用检测门禁单测（DANG...<br/>Test Dangling Reference Gate<br/>文件: commit_gates<br/>/test_dangling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py["生成器代码 datetime.now<br/>test_datetime_now_forbidden_gate.py —<br/>生成器代码 datetime.now() 硬阻断门禁单...<br/>Test Datetime Now Forbidden Gate<br/>文件: commit_gates<br/>/test_datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_freshness_gate_py["DEPGRAPH-FRESHNESS 门禁单测<br/>test_depgraph_freshness_gate.py —<br/>DEPGRAPH-FRESHNESS 门禁单测<br/>Test Depgraph Freshness Gate<br/>文件: commit_gates<br/>/test_depgraph_freshness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py["DEPGRAPH-PRE-REGISTRATION gate 测试<br/>test_depgraph_pre_registration_gate.py —<br/>DEPGRAPH-PRE-REGISTRATION gate 测试<br/>Test Depgraph Pre Registration Gate<br/>文件: commit_gates<br/>/test_depgraph_pre_registration_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_derived_file_deletion_gate_py["派生文件删除保护门禁单测<br/>test_derived_file_deletion_gate.py —<br/>派生文件删除保护门禁单测（DERIVED-FILE-...<br/>Test Derived File Deletion Gate<br/>文件: commit_gates<br/>/test_derived_file_deletion_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_diff_helpers_py["gate 共享 diff 解析工具模块单测<br/>test_diff_helpers.py — gate 共享 diff<br/>解析工具模块单测<br/>Test Diff Helpers<br/>文件: commit_gates/test_diff_helpers.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_doc_ref_broken_gate_py["DOC-REF-BROKEN 门禁单测<br/>test_doc_ref_broken_gate.py — DOC-REF-BROKEN<br/>门禁单测<br/>Test Doc Ref Broken Gate<br/>文件: commit_gates/test_doc_ref_broken_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_fk_gate_py["GATE-DOMAIN-FK 门禁单测<br/>test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测<br/>Test Domain Fk Gate<br/>文件: commit_gates/test_domain_fk_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py["NO-DOMAIN-NAME-ZH-DIRECT-ACCESS 门禁单测<br/>test_domain_name_zh_direct_access_gate.py —<br/>NO-DOMAIN-NAME-ZH-DIRECT-ACCESS ...<br/>Test Domain Name Zh Direct Access Gate<br/>文件: commit_gates<br/>/test_domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_empty_handler_gate_py["EMPTY-HANDLER 门禁单测<br/>test_empty_handler_gate.py — EMPTY-HANDLER<br/>门禁单测<br/>Test Empty Handler Gate<br/>文件: commit_gates/test_empty_handler_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py["EXEMPT-ZONE-FM 门禁单测<br/>test_exempt_zone_frontmatter_gate.py —<br/>EXEMPT-ZONE-FM 门禁单测<br/>Test Exempt Zone Frontmatter Gate<br/>文件: commit_gates<br/>/test_exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_file_copy_gate_py["FILE-COPY 门禁单测<br/>test_file_copy_gate.py — FILE-COPY 门禁单测<br/>Test File Copy Gate<br/>文件: commit_gates/test_file_copy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_foreign_change_gate_py["外来变更检测门禁单测<br/>test_foreign_change_gate.py —<br/>外来变更检测门禁单测<br/>（FOREIGN-CHANGE-DETECTION...<br/>Test Foreign Change Gate<br/>文件: commit_gates/test_foreign_change_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_forged_gw_marker_gate_py["Forged GW Marker 前置检测门禁单测<br/>test_forged_gw_marker_gate.py — Forged GW<br/>Marker 前置检测门禁单测（...<br/>Test Forged Gw Marker Gate<br/>文件: commit_gates/test_forged_gw_marker_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_function_dup_gate_py["FUNCTION-DUP 门禁单测<br/>test_function_dup_gate.py — FUNCTION-DUP<br/>门禁单测<br/>Test Function Dup Gate<br/>文件: commit_gates/test_function_dup_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_god_class_gate_py["NO-GOD-CLASS 门禁单测<br/>test_god_class_gate.py — NO-GOD-CLASS 门禁单测<br/>Test God Class Gate<br/>文件: commit_gates/test_god_class_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_hardcoded_url_gate_py["NO-HARDCODED-URL 门禁单测<br/>test_hardcoded_url_gate.py — NO-HARDCODED-URL<br/>门禁单测<br/>Test Hardcoded Url Gate<br/>文件: commit_gates/test_hardcoded_url_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_held_overlap_gate_py["搭便车防护门禁单测<br/>test_held_overlap_gate.py — 搭便车防护门禁单测<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>Test Held Overlap Gate<br/>文件: commit_gates/test_held_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_high_complexity_gate_py["NO-HIGH-COMPLEXITY 门禁单测<br/>test_high_complexity_gate.py —<br/>NO-HIGH-COMPLEXITY 门禁单测<br/>Test High Complexity Gate<br/>文件: commit_gates/test_high_complexity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_id_uniqueness_gate_py["ID-UNIQUENESS 门禁单测<br/>test_id_uniqueness_gate.py — ID-UNIQUENESS<br/>门禁单测<br/>Test Id Uniqueness Gate<br/>文件: commit_gates/test_id_uniqueness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_direction_gate_py["NO-UPWARD-IMPORT 门禁单测<br/>test_import_direction_gate.py —<br/>NO-UPWARD-IMPORT 门禁单测<br/>Test Import Direction Gate<br/>文件: commit_gates/test_import_direction_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_integrity_gate_py["IMPORT-INTEGRITY 门禁单测<br/>test_import_integrity_gate.py —<br/>IMPORT-INTEGRITY 门禁单测（...<br/>Test Import Integrity Gate<br/>文件: commit_gates/test_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_long_param_list_gate_py["NO-LONG-PARAM-LIST 门禁单测<br/>test_long_param_list_gate.py —<br/>NO-LONG-PARAM-LIST 门禁单测<br/>Test Long Param List Gate<br/>文件: commit_gates/test_long_param_list_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py["MANUAL-ONLY-PERMANENT m11 noqa 豁免单测<br/>test_manual_only_permanent_gate_noqa.py —<br/>MANUAL-ONLY-PERMANENT m11 noqa 豁...<br/>Test Manual Only Permanent Gate Noqa<br/>文件: commit_gates<br/>/test_manual_only_permanent_gate_noqa.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mcp_version_field_gate_py["MCP version 字段缺失硬阻断门禁单测<br/>test_mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁单测（MCP-VER...<br/>Test Mcp Version Field Gate<br/>文件: commit_gates<br/>/test_mcp_version_field_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_module_id_consistency_gate_py["module_id 三声明轨道一致性 + count 派生 +<br/>跨文件唯一性门禁单测<br/>test_module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生...<br/>Test Module Id Consistency Gate<br/>文件: commit_gates<br/>/test_module_id_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_exposure_gate_py["MSG-EXPOSURE 门禁单测<br/>test_msg_exposure_gate.py — MSG-EXPOSURE<br/>门禁单测<br/>Test Msg Exposure Gate<br/>文件: commit_gates/test_msg_exposure_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_style_gate_py["MSG-STYLE 门禁单测<br/>test_msg_style_gate.py — MSG-STYLE 门禁单测<br/>Test Msg Style Gate<br/>文件: commit_gates/test_msg_style_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py["可变常量缺 Final 标注硬阻断门禁单测<br/>test_mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁单...<br/>Test Mutable Const Without Final Gate<br/>文件: commit_gates<br/>/test_mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_new_file_depgraph_gate_py["NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>test_new_file_depgraph_gate.py —<br/>NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>Test New File Depgraph Gate<br/>文件: commit_gates<br/>/test_new_file_depgraph_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_no_import_side_effect_gate_py["NO-IMPORT-SIDE-EFFECT 门禁单测<br/>test_no_import_side_effect_gate.py —<br/>NO-IMPORT-SIDE-EFFECT 门禁单测<br/>Test No Import Side Effect Gate<br/>文件: commit_gates<br/>/test_no_import_side_effect_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_open_without_with_gate_py["open<br/>test_open_without_with_gate.py — open() 未在<br/>with 内硬阻断门禁单测（OPEN-WIT...<br/>Test Open Without With Gate<br/>文件: commit_gates<br/>/test_open_without_with_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_orphan_module_gate_py["ORPHAN-MODULE 门禁单测<br/>test_orphan_module_gate.py — ORPHAN-MODULE<br/>门禁单测<br/>Test Orphan Module Gate<br/>文件: commit_gates/test_orphan_module_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_panorama_alignment_gate_py["四图模块对齐门禁单测<br/>test_panorama_alignment_gate.py —<br/>四图模块对齐门禁单测（GATE-PANORAMA-ALIGNM...<br/>Test Panorama Alignment Gate<br/>文件: commit_gates<br/>/test_panorama_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_perm_trigger_gate_py["PERM-TRIGGER 门禁单测<br/>test_perm_trigger_gate.py — PERM-TRIGGER<br/>门禁单测<br/>Test Perm Trigger Gate<br/>文件: commit_gates/test_perm_trigger_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_precommit_offline_gate_py["GATE-PRECOMMIT-OFFLINE 门禁单测<br/>test_precommit_offline_gate.py —<br/>GATE-PRECOMMIT-OFFLINE 门禁单测<br/>Test Precommit Offline Gate<br/>文件: commit_gates<br/>/test_precommit_offline_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_protected_paths_gate_py["受保护路径写入检测门禁单测<br/>test_protected_paths_gate.py —<br/>受保护路径写入检测门禁单测（...<br/>Test Protected Paths Gate<br/>文件: commit_gates/test_protected_paths_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["R5-DIGIT-SUFFIX 门禁单元测试<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX<br/>门禁单元测试<br/>Test R5 Digit Suffix Gate<br/>文件: commit_gates/test_r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_reconciler_health_gate_py["RECONCILER-HEALTH 门禁单测<br/>test_reconciler_health_gate.py —<br/>RECONCILER-HEALTH 门禁单测<br/>Test Reconciler Health Gate<br/>文件: commit_gates<br/>/test_reconciler_health_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py["RENAME-DEPGRAPH-SYNC 门禁单测<br/>test_rename_depgraph_sync_gate.py —<br/>RENAME-DEPGRAPH-SYNC 门禁单测<br/>Test Rename Depgraph Sync Gate<br/>文件: commit_gates<br/>/test_rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py["Test Rule Execution Pairing Gate<br/>Tests for RULE-EXECUTION-PAIRING gate (Phase<br/>3.5).<br/>文件: commit_gates<br/>/test_rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py["RULE-FOUR-WAY-ALIGN 门禁单测<br/>test_rule_four_way_alignment_gate.py —<br/>RULE-FOUR-WAY-ALIGN 门禁单测<br/>Test Rule Four Way Alignment Gate<br/>文件: commit_gates<br/>/test_rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py["RULING-COMMIT-VERIFIED 门禁单测<br/>test_ruling_commit_verified_gate.py —<br/>RULING-COMMIT-VERIFIED 门禁单测。<br/>Test Ruling Commit Verified Gate<br/>文件: commit_gates<br/>/test_ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_reference_gate_py["裁定#NNN 悬空引用检测门禁单测<br/>test_ruling_reference_gate.py — 裁定#NNN<br/>悬空引用检测门禁单测（RULING-REFERE...<br/>Test Ruling Reference Gate<br/>文件: commit_gates/test_ruling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_schema_file_exists_gate_py["SCHEMA-FILE-EXISTS 门禁单测<br/>test_schema_file_exists_gate.py —<br/>SCHEMA-FILE-EXISTS 门禁单测<br/>Test Schema File Exists Gate<br/>文件: commit_gates<br/>/test_schema_file_exists_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py["SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>test_scripts_import_integrity_gate.py —<br/>SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>Test Scripts Import Integrity Gate<br/>文件: commit_gates<br/>/test_scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_secret_hardcode_gate_py["NO-SECRET-HARDCODE 门禁单测<br/>test_secret_hardcode_gate.py —<br/>NO-SECRET-HARDCODE 门禁单测<br/>Test Secret Hardcode Gate<br/>文件: commit_gates/test_secret_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py["SECRET-REGISTRY-CONSISTENCY 门禁单测<br/>test_secret_registry_consistency_gate.py —<br/>SECRET-REGISTRY-CONSISTENCY 门禁单测<br/>Test Secret Registry Consistency Gate<br/>文件: commit_gates<br/>/test_secret_registry_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_session_required_gate_py["SESSION-REQUIRED 门禁单测<br/>test_session_required_gate.py —<br/>SESSION-REQUIRED 门禁单测<br/>Test Session Required Gate<br/>文件: commit_gates/test_session_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ssot_redefinition_gate_py["SSoT 符号重复定义硬阻断门禁单测<br/>test_ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁单测（SSOT-REDEF...<br/>Test Ssot Redefinition Gate<br/>文件: commit_gates<br/>/test_ssot_redefinition_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_test_source_consistency_gate_py["TEST-SOURCE-CONSISTENCY 门禁单测<br/>test_test_source_consistency_gate.py —<br/>TEST-SOURCE-CONSISTENCY 门禁单测<br/>Test Test Source Consistency Gate<br/>文件: commit_gates<br/>/test_test_source_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_translation_coverage_gate_py["TRANSLATION-COVERAGE 门禁单测<br/>test_translation_coverage_gate.py —<br/>TRANSLATION-COVERAGE 门禁单测<br/>Test Translation Coverage Gate<br/>文件: commit_gates<br/>/test_translation_coverage_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_undefined_name_gate_py["UNDEFINED-NAME 门禁单测<br/>test_undefined_name_gate.py — UNDEFINED-NAME<br/>门禁单测<br/>Test Undefined Name Gate<br/>文件: commit_gates/test_undefined_name_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py["``**data`` 直接展开 warn 级门禁单测<br/>test_unsafe_dict_spread_gate.py — ``**data``<br/>直接展开 warn 级门禁单测（UNSAF...<br/>Test Unsafe Dict Spread Gate<br/>文件: commit_gates<br/>/test_unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_vocab_hardcode_gate_py["VOCAB-HARDCODE 门禁单测<br/>test_vocab_hardcode_gate.py — VOCAB-HARDCODE<br/>门禁单测<br/>Test Vocab Hardcode Gate<br/>文件: commit_gates/test_vocab_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_worktree_required_gate_py["WORKTREE-REQUIRED 门禁单测<br/>test_worktree_required_gate.py —<br/>WORKTREE-REQUIRED 门禁单测<br/>Test Worktree Required Gate<br/>文件: commit_gates<br/>/test_worktree_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py["ZEPHYR_ENV 直访硬阻断门禁单测<br/>test_zephyr_env_direct_access_gate.py —<br/>ZEPHYR_ENV 直访硬阻断门禁单测（ZEPHY...<br/>Test Zephyr Env Direct Access Gate<br/>文件: commit_gates<br/>/test_zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["P2-2 并发 session 文件级原子性测试<br/>test_claim_files_for_edit.py — P2-2 并发<br/>session 文件级原子性测试<br/>Test Claim Files For Edit<br/>文件: rule_bridge/test_claim_files_for_edit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_commit_gate_registry_py["CommitGateRegistry 单测<br/>test_commit_gate_registry.py —<br/>CommitGateRegistry 单测（架构债务 #AD-001 治本）<br/>Test Commit Gate Registry<br/>文件: rule_bridge/test_commit_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_emergency_commit_py["emergency_commit API 测试<br/>test_emergency_commit.py — emergency_commit API<br/>测试（Ruling:100PCT-AI-GOVER...<br/>Test Emergency Commit<br/>文件: rule_bridge/test_emergency_commit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_gate_auto_registrar_py["gate_auto_registrar 单元测试<br/>test_gate_auto_registrar.py —<br/>gate_auto_registrar 单元测试（...<br/>Test Gate Auto Registrar<br/>文件: rule_bridge/test_gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["heartbeat daemon + 成本递增 smoke test<br/>test_heartbeat_daemon.py — heartbeat daemon +<br/>成本递增 smoke test（Ruling:10...<br/>Test Heartbeat Daemon<br/>文件: rule_bridge/test_heartbeat_daemon.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_py["worktree 物理隔离端到端测试<br/>test_session_worktree.py — worktree<br/>物理隔离端到端测试（FP-ISO.4C，2026-07-0...<br/>Test Session Worktree<br/>文件: rule_bridge/test_session_worktree.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_cli_py["session_worktree_cli CLI 测试<br/>test_session_worktree_cli.py —<br/>session_worktree_cli CLI 测试（治本遗留项#2, ...<br/>Test Session Worktree Cli<br/>文件: rule_bridge/test_session_worktree_cli.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_health_check_py["session_worktree_start 启动健康度自检测试<br/>test_session_worktree_health_check.py —<br/>session_worktree_start 启动健康度自...<br/>Test Session Worktree Health Check<br/>文件: rule_bridge<br/>/test_session_worktree_health_check.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py["_trusted_git_env 进程级隔离单测<br/>test_session_worktree_trusted_git_env.py —<br/>_trusted_git_env 进程级隔离单测（...<br/>Test Session Worktree Trusted Git Env<br/>文件: rule_bridge<br/>/test_session_worktree_trusted_git_env.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py["session lifecycle 工作区 clean 检查单测<br/>test_session_worktree_workspace_clean.py —<br/>session lifecycle 工作区 clean 检...<br/>Test Session Worktree Workspace Clean<br/>文件: rule_bridge<br/>/test_session_worktree_workspace_clean.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_pool_py["WorktreePool 端到端 smoke test<br/>test_worktree_pool.py — WorktreePool 端到端<br/>smoke test（ARCH-GIT-CALL-BUDGET...<br/>Test Worktree Pool<br/>文件: rule_bridge/test_worktree_pool.py<br/>(生产态 / production)"]
    tests_ops_test_shadow_canary_deploy_py["Shadow Canary 部署运行器单元测试<br/>test_shadow_canary_deploy.py — Shadow Canary<br/>部署运行器单元测试<br/>Test Shadow Canary Deploy<br/>文件: ops/test_shadow_canary_deploy.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml ~~~ scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py ~~~ scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py ~~~ scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py ~~~ scripts_governance_session_worktree_cli_py
    scripts_governance_session_worktree_cli_py ~~~ scripts_ops_shadow_canary_deploy_py
    scripts_ops_shadow_canary_deploy_py ~~~ src_zephyr_gov_enforcement_init_py
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
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_secret_hardcode_gate_py
    tests_governance_commit_gates_test_secret_hardcode_gate_py ~~~ tests_governance_commit_gates_test_secret_registry_consistency_gate_py
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py ~~~ tests_governance_commit_gates_test_session_required_gate_py
    tests_governance_commit_gates_test_session_required_gate_py ~~~ tests_governance_commit_gates_test_ssot_redefinition_gate_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py ~~~ tests_governance_commit_gates_test_test_source_consistency_gate_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py ~~~ tests_governance_commit_gates_test_translation_coverage_gate_py
    tests_governance_commit_gates_test_translation_coverage_gate_py ~~~ tests_governance_commit_gates_test_undefined_name_gate_py
    tests_governance_commit_gates_test_undefined_name_gate_py ~~~ tests_governance_commit_gates_test_unsafe_dict_spread_gate_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py ~~~ tests_governance_commit_gates_test_vocab_hardcode_gate_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py ~~~ tests_governance_commit_gates_test_worktree_required_gate_py
    tests_governance_commit_gates_test_worktree_required_gate_py ~~~ tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py
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
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["Admission Response<br/>behavioral admission包的admission_response模块<br/>文件: behavioral_admission/admission_response.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["Code Review Ai<br/>behavioral admission包的code_review_ai模块<br/>文件: behavioral_admission/code_review_ai.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["—将 gate 结果写入 task_events<br/>GateEventAdapter — GateRepo 事件适配器<br/>（DW-0006）<br/>Gate Event Adapter<br/>文件: behavioral_admission/gate_event_adapter.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["Gpu Consensus Scheduler<br/>behavioral<br/>admission包的gpu_consensus_scheduler模块<br/>文件: behavioral_admission<br/>/gpu_consensus_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["Protection Index<br/>behavioral admission包的protection_index模块<br/>文件: behavioral_admission/protection_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["GitCommitGateway pre-commit 门禁注册表<br/>commit_gate_registry.py — GitCommitGateway<br/>pre-commit 门禁注册表（架构债务 #...<br/>Commit Gate Registry<br/>文件: rule_bridge/commit_gate_registry.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["Session Worktree<br/>session_worktree.py — AI 对话 worktree 物理隔离<br/>helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["Data Quality Gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["Admission Controller<br/>behavioral admission包的admission_controller模块<br/>文件: behavioral_admission<br/>/admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["Verdict Engine<br/>behavioral admission包的verdict_engine模块<br/>文件: behavioral_admission/verdict_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["紧急提交通道<br/>emergency_commit.py — 紧急提交通道<br/>（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>Emergency Commit<br/>文件: rule_bridge/emergency_commit.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["session heartbeat 独立进程<br/>heartbeat_daemon.py — session heartbeat<br/>独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>Heartbeat Daemon<br/>文件: rule_bridge/heartbeat_daemon.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["AI 对话并发声明 helper<br/>session_claim.py — AI 对话并发声明 helper<br/>（FP-ISO.4B 件2改，2026-07-01 治本）<br/>Session Claim<br/>文件: rule_bridge/session_claim.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["session worktree 物理隔离管理器<br/>worktree_manager.py — session worktree<br/>物理隔离管理器（阶段3 治本 stash 循环）<br/>Worktree Manager<br/>文件: rule_bridge/worktree_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["Worktree 预创建池<br/>worktree_pool.py — Worktree 预创建池<br/>（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>Worktree Pool<br/>文件: rule_bridge/worktree_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["全项目唯一合法 git commit 入口<br/>GitCommitGateway — 全项目唯一合法 git commit<br/>入口（OPS-2026062512 治本）<br/>Git Commit Gateway<br/>文件: rule_bridge/git_commit_gateway.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["Reconciler 批量化 auto-commit 拦截器<br/>batched_auto_committer.py — Reconciler 批量化<br/>auto-commit 拦截器（ARCH-GIT-C...<br/>Batched Auto Committer<br/>文件: rule_bridge/batched_auto_committer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_getenv_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_sql_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_version_col_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_claim_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_fk_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_file_copy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_function_dup_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_empty_handler_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_held_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_god_class_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_high_complexity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_direction_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_exposure_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_long_param_list_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_style_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_orphan_module_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_open_without_with_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_protected_paths_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_perm_trigger_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_reconciler_health_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_precommit_offline_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_secret_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_session_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_translation_coverage_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_undefined_name_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_worktree_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_commit_gate_registry_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOV_RULE["规则治理<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>Rule Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_GOV_RULE
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_ops_shadow_canary_deploy_py -.->|导入依赖 / import_depends| D_SECURITY
    D_GOV_CODE_QUALITY["代码质量治理<br/>代码质量治理，负责代码去重引擎、函数重复检测、AS<br/>T语义分析和提交门禁引擎<br/>Code Quality Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    tests_ops_test_shadow_canary_deploy_py -->|测试依赖 / test_depends| D_GOV_RULE
    tests_governance_commit_gates_test_msg_exposure_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    tests_governance_commit_gates_test_worktree_required_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    tests_governance_commit_gates_test_secret_hardcode_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    tests_governance_commit_gates_test_empty_handler_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| D_SHARED
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py -->|测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_ML_TRAIN["训练<br/>训练，负责模型训练、特征工程和模型评估<br/>Training<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_ML_TRAIN -.->|data / data| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_OPS_RESILIENCE -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py
    D_GOV_AUDIT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_arch_reference_gate_py,tests_governance_commit_gates_test_asyncio_run_in_context_gate_py,tests_governance_commit_gates_test_bare_getenv_gate_py,tests_governance_commit_gates_test_bare_sql_gate_py,tests_governance_commit_gates_test_bare_subprocess_gate_py,tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py,tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py,tests_governance_commit_gates_test_capability_lookup_audit_log_py,tests_governance_commit_gates_test_capability_lookup_bypass_policy_py,tests_governance_commit_gates_test_capability_lookup_required_gate_py,tests_governance_commit_gates_test_capability_overlap_gate_py,tests_governance_commit_gates_test_ch_batch_size_gate_py,tests_governance_commit_gates_test_ch_version_col_gate_py,tests_governance_commit_gates_test_claim_required_gate_py,tests_governance_commit_gates_test_consumers_accuracy_gate_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_dangling_reference_gate_py,tests_governance_commit_gates_test_datetime_now_forbidden_gate_py,tests_governance_commit_gates_test_depgraph_freshness_gate_py,tests_governance_commit_gates_test_depgraph_pre_registration_gate_py,tests_governance_commit_gates_test_derived_file_deletion_gate_py,tests_governance_commit_gates_test_diff_helpers_py,tests_governance_commit_gates_test_doc_ref_broken_gate_py,tests_governance_commit_gates_test_domain_fk_gate_py,tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py,tests_governance_commit_gates_test_empty_handler_gate_py,tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py,tests_governance_commit_gates_test_file_copy_gate_py,tests_governance_commit_gates_test_foreign_change_gate_py,tests_governance_commit_gates_test_forged_gw_marker_gate_py,tests_governance_commit_gates_test_function_dup_gate_py,tests_governance_commit_gates_test_god_class_gate_py,tests_governance_commit_gates_test_hardcoded_url_gate_py,tests_governance_commit_gates_test_held_overlap_gate_py,tests_governance_commit_gates_test_high_complexity_gate_py,tests_governance_commit_gates_test_id_uniqueness_gate_py,tests_governance_commit_gates_test_import_direction_gate_py,tests_governance_commit_gates_test_import_integrity_gate_py,tests_governance_commit_gates_test_long_param_list_gate_py,tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py,tests_governance_commit_gates_test_mcp_version_field_gate_py,tests_governance_commit_gates_test_module_id_consistency_gate_py,tests_governance_commit_gates_test_msg_exposure_gate_py,tests_governance_commit_gates_test_msg_style_gate_py,tests_governance_commit_gates_test_mutable_const_without_final_gate_py,tests_governance_commit_gates_test_new_file_depgraph_gate_py,tests_governance_commit_gates_test_no_import_side_effect_gate_py,tests_governance_commit_gates_test_open_without_with_gate_py,tests_governance_commit_gates_test_orphan_module_gate_py,tests_governance_commit_gates_test_panorama_alignment_gate_py,tests_governance_commit_gates_test_perm_trigger_gate_py,tests_governance_commit_gates_test_precommit_offline_gate_py,tests_governance_commit_gates_test_protected_paths_gate_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_commit_gates_test_reconciler_health_gate_py,tests_governance_commit_gates_test_rename_depgraph_sync_gate_py,tests_governance_commit_gates_test_rule_execution_pairing_gate_py,tests_governance_commit_gates_test_rule_four_way_alignment_gate_py,tests_governance_commit_gates_test_ruling_commit_verified_gate_py,tests_governance_commit_gates_test_ruling_reference_gate_py,tests_governance_commit_gates_test_schema_file_exists_gate_py,tests_governance_commit_gates_test_scripts_import_integrity_gate_py,tests_governance_commit_gates_test_secret_hardcode_gate_py,tests_governance_commit_gates_test_secret_registry_consistency_gate_py,tests_governance_commit_gates_test_session_required_gate_py,tests_governance_commit_gates_test_ssot_redefinition_gate_py,tests_governance_commit_gates_test_test_source_consistency_gate_py,tests_governance_commit_gates_test_translation_coverage_gate_py,tests_governance_commit_gates_test_undefined_name_gate_py,tests_governance_commit_gates_test_unsafe_dict_spread_gate_py,tests_governance_commit_gates_test_vocab_hardcode_gate_py,tests_governance_commit_gates_test_worktree_required_gate_py,tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_commit_gate_registry_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_gate_auto_registrar_py,tests_governance_rule_bridge_test_heartbeat_daemon_py,tests_governance_rule_bridge_test_session_worktree_py,tests_governance_rule_bridge_test_session_worktree_cli_py,tests_governance_rule_bridge_test_session_worktree_health_check_py,tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py,tests_governance_rule_bridge_test_session_worktree_workspace_clean_py,tests_governance_rule_bridge_test_worktree_pool_py,tests_ops_test_shadow_canary_deploy_py production
    class scripts_ops_shadow_canary_deploy_py design
    class D_GOV_RULE,D_GOVERNANCE,D_AUTONOMY_CORE,D_SECURITY,D_GOV_CODE_QUALITY,D_SHARED,D_GOV_AUDIT,D_GOV_OPS_RESILIENCE external_prod
    class D_ML_TRAIN external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 121 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml["Rule Enforcement Registry<br/>catalogs包的rule_enforcement_registry模块<br/>文件: catalogs/rule_enforcement_registry.yaml<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["dashboard 指标数描述派生校验 reconciler<br/>metric_count_drift_reconciler.py — dashboard<br/>指标数描述派生校验 reconciler<br/>Metric Count Drift Reconciler<br/>文件: d8_doc_sync<br/>/metric_count_drift_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["README 版本号派生展示校验 reconciler<br/>readme_version_sync_reconciler.py — README<br/>版本号派生展示校验 reconciler<br/>Readme Version Sync Reconciler<br/>文件: d8_doc_sync<br/>/readme_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["requirements.txt ↔ pyproject.toml<br/>依赖一致性校验 reconciler<br/>requirements_version_sync_reconciler.py —<br/>requirements.txt ↔ pyproject.toml...<br/>Requirements Version Sync Reconciler<br/>文件: d8_doc_sync<br/>/requirements_version_sync_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_session_worktree_cli_py["session worktree 管理 CLI<br/>session_worktree_cli.py — session worktree 管理<br/>CLI（治本遗留项#2，2026-07-17）<br/>Session Worktree Cli<br/>文件: governance/session_worktree_cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_init_py["执行治理域<br/>gov_enforcement package — 执行治理域<br/>（D_GOV_ENFORCEMENT）<br/>Init<br/>文件: gov_enforcement/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["Init<br/>管理gov_enforcement.behavioral_admission子包的加<br/>载和懒导入<br/>文件: behavioral_admission/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["stash 堆积阈值检测门禁<br/>stash_accumulation_gate.py — stash<br/>堆积阈值检测门禁（STASH-ACCUMULATION）<br/>Stash Accumulation Gate<br/>文件: commit_gates/stash_accumulation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["Approval<br/>G-CT-004 — Backward-compat re-export of<br/>ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["ComplianceRule 真源已合并至<br/>zephyr.shared.contracts.compliance_rule<br/>rule enforcement包的compliance_rule模块<br/>Compliance Rule<br/>文件: rule_enforcement/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["Default Data Quality Gate<br/>D_DATA — Default Data Quality Gate<br/>Default Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["对接 shared/events/dlq.DeadLetterQueue 的真重试<br/>DLQ 重试策略 — 对接 shared/events<br/>/dlq.DeadLetterQueue 的真重试。<br/>Dlq Retry Policy<br/>文件: rule_enforcement/dlq_retry_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["只读：rules<br/>rule enforcement包的output_quality_gate模块<br/>Output Quality Gate<br/>文件: rule_enforcement/output_quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["只读：engine<br/>rule enforcement包的pre_flight_gate模块<br/>Pre Flight Gate<br/>文件: rule_enforcement/pre_flight_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["只读：baseline_metrics<br/>Rule Canary Manager — v0.10.0 规则金丝雀:<br/>1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["Rule Debt Auditor<br/>v0.7.0 规则债务审计器:<br/>分析escalation_rules.yaml维护债务<br/>文件: rule_engine/rule_debt_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["Rule Shadow Runner<br/>v0.10.0 规则影子模式: 新规则shadow运行3天->diff<br/>old vs<br/>文件: rule_engine/rule_shadow_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["mtime 轮询 + 自动同步 + 验证<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>Rule Watcher<br/>文件: rule_engine/rule_watcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["D-022-12.<br/>SLO-Driven Escalation Contract — D-022-12.<br/>Slo Contract<br/>文件: rule_enforcement/slo_contract.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_arch_reference_gate_py["#ARCH-NNN 悬空引用检测门禁单测<br/>test_arch_reference_gate.py — #ARCH-NNN<br/>悬空引用检测门禁单测（ARCH-REFERENCE）<br/>Test Arch Reference Gate<br/>文件: commit_gates/test_arch_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py["asyncio API 误用硬阻断门禁单测<br/>test_asyncio_run_in_context_gate.py — asyncio<br/>API 误用硬阻断门禁单测（ASYNCI...<br/>Test Asyncio Run In Context Gate<br/>文件: commit_gates<br/>/test_asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_getenv_gate_py["NO-BARE-GETENV 门禁单测<br/>test_bare_getenv_gate.py — NO-BARE-GETENV<br/>门禁单测<br/>Test Bare Getenv Gate<br/>文件: commit_gates/test_bare_getenv_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_sql_gate_py["NO-BARE-SQL 门禁单测<br/>test_bare_sql_gate.py — NO-BARE-SQL 门禁单测<br/>Test Bare Sql Gate<br/>文件: commit_gates/test_bare_sql_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_bare_subprocess_gate_py["BARE-SUBPROCESS 门禁单测<br/>test_bare_subprocess_gate.py — BARE-SUBPROCESS<br/>门禁单测<br/>Test Bare Subprocess Gate<br/>文件: commit_gates/test_bare_subprocess_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py["BLUEPRINT-AMODULE-CONSISTENCY 门禁单测<br/>test_blueprint_amodule_consistency_gate.py —<br/>BLUEPRINT-AMODULE-CONSISTENCY ...<br/>Test Blueprint Amodule Consistency Gate<br/>文件: commit_gates<br/>/test_blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py["BLUEPRINT-AMODULE-CROSS-CHECK 门禁单测<br/>test_blueprint_amodule_cross_check_gate.py —<br/>BLUEPRINT-AMODULE-CROSS-CHECK ...<br/>Test Blueprint Amodule Cross Check Gate<br/>文件: commit_gates<br/>/test_blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_audit_log_py["capability_lookup audit log 落盘 e2e smoke test<br/>test_capability_lookup_audit_log.py —<br/>capability_lookup audit log 落盘 e2e s...<br/>Test Capability Lookup Audit Log<br/>文件: commit_gates<br/>/test_capability_lookup_audit_log.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_bypass_policy_py["CAPABILITY-LOOKUP bypass 策略共享模块单测<br/>test_capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享...<br/>Test Capability Lookup Bypass Policy<br/>文件: commit_gates<br/>/test_capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_lookup_required_gate_py["CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>test_capability_lookup_required_gate.py —<br/>CAPABILITY-LOOKUP-REQUIRED 门禁单测<br/>Test Capability Lookup Required Gate<br/>文件: commit_gates<br/>/test_capability_lookup_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_capability_overlap_gate_py["CAPABILITY-OVERLAP 门禁单测<br/>test_capability_overlap_gate.py —<br/>CAPABILITY-OVERLAP 门禁单测<br/>Test Capability Overlap Gate<br/>文件: commit_gates<br/>/test_capability_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_batch_size_gate_py["CH-BATCH-SIZE 门禁单测<br/>test_ch_batch_size_gate.py — CH-BATCH-SIZE<br/>门禁单测<br/>Test Ch Batch Size Gate<br/>文件: commit_gates/test_ch_batch_size_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ch_version_col_gate_py["CH-VERSION-COL 门禁单测<br/>test_ch_version_col_gate.py — CH-VERSION-COL<br/>门禁单测<br/>Test Ch Version Col Gate<br/>文件: commit_gates/test_ch_version_col_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_claim_required_gate_py["claim_files 前置检查门禁单测<br/>test_claim_required_gate.py — claim_files<br/>前置检查门禁单测（CLAIM-REQUIRED，...<br/>Test Claim Required Gate<br/>文件: commit_gates/test_claim_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_consumers_accuracy_gate_py["CONSUMERS-ACCURACY 门禁单测<br/>test_consumers_accuracy_gate.py —<br/>CONSUMERS-ACCURACY 门禁单测（...<br/>Test Consumers Accuracy Gate<br/>文件: commit_gates<br/>/test_consumers_accuracy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_create_guard_py["CREATE-GUARD 门禁单元测试<br/>test_create_guard.py — CREATE-GUARD<br/>门禁单元测试（2026-06-30 治本补全）<br/>Test Create Guard<br/>文件: commit_gates/test_create_guard.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_dangling_reference_gate_py["AGENTS.md §X.Y 悬空引用检测门禁单测<br/>test_dangling_reference_gate.py — AGENTS.md<br/>§X.Y 悬空引用检测门禁单测（DANG...<br/>Test Dangling Reference Gate<br/>文件: commit_gates<br/>/test_dangling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py["生成器代码 datetime.now<br/>test_datetime_now_forbidden_gate.py —<br/>生成器代码 datetime.now() 硬阻断门禁单...<br/>Test Datetime Now Forbidden Gate<br/>文件: commit_gates<br/>/test_datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_freshness_gate_py["DEPGRAPH-FRESHNESS 门禁单测<br/>test_depgraph_freshness_gate.py —<br/>DEPGRAPH-FRESHNESS 门禁单测<br/>Test Depgraph Freshness Gate<br/>文件: commit_gates<br/>/test_depgraph_freshness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py["DEPGRAPH-PRE-REGISTRATION gate 测试<br/>test_depgraph_pre_registration_gate.py —<br/>DEPGRAPH-PRE-REGISTRATION gate 测试<br/>Test Depgraph Pre Registration Gate<br/>文件: commit_gates<br/>/test_depgraph_pre_registration_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_derived_file_deletion_gate_py["派生文件删除保护门禁单测<br/>test_derived_file_deletion_gate.py —<br/>派生文件删除保护门禁单测（DERIVED-FILE-...<br/>Test Derived File Deletion Gate<br/>文件: commit_gates<br/>/test_derived_file_deletion_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_diff_helpers_py["gate 共享 diff 解析工具模块单测<br/>test_diff_helpers.py — gate 共享 diff<br/>解析工具模块单测<br/>Test Diff Helpers<br/>文件: commit_gates/test_diff_helpers.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_doc_ref_broken_gate_py["DOC-REF-BROKEN 门禁单测<br/>test_doc_ref_broken_gate.py — DOC-REF-BROKEN<br/>门禁单测<br/>Test Doc Ref Broken Gate<br/>文件: commit_gates/test_doc_ref_broken_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_fk_gate_py["GATE-DOMAIN-FK 门禁单测<br/>test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测<br/>Test Domain Fk Gate<br/>文件: commit_gates/test_domain_fk_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py["NO-DOMAIN-NAME-ZH-DIRECT-ACCESS 门禁单测<br/>test_domain_name_zh_direct_access_gate.py —<br/>NO-DOMAIN-NAME-ZH-DIRECT-ACCESS ...<br/>Test Domain Name Zh Direct Access Gate<br/>文件: commit_gates<br/>/test_domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_empty_handler_gate_py["EMPTY-HANDLER 门禁单测<br/>test_empty_handler_gate.py — EMPTY-HANDLER<br/>门禁单测<br/>Test Empty Handler Gate<br/>文件: commit_gates/test_empty_handler_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py["EXEMPT-ZONE-FM 门禁单测<br/>test_exempt_zone_frontmatter_gate.py —<br/>EXEMPT-ZONE-FM 门禁单测<br/>Test Exempt Zone Frontmatter Gate<br/>文件: commit_gates<br/>/test_exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_file_copy_gate_py["FILE-COPY 门禁单测<br/>test_file_copy_gate.py — FILE-COPY 门禁单测<br/>Test File Copy Gate<br/>文件: commit_gates/test_file_copy_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_foreign_change_gate_py["外来变更检测门禁单测<br/>test_foreign_change_gate.py —<br/>外来变更检测门禁单测<br/>（FOREIGN-CHANGE-DETECTION...<br/>Test Foreign Change Gate<br/>文件: commit_gates/test_foreign_change_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_forged_gw_marker_gate_py["Forged GW Marker 前置检测门禁单测<br/>test_forged_gw_marker_gate.py — Forged GW<br/>Marker 前置检测门禁单测（...<br/>Test Forged Gw Marker Gate<br/>文件: commit_gates/test_forged_gw_marker_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_function_dup_gate_py["FUNCTION-DUP 门禁单测<br/>test_function_dup_gate.py — FUNCTION-DUP<br/>门禁单测<br/>Test Function Dup Gate<br/>文件: commit_gates/test_function_dup_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_god_class_gate_py["NO-GOD-CLASS 门禁单测<br/>test_god_class_gate.py — NO-GOD-CLASS 门禁单测<br/>Test God Class Gate<br/>文件: commit_gates/test_god_class_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_hardcoded_url_gate_py["NO-HARDCODED-URL 门禁单测<br/>test_hardcoded_url_gate.py — NO-HARDCODED-URL<br/>门禁单测<br/>Test Hardcoded Url Gate<br/>文件: commit_gates/test_hardcoded_url_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_held_overlap_gate_py["搭便车防护门禁单测<br/>test_held_overlap_gate.py — 搭便车防护门禁单测<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>Test Held Overlap Gate<br/>文件: commit_gates/test_held_overlap_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_high_complexity_gate_py["NO-HIGH-COMPLEXITY 门禁单测<br/>test_high_complexity_gate.py —<br/>NO-HIGH-COMPLEXITY 门禁单测<br/>Test High Complexity Gate<br/>文件: commit_gates/test_high_complexity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_id_uniqueness_gate_py["ID-UNIQUENESS 门禁单测<br/>test_id_uniqueness_gate.py — ID-UNIQUENESS<br/>门禁单测<br/>Test Id Uniqueness Gate<br/>文件: commit_gates/test_id_uniqueness_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_direction_gate_py["NO-UPWARD-IMPORT 门禁单测<br/>test_import_direction_gate.py —<br/>NO-UPWARD-IMPORT 门禁单测<br/>Test Import Direction Gate<br/>文件: commit_gates/test_import_direction_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_import_integrity_gate_py["IMPORT-INTEGRITY 门禁单测<br/>test_import_integrity_gate.py —<br/>IMPORT-INTEGRITY 门禁单测（...<br/>Test Import Integrity Gate<br/>文件: commit_gates/test_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_long_param_list_gate_py["NO-LONG-PARAM-LIST 门禁单测<br/>test_long_param_list_gate.py —<br/>NO-LONG-PARAM-LIST 门禁单测<br/>Test Long Param List Gate<br/>文件: commit_gates/test_long_param_list_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py["MANUAL-ONLY-PERMANENT m11 noqa 豁免单测<br/>test_manual_only_permanent_gate_noqa.py —<br/>MANUAL-ONLY-PERMANENT m11 noqa 豁...<br/>Test Manual Only Permanent Gate Noqa<br/>文件: commit_gates<br/>/test_manual_only_permanent_gate_noqa.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mcp_version_field_gate_py["MCP version 字段缺失硬阻断门禁单测<br/>test_mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁单测（MCP-VER...<br/>Test Mcp Version Field Gate<br/>文件: commit_gates<br/>/test_mcp_version_field_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_module_id_consistency_gate_py["module_id 三声明轨道一致性 + count 派生 +<br/>跨文件唯一性门禁单测<br/>test_module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生...<br/>Test Module Id Consistency Gate<br/>文件: commit_gates<br/>/test_module_id_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_exposure_gate_py["MSG-EXPOSURE 门禁单测<br/>test_msg_exposure_gate.py — MSG-EXPOSURE<br/>门禁单测<br/>Test Msg Exposure Gate<br/>文件: commit_gates/test_msg_exposure_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_msg_style_gate_py["MSG-STYLE 门禁单测<br/>test_msg_style_gate.py — MSG-STYLE 门禁单测<br/>Test Msg Style Gate<br/>文件: commit_gates/test_msg_style_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py["可变常量缺 Final 标注硬阻断门禁单测<br/>test_mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁单...<br/>Test Mutable Const Without Final Gate<br/>文件: commit_gates<br/>/test_mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_new_file_depgraph_gate_py["NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>test_new_file_depgraph_gate.py —<br/>NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测<br/>Test New File Depgraph Gate<br/>文件: commit_gates<br/>/test_new_file_depgraph_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_no_import_side_effect_gate_py["NO-IMPORT-SIDE-EFFECT 门禁单测<br/>test_no_import_side_effect_gate.py —<br/>NO-IMPORT-SIDE-EFFECT 门禁单测<br/>Test No Import Side Effect Gate<br/>文件: commit_gates<br/>/test_no_import_side_effect_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_open_without_with_gate_py["open<br/>test_open_without_with_gate.py — open() 未在<br/>with 内硬阻断门禁单测（OPEN-WIT...<br/>Test Open Without With Gate<br/>文件: commit_gates<br/>/test_open_without_with_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_orphan_module_gate_py["ORPHAN-MODULE 门禁单测<br/>test_orphan_module_gate.py — ORPHAN-MODULE<br/>门禁单测<br/>Test Orphan Module Gate<br/>文件: commit_gates/test_orphan_module_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_panorama_alignment_gate_py["四图模块对齐门禁单测<br/>test_panorama_alignment_gate.py —<br/>四图模块对齐门禁单测（GATE-PANORAMA-ALIGNM...<br/>Test Panorama Alignment Gate<br/>文件: commit_gates<br/>/test_panorama_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_perm_trigger_gate_py["PERM-TRIGGER 门禁单测<br/>test_perm_trigger_gate.py — PERM-TRIGGER<br/>门禁单测<br/>Test Perm Trigger Gate<br/>文件: commit_gates/test_perm_trigger_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_precommit_offline_gate_py["GATE-PRECOMMIT-OFFLINE 门禁单测<br/>test_precommit_offline_gate.py —<br/>GATE-PRECOMMIT-OFFLINE 门禁单测<br/>Test Precommit Offline Gate<br/>文件: commit_gates<br/>/test_precommit_offline_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_protected_paths_gate_py["受保护路径写入检测门禁单测<br/>test_protected_paths_gate.py —<br/>受保护路径写入检测门禁单测（...<br/>Test Protected Paths Gate<br/>文件: commit_gates/test_protected_paths_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["R5-DIGIT-SUFFIX 门禁单元测试<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX<br/>门禁单元测试<br/>Test R5 Digit Suffix Gate<br/>文件: commit_gates/test_r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_reconciler_health_gate_py["RECONCILER-HEALTH 门禁单测<br/>test_reconciler_health_gate.py —<br/>RECONCILER-HEALTH 门禁单测<br/>Test Reconciler Health Gate<br/>文件: commit_gates<br/>/test_reconciler_health_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py["RENAME-DEPGRAPH-SYNC 门禁单测<br/>test_rename_depgraph_sync_gate.py —<br/>RENAME-DEPGRAPH-SYNC 门禁单测<br/>Test Rename Depgraph Sync Gate<br/>文件: commit_gates<br/>/test_rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_execution_pairing_gate_py["Test Rule Execution Pairing Gate<br/>Tests for RULE-EXECUTION-PAIRING gate (Phase<br/>3.5).<br/>文件: commit_gates<br/>/test_rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py["RULE-FOUR-WAY-ALIGN 门禁单测<br/>test_rule_four_way_alignment_gate.py —<br/>RULE-FOUR-WAY-ALIGN 门禁单测<br/>Test Rule Four Way Alignment Gate<br/>文件: commit_gates<br/>/test_rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_commit_verified_gate_py["RULING-COMMIT-VERIFIED 门禁单测<br/>test_ruling_commit_verified_gate.py —<br/>RULING-COMMIT-VERIFIED 门禁单测。<br/>Test Ruling Commit Verified Gate<br/>文件: commit_gates<br/>/test_ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ruling_reference_gate_py["裁定#NNN 悬空引用检测门禁单测<br/>test_ruling_reference_gate.py — 裁定#NNN<br/>悬空引用检测门禁单测（RULING-REFERE...<br/>Test Ruling Reference Gate<br/>文件: commit_gates/test_ruling_reference_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_schema_file_exists_gate_py["SCHEMA-FILE-EXISTS 门禁单测<br/>test_schema_file_exists_gate.py —<br/>SCHEMA-FILE-EXISTS 门禁单测<br/>Test Schema File Exists Gate<br/>文件: commit_gates<br/>/test_schema_file_exists_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py["SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>test_scripts_import_integrity_gate.py —<br/>SCRIPTS-IMPORT-INTEGRITY 门禁单测<br/>Test Scripts Import Integrity Gate<br/>文件: commit_gates<br/>/test_scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_secret_hardcode_gate_py["NO-SECRET-HARDCODE 门禁单测<br/>test_secret_hardcode_gate.py —<br/>NO-SECRET-HARDCODE 门禁单测<br/>Test Secret Hardcode Gate<br/>文件: commit_gates/test_secret_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py["SECRET-REGISTRY-CONSISTENCY 门禁单测<br/>test_secret_registry_consistency_gate.py —<br/>SECRET-REGISTRY-CONSISTENCY 门禁单测<br/>Test Secret Registry Consistency Gate<br/>文件: commit_gates<br/>/test_secret_registry_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_session_required_gate_py["SESSION-REQUIRED 门禁单测<br/>test_session_required_gate.py —<br/>SESSION-REQUIRED 门禁单测<br/>Test Session Required Gate<br/>文件: commit_gates/test_session_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_ssot_redefinition_gate_py["SSoT 符号重复定义硬阻断门禁单测<br/>test_ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁单测（SSOT-REDEF...<br/>Test Ssot Redefinition Gate<br/>文件: commit_gates<br/>/test_ssot_redefinition_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_test_source_consistency_gate_py["TEST-SOURCE-CONSISTENCY 门禁单测<br/>test_test_source_consistency_gate.py —<br/>TEST-SOURCE-CONSISTENCY 门禁单测<br/>Test Test Source Consistency Gate<br/>文件: commit_gates<br/>/test_test_source_consistency_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_translation_coverage_gate_py["TRANSLATION-COVERAGE 门禁单测<br/>test_translation_coverage_gate.py —<br/>TRANSLATION-COVERAGE 门禁单测<br/>Test Translation Coverage Gate<br/>文件: commit_gates<br/>/test_translation_coverage_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_undefined_name_gate_py["UNDEFINED-NAME 门禁单测<br/>test_undefined_name_gate.py — UNDEFINED-NAME<br/>门禁单测<br/>Test Undefined Name Gate<br/>文件: commit_gates/test_undefined_name_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py["``**data`` 直接展开 warn 级门禁单测<br/>test_unsafe_dict_spread_gate.py — ``**data``<br/>直接展开 warn 级门禁单测（UNSAF...<br/>Test Unsafe Dict Spread Gate<br/>文件: commit_gates<br/>/test_unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_vocab_hardcode_gate_py["VOCAB-HARDCODE 门禁单测<br/>test_vocab_hardcode_gate.py — VOCAB-HARDCODE<br/>门禁单测<br/>Test Vocab Hardcode Gate<br/>文件: commit_gates/test_vocab_hardcode_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_worktree_required_gate_py["WORKTREE-REQUIRED 门禁单测<br/>test_worktree_required_gate.py —<br/>WORKTREE-REQUIRED 门禁单测<br/>Test Worktree Required Gate<br/>文件: commit_gates<br/>/test_worktree_required_gate.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py["ZEPHYR_ENV 直访硬阻断门禁单测<br/>test_zephyr_env_direct_access_gate.py —<br/>ZEPHYR_ENV 直访硬阻断门禁单测（ZEPHY...<br/>Test Zephyr Env Direct Access Gate<br/>文件: commit_gates<br/>/test_zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["P2-2 并发 session 文件级原子性测试<br/>test_claim_files_for_edit.py — P2-2 并发<br/>session 文件级原子性测试<br/>Test Claim Files For Edit<br/>文件: rule_bridge/test_claim_files_for_edit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_commit_gate_registry_py["CommitGateRegistry 单测<br/>test_commit_gate_registry.py —<br/>CommitGateRegistry 单测（架构债务 #AD-001 治本）<br/>Test Commit Gate Registry<br/>文件: rule_bridge/test_commit_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_emergency_commit_py["emergency_commit API 测试<br/>test_emergency_commit.py — emergency_commit API<br/>测试（Ruling:100PCT-AI-GOVER...<br/>Test Emergency Commit<br/>文件: rule_bridge/test_emergency_commit.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_gate_auto_registrar_py["gate_auto_registrar 单元测试<br/>test_gate_auto_registrar.py —<br/>gate_auto_registrar 单元测试（...<br/>Test Gate Auto Registrar<br/>文件: rule_bridge/test_gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["heartbeat daemon + 成本递增 smoke test<br/>test_heartbeat_daemon.py — heartbeat daemon +<br/>成本递增 smoke test（Ruling:10...<br/>Test Heartbeat Daemon<br/>文件: rule_bridge/test_heartbeat_daemon.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_py["worktree 物理隔离端到端测试<br/>test_session_worktree.py — worktree<br/>物理隔离端到端测试（FP-ISO.4C，2026-07-0...<br/>Test Session Worktree<br/>文件: rule_bridge/test_session_worktree.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_cli_py["session_worktree_cli CLI 测试<br/>test_session_worktree_cli.py —<br/>session_worktree_cli CLI 测试（治本遗留项#2, ...<br/>Test Session Worktree Cli<br/>文件: rule_bridge/test_session_worktree_cli.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_health_check_py["session_worktree_start 启动健康度自检测试<br/>test_session_worktree_health_check.py —<br/>session_worktree_start 启动健康度自...<br/>Test Session Worktree Health Check<br/>文件: rule_bridge<br/>/test_session_worktree_health_check.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py["_trusted_git_env 进程级隔离单测<br/>test_session_worktree_trusted_git_env.py —<br/>_trusted_git_env 进程级隔离单测（...<br/>Test Session Worktree Trusted Git Env<br/>文件: rule_bridge<br/>/test_session_worktree_trusted_git_env.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py["session lifecycle 工作区 clean 检查单测<br/>test_session_worktree_workspace_clean.py —<br/>session lifecycle 工作区 clean 检...<br/>Test Session Worktree Workspace Clean<br/>文件: rule_bridge<br/>/test_session_worktree_workspace_clean.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_pool_py["WorktreePool 端到端 smoke test<br/>test_worktree_pool.py — WorktreePool 端到端<br/>smoke test（ARCH-GIT-CALL-BUDGET...<br/>Test Worktree Pool<br/>文件: rule_bridge/test_worktree_pool.py<br/>(生产态 / production)"]
    tests_ops_test_shadow_canary_deploy_py["Shadow Canary 部署运行器单元测试<br/>test_shadow_canary_deploy.py — Shadow Canary<br/>部署运行器单元测试<br/>Test Shadow Canary Deploy<br/>文件: ops/test_shadow_canary_deploy.py<br/>(生产态 / production)"]
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
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py ~~~ tests_governance_commit_gates_test_secret_hardcode_gate_py
    tests_governance_commit_gates_test_secret_hardcode_gate_py ~~~ tests_governance_commit_gates_test_secret_registry_consistency_gate_py
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py ~~~ tests_governance_commit_gates_test_session_required_gate_py
    tests_governance_commit_gates_test_session_required_gate_py ~~~ tests_governance_commit_gates_test_ssot_redefinition_gate_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py ~~~ tests_governance_commit_gates_test_test_source_consistency_gate_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py ~~~ tests_governance_commit_gates_test_translation_coverage_gate_py
    tests_governance_commit_gates_test_translation_coverage_gate_py ~~~ tests_governance_commit_gates_test_undefined_name_gate_py
    tests_governance_commit_gates_test_undefined_name_gate_py ~~~ tests_governance_commit_gates_test_unsafe_dict_spread_gate_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py ~~~ tests_governance_commit_gates_test_vocab_hardcode_gate_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py ~~~ tests_governance_commit_gates_test_worktree_required_gate_py
    tests_governance_commit_gates_test_worktree_required_gate_py ~~~ tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py
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
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["Admission Response<br/>behavioral admission包的admission_response模块<br/>文件: behavioral_admission/admission_response.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["Code Review Ai<br/>behavioral admission包的code_review_ai模块<br/>文件: behavioral_admission/code_review_ai.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["—将 gate 结果写入 task_events<br/>GateEventAdapter — GateRepo 事件适配器<br/>（DW-0006）<br/>Gate Event Adapter<br/>文件: behavioral_admission/gate_event_adapter.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["Gpu Consensus Scheduler<br/>behavioral<br/>admission包的gpu_consensus_scheduler模块<br/>文件: behavioral_admission<br/>/gpu_consensus_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["Protection Index<br/>behavioral admission包的protection_index模块<br/>文件: behavioral_admission/protection_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["GitCommitGateway pre-commit 门禁注册表<br/>commit_gate_registry.py — GitCommitGateway<br/>pre-commit 门禁注册表（架构债务 #...<br/>Commit Gate Registry<br/>文件: rule_bridge/commit_gate_registry.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["Session Worktree<br/>session_worktree.py — AI 对话 worktree 物理隔离<br/>helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["Data Quality Gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["Admission Controller<br/>behavioral admission包的admission_controller模块<br/>文件: behavioral_admission<br/>/admission_controller.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["Verdict Engine<br/>behavioral admission包的verdict_engine模块<br/>文件: behavioral_admission/verdict_engine.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["紧急提交通道<br/>emergency_commit.py — 紧急提交通道<br/>（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>Emergency Commit<br/>文件: rule_bridge/emergency_commit.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["session heartbeat 独立进程<br/>heartbeat_daemon.py — session heartbeat<br/>独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>Heartbeat Daemon<br/>文件: rule_bridge/heartbeat_daemon.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["AI 对话并发声明 helper<br/>session_claim.py — AI 对话并发声明 helper<br/>（FP-ISO.4B 件2改，2026-07-01 治本）<br/>Session Claim<br/>文件: rule_bridge/session_claim.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["session worktree 物理隔离管理器<br/>worktree_manager.py — session worktree<br/>物理隔离管理器（阶段3 治本 stash 循环）<br/>Worktree Manager<br/>文件: rule_bridge/worktree_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["Worktree 预创建池<br/>worktree_pool.py — Worktree 预创建池<br/>（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>Worktree Pool<br/>文件: rule_bridge/worktree_pool.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["全项目唯一合法 git commit 入口<br/>GitCommitGateway — 全项目唯一合法 git commit<br/>入口（OPS-2026062512 治本）<br/>Git Commit Gateway<br/>文件: rule_bridge/git_commit_gateway.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["Reconciler 批量化 auto-commit 拦截器<br/>batched_auto_committer.py — Reconciler 批量化<br/>auto-commit 拦截器（ARCH-GIT-C...<br/>Batched Auto Committer<br/>文件: rule_bridge/batched_auto_committer.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_asyncio_run_in_context_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_getenv_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_subprocess_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_bare_sql_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_batch_size_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_capability_lookup_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ch_version_col_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_claim_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_pre_registration_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_derived_file_deletion_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_depgraph_freshness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_consumers_accuracy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_datetime_now_forbidden_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_doc_ref_broken_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_fk_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_file_copy_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_function_dup_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_forged_gw_marker_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_empty_handler_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_held_overlap_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_hardcoded_url_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_foreign_change_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_god_class_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_high_complexity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_id_uniqueness_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mcp_version_field_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_direction_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_exposure_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_long_param_list_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_mutable_const_without_final_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_msg_style_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_orphan_module_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_open_without_with_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_no_import_side_effect_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_new_file_depgraph_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_protected_paths_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_perm_trigger_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rename_depgraph_sync_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_rule_four_way_alignment_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_reconciler_health_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_precommit_offline_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_schema_file_exists_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_ssot_redefinition_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_secret_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_secret_registry_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_session_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_scripts_import_integrity_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_unsafe_dict_spread_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_translation_coverage_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_test_source_consistency_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_undefined_name_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_vocab_hardcode_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_worktree_required_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_commit_gate_registry_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_gate_auto_registrar_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    tests_governance_rule_bridge_test_session_worktree_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_health_check_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_session_worktree_workspace_clean_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    tests_governance_rule_bridge_test_worktree_pool_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_arch_reference_gate_py,tests_governance_commit_gates_test_asyncio_run_in_context_gate_py,tests_governance_commit_gates_test_bare_getenv_gate_py,tests_governance_commit_gates_test_bare_sql_gate_py,tests_governance_commit_gates_test_bare_subprocess_gate_py,tests_governance_commit_gates_test_blueprint_amodule_consistency_gate_py,tests_governance_commit_gates_test_blueprint_amodule_cross_check_gate_py,tests_governance_commit_gates_test_capability_lookup_audit_log_py,tests_governance_commit_gates_test_capability_lookup_bypass_policy_py,tests_governance_commit_gates_test_capability_lookup_required_gate_py,tests_governance_commit_gates_test_capability_overlap_gate_py,tests_governance_commit_gates_test_ch_batch_size_gate_py,tests_governance_commit_gates_test_ch_version_col_gate_py,tests_governance_commit_gates_test_claim_required_gate_py,tests_governance_commit_gates_test_consumers_accuracy_gate_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_dangling_reference_gate_py,tests_governance_commit_gates_test_datetime_now_forbidden_gate_py,tests_governance_commit_gates_test_depgraph_freshness_gate_py,tests_governance_commit_gates_test_depgraph_pre_registration_gate_py,tests_governance_commit_gates_test_derived_file_deletion_gate_py,tests_governance_commit_gates_test_diff_helpers_py,tests_governance_commit_gates_test_doc_ref_broken_gate_py,tests_governance_commit_gates_test_domain_fk_gate_py,tests_governance_commit_gates_test_domain_name_zh_direct_access_gate_py,tests_governance_commit_gates_test_empty_handler_gate_py,tests_governance_commit_gates_test_exempt_zone_frontmatter_gate_py,tests_governance_commit_gates_test_file_copy_gate_py,tests_governance_commit_gates_test_foreign_change_gate_py,tests_governance_commit_gates_test_forged_gw_marker_gate_py,tests_governance_commit_gates_test_function_dup_gate_py,tests_governance_commit_gates_test_god_class_gate_py,tests_governance_commit_gates_test_hardcoded_url_gate_py,tests_governance_commit_gates_test_held_overlap_gate_py,tests_governance_commit_gates_test_high_complexity_gate_py,tests_governance_commit_gates_test_id_uniqueness_gate_py,tests_governance_commit_gates_test_import_direction_gate_py,tests_governance_commit_gates_test_import_integrity_gate_py,tests_governance_commit_gates_test_long_param_list_gate_py,tests_governance_commit_gates_test_manual_only_permanent_gate_noqa_py,tests_governance_commit_gates_test_mcp_version_field_gate_py,tests_governance_commit_gates_test_module_id_consistency_gate_py,tests_governance_commit_gates_test_msg_exposure_gate_py,tests_governance_commit_gates_test_msg_style_gate_py,tests_governance_commit_gates_test_mutable_const_without_final_gate_py,tests_governance_commit_gates_test_new_file_depgraph_gate_py,tests_governance_commit_gates_test_no_import_side_effect_gate_py,tests_governance_commit_gates_test_open_without_with_gate_py,tests_governance_commit_gates_test_orphan_module_gate_py,tests_governance_commit_gates_test_panorama_alignment_gate_py,tests_governance_commit_gates_test_perm_trigger_gate_py,tests_governance_commit_gates_test_precommit_offline_gate_py,tests_governance_commit_gates_test_protected_paths_gate_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_commit_gates_test_reconciler_health_gate_py,tests_governance_commit_gates_test_rename_depgraph_sync_gate_py,tests_governance_commit_gates_test_rule_execution_pairing_gate_py,tests_governance_commit_gates_test_rule_four_way_alignment_gate_py,tests_governance_commit_gates_test_ruling_commit_verified_gate_py,tests_governance_commit_gates_test_ruling_reference_gate_py,tests_governance_commit_gates_test_schema_file_exists_gate_py,tests_governance_commit_gates_test_scripts_import_integrity_gate_py,tests_governance_commit_gates_test_secret_hardcode_gate_py,tests_governance_commit_gates_test_secret_registry_consistency_gate_py,tests_governance_commit_gates_test_session_required_gate_py,tests_governance_commit_gates_test_ssot_redefinition_gate_py,tests_governance_commit_gates_test_test_source_consistency_gate_py,tests_governance_commit_gates_test_translation_coverage_gate_py,tests_governance_commit_gates_test_undefined_name_gate_py,tests_governance_commit_gates_test_unsafe_dict_spread_gate_py,tests_governance_commit_gates_test_vocab_hardcode_gate_py,tests_governance_commit_gates_test_worktree_required_gate_py,tests_governance_commit_gates_test_zephyr_env_direct_access_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_commit_gate_registry_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_gate_auto_registrar_py,tests_governance_rule_bridge_test_heartbeat_daemon_py,tests_governance_rule_bridge_test_session_worktree_py,tests_governance_rule_bridge_test_session_worktree_cli_py,tests_governance_rule_bridge_test_session_worktree_health_check_py,tests_governance_rule_bridge_test_session_worktree_trusted_git_env_py,tests_governance_rule_bridge_test_session_worktree_workspace_clean_py,tests_governance_rule_bridge_test_worktree_pool_py,tests_ops_test_shadow_canary_deploy_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 1 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_ops_shadow_canary_deploy_py["影子金丝雀部署运行器<br/>把 4 个已有零件串成一条命令，做灰度发布的安全网<br/>：先检查能不能上线，再开个影子进程跑同样的输入但<br/>不接真券商，然后比对两边输出是否一致，分歧小就放<br/>行、分歧大就回滚。专门满足 EX-021 那半 CI/CD<br/>灰度门禁。<br/>Shadow Canary Deploy Runner<br/>Shadow Canary deploy runner orchestrating<br/>precheck/shadow/compare/state-machine,<br/>satisfying EX-021 CI/CD gate half<br/>文件: ops/shadow_canary_deploy.py<br/>(设计态 / design)"]
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_ops_shadow_canary_deploy_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_AUTONOMY_CORE 自治核心: 影子金丝雀 / shadow_canary (context/shadow_canary.py) | 导入依赖 / import_depends |
| 2 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | 导入依赖 / import_depends |
| 3 | Init / Init (behavioral_admission/__init__.py) | → | D_GOVERNANCE 生命周期管理: worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | 导入依赖 / import_depends |
| 4 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 5 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 6 | capability_lookup audit log 落盘 e2e smoke test / Test Ca... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 7 | CAPABILITY-OVERLAP 门禁单测 / Test Capability Overlap Gat... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 8 | NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测 / Test New File De... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 测试依赖 / test_depends |
| 9 | SSoT 符号重复定义硬阻断门禁单测 / Test Ssot Redefinition ... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 测试依赖 / test_depends |
| 10 | dashboard 指标数描述派生校验 reconciler / Metric Count Dr... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 11 | README 版本号派生展示校验 reconciler / Readme Version Syn... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 12 | requirements.txt ↔ pyproject.toml 依赖一致性校验 reconci... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 13 | Init / Init (behavioral_admission/__init__.py) | → | D_GOV_AUDIT 审计追踪: MCP结果推送 / mcp_result_push (behavioral_admission/mcp_r... | 导入依赖 / import_depends |
| 14 | Init / Init (behavioral_admission/__init__.py) | → | D_GOV_AUDIT 审计追踪: 提交进程 / post_process (behavioral_admission/post_proces... | 导入依赖 / import_depends |
| 15 | Init / Init (behavioral_admission/__init__.py) | → | D_GOV_AUDIT 审计追踪: vibecoding执行器 / vibe_coding_enforcer (behavioral_admis... | 导入依赖 / import_depends |
| 16 | —将 gate 结果写入 task_events / Gate Event Adapter (beha... | → | D_GOV_AUDIT 审计追踪: 事件存储 / event_store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 17 | Verdict Engine / Verdict Engine (behavioral_admission/ver... | → | D_GOV_AUDIT 审计追踪: 审计事件类型枚举——治本（裁定#18 G2）：转为真 Enu / mode... | 导入依赖 / import_depends |
| 18 | 紧急提交通道 / Emergency Commit (rule_bridge/emergency_co... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 19 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 蓝图状态转换协调器 / blueprint_status_transition_reconcil... | 导入依赖 / import_depends |
| 20 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: commitgatewayabuse监控器对账器 / commit_gateway_abuse_mon... | 导入依赖 / import_depends |
| 21 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 跨layercontractsignature对账器 / cross_layer_contract_sig... | 导入依赖 / import_depends |
| 22 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 死公共 wrapper 自动检测 reconciler. / Dead Public Wrapper... | 导入依赖 / import_depends |
| 23 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 错误模式消费者协调器 / error_pattern_consumer_reconciler ... | 导入依赖 / import_depends |
| 24 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: git_guard alias 绕过检测 post-commit reconciler / Git Gua... | 导入依赖 / import_depends |
| 25 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: Git绩效监控协调器 / git_performance_monitor_reconciler (a... | 导入依赖 / import_depends |
| 26 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 27 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 28 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 修复进度对账器 / remediation_progress_reconciler (audit/r... | 导入依赖 / import_depends |
| 29 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 运行时违规快照协调器 / runtime_violation_snapshot_reconci... | 导入依赖 / import_depends |
| 30 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 翻译覆盖率存量对账 reconciler. / Translation Coverage Rec... | 导入依赖 / import_depends |
| 31 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 32 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_AUDIT 审计追踪: AI错误模式库 / ai_error_pattern_library (audit/ai_error_p... | 导入依赖 / import_depends |
| 33 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_AUDIT 审计追踪: 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | 导入依赖 / import_depends |
| 34 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 35 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 36 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_CODE_QUALITY 代码质量治理: YAML 驱动的 in-process gate 自动注册器 / Gate Auto Regist... | 导入依赖 / import_depends |
| 37 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_CODE_QUALITY 代码质量治理: 包入口 / __init__ (commit_gates/__init__.py) | 导入依赖 / import_depends |
| 38 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 导入依赖 / import_depends |
| 39 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_GOV_CODE_QUALITY 代码质量治理: 测试-源码符号一致性门禁 / Test Source Consistency Gate (c... | 导入依赖 / import_depends |
| 40 | #ARCH-NNN 悬空引用检测门禁单测 / Test Arch Reference Gate... | → | D_GOV_CODE_QUALITY 代码质量治理: reference辅助 / _reference_helpers (commit_gates/_referen... | 测试依赖 / test_depends |
| 41 | #ARCH-NNN 悬空引用检测门禁单测 / Test Arch Reference Gate... | → | D_GOV_CODE_QUALITY 代码质量治理: archreference门禁 / arch_reference_gate (commit_gates/arc... | 测试依赖 / test_depends |
| 42 | asyncio API 误用硬阻断门禁单测 / Test Asyncio Run In Cont... | → | D_GOV_CODE_QUALITY 代码质量治理: asynciorunin上下文门禁 / asyncio_run_in_context_gate (com... | 测试依赖 / test_depends |
| 43 | NO-BARE-GETENV 门禁单测 / Test Bare Getenv Gate (commit_g... | → | D_GOV_CODE_QUALITY 代码质量治理: baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | 测试依赖 / test_depends |
| 44 | NO-BARE-SQL 门禁单测 / Test Bare Sql Gate (commit_gates/t... | → | D_GOV_CODE_QUALITY 代码质量治理: baresql门禁 / bare_sql_gate (commit_gates/bare_sql_gate.py) | 测试依赖 / test_depends |
| 45 | BARE-SUBPROCESS 门禁单测 / Test Bare Subprocess Gate (com... | → | D_GOV_CODE_QUALITY 代码质量治理: baresubprocess门禁 / bare_subprocess_gate (commit_gates/b... | 测试依赖 / test_depends |
| 46 | BLUEPRINT-AMODULE-CONSISTENCY 门禁单测 / Test Blueprint A... | → | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amoduleconsistency门禁 / blueprint_amodule_consistenc... | 测试依赖 / test_depends |
| 47 | BLUEPRINT-AMODULE-CROSS-CHECK 门禁单测 / Test Blueprint A... | → | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule跨check门禁 / blueprint_amodule_cross_check_ga... | 测试依赖 / test_depends |
| 48 | capability_lookup audit log 落盘 e2e smoke test / Test Ca... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 测试依赖 / test_depends |
| 49 | CAPABILITY-LOOKUP bypass 策略共享模块单测 / Test Capabili... | → | D_GOV_CODE_QUALITY 代码质量治理: 包入口 / __init__ (commit_gates/__init__.py) | 测试依赖 / test_depends |
| 50 | CAPABILITY-LOOKUP bypass 策略共享模块单测 / Test Capabili... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookup绕过策略 / capability_lookup_bypass_polic... | 测试依赖 / test_depends |
| 51 | CAPABILITY-LOOKUP-REQUIRED 门禁单测 / Test Capability Loo... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | 测试依赖 / test_depends |
| 52 | CAPABILITY-OVERLAP 门禁单测 / Test Capability Overlap Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: capabilityoverlap门禁 / capability_overlap_gate (commit_g... | 测试依赖 / test_depends |
| 53 | CH-BATCH-SIZE 门禁单测 / Test Ch Batch Size Gate (commit_... | → | D_GOV_CODE_QUALITY 代码质量治理: ch批次大小门禁 / ch_batch_size_gate (commit_gates/ch_batc... | 测试依赖 / test_depends |
| 54 | CH-VERSION-COL 门禁单测 / Test Ch Version Col Gate (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: ch版本col门禁 / ch_version_col_gate (commit_gates/ch_vers... | 测试依赖 / test_depends |
| 55 | claim_files 前置检查门禁单测 / Test Claim Required Gate (... | → | D_GOV_CODE_QUALITY 代码质量治理: claimrequired门禁 / claim_required_gate (commit_gates/cla... | 测试依赖 / test_depends |
| 56 | CONSUMERS-ACCURACY 门禁单测 / Test Consumers Accuracy Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 测试依赖 / test_depends |
| 57 | CREATE-GUARD 门禁单元测试 / Test Create Guard (commit_gat... | → | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | 测试依赖 / test_depends |
| 58 | AGENTS.md §X.Y 悬空引用检测门禁单测 / Test Dangling Refe... | → | D_GOV_CODE_QUALITY 代码质量治理: danglingreference门禁 / dangling_reference_gate (commit_g... | 测试依赖 / test_depends |
| 59 | 生成器代码 datetime.now / Test Datetime Now Forbidden Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: datetimenowforbidden门禁 / datetime_now_forbidden_gate (c... | 测试依赖 / test_depends |
| 60 | DEPGRAPH-FRESHNESS 门禁单测 / Test Depgraph Freshness Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: depgraphfreshness门禁 / depgraph_freshness_gate (commit_g... | 测试依赖 / test_depends |
| 61 | DEPGRAPH-PRE-REGISTRATION gate 测试 / Test Depgraph Pre R... | → | D_GOV_CODE_QUALITY 代码质量治理: depgraph planned→production 流转强制门禁 / Depgraph Pre ... | 测试依赖 / test_depends |
| 62 | 派生文件删除保护门禁单测 / Test Derived File Deletion Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: 派生文件删除保护门禁 / Derived File Deletion Gate (commit... | 测试依赖 / test_depends |
| 63 | gate 共享 diff 解析工具模块单测 / Test Diff Helpers (comm... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 测试依赖 / test_depends |
| 64 | DOC-REF-BROKEN 门禁单测 / Test Doc Ref Broken Gate (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: docrefbroken门禁 / doc_ref_broken_gate (commit_gates/doc_... | 测试依赖 / test_depends |
| 65 | GATE-DOMAIN-FK 门禁单测 / Test Domain Fk Gate (commit_gat... | → | D_GOV_CODE_QUALITY 代码质量治理: 域fk门禁 / domain_fk_gate (commit_gates/domain_fk_gate.py) | 测试依赖 / test_depends |
| 66 | NO-DOMAIN-NAME-ZH-DIRECT-ACCESS 门禁单测 / Test Domain Na... | → | D_GOV_CODE_QUALITY 代码质量治理: domainnamezhdirect访问门禁 / domain_name_zh_direct_access... | 测试依赖 / test_depends |
| 67 | EMPTY-HANDLER 门禁单测 / Test Empty Handler Gate (commit_... | → | D_GOV_CODE_QUALITY 代码质量治理: empty处理器门禁 / empty_handler_gate (commit_gates/empty_... | 测试依赖 / test_depends |
| 68 | EXEMPT-ZONE-FM 门禁单测 / Test Exempt Zone Frontmatter Ga... | → | D_GOV_CODE_QUALITY 代码质量治理: exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | 测试依赖 / test_depends |
| 69 | FILE-COPY 门禁单测 / Test File Copy Gate (commit_gates/te... | → | D_GOV_CODE_QUALITY 代码质量治理: filecopy门禁 / file_copy_gate (commit_gates/file_copy_gat... | 测试依赖 / test_depends |
| 70 | 外来变更检测门禁单测 / Test Foreign Change Gate (commit_g... | → | D_GOV_CODE_QUALITY 代码质量治理: foreignchange门禁 / foreign_change_gate (commit_gates/for... | 测试依赖 / test_depends |
| 71 | Forged GW Marker 前置检测门禁单测 / Test Forged Gw Marker... | → | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | 测试依赖 / test_depends |
| 72 | FUNCTION-DUP 门禁单测 / Test Function Dup Gate (commit_ga... | → | D_GOV_CODE_QUALITY 代码质量治理: 函数dup门禁 / function_dup_gate (commit_gates/function_du... | 测试依赖 / test_depends |
| 73 | NO-GOD-CLASS 门禁单测 / Test God Class Gate (commit_gates... | → | D_GOV_CODE_QUALITY 代码质量治理: god类门禁 / god_class_gate (commit_gates/god_class_gate.py) | 测试依赖 / test_depends |
| 74 | NO-HARDCODED-URL 门禁单测 / Test Hardcoded Url Gate (comm... | → | D_GOV_CODE_QUALITY 代码质量治理: hardcodedurl门禁 / hardcoded_url_gate (commit_gates/hardc... | 测试依赖 / test_depends |
| 75 | 搭便车防护门禁单测 / Test Held Overlap Gate (commit_gates... | → | D_GOV_CODE_QUALITY 代码质量治理: heldoverlap门禁 / held_overlap_gate (commit_gates/held_ov... | 测试依赖 / test_depends |
| 76 | NO-HIGH-COMPLEXITY 门禁单测 / Test High Complexity Gate (... | → | D_GOV_CODE_QUALITY 代码质量治理: highcomplexity门禁 / high_complexity_gate (commit_gates/h... | 测试依赖 / test_depends |
| 77 | ID-UNIQUENESS 门禁单测 / Test Id Uniqueness Gate (commit_... | → | D_GOV_CODE_QUALITY 代码质量治理: iduniqueness门禁 / id_uniqueness_gate (commit_gates/id_un... | 测试依赖 / test_depends |
| 78 | NO-UPWARD-IMPORT 门禁单测 / Test Import Direction Gate (c... | → | D_GOV_CODE_QUALITY 代码质量治理: importdirection门禁 / import_direction_gate (commit_gates... | 测试依赖 / test_depends |
| 79 | IMPORT-INTEGRITY 门禁单测 / Test Import Integrity Gate (c... | → | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | 测试依赖 / test_depends |
| 80 | NO-LONG-PARAM-LIST 门禁单测 / Test Long Param List Gate (... | → | D_GOV_CODE_QUALITY 代码质量治理: longparamlist门禁 / long_param_list_gate (commit_gates/lo... | 测试依赖 / test_depends |
| 81 | MANUAL-ONLY-PERMANENT m11 noqa 豁免单测 / Test Manual Onl... | → | D_GOV_CODE_QUALITY 代码质量治理: 手册onlypermanent门禁 / manual_only_permanent_gate (commi... | 测试依赖 / test_depends |
| 82 | MCP version 字段缺失硬阻断门禁单测 / Test Mcp Version Fie... | → | D_GOV_CODE_QUALITY 代码质量治理: MCP版本字段门禁 / mcp_version_field_gate (commit_gates/mc... | 测试依赖 / test_depends |
| 83 | module_id 三声明轨道一致性 + count 派生 + 跨文件唯一性门... | → | D_GOV_CODE_QUALITY 代码质量治理: 模块id一致性门禁 / module_id_consistency_gate (commit_gat... | 测试依赖 / test_depends |
| 84 | MSG-EXPOSURE 门禁单测 / Test Msg Exposure Gate (commit_ga... | → | D_GOV_CODE_QUALITY 代码质量治理: msg敞口门禁 / msg_exposure_gate (commit_gates/msg_exposur... | 测试依赖 / test_depends |
| 85 | MSG-STYLE 门禁单测 / Test Msg Style Gate (commit_gates/te... | → | D_GOV_CODE_QUALITY 代码质量治理: msgstyle门禁 / msg_style_gate (commit_gates/msg_style_gat... | 测试依赖 / test_depends |
| 86 | 可变常量缺 Final 标注硬阻断门禁单测 / Test Mutable Const ... | → | D_GOV_CODE_QUALITY 代码质量治理: mutableconstwithoutfinal门禁 / mutable_const_without_fina... | 测试依赖 / test_depends |
| 87 | NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测 / Test New File De... | → | D_GOV_CODE_QUALITY 代码质量治理: 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | 测试依赖 / test_depends |
| 88 | NO-IMPORT-SIDE-EFFECT 门禁单测 / Test No Import Side Effe... | → | D_GOV_CODE_QUALITY 代码质量治理: noimportsideeffect门禁 / no_import_side_effect_gate (comm... | 测试依赖 / test_depends |
| 89 | open / Test Open Without With Gate (commit_gates/test_ope... | → | D_GOV_CODE_QUALITY 代码质量治理: openwithoutwith门禁 / open_without_with_gate (commit_gate... | 测试依赖 / test_depends |
| 90 | ORPHAN-MODULE 门禁单测 / Test Orphan Module Gate (commit_... | → | D_GOV_CODE_QUALITY 代码质量治理: 孤儿module门禁 / orphan_module_gate (commit_gates/orphan_... | 测试依赖 / test_depends |
| 91 | 四图模块对齐门禁单测 / Test Panorama Alignment Gate (comm... | → | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | 测试依赖 / test_depends |
| 92 | PERM-TRIGGER 门禁单测 / Test Perm Trigger Gate (commit_ga... | → | D_GOV_CODE_QUALITY 代码质量治理: permtrigger门禁 / perm_trigger_gate (commit_gates/perm_tr... | 测试依赖 / test_depends |
| 93 | GATE-PRECOMMIT-OFFLINE 门禁单测 / Test Precommit Offline ... | → | D_GOV_CODE_QUALITY 代码质量治理: precommitoffline门禁 / precommit_offline_gate (commit_gat... | 测试依赖 / test_depends |
| 94 | 受保护路径写入检测门禁单测 / Test Protected Paths Gate (c... | → | D_GOV_CODE_QUALITY 代码质量治理: 受保护路径写入检测门禁 / Protected Paths Gate (commit_gat... | 测试依赖 / test_depends |
| 95 | R5-DIGIT-SUFFIX 门禁单元测试 / Test R5 Digit Suffix Gate ... | → | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | 测试依赖 / test_depends |
| 96 | RECONCILER-HEALTH 门禁单测 / Test Reconciler Health Gate ... | → | D_GOV_CODE_QUALITY 代码质量治理: reconciler 健康度门禁 / Reconciler Health Gate (commit_ga... | 测试依赖 / test_depends |
| 97 | RENAME-DEPGRAPH-SYNC 门禁单测 / Test Rename Depgraph Sync... | → | D_GOV_CODE_QUALITY 代码质量治理: 文件重命名后 depgraph 未同步阻断门禁 / Rename Depgraph Sy... | 测试依赖 / test_depends |
| 98 | Test Rule Execution Pairing Gate / Test Rule Execution Pa... | → | D_GOV_CODE_QUALITY 代码质量治理: 规则-执行配对门禁 / Rule Execution Pairing Gate (commit_g... | 测试依赖 / test_depends |
| 99 | RULE-FOUR-WAY-ALIGN 门禁单测 / Test Rule Four Way Alignme... | → | D_GOV_CODE_QUALITY 代码质量治理: 规则四方对齐门禁 / Rule Four Way Alignment Gate (commit_g... | 测试依赖 / test_depends |
| 100 | RULING-COMMIT-VERIFIED 门禁单测 / Test Ruling Commit Veri... | → | D_GOV_CODE_QUALITY 代码质量治理: 文档"已完成"声明 commit hash 真实性硬验证门禁 / Ruling Co... | 测试依赖 / test_depends |
| 101 | 裁定#NNN 悬空引用检测门禁单测 / Test Ruling Reference Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: 裁定#NNN 悬空引用自动检测门禁 / Ruling Reference Gate (co... | 测试依赖 / test_depends |
| 102 | SCHEMA-FILE-EXISTS 门禁单测 / Test Schema File Exists Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 测试依赖 / test_depends |
| 103 | SCHEMA-FILE-EXISTS 门禁单测 / Test Schema File Exists Gat... | → | D_GOV_CODE_QUALITY 代码质量治理: SCHEMA-FILE-EXISTS block 门禁 / Schema File Exists Gate (... | 测试依赖 / test_depends |
| 104 | SCRIPTS-IMPORT-INTEGRITY 门禁单测 / Test Scripts Import I... | → | D_GOV_CODE_QUALITY 代码质量治理: _shared.constants 符号导入完整性门禁 / Scripts Import Int... | 测试依赖 / test_depends |
| 105 | NO-SECRET-HARDCODE 门禁单测 / Test Secret Hardcode Gate (... | → | D_GOV_CODE_QUALITY 代码质量治理: 密钥值硬编码阻断门禁 (commit_gates/secret_hardcode_gate.py) | 测试依赖 / test_depends |
| 106 | SECRET-REGISTRY-CONSISTENCY 门禁单测 / Test Secret Regist... | → | D_GOV_CODE_QUALITY 代码质量治理: 密钥注册表一致性门禁 (commit_gates/secret_registry_consis... | 测试依赖 / test_depends |
| 107 | SESSION-REQUIRED 门禁单测 / Test Session Required Gate (c... | → | D_GOV_CODE_QUALITY 代码质量治理: session 注册强制门禁 / Session Required Gate (commit_gate... | 测试依赖 / test_depends |
| 108 | SSoT 符号重复定义硬阻断门禁单测 / Test Ssot Redefinition ... | → | D_GOV_CODE_QUALITY 代码质量治理: SSoT 符号重复定义硬阻断门禁 / Ssot Redefinition Gate (com... | 测试依赖 / test_depends |
| 109 | TEST-SOURCE-CONSISTENCY 门禁单测 / Test Test Source Consi... | → | D_GOV_CODE_QUALITY 代码质量治理: 测试-源码符号一致性门禁 / Test Source Consistency Gate (c... | 测试依赖 / test_depends |
| 110 | TRANSLATION-COVERAGE 门禁单测 / Test Translation Coverage... | → | D_GOV_CODE_QUALITY 代码质量治理: 新建 .py 文件大白话简介覆盖率门禁 / Translation Coverage ... | 测试依赖 / test_depends |
| 111 | UNDEFINED-NAME 门禁单测 / Test Undefined Name Gate (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: UNDEFINED-NAME 门禁 / Undefined Name Gate (commit_gates/u... | 测试依赖 / test_depends |
| 112 | ``**data`` 直接展开 warn 级门禁单测 / Test Unsafe Dict Sp... | → | D_GOV_CODE_QUALITY 代码质量治理: ``**data`` 直接展开模式 warn 级门禁 / Unsafe Dict Spread ... | 测试依赖 / test_depends |
| 113 | VOCAB-HARDCODE 门禁单测 / Test Vocab Hardcode Gate (commi... | → | D_GOV_CODE_QUALITY 代码质量治理: 新增 .py 文件词表硬编码阻断门禁 / Vocab Hardcode Gate (co... | 测试依赖 / test_depends |
| 114 | WORKTREE-REQUIRED 门禁单测 / Test Worktree Required Gate ... | → | D_GOV_CODE_QUALITY 代码质量治理: worktree 隔离强制门禁 / Worktree Required Gate (commit_ga... | 测试依赖 / test_depends |
| 115 | ZEPHYR_ENV 直访硬阻断门禁单测 / Test Zephyr Env Direct Ac... | → | D_GOV_CODE_QUALITY 代码质量治理: ZEPHYR_ENV 直访硬阻断门禁 / Zephyr Env Direct Access Gate... | 测试依赖 / test_depends |
| 116 | gate_auto_registrar 单元测试 / Test Gate Auto Registrar (... | → | D_GOV_CODE_QUALITY 代码质量治理: YAML 驱动的 in-process gate 自动注册器 / Gate Auto Regist... | 测试依赖 / test_depends |
| 117 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: ZephyrAlpha 施工阶段门控引擎. / Phase Manager (ops_govern... | 导入依赖 / import_depends |
| 118 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_GOV_RULE 规则治理: 预部署门禁 / Can-I-Deploy (rule_enforcement/can_i_deploy.py) | 导入依赖 / import_depends |
| 119 | Shadow Canary 部署运行器单元测试 / Test Shadow Canary Dep... | → | D_GOV_RULE 规则治理: 预部署门禁 / Can-I-Deploy (rule_enforcement/can_i_deploy.py) | 测试依赖 / test_depends |
| 120 | dashboard 指标数描述派生校验 reconciler / Metric Count Dr... | → | D_GOV_SCRIPTS 脚本治理: 架构健康度仪表盘 / Architecture Health Dashboard (governa... | 导入依赖 / import_depends |
| 121 | session worktree 管理 CLI / Session Worktree Cli (governa... | → | D_GOV_SCRIPTS 脚本治理: 标记 depgraph / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 122 | ComplianceRule 真源已合并至 zephyr.shared.contracts.compl... | → | D_INFRASTRUCTURE 跨层契约基础设施: Compliance Rule / Compliance Rule (contracts/compliance_r... | 导入依赖 / import_depends |
| 123 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_INFRA_RUNTIME 运行时集成: Git 命令批量化工具 / Git Batcher (infrastructure/git_batc... | 导入依赖 / import_depends |
| 124 | Approval / Approval (rule_enforcement/approval.py) | → | D_INTEGRATION 管线路由: Approval Types / Approval Types (contracts/approval_types... | 导入依赖 / import_depends |
| 125 | CAPABILITY-LOOKUP-REQUIRED 门禁单测 / Test Capability Loo... | → | D_INTEGRATION 管线路由: MCP Server for rule discovery / Rule Discovery Server (mc... | 测试依赖 / test_depends |
| 126 | 只读：engine / Pre Flight Gate (rule_enforcement/pre_flig... | → | D_OPS 反馈循环: —5.133.2 DI 注入契约 / Budget Engine (ops_governance/bud... | 导入依赖 / import_depends |
| 127 | 只读：engine / Pre Flight Gate (rule_enforcement/pre_flig... | → | D_OPS 反馈循环: Budget Models / Budget Models (ops_governance/budget_mode... | 导入依赖 / import_depends |
| 128 | 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | D_SECURITY 对抗验证: 灰度发布管理器. / Canary Rollout Manager (access_control/... | 导入依赖 / import_depends |
| 129 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 130 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_SECURITY 对抗验证: Commit Trigger / Commit Trigger (adversarial_validation/c... | 导入依赖 / import_depends |
| 131 | session heartbeat 独立进程 / Heartbeat Daemon (rule_bridg... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 132 | AI 对话并发声明 helper / Session Claim (rule_bridge/sessi... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 133 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 134 | IMPORT-INTEGRITY 门禁单测 / Test Import Integrity Gate (c... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 135 | P2-2 并发 session 文件级原子性测试 / Test Claim Files For... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 136 | worktree 物理隔离端到端测试 / Test Session Worktree (rule... | → | D_SECURITY 对抗验证: Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 137 | session worktree 管理 CLI / Session Worktree Cli (governa... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 138 | —将 gate 结果写入 task_events / Gate Event Adapter (beha... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 139 | Gpu Consensus Scheduler / Gpu Consensus Scheduler (behavi... | → | D_SHARED 共享服务: Constants / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 140 | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 141 | 紧急提交通道 / Emergency Commit (rule_bridge/emergency_co... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 142 | 紧急提交通道 / Emergency Commit (rule_bridge/emergency_co... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 143 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_SHARED 共享服务: 任务生命周期事件类型 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 144 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 145 | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 146 | AI 对话并发声明 helper / Session Claim (rule_bridge/sessi... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 147 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 148 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 149 | Session Worktree / Session Worktree (rule_bridge/session_... | → | D_SHARED 共享服务: 主工作区文件操作遥测公共 API / Workspace Telemetry (io/wo... | 导入依赖 / import_depends |
| 150 | session worktree 物理隔离管理器 / Worktree Manager (rule_... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 151 | session worktree 物理隔离管理器 / Worktree Manager (rule_... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 152 | Worktree 预创建池 / Worktree Pool (rule_bridge/worktree_p... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 153 | Worktree 预创建池 / Worktree Pool (rule_bridge/worktree_p... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 154 | 对接 shared/events/dlq.DeadLetterQueue 的真重试 / Dlq Ret... | → | D_SHARED 共享服务: 5.63.2 修复：对 traceback / error 字符串脱敏，防止敏感信... | 导入依赖 / import_depends |
| 155 | 对接 shared/events/dlq.DeadLetterQueue 的真重试 / Dlq Ret... | → | D_SHARED 共享服务: Observer / Observer (infra/observer.py) | 导入依赖 / import_depends |
| 156 | 对接 shared/events/dlq.DeadLetterQueue 的真重试 / Dlq Ret... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 157 | mtime 轮询 + 自动同步 + 验证 / Rule Watcher (rule_engine/... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 158 | mtime 轮询 + 自动同步 + 验证 / Rule Watcher (rule_engine/... | → | D_SHARED 共享服务: 对连接应用 KBG-0030 §4.3 PRAGMA 基线 / Sqlite Factory (i... | 导入依赖 / import_depends |
| 159 | gate_auto_registrar 单元测试 / Test Gate Auto Registrar (... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 测试依赖 / test_depends |
| 160 | worktree 物理隔离端到端测试 / Test Session Worktree (rule... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 测试依赖 / test_depends |
| 161 | WorktreePool 端到端 smoke test / Test Worktree Pool (rule... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_DATA 数据接入层: 质量门禁 / quality_gate (data/quality_gate.py) | → | Data Quality Gate / Quality Gate (rule_enforcement/qualit... | 导入依赖 / import_depends |
| 2 | D_DATA 数据接入层: 包入口 / D_DATA Data Source (satellite_geospatial_engine/... | → | Data Quality Gate / Quality Gate (rule_enforcement/qualit... | 导入依赖 / import_depends |
| 3 | D_DATA 数据接入层: #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。 / tes... | → | Data Quality Gate / Quality Gate (rule_enforcement/qualit... | 测试依赖 / test_depends |
| 4 | D_GOVERNANCE 生命周期管理: Git提交 / git_commit (scripts/git_commit.py) | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: 合规管理器 / compliance_manager (compliance_gate_a6/compl... | → | ComplianceRule 真源已合并至 zephyr.shared.contracts.compl... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: 测试会话感知stashredblue / test_session_aware_stash_red_b... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 8 | D_GOVERNANCE 生命周期管理: 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 测试依赖 / test_depends |
| 9 | D_GOVERNANCE 生命周期管理: 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 10 | D_GOVERNANCE 生命周期管理: 测试Gitcommitextreme / test_git_commit_extreme (git/test_... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 11 | D_GOVERNANCE 生命周期管理: 测试Git提交网关 / test_git_commit_gateway (git/test_git_c... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 12 | D_GOVERNANCE 生命周期管理: Test Approval / Test Approval (access_control/test_approv... | → | Approval / Approval (rule_enforcement/approval.py) | 测试依赖 / test_depends |
| 13 | D_GOVERNANCE 生命周期管理: META-TESTS-COVERAGE meta-gate 单测 / Test Tests Coverage ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 测试依赖 / test_depends |
| 14 | D_GOVERNANCE 生命周期管理: Akshare 真实数据端到端测试 / Test Akshare Real Data (data... | → | Default Data Quality Gate / Default Quality Gate (rule_en... | 测试依赖 / test_depends |
| 15 | D_GOVERNANCE 生命周期管理: Test Slo Contract / Test Slo Contract (integration/test_s... | → | D-022-12. / Slo Contract (rule_enforcement/slo_contract.py) | 测试依赖 / test_depends |
| 16 | D_GOVERNANCE 生命周期管理: Escalation → RBAC 集成测试.""" / Test Gct 004 Escalation... | → | Approval / Approval (rule_enforcement/approval.py) | 测试依赖 / test_depends |
| 17 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言""" / Test P0 U1... | → | Approval / Approval (rule_enforcement/approval.py) | 测试依赖 / test_depends |
| 18 | D_GOVERNANCE 生命周期管理: Test E2e Pipeline / Test E2e Pipeline (trading/test_e2e_p... | → | Default Data Quality Gate / Default Quality Gate (rule_en... | 测试依赖 / test_depends |
| 19 | D_GOVERNANCE 生命周期管理: 测试taskrepogatewaye2e / test_task_repo_gateway_e2e (task... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 20 | D_GOV_AUDIT 审计追踪: Git绩效监控协调器 / git_performance_monitor_reconciler (a... | → | Session Worktree / Session Worktree (rule_bridge/session_... | 导入依赖 / import_depends |
| 21 | D_GOV_AUDIT 审计追踪: 对账工作器 / reconcile_worker (audit/reconcile_worker.py) | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 导入依赖 / import_depends |
| 22 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 23 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | Session Worktree / Session Worktree (rule_bridge/session_... | 导入依赖 / import_depends |
| 24 | D_GOV_AUDIT 审计追踪: 翻译覆盖率存量对账 reconciler. / Translation Coverage Rec... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 25 | D_GOV_AUDIT 审计追踪: Phase 4 G6 监控 reconciler e2e smoke test / Test Capabili... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 26 | D_GOV_AUDIT 审计追踪: GATE-INTEGRITY-AUDIT reconciler 单测 / Test Integrity Aud... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 27 | D_GOV_AUDIT 审计追踪: 测试对账异步 / test_reconcile_async (audit/test_reconcile... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 28 | D_GOV_AUDIT 审计追踪: 测试对账工作进程selfheal / test_reconcile_worker_selfheal... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 测试依赖 / test_depends |
| 29 | D_GOV_AUDIT 审计追踪: stash 生命周期治本单测 / Test Stash Lifecycle (audit/test... | → | Session Worktree / Session Worktree (rule_bridge/session_... | 测试依赖 / test_depends |
| 30 | D_GOV_AUDIT 审计追踪: 测试会话worktree异步对账 / test_session_worktree_async_re... | → | Session Worktree / Session Worktree (rule_bridge/session_... | 测试依赖 / test_depends |
| 31 | D_GOV_CODE_QUALITY 代码质量治理: reference辅助 / _reference_helpers (commit_gates/_referen... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 32 | D_GOV_CODE_QUALITY 代码质量治理: archreference门禁 / arch_reference_gate (commit_gates/arc... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 33 | D_GOV_CODE_QUALITY 代码质量治理: asynciorunin上下文门禁 / asyncio_run_in_context_gate (com... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 34 | D_GOV_CODE_QUALITY 代码质量治理: baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 35 | D_GOV_CODE_QUALITY 代码质量治理: baresql门禁 / bare_sql_gate (commit_gates/bare_sql_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 36 | D_GOV_CODE_QUALITY 代码质量治理: baresubprocess门禁 / bare_subprocess_gate (commit_gates/b... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 37 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amoduleconsistency门禁 / blueprint_amodule_consistenc... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 38 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule跨check门禁 / blueprint_amodule_cross_check_ga... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 39 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图format门禁 / blueprint_format_gate (commit_gates/blue... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 40 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图物理ID硬编码阻断门禁 (commit_gates/blueprint_node_id_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 41 | D_GOV_CODE_QUALITY 代码质量治理: 能力一致性门禁 / capability_consistency_gate (commit_gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 42 | D_GOV_CODE_QUALITY 代码质量治理: capabilitylookuprequired门禁 / capability_lookup_required... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 43 | D_GOV_CODE_QUALITY 代码质量治理: capabilityoverlap门禁 / capability_overlap_gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 44 | D_GOV_CODE_QUALITY 代码质量治理: ch批次大小门禁 / ch_batch_size_gate (commit_gates/ch_batc... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 45 | D_GOV_CODE_QUALITY 代码质量治理: ch最终门禁 / ch_final_gate (commit_gates/ch_final_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 46 | D_GOV_CODE_QUALITY 代码质量治理: ch版本col门禁 / ch_version_col_gate (commit_gates/ch_vers... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 47 | D_GOV_CODE_QUALITY 代码质量治理: claimrequired门禁 / claim_required_gate (commit_gates/cla... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 48 | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 49 | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 50 | D_GOV_CODE_QUALITY 代码质量治理: danglingreference门禁 / dangling_reference_gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 51 | D_GOV_CODE_QUALITY 代码质量治理: 数据taskcompleteness门禁 / data_task_completeness_gate (c... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 52 | D_GOV_CODE_QUALITY 代码质量治理: datetimenowforbidden门禁 / datetime_now_forbidden_gate (c... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 53 | D_GOV_CODE_QUALITY 代码质量治理: depgraphfreshness门禁 / depgraph_freshness_gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 54 | D_GOV_CODE_QUALITY 代码质量治理: depgraph planned→production 流转强制门禁 / Depgraph Pre ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: depgraphwritepath门禁 / depgraph_write_path_gate (commit_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 56 | D_GOV_CODE_QUALITY 代码质量治理: derivationannotation门禁 / derivation_annotation_gate (co... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 57 | D_GOV_CODE_QUALITY 代码质量治理: 派生文件删除保护门禁 / Derived File Deletion Gate (commit... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 58 | D_GOV_CODE_QUALITY 代码质量治理: directorycontract门禁 / directory_contract_gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 59 | D_GOV_CODE_QUALITY 代码质量治理: docrefbroken门禁 / doc_ref_broken_gate (commit_gates/doc_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 60 | D_GOV_CODE_QUALITY 代码质量治理: 域fk门禁 / domain_fk_gate (commit_gates/domain_fk_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 61 | D_GOV_CODE_QUALITY 代码质量治理: domainnamezhdirect访问门禁 / domain_name_zh_direct_access... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 62 | D_GOV_CODE_QUALITY 代码质量治理: empty处理器门禁 / empty_handler_gate (commit_gates/empty_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 63 | D_GOV_CODE_QUALITY 代码质量治理: encoding门禁 / encoding_gate (commit_gates/encoding_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 64 | D_GOV_CODE_QUALITY 代码质量治理: exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 65 | D_GOV_CODE_QUALITY 代码质量治理: filecopy门禁 / file_copy_gate (commit_gates/file_copy_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 66 | D_GOV_CODE_QUALITY 代码质量治理: fileplacementttl门禁 / file_placement_ttl_gate (commit_ga... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 67 | D_GOV_CODE_QUALITY 代码质量治理: folder容量hardlimit门禁 / folder_capacity_hard_limit_gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 68 | D_GOV_CODE_QUALITY 代码质量治理: foreignchange门禁 / foreign_change_gate (commit_gates/for... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 69 | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 70 | D_GOV_CODE_QUALITY 代码质量治理: 函数dup门禁 / function_dup_gate (commit_gates/function_du... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 71 | D_GOV_CODE_QUALITY 代码质量治理: Gitcall预算门禁 / git_call_budget_gate (commit_gates/git_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 72 | D_GOV_CODE_QUALITY 代码质量治理: god类门禁 / god_class_gate (commit_gates/god_class_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 73 | D_GOV_CODE_QUALITY 代码质量治理: hardcodedurl门禁 / hardcoded_url_gate (commit_gates/hardc... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 74 | D_GOV_CODE_QUALITY 代码质量治理: heldoverlap门禁 / held_overlap_gate (commit_gates/held_ov... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 75 | D_GOV_CODE_QUALITY 代码质量治理: highcomplexity门禁 / high_complexity_gate (commit_gates/h... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 76 | D_GOV_CODE_QUALITY 代码质量治理: iduniqueness门禁 / id_uniqueness_gate (commit_gates/id_un... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 77 | D_GOV_CODE_QUALITY 代码质量治理: importdirection门禁 / import_direction_gate (commit_gates... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 78 | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 79 | D_GOV_CODE_QUALITY 代码质量治理: issueresolved完整性门禁 / issue_resolved_integrity_gate (... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 80 | D_GOV_CODE_QUALITY 代码质量治理: longparamlist门禁 / long_param_list_gate (commit_gates/lo... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 81 | D_GOV_CODE_QUALITY 代码质量治理: 手册onlypermanent门禁 / manual_only_permanent_gate (commi... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 82 | D_GOV_CODE_QUALITY 代码质量治理: MCP版本字段门禁 / mcp_version_field_gate (commit_gates/mc... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 83 | D_GOV_CODE_QUALITY 代码质量治理: 模块id一致性门禁 / module_id_consistency_gate (commit_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 84 | D_GOV_CODE_QUALITY 代码质量治理: msg敞口门禁 / msg_exposure_gate (commit_gates/msg_exposur... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 85 | D_GOV_CODE_QUALITY 代码质量治理: msgstyle门禁 / msg_style_gate (commit_gates/msg_style_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 86 | D_GOV_CODE_QUALITY 代码质量治理: mutableconstwithoutfinal门禁 / mutable_const_without_fina... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 87 | D_GOV_CODE_QUALITY 代码质量治理: 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 88 | D_GOV_CODE_QUALITY 代码质量治理: noimportsideeffect门禁 / no_import_side_effect_gate (comm... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 89 | D_GOV_CODE_QUALITY 代码质量治理: noqa验证门禁 / noqa_validation_gate (commit_gates/noqa_va... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 90 | D_GOV_CODE_QUALITY 代码质量治理: openwithoutwith门禁 / open_without_with_gate (commit_gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 91 | D_GOV_CODE_QUALITY 代码质量治理: 孤儿module门禁 / orphan_module_gate (commit_gates/orphan_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 92 | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 93 | D_GOV_CODE_QUALITY 代码质量治理: permtrigger门禁 / perm_trigger_gate (commit_gates/perm_tr... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 94 | D_GOV_CODE_QUALITY 代码质量治理: precommitoffline门禁 / precommit_offline_gate (commit_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 95 | D_GOV_CODE_QUALITY 代码质量治理: 受保护路径写入检测门禁 / Protected Paths Gate (commit_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 96 | D_GOV_CODE_QUALITY 代码质量治理: pureassertion门禁 / pure_assertion_gate (commit_gates/pur... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 97 | D_GOV_CODE_QUALITY 代码质量治理: pureshim门禁 / pure_shim_gate (commit_gates/pure_shim_gat... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 98 | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 99 | D_GOV_CODE_QUALITY 代码质量治理: reconciler 健康度门禁 / Reconciler Health Gate (commit_ga... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 100 | D_GOV_CODE_QUALITY 代码质量治理: 相对路径字面量硬阻断门禁 / Relative Path Literal Gate (co... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 101 | D_GOV_CODE_QUALITY 代码质量治理: 文件重命名后 depgraph 未同步阻断门禁 / Rename Depgraph Sy... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 102 | D_GOV_CODE_QUALITY 代码质量治理: 规则-执行配对门禁 / Rule Execution Pairing Gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 103 | D_GOV_CODE_QUALITY 代码质量治理: 规则四方对齐门禁 / Rule Four Way Alignment Gate (commit_g... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 104 | D_GOV_CODE_QUALITY 代码质量治理: 文档"已完成"声明 commit hash 真实性硬验证门禁 / Ruling Co... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 105 | D_GOV_CODE_QUALITY 代码质量治理: 裁定#NNN 悬空引用自动检测门禁 / Ruling Reference Gate (co... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 106 | D_GOV_CODE_QUALITY 代码质量治理: SCHEMA-FILE-EXISTS block 门禁 / Schema File Exists Gate (... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 107 | D_GOV_CODE_QUALITY 代码质量治理: _shared.constants 符号导入完整性门禁 / Scripts Import Int... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 108 | D_GOV_CODE_QUALITY 代码质量治理: 密钥值硬编码阻断门禁 (commit_gates/secret_hardcode_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 109 | D_GOV_CODE_QUALITY 代码质量治理: 密钥注册表一致性门禁 (commit_gates/secret_registry_consis... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 110 | D_GOV_CODE_QUALITY 代码质量治理: session 注册强制门禁 / Session Required Gate (commit_gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 111 | D_GOV_CODE_QUALITY 代码质量治理: 运行时违规快照漂移阻断门禁 / Snapshot Drift Gate (commit_... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 112 | D_GOV_CODE_QUALITY 代码质量治理: SSoT 符号重复定义硬阻断门禁 / Ssot Redefinition Gate (com... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 113 | D_GOV_CODE_QUALITY 代码质量治理: TABLE-NAME-REGISTRY block 门禁 / Table Name Registry Gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 114 | D_GOV_CODE_QUALITY 代码质量治理: 测试残留前缀硬编码阻断门禁 (commit_gates/test_residue_sso... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 115 | D_GOV_CODE_QUALITY 代码质量治理: 测试-源码符号一致性门禁 / Test Source Consistency Gate (c... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 116 | D_GOV_CODE_QUALITY 代码质量治理: Gate 测试覆盖率校验 meta-gate / Tests Coverage Gate (comm... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 117 | D_GOV_CODE_QUALITY 代码质量治理: 新建 .py 文件大白话简介覆盖率门禁 / Translation Coverage ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 118 | D_GOV_CODE_QUALITY 代码质量治理: ttl 字段校验门禁 / Ttl Gate (commit_gates/ttl_gate.py) | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 119 | D_GOV_CODE_QUALITY 代码质量治理: UNDEFINED-NAME 门禁 / Undefined Name Gate (commit_gates/u... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 120 | D_GOV_CODE_QUALITY 代码质量治理: ``**data`` 直接展开模式 warn 级门禁 / Unsafe Dict Spread ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 121 | D_GOV_CODE_QUALITY 代码质量治理: SSoT 引用硬编码阻断门禁 / Vocab Chain Gate (commit_gates/... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 122 | D_GOV_CODE_QUALITY 代码质量治理: 新增 .py 文件词表硬编码阻断门禁 / Vocab Hardcode Gate (co... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 123 | D_GOV_CODE_QUALITY 代码质量治理: worktree 隔离强制门禁 / Worktree Required Gate (commit_ga... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 124 | D_GOV_CODE_QUALITY 代码质量治理: ZEPHYR_ENV 直访硬阻断门禁 / Zephyr Env Direct Access Gate... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 125 | D_GOV_CODE_QUALITY 代码质量治理: YAML 驱动的 in-process gate 自动注册器 / Gate Auto Regist... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 导入依赖 / import_depends |
| 126 | D_GOV_CODE_QUALITY 代码质量治理: BLUEPRINT-NODE-ID-HARDCODE 门禁单测 / Test Blueprint Node... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 测试依赖 / test_depends |
| 127 | D_GOV_CODE_QUALITY 代码质量治理: TEST-RESIDUE-SSOT 门禁单测 / Test Test Residue Ssot Gate ... | → | GitCommitGateway pre-commit 门禁注册表 / Commit Gate Regi... | 测试依赖 / test_depends |
| 128 | D_GOV_CODE_QUALITY 代码质量治理: Test Output Quality Gate / Test Output Quality Gate (rule... | → | 只读：rules / Output Quality Gate (rule_enforcement/outpu... | 测试依赖 / test_depends |
| 129 | D_GOV_CODE_QUALITY 代码质量治理: worktree_ops_log 遥测完整性审计测试 / Test Audit Worktree... | → | Session Worktree / Session Worktree (rule_bridge/session_... | 测试依赖 / test_depends |
| 130 | D_GOV_DRIFT 漂移检测: Tamper Proof Audit / Tamper Proof Audit (gov_drift/tamper... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 导入依赖 / import_depends |
| 131 | D_GOV_OPS_RESILIENCE 运维弹性治理: 审计动作类型""" / Security Gateway Base (security_governa... | → | ComplianceRule 真源已合并至 zephyr.shared.contracts.compl... | 导入依赖 / import_depends |
| 132 | D_GOV_OPS_RESILIENCE 运维弹性治理: Test Pre Flight Gate / Test Pre Flight Gate (budget/test_... | → | 只读：engine / Pre Flight Gate (rule_enforcement/pre_flig... | 测试依赖 / test_depends |
| 133 | D_GOV_RULE 规则治理: 规则引擎模块集 / Rule Engine Package (rule_engine/__init_... | → | 只读：baseline_metrics / Rule Canary Manager (rule_engine... | config_depends / config_depends |
| 134 | D_GOV_SCRIPTS 脚本治理: 幽灵提交红蓝对抗脚本 / Concurrent Commit Test (repair/con... | → | 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | 导入依赖 / import_depends |
| 135 | D_ML_TRAIN 训练: Training Dataset Manager / Training Dataset Manager (trai... | → | Data Quality Gate / Quality Gate (rule_enforcement/qualit... | data / data |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 16 个外部域直接连接（出边 161 条 + 入边 135 条 = 296 条）。只显示直接连接的域，不展开具体节点。

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
    D_GOV_ENFORCEMENT -->|81条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_CODE_QUALITY
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
    D_GOV_CODE_QUALITY -->|99条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
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
