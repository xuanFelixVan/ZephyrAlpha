# [BLUEPRINT] MOD-INF-087 | docs/03_modules/_domain_infrastructure_operations/runtime_topology_visualizer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-087 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_ops.test_runtime_topology_visualizer
# [TESTS] src/zephyr/infra_ops/runtime_topology_visualizer.py
"""MOD-INF-087 单元测试：runtime_topology_visualizer 运行时依赖拓扑器。

蓝图验收（B14-04635/CAND-INFRAOPS-005，A9运维架构）：
节点注册（PROCESS/REDIS/GPU/BROKER/DATAFEED）+ 心跳状态着色
（green/yellow/red 由心跳新鲜度+注入时钟判定）+ 数据流边标注
（Pub/Sub/KV/List）+ snapshot() JSON 字典供仪表盘消费（只后端数据）。
时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import json

import pytest

pytest.importorskip(
    "zephyr.infra_ops.runtime_topology_visualizer",
    reason="runtime_topology_visualizer not importable",
)

from zephyr.infra_ops.runtime_topology_visualizer import (  # noqa: E402
    EdgeLabel,
    NodeKind,
    NodeStatus,
    RuntimeTopologyError,
    RuntimeTopologyVisualizer,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _viz(now: datetime.datetime = _T0, yellow: float = 30.0, red: float = 90.0) -> RuntimeTopologyVisualizer:
    return RuntimeTopologyVisualizer(clock=lambda: now, yellow_after_s=yellow, red_after_s=red)


def _at(seconds_ago: float, now: datetime.datetime = _T0) -> datetime.datetime:
    return now - datetime.timedelta(seconds=seconds_ago)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruct:
    def test_negative_threshold_raises(self) -> None:
        with pytest.raises(RuntimeTopologyError):
            RuntimeTopologyVisualizer(clock=lambda: _T0, yellow_after_s=-1.0)

    def test_yellow_ge_red_raises(self) -> None:
        with pytest.raises(RuntimeTopologyError):
            RuntimeTopologyVisualizer(clock=lambda: _T0, yellow_after_s=90.0, red_after_s=90.0)


# ──────────────────────────────────────────────────────────────────────────────
# 节点/边注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_node_ok(self) -> None:
        viz = _viz()
        node = viz.register_node("P1", NodeKind.PROCESS, heartbeat_at=_T0)
        assert node.node_id == "P1" and node.kind is NodeKind.PROCESS

    def test_empty_node_id_raises(self) -> None:
        with pytest.raises(RuntimeTopologyError):
            _viz().register_node("", NodeKind.PROCESS)

    def test_duplicate_node_raises(self) -> None:
        viz = _viz()
        viz.register_node("redis", NodeKind.REDIS)
        with pytest.raises(RuntimeTopologyError):
            viz.register_node("redis", NodeKind.REDIS)

    def test_invalid_kind_raises(self) -> None:
        with pytest.raises(RuntimeTopologyError):
            _viz().register_node("x", "process")  # str 非 NodeKind

    def test_register_edge_ok_and_idempotent(self) -> None:
        viz = _viz()
        viz.register_node("P1", NodeKind.PROCESS)
        viz.register_node("redis", NodeKind.REDIS)
        viz.register_edge("P1", "redis", EdgeLabel.KV)
        viz.register_edge("P1", "redis", EdgeLabel.KV)  # 幂等
        snap = viz.snapshot()
        assert len(snap["edges"]) == 1

    def test_edge_unknown_endpoint_raises(self) -> None:
        viz = _viz()
        viz.register_node("P1", NodeKind.PROCESS)
        with pytest.raises(RuntimeTopologyError):
            viz.register_edge("P1", "ghost", EdgeLabel.PUB)

    def test_invalid_edge_label_raises(self) -> None:
        viz = _viz()
        viz.register_node("P1", NodeKind.PROCESS)
        viz.register_node("P2", NodeKind.PROCESS)
        with pytest.raises(RuntimeTopologyError):
            viz.register_edge("P1", "P2", "Pub")  # str 非 EdgeLabel


# ──────────────────────────────────────────────────────────────────────────────
# 心跳与着色
# ──────────────────────────────────────────────────────────────────────────────


class TestColoring:
    def test_fresh_green(self) -> None:
        viz = _viz()
        viz.register_node("gpu0", NodeKind.GPU, heartbeat_at=_at(5))
        viz.refresh_status()
        assert viz.snapshot()["nodes"][0]["status"] == "green"

    def test_yellow_zone(self) -> None:
        viz = _viz()
        viz.register_node("gpu0", NodeKind.GPU, heartbeat_at=_at(60))
        viz.refresh_status()
        assert viz.snapshot()["nodes"][0]["status"] == "yellow"

    def test_stale_red(self) -> None:
        viz = _viz()
        viz.register_node("gpu0", NodeKind.GPU, heartbeat_at=_at(120))
        viz.refresh_status()
        assert viz.snapshot()["nodes"][0]["status"] == "red"

    def test_no_heartbeat_red(self) -> None:
        viz = _viz()
        viz.register_node("gpu0", NodeKind.GPU)
        viz.refresh_status()
        assert viz.snapshot()["nodes"][0]["status"] == "red"

    def test_boundary_values(self) -> None:
        viz = _viz()
        viz.register_node("a", NodeKind.PROCESS, heartbeat_at=_at(30))   # 恰 yellow 阈 → green
        viz.register_node("b", NodeKind.PROCESS, heartbeat_at=_at(90))   # 恰 red 阈 → yellow
        viz.refresh_status()
        snap = {n["node_id"]: n["status"] for n in viz.snapshot()["nodes"]}
        assert snap == {"a": "green", "b": "yellow"}

    def test_heartbeat_unknown_raises(self) -> None:
        with pytest.raises(RuntimeTopologyError):
            _viz().heartbeat("ghost")

    def test_heartbeat_refreshes_color(self) -> None:
        now = _T0
        viz = RuntimeTopologyVisualizer(clock=lambda: now)
        viz.register_node("P1", NodeKind.PROCESS, heartbeat_at=_at(120))
        viz.refresh_status()
        assert viz.snapshot()["nodes"][0]["status"] == "red"
        viz.heartbeat("P1")  # 默认取注入时钟
        assert viz.snapshot()["nodes"][0]["status"] == "green"


# ──────────────────────────────────────────────────────────────────────────────
# 快照
# ──────────────────────────────────────────────────────────────────────────────


class TestSnapshot:
    def _full(self) -> RuntimeTopologyVisualizer:
        viz = _viz()
        viz.register_node("P2", NodeKind.PROCESS, heartbeat_at=_at(5))
        viz.register_node("P1", NodeKind.PROCESS, heartbeat_at=_at(5))
        viz.register_node("redis", NodeKind.REDIS, heartbeat_at=_at(60))
        viz.register_node("gpu0", NodeKind.GPU)
        viz.register_node("miniqmt", NodeKind.BROKER, heartbeat_at=_at(5))
        viz.register_node("ifind", NodeKind.DATAFEED, heartbeat_at=_at(200))
        viz.register_edge("P1", "redis", EdgeLabel.KV)
        viz.register_edge("P1", "P2", EdgeLabel.PUB)
        viz.register_edge("P2", "P1", EdgeLabel.SUB)
        viz.register_edge("redis", "P1", EdgeLabel.LIST)
        return viz

    def test_snapshot_sorted(self) -> None:
        snap = self._full().snapshot()
        ids = [n["node_id"] for n in snap["nodes"]]
        assert ids == sorted(ids)
        edge_keys = [(e["from"], e["to"], e["label"]) for e in snap["edges"]]
        assert edge_keys == sorted(edge_keys)

    def test_snapshot_json_serializable(self) -> None:
        snap = self._full().snapshot()
        text = json.dumps(snap, ensure_ascii=False)
        assert '"generated_at"' in text
        assert snap["generated_at"] == _T0.isoformat()

    def test_snapshot_fields(self) -> None:
        snap = self._full().snapshot()
        node = next(n for n in snap["nodes"] if n["node_id"] == "miniqmt")
        assert node["kind"] == "broker"
        assert node["status"] == "green"
        assert node["heartbeat_at"] is not None
        dead = next(n for n in snap["nodes"] if n["node_id"] == "gpu0")
        assert dead["heartbeat_at"] is None and dead["status"] == "red"

    def test_snapshot_deterministic(self) -> None:
        viz = self._full()
        assert viz.snapshot() == viz.snapshot()
