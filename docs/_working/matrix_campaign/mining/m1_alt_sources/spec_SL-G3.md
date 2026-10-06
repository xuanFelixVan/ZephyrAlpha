---
ttl: task_bound
title: M1-SL-G3 预注册卡（规格预填）——十大股东结构变动因子（实体股权穿透的 CH 可考面）
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-G3
n_eff: 6   # HHI/机构占比/大股东增减 × 前瞻(20/60) × 桶(2)，冻结后回填
hypothesis: 前十大股东持股集中度上升与机构型股东占比提升=内部人/知情资金用脚投票，对 20-60 日收益有正向预测力；本卡只考 CH 可达的十大股东结构面——股权穿透图本体（edge_holding/equity_penetration.py，PG 域）归 TDM G3 原节点只登记不进本卡。
data_plane:   # CH 2026-10-06 实测
  - {table: c3_fundamental.top10_shareholders, fields: [symbol, announce_date, report_period, shareholder_name, hold_shares, hold_ratio, float_ratio, hold_change, shareholder_type, quality_flag], range: "2005-01-29..2026-09-30", coverage: "1,500,471 行 / 5,843 票", pollution_notes: "announce_date+report_period 双轴=PIT 干净；hold_change 单位（股 vs 比例）与 shareholder_type 取值域冻结前抽查核实"}
  - {table: c3_fundamental.top10_circulating_shareholders, fields: 同构, range: "同窗", coverage: "流通口径对照面", pollution_notes: "总股本口径 vs 流通口径分离考，防混算"}
proxy_downgrade: "proxy：十大股东结构变动代理'控制权/知情资金结构变化'（穿透到自然人/集团的 N 度控制在 PG 域，本期不可考）——披露"
mechanism_one_liner: 经济逻辑一句话——大股东与机构是最低频但信息优势最强的持有者，其仓位变化是对公司内在价值的事前定价。
data_columns_and_formula: |
  数据列名: top10_shareholders.symbol/announce_date/report_period/hold_ratio/hold_change/shareholder_type
  计算式:
    f_hhi(t) = -Δ HHI( hold_ratio_i / Σhold_ratio, i=1..10 )   # 集中度环比降幅（正=更集中），asof announce_date 投影
    f_inst(t) = Δ( Σ hold_ratio | shareholder_type ∈ 机构类 )   # 机构占比变化
    f_net(t) = rank( Σ hold_change | hold_change>0 ) - rank( Σ |hold_change| | hold_change<0 )   # 增减持净方向
    全部 T-1 PIT；低频因子配长前瞻 20/60
exam_method: |
  考法: S2 海选=Spearman 秩 IC 前瞻 20/60；分体制主轴=F4_BDI_MOMENTUM_Z20 三桶；
  辅助分桶: 财报披露季 vs 非披露季。
thresholds:
  - {metric: 海选 |t|, rule: ">3.29 升考弱证据"}
  - {metric: S5 正考, rule: 按 exam_policy；与 A13 户数因子做同源预检（S4 第一关），相关 >0.9 先去重（S4 第二关）}
exam_windows:
  is: 2006-01..2022-12   # 数据 2005 起，留 1 年做基期
  oos: 2023-01..2026-09
sample_window_note: 21 年跨股改全流通/注册制/减持新规各体制段——监管规则变化对增减持语义的跳变按年度分段报告
regime_axis: F4_BDI_MOMENTUM_Z20 主轴 T-1 三桶；预期集中度因子在存量博弈桶更有效，如实报
multiplicity:
  total_tests: "3 因子 × 2 前瞻 × 3 桶 = 18 组（另含流通口径对照 6 组，单独成族不混 N_eff）"
  dsr_note: 与 A13（户数）若同批考试须合并计族 N_eff 或拆批（SOP §3.4 封闭族）
cost_spec: 成本五项现行口径；季频更新低换手
risks_and_prohibitions:
  - "PIT 铁律: announce_date 可知日消费；report_period 禁用于时点对齐（财报期末≠可知日）"
  - "hold_change 正负号/单位冻结前抽查核实（股数 vs 比例混淆=因子整体符号翻转事故）"
  - "shareholder_type 分类的口径版本（数据源变更）按年度报占比，重大变更圈污染段"
  - "十大股东名称中'一致行动人'合并不做（需实体归并=PG 域工作），禁用字符串模糊匹配伪装合并——留痕为简化假设"
  - "与 A13 卡共享样本期，防跨卡同票重复计票（同源预检强制）"
exits: [达标→S6 备料 / 不达标回S0-S3 / 判死归档]
---
