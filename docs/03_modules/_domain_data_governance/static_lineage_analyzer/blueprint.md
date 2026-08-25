---
blueprint_id: MOD-DATA_GOV-005
module_name: static_lineage_analyzer
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
path: src/zephyr/data_governance/core/static_lineage_analyzer.py
granularity: file
---

# MOD-DATA_GOV-005 static_lineage_analyzer 蓝图（M8-S02 静态分析器）

> **module_id**: MOD-DATA_GOV-005 | **域**: D_DATA_GOV | **优先级**: P1
> **来源**: B10-02314（AUD-DRAFT-001-DIGEST P1 波 W-P1-18，CAND-DATGOV-002，A1 交易决策架构 §30.4.3）
> 代码：`src/zephyr/data_governance/core/static_lineage_analyzer.py`

## 0. 定位

M8-S02 静态分析器——基于 ast 解析 Python 读写调用 + sqlglot 解析 SQL 表级血缘，
输出统一边格式入 lineage_tracker；离线批跑不占盘中资源。TSV 现状注记：代码/SQL
静态分析提取血缘为零起步。

查重分工（W-P1-18 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| lineage_tracker | MOD-DATA_GOV-002 | 血缘边注册/上下游查询/环检测/幂等 | 本模块只做**静态抽取**，幂等与环检测复用其实现不重造 |
| lineage_parser | MOD-DATA_GOV-004 | CTR 契约/模块头注解解析（M8-S01） | S01 解析**契约定义**，S02 解析**代码/SQL 文本**；入图语义（批内去重/幂等 updated/环 rejected）复用 S01 `ingest_into_tracker` 不重造 |
| column_lineage_analyzer | MOD-DATA_GOV-007 | sqlglot 列级血缘（M8-NEW-02） | 粒度分工：S02=**表级**边，列级=table.column 节点归 007 |

不做什么：不重造图算法与入图幂等语义（复用 002/004）、不解析列级转换（007 职责）、
不做运行时采集（M8-S03 职责）、不内置 SQL 解析器（sqlglot 懒加载，依赖登记前
SQL 面降级留痕不崩溃）。

## 1. 解析规则（确定性，纯函数）

- **Python AST 面** `extract_python_io_edges(source, *, module)`：stdlib ast 遍历，
  读词表（read_parquet/read_csv/read_sql/read_table/read_json/read_feather/read_orc）
  首位置字符串字面量路径 → 边 path --reads--> module；写词表（to_parquet/to_csv/
  to_json/to_feather/to_orc/write_parquet）→ 边 module --writes--> path。
  非字面量路径（变量/拼接）跳过不成边；语法错误 Fail-Closed（StaticLineageError）。
- **SQL 面** `extract_sql_table_edges(sql, *, dialect=None)`：sqlglot 懒加载解析
  单条语句——INSERT INTO/CREATE TABLE AS 目标表 ← FROM/JOIN 源表，
  边 source_table --sql--> target_table；无目标表的纯查询不出边。
  sqlglot 未安装 → SqlglotUnavailableError（批跑面捕获记 degraded，fail-open 不中断批）。
- **批跑面** `analyze_sources(*, python_sources, sql_sources, tracker)`：逐来源抽取
  → 汇总 → 复用 S01 `ingest_into_tracker` 入图（批内 (source,target) 去重首条胜出、
  幂等 updated、环 rejected 不中断）；产出 StaticLineageReport
  （files/edges/added/updated/rejected/skipped/degraded/sources）。

## 2. 接口

```python
class StaticLineageError(ValueError)
class SqlglotUnavailableError(StaticLineageError)
@dataclass(frozen=True)
class StaticLineageReport: files / edges / added / updated / rejected / skipped / degraded / sources
extract_python_io_edges(source: str, *, module: str) -> list[LineageEdge]
extract_sql_table_edges(sql: str, *, dialect: str | None = None) -> list[LineageEdge]
analyze_sources(*, python_sources, sql_sources, tracker, sources) -> StaticLineageReport
```

## 3. 依赖前置

- MOD-DATA_GOV-002 lineage_tracker（LineageEdge/add_edge/环检测/幂等唯一真源）。
- MOD-DATA_GOV-004 lineage_parser（ingest_into_tracker 入图语义复用）。
- sqlglot（未登记三方依赖，懒加载；登记后补 SQL 面 happy-path 集成测试）。

## 4. 验收标准

- 单测全绿（AST 读/写边抽取、非字面量跳过、语法错误 Fail-Closed、sqlglot 缺失降级
  fail-open、批内去重/幂等/环拒记复用语义、端到端 抽取→入图→上下游查询）；
  相关域集成零回归。
