# [BLUEPRINT] MOD-SIG-112 | docs/03_modules/_domain_signal/event_causal_reasoner/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-112 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_event_causal_reasoner
# [TESTS] src/zephyr/signal_ashare/event_causal_reasoner.py
"""MOD-SIG-112 单元测试：event_causal_reasoner 事件因果推理器。

蓝图验收（B1-00125/CAND-TESTB-029，C2 D-ALT-22）：
传导边模板（三类词表闭合）+ DoWhy反事实降级 + sqlite时序存储 + BFS影响路径。
内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.event_causal_reasoner",
    reason="event_causal_reasoner not importable",
)

from zephyr.signal_ashare.event_causal_reasoner import (  # noqa: E402
    CausalImpactPath,
    ConductionEdgeTemplate,
    EventCausalError,
    EventCausalReasoner,
    EventType,
    RelationType,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE event_chain (event_type TEXT, triggered_at TEXT, path_count INTEGER)")
    return c


def _reasoner(**kwargs) -> EventCausalReasoner:
    kwargs.setdefault("clock", lambda: _T0)
    return EventCausalReasoner(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_decay_factor_out_of_range_raises(self) -> None:
        with pytest.raises(EventCausalError):
            _reasoner(decay_factor=0.0)
        with pytest.raises(EventCausalError):
            _reasoner(decay_factor=1.1)

    def test_max_hops_zero_raises(self) -> None:
        with pytest.raises(EventCausalError):
            _reasoner(max_hops=0)

    def test_min_cumulative_decay_out_of_range_raises(self) -> None:
        with pytest.raises(EventCausalError):
            _reasoner(min_cumulative_decay=1.0)


# ──────────────────────────────────────────────────────────────────────────────
# 模板
# ──────────────────────────────────────────────────────────────────────────────


class TestTemplate:
    def test_register_and_view(self) -> None:
        r = _reasoner()
        t = ConductionEdgeTemplate(
            event_type=EventType.POLICY,
            target_sectors=("新能源", "光伏"),
            relation_type=RelationType.UPSTREAM_DOWNSTREAM,
            decay=0.8,
        )
        r.register_template(t)
        assert r.templates() == (t,)

    def test_template_invalid_event_type_raises(self) -> None:
        with pytest.raises(EventCausalError):
            ConductionEdgeTemplate(
                event_type="INVALID",  # type: ignore[arg-type]
                target_sectors=("A",),
                relation_type=RelationType.PEER,
                decay=0.5,
            )

    def test_template_empty_sectors_raises(self) -> None:
        with pytest.raises(EventCausalError):
            ConductionEdgeTemplate(
                event_type=EventType.POLICY,
                target_sectors=(),
                relation_type=RelationType.PEER,
                decay=0.5,
            )

    def test_template_decay_out_of_range_raises(self) -> None:
        with pytest.raises(EventCausalError):
            ConductionEdgeTemplate(
                event_type=EventType.POLICY,
                target_sectors=("A",),
                relation_type=RelationType.PEER,
                decay=1.5,
            )


# ──────────────────────────────────────────────────────────────────────────────
# DoWhy反事实（降级不阻断）
# ──────────────────────────────────────────────────────────────────────────────


class TestDoWhy:
    def test_no_runner_downgrades(self) -> None:
        r = _reasoner(dowhy_runner=None)
        result = r.reason(EventType.POLICY)
        assert result.dowhy_downgraded is True
        assert "未注入" in result.dowhy_notes[0]

    def test_runner_ok(self) -> None:
        r = _reasoner(dowhy_runner=lambda et, ctx: {"effect": 0.12})
        result = r.reason(EventType.POLICY)
        assert result.dowhy_downgraded is False

    def test_runner_exception_downgrades(self) -> None:
        def _boom(et, ctx):
            raise RuntimeError("dowhy not installed")

        r = _reasoner(dowhy_runner=_boom)
        result = r.reason(EventType.POLICY)
        assert result.dowhy_downgraded is True
        assert "异常" in result.dowhy_notes[0]


# ──────────────────────────────────────────────────────────────────────────────
# 时序存储
# ──────────────────────────────────────────────────────────────────────────────


class TestStorage:
    def test_no_sqlite_skips(self) -> None:
        r = _reasoner(sqlite_conn=None)
        result = r.reason(EventType.POLICY)
        assert result.stored is False
        assert "跳过" in result.storage_notes[0]

    def test_sqlite_ok(self) -> None:
        conn = _conn()
        r = _reasoner(sqlite_conn=conn)
        t = ConductionEdgeTemplate(
            event_type=EventType.POLICY,
            target_sectors=("新能源",),
            relation_type=RelationType.UPSTREAM_DOWNSTREAM,
            decay=0.9,
        )
        r.register_template(t)
        result = r.reason(EventType.POLICY)
        assert result.stored is True
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM event_chain")
        assert cur.fetchone()[0] == 1


# ──────────────────────────────────────────────────────────────────────────────
# BFS影响路径
# ──────────────────────────────────────────────────────────────────────────────


class TestBFS:
    def test_empty_templates_returns_empty(self) -> None:
        r = _reasoner()
        result = r.reason(EventType.POLICY)
        assert result.impact_paths == ()

    def test_single_template_bfs(self) -> None:
        r = _reasoner(decay_factor=0.5)
        t = ConductionEdgeTemplate(
            event_type=EventType.POLICY,
            target_sectors=("新能源", "光伏"),
            relation_type=RelationType.UPSTREAM_DOWNSTREAM,
            decay=0.8,
        )
        r.register_template(t)
        result = r.reason(EventType.POLICY)
        assert len(result.impact_paths) == 2
        # 排序：累计衰减降序，相同按路径字典序
        assert result.impact_paths[0].path == ("政策", "光伏")
        assert result.impact_paths[1].path == ("政策", "新能源")
        assert result.impact_paths[0].cumulative_decay == pytest.approx(0.8 * 0.5)

    def test_unrelated_template_not_expanded(self) -> None:
        r = _reasoner(decay_factor=0.5, max_hops=3)
        t1 = ConductionEdgeTemplate(
            event_type=EventType.POLICY,
            target_sectors=("锂电",),
            relation_type=RelationType.UPSTREAM_DOWNSTREAM,
            decay=0.8,
        )
        t2 = ConductionEdgeTemplate(
            event_type=EventType.SECTOR_ROTATION,
            target_sectors=("新能源车",),
            relation_type=RelationType.PEER,
            decay=0.9,
        )
        # 注册 t2 但 event_type 不同，不影响 POLICY 的 BFS
        r.register_template(t1)
        r.register_template(t2)
        result = r.reason(EventType.POLICY)
        assert len(result.impact_paths) == 1
        assert result.impact_paths[0].hops == 1
        assert result.impact_paths[0].path == ("政策", "锂电")

    def test_min_cumulative_decay_prunes(self) -> None:
        r = _reasoner(decay_factor=0.5, min_cumulative_decay=0.5)
        r.register_template(
            ConductionEdgeTemplate(
                event_type=EventType.POLICY,
                target_sectors=("新能源",),
                relation_type=RelationType.PEER,
                decay=0.8,
            )
        )
        # 0.8*0.5=0.4 < 0.5 剪枝
        result = r.reason(EventType.POLICY)
        assert result.impact_paths == ()

    def test_invalid_event_type_raises(self) -> None:
        r = _reasoner()
        with pytest.raises(EventCausalError):
            r.reason("INVALID")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        def _build() -> EventCausalReasoner:
            r = _reasoner()
            r.register_template(
                ConductionEdgeTemplate(
                    event_type=EventType.POLICY,
                    target_sectors=("A", "B"),
                    relation_type=RelationType.PEER,
                    decay=0.7,
                )
            )
            return r

        r1 = _build()
        r2 = _build()
        res1 = r1.reason(EventType.POLICY)
        res2 = r2.reason(EventType.POLICY)
        assert res1.impact_paths == res2.impact_paths
        assert res1.triggered_at == res2.triggered_at
