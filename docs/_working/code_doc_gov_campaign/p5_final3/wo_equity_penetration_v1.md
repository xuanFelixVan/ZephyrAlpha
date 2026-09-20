---
ttl: task_bound
session: st-code-doc-20260921
---

# WO：股权穿透底座施工 v1（只待 Owner 点火）

> 出单：st-code-doc-20260921（代码文档治理线 分包5/WO-16 R11，2026-09-21）。本单**零施工**，供 Owner 点火后**新会话整贴开工**。
> 设计真源：[altdata_line/02_entity_graph_equity_person.md](../../../altdata_line/02_entity_graph_equity_person.md)（已定调，设计 100/施工 0/原料 60——A 层 akshare 零爬虫就绪、B 层 PDF 管道既有、C 层 gsxt 地狱反爬不碰、D 层商业 API 不买）。
> 排期挂点：altdata_line/08_full_chain_roadmap.md **P7**（人物线）前置 = P1①消歧桥（entity_code_map uscc 主键接入）；纪律承 09_data_subpackage_worklist.md §3。

## 一、目标（一句话+边界）

自建**带时间版本的多边图底座**（股权边 edge_holding + 任职边 edge_role 为骨干）+ **股权穿透查询视图**（A 股 5000+ 上市公司 N 度邻域子图，M1 期=3 跳内），数据走 A 层（akshare 免费源）首批灌库。**不做**：gsxt 爬虫、商业 API 采购、亲属/专利边（第二批）、全市场 1.8 亿主体。

## 二、处方（按序分步，每步有产物有验收）

- **S0 冷启动**（30min）：AGENTS.md §0 四步（RULE-ENV 3.12 PATH → reaper 存活 → worktree/claim → capability_lookup 留审计）；领 sid，建本单执行台账。
- **S1 DDL 五件套**（60min）：`node_entity` / `node_person` / `node_company` / `edge_holding` / `edge_role` 五表，按 02 文档 §2 字段定调。DDL 真源=`schemas/categories/` 下新建 Python schema 模块；**DateTime64(3)+显式时区**；`valid_from/valid_to` 版本区间（变更追加不覆盖）；禁 `datetime.now()`/`time.time()` 生成器。
- **S2 A 层 provider+首批灌库**（90min）：akshare 十大股东/十大流通/股东户数/实控人变动 → 清洗映射进 `edge_holding`（role=股东）；uscc 缺失时以股票代码+股东名称暂驻 `node_company` 待补列。走 DatabaseService，禁裸 duckdb。
- **S3 穿透查询视图**（60min）：N 度邻域子图查询函数（M1=3 跳）+ `as_of` 时间版本查询（PIT 双轴：事实时间≠采集时间）；冒烟=任一上市公司 3 跳内股东链可回溯。
- **S4 任务+哨兵**（30min）：`tasks.yaml` 登记增量任务+当日校验哨兵；新源进 data_sources_registry；上架检查单走 data_source_onboarding_sop.md §13。
- **S5 收口**（30min）：执行台账（发现/证据[亲验]/停手项）→ `git add` → git_commit.py 正门提交（**拆批提交**，见 §五坑册）→ 向 Owner 汇报。

## 三、文件白名单（仅限 additive，禁区见 §六）

| 动作 | 路径 |
|---|---|
| 新建 | `schemas/categories/equity_graph.py`（DDL 真源） |
| 新建 | `src/zephyr/data/implementations/equity_graph_provider.py`（A 层接入） |
| 修改 | `tasks.yaml`（仅追加本单任务块+哨兵） |
| 修改 | `src/zephyr/data/config/known_data_gaps.yaml`（如需登记缺口，仅追加） |
| 新建 | `docs/_working/altdata_line/wo_equity_penetration_execution_ledger.md`（执行台账） |
| 新建 | `data/capability_cards/`（如需补能力卡，仅新文件） |

白名单外一切改动=越权。新建 .py/.yaml/.md 必办 CREATE-GUARD token（`batch_creation_tokens.py --prefix <目录> --capability altdata_line`，或随主会话统一办）。

## 四、红证双向（红线↔证据逐条对照，交台账时双向可查）

| # | 红线/验收项 | 正向证据（做→留什么） | 反向复核（证→怎么验） |
|---|---|---|---|
| R1 | 五表 DDL 落地且 schema 真源唯一 | schema 模块路径+建表日志 | `DatabaseService` SHOW CREATE TABLE 对字段表 |
| R2 | PIT 双轴：valid_from/valid_to+ingested_at+source 齐全 | 抽 1 条边全字段截图/SQL | `SELECT` 单边四字段非空核验 |
| R3 | 版本追加不覆盖 | 同一股东比例变更产生 2 行 | 按 entity 对 valid 区间不重叠断言 |
| R4 | A 层灌库真数据 | 抽 20 条边与 akshare 原值对照表 | 反向任抽 5 条回源页核对 |
| R5 | 穿透 3 跳可达 | 任一公司 3 跳链路输出 | 换第二家公司复跑同函数 |
| R6 | 任务+哨兵在册 | tasks.yaml 块 hash+哨兵配置名 | commit 后 `git log -1 --name-only` 核归属 |
| R7 | 提交全走正门 | [GW:] 标记+queue 状态 done | commit_queue.py status 查本 sid 无死信 |

## 五、时间盒与已知坑（前人配方，勿再踩）

- 总时间盒 **5 小时**；单步超 40min→该步记"存疑+线索"转下一步，禁死磕。
- **提交连环死信坑**（tilib 班 q-0001..0005 + GATE-21 mutation 盲区在案）：新文件多时**拆批**（DDL 批/provider 批/台账批），CREATE-GUARD token 先办后提交，新 .md frontmatter 禁 doc_type、带 ttl。
- R7 若遇 queue 死信：读 dead json 全文再判，勿盲 requeue（q-0040 先例：payload 已落地=留档作废）。

## 六、避让（禁区，违反即停手上报）

1. `ig_*` 表与产业链资产（05/07 文档域）——产业链分包领地，本单只读。
2. gsxt 层 C、商业 API 层 D——设计钉死不碰不买。
3. `ruling_registry.yaml`、`docs/02_enterprise_architecture/**`、`data/strategy_intake/**`、`tests/**`（新测试走 tests/ 豁免通道新建除外，禁改既有）。
4. 他人 claim 文件与活跃会话在途产物——LOCK 忙即改道入队。
5. 破坏性 DB 操作走三步验证（RULE-DATA-OPS）；判重用 check_tick_duplication.py。

## 七、验收六要素（Owner 收单口径）

①五表可查且字段合 02 文档 §2；②抽 20 条边对源通过（R4 双向）；③3 跳穿透冒烟双公司可复现；④增量任务+哨兵在册（R6）；⑤台账完整含停手项与[亲验]标记；⑥全部改动正门落地、无死信新增。

> 点火方式：Owner 在任意新会话整贴本单即可开工；开工前先 `capability_lookup.find("股权穿透")` 留审计。
