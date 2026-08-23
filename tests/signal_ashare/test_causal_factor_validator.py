# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/25_multifactor_strategy_detail.md §3.1
# [TTL] permanent
"""因果因子验证器（BM-SEL-02-M，MOD-SIG-054）单元测试——裁定→乘子映射/批量/降级。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.causal_factor_validator import (
    CausalValidatorConfig,
    validate_factor,
    validate_factors,
)
from zephyr.signal_ashare.causal_inference_engine import CausalVerdict


def _causal_pair(n: int = 300, seed: int = 7):
    rng = np.random.default_rng(seed)
    factor = rng.normal(0.0, 1.0, n + 1)
    ret = np.zeros(n + 1)
    ret[1:] = 0.8 * factor[:-1] + rng.normal(0.0, 0.5, n)
    return factor, ret


class TestValidateFactor:
    def test_causal_candidate_boosted(self):
        factor, ret = _causal_pair()
        rep = validate_factor("causal_alpha", factor, ret)
        assert rep.verdict == CausalVerdict.CAUSAL_CANDIDATE
        assert rep.weight_multiplier == pytest.approx(1.2)
        assert rep.degraded is False
        assert rep.n_samples == 300

    def test_spurious_discounted(self):
        """市场共同驱动 → 伪相关 → 降权 0.5。"""
        rng = np.random.default_rng(11)
        n = 300
        driver = np.cumsum(rng.normal(0.0, 0.3, n + 1)) + rng.normal(0, 1, n + 1)
        factor = 0.9 * driver + rng.normal(0.0, 0.05, n + 1)
        ret = np.zeros(n + 1)
        ret[1:] = 0.9 * driver[1:] + rng.normal(0.0, 0.05, n)
        rep = validate_factor("spurious_beta", factor, ret, control_values=driver)
        assert rep.verdict == CausalVerdict.SPURIOUS
        assert rep.weight_multiplier == pytest.approx(0.5)

    def test_insignificant_neutral(self):
        rng = np.random.default_rng(13)
        rep = validate_factor("noise", rng.normal(size=101), rng.normal(size=101), config=CausalValidatorConfig(ic_floor=0.15))
        assert rep.verdict == CausalVerdict.INSIGNIFICANT
        assert rep.weight_multiplier == pytest.approx(1.0)

    def test_insufficient_samples_degraded(self):
        rep = validate_factor("short", [1.0] * 10, [0.1] * 10)
        assert rep.degraded is True
        assert rep.verdict is None
        assert rep.weight_multiplier == pytest.approx(1.0)

    def test_length_mismatch_degraded_not_raise(self):
        """单因子失败不抛错（批量评估不阻断）。"""
        rep = validate_factor("bad", [1.0] * 50, [0.1] * 40)
        assert rep.degraded is True

    def test_custom_multipliers(self):
        factor, ret = _causal_pair()
        cfg = CausalValidatorConfig(causal_boost=1.5)
        rep = validate_factor("causal_alpha", factor, ret, config=cfg)
        assert rep.weight_multiplier == pytest.approx(1.5)


class TestValidateFactors:
    def test_batch(self):
        factor, ret = _causal_pair()
        rng = np.random.default_rng(13)
        batch = {
            "causal_alpha": (factor, ret),
            "noise": (rng.normal(size=101).tolist(), rng.normal(size=101).tolist()),
            "short": ([1.0] * 5, [0.1] * 5),
        }
        reps = validate_factors(batch, config=CausalValidatorConfig(ic_floor=0.15))
        by_name = {r.factor_name: r for r in reps}
        assert by_name["causal_alpha"].verdict == CausalVerdict.CAUSAL_CANDIDATE
        assert by_name["noise"].verdict == CausalVerdict.INSIGNIFICANT
        assert by_name["short"].degraded is True  # 单因子失败不阻断批量

    def test_empty_batch(self):
        assert validate_factors({}) == []
