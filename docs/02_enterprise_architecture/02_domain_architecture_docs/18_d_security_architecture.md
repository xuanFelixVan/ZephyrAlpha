---
doc_type: domain_architecture_diagram
title: D-SECURITY 对抗验证架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 18_d_security / 对抗验证 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示对抗验证（D-SECURITY）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:21
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 对抗验证（D-SECURITY）的模块分布。共 276 个模块 / 276 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (272 modules)            │
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
│   src/zephyr/security/_extensions/__init__.py  [prototype]       │
│   src/zephyr/security/access_control/__init__.py  [production]   │
│   ...还有 254 个模块 / 254 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (4 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F16-orphan-judge/  [design]                                    │
│   F30-red-blue/  [design]                                        │
│   F7-llm-gateway/  [design]                                      │
│   F8-rbac/  [design]                                             │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 276 个模块 / 276 modules）。

### L1 基础层 / Foundation Layer (272 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/behavioral_audit/__init__.py | src/zephyr/behavioral_audit/__init__.py | prototype | generated |
| 2 | src/zephyr/behavioral_audit/__main__.py | src/zephyr/behavioral_audit/__main__.py | prototype | generated |
| 3 | src/zephyr/behavioral_audit/_analysis.py | src/zephyr/behavioral_audit/_analysis.py | prototype | generated |
| 4 | src/zephyr/behavioral_audit/_core.py | src/zephyr/behavioral_audit/_core.py | prototype | generated |
| 5 | src/zephyr/behavioral_audit/_drift.py | src/zephyr/behavioral_audit/_drift.py | prototype | generated |
| 6 | src/zephyr/behavioral_audit/_infrastructure.py | src/zephyr/behavioral_audit/_infrastr... | prototype | generated |
| 7 | src/zephyr/behavioral_audit/_scanners.py | src/zephyr/behavioral_audit/_scanners.py | prototype | generated |
| 8 | src/zephyr/behavioral_audit/alert_router.py | src/zephyr/behavioral_audit/alert_rou... | prototype | generated |
| 9 | src/zephyr/behavioral_audit/cold_start.py | src/zephyr/behavioral_audit/cold_star... | prototype | generated |
| 10 | src/zephyr/behavioral_audit/data_quality.py | src/zephyr/behavioral_audit/data_qual... | prototype | generated |
| 11 | src/zephyr/behavioral_audit/events.py | src/zephyr/behavioral_audit/events.py | prototype | generated |
| 12 | src/zephyr/behavioral_audit/integration_test_runner.py | src/zephyr/behavioral_audit/integrati... | prototype | generated |
| 13 | src/zephyr/behavioral_audit/reconciler.py | src/zephyr/behavioral_audit/reconcile... | prototype | generated |
| 14 | src/zephyr/behavioral_audit/runbook_generator.py | src/zephyr/behavioral_audit/runbook_g... | prototype | generated |
| 15 | src/zephyr/behavioral_audit/state_machine.py | src/zephyr/behavioral_audit/state_mac... | prototype | generated |
| 16 | src/zephyr/security/__init__.py | src/zephyr/security/__init__.py | prototype | generated |
| 17 | src/zephyr/security/_extensions/__init__.py | src/zephyr/security/_extensions/__ini... | prototype | deprecated |
| 18 | src/zephyr/security/access_control/__init__.py | src/zephyr/security/access_control/__... | production | stable |
| 19 | src/zephyr/security/access_control/a2a_check.py | src/zephyr/security/access_control/a2... | production | stable |
| 20 | src/zephyr/security/access_control/abac_guard.py | src/zephyr/security/access_control/ab... | production | stable |
| 21 | src/zephyr/security/access_control/adversarial_resilience.py | src/zephyr/security/access_control/ad... | production | stable |
| 22 | src/zephyr/security/access_control/agent_creation_policy.py | src/zephyr/security/access_control/ag... | production | stable |
| 23 | src/zephyr/security/access_control/anomaly_detector.py | src/zephyr/security/access_control/an... | production | stable |
| 24 | src/zephyr/security/access_control/anti_pattern_guard.py | src/zephyr/security/access_control/an... | production | stable |
| 25 | src/zephyr/security/access_control/approver_check.py | src/zephyr/security/access_control/ap... | production | stable |
| 26 | src/zephyr/security/access_control/asymmetric_audit.py | src/zephyr/security/access_control/as... | production | stable |
| 27 | src/zephyr/security/access_control/audit_log_guard.py | src/zephyr/security/access_control/au... | production | stable |
| 28 | src/zephyr/security/access_control/auto_fix_engine_03/__i... | src/zephyr/security/access_control/au... | prototype | stable |
| 29 | src/zephyr/security/access_control/auto_fix_engine_03/__m... | src/zephyr/security/access_control/au... | prototype | stable |
| 30 | src/zephyr/security/access_control/auto_fix_engine_03/ali... | src/zephyr/security/access_control/au... | prototype | stable |
| 31 | src/zephyr/security/access_control/auto_fix_engine_03/all... | src/zephyr/security/access_control/au... | prototype | stable |
| 32 | src/zephyr/security/access_control/auto_fix_engine_03/bat... | src/zephyr/security/access_control/au... | prototype | stable |
| 33 | src/zephyr/security/access_control/auto_fix_engine_03/com... | src/zephyr/security/access_control/au... | prototype | stable |
| 34 | src/zephyr/security/access_control/auto_fix_engine_03/con... | src/zephyr/security/access_control/au... | prototype | stable |
| 35 | src/zephyr/security/access_control/auto_fix_engine_03/ded... | src/zephyr/security/access_control/au... | prototype | stable |
| 36 | src/zephyr/security/access_control/auto_fix_engine_03/dep... | src/zephyr/security/access_control/au... | production | stable |
| 37 | src/zephyr/security/access_control/auto_fix_engine_03/dri... | src/zephyr/security/access_control/au... | production | stable |
| 38 | src/zephyr/security/access_control/auto_fix_engine_03/eng... | src/zephyr/security/access_control/au... | production | stable |
| 39 | src/zephyr/security/access_control/auto_fix_engine_03/esc... | src/zephyr/security/access_control/au... | production | stable |
| 40 | src/zephyr/security/access_control/auto_fix_engine_03/eve... | src/zephyr/security/access_control/au... | production | stable |
| 41 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 42 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 43 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 44 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 45 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 46 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 47 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 48 | src/zephyr/security/access_control/auto_fix_engine_03/fix... | src/zephyr/security/access_control/au... | production | stable |
| 49 | src/zephyr/security/access_control/auto_fix_engine_03/imp... | src/zephyr/security/access_control/au... | prototype | stable |
| 50 | src/zephyr/security/access_control/auto_fix_engine_03/int... | src/zephyr/security/access_control/au... | production | stable |
| 51 | src/zephyr/security/access_control/auto_fix_engine_03/llm... | src/zephyr/security/access_control/au... | production | stable |
| 52 | src/zephyr/security/access_control/auto_fix_engine_03/mod... | src/zephyr/security/access_control/au... | production | stable |
| 53 | src/zephyr/security/access_control/auto_fix_engine_03/sca... | src/zephyr/security/access_control/au... | production | stable |
| 54 | src/zephyr/security/access_control/auto_fix_engine_03/sel... | src/zephyr/security/access_control/au... | production | stable |
| 55 | src/zephyr/security/access_control/auto_fix_engine_03/sha... | src/zephyr/security/access_control/au... | production | stable |
| 56 | src/zephyr/security/access_control/auto_fix_engine_03/sta... | src/zephyr/security/access_control/au... | production | stable |
| 57 | src/zephyr/security/access_control/auto_fix_engine_03/zom... | src/zephyr/security/access_control/au... | production | stable |
| 58 | src/zephyr/security/access_control/auto_maintenance.py | src/zephyr/security/access_control/au... | production | stable |
| 59 | src/zephyr/security/access_control/blind_spot_tracker.py | src/zephyr/security/access_control/bl... | production | stable |
| 60 | src/zephyr/security/access_control/blueprint_fidelity.py | src/zephyr/security/access_control/bl... | production | stable |
| 61 | src/zephyr/security/access_control/bootstrap_superadmin.py | src/zephyr/security/access_control/bo... | production | stable |
| 62 | src/zephyr/security/access_control/bootstrap_verifier.py | src/zephyr/security/access_control/bo... | production | stable |
| 63 | src/zephyr/security/access_control/build_sanitizer.py | src/zephyr/security/access_control/bu... | production | stable |
| 64 | src/zephyr/security/access_control/cache_invalidation.py | src/zephyr/security/access_control/ca... | production | stable |
| 65 | src/zephyr/security/access_control/canary_rollout_manager.py | src/zephyr/security/access_control/ca... | production | stable |
| 66 | src/zephyr/security/access_control/capability_check.py | src/zephyr/security/access_control/ca... | production | stable |
| 67 | src/zephyr/security/access_control/cascading_failure_isol... | src/zephyr/security/access_control/ca... | production | stable |
| 68 | src/zephyr/security/access_control/cold_start_lock.py | src/zephyr/security/access_control/co... | production | stable |
| 69 | src/zephyr/security/access_control/compliance_matrix.py | src/zephyr/security/access_control/co... | production | stable |
| 70 | src/zephyr/security/access_control/context_drift_detector.py | src/zephyr/security/access_control/co... | production | stable |
| 71 | src/zephyr/security/access_control/continuous_verifier.py | src/zephyr/security/access_control/co... | production | stable |
| 72 | src/zephyr/security/access_control/contract_verifier.py | src/zephyr/security/access_control/co... | production | stable |
| 73 | src/zephyr/security/access_control/contracts.py | src/zephyr/security/access_control/co... | production | stable |
| 74 | src/zephyr/security/access_control/cross_cutting.py | src/zephyr/security/access_control/cr... | production | stable |
| 75 | src/zephyr/security/access_control/cross_session_detector.py | src/zephyr/security/access_control/cr... | production | stable |
| 76 | src/zephyr/security/access_control/cybersec_2026_guard.py | src/zephyr/security/access_control/cy... | production | stable |
| 77 | src/zephyr/security/access_control/decision_explainer.py | src/zephyr/security/access_control/de... | production | stable |
| 78 | src/zephyr/security/access_control/decision_registry.py | src/zephyr/security/access_control/de... | production | stable |
| 79 | src/zephyr/security/access_control/defense_depth.py | src/zephyr/security/access_control/de... | production | stable |
| 80 | src/zephyr/security/access_control/dependency_auditor.py | src/zephyr/security/access_control/de... | production | stable |
| 81 | src/zephyr/security/access_control/derive_rbac_roles.py | src/zephyr/security/access_control/de... | production | stable |
| 82 | src/zephyr/security/access_control/dry_run.py | src/zephyr/security/access_control/dr... | production | stable |
| 83 | src/zephyr/security/access_control/emergency_override.py | src/zephyr/security/access_control/em... | production | stable |
| 84 | src/zephyr/security/access_control/engine_degradation.py | src/zephyr/security/access_control/en... | production | stable |
| 85 | src/zephyr/security/access_control/environment_manager.py | src/zephyr/security/access_control/en... | production | stable |
| 86 | src/zephyr/security/access_control/escalation_handler.py | src/zephyr/security/access_control/es... | production | stable |
| 87 | src/zephyr/security/access_control/exceptions.py | src/zephyr/security/access_control/ex... | production | stable |
| 88 | src/zephyr/security/access_control/false_completion_detec... | src/zephyr/security/access_control/fa... | production | stable |
| 89 | src/zephyr/security/access_control/genesis_bootstrap.py | src/zephyr/security/access_control/ge... | production | stable |
| 90 | src/zephyr/security/access_control/guard_layers.py | src/zephyr/security/access_control/gu... | production | stable |
| 91 | src/zephyr/security/access_control/identity.py | src/zephyr/security/access_control/id... | production | stable |
| 92 | src/zephyr/security/access_control/immutable_core.py | src/zephyr/security/access_control/im... | production | stable |
| 93 | src/zephyr/security/access_control/input_guard.py | src/zephyr/security/access_control/in... | production | stable |
| 94 | src/zephyr/security/access_control/integration.py | src/zephyr/security/access_control/in... | production | stable |
| 95 | src/zephyr/security/access_control/integrity_self_check.py | src/zephyr/security/access_control/in... | production | stable |
| 96 | src/zephyr/security/access_control/intent_binder.py | src/zephyr/security/access_control/in... | production | stable |
| 97 | src/zephyr/security/access_control/key_hierarchy.py | src/zephyr/security/access_control/ke... | production | stable |
| 98 | src/zephyr/security/access_control/kill_switch.py | src/zephyr/security/access_control/ki... | production | stable |
| 99 | src/zephyr/security/access_control/legal_audit_chain.py | src/zephyr/security/access_control/le... | production | stable |
| 100 | src/zephyr/security/access_control/memory_guard.py | src/zephyr/security/access_control/me... | production | stable |
| 101 | src/zephyr/security/access_control/memory_provenance_guar... | src/zephyr/security/access_control/me... | production | stable |
| 102 | src/zephyr/security/access_control/micro_verifier.py | src/zephyr/security/access_control/mi... | production | stable |
| 103 | src/zephyr/security/access_control/microstructure_defense.py | src/zephyr/security/access_control/mi... | production | stable |
| 104 | src/zephyr/security/access_control/monotonic_clock.py | src/zephyr/security/access_control/mo... | production | stable |
| 105 | src/zephyr/security/access_control/multi_agent_collusion_... | src/zephyr/security/access_control/mu... | production | stable |
| 106 | src/zephyr/security/access_control/native_api_guard.py | src/zephyr/security/access_control/na... | production | stable |
| 107 | src/zephyr/security/access_control/non_repudiation.py | src/zephyr/security/access_control/no... | production | stable |
| 108 | src/zephyr/security/access_control/novel_attack_guard.py | src/zephyr/security/access_control/no... | production | stable |
| 109 | src/zephyr/security/access_control/observability.py | src/zephyr/security/access_control/ob... | production | stable |
| 110 | src/zephyr/security/access_control/orphan_judge/__init__.py | src/zephyr/security/access_control/or... | prototype | stable |
| 111 | src/zephyr/security/access_control/orphan_judge/__main__.py | src/zephyr/security/access_control/or... | prototype | stable |
| 112 | src/zephyr/security/access_control/orphan_judge/cascade_a... | src/zephyr/security/access_control/or... | production | stable |
| 113 | src/zephyr/security/access_control/orphan_judge/config_lo... | src/zephyr/security/access_control/or... | prototype | stable |
| 114 | src/zephyr/security/access_control/orphan_judge/db.py | src/zephyr/security/access_control/or... | prototype | stable |
| 115 | src/zephyr/security/access_control/orphan_judge/decision_... | src/zephyr/security/access_control/or... | production | stable |
| 116 | src/zephyr/security/access_control/orphan_judge/deprecati... | src/zephyr/security/access_control/or... | production | stable |
| 117 | src/zephyr/security/access_control/orphan_judge/drift_bri... | src/zephyr/security/access_control/or... | prototype | stable |
| 118 | src/zephyr/security/access_control/orphan_judge/duplicate... | src/zephyr/security/access_control/or... | prototype | stable |
| 119 | src/zephyr/security/access_control/orphan_judge/escalatio... | src/zephyr/security/access_control/or... | prototype | stable |
| 120 | src/zephyr/security/access_control/orphan_judge/feedback_... | src/zephyr/security/access_control/or... | prototype | stable |
| 121 | src/zephyr/security/access_control/orphan_judge/judge.py | src/zephyr/security/access_control/or... | production | stable |
| 122 | src/zephyr/security/access_control/orphan_judge/kb_bridge.py | src/zephyr/security/access_control/or... | prototype | stable |
| 123 | src/zephyr/security/access_control/orphan_judge/mcp_integ... | src/zephyr/security/access_control/or... | prototype | stable |
| 124 | src/zephyr/security/access_control/orphan_judge/models.py | src/zephyr/security/access_control/or... | prototype | stable |
| 125 | src/zephyr/security/access_control/orphan_judge/orphan_co... | src/zephyr/security/access_control/or... | prototype | stable |
| 126 | src/zephyr/security/access_control/orphan_judge/orphan_de... | src/zephyr/security/access_control/or... | production | stable |
| 127 | src/zephyr/security/access_control/orphan_judge/rbac_brid... | src/zephyr/security/access_control/or... | prototype | stable |
| 128 | src/zephyr/security/access_control/orphan_judge/reference... | src/zephyr/security/access_control/or... | prototype | stable |
| 129 | src/zephyr/security/access_control/orphan_judge/registrat... | src/zephyr/security/access_control/or... | prototype | stable |
| 130 | src/zephyr/security/access_control/orphan_judge/report_ge... | src/zephyr/security/access_control/or... | prototype | stable |
| 131 | src/zephyr/security/access_control/orphan_judge/safety_fe... | src/zephyr/security/access_control/or... | production | stable |
| 132 | src/zephyr/security/access_control/orphan_judge/standalon... | src/zephyr/security/access_control/or... | prototype | stable |
| 133 | src/zephyr/security/access_control/orphan_judge/swid_tag.py | src/zephyr/security/access_control/or... | prototype | stable |
| 134 | src/zephyr/security/access_control/orphan_judge/unique_an... | src/zephyr/security/access_control/or... | prototype | stable |
| 135 | src/zephyr/security/access_control/output_guard.py | src/zephyr/security/access_control/ou... | production | stable |
| 136 | src/zephyr/security/access_control/path_guard.py | src/zephyr/security/access_control/pa... | production | stable |
| 137 | src/zephyr/security/access_control/permission_guard.py | src/zephyr/security/access_control/pe... | production | stable |
| 138 | src/zephyr/security/access_control/permission_hooks.py | src/zephyr/security/access_control/pe... | production | stable |
| 139 | src/zephyr/security/access_control/permission_mode_manage... | src/zephyr/security/access_control/pe... | production | stable |
| 140 | src/zephyr/security/access_control/phase_executor.py | src/zephyr/security/access_control/ph... | prototype | stable |
| 141 | src/zephyr/security/access_control/post_action_verifier.py | src/zephyr/security/access_control/po... | production | stable |
| 142 | src/zephyr/security/access_control/rbac_guard.py | src/zephyr/security/access_control/rb... | production | stable |
| 143 | src/zephyr/security/access_control/replay_attack_guard.py | src/zephyr/security/access_control/re... | production | stable |
| 144 | src/zephyr/security/access_control/risk_mitigation.py | src/zephyr/security/access_control/ri... | production | stable |
| 145 | src/zephyr/security/access_control/rollback_sandbox.py | src/zephyr/security/access_control/ro... | production | stable |
| 146 | src/zephyr/security/access_control/rule_injection_guard.py | src/zephyr/security/access_control/ru... | production | stable |
| 147 | src/zephyr/security/access_control/secrets_lifecycle.py | src/zephyr/security/access_control/se... | production | stable |
| 148 | src/zephyr/security/access_control/sequence_guard.py | src/zephyr/security/access_control/se... | production | stable |
| 149 | src/zephyr/security/access_control/session_concurrency.py | src/zephyr/security/access_control/se... | production | stable |
| 150 | src/zephyr/security/access_control/session_lifecycle.py | src/zephyr/security/access_control/se... | production | stable |
| 151 | src/zephyr/security/access_control/shell_dialect_detector.py | src/zephyr/security/access_control/sh... | production | stable |
| 152 | src/zephyr/security/access_control/toctou_guard.py | src/zephyr/security/access_control/to... | production | stable |
| 153 | src/zephyr/security/access_control/vibe_coding_guard.py | src/zephyr/security/access_control/vi... | production | stable |
| 154 | src/zephyr/security/adversarial_validation/__init__.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 155 | src/zephyr/security/adversarial_validation/__main__.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 156 | src/zephyr/security/adversarial_validation/ai_attack_gene... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 157 | src/zephyr/security/adversarial_validation/async_monitor.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 158 | src/zephyr/security/adversarial_validation/attack_registr... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 159 | src/zephyr/security/adversarial_validation/blast_radius.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 160 | src/zephyr/security/adversarial_validation/bypass_recorde... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 161 | src/zephyr/security/adversarial_validation/circuit_breake... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 162 | src/zephyr/security/adversarial_validation/cleanup.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 163 | src/zephyr/security/adversarial_validation/cli.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 164 | src/zephyr/security/adversarial_validation/cold_start.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 165 | src/zephyr/security/adversarial_validation/constitution_e... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 166 | src/zephyr/security/adversarial_validation/constitution_g... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 167 | src/zephyr/security/adversarial_validation/convergence_ch... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 168 | src/zephyr/security/adversarial_validation/defense_runner.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 169 | src/zephyr/security/adversarial_validation/game_day_runne... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 170 | src/zephyr/security/adversarial_validation/game_day_sched... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 171 | src/zephyr/security/adversarial_validation/injection_engi... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 172 | src/zephyr/security/adversarial_validation/mcp_endpoints.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 173 | src/zephyr/security/adversarial_validation/models.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 174 | src/zephyr/security/adversarial_validation/scenario_loade... | src/zephyr/security/adversarial_valid... | prototype | generated |
| 175 | src/zephyr/security/adversarial_validation/steady_state.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 176 | src/zephyr/security/adversarial_validation/validator.py | src/zephyr/security/adversarial_valid... | prototype | generated |
| 177 | src/zephyr/security/api/__init__.py | src/zephyr/security/api/__init__.py | prototype | deprecated |
| 178 | src/zephyr/security/core/__init__.py | src/zephyr/security/core/__init__.py | prototype | deprecated |
| 179 | src/zephyr/security/infrastructure/__init__.py | src/zephyr/security/infrastructure/__... | prototype | deprecated |
| 180 | src/zephyr/security/llm_defense/__init__.py | src/zephyr/security/llm_defense/__ini... | prototype | deprecated |
| 181 | src/zephyr/security/llm_defense/llm_security/__init__.py | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 182 | src/zephyr/security/llm_defense/llm_security/behavior_aud... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 183 | src/zephyr/security/llm_defense/llm_security/dashboard/__... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 184 | src/zephyr/security/llm_defense/llm_security/dashboard/ap... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 185 | src/zephyr/security/llm_defense/llm_security/gateway.py | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 186 | src/zephyr/security/llm_defense/llm_security/input_saniti... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 187 | src/zephyr/security/llm_defense/llm_security/layers/__ini... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 188 | src/zephyr/security/llm_defense/llm_security/layers/l0_su... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 189 | src/zephyr/security/llm_defense/llm_security/layers/l1_in... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 190 | src/zephyr/security/llm_defense/llm_security/layers/l2_pr... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 191 | src/zephyr/security/llm_defense/llm_security/layers/l2a_p... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 192 | src/zephyr/security/llm_defense/llm_security/layers/l3_ou... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 193 | src/zephyr/security/llm_defense/llm_security/layers/l4_ag... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 194 | src/zephyr/security/llm_defense/llm_security/layers/l5_re... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 195 | src/zephyr/security/llm_defense/llm_security/layers/l6_da... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 196 | src/zephyr/security/llm_defense/llm_security/layers/l6_ob... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 197 | src/zephyr/security/llm_defense/llm_security/layers/l7_ru... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 198 | src/zephyr/security/llm_defense/llm_security/layers/l8_co... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 199 | src/zephyr/security/llm_defense/llm_security/layers/l8_mu... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 200 | src/zephyr/security/llm_defense/llm_security/patterns/__i... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |

> (仅显示前 200 个模块，共 272 个)

### 未分类 / Unclassified (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F16-orphan-judge/ | F16-orphan-judge/ | design | stable |
| 2 | F30-red-blue/ | F30-red-blue/ | design | stable |
| 3 | F7-llm-gateway/ | F7-llm-gateway/ | design | stable |
| 4 | F8-rbac/ | F8-rbac/ | design | stable |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 245 条 / 245 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 245 条 / 245 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 3                               │
│   [import_depends]: 238 条 / edges                               │
│   [config_depends]: 6 条 / edges                                 │
│   [contract]: 1 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (238 条 / edges)                 │
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
│   ...还有 189 条 / 189 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 245 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `18_d_security_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
