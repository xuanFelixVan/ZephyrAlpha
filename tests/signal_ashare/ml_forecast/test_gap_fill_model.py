# [A_test] module_id: MOD-SIG-092 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-092 | docs/03_modules/_domain_signal/gap_fill_model/blueprint.md
# [MODULE] tests.signal_ashare.test_gap_fill_model
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""缺口回补概率模型（MOD-SIG-092，B10-01359）施工验证测试。

覆盖：
- 分级：ATR 标准化缺口四档封闭集（Tiny/Small/Medium/Large）边界归属；
- 查表：默认回补概率（Tiny=77.8%/Large=8.2%）+ 部分回补分布归一；
- MAE 止损参考：方向正确（上缺口止损在开盘价上方，下缺口反之）；
- detect：合成序列缺口识别、当日回补标记（high/low）、min_gap_atr 过滤；
- fail-closed：非法 ATR/价格/配置（概率越界、分布不归一、阈值非递增）→ ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pandas as pd
import pytest

from zephyr.signal_ashare.gap_fill_model import (
    GapFillConfig,
    GapFillProbabilityModel,
    GapGrade,
)


def _model() -> GapFillProbabilityModel:
    return GapFillProbabilityModel(GapFillConfig())


class TestGrade:
    def test_tiny_below_threshold(self) -> None:
        assert _model().classify(0.29) is GapGrade.TINY

    def test_boundary_belongs_to_upper_grade(self) -> None:
        m = _model()
        assert m.classify(0.30) is GapGrade.SMALL
        assert m.classify(0.60) is GapGrade.MEDIUM
        assert m.classify(1.20) is GapGrade.LARGE

    def test_mid_values(self) -> None:
        m = _model()
        assert m.classify(0.45) is GapGrade.SMALL
        assert m.classify(0.90) is GapGrade.MEDIUM
        assert m.classify(2.50) is GapGrade.LARGE

    def test_negative_input_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            _model().classify(-0.1)


class TestForecast:
    def test_default_fill_probability_table(self) -> None:
        m = _model()
        up = m.forecast(direction="up", gap_size_atr=0.2, prev_close=10.0, open_price=10.2)
        large = m.forecast(direction="up", gap_size_atr=1.5, prev_close=10.0, open_price=11.5)
        assert up.fill_probability == pytest.approx(0.778)
        assert large.fill_probability == pytest.approx(0.082)
        assert up.fill_probability > large.fill_probability

    def test_partial_fill_distribution_normalized(self) -> None:
        f = _model().forecast(direction="down", gap_size_atr=0.4, prev_close=10.0, open_price=9.6)
        assert set(f.partial_fill_distribution) == {0.25, 0.5, 0.75, 1.0}
        assert sum(f.partial_fill_distribution.values()) == pytest.approx(1.0)

    def test_expected_fill_fraction_in_range(self) -> None:
        f = _model().forecast(direction="up", gap_size_atr=0.2, prev_close=10.0, open_price=10.2)
        assert 0.0 < f.expected_fill_fraction <= 1.0

    def test_mae_stop_direction_up_gap(self) -> None:
        # 上缺口做空回补策略：止损参考在开盘价上方（逆向不利 excursion）
        f = _model().forecast(direction="up", gap_size_atr=0.5, prev_close=10.0, open_price=10.5)
        assert f.mae_stop_price > f.open_price

    def test_mae_stop_direction_down_gap(self) -> None:
        f = _model().forecast(direction="down", gap_size_atr=0.5, prev_close=10.0, open_price=9.5)
        assert f.mae_stop_price < f.open_price

    def test_mae_stop_distance_scales_with_gap(self) -> None:
        m = _model()
        small = m.forecast(direction="up", gap_size_atr=0.4, prev_close=10.0, open_price=10.4)
        big = m.forecast(direction="up", gap_size_atr=1.0, prev_close=10.0, open_price=11.0)
        d_small = small.mae_stop_price - small.open_price
        d_big = big.mae_stop_price - big.open_price
        assert d_big > d_small

    def test_expected_fill_bars_positive(self) -> None:
        f = _model().forecast(direction="up", gap_size_atr=0.2, prev_close=10.0, open_price=10.2)
        assert f.expected_fill_bars >= 1

    def test_invalid_inputs_fail_closed(self) -> None:
        m = _model()
        with pytest.raises(ValueError):
            m.forecast(direction="sideways", gap_size_atr=0.2, prev_close=10.0, open_price=10.2)
        with pytest.raises(ValueError):
            m.forecast(direction="up", gap_size_atr=-0.2, prev_close=10.0, open_price=10.2)
        with pytest.raises(ValueError):
            m.forecast(direction="up", gap_size_atr=0.2, prev_close=0.0, open_price=10.2)
        with pytest.raises(ValueError):
            m.forecast(direction="up", gap_size_atr=0.2, prev_close=10.0, open_price=-1.0)


class TestDetect:
    def _df(self) -> pd.DataFrame:
        # 5 根K线：第 3 根明显上缺口（open 11.0 vs prev close 10.0，ATR=1.0）
        return pd.DataFrame(
            {
                "open": [10.0, 10.1, 11.0, 10.8, 10.9],
                "high": [10.2, 10.3, 11.2, 11.0, 11.0],
                "low": [9.9, 10.0, 10.5, 10.6, 10.7],
                "close": [10.1, 10.0, 10.8, 10.9, 10.95],
            }
        )

    def test_detect_finds_gap_with_grade(self) -> None:
        atr = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0])
        events = _model().detect(self._df(), atr)
        assert len(events) == 1
        row = events.iloc[0]
        assert row["direction"] == "up"
        assert row["gap_size_atr"] == pytest.approx(1.0)
        assert row["grade"] == GapGrade.MEDIUM.value

    def test_detect_marks_same_day_fill(self) -> None:
        # 上缺口当日 low 回落到 prev_close 之下 → 当日回补
        df = self._df()
        df.loc[2, "low"] = 9.95
        atr = pd.Series([1.0] * 5)
        events = _model().detect(df, atr)
        assert bool(events.iloc[0]["filled_same_day"]) is True

    def test_detect_min_gap_filter(self) -> None:
        atr = pd.Series([1.0] * 5)
        events = _model().detect(self._df(), atr, min_gap_atr=1.5)
        assert events.empty

    def test_detect_requires_columns_fail_closed(self) -> None:
        bad = pd.DataFrame({"open": [1.0], "close": [1.0]})
        with pytest.raises(ValueError):
            _model().detect(bad, pd.Series([1.0]))

    def test_detect_nonpositive_atr_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            _model().detect(self._df(), pd.Series([1.0, 0.0, 1.0, 1.0, 1.0]))


class TestConfigValidation:
    def test_probability_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError):
            GapFillConfig(fill_probability={"tiny": 1.5, "small": 0.5, "medium": 0.3, "large": 0.1})

    def test_partial_distribution_not_normalized_rejected(self) -> None:
        bad = {
            "tiny": {0.25: 0.5, 0.5: 0.5, 0.75: 0.5, 1.0: 0.5},
            "small": {0.25: 0.25, 0.5: 0.25, 0.75: 0.25, 1.0: 0.25},
            "medium": {0.25: 0.25, 0.5: 0.25, 0.75: 0.25, 1.0: 0.25},
            "large": {0.25: 0.25, 0.5: 0.25, 0.75: 0.25, 1.0: 0.25},
        }
        with pytest.raises(ValueError):
            GapFillConfig(partial_fill_distribution=bad)

    def test_thresholds_must_increase(self) -> None:
        with pytest.raises(ValueError):
            GapFillConfig(tiny_max=0.6, small_max=0.3)


class TestContract:
    def test_forecast_frozen_and_json_serializable(self) -> None:
        f = _model().forecast(direction="up", gap_size_atr=0.2, prev_close=10.0, open_price=10.2)
        assert dataclasses.is_dataclass(f)
        with pytest.raises(dataclasses.FrozenInstanceError):
            f.fill_probability = 0.0  # type: ignore[misc]
        json.dumps(f.to_dict())

    def test_config_frozen(self) -> None:
        cfg = GapFillConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.tiny_max = 0.1  # type: ignore[misc]
