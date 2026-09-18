---
ttl: task_bound
completes_when: 全流通战役收官且六向台账连续两轮红件=0
---

# 六向台账（验收仪实测产出，勿手改；生成件=`scripts/automation/flowthrough_verifier.py`）

生成时间：2026-09-18 11:36:03.016513+00:00 · 裁定权：总包（本表仅出**建议**，规范 §2）

真源新鲜度：A_arch_model=fresh(0.07d); B_functional_domain_registry=fresh(0.01d); C_battle_map_domain_policy=fresh(0.02d); D_trading_decision_map=fresh(0.07d); E_data_tasks_and_schedule=fresh(0.01d); F_docs_03_modules_dirs=fresh(Noned); G_depgraph_runtime=fresh(0.82d)

## 三态建议分布

| 环节 | ① | ② | ③ | ④ | ⑤ | ⑥ | 建议 |
|---|---|---|---|---|---|---|---|
| FF-01 数据供给链（源 E：tasks+schedule） | 绿 | 红 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-02 research_incubation | 绿 | 红 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-03 model_training | 绿 | 红 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-04 backtest_validation | 绿 | 红 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-05 simulation_validation | 黄 | 黄-门位 | 不可测 | 绿 | 绿 | 黄 | **黄** |
| FF-06 stock_selection | 绿 | 红 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-07 buy_flow | 红 | 黄 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-08 sell_flow | 红 | 黄-门位 | 不可测 | 绿 | 红 | 黄 | **红** |
| FF-09 position_management | 红 | 黄-门位 | 不可测 | 绿 | 绿 | 黄 | **红** |
| FF-10 risk_control | 红 | 黄-门位 | 不可测 | 绿 | 红 | 黄 | **红** |
| FF-11 execution | 黄 | 黄-门位 | 绿 | 绿 | 绿 | 黄 | **黄** |
| FF-12 reconciliation | 红 | 黄-门位 | 绿 | 绿 | 绿 | 黄 | **红** |
| FF-13 横切机制层 | 不可测 | 不可测 | 不可测 | 红 | 不可测 | 黄 | **红** |
| FF-14 X_AI_RUNTIME | 不可测 | 黄-门位 | 不可测 | 绿 | 不可测 | 黄 | **黄** |
| FF-15 X_DELIVERY | 红 | 绿 | 不可测 | 绿 | 绿 | 黄 | **红** |
| FF-16 X_GOV_SUBSTRATE | 红 | 绿 | 绿 | 绿 | 红 | 黄 | **红** |
| FF-17 X_UNCLASSIFIED | 绿 | 黄-门位 | 不可测 | 绿 | 红 | 黄 | **黄** |
| COVERAGE-DIFF 推导环节 vs 骨架环节 | — | — | — | — | — | — | **黄** |

分布：红=13, 黄=5

## 逐环节六向明细

### FF-01 数据供给链（源 E：tasks+schedule） · 建议裁定 **红**

- 域：`D_ALT_DATA`, `D_DATA`, `D_DATA_ENG`, `D_DATA_GOV`, `D_DATA_SEC`, `D_INTEGRATION`, `D_INTEGRATION_GATEWAY`, `D_KNOWLEDGE`, `D_MKT_DATA`
- 代码路径：`src/zephyr/alt_data/`, `src/zephyr/data/`, `src/zephyr/data_eng/`, `src/zephyr/data_governance/`, `src/zephyr/data_security/`, `src/zephyr/integration/`, `src/zephyr/integration/mcp/`, `src/zephyr/integration/vector_memory/`, `src/zephyr/market_data/`
- 扫描文件数（实测）：357

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c0_meta.fetch_perf=103行; c1_backtest.regime_state_anchored=2235行@2026-09-18(0.8d); c1_market.adj_factor=21054931行@2026-09-18(0.8d) |
| ②转化能跑 | 红 | src\zephyr\alt_data\cohort_daily_ledger.py rc=1 2.06s 报错=ModuleNotFoundError: No module named 'schemas.categories' |
| ③出口有货 | 绿 | c1_market.alt_fx_rate_ecb=66行; c1_market.kline_daily=10085765行; c1_market.market_breadth_snapshot=125行 | data/source_health_streaks.json=1273B/68行 |
| ④下游能取 | 绿 | src 真消费者 888 / scripts-only 295 / tests-only 393 / 动态注册面 3 |
| ⑤哨兵在岗 | 绿 | 有阈值行 40 表 / allow_empty 白名单 1 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 324 处 / 有告警接线文件 24 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/alt_data/alt_data_connector.py` → `tests/alt_data/test_alt_data_connector.py`(0.75), `src/zephyr/alt_data/alt_data_catalog.py`(0.5), `tests/alt_data/test_alt_data_catalog.py`(0.4)
  - 孤儿候选 `src/zephyr/alt_data/alt_data_privacy_protector.py` → `tests/alt_data/test_alt_data_privacy_protector.py`(0.8), `src/zephyr/alt_data/alt_data_connector.py`(0.4), `src/zephyr/alt_data/alt_data_catalog.py`(0.4)
  - 孤儿候选 `src/zephyr/alt_data/alt_data_signal_extractor.py` → `tests/alt_data/test_alt_data_signal_extractor.py`(0.8), `src/zephyr/alt_data/alt_data_connector.py`(0.4), `src/zephyr/alt_data/alt_data_catalog.py`(0.4)
  - 孤儿候选 `src/zephyr/alt_data/alt_source_bootstrap.py` → `src/zephyr/alt_data/alt_source_health_manager.py`(0.4), `tests/alt_data/test_alt_source_health_manager.py`(0.33), `src/zephyr/strategy_pipeline/screen_source.py`(0.25)
  - 孤儿候选 `src/zephyr/alt_data/concept_factor_mapper.py` → `tests/alt_data/test_concept_factor_mapper.py`(0.75), `src/zephyr/autonomy_core/module_factory/module_mapper.py`(0.25), `src/zephyr/alt_data/policy_theme_mapper.py`(0.2)

- 动态注册面（BRK-009，不判孤儿）3 件：`policy_expectation_analyzer.py`∈['backtest_backlog.yaml']; `instrument_master.py`∈['backtest_backlog.yaml']; `sector_snapshot_collector.py`∈['dataflow_graph_registry.yaml']

### FF-02 research_incubation · 建议裁定 **红**

- 域：`D_DATA`, `D_DATA_ENG`, `D_DATA_GOV`, `D_DATA_SEC`, `D_INTELLIGENCE`, `D_KNOWLEDGE`, `D_ML_TRAIN`, `D_RESEARCH`
- 代码路径：`src/zephyr/data/`, `src/zephyr/data_eng/`, `src/zephyr/data_governance/`, `src/zephyr/data_security/`, `src/zephyr/integration/vector_memory/`, `src/zephyr/intelligence/`, `src/zephyr/intelligence/model_evaluation/`, `src/zephyr/research/`
- 扫描文件数（实测）：316

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c0_meta.fetch_perf=103行; c1_backtest.regime_state_anchored=2235行@2026-09-18(0.8d); c1_market.adj_factor=21054931行@2026-09-18(0.8d) |
| ②转化能跑 | 红 | src\zephyr\data\ch_parts_monitor.py rc=1 1.23s 报错=AttributeError: module 'calendar' has no attribute 'day_abbr' |
| ③出口有货 | 绿 | c1_market.alt_fx_rate_ecb=66行; c1_market.kline_daily=10085765行; c1_market.market_breadth_snapshot=125行 | data/source_health_streaks.json=1273B/68行 |
| ④下游能取 | 绿 | src 真消费者 802 / scripts-only 279 / tests-only 353 / 动态注册面 2 |
| ⑤哨兵在岗 | 绿 | 有阈值行 40 表 / allow_empty 白名单 1 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 236 处 / 有告警接线文件 20 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/data/c4_history_repair.py` → `scripts/data/repair_kline_tz_monthly.py`(0.25), `scripts/backtest/print_regime_history.py`(0.25), `src/zephyr/signal_ashare/market_breadth_history_store.py`(0.2)
  - 孤儿候选 `src/zephyr/data/capability_semantic_gate.py` → `tests/zephyr/data/test_capability_semantic_gate.py`(0.75), `src/zephyr/gov_enforcement/commit_gates/capability_consistency_gate.py`(0.5), `src/zephyr/data/capability_symbol_gate.py`(0.5)
  - 孤儿候选 `src/zephyr/data/cross_source_validator.py` → `tests/zephyr/data/test_cross_source_validator.py`(0.75), `src/zephyr/strategy_pipeline/screen_source.py`(0.25), `src/zephyr/data/redundant_source/source_switcher.py`(0.25)
  - 孤儿候选 `src/zephyr/data/data_compression_archiver.py` → `tests/data/test_data_compression_archiver.py`(0.75), `scripts/ch/archiver.py`(0.33), `src/zephyr/data_eng/services/synthetic_data/`(0.25)
  - 孤儿候选 `src/zephyr/data/foreign_market_coverage.py` → `tests/zephyr/data/test_foreign_market_coverage.py`(0.75), `tests/zephyr/data/calendar/test_market_calendar.py`(0.2), `src/zephyr/signal_ashare/market_state_sensor.py`(0.2)

- 动态注册面（BRK-009，不判孤儿）2 件：`instrument_master.py`∈['backtest_backlog.yaml']; `sector_snapshot_collector.py`∈['dataflow_graph_registry.yaml']

### FF-03 model_training · 建议裁定 **红**

- 域：`D_DATA`, `D_FACTOR`, `D_ML_TRAIN`, `D_RESEARCH`
- 代码路径：`src/zephyr/data/`, `src/zephyr/factor/`, `src/zephyr/intelligence/model_evaluation/`, `src/zephyr/research/`
- 扫描文件数（实测）：251

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c0_meta.fetch_perf=103行; c1_backtest.regime_state_anchored=2235行@2026-09-18(0.8d); c1_market.adj_factor=21054931行@2026-09-18(0.8d) |
| ②转化能跑 | 红 | src\zephyr\data\ch_parts_monitor.py rc=1 1.33s 报错=AttributeError: module 'calendar' has no attribute 'day_abbr' |
| ③出口有货 | 绿 | c1_market.alt_fx_rate_ecb=66行; c1_market.factor_feature_value=-1行; c1_market.kline_daily=10085765行 | data/runtime/factor_lifecycle_state.json=13855B/705行; data/source_health_streaks.json=1273B/68行 |
| ④下游能取 | 绿 | src 真消费者 789 / scripts-only 264 / tests-only 316 / 动态注册面 7 |
| ⑤哨兵在岗 | 绿 | 有阈值行 40 表 / allow_empty 白名单 1 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 182 处 / 有告警接线文件 14 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/data/c4_history_repair.py` → `scripts/data/repair_kline_tz_monthly.py`(0.25), `scripts/backtest/print_regime_history.py`(0.25), `src/zephyr/signal_ashare/market_breadth_history_store.py`(0.2)
  - 孤儿候选 `src/zephyr/data/capability_semantic_gate.py` → `tests/zephyr/data/test_capability_semantic_gate.py`(0.75), `src/zephyr/gov_enforcement/commit_gates/capability_consistency_gate.py`(0.5), `src/zephyr/data/capability_symbol_gate.py`(0.5)
  - 孤儿候选 `src/zephyr/data/cross_source_validator.py` → `tests/zephyr/data/test_cross_source_validator.py`(0.75), `src/zephyr/strategy_pipeline/screen_source.py`(0.25), `src/zephyr/factor/mine/causal_validator/`(0.25)
  - 孤儿候选 `src/zephyr/data/data_compression_archiver.py` → `tests/data/test_data_compression_archiver.py`(0.75), `scripts/ch/archiver.py`(0.33), `src/zephyr/data/data_service.py`(0.25)
  - 孤儿候选 `src/zephyr/data/foreign_market_coverage.py` → `tests/zephyr/data/test_foreign_market_coverage.py`(0.75), `src/zephyr/factor/ashare/market_structure/`(0.25), `src/zephyr/factor/ashare/cross_market/`(0.25)

- 动态注册面（BRK-009，不判孤儿）7 件：`instrument_master.py`∈['backtest_backlog.yaml']; `sector_snapshot_collector.py`∈['dataflow_graph_registry.yaml']; `ic_ir_evaluator.py`∈['dataflow_graph_registry.yaml']; `expectations.py`∈['factor_registry.yaml']; `engine.py`∈['ai_autonomy_authority_registry.yaml', 'cross_module_dependency_registry.yaml']; `momentum_factor.py`∈['factor_registry.yaml']

### FF-04 backtest_validation · 建议裁定 **红**

- 域：`D_BACKTEST`, `D_DATA`, `D_EXEC_SIM`, `D_FACTOR`, `D_POSITION`, `D_RISK`, `D_SIMULATION`
- 代码路径：`src/zephyr/backtest/`, `src/zephyr/data/`, `src/zephyr/execution_simulation/`, `src/zephyr/factor/`, `src/zephyr/position/`, `src/zephyr/risk/`, `src/zephyr/simulation/`
- 扫描文件数（实测）：430

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c0_meta.fetch_perf=103行; c1_backtest.regime_state_anchored=2235行@2026-09-18(0.8d); c1_backtest.strategy_screen=1306行 |
| ②转化能跑 | 红 | src\zephyr\data\ch_parts_monitor.py rc=1 1.12s 报错=AttributeError: partially initialized module 'pandas' has no attribute '_pandas_datetime_CAPI' (most likely due to a circular import) |
| ③出口有货 | 绿 | c1_market.alt_fx_rate_ecb=66行; c1_market.factor_feature_value=-1行; c1_market.kline_daily=10085765行 | data/runtime/factor_lifecycle_state.json=13855B/705行; data/source_health_streaks.json=1273B/68行 |
| ④下游能取 | 绿 | src 真消费者 1090 / scripts-only 330 / tests-only 667 / 动态注册面 13 |
| ⑤哨兵在岗 | 绿 | 有阈值行 40 表 / allow_empty 白名单 1 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 219 处 / 有告警接线文件 23 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/backtest/core/data_handler.py` → `tests/backtest/test_data_handler_pit.py`(0.5), `tests/backtest/test_tick_replay_data_handler.py`(0.4), `src/zephyr/data/data_service.py`(0.33)
  - 孤儿候选 `src/zephyr/backtest/core/overfitting_adjudicator.py` → `tests/backtest/test_overfitting_adjudicator.py`(0.67), `tests/regime/validation/test_overfitting_guard.py`(0.25), `tests/backtest/test_overfitting_detector.py`(0.25)
  - 孤儿候选 `src/zephyr/backtest/core/preflight_checker.py` → `tests/backtest/test_preflight_checker.py`(0.67), `src/zephyr/ex_core/premarket_checker.py`(0.33), `src/zephyr/data/integrity_checker.py`(0.33)
  - 孤儿候选 `src/zephyr/backtest/core/purged_kfold.py` → `tests/backtest/test_purged_kfold.py`(0.67)
  - 孤儿候选 `src/zephyr/backtest/implementations/ch_tick_replay.py` → `src/zephyr/backtest/core/tick_replay.py`(1.0), `tests/zephyr/backtest/test_ch_tick_replay.py`(0.67), `tests/backtest/test_tick_replay_data_handler.py`(0.4)

- 动态注册面（BRK-009，不判孤儿）10 件：`c1_runner.py`∈['experiment_registry.yaml']; `decay_monitor.py`∈['dataflow_graph_registry.yaml']; `param_analyzer.py`∈['dataflow_graph_registry.yaml']; `report_generator.py`∈['dataflow_graph_registry.yaml']; `result_comparator.py`∈['dataflow_graph_registry.yaml']; `scheduler.py`∈['cross_module_dependency_registry.yaml', 'infrastructure_registry.yaml']

### FF-05 simulation_validation · 建议裁定 **黄**

- 域：`D_BACKTEST`, `D_DIGITAL_TWIN`, `D_RISK`, `D_SIMULATION`
- 代码路径：`src/zephyr/backtest/`, `src/zephyr/digital_twin/`, `src/zephyr/risk/`, `src/zephyr/simulation/`
- 扫描文件数（实测）：166

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 黄 | c1_backtest.strategy_screen=1306行; c1_market.futures_kline_qmt=906行@2026-09-16(2.8d); c1_market.kline_daily=10085765行@2026-09-18(0.8d) || 过期未落容差=['c1_market.futures_kline_qmt'] |
| ②转化能跑 | 黄-门位 | 无可真跑入口（1 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 265 / scripts-only 64 / tests-only 321 / 动态注册面 7 |
| ⑤哨兵在岗 | 绿 | 有阈值行 3 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 29 处 / 有告警接线文件 6 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/backtest/core/data_handler.py` → `tests/backtest/test_data_handler_pit.py`(0.5), `tests/backtest/test_tick_replay_data_handler.py`(0.4), `src/zephyr/risk/var_data_prefetcher.py`(0.25)
  - 孤儿候选 `src/zephyr/backtest/core/overfitting_adjudicator.py` → `tests/backtest/test_overfitting_adjudicator.py`(0.67), `tests/regime/validation/test_overfitting_guard.py`(0.25), `tests/backtest/test_overfitting_detector.py`(0.25)
  - 孤儿候选 `src/zephyr/backtest/core/preflight_checker.py` → `tests/backtest/test_preflight_checker.py`(0.67), `src/zephyr/ex_core/pre_execution_checker.py`(0.25), `tests/ex_core/test_pre_execution_checker.py`(0.2)
  - 孤儿候选 `src/zephyr/backtest/core/purged_kfold.py` → `tests/backtest/test_purged_kfold.py`(0.67)
  - 孤儿候选 `src/zephyr/backtest/implementations/ch_tick_replay.py` → `src/zephyr/backtest/core/tick_replay.py`(1.0), `tests/zephyr/backtest/test_ch_tick_replay.py`(0.67), `tests/backtest/test_tick_replay_data_handler.py`(0.4)

- 动态注册面（BRK-009，不判孤儿）7 件：`c1_runner.py`∈['experiment_registry.yaml']; `decay_monitor.py`∈['dataflow_graph_registry.yaml']; `param_analyzer.py`∈['dataflow_graph_registry.yaml']; `report_generator.py`∈['dataflow_graph_registry.yaml']; `result_comparator.py`∈['dataflow_graph_registry.yaml']; `scheduler.py`∈['cross_module_dependency_registry.yaml', 'infrastructure_registry.yaml']

### FF-06 stock_selection · 建议裁定 **红**

- 域：`D_ALT_DATA`, `D_ASHARE_SIGNAL`, `D_CROSS_ASSET`, `D_DATA`, `D_FACTOR`, `D_FUNDAMENTAL_SIGNAL`, `D_INFRA_RUNTIME`, `D_INTEGRATION`, `D_INTELLIGENCE`, `D_KNOWLEDGE`, `D_MKT_DATA`, `D_ML_SERVE`, `D_ML_TRAIN`, `D_REGIME`, `D_SHARED`, `D_SIGNAL`, `D_SIGQC`
- 代码路径：`src/zephyr/alt_data/`, `src/zephyr/cross_asset/`, `src/zephyr/data/`, `src/zephyr/factor/`, `src/zephyr/infra_runtime/`, `src/zephyr/integration/`, `src/zephyr/integration/vector_memory/`, `src/zephyr/intelligence/`, `src/zephyr/intelligence/model_evaluation/`, `src/zephyr/market_data/`, `src/zephyr/ml_serve/`, `src/zephyr/regime/`, `src/zephyr/shared/shared_services/`, `src/zephyr/signal_ashare/`, `src/zephyr/signal_fundamental/`, `src/zephyr/signal_quality/`
- 扫描文件数（实测）：738

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c0_meta.fetch_perf=103行; c1_backtest.regime_state_anchored=2235行@2026-09-18(0.8d); c1_backtest.strategy_screen=1306行 |
| ②转化能跑 | 红 | src\zephyr\alt_data\cohort_daily_ledger.py rc=1 2.23s 报错=ModuleNotFoundError: No module named 'schemas.categories' |
| ③出口有货 | 绿 | c1_market.alt_fx_rate_ecb=66行; c1_market.factor_feature_value=-1行; c1_market.kline_daily=10085765行 | data/runtime/factor_lifecycle_state.json=13855B/705行; data/source_health_streaks.json=1273B/68行 |
| ④下游能取 | 绿 | src 真消费者 1346 / scripts-only 376 / tests-only 796 / 动态注册面 8 |
| ⑤哨兵在岗 | 绿 | 有阈值行 40 表 / allow_empty 白名单 1 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 306 处 / 有告警接线文件 21 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/alt_data/alt_data_connector.py` → `tests/alt_data/test_alt_data_connector.py`(0.75), `tests/alt_data/test_alt_data_catalog.py`(0.4), `tests/alt_data/test_alt_data_signal_extractor.py`(0.33)
  - 孤儿候选 `src/zephyr/alt_data/alt_data_privacy_protector.py` → `tests/alt_data/test_alt_data_privacy_protector.py`(0.8), `src/zephyr/alt_data/alt_data_connector.py`(0.4), `tests/alt_data/test_alt_data_connector.py`(0.33)
  - 孤儿候选 `src/zephyr/alt_data/alt_data_signal_extractor.py` → `tests/alt_data/test_alt_data_signal_extractor.py`(0.8), `src/zephyr/alt_data/alt_data_connector.py`(0.4), `tests/alt_data/test_alt_data_connector.py`(0.33)
  - 孤儿候选 `src/zephyr/alt_data/alt_source_bootstrap.py` → `src/zephyr/alt_data/alt_source_health_manager.py`(0.4), `tests/alt_data/test_alt_source_health_manager.py`(0.33), `src/zephyr/strategy_pipeline/screen_source.py`(0.25)
  - 孤儿候选 `src/zephyr/alt_data/concept_factor_mapper.py` → `tests/alt_data/test_concept_factor_mapper.py`(0.75), `src/zephyr/factor/value_factor.py`(0.25), `src/zephyr/factor/momentum_factor.py`(0.25)

- 动态注册面（BRK-009，不判孤儿）8 件：`policy_expectation_analyzer.py`∈['backtest_backlog.yaml']; `instrument_master.py`∈['backtest_backlog.yaml']; `sector_snapshot_collector.py`∈['dataflow_graph_registry.yaml']; `ic_ir_evaluator.py`∈['dataflow_graph_registry.yaml']; `expectations.py`∈['factor_registry.yaml']; `engine.py`∈['ai_autonomy_authority_registry.yaml', 'cross_module_dependency_registry.yaml']

### FF-07 buy_flow · 建议裁定 **红**

- 域：`D_ASHARE_SIGNAL`, `D_COMPLIANCE`, `D_INTEGRATION`, `D_INTELLIGENCE`, `D_ORCHESTRATOR`, `D_PF_ALLOC`, `D_PF_CORE`, `D_RISK`, `D_TRADING`
- 代码路径：`src/zephyr/compliance/`, `src/zephyr/integration/`, `src/zephyr/intelligence/`, `src/zephyr/orchestrator/`, `src/zephyr/pf_alloc/`, `src/zephyr/pf_core/`, `src/zephyr/risk/`, `src/zephyr/signal_ashare/`, `src/zephyr/trading/`
- 扫描文件数（实测）：650

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_backtest.crisis_gate_log=0行; c1_backtest.node_verdict=58行; c1_backtest.regime_snapshot_history=3621行 |
| ②转化能跑 | 黄 | src\zephyr\intelligence\model_routing\runtime_assembly.py rc=2 2.97s 报错=runtime_assembly: error: the following arguments are required: --task-type |
| ③出口有货 | 绿 | c1_market.market_pattern_certification=66行; c1_market.market_signal_history=329行 | data/databases/governance.db=183824384B/817628行 |
| ④下游能取 | 绿 | src 真消费者 831 / scripts-only 92 / tests-only 928 / 动态注册面 2 |
| ⑤哨兵在岗 | 绿 | 有阈值行 6 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 164 处 / 有告警接线文件 16 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/compliance/compliance_continuous_ops.py` → `tests/compliance/test_compliance_continuous_ops.py`(0.75), `src/zephyr/trading/trading_contracts/risk/compliance_rule.py`(0.25), `src/zephyr/frontend/compliance_dashboard.py`(0.25)
  - 孤儿候选 `src/zephyr/compliance/compliance_drift_detector.py` → `tests/compliance/test_compliance_drift_detector.py`(0.75), `src/zephyr/compliance/trading_compliance_detector.py`(0.5), `tests/model/test_model_drift_detector.py`(0.4)
  - 孤儿候选 `src/zephyr/compliance/compliance_policy_engine.py` → `tests/compliance/test_compliance_policy_engine.py`(0.75), `src/zephyr/compliance/compliance_rule_engine.py`(0.5), `tests/compliance/test_compliance_rule_engine.py`(0.4)
  - 孤儿候选 `src/zephyr/compliance/compliance_rule_engine.py` → `tests/compliance/test_compliance_rule_engine.py`(0.75), `src/zephyr/trading/trading_contracts/risk/compliance_rule.py`(0.67), `tests/compliance/test_compliance_policy_engine.py`(0.4)
  - 孤儿候选 `src/zephyr/compliance/compliance_tech_enabler.py` → `tests/compliance/test_compliance_tech_enabler.py`(0.75), `src/zephyr/trading/trading_contracts/risk/compliance_rule.py`(0.25), `src/zephyr/frontend/compliance_dashboard.py`(0.25)

- 动态注册面（BRK-009，不判孤儿）2 件：`rule_discovery_server.py`∈['registry_of_logs.yaml']; `prompt_version.py`∈['registry_of_logs.yaml']

### FF-08 sell_flow · 建议裁定 **红**

- 域：`D_POSITION`, `D_RISK`, `D_SELL_DECISION`, `D_TRADING`
- 代码路径：`src/zephyr/position/`, `src/zephyr/risk/`, `src/zephyr/sell_decision/`, `src/zephyr/trading/`
- 扫描文件数（实测）：243

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_backtest.node_verdict=58行; c1_market.account_nav_daily=0行; c1_market.futures_kline_qmt=906行@2026-09-16(2.8d) || 过期未落容差=['c1_market.futures_kline_qmt'] |
| ②转化能跑 | 黄-门位 | 无可真跑入口（4 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 415 / scripts-only 28 / tests-only 421 / 动态注册面 4 |
| ⑤哨兵在岗 | 红 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 178 处 / 有告警接线文件 14 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/position/core/cold_start_progression.py` → `tests/position/test_cold_start_progression.py`(0.75), `scripts/construction/start_brain.py`(0.25), `scripts/start_paper_session.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/cross_strategy_position_merger.py` → `tests/position/test_cross_strategy_position_merger.py`(0.8), `src/zephyr/sell_decision/core/position_triage.py`(0.2), `src/zephyr/position/core/strategy_book.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/position_behavior_classifier.py` → `tests/position/test_position_behavior_classifier.py`(0.75), `src/zephyr/sell_decision/core/position_triage.py`(0.25), `tests/sell_decision/test_position_triage.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/position_time_budget.py` → `tests/position/test_position_time_budget.py`(0.75), `src/zephyr/position/core/position_risk_budget_allocator.py`(0.4), `tests/position/test_position_risk_budget_allocator.py`(0.33)
  - 孤儿候选 `src/zephyr/position/core/sell_position_link.py` → `tests/position/test_sell_position_link.py`(0.75), `src/zephyr/sell_decision/core/position_triage.py`(0.25), `tests/sell_decision/test_position_triage.py`(0.2)

- 动态注册面（BRK-009，不判孤儿）4 件：`ashare_stop_loss_engine.py`∈['backtest_backlog.yaml', 'chart_pattern_registry.yaml']; `scaling_out.py`∈['backtest_backlog.yaml']; `recon_runner.py`∈['registry_of_logs.yaml']; `three_way_reconciliation.py`∈['backtest_backlog.yaml']

### FF-09 position_management · 建议裁定 **红**

- 域：`D_PF_ALLOC`, `D_PF_CORE`, `D_PLAN`, `D_POSITION`, `D_RISK`
- 代码路径：`src/zephyr/pf_alloc/`, `src/zephyr/pf_core/`, `src/zephyr/plan_engine/`, `src/zephyr/position/`, `src/zephyr/risk/`
- 扫描文件数（实测）：217

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_backtest.crisis_gate_log=0行; c1_backtest.regime_snapshot_history=3621行; c1_backtest.sim_pocket_daily=65行 |
| ②转化能跑 | 黄-门位 | 无可真跑入口（1 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 331 / scripts-only 25 / tests-only 358 / 动态注册面 6 |
| ⑤哨兵在岗 | 绿 | 有阈值行 5 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 45 处 / 有告警接线文件 11 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/pf_alloc/allocation_orchestrator.py` → `src/zephyr/reporting/review_orchestrator.py`(0.33), `src/zephyr/pf_alloc/allocation_inputs.py`(0.33), `tests/reporting/test_review_orchestrator.py`(0.25)
  - 孤儿候选 `src/zephyr/pf_alloc/core/forward_stop_loss.py` → `tests/pf_alloc/test_forward_stop_loss.py`(0.75), `src/zephyr/risk/stop_loss.py`(0.67), `tests/trading/test_stop_loss.py`(0.5)
  - 孤儿候选 `src/zephyr/pf_alloc/core/maxdd_limit_allocator.py` → `tests/pf_alloc/test_maxdd_limit_allocator.py`(0.75), `src/zephyr/risk/core/risk_budget_allocator.py`(0.2), `src/zephyr/position/core/core_satellite_allocator.py`(0.2)
  - 孤儿候选 `src/zephyr/pf_alloc/core/regime_bma_weighting.py` → `tests/pf_alloc/test_regime_bma_weighting.py`(0.75), `src/zephyr/regime/volatility_regime_alerter.py`(0.2), `src/zephyr/position/core/correlation_regime_monitor.py`(0.2)
  - 孤儿候选 `src/zephyr/pf_alloc/core/strategy_screener_3d.py` → `tests/pf_alloc/test_strategy_screener_3d.py`(0.67), `src/zephyr/position/core/strategy_book.py`(0.33), `src/zephyr/pf_core/strategy_engine/strategy_runner.py`(0.33)

- 动态注册面（BRK-009，不判孤儿）6 件：`multi_strategy_capital_allocator.py`∈['backtest_backlog.yaml']; `topn_momentum_strategy.py`∈['dataflow_graph_registry.yaml', 'model_registry.yaml']; `daily_warroom_pipeline.py`∈['backtest_backlog.yaml']; `intraday_tomorrow_forecast.py`∈['backtest_backlog.yaml']; `plan_deviation_monitor.py`∈['backtest_backlog.yaml']; `ashare_stop_loss_engine.py`∈['backtest_backlog.yaml', 'chart_pattern_registry.yaml']

### FF-10 risk_control · 建议裁定 **红**

- 域：`D_POSITION`, `D_REPORTING`, `D_RISK`, `D_SECURITY`, `D_TRADING`
- 代码路径：`src/zephyr/position/`, `src/zephyr/reporting/`, `src/zephyr/risk/`, `src/zephyr/security/access_control/orphan_judge/`, `src/zephyr/trading/`
- 扫描文件数（实测）：276

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_backtest.node_verdict=58行; c1_market.account_nav_daily=0行; c1_market.futures_kline_qmt=906行@2026-09-16(2.8d) || 过期未落容差=['c1_market.futures_kline_qmt'] |
| ②转化能跑 | 黄-门位 | 无可真跑入口（5 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 459 / scripts-only 28 / tests-only 450 / 动态注册面 3 |
| ⑤哨兵在岗 | 红 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 189 处 / 有告警接线文件 23 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/position/core/cold_start_progression.py` → `tests/position/test_cold_start_progression.py`(0.75), `scripts/construction/start_brain.py`(0.25), `scripts/start_paper_session.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/cross_strategy_position_merger.py` → `tests/position/test_cross_strategy_position_merger.py`(0.8), `src/zephyr/sell_decision/core/position_triage.py`(0.2), `src/zephyr/position/core/strategy_book.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/position_behavior_classifier.py` → `tests/position/test_position_behavior_classifier.py`(0.75), `src/zephyr/sell_decision/core/position_triage.py`(0.25), `tests/sell_decision/test_position_triage.py`(0.2)
  - 孤儿候选 `src/zephyr/position/core/position_time_budget.py` → `tests/position/test_position_time_budget.py`(0.75), `src/zephyr/position/core/position_risk_budget_allocator.py`(0.4), `tests/position/test_position_risk_budget_allocator.py`(0.33)
  - 孤儿候选 `src/zephyr/position/core/sell_position_link.py` → `tests/position/test_sell_position_link.py`(0.75), `src/zephyr/sell_decision/core/position_triage.py`(0.25), `tests/sell_decision/test_position_triage.py`(0.2)

- 动态注册面（BRK-009，不判孤儿）3 件：`ashare_stop_loss_engine.py`∈['backtest_backlog.yaml', 'chart_pattern_registry.yaml']; `recon_runner.py`∈['registry_of_logs.yaml']; `three_way_reconciliation.py`∈['backtest_backlog.yaml']

### FF-11 execution · 建议裁定 **黄**

- 域：`D_EX_CORE`, `D_EX_SOR`, `D_REPORTING`, `D_RISK`, `D_TRADING`
- 代码路径：`src/zephyr/ex_core/`, `src/zephyr/ex_sor/`, `src/zephyr/reporting/`, `src/zephyr/risk/`, `src/zephyr/trading/`
- 扫描文件数（实测）：305

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 黄 | c1_backtest.node_verdict=58行; c1_market.daban_board_event=936行@2026-09-15(3.8d); c1_market.daban_engine_load=936行@2026-09-15(3.8d) || 过期未落容差=['c1_market.daban_board_event', 'c1_market.daban_engine_load'] |
| ②转化能跑 | 黄-门位 | 无可真跑入口（4 件需门位） |
| ③出口有货 | 绿 | c1_market.execution_report=1行 |
| ④下游能取 | 绿 | src 真消费者 492 / scripts-only 46 / tests-only 544 / 动态注册面 5 |
| ⑤哨兵在岗 | 绿 | 有阈值行 2 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 215 处 / 有告警接线文件 15 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/ex_core/adapters/okx_broker.py` → `tests/ex_core/adapters/test_okx_broker.py`(0.67), `src/zephyr/governance/adapters/simulation_broker.py`(0.33), `src/zephyr/ex_core/adapters/miniqmt_broker.py`(0.33)
  - 孤儿候选 `src/zephyr/ex_core/async_fill_dispatcher.py` → `tests/ex_core/test_async_fill_dispatcher.py`(0.75), `src/zephyr/ex_core/fill_processor.py`(0.25), `src/zephyr/ex_core/fill_handler.py`(0.25)
  - 孤儿候选 `src/zephyr/ex_core/broker_link_probe.py` → `tests/ex_core/test_broker_link_probe.py`(0.75), `tests/reporting/test_miniqmt_order_link_probe.py`(0.33), `src/zephyr/governance/adapters/simulation_broker.py`(0.25)
  - 孤儿候选 `src/zephyr/ex_core/corporate_action_adjuster.py` → `tests/ex_core/test_corporate_action_adjuster.py`(0.75), `tests/trading/test_corporate_action_processor.py`(0.4), `tests/action/test_action_dispatcher.py`(0.2)
  - 孤儿候选 `src/zephyr/ex_core/daban_instant_circuit_breaker.py` → `tests/ex_core/test_daban_instant_circuit_breaker.py`(0.8), `tests/ex_core/test_daban_monitors.py`(0.17), `tests/ex_core/test_daban_execution.py`(0.17)

- 动态注册面（BRK-009，不判孤儿）5 件：`execution_report.py`∈['field_dictionary.yaml']; `pricing_policy.py`∈['backtest_backlog.yaml', 'universe_registry.yaml']; `trading_halt_resolver.py`∈['universe_registry.yaml']; `algo_execution_selector.py`∈['backtest_backlog.yaml']; `ashare_stop_loss_engine.py`∈['backtest_backlog.yaml', 'chart_pattern_registry.yaml']

### FF-12 reconciliation · 建议裁定 **红**

- 域：`D_BACKTEST`, `D_FACTOR`, `D_FBL_DETECTORS`, `D_FBL_DIAGNOSERS`, `D_FBL_VERIFICATION`, `D_FEEDBACK_LOOP`, `D_OPS`, `D_REPORTING`, `D_SIMULATION`, `D_TRADING`
- 代码路径：`src/zephyr/backtest/`, `src/zephyr/factor/`, `src/zephyr/feedback_loop/`, `src/zephyr/feedback_loop/detectors/`, `src/zephyr/feedback_loop/diagnosers/`, `src/zephyr/feedback_loop/verifiers/`, `src/zephyr/infrastructure/system_telemetry/`, `src/zephyr/reporting/`, `src/zephyr/simulation/`, `src/zephyr/trading/`
- 扫描文件数（实测）：842

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_backtest.node_verdict=58行; c1_backtest.strategy_screen=1306行; c1_market.account_nav_daily=0行 |
| ②转化能跑 | 黄-门位 | 无可真跑入口（1 件需门位） |
| ③出口有货 | 绿 | c1_market.factor_feature_value=-1行 | data/databases/governance.db=183824384B/817628行; data/runtime/factor_lifecycle_state.json=13855B/705行 |
| ④下游能取 | 绿 | src 真消费者 973 / scripts-only 84 / tests-only 1325 / 动态注册面 13 |
| ⑤哨兵在岗 | 绿 | 有阈值行 3 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 46 处 / 有告警接线文件 12 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/backtest/core/data_handler.py` → `tests/backtest/test_data_handler_pit.py`(0.5), `tests/backtest/test_tick_replay_data_handler.py`(0.4), `src/zephyr/trading/reference_data_manager.py`(0.25)
  - 孤儿候选 `src/zephyr/backtest/core/overfitting_adjudicator.py` → `tests/backtest/test_overfitting_adjudicator.py`(0.67), `tests/regime/validation/test_overfitting_guard.py`(0.25), `tests/backtest/test_overfitting_detector.py`(0.25)
  - 孤儿候选 `src/zephyr/backtest/core/preflight_checker.py` → `tests/backtest/test_preflight_checker.py`(0.67), `src/zephyr/ex_core/premarket_checker.py`(0.33), `tests/backtest/test_data_quality_checker.py`(0.2)
  - 孤儿候选 `src/zephyr/backtest/core/purged_kfold.py` → `tests/backtest/test_purged_kfold.py`(0.67)
  - 孤儿候选 `src/zephyr/backtest/implementations/ch_tick_replay.py` → `src/zephyr/backtest/core/tick_replay.py`(1.0), `tests/zephyr/backtest/test_ch_tick_replay.py`(0.67), `tests/backtest/test_tick_replay_data_handler.py`(0.4)

- 动态注册面（BRK-009，不判孤儿）10 件：`c1_runner.py`∈['experiment_registry.yaml']; `decay_monitor.py`∈['dataflow_graph_registry.yaml']; `param_analyzer.py`∈['dataflow_graph_registry.yaml']; `report_generator.py`∈['dataflow_graph_registry.yaml']; `result_comparator.py`∈['dataflow_graph_registry.yaml']; `scheduler.py`∈['cross_module_dependency_registry.yaml', 'infrastructure_registry.yaml']

### FF-13 横切机制层 · 建议裁定 **红**

- 域：
- 代码路径：
- 扫描文件数（实测）：0

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 不可测 | 无读源表字面量（该环节可能为纯编排/无表输入） |
| ②转化能跑 | 不可测 | 无可真跑入口（0 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 红 | src 真消费者 0 / scripts-only 0 / tests-only 0 / 动态注册面 0 |
| ⑤哨兵在岗 | 不可测 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 0 处 / 有告警接线文件 0 件 |

### FF-14 X_AI_RUNTIME · 建议裁定 **黄**

- 域：`D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_INFRA_A2A`, `D_INTEGRATION_GATEWAY`, `D_SECURITY_LLM`
- 代码路径：`src/zephyr/autonomy_core/`, `src/zephyr/autonomy_perm/`, `src/zephyr/infrastructure/a2a_protocol/`, `src/zephyr/integration/mcp/`, `src/zephyr/security/llm_defense/`
- 扫描文件数（实测）：298

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 不可测 | 无读源表字面量（该环节可能为纯编排/无表输入） |
| ②转化能跑 | 黄-门位 | 无可真跑入口（11 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 304 / scripts-only 5 / tests-only 414 / 动态注册面 2 |
| ⑤哨兵在岗 | 不可测 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 119 处 / 有告警接线文件 20 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/autonomy_core/__main__.py` → `tests/ba/test_ba_main.py`(0.5), `tests/autonomy/test_behavioral_auditor_main.py`(0.25), `tests/agent/test_agent_spec_main.py`(0.25)
  - 孤儿候选 `src/zephyr/autonomy_core/agent_observability.py` → `tests/agent/test_agent_observability.py`(0.67), `src/zephyr/security/llm_defense/llm_security/layers/l6_observability.py`(0.5), `src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py`(0.5)
  - 孤儿候选 `src/zephyr/autonomy_core/agents/algorithm_agent_entry.py` → `src/zephyr/autonomy_core/agents/governance_agent_entry.py`(0.5), `src/zephyr/autonomy_core/agents/business_agent_entry.py`(0.5), `src/zephyr/autonomy_core/agents/self_iteration_agent_entry.py`(0.4)
  - 孤儿候选 `src/zephyr/autonomy_core/agents/governance_agent_entry.py` → `src/zephyr/autonomy_core/agents/business_agent_entry.py`(0.5), `src/zephyr/autonomy_core/agents/algorithm_agent_entry.py`(0.5), `src/zephyr/autonomy_core/agents/self_iteration_agent_entry.py`(0.4)
  - 孤儿候选 `src/zephyr/autonomy_core/agents/researcher_agent.py` → `tests/autonomy/test_researcher_agent.py`(0.67), `src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py`(0.5), `src/zephyr/security/llm_defense/llm_security/layers/l8_multi_agent.py`(0.33)

- 动态注册面（BRK-009，不判孤儿）2 件：`context_budget.py`∈['functional_domain_registry.yaml']; `context_budget_tracker.py`∈['ai_autonomy_authority_registry.yaml']

### FF-15 X_DELIVERY · 建议裁定 **红**

- 域：`D_FRONTEND`, `D_INFRA_TELEMETRY`
- 代码路径：`src/zephyr/frontend/`, `src/zephyr/infrastructure/system_telemetry/`
- 扫描文件数（实测）：82

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c0_meta.stock_list=-1行; c1_backtest.decision_daily=25行; c1_backtest.node_verdict=58行 || 断链=['c0_meta.stock_list'] |
| ②转化能跑 | 绿 | src\zephyr\infrastructure\system_telemetry\measure_calibration.py rc=0 2.23s |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 105 / scripts-only 11 / tests-only 87 / 动态注册面 2 |
| ⑤哨兵在岗 | 绿 | 有阈值行 2 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=True 违规=0 |
| ⑥失败会响 | 黄 | 静默放行候选 85 处 / 有告警接线文件 9 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/frontend/compliance_dashboard.py` → `tests/frontend/test_compliance_dashboard.py`(0.67), `tests/governance/observability/test_dashboard_unit.py`(0.25), `tests/frontend/test_dashboard_feeds.py`(0.25)
  - 孤儿候选 `src/zephyr/frontend/dashboard/api_server.py` → `tests/frontend/test_api_server_ch_timeout.py`(0.5), `tests/frontend/test_api_server_cron_single_source.py`(0.33), `src/zephyr/integration/mcp/telemetry_server.py`(0.33)
  - 孤儿候选 `src/zephyr/frontend/dashboard/app.py` → `src/zephyr/frontend/dashboard/app_panel.py`(0.5), `tests/governance/observability/test_app_panel_unit.py`(0.25)
  - 孤儿候选 `src/zephyr/frontend/domain_mapping_view.py` → `tests/frontend/test_domain_mapping_view.py`(0.75), `tests/frontend/test_value_stream_view.py`(0.17), `tests/frontend/test_trace_waterfall_view.py`(0.17)
  - 孤儿候选 `src/zephyr/frontend/frontend_api_proxy.py` → `tests/frontend/test_frontend_api_proxy.py`(0.75), `src/zephyr/frontend/dashboard/api_server.py`(0.25), `scripts/tests/test_frontend_components.py`(0.2)

- 动态注册面（BRK-009，不判孤儿）2 件：`app_panel.py`∈['cross_module_dependency_registry.yaml']; `asset_inventory.py`∈['cross_module_dependency_registry.yaml', 'registry_of_logs.yaml']

### FF-16 X_GOV_SUBSTRATE · 建议裁定 **红**

- 域：`D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_AUDITTEST`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CONTRACTS`, `D_DATA_SCRIPTS`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_META_SCRIPTS`, `D_SEC_SCRIPTS`, `D_STRUCT_SCRIPTS`, `D_TEST`
- 代码路径：``, `architecture_model/`, `docs/02_enterprise_architecture/`, `scripts/arch_guard`, `scripts/governance/`, `scripts/governance/_archive`, `scripts/governance/d11_compliance`, `scripts/governance/d1_structure`, `scripts/governance/d3_metadata`, `scripts/governance/d5_architecture`, `scripts/governance/d6_security`, `scripts/governance/d7_code`, `scripts/governance/meta`, `src/zephyr/gov_audit/`, `src/zephyr/gov_code_quality/code_dedup/`, `src/zephyr/gov_drift/`, `src/zephyr/gov_enforcement/rule_enforcement/`, `src/zephyr/gov_rule/`, `src/zephyr/governance/`, `src/zephyr/governance/ops_governance/`, `src/zephyr/shared/contracts`, `tests/`
- 扫描文件数（实测）：900

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 红 | c1_market.macro_data=50168行@2026-09-18(0.8d); c1_market.xxx=-1行 || 断链=['c1_market.xxx'] |
| ②转化能跑 | 绿 | scripts\governance\check_registry_of_logs.py rc=0 8.28s 报错=[WARN] 覆盖度 59.0% 低于目标 95% |
| ③出口有货 | 绿 | data/databases/governance.db=183824384B/817628行; data/runtime_violation_snapshot/latest.json=3207B/71行 |
| ④下游能取 | 绿 | src 真消费者 1175 / scripts-only 1384 / tests-only 1518 / 动态注册面 18 |
| ⑤哨兵在岗 | 红 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 188 处 / 有告警接线文件 12 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `scripts/arch_guard/_arch_ssot.py` → `scripts/governance/d5_architecture/validators/validate_ssot.py`(0.33), `tests/risk/test_risk_ssot.py`(0.25), `tests/governance/rule_bridge/test_ssot_gate.py`(0.25)
  - 孤儿候选 `scripts/governance/_archive/one_off/check_exam_case_consistency.py` → `scripts/governance/d7_code/check_module_id_consistency.py`(0.4), `scripts/governance/d3_metadata/check_registry_consistency.py`(0.4), `scripts/arch_guard/check_schema_consistency.py`(0.4)
  - 孤儿候选 `scripts/governance/_archive/prototype/adversarial_sys_master_test.py` → `tests/gate/test_sys_master_compliance.py`(0.6), `tests/utils/test_adversarial_shared.py`(0.4), `tests/rollback/test_rollback_adversarial.py`(0.4)
  - 孤儿候选 `scripts/governance/_shared/algo_flow_drafter.py` → `scripts/governance/d5_architecture/generators/externalize_algo_flow.py`(0.5), `scripts/governance/d5_architecture/checkers/check_algo_flow.py`(0.5), `scripts/governance/_shared/algo_flow_applier.py`(0.5)
  - 孤儿候选 `scripts/governance/_shared/algo_flow_validate_marker.py` → `scripts/governance/d5_architecture/generators/externalize_algo_flow.py`(0.4), `scripts/governance/d5_architecture/checkers/check_algo_flow.py`(0.4), `scripts/governance/_shared/algo_flow_drafter.py`(0.4)

- 动态注册面（BRK-009，不判孤儿）10 件：`check_fe_acl_boundary.py`∈['rule_registry_collection.yaml']; `constants.py`∈['infrastructure_registry.yaml']; `encoding.py`∈['chart_pattern_registry.yaml', 'rule_enforcement_registry.yaml']; `file_utils.py`∈['functional_domain_registry.yaml', 'registry_of_logs.yaml']; `frontmatter.py`∈['ai_autonomy_authority_registry.yaml', 'ai_risk_register.yaml']; `terminology_loader.py`∈['cross_module_dependency_registry.yaml', 'terminology_glossary.yaml']

### FF-17 X_UNCLASSIFIED · 建议裁定 **黄**

- 域：`D_INFRASTRUCTURE`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_SIGLEGACY`
- 代码路径：`src/zephyr/infra_ops/`, `src/zephyr/infrastructure/rollback/`, `src/zephyr/shared/contracts/`, `src/zephyr/signal_fundamental/`
- 扫描文件数（实测）：190

| 向 | 判定 | 实测证据 |
|---|---|---|
| ①入口有料 | 绿 | c1_market.st_stock_list=376340行@2026-09-18(0.8d) |
| ②转化能跑 | 黄-门位 | 无可真跑入口（1 件需门位） |
| ③出口有货 | 不可测 | 声明 sink 为空（需蓝图/注册表补） |
| ④下游能取 | 绿 | src 真消费者 437 / scripts-only 10 / tests-only 309 / 动态注册面 4 |
| ⑤哨兵在岗 | 红 | 有阈值行 0 表 / allow_empty 白名单 0 表（白名单不判绿） / breach 实跑=False 违规=None |
| ⑥失败会响 | 黄 | 静默放行候选 90 处 / 有告警接线文件 17 件 |

- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）：
  - 孤儿候选 `src/zephyr/infrastructure/rollback/cascade_failure_simulator.py` → `tests/infrastructure/process_lifecycle/test_cascade_failure_simulator.py`(0.75), `tests/rollback/test_rollback_simulator.py`(0.2)
  - 孤儿候选 `src/zephyr/infrastructure/rollback/credential_rotation_trigger.py` → `tests/governance/access_control/test_credential_rotation_trigger.py`(0.75), `tests/governance/access_control/test_secret_rotation_aware.py`(0.17), `tests/automation/test_auto_rollback_trigger.py`(0.17)
  - 孤儿候选 `src/zephyr/infrastructure/rollback/cross_platform_shell.py` → `tests/cross/test_cross_platform_shell.py`(0.75), `tests/cross/test_cross_layer.py`(0.2)
  - 孤儿候选 `src/zephyr/infrastructure/rollback/hallucination_guard.py` → `tests/governance/adversarial/test_hallucination_guard.py`(0.67), `src/zephyr/security/access_control/guards/permission_guard.py`(0.33), `tests/contracts/test_rbac_guard_root.py`(0.2)
  - 孤儿候选 `src/zephyr/infrastructure/rollback/venv_sync.py` → `tests/governance/lifecycle/test_venv_sync.py`(0.67), `tests/governance/integration/test_submodule_sync.py`(0.25)

- 动态注册面（BRK-009，不判孤儿）4 件：`intent_archiver.py`∈['registry_of_logs.yaml']; `knowngoodstate_ledger.py`∈['registry_of_logs.yaml']; `rollback_abuse_detector.py`∈['registry_of_logs.yaml']; `rollback_audit_nexus.py`∈['registry_of_logs.yaml']

### COVERAGE-DIFF 推导环节 vs 骨架环节

- 推导环节（17）：FF-01, FF-02, FF-03, FF-04, FF-05, FF-06, FF-07, FF-08, FF-09, FF-10, FF-11, FF-12, FF-13, FF-14, FF-15, FF-16, FF-17
- 骨架环节（16）：FF-01, FF-02, FF-03, FF-04, FF-05, FF-06, FF-07, FF-08, FF-09, FF-10, FF-11, FF-12, FF-13, FF-14, FF-15, FF-16
- 仅在骨架：无；仅在推导：['FF-17']
- 未被 flow_stage 机械归口的 depgraph 域：33 个

