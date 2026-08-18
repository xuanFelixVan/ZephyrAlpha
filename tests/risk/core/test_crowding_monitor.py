# [BLUEPRINT] MOD-RK-13 | docs/03_modules/_domain_risk/crowding_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_crowding_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.crowding_monitor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_crowding_monitor.py
# [A_test] module_id: MOD-RK-13 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-13 Crowding Monitor 单元测试.

覆盖: 持仓重叠度(手工验证)/方向一致性/综合判定/批量评估/
策略数不足/无暴露/零权重/RiskCheckResult转换/不可变性.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytest.importorskip("zephyr.risk.core.crowding_monitor", reason="crowding_monitor not importable")

from zephyr.risk.core.crowding_monitor import (  # noqa: E402
    DEFAULT_CROWDING_THRESHOLD,
    CrowdingMetrics,
    CrowdingMonitor,
    InvalidCrowdingInputError,
)

# ── Mock 数据 ─────────────────────────────────────────────────────────


#: Scenario 1: 完全相同持仓 → overlap=1.0
MOCK_IDENTICAL = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2, "600036.SH": 0.1},
    "strat_b": {"600000.SH": 0.3, "000001.SZ": 0.2, "600036.SH": 0.1},
}

#: Scenario 2: 完全不同持仓 → overlap=0.0
MOCK_NO_OVERLAP = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2},
    "strat_b": {"600036.SH": 0.3, "601398.SH": 0.2},
}

#: Scenario 3: 部分重叠
MOCK_PARTIAL = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2},
    "strat_b": {"600000.SH": 0.2, "600036.SH": 0.3},
}

#: Scenario 4: 拥挤（高重叠 + 同方向）
MOCK_CROWDED = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2, "600036.SH": 0.1},
    "strat_b": {"600000.SH": 0.28, "000001.SZ": 0.18, "600036.SH": 0.12},
    "strat_c": {"600000.SH": 0.25, "000001.SZ": 0.22, "600036.SH": 0.08},
}
MOCK_CROWDED_EXP = {"strat_a": 0.8, "strat_b": 0.7, "strat_c": 0.6}

#: Scenario 5: 不拥挤（低重叠）
MOCK_NOT_CROWDED = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2},
    "strat_b": {"600036.SH": 0.3, "601398.SH": 0.2},
    "strat_c": {"000002.SZ": 0.3, "600519.SH": 0.2},
}

#: Scenario 6: 对冲（方向完全相反）
MOCK_HEDGED_EXP = {"strat_a": 0.8, "strat_b": -0.8}

#: Scenario 7: 单策略（不足以评估）
MOCK_SINGLE = {"strat_a": {"600000.SH": 0.3}}


# ── CrowdingMetrics 数据模型测试 ──────────────────────────────────────


class TestCrowdingMetrics:
    def test_creation(self):
        m = CrowdingMetrics(
            factor_name="momentum",
            crowding_score=0.7,
            position_overlap=0.6,
            direction_consensus=0.8,
            n_strategies=3,
            is_crowded=True,
            threshold=0.6,
            timestamp=datetime.now(UTC),
            idempotency_key="key-1",
        )
        assert m.factor_name == "momentum"
        assert m.is_crowded is True

    def test_frozen_immutability(self):
        m = CrowdingMetrics(
            factor_name="f", crowding_score=0, position_overlap=0,
            direction_consensus=0, n_strategies=1, is_crowded=False,
            threshold=0.6, timestamp=datetime.now(UTC), idempotency_key="k",
        )
        with pytest.raises(AttributeError):
            m.factor_name = "other"


# ── 持仓重叠度测试 ────────────────────────────────────────────────────


class TestPositionOverlap:
    def test_identical_positions(self):
        """完全相同持仓 → overlap=1.0"""
        mon = CrowdingMonitor()
        overlap = mon.compute_position_overlap(MOCK_IDENTICAL)
        assert overlap == pytest.approx(1.0, abs=1e-6)

    def test_no_overlap(self):
        """完全不同持仓 → overlap=0.0"""
        mon = CrowdingMonitor()
        overlap = mon.compute_position_overlap(MOCK_NO_OVERLAP)
        assert overlap == pytest.approx(0.0, abs=1e-6)

    def test_partial_overlap_manual_verification(self):
        """手工验证部分重叠。

        strat_a: {600000: 0.3, 000001: 0.2}
        strat_b: {600000: 0.2, 600036: 0.3}

        symbols: 600000, 000001, 600036
        min: min(0.3,0.2)=0.2, min(0.2,0)=0, min(0,0.3)=0 → Σmin=0.2
        max: max(0.3,0.2)=0.3, max(0.2,0)=0.2, max(0,0.3)=0.3 → Σmax=0.8
        overlap = 0.2 / 0.8 = 0.25
        """
        mon = CrowdingMonitor()
        overlap = mon.compute_position_overlap(MOCK_PARTIAL)
        expected = 0.2 / 0.8  # 0.25
        assert overlap == pytest.approx(expected, abs=1e-6)

    def test_three_strategies_overlap(self):
        """3 策略拥挤场景 → 高重叠度

        手工验证:
        600000: min(0.3,0.28,0.25)=0.25, max=0.3
        000001: min(0.2,0.18,0.22)=0.18, max=0.22
        600036: min(0.1,0.12,0.08)=0.08, max=0.12
        Σmin=0.51, Σmax=0.64 → overlap=0.796875
        """
        mon = CrowdingMonitor()
        overlap = mon.compute_position_overlap(MOCK_CROWDED)
        assert overlap == pytest.approx(0.796875, abs=1e-6)
        assert overlap > 0.75  # 高重叠

    def test_single_strategy_raises(self):
        """策略数 < 2 → InvalidCrowdingInputError"""
        mon = CrowdingMonitor()
        with pytest.raises(InvalidCrowdingInputError):
            mon.compute_position_overlap(MOCK_SINGLE)

    def test_empty_positions_returns_zero(self):
        """所有策略空持仓 → overlap=0.0"""
        mon = CrowdingMonitor()
        overlap = mon.compute_position_overlap({"a": {}, "b": {}})
        assert overlap == 0.0


# ── 方向一致性测试 ────────────────────────────────────────────────────


class TestDirectionConsensus:
    def test_all_same_direction(self):
        """所有策略同方向 → consensus=1.0"""
        mon = CrowdingMonitor()
        consensus = mon.compute_direction_consensus(MOCK_CROWDED_EXP)
        assert consensus == pytest.approx(1.0, abs=1e-6)

    def test_hedged_directions(self):
        """方向完全相反 → consensus=0.0"""
        mon = CrowdingMonitor()
        consensus = mon.compute_direction_consensus(MOCK_HEDGED_EXP)
        assert consensus == pytest.approx(0.0, abs=1e-6)

    def test_partial_consensus_manual_verification(self):
        """手工验证: 3正1负 → |3-1|/4 = 0.5"""
        exposures = {"a": 0.5, "b": 0.3, "c": 0.2, "d": -0.4}
        mon = CrowdingMonitor()
        consensus = mon.compute_direction_consensus(exposures)
        # sign: +1, +1, +1, -1 → |3-1|/4 = 0.5
        assert consensus == pytest.approx(0.5, abs=1e-6)

    def test_zero_exposures(self):
        """全部零暴露 → consensus=0.0"""
        mon = CrowdingMonitor()
        consensus = mon.compute_direction_consensus({"a": 0.0, "b": 0.0})
        assert consensus == pytest.approx(0.0, abs=1e-6)

    def test_empty_raises(self):
        """空字典 → InvalidCrowdingInputError"""
        mon = CrowdingMonitor()
        with pytest.raises(InvalidCrowdingInputError):
            mon.compute_direction_consensus({})


# ── 综合评估测试 ──────────────────────────────────────────────────────


class TestAssess:
    def test_crowded_detected(self):
        """高重叠 + 同方向 → is_crowded=True"""
        mon = CrowdingMonitor()
        m = mon.assess(
            factor_name="momentum",
            strategy_positions=MOCK_CROWDED,
            factor_exposures=MOCK_CROWDED_EXP,
        )
        assert m.is_crowded is True
        assert m.crowding_score > DEFAULT_CROWDING_THRESHOLD
        assert m.position_overlap > 0.75  # 0.796875 手工验证
        assert m.direction_consensus > 0.9

    def test_not_crowded_low_overlap(self):
        """低重叠 → is_crowded=False"""
        mon = CrowdingMonitor()
        m = mon.assess(
            factor_name="value",
            strategy_positions=MOCK_NOT_CROWDED,
            factor_exposures={"strat_a": 0.5, "strat_b": 0.3, "strat_c": 0.4},
        )
        assert m.is_crowded is False
        assert m.position_overlap < 0.3

    def test_not_crowded_hedged(self):
        """高重叠但方向对冲 → consensus=0 → crowding=0.5*overlap < threshold"""
        mon = CrowdingMonitor()
        m = mon.assess(
            factor_name="beta",
            strategy_positions=MOCK_IDENTICAL,
            factor_exposures=MOCK_HEDGED_EXP,
        )
        # overlap=1.0, consensus=0.0 → crowding=0.5 < 0.6
        assert m.position_overlap == pytest.approx(1.0, abs=1e-6)
        assert m.direction_consensus == pytest.approx(0.0, abs=1e-6)
        assert m.is_crowded is False

    def test_no_exposures_consensus_zero(self):
        """无因子暴露 → consensus=0.0"""
        mon = CrowdingMonitor()
        m = mon.assess(
            factor_name="size",
            strategy_positions=MOCK_CROWDED,
        )
        assert m.direction_consensus == 0.0

    def test_single_strategy_not_crowded(self):
        """单策略 → 跳过评估，默认 not crowded"""
        mon = CrowdingMonitor()
        m = mon.assess(
            factor_name="test",
            strategy_positions=MOCK_SINGLE,
        )
        assert m.is_crowded is False
        assert m.crowding_score == 0.0
        assert m.n_strategies == 1

    def test_idempotency_key_unique(self):
        mon = CrowdingMonitor()
        m1 = mon.assess("f", MOCK_CROWDED, MOCK_CROWDED_EXP)
        m2 = mon.assess("f", MOCK_CROWDED, MOCK_CROWDED_EXP)
        assert m1.idempotency_key != m2.idempotency_key

    def test_custom_threshold(self):
        """自定义阈值：低阈值使正常持仓也判定为拥挤"""
        mon = CrowdingMonitor(crowding_threshold=0.1)
        m = mon.assess(
            factor_name="low_thresh",
            strategy_positions=MOCK_PARTIAL,
            factor_exposures={"strat_a": 0.5, "strat_b": 0.3},
        )
        # overlap=0.25, consensus=1.0 → crowding=0.625 > 0.1 → crowded
        assert m.is_crowded is True
        assert m.threshold == 0.1


# ── 批量评估测试 ──────────────────────────────────────────────────────


class TestAssessBatch:
    def test_batch_mixed_results(self):
        mon = CrowdingMonitor()
        results = mon.assess_batch(
            factors={
                "momentum": MOCK_CROWDED,
                "value": MOCK_NOT_CROWDED,
            },
            factor_exposures_map={
                "momentum": MOCK_CROWDED_EXP,
                "value": {"strat_a": 0.5, "strat_b": 0.3, "strat_c": 0.4},
            },
        )
        assert len(results) == 2
        momentum = next(m for m in results if m.factor_name == "momentum")
        value = next(m for m in results if m.factor_name == "value")
        assert momentum.is_crowded is True
        assert value.is_crowded is False

    def test_batch_without_exposures(self):
        mon = CrowdingMonitor()
        results = mon.assess_batch({
            "f1": MOCK_CROWDED,
            "f2": MOCK_NOT_CROWDED,
        })
        assert len(results) == 2
        # 无暴露 → consensus=0 → crowding=0.5*overlap
        for m in results:
            assert m.direction_consensus == 0.0

    def test_batch_skips_invalid(self):
        """单策略因子被跳过"""
        mon = CrowdingMonitor()
        results = mon.assess_batch({
            "valid": MOCK_CROWDED,
            "invalid": MOCK_SINGLE,
        })
        # invalid 的 assess 返回默认值（不 raise），所以也在结果中
        assert len(results) == 2
        invalid_metric = next(m for m in results if m.factor_name == "invalid")
        assert invalid_metric.n_strategies == 1


# ── RiskCheckResult 转换测试 ──────────────────────────────────────────


class TestToRiskCheckResult:
    def test_crowded_to_halt(self):
        mon = CrowdingMonitor()
        m = CrowdingMetrics(
            factor_name="momentum", crowding_score=0.8,
            position_overlap=0.7, direction_consensus=0.9,
            n_strategies=3, is_crowded=True, threshold=0.6,
            timestamp=datetime.now(UTC), idempotency_key="k",
        )
        r = mon.to_risk_check_result(m)
        assert r.passed is False
        assert r.severity == "HALT"
        assert r.rule_name == "crowding_monitor"

    def test_not_crowded_to_pass(self):
        mon = CrowdingMonitor()
        m = CrowdingMetrics(
            factor_name="value", crowding_score=0.3,
            position_overlap=0.2, direction_consensus=0.4,
            n_strategies=3, is_crowded=False, threshold=0.6,
            timestamp=datetime.now(UTC), idempotency_key="k",
        )
        r = mon.to_risk_check_result(m)
        assert r.passed is True
        assert r.severity == "info"
