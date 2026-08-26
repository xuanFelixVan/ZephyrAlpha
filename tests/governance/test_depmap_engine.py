# [BLUEPRINT] MOD-GOV-051 | docs/03_modules/_domain_governance/depmap_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-051 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.governance.test_depmap_engine
# [TESTS] src/zephyr/governance/depmap_engine.py
"""MOD-GOV-051 单元测试：depmap_engine DepMap 依赖扫描引擎。

蓝图验收（B13-04303/CAND-WORKTREE-002，A3 MOD-INF-040）：
AST import 解析（ast.walk + 目录过滤）→ 分层（L0/L1/L2 层注册表）存储 →
与 depgraph 库 diff（注入 depgraph_reader 回调）→ 循环依赖 / 越层调用报告。
depgraph reader 全注入内存替身，不触库不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.governance.depmap_engine",
    reason="depmap_engine not importable",
)

from zephyr.governance.depmap_engine import (  # noqa: E402
    DepmapEngine,
    DepmapError,
    DepmapLayer,
)

_REGISTRY = {
    "zephyr.shared": DepmapLayer.L0,
    "zephyr.domain": DepmapLayer.L1,
    "zephyr.app": DepmapLayer.L2,
}

_SOURCES = {
    "src/zephyr/shared/util.py": "import datetime\n",
    "src/zephyr/domain/svc.py": (
        "import zephyr.shared.util\nfrom zephyr.shared import util\n"
    ),
    "src/zephyr/app/main.py": (
        "import zephyr.domain.svc\nfrom . import sibling\n"
    ),
    "src/zephyr/app/sibling.py": "from zephyr.domain import svc\n",
}


def _engine(reader=None) -> DepmapEngine:
    return DepmapEngine(layer_registry=_REGISTRY, depgraph_reader=reader)


def _scanned(reader=None, sources=None) -> DepmapEngine:
    engine = _engine(reader)
    engine.scan_sources(_SOURCES if sources is None else sources)
    return engine


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_registry_raises(self) -> None:
        with pytest.raises(DepmapError):
            DepmapEngine(layer_registry={})

    def test_invalid_layer_raises(self) -> None:
        with pytest.raises(DepmapError):
            DepmapEngine(layer_registry={"zephyr.x": "L9"})

    def test_empty_prefix_raises(self) -> None:
        with pytest.raises(DepmapError):
            DepmapEngine(layer_registry={"": DepmapLayer.L0})


# ──────────────────────────────────────────────────────────────────────────────
# AST 扫描（目录过滤 / 语法错误 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestScan:
    def test_basic_import_edges(self) -> None:
        engine = _scanned()
        pairs = {(e.importer, e.imported) for e in engine.edges()}
        assert ("zephyr.domain.svc", "zephyr.shared.util") in pairs
        assert ("zephyr.domain.svc", "zephyr.shared") in pairs
        assert ("zephyr.app.main", "zephyr.domain.svc") in pairs

    def test_relative_import_resolved(self) -> None:
        engine = _scanned()
        pairs = {(e.importer, e.imported) for e in engine.edges()}
        # from . import sibling（zephyr.app.main 内）→ zephyr.app.sibling
        assert ("zephyr.app.main", "zephyr.app.sibling") in pairs

    def test_module_name_normalization(self) -> None:
        engine = _engine()
        engine.scan_sources({"src/zephyr/shared/__init__.py": "import os\n"})
        importers = {e.importer for e in engine.edges()}
        assert importers == {"zephyr.shared"}

    def test_syntax_error_raises(self) -> None:
        engine = _engine()
        with pytest.raises(DepmapError):
            engine.scan_sources({"src/zephyr/app/bad.py": "def broken(:\n"})

    def test_relative_beyond_top_raises(self) -> None:
        engine = _engine()
        with pytest.raises(DepmapError):
            engine.scan_sources({"src/zephyr/top.py": "from .. import x\n"})

    def test_non_py_path_raises(self) -> None:
        engine = _engine()
        with pytest.raises(DepmapError):
            engine.scan_sources({"src/zephyr/app/readme.md": "import os\n"})
        with pytest.raises(DepmapError):
            engine.scan_sources({"": "import os\n"})

    def test_include_prefix_filter(self) -> None:
        engine = _engine()
        added = engine.scan_sources(_SOURCES, include_prefixes=("src/zephyr/app/",))
        pairs = {(e.importer, e.imported) for e in engine.edges()}
        assert added == 3
        assert all(imp.startswith("zephyr.app") for imp, _ in pairs)

    def test_exclude_prefix_filter(self) -> None:
        engine = _engine()
        engine.scan_sources(_SOURCES, exclude_prefixes=("src/zephyr/app/",))
        importers = {e.importer for e in engine.edges()}
        assert "zephyr.app.main" not in importers
        assert "zephyr.domain.svc" in importers

    def test_scan_idempotent(self) -> None:
        engine = _engine()
        first = engine.scan_sources(_SOURCES)
        second = engine.scan_sources(_SOURCES)
        assert first > 0
        assert second == 0

    def test_edges_deterministic_order(self) -> None:
        a = _scanned()
        b = _scanned()
        assert a.edges() == b.edges()
        keys = [(e.importer, e.imported, e.lineno) for e in a.edges()]
        assert keys == sorted(keys)


# ──────────────────────────────────────────────────────────────────────────────
# 分层存储 / 越层报告
# ──────────────────────────────────────────────────────────────────────────────


class TestLayer:
    def test_edges_by_layer(self) -> None:
        engine = _scanned()
        l2 = engine.edges_by_layer(DepmapLayer.L2)
        assert {e.importer for e in l2} == {"zephyr.app.main", "zephyr.app.sibling"}
        l0 = engine.edges_by_layer(DepmapLayer.L0)
        assert {e.importer for e in l0} == {"zephyr.shared.util"}

    def test_edges_by_layer_invalid_raises(self) -> None:
        engine = _scanned()
        with pytest.raises(DepmapError):
            engine.edges_by_layer("L9")

    def test_downward_and_same_layer_no_violation(self) -> None:
        engine = _scanned()
        assert engine.layer_violations() == []

    def test_upward_import_violation(self) -> None:
        engine = _scanned(sources={
            "src/zephyr/shared/util.py": "import zephyr.app.main\n",
        })
        violations = engine.layer_violations()
        assert len(violations) == 1
        v = violations[0]
        assert v.importer == "zephyr.shared.util"
        assert v.importer_layer is DepmapLayer.L0
        assert v.imported_layer is DepmapLayer.L2
        assert "越层" in v.reason

    def test_unregistered_endpoint_ignored(self) -> None:
        engine = _scanned(sources={
            "src/zephyr/shared/util.py": "import requests\n",
        })
        assert engine.layer_violations() == []
        assert engine.find_cycles() == []


# ──────────────────────────────────────────────────────────────────────────────
# depgraph diff（注入 reader）
# ──────────────────────────────────────────────────────────────────────────────


class TestDiff:
    def test_reader_not_injected_fail_closed(self) -> None:
        engine = _scanned()
        with pytest.raises(DepmapError):
            engine.diff_depgraph()

    def test_diff_missing_and_stale(self) -> None:
        known = [
            ("zephyr.domain.svc", "zephyr.shared.util"),
            ("zephyr.legacy.old", "zephyr.shared.util"),  # 陈旧
        ]
        engine = _scanned(reader=lambda: known)
        diff = engine.diff_depgraph()
        assert ("zephyr.legacy.old", "zephyr.shared.util") in diff.stale_in_depgraph
        assert ("zephyr.app.main", "zephyr.domain.svc") in diff.missing_in_depgraph
        assert ("zephyr.domain.svc", "zephyr.shared.util") not in diff.missing_in_depgraph

    def test_diff_clean(self) -> None:
        scanned = {("zephyr.app.a", "zephyr.shared.util")}
        engine = DepmapEngine(layer_registry=_REGISTRY, depgraph_reader=lambda: scanned)
        engine.scan_sources({"src/zephyr/app/a.py": "import zephyr.shared.util\n"})
        diff = engine.diff_depgraph()
        assert diff.missing_in_depgraph == ()
        assert diff.stale_in_depgraph == ()

    def test_reader_error_wrapped(self) -> None:
        def _boom():
            raise RuntimeError("pg down")

        engine = _scanned(reader=_boom)
        with pytest.raises(DepmapError):
            engine.diff_depgraph()


# ──────────────────────────────────────────────────────────────────────────────
# 循环依赖报告
# ──────────────────────────────────────────────────────────────────────────────


class TestCycles:
    def test_acyclic(self) -> None:
        engine = _scanned()
        assert engine.find_cycles() == []

    def test_simple_two_node_cycle(self) -> None:
        engine = _scanned(sources={
            "src/zephyr/app/a.py": "import zephyr.app.b\n",
            "src/zephyr/app/b.py": "import zephyr.app.a\n",
        })
        cycles = engine.find_cycles()
        assert cycles == [("zephyr.app.a", "zephyr.app.b")]

    def test_three_node_cycle_normalized(self) -> None:
        engine = _scanned(sources={
            "src/zephyr/app/c.py": "import zephyr.app.a\n",
            "src/zephyr/app/a.py": "import zephyr.app.b\n",
            "src/zephyr/app/b.py": "import zephyr.app.c\n",
        })
        cycles = engine.find_cycles()
        assert cycles == [("zephyr.app.a", "zephyr.app.b", "zephyr.app.c")]
        # 确定性：同输入重扫必同输出
        assert _scanned(sources={
            "src/zephyr/app/c.py": "import zephyr.app.a\n",
            "src/zephyr/app/a.py": "import zephyr.app.b\n",
            "src/zephyr/app/b.py": "import zephyr.app.c\n",
        }).find_cycles() == cycles
