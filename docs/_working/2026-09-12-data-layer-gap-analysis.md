---
ttl: task_bound
---

# ZephyrAlpha 数据分层体检报告（2026-09-12）

> 任务：①调研专业机构/量化社区的数据分层方法，对照 Owner 的 L1/L2/L3 三层分法；②逐层盘点项目数据家底，回答"财报研究模块/表格数据源/研报还缺不缺"。
> 证据来源：数据资产登记表 REG-DATAFLOW-001（sources 16 / datasets 226 / jobs 88）、字段字典 REG-FLD-001、ROOR、src/zephyr 代码扫描、tasks.yaml 调度清单、全网调研（出处见 §1）。

---

## 0. 一页结论（先看这里）

1. **你的三层分法方向是对的**——它就是行业的"内容轴"分法（行情 → 基本面/扩展 → 另类）。但机构实际用**两条轴**：内容轴之外还有一条"加工轴"（原始→标准化→因子→应用，即数据中台的 ODS/DWD/DWS/ADS）。咱们项目的治理体系其实已经在做加工轴的事，只是没起名字。
2. **L1 行情层 ≈95%**：K线全家桶（日/周/月/1-60min/复权/ETF/LOF/可转债/指数/板块880/期货/港美/币圈）+ 盘口竞价 + Level-2 逐笔 + 资金面（两融/北向/龙虎榜席位/大宗/宽度）+ 衍生品。超出多数个人与小型机构的配置。
3. **L2 扩展层：数据侧 ≈70% 完成，研究消费端 ≈30%**——这是最重要的结构性发现：
   - 财报**数据不缺**：c3_fundamental 25 张表（三大报表/财务指标/业绩预告/快报/审计意见/股东结构全家桶/主营构成）都在，且 PIT 查询层已建（pit_query.py，9 表白名单+as_of/embargo/survivorship 三公理）。
   - **缺的是"厨师"**：三大报表在 src 内没有直接下游消费者。基本面因子族目前只有 PE 类价值因子 1 个 + 业绩暴雷否决器 1 个 + LLM 财报三 Agent（testing）。
4. **研报：真缺，但没缺到底**。全项目登记 0 研报数据集，但有三处未接线雏形：tasks.yaml 的 research_report_incremental（东财研报元数据→写入 news_data 共表）、src/zephyr/alt_data/research_report_collector.py（DORMANT，需运行时注入 fetch_api）、src/zephyr/nlp/research_rating.py。缺的是：研报文本库 → 结构化解析（盈利预测/评级/目标价）→ 因子消费。
5. **表格数据源：通道不缺，付费广度缺**。20+ 个 provider 实现、~90 个 ingest 任务、19 个调度时段在跑；iFind 商业终端 2026-08-14 主动退役（#ARCH-DATA-IFIND-RETIRE-001，试用到期不续费）。所以这不是"遗漏"，是"取舍"——真问题是要不要为一致预期长历史付费（见下条）。
6. **最容易被忽略的隐性缺口：分析师预测表只有 2 个月历史**。c3_fundamental.analyst_forecast（DS-199）CH 实况仅 8 万行，分区 2026-07-01 起。一致预期是机构公认"第三大数据源"（行情、财务之后），预期修正/超预期/分歧度因子族目前**根本没法回测**。对比：同库 earnings_forecast（业绩预告）13 万行、历史到 1998 年。
7. **L3 另类层 ≈15%**：alt_data 包整体 DORMANT 占位（6 个模块仅 __init__，satellite_collector 空壳）。反而真正落地的边缘另类（天气/生猪产业链/人气榜/币圈影子/链上）都没挂在 alt_data 名下。专业警示：黑子私募实测卫星停车场类数据后因"合规+成本 vs 阿尔法不成正比"主动放弃（出处见 §1.3）——个人项目不建议追硬另类。
8. **隐藏的第四条轴（项目最强项）：数据治理 ≈90%**。数据资产登记表对标 OpenLineage、字段字典 16 域 259 条、PIT/幸存者偏差强制声明（E14）、known_data_gaps.yaml 缺口登记、前端数据监管页 v3（四色健康状态/宽度/深度/完整度/缺口面板）、90 任务 19 时段调度。这套东西达到机构数据中台形态，在个人项目里罕见。
9. **优先级建议**：P1-A 财报因子消费端（数据现成、PIT 现成，只差把菜做成菜）＞ P1-B 研报链路贯通 MVP（把三处雏形接成一条链）＞ P1-C 一致预期历史回补评估 ＞ P2 加工轴显性化登记、低成本另类试点。**回测生死线三件套（P0）不依赖任何新数据**，不用为回测启动补数据。

> 另：你开头提到"用标准研究版复现这篇研报并形成可审计的因子结论"——项目里没有叫"标准研究版"的工作流，本对话也没有附研报文件。如需复现某篇研报，请把研报（PDF/文字）发我，按 SOP-B 七步循环走台账归档。

---

## 1. 专业机构和量化社区怎么分层（全网调研）

### 1.1 内容轴（横向，按数据类型）——你的分法对标这条

| 来源 | 分类 |
|------|------|
| BigQuant 知识库 | 市场数据 / 基本面 / 宏观经济 / 技术分析 / 衍生品 / 替代数据 / 风险管理 / 合规与交易成本 / ESG（9 类） |
| arXiv 2025 综述《AI in Quantitative Investment》(2503.21422) | **numerical**（行情 quote + 基本面 fundamental）/ **relational**（产业链/供应链/概念等关系图谱，单独成类）/ **alternative**（文本/图像/语音多模态）/ **simulation**（合成数据）——4 类 |
| paperswithbacktest（对冲基金实践） | market（time bars / quote bars / tick / orderbook）/ fundamental / alternative（3 类） |
| 聚宽 JQData 目录 | 股票 / 行业概念 / 指数 / 宏观 / 期货 / 期权 / 场内外基金 / 技术指标 / 因子库 / Alpha101/191 / 舆情 / 债券 |
| 米筐 RQData 目录 | 同上 + **电商数据**（天猫/淘宝/京东）+ **舆情**（雪球/股吧）+ **财务 PIT API**（官方明示防前视偏差）+ 2500 宏观因子 |
| 朝阳永续 | **盈利预测数据 = 继行情、财务之后的国内第三大量化数据源**；本质是把卖方研报结构化（一致预期，2006 年注册商标） |

**另类数据的行业 6 子类**（Apify/DataSetIQ/alphanume 等）：① web 注意度与搜索 ② 社媒/新闻情绪 ③ 信用卡/交易流水 ④ 地理定位/客流 ⑤ 卫星遥感 ⑥ 网络爬虫（价格/招聘）+ 监管文件衍生。行业共识：另类数据"采集只占小头，清洗、PIT 对齐、合规才是工程大头"。

### 1.2 加工轴（纵向，按加工阶段）——你目前没有显性命名的一条轴

| 来源 | 分层 |
|------|------|
| 量化社区"数据中台"文章（dev.to/cnnetsun） | **ODS 原始层**（保留原貌可追溯）→ **DWD 标准化层**（统一字段命名）→ **DWS 因子层**（技术指标/Alpha/AI特征）→ **ADS 策略层**（直供回测/前端） |
| 博客园"量化 6 层数仓" | ODS → 清洗明细 → 聚合指标 → 公共模型 CDM → 业务应用 |
| 百亿量化私募（基金报报道） | 底部数据层 → 因子发现层 → 策略开发层 → 策略跟踪层 → 产品层 |

### 1.3 延迟轴（高频机构的第三条轴）+ 专业警示

- 黑子私募（sunspotfund）：实时极速层（Tick/Level2，当日生命周期）/ 近线缓存层（分钟级清洗）/ 历史存储层（完整历史+基本面+另类）。
- **同文案例**：该私募试过接入卫星图像"停车场车辆数/工地开工"跟踪周期股，最终因**合规风险+接入成本远超阿尔法提升而放弃**——"另类数据的接入、处理与合规成本，往往远超其带来的阿尔法提升"。
- QuantStudio（国内量化框架）强调财报数据三大纪律：**时点数据 PIT / 前视偏差 / 幸存者偏差**——财报数据"处理起来最复杂"，核心是公告期 vs 报告期的时点化查询。

### 1.4 对照结论

- 你的 L1/L2/L3 = 行业内容轴的 1/2/3 档，**分法成立且和主流一致**；产业链单独成类（arXiv 的 relational）和预期数据（朝阳永续第三源）是你 L2 里价值密度最高的两类，项目恰好都在建。
- 缺的不是"某一层数据"，而是：①加工轴没有显性命名（实际在做）②L2 的"数据→因子→回测证据"闭环（消费端）③研报这一条链。

---

## 2. 逐层体检（项目现状）

### 2.1 L1 行情层 —— ≈95%

**已有**（ClickHouse c1_market 96 张表，中文名真源=api_server._TABLE_ZH）：
- K线：日/周/月（不复权+后复权）、1/5/15/30/60 分钟、ETF/LOF 分钟全家桶、可转债、指数、板块（880/盘中）、期货、港股、美股、全球、币圈现货
- 盘口与微观：tick_data（**3 秒快照 Tick，含买卖一档**，CH 实况 84.2 亿行、2025-01 起——**非逐笔**；登记表 format_summary 原"Tick 逐笔"为误标，2026-09-12 勘正）、realtime_snapshot、集合竞价盘口/快照、涨跌停明细/价格、大宗交易（明细）。**Level-2 逐笔（逐笔委托/成交）当前没有**：l2_tick_snapshot 任务 disabled（tasks.yaml:1633，#ARCH-DATA-014 需付费 L2 行情权限；miniQMT 通道退役后桥无 L2），l2_tick 表无数据流——Owner 2026-09-12 勘正，此前误记"tick_data（L2 逐笔）"
- 资金面：money_flow、两融、北向持仓快照、港股通资金流、龙虎榜+席位、市场宽度快照、个股人气榜
- 参考数据：股票清单/基础信息/ST、指数清单/成分/权重/估值、复权因子、交易日历（A/港）、技术指标、每日估值、全A等权自算指数（kline_index_calc，防幸存者偏差）

**小缺口**：美股数据深度（known_data_gaps.yaml 已登记）；期货夜盘时段覆盖需巡检。对日线为主+分钟级的当前策略形态，**不构成瓶颈**。

### 2.2 L2 扩展层 —— 数据 ≈70% / 消费 ≈30%

**财报（数据侧齐备，机构级）**：c3_fundamental 25 张表 = 三大报表（income_statement/balance_sheet/cashflow_statement）+ financial_indicator + 业绩预告/快报/披露计划 + 审计意见 + 股东结构全家桶（top10 流通/普通股东、股东人数、股质明细/汇总、限售、配股、解禁）+ 主营构成 + 行业分类补充。**PIT 查询层已建**：src/zephyr/data/pit_query.py 白名单 9 表（四财报+快报/审计/业绩预测/分红/回购），as_of+embargo+survivorship 三公理，消费方=backtest pit_manager/data_handler——这正是 QuantStudio 强调的财报三大纪律，咱们已经工程化。

**分析师预期（最大的隐性缺口）**：analyst_forecast（DS-199，akshare 源）仅 8 万行、历史 2026-07-01 起 ≈2 个月；对照机构（朝阳永续 19 年积累、覆盖度全A 75%+）——预期修正/超预期/分歧度/目标价因子族全部做不了回测。同域 earnings_forecast（业绩预告，miniQMT 源）13 万行、1998 年起，历史深度合格。

**产业链全景图（在建，对标"关系型数据"）**：PostgreSQL ig_chain/ig_node/ig_edge/ig_node_company 四表族（839 链/3328 节点/公司映射在扩）+ src/zephyr/intelligence/chain_impact_stream.py（事件→链传导 2 跳 BFS、strict PIT）+ chain_impact_resolver + news_chain_node_linker + event_chain_causal_graph。方向正确，正在扩表期。

**事件/新闻/宏观**：事件日历 12 类（REG-EVT-001，全量 PIT 规则）+ event_* 模块 8 个（IPO 抽血/地缘/龙虎榜事件/异常/漏斗/评分/因子矩阵/链式因果）；news_data（RSS：财联社+东财 5 类研报 RSS）→ news_sentiment_window/analyzer + news_symbol_linker；macro_data（CPI/PPI/PMI/GDP/社融/M2/LPR 十债汇率）+ FRED 美国 22 序列 + EIA 能源 + 和风天气。宏观表（DS-101）status=candidate，且 iFind EDB 配额退役后宏观宽表 0 行——宏观侧实际偏薄。

**研报（三处雏形，未成链）**：① tasks.yaml research_report_incremental（akshare 东财研报元数据→写 c3_fundamental.news_data 共表）② src/zephyr/alt_data/research_report_collector.py（MOD-ALT-009，元数据采集+评级变动事件，DORMANT：需运行时注入 fetch_api，未见装配）③ src/zephyr/nlp/research_rating.py。**缺**：独立研报物理表、研报文本库、结构化解析（盈利预测/评级/目标价）、因子消费。

**消费端（"厨师"在哪）**：signal_fundamental（业绩暴雷 negative_veto 否决器——唯一真实消费者）；llm_fundamental_analysis（财报质量/新闻政策/综合裁决三 Agent，testing，仅信号不下单）；factor/value_factor.py 只有 PE 类。**三大报表+financial_indicator 在 src 内 0 直接下游**——字段字典登记了、PIT 建了、菜齐了，菜还没炒。

### 2.3 L3 另类层 —— ≈15%

- **已落地的边缘另类（未挂 alt_data 名下）**：weather_data（和风）、hog_futures_core/hog_province_spot/hog_spot_index（生猪产业链垂直数据）、stock_hot_rank（社交热度类）、crypto_kline_daily + crypto_shadow_gate（币圈影子）、macro 事件。这些其实已经是"低成本另类"的正确形态。
- **alt_data 包整体 DORMANT**：6 个模块仅 __init__ 占位，satellite_collector 空壳，唯一非空壳 research_report_collector 未接线。另类数据集登记 0。
- **专业裁决**：对个人项目，卫星/停车场/工厂灯光级硬另类不建议做（黑子私募案例）；正确路径是 ①把 L2 做深 ②低成本 web 衍生数据试点（电商价格/招聘/搜索热度——米筐把电商数据做成标准目录项可参考）。**L3 不是当前瓶颈，排在财报消费端和研报链路之后。**

### 2.4 第四条轴：数据治理（≈90%，机构级，个人项目罕见）

数据资产登记表 226 数据集/16 源/88 任务（三实体模型对标 OpenLineage）；字段字典 16 域 259 条（PIT 性质/复权口径/质量规则）；E14 幸存者偏差与 PIT 强制声明（财报类 MUST）；license_type/latency_profile 合规画像；known_data_gaps.yaml 主动登记缺口（美股深度/红利断供等）；tasks.yaml ~90 任务 + schedule.yaml 19 时段 + 21+ provider 实现 + 集成器 7 子命令；前端数据监管页 v3 四色健康/宽度/深度/完整度/缺口面板。**这就是行业说的"数据中台/加工轴"，只是没有显性叫这个名字。**

---

## 3. 缺什么（优先级行动清单）

| 级别 | 事项 | 理由 |
|------|------|------|
| — | 回测生死线 P0 三件套**不需要等任何新数据** | L1+已有治理足够支撑 SOP-B 启动 |
| **P1-A** | **财报因子消费端**：三大报表+financial_indicator → 基本面因子族（成长/质量/盈利/应计/现金流质量）→ 走 SOP-B 回测出证据 | 数据现成、PIT 现成，投入产出比最高；161 条因子登记表里基本面族回填证据 |
| **P1-B** | **研报链路贯通 MVP**：research_report_collector 接线 → 独立研报表 → 结构化（评级/目标价/盈利预测）→ 与 analyst_forecast 融合 → LLM 观点提取（复用 intelligence 域现成基建） | 三处雏形已在，缺的是"接成一条链"；朝阳永续模式证明这是第三大源 |
| **P1-C** | **一致预期历史回补**：评估 akshare 历史接口/免费源，把 analyst_forecast 从 2 个月回补到 5 年+ | 没有历史，预期因子族全部无法回测；若免费源确实拿不到，再评估付费（这是 iFind 退役后唯一值得重新花钱的点） |
| P2-A | 加工轴显性化：在 ROOR/数据资产登记表头加一段 ODS/DWD/DWS/ADS 映射说明（不重构，纯登记） | 治理价值显性化，成本半天 |
| P2-B | 低成本另类试点：电商价格/招聘热度等 web 衍生，纳入 alt_data 包唤醒第一批 | 唤醒 DORMANT 包；避开卫星级合规深水区 |
| 巡检 | known_data_gaps.yaml 存量缺口按节奏消化（美股深度/红利断供） | 已有机制，保持 |

**一句话回答你的三个猜测**：财报模块——**数据不缺、查询不缺，缺因子消费端**；表格数据源——**通道不缺，付费广度缺（iFind 已退役，是取舍不是遗漏）**；研报——**真缺，但有三处未接线雏形，缺文本库+结构化+因子化**。

---

## 4. 证据清单

- 数据资产登记表：docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml（v1.6.x，sources 16/datasets 226/jobs 88；DS-199/204/209 条目含 CH 实况行数）
- 字段字典：…/field_dictionary.yaml（REG-FLD-001，16 域 259 条）；ROOR：docs/registry_of_registries.yaml
- 物理表中文名真源：src/zephyr/frontend/dashboard/api_server.py::_TABLE_ZH（122 张）
- PIT：src/zephyr/data/pit_query.py（9 表白名单+三公理）；回测消费：src/zephyr/backtest/pit_manager.py、data_handler.py
- 研报雏形：src/zephyr/alt_data/research_report_collector.py（DORMANT）；src/zephyr/nlp/research_rating.py；tasks.yaml research_report_incremental
- 基本面消费端：src/zephyr/signal_fundamental/、src/zephyr/intelligence/llm_fundamental_analysis.py（三 Agent，testing）、src/zephyr/factor/value_factor.py
- 产业链：ig_* PG 四表族（839 链/3328 节点）；src/zephyr/intelligence/chain_impact_stream.py / chain_impact_resolver.py / news_chain_node_linker.py
- 另类占位：src/zephyr/alt_data/（6 模块 DORMANT，satellite 空壳）；已落地另类：weather_data/hog_*/stock_hot_rank/crypto_*（c1_market）
- 调度：config 数据任务清单 tasks.yaml（~90 任务）、schedule.yaml（19 时段）、providers 21+ 实现（src/zephyr/data/implementations/）
- 外部调研出处：BigQuant wiki；arXiv 2503.21422；paperswithbacktest blog；聚宽 joinquant.com/data；米筐 ricequant.com；朝阳永续 go-goal.com；黑子私募 sunspotfund.com/dynamic/66.html；数据中台文章（dev.to/cnnetsun）；QuantStudio 文档 qsdoc.readthedocs.io
