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
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py["(生产态 / production) metriccount漂移reconciler / Metric Count Drift Reconciler<br/>metric_count_drift_reconciler.py — dashboard 指标数描述派生校验 reconciler<br/>文件: d8_doc_sync/metric_count_drift_reconciler.py"]
    scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py["(生产态 / production) readme版本同步reconciler / Readme Version Sync Reconciler<br/>readme_version_sync_reconciler.py — README 版本号派生展示校验 reconciler<br/>文件: d8_doc_sync/readme_version_sync_reconciler.py"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py["(生产态 / production) requirements版本同步reconciler / Requirements Version Sync Reconciler<br/>requirements_version_sync_reconciler.py — requirements.txt ↔ pyproject.toml...<br/>文件: d8_doc_sync/requirements_version_sync_reconciler.py"]
    scripts_governance_session_worktree_cli_py["(生产态 / production) 会话worktree命令行 / Session Worktree CLI<br/>session_worktree_cli.py — session worktree 管理 CLI（治本遗留项#2，2026-07-17）<br/>文件: governance/session_worktree_cli.py"]
    src_zephyr_gov_enforcement_init_py["(生产态 / production) 规则执行域包 / Gov Enforcement Domain Package<br/>规则执行域的文件夹入口，标记该域的代码边界。本身不含业务逻辑，给域内模块一个稳定归属。<br/>文件: gov_enforcement/__init__.py"]
    src_zephyr_gov_enforcement_behavioral_admission_init_py["(生产态 / production) 规则执行Behavioral Admission包 / Gov Enforcement Behavioral Admission Package<br/>规则执行域下 behavioral_admission 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: behavioral_admission/__init__.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py["(设计态 / design) depgraph预registration门禁 / Depgraph Pre Registration Gate<br/>depgraph_pre_registration_gate.py — depgraph planned→production 流转强制门...<br/>文件: commit_gates/depgraph_pre_registration_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py["(生产态 / production) stashaccumulation门禁 / Stash Accumulation Gate<br/>stash_accumulation_gate.py — stash 堆积阈值检测门禁（STASH-ACCUMULATION）<br/>文件: commit_gates/stash_accumulation_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_approval_py["(生产态 / production) approval / Approval<br/>G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contract...<br/>文件: rule_enforcement/approval.py"]
    src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py["(生产态 / production) 合规规则 / Compliance Rule<br/>Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.complia...<br/>文件: rule_enforcement/compliance_rule.py"]
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py["(生产态 / production) default质量门禁 / Default Quality Gate<br/>D_DATA — Default Data Quality Gate<br/>文件: rule_enforcement/default_quality_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py["(生产态 / production) dlqretry策略 / Dlq Retry Policy<br/>DLQ 重试策略 — 对接 shared/events/dlq.DeadLetterQueue 的真重试。<br/>文件: rule_enforcement/dlq_retry_policy.py"]
    src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py["(生产态 / production) 输出质量门禁 / Output Quality Gate<br/>定义 QualityRule、QualityVerdict、OutputQualityGate 等类型。<br/>文件: rule_enforcement/output_quality_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py["(生产态 / production) 预飞行门禁 / Pre Flight Gate<br/>定义 PreFlightDecision、PreFlightReport、PreFlightGate 等类型。<br/>文件: rule_enforcement/pre_flight_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py["(生产态 / production) 规则canary管理器 / Rule Canary Manager<br/>Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则->A/B对比->rollback。<br/>文件: rule_engine/rule_canary_manager.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py["(生产态 / production) 规则debt审计器 / Rule Debt Auditor<br/>Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务...<br/>文件: rule_engine/rule_debt_auditor.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py["(生产态 / production) 规则shadow运行器 / Rule Shadow Runner<br/>Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天->diff old vs ...<br/>文件: rule_engine/rule_shadow_runner.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py["(生产态 / production) 规则监视器 / Rule Watcher<br/>RuleWatcher — YAML 规则文件变更检测与自动同步<br/>文件: rule_engine/rule_watcher.py"]
    src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py["(生产态 / production) SLOcontract / SLO Contract<br/>SLO-Driven Escalation Contract — D-022-12.<br/>文件: rule_enforcement/slo_contract.py"]
    tests_governance_commit_gates_test_create_guard_py["(生产态 / production) 测试create守卫 / Test Create Guard<br/>test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-06-30 治本补全）<br/>文件: commit_gates/test_create_guard.py"]
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py["(生产态 / production) 测试r5digitsuffix门禁 / Test R5 Digit Suffix Gate<br/>test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元测试<br/>文件: commit_gates/test_r5_digit_suffix_gate.py"]
    tests_governance_rule_bridge_test_claim_files_for_edit_py["(生产态 / production) 测试claimfilesforedit / Test Claim Files For Edit<br/>test_claim_files_for_edit.py — P2-2 并发 session 文件级原子性测试<br/>文件: rule_bridge/test_claim_files_for_edit.py"]
    tests_governance_rule_bridge_test_emergency_commit_py["(生产态 / production) 测试emergencycommit / Test Emergency Commit<br/>test_emergency_commit.py — emergency_commit API 测试（Ruling:100PCT-AI-GOVER...<br/>文件: rule_bridge/test_emergency_commit.py"]
    tests_governance_rule_bridge_test_heartbeat_daemon_py["(生产态 / production) 测试心跳daemon / Test Heartbeat Daemon<br/>test_heartbeat_daemon.py — heartbeat daemon + 成本递增 smoke test（Ruling:10...<br/>文件: rule_bridge/test_heartbeat_daemon.py"]
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
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py["(生产态 / production) 准入响应 / Admission Response<br/>InvalidDecisionError<br/>文件: behavioral_admission/admission_response.py"]
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py["(生产态 / production) 代码审查AI / Code Review AI<br/>定义 ReviewLevel 等类型。<br/>文件: behavioral_admission/code_review_ai.py"]
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py["(生产态 / production) 门禁事件适配器 / Gate Event Adapter<br/>GateEventAdapter — GateRepo 事件适配器（DW-0006）<br/>文件: behavioral_admission/gate_event_adapter.py"]
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py["(生产态 / production) gpu共识调度器 / Gpu Consensus Scheduler<br/>noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>文件: behavioral_admission/gpu_consensus_scheduler.py"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py["(生产态 / production) 保护索引 / Protection Index<br/>query: BloomFilterError->fallback to Trie-only; rebuild: IOError->return part...<br/>文件: behavioral_admission/protection_index.py"]
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py["(生产态 / production) commit门禁注册表 / Commit Gate Registry<br/>commit_gate_registry.py — GitCommitGateway pre-commit 门禁注册表（架构债务 #...<br/>文件: rule_bridge/commit_gate_registry.py"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py["(生产态 / production) 会话worktree / Session Worktree<br/>session_worktree.py — AI 对话 worktree 物理隔离 helper（FP-ISO.4C，2026-07-0...<br/>文件: rule_bridge/session_worktree.py"]
    src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py["(生产态 / production) 质量门禁 / Quality Gate<br/>D_DATA — Data Quality Gate<br/>文件: rule_enforcement/quality_gate.py"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py ~~~ src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py["(生产态 / production) 准入控制器 / Admission Controller<br/>admit: RateLimited->retry_after_ms; admit: CircuitOpen->retry_after_cb_recovery<br/>文件: behavioral_admission/admission_controller.py"]
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py["(生产态 / production) verdict引擎 / Verdict Engine<br/>noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>文件: behavioral_admission/verdict_engine.py"]
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py["(生产态 / production) emergencycommit / Emergency Commit<br/>emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-0...<br/>文件: rule_bridge/emergency_commit.py"]
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py["(生产态 / production) 心跳daemon / Heartbeat Daemon<br/>heartbeat_daemon.py — session heartbeat 独立进程（Ruling:100PCT-AI-GOVERNANC...<br/>文件: rule_bridge/heartbeat_daemon.py"]
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py["(生产态 / production) 会话claim / Session Claim<br/>session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2改，2026-07-01 治本）<br/>文件: rule_bridge/session_claim.py"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py["(生产态 / production) worktree管理器 / Worktree Manager<br/>worktree_manager.py — session worktree 物理隔离管理器（阶段3 治本 stash 循环）<br/>文件: rule_bridge/worktree_manager.py"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py["(生产态 / production) worktree池 / Worktree Pool<br/>worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）<br/>文件: rule_bridge/worktree_pool.py"]
    src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py ~~~ src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py ~~~ src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py ~~~ src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py ~~~ src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_claim_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py["(生产态 / production) gitcommitgateway / Git Commit Gateway<br/>GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2026062512 治本）<br/>文件: rule_bridge/git_commit_gateway.py"]
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py["(生产态 / production) batched自动committer / Batched Auto Committer<br/>batched_auto_committer.py — Reconciler 批量化 auto-commit 拦截器（ARCH-GIT-C...<br/>文件: rule_bridge/batched_auto_committer.py"]
    src_zephyr_gov_enforcement_behavioral_admission_protection_index_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_admission_response_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_protection_index_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_admission_response_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py
    src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_claim_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_commit_gates_test_create_guard_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    tests_governance_commit_gates_test_r5_digit_suffix_gate_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    tests_governance_rule_bridge_test_emergency_commit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_claim_files_for_edit_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py
    tests_governance_rule_bridge_test_heartbeat_daemon_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY["(生产态 / production) 代码质量治理 / Code Quality Governance<br/>代码质量治理，负责代码去重引擎、函数重复检测、AST语义分析和提交门禁引擎<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_CODE_QUALITY
    src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_OPS["(生产态 / production) 反馈循环 / Feedback Loop<br/>反馈循环，负责系统运行反馈、性能监控和自动调优闭环<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py -->|导入依赖 / import_depends| D_OPS
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_SCRIPTS["(生产态 / production) 脚本治理 / Script Governance<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>跨域节点 / cross-domain"]
    scripts_governance_session_worktree_cli_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_gov_enforcement_behavioral_admission_init_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_OPS_RESILIENCE["(生产态 / production) 运维弹性治理 / Ops Resilience Governance<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和升级协议<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_gov_enforcement_rule_bridge_session_worktree_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_DATA["(生产态 / production) 数据接入层 / Data Access Layer<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>跨域节点 / cross-domain"]
    D_DATA -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_session_worktree_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_AUDIT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_enforcement_registry_yaml,scripts_governance_d8_doc_sync_metric_count_drift_reconciler_py,scripts_governance_d8_doc_sync_readme_version_sync_reconciler_py,scripts_governance_d8_doc_sync_requirements_version_sync_reconciler_py,scripts_governance_session_worktree_cli_py,src_zephyr_gov_enforcement_init_py,src_zephyr_gov_enforcement_behavioral_admission_init_py,src_zephyr_gov_enforcement_behavioral_admission_admission_controller_py,src_zephyr_gov_enforcement_behavioral_admission_admission_response_py,src_zephyr_gov_enforcement_behavioral_admission_code_review_ai_py,src_zephyr_gov_enforcement_behavioral_admission_gate_event_adapter_py,src_zephyr_gov_enforcement_behavioral_admission_gpu_consensus_scheduler_py,src_zephyr_gov_enforcement_behavioral_admission_protection_index_py,src_zephyr_gov_enforcement_behavioral_admission_verdict_engine_py,src_zephyr_gov_enforcement_commit_gates_stash_accumulation_gate_py,src_zephyr_gov_enforcement_rule_bridge_batched_auto_committer_py,src_zephyr_gov_enforcement_rule_bridge_commit_gate_registry_py,src_zephyr_gov_enforcement_rule_bridge_emergency_commit_py,src_zephyr_gov_enforcement_rule_bridge_git_commit_gateway_py,src_zephyr_gov_enforcement_rule_bridge_heartbeat_daemon_py,src_zephyr_gov_enforcement_rule_bridge_session_claim_py,src_zephyr_gov_enforcement_rule_bridge_session_worktree_py,src_zephyr_gov_enforcement_rule_bridge_worktree_manager_py,src_zephyr_gov_enforcement_rule_bridge_worktree_pool_py,src_zephyr_gov_enforcement_rule_enforcement_approval_py,src_zephyr_gov_enforcement_rule_enforcement_compliance_rule_py,src_zephyr_gov_enforcement_rule_enforcement_default_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_dlq_retry_policy_py,src_zephyr_gov_enforcement_rule_enforcement_output_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_pre_flight_gate_py,src_zephyr_gov_enforcement_rule_enforcement_quality_gate_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_canary_manager_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_debt_auditor_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_shadow_runner_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_watcher_py,src_zephyr_gov_enforcement_rule_enforcement_slo_contract_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_rule_bridge_test_claim_files_for_edit_py,tests_governance_rule_bridge_test_emergency_commit_py,tests_governance_rule_bridge_test_heartbeat_daemon_py production
    class src_zephyr_gov_enforcement_commit_gates_depgraph_pre_registration_gate_py design
    class D_GOV_AUDIT,D_GOV_CODE_QUALITY,D_OPS,D_GOVERNANCE,D_GOV_SCRIPTS,D_SHARED,D_GOV_OPS_RESILIENCE,D_SECURITY,D_DATA external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 规则执行Behavioral Admission包 / Gov Enforcement Behavior... | → | D_GOVERNANCE 生命周期管理: worktree生命周期 / Worktree Lifecycle (rule_bridge/worktr... | 导入依赖 / import_depends |
| 2 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOVERNANCE 生命周期管理: 能力lookup / Capability Lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 3 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOVERNANCE 生命周期管理: 能力lookup / Capability Lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 4 | metriccount漂移reconciler / Metric Count Drift Reconciler... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 5 | readme版本同步reconciler / Readme Version Sync Reconciler... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 6 | requirements版本同步reconciler / Requirements Version Syn... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 7 | 规则执行Behavioral Admission包 / Gov Enforcement Behavior... | → | D_GOV_AUDIT 审计追踪: MCP结果推送 / MCP Result Push (behavioral_admission/mcp_r... | 导入依赖 / import_depends |
| 8 | 规则执行Behavioral Admission包 / Gov Enforcement Behavior... | → | D_GOV_AUDIT 审计追踪: 后process / Post Process (behavioral_admission/post_proce... | 导入依赖 / import_depends |
| 9 | 规则执行Behavioral Admission包 / Gov Enforcement Behavior... | → | D_GOV_AUDIT 审计追踪: 直觉编码执行器 / Vibe Coding Enforcer (behavioral_admissi... | 导入依赖 / import_depends |
| 10 | 门禁事件适配器 / Gate Event Adapter (behavioral_admission... | → | D_GOV_AUDIT 审计追踪: 事件store / Event Store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 11 | verdict引擎 / Verdict Engine (behavioral_admission/verdic... | → | D_GOV_AUDIT 审计追踪: 模型 / Models (gov_audit/models.py) | 导入依赖 / import_depends |
| 12 | emergencycommit / Emergency Commit (rule_bridge/emergency... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 13 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: 蓝图status过渡reconciler / Blueprint Status Transition Re... | 导入依赖 / import_depends |
| 14 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: commitgatewayabuse监控器reconciler / Commit Gateway Abuse... | 导入依赖 / import_depends |
| 15 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: 跨层contractsignaturereconciler / Cross Layer Contract Si... | 导入依赖 / import_depends |
| 16 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: 错误模式consumerreconciler / Error Pattern Consumer Recon... | 导入依赖 / import_depends |
| 17 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: git性能监控器reconciler / Git Performance Monitor Reconci... | 导入依赖 / import_depends |
| 18 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: reconcile运行器 / Reconcile Runner (audit/reconcile_runne... | 导入依赖 / import_depends |
| 19 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 20 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: remediationprogressreconciler / Remediation Progress Reco... | 导入依赖 / import_depends |
| 21 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: 运行时违规snapshotreconciler / Runtime Violation Snapshot... | 导入依赖 / import_depends |
| 22 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_AUDIT 审计追踪: workspacehygienereconciler / Workspace Hygiene Reconciler... | 导入依赖 / import_depends |
| 23 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_AUDIT 审计追踪: AI错误模式library / AI Error Pattern Library (audit/ai_er... | 导入依赖 / import_depends |
| 24 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_AUDIT 审计追踪: reconcile运行器 / Reconcile Runner (audit/reconcile_runne... | 导入依赖 / import_depends |
| 25 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 26 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_AUDIT 审计追踪: workspacehygienereconciler / Workspace Hygiene Reconciler... | 导入依赖 / import_depends |
| 27 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_CODE_QUALITY 代码质量治理: 门禁自动registrar / Gate Auto Registrar (rule_bridge/gate... | 导入依赖 / import_depends |
| 28 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_CODE_QUALITY 代码质量治理: 规则执行Commit Gates包 / Gov Enforcement Commit Gates Pac... | 导入依赖 / import_depends |
| 29 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_CODE_QUALITY 代码质量治理: 能力lookuprequired门禁 / Capability Lookup Required Gate ... | 导入依赖 / import_depends |
| 30 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_GOV_CODE_QUALITY 代码质量治理: 测试源一致性门禁 / Test Source Consistency Gate (commit_g... | 导入依赖 / import_depends |
| 31 | 测试create守卫 / Test Create Guard (commit_gates/test_cre... | → | D_GOV_CODE_QUALITY 代码质量治理: create守卫 / Create Guard (commit_gates/create_guard.py) | 测试依赖 / test_depends |
| 32 | 测试r5digitsuffix门禁 / Test R5 Digit Suffix Gate (commit... | → | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / R5 Digit Suffix Gate (commit_gates/r5... | 测试依赖 / test_depends |
| 33 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: phase管理器 / Phase Manager (ops_governance/phase_manager... | 导入依赖 / import_depends |
| 34 | metriccount漂移reconciler / Metric Count Drift Reconciler... | → | D_GOV_SCRIPTS 脚本治理: 架构健康仪表板 / Architecture Health Dashboard (governanc... | 导入依赖 / import_depends |
| 35 | 会话worktree命令行 / Session Worktree CLI (governance/ses... | → | D_GOV_SCRIPTS 脚本治理: constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 36 | 合规规则 / Compliance Rule (rule_enforcement/compliance_r... | → | D_INFRASTRUCTURE 跨层契约基础设施: 合规规则 / Compliance Rule (contracts/compliance_rule.py) | 导入依赖 / import_depends |
| 37 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_INFRA_RUNTIME 运行时集成: gitbatcher / Git Batcher (infrastructure/git_batcher.py) | 导入依赖 / import_depends |
| 38 | approval / Approval (rule_enforcement/approval.py) | → | D_INTEGRATION 管线路由: approval类型 / Approval Types (contracts/approval_types.py) | 导入依赖 / import_depends |
| 39 | 预飞行门禁 / Pre Flight Gate (rule_enforcement/pre_flight... | → | D_OPS 反馈循环: 预算引擎 / Budget Engine (ops_governance/budget_engine.py) | 导入依赖 / import_depends |
| 40 | 预飞行门禁 / Pre Flight Gate (rule_enforcement/pre_flight... | → | D_OPS 反馈循环: 预算模型 / Budget Models (ops_governance/budget_models.py) | 导入依赖 / import_depends |
| 41 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 导入依赖 / import_depends |
| 42 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_SECURITY 对抗验证: commit触发器 / Commit Trigger (adversarial_validation/com... | 导入依赖 / import_depends |
| 43 | 心跳daemon / Heartbeat Daemon (rule_bridge/heartbeat_daem... | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 导入依赖 / import_depends |
| 44 | 会话claim / Session Claim (rule_bridge/session_claim.py) | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 导入依赖 / import_depends |
| 45 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 导入依赖 / import_depends |
| 46 | 测试claimfilesforedit / Test Claim Files For Edit (rule_b... | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 测试依赖 / test_depends |
| 47 | 会话worktree命令行 / Session Worktree CLI (governance/ses... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 48 | 门禁事件适配器 / Gate Event Adapter (behavioral_admission... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 49 | gpu共识调度器 / Gpu Consensus Scheduler (behavioral_admis... | → | D_SHARED 共享服务: constants / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 50 | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 51 | emergencycommit / Emergency Commit (rule_bridge/emergency... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 52 | emergencycommit / Emergency Commit (rule_bridge/emergency... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 53 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_SHARED 共享服务: 事件总线 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 54 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 55 | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 56 | 会话claim / Session Claim (rule_bridge/session_claim.py) | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 57 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 58 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 59 | 会话worktree / Session Worktree (rule_bridge/session_work... | → | D_SHARED 共享服务: workspace遥测 / Workspace Telemetry (io/workspace_telemet... | 导入依赖 / import_depends |
| 60 | worktree管理器 / Worktree Manager (rule_bridge/worktree_m... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 61 | worktree管理器 / Worktree Manager (rule_bridge/worktree_m... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 62 | worktree池 / Worktree Pool (rule_bridge/worktree_pool.py) | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 63 | worktree池 / Worktree Pool (rule_bridge/worktree_pool.py) | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 64 | dlqretry策略 / Dlq Retry Policy (rule_enforcement/dlq_ret... | → | D_SHARED 共享服务: dlq / Dlq (events/dlq.py) | 导入依赖 / import_depends |
| 65 | dlqretry策略 / Dlq Retry Policy (rule_enforcement/dlq_ret... | → | D_SHARED 共享服务: observer / Observer (infra/observer.py) | 导入依赖 / import_depends |
| 66 | dlqretry策略 / Dlq Retry Policy (rule_enforcement/dlq_ret... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 67 | 规则监视器 / Rule Watcher (rule_engine/rule_watcher.py) | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 68 | 规则监视器 / Rule Watcher (rule_engine/rule_watcher.py) | → | D_SHARED 共享服务: sqlite工厂 / Sqlite Factory (io/sqlite_factory.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_DATA 数据接入层: 质量门禁 / Quality Gate (data/quality_gate.py) | → | 质量门禁 / Quality Gate (rule_enforcement/quality_gate.py) | 导入依赖 / import_depends |
| 2 | D_DATA 数据接入层: 数据接入层Satellite Geospatial Engine包 / Data Satellite ... | → | 质量门禁 / Quality Gate (rule_enforcement/quality_gate.py) | 导入依赖 / import_depends |
| 3 | D_DATA 数据接入层: 测试market质量校验器 / Test Market Quality Validator (dat... | → | 质量门禁 / Quality Gate (rule_enforcement/quality_gate.py) | 测试依赖 / test_depends |
| 4 | D_GOVERNANCE 生命周期管理: gitcommit / Git Commit (scripts/git_commit.py) | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: 合规管理器 / Compliance Manager (compliance_gate_a6/compl... | → | 合规规则 / Compliance Rule (rule_enforcement/compliance_r... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: 测试会话感知stashredblue / Test Session Aware Stash Red B... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 8 | D_GOVERNANCE 生命周期管理: 测试gitcommitconcurrent / Test Git Commit Concurrent (git... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 测试依赖 / test_depends |
| 9 | D_GOVERNANCE 生命周期管理: 测试gitcommitconcurrent / Test Git Commit Concurrent (git... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 10 | D_GOVERNANCE 生命周期管理: 测试gitcommitextreme / Test Git Commit Extreme (git/test_... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 11 | D_GOVERNANCE 生命周期管理: 测试gitcommitgateway / Test Git Commit Gateway (git/test_... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 12 | D_GOVERNANCE 生命周期管理: 测试任务repogateway端到端 / Test Task Repo Gateway E2E (t... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 13 | D_GOV_AUDIT 审计追踪: git性能监控器reconciler / Git Performance Monitor Reconci... | → | 会话worktree / Session Worktree (rule_bridge/session_work... | 导入依赖 / import_depends |
| 14 | D_GOV_AUDIT 审计追踪: reconcileworker / Reconcile Worker (audit/reconcile_worke... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |
| 15 | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 16 | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | → | 会话worktree / Session Worktree (rule_bridge/session_work... | 导入依赖 / import_depends |
| 17 | D_GOV_AUDIT 审计追踪: 测试reconcile异步 / Test Reconcile Async (audit/test_reco... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 18 | D_GOV_AUDIT 审计追踪: 测试reconcileworkerselfheal / Test Reconcile Worker Selfh... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 测试依赖 / test_depends |
| 19 | D_GOV_AUDIT 审计追踪: 测试会话worktree异步reconcile / Test Session Worktree Asy... | → | 会话worktree / Session Worktree (rule_bridge/session_work... | 测试依赖 / test_depends |
| 20 | D_GOV_CODE_QUALITY 代码质量治理: referencehelpers / Reference Helpers (commit_gates/_refer... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 21 | D_GOV_CODE_QUALITY 代码质量治理: 架构reference门禁 / Arch Reference Gate (commit_gates/arc... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 22 | D_GOV_CODE_QUALITY 代码质量治理: asynciorunin上下文门禁 / Asyncio Run In Context Gate (com... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 23 | D_GOV_CODE_QUALITY 代码质量治理: baregetenv门禁 / Bare Getenv Gate (commit_gates/bare_gete... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 24 | D_GOV_CODE_QUALITY 代码质量治理: baresql门禁 / Bare Sql Gate (commit_gates/bare_sql_gate.py) | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 25 | D_GOV_CODE_QUALITY 代码质量治理: baresubprocess门禁 / Bare Subprocess Gate (commit_gates/b... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 26 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule一致性门禁 / Blueprint Amodule Consistency Gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 27 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图amodule跨检查门禁 / Blueprint Amodule Cross Check Gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 28 | D_GOV_CODE_QUALITY 代码质量治理: 蓝图format门禁 / Blueprint Format Gate (commit_gates/blue... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 29 | D_GOV_CODE_QUALITY 代码质量治理: 能力一致性门禁 / Capability Consistency Gate (commit_gate... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 30 | D_GOV_CODE_QUALITY 代码质量治理: 能力lookuprequired门禁 / Capability Lookup Required Gate ... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 31 | D_GOV_CODE_QUALITY 代码质量治理: 能力overlap门禁 / Capability Overlap Gate (commit_gates/c... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 32 | D_GOV_CODE_QUALITY 代码质量治理: ch批次size门禁 / Ch Batch Size Gate (commit_gates/ch_batc... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 33 | D_GOV_CODE_QUALITY 代码质量治理: chfinal门禁 / Ch Final Gate (commit_gates/ch_final_gate.py) | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 34 | D_GOV_CODE_QUALITY 代码质量治理: ch版本col门禁 / Ch Version Col Gate (commit_gates/ch_vers... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 35 | D_GOV_CODE_QUALITY 代码质量治理: claimrequired门禁 / Claim Required Gate (commit_gates/cla... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 36 | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / Consumers Accuracy Gate (commit_g... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 37 | D_GOV_CODE_QUALITY 代码质量治理: create守卫 / Create Guard (commit_gates/create_guard.py) | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 38 | D_GOV_CODE_QUALITY 代码质量治理: danglingreference门禁 / Dangling Reference Gate (commit_g... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 39 | D_GOV_CODE_QUALITY 代码质量治理: 数据任务completeness门禁 / Data Task Completeness Gate (c... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 40 | D_GOV_CODE_QUALITY 代码质量治理: datetimenowforbidden门禁 / Datetime Now Forbidden Gate (c... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 41 | D_GOV_CODE_QUALITY 代码质量治理: depgraphfreshness门禁 / Depgraph Freshness Gate (commit_g... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 42 | D_GOV_CODE_QUALITY 代码质量治理: depgraphwrite路径门禁 / Depgraph Write Path Gate (commit_... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 43 | D_GOV_CODE_QUALITY 代码质量治理: derivationannotation门禁 / Derivation Annotation Gate (co... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 44 | D_GOV_CODE_QUALITY 代码质量治理: directorycontract门禁 / Directory Contract Gate (commit_g... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 45 | D_GOV_CODE_QUALITY 代码质量治理: docrefbroken门禁 / Doc Ref Broken Gate (commit_gates/doc_... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 46 | D_GOV_CODE_QUALITY 代码质量治理: domainfk门禁 / Domain Fk Gate (commit_gates/domain_fk_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 47 | D_GOV_CODE_QUALITY 代码质量治理: domainnamezhdirectaccess门禁 / Domain Name Zh Direct Acce... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 48 | D_GOV_CODE_QUALITY 代码质量治理: emptyhandler门禁 / Empty Handler Gate (commit_gates/empty... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 49 | D_GOV_CODE_QUALITY 代码质量治理: encoding门禁 / Encoding Gate (commit_gates/encoding_gate.py) | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 50 | D_GOV_CODE_QUALITY 代码质量治理: exemptzonefrontmatter门禁 / Exempt Zone Frontmatter Gate ... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 51 | D_GOV_CODE_QUALITY 代码质量治理: 文件copy门禁 / File Copy Gate (commit_gates/file_copy_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 52 | D_GOV_CODE_QUALITY 代码质量治理: 文件placementTTL门禁 / File Placement TTL Gate (commit_ga... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 53 | D_GOV_CODE_QUALITY 代码质量治理: folder容量hard限制门禁 / Folder Capacity Hard Limit Gate ... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 54 | D_GOV_CODE_QUALITY 代码质量治理: foreignchange门禁 / Foreign Change Gate (commit_gates/for... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / Forged Gw Marker Gate (commit_gates/... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 56 | D_GOV_CODE_QUALITY 代码质量治理: functiondup门禁 / Function Dup Gate (commit_gates/functio... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 57 | D_GOV_CODE_QUALITY 代码质量治理: gitcall预算门禁 / Git Call Budget Gate (commit_gates/git_... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 58 | D_GOV_CODE_QUALITY 代码质量治理: godclass门禁 / God Class Gate (commit_gates/god_class_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 59 | D_GOV_CODE_QUALITY 代码质量治理: hardcodedurl门禁 / Hardcoded Url Gate (commit_gates/hardc... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 60 | D_GOV_CODE_QUALITY 代码质量治理: heldoverlap门禁 / Held Overlap Gate (commit_gates/held_ov... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 61 | D_GOV_CODE_QUALITY 代码质量治理: highcomplexity门禁 / High Complexity Gate (commit_gates/h... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 62 | D_GOV_CODE_QUALITY 代码质量治理: iduniqueness门禁 / Id Uniqueness Gate (commit_gates/id_un... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 63 | D_GOV_CODE_QUALITY 代码质量治理: 导入direction门禁 / Import Direction Gate (commit_gates/i... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 64 | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / Import Integrity Gate (commit_gates/impo... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 65 | D_GOV_CODE_QUALITY 代码质量治理: issueresolved完整性门禁 / Issue Resolved Integrity Gate (... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 66 | D_GOV_CODE_QUALITY 代码质量治理: longparamlist门禁 / Long Param List Gate (commit_gates/lo... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 67 | D_GOV_CODE_QUALITY 代码质量治理: 手册onlypermanent门禁 / Manual Only Permanent Gate (commi... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 68 | D_GOV_CODE_QUALITY 代码质量治理: MCP版本field门禁 / MCP Version Field Gate (commit_gates/m... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 69 | D_GOV_CODE_QUALITY 代码质量治理: 模块id一致性门禁 / Module Id Consistency Gate (commit_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 70 | D_GOV_CODE_QUALITY 代码质量治理: msgexposure门禁 / Msg Exposure Gate (commit_gates/msg_exp... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 71 | D_GOV_CODE_QUALITY 代码质量治理: msgstyle门禁 / Msg Style Gate (commit_gates/msg_style_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 72 | D_GOV_CODE_QUALITY 代码质量治理: mutableconstwithoutfinal门禁 / Mutable Const Without Fina... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 73 | D_GOV_CODE_QUALITY 代码质量治理: new文件depgraph门禁 / New File Depgraph Gate (commit_gate... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 74 | D_GOV_CODE_QUALITY 代码质量治理: no导入sideeffect门禁 / No Import Side Effect Gate (commit... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 75 | D_GOV_CODE_QUALITY 代码质量治理: noqavalidation门禁 / Noqa Validation Gate (commit_gates/n... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 76 | D_GOV_CODE_QUALITY 代码质量治理: openwithoutwith门禁 / Open Without With Gate (commit_gate... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 77 | D_GOV_CODE_QUALITY 代码质量治理: orphan模块门禁 / Orphan Module Gate (commit_gates/orphan_... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 78 | D_GOV_CODE_QUALITY 代码质量治理: panorama对齐门禁 / Panorama Alignment Gate (commit_gates/... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 79 | D_GOV_CODE_QUALITY 代码质量治理: perm触发器门禁 / Perm Trigger Gate (commit_gates/perm_tri... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 80 | D_GOV_CODE_QUALITY 代码质量治理: precommit离线门禁 / Precommit Offline Gate (commit_gates/... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 81 | D_GOV_CODE_QUALITY 代码质量治理: pureassertion门禁 / Pure Assertion Gate (commit_gates/pur... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 82 | D_GOV_CODE_QUALITY 代码质量治理: pureshim门禁 / Pure Shim Gate (commit_gates/pure_shim_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 83 | D_GOV_CODE_QUALITY 代码质量治理: r5digitsuffix门禁 / R5 Digit Suffix Gate (commit_gates/r5... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 84 | D_GOV_CODE_QUALITY 代码质量治理: reconciler健康门禁 / Reconciler Health Gate (commit_gates... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 85 | D_GOV_CODE_QUALITY 代码质量治理: relative路径literal门禁 / Relative Path Literal Gate (com... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 86 | D_GOV_CODE_QUALITY 代码质量治理: renamedepgraph同步门禁 / Rename Depgraph Sync Gate (commi... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 87 | D_GOV_CODE_QUALITY 代码质量治理: 规则执行pairing门禁 / Rule Execution Pairing Gate (commit... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 88 | D_GOV_CODE_QUALITY 代码质量治理: 规则fourway对齐门禁 / Rule Four Way Alignment Gate (commi... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 89 | D_GOV_CODE_QUALITY 代码质量治理: rulingcommitverified门禁 / Ruling Commit Verified Gate (c... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 90 | D_GOV_CODE_QUALITY 代码质量治理: rulingreference门禁 / Ruling Reference Gate (commit_gates... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 91 | D_GOV_CODE_QUALITY 代码质量治理: schema文件exists门禁 / Schema File Exists Gate (commit_ga... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 92 | D_GOV_CODE_QUALITY 代码质量治理: scripts导入完整性门禁 / Scripts Import Integrity Gate (co... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 93 | D_GOV_CODE_QUALITY 代码质量治理: 会话required门禁 / Session Required Gate (commit_gates/se... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 94 | D_GOV_CODE_QUALITY 代码质量治理: snapshot漂移门禁 / Snapshot Drift Gate (commit_gates/snap... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 95 | D_GOV_CODE_QUALITY 代码质量治理: ssotredefinition门禁 / Ssot Redefinition Gate (commit_gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 96 | D_GOV_CODE_QUALITY 代码质量治理: tablename注册表门禁 / Table Name Registry Gate (commit_ga... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 97 | D_GOV_CODE_QUALITY 代码质量治理: 测试源一致性门禁 / Test Source Consistency Gate (commit_g... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 98 | D_GOV_CODE_QUALITY 代码质量治理: testscoverage门禁 / Tests Coverage Gate (commit_gates/tes... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 99 | D_GOV_CODE_QUALITY 代码质量治理: TTL门禁 / TTL Gate (commit_gates/ttl_gate.py) | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 100 | D_GOV_CODE_QUALITY 代码质量治理: undefinedname门禁 / Undefined Name Gate (commit_gates/und... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 101 | D_GOV_CODE_QUALITY 代码质量治理: unsafedictspread门禁 / Unsafe Dict Spread Gate (commit_ga... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 102 | D_GOV_CODE_QUALITY 代码质量治理: vocab链门禁 / Vocab Chain Gate (commit_gates/vocab_chain_... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 103 | D_GOV_CODE_QUALITY 代码质量治理: vocabhardcode门禁 / Vocab Hardcode Gate (commit_gates/voc... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 104 | D_GOV_CODE_QUALITY 代码质量治理: Zephyr环境directaccess门禁 / Zephyr Env Direct Access Gat... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 105 | D_GOV_CODE_QUALITY 代码质量治理: 门禁自动registrar / Gate Auto Registrar (rule_bridge/gate... | → | commit门禁注册表 / Commit Gate Registry (rule_bridge/comm... | 导入依赖 / import_depends |
| 106 | D_GOV_CODE_QUALITY 代码质量治理: 测试审计worktree运维遥测 / Test Audit Worktree Ops Teleme... | → | 会话worktree / Session Worktree (rule_bridge/session_work... | 测试依赖 / test_depends |
| 107 | D_GOV_DRIFT 漂移检测: tamperproof审计 / Tamper Proof Audit (gov_drift/tamper_pr... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |
| 108 | D_GOV_OPS_RESILIENCE 运维弹性治理: 安全gateway基础 / Security Gateway Base (security_governa... | → | 合规规则 / Compliance Rule (rule_enforcement/compliance_r... | 导入依赖 / import_depends |
| 109 | D_GOV_RULE 规则治理: 规则引擎模块集 / Rule Engine Package (rule_engine/__init_... | → | 规则debt审计器 / Rule Debt Auditor (rule_engine/rule_debt... | config_depends / config_depends |
| 110 | D_GOV_SCRIPTS 脚本治理: concurrentcommit测试 / Concurrent Commit Test (repair/con... | → | gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |

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
