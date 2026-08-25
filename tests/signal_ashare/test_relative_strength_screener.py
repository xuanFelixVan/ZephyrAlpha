# [A_test] module_id: MOD-SIG-096 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-096 | docs/03_modules/_domain_signal/relative_strength_screener/blueprint.md
# [MODULE] tests.signal_ashare.test_relative_strength_screener
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""多维度相对强弱筛选（MOD-SIG-096，B10-01365）施工验证测试。

覆盖：
- 区间 RS：跑赢基准→>50、跑输→<50；
- 结构强弱：完美多头排列→100、完全反排→0；
- 52 周新高接近度：0.98→near_high_52w=True（>0.95）、0.5→False；
- 放量突破确认：新高+量≥1.5×均量→confirmed/100 分；新高无量→不 confirmed；
- 合成：强股>弱股（单调）；权重校验；
- 批量 rank 排序正确；
- 降级：历史不足 252 根→degraded=True 仍计算（显式不静默）；
- fail-closed：空/不等长/非正价格/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.relative_strength_screener import (
    RelativeStrengthConfig,
    RelativeStrengthScreener,
)


def _screener(**kw) -> RelativeStrengthScreener:
    return RelativeStrengthScreener(RelativeStrengthConfig(**kw))


def _flat_benchmark(n: int = 260) -> pd.Series:
    return pd.Series([100.0] * n)


def _strong_stock(n: int = 260) -> tuple[pd.Series, pd.Series, pd.Series]:
    # 多头排列缓涨 260 根：close≈均线多头，末根未创新高
    close = pd.Series([100.0 + 0.15 * i for i in range(n)])
    high = close * 1.01
    volume = pd.Series([1000.0] * n)
    return close, high, volume


class TestDimensions:
    def test_interval_rs_outperform_above_50(self) -> None:
        close, high, volume = _strong_stock()
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.rs_interval_score > 50.0

    def test_interval_rs_underperform_below_50(self) -> None:
        n = 260
        close = pd.Series([140.0 - 0.15 * i for i in range(n)])  # 阴跌
        high = close * 1.01
        volume = pd.Series([1000.0] * n)
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.rs_interval_score < 50.0

    def test_structural_perfect_alignment_100(self) -> None:
        close, high, volume = _strong_stock()
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.structural_score == pytest.approx(100.0)

    def test_structural_inverse_alignment_zero(self) -> None:
        n = 260
        close = pd.Series([200.0 - 0.3 * i for i in range(n)])  # 持续空头排列
        high = close * 1.005
        volume = pd.Series([1000.0] * n)
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.structural_score == pytest.approx(0.0)

    def test_high_52w_proximity_flag(self) -> None:
        n = 260
        # 前段冲高 120，后段回落，现价为前高的 98%（>0.95 → near_high）
        base = [100.0] * 130 + [120.0] * 5 + [117.6] * (n - 135)
        close = pd.Series(base)
        high = pd.Series([max(100.0, c * 1.001) for c in base])
        volume = pd.Series([1000.0] * n)
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.high_52w_proximity == pytest.approx(117.6 / 120.12, abs=0.02)
        assert s.near_high_52w is True

    def test_high_52w_proximity_low(self) -> None:
        n = 260
        base = [100.0] * 130 + [200.0] * 5 + [100.0] * (n - 135)
        close = pd.Series(base)
        high = pd.Series(base) * 1.001
        volume = pd.Series([1000.0] * n)
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.high_52w_proximity == pytest.approx(0.5, abs=0.01)
        assert s.near_high_52w is False

    def test_volume_breakout_confirmed(self) -> None:
        n = 260
        base = [100.0 + 0.05 * i for i in range(n - 1)]
        breakout_close = max(base) * 1.02
        close = pd.Series(base + [breakout_close])
        high = close * 1.001
        volume = pd.Series([1000.0] * (n - 1) + [2500.0])  # 2.5×均量
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.breakout_confirmed is True
        assert s.breakout_score == pytest.approx(100.0)

    def test_breakout_without_volume_not_confirmed(self) -> None:
        n = 260
        base = [100.0 + 0.05 * i for i in range(n - 1)]
        breakout_close = max(base) * 1.02
        close = pd.Series(base + [breakout_close])
        high = close * 1.001
        volume = pd.Series([1000.0] * n)  # 无量
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert s.breakout_confirmed is False
        assert 0.0 < s.breakout_score < 100.0


class TestComposite:
    def test_strong_beats_weak(self) -> None:
        c1, h1, v1 = _strong_stock()
        strong = _screener().score("S", c1, h1, v1, _flat_benchmark())
        n = 260
        c2 = pd.Series([140.0 - 0.15 * i for i in range(n)])
        weak = _screener().score("W", c2, c2 * 1.01, pd.Series([1000.0] * n), _flat_benchmark())
        assert 0.0 <= strong.composite_score <= 100.0
        assert strong.composite_score > weak.composite_score

    def test_rank_orders_desc(self) -> None:
        c1, h1, v1 = _strong_stock()
        n = 260
        c2 = pd.Series([140.0 - 0.15 * i for i in range(n)])
        bars = {
            "strong": (c1, h1, v1),
            "weak": (c2, c2 * 1.01, pd.Series([1000.0] * n)),
        }
        ranked = _screener().rank(bars, _flat_benchmark())
        assert [r.symbol for r in ranked] == ["strong", "weak"]
        assert ranked[0].composite_score >= ranked[1].composite_score

    def test_degraded_on_short_history(self) -> None:
        n = 120  # <252
        close = pd.Series([100.0 + 0.1 * i for i in range(n)])
        s = _screener().score("X", close, close * 1.01, pd.Series([1000.0] * n), _flat_benchmark(n))
        assert s.degraded is True
        assert 0.0 <= s.composite_score <= 100.0


class TestFailClosed:
    def test_empty_and_unequal_and_nonpositive(self) -> None:
        d = _screener()
        with pytest.raises(ValueError):
            d.score("X", pd.Series([], dtype=float), pd.Series([], dtype=float),
                    pd.Series([], dtype=float), _flat_benchmark())
        with pytest.raises(ValueError):
            d.score("X", pd.Series([1.0, 2.0]), pd.Series([1.0]),
                    pd.Series([1.0, 1.0]), pd.Series([1.0, 1.0]))
        with pytest.raises(ValueError):
            d.score("X", pd.Series([0.0] * 30), pd.Series([1.0] * 30),
                    pd.Series([1.0] * 30), pd.Series([1.0] * 30))

    def test_config_validation(self) -> None:
        with pytest.raises(ValueError):
            RelativeStrengthConfig(weight_interval_rs=0.9)  # 权重和≠1
        with pytest.raises(ValueError):
            RelativeStrengthConfig(near_high_threshold=1.5)
        with pytest.raises(ValueError):
            RelativeStrengthConfig(breakout_volume_multiple=0.5)
        with pytest.raises(ValueError):
            RelativeStrengthConfig(interval_windows=(20, 60))  # 须与权重等长


class TestContract:
    def test_score_frozen_and_json_serializable(self) -> None:
        close, high, volume = _strong_stock()
        s = _screener().score("X", close, high, volume, _flat_benchmark())
        assert dataclasses.is_dataclass(s)
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.composite_score = 0.0  # type: ignore[misc]
        json.dumps(s.to_dict())
