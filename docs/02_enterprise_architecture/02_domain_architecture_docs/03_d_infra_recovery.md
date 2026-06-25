---
doc_type: domain_architecture_doc
title: D-INFRA_RECOVERY rollback_recovery架构文档
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 03_d_infra_recovery / rollback_recovery

> **文档作用 / Purpose**: 展示 rollback_recovery（D-INFRA_RECOVERY）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 18:42:45
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 03 | Number | 03 |
| 域ID | D-INFRA_RECOVERY | Domain ID | D-INFRA_RECOVERY |
| 域名称 | rollback_recovery | Domain Name | rollback_recovery |
| 层级 | L0_infrastructure | Layer | L0_infrastructure |
| 模块数 | 107 | Module Count | 107 |
| 域内依赖 | 79 | Internal Dependencies | 79 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 51 | Cross-domain Outgoing | 51 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 107 | Production Modules | 107 |
| 容量 | 107/150 (正常) | Capacity | 107/150 (正常) |

## 模块清单 / Module List

共 107 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| src/zephyr/infrastructure/auto_fix_engine/__init__.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/__main__.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/alignment_syncer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/all_completer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/batch_fixer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/compliance_auditor.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/config_fixer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/dedup_extractor.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/dep_version_fixer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/drift_fixer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/engine.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/escalation_bridge.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/event_hooks.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_budget.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_diff.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_health_check.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_pattern_miner.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_reliability.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_report.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_safety.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/import_fixer.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/llm_fix_adapter.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/models.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/scaffold_registrar.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/shadow_workspace.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/state_machine.py |  | production | generated |
| src/zephyr/infrastructure/auto_fix_engine/zombie_cleaner.py |  | production | generated |
| src/zephyr/infrastructure/reliability/__init__.py |  | production | generated |
| src/zephyr/infrastructure/reliability/circuit_breaker.py |  | production | generated |
| src/zephyr/infrastructure/reliability/context_guard.py |  | production | generated |
| src/zephyr/infrastructure/rollback/__init__.py |  | production | generated |
| src/zephyr/infrastructure/rollback/_manifest.py |  | production | generated |
| src/zephyr/infrastructure/rollback/agent_cooldown.py |  | production | generated |
| src/zephyr/infrastructure/rollback/auditor.py |  | production | generated |
| src/zephyr/infrastructure/rollback/auto_rollback_trigger.py |  | production | generated |
| src/zephyr/infrastructure/rollback/autonomy_dashboard.py |  | production | generated |
| src/zephyr/infrastructure/rollback/backtest_engine.py |  | production | generated |
| src/zephyr/infrastructure/rollback/budget_tracker.py |  | production | generated |
| src/zephyr/infrastructure/rollback/checkpoint_gc.py |  | production | generated |
| src/zephyr/infrastructure/rollback/commit_quality_gate.py |  | production | generated |
| src/zephyr/infrastructure/rollback/complexity_budget.py |  | production | generated |
| src/zephyr/infrastructure/rollback/confidence_quantifier.py |  | production | generated |
| src/zephyr/infrastructure/rollback/continuous_trust.py |  | production | generated |
| src/zephyr/infrastructure/rollback/contract.py |  | production | generated |
| src/zephyr/infrastructure/rollback/contracts.py |  | production | generated |
| src/zephyr/infrastructure/rollback/credential_rotation_trigger.py |  | production | generated |
| src/zephyr/infrastructure/rollback/cross_agent_conflict_detector.py |  | production | generated |
| src/zephyr/infrastructure/rollback/cross_platform_shell.py |  | production | generated |
| src/zephyr/infrastructure/rollback/down_migration_generator.py |  | production | generated |
| src/zephyr/infrastructure/rollback/drift_fix.py |  | production | generated |
| src/zephyr/infrastructure/rollback/env_watcher.py |  | production | generated |
| src/zephyr/infrastructure/rollback/external_merkle_proof.py |  | production | generated |
| src/zephyr/infrastructure/rollback/fault_tolerance.py |  | production | generated |
| src/zephyr/infrastructure/rollback/forensic.py |  | production | generated |
| src/zephyr/infrastructure/rollback/forward_fix_runner.py |  | production | generated |
| src/zephyr/infrastructure/rollback/fsm_verifier.py |  | production | generated |
| src/zephyr/infrastructure/rollback/git_infra_snapshot.py |  | production | generated |
| src/zephyr/infrastructure/rollback/hallucination_guard.py |  | production | generated |
| src/zephyr/infrastructure/rollback/intent_archiver.py |  | production | generated |
| src/zephyr/infrastructure/rollback/kill_switch.py |  | production | generated |
| src/zephyr/infrastructure/rollback/knowngoodstate_ledger.py |  | production | generated |
| src/zephyr/infrastructure/rollback/llm_impact_analyzer.py |  | production | generated |
| src/zephyr/infrastructure/rollback/model_drift_detector.py |  | production | generated |
| src/zephyr/infrastructure/rollback/owner_absent.py |  | production | generated |
| src/zephyr/infrastructure/rollback/paper_live_transition.py |  | production | generated |
| src/zephyr/infrastructure/rollback/phase_check_registry.py |  | production | generated |
| src/zephyr/infrastructure/rollback/phase_manager.py |  | production | generated |
| src/zephyr/infrastructure/rollback/post_live_verification.py |  | production | generated |
| src/zephyr/infrastructure/rollback/result_types.py |  | production | generated |
| src/zephyr/infrastructure/rollback/right_to_be_forgotten.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_abuse_detector.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_audit_nexus.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_boot_integration.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_bootstrap.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_budget.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_context_restorer.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_dashboard.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_drill.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_executor.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_integration.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_lock.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_loop_detector.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_scheduler.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_simulator.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_state_machine.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_target_staleness.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_verifier.py |  | production | generated |
| src/zephyr/infrastructure/rollback/rollback_wal.py |  | production | generated |
| src/zephyr/infrastructure/rollback/runbook_generator.py |  | production | generated |
| src/zephyr/infrastructure/rollback/s3_snapshot_lifecycle.py |  | production | generated |
| src/zephyr/infrastructure/rollback/sandbox_enforcer.py |  | production | generated |
| src/zephyr/infrastructure/rollback/secret_rotation_aware.py |  | production | generated |
| src/zephyr/infrastructure/rollback/semantic_rollback_tag.py |  | production | generated |
| src/zephyr/infrastructure/rollback/semantic_similar_detector.py |  | production | generated |
| src/zephyr/infrastructure/rollback/sqlite_dumper.py |  | production | generated |
| src/zephyr/infrastructure/rollback/startup_shutdown.py |  | production | generated |
| src/zephyr/infrastructure/rollback/startup_shutdown_cli.py |  | production | generated |
| src/zephyr/infrastructure/rollback/submodule_sync.py |  | production | generated |
| src/zephyr/infrastructure/rollback/temporal_context_adapter.py |  | production | generated |
| src/zephyr/infrastructure/rollback/topology_change_log.py |  | production | generated |
| src/zephyr/infrastructure/rollback/trading_kill_switch.py |  | production | generated |
| src/zephyr/infrastructure/rollback/venv_sync.py |  | production | generated |
| src/zephyr/infrastructure/rollback/vulnerability_rescanner.py |  | production | generated |
| src/zephyr/infrastructure/rollback/warm_standby.py |  | production | generated |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 4 页 / Page 1 of 4

```mermaid
graph TD
    subgraph D_INFRA_RECOVERY["D-INFRA_RECOVERY rollback_recovery"]
        src_zephyr_infrastructure_auto_fix_engine_init_py["src/zephyr/infrastructure/auto_fix_engine/__ini... production"]
        src_zephyr_infrastructure_auto_fix_engine_main_py["src/zephyr/infrastructure/auto_fix_engine/__mai... production"]
        src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py["src/zephyr/infrastructure/auto_fix_engine/align... production"]
        src_zephyr_infrastructure_auto_fix_engine_all_completer_py["src/zephyr/infrastructure/auto_fix_engine/all_c... production"]
        src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py["src/zephyr/infrastructure/auto_fix_engine/batch... production"]
        src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py["src/zephyr/infrastructure/auto_fix_engine/compl... production"]
        src_zephyr_infrastructure_auto_fix_engine_config_fixer_py["src/zephyr/infrastructure/auto_fix_engine/confi... production"]
        src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py["src/zephyr/infrastructure/auto_fix_engine/dedup... production"]
        src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py["src/zephyr/infrastructure/auto_fix_engine/dep_v... production"]
        src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py["src/zephyr/infrastructure/auto_fix_engine/drift... production"]
        src_zephyr_infrastructure_auto_fix_engine_engine_py["src/zephyr/infrastructure/auto_fix_engine/engin... production"]
        src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py["src/zephyr/infrastructure/auto_fix_engine/escal... production"]
        src_zephyr_infrastructure_auto_fix_engine_event_hooks_py["src/zephyr/infrastructure/auto_fix_engine/event... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_budget_py["src/zephyr/infrastructure/auto_fix_engine/fix_b... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_diff_py["src/zephyr/infrastructure/auto_fix_engine/fix_d... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py["src/zephyr/infrastructure/auto_fix_engine/fix_h... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py["src/zephyr/infrastructure/auto_fix_engine/fix_p... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py["src/zephyr/infrastructure/auto_fix_engine/fix_r... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_report_py["src/zephyr/infrastructure/auto_fix_engine/fix_r... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_safety_py["src/zephyr/infrastructure/auto_fix_engine/fix_s... production"]
        src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py["src/zephyr/infrastructure/auto_fix_engine/fix_s... production"]
        src_zephyr_infrastructure_auto_fix_engine_import_fixer_py["src/zephyr/infrastructure/auto_fix_engine/impor... production"]
        src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py["src/zephyr/infrastructure/auto_fix_engine/inter... production"]
        src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py["src/zephyr/infrastructure/auto_fix_engine/llm_f... production"]
        src_zephyr_infrastructure_auto_fix_engine_models_py["src/zephyr/infrastructure/auto_fix_engine/model... production"]
        src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py["src/zephyr/infrastructure/auto_fix_engine/scaff... production"]
        src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py["src/zephyr/infrastructure/auto_fix_engine/self_... production"]
        src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py["src/zephyr/infrastructure/auto_fix_engine/shado... production"]
        src_zephyr_infrastructure_auto_fix_engine_state_machine_py["src/zephyr/infrastructure/auto_fix_engine/state... production"]
        src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py["src/zephyr/infrastructure/auto_fix_engine/zombi... production"]
    end
    src_zephyr_infrastructure_auto_fix_engine_models_py -->|config_depends| src_zephyr_infrastructure_auto_fix_engine_init_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_all_completer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_config_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_event_hooks_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_import_fixer_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py
    src_zephyr_infrastructure_auto_fix_engine_init_py -->|import_depends| src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py
    D_INFRA_RUNTIME["D-INFRA_RUNTIME production"]
    src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_all_completer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_engine_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["D-GOVERNANCE production"]
    src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py -->|import_depends| D_GOVERNANCE
    src_zephyr_infrastructure_auto_fix_engine_config_fixer_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_event_hooks_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_fix_budget_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_auto_fix_engine_fix_diff_py -->|import_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_auto_fix_engine_init_py,src_zephyr_infrastructure_auto_fix_engine_main_py,src_zephyr_infrastructure_auto_fix_engine_alignment_syncer_py,src_zephyr_infrastructure_auto_fix_engine_all_completer_py,src_zephyr_infrastructure_auto_fix_engine_batch_fixer_py,src_zephyr_infrastructure_auto_fix_engine_compliance_auditor_py,src_zephyr_infrastructure_auto_fix_engine_config_fixer_py,src_zephyr_infrastructure_auto_fix_engine_dedup_extractor_py,src_zephyr_infrastructure_auto_fix_engine_dep_version_fixer_py,src_zephyr_infrastructure_auto_fix_engine_drift_fixer_py,src_zephyr_infrastructure_auto_fix_engine_engine_py,src_zephyr_infrastructure_auto_fix_engine_escalation_bridge_py,src_zephyr_infrastructure_auto_fix_engine_event_hooks_py,src_zephyr_infrastructure_auto_fix_engine_fix_budget_py,src_zephyr_infrastructure_auto_fix_engine_fix_diff_py,src_zephyr_infrastructure_auto_fix_engine_fix_health_check_py,src_zephyr_infrastructure_auto_fix_engine_fix_pattern_miner_py,src_zephyr_infrastructure_auto_fix_engine_fix_reliability_py,src_zephyr_infrastructure_auto_fix_engine_fix_report_py,src_zephyr_infrastructure_auto_fix_engine_fix_safety_py,src_zephyr_infrastructure_auto_fix_engine_fix_scheduler_py,src_zephyr_infrastructure_auto_fix_engine_import_fixer_py,src_zephyr_infrastructure_auto_fix_engine_interrupt_guard_py,src_zephyr_infrastructure_auto_fix_engine_llm_fix_adapter_py,src_zephyr_infrastructure_auto_fix_engine_models_py,src_zephyr_infrastructure_auto_fix_engine_scaffold_registrar_py,src_zephyr_infrastructure_auto_fix_engine_self_heal_agent_py,src_zephyr_infrastructure_auto_fix_engine_shadow_workspace_py,src_zephyr_infrastructure_auto_fix_engine_state_machine_py,src_zephyr_infrastructure_auto_fix_engine_zombie_cleaner_py production
    class D_INFRA_RUNTIME,D_GOVERNANCE external_prod
```

### 第 2 页 / 共 4 页 / Page 2 of 4

```mermaid
graph TD
    subgraph D_INFRA_RECOVERY["D-INFRA_RECOVERY rollback_recovery"]
        src_zephyr_infrastructure_reliability_init_py["src/zephyr/infrastructure/reliability/__init__.py production"]
        src_zephyr_infrastructure_reliability_circuit_breaker_py["src/zephyr/infrastructure/reliability/circuit_b... production"]
        src_zephyr_infrastructure_reliability_context_guard_py["src/zephyr/infrastructure/reliability/context_g... production"]
        src_zephyr_infrastructure_rollback_init_py["src/zephyr/infrastructure/rollback/__init__.py production"]
        src_zephyr_infrastructure_rollback_manifest_py["src/zephyr/infrastructure/rollback/_manifest.py production"]
        src_zephyr_infrastructure_rollback_agent_cooldown_py["src/zephyr/infrastructure/rollback/agent_cooldo... production"]
        src_zephyr_infrastructure_rollback_auditor_py["src/zephyr/infrastructure/rollback/auditor.py production"]
        src_zephyr_infrastructure_rollback_auto_rollback_trigger_py["src/zephyr/infrastructure/rollback/auto_rollbac... production"]
        src_zephyr_infrastructure_rollback_autonomy_dashboard_py["src/zephyr/infrastructure/rollback/autonomy_das... production"]
        src_zephyr_infrastructure_rollback_backtest_engine_py["src/zephyr/infrastructure/rollback/backtest_eng... production"]
        src_zephyr_infrastructure_rollback_budget_tracker_py["src/zephyr/infrastructure/rollback/budget_track... production"]
        src_zephyr_infrastructure_rollback_checkpoint_gc_py["src/zephyr/infrastructure/rollback/checkpoint_g... production"]
        src_zephyr_infrastructure_rollback_commit_quality_gate_py["src/zephyr/infrastructure/rollback/commit_quali... production"]
        src_zephyr_infrastructure_rollback_complexity_budget_py["src/zephyr/infrastructure/rollback/complexity_b... production"]
        src_zephyr_infrastructure_rollback_confidence_quantifier_py["src/zephyr/infrastructure/rollback/confidence_q... production"]
        src_zephyr_infrastructure_rollback_continuous_trust_py["src/zephyr/infrastructure/rollback/continuous_t... production"]
        src_zephyr_infrastructure_rollback_contract_py["src/zephyr/infrastructure/rollback/contract.py production"]
        src_zephyr_infrastructure_rollback_contracts_py["src/zephyr/infrastructure/rollback/contracts.py production"]
        src_zephyr_infrastructure_rollback_credential_rotation_trigger_py["src/zephyr/infrastructure/rollback/credential_r... production"]
        src_zephyr_infrastructure_rollback_cross_agent_conflict_detector_py["src/zephyr/infrastructure/rollback/cross_agent_... production"]
        src_zephyr_infrastructure_rollback_cross_platform_shell_py["src/zephyr/infrastructure/rollback/cross_platfo... production"]
        src_zephyr_infrastructure_rollback_down_migration_generator_py["src/zephyr/infrastructure/rollback/down_migrati... production"]
        src_zephyr_infrastructure_rollback_drift_fix_py["src/zephyr/infrastructure/rollback/drift_fix.py production"]
        src_zephyr_infrastructure_rollback_env_watcher_py["src/zephyr/infrastructure/rollback/env_watcher.py production"]
        src_zephyr_infrastructure_rollback_external_merkle_proof_py["src/zephyr/infrastructure/rollback/external_mer... production"]
        src_zephyr_infrastructure_rollback_fault_tolerance_py["src/zephyr/infrastructure/rollback/fault_tolera... production"]
        src_zephyr_infrastructure_rollback_forensic_py["src/zephyr/infrastructure/rollback/forensic.py production"]
        src_zephyr_infrastructure_rollback_forward_fix_runner_py["src/zephyr/infrastructure/rollback/forward_fix_... production"]
        src_zephyr_infrastructure_rollback_fsm_verifier_py["src/zephyr/infrastructure/rollback/fsm_verifier.py production"]
        src_zephyr_infrastructure_rollback_git_infra_snapshot_py["src/zephyr/infrastructure/rollback/git_infra_sn... production"]
    end
    src_zephyr_infrastructure_reliability_init_py -->|import_depends| src_zephyr_infrastructure_reliability_circuit_breaker_py
    src_zephyr_infrastructure_reliability_init_py -->|import_depends| src_zephyr_infrastructure_reliability_context_guard_py
    src_zephyr_infrastructure_rollback_auto_rollback_trigger_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_backtest_engine_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_continuous_trust_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_contract_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_cross_agent_conflict_detector_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_credential_rotation_trigger_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_manifest_py -->|config_depends| src_zephyr_infrastructure_rollback_init_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_agent_cooldown_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_autonomy_dashboard_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_auditor_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_complexity_budget_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_checkpoint_gc_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_budget_tracker_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_confidence_quantifier_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_commit_quality_gate_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_down_migration_generator_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_cross_platform_shell_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_external_merkle_proof_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_forensic_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_forward_fix_runner_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_fault_tolerance_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_env_watcher_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_fsm_verifier_py
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| src_zephyr_infrastructure_rollback_git_infra_snapshot_py
    D_INFRA_RUNTIME["D-INFRA_RUNTIME production"]
    src_zephyr_infrastructure_reliability_init_py -->|import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT["D-GOV_AUDIT production"]
    src_zephyr_infrastructure_rollback_auditor_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_infrastructure_rollback_contracts_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_infrastructure_rollback_init_py -->|import_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_reliability_init_py,src_zephyr_infrastructure_reliability_circuit_breaker_py,src_zephyr_infrastructure_reliability_context_guard_py,src_zephyr_infrastructure_rollback_init_py,src_zephyr_infrastructure_rollback_manifest_py,src_zephyr_infrastructure_rollback_agent_cooldown_py,src_zephyr_infrastructure_rollback_auditor_py,src_zephyr_infrastructure_rollback_auto_rollback_trigger_py,src_zephyr_infrastructure_rollback_autonomy_dashboard_py,src_zephyr_infrastructure_rollback_backtest_engine_py,src_zephyr_infrastructure_rollback_budget_tracker_py,src_zephyr_infrastructure_rollback_checkpoint_gc_py,src_zephyr_infrastructure_rollback_commit_quality_gate_py,src_zephyr_infrastructure_rollback_complexity_budget_py,src_zephyr_infrastructure_rollback_confidence_quantifier_py,src_zephyr_infrastructure_rollback_continuous_trust_py,src_zephyr_infrastructure_rollback_contract_py,src_zephyr_infrastructure_rollback_contracts_py,src_zephyr_infrastructure_rollback_credential_rotation_trigger_py,src_zephyr_infrastructure_rollback_cross_agent_conflict_detector_py,src_zephyr_infrastructure_rollback_cross_platform_shell_py,src_zephyr_infrastructure_rollback_down_migration_generator_py,src_zephyr_infrastructure_rollback_drift_fix_py,src_zephyr_infrastructure_rollback_env_watcher_py,src_zephyr_infrastructure_rollback_external_merkle_proof_py,src_zephyr_infrastructure_rollback_fault_tolerance_py,src_zephyr_infrastructure_rollback_forensic_py,src_zephyr_infrastructure_rollback_forward_fix_runner_py,src_zephyr_infrastructure_rollback_fsm_verifier_py,src_zephyr_infrastructure_rollback_git_infra_snapshot_py production
    class D_INFRA_RUNTIME,D_GOV_AUDIT external_prod
```

### 第 3 页 / 共 4 页 / Page 3 of 4

```mermaid
graph TD
    subgraph D_INFRA_RECOVERY["D-INFRA_RECOVERY rollback_recovery"]
        src_zephyr_infrastructure_rollback_hallucination_guard_py["src/zephyr/infrastructure/rollback/hallucinatio... production"]
        src_zephyr_infrastructure_rollback_intent_archiver_py["src/zephyr/infrastructure/rollback/intent_archi... production"]
        src_zephyr_infrastructure_rollback_kill_switch_py["src/zephyr/infrastructure/rollback/kill_switch.py production"]
        src_zephyr_infrastructure_rollback_knowngoodstate_ledger_py["src/zephyr/infrastructure/rollback/knowngoodsta... production"]
        src_zephyr_infrastructure_rollback_llm_impact_analyzer_py["src/zephyr/infrastructure/rollback/llm_impact_a... production"]
        src_zephyr_infrastructure_rollback_model_drift_detector_py["src/zephyr/infrastructure/rollback/model_drift_... production"]
        src_zephyr_infrastructure_rollback_owner_absent_py["src/zephyr/infrastructure/rollback/owner_absent.py production"]
        src_zephyr_infrastructure_rollback_paper_live_transition_py["src/zephyr/infrastructure/rollback/paper_live_t... production"]
        src_zephyr_infrastructure_rollback_phase_check_registry_py["src/zephyr/infrastructure/rollback/phase_check_... production"]
        src_zephyr_infrastructure_rollback_phase_manager_py["src/zephyr/infrastructure/rollback/phase_manage... production"]
        src_zephyr_infrastructure_rollback_post_live_verification_py["src/zephyr/infrastructure/rollback/post_live_ve... production"]
        src_zephyr_infrastructure_rollback_result_types_py["src/zephyr/infrastructure/rollback/result_types.py production"]
        src_zephyr_infrastructure_rollback_right_to_be_forgotten_py["src/zephyr/infrastructure/rollback/right_to_be_... production"]
        src_zephyr_infrastructure_rollback_rollback_abuse_detector_py["src/zephyr/infrastructure/rollback/rollback_abu... production"]
        src_zephyr_infrastructure_rollback_rollback_audit_nexus_py["src/zephyr/infrastructure/rollback/rollback_aud... production"]
        src_zephyr_infrastructure_rollback_rollback_boot_integration_py["src/zephyr/infrastructure/rollback/rollback_boo... production"]
        src_zephyr_infrastructure_rollback_rollback_bootstrap_py["src/zephyr/infrastructure/rollback/rollback_boo... production"]
        src_zephyr_infrastructure_rollback_rollback_budget_py["src/zephyr/infrastructure/rollback/rollback_bud... production"]
        src_zephyr_infrastructure_rollback_rollback_context_restorer_py["src/zephyr/infrastructure/rollback/rollback_con... production"]
        src_zephyr_infrastructure_rollback_rollback_dashboard_py["src/zephyr/infrastructure/rollback/rollback_das... production"]
        src_zephyr_infrastructure_rollback_rollback_drill_py["src/zephyr/infrastructure/rollback/rollback_dri... production"]
        src_zephyr_infrastructure_rollback_rollback_executor_py["src/zephyr/infrastructure/rollback/rollback_exe... production"]
        src_zephyr_infrastructure_rollback_rollback_integration_py["src/zephyr/infrastructure/rollback/rollback_int... production"]
        src_zephyr_infrastructure_rollback_rollback_lock_py["src/zephyr/infrastructure/rollback/rollback_loc... production"]
        src_zephyr_infrastructure_rollback_rollback_loop_detector_py["src/zephyr/infrastructure/rollback/rollback_loo... production"]
        src_zephyr_infrastructure_rollback_rollback_scheduler_py["src/zephyr/infrastructure/rollback/rollback_sch... production"]
        src_zephyr_infrastructure_rollback_rollback_simulator_py["src/zephyr/infrastructure/rollback/rollback_sim... production"]
        src_zephyr_infrastructure_rollback_rollback_state_machine_py["src/zephyr/infrastructure/rollback/rollback_sta... production"]
        src_zephyr_infrastructure_rollback_rollback_target_staleness_py["src/zephyr/infrastructure/rollback/rollback_tar... production"]
        src_zephyr_infrastructure_rollback_rollback_verifier_py["src/zephyr/infrastructure/rollback/rollback_ver... production"]
    end
    D_SHARED["D-SHARED production"]
    src_zephyr_infrastructure_rollback_phase_check_registry_py -->|import_depends| D_SHARED
    D_INTEGRATION["D-INTEGRATION prototype"]
    src_zephyr_infrastructure_rollback_phase_check_registry_py -.->|import_depends| D_INTEGRATION
    src_zephyr_infrastructure_rollback_phase_check_registry_py -.->|import_depends| D_INTEGRATION
    src_zephyr_infrastructure_rollback_phase_check_registry_py -.->|import_depends| D_SHARED
    D_GOV_AUDIT["D-GOV_AUDIT prototype"]
    src_zephyr_infrastructure_rollback_phase_check_registry_py -.->|import_depends| D_GOV_AUDIT
    src_zephyr_infrastructure_rollback_phase_check_registry_py -->|import_depends| D_GOV_AUDIT
    D_GOVERNANCE["D-GOVERNANCE production"]
    src_zephyr_infrastructure_rollback_phase_check_registry_py -->|import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["D-INFRA_RUNTIME production"]
    src_zephyr_infrastructure_rollback_phase_check_registry_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_rollback_phase_check_registry_py -->|import_depends| D_GOVERNANCE
    src_zephyr_infrastructure_rollback_rollback_abuse_detector_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_infrastructure_rollback_rollback_audit_nexus_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_infrastructure_rollback_phase_manager_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_rollback_rollback_integration_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_rollback_rollback_executor_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_rollback_rollback_executor_py -->|import_depends| D_GOV_AUDIT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_rollback_hallucination_guard_py,src_zephyr_infrastructure_rollback_intent_archiver_py,src_zephyr_infrastructure_rollback_kill_switch_py,src_zephyr_infrastructure_rollback_knowngoodstate_ledger_py,src_zephyr_infrastructure_rollback_llm_impact_analyzer_py,src_zephyr_infrastructure_rollback_model_drift_detector_py,src_zephyr_infrastructure_rollback_owner_absent_py,src_zephyr_infrastructure_rollback_paper_live_transition_py,src_zephyr_infrastructure_rollback_phase_check_registry_py,src_zephyr_infrastructure_rollback_phase_manager_py,src_zephyr_infrastructure_rollback_post_live_verification_py,src_zephyr_infrastructure_rollback_result_types_py,src_zephyr_infrastructure_rollback_right_to_be_forgotten_py,src_zephyr_infrastructure_rollback_rollback_abuse_detector_py,src_zephyr_infrastructure_rollback_rollback_audit_nexus_py,src_zephyr_infrastructure_rollback_rollback_boot_integration_py,src_zephyr_infrastructure_rollback_rollback_bootstrap_py,src_zephyr_infrastructure_rollback_rollback_budget_py,src_zephyr_infrastructure_rollback_rollback_context_restorer_py,src_zephyr_infrastructure_rollback_rollback_dashboard_py,src_zephyr_infrastructure_rollback_rollback_drill_py,src_zephyr_infrastructure_rollback_rollback_executor_py,src_zephyr_infrastructure_rollback_rollback_integration_py,src_zephyr_infrastructure_rollback_rollback_lock_py,src_zephyr_infrastructure_rollback_rollback_loop_detector_py,src_zephyr_infrastructure_rollback_rollback_scheduler_py,src_zephyr_infrastructure_rollback_rollback_simulator_py,src_zephyr_infrastructure_rollback_rollback_state_machine_py,src_zephyr_infrastructure_rollback_rollback_target_staleness_py,src_zephyr_infrastructure_rollback_rollback_verifier_py production
    class D_SHARED,D_GOVERNANCE,D_INFRA_RUNTIME external_prod
    class D_INTEGRATION,D_GOV_AUDIT external_design
```

### 第 4 页 / 共 4 页 / Page 4 of 4

```mermaid
graph TD
    subgraph D_INFRA_RECOVERY["D-INFRA_RECOVERY rollback_recovery"]
        src_zephyr_infrastructure_rollback_rollback_wal_py["src/zephyr/infrastructure/rollback/rollback_wal.py production"]
        src_zephyr_infrastructure_rollback_runbook_generator_py["src/zephyr/infrastructure/rollback/runbook_gene... production"]
        src_zephyr_infrastructure_rollback_s3_snapshot_lifecycle_py["src/zephyr/infrastructure/rollback/s3_snapshot_... production"]
        src_zephyr_infrastructure_rollback_sandbox_enforcer_py["src/zephyr/infrastructure/rollback/sandbox_enfo... production"]
        src_zephyr_infrastructure_rollback_secret_rotation_aware_py["src/zephyr/infrastructure/rollback/secret_rotat... production"]
        src_zephyr_infrastructure_rollback_semantic_rollback_tag_py["src/zephyr/infrastructure/rollback/semantic_rol... production"]
        src_zephyr_infrastructure_rollback_semantic_similar_detector_py["src/zephyr/infrastructure/rollback/semantic_sim... production"]
        src_zephyr_infrastructure_rollback_sqlite_dumper_py["src/zephyr/infrastructure/rollback/sqlite_dumpe... production"]
        src_zephyr_infrastructure_rollback_startup_shutdown_py["src/zephyr/infrastructure/rollback/startup_shut... production"]
        src_zephyr_infrastructure_rollback_startup_shutdown_cli_py["src/zephyr/infrastructure/rollback/startup_shut... production"]
        src_zephyr_infrastructure_rollback_submodule_sync_py["src/zephyr/infrastructure/rollback/submodule_sy... production"]
        src_zephyr_infrastructure_rollback_temporal_context_adapter_py["src/zephyr/infrastructure/rollback/temporal_con... production"]
        src_zephyr_infrastructure_rollback_topology_change_log_py["src/zephyr/infrastructure/rollback/topology_cha... production"]
        src_zephyr_infrastructure_rollback_trading_kill_switch_py["src/zephyr/infrastructure/rollback/trading_kill... production"]
        src_zephyr_infrastructure_rollback_venv_sync_py["src/zephyr/infrastructure/rollback/venv_sync.py production"]
        src_zephyr_infrastructure_rollback_vulnerability_rescanner_py["src/zephyr/infrastructure/rollback/vulnerabilit... production"]
        src_zephyr_infrastructure_rollback_warm_standby_py["src/zephyr/infrastructure/rollback/warm_standby.py production"]
    end
    D_SHARED["D-SHARED prototype"]
    src_zephyr_infrastructure_rollback_sqlite_dumper_py -.->|import_depends| D_SHARED
    D_GOVERNANCE["D-GOVERNANCE production"]
    src_zephyr_infrastructure_rollback_sqlite_dumper_py -->|import_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_rollback_rollback_wal_py,src_zephyr_infrastructure_rollback_runbook_generator_py,src_zephyr_infrastructure_rollback_s3_snapshot_lifecycle_py,src_zephyr_infrastructure_rollback_sandbox_enforcer_py,src_zephyr_infrastructure_rollback_secret_rotation_aware_py,src_zephyr_infrastructure_rollback_semantic_rollback_tag_py,src_zephyr_infrastructure_rollback_semantic_similar_detector_py,src_zephyr_infrastructure_rollback_sqlite_dumper_py,src_zephyr_infrastructure_rollback_startup_shutdown_py,src_zephyr_infrastructure_rollback_startup_shutdown_cli_py,src_zephyr_infrastructure_rollback_submodule_sync_py,src_zephyr_infrastructure_rollback_temporal_context_adapter_py,src_zephyr_infrastructure_rollback_topology_change_log_py,src_zephyr_infrastructure_rollback_trading_kill_switch_py,src_zephyr_infrastructure_rollback_venv_sync_py,src_zephyr_infrastructure_rollback_vulnerability_rescanner_py,src_zephyr_infrastructure_rollback_warm_standby_py production
    class D_GOVERNANCE external_prod
    class D_SHARED external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D-INFRA_RUNTIME | 33 | import_depends |
| D-GOV_AUDIT | 7 | import_depends |
| D-SHARED | 5 | import_depends |
| D-GOVERNANCE | 4 | import_depends |
| D-INTEGRATION | 2 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
