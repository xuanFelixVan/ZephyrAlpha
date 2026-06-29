---
doc_type: architecture_view
title: D_AUTONOMY_PERM 自治保护架构文档
version: "1.0"
status: active
date: 2026-06-29
owner: auto-generator
ttl: permanent
---

# 23_d_autonomy_perm / 自治保护

> **文档作用 / Purpose**: 展示 自治保护（D_AUTONOMY_PERM）功能域的模块清单、域内依赖关系、跨域依赖关系、架构全景图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-29 17:11:16
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 23 | Number | 23 |
| 域ID | D_AUTONOMY_PERM | Domain ID | D_AUTONOMY_PERM |
| 域名称 | 自治保护 | Domain Name | 自治保护 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 70 | Module Count | 70 |
| 域内依赖 | 7 | Internal Dependencies | 7 |
| 跨域入边 | 5 | Cross-domain Incoming | 5 |
| 跨域出边 | 145 | Cross-domain Outgoing | 145 |
| 设计态模块 | 1 | Design Modules | 1 |
| 原型态模块 | 67 | Prototype Modules | 67 |
| 生产态模块 | 2 | Production Modules | 2 |
| 容量 | 2/150 (正常) | Capacity | 2/150 (正常) |
| 描述 | 规则驱动升级(EscalationEngine) | Description | 规则驱动升级(EscalationEngine) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 3 页 / Page 1 of 3

```mermaid
graph TD
    subgraph D_AUTONOMY_PERM["D_AUTONOMY_PERM 自治保护"]
        config_runtime_kill_switch_state_yaml["config/runtime/kill_switch_state.yaml production"]
        docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md["docs__03_modules___domain_autonomy_core__agent_... design"]
        src_zephyr_autonomy_perm_init_py["src/zephyr/autonomy_perm/__init__.py prototype"]
        src_zephyr_autonomy_perm_extensions_init_py["src/zephyr/autonomy_perm/_extensions/__init__.py prototype"]
        src_zephyr_autonomy_perm_api_init_py["src/zephyr/autonomy_perm/api/__init__.py prototype"]
        src_zephyr_autonomy_perm_core_init_py["src/zephyr/autonomy_perm/core/__init__.py prototype"]
        src_zephyr_autonomy_perm_infrastructure_init_py["src/zephyr/autonomy_perm/infrastructure/__init_... prototype"]
        src_zephyr_autonomy_perm_models_init_py["src/zephyr/autonomy_perm/models/__init__.py prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_init_py["src/zephyr/autonomy_perm/red_blue_validator/__i... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_attack_registry_py["src/zephyr/autonomy_perm/red_blue_validator/att... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_bypass_recorder_py["src/zephyr/autonomy_perm/red_blue_validator/byp... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_constitution_guard_py["src/zephyr/autonomy_perm/red_blue_validator/con... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_convergence_checker_py["src/zephyr/autonomy_perm/red_blue_validator/con... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_defense_runner_py["src/zephyr/autonomy_perm/red_blue_validator/def... prototype"]
        src_zephyr_autonomy_perm_red_blue_validator_game_day_runner_py["src/zephyr/autonomy_perm/red_blue_validator/gam... prototype"]
        src_zephyr_autonomy_perm_services_init_py["src/zephyr/autonomy_perm/services/__init__.py prototype"]
        src_zephyr_governance_agent_signer_py["src/zephyr/governance/agent_signer.py prototype"]
        src_zephyr_security_access_control_governance_bridges_init_py["src/zephyr/security/access_control/governance_b... prototype"]
        src_zephyr_security_access_control_governance_bridges_a2a_check_py["src/zephyr/security/access_control/governance_b... prototype"]
        src_zephyr_security_access_control_governance_bridges_approver_check_py["src/zephyr/security/access_control/governance_b... prototype"]
        src_zephyr_security_access_control_governance_bridges_bootstrap_superadmin_py["src/zephyr/security/access_control/governance_b... production"]
        src_zephyr_security_access_control_governance_bridges_capability_check_py["src/zephyr/security/access_control/governance_b... prototype"]
        src_zephyr_security_access_control_governance_bridges_contracts_py["src/zephyr/security/access_control/governance_b... prototype"]
        tests_agent_rbac_init_py["tests/agent_rbac/__init__.py prototype"]
        tests_agent_rbac_conftest_py["tests/agent_rbac/conftest.py prototype"]
        tests_agent_rbac_test_abac_guard_agent_rbac_py["tests/agent_rbac/test_abac_guard_agent_rbac.py prototype"]
        tests_agent_rbac_test_adversarial_agent_rbac_py["tests/agent_rbac/test_adversarial_agent_rbac.py prototype"]
        tests_agent_rbac_test_blind_spot_coverage_py["tests/agent_rbac/test_blind_spot_coverage.py prototype"]
        tests_agent_rbac_test_cross_model_consistency_py["tests/agent_rbac/test_cross_model_consistency.py prototype"]
        tests_agent_rbac_test_crosscut_d_py["tests/agent_rbac/test_crosscut_d.py prototype"]
    end
    src_zephyr_security_access_control_governance_bridges_a2a_check_py -.->|config_depends| src_zephyr_security_access_control_governance_bridges_init_py
    src_zephyr_security_access_control_governance_bridges_approver_check_py -.->|config_depends| src_zephyr_security_access_control_governance_bridges_init_py
    src_zephyr_security_access_control_governance_bridges_bootstrap_superadmin_py -.->|config_depends| src_zephyr_security_access_control_governance_bridges_init_py
    src_zephyr_security_access_control_governance_bridges_capability_check_py -.->|config_depends| src_zephyr_security_access_control_governance_bridges_init_py
    src_zephyr_security_access_control_governance_bridges_contracts_py -.->|config_depends| src_zephyr_security_access_control_governance_bridges_init_py
    tests_agent_rbac_conftest_py -.->|config_depends| tests_agent_rbac_init_py
    D_GOVERNANCE["D_GOVERNANCE production"]
    src_zephyr_governance_agent_signer_py -.->|config_depends| D_GOVERNANCE
    D_SECURITY["D_SECURITY production"]
    tests_agent_rbac_test_adversarial_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_adversarial_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_adversarial_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_adversarial_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_blind_spot_coverage_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_cross_model_consistency_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_cross_model_consistency_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_cross_model_consistency_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_cross_model_consistency_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_cross_model_consistency_py -.->|test_depends| D_SECURITY
    D_GOVERNANCE -.->|runtime| docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md
    D_GOV_DRIFT["D_GOV_DRIFT design"]
    D_GOV_DRIFT -.->|runtime| docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md
    D_GOVERNANCE -.->|contract| docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md
    D_GOVERNANCE -.->|contract| docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md
    D_GOVERNANCE -.->|runtime| docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class config_runtime_kill_switch_state_yaml,src_zephyr_security_access_control_governance_bridges_bootstrap_superadmin_py production
    class docs_03_modules_domain_autonomy_core_agent_rbac_blueprint_md,src_zephyr_autonomy_perm_init_py,src_zephyr_autonomy_perm_extensions_init_py,src_zephyr_autonomy_perm_api_init_py,src_zephyr_autonomy_perm_core_init_py,src_zephyr_autonomy_perm_infrastructure_init_py,src_zephyr_autonomy_perm_models_init_py,src_zephyr_autonomy_perm_red_blue_validator_init_py,src_zephyr_autonomy_perm_red_blue_validator_attack_registry_py,src_zephyr_autonomy_perm_red_blue_validator_bypass_recorder_py,src_zephyr_autonomy_perm_red_blue_validator_constitution_guard_py,src_zephyr_autonomy_perm_red_blue_validator_convergence_checker_py,src_zephyr_autonomy_perm_red_blue_validator_defense_runner_py,src_zephyr_autonomy_perm_red_blue_validator_game_day_runner_py,src_zephyr_autonomy_perm_services_init_py,src_zephyr_governance_agent_signer_py,src_zephyr_security_access_control_governance_bridges_init_py,src_zephyr_security_access_control_governance_bridges_a2a_check_py,src_zephyr_security_access_control_governance_bridges_approver_check_py,src_zephyr_security_access_control_governance_bridges_capability_check_py,src_zephyr_security_access_control_governance_bridges_contracts_py,tests_agent_rbac_init_py,tests_agent_rbac_conftest_py,tests_agent_rbac_test_abac_guard_agent_rbac_py,tests_agent_rbac_test_adversarial_agent_rbac_py,tests_agent_rbac_test_blind_spot_coverage_py,tests_agent_rbac_test_cross_model_consistency_py,tests_agent_rbac_test_crosscut_d_py design
    class D_GOVERNANCE,D_SECURITY external_prod
    class D_GOV_DRIFT external_design
```

### 第 2 页 / 共 3 页 / Page 2 of 3

```mermaid
graph TD
    subgraph D_AUTONOMY_PERM["D_AUTONOMY_PERM 自治保护"]
        tests_agent_rbac_test_cybersec_2026_py["tests/agent_rbac/test_cybersec_2026.py prototype"]
        tests_agent_rbac_test_decision_explainer_agent_rbac_py["tests/agent_rbac/test_decision_explainer_agent_... prototype"]
        tests_agent_rbac_test_decisions_py["tests/agent_rbac/test_decisions.py prototype"]
        tests_agent_rbac_test_derive_rbac_py["tests/agent_rbac/test_derive_rbac.py prototype"]
        tests_agent_rbac_test_dry_run_agent_rbac_py["tests/agent_rbac/test_dry_run_agent_rbac.py prototype"]
        tests_agent_rbac_test_engine_degradation_agent_rbac_py["tests/agent_rbac/test_engine_degradation_agent_... prototype"]
        tests_agent_rbac_test_enhanced_security_py["tests/agent_rbac/test_enhanced_security.py prototype"]
        tests_agent_rbac_test_exceptions_agent_rbac_py["tests/agent_rbac/test_exceptions_agent_rbac.py prototype"]
        tests_agent_rbac_test_forensic_a_py["tests/agent_rbac/test_forensic_a.py prototype"]
        tests_agent_rbac_test_forensic_b_py["tests/agent_rbac/test_forensic_b.py prototype"]
        tests_agent_rbac_test_forensic_c_py["tests/agent_rbac/test_forensic_c.py prototype"]
        tests_agent_rbac_test_guard_layers_agent_rbac_py["tests/agent_rbac/test_guard_layers_agent_rbac.py prototype"]
        tests_agent_rbac_test_identity_py["tests/agent_rbac/test_identity.py prototype"]
        tests_agent_rbac_test_immutable_core_agent_rbac_py["tests/agent_rbac/test_immutable_core_agent_rbac.py prototype"]
        tests_agent_rbac_test_input_guard_agent_rbac_py["tests/agent_rbac/test_input_guard_agent_rbac.py prototype"]
        tests_agent_rbac_test_integration_agent_rbac_py["tests/agent_rbac/test_integration_agent_rbac.py prototype"]
        tests_agent_rbac_test_integrity_agent_rbac_py["tests/agent_rbac/test_integrity_agent_rbac.py prototype"]
        tests_agent_rbac_test_intent_binder_agent_rbac_py["tests/agent_rbac/test_intent_binder_agent_rbac.py prototype"]
        tests_agent_rbac_test_kill_switch_agent_rbac_py["tests/agent_rbac/test_kill_switch_agent_rbac.py prototype"]
        tests_agent_rbac_test_novel_attack_py["tests/agent_rbac/test_novel_attack.py prototype"]
        tests_agent_rbac_test_observability_agent_rbac_py["tests/agent_rbac/test_observability_agent_rbac.py prototype"]
        tests_agent_rbac_test_output_guard_agent_rbac_py["tests/agent_rbac/test_output_guard_agent_rbac.py prototype"]
        tests_agent_rbac_test_permission_guard_py["tests/agent_rbac/test_permission_guard.py prototype"]
        tests_agent_rbac_test_permissions_py["tests/agent_rbac/test_permissions.py prototype"]
        tests_agent_rbac_test_post_action_py["tests/agent_rbac/test_post_action.py prototype"]
        tests_agent_rbac_test_rbac_guard_agent_rbac_py["tests/agent_rbac/test_rbac_guard_agent_rbac.py prototype"]
        tests_agent_rbac_test_redteam_adversarial_py["tests/agent_rbac/test_redteam_adversarial.py prototype"]
        tests_agent_rbac_test_risk_mitigation_agent_rbac_py["tests/agent_rbac/test_risk_mitigation_agent_rba... prototype"]
        tests_agent_rbac_test_sequence_guard_agent_rbac_py["tests/agent_rbac/test_sequence_guard_agent_rbac.py prototype"]
        tests_agent_rbac_test_toctou_guard_agent_rbac_py["tests/agent_rbac/test_toctou_guard_agent_rbac.py prototype"]
    end
    D_SECURITY["D_SECURITY production"]
    tests_agent_rbac_test_cybersec_2026_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_decisions_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_decision_explainer_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_derive_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_derive_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_engine_degradation_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_dry_run_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_dry_run_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_dry_run_agent_rbac_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_enhanced_security_py -.->|test_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_agent_rbac_test_cybersec_2026_py,tests_agent_rbac_test_decision_explainer_agent_rbac_py,tests_agent_rbac_test_decisions_py,tests_agent_rbac_test_derive_rbac_py,tests_agent_rbac_test_dry_run_agent_rbac_py,tests_agent_rbac_test_engine_degradation_agent_rbac_py,tests_agent_rbac_test_enhanced_security_py,tests_agent_rbac_test_exceptions_agent_rbac_py,tests_agent_rbac_test_forensic_a_py,tests_agent_rbac_test_forensic_b_py,tests_agent_rbac_test_forensic_c_py,tests_agent_rbac_test_guard_layers_agent_rbac_py,tests_agent_rbac_test_identity_py,tests_agent_rbac_test_immutable_core_agent_rbac_py,tests_agent_rbac_test_input_guard_agent_rbac_py,tests_agent_rbac_test_integration_agent_rbac_py,tests_agent_rbac_test_integrity_agent_rbac_py,tests_agent_rbac_test_intent_binder_agent_rbac_py,tests_agent_rbac_test_kill_switch_agent_rbac_py,tests_agent_rbac_test_novel_attack_py,tests_agent_rbac_test_observability_agent_rbac_py,tests_agent_rbac_test_output_guard_agent_rbac_py,tests_agent_rbac_test_permission_guard_py,tests_agent_rbac_test_permissions_py,tests_agent_rbac_test_post_action_py,tests_agent_rbac_test_rbac_guard_agent_rbac_py,tests_agent_rbac_test_redteam_adversarial_py,tests_agent_rbac_test_risk_mitigation_agent_rbac_py,tests_agent_rbac_test_sequence_guard_agent_rbac_py,tests_agent_rbac_test_toctou_guard_agent_rbac_py design
    class D_SECURITY external_prod
```

### 第 3 页 / 共 3 页 / Page 3 of 3

```mermaid
graph TD
    subgraph D_AUTONOMY_PERM["D_AUTONOMY_PERM 自治保护"]
        tests_agent_rbac_test_vibe_coding_py["tests/agent_rbac/test_vibe_coding.py prototype"]
        tests_test_agent_signer_py["tests/test_agent_signer.py prototype"]
        tests_test_ce_kill_switch_py["tests/test_ce_kill_switch.py prototype"]
        tests_test_kill_switch_root_py["tests/test_kill_switch_root.py prototype"]
        tests_test_kill_switch_sim_py["tests/test_kill_switch_sim.py prototype"]
        tests_test_skill_kill_switch_py["tests/test_skill_kill_switch.py prototype"]
        tests_test_trading_kill_switch_py["tests/test_trading_kill_switch.py prototype"]
        tests_unit_agent_rbac_init_py["tests/unit/agent_rbac/__init__.py prototype"]
        tests_unit_agent_rbac_conftest_py["tests/unit/agent_rbac/conftest.py prototype"]
        tests_unit_agent_rbac_test_rbac_core_py["tests/unit/agent_rbac/test_rbac_core.py prototype"]
    end
    tests_unit_agent_rbac_conftest_py -.->|config_depends| tests_unit_agent_rbac_init_py
    D_GOV_AUDIT["D_GOV_AUDIT production"]
    tests_test_agent_signer_py -.->|test_depends| D_GOV_AUDIT
    D_GOVERNANCE["D_GOVERNANCE production"]
    tests_test_ce_kill_switch_py -.->|test_depends| D_GOVERNANCE
    D_SECURITY["D_SECURITY production"]
    tests_test_kill_switch_root_py -.->|test_depends| D_SECURITY
    tests_test_kill_switch_root_py -.->|test_depends| D_SECURITY
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    tests_test_kill_switch_sim_py -.->|test_depends| D_INFRA_RUNTIME
    D_AUTONOMY_CORE["D_AUTONOMY_CORE production"]
    tests_test_skill_kill_switch_py -.->|test_depends| D_AUTONOMY_CORE
    tests_test_trading_kill_switch_py -.->|test_depends| D_GOVERNANCE
    tests_agent_rbac_test_vibe_coding_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_vibe_coding_py -.->|test_depends| D_SECURITY
    tests_agent_rbac_test_vibe_coding_py -.->|test_depends| D_SECURITY
    D_INTEGRATION["D_INTEGRATION production"]
    tests_unit_agent_rbac_test_rbac_core_py -.->|test_depends| D_INTEGRATION
    tests_unit_agent_rbac_test_rbac_core_py -.->|test_depends| D_INTEGRATION
    tests_unit_agent_rbac_test_rbac_core_py -.->|test_depends| D_SECURITY
    tests_unit_agent_rbac_test_rbac_core_py -.->|test_depends| D_SECURITY
    tests_unit_agent_rbac_test_rbac_core_py -.->|test_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_agent_rbac_test_vibe_coding_py,tests_test_agent_signer_py,tests_test_ce_kill_switch_py,tests_test_kill_switch_root_py,tests_test_kill_switch_sim_py,tests_test_skill_kill_switch_py,tests_test_trading_kill_switch_py,tests_unit_agent_rbac_init_py,tests_unit_agent_rbac_conftest_py,tests_unit_agent_rbac_test_rbac_core_py design
    class D_GOV_AUDIT,D_GOVERNANCE,D_SECURITY,D_INFRA_RUNTIME,D_AUTONOMY_CORE,D_INTEGRATION external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SECURITY | 137 | import_depends,test_depends |
| D_GOVERNANCE | 3 | config_depends,test_depends |
| D_INTEGRATION | 2 | test_depends |
| D_AUTONOMY_CORE | 1 | test_depends |
| D_GOV_AUDIT | 1 | test_depends |
| D_INFRA_RUNTIME | 1 | test_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_GOVERNANCE | 4 | contract,runtime |
| D_GOV_DRIFT | 1 | runtime |

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 自治保护（D_AUTONOMY_PERM）的模块分布。共 70 个模块 / 70 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (70 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/runtime/kill_switch_state.yaml  [production]            │
│   docs__03_modules___domain_autonomy_core__agent_rbac__bluepr... │
│   src/zephyr/autonomy_perm/__init__.py  [prototype]              │
│   src/zephyr/autonomy_perm/_extensions/__init__.py  [prototype]  │
│   src/zephyr/autonomy_perm/api/__init__.py  [prototype]          │
│   src/zephyr/autonomy_perm/core/__init__.py  [prototype]         │
│   src/zephyr/autonomy_perm/infrastructure/__init__.py  [proto... │
│   src/zephyr/autonomy_perm/models/__init__.py  [prototype]       │
│   src/zephyr/autonomy_perm/red_blue_validator/__init__.py  [p... │
│   src/zephyr/autonomy_perm/red_blue_validator/attack_registry... │
│   src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder... │
│   src/zephyr/autonomy_perm/red_blue_validator/constitution_gu... │
│   src/zephyr/autonomy_perm/red_blue_validator/convergence_che... │
│   src/zephyr/autonomy_perm/red_blue_validator/defense_runner.... │
│   src/zephyr/autonomy_perm/red_blue_validator/game_day_runner... │
│   src/zephyr/autonomy_perm/services/__init__.py  [prototype]     │
│   src/zephyr/governance/agent_signer.py  [prototype]             │
│   src/zephyr/security/access_control/governance_bridges/__ini... │
│   ...还有 52 个模块 / 52 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 70 个模块 / 70 modules）。

### L1 基础层 / Foundation Layer (70 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/runtime/kill_switch_state.yaml | config/runtime/kill_switch_state.yaml | production | deprecated |
| 2 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprin... | docs__03_modules___domain_autonomy_co... | design | planned |
| 3 | src/zephyr/autonomy_perm/__init__.py | src/zephyr/autonomy_perm/__init__.py | prototype | deprecated |
| 4 | src/zephyr/autonomy_perm/_extensions/__init__.py | src/zephyr/autonomy_perm/_extensions/... | prototype | deprecated |
| 5 | src/zephyr/autonomy_perm/api/__init__.py | src/zephyr/autonomy_perm/api/__init__.py | prototype | deprecated |
| 6 | src/zephyr/autonomy_perm/core/__init__.py | src/zephyr/autonomy_perm/core/__init_... | prototype | deprecated |
| 7 | src/zephyr/autonomy_perm/infrastructure/__init__.py | src/zephyr/autonomy_perm/infrastructu... | prototype | deprecated |
| 8 | src/zephyr/autonomy_perm/models/__init__.py | src/zephyr/autonomy_perm/models/__ini... | prototype | deprecated |
| 9 | src/zephyr/autonomy_perm/red_blue_validator/__init__.py | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 10 | src/zephyr/autonomy_perm/red_blue_validator/attack_regist... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 11 | src/zephyr/autonomy_perm/red_blue_validator/bypass_record... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 12 | src/zephyr/autonomy_perm/red_blue_validator/constitution_... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 13 | src/zephyr/autonomy_perm/red_blue_validator/convergence_c... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 14 | src/zephyr/autonomy_perm/red_blue_validator/defense_runne... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 15 | src/zephyr/autonomy_perm/red_blue_validator/game_day_runn... | src/zephyr/autonomy_perm/red_blue_val... | prototype | generated |
| 16 | src/zephyr/autonomy_perm/services/__init__.py | src/zephyr/autonomy_perm/services/__i... | prototype | deprecated |
| 17 | src/zephyr/governance/agent_signer.py | src/zephyr/governance/agent_signer.py | prototype | generated |
| 18 | src/zephyr/security/access_control/governance_bridges/__i... | src/zephyr/security/access_control/go... | prototype | stable |
| 19 | src/zephyr/security/access_control/governance_bridges/a2a... | src/zephyr/security/access_control/go... | prototype | stable |
| 20 | src/zephyr/security/access_control/governance_bridges/app... | src/zephyr/security/access_control/go... | prototype | stable |
| 21 | src/zephyr/security/access_control/governance_bridges/boo... | src/zephyr/security/access_control/go... | production | stable |
| 22 | src/zephyr/security/access_control/governance_bridges/cap... | src/zephyr/security/access_control/go... | prototype | stable |
| 23 | src/zephyr/security/access_control/governance_bridges/con... | src/zephyr/security/access_control/go... | prototype | stable |
| 24 | tests/agent_rbac/__init__.py | tests/agent_rbac/__init__.py | prototype | generated |
| 25 | tests/agent_rbac/conftest.py | tests/agent_rbac/conftest.py | prototype | generated |
| 26 | tests/agent_rbac/test_abac_guard_agent_rbac.py | tests/agent_rbac/test_abac_guard_agen... | prototype | generated |
| 27 | tests/agent_rbac/test_adversarial_agent_rbac.py | tests/agent_rbac/test_adversarial_age... | prototype | generated |
| 28 | tests/agent_rbac/test_blind_spot_coverage.py | tests/agent_rbac/test_blind_spot_cove... | prototype | generated |
| 29 | tests/agent_rbac/test_cross_model_consistency.py | tests/agent_rbac/test_cross_model_con... | prototype | generated |
| 30 | tests/agent_rbac/test_crosscut_d.py | tests/agent_rbac/test_crosscut_d.py | prototype | generated |
| 31 | tests/agent_rbac/test_cybersec_2026.py | tests/agent_rbac/test_cybersec_2026.py | prototype | generated |
| 32 | tests/agent_rbac/test_decision_explainer_agent_rbac.py | tests/agent_rbac/test_decision_explai... | prototype | generated |
| 33 | tests/agent_rbac/test_decisions.py | tests/agent_rbac/test_decisions.py | prototype | generated |
| 34 | tests/agent_rbac/test_derive_rbac.py | tests/agent_rbac/test_derive_rbac.py | prototype | generated |
| 35 | tests/agent_rbac/test_dry_run_agent_rbac.py | tests/agent_rbac/test_dry_run_agent_r... | prototype | generated |
| 36 | tests/agent_rbac/test_engine_degradation_agent_rbac.py | tests/agent_rbac/test_engine_degradat... | prototype | generated |
| 37 | tests/agent_rbac/test_enhanced_security.py | tests/agent_rbac/test_enhanced_securi... | prototype | generated |
| 38 | tests/agent_rbac/test_exceptions_agent_rbac.py | tests/agent_rbac/test_exceptions_agen... | prototype | generated |
| 39 | tests/agent_rbac/test_forensic_a.py | tests/agent_rbac/test_forensic_a.py | prototype | generated |
| 40 | tests/agent_rbac/test_forensic_b.py | tests/agent_rbac/test_forensic_b.py | prototype | generated |
| 41 | tests/agent_rbac/test_forensic_c.py | tests/agent_rbac/test_forensic_c.py | prototype | generated |
| 42 | tests/agent_rbac/test_guard_layers_agent_rbac.py | tests/agent_rbac/test_guard_layers_ag... | prototype | generated |
| 43 | tests/agent_rbac/test_identity.py | tests/agent_rbac/test_identity.py | prototype | generated |
| 44 | tests/agent_rbac/test_immutable_core_agent_rbac.py | tests/agent_rbac/test_immutable_core_... | prototype | generated |
| 45 | tests/agent_rbac/test_input_guard_agent_rbac.py | tests/agent_rbac/test_input_guard_age... | prototype | generated |
| 46 | tests/agent_rbac/test_integration_agent_rbac.py | tests/agent_rbac/test_integration_age... | prototype | generated |
| 47 | tests/agent_rbac/test_integrity_agent_rbac.py | tests/agent_rbac/test_integrity_agent... | prototype | generated |
| 48 | tests/agent_rbac/test_intent_binder_agent_rbac.py | tests/agent_rbac/test_intent_binder_a... | prototype | generated |
| 49 | tests/agent_rbac/test_kill_switch_agent_rbac.py | tests/agent_rbac/test_kill_switch_age... | prototype | generated |
| 50 | tests/agent_rbac/test_novel_attack.py | tests/agent_rbac/test_novel_attack.py | prototype | generated |
| 51 | tests/agent_rbac/test_observability_agent_rbac.py | tests/agent_rbac/test_observability_a... | prototype | generated |
| 52 | tests/agent_rbac/test_output_guard_agent_rbac.py | tests/agent_rbac/test_output_guard_ag... | prototype | generated |
| 53 | tests/agent_rbac/test_permission_guard.py | tests/agent_rbac/test_permission_guar... | prototype | generated |
| 54 | tests/agent_rbac/test_permissions.py | tests/agent_rbac/test_permissions.py | prototype | generated |
| 55 | tests/agent_rbac/test_post_action.py | tests/agent_rbac/test_post_action.py | prototype | generated |
| 56 | tests/agent_rbac/test_rbac_guard_agent_rbac.py | tests/agent_rbac/test_rbac_guard_agen... | prototype | generated |
| 57 | tests/agent_rbac/test_redteam_adversarial.py | tests/agent_rbac/test_redteam_adversa... | prototype | generated |
| 58 | tests/agent_rbac/test_risk_mitigation_agent_rbac.py | tests/agent_rbac/test_risk_mitigation... | prototype | generated |
| 59 | tests/agent_rbac/test_sequence_guard_agent_rbac.py | tests/agent_rbac/test_sequence_guard_... | prototype | generated |
| 60 | tests/agent_rbac/test_toctou_guard_agent_rbac.py | tests/agent_rbac/test_toctou_guard_ag... | prototype | generated |
| 61 | tests/agent_rbac/test_vibe_coding.py | tests/agent_rbac/test_vibe_coding.py | prototype | generated |
| 62 | tests/test_agent_signer.py | tests/test_agent_signer.py | prototype | generated |
| 63 | tests/test_ce_kill_switch.py | tests/test_ce_kill_switch.py | prototype | generated |
| 64 | tests/test_kill_switch_root.py | tests/test_kill_switch_root.py | prototype | generated |
| 65 | tests/test_kill_switch_sim.py | tests/test_kill_switch_sim.py | prototype | generated |
| 66 | tests/test_skill_kill_switch.py | tests/test_skill_kill_switch.py | prototype | generated |
| 67 | tests/test_trading_kill_switch.py | tests/test_trading_kill_switch.py | prototype | generated |
| 68 | tests/unit/agent_rbac/__init__.py | tests/unit/agent_rbac/__init__.py | prototype | generated |
| 69 | tests/unit/agent_rbac/conftest.py | tests/unit/agent_rbac/conftest.py | prototype | generated |
| 70 | tests/unit/agent_rbac/test_rbac_core.py | tests/unit/agent_rbac/test_rbac_core.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 7 条 / 7 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 7 条 / 7 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 7 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (7 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   a2a_check.py → __init__.py                                     │
│   approver_check.py → __init__.py                                │
│   bootstrap_superadmin.py → __init__.py                          │
│   capability_check.py → __init__.py                              │
│   contracts.py → __init__.py                                     │
│   conftest.py → __init__.py                                      │
│   conftest.py → __init__.py                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
