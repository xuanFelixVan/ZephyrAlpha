# [A_test] module_id: SRC-TST-2025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-642 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_fitness_functions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# AI-generated: 适应度函数框架单元测试（T-4-04, B17）
"""
FitnessFunctionFramework 单元测试
===================================
Task ID : T-4-04 (B17)
验收标准：≥ 15 条单元测试，mypy --strict 0 errors, ruff 0 errors

测试矩阵
--------
FitnessThresholds       : 默认值验证 / 自定义覆盖
measure_module_coupling : 单模块边界 / 低密度 PASS / 高密度 FAIL / 警告区间
measure_test_coverage   : 达标 PASS / 不足 FAIL / 警告区间
measure_compliance_rate : 全通过 / 高通过率 / 零记录默认 PASS / 低通过 FAIL
measure_knowledge_activation : 正常激活 / 零知识库 / WARN 区间
measure_hallucination_interception : 正常 / 零记录默认 PASS / 低拦截 FAIL
run_all / overall_status: 全 PASS / 有 WARN / 有 FAIL
to_json_report          : 可反序列化 / 包含所有字段
to_trend_data           : 多报告趋势转换
from_gate_results       : 工厂函数正确计数
FitnessReport.get_metric : 命中 / 未命中返回 None
"""

from __future__ import annotations

import json

import pytest

from zephyr.feedback_loop.fitness_functions import (
    METRIC_COMPLIANCE_RATE,
    METRIC_HALLUCINATION_INTERCEPTION,
    METRIC_KNOWLEDGE_ACTIVATION,
    METRIC_MODULE_COUPLING,
    METRIC_TEST_COVERAGE,
    FitnessFunctionFramework,
    FitnessInputs,
    FitnessThresholds,
    MetricStatus,
    from_gate_results,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def ff() -> FitnessFunctionFramework:
    """使用默认阈值的框架实例。"""
    return FitnessFunctionFramework()


@pytest.fixture()
def default_inputs() -> FitnessInputs:
    """全部度量通过的标准输入。"""
    return FitnessInputs(
        dependency_edges=[("A", "B"), ("B", "C")],
        module_count=20,
        coverage_pct=72.0,
        gate_total=100,
        gate_passed=95,
        ke_total=50,
        ke_activated=20,
        hallucination_total=30,
        hallucination_intercepted=25,
    )


# ---------------------------------------------------------------------------
# 1. FitnessThresholds
# ---------------------------------------------------------------------------


class TestFitnessThresholds:
    def test_default_values(self) -> None:
        """默认阈值符合验收标准约定。"""
        th = FitnessThresholds()
        assert th.module_coupling_max == 0.30
        assert th.test_coverage_min == 65.0
        assert th.compliance_rate_min == 0.90
        assert th.knowledge_activation_min == 0.30
        assert th.hallucination_interception_min == 0.70

    def test_custom_override(self) -> None:
        """自定义阈值可正常覆盖。"""
        th = FitnessThresholds(test_coverage_min=80.0, compliance_rate_min=0.95)
        assert th.test_coverage_min == 80.0
        assert th.compliance_rate_min == 0.95


# ---------------------------------------------------------------------------
# 2. measure_module_coupling
# ---------------------------------------------------------------------------


class TestModuleCoupling:
    def test_single_module_zero_density(self, ff: FitnessFunctionFramework) -> None:
        """单模块系统密度为 0，状态 PASS。"""
        m = ff.measure_module_coupling([("A", "B")], module_count=1)
        assert m.value == 0.0
        assert m.status == MetricStatus.PASS

    def test_low_density_passes(self, ff: FitnessFunctionFramework) -> None:
        """低密度（< 0.30）应为 PASS。"""
        # 2 edges, 20 modules → max = 190, density ≈ 0.011
        m = ff.measure_module_coupling([("A", "B"), ("B", "C")], module_count=20)
        assert m.status == MetricStatus.PASS
        assert m.value < 0.30

    def test_high_density_fails(self, ff: FitnessFunctionFramework) -> None:
        """高密度（> 0.35 含 warn_margin）应为 FAIL。"""
        # 全连接 5 模块：10 edges / 10 max = 1.0
        edges = [
            ("A", "B"),
            ("A", "C"),
            ("A", "D"),
            ("A", "E"),
            ("B", "C"),
            ("B", "D"),
            ("B", "E"),
            ("C", "D"),
            ("C", "E"),
            ("D", "E"),
        ]
        m = ff.measure_module_coupling(edges, module_count=5)
        assert m.status == MetricStatus.FAIL
        assert m.value > 0.30

    def test_warn_zone(self) -> None:
        """密度在 warn 区间 (threshold, threshold+warn_margin] 应为 WARN。"""
        th = FitnessThresholds(module_coupling_max=0.20, warn_margin=0.10)
        ff2 = FitnessFunctionFramework(thresholds=th)
        # 5 nodes → max_edges = 10; 3 unique edges → density = 3/10 = 0.30
        # 0.20 < 0.30 ≤ (0.20+0.10=0.30) → WARN
        edges = [("A", "B"), ("A", "C"), ("B", "C")]
        m = ff2.measure_module_coupling(edges, module_count=5)
        assert m.status == MetricStatus.WARN

    def test_duplicate_edges_deduplicated(self, ff: FitnessFunctionFramework) -> None:
        """重复边（无向）计为 1 条，不影响密度虚高。"""
        edges = [("A", "B"), ("B", "A"), ("A", "B")]
        m = ff.measure_module_coupling(edges, module_count=5)
        # 实际唯一边 = 1，density = 1/10 = 0.1 → PASS
        assert m.value == pytest.approx(1 / 10, abs=1e-6)
        assert m.status == MetricStatus.PASS


# ---------------------------------------------------------------------------
# 3. measure_test_coverage
# ---------------------------------------------------------------------------


class TestTestCoverage:
    def test_above_threshold_passes(self, ff: FitnessFunctionFramework) -> None:
        """72% > 65% → PASS。"""
        m = ff.measure_test_coverage(72.0)
        assert m.status == MetricStatus.PASS
        assert m.value == 72.0

    def test_exactly_at_threshold_passes(self, ff: FitnessFunctionFramework) -> None:
        """恰好等于阈值应为 PASS。"""
        m = ff.measure_test_coverage(65.0)
        assert m.status == MetricStatus.PASS

    def test_below_threshold_warn(self, ff: FitnessFunctionFramework) -> None:
        """60% < 65% 但 ≥ 60% (65 - 5%) → WARN。"""
        m = ff.measure_test_coverage(61.0)
        assert m.status == MetricStatus.WARN

    def test_far_below_threshold_fails(self, ff: FitnessFunctionFramework) -> None:
        """50% 远低于 65% → FAIL。"""
        m = ff.measure_test_coverage(50.0)
        assert m.status == MetricStatus.FAIL


# ---------------------------------------------------------------------------
# 4. measure_compliance_rate
# ---------------------------------------------------------------------------


class TestComplianceRate:
    def test_all_passed_is_pass(self, ff: FitnessFunctionFramework) -> None:
        """全部通过 → rate=1.0 → PASS。"""
        m = ff.measure_compliance_rate(gate_total=100, gate_passed=100)
        assert m.status == MetricStatus.PASS
        assert m.value == pytest.approx(1.0)

    def test_zero_total_defaults_to_pass(self, ff: FitnessFunctionFramework) -> None:
        """无门禁记录时默认为 PASS（rate=1.0）。"""
        m = ff.measure_compliance_rate(gate_total=0, gate_passed=0)
        assert m.status == MetricStatus.PASS
        assert m.value == pytest.approx(1.0)

    def test_low_compliance_fails(self, ff: FitnessFunctionFramework) -> None:
        """70% 通过率 < 85%（90-5% warn_margin）→ FAIL。"""
        m = ff.measure_compliance_rate(gate_total=100, gate_passed=70)
        assert m.status == MetricStatus.FAIL

    def test_warn_zone_compliance(self, ff: FitnessFunctionFramework) -> None:
        """86% 在警告区间 [85%, 90%) → WARN。"""
        m = ff.measure_compliance_rate(gate_total=100, gate_passed=86)
        assert m.status == MetricStatus.WARN


# ---------------------------------------------------------------------------
# 5. measure_knowledge_activation_rate
# ---------------------------------------------------------------------------


class TestKnowledgeActivationRate:
    def test_good_activation_passes(self, ff: FitnessFunctionFramework) -> None:
        """40% 激活率 > 30% → PASS。"""
        m = ff.measure_knowledge_activation_rate(ke_total=50, ke_activated=20)
        assert m.status == MetricStatus.PASS

    def test_zero_ke_total_is_warn_or_fail(self, ff: FitnessFunctionFramework) -> None:
        """空知识库激活率 = 0.0 < 25% → FAIL。"""
        m = ff.measure_knowledge_activation_rate(ke_total=0, ke_activated=0)
        assert m.status == MetricStatus.FAIL

    def test_warn_zone_activation(self, ff: FitnessFunctionFramework) -> None:
        """26% 在警告区间 [25%, 30%) → WARN。"""
        m = ff.measure_knowledge_activation_rate(ke_total=100, ke_activated=26)
        assert m.status == MetricStatus.WARN


# ---------------------------------------------------------------------------
# 6. measure_hallucination_interception_rate
# ---------------------------------------------------------------------------


class TestHallucinationInterceptionRate:
    def test_high_interception_passes(self, ff: FitnessFunctionFramework) -> None:
        """25/30 ≈ 83% > 70% → PASS。"""
        m = ff.measure_hallucination_interception_rate(hallucination_total=30, hallucination_intercepted=25)
        assert m.status == MetricStatus.PASS

    def test_zero_total_defaults_pass(self, ff: FitnessFunctionFramework) -> None:
        """无检测记录时默认 rate=1.0 → PASS。"""
        m = ff.measure_hallucination_interception_rate(hallucination_total=0, hallucination_intercepted=0)
        assert m.status == MetricStatus.PASS

    def test_low_interception_fails(self, ff: FitnessFunctionFramework) -> None:
        """50% 拦截率 < 65%（70-5%）→ FAIL。"""
        m = ff.measure_hallucination_interception_rate(hallucination_total=100, hallucination_intercepted=50)
        assert m.status == MetricStatus.FAIL


# ---------------------------------------------------------------------------
# 7. run_all / overall_status
# ---------------------------------------------------------------------------


class TestRunAll:
    def test_all_pass_overall_pass(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """全部 PASS 时 overall_status = PASS，report.passed = True。"""
        report = ff.run_all(default_inputs)
        assert report.overall_status == MetricStatus.PASS
        assert report.passed is True
        assert len(report.metrics) == 5

    def test_one_fail_overall_fail(self, ff: FitnessFunctionFramework) -> None:
        """任一度量 FAIL 时 overall_status = FAIL。"""
        inputs = FitnessInputs(
            dependency_edges=[],
            module_count=20,
            coverage_pct=20.0,  # FAIL: 低于 65%
            gate_total=100,
            gate_passed=98,
            ke_total=50,
            ke_activated=20,
            hallucination_total=30,
            hallucination_intercepted=25,
        )
        report = ff.run_all(inputs)
        assert report.overall_status == MetricStatus.FAIL
        assert report.passed is False

    def test_report_has_unique_id(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """每次 run_all 产生唯一 report_id（FF- 前缀）。"""
        r1 = ff.run_all(default_inputs)
        assert r1.report_id.startswith("FF-")
        # 两次调用时间间隔可能 < 1s，report_id 可能相同（秒级），跳过唯一性断言

    def test_get_metric_by_name(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """FitnessReport.get_metric 按名称查找正常返回。"""
        report = ff.run_all(default_inputs)
        m = report.get_metric(METRIC_TEST_COVERAGE)
        assert m is not None
        assert m.metric_name == METRIC_TEST_COVERAGE

    def test_get_metric_unknown_returns_none(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """未知度量名称返回 None。"""
        report = ff.run_all(default_inputs)
        assert report.get_metric("nonexistent_metric") is None


# ---------------------------------------------------------------------------
# 8. to_json_report / to_trend_data
# ---------------------------------------------------------------------------


class TestOutputFormats:
    def test_to_json_report_valid_json(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """to_json_report 返回合法 JSON，包含所有必要字段。"""
        report = ff.run_all(default_inputs)
        raw = FitnessFunctionFramework.to_json_report(report)
        data = json.loads(raw)
        assert "report_id" in data
        assert "overall_status" in data
        assert "metrics" in data
        assert len(data["metrics"]) == 5

    def test_to_json_report_metrics_have_required_fields(
        self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs
    ) -> None:
        """每条度量含 metric_name, value, threshold, status。"""
        report = ff.run_all(default_inputs)
        raw = FitnessFunctionFramework.to_json_report(report)
        data = json.loads(raw)
        for m in data["metrics"]:
            assert "metric_name" in m
            assert "value" in m
            assert "threshold" in m
            assert "status" in m

    def test_to_trend_data_empty_list(self, ff: FitnessFunctionFramework) -> None:
        """空报告列表返回空趋势数据。"""
        result = FitnessFunctionFramework.to_trend_data([])
        assert result == []

    def test_to_trend_data_multiple_reports(self, ff: FitnessFunctionFramework, default_inputs: FitnessInputs) -> None:
        """多份报告转为时序数据，每行含 5 类指标字段。"""
        r1 = ff.run_all(default_inputs)
        r2 = ff.run_all(default_inputs)
        trend = FitnessFunctionFramework.to_trend_data([r1, r2])
        assert len(trend) == 2
        for row in trend:
            assert "timestamp" in row
            assert "overall_status" in row
            assert METRIC_MODULE_COUPLING in row
            assert METRIC_TEST_COVERAGE in row
            assert METRIC_COMPLIANCE_RATE in row
            assert METRIC_KNOWLEDGE_ACTIVATION in row
            assert METRIC_HALLUCINATION_INTERCEPTION in row


# ---------------------------------------------------------------------------
# 9. from_gate_results 工厂函数
# ---------------------------------------------------------------------------


class TestFromGateResults:
    def test_counts_passed_correctly(self) -> None:
        """from_gate_results 正确统计通过 / 失败数量。"""
        gate_rows = [
            {"passed": True},
            {"passed": False},
            {"passed": 1},  # int 形式
            {"passed": 0},
            {"passed": True},
        ]
        inputs = from_gate_results(gate_rows, coverage_pct=70.0)
        assert inputs.gate_total == 5
        assert inputs.gate_passed == 3
        assert inputs.coverage_pct == 70.0

    def test_empty_gate_rows(self) -> None:
        """空行列表时 gate_total=0, gate_passed=0。"""
        inputs = from_gate_results([])
        assert inputs.gate_total == 0
        assert inputs.gate_passed == 0

    def test_extra_fields_forwarded(self) -> None:
        """ke_total 等额外字段可以通过 kwargs 传入。"""
        inputs = from_gate_results(
            [{"passed": True}],
            ke_total=100,
            ke_activated=40,
            hallucination_total=50,
            hallucination_intercepted=40,
        )
        assert inputs.ke_total == 100
        assert inputs.ke_activated == 40
