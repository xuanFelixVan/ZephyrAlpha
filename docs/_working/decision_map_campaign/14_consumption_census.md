---
ttl: task_bound
title: 14_consumption_census
doc_type: audit_report
---

# 14 · 数据消费面普查（九族消费矩阵）

- 班次：st-census-14-20260924（decision_map_campaign · 只读挖掘 + 本文件唯一写入）
- 回答 Owner 之问："每个环节是不是把所有可用数据都用了"——按族记账：谁在消费、在哪环节、哪些上架无客、哪些考死退役。
- 方法：登记册（docs/01_policies_and_standards/_registry/catalogs/）条目清单 → src/ scripts/ 全词边界 grep（`\b` 词界，排除 producer 层 `data/implementations|*provider*|*collector*|*fetcher*`、display 层 `frontend/`、infra 层 `scripts/ch|DDL|backfill|tasks.yaml|known_data_gaps|data_supply_sentinel|speed_tester`）→ 分类计数。
- 已有账本优先引用：`docs/_working/ultimate_library/ulib3b_supply_relationship_ledger.md`（S1-S70）、`ulib3b_demand_gap_ledger.md`（D1-D36）、`docs/_working/audit_all/LEDGER.md`（L3）、`docs/_audit/data_utilization_audit_2026-08-24.csv`（下称"63 号 CSV"）、机账 `data/runtime/indicator_usage_ledger.json`（2026-09-21）。

---

## 一、九族消费矩阵

| 族 | 条目数 | 有消费方 | 零消费 | 考死/退役 | 代表性消费环节（路径证据） |
|----|--------|---------|--------|-----------|---------------------------|
| ① 技术指标（REG-IND-001） | **143**（142 active+1 deprecated），215 输出列 | **24**（机账 active 口径） | **114**（机账 zero）+ CHIPS 5 条未入机账（本班扫描 4 条零下游） | 1（IND-REV-001，裁定#233） | 唯一统一读取入口 `src/zephyr/factor/indicator_reader.py`（PIT 白名单）——**其唯一 import 方是 demo 脚本** `scripts/backtest/indicator_consumption_demo.py`；实际下游：`alt_data/emotion_index_builder.py`（C3/C4 原料）、`position/core/capital_curve_manager.py`、`position/core/defensive_asset_whitelist.py`、`risk/core/drawdown_tracker.py`、`ex_core/daban_execution.py`、`ex_core/daban_monitors.py` |
| ② 图形指标（candle_pattern） | 1 列（已废） | 0 残留（**全仓 src/scripts/config grep = 0 文件**） | — | **1 全退**（裁定#233，2026-09-14，ruling_registry.yaml:1769） | 继任者图形域健康：`signal_ashare/strategy_signal/pattern_event_store.py` + `pattern_event_job.py` + `scripts/data/pattern_event_backfill.py`/`pattern_catalog_sync.py` 有完整产消链 |
| ③ 另类数据 | **20 表** | **17 表有严格消费方** | **3**（block_trade_detail、stock_comments、+northbound 仅 1 消费） | 0 | 消费强度分层见 §三；龙虎榜→`signal_ashare/limit_up/seat_pattern_analyzer.py`/`lhb_premium_analyzer.py`+`intelligence/event_dragon_tiger.py`；新闻→`intelligence/news_sentiment_analyzer.py`/`news_llm_scorer.py`（30 文件）；两融→emotion C5+`regime/institutional_regime_scorer.py`；竞价→`plan_engine/auction_hit_recorder.py`/`scenario_planner.py`+`risk/core/liquidity_crisis_manager.py` |
| ④ 情绪成分（C1-C6） | 6 | **1 KEEP**（C3）+ 3 留库观察（C4/C5/C6 NO_SIGNAL） | 0 | 0（C1/C2=INSUFFICIENT 等史生长，非退役） | 考试真源 `docs/_working/emotion_line/exam_report_v1.md`（+09-23 S4 重考）；消费方 `data/sector_state_pipeline.py`（偏好重映射）、`signal_ashare/sector/sector_state_aggregator.py`（**emotion_index=None 时 mock 0.5=D13 缺口代码实证**）、`backtest/regime_validation/condition_package.py` |
| ⑤ 宏观（edb/us_index/MAC-*） | **18**（edb_data+us_index+cn_macro+sw_daily+MAC 15 条） | **1**（us_index） | 17 | 1（edb_data 已退役：`frontend/dashboard/api_server.py:1477` 标签"宏观 EDB（已退役）"，代码 0 引用） | us_index 唯一实链消费 `plan_engine/overnight_boundary_reviser.py`（M3-①a 隔夜涨跌幅，经 plan_engine/__init__ 编入 premarket_workflow）；cn_macro/sw_daily 零引用（63 号 CSV 即零，至今未变）；`macro_indicator_registry.yaml` 15 条 MAC-* 全 candidate 且**代码 0 引用、无 source_table 供数绑定** |
| ⑥ 因子（REG-FCT-001） | **175**（170 candidate+4 experimental+1 deprecated） | **4 条有真码消费**（18 条有 code_path；36 条被引用但其中 32 条=TDM 设计意图） | **139** | 1（FCT-FQ-003） | TDM 引用 32 条=设计意图（`config/trading_decision_map.yaml`，与 audit_all L3"24 策略引用 32 因子仅 4 已算"互证）；真码消费 4 条：FCT-FQ-001/002（`scripts/backtest/eval_f2_fundamental_ic.py`）、FCT-EXP-002/006（`scripts/backtest/eval_exp_expectations.py`/`exp_ic_evidence.py`）；实现域 `src/zephyr/factor/fundamentals.py`+`expectations.py`；`belongs_to_strategies` 字段 **175 条全空** |
| ⑦ 策略（REG-STRAT） | **161**（19 active+139 candidate+3 deprecated） | 19 active 全部 code_path 落地+distilled_to_code=True | 139 candidate（0 条因子链齐备，audit_all L3） | 3 deprecated | 因子依赖声明：**仅 2/19 填 alpha_sources**（STR-VREV-018/019→FCT-INTRADAY-029），17 条空声明；实际因子消费在 `pf_core/strategies/multifactor_sleeve_strategy.py`→`factor/analysis/multifactor_synthesis.py`+`ic_ir_calc.py`；数据依赖见 S 册 S37/S60/S67 |
| ⑧ 基本面（c3_fundamental） | **29 表**（DS-199~220/228/229/232/275/302-304） | **14 严格消费 + 3 PIT-only** | **10 ZERO**（+2 事故保留件 news_data_corrupt/pre_tz2） | 0 | 消费改善实证：63 号 CSV（08-24）fin_income/balancesheet/cashflow/indicator 全零 → 今 balance_sheet/income_statement 入 `backtest/core/data_handler.py`，四表入 `data/pit_query.py` 白名单（09-12 PIT 层），financial_indicator 入 `scripts/backtest/three_high_screen.py`；预期侧链 research_report→consensus_daily→`factor/expectations.py`（FCT-EXP 族） |
| ⑨ 另类日历 | **5+**（calendar_event/ipo_schedule/index_adjustment/trade_calendar + 财报解禁历） | 3 强：trade_calendar（37 文件，基础设施级）、calendar_event（6 文件：`overnight_boundary_reviser`/`llm_premarket_analysis`/`regime_cycle_analyzer`/`futures_basis_monitor`/`option_sentiment`/`event_calendar_filler`）、disclosure_plan+share_unlock（经 `data/event_calendar_filler.py` 入日历） | 2：ipo_schedule、index_adjustment **仅 dashboard 展示，零分析消费** | 0 | D25（节前事件前置）、BM-SEL-16（上市天数过滤）声明在案无码 |

矩阵口径备注：
- ①机账 `indicator_usage_ledger.json`（2026-09-21，138 条口径）counts=active 24/stale 0/zero 114；其后新增批 10 CHIPS 5 条（IND-CHIPS-001~005）未入机账，本班 215 列名全词扫描（排除 producer/registry，5,277 文件）判定 CHIPS 4 条零下游、IND-CHIPS-002（SCR）有 1 处换手率输入侧引用。
- ①②⑥⑦ 为登记册全量逐条 grep（143/175/161 全查）；③⑧⑨ 为表名级全词 grep 严格分类（producer/display/infra 剔除后计消费文件数）；④ 读考试卡真源+消费代码实读。
- 63 号 CSV 基准（08-24，DS-001~108）：covered=40/zero_ref=59/code_only=7——本普查为该账的 2026-09-24 分族续账。

---

## 二、"上架无客"清单（数据在库、零/近零消费，按潜在价值 Top 20）

| # | 资产 | 在库规模/状态 | 潜在价值依据 | 现状 |
|---|------|--------------|--------------|------|
| 1 | cn_macro（DS-101） | 宏观库整表 | TDM D5 宏观四组需求（Shibor/社融/M1M2/利差）声明在案 | 代码 0 引用；宏观"有需求无供给、有库无需求"双向断 |
| 2 | sw_daily（DS-102）申万行业日线 | 行业深史 | 行业动量/轮动标尺原料（BM-SEL-08 板块轮动） | 仅 `scripts/governance/meta_question/wo_a2legs/probe_backfill_sources.py` 探测引用 |
| 3 | restricted_shares/share_unlock/share_change 解禁族 | c3 三表 | S41：35_drawdown_protocol 解禁压力减仓 | 仅 share_unlock 经 event_calendar_filler 入日历；**减仓逻辑零消费** |
| 4 | block_trade_detail 大宗明细 | 明细级深表 | S42：机构折价大宗信号（24_daban） | **0 消费**（block_trade 汇总表有 4 消费，明细表闲置） |
| 5 | equity_pledge_detail/summary 股权质押 | c3 两表 | 质押风险否决器原料（基本面消费设计 §不变量④） | 0 消费 |
| 6 | macro_indicator_registry MAC-001~016 | 15 条注册 | regime 周期判定/风险五信号（S33） | 全 candidate、无供数绑定、0 引用 |
| 7 | shareholder_count/top10_circulating_shareholders 筹码族 | c3 两表 | S6：板块筹码维；筹码集中度因子 | 0 消费 |
| 8 | ir_activity_record/irm_interactive_qa 调研互动 | c3 新入库 | 调研热度另类信号 | 0 消费 |
| 9 | hk_kline 与 kline_hq_daily | 双表并存 | 港股联动/ AH 溢价 | **双双 0 消费 + 口径存疑**（S 册存疑①） |
| 10 | factor.ashare_* 14 表（DS-015~028） | 87 因子老库 | 历史因子库 | 63 号 CSV 全零至今——无客亦无死亡证明 |
| 11 | barra 族 4 表（DS-041~044） | 风险模型 | 组合风险分解/风控 | 全零 |
| 12 | ipo_schedule | 在产 | 打板/次新情绪、上市天数过滤（BM-SEL-16） | 仅 dashboard 展示 |
| 13 | index_adjustment | 在产 | 指数调仓事件驱动（S47） | 仅 internal_compute_provider + 展示 |
| 14 | northbound_hold_snapshot（DS-103） | 季度快照 | 北向资金因子（设计备忘 19 号声明"外资行为因子待立项"） | 仅 1 消费（`data/northbound_hold_analysis.py`），未入策略/因子 |
| 15 | auction_book（303 万行） | 竞价逐笔 | S26/S55：竞价强度因子 BM-SEL-23-A-5、大宗配对 | 仅 2 消费（auction_hit_recorder/scenario_planner） |
| 16 | renko/point_figure（DS-077/078） | 变形图 | 形态域素材 | 0 消费（kagi 尚有 7 文件） |
| 17 | 技术指标 CHIPS 族 4 条（CYQ/SCR/CYC 邻族） | 批 10 新产 | 筹码分布/成本均线——打板/获利盘 D21 原料 | 零下游（未入机账） |
| 18 | etf_nav | 在产 | S43：流动性危机协议折溢价监测 | 0 分析消费（仅 producer+展示） |
| 19 | us_futures_intraday | 在产 | D32：晨判美股夜盘/期货供表需求 | 探测+展示级 |
| 20 | 情绪 C4/C6 成分 | 在产（考试 NO_SIGNAL） | 降权候选留用 | 非退役但无加权消费路径（C6 待 LLM 分支 S5） |

---

## 三、"考死退役"清单（防复活无据）

| 项 | 退役依据 | 残留核验（本班） |
|----|---------|------------------|
| candle_pattern 列 + IND-REV-001（图形指标） | **裁定#233**（2026-09-14，ruling_registry.yaml:1769"IND-REV-001/candle_pattern 列退役——蜡烛实现唯一真源迁移图形域 MOD-SIG-145"） | src/scripts/config 全词 grep=**0 文件**，零残留 ✅；IND-REV-001 引用仅存设计文档 docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md（机账 09-21 仍记其 7 consumer files，系文档引用非代码，建议机账加 docs/代码分列） |
| edb_data（宏观 EDB） | api_server.py:1477 标签"宏观 EDB（已退役）" | 代码 0 引用 ✅（ruling_registry 未检索到独立退役裁定条目——建议补登记，防复活无据） |
| FCT-FQ-003（因子） | factor_registry status=deprecated | code_path 仍在 fundamentals.py（实现保留、语义废弃） |
| STR deprecated 3 条 | strategy_registry status=deprecated | — |
| 情绪 C1/C2（INSUFFICIENT）与 C1×C3 ρ=0.824（REDUNDANT-warn） | exam_report_v1 卡B | **非退役**：预承诺等 daban 史生长后与 C3 二选一/合并重考；禁止在重考前删除成分代码 |
| 老架构零客表（无死亡证明的事实死亡） | 63 号 CSV zero_ref 至今：ashare_* 14 表、barra 4 表、data_eng 域 5 表、portfolio_aggregate/ai_operator_decisions/anomaly_diagnoser_result/point_figure 等 | 均未走退役登记——**"零消费≠可删"，须出死亡证明后才入本节**（内收判据 w5_1：零触发零消费→退役） |

---

## 四、"该接未接"清单（消费侧断链，引 D 册+本班实证）

| # | 断链 | 证据 |
|---|------|------|
| 1 | 指标→因子/策略层零接线：indicator_reader（PIT 读取入口）唯一消费方是 demo | src/zephyr/factor/indicator_reader.py 头注+grep import 全仓仅 scripts/backtest/indicator_consumption_demo.py |
| 2 | TDM 32 因子仅 4 已算、0/24 策略因子集齐备 | audit_all/LEDGER.md L3+本班 FCT grep 互证 |
| 3 | 17/19 active 策略 alpha_sources 空声明 | strategy_registry 本班解析 |
| 4 | D13 emotion_index 缺口在码：aggregator None→mock 0.5 | signal_ashare/sector/sector_state_aggregator.py:499-508 |
| 5 | D15 L2 门三原料缺口（sector_state/sector_preference 已产、gate 恒 not_evaluated） | S66 供料实证+D 册 D15 |
| 6 | D34 执行成本反馈闭环：三零件在、选择器不消费 | D 册 D34 |
| 7 | D17 拥挤度/景气/资金三标尺原料在库待接线（stock_daily_basic 7.1M/analyst_forecast 104k/money_flow） | S7/S5/S61+D17 |
| 8 | D5 宏观四组：需求声明无供表，而 cn_macro/sw_daily 在库零消费——同族双向断 | D5+本班族⑤ |
| 9 | D21 流通股本/获利盘（CHIPS 族数据已产，消费未接，裁定#257④ 挂起） | D21+族①CHIPS |
| 10 | 基本面事实侧消费设计未施工：四表已 PIT 可读，FQ/GR 因子仅 2 条被考 | 2026-09-12-fundamental-consumption-design.md+族⑥ |
| 11 | pit_query 白名单 3 表（audit_opinion/earnings_forecast/express_report）进了白名单无分析消费 | 本班族⑧ PIT-only 判定 |
| 12 | 研报 rating 情绪成分（S20 候选）未入 emotion_index（C6 现用 rule 法 news 打分） | S20+exam_report C6 NO_SIGNAL 归因 |

---

## 五、施工项（CNS-01 起，供排班）

| # | 施工项 | 族 | 验收口径 |
|---|--------|----|---------|
| CNS-01 | indicator_reader 接入 multifactor_synthesis：为 FCT-TECH-061/062/070/071/077/083/085 等 TDM 已声明 TECH 因子建计算链（读指标宽表→因子值） | ①⑥ | FCT-TECH 至少 3 条出 IC 证据 |
| CNS-02 | 指标退役轮次评审：机账 zero=114 逐条"消费活性听证"（先批 8/9 社区族），退役走登记；CHIPS 5 条补入机账 | ① | zero 计数带处置结论，机账 143 全覆盖 |
| CNS-03 | block_trade_detail 建消费方（机构折价大宗信号→daban/cohort）或退役评审 | ③ | 折价率信号入 alt_data 或表出死亡证明 |
| CNS-04 | 宏观族总裁决：MAC 15 条绑定 cn_macro/edb 供数+消费方（接 D5/regime），或整族退役；cn_macro/sw_daily 同判；edb_data 退役补裁定登记 | ⑤ | 宏观族每条目有 consumer 或死亡证明 |
| CNS-05 | 基本面 ZERO 10 表打 potential_consumers 标签（引 S 册 S41/S48/S51/S6）或退役评审；restricted_shares 解禁减仓逻辑落码 | ⑧ | 每表 4 态标记（consumed/pit-only/potential/dead） |
| CNS-06 | hk_kline/kline_hq_daily 口径归一裁定（S 册存疑①），败者退役 | ③ | 单一真源+对账记录 |
| CNS-07 | 情绪成分治理落地：C4 降权二评、C6 LLM 分支（S5）、C1 等史自动重考触发器（daban 史≥120 自动跑卡） | ④ | exam 卡重跑记录 |
| CNS-08 | strategy_registry alpha_sources 机械回填：扫描 pf_core/strategies/* import 反填 17 条空声明 | ⑦ | 19/19 active 声明非空且与码一致 |
| CNS-09 | factor_registry belongs_to_strategies 回填：TDM 32 因子×24 策略映射落库 | ⑥⑦ | 字段非空率 0%→≥18% |
| CNS-10 | ipo_schedule/index_adjustment 分析消费方：上市天数过滤（BM-SEL-16）+节前事件前置（D25/M-26） | ⑨ | 过滤器入 universe 链 |
| CNS-11 | auction_book 竞价强度因子 BM-SEL-23-A-5 接线（266k/303 万行在库） | ③ | 因子注册+回测证据 |
| CNS-12 | 北向因子立项（DS-103 消费方从 analysis 升级到 factor） | ③⑥ | FCT 条目+IC 证据 |
| CNS-13 | ashare_*/barra/data_eng 零客老表（约 23 张）死亡证明批量评审（零触发零消费→退役，w5_1） | 全局 | CSV zero_ref 清零带结论 |
| CNS-14 | 机账口径升级：indicator_usage_ledger 分列"代码引用 vs 文档引用"（IND-REV-001 7 文件假阳性案例）；potential_consumers 增枝批文跟催（ulib3b 提案 Owner 未批，登记待令） | ①全局 | 机账 schema v2 |

---

## 六、一句话结论

**数据面"产消比"健康、消费面"用产比"失衡**：20 表另类数据 17 表有客、基本面 29 表 17 表有客（含 PIT 预备）——采集侧无明显浪费；真正的断层的在**变换层与消费层之间**：143 指标仅 24 有客（且统一读取入口无人用）、175 因子仅 4 被考、19 active 策略 17 条不声明因子依赖、宏观族 18 资产仅 1 有客。"每个环节是不是把所有可用数据都用了"的机械答案：**环节④（情绪）⑧（基本面）接近用满；环节①（指标）⑤（宏观）⑥（因子）是上架无客重灾区（合计约 270 条目零客）**；退役面干净（裁定#233 零残留），但 23+ 张零客老表欠死亡证明。
