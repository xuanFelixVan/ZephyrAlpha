---
ttl: task_bound
rule_form: data
verifiability: manual
title: MID 洼地 top-10 候选预注册卡（10 卡合册，考试门槛 frozen，st-bizmine-mid-20260919）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（卡片在考试执行前写死；启动后任何字段不得改动，改动即作废重开）
lane: bizmine W2.4（MID 洼地深挖）
family_id: MIDVAL-20260919-TOP10
n_eff: 10（名义；同源族合并后有效独立族≈4，见 §0 同源声明）
parent_context: >
  prereg_card_mid_valley_screen.md（二筛协议卡，先于跑数钉死）
  + mid_valley_top10.csv（排序依据）
  + docs/_working/kimi_audit/lane_reports/p3_prereg/P3-E1C-09.md（卡面与门槛格式模板）
---

# MID 洼地 top-10 候选预注册卡（合册）

## 0. 全卡共用水准（每卡同文引用，禁逐卡挪改）

- **因子实现**：全部沿用 F 车道 f2 管线实现（`.runtime/tmp/bizmine/f/f2_run.py`，与 screen_results.csv 同源同码），本批零重定义。
- **数据列**：`c1_market.kline_daily`（open/high/low/close/volume/amount/turnover/pct_change，market_type='A_share'，2014-01-01..2024-02-29）；基本面卡另用 `c3_fundamental.financial_indicator`（announce_date PIT）。经 DatabaseService 只读。
- **宇宙**：全 A；标的须 ≥120 交易日历史 + 当日未停牌（volume>0）；日度截面有效宽度 ≥300；样本 (t, t+h] 窗内命中 `c3_fundamental.ex_dividend_event` 除权除息/送转/配股/股改事件者剔除。
- **MID 桶判定规则（冻结）**：状态=`c1_backtest.regime_state_anchored.vol_pct`（hv20 滚动 250 日分位），`SELECT DISTINCT trade_date, vol_pct` 去重；T-1 交易日 PIT（严格早于收益日 t 的最近状态日，禁当日值落桶）；**MID 桶 = 0.3200 < vol_pct ≤ 0.7040**（边界沿用 R 车道预注册卡 §3 冻结值，IS=2017-07-11..2023-12-29 分位）。
- **IS 筛选证据**：2019-01-01..2023-12-31；IC=日度横截面 Spearman 秩 IC；各卡「证据」列=h=10 MID 桶统计量（二筛实测，见 mid_valley_top10.csv）。
- **考试门槛（G1/G2/G3，写死）**：
  - **G1 窄测（MID 条件化组合窄测）**：因子值按建成方向（signal_dir_mid 列：+1=因子值高看多，-1=因子值高看空）截面 top 10% 等权多头，**仅 MID 桶日持仓**（T-1 vol_pct 落桶），T 收盘信号→T+1 收盘成交；成本=引擎现行（佣金万 0.854 双向 + ¥5 地板 + 卖出印花税万 5 + 滑点五分位 Q1-Q5，`matching_logic.py:69-76`）；考窗=2024-01-01..2025-08-31（禁用 IS 数据选参）。**G1-PASS：MID 桶日净 Sharpe ≥ 1.4 且 MID 桶净 Sharpe / 全窗净 Sharpe ≥ 1.5**（弹药账 @H2 需求 + 状态专属门）。
  - **G2 E4 正考**：`scripts/backtest/f06_e4_wfa_exam.py` 通道，先例参数（P3-E1C-09 → E4 先例）：train 24m / test 6m / step 6m，OOS 起点 2024-01，阈值比按引擎常量；前置=组合规则经 E2 幂等预审并登记 `data/strategy_intake`（该目录本车道禁碰，W2.3 收口执行）。
  - **G3 DSR**：精确 DSR > 0.5（MOD-SIM-024 官方件），N_eff=10（封闭族=本批 10 卡）；**同源族内多条同考时按族合并缩减 N_eff**（见 §0 同源声明），不得按 10 充数。
- **同源声明（先钉死，防「10 条=10 份证据」幻觉）**：top-10 按 IS 日度 IC 序列 Pearson |ρ|≥0.7 归族——**量能反转族**（#1 历史天量 ↔ #3 地量，|ρ|=0.932）、**波动率压缩族**（#4 ATR14 ↔ #7 布林收口，|ρ|=0.935）、**趋势反转族**（#10 MA20 斜率 ↔ #5 假突破 0.751 ↔ #6 下方缺口 0.704，且与 HIGH 强候选 MACD 零轴 |ρ|=0.947）、**相对独立组**（#2 二进三断板 0.468 / #8 缺口ATR分级 0.149 / #9 UTAD 0.666）。族内任一条 PASS 只记族代表一次；三条相对独立条目是本批信息量最高的考试对象。
- **复权暂定标注（全卡适用）**：`kline_daily.adj_factor` 恒 1（回测日线路径未复权），本册全部证据与未来考试结论=**暂定**，复权链修复后全量复核；已做缓解=除权事件窗剔除。

---

## 卡 1 FCT-TECH-059 历史天量（midval-01）

- **H1（唯一）**：量/250 日最大量比在 MID 灰度桶（0.3200<vol_pct≤0.7040，T-1 PIT）内具有负向预测力——天量=顶部，天量日后的 MID 桶持仓被显著拖累；按该信号做 MID 条件化规避/空头组合可过 G1 门槛。
- **因子定义**：`f_te059_hist_volspike = volume / rolling_max(volume, 250)`；signal_dir_mid=-1（天量看空）。
- **筛选证据**：MID 桶 h10 IC=-0.078（IR=-0.629，t=-12.6，n=402 IC 日，pct_pos=0.254）；h5/h20 同号；contrast(总体)=0.830。
- **同源标注**：与 #3 地量 |ρ|=0.932 同族（量能反转族，一体两面）；与 HIGH 强候选同源（|ρ|≥0.7）。
- **门槛**：G1/G2/G3 全卡共用；族代表优先级=本族第 1（MID |IR| 最高）。

## 卡 2 FCT-MOM-017 二进三断板（midval-02）

- **H1**：连板高度计数（pct_change≥9.8% 近似涨停，口径局限登记）在 MID 桶内负向——高位接力衰减；连板高度越高，后续 MID 桶收益越差。
- **因子定义**：`f_mom017_limit_streak` = 连续涨停天数计数；signal_dir_mid=-1（高连板看空）。
- **筛选证据**：MID 桶 h10 IC=-0.061（IR=-0.612，t=-12.3，n=406，pct_pos=0.254）；三档同号；contrast=0.915。
- **同源标注**：与 HIGH 强候选最大 |ρ|=0.468，**本批相对独立条目之一**；与 top-10 内部最大 |ρ|=0.468（历史天量）。
- **口径局限**：未分 10/20cm 板；正式考试前如获精确涨停标记须重申卡（不改本卡结论判定）。

## 卡 3 FCT-LIQ-025 地量（midval-03）

- **H1**：`-(volume/rolling_max(volume,120))` 在 MID 桶内正向——地量=抛压衰竭。
- **因子定义**：`f_liq025_neg_diliang`；signal_dir_mid=+1（地量看多）。
- **筛选证据**：MID 桶 h10 IC=+0.072（IR=+0.516，t=+10.4，n=406，pct_pos=0.700）；三档同号；contrast=0.859。
- **同源标注**：与 #1 历史天量 |ρ|=0.932 同族（量能反转族反面）；与 HIGH 强候选同源（|ρ|≥0.7）。族内代表=#1。

## 卡 4 FCT-TECH-064 ATR14（midval-04）

- **H1**：`ATR14/close` 在 MID 桶内负向（低波异象在中间灰度延续）。
- **因子定义**：`f_te064_natr14 = mean(TR,14)/close`；signal_dir_mid=-1（高波动看空）。
- **筛选证据**：MID 桶 h10 IC=-0.060（IR=-0.470，t=-9.5，n=406，pct_pos=0.328）；三档同号；contrast=0.844。
- **同源标注**：与 #7 布林收口 |ρ|=0.935 同族（波动率压缩族）；与 HIGH 强候选同源（|ρ|≥0.7）。族代表优先级=本族第 1。

## 卡 5 FCT-TECH-083 假突破统计（midval-05）

- **H1**：10 日内假突破计数（破 20 日高+量>1.5×5 日均量，随后收盘跌回突破位下方）在 MID 桶内负向（假突破多→后续弱）。
- **因子定义**：`f_te083_neg_fakebreak10`（已取负号建成）；signal_dir_mid=+1（因子值高=假突破多=看空）。
- **筛选证据**：MID 桶 h10 IC=+0.030（IR=+0.422，t=+8.5，n=406，pct_pos=0.675）；三档同号；contrast=1.057（MID 桶略强于总体，本批最高 contrast 之一）。
- **同源标注**：与 HIGH 强候选 |ρ|=0.719（过 0.7 线，标注）；与 MA20 斜率 |ρ|=0.751（趋势反转族边缘）。

## 卡 6 FCT-TECH-078 下方缺口不回补（midval-06）

- **H1**：20 日内未回补向上缺口计数在 MID 桶内负向（未回补缺口越多→均值回归压力越大）。
- **因子定义**：`f_te078_unfilled_upgap20`；signal_dir_mid=-1。
- **筛选证据**：MID 桶 h10 IC=-0.057（IR=-0.420，t=-8.5，n=406，pct_pos=0.323）；三档同号；contrast=0.884。
- **同源标注**：与 HIGH 强候选 MACD 零轴 |ρ|=0.716（过线，标注）；与 MA20 斜率 |ρ|=0.704。

## 卡 7 FCT-TECH-072 布林收口（midval-07）

- **H1**：`-4×std20/MA20`（布林带宽负值）在 MID 桶内正向——低带宽压缩→变盘上行。
- **因子定义**：`f_te072_neg_bollbw`；signal_dir_mid=+1。
- **筛选证据**：MID 桶 h10 IC=+0.069（IR=+0.418，t=+8.4，n=406，pct_pos=0.680）；三档同号；contrast=0.856。
- **同源标注**：与 #4 ATR14 |ρ|=0.935 同族（波动率压缩族）；与 HIGH 强候选同源。族代表=#4。

## 卡 8 FCT-TECH-073 缺口ATR分级（midval-08）

- **H1**：`(open-昨收)/ATR14`（ATR 标准化跳空）在 MID 桶内正向——跳空方向漂移延续。
- **因子定义**：`f_te073_gap_atr`；signal_dir_mid=+1。
- **筛选证据**：MID 桶 h10 IC=+0.041（IR=+0.415，t=+8.4，n=406，pct_pos=0.680）；三档同号；contrast=0.971。
- **同源标注**：与 HIGH 强候选最大 |ρ|=0.149、top-10 内部最大 |ρ|=0.156——**本批最独立条目**。

## 卡 9 FCT-TECH-082 Wyckoff派发UTAD（midval-09）

- **H1**：破 60 日高后收回下方（UTAD 0/1，已取负建成）在 MID 桶内正向——冲高回落派发→后续弱。
- **因子定义**：`f_te082_neg_upthrust = -UTAD_indicator`；signal_dir_mid=+1。
- **筛选证据**：MID 桶 h10 IC=+0.020（IR=+0.374，t=+7.5，n=406，pct_pos=0.687）；三档同号；contrast=0.881。
- **同源标注**：与 HIGH 强候选最大 |ρ|=0.666（未过 0.7 线）；0/1 稀疏事件因子，IC 功效受事件率限制，卡面如实标注。

## 卡 10 FCT-TECH-055 20日均线趋势判定（midval-10）

- **H1**：`MA20 5 日斜率`在 MID 桶内负向（A 股中期反转结构：趋势斜率高→后续回调）。
- **因子定义**：`f_te055_ma20_slope = ma(ma20,5)/ma20.shift(5)-1`；signal_dir_mid=-1。
- **筛选证据**：MID 桶 h10 IC=-0.035（IR=-0.355，t=-7.1，n=406，pct_pos=0.370）；三档同号；**contrast=1.124（top-10 内最高）**——MID 桶效应强于其总体平均，形态上最接近「状态倾斜」但未达总体平庸门（总体 |t|=10.4>2，不标 MID 专属）。
- **同源标注**：与 HIGH 强候选 MACD 零轴 |ρ|=0.947、与假突破 0.751、与下方缺口 0.704——趋势反转族核心。

---

## 附：卡面生成依据与禁改

- 卡面证据全部来自二筛实测（`mid_valley_top10.csv`，协议卡先于跑数钉死）；卡在考试执行前 frozen，G1/G2/G3 门槛、宇宙、MID 桶规则、同源归族启动后不得改动——改动即作废重开新卡。
- 本册是**待考池**，不是 PASS 结论；筛≠考（历史前科：宽测好看窄测大面积衰减）。
