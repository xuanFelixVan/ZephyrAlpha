---
ttl: task_bound
completes_when: 缺失清单并入转正批收尾报告后归档
title: 九张在册图 frontmatter L0 字段缺口清单（任务5，只登记不改 YAML）
owner: st-mapreg-20261003
---

# 九图 frontmatter L0 缺口清单（只读普查，零 YAML 改动）

> 判据真源：`docs/_working/map_build/03_final_blueprint_and_schema.md` §1 裁定一「L0 通用层」（六图终局卷，原生于图11-16 家族；本普查将其作为存量九图的对照基线，登记缺口供转正批/后续对齐排程引用，**不构成 retrofit 义务**）。
> 方法：逐张定位载体 → 解析 frontmatter（顶层键）+ 节点级字段逐格扫描（yaml.safe_load 全量）。
> 普查时点：2026-10-03 深夜（HEAD=62b59093d0 盘面）。

## 九图缺口总表

| # | 图 | 载体（实测） | L0 顶层缺 | L0 节点级缺（缺失节点数/总数） | 别名违规（裁定「同语义必同名」收敛对象） |
|---|---|---|---|---|---|
| 1 | depgraph | PostgreSQL `dep_` 表组（无 YAML 载体） | 不适用 | 不适用（L0 针对 YAML 图头/节点；PG 侧对齐走表 schema 层） | — |
| 2 | dataflowgraph | PostgreSQL 3 表（无 YAML 载体） | 不适用 | 不适用 | — |
| 3 | blueprint | MD frontmatter ×548 件（`find docs/03_modules -name blueprint.md` 实测；四字段制 module_id/responsibility_domain/design_maturity/build_status） | 不适用 | 不适用（MD 四字段制非 YAML 图） | — |
| 4 | frontend_map | `src/zephyr/frontend/dashboard/web/frontend_map.yaml`（364 features） | **全 7 缺**：map_id/schema_version/name_zh/effective_from/markets/laws/boundary 均无（仅有 version/updated/features） | **全缺 ×364**：node_id/name_zh/node_type/decision_question/note_zh/source_anchors/confidence/verified_scope/build_status 九项全无；分组轴四选一无 | `id`≠node_id、`name`≠name_zh（旧名制）；module_id ✓ 满挂（0 缺） |
| 5 | industry_chain_map | PG industry_chain 表组 + `config/chainmap_cluster_names.yaml`（簇名词表，非图体） | 不适用 | 不适用 | — |
| 6 | trading_decision_map | `config/trading_decision_map.yaml`（182 nodes） | laws、boundary（缺 2） | note_zh/source_anchors/confidence/verified_scope/build_status **全缺 ×182**；module_id 缺 60/182（122 在挂）；分组轴用 layer/point/market 非四选一名 | `algo_note_zh`→应 `note_zh`（裁定废止别名语族）；has factor_refs/strategy_mounts（TDM 自有语义，非越域） |
| 7 | strategy_production_map | `config/strategy_production_map.yaml`（16 nodes） | **无缺（七项全在）**，另带 nickname/purpose_legend 增益 | note_zh/source_anchors/confidence/verified_scope 缺 ×16；module_id 缺 16/16（但 module_ref 16/16 在场，§2 代码锚腿满足）；build_status ✓ 0 缺；分组轴=stage ✓ | `algo_note_zh`→应 `note_zh`；`design_refs`（裁定明文废止名，应归 doc_refs） |
| 8 | governance_operations_map | `config/governance_operations_map.yaml`（机生：families dict×7 + 人工 pipeline dict×1，schema_version 0.1，map_id GOMAP-001） | markets、laws、boundary（缺 3；map_id/schema_version/name_zh/effective_from/ssot_note_zh ✓） | 不直接适用（无 nodes 数组，机生层字段由生成器 schema 管） | — |
| 9 | battle_map | PostgreSQL 3 表 battle_map_steps/anchors/edges（无 YAML 载体） | 不适用 | 不适用 | — |

## 缺口分层结论（供转正批排程参考）

1. **顶层 L0**：strategy_production_map 满贯 > trading_decision_map 缺 2（laws/boundary）> governance_operations_map 缺 3（markets/laws/boundary）> frontend_map 全缺 7。
2. **节点级血肉（note_zh/source_anchors/confidence/verified_scope）**：TDM 182 台、图9 16 台、frontend_map 364 台全缺——与挂图 SOP（vertical_map_mounting_policy）四字段血肉批属同一工程面，宜随各图血肉 F 批统一补齐，不单独立项。
3. **别名收敛**（裁定一「同语义必同名」）：`algo_note_zh`（TDM+图9）→`note_zh`、`design_refs`（图9）→doc_refs、frontend_map `id`/`name`→`node_id`/`name_zh`——机械改名面，随各图下一次 schema 升版顺带（改 YAML 须过各自校验器，本批零改动）。
4. **schema_version 现状**：TDM/图9/GOMAP 在册有版本号（TDM 与图9 已随今夜批次升至 0.3，GOMAP 0.1）；frontend_map 用 `version`（v2.0.0）非 `schema_version` 键名。
5. **五张 PG/MD 载体图**（depgraph/dataflowgraph/blueprint/industry_chain_map/battle_map）：无 YAML 图体，L0 frontmatter 语义不适用；其「对齐清单 §3 真源」列即载体真源，若未来立 YAML 图体再入 L0 管辖。
