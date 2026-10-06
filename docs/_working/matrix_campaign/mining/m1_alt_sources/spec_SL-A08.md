---
ttl: task_bound
title: M1-SL-A08 预注册卡（规格预填）——BDI 运价条件化（状态轴+出口链条件因子）
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A08
n_eff: 6   # BDI/BCI/BDTI 三指数变体 × 三桶 × 出口链板块清单两版，冻结后回填
hypothesis: BDI 是全球贸易实物量的即期计价（运价=即期供需的 tick），BDI 动量上行期出口链（航运/港口/出口制造）相对收益为正——实战先例：bizmine F 车道已把 F4_BDI 作状态轴 T-1 分桶，本卡把"轴"升格为"轴+条件选股"的完整考法。
data_plane:   # CH 2026-10-06 实测
  - {table: c1_market.alt_shipping_index, fields: [trade_date, index_code, index_name, value, change_pct], range: "BDI 1988-10-19..2026-09-30；BCI/BSI/BDTI/BCTI 2006-07-17..2026-09-29", coverage: "31,686 行 / 7 指数", pollution_notes: "运价指数发布日锚定（TDM pit_proof）；HRCI 2011 断供、BHMI 单点=弃用"}
  - {table: c1_market.alt_regime_signal, fields: [signal_date, signal_id, signal_value, state], range: "F4_BDI_MOMENTUM_Z20 1989-11-14..2026-09-30（9,301 条）", coverage: "在产轴", pollution_notes: "轴定义真源在 alt_regime_signal，本卡只引用不重算"}
  - {table: c1_market.kline_sector_880, fields: [trade_date, sector_code, close], range: "2020-03..2026-09", coverage: "出口链板块层（航运/港口/贸易板块代码冻结清单）", pollution_notes: "板块清单 IS 期钉死"}
proxy_downgrade: 出口链成员界定用板块层近似（无个股级出口敞口数据）——proxy 披露：板块级敞口 ≠ 公司级海外营收占比
mechanism_one_liner: 经济逻辑一句话——运价是全球实物贸易的现货价，BDI 领先于出口链企业订单-盈利的实现，运价动量期出口链资产被系统性重定价。
data_columns_and_formula: |
  数据列名: alt_shipping_index.trade_date/index_code/value；alt_regime_signal.signal_value（F4_BDI_MOMENTUM_Z20）
  计算式:
    状态轴: bdi_bucket(t) = 三分位桶( F4_BDI_MOMENTUM_Z20 at T-1 )   # 边界 IS 期钉死
    条件因子: 出口链组合 R_top(t) - 全市场等权 R_mkt(t)，按 bdi_bucket 分桶累计
    判定量: 桶内条件 Sharpe 差 = Sharpe(上桶) - Sharpe(下桶)；-bootstrap 1000 次 CI
exam_method: |
  考法: 非 IC 路线（宏观轴=时序条件，非截面因子）——分桶条件收益/条件回撤 + 桶间差 bootstrap；
  辅助截面考法: BDI mom>0 期，出口链板块动量因子的 IC 是否高于 BDI mom<0 期（交互项）。
thresholds:
  - {metric: 桶间差, rule: "上桶-下桶条件 Sharpe 差 >0 且 90% bootstrap CI 不含 0，仅作升考证据；正考按 exam_policy"}
exam_windows:
  is: 2006-01..2021-12   # BCI/BSI/BDTI 2006 起；BDI 单指数变体可回溯 1990+
  oos: 2022-01..2026-09
sample_window_note: 覆盖 2008 危机/2016 弱复苏/2020 断裂/2021 暴涨/2022-23 回落全体制——体制覆盖是本卡最强项
regime_axis: 本卡自带状态轴（F4_BDI 即主轴）；若叠加六态桶=新预注册，禁跑完换轴
multiplicity:
  total_tests: "3 指数 × 3 桶 × 2 板块清单 = 18 组 + 交互项 6 组"
  dsr_note: 条件化考法的桶数照计 N_eff（SOP §2.7）
cost_spec: 成本五项现行口径；条件化增益判据用成本后口径（防"毛收益幻觉"）
risks_and_prohibitions:
  - "时滞: BDI 伦敦收盘发布，对 A 股自然对齐=T-1；严禁用当日 BDI 分桶当日 A 股"
  - "发布日锚定 PIT：alt_shipping_index.trade_date 即发布锚定日，禁向前填充到更早交易日"
  - "出口链板块代码清单冻结进卡，禁事后挑表现好的板块（选择性报告=本批作废）"
  - "2021 运价极端体制在 IS 内，防单段主导——分桶报告必须含各桶占比"
exits: [达标→S6 备料（条件化收窄适用状态回填 regime_valid） / 不达标回S0-S3 / 判死归档]
---
