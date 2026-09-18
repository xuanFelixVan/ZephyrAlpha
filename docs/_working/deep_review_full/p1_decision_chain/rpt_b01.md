---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——事件驱动回测引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：事件驱动回测引擎（B01）

- 状态: **已审**
- 级别: P0｜类型: 引擎
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/implementations/event_driven_engine.py:102`
- 生产调用方: `src/zephyr/pf_core/strategy_engine/strategy_runner.py:212,296`（run_tick_backtest/run_tick_strategy_backtest）、`src/zephyr/pf_core/topn_momentum_strategy.py`；引擎内 WFA/detect_overfitting/decision_gate 桥接方法经 grep **零生产调用方**
- 测试文件: tests/backtest/test_event_driven_engine.py（161 行，3 测试，87 项关联批全绿 3.51s）
- 备注: 审查范围含其直接依赖 portfolio.py / engine_base.py / metrics.py（缺陷根因落点如实标注归属文件）

## 1 对象快照

- 范围：EventDrivenEngine（run_tick 主流程 + on_tick 回调 + 桥接方法）；依赖链 TickReplayEngine→MatchingEngine.generate_fills_with_tick→Portfolio.apply_fill→calculate_full_metrics 全部实读。
- 排除项：MatchingEngine/MatchingLogic 内部数学归 B03 详查，本报告只按消费口径引用；TickReplay 归 B06。
- 测试覆盖概况：3 个测试只断言 11 必填字段非 None + strategy_id（test_event_driven_engine.py:102-118），**无任何数值断言**；20 tick < MIN_SAMPLES_FOR_SHARPE=60，测试从未走到正样本量的指标路径。
- 材料包缺项声明：运行时证据包（近 N 天 error 日志）未取（无生产 tick 回测运行痕迹可查）；数据画像未做（tick 数据真机不可达）。
- 变更热力：30 commits（--follow），近频返工区，末次 2026-09-16。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **tick 频 NAV 直入日频年化 metrics，全部指标量纲错乱**：update_market_value 逐 tick 落 NAV，calculate_full_metrics 用默认 periods_per_year=252 年化；实证单日 4000 tick +1% → annual_return=0.0627%、sharpe=-214847、win_rate=1.0（"日度正收益占比"口径退化为 tick 级，metrics.py:140-143 的 P1-3 澄清在本引擎失效）；DSR 也吃同一错量纲收益序列（metrics.py:311-334） | event_driven_engine.py:291,313-317；metrics.py:106-124,311-334 | P1 | 跑 `.runtime/tmp/rev_b01_t1_probe.py`（本次审查留存，24h TTL）或手造 4000 点线性 NAV 调 calculate_metrics 看三指标 |
| A | **T+1 锁定在 tick 时间戳粒度失效**：portfolio.py:268 以 `pos.buy_date == fill.date` 精确相等判同日，tick 级 fill.date 带秒级时间戳 → 当日 10:00:00 买入、10:00:01 卖出被放行（allow_t_plus_1=False 形同虚设）。回测可行集>实盘可行集，做T成绩虚高+实盘必拒单。实证 REPRO-1 通过 | portfolio.py:268（根因）；event_driven_engine.py:285（受害调用）；matching_engine.py:956（date=timestamp 直传） | P1 | 同上 probe REPRO-1：构造两笔差 1 秒的 BUY/SELL 直接打 Portfolio.apply_fill |
| A.3 | 测试假阳性风险：3 测试全为字段非 None 断言，撮合/T+1/指标数值全无验证；fixture spread 10bps + ask_vol_1=100 股恰好走部分成交路径但无人断言其正确性 | tests/backtest/test_event_driven_engine.py:102-118 | P2 | 给测试补一条"20 tick 买入路径 trades_count=预期手数"断言看是否现行成立 |
| B | run_tick docstring 承诺 raises EventDrivenEngineError，实际 MetricsError/ImplausibleBacktestError/OverfittingGateError 裸穿到 strategy_runner（其只捕 EventDrivenEngineError，strategy_runner.py:226） | event_driven_engine.py:211-212,313-317,357-373；strategy_runner.py:226-227 | P2 | 空数据 provider 触发 MetricsError 路径，看 strategy_runner 是否漏捕 |
| B | provider 鸭子类型无任何能力校验（无 fetch_historical 属性时 run 中途 AttributeError 而非入口 fail-fast） | event_driven_engine.py:222-228,301 | P3 | 传 `provider=object()` 跑 run_tick 看报错形态 |
| C | BacktestResult.sharpe/annual_return 消费方（CTR-P1-016 策略遴选"sharpe>阈值入池"）拿到的是轴A发现所述错量纲值——错值带病传播到遴选决策 | engine_base.py:73,82（契约）；strategy_runner.py:212-228 | P1（同轴A爆炸半径） | 读 CTR-P1-016 契约文本 + strategy_runner 返回值去向 |
| C | 引擎桥接方法 run_walk_forward_analysis/detect_overfitting/evaluate_decision_gate/wf_fold_to_gate_dict 生产调用方=0（grep 全仓）——"W3 治本消除零调用方"声明未达成 | event_driven_engine.py:392-528；grep run_walk_forward_analysis src/ 仅自身 | P3 | `grep -rn run_walk_forward_analysis src/` |
| D | **与 vectorized_engine 逐行重复 4 个方法**（run_walk_forward_analysis/detect_overfitting/evaluate_decision_gate/wf_fold_to_gate_dict，~140 行双份承载）——改一处必漏另一处（pattern #4） | event_driven_engine.py:392-528 vs vectorized_engine.py:609-739 | P2 | diff 两文件同名方法体 |
| E | 撮合失败/fill 应用失败 `except` 吞 + **debug 级**日志（:279,:288）：系统性现金不足=整段静默无成交，仅 trades=0 被 sanity guard 兜住；部分失败（部分标的拒单）无任何显影。对照 vectorized 已整改的 warning+计数+原因分类（vectorized_engine.py:341-370, H4-D）——同缺陷两引擎整改不对称 | event_driven_engine.py:277-288 vs vectorized_engine.py:338-370 | P2 | 断点/日志级别调 DEBUG 看现金不足场景是否只有 debug 行 |
| E | strategy_callback 异常 error 日志后 continue（:261-263）：策略特定形态 bug（如某类 tick 抛异常）→ 无声跳过，统计计数不区分 | event_driven_engine.py:259-263 | P2 | callback 按 tick 奇偶抛异常，核对回测结果无异常痕迹 |
| E | 回放数据全量预载内存（tick_replay.py:332 to_dict records）——单日做T设计内 OK，跨日/多标的 OOM 面 | tick_replay.py:296-333 | P3 | 评估一年 5 档 tick 行数量级 |
| A(亮点) | PIT 结构性保障：callback 只接收当前 TickEvent，引擎不暴露未来 tick 访问通道；同 tick 成交已在模块 docstring 声明为设计语义（:45-48），非前视 | event_driven_engine.py:44-48,236-291 | — | — |
| A(亮点) | sanity_guard 默认开且 duck-typed 兜底、结果附 map_snapshot（PB-06） | event_driven_engine.py:354-365 | — | — |

## 3 SOTA 对照

- 事件驱动回测架构：**对等已有**——NautilusTrader（nautilustrader.io，2026 仍活跃）同为事件循环+委托撮合引擎，结构同构；差异：Nautilus 有确定性消息排序与延迟建模，本引擎同 tick 零延迟成交是声明过的设计取舍（对 tick 级做T可辩护，见 docstring :45-48）。（来源：NautilusTrader 官网 https://nautilustrader.io/ ；Implementation Risk in Portfolio Backtesting, arXiv:2603.20319, 2026——该文指认回测引擎实现细节是收益失真独立来源，与本报告轴A发现同族）
- 指标年化：**立卡候选**——per-tick NAV 年化须按实际采样频率换算 periods_per_year（或重采样到日频再算），VectorBT/Nautilus 均按 bar 频率显式传 annualization 参数；本引擎 252 硬默认是缺口。（来源：The Python Backtesting Landscape, python.financial, 2026；vectorbt Tutorial, quantt.co.uk, 2026）
- 同 tick 成交+5 档逐档消化容量模型：**对等已有**（限价簿逐档 walk 是 SimTradeLab/PTrade 类 A 股事件驱动框架常规做法；来源：github.com/topics/backtesting-engine，2026）。

## 4 缺陷清单

1. **[P1] tick 频 NAV×日频年化=指标全错**（含 DSR/win_rate）。现状→证据→影响：per-tick NAV 进 calculate_full_metrics(252)，实证 sharpe=-214847/annual_return=0.06%量纲爆炸；遴选/门控（SIM-56 读 overfitting_flag、DecisionGate 读 sharpe）全在此错地基上。建议修法：run_tick 内先重采样 nav_series 到日频（或传 periods_per_year=实际采样频率换算值）再算指标；win_rate 语义注明 tick 级。验证法：§2 轴A 验证法。
2. **[P1] T+1 锁定 tick 级失效**（根因 portfolio.py:268，两引擎共享真源）。影响：A股当日买入当日卖在回测可行→做T虚高+实盘拒单（"回测=实盘一致性"声明的真破口）。建议修法：比较日历日（`pd.Timestamp(fill.date).date()` 同款归一，portfolio.py:73 已有 `_ledger_date_key` 先例）；补 tick 级 T+1 回归测试。验证法：REPRO-1 两行构造。
3. **[P2] 撮合/成交失败 debug 级吞没，与 vectorized 的 H4-D 整改不对称**。建议修法：对齐 warning+skipped 计数+原因分类透传产物。验证法：现金不足场景查日志级别。
4. **[P2] 异常契约不实**（MetricsError 等裸穿）。建议修法：run_tick 统一 wrap EventDrivenEngineError（保留 error_code 链）。验证法：空 provider 触达。
5. **[P2] 四个桥接方法与 vectorized 双份承载且零调用方**。建议修法：提公共 mixin 或删（规范预算净零）。验证法：grep 调用方+diff。
6. **[P3] enforce_result_plausibility 在 `_results.append` 之后**（:340 vs :357）——raise 后进程内残留脏结果；`_to_datetime` 解析失败静默回 `now()`（:544）污染 start/end_date。验证法：读代码序。

## 5 挂起疑问

- 同 tick 成交+CH 1 档降级（B07）组合后，tick 撮合容量=单档 ask_vol_1：QMT 时代回测与 CH 时代回测同策略成交率不可比——需要 Owner 裁定是否按数据源分域披露。
- 策略回调返回的 target_weights 对多标的时仅当前 symbol 有 tick 数据（:274）——多标的 tick 回测实际是"逐标的独立撮合"语义，是否为有意设计待确认。

## 6 完备性自评

六轴全查。长尾：①test_matching_logic.py/test_matching_engine.py 逐断言审归 B03；②真实 QMT/CH tick 数据画像缺（无真机）；③strategy_runner 侧回调包装层（build_weight_panel→tick 频映射）未逐行审（归 pf_core 对象）；④run_tick 的 5 秒聚合 K 线路径（sequence=-1）仅审跳过逻辑，聚合 K 线本身未被任何引擎消费（死路径嫌疑，归 B06 复核）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
