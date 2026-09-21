---
ttl: task_bound
rule_form: data
verifiability: manual
title: 指标库全扫切片B 预注册协议（TI 宽表第2等分54列 IC 筛）——执行前钉死
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-bizmine-indb-20260919
---

# 指标库全扫·切片 B 预注册协议（先落本段后取数，钉死禁改）

## 1. 切片定义（程序化生成，防手挑）

- 母体：`DESCRIBE c1_market.technical_indicator` 全部因子列，剔除键列/备份列 8 个
  （trade_date/trade_time/symbol/period/data_source/ingest_ts/exchange/symbol_canonical）后
  **163 列**，按列名升序均分三份（55/54/54）。本车道取**第 2 份**（54 列）；第 1/3 份归并行车道，勿越界。
- 切片 B 清单（54 列，字典序）：garman_klass_20, gmma_l30, gmma_l35, gmma_l40, gmma_l45,
  gmma_l50, gmma_l60, gmma_s10, gmma_s12, gmma_s15, gmma_s3, gmma_s5, gmma_s8, histvol_20,
  hma_16, ht_dcperiod, ht_dcphase, ht_ip, ht_leadsine, ht_qp, ht_sine, ht_trendmode, kama_10,
  kc_lower, kc_middle, kc_upper, kdj_d, kdj_j, kdj_k, kijun_sen, kst, kst_signal, kvo,
  kvo_signal, linearreg_14, lwr_1, lwr_2, ma_10, ma_20, ma_5, ma_60, macd_dea, macd_dif,
  macd_divergence, macd_hist, massi_25, md_14, mdi_14, mfi_14, mtm_12, mtmma_12, natr_14,
  nvi, obv。

## 2. 筛协议（任务书钉死，与 F 车道同族）

- 横截面 Spearman 秩 IC vs 前瞻 5/10/20 日收益（kline_daily FINAL close 宽表）；
  IS=2019-01-01..2023-12-31（**排名与选择只用 IS**），OOS=2024-01-01..2026-09-18（只报告不选择）。
- **数据边界事实（预注册时已知，非事后偏离）**：TI 表 daily 频实测 2021-01-04 起（F 车道同证），
  IS 有效窗=2021-01-04..2023-12-31，如实标注；OOS 至 2026-09-18。
- 除权剔除：`c3_fundamental.ex_dividend_event`，(t, t+h] 窗内有 divid/bonus/gift/allotment/gugai
  任一事件的样本剔除（事件日非交易日顺延到下一交易日，同 F 车道实现）。
- 有效性掩膜：volume>0（非停牌）& close 有效 & 标的已有 ≥120 交易日历史 & 截面宽度 ≥300（不足记 NaN）。
- regime 条件版：`c1_backtest.regime_state_anchored.vol_pct`（**T-1 PIT**：交易日 t 取 trade_date<t
  最近值；plain MergeTree 有重复日期，argMax(vol_pct, ingest_ts) 去重），桶边界冻结：
  **vol_pct<0.3200=vol_low，0.3200..0.7040=vol_mid，>0.7040=vol_high**；禁用 alt_regime_signal。
- 全部结果入册（含负/零/无效），|IC_IR| 排名，筛≠考。

## 3. 量纲分类（本切片 54 列逐列钉死；rank IC 对日内全截面同变换单调不变，
分类目的=消除跨股量纲不可比；分错风险在 §7 登记）

| 类 | 规则 | 列 |
|---|------|----|
| PX | 原值÷t 日 close（价格尺度水平/价格单位振荡量） | gmma_l30/35/40/45/50/60, gmma_s3/5/8/10/12/15, hma_16, kama_10, kc_upper/middle/lower, kijun_sen, linearreg_14, ma_5/10/20/60, macd_dif/dea/hist, md_14, mtm_12, mtmma_12, ht_ip, ht_qp |
| PX2 | 原值÷close²（价格²方差尺度） | garman_klass_20 |
| VOLCUM | (x−x.shift(20))÷(20×vol_ma20)（累计量类→20日净量占比） | nvi, obv |
| VOLFLOW | 原值÷vol_ma20（成交量单位流量） | kvo, kvo_signal |
| RAW | 构造已无量纲/有界，原值 | histvol_20, ht_dcperiod, ht_dcphase, ht_leadsine, ht_sine, ht_trendmode, kdj_k/d/j, kst, kst_signal, lwr_1/2, massi_25, mdi_14, mfi_14, natr_14, macd_divergence |

- vol_ma20=kline_daily volume 20 日均值（FINAL）；mtm_12 按通达信口径=收盘差分（价格单位）归 PX，
  若实为比率口径则退化为轻度价格倾斜，残差登记 §7。

## 4. 重叠标注 prior_coverage（先钉映射再跑数）

- **l1_pending**（volume_family_l1 在考，取其 exam_results.csv 精确 column 清单交集）：
  kvo, kvo_signal（kvo 族）, linearreg_14, mfi_14, nvi, obv —— 6 列。
- **f_screened**（factor_sop_screen/screen_results.csv 已筛同族）：
  ma_5/10/20/60（MA 族：FCT-TECH-055/058/061/062）, kdj_k/d/j（FCT-TECH-063 KDJ）,
  macd_dif/dea/hist（FCT-TECH-067）, natr_14（FCT-TECH-064 NATR14 直接同源）—— 11 列。
- **none**：其余 37 列。
- 标注只作重叠披露，不剔除不降权——本协议仍全列照筛。

## 5. 统计与选择规则（冻结）

- 每列 × h∈{5,10,20} × {overall, vol_low, vol_mid, vol_high}，IS 与 OOS 各一套：
  ic_mean/ic_std/ic_ir/ic_t/n_days/pct_pos（ic_t=ir×√n）。
- **切片 top-10 升待考池**：按 IS overall h=10 |IC_IR| 降序，门=n_days≥200 且 |ic_t|≥2
  且 h=5/10/20 三档 overall 同号；同 |IC_IR| 并列以 h=20 |IC_IR| 大者先。OOS 只展示不参与选择。
- 多重检验披露：54 列×3 前瞻×4 桶×2 窗=1296 组统计量，选择只在 IS overall h=10 一轴上发生。

## 6. 数据与工程

- TI 按年分块读（2021..2026，period='daily'）；kline_daily FINAL 读 2020-06..2026-10
  （120 日历史门+20 日前瞻覆盖）；缓存 `.runtime/tmp/bizmine/indb/`；只读查库（DatabaseService reader）。
- 时间盒 08:00 收口：算不完交已完成部分+覆盖矩阵。

## 7. 已知边界与残差（诚实登记）

1. adj_factor 恒 1 未复权：全部结论**暂定**，待复权链修复后复核（除权窗剔除为唯一缓解）。
2. IS 有效窗因 TI 覆盖实为 2021-01 起（3 年），短于 F 车道 5 年——统计功效更低，结论权重相应降级。
3. 量纲分类按名称语义钉死，个别列（mtm_12/mtmma_12）库内实现口径未知，分错已定向登记。
4. 停牌/涨跌停不可交易、ST/退市、市值中性化未处理（同 F 车道口径，等权秩相关）。
5. TI 为上游生成器产出，本筛不做逐列数值校验（与 F 车道同，抽查省略登记）。
