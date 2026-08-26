# [BLUEPRINT] MOD-SIG-114 | docs/03_modules/_domain_signal/crowd_game_simulator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-114 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_crowd_game_simulator
# [TESTS] src/zephyr/signal_ashare/crowd_game_simulator.py
"""MOD-SIG-114 单元测试：crowd_game_simulator 群体博弈模拟器。

蓝图验收（B1-00169/CAND-TESTB-031，C2 C-036）：
四类玩家行为规则库 + 合力方向（加权净方向）/分歧度（方向熵）+ 盘后语义 + 推断性质标注。
内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.crowd_game_simulator",
    reason="crowd_game_simulator not importable",
)

from zephyr.signal_ashare.crowd_game_simulator import (  # noqa: E402
    CrowdGameError,
    CrowdGameSimulator,
    PlayerPrior,
    PlayerType,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 0, 0)


def _sim(**kwargs) -> CrowdGameSimulator:
    kwargs.setdefault("clock", lambda: _T0)
    return CrowdGameSimulator(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_invalid_player_type_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            PlayerPrior(
                player_type="INVALID",  # type: ignore[arg-type]
                weight=0.5,
                momentum_bias=0.0,
                sentiment_sensitivity=0.5,
            )

    def test_weight_non_positive_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            PlayerPrior(
                player_type=PlayerType.NORTHBOUND,
                weight=0.0,
                momentum_bias=0.0,
                sentiment_sensitivity=0.5,
            )

    def test_momentum_bias_out_of_range_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            PlayerPrior(
                player_type=PlayerType.NORTHBOUND,
                weight=0.5,
                momentum_bias=1.5,
                sentiment_sensitivity=0.5,
            )

    def test_sentiment_sensitivity_out_of_range_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            PlayerPrior(
                player_type=PlayerType.NORTHBOUND,
                weight=0.5,
                momentum_bias=0.0,
                sentiment_sensitivity=1.5,
            )

    def test_missing_prior_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            _sim(priors={
                PlayerType.NORTHBOUND: PlayerPrior(
                    player_type=PlayerType.NORTHBOUND,
                    weight=0.5,
                    momentum_bias=0.0,
                    sentiment_sensitivity=0.5,
                )
            })

    def test_prior_wrong_type_raises(self) -> None:
        with pytest.raises(CrowdGameError):
            _sim(priors={
                PlayerType.NORTHBOUND: "not-a-prior",  # type: ignore[dict-item]
                PlayerType.PUBLIC_FUND: PlayerPrior(
                    player_type=PlayerType.PUBLIC_FUND,
                    weight=0.5,
                    momentum_bias=0.0,
                    sentiment_sensitivity=0.5,
                ),
                PlayerType.HOT_MONEY: PlayerPrior(
                    player_type=PlayerType.HOT_MONEY,
                    weight=0.5,
                    momentum_bias=0.0,
                    sentiment_sensitivity=0.5,
                ),
                PlayerType.RETAIL: PlayerPrior(
                    player_type=PlayerType.RETAIL,
                    weight=0.5,
                    momentum_bias=0.0,
                    sentiment_sensitivity=0.5,
                ),
            })


# ──────────────────────────────────────────────────────────────────────────────
# 博弈推演
# ──────────────────────────────────────────────────────────────────────────────


class TestSimulate:
    def test_simulate_structure(self) -> None:
        sim = _sim()
        result = sim.simulate(market_momentum=0.3, sentiment_index=0.5)
        assert result.timestamp == _T0
        assert -1.0 <= result.net_direction <= 1.0
        assert 0.0 <= result.direction_entropy <= 1.0
        assert len(result.player_votes) == 4
        assert result.inference is True
        assert result.post_close.is_post_close is True

    def test_player_votes_sorted(self) -> None:
        sim = _sim()
        result = sim.simulate(market_momentum=0.0, sentiment_index=0.0)
        pts = [p for p, _ in result.player_votes]
        assert pts == sorted(PlayerType, key=lambda x: x.value)

    def test_extreme_bullish(self) -> None:
        sim = _sim()
        result = sim.simulate(market_momentum=1.0, sentiment_index=1.0)
        assert result.net_direction > 0.5

    def test_extreme_bearish(self) -> None:
        sim = _sim()
        result = sim.simulate(market_momentum=-1.0, sentiment_index=-1.0)
        assert result.net_direction < -0.5

    def test_entropy_unanimous(self) -> None:
        # 所有玩家同向，熵应为 0
        priors = {
            pt: PlayerPrior(player_type=pt, weight=0.5, momentum_bias=1.0, sentiment_sensitivity=0.0)
            for pt in PlayerType
        }
        sim = _sim(priors=priors)
        result = sim.simulate(market_momentum=0.0, sentiment_index=0.0)
        assert result.direction_entropy == 0.0

    def test_entropy_divergent(self) -> None:
        # 玩家方向极端分散，熵应接近 1
        priors = {
            PlayerType.NORTHBOUND: PlayerPrior(
                player_type=PlayerType.NORTHBOUND, weight=0.5, momentum_bias=-1.0, sentiment_sensitivity=0.0
            ),
            PlayerType.PUBLIC_FUND: PlayerPrior(
                player_type=PlayerType.PUBLIC_FUND, weight=0.5, momentum_bias=-0.5, sentiment_sensitivity=0.0
            ),
            PlayerType.HOT_MONEY: PlayerPrior(
                player_type=PlayerType.HOT_MONEY, weight=0.5, momentum_bias=0.5, sentiment_sensitivity=0.0
            ),
            PlayerType.RETAIL: PlayerPrior(
                player_type=PlayerType.RETAIL, weight=0.5, momentum_bias=1.0, sentiment_sensitivity=0.0
            ),
        }
        sim = _sim(priors=priors)
        result = sim.simulate(market_momentum=0.0, sentiment_index=0.0)
        assert result.direction_entropy > 0.8

    def test_momentum_out_of_range_raises(self) -> None:
        sim = _sim()
        with pytest.raises(CrowdGameError):
            sim.simulate(market_momentum=1.5, sentiment_index=0.0)

    def test_sentiment_out_of_range_raises(self) -> None:
        sim = _sim()
        with pytest.raises(CrowdGameError):
            sim.simulate(market_momentum=0.0, sentiment_index=-1.5)

    def test_post_close_semantics(self) -> None:
        sim = _sim()
        result = sim.simulate(market_momentum=0.0, sentiment_index=0.0, post_close=False, data_as_of="intraday")
        assert result.post_close.is_post_close is False
        assert result.post_close.data_as_of == "intraday"


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        sim = _sim()
        r1 = sim.simulate(market_momentum=0.3, sentiment_index=0.5)
        r2 = sim.simulate(market_momentum=0.3, sentiment_index=0.5)
        assert r1 == r2
