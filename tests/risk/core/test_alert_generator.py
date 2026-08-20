# [BLUEPRINT] MOD-RK-06 | docs/03_modules/_domain_risk/alert_generator/blueprint.md | §test
# [MODULE] tests.risk.core.test_alert_generator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.alert_generator; zephyr.risk.risk_manager_base
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_alert_generator.py
# [A_test] module_id: MOD-RK-06 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-06 Alert Generator 单元测试.

覆盖: 三级分类(RED kill_switch/HALT, ORANGE, YELLOW)/混合场景/
去重(窗口内抑制/窗口外放行)/路由(级别→通道映射)/通道失败best-effort/
全流程process/幂等键唯一性.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

pytest.importorskip("zephyr.risk.core.alert_generator", reason="alert_generator not importable")

from zephyr.risk.core.alert_generator import (  # noqa: E402
    Alert,
    AlertGenerator,
    AlertLevel,
    EmailChannel,
    LogChannel,
    WeChatChannel,
)
from zephyr.risk.risk_manager_base import RiskCheckResult, RiskReport  # noqa: E402

NOW = datetime.now(UTC)


# ── Mock 数据工厂 ─────────────────────────────────────────────────────


def _check(
    check_id: str = "chk-1",
    rule_name: str = "position_limit",
    passed: bool = False,
    severity: str = "info",
    message: str = "",
) -> RiskCheckResult:
    return RiskCheckResult(
        check_id=check_id,
        rule_name=rule_name,
        passed=passed,
        limit_value=Decimal("0.10"),
        actual_value=Decimal("0.20"),
        message=message,
        severity=severity,
    )


def _report(
    checks: list[RiskCheckResult] | None = None,
    overall_pass: bool = True,
    active_alerts: list[str] | None = None,
    kill_switch: bool = False,
    portfolio_id: str = "test-portfolio",
) -> RiskReport:
    return RiskReport(
        as_of_timestamp=NOW,
        portfolio_id=portfolio_id,
        checks=checks or [],
        overall_pass=overall_pass,
        active_alerts=active_alerts or [],
        kill_switch_active=kill_switch,
    )


# ── Mock 数据场景 ─────────────────────────────────────────────────────

#: Scenario 1: RED via kill switch
MOCK_RED_KILL_SWITCH = _report(kill_switch=True, overall_pass=False)

#: Scenario 2: RED via HALT violation
MOCK_RED_HALT = _report(
    checks=[_check(severity="HALT", message="position limit breached")],
    overall_pass=False,
)

#: Scenario 3: ORANGE via non-HALT failure
MOCK_ORANGE = _report(
    checks=[_check(rule_name="drawdown", severity="WARNING", message="drawdown approaching limit")],
    overall_pass=True,
)

#: Scenario 4: YELLOW via active_alerts
MOCK_YELLOW = _report(
    active_alerts=["concentration: HHI=0.15 above threshold"],
    overall_pass=True,
)

#: Scenario 5: Clean — no alerts
MOCK_CLEAN = _report()

#: Scenario 6: Mixed — HALT + non-HALT + active_alerts
MOCK_MIXED = _report(
    checks=[
        _check(check_id="c1", rule_name="position_limit", severity="HALT", message="position limit breached"),
        _check(check_id="c2", rule_name="drawdown", severity="WARNING", message="drawdown approaching limit"),
    ],
    active_alerts=["volatility: VIX spike detected"],
    overall_pass=False,
)

#: Scenario 7: Multiple non-HALT failures (different sources)
MOCK_MULTI_ORANGE = _report(
    checks=[
        _check(check_id="c1", rule_name="drawdown", severity="WARNING"),
        _check(check_id="c2", rule_name="leverage", severity="WARNING"),
    ],
    overall_pass=True,
)

#: Scenario 8: Same source HALT + non-HALT (should only produce RED)
MOCK_SAME_SOURCE = _report(
    checks=[
        _check(check_id="c1", rule_name="position_limit", severity="HALT"),
        _check(check_id="c2", rule_name="position_limit", severity="WARNING"),
    ],
    overall_pass=False,
)


# ── AlertLevel / Alert 数据模型测试 ────────────────────────────────────


class TestAlertLevel:
    def test_three_levels_exist(self):
        assert AlertLevel.YELLOW
        assert AlertLevel.ORANGE
        assert AlertLevel.RED

    def test_level_values(self):
        assert AlertLevel.YELLOW.value == "yellow"
        assert AlertLevel.ORANGE.value == "orange"
        assert AlertLevel.RED.value == "red"


class TestAlertDataclass:
    def test_creation(self):
        a = Alert(
            level=AlertLevel.RED,
            source="kill_switch",
            message="test",
            timestamp=NOW,
            idempotency_key="key-1",
        )
        assert a.level == AlertLevel.RED
        assert a.source == "kill_switch"

    def test_frozen_immutability(self):
        a = Alert(
            level=AlertLevel.YELLOW,
            source="s",
            message="m",
            timestamp=NOW,
            idempotency_key="k",
        )
        with pytest.raises(AttributeError):
            a.level = AlertLevel.RED


# ── 分类测试 ──────────────────────────────────────────────────────────


class TestClassify:
    def test_red_via_kill_switch(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_RED_KILL_SWITCH)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.RED
        assert alerts[0].source == "kill_switch"

    def test_red_via_halt_violation(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_RED_HALT)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.RED
        assert alerts[0].source == "position_limit"

    def test_orange_via_non_halt_failure(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_ORANGE)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.ORANGE
        assert alerts[0].source == "drawdown"

    def test_yellow_via_active_alerts(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_YELLOW)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.YELLOW
        assert alerts[0].source == "concentration"

    def test_clean_report_no_alerts(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_CLEAN)
        assert len(alerts) == 0

    def test_mixed_scenario(self):
        """HALT→RED + non-HALT→ORANGE + active_alert→YELLOW = 3 alerts."""
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_MIXED)
        assert len(alerts) == 3
        levels = {a.level for a in alerts}
        assert levels == {AlertLevel.RED, AlertLevel.ORANGE, AlertLevel.YELLOW}

    def test_same_source_halt_suppresses_orange(self):
        """Same source with both HALT and WARNING → only RED."""
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_SAME_SOURCE)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.RED
        assert alerts[0].source == "position_limit"

    def test_multiple_orange_different_sources(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_MULTI_ORANGE)
        assert len(alerts) == 2
        assert all(a.level == AlertLevel.ORANGE for a in alerts)
        sources = {a.source for a in alerts}
        assert sources == {"drawdown", "leverage"}

    def test_idempotency_key_unique(self):
        gen = AlertGenerator()
        alerts = gen.classify(MOCK_MIXED)
        keys = {a.idempotency_key for a in alerts}
        assert len(keys) == len(alerts)  # all unique


# ── 去重测试 ──────────────────────────────────────────────────────────


class TestDeduplicate:
    def test_duplicate_suppressed_within_window(self):
        """Same source+message within window → suppressed."""
        gen = AlertGenerator(dedup_window=timedelta(minutes=5))
        alert = Alert(
            level=AlertLevel.RED,
            source="kill_switch",
            message="same message",
            timestamp=NOW,
            idempotency_key="k1",
        )
        # First pass: allowed
        result1 = gen.deduplicate([alert])
        assert len(result1) == 1
        # Second pass (same key, within window): suppressed
        alert2 = Alert(
            level=AlertLevel.RED,
            source="kill_switch",
            message="same message",
            timestamp=NOW + timedelta(seconds=30),
            idempotency_key="k2",
        )
        result2 = gen.deduplicate([alert2])
        assert len(result2) == 0

    def test_different_message_not_suppressed(self):
        gen = AlertGenerator(dedup_window=timedelta(minutes=5))
        a1 = Alert(AlertLevel.ORANGE, "drawdown", "msg A", NOW, "k1")
        a2 = Alert(AlertLevel.ORANGE, "drawdown", "msg B", NOW, "k2")
        result = gen.deduplicate([a1, a2])
        assert len(result) == 2

    def test_different_source_not_suppressed(self):
        gen = AlertGenerator(dedup_window=timedelta(minutes=5))
        a1 = Alert(AlertLevel.ORANGE, "drawdown", "same msg", NOW, "k1")
        a2 = Alert(AlertLevel.ORANGE, "leverage", "same msg", NOW, "k2")
        result = gen.deduplicate([a1, a2])
        assert len(result) == 2

    def test_window_expired_allows_resend(self):
        """Same source+message after window expires → allowed."""
        gen = AlertGenerator(dedup_window=timedelta(minutes=5))
        a1 = Alert(AlertLevel.RED, "kill_switch", "msg", NOW, "k1")
        gen.deduplicate([a1])
        # After window expires
        a2 = Alert(
            AlertLevel.RED,
            "kill_switch",
            "msg",
            NOW + timedelta(minutes=6),
            "k2",
        )
        result = gen.deduplicate([a2])
        assert len(result) == 1

    def test_empty_input(self):
        gen = AlertGenerator()
        assert gen.deduplicate([]) == []


# ── 路由测试 ──────────────────────────────────────────────────────────


class TestRoute:
    def test_red_routes_to_all_channels(self):
        dispatched: list[str] = []
        channels = {
            "log": _RecordingChannel(dispatched, "log"),
            "email": _RecordingChannel(dispatched, "email"),
            "wechat": _RecordingChannel(dispatched, "wechat"),
        }
        gen = AlertGenerator(channels=channels)
        alert = Alert(AlertLevel.RED, "kill_switch", "msg", NOW, "k1")
        gen.route(alert)
        assert set(dispatched) == {"log", "email", "wechat"}

    def test_orange_routes_to_log_and_email(self):
        dispatched: list[str] = []
        channels = {
            "log": _RecordingChannel(dispatched, "log"),
            "email": _RecordingChannel(dispatched, "email"),
            "wechat": _RecordingChannel(dispatched, "wechat"),
        }
        gen = AlertGenerator(channels=channels)
        alert = Alert(AlertLevel.ORANGE, "drawdown", "msg", NOW, "k1")
        gen.route(alert)
        assert set(dispatched) == {"log", "email"}

    def test_yellow_routes_to_log_only(self):
        dispatched: list[str] = []
        channels = {
            "log": _RecordingChannel(dispatched, "log"),
            "email": _RecordingChannel(dispatched, "email"),
            "wechat": _RecordingChannel(dispatched, "wechat"),
        }
        gen = AlertGenerator(channels=channels)
        alert = Alert(AlertLevel.YELLOW, "concentration", "msg", NOW, "k1")
        gen.route(alert)
        assert set(dispatched) == {"log"}

    def test_channel_failure_does_not_block(self):
        """Channel raising exception → logged but other channels still dispatched."""
        dispatched: list[str] = []
        channels = {
            "log": _RecordingChannel(dispatched, "log"),
            "email": _FailingChannel(),
            "wechat": _RecordingChannel(dispatched, "wechat"),
        }
        gen = AlertGenerator(channels=channels)
        alert = Alert(AlertLevel.RED, "kill_switch", "msg", NOW, "k1")
        gen.route(alert)  # should not raise
        assert "log" in dispatched
        assert "wechat" in dispatched

    def test_default_channels_no_error(self):
        """Default channels (email/wechat no-op) should not raise."""
        gen = AlertGenerator()
        alert = Alert(AlertLevel.RED, "kill_switch", "msg", NOW, "k1")
        gen.route(alert)  # should not raise


# ── 全流程测试 ────────────────────────────────────────────────────────


class TestProcess:
    def test_full_pipeline_clean_report(self):
        gen = AlertGenerator()
        alerts = gen.process(MOCK_CLEAN)
        assert len(alerts) == 0

    def test_full_pipeline_red(self):
        gen = AlertGenerator()
        alerts = gen.process(MOCK_RED_KILL_SWITCH)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.RED

    def test_full_pipeline_mixed(self):
        gen = AlertGenerator()
        alerts = gen.process(MOCK_MIXED)
        assert len(alerts) == 3

    def test_full_pipeline_dedup_on_repeat(self):
        """Same report processed twice → second time suppressed by dedup."""
        gen = AlertGenerator(dedup_window=timedelta(hours=1))
        alerts1 = gen.process(MOCK_ORANGE)
        assert len(alerts1) == 1
        alerts2 = gen.process(MOCK_ORANGE)
        assert len(alerts2) == 0  # suppressed


# ── 辅助 Mock 通道 ────────────────────────────────────────────────────


class _RecordingChannel:
    """记录派发的通道（测试用）。"""

    def __init__(self, record: list[str], name: str):
        self._record = record
        self._name = name

    def send(self, alert: Alert) -> bool:
        self._record.append(self._name)
        return True


class _FailingChannel:
    """总是抛异常的通道（测试 best-effort 不阻断）。"""

    def send(self, alert: Alert) -> bool:
        raise RuntimeError("channel unavailable")
