---
ttl: task_bound
title: L04 板块→个股传导 · 挖干作业簿（SKEL）
created: 2026-09-25
sid: L04-stock-wire 班（campaign links/L04）
lane: decision_map_campaign_20260924/links
status: mining（六向全填、三态已裁、施工项待排）
doc_version: v0.1
skeleton_source: ../../09_link_skeletons.md#环节-4（291-353 行）
doc_type: log
---

# L04 · 板块→个股传导（选股/成分映射/因子）——挖干作业簿

> 授权与格式真源=[../README.md](../README.md)（六向台账+自审闸三态+封矿制）。
> 骨架事实基线=[../../09_link_skeletons.md](../../09_link_skeletons.md) 环节 4（TDM L3 十五节点骨架全在、
> 只在回测里跑、候选池无持久化载体 M-41、个股层状态轴/概率表双空白、指数成分 000010.SH 零行、
> DU-11 部分写入病）——本簿对该基线逐项落证或加厚，不推翻。

## §0 本簿三态裁定（自审闸）

| 层 | 三态 | 依据 |
|---|---|---|
| 全簿 | **MINING 待挖** | 六向台账 8 子块全填 ✅；但下列指针文件未读，按 README"章节内全部指针文件已读"判据不达 SEALED |
| W1 成分映射 | **SEALED** | 12 号文行+11 号文 IBT-A02+消费码五件全读；无未读指针 |
| W2 候选池构建 | **MINING** | 未读：24_daban_strategy_detail.md / 25_multifactor_strategy_detail.md / docs/_working/2026-09-11-l308-aggregator-construction.md / 69 号文 §2.16 / algo_flow 出仓块（docs/03_modules/_domain_signal/algo_flow/{fine_scoring_engine,quant_short_term_strength_engine,negative_veto}.yaml） |
| W3 选股因子层 | **MINING** | 未读：factor_registry.yaml 本体逐条 / docs/_working/archive/2026-09/design_memos/90_methodology_open_questions.md（IC 阈值总纲） / 2026-09-12-fundamental-consumption-design.md |
| W4 市值流动性过滤 | **SEALED** | BM-SEL-22-C-5+12 号文 daily_valuation/stock_indicator 行+DU-11+17 号文 §三.3 全读 |
| W5 ST/涨跌停/停牌过滤 | **MINING** | 未读：tradability_preflight.py 本体逐行 / stk_limit S16 三级解析链 / instrument_master.py |
| W6 新闻活跃度维 | **MINING** | 未读：intelligence/news_sentiment_analyzer.py / news_llm_scorer.py / emotion_line exam_report_v1（C6 归因） |
| W7 个股状态轴物化 | **SEALED** | 09 §④⑤+D 册 D22+audit SKL3 行+daban_engine_load 先例码全读；其概率表依赖本身是施工项非未读指针 |

- **BLOCKED = 0**（无外部等待；G9 边界追认属板块线在途定桩，不阻断本线施工）。
- 未读指针清单（解封路径）：上表 5 个 MINING 子块所列 12 件；补读后逐块改判 SEALED 即可封矿。

## §1 子块全树

```
L03 板块层（sector_state/Top-N 名单，G9 追认中）
  │
  ├─ W0 传导段（TDM-E-L2-06/06-1/06-2/06-3 + L2-07/09/10 家族）
  │    sector_conduction 强度调节分（10→+15%/6→+5%/<6→−10% 封闭乘数）
  │    + sector_gate 三级放行门槛（板块>6/个股>5/日成交>2亿）+ sector_leader 龙头定位
  │
  ├─ W1 成分映射（c1_market.sector_constituent，595 板块→6,179 股 SCD-2）
  │    └ 指数成分腿：index_constituent（000010.SH 零行=IBT-A02）
  │
  ├─ W2 候选池构建（TDM-E-L3 全家族十五节点主链）
  │    L3-01 Universe 剔除 → L3-02 九阶段漏斗 → L3-03 双池 5 分制+合流体检
  │    → L3-04 负面否决（七清单）→ L3-05 顺位排序 → L3-06 环境开关
  │    → L3-07 三 sleeve 链 → L3-08 候选池汇总 → L3-09 Tier 分层维护
  │    → L3-10 可交易性预检 ｜ L3-11 日内动态选股（竞价+涨速）｜ L3-12 四维验证
  │
  ├─ W3 选股因子层（15 号文特征仓库架构 + L3 声明 FCT 因子接线）
  │
  ├─ W4 市值流动性过滤（L3-01 市值<30亿/成交<5000万 + BM-SEL-22-C-5 维度 + 17 号文市值五分位）
  │
  ├─ W5 ST/涨跌停/停牌过滤（BM-SEL-16 分级指标过滤 + L3-10 可交易性预检）
  │
  ├─ W6 新闻活跃度维（05 号文③个股条件维 + 17 号文 §三.3 十分位）
  │
  └─ W7 个股状态轴物化（候选池/评分/传导分持久化载体 D22=M-41 + 个股层概率表 LK-05）
       └ 唯一先例：c1_market.daban_engine_load（tasks.yaml:3422 盘后日批）
```

消费总出口：TDM-E-L4 买卖执行 / TDM-P-P2-02 做T调度 / TDM-P-P1 持仓体检 / BM-BUY-03 决策编排 /
整装回测（framework_composer）——现状唯一实际消费面=回测（audit 行 102"生产日循环无挂点"）。

## §2 六向台账（每子块六向全填）

### W0 传导段（L2-06/06-1/06-2/06-3）

| 向 | 台账 |
|---|---|
| ①上游输入 | L03 板块层 sector_state 强弱分位/Top-N（板块线产出，G9 边界追认中=sector_gap_list_and_construction_proposal.md:35）；L1 相位（环境开关查表轴） |
| ②数据原料 | config/trading_decision_map.yaml:1073-1129（节点定义：两字段边界+乘数封闭+三关门槛）；模块 src/zephyr/signal_ashare/core/sector_conduction.py（MOD-SIG-136，99 行）、sector/sector_gate.py（MOD-SIG-026）、sector/sector_leader.py（L2-06-2 实锚） |
| ③状态输出 | 板块强度调节分（乘数封闭）+龙头定位两字段——**无落库载体**（随 W7 一并物化） |
| ④下游消费 | TDM 声明喂 L3 打板链（L3-07-1 消费龙头定位）；代码侧现仅 signal_ashare/__init__ 导出面，无生产调用方（coverage-audit:101"覆盖未接电"同判） |
| ⑤自动化挂点 | **缺位**：yaml activation=postmarket/intraday 声明在，无日循环接线（audit §二 L3 族行） |
| ⑥缺口债 | LK-04（09 号文 §⑦）生产挂点；D15 相关（L2 门三原料，14 号文 §四.5）；两字段边界 vs 22 号 spec 的 G9 追认依赖 |

### W1 成分映射（sector_constituent）

| 向 | 台账 |
|---|---|
| ①上游输入 | 采集侧 tqcenter_provider.py/tdx_provider.py/sector_code_bridge.py（data/implementations/，SCD-2 写入） |
| ②数据原料 | c1_market.sector_constituent FINAL 95,124 行｜2026-07-22..09-03｜595 板块（880 族+881 行业，8803/8804 缺=known_data_gaps `sector_constituent_8803_8804_missing` open）；sector_constituent_snapshot 380,496 行｜09-14..09-24 当日到（12 号文 §1.2:69-70）；指数腿 index_constituent 5 指数，000010.SH（上证 180）**零行**（11 号文 :54） |
| ③状态输出 | 成分归属 SCD-2 截面（sector_code↔symbol+sector_name），非本线新产物、直接复用 |
| ④下游消费 | data/sector_state_pipeline.py:55（money_flow/limit_up_pool×成分聚合）；signal_ashare/mainline_candidates.py:105（881xxx 行业收益合成+名称映射）；signal_ashare/sector/sector_breadth.py、sector_divergence.py；plan_engine/llm_premarket_analysis.py:970（主力资金板块净额 Top5） |
| ⑤自动化挂点 | **在产**：tasks.yaml 自动采集（12 号文 ④列"自动"）；消费侧随 L03 盘后批走 |
| ⑥缺口债 | IBT-A02（000010.SH 回补/改靶裁定，11 号文 :72,324，P1）；8803/8804 缺族（DU-02 连带，12 号文 :67）；成分快照止 09-03 vs snapshot 当日到——两表新鲜度劈叉未立卡（本簿新观察，移交数据线判读） |

### W2 候选池构建（TDM-E-L3 十五节点主链）

| 向 | 台账 |
|---|---|
| ①上游输入 | W0 传导两字段（设计态）、W1 成分映射、W3 因子、W4/W5 过滤器、L1 相位（L3-06 查表轴）、L3-11 竞价/涨速盘中通道（auction_snapshot/auction_book+DS-082） |
| ②数据原料 | 码件全在：signal_fundamental/selection_funnel.py（九阶段，MOD-SIG-086）、negative_veto.py（MOD-SIG-137，七清单含 high_accrual 裁定#231）、selection_confidence.py（MOD-SIG-141）、signal_ashare/fine_scoring_engine.py（MOD-SIG-048）+quant_short_term_strength_engine.py（MOD-SIG-034）+router/signal_conflict_resolver.py（MOD-SIG-010）、core/candidate_pool_aggregator.py（430 行纯函数核，三来源注入零 IO，否决只标记不剔除/容量 10-20/去重确定序）、core/pool_tier_maintenance.py（MOD-SIG-139，165 行升降剔状态机）、core/environment_switch.py（MOD-SIG-138，六段×四开关）、pf_core/strategies/{daban,multifactor,event_driven}_sleeve_strategy.py；原料表 dragon_tiger_seat 4.5 年/money_flow 六年/limit_up_pool/涨速族（12 号文 §1.2，D20 已供给） |
| ③状态输出 | 最终候选池（10-20 只，带 sleeve 标签+顺位分）+双池 5 分制评分+顺位排序表——**纯内存/回测内存话，无持久化**（W7 承接） |
| ④下游消费 | 回测整装 framework_composer.py（唯一实链，audit:102"选股主链互调正常、selection_funnel 4/fine_scoring 6 消费方"）；signal_ashare/screening/* 漏斗族互调；tradability_preflight.py（其自身调用方=0，audit:18） |
| ⑤自动化挂点 | **缺位（LK-04 本体）**：tasks.yaml 仅数据任务无决策日循环触发面（09 号文 §②:314）；唯一近生产挂点=strategy_pipeline/daily_gate_snapshot.py:166（已采集 environment_switch 六段×四开关，只采不断言）；例外先例=daban_engine_load_daily 盘后日批（tasks.yaml:3422→internal_compute_provider→ex_core/daban_load_producer.py） |
| ⑥缺口债 | LK-04（生产挂点）；D22/M-41（池成员持久化，ulib3b_demand_gap_ledger.md:47）；D19 部分（Universe 剔除字段组：limit_up_down 仅 2026-08-03 起，12 号文 :77）；D21（流通股本/获利盘，裁定#257④ 挂起，yaml:2083-2086 注记）；suspend 表 0 行（停牌批量源缺，12 号文 :266） |

### W3 选股因子层（15 号文特征架构+L3 声明因子）

| 向 | 台账 |
|---|---|
| ①上游输入 | technical_indicator 3.5 亿行（12 号文 :97，429 万重复行待清）；c3_fundamental 29 表（14 号文 族⑧：14 严格消费+3 PIT-only+10 ZERO）；news/龙虎榜/资金流另类族 |
| ②数据原料 | 架构真源=docs/_working/archive/2026-09/design_memos/15_data_feature_layer_spec.md §3.4：FactorDAG（factor/core/factor_dag/dag.py）+双执行器+incremental_compute 已施工；**存储层（CH 特征宽表）与实现"待施工"**；因子定义真源=factor_registry.yaml 175 条（170 candidate+4 experimental+1 deprecated）；L3 节点声明因子族（yaml 逐节点 factor_refs）：FCT-MOM-003/009/010/016/029/030、FCT-QUAL-001、FCT-TECH-070/071/077/083/085、FCT-SENT-007、FCT-FQ-004；实现域 factor/fundamentals.py+expectations.py+analysis/multifactor_synthesis.py+ic_ir_calc.py；PIT 入口 factor/indicator_reader.py（唯一消费方=demo，14 号文 §四.1） |
| ③状态输出 | 因子值序列（FactorSignal：z-score+rank_pct+NaN ffill 裁定）——落库载体待建（15 号文 §3.4 存储层） |
| ④下游消费 | **仅 4 条因子有真码消费**（FCT-FQ-001/002→scripts/backtest/eval_f2_fundamental_ic.py、FCT-EXP-002/006→eval_exp_expectations.py/exp_ic_evidence.py，14 号文 族⑥）；TDM 引用 32 条=设计意图（与 audit_all/LEDGER.md L3"24 策略引用 32 因子仅 4 已算"互证）；belongs_to_strategies 175 条全空 |
| ⑤自动化挂点 | 回测侧在（FactorDAG/评估器）；生产侧缺位——因子计算无日循环批（同 LK-04 根因） |
| ⑥缺口债 | CNS-01（14 号文 §五：indicator_reader 接 multifactor_synthesis）；CNS-09（belongs_to_strategies 回填）；指标 429 万重复行待清（12 号文 :97）；D17 拥挤度/景气/资金三标尺原料在库待接线（14 号文 §四.7） |

### W4 市值流动性过滤

| 向 | 台账 |
|---|---|
| ①上游输入 | stock_daily_basic 7.1M 行（5,781 只/日满量，12 号文 :95）、stock_indicator 1,168 万行（circ_mv 断供双案 resolved #288，:96）、daily_valuation（残病，DU-11） |
| ②数据原料 | 口径三条：L3-01 yaml:1417-1425（市值<30 亿/日成交<5000 万剔除）；BM-SEL-22-C-5（battle_map_05:99：30-150 亿满分 10 分、大盘折价、微盘扣分）；17 号文 §三.3 市值五分位验收轴 |
| ③状态输出 | 过滤布尔+市值流动性子分（BM-SEL-22-C-5 维度分）——随候选池落 W7 载体 |
| ④下游消费 | selection_funnel 流动性阶段+short_term_stock_selector 评分卡（battle_map_05:419 MOD-SIG-023 stable） |
| ⑤自动化挂点 | 缺位（随 L3 主链，LK-04）；数据面 daily_valuation 病未被哨兵捕获（7 日行数地板 2,000 对 1,000 行日会响但当日落库中，12 号文 DU-11 :228） |
| ⑥缺口债 | **DU-11**（registered 扩面 P2：09-23=2,504/09-24=1,000 行 vs 应 ~5,560，已有幂等重跑工单 ~11h/次，12 号文 :227-229,257）；估值分位（S4）+市值权重消费直接受害 |

### W5 ST/涨跌停/停牌过滤（BM-SEL-16+L3-10）

| 向 | 台账 |
|---|---|
| ①上游输入 | stock_basic（名称 ST 标记，快照型缺 5 日 accepted）、stk_limit 921 万行（涨停价真源 S16 三级解析链 100% 验证，12 号文 :59）、limit_up_down 49 日浅史+limit_up_pool 54 日（DU-14，:77-78）、ipo_schedule（0 分析消费，仅展示，14 号文 §二.12）、suspend 表 **0 行**（akshare 无批量源，12 号文 :266） |
| ②数据原料 | BM-SEL-16 六件套（battle_map_05:1394-1436：3 秒级 7000→1200 只，绝对排除涨停封板/跌停/停牌+门禁排除 ST/*ST+AUM 分级成交额门槛+次新<30 天+弃庄>95%；**三参数全 proposed 待实现**）；码件=signal_ashare/screening/tiered_screening_filter.py（MOD-SIG-046，is_st/涨跌幅限参已实装 :72-90,152）；L3-10 可交易性预检=tradability_preflight.py（MOD-SIG-151 五查：停牌/一字/权限/资金一手 fail-closed+笼子建议价，yaml:1883-1914）； instrument_master.py 为数据口径锚（MOD-DATA-069） |
| ③状态输出 | 可交易布尔+排除原因分类（喂漏斗与执行层防空转） |
| ④下游消费 | BM-SEL-17 初筛漏斗（battle_map_05 链）；执行层兜底拦截（yaml fallback"预检数据缺→标记未预检"）；**tradability_preflight 现调用方=0**（audit:18"今天刚落地、调用方为零"复核成立：src 全仓 grep 仅自身） |
| ⑤自动化挂点 | 缺位；S25 供数声明在案（ulib3b_supply_relationship_ledger.md:60→battle_map_05:1408） |
| ⑥缺口债 | D19（limit_up_down 浅史→历史回测面缺）；suspend 0 行=停牌批量真源缺（新观察：BM-SEL-16"绝对排除停牌"无批量数据可执行，移交数据线）；CNS-10（上市天数过滤接线 ipo_schedule）；弃庄概率腿依赖 BM-SEL-05（设计态 ⛔，battle_map_05:213） |

### W6 新闻活跃度维

| 向 | 台账 |
|---|---|
| ①上游输入 | news_data 825 万行（当日到，在产健在，12 号文 :75） |
| ②数据原料 | 打分腿 news_sentiment_score 773 万行**止 2025-09-09**（停摆 1 年+=DU-05 新发现未登记，:74）；窗口腿 news_sentiment_window market 级 185 日在产、**symbol 级止 2026-08-20**（DU-06，:73）；需求口径=05 号文 :12（"新闻活跃度（期内新闻多的优先）——选股传导层条件维，立卡"）+17 号文 :33（近 30 日新闻条数十分位、每格 n≥30） |
| ③状态输出 | 个股新闻活跃度十分位特征（未存在，待 C06 注册） |
| ④下游消费 | 设计消费方=L04 条件维（05 号文）+做T全量×状态匹配轴（17 号文）；现无任何消费码 |
| ⑤自动化挂点 | news_sentiment_window nightly cron 20:08 在跑（仅 market 腿）；symbol 腿接线已修但仅覆盖 market（12 号文 ④列）——半挂点 |
| ⑥缺口债 | DU-05/DU-06（补采优先级表序 6"修接线即回"，12 号文 :259）；intelligence/news_sentiment_analyzer.py+news_llm_scorer.py 消费面未读（§0 已列） |

### W7 个股状态轴物化（M-41/D22+概率表 LK-05）

| 向 | 台账 |
|---|---|
| ①上游输入 | W0 传导两字段+W2 池/评分/顺位+W4/W5 过滤结论（全在内存与回测里，无落盘） |
| ②数据原料 | 需求真源=ulib3b_demand_gap_ledger.md:47（D22 池成员持久化载体，TDM:1850-1862 映射，M-41 待登记）；yaml L3-09 注记"池成员状态存储=治理状态表/新 DS（待登记施工，外审 M-41）"；09 号文 §8.3.3"骨架定义在、状态轴与概率面双空洞"；**仓内唯一先例=c1_market.daban_engine_load**（ex_core/daban_load_producer.py 逐交易日产出、internal_compute_provider 路由、tasks.yaml:3422 日批、PIT 读法=先 max(trade_date)<T 最近事件日分区，yaml L3-07-1 :1714-1748） |
| ③状态输出 | 应产出：候选池快照（trade_date×stage×symbol×sleeve×顺位分×评分明细×否决标记×传导调节分）+Tier 归属变更流——载体不存在 |
| ④下游消费 | 全部下游（L4 买卖/P2-02 做T调度/P1 体检/BM-BUY-03/整装回测/做T全量×状态匹配 05 号文 ⓪.2）现都吃不到真值全史；回测侧只能现算 |
| ⑤自动化挂点 | 缺位=本簿主施工面（C01/C02）；复用 daban_engine_load_daily 模式即有调度先例，零新调度器 |
| ⑥缺口债 | **M-41/D22（本簿头号施工项）**；LK-05（个股层状态轴物化与概率表空白，09 号文 §⑦:348）；概率表面=个股层无条件概率表仓内未立项（09 §⑤），GPU 搜索只覆盖策略层（03 号文 §一）；S10 NO_EDGE 削弱上游输入有效性（09 §⑤） |

## §3 施工项（L04-C01 起；既有账本条目只引用不重立，净零）

| # | 施工项 | 内容与真源 | 验收口径 | 内收声明 |
|---|---|---|---|---|
| **L04-C01** | **候选池持久化载体补建（M-41/D22 落地）** | 新表族：c1_market.stock_candidate_pool（trade_date×stage×symbol×sleeve×rank_score×score_components JSON×veto_flags×conduction_adj×version）+ 池成员 Tier 变更流；DDL 形态对齐 sector_state 草案（sector_layer_skeleton_v0.md §5：DateTime64(3)+显式时区、ReplacingMergeTree、components JSON 逐成分 status、语义化 version，RULE-SCHEMA-TZ 合规）；按 RULE-SSOT 架构数据走 apply 直写 DB+DDL-as-Code | 表建成且连续 10 个交易日有盘后真值行；回放任一历史日可取当日池快照 | 载体=合并"D22 欠账+回测内存话"两处旧态；调度复用 daban_engine_load_daily 模式零新调度器 |
| **L04-C02** | **L3 生产日循环挂点通电（引 LK-04）** | 盘后 internal 批串接：selection_funnel→negative_veto→candidate_pool_aggregator→pool_tier_maintenance→L04-C01 表；盘前 tradability_preflight 挂 premarket_workflow（接线先例=strategy_pipeline/daily_gate_snapshot.py:166 已采集 environment_switch）；环境开关断流降级遵 yaml L3-06 fallback（不开新仓，D103 终裁） | 生产日循环每交易日产出池快照且 audit 矩阵 L3 行"覆盖未接电"→"已接电"；tradability_preflight 调用方 0→≥1 | 不新建编排器（日循环编排器本体=09 号文 §8.3.2 另案），只挂既有 internal 批与 premarket_workflow |
| **L04-C03** | **DU-11 daily_valuation 部分写入重跑排期** | 已有幂等 full_refresh 工单（~11h/次）排期执行；重跑后 09-16..09-24 符号覆盖复核（12 号文 :227-229,257） | 最新日行数恢复 ~5,560 且连续 5 日稳定；S4 估值分位消费解除降级 | 纯引用既有工单，本簿只登记排期义务 |
| **L04-C04** | **BM-SEL-16 参数收口** | tiered_screening_filter.py 三参数 proposed→implemented：成交额门槛（AUM≤100 万→≥500 万）、次新<30 天排除（接 ipo_schedule，并 CNS-10）、弃庄>95% 排除（依赖 BM-SEL-05 设计态→如实降级 status=insufficient 禁硬凑） | 过滤器参数全 implemented 或 insufficient 留痕；7000→1200 淘汰率实测报告一份 | 不新增过滤器文件，收口既有 MOD-SIG-046 |
| **L04-C05** | **L3 声明因子计算链（收窄 CNS-01）** | 优先 8 条：FCT-MOM-003/009/010/030、FCT-TECH-070/071/085、FCT-SENT-007；indicator_reader（PIT 白名单）→multifactor_synthesis/ic_ir_calc 出 IC 证据；IC 阈值遵 15 号文 §3.5 四门禁 | ≥3 条因子出 IC 证据（对齐 CNS-01 验收）；L3 节点 factor_refs 逐条"已算/未算"状态可机查 | 与 CNS-01 合并执行不另立项目，本簿只圈定 L04 优先子集 |
| **L04-C06** | **新闻活跃度维特征** | 前置=DU-05/06 修复（12 号文补采序 6）；后注册"近 30 日新闻条数十分位"因子入 factor_registry（17 号文 §三.3 口径：n≥30/格） | 因子注册+IC 证据；05 号文 :12 立卡闭环 | 单特征一卡，不建新闻子系统 |
| **L04-C07** | **个股层状态轴概率表立项（引 LK-05）** | P(个股 T+1 收益分布｜板块状态×传导调节分×池层/Tier)——载体（C01）有≥120 交易日真值后开算；方法论对齐 P1-T2 排名持续性法（04 号文 §一）+17 号文 §三格子四元组（n≥30/Wilson LB） | 预注册考试卡+首版概率表；四判据"概率表可算" ✗→🟡 | 复用 P1 表四元组范式零新框架 |
| **L04-C08** | **传导两字段接线核验** | sector_conduction.py 乘数表与 yaml:1073-1100 对表（10→+15%/6→+5%/<6→−10%）；三级放行门槛三原料（sector_state 强度/个股强度/日成交额）供数接线（D15 关联） | 单测对表绿+三原料在 daily_gate_snapshot 可取 | 收口既有 MOD-SIG-136/026，零新模块 |

**引用既有账本（不重立）**：IBT-A02（000010.SH 回补/改靶，11 号文 :72，P1）；CNS-10（ipo_schedule 接线）；CNS-11（auction_book 竞价强度因子 BM-SEL-23-A-5）；CNS-02/09（机账/注册表回填）；DU-03（margin_trading 断 4 日→L3-12-1 资金面验证降级）；DU-05/06（新闻双腿，C06 前置）；DU-14（limit_up_down 等浅史群）；D21（流通股本工程，裁定#257④ 挂起）；G6（能力反查面板块资产零在编→图书馆班）。

**优先级 Top3**：① L04-C01（M-41 载体——四判据"状态真值全史 ✗"唯一解，下游全链条解锁）→ ② L04-C02（LK-04 通电——载体无挂点=死表，二者同批施工）→ ③ L04-C03（DU-11 重跑——市值/估值原料日毁中，已有工单只欠排期）。

## §4 标准件（18 号文纪律：有开源实现必须引用并采用，不自造）

| 标准件 | 仓库 | 许可证 | 对本线可采纳点 | 采纳建议 |
|---|---|---|---|---|
| **qlib**（Microsoft） | https://github.com/microsoft/qlib | MIT | 横截面选股全流水线范式：数据处理→Alpha158/360 因子库→IC/ICIR 评估→TopKDropout 选股组合→回测；截截面 rank 归一算子实践 | W2 漏斗压缩率与 W3 因子评估对表参照；TopKDropout 对照 L3-05 顺位排序做基线考试（本簿判：采纳其评估与基线范式，不引入其数据层） |
| **vectorbt** | https://github.com/polakowo/vectorbt | Apache-2.0 | 向量化截面筛选+组合模拟（from_signals 批量筛→排→组合），数千参数组合秒级 | W4/W5 过滤矩阵的向量化实现参照；单机轻量路线与 15 号文 §3.4"不引入重型框架"裁定同向 |
| **zvt** | https://github.com/zvtvz/zvt | MIT | A 股友好统一 schema+因子计算+选股（screener）一体编排 | W1 成分映射 SCD 语义与 W2 池维护状态机对照件 |
| **rqalpha**（Ricequant） | https://github.com/ricequant/rqalpha | Apache-2.0 | A 股回测撮合/停牌涨跌停处理口径 | W5 可交易性规则（停牌/一字/笼子）对表参照 |
| qlib RL/研究面（延伸） | https://github.com/microsoft/qlib/tree/main/qlib/contrib | MIT（同库） | 截面因子→学习排序（Learning-to-Rank）样本，TDM 调研已点名 RankGLU/L2R（yaml:1408 注记） | W3 因子合成第二阶段参照 |

- 许可证核对说明：搜证时外部搜索通道部分限流（429），上表仓库与许可证按检索所得+各仓库 LICENSE 惯常记载录入；**采纳施工前须以仓库 LICENSE 文件当时文本复核一次**（18 号文纪律的留痕义务）。
- 采纳边界（防自造复发）：本线所有"漏斗压缩/截面归一/IC 评估/可交易排除"算法在施工时必须先对表上列实现并留对照注记，差异点写进节点 algo_note，禁闭门造轮子。

## §5 挖掘执行日志

| 批 | 矿脉 | 证据源（路径） | 判定 |
|---|---|---|---|
| B1 | 作业簿授权与格式 | links/README.md + 09_link_skeletons.md:291-353,725-745 | 六向台账+三态判据锁定 |
| B2 | TDM L2-06/L3 全家族 | config/trading_decision_map.yaml:1073-2150 | 十五节点定义/模块锚/因子声明全录 |
| B3 | battle_map 选股域 | battle_map_05_stock_selection.md（BM-SEL-16/22/23/24/25/05+S22/S25/S26/S27/S28 供数行 714/1408/3094/2434/3259） | 过滤/评分/融合链全录；BM-SEL-16 三参数 proposed 实锤 |
| B4 | 数据普查 | 12_data_universe_census.md（§1.2/§1.3/§1.6+DU-11:227-229+补采表:250-262+空表:264-266） | 原料表供给态+DU 债全录 |
| B5 | 消费普查 | 14_consumption_census.md（九族矩阵+§二上架无客+§四该接未接+§五 CNS-01~14） | 因子 175/4、停牌/次新/竞价断链全录 |
| B6 | 账本与审计 | ulib3b_demand_gap_ledger.md:44-47（D19/D21/D22）、ulib3b_supply_relationship_ledger.md:57-63、trading_vision/2026-09-16-skeleton-coverage-audit.md:18,36,101-116、11_integrated_backtest_audit.md:26,54,72,324 | M-41/S 册/电态/000010.SH 全实锤 |
| B7 | 代码面 | signal_ashare/core/{candidate_pool_aggregator,pool_tier_maintenance,sector_conduction,environment_switch}.py、signal_fundamental/{selection_funnel,negative_veto,selection_confidence}.py、signal_ashare/screening/*、signal_ashare/{mainline_candidates,tradability_preflight}.py、strategy_pipeline/daily_gate_snapshot.py、pf_core/strategy_engine/framework_composer.py、ex_core/daban_load_producer.py、data/config/tasks.yaml:3422 | 码件全在+消费面=回测+唯一持久化先例实证 |
| B8 | 方法论口径 | 05_t0_and_strategy_library.md:12（新闻活跃度/市值维）、17_quantified_acceptance.md:33（五分位/十分位/n≥30）、archive/2026-09/design_memos/15_data_feature_layer_spec.md（特征仓库三层） | W3/W4/W6 口径真源锁定 |
| B9 | 板块线移交件 | sector_line/sector_layer_skeleton_v0.md（DDL 模式 §5）、sector_gap_list_and_construction_proposal.md:32,35,60（G6/G9/G15） | 上游边界+追认依赖+能力反查债 |
