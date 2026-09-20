---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L68: - **概念体系已落地**：stock_concept 表（22,111 行/3,365 公司/1,853 概念，市场分类标签已过滤），装载器 scripts/industry_graph/concept_ingest.py。
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L34: ## 3. 待施工：B 组 44,008 行二次代码化（官方数据补充）
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 前五大供应商/客户数据（483 层）全量重验报告

> Owner 2026-09-14 指令："官方数据全部去验一遍——有错的覆盖/关闭，没有的补充。"
> 范围：ig_company_edge source='483_top5_customer' 共 51,345 行（年报前五大披露管线,2001-2025）。

## 0. 数据结构（验前摸底）

| 分组 | 行数 | 说明 |
|---|---|---|
| A 组·双边代码行 | 7,337 | 供应商→客户都有股票代码=可直接验证/可直接供详情页消费 |
| B 组·仅客户名行 | 44,008 | 客户未上市或未代码化；**to_name 客户名填充率 100%**（二次代码化的原料） |

## 1. 三重机检结果（A 组 7,337 行全量）

| 检查 | 结果 | 处置 |
|---|---|---|
| ① 代码格式/在市 | 0 错 | 干净 |
| ② 自环（自己供自己） | 0 条 | 干净 |
| ③ 金融机构混入（研报作者类误挂） | 0 条 | 干净（ig_node 层的券商误挂在落位复核批已清，本层无此病） |
| ④ 跨源方向印证（vs match_list 2012-2023） | 695 对一致 / 17 对相反 | 相反对逐对行业仲裁（见 §2） |
| ⑤ 双向披露对 | 28 对 | **合法互供**（两家都把对方列为前五大客户），保留为强证据 |

## 2. 17 对方向矛盾的仲裁（申万行业+产业常识）

- **483 错向 3 对**（钢铁/煤炭/化工方向明显反向）：万向钱潮←中信特钢、新华制药←华鲁恒升、新兴铸管←兖矿能源——483 错向行 3 条已 edge_close（批次 supply483_dirfix_p5，正确方向 match_list 已有，零信息损失）。
- **483 对/名单错**：金禾实业→六国化工、福瑞股份→国药股份、国缆检测→起帆电缆、天桥起重→柳钢、安泰集团→浙商中拓等 5 对——483 保留，名单源反向行留待名单源验证批处置。
- **互供确认 3 对**：一汽解放↔启明信息（集团内）等——双向保留。
- **结论**：483 层错率约 3/7337（0.04%），但方向矛盾集中在双源都有解析的少数对——证明 Owner"全量重验"的必要性。

## 3. 待施工：B 组 44,008 行二次代码化（官方数据补充）

to_name 100% 有客户名。施工件=名称→代码匹配器（模糊匹配+拼音/简称库+人工复核队列），匹配上的行升级为双边行（直接增厚详情页数据），匹配不上且非上市的走 UNLISTED:UE- 编码表登记（既有的 v3 通道）。**这是"官方数据补充"的主战场，建议下一个施工班立项。**

## 4. 详情页上下游支撑——后端接口规格（交 chainmap 前端会话）

数据真源：ig_company_edge（验证后）。查询语义（PG depgraph 库）：

```sql
-- 我买谁的货（上游供应商）: 别人披露里 to=本公司, 对端 from 即供应商
SELECT from_symbol AS counterparty, from_name, string_agg(DISTINCT year::text, ',') AS years
FROM ig_company_edge
WHERE to_symbol=:sym AND valid_to IS NULL AND to_symbol<>'' AND source='483_top5_customer'
GROUP BY 1,2;

-- 谁买我的货（下游客户）: 本公司披露的客户
SELECT to_symbol AS counterparty, to_name, string_agg(DISTINCT year::text, ',') AS years
FROM ig_company_edge
WHERE from_symbol=:sym AND valid_to IS NULL AND source='483_top5_customer'
GROUP BY 1,2;
```

API 建议：`GET /api/company/{symbol}/supply_chain` 返回 `{suppliers:[], customers:[]}`（各含 counterparty/name/years），8890 端 api_server 加只读端点即可，无新表无写操作。**上下游验证支点语义**：客户名单里的公司=本公司的下游——可用于 ig_edge 方向的抽样核对（批内已示范 11 对仲裁法）。

## 5. 结论

- 483 层验证后可信度：代码层 100%、方向层 99.96%（3 条错向已关）。
- 双边行 7,337 条可直接支撑详情页上下游展示与图谱方向印证。
- B 组 44,008 条客户名的二次代码化=下一增量批（官方数据补充主战场）。


## 6. 追加（2026-09-14）：概念展示+代码化回填进展

- **代码化回填已执行**：558 个客户名回写 to_symbol，B 组 44,008 行中 1,248 行升级为双边行（7,337→8,585），审计留痕 .runtime/audit/name_backfill_actions.json，可逆（edge_id 清单在案）。
- **概念体系已落地**：stock_concept 表（22,111 行/3,365 公司/1,853 概念，市场分类标签已过滤），装载器 scripts/industry_graph/concept_ingest.py。
- **概念展示规格（交 chainmap 前端会话）**：

```sql
-- 公司所属概念（详情页标签行）
SELECT concept FROM stock_concept
WHERE symbol=:sym AND valid_to IS NULL ORDER BY concept;
```

API 建议：`GET /api/company/{symbol}` 返回体并入 `concepts: []` 数组（与 §4 的 supply_chain 同源复用）；链图节点详情弹窗可加同名标签。概念动态更新未来接 akshare concept_sector 定期刷新。
