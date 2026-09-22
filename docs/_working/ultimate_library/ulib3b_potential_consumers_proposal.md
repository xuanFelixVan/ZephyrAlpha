---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_potential_consumers_proposal.md"
ttl: "task_bound"
---

# potential_consumers 增枝申请（呈 Owner 批·增补令 #11）

- 申请人：st-ulib3b-20260922（G15-② 承接班）
- 依据：08 字段词典 v1.0 §6 增枝制（schema 只增不改语义；停止判据三问+Owner 批）
- 证据库：ulib3b_supply_relationship_ledger.md（供给 40 条）/ ulib3b_demand_gap_ledger.md（需求 36 项）/ ulib3b_to_derive_candidates.md（待推导 12 条）
- 缺口立案原文：docs/_working/sector_line/sector_gap_list_and_construction_proposal.md G15 行（R7 轮 Owner"有图书馆为何还漏"实证）

## 一、提案内容

lib_assets 增一列 **`potential_consumers text[] DEFAULT '{}'`**（供数用途维度）：登记该资产**能喂什么**——标尺/节点/消费方清单，粒度对标 TDM 节点名与骨架成分名（如 `dragon_tiger → [板块hot_money维, 游资温度成分, BM-SEL-05]`）。

## 二、停止判据三问（增枝制门槛）

1. **现有字段能否表达？** 不能。tags 是主题词（行情/资金面），不是"供数关系"；title/notes 记"是什么"。供给→用途是结构化关系，63 号审计与 R7 轮均证明按名索引结构性盲（跨域推导无人能扫）。
2. **是否零触发零消费（内收判据 w5_1）？** 非零：①G15-① 别名轴解决"知道词查不到"，本维度解决"不知道有这东西"——需求侧反查（用途→表）是 lookuo 反查面的直接消费方；②需求侧缺口册 36 项中"已供给"部分可零推导机械回填首批数据，上架即有存量；③数据面班流程配方（盘数据面第一步=图书馆双语概念词查询）写入藏书规程页后，potential_consumers 是该流程的第二查询轴。
3. **是否与既有字段同真源可派生？** 不可。供数关系散落在 battle_map（抽象类级）、各线台账（明文级）、63 号 CSV（计数级），无任何单一真源可派生——恰需本列做汇聚点。

## 三、设计要点

| 项 | 提案 |
|---|---|
| 类型 | `text[] DEFAULT '{}'`（NULL=未评估，空数组=已评估无供数关系——两态分开） |
| 内容词表 | 首批=TDM 节点名+骨架成分标尺名+自由文本后缀；不建强制枚举（跨域语义开放），TAG-VOCAB 观察期同款 warn 闸观察后视情收词 |
| 写入方 | 首批=本班三册产出机械回填（已供给 36 项）；增量=采集器不碰（人工/施工批按 merge_evaluation 同款留痕），death 证明时随户籍注销 |
| 反查面 | lookup 增 `--feeds <关键词>` 过滤（potential_consumers 数组包含匹配），中文概念词经增补令 #12 别名轴归一 |
| 不做 | 不做外键约束（消费方可能是文档概念非资产）；不做自动推荐推导（待推导清单 T1-T12 实探前不填） |

## 四、落地步骤（Owner 批后）

1. DDL 迁移：`ALTER TABLE lib_assets ADD COLUMN potential_consumers text[] NOT NULL DEFAULT '{}';`（PG depgraph 库；先备份，RULE-DATA-OPS 三步验证）
2. 08 字段词典升 v1.1：§1 核心户籍字段表增一行（只增不改语义）
3. 登记闸同步：librarian upsert 路径带新列；fs/pg/ch 采集器默认空数组不填（供数关系=人工判定资产）
4. 首批回填：三册产出已供给项 → 单独施工批（每条带出处路径，merge_evaluation 留痕）
5. lookup --feeds 反查面 + tests/library 回归

## 五、呈请

- [ ] Owner 批准增枝（本件四节全量）
- [ ] Owner 指定回填班次（建议：增补令 #12 别名展开同批或紧随，共用 lookup 面）

**呈批不施工**：DDL 迁移待 Owner 批文后另批执行（机械判定门铁律：schema 变更不可自裁）。
