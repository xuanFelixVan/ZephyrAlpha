# [A_test] module_id: MOD-SIG-073 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-073 | 待统筹登记 | 缺口总账 GAP-F-39 行
# [MODULE] tests.signal_ashare.test_stock_signal_strength
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""个股级信号强度合成器（MOD-SIG-073，GAP-F-39）施工验证测试。

覆盖：
- 五维明细齐备且各维 ∈ [0,100]；合成 0~100 加权正确（含权重覆盖=单维直通）；
- 方向合理性：放量上行合成偏强、放量下行合成偏弱；
- AI NLP 维注入/缺省（缺省剔除并权重重归一+留痕）；非法 NLP 分拒；
- fail-closed：根数不足/负价/负量/负权重/全零权重；
- 契约：frozen、to_dict JSON 可序列化、同输入同输出（纯函数确定性）。
全程内存合成数据，无 DB 无 LLM。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from zephyr.signal_ashare.stock_signal_strength import (
    DIMENSION_KEYS,
    StrengthConfig,
    StrengthResult,
    compose_strength,
)


def _series(n: int = 80, drift: float = 0.004, vol_base: float = 1000.0, vol_growth: float = 1.0):
    rng = np.random.default_rng(11)
    rets = drift + 0.01 * rng.standard_normal(n)
    closes = 100.0 * np.exp(np.cumsum(rets))
    volumes = vol_base * np.linspace(1.0, vol_growth, n)
    return closes.tolist(), volumes.tolist()


class TestCompose:
    def test_five_dimensions_present(self) -> None:
        closes, volumes = _series()
        res = compose_strength(closes, volumes, ai_nlp_score=65.0)
        assert isinstance(res, StrengthResult)
        assert [d.key for d in res.dimensions] == list(DIMENSION_KEYS)
        for d in res.dimensions:
            assert 0.0 <= d.score <= 100.0
        assert 0.0 <= res.strength <= 100.0
        assert res.ai_nlp_included is True

    def test_uptrend_volume_up_scores_high(self) -> None:
        closes, volumes = _series(drift=0.006, vol_growth=2.0)
        res = compose_strength(closes, volumes)
        assert res.strength > 60.0
        assert res.label in ("偏强", "强")

    def test_downtrend_volume_up_scores_low(self) -> None:
        closes, volumes = _series(drift=-0.006, vol_growth=2.0)
        res = compose_strength(closes, volumes)
        assert res.strength < 40.0
        assert res.label in ("偏弱", "弱")

    def test_ai_nlp_none_excluded_and_renormalized(self) -> None:
        closes, volumes = _series()
        res = compose_strength(closes, volumes, ai_nlp_score=None)
        assert res.ai_nlp_included is False
        dims = {d.key: d for d in res.dimensions}
        nlp = dims["ai_nlp"]
        assert nlp.score == 0.0 and nlp.available is False
        expected = (
            res.config.w_macd * dims["macd"].score
            + res.config.w_rsi * dims["rsi"].score
            + res.config.w_volume * dims["volume"].score
            + res.config.w_ma * dims["ma"].score
        ) / (res.config.w_macd + res.config.w_rsi + res.config.w_volume + res.config.w_ma)
        assert res.strength == pytest.approx(expected, abs=0.01)  # 合成分保留两位小数
        assert any("AI NLP" in n for n in res.notes)

    def test_weight_override_single_dimension_passthrough(self) -> None:
        closes, volumes = _series()
        cfg = StrengthConfig(w_macd=1.0, w_rsi=0.0, w_volume=0.0, w_ma=0.0, w_ai_nlp=0.0)
        res = compose_strength(closes, volumes, config=cfg)
        dims = {d.key: d for d in res.dimensions}
        assert res.strength == pytest.approx(dims["macd"].score, abs=1e-6)

    def test_deterministic(self) -> None:
        closes, volumes = _series()
        a = compose_strength(closes, volumes, ai_nlp_score=55.0)
        b = compose_strength(closes, volumes, ai_nlp_score=55.0)
        assert a.to_dict() == b.to_dict()


class TestValidation:
    def test_short_bars_rejected(self) -> None:
        closes, volumes = _series(n=20)
        with pytest.raises(ValueError, match="根数"):
            compose_strength(closes, volumes)

    def test_length_mismatch_rejected(self) -> None:
        closes, volumes = _series()
        with pytest.raises(ValueError, match="等长"):
            compose_strength(closes, volumes[:-1])

    def test_non_positive_close_rejected(self) -> None:
        closes, volumes = _series()
        closes[30] = -1.0
        with pytest.raises(ValueError, match="收盘"):
            compose_strength(closes, volumes)

    def test_negative_volume_rejected(self) -> None:
        closes, volumes = _series()
        volumes[10] = -5.0
        with pytest.raises(ValueError, match="量"):
            compose_strength(closes, volumes)

    def test_ai_nlp_out_of_range_rejected(self) -> None:
        closes, volumes = _series()
        with pytest.raises(ValueError, match="ai_nlp_score"):
            compose_strength(closes, volumes, ai_nlp_score=120.0)

    def test_negative_weight_rejected(self) -> None:
        with pytest.raises(ValueError, match="权重"):
            StrengthConfig(w_macd=-0.1)

    def test_all_zero_weights_rejected(self) -> None:
        with pytest.raises(ValueError, match="权重"):
            StrengthConfig(w_macd=0.0, w_rsi=0.0, w_volume=0.0, w_ma=0.0, w_ai_nlp=0.0)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        closes, volumes = _series()
        res = compose_strength(closes, volumes, ai_nlp_score=60.0)
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "strength" in text

    def test_frozen(self) -> None:
        closes, volumes = _series()
        res = compose_strength(closes, volumes)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.strength = 99.0  # type: ignore[misc]
