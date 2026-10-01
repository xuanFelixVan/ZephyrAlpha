---
ttl: task_bound
title: S3 挖矿档·G 段回测模拟链（F64-F71）——W3-2
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# G 段·回测模拟链（F64-F71）六向台账（W3-2 代码级核验）

> 段结论：8 环节全挖干，无断链。段健康：绿维持。
> 注意：骨架中 G-01 三册路径写 config/ 为漂移（真身在 docs/01_policies_and_standards/_registry/catalogs/）。

## G-01(F64) 回测三件套

| 维度 | 台账 |
|------|------|
| 上游 | REG 三册（静态真源） |
| 下游 | F65/F66（每次回测 MUST 引用） |
| 生产者 | 三册真源：`docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml`（universe_id 计 **9 条**，:76 universes: 段，UNI-DYNAMIC-001 打板连板梯队池等）、`benchmark_registry.yaml`（**10 条**）、`cost_model_registry.yaml`（**7 条**） |
| 消费者 | 回测引擎族/考试族/工厂格子（MUST 引用面） |
| 自动化态 | 静态册（引用态，门禁保证 MUST） |
| 运行态 | 册在 HEAD 且有条目；骨架写"config/universe_registry.yaml"路径漂移（实际路径如上，find 全仓唯一命中处） |
| 三态复核 | **挖干** ✅（路径漂移注记：§2 代码入口列需刷） |

## G-02(F65) 回测引擎族

| 维度 | 台账 |
|------|------|
| 上游 | F06（CH 行情）/F64（三册口径） |
| 下游 | F66（预注册归档）/F70（偏差检测） |
| 生产者 | `src/zephyr/backtest/core/matching_engine.py:271`（MatchingEngine，:1170 StkLimitProvider；112 LiquidityGuardConfig）；`src/zephyr/backtest/implementations/ch_tick_replay.py:61`（fetch_historical）；event_driven_engine.py / vectorized_engine.py |
| 消费者 | backtest/implementations/{event_driven_engine, vectorized_engine}.py、scripts/backtest/ibt/ibt_runner.py（grep -rln 命中） |
| 自动化态 | 事件（跑批触发） |
| 运行态 | `data/backtest_artifacts/bt-*.json` 60+ 件（bt-* 32 + bt-fw-* 26 + bt-tick-* 2；最新 bt-8607ffc2.json 09-23 14:21） |
| 三态复核 | **挖干** ✅ |

## G-03(F66) 回测预注册与七步循环

| 维度 | 台账 |
|------|------|
| 上游 | F64（阈值口径） |
| 下游 | F25（入库）/F67（实验登记） |
| 生产者 | `scripts/backtest/generate_backtest_backlog.py:296`（main）；sim_daily_runner.py 六腿（plan-bridge/plan-execute/e4-replay/report/settle/bridge-execute，:1587 注册） |
| 消费者 | 跑批归档链（无注册不归档门） |
| 自动化态 | 手动预注册门+跑批 |
| 运行态 | `data/backtest_artifacts/runs/` 实测 **191 目**，最新 VAL-P0-20260930-163635（09-30 预注册跑在档） |
| 三态复核 | **挖干** ✅ |

## G-04(F67) 实验登记与档案

| 维度 | 台账 |
|------|------|
| 上游 | F66 |
| 下游 | F50（绩效归因回灌） |
| 生产者 | 真源册 `docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`：experiment_id 计 **74 条**（骨架写"11 条档案"——计数漂移 ×6.7，实验档案持续累积） |
| 消费者 | F50 绩效链/评审周期 |
| 自动化态 | 手动登记（+跑批写入口） |
| 运行态 | 册在 HEAD，74 条在册 |
| 三态复核 | **挖干** ✅（计数漂移注记） |

## G-05(F68) GPU 矩阵/工厂格子

| 维度 | 台账 |
|------|------|
| 上游 | F13（算力调度心跳） |
| 下游 | F66（格子产物归考试） |
| 生产者 | `src/zephyr/trading/gpu_consensus_scheduler.py:88`（ConsensusRequest；:65 ConsensusPriority）；`scripts/backtest/factory_grid_executor.py`（exam_cost_gate 消费者，G-06 交叉证） |
| 消费者 | 考试/共识矩阵消费面 |
| 自动化态 | resource_profile_registry.yaml:975 manual_factory_grid_anova、:995 manual_factory_grid_executor（手动档注册在案） |
| 运行态 | `data/strategy_intake/grid_gpu_sectorcond_20260924-0834/`（09-24 格子批：sector_index.json/is_holdout.npy 在）；`data/backtest_artifacts/fw-auto/` 最后 09-15；**10-01 未取到在跑实拍**（假日+采样缺失），"T1 在跑禁中动"注记沿用——禁中动铁律照旧执行 |
| 三态复核 | **挖干** ✅（T1 在跑注记沿用；本轮无在跑反证，不降级） |

## G-06(F69) T0/成本门/IBT

| 维度 | 台账 |
|------|------|
| 上游 | F64 成本双口径 |
| 下游 | F66 门判定 |
| 生产者 | `src/zephyr/backtest/regime_validation/exam_cost_gate.py`（:96 BreakevenGateConfig、:127 BreakevenGateVerdict、:152 breakeven_cost_star_from_net_line、:176 monotonic_grid_violations） |
| 消费者 | scripts/backtest/{calibrate_cost_tier_redblue, f06_e4_wfa_exam, exam_cost_reexam, factory_grid_executor, t1_t2_handover}.py（grep -rln 5 处命中） |
| 自动化态 | 事件（考试内嵌门判定） |
| 运行态 | 消费面 5 脚本在册（t1_t2_handover=移交链在） |
| 三态复核 | **挖干** ✅ |

## G-07(F70) 模拟撮合与偏差检测

| 维度 | 台账 |
|------|------|
| 上游 | F65 回测产物 |
| 下游 | F72（模拟盘准入）/F23 考试判定 |
| 生产者 | `src/zephyr/simulation/look_ahead_bias_detector.py`；`src/zephyr/simulation/overfitting_protection_gate.py:66`（ProtectionLayer）；`src/zephyr/simulation/deflated_sharpe_calculator.py:388`（DeflatedSharpeCalculator；:96 DSRConfig） |
| 消费者 | backtest/core/{decision_gate, metrics, overfitting_adjudicator}.py、backtest/regime_validation/c4_deflated_sharpe_runner.py、simulation/sharpe_calculator_fixer.py、scripts/backtest/dsr_recalc_backfill.py |
| 自动化态 | 事件（回测产出即检） |
| 运行态 | 消费面 backtest core 三件在码（判定链闭合）；dsr_recalc_backfill 回填脚本在册 |
| 三态复核 | **挖干** ✅ |

## G-08(F71) AutoRuntime Core

| 维度 | 台账 |
|------|------|
| 上游 | 全链状态 |
| 下游 | 全链（节律调度/三层路由/work DAG） |
| 生产者 | `src/zephyr/trading/auto_runtime_core.py:102`（AutoRuntimeCore，1335 行；:494 run_boot_triple_alignment）；入口 `src/zephyr/trading/__main__.py:32`（MOD-INF-035） |
| 消费者 | 全链（系统大脑） |
| 自动化态 | 常驻（手动启动后自动运行；__main__.py:18 M10 豁免注记：reconcile 轮询=系统心跳设计，转纯事件驱动=独立架构倡议） |
| 运行态 | `.runtime/logs/reconcile_worker_*.log` 最新 10-01 14:01（e9e89d98…bb369a55）——轮询心跳今日在跑实拍 |
| 三态复核 | **挖干(P0)** ✅ |
