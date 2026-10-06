---
ttl: task_bound
title: M1-SL-A10 预注册卡（规格预填）——隔夜美股/CFTC 定位 cross-market 风险偏好条件化
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A10
n_eff: 8   # SPX overnight/A50/CFTC净头寸三族 × 桶(2-3) × 前瞻(1/5)，冻结后回填
hypothesis: 美股隔夜收益与 CFTC 投机净头寸是全球风险偏好的同步计量，跨市场传染使其对 A 股次日风险偏好有条件预测力（A50/夜盘已部分定价，残差传导仍在）；极端 risk-off 桶收缩 A 股敞口可改善回撤。
data_plane:   # CH 2026-10-06 实测
  - {table: c1_market.us_index, fields: [trade_date, symbol, close], range: "SPX 1993-01-29..2026-09-29；IXIC/DJI 1998/1999 起", coverage: "22,624 行 / 3 指数", pollution_notes: "trade_date 语义须核实为美东交易日（冻结前抽查）"}
  - {table: c1_market.cftc_positioning, fields: [report_date, trader_class, asset_class, market_name, net_positions], range: "1986-01-15..2026-09-08", coverage: "81,270 行 / 21 市场", pollution_notes: "CFTC 周报 report_date=周二头寸、周五发布——发布滞后 3 天必须建模"}
  - {table: c1_market.a50_futures_daily, fields: [trade_date, close], range: "2016-08-29..2026-10-02", coverage: "2,620 行", pollution_notes: "A50 已含夜盘定价信息，作对照项不并主卡"}
  - {table: c1_market.macro_data(_vintage), range: "1993..2026", coverage: "2,261 指标全为中国宏观；国际指标 0 条", pollution_notes: "TDM 自述 DS锚=FRED，但在库无 FRED 面 → FRED 直连假设本期不立，如实记缺口；CN 宏观面归 DS-101 另册"}
proxy_downgrade: "proxy：用 SPX 价格收益代理'全球风险偏好'（无 VIX 在库）；用 CFTC 商品/股指净头寸代理投机情绪。两处 proxy 均披露"
mechanism_one_liner: 经济逻辑一句话——全球风险偏好是单一隐含因子，美股隔夜与杠杆资金净头寸是其最高频可观测投影，传染渠道（资金流+情绪）使 A 股开盘定价系统性偏离后回补。
data_columns_and_formula: |
  数据列名: us_index.trade_date/symbol/close；cftc_positioning.report_date/trader_class/net_positions/market_name
  计算式:
    f_spx(t) = r_SPX(t_us)   # t_us = A 股 t 日前一美东交易日（时区对齐规则冻结：A 股 t 日开盘前最后一个已收盘的美股交易日）
    f_cftc(t) = ( net_positions(t_w) - mean(net_positions, 26w) ) / std(net_positions, 52w)   # 投机净头寸 z，t_w=已发布最晚周（report_date+3 天发布滞后后可知）
    考法: 桶= f_spx 三分位 / f_cftc 二分位（risk-on/off），桶内 A 股组合（考卷现行因子主干）Sharpe/MaxDD 对比
exam_method: |
  考法: 条件化（SOP §2 报告模板：总体+分桶 Sharpe/占比+"何时有效"一句话）；辅助截面: risk-off 桶内低波/高波因子 IC 差。
thresholds:
  - {metric: 条件增益, rule: "risk-off 桶 MaxDD 改善 ≥5pp 且收益不劣化（对齐 T3a regime 增益判据口径）→ 升考证据"}
exam_windows:
  is: 1995-01..2021-12   # SPX 1993 起留 2 年做 z 窗；CFTC 变体可至 1990
  oos: 2022-01..2026-09
sample_window_note: 30+ 年含 1997/2008/2015/2018/2020/2022 危机——尾部事件充足是本卡最强项
regime_axis: f_spx 为主轴；f_cftc 为对照组轴（分别跑、不叠加，叠加=新预注册）
multiplicity:
  total_tests: "2 轴 × 3 桶 × 2 前瞻 ≈ 12 组 + 危机子段 6 组"
  dsr_note: 条件化样本分段后每桶数百日，小桶 low_power 照报
cost_spec: 成本五项现行口径；条件增益判据用成本后净值
risks_and_prohibitions:
  - "前视头号坑=时区对齐错位：美股 t_us 收盘必须严格早于 A 股 t 日开盘，对齐规则冻结进卡并抽 3 个边界日人工核"
  - "CFTC 发布滞后 3 天：t 日只可知 report_date ≤ t-3 天的周报；禁用 report_date 当日可用假设"
  - "macro_data 无国际指标（FRED 缺口）如实记，禁拿中国宏观序列冒充国际宏观源"
  - "us_index.trade_date 时区语义冻结前抽查核实（防收盘日错位一格）"
exits: [达标→S6 备料（条件化收窄） / 不达标回S0-S3 / 判死归档]
---
