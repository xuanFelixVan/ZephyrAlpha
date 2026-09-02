# [BLUEPRINT] MOD-OPS-001 | docs/03_modules/_domain_infrastructure/ops_incident_aggregate/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-OPS-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.system_telemetry.test_ops_incident_aggregate
# [TESTS] src/zephyr/infrastructure/system_telemetry/ops_incident_aggregate.py
"""MOD-OPS-001 单元测试：ops_incident_aggregate 运维事件聚合根。

蓝图验收（B9-11460/CAND-OPS-001，B9 D-OPS）：
P0~P2 分级词表闭合 + 状态机（open→ack→mitigating→resolved→postmortem 仅正向单步）
+ 事件三件套（detected/escalated/resolved Schema 留痕）+ 持久化注入 +
升级仅向更高严重级且终态禁止 + 查询确定性排序。
时钟/事件 sink/持久化全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.ops_incident_aggregate",
    reason="ops_incident_aggregate not importable",
)

from zephyr.infrastructure.system_telemetry.ops_incident_aggregate import (  # noqa: E402
    DetectedEvent,
    EscalatedEvent,
    IncidentEventKind,
    IncidentSeverity,
    IncidentStatus,
    OpsIncident,
    OpsIncidentAggregate,
    OpsIncidentError,
    ResolvedEvent,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 0, 0)
_T1 = datetime.datetime(2026, 8, 26, 9, 5, 0)


def _agg(
    sink: list | None = None,
    store: list | None = None,
) -> OpsIncidentAggregate:
    return OpsIncidentAggregate(
        clock=lambda: _T1,
        event_sink=sink.append if sink is not None else None,
        store=store.append if store is not None else None,
    )


def _detected(
    incident_id: str = "INC-1",
    severity: IncidentSeverity = IncidentSeverity.P1,
) -> DetectedEvent:
    return DetectedEvent(
        incident_id=incident_id,
        severity=severity,
        title="撮合延迟突增",
        source="latency_attributor",
        occurred_at=_T0,
    )


def _opened(agg: OpsIncidentAggregate, incident_id: str = "INC-1") -> OpsIncident:
    return agg.detect(_detected(incident_id))


def _mitigating(agg: OpsIncidentAggregate, incident_id: str = "INC-1") -> OpsIncident:
    _opened(agg, incident_id)
    agg.acknowledge(incident_id)
    return agg.start_mitigation(incident_id)


# ──────────────────────────────────────────────────────────────────────────────
# 检测登记（三件套之 detected）
# ──────────────────────────────────────────────────────────────────────────────


class TestDetect:
    def test_detect_ok_creates_open(self) -> None:
        agg = _agg()
        inc = _opened(agg)
        assert inc.status is IncidentStatus.OPEN
        assert inc.severity is IncidentSeverity.P1
        assert inc.detected_at == _T0
        assert inc.history == (IncidentEventKind.DETECTED,)

    def test_detect_emits_event_and_persists(self) -> None:
        sink: list = []
        store: list = []
        agg = _agg(sink, store)
        event = _detected()
        inc = agg.detect(event)
        assert sink == [event]
        assert store == [inc]

    def test_detect_empty_id_raises(self) -> None:
        agg = _agg()
        with pytest.raises(OpsIncidentError):
            agg.detect(_detected(incident_id=""))

    def test_detect_empty_title_raises(self) -> None:
        agg = _agg()
        event = DetectedEvent(
            incident_id="INC-1",
            severity=IncidentSeverity.P1,
            title="",
            source="s",
            occurred_at=_T0,
        )
        with pytest.raises(OpsIncidentError):
            agg.detect(event)

    def test_detect_empty_source_raises(self) -> None:
        agg = _agg()
        event = DetectedEvent(
            incident_id="INC-1",
            severity=IncidentSeverity.P1,
            title="t",
            source="",
            occurred_at=_T0,
        )
        with pytest.raises(OpsIncidentError):
            agg.detect(event)

    def test_detect_invalid_severity_raises(self) -> None:
        agg = _agg()
        event = DetectedEvent(
            incident_id="INC-1",
            severity="P9",  # type: ignore[arg-type]
            title="t",
            source="s",
            occurred_at=_T0,
        )
        with pytest.raises(OpsIncidentError):
            agg.detect(event)

    def test_detect_duplicate_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        with pytest.raises(OpsIncidentError):
            agg.detect(_detected())

    def test_detect_sink_exception_swallowed(self) -> None:
        def _bad_sink(_e: object) -> None:
            raise RuntimeError("boom")

        agg = OpsIncidentAggregate(clock=lambda: _T1, event_sink=_bad_sink)
        inc = agg.detect(_detected())
        assert inc.status is IncidentStatus.OPEN


# ──────────────────────────────────────────────────────────────────────────────
# 状态机（仅正向单步）
# ──────────────────────────────────────────────────────────────────────────────


class TestStateMachine:
    def test_full_lifecycle(self) -> None:
        agg = _agg()
        _opened(agg)
        assert agg.acknowledge("INC-1").status is IncidentStatus.ACK
        assert agg.start_mitigation("INC-1").status is IncidentStatus.MITIGATING
        assert (
            agg.resolve(
                ResolvedEvent(
                    incident_id="INC-1",
                    resolution="扩容撮合线程池",
                    occurred_at=_T1,
                )
            ).status
            is IncidentStatus.RESOLVED
        )
        assert agg.close_postmortem("INC-1").status is IncidentStatus.POSTMORTEM

    def test_skip_transition_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        with pytest.raises(OpsIncidentError):
            agg.start_mitigation("INC-1")  # open → mitigating 越步

    def test_resolve_before_mitigating_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        agg.acknowledge("INC-1")
        with pytest.raises(OpsIncidentError):
            agg.resolve(
                ResolvedEvent(
                    incident_id="INC-1",
                    resolution="r",
                    occurred_at=_T1,
                )
            )  # ack → resolved 越步

    def test_terminal_blocks_transition(self) -> None:
        agg = _agg()
        _mitigating(agg)
        agg.resolve(ResolvedEvent(incident_id="INC-1", resolution="r", occurred_at=_T1))
        agg.close_postmortem("INC-1")
        with pytest.raises(OpsIncidentError):
            agg.acknowledge("INC-1")

    def test_unknown_incident_raises(self) -> None:
        agg = _agg()
        with pytest.raises(OpsIncidentError):
            agg.acknowledge("ghost")
        with pytest.raises(OpsIncidentError):
            agg.close_postmortem("ghost")

    def test_resolve_emits_event_persists_and_appends_history(self) -> None:
        sink: list = []
        store: list = []
        agg = _agg(sink, store)
        _mitigating(agg)
        event = ResolvedEvent(incident_id="INC-1", resolution="重启网关", occurred_at=_T1)
        inc = agg.resolve(event)
        assert sink[-1] is event
        assert store[-1] == inc
        assert inc.history == (IncidentEventKind.DETECTED, IncidentEventKind.RESOLVED)

    def test_resolve_empty_resolution_raises(self) -> None:
        agg = _agg()
        _mitigating(agg)
        with pytest.raises(OpsIncidentError):
            agg.resolve(ResolvedEvent(incident_id="INC-1", resolution="", occurred_at=_T1))

    def test_transition_persists_each_step(self) -> None:
        store: list = []
        agg = _agg(store=store)
        _opened(agg)
        agg.acknowledge("INC-1")
        agg.start_mitigation("INC-1")
        assert [s.status for s in store] == [
            IncidentStatus.OPEN,
            IncidentStatus.ACK,
            IncidentStatus.MITIGATING,
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 升级（仅向更高严重级，终态禁止）
# ──────────────────────────────────────────────────────────────────────────────


class TestEscalate:
    def test_escalate_p1_to_p0_ok(self) -> None:
        sink: list = []
        agg = _agg(sink)
        _opened(agg)
        event = EscalatedEvent(
            incident_id="INC-1",
            from_severity=IncidentSeverity.P1,
            to_severity=IncidentSeverity.P0,
            reason="延迟超 SLO 10 倍",
            occurred_at=_T1,
        )
        inc = agg.escalate(event)
        assert inc.severity is IncidentSeverity.P0
        assert inc.history == (IncidentEventKind.DETECTED, IncidentEventKind.ESCALATED)
        assert sink[-1] is event

    def test_escalate_to_lower_severity_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-1",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P2,  # 降级非法
                    reason="r",
                    occurred_at=_T1,
                )
            )

    def test_escalate_same_level_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-1",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P1,
                    reason="r",
                    occurred_at=_T1,
                )
            )

    def test_escalate_from_mismatch_raises(self) -> None:
        agg = _agg()
        agg.detect(_detected(severity=IncidentSeverity.P2))
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-1",
                    from_severity=IncidentSeverity.P1,  # 声明与当前不符
                    to_severity=IncidentSeverity.P0,
                    reason="r",
                    occurred_at=_T1,
                )
            )

    def test_escalate_terminal_raises(self) -> None:
        agg = _agg()
        _mitigating(agg)
        agg.resolve(ResolvedEvent(incident_id="INC-1", resolution="r", occurred_at=_T1))
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-1",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P0,
                    reason="r",
                    occurred_at=_T1,
                )
            )

    def test_escalate_unknown_raises(self) -> None:
        agg = _agg()
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="ghost",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P0,
                    reason="r",
                    occurred_at=_T1,
                )
            )

    def test_escalate_empty_reason_raises(self) -> None:
        agg = _agg()
        _opened(agg)
        with pytest.raises(OpsIncidentError):
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-1",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P0,
                    reason="",
                    occurred_at=_T1,
                )
            )


# ──────────────────────────────────────────────────────────────────────────────
# 查询（确定性排序）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_list_sorted_by_detected_at_then_id(self) -> None:
        agg = _agg()
        agg.detect(
            DetectedEvent(
                incident_id="INC-2",
                severity=IncidentSeverity.P1,
                title="t",
                source="s",
                occurred_at=_T0,
            )
        )
        agg.detect(
            DetectedEvent(
                incident_id="INC-1",
                severity=IncidentSeverity.P1,
                title="t",
                source="s",
                occurred_at=_T0,
            )
        )
        assert [i.incident_id for i in agg.list_incidents()] == ["INC-1", "INC-2"]

    def test_list_filter_by_status(self) -> None:
        agg = _agg()
        _opened(agg, "INC-1")
        _opened(agg, "INC-2")
        agg.acknowledge("INC-2")
        assert [i.incident_id for i in agg.list_incidents(IncidentStatus.OPEN)] == ["INC-1"]
        assert [i.incident_id for i in agg.list_incidents(IncidentStatus.ACK)] == ["INC-2"]

    def test_list_invalid_status_filter_raises(self) -> None:
        agg = _agg()
        with pytest.raises(OpsIncidentError):
            agg.list_incidents("open")  # type: ignore[arg-type]

    def test_get_unknown_raises(self) -> None:
        agg = _agg()
        with pytest.raises(OpsIncidentError):
            agg.get("ghost")

    def test_determinism_same_inputs_same_output(self) -> None:
        def _run() -> list:
            agg = _agg()
            _opened(agg, "INC-1")
            _opened(agg, "INC-2")
            agg.acknowledge("INC-1")
            agg.escalate(
                EscalatedEvent(
                    incident_id="INC-2",
                    from_severity=IncidentSeverity.P1,
                    to_severity=IncidentSeverity.P0,
                    reason="r",
                    occurred_at=_T1,
                )
            )
            return agg.list_incidents()

        assert _run() == _run()
