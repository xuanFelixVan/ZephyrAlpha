# [BLUEPRINT] MOD-RK-38 | docs/03_modules/_domain_risk/factor_exposure_manager/blueprint.md | §test
# [MODULE] tests.risk.core.test_factor_exposure_manager
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.factor_exposure_manager
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_factor_exposure_manager.py
# [A_test] module_id: MOD-RK-38 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-38 单元测试: FactorExposureManager — 因子敞口管理器（PC-14）。

覆盖: 载荷加权敞口矩阵、权重归一化、缺载荷 uncovered 披露、超限 WARNING/BREACH
分级与降序、limits 外因子只计量不预警、audit_sink 回调、非法输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.risk.core.factor_exposure_manager import (
    ExposureBreach,
    ExposureSeverity,
    FactorExposureConfig,
    FactorExposureManager,
    FactorExposureReport,
    InvalidFactorExposureInputError,
)


def _manager(**kwargs) -> FactorExposureManager:
    return FactorExposureManager(FactorExposureConfig(**kwargs))


class TestExposureComputation:
    def test_weighted_exposure_matrix(self):
        mgr = _manager(limits={"value": 1.0, "size": 1.0})
        report = mgr.compute_exposures(
            positions={"A": 0.5, "B": 0.5},
            factor_loadings={"A": {"value": 0.8, "size": -0.2}, "B": {"value": 0.4, "size": 0.6}},
        )
        assert report.exposures["value"] == pytest.approx(0.5 * 0.8 + 0.5 * 0.4)
        assert report.exposures["size"] == pytest.approx(0.5 * -0.2 + 0.5 * 0.6)
        assert report.breaches == ()
        assert report.uncovered_symbols == ()
        assert report.weight_sum == pytest.approx(1.0)

    def test_weights_auto_normalized(self):
        mgr = _manager(limits={"value": 1.0})
        report = mgr.compute_exposures(
            positions={"A": 2.0, "B": 6.0},
            factor_loadings={"A": {"value": 1.0}, "B": {"value": 0.0}},
        )
        # 归一化后 w_A=0.25 → exposure=0.25
        assert report.exposures["value"] == pytest.approx(0.25)
        assert report.weight_sum == pytest.approx(1.0)

    def test_missing_loadings_disclosed_as_uncovered(self):
        mgr = _manager(limits={"value": 1.0})
        report = mgr.compute_exposures(
            positions={"A": 0.5, "B": 0.5},
            factor_loadings={"A": {"value": 1.0}},
        )
        assert report.exposures["value"] == pytest.approx(0.5)
        assert report.uncovered_symbols == ("B",)

    def test_factor_union_loadings_beyond_limits_measured_only(self):
        mgr = _manager(limits={"value": 1.0})
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.1, "momentum": 5.0}},
        )
        # momentum 无 limit：计量但不预警
        assert report.exposures["momentum"] == pytest.approx(5.0)
        assert report.breaches == ()

    def test_limit_factor_without_loading_is_zero(self):
        mgr = _manager(limits={"value": 1.0, "industry_sw_bank": 0.3})
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.2}},
        )
        assert report.exposures["industry_sw_bank"] == pytest.approx(0.0)
        assert report.breaches == ()


class TestBreachGrading:
    def test_warning_and_breach_sorted_desc(self):
        mgr = _manager(limits={"value": 0.5, "size": 0.4, "beta": 1.0}, warn_ratio=0.8)
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.45, "size": 0.44, "beta": 0.1}},
        )
        # value: 0.45/0.5=0.9 → WARNING; size: 0.44/0.4=1.1 → BREACH; beta OK
        assert [b.factor for b in report.breaches] == ["size", "value"]
        assert report.breaches[0].severity is ExposureSeverity.BREACH
        assert report.breaches[1].severity is ExposureSeverity.WARNING

    def test_negative_exposure_abs_judged(self):
        mgr = _manager(limits={"size": 0.3})
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"size": -0.35}},
        )
        assert len(report.breaches) == 1
        assert report.breaches[0].severity is ExposureSeverity.BREACH

    def test_exactly_at_warn_ratio_is_warning(self):
        mgr = _manager(limits={"value": 1.0}, warn_ratio=0.8)
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.8}},
        )
        assert len(report.breaches) == 1
        assert report.breaches[0].severity is ExposureSeverity.WARNING

    def test_report_is_frozen(self):
        mgr = _manager(limits={"value": 1.0})
        report = mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.1}},
        )
        assert isinstance(report, FactorExposureReport)
        with pytest.raises(AttributeError):
            report.weight_sum = 2.0  # type: ignore[misc]


class TestAuditSink:
    def test_audit_sink_called_per_breach(self):
        seen: list[ExposureBreach] = []
        mgr = FactorExposureManager(
            FactorExposureConfig(limits={"value": 0.3, "size": 0.3}),
            audit_sink=seen.append,
        )
        mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.5, "size": 0.1}},
        )
        assert [b.factor for b in seen] == ["value"]

    def test_no_breach_no_audit(self):
        seen: list[ExposureBreach] = []
        mgr = FactorExposureManager(
            FactorExposureConfig(limits={"value": 1.0}),
            audit_sink=seen.append,
        )
        mgr.compute_exposures(
            positions={"A": 1.0},
            factor_loadings={"A": {"value": 0.1}},
        )
        assert seen == []


class TestFailClosed:
    def test_negative_weight_rejected(self):
        mgr = _manager(limits={"value": 1.0})
        with pytest.raises(InvalidFactorExposureInputError):
            mgr.compute_exposures(positions={"A": -0.1}, factor_loadings={"A": {"value": 0.1}})

    def test_empty_positions_rejected(self):
        mgr = _manager(limits={"value": 1.0})
        with pytest.raises(InvalidFactorExposureInputError):
            mgr.compute_exposures(positions={}, factor_loadings={})

    def test_zero_weight_sum_rejected(self):
        mgr = _manager(limits={"value": 1.0})
        with pytest.raises(InvalidFactorExposureInputError):
            mgr.compute_exposures(positions={"A": 0.0}, factor_loadings={"A": {"value": 0.1}})

    def test_non_finite_weight_rejected(self):
        mgr = _manager(limits={"value": 1.0})
        with pytest.raises(InvalidFactorExposureInputError):
            mgr.compute_exposures(positions={"A": float("nan")}, factor_loadings={"A": {"value": 0.1}})

    def test_non_finite_loading_rejected(self):
        mgr = _manager(limits={"value": 1.0})
        with pytest.raises(InvalidFactorExposureInputError):
            mgr.compute_exposures(positions={"A": 1.0}, factor_loadings={"A": {"value": float("inf")}})

    def test_bad_limit_rejected(self):
        with pytest.raises(InvalidFactorExposureInputError):
            FactorExposureConfig(limits={"value": 0.0})

    def test_bad_warn_ratio_rejected(self):
        with pytest.raises(InvalidFactorExposureInputError):
            FactorExposureConfig(limits={"value": 1.0}, warn_ratio=1.0)
