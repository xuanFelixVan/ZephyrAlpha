---
ttl: task_bound
rule_form: data
verifiability: manual
title: L1 第二批预注册·族总卡——量能/统计族 18 档（去重后 15 组）沙箱考试（frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（考试启动前写死；启动后任何字段不得改动，改动即作废重开）
lane: P3-B2（L1 车道 st-bizmine-l1-20260919）
family_id: P3-B2-VOLSTAT
sub_families: P3-B2-VOL12（N_eff=12）/ P3-B2-STAT3（N_eff=3）
parent_context: docs/_working/kimi_audit/lane_reports/P3.md §P3-B-NARROWING + p3_prereg/P3-B-NARROWING.md
  + docs/_working/bizmine_night/bizmine_general_order.md §2 §3-L1 + prereview.csv（indicator 库 volume 14 + statistics 4）
---

# P3 第二批总卡：量能/统计族 18 档 → 同源预检+去重 → 15 组点火考试

## 1. 封闭族声明（跑前 frozen，不多不少）

- 候选全集 = prereview.csv indicator 库 volume 族 IND-VOLUME-001..014（14 条，值得考/15 分）
  + statistics 族 IND-STAT-001..004（4 条，值得考/15 分），共 18 条。
- 统一方向规则：**多头方向 = IS 期（2021-2023）平均 raw IC 符号钉死**（总包令 §2 多重检验条款：
  规则在 IS 期钉死后预注册，OOS 干净）。逐档方向与机制见各组卡。
- 同源预检+去重（裁定书挂单前置①②，本 lane 受令执行）：IS 段 (date,symbol) 池化秩相关
  **|ρ|>0.8 合并同源组**；代表档=组内 |增量 IC| 最大者。结果：18 档→**15 组（3 dup）**——
  唯一合并组 {{VWAP, VWMA, LINEARREG, ROLLVAR}}（均为价格水平/量纲代理，ρ 全对 >0.8，代表=ROLLVAR）；
  裁定书 §4.3 先验怀疑的累积族（OBV/AD/PVT/NVI/PVI）**实测未过 0.8 线**（各股上市以来积分路径分歧），
  按实测保留独立档——先验分组让位于数据，此点在报告明示。
- N_eff（挂单前置③）：volume 子族=12 组、statistics 子族=3 组，各自封闭计 DSR 族账；
  跨族 dup（VWAP/VWMA 归 STAT 代表组）计入 STAT3，VOL12 只计 12 组。

## 2. 考试口径（全族冻结，禁挪）

- **数据**（只读经 DatabaseService）：`c1_market.technical_indicator` period='daily'（REG-IND-001 物化宽表；
  ingest_ts 侧 pandas 去重 keep 最后，实测样例日 476 符号日有重复批行）；`c1_market.kline_daily_hfq` FINAL
  （收盘价/成交额/换手）；`c3_fundamental.ex_dividend_event` FINAL（除权剔除）。
- **数据面披露①**：prereview 称 technical_indicator "2019-01 起"，实查 period='daily' 仅 **2021-01-04** 起
  （与 P3 §2.2 consensus 复核同类的乐观口径修正）——IS 窗起点由 prereview 的 2020-01 修正为 2021-01-04。
- **数据面披露②**（诚实条款）：kline_daily_hfq 为后复权表；复权链若后续修正，全部结论标
  「待复权链修复后复核」。
- **宇宙**：当日指标有值且 K 线有收盘价的全部股票（~4400-5200 只/日，截面覆盖 ~91%）；无流动性预筛
  （与 prereview 宽表口径一致；小票容量/滑点风险披露——冻结土规滑点 5bp 对微盘股偏乐观）。
- **组合**：日频截面按方向后因子值取 top50 等权（prereview signalization=截面排名多头；TOP_N=50）；
  当日有效值 <300 只=当日空仓；T 收盘出信号 → T+1 收盘成交（`_c4_engine` 冻结 w.shift(1)，
  涨跌停可成交闸默认开）；成本=冻结土规（佣金 2.5bp 双边 + 印花 10bp 卖 + 滑点 5bp 双边）。
  日频换手不设上限——净收益如实吞换手成本（reject_cost_prohibitive 属合法判红路径）。
- **除权剔除**：ex_dividend_event 事件日 D 与下一交易日禁 Formation（hfq 已含价格调整，此为邻域残余
  伪影保守剔除）；窗内（2020-11..2026-09）事件 24361 起/4921 标的。
- **考窗**：IS=2021-01-04..2023-12-29（参考段不进门：方向/去重/机制在此钉死）；
  OOS=2024-01-02..2026-09-14（判读主段，沿用 P3 FULL cohort 口径，~640 交易日）。
- **毛边际定义**：组合毛日收益 − 当日 K 线全宇宙等权日收益（去 beta 留 alpha），bp/日。
- **反向参考披露**：反方向毛超额（=−毛超额，组合恒等式精确）记参考值**不进门**——若远超门槛属
  「方向待考」证据，报告如实登记但不判 PASS（防事后翻向择优）。

## 3. 三关判据（P3.md 已用口径，勿自创；逐卡同判）

| 关 | 判据 | 门槛 |
|---|---|---|
| ① 毛边际 | OOS 段日均毛超额 | **> 2.7bp/日**（池均成本线口径） |
| ② DSR | OOS 段净日收益，精确 DSR（MOD-SIM-024 官方件 fail-closed） | **> 0.5**，N_eff=子族组数（VOL12→12 / STAT3→3） |
| ③ 经济解释 | 一句话机制自述 + OOS 天数 | 见各卡 §机制，须与因子结构一致；OOS ≥60 交易日 |

判红：任一关不达即 RED；DSR 引擎报错=fail-closed 判红。三关全绿=点火成功，建议进正式 E4 通道
（仍须 E2 幂等预审/E3 构造环，本卡不替代）。

## 4. regime 分桶段（全族义务）

`c1_market.alt_regime_signal` FINAL，取 **F4_BDI_MOMENTUM_Z20**（唯一覆盖全 OOS 窗的状态轴，
risk_on/risk_off/neutral 三态，1989-2026 连续），**T-1 日状态**；每个 PASS 档分桶报 OOS 毛超额/净
Sharpe/天数占比；RED 档分桶值同落结果 JSON 备查（呼应 R 车道「幸存者收益集中于高波灰度桶」发现）。

## 5. 多重检验账

- 两封闭子族各自 N_eff（VOL12=12 组 / STAT3=3 组）；18 档→15 组去重由预检钉死；
  方向=IS 期 IC 符号钉死；参数=REG-IND-001 注册参数不调参——本批无其他研究者自由度。
- 全部结果（含 RED）如实入册：`exam_results.csv` + `exam_report.md`；预检底档
  `.runtime/tmp/bizmine/l1/precheck/precheck_results.json`（含 pairwise_rank_corr.csv）。
- 考试脚本：`.runtime/tmp/bizmine/l1/l1_volstat_exam.py`（临时件不过夜提交）。

## 6. 组卡索引（15 张，跑前 frozen）

| 组卡 | 代表档 | 成员 | 方向 |
|---|---|---|---|
| prereg_group_01_obv.md | IND-VOLUME-001 OBV 能量潮 | 1 档 | 做多低值 |
| prereg_group_02_mfi.md | IND-VOLUME-002 MFI 资金流量 | 1 档 | 做多低值 |
| prereg_group_03_vr.md | IND-VOLUME-004 VR 容量比率 | 1 档 | 做多低值 |
| prereg_group_04_ad.md | IND-VOLUME-005 AD 累积/派发线 | 1 档 | 做多低值 |
| prereg_group_05_pvt.md | IND-VOLUME-006 PVT 价量趋势 | 1 档 | 做多低值 |
| prereg_group_06_wvad.md | IND-VOLUME-007 WVAD 威廉变异离散量 | 1 档 | 做多低值 |
| prereg_group_07_adosc.md | IND-VOLUME-009 ADOSC 蔡金震荡器 | 1 档 | 做多低值 |
| prereg_group_08_eom.md | IND-VOLUME-010 EOM 简易波动量 | 1 档 | 做多低值 |
| prereg_group_09_kvo.md | IND-VOLUME-011 KVO 克林格震荡器 | 1 档 | 做多低值 |
| prereg_group_10_nvi.md | IND-VOLUME-012 NVI 负成交量指标 | 1 档 | 做多高值 |
| prereg_group_11_pvi.md | IND-VOLUME-013 PVI 正成交量指标 | 1 档 | 做多低值 |
| prereg_group_12_force_index.md | IND-VOLUME-014 FORCE_INDEX 强力指数 | 1 档 | 做多低值 |
| prereg_group_13_correl.md | IND-STAT-001 CORREL 量价相关 | 1 档 | 做多低值 |
| prereg_group_14_beta.md | IND-STAT-002 BETA 量价弹性 | 1 档 | 做多低值 |
| prereg_group_15_rollvar_pricelevel.md | IND-STAT-004 ROLLVAR 低波（合并价水平组） | 4 档（dup: IND-VOLUME-003, IND-VOLUME-008, IND-STAT-003） | 做多低值 |

---

合规声明：研究方法与工程产出，不构成投资建议；全部候选未经正式验收（E2/E3/§8 冻结门槛），禁止直接投产。
