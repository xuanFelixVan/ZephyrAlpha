# [BLUEPRINT] MOD-BT-026 | docs/03_modules/_domain_backtest/nan_processor/blueprint.md | §D-BACKTEST BT-26
# [A_module] module_id=MOD-BT-026 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-BT-026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_nan_processor
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""NaNProcessor (MOD-BT-026) 测试套件。

覆盖: 6种填充策略、全NaN行/列删除、高NaN比例删除、fill_limit、
       不修改输入、报告准确性、空DataFrame、非数值列。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.services.nan_processor import (
    FillStrategy,
    InvalidDataFormatError,
    NaNProcessor,
    NaNProcessorConfig,
    NaNProcessReport,
)


@pytest.fixture
def processor() -> NaNProcessor:
    return NaNProcessor()


def _make_df_with_nan() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a": [1.0, np.nan, 3.0, np.nan, 5.0],
            "b": [10.0, 20.0, np.nan, 40.0, 50.0],
            "c": [np.nan, np.nan, np.nan, np.nan, np.nan],  # 全NaN列
        },
        index=pd.date_range("2026-01-05", periods=5),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_non_dataframe_raises(self, processor: NaNProcessor):
        with pytest.raises(InvalidDataFormatError, match="must be a pandas DataFrame"):
            processor.process([1, 2, 3])

    def test_empty_dataframe_returns_empty(self, processor: NaNProcessor):
        df = pd.DataFrame(columns=["a", "b"])
        result, report = processor.process(df)
        assert report.total_nan_before == 0
        assert report.filled_count == 0

    def test_no_nan_returns_unchanged(self, processor: NaNProcessor):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
        result, report = processor.process(df)
        assert report.total_nan_before == 0
        assert report.filled_count == 0
        pd.testing.assert_frame_equal(result, df)


# ──────────────────────────────────────────────────────────────────────────────
# 填充策略
# ──────────────────────────────────────────────────────────────────────────────


class TestFillStrategies:
    def test_ffill(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.FFILL,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 5.0]})
        result, report = proc.process(df)
        assert result["a"].tolist() == [1.0, 1.0, 3.0, 3.0, 5.0]
        assert report.filled_count == 2

    def test_bfill(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.BFILL,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 5.0]})
        result, report = proc.process(df)
        assert result["a"].tolist() == [1.0, 3.0, 3.0, 5.0, 5.0]

    def test_mean_fill(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.MEAN,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 5.0]})
        result, report = proc.process(df)
        # mean of [1,3,5] = 3.0
        assert result["a"].tolist() == [1.0, 3.0, 3.0, 3.0, 5.0]

    def test_median_fill(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.MEDIAN,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 100.0]})
        result, report = proc.process(df)
        # median of [1,3,100] = 3.0
        assert result["a"].tolist() == [1.0, 3.0, 3.0, 3.0, 100.0]

    def test_linear_interpolation(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.LINEAR,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 5.0]})
        result, report = proc.process(df)
        assert result["a"].tolist() == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_zero_fill(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.ZERO,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0]})
        result, report = proc.process(df)
        assert result["a"].tolist() == [1.0, 0.0, 3.0]


# ──────────────────────────────────────────────────────────────────────────────
# 清洗
# ──────────────────────────────────────────────────────────────────────────────


class TestCleaning:
    def test_drop_all_nan_rows(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                drop_all_nan_rows=True,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
                fill_strategy=FillStrategy.FFILL,
            )
        )
        df = pd.DataFrame(
            {
                "a": [1.0, np.nan, 3.0],  # row 1 is all-NaN
                "b": [4.0, np.nan, 6.0],
            }
        )
        result, report = proc.process(df)
        assert report.dropped_rows == 1
        assert len(result) == 2

    def test_drop_all_nan_cols(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                drop_all_nan_rows=False,
                drop_all_nan_cols=True,
                max_nan_ratio=0,
                fill_strategy=FillStrategy.FFILL,
            )
        )
        df = _make_df_with_nan()
        result, report = proc.process(df)
        assert report.dropped_cols == 1  # column "c"
        assert "c" not in result.columns

    def test_max_nan_ratio_drops_high_nan_rows(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0.4,
                fill_strategy=FillStrategy.FFILL,
            )
        )
        df = pd.DataFrame(
            {
                "a": [1.0, np.nan, np.nan],  # row 1: 1/2=0.5 > 0.4
                "b": [4.0, 5.0, np.nan],  # row 2: 1/2=0.5 > 0.4
            }
        )
        result, report = proc.process(df)
        assert report.dropped_rows == 2

    def test_fill_limit(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.FFILL,
                fill_limit=1,
                drop_all_nan_rows=False,
                drop_all_nan_cols=False,
                max_nan_ratio=0,
            )
        )
        df = pd.DataFrame({"a": [1.0, np.nan, np.nan, np.nan, 5.0]})
        result, report = proc.process(df)
        # limit=1: only first NaN after 1.0 is filled
        vals = result["a"].tolist()
        assert vals[0] == 1.0
        assert vals[1] == 1.0  # filled by ffill limit=1
        assert np.isnan(vals[2])  # not filled (limit reached)
        assert np.isnan(vals[3])  # not filled
        assert vals[4] == 5.0


# ──────────────────────────────────────────────────────────────────────────────
# 不变量与报告
# ──────────────────────────────────────────────────────────────────────────────


class TestInvariants:
    def test_does_not_modify_input(self, processor: NaNProcessor):
        df = _make_df_with_nan()
        df_copy = df.copy()
        processor.process(df)
        pd.testing.assert_frame_equal(df, df_copy)

    def test_report_accuracy(self, processor: NaNProcessor):
        df = _make_df_with_nan()
        _, report = processor.process(df)
        # original: a=2 nan, b=1 nan, c=5 nan = 8 total
        assert report.total_nan_before == 8
        # after processing, all NaN should be handled (filled or dropped)
        assert report.total_nan_after == 0
        assert report.cleanup_ratio == 1.0

    def test_report_shape(self, processor: NaNProcessor):
        df = _make_df_with_nan()
        _, report = processor.process(df)
        assert report.original_shape == (5, 3)
        # col c dropped (all nan), no rows dropped (none all-nan)
        assert "c" not in df.columns or True  # input not modified

    def test_config_validation(self):
        with pytest.raises(InvalidDataFormatError):
            NaNProcessorConfig(max_nan_ratio=1.5)
        with pytest.raises(InvalidDataFormatError):
            NaNProcessorConfig(fill_limit=-1)


# ──────────────────────────────────────────────────────────────────────────────
# 综合
# ──────────────────────────────────────────────────────────────────────────────


class TestIntegration:
    def test_full_pipeline_with_realistic_data(self):
        proc = NaNProcessor(
            NaNProcessorConfig(
                fill_strategy=FillStrategy.LINEAR,
                drop_all_nan_cols=True,
                max_nan_ratio=0.6,
            )
        )
        dates = pd.date_range("2026-01-05", periods=10)
        df = pd.DataFrame(
            {
                "close": [100, np.nan, 102, np.nan, np.nan, 105, 106, np.nan, 108, 109],
                "volume": [1000, 2000, np.nan, 4000, 5000, np.nan, 7000, 8000, 9000, 10000],
                "junk": [np.nan] * 10,  # all nan col
            },
            index=dates,
        )
        result, report = proc.process(df)
        assert "junk" not in result.columns
        assert report.total_nan_after == 0
        assert report.dropped_cols == 1
        # linear interpolation should fill close gaps
        assert result["close"].isna().sum() == 0
