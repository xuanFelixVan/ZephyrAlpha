# [BLUEPRINT] MOD-OPS-003 | docs/03_modules/_domain_infrastructure/asset_inventory/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-OPS-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.system_telemetry.test_asset_inventory
# [TESTS] src/zephyr/infrastructure/system_telemetry/asset_inventory.py
"""MOD-OPS-003 单元测试：asset_inventory 资产盘点器。

蓝图验收（B9-11648/CAND-OPS-003，B9 OPS-06）：
统一资产索引（类型词表闭合 + 注册表校验）+ 健康评分三分量（元数据完整度/
依赖连通/新鲜度）+ 孤儿率统计（无依赖且无归属）+ 依赖图生成（确定性排序）。
时钟注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.asset_inventory",
    reason="asset_inventory not importable",
)

from zephyr.infrastructure.system_telemetry.asset_inventory import (  # noqa: E402
    Asset,
    AssetInventory,
    AssetInventoryError,
    AssetType,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 0, 0)


class _Clock:
    def __init__(self) -> None:
        self.now = _T0

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


def _inv(clock: _Clock | None = None, ttl: float = 3600.0) -> AssetInventory:
    return AssetInventory(clock=(clock or _Clock()), freshness_ttl_seconds=ttl)


def _asset(
    asset_id: str = "svc-gateway",
    asset_type: AssetType = AssetType.SERVICE,
    owner: str | None = "ops-team",
    metadata: dict | None = None,
    dependencies: tuple[str, ...] = (),
    refreshed_at: datetime.datetime = _T0,
) -> Asset:
    return Asset(
        asset_id=asset_id,
        asset_type=asset_type,
        name=asset_id,
        owner=owner,
        metadata=metadata if metadata is not None else {
            "description": "d", "version": "v1", "environment": "prod",
        },
        dependencies=dependencies,
        refreshed_at=refreshed_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册表（类型词表 + 校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok_and_get(self) -> None:
        inv = _inv()
        inv.register(_asset())
        assert inv.get("svc-gateway").asset_type is AssetType.SERVICE

    def test_register_empty_id_raises(self) -> None:
        inv = _inv()
        with pytest.raises(AssetInventoryError):
            inv.register(_asset(asset_id=""))

    def test_register_empty_name_raises(self) -> None:
        inv = _inv()
        a = _asset()
        bad = Asset(
            asset_id=a.asset_id, asset_type=a.asset_type, name="",
            owner=a.owner, metadata=a.metadata,
            dependencies=a.dependencies, refreshed_at=a.refreshed_at,
        )
        with pytest.raises(AssetInventoryError):
            inv.register(bad)

    def test_register_invalid_type_raises(self) -> None:
        inv = _inv()
        a = _asset()
        bad = Asset(
            asset_id=a.asset_id, asset_type="vm",  # type: ignore[arg-type]
            name=a.name, owner=a.owner, metadata=a.metadata,
            dependencies=a.dependencies, refreshed_at=a.refreshed_at,
        )
        with pytest.raises(AssetInventoryError):
            inv.register(bad)

    def test_register_duplicate_raises(self) -> None:
        inv = _inv()
        inv.register(_asset())
        with pytest.raises(AssetInventoryError):
            inv.register(_asset())

    def test_register_self_dependency_raises(self) -> None:
        inv = _inv()
        with pytest.raises(AssetInventoryError):
            inv.register(_asset(dependencies=("svc-gateway",)))

    def test_register_empty_dependency_raises(self) -> None:
        inv = _inv()
        with pytest.raises(AssetInventoryError):
            inv.register(_asset(dependencies=("",)))

    def test_register_non_asset_raises(self) -> None:
        inv = _inv()
        with pytest.raises(AssetInventoryError):
            inv.register("not-an-asset")  # type: ignore[arg-type]

    def test_deregister_ok_and_unknown_raises(self) -> None:
        inv = _inv()
        inv.register(_asset())
        inv.deregister("svc-gateway")
        with pytest.raises(AssetInventoryError):
            inv.get("svc-gateway")
        with pytest.raises(AssetInventoryError):
            inv.deregister("svc-gateway")

    def test_invalid_ttl_raises(self) -> None:
        with pytest.raises(AssetInventoryError):
            _inv(ttl=0.0)

    def test_list_assets_filter_and_sort(self) -> None:
        inv = _inv()
        inv.register(_asset("svc-b", AssetType.SERVICE))
        inv.register(_asset("db-a", AssetType.DATABASE))
        inv.register(_asset("svc-a", AssetType.SERVICE))
        assert [a.asset_id for a in inv.list_assets()] == ["db-a", "svc-a", "svc-b"]
        assert [a.asset_id for a in inv.list_assets(AssetType.SERVICE)] == ["svc-a", "svc-b"]
        with pytest.raises(AssetInventoryError):
            inv.list_assets("service")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 健康评分（三分量）
# ──────────────────────────────────────────────────────────────────────────────


class TestHealthScore:
    def test_full_metadata_completeness(self) -> None:
        inv = _inv()
        inv.register(_asset())
        assert inv.health_score("svc-gateway").metadata_completeness == 1.0

    def test_partial_metadata_completeness(self) -> None:
        inv = _inv()
        inv.register(_asset(metadata={"description": "d"}))
        score = inv.health_score("svc-gateway")
        assert score.metadata_completeness == pytest.approx(1 / 3, abs=1e-6)

    def test_connectivity_no_deps_full(self) -> None:
        inv = _inv()
        inv.register(_asset())
        assert inv.health_score("svc-gateway").dependency_connectivity == 1.0

    def test_connectivity_partial_known(self) -> None:
        inv = _inv()
        inv.register(_asset("db-a", AssetType.DATABASE))
        inv.register(_asset("svc-gateway", dependencies=("db-a", "ghost")))
        score = inv.health_score("svc-gateway")
        assert score.dependency_connectivity == 0.5

    def test_freshness_fresh_within_ttl(self) -> None:
        clock = _Clock()
        inv = _inv(clock)
        inv.register(_asset())
        clock.advance(3000.0)  # < ttl 3600
        assert inv.health_score("svc-gateway").freshness == 1.0

    def test_freshness_linear_decay(self) -> None:
        clock = _Clock()
        inv = _inv(clock)
        inv.register(_asset())
        clock.advance(5400.0)  # ttl*1.5 → 0.5
        assert inv.health_score("svc-gateway").freshness == 0.5

    def test_freshness_stale_beyond_double_ttl_zero(self) -> None:
        clock = _Clock()
        inv = _inv(clock)
        inv.register(_asset())
        clock.advance(7200.0)
        assert inv.health_score("svc-gateway").freshness == 0.0

    def test_total_is_mean_of_components(self) -> None:
        inv = _inv()
        inv.register(_asset(metadata={"description": "d"}))
        score = inv.health_score("svc-gateway")
        expected = round((score.metadata_completeness + 1.0 + 1.0) / 3, 6)
        assert score.total == pytest.approx(expected, abs=1e-6)

    def test_health_unknown_raises(self) -> None:
        inv = _inv()
        with pytest.raises(AssetInventoryError):
            inv.health_score("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 孤儿率统计
# ──────────────────────────────────────────────────────────────────────────────


class TestOrphanStats:
    def test_orphan_no_deps_no_owner(self) -> None:
        inv = _inv()
        inv.register(_asset("svc-gateway", owner=None))
        stats = inv.orphan_stats()
        assert stats.orphan_ids == ("svc-gateway",)
        assert stats.orphan_count == 1
        assert stats.orphan_rate == 1.0

    def test_owner_present_not_orphan(self) -> None:
        inv = _inv()
        inv.register(_asset("svc-gateway", owner="ops-team"))
        assert inv.orphan_stats().orphan_count == 0

    def test_deps_present_not_orphan(self) -> None:
        inv = _inv()
        inv.register(_asset("db-a", AssetType.DATABASE, owner=None))
        inv.register(_asset("svc-gateway", owner=None, dependencies=("db-a",)))
        stats = inv.orphan_stats()
        assert stats.orphan_ids == ("db-a",)  # db-a 无依赖无归属才是孤儿

    def test_orphan_rate_and_sorted_ids(self) -> None:
        inv = _inv()
        inv.register(_asset("z-orphan", owner=None))
        inv.register(_asset("a-orphan", owner=None))
        inv.register(_asset("svc-gateway"))
        inv.register(_asset("db-a", AssetType.DATABASE, owner="dba"))
        stats = inv.orphan_stats()
        assert stats.total_assets == 4
        assert stats.orphan_count == 2
        assert stats.orphan_rate == 0.5
        assert stats.orphan_ids == ("a-orphan", "z-orphan")

    def test_empty_inventory_rate_zero(self) -> None:
        stats = _inv().orphan_stats()
        assert stats.total_assets == 0
        assert stats.orphan_rate == 0.0
        assert stats.orphan_ids == ()


# ──────────────────────────────────────────────────────────────────────────────
# 依赖图
# ──────────────────────────────────────────────────────────────────────────────


class TestDependencyGraph:
    def test_nodes_edges_sorted(self) -> None:
        inv = _inv()
        inv.register(_asset("db-b", AssetType.DATABASE))
        inv.register(_asset("db-a", AssetType.DATABASE))
        inv.register(_asset("svc-gateway", dependencies=("db-b", "db-a")))
        graph = inv.dependency_graph()
        assert graph.nodes == ("db-a", "db-b", "svc-gateway")
        assert graph.edges == (("svc-gateway", "db-a"), ("svc-gateway", "db-b"))

    def test_edges_exclude_unregistered_deps(self) -> None:
        inv = _inv()
        inv.register(_asset("svc-gateway", dependencies=("ghost",)))
        graph = inv.dependency_graph()
        assert graph.nodes == ("svc-gateway",)
        assert graph.edges == ()

    def test_determinism_same_inputs_same_graph(self) -> None:
        def _build():
            inv = _inv()
            inv.register(_asset("db-a", AssetType.DATABASE))
            inv.register(_asset("svc-gateway", dependencies=("db-a",)))
            return inv.dependency_graph(), inv.orphan_stats()

        assert _build() == _build()
