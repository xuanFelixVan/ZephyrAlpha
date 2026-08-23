# [A_test] module_id: MOD-SIG-074 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-074 | 待统筹登记 | 缺口总账 GAP-F-36 行
# [MODULE] tests.signal_ashare.test_mc_path_simulator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""蒙特卡洛路径模拟引擎（MOD-SIG-074，GAP-F-36）施工验证测试。

覆盖：
- GBM/重采样两法：产出结构完整（胜率/90% 置信上下限/逐日分布带），种子可复现；
- 统计合理性：强上行合成序列胜率显著>0.5；恒定价格零波动降级（路径恒平、胜率 0）；
- fail-closed：历史不足/非正价格/非法方法/路径数不足/置信度越界全拒；
- 契约：to_dict JSON 可序列化；frozen 不可变。
全程内存合成数据，无 DB 无网络。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from zephyr.signal_ashare.mc_path_simulator import (
    METHOD_BOOTSTRAP,
    METHOD_GBM,
    MCSimConfig,
    MCSimResult,
    simulate_paths,
)


def _uptrend_closes(n: int = 120) -> list[float]:
    rng = np.random.default_rng(7)
    rets = 0.004 + 0.01 * rng.standard_normal(n - 1)
    return (100.0 * np.exp(np.concatenate([[0.0], np.cumsum(rets)]))).tolist()


def _flat_closes(n: int = 60) -> list[float]:
    return [50.0] * n


class TestGBM:
    def test_result_shape_and_fields(self) -> None:
        res = simulate_paths(_uptrend_closes(), method=METHOD_GBM, config=MCSimConfig(n_paths=500))
        assert res.method == METHOD_GBM
        assert res.horizon == 20
        assert res.n_paths == 500
        assert len(res.band_lower) == len(res.band_median) == len(res.band_upper) == 20
        assert 0.0 <= res.win_rate <= 1.0
        assert res.ci_lower < res.ci_upper
        assert res.start_price > 0

    def test_seed_reproducible(self) -> None:
        cfg = MCSimConfig(n_paths=300, seed=123)
        a = simulate_paths(_uptrend_closes(), method=METHOD_GBM, config=cfg)
        b = simulate_paths(_uptrend_closes(), method=METHOD_GBM, config=cfg)
        assert a.to_dict() == b.to_dict()

    def test_uptrend_high_win_rate(self) -> None:
        res = simulate_paths(_uptrend_closes(), method=METHOD_GBM, config=MCSimConfig(n_paths=1000))
        assert res.win_rate > 0.6
        assert res.terminal_median > res.start_price

    def test_flat_zero_vol_degenerate(self) -> None:
        res = simulate_paths(_flat_closes(), method=METHOD_GBM, config=MCSimConfig(n_paths=300))
        assert res.win_rate == 0.0
        assert res.ci_lower == pytest.approx(50.0)
        assert res.ci_upper == pytest.approx(50.0)
        assert res.annualized_vol == 0.0


class TestBootstrap:
    def test_result_fields(self) -> None:
        res = simulate_paths(_uptrend_closes(), method=METHOD_BOOTSTRAP, config=MCSimConfig(n_paths=500))
        assert res.method == METHOD_BOOTSTRAP
        assert len(res.band_lower) == 20
        assert res.ci_lower < res.ci_upper

    def test_seed_reproducible(self) -> None:
        cfg = MCSimConfig(n_paths=300, seed=9)
        a = simulate_paths(_uptrend_closes(), method=METHOD_BOOTSTRAP, config=cfg)
        b = simulate_paths(_uptrend_closes(), method=METHOD_BOOTSTRAP, config=cfg)
        assert a.to_dict() == b.to_dict()

    def test_uptrend_win_rate(self) -> None:
        res = simulate_paths(_uptrend_closes(), method=METHOD_BOOTSTRAP, config=MCSimConfig(n_paths=1000))
        assert res.win_rate > 0.6

    def test_bands_ordered(self) -> None:
        res = simulate_paths(_uptrend_closes(), method=METHOD_BOOTSTRAP, config=MCSimConfig(n_paths=500))
        for lo, mid, hi in zip(res.band_lower, res.band_median, res.band_upper):
            assert lo <= mid <= hi


class TestValidation:
    def test_short_history_rejected(self) -> None:
        with pytest.raises(ValueError, match="历史"):
            simulate_paths([10.0] * 10)

    def test_non_positive_price_rejected(self) -> None:
        closes = _uptrend_closes()
        closes[50] = 0.0
        with pytest.raises(ValueError, match="价格"):
            simulate_paths(closes)

    def test_non_finite_rejected(self) -> None:
        closes = _uptrend_closes()
        closes[10] = float("nan")
        with pytest.raises(ValueError, match="价格"):
            simulate_paths(closes)

    def test_bad_method_rejected(self) -> None:
        with pytest.raises(ValueError, match="method"):
            simulate_paths(_uptrend_closes(), method="garch")

    def test_too_few_paths_rejected(self) -> None:
        with pytest.raises(ValueError, match="n_paths"):
            simulate_paths(_uptrend_closes(), config=MCSimConfig(n_paths=50))

    def test_bad_horizon_rejected(self) -> None:
        with pytest.raises(ValueError, match="horizon"):
            simulate_paths(_uptrend_closes(), config=MCSimConfig(horizon=0))

    def test_bad_ci_level_rejected(self) -> None:
        with pytest.raises(ValueError, match="ci_level"):
            simulate_paths(_uptrend_closes(), config=MCSimConfig(ci_level=1.5))


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = simulate_paths(_uptrend_closes(), config=MCSimConfig(n_paths=200))
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "win_rate" in text

    def test_frozen(self) -> None:
        res = simulate_paths(_uptrend_closes(), config=MCSimConfig(n_paths=200))
        assert isinstance(res, MCSimResult)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.win_rate = 0.5  # type: ignore[misc]
