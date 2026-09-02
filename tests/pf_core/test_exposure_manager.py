# [TTL] permanent
# [TESTS] src/zephyr/pf_core/core/exposure_manager.py (MOD-PF-011)
"""MOD-PF-011 exposure_manager 单元测试（B3-05543 PC-07 敞口管理器）。"""

from __future__ import annotations

import pytest

from zephyr.pf_core.core.exposure_manager import (
    ActiveExposureReport,
    ExposureManager,
    ExposureManagerConfig,
    ExposureManagerError,
    RotationSignal,
)

IND = {"A": "银行", "B": "银行", "C": "电子", "D": "医药"}


def _mgr(**kw) -> ExposureManager:
    return ExposureManager(ExposureManagerConfig(**kw))


class TestActiveExposure:
    def test_industry_active_vs_benchmark(self) -> None:
        mgr = _mgr()
        rep = mgr.analyze(
            positions={"A": 0.4, "B": 0.2, "C": 0.4},
            industry_map=IND,
            benchmark_industry_weights={"银行": 0.30, "电子": 0.30, "医药": 0.40},
        )
        assert isinstance(rep, ActiveExposureReport)
        assert abs(rep.industry_active["银行"] - 0.30) < 1e-9  # 0.6-0.3
        assert abs(rep.industry_active["电子"] - 0.10) < 1e-9  # 0.4-0.3
        assert abs(rep.industry_active["医药"] + 0.40) < 1e-9  # 0-0.4

    def test_benchmark_from_weights(self) -> None:
        mgr = _mgr()
        rep = mgr.analyze(
            positions={"A": 0.5, "C": 0.5},
            industry_map=IND,
            benchmark_weights={"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25},
        )
        # 基准行业：银行 0.5 / 电子 0.25 / 医药 0.25
        assert abs(rep.industry_active["银行"] - 0.0) < 1e-9  # 0.5-0.5
        assert abs(rep.industry_active["电子"] - 0.25) < 1e-9  # 0.5-0.25
        assert abs(rep.industry_active["医药"] + 0.25) < 1e-9

    def test_style_active_exposure(self) -> None:
        mgr = _mgr()
        rep = mgr.analyze(
            positions={"A": 0.5, "C": 0.5},
            industry_map=IND,
            benchmark_industry_weights={"银行": 0.5, "电子": 0.5},
            style_loadings={"A": {"growth": 1.0}, "C": {"growth": 0.0, "size": -0.5}},
            benchmark_style_exposures={"growth": 0.2, "size": 0.0},
        )
        assert abs(rep.style_active["growth"] - (0.5 - 0.2)) < 1e-9
        assert abs(rep.style_active["size"] - (-0.25 - 0.0)) < 1e-9

    def test_uncovered_symbols_disclosed(self) -> None:
        mgr = _mgr()
        rep = mgr.analyze(
            positions={"A": 0.5, "ZZ": 0.5},
            industry_map=IND,
            benchmark_industry_weights={"银行": 1.0},
        )
        assert "ZZ" in rep.uncovered_symbols


class TestDeviationAlerts:
    def test_breach_and_warning_sorted(self) -> None:
        mgr = _mgr(industry_warn=0.05, industry_breach=0.10)
        rep = mgr.analyze(
            positions={"A": 0.4, "B": 0.2, "C": 0.36, "D": 0.04},
            industry_map=IND,
            benchmark_industry_weights={"银行": 0.30, "电子": 0.30, "医药": 0.40},
        )
        # 银行 active +0.30 BREACH；医药 -0.36 BREACH；电子 +0.06 WARNING(≥0.05 未超0.10)
        factors = [(d.dimension, d.name, d.severity) for d in rep.deviations]
        assert ("industry", "医药", "BREACH") in factors
        assert ("industry", "银行", "BREACH") in factors
        assert ("industry", "电子", "WARNING") in factors
        # 按 |active/limit| 降序
        assert rep.deviations[0].name == "医药"


class TestRotationSignals:
    def test_rotation_top_bottom(self) -> None:
        mgr = _mgr(rotation_band=0.10, rotation_top_n=1, rotation_bottom_n=1)
        rep = mgr.analyze(
            positions={"A": 0.2, "C": 0.45, "D": 0.35},
            industry_map=IND,
            benchmark_industry_weights={"银行": 0.2, "电子": 0.4, "医药": 0.4},
            industry_momentum={"电子": 0.9, "医药": -0.8, "银行": 0.0},
        )
        rot = {r.industry: r.signal for r in rep.rotation}
        # 电子 top1 且 active +0.05 带内 → 增配；医药 bottom1 且 active -0.05 带内 → 减配
        assert rot["电子"] is RotationSignal.OVERWEIGHT
        assert rot["医药"] is RotationSignal.UNDERWEIGHT
        assert rot["银行"] is RotationSignal.NEUTRAL

    def test_rotation_requires_momentum(self) -> None:
        mgr = _mgr()
        rep = mgr.analyze(
            positions={"A": 1.0},
            industry_map=IND,
            benchmark_industry_weights={"银行": 1.0},
            industry_momentum=None,
        )
        assert rep.rotation == ()

    def test_overweight_when_room(self) -> None:
        mgr = _mgr(rotation_band=0.10, rotation_top_n=1, rotation_bottom_n=1)
        rep = mgr.analyze(
            positions={"A": 0.5, "C": 0.5},
            industry_map=IND,
            benchmark_industry_weights={"银行": 0.5, "电子": 0.5},
            industry_momentum={"电子": 1.0, "银行": -1.0},
        )
        rot = {r.industry: r.signal for r in rep.rotation}
        assert rot["电子"] is RotationSignal.OVERWEIGHT  # top1 且 active 0 < band
        assert rot["银行"] is RotationSignal.UNDERWEIGHT  # bottom1 且 active 0 > -band


class TestFailClosed:
    def test_empty_positions(self) -> None:
        with pytest.raises(ExposureManagerError):
            _mgr().analyze(positions={}, industry_map=IND, benchmark_industry_weights={})

    def test_negative_weight(self) -> None:
        with pytest.raises(ExposureManagerError):
            _mgr().analyze(positions={"A": -0.1}, industry_map=IND, benchmark_industry_weights={})

    def test_empty_industry_map(self) -> None:
        with pytest.raises(ExposureManagerError):
            _mgr().analyze(positions={"A": 1.0}, industry_map={}, benchmark_industry_weights={})

    def test_no_benchmark_rejected(self) -> None:
        with pytest.raises(ExposureManagerError):
            _mgr().analyze(positions={"A": 1.0}, industry_map=IND)

    def test_invalid_config(self) -> None:
        with pytest.raises(ExposureManagerError):
            ExposureManagerConfig(industry_warn=-0.1)
        with pytest.raises(ExposureManagerError):
            ExposureManagerConfig(industry_warn=0.2, industry_breach=0.1)

    def test_non_finite_momentum(self) -> None:
        with pytest.raises(ExposureManagerError):
            _mgr().analyze(
                positions={"A": 1.0},
                industry_map=IND,
                benchmark_industry_weights={"银行": 1.0},
                industry_momentum={"银行": float("inf")},
            )
