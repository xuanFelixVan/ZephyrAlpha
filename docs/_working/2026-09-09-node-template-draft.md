---
ttl: task_bound
---

# 节点模板草案（Owner 审定稿前不动工引擎/门禁）

> **状态**：草案 v0.2（2026-09-09 股权穿透三裁定并入），待 Owner 圈改。
> **配套**：graph_quality_standard.md §6~§8（深度体系/详情卡/三查 S21~S23）——本文档是**字段级落地样例**，审定后字段标准回写标准文件，引擎按审定稿施工。

## 〇、链模板（第一层：链本身就是一种节点——全景图的三种节点）

```yaml
chain:
  chain_id: CH-xxxxxxxxxxxx        # 自动生成
  name: 半导体产业链                # 规范名（"XX产业链"句式，禁标题腔）
  category: 半导体                  # 申万 38 词表（一级分类）
  version_year: 2026                # 信息版本年（内容描述哪一年的实态）
  market: cn                        # cn/global
  status: active                    # active/deprecated（deprecated 必带 merged_into）
  source_note: "查询词|URL|2026-09-09"   # 首建来源
  # ---- 深度体系（链层视角）----
  level: 1                          # 层级：L1 主链/L2 子链/L3 孙链…（派生可算，也可落库加速查询）
  parent_node: ND-xxxxxxxxxxxx      # 挂接到父链的哪个环节节点（L1 根链为 NULL）
  #   注：这是 node.child_chain_id 的反向视角——同一关系两边都能查
  # ---- 骨架（链的内部结构，R2 扩产主对象）----
  structure:                        # structure 边串起来的流程主干
    flow: 半导体材料→半导体设备(支撑)→芯片设计→晶圆制造→封装测试→终端应用
    edges_count: 6                  # S21 审查：主干必须连通
  # ---- 验收口径 ----
  acceptance:
    nodes_min: 3                    # 链合格线：≥3 环节（SOP §5 stats 已有此指标）
    companies_min: 5                # 落位公司建议下限（低于=骨架空）
    p1_priority: true               # 是否 P1 链（决定下钻深度要求）
```

**链节点必填**：name/category/market。**关键决策**：level 和 parent_node 是"落库"还是"派生"——落库查询快但要维护一致性（挂接变更时两处同步）；派生省维护但每次递归查。我建议 **parent_node 不落库（由 node.child_chain_id 反查派生，单一真源）**，level 落库（写挂接时顺手写，防递归爆栈）。

**三种节点的对比总览**：

| | 链节点 | 环节节点 | 公司节点 |
|---|---|---|---|
| 是什么 | 流程全景（一个产业） | 流程步骤（链上一步） | 参与者（落到环节上的公司） |
| 主键 | CH- | ND- | symbol（/UE-） |
| 上下 | 父链（经 parent_node）/子链（经环节挂接） | 同链前后环节（structure 边）/子链（child_chain_id） | 上游供应商/下游客户（company_edge） |
| 模板核心字段 | name/category/version_year/level/parent_node | name/tier/child_chain_id/drill_status | positions/upstream/downstream/标签/简介 |
| 引擎审查 | S1~S5 | S6~S9+S21~S22 | S10~S14+S23 |

## 一、环节节点模板（链上的"流程步骤"，如"晶圆制造"）

```yaml
node:
  node_id: ND-xxxxxxxxxxxx          # 自动生成
  chain_id: CH-xxxxxxxxxxxx         # 所属链
  name: 晶圆制造                    # 纯环节名（禁后缀/禁标题腔）
  tier: 中游                        # 上游/中游/下游/设备/材料/零部件/原材料/辅材
  aliases: [晶圆厂, Fab, IC制造]     # 别名（搜索用）
  description: 在硅片上光刻蚀刻出电路图形，是芯片制造的core环节   # 一句话+关键参数
  market: cn
  # ---- 深度体系列（DDL v4 已建）----
  child_chain_id: CH-yyyyyyyyyyyy   # 下钻子链（NULL=未挂）；样例：挂"晶圆制造产业链"
  drill_status: child               # child/brick_mass/brick_noalpha/NULL(待判定)
  # 例：某"稀土精矿"节点 drill_status=brick_mass（通用大宗原料，判据A）
  # 例：某"树脂合成"节点 drill_status=brick_noalpha（下钻无A股标的，判据B）
```

**环节节点必填**：name/tier/market。**可选**：aliases/description/child_chain_id/drill_status。

## 二、公司节点模板（落到环节上的"公司"，即详情页主体）

```yaml
company:
  symbol: 688825.SH                 # 身份：代码（UNLISTED:UE-xxx 或真代码）
  name: 长鑫科技                    # 身份：名称
  market: cn
  # ---- 坐标（挂在哪）----
  positions:                        # 多链多环节合法，每条一条坐标
    - chain: 半导体产业链           # 链名（L1 主链）
      node: 存储晶圆制造            # 环节名
      tier: 中游
      role: 龙头                    # 五值：龙头/核心/主要/参与/提及
      chain_path: 半导体产业链      # 层级路径（渐进字段：样板链验收后必填）
  # ---- 上下游（左右邻居）----
  upstream:                         # 供应商边（我是 to_symbol）
    - {party: 中微公司, symbol: 688012.SH, product: 刻蚀设备, year: 2026,
       valid_from: 2026-01-01, as_of: 2026-09-09, evidence: "原文摘录一句"}
  downstream:                       # 客户边（我是 from_symbol）
    - {party: 江波龙, symbol: 301308.SZ, product: DRAM颗粒, year: 2026, ...}
  # ---- 标签（横坐标）----
  ths_industry: 半导体              # THS 二级标签（行业聚合链落位）
  sub_industry: 数字芯片设计        # THS 三级细分（257 值，新）
  sw_category: 半导体               # 申万一级（链 category）
  csrc_industry: 制造业             # 证监会行业（SHOULD，交叉验证用）
  # ---- 资本关系域（Owner 2026-09-09 裁定：独立股权表，与供应边彻底分域）----
  equity:                           # 全部来自 ig_equity_edge（新表），查询侧拼装
    holdings_in:                    # 我投了谁（对外投资，THS 被投列+年报口径）
      - {party: 声通科技, stake: 15.2%, as_of: 2025FY年报}
    held_by:                        # 谁投了我（股东，含穿透链）
      - {party: 合肥产投, stake: 22.1%, layer: 1, actual: true}
    subsidiaries: [UE-xxx, UE-yyy]  # 子公司 UE 编码列表（回链编码表）
    actual_controller: {name: 合肥国资委, type: 国资, country: CN}
    pledge_ratio: 0.0               # 大股东质押比例（A股避坑刚需，SHOULD）
  # ---- 新闻联动域（供新闻引擎实体匹配+影响面扩散）----
  news_keywords: [DRAM, 存储芯片, HBM, 合肥]   # 新闻关键词（海峡→石油股全命中类）
  aliases: [长鑫, CXMT, 长鑫存储]     # 别名集（实体匹配主力：中英简称/曾用名）
  index_membership: [科创50, MSCI中国]  # 指数成分（被动资金流量放大器）
  mcap_tier: 大盘                   # 市值档（新闻资金容量分组）
  soe_flag: true                    # 国资属性（同新闻国企民企反应方向不同）
  # ---- 全球属性（Owner 2026-09-09 增）----
  country: CN                       # 国籍
  listing_venue: 上交所科创板        # 上市市场（纳斯达克/港交所/未上市…）
  listing_status: listed            # listed/unlisted/delisted（与编码表枚举统一）
  listing_date: 2026-07-27          # 上市日（PIT）
  delisting_date: null              # 退市日（未退市 null）
  dual_listing: [A]                # 多市场挂牌（A+H/ADR——美股新闻传导A股通道）
  st_flag: false                    # ST/风险警示标记
  # ---- 日历域 ----
  calendar: {earnings: 2026-10-28, unlock: null, ex_div: null}   # 财报/解禁/除权（新闻时间锚）
  # ---- 内容 ----
  profile: 国内唯一DRAM IDM，全球第四大DRAM厂商…   # ig_chunk ths_profile
  # ---- 质量 ----
  confidence: 0.7
  source_doc: "查询词|URL|2026-09-09"
```

**字段分级**（标准文件 §7，审定点；v0.2 扩至七域）：

| 级别 | 字段 | 说明 |
|---|---|---|
| MUST（缺=残缺） | symbol/name/market/country/listing_status/坐标≥1条（链+环节+role）/sw_category(A股)/质量三件 | 引擎 S23 可审 |
| SHOULD（缺=登记） | upstream≥1 / downstream≥1 / ths_industry / profile / listing_venue+listing_date / aliases（A股） | 源头公司豁免上游、终端公司豁免下游，均须登记 |
| SHOULD-股权域 | holdings_in≥0 / actual_controller（A 股） | 缺=登记；股权数据源齐后升 MUST |
| SHOULD-新闻域 | news_keywords / index_membership / mcap_tier / soe_flag | 缺=登记；新闻引擎上线前补齐 |
| DERIVED（不落库） | 上二层/下二层传递上下游 / chain_path | 查询侧实时算（二层闭包+child_chain_id 递归） |
| 渐进 | pledge_ratio / calendar / sub_industry / csrc_industry / dual_listing / st_flag | 半导体样板链验收后分批转 MUST |
| **未来扩展点（三年内不建）** | 高管表（董监高变更）/诉讼表 | 字段位声明，新闻引擎成熟后评估 |

## 2.5、股权穿透表设计（ig_equity_edge，Owner 2026-09-09 裁定：同库独立表，与 ig_company_edge 分域）

```sql
CREATE TABLE ig_equity_edge (
    edge_id     BIGSERIAL PRIMARY KEY,
    holder      TEXT NOT NULL,        -- 持有方 symbol（688825.SH / UNLISTED:UE-xxx / 人名前缀 PERSON:）
    held        TEXT NOT NULL,        -- 被持有方 symbol/UE
    stake_pct   NUMERIC,              -- 持股比例（%，可 NULL=未披露具体比例）
    layer       SMALLINT DEFAULT 1,   -- 穿透层（1=直接持有，2=一层间接…）
    relation    TEXT NOT NULL,        -- 封闭枚举: invests_in(对外投资)/subsidiary(控股子公司)/
                                      --            shareholding(一般持股)/actual_control(实控)
    as_of       DATE,                 -- 股权口径日（年报=报告期末，公告=公告日）PIT
    valid_from  DATE,                 -- 关系生效日（增减持事件日）
    valid_to    DATE,                 -- 减持/清仓日（未终止 NULL）
    source      TEXT NOT NULL,        -- ths_export/websearch/annual_report
    source_doc  TEXT,                 -- 三段式溯源
    evidence    TEXT,                 -- 原文摘录（"持有XX公司15.2%股权"）
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (holder, held, as_of, source)   -- 幂等锚
)
```

**分流纪律（裁定 12）**：
- 被**投**关系/持股比例/实控人/质押 → `ig_equity_edge`（THS 被投 922 条+年报口径年份戳**进本表**）
- 供应/客户/竞争/合作/生产/归属 → `ig_company_edge`（业务传导，现状不变）
- **两表互不相混**：写入工具按 record type 分发，查公司详情页时查询侧 UNION 拼装（一个 symbol 两个域一起看）
- 人名类持有方（实控人/自然人股东）用 `PERSON:姓名` 前缀（与 UNLISTED: 同风格，查询可过滤）

## 三、三层实样（用你的图例，落库后长这样）

### L1 半导体产业链（主链，根链）

```
半导体产业链 (CH-a1b2c3, 根链, 无父)
├─ [上游] 半导体材料 ── drill_status=child → 子链:半导体材料产业链
├─ [上游] 半导体设备 ── drill_status=child → 子链:半导体设备产业链
├─ [上游] EDA软件     ── drill_status=NULL(待下钻判定)
├─ [中游] 芯片设计    ── drill_status=NULL
├─ [中游] 晶圆制造    ── drill_status=NULL
├─ [中游] 封装测试    ── drill_status=child → 子链:封装测试产业链
└─ [下游] 终端应用    ── drill_status=NULL
   落位公司举例：中微公司(设备·龙头)、长鑫科技(晶圆制造·龙头)、长电科技(封测·龙头)
   structure 边：材料→晶圆制造→封装测试→终端应用（流程主干，S21 审查对象）
```

### L2 封装测试产业链（子链，被 L1"封装测试"节点挂接）

```
封装测试产业链 (CH-d4e5f6, 父=L1.封装测试节点)
├─ [上游] 封装材料   ── drill_status=child → 子链:封装基板行业
│   落位：深南电路(基板·核心)、兴森科技(基板·主要)、康强电子(框架·主要)
├─ [上游] 封装设备   ── drill_status=child → 子链:划片机产业链（下例）
│   落位：Disco(划片机·全球龙头 3745.T)、光力科技(空气主轴·龙头 300480.SZ)
├─ [中游] 封装服务   ── drill_status=NULL
│   落位：长电科技(全球前三·龙头 600584.SH)、通富微电(全球第四·核心 002156.SZ)
├─ [中游] 测试服务   ── drill_status=NULL
└─ [下游] 终端应用   ── drill_status=brick_mass（通用大宗应用面，判据A）
```

### L3 划片机产业链（孙链，被 L2"封装设备"节点挂接）

```
划片机产业链 (CH-g7h8i9, 父=L2.封装设备节点)
├─ [上游] 空气主轴   ── drill_status=brick_noalpha（再拆无A股新标的,判据B）
│   落位：光力科技(300480.SZ)
├─ [上游] 切割刀片   ── drill_status=NULL
│   落位：西斯特科技(688608.SH)
├─ [中游] 划片机整机制造 ── drill_status=brick_mass（整机即产品,判据A）
│   落位：Disco(3745.T·全球龙头)、京创先进(未上市→UE-xxx)、和研科技(未上市→UE-xxx)
└─ [下游] 封测厂应用 ── drill_status=brick_noalpha（客户即L2中游已覆盖）
```

> 注：以上公司/链 id 为示意，实际以库内存量为准；本样例只定**字段与挂接形态**。

## 四、待 Owner 圈改的决策点（2026-09-09 裁定进展：10/14 已定）

| # | 决策点 | 状态 |
|---|---|---|
| 1 | drill_status 四值 | 待圈 |
| 2 | 同一环节挂多条子链=禁（多主题拆多环节） | 待圈（建议禁） |
| 3 | chain_path 渐进转 MUST 时机=半导体样板链验收后 | 待圈 |
| 4 | 上下游豁免口径=源头豁上游/终端豁下游登记制 | 待圈 |
| 5 | 子链 tier 语义=本链视角 | 待圈 |
| 6 | 砖判据依据写环节 description | 待圈 |
| 7 | tier 六值自洽 | 待圈 |
| 8 | 链 level 落库/parent_node 派生 | 待圈 |
| 9 | 链骨架验收线 companies_min=5 | 待圈 |
| 10 | **股权穿透独立表（Owner 2026-09-09 已裁定）**：ig_equity_edge 与供应边表彻底分开；THS 被投 922 条+年份戳进股权表；子公司 UE 编码回链 | ✅ 已裁定 |
| 11 | **股权与供应同夜并行（已裁定）**：子代理查公司时两个表各填各的，互不污染 | ✅ 已裁定 |
| 12 | **股权表数据分流（已裁定）**：被投关系/持股比例/实控人/质押→ig_equity_edge；供应/客户/竞争/合作→ig_company_edge；产品/环节落位→落位表 | ✅ 已裁定 |
| 13 | 国籍/上市市场/上市状态/新闻关键词+别名集→公司主表（扩展点六组按建议档位） | 待圈（高管表降未来扩展点） |
| 14 | 高管表三年内不建（字段位声明"未来扩展点"） | 待圈（建议同意） |
| 15 | **供应边补两列（已裁定）**：capacity 产能（吨/片/GWh 供给侧瓶颈变量）+exclusivity 独供/双供（断供冲击弹性） | ✅ 已裁定（DDL 已建） |
| 16 | **财务表分域（已裁定）**：通用财务主数据进 c1_market（与行情同库、采购/下载通道、禁 AI 搜索）；图谱侧只建 ig_product_revenue 产品营收归因（年报文本抽取） | ✅ 已裁定（DDL 已建） |
| 17 | **ig_company_metric 处置（已裁定）**：供应链集中度指标层保留不融不删（五层架构第五层：文档→内容→事实→图谱→指标），PIT 化改造 | ✅ 已裁定（DDL 已建） |

## 五、审定后的动工清单（待你放行）

1. 标准文件 §6~§8 按审定稿回写（v1.3.0，含链节点模板）
2. 引擎加 S21~S23（进度指标段，样板验收后升硬闸）+链骨架验收（S24 候选：companies_min 低于阈值进报告）
3. SOP §6 第2轮挂"深度下钻协议"（病菌寻路顺带判定 drill_status）
4. websearch_ingest node 记录支持 child_chain_id/drill_status 写入+校验（drill_status=child 时 child_chain_id 必填交叉校验）；ig_chain 加 level 列（DDL v4 已含 node/company 列）
5. 长城指令书 Phase 5 扩产段挂"半导体样板链"专项（L1 建主干→L2 挂接→L3 下钻→砖判定→公司详情卡打样）
