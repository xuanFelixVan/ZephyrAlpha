---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.signal_ashare（78 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.signal_ashare（78 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=7，wired=37，wired_by_header=34；初判汇总：dispute=7，mount=71

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/signal_ashare/intraday_t0/__init__.py` | intraday_t0 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/limit_up/__init__.py` | limit_up 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/ml_forecast/__init__.py` | ml_forecast 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/screening/__init__.py` | screening 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/sector/__init__.py` | sector 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/sentiment/__init__.py` | sentiment 子包（2026-09-13 平铺债拆分，模块图见上级 __init__.py）。 | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/strategy_signal/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 20 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端）/图12 备选 ②retire→Owner 门位） |
| `src/zephyr/signal_ashare/_extensions/__init__.py` | signal_ashare/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/api/__init__.py` | signal_ashare/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/banker_pattern_simulator.py` | BankerPatternSimulator — 庄家行为模式识别与模拟（MOD-SIG-113，B1-00168，C2 C-035）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/bottom_confirmation_entry.py` | 多维度底部确认与右侧入场模型（MOD-SIG-103，B10-01414，模块17）。 | 2026-09-02（32天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/event_causal_reasoner.py` | EventCausalReasoner — A股事件因果推理器（MOD-SIG-112，B1-00125，C2 D-ALT-22）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/false_breakout_trap_detector.py` | 假突破与诱多检测模型（MOD-SIG-100，B10-01370）。 | 2026-08-25（40天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/foreign_impact_judge.py` | MOD-SIG-038 supplement — 外盘对 A 股影响判定引擎（GAP-F-24，外盘页整体分析后端）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/industry_chain_graph.py` | IndustryChainGraph — 产业链知识图谱（MOD-SIG-125）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/infrastructure/__init__.py` | signal_ashare/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/day_trade_pnl_estimator.py` | DayTradePnlEstimator — 做T盈亏预估器（MOD-SIG-132）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/intraday_buy_sell_point_analyzer.py` | D-SIGNAL-24 A股日内买卖点引擎 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/intraday_size_style.py` | IntradaySizeStyle — 分时微结构与大小盘风格（MOD-SIG-120）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/overnight_conduction_model.py` | OvernightConductionModel — 隔夜全球传导评估模型（MOD-SIG-117）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/overnight_return_expectancy.py` | 隔夜收益预测与开仓期望值（MOD-SIG-107，B10-01464，模块13）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/intraday_t0/t0_point_analyzer.py` | MOD-SIG-068 — 做T点位算法 + 信号回验管线（GAP-F-25 = 设计文档缺口⑤）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/limit_up/limit_up_ecosystem_leadership.py` | 动量领导因子与涨停板生态模型（MOD-SIG-097，B10-01366）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/limit_up/limit_up_potential_scorer.py` | IC加权多因子涨停板潜力评分模型（MOD-SIG-102，B10-01380，模块33）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/limit_up/youzi_relay_emotion_engine.py` | D-SIGNAL-33 A股游资接力情绪引擎 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/market_cap_tier.py` | D_SIGNAL_ASHARE — 流通市值 6 级分层（90 号 Phase2 项，#15 资产分级两维精简） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/adaptive_conformal_tcp_rm_ddci.py` | 自适应保形 TCP-RM/DDCI（MOD-SIG-052，91 号 memo BM-SEL-14-A）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/causal_ml_engine.py` | CausalMlEngine — 因果ML引擎（MOD-SIG-127）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/conditional_density_predictor.py` | 收益率条件密度预测（BM-SEL-13，MOD-SIG-043）。 | 2026-09-18（16天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/conformal_predictor.py` | 共形预测器（BM-SEL-14，MOD-SIG-044）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/event_conditional_density.py` | EventConditionalDensity — 事件驱动条件分布预测（MOD-SIG-123）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/fake_move_distribution.py` | FakeMoveDetector — 主力假动作与筹码派发识别（MOD-SIG-124）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/gap_fill_model.py` | 缺口回补概率模型（MOD-SIG-092，B10-01359）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/kronos_tsfm_predictor.py` | Kronos TSFM 时序基础模型预测器（MOD-SIG-050）——接口契约 + 轻量占位实现。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/mamba_ssm_temporal_enhancer.py` | Mamba-SSM 时序增强器（MOD-SIG-051）——接口契约 + 轻量占位实现。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/mc_path_simulator.py` | 蒙特卡洛路径模拟引擎（MOD-SIG-074，GAP-F-36）。 | 2026-09-13（21天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/next_day_probability_gate.py` | 次日上涨概率统一门槛模块（MOD-SIG-104，B10-01415，模块29）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/survival_time_predictor.py` | Survival 止盈止损时间预测（BM-SEL-15，MOD-SIG-045）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/tcp_rm_conformal.py` | TcpRmConformal — TCP-RM 时序保形预测增强器（MOD-SIG-128）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/ml_forecast/xlstm_long_memory.py` | xLSTM 长记忆（MOD-SIG-053）——接口契约 + 轻量占位实现。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/models/__init__.py` | signal_ashare/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/multi_factor_timing_overlay.py` | 多因子叠加择时（MOD-SIG-108，B10-01482，模块57）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/multi_indicator_divergence.py` | 多指标背离检测（MOD-SIG-095，B10-01363）。 | 2026-09-02（32天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/screening/coarse_screening_funnel.py` | 选股漏斗第二层——初筛漏斗（BM-SEL-17，~1200→~300）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/screening/relative_strength_screener.py` | 多维度相对强弱筛选（MOD-SIG-096，B10-01365）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/screening/selection_funnel_skeleton.py` | 选股漏斗共享骨架（MOD-SIG-086，SIGNAL-ARCH-001 归并裁定落地）。 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/screening/short_term_stock_selector.py` | D-SIGNAL-23 A股短线选股引擎 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/screening/tiered_screening_filter.py` | 选股漏斗第一层——分级指标过滤（BM-SEL-16，~7000→~1200）——A 股信号域薄适配层。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sector/sector_attribute_rules.py` | MOD-SIG-077 — 板块属性标注规则库（GAP-F-18，板块 Top10「属性」列后端）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sector/sector_crowding_launch.py` | SectorCrowdingLauncher — 板块拥挤度与启动条件（MOD-SIG-119）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sector/sector_detail_enricher.py` | MOD-SIG-081 — 板块详情补充维度（GAP-F-17，板块详情页两维度后端）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sentiment/extreme_sentiment_reversal_detector.py` | 极端情绪反转与恐慌底部检测模型（MOD-SIG-099，B10-01369）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sentiment/market_sentiment_analyzer.py` | D-SIGNAL-25 — A股市场情绪分析引擎 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sentiment/sell_news_overdraft_detector.py` | 利好落地变利空预期透支检测（MOD-SIG-106，B10-01453，模块28）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/sentiment/sentiment_price_divergence.py` | 情绪-价格背离指数模型（MOD-SIG-101，B10-01371，Sentiment-Price Divergence Index）。 | 2026-09-13（21天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/services/__init__.py` | signal_ashare/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/signal_history_writer.py` | 信号历史写入管道（c1_market.market_signal_history，一张窄表两管道）。 | 2026-10-02（2天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/stock_relation_gnn.py` | StockRelationGNN — 股票关系 GNN 基类（MOD-SIG-126）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/stock_signal_strength.py` | 个股级信号强度合成器（MOD-SIG-073，GAP-F-39）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/candlestick_scanner.py` | 蜡烛形态扫描器（MOD-SIG-145 P2-a——83 条蜡烛目录的实现主体）。 | 2026-09-29（5天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/combo_rule_loader.py` | 组合规则 YAML 卡加载与匹配（图形四件要单之「组合规则卡」真源读端）。 | 2026-09-30（4天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py` | pattern_event 增量/物化的调度器薄适配（MOD-SIG-145 W4b，JOB-108）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/pattern_event_store.py` | 图形事件存储（c1_market.market_pattern_event 读写，MOD-SIG-145 W1）。 | 2026-09-15（19天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py` | pattern_evidence_certifier — 反过拟合自动认证器（MOD-SIG-148，消费班续班）。 | 2026-09-18（16天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/pattern_match_strategy_library.py` | 量化模式匹配与执行策略库（MOD-SIG-105，B10-01416，模块44）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py` | 图形历史胜率 provider（MOD-SIG-145 W3——win_rate_provider 注入契约的实现侧）。 | 2026-09-18（16天） | in=4/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/series_transform.py` | 序列变换层（MOD-SIG-146）：OHLCV 时间序列 → 替代价格表示（去噪底座）。 | 2026-09-14（20天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/signal_factory.py` | C-028 信号工厂（MOD-SIG-087，B1-00149）。 | 2026-09-13（21天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/signal_weight_adjuster.py` | SignalWeightAdjuster — 信号权重调节器（MOD-SIG-131）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/strategy_cross_vote_funnel.py` | 筛选漏斗第五层多策略交叉投票（MOD-SIG-109，B10-01504）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py` | strategy_decay_certifier — 策略域衰减侧认证器（MOD-SIG-150，协议 v2.0 三域落地）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strategy_signal/strategy_vote_integrator.py` | StrategyVoteIntegrator — 多策略投票加权整合器（MOD-SIG-134，CAND-SIG-004）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strength_ic_data_assembler.py` | MOD-SIG-064 — 选股 6 维权重 IC 校准 60 日窗口数据装配器（21号 memo §3.4 前置）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/strength_ic_weight_calibrator.py` | 量化短线强度 6 维权重 IC 加权校准（21 号 memo §3.4 路径 A，函数级）。 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/supply_chain_gnn.py` | 供应链 GNN（MOD-SIG-055）——接口契约 + 轻量占位实现。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/trendline_sr_detector.py` | MOD-SIG-069 supplement — 趋势线/压力支撑自动识别（GAP-F-33，指数页叠加层后端）。 | 2026-09-29（5天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/volume_regime_adaptive.py` | VolumeRegimeAdaptive — 量能体制自适应策略（MOD-SIG-129）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
| `src/zephyr/signal_ashare/wyckoff_accumulation_signal.py` | Wyckoff 吸筹买点信号（MOD-SIG-094，B10-01362）。 | 2026-09-02（32天） | in=1/out=0·wired | **mount**→FACTORY（原料端）/图12 备选（活线在身未挂线） |
