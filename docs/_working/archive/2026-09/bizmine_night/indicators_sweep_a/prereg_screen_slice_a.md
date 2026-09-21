---
ttl: task_bound
rule_form: data
verifiability: manual
title: 指标库全扫切片A预注册——technical_indicator 宽表 163 因子列均分第 1 份 55 列 IC 筛（st-bizmine-inda-20260919，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-bizmine-inda-20260919
---

# 指标库全扫 · 切片A 预注册协议（执行前钉死，2026-09-19 夜）

- 本文件在跑数之前写定；执行后只许引用，不许改。任何偏离在 report.md「偏离登记」逐条列明。
- 任务：c1_market.technical_indicator 宽表因子列全扫（三并行车道均分），本车道取排序第 1 份。
- 筛协议与 F 车道（docs/_working/bizmine_night/factor_sop_screen/screen_report.md）一致；regime 轴按总包令改用全夜统一灰度轴 vol_pct。

## 1. 切片定义（钉死）

- DESCRIBE 实查：宽表共 171 列；剔除键/元列 8 个（trade_date、trade_time、symbol、period、data_source、ingest_ts、exchange、symbol_canonical），余 **163 个因子列**（全部 Nullable(Float64)，含 flag 类）。
- 163 列按列名字典序升序，numpy.array_split 均分三份：切片A=**55 列**、切片B=54、切片C=54。本车道取切片A：
  ac, ad, adosc, adx_14, alligator_jaw, alligator_lips, alligator_teeth, ao, apo, ar_26, aroon_down, aroon_up, aroonosc, atr_14, bbi, bear_power_13, beta_30, bias_12, bias_24, bias_6, boll_breakout, boll_bw, boll_lower, boll_middle, boll_pctb, boll_upper, bop, br_26, bull_power_13, candle_pattern, cci_14, chikou_span, cmf_20, cmo_14, coppock, correl_30, cr_26, crsi, dc_lower, dc_upper, dema_12, dkx_20, dkx_ma10, dpo_20, dx_14, ema_12, ema_26, eom_14, fi_13, fisher_9, fisher_sig9, fractal_high, fractal_low, gann_hilo, gann_hilo_dir

## 2. 数据与口径（钉死）

- 因子值：c1_market.technical_indicator，period='daily'（实查 2021-01-04..2026-09-18，17,564,093 行）。**IS 2019-2020 段无 TI 日频数据**（F 车道同发现），有效 IS 覆盖=2021-01..2023-12，n_days 如实报告。
- 去重（数据面修正，预注册即钉死）：plain 重复 ingest 实查 (trade_date,symbol) 重复键 429 万、重复行 1475 万，抽样核实**值完全相同**（多次全表重灌）。去重=按 (trade_date,symbol) 保留最小 ingest_ts 行；去重后若同键值冲突超抽样阈值则停机登记。
- 前瞻收益：kline_daily FINAL，close（adj_factor 恒 1 未复权）；fwd_h = close_{t+h}/close_t - 1，h∈{5,10,20}。
- 除权剔除：c3_fundamental.ex_dividend_event，(t,t+h] 内 divid/bonus/gift/allotment/gugai 任一非空即剔除该 (symbol,t,h) 样本。
- 样本过滤（同 F）：t 日 kline volume>0；标的 ≥120 交易日历史；因子值非 NaN；当日截面宽度 <300 剔除该日。
- 未做（登记为口径局限）：涨跌停不可交易剔除、ST 剔除、市值加权（等权秩相关）；TI 列值与 kline 重算的抽查校验不做（时间盒，与 F 同留缺口）。

## 3. IC 计算（钉死）

- 横截面 Spearman 秩 IC：每日因子截面秩 vs fwd_h 秩的 Pearson。IS=2019-01-01..2023-12-31（排名用，有效日=∩TI 覆盖）；OOS=2024-01-01..2026-09-18（只报告不参与排序）。
- 统计量：IC 均值、std、IC_IR=mean/std、t=IR*sqrt(n_days)、日均有效样本数、IC>0 占比。h=10 为主档。
- 方向不翻转、不筛选；flag/水平值类列（如 gann_hilo_dir、boll_upper）照常入册，非平稳性如实呈现。

## 4. regime 条件版（钉死，全夜统一灰度轴）

- 状态轴：c1_backtest.regime_state_anchored.vol_pct（plain MergeTree，SELECT DISTINCT trade_date,vol_pct 去重），T-1 PIT（对交易日 t 取 trade_date<t 最近一条）。
- 桶边界冻结（与 R/MID 车道同源）：LOW：vol_pct ≤ 0.3200；MID：0.3200 < vol_pct ≤ 0.7040；HIGH：> 0.7040。禁用 alt_regime_signal。
- 报总体 + LOW/MID/HIGH 共 4 组 IC 统计；桶内 n_days<60 标 low_power。

## 5. 先验覆盖标注（prior_coverage，钉死）

- l1_pending：L1 车道 15 组量能/统计族对应列（docs/_working/bizmine_night/volume_family_l1/prereg_family_summary.md）——本切片命中 6 列：ad、adosc、eom_14、fi_13、correl_30、beta_30。
- f_screened：F 车道 38 条已筛**同概念代理因子**（f2_mapping_used.csv used 行）——本切片命中 6 列：atr_14（←f_te064 ATR14）、boll_bw（←f_te072 布林收口）、bias_6/bias_12/bias_24（←f_te062 乖离率）、boll_pctb（←f_te068 区间位置百分位，位置类近似）。注意 F 筛的是 kline 复算代理非 TI 列值，属概念重叠非同数据源。
- 其余 43 列 none。标注仅供 Owner 合并视图，不改变本筛执行。

## 6. 多重检验与排名（钉死）

- 统计量总量 = 55 因子 × 3 前瞻 × 4 组 × 2 窗 ≈ 1320 组，假阳性结构性放大；全部结果（含 NaN/覆盖不足列）如实入册 screen_results.csv。
- 排名（唯一、预先钉死）：**IS 窗 h=10 总体 |IC_IR| 降序**，要求 h=5/10/20 三档 IS 总体 IC 均值同号（稳健门），取 top-10 升「待考池」，不足如实缺额。筛≠考，不判 PASS/FAIL。

## 7. 产出与时间盒（钉死）

- 落点 docs/_working/bizmine_night/indicators_sweep_a/：本预注册 + screen_results.csv + report.md。
- 中间缓存 .runtime/tmp/bizmine/inda/（按年 parquet 分块，禁一次全取）。
- 时间盒 08:00 收口：算不完则提交已完成部分+覆盖矩阵（实测 X/55 列），诚实标注。
- 诚实条款引用：adj_factor 恒 1，一切结论=暂定，待复权链修复后复核。

## 8. 偏离预登记 D1（2026-09-19 夜，首次拉数停机后、筛选执行前钉死）

- 事实：预注册 §2 去重条款触发停机——2021 年全行去重后同键仍多行（348 万行）。抽样核实多数键跨批次**值全同**（整表多次重灌），但存在 NaN 模式/值差异键。
- 裁定（自裁框架：第一性原理——TI 列为衍生数据、非 PIT 特征，同键多版本时最新重算版=当前表意版本，与 FINAL 语义同构）：去重规则由「保留最小 ingest_ts」改为**「全行去重 → 剩余冲突保留最大 ingest_ts（最新重算版）」**，并量化登记每年 conflict_rows/conflict_keys/value_diff_keys（cache/dedup_stats.json）。
- 本附录在筛选跑数之前写入，属预注册内数据面修正，非事后偏离；对值差异键占比若超 5% 将在报告显著披露。
