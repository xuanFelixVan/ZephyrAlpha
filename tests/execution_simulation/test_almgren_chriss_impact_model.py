# [BLUEPRINT] MOD-EXSIM-001 | docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-EXSIM-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.execution_simulation.test_almgren_chriss_impact_model
# [TESTS] src/zephyr/execution_simulation/almgren_chriss_impact_model.py
"""MOD-EXSIM-001 单元测试：almgren_chriss_impact_model Almgren-Chriss 冲击成本模型。

蓝图验收（B3-06286/CAND-EXSIM-001，B3 R-118）：
临时冲击（η×参与率^β×σ）+ 永久冲击（γ×sqrt(参与率)×σ 默认档）参数化 +
冲击衰减曲线（按成交节奏分段）+ 基于分钟成交额的参数估计器 +
冲击成本真源输出。纯内存确定性，不触网。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.execution_simulation.almgren_chriss_impact_model",
    reason="almgren_chriss_impact_model not importable",
)

from zephyr.execution_simulation.almgren_chriss_impact_model import (  # noqa: E402
    AlmgrenChrissError,
    AlmgrenChrissImpactModel,
    ImpactParams,
    MinuteBar,
    ScheduleType,
)

_PARAMS = ImpactParams(eta=0.1, beta=1.0, gamma=0.05, sigma=0.02)


def _model(**kw) -> AlmgrenChrissImpactModel:
    kw.setdefault("params", _PARAMS)
    return AlmgrenChrissImpactModel(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 包门面（守卫式 import）
# ──────────────────────────────────────────────────────────────────────────────


class TestPackageFacade:
    def test_facade_exports(self) -> None:
        import zephyr.execution_simulation as pkg

        assert pkg.AlmgrenChrissImpactModel is AlmgrenChrissImpactModel
        assert "AlmgrenChrissError" in pkg.__all__


# ──────────────────────────────────────────────────────────────────────────────
# 参数
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactParams:
    def test_default_params_valid(self) -> None:
        model = AlmgrenChrissImpactModel()
        assert model.params.eta == 0.1
        assert model.params.permanent_exponent == 0.5  # 默认档 sqrt

    @pytest.mark.parametrize(
        "kw",
        [
            {"eta": -0.1},
            {"beta": 0.0},
            {"gamma": -1.0},
            {"sigma": -0.01},
            {"permanent_exponent": 0.0},
        ],
    )
    def test_invalid_params_raise(self, kw: dict) -> None:
        base = {"eta": 0.1, "beta": 1.0, "gamma": 0.05, "sigma": 0.02}
        base.update(kw)
        with pytest.raises(AlmgrenChrissError):
            ImpactParams(**base)

    def test_invalid_decay_lambda_raises(self) -> None:
        with pytest.raises(AlmgrenChrissError):
            _model(decay_lambda=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 冲击原子
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactAtoms:
    def test_temporary_formula(self) -> None:
        # η × p^β × σ = 0.1 × 0.1 × 0.02
        assert _model().temporary_impact(0.1) == pytest.approx(2e-4)

    def test_temporary_beta_exponent(self) -> None:
        model = _model(params=ImpactParams(eta=0.1, beta=2.0, gamma=0.05, sigma=0.02))
        assert model.temporary_impact(0.1) == pytest.approx(0.1 * 0.01 * 0.02)

    def test_temporary_zero_participation(self) -> None:
        assert _model().temporary_impact(0.0) == 0.0
        assert _model().permanent_impact(0.0) == 0.0

    def test_participation_out_of_range_raises(self) -> None:
        model = _model()
        with pytest.raises(AlmgrenChrissError):
            model.temporary_impact(-0.1)
        with pytest.raises(AlmgrenChrissError):
            model.permanent_impact(1.1)
        with pytest.raises(AlmgrenChrissError):
            model.temporary_impact("x")

    def test_permanent_default_sqrt(self) -> None:
        # γ × √p × σ = 0.05 × 0.3 × 0.02（p=0.09）
        assert _model().permanent_impact(0.09) == pytest.approx(3e-4)

    def test_permanent_custom_exponent(self) -> None:
        model = _model(
            params=ImpactParams(
                eta=0.1,
                beta=1.0,
                gamma=0.05,
                sigma=0.02,
                permanent_exponent=1.0,
            )
        )
        assert model.permanent_impact(0.1) == pytest.approx(0.05 * 0.1 * 0.02)


# ──────────────────────────────────────────────────────────────────────────────
# 单笔报价（真源输出）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuote:
    def test_quote_aggregates(self) -> None:
        q = _model().quote(order_qty=100, market_volume=1000)
        assert q.participation == pytest.approx(0.1)
        assert q.temporary_impact == pytest.approx(2e-4)
        assert q.permanent_impact == pytest.approx(0.05 * math.sqrt(0.1) * 0.02)
        assert q.total_impact == pytest.approx(q.temporary_impact + q.permanent_impact)
        assert q.cost_bps == pytest.approx(q.total_impact * 1e4)

    def test_quote_invalid_inputs(self) -> None:
        model = _model()
        with pytest.raises(AlmgrenChrissError):
            model.quote(0, 1000)  # 订单量非正
        with pytest.raises(AlmgrenChrissError):
            model.quote(100, 0)  # 市场量非正
        with pytest.raises(AlmgrenChrissError):
            model.quote(2000, 1000)  # 参与率 > 1

    def test_quote_deterministic(self) -> None:
        assert _model().quote(100, 1000) == _model().quote(100, 1000)


# ──────────────────────────────────────────────────────────────────────────────
# 冲击衰减曲线（按成交节奏分段）
# ──────────────────────────────────────────────────────────────────────────────


class TestDecayCurve:
    def test_uniform_two_slices_hand_computed(self) -> None:
        # 订单 200 / 市场 1000，2 段匀速：段市场量 500，段参与率 0.2
        traj = _model().decay_curve(200, 1000, 2, schedule=ScheduleType.UNIFORM)
        assert [p.fraction for p in traj.points] == [0.5, 0.5]
        assert all(p.participation == pytest.approx(0.2) for p in traj.points)
        temp = 0.1 * 0.2 * 0.02  # 4e-4
        perm = 0.05 * math.sqrt(0.2) * 0.02  # 4.47213595e-4
        p0, p1 = traj.points
        assert p0.temporary == pytest.approx(temp)
        assert p0.residual_temporary == pytest.approx(temp)
        assert p0.effective_permanent == pytest.approx(0.5 * perm)
        assert p0.segment_cost == pytest.approx(0.5 * perm + temp)
        assert p1.residual_temporary == pytest.approx(temp + 0.5 * temp)  # λ=0.5 几何衰减
        assert p1.effective_permanent == pytest.approx(perm + 0.5 * perm)
        assert traj.total_cost == pytest.approx(0.5 * p0.segment_cost + 0.5 * p1.segment_cost)
        assert traj.total_cost_bps == pytest.approx(traj.total_cost * 1e4)

    def test_front_fractions_descending(self) -> None:
        traj = _model().decay_curve(300, 3000, 3, schedule=ScheduleType.FRONT)
        fracs = [p.fraction for p in traj.points]
        assert fracs[0] > fracs[1] > fracs[2]
        assert sum(fracs) == pytest.approx(1.0)

    def test_back_fractions_ascending(self) -> None:
        traj = _model().decay_curve(300, 3000, 3, schedule=ScheduleType.BACK)
        fracs = [p.fraction for p in traj.points]
        assert fracs[0] < fracs[1] < fracs[2]
        assert sum(fracs) == pytest.approx(1.0)

    def test_residual_decay_lambda_bounds(self) -> None:
        # λ=0：临时冲击不残留（residual=本段 temp）；λ=1：全额累积
        traj0 = _model(decay_lambda=0.0).decay_curve(200, 1000, 2)
        assert traj0.points[1].residual_temporary == pytest.approx(traj0.points[1].temporary)
        traj1 = _model(decay_lambda=1.0).decay_curve(200, 1000, 2)
        assert traj1.points[1].residual_temporary == pytest.approx(2.0 * traj1.points[1].temporary)

    def test_schedule_changes_total_cost(self) -> None:
        model = _model()
        totals = {s: model.decay_curve(300, 3000, 3, schedule=s).total_cost for s in ScheduleType}
        assert len(set(totals.values())) == 3  # 节奏影响成本（前重→高参与率早段）

    def test_curve_invalid_inputs(self) -> None:
        model = _model()
        with pytest.raises(AlmgrenChrissError):
            model.decay_curve(100, 1000, 2, schedule="uniform")  # 字符串非枚举
        with pytest.raises(AlmgrenChrissError):
            model.decay_curve(100, 1000, 0)  # slices 非正
        with pytest.raises(AlmgrenChrissError):
            model.decay_curve(2000, 1000, 2)  # 参与率 > 1
        with pytest.raises(AlmgrenChrissError):
            model.decay_curve(0, 1000, 2)  # 订单量非正


# ──────────────────────────────────────────────────────────────────────────────
# 参数估计器（基于分钟成交额）
# ──────────────────────────────────────────────────────────────────────────────


class TestEstimateParams:
    _BARS = [MinuteBar(minute=f"m{i:03d}", dollar_volume=1e6, range_pct=0.001) for i in range(240)]

    def test_estimate_calibration(self) -> None:
        params = AlmgrenChrissImpactModel.estimate_params(self._BARS)
        sigma = 0.001 * math.sqrt(240)
        assert params.sigma == pytest.approx(sigma)
        # η 校准：临时冲击(0.10) = mean(range_pct)
        assert params.eta == pytest.approx(0.001 / (0.10 * sigma))
        assert params.gamma == pytest.approx(0.5 * params.eta)  # gamma_ratio 默认 0.5
        assert params.beta == 1.0
        # 估计参数回代：参考参与率下临时冲击恰为一个分钟波幅
        model = AlmgrenChrissImpactModel(params=params)
        assert model.temporary_impact(0.10) == pytest.approx(0.001)

    def test_estimate_custom_hyperparams(self) -> None:
        params = AlmgrenChrissImpactModel.estimate_params(
            self._BARS,
            beta=2.0,
            gamma_ratio=0.3,
            reference_participation=0.2,
        )
        sigma = 0.001 * math.sqrt(240)
        assert params.eta == pytest.approx(0.001 / (0.2**2.0 * sigma))
        assert params.gamma == pytest.approx(0.3 * params.eta)

    def test_estimate_invalid_inputs(self) -> None:
        with pytest.raises(AlmgrenChrissError):
            AlmgrenChrissImpactModel.estimate_params([])  # 空
        with pytest.raises(AlmgrenChrissError):
            AlmgrenChrissImpactModel.estimate_params(
                [MinuteBar(minute="m1", dollar_volume=0.0, range_pct=0.001)]
            )  # 成交额非正
        with pytest.raises(AlmgrenChrissError):
            AlmgrenChrissImpactModel.estimate_params(
                [MinuteBar(minute="m1", dollar_volume=1e6, range_pct=-0.1)]
            )  # 波幅为负
        with pytest.raises(AlmgrenChrissError):
            AlmgrenChrissImpactModel.estimate_params(
                [MinuteBar(minute="m1", dollar_volume=1e6, range_pct=0.0)]
            )  # 全零波幅 → σ=0 无法校准

    def test_estimate_deterministic(self) -> None:
        p1 = AlmgrenChrissImpactModel.estimate_params(self._BARS)
        p2 = AlmgrenChrissImpactModel.estimate_params(self._BARS)
        assert p1 == p2
