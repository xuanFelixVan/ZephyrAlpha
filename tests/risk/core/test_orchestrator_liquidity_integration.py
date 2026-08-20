# [BLUEPRINT] MOD-RK-08 | docs/03_modules/_domain_risk/liquidity_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_orchestrator_liquidity_integration
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_risk_manager_orchestrator; zephyr.risk.core.liquidity_monitor; zephyr.risk.core.alert_generator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_orchestrator_liquidity_integration.py
# [A_test] module_id: MOD-RK-08 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G2-S6 集成测试: 流动性监控 → 编排器 → 告警管道（G1↔G2 端到端）.

覆盖: 向后兼容(无liquidity_monitor)/流动性正常(无告警)/流动性恶化(RED告警)/
best-effort异常不阻断/全流程(preliminary→liquidity→aggregate→alerts).
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

pytest.importorskip(
    "zephyr.risk.implementations.default_risk_manager_orchestrator",
    reason="orchestrator not importable",
)

from zephyr.risk.core.alert_generator import AlertGenerator, AlertLevel  # noqa: E402
from zephyr.risk.core.liquidity_monitor import LiquidityMonitor  # noqa: E402
from zephyr.risk.implementations.default_risk_manager_orchestrator import (  # noqa: E402
    DefaultRiskManagerOrchestrator,
)

# ── Mock 数据 ─────────────────────────────────────────────────────────


def _make_ohlcv(closes: list[float], volumes: list[float]) -> pd.DataFrame:
    n = len(closes)
    dates = pd.date_range("2026-07-01", periods=n, freq="B")
    return pd.DataFrame({"close": closes, "volume": volumes}, index=dates)


#: 流动性正常: 低 Amihud + 正常成交量
MOCK_LIQUID = _make_ohlcv(
    closes=[10.0 + i * 0.01 for i in range(20)],
    volumes=[1e8] * 20,
)

#: 流动性恶化: 高 Amihud（小成交额 + 大价格波动）
MOCK_ILLIQUID = _make_ohlcv(
    closes=[
        10.0,
        11.0,
        9.5,
        10.5,
        9.0,
        11.5,
        9.8,
        10.8,
        9.2,
        11.0,
        10.0,
        11.0,
        9.5,
        10.5,
        9.0,
        11.5,
        9.8,
        10.8,
        9.2,
        11.0,
    ],
    volumes=[1e4] * 20,
)

#: 成交量萎缩: 最后一日成交额骤降
MOCK_SHRINKAGE = _make_ohlcv(
    closes=[10.0 + i * 0.01 for i in range(20)],
    volumes=[1e8] * 19 + [1e7],
)


# ── 向后兼容测试 ──────────────────────────────────────────────────────


class TestBackwardCompatibility:
    """无 liquidity_monitor 时，编排器行为与修改前一致。"""

    def test_no_liquidity_monitor_returns_none(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        result = orch.check_liquidity("600000.SH", MOCK_LIQUID)
        assert result is None

    def test_no_liquidity_monitor_no_extra_checks(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        orch.check_liquidity("600000.SH", MOCK_LIQUID)
        report = orch.aggregate_report()
        assert len(report.checks) == 0


# ── 流动性正常测试 ────────────────────────────────────────────────────


class TestLiquidStock:
    """流动性正常时，不触发告警。"""

    def test_liquid_stock_no_alerts(self):
        gen = AlertGenerator()
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            liquidity_monitor=mon,
        )

        metrics = orch.check_liquidity("600000.SH", MOCK_LIQUID)
        assert metrics is not None
        assert metrics.is_illiquid is False

        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_liquid_stock_check_result_is_pass(self):
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            liquidity_monitor=mon,
        )

        orch.check_liquidity("600000.SH", MOCK_LIQUID)
        report = orch.aggregate_report()

        # 应有 1 个 check，且 passed=True
        assert len(report.checks) == 1
        assert report.checks[0].passed is True
        assert report.checks[0].severity == "info"


# ── 流动性恶化测试 ────────────────────────────────────────────────────


class TestIlliquidStock:
    """流动性恶化时，触发 RED 告警。"""

    def test_illiquid_stock_triggers_red_alert(self):
        """高 Amihud → is_illiquid=True → HALT → RED 告警"""
        gen = AlertGenerator()
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            liquidity_monitor=mon,
        )

        metrics = orch.check_liquidity("600001.SZ", MOCK_ILLIQUID)
        assert metrics is not None
        assert metrics.is_illiquid is True

        report = orch.aggregate_report()
        assert report.overall_pass is False

        alerts = orch.last_alerts
        assert len(alerts) > 0
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) > 0
        assert any(a.source == "liquidity_monitor" for a in red_alerts)

    def test_shrinkage_triggers_alert(self):
        """成交量萎缩 → is_illiquid=True → 告警"""
        gen = AlertGenerator()
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            liquidity_monitor=mon,
        )

        metrics = orch.check_liquidity("600002.SH", MOCK_SHRINKAGE)
        assert metrics is not None
        assert metrics.is_illiquid is True

        report = orch.aggregate_report()
        alerts = orch.last_alerts
        assert len(alerts) > 0

    def test_illiquid_check_result_is_halt(self):
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            liquidity_monitor=mon,
        )

        orch.check_liquidity("600001.SZ", MOCK_ILLIQUID)
        report = orch.aggregate_report()

        assert len(report.checks) == 1
        assert report.checks[0].passed is False
        assert report.checks[0].severity == "HALT"


# ── Best-effort 测试 ──────────────────────────────────────────────────


class TestBestEffort:
    """流动性检查异常不阻断编排器。"""

    def test_invalid_data_returns_none(self):
        """无效数据（缺列）→ best-effort 返回 None，不崩溃"""
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            liquidity_monitor=mon,
        )

        bad_df = pd.DataFrame({"close": [10.0]})  # 缺 volume
        result = orch.check_liquidity("X", bad_df)
        assert result is None

        report = orch.aggregate_report()
        assert report is not None  # 编排器未崩溃


# ── 全流程测试 ────────────────────────────────────────────────────────


class TestFullPipeline:
    """完整流程: 事前检查 → 流动性检查 → 汇总报告 → 告警派发。"""

    def test_full_pipeline_with_illiquid_alert(self):
        gen = AlertGenerator()
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            liquidity_monitor=mon,
        )

        # 1. 事前检查（模拟通过）
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik-test",
            max_single_position=0.10,
            max_gross_leverage=1.5,
        )

        class _MockOrder:
            symbol = "600000.SH"
            quantity = 0.05

        orch.pre_trade_check(_MockOrder(), limits, [])
        assert orch.aggregate_report().overall_pass is True

        # 2. 流动性检查（恶化）
        metrics = orch.check_liquidity("600000.SH", MOCK_ILLIQUID)
        assert metrics.is_illiquid is True

        # 3. 汇总报告 → 自动派发 RED 告警
        report = orch.aggregate_report()
        assert report.overall_pass is False

        alerts = orch.last_alerts
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) > 0
        assert any(a.source == "liquidity_monitor" for a in red_alerts)

    def test_full_pipeline_clean_then_illiquid(self):
        """先检查流动性正常的标的，再检查恶化的标的"""
        gen = AlertGenerator()
        mon = LiquidityMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            liquidity_monitor=mon,
        )

        # 正常标的
        m1 = orch.check_liquidity("A", MOCK_LIQUID)
        assert m1.is_illiquid is False

        # 恶化标的
        m2 = orch.check_liquidity("B", MOCK_ILLIQUID)
        assert m2.is_illiquid is True

        report = orch.aggregate_report()
        assert report.overall_pass is False  # B 恶化了

        alerts = orch.last_alerts
        # 应有 B 的 RED 告警
        assert any(a.level == AlertLevel.RED and "liquidity" in a.source for a in alerts)
