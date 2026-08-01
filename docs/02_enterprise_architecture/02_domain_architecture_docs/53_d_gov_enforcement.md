---
doc_type: architecture_view
title: D_GOV_ENFORCEMENT 规则执行架构文档
version: "1.0"
status: active
date: 2026-08-01
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
| 模块数 | 42 | Module Count | 42 |
| 域内依赖 | 32 | Internal Dependencies | 32 |
| 跨域入边 | 110 | Cross-domain Incoming | 110 |
| 跨域出边 | 68 | Cross-domain Outgoing | 68 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 41 | Production Modules | 41 |
| 容量 | 41/150 (正常) | Capacity | 41/150 (正常) |
| 描述 | 门禁引擎流程编排(GatePipeline/GateEngine) | Description | 门禁引擎流程编排(GatePipeline/GateEngine) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。全景图用颜色区分运营态/设计态，不再分页/拆子图。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 42 个模块（生产态 41 + 设计态 1），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml["(生产态 / production)<br/>文件: catalogs/rule_enforcement_registry.yaml"]
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["(生产态 / production) metric_count_drift_reconciler.py — dashboard 指标数描述派生校验 reconciler<br/>metric_count_drift_reconciler.py — dashboard 指标数描述派生校验 reconciler<br/>文件: d8_doc_sync/metric_count_drift_reconciler.py"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["(生产态 / production) readme_version_sync_reconciler.py — README 版本号派生展示校验 reconciler<br/>readme_version_sync_reconciler.py — README 版本号派生展示校验 reconciler<br/>文件: d8_doc_sync/readme_version_sync_reconciler.py"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["(生产态 / production) requirements_version_sync_reconciler.py — requirements.txt ↔ pyproject.toml...<br/>requirements_version_sync_reconciler.py — requirements.txt ↔ pyproject.toml...<br/>文件: d8_doc_sync/requirements_version_sync_reconciler.py"]
    scripts_governance_session_worktree_cli_py["(生产态 / production) session_worktree_cli.py — session worktree 管理 CLI（治本遗留项#2，2026-07-17）<br/>session_worktree_cli.py — session worktree 管理 CLI（治本遗留项#2，2026-07-17）<br/>文件: governance/session_worktree_cli.py"]
    src_zephyr_gov_enforcement_init_py["(生产态 / production) gov_enforcement package — 执行治理域（D_GOV_ENFORCEMENT）<br/>gov_enforcement package — 执行治理域（D_GOV_ENFORCEMENT）<br/>文件: gov_enforcement/__init__.py"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["(生产态 / production)<br/>文件: behavioral_admission/__init__.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py["(设计态 / design) depgraph_pre_registration_gate.py — depgraph planned→production 流转强制门...<br/>depgraph_pre_registration_gate.py — depgraph planned→production 流转强制门...<br/>文件: commit_gates/depgraph_pre_registration_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["(生产态 / production) stash_accumulation_gate.py — stash 堆积阈值检测门禁（STASH-ACCUMULATION）<br/>stash_accumulation_gate.py — stash 堆积阈值检测门禁（STASH-ACCUMULATION）<br/>文件: commit_gates/stash_accumulation_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["(生产态 / production) G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contract...<br/>G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["(生产态 / production) Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.complia...<br/>Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.complia...<br/>文件: rule_enforcement/compliance_rule.py"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["(生产态 / production) D_DATA — Default Data Quality Gate<br/>D_DATA — Default Data Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["(生产态 / production) DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的真重试。<br/>DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的真重试。<br/>文件: rule_enforcement/dlq_retry_policy.py"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["(生产态 / production)<br/>文件: rule_enforcement/output_quality_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["(生产态 / production)<br/>文件: rule_enforcement/pre_flight_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["(生产态 / production) Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则->A/B对比->rollback。<br/>Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["(生产态 / production) Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务...<br/>Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务...<br/>文件: rule_engine/rule_debt_auditor.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["(生产态 / production) Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天->diff old vs ...<br/>Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天->diff old vs ...<br/>文件: rule_engine/rule_shadow_runner.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["(生产态 / production) RuleWatcher — YAML 规则文件变更检测与自动同步<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>文件: rule_engine/rule_watcher.py"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["(生产态 / production) SLO-Driven Escalation Contract — D-022-12.<br/>SLO-Driven Escalation Contract — D-022-12.<br/>文件: rule_enforcement/slo_contract.py"]
    tests_governance_commit_gates_test_create_guard_py["(生产态 / production) test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-06-30 治本补全）<br/>test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-06-30 治本补全）<br/>文件: commit_gates/test_create_guard.py"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["(生产态 / production) test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元测试<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元测试<br/>文件: commit_gates/test_r5_digit_suffix_gate.py"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["(生产态 / production) test_claim_files_for_edit.py — P2-2 并发 session 文件级原子性测试<br/>test_claim_files_for_edit.py — P2-2 并发 session 文件级原子性测试<br/>文件: rule_bridge/test_claim_files_for_edit.py"]
    tests_governance_rule_bridge_test_emergency_commit_py["(生产态 / production) test_emergency_commit.py — emergency_commit API 测试（Ruling:100PCT-AI-GOVER...<br/>test_emergency_commit.py — emergency_commit API 测试（Ruling:100PCT-AI-GOVER...<br/>文件: rule_bridge/test_emergency_commit.py"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["(生产态 / production) test_heartbeat_daemon.py — heartbeat daemon + 成本递增 smoke test（Ruling:10...<br/>test_heartbeat_daemon.py — heartbeat daemon + 成本递增 smoke test（Ruling:10...<br/>文件: rule_bridge/test_heartbeat_daemon.py"]
    docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml ~~~ scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py ~~~ scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py ~~~ scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py ~~~ scripts_governance_session_worktree_cli_py
    scripts_governance_session_worktree_cli_py ~~~ src_zephyr_gov_enforcement_init_py
    src_zephyr_gov_enforcement_init_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_init_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py ~~~ src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py
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
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py ~~~ tests_governance_commit_gates_test_create_guard_py
    tests_governance_commit_gates_test_create_guard_py ~~~ tests_governance_commit_gates_test_r5_digit_suffix_gate_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py ~~~ tests_governance_rule_bridge_test_claim_files_for_edit_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py ~~~ tests_governance_rule_bridge_test_emergency_commit_py
    tests_governance_rule_bridge_test_emergency_commit_py ~~~ tests_governance_rule_bridge_test_heartbeat_daemon_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["(生产态 / production)<br/>文件: behavioral_admission/admission_response.py"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["(生产态 / production)<br/>文件: behavioral_admission/code_review_ai.py"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["(生产态 / production) GateEventAdapter — GateRepo 事件适配器（DW-0006）<br/>GateEventAdapter — GateRepo 事件适配器（DW-0006）<br/>文件: behavioral_admission/gate_event_adapter.py"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["(生产态 / production)<br/>文件: behavioral_admission/gpu_consensus_scheduler.py"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["(生产态 / production)<br/>文件: behavioral_admission/protection_index.py"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["(生产态 / production) commit_gate_registry.py — GitCommitGateway pre-commit 门禁注册表（架构债务 #...<br/>commit_gate_registry.py — GitCommitGateway pre-commit 门禁注册表（架构债务 #...<br/>文件: rule_bridge/commit_gate_registry.py"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["(生产态 / production) session_worktree.py — AI 对话 worktree 物理隔离 helper（FP-ISO.4C，2026-07-0...<br/>session_worktree.py — AI 对话 worktree 物理隔离 helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["(生产态 / production) D_DATA — Data Quality Gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["(生产态 / production)<br/>文件: behavioral_admission/admission_controller.py"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["(生产态 / production)<br/>文件: behavioral_admission/verdict_engine.py"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["(生产态 / production) emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>文件: rule_bridge/emergency_commit.py"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["(生产态 / production) heartbeat_daemon.py — session heartbeat 独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>heartbeat_daemon.py — session heartbeat 独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>文件: rule_bridge/heartbeat_daemon.py"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["(生产态 / production) session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2改，2026-07-01 治本）<br/>session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2改，2026-07-01 治本）<br/>文件: rule_bridge/session_claim.py"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["(生产态 / production) worktree_manager.py — session worktree 物理隔离管理器（阶段3 治本 stash 循环）<br/>worktree_manager.py — session worktree 物理隔离管理器（阶段3 治本 stash 循环）<br/>文件: rule_bridge/worktree_manager.py"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["(生产态 / production) worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>文件: rule_bridge/worktree_pool.py"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["(生产态 / production) GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2026062512 治本）<br/>GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2026062512 治本）<br/>文件: rule_bridge/git_commit_gateway.py"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["(生产态 / production) batched_auto_committer.py — Reconciler 批量化 auto-commit 拦截器（ARCH-GIT-C...<br/>batched_auto_committer.py — Reconciler 批量化 auto-commit 拦截器（ARCH-GIT-C...<br/>文件: rule_bridge/batched_auto_committer.py"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) 管线路由 / Pipeline Routing<br/>管线路由，负责跨域数据流路由、管道编排和集成适配<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py -->|导入依赖 / import_depends| D_INTEGRATION
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY["(生产态 / production) 代码质量治理 / Code Quality Governance<br/>代码质量治理，负责代码去重引擎、函数重复检测、AST语义分析和提交门禁引擎<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_AUDIT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_RULE["(生产态 / production) 规则治理 / Rule Governance<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>跨域节点 / cross-domain"]
    D_GOV_RULE -->|config_depends / config_depends| src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) 运维弹性治理 / Ops Resilience Governance<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和升级协议<br/>跨域节点 / cross-domain"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_heartbeat_daemon_py production
    class src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py design
    class D_SHARED,D_GOV_AUDIT,D_INTEGRATION,D_INFRASTRUCTURE,D_GOV_CODE_QUALITY,D_GOVERNANCE,D_GOV_RULE,D_GOV_OPS_RESILIENCE external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | behavioral_admission/__init__.py | → | D_GOVERNANCE 生命周期管理: WorktreeLifecycle — worktree 生命周期状态机（5态 + 8转换... | 导入依赖 / import_depends |
| 2 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API + ... | 导入依赖 / import_depends |
| 3 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API + ... | 导入依赖 / import_depends |
| 4 | metric_count_drift_reconciler.py — dashboard 指标数描述... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 5 | readme_version_sync_reconciler.py — README 版本号派生展... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 6 | requirements_version_sync_reconciler.py — requirements.t... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 7 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: behavioral_admission/mcp_result_push.py | 导入依赖 / import_depends |
| 8 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: post_process.py —— AI 生成代码后处理管道（Phase 13 | 盲... | 导入依赖 / import_depends |
| 9 | behavioral_admission/__init__.py | → | D_GOV_AUDIT 审计追踪: behavioral_admission/vibe_coding_enforcer.py | 导入依赖 / import_depends |
| 10 | GateEventAdapter — GateRepo 事件适配器（DW-0006） (behav... | → | D_GOV_AUDIT 审计追踪: EventStore — Event Sourcing 事件追加与回放（DW-0002） (g... | 导入依赖 / import_depends |
| 11 | behavioral_admission/verdict_engine.py | → | D_GOV_AUDIT 审计追踪: gov_audit/models.py | 导入依赖 / import_depends |
| 12 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 13 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: blueprint_status_transition_reconciler.py — 蓝图状态单调... | 导入依赖 / import_depends |
| 14 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: commit_gateway_abuse_monitor_reconciler.py — commit gate... | 导入依赖 / import_depends |
| 15 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: cross_layer_contract_signature_reconciler.py — 跨层契约... | 导入依赖 / import_depends |
| 16 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: error_pattern_consumer_reconciler.py — AI 行为遥测 JSONL... | 导入依赖 / import_depends |
| 17 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: git_performance_monitor_reconciler.py — git 性能持续监控... | 导入依赖 / import_depends |
| 18 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | 导入依赖 / import_depends |
| 19 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 20 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: remediation_progress_reconciler.py — 治本进度持久化 + 新... | 导入依赖 / import_depends |
| 21 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: runtime_violation_snapshot_reconciler.py — trae_060 §5 ... | 导入依赖 / import_depends |
| 22 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_AUDIT 审计追踪: workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | 导入依赖 / import_depends |
| 23 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: ai_error_pattern_library.py — AI 错误模式库（只读查询接... | 导入依赖 / import_depends |
| 24 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: reconcile_runner.py — Reconciler 链路异步化（Ruling:100P... | 导入依赖 / import_depends |
| 25 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 26 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_AUDIT 审计追踪: workspace_hygiene_reconciler.py — 工作区卫生自动清理 rec... | 导入依赖 / import_depends |
| 27 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 导入依赖 / import_depends |
| 28 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: commit_gates — GitCommitGateway pre-commit 门禁实现包。 ... | 导入依赖 / import_depends |
| 29 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: capability_lookup_required_gate.py — Capability Lookup ... | 导入依赖 / import_depends |
| 30 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_GOV_CODE_QUALITY 代码质量治理: test_source_consistency_gate.py — 测试-源码符号一致性门... | 导入依赖 / import_depends |
| 31 | test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-0... | → | D_GOV_CODE_QUALITY 代码质量治理: create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | 测试依赖 / test_depends |
| 32 | test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元... | → | D_GOV_CODE_QUALITY 代码质量治理: r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本... | 测试依赖 / test_depends |
| 33 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Phase Manager — ZephyrAlpha 施工阶段门控引擎. (ops_gover... | 导入依赖 / import_depends |
| 34 | metric_count_drift_reconciler.py — dashboard 指标数描述... | → | D_GOV_SCRIPTS 脚本治理: architecture_health_dashboard.py — 架构健康度仪表盘（自... | 导入依赖 / import_depends |
| 35 | session_worktree_cli.py — session worktree 管理 CLI（治... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 36 | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/compliance_rule.py | 导入依赖 / import_depends |
| 37 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_INFRA_RUNTIME 运行时集成: git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGE... | 导入依赖 / import_depends |
| 38 | G-CT-004 — Backward-compat re-export of ApprovalRequest ... | → | D_INTEGRATION 管线路由: G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请... | 导入依赖 / import_depends |
| 39 | rule_enforcement/pre_flight_gate.py | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 40 | rule_enforcement/pre_flight_gate.py | → | D_OPS 反馈循环: Budget Enforcer data models — MOD-INF-024 (ops_governanc... | 导入依赖 / import_depends |
| 41 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 42 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SECURITY 对抗验证: CommitTrigger — 事件驱动红蓝对抗触发器 (MOD-INF-030). (a... | 导入依赖 / import_depends |
| 43 | heartbeat_daemon.py — session heartbeat 独立进程（Ruling... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 44 | session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 45 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 46 | test_claim_files_for_edit.py — P2-2 并发 session 文件级... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 测试依赖 / test_depends |
| 47 | session_worktree_cli.py — session worktree 管理 CLI（治... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 48 | GateEventAdapter — GateRepo 事件适配器（DW-0006） (behav... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 49 | behavioral_admission/gpu_consensus_scheduler.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 50 | commit_gate_registry.py — GitCommitGateway pre-commit 门... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 51 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 52 | emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOV... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 53 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 54 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 55 | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 56 | session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 57 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 58 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 59 | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | D_SHARED 共享服务: workspace_telemetry.py — 主工作区文件操作遥测公共 API（.... | 导入依赖 / import_depends |
| 60 | worktree_manager.py — session worktree 物理隔离管理器（... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 61 | worktree_manager.py — session worktree 物理隔离管理器（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 62 | worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDG... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 63 | worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDG... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 64 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: dlq.py —— ZephyrAlpha 死信队列（Dead Letter Queue） (ev... | 导入依赖 / import_depends |
| 65 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emit/unsubscr... | 导入依赖 / import_depends |
| 66 | DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 67 | RuleWatcher — YAML 规则文件变更检测与自动同步 (rule_engi... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 68 | RuleWatcher — YAML 规则文件变更检测与自动同步 (rule_engi... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (io/sqlite_factory.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_DATA 数据接入层: Re-export wrapper: QualityReport 真源在 zephyr.gov_enforc... | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 导入依赖 / import_depends |
| 2 | D_DATA 数据接入层: D_DATA Data Source (satellite_geospatial_engine/__init__.py) | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 导入依赖 / import_depends |
| 3 | D_DATA 数据接入层: #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。 (data... | → | D_DATA — Data Quality Gate (rule_enforcement/quality_gat... | 测试依赖 / test_depends |
| 4 | D_GOVERNANCE 生命周期管理: git_commit.py — GitCommitGateway CLI 封装（OPS-202606251... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: ZephyrAlpha — D_COMPLIANCE Compliance Layer — 合规规则... | → | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04） (per... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: session 隔离 stash 红蓝对抗极限测试。 (agent_rbac/test_se... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 8 | D_GOVERNANCE 生命周期管理: test_git_commit_concurrent.py — 幽灵提交红蓝对抗测试（OP... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 测试依赖 / test_depends |
| 9 | D_GOVERNANCE 生命周期管理: test_git_commit_concurrent.py — 幽灵提交红蓝对抗测试（OP... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 10 | D_GOVERNANCE 生命周期管理: test_git_commit_extreme.py — GitCommitGateway 极端故障注... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 11 | D_GOVERNANCE 生命周期管理: test_git_commit_gateway.py — GitCommitGateway 单元测试（... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 12 | D_GOVERNANCE 生命周期管理: test_task_repo_gateway_e2e.py — 端到端链路测试（OPS-2026... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 13 | D_GOV_AUDIT 审计追踪: git_performance_monitor_reconciler.py — git 性能持续监控... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 14 | D_GOV_AUDIT 审计追踪: reconcile_worker.py — 异步 reconciler worker（Ruling:100... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 15 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 16 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 导入依赖 / import_depends |
| 17 | D_GOV_AUDIT 审计追踪: test_reconcile_async.py — P2-3 reconciler 链路异步化测试... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 18 | D_GOV_AUDIT 审计追踪: test_reconcile_worker_selfheal.py —... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 测试依赖 / test_depends |
| 19 | D_GOV_AUDIT 审计追踪: test_session_worktree_async_reconcile.py — _run_reconcil... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 20 | D_GOV_CODE_QUALITY 代码质量治理: _reference_helpers.py — 引用检测门禁共享工具函数（ARCH-R... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 21 | D_GOV_CODE_QUALITY 代码质量治理: arch_reference_gate.py — #ARCH-NNN / #ARCH-DOMAIN-NNN 悬... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 22 | D_GOV_CODE_QUALITY 代码质量治理: asyncio_run_in_context_gate.py — 异步上下文误用硬阻断门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 23 | D_GOV_CODE_QUALITY 代码质量治理: bare_getenv_gate.py — 裸 os.getenv 读密钥阻断门禁（NO-BA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 24 | D_GOV_CODE_QUALITY 代码质量治理: bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BARE-SQL，§5... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 25 | D_GOV_CODE_QUALITY 代码质量治理: bare_subprocess_gate.py — 裸 subprocess 调用硬阻断门禁（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 26 | D_GOV_CODE_QUALITY 代码质量治理: blueprint_amodule_consistency_gate.py — [A_module] 头部 ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 27 | D_GOV_CODE_QUALITY 代码质量治理: blueprint_amodule_cross_check_gate.py — [BLUEPRINT] vs [... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 28 | D_GOV_CODE_QUALITY 代码质量治理: blueprint_format_gate.py — [BLUEPRINT] 头部 module_id 格... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 29 | D_GOV_CODE_QUALITY 代码质量治理: capability_consistency_gate.py — Provider 路由-meta 一致... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 30 | D_GOV_CODE_QUALITY 代码质量治理: capability_lookup_required_gate.py — Capability Lookup ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 31 | D_GOV_CODE_QUALITY 代码质量治理: capability_overlap_gate.py — 新建 .py 文件 CapabilityLoo... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 32 | D_GOV_CODE_QUALITY 代码质量治理: ch_batch_size_gate.py — CH 批量写入防回退门禁（CH-BATCH-... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 33 | D_GOV_CODE_QUALITY 代码质量治理: ch_final_gate.py — ch_writer.query() 直接调用阻断门禁（C... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 34 | D_GOV_CODE_QUALITY 代码质量治理: ch_version_col_gate.py — CH version 列语义误用阻断门禁（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 35 | D_GOV_CODE_QUALITY 代码质量治理: claim_required_gate.py — claim_files 前置检查门禁（CLAIM... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 36 | D_GOV_CODE_QUALITY 代码质量治理: consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-o... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 37 | D_GOV_CODE_QUALITY 代码质量治理: create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 38 | D_GOV_CODE_QUALITY 代码质量治理: dangling_reference_gate.py — AGENTS.md §X.Y 悬空引用自... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 39 | D_GOV_CODE_QUALITY 代码质量治理: data_task_completeness_gate.py — 数据任务完整性门禁（war... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 40 | D_GOV_CODE_QUALITY 代码质量治理: datetime_now_forbidden_gate.py — 时间戳约定硬阻断门禁（D... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 41 | D_GOV_CODE_QUALITY 代码质量治理: depgraph_freshness_gate.py — depgraph 新鲜度门禁（dual-t... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 42 | D_GOV_CODE_QUALITY 代码质量治理: depgraph_write_path_gate.py — depgraph 写入路径白名单门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 43 | D_GOV_CODE_QUALITY 代码质量治理: derivation_annotation_gate.py — 派生关系声明真实性校验门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 44 | D_GOV_CODE_QUALITY 代码质量治理: directory_contract_gate.py — DCR-001~007 等效校验门禁（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 45 | D_GOV_CODE_QUALITY 代码质量治理: doc_ref_broken_gate.py — 文档相对路径断裂引用阻断门禁（D... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 46 | D_GOV_CODE_QUALITY 代码质量治理: domain_fk_gate.py — [DOMAIN] 头部域注册表 FK 校验门禁（G... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 47 | D_GOV_CODE_QUALITY 代码质量治理: domain_name_zh_direct_access_gate.py — DOMAIN_NAME_ZH 字... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 48 | D_GOV_CODE_QUALITY 代码质量治理: empty_handler_gate.py — 空事件 handler 函数阻断门禁（EMP... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 49 | D_GOV_CODE_QUALITY 代码质量治理: encoding_gate.py — 编码安全校验门禁（治本：弥补 --no-ver... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 50 | D_GOV_CODE_QUALITY 代码质量治理: exempt_zone_frontmatter_gate.py — 豁免区 frontmatter 门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 51 | D_GOV_CODE_QUALITY 代码质量治理: file_copy_gate.py — 新增 .py 文件复制检测阻断门禁（FILE-... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 52 | D_GOV_CODE_QUALITY 代码质量治理: file_placement_ttl_gate.py — 文件放置与 TTL 一致性门禁（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 53 | D_GOV_CODE_QUALITY 代码质量治理: folder_capacity_hard_limit_gate.py — 文件夹容量硬上限门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 54 | D_GOV_CODE_QUALITY 代码质量治理: foreign_change_gate.py — 外来变更检测门禁（FOREIGN-CHANG... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: forged_gw_marker_gate.py — Forged GW Marker 前置检测门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 56 | D_GOV_CODE_QUALITY 代码质量治理: function_dup_gate.py — 重复函数实现阻断门禁（FUNCTION-DU... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 57 | D_GOV_CODE_QUALITY 代码质量治理: git_call_budget_gate.py — Git 调用预算 warn-only 门禁（G... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 58 | D_GOV_CODE_QUALITY 代码质量治理: god_class_gate.py — God Class 阻断门禁（NO-GOD-CLASS，§... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 59 | D_GOV_CODE_QUALITY 代码质量治理: hardcoded_url_gate.py — 硬编码 localhost URL 阻断门禁（N... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 60 | D_GOV_CODE_QUALITY 代码质量治理: held_overlap_gate.py — 搭便车防护门禁（HELD-OVERLAP，202... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 61 | D_GOV_CODE_QUALITY 代码质量治理: high_complexity_gate.py — 高循环复杂度阻断门禁（NO-HIGH-... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 62 | D_GOV_CODE_QUALITY 代码质量治理: id_uniqueness_gate.py — pre-commit hook ID 唯一性门禁（P... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 63 | D_GOV_CODE_QUALITY 代码质量治理: import_direction_gate.py — shared 层向上依赖阻断门禁（NO... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 64 | D_GOV_CODE_QUALITY 代码质量治理: import_integrity_gate.py — IMPORT-INTEGRITY 门禁（悬空 i... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 65 | D_GOV_CODE_QUALITY 代码质量治理: issue_resolved_integrity_gate.py — ISSUE-RESOLVED-INTEGR... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 66 | D_GOV_CODE_QUALITY 代码质量治理: long_param_list_gate.py — 长参数列表阻断门禁（NO-LONG-PA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 67 | D_GOV_CODE_QUALITY 代码质量治理: manual_only_permanent_gate.py — 永久系统脚本 manual 触发... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 68 | D_GOV_CODE_QUALITY 代码质量治理: mcp_version_field_gate.py — MCP version 字段缺失硬阻断门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 69 | D_GOV_CODE_QUALITY 代码质量治理: module_id_consistency_gate.py — module_id 三声明轨道一致... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 70 | D_GOV_CODE_QUALITY 代码质量治理: msg_exposure_gate.py — 错误消息暴露敏感信息阻断门禁（MSG... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 71 | D_GOV_CODE_QUALITY 代码质量治理: msg_style_gate.py — 错误消息标点/箭头风格阻断门禁（MSG-S... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 72 | D_GOV_CODE_QUALITY 代码质量治理: mutable_const_without_final_gate.py — 可变常量缺 Final ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 73 | D_GOV_CODE_QUALITY 代码质量治理: new_file_depgraph_gate.py — 新建 .py 文件 depgraph 未登... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 74 | D_GOV_CODE_QUALITY 代码质量治理: no_import_side_effect_gate.py — 模块导入零副作用门禁（NO... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 75 | D_GOV_CODE_QUALITY 代码质量治理: noqa_validation_gate.py — 自定义 noqa 标记合规性门禁（NO... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 76 | D_GOV_CODE_QUALITY 代码质量治理: open_without_with_gate.py — open() 未在 with 内硬阻断门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 77 | D_GOV_CODE_QUALITY 代码质量治理: orphan_module_gate.py — 孤儿模块（无 import 引用）阻断门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 78 | D_GOV_CODE_QUALITY 代码质量治理: panorama_alignment_gate.py — 三图模块对齐门禁（四图模块... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 79 | D_GOV_CODE_QUALITY 代码质量治理: perm_trigger_gate.py — 永久系统脚本时间触发模式无事件订... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 80 | D_GOV_CODE_QUALITY 代码质量治理: precommit_offline_gate.py — pre-commit 配置离线可运行检... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 81 | D_GOV_CODE_QUALITY 代码质量治理: pure_assertion_gate.py — 纯陈述原则阻断门禁（PURE-ASSERT... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 82 | D_GOV_CODE_QUALITY 代码质量治理: pure_shim_gate.py — 纯 re-export shim 阻断门禁（PURE-SHI... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 83 | D_GOV_CODE_QUALITY 代码质量治理: r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 84 | D_GOV_CODE_QUALITY 代码质量治理: reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 85 | D_GOV_CODE_QUALITY 代码质量治理: relative_path_literal_gate.py — 相对路径字面量硬阻断门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 86 | D_GOV_CODE_QUALITY 代码质量治理: rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 87 | D_GOV_CODE_QUALITY 代码质量治理: rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 88 | D_GOV_CODE_QUALITY 代码质量治理: rule_four_way_alignment_gate.py — 规则四方对齐门禁（RULE... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 89 | D_GOV_CODE_QUALITY 代码质量治理: ruling_commit_verified_gate.py — 文档"已完成"声明 commit... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 90 | D_GOV_CODE_QUALITY 代码质量治理: ruling_reference_gate.py — 裁定#NNN 悬空引用自动检测门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 91 | D_GOV_CODE_QUALITY 代码质量治理: schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 92 | D_GOV_CODE_QUALITY 代码质量治理: scripts_import_integrity_gate.py — _shared.constants 符... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 93 | D_GOV_CODE_QUALITY 代码质量治理: session_required_gate.py — session 注册强制门禁（SESSION... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 94 | D_GOV_CODE_QUALITY 代码质量治理: snapshot_drift_gate.py — 运行时违规快照漂移阻断门禁（SNA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 95 | D_GOV_CODE_QUALITY 代码质量治理: ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁 ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 96 | D_GOV_CODE_QUALITY 代码质量治理: table_name_registry_gate.py — TABLE-NAME-REGISTRY block ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 97 | D_GOV_CODE_QUALITY 代码质量治理: test_source_consistency_gate.py — 测试-源码符号一致性门... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 98 | D_GOV_CODE_QUALITY 代码质量治理: tests_coverage_gate.py — Gate 测试覆盖率校验 meta-gate（... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 99 | D_GOV_CODE_QUALITY 代码质量治理: ttl_gate.py — ttl 字段校验门禁（治本：弥补 --no-verify ... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 100 | D_GOV_CODE_QUALITY 代码质量治理: undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 101 | D_GOV_CODE_QUALITY 代码质量治理: unsafe_dict_spread_gate.py — ``**data`` 直接展开模式 war... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 102 | D_GOV_CODE_QUALITY 代码质量治理: vocab_chain_gate.py — SSoT 引用硬编码阻断门禁（VOCAB-CHA... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 103 | D_GOV_CODE_QUALITY 代码质量治理: vocab_hardcode_gate.py — 新增 .py 文件词表硬编码阻断门禁... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 104 | D_GOV_CODE_QUALITY 代码质量治理: zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 105 | D_GOV_CODE_QUALITY 代码质量治理: gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | → | commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 106 | D_GOV_CODE_QUALITY 代码质量治理: test_audit_worktree_ops_telemetry.py — worktree_ops_log ... | → | session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 107 | D_GOV_DRIFT 漂移检测: Tamper-Proof Audit — 防篡改审计 D-023-37 · §6.26。 (go... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |
| 108 | D_GOV_OPS_RESILIENCE 运维弹性治理: D_COMPLIANCE — Governance & Compliance Layer (security_g... | → | Re-export shim — ComplianceRule 真源已合并至 zephyr.shar... | 导入依赖 / import_depends |
| 109 | D_GOV_RULE 规则治理: 规则引擎模块集 / Rule Engine Package (rule_engine/__init_... | → | Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规... | config_depends / config_depends |
| 110 | D_GOV_SCRIPTS 脚本治理: concurrent_commit_test.py — 幽灵提交红蓝对抗脚本（OPS-20... | → | GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 14 个外部域直接连接（出边 68 条 + 入边 110 条 = 178 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_GOV_ENFORCEMENT -->|23条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_ENFORCEMENT -->|22条 导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_GOV_ENFORCEMENT -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_GOV_ENFORCEMENT -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_OPS
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_CODE_QUALITY -->|87条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT -->|7条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_DATA -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_DRIFT -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_OPS_RESILIENCE -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_RULE -->|1条 config_depends / config_depends| D_GOV_ENFORCEMENT
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
