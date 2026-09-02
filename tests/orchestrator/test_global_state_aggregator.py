# [BLUEPRINT] MOD-ORCH-002 | docs/03_modules/_domain_orchestrator/global_state_aggregator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ORCH-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.orchestrator.test_global_state_aggregator
# [TESTS] src/zephyr/orchestrator/global_state_aggregator.py
"""MOD-ORCH-002 单元测试：global_state_aggregator 全局状态聚合器。

蓝图验收（B1-00201/CAND-ORCH-002，C2）：持仓/资金/风控/策略/市场/系统健康
六域采集器注入（词表闭合）→ 统一 StateSnapshot JSON + 采集失败降级标记 +
确定性快照序 + Fail-Closed 非法输入。采集器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import json

import pytest

pytest.importorskip(
    "zephyr.orchestrator.global_state_aggregator",
    reason="global_state_aggregator not importable",
)

from zephyr.orchestrator.global_state_aggregator import (  # noqa: E402
    GlobalStateAggregator,
    GlobalStateError,
    StateDomain,
    StateSnapshot,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _collectors(**overrides) -> dict:
    base = {
        StateDomain.POSITION: lambda: {"positions": [{"symbol": "600000", "qty": 100}]},
        StateDomain.CAPITAL: lambda: {"cash": 1_000_000.0},
        StateDomain.RISK: lambda: {"max_drawdown": 0.05},
        StateDomain.STRATEGY: lambda: {"active": ["t0", "grid"]},
        StateDomain.MARKET: lambda: {"index": 3200.5},
        StateDomain.SYSTEM_HEALTH: lambda: {"cpu": 0.3, "mem": 0.5},
    }
    base.update(overrides)
    return base


def _agg(collectors=None) -> GlobalStateAggregator:
    return GlobalStateAggregator(
        collectors=collectors if collectors is not None else _collectors(),
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造与注册（词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_six_domain_collectors_ok(self) -> None:
        agg = _agg()
        assert agg.registered_domains() == tuple(StateDomain)  # 枚举序确定性

    def test_empty_collectors_raises(self) -> None:
        with pytest.raises(GlobalStateError):
            GlobalStateAggregator(collectors={}, clock=lambda: _T0)

    def test_unknown_domain_raises(self) -> None:
        with pytest.raises(GlobalStateError):
            GlobalStateAggregator(collectors={"ghost_domain": lambda: {}}, clock=lambda: _T0)

    def test_non_callable_collector_raises(self) -> None:
        with pytest.raises(GlobalStateError):
            GlobalStateAggregator(collectors={StateDomain.POSITION: "not-callable"}, clock=lambda: _T0)

    def test_partial_domains_ok(self) -> None:
        agg = GlobalStateAggregator(collectors={StateDomain.MARKET: lambda: {"index": 1}}, clock=lambda: _T0)
        assert agg.registered_domains() == (StateDomain.MARKET,)

    def test_register_collector_late(self) -> None:
        agg = GlobalStateAggregator(collectors={StateDomain.MARKET: lambda: {}}, clock=lambda: _T0)
        agg.register_collector(StateDomain.RISK, lambda: {"var": 0.01})
        assert agg.registered_domains() == (StateDomain.RISK, StateDomain.MARKET)

    def test_register_duplicate_raises(self) -> None:
        agg = _agg()
        with pytest.raises(GlobalStateError):
            agg.register_collector(StateDomain.POSITION, lambda: {})


# ──────────────────────────────────────────────────────────────────────────────
# 采集与快照（降级标记）
# ──────────────────────────────────────────────────────────────────────────────


class TestCollect:
    def test_collect_all_ok(self) -> None:
        snap = _agg().collect()
        assert isinstance(snap, StateSnapshot)
        assert snap.healthy is True
        assert snap.degraded_domains == ()
        assert len(snap.readings) == 6
        assert [r.domain for r in snap.readings] == list(StateDomain)  # 枚举序

    def test_collect_failure_degraded_not_blocking(self) -> None:
        def _boom():
            raise RuntimeError("券商连接断开")

        agg = _agg(_collectors(**{StateDomain.POSITION: _boom}))
        snap = agg.collect()
        assert snap.healthy is False
        assert snap.degraded_domains == (StateDomain.POSITION,)
        assert snap.reading_of(StateDomain.POSITION).ok is False
        assert "券商连接断开" in snap.reading_of(StateDomain.POSITION).error
        assert snap.reading_of(StateDomain.CAPITAL).ok is True  # 他域不阻断

    def test_collect_non_mapping_payload_degraded(self) -> None:
        agg = _agg(_collectors(**{StateDomain.MARKET: lambda: [1, 2, 3]}))
        snap = agg.collect()
        assert snap.degraded_domains == (StateDomain.MARKET,)
        assert snap.reading_of(StateDomain.MARKET).error

    def test_collect_deterministic_snapshot_id_seq(self) -> None:
        agg = _agg()
        s1 = agg.collect()
        s2 = agg.collect()
        assert (s1.snapshot_id, s2.snapshot_id) == ("snap-000001", "snap-000002")

    def test_collect_explicit_snapshot_id(self) -> None:
        snap = _agg().collect(snapshot_id="snap-manual-1")
        assert snap.snapshot_id == "snap-manual-1"

    def test_collect_empty_snapshot_id_raises(self) -> None:
        with pytest.raises(GlobalStateError):
            _agg().collect(snapshot_id="")

    def test_snapshot_immutable_payload_copy(self) -> None:
        src = {"cash": 1.0}
        agg = _agg(_collectors(**{StateDomain.CAPITAL: lambda: src}))
        snap = agg.collect()
        src["cash"] = 999.0  # 采集后外部变更不影响快照
        assert snap.reading_of(StateDomain.CAPITAL).payload["cash"] == 1.0


# ──────────────────────────────────────────────────────────────────────────────
# 查询与 JSON
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_latest_before_collect_raises(self) -> None:
        with pytest.raises(GlobalStateError):
            _agg().latest()

    def test_latest_returns_last_snapshot(self) -> None:
        agg = _agg()
        agg.collect()
        s2 = agg.collect()
        assert agg.latest() is s2

    def test_reading_of_unknown_domain_raises(self) -> None:
        snap = _agg().collect()
        with pytest.raises(GlobalStateError):
            snap.reading_of("ghost_domain")

    def test_reading_of_unregistered_domain_raises(self) -> None:
        agg = GlobalStateAggregator(collectors={StateDomain.MARKET: lambda: {}}, clock=lambda: _T0)
        snap = agg.collect()
        with pytest.raises(GlobalStateError):
            snap.reading_of(StateDomain.RISK)

    def test_to_json_deterministic_and_parseable(self) -> None:
        agg = _agg()
        snap = agg.collect()
        j1 = snap.to_json()
        j2 = agg.collect(snapshot_id=snap.snapshot_id).to_json()
        assert j1 == j2  # 同输入必同输出
        data = json.loads(j1)
        assert data["healthy"] is True
        assert sorted(data["domains"].keys()) == sorted(d.value for d in StateDomain)
        assert data["collected_at"] == _T0.isoformat()

    def test_to_json_marks_degraded(self) -> None:
        def _boom():
            raise ValueError("x")

        agg = _agg(_collectors(**{StateDomain.RISK: _boom}))
        data = json.loads(agg.collect().to_json())
        assert data["healthy"] is False
        assert data["degraded_domains"] == ["risk"]
        assert data["domains"]["risk"]["ok"] is False
