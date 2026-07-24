---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 209 |
| Open（未解决） | 209 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 103 |
| hard | 6 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 6 |
| cross_domain_violation | 86 |
| hard_limit_exceeded | 6 |
| layer_violation | 10 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-7035230 | 孤儿节点: 7035230 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 7035230 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-7035231 | 孤儿节点: 7035231 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 7035231 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-7035232 | 孤儿节点: 7035232 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 7035232 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-7035233 | 孤儿节点: 7035233 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 7035233 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-7035358 | 孤儿节点: 7035358 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 7035358 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-7035379 | 孤儿节点: 7035379 | orphan_node |  |  | warn | advisory | 节点 7035379 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-7035416 | 孤儿节点: 7035416 | orphan_node | D_DATA |  | warn | advisory | 节点 7035416 路径 src/zephyr/data/kline_resampler.py 未注册到目录树 |
| V-ORPHAN-7035433 | 孤儿节点: 7035433 | orphan_node | D_DATA |  | warn | advisory | 节点 7035433 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-7035525 | 孤儿节点: 7035525 | orphan_node | D_FEEDBACK_LOOP |  | warn | advisory | 节点 7035525 路径 src/zephyr/feedback_loop/config.py 未注册到目录树 |
| V-ORPHAN-7035563 | 孤儿节点: 7035563 | orphan_node | D_FEEDBACK_LOOP |  | warn | advisory | 节点 7035563 路径 src/zephyr/feedback_loop/collectors/calendar_a... |
| V-ORPHAN-7035564 | 孤儿节点: 7035564 | orphan_node | D_FEEDBACK_LOOP |  | warn | advisory | 节点 7035564 路径 src/zephyr/feedback_loop/collectors/config_tim... |
| V-ORPHAN-7035576 | 孤儿节点: 7035576 | orphan_node | D_FEEDBACK_LOOP |  | warn | advisory | 节点 7035576 路径 src/zephyr/feedback_loop/collectors/token_fino... |
| V-ORPHAN-7035591 | 孤儿节点: 7035591 | orphan_node | D_FBL_DETECTORS |  | warn | advisory | 节点 7035591 路径 src/zephyr/feedback_loop/detectors/anomaly/tem... |
| V-ORPHAN-7035638 | 孤儿节点: 7035638 | orphan_node | D_FBL_DETECTORS |  | warn | advisory | 节点 7035638 路径 src/zephyr/feedback_loop/detectors/reliability... |
| V-ORPHAN-7035745 | 孤儿节点: 7035745 | orphan_node | D_FEEDBACK_LOOP |  | warn | advisory | 节点 7035745 路径 src/zephyr/feedback_loop/forensic/automated_rc... |
| V-ORPHAN-7035776 | 孤儿节点: 7035776 | orphan_node | D_FBL_VERIFICATION |  | warn | advisory | 节点 7035776 路径 src/zephyr/feedback_loop/gates/conflict_arbitr... |
| V-ORPHAN-7035836 | 孤儿节点: 7035836 | orphan_node | D_FBL_VERIFICATION |  | warn | advisory | 节点 7035836 路径 src/zephyr/feedback_loop/verifiers/attack_simu... |
| V-ORPHAN-7035979 | 孤儿节点: 7035979 | orphan_node | D_GOV_OPS_RESILIENCE |  | warn | advisory | 节点 7035979 路径 src/zephyr/governance/escalation/human_factors... |
| V-ORPHAN-7036006 | 孤儿节点: 7036006 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 7036006 路径 src/zephyr/governance/intelligence_governance/... |
| V-ORPHAN-7036278 | 孤儿节点: 7036278 | orphan_node | D_GOV_CODE_QUALITY |  | warn | advisory | 节点 7036278 路径 src/zephyr/gov_code_quality/code_dedup/self_sc... |
| V-ORPHAN-7036375 | 孤儿节点: 7036375 | orphan_node | D_GOV_AUDIT |  | warn | advisory | 节点 7036375 路径 src/zephyr/gov_enforcement/behavioral_admissio... |
| V-ORPHAN-7036401 | 孤儿节点: 7036401 | orphan_node | D_GOV_CODE_QUALITY |  | warn | advisory | 节点 7036401 路径 src/zephyr/gov_enforcement/commit_gates/ch_fin... |
| V-ORPHAN-7036445 | 孤儿节点: 7036445 | orphan_node | D_GOV_CODE_QUALITY |  | warn | advisory | 节点 7036445 路径 src/zephyr/gov_enforcement/commit_gates/noqa_v... |
| V-ORPHAN-7036560 | 孤儿节点: 7036560 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 7036560 路径 src/zephyr/infrastructure/git_batcher.py 未注册到目... |
| V-ORPHAN-7036787 | 孤儿节点: 7036787 | orphan_node | D_INFRA_RECOVERY |  | warn | advisory | 节点 7036787 路径 src/zephyr/infrastructure/rollback/forensic.py... |
| V-ORPHAN-7036940 | 孤儿节点: 7036940 | orphan_node |  |  | warn | advisory | 节点 7036940 路径 src/zephyr/intelligence/__init__.py 未注册到目录树 |
| V-ORPHAN-7037620 | 孤儿节点: 7037620 | orphan_node |  |  | warn | advisory | 节点 7037620 路径 src/zephyr/signal_quality/infrastructure/__ini... |
| V-ORPHAN-7037622 | 孤儿节点: 7037622 | orphan_node |  |  | warn | advisory | 节点 7037622 路径 src/zephyr/signal_quality/core/__init__.py 未注册... |
| V-ORPHAN-7037623 | 孤儿节点: 7037623 | orphan_node |  |  | warn | advisory | 节点 7037623 路径 src/zephyr/signal_quality/_extensions/__init__... |
| V-ORPHAN-7037624 | 孤儿节点: 7037624 | orphan_node |  |  | warn | advisory | 节点 7037624 路径 src/zephyr/signal_quality/services/__init__.py... |
| V-ORPHAN-7037773 | 孤儿节点: 7037773 | orphan_node |  |  | warn | advisory | 节点 7037773 路径 scripts/ch/_check_backup.py 未注册到目录树 |
| V-ORPHAN-7037774 | 孤儿节点: 7037774 | orphan_node |  |  | warn | advisory | 节点 7037774 路径 scripts/ch/_check_backup_status.py 未注册到目录树 |
| V-ORPHAN-7037775 | 孤儿节点: 7037775 | orphan_node |  |  | warn | advisory | 节点 7037775 路径 scripts/ch/_check_queries.py 未注册到目录树 |
| V-ORPHAN-7037776 | 孤儿节点: 7037776 | orphan_node |  |  | warn | advisory | 节点 7037776 路径 scripts/ch/_check_ch_processes.py 未注册到目录树 |
| V-ORPHAN-7037777 | 孤儿节点: 7037777 | orphan_node |  |  | warn | advisory | 节点 7037777 路径 scripts/ch/_check_engine.py 未注册到目录树 |
| V-ORPHAN-7037779 | 孤儿节点: 7037779 | orphan_node |  |  | warn | advisory | 节点 7037779 路径 scripts/ch/_check_adj_factor.py 未注册到目录树 |
| V-ORPHAN-7037780 | 孤儿节点: 7037780 | orphan_node |  |  | warn | advisory | 节点 7037780 路径 scripts/ch/_check_backups_clean.py 未注册到目录树 |
| V-ORPHAN-7037781 | 孤儿节点: 7037781 | orphan_node |  |  | warn | advisory | 节点 7037781 路径 scripts/ch/_cleanup_tznew.py 未注册到目录树 |
| V-ORPHAN-7037782 | 孤儿节点: 7037782 | orphan_node |  |  | warn | advisory | 节点 7037782 路径 scripts/ch/_check_tickdata.py 未注册到目录树 |
| V-ORPHAN-7037783 | 孤儿节点: 7037783 | orphan_node |  |  | warn | advisory | 节点 7037783 路径 scripts/ch/_check_tickdata_live.py 未注册到目录树 |
| V-ORPHAN-7037784 | 孤儿节点: 7037784 | orphan_node |  |  | warn | advisory | 节点 7037784 路径 scripts/ch/_compare_partitions.py 未注册到目录树 |
| V-ORPHAN-7037785 | 孤儿节点: 7037785 | orphan_node |  |  | warn | advisory | 节点 7037785 路径 scripts/ch/_diagnose_recreate.py 未注册到目录树 |
| V-ORPHAN-7037786 | 孤儿节点: 7037786 | orphan_node |  |  | warn | advisory | 节点 7037786 路径 scripts/ch/_check_tz_state.py 未注册到目录树 |
| V-ORPHAN-7037787 | 孤儿节点: 7037787 | orphan_node |  |  | warn | advisory | 节点 7037787 路径 scripts/ch/_complete_kline_1min.py 未注册到目录树 |
| V-ORPHAN-7037788 | 孤儿节点: 7037788 | orphan_node |  |  | warn | advisory | 节点 7037788 路径 scripts/ch/_data_inventory.py 未注册到目录树 |
| V-ORPHAN-7037789 | 孤儿节点: 7037789 | orphan_node |  |  | warn | advisory | 节点 7037789 路径 scripts/ch/_diag_etf_15min.py 未注册到目录树 |
| V-ORPHAN-7037790 | 孤儿节点: 7037790 | orphan_node |  |  | warn | advisory | 节点 7037790 路径 scripts/ch/_drop_tzold.py 未注册到目录树 |
| V-ORPHAN-7037791 | 孤儿节点: 7037791 | orphan_node |  |  | warn | advisory | 节点 7037791 路径 scripts/ch/_drop_verified_tzold.py 未注册到目录树 |
| V-ORPHAN-7037792 | 孤儿节点: 7037792 | orphan_node |  |  | warn | advisory | 节点 7037792 路径 scripts/ch/_final_cleanup_tzold.py 未注册到目录树 |
| V-ORPHAN-7037793 | 孤儿节点: 7037793 | orphan_node |  |  | warn | advisory | 节点 7037793 路径 scripts/ch/_investigate_etf_15min.py 未注册到目录树 |
| V-ORPHAN-7037794 | 孤儿节点: 7037794 | orphan_node |  |  | warn | advisory | 节点 7037794 路径 scripts/ch/_monitor_tz_migration.py 未注册到目录树 |
| V-ORPHAN-7037796 | 孤儿节点: 7037796 | orphan_node |  |  | warn | advisory | 节点 7037796 路径 scripts/ch/_find_missing_rows.py 未注册到目录树 |
| V-ORPHAN-7037797 | 孤儿节点: 7037797 | orphan_node |  |  | warn | advisory | 节点 7037797 路径 scripts/ch/_force_drop_tzold.py 未注册到目录树 |
| V-ORPHAN-7037803 | 孤儿节点: 7037803 | orphan_node |  |  | warn | advisory | 节点 7037803 路径 scripts/ch/_post_tz_verify.py 未注册到目录树 |
| V-ORPHAN-7037805 | 孤儿节点: 7037805 | orphan_node |  |  | warn | advisory | 节点 7037805 路径 scripts/ch/_verify_total_final.py 未注册到目录树 |
| V-ORPHAN-7037807 | 孤儿节点: 7037807 | orphan_node |  |  | warn | advisory | 节点 7037807 路径 scripts/ch/_recovery_drill.py 未注册到目录树 |
| V-ORPHAN-7037812 | 孤儿节点: 7037812 | orphan_node |  |  | warn | advisory | 节点 7037812 路径 scripts/ch/_verify_historical_partition.py 未注册... |
| V-ORPHAN-7037813 | 孤儿节点: 7037813 | orphan_node |  |  | warn | advisory | 节点 7037813 路径 scripts/ch/_verify_kline_1min.py 未注册到目录树 |
| V-ORPHAN-7037874 | 孤儿节点: 7037874 | orphan_node |  |  | warn | advisory | 节点 7037874 路径 scripts/governance/d12_ai_hallucination/__init... |
| V-ORPHAN-7038133 | 孤儿节点: 7038133 | orphan_node |  |  | warn | advisory | 节点 7038133 路径 scripts/governance/generators/__init__.py 未注册到... |
| V-ORPHAN-7038318 | 孤儿节点: 7038318 | orphan_node |  |  | warn | advisory | 节点 7038318 路径 scripts/_archive/migration/safe_delete_operati... |
| V-ORPHAN-7038688 | 孤儿节点: 7038688 | orphan_node |  |  | warn | advisory | 节点 7038688 路径 tests/ba/test_ba_events.py 未注册到目录树 |
| V-ORPHAN-7038696 | 孤儿节点: 7038696 | orphan_node |  |  | warn | advisory | 节点 7038696 路径 tests/ba/test_ba_main.py 未注册到目录树 |
| V-ORPHAN-7038758 | 孤儿节点: 7038758 | orphan_node |  |  | warn | advisory | 节点 7038758 路径 tests/chaos/__init__.py 未注册到目录树 |
| V-ORPHAN-7038814 | 孤儿节点: 7038814 | orphan_node |  |  | warn | advisory | 节点 7038814 路径 tests/context/test_context_rot_model_unit.py 未... |
| V-ORPHAN-7038968 | 孤儿节点: 7038968 | orphan_node |  |  | warn | advisory | 节点 7038968 路径 tests/escalation/conftest.py 未注册到目录树 |
| V-ORPHAN-7039066 | 孤儿节点: 7039066 | orphan_node |  |  | warn | advisory | 节点 7039066 路径 tests/federated_learning/test_fl_safety_gate_l... |
| V-ORPHAN-7039077 | 孤儿节点: 7039077 | orphan_node |  |  | warn | advisory | 节点 7039077 路径 tests/federated_learning/test_fl_scheduler.py ... |
| V-ORPHAN-7039162 | 孤儿节点: 7039162 | orphan_node |  |  | warn | advisory | 节点 7039162 路径 tests/feedback/test_notification_feedback.py 未... |
| V-ORPHAN-7039179 | 孤儿节点: 7039179 | orphan_node |  |  | warn | advisory | 节点 7039179 路径 tests/feedback/test_scheduler_health.py 未注册到目录... |
| V-ORPHAN-7039241 | 孤儿节点: 7039241 | orphan_node |  |  | warn | advisory | 节点 7039241 路径 tests/f_lifecycle/test_flag_lifecycle.py 未注册到目... |
| V-ORPHAN-7039425 | 孤儿节点: 7039425 | orphan_node |  |  | warn | advisory | 节点 7039425 路径 tests/governance/budget/test_roi_calculator.py... |
| V-ORPHAN-7039491 | 孤儿节点: 7039491 | orphan_node |  |  | warn | advisory | 节点 7039491 路径 tests/governance/commit_gates/test_m21_phase3_... |
| V-ORPHAN-7039540 | 孤儿节点: 7039540 | orphan_node |  |  | warn | advisory | 节点 7039540 路径 tests/governance/d1_structure/__init__.py 未注册到... |
| V-ORPHAN-7039653 | 孤儿节点: 7039653 | orphan_node |  |  | warn | advisory | 节点 7039653 路径 tests/governance/orchestrator/test_objective_t... |
| V-ORPHAN-7039768 | 孤儿节点: 7039768 | orphan_node |  |  | warn | advisory | 节点 7039768 路径 tests/governance/shared/test_governance_core.p... |
| V-ORPHAN-7039769 | 孤儿节点: 7039769 | orphan_node |  |  | warn | advisory | 节点 7039769 路径 tests/governance/shared/test_governance_db.py ... |
| V-ORPHAN-7039771 | 孤儿节点: 7039771 | orphan_node |  |  | warn | advisory | 节点 7039771 路径 tests/governance/shared/test_shared_evolver.py... |
| V-ORPHAN-7039781 | 孤儿节点: 7039781 | orphan_node |  |  | warn | advisory | 节点 7039781 路径 tests/governance/trading/test_exchange_partiti... |
| V-ORPHAN-7039807 | 孤儿节点: 7039807 | orphan_node |  |  | warn | advisory | 节点 7039807 路径 tests/infrastructure/test_audit_rename_complet... |
| V-ORPHAN-7039845 | 孤儿节点: 7039845 | orphan_node |  |  | warn | advisory | 节点 7039845 路径 tests/infrastructure/test_graceful_degradation... |
| V-ORPHAN-7039890 | 孤儿节点: 7039890 | orphan_node |  |  | warn | advisory | 节点 7039890 路径 tests/infrastructure/test_span_stub.py 未注册到目录树 |
| V-ORPHAN-7039981 | 孤儿节点: 7039981 | orphan_node |  |  | warn | advisory | 节点 7039981 路径 tests/llm_security/__init__.py 未注册到目录树 |
| V-ORPHAN-7039998 | 孤儿节点: 7039998 | orphan_node |  |  | warn | advisory | 节点 7039998 路径 tests/ml_experiment/test_adversarial_ml_experi... |
| V-ORPHAN-7040048 | 孤儿节点: 7040048 | orphan_node |  |  | warn | advisory | 节点 7040048 路径 tests/observability/test_watchdog.py 未注册到目录树 |
| V-ORPHAN-7040126 | 孤儿节点: 7040126 | orphan_node |  |  | warn | advisory | 节点 7040126 路径 tests/rollback/test_rollback_abuse_detector.py... |
| V-ORPHAN-7040189 | 孤儿节点: 7040189 | orphan_node |  |  | warn | advisory | 节点 7040189 路径 tests/scripts/backup/__init__.py 未注册到目录树 |
| V-ORPHAN-7040393 | 孤儿节点: 7040393 | orphan_node |  |  | warn | advisory | 节点 7040393 路径 tests/trading/unit/test_dlq_manager_unit.py 未注... |
| V-ORPHAN-7040601 | 孤儿节点: 7040601 | orphan_node |  |  | warn | advisory | 节点 7040601 路径 config/runtime/script_retirement_state.yaml 未注... |
| V-ORPHAN-7040602 | 孤儿节点: 7040602 | orphan_node |  |  | warn | advisory | 节点 7040602 路径 config/infra/prometheus/prometheus.yml 未注册到目录树 |
| V-ORPHAN-7040603 | 孤儿节点: 7040603 | orphan_node |  |  | warn | advisory | 节点 7040603 路径 config/runtime/burn_rate_acceleration.yaml 未注册... |
| V-ORPHAN-7040604 | 孤儿节点: 7040604 | orphan_node |  |  | warn | advisory | 节点 7040604 路径 config/infra/grafana/datasources/prometheus.ym... |
| V-ORPHAN-7040605 | 孤儿节点: 7040605 | orphan_node |  |  | warn | advisory | 节点 7040605 路径 config/runtime/error_budget_state.yaml 未注册到目录树 |
| V-ORPHAN-7040606 | 孤儿节点: 7040606 | orphan_node |  |  | warn | advisory | 节点 7040606 路径 config/runtime/kill_switch_state.yaml 未注册到目录树 |
| V-ORPHAN-7040607 | 孤儿节点: 7040607 | orphan_node |  |  | warn | advisory | 节点 7040607 路径 config/runtime/shadow_mode_state.yaml 未注册到目录树 |
| V-ORPHAN-7040608 | 孤儿节点: 7040608 | orphan_node |  |  | warn | advisory | 节点 7040608 路径 docs/03_modules/_cross_layer/database/business... |
| V-ORPHAN-7040609 | 孤儿节点: 7040609 | orphan_node |  |  | warn | advisory | 节点 7040609 路径 docs/03_modules/_domain_infrastructure_operati... |
| V-ORPHAN-7040684 | 孤儿节点: 7040684 | orphan_node |  |  | warn | advisory | 节点 7040684 路径 docs/01_policies_and_standards/rules/trae_070_... |
| V-ORPHAN-7040686 | 孤儿节点: 7040686 | orphan_node |  |  | warn | advisory | 节点 7040686 路径 docs/01_policies_and_standards/rules/trae_069_... |
| V-ORPHAN-7040691 | 孤儿节点: 7040691 | orphan_node |  |  | warn | advisory | 节点 7040691 路径 docs/01_policies_and_standards/rules/trae_081_... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(生命周期管理) production 节点 219 超过上限 150，需拆分或提升上限 (... |
| V-CAP-D_GOV_CODE_QUALITY | 容量超限: D_GOV_CODE_QUALITY | capacity_exceeded | D_GOV_CODE_QUALITY |  | hard | gate | 域 D_GOV_CODE_QUALITY(代码质量治理) production 节点 168 超过上限 150，需拆分或... |
| V-CAP-D_GOV_SCRIPTS | 容量超限: D_GOV_SCRIPTS | capacity_exceeded | D_GOV_SCRIPTS |  | hard | gate | 域 D_GOV_SCRIPTS(脚本治理) production 节点 377 超过上限 150，需拆分或提升上限 (A... |
| V-CAP-D_INFRA_RUNTIME | 容量超限: D_INFRA_RUNTIME | capacity_exceeded | D_INFRA_RUNTIME |  | hard | gate | 域 D_INFRA_RUNTIME(运行时集成) production 节点 160 超过上限 150，需拆分或提升上限... |
| V-CAP-D_SECURITY | 容量超限: D_SECURITY | capacity_exceeded | D_SECURITY |  | hard | gate | 域 D_SECURITY(对抗验证) production 节点 166 超过上限 150，需拆分或提升上限 (ARCH... |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | gate | 域 D_SHARED(共享服务) production 节点 184 超过上限 150，需拆分或提升上限 (ARCH-C... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_DRIFT |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_DATA -> D_GOV_ENFORCEMENT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DETECTORS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_DRIFT |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INTEGRATION |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SHARED |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_INFRASTRUCTURE | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_TRADING | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_TRADING | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_TRADING | error | gate | 跨域依赖未声明: D_FUNDAMENTAL_SIGNAL -> D_TRADING |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_AUDIT |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_DRIFT |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOVERNANCE-D_GOV_RULE | 跨域违规: D_GOVERNANCE -> D_GOV_RULE | cross_domain_violation | D_GOVERNANCE | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_RULE |
| V-CROSS-D_GOVERNANCE-D_INFRASTRUCTURE | 跨域违规: D_GOVERNANCE -> D_INFRASTRUCTURE | cross_domain_violation | D_GOVERNANCE | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRASTRUCTURE |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INTELLIGENCE |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_SECURITY |
| V-CROSS-D_GOV_AUDIT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_AUDIT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_AUDIT | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_AUDIT-D_GOV_DRIFT | 跨域违规: D_GOV_AUDIT -> D_GOV_DRIFT | cross_domain_violation | D_GOV_AUDIT | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_DRIFT |
| V-CROSS-D_GOV_AUDIT-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_AUDIT -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_AUDIT | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_AUDIT-D_GOV_SCRIPTS | 跨域违规: D_GOV_AUDIT -> D_GOV_SCRIPTS | cross_domain_violation | D_GOV_AUDIT | D_GOV_SCRIPTS | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_SCRIPTS |
| V-CROSS-D_GOV_AUDIT-D_INFRA_RUNTIME | 跨域违规: D_GOV_AUDIT -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_AUDIT | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_AUDIT-D_SECURITY | 跨域违规: D_GOV_AUDIT -> D_SECURITY | cross_domain_violation | D_GOV_AUDIT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_SECURITY |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_SHARED |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_DATA |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOVERNANCE | 跨域违规: D_GOV_CODE_QUALITY -> D_GOVERNANCE | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOVERNANCE |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_CODE_QUALITY-D_INFRASTRUCTURE | 跨域违规: D_GOV_CODE_QUALITY -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_CODE_QUALITY | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_INFRASTRUCTURE |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_SHARED |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_DRIFT-D_GOV_SCRIPTS | 跨域违规: D_GOV_DRIFT -> D_GOV_SCRIPTS | cross_domain_violation | D_GOV_DRIFT | D_GOV_SCRIPTS | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_GOV_SCRIPTS |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_SHARED |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOVERNANCE |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_SECURITY |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_OPS |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOVERNANCE |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_RULE-D_GOV_AUDIT | 跨域违规: D_GOV_RULE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_RULE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_GOV_AUDIT |
| V-CROSS-D_GOV_RULE-D_INFRA_RUNTIME | 跨域违规: D_GOV_RULE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_RULE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_RULE-D_SHARED | 跨域违规: D_GOV_RULE -> D_SHARED | cross_domain_violation | D_GOV_RULE | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_SHARED |
| V-CROSS-D_GOV_SCRIPTS-D_GOVERNANCE | 跨域违规: D_GOV_SCRIPTS -> D_GOVERNANCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOVERNANCE |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_AUDIT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_AUDIT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_AUDIT |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_RULE |
| V-CROSS-D_GOV_SCRIPTS-D_INFRA_RUNTIME | 跨域违规: D_GOV_SCRIPTS -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_SCRIPTS | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_SCRIPTS-D_INTEGRATION | 跨域违规: D_GOV_SCRIPTS -> D_INTEGRATION | cross_domain_violation | D_GOV_SCRIPTS | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_INTEGRATION |
| V-CROSS-D_GOV_SCRIPTS-D_ORCHESTRATOR | 跨域违规: D_GOV_SCRIPTS -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_SCRIPTS | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_ORCHESTRATOR |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_SHARED |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | gate | 跨域依赖未声明: D_INFRASTRUCTURE -> D_SHARED |
| V-CROSS-D_INFRA_A2A-D_SHARED | 跨域违规: D_INFRA_A2A -> D_SHARED | cross_domain_violation | D_INFRA_A2A | D_SHARED | error | gate | 跨域依赖未声明: D_INFRA_A2A -> D_SHARED |
| V-CROSS-D_INFRA_RECOVERY-D_SHARED | 跨域违规: D_INFRA_RECOVERY -> D_SHARED | cross_domain_violation | D_INFRA_RECOVERY | D_SHARED | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_SHARED |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_AUDIT | 跨域违规: D_INFRA_RUNTIME -> D_GOV_AUDIT | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_AUDIT |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_RULE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRASTRUCTURE | 跨域违规: D_INFRA_RUNTIME -> D_INFRASTRUCTURE | cross_domain_violation | D_INFRA_RUNTIME | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRASTRUCTURE |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTEGRATION |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTELLIGENCE |
| V-CROSS-D_INFRA_RUNTIME-D_ORCHESTRATOR | 跨域违规: D_INFRA_RUNTIME -> D_ORCHESTRATOR | cross_domain_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_ORCHESTRATOR |
| V-CROSS-D_INFRA_RUNTIME-D_SECURITY | 跨域违规: D_INFRA_RUNTIME -> D_SECURITY | cross_domain_violation | D_INFRA_RUNTIME | D_SECURITY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_SECURITY |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_GOV_AUDIT |
| V-CROSS-D_INTEGRATION-D_GOV_RULE | 跨域违规: D_INTEGRATION -> D_GOV_RULE | cross_domain_violation | D_INTEGRATION | D_GOV_RULE | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_GOV_RULE |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_INTELLIGENCE |
| V-CROSS-D_INTEGRATION-D_OPS | 跨域违规: D_INTEGRATION -> D_OPS | cross_domain_violation | D_INTEGRATION | D_OPS | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_OPS |
| V-CROSS-D_INTEGRATION-D_SECURITY | 跨域违规: D_INTEGRATION -> D_SECURITY | cross_domain_violation | D_INTEGRATION | D_SECURITY | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_SECURITY |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | gate | 跨域依赖未声明: D_ML_TRAIN -> D_TRADING |
| V-CROSS-D_ORCHESTRATOR-D_FEEDBACK_LOOP | 跨域违规: D_ORCHESTRATOR -> D_FEEDBACK_LOOP | cross_domain_violation | D_ORCHESTRATOR | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_FEEDBACK_LOOP |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_GOVERNANCE |
| V-CROSS-D_ORCHESTRATOR-D_GOV_DRIFT | 跨域违规: D_ORCHESTRATOR -> D_GOV_DRIFT | cross_domain_violation | D_ORCHESTRATOR | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_GOV_DRIFT |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_SHARED |
| V-CROSS-D_PF_ALLOC-D_INFRASTRUCTURE | 跨域违规: D_PF_ALLOC -> D_INFRASTRUCTURE | cross_domain_violation | D_PF_ALLOC | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_PF_ALLOC -> D_INFRASTRUCTURE |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | gate | 跨域依赖未声明: D_PF_CORE -> D_PF_ALLOC |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_DRIFT |
| V-CROSS-D_SECURITY-D_GOV_RULE | 跨域违规: D_SECURITY -> D_GOV_RULE | cross_domain_violation | D_SECURITY | D_GOV_RULE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_RULE |
| V-CROSS-D_SHARED-D_GOV_RULE | 跨域违规: D_SHARED -> D_GOV_RULE | cross_domain_violation | D_SHARED | D_GOV_RULE | error | gate | 跨域依赖未声明: D_SHARED -> D_GOV_RULE |
| V-CROSS-D_SHARED-D_INFRASTRUCTURE | 跨域违规: D_SHARED -> D_INFRASTRUCTURE | cross_domain_violation | D_SHARED | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_SHARED -> D_INFRASTRUCTURE |
| V-CROSS-D_SIGQC-D_INFRASTRUCTURE | 跨域违规: D_SIGQC -> D_INFRASTRUCTURE | cross_domain_violation | D_SIGQC | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_SIGQC -> D_INFRASTRUCTURE |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_TRADING -> D_INFRASTRUCTURE |
| V-CROSS-D_TRADING-D_ORCHESTRATOR | 跨域违规: D_TRADING -> D_ORCHESTRATOR | cross_domain_violation | D_TRADING | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_TRADING -> D_ORCHESTRATOR |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(生命周期管理) production 节点 219 超过硬上限 150 (ARCH-CAP... |
| V-HARD150-D_GOV_CODE_QUALITY | 硬上限违规: D_GOV_CODE_QUALITY | hard_limit_exceeded | D_GOV_CODE_QUALITY |  | error | gate | 域 D_GOV_CODE_QUALITY(代码质量治理) production 节点 168 超过硬上限 150 (AR... |
| V-HARD150-D_GOV_SCRIPTS | 硬上限违规: D_GOV_SCRIPTS | hard_limit_exceeded | D_GOV_SCRIPTS |  | error | gate | 域 D_GOV_SCRIPTS(脚本治理) production 节点 377 超过硬上限 150 (ARCH-CAP-... |
| V-HARD150-D_INFRA_RUNTIME | 硬上限违规: D_INFRA_RUNTIME | hard_limit_exceeded | D_INFRA_RUNTIME |  | error | gate | 域 D_INFRA_RUNTIME(运行时集成) production 节点 160 超过硬上限 150 (ARCH-C... |
| V-HARD150-D_SECURITY | 硬上限违规: D_SECURITY | hard_limit_exceeded | D_SECURITY |  | error | gate | 域 D_SECURITY(对抗验证) production 节点 166 超过硬上限 150 (ARCH-CAP-002... |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | gate | 域 D_SHARED(共享服务) production 节点 184 超过硬上限 150 (ARCH-CAP-002 v... |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 7035342 -> 7036174 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 7035314 -> 7036528 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 7035808 -> 7036174 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 7035536 -> 7036091 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 7035538 -> 7035886 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 7035860 -> 7036091 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 7035879 -> 7037697 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 层级违规: 7036462 -> 7035882 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | gate | 层级违规: 7036452 -> 7035923 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 7036466 -> 7036481 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-7035230 | 孤儿节点: 7035230 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-7035231 | 孤儿节点: 7035231 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-7035232 | 孤儿节点: 7035232 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-7035233 | 孤儿节点: 7035233 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-7035358 | 孤儿节点: 7035358 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-7035379 | 孤儿节点: 7035379 | orphan_node |  |  | warn | open |
| V-ORPHAN-7035416 | 孤儿节点: 7035416 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-7035433 | 孤儿节点: 7035433 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-7035525 | 孤儿节点: 7035525 | orphan_node | D_FEEDBACK_LOOP |  | warn | open |
| V-ORPHAN-7035563 | 孤儿节点: 7035563 | orphan_node | D_FEEDBACK_LOOP |  | warn | open |
| V-ORPHAN-7035564 | 孤儿节点: 7035564 | orphan_node | D_FEEDBACK_LOOP |  | warn | open |
| V-ORPHAN-7035576 | 孤儿节点: 7035576 | orphan_node | D_FEEDBACK_LOOP |  | warn | open |
| V-ORPHAN-7035591 | 孤儿节点: 7035591 | orphan_node | D_FBL_DETECTORS |  | warn | open |
| V-ORPHAN-7035638 | 孤儿节点: 7035638 | orphan_node | D_FBL_DETECTORS |  | warn | open |
| V-ORPHAN-7035745 | 孤儿节点: 7035745 | orphan_node | D_FEEDBACK_LOOP |  | warn | open |
| V-ORPHAN-7035776 | 孤儿节点: 7035776 | orphan_node | D_FBL_VERIFICATION |  | warn | open |
| V-ORPHAN-7035836 | 孤儿节点: 7035836 | orphan_node | D_FBL_VERIFICATION |  | warn | open |
| V-ORPHAN-7035979 | 孤儿节点: 7035979 | orphan_node | D_GOV_OPS_RESILIENCE |  | warn | open |
| V-ORPHAN-7036006 | 孤儿节点: 7036006 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-7036278 | 孤儿节点: 7036278 | orphan_node | D_GOV_CODE_QUALITY |  | warn | open |
| V-ORPHAN-7036375 | 孤儿节点: 7036375 | orphan_node | D_GOV_AUDIT |  | warn | open |
| V-ORPHAN-7036401 | 孤儿节点: 7036401 | orphan_node | D_GOV_CODE_QUALITY |  | warn | open |
| V-ORPHAN-7036445 | 孤儿节点: 7036445 | orphan_node | D_GOV_CODE_QUALITY |  | warn | open |
| V-ORPHAN-7036560 | 孤儿节点: 7036560 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-7036787 | 孤儿节点: 7036787 | orphan_node | D_INFRA_RECOVERY |  | warn | open |
| V-ORPHAN-7036940 | 孤儿节点: 7036940 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037620 | 孤儿节点: 7037620 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037622 | 孤儿节点: 7037622 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037623 | 孤儿节点: 7037623 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037624 | 孤儿节点: 7037624 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037773 | 孤儿节点: 7037773 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037774 | 孤儿节点: 7037774 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037775 | 孤儿节点: 7037775 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037776 | 孤儿节点: 7037776 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037777 | 孤儿节点: 7037777 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037779 | 孤儿节点: 7037779 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037780 | 孤儿节点: 7037780 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037781 | 孤儿节点: 7037781 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037782 | 孤儿节点: 7037782 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037783 | 孤儿节点: 7037783 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037784 | 孤儿节点: 7037784 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037785 | 孤儿节点: 7037785 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037786 | 孤儿节点: 7037786 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037787 | 孤儿节点: 7037787 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037788 | 孤儿节点: 7037788 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037789 | 孤儿节点: 7037789 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037790 | 孤儿节点: 7037790 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037791 | 孤儿节点: 7037791 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037792 | 孤儿节点: 7037792 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037793 | 孤儿节点: 7037793 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037794 | 孤儿节点: 7037794 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037796 | 孤儿节点: 7037796 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037797 | 孤儿节点: 7037797 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037803 | 孤儿节点: 7037803 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037805 | 孤儿节点: 7037805 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037807 | 孤儿节点: 7037807 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037812 | 孤儿节点: 7037812 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037813 | 孤儿节点: 7037813 | orphan_node |  |  | warn | open |
| V-ORPHAN-7037874 | 孤儿节点: 7037874 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038133 | 孤儿节点: 7038133 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038318 | 孤儿节点: 7038318 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038688 | 孤儿节点: 7038688 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038696 | 孤儿节点: 7038696 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038758 | 孤儿节点: 7038758 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038814 | 孤儿节点: 7038814 | orphan_node |  |  | warn | open |
| V-ORPHAN-7038968 | 孤儿节点: 7038968 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039066 | 孤儿节点: 7039066 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039077 | 孤儿节点: 7039077 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039162 | 孤儿节点: 7039162 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039179 | 孤儿节点: 7039179 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039241 | 孤儿节点: 7039241 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039425 | 孤儿节点: 7039425 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039491 | 孤儿节点: 7039491 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039540 | 孤儿节点: 7039540 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039653 | 孤儿节点: 7039653 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039768 | 孤儿节点: 7039768 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039769 | 孤儿节点: 7039769 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039771 | 孤儿节点: 7039771 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039781 | 孤儿节点: 7039781 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039807 | 孤儿节点: 7039807 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039845 | 孤儿节点: 7039845 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039890 | 孤儿节点: 7039890 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039981 | 孤儿节点: 7039981 | orphan_node |  |  | warn | open |
| V-ORPHAN-7039998 | 孤儿节点: 7039998 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040048 | 孤儿节点: 7040048 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040126 | 孤儿节点: 7040126 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040189 | 孤儿节点: 7040189 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040393 | 孤儿节点: 7040393 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040601 | 孤儿节点: 7040601 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040602 | 孤儿节点: 7040602 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040603 | 孤儿节点: 7040603 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040604 | 孤儿节点: 7040604 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040605 | 孤儿节点: 7040605 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040606 | 孤儿节点: 7040606 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040607 | 孤儿节点: 7040607 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040608 | 孤儿节点: 7040608 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040609 | 孤儿节点: 7040609 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040684 | 孤儿节点: 7040684 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040686 | 孤儿节点: 7040686 | orphan_node |  |  | warn | open |
| V-ORPHAN-7040691 | 孤儿节点: 7040691 | orphan_node |  |  | warn | open |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | open |
| V-CAP-D_GOV_CODE_QUALITY | 容量超限: D_GOV_CODE_QUALITY | capacity_exceeded | D_GOV_CODE_QUALITY |  | hard | open |
| V-CAP-D_GOV_SCRIPTS | 容量超限: D_GOV_SCRIPTS | capacity_exceeded | D_GOV_SCRIPTS |  | hard | open |
| V-CAP-D_INFRA_RUNTIME | 容量超限: D_INFRA_RUNTIME | capacity_exceeded | D_INFRA_RUNTIME |  | hard | open |
| V-CAP-D_SECURITY | 容量超限: D_SECURITY | capacity_exceeded | D_SECURITY |  | hard | open |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | open |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_INFRASTRUCTURE | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_TRADING | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_TRADING | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_TRADING | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_RULE | 跨域违规: D_GOVERNANCE -> D_GOV_RULE | cross_domain_violation | D_GOVERNANCE | D_GOV_RULE | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRASTRUCTURE | 跨域违规: D_GOVERNANCE -> D_INFRASTRUCTURE | cross_domain_violation | D_GOVERNANCE | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_AUDIT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_AUDIT | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_DRIFT | 跨域违规: D_GOV_AUDIT -> D_GOV_DRIFT | cross_domain_violation | D_GOV_AUDIT | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_AUDIT -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_AUDIT | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_SCRIPTS | 跨域违规: D_GOV_AUDIT -> D_GOV_SCRIPTS | cross_domain_violation | D_GOV_AUDIT | D_GOV_SCRIPTS | error | open |
| V-CROSS-D_GOV_AUDIT-D_INFRA_RUNTIME | 跨域违规: D_GOV_AUDIT -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_AUDIT | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_AUDIT-D_SECURITY | 跨域违规: D_GOV_AUDIT -> D_SECURITY | cross_domain_violation | D_GOV_AUDIT | D_SECURITY | error | open |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOVERNANCE | 跨域违规: D_GOV_CODE_QUALITY -> D_GOVERNANCE | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_INFRASTRUCTURE | 跨域违规: D_GOV_CODE_QUALITY -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_CODE_QUALITY | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | open |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_DRIFT-D_GOV_SCRIPTS | 跨域违规: D_GOV_DRIFT -> D_GOV_SCRIPTS | cross_domain_violation | D_GOV_DRIFT | D_GOV_SCRIPTS | error | open |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_RULE-D_GOV_AUDIT | 跨域违规: D_GOV_RULE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_RULE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_RULE-D_INFRA_RUNTIME | 跨域违规: D_GOV_RULE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_RULE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_RULE-D_SHARED | 跨域违规: D_GOV_RULE -> D_SHARED | cross_domain_violation | D_GOV_RULE | D_SHARED | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOVERNANCE | 跨域违规: D_GOV_SCRIPTS -> D_GOVERNANCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_AUDIT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_AUDIT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_INFRA_RUNTIME | 跨域违规: D_GOV_SCRIPTS -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_SCRIPTS | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_INTEGRATION | 跨域违规: D_GOV_SCRIPTS -> D_INTEGRATION | cross_domain_violation | D_GOV_SCRIPTS | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_ORCHESTRATOR | 跨域违规: D_GOV_SCRIPTS -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_SCRIPTS | D_ORCHESTRATOR | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | open |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | open |
| V-CROSS-D_INFRA_A2A-D_SHARED | 跨域违规: D_INFRA_A2A -> D_SHARED | cross_domain_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_SHARED | 跨域违规: D_INFRA_RECOVERY -> D_SHARED | cross_domain_violation | D_INFRA_RECOVERY | D_SHARED | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_AUDIT | 跨域违规: D_INFRA_RUNTIME -> D_GOV_AUDIT | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_AUDIT | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRASTRUCTURE | 跨域违规: D_INFRA_RUNTIME -> D_INFRASTRUCTURE | cross_domain_violation | D_INFRA_RUNTIME | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_ORCHESTRATOR | 跨域违规: D_INFRA_RUNTIME -> D_ORCHESTRATOR | cross_domain_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_SECURITY | 跨域违规: D_INFRA_RUNTIME -> D_SECURITY | cross_domain_violation | D_INFRA_RUNTIME | D_SECURITY | error | open |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_INTEGRATION-D_GOV_RULE | 跨域违规: D_INTEGRATION -> D_GOV_RULE | cross_domain_violation | D_INTEGRATION | D_GOV_RULE | error | open |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | open |
| V-CROSS-D_INTEGRATION-D_OPS | 跨域违规: D_INTEGRATION -> D_OPS | cross_domain_violation | D_INTEGRATION | D_OPS | error | open |
| V-CROSS-D_INTEGRATION-D_SECURITY | 跨域违规: D_INTEGRATION -> D_SECURITY | cross_domain_violation | D_INTEGRATION | D_SECURITY | error | open |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | open |
| V-CROSS-D_ORCHESTRATOR-D_FEEDBACK_LOOP | 跨域违规: D_ORCHESTRATOR -> D_FEEDBACK_LOOP | cross_domain_violation | D_ORCHESTRATOR | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | open |
| V-CROSS-D_ORCHESTRATOR-D_GOV_DRIFT | 跨域违规: D_ORCHESTRATOR -> D_GOV_DRIFT | cross_domain_violation | D_ORCHESTRATOR | D_GOV_DRIFT | error | open |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | open |
| V-CROSS-D_PF_ALLOC-D_INFRASTRUCTURE | 跨域违规: D_PF_ALLOC -> D_INFRASTRUCTURE | cross_domain_violation | D_PF_ALLOC | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | open |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | open |
| V-CROSS-D_SECURITY-D_GOV_RULE | 跨域违规: D_SECURITY -> D_GOV_RULE | cross_domain_violation | D_SECURITY | D_GOV_RULE | error | open |
| V-CROSS-D_SHARED-D_GOV_RULE | 跨域违规: D_SHARED -> D_GOV_RULE | cross_domain_violation | D_SHARED | D_GOV_RULE | error | open |
| V-CROSS-D_SHARED-D_INFRASTRUCTURE | 跨域违规: D_SHARED -> D_INFRASTRUCTURE | cross_domain_violation | D_SHARED | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_SIGQC-D_INFRASTRUCTURE | 跨域违规: D_SIGQC -> D_INFRASTRUCTURE | cross_domain_violation | D_SIGQC | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_TRADING-D_ORCHESTRATOR | 跨域违规: D_TRADING -> D_ORCHESTRATOR | cross_domain_violation | D_TRADING | D_ORCHESTRATOR | error | open |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | open |
| V-HARD150-D_GOV_CODE_QUALITY | 硬上限违规: D_GOV_CODE_QUALITY | hard_limit_exceeded | D_GOV_CODE_QUALITY |  | error | open |
| V-HARD150-D_GOV_SCRIPTS | 硬上限违规: D_GOV_SCRIPTS | hard_limit_exceeded | D_GOV_SCRIPTS |  | error | open |
| V-HARD150-D_INFRA_RUNTIME | 硬上限违规: D_INFRA_RUNTIME | hard_limit_exceeded | D_INFRA_RUNTIME |  | error | open |
| V-HARD150-D_SECURITY | 硬上限违规: D_SECURITY | hard_limit_exceeded | D_SECURITY |  | error | open |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
