---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·研报域（预期修正面）
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 研报/一致预期→预期修正信号族装配与消费接线——exp02 修正动量/exp03 修正宽度/exp05 分歧度/exp06 评级动量装配为信号＋评级变动事件流落库（数据已在库，缺口在装配与接线）
  output_contract: expectation_revision 信号族（expectations.py 注册位）＋rating_change 事件流（RatingChangeEvent 契约 :85-95 已定义、落库现空，P2 定形）
  exam_ref: 修正信号 IC 序列＋事件研究 CAR（预注册与全战役同批：IC 分组分位单调＋调级事件方向命中）
  campaign_ref: st-infoaxis-20261013（裁定#516）
---

# 研报域作业簿（12_research_workbook.md）

## §0 重大发现（开班令前提被实查推翻——P2 施工面据此改写）

开班令/A17 algo_note（trading_decision_map.yaml:5416）记载**"研报为唯一源线级设计缺口"**。
实查（2026-10-13）推翻其数据面前提：

- **一致预期表已存在**：c3_fundamental.consensus_daily **6,829,376 行**（2017-2026），列
  eps_consensus/eps_median/eps_std/pe_consensus/n_reports/n_orgs/n_buy/n_add/n_neutral/n_negative；
- **修正面因子雏形已在库**：src/zephyr/factor/expectations.py exp01~exp06（exp02_revision_momentum/
  exp03_revision_breadth/exp05_dispersion/exp06_rating_momentum，:39-45 注册）。

⇒ **缺口实为"预期修正面装配与消费接线"，而非数据缺失**：exp02/03/05/06 尚为纯函数未装配为
信号、未挂 selection 消费（A17 零挂接）；评级变动事件流（RatingChangeEvent 契约已在 collector
:85-95 定义）落库 100% 空。本簿病灶与 P2 施工面均按此改写。

## §1 问题定义（它出什么）

研报/一致预期→**预期修正信号族＋评级变动事件流**，供：
1. 选票漏斗 L3-02：修正动量/修正宽度/评级动量作选票增量因子（REC 文献量级：多空年化 14.8%、IR 2.36）；
2. 板块催化定位：研报覆盖密度/调级密度→板块热度面；
3. 装配批先例：FAC-E1G-M-007（strategy_production_map.yaml:1369 build_status=built）同通道扩员。

## §2 输出契约 v0

```
expectation_revision 信号族（因子名沿用 expectations.py 注册位，表名走 TableRegistry 派生）：
  exp02_revision_momentum(code, trade_date, score) / exp03_revision_breadth /
  exp05_dispersion / exp06_rating_momentum —— 纯函数已备，P2 装配+评估
rating_change_event 事件流（落库表现空，P2 定形）：
  event_id, code, ts, change_type∈{上调,下调,维持,首次}, org, pre_rating, post_rating,
  raw_text（留原始评级串），pit=research_report 落库时点
验收：IC 序列＋事件研究 CAR＋与 FAC-E1G-M-007 同批对比
```

## §3 外部对标（2026-10-13 车道回报，URL 在案）

| 来源 | 可借鉴点 |
|---|---|
| REC 修正幅度因子（搜狐 418394247） | 2010 年来多空年化 14.8%、IR 2.36——修正面 alpha 量级基准 |
| 中金 CAFR（新浪 2022） | 一致性修正区分"共识上调/分歧上调"——exp02 与 exp05 组合逻辑 |
| 国盛 PFRD | 预期修正维度体系对照 |
| AKShare stock_profit_forecast_em/ths | 免费一致预期补充源 |
| Tushare 券商卖方盈利预测（积分，doc_id 292） | 采购替换接口（积分=变相花钱门，只报价） |
| DISC-FinLLM/FinRobot | LLM+JSON schema 抽四字段（目标价/评级/EPS/机构）——LLM 必经 LSG |
| 评级编码实践 | 自建文本评级→五级标准化→调级方向映射表留原始串（证监会不统一阈值，卖出评级稀缺） |

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面
- MOD-ALT-009 research_report_collector.py production 纯内存 DI 模块；落库表=c3_fundamental.
  research_report（scripts/ch/backfill_research_report_full.py:23-25 写，源=akshare
  stock_research_report_em 东财研报中心，tasks.yaml research_report_detail_incremental 日增）。
- ig_chunk 5,200 全部 doc_type=ths_profile（同花顺公司简介）；ig_document 3,050=panorama_pdf 872/
  research_report 829/atlas_image 741/archive 572/structured 18/other 13/code 4/ths 1
  ⇒ **829 份研报已登记未切块，ig_chunk 零研报文本**。
- **一致预期表已存在：c3_fundamental.consensus_daily（6,829,376 行，2017-2026，列
  eps_consensus/eps_median/eps_std/pe_consensus/n_reports/n_orgs/n_buy/n_add/n_neutral/
  n_negative）**（§0 重大发现）。
- 备援：analyst_forecast（123,741 行仅 52 天）、pdf_forecast_extracted（192,365）、
  consensus_daily_repaired。

### 4.2 模块面
- collector 五方法 collect/reports/latest_rating/events/body_ref_of(:98)；契约
  ResearchReport:62-73（含 target_price）、RatingChangeEvent:85-95、快照 diff :180-203。
- A17 algo_note（yaml:5416）="研报为唯一源线级设计缺口；research_report_collector 已存在待补挂此"
  ——前提已被 §0 实查修正。
- 装配批消费=strategy_production_map.yaml:1369 FAC-E1G-M-007 build_status=built。

### 4.3 接线面
- A17(:5407-5425) factor_refs/data_refs/algo_refs 全空、module_ref null、untested——**纯登记位**。
- L3 双池(:1774)/九阶段(:1757 挂 selection_funnel)均无研报 module_ref。
- ig_chunk 消费者仅 websearch_ingest.py:806/ths_import.py:31。
- 研报全文提取=scripts/industry_graph/p2a_extract_reports.py:14（PyMuPDF；docstring 口径 484 份
  文字型 vs ig_document 登记 829 份——覆盖差进病灶 D2）。

### 4.4 词表面
- RATING_SCORE_MAP=src/zephyr/data/implementations/consensus_daily_compute.py:70-78
  （买入7/增持5/中性3/持有3/减持2/卖出1/回避2，华泰口径）；expectations.py 只读镜像
  （:47-48，车道锚 :23-31 为设计约定节）。
- rating_change 枚举注释 schemas :61"上调/下调/维持/首次"但实库 100% 空；评级分布
  买入101225/增持33144/空11384/卖出30（卖出评级稀缺与外部对标一致）。
- 目标价无 CH 列（GAP）——collector 契约有 target_price:62-73，落库表无对应列。
- 修正宽度因子雏形=expectations.py:39-45 exp01~exp06（exp02_revision_momentum/
  exp03_revision_breadth/exp05_dispersion/exp06_rating_momentum）。

## §5 六向台账（后两向）

### 5.5 判据面
- 修正信号 IC：RankIC 序列＋分组分位单调性（预注册=看数前冻结，与全战役判据同批呈批）。
- 评级变动事件研究：事件日=调级日，CAR 窗与传导链/股权域同批协议；方向命中=调级方向与
  CAR 符号一致率。
- PIT：research_report 落库时点＋快照 diff(:180-203)；consensus_daily 增量重叠窗 3 日
  （consensus_daily_compute.py:80-81）登记为迟到面。

### 5.6 消费面
- 选票漏斗 L3-02（selection_funnel，yaml:1757 九阶段挂点）——修正信号族作选票增量。
- 板块催化定位：研报覆盖/调级密度→板块热度面（与传导链域 L2-09 互引）。
- 装配通道：FAC-E1G-M-007（strategy_production_map.yaml:1369 built）同批扩员 exp02/03/05/06。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| D1 | rating_change 实库 100% 空（schemas :61 枚举注释无一行数据）——评级变动事件流有名无实 | 阻断级 | P2：collector events 快照 diff(:180-203) 落库（待裁 C3 定粒度） |
| D2 | 829 份研报登记 ig_document 未切块（ig_chunk 零研报文本）；p2a 提取件 docstring 口径仅 484 份文字型 | 阻断级 | P2：p2a 全量跑＋切块入 ig_chunk |
| D3 | A17 零挂接：factor/data/algo_refs 全空、module_ref null、untested——纯登记位 | 阻断级 | P2：挂 research_report_collector＋expectations 族 |
| D4 | analyst_forecast 仅 52 天（123,741 行）——备援窗口不足；pdf_forecast_extracted 192,365 行未接消费 | 缺口级 | 备援定级：consensus_daily 为主源，备援只做校验（待裁 C4） |
| D5 | 目标价无 CH 列（GAP）——契约有 target_price:62-73，落库表无列 | 缺口级 | P2：DDL 补列（走 apply_consensus_daily_ddl 同通道） |
| D6 | exp01~exp06 纯函数未装配未评估（factor_registry expectations 族登记排队 P0 后） | 缺口级 | P2：装配 exp02/03/05/06 为信号＋SOP-B 评估 |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| C1 | 朝阳永续等一致预期商业源采购 | 只调研报价呈批 | 不采（花钱门=Owner；consensus_daily 683 万行先吃仓内） |
| C2 | LLM 抽四字段（目标价/评级/EPS/机构）管线 | 走 LSG 网关（DISC-FinLLM 式 JSON schema） | 采纳——LLM 调用必经 LSG（硬规则） |
| C3 | rating_change 落库粒度 | A=逐条研报级；B=机构×日聚合级 | A（事件流原始粒度，聚合下游派生） |
| C4 | 备援表处置（analyst_forecast 仅 52 天） | A=保留为校验源；B=退役 | A（净零原则下不扩，不退役） |

## §8 车道回报存档

- 仓内四层＋外部对标：战役协调车道下发（2026-10-13，全带 :行号 锚点）；本起草车道抽验
  consensus_daily_compute.py:70-78（实路径 src/zephyr/data/implementations/）、
  expectations.py:39-45/:47、p2a_extract_reports.py:14 实核一致（p2a docstring 口径 484 份
  已在 §4.3/D2 双记）。

## §9 自审闸三态裁定（初判）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 病灶 6 条全部定级＋处置走向（含 §0 重大发现改写后的施工面）
- [x] 待裁 4 项进 P1 总表候选（C1 花钱门只报价、C2 LSG 硬规则）
- [x] 重大发现显著置顶（§0）：缺口=装配与消费接线，非数据缺失
- 状态：**初判过闸·封矿候选**（终判留战役总闸；IC 阈值/CAR 窗宽留 P2 看数前冻结呈批）
