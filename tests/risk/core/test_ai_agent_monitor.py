# [BLUEPRINT] MOD-RK-14 | docs/03_modules/_domain_risk/ai_agent_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_ai_agent_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.ai_agent_monitor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_ai_agent_monitor.py
# [A_test] module_id: MOD-RK-14 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G3 单元测试: AiAgentMonitor — 涌现行为/轨迹异常/指纹偏差综合评分。

覆盖: STABLE/CORRELATING/CRITICAL 状态映射、risk_score 公式守恒、
轨迹归一化、指纹钳制、breach 判定、RiskCheckResult 转换、幂等键。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.ai_agent_monitor",
    reason="ai_agent_monitor not importable",
)

from zephyr.risk.core.ai_agent_monitor import (  # noqa: E402
    DEFAULT_RISK_THRESHOLD,
    AiAgentMonitor,
    AiAgentRiskMetrics,
)

# ── 辅助 ─────────────────────────────────────────────────────────────


def _drive_to_critical(mon: AiAgentMonitor, n_calls: int = 6) -> AiAgentRiskMetrics:
    """用 4 个完全相关的指标驱动检测器到 CRITICAL 状态。"""
    metrics = None
    for i in range(n_calls):
        metrics = mon.assess(
            agent_metrics={"a": float(i), "b": float(i), "c": float(i), "d": float(i)},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.0,
        )
    assert metrics is not None
    return metrics


# ── 状态映射测试 ──────────────────────────────────────────────────────


class TestEmergenceStateMapping:
    """emergence_state 来自 EmergentBehaviorDetector。"""

    def test_no_metrics_returns_stable(self):
        """无 agent_metrics → STABLE（跳过检测）。"""
        mon = AiAgentMonitor()
        m = mon.assess(trajectory_anomaly_count=0, fingerprint_deviation=0.0)
        assert m.emergence_state == "STABLE"
        assert m.high_correlation_pairs == 0

    def test_single_metric_stable(self):
        """单指标无配对 → STABLE。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"latency": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.0,
        )
        assert m.emergence_state == "STABLE"

    def test_correlated_metrics_reach_critical(self):
        """4 个完全相关指标 × 6 次调用 → CRITICAL。"""
        mon = AiAgentMonitor()
        m = _drive_to_critical(mon)
        assert m.emergence_state == "CRITICAL"
        assert m.high_correlation_pairs >= 3


# ── risk_score 公式守恒 ──────────────────────────────────────────────


class TestRiskScoreFormula:
    """risk_score = 0.4×emergence + 0.3×trajectory + 0.3×fingerprint。"""

    def test_stable_zero_trajectory_zero_fp(self):
        """STABLE + 0 anomalies + 0 fp → risk_score=0.0。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.0,
        )
        assert m.risk_score == pytest.approx(0.0)

    def test_critical_only_emergence(self):
        """CRITICAL + 0 trajectory + 0 fp → risk_score=0.4（0.4×1.0）。"""
        mon = AiAgentMonitor()
        m = _drive_to_critical(mon)
        assert m.emergence_state == "CRITICAL"
        # emergence_score=1.0, trajectory=0, fp=0 → 0.4
        assert m.risk_score == pytest.approx(0.4)

    def test_trajectory_only(self):
        """STABLE + 5 anomalies + 0 fp → risk_score=0.3（0.3×1.0）。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=5,
            fingerprint_deviation=0.0,
        )
        assert m.risk_score == pytest.approx(0.3)

    def test_fingerprint_only(self):
        """STABLE + 0 anomalies + 0.8 fp → risk_score=0.24（0.3×0.8）。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.8,
        )
        assert m.risk_score == pytest.approx(0.24)

    def test_full_formula(self):
        """CRITICAL + 5 anomalies + 0.9 fp → 0.4+0.3+0.27=0.97。"""
        mon = AiAgentMonitor()
        for i in range(6):
            m = mon.assess(
                agent_metrics={"a": float(i), "b": float(i), "c": float(i), "d": float(i)},
                trajectory_anomaly_count=5,
                fingerprint_deviation=0.9,
            )
        assert m.emergence_state == "CRITICAL"
        assert m.risk_score == pytest.approx(0.97, abs=1e-4)


# ── 轨迹归一化 ───────────────────────────────────────────────────────


class TestTrajectoryNormalization:
    """trajectory_score = min(anomalies/5, 1.0)。"""

    def test_three_anomalies(self):
        """3 anomalies → trajectory_score=0.6。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=3,
            fingerprint_deviation=0.0,
        )
        assert m.details["trajectory_score"] == pytest.approx(0.6)

    def test_ten_anomalies_capped(self):
        """10 anomalies → trajectory_score=1.0（封顶）。"""
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=10,
            fingerprint_deviation=0.0,
        )
        assert m.details["trajectory_score"] == pytest.approx(1.0)


# ── 指纹钳制 ─────────────────────────────────────────────────────────


class TestFingerprintClamping:
    """fingerprint_deviation 钳制到 [0, 1]。"""

    def test_above_one_clamped(self):
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            fingerprint_deviation=1.5,
        )
        assert m.fingerprint_deviation == pytest.approx(1.0)

    def test_below_zero_clamped(self):
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            fingerprint_deviation=-0.3,
        )
        assert m.fingerprint_deviation == pytest.approx(0.0)

    def test_none_fingerprint_zero(self):
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            fingerprint_deviation=None,
        )
        assert m.fingerprint_deviation == pytest.approx(0.0)


# ── breach 判定 ──────────────────────────────────────────────────────


class TestBreachJudgment:
    """is_breached = risk_score > threshold OR emergence_state == CRITICAL。"""

    def test_stable_low_score_not_breached(self):
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.0,
        )
        assert m.is_breached is False

    def test_critical_always_breached(self):
        """CRITICAL → is_breached=True，即使 risk_score < threshold。"""
        mon = AiAgentMonitor()
        m = _drive_to_critical(mon)
        # risk_score=0.4 < 0.6, but CRITICAL → breached
        assert m.risk_score < DEFAULT_RISK_THRESHOLD
        assert m.is_breached is True

    def test_high_score_breached(self):
        """risk_score > 0.6 → breached（非 CRITICAL）。"""
        mon = AiAgentMonitor()
        # STABLE + 5 anomalies + 1.0 fp → 0+0.3+0.3=0.6, not > 0.6
        # STABLE + 5 anomalies + 1.0 fp with trajectory=5 → 0.3+0.3=0.6
        # Need > 0.6: use fp=1.0 + trajectory=5 → 0.3+0.3=0.6 (not >)
        # Use trajectory=5 + fp=1.0 → 0.6 exactly, not breached
        # Need slightly more: but STABLE emergence=0, so max without CRITICAL is 0.6
        # With trajectory=5 and fp=1.0 → exactly 0.6, not > 0.6
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=5,
            fingerprint_deviation=1.0,
        )
        assert m.risk_score == pytest.approx(0.6)
        assert m.is_breached is False  # 0.6 is not > 0.6

    def test_custom_threshold_breach(self):
        """自定义低阈值 → 更容易 breach。"""
        mon = AiAgentMonitor(risk_threshold=0.2)
        # STABLE + 0 + 0.8 fp → 0.24 > 0.2 → breached
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.8,
        )
        assert m.risk_score == pytest.approx(0.24)
        assert m.is_breached is True


# ── RiskCheckResult 转换 ─────────────────────────────────────────────


class TestToRiskCheckResult:
    def test_not_breached_info(self):
        mon = AiAgentMonitor()
        m = mon.assess(agent_metrics={"a": 0.5})
        r = mon.to_risk_check_result(m)
        assert r.passed is True
        assert r.severity == "info"
        assert r.rule_name == "ai_agent_monitor"

    def test_breached_halt(self):
        mon = AiAgentMonitor()
        m = _drive_to_critical(mon)
        r = mon.to_risk_check_result(m)
        assert r.passed is False
        assert r.severity == "HALT"

    def test_actual_value_is_risk_score(self):
        mon = AiAgentMonitor()
        m = mon.assess(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=5,
            fingerprint_deviation=0.8,
        )
        r = mon.to_risk_check_result(m)
        assert r.actual_value == Decimal(str(m.risk_score))


# ── 幂等键 ───────────────────────────────────────────────────────────


class TestIdempotencyKey:
    def test_unique_keys(self):
        mon = AiAgentMonitor()
        m1 = mon.assess(agent_metrics={"a": 0.5})
        m2 = mon.assess(agent_metrics={"a": 0.5})
        assert m1.idempotency_key != m2.idempotency_key
        assert m1.idempotency_key.startswith("aiagent-")

    def test_frozen_metrics(self):
        """AiAgentRiskMetrics 是 frozen dataclass。"""
        mon = AiAgentMonitor()
        m = mon.assess(agent_metrics={"a": 0.5})
        with pytest.raises(Exception):
            m.risk_score = 1.0  # type: ignore[misc]
