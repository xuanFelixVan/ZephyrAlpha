---
doc_type: architecture_view
title: D_AUDITTEST audit_test_suite架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 21_d_audittest / audit_test_suite / Audit Test Suite

> **文档作用 / Purpose**: 展示 audit_test_suite（D_AUDITTEST）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 16:12:27
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 21 | Number | 21 |
| 域ID | D_AUDITTEST | Domain ID | D_AUDITTEST |
| 域名称 | audit_test_suite | Domain Name | Audit Test Suite |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 1 | Module Count | 1 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 48/150 (正常) | Capacity | 48/150 (正常) |
| 描述 | 审计单元测试(unit) | Description | 审计单元测试(unit) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST audit_test_suite"]
        docs_01_policies_and_standards_registry_catalogs_test_suite_registry_yaml["测试集 (Test Suite) — ARCH-052 聚合节点 production"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_test_suite_registry_yaml production
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

无跨域出边依赖 / No cross-domain outgoing dependencies

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 audit_test_suite（D_AUDITTEST）的模块分布。共 1 个模块 / 1 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   测试集 (Test Suite) — ARCH-052 聚合节点  [production]          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 1 个模块 / 1 modules）。

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|---------|:---:|:---:|
| 1 | docs/01_policies_and_standards/_registry/catalogs/test_su... | 测试集 (Test Suite) — ARCH-052 聚合节点 | [聚合节点 / Aggregated] 测试集 / Test Suite (1718 items) | production | stable |
| ↳1 |   ↳ tests/a2a/test_a2a_anomaly_detector.py |  |  | - | - |
| ↳2 |   ↳ tests/a2a/test_a2a_behavior_fingerprint.py |  |  | - | - |
| ↳3 |   ↳ tests/a2a/test_a2a_blame_attribution.py |  |  | - | - |
| ↳4 |   ↳ tests/a2a/test_a2a_carbon.py |  |  | - | - |
| ↳5 |   ↳ tests/a2a/test_a2a_card_registry.py |  |  | - | - |
| ↳6 |   ↳ tests/a2a/test_a2a_causal_trace.py |  |  | - | - |
| ↳7 |   ↳ tests/a2a/test_a2a_check.py |  |  | - | - |
| ↳8 |   ↳ tests/a2a/test_a2a_checkpoint.py |  |  | - | - |
| ↳9 |   ↳ tests/a2a/test_a2a_collusion_detector.py |  |  | - | - |
| ↳10 |   ↳ tests/a2a/test_a2a_consent.py |  |  | - | - |
| ↳11 |   ↳ tests/a2a/test_a2a_constitutional.py |  |  | - | - |
| ↳12 |   ↳ tests/a2a/test_a2a_context_rot.py |  |  | - | - |
| ↳13 |   ↳ tests/a2a/test_a2a_cross_agent_semantic_flow.py |  |  | - | - |
| ↳14 |   ↳ tests/a2a/test_a2a_dashboard.py |  |  | - | - |
| ↳15 |   ↳ tests/a2a/test_a2a_debate.py |  |  | - | - |
| ↳16 |   ↳ tests/a2a/test_a2a_delegation_chain.py |  |  | - | - |
| ↳17 |   ↳ tests/a2a/test_a2a_economics.py |  |  | - | - |
| ↳18 |   ↳ tests/a2a/test_a2a_failure.py |  |  | - | - |
| ↳19 |   ↳ tests/a2a/test_a2a_forgetting.py |  |  | - | - |
| ↳20 |   ↳ tests/a2a/test_a2a_formal_verification.py |  |  | - | - |
| ↳21 |   ↳ tests/a2a/test_a2a_frame_negotiation.py |  |  | - | - |
| ↳22 |   ↳ tests/a2a/test_a2a_governance.py |  |  | - | - |
| ↳23 |   ↳ tests/a2a/test_a2a_governance_adapter.py |  |  | - | - |
| ↳24 |   ↳ tests/a2a/test_a2a_hardware_router.py |  |  | - | - |
| ↳25 |   ↳ tests/a2a/test_a2a_hibernate.py |  |  | - | - |
| ↳26 |   ↳ tests/a2a/test_a2a_idempotency.py |  |  | - | - |
| ↳27 |   ↳ tests/a2a/test_a2a_idle_guard.py |  |  | - | - |
| ↳28 |   ↳ tests/a2a/test_a2a_immune.py |  |  | - | - |
| ↳29 |   ↳ tests/a2a/test_a2a_knowledge_distill.py |  |  | - | - |
| ↳30 |   ↳ tests/a2a/test_a2a_latent_comm.py |  |  | - | - |
| ↳31 |   ↳ tests/a2a/test_a2a_layer1_discovery.py |  |  | - | - |
| ↳32 |   ↳ tests/a2a/test_a2a_metrics.py |  |  | - | - |
| ↳33 |   ↳ tests/a2a/test_a2a_negotiation.py |  |  | - | - |
| ↳34 |   ↳ tests/a2a/test_a2a_protocol_gateway.py |  |  | - | - |
| ↳35 |   ↳ tests/a2a/test_a2a_protocol_security.py |  |  | - | - |
| ↳36 |   ↳ tests/a2a/test_a2a_red_team.py |  |  | - | - |
| ↳37 |   ↳ tests/a2a/test_a2a_saga.py |  |  | - | - |
| ↳38 |   ↳ tests/a2a/test_a2a_schemas.py |  |  | - | - |
| ↳39 |   ↳ tests/a2a/test_a2a_security.py |  |  | - | - |
| ↳40 |   ↳ tests/a2a/test_a2a_state.py |  |  | - | - |
| ↳41 |   ↳ tests/a2a/test_a2a_temporal_admission.py |  |  | - | - |
| ↳42 |   ↳ tests/a2a/test_a2a_tracing.py |  |  | - | - |
| ↳43 |   ↳ tests/a2a/test_a2a_vector_reputation.py |  |  | - | - |
| ↳44 |   ↳ tests/a2a/test_a2a_voting.py |  |  | - | - |
| ↳45 |   ↳ tests/a2a/test_a2a_work_steal.py |  |  | - | - |
| ↳46 |   ↳ tests/a2a/test_construction_verifier.py |  |  | - | - |
| ↳47 |   ↳ tests/a2a/test_legacy_auditor.py |  |  | - | - |
| ↳48 |   ↳ tests/a2a/test_legacy_governance_adapter.py |  |  | - | - |
| ↳49 |   ↳ tests/a2a/test_legacy_protocol.py |  |  | - | - |
| ↳50 |   ↳ tests/a2a/test_mcp.py |  |  | - | - |
| ↳51 |   ↳ tests/a2a/test_spec_sync.py |  |  | - | - |
| ↳52 |   ↳ tests/action/test_action_composition_health_monitor.py |  |  | - | - |
| ↳53 |   ↳ tests/action/test_action_dispatcher.py |  |  | - | - |
| ↳54 |   ↳ tests/action/test_action_efficacy_decay_detector.py |  |  | - | - |
| ↳55 |   ↳ tests/action/test_action_explainability.py |  |  | - | - |
| ↳56 |   ↳ tests/action/test_action_history.py |  |  | - | - |
| ↳57 |   ↳ tests/action/test_action_interaction_detector.py |  |  | - | - |
| ↳58 |   ↳ tests/action/test_action_reversibility.py |  |  | - | - |
| ↳59 |   ↳ tests/action/test_action_selector.py |  |  | - | - |
| ↳60 |   ↳ tests/action/test_action_side_effect_cumulative_dete... |  |  | - | - |
| ↳61 |   ↳ tests/agent/test_agent_cooldown.py |  |  | - | - |
| ↳62 |   ↳ tests/agent/test_agent_creation_policy.py |  |  | - | - |
| ↳63 |   ↳ tests/agent/test_agent_health_monitor_root.py |  |  | - | - |
| ↳64 |   ↳ tests/agent/test_agent_lifecycle.py |  |  | - | - |
| ↳65 |   ↳ tests/agent/test_agent_observability.py |  |  | - | - |
| ↳66 |   ↳ tests/agent/test_agent_orchestrator_root.py |  |  | - | - |
| ↳67 |   ↳ tests/agent/test_agent_quality.py |  |  | - | - |
| ↳68 |   ↳ tests/agent/test_agent_signer.py |  |  | - | - |
| ↳69 |   ↳ tests/agent/test_agent_skill_guard.py |  |  | - | - |
| ↳70 |   ↳ tests/agent/test_agent_spec_main.py |  |  | - | - |
| ↳71 |   ↳ tests/agent/test_agent_spec_registry.py |  |  | - | - |
| ↳72 |   ↳ tests/agent/test_agent_trajectory_anomaly_detector.py |  |  | - | - |
| ↳73 |   ↳ tests/agent_rbac/conftest.py |  |  | - | - |
| ↳74 |   ↳ tests/agent_rbac/test_abac_guard_agent_rbac.py |  |  | - | - |
| ↳75 |   ↳ tests/agent_rbac/test_adversarial_agent_rbac.py |  |  | - | - |
| ↳76 |   ↳ tests/agent_rbac/test_adversarial_resilience.py |  |  | - | - |
| ↳77 |   ↳ tests/agent_rbac/test_cross_model_consistency.py |  |  | - | - |
| ↳78 |   ↳ tests/agent_rbac/test_crosscut_d.py |  |  | - | - |
| ↳79 |   ↳ tests/agent_rbac/test_cybersec_2026.py |  |  | - | - |
| ↳80 |   ↳ tests/agent_rbac/test_decision_explainer_agent_rbac.py |  |  | - | - |
| ↳81 |   ↳ tests/agent_rbac/test_decisions.py |  |  | - | - |
| ↳82 |   ↳ tests/agent_rbac/test_derive_rbac.py |  |  | - | - |
| ↳83 |   ↳ tests/agent_rbac/test_dry_run_agent_rbac.py |  |  | - | - |
| ↳84 |   ↳ tests/agent_rbac/test_engine_degradation_agent_rbac.py |  |  | - | - |
| ↳85 |   ↳ tests/agent_rbac/test_enhanced_security.py |  |  | - | - |
| ↳86 |   ↳ tests/agent_rbac/test_exceptions_agent_rbac.py |  |  | - | - |
| ↳87 |   ↳ tests/agent_rbac/test_forensic_a.py |  |  | - | - |
| ↳88 |   ↳ tests/agent_rbac/test_forensic_b.py |  |  | - | - |
| ↳89 |   ↳ tests/agent_rbac/test_forensic_c.py |  |  | - | - |
| ↳90 |   ↳ tests/agent_rbac/test_guard_layers_agent_rbac.py |  |  | - | - |
| ↳91 |   ↳ tests/agent_rbac/test_identity.py |  |  | - | - |
| ↳92 |   ↳ tests/agent_rbac/test_immutable_core_agent_rbac.py |  |  | - | - |
| ↳93 |   ↳ tests/agent_rbac/test_input_guard_agent_rbac.py |  |  | - | - |
| ↳94 |   ↳ tests/agent_rbac/test_integration_agent_rbac.py |  |  | - | - |
| ↳95 |   ↳ tests/agent_rbac/test_integration_root.py |  |  | - | - |
| ↳96 |   ↳ tests/agent_rbac/test_integrity_agent_rbac.py |  |  | - | - |
| ↳97 |   ↳ tests/agent_rbac/test_intent_binder_agent_rbac.py |  |  | - | - |
| ↳98 |   ↳ tests/agent_rbac/test_kill_switch_agent_rbac.py |  |  | - | - |
| ↳99 |   ↳ tests/agent_rbac/test_novel_attack.py |  |  | - | - |
| ↳100 |   ↳ tests/agent_rbac/test_observability_agent_rbac.py |  |  | - | - |
| | | | > (仅显示前 100 个 items，共 1718 个) | | |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
