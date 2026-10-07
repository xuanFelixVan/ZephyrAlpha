---
ttl: task_bound
completes_when: 总筹对 A17 口径与全部 needs_chief 行裁决并回写 TDM data_refs 后本件转归档参考
title: "fc·DS 资产×TDM 源线双向对账 v1（机生）"
owner: st-fc-census2-20261005
generation: machine_generated
anchor: "a1e0eed23e"
---

# DS 资产 × TDM 源线 双向对账 v1（机生）

> DS 资产册=docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml datasets 全量（实测 334 条；另有 sources 18、jobs 122 不入本对账）。TDM 源线=config/trading_decision_map.yaml E-L9 层 44 节点。

## 挂接真源勘察结论（先行呈报）

- E-L9 节点**有数据资产引用字段** `data_refs`（44 中 12 非空）→ 有字段者按字段精确挂（needs_chief=false）。
- 无字段者按名称/语义保守匹配：区分性关键词（对象名词级）×资产侧 entity_name/name_zh/format_summary；**排除他节点精确已挂资产**（防语义抢挂）；全行 needs_chief=true，禁硬凑。
- **A17 口径呈裁**：任务面「E-L9 源线 44 条+A17=45 条」中 A17 无法在真源定位——trading_decision_map.yaml 无 A17 节点/字串；源线谱注册表（chain_piling_campaign/02）=SL-A01..C03 共 29 条（已在 E-L9 tags 内）；altdata_line/01 的 A17=特殊品种中类；裁定册 A17=测试真账事项。均非「45 条源线」。本件按可验证口径（E-L9=44）施工，A17 真源请总筹示下。

## 计数（字段，勿散文引用）

- ds_datasets_total: 334
- tdm_sourceline_nodes: 44
- precise_mounted_nodes: 12
- semantic_matched_nodes: 11
- nodes_without_asset: 21
- assets_referenced_precise: 18
- assets_referenced_semantic: 25
- assets_without_sourceline: 291

## 方向一·有源线无资产（21 条，红区=源线在图无资产可挂）

- 缺口节点数: 21

| # | node_id | 名称 | 类别 | 证据 |
|---|---|---|---|---|
| 1 | TDM-E-L9-A16 | 源线·投入产出 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [投入产出;io_table;input_output]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 2 | TDM-E-L9-B01 | 源线·卫星影像 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [卫星;satellite]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 3 | TDM-E-L9-B03 | 源线·招聘JD | 源线 | data_refs 缺失；语义检索零命中（关键词表 [招聘;hiring;job_posting]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 4 | TDM-E-L9-B04 | 源线·电商价格 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [电商;keepa]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 5 | TDM-E-L9-B05 | 源线·招投标 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [招标;投标;procurement]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 6 | TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | 源线 | data_refs 缺失；语义检索零命中（关键词表 [reddit;twitter;社媒]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 7 | TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [雪球;股吧;guba;xueqiu]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 8 | TDM-E-L9-B08 | 源线·APP榜单 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [qimai;sensor_tower;app_rank]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 9 | TDM-E-L9-B10 | 源线·信用卡/支付消费 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [信用卡;spending]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 10 | TDM-E-L9-C01 | 源线·实时门店客流 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [客流;footfall]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 11 | TDM-E-L9-C03 | 源线·直播电商实时成交 | 源线 | data_refs 缺失；语义检索零命中（关键词表 [直播;livestream]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 12 | TDM-E-L9-G2 | 图谱·ChainKnowledgeGraph事实层 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [knowledge_graph;ckg;事实层]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 13 | TDM-E-L9-G3 | 图谱·实体股权穿透 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [股权穿透;equity_penetration;entity_graph]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 14 | TDM-E-L9-G5 | 图谱·投入产出传导 | 图谱/快照/治理 | data_refs 缺失；语义检索零命中（关键词表 [投入产出;io_table]；近名候选若已被他节点 data_refs 精确挂接则排除不抢挂） |
| 15 | TDM-E-L9-AGG | 知识供给汇聚 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 16 | TDM-E-L9-D1 | 决策假设·因子组合挖掘 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 17 | TDM-E-L9-D2 | 决策假设·登记与考试方案 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 18 | TDM-E-L9-E1 | 验证·一问一考考试链 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 19 | TDM-E-L9-E2 | 验证·结论回传与修正 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 20 | TDM-E-L9-Z1 | 治理·问题治理与状态机 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |
| 21 | TDM-E-L9-Z2 | 治理·净零与资产对账 | 图谱/快照/治理 | data_refs 缺失；治理/验证/汇聚节点不设资产关键词（语义面无对象 noun） |

## 方向二·有资产无源线（291 条，DS 册在册而 E-L9 全域零引用）

证据=未被任何 E-L9 节点 data_refs 引用且语义关键词零命中；此类资产多为流程内部资产（因子/信号/回测/执行族），与源线（外部数据供给）本不同层——是否补源线或改挂 E-L9 之外节点，逐台交总筹裁决。

| # | dataset_id | entity | name_zh | 域 | 证据 |
|---|---|---|---|---|---|
| 1 | DS-003 | factor.value_factor | 价值因子信号 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 2 | DS-004 | factor.momentum_20d | 20日动量因子信号 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 3 | DS-005 | signal.composite | 合成交易信号 | D_SIGLEGACY | E-L9 data_refs=0｜语义=0 |
| 4 | DS-006 | risk.limits | 风险限额 | D_RISK | E-L9 data_refs=0｜语义=0 |
| 5 | DS-007 | order.target | 目标订单 | D_PF_CORE | E-L9 data_refs=0｜语义=0 |
| 6 | DS-008 | fill.executed | 成交回报 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 7 | DS-009 | position.snapshot | 持仓快照 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 8 | DS-010 | backtest.result | 回测结果 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 9 | DS-011 | backtest.tick_event | 回测Tick事件 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 10 | DS-012 | backtest.target_weights | 回测目标权重 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 11 | DS-013 | backtest.fills | 回测模拟成交 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 12 | DS-014 | backtest.nav_series | 回测净值序列 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 13 | DS-015 | factor.ashare_alpha87 | A股Alpha#87因子信号 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 14 | DS-017 | factor.ashare_cross_market | A股跨市场因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 15 | DS-018 | factor.ashare_fundamental | A股基本面因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 16 | DS-019 | factor.ashare_institutional | A股机构持仓变动因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 17 | DS-020 | factor.ashare_intraday | A股日内动量因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 18 | DS-021 | factor.ashare_irl | A股IRL因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 19 | DS-022 | factor.ashare_market_structure | A股市场结构因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 20 | DS-023 | factor.ashare_microstructure | A股微观结构因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 21 | DS-024 | factor.ashare_pattern_signal | A股K线形态因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 22 | DS-025 | factor.ashare_ps_liquidity | A股PS流动性因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 23 | DS-026 | factor.ashare_sector | A股板块轮动因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 24 | DS-027 | factor.ashare_smc | A股SMC因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 25 | DS-028 | factor.ashare_technical_indicator | A股技术指标因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 26 | DS-029 | factor_analysis.correlation_analyzer | 因子间相关系数矩阵 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 27 | DS-030 | factor_analysis.correlation_dedup | 去重后的因子集合 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 28 | DS-031 | factor_analysis.decay_monitor | 因子衰减报告 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 29 | DS-032 | factor_analysis.factor_attribution | 因子归因报告 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 30 | DS-033 | factor_analysis.factor_optimization | 优化后的因子权重 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 31 | DS-034 | factor_analysis.ic_decay | IC衰减曲线 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 32 | DS-035 | factor_analysis.ic_ir_calc | IC/IR指标序列 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 33 | DS-036 | factor_analysis.ic_ir_evaluator | IC/IR评估报告 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 34 | DS-037 | factor_analysis.layered_backtest | 分层回测结果 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 35 | DS-038 | factor_analysis.multifactor_synthesis | 合成因子信号 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 36 | DS-039 | factor_analysis.three_level_judgment | 三级研判结果 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 37 | DS-040 | factor_analysis.turnover_analyzer | 换手率分析报告 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 38 | DS-041 | factor.barra_esg | ESG风险因子 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 39 | DS-042 | factor.barra_exposure_calculator | Barra因子暴露矩阵 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 40 | DS-043 | factor.barra_risk_budget_allocator | 风险预算分配方案 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 41 | DS-044 | factor.barra_risk_model | Barra风险模型协方差矩阵 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 42 | DS-045 | factor_mining.causal_validator | 因子因果性验证报告 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 43 | DS-046 | factor_mining.mining_agent | 候选因子集合 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 44 | DS-047 | backtest.anomaly_diagnoser_result | 回测异常诊断报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 45 | DS-048 | backtest.data_quality_checker_result | 数据质量报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 46 | DS-049 | backtest.decay_monitor_result | 策略衰减报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 47 | DS-051 | backtest.param_analyzer_result | 参数敏感性分析报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 48 | DS-052 | backtest.report_generator_result | 回测报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 49 | DS-053 | backtest.result_comparator_result | 回测对比报告 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 50 | DS-054 | backtest.result_deployer_result | 部署状态记录 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 51 | DS-055 | data.feature_store | 特征数据集 | D_DATA | E-L9 data_refs=0｜语义=0 |
| 52 | DS-056 | data.realtime_push_manager | 实时推送数据流 | D_DATA | E-L9 data_refs=0｜语义=0 |
| 53 | DS-058 | data.kline_resampler | 重采样K线数据 | D_DATA | E-L9 data_refs=0｜语义=0 |
| 54 | DS-060 | data_eng.data_lake_manager | 数据湖资产清单 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 55 | DS-061 | data_eng.knowledge_cleaning | 清洗后知识库 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 56 | DS-062 | data_eng.stream_processing | 流处理结果 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 57 | DS-063 | data_eng.synthetic_data | 合成数据集 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 58 | DS-064 | data_eng.training_data_manager | 训练数据集 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 59 | DS-065 | execution.audit_journal | 审计日志记录 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 60 | DS-066 | execution.fill_handler | 成交处理记录 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 61 | DS-067 | execution.position_tracker | 持仓跟踪记录 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 62 | DS-068 | execution.live_portfolio | 实盘组合状态 | D_EX_CORE | E-L9 data_refs=0｜语义=0 |
| 63 | DS-069 | portfolio.optimizer | 优化后目标权重 | D_PF_CORE | E-L9 data_refs=0｜语义=0 |
| 64 | DS-070 | portfolio.portfolio_aggregate | 组合汇总状态 | D_PF_CORE | E-L9 data_refs=0｜语义=0 |
| 65 | DS-071 | portfolio.strategy_runner | 策略目标权重 | D_PF_CORE | E-L9 data_refs=0｜语义=0 |
| 66 | DS-072 | portfolio.topn_momentum_strategy | TopN动量信号 | D_PF_CORE | E-L9 data_refs=0｜语义=0 |
| 67 | DS-073 | ml.ai_operator_decisions | AI操作员决策记录 | D_ML_TRAIN | E-L9 data_refs=0｜语义=0 |
| 68 | DS-074 | ml.training_dataset | 训练数据集 | D_ML_TRAIN | E-L9 data_refs=0｜语义=0 |
| 69 | DS-075 | risk.drawdown_metric | 回撤指标序列 | D_RISK | E-L9 data_refs=0｜语义=0 |
| 70 | DS-076 | trading.pnl | 盈亏序列 | D_TRADING | E-L9 data_refs=0｜语义=0 |
| 71 | DS-077 | market_data.renko | Renko 砖块图 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 72 | DS-078 | market_data.point_figure | Point & Figure 点数图 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 73 | DS-079 | market_data.kagi | Kagi 图 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 74 | DS-080 | market_data.lhb_detail | 龙虎榜明细 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 75 | DS-081 | meta.stock_basic | 股票基本信息 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 76 | DS-082 | market_data.stk_limit | 涨跌停价格 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 77 | DS-083 | market_data.suspend | 停复牌 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 78 | DS-084 | c1_market.index_constituent | 指数成分 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 79 | DS-085 | c1_market.st_stock_list | ST 状态 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 80 | DS-086 | fundamental.daily_basic | 每日估值指标 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 81 | DS-087 | fundamental.fin_income | 利润表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 82 | DS-088 | fundamental.fin_balancesheet | 资产负债表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 83 | DS-089 | fundamental.fin_cashflow | 现金流量表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 84 | DS-090 | fundamental.fin_indicator | 财务指标 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 85 | DS-091 | event.disclosure_date | 财报披露计划 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 86 | DS-092 | event.fin_forecast | 业绩预告 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 87 | DS-093 | event.fin_express | 业绩快报 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 88 | DS-094 | event.dividend | 分红送转 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 89 | DS-095 | event.share_float | 限售解禁 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 90 | DS-096 | event.holder_trade | 股东增减持 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 91 | DS-097 | event.repurchase | 股票回购 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 92 | DS-098 | capital.margin | 两融数据 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 93 | DS-099 | capital.hk_hold | 北向持仓 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 94 | DS-100 | capital.moneyflow | 个股资金流 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 95 | DS-102 | industry.sw_daily | 申万行业行情 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 96 | DS-103 | market_data.northbound_hold_snapshot | 北向资金季度持仓快照 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 97 | DS-105 | meta.ipo_calendar | IPO日历与募资规模 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 98 | DS-106 | market_data.us_futures_intraday | 美股期指与A50盘中实时快照 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 99 | DS-108 | market_data.market_breadth_snapshot | 全市场分钟级宽度快照 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 100 | DS-109 | c0_meta.fetch_perf | 抓取性能记录 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 101 | DS-110 | c1_market.a50_futures_daily | A50 期货日线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 102 | DS-111 | c1_market.adj_factor | 复权因子 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 103 | DS-112 | c1_market.auction_book | 集合竞价盘口 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 104 | DS-113 | c1_market.auction_snapshot | 集合竞价快照 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 105 | DS-114 | c1_market.block_trade | 大宗交易 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 106 | DS-115 | c1_market.block_trade_detail | 大宗交易明细 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 107 | DS-116 | c1_market.calendar_event | 宏观事件日历 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 108 | DS-120 | c1_market.convertible_bond_iv | 可转债隐波 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 109 | DS-121 | c1_market.convertible_bond_list | 可转债清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 110 | DS-122 | c1_market.cross_validation_log | 交叉验证日志 | D_DATA_ENG | E-L9 data_refs=0｜语义=0 |
| 111 | DS-124 | c1_market.dragon_tiger | 龙虎榜 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 112 | DS-125 | c1_market.dragon_tiger_seat | 龙虎榜席位 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 113 | DS-126 | c1_market.etf_list | ETF 清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 114 | DS-127 | c1_market.etf_nav | ETF 净值 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 115 | DS-128 | c1_market.futures_kline_qmt | 期货 K 线（QMT） | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 116 | DS-129 | c1_market.futures_position | 期货持仓 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 117 | DS-130 | c1_market.futures_term_structure | 期货期限结构 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 118 | DS-131 | c1_market.hk_connect_flow | 港股通资金流 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 119 | DS-132 | c1_market.hk_kline | 港股 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 120 | DS-133 | c1_market.hk_stock_list | 港股清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 121 | DS-134 | c1_market.hk_trade_calendar | 港股交易日历 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 122 | DS-135 | c1_market.hog_futures_core | 生猪期货核心 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 123 | DS-136 | c1_market.hog_province_spot | 生猪省现货 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 124 | DS-137 | c1_market.hog_spot_index | 生猪现货指数 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 125 | DS-138 | c1_market.index_constituent | 指数成分 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 126 | DS-139 | c1_market.index_list | 指数清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 127 | DS-140 | c1_market.index_quote | 指数行情 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 128 | DS-142 | c1_market.index_weight | 指数权重 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 129 | DS-143 | c1_market.industry_class | 行业分类 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 130 | DS-144 | c1_market.kline_15min | 15 分钟 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 131 | DS-145 | c1_market.kline_1min | 1 分钟 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 132 | DS-146 | c1_market.kline_30min | 30 分钟 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 133 | DS-147 | c1_market.kline_5min | 5 分钟 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 134 | DS-148 | c1_market.kline_60min | 60 分钟 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 135 | DS-149 | c1_market.kline_cb | 可转债 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 136 | DS-150 | c1_market.kline_daily | 日 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 137 | DS-151 | c1_market.kline_daily_bak_256 | 日 K 备份（256） | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 138 | DS-152 | c1_market.kline_daily_hfq | 日 K 后复权 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 139 | DS-153 | c1_market.kline_etf_15min | ETF 15 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 140 | DS-154 | c1_market.kline_etf_1min | ETF 1 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 141 | DS-155 | c1_market.kline_etf_30min | ETF 30 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 142 | DS-156 | c1_market.kline_etf_5min | ETF 5 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 143 | DS-157 | c1_market.kline_etf_60min | ETF 60 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 144 | DS-158 | c1_market.kline_etf_daily | ETF 日 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 145 | DS-159 | c1_market.kline_futures | 期货 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 146 | DS-160 | c1_market.kline_global | 全球 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 147 | DS-161 | c1_market.kline_hk_daily | 港股日 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 148 | DS-162 | c1_market.kline_index | 指数日 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 149 | DS-163 | c1_market.kline_lof_15min | LOF 15 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 150 | DS-164 | c1_market.kline_lof_1min | LOF 1 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 151 | DS-165 | c1_market.kline_lof_30min | LOF 30 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 152 | DS-166 | c1_market.kline_lof_5min | LOF 5 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 153 | DS-167 | c1_market.kline_lof_60min | LOF 60 分 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 154 | DS-168 | c1_market.kline_monthly | 月 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 155 | DS-169 | c1_market.kline_monthly_hfq | 月 K 后复权 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 156 | DS-170 | c1_market.kline_sector | 板块 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 157 | DS-171 | c1_market.kline_sector_880 | 板块 K 线（880） | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 158 | DS-172 | c1_market.kline_sector_intraday | 板块盘中 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 159 | DS-173 | c1_market.kline_us_daily | 美股日 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 160 | DS-174 | c1_market.kline_weekly | 周 K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 161 | DS-175 | c1_market.kline_weekly_hfq | 周 K 后复权 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 162 | DS-176 | c1_market.limit_up_down | 涨跌停明细 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 163 | DS-177 | c1_market.lof_list | LOF 清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 164 | DS-178 | c1_market.macro_data | 宏观数据 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 165 | DS-179 | c1_market.margin_trading | 两融数据 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 166 | DS-180 | c1_market.market_signal_history | 量化信号历史 | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 167 | DS-181 | c1_market.money_flow | 资金流 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 168 | DS-182 | c1_market.option_greeks | 期权希腊字母 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 169 | DS-183 | c1_market.option_iv_surface | 期权波面 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 170 | DS-184 | c1_market.option_kline | 期权 K 线 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 171 | DS-185 | c1_market.realtime_snapshot | 实时快照 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 172 | DS-186 | c1_market.sector_constituent | 行业成分 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 173 | DS-187 | c1_market.sector_list | 板块清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 174 | DS-188 | c1_market.sector_meta | 板块元数据 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 175 | DS-190 | c1_market.st_stock_list | ST 股清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 176 | DS-191 | c1_market.stock_hot_rank | 个股人气榜 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 177 | DS-192 | c1_market.stock_indicator | 个股指标 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 178 | DS-193 | c1_market.stock_list | 股票清单 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 179 | DS-194 | c1_market.technical_indicator | 技术指标 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 180 | DS-195 | c1_market.tick_data | Tick 逐笔 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 181 | DS-196 | c1_market.trade_calendar | 交易日历 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 182 | DS-197 | c1_market.us_index | 美股指数 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 183 | DS-199 | c3_fundamental.analyst_forecast | 分析师预测 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 184 | DS-200 | c3_fundamental.audit_opinion | 审计意见 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 185 | DS-201 | c3_fundamental.balance_sheet | 资产负债表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 186 | DS-202 | c3_fundamental.cashflow_statement | 现金流量表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 187 | DS-203 | c3_fundamental.disclosure_plan | 披露计划 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 188 | DS-204 | c3_fundamental.earnings_forecast | 业绩预测 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 189 | DS-205 | c3_fundamental.equity_pledge_detail | 股权质押明细 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 190 | DS-206 | c3_fundamental.equity_pledge_summary | 股权质押汇总 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 191 | DS-207 | c3_fundamental.express_report | 业绩快报 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 192 | DS-209 | c3_fundamental.income_statement | 利润表 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 193 | DS-210 | c3_fundamental.industry_class_suppl | 行业分类补充 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 194 | DS-211 | c3_fundamental.main_business | 主营业务 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 195 | DS-212 | c3_fundamental.news_data_corrupt_20260828 | 新闻数据（0828 事故隔离） | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 196 | DS-213 | c3_fundamental.news_data_pre_tz2_20260828 | 新闻数据（0828 时区修复前置） | D_ASHARE_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 197 | DS-214 | c3_fundamental.restricted_shares | 限售解禁 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 198 | DS-215 | c3_fundamental.rights_issue | 配股 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 199 | DS-216 | c3_fundamental.share_change | 股本变动 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 200 | DS-217 | c3_fundamental.share_unlock | 限售解禁日历 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 201 | DS-219 | c3_fundamental.top10_circulating_shareholders | 十大流通股东 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 202 | DS-220 | c3_fundamental.top10_shareholders | 十大股东 | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 203 | DS-221 | c1_market.kline_index_calc | 自算衍生指数日K | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 204 | DS-222 | c1_backtest.node_verdict | 节点验证台账 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 205 | DS-223 | c1_market.stock_profile_ths | THS 个股元数据主数据 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 206 | DS-225 | intelligence.chain_impact_stream | 盘中事件冲击流 | D_INTELLIGENCE | E-L9 data_refs=0｜语义=0 |
| 207 | DS-228 | c3_fundamental.research_report | 券商研报明细（全字段含盈利预测） | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 208 | DS-229 | c3_fundamental.consensus_daily | 一致预期每日快照（预期因子族地基） | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 209 | DS-233 | c1_market.alt_typhoon_track | 台风路径结构化数据 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 210 | DS-234 | c1_market.alt_sz_stat_monthly | 深圳统计月报长表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 211 | DS-236 | c1_market.alt_sz_house_daily | 深圳楼市日度成交表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 212 | DS-239 | c1_market.alt_typhoon_landfall_history | 台风历史登陆档案 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 213 | DS-240 | c1_market.alt_typhoon_names | 台风名称对照字典 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 214 | DS-243 | c1_market.market_pattern_event | 图形形态事件 | D_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 215 | DS-244 | c1_market.market_pattern_win_rate | 图形形态胜率统计 | D_SIGNAL | E-L9 data_refs=0｜语义=0 |
| 216 | DS-256 | c1_market.alt_sz_air_quality_daily | 深圳空气质量日报表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 217 | DS-257 | c1_market.alt_sz_air_quality_region | 深圳分区域空气质量表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 218 | DS-258 | c1_market.alt_sz_reservoir_station | 深圳水库测站字典表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 219 | DS-259 | c1_market.alt_sz_reservoir_rain_day | 深圳水库站点日降雨量表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 220 | DS-260 | c1_market.alt_sz_reservoir_rain_month | 深圳水库站点月降雨量表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 221 | DS-261 | c1_market.alt_sz_house_area | 深圳一手房按面积成交表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 222 | DS-262 | c1_market.alt_sz_house_listing | 深圳二手房源信息表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 223 | DS-263 | c1_market.alt_sz_house_presale | 深圳商品房批准预售表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 224 | DS-264 | c1_market.alt_sz_market_subject | 深圳市场主体发展统计表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 225 | DS-265 | c1_market.alt_sz_stat_analysis | 深圳统计分析文章流表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 226 | DS-266 | c1_market.alt_sz_enterprise_year | 深圳企业登记发展年报表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 227 | DS-267 | c1_market.alt_sz_reservoir_level | 深圳水库水位分钟级序列表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 228 | DS-268 | c1_market.alt_sz_env_meteor | 深圳环境气象预报表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 229 | DS-269 | c1_market.alt_sz_climate_hist | 深圳基本站气候历史表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 230 | DS-270 | c1_market.alt_sz_ground_obs | 深圳地面观测实况表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 231 | DS-245 | c1_market.alt_sz_visibility | 深圳能见度探测分钟级站点流 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 232 | DS-271 | c1_market.daban_engine_load | 打板四引擎应用层负载日批表 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 233 | DS-272 | c1_backtest.alloc_budget_daily | 组合分配逐策略预算表 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 234 | DS-273 | c1_backtest.alloc_shrinkage_daily | 全局风险节流与总暴露表 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 235 | DS-274 | c1_backtest.alloc_budget_change_log | 预算变动裁决与升级流水表 | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 236 | DS-275 | c3_fundamental.consensus_daily_repaired | 一致预期每日快照·历史修复双轨表（研报 PDF 发布时点预测） | D_FACTOR | E-L9 data_refs=0｜语义=0 |
| 237 | DS-276 | c1_backtest.crisis_gate_log | - | D_PF_ALLOC | E-L9 data_refs=0｜语义=0 |
| 238 | DS-277 | c1_backtest.decision_daily | - | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 239 | DS-279 | c1_backtest.sim_platform_journal | - | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 240 | DS-280 | c1_backtest.sim_pocket_daily | - | D_BACKTEST | E-L9 data_refs=0｜语义=0 |
| 241 | DS-285 | c1_market.judgment_daily_plan | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 242 | DS-287 | c1_market.judgment_next_day_forecast | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 243 | DS-288 | c1_market.judgment_plan_verification | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 244 | DS-289 | c1_market.macro_activity_gauge | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 245 | DS-292 | c1_market.macro_pmi_gauge | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 246 | DS-293 | c1_market.macro_price_gauge | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 247 | DS-295 | c1_market.market_breadth_snapshot | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 248 | DS-296 | c1_market.market_cffex_member_ranking | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 249 | DS-297 | c1_market.market_china_bond_yield | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 250 | DS-298 | c1_market.market_convertible_bond_clause | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 251 | DS-299 | c1_market.market_etf_share_snapshot | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 252 | DS-300 | c1_market.market_fund_flow_daily | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 253 | DS-301 | c1_market.market_index_meta | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 254 | DS-302 | c3_fundamental.ir_activity_record | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 255 | DS-304 | c3_fundamental.pdf_forecast_extracted | - | D_DATA | E-L9 data_refs=0｜语义=0 |
| 256 | DS-305 | c1_market.stock_daily_basic | 每日基本面 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 257 | DS-306 | c1_market.tick_depth_5 | 五档 tick 深度 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 258 | DS-308 | c1_market.board_index_tick | 板指 tick | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 259 | DS-310 | c1_market.sector_preference | 板块偏好 | D_SECTOR | E-L9 data_refs=0｜语义=0 |
| 260 | DS-311 | c1_market.sector_fund_flow | 板块资金流 | D_MFLOW | E-L9 data_refs=0｜语义=0 |
| 261 | DS-312 | c1_market.sector_constituent_snapshot | 板块成分快照 | D_SECTOR | E-L9 data_refs=0｜语义=0 |
| 262 | DS-313 | c1_market.sector_constituent_sw_history | 申万成分历史 | D_SECTOR | E-L9 data_refs=0｜语义=0 |
| 263 | DS-315 | c1_backtest.strategy_screen | 策略筛选结果 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 264 | DS-316 | c1_market.limit_up_pool | 涨停池 | D_MARKET | E-L9 data_refs=0｜语义=0 |
| 265 | DS-318 | c1_market.cftc_positioning | CFTC 持仓 | D_POS | E-L9 data_refs=0｜语义=0 |
| 266 | DS-319 | c1_market.agri_wholesale_index | 农批指数 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 267 | DS-320 | c1_market.commodity_futures_main | 商品期货主连 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 268 | DS-321 | c1_market.commodity_spot_price | 商品现货价 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 269 | DS-322 | c1_market.ndrc_fuel_price | 发改委油价 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 270 | DS-323 | c1_market.road_freight_index | 公路运价 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 271 | DS-324 | c1_market.gold_etf_holdings | 黄金ETF持仓 | D_POS | E-L9 data_refs=0｜语义=0 |
| 272 | DS-325 | c1_market.rate_decision_calendar | 议息日历 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 273 | DS-326 | c1_market.macro_data_vintage | 宏观初值修正 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 274 | DS-327 | c1_market.futures_warehouse_receipt | 仓单 | D_POS | E-L9 data_refs=0｜语义=0 |
| 275 | DS-328 | c1_market.option_daily_stats | 期权日统计 | D_MKT | E-L9 data_refs=0｜语义=0 |
| 276 | DS-329 | c3_fundamental.ex_dividend_event | 除权除息事件 | D_MKT | E-L9 data_refs=0｜语义=0 |
| 277 | DS-330 | c1_market.index_adjustment | 指数调整 | D_MKT | E-L9 data_refs=0｜语义=0 |
| 278 | DS-331 | c1_market.sector_code_name_map | 板块码表 | D_SECTOR | E-L9 data_refs=0｜语义=0 |
| 279 | DS-332 | c1_market.l9_readiness_daily | L9 就绪度 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 280 | DS-333 | c3_fundamental.ir_activity_extracted | IR 活动抽取 | D_FCT | E-L9 data_refs=0｜语义=0 |
| 281 | DS-335 | c1_market.account_nav_daily | 账户净值日 | D_PERF | E-L9 data_refs=0｜语义=0 |
| 282 | DS-336 | c1_market.execution_report | 成交回报 | D_EXEC | E-L9 data_refs=0｜语义=0 |
| 283 | DS-337 | c1_backtest.sim_attribution_daily | 归因日 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 284 | DS-338 | c1_backtest.sim_daily_report | 仿真日报 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 285 | DS-339 | c1_backtest.sim_trade_log | 仿真成交流水 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 286 | DS-340 | c1_backtest.cohort_daily_ledger | 队列日账 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 287 | DS-341 | c1_backtest.hypothesis_precheck | 假设预检 | D_SIG | E-L9 data_refs=0｜语义=0 |
| 288 | DS-342 | c1_market.daban_board_event | 打板事件 | D_MKT | E-L9 data_refs=0｜语义=0 |
| 289 | DS-343 | c1_market.alt_fx_rate_ecb | ECB 汇率 | D_MACRO | E-L9 data_refs=0｜语义=0 |
| 290 | DS-344 | c1_market.etf_benchmark | ETF 基准 | D_MKT | E-L9 data_refs=0｜语义=0 |
| 291 | DS-345 | c1_market.market_pattern_certification | 形态认证 | D_SIG | E-L9 data_refs=0｜语义=0 |

## 全 44 源线挂接明细（逐行带证据）

| # | node_id | 名称 | 挂接类型 | 挂接资产 | 证据 | needs_chief |
|---|---|---|---|---|---|---|
| 1 | TDM-E-L9-A01 | 源线·日线/分钟行情 | 精确(data_refs) | DS-002 | DS-002=market_data.ohlc_bar | false |
| 2 | TDM-E-L9-A02 | 源线·Tick分笔 | 精确(data_refs) | DS-001、DS-057 | DS-001=market_data.tick；DS-057=data.tick_data_manager | false |
| 3 | TDM-E-L9-A03 | 源线·板块/概念指数 | 精确(data_refs) | DS-117、DS-119 | DS-117=c1_market.concept_board；DS-119=c1_market.concept_sector | false |
| 4 | TDM-E-L9-A04 | 源线·估值 | 精确(data_refs) | DS-123、DS-141 | DS-123=c1_market.daily_valuation；DS-141=c1_market.index_valuation_daily | false |
| 5 | TDM-E-L9-A05 | 源线·财务 | 精确(data_refs) | DS-208、DS-232 | DS-208=c3_fundamental.financial_indicator；DS-232=c3_fundamental.financial_derived | false |
| 6 | TDM-E-L9-A06 | 源线·资金流 | 精确(data_refs) | DS-016 | DS-016=factor.ashare_capital_flow | false |
| 7 | TDM-E-L9-A07 | 源线·千股千评 | 精确(data_refs) | DS-230 | DS-230=c1_market.alt_stock_comment | false |
| 8 | TDM-E-L9-A08 | 源线·航运运价BDI | 精确(data_refs) | DS-231 | DS-231=c1_market.alt_shipping_index | false |
| 9 | TDM-E-L9-A09 | 源线·财经快讯情绪 | 精确(data_refs) | DS-104、DS-107 | DS-104=event.news_data；DS-107=event.news_sentiment_window | false |
| 10 | TDM-E-L9-A10 | 源线·国际宏观 | 精确(data_refs) | DS-101 | DS-101=macro.cn_macro | false |
| 11 | TDM-E-L9-A12 | 源线·天气 | 精确(data_refs) | DS-198、DS-237 | DS-198=c1_market.weather_data；DS-237=c1_market.alt_sz_weather_warning | false |
| 12 | TDM-E-L9-A13 | 源线·股东户数 | 精确(data_refs) | DS-218 | DS-218=c3_fundamental.shareholder_count | false |
| 13 | TDM-E-L9-A11 | 源线·能源库存 | 语义匹配 | DS-291 | DS-291 命中「能源」(c1_market.macro_daily_gauge) | true |
| 14 | TDM-E-L9-A14 | 源线·互动易问答 | 语义匹配 | DS-303、DS-334 | DS-303 命中「互动易」(c3_fundamental.irm_interactive_qa)；DS-334 命中「irm_interactive」(c3_fundamental.irm_interactive_extracted) | true |
| 15 | TDM-E-L9-A15 | 源线·加密永续/费率 | 语义匹配 | DS-226、DS-227、DS-241、DS-281、DS-282、DS-283、DS-284 | DS-226 命中「crypto」(c1_market.crypto_kline_daily)；DS-227 命中「crypto」(c1_market.crypto_shadow_gate)；DS-241 命中「crypto」(c1_market.sentiment_panel)；DS-281 命中「crypto」(c1_market.hl_funding_history)；DS-282 命中「crypto」(c1_market.hl_liquidation_raw)；DS-283 命中「crypto」(c1_market.hl_oi_snapshot_daily)；DS-284 命中「crypto」(c1_market.hl_perp_snapshot_daily) | true |
| 16 | TDM-E-L9-B02 | 源线·美国官方天气/海洋 | 语义匹配 | DS-238 | DS-238 命中「海洋」(c1_market.alt_sz_marine_forecast) | true |
| 17 | TDM-E-L9-B09 | 源线·进出口贸易 | 语义匹配 | DS-235、DS-294 | DS-235 命中「进出口」(c1_market.alt_sz_port_monthly)；DS-294 命中「进出口」(c1_market.macro_trade_gauge) | true |
| 18 | TDM-E-L9-C02 | 源线·银行网点/信贷活跃 | 语义匹配 | DS-290 | DS-290 命中「信贷」(c1_market.macro_credit_money) | true |
| 19 | TDM-E-L9-G1 | 图谱·Zephyr产业链 | 语义匹配 | DS-224 | DS-224 命中「产业链」(governance.ig_industry_graph) | true |
| 20 | TDM-E-L9-G4 | 图谱·概念/题材 | 语义匹配 | DS-118 | DS-118 命中「概念板块」(c1_market.concept_board_constituent) | true |
| 21 | TDM-E-L9-V1 | 状态变量快照·大盘 | 语义匹配 | DS-242、DS-278、DS-286、DS-314 | DS-242 命中「regime_signal」(c1_market.alt_regime_signal)；DS-278 命中「regime_snapshot」(c1_backtest.regime_snapshot_history)；DS-286 命中「market_state」(c1_market.judgment_intraday_market_state)；DS-314 命中「regime_state」(c1_backtest.regime_state_anchored) | true |
| 22 | TDM-E-L9-V2 | 状态变量快照·情绪 | 语义匹配 | DS-307、DS-317 | DS-307 命中「情绪指数」(c1_market.emotion_index)；DS-317 命中「sentiment_score」(c3_fundamental.news_sentiment_score) | true |
| 23 | TDM-E-L9-V3 | 状态变量快照·板块 | 语义匹配 | DS-059、DS-189、DS-309 | DS-059 命中「sector_snapshot」(data.sector_snapshot_collector)；DS-189 命中「sector_snapshot」(c1_market.sector_snapshot)；DS-309 命中「sector_state」(c1_market.sector_state) | true |
| 24 | TDM-E-L9-A16 | 源线·投入产出 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [投入产出 ; io_table ; input_output]） | true |
| 25 | TDM-E-L9-B01 | 源线·卫星影像 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [卫星 ; satellite]） | true |
| 26 | TDM-E-L9-B03 | 源线·招聘JD | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [招聘 ; hiring ; job_posting]） | true |
| 27 | TDM-E-L9-B04 | 源线·电商价格 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [电商 ; keepa]） | true |
| 28 | TDM-E-L9-B05 | 源线·招投标 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [招标 ; 投标 ; procurement]） | true |
| 29 | TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [reddit ; twitter ; 社媒]） | true |
| 30 | TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [雪球 ; 股吧 ; guba ; xueqiu]） | true |
| 31 | TDM-E-L9-B08 | 源线·APP榜单 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [qimai ; sensor_tower ; app_rank]） | true |
| 32 | TDM-E-L9-B10 | 源线·信用卡/支付消费 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [信用卡 ; spending]） | true |
| 33 | TDM-E-L9-C01 | 源线·实时门店客流 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [客流 ; footfall]） | true |
| 34 | TDM-E-L9-C03 | 源线·直播电商实时成交 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [直播 ; livestream]） | true |
| 35 | TDM-E-L9-G2 | 图谱·ChainKnowledgeGraph事实层 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [knowledge_graph ; ckg ; 事实层]） | true |
| 36 | TDM-E-L9-G3 | 图谱·实体股权穿透 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [股权穿透 ; equity_penetration ; entity_graph]） | true |
| 37 | TDM-E-L9-G5 | 图谱·投入产出传导 | 无资产 | - | data_refs 缺失；语义检索零命中（关键词表 [投入产出 ; io_table]） | true |
| 38 | TDM-E-L9-AGG | 知识供给汇聚 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 39 | TDM-E-L9-D1 | 决策假设·因子组合挖掘 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 40 | TDM-E-L9-D2 | 决策假设·登记与考试方案 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 41 | TDM-E-L9-E1 | 验证·一问一考考试链 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 42 | TDM-E-L9-E2 | 验证·结论回传与修正 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 43 | TDM-E-L9-Z1 | 治理·问题治理与状态机 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |
| 44 | TDM-E-L9-Z2 | 治理·净零与资产对账 | 无资产 | - | data_refs 缺失；治理/验证/汇聚节点无直接资产语义 | true |

## 需总筹裁决清单

1. A17 口径真源（见勘察结论；若确有 45 条源线集，本对账按其补算双向差集）。
2. 全部语义匹配行（11 节点/25 资产）逐台裁决后回写 TDM data_refs 字段。
3. 方向二 291 条零引用资产的层位判定：源线补挂 vs 本属流程内部资产不入源线轴。
4. 方向一 21 条无资产源线的供给决策（B/C 档外采线是否建资产条目）。
