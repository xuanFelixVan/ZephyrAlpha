---
ttl: task_bound
---

# 节点模板草案（Owner 审定稿前不动工引擎/门禁）

> **状态**：草案 v0.5（2026-09-09 终稿：四决策点 Owner"按建议"全裁定+股权表 21 列全量同步+质押事件化），**审定通过，可放行**。
> **配套**：graph_quality_standard.md §6~§8——本文档是**字段级落地样例**，字段标准回写标准文件在长城任务收尾轮执行。
> **权威对标（2026-09-09 全网调研）**：深交所课题《资本市场产业链图谱业务标准及数据标准研究》（申万三级+第四层起开放延伸，与本体系同构）｜济安金信 45/144/369 三级架构｜GICS 4 层｜人行《受益所有人信息管理办法》｜FactSet Supply Chain API｜W3C PROV-O。

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
  tier: 中游                        # 链内位置（v0.4 语义收窄）：上游/中游/下游——仅三值，L1 主链口径；子链视角递归（划片机链里"空气主轴"=该链上游）
                                   # 【Owner 2026-09-09 质疑裁定改造】原 9 值混职能已废弃：设备/材料等职能拆到 function_role
  function_role: 加工工艺           # 职能角色（新字段，深交所课题八大关系词表）：
                                   # 生产设备/生产原料/辅助材料/辅助设备/加工工艺/技术服务/产品业务/销售渠道
                                   # AI 应用公司=技术服务或产品业务（职能语义，绝对概念不随链变）
  aliases: [晶圆厂, Fab, IC制造]     # 别名（搜索用）
  description: 在硅片上光刻蚀刻出电路图形，是芯片制造的core环节   # 一句话+关键参数
  market: cn
  # ---- 深度体系列（DDL v4 已建）----
  child_chain_id: CH-yyyyyyyyyyyy   # 下钻子链（NULL=未挂）；样例：挂"晶圆制造产业链"
  drill_status: child               # child/brick_mass/brick_noalpha/NULL(待判定)
  # 例：某"稀土精矿"节点 drill_status=brick_mass（通用大宗原料，判据A）
  # 例：某"树脂合成"节点 drill_status=brick_noalpha（下钻无A股标的，判据B）
```

**tier 与 function_role 分离依据（Owner 2026-09-09 质疑驱动）**：位置（上游/中游/下游）是**相对概念**随链变，职能（设备/原料/工艺/服务）是**绝对概念**不随链变——原 9 值词表把两者混在一个字段语义不干净；深交所课题与招商图谱指南的权威实践均为"三位置+职能关系词表"分离式。存量 5,215 只股票 tier 迁移：位置值保留、职能值迁 function_role（治理脚本一次性）。

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
  # ---- 资本关系域（Owner 2026-09-09 裁定：独立股权表 ig_equity_edge，与供应边彻底分域）----
  # ⚠️ 视图澄清：本段是【详情页展示视图】——查询时从 ig_equity_edge 拼装，数据物理上只存股权表一处
  #    （模板段落=效果图，表=房子本身）。成本价/取得日期两字段随裁定新增（股权避坑核心：浮亏浮盈+减持动机）
  equity:                           # ← 视图字段，来源=ig_equity_edge
    holdings_in:                    # 我投了谁（对外投资）
      - {party: 声通科技, stake: 15.2%, as_of: 2025FY年报,
         acquisition_cost: 2.1亿, acquisition_date: 2024-06-30,   # 取得成本+取得日（新增，PIT）
         pit_strength: weak}        # ⚠️ THS 年报口径=weak；websearch 复核一手公告后升 strong
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
  hq_location: 合肥·安徽·中国       # 总部地理（FactSet Revere 实践：地缘风险推演/台海情境模拟用）
  listing_venue: 上交所科创板        # 上市市场（纳斯达克/港交所/未上市…）
  listing_status: listed            # listed/unlisted/delisted（与编码表枚举统一）
  listing_date: 2026-07-27          # 上市日（PIT）
  delisting_date: null              # 退市日（未退市 null）
  dual_listing: [A]                # 多市场挂牌（A+H/ADR——美股新闻传导A股通道）
  st_flag: false                    # ST/风险警示标记
  # ---- 设施域（GitHub supply-chain-kg 实践：Facility 节点轻量化为公司字段）----
  facilities:                       # 产能地理点（capacity 列的地理维度）
    - {site: 合肥空港工业园, type: 12英寸DRAM晶圆厂, capacity: 12万片/月, country: CN}
  # ---- 溯源六件套（W3C PROV 六问对齐，v0.3 全网调研增补）----
  source: ths_export                # ① 来源（已有）
  source_doc: "查询词|URL|日期"      # ② 证据链接（已有）
  evidence: "原文摘录"              # ③ 证据原文（已有）
  info_channel: 巨潮资讯网          # ④ 信息渠道（新：公司公告发布渠道，爬虫着陆点）
  source_url: https://...           # ⑤ 渠道入口网址（新：详情页/披露页 URL）
  refresh_policy: {freq: quarterly, next_due: 2026-12-31, last_checked: null,
                   checker: null}   # ⑥ 更新策略（新：频率+下次到期+上次核验+核验人；S25 审查对象）
  # ---- 日历域 ----
  calendar: {earnings: 2026-10-28, unlock: null, ex_div: null}   # 财报/解禁/除权（新闻时间锚）
  # ---- 内容 ----
  profile: 国内唯一DRAM IDM，全球第四大DRAM厂商…   # ig_chunk ths_profile
  # ---- 质量 ----
  confidence: 0.7                  # （溯源见六件套,此处不重复 source_doc）
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
    edge_id           BIGSERIAL PRIMARY KEY,
    holder            TEXT NOT NULL,     -- 持有方（688825.SH / UNLISTED:UE-xxx / PERSON:人名）
    held              TEXT NOT NULL,     -- 被持有方（symbol/UE）
    stake_pct         NUMERIC,           -- 持股比例 %（NULL=未披露）
    voting_pct        NUMERIC,           -- 表决权比例（人行办法六条二款,AB股场景）
    layer             SMALLINT DEFAULT 1,-- 穿透层（1=直接,2=一层间接…）
    relation          TEXT NOT NULL,     -- 封闭枚举六值: invests_in/subsidiary/shareholding/
                                        --   actual_control/pledge(质押)/judicial_frozen(司法冻结)
    control_method    TEXT,              -- 控制方式（人行六条三款: 股权/协议/亲属/一致行动人）
    acquisition_cost  NUMERIC,           -- 取得成本（Owner 2026-09-09 裁定:浮亏浮盈+减持动机）
    acquisition_date  DATE,              -- 取得日（PIT）
    as_of             DATE,              -- 股权口径日（年报=报告期末/公告=公告日）
    valid_from        DATE,              -- 关系生效日（增减持/质押起始日）
    valid_to          DATE,              -- 减持/清仓/解押日（未终止 NULL）
    holder_name       TEXT,              -- 自然人姓名（EU 5AMLD 必填,PERSON: 行配套）
    holder_country    TEXT,              -- 持有方国籍（EU 5AMLD 必填）
    verification      TEXT,              -- 核验状态 unverified/verified/official（瑞士LETA纪律）
    source            TEXT NOT NULL,     -- ths_export/websearch/annual_report
    source_doc        TEXT,              -- 三段式溯源
    evidence          TEXT,              -- 原文摘录；pledge 行存"平仓线=收盘价×质押率×比例"公式与数值
    created_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE (holder, held, as_of, source) -- 幂等锚
)
-- 21 列，达国际 UBO 登记标准（人行+瑞士LETA+EU 5AMLD 三方对标）；DDL 已部署
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

## 四、决策点终态（2026-09-09 Owner"按建议"全裁定，17/17 定案）

| # | 决策点 | 状态 |
|---|---|---|
| 1 | drill_status 五值：child/brick_mass/brick_noalpha/NULL/drill_manual（人工钉死 AI 永不改） | ✅ 已裁定 |
| 2 | 同一环节挂多条子链=禁（多主题拆多环节） | ✅ 已裁定 |
| 3 | chain_path 渐进转 MUST 时机=半导体样板链验收后 | ✅ 已裁定 |
| 4 | 上下游豁免口径=源头豁上游/终端豁下游登记制 | ✅ 已裁定 |
| 5 | 子链 tier 语义=本链视角（递归） | ✅ 已裁定 |
| 6 | 砖判据依据写环节 description | ✅ 已裁定 |
| 7 | tier 三值（上中下游）+function_role 八值（深交所词表）分离 | ✅ 已裁定 |
| 8 | 链 level 落库/parent_node 派生（单一真源） | ✅ 已裁定 |
| 9 | 链骨架验收线 companies_min=5 | ✅ 已裁定 |
| 10 | **股权穿透独立表**：ig_equity_edge 与供应边表彻底分开；THS 被投 922 条+年份戳进股权表；子公司 UE 编码回链 | ✅ 已裁定 |
| 11 | **股权与供应同夜并行**：子代理查公司时两个表各填各的，互不污染 | ✅ 已裁定 |
| 12 | **股权表数据分流**：被投/持股/实控/质押→ig_equity_edge；供应/客户/竞争/合作→ig_company_edge；产品/环节落位→落位表 | ✅ 已裁定 |
| 13 | 国籍/上市市场/上市状态/新闻关键词+别名集→公司主表（七域按 v0.4 档位） | ✅ 已裁定 |
| 14 | 高管表三年内不建（字段位声明"未来扩展点"） | ✅ 已裁定 |
| 15 | **供应边补两列**：capacity 产能+exclusivity 独供/双供 | ✅ 已裁定（DDL 已建） |
| 16 | **财务表分域**：通用财务主数据进 c1_market（采购通道禁 AI 搜索）；图谱侧只建 ig_product_revenue | ✅ 已裁定（DDL 已建） |
| 17 | **ig_company_metric 处置**：指标层保留不融不删（五层第五层），PIT 化 | ✅ 已裁定（DDL 已建） |

## 五、审定后的动工清单（待你放行）

1. 标准文件 §6~§8 按审定稿回写（v1.3.0，含链节点模板+溯源六件套+专业名词对照）
2. 引擎加 S21~S23（进度指标段，样板验收后升硬闸）+S24 链骨架+S25 新鲜度（refresh_policy 到期未检=违规候选进待更新队列）
3. SOP §6 第2轮挂"深度下钻协议"（病菌寻路顺带判定 drill_status）
4. websearch_ingest node 记录支持 child_chain_id/drill_status 写入+校验（drill_status=child 时 child_chain_id 必填交叉校验）；ig_chain 加 level 列（DDL v4 已含 node/company 列）
5. 长城指令书 Phase 5 扩产段挂"半导体样板链"专项（L1 建主干→L2 挂接→L3 下钻→砖判定→公司详情卡打样）

## 六、专业名词对照表（2026-09-09 全网调研定稿——对齐 FactSet/W3C，不推翻只补齐）

**调研结论**：我们的 edge_type v2 词表与 FactSet 官方 API 的四大类（customer/supplier/partner/competitor+13 子类型）**语义一一对应，不需要换词**。需要补齐的是命名规范、别名归一层、以及以下对照：

| 我们的名 | FactSet 标准名 | 说明 |
|---|---|---|
| supplies_to | SUPPLIER（四类之一）| 方向语义一致（供应商→客户）|
| customer_of | CUSTOMER | 反向冗余边，FactSet 同做法（任一公司视角可查）|
| competitor_of | COMPETITOR | 一致 |
| partners_with | PARTNER | 一致 |
| produces | —（FactSet 无，ArthaNethra 有 PRODUCES） | 保留（产品域） |
| belongs_to_sector | —（FactSet 用 RBICS/GICS 行业） | 保留（申万归属） |
| （无）| relationship_id（REL-GCID-x-GCID-y） | **采**：边的持久 ID（我们用 edge_id 序列，等价） |
| （无）| relevance rankings | 已有 relevance 列 |
| （无）| centrality measures | DERIVED 查询侧算（度中心性），不落库 |
| （无）| keywords | **采**：边级关键词（我们只在公司级有 news_keywords）——边表加 keywords TEXT[] |

**命名规范对齐（ArthaNethra 教训：40+ 别名归一到 26 类型，禁自由文本）**：
- 词表封闭枚举已有（工具硬校验），补**关系别名映射表** `relation_alias_map.yaml`：中文别名（"供货/供应/卖给/采购自"→supplies_to）→ 写入时归一，防子代理自由发挥
- 命名风格：蛇形（已是）；股权表 relation 四值（invests_in/subsidiary/shareholding/actual_control）与 ArthaNethra 的 INVESTED_IN/SUBSIDIARY_OF/OWNS 语义对应，保留我们的命名

## 七、供应链 vs 产业链字段对照（2026-09-09 定稿：同库同表+edge_type 读法开关）

| 维度 | 产业链读法 | 供应链读法 |
|---|---|---|
| 查询开关 | edge_type='structure' | edge_type IN (supplies_to, customer_of, …) |
| 表 | ig_chain→ig_node→ig_edge | ig_company_edge（21→23 列） |
| 核心字段 | 环节名/tier(三值)/function_role(八值)/child_chain_id/drill_status | product/year/PIT 三时间戳/weight/revenue_pct/evidence_type/subsidiary/relevance/transmission_type/**capacity**/**exclusivity**/**keywords** |
| 机构对标 | Wind/Choice 三层产业树+深交所八大关系 | FactSet Revere 21 维边属性 |
| 增删 | 每条 structure 边=流程一步 | 供给侧瓶颈+独供弹性+关键词联动 |

**边表列终态（DDL 已全建）**：capacity/exclusivity/keywords TEXT[] 均已部署。公司级溯源六件套中 info_channel/source_url/refresh_policy 三列为**公司主表扩展**（施工时机=爬虫体系立项时，现在只在模板留位）。**tier 迁移治理项**：存量 ig_node 的职能值 tier（设备 522/材料 542/零部件 117/原材料 237/辅材 15 ≈1,433 行）迁 function_role，tier 保留仅三位置值——引擎 S6 与工具校验**同 commit 同词表**切换（三值+八值），防漂移。
