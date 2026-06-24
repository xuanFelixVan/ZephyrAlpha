---
doc_type: domain_architecture_diagram
title: D-SECURITY 对抗验证架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 14_d_security / 对抗验证 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示对抗验证（D-SECURITY）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 对抗验证（D-SECURITY）的模块分布。共 849 个模块 / 849 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (274 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/behavioral_audit/__init__.py  [prototype]           │
│   src/zephyr/behavioral_audit/__main__.py  [prototype]           │
│   src/zephyr/behavioral_audit/_analysis.py  [prototype]          │
│   src/zephyr/behavioral_audit/_core.py  [prototype]              │
│   src/zephyr/behavioral_audit/_drift.py  [prototype]             │
│   src/zephyr/behavioral_audit/_infrastructure.py  [prototype]    │
│   src/zephyr/behavioral_audit/_scanners.py  [prototype]          │
│   src/zephyr/behavioral_audit/alert_router.py  [prototype]       │
│   src/zephyr/behavioral_audit/cold_start.py  [prototype]         │
│   src/zephyr/behavioral_audit/data_quality.py  [prototype]       │
│   src/zephyr/behavioral_audit/events.py  [prototype]             │
│   src/zephyr/behavioral_audit/integration_test_runner.py  [pr... │
│   src/zephyr/behavioral_audit/reconciler.py  [prototype]         │
│   src/zephyr/behavioral_audit/runbook_generator.py  [prototype]  │
│   src/zephyr/behavioral_audit/state_machine.py  [prototype]      │
│   src/zephyr/security/__init__.py  [prototype]                   │
│   src/zephyr/security/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/security/access_control/__init__.py  [production]   │
│   ...还有 256 个模块 / 256 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (575 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   4层guardrails 4-layer Guardrails  [design]                     │
│   6W Log Specification 6W日志规范  [design]                      │
│   AAAI 2026 FinJailbreak AAAI 2026金融越狱  [design]             │
│   ABAC策略引擎 ABAC Policy Engine  [design]                      │
│   ACLGuard 访问控制  [design]                                    │
│   AES-256-GCM AES-256-GCM加密  [design]                          │
│   AES-256加密 AES-256 Encryption  [design]                       │
│   AI Agent Dependency Sandbox AI Agent依赖沙箱  [design]         │
│   AI Agent Dependency Security Sandbox AI Agent依赖安全沙箱  ... │
│   AI Code Modification Auditor AI代码修改审计器  [design]        │
│   AI Construction Governor AI代码质量门控  [design]              │
│   AI Driven Insider Trading Monitoring AI驱动内幕交易监控  [d... │
│   AI Hallucination Package Name Guard AI幻觉包名防护  [design]   │
│   AI Read-Only Permission Executor AI只读权限执行器  [design]    │
│   AI Writable Permission Controller AI可写权限控制器  [design]   │
│   AI-driven Automated Red Team AI驱动自动化红队  [design]        │
│   AI-driven Insider Trading Monitoring 监控  [design]            │
│   AISGBlocked AISG门禁拦截  [design]                             │
│   ...还有 557 个模块 / 557 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 849 个模块 / 849 modules）。

### L1 基础层 / Foundation Layer (274 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/behavioral_audit/__init__.py | src/zephyr/behavioral_audit/__init__.py | prototype | draft |
| 2 | src/zephyr/behavioral_audit/__main__.py | src/zephyr/behavioral_audit/__main__.py | prototype | draft |
| 3 | src/zephyr/behavioral_audit/_analysis.py | src/zephyr/behavioral_audit/_analysis.py | prototype | draft |
| 4 | src/zephyr/behavioral_audit/_core.py | src/zephyr/behavioral_audit/_core.py | prototype | draft |
| 5 | src/zephyr/behavioral_audit/_drift.py | src/zephyr/behavioral_audit/_drift.py | prototype | draft |
| 6 | src/zephyr/behavioral_audit/_infrastructure.py | src/zephyr/behavioral_audit/_infrastr... | prototype | draft |
| 7 | src/zephyr/behavioral_audit/_scanners.py | src/zephyr/behavioral_audit/_scanners.py | prototype | draft |
| 8 | src/zephyr/behavioral_audit/alert_router.py | src/zephyr/behavioral_audit/alert_rou... | prototype | draft |
| 9 | src/zephyr/behavioral_audit/cold_start.py | src/zephyr/behavioral_audit/cold_star... | prototype | draft |
| 10 | src/zephyr/behavioral_audit/data_quality.py | src/zephyr/behavioral_audit/data_qual... | prototype | draft |
| 11 | src/zephyr/behavioral_audit/events.py | src/zephyr/behavioral_audit/events.py | prototype | draft |
| 12 | src/zephyr/behavioral_audit/integration_test_runner.py | src/zephyr/behavioral_audit/integrati... | prototype | draft |
| 13 | src/zephyr/behavioral_audit/reconciler.py | src/zephyr/behavioral_audit/reconcile... | prototype | draft |
| 14 | src/zephyr/behavioral_audit/runbook_generator.py | src/zephyr/behavioral_audit/runbook_g... | prototype | draft |
| 15 | src/zephyr/behavioral_audit/state_machine.py | src/zephyr/behavioral_audit/state_mac... | prototype | draft |
| 16 | src/zephyr/security/__init__.py | src/zephyr/security/__init__.py | prototype | draft |
| 17 | src/zephyr/security/_extensions/__init__.py | src/zephyr/security/_extensions/__ini... | scaffold_placeholder | orphan |
| 18 | src/zephyr/security/access_control/__init__.py | src/zephyr/security/access_control/__... | production | production |
| 19 | src/zephyr/security/access_control/a2a_check.py | src/zephyr/security/access_control/a2... | production | production |
| 20 | src/zephyr/security/access_control/abac_guard.py | src/zephyr/security/access_control/ab... | production | production |
| 21 | src/zephyr/security/access_control/adversarial_resilience.py | src/zephyr/security/access_control/ad... | production | production |
| 22 | src/zephyr/security/access_control/agent_creation_policy.py | src/zephyr/security/access_control/ag... | production | production |
| 23 | src/zephyr/security/access_control/anomaly_detector.py | src/zephyr/security/access_control/an... | production | production |
| 24 | src/zephyr/security/access_control/anti_pattern_guard.py | src/zephyr/security/access_control/an... | production | production |
| 25 | src/zephyr/security/access_control/approver_check.py | src/zephyr/security/access_control/ap... | production | production |
| 26 | src/zephyr/security/access_control/asymmetric_audit.py | src/zephyr/security/access_control/as... | production | production |
| 27 | src/zephyr/security/access_control/audit_log_guard.py | src/zephyr/security/access_control/au... | production | production |
| 28 | src/zephyr/security/access_control/auto_fix_engine_03/__i... | src/zephyr/security/access_control/au... | prototype | production |
| 29 | src/zephyr/security/access_control/auto_fix_engine_03/__m... | src/zephyr/security/access_control/au... | prototype | production |
| 30 | src/zephyr/security/access_control/auto_fix_engine_03/ali... | src/zephyr/security/access_control/au... | prototype | production |
| 31 | src/zephyr/security/access_control/auto_fix_engine_03/all... | src/zephyr/security/access_control/au... | prototype | production |
| 32 | src/zephyr/security/access_control/auto_fix_engine_03/bat... | src/zephyr/security/access_control/au... | prototype | production |
| 33 | src/zephyr/security/access_control/auto_fix_engine_03/com... | src/zephyr/security/access_control/au... | prototype | production |
| 34 | src/zephyr/security/access_control/auto_fix_engine_03/con... | src/zephyr/security/access_control/au... | prototype | production |
| 35 | src/zephyr/security/access_control/auto_fix_engine_03/ded... | src/zephyr/security/access_control/au... | prototype | production |
| 36 | src/zephyr/security/access_control/auto_fix_engine_03/dep... | src/zephyr/security/access_control/au... | production | production |
| 37 | src/zephyr/security/access_control/auto_fix_engine_03/dri... | src/zephyr/security/access_control/au... | production | production |
| 38 | src/zephyr/security/access_control/auto_fix_engine_03/eng... | src/zephyr/security/access_control/au... | production | production |
| 39 | src/zephyr/security/access_control/auto_fix_engine_03/esc... | src/zephyr/security/access_control/au... | production | production |
| 40 | src/zephyr/security/access_control/auto_fix_engine_03/eve... | src/zephyr/security/access_control/au... | production | production |
| 41 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 42 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 43 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 44 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 45 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 46 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 47 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 48 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | production |
| 49 | src/zephyr/security/access_control/auto_fix_engine_03/imp... | src/zephyr/security/access_control/au... | prototype | production |
| 50 | src/zephyr/security/access_control/auto_fix_engine_03/int... | src/zephyr/security/access_control/au... | production | production |
| 51 | src/zephyr/security/access_control/auto_fix_engine_03/llm... | src/zephyr/security/access_control/au... | production | production |
| 52 | src/zephyr/security/access_control/auto_fix_engine_03/mod... | src/zephyr/security/access_control/au... | production | production |
| 53 | src/zephyr/security/access_control/auto_fix_engine_03/sca... | src/zephyr/security/access_control/au... | production | production |
| 54 | src/zephyr/security/access_control/auto_fix_engine_03/sel... | src/zephyr/security/access_control/au... | production | production |
| 55 | src/zephyr/security/access_control/auto_fix_engine_03/sha... | src/zephyr/security/access_control/au... | production | production |
| 56 | src/zephyr/security/access_control/auto_fix_engine_03/sta... | src/zephyr/security/access_control/au... | production | production |
| 57 | src/zephyr/security/access_control/auto_fix_engine_03/zom... | src/zephyr/security/access_control/au... | production | production |
| 58 | src/zephyr/security/access_control/auto_maintenance.py | src/zephyr/security/access_control/au... | production | production |
| 59 | src/zephyr/security/access_control/blind_spot_tracker.py | src/zephyr/security/access_control/bl... | production | production |
| 60 | src/zephyr/security/access_control/blueprint_fidelity.py | src/zephyr/security/access_control/bl... | production | production |
| 61 | src/zephyr/security/access_control/bootstrap_superadmin.py | src/zephyr/security/access_control/bo... | production | production |
| 62 | src/zephyr/security/access_control/bootstrap_verifier.py | src/zephyr/security/access_control/bo... | production | production |
| 63 | src/zephyr/security/access_control/build_sanitizer.py | src/zephyr/security/access_control/bu... | production | production |
| 64 | src/zephyr/security/access_control/cache_invalidation.py | src/zephyr/security/access_control/ca... | production | production |
| 65 | src/zephyr/security/access_control/canary_rollout_manager.py | src/zephyr/security/access_control/ca... | production | production |
| 66 | src/zephyr/security/access_control/capability_check.py | src/zephyr/security/access_control/ca... | production | production |
| 67 | src/zephyr/security/access_control/cascading_failure_isol... | src/zephyr/security/access_control/ca... | production | production |
| 68 | src/zephyr/security/access_control/cold_start_lock.py | src/zephyr/security/access_control/co... | production | production |
| 69 | src/zephyr/security/access_control/compliance_matrix.py | src/zephyr/security/access_control/co... | production | production |
| 70 | src/zephyr/security/access_control/context_drift_detector.py | src/zephyr/security/access_control/co... | production | production |
| 71 | src/zephyr/security/access_control/continuous_verifier.py | src/zephyr/security/access_control/co... | production | production |
| 72 | src/zephyr/security/access_control/contract_verifier.py | src/zephyr/security/access_control/co... | production | production |
| 73 | src/zephyr/security/access_control/contracts.py | src/zephyr/security/access_control/co... | production | production |
| 74 | src/zephyr/security/access_control/cross_cutting.py | src/zephyr/security/access_control/cr... | production | production |
| 75 | src/zephyr/security/access_control/cross_session_detector.py | src/zephyr/security/access_control/cr... | production | production |
| 76 | src/zephyr/security/access_control/cybersec_2026_guard.py | src/zephyr/security/access_control/cy... | production | production |
| 77 | src/zephyr/security/access_control/decision_explainer.py | src/zephyr/security/access_control/de... | production | production |
| 78 | src/zephyr/security/access_control/decision_registry.py | src/zephyr/security/access_control/de... | production | production |
| 79 | src/zephyr/security/access_control/defense_depth.py | src/zephyr/security/access_control/de... | production | production |
| 80 | src/zephyr/security/access_control/dependency_auditor.py | src/zephyr/security/access_control/de... | production | production |
| 81 | src/zephyr/security/access_control/derive_rbac_roles.py | src/zephyr/security/access_control/de... | production | production |
| 82 | src/zephyr/security/access_control/dry_run.py | src/zephyr/security/access_control/dr... | production | production |
| 83 | src/zephyr/security/access_control/emergency_override.py | src/zephyr/security/access_control/em... | production | production |
| 84 | src/zephyr/security/access_control/engine_degradation.py | src/zephyr/security/access_control/en... | production | production |
| 85 | src/zephyr/security/access_control/environment_manager.py | src/zephyr/security/access_control/en... | production | production |
| 86 | src/zephyr/security/access_control/escalation_handler.py | src/zephyr/security/access_control/es... | production | production |
| 87 | src/zephyr/security/access_control/exceptions.py | src/zephyr/security/access_control/ex... | production | production |
| 88 | src/zephyr/security/access_control/false_completion_detec... | src/zephyr/security/access_control/fa... | production | production |
| 89 | src/zephyr/security/access_control/genesis_bootstrap.py | src/zephyr/security/access_control/ge... | production | production |
| 90 | src/zephyr/security/access_control/guard_layers.py | src/zephyr/security/access_control/gu... | production | production |
| 91 | src/zephyr/security/access_control/identity.py | src/zephyr/security/access_control/id... | production | production |
| 92 | src/zephyr/security/access_control/immutable_core.py | src/zephyr/security/access_control/im... | production | production |
| 93 | src/zephyr/security/access_control/input_guard.py | src/zephyr/security/access_control/in... | production | production |
| 94 | src/zephyr/security/access_control/integration.py | src/zephyr/security/access_control/in... | production | production |
| 95 | src/zephyr/security/access_control/integrity_self_check.py | src/zephyr/security/access_control/in... | production | production |
| 96 | src/zephyr/security/access_control/intent_binder.py | src/zephyr/security/access_control/in... | production | production |
| 97 | src/zephyr/security/access_control/key_hierarchy.py | src/zephyr/security/access_control/ke... | production | production |
| 98 | src/zephyr/security/access_control/kill_switch.py | src/zephyr/security/access_control/ki... | production | production |
| 99 | src/zephyr/security/access_control/legal_audit_chain.py | src/zephyr/security/access_control/le... | production | production |
| 100 | src/zephyr/security/access_control/memory_guard.py | src/zephyr/security/access_control/me... | production | production |
| 101 | src/zephyr/security/access_control/memory_provenance_guar... | src/zephyr/security/access_control/me... | production | production |
| 102 | src/zephyr/security/access_control/micro_verifier.py | src/zephyr/security/access_control/mi... | production | production |
| 103 | src/zephyr/security/access_control/microstructure_defense.py | src/zephyr/security/access_control/mi... | production | production |
| 104 | src/zephyr/security/access_control/monotonic_clock.py | src/zephyr/security/access_control/mo... | production | production |
| 105 | src/zephyr/security/access_control/multi_agent_collusion_... | src/zephyr/security/access_control/mu... | production | production |
| 106 | src/zephyr/security/access_control/native_api_guard.py | src/zephyr/security/access_control/na... | production | production |
| 107 | src/zephyr/security/access_control/non_repudiation.py | src/zephyr/security/access_control/no... | production | production |
| 108 | src/zephyr/security/access_control/novel_attack_guard.py | src/zephyr/security/access_control/no... | production | production |
| 109 | src/zephyr/security/access_control/observability.py | src/zephyr/security/access_control/ob... | production | production |
| 110 | src/zephyr/security/access_control/orphan_judge/__init__.py | src/zephyr/security/access_control/or... | prototype | production |
| 111 | src/zephyr/security/access_control/orphan_judge/__main__.py | src/zephyr/security/access_control/or... | prototype | production |
| 112 | src/zephyr/security/access_control/orphan_judge/cascade_a... | src/zephyr/security/access_control/or... | production | production |
| 113 | src/zephyr/security/access_control/orphan_judge/config_lo... | src/zephyr/security/access_control/or... | prototype | production |
| 114 | src/zephyr/security/access_control/orphan_judge/db.py | src/zephyr/security/access_control/or... | prototype | production |
| 115 | src/zephyr/security/access_control/orphan_judge/decision_... | src/zephyr/security/access_control/or... | production | production |
| 116 | src/zephyr/security/access_control/orphan_judge/deprecati... | src/zephyr/security/access_control/or... | production | production |
| 117 | src/zephyr/security/access_control/orphan_judge/drift_bri... | src/zephyr/security/access_control/or... | prototype | production |
| 118 | src/zephyr/security/access_control/orphan_judge/duplicate... | src/zephyr/security/access_control/or... | prototype | production |
| 119 | src/zephyr/security/access_control/orphan_judge/escalatio... | src/zephyr/security/access_control/or... | prototype | production |
| 120 | src/zephyr/security/access_control/orphan_judge/feedback_... | src/zephyr/security/access_control/or... | prototype | production |
| 121 | src/zephyr/security/access_control/orphan_judge/judge.py | src/zephyr/security/access_control/or... | production | production |
| 122 | src/zephyr/security/access_control/orphan_judge/kb_bridge.py | src/zephyr/security/access_control/or... | prototype | production |
| 123 | src/zephyr/security/access_control/orphan_judge/mcp_integ... | src/zephyr/security/access_control/or... | prototype | production |
| 124 | src/zephyr/security/access_control/orphan_judge/models.py | src/zephyr/security/access_control/or... | prototype | production |
| 125 | src/zephyr/security/access_control/orphan_judge/orphan_co... | src/zephyr/security/access_control/or... | prototype | production |
| 126 | src/zephyr/security/access_control/orphan_judge/orphan_de... | src/zephyr/security/access_control/or... | production | production |
| 127 | src/zephyr/security/access_control/orphan_judge/rbac_brid... | src/zephyr/security/access_control/or... | prototype | production |
| 128 | src/zephyr/security/access_control/orphan_judge/reference... | src/zephyr/security/access_control/or... | prototype | production |
| 129 | src/zephyr/security/access_control/orphan_judge/registrat... | src/zephyr/security/access_control/or... | prototype | production |
| 130 | src/zephyr/security/access_control/orphan_judge/report_ge... | src/zephyr/security/access_control/or... | prototype | production |
| 131 | src/zephyr/security/access_control/orphan_judge/safety_fe... | src/zephyr/security/access_control/or... | production | production |
| 132 | src/zephyr/security/access_control/orphan_judge/standalon... | src/zephyr/security/access_control/or... | prototype | production |
| 133 | src/zephyr/security/access_control/orphan_judge/swid_tag.py | src/zephyr/security/access_control/or... | prototype | production |
| 134 | src/zephyr/security/access_control/orphan_judge/unique_an... | src/zephyr/security/access_control/or... | prototype | production |
| 135 | src/zephyr/security/access_control/output_guard.py | src/zephyr/security/access_control/ou... | production | production |
| 136 | src/zephyr/security/access_control/path_guard.py | src/zephyr/security/access_control/pa... | production | production |
| 137 | src/zephyr/security/access_control/permission_guard.py | src/zephyr/security/access_control/pe... | production | production |
| 138 | src/zephyr/security/access_control/permission_hooks.py | src/zephyr/security/access_control/pe... | production | production |
| 139 | src/zephyr/security/access_control/permission_mode_manage... | src/zephyr/security/access_control/pe... | production | production |
| 140 | src/zephyr/security/access_control/phase_executor.py | src/zephyr/security/access_control/ph... | prototype | production |
| 141 | src/zephyr/security/access_control/post_action_verifier.py | src/zephyr/security/access_control/po... | production | production |
| 142 | src/zephyr/security/access_control/rbac_guard.py | src/zephyr/security/access_control/rb... | production | production |
| 143 | src/zephyr/security/access_control/replay_attack_guard.py | src/zephyr/security/access_control/re... | production | production |
| 144 | src/zephyr/security/access_control/risk_mitigation.py | src/zephyr/security/access_control/ri... | production | production |
| 145 | src/zephyr/security/access_control/rollback_sandbox.py | src/zephyr/security/access_control/ro... | production | production |
| 146 | src/zephyr/security/access_control/rule_injection_guard.py | src/zephyr/security/access_control/ru... | production | production |
| 147 | src/zephyr/security/access_control/secrets_lifecycle.py | src/zephyr/security/access_control/se... | production | production |
| 148 | src/zephyr/security/access_control/sequence_guard.py | src/zephyr/security/access_control/se... | production | production |
| 149 | src/zephyr/security/access_control/session_concurrency.py | src/zephyr/security/access_control/se... | production | production |
| 150 | src/zephyr/security/access_control/session_lifecycle.py | src/zephyr/security/access_control/se... | production | production |
| 151 | src/zephyr/security/access_control/shell_dialect_detector.py | src/zephyr/security/access_control/sh... | production | production |
| 152 | src/zephyr/security/access_control/toctou_guard.py | src/zephyr/security/access_control/to... | production | production |
| 153 | src/zephyr/security/access_control/vibe_coding_guard.py | src/zephyr/security/access_control/vi... | production | production |
| 154 | src/zephyr/security/adversarial_validation/__init__.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 155 | src/zephyr/security/adversarial_validation/__main__.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 156 | src/zephyr/security/adversarial_validation/_constitution_... | src/zephyr/security/adversarial_valid... | production | orphan |
| 157 | src/zephyr/security/adversarial_validation/_scenario_regi... | src/zephyr/security/adversarial_valid... | production | orphan |
| 158 | src/zephyr/security/adversarial_validation/ai_attack_gene... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 159 | src/zephyr/security/adversarial_validation/async_monitor.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 160 | src/zephyr/security/adversarial_validation/attack_registr... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 161 | src/zephyr/security/adversarial_validation/blast_radius.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 162 | src/zephyr/security/adversarial_validation/bypass_recorde... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 163 | src/zephyr/security/adversarial_validation/circuit_breake... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 164 | src/zephyr/security/adversarial_validation/cleanup.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 165 | src/zephyr/security/adversarial_validation/cli.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 166 | src/zephyr/security/adversarial_validation/cold_start.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 167 | src/zephyr/security/adversarial_validation/constitution_e... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 168 | src/zephyr/security/adversarial_validation/constitution_g... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 169 | src/zephyr/security/adversarial_validation/convergence_ch... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 170 | src/zephyr/security/adversarial_validation/defense_runner.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 171 | src/zephyr/security/adversarial_validation/game_day_runne... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 172 | src/zephyr/security/adversarial_validation/game_day_sched... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 173 | src/zephyr/security/adversarial_validation/injection_engi... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 174 | src/zephyr/security/adversarial_validation/mcp_endpoints.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 175 | src/zephyr/security/adversarial_validation/models.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 176 | src/zephyr/security/adversarial_validation/scenario_loade... | src/zephyr/security/adversarial_valid... | prototype | draft |
| 177 | src/zephyr/security/adversarial_validation/steady_state.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 178 | src/zephyr/security/adversarial_validation/validator.py | src/zephyr/security/adversarial_valid... | prototype | draft |
| 179 | src/zephyr/security/api/__init__.py | src/zephyr/security/api/__init__.py | scaffold_placeholder | orphan |
| 180 | src/zephyr/security/core/__init__.py | src/zephyr/security/core/__init__.py | scaffold_placeholder | orphan |
| 181 | src/zephyr/security/infrastructure/__init__.py | src/zephyr/security/infrastructure/__... | scaffold_placeholder | orphan |
| 182 | src/zephyr/security/llm_defense/__init__.py | src/zephyr/security/llm_defense/__ini... | prototype | orphan |
| 183 | src/zephyr/security/llm_defense/llm_security/__init__.py | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 184 | src/zephyr/security/llm_defense/llm_security/behavior_aud... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 185 | src/zephyr/security/llm_defense/llm_security/dashboard/__... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 186 | src/zephyr/security/llm_defense/llm_security/dashboard/ap... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 187 | src/zephyr/security/llm_defense/llm_security/gateway.py | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 188 | src/zephyr/security/llm_defense/llm_security/input_saniti... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 189 | src/zephyr/security/llm_defense/llm_security/layers/__ini... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 190 | src/zephyr/security/llm_defense/llm_security/layers/l0_su... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 191 | src/zephyr/security/llm_defense/llm_security/layers/l1_in... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 192 | src/zephyr/security/llm_defense/llm_security/layers/l2_pr... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 193 | src/zephyr/security/llm_defense/llm_security/layers/l2a_p... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 194 | src/zephyr/security/llm_defense/llm_security/layers/l3_ou... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 195 | src/zephyr/security/llm_defense/llm_security/layers/l4_ag... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 196 | src/zephyr/security/llm_defense/llm_security/layers/l5_re... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 197 | src/zephyr/security/llm_defense/llm_security/layers/l6_da... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 198 | src/zephyr/security/llm_defense/llm_security/layers/l6_ob... | src/zephyr/security/llm_defense/llm_s... | production | draft |
| 199 | src/zephyr/security/llm_defense/llm_security/layers/l7_ru... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |
| 200 | src/zephyr/security/llm_defense/llm_security/layers/l8_co... | src/zephyr/security/llm_defense/llm_s... | prototype | draft |

> (仅显示前 200 个模块，共 274 个)

### 未分类 / Unclassified (575 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-SECURITY/4层guardrails 4-layer Guardrails | 4层guardrails 4-layer Guardrails | design | design_only |
| 2 | D-SECURITY/6W Log Specification 6W日志规范 | 6W Log Specification 6W日志规范 | design | design_only |
| 3 | D-SECURITY/AAAI 2026 FinJailbreak AAAI 2026金融越狱 | AAAI 2026 FinJailbreak AAAI 2026金融越狱 | design | design_only |
| 4 | D-SECURITY/ABAC策略引擎 ABAC Policy Engine | ABAC策略引擎 ABAC Policy Engine | design | design_only |
| 5 | D-SECURITY/ACLGuard 访问控制 | ACLGuard 访问控制 | design | design_only |
| 6 | D-SECURITY/AES-256-GCM AES-256-GCM加密 | AES-256-GCM AES-256-GCM加密 | design | design_only |
| 7 | D-SECURITY/AES-256加密 AES-256 Encryption | AES-256加密 AES-256 Encryption | design | design_only |
| 8 | D-SECURITY/AI Agent Dependency Sandbox AI Agent依赖沙箱 | AI Agent Dependency Sandbox AI Agent... | design | design_only |
| 9 | D-SECURITY/AI Agent Dependency Security Sandbox AI Agent... | AI Agent Dependency Security Sandbox ... | design | design_only |
| 10 | D-SECURITY/AI Code Modification Auditor AI代码修改审计器 | AI Code Modification Auditor AI代码修... | design | design_only |
| 11 | D-SECURITY/AI Construction Governor AI代码质量门控 | AI Construction Governor AI代码质量门控 | design | design_only |
| 12 | D-SECURITY/AI Driven Insider Trading Monitoring AI驱动内... | AI Driven Insider Trading Monitoring ... | design | design_only |
| 13 | D-SECURITY/AI Hallucination Package Name Guard AI幻觉包名... | AI Hallucination Package Name Guard A... | design | design_only |
| 14 | D-SECURITY/AI Read-Only Permission Executor AI只读权限执行器 | AI Read-Only Permission Executor AI只... | design | design_only |
| 15 | D-SECURITY/AI Writable Permission Controller AI可写权限控... | AI Writable Permission Controller AI... | design | design_only |
| 16 | D-SECURITY/AI-driven Automated Red Team AI驱动自动化红队 | AI-driven Automated Red Team AI驱动自... | design | design_only |
| 17 | D-SECURITY/AI-driven Insider Trading Monitoring 监控 | AI-driven Insider Trading Monitoring ... | design | design_only |
| 18 | D-SECURITY/AISGBlocked AISG门禁拦截 | AISGBlocked AISG门禁拦截 | design | design_only |
| 19 | D-SECURITY/AISGGate AISG拦截门禁 | AISGGate AISG拦截门禁 | design | design_only |
| 20 | D-SECURITY/AISG拦截门禁 AISG Intercept Gate | AISG拦截门禁 AISG Intercept Gate | design | design_only |
| 21 | D-SECURITY/AISG门禁与gateway.py关系 AISG Gate gateway.py ... | AISG门禁与gateway.py关系 AISG Gate ga... | design | design_only |
| 22 | D-SECURITY/AI_Agent | AI_Agent | design | design_only |
| 23 | D-SECURITY/AI脱敏管道 AI Desensitization Pipeline | AI脱敏管道 AI Desensitization Pipeline | design | design_only |
| 24 | D-SECURITY/AI驱动自动化红队 AI-driven Automated Red Team | AI驱动自动化红队 AI-driven Automated ... | design | design_only |
| 25 | D-SECURITY/API Security Gateway API安全网关 | API Security Gateway API安全网关 | design | design_only |
| 26 | D-SECURITY/AWS Agentic AI Security Scope Matrix 安全 | AWS Agentic AI Security Scope Matrix ... | design | design_only |
| 27 | D-SECURITY/AWS Bedrock AgentCore沙箱逃逸 AWS Bedrock Agen... | AWS Bedrock AgentCore沙箱逃逸 AWS Bed... | design | design_only |
| 28 | D-SECURITY/AWS Security Scope 2 AWS安全范围Scope 2 | AWS Security Scope 2 AWS安全范围Scope 2 | design | design_only |
| 29 | D-SECURITY/AWS Security Scope 4 AWS安全范围Scope 4 | AWS Security Scope 4 AWS安全范围Scope 4 | design | design_only |
| 30 | D-SECURITY/Abnormal Access Pattern Detection 异常访问模式... | Abnormal Access Pattern Detection 异... | design | design_only |
| 31 | D-SECURITY/Abnormal Profit Rate 异常盈利率 | Abnormal Profit Rate 异常盈利率 | design | design_only |
| 32 | D-SECURITY/Abnormal Profit 异常盈利检测 | Abnormal Profit 异常盈利检测 | design | design_only |
| 33 | D-SECURITY/Abnormal Trading Pattern Detection 异常交易模... | Abnormal Trading Pattern Detection 异... | design | design_only |
| 34 | D-SECURITY/Access Controller 访问控制器 | Access Controller 访问控制器 | design | design_only |
| 35 | D-SECURITY/Access Record 审计记录 | Access Record 审计记录 | design | design_only |
| 36 | D-SECURITY/Agent Alignment Checks Agent对齐检查 | Agent Alignment Checks Agent对齐检查 | design | design_only |
| 37 | D-SECURITY/Agent Behavior Baseline Learner Agent行为基线... | Agent Behavior Baseline Learner Agent... | design | design_only |
| 38 | D-SECURITY/Agent Cannot Impersonate Agent不可冒充其他Agent | Agent Cannot Impersonate Agent不可冒... | design | design_only |
| 39 | D-SECURITY/Agent Collusion Must Be Detected Agent串谋行为... | Agent Collusion Must Be Detected Agen... | design | design_only |
| 40 | D-SECURITY/Agent Communication Encryptor Agent间通信加密器 | Agent Communication Encryptor Agent间... | design | design_only |
| 41 | D-SECURITY/Agent Cryptographic Identity DID Ed25519 Agent... | Agent Cryptographic Identity DID Ed25... | design | design_only |
| 42 | D-SECURITY/Agent Emergent Behavior Must Be Detected Agent... | Agent Emergent Behavior Must Be Detec... | design | design_only |
| 43 | D-SECURITY/Agent Goal Hijack Agent目标劫持 | Agent Goal Hijack Agent目标劫持 | design | design_only |
| 44 | D-SECURITY/Agent Identity Non-Impersonation Agent身份不可... | Agent Identity Non-Impersonation Agen... | design | design_only |
| 45 | D-SECURITY/Agent Mesh Cryptographic Identity Agent Mesh密... | Agent Mesh Cryptographic Identity Age... | design | design_only |
| 46 | D-SECURITY/Agent Output Content Filter Agent输出内容过滤器 | Agent Output Content Filter Agent输出... | design | design_only |
| 47 | D-SECURITY/Agent Permission Dynamic Shrinker Agent权限动... | Agent Permission Dynamic Shrinker Age... | design | design_only |
| 48 | D-SECURITY/Agent Security Agent安全 | Agent Security Agent安全 | design | design_only |
| 49 | D-SECURITY/Agent Security Agent安全串谋/涌现/幻觉/记忆投毒 | Agent Security Agent安全串谋/涌现/幻... | design | design_only |
| 50 | D-SECURITY/Agent Security Module Agent安全模块 | Agent Security Module Agent安全模块 | design | design_only |
| 51 | D-SECURITY/AgentSandbox Agent沙箱隔离 | AgentSandbox Agent沙箱隔离 | design | design_only |
| 52 | D-SECURITY/Agentic Supply Chain Vulnerabilities Agent供应... | Agentic Supply Chain Vulnerabilities ... | design | design_only |
| 53 | D-SECURITY/Agent不可绕过安全检查 Agent No Bypass Security... | Agent不可绕过安全检查 Agent No Bypass... | design | design_only |
| 54 | D-SECURITY/Agent安全 Agent Security | Agent安全 Agent Security | design | design_only |
| 55 | D-SECURITY/Agent安全是独立关注点 Agent Security Independe... | Agent安全是独立关注点 Agent Security ... | design | design_only |
| 56 | D-SECURITY/Agent工具调用白名单 Agent Tool Call Whitelist | Agent工具调用白名单 Agent Tool Call W... | design | design_only |
| 57 | D-SECURITY/Agent持久化记忆写入验证 Agent Memory Write Val... | Agent持久化记忆写入验证 Agent Memory ... | design | design_only |
| 58 | D-SECURITY/Agent沙箱实例不可共享 Agent Sandbox No Sharing | Agent沙箱实例不可共享 Agent Sandbox N... | design | design_only |
| 59 | D-SECURITY/Agent漂移检测 Agent Drift Detection | Agent漂移检测 Agent Drift Detection | design | design_only |
| 60 | D-SECURITY/Agent预算上限 Agent Budget Limit | Agent预算上限 Agent Budget Limit | design | design_only |
| 61 | D-SECURITY/Agent预算不可超限 Agent Budget Limit | Agent预算不可超限 Agent Budget Limit | design | design_only |
| 62 | D-SECURITY/Application and API Layer 应用与API层 | Application and API Layer 应用与API层 | design | design_only |
| 63 | D-SECURITY/Attack Behavior Auto Blocker 攻击行为自动阻断器 | Attack Behavior Auto Blocker 攻击行为... | design | design_only |
| 64 | D-SECURITY/Attack Surface Simulator 攻击面模拟器 | Attack Surface Simulator 攻击面模拟器 | design | design_only |
| 65 | D-SECURITY/Audit Chain 审计链 | Audit Chain 审计链 | design | design_only |
| 66 | D-SECURITY/Audit Log Protector 审计日志保护器 | Audit Log Protector 审计日志保护器 | design | design_only |
| 67 | D-SECURITY/Audit Trail 不可变审计轨迹 | Audit Trail 不可变审计轨迹 | design | design_only |
| 68 | D-SECURITY/Authentication Failure Handler 认证失败处理器 | Authentication Failure Handler 认证失... | design | design_only |
| 69 | D-SECURITY/Auto Alert and Manual Review 自动告警与人工审查 | Auto Alert and Manual Review 自动告警... | design | design_only |
| 70 | D-SECURITY/BLACKICE Red Team Toolkit BLACKICE红队工具包 | BLACKICE Red Team Toolkit BLACKICE红... | design | design_only |
| 71 | D-SECURITY/BLACKICE 红队工具包 | BLACKICE 红队工具包 | design | design_only |
| 72 | D-SECURITY/Behavior Pattern Testing 行为模式测试 | Behavior Pattern Testing 行为模式测试 | design | design_only |
| 73 | D-SECURITY/Behavior Trajectory Similarity 行为轨迹相似度 | Behavior Trajectory Similarity 行为轨... | design | design_only |
| 74 | D-SECURITY/Blockchain Anchored Timestamp 区块链锚定时间戳 | Blockchain Anchored Timestamp 区块链... | design | design_only |
| 75 | D-SECURITY/Blockchain Anchoring 区块链锚定 | Blockchain Anchoring 区块链锚定 | design | design_only |
| 76 | D-SECURITY/CEO Annual Certification CEO年度认证 | CEO Annual Certification CEO年度认证 | design | design_only |
| 77 | D-SECURITY/Casbin RBAC Permission Controller Casbin RBAC... | Casbin RBAC Permission Controller Cas... | design | design_only |
| 78 | D-SECURITY/Cascading Failures 级联失败 | Cascading Failures 级联失败 | design | design_only |
| 79 | D-SECURITY/Cloud Security Alliance Agentic Trust Framewor... | Cloud Security Alliance Agentic Trust... | design | design_only |
| 80 | D-SECURITY/Code Security Auto Scanner 代码安全自动扫描器 | Code Security Auto Scanner 代码安全自... | design | design_only |
| 81 | D-SECURITY/CodeShield CodeShield代码盾 | CodeShield CodeShield代码盾 | design | design_only |
| 82 | D-SECURITY/Collective Score 核心 | Collective Score 核心 | design | design_only |
| 83 | D-SECURITY/Collusion Detection Threshold 串谋检测阈值 | Collusion Detection Threshold 串谋检... | design | design_only |
| 84 | D-SECURITY/Collusion Detection via Communication Pattern ... | Collusion Detection via Communication... | design | design_only |
| 85 | D-SECURITY/Collusion Pattern Simulation 串谋模式模拟 | Collusion Pattern Simulation 串谋模式... | design | design_only |
| 86 | D-SECURITY/CollusionDetected 共谋检测触发 | CollusionDetected 共谋检测触发 | design | design_only |
| 87 | D-SECURITY/CollusionDetection 串谋检测 | CollusionDetection 串谋检测 | design | design_only |
| 88 | D-SECURITY/Communication Security 通信安全 | Communication Security 通信安全 | design | design_only |
| 89 | D-SECURITY/Compliance Framework Comprehensive Benchmark ... | Compliance Framework Comprehensive Be... | design | design_only |
| 90 | D-SECURITY/Compliance Governance 合规与治理 | Compliance Governance 合规与治理 | design | design_only |
| 91 | D-SECURITY/Compliance Security Module Completion 合规安全... | Compliance Security Module Completion... | design | design_only |
| 92 | D-SECURITY/Confidence Scoring Mechanism 置信度评分机制 | Confidence Scoring Mechanism 置信度评... | design | design_only |
| 93 | D-SECURITY/Consistency Check 一致性检查 | Consistency Check 一致性检查 | design | design_only |
| 94 | D-SECURITY/Content Fingerprint Generator Verifier 内容指... | Content Fingerprint Generator Verifie... | design | design_only |
| 95 | D-SECURITY/Content Security 内容安全 | Content Security 内容安全 | design | design_only |
| 96 | D-SECURITY/Correlation 相关性 | Correlation 相关性 | design | design_only |
| 97 | D-SECURITY/Cross Wall Audit Chain 跨墙操作审计链 | Cross Wall Audit Chain 跨墙操作审计链 | design | design_only |
| 98 | D-SECURITY/Cross Wall End 跨墙结束 | Cross Wall End 跨墙结束 | design | design_only |
| 99 | D-SECURITY/Cross Wall Request 跨墙请求 | Cross Wall Request 跨墙请求 | design | design_only |
| 100 | D-SECURITY/Cross-wall Approval Procedure 跨墙审批流程 | Cross-wall Approval Procedure 跨墙审... | design | design_only |
| 101 | D-SECURITY/Crypto-Shredding Interface Crypto-Shredding接口 | Crypto-Shredding Interface Crypto-Shr... | design | design_only |
| 102 | D-SECURITY/Crypto-Shredding Key Destruction Restricted Cr... | Crypto-Shredding Key Destruction Rest... | design | design_only |
| 103 | D-SECURITY/Crypto-Shredding 加密粉碎 | Crypto-Shredding 加密粉碎 | design | design_only |
| 104 | D-SECURITY/Crypto-Shredding 密码粉碎 | Crypto-Shredding 密码粉碎 | design | design_only |
| 105 | D-SECURITY/D-SECURITY 安全 | D-SECURITY 安全 | design | design_only |
| 106 | D-SECURITY/D-SECURITY→D-AUTONOMY-CORE 安全域硬依赖自治核心 | D-SECURITY→D-AUTONOMY-CORE 安全域硬... | design | design_only |
| 107 | D-SECURITY/D-SECURITY→D-INFRA-RUNTIME 安全域软依赖运行时 | D-SECURITY→D-INFRA-RUNTIME 安全域软... | design | design_only |
| 108 | D-SECURITY/D-SECURITY→D-INTEGRATION 安全域软依赖集成域 | D-SECURITY→D-INTEGRATION 安全域软依... | design | design_only |
| 109 | D-SECURITY/DID Decentralized Identifier DID去中心化标识符 | DID Decentralized Identifier DID去中... | design | design_only |
| 110 | D-SECURITY/DLP Data Loss Prevention 事件 | DLP Data Loss Prevention 事件 | design | design_only |
| 111 | D-SECURITY/Daily Data Access Report 每日数据访问报告 | Daily Data Access Report 每日数据访问... | design | design_only |
| 112 | D-SECURITY/Data Access Audit 数据访问审计 | Data Access Audit 数据访问审计 | design | design_only |
| 113 | D-SECURITY/Data Access Controller 数据访问控制器 | Data Access Controller 数据访问控制器 | design | design_only |
| 114 | D-SECURITY/Data Classification Determination 数据分级判定 | Data Classification Determination 数... | design | design_only |
| 115 | D-SECURITY/Data Desensitization Engine 数据脱敏引擎 | Data Desensitization Engine 数据脱敏引擎 | design | design_only |
| 116 | D-SECURITY/Data Encryption and Masking Processor 数据加密... | Data Encryption and Masking Processor... | design | design_only |
| 117 | D-SECURITY/Data Layer 数据层 | Data Layer 数据层 | design | design_only |
| 118 | D-SECURITY/Data Masking & Privacy 数据脱敏与隐私 | Data Masking & Privacy 数据脱敏与隐私 | design | design_only |
| 119 | D-SECURITY/Data Protection 数据保护 | Data Protection 数据保护 | design | design_only |
| 120 | D-SECURITY/Data Source API Key Security Storage 数据源API... | Data Source API Key Security Storage ... | design | design_only |
| 121 | D-SECURITY/Deception Split 欺骗分割 | Deception Split 欺骗分割 | design | design_only |
| 122 | D-SECURITY/Defense in Depth 6 Layer 纵深防御6层 | Defense in Depth 6 Layer 纵深防御6层 | design | design_only |
| 123 | D-SECURITY/Defense in Depth 6 Layers 纵深防御6层 | Defense in Depth 6 Layers 纵深防御6层 | design | design_only |
| 124 | D-SECURITY/Dependency Behavior eBPF Monitor 依赖行为eBPF... | Dependency Behavior eBPF Monitor 依赖... | design | design_only |
| 125 | D-SECURITY/Dependency Graph ZK Proof 依赖图ZK证明 | Dependency Graph ZK Proof 依赖图ZK证明 | design | design_only |
| 126 | D-SECURITY/Dependency Penetration Mapper 依赖穿透映射器 | Dependency Penetration Mapper 依赖穿... | design | design_only |
| 127 | D-SECURITY/Dependency Vulnerability Auto Detector 依赖漏... | Dependency Vulnerability Auto Detecto... | design | design_only |
| 128 | D-SECURITY/Deutsche Bank AI Compliance 德意志银行AI合规监控 | Deutsche Bank AI Compliance 德意志银... | design | design_only |
| 129 | D-SECURITY/Direct Exclusive Control 直接且独占的控制权 | Direct Exclusive Control 直接且独占的... | design | design_only |
| 130 | D-SECURITY/Docker Container Docker容器 | Docker Container Docker容器 | design | design_only |
| 131 | D-SECURITY/Dynamic Permission Allocation 动态权限分配 | Dynamic Permission Allocation 动态权... | design | design_only |
| 132 | D-SECURITY/E2B沙箱 E2B Sandbox | E2B沙箱 E2B Sandbox | design | design_only |
| 133 | D-SECURITY/EncryptionKeyRotated 密钥轮换完成 | EncryptionKeyRotated 密钥轮换完成 | design | design_only |
| 134 | D-SECURITY/End-to-End Data Encryption and Access Controll... | End-to-End Data Encryption and Access... | design | design_only |
| 135 | D-SECURITY/Ensemble 集成 | Ensemble 集成 | design | design_only |
| 136 | D-SECURITY/Error Duplicate Order Control 错误/重复订单控制 | Error Duplicate Order Control 错误/重... | design | design_only |
| 137 | D-SECURITY/Ethical Wall 信息隔离墙 | Ethical Wall 信息隔离墙 | design | design_only |
| 138 | D-SECURITY/FCFT金融宪法微调 FCFT Financial Constitution F... | FCFT金融宪法微调 FCFT Financial Const... | design | design_only |
| 139 | D-SECURITY/FHE Fully Homomorphic Encryption 全量 | FHE Fully Homomorphic Encryption 全量 | design | design_only |
| 140 | D-SECURITY/FL Federated Learning FL联邦学习 | FL Federated Learning FL联邦学习 | design | design_only |
| 141 | D-SECURITY/Fact Checking 事实核查 | Fact Checking 事实核查 | design | design_only |
| 142 | D-SECURITY/Fail-Closed Policy Manager 失败关闭策略管理器 | Fail-Closed Policy Manager 失败关闭策... | design | design_only |
| 143 | D-SECURITY/Financial Constitution Fine-Tuning 金融宪法微调 | Financial Constitution Fine-Tuning 金... | design | design_only |
| 144 | D-SECURITY/Financial Security Compliance Checker 金融安全... | Financial Security Compliance Checker... | design | design_only |
| 145 | D-SECURITY/Firecracker microVM Firecracker微虚拟机 | Firecracker microVM Firecracker微虚拟机 | design | design_only |
| 146 | D-SECURITY/Firecracker microVM Sandbox Isolation Firecrac... | Firecracker microVM Sandbox Isolation... | design | design_only |
| 147 | D-SECURITY/Formal Verification形式化验证 Formal Verification | Formal Verification形式化验证 Formal ... | design | design_only |
| 148 | D-SECURITY/GATE-PQC 纯PQC模式门禁 | GATE-PQC 纯PQC模式门禁 | design | design_only |
| 149 | D-SECURITY/GATE-SOC2 SOC 2认证汇总 | GATE-SOC2 SOC 2认证汇总 | design | design_only |
| 150 | D-SECURITY/GATE-SOC2-01 第三方服务 | GATE-SOC2-01 第三方服务 | design | design_only |
| 151 | D-SECURITY/GATE-SOC2-02 资金规模 | GATE-SOC2-02 资金规模 | design | design_only |
| 152 | D-SECURITY/GATE-SOC2-03 审计观察期 | GATE-SOC2-03 审计观察期 | design | design_only |
| 153 | D-SECURITY/Gap Ratio 缺口比率 | Gap Ratio 缺口比率 | design | design_only |
| 154 | D-SECURITY/Goal Drift Detection 目标漂移检测 | Goal Drift Detection 目标漂移检测 | design | design_only |
| 155 | D-SECURITY/Goldman Sachs Agentic AI 高盛Agentic AI合规工具 | Goldman Sachs Agentic AI 高盛Agentic ... | design | design_only |
| 156 | D-SECURITY/Graph 图谱 | Graph 图谱 | design | design_only |
| 157 | D-SECURITY/Hard Boundary HB-SEC-01~13 硬边界 | Hard Boundary HB-SEC-01~13 硬边界 | design | design_only |
| 158 | D-SECURITY/Host and OS Layer 主机与操作系统层 | Host and OS Layer 主机与操作系统层 | design | design_only |
| 159 | D-SECURITY/Human-Agent Trust Exploitation 人机信任利用 | Human-Agent Trust Exploitation 人机信... | design | design_only |
| 160 | D-SECURITY/IAM Access Control IAM与访问控制 | IAM Access Control IAM与访问控制 | design | design_only |
| 161 | D-SECURITY/IAM与访问控制 IAM and Access Control | IAM与访问控制 IAM and Access Control | design | design_only |
| 162 | D-SECURITY/IAM仍然重要 IAM Still Important | IAM仍然重要 IAM Still Important | design | design_only |
| 163 | D-SECURITY/IP Whitelist Manager IP白名单管理 | IP Whitelist Manager IP白名单管理 | design | design_only |
| 164 | D-SECURITY/ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 | ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 | design | design_only |
| 165 | D-SECURITY/Identity & Access Manager 身份与访问管理器 | Identity & Access Manager 身份与访问... | design | design_only |
| 166 | D-SECURITY/Identity Access 身份与访问 | Identity Access 身份与访问 | design | design_only |
| 167 | D-SECURITY/Identity Privilege Abuse 身份与权限滥用 | Identity Privilege Abuse 身份与权限滥用 | design | design_only |
| 168 | D-SECURITY/Identity Rotation and Anonymization 身份轮换与... | Identity Rotation and Anonymization ... | design | design_only |
| 169 | D-SECURITY/Identity and Access Layer 身份与访问层 | Identity and Access Layer 身份与访问层 | design | design_only |
| 170 | D-SECURITY/Info Trading Time Lag 信息-交易时滞 | Info Trading Time Lag 信息-交易时滞 | design | design_only |
| 171 | D-SECURITY/Input Detection/Auth/Scan 输入检测/认证/扫描等 | Input Detection/Auth/Scan 输入检测/认... | design | design_only |
| 172 | D-SECURITY/Input Provenance Tagging 标签 | Input Provenance Tagging 标签 | design | design_only |
| 173 | D-SECURITY/InputOutputGuard 输入输出防护 | InputOutputGuard 输入输出防护 | design | design_only |
| 174 | D-SECURITY/Insecure Inter-Agent Communication 不安全Agent... | Insecure Inter-Agent Communication 不... | design | design_only |
| 175 | D-SECURITY/Insider Trading Prevention 内幕交易防护 | Insider Trading Prevention 内幕交易防护 | design | design_only |
| 176 | D-SECURITY/Insider Trading Protection 内幕交易防护 | Insider Trading Protection 内幕交易防护 | design | design_only |
| 177 | D-SECURITY/IntegrityViolation 完整性违规 | IntegrityViolation 完整性违规 | design | design_only |
| 178 | D-SECURITY/Invariant Labs MCP工具投毒 Invariant Labs MCP ... | Invariant Labs MCP工具投毒 Invariant ... | design | design_only |
| 179 | D-SECURITY/KILLSWITCH.md标准化 KILLSWITCH Standardization | KILLSWITCH.md标准化 KILLSWITCH Standa... | design | design_only |
| 180 | D-SECURITY/Key Destruction 密钥销毁 | Key Destruction 密钥销毁 | design | design_only |
| 181 | D-SECURITY/Key Hierarchy Management 密钥层级管理 | Key Hierarchy Management 密钥层级管理 | design | design_only |
| 182 | D-SECURITY/Key Layer Management 密钥层级管理 | Key Layer Management 密钥层级管理 | design | design_only |
| 183 | D-SECURITY/KeySecretManager 密钥管理 | KeySecretManager 密钥管理 | design | design_only |
| 184 | D-SECURITY/Kill Switch 15c3-5 Kill Switch市场接入 | Kill Switch 15c3-5 Kill Switch市场接入 | design | design_only |
| 185 | D-SECURITY/Kill Switch Five Layer Defense Kill Switch五层... | Kill Switch Five Layer Defense Kill S... | design | design_only |
| 186 | D-SECURITY/Kill Switch Infrastructure Layer OWASP ASI08 K... | Kill Switch Infrastructure Layer OWAS... | design | design_only |
| 187 | D-SECURITY/Kill Switch Invariant Kill Switch不变量 | Kill Switch Invariant Kill Switch不变量 | design | design_only |
| 188 | D-SECURITY/Kill Switch 紧急停机开关 | Kill Switch 紧急停机开关 | design | design_only |
| 189 | D-SECURITY/Knowledge Access Control 知识访问控制 | Knowledge Access Control 知识访问控制 | design | design_only |
| 190 | D-SECURITY/L0 Supply Chain SHA256 Verifier L0供应链SHA256... | L0 Supply Chain SHA256 Verifier L0供... | design | design_only |
| 191 | D-SECURITY/L2 Auto Approval L2自动审批 | L2 Auto Approval L2自动审批 | design | design_only |
| 192 | D-SECURITY/L2 L3 Data Access Audit L2/L3数据访问审计 | L2 L3 Data Access Audit L2/L3数据访问... | design | design_only |
| 193 | D-SECURITY/L3 Manual Approval L3人工审批 | L3 Manual Approval L3人工审批 | design | design_only |
| 194 | D-SECURITY/L4 Agent Security Permission Isolator L4 Agent... | L4 Agent Security Permission Isolator... | design | design_only |
| 195 | D-SECURITY/LLM Guardrails MCP Triple Gate LLM guardrails+... | LLM Guardrails MCP Triple Gate LLM gu... | design | design_only |
| 196 | D-SECURITY/LLM Pentesting 5-layer Methodology LLM渗透测试... | LLM Pentesting 5-layer Methodology LL... | design | design_only |
| 197 | D-SECURITY/LLM Pentesting 5层方法论 LLM Pentesting 5-laye... | LLM Pentesting 5层方法论 LLM Pentesti... | design | design_only |
| 198 | D-SECURITY/LLM Security Gateway LLM安全网关 | LLM Security Gateway LLM安全网关 | design | design_only |
| 199 | D-SECURITY/LLM Security LLM安全网关 | LLM Security LLM安全网关 | design | design_only |
| 200 | D-SECURITY/LLM调用脱敏 LLM Call Desensitization | LLM调用脱敏 LLM Call Desensitization | design | design_only |

> (仅显示前 200 个模块，共 575 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 844 条 / 844 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 844 条 / 844 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 703 条 / edges                               │
│   [config_depends]: 49 条 / edges                                │
│   [event]: 26 条 / edges                                         │
│   [contract]: 26 条 / edges                                      │
│   [runtime]: 26 条 / edges                                       │
│   [data]: 14 条 / edges                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (703 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → __init__.py                                      │
│   __init__.py → __init__.py                                      │
│   all_completer.py → models.py                                   │
│   alignment_syncer.py → models.py                                │
│   compliance_auditor.py → models.py                              │
│   batch_fixer.py → fix_budget.py                                 │
│   batch_fixer.py → fix_reliability.py                            │
│   batch_fixer.py → models.py                                     │
│   config_fixer.py → models.py                                    │
│   dep_version_fixer.py → models.py                               │
│   engine.py → compliance_auditor.py                              │
│   engine.py → batch_fixer.py                                     │
│   engine.py → escalation_bridge.py                               │
│   engine.py → fix_diff.py                                        │
│   engine.py → fix_pattern_miner.py                               │
│   engine.py → fix_budget.py                                      │
│   engine.py → fix_reliability.py                                 │
│   engine.py → fix_health_check.py                                │
│   engine.py → fix_safety.py                                      │
│   engine.py → fix_report.py                                      │
│   engine.py → models.py                                          │
│   engine.py → shadow_workspace.py                                │
│   engine.py → state_machine.py                                   │
│   escalation_bridge.py → models.py                               │
│   drift_fixer.py → models.py                                     │
│   dedup_extractor.py → models.py                                 │
│   fix_diff.py → models.py                                        │
│   fix_pattern_miner.py → models.py                               │
│   fix_budget.py → models.py                                      │
│   event_hooks.py → models.py                                     │
│   fix_reliability.py → models.py                                 │
│   fix_health_check.py → models.py                                │
│   fix_safety.py → models.py                                      │
│   fix_report.py → models.py                                      │
│   import_fixer.py → models.py                                    │
│   fix_scheduler.py → models.py                                   │
│   llm_fix_adapter.py → fix_safety.py                             │
│   llm_fix_adapter.py → models.py                                 │
│   scaffold_registrar.py → models.py                              │
│   self_heal_agent.py → models.py                                 │
│   shadow_workspace.py → models.py                                │
│   __init__.py → all_completer.py                                 │
│   __init__.py → alignment_syncer.py                              │
│   __init__.py → compliance_auditor.py                            │
│   __init__.py → batch_fixer.py                                   │
│   __init__.py → config_fixer.py                                  │
│   __init__.py → dep_version_fixer.py                             │
│   __init__.py → engine.py                                        │
│   __init__.py → escalation_bridge.py                             │
│   ...还有 654 条 / 654 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (49 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (26 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (26 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (26 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (14 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 844 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `14_d_security_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
