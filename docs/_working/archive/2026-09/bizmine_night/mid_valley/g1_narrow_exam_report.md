---
ttl: task_bound
rule_form: data
verifiability: manual
title: MID 三独立卡 G1 窄测执行报告（W2-T3，st-final3-20260919）——3×RED，无卡进 G2
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-final3-20260919
prereg: prereg_card_mid_valley_top10.md（既有冻结卡，本执行零改卡）
results: g1_narrow_exam_results.csv（全字段含 BH-FDR）
---

# MID 三独立卡 G1 窄测执行报告（W2-T3 E4 收口批次·组①）

> **一句话**：缺口ATR分级/二进三断板/UTAD 三卡按冻结卡 G1 门槛（MID 桶日净 Sharpe≥1.4 且 uplift≥1.5）全数 **RED**——缺口ATR 分级有效成组合但净 Sharpe 深负（MID 桶 -1.061/全窗 -1.189）；二进三断板与 UTAD 在卡面「top 10% 多头」构架下为**空仓退化**（0 膨胀稀疏因子并列值吃掉 rank 选择）。G1 未过 → G2 E4/G3 DSR 按级联前置**不跑**，E4 未过的唯一后路=新卡另预注册。

## 1. 执行口径（照冻结卡 §0，实现级注记）

- 因子实现零重定义：直接调用 F 车道管线 `.runtime/tmp/bizmine/f/f2_run.py` 的 `build_price_factors`（与二筛同源同码）。
- 数据：`c1_market.kline_daily`（market_type='A_share'），2018-01-02..2025-08-29（1,860 日×5,518 只；缓存 2014-2024+增量 2024-03 起拼接，接缝日 2024-02-29 重叠已按增量值去重）；`c3_fundamental.ex_dividend_event` 36,305 事件；状态轴=`c1_backtest.regime_state_anchored.vol_pct`（去重后零冲突日，T-1 PIT，MID 桶=(0.3200,0.7040]）。
- 构造：信号 T 收盘→T+1 收盘成交→T+2 收益日；score=signal_dir_mid×因子值；截面 top 10% 等权（rank='average'，并列值整体进/出）；仅 MID 桶日持仓；历史≥120td+信号日未停牌+信号日或收益日(+2)除权即不形成；截面<300 不建仓。
- 成本（引擎现行口径）：佣金万 0.854 双边+卖出印花万 5+滑点 ADV 五分位（7.24/5.69/4.67/4.00/2.34bp/边，标定真源冻结表，ADV=截至信号日 20 日均额）双边计入；¥5 地板未逐笔建模（etft0_screen/pattern_narrow_exam 战役先例同法，等权 top10% 在 ≥3000 万名义下单票佣金>¥5 不绑定）。
- 考窗：2024-01-01..2025-08-31（403 交易日，MID 桶日 117）。

## 2. 结果（全部 RED）

| 卡 | 因子 | dir | MID 桶净 Sharpe | 全窗净 Sharpe | uplift | 毛Sharpe | 日均持仓 | 单边年换手 | 成本bp/日 | G1 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| midval-08 缺口ATR分级 | f_te073_gap_atr | +1 | **-1.061** | **-1.189** | 0.892 | -0.518 | 153.0 | 0.25 | 4.35 | **RED**（双门均未达） |
| midval-02 二进三断板 | f_mom017_limit_streak | -1 | n/a（空仓） | 0.000 | n/a | 0.000 | 0.0 | 0 | 0 | **RED（构造退化）** |
| midval-09 UTAD | f_te082_neg_upthrust | +1 | n/a（空仓） | 0.000 | n/a | 0.000 | 0.0 | 0 | 0 | **RED（构造退化）** |

- 多重检验（BH-FDR q=0.10，与 F 池 20 条合并 23 检验）：三卡 p_adj=0.75/0.937/0.75，**零幸存**（弱口径 t 近似亦无幸存，结论稳健）。

## 3. 诚实披露

1. **缺口ATR分级=实质 RED**：卡面 H1（跳空正向漂移）在 2024-01..2025-08 考窗不成立——top 10% 高跳空组合毛 Sharpe 即为负（-0.518），成本后放大至 -1.189。MID 条件化（uplift 0.892）反而略好于全窗，但两者同为深负。
2. **二进三断板/UTAD=构架级退化，不是因子有效性的证据**：两者为 0 膨胀稀疏因子（连板数/UTAD 事件的非事件侧占 ~95% 且同值并列），rank='average' 下并列 0 值组的平均秩 ~2,400 远超 n_top≈500 → 每日 0 持仓。IC 筛选层（全截面秩相关）与 top-10% 多头组合层对稀疏因子**不可通约**——本批如实登记「卡面 G1 构架对卡 2/卡 9 不可考」；若 Owner 认为值得继续，唯一后路=**新卡另预注册**（改事件研究法或含空头腿/规避腿构架），禁在本卡下换构架重跑。
3. **复权暂定**：kline_daily.adj_factor 恒 1，本报告全部数值=**暂定**，复权链修复后复核；缓解=除权邻域剔除。
4. 成本双口径：本报告=引擎现行；E4 冻结土规（2.5/10/5）口径本轮未启用（无卡进 G2）。
5. ST/退市未剔除（继承筛选口径局限）；涨跌停可成交性闸本构架未建模（E4 引擎闸本轮未启用）。
6. 输入绑定声明：data/strategy_intake 当日 10:00 起被工厂车道（E1D-20260919-100005）占用（20+3 行未提交追加）——本批**未写 intake**，登记与产物走 docs 侧册（冻结卡 G2 前置「经 E2 预审并登记 intake」本就归属 W2.3 收口，本批未触发）。

## 4. 级联状态

- G1 全 RED → G2 E4 正考 0 卡进入 → G3 DSR 未触发（N_eff≈4 冻结值未消费）。
- 产物：本报告+`g1_narrow_exam_results.csv`（15 字段全量入册，含 RED）；中间件 `.runtime/tmp/bizmine/w2t3/`（data.pkl/factors.pkl/narrow_mid.csv/nets/wts）。

> 合规声明：研究方法与工程产出，不构成投资建议。
