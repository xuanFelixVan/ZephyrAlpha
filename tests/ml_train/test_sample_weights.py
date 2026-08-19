# [A_test] module_id: MOD-GOV_test_sample_weights | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_sample_weights
# [TESTS] src/zephyr/ml_train/core/sample_weights.py
# [TTL] task_bound
"""90 号 Phase2 项（#9 数据分层）：半衰期样本权重已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §9（v2.0.0 修订采纳）——
  ② w(t)=0.5^(t/HL)，HL 默认 2.5 年（实现式 0.5**(days_ago/(HL*252))）；
  ③ 结构断裂期（2015股灾/2018熊市/2024微盘崩盘）不剔除，降权 50% 保留。
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from zephyr.ml_train.core.sample_weights import (
    DEFAULT_BREAK_PERIODS,
    compute_sample_weights,
)


class TestHalfLifeFormula:
    def test_today_weight_is_one(self):
        w = compute_sample_weights([date(2026, 8, 19)], reference_date=date(2026, 8, 19))
        assert w[0] == pytest.approx(1.0)

    def test_one_hl_decay(self):
        """HL=1 年：252 天前权重=0.5。"""
        ref = date(2026, 8, 19)
        d = date.fromordinal(ref.toordinal() - 252)
        w = compute_sample_weights([d], reference_date=ref, half_life_years=1.0)
        assert w[0] == pytest.approx(0.5)

    def test_two_hl_decay(self):
        """HL=1 年：504 天前权重=0.25。"""
        ref = date(2026, 8, 19)
        d = date.fromordinal(ref.toordinal() - 504)
        w = compute_sample_weights([d], reference_date=ref, half_life_years=1.0)
        assert w[0] == pytest.approx(0.25)

    def test_default_hl_2p5_years(self):
        """默认 HL=2.5 年：630 天（2.5×252）前权重=0.5。"""
        ref = date(2026, 8, 19)
        d = date.fromordinal(ref.toordinal() - 630)
        w = compute_sample_weights([d], reference_date=ref)
        assert w[0] == pytest.approx(0.5)


class TestBreakPeriods:
    def test_break_period_downweight_50pct(self):
        """断裂期样本降权 50% 保留（不剔除）。"""
        ref = date(2026, 8, 19)
        # 今日落在自定义断裂期内：1.0 × 0.5 = 0.5
        w = compute_sample_weights(
            [ref],
            reference_date=ref,
            half_life_years=1.0,
            break_periods=[(date(2026, 8, 1), date(2026, 8, 31))],
        )
        assert w[0] == pytest.approx(0.5)

    def test_default_break_periods_cover_2015_crash(self):
        """默认断裂期清单配置化且覆盖 2015 股灾（2015-07 在期内）。"""
        assert any(
            start <= date(2015, 7, 15) <= end for start, end in DEFAULT_BREAK_PERIODS
        )

    def test_outside_break_period_no_downweight(self):
        ref = date(2026, 8, 19)
        w = compute_sample_weights(
            [ref],
            reference_date=ref,
            half_life_years=1.0,
            break_periods=[(date(2018, 1, 1), date(2018, 12, 31))],
        )
        assert w[0] == pytest.approx(1.0)


class TestValidation:
    def test_future_date_raises(self):
        with pytest.raises(ValueError):
            compute_sample_weights([date(2026, 8, 20)], reference_date=date(2026, 8, 19))

    def test_nonpositive_hl_raises(self):
        with pytest.raises(ValueError):
            compute_sample_weights([date(2026, 8, 19)], reference_date=date(2026, 8, 19), half_life_years=0)

    def test_output_shape_and_monotonic(self):
        ref = date(2026, 8, 19)
        ds = [date.fromordinal(ref.toordinal() - k) for k in (0, 100, 500)]
        w = compute_sample_weights(ds, reference_date=ref)
        assert isinstance(w, np.ndarray)
        assert w.shape == (3,)
        assert w[0] > w[1] > w[2]
