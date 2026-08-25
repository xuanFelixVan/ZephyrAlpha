# [BLUEPRINT] MOD-GOV-050 | docs/03_modules/_domain_gov_enforcement/threshold_split_detector/blueprint.md | §test
# [A_test] module_id: MOD-GOV-050 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ThresholdSplitDetector 单元测试 (MOD-GOV-050, 阈值拆分检测器 MVP)。

覆盖: 30分钟窗/当日窗两档累计≥阈值80%判拆分 / 阻断后续单不计入窗口 /
提请审批幂等(同标的同方向同日一次) / 窗内含单笔≥阈值→CLEAN / 累计<80%→CLEAN /
端口异常隔离但阻断生效(Fail-Closed) / 非法意图校验 / 时钟注入窗口边界 / 配置校验 /
结果frozen不可变。
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.gov_enforcement.rule_enforcement.threshold_split_detector",
    reason="threshold_split_detector not importable",
)

from zephyr.gov_enforcement.rule_enforcement.threshold_split_detector import (  # noqa: E402
    InvalidOrderIntentError,
    InvalidThresholdSplitConfigError,
    OrderIntent,
    OrderSide,
    SplitDetectionResult,
    SplitVerdict,
    ThresholdPair,
    ThresholdSplitConfig,
    ThresholdSplitDetector,
)

_T0 = datetime(2026, 8, 25, 1, 0, tzinfo=UTC)
_THR = ThresholdPair(quantity=100, amount=Decimal("100000"))


def _intent(
    idx: int,
    *,
    intent_id: str | None = None,
    strategy_id: str = "STRAT-001",
    symbol: str = "000001.SZ",
    side: OrderSide = OrderSide.BUY,
    quantity: int = 30,
    amount: Decimal = Decimal("30000"),
) -> OrderIntent:
    return OrderIntent(
        intent_id=intent_id if intent_id is not None else f"INT-{idx:03d}",
        strategy_id=strategy_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        amount=amount,
    )


class _Clock:
    def __init__(self, start: datetime = _T0) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


class _Gateway:
    def __init__(self, *, boom: bool = False) -> None:
        self.submitted: list = []
        self._boom = boom

    def submit(self, request) -> str:
        if self._boom:
            raise RuntimeError("gateway boom")
        self.submitted.append(request)
        return request.request_id


class _Sinks:
    def __init__(self, *, boom: bool = False) -> None:
        self.alerts: list[tuple[str, dict]] = []
        self.audits: list[tuple[str, dict]] = []
        self._boom = boom

    def alert(self, level: str, payload: dict) -> None:
        if self._boom:
            raise RuntimeError("alert boom")
        self.alerts.append((level, payload))

    def audit(self, event: str, payload: dict) -> None:
        if self._boom:
            raise RuntimeError("audit boom")
        self.audits.append((event, payload))


def _detector(
    clock: _Clock,
    gateway: _Gateway | None = None,
    sinks: _Sinks | None = None,
    config: ThresholdSplitConfig | None = None,
) -> ThresholdSplitDetector:
    g = gateway if gateway is not None else _Gateway()
    s = sinks if sinks is not None else _Sinks()
    return ThresholdSplitDetector(
        config=config or ThresholdSplitConfig(default_thresholds=_THR),
        approval_gateway=g,
        alert_sink=s.alert,
        audit_sink=s.audit,
        clock=clock,
    )


# ── 30 分钟窗触发拆分 ─────────────────────────────────────────────────


def test_split_suspected_30m_window() -> None:
    clock, gateway, sinks = _Clock(), _Gateway(), _Sinks()
    det = _detector(clock, gateway, sinks)
    det.register_intent(_intent(1))
    clock.advance(minutes=5)
    det.register_intent(_intent(2))
    clock.advance(minutes=5)
    result = det.register_intent(_intent(3))  # 累计 90 ≥ 100×0.8

    assert result.verdict is SplitVerdict.SPLIT_SUSPECTED
    assert result.trigger_window == "30m"
    assert result.qty_30m == 90
    assert result.amount_30m == Decimal("90000")
    assert result.escalation_request_id == "SPLIT-000001.SZ-buy-2026-08-25"
    # 提请审批一次 + 审计 + CRITICAL 告警
    assert len(gateway.submitted) == 1
    req = gateway.submitted[0]
    assert req.action == "threshold_split_escalation"
    assert req.context["symbol"] == "000001.SZ"
    assert any(ev == "SPLIT_SUSPECTED" for ev, _ in sinks.audits)
    assert any(level == "CRITICAL" for level, _ in sinks.alerts)


# ── 当日窗触发（30 分钟窗已滑出）───────────────────────────────────────


def test_split_suspected_day_window() -> None:
    clock = _Clock()
    det = _detector(clock)
    det.register_intent(_intent(1))
    clock.advance(minutes=40)  # 滑出 30 分钟窗
    det.register_intent(_intent(2))
    clock.advance(minutes=40)
    result = det.register_intent(_intent(3))  # 当日累计 90，30m 窗仅 30

    assert result.verdict is SplitVerdict.SPLIT_SUSPECTED
    assert result.trigger_window == "day"
    assert result.qty_day == 90
    assert result.qty_30m == 30


# ── 窗内含单笔≥阈值 → 非拆分（走单笔审批视角）─────────────────────────


def test_single_above_threshold_clean() -> None:
    clock = _Clock()
    det = _detector(clock)
    det.register_intent(_intent(1, quantity=150, amount=Decimal("150000")))
    clock.advance(minutes=5)
    result = det.register_intent(_intent(2))
    assert result.verdict is SplitVerdict.CLEAN


# ── 累计不足 80% → CLEAN ─────────────────────────────────────────────


def test_below_80pct_clean() -> None:
    clock = _Clock()
    det = _detector(clock)
    det.register_intent(_intent(1))
    clock.advance(minutes=5)
    result = det.register_intent(_intent(2))  # 累计 60 < 80
    assert result.verdict is SplitVerdict.CLEAN
    assert result.escalation_request_id is None


def test_single_85pct_order_clean() -> None:
    """仅一笔（≥80% 但 <100%）不构成拆分——拆分须 ≥2 笔。"""
    det = _detector(_Clock())
    result = det.register_intent(_intent(1, quantity=85, amount=Decimal("85000")))
    assert result.verdict is SplitVerdict.CLEAN


# ── 阻断后续单：BLOCKED 且不计入窗口；提请审批幂等 ─────────────────────


def test_blocked_after_suspicion() -> None:
    clock, gateway = _Clock(), _Gateway()
    det = _detector(clock, gateway)
    det.register_intent(_intent(1))
    det.register_intent(_intent(2))
    suspected = det.register_intent(_intent(3))
    assert suspected.verdict is SplitVerdict.SPLIT_SUSPECTED
    assert det.is_blocked("000001.SZ", OrderSide.BUY) is True

    clock.advance(minutes=5)
    blocked = det.register_intent(_intent(4))
    assert blocked.verdict is SplitVerdict.BLOCKED
    assert blocked.qty_day == 90  # 阻断单不计入窗口（仍为前 3 笔累计）
    assert len(gateway.submitted) == 1  # 提请审批幂等

    # 反方向不受影响
    other = det.register_intent(_intent(5, side=OrderSide.SELL))
    assert other.verdict is SplitVerdict.CLEAN
    assert det.is_blocked("000001.SZ", OrderSide.SELL) is False


# ── 端口异常隔离：审批/告警/审计全炸，阻断仍生效（Fail-Closed）─────────


def test_port_failure_isolated_but_blocked() -> None:
    clock = _Clock()
    det = _detector(clock, _Gateway(boom=True), _Sinks(boom=True))
    det.register_intent(_intent(1))
    det.register_intent(_intent(2))
    result = det.register_intent(_intent(3))
    assert result.verdict is SplitVerdict.SPLIT_SUSPECTED
    assert result.escalation_request_id is None  # 提请失败如实留空
    assert det.is_blocked("000001.SZ", OrderSide.BUY) is True


# ── 非法意图校验 ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "field,value",
    [
        ("intent_id", ""),
        ("strategy_id", ""),
        ("symbol", ""),
        ("quantity", 0),
        ("quantity", -5),
        ("amount", Decimal("-1")),
    ],
)
def test_invalid_intent_raises(field: str, value) -> None:
    det = _detector(_Clock())
    kwargs = {field: value}
    with pytest.raises(InvalidOrderIntentError):
        det.register_intent(_intent(1, **kwargs))


# ── 配置校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kwargs",
    [
        {"alert_ratio": 0.0},
        {"alert_ratio": 1.5},
        {"window_minutes": 0},
    ],
)
def test_invalid_config_raises(kwargs: dict) -> None:
    with pytest.raises(InvalidThresholdSplitConfigError):
        ThresholdSplitDetector(config=ThresholdSplitConfig(default_thresholds=_THR, **kwargs))


def test_invalid_threshold_pair_raises() -> None:
    with pytest.raises(InvalidThresholdSplitConfigError):
        ThresholdSplitDetector(
            config=ThresholdSplitConfig(
                default_thresholds=ThresholdPair(quantity=0, amount=Decimal("100000"))
            )
        )


# ── symbol 覆盖阈值 ───────────────────────────────────────────────────


def test_symbol_override_thresholds() -> None:
    config = ThresholdSplitConfig(
        default_thresholds=_THR,
        symbol_overrides={"600000.SH": ThresholdPair(quantity=50, amount=Decimal("50000"))},
    )
    clock = _Clock()
    det = _detector(clock, config=config)
    det.register_intent(_intent(1, symbol="600000.SH"))
    result = det.register_intent(_intent(2, symbol="600000.SH"))  # 累计 60 ≥ 50×0.8
    assert result.verdict is SplitVerdict.SPLIT_SUSPECTED
    assert result.threshold_quantity == 50


# ── 结果不可变 ────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    det = _detector(_Clock())
    result = det.register_intent(_intent(1))
    assert isinstance(result, SplitDetectionResult)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.verdict = SplitVerdict.BLOCKED  # type: ignore[misc]
