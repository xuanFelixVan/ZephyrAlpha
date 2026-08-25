# [A_test] module_id: MOD-SIG-098 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-098 | docs/03_modules/_domain_signal/sector_momentum_persistence/blueprint.md
# [MODULE] tests.signal_ashare.test_sector_momentum_persistence
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""动量层级与板块持续性模型（MOD-SIG-098，B10-01367）施工验证测试。

覆盖：
- 五维持续分：MPS（正收益日占比+persistent 标记）/资金流持续性（064 F3 同口径）/
  梯队稳定性 CV 查表/板块-指数共振 Pearson/分歧恢复速度查表；
- 合成：默认权重加权×100；缺维腿重归一；全腿缺 → composite=None+degraded；
- 市场动量广度：>60% 主线/<30% 投机/其间 balanced；空列表 fail-closed；
- fail-closed：不等长/短窗/非有限/负梯队高度/非法配置（权重和≠1）→ ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.sector_momentum_persistence import (
    MomentumPersistenceConfig,
    SectorMomentumInput,
    SectorMomentumPersistence,
)


def _engine() -> SectorMomentumPersistence:
    return SectorMomentumPersistence(MomentumPersistenceConfig())


def _sector(
    code: str = "880001",
    returns: tuple[float, ...] = (0.01,) * 20,
    inflows: tuple[float, ...] = (100.0,) * 20,
    ladder: tuple[int, ...] = (3,) * 20,
    dist: dict[int, int] | None = None,
) -> SectorMomentumInput:
    return SectorMomentumInput(
        sector_code=code,
        daily_returns=returns,
        fund_net_inflows=inflows,
        ladder_top_heights=ladder,
        ladder_distribution=dist if dist is not None else {1: 5, 2: 3, 3: 1},
    )


class TestConfigValidation:
    def test_default_config_ok(self) -> None:
        MomentumPersistenceConfig()

    def test_weight_sum_must_be_one(self) -> None:
        with pytest.raises(ValueError):
            MomentumPersistenceConfig(
                weight_mps=0.5,
                weight_fund=0.5,
                weight_ladder=0.5,
                weight_resonance=0.5,
                weight_recovery=0.5,
            )

    @pytest.mark.parametrize(
        "field,value",
        [
            ("min_window", 4),
            ("mps_persistent_threshold", 0.0),
            ("mps_persistent_threshold", 1.0),
            ("fund_sustain_days", 0),
            ("ladder_cv_stable", 0.0),
            ("resonance_threshold", 0.0),
            ("divergence_threshold", 0.0),
            ("breadth_mainline", 0.2),
            ("breadth_speculative", 0.6),
            ("weight_mps", -0.1),
        ],
    )
    def test_invalid_config_raises(self, field: str, value: float) -> None:
        with pytest.raises(ValueError):
            MomentumPersistenceConfig(**{field: value})


class TestScoreSector:
    def test_perfect_persistent_sector(self) -> None:
        # 全正收益+全正流入+梯队恒定 3 板+与指数完全同步（板块=1.25×指数）+无分歧
        idx = (0.008, 0.016, 0.012, 0.004) * 5
        returns = (0.010, 0.020, 0.015, 0.005) * 5
        score = _engine().score_sector(_sector(returns=returns), idx)
        assert score.mps == pytest.approx(1.0)
        assert score.mps_persistent is True
        assert score.fund_score == pytest.approx(1.0)
        assert score.fund_streak_days == 20
        assert score.ladder_cv == pytest.approx(0.0)
        assert score.ladder_stability_score == pytest.approx(1.0)
        assert score.resonance == pytest.approx(1.0)
        assert score.recovery_days is None  # 窗内无分歧 → 该腿降级
        assert score.recovery_score is None
        # 恢复腿缺维 → 按其余四腿权重 0.9 重归一，五维全 1 → 100
        assert score.composite_score == pytest.approx(100.0)
        assert score.degraded is False

    def test_weak_sector_low_scores(self) -> None:
        returns = (-0.01,) * 20
        inflows = (-50.0,) * 20
        ladder = (0,) * 20  # 零涨停 → 梯队腿降级
        idx = (0.005,) * 20
        score = _engine().score_sector(
            _sector(returns=returns, inflows=inflows, ladder=ladder), idx
        )
        assert score.mps == pytest.approx(0.0)
        assert score.mps_persistent is False
        assert score.fund_score == pytest.approx(0.0)
        assert score.fund_streak_days == 0
        assert score.ladder_stability_score is None  # μ=0 降级
        # 收益恒定 → 板块零方差 → 共振 None
        assert score.resonance is None
        # 日日 -1% ≤ -2%? 否（-1%>-2%）→ 无分歧腿
        assert score.recovery_days is None
        assert score.composite_score == pytest.approx(0.0)

    def test_ladder_cv_lookup(self) -> None:
        # 高度交替 1/5 → μ=3, σ=2, CV=0.667 → 0.4 档
        ladder = (1, 5) * 10
        score = _engine().score_sector(_sector(ladder=ladder), (0.008,) * 20)
        assert score.ladder_cv == pytest.approx(2 / 3, abs=1e-6)
        assert score.ladder_stability_score == pytest.approx(0.4)

    def test_recovery_speed_lookup(self) -> None:
        # 第 15 日（索引 14）分歧 -3%，其后 2 日收复 → recovery_days=2 → 0.8
        returns = [0.01] * 20
        returns[14] = -0.03
        returns[15] = 0.015
        returns[16] = 0.02  # 累计 -0.03+0.015+0.02=+0.005 ≥0 → 2 日收复
        score = _engine().score_sector(
            _sector(returns=tuple(returns)), (0.008,) * 20
        )
        assert score.recovery_days == 2
        assert score.recovery_score == pytest.approx(0.8)

    def test_recovery_unresolved(self) -> None:
        # 末日分歧 -3%，无后续收复窗口 → 未收复 → 0.1
        returns = [0.01] * 19 + [-0.03]
        score = _engine().score_sector(
            _sector(returns=tuple(returns)), (0.008,) * 20
        )
        assert score.recovery_days is None
        assert score.recovery_score == pytest.approx(0.1)

    def test_fund_partial_streak(self) -> None:
        # 尾部连续 2 日正流入，正流入占比 15/20=0.75
        inflows = tuple([100.0] * 13 + [-10.0] * 5 + [100.0] * 2)
        score = _engine().score_sector(_sector(inflows=inflows), (0.008,) * 20)
        assert score.fund_streak_days == 2
        # 0.6×0.75 + 0.4×min(2/3,1) = 0.45 + 0.2667
        assert score.fund_score == pytest.approx(0.6 * 0.75 + 0.4 * (2 / 3))

    def test_input_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().score_sector(
                _sector(returns=(0.01,) * 19), (0.008,) * 20
            )

    def test_short_window_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().score_sector(_sector(returns=(0.01,) * 9), (0.008,) * 9)

    def test_non_finite_raises(self) -> None:
        bad = (0.01,) * 19 + (float("nan"),)
        with pytest.raises(ValueError):
            _engine().score_sector(_sector(returns=bad), (0.008,) * 20)

    def test_negative_ladder_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().score_sector(
                _sector(ladder=(3,) * 19 + (-1,)), (0.008,) * 20
            )


class TestMarketBreadth:
    def test_mainline_regime(self) -> None:
        sectors = [_sector(code=f"c{i}", returns=(0.01,) * 20) for i in range(7)]
        sectors += [_sector(code=f"n{i}", returns=(-0.01,) * 20) for i in range(3)]
        regime = _engine().market_breadth(sectors)
        assert regime.breadth == pytest.approx(0.7)
        assert regime.regime == "mainline"
        assert regime.mainline_flag is True
        assert regime.speculative_flag is False

    def test_speculative_regime(self) -> None:
        sectors = [_sector(code=f"n{i}", returns=(-0.01,) * 20) for i in range(8)]
        sectors += [_sector(code=f"c{i}", returns=(0.01,) * 20) for i in range(2)]
        regime = _engine().market_breadth(sectors)
        assert regime.breadth == pytest.approx(0.2)
        assert regime.regime == "speculative"
        assert regime.speculative_flag is True

    def test_balanced_regime(self) -> None:
        sectors = [_sector(code=f"c{i}", returns=(0.01,) * 20) for i in range(5)]
        sectors += [_sector(code=f"n{i}", returns=(-0.01,) * 20) for i in range(5)]
        regime = _engine().market_breadth(sectors)
        assert regime.regime == "balanced"
        assert regime.mainline_flag is False
        assert regime.speculative_flag is False

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().market_breadth([])


class TestContract:
    def test_frozen_and_json_serializable(self) -> None:
        score = _engine().score_sector(_sector(), (0.008,) * 20)
        with pytest.raises(dataclasses.FrozenInstanceError):
            score.mps = 0.0  # type: ignore[misc]
        json.dumps(score.to_dict())
        regime = _engine().market_breadth([_sector()])
        json.dumps(regime.to_dict())
