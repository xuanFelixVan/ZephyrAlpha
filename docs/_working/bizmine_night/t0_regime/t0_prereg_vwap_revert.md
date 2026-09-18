---
ttl: task_bound
rule_form: data
verifiability: manual
title: T0 预注册卡 T0-PRERG-01——510300 日内 VWAP 负偏离回归做T（M1+M4，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（判据冻结于任何考试运行之前；本役不跑数，跑数前须另登记 trial ledger 并 Owner 快签）
lane: T
family_id: T0-PRERG
n_eff: 1
parent_context: t0_subjective_methods.md M1/M4 + t0_conversion_table.md §3-M1 + S2_做T_v2_战役裁定书.md §3（成本线）+ T.md（前役 RED 基线）
---

# T0-PRERG-01：510300 日内 VWAP 负偏离回归信号有正毛边际？

## 1. 假设（H1，唯一）

**在 510300 上，日内价格显著低于当日累计 VWAP（分时黄线）并短暂企稳后买入、回归 VWAP 或日终平仓的做T信号（正T/分时均线偏离族），单笔毛边际 > 12bp/边（Q5 口径）。**

零假设 H0：毛边际均值 ≤ 12bp/边，或不优于"每日首 bar 无条件出手"对照组。

机制自述（关③）：日内流动性冲击把价格砸离 VWAP 后，收盘前的被动盘与套利回补驱动价格向 VWAP 回归（intraday mean reversion，模型知识，未引证——本机制声明为待证机制而非依据）。

## 2. 信号与执行口径（冻结）

- 标的/数据：`c1_market.kline_etf_1min`，symbol='510300'；样本=表内全部可用日（地形实测 2019-01-02→2026-09-18，1,873 日）；(symbol,trade_time) 去重保留 ingest_ts 最新。
- VWAP：当日累计 `sum(amount)/sum(volume)`（1min 逐 bar 递推，只用当日 ≤t 数据）。
- 信号（bar t 收盘判定）：`close_t < vwap_t × (1 − 0.003)` **且** `close_{t−4..t} 全部 < vwap_{t−4..t} × (1 − 0.003)`（5 根持续，防单 bar 假信号）。
- 入场：bar t+1 开盘价买入（滚动仓，≤前收持仓 1/3；本测算只量单腿价差，T+1 额度框架由 S-OWNER-001 承担）。
- 出场：`close ≥ vwap` 首根 bar 收盘卖出；或 14:55 bar 收盘强制平仓（先到先平）。不隔夜。
- 止损：入场价 ×0.992 触及即平。
- 约束：每日至多 1 笔；14:50 后不新开。
- 对照组：每交易日首根可交易 bar（09:31）无条件同规则进出（无 VWAP 过滤），同止损/强平。

## 3. 及格/判红判据（冻结）

| 关 | 判据 | 门槛 |
|---|---|---|
| ① 毛边际 | 全样本单笔毛边际均值（Q5 口径参考线 8.4bp） | **> 12bp/边** |
| ② 对照差 | 信号组 − 对照组差值（单侧 Welch） | **p < 0.05** |
| ③ 样本量 | 成交笔数 | **≥ 200**（1min 级信号应高频，低于此=信号定义失效） |

任一不满足=红。三关全绿方可进 N 账本登记+Owner 快签流程。Owner-001 口径（6.71bp 往返）仅作并行披露，不作为判据。

## 4. 成本与披露（冻结）

- 主口径：引擎现行 Q5 往返 8.4bp（100k：佣金 0.854×2+滑点 2.34×2+加成 1×2，ETF 免印花，matching_logic.py:69-76/cost_model_calibration.py:229-235）；12bp 门=8.4+3.6 安全边际。
- 并行披露：Owner-001 滑点 1.5bp 档往返 6.71bp；ex_sor t0_cost_model.py HIGH_LIQUIDITY 10bp/边（个股口径，参考）。
- 多重检验披露：本卡属 T0-PRERG 封闭族 N_eff=1；若 M2 镜像/其他手法后续开卡，族计数随之 +1 并重算 DSR 门。

## 5. PIT 与纪律

- 信号只用当日 ≤t 的 1min 数据；无日线/横截面引用；无未来函数。
- 本卡冻结后任何阈值/口径改动=作废重开新卡；考试结果无论红绿全量入册。
- 本役（2026-09-19 通宵战）**不执行**本考试：判据先冻结、跑数须排期（防通宵战无监督跑批+族膨胀）。
