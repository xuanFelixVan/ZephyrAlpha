---
ttl: task_bound
title: M1-SL-A12 预注册卡（规格预填）——极端天气预警事件研究（台风/暴雨/高温）
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A12
n_eff: 6   # 事件族(台风/暴雨/高温) × 受影响资产族(财险/农业链/深圳本地) × 窗口(2)，冻结后回填
hypothesis: 极端天气预警事件对特定资产族有方向可预期的短窗冲击（台风→财险赔付预期负向/农业链供给冲击正向脉冲），事件研究可检验冲击的统计显著性与可交易性——事件考法，非连续截面因子。
data_plane:   # CH 2026-10-06 实测
  - {table: c1_market.alt_sz_weather_warning, fields: [issue_ts, signal_type, signal_level, district, issue_content, crt_date], range: "2008-07-12..2026-09-28", coverage: "9,595 行 / 14 类信号（深圳）", pollution_notes: "issue_ts 即发布时戳（PIT 干净）；单城覆盖=外推受限"}
  - {table: c1_market.alt_typhoon_landfall_history, fields: ["登陆时点/路径字段"], range: "845 行", coverage: "历史台风登陆全记录", pollution_notes: "跨区域，映射窗口须按登陆地"}
  - {table: c1_market.alt_regime_signal, fields: [signal_date, signal_id, signal_value], range: "F7_TYPHOON_EVENT 116 事件 2005-07..2018-11；F8_HEAT_EVENT 38 事件 2026-08 起", coverage: "事件字典在册但 F7 停更 2018——重建事件表是 M 级前置工作", pollution_notes: "F7 停更缺口如实记"}
  - {table: c1_market.weather_data, fields: [record_date, location_name, forecast_type, temp, precip], range: "2026-08-04..2026-09-30", coverage: "11,313 行 / 40 城——仅 2 个月，不足以考", pollution_notes: "qweather 实时面禁进 IS；TDM pit_proof：预报分版本，禁预报值进 PIT 窗"}
proxy_downgrade: "proxy：深圳预警流代理'华南极端天气'；用板块（财险/农业）代理公司级敞口。均披露"
mechanism_one_liner: 经济逻辑一句话——极端天气对赔付端（财险）、供给端（农业/养殖）、需求端（电力）是物理强制的外生冲击，方向先验清晰且与市场情绪正交。
data_columns_and_formula: |
  数据列名: alt_sz_weather_warning.issue_ts/signal_type/signal_level；alt_typhoon_landfall_history 全列；kline_daily.close
  计算式（事件研究法）:
    事件日 e = issue_ts 所在 A 股交易日（issue_ts ≥ 当日 15:00 则顺延 t+1）
    事件窗 CAR = Σ_{τ∈[0,5]} ( R_asset(τ) - R_bench(τ) )   # 受影响资产族 vs 中证全指代理
    强度加权: signal_level 红色/橙色分桶；显著性 = 事件截面的 t 检验 + bootstrap
exam_method: |
  考法: 事件研究（CAR/t 检验/bootstrap），非 IC；报告各事件族样本量、各窗 CAR 均值与 CI。
thresholds:
  - {metric: CAR 显著性, rule: "主事件族 CAR[0,5] 同号且 90% CI 不含 0 → 升考证据；正考按 exam_policy 事件型准入"}
exam_windows:
  is: 2008-07..2021-12   # 预警流全史前段
  oos: 2022-01..2026-09   # 含 2023-2024 台风季
sample_window_note: 18 年预警史+845 次登陆；事件数决定功效（台风登陆映射华南的子样本更小，low_power 照报）
regime_axis: 事件考法无连续轴；报告义务改为按市场体制（六态）分层的事件冲击对比
multiplicity:
  total_tests: "3 事件族 × 3 资产族 × 2 窗 = 18 组"
  dsr_note: 事件数≈百级，多重检验负担低但单检验功效弱——两头如实声明
cost_spec: 事件型按冲击日开盘→T+1 收盘的执行口径计五项成本
risks_and_prohibitions:
  - "PIT: 用 issue_ts（发布时戳），禁用天气实况回填事件；预报值禁进任何 PIT 窗（TDM: 预报分版本）"
  - "weather_data（2 个月）禁进事件样本；F7 轴停更 2018 的缺口如实记，重建事件表后才可延长"
  - "深圳单城→只对深圳本地/华南资产族立假设，禁全国外推"
  - "财险冲击方向=负（赔付），农业链=供给冲击正向脉冲——方向先验写进卡，事后禁改方向故事"
exits: [达标→S6 备料（事件型 sleeve 备料） / 不达标回S0-S3 / 判死归档（记录已排除事件族）]
---
