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
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_UNKNOWN,
    SYSTEM_HEALTH_SOURCE_NAMES,
    GlobalStateAggregator,
    GlobalStateError,
    StateDomain,
    StateSnapshot,
    build_system_health_collector,
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


# ──────────────────────────────────────────────────────────────────────────────
# L-4 系统健康域四源绑定（排班表 v2 §2.2 L-4 / P2-d）
# ──────────────────────────────────────────────────────────────────────────────


def _healthy_sampler() -> dict:
    return {
        "entities_total": 72,
        "observable_tasks": 18,
        "host_shared_skipped": 3,
        "evidence_rows": 5,
        "direction_counts": {"match": 4, "underdeclared": 1},
    }


def _healthy_incubator() -> dict:
    return {
        "water_percent": 41.3,
        "queue_line_percent": 85.0,
        "reject_line_percent": 90.0,
        "ledger_stats": {"total": 4, "active": 2, "expired_active": 0, "owners": ["boot_hooks"]},
    }


def _healthy_gpu() -> dict:
    return {"available": True, "gpu_count": 1, "gpu_percent": 12.0, "memory_used_gb": 3.0, "memory_total_gb": 24.0}


def _healthy_reaper() -> dict:
    return {"ghost_suspects": 0, "suspect_pids": []}


def _collector(**overrides):
    stubs = {
        "resource_sampler_summary": _healthy_sampler,
        "incubator_water_level": _healthy_incubator,
        "gpu_stats": _healthy_gpu,
        "reaper_outcome": _healthy_reaper,
    }
    stubs.update(overrides)
    return build_system_health_collector(**stubs)


_ALL_STUBS_DOWN = {
    "resource_sampler_summary": lambda: (_ for _ in ()).throw(OSError("nope")),
    "incubator_water_level": lambda: (_ for _ in ()).throw(OSError("nope")),
    "gpu_stats": lambda: (_ for _ in ()).throw(OSError("nope")),
    "reaper_outcome": lambda: (_ for _ in ()).throw(OSError("nope")),
}

_PAYLOAD_KEYS = {
    "status",
    "sources",
    "sources_total",
    "healthy_count",
    "degraded_sources",
    "unhealthy_sources",
    "unknown_sources",
    "water_percent",
    "incubator_active",
    "gpu_available",
    "gpu_percent",
    "ghost_suspects",
    "sampler_evidence_rows",
}


class TestL4SystemHealthBinding:
    def test_four_healthy_sources_roll_up_to_healthy(self) -> None:
        payload = _collector()()
        assert payload["status"] == HEALTH_STATUS_HEALTHY
        assert payload["sources_total"] == 4
        assert payload["healthy_count"] == 4
        assert payload["degraded_sources"] == []
        assert payload["unhealthy_sources"] == []
        assert payload["unknown_sources"] == []
        assert list(payload["sources"].keys()) == list(SYSTEM_HEALTH_SOURCE_NAMES)  # 确定性键序

    def test_metrics_pass_through_verbatim(self) -> None:
        payload = _collector()()
        assert payload["sources"]["incubator"]["metrics"]["water_percent"] == 41.3
        assert payload["sources"]["resource_sampler"]["metrics"]["evidence_rows"] == 5
        assert payload["sources"]["gpu_monitor"]["metrics"]["gpu_count"] == 1
        assert payload["sources"]["reaper"]["metrics"]["ghost_suspects"] == 0

    def test_flat_convenience_fields_populated(self) -> None:
        payload = _collector()()
        assert payload["water_percent"] == 41.3
        assert payload["incubator_active"] == 2
        assert payload["gpu_available"] is True
        assert payload["gpu_percent"] == 12.0
        assert payload["ghost_suspects"] == 0
        assert payload["sampler_evidence_rows"] == 5

    # ── 逐源判定规则 ──

    def test_gpu_unavailable_degrades_not_unhealthy(self) -> None:
        payload = _collector(gpu_stats=lambda: {"available": False})()
        assert payload["sources"]["gpu_monitor"]["status"] == HEALTH_STATUS_DEGRADED
        assert payload["status"] == HEALTH_STATUS_DEGRADED
        assert payload["degraded_sources"] == ["gpu_monitor"]

    def test_water_at_reject_line_is_unhealthy(self) -> None:
        def _hot():
            m = _healthy_incubator()
            m["water_percent"] = 93.5
            return m

        payload = _collector(incubator_water_level=_hot)()
        assert payload["sources"]["incubator"]["status"] == HEALTH_STATUS_UNHEALTHY
        assert payload["status"] == HEALTH_STATUS_UNHEALTHY
        assert "拒绝线" in payload["sources"]["incubator"]["note"]

    def test_water_at_queue_line_degrades(self) -> None:
        def _warm():
            m = _healthy_incubator()
            m["water_percent"] = 86.0
            return m

        payload = _collector(incubator_water_level=_warm)()
        assert payload["sources"]["incubator"]["status"] == HEALTH_STATUS_DEGRADED

    def test_expired_incubation_degrades(self) -> None:
        def _leak():
            m = _healthy_incubator()
            m["ledger_stats"] = {"total": 9, "active": 3, "expired_active": 2, "owners": ["x"]}
            return m

        payload = _collector(incubator_water_level=_leak)()
        assert payload["sources"]["incubator"]["status"] == HEALTH_STATUS_DEGRADED

    def test_reaper_open_suspects_degrade(self) -> None:
        payload = _collector(reaper_outcome=lambda: {"ghost_suspects": 2, "suspect_pids": [1, 2]})()
        assert payload["sources"]["reaper"]["status"] == HEALTH_STATUS_DEGRADED
        assert payload["ghost_suspects"] == 2

    def test_sampler_zero_evidence_degrades(self) -> None:
        def _dry():
            m = _healthy_sampler()
            m["evidence_rows"] = 0
            return m

        payload = _collector(resource_sampler_summary=_dry)()
        assert payload["sources"]["resource_sampler"]["status"] == HEALTH_STATUS_DEGRADED

    def test_sampler_zero_observable_degrades(self) -> None:
        def _blind():
            m = _healthy_sampler()
            m["observable_tasks"] = 0
            return m

        payload = _collector(resource_sampler_summary=_blind)()
        assert payload["sources"]["resource_sampler"]["status"] == HEALTH_STATUS_DEGRADED

    # ── 隔离与降级 ──

    def test_source_exception_is_isolated_not_raised(self) -> None:
        def _boom():
            raise RuntimeError("nvidia-smi 挂了")

        payload = _collector(gpu_stats=_boom)()
        section = payload["sources"]["gpu_monitor"]
        assert section["status"] == HEALTH_STATUS_UNHEALTHY
        assert section["available"] is False
        assert "nvidia-smi 挂了" in section["error"]
        assert payload["status"] == HEALTH_STATUS_UNHEALTHY
        assert payload["unhealthy_sources"] == ["gpu_monitor"]
        assert payload["healthy_count"] == 3  # 他源不受影响

    def test_source_non_mapping_is_unhealthy(self) -> None:
        payload = _collector(reaper_outcome=lambda: [1, 2])()
        assert payload["sources"]["reaper"]["status"] == HEALTH_STATUS_UNHEALTHY
        assert "非 Mapping" in payload["sources"]["reaper"]["error"]

    def test_key_set_is_constant_even_when_all_sources_fail(self) -> None:
        happy = set(_collector()())
        broken_payload = _collector(**_ALL_STUBS_DOWN)()
        assert happy == set(broken_payload) == _PAYLOAD_KEYS  # 下游按键读取永不 KeyError
        for section in broken_payload["sources"].values():
            assert set(section) == {"status", "available", "note", "error", "metrics"}
        assert broken_payload["unknown_sources"] == []  # 炸=UNHEALTHY 而非 UNKNOWN

    def test_missing_metrics_leave_flat_defaults_not_keyerror(self) -> None:
        payload = _collector(
            resource_sampler_summary=lambda: {},
            incubator_water_level=lambda: {},
            gpu_stats=lambda: {},
            reaper_outcome=lambda: {},
        )()
        assert payload["water_percent"] is None
        assert payload["incubator_active"] is None
        assert payload["gpu_available"] is False
        assert payload["gpu_percent"] is None
        assert payload["ghost_suspects"] is None
        assert payload["sampler_evidence_rows"] is None

    # ── 与聚合器端到端接线 ──

    def test_registered_into_aggregator_and_json_serialisable(self) -> None:
        agg = _agg(_collectors(**{StateDomain.SYSTEM_HEALTH: _collector()}))
        snap = agg.collect(snapshot_id="snap-l4")
        assert snap.healthy is True
        data = json.loads(snap.to_json())
        health = data["domains"]["system_health"]
        assert health["ok"] is True
        assert health["payload"]["status"] == HEALTH_STATUS_HEALTHY
        assert sorted(health["payload"]["sources"]) == sorted(SYSTEM_HEALTH_SOURCE_NAMES)

    def test_overall_json_deterministic_with_binding(self) -> None:
        agg = _agg(_collectors(**{StateDomain.SYSTEM_HEALTH: _collector()}))
        s1 = agg.collect(snapshot_id="snap-l4")
        assert s1.to_json() == agg.collect(snapshot_id="snap-l4").to_json()

    def test_source_degrade_does_not_degrade_domain_reading(self) -> None:
        agg = _agg(
            _collectors(
                **{
                    StateDomain.SYSTEM_HEALTH: _collector(
                        reaper_outcome=lambda: {"ghost_suspects": 1, "suspect_pids": [7]}
                    )
                }
            )
        )
        snap = agg.collect()
        assert snap.healthy is True  # 采集成功=域不降级；源内降级≠域降级
        assert snap.reading_of(StateDomain.SYSTEM_HEALTH).payload["status"] == HEALTH_STATUS_DEGRADED

    # ── 缺省适配器与词表 ──

    def test_default_adapters_cover_all_four_sources(self) -> None:
        from zephyr.orchestrator.global_state_aggregator import _DEFAULT_SOURCE_ADAPTERS

        assert set(_DEFAULT_SOURCE_ADAPTERS) == set(SYSTEM_HEALTH_SOURCE_NAMES)
        for adapter in _DEFAULT_SOURCE_ADAPTERS.values():
            assert callable(adapter)

    def test_health_vocabulary_matches_system_telemetry(self) -> None:
        """词表对齐：本件四常量字面量须与 HealthStatus 真源逐字一致。"""
        health_mod = pytest.importorskip(
            "zephyr.infrastructure.system_telemetry.health",
            reason="system_telemetry.health not importable",
        )
        vocab = {
            health_mod.HealthStatus.HEALTHY,
            health_mod.HealthStatus.DEGRADED,
            health_mod.HealthStatus.UNHEALTHY,
            health_mod.HealthStatus.UNKNOWN,
        }
        assert {
            HEALTH_STATUS_HEALTHY,
            HEALTH_STATUS_DEGRADED,
            HEALTH_STATUS_UNHEALTHY,
            HEALTH_STATUS_UNKNOWN,
        } == vocab

    def test_core_import_pulls_no_executor_modules(self) -> None:
        """零依赖不变量：仅 import 本件不得连带拉起四执行体（延迟 import 纪律）。"""
        import subprocess
        import sys

        code = (
            "import sys;"
            "import zephyr.orchestrator.global_state_aggregator;"
            "print(any(m.startswith('zephyr.trading.gpu_monitor')"
            " or m.startswith('zephyr.trading.process_reaper')"
            " or m.startswith('zephyr.shared.infra.process_incubator')"
            " or m.startswith('zephyr.infrastructure.system_telemetry.resource_sampler')"
            " for m in sys.modules))"
        )
        # 子进程隔离：本进程模块表已被同批其他测试污染，只有在干净解释器里
        # "仅 import 本件"才等价于生产导入路径。
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=180, check=False
        )
        assert out.returncode == 0, out.stderr
        assert out.stdout.strip().endswith("False"), out.stdout
