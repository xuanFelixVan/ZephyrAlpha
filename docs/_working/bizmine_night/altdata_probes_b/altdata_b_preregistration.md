---
ttl: task_bound
---

# 另类数据剩余面探针 B · 预注册（st-bizmine-altb-20260919）

> 冻结时间：2026-09-19（覆盖查证完成后、任何 IC 计算前）。本文件冻结信号定义/窗口/分桶边界；计算脚本零参数改动执行。探针≠考试：本册全部结论为筛查级，top 升「待考池」走正式预注册卡。

## 1. 数据面（只读查证于冻结前完成）

| 表 | 行数 | 覆盖 | 粒度 |
|----|------|------|------|
| c1_market.auction_book | 2,675,173 | 2026-07-21..09-16，全快照日 17 天（nts≥600） | 逐票逐快照，末日快照=09:25:0x 集合竞价撮合 |
| c1_market.news_sentiment_window | 19,811 | 2026-02-24..09-14，scope=symbol 的 night 窗 19,635 行 | 个股×日（隔夜新闻窗），sentiment_index∈[-0.6,0.8] |
| c3_fundamental.research_report | 146,669 | 2017-01-02..2026-09-13，4,701 标的/116 机构 | 逐篇元数据（评级/EPS FY0-FY2）；**全文未搬（20GB），只能元数据级** |
| c1_market.stock_hot_rank | 5,993 | 2026-08-04..09-18，29 天，hot_rank=每日 top100 | 逐票逐日排名；hot_value 全空 → 只能用 rank |
| c1_market.limit_up_down | 4,787 | 2026-07-20..09-17，44 天 | 涨停 3,832 / 跌停 955 逐票逐日 |
| c1_market.weather_data | 9,073 | 2026-08-04..09-18，仅 31 个记录日、40 城 | **样本不足，不做 IC，仅登记缺口** |
| c1_market.alt_shipping_index | 27,186 | BDI 1988-10..2026-09-18（日更），BCI/BDTI/BCTI 2006+ | 逐指数逐日 |
| c1_market.cftc_positioning | 81,270 | 1986-01..2026-09-08，goods 12 市场+currency 9 市场，周度 | 逐市场逐周（non_commercial/commercial） |
| c1_market.agri_wholesale_index | 11,638 | AJC200/CLZ200 2005-09..2026-09-18 | 逐指数逐日 |

## 2. 统一协议（冻结）

- IC 口径：Spearman 秩相关。横截面面板=日度横截面 IC 序列；宏观面=**时序 IC**（信号序列 vs 000300 前瞻收益，非横截面，结论只对该时序口径负责）。
- 窗口：长历史面（research/宏观）IS=2019-01-01..2023-12-31 排名，OOS=2024-01-01..2026-09 报告档；短样本面（auction/news/hot/limit）**全窗计算并强制标注功效低**（n_days<200，t 检验仅供参考）。
- 前瞻收益：`c1_market.kline_daily`（A_share）。横截面 fwd_h = close[t+h]/close[t]-1；auction 另有「竞价后当日」= close/竞价末次快照 last_price - 1。已知 kline_daily.adj_factor 恒 1（未复权）→ **一切日线结论待复权链修复后复核**。
- PIT：auction vratio 的分母=过去 20 交易日 kline 日均成交量（仅 t 前数据）；news 用 night 窗（t 日晨发布，交易于 t 日及以后→对 T+1 及更长前瞻无前视；对「竞价后当日」前瞻不适用，news 只配 T+1/T+5）；CFTC 周报 report_date+4 自然日后才可用；BDI 当日 10am 发布→信号 shift 1 交易日（保守）。
- regime 条件版：`c1_backtest.regime_state_anchored.vol_pct`（plain MergeTree，无 FINAL；同日多行取 argMax(vol_pct, ingest_ts)），T-1 PIT（交易日 t 用 signal_date<t 最近值），边界 vol_pct<0.3200=low / ≤0.7040=mid / >0.7040=high。**冻结前已探明：2026-07..09 样本期 vol_pct≈1.0 全落 high 桶 → 面板 1-3 的 regime 条件版退化为单桶，如实报告桶构成不做跨桶比较**；宏观面（长历史）做三分桶条件 IC。
- 多重检验：本探针共 4 面板×约 20 信号×前瞻档，全部结果（含零/负）入 `altdata_b_results.csv`，不隐藏；筛选结论仅为待考池提名。
- 横截面最小样本：auction 每日 ≥1,000 票、hot ≥40 票、news ≥20 票、limit ≥20 票，低于则该日记 NaN。

## 3. 信号定义（冻结）

**面板1 集合竞价（17 全快照日，全窗=功效低）**
- `auc_gap` = 竞价末次快照 last_price/pre_close - 1
- `auc_vratio` = 竞价快照 volume / 过去 20 交易日日均 kline volume（ln(1+x) 后入 IC）
- `auc_imb` = (Σbid_vol1-5 − Σask_vol1-5)/(Σbid+Σask)（末次快照）
- 前瞻：`eod`（竞价价→当日 close）、`t1`（close→T+1 close）
- 强弱分档：每票按 auc_gap 五分位分档 → 各档平均前瞻收益表（描述性）

**面板2 新闻+研报**
- `news_sent`（sentiment_index）、`news_buzz`（ln(1+total_count)）→ 前瞻 T+1、T+5
- `rpt_cov_chg` = ln(1+近20日报告数) − ln(1+前20日报告数)（月滚动，日频取值）
- `rpt_rating` = 近20日报告评级均分（买入5/增持4/持有3/中性2/减持1/卖出·回避0/空→NaN）
- `rpt_eps_rev` = (近20日 eps_fy1 均值 − 之前40日均值) / |之前40日均值|（分母<0.01 记 NaN）
- 前瞻 5/10/20 日；IS 2019-2023 / OOS 2024+

**面板3 热度+涨跌停（全窗=功效低）**
- `hot_rankchg` = rank[t-1] − rank[t]（正=升温，仅两日均上榜的交集票）
- `lianban_h` = 连续涨停天数（按 limit_up_down 涨停行连续交易日计数，断档归 1）；跌停同理 `lianban_d`
- 前瞻 T+1 close-close

**面板4 宏观择时（时序 IC，全历史，IS/OOS 分档）**
- `bdi_mom20` = ln(BDI_t/BDI_{t-20})；`bdi_z60` = 60 日 z 分；`bdti_mom20` 同 bdi；`agri_mom20` = ln(AJC200_t/AJC200_{t-20})（食品通胀动量）
- `cftc_goods_net_chg8w` = goods 12 市场 non_commercial 净头寸合计，最新报告 vs 8 周前，除以 8 周前绝对值（周度→交易日 ffill）
- 前瞻：000300 close→close 5/10/20 日
- 开关回测：`bdi_mom20>0` 持有 000300 否则空仓（次日收益计，无成本——指数不可直接交易，口径声明）；对比买入持有

## 4. 判读门槛（待考池提名线，冻结）

- 长历史面：IS |IC_mean|≥0.02 且 IC_IR≥0.3，且 OOS 同号 → 提名
- 短样本面：仅记录，不提名（功效不足）；若 |IC_mean|≥0.05 且同号日占比≥60% → 标记「待扩样本观察」
- 时序面：IS IC 同上，另需开关回测 IS Sharpe>买入持有 Sharpe
