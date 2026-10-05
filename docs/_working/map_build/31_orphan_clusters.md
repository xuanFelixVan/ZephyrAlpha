---
ttl: task_bound
completes_when: 覆盖账本 v2 验收闭环（孤儿清零/入图判罚完）后本报告随 30 号转归档
title: 孤儿簇报告与六图覆盖率（join checker 首跑，机生禁手改）
owner: st-joinchk-20261004
---

# 孤儿簇报告（31 号·机生）

> 宇宙=5209（裁定#481 预估≈5200，偏差 +0.2%）；直接挂载 2306；闭包归属 1213；真孤儿 2029（簇 74）；豁免在案 9；悬空键 0。

## 六图覆盖率一栏表

| 行 | GOMAP | TDM | FACTORY | FIG11 | FIG12 | FIG13 |
|---|---|---|---|---|---|---|
| direct（直接挂载） | 455 | 113 | 396 | 906 | 218 | 218 |
| closure（闭包归属） | 739 | 565 | 290 | 682 | 411 | 434 |
| 覆盖率%（direct+closure）/宇宙 | 22.9% | 13.0% | 13.2% | 30.5% | 12.1% | 12.5% |

> 孤儿为全集判（六图两不沾），跨图共享一份清单；上表第三行按 (direct+closure)/宇宙 计单图覆盖。

## 孤儿簇（按顶级包聚簇，判级四档）

### src.zephyr.feedback_loop（227 台：wired=142，wired_by_header=85）
- `src/zephyr/feedback_loop/actors/alert_router.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/feedback_loop/actors/api_version_contract.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/feedback_loop/actors/global_action_scheduler.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 224 台见 30 号 units 段

### src.zephyr.shared（208 台：suspect_orphan=26，wired=117，wired_by_header=56，wired_dynamic=9）
- `src/zephyr/shared/__version__.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/shared/_cross_layer/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 205 台见 30 号 units 段

### src.zephyr.frontend（167 台：suspect_orphan=140，wired=15，wired_by_header=12）
- `src/zephyr/frontend/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/frontend/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/frontend/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 164 台见 30 号 units 段

### src.zephyr.infrastructure（160 台：suspect_orphan=5，wired=111，wired_by_header=43，wired_dynamic=1）
- `src/zephyr/infrastructure/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/infrastructure/a2a_protocol/a2a_card_registry.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/infrastructure/a2a_protocol/governance/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 157 台见 30 号 units 段

### src.zephyr.governance（158 台：suspect_orphan=4，wired=40，wired_by_header=77，wired_dynamic=37）
- `src/zephyr/governance/a2a/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/governance/agent_spec/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/governance/agent_spec/registry.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 155 台见 30 号 units 段

### src.zephyr.autonomy_core（103 台：suspect_orphan=2，wired=22，wired_by_header=79）
- `src/zephyr/autonomy_core/__init__.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/autonomy_core/__main__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/autonomy_core/agent_observability.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 100 台见 30 号 units 段

### src.zephyr.signal_ashare（84 台：suspect_orphan=7，wired=37，wired_by_header=40）
- `src/zephyr/signal_ashare/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_ashare/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_ashare/banker_pattern_simulator.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 81 台见 30 号 units 段

### src.zephyr.gov_code_quality（61 台：suspect_orphan=1，wired=6，wired_by_header=51，wired_dynamic=3）
- `src/zephyr/gov_code_quality/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_code_quality/code_dedup/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_code_quality/code_dedup/annotations.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 58 台见 30 号 units 段

### src.zephyr.intelligence（53 台：suspect_orphan=7，wired=27，wired_by_header=19）
- `src/zephyr/intelligence/__init__.py`（wired，imported_by=0，last_commit=2026-09-23）
- `src/zephyr/intelligence/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/intelligence/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 50 台见 30 号 units 段

### src.zephyr.orchestrator（49 台：suspect_orphan=5，wired=11，wired_by_header=32，wired_dynamic=1）
- `src/zephyr/orchestrator/contracts/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/orchestrator/contracts/construction_guide.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/orchestrator/contracts/contract_registry.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 46 台见 30 号 units 段

### src.zephyr.gov_drift（47 台：suspect_orphan=1，wired=35，wired_by_header=4，wired_dynamic=7）
- `src/zephyr/gov_drift/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_drift/absence_manager.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_drift/ai_construction_detectors.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 44 台见 30 号 units 段

### scripts.governance（44 台：suspect_orphan=8，wired=11，wired_by_header=25）
- `scripts/governance/__init__.py`（wired，imported_by=0，last_commit=2026-06-21）
- `scripts/governance/_shared/__init__.py`（wired，imported_by=0，last_commit=2026-06-21）
- `scripts/governance/_shared/algo_flow_applier.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 41 台见 30 号 units 段

### src.zephyr.gov_audit（40 台：wired=21，wired_by_header=9，wired_dynamic=10）
- `src/zephyr/gov_audit/__init__.py`（wired，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/gov_audit/action_history.py`（wired_by_header，imported_by=0，last_commit=2026-09-17）
- `src/zephyr/gov_audit/agent_signer.py`（wired，imported_by=0，last_commit=2026-09-17）
- …其余 37 台见 30 号 units 段

### src.zephyr.ml_train（40 台：suspect_orphan=9，wired=10，wired_by_header=20，wired_dynamic=1）
- `src/zephyr/ml_train/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/ml_train/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/ml_train/adversarial_robustness_validator.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- …其余 37 台见 30 号 units 段

### src.zephyr.factor（38 台：suspect_orphan=4，wired=25，wired_by_header=9）
- `src/zephyr/factor/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/factor/analysis/bhy_fdr.py`（wired，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/factor/analysis/correlation_analyzer.py`（wired，imported_by=0，last_commit=2026-09-15）
- …其余 35 台见 30 号 units 段

### scripts._archive（31 台：suspect_orphan=14，wired=1，wired_by_header=16）
- `scripts/_archive/construction/create_db_alignment_tasks.py`（suspect_orphan，imported_by=0，last_commit=2026-08-21）
- `scripts/_archive/construction/create_dm_phase9_tasks.py`（suspect_orphan，imported_by=0，last_commit=2026-08-21）
- `scripts/_archive/construction/dm014_orphan_edge_repair.py`（suspect_orphan，imported_by=0，last_commit=2026-08-21）
- …其余 28 台见 30 号 units 段

### src.zephyr.trading（29 台：suspect_orphan=7，wired=19，wired_by_header=2，wired_dynamic=1）
- `src/zephyr/trading/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/trading/admission_controller.py`（wired，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/trading/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- …其余 26 台见 30 号 units 段

### src.zephyr.reporting（27 台：suspect_orphan=6，wired=10，wired_by_header=11）
- `src/zephyr/reporting/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/reporting/ai_review_summary.py`（wired_by_header，imported_by=0，last_commit=2026-08-24）
- `src/zephyr/reporting/alert_aggregator.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 24 台见 30 号 units 段

### src.zephyr.risk（27 台：suspect_orphan=5，wired=14，wired_by_header=7，wired_dynamic=1）
- `src/zephyr/risk/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/risk/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/risk/atr_stop_engine.py`（wired，imported_by=0，last_commit=2026-09-15）
- …其余 24 台见 30 号 units 段

### src.zephyr.compliance（25 台：suspect_orphan=6，wired=9，wired_by_header=10）
- `src/zephyr/compliance/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/compliance/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/compliance/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- …其余 22 台见 30 号 units 段

### src.zephyr.integration（24 台：wired=19，wired_by_header=4，wired_dynamic=1）
- `src/zephyr/integration/ai_service_route_matrix.py`（wired_by_header，imported_by=0，last_commit=2026-09-06）
- `src/zephyr/integration/api_gateway.py`（wired_by_header，imported_by=0，last_commit=2026-09-06）
- `src/zephyr/integration/llm_bridge.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 21 台见 30 号 units 段

### src.zephyr.signal_fundamental（24 台：suspect_orphan=10，wired=9，wired_by_header=5）
- `src/zephyr/signal_fundamental/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_fundamental/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_fundamental/audit/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 21 台见 30 号 units 段

### src.zephyr.ai_layer（22 台：suspect_orphan=1，wired=18，wired_by_header=3）
- `src/zephyr/ai_layer/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-19）
- `src/zephyr/ai_layer/cleaning/auditor.py`（wired，imported_by=0，last_commit=2026-09-26）
- `src/zephyr/ai_layer/cleaning/local_prefill.py`（wired，imported_by=0，last_commit=2026-09-26）
- …其余 19 台见 30 号 units 段

### src.zephyr.ex_core（21 台：suspect_orphan=4，wired=7，wired_by_header=10）
- `src/zephyr/ex_core/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/ex_core/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/ex_core/audit_journal/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- …其余 18 台见 30 号 units 段

### src.zephyr.data_governance（19 台：wired=2，wired_by_header=17）
- `src/zephyr/data_governance/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data_governance/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data_governance/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 16 台见 30 号 units 段

### src.zephyr.security（19 台：suspect_orphan=6，wired=12，wired_by_header=1）
- `src/zephyr/security/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/security/adversarial_validation/ai_attack_generator.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/security/adversarial_validation/attack_registry.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 16 台见 30 号 units 段

### src.zephyr.ex_sor（15 台：wired=6，wired_by_header=9）
- `src/zephyr/ex_sor/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/ex_sor/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/ex_sor/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 12 台见 30 号 units 段

### src.zephyr.gov_enforcement（14 台：wired=6，wired_by_header=6，wired_dynamic=2）
- `src/zephyr/gov_enforcement/behavioral_admission/admission_controller.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_enforcement/behavioral_admission/protection_index.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_enforcement/behavioral_admission/verdict_engine.py`（wired，imported_by=0，last_commit=2026-09-05）
- …其余 11 台见 30 号 units 段

### src.zephyr.regime（14 台：wired=6，wired_by_header=8）
- `src/zephyr/regime/cross_sectional_features.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/regime/institutional_regime_scorer.py`（wired，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/regime/validation/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- …其余 11 台见 30 号 units 段

### src.zephyr.simulation（13 台：suspect_orphan=6，wired=2，wired_by_header=5）
- `src/zephyr/simulation/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/simulation/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/simulation/core/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 10 台见 30 号 units 段

### src.zephyr.data（12 台：suspect_orphan=2，wired=8，wired_by_header=2）
- `src/zephyr/data/connectors/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data/connectors/connector_base.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data/connectors/file_connector.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 9 台见 30 号 units 段

### src.zephyr.position（12 台：suspect_orphan=4，wired=5，wired_by_header=3）
- `src/zephyr/position/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/position/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/position/core/calendar_position_constraint.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 9 台见 30 号 units 段

### src.zephyr.alt_data（11 台：wired=3，wired_by_header=8）
- `src/zephyr/alt_data/__init__.py`（wired，imported_by=0，last_commit=2026-09-23）
- `src/zephyr/alt_data/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/alt_data/alt_data_catalog.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 8 台见 30 号 units 段

### src.zephyr.backtest（11 台：suspect_orphan=4，wired=7）
- `src/zephyr/backtest/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/backtest/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- `src/zephyr/backtest/infrastructure/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-15）
- …其余 8 台见 30 号 units 段

### src.zephyr.clone_guard（11 台：wired=10，wired_by_header=1）
- `src/zephyr/clone_guard/aggregator.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/clone_guard/config.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/clone_guard/engines/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 8 台见 30 号 units 段

### scripts.industry_graph（10 台：wired=1，wired_by_header=9）
- `scripts/industry_graph/execute_r1_chain_plans.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- `scripts/industry_graph/fix_s6_s7_nodes.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- `scripts/industry_graph/migrate_roles.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- …其余 7 台见 30 号 units 段

### src.zephyr.data_security（9 台：wired=3，wired_by_header=6）
- `src/zephyr/data_security/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data_security/ai_masking_pipeline.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/data_security/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 6 台见 30 号 units 段

### src.zephyr.experiment_tracking（9 台：wired=5，wired_by_header=4）
- `src/zephyr/experiment_tracking/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/experiment_tracking/adapters/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/experiment_tracking/adapters/c2c3_adapter.py`（wired_by_header，imported_by=0，last_commit=2026-09-17）
- …其余 6 台见 30 号 units 段

### src.zephyr.sell_decision（9 台：wired_by_header=9）
- `src/zephyr/sell_decision/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/sell_decision/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/sell_decision/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 6 台见 30 号 units 段

### src.zephyr.digital_twin（8 台：wired_by_header=8）
- `src/zephyr/digital_twin/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/digital_twin/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/digital_twin/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 5 台见 30 号 units 段

### src.zephyr.execution_simulation（8 台：wired=1，wired_by_header=7）
- `src/zephyr/execution_simulation/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/execution_simulation/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/execution_simulation/almgren_chriss_impact_model.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 5 台见 30 号 units 段

### src.zephyr.library（8 台：wired=8）
- `src/zephyr/library/__init__.py`（wired，imported_by=0，last_commit=2026-09-22）
- `src/zephyr/library/collectors/fs_collector.py`（wired，imported_by=0，last_commit=2026-09-24）
- `src/zephyr/library/collectors/logs_collector.py`（wired，imported_by=0，last_commit=2026-09-24）
- …其余 5 台见 30 号 units 段

### src.zephyr.pf_alloc（8 台：suspect_orphan=5，wired=2，wired_by_header=1）
- `src/zephyr/pf_alloc/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/pf_alloc/allocation_config.py`（wired，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/pf_alloc/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 5 台见 30 号 units 段

### src.zephyr.pf_core（8 台：suspect_orphan=4，wired=3，wired_dynamic=1）
- `src/zephyr/pf_core/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/pf_core/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/pf_core/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 5 台见 30 号 units 段

### src.zephyr.research（8 台：wired=1，wired_by_header=6，wired_dynamic=1）
- `src/zephyr/research/__init__.py`（wired_dynamic，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/research/auto_feature_discoverer.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/research/factor_mining_pipeline.py`（wired_by_header，imported_by=0，last_commit=2026-09-02）
- …其余 5 台见 30 号 units 段

### src.zephyr.signal_quality（8 台：suspect_orphan=6，wired_by_header=2）
- `src/zephyr/signal_quality/_extensions/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_quality/api/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/signal_quality/core/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- …其余 5 台见 30 号 units 段

### src.zephyr.cross_asset（7 台：wired_by_header=7）
- `src/zephyr/cross_asset/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/cross_asset/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/cross_asset/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 4 台见 30 号 units 段

### src.zephyr.market_data（7 台：wired_by_header=7）
- `src/zephyr/market_data/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/market_data/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/market_data/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 4 台见 30 号 units 段

### src.zephyr.ml_serve（7 台：wired_by_header=7）
- `src/zephyr/ml_serve/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-29）
- `src/zephyr/ml_serve/_extensions/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/ml_serve/api/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- …其余 4 台见 30 号 units 段

### src.zephyr.strategy_factory（7 台：wired=6，wired_by_header=1）
- `src/zephyr/strategy_factory/__init__.py`（wired_by_header，imported_by=0，last_commit=2026-09-18）
- `src/zephyr/strategy_factory/owner_band_t/intraday_t.py`（wired，imported_by=0，last_commit=2026-09-17）
- `src/zephyr/strategy_factory/owner_band_t/regime_gate.py`（wired，imported_by=0，last_commit=2026-09-17）
- …其余 4 台见 30 号 units 段

### src.zephyr.nlp（6 台：suspect_orphan=1，wired=3，wired_by_header=2）
- `src/zephyr/nlp/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/nlp/news_impact_grader.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/nlp/nlp_inference.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 3 台见 30 号 units 段

### scripts.data（5 台：wired_by_header=5）
- `scripts/data/pattern_catalog_sync.py`（wired_by_header，imported_by=0，last_commit=untracked）
- `scripts/data/pattern_event_backfill.py`（wired_by_header，imported_by=0，last_commit=untracked）
- `scripts/data/pattern_event_incremental.py`（wired_by_header，imported_by=0，last_commit=untracked）
- …其余 2 台见 30 号 units 段

### src.zephyr.knowledge（5 台：wired=2，wired_by_header=3）
- `src/zephyr/knowledge/ai_knowledge_extractor.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/knowledge/collection_schema_manager.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/knowledge/financial_knowledge_graph.py`（wired，imported_by=0，last_commit=2026-09-16）
- …其余 2 台见 30 号 units 段

### scripts.ch（4 台：wired_by_header=4）
- `scripts/ch/apply_pattern_certification_ddl.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- `scripts/ch/apply_pattern_event_ddl.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- `scripts/ch/apply_pattern_win_rate_ddl.py`（wired_by_header，imported_by=0，last_commit=2026-09-15）
- …其余 1 台见 30 号 units 段

### src.zephyr.plan_engine（4 台：wired=4）
- `src/zephyr/plan_engine/brier_calibration.py`（wired，imported_by=0，last_commit=2026-09-02）
- `src/zephyr/plan_engine/evidence_chain_decision.py`（wired，imported_by=0，last_commit=2026-08-24）
- `src/zephyr/plan_engine/scenario_attribution_stats.py`（wired，imported_by=0，last_commit=2026-09-02）
- …其余 1 台见 30 号 units 段

### scripts.audit（3 台：wired=2，wired_by_header=1）
- `scripts/audit/cost_trio_exam.py`（wired，imported_by=0，last_commit=2026-09-24）
- `scripts/audit/t0_conditional_e4_v2_exam.py`（wired，imported_by=0，last_commit=2026-09-28）
- `scripts/audit/t0_six_phase_materialize.py`（wired_by_header，imported_by=0，last_commit=2026-09-28）

### src.zephyr.infra_runtime（3 台：wired_by_header=3）
- `src/zephyr/infra_runtime/cold_plane_isolation.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/infra_runtime/ml_pipeline_process.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/infra_runtime/runtime_admission.py`（wired_by_header，imported_by=0，last_commit=2026-09-17）

### src.zephyr.gov_rule（2 台：suspect_orphan=1，wired_by_header=1）
- `src/zephyr/gov_rule/__init__.py`（suspect_orphan，imported_by=0，last_commit=2026-09-16）
- `src/zephyr/gov_rule/standards_manager.py`（wired_by_header，imported_by=0，last_commit=2026-09-16）

### scripts.__init__.py（1 台：wired=1）
- `scripts/__init__.py`（wired，imported_by=0，last_commit=2026-06-21）

### scripts.ai_layer（1 台：wired_by_header=1）
- `scripts/ai_layer/run_ai_l1_scan_tick.py`（wired_by_header，imported_by=0，last_commit=2026-10-02）

### scripts.backtest（1 台：wired=1）
- `scripts/backtest/lane_e_enhanced.py`（wired，imported_by=0，last_commit=2026-09-16）

### scripts.check_naming_convention.py（1 台：wired=1）
- `scripts/check_naming_convention.py`（wired，imported_by=0，last_commit=2026-08-03）

### scripts.clone_guard_audit.py（1 台：wired_by_header=1）
- `scripts/clone_guard_audit.py`（wired_by_header，imported_by=0，last_commit=2026-08-21）

### scripts.compute_signals.py（1 台：wired_by_header=1）
- `scripts/compute_signals.py`（wired_by_header，imported_by=0，last_commit=2026-09-02）

### scripts.estimate_pit_backfill_cost.py（1 台：wired_by_header=1）
- `scripts/estimate_pit_backfill_cost.py`（wired_by_header，imported_by=0，last_commit=2026-09-02）

### scripts.ml（1 台：wired_by_header=1）
- `scripts/ml/run_sft_train.py`（wired_by_header，imported_by=0，last_commit=2026-08-24）

### scripts.post_checkout_guard.py（1 台：wired_by_header=1）
- `scripts/post_checkout_guard.py`（wired_by_header，imported_by=0，last_commit=2026-09-29）

### scripts.print_exam_summary.py（1 台：suspect_orphan=1）
- `scripts/print_exam_summary.py`（suspect_orphan，imported_by=0，last_commit=2026-08-21）

### scripts.scan_forward_days.py（1 台：wired_by_header=1）
- `scripts/scan_forward_days.py`（wired_by_header，imported_by=0，last_commit=2026-08-21）

### scripts.serve_docs.py（1 台：wired_by_header=1）
- `scripts/serve_docs.py`（wired_by_header，imported_by=0，last_commit=2026-09-07）

### scripts.setup_dev_env.py（1 台：wired_by_header=1）
- `scripts/setup_dev_env.py`（wired_by_header，imported_by=0，last_commit=2026-07-23）

### scripts.setup_git_guard_aliases.py（1 台：wired_by_header=1）
- `scripts/setup_git_guard_aliases.py`（wired_by_header，imported_by=0，last_commit=2026-08-21）

### scripts.verify_sentiment_hidden_driver.py（1 台：wired_by_header=1）
- `scripts/verify_sentiment_hidden_driver.py`（wired_by_header，imported_by=0，last_commit=2026-09-13）

### src.zephyr.infra_ops（1 台：wired=1）
- `src/zephyr/infra_ops/storage_cost_calculator.py`（wired，imported_by=0，last_commit=2026-09-16）

## 豁免在案（有结论，第三合法态——不打红不隐身，复查条件到期须处置）

- `scripts/crypto_daily_review.py`：币圈暂停开发（Owner 令 2026-10-04），脚本保留现状等恢复通知；恢复时接线、长期不用则退役（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 2027-01-04（90 天）未恢复则呈退役提案）
- `src/zephyr/ex_core/rules/crypto.py`：币圈暂停开发（Owner 令 2026-10-04），规则模块保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/feedback_loop/forensic/crypto_bootstrap.py`：币圈暂停开发（Owner 令 2026-10-04），取证自举件保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/features/cryptomarket/cm-engine.js`：币圈暂停开发（Owner 令 2026-10-04），前端引擎保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/pages/cryptobt.html`：币圈暂停开发（Owner 令 2026-10-04），币圈回测页保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/pages/cryptoinfo.html`：币圈暂停开发（Owner 令 2026-10-04），币圈信息页保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/pages/cryptomarket.html`：币圈暂停开发（Owner 令 2026-10-04），币圈行情页保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/pages/cryptopos.html`：币圈暂停开发（Owner 令 2026-10-04），币圈持仓页保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）
- `src/zephyr/frontend/dashboard/web/pages/cryptostrat.html`：币圈暂停开发（Owner 令 2026-10-04），币圈策略页保留现状等通知（依据 crypto-dev-paused-20261004；复查：币圈恢复开发通知，或 90 天未恢复则呈退役提案）

## align_all 第十二节接入（已施工，ff8f841edf）

1. 调用点：align_all.py 第十二节（图12 第十节/图13 第十一节之后）复用 run_attribution()（普查面只取计数，证据细节归本 30/31 号）。
2. 阈值：`--orphan-threshold` 缺省 report-only 恒 exit 0；设值后 **真孤儿**（两不沾且无结论）>阈值 或 悬空键>0 即 exit 1（悬空键不随阈值宽限恒硬）。Owner 立法口径（2026-10-04）：存在就要有用，或者有结论——终点=真孤儿 0。
3. 豁免册：config/coverage_exemption_registry.yaml（在案结论的机械载体，豁免=第三合法态；陈旧条目（路径不存在/已重新挂载）由普查显性报 stale_exemptions 促清册）。
