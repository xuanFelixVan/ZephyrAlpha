---
ttl: task_bound
rule_form: data
verifiability: manual
title: F 车道 top-20 待考池窄考+正考预注册卡（W2-T3 E4 收口批次，st-final3-20260919）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（本卡在考试执行前写死；启动后任何字段不得改动，改动即作废重开）
lane: bizmine W2-T3（E4 正考收口批次·组③）
family_id: FPOOL-20260919-TOP20
n_eff: 6（封闭族=本池 20 条按 IS IC 序列 |ρ|≥0.7 单链聚类，见 §3；禁按 20 充数）
parent_context: >
  factor_sop_screen/screen_report.md（F2 v2 筛选报告，top-20 待考池真源）
  + .runtime/tmp/bizmine/f/f2_top20_pool.csv（池清单，只读）
  + .runtime/tmp/bizmine/mid/mid_ic_series_h10.pkl（IS h10 IC 序列，聚类输入，只读）
  + prereg_card_mid_valley_top10.md（G1/G2/G3 门槛与执行惯例模板，同战役同门槛）
---

# F 车道 top-20 待考池考试预注册卡（组③）

## 0. 池与出身

- 待考池=F2 宽表因子 IC 大海选 v2（除权掩膜修复版）top-20，按 h=10 总体 |IC_IR| 降序，三档同号门已过（screen_report.md §2）。池内无一条有 PASS 结论；筛≠考。
- 本卡冻结时点=考试执行前（考试窗尾部数据尚未取数）；冻结依据仅来自已入册筛选产物（screen_report/池 csv/IS IC 序列缓存），零考试窗信息。

## 1. 组合构造（冻结，MID 卡 G1 同法去状态门）

- **因子实现**：沿用 F 车道 f2 管线实现（`.runtime/tmp/bizmine/f/f2_run.py` build_price_factors，与 screen_results.csv 同源同码），本批零重定义；方向按池 csv `dir` 列与 MID 卡 signal_dir 同一语义换算（见 §1 注：score=建成方向×因子值，建成方向使 IS IC 为正）。
- **数据列**：`c1_market.kline_daily`（open/high/low/close/volume/amount/turnover/pct_change，market_type='A_share'）。经 DatabaseService 只读。
- **宇宙**：全 A；标的须 ≥120 交易日历史 + 信号日未停牌（volume>0）；日度截面有效宽度 <300 则当日不建仓；信号日或收益日命中 `c3_fundamental.ex_dividend_event` 者当日不形成信号（除权邻域剔除，L1 车道同法）。
- **执行口径**：T 收盘信号→T+1 收盘成交，持仓于 T+2 收益日（T+1 close→T+2 close），等权 top 10% 多头（n_top=ceil(0.1×有效宽度)）；引擎实现=w_engine(u)=w_sig(u−1)（u=成交日），与引擎 w.shift(1) 口径合成后恰为「信号 T→成交 T+1→收益 T+2」，全链路 PIT。
- **成本（引擎现行口径）**：佣金万 0.854 双边 + 卖出印花税万 5 + 滑点 ADV 五分位（Q1 7.24/Q2 5.69/Q3 4.67/Q4 4.00/Q5 2.34 bp/边；边界 46.4M/90.2M/174M/418M=cost_model_calibration 冻结表，ADV=截至信号日 trailing 20 日均成交额）双边计入。¥5 佣金地板未逐笔建模（战役先例 etft0_screen/pattern_narrow_exam 同法）；等权 top10% 在 ≥3000 万组合名义下单票佣金>¥5 地板不绑定，更小名义成本上浮，已披露。
- **考窗**：2024-01-01..2025-08-31（禁用 IS 数据选参）。

## 2. 考试门槛（写死）

- **F1 窄测**：**全窗净 Sharpe ≥ 1.4**（引擎现行成本，考窗全交易日含平仓日；战役 H2 弹药账同门）。MID 三卡 G1 门槛（Sharpe≥1.4+uplift≥1.5）按其已冻结卡执行，不因本卡改动。
- **F2 E4 正考（仅 F1 过卡进入）**：MOD-BT-211 路线（`f06_e4_wfa_exam.py` 内部件复用，判定零重写 strategy_validation_pipeline+DecisionGate+OverfittingDetector）；全窗 2020-01-01..2025-08-31，折法 train 24m/test 6m/step 6m，真 OOS=测试段起点≥2024-01-01；成本=E4 冻结土规（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp，_c4_engine），与 F1 引擎现行口径双口径并注。
- **F3 DSR**：MOD-SIM-024 精确口径，真 OOS 段收益序列，**N_eff=6**（§3 聚类）；DSR≤0.5 判不通过。
- **多重检验**：本批 23 场窄测（F 池 20+MID 卡 3）合并做 BH-FDR（q=0.10），p=单侧 t（日净收益均值 t 统计，正态近似已披露为弱口径）；BH 幸存与门槛通过是两个独立条件，均须满足才算「过卡」。

## 3. 封闭族聚类（N_eff=6，冻结）

IS 2019-2023 h10 日度 IC 序列（mid_ic_series_h10.pkl，与筛选报告同源）两两 |ρ|≥0.7 单链聚类：

| 族 | 成员 |
|---|---|
| 1（量能反转×趋势反转大簇，14 条） | 059 天量、025 地量、078 下方缺口、024 缩量、083 假突破、067 MACD、009 RS、076 高位振幅、055 MA20 斜率、062 乖离、061 均线排列、058 月线支撑、057 红多绿少、056 放量突破 |
| 2（波动率压缩） | 064 ATR14、072 布林收口 |
| 3 | 017 二进三断板（独立） |
| 4 | 073 缺口ATR分级（独立） |
| 5 | 082 UTAD（独立） |
| 6 | 031 立桩量（独立） |

- 同族多条同考只记一份证据；E4 判定层不做族合并（逐条机械判），族合并仅作用于 DSR 折减分母 N_eff 与结论解读。
- 参考（同序列复算）：MID 三独立卡两两 |ρ|=0.149/0.135/0.395 均 <0.7，互为独立；其 G3 N_eff 按其卡面与 MID 报告冻结值 ≈4 执行。

## 4. 全卡通用声明

- 复权暂定：`kline_daily.adj_factor` 恒 1，本卡全部考试结论=**暂定**，复权链修复后全量复核；缓解=除权事件邻域剔除。
- 成本双口径必注明：F1=引擎现行（万 0.854+印花 5+滑点五分位）；F2/E4=冻结土规（2.5/10/5）。
- 全部结果含 RED 入册；E4 未过唯一后路=新卡另预注册（禁原地重跑/禁改卡）。
- ST/退市未剔除（继承筛选口径局限）；涨跌停可成交性闸 F1 未建模（卡面构造为准）、E4 由引擎闸覆盖。
