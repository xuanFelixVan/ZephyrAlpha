---
module_id: MOD-LIB-001
asset_id: "DOC:docs/03_modules/_domain_library/blueprint.md"
ttl: permanent
doc_type: blueprint
status: Active
version: "1.0.0"
title: "终极图书馆总账域蓝图 — 资产户籍+馆员+采集器+总口"
responsibility_domain: 
---

# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md

> **一句话**：全项目资产户籍（lib_assets/lib_events）+ 馆员唯一写路径 + 五采集器 + 总口查询。
> 真源：docs/_working/ultimate_library/08_field_dictionary_v0_1.md（schema 冻结 v1.0）；04 总攻派工单 B1/B2/C1/C2。

## 模块清单

| module_id | 模块 | 职责 |
|---|---|---|
| MOD-LIB-001 | zephyr.library.schema | DDL 常量+身份派生纯函数（零 IO） |
| MOD-LIB-002 | zephyr.library.registry | 馆员 Librarian：act/lookup/ensure_schema（唯一写路径） |
| MOD-LIB-003 | zephyr.library.lookup | 总口查询 API+CLI |
| MOD-LIB-004 | zephyr.library.collectors | 五采集器（fs/pg/ch/schtasks/mcp，全只读）+ingest |
| MOD-LIB-005 | zephyr.library.relations | 关系树一键查询：关键词→depgraph 有界 BFS→四馆归类树（W+1 Owner 点名） |
| MOD-GATE_ENGINE 派生 | commit_gates/library_coverage_gate | LIBRARY-COVERAGE 观察闸（warn-only，W+1 硬闸） |

## 依赖

- PG 资产总线（depgraph 库，get_depgraph_pg_connection）
- ch_writer.get_client_strict（CH 统一入口）
- run_subprocess_hidden（BARE-SUBPROCESS 正门）

## 场外区条款（梵蒂冈条款，Owner 2026-09-21 令）

docs/_working/ 与一切临时区（.runtime/tmp、根 tmp）= **场外区**：免索书号、免 token、免 per-file 门禁；不逐件入总账，只以堆积量指标与盲册候选呈现。场外区工作流零登记负担；晋升（转正）时才过门禁办 fully 身份。

## 不变量

1. 不登记不变更（event+state 同事务）。
2. delete 必须携带处置预授权（死亡证明，08 §3.1）。
3. 全部 SQL 模块级常量（NO-BARE-SQL）。
4. 采集器全只读、fail-soft。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-LIB-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-LIB-001` 的 4 个 file 节点 | design | `extract_depgraph.py --modules MOD-LIB-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-LIB-001 | MOD-LIB-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
