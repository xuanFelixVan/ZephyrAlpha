---
ttl: task_bound
title: 环节④ 传导标的集——链图谱双真源收敛方案与事件方向语义两路线
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节④ 传导标的集（链图谱双真源收敛＋方向语义）

> **目标形态**（研究册 §1.2④）：板块→个股映射+传导强度排序（链上位置×传导时滞×龙头分档）；个股级考试属个股信号域（边界）。
> **红线**：热度传导月 IC=-0.029 禁用（docs/03_modules/_domain_frontend/acceptance/ACC-F-CHAINMAP-CATALYST.yaml:25 实查复认："只做事件命中定位，不做涨跌/传导预测"）；事件方向语义建成前管线只定位不判向。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|------|------------------|---------|--------|------|---------|
| PG ig_* 大图（DDL 真源） | scripts/industry_graph/apply_industry_graph_ddl.py:54-407（**15 个 CREATE TABLE=14 个 ig_\*+stock_concept**；ig_edge 结构 :80-90=edge_type structure\|supply，UNIQUE(from,to,type)；ig_node_company :92-106 PIT） | ✅ production（DDL-as-Code 头注；幂等） | W3/W4/W5 链路（linker/resolver/stream 三件经 depgraph_schema 只读） | **ig_equity_edge DDL 有（:296）而 PG 实查不存在**（2026-10-13 关系缺失）——DDL 段未部署或分域差异 | ①语料/CKG/THS/IO 四源导入 ②W3-W5+chainmap 前端 ③DDL-as-Code ④已落 ⑤chainmap ⑥下三行 |
| ├ PG 实查规模 | 2026-10-13 只读实查：ig_chain 873 / ig_node 5,560 / ig_edge 1,726（structure 1,478+supply 212+supplies_to 36）/ ig_node_company 25,559 / ig_company_edge 58,207 / ig_fact 264,072 / ig_chunk **5,200**（=03_graph_registry.md:19 实查口径；76,112=E 盘语料块口径，DDL 头注:24——双口径在册）/ ig_io_edge 16,859 / stock_concept 61,053 / ig_unlisted_entity 14,070 / ig_product_revenue 165,255 | ✅ | — | ig_chain 873 行（含 level 子链层级）vs 前端"61 条主链"两口径并存 | ①- ②- ③- ④实测 ⑤- ⑥实测 |
| SQLite 小图（MOD-SIG-125） | src/zephyr/signal_ashare/industry_chain_graph.py:53-70（ic_nodes/ic_edges 两表；边词表 supply\|material\|demand\|byproduct、权重∈(0,1]）+ :88 EdgeKind + :134-147 IndustryChainGraph（BFS decay^跳数×边权连乘，确定性排序） | ✅ production（头注）但**零生产实例化**——`IndustryChainGraph(` 全仓非测试零调用（grep 实查；quality_closeout_governance/gen_obj_r3 为 ast/topic 同名误匹配） | 头注写"运行时装配批"（未落地） | **双真源核心事实：小图是空库库件**——无数据、无调用方、与 PG 互不联通（研究册 §6.4 复认成立） | ①（设计上）PG 投影 ②设计上信号装配 ③乘积衰减 BFS ④库件在产数据⬜ ⑤- ⑥⬜ |
| news_chain_node_linker（W3 词表定位） | src/zephyr/intelligence/news_chain_node_linker.py:6-15（testing；词表=ig_node JOIN ig_chain active，墓碑剔除、泛化聚合名自动排除、最长词优先+span 占用） | 🔨 | chain_impact_resolver/stream | **已消费 PG 大图**（depgraph_schema 只读）——W3 起链路就在 PG 侧 | ①PG ig_node ②W4/W5 ③规则匹配 ④已落 ⑤- ⑥ig_node 在 |
| chain_impact_resolver（W4 冲击标的） | src/zephyr/intelligence/chain_impact_resolver.py:6-13（testing；ig_edge **无向** BFS N 跳默认 2；方向由调用方传入 polarity∈[-1,1]、±0.15 死区；**方向符号全跳同向保留（板块联动假设；成本反号留事件类型细分后迭代，known simplification）**；公司映射 PIT valid_to IS NULL） | 🔨 | chain_impact_stream；TDM-E-L2-09-2 | **方向语义缺口本体**（研究册 §6.5）：涨价=上下游同受益的假设在"断供/成本反号"场景失真 | ①W3 hits+polarity ②W5/地图 ③无向 BFS ④已落 ⑤- ⑥ig_edge/ig_node_company PIT |
| chain_impact_stream（W5 盘中流） | src/zephyr/intelligence/chain_impact_stream.py:6-15（testing；单拍 run(now) 无常驻、PIT 严格、fail-open、TTL 缓存 600s、RuleBasedSentimentScorer 复用） | 🔨 | api_server.py:4793 `GET /api/chain-impact-stream`（只读端点实查）＋TDM-E-L2-09-1/2 预留 | 情绪方向=规则评分器（L1-S0-1），LLM 蒸馏替换位在（可注入） | ①CH 新闻+图谱 ②前端只读端点 ③事件流 ④已落 ⑤已接 ⑥news_data 多版本表 |
| sector_conduction（强度加权传导核） | src/zephyr/signal_ashare/core/sector_conduction.py:6-19（design，MOD-SIG-136；锚点系数封闭 10 分=+15%/6 分=+5%/<6 分=-10%、乘数∈[0.90,1.15]、先传导后归一） | 🔨 design | TDM-E-L2-06-3；G05 打分池（待接线） | 传导时滞×链上位置排序（目标形态）未建——现只有强度单维乘数 | ①板块强度(DS-059) ②L2-06-3 ③锚点乘数 ④已落码 ⑤- ⑥- |
| policy_theme_mapper / concept_factor_mapper | src/zephyr/alt_data/policy_theme_mapper.py:6-9 / concept_factor_mapper.py:6-9（均 design；**beneficiary/damaged 方向词表已在**（主题→申万受益/受损）；PIT 严格版本行） | 🔨 design 未投产 | 运行时装配批 | **方向语义路线 A 的现成地基**：受益/受损映射已落码，缺主题→链投影 | ①政策新闻 ②ACC-F 前端/信号 ③规则+LLM 回落 ④判定核在 ⑤- ⑥在 |
| supply_chain_momentum（同源补涨比价） | src/zephyr/signal_ashare/supply_chain_momentum.py:6（production） | ✅ | TDM-E-L2-10 | - | ①链上动量 ②TDM-E-L2-10 ③- ④已落 ⑤- ⑥- |
| 事件方向语义件（两路线） | ⬜ 未建（研究册 §6.5） | ⬜ | T-12 催化证伪+W4 | **路线 A=规则词表**（MOD-ALT-005 beneficiary/damaged 直引，ACC-F 已按此落地 11 项别名归一）/ **路线 B=LLM 蒸馏分类**（2608.14014 方法论：任务专用蒸馏、拒绝零样本——2606.12210 零样本不可行实证） | ①新闻 ②③/W4 ③两路线 ④⬜ ⑤- ⑥⬜ |
| 链↔板块路由件 | ⬜（ig_chain.category→板块码映射，grep 零命中） | ⬜ | ④与①-③环节合流 | 板块域信号（①②③）与链域标的（④）之间无机械路由——ACC-F 的"主题→申万一级→ig_chain.category→环节投影"四跳是唯一先例（ACC-F:22-28） | ①- ②- ③四跳投影 ④⬜ ⑤- ⑥- |

## §2 双真源收敛两方案（挖矿令特别点①：读两边表结构/边类型/规模后给方案）

**事实基座**：PG 大图 11+ 表在产（节点 5,560/环节边 1,726/公司映射 25,559 PIT/公司边 58,207/事实 26.4 万）；SQLite 小图=空库库件（零数据零调用）；W3-W5 生产链路**已全部走 PG**；小图边类型（material/demand/byproduct 细分+权重 (0,1]）是 PG ig_edge（structure/supply 两型+UNIQUE 三元组）没有的语义。

| 维度 | 方案 A：弃 SQLite 壳，语义并入大图 | 方案 B：SQLite API 化只读投影 |
|------|-----------------------------------|------------------------------|
| 做法 | ig_edge 扩 edge_type 词表（material/demand/byproduct）+weight 列（ALTER 幂等，DDL-as-Code 惯例 v10 增量）；IndustryChainGraph 的 BFS 乘积衰减算法改写为 PG 只读查询件（depgraph_schema 同款注入） | 保留 MOD-SIG-125 壳，从 PG 定期投影 ig_node/ig_edge→ic_nodes/ic_edges（加 material/demand/byproduct 映射规则） |
| 利 | 单一真源（RULE-SSOT）；零同步成本；PIT/墓碑/实体主数据全部白得；W3-W5 链路零改动 | 算法件（纯函数+确定性排序）不动；SQLite 零依赖可离线单测 |
| 弊 | MOD-SIG-125 蓝图重写（human_gated 头注——改动过 Owner 门）；BFS 在 PG 侧性能须压测（1,726 边规模无虞） | **投影=第二数据副本=双真源永续化**（违内收判据"同真源可派生→必并"）；投影任务=新增常驻运维面（违终局全貌无人参与方向）；边类型映射规则=新漂移点 |
| 判定 | **推荐 A** | 否 |

**推荐 A 的三条挖矿证据**：①小图零生产实例化（沉没成本≈0，弃壳无痛）；②W3-W5 已在 PG 侧运行（收敛=认既成事实，非迁移）；③终局全貌（全自动化无人运维）对"投影任务"零诉求。前置=过 MOD-SIG-125 human_gated 门（蓝图退役/改写属 Owner 门位范围，呈批件语言已在）。

## §3 施工要点

1. **方向语义两路线的裁定依赖**：路线 A（规则）地基已在（MOD-ALT-005+ACC-F 11 项别名实践）；路线 B（LLM 蒸馏）前置=新闻源面拍板（研究册 §6.5）——建议 A 先行 B 挂起，B 的解锁条件=新闻源面 Owner 裁定+LLM 蒸馏基建（班外）。
2. **resolver 的 known simplification 是显式债务**：头注明写"成本反号传导留事件类型细分后迭代"——方向语义施工时禁原地改 resolver 判定核（SAFETY M），应新建事件类型→符号映射层注入 polarity。
3. **ig_equity_edge 缺表**先查 DDL 版本部署史（apply 脚本分段执行？）再决定补部署或删段——禁留"DDL 有表无"漂移（RULE-SSOT）。
4. **链↔板块路由**建议复用 ACC-F 四跳（主题→申万一级→ig_chain.category→环节）为通用投影件——ACC-F 已实证 24 条事件窗 4 命中（:28-30），投影端点 /api/chainmap-catalyst 在产。
5. **传导排序目标形态**（链上位置×时滞×龙头分档）三乘数分属三件：位置=BFS hop（resolver）、龙头=四档（sector_leader）、时滞=⬜（迁移熵估计，研究册 §3.6-3 排第三优先级，挂起）。
6. **CKG 规模数字出处**=docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md:14038（4,654 上市公司/511 申万/95,559 产品/110,153 边，实查复认）——引用式冻结，禁抄进代码注释。

## §4 自审闸三态裁定

**裁定：施工**（分两期：A 期=方向语义规则层+链↔板块路由件；B 期=SQLite 壳收敛，过 human_gated 门后）——理由：④是"板块确认后买什么"的唯一机械答案源，A 期消灭"事件→标的人工翻链"环节且全部地基在码；B 期是 RULE-SSOT 内收义务（双真源收敛），终局必为单真源。时滞估计（迁移熵）与 GNN 特征=挂起排期（终局有位、数据/方法未到窗口，研究册 §3.6 排序 3、5 位）。
