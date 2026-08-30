# [BLUEPRINT] MOD-DATA_GOV-005 | docs/03_modules/_domain_data_governance/static_lineage_analyzer/blueprint.md
# [MODULE] zephyr.data_governance.core.static_lineage_analyzer
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.lineage_tracker; zephyr.data_governance.core.lineage_parser
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 幂等与环检测复用 MOD-DATA_GOV-002 不重造; 入图语义复用 MOD-DATA_GOV-004 ingest_into_tracker 不重造; 语法错误/空模块名/空SQL Fail-Closed; 非字面量路径跳过不成边; sqlglot 缺失 SQL 面降级 fail-open 记 degraded 不中断批
# [MODIFY-GUARD] tests/data_governance/test_static_lineage_analyzer.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StaticLineageError(未登记错误码-申请中); SqlglotUnavailableError(未登记错误码-申请中)
# [TESTS] tests/data_governance/test_static_lineage_analyzer.py
# [A_module] module_id=MOD-DATA_GOV-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
M8-S02 静态分析器（MOD-DATA_GOV-005）。

真源：construction_backlog_dig.tsv B10-02314（A1 交易决策架构 §30.4.3，
裁定=做 P1）+ CAND-DATGOV-002。

定位：代码/SQL 静态分析提取血缘为零起步（TSV 现状）。与血缘族分工：

  ① S01 血缘解析器（MOD-DATA_GOV-004）：解析**契约定义**（CTR 契约/模块头注解）；
     本模块解析**代码/SQL 文本**——输入面不同，入图语义（批内去重/幂等 updated/
     环 rejected 不中断）复用 S01 `ingest_into_tracker` 不重造；
  ② 表级粒度：本模块出**表级/文件级**边；列级（table.column）归
     column_lineage_analyzer（MOD-DATA_GOV-007，M8-NEW-02）；
  ③ 离线批跑不占盘中资源：无后台线程、无定时器，由调用方批扫驱动。

sqlglot 依赖裁定：TSV 指定 sqlglot 解析 SQL 表级血缘，但 sqlglot 尚未登记为项目
依赖（requirements/pyproject 均无）——SQL 面走懒加载，未安装时批跑 fail-open
记 degraded 不中断（Python AST 面不受影响）；依赖登记后补 SQL 面 happy-path
集成测试。不内置 regex SQL 解析器（易碎且非 TSV 指定形态）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: source 参数
#   fields: 参数 source，类型注解 str
#   code: static_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: module 参数
#   fields: 参数 module（无注解）
#   code: static_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sql 参数
#   fields: 参数 sql，类型注解 str
#   code: static_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dialect 参数
#   fields: 参数 dialect（无注解）
#   code: static_lineage_analyzer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① extract_python_io_edges
#   name_en: extract_python_io_edges
#   intro: ast 解析 Python 读写调用 → 血缘边（读 path→module；写 module→path）。
#   desc: ast 解析 Python 读写调用 → 血缘边（读 path→module；写 module→path）。 仅字符串字面量路径成边；变量/拼接等动态路径跳过（保守不错抽）。 语…；源码 L192-L221
#   inputs: source module
#   outputs: list[LineageEdge]
# - id: A2
#   name_zh: ② extract_sql_table_edges
#   name_en: extract_sql_table_edges
#   intro: sqlglot 解析单条 SQL → 表级血缘边（源表 --sql--> 目标表）。
#   desc: sqlglot 解析单条 SQL → 表级血缘边（源表 --sql--> 目标表）。 无目标表的纯查询不出边；空 SQL Fail-Closed；sqlglot 未安装 → Sq…；源码 L245-L262
#   inputs: sql dialect
#   outputs: list[LineageEdge]
# - id: A3
#   name_zh: ③ analyze_sources
#   name_en: analyze_sources
#   intro: 批量静态分析入图（离线批跑；幂等/环/去重复用 MOD-DATA_GOV-004 入图语义）。
#   desc: 批量静态分析入图（离线批跑；幂等/环/去重复用 MOD-DATA_GOV-004 入图语义）。 - python_sources: {模块名: 源码文本}，逐文件 ast 抽取；…；源码 L265-L314
#   inputs: python_sources sql_sources tracker dialect sources
#   outputs: StaticLineageReport
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[LineageEdge]
#   name_en: list[LineageEdge]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: StaticLineageReport
#   name_en: StaticLineageReport
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
# A3 --> O1
"""

from __future__ import annotations

import ast
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from zephyr.data_governance.core.lineage_parser import ingest_into_tracker
from zephyr.data_governance.core.lineage_tracker import LineageEdge, LineageTracker

__all__: Final = [
    "SqlglotUnavailableError",
    "StaticLineageError",
    "StaticLineageReport",
    "analyze_sources",
    "extract_python_io_edges",
    "extract_sql_table_edges",
]

_log = logging.getLogger(__name__)

TRANSFORMATION_READS: Final[str] = "reads"
TRANSFORMATION_WRITES: Final[str] = "writes"
TRANSFORMATION_SQL: Final[str] = "sql"

#: Python 读函数词表（末段属性名/裸函数名匹配）
_READ_FUNCS: Final = frozenset(
    {"read_parquet", "read_csv", "read_sql", "read_table", "read_json", "read_feather", "read_orc"}
)
#: Python 写函数词表
_WRITE_FUNCS: Final = frozenset({"to_parquet", "to_csv", "to_json", "to_feather", "to_orc", "write_parquet"})
#: 路径关键字参数词表（位置参数缺位时兜底）
_PATH_KWARGS: Final = frozenset({"path", "filepath", "file_path"})


class StaticLineageError(ValueError):
    """静态血缘解析输入畸形（Fail-Closed；未登记错误码-申请中）。"""


class SqlglotUnavailableError(StaticLineageError):
    """sqlglot 未安装，SQL 表级血缘解析不可用（未登记错误码-申请中）。"""


@dataclass(frozen=True)
class StaticLineageReport:
    """静态分析批跑报告。

    Attributes:
        files: 本批解析来源数（Python 文件 + SQL 语句）
        edges: 抽取边总数
        added: 新入图边数
        updated: tracker 幂等重加边数
        rejected: 环拒记 (source, target, reason) 三元组
        skipped: 批内 (source,target) 重复去重边数（首条胜出）
        degraded: 降级留痕（如 sqlglot 缺失致 SQL 面整体跳过）
        sources: 本批解析来源标签
    """

    files: int
    edges: int
    added: int
    updated: int
    rejected: tuple[tuple[str, str, str], ...] = ()
    skipped: int = 0
    degraded: tuple[str, ...] = ()
    sources: tuple[str, ...] = field(default=())


def _func_leaf_name(func: ast.expr) -> str:
    """取调用末段名：pd.read_parquet→read_parquet；df.to_parquet→to_parquet；裸名直取。"""
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _literal_path(call: ast.Call) -> str | None:
    """首位置字符串字面量路径，或 path/filepath/file_path 关键字字面量；否则 None（跳过）。"""
    if call.args:
        first = call.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        return None  # 位置参数非字面量（变量/拼接/表达式）→ 不成边
    for kw in call.keywords:
        if kw.arg in _PATH_KWARGS and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return kw.value.value
    return None


def extract_python_io_edges(source: str, *, module: str) -> list[LineageEdge]:
    """ast 解析 Python 读写调用 → 血缘边（读 path→module；写 module→path）。

    仅字符串字面量路径成边；变量/拼接等动态路径跳过（保守不错抽）。
    语法错误/空模块名 Fail-Closed（StaticLineageError）。
    """
    if not isinstance(module, str) or not module.strip():
        raise StaticLineageError(f"模块名为空: module={module!r}")
    module = module.strip()
    if not isinstance(source, str):
        raise StaticLineageError(f"Python 源码非字符串: {type(source).__name__}")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise StaticLineageError(f"Python 语法错误（{module}）: {exc.msg} @L{exc.lineno}") from exc

    edges: list[LineageEdge] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        leaf = _func_leaf_name(node.func)
        if leaf in _READ_FUNCS:
            path = _literal_path(node)
            if path is not None and path.strip():
                edges.append(LineageEdge(path.strip(), module, TRANSFORMATION_READS))
        elif leaf in _WRITE_FUNCS:
            path = _literal_path(node)
            if path is not None and path.strip():
                edges.append(LineageEdge(module, path.strip(), TRANSFORMATION_WRITES))
    return edges


def _import_sqlglot():
    """sqlglot 懒加载（未登记依赖，登记前 SQL 面降级）。"""
    try:
        import sqlglot
        from sqlglot import exp
    except ImportError as exc:
        raise SqlglotUnavailableError("sqlglot 未安装（三方依赖登记申请中），SQL 表级血缘解析不可用") from exc
    return sqlglot, exp


def _target_table_name(statement, exp) -> str | None:
    """INSERT INTO / CREATE TABLE AS 目标表名；纯查询返回 None（薄胶水，依赖登记后补测）。"""
    if isinstance(statement, (exp.Insert, exp.Create)):
        this = statement.this
        if isinstance(this, exp.Schema):
            this = this.this
        if isinstance(this, exp.Table):
            return this.name
    return None


def extract_sql_table_edges(sql: str, *, dialect: str | None = None) -> list[LineageEdge]:
    """sqlglot 解析单条 SQL → 表级血缘边（源表 --sql--> 目标表）。

    无目标表的纯查询不出边；空 SQL Fail-Closed；sqlglot 未安装
    → SqlglotUnavailableError（批跑面捕获记 degraded）。
    """
    if not isinstance(sql, str) or not sql.strip():
        raise StaticLineageError(f"SQL 文本为空: {sql!r}")
    sqlglot, exp = _import_sqlglot()
    try:
        statement = sqlglot.parse_one(sql, read=dialect)
    except Exception as exc:  # sqlglot 解析异常族（ParseError 等）
        raise StaticLineageError(f"SQL 解析失败: {exc}") from exc
    target = _target_table_name(statement, exp)
    if target is None:
        return []
    sources = {table.name for table in statement.find_all(exp.Table) if table.name and table.name != target}
    return [LineageEdge(src, target, TRANSFORMATION_SQL) for src in sorted(sources)]


def analyze_sources(
    *,
    python_sources: Mapping[str, str] | None = None,
    sql_sources: Mapping[str, str] | None = None,
    tracker: LineageTracker,
    dialect: str | None = None,
    sources: Sequence[str] = (),
) -> StaticLineageReport:
    """批量静态分析入图（离线批跑；幂等/环/去重复用 MOD-DATA_GOV-004 入图语义）。

    - python_sources: {模块名: 源码文本}，逐文件 ast 抽取；
    - sql_sources: {来源标签: SQL 文本}，sqlglot 未安装时整面跳过记 degraded
      （fail-open 不中断批，Python 面不受影响）；
    - tracker 为空 Fail-Closed。
    """
    if tracker is None:
        raise StaticLineageError("tracker 不能为空（Fail-Closed）")
    python_sources = python_sources or {}
    sql_sources = sql_sources or {}

    edges: list[LineageEdge] = []
    files = 0
    degraded: list[str] = []

    for module, text in python_sources.items():
        edges.extend(extract_python_io_edges(text, module=module))
        files += 1

    if sql_sources:
        try:
            _import_sqlglot()
        except SqlglotUnavailableError as exc:
            degraded.append(str(exc))
            _log.warning("SQL 表级血缘面降级跳过: %s", exc)
        else:
            for _label, sql in sql_sources.items():
                edges.extend(extract_sql_table_edges(sql, dialect=dialect))
                files += 1

    ingest = ingest_into_tracker(edges, tracker, sources=sources)
    return StaticLineageReport(
        files=files,
        edges=ingest.edges,
        added=ingest.added,
        updated=ingest.updated,
        rejected=ingest.rejected,
        skipped=ingest.skipped,
        degraded=tuple(degraded),
        sources=tuple(sources),
    )
