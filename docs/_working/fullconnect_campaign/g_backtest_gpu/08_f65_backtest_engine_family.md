---
ttl: task_bound
title: "F65 回测引擎族——事件驱动引擎+CH tick replay+撮合+组合核算（backtest 九子包）"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F65 · 回测引擎族（总册状态 built/P1；本卷复核=built 维持，九子包实扫与任务书口径逐一相符，锚点一处漂移）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | F06 数据链（kline_daily_hfq 四窗全绿 W_IS 484.7 万行/4996 标的，M2-06 实锚）；tick 数据（MiniQmtQuoteProvider 同构 duck-type，ch_tick_replay.py:8 实锚）；F64 三指定（universe/benchmark/cost_model） |
| 下游消费 | F66 预注册循环（SOP-B 七步每步调引擎）；F67 experiment_tracking adapters（vectorized/strategy_runner/c1/c2c3 四 adapter 实测）；pf_core 策略族、ex_sor rl_exec、intelligence/model_evaluation、library/lookup（本日 grep 消费域实测） |
| 自动化触发 | 库件 imported（无自有触发）；跑批经 factory_grid_executor/ibt_runner/sim_daily_runner 三入口 |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_backtest/blueprint.md（MOD-BT-001/090/222/033，M2-02 实锚）；引擎双体真值=M2 总览 §二（_c4_engine 向量化考尺 vs DefaultBacktestEngine 整装 IBT） |
| 门禁与质量尺 | 引擎护栏：execution_lag_days=1 硬断言+lag0 raise/ImplausibleBacktestError/CH 空串→RuntimeError（M2-06）；红蓝四向 4 轮 8/8→8/8 连续两轮 0 闭环；IBT HOLDOUT 单次烧毁（-12.2%/-1.389 C 门不过）；tests/backtest/ 119 件（M2-02 实测） |
| 当前运行状态 | **绿**（代码+测试+红蓝闭环在案；GPU T1 跑批曾以本引擎全档 35.33s/格 实测口径出证） |

## 二、子模块三级枚举（src/zephyr/backtest/ 九子包本日实扫，.py 计数含 __init__）

| 子包 | .py 数 | 内容（实测件名） |
|---|---|---|
| core | **22** | matching_engine.py（1321 行撮合真源）/matching_logic（bid1/ask1 预校验口径）/engine_base/tick_replay/portfolio（组合核算）/data_handler/metrics/pit_manager/purged_kfold/cpcv/walk_forward/n_trial_ledger（DSR 分母）/overfitting_detector/adjudicator/closed_book_gate/decision_gate/preflight_checker/cost_attribution/cost_model_calibration/strategy_cpcv_matrix/strategy_validation_pipeline |
| regime_validation | **12** | exam_cost_gate.py（232 行，F69 真身）/condition_package/c1_comparator/c1_runner/c2_extreme_event_protection/c3_throttle_attribution/c4_deflated_sharpe_runner/e2_stationary_bootstrap/e3_param_sensitivity/e4_cost_sensitivity/shrinkage_provider |
| services | **10** | layered_validation_pipeline/report_generator/result_comparator/anomaly_diagnoser/cache_manager/data_quality_checker/decay_monitor/param_analyzer/scheduler |
| implementations | **5** | vectorized_engine.py（DefaultBacktestEngine，IBT 用）/event_driven_engine.py/**ch_tick_replay.py**（140 行，1 档降级如实登记 :8/:54/:116）/shrinkage_engine.py |
| io | **3** | 落盘/装载面 |
| api/models/infrastructure/_extensions | 各 1 | **空壳包（仅 __init__）**，占位 |
| 根 | run_archive.py（366 行） | run 目录归档（verify_run_archive.py 消费 :4 DEPENDENCIES 实锚） |

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 撮合/组合核算（core） | built wired | 22 件实扫；matching_engine 1321 行+红蓝审计 49,147 fills T+1 零违例（M2-06） |
| tick replay | built（1 档降级显式） | ch_tick_replay 140 行：2-5 档填 0 如实降级、撮合只用 bid1/ask1（:8/:116 实测） |
| 引擎双体口径 | built 但**两真相** | _c4_engine（考尺）vs vectorized_engine（整装）成本口径不同源=IBT-D01 待裁 |
| 空壳四包 | 占位未施工 | api/models/infrastructure/_extensions 各仅 __init__（本日 ls） |

### 骨架勘误
- 总册 F65 锚点"core/matching_engine.py、ch_tick_replay.py"——**ch_tick_replay.py 实居 implementations/ 非 core/**（本日 find 实证）；matching_engine.py 在 core/ 无误。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 引擎成本口径两真相（IBT-D01，GPU 毕业生复考换尺） | Owner 裁 R-M2-2（双口径出证过渡案零重跑） | P1（Owner） |
| 2 | 组合构建占位（等权 1/15，7 态×15 员 105 格空，IBT-C01） | 与 pf_alloc 分配合流施工（M2-06/07 双册同判） | P1 |
| 3 | IBT 成绩单 22 件蒸发（尾件主区盘面不见） | runner 幂等可重放重建（移交施工班，IBT-B03） | P1 |
| 4 | 空壳四包 | 按内收判据评审：零触发零消费→退役或补实 | P2 |
| 5 | regime_snapshot_history 多 run 重叠无机械闸（W_IS 2312 行=2 run） | condition_package 加 run 版本钉（M2-04 堵点 5，跨车道） | P2 |

## 五、自审闸三态
**挖干可施工**（九子包逐包实扫计数与任务书口径相符；勘误 1 条锚点路径；M2 车道 6 册引用不重挖，本卷补九子包枚举与消费域实测）。

## 六、复跑命令
```bash
for d in core regime_validation services implementations io; do echo "$d: $(ls src/zephyr/backtest/$d/*.py | wc -l)"; done   # 22/12/10/5/3
wc -l src/zephyr/backtest/core/matching_engine.py src/zephyr/backtest/implementations/ch_tick_replay.py   # 1321/140
find src/zephyr/backtest -name "ch_tick_replay.py"     # implementations/ 非 core/
grep -rln "from zephyr.backtest\|import zephyr.backtest" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v "src/zephyr.backtest" | wc -l   # 消费域
```
