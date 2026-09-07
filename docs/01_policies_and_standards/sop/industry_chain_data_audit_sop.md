---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 产业链供应链全景图数据审计与更新SOP——夜班自主执行版
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.0"
date: 2026-09-07
topic: industry_chain_data_audit
scope: global
depends_on:
  - document_review_and_optimization_sop
  - construction_workflow_sop
  - 2026-08-28-industry-graph-frontend
related_issues: []
related_modules:
  - scripts/industry_graph/
  - src/zephyr/governance/depgraph_schema.py
---

# ZEPHYR数据审计与更新 SOP——夜班自主执行版

> 本 SOP 是 **产业链/供应链全景图数据**（PG depgraph 库 ig\_\* 七表）的**审计、更新、补充流程真源**。
> **核心用途**：Owner 睡前对 AI 说一句"按照 industry\_chain\_data\_audit\_sop 执行夜班"，AI 自主执行到 Owner 醒来，中途不问用户、不汇报中间态，醒后一次性大白话汇报。
> **性质**：编排层 + 数据契约。表结构真源是 [apply\_industry\_graph\_ddl.py](../../../../../scripts/industry_graph/apply_industry_graph_ddl.py)（DDL-as-Code），五视图设计真源是 [2026-08-28-industry-graph-frontend.md](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/2026-08-28-industry-graph-frontend.md)。本文件不重复表结构，只规定：审计什么 / 怎么补 / 数据怎么写 / 写成什么样算合格 / 怎么汇报。
> **方法论参考**：[document\_review\_and\_optimization\_sop](document_review_and_optimization_sop.md)（轮次循环+连续零发现退出）｜[audit\_prompts\_20\_ai](audit_prompts_20_ai.md)（总控派单+自包含提示词+无人值守编排）。
> **不做什么**：不动交易/实盘模块（只写 depgraph PG 库）；不做前端接线（chainmap 页接线走 DAL-C01/C02 另行派单）；不做 lead-lag 因子（2026-08-28 已证伪裁定，不推翻）。

## 1. 主题组信息

| 项    | 内容                                                                                                                                                                    |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 主题组  | G10 产业链数据审计 SOP                                                                                                                                                       |
| 创建   | 2026-09-03                                                                                                                                                            |
| 优先级  | P1（数据底座保鲜的常态机制）                                                                                                                                                       |
| 状态   | active v1.0.0                                                                                                                                                         |
| 上游   | [2026-08-28-industry-graph-frontend.md](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/2026-08-28-industry-graph-frontend.md)（数据底座验收） |
| 下游   | 所有执行夜班数据审计的 AI session（必读）                                                                                                                                            |
| 真源边界 | 表结构以 DDL 脚本为准，数据契约以本文件 §4 为准，流程编排以本文件为准                                                                                                                               |
| 冲突解决 | 表结构冲突→DDL 脚本为准；数据写入约定冲突→本文件为准；与既有裁定冲突→既有裁定为准并登记开放问题                                                                                                                   |

## 2. 背景与数据基线

### 2.1 现状（2026-09-03 实测基线，夜班开工时以第 0 轮重测为准）

| 表                   | 行数      | 说明                                                   |
| ------------------- | ------- | ---------------------------------------------------- |
| ig\_chain           | 686     | 产业链主表（market='cn'）                                   |
| ig\_node            | 2,911   | 环节节点（上游/中游/下游/设备/材料）                                 |
| ig\_edge            | 1,133   | 环节结构边                                                |
| ig\_node\_company   | 11,075  | 环节↔股票映射（2,441 只 A 股，占在市 5,214 只的 46.8%）              |
| ig\_document        | 3,049   | 源文档登记（canonical 2,110）                               |
| ig\_company\_edge   | 58,029  | 公司供应链边（483 前五大客户 2001-2025 / match\_list / J88 专利协同） |
| ig\_company\_metric | 235,367 | 客户集中度/韧性年度指标（覆盖 5,065 只 ≈ 97%）                       |

### 2.2 痛点

1. **数据一次性**：全部来自 2026-08 淘宝采购包（source\_note='taobao\_purchase\_internal\_only'），无自动更新机制，无爬虫无定时任务。数据天然随时间陈旧（年报数据止于 2025、链版本止于采购时点）。
2. **覆盖不全**：46.8% 的 A 股有环节落位；半导体/AI 算力等链缺全球锚点公司（英伟达/台积电/三星/海力士/ASML 等），而这些正是对 A 股传导最强的节点。
3. **无更新流程**：16 个脚本只管"从采购包导入"，没有"无采购包时如何保鲜"的流程——本 SOP 即为此而设，主渠道为 AI WebSearch（联网搜索）。

### 2.3 全球扩展裁定（2026-09-03 Owner 确认：锚点模式）

- **做**：约 150 家全球关键公司（英伟达/AMD/台积电/三星/海力士/美光/ASML/应用材料/特斯拉/苹果/微软/谷歌/Meta/亚马逊等）作为**传导锚点**挂到 A 股产业链上，`market='global'` 标记。
- **不做**：美股/韩股全市场产业链（超出单机个人项目硬边界，系统只交易 A 股+数字货币）。
- **定位**：全球锚点是**信息全景**（判断传导关系用），不进因子框架（lead-lag 已证伪的裁定不推翻）。
- schema 已有 market 字段，**无需改表**。

## 3. 触发条件与夜班总则

| 编号 | 场景                  | 说明                                                              |
| -- | ------------------- | --------------------------------------------------------------- |
| T1 | **夜班模式**（本 SOP 主用途） | Owner 睡前一句"按照 industry\_chain\_data\_audit\_sop 执行夜班"，AI 自主执行整夜 |
| T2 | 重新采购数据包后            | 新数据包到位，走 16 个既有导入脚本后再跑本 SOP 审计轮                                 |
| T3 | Owner 专项触发          | 发现某链/某公司数据明显过期或缺失                                               |

### 夜班总则（八条）

1. **不问用户**：Owner 在睡觉。一切需要 Owner 拍板的（删数据、推翻裁定、合并重复链）→ 登记到夜班报告「开放问题」节，醒后裁定。
2. **可截断**：所有轮次内部按优先级排序（P1 最先做），任意时刻中断都不留脏数据（每批一个事务）。
3. **断点续跑**：进度落 `.runtime/industry_graph/night_audit/progress.json`，会话崩溃重启后从断点继续，已完成批次不重做。
4. **只增不删**：数据库只 INSERT/UPDATE，永不 DELETE。发现错误数据→登记开放问题。
5. **先备份后写入**：第 0 轮先做库内备份表，之后才允许任何写入。
6. **写完即校验**：每轮结束跑一致性校验（§6 第 6 轮的 SQL 清单），不合格当轮修复。
7. **时间盒**：每轮有软时限（§6）；若到早上 07:00（本机时间 `Get-Date` 实测）仍未收尾→停止派新批次，对**已写入数据**执行第 6/7 轮校验与汇报，剩余批次写入 progress.json 待续。
8. **大白话汇报**：醒后一次性汇报，只给结果不给过程，格式见 §10。

## 4. 数据契约（写入纪律，逐字适用）

> 本节是所有写入的强制约定。第 0 轮施工的写入工具负责机械强制执行这些约定，子代理不允许绕过工具手写 SQL。

### 4.1 连接与幂等

- PG 连接**必须**走 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`，**禁止裸连接**（配置在 `config/.env.postgres`，库 depgraph）。
- 所有写入**必须幂等**：尊重各表 UNIQUE 约束，用 `INSERT ... ON CONFLICT DO UPDATE`。同一批次重复执行结果一致。
- 每个批次文件 = 一个事务：全成或全败，禁止半批落库。

### 4.2 来源标记（source 契约）

| 数据来源           | source 字段                      | source\_doc 字段              | 说明                 |
| -------------- | ------------------------------ | --------------------------- | ------------------ |
| WebSearch 联网搜索 | `websearch`                    | `查询词 \| URL \| YYYY-MM-DD`  | 竖线分隔三段，URL 和访问日期必填 |
| 存量语料 RAG 复核    | `corpus_rag`                   | `语料文件名 \| 主题 \| YYYY-MM-DD` | E盘语料库 76,112 块向量索引 |
| 采购包（既有数据）      | 不变（483/match\_list/J88/结构抽取原值） | 不变                          | 本 SOP 不碰存量行的来源标记   |

- **source\_doc 非空率对新写入行 = 100%**。无来源不落库，宁可登记缺口。

### 4.3 置信度分级（confidence 契约）

| 档位         | 赋值条件                           | 适用               |
| ---------- | ------------------------------ | ---------------- |
| 0.5        | 单一网络来源                         | websearch 默认     |
| 0.7        | 两个独立网络来源互证，或网络来源与存量语料 RAG 互证   | websearch 上限     |
| 0.6 / 0.85 | 既有档位（0.6=规则抽取单文档，0.85=≥2 文档互证） | 仅采购管线使用，本 SOP 不赋 |

- **websearch 来源数据 confidence 永不超过 0.7**（工具硬校验）。现有 0.85 互证子集（theme\_linkage\_monitor 只用 ≥0.85）天然不被污染。
- ig\_chain/ig\_node/ig\_edge 无 confidence 字段，质量经 source\_doc 溯源。

### 4.4 market 与 symbol 约定

| market | symbol 格式 | 正则                    | 示例              | <br />       | <br /> | <br /> | <br />                    |
| ------ | --------- | --------------------- | --------------- | :----------- | :----- | :----- | :------------------------ |
| <br /> | <br />    | cn                    | 6位数字.SH/.SZ/.BJ | \`^\d{6}.(SH | SZ     | BJ)$\` | 300750.SZ、688981.SH       |
| global | 代码.交易所国别  | \`^\[A-Z0-9]{1,6}.(US | KS              | TW           | T      | HK)$\` | NVDA.US、005930.KS、2330.TW |

- `market='cn'` 的行**必须**能反查到 ClickHouse `c1_market.stock_basic FINAL WHERE valid_to IS NULL`；`market='global'` 的行豁免（不在 stock\_basic 是预期行为）。
- global 公司中文名写入 name/aliases（ig\_node）或 from\_name/to\_name（ig\_company\_edge），symbol 用上表格式。

### 4.5 备份与不删

- 第 0 轮建库内备份：`CREATE TABLE ig_<表名>_bak_YYYYMMDD AS SELECT * FROM ig_<表名>`（七表全做）。
- 恢复 = Owner 醒后人工裁定执行，夜班 AI 只备份不恢复。
- **禁止 DELETE/TRUNCATE/DROP**（备份表除外，也不许动）。

### 4.6 字段字典（数据标准真源，2026-09-07 增补）

> 七表全字段标准。夜班 AI 写入任何一列前必读本节对应行；`websearch_ingest.py` 硬校验以此为准。**时效三件套**（version\_year / year / source\_doc 采集日期）是过期判定的唯一依据，缺一不可。

**ig\_chain（产业链主表，10 字段）**

| 字段 | 类型 | 必填 | 标准 |
|---|---|---|---|
| chain\_id | TEXT PK | 是 | 格式 `CH-{12位hex}`（存量惯例）；新建沿用 |
| name | TEXT | 是 | 规范见 §4.7.1（≤12 字，禁文档标题腔） |
| category | TEXT | 否→治理后是 | 申万一级类目（§4.7.3 词表），**禁数据包名** |
| version\_year | SMALLINT | 否→新链必填 | **信息版本年**=图谱内容描述的年份（如 2026 新版图谱→2026），非写入年 |
| market | TEXT | 是 | ∈{cn, global}，链本身默认 cn |
| status | TEXT | 是 | ∈{active, deprecated}；deprecated 须在 source\_note 写 `merged_into:CH-xxx` |
| source\_note | TEXT | 新链必填 | `websearch`（或存量采购标记） |
| created\_at / updated\_at | TIMESTAMPTZ | 自动 | **任何对本链条目的写入必须刷新 updated\_at**（工具强制） |

**ig\_node（环节节点表，9 字段）**

| 字段 | 类型 | 必填 | 标准 |
|---|---|---|---|
| node\_id | TEXT PK | 是 | `ND-{12位hex}` |
| chain\_id | TEXT FK | 是 | |
| name | TEXT | 是 | **纯环节功能名**（如"HBM 封装""光引发剂"），禁链名前缀/`-tier` 后缀残留 |
| tier | TEXT | 新节点必填 | §4.7.2 词表 9 值；**websearch 新写入禁 unspecified** |
| aliases | TEXT\[\] | 否 | 别名数组（含英文名/简称） |
| description | TEXT | 否 | 一句话环节说明 |
| market | TEXT | 是 | ∈{cn, global} |
| created\_at / updated\_at | TIMESTAMPTZ | 自动 | 同上刷新纪律 |

**ig\_edge（环节结构边，8 字段）**

| 字段 | 类型 | 必填 | 标准 |
|---|---|---|---|
| edge\_id | BIGSERIAL PK | 自动 | |
| from\_node / to\_node | TEXT FK | 是 | 方向=供应流向（上游→下游） |
| edge\_type | TEXT | 是 | ∈{structure（环节顺序）, supply（环节间供应）}；UNIQUE(from,to,type) 幂等锚 |
| source\_doc | TEXT | 新边必填 | §4.2 三段式 |
| market | TEXT | 是 | |

**ig\_node\_company（公司落位表，11 字段）——"每个公司一个节点落位"的核心表**

| 字段 | 类型 | 必填 | 标准 |
|---|---|---|---|
| id | BIGSERIAL PK | 自动 | |
| node\_id | TEXT FK | 是 | 落到具体环节 |
| symbol | TEXT | 是 | §4.4 正则（cn 反查 stock\_basic / global 豁免）；UNIQUE(node\_id,symbol) |
| role | TEXT | 否 | ∈{龙头, 核心, 参与, 全球龙头, 潜在}（自由词但须名词性） |
| confidence | REAL | 是 | §4.3（websearch ≤0.7） |
| evidence\_text | TEXT | websearch 必填 | **原文摘录一句**（反幻觉锚） |
| source\_doc | TEXT | 是 | 三段式含采集日期 |
| market | TEXT | 是 | 与 node.market 一致（校验项 4） |
| updated\_at | TIMESTAMPTZ | 自动 | **公司信息变更（role/别名/主营变化）刷新此戳** |

**ig\_company\_edge（公司间供应链边，14 字段）——上下游关系的核心表**

| 字段 | 类型 | 必填 | 标准 |
|---|---|---|---|
| from\_symbol / to\_symbol | TEXT | 是 | 供应商→客户方向；to\_symbol='' 表示非上市对手方（名称在 to\_name） |
| year | SMALLINT | 是 | **关系数据年**（年报年/新闻年），UNIQUE(from,to,year,source) 幂等锚 |
| product | TEXT | 否 | 供应的产品/服务（如"AI 服务器整机代工""HBM3"） |
| weight / weight\_type | REAL / TEXT | 否 | 数值及其类型（如占营收比/采购额亿） |
| source | TEXT | 是 | §4.2 枚举 |
| from\_name / to\_name | TEXT | 否 | 公司中文名（global/非上市必填其一侧） |
| amount / rank | NUMERIC / SMALLINT | 否 | 金额（亿元）/ 前五大客户排位 |
| market | TEXT | 是 | cn 边=双侧 A 股；跨国边=global |

**ig\_company\_metric（公司年度指标，9 字段）**：symbol/year/metric/value/value\_aux/source/market；metric ∈ {customer\_hhi, customer\_stability, top1\_ratio, top5\_ratio, supply\_chain\_resilience}（新指标须先在本 SOP 登记词表再写入）。

**ig\_document（源语料登记，22 字段）**：夜班 AI 一般不写此表（WebSearch 不是文档入库）；仅 RAG 复核时引用 doc\_id。

**时效三件套与过期判定（Owner 2026-09-07 要求：时间戳是快速定位过时数据的主键）**

1. 采集日期（source\_doc 第三段）：数据**何时拿到**。
2. version\_year / year：数据**描述哪一年**的产业实态。
3. updated\_at：本行**最后一次被核验/修正**的时间。
4. **过期公式**（第 0 轮 gap\_ledger 与 §6 第 6 轮校验共用）：
   - 链过期：`version_year ≤ 当前年-2` OR `updated_at < now()-180天` → 进更新候选
   - 边过期：`year ≤ 当前年-2`（供应链关系 2 年一验）
   - 全新写入**永远带当日采集日期**——没有时间戳的数据等于没写。

### 4.7 命名与词表标准（2026-09-07 增补）

#### 4.7.1 chain.name 规范

- 格式：`{核心产品/行业}产业链`（如"存储芯片产业链""光刻胶产业链"），或行业通名（"模拟芯片"）。
- ≤12 字；禁文档标题腔（"一张图看懂""80页PPT""XX启幕""IPO""深度投资""本轮涨价能走多远"）；禁标点；允许可选后缀 `（全球）` 仅用于 global 视图链。
- 写入前必跑 `find-chain`，命中相似度≥0.7 的存量链→复用不新建。

#### 4.7.2 tier 词表（9 值封闭枚举）

`上游 / 中游 / 下游 / 设备 / 材料 / 零部件 / 原材料 / 辅材 / unspecified`

- 新写入只用前 5 值；`零部件/原材料/辅材` 为存量兼容值（治理目标：逐步归并入 上游/材料）。
- `unspecified`（存量 686 个）为抽取残留：**websearch 写入禁用**；治理时按环节语义判 5 值。

#### 4.7.3 category 词表（申万一级 31 类）

 electronics 类：半导体、消费电子、元件、光学光电子、计算机设备；制造类：机械设备、电力设备、汽车、国防军工、家用电器；材料类：基础化工、有色金属、钢铁、建筑材料、石油石化；医药类：医药生物；消费类：食品饮料、纺织服饰、商贸零售、社会服务、美容护理、轻工制造、农林牧渔；TMT 类：软件开发、互联网服务、通信服务、通信设备、游戏、传媒；金融基建类：银行、非银金融、房地产、建筑装饰、交通运输、公用事业、环保、综合。

- **禁数据包名**（现状 5 个值全是包名，属第 1 轮治理对象）；不确定时用"综合"并在开放问题登记。

#### 4.7.4 链名治理样板（半导体实例，Owner 2026-09-07 过目版）

**现状（15 条半导体相关碎片链，规则抽取把文档标题切成了链）**：

| 现有链名（节选） | 节点数 | 公司数 | 病因 |
|---|---|---|---|
| 80页PPT全方位解读半导体行业 | 6 | 14 | 文档标题当链名 |
| 长鑫科技IPO启幕：半导体设备与材料产业链深度投资 | 6 | 7 | 同上 |
| 半导体设备行业 / 半导体硅材料行业 / 半导体硅片行业 | 3-6 | 3-12 | 同产品族被拆 3 条 |
| 光刻胶产业链行业 / 光刻胶行业 / 一张图看懂光刻胶 | 4-6 | 5-31 | 同主题被拆 3 条 |
| 存储芯片本轮涨价能走多远？一文看懂产业链 | 5 | 4 | 文档标题腔 |
| 氮化镓半导体材料行业 / 倒装芯片 / 智驾SoC / 模拟芯片 / 光芯片 / 算力芯片 | 1-6 | 5-23 | 粒度不齐 |

**跨链重叠证据**：中芯国际 688981.SH 落 6 条链（真重叠）；000591.SZ 太阳能落 8 条链（**误挂**——抽取器把"材料"环节模糊匹配，治理时降 confidence/移除）。

**治理后目标（15 → 8 条母链，只增不删：子链标 deprecated 不物理删除）**：

| 母链（新 name / category） | 吸收的子链 | 合并规则 |
|---|---|---|
| 半导体设备产业链（半导体） | 半导体设备行业、长鑫科技IPO… | 公司并集去重，confidence 取 max，evidence 各自保留 |
| 半导体材料产业链（半导体） | 硅材料、硅片、氮化镓材料、80页PPT | 节点按 tier 重排（材料族归"材料"） |
| 光刻胶产业链（半导体） | 光刻胶产业链行业、光刻胶行业、一张图看懂光刻胶 | 三合一（31+8+5 公司去重） |
| 存储芯片产业链（半导体） | 存储芯片本轮涨价… | 改规范名 |
| 模拟芯片（半导体） | —（已合规） | 仅补 category/version\_year |
| 光芯片（半导体） | —（已合规） | 同上 |
| 算力芯片（半导体） | —（已合规） | 同上 |
| 先进封装产业链（半导体） | 一张图看懂倒装芯片行业 | 改规范名 |

**单链合并明细样板（光刻胶三合一 before→after）**：

```
新建：CH-新 | 光刻胶产业链 | 半导体 | version_year=2026 | source_note=websearch
节点（按 tier 归一）：
  上游：树脂与单体 / 溶剂 / 光引发剂        ← 三条子链"上游/材料"节点归并
  中游：光刻胶生产（ArF/KrF/i线 分 aliases）
  下游：晶圆制造 / PCB 制造
  设备：涂胶显影设备
公司：31+8+5 去重后 33 家（重叠 11 家合并，confidence 取各方 max，
      000591.SZ 类误挂登记开放问题待 Owner 裁定移除）
子链处置：三条旧链 status='deprecated'，source_note='merged_into:CH-新'
审计链：合并明细写入夜班报告（谁并进了谁、公司数 from→to）
```

**执行边界**：合并涉及存量行修改 → 按夜班总则第 1 条，AI 可做**方案与 dry-run**，执行合并须 Owner 醒后拍板（样板批准后可按同款规则批量化）。

## 5. 写入工具（第 0 轮施工件）

夜班开工先施工统一写入工具 `scripts/industry_graph/websearch_ingest.py`，之后所有轮次的写入**只准走这个工具**。施工遵循 [construction\_workflow\_sop](construction_workflow_sop.md) 纪律。

**子命令**：

| 命令                      | 作用                                                           |
| ----------------------- | ------------------------------------------------------------ |
| `stats`                 | 七表计数 + 关键缺口统计（无落位股票数、version\_year≤2023 链数、节点数<3 链数），输出 JSON |
| `backup`                | 七表库内备份（§4.5），幂等（已存在当日备份表则跳过）                                 |
| `find-chain --name XX`  | 模糊找链（返回最相似的前 5 条 chain\_id+name+version\_year），子代理写链前必查防重复建链 |
| `ingest --batch <path>` | 校验+事务写入一个批次 JSON                                             |

**批次 JSON 格式**（`.runtime/industry_graph/night_audit/batches/roundN_主题_序号.json`）：

```json
{
  "batch_id": "round2_存储芯片链_001",
  "round": 2,
  "records": [
    {"type": "chain", "name": "存储芯片产业链", "category": "半导体", "version_year": 2026, "market": "cn", "source_doc": "查询词|https://...|2026-09-03"},
    {"type": "node", "chain_name": "存储芯片产业链", "name": "HBM制造", "tier": "中游", "market": "cn", "source_doc": "..."},
    {"type": "node_edge", "chain_name": "存储芯片产业链", "from_node": "晶圆制造", "to_node": "HBM制造", "edge_type": "structure", "source_doc": "..."},
    {"type": "node_company", "chain_name": "存储芯片产业链", "node_name": "HBM制造", "symbol": "005930.KS", "role": "全球龙头", "confidence": 0.5, "evidence_text": "原文摘录一句", "market": "global", "source_doc": "..."},
    {"type": "company_edge", "from_symbol": "NVDA.US", "to_symbol": "002463.SZ", "year": 2026, "product": "AI服务器整机代工", "source": "websearch", "from_name": "英伟达", "to_name": "沪电股份", "market": "global", "source_doc": "..."},
    {"type": "metric", "symbol": "002463.SZ", "year": 2025, "metric": "top5_ratio", "value": 0.62, "source": "websearch", "market": "cn", "source_doc": "..."}
  ]
}
```

**工具硬校验**（不合格整批拒绝，报错给子代理改）：

1. source\_doc 非空且含 `|` 分隔的 URL 段和日期段。
2. `source in ('websearch','corpus_rag')` 的行 confidence ≤ 0.7。
3. symbol 正则（§4.4）按 market 校验；cn 行额外反查 stock\_basic。
4. chain\_name/node\_name 先解析成 id（find-chain 精确/唯一匹配则复用，无则按序创建）。
5. market 枚举 ∈ {cn, global}。
6. 写入后刷新对应 ig\_chain.updated\_at。
7. tier ∈ §4.7.2 词表且 websearch 写入禁 unspecified（§4.6/4.7 标准，2026-09-07 增）。
8. category ∈ §4.7.3 申万词表（空/兜底"综合"放行但记 warn）。
9. node.name 禁链名前缀/`-tier` 后缀（正则 `-\d|-[上下游中]|-设备|-材料|-零部件|-原材料|-辅材|-unspecified$` 命中即拒）。

**登记要求**：script-manifest.yaml 新增条目（STARTUP: manual，domain: industry\_graph）+ `tests/scripts/test_websearch_ingest.py` 测试件（幂等/校验拒绝/事务回滚三测）+ GitCommitGateway 提交。

## 6. 八轮审计循环

> **总原则**：按顺序执行；每轮内部按优先级排序、分批推进；每批写入即校验；轮末跑当轮通过条件。夜班 AI 扮演**总控**，按 §8 派子代理执行。

### 第 0 轮：基线盘点与工具施工（软时限 1 小时）

**目的**：摸清家底、建好写入通道，生成整夜工作清单。

**操作**：

1. **开工探测**：主仓 `git status` + 活跃文件锁检查（`python scripts/lock_files.py check`）；若 scripts/industry\_graph/ 或本 SOP 被在途 session 持锁→等待 5 分钟重试，仍锁→只读轮次先行，写入轮次顺延并在 progress 登记。
2. **施工写入工具**（§5），走完整施工纪律。
3. **备份**：`websearch_ingest.py backup`。
4. **基线与缺口总账**：`websearch_ingest.py stats` + 以下清单写入 `.runtime/industry_graph/night_audit/gap_ledger_YYYYMMDD.md`：
   - 无落位股票清单（stock\_basic 在市 - ig\_node\_company cn symbol），按行业分组计数
   - version\_year ≤2023 的链清单（数据陈旧）
   - 节点数 <3 的链清单（疑似抽取不完整）
   - 疑似重复链清单（name 相同/规范化后相同/包含关系）
   - ig\_company\_edge 按 year 分布（确认止于哪年）
   - **命名不规范清单**（§4.7 标准）：文档标题腔链名 / tier=unspecified 节点 / category 非申万词表链 / 跨链误挂公司（单公司挂 ≥5 链抽验）
   - **过期链清单**（§4.6 过期公式：version\_year≤当前年-2 OR updated\_at<180 天）
5. **优先级裁定**（机械规则）：
   - **P1 链** = theme\_linkage\_daily.csv 中 corr20 绝对值 TOP30 的链 ∪ 主线链清单（半导体、AI算力、存储芯片、新能源车、锂电池、光伏、储能、机器人、军工、医药、消费电子、低空经济）
   - **P2 链** = version\_year ≤2023 的链
   - **P3 链** = 节点数 <3 的链
   - 去重合并后按 P1→P2→P3 排序成整夜链工作清单

**通过条件**：工具三测绿 + 备份表存在 + 缺口总账五清单齐 + 链工作清单已排序。

**失败处置**：工具施工受阻（依赖/环境问题）→ 降级方案：用一次性 Python 脚本内联实现校验逻辑执行写入（同样遵守 §4 契约），并在夜班报告登记"工具未施工，下轮夜班补"。

### 第 1 轮：存量质量审计（软时限 1 小时）

**目的**：先治已有数据的病，再补新数据（防"边补边烂"）。

**操作**：

1. **重复链处理**：对第 0 轮疑似重复链清单逐组核（读 description/节点/公司重合度）。**合并需 Owner 拍板→登记开放问题**；本夜只在 progress 标记，不合并。合并方案按 §4.7.4 样板格式产出（半导体样板已过 Owner 目，其余行业按同款规则套）。
2. **死映射核验**：ig\_node\_company 的 cn symbol 反查 stock\_basic；查不到的（退市/更名）→ 登记清单进开放问题（不删）。**更名股**（simple name 变化但 symbol 在）→ 修正属机械操作，可做。
3. **孤岛节点**：无 edge 且无 company 映射的 node → 清单登记；若属明显漏连（如"下游"节点无任何上游边）→ 补边（走工具，source\_doc 写明推断依据）。
4. **category 补全**：ig\_chain.category 为空或非 §4.7.3 词表的链，从链名/节点推断补齐（禁数据包名；不确定→"综合"+开放问题）。
5. **ig\_company\_edge 年度缺口确认**：按 year 分布确定本夜第 5 轮的目标年份区间。
6. **命名治理（dry-run）**：按 §4.7.1/§4.7.2 标准产出改名/归并方案清单（不改库）——文档标题腔链名→规范名映射表、unspecified 节点的 tier 判定表，随夜班报告交 Owner 批量拍板。

**通过条件**：重复链 100% 核验标记（不是清零，是清点）；死映射/孤岛节点清单完整；category 空值清零。

**失败处置**：核验量大→按 P1 链优先核，其余登记"未核验完"进 progress。

### 第 2 轮：链级补全（WebSearch 主战场，软时限 3 小时）

**目的**：对链工作清单逐链补齐节点/结构边/公司落位。

**操作**（每链一批次，子代理并发执行）：

1. 写链前必跑 `find-chain` 防重复建链。
2. 搜索（§7 规范）：`"{链名} 产业链图谱 上中下游 2026"` → 补环节节点与结构边；`"{链名} 龙头上市公司 A股 2026"` → 补公司落位。
3. 每链先与存量比对：已有节点不重写，只补缺；发现存量节点明显错误→登记开放问题。
4. A 股公司 symbol 从 stock\_basic 精确匹配简称/全称；匹配不到的候选公司→不硬写，登记缺口。
5. 涉及全球龙头（该链的英伟达/三星级节点）→ 本轮只登记进第 4 轮锚点清单，不在此轮展开。

**通过条件**：链工作清单中已处理链（含"查过无新可补"）100% 有批次记录或缺口登记；P1 链全部处理完才算本轮达标。

**失败处置**：搜索连续失败→换词重试 1 次→跳过该链登记缺口；时间耗尽→剩余链进 progress 待续（P1 未完优先续）。

### 第 3 轮：A 股落位覆盖率提升（软时限 2 小时）

**目的**：把环节落位覆盖率从 46.8% 提到 ≥80%。

**操作**：

1. 取第 0 轮无落位股票清单（按行业分组），按组派子代理。
2. 每组搜索：`"{行业} 产业链 代表上市公司 环节 2026"`，把公司映射到已有链/节点；无对应链的行业（该行业股票≥5 只时）→ 建新链（category=行业名）。
3. 金融/综合/多元化工等无明确产业链属性的标的→不硬挂，登记"无链可挂"清单（这类占剩余合理）。
4. 每组一批次；symbol 一律 stock\_basic 精确匹配。

**通过条件**：在市 A 股落位覆盖率 ≥80%，或剩余未落位股 100% 有"无链可挂"登记。

**失败处置**：达不到 80% 且时间尽→记录当前覆盖率和剩余组清单进 progress。

### 第 4 轮：全球锚点扩展（软时限 1.5 小时，按 §2.3 裁定执行）

**目的**：把约 150 家全球关键公司挂上 A 股产业链，形成传导锚点。

**操作**：

1. **锚点清单生成**（机械规则）：
   - 预置清单（半导体：英伟达/AMD/英特尔/高通/博通/美光/应用材料/泛林/ASML/台积电/三星/海力士/联发科；消费电子：苹果；汽车：特斯拉/丰田/现代；云与AI：微软/谷歌/Meta/亚马逊；软件：SAP/Oracle）
   - ∪ 从 ig\_company\_edge 非上市对手方（to\_symbol=''）中提取出现 ≥5 次的全球公司名
   - 去重后约 100\~200 家为锚点清单，写入 progress。
2. 每锚点搜索：`"{公司} A股 供应链 供应商 2026"` / `"{公司英文名} China A-share suppliers 2026"`。
3. 写入三件套：
   - ig\_node：挂到对应 A 股链的对应环节（如英伟达→半导体链"GPU设计"节点），market='global'
   - ig\_node\_company：symbol='NVDA.US'，market='global'，confidence 按 §4.3
   - ig\_company\_edge：全球↔A 股直接供应边（如 NVDA.US↔002463.SZ），market='global'
4. 找不到可靠 A 股关联的锚点→只建节点挂链，不硬造供应边。

**通过条件**：锚点清单 100% 处理（挂上链或登记"无可靠关联"）；预置清单中的公司 100% 挂链。

**失败处置**：时间尽→按预置清单顺序处理了多少记多少，剩余进 progress。

### 第 5 轮：供应链边与指标更新（软时限 1 小时）

**目的**：把 ig\_company\_edge 的年度数据从采购包止点（2025）向 2026 推进，捕获新闻级供应链变化。

**操作**：

1. 对 P1 链每链关联公司数 TOP5 的公司，搜：`"{公司} 2025年报 前五大客户 供应商"` → 补 company\_edge（year=2025，source='websearch'）。
2. 新闻级重大变化（断供/新签/扩产/替代）：`"{公司A} {公司B} 供应 协议 2026"` → 补边（product 写事件，evidence/source\_doc 记新闻 URL）。
3. ig\_company\_metric：2025 年报指标已披露的搜到就补；未披露→登记"待年报"清单，不强补。

**通过条件**：P1 链 TOP5 公司全部查过（补到或登记待年报）。

**失败处置**：年报未披露是常态不是失败，登记即可。

### 第 6 轮：一致性校验（软时限 30 分钟，**无论推进到哪轮都必须执行**）

**目的**：保证已写入数据经得起反查。

**操作**（SQL 清单，全部跑完出报告）：

1. 本夜新写入行（source\_doc 含本夜日期）source\_doc 非空率 = 100%。
2. `source IN ('websearch','corpus_rag')` 的行 confidence ≤0.7 违规数 = 0。
3. 全表 symbol 正则扫描（按 market 分组）违规数 = 0。
4. node\_company.market 与 node.market 不一致数 = 0。
5. 本夜有写入的链 updated\_at 已刷新数 = 写入链数。
6. 重复链复扫：新增链与存量链无 name 完全重复。
7. cn symbol 反查 stock\_basic 不命中率 = 0（第 1 轮已登记的死映射除外）。

**通过条件**：七项违规全部为 0，或非零项 100% 有登记说明。

**失败处置**：机械可修的（updated\_at 漏刷、market 笔误）当轮修；修不了的登记开放问题。

### 第 7 轮：验收收尾与夜班报告（软时限 30 分钟，**必执行**）

**操作**：

1. `websearch_ingest.py stats` 终态 vs 第 0 轮基线对比。
2. 夜班报告落盘 `.runtime/industry_graph/night_audit/report_YYYYMMDD.md`（格式见 §10）。
3. 本 SOP 若在执行中发现缺陷→小改升 1.0.1+修订记录（走 GitCommitGateway）。
4. 脚本/文档类改动全部提交（GitCommitGateway）；progress.json 终态更新（completed/remaining 清单）。
5. 对话内大白话一次性汇报（§10 格式）。

**通过条件**：报告落盘 + 汇报完成 + git status 干净（除 .runtime）+ progress 终态。

## 7. WebSearch 使用规范

1. **搜索词带年份**：`关键词 2026`（追新优先，查历史数据用对应年份）。
2. **来源分级**：
   - **一手**（可直接作 0.5 证据）：公司公告/年报、交易所披露、公司官网、政府统计、行业协会
   - **二手**（需两个独立来源互证才升 0.7）：券商研报、主流财经媒体（财新/证券时报/Reuters/Bloomberg）
   - **三手**（仅作线索，不作证据）：自媒体、百科、论坛——从三手找到的线索必须追到一手/二手原文才准落库
3. **反幻觉**：每条落库数据必须能在搜索结果原文中找到依据（evidence\_text 摘一句原文）；找不到原文依据的**不写**，登记缺口。禁止凭训练记忆编造供应链关系。
4. **限速纪律**：每链/每锚点搜索 ≤5 次；连续 2 次无有效结果→跳过登记，不刷搜索。
5. **失败处置**：搜索报错→换词重试 1 次→仍失败登记"搜索失败"缺口，继续下一目标。

### 7.6 病菌寻路采集法（swarm crawling 模板，2026-09-07 增补）

> 本项目无数据包可下载，唯一增量渠道=AI 全网搜索。寻路模式：从一段文本/一家公司出发，像病菌传播一样**沿供应链逐跳扩散**——读到谁就查谁，查到新公司就入队再查，直到停止条件。第 2 轮（按链寻路）、第 3 轮（按公司反向寻路）、第 5 轮（按年报文本寻路）共用本模板。

**单次寻路协议（每次执行按此 7 步走）**：

```
[种子]   一段文本 / 一家公司 symbol / 一条链名
[提取]   从种子中提取全部公司名（含非上市）与环节词
[访问]   对每个公司执行查询：
           "{公司名} {产品或环节} 供应商 客户 2026"
           （英文公司加一轮：" {英文名} suppliers customers 2026"）
[落库]   每次访问的产出按三件套落：
           ① 公司→环节落位（ig_node_company，evidence 摘原文一句）
           ② 供应关系边（ig_company_edge，year=信息年，product 写明供什么）
           ③ 新发现公司 → stock_basic 匹配 symbol（非上市 to_symbol=''）
[扩散]   新公司入 frontier（待访队列，宽度优先）；已访公司入 visited（防环）
[预算]   单链 ≤30 次查询 / 深度 ≤3 跳 / frontier ≤50 家
[停止]   预算尽 OR 连续 3 次访问零新增 OR frontier 全部已访
```

**扩散优先级**（预算内先访谁）：
1. P1 链上的 A 股公司（与交易决策直接相关）
2. 非上市对手方（名称入 to\_name，只建边不建落位）
3. 全球锚点公司（进第 4 轮锚点清单，不在此展开）

**纪律**：
- 每次访问必带采集日期（§4.6 时效三件套）；关系数据按信息年写 year。
- 三手来源只提供 frontier 线索，落库证据必须一手/二手（§7.2）。
- 寻路明细（访问了几家/新增几家/停止原因）写入批次 JSON 的 `crawl_log` 字段，夜班汇报汇总。
- 查到与存量矛盾的信息（如已断供还在库里）→ 不覆盖，新增带新 year 的边 + 登记开放问题。

**子代理提示词模板**（总控派单时复制）：

```
你是产业链寻路采集员。种子：{种子}。按 SOP §7.6 协议执行：
预算 30 查/3 跳；每次访问产出三件套（落位/供应边/新公司）；
写入走 websearch_ingest.py ingest（§5 批次格式）；矛盾信息登记不覆盖；
返回：{访问数, 新增公司数, 新增边数, 停止原因, 需拍板问题}。
```

## 8. 夜班编排（总控职责）

### 8.1 派单结构

- 夜班会话 = **总控**：读本 SOP、维护 progress.json、派子代理、串行收口。
- 每轮总控把工作切成批次，**单条消息内并发启动多个子代理**（最大并行度），每个子代理提示词**自包含**：
  - 本 SOP 对应轮次的操作全文复制
  - 该子代理的批次清单（哪些链/哪些行业组/哪些锚点）
  - §4 数据契约全文 + §5 工具用法
  - 返回格式：`{处理数, 写入批次文件列表, 新增记录计数（按表）, 缺口登记清单, 需拍板问题清单}`
- **子代理不直接改 progress.json**（防并发写坏）；完成后返回结果，由总控独写 progress。
- 子代理可自己跑 `websearch_ingest.py ingest`（PG 事务天然并发安全，批次文件名唯一）。

### 8.2 进度与断点续跑

progress.json 结构：

```json
{
  "night_date": "2026-09-03",
  "started_at": "…", "updated_at": "…",
  "baseline": {"ig_chain": 686, "ig_node": 2911, "...": 0},
  "rounds": {
    "round0": {"status": "completed", "note": "…"},
    "round2": {"status": "in_progress", "done": ["链A", "链B"], "pending": ["链C"], "failed": []}
  },
  "batches_written": ["round2_存储芯片链_001.json"],
  "open_questions": []
}
```

- 每批次完成即更新（总控）；会话崩溃重启后读 progress 从断点继续。
- 已 ingest 的批次不重复 ingest（幂等兜底 + progress 双保险）。

### 8.3 时间盒与收敛

- 各轮软时限见 §6；总时间盒到 07:00（`Get-Date` 实测）即收敛：停止派新批→跑第 6/7 轮（对已写入数据）→ 汇报。
- 优先级保证截断安全：P1 永远先做，任意截断点都留下"最有价值的部分已完成"。

## 9. 铁律（逐字适用）

1. **Git 安全**（同 [document\_review\_and\_optimization\_sop §6.4](document_review_and_optimization_sop.md)）：改文件后立即 `git add`；禁止 `git clean` / `git reset --hard` / `git checkout --` / `git restore` / `git stash` / `git checkout .`；提交一律走 GitCommitGateway（`python scripts/git_commit.py`，禁裸 commit、禁 --no-verify）；commit ≠ push，push 需 Owner 明确指令。
2. **文件锁**：修改 scripts/ 或 docs/ 文件前 `python scripts/lock_files.py acquire <file> <session_id>`，完成后 release。
3. **不碰交易面**：本 SOP 全程只读写 PG depgraph 库 + 项目文件，禁止触碰实盘/模拟盘/交易模块。
4. **不删数据**：§4.5，逐字适用。
5. **AI 不替 Owner 拍板**：合并链、删数据、推翻既有裁定、覆盖存量行——全部登记开放问题等醒后裁定。
6. **写完即校验即提交**：脚本/文档改动当轮提交；PG 数据写入即生效（无 git 对象），以批次文件+progress 为审计线索。
7. **实测禁记忆**：一切计数以 `stats` 实测为准，禁止凭记忆或本 SOP §2.1 基线报数（那是 2026-09-03 的旧值）。

## 10. 汇报格式（Owner 醒来看什么）

**对话内大白话汇报**（一次性，只给结果）：

```
【夜班完成度】一句话（八轮完成 X 轮 / 断点在哪）
【数据增量】基线 vs 终态表（七表计数 + 本夜新增行数按表）
【本夜做了什么】按轮次 3-5 条/轮：补了哪些链（新增节点/公司数）、落位覆盖率 46.8%→X%、锚点挂了 Y 家、供应链边补了 Z 条
【数据质量声明】websearch 行数 / confidence 分布（0.5 vs 0.7）/ 来源数 / 三手线索未落库数
【开放问题】需 Owner 拍板清单（重复链合并、死映射处置、SOP 缺陷…）
【断点与续跑】剩余批次 + 一句"下次夜班从哪继续"（如全部完成写"无"）
```

**落盘报告** `.runtime/industry_graph/night_audit/report_YYYYMMDD.md`：上述内容 + 明细（每链/每锚点处理记录、缺口总账终态、七项校验结果）。报告在 .runtime 不入 git（与 INDUSTRY\_GRAPH\_001\_report.md 同规）。

## 11. 附录：夜班速查清单

```
□ 开工
  □ 开工探测（git status + 文件锁）
  □ 施工 websearch_ingest.py（三测绿 + manifest 登记 + commit）
  □ backup 七表
  □ stats 基线 + 缺口总账五清单
  □ 链工作清单排优先级（P1/P2/P3）
□ 第1轮 存量质量：重复链核验 / 死映射 / 孤岛节点 / category 补全
□ 第2轮 链级补全：P1 链优先，find-chain 防重，每链≤5 搜索
□ 第3轮 落位覆盖：按行业组并发，目标 ≥80%，无链可挂要登记
□ 第4轮 全球锚点：预置∪高频对手方清单，三件套写入，不硬造边
□ 第5轮 供应链边：P1 链 TOP5 公司年报客户/供应商 + 新闻级变化
□ 第6轮 七项校验（必跑）：source_doc 非空 / confidence cap / symbol 正则 / market 一致 / updated_at / 重复链 / 反查 stock_basic
□ 第7轮 收尾（必跑）：stats 终态对比 / 报告落盘 / progress 终态 / git 干净 / 大白话汇报
□ 全程纪律：每批一事务 / 只增不删 / 不问用户 / 07:00 收敛
```

***

## 开放问题/待定问题

| # | 问题                                                                        | 状态   |
| - | ------------------------------------------------------------------------- | ---- |
| 1 | 全球锚点清单范围（预置+高频对手方 ≈150 家）是否合适，选取标准是否需 Owner 增删                            | 待裁定  |
| 2 | 退市/更名股的 ig\_node\_company 死映射处置（保留/标记/清理）——首次夜班后凭清单裁定                     | 待裁定  |
| 3 | websearch 数据复核周期：建议每季度夜班重扫 source='websearch' 行验证链接有效性                    | 待裁定  |
| 4 | 全球锚点是否纳入 theme\_linkage\_monitor 联动口径（当前只跑 cn ≥0.85 子集，天然不含 websearch 数据） | 待裁定  |
| 5 | chainmap 前端接线（DAL-C01/C02，P0）不在本 SOP 范围，待另行派单                             | 已知缺口 |
| 6 | 落位覆盖率 80% 目标线是否合理（剩余多为金融/综合类无链可挂）                                         | 待裁定  |

## 修订记录

| 日期         | 版本    | 改动内容                                                            | 为什么改                                                                    |
| ---------- | ----- | --------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 2026-09-03 | 1.0.0 | 初稿：建立产业链/供应链全景图数据审计与更新 SOP（夜班自主执行版），八轮循环+数据契约+WebSearch 规范+总控编排 | ig\_\* 七表数据为一次性采购包无更新机制，落位覆盖率 46.8%，缺全球锚点；Owner 需要睡前一键启动、醒来看结果的自主数据保鲜流程 |
| 2026-09-07 | 1.1.0 | 增补数据标准与采集模板：§4.6 七表字段字典（含时效三件套+过期公式）｜§4.7 命名与词表标准（链名规范/tier 9 值/category 申万 31 类/半导体链名治理样板 15→8）｜§7.6 病菌寻路采集法（种子→逐跳扩散→预算停止，7 步协议+子代理模板）｜第 0 轮缺口清单+第 1 轮治理动作挂接新标准｜工具硬校验扩至 9 条 | Owner 2026-09-07 指令：先定数据字段标准写入 SOP，再定全网搜索寻路模板（无数据包可下载，增量只能靠 AI 联网逐跳采集）；更新时间是快速定位过时数据的主键 |

