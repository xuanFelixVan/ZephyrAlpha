# [BLUEPRINT] MOD-DATA_GOV-005 | docs/03_modules/_domain_data_governance/static_lineage_analyzer/blueprint.md | §test
# [MODULE] tests.data_governance.test_static_lineage_analyzer
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.static_lineage_analyzer
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_static_lineage_analyzer.py
# [A_test] module_id: MOD-DATA_GOV-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_GOV-005 单元测试: M8-S02 静态分析器。

覆盖: AST 读/写边抽取（字符串字面量路径）、非字面量路径跳过、未知函数忽略、
语法错误 Fail-Closed、空模块名 Fail-Closed、sqlglot 缺失 SqlglotUnavailableError、
批跑面 SQL 降级 fail-open 记 degraded、批内去重/幂等 updated/环拒记不中断复用语义、
端到端 抽取→入图→上下游查询。
"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.lineage_tracker import LineageTracker
from zephyr.data_governance.core.static_lineage_analyzer import (
    SqlglotUnavailableError,
    StaticLineageError,
    StaticLineageReport,
    analyze_sources,
    extract_python_io_edges,
    extract_sql_table_edges,
)

_MOD = "zephyr.factor.compute_momentum"

_PY_READ = """\
import pandas as pd

def load():
    return pd.read_parquet("data/kline_daily.parquet")
"""

_PY_WRITE = """\
def save(df):
    df.to_parquet("data/factor_momentum.parquet")
"""

_PY_MIXED = """\
import pandas as pd

def pipeline(out_path):
    a = pd.read_parquet("data/a.parquet")
    b = pd.read_csv("data/b.csv")
    c = pd.read_parquet(out_path)  # 非字面量：跳过
    a.to_parquet("data/out.parquet")
    unknown_call("data/x.parquet")
    return a
"""


class TestExtractPythonIOEdges:
    def test_read_literal_path(self) -> None:
        edges = extract_python_io_edges(_PY_READ, module=_MOD)
        assert len(edges) == 1
        e = edges[0]
        assert e.source == "data/kline_daily.parquet"
        assert e.target == _MOD
        assert e.transformation == "reads"

    def test_write_literal_path(self) -> None:
        edges = extract_python_io_edges(_PY_WRITE, module=_MOD)
        assert len(edges) == 1
        e = edges[0]
        assert e.source == _MOD
        assert e.target == "data/factor_momentum.parquet"
        assert e.transformation == "writes"

    def test_mixed_dynamic_skipped_and_unknown_ignored(self) -> None:
        edges = extract_python_io_edges(_PY_MIXED, module=_MOD)
        pairs = {(e.source, e.target, e.transformation) for e in edges}
        assert ("data/a.parquet", _MOD, "reads") in pairs
        assert ("data/b.csv", _MOD, "reads") in pairs
        assert (_MOD, "data/out.parquet", "writes") in pairs
        # 非字面量路径与未知函数均不成边
        assert len(edges) == 3

    def test_keyword_path_literal(self) -> None:
        src = 'import pandas as pd\ndf = pd.read_parquet(path="data/kw.parquet")\n'
        edges = extract_python_io_edges(src, module=_MOD)
        assert len(edges) == 1
        assert edges[0].source == "data/kw.parquet"

    def test_syntax_error_fail_closed(self) -> None:
        with pytest.raises(StaticLineageError):
            extract_python_io_edges("def broken(:\n", module=_MOD)

    def test_empty_module_fail_closed(self) -> None:
        with pytest.raises(StaticLineageError):
            extract_python_io_edges(_PY_READ, module="  ")

    def test_empty_source_yields_no_edges(self) -> None:
        assert extract_python_io_edges("x = 1\n", module=_MOD) == []


class TestExtractSqlTableEdges:
    def test_sqlglot_missing_fail_closed(self) -> None:
        # 本环境 sqlglot 未登记安装 → 显式不可用错误（依赖登记后补 happy-path）
        try:
            import sqlglot  # noqa: F401
        except ImportError:
            with pytest.raises(SqlglotUnavailableError):
                extract_sql_table_edges("INSERT INTO t SELECT * FROM s")
        else:
            edges = extract_sql_table_edges("INSERT INTO t SELECT * FROM s")
            assert (edges[0].source, edges[0].target) == ("s", "t")

    def test_empty_sql_fail_closed(self) -> None:
        with pytest.raises(StaticLineageError):
            extract_sql_table_edges("   ")


class TestAnalyzeSources:
    def test_python_only_batch_ingest(self) -> None:
        tracker = LineageTracker()
        report = analyze_sources(
            python_sources={_MOD: _PY_MIXED},
            tracker=tracker,
            sources=("test",),
        )
        assert isinstance(report, StaticLineageReport)
        assert report.files == 1
        assert report.edges == 3
        assert report.added == 3
        assert report.updated == 0
        assert report.rejected == ()
        assert report.degraded == ()
        assert "data/a.parquet" in tracker.get_upstream(_MOD)
        assert "data/out.parquet" in tracker.get_downstream(_MOD)

    def test_sql_degraded_fail_open_when_sqlglot_missing(self) -> None:
        try:
            import sqlglot  # noqa: F401

            pytest.skip("sqlglot 已安装环境不走降级路径")
        except ImportError:
            pass
        tracker = LineageTracker()
        report = analyze_sources(
            python_sources={_MOD: _PY_READ},
            sql_sources={"job_daily": "INSERT INTO t SELECT * FROM s"},
            tracker=tracker,
        )
        # fail-open：Python 面正常入图，SQL 面记 degraded 不中断
        assert report.added == 1
        assert len(report.degraded) == 1
        assert "sqlglot" in report.degraded[0]

    def test_batch_two_files_same_path_no_false_dedup(self) -> None:
        tracker = LineageTracker()
        report = analyze_sources(
            python_sources={"m1": _PY_READ, "m2": _PY_READ},
            tracker=tracker,
        )
        # 两文件同读一路径→不同边（target 不同），不构成去重
        assert report.edges == 2
        assert report.added == 2

    def test_idempotent_reingest_counts_updated(self) -> None:
        tracker = LineageTracker()
        analyze_sources(python_sources={_MOD: _PY_READ}, tracker=tracker)
        report2 = analyze_sources(python_sources={_MOD: _PY_READ}, tracker=tracker)
        assert report2.added == 0
        assert report2.updated == 1

    def test_none_tracker_fail_closed(self) -> None:
        with pytest.raises(StaticLineageError):
            analyze_sources(python_sources={_MOD: _PY_READ}, tracker=None)

    def test_end_to_end_upstream_downstream(self) -> None:
        tracker = LineageTracker()
        analyze_sources(python_sources={_MOD: _PY_MIXED}, tracker=tracker)
        upstream = tracker.get_upstream(_MOD)
        downstream = tracker.get_downstream(_MOD)
        assert set(upstream) == {"data/a.parquet", "data/b.csv"}
        assert downstream == ["data/out.parquet"]
