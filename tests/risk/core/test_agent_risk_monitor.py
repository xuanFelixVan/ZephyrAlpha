# [BLUEPRINT] MOD-RK-22 | docs/03_modules/MOD-RK-22/ | §test
# [MODULE] tests.risk.core.test_agent_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.agent_risk_monitor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_agent_risk_monitor.py
# [A_test] module_id: MOD-RK-22 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-22 单元测试: AgentRiskMonitor — agent 交易行为风险监控。

覆盖: 下单爆发/拒单率/撤单率/置信度/快照降级/限额逼近六类指标,
小样本地板守卫, 等级映射与 recommended_action, 非法输入 Fail-Closed。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.agent_risk_monitor",
    reason="agent_risk_monitor not importable",
)

from zephyr.risk.core.agent_risk_monitor import (  # noqa: E402
    AgentActivityWindow,
    AgentRiskLevel,
    AgentRiskMonitor,
    AgentRiskThresholds,
    InvalidAgentActivityError,
    evaluate_agent_risk,
)
from zephyr.risk.core.risk_data_pipeline import (  # noqa: E402
    RiskSnapshotInput,
    assemble_risk_snapshot,
)
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402
from zephyr.shared.contracts.position import PositionSnapshot  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402

# ── 夹具 ─────────────────────────────────────────────────────────────

_NOW = datetime(2026, 8, 21, 14, 0, tzinfo=UTC)


def _activity(**overrides) -> AgentActivityWindow:
    base = dict(
        window_start=datetime(2026, 8, 21, 13, 0, tzinfo=UTC),
        window_end=_NOW,
        orders_submitted=20,
        orders_rejected=1,
        orders_cancelled=2,
        decisions_made=20,
        avg_confidence=0.75,
    )
    base.update(overrides)
    return AgentActivityWindow(**base)


def _snapshot(*, degraded: bool = False, top_weight: float = 0.05):
    """经 3.1 纯函数造一个真快照（top_weight 由持仓市值/cash 配比控制）。"""
    mv = Decimal("10000")
    # cash 反解使 weight = mv/(mv+cash) = top_weight
    cash = (mv * (Decimal("1") - Decimal(str(top_weight)))) / Decimal(str(top_weight))
    pos = PositionSnapshot(
        portfolio_id="pf-1",
        as_of_timestamp=_NOW,
        idempotency_key="pos-1",
        cash=cash,
        holdings={"600519.SH": Decimal("100")},
        market_values={"600519.SH": mv},
        total_market_value=mv,
    )
    quote = NormalizedMarketData(
        symbol="600519.SH",
        timestamp=_NOW,
        open=Decimal("100"),
        high=Decimal("100"),
        low=Decimal("100"),
        close=Decimal("100"),
        volume=Decimal("1000"),
        data_source="stub",
        idempotency_key="q-1",
    )
    limits = RiskLimits(
        as_of_date=_NOW,
        idempotency_key="lim-1",
        max_single_position=0.10,
        max_gross_leverage=1.0,
    )
    return assemble_risk_snapshot(
        RiskSnapshotInput(
            position_snapshot=pos,
            quotes={} if degraded else {"600519.SH": quote},
            fills=(),
            limits=None if degraded else limits,
            as_of=_NOW,
        )
    )


# ── 等级与动作映射 ───────────────────────────────────────────────────


class TestLevelMapping:
    def test_normal_when_no_indicators(self):
        report = evaluate_agent_risk(_activity(), _snapshot(), AgentRiskThresholds())
        assert report.level == AgentRiskLevel.NORMAL
        assert report.recommended_action == "none"
        assert report.indicators == ()

    def test_order_burst_critical(self):
        report = evaluate_agent_risk(
            _activity(orders_submitted=101),
            _snapshot(),
            AgentRiskThresholds(max_orders_per_window=100),
        )
        assert report.level == AgentRiskLevel.CRITICAL
        assert report.recommended_action == "suspend_new_orders"
        ids = [i.indicator_id for i in report.indicators]
        assert "order_burst" in ids

    def test_reject_rate_warning(self):
        report = evaluate_agent_risk(
            _activity(orders_submitted=20, orders_rejected=5),
            _snapshot(),
            AgentRiskThresholds(max_reject_rate=0.2),
        )
        assert report.level == AgentRiskLevel.WARNING
        assert report.recommended_action == "throttle"
        ids = [i.indicator_id for i in report.indicators]
        assert "reject_rate" in ids

    def test_reject_rate_critical_over_double(self):
        report = evaluate_agent_risk(
            _activity(orders_submitted=20, orders_rejected=9),
            _snapshot(),
            AgentRiskThresholds(max_reject_rate=0.2),
        )
        crit = [i for i in report.indicators if i.indicator_id == "reject_rate"]
        assert crit and crit[0].severity == "CRITICAL"
        assert report.recommended_action == "suspend_new_orders"

    def test_cancel_rate_indicator(self):
        report = evaluate_agent_risk(
            _activity(orders_submitted=20, orders_cancelled=12),
            _snapshot(),
            AgentRiskThresholds(max_cancel_rate=0.5),
        )
        ids = [i.indicator_id for i in report.indicators]
        assert "cancel_rate" in ids

    def test_low_confidence_warning(self):
        report = evaluate_agent_risk(
            _activity(avg_confidence=0.3),
            _snapshot(),
            AgentRiskThresholds(min_confidence=0.5),
        )
        ids = [i.indicator_id for i in report.indicators]
        assert "low_confidence" in ids
        assert report.level == AgentRiskLevel.WARNING

    def test_degraded_snapshot_warning(self):
        report = evaluate_agent_risk(_activity(), _snapshot(degraded=True), AgentRiskThresholds())
        ids = [i.indicator_id for i in report.indicators]
        assert "snapshot_degraded" in ids
        assert report.level == AgentRiskLevel.WARNING

    def test_limit_proximity_warning(self):
        # weight 0.09 vs limit 0.10 → 90% > warning_ratio 0.8
        report = evaluate_agent_risk(_activity(), _snapshot(top_weight=0.09), AgentRiskThresholds())
        ids = [i.indicator_id for i in report.indicators]
        assert "limit_proximity" in ids

    def test_no_proximity_when_limits_missing(self):
        # degraded 快照（limits=None）不应误报 limit_proximity
        report = evaluate_agent_risk(_activity(), _snapshot(degraded=True), AgentRiskThresholds())
        ids = [i.indicator_id for i in report.indicators]
        assert "limit_proximity" not in ids


# ── 小样本地板守卫 ───────────────────────────────────────────────────


class TestSampleFloor:
    def test_rates_skipped_below_floor(self):
        # submitted=3 < floor 10, 即使 3/3 全拒也不出 reject_rate
        report = evaluate_agent_risk(
            _activity(orders_submitted=3, orders_rejected=3, orders_cancelled=3, decisions_made=3),
            _snapshot(),
            AgentRiskThresholds(min_decisions_for_rates=10),
        )
        ids = [i.indicator_id for i in report.indicators]
        assert "reject_rate" not in ids
        assert "cancel_rate" not in ids

    def test_confidence_none_skipped(self):
        report = evaluate_agent_risk(
            _activity(avg_confidence=None),
            _snapshot(),
            AgentRiskThresholds(min_confidence=0.5),
        )
        ids = [i.indicator_id for i in report.indicators]
        assert "low_confidence" not in ids


# ── 输入校验 Fail-Closed ─────────────────────────────────────────────


class TestInputValidation:
    def test_negative_counts_raise(self):
        with pytest.raises(InvalidAgentActivityError):
            evaluate_agent_risk(_activity(orders_submitted=-1), _snapshot(), AgentRiskThresholds())

    def test_rejected_exceeds_submitted_raises(self):
        with pytest.raises(InvalidAgentActivityError):
            evaluate_agent_risk(
                _activity(orders_submitted=5, orders_rejected=6),
                _snapshot(),
                AgentRiskThresholds(),
            )

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(InvalidAgentActivityError):
            evaluate_agent_risk(_activity(avg_confidence=1.5), _snapshot(), AgentRiskThresholds())

    def test_window_inverted_raises(self):
        with pytest.raises(InvalidAgentActivityError):
            evaluate_agent_risk(
                _activity(
                    window_start=datetime(2026, 8, 21, 15, 0, tzinfo=UTC),
                    window_end=datetime(2026, 8, 21, 14, 0, tzinfo=UTC),
                ),
                _snapshot(),
                AgentRiskThresholds(),
            )


# ── 报告契约 ─────────────────────────────────────────────────────────


class TestReportContract:
    def test_report_carries_snapshot_id(self):
        snap = _snapshot()
        report = evaluate_agent_risk(_activity(), snap, AgentRiskThresholds())
        assert report.snapshot_id == snap.snapshot_id

    def test_report_immutable(self):
        report = evaluate_agent_risk(_activity(), _snapshot(), AgentRiskThresholds())
        with pytest.raises(AttributeError):
            report.level = AgentRiskLevel.CRITICAL  # type: ignore[misc]

    def test_monitor_wrapper_keeps_last_report(self):
        mon = AgentRiskMonitor(thresholds=AgentRiskThresholds())
        assert mon.last_report is None
        report = mon.assess(_activity(), _snapshot())
        assert mon.last_report is report
