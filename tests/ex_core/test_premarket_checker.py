# [BLUEPRINT] MOD-EX-063 | docs/03_modules/_domain_execution_core/premarket_checker/blueprint.md | §test
# [A_test] module_id: MOD-EX-063 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PremarketChecker 单元测试 (MOD-EX-063, D-TRADING-05 盘前检查器 MVP)。

覆盖: 四道关(限额基线/纪律预检/数据完整性/系统就绪)全过→ready / 过期限额
LIMITS_STALE / 限额取值域越界 / 纪律违规 / 数据质量不达标 / 子系统未就绪点名 /
探针异常 PROBE_ERROR(Fail-Closed) / 全量评估不短路 / 报告frozen / 事件订阅幂等 /
未接线收到请求 ready=False。
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, date, datetime

import pytest

pytest.importorskip(
    "zephyr.ex_core.premarket_checker",
    reason="premarket_checker not importable",
)

from zephyr.data.quality_gate import QualityReport  # noqa: E402
from zephyr.ex_core.premarket_checker import (  # noqa: E402
    PremarketChecker,
    PremarketReport,
)
from zephyr.trading.trading_contracts.risk.risk_limits import RiskLimits  # noqa: E402

_TRADING_DATE = date(2026, 8, 25)
_NOW = datetime(2026, 8, 25, 0, 50, tzinfo=UTC)


def _limits(**overrides) -> RiskLimits:
    base = dict(
        as_of_date=datetime(2026, 8, 25, 0, 0, tzinfo=UTC),
        idempotency_key="RL-20260825",
        max_single_position=0.1,
        max_sector_concentration=0.3,
        max_gross_leverage=1.0,
    )
    base.update(overrides)
    return RiskLimits(**base)


def _quality_report(*, passed: bool = True) -> QualityReport:
    return QualityReport(
        symbol="000001.SZ",
        quality_score=0.95 if passed else 0.5,
        passed=passed,
    )


class _Probes:
    def __init__(
        self,
        *,
        limits: RiskLimits | None = None,
        violations: tuple[str, ...] = (),
        quality_passed: bool = True,
        readiness: dict[str, bool] | None = None,
    ) -> None:
        self.limits = limits if limits is not None else _limits()
        self.violations = violations
        self.quality_passed = quality_passed
        self.readiness = readiness if readiness is not None else {"broker_link": True, "market_data": True}
        self.fail_on: set[str] = set()

    def limits_probe(self) -> RiskLimits:
        if "limits" in self.fail_on:
            raise RuntimeError("limits probe boom")
        return self.limits

    def compliance_probe(self) -> tuple[str, ...]:
        if "compliance" in self.fail_on:
            raise RuntimeError("compliance probe boom")
        return self.violations

    def data_quality_probe(self) -> QualityReport:
        if "quality" in self.fail_on:
            raise RuntimeError("quality probe boom")
        return _quality_report(passed=self.quality_passed)

    def readiness_probe(self) -> dict[str, bool]:
        if "readiness" in self.fail_on:
            raise RuntimeError("readiness probe boom")
        return self.readiness


def _checker(probes: _Probes) -> PremarketChecker:
    return PremarketChecker(
        risk_limits_probe=probes.limits_probe,
        compliance_probe=probes.compliance_probe,
        data_quality_probe=probes.data_quality_probe,
        system_readiness_probe=probes.readiness_probe,
        clock=lambda: _NOW,
    )


def _item(report: PremarketReport, check_id: str):
    return next(i for i in report.items if i.check_id == check_id)


# ── 四道关全过 ────────────────────────────────────────────────────────


def test_all_gates_pass_ready() -> None:
    report = _checker(_Probes()).run(_TRADING_DATE)
    assert report.ready is True
    assert report.trading_date == _TRADING_DATE
    assert [i.check_id for i in report.items] == [
        "risk_limits",
        "compliance",
        "data_integrity",
        "system_readiness",
    ]
    assert all(i.passed for i in report.items)
    assert report.evaluated_at == _NOW


# ── 限额基线 ──────────────────────────────────────────────────────────


def test_stale_limits_blocked() -> None:
    stale = _limits(as_of_date=datetime(2026, 8, 24, 0, 0, tzinfo=UTC))
    report = _checker(_Probes(limits=stale)).run(_TRADING_DATE)
    item = _item(report, "risk_limits")
    assert report.ready is False
    assert item.passed is False
    assert item.reason_code == "LIMITS_STALE"


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_single_position", 0.0),
        ("max_single_position", 1.5),
        ("max_sector_concentration", 0.0),
        ("max_sector_concentration", 1.5),
        ("max_gross_leverage", 0.0),
    ],
)
def test_limit_value_range_blocked(field: str, value: float) -> None:
    report = _checker(_Probes(limits=_limits(**{field: value}))).run(_TRADING_DATE)
    item = _item(report, "risk_limits")
    assert report.ready is False
    assert item.passed is False
    assert item.reason_code == "LIMITS_INVALID"


# ── 纪律预检 ──────────────────────────────────────────────────────────


def test_compliance_violations_blocked() -> None:
    report = _checker(_Probes(violations=("程序化交易报备缺失",))).run(_TRADING_DATE)
    item = _item(report, "compliance")
    assert report.ready is False
    assert item.passed is False
    assert item.reason_code == "COMPLIANCE_VIOLATION"
    assert "程序化交易报备缺失" in item.message


# ── 数据完整性 ────────────────────────────────────────────────────────


def test_data_quality_failed_blocked() -> None:
    report = _checker(_Probes(quality_passed=False)).run(_TRADING_DATE)
    item = _item(report, "data_integrity")
    assert report.ready is False
    assert item.passed is False
    assert item.reason_code == "DATA_QUALITY_FAILED"


# ── 系统就绪 ──────────────────────────────────────────────────────────


def test_subsystem_not_ready_named() -> None:
    readiness = {"broker_link": False, "market_data": True, "risk_engine": False}
    report = _checker(_Probes(readiness=readiness)).run(_TRADING_DATE)
    item = _item(report, "system_readiness")
    assert report.ready is False
    assert item.passed is False
    assert item.reason_code == "SUBSYSTEM_NOT_READY"
    assert "broker_link" in item.message and "risk_engine" in item.message
    assert "market_data" not in item.message


# ── 探针异常 = Fail-Closed；全量评估不短路 ────────────────────────────


@pytest.mark.parametrize("probe", ["limits", "compliance", "quality", "readiness"])
def test_probe_exception_fail_closed(probe: str) -> None:
    probes = _Probes()
    probes.fail_on.add(probe)
    report = _checker(probes).run(_TRADING_DATE)
    assert report.ready is False
    assert len(report.items) == 4  # 全量评估不短路
    failed = [i for i in report.items if not i.passed]
    assert len(failed) == 1 and failed[0].reason_code == "PROBE_ERROR"


# ── 报告不可变 ────────────────────────────────────────────────────────


def test_report_frozen() -> None:
    report = _checker(_Probes()).run(_TRADING_DATE)
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.ready = False  # type: ignore[misc]


# ── 事件总线接线（boot_hooks 消费方模式）──────────────────────────────


def test_subscribe_eventbus_idempotent() -> None:
    import zephyr.ex_core.premarket_checker as mod
    from zephyr.shared.event_bus import bus

    captured: list = []
    bus.subscribe("premarket.check.completed", captured.append)
    mod.register_checker(_checker(_Probes()))
    try:
        mod.subscribe_eventbus()
        mod.subscribe_eventbus()  # 幂等：重复注册不重复生效
        assert "premarket.check.requested" in bus.subscribed_topics

        bus.emit("premarket.check.requested", {"trading_date": "2026-08-25", "marker": "wired"})
        mine = [e for e in captured if e.payload.get("marker") == "wired"]
        assert len(mine) == 1, "幂等：一次请求只应产一条 completed"
        assert mine[0].payload["ready"] is True
    finally:
        mod.register_checker(None)


def test_unwired_checker_emits_not_ready() -> None:
    import zephyr.ex_core.premarket_checker as mod
    from zephyr.shared.event_bus import bus

    captured: list = []
    bus.subscribe("premarket.check.completed", captured.append)
    mod.register_checker(None)
    mod.subscribe_eventbus()
    bus.emit("premarket.check.requested", {"trading_date": "2026-08-25", "marker": "unwired"})
    mine = [e for e in captured if e.payload.get("marker") == "unwired"]
    assert mine, "未接线也应发布 completed（Fail-Closed ready=False）"
    assert mine[-1].payload["ready"] is False
