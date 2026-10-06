---
ttl: task_bound
title: M1-SL-A06 预注册卡（规格预填）——主力资金流净流入因子族
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A06
n_eff: 8   # 主因子(主力净流入率5d) + 超大单/大单变体 × 前瞻(5/10/20) × 剔除中性化变体，冻结清单定稿后回填
hypothesis: 大单/超大单净流入占比是知情交易者订单流的代理（Kyle 价格影响 + A股资金流研报共识），短期有正自相关漂移；主力净流入率截面秩可预测 5-20 日相对收益。
data_plane:   # CH 2026-10-06 实测
  - {table: c1_market.money_flow, fields: [trade_date, symbol, close, pct_change, main_net_inflow, main_net_inflow_pct, super_large_net_inflow, super_large_net_inflow_pct, large_net_inflow_pct, medium_net_inflow_pct, small_net_inflow_pct], range: "2021-01-04..2026-09-30", coverage: "5,971,039 行 / 5,781 票 / 全 A", pollution_notes: "日度聚合盘后落定不修订（TDM pit_proof）；单笔口径受算法拆单污染的长期趋势属体制风险非数据缺陷"}
  - {table: c1_market.sector_fund_flow, fields: [trade_date, sector_name, net_amount], range: "2026-09-15..2026-10-05", coverage: "板块级仅 3 周——不足以考，本卡不用", pollution_notes: "板块级资金流=未来回补后再立项"}
  - {table: c1_market.market_fund_flow_daily, range: "2026-03-27..2026-09-30", coverage: "146 行市场级——不足以考，本卡不用", pollution_notes: ""}
proxy_downgrade: 无
mechanism_one_liner: 经济逻辑一句话——大单净流入=资金实力方用真金白银投票，知情性订单的自我隐藏极限使流向在数日尺度上持续。
data_columns_and_formula: |
  数据列名: money_flow.trade_date/symbol/main_net_inflow_pct/super_large_net_inflow_pct/large_net_inflow_pct
  计算式:
    f_main(t) = rank( mean(main_net_inflow_pct, 5) )                    # 主因子：5 日主力净流入率均值截面秩
    f_super(t) = rank( mean(super_large_net_inflow_pct, 5) )            # 超大单变体
    f_persist(t) = rank( count_days(main_net_inflow_pct>0, 10) / 10 )   # 持续性变体（正流入天数占比）
    全部 T-1 PIT；考卷接线=进 A1 因子面单因子档
exam_method: |
  考法: S2 海选=Spearman 秩 IC，前瞻 5/10/20；分体制主轴=F4_BDI_MOMENTUM_Z20（T-1）三桶（边界 IS 钉死，最小桶 60 日）；
  分桶预期: 资金流因子在情绪上行桶更有效（跟随资金），下行桶可能反转主导——如实报，不硬凑。
thresholds:
  - {metric: 海选 |t|, rule: ">3.29 仅作升考弱证据"}
  - {metric: S5 正考, rule: 按 exam_policy（成本五项+DSR 喂全部试验次数）；资金流因子必过高换手成本门}
exam_windows:
  is: 2021-06..2024-12   # 数据 2021-01 起，留 5 个月做均线窗+新票稳定性
  oos: 2025-01..2026-09
sample_window_note: 5.7 年横跨牛熊/注册制改革，体制漂移本身是考点（分桶报告义务）
regime_axis: F4_BDI_MOMENTUM_Z20 主轴 T-1 三桶；不做多轴（SOP §2.1 一次一轴）
multiplicity:
  total_tests: "3 因子 × 3 前瞻 × 3 桶 = 27 组"
  dsr_note: 桶计入 N_eff；若按"分体制有效"收窄适用状态须回填 factor_registry.regime_valid
cost_spec: 成本五项现行口径；资金流因子预期高换手，λ 换手惩罚维必须开
risks_and_prohibitions:
  - "PIT: 当日资金流盘后才落定——严禁 T 日因子消费 T 日流向（前视）；一律 T-1"
  - "小单=负向代理受拆单算法长期污染，仅作剔除/对照项，禁作主因子方向假设"
  - "main_net_inflow（绝对额）受市值机械相关，主口径用 _pct（占比）版"
  - "板块级/市场级表（3 周/146 行）禁进 IS——样本不足如实记，不得拉长窗口伪装"
exits: [达标→S6 备料 / 不达标回S0-S3 / 判死归档]
---
