# [BLUEPRINT] MOD-FE-006 | docs/03_modules/_domain_frontend/domain_mapping_view/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-006 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_domain_mapping_view
# [TESTS] src/zephyr/frontend/domain_mapping_view.py
"""MOD-FE-006 单元测试：domain_mapping_view 域映射矩阵视图器。

蓝图验收（B10-02409/CAND-FE-007，A1 M6-S07）：
映射关系登记（architecture_model 快照注入语义）+ 矩阵单元格计数聚合 +
桑基流量边（源→目标权重）+ 未映射孤儿清单。快照/时钟全内存注入，不触库。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.domain_mapping_view",
    reason="domain_mapping_view not importable",
)

from zephyr.frontend.domain_mapping_view import (  # noqa: E402
    DomainMappingError,
    DomainMappingView,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_ENTITIES = ("e1", "e2", "e3", "e4", "e5")


def _view(entities=_ENTITIES) -> DomainMappingView:
    return DomainMappingView(known_entities=entities, clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 构造与登记（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_init_ok(self) -> None:
        view = _view()
        assert view.orphans() == _ENTITIES

    def test_empty_snapshot_raises(self) -> None:
        with pytest.raises(DomainMappingError):
            DomainMappingView(known_entities=[], clock=lambda: _T0)

    def test_blank_entity_in_snapshot_raises(self) -> None:
        with pytest.raises(DomainMappingError):
            DomainMappingView(known_entities=["e1", ""], clock=lambda: _T0)

    def test_register_ok_with_clock(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        mapping = view.mapping_of("e1")
        assert mapping.business_domain == "交易域"
        assert mapping.db_domain == "DB_TRADE"
        assert mapping.registered_at == _T0  # 时钟 DI 注入

    def test_unknown_entity_raises(self) -> None:
        with pytest.raises(DomainMappingError):
            _view().register_mapping("ghost", "交易域", "DB_TRADE")

    def test_blank_domain_raises(self) -> None:
        view = _view()
        with pytest.raises(DomainMappingError):
            view.register_mapping("e1", "", "DB_TRADE")
        with pytest.raises(DomainMappingError):
            view.register_mapping("e1", "交易域", "")

    def test_duplicate_same_triple_idempotent(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e1", "交易域", "DB_TRADE")  # 幂等不抛
        assert len(view.matrix().cells) == 1

    def test_conflicting_duplicate_raises(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        with pytest.raises(DomainMappingError):
            view.register_mapping("e1", "风控域", "DB_RISK")

    def test_mapping_of_unregistered_raises(self) -> None:
        with pytest.raises(DomainMappingError):
            _view().mapping_of("e1")


# ──────────────────────────────────────────────────────────────────────────────
# 矩阵计数聚合
# ──────────────────────────────────────────────────────────────────────────────


class TestMatrix:
    def test_cell_count_aggregation(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "交易域", "DB_TRADE")
        view.register_mapping("e3", "交易域", "DB_RISK")
        view.register_mapping("e4", "风控域", "DB_RISK")
        matrix = view.matrix()
        counts = {(c.business_domain, c.db_domain): c.count for c in matrix.cells}
        assert counts == {
            ("交易域", "DB_TRADE"): 2,
            ("交易域", "DB_RISK"): 1,
            ("风控域", "DB_RISK"): 1,
        }

    def test_rows_cols_sorted(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "风控域", "DB_RISK")
        matrix = view.matrix()
        assert matrix.rows == tuple(sorted(matrix.rows))
        assert matrix.cols == tuple(sorted(matrix.cols))

    def test_cells_sorted(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "风控域", "DB_RISK")
        matrix = view.matrix()
        keys = [(c.business_domain, c.db_domain) for c in matrix.cells]
        assert keys == sorted(keys)

    def test_empty_mapping_matrix(self) -> None:
        matrix = _view().matrix()
        assert matrix.rows == () and matrix.cols == () and matrix.cells == ()


# ──────────────────────────────────────────────────────────────────────────────
# 桑基流量边 / 孤儿清单
# ──────────────────────────────────────────────────────────────────────────────


class TestSankeyAndOrphans:
    def test_sankey_weights_match_matrix(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "交易域", "DB_TRADE")
        view.register_mapping("e3", "风控域", "DB_RISK")
        flows = view.sankey_edges()
        weights = {(f.source, f.target): f.weight for f in flows}
        matrix = view.matrix()
        assert weights == {(c.business_domain, c.db_domain): c.count for c in matrix.cells}

    def test_sankey_sorted(self) -> None:
        view = _view()
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "风控域", "DB_RISK")
        pairs = [(f.source, f.target) for f in view.sankey_edges()]
        assert pairs == sorted(pairs)

    def test_orphans_unmapped_sorted(self) -> None:
        view = _view()
        view.register_mapping("e3", "交易域", "DB_TRADE")
        view.register_mapping("e1", "风控域", "DB_RISK")
        assert view.orphans() == ("e2", "e4", "e5")

    def test_orphans_empty_when_all_mapped(self) -> None:
        view = _view(entities=("e1", "e2"))
        view.register_mapping("e1", "交易域", "DB_TRADE")
        view.register_mapping("e2", "交易域", "DB_TRADE")
        assert view.orphans() == ()

    def test_deterministic(self) -> None:
        def _build() -> DomainMappingView:
            view = _view()
            view.register_mapping("e2", "交易域", "DB_TRADE")
            view.register_mapping("e1", "交易域", "DB_TRADE")
            view.register_mapping("e3", "风控域", "DB_RISK")
            return view

        assert _build().matrix() == _build().matrix()
        assert _build().sankey_edges() == _build().sankey_edges()
        assert _build().orphans() == _build().orphans()
