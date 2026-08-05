---
doc_type: architecture_view
title: D_SECURITY 对抗验证架构文档
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 27_d_security / 对抗验证域 / Adversarial Validation

> **功能简介 / Overview**: 对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证

> **文档作用 / Purpose**: 展示 对抗验证（D_SECURITY）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/27_d_security.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 27 | Number | 27 |
| 域ID | D_SECURITY | Domain ID | D_SECURITY |
| 域名称 | 对抗验证 | Domain Name | Adversarial Validation |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 171 | Module Count | 171 |
| 域内依赖 | 125 | Internal Dependencies | 125 |
| 跨域入边 | 72 | Cross-domain Incoming | 72 |
| 跨域出边 | 102 | Cross-domain Outgoing | 102 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 171 | Production Modules | 171 |
| 容量 | 171/150 (超容) | Capacity | 171/150 (超容) |
| 描述 | 孤儿文件检测(orphan_detector) | Description | 孤儿文件检测(orphan_detector) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 171 个模块（生产态 171 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_drift_main_py["主入口<br/>Drift Detector MOD-INF-023 CLI — 漂移扫描入口。<br/>Main<br/>文件: gov_drift/__main__.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_analysis_py["分析<br/>gov drift包的analysis模块<br/>文件: gov_drift/_analysis.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_core_py["核心<br/>gov drift包的core模块<br/>文件: gov_drift/_core.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_drift_py["漂移<br/>gov drift包的drift模块<br/>文件: gov_drift/_drift.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_infrastructure_py["基础设施<br/>gov drift包的infrastructure模块<br/>文件: gov_drift/_infrastructure.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_scanners_py["扫描器<br/>gov drift包的scanners模块<br/>文件: gov_drift/_scanners.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_rbac_contracts_py["G-CT-001 RBAC 契约<br/>agent-rbac/contracts.py — G-CT-001 RBAC 契约<br/>（re-export）。<br/>文件: agent-rbac/contracts.py<br/>(生产态 / production)"]
    src_zephyr_red_blue_validator_init_py["zephyr/red_blue_validator 包入口<br/>red_blue_validator — re-export shim for<br/>zephyr.security.adversarial_validation.<br/>Init<br/>文件: red_blue_validator/__init__.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_adversarial_resilience_py["对抗Resilience<br/>AdversarialResilience - adversarial resilience<br/>& OWASP coverage.<br/>文件: access_control/adversarial_resilience.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_agent_creation_policy_py["Agent 创建策略.<br/>AgentCreationPolicy — Agent 创建策略.<br/>Agent Creation Policy<br/>文件: access_control/agent_creation_policy.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_asymmetric_audit_py["Asymmetric审计<br/>AsymmetricAudit - quorum-based approval for<br/>high-risk operations.<br/>Asymmetric Audit<br/>文件: access_control/asymmetric_audit.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_auto_maintenance_py["自动维护与规则健康仪表盘.<br/>AutoMaintenance — 自动维护与规则健康仪表盘.<br/>Auto Maintenance<br/>文件: access_control/auto_maintenance.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_blueprint_fidelity_py["蓝图保真度检查.<br/>BlueprintFidelity — 蓝图保真度检查.<br/>Blueprint Fidelity<br/>文件: access_control/blueprint_fidelity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_build_sanitizer_py["zephyr.security.access_control.build_sanitizer<br/>— implementation pending.'''<br/>安全/access control包的build_sanitizer模块<br/>Build Sanitizer<br/>文件: access_control/build_sanitizer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cache_invalidation_py["缓存失效事件管理.<br/>CacheInvalidation — 缓存失效事件管理.<br/>Cache Invalidation<br/>文件: access_control/cache_invalidation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_canary_rollout_manager_py["灰度发布管理器.<br/>CanaryRolloutManager — 灰度发布管理器.<br/>Canary Rollout Manager<br/>文件: access_control/canary_rollout_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cascading_failure_isolator_py["zephyr.security.access_control.cascading_failure<br/>_isolator — implementation pending.'''<br/>安全/access<br/>control包的cascading_failure_isolator模块<br/>Cascading Failure Isolator<br/>文件: access_control<br/>/cascading_failure_isolator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_compliance_matrix_py["合规Matrix<br/>安全/access control包的compliance_matrix模块<br/>Compliance Matrix<br/>文件: access_control/compliance_matrix.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cross_cutting_py["横切面权限组件.<br/>CrossCutting — 横切面权限组件.<br/>Cross Cutting<br/>文件: access_control/cross_cutting.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_decision_explainer_py["拒绝决策的结构化解释器.<br/>DecisionExplainer — 拒绝决策的结构化解释器.<br/>Decision Explainer<br/>文件: access_control/decision_explainer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_decision_registry_py["决策注册表<br/>DecisionRegistry - decision log with query and<br/>stats.<br/>Decision Registry<br/>文件: access_control/decision_registry.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_defense_depth_py["zephyr.security.access_control.defense_depth —<br/>implementation pending.'''<br/>安全/access control包的defense_depth模块<br/>Defense Depth<br/>文件: access_control/defense_depth.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_dependency_auditor_py["Dependency审计器<br/>安全/access control包的dependency_auditor模块<br/>Dependency Auditor<br/>文件: access_control/dependency_auditor.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_derive_rbac_roles_py["RBAC 角色派生器.<br/>RBACRoleDeriver — RBAC 角色派生器.<br/>Derive Rbac Roles<br/>文件: access_control/derive_rbac_roles.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_anomaly_detector_py["异常检测器<br/>AnomalyDetector - rolling z-score anomaly<br/>detection per field.<br/>Anomaly Detector<br/>文件: detectors/anomaly_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_context_drift_detector_py["上下文漂移与范围蔓延检测.<br/>ContextDriftDetector — 上下文漂移与范围蔓延检测.<br/>Context Drift Detector<br/>文件: detectors/context_drift_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_cross_session_detector_py["跨 Session 检测器.<br/>CrossSessionDetector — 跨 Session 检测器.<br/>Cross Session Detector<br/>文件: detectors/cross_session_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_false_completion_detector_py["虚假完成检测.<br/>FalseCompletionDetector — 虚假完成检测.<br/>False Completion Detector<br/>文件: detectors/false_completion_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py["多 agent 合谋检测.<br/>MultiAgentCollusionDetector — 多 agent 合谋检测.<br/>Multi Agent Collusion Detector<br/>文件: detectors<br/>/multi_agent_collusion_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_shell_dialect_detector_py["Shell 方言检测器.<br/>ShellDialectDetector — Shell 方言检测器.<br/>Shell Dialect Detector<br/>文件: detectors/shell_dialect_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_dry_run_py["权限模拟与影响分析.<br/>DryRun — 权限模拟与影响分析.<br/>Dry Run<br/>文件: access_control/dry_run.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_emergency_override_py["紧急覆盖令牌管理.<br/>EmergencyOverride — 紧急覆盖令牌管理.<br/>Emergency Override<br/>文件: access_control/emergency_override.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_environment_manager_py["Environment管理器<br/>安全/access control包的environment_manager模块<br/>Environment Manager<br/>文件: access_control/environment_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_escalation_handler_py["Escalation处理器<br/>安全/access control包的escalation_handler模块<br/>Escalation Handler<br/>文件: access_control/escalation_handler.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_exceptions_py["AgentRbac 异常类型.<br/>安全/access control包的exceptions模块<br/>文件: access_control/exceptions.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_genesis_bootstrap_py["RBAC系统启动引导器.<br/>GenesisBootstrap — RBAC系统启动引导器.<br/>Genesis Bootstrap<br/>文件: access_control/genesis_bootstrap.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guard_layers_py["权限守卫层组件.<br/>GuardLayers — 权限守卫层组件.<br/>Guard Layers<br/>文件: access_control/guard_layers.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_abac_guard_py["基于属性的权限守卫.<br/>ABACGuard — 基于属性的权限守卫.<br/>Abac Guard<br/>文件: guards/abac_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_anti_pattern_guard_py["反模式守卫<br/>安全/guards包的anti_pattern_guard模块<br/>Anti Pattern Guard<br/>文件: guards/anti_pattern_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_audit_log_guard_py["审计日志注入防护守卫<br/>audit_log_guard.py — 审计日志注入防护守卫<br/>Audit Log Guard<br/>文件: guards/audit_log_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_cybersec_2026_guard_py["2026 网络安全威胁检测.<br/>Cybersec2026Guard — 2026 网络安全威胁检测.<br/>Cybersec 2026 Guard<br/>文件: guards/cybersec_2026_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_input_guard_py["输入参数守卫.<br/>InputGuard — 输入参数守卫.<br/>Input Guard<br/>文件: guards/input_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_memory_guard_py["内存访问守卫.<br/>MemoryGuard — 内存访问守卫.<br/>Memory Guard<br/>文件: guards/memory_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_memory_provenance_guard_py["记忆来源溯源守卫.<br/>MemoryProvenanceGuard — 记忆来源溯源守卫.<br/>Memory Provenance Guard<br/>文件: guards/memory_provenance_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_native_api_guard_py["原生 API 守卫.<br/>NativeApiGuard — 原生 API 守卫.<br/>Native Api Guard<br/>文件: guards/native_api_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_novel_attack_guard_py["新型攻击行为画像.<br/>NovelAttackGuard — 新型攻击行为画像.<br/>Novel Attack Guard<br/>文件: guards/novel_attack_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_output_guard_py["输出内容守卫.<br/>OutputGuard — 输出内容守卫.<br/>Output Guard<br/>文件: guards/output_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_path_guard_py["路径守卫.<br/>PathGuard — 路径守卫.<br/>Path Guard<br/>文件: guards/path_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_replay_attack_guard_py["重放攻击防护.<br/>ReplayAttackGuard — 重放攻击防护.<br/>Replay Attack Guard<br/>文件: guards/replay_attack_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_rule_injection_guard_py["规则注入守卫.<br/>RuleInjectionGuard — 规则注入守卫.<br/>Rule Injection Guard<br/>文件: guards/rule_injection_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_sequence_guard_py["操作序列守卫.<br/>SequenceGuard — 操作序列守卫.<br/>Sequence Guard<br/>文件: guards/sequence_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_toctou_guard_py["Toctou守卫<br/>TOCTOUGuard — TOCTOU (Time-of-Check to<br/>Time-of-Use) 防护.<br/>Toctou Guard<br/>文件: guards/toctou_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_vibe_coding_guard_py["Vibe Coding 攻击面检测.<br/>VibeCodingGuard — Vibe Coding 攻击面检测.<br/>Vibe Coding Guard<br/>文件: guards/vibe_coding_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_integration_py["集成<br/>IntegrationManager - system integration<br/>registry & health check.<br/>文件: access_control/integration.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_integrity_self_check_py["完整性自检.<br/>IntegritySelfCheck — 完整性自检.<br/>Integrity Self Check<br/>文件: access_control/integrity_self_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_intent_binder_py["意图绑定与漂移检测.<br/>IntentBinder — 意图绑定与漂移检测.<br/>Intent Binder<br/>文件: access_control/intent_binder.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_key_hierarchy_py["zephyr.security.access_control.key_hierarchy —<br/>implementation pending.'''<br/>安全/access control包的key_hierarchy模块<br/>Key Hierarchy<br/>文件: access_control/key_hierarchy.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_legal_audit_chain_py["Legal审计链<br/>LegalAuditChain - append-only hash-chained<br/>legal audit log.<br/>Legal Audit Chain<br/>文件: access_control/legal_audit_chain.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_microstructure_defense_py["—对抗做市/交易微结构攻击的策略与保真度因子<br/>微结构防御——对抗做市<br/>/交易微结构攻击的策略与保真度因子。<br/>Microstructure Defense<br/>文件: access_control/microstructure_defense.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_monotonic_clock_py["单调时钟.<br/>MonotonicClock — 单调时钟.<br/>Monotonic Clock<br/>文件: access_control/monotonic_clock.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_non_repudiation_py["不可抵赖性审计签名.<br/>NonRepudiation — 不可抵赖性审计签名.<br/>Non Repudiation<br/>文件: access_control/non_repudiation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_observability_py["指标上报与异常检测.<br/>ObservabilityReporter — 指标上报与异常检测.<br/>文件: access_control/observability.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_main_py["主入口<br/>安全/orphan judge包的main__模块<br/>文件: orphan_judge/__main__.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_config_loader_py["配置加载器<br/>安全/orphan judge包的config_loader模块<br/>Config Loader<br/>文件: orphan_judge/config_loader.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_drift_bridge_py["漂移桥接器<br/>安全/orphan judge包的drift_bridge模块<br/>Drift Bridge<br/>文件: orphan_judge/drift_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_escalation_bridge_py["Escalation桥接器<br/>安全/orphan judge包的escalation_bridge模块<br/>Escalation Bridge<br/>文件: orphan_judge/escalation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_feedback_bridge_py["反馈桥接器<br/>安全/orphan judge包的feedback_bridge模块<br/>Feedback Bridge<br/>文件: orphan_judge/feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_kb_bridge_py["Kb桥接器<br/>安全/orphan judge包的kb_bridge模块<br/>Kb Bridge<br/>文件: orphan_judge/kb_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py["MCP集成<br/>安全/orphan judge包的mcp_integration模块<br/>Mcp Integration<br/>文件: orphan_judge/mcp_integration.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py["—整合 SafetyFence 安全检查后执行处置动作<br/>安全/orphan judge包的orphan_collector模块<br/>Orphan Collector<br/>文件: orphan_judge/orphan_collector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_orphan_detector_py["孤儿检测器<br/>(INVARIANTS) 蓝图 §4 文件清单与代码双向对齐<br/>Orphan Detector<br/>文件: orphan_judge/orphan_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py["Rbac桥接器<br/>安全/orphan judge包的rbac_bridge模块<br/>Rbac Bridge<br/>文件: orphan_judge/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py["L1 引用图引擎<br/>AST解析+import链遍历，判断文件是否被其他文件引用<br/>。<br/>Reference Graph Engine<br/>文件: orphan_judge/reference_graph_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_registration_checker_py["L0 注册检查器<br/>扫描项目注册表，判断文件是否已登记在册。<br/>Registration Checker<br/>文件: orphan_judge/registration_checker.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_report_generator_py["报告生成器<br/>安全/orphan judge包的report_generator模块<br/>Report Generator<br/>文件: orphan_judge/report_generator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py["L4 独立价值评估器<br/>六指标加权评分: 文件大小(15%) + 代码行数(20%) +<br/>定义数(20%)<br/>Standalone Evaluator<br/>文件: orphan_judge/standalone_evaluator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_swid_tag_py["SWID标签<br/>安全/orphan judge包的swid_tag模块<br/>Swid Tag<br/>文件: orphan_judge/swid_tag.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py["L3 独特价值分析器<br/>AST节点比对，检测文件中的独特代码元素(类/函数<br/>/常量定义等)。<br/>Unique Analyzer<br/>文件: orphan_judge/unique_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_permission_hooks_py["权限钩子注册表.<br/>PermissionHooks — 权限钩子注册表.<br/>Permission Hooks<br/>文件: access_control/permission_hooks.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_permission_mode_manager_py["Permission模式管理器<br/>安全/access<br/>control包的permission_mode_manager模块<br/>Permission Mode Manager<br/>文件: access_control/permission_mode_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_phase_executor_py["阶段执行器<br/>安全/access control包的phase_executor模块<br/>Phase Executor<br/>文件: access_control/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_risk_mitigation_py["风险评估与缓解策略.<br/>RiskMitigation — 风险评估与缓解策略.<br/>Risk Mitigation<br/>文件: access_control/risk_mitigation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_rollback_sandbox_py["回滚Sandbox<br/>RollbackSandbox - isolate/execute/rollback<br/>pattern for reversible operations.<br/>Rollback Sandbox<br/>文件: access_control/rollback_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_secrets_lifecycle_py["Secrets生命周期<br/>安全/access control包的secrets_lifecycle模块<br/>Secrets Lifecycle<br/>文件: access_control/secrets_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_session_concurrency_py["Session 级并发协调模块<br/>（P2-SES 落地）<br/>Session Concurrency<br/>文件: access_control/session_concurrency.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_session_lifecycle_py["会话生命周期<br/>安全/access control包的session_lifecycle模块<br/>Session Lifecycle<br/>文件: access_control/session_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_bootstrap_verifier_py["Bootstrap验证器<br/>安全/verifiers包的bootstrap_verifier模块<br/>Bootstrap Verifier<br/>文件: verifiers/bootstrap_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_continuous_verifier_py["Continuous验证器<br/>安全/verifiers包的continuous_verifier模块<br/>Continuous Verifier<br/>文件: verifiers/continuous_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_contract_verifier_py["契约验证器.<br/>ContractVerifier — 契约验证器.<br/>Contract Verifier<br/>文件: verifiers/contract_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_micro_verifier_py["Micro验证器<br/>安全/verifiers包的micro_verifier模块<br/>Micro Verifier<br/>文件: verifiers/micro_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_post_action_verifier_py["事后动作验证器<br/>安全/verifiers包的post_action_verifier模块<br/>Post Action Verifier<br/>文件: verifiers/post_action_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_main_py["主入口<br/>安全/adversarial validation包的main__模块<br/>文件: adversarial_validation/__main__.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_ai_attack_generator_py["Ai攻击生成器<br/>安全/adversarial<br/>validation包的ai_attack_generator模块<br/>Ai Attack Generator<br/>文件: adversarial_validation<br/>/ai_attack_generator.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_async_monitor_py["Async监控器<br/>安全/adversarial validation包的async_monitor模块<br/>Async Monitor<br/>文件: adversarial_validation/async_monitor.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_attack_registry_py["攻击注册表<br/>安全/adversarial<br/>validation包的attack_registry模块<br/>Attack Registry<br/>文件: adversarial_validation/attack_registry.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_commit_trigger_py["提交触发器<br/>CommitTrigger — 事件驱动红蓝对抗触发器<br/>(MOD-INF-030).<br/>Commit Trigger<br/>文件: adversarial_validation/commit_trigger.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_constitution_engine_py["Constitution引擎<br/>安全/adversarial<br/>validation包的constitution_engine模块<br/>Constitution Engine<br/>文件: adversarial_validation<br/>/constitution_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_game_day_scheduler_py["GameDay调度器<br/>安全/adversarial<br/>validation包的game_day_scheduler模块<br/>Game Day Scheduler<br/>文件: adversarial_validation<br/>/game_day_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_injection_engine_py["注入引擎<br/>安全/adversarial<br/>validation包的injection_engine模块<br/>Injection Engine<br/>文件: adversarial_validation/injection_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_mcp_endpoints_py["MCP端点<br/>安全/adversarial validation包的mcp_endpoints模块<br/>Mcp Endpoints<br/>文件: adversarial_validation/mcp_endpoints.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_validator_event_bridge_py["订阅 EventBusBackpressure 的 fix_completed 事件<br/>ValidatorEventBridge — 红蓝验证器事件桥接<br/>(MOD-SEC-030).<br/>Validator Event Bridge<br/>文件: adversarial_validation<br/>/validator_event_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py["仪表盘应用<br/>LLM Security Gateway - Streamlit Dashboard.<br/>App<br/>文件: dashboard/app.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py["L6数据流<br/>安全/layers包的l6_data_flow模块<br/>L6 Data Flow<br/>文件: layers/l6_data_flow.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py["L8合规<br/>安全/layers包的l8_compliance模块<br/>L8 Compliance<br/>文件: layers/l8_compliance.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py["流程Sandbox<br/>L2a ProcessSandbox — subprocess 路径白名单沙箱<br/>Process Sandbox<br/>文件: llm_security/process_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py["对 Red Team 载荷施加 10 种变异技术，检验 LSG<br/>抗干扰能力.<br/>安全/self protection包的adversarial_mutator模块<br/>Adversarial Mutator<br/>文件: self_protection/adversarial_mutator.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py["L7 Red Team 对抗扫描器.<br/>安全/self protection包的red_team_scanner模块<br/>Red Team Scanner<br/>文件: self_protection/red_team_scanner.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_a2a_check_py["治理A2A检查测试<br/>安全包的test_governance_a2a_check模块<br/>Test Governance A2a Check<br/>文件: security/test_governance_a2a_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_approver_check_py["治理Approver检查测试<br/>安全包的test_governance_approver_check模块<br/>Test Governance Approver Check<br/>文件: security/test_governance_approver_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_bootstrap_superadmin_py["治理BootstrapSuperadmin测试<br/>安全包的test_governance_bootstrap_superadmin模块<br/>Test Governance Bootstrap Superadmin<br/>文件: security<br/>/test_governance_bootstrap_superadmin.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_capability_check_py["治理能力检查测试<br/>安全包的test_governance_capability_check模块<br/>Test Governance Capability Check<br/>文件: security<br/>/test_governance_capability_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_contracts_py["治理契约测试<br/>安全包的test_governance_contracts模块<br/>Test Governance Contracts<br/>文件: security/test_governance_contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_main_py ~~~ src_zephyr_gov_drift_analysis_py
    src_zephyr_gov_drift_analysis_py ~~~ src_zephyr_gov_drift_core_py
    src_zephyr_gov_drift_core_py ~~~ src_zephyr_gov_drift_drift_py
    src_zephyr_gov_drift_drift_py ~~~ src_zephyr_gov_drift_infrastructure_py
    src_zephyr_gov_drift_infrastructure_py ~~~ src_zephyr_gov_drift_scanners_py
    src_zephyr_gov_drift_scanners_py ~~~ src_zephyr_governance_agent_rbac_contracts_py
    src_zephyr_governance_agent_rbac_contracts_py ~~~ src_zephyr_red_blue_validator_init_py
    src_zephyr_red_blue_validator_init_py ~~~ src_zephyr_security_access_control_adversarial_resilience_py
    src_zephyr_security_access_control_adversarial_resilience_py ~~~ src_zephyr_security_access_control_agent_creation_policy_py
    src_zephyr_security_access_control_agent_creation_policy_py ~~~ src_zephyr_security_access_control_asymmetric_audit_py
    src_zephyr_security_access_control_asymmetric_audit_py ~~~ src_zephyr_security_access_control_auto_maintenance_py
    src_zephyr_security_access_control_auto_maintenance_py ~~~ src_zephyr_security_access_control_blueprint_fidelity_py
    src_zephyr_security_access_control_blueprint_fidelity_py ~~~ src_zephyr_security_access_control_build_sanitizer_py
    src_zephyr_security_access_control_build_sanitizer_py ~~~ src_zephyr_security_access_control_cache_invalidation_py
    src_zephyr_security_access_control_cache_invalidation_py ~~~ src_zephyr_security_access_control_canary_rollout_manager_py
    src_zephyr_security_access_control_canary_rollout_manager_py ~~~ src_zephyr_security_access_control_cascading_failure_isolator_py
    src_zephyr_security_access_control_cascading_failure_isolator_py ~~~ src_zephyr_security_access_control_compliance_matrix_py
    src_zephyr_security_access_control_compliance_matrix_py ~~~ src_zephyr_security_access_control_cross_cutting_py
    src_zephyr_security_access_control_cross_cutting_py ~~~ src_zephyr_security_access_control_decision_explainer_py
    src_zephyr_security_access_control_decision_explainer_py ~~~ src_zephyr_security_access_control_decision_registry_py
    src_zephyr_security_access_control_decision_registry_py ~~~ src_zephyr_security_access_control_defense_depth_py
    src_zephyr_security_access_control_defense_depth_py ~~~ src_zephyr_security_access_control_dependency_auditor_py
    src_zephyr_security_access_control_dependency_auditor_py ~~~ src_zephyr_security_access_control_derive_rbac_roles_py
    src_zephyr_security_access_control_derive_rbac_roles_py ~~~ src_zephyr_security_access_control_detectors_anomaly_detector_py
    src_zephyr_security_access_control_detectors_anomaly_detector_py ~~~ src_zephyr_security_access_control_detectors_context_drift_detector_py
    src_zephyr_security_access_control_detectors_context_drift_detector_py ~~~ src_zephyr_security_access_control_detectors_cross_session_detector_py
    src_zephyr_security_access_control_detectors_cross_session_detector_py ~~~ src_zephyr_security_access_control_detectors_false_completion_detector_py
    src_zephyr_security_access_control_detectors_false_completion_detector_py ~~~ src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py
    src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py ~~~ src_zephyr_security_access_control_detectors_shell_dialect_detector_py
    src_zephyr_security_access_control_detectors_shell_dialect_detector_py ~~~ src_zephyr_security_access_control_dry_run_py
    src_zephyr_security_access_control_dry_run_py ~~~ src_zephyr_security_access_control_emergency_override_py
    src_zephyr_security_access_control_emergency_override_py ~~~ src_zephyr_security_access_control_environment_manager_py
    src_zephyr_security_access_control_environment_manager_py ~~~ src_zephyr_security_access_control_escalation_handler_py
    src_zephyr_security_access_control_escalation_handler_py ~~~ src_zephyr_security_access_control_exceptions_py
    src_zephyr_security_access_control_exceptions_py ~~~ src_zephyr_security_access_control_genesis_bootstrap_py
    src_zephyr_security_access_control_genesis_bootstrap_py ~~~ src_zephyr_security_access_control_guard_layers_py
    src_zephyr_security_access_control_guard_layers_py ~~~ src_zephyr_security_access_control_guards_abac_guard_py
    src_zephyr_security_access_control_guards_abac_guard_py ~~~ src_zephyr_security_access_control_guards_anti_pattern_guard_py
    src_zephyr_security_access_control_guards_anti_pattern_guard_py ~~~ src_zephyr_security_access_control_guards_audit_log_guard_py
    src_zephyr_security_access_control_guards_audit_log_guard_py ~~~ src_zephyr_security_access_control_guards_cybersec_2026_guard_py
    src_zephyr_security_access_control_guards_cybersec_2026_guard_py ~~~ src_zephyr_security_access_control_guards_input_guard_py
    src_zephyr_security_access_control_guards_input_guard_py ~~~ src_zephyr_security_access_control_guards_memory_guard_py
    src_zephyr_security_access_control_guards_memory_guard_py ~~~ src_zephyr_security_access_control_guards_memory_provenance_guard_py
    src_zephyr_security_access_control_guards_memory_provenance_guard_py ~~~ src_zephyr_security_access_control_guards_native_api_guard_py
    src_zephyr_security_access_control_guards_native_api_guard_py ~~~ src_zephyr_security_access_control_guards_novel_attack_guard_py
    src_zephyr_security_access_control_guards_novel_attack_guard_py ~~~ src_zephyr_security_access_control_guards_output_guard_py
    src_zephyr_security_access_control_guards_output_guard_py ~~~ src_zephyr_security_access_control_guards_path_guard_py
    src_zephyr_security_access_control_guards_path_guard_py ~~~ src_zephyr_security_access_control_guards_replay_attack_guard_py
    src_zephyr_security_access_control_guards_replay_attack_guard_py ~~~ src_zephyr_security_access_control_guards_rule_injection_guard_py
    src_zephyr_security_access_control_guards_rule_injection_guard_py ~~~ src_zephyr_security_access_control_guards_sequence_guard_py
    src_zephyr_security_access_control_guards_sequence_guard_py ~~~ src_zephyr_security_access_control_guards_toctou_guard_py
    src_zephyr_security_access_control_guards_toctou_guard_py ~~~ src_zephyr_security_access_control_guards_vibe_coding_guard_py
    src_zephyr_security_access_control_guards_vibe_coding_guard_py ~~~ src_zephyr_security_access_control_integration_py
    src_zephyr_security_access_control_integration_py ~~~ src_zephyr_security_access_control_integrity_self_check_py
    src_zephyr_security_access_control_integrity_self_check_py ~~~ src_zephyr_security_access_control_intent_binder_py
    src_zephyr_security_access_control_intent_binder_py ~~~ src_zephyr_security_access_control_key_hierarchy_py
    src_zephyr_security_access_control_key_hierarchy_py ~~~ src_zephyr_security_access_control_legal_audit_chain_py
    src_zephyr_security_access_control_legal_audit_chain_py ~~~ src_zephyr_security_access_control_microstructure_defense_py
    src_zephyr_security_access_control_microstructure_defense_py ~~~ src_zephyr_security_access_control_monotonic_clock_py
    src_zephyr_security_access_control_monotonic_clock_py ~~~ src_zephyr_security_access_control_non_repudiation_py
    src_zephyr_security_access_control_non_repudiation_py ~~~ src_zephyr_security_access_control_observability_py
    src_zephyr_security_access_control_observability_py ~~~ src_zephyr_security_access_control_orphan_judge_main_py
    src_zephyr_security_access_control_orphan_judge_main_py ~~~ src_zephyr_security_access_control_orphan_judge_config_loader_py
    src_zephyr_security_access_control_orphan_judge_config_loader_py ~~~ src_zephyr_security_access_control_orphan_judge_drift_bridge_py
    src_zephyr_security_access_control_orphan_judge_drift_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_escalation_bridge_py
    src_zephyr_security_access_control_orphan_judge_escalation_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_feedback_bridge_py
    src_zephyr_security_access_control_orphan_judge_feedback_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_kb_bridge_py
    src_zephyr_security_access_control_orphan_judge_kb_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_mcp_integration_py
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py ~~~ src_zephyr_security_access_control_orphan_judge_orphan_collector_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py ~~~ src_zephyr_security_access_control_orphan_judge_orphan_detector_py
    src_zephyr_security_access_control_orphan_judge_orphan_detector_py ~~~ src_zephyr_security_access_control_orphan_judge_rbac_bridge_py
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py ~~~ src_zephyr_security_access_control_orphan_judge_registration_checker_py
    src_zephyr_security_access_control_orphan_judge_registration_checker_py ~~~ src_zephyr_security_access_control_orphan_judge_report_generator_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py ~~~ src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py ~~~ src_zephyr_security_access_control_orphan_judge_swid_tag_py
    src_zephyr_security_access_control_orphan_judge_swid_tag_py ~~~ src_zephyr_security_access_control_orphan_judge_unique_analyzer_py
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py ~~~ src_zephyr_security_access_control_permission_hooks_py
    src_zephyr_security_access_control_permission_hooks_py ~~~ src_zephyr_security_access_control_permission_mode_manager_py
    src_zephyr_security_access_control_permission_mode_manager_py ~~~ src_zephyr_security_access_control_phase_executor_py
    src_zephyr_security_access_control_phase_executor_py ~~~ src_zephyr_security_access_control_risk_mitigation_py
    src_zephyr_security_access_control_risk_mitigation_py ~~~ src_zephyr_security_access_control_rollback_sandbox_py
    src_zephyr_security_access_control_rollback_sandbox_py ~~~ src_zephyr_security_access_control_secrets_lifecycle_py
    src_zephyr_security_access_control_secrets_lifecycle_py ~~~ src_zephyr_security_access_control_session_concurrency_py
    src_zephyr_security_access_control_session_concurrency_py ~~~ src_zephyr_security_access_control_session_lifecycle_py
    src_zephyr_security_access_control_session_lifecycle_py ~~~ src_zephyr_security_access_control_verifiers_bootstrap_verifier_py
    src_zephyr_security_access_control_verifiers_bootstrap_verifier_py ~~~ src_zephyr_security_access_control_verifiers_continuous_verifier_py
    src_zephyr_security_access_control_verifiers_continuous_verifier_py ~~~ src_zephyr_security_access_control_verifiers_contract_verifier_py
    src_zephyr_security_access_control_verifiers_contract_verifier_py ~~~ src_zephyr_security_access_control_verifiers_micro_verifier_py
    src_zephyr_security_access_control_verifiers_micro_verifier_py ~~~ src_zephyr_security_access_control_verifiers_post_action_verifier_py
    src_zephyr_security_access_control_verifiers_post_action_verifier_py ~~~ src_zephyr_security_adversarial_validation_main_py
    src_zephyr_security_adversarial_validation_main_py ~~~ src_zephyr_security_adversarial_validation_ai_attack_generator_py
    src_zephyr_security_adversarial_validation_ai_attack_generator_py ~~~ src_zephyr_security_adversarial_validation_async_monitor_py
    src_zephyr_security_adversarial_validation_async_monitor_py ~~~ src_zephyr_security_adversarial_validation_attack_registry_py
    src_zephyr_security_adversarial_validation_attack_registry_py ~~~ src_zephyr_security_adversarial_validation_commit_trigger_py
    src_zephyr_security_adversarial_validation_commit_trigger_py ~~~ src_zephyr_security_adversarial_validation_constitution_engine_py
    src_zephyr_security_adversarial_validation_constitution_engine_py ~~~ src_zephyr_security_adversarial_validation_game_day_scheduler_py
    src_zephyr_security_adversarial_validation_game_day_scheduler_py ~~~ src_zephyr_security_adversarial_validation_injection_engine_py
    src_zephyr_security_adversarial_validation_injection_engine_py ~~~ src_zephyr_security_adversarial_validation_mcp_endpoints_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py ~~~ src_zephyr_security_adversarial_validation_validator_event_bridge_py
    src_zephyr_security_adversarial_validation_validator_event_bridge_py ~~~ src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py ~~~ src_zephyr_security_llm_defense_llm_security_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py ~~~ tests_governance_security_test_governance_a2a_check_py
    tests_governance_security_test_governance_a2a_check_py ~~~ tests_governance_security_test_governance_approver_check_py
    tests_governance_security_test_governance_approver_check_py ~~~ tests_governance_security_test_governance_bootstrap_superadmin_py
    tests_governance_security_test_governance_bootstrap_superadmin_py ~~~ tests_governance_security_test_governance_capability_check_py
    tests_governance_security_test_governance_capability_check_py ~~~ tests_governance_security_test_governance_contracts_py
    src_zephyr_gov_drift_alert_router_py["Alert路由器<br/>Alert Router — alert_router.py<br/>文件: gov_drift/alert_router.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_cold_start_py["冷启动<br/>Cold Start Bootstrapper — 冷启动引导 §6.31。<br/>文件: gov_drift/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_events_py["ManagedDriftEvent Pydantic V2 BaseModel<br/>漂移事件定义.<br/>G-CT-005 — ManagedDriftEvent Pydantic V2<br/>BaseModel 漂移事件定义.<br/>Events<br/>文件: gov_drift/events.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_reconciler_py["对账器<br/>Auto Reconciler — reconciler.py<br/>文件: gov_drift/reconciler.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_runbook_generator_py["构造 YAML frontmatter<br/>Drift Runbook Generator — 漂移演练手册自动生成。<br/>文件: gov_drift/runbook_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_state_machine_py["状态Machine<br/>Drift State Machine — state_machine.py<br/>文件: gov_drift/state_machine.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_a2a_check_py["—校验两个 agent 之间是否允许通信<br/>A2A 通信对验证——校验两个 agent<br/>之间是否允许通信。<br/>A2a Check<br/>文件: access_control/a2a_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_approver_check_py["校验审批人是否有权执行请求的动作<br/>Approver authorization verifier —<br/>校验审批人是否有权执行请求的动作。<br/>Approver Check<br/>文件: access_control/approver_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_bootstrap_superadmin_py["Superadmin 账户启动器.<br/>BootstrapSuperadmin — Superadmin 账户启动器.<br/>Bootstrap Superadmin<br/>文件: access_control/bootstrap_superadmin.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_capability_check_py["拒绝受限能力声明、空能力声明及能力数量超限<br/>Agent capability scope verification —<br/>拒绝受限能力声明、空能力声明及能力数量...<br/>Capability Check<br/>文件: access_control/capability_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cold_start_lock_py["冷启动锁.<br/>ColdStartLock — 冷启动锁.<br/>Cold Start Lock<br/>文件: access_control/cold_start_lock.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_contracts_py["G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge.<br/>安全/access control包的contracts模块<br/>文件: access_control/contracts.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_engine_degradation_py["引擎降级管理.<br/>EngineDegradation — 引擎降级管理.<br/>Engine Degradation<br/>文件: access_control/engine_degradation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_permission_guard_py["七层权限编排器.<br/>PermissionGuard — 七层权限编排器.<br/>Permission Guard<br/>文件: guards/permission_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_kill_switch_py["熔断器.<br/>KillSwitch — 熔断器.<br/>Kill Switch<br/>文件: access_control/kill_switch.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py["—分析删除文件对项目的影响<br/>安全/orphan judge包的cascade_analyzer模块<br/>Cascade Analyzer<br/>文件: orphan_judge/cascade_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_db_py["数据库<br/>安全/orphan judge包的db模块<br/>文件: orphan_judge/db.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_decision_table_py["五层判定结果 -> 处置动作映射表<br/>安全/orphan judge包的decision_table模块<br/>Decision Table<br/>文件: orphan_judge/decision_table.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py["—标记和追踪废弃文件的生命周期<br/>安全/orphan judge包的deprecation_tracker模块<br/>Deprecation Tracker<br/>文件: orphan_judge/deprecation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_safety_fence_py["—阻止删除 frozen/immutable_core 文件<br/>安全/orphan judge包的safety_fence模块<br/>Safety Fence<br/>文件: orphan_judge/safety_fence.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_circuit_breaker_py["写入：state<br/>安全/adversarial<br/>validation包的circuit_breaker模块<br/>Circuit Breaker<br/>文件: adversarial_validation/circuit_breaker.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cli_py["对抗验证CLI<br/>安全/adversarial validation包的cli模块<br/>文件: adversarial_validation/cli.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_constitution_guard_py["Constitution守卫<br/>安全/adversarial<br/>validation包的constitution_guard模块<br/>Constitution Guard<br/>文件: adversarial_validation<br/>/constitution_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_convergence_checker_py["Convergence检查器<br/>安全/adversarial<br/>validation包的convergence_checker模块<br/>Convergence Checker<br/>文件: adversarial_validation<br/>/convergence_checker.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py["行为审计日志器<br/>安全/llm security包的behavior_audit_logger模块<br/>Behavior Audit Logger<br/>文件: llm_security/behavior_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_gateway_py["网关<br/>安全/llm security包的gateway模块<br/>文件: llm_security/gateway.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_input_sanitizer_py["输入净化器<br/>InputSanitizer: path whitelist + command<br/>whitelist + token budget guard.<br/>Input Sanitizer<br/>文件: llm_security/input_sanitizer.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py["注入Patterns<br/>安全/patterns包的injection_patterns模块<br/>Injection Patterns<br/>文件: patterns/injection_patterns.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py["密钥模式<br/>安全/patterns包的secrets模块<br/>文件: patterns/secrets.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py["LSG 自身隔离策略.<br/>安全/self protection包的isolation模块<br/>文件: self_protection/isolation.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_alert_router_py ~~~ src_zephyr_gov_drift_cold_start_py
    src_zephyr_gov_drift_cold_start_py ~~~ src_zephyr_gov_drift_events_py
    src_zephyr_gov_drift_events_py ~~~ src_zephyr_gov_drift_reconciler_py
    src_zephyr_gov_drift_reconciler_py ~~~ src_zephyr_gov_drift_runbook_generator_py
    src_zephyr_gov_drift_runbook_generator_py ~~~ src_zephyr_gov_drift_state_machine_py
    src_zephyr_gov_drift_state_machine_py ~~~ src_zephyr_security_access_control_a2a_check_py
    src_zephyr_security_access_control_a2a_check_py ~~~ src_zephyr_security_access_control_approver_check_py
    src_zephyr_security_access_control_approver_check_py ~~~ src_zephyr_security_access_control_bootstrap_superadmin_py
    src_zephyr_security_access_control_bootstrap_superadmin_py ~~~ src_zephyr_security_access_control_capability_check_py
    src_zephyr_security_access_control_capability_check_py ~~~ src_zephyr_security_access_control_cold_start_lock_py
    src_zephyr_security_access_control_cold_start_lock_py ~~~ src_zephyr_security_access_control_contracts_py
    src_zephyr_security_access_control_contracts_py ~~~ src_zephyr_security_access_control_engine_degradation_py
    src_zephyr_security_access_control_engine_degradation_py ~~~ src_zephyr_security_access_control_guards_permission_guard_py
    src_zephyr_security_access_control_guards_permission_guard_py ~~~ src_zephyr_security_access_control_kill_switch_py
    src_zephyr_security_access_control_kill_switch_py ~~~ src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py
    src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py ~~~ src_zephyr_security_access_control_orphan_judge_db_py
    src_zephyr_security_access_control_orphan_judge_db_py ~~~ src_zephyr_security_access_control_orphan_judge_decision_table_py
    src_zephyr_security_access_control_orphan_judge_decision_table_py ~~~ src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py
    src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py ~~~ src_zephyr_security_access_control_orphan_judge_safety_fence_py
    src_zephyr_security_access_control_orphan_judge_safety_fence_py ~~~ src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_circuit_breaker_py ~~~ src_zephyr_security_adversarial_validation_cli_py
    src_zephyr_security_adversarial_validation_cli_py ~~~ src_zephyr_security_adversarial_validation_constitution_guard_py
    src_zephyr_security_adversarial_validation_constitution_guard_py ~~~ src_zephyr_security_adversarial_validation_convergence_checker_py
    src_zephyr_security_adversarial_validation_convergence_checker_py ~~~ src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py ~~~ src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_gateway_py ~~~ src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_input_sanitizer_py ~~~ src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py
    src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py ~~~ src_zephyr_security_llm_defense_llm_security_patterns_secrets_py
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    src_zephyr_security_access_control_guards_rbac_guard_py["基于角色的权限守卫.<br/>RBACGuard — 基于角色的权限守卫.<br/>Rbac Guard<br/>文件: guards/rbac_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_models_py["模型<br/>安全/orphan judge包的models模块<br/>文件: orphan_judge/models.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cold_start_py["冷启动<br/>安全/adversarial validation包的cold_start模块<br/>Cold Start<br/>文件: adversarial_validation/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_game_day_runner_py["GameDay运行器<br/>安全/adversarial<br/>validation包的game_day_runner模块<br/>Game Day Runner<br/>文件: adversarial_validation/game_day_runner.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py["L0Supply链<br/>安全/layers包的l0_supply_chain模块<br/>L0 Supply Chain<br/>文件: layers/l0_supply_chain.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py["输入来源类型<br/>安全/layers包的l1_input模块<br/>L1 Input<br/>文件: layers/l1_input.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py["prompt 泄露扫描结果<br/>安全/layers包的l2_prompt_protection模块<br/>L2 Prompt Protection<br/>文件: layers/l2_prompt_protection.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py["L2a流程Sandbox<br/>安全/layers包的l2a_process_sandbox模块<br/>L2a Process Sandbox<br/>文件: layers/l2a_process_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py["兼容旧接口的输出过滤层<br/>安全/layers包的l3_output模块<br/>L3 Output<br/>文件: layers/l3_output.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py["解析 L4 HMAC 密钥<br/>安全/layers包的l4_agent模块<br/>L4 Agent<br/>文件: layers/l4_agent.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py["L5 资源保护层：token/cost/rate 限额 +<br/>成本不对称检测<br/>安全/layers包的l5_resource_protection模块<br/>L5 Resource Protection<br/>文件: layers/l5_resource_protection.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py["L6可观测性<br/>L6 Observability Layer — security event<br/>logging, alerting, and reporting.<br/>文件: layers/l6_observability.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py["L8多代理<br/>安全/layers包的l8_multi_agent模块<br/>L8 Multi Agent<br/>文件: layers/l8_multi_agent.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py["裸调 LLM API 被运行时拦截器阻断<br/>runtime_interceptor.py — 运行时 LLM 裸调拦截器<br/>（GATE-20 后备防线）<br/>Runtime Interceptor<br/>文件: llm_security/runtime_interceptor.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py["L7验证<br/>安全/self protection包的l7_validation模块<br/>L7 Validation<br/>文件: self_protection/l7_validation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_rbac_guard_py ~~~ src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_models_py ~~~ src_zephyr_security_adversarial_validation_cold_start_py
    src_zephyr_security_adversarial_validation_cold_start_py ~~~ src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_game_day_runner_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py ~~~ src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py
    src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_access_control_identity_py["角色与成熟度定义.<br/>Agent identity — 角色与成熟度定义.<br/>文件: access_control/identity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_immutable_core_py["不可变核心验证器.<br/>ImmutableCore — 不可变核心验证器.<br/>Immutable Core<br/>文件: access_control/immutable_core.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_judge_py["OrphanJudge 模块基础异常'''<br/>安全/orphan judge包的judge模块<br/>文件: orphan_judge/judge.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_validator_py["只读：blast<br/>安全/adversarial validation包的validator模块<br/>文件: adversarial_validation/validator.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_protocol_py["LLM Security Gateway 九层防御统一接口契约<br/>安全/llm security包的protocol模块<br/>文件: llm_security/protocol.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py["只读：last_scan_time<br/>安全/self protection包的code_integrity模块<br/>Code Integrity<br/>文件: self_protection/code_integrity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_identity_py ~~~ src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_immutable_core_py ~~~ src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_judge_py ~~~ src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_validator_py ~~~ src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_protocol_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_access_control_orphan_judge_duplicate_detector_py["—基于 AST 哈希的 Jaccard<br/>相似度检测模块间功能重叠<br/>安全/orphan judge包的duplicate_detector模块<br/>Duplicate Detector<br/>文件: orphan_judge/duplicate_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_blast_radius_py["影响半径<br/>安全/adversarial validation包的blast_radius模块<br/>Blast Radius<br/>文件: adversarial_validation/blast_radius.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_bypass_recorder_py["绕过Recorder<br/>安全/adversarial<br/>validation包的bypass_recorder模块<br/>Bypass Recorder<br/>文件: adversarial_validation/bypass_recorder.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cleanup_py["清理<br/>安全/adversarial validation包的cleanup模块<br/>文件: adversarial_validation/cleanup.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_defense_runner_py["Defense运行器<br/>安全/adversarial<br/>validation包的defense_runner模块<br/>Defense Runner<br/>文件: adversarial_validation/defense_runner.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_scenario_loader_py["场景加载器<br/>安全/adversarial<br/>validation包的scenario_loader模块<br/>Scenario Loader<br/>文件: adversarial_validation/scenario_loader.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_steady_state_py["Steady状态<br/>安全/adversarial validation包的steady_state模块<br/>Steady State<br/>文件: adversarial_validation/steady_state.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_duplicate_detector_py ~~~ src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_blast_radius_py ~~~ src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_bypass_recorder_py ~~~ src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_cleanup_py ~~~ src_zephyr_security_adversarial_validation_defense_runner_py
    src_zephyr_security_adversarial_validation_defense_runner_py ~~~ src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_scenario_loader_py ~~~ src_zephyr_security_adversarial_validation_steady_state_py
    src_zephyr_security_adversarial_validation_models_py["模型<br/>安全/adversarial validation包的models模块<br/>文件: adversarial_validation/models.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_rbac_contracts_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_contracts_py
    src_zephyr_gov_drift_core_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_events_py
    src_zephyr_gov_drift_core_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_state_machine_py
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_reconciler_py
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_runbook_generator_py
    src_zephyr_gov_drift_infrastructure_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_alert_router_py
    src_zephyr_gov_drift_infrastructure_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_cold_start_py
    src_zephyr_red_blue_validator_init_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_constitution_guard_py
    src_zephyr_red_blue_validator_init_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_access_control_cold_start_lock_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_derive_rbac_roles_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_bootstrap_superadmin_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_cold_start_lock_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_engine_degradation_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_kill_switch_py
    src_zephyr_security_access_control_guards_abac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_rbac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_rbac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_guards_rbac_guard_py
    src_zephyr_security_access_control_orphan_judge_config_loader_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_db_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_judge_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_duplicate_detector_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_decision_table_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_safety_fence_py
    src_zephyr_security_access_control_orphan_judge_models_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_registration_checker_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_db_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_swid_tag_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_guards_permission_guard_py
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_main_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_bypass_recorder_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_circuit_breaker_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_blast_radius_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_convergence_checker_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cold_start_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_constitution_engine_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_constitution_guard_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_defense_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_injection_engine_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_convergence_checker_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_game_day_scheduler_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_scenario_loader_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_steady_state_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_main_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cli_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_defense_runner_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_steady_state_py
    src_zephyr_security_adversarial_validation_validator_event_bridge_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_secrets_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    tests_governance_security_test_governance_approver_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_approver_check_py
    tests_governance_security_test_governance_a2a_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_a2a_check_py
    tests_governance_security_test_governance_contracts_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_contracts_py
    tests_governance_security_test_governance_capability_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_capability_check_py
    tests_governance_security_test_governance_bootstrap_superadmin_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_bootstrap_superadmin_py
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_drift_infrastructure_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_drift_reconciler_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_drift_scanners_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_drift_core_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_security_access_control_orphan_judge_report_generator_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_security_access_control_contracts_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_security_access_control_immutable_core_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_security_access_control_genesis_bootstrap_py
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_RISK -->|导入依赖 / import_depends| src_zephyr_security_access_control_kill_switch_py
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_GOV_ENFORCEMENT -.->|导入依赖 / import_depends| src_zephyr_security_access_control_canary_rollout_manager_py
    D_ORCHESTRATOR["代理编排器<br/>代理编排器，负责 Agent<br/>任务全生命周期：任务入队、调度、沙箱执行、幻觉检<br/>测和收尾归档<br/>Agent Orchestrator<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_security_access_control_non_repudiation_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_security_access_control_capability_check_py
    D_GOV_CODE_QUALITY["代码质量治理<br/>代码质量治理，负责代码去重引擎、函数重复检测、AS<br/>T语义分析和提交门禁引擎<br/>Code Quality Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_security_access_control_session_concurrency_py
    D_INFRA_RECOVERY["回滚恢复<br/>回滚恢复，负责系统故障时的状态回滚、事务补偿和恢<br/>复编排<br/>Rollback Recovery<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RECOVERY -->|导入依赖 / import_depends| src_zephyr_gov_drift_runbook_generator_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_security_access_control_approver_check_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_gov_drift_events_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_gov_drift_events_py
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_security_access_control_session_concurrency_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_security_access_control_a2a_check_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_security_access_control_session_concurrency_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_drift_main_py,src_zephyr_gov_drift_analysis_py,src_zephyr_gov_drift_core_py,src_zephyr_gov_drift_drift_py,src_zephyr_gov_drift_infrastructure_py,src_zephyr_gov_drift_scanners_py,src_zephyr_gov_drift_alert_router_py,src_zephyr_gov_drift_cold_start_py,src_zephyr_gov_drift_events_py,src_zephyr_gov_drift_reconciler_py,src_zephyr_gov_drift_runbook_generator_py,src_zephyr_gov_drift_state_machine_py,src_zephyr_governance_agent_rbac_contracts_py,src_zephyr_red_blue_validator_init_py,src_zephyr_security_access_control_a2a_check_py,src_zephyr_security_access_control_adversarial_resilience_py,src_zephyr_security_access_control_agent_creation_policy_py,src_zephyr_security_access_control_approver_check_py,src_zephyr_security_access_control_asymmetric_audit_py,src_zephyr_security_access_control_auto_maintenance_py,src_zephyr_security_access_control_blueprint_fidelity_py,src_zephyr_security_access_control_bootstrap_superadmin_py,src_zephyr_security_access_control_build_sanitizer_py,src_zephyr_security_access_control_cache_invalidation_py,src_zephyr_security_access_control_canary_rollout_manager_py,src_zephyr_security_access_control_capability_check_py,src_zephyr_security_access_control_cascading_failure_isolator_py,src_zephyr_security_access_control_cold_start_lock_py,src_zephyr_security_access_control_compliance_matrix_py,src_zephyr_security_access_control_contracts_py,src_zephyr_security_access_control_cross_cutting_py,src_zephyr_security_access_control_decision_explainer_py,src_zephyr_security_access_control_decision_registry_py,src_zephyr_security_access_control_defense_depth_py,src_zephyr_security_access_control_dependency_auditor_py,src_zephyr_security_access_control_derive_rbac_roles_py,src_zephyr_security_access_control_detectors_anomaly_detector_py,src_zephyr_security_access_control_detectors_context_drift_detector_py,src_zephyr_security_access_control_detectors_cross_session_detector_py,src_zephyr_security_access_control_detectors_false_completion_detector_py,src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py,src_zephyr_security_access_control_detectors_shell_dialect_detector_py,src_zephyr_security_access_control_dry_run_py,src_zephyr_security_access_control_emergency_override_py,src_zephyr_security_access_control_engine_degradation_py,src_zephyr_security_access_control_environment_manager_py,src_zephyr_security_access_control_escalation_handler_py,src_zephyr_security_access_control_exceptions_py,src_zephyr_security_access_control_genesis_bootstrap_py,src_zephyr_security_access_control_guard_layers_py,src_zephyr_security_access_control_guards_abac_guard_py,src_zephyr_security_access_control_guards_anti_pattern_guard_py,src_zephyr_security_access_control_guards_audit_log_guard_py,src_zephyr_security_access_control_guards_cybersec_2026_guard_py,src_zephyr_security_access_control_guards_input_guard_py,src_zephyr_security_access_control_guards_memory_guard_py,src_zephyr_security_access_control_guards_memory_provenance_guard_py,src_zephyr_security_access_control_guards_native_api_guard_py,src_zephyr_security_access_control_guards_novel_attack_guard_py,src_zephyr_security_access_control_guards_output_guard_py,src_zephyr_security_access_control_guards_path_guard_py,src_zephyr_security_access_control_guards_permission_guard_py,src_zephyr_security_access_control_guards_rbac_guard_py,src_zephyr_security_access_control_guards_replay_attack_guard_py,src_zephyr_security_access_control_guards_rule_injection_guard_py,src_zephyr_security_access_control_guards_sequence_guard_py,src_zephyr_security_access_control_guards_toctou_guard_py,src_zephyr_security_access_control_guards_vibe_coding_guard_py,src_zephyr_security_access_control_identity_py,src_zephyr_security_access_control_immutable_core_py,src_zephyr_security_access_control_integration_py,src_zephyr_security_access_control_integrity_self_check_py,src_zephyr_security_access_control_intent_binder_py,src_zephyr_security_access_control_key_hierarchy_py,src_zephyr_security_access_control_kill_switch_py,src_zephyr_security_access_control_legal_audit_chain_py,src_zephyr_security_access_control_microstructure_defense_py,src_zephyr_security_access_control_monotonic_clock_py,src_zephyr_security_access_control_non_repudiation_py,src_zephyr_security_access_control_observability_py,src_zephyr_security_access_control_orphan_judge_main_py,src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py,src_zephyr_security_access_control_orphan_judge_config_loader_py,src_zephyr_security_access_control_orphan_judge_db_py,src_zephyr_security_access_control_orphan_judge_decision_table_py,src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py,src_zephyr_security_access_control_orphan_judge_drift_bridge_py,src_zephyr_security_access_control_orphan_judge_duplicate_detector_py,src_zephyr_security_access_control_orphan_judge_escalation_bridge_py,src_zephyr_security_access_control_orphan_judge_feedback_bridge_py,src_zephyr_security_access_control_orphan_judge_judge_py,src_zephyr_security_access_control_orphan_judge_kb_bridge_py,src_zephyr_security_access_control_orphan_judge_mcp_integration_py,src_zephyr_security_access_control_orphan_judge_models_py,src_zephyr_security_access_control_orphan_judge_orphan_collector_py,src_zephyr_security_access_control_orphan_judge_orphan_detector_py,src_zephyr_security_access_control_orphan_judge_rbac_bridge_py,src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py,src_zephyr_security_access_control_orphan_judge_registration_checker_py,src_zephyr_security_access_control_orphan_judge_report_generator_py,src_zephyr_security_access_control_orphan_judge_safety_fence_py,src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py,src_zephyr_security_access_control_orphan_judge_swid_tag_py,src_zephyr_security_access_control_orphan_judge_unique_analyzer_py,src_zephyr_security_access_control_permission_hooks_py,src_zephyr_security_access_control_permission_mode_manager_py,src_zephyr_security_access_control_phase_executor_py,src_zephyr_security_access_control_risk_mitigation_py,src_zephyr_security_access_control_rollback_sandbox_py,src_zephyr_security_access_control_secrets_lifecycle_py,src_zephyr_security_access_control_session_concurrency_py,src_zephyr_security_access_control_session_lifecycle_py,src_zephyr_security_access_control_verifiers_bootstrap_verifier_py,src_zephyr_security_access_control_verifiers_continuous_verifier_py,src_zephyr_security_access_control_verifiers_contract_verifier_py,src_zephyr_security_access_control_verifiers_micro_verifier_py,src_zephyr_security_access_control_verifiers_post_action_verifier_py,src_zephyr_security_adversarial_validation_main_py,src_zephyr_security_adversarial_validation_ai_attack_generator_py,src_zephyr_security_adversarial_validation_async_monitor_py,src_zephyr_security_adversarial_validation_attack_registry_py,src_zephyr_security_adversarial_validation_blast_radius_py,src_zephyr_security_adversarial_validation_bypass_recorder_py,src_zephyr_security_adversarial_validation_circuit_breaker_py,src_zephyr_security_adversarial_validation_cleanup_py,src_zephyr_security_adversarial_validation_cli_py,src_zephyr_security_adversarial_validation_cold_start_py,src_zephyr_security_adversarial_validation_commit_trigger_py,src_zephyr_security_adversarial_validation_constitution_engine_py,src_zephyr_security_adversarial_validation_constitution_guard_py,src_zephyr_security_adversarial_validation_convergence_checker_py,src_zephyr_security_adversarial_validation_defense_runner_py,src_zephyr_security_adversarial_validation_game_day_runner_py,src_zephyr_security_adversarial_validation_game_day_scheduler_py,src_zephyr_security_adversarial_validation_injection_engine_py,src_zephyr_security_adversarial_validation_mcp_endpoints_py,src_zephyr_security_adversarial_validation_models_py,src_zephyr_security_adversarial_validation_scenario_loader_py,src_zephyr_security_adversarial_validation_steady_state_py,src_zephyr_security_adversarial_validation_validator_py,src_zephyr_security_adversarial_validation_validator_event_bridge_py,src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py,src_zephyr_security_llm_defense_llm_security_dashboard_app_py,src_zephyr_security_llm_defense_llm_security_gateway_py,src_zephyr_security_llm_defense_llm_security_input_sanitizer_py,src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py,src_zephyr_security_llm_defense_llm_security_layers_l1_input_py,src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_layers_l3_output_py,src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py,src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py,src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py,src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py,src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py,src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py,src_zephyr_security_llm_defense_llm_security_patterns_secrets_py,src_zephyr_security_llm_defense_llm_security_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_protocol_py,src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py,src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py,src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py,src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py,src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py,src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py,tests_governance_security_test_governance_a2a_check_py,tests_governance_security_test_governance_approver_check_py,tests_governance_security_test_governance_bootstrap_superadmin_py,tests_governance_security_test_governance_capability_check_py,tests_governance_security_test_governance_contracts_py production
    class D_GOV_DRIFT,D_SHARED,D_INFRA_RUNTIME,D_GOV_AUDIT,D_RISK,D_ORCHESTRATOR,D_GOVERNANCE,D_GOV_CODE_QUALITY,D_INFRA_RECOVERY,D_AUTONOMY_CORE external_prod
    class D_GOV_ENFORCEMENT external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 171 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_drift_main_py["主入口<br/>Drift Detector MOD-INF-023 CLI — 漂移扫描入口。<br/>Main<br/>文件: gov_drift/__main__.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_analysis_py["分析<br/>gov drift包的analysis模块<br/>文件: gov_drift/_analysis.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_core_py["核心<br/>gov drift包的core模块<br/>文件: gov_drift/_core.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_drift_py["漂移<br/>gov drift包的drift模块<br/>文件: gov_drift/_drift.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_infrastructure_py["基础设施<br/>gov drift包的infrastructure模块<br/>文件: gov_drift/_infrastructure.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_scanners_py["扫描器<br/>gov drift包的scanners模块<br/>文件: gov_drift/_scanners.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_rbac_contracts_py["G-CT-001 RBAC 契约<br/>agent-rbac/contracts.py — G-CT-001 RBAC 契约<br/>（re-export）。<br/>文件: agent-rbac/contracts.py<br/>(生产态 / production)"]
    src_zephyr_red_blue_validator_init_py["zephyr/red_blue_validator 包入口<br/>red_blue_validator — re-export shim for<br/>zephyr.security.adversarial_validation.<br/>Init<br/>文件: red_blue_validator/__init__.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_adversarial_resilience_py["对抗Resilience<br/>AdversarialResilience - adversarial resilience<br/>& OWASP coverage.<br/>文件: access_control/adversarial_resilience.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_agent_creation_policy_py["Agent 创建策略.<br/>AgentCreationPolicy — Agent 创建策略.<br/>Agent Creation Policy<br/>文件: access_control/agent_creation_policy.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_asymmetric_audit_py["Asymmetric审计<br/>AsymmetricAudit - quorum-based approval for<br/>high-risk operations.<br/>Asymmetric Audit<br/>文件: access_control/asymmetric_audit.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_auto_maintenance_py["自动维护与规则健康仪表盘.<br/>AutoMaintenance — 自动维护与规则健康仪表盘.<br/>Auto Maintenance<br/>文件: access_control/auto_maintenance.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_blueprint_fidelity_py["蓝图保真度检查.<br/>BlueprintFidelity — 蓝图保真度检查.<br/>Blueprint Fidelity<br/>文件: access_control/blueprint_fidelity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_build_sanitizer_py["zephyr.security.access_control.build_sanitizer<br/>— implementation pending.'''<br/>安全/access control包的build_sanitizer模块<br/>Build Sanitizer<br/>文件: access_control/build_sanitizer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cache_invalidation_py["缓存失效事件管理.<br/>CacheInvalidation — 缓存失效事件管理.<br/>Cache Invalidation<br/>文件: access_control/cache_invalidation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_canary_rollout_manager_py["灰度发布管理器.<br/>CanaryRolloutManager — 灰度发布管理器.<br/>Canary Rollout Manager<br/>文件: access_control/canary_rollout_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cascading_failure_isolator_py["zephyr.security.access_control.cascading_failure<br/>_isolator — implementation pending.'''<br/>安全/access<br/>control包的cascading_failure_isolator模块<br/>Cascading Failure Isolator<br/>文件: access_control<br/>/cascading_failure_isolator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_compliance_matrix_py["合规Matrix<br/>安全/access control包的compliance_matrix模块<br/>Compliance Matrix<br/>文件: access_control/compliance_matrix.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cross_cutting_py["横切面权限组件.<br/>CrossCutting — 横切面权限组件.<br/>Cross Cutting<br/>文件: access_control/cross_cutting.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_decision_explainer_py["拒绝决策的结构化解释器.<br/>DecisionExplainer — 拒绝决策的结构化解释器.<br/>Decision Explainer<br/>文件: access_control/decision_explainer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_decision_registry_py["决策注册表<br/>DecisionRegistry - decision log with query and<br/>stats.<br/>Decision Registry<br/>文件: access_control/decision_registry.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_defense_depth_py["zephyr.security.access_control.defense_depth —<br/>implementation pending.'''<br/>安全/access control包的defense_depth模块<br/>Defense Depth<br/>文件: access_control/defense_depth.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_dependency_auditor_py["Dependency审计器<br/>安全/access control包的dependency_auditor模块<br/>Dependency Auditor<br/>文件: access_control/dependency_auditor.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_derive_rbac_roles_py["RBAC 角色派生器.<br/>RBACRoleDeriver — RBAC 角色派生器.<br/>Derive Rbac Roles<br/>文件: access_control/derive_rbac_roles.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_anomaly_detector_py["异常检测器<br/>AnomalyDetector - rolling z-score anomaly<br/>detection per field.<br/>Anomaly Detector<br/>文件: detectors/anomaly_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_context_drift_detector_py["上下文漂移与范围蔓延检测.<br/>ContextDriftDetector — 上下文漂移与范围蔓延检测.<br/>Context Drift Detector<br/>文件: detectors/context_drift_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_cross_session_detector_py["跨 Session 检测器.<br/>CrossSessionDetector — 跨 Session 检测器.<br/>Cross Session Detector<br/>文件: detectors/cross_session_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_false_completion_detector_py["虚假完成检测.<br/>FalseCompletionDetector — 虚假完成检测.<br/>False Completion Detector<br/>文件: detectors/false_completion_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py["多 agent 合谋检测.<br/>MultiAgentCollusionDetector — 多 agent 合谋检测.<br/>Multi Agent Collusion Detector<br/>文件: detectors<br/>/multi_agent_collusion_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_detectors_shell_dialect_detector_py["Shell 方言检测器.<br/>ShellDialectDetector — Shell 方言检测器.<br/>Shell Dialect Detector<br/>文件: detectors/shell_dialect_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_dry_run_py["权限模拟与影响分析.<br/>DryRun — 权限模拟与影响分析.<br/>Dry Run<br/>文件: access_control/dry_run.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_emergency_override_py["紧急覆盖令牌管理.<br/>EmergencyOverride — 紧急覆盖令牌管理.<br/>Emergency Override<br/>文件: access_control/emergency_override.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_environment_manager_py["Environment管理器<br/>安全/access control包的environment_manager模块<br/>Environment Manager<br/>文件: access_control/environment_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_escalation_handler_py["Escalation处理器<br/>安全/access control包的escalation_handler模块<br/>Escalation Handler<br/>文件: access_control/escalation_handler.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_exceptions_py["AgentRbac 异常类型.<br/>安全/access control包的exceptions模块<br/>文件: access_control/exceptions.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_genesis_bootstrap_py["RBAC系统启动引导器.<br/>GenesisBootstrap — RBAC系统启动引导器.<br/>Genesis Bootstrap<br/>文件: access_control/genesis_bootstrap.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guard_layers_py["权限守卫层组件.<br/>GuardLayers — 权限守卫层组件.<br/>Guard Layers<br/>文件: access_control/guard_layers.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_abac_guard_py["基于属性的权限守卫.<br/>ABACGuard — 基于属性的权限守卫.<br/>Abac Guard<br/>文件: guards/abac_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_anti_pattern_guard_py["反模式守卫<br/>安全/guards包的anti_pattern_guard模块<br/>Anti Pattern Guard<br/>文件: guards/anti_pattern_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_audit_log_guard_py["审计日志注入防护守卫<br/>audit_log_guard.py — 审计日志注入防护守卫<br/>Audit Log Guard<br/>文件: guards/audit_log_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_cybersec_2026_guard_py["2026 网络安全威胁检测.<br/>Cybersec2026Guard — 2026 网络安全威胁检测.<br/>Cybersec 2026 Guard<br/>文件: guards/cybersec_2026_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_input_guard_py["输入参数守卫.<br/>InputGuard — 输入参数守卫.<br/>Input Guard<br/>文件: guards/input_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_memory_guard_py["内存访问守卫.<br/>MemoryGuard — 内存访问守卫.<br/>Memory Guard<br/>文件: guards/memory_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_memory_provenance_guard_py["记忆来源溯源守卫.<br/>MemoryProvenanceGuard — 记忆来源溯源守卫.<br/>Memory Provenance Guard<br/>文件: guards/memory_provenance_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_native_api_guard_py["原生 API 守卫.<br/>NativeApiGuard — 原生 API 守卫.<br/>Native Api Guard<br/>文件: guards/native_api_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_novel_attack_guard_py["新型攻击行为画像.<br/>NovelAttackGuard — 新型攻击行为画像.<br/>Novel Attack Guard<br/>文件: guards/novel_attack_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_output_guard_py["输出内容守卫.<br/>OutputGuard — 输出内容守卫.<br/>Output Guard<br/>文件: guards/output_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_path_guard_py["路径守卫.<br/>PathGuard — 路径守卫.<br/>Path Guard<br/>文件: guards/path_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_replay_attack_guard_py["重放攻击防护.<br/>ReplayAttackGuard — 重放攻击防护.<br/>Replay Attack Guard<br/>文件: guards/replay_attack_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_rule_injection_guard_py["规则注入守卫.<br/>RuleInjectionGuard — 规则注入守卫.<br/>Rule Injection Guard<br/>文件: guards/rule_injection_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_sequence_guard_py["操作序列守卫.<br/>SequenceGuard — 操作序列守卫.<br/>Sequence Guard<br/>文件: guards/sequence_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_toctou_guard_py["Toctou守卫<br/>TOCTOUGuard — TOCTOU (Time-of-Check to<br/>Time-of-Use) 防护.<br/>Toctou Guard<br/>文件: guards/toctou_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_vibe_coding_guard_py["Vibe Coding 攻击面检测.<br/>VibeCodingGuard — Vibe Coding 攻击面检测.<br/>Vibe Coding Guard<br/>文件: guards/vibe_coding_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_integration_py["集成<br/>IntegrationManager - system integration<br/>registry & health check.<br/>文件: access_control/integration.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_integrity_self_check_py["完整性自检.<br/>IntegritySelfCheck — 完整性自检.<br/>Integrity Self Check<br/>文件: access_control/integrity_self_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_intent_binder_py["意图绑定与漂移检测.<br/>IntentBinder — 意图绑定与漂移检测.<br/>Intent Binder<br/>文件: access_control/intent_binder.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_key_hierarchy_py["zephyr.security.access_control.key_hierarchy —<br/>implementation pending.'''<br/>安全/access control包的key_hierarchy模块<br/>Key Hierarchy<br/>文件: access_control/key_hierarchy.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_legal_audit_chain_py["Legal审计链<br/>LegalAuditChain - append-only hash-chained<br/>legal audit log.<br/>Legal Audit Chain<br/>文件: access_control/legal_audit_chain.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_microstructure_defense_py["—对抗做市/交易微结构攻击的策略与保真度因子<br/>微结构防御——对抗做市<br/>/交易微结构攻击的策略与保真度因子。<br/>Microstructure Defense<br/>文件: access_control/microstructure_defense.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_monotonic_clock_py["单调时钟.<br/>MonotonicClock — 单调时钟.<br/>Monotonic Clock<br/>文件: access_control/monotonic_clock.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_non_repudiation_py["不可抵赖性审计签名.<br/>NonRepudiation — 不可抵赖性审计签名.<br/>Non Repudiation<br/>文件: access_control/non_repudiation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_observability_py["指标上报与异常检测.<br/>ObservabilityReporter — 指标上报与异常检测.<br/>文件: access_control/observability.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_main_py["主入口<br/>安全/orphan judge包的main__模块<br/>文件: orphan_judge/__main__.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_config_loader_py["配置加载器<br/>安全/orphan judge包的config_loader模块<br/>Config Loader<br/>文件: orphan_judge/config_loader.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_drift_bridge_py["漂移桥接器<br/>安全/orphan judge包的drift_bridge模块<br/>Drift Bridge<br/>文件: orphan_judge/drift_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_escalation_bridge_py["Escalation桥接器<br/>安全/orphan judge包的escalation_bridge模块<br/>Escalation Bridge<br/>文件: orphan_judge/escalation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_feedback_bridge_py["反馈桥接器<br/>安全/orphan judge包的feedback_bridge模块<br/>Feedback Bridge<br/>文件: orphan_judge/feedback_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_kb_bridge_py["Kb桥接器<br/>安全/orphan judge包的kb_bridge模块<br/>Kb Bridge<br/>文件: orphan_judge/kb_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py["MCP集成<br/>安全/orphan judge包的mcp_integration模块<br/>Mcp Integration<br/>文件: orphan_judge/mcp_integration.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py["—整合 SafetyFence 安全检查后执行处置动作<br/>安全/orphan judge包的orphan_collector模块<br/>Orphan Collector<br/>文件: orphan_judge/orphan_collector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_orphan_detector_py["孤儿检测器<br/>(INVARIANTS) 蓝图 §4 文件清单与代码双向对齐<br/>Orphan Detector<br/>文件: orphan_judge/orphan_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py["Rbac桥接器<br/>安全/orphan judge包的rbac_bridge模块<br/>Rbac Bridge<br/>文件: orphan_judge/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py["L1 引用图引擎<br/>AST解析+import链遍历，判断文件是否被其他文件引用<br/>。<br/>Reference Graph Engine<br/>文件: orphan_judge/reference_graph_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_registration_checker_py["L0 注册检查器<br/>扫描项目注册表，判断文件是否已登记在册。<br/>Registration Checker<br/>文件: orphan_judge/registration_checker.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_report_generator_py["报告生成器<br/>安全/orphan judge包的report_generator模块<br/>Report Generator<br/>文件: orphan_judge/report_generator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py["L4 独立价值评估器<br/>六指标加权评分: 文件大小(15%) + 代码行数(20%) +<br/>定义数(20%)<br/>Standalone Evaluator<br/>文件: orphan_judge/standalone_evaluator.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_swid_tag_py["SWID标签<br/>安全/orphan judge包的swid_tag模块<br/>Swid Tag<br/>文件: orphan_judge/swid_tag.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py["L3 独特价值分析器<br/>AST节点比对，检测文件中的独特代码元素(类/函数<br/>/常量定义等)。<br/>Unique Analyzer<br/>文件: orphan_judge/unique_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_permission_hooks_py["权限钩子注册表.<br/>PermissionHooks — 权限钩子注册表.<br/>Permission Hooks<br/>文件: access_control/permission_hooks.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_permission_mode_manager_py["Permission模式管理器<br/>安全/access<br/>control包的permission_mode_manager模块<br/>Permission Mode Manager<br/>文件: access_control/permission_mode_manager.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_phase_executor_py["阶段执行器<br/>安全/access control包的phase_executor模块<br/>Phase Executor<br/>文件: access_control/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_risk_mitigation_py["风险评估与缓解策略.<br/>RiskMitigation — 风险评估与缓解策略.<br/>Risk Mitigation<br/>文件: access_control/risk_mitigation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_rollback_sandbox_py["回滚Sandbox<br/>RollbackSandbox - isolate/execute/rollback<br/>pattern for reversible operations.<br/>Rollback Sandbox<br/>文件: access_control/rollback_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_secrets_lifecycle_py["Secrets生命周期<br/>安全/access control包的secrets_lifecycle模块<br/>Secrets Lifecycle<br/>文件: access_control/secrets_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_session_concurrency_py["Session 级并发协调模块<br/>（P2-SES 落地）<br/>Session Concurrency<br/>文件: access_control/session_concurrency.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_session_lifecycle_py["会话生命周期<br/>安全/access control包的session_lifecycle模块<br/>Session Lifecycle<br/>文件: access_control/session_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_bootstrap_verifier_py["Bootstrap验证器<br/>安全/verifiers包的bootstrap_verifier模块<br/>Bootstrap Verifier<br/>文件: verifiers/bootstrap_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_continuous_verifier_py["Continuous验证器<br/>安全/verifiers包的continuous_verifier模块<br/>Continuous Verifier<br/>文件: verifiers/continuous_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_contract_verifier_py["契约验证器.<br/>ContractVerifier — 契约验证器.<br/>Contract Verifier<br/>文件: verifiers/contract_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_micro_verifier_py["Micro验证器<br/>安全/verifiers包的micro_verifier模块<br/>Micro Verifier<br/>文件: verifiers/micro_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_verifiers_post_action_verifier_py["事后动作验证器<br/>安全/verifiers包的post_action_verifier模块<br/>Post Action Verifier<br/>文件: verifiers/post_action_verifier.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_main_py["主入口<br/>安全/adversarial validation包的main__模块<br/>文件: adversarial_validation/__main__.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_ai_attack_generator_py["Ai攻击生成器<br/>安全/adversarial<br/>validation包的ai_attack_generator模块<br/>Ai Attack Generator<br/>文件: adversarial_validation<br/>/ai_attack_generator.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_async_monitor_py["Async监控器<br/>安全/adversarial validation包的async_monitor模块<br/>Async Monitor<br/>文件: adversarial_validation/async_monitor.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_attack_registry_py["攻击注册表<br/>安全/adversarial<br/>validation包的attack_registry模块<br/>Attack Registry<br/>文件: adversarial_validation/attack_registry.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_commit_trigger_py["提交触发器<br/>CommitTrigger — 事件驱动红蓝对抗触发器<br/>(MOD-INF-030).<br/>Commit Trigger<br/>文件: adversarial_validation/commit_trigger.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_constitution_engine_py["Constitution引擎<br/>安全/adversarial<br/>validation包的constitution_engine模块<br/>Constitution Engine<br/>文件: adversarial_validation<br/>/constitution_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_game_day_scheduler_py["GameDay调度器<br/>安全/adversarial<br/>validation包的game_day_scheduler模块<br/>Game Day Scheduler<br/>文件: adversarial_validation<br/>/game_day_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_injection_engine_py["注入引擎<br/>安全/adversarial<br/>validation包的injection_engine模块<br/>Injection Engine<br/>文件: adversarial_validation/injection_engine.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_mcp_endpoints_py["MCP端点<br/>安全/adversarial validation包的mcp_endpoints模块<br/>Mcp Endpoints<br/>文件: adversarial_validation/mcp_endpoints.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_validator_event_bridge_py["订阅 EventBusBackpressure 的 fix_completed 事件<br/>ValidatorEventBridge — 红蓝验证器事件桥接<br/>(MOD-SEC-030).<br/>Validator Event Bridge<br/>文件: adversarial_validation<br/>/validator_event_bridge.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py["仪表盘应用<br/>LLM Security Gateway - Streamlit Dashboard.<br/>App<br/>文件: dashboard/app.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py["L6数据流<br/>安全/layers包的l6_data_flow模块<br/>L6 Data Flow<br/>文件: layers/l6_data_flow.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py["L8合规<br/>安全/layers包的l8_compliance模块<br/>L8 Compliance<br/>文件: layers/l8_compliance.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py["流程Sandbox<br/>L2a ProcessSandbox — subprocess 路径白名单沙箱<br/>Process Sandbox<br/>文件: llm_security/process_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py["对 Red Team 载荷施加 10 种变异技术，检验 LSG<br/>抗干扰能力.<br/>安全/self protection包的adversarial_mutator模块<br/>Adversarial Mutator<br/>文件: self_protection/adversarial_mutator.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py["L7 Red Team 对抗扫描器.<br/>安全/self protection包的red_team_scanner模块<br/>Red Team Scanner<br/>文件: self_protection/red_team_scanner.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_a2a_check_py["治理A2A检查测试<br/>安全包的test_governance_a2a_check模块<br/>Test Governance A2a Check<br/>文件: security/test_governance_a2a_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_approver_check_py["治理Approver检查测试<br/>安全包的test_governance_approver_check模块<br/>Test Governance Approver Check<br/>文件: security/test_governance_approver_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_bootstrap_superadmin_py["治理BootstrapSuperadmin测试<br/>安全包的test_governance_bootstrap_superadmin模块<br/>Test Governance Bootstrap Superadmin<br/>文件: security<br/>/test_governance_bootstrap_superadmin.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_capability_check_py["治理能力检查测试<br/>安全包的test_governance_capability_check模块<br/>Test Governance Capability Check<br/>文件: security<br/>/test_governance_capability_check.py<br/>(生产态 / production)"]
    tests_governance_security_test_governance_contracts_py["治理契约测试<br/>安全包的test_governance_contracts模块<br/>Test Governance Contracts<br/>文件: security/test_governance_contracts.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_main_py ~~~ src_zephyr_gov_drift_analysis_py
    src_zephyr_gov_drift_analysis_py ~~~ src_zephyr_gov_drift_core_py
    src_zephyr_gov_drift_core_py ~~~ src_zephyr_gov_drift_drift_py
    src_zephyr_gov_drift_drift_py ~~~ src_zephyr_gov_drift_infrastructure_py
    src_zephyr_gov_drift_infrastructure_py ~~~ src_zephyr_gov_drift_scanners_py
    src_zephyr_gov_drift_scanners_py ~~~ src_zephyr_governance_agent_rbac_contracts_py
    src_zephyr_governance_agent_rbac_contracts_py ~~~ src_zephyr_red_blue_validator_init_py
    src_zephyr_red_blue_validator_init_py ~~~ src_zephyr_security_access_control_adversarial_resilience_py
    src_zephyr_security_access_control_adversarial_resilience_py ~~~ src_zephyr_security_access_control_agent_creation_policy_py
    src_zephyr_security_access_control_agent_creation_policy_py ~~~ src_zephyr_security_access_control_asymmetric_audit_py
    src_zephyr_security_access_control_asymmetric_audit_py ~~~ src_zephyr_security_access_control_auto_maintenance_py
    src_zephyr_security_access_control_auto_maintenance_py ~~~ src_zephyr_security_access_control_blueprint_fidelity_py
    src_zephyr_security_access_control_blueprint_fidelity_py ~~~ src_zephyr_security_access_control_build_sanitizer_py
    src_zephyr_security_access_control_build_sanitizer_py ~~~ src_zephyr_security_access_control_cache_invalidation_py
    src_zephyr_security_access_control_cache_invalidation_py ~~~ src_zephyr_security_access_control_canary_rollout_manager_py
    src_zephyr_security_access_control_canary_rollout_manager_py ~~~ src_zephyr_security_access_control_cascading_failure_isolator_py
    src_zephyr_security_access_control_cascading_failure_isolator_py ~~~ src_zephyr_security_access_control_compliance_matrix_py
    src_zephyr_security_access_control_compliance_matrix_py ~~~ src_zephyr_security_access_control_cross_cutting_py
    src_zephyr_security_access_control_cross_cutting_py ~~~ src_zephyr_security_access_control_decision_explainer_py
    src_zephyr_security_access_control_decision_explainer_py ~~~ src_zephyr_security_access_control_decision_registry_py
    src_zephyr_security_access_control_decision_registry_py ~~~ src_zephyr_security_access_control_defense_depth_py
    src_zephyr_security_access_control_defense_depth_py ~~~ src_zephyr_security_access_control_dependency_auditor_py
    src_zephyr_security_access_control_dependency_auditor_py ~~~ src_zephyr_security_access_control_derive_rbac_roles_py
    src_zephyr_security_access_control_derive_rbac_roles_py ~~~ src_zephyr_security_access_control_detectors_anomaly_detector_py
    src_zephyr_security_access_control_detectors_anomaly_detector_py ~~~ src_zephyr_security_access_control_detectors_context_drift_detector_py
    src_zephyr_security_access_control_detectors_context_drift_detector_py ~~~ src_zephyr_security_access_control_detectors_cross_session_detector_py
    src_zephyr_security_access_control_detectors_cross_session_detector_py ~~~ src_zephyr_security_access_control_detectors_false_completion_detector_py
    src_zephyr_security_access_control_detectors_false_completion_detector_py ~~~ src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py
    src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py ~~~ src_zephyr_security_access_control_detectors_shell_dialect_detector_py
    src_zephyr_security_access_control_detectors_shell_dialect_detector_py ~~~ src_zephyr_security_access_control_dry_run_py
    src_zephyr_security_access_control_dry_run_py ~~~ src_zephyr_security_access_control_emergency_override_py
    src_zephyr_security_access_control_emergency_override_py ~~~ src_zephyr_security_access_control_environment_manager_py
    src_zephyr_security_access_control_environment_manager_py ~~~ src_zephyr_security_access_control_escalation_handler_py
    src_zephyr_security_access_control_escalation_handler_py ~~~ src_zephyr_security_access_control_exceptions_py
    src_zephyr_security_access_control_exceptions_py ~~~ src_zephyr_security_access_control_genesis_bootstrap_py
    src_zephyr_security_access_control_genesis_bootstrap_py ~~~ src_zephyr_security_access_control_guard_layers_py
    src_zephyr_security_access_control_guard_layers_py ~~~ src_zephyr_security_access_control_guards_abac_guard_py
    src_zephyr_security_access_control_guards_abac_guard_py ~~~ src_zephyr_security_access_control_guards_anti_pattern_guard_py
    src_zephyr_security_access_control_guards_anti_pattern_guard_py ~~~ src_zephyr_security_access_control_guards_audit_log_guard_py
    src_zephyr_security_access_control_guards_audit_log_guard_py ~~~ src_zephyr_security_access_control_guards_cybersec_2026_guard_py
    src_zephyr_security_access_control_guards_cybersec_2026_guard_py ~~~ src_zephyr_security_access_control_guards_input_guard_py
    src_zephyr_security_access_control_guards_input_guard_py ~~~ src_zephyr_security_access_control_guards_memory_guard_py
    src_zephyr_security_access_control_guards_memory_guard_py ~~~ src_zephyr_security_access_control_guards_memory_provenance_guard_py
    src_zephyr_security_access_control_guards_memory_provenance_guard_py ~~~ src_zephyr_security_access_control_guards_native_api_guard_py
    src_zephyr_security_access_control_guards_native_api_guard_py ~~~ src_zephyr_security_access_control_guards_novel_attack_guard_py
    src_zephyr_security_access_control_guards_novel_attack_guard_py ~~~ src_zephyr_security_access_control_guards_output_guard_py
    src_zephyr_security_access_control_guards_output_guard_py ~~~ src_zephyr_security_access_control_guards_path_guard_py
    src_zephyr_security_access_control_guards_path_guard_py ~~~ src_zephyr_security_access_control_guards_replay_attack_guard_py
    src_zephyr_security_access_control_guards_replay_attack_guard_py ~~~ src_zephyr_security_access_control_guards_rule_injection_guard_py
    src_zephyr_security_access_control_guards_rule_injection_guard_py ~~~ src_zephyr_security_access_control_guards_sequence_guard_py
    src_zephyr_security_access_control_guards_sequence_guard_py ~~~ src_zephyr_security_access_control_guards_toctou_guard_py
    src_zephyr_security_access_control_guards_toctou_guard_py ~~~ src_zephyr_security_access_control_guards_vibe_coding_guard_py
    src_zephyr_security_access_control_guards_vibe_coding_guard_py ~~~ src_zephyr_security_access_control_integration_py
    src_zephyr_security_access_control_integration_py ~~~ src_zephyr_security_access_control_integrity_self_check_py
    src_zephyr_security_access_control_integrity_self_check_py ~~~ src_zephyr_security_access_control_intent_binder_py
    src_zephyr_security_access_control_intent_binder_py ~~~ src_zephyr_security_access_control_key_hierarchy_py
    src_zephyr_security_access_control_key_hierarchy_py ~~~ src_zephyr_security_access_control_legal_audit_chain_py
    src_zephyr_security_access_control_legal_audit_chain_py ~~~ src_zephyr_security_access_control_microstructure_defense_py
    src_zephyr_security_access_control_microstructure_defense_py ~~~ src_zephyr_security_access_control_monotonic_clock_py
    src_zephyr_security_access_control_monotonic_clock_py ~~~ src_zephyr_security_access_control_non_repudiation_py
    src_zephyr_security_access_control_non_repudiation_py ~~~ src_zephyr_security_access_control_observability_py
    src_zephyr_security_access_control_observability_py ~~~ src_zephyr_security_access_control_orphan_judge_main_py
    src_zephyr_security_access_control_orphan_judge_main_py ~~~ src_zephyr_security_access_control_orphan_judge_config_loader_py
    src_zephyr_security_access_control_orphan_judge_config_loader_py ~~~ src_zephyr_security_access_control_orphan_judge_drift_bridge_py
    src_zephyr_security_access_control_orphan_judge_drift_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_escalation_bridge_py
    src_zephyr_security_access_control_orphan_judge_escalation_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_feedback_bridge_py
    src_zephyr_security_access_control_orphan_judge_feedback_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_kb_bridge_py
    src_zephyr_security_access_control_orphan_judge_kb_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_mcp_integration_py
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py ~~~ src_zephyr_security_access_control_orphan_judge_orphan_collector_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py ~~~ src_zephyr_security_access_control_orphan_judge_orphan_detector_py
    src_zephyr_security_access_control_orphan_judge_orphan_detector_py ~~~ src_zephyr_security_access_control_orphan_judge_rbac_bridge_py
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py ~~~ src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py ~~~ src_zephyr_security_access_control_orphan_judge_registration_checker_py
    src_zephyr_security_access_control_orphan_judge_registration_checker_py ~~~ src_zephyr_security_access_control_orphan_judge_report_generator_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py ~~~ src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py ~~~ src_zephyr_security_access_control_orphan_judge_swid_tag_py
    src_zephyr_security_access_control_orphan_judge_swid_tag_py ~~~ src_zephyr_security_access_control_orphan_judge_unique_analyzer_py
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py ~~~ src_zephyr_security_access_control_permission_hooks_py
    src_zephyr_security_access_control_permission_hooks_py ~~~ src_zephyr_security_access_control_permission_mode_manager_py
    src_zephyr_security_access_control_permission_mode_manager_py ~~~ src_zephyr_security_access_control_phase_executor_py
    src_zephyr_security_access_control_phase_executor_py ~~~ src_zephyr_security_access_control_risk_mitigation_py
    src_zephyr_security_access_control_risk_mitigation_py ~~~ src_zephyr_security_access_control_rollback_sandbox_py
    src_zephyr_security_access_control_rollback_sandbox_py ~~~ src_zephyr_security_access_control_secrets_lifecycle_py
    src_zephyr_security_access_control_secrets_lifecycle_py ~~~ src_zephyr_security_access_control_session_concurrency_py
    src_zephyr_security_access_control_session_concurrency_py ~~~ src_zephyr_security_access_control_session_lifecycle_py
    src_zephyr_security_access_control_session_lifecycle_py ~~~ src_zephyr_security_access_control_verifiers_bootstrap_verifier_py
    src_zephyr_security_access_control_verifiers_bootstrap_verifier_py ~~~ src_zephyr_security_access_control_verifiers_continuous_verifier_py
    src_zephyr_security_access_control_verifiers_continuous_verifier_py ~~~ src_zephyr_security_access_control_verifiers_contract_verifier_py
    src_zephyr_security_access_control_verifiers_contract_verifier_py ~~~ src_zephyr_security_access_control_verifiers_micro_verifier_py
    src_zephyr_security_access_control_verifiers_micro_verifier_py ~~~ src_zephyr_security_access_control_verifiers_post_action_verifier_py
    src_zephyr_security_access_control_verifiers_post_action_verifier_py ~~~ src_zephyr_security_adversarial_validation_main_py
    src_zephyr_security_adversarial_validation_main_py ~~~ src_zephyr_security_adversarial_validation_ai_attack_generator_py
    src_zephyr_security_adversarial_validation_ai_attack_generator_py ~~~ src_zephyr_security_adversarial_validation_async_monitor_py
    src_zephyr_security_adversarial_validation_async_monitor_py ~~~ src_zephyr_security_adversarial_validation_attack_registry_py
    src_zephyr_security_adversarial_validation_attack_registry_py ~~~ src_zephyr_security_adversarial_validation_commit_trigger_py
    src_zephyr_security_adversarial_validation_commit_trigger_py ~~~ src_zephyr_security_adversarial_validation_constitution_engine_py
    src_zephyr_security_adversarial_validation_constitution_engine_py ~~~ src_zephyr_security_adversarial_validation_game_day_scheduler_py
    src_zephyr_security_adversarial_validation_game_day_scheduler_py ~~~ src_zephyr_security_adversarial_validation_injection_engine_py
    src_zephyr_security_adversarial_validation_injection_engine_py ~~~ src_zephyr_security_adversarial_validation_mcp_endpoints_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py ~~~ src_zephyr_security_adversarial_validation_validator_event_bridge_py
    src_zephyr_security_adversarial_validation_validator_event_bridge_py ~~~ src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py ~~~ src_zephyr_security_llm_defense_llm_security_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py ~~~ tests_governance_security_test_governance_a2a_check_py
    tests_governance_security_test_governance_a2a_check_py ~~~ tests_governance_security_test_governance_approver_check_py
    tests_governance_security_test_governance_approver_check_py ~~~ tests_governance_security_test_governance_bootstrap_superadmin_py
    tests_governance_security_test_governance_bootstrap_superadmin_py ~~~ tests_governance_security_test_governance_capability_check_py
    tests_governance_security_test_governance_capability_check_py ~~~ tests_governance_security_test_governance_contracts_py
    src_zephyr_gov_drift_alert_router_py["Alert路由器<br/>Alert Router — alert_router.py<br/>文件: gov_drift/alert_router.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_cold_start_py["冷启动<br/>Cold Start Bootstrapper — 冷启动引导 §6.31。<br/>文件: gov_drift/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_events_py["ManagedDriftEvent Pydantic V2 BaseModel<br/>漂移事件定义.<br/>G-CT-005 — ManagedDriftEvent Pydantic V2<br/>BaseModel 漂移事件定义.<br/>Events<br/>文件: gov_drift/events.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_reconciler_py["对账器<br/>Auto Reconciler — reconciler.py<br/>文件: gov_drift/reconciler.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_runbook_generator_py["构造 YAML frontmatter<br/>Drift Runbook Generator — 漂移演练手册自动生成。<br/>文件: gov_drift/runbook_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_state_machine_py["状态Machine<br/>Drift State Machine — state_machine.py<br/>文件: gov_drift/state_machine.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_a2a_check_py["—校验两个 agent 之间是否允许通信<br/>A2A 通信对验证——校验两个 agent<br/>之间是否允许通信。<br/>A2a Check<br/>文件: access_control/a2a_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_approver_check_py["校验审批人是否有权执行请求的动作<br/>Approver authorization verifier —<br/>校验审批人是否有权执行请求的动作。<br/>Approver Check<br/>文件: access_control/approver_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_bootstrap_superadmin_py["Superadmin 账户启动器.<br/>BootstrapSuperadmin — Superadmin 账户启动器.<br/>Bootstrap Superadmin<br/>文件: access_control/bootstrap_superadmin.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_capability_check_py["拒绝受限能力声明、空能力声明及能力数量超限<br/>Agent capability scope verification —<br/>拒绝受限能力声明、空能力声明及能力数量...<br/>Capability Check<br/>文件: access_control/capability_check.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_cold_start_lock_py["冷启动锁.<br/>ColdStartLock — 冷启动锁.<br/>Cold Start Lock<br/>文件: access_control/cold_start_lock.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_contracts_py["G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge.<br/>安全/access control包的contracts模块<br/>文件: access_control/contracts.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_engine_degradation_py["引擎降级管理.<br/>EngineDegradation — 引擎降级管理.<br/>Engine Degradation<br/>文件: access_control/engine_degradation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_permission_guard_py["七层权限编排器.<br/>PermissionGuard — 七层权限编排器.<br/>Permission Guard<br/>文件: guards/permission_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_kill_switch_py["熔断器.<br/>KillSwitch — 熔断器.<br/>Kill Switch<br/>文件: access_control/kill_switch.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py["—分析删除文件对项目的影响<br/>安全/orphan judge包的cascade_analyzer模块<br/>Cascade Analyzer<br/>文件: orphan_judge/cascade_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_db_py["数据库<br/>安全/orphan judge包的db模块<br/>文件: orphan_judge/db.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_decision_table_py["五层判定结果 -> 处置动作映射表<br/>安全/orphan judge包的decision_table模块<br/>Decision Table<br/>文件: orphan_judge/decision_table.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py["—标记和追踪废弃文件的生命周期<br/>安全/orphan judge包的deprecation_tracker模块<br/>Deprecation Tracker<br/>文件: orphan_judge/deprecation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_safety_fence_py["—阻止删除 frozen/immutable_core 文件<br/>安全/orphan judge包的safety_fence模块<br/>Safety Fence<br/>文件: orphan_judge/safety_fence.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_circuit_breaker_py["写入：state<br/>安全/adversarial<br/>validation包的circuit_breaker模块<br/>Circuit Breaker<br/>文件: adversarial_validation/circuit_breaker.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cli_py["对抗验证CLI<br/>安全/adversarial validation包的cli模块<br/>文件: adversarial_validation/cli.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_constitution_guard_py["Constitution守卫<br/>安全/adversarial<br/>validation包的constitution_guard模块<br/>Constitution Guard<br/>文件: adversarial_validation<br/>/constitution_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_convergence_checker_py["Convergence检查器<br/>安全/adversarial<br/>validation包的convergence_checker模块<br/>Convergence Checker<br/>文件: adversarial_validation<br/>/convergence_checker.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py["行为审计日志器<br/>安全/llm security包的behavior_audit_logger模块<br/>Behavior Audit Logger<br/>文件: llm_security/behavior_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_gateway_py["网关<br/>安全/llm security包的gateway模块<br/>文件: llm_security/gateway.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_input_sanitizer_py["输入净化器<br/>InputSanitizer: path whitelist + command<br/>whitelist + token budget guard.<br/>Input Sanitizer<br/>文件: llm_security/input_sanitizer.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py["注入Patterns<br/>安全/patterns包的injection_patterns模块<br/>Injection Patterns<br/>文件: patterns/injection_patterns.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py["密钥模式<br/>安全/patterns包的secrets模块<br/>文件: patterns/secrets.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py["LSG 自身隔离策略.<br/>安全/self protection包的isolation模块<br/>文件: self_protection/isolation.py<br/>(生产态 / production)"]
    src_zephyr_gov_drift_alert_router_py ~~~ src_zephyr_gov_drift_cold_start_py
    src_zephyr_gov_drift_cold_start_py ~~~ src_zephyr_gov_drift_events_py
    src_zephyr_gov_drift_events_py ~~~ src_zephyr_gov_drift_reconciler_py
    src_zephyr_gov_drift_reconciler_py ~~~ src_zephyr_gov_drift_runbook_generator_py
    src_zephyr_gov_drift_runbook_generator_py ~~~ src_zephyr_gov_drift_state_machine_py
    src_zephyr_gov_drift_state_machine_py ~~~ src_zephyr_security_access_control_a2a_check_py
    src_zephyr_security_access_control_a2a_check_py ~~~ src_zephyr_security_access_control_approver_check_py
    src_zephyr_security_access_control_approver_check_py ~~~ src_zephyr_security_access_control_bootstrap_superadmin_py
    src_zephyr_security_access_control_bootstrap_superadmin_py ~~~ src_zephyr_security_access_control_capability_check_py
    src_zephyr_security_access_control_capability_check_py ~~~ src_zephyr_security_access_control_cold_start_lock_py
    src_zephyr_security_access_control_cold_start_lock_py ~~~ src_zephyr_security_access_control_contracts_py
    src_zephyr_security_access_control_contracts_py ~~~ src_zephyr_security_access_control_engine_degradation_py
    src_zephyr_security_access_control_engine_degradation_py ~~~ src_zephyr_security_access_control_guards_permission_guard_py
    src_zephyr_security_access_control_guards_permission_guard_py ~~~ src_zephyr_security_access_control_kill_switch_py
    src_zephyr_security_access_control_kill_switch_py ~~~ src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py
    src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py ~~~ src_zephyr_security_access_control_orphan_judge_db_py
    src_zephyr_security_access_control_orphan_judge_db_py ~~~ src_zephyr_security_access_control_orphan_judge_decision_table_py
    src_zephyr_security_access_control_orphan_judge_decision_table_py ~~~ src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py
    src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py ~~~ src_zephyr_security_access_control_orphan_judge_safety_fence_py
    src_zephyr_security_access_control_orphan_judge_safety_fence_py ~~~ src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_circuit_breaker_py ~~~ src_zephyr_security_adversarial_validation_cli_py
    src_zephyr_security_adversarial_validation_cli_py ~~~ src_zephyr_security_adversarial_validation_constitution_guard_py
    src_zephyr_security_adversarial_validation_constitution_guard_py ~~~ src_zephyr_security_adversarial_validation_convergence_checker_py
    src_zephyr_security_adversarial_validation_convergence_checker_py ~~~ src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py ~~~ src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_gateway_py ~~~ src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_input_sanitizer_py ~~~ src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py
    src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py ~~~ src_zephyr_security_llm_defense_llm_security_patterns_secrets_py
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    src_zephyr_security_access_control_guards_rbac_guard_py["基于角色的权限守卫.<br/>RBACGuard — 基于角色的权限守卫.<br/>Rbac Guard<br/>文件: guards/rbac_guard.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_models_py["模型<br/>安全/orphan judge包的models模块<br/>文件: orphan_judge/models.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cold_start_py["冷启动<br/>安全/adversarial validation包的cold_start模块<br/>Cold Start<br/>文件: adversarial_validation/cold_start.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_game_day_runner_py["GameDay运行器<br/>安全/adversarial<br/>validation包的game_day_runner模块<br/>Game Day Runner<br/>文件: adversarial_validation/game_day_runner.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py["L0Supply链<br/>安全/layers包的l0_supply_chain模块<br/>L0 Supply Chain<br/>文件: layers/l0_supply_chain.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py["输入来源类型<br/>安全/layers包的l1_input模块<br/>L1 Input<br/>文件: layers/l1_input.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py["prompt 泄露扫描结果<br/>安全/layers包的l2_prompt_protection模块<br/>L2 Prompt Protection<br/>文件: layers/l2_prompt_protection.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py["L2a流程Sandbox<br/>安全/layers包的l2a_process_sandbox模块<br/>L2a Process Sandbox<br/>文件: layers/l2a_process_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py["兼容旧接口的输出过滤层<br/>安全/layers包的l3_output模块<br/>L3 Output<br/>文件: layers/l3_output.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py["解析 L4 HMAC 密钥<br/>安全/layers包的l4_agent模块<br/>L4 Agent<br/>文件: layers/l4_agent.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py["L5 资源保护层：token/cost/rate 限额 +<br/>成本不对称检测<br/>安全/layers包的l5_resource_protection模块<br/>L5 Resource Protection<br/>文件: layers/l5_resource_protection.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py["L6可观测性<br/>L6 Observability Layer — security event<br/>logging, alerting, and reporting.<br/>文件: layers/l6_observability.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py["L8多代理<br/>安全/layers包的l8_multi_agent模块<br/>L8 Multi Agent<br/>文件: layers/l8_multi_agent.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py["裸调 LLM API 被运行时拦截器阻断<br/>runtime_interceptor.py — 运行时 LLM 裸调拦截器<br/>（GATE-20 后备防线）<br/>Runtime Interceptor<br/>文件: llm_security/runtime_interceptor.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py["L7验证<br/>安全/self protection包的l7_validation模块<br/>L7 Validation<br/>文件: self_protection/l7_validation.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_guards_rbac_guard_py ~~~ src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_models_py ~~~ src_zephyr_security_adversarial_validation_cold_start_py
    src_zephyr_security_adversarial_validation_cold_start_py ~~~ src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_game_day_runner_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py ~~~ src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py ~~~ src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py
    src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_access_control_identity_py["角色与成熟度定义.<br/>Agent identity — 角色与成熟度定义.<br/>文件: access_control/identity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_immutable_core_py["不可变核心验证器.<br/>ImmutableCore — 不可变核心验证器.<br/>Immutable Core<br/>文件: access_control/immutable_core.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_judge_py["OrphanJudge 模块基础异常'''<br/>安全/orphan judge包的judge模块<br/>文件: orphan_judge/judge.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_validator_py["只读：blast<br/>安全/adversarial validation包的validator模块<br/>文件: adversarial_validation/validator.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_protocol_py["LLM Security Gateway 九层防御统一接口契约<br/>安全/llm security包的protocol模块<br/>文件: llm_security/protocol.py<br/>(生产态 / production)"]
    src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py["只读：last_scan_time<br/>安全/self protection包的code_integrity模块<br/>Code Integrity<br/>文件: self_protection/code_integrity.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_identity_py ~~~ src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_immutable_core_py ~~~ src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_judge_py ~~~ src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_validator_py ~~~ src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_protocol_py ~~~ src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_access_control_orphan_judge_duplicate_detector_py["—基于 AST 哈希的 Jaccard<br/>相似度检测模块间功能重叠<br/>安全/orphan judge包的duplicate_detector模块<br/>Duplicate Detector<br/>文件: orphan_judge/duplicate_detector.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_blast_radius_py["影响半径<br/>安全/adversarial validation包的blast_radius模块<br/>Blast Radius<br/>文件: adversarial_validation/blast_radius.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_bypass_recorder_py["绕过Recorder<br/>安全/adversarial<br/>validation包的bypass_recorder模块<br/>Bypass Recorder<br/>文件: adversarial_validation/bypass_recorder.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_cleanup_py["清理<br/>安全/adversarial validation包的cleanup模块<br/>文件: adversarial_validation/cleanup.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_defense_runner_py["Defense运行器<br/>安全/adversarial<br/>validation包的defense_runner模块<br/>Defense Runner<br/>文件: adversarial_validation/defense_runner.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_scenario_loader_py["场景加载器<br/>安全/adversarial<br/>validation包的scenario_loader模块<br/>Scenario Loader<br/>文件: adversarial_validation/scenario_loader.py<br/>(生产态 / production)"]
    src_zephyr_security_adversarial_validation_steady_state_py["Steady状态<br/>安全/adversarial validation包的steady_state模块<br/>Steady State<br/>文件: adversarial_validation/steady_state.py<br/>(生产态 / production)"]
    src_zephyr_security_access_control_orphan_judge_duplicate_detector_py ~~~ src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_blast_radius_py ~~~ src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_bypass_recorder_py ~~~ src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_cleanup_py ~~~ src_zephyr_security_adversarial_validation_defense_runner_py
    src_zephyr_security_adversarial_validation_defense_runner_py ~~~ src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_scenario_loader_py ~~~ src_zephyr_security_adversarial_validation_steady_state_py
    src_zephyr_security_adversarial_validation_models_py["模型<br/>安全/adversarial validation包的models模块<br/>文件: adversarial_validation/models.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_rbac_contracts_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_contracts_py
    src_zephyr_gov_drift_core_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_events_py
    src_zephyr_gov_drift_core_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_state_machine_py
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_reconciler_py
    src_zephyr_gov_drift_analysis_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_runbook_generator_py
    src_zephyr_gov_drift_infrastructure_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_alert_router_py
    src_zephyr_gov_drift_infrastructure_py -->|导入依赖 / import_depends| src_zephyr_gov_drift_cold_start_py
    src_zephyr_red_blue_validator_init_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_constitution_guard_py
    src_zephyr_red_blue_validator_init_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_access_control_cold_start_lock_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_derive_rbac_roles_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_bootstrap_superadmin_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_cold_start_lock_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_engine_degradation_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_genesis_bootstrap_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_kill_switch_py
    src_zephyr_security_access_control_guards_abac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_rbac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_rbac_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_identity_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_immutable_core_py
    src_zephyr_security_access_control_guards_permission_guard_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_guards_rbac_guard_py
    src_zephyr_security_access_control_orphan_judge_config_loader_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_db_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_judge_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_duplicate_detector_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_decision_table_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py
    src_zephyr_security_access_control_orphan_judge_orphan_collector_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_safety_fence_py
    src_zephyr_security_access_control_orphan_judge_models_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_mcp_integration_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_registration_checker_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_db_py
    src_zephyr_security_access_control_orphan_judge_report_generator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_swid_tag_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_models_py
    src_zephyr_security_access_control_orphan_judge_rbac_bridge_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_guards_permission_guard_py
    src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_unique_analyzer_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_access_control_orphan_judge_main_py -->|导入依赖 / import_depends| src_zephyr_security_access_control_orphan_judge_judge_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_async_monitor_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_bypass_recorder_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_circuit_breaker_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_blast_radius_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_convergence_checker_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cold_start_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_cli_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_circuit_breaker_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_commit_trigger_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_constitution_engine_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_game_day_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_constitution_guard_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_defense_runner_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_injection_engine_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_convergence_checker_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_mcp_endpoints_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_adversarial_validation_game_day_scheduler_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_game_day_runner_py
    src_zephyr_security_adversarial_validation_scenario_loader_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_steady_state_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_main_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cli_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_bypass_recorder_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_blast_radius_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_cleanup_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_defense_runner_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_models_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_scenario_loader_py
    src_zephyr_security_adversarial_validation_validator_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_steady_state_py
    src_zephyr_security_adversarial_validation_validator_event_bridge_py -->|导入依赖 / import_depends| src_zephyr_security_adversarial_validation_validator_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_secrets_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    tests_governance_security_test_governance_approver_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_approver_check_py
    tests_governance_security_test_governance_a2a_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_a2a_check_py
    tests_governance_security_test_governance_contracts_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_contracts_py
    tests_governance_security_test_governance_capability_check_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_capability_check_py
    tests_governance_security_test_governance_bootstrap_superadmin_py -->|测试依赖 / test_depends| src_zephyr_security_access_control_bootstrap_superadmin_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_gov_drift_main_py,src_zephyr_gov_drift_analysis_py,src_zephyr_gov_drift_core_py,src_zephyr_gov_drift_drift_py,src_zephyr_gov_drift_infrastructure_py,src_zephyr_gov_drift_scanners_py,src_zephyr_gov_drift_alert_router_py,src_zephyr_gov_drift_cold_start_py,src_zephyr_gov_drift_events_py,src_zephyr_gov_drift_reconciler_py,src_zephyr_gov_drift_runbook_generator_py,src_zephyr_gov_drift_state_machine_py,src_zephyr_governance_agent_rbac_contracts_py,src_zephyr_red_blue_validator_init_py,src_zephyr_security_access_control_a2a_check_py,src_zephyr_security_access_control_adversarial_resilience_py,src_zephyr_security_access_control_agent_creation_policy_py,src_zephyr_security_access_control_approver_check_py,src_zephyr_security_access_control_asymmetric_audit_py,src_zephyr_security_access_control_auto_maintenance_py,src_zephyr_security_access_control_blueprint_fidelity_py,src_zephyr_security_access_control_bootstrap_superadmin_py,src_zephyr_security_access_control_build_sanitizer_py,src_zephyr_security_access_control_cache_invalidation_py,src_zephyr_security_access_control_canary_rollout_manager_py,src_zephyr_security_access_control_capability_check_py,src_zephyr_security_access_control_cascading_failure_isolator_py,src_zephyr_security_access_control_cold_start_lock_py,src_zephyr_security_access_control_compliance_matrix_py,src_zephyr_security_access_control_contracts_py,src_zephyr_security_access_control_cross_cutting_py,src_zephyr_security_access_control_decision_explainer_py,src_zephyr_security_access_control_decision_registry_py,src_zephyr_security_access_control_defense_depth_py,src_zephyr_security_access_control_dependency_auditor_py,src_zephyr_security_access_control_derive_rbac_roles_py,src_zephyr_security_access_control_detectors_anomaly_detector_py,src_zephyr_security_access_control_detectors_context_drift_detector_py,src_zephyr_security_access_control_detectors_cross_session_detector_py,src_zephyr_security_access_control_detectors_false_completion_detector_py,src_zephyr_security_access_control_detectors_multi_agent_collusion_detector_py,src_zephyr_security_access_control_detectors_shell_dialect_detector_py,src_zephyr_security_access_control_dry_run_py,src_zephyr_security_access_control_emergency_override_py,src_zephyr_security_access_control_engine_degradation_py,src_zephyr_security_access_control_environment_manager_py,src_zephyr_security_access_control_escalation_handler_py,src_zephyr_security_access_control_exceptions_py,src_zephyr_security_access_control_genesis_bootstrap_py,src_zephyr_security_access_control_guard_layers_py,src_zephyr_security_access_control_guards_abac_guard_py,src_zephyr_security_access_control_guards_anti_pattern_guard_py,src_zephyr_security_access_control_guards_audit_log_guard_py,src_zephyr_security_access_control_guards_cybersec_2026_guard_py,src_zephyr_security_access_control_guards_input_guard_py,src_zephyr_security_access_control_guards_memory_guard_py,src_zephyr_security_access_control_guards_memory_provenance_guard_py,src_zephyr_security_access_control_guards_native_api_guard_py,src_zephyr_security_access_control_guards_novel_attack_guard_py,src_zephyr_security_access_control_guards_output_guard_py,src_zephyr_security_access_control_guards_path_guard_py,src_zephyr_security_access_control_guards_permission_guard_py,src_zephyr_security_access_control_guards_rbac_guard_py,src_zephyr_security_access_control_guards_replay_attack_guard_py,src_zephyr_security_access_control_guards_rule_injection_guard_py,src_zephyr_security_access_control_guards_sequence_guard_py,src_zephyr_security_access_control_guards_toctou_guard_py,src_zephyr_security_access_control_guards_vibe_coding_guard_py,src_zephyr_security_access_control_identity_py,src_zephyr_security_access_control_immutable_core_py,src_zephyr_security_access_control_integration_py,src_zephyr_security_access_control_integrity_self_check_py,src_zephyr_security_access_control_intent_binder_py,src_zephyr_security_access_control_key_hierarchy_py,src_zephyr_security_access_control_kill_switch_py,src_zephyr_security_access_control_legal_audit_chain_py,src_zephyr_security_access_control_microstructure_defense_py,src_zephyr_security_access_control_monotonic_clock_py,src_zephyr_security_access_control_non_repudiation_py,src_zephyr_security_access_control_observability_py,src_zephyr_security_access_control_orphan_judge_main_py,src_zephyr_security_access_control_orphan_judge_cascade_analyzer_py,src_zephyr_security_access_control_orphan_judge_config_loader_py,src_zephyr_security_access_control_orphan_judge_db_py,src_zephyr_security_access_control_orphan_judge_decision_table_py,src_zephyr_security_access_control_orphan_judge_deprecation_tracker_py,src_zephyr_security_access_control_orphan_judge_drift_bridge_py,src_zephyr_security_access_control_orphan_judge_duplicate_detector_py,src_zephyr_security_access_control_orphan_judge_escalation_bridge_py,src_zephyr_security_access_control_orphan_judge_feedback_bridge_py,src_zephyr_security_access_control_orphan_judge_judge_py,src_zephyr_security_access_control_orphan_judge_kb_bridge_py,src_zephyr_security_access_control_orphan_judge_mcp_integration_py,src_zephyr_security_access_control_orphan_judge_models_py,src_zephyr_security_access_control_orphan_judge_orphan_collector_py,src_zephyr_security_access_control_orphan_judge_orphan_detector_py,src_zephyr_security_access_control_orphan_judge_rbac_bridge_py,src_zephyr_security_access_control_orphan_judge_reference_graph_engine_py,src_zephyr_security_access_control_orphan_judge_registration_checker_py,src_zephyr_security_access_control_orphan_judge_report_generator_py,src_zephyr_security_access_control_orphan_judge_safety_fence_py,src_zephyr_security_access_control_orphan_judge_standalone_evaluator_py,src_zephyr_security_access_control_orphan_judge_swid_tag_py,src_zephyr_security_access_control_orphan_judge_unique_analyzer_py,src_zephyr_security_access_control_permission_hooks_py,src_zephyr_security_access_control_permission_mode_manager_py,src_zephyr_security_access_control_phase_executor_py,src_zephyr_security_access_control_risk_mitigation_py,src_zephyr_security_access_control_rollback_sandbox_py,src_zephyr_security_access_control_secrets_lifecycle_py,src_zephyr_security_access_control_session_concurrency_py,src_zephyr_security_access_control_session_lifecycle_py,src_zephyr_security_access_control_verifiers_bootstrap_verifier_py,src_zephyr_security_access_control_verifiers_continuous_verifier_py,src_zephyr_security_access_control_verifiers_contract_verifier_py,src_zephyr_security_access_control_verifiers_micro_verifier_py,src_zephyr_security_access_control_verifiers_post_action_verifier_py,src_zephyr_security_adversarial_validation_main_py,src_zephyr_security_adversarial_validation_ai_attack_generator_py,src_zephyr_security_adversarial_validation_async_monitor_py,src_zephyr_security_adversarial_validation_attack_registry_py,src_zephyr_security_adversarial_validation_blast_radius_py,src_zephyr_security_adversarial_validation_bypass_recorder_py,src_zephyr_security_adversarial_validation_circuit_breaker_py,src_zephyr_security_adversarial_validation_cleanup_py,src_zephyr_security_adversarial_validation_cli_py,src_zephyr_security_adversarial_validation_cold_start_py,src_zephyr_security_adversarial_validation_commit_trigger_py,src_zephyr_security_adversarial_validation_constitution_engine_py,src_zephyr_security_adversarial_validation_constitution_guard_py,src_zephyr_security_adversarial_validation_convergence_checker_py,src_zephyr_security_adversarial_validation_defense_runner_py,src_zephyr_security_adversarial_validation_game_day_runner_py,src_zephyr_security_adversarial_validation_game_day_scheduler_py,src_zephyr_security_adversarial_validation_injection_engine_py,src_zephyr_security_adversarial_validation_mcp_endpoints_py,src_zephyr_security_adversarial_validation_models_py,src_zephyr_security_adversarial_validation_scenario_loader_py,src_zephyr_security_adversarial_validation_steady_state_py,src_zephyr_security_adversarial_validation_validator_py,src_zephyr_security_adversarial_validation_validator_event_bridge_py,src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py,src_zephyr_security_llm_defense_llm_security_dashboard_app_py,src_zephyr_security_llm_defense_llm_security_gateway_py,src_zephyr_security_llm_defense_llm_security_input_sanitizer_py,src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py,src_zephyr_security_llm_defense_llm_security_layers_l1_input_py,src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_layers_l3_output_py,src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py,src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py,src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py,src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py,src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py,src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py,src_zephyr_security_llm_defense_llm_security_patterns_secrets_py,src_zephyr_security_llm_defense_llm_security_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_protocol_py,src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py,src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py,src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py,src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py,src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py,src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py,tests_governance_security_test_governance_a2a_check_py,tests_governance_security_test_governance_approver_check_py,tests_governance_security_test_governance_bootstrap_superadmin_py,tests_governance_security_test_governance_capability_check_py,tests_governance_security_test_governance_contracts_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 拒绝受限能力声明、空能力声明及能力数量超限 / Capability C... | → | D_AUTONOMY_CORE 自治核心: skillRBAC注册表 / G-CT-003: Agent Spec -> RBAC capability... | 导入依赖 / import_depends |
| 2 | 治理能力检查测试 / Test Governance Capability Check (secu... | → | D_AUTONOMY_CORE 自治核心: skillRBAC注册表 / G-CT-003: Agent Spec -> RBAC capability... | 测试依赖 / test_depends |
| 3 | 反馈桥接器 / Feedback Bridge (orphan_judge/feedback_bridg... | → | D_FEEDBACK_LOOP 反馈循环引擎: 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 4 | 数据库 / Db (orphan_judge/db.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 5 | G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. / Contra... | → | D_GOV_AUDIT 审计追踪: 契约 / contracts (gov_audit/contracts.py) | 导入依赖 / import_depends |
| 6 | OrphanJudge 模块基础异常 / Judge (orphan_judge/judge.py) | → | D_GOV_AUDIT 审计追踪: 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 7 | Defense运行器 / Defense Runner (adversarial_validation/de... | → | D_GOV_AUDIT 审计追踪: 发现模型 / finding_model (gov_audit/finding_model.py) | 导入依赖 / import_depends |
| 8 | 行为审计日志器 / Behavior Audit Logger (llm_security/beha... | → | D_GOV_AUDIT 审计追踪: 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 9 | LSG 自身隔离策略. / Isolation (self_protection/isolation.py) | → | D_GOV_AUDIT 审计追踪: 写入核心审计链——治本（裁定#18 G7 + 5.37.1） / bridge (g... | 导入依赖 / import_depends |
| 10 | 主入口 / Main (gov_drift/__main__.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / Drift Engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 11 | 主入口 / Main (gov_drift/__main__.py) | → | D_GOV_DRIFT 漂移检测: 漂移基础设施 / Drift Infrastructure (gov_drift/drift_infr... | 导入依赖 / import_depends |
| 12 | 主入口 / Main (gov_drift/__main__.py) | → | D_GOV_DRIFT 漂移检测: Self检查 / Self Check (gov_drift/self_check.py) | 导入依赖 / import_depends |
| 13 | 主入口 / Main (gov_drift/__main__.py) | → | D_GOV_DRIFT 漂移检测: 只读：base_dir / Self Test Verifier (gov_drift/self_test_... | 导入依赖 / import_depends |
| 14 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：db_path / Correlation Engine (gov_drift/correlation... | 导入依赖 / import_depends |
| 15 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: Credibility引擎 / Credibility Engine (gov_drift/credibili... | 导入依赖 / import_depends |
| 16 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：history / Cross Module Score (gov_drift/cross_modul... | 导入依赖 / import_depends |
| 17 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 重放baseline历史，重构时间线 / Forensics Engine (gov_drif... | 导入依赖 / import_depends |
| 18 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：cache / Git Bisector (gov_drift/git_bisector.py) | 导入依赖 / import_depends |
| 19 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：effort_feedback / Roi Engine (gov_drift/roi_engine.py) | 导入依赖 / import_depends |
| 20 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 行为漂移->回滚触发. / Rollback Bridge (gov_drift/rollback... | 导入依赖 / import_depends |
| 21 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: Self检查 / Self Check (gov_drift/self_check.py) | 导入依赖 / import_depends |
| 22 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：patterns / Suppression Learner (gov_drift/suppressi... | 导入依赖 / import_depends |
| 23 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: TamperProof审计 / Tamper Proof Audit (gov_drift/tamper_pr... | 导入依赖 / import_depends |
| 24 | 分析 / Analysis (gov_drift/_analysis.py) | → | D_GOV_DRIFT 漂移检测: 只读：archive_dir / Trend Analyzer (gov_drift/trend_analy... | 导入依赖 / import_depends |
| 25 | 核心 / Core (gov_drift/_core.py) | → | D_GOV_DRIFT 漂移检测: 配置一致性 / Config Consistency (gov_drift/config_consist... | 导入依赖 / import_depends |
| 26 | 核心 / Core (gov_drift/_core.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / Drift Engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 27 | 核心 / Core (gov_drift/_core.py) | → | D_GOV_DRIFT 漂移检测: 漂移模型 / Drift Models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 28 | 漂移 / Drift (gov_drift/_drift.py) | → | D_GOV_DRIFT 漂移检测: 契约漂移检测器 / Contract Drift Detector (gov_drift/contr... | 导入依赖 / import_depends |
| 29 | 漂移 / Drift (gov_drift/_drift.py) | → | D_GOV_DRIFT 漂移检测: 只读：audit_dir / Drift Hotfix Bypass (gov_drift/drift_ho... | 导入依赖 / import_depends |
| 30 | 漂移 / Drift (gov_drift/_drift.py) | → | D_GOV_DRIFT 漂移检测: 漂移基础设施 / Drift Infrastructure (gov_drift/drift_infr... | 导入依赖 / import_depends |
| 31 | 漂移 / Drift (gov_drift/_drift.py) | → | D_GOV_DRIFT 漂移检测: 语义漂移检测结果 / Drift Result Types (gov_drift/drift_re... | 导入依赖 / import_depends |
| 32 | 漂移 / Drift (gov_drift/_drift.py) | → | D_GOV_DRIFT 漂移检测: 从重复漂移事件中提取的可训练模式 / Drift Training (gov_dr... | 导入依赖 / import_depends |
| 33 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: Absence管理器 / Absence Manager (gov_drift/absence_manage... | 导入依赖 / import_depends |
| 34 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: Ai上下文注入器 / Ai Context Injector (gov_drift/ai_contex... | 导入依赖 / import_depends |
| 35 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 只读：baselines_root / Baseline Manager (gov_drift/baseli... | 导入依赖 / import_depends |
| 36 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: Canary控制器 / Canary Controller (gov_drift/canary_contro... | 导入依赖 / import_depends |
| 37 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 配置一致性 / Config Consistency (gov_drift/config_consist... | 导入依赖 / import_depends |
| 38 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 仪表盘 / Dashboard (gov_drift/dashboard.py) | 导入依赖 / import_depends |
| 39 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 只读：project_root / Gate Persistence (gov_drift/gate_per... | 导入依赖 / import_depends |
| 40 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 构建跨Session交接包 / Handoff Manager (gov_drift/handoff_... | 导入依赖 / import_depends |
| 41 | 基础设施 / Infrastructure (gov_drift/_infrastructure.py) | → | D_GOV_DRIFT 漂移检测: 资源守卫 / Resource Guard (gov_drift/resource_guard.py) | 导入依赖 / import_depends |
| 42 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: 只读：project_root / Incremental Scanner (gov_drift/incre... | 导入依赖 / import_depends |
| 43 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: NamingMagic检查器 / Naming Magic Checker (gov_drift/namin... | 导入依赖 / import_depends |
| 44 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: 孤儿扫描器 / Orphan Scanner (gov_drift/orphan_scanner.py) | 导入依赖 / import_depends |
| 45 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: Python Compat (gov_drift/python_compat.py) | 导入依赖 / import_depends |
| 46 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: 只读：lock_dir / Scan Mutex (gov_drift/scan_mutex.py) | 导入依赖 / import_depends |
| 47 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: Symlink检查器 / Symlink Checker (gov_drift/symlink_checke... | 导入依赖 / import_depends |
| 48 | 扫描器 / Scanners (gov_drift/_scanners.py) | → | D_GOV_DRIFT 漂移检测: 检查测试夹具中硬编码数据结构是否与 ORM/pydantic schema 一... | 导入依赖 / import_depends |
| 49 | 冷启动 / Cold Start (gov_drift/cold_start.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / Drift Engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 50 | 对账器 / Reconciler (gov_drift/reconciler.py) | → | D_GOV_DRIFT 漂移检测: 漂移模型 / Drift Models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 51 | 构造 YAML frontmatter / Runbook Generator (gov_drift/runb... | → | D_GOV_DRIFT 漂移检测: 漂移模型 / Drift Models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 52 | 状态Machine / State Machine (gov_drift/state_machine.py) | → | D_GOV_DRIFT 漂移检测: 漂移模型 / Drift Models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 53 | 漂移桥接器 / Drift Bridge (orphan_judge/drift_bridge.py) | → | D_GOV_DRIFT 漂移检测: ``drift_detected`` 触发器恢复入口 / Drift Detector (rule_... | 导入依赖 / import_depends |
| 54 | Escalation桥接器 / Escalation Bridge (orphan_judge/escala... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 空 Protocol 作为 12 个异构 detector 类的鸭子类型标记 / Es... | 导入依赖 / import_depends |
| 55 | GameDay调度器 / Game Day Scheduler (adversarial_validatio... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: ZephyrAlpha 施工阶段门控引擎. / Phase Manager (ops_govern... | 导入依赖 / import_depends |
| 56 | OrphanJudge 模块基础异常 / Judge (orphan_judge/judge.py) | → | D_GOV_RULE 规则治理: 门禁类型定义 / Gate Types (rule_enforcement/gate_types.py) | 导入依赖 / import_depends |
| 57 | Constitution守卫 / Constitution Guard (adversarial_valida... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 58 | Defense运行器 / Defense Runner (adversarial_validation/de... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 59 | Defense运行器 / Defense Runner (adversarial_validation/de... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 60 | MCP集成 / Mcp Integration (orphan_judge/mcp_integration.py) | → | D_INFRA_RUNTIME 运行时集成: MOD-INF-026 蓝图 §21 / Mcp Server (asset_inventory/mcp_s... | 导入依赖 / import_depends |
| 61 | 孤儿检测器 / Orphan Detector (orphan_judge/orphan_detecto... | → | D_INFRA_RUNTIME 运行时集成: 解决'AI 不知道有这个功能'的问题 / Capability Registry (tr... | 导入依赖 / import_depends |
| 62 | 孤儿检测器 / Orphan Detector (orphan_judge/orphan_detecto... | → | D_INFRA_RUNTIME 运行时集成: 主动发现未注册模块 / Module Onboarding Scanner (trading/m... | 导入依赖 / import_depends |
| 63 | Kb桥接器 / Kb Bridge (orphan_judge/kb_bridge.py) | → | D_INTELLIGENCE 上下文管理: ChromaDB 中承载 RI-02 跨模块记忆的集合名 / Unified Memory... | 导入依赖 / import_depends |
| 64 | 主入口 / Main (gov_drift/__main__.py) | → | D_SHARED 共享服务: async/sync 边界桥接 / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 65 | 冷启动 / Cold Start (gov_drift/cold_start.py) | → | D_SHARED 共享服务: async/sync 边界桥接 / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 66 | 对账器 / Reconciler (gov_drift/reconciler.py) | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 67 | 基于属性的权限守卫. / Abac Guard (guards/abac_guard.py) | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 68 | 角色与成熟度定义. / Identity (access_control/identity.py) | → | D_SHARED 共享服务: 代理Identity / Agent Identity (identity/agent_identity.py) | 导入依赖 / import_depends |
| 69 | 不可变核心验证器. / Immutable Core (access_control/immuta... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 70 | 主入口 / Main (orphan_judge/__main__.py) | → | D_SHARED 共享服务: 序列化/反序列化过程中类型不兼容或格式错误 / Serialization... | 导入依赖 / import_depends |
| 71 | 配置加载器 / Config Loader (orphan_judge/config_loader.py) | → | D_SHARED 共享服务: 序列化/反序列化过程中类型不兼容或格式错误 / Serialization... | 导入依赖 / import_depends |
| 72 | 反馈桥接器 / Feedback Bridge (orphan_judge/feedback_bridg... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 73 | 报告生成器 / Report Generator (orphan_judge/report_genera... | → | D_SHARED 共享服务: 序列化/反序列化过程中类型不兼容或格式错误 / Serialization... | 导入依赖 / import_depends |
| 74 | Session 级并发协调模块 / Session Concurrency (access_cont... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 75 | 提交触发器 / Commit Trigger (adversarial_validation/commi... | → | D_SHARED 共享服务: 任务生命周期事件类型 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 76 | 提交触发器 / Commit Trigger (adversarial_validation/commi... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 77 | Defense运行器 / Defense Runner (adversarial_validation/de... | → | D_SHARED 共享服务: 执行模型 / Execution Model (schema/execution_model.py) | 导入依赖 / import_depends |
| 78 | Defense运行器 / Defense Runner (adversarial_validation/de... | → | D_SHARED 共享服务: Severity类型定义 / Severity Types (schema/severity_types.py) | 导入依赖 / import_depends |
| 79 | Steady状态 / Steady State (adversarial_validation/steady_... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 80 | 只读：blast / Validator (adversarial_validation/validator... | → | D_SHARED 共享服务: 任务生命周期事件类型 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 81 | 订阅 EventBusBackpressure 的 fix_completed 事件 / Validat... | → | D_SHARED 共享服务: 任务生命周期事件类型 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 82 | 行为审计日志器 / Behavior Audit Logger (llm_security/beha... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 83 | 仪表盘应用 / App (dashboard/app.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 84 | L0Supply链 / L0 Supply Chain (layers/l0_supply_chain.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 85 | L0Supply链 / L0 Supply Chain (layers/l0_supply_chain.py) | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 86 | 输入来源类型 / L1 Input (layers/l1_input.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 87 | prompt 泄露扫描结果 / L2 Prompt Protection (layers/l2_pro... | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 88 | L2a流程Sandbox / L2a Process Sandbox (layers/l2a_process_... | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 89 | L2a流程Sandbox / L2a Process Sandbox (layers/l2a_process_... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 90 | 兼容旧接口的输出过滤层 / L3 Output (layers/l3_output.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 91 | 解析 L4 HMAC 密钥 / L4 Agent (layers/l4_agent.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 92 | 解析 L4 HMAC 密钥 / L4 Agent (layers/l4_agent.py) | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 93 | L5 资源保护层：token/cost/rate 限额 + 成本不对称检测 / L5... | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 94 | L6可观测性 / L6 Observability (layers/l6_observability.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 95 | L8多代理 / L8 Multi Agent (layers/l8_multi_agent.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 96 | 密钥模式 / Secrets (patterns/secrets.py) | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 97 | 流程Sandbox / Process Sandbox (llm_security/process_sandb... | → | D_SHARED 共享服务: 返回 Windows 无窗口 creationflags；POSIX 返回 0 / Process... | 导入依赖 / import_depends |
| 98 | 流程Sandbox / Process Sandbox (llm_security/process_sandb... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 99 | LLM Security Gateway 九层防御统一接口契约 / Protocol (llm... | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 100 | 对 Red Team 载荷施加 10 种变异技术，检验 LSG 抗干扰能力. ... | → | D_SHARED 共享服务: async/sync 边界桥接 / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 101 | L7验证 / L7 Validation (self_protection/l7_validation.py) | → | D_SHARED 共享服务: 安全决策 / Security Decision (security/security_decision.py) | 导入依赖 / import_depends |
| 102 | L7 Red Team 对抗扫描器. / Red Team Scanner (self_protecti... | → | D_SHARED 共享服务: async/sync 边界桥接 / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: 上下文injector / ContextInjector: retrieve and inject rel... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 2 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | Alert路由器 / Alert Router (gov_drift/alert_router.py) | 导入依赖 / import_depends |
| 3 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | 冷启动 / Cold Start (gov_drift/cold_start.py) | 导入依赖 / import_depends |
| 4 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 导入依赖 / import_depends |
| 5 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | 对账器 / Reconciler (gov_drift/reconciler.py) | 导入依赖 / import_depends |
| 6 | D_COMPLIANCE 合规: 包入口 / __init__ (behavioral_auditor/__init__.py) | → | 构造 YAML frontmatter / Runbook Generator (gov_drift/runb... | 导入依赖 / import_depends |
| 7 | D_FEEDBACK_LOOP 反馈循环引擎: 进化引擎 / evolution_engine (feedback_loop/evolution_engi... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: Git提交 / git_commit (scripts/git_commit.py) | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | → | 七层权限编排器. / Permission Guard (guards/permission_gua... | 导入依赖 / import_depends |
| 10 | D_GOVERNANCE 生命周期管理: delegation引擎 / Delegation Engine — MOD-INF-022 (intell... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 11 | D_GOVERNANCE 生命周期管理: 治理服务端 / governance_server (mcp/governance_server.py) | → | 冷启动 / Cold Start (gov_drift/cold_start.py) | 导入依赖 / import_depends |
| 12 | D_GOVERNANCE 生命周期管理: 治理服务端 / governance_server (mcp/governance_server.py) | → | 七层权限编排器. / Permission Guard (guards/permission_gua... | 导入依赖 / import_depends |
| 13 | D_GOVERNANCE 生命周期管理: 测试会话感知stashredblue / test_session_aware_stash_red_b... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 14 | D_GOVERNANCE 生命周期管理: Drift → Rollback 集成测试. / Test Gct 005 Drift To Rollb... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 15 | D_GOVERNANCE 生命周期管理: G-CT GCT集成契约测试. / Test Gct Integration (drift/test_... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 16 | D_GOVERNANCE 生命周期管理: G-CT GCT集成契约测试. / Test Gct Integration (drift/test_... | → | 校验两个 agent 之间是否允许通信 / A2a Check (access_contr... | 测试依赖 / test_depends |
| 17 | D_GOVERNANCE 生命周期管理: G-CT GCT集成契约测试. / Test Gct Integration (drift/test_... | → | 拒绝受限能力声明、空能力声明及能力数量超限 / Capability C... | 测试依赖 / test_depends |
| 18 | D_GOVERNANCE 生命周期管理: 治理漂移修复测试 / Test Governance Drift Fix (drift/test_... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 19 | D_GOVERNANCE 生命周期管理: 治理域八件套红白对抗测试 / Test Adversarial Contract Atta... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 20 | D_GOVERNANCE 生命周期管理: 治理域八件套红白对抗测试 / Test Adversarial Contract Atta... | → | 校验两个 agent 之间是否允许通信 / A2a Check (access_contr... | 测试依赖 / test_depends |
| 21 | D_GOVERNANCE 生命周期管理: 治理域八件套红白对抗测试 / Test Adversarial Contract Atta... | → | 校验审批人是否有权执行请求的动作 / Approver Check (access... | 测试依赖 / test_depends |
| 22 | D_GOVERNANCE 生命周期管理: 治理域八件套红白对抗测试 / Test Adversarial Contract Atta... | → | 拒绝受限能力声明、空能力声明及能力数量超限 / Capability C... | 测试依赖 / test_depends |
| 23 | D_GOVERNANCE 生命周期管理: 治理域八件套红白对抗测试 / Test Adversarial Contract Atta... | → | G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. / Contra... | 测试依赖 / test_depends |
| 24 | D_GOVERNANCE 生命周期管理: RBAC→Audit 端到端数据流通. / Test Gct 001 Rbac To Audit ... | → | G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. / Contra... | 测试依赖 / test_depends |
| 25 | D_GOVERNANCE 生命周期管理: Escalation → RBAC 集成测试. / Test Gct 004 Escalation To... | → | 校验审批人是否有权执行请求的动作 / Approver Check (access... | 测试依赖 / test_depends |
| 26 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言 / Test P0 U1 Co... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 27 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言 / Test P0 U1 Co... | → | 校验两个 agent 之间是否允许通信 / A2a Check (access_contr... | 测试依赖 / test_depends |
| 28 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言 / Test P0 U1 Co... | → | 校验审批人是否有权执行请求的动作 / Approver Check (access... | 测试依赖 / test_depends |
| 29 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言 / Test P0 U1 Co... | → | 拒绝受限能力声明、空能力声明及能力数量超限 / Capability C... | 测试依赖 / test_depends |
| 30 | D_GOVERNANCE 生命周期管理: G-CT-001~008 每条契约的端到端数据流通断言 / Test P0 U1 Co... | → | G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. / Contra... | 测试依赖 / test_depends |
| 31 | D_GOVERNANCE 生命周期管理: A2A → RBAC 集成测试. / Test Gct 008 A2a To Rbac Escalati... | → | 校验两个 agent 之间是否允许通信 / A2a Check (access_contr... | 测试依赖 / test_depends |
| 32 | D_GOVERNANCE 生命周期管理: P0U2Input验证测试 / Test P0 U2 Input Validation (shared/t... | → | 拒绝受限能力声明、空能力声明及能力数量超限 / Capability C... | 测试依赖 / test_depends |
| 33 | D_GOVERNANCE 生命周期管理: Phase Gates + 依赖审计隔离 + A2A Phase 4 Hold 测试. / Tes... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 测试依赖 / test_depends |
| 34 | D_GOVERNANCE 生命周期管理: Phase Gates + 依赖审计隔离 + A2A Phase 4 Hold 测试. / Tes... | → | Superadmin 账户启动器. / Bootstrap Superadmin (access_con... | 测试依赖 / test_depends |
| 35 | D_GOV_AUDIT 审计追踪: 命令行 / cli (gov_audit/cli.py) | → | OrphanJudge 模块基础异常 / Judge (orphan_judge/judge.py) | 导入依赖 / import_depends |
| 36 | D_GOV_AUDIT 审计追踪: 命令行 / cli (gov_audit/cli.py) | → | 只读：blast / Validator (adversarial_validation/validator... | 导入依赖 / import_depends |
| 37 | D_GOV_AUDIT 审计追踪: 对账运行器 / reconcile_runner (audit/reconcile_runner.py) | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 38 | D_GOV_AUDIT 审计追踪: 对账工作器 / reconcile_worker (audit/reconcile_worker.py) | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 39 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 40 | D_GOV_AUDIT 审计追踪: P0I2Construction订单测试 / Test P0 I2 Construction Order ... | → | G-CT-001 RBAC->Audit 桥接契约 - RBACAuditBridge. / Contra... | 测试依赖 / test_depends |
| 41 | D_GOV_CODE_QUALITY 代码质量治理: forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 42 | D_GOV_CODE_QUALITY 代码质量治理: 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 43 | D_GOV_DRIFT 漂移检测: Brain集成 / Brain Integration (gov_drift/brain_integratio... | → | 冷启动 / Cold Start (gov_drift/cold_start.py) | 导入依赖 / import_depends |
| 44 | D_GOV_DRIFT 漂移检测: ``drift_detected`` 触发器恢复入口 / Drift Detector (rule_... | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 导入依赖 / import_depends |
| 45 | D_GOV_DRIFT 漂移检测: ``drift_detected`` 触发器恢复入口 / Drift Detector (rule_... | → | 对账器 / Reconciler (gov_drift/reconciler.py) | 导入依赖 / import_depends |
| 46 | D_GOV_ENFORCEMENT 规则执行: 影子金丝雀部署运行器 / Shadow Canary Deploy Runner (ops/s... | → | 灰度发布管理器. / Canary Rollout Manager (access_control/... | 导入依赖 / import_depends |
| 47 | D_GOV_ENFORCEMENT 规则执行: 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 48 | D_GOV_ENFORCEMENT 规则执行: 全项目唯一合法 git commit 入口 / Git Commit Gateway (rule... | → | 提交触发器 / Commit Trigger (adversarial_validation/commi... | 导入依赖 / import_depends |
| 49 | D_GOV_ENFORCEMENT 规则执行: session heartbeat 独立进程 / Heartbeat Daemon (rule_bridg... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 50 | D_GOV_ENFORCEMENT 规则执行: AI 对话并发声明 helper / Session Claim (rule_bridge/sessi... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 51 | D_GOV_ENFORCEMENT 规则执行: 会话Worktree / Session Worktree (rule_bridge/session_work... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 52 | D_GOV_ENFORCEMENT 规则执行: IMPORT-INTEGRITY 门禁单测 / Test Import Integrity Gate (c... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 53 | D_GOV_ENFORCEMENT 规则执行: P2-2 并发 session 文件级原子性测试 / Test Claim Files For... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 54 | D_GOV_ENFORCEMENT 规则执行: worktree 物理隔离端到端测试 / Test Session Worktree (rule... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 测试依赖 / test_depends |
| 55 | D_GOV_OPS_RESILIENCE 运维弹性治理: 空 Protocol 作为 12 个异构 detector 类的鸭子类型标记 / Es... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 56 | D_GOV_OPS_RESILIENCE 运维弹性治理: ZephyrAlpha 施工阶段门控引擎. / Phase Manager (ops_govern... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 57 | D_GOV_OPS_RESILIENCE 运维弹性治理: " in finding` 语法 / Default Security Gateway (security_g... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 58 | D_GOV_OPS_RESILIENCE 运维弹性治理: " in finding` 语法 / Default Security Gateway (security_g... | → | 输入净化器 / Input Sanitizer (llm_security/input_sanitize... | 导入依赖 / import_depends |
| 59 | D_GOV_SCRIPTS 脚本治理: lock协议检查+GateEngine Phase评估+注册完整性验证 / Pre Wr... | → | Session 级并发协调模块 / Session Concurrency (access_cont... | 导入依赖 / import_depends |
| 60 | D_INFRA_RECOVERY 回滚恢复: G-CT-005 消费端. / Drift Fix (rollback/drift_fix.py) | → | ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 导入依赖 / import_depends |
| 61 | D_INFRA_RECOVERY 回滚恢复: Runbook生成器 / Runbook Generator (rollback/runbook_gener... | → | 构造 YAML frontmatter / Runbook Generator (gov_drift/runb... | 导入依赖 / import_depends |
| 62 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / Auto Runtime Core (trading/auto_runtime_... | → | RBAC系统启动引导器. / Genesis Bootstrap (access_control/g... | 导入依赖 / import_depends |
| 63 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | RBAC系统启动引导器. / Genesis Bootstrap (access_control/g... | 导入依赖 / import_depends |
| 64 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | 熔断器. / Kill Switch (access_control/kill_switch.py) | 导入依赖 / import_depends |
| 65 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | 不可抵赖性审计签名. / Non Repudiation (access_control/non... | 导入依赖 / import_depends |
| 66 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | 提交触发器 / Commit Trigger (adversarial_validation/commi... | 导入依赖 / import_depends |
| 67 | D_INTEGRATION 管线路由: MCP Gateway 集中式治理节点 / Gateway Server (mcp/gateway_... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 68 | D_INTEGRATION 管线路由: MCP Gateway 集中式治理节点 / Gateway Server (mcp/gateway_... | → | LLM Security Gateway 九层防御统一接口契约 / Protocol (llm... | 导入依赖 / import_depends |
| 69 | D_INTEGRATION 管线路由: 管道编排器 / Pipeline Orchestrator (integration/pipeline_... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 70 | D_ORCHESTRATOR 代理编排器: 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | 网关 / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 71 | D_ORCHESTRATOR 代理编排器: 代理编排器 / Agent Orchestrator (orchestrator/agent_orche... | → | 输入净化器 / Input Sanitizer (llm_security/input_sanitize... | 导入依赖 / import_depends |
| 72 | D_RISK 风控: A股系统性风险检测器输入数据非法 / Ashare Systemic Risk De... | → | 熔断器. / Kill Switch (access_control/kill_switch.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 18 个外部域直接连接（出边 102 条 + 入边 72 条 = 174 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_COMPLIANCE["D_COMPLIANCE<br/>合规"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_RISK["D_RISK<br/>风控"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_SECURITY -->|44条 导入依赖 / import_depends| D_GOV_DRIFT
    D_SECURITY -->|39条 导入依赖 / import_depends| D_SHARED
    D_SECURITY -->|5条 导入依赖 / import_depends| D_GOV_AUDIT
    D_SECURITY -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_SECURITY -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SECURITY -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_SECURITY -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_AUTONOMY_CORE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_INTELLIGENCE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOVERNANCE -->|27条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_GOV_ENFORCEMENT -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_INFRA_RUNTIME -->|5条 导入依赖 / import_depends| D_SECURITY
    D_COMPLIANCE -->|5条 导入依赖 / import_depends| D_SECURITY
    D_GOV_OPS_RESILIENCE -->|4条 导入依赖 / import_depends| D_SECURITY
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_SECURITY
    D_GOV_DRIFT -->|3条 导入依赖 / import_depends| D_SECURITY
    D_INFRA_RECOVERY -->|2条 导入依赖 / import_depends| D_SECURITY
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_SECURITY
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_SECURITY
    D_RISK -->|1条 导入依赖 / import_depends| D_SECURITY
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_SECURITY
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_SECURITY
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_SECURITY
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
