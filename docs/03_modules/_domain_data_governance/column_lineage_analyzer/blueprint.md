---
blueprint_id: MOD-DATA_GOV-007
module_name: column_lineage_analyzer
domain: D_DATA_GOV
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/core/column_lineage_analyzer.py
granularity: file
---

# MOD-DATA_GOV-007 column_lineage_analyzer 蓝图（M8-NEW-02 Column-Level Lineage Analyzer）

> **module_id**: MOD-DATA_GOV-007 | **域**: D_DATA_GOV | **优先级**: P1
> **来源**: B13-04276（AUD-DRAFT-001-DIGEST P1 波 W-P1-18，CAND-DATGOV-004，A3 数据架构 §17.2）
> 代码：`src/zephyr/data_governance/core/column_lineage_analyzer.py`

## 0. 定位

M8-NEW-02 列级血缘分析器——sqlglot AST 解析 SQL/视图抽取**列级**血缘
（源列→转换表达式→目标列），DAG 入 lineage_tracker，提供字段级影响面查询 API
供变更评审。TSV 现状：已有 lineage_tracker（表/文件级），缺字段级转换逻辑追踪。

查重分工（W-P1-18 探查结论，**粒度分工**不复制）：

| 既有件 | module_id | 粒度 | 与本模块边界 |
|---|---|---|---|
| lineage_tracker | MOD-DATA_GOV-002 | 节点字符串无关粒度 | 列级节点命名 `table.column` 入同一 DAG，幂等/环检测复用不重造 |
| lineage_parser | MOD-DATA_GOV-004 | 契约/模块头（域/模块级） | 入图语义复用 S01 `ingest_into_tracker` 不重造 |
| static_lineage_analyzer | MOD-DATA_GOV-005 | **表级**（M8-S02） | S02 出表级边；本模块出**列级**边（源列→表达式→目标列），粒度互补 |
| record_lineage_tracker | MOD-DATA_GOV-008 | **记录级**（特征批次溯源） | 列级=SQL 变换列依赖；记录级=批次 provenance，不重叠 |

不做什么：不重造图算法与入图幂等语义（复用 002/004）、不追踪记录级批次溯源
（008 职责）、不内置 SQL 解析器（sqlglot 懒加载，未登记前解析面 Fail-Closed
显式不可用错误，不做 regex 兜底）。

## 1. 解析与查询规则

- **列节点命名** `column_node(table, column)` → `"table.column"`（空表名/列名
  Fail-Closed）。
- **列级抽取** `extract_column_lineage(sql, *, target_table, dialect=None)`：
  sqlglot 懒加载解析 SELECT/视图——SELECT 列表每个输出列（含别名）→ 其表达式
  引用的全部源列（`table.column`，无表前缀继承 target 语境拒绝歧义列）；
  产出 ColumnLineageEdge（source_table/source_column/target_table/target_column/
  expression）。sqlglot 未安装 → ColumnLineageError（Fail-Closed 显式不可用，
  不降级错抽）。
- **入图** `ingest_columns_into_tracker(edges, tracker)`：列边 → `table.column`
  节点 LineageEdge（transformation=表达式文本截断）→ 复用 S01 ingest 语义。
- **影响面查询** `column_impact(tracker, table, column)`：字段级上游/下游
  （变更评审用：改某列前查其下游影响面）。

## 2. 接口

```python
class ColumnLineageError(ValueError)
@dataclass(frozen=True)
class ColumnLineageEdge: source_table / source_column / target_table / target_column / expression
@dataclass(frozen=True)
class ColumnImpact: node / upstream / downstream
column_node(table, column) -> str
extract_column_lineage(sql, *, target_table, dialect=None) -> list[ColumnLineageEdge]
ingest_columns_into_tracker(edges, tracker) -> LineageParseReport
column_impact(tracker, table, column) -> ColumnImpact
```

## 3. 依赖前置

- MOD-DATA_GOV-002 lineage_tracker（DAG/环检测/幂等唯一真源）。
- MOD-DATA_GOV-004 lineage_parser（ingest_into_tracker 入图语义复用）。
- sqlglot（未登记三方依赖，懒加载；登记后补抽取 happy-path 集成测试）。

## 4. 验收标准

- 单测全绿（列节点命名校验、sqlglot 缺失 Fail-Closed、列边→DAG 入图复用语义、
  影响面查询上游/下游、端到端 建边→影响面）；相关域集成零回归。
