---
ttl: task_bound
completes_when: 总筹消费裁决后归档
title: 37红源线实现优先级矩阵 v1（TDM 体检后续·车道D备料批）
owner: st-fd-srcline-20261005
generation: machine_generated
task_id: tdm-fd-srcline
source_map: config/trading_decision_map.yaml
source_registry: docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml
red_nodes_measured: 38
red_nodes_mother_order: "37 + A17 = 38（实测吻合，0 漏行）"
needs_chief_rows: 4
top5: [TDM-E-L9-A01, TDM-E-L9-A03, TDM-E-L9-A06, TDM-E-L9-A09, TDM-E-L9-A02]
priority_dist: {P0: 6, P1: 18, P2: 2, P3: 12}
---

# 37红源线实现优先级矩阵 v1

> 车道D备料批（sid=st-fd-srcline-20261005，task_id=tdm-fd-srcline）。本文为**只读分析产物**：未改图、未施工、未改任何代码。真源引用：TDM=`config/trading_decision_map.yaml`（schema 见其 nodes/edges）、DS 册=`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（334 datasets/18 sources/122 jobs）。
>
> **口径**：E-L9 层全部含 `red_reason` 字段节点（含 red_reason 值=by_ref_design 者）。母单口径 37+A17；**实测 38，吻合**（A17 为 2026-10-05 体检批新增，其 red_reason 值即 `by_ref_design`）。L9 层全表 45 节点中红 38、非红 7（AGG/E1/D1 等已建成非红节点不入矩阵）。全仓另有非 L9 层红节点 25 个（terminal/structural 流程节点），不在本批范围。
>
> **红节点构成（red_reason 值分布）**：by_ref_design=17（A01–A17 全部）、not_built=15（B01–B10、C01–C03、G5、V2）、structural=5（D2、G1、G2、G4、Z1）、pending_gate=1（E2）。

## 0. 打分规则（四维，各 0–2 分，总分 8）

| 维度 | 2 分 | 1 分 | 0 分 |
|------|------|------|------|
| R 数据就绪度 | 主数据集 active/production（在册且有 CH 生产表实测行数）或源+采集器双在产 | 源/表部分在产（DS 册缺条目、或依赖缺口、或仅共表） | 无渠道未接（B/C 档口径） |
| D 下游消费者 | 出边 ≥2 | 出边 =1 | 出边 =0 |
| M materiality | critical | normal | low（本批无） |
| C 施工复杂度（越低越高分） | 低=采集器/表全在产，剩挂线/聚合 | 中=有可复用底座但需实质装配/桥接 | 高=全新外部源采集器（B/C 档口径） |

**综合优先级**：总分 ≥7=P0；5–6=P1；3–4=P2；≤2=P3。C 档政策挂起（纪要定案不入批）机械落 P3，不另行加权重排。打分为机械规则，无人工调权；Top5 取源线节点（sensor）内总分降序，同分依次按 materiality、出边数、node_id 破平。

## 1. 矩阵（38 行，按 node_id 排序，实测 0 漏行）

| 源线节点 | name_zh | red_reason 摘句 | 数据就绪度（档+依据） | 下游消费者数（出边） | materiality | 施工复杂度（档+依据） | 综合优先级 | needs_chief |
|---|---|---|---|---|---|---|---|---|
| TDM-E-L9-A01 | 源线·日线/分钟行情 | by_ref_design（A档在产，DS锚=MINIQMT/TUSHARE/BAOSTOCK/TDX，全表挂接密度最高线） | 高：DS-150 日K active（CH 1002万行，1990-12 起）+DS-152 后复权 active+DS-144~148 分钟K 全 active（1分K 14.6 亿行）；DS-002 deprecated 已由上述表承接 | 2（→L9-AGG、L3-02） | critical | 低：miniqmt_provider kline_daily/1min/5min 等 incremental 任务全在产，剩挂线聚合 | **P0**（8） | — |
| TDM-E-L9-A02 | 源线·Tick分笔 | by_ref_design（DS锚=TICKFLOW/TDX/BAIDUYUN，滑点/冲击近独占来源） | 高：DS-195 Tick逐笔 active+DS-306 五档深度 active（CH 1.3 亿行）；注：TDX 分笔仅近交易日，历史存量断档不可补 | 2（→L9-AGG、L4-14） | critical | 中：ch_tick_kline/tick_depth_backfill 在产，但 PIT 历史断档→增量窗口与断档对账工程 | **P0**（7） | — |
| TDM-E-L9-A03 | 源线·板块/概念指数 | by_ref_design（DS锚=TQCENTER/TDX/AKSHARE） | 高：DS-117 概念板块 active+DS-119 概念行业 active（CH 各 375 行）+SRC-TQCENTER-001 active（880xxx 自动调度）+SRC-TDX-001 active | 2（→L9-AGG、L2-01-2） | critical | 低：tqcenter_provider/tdx_provider/akshare_provider 在产 | **P0**（8） | — |
| TDM-E-L9-A04 | 源线·估值 | by_ref_design（DS锚=AKSHARE） | 高：DS-123 每日估值 active（CH 21 万行）+DS-141 指数估值 active（8101 行，2010 起） | 1（→L9-AGG） | normal | 低：daily_valuation_incremental 等任务在产 | P1（6） | — |
| TDM-E-L9-A05 | 源线·财务 | by_ref_design（DS锚=TUSHARE/BAOSTOCK，公告日 PIT） | 高：DS-208 财务指标 active（39 万行，1970 起）+DS-232 财报派生层 active（pit_available=true） | 1（→L9-AGG） | normal | 低：financial_indicator_incremental+build_financial_derived 在产 | P1（6） | — |
| TDM-E-L9-A06 | 源线·资金流 | by_ref_design（DS锚=TUSHARE，日度聚合盘后落定） | 高：akshare_provider 个股资金流任务在产（写 c1_market.money_flow，`src/zephyr/data/implementations/akshare_provider.py` L2222+）+DS-300 大盘资金流 active+DS-311 板块资金流 active；DS-016 仍 candidate（升档需求见 §4） | 2（→L9-AGG、L2-01-4） | critical | 低：JOB-015/JOB-080 资金面任务在产；大盘接口 2026-09-18 断供已换道混合回填（代码留痕） | **P0**（8） | — |
| TDM-E-L9-A07 | 源线·千股千评 | by_ref_design（DS锚=AKSHARE-ALT，评级快照日更） | 高：DS-230 千股千评日快照 active（接口仅当日无历史，日更自积） | 1（→L9-AGG） | normal | 低：akshare_alt_provider alt_stock_comment_snapshot 在产 | P1（6） | — |
| TDM-E-L9-A08 | 源线·航运运价BDI | by_ref_design（DS锚=AKSHARE-ALT，发布日锚定） | 高：DS-231 航运运价长表 active（1988-10 起含日涨跌幅+国内货运指数约 2006 起） | 1（→L9-AGG） | normal | 低：alt_shipping_index_incremental 日度增量在产 | P1（6） | — |
| TDM-E-L9-A09 | 源线·财经快讯情绪 | by_ref_design（DS锚=CLS/EASTMONEY_NEWS/RSS，快讯时戳不可回填） | 高：DS-104 新闻快讯 production（pit_available=true，多源 event_driven）+DS-107 情绪窗口聚合 testing；覆盖缺口 2024-08~2026-06 仅细流（月千级） | 2（→L9-AGG、L1-S0-1） | critical | 低：cls/eastmoney_news/rss 三 provider 全在产；剩 DS-107 聚合层 testing→production 升档 | **P0**（8） | — |
| TDM-E-L9-A10 | 源线·国际宏观 | by_ref_design（DS锚=FRED，修订挂 vintage） | 中：SRC-FRED-001 active（22 序列，2026-08-04 新增）+fred_provider 在产写 c1_market.macro_data；但 DS 册无 FRED 数据集条目，且地图 data_refs=[DS-101]=中国宏观（akshare），锚与节点语义不匹配 | 1（→L9-AGG） | normal | 低：fred_provider.py 在产（`src/zephyr/data/implementations/fred_provider.py`，MOD-DAT-fred_ingest） | P1（5） | **是**（DS 映射+地图 data_refs 校准） |
| TDM-E-L9-A11 | 源线·能源库存 | by_ref_design（DS锚=EIA，周报发布时点锚定） | 中：SRC-EIA-001 active（石油库存/价格/天然气）+eia_provider 在产共表 c1_market.macro_data（indicator_name 前缀区分）；DS 册无 EIA 数据集条目 | 1（→L9-AGG） | normal | 低：eia_provider.py 在产（含代理探测） | P1（5） | **是**（DS 编号登记） |
| TDM-E-L9-A12 | 源线·天气 | by_ref_design（DS锚=QWEATHER，观测时戳即落定） | 高：DS-198 天气数据 active（CH 6200 行，40 城实时+7 天预报每日自积）+DS-237 深圳预警流 degraded（源侧止于 2020-09，历史档案定位） | 1（→L9-AGG） | normal | 低：qweather_provider 在产 | P1（6） | — |
| TDM-E-L9-A13 | 源线·股东户数 | by_ref_design（DS锚=EASTMONEY_DATACENTER，披露日锚定） | 高：DS-218 股东人数 active（CH 50 万行，1992-12 起） | 1（→L9-AGG） | normal | 低：shareholder_incremental 在产 | P1（6） | — |
| TDM-E-L9-A14 | 源线·互动易问答 | by_ref_design（DS锚=IRM，问答时戳不可回填） | 高：DS-303 irm_interactive_qa active（C6 原文层）+DS-334 IRM 问答抽取 active（CH 74 行）+irm_provider 在产 | 1（→L9-AGG） | normal | 低：irm_provider+抽取链在产 | P1（6） | — |
| TDM-E-L9-A15 | 源线·加密永续/费率 | by_ref_design（DS锚=HYPERLIQUID，8 小时费率周期锚定） | 高：DS-281~284 Hyperliquid 四表 active（费率逐小时/清算流/OI 快照/永续快照，日更自积）+hyperliquid_provider 在产；OKX 已 degraded（DNS 阻断降级预案） | 2（→L9-AGG、L1-S0） | normal | 低：hyperliquid_provider 在产 | **P0**（7，下缘） | — |
| TDM-E-L9-A16 | 源线·投入产出 | by_ref_design（DS锚=IO_TABLE 国家统计局，2020 版 153 部门口径锚定） | 中：ig_io_edge 16,859 条已导入（G5 口径）但 DS 册无对应数据集条目；头号缺口=部门码与 ig_node 两套 id 体系，边 100% 挂零（altdata_line WP-0.5） | 1（→L9-AGG） | normal | 中：scripts/industry_graph/io_ingest.py 在产，剩 id 消歧桥=中等工程量 | P2（4） | **是**（消歧桥施工裁决） |
| TDM-E-L9-A17 | 源线·卖方研报 | by_ref_design（2026-10-05 体检批新增；唯一源线级设计缺口；研报评级/目标价领先性） | 高：DS-228 券商研报明细 active（东财研报中心，research_nightly 时段）+DS-229 一致预期 active+DS-275 历史修复双轨 active+DS-304 PDF 提取 active；research_report_collector=MOD-ALT-009 maturity=production（模块头已带 module_id） | **0（未挂线）** | normal | 低：采集与派生链全在产，剩 TDM 挂线动作 | P1（5） | **是**（挂线涉写图，裁决时点） |
| TDM-E-L9-B01 | 源线·卫星影像 | not_built（B档外采：Copernicus 免费/Planet 商业；接入=资金门位） | 低：DS 册 0 命中，渠道未接 PIT 未评估 | 1（→L9-AGG） | normal | 高：全新外部源采集器（遥感数据量大、Planet 付费） | P3（2） | —（B档资金门位统一见 §4） |
| TDM-E-L9-B02 | 源线·美国官方天气/海洋 | not_built（B档外采：NWS API 免费） | 低：0 命中 | 1（→L9-AGG） | normal | 高：全新采集器（API 免费但接入工程全新） | P3（2） | — |
| TDM-E-L9-B03 | 源线·招聘JD | not_built（B档外采：智联招聘抓取） | 低：0 命中（全仓无招聘采集代码） | 1（→L9-AGG） | normal | 高：全新采集器+反爬/合规风险 | P3（2） | — |
| TDM-E-L9-B04 | 源线·电商价格 | not_built（B档外采：Keepa 付费 API） | 低：0 命中 | 1（→L9-AGG） | normal | 高：全新采集器+付费 | P3（2） | — |
| TDM-E-L9-B05 | 源线·招投标 | not_built（B档外采：政采网/公共资源平台） | 低：0 命中 | 1（→L9-AGG） | normal | 高：全新采集器（多平台异构） | P3（2） | — |
| TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | not_built（B档外采：Reddit/X API） | 低：0 命中 | 1（→L9-AGG） | normal | 高：全新采集器+API 付费/地域限制 | P3（2） | — |
| TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | not_built（B档外采：雪球强反爬） | 低：0 命中（DS-230 千股千评仅为股吧关注度代理，非发帖文本） | 1（→L9-AGG） | normal | 中：判定核心 SocialSentimentCollector（MOD-ALT-001）已 design 在库，fetcher/scorer/sink 装配位齐，缺雪球页面抓取 fetcher（强反爬） | P2（3） | — |
| TDM-E-L9-B08 | 源线·APP榜单 | not_built（B档外采：七麦会员/SensorTower） | 低：0 命中 | 1（→L9-AGG） | normal | 高：全新采集器+双渠道均付费 | P3（2） | — |
| TDM-E-L9-B09 | 源线·进出口贸易 | not_built（B档外采：UN Comtrade 免费 API） | 低：0 命中（DS-294 海关进出口宽表为月度总量，非分商品量价，仅部分覆盖） | 1（→L9-AGG） | normal | 高：全新采集器（免费 API 但增量/国别维度工程全新） | P3（2） | — |
| TDM-E-L9-B10 | 源线·信用卡/支付消费 | not_built（B档外采：SpendingPulse proxy） | 低：0 命中（无正式渠道，proxy 定位） | 1（→L9-AGG） | normal | 高：无正式源，需 proxy 建模+全新采集器 | P3（2） | — |
| TDM-E-L9-C01 | 源线·实时门店客流 | not_built（C档无渠道） | 低：0 命中 | 1（→L9-AGG） | normal | 高：想得到无机械接入渠道 | P3（2，政策挂起不入批） | — |
| TDM-E-L9-C02 | 源线·银行网点/信贷活跃 | not_built（C档无渠道） | 低：0 命中（DS-290 社融/M1/M2 宽表为宏观月度，非草根观测） | 1（→L9-AGG） | normal | 高：C档无渠道 | P3（2，政策挂起不入批） | — |
| TDM-E-L9-C03 | 源线·直播电商实时成交 | not_built（C档无正式渠道） | 低：0 命中 | 1（→L9-AGG） | normal | 高：C档无渠道 | P3（2，政策挂起不入批） | — |
| TDM-E-L9-D2 | 决策假设·登记与考试方案 | structural（入表即挂 exam_plan，一问一考；禁临场改题） | 高：meta_question 三表在产（PG 283 问）+meta_question_registry.py 在树（`src/zephyr/governance/meta_question/`）；registry 代码随 B7v2 尾批落地（worktree 在飞） | 1（→E1，sequence） | normal | 低：载体+代码面在产/落地中，剩执行面收口 | P1（6） | — |
| TDM-E-L9-E2 | 验证·结论回传与修正 | pending_gate（今日考试结论次日方可进下游；时间分层铁律） | 中：依赖 D2/E1 链先行，反馈数据边未通 | 3（→F-C3-02、L9-D1 feedback、E-L0 feedback） | normal | 中：回传边三向装配，判定台账表族（DS-285~288）已 DDL 在册 | P1（5） | — |
| TDM-E-L9-G1 | 图谱·Zephyr产业链 | structural（传导图谱供给侧；873 链/5560 节点/1726 结构边） | 高：ig_*14 表在产（PG depgraph 图谱域）；583/873 链有链内传导边；缺口=ig_entity_code_map 消歧桥仅 2 行（假边风险） | 2（→L2-06、L3-01） | normal | 中：消歧桥补齐=中等工程（涉实体消歧） | P1（6） | — |
| TDM-E-L9-G2 | 图谱·ChainKnowledgeGraph事实层 | structural（已导入 ig_fact，source=ckg_2021，PIT 诚实；静态快照仅结构先验） | 高：ig_fact 已导入（4654 上市公司/95559 产品，as_of=2021-10-26） | 1（→G1） | normal | 低：静态快照已就位，红点=structural 口径声明，解除动作轻 | P1（6） | — |
| TDM-E-L9-G4 | 图谱·概念/题材 | structural（stock_concept as_of 2026-09-14 THS 导出；概念≠产业链硬边界） | 高：stock_concept 已导入（静态快照）；W6 行数实测待补（行情落库前置） | 1（→L1-AGG） | normal | 低：导入完成，剩 W6 实测动作 | P1（6） | — |
| TDM-E-L9-G5 | 图谱·投入产出传导 | not_built（ig_io_edge 16,859 条已导但头号缺口=两套 id 挂零） | 中：ig_io_edge 16,859 条（2020 版 153 部门直接消耗系数）已入库，边 100% 挂零不可消费 | 2（→L1-S0、L9-D1） | normal | 中：部门码↔ig_node 消歧桥（与 A16 同一缺口，合并施工） | P1（5） | — |
| TDM-E-L9-V2 | 状态变量快照·情绪 | not_built（情绪聚合器=独立对话未建，纪要 §8.3 定案不代建；T-1 快照带时戳落台） | 中：DS-307 情绪指数 active（CH 8655 行）+DS-107 聚合 testing，但六段相位 T-1 快照未落台 | 2（→L2-05、X-S1-04） | normal | 中：底座 MOD-ALT-EMOTION-INDEX-BUILDER experimental 在树，聚合装配+落台待独立对话 | P1（5） | —（开话裁决见 §4） |
| TDM-E-L9-Z1 | 治理·问题治理与状态机 | structural（draft→…→退役十态；墓碑 q_id 不复用；乐观锁 version） | 高：meta_question 三表+审计双轨在产；载体真源齐 | 1（→L9-AGG broadcast） | normal | 中：十态状态机强制执行面（机检/gate 化）=中等 | P1（5） | — |

**分布核对**：P0=6（A01/A02/A03/A06/A09/A15）；P1=18（A04、A05、A07、A08、A10、A11、A12、A13、A14、A17、D2、E2、G1、G2、G4、G5、V2、Z1）；P2=2（A16、B07）；P3=12（B01–B06、B08–B10、C01–C03）。合计 6+18+2+12=38 ✓。

**Top5 选出**（源线 sensor 内总分降序，同分按 materiality→出边→node_id 破平）：**A01（8）> A03（8）> A06（8）> A09（8）> A02（7，critical 破平胜 A15）**。A15（7 分）为第 6 名备选，若总筹对跨市场预警线加权可顶替。

## 2. Top5 施工规格草案（半页/线；备料供总筹裁决，本批未施工）

> 时区规范统一：所有落库时间戳 `DateTime64(3)` + 显式时区（`Asia/Shanghai`），禁 `datetime.now()`/`time.time()`（RULE-SCHEMA-TZ）。挂手节点均指 TDM 图内 node_id，**挂线动作涉写图，须总筹批准后由施工班执行**。

### 2.1 TDM-E-L9-A01 源线·日线/分钟行情（P0，8 分）

- **数据源**：miniQMT 实盘行情终端（SRC-QMT-001 active，主力源，确定性=高，已签约在产）；修复/回补口=tushare+baostock（SRC-BAOSTOCK-001 active，滞后 1 周）；复权因子独立口=miniqmt adj_factor（DS-111 active）。
- **采集**：日 K=daily_kline 时段日度增量（盘后）；分钟 K=intraday_minute 时段（1/5/15/30/60 分五粒度）；存量已实测：日 K 1002 万行（1990-12 起、431 parts）、1 分 K 14.6 亿行（2021-09 起）。增量水位=分区日期+行数对账（现有任务已带）。
- **标准化**：真源表=schemas/categories/kline/（market_kline_daily / market_kline_daily_hfq / market_kline_1min~60min，DDL-as-Code）；要点=(symbol, ts DateTime64(3,'Asia/Shanghai'), ohlcv, amount)；复权因子禁进 PIT 窗（地图 A01 note 铁律），后复权价独立成表（DS-152）不混列。
- **判据输出接口**：挂手=TDM-E-L9-AGG（feed, hours）+TDM-E-L3-02（feed, hours）；输出字段=(symbol, trade_date, close, hfq_close, pct_chg, turnover)；消费方=L3 价量趋势/动量因子族、L2 板块强弱聚合、全表挂接密度最高线（下游 2 出边均为主干消费者）。

### 2.2 TDM-E-L9-A03 源线·板块/概念指数（P0，8 分）

- **数据源**：通达信中心 TQCENTER 880xxx 板块日 K/成分/实时快照（SRC-TQCENTER-001 active，2026-07-30 起自动调度，确定性=高）；TDX TCP 直连盘中分钟（SRC-TDX-001 active）；akshare 概念板块/概念行业（DS-117/119 active 旁证）。
- **采集**：realtime 快照（盘中 0d 时滞）+板块日 K 盘后增量；概念成分随披露更新（日频）；存量=CH 概念 375 行（2026-09-03 system.parts 实测，日更自积中）。
- **标准化**：板块指数表（board_code, ts DateTime64(3,'Asia/Shanghai'), ohlc, amount, 成分数）+成分映射长表（board_code, symbol, in_date, out_date）；概念≠产业链硬边界（概念型链名禁入 ig_chain，G4 边界铁律）。
- **判据输出接口**：挂手=TDM-E-L9-AGG（feed, 0d）+TDM-E-L2-01-2（feed, 0d）；输出字段=(board_code, trade_date, board_pct_chg, rel_strength, members)；消费方=L2 板块选择（轮动/强弱持续）、L1 情绪聚合、G4 概念标签面交叉。

### 2.3 TDM-E-L9-A06 源线·资金流（P0，8 分）

- **数据源**：akshare 东财个股资金流（stock_individual_fund_flow 语义，经 SRC-AKSHARE-001 active，确定性=高）；大盘四档净流入=东财 CDN（注意 2026-09-18 起 stock_market_fund_flow 全量 RemoteDisconnected 断供，已换道混合回填，代码留痕 `akshare_provider.py` L204+）；板块资金流 DS-311 active。
- **采集**：daily 盘后（hours 时滞）；增量按交易日；存量=c1_market.money_flow 在产（源注册册 jobs 时段 daily_capital/nightly）；大盘 DS-300 已实测 120 行起步（2026-09-20）。
- **标准化**：money_flow 表（symbol, ts DateTime64(3,'Asia/Shanghai'), main/super/large/medium/small 净额与净占比）；日度聚合盘后落定不修订（PIT 铁律）；DS-016 candidate 建议随本线施工升 active。
- **判据输出接口**：挂手=TDM-E-L9-AGG（feed, hours）+TDM-E-L2-01-4（feed, hours）；输出字段=(symbol, trade_date, main_net_inflow, main_ratio, consec_days)；消费方=L2 板块选择资金面、L9-AGG 主干、L4 风险侧（主力撤退信号）。

### 2.4 TDM-E-L9-A09 源线·财经快讯情绪（P0，8 分）

- **数据源**：财联社电报（SRC-CLS-001 active，HTTP 直连）+东财 7x24 快讯（SRC-EASTMONEY-001 active）+RSS 聚合 8 源（SRC-RSS-001 active：36氪/钛媒体/华尔街见闻等）；确定性=高（三源互备）。
- **采集**：realtime event_driven（0d 时滞）；存量缺口：2024-08~2026-06 仅 akshare 细流（月千级），多源全量直播 2026-07 上线——历史段不可回填（PIT 时戳不可回填铁律），向前增量为主。
- **标准化**：news 主表（news_id 锚定 SCD 语义，ts DateTime64(3,'Asia/Shanghai'), source, title, content_ref, symbols）→ DS-107 情绪窗口聚合（夜间窗=前一交易日 18:00 含→交易日 08:00 不含，1h 整点窗可选；sentiment_index∈[-1,1]+正/负/中性计数+top_events_json；data_source=rule/llm 双轨留痕）；聚合窗口须右闭（地图 note）。
- **判据输出接口**：挂手=TDM-E-L9-AGG（feed, 0d）+TDM-E-L1-S0-1（feed, 0d）；输出字段=(window_start, window_end, sentiment_index, pos_cnt, neg_cnt, top_events_json)；消费方=L1 情绪聚合（六段相位输入）、V2 状态快照（T-1 落台）、L2 题材催化。

### 2.5 TDM-E-L9-A02 源线·Tick分笔（P0，7 分）

- **数据源**：miniQMT 逐笔/快照（SRC-QMT-001 active）+mootdx/TDX TCP 直连分笔（SRC-TDX-001 active，bestip 自动选速）；美股侧 TickFlow（SRC-TICKFLOW-001 active）不属本线 cn_a 口径；确定性=高（在产）但历史依赖包断档（百度云包止于断档点）不可补。
- **采集**：realtime 盘中（0d 时滞）；TDX 分笔仅近交易日→**存量扩张唯一路径=向前日积**；增量对账=每日分区行数+五档深度交叉核。存量实测：DS-195 Tick 逐笔 active+DS-306 五档深度 1.3 亿行（2026-10-01 system.tables）。
- **标准化**：tick 逐笔表（symbol, ts DateTime64(3,'Asia/Shanghai'), price, volume, bs_flag）+五档深度表（bid1-5/ask1-5 价量）；滑点/冲击衍生（vwap 偏差、冲击成本曲线）为下游派生不进原始层；PIT=分笔落定不修订。
- **判据输出接口**：挂手=TDM-E-L9-AGG（feed, 0d）+TDM-E-L4-14（feed, hours）；输出字段=(symbol, trade_date, tick_cnt, adv20_impact, slippage_p50/p90)；消费方=L4 执行域（冲击成本/滑点模型近独占来源）、L9-AGG 主干。

## 3. 与母单口径差异说明

- 母单口径"37 个+A17"：实测 E-L9 红节点 38 个=A17 在列（其 red_reason 字段值即 `by_ref_design`，与"字段含 red_reason 或 by_ref_design"两读法等价），**零差异**。
- by_ref_design 读法说明：本图无独立 `by_ref_design` 字段，该词仅以 red_reason 取值出现（17 处，全 A 档）；按"red_reason 字段存在"口径同为 38。
- 非 L9 层另有 25 个红节点（E-FLOW/P-FLOW/X-FLOW/F-FLOW terminal、L2/L3/L4 structural 等），属地图其他层红线，不在"37 红源线"范围，未计入矩阵。

## 4. needs_chief 清单（4 行标记 + 3 项政策级门位）

| # | 对象 | 待裁决内容 |
|---|------|-----------|
| 1 | A10 国际宏观 | 地图 data_refs=[DS-101]（中国宏观/akshare）与节点语义（国际宏观/FRED）不匹配；DS 册缺 FRED 数据集条目（源与 provider 在产，共表 c1_market.macro_data）——DS 编号映射与地图 data_refs 校准（涉写图） |
| 2 | A11 能源库存 | EIA 数据集未登记（源 active+provider 在产共表）——DS 编号登记口径裁定 |
| 3 | A16 投入产出（与 G5 同缺口） | 部门码↔ig_node 两套 id 体系消歧桥施工（边 100% 挂零，altdata_line WP-0.5）——施工班与优先级裁决 |
| 4 | A17 卖方研报 | 出边=0 未挂线；MOD-ALT-009 已带 module_id——挂线动作（涉写图）时点裁决 |
| 5 | B 档 10 线（政策级） | 全部 B档外采=资金门位（宪法 §5 high 域 Owner 门位）：B01 Planet 商业/B04 Keepa/B08 七麦/SensorTower 付费，B03/B06/B07 反爬合规——预算与渠道审批统一归 Owner |
| 6 | C 档 3 线（政策级） | 纪要定案挂起不入批；如需激活须 Owner 重开（本矩阵机械落 P3，不构成重启建议） |
| 7 | V2 情绪快照（政策级） | 情绪聚合器=独立对话未建（纪要 §8.3 定案不代建）——开话时点归总筹 |

## 5. 证据与生成方式声明

- 节点/出边/materiality/red_reason：python yaml.safe_load 解析 `config/trading_decision_map.yaml`（nodes=183/edges=257，出边按 edges.from_node 机械计数，非肉眼 grep）。
- DS 就绪度：`data_asset_registry.yaml` 按 dataset_id 精确匹配+format_summary/name_zh 关键词反查（CH 行数为册内 2026-09-03/2026-10-01 system.parts/tables 实测快照）；采集器存在性=模块头 [MATURITY]/[A_module] 逐文件核对。
- 档位交叉核对：W4 源线谱机生册 `data/registers/metaq_source_line/source_line_registry.yaml`（SL-A01~A16/B01~B10/C01~C03 共 29 线三档）与本矩阵 A01–A16+B01–B10+C01–C03 一一对应；A17 为册后新增第 30 线（尚未入 W4 册，提示总筹同步）。
- 拿不准处已标 needs_chief（A10/A11/A16/A17），未硬凑。
