# [BLUEPRINT] MOD-DATA_GOV-007 | docs/03_modules/_domain_data_governance/column_lineage_analyzer/blueprint.md
# [MODULE] zephyr.data_governance.core.column_lineage_analyzer
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.lineage_tracker; zephyr.data_governance.core.lineage_parser
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 列节点命名 table.column; 幂等与环检测复用 MOD-DATA_GOV-002 不重造; 入图语义复用 MOD-DATA_GOV-004 不重造; 空标识 Fail-Closed; sqlglot 缺失显式不可用不降级错抽
# [MODIFY-GUARD] tests/data_governance/test_column_lineage_analyzer.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ColumnLineageError(未登记错误码-申请中)
# [TESTS] tests/data_governance/test_column_lineage_analyzer.py
# [A_module] module_id=MOD-DATA_GOV-007 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
M8-NEW-02 Column-Level Lineage Analyzer（MOD-DATA_GOV-007）。

真源：construction_backlog_dig.tsv B13-04276（A3 数据架构 §17.2，裁定=做 P1）
+ CAND-DATGOV-004。

定位：已有 lineage_tracker（表/文件级），缺**字段级**转换逻辑追踪（TSV 现状）。
本模块以 sqlglot AST 解析 SQL/视图抽取**列级**血缘（源列→转换表达式→目标列），
列节点命名 `table.column` 入同一 DAG（粒度分工：表级归 M8-S02，列级归本模块，
记录级批次溯源归 MOD-DATA_GOV-008），并提供字段级影响面查询 API 供变更评审
（改某列前查其下游影响面）。

sqlglot 依赖裁定：未登记三方依赖（同 M8-S02）——懒加载，未安装时解析面
Fail-Closed 显式不可用（ColumnLineageError），不做 regex 兜底错抽；登记后补
抽取 happy-path 集成测试。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: table 参数
#   fields: 参数 table，类型注解 str
#   code: column_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: column 参数
#   fields: 参数 column，类型注解 str
#   code: column_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sql 参数
#   fields: 参数 sql，类型注解 str
#   code: column_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: target_table 参数
#   fields: 参数 target_table（无注解）
#   code: column_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① column_node
#   name_en: column_node
#   intro: 列节点命名 `table.column`（空表名/列名 Fail-Closed）。
#   desc: 列节点命名 `table.column`（空表名/列名 Fail-Closed）。；源码 L176-L178
#   inputs: table column
#   outputs: str
# - id: A2
#   name_zh: ② extract_column_lineage
#   name_en: extract_column_lineage
#   intro: sqlglot AST 解析 SELECT/视图 → 列级血缘边（薄胶水，依赖登记后补 happy-path 测）。
#   desc: sqlglot AST 解析 SELECT/视图 → 列级血缘边（薄胶水，依赖登记后补 happy-path 测）。 每个输出列（含别名）→ 其表达式引用的全部源列；无表前缀列在…；源码 L191-L237
#   inputs: sql target_table dialect
#   outputs: list[ColumnLineageEdge]
# - id: A3
#   name_zh: ③ ingest_columns_into_tracker
#   name_en: ingest_columns_into_tracker
#   intro: 列边 → `table.column` 节点入 DAG（幂等/环/去重复用 MOD-DATA_GOV-004 语义）。
#   desc: 列边 → `table.column` 节点入 DAG（幂等/环/去重复用 MOD-DATA_GOV-004 语义）。 transformation 记转换表达式（截断 80 字…；源码 L240-L258
#   inputs: edges tracker
#   outputs: LineageParseReport
# - id: A4
#   name_zh: ④ column_impact
#   name_en: column_impact
#   intro: 字段级影响面查询：列节点的全部上游/下游（变更评审用；未知节点空结果）。
#   desc: 字段级影响面查询：列节点的全部上游/下游（变更评审用；未知节点空结果）。；源码 L261-L270
#   inputs: tracker table column
#   outputs: ColumnImpact
#   （注：A4 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: list[ColumnLineageEdge]
#   name_en: list[ColumnLineageEdge]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from zephyr.data_governance.core.lineage_parser import LineageParseReport, ingest_into_tracker
from zephyr.data_governance.core.lineage_tracker import LineageEdge, LineageTracker

__all__: Final = [
    "ColumnImpact",
    "ColumnLineageEdge",
    "ColumnLineageError",
    "column_impact",
    "column_node",
    "extract_column_lineage",
    "ingest_columns_into_tracker",
]

_log = logging.getLogger(__name__)

#: 表达式文本入 transformation 的截断长度（边描述可读性）
_EXPR_MAX_LEN: Final[int] = 80


class ColumnLineageError(ValueError):
    """列级血缘解析/查询输入非法（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class ColumnLineageEdge:
    """列级血缘边（源列→转换表达式→目标列）。

    Attributes:
        source_table: 源表名
        source_column: 源列名
        target_table: 目标表名（视图/落表）
        target_column: 目标列名（输出列/别名）
        expression: 转换表达式文本（如 `close / prev_close - 1`）
    """

    source_table: str
    source_column: str
    target_table: str
    target_column: str
    expression: str = ""


@dataclass(frozen=True)
class ColumnImpact:
    """字段级影响面（变更评审用）。

    Attributes:
        node: 查询列节点（table.column）
        upstream: 全部上游列节点（拓扑序）
        downstream: 全部下游列节点（拓扑序）
    """

    node: str
    upstream: tuple[str, ...] = ()
    downstream: tuple[str, ...] = ()


def _validate_ident(value: str, *, field_name: str) -> str:
    """标识符校验：非空非空白（Fail-Closed）。"""
    if not isinstance(value, str) or not value.strip():
        raise ColumnLineageError(f"标识为空: {field_name}={value!r}")
    return value.strip()


def column_node(table: str, column: str) -> str:
    """列节点命名 `table.column`（空表名/列名 Fail-Closed）。"""
    return f"{_validate_ident(table, field_name='table')}.{_validate_ident(column, field_name='column')}"


def _import_sqlglot():
    """sqlglot 懒加载（未登记依赖，未安装 → Fail-Closed 显式不可用）。"""
    try:
        import sqlglot
        from sqlglot import exp
    except ImportError as exc:
        raise ColumnLineageError("sqlglot 未安装（三方依赖登记申请中），列级血缘解析不可用") from exc
    return sqlglot, exp


def extract_column_lineage(
    sql: str,
    *,
    target_table: str,
    dialect: str | None = None,
) -> list[ColumnLineageEdge]:
    """sqlglot AST 解析 SELECT/视图 → 列级血缘边（薄胶水，依赖登记后补 happy-path 测）。

    每个输出列（含别名）→ 其表达式引用的全部源列；无表前缀列在 FROM 单表时
    继承该表，多表歧义 Fail-Closed。空 SQL/空目标表 Fail-Closed；sqlglot 未安装
    → ColumnLineageError（不降级错抽）。
    """
    if not isinstance(sql, str) or not sql.strip():
        raise ColumnLineageError(f"SQL 文本为空: {sql!r}")
    target_table = _validate_ident(target_table, field_name="target_table")
    sqlglot, exp = _import_sqlglot()
    try:
        statement = sqlglot.parse_one(sql, read=dialect)
    except Exception as exc:  # sqlglot 解析异常族
        raise ColumnLineageError(f"SQL 解析失败: {exc}") from exc
    select = statement.find(exp.Select) if not isinstance(statement, exp.Select) else statement
    if select is None:
        raise ColumnLineageError("SQL 无 SELECT 投影（无法抽取列级血缘）")

    from_tables = {t.name for t in select.find_all(exp.Table) if t.name}
    edges: list[ColumnLineageEdge] = []
    for projection in select.expressions:
        target_column = projection.alias_or_name
        if not target_column:
            continue
        expression = projection.sql()[:_EXPR_MAX_LEN]
        for column in projection.find_all(exp.Column):
            source_table = column.table
            if not source_table:
                if len(from_tables) != 1:
                    raise ColumnLineageError(f"列 {column.name!r} 无表前缀且 FROM 多表歧义（Fail-Closed）")
                source_table = next(iter(from_tables))
            edges.append(
                ColumnLineageEdge(
                    source_table=source_table,
                    source_column=column.name,
                    target_table=target_table,
                    target_column=target_column,
                    expression=expression,
                )
            )
    return edges


def ingest_columns_into_tracker(
    edges: Sequence[ColumnLineageEdge],
    tracker: LineageTracker,
) -> LineageParseReport:
    """列边 → `table.column` 节点入 DAG（幂等/环/去重复用 MOD-DATA_GOV-004 语义）。

    transformation 记转换表达式（截断 80 字符）；tracker 为空 Fail-Closed。
    """
    if tracker is None:
        raise ColumnLineageError("tracker 不能为空（Fail-Closed）")
    dag_edges = [
        LineageEdge(
            column_node(edge.source_table, edge.source_column),
            column_node(edge.target_table, edge.target_column),
            f"column:{edge.expression[:_EXPR_MAX_LEN]}",
        )
        for edge in edges
    ]
    return ingest_into_tracker(dag_edges, tracker, sources=("column",))


def column_impact(tracker: LineageTracker, table: str, column: str) -> ColumnImpact:
    """字段级影响面查询：列节点的全部上游/下游（变更评审用；未知节点空结果）。"""
    if tracker is None:
        raise ColumnLineageError("tracker 不能为空（Fail-Closed）")
    node = column_node(table, column)
    return ColumnImpact(
        node=node,
        upstream=tuple(tracker.get_upstream(node)),
        downstream=tuple(tracker.get_downstream(node)),
    )
