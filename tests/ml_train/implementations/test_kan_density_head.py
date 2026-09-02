# [BLUEPRINT] MOD-ML-017 | docs/03_modules/_domain_machine_learning_train/kan_density_head/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-017 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.implementations.test_kan_density_head
# [TESTS] src/zephyr/ml_train/implementations/kan_density_head.py
"""MOD-ML-017 单元测试：kan_density_head KAN 密度预测头。

蓝图验收（B10-01878/CAND-MLT-024，A1 §29.33）：
可学习 B 样条激活（阶数≤4 护栏 + Cox-de Boor 递推纯 numpy）+ 分位数前向
输出（单调不交叉）+ 接口对齐 QNN Stage1 + C-003 验证报告注入（未注入/未过
Fail-Closed 禁预测）。验证报告全内存替身。
"""

from __future__ import annotations

import datetime

import numpy as np
import pytest

pytest.importorskip(
    "zephyr.ml_train.implementations.kan_density_head",
    reason="kan_density_head not importable",
)

from zephyr.ml_train.implementations.kan_density_head import (  # noqa: E402
    KanDensityConfig,
    KanDensityHead,
    KanHeadError,
    MAX_SPLINE_ORDER,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_PASSED = {"c003_passed": True, "report_id": "C003-2026-001"}
_FAILED = {"c003_passed": False, "report_id": "C003-2026-002"}

#: 确定性训练数据：y = 2*x0 - x1 + 小扰动
_X = np.array(
    [
        [0.0, 1.0],
        [0.5, 0.8],
        [1.0, 0.6],
        [1.5, 0.4],
        [2.0, 0.2],
        [2.5, 0.0],
        [3.0, 0.2],
        [3.5, 0.4],
        [4.0, 0.6],
        [4.5, 0.8],
    ]
)
_Y = 2.0 * _X[:, 0] - _X[:, 1]


def _head(report=_PASSED, **cfg) -> KanDensityHead:
    return KanDensityHead(
        KanDensityConfig(**cfg) if cfg else None,
        validation_report=report,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 配置护栏
# ──────────────────────────────────────────────────────────────────────────────


class TestConfigGuard:
    def test_order_over_4_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head(spline_order=5)

    def test_order_boundary_4_accepted(self) -> None:
        head = _head(spline_order=4)
        assert head.config.spline_order == MAX_SPLINE_ORDER == 4

    def test_order_zero_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head(spline_order=0)

    def test_n_grid_zero_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head(n_grid=0)

    def test_quantile_out_of_range_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head(quantiles=(0.1, 1.5))
        with pytest.raises(KanHeadError):
            _head(quantiles=())

    def test_quantiles_must_be_sorted(self) -> None:
        with pytest.raises(KanHeadError):
            _head(quantiles=(0.5, 0.1))


# ──────────────────────────────────────────────────────────────────────────────
# 拟合
# ──────────────────────────────────────────────────────────────────────────────


class TestFit:
    def test_fit_ok_metrics(self) -> None:
        head = _head()
        metrics = head.fit(_X, _Y)
        assert metrics["n_train"] == 10
        assert metrics["n_features"] == 2
        assert metrics["spline_order"] == 3
        assert metrics["n_basis_total"] > 0
        assert metrics["trained_at"] == _T0.isoformat()

    def test_fit_learns_linear_shape(self) -> None:
        head = _head()
        head.fit(_X, _Y)
        pred = head.predict_quantiles(_X)[0.5]
        assert pred == pytest.approx(_Y, abs=0.3)

    def test_fit_deterministic(self) -> None:
        h1, h2 = _head(), _head()
        h1.fit(_X, _Y)
        h2.fit(_X, _Y)
        p1 = h1.predict_quantiles(_X)
        p2 = h2.predict_quantiles(_X)
        for q in p1:
            assert p1[q] == pytest.approx(p2[q])

    def test_fit_1d_input_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head().fit(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))

    def test_fit_too_few_samples_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head().fit(np.array([[1.0, 2.0]]), np.array([1.0]))

    def test_fit_length_mismatch_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head().fit(_X, _Y[:-1])

    def test_fit_constant_feature_ok(self) -> None:
        x = np.column_stack([_X[:, 0], np.ones(len(_X))])
        head = _head()
        head.fit(x, _Y)
        pred = head.predict_quantiles(x)
        assert set(pred) == set(head.config.quantiles)


# ──────────────────────────────────────────────────────────────────────────────
# 前向分位数输出（接口对齐 QNN Stage1）
# ──────────────────────────────────────────────────────────────────────────────


class TestPredictQuantiles:
    def test_output_interface_aligned_with_qnn_stage1(self) -> None:
        head = _head()
        head.fit(_X, _Y)
        out = head.predict_quantiles(_X)
        assert isinstance(out, dict)
        assert set(out) == {0.1, 0.25, 0.5, 0.75, 0.9}
        for arr in out.values():
            assert arr.shape == (len(_X),)

    def test_quantiles_monotone_non_crossing(self) -> None:
        head = _head()
        head.fit(_X, _Y)
        out = head.predict_quantiles(_X)
        qs = sorted(out)
        for i in range(1, len(qs)):
            assert np.all(out[qs[i]] >= out[qs[i - 1]] - 1e-12)

    def test_median_between_band_edges(self) -> None:
        head = _head()
        head.fit(_X, _Y)
        out = head.predict_quantiles(_X)
        assert np.all(out[0.5] >= out[0.1])
        assert np.all(out[0.5] <= out[0.9])

    def test_predict_before_fit_rejected(self) -> None:
        with pytest.raises(KanHeadError):
            _head().predict_quantiles(_X)

    def test_predict_dim_mismatch_rejected(self) -> None:
        head = _head()
        head.fit(_X, _Y)
        with pytest.raises(KanHeadError):
            head.predict_quantiles(np.ones((4, 3)))
        with pytest.raises(KanHeadError):
            head.predict_quantiles(np.ones(4))


# ──────────────────────────────────────────────────────────────────────────────
# C-003 验证语义（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestC003Gate:
    def test_report_not_injected_forbids_predict(self) -> None:
        head = KanDensityHead(validation_report=None, clock=lambda: _T0)
        head.fit(_X, _Y)
        with pytest.raises(KanHeadError):
            head.predict_quantiles(_X)

    def test_report_failed_forbids_predict(self) -> None:
        head = _head(report=_FAILED)
        head.fit(_X, _Y)
        with pytest.raises(KanHeadError):
            head.predict_quantiles(_X)

    def test_report_passed_allows_predict(self) -> None:
        head = _head(report=_PASSED)
        head.fit(_X, _Y)
        assert head.predict_quantiles(_X)  # 不抛即过门禁


# ──────────────────────────────────────────────────────────────────────────────
# Cox-de Boor 基函数性质
# ──────────────────────────────────────────────────────────────────────────────


class TestSplineBasis:
    def test_basis_partition_of_unity(self) -> None:
        knots = KanDensityHead._build_knots(0.0, 1.0, n_grid=4, degree=3)
        n_basis = 4 + 3
        x = np.linspace(0.0, 1.0, 21)
        basis = KanDensityHead._basis_matrix(x, knots, degree=3, n_basis=n_basis)
        assert basis.shape == (21, n_basis)
        assert basis.sum(axis=1) == pytest.approx(np.ones(21))  # 单位分解

    def test_knots_clamped_endpoints(self) -> None:
        knots = KanDensityHead._build_knots(0.0, 2.0, n_grid=3, degree=2)
        assert list(knots[:3]) == [0.0, 0.0, 0.0]
        assert list(knots[-3:]) == [2.0, 2.0, 2.0]
