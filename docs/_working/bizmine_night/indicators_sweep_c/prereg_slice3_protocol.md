---
ttl: task_bound
rule_form: data
verifiability: manual
title: 指标库全扫切片C 预注册协议（执行前钉死）——c1_market.technical_indicator 因子列第3等分 55 列 IC 大海选
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-bizmine-indc-20260919
lane: bizmine_night 指标库全扫切片C（与切片A/B 车道并行，按列名排序三等分）
status: frozen（本文落盘先于任何因子取数；落盘后禁改，改动即作废重开）
---

# 切片C 预注册协议（筛≠考）

> 本文件在 DESCRIBE/覆盖探针（仅表结构、日期范围、桶可行性、重复行数）之后、任何因子数值取数之前写死。
> 筛协议与 F 车道 factor_sop_screen 同源（横截面 Spearman 秩 IC），regime 轴按总包令改用
> `c1_backtest.regime_state_anchored.vol_pct`（禁用 alt_regime_signal）。

## 1. 切片定义（确定性，先于取数钉死）

- 列全集 = `DESCRIBE c1_market.technical_indicator` 全 171 列，剔除 8 键/元列
  （trade_date, trade_time, symbol, period, data_source, ingest_ts, exchange, symbol_canonical）
  = **163 因子列**（任务书称 162，实查 163，数据面如实登记）。
- 按 Python `sorted()` 列名升序排列，三等分：切片A=[0:54)，切片B=[54:108)，**切片C=[108:163) 本车道=55 列**。
- 切片C 列清单（升序，序号为全列名排序位次 109..163）：
  obv, parkinson_20, pdi_14, ppo, psy_12, psy_ma6, pvi, pvt, qqe_14, qqe_rsi_ma, roc_12,
  rogers_satchell_20, rsi_12, rsi_24, rsi_6, rsi_divergence, rvgi_10, rvgi_sig, sar,
  senkou_span_a, senkou_span_b, smi, smi_signal, squeeze_mom, squeeze_on, stc, stddev_20,
  stoch_fastd, stoch_fastk, stoch_slowd, stoch_slowk, stochrsi, supertrend_10, supertrend_dir,
  tenkan_sen, trange, trix, trma, tsf_14, tsi, uos, var_20, vim_14, vip_14, vol_price_div,
  vr_26, vwap, vwma_20, wma_10, wr_14, wt1, wt2, wvad_24, yang_zhang_20, zlema_21。

## 2. 筛协议（写死，禁改）

1. **IC 定义**：日度横截面 Spearman 秩 IC（因子列原值秩 vs 前瞻收益秩），前瞻 h∈{5,10,20} 交易日。
   实现复用 F 车道已验证的向量化公式（f2_lib.rank_ic_series 同式）；计算优化=因子秩对三档前瞻复用
   （数学等价：秩不依赖 h），上线前抽 1 因子与逐档全量式比对须逐日相等，等价性核验记录进报告。
2. **窗口**：IS=2019-01-01..2023-12-31（排名用）；OOS=2024-01-01..2026-09-18（只报告不排名）。
   **数据面修正（探针已证，落盘于取数前）**：technical_indicator period='daily' 仅 2021-01-04 起
   （与 F/L1 车道同款乐观口径修正），故**有效 IS=2021-01-04..2023-12-29**，预注册窗起点因数据缺失
   自然截断，非事后选择。
3. **前瞻收益**：`c1_market.kline_daily` FINAL 收盘价，kline 加载 2019-01-01..2026-09-18（预热基准）。
   h 日前瞻 = close[t+h]/close[t]−1；窗尾自然截断（2026-09 前瞻不足的尾部样本落 NaN 自动剔除）。
4. **除权剔除**：`c3_fundamental.ex_dividend_event`，(t, t+h] 内有除权除息/送转/配股/股改事件的
   (t,symbol) 样本剔除（div_masks 同 F 车道实现；事件窗 2019-01-01..2026-09-18 全量加载）。
5. **有效掩膜**：volume>0（非停牌）且 close 有效且该标的 kline 历史 ≥120 交易日（MIN_HIST，同 F）；
   当日有效截面 n<300（MIN_XSEC，同 F）该日 IC 记 NaN。
6. **重复行**：TI 表 (trade_date,symbol) 实测 4,290,444 组重复（多批入库）；统一按 ingest_ts 排序后
   keep 最后一条（与 L1 车道披露口径一致）。
7. **regime 条件版**：`c1_backtest.regime_state_anchored`（plain MergeTree，无 FINAL）vol_pct，
   同 trade_date 多行取 argMax(vol_pct, ingest_ts)；PIT=T-1（交易日 t 取 trade_date 严格小于 t 的
   最近一条）。桶边界**冻结 0.3200/0.7040**：vol_low=<0.3200，vol_mid=[0.3200,0.7040)，vol_high=>=0.7040。
   桶可行性探针（argMax 去重后）：IS 727 日=low 273/mid 289/high 165；OOS 659 日=low 169/mid 248/high 242，
   无 low_power 桶。禁用 alt_regime_signal。
8. **统计量**：每（因子列×h×桶×窗口）记 ic_mean/ic_std/ic_ir/ic_t/n_days/pct_pos；桶∈{overall,
   vol_low, vol_mid, vol_high}，窗口∈{IS, OOS}。全部结果入册（含负/零），共 55×3×4×2=1320 行统计量。
9. **排名与待考池**：按 IS 窗 overall 桶 h=10 的 |IC_IR| 降序排切片内名次，**top-10 升「待考池」**
   （筛≠考，升池不构成 PASS/FAIL）。多重检验位置：55 因子×3 前瞻×4 桶=660 组 IS 统计量，如实披露。
10. **时间盒**：08:00 前收口；算不完交已完成部分+覆盖矩阵，未完成列在报告「未达成」段如实登记。

## 3. prior_coverage 重叠标注（规则先钉死，防事后择优）

每列标注 ∈ {f_screened, l1_pending, none}，判定规则：
- **l1_pending**：本列属 L1 封闭族 18 档（prereview.csv IND-VOLUME-001..014 + IND-STAT-001..004）
  的表列直接映射：obv→OBV, pvt→PVT, pvi→PVI, vr_26→VR, wvad_24→WVAD, vwap→VWAP, vwma_20→VWMA,
  var_20→ROLLVAR, tsf_14→LINEARREG 同指标一步外推输出（注：L1 卡为拟合值，TSF 为伴生输出）。
- **f_screened**：F 车道 screen_results.csv 38 条中存在同技术指标族条目（同名指标或其标准变体，
  参数可异），映射 f_entry_id：rsi_6/rsi_12/rsi_24/stochrsi/crsi→FCT-TECH-066（RSI 族）；
  stoch_fastk/stoch_fastd/stoch_slowk/stoch_slowd/wr_14→FCT-TECH-063（随机/KDJ 族）；
  ppo→FCT-TECH-067（MACD 百分比振荡族）；trange→FCT-TECH-064（ATR/真实波幅族）。
- **none**：其他（保守默认；近似不映射，宁漏标不冒认）。
- 同列双命中取 l1_pending（在考优先）。预计 l1_pending 9 列 / f_screened 12 列 / none 34 列（实测后如实修正）。

## 4. 诚实条款落点（预登记，报告必须回执）

1. 复权：kline_daily.adj_factor 恒 1，全部结论=**暂定**，待复权链修复后复核；缓解=除权事件窗剔除。
2. **水平量列（level）解释边界**：wma_10/trma/zlema_21/senkou_span_a/b/tenkan_sen/supertrend_10/
   sar/vwap/vwma_20/md 类价格水平列的横截面秩 IC≈「名义价格水平效应」（低价格异象），不是该指标
   设计语义的择时信号；本筛按协议**原值入算不做标准化**（禁改协议），报告以 factor_nature 注记
   （level/ratio/oscillator/signal/vol_est 五类）并在解读段显式降级水平量列结论。
3. 因子列由 TI 表物化口径生成，本车道不复算不校验物化正确性（超时间盒，登记为边界）。
4. IS 起点 2021-01-04（数据缺失截断，见 §2.2）；OOS 段尾部前瞻不足自然截断。
5. 胜负不装饰：|IC_IR| 排名全量如实入册，零结果列照登。

## 5. 产物与落点

- 本预注册：`docs/_working/bizmine_night/indicators_sweep_c/prereg_slice3_protocol.md`（先于取数 commit）。
- 结果册：`docs/_working/bizmine_night/indicators_sweep_c/screen_results.csv`（1320 行统计量+标注）。
- 报告：`docs/_working/bizmine_night/indicators_sweep_c/report.md`（协议回执+top-10 待考池+桶分解+偏离登记）。
- 中间件/缓存：`.runtime/tmp/bizmine/indc/`（runner 脚本、长表、宽表缓存，交付后随 TTL 清理）。
