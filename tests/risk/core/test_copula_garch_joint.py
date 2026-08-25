# [BLUEPRINT] MOD-RK-33 | docs/03_modules/_domain_risk/copula_garch_joint/blueprint.md | §test
# [MODULE] tests.risk.core.test_copula_garch_joint
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.copula_garch_joint
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_copula_garch_joint.py
# [A_test] module_id: MOD-RK-33 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-33 单元测试: CopulaGarchJointModel — Copula-GARCH 联合分布建模（CAND-RSK-036）。

覆盖: 配置/输入校验（≤50 只硬约束/等长/有限值/权重/组合价值）、输出结构不变量
（矩阵对称/对角语义/值域/ES≥VaR/置信度单调）、联合尾部依赖识别（同暴跌对 λ 高于
独立对）、完全相关奇异性兜底、固定种子可复现、边缘密度预测注入。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.risk.core.copula_garch_joint import (
    CopulaGarchConfig,
    CopulaGarchJointError,
    CopulaGarchJointModel,
    JointRiskReport,
    MarginalForecast,
)

_T = 120  # 样本长度（≥min_history 默认 60）


def _iid_returns(seed: int = 7) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    return {
        "AAA": (0.0005 + 0.012 * rng.standard_normal(_T)).tolist(),
        "BBB": (0.0003 + 0.010 * rng.standard_normal(_T)).tolist(),
        "CCC": (-0.0002 + 0.015 * rng.standard_normal(_T)).tolist(),
    }


def _crash_pair_returns() -> dict[str, list[float]]:
    """X/Y 完全同跌同涨（共享收益序列），Z 与之近似独立。"""
    rng = np.random.default_rng(11)
    shared = 0.011 * rng.standard_normal(_T)
    shared[10] = -0.09
    shared[40] = -0.08
    shared[80] = -0.10  # 三天共同暴跌
    indep = 0.011 * rng.standard_normal(_T)
    return {"XXX": shared.tolist(), "YYY": shared.tolist(), "ZZZ": indep.tolist()}


class TestConfigValidation:
    def test_dcc_params_must_be_stationary(self):
        with pytest.raises(CopulaGarchJointError):
            CopulaGarchConfig(dcc_a=0.5, dcc_b=0.6)  # a+b≥1

    def test_max_assets_floor(self):
        with pytest.raises(CopulaGarchJointError):
            CopulaGarchConfig(max_assets=1)

    def test_garch_params_must_be_stationary(self):
        with pytest.raises(CopulaGarchJointError):
            CopulaGarchConfig(garch_alpha=0.7, garch_beta=0.5)

    def test_tail_quantile_range(self):
        with pytest.raises(CopulaGarchJointError):
            CopulaGarchConfig(tail_quantile=0.5)


class TestInputValidation:
    def test_rejects_more_than_50_assets(self):
        rng = np.random.default_rng(3)
        returns = {f"S{i:03d}": (0.01 * rng.standard_normal(_T)).tolist() for i in range(51)}
        weights = {f"S{i:03d}": 1.0 / 51 for i in range(51)}
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(returns, weights, portfolio_value=1_000_000.0)

    def test_rejects_ragged_lengths(self):
        rng = np.random.default_rng(21)
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(
                {
                    "AAA": (0.01 * rng.standard_normal(100)).tolist(),
                    "BBB": (0.01 * rng.standard_normal(99)).tolist(),
                },
                {"AAA": 0.5, "BBB": 0.5},
            )

    def test_rejects_short_history(self):
        rng = np.random.default_rng(22)
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(
                {
                    "AAA": (0.01 * rng.standard_normal(30)).tolist(),
                    "BBB": (0.012 * rng.standard_normal(30)).tolist(),
                },
                {"AAA": 0.5, "BBB": 0.5},
            )

    def test_rejects_non_finite(self):
        returns = _iid_returns()
        returns["AAA"][5] = float("nan")
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(returns, {"AAA": 0.4, "BBB": 0.3, "CCC": 0.3})

    def test_rejects_weight_symbol_mismatch(self):
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(_iid_returns(), {"AAA": 0.5, "BBB": 0.5})

    def test_rejects_zero_total_weight(self):
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(
                _iid_returns(), {"AAA": 0.0, "BBB": 0.0, "CCC": 0.0}
            )

    def test_rejects_non_positive_portfolio_value(self):
        model = CopulaGarchJointModel()
        with pytest.raises(CopulaGarchJointError):
            model.fit_portfolio_risk(
                _iid_returns(),
                {"AAA": 0.4, "BBB": 0.3, "CCC": 0.3},
                portfolio_value=0.0,
            )


class TestReportInvariants:
    @pytest.fixture(scope="class")
    def report(self) -> JointRiskReport:
        model = CopulaGarchJointModel(CopulaGarchConfig(n_simulations=4000))
        return model.fit_portfolio_risk(
            _iid_returns(),
            {"AAA": 0.5, "BBB": 0.3, "CCC": 0.2},
            portfolio_value=1_000_000.0,
        )

    def test_matrix_shape_and_symmetry(self, report: JointRiskReport):
        td = np.asarray(report.tail_dependence_matrix)
        assert td.shape == (3, 3)
        assert np.allclose(td, td.T)
        corr = np.asarray(report.dcc_correlation)
        assert corr.shape == (3, 3)
        assert np.allclose(corr, corr.T, atol=1e-8)

    def test_tail_dependence_diagonal_is_one(self, report: JointRiskReport):
        td = np.asarray(report.tail_dependence_matrix)
        assert np.allclose(np.diag(td), 1.0)
        assert np.all(td >= 0.0) and np.all(td <= 1.0)

    def test_correlation_diagonal_and_range(self, report: JointRiskReport):
        corr = np.asarray(report.dcc_correlation)
        assert np.allclose(np.diag(corr), 1.0, atol=1e-6)
        assert np.all(corr >= -1.0 - 1e-9) and np.all(corr <= 1.0 + 1e-9)

    def test_es_ge_var_and_confidence_monotone(self, report: JointRiskReport):
        assert report.joint_es[0.95] >= report.joint_var[0.95] >= 0.0
        assert report.joint_var[0.99] >= report.joint_var[0.95]
        assert report.joint_es[0.99] >= report.joint_es[0.95]

    def test_provenance_fields(self, report: JointRiskReport):
        assert report.n_assets == 3
        assert report.n_observations == _T
        assert report.simulations == 4000
        assert report.symbols == ("AAA", "BBB", "CCC")


class TestTailDependenceDetection:
    def test_shared_crash_pair_has_higher_tail_dependence(self):
        model = CopulaGarchJointModel(CopulaGarchConfig(n_simulations=2000))
        report = model.fit_portfolio_risk(
            _crash_pair_returns(),
            {"XXX": 0.4, "YYY": 0.4, "ZZZ": 0.2},
        )
        td = np.asarray(report.tail_dependence_matrix)
        idx = {s: i for i, s in enumerate(report.symbols)}
        lam_crash = td[idx["XXX"], idx["YYY"]]
        lam_indep = td[idx["XXX"], idx["ZZZ"]]
        assert lam_crash == pytest.approx(1.0)
        assert lam_crash > lam_indep

    def test_perfectly_correlated_assets_do_not_crash_model(self):
        # Qbar 奇异（ρ=1）时 Cholesky 需抖动兜底，不得抛非受控异常
        model = CopulaGarchJointModel(CopulaGarchConfig(n_simulations=2000))
        report = model.fit_portfolio_risk(
            _crash_pair_returns(),
            {"XXX": 0.5, "YYY": 0.5, "ZZZ": 0.0},
        )
        assert report.joint_var[0.95] >= 0.0


class TestReproducibilityAndInjection:
    def test_fixed_seed_reproducible(self):
        cfg = CopulaGarchConfig(n_simulations=3000)
        r1 = CopulaGarchJointModel(cfg).fit_portfolio_risk(
            _iid_returns(), {"AAA": 0.4, "BBB": 0.3, "CCC": 0.3}
        )
        r2 = CopulaGarchJointModel(cfg).fit_portfolio_risk(
            _iid_returns(), {"AAA": 0.4, "BBB": 0.3, "CCC": 0.3}
        )
        assert r1.joint_var == r2.joint_var
        assert r1.joint_es == r2.joint_es

    def test_marginal_forecast_injection_accepted(self):
        cfg = CopulaGarchConfig(n_simulations=3000)
        forecasts = {
            "AAA": MarginalForecast(mu=0.001, sigma=0.02),
            "BBB": MarginalForecast(mu=0.0, sigma=0.015),
            "CCC": MarginalForecast(mu=-0.001, sigma=0.025),
        }
        report = CopulaGarchJointModel(cfg).fit_portfolio_risk(
            _iid_returns(),
            {"AAA": 0.4, "BBB": 0.3, "CCC": 0.3},
            marginal_forecasts=forecasts,
        )
        assert report.joint_var[0.95] >= 0.0

    def test_marginal_forecast_rejects_non_positive_sigma(self):
        with pytest.raises(CopulaGarchJointError):
            MarginalForecast(mu=0.0, sigma=0.0)
