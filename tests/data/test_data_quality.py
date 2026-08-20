# [A_test] module_id: MOD-GOV_data_quality | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-374 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_data_quality
# [INVARIANTS] DQ_SPECS covers all DQDimension values; score_dq returns 0.0 for unknown dim
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_data_quality.py
# [TTL] task_bound

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.governance.data_governance.data_quality import (
    DQ_CHECK_FUNCS,
    DQ_DIM_COUNT,
    DQ_SPECS,
    DQDimension,
    DQSpec,
    check_accuracy,
    check_anomaly,
    check_completeness,
    check_consistency,
    check_freshness,
    check_timeliness,
    check_uniqueness,
    check_validity,
    get_dq_spec,
    run_dq_check,
    score_dq,
)


class TestDQDimension:
    def test_all_dimensions_exist(self):
        assert len(DQDimension) == DQ_DIM_COUNT

    def test_dimension_values(self):
        expected = {
            "Completeness",
            "Accuracy",
            "Anomaly",
            "Consistency",
            "Freshness",
            "Timeliness",
            "Uniqueness",
            "Validity",
        }
        actual = {d.value for d in DQDimension}
        assert actual == expected


class TestDQSpec:
    def test_spec_creation_defaults(self):
        spec = DQSpec(dimension=DQDimension.ACCURACY, label="test", metric="m1")
        assert spec.threshold == 0.95
        assert spec.check_func == ""

    def test_spec_creation_custom(self):
        spec = DQSpec(dimension=DQDimension.COMPLETENESS, label="t", metric="m", threshold=0.80, check_func="cf")
        assert spec.threshold == 0.80
        assert spec.check_func == "cf"


class TestDQSpecs:
    def test_all_dimensions_have_specs(self):
        for dim in DQDimension:
            assert dim in DQ_SPECS

    def test_specs_have_check_funcs(self):
        for dim, spec in DQ_SPECS.items():
            assert spec.check_func != ""
            assert spec.dimension == dim


class TestGetDqSpec:
    def test_known_dimension(self):
        spec = get_dq_spec(DQDimension.ACCURACY)
        assert spec is not None
        assert spec.dimension == DQDimension.ACCURACY

    def test_returns_correct_spec(self):
        spec = get_dq_spec(DQDimension.COMPLETENESS)
        assert spec is not None
        assert spec.metric == "missing_pct"

    def test_all_dimensions_retrievable(self):
        for dim in DQDimension:
            assert get_dq_spec(dim) is not None


class TestScoreDq:
    def test_score_at_threshold(self):
        spec = get_dq_spec(DQDimension.COMPLETENESS)
        score = score_dq(DQDimension.COMPLETENESS, spec.threshold)
        assert score == 1.0

    def test_score_above_threshold_capped(self):
        score = score_dq(DQDimension.COMPLETENESS, 2.0)
        assert score == 1.0

    def test_score_below_threshold(self):
        score = score_dq(DQDimension.ACCURACY, 0.5)
        assert 0.0 < score < 1.0

    def test_score_zero_value(self):
        score = score_dq(DQDimension.ACCURACY, 0.0)
        assert score == 0.0


class TestBoundary:
    def test_dq_dim_count_matches_enum(self):
        assert len(DQDimension) == DQ_DIM_COUNT

    def test_score_dq_consistency(self):
        spec = get_dq_spec(DQDimension.CONSISTENCY)
        score = score_dq(DQDimension.CONSISTENCY, spec.threshold)
        assert score == 1.0


class TestB4Dimensions:
    """B4 SLA 四维度对齐：FRESHNESS / ANOMALY 的方向性与阈值语义。"""

    def test_freshness_score_direction(self):
        # age 越小越健康：0→满分, threshold→0分, 超限→0分
        assert score_dq(DQDimension.FRESHNESS, 0.0) == 1.0
        assert score_dq(DQDimension.FRESHNESS, 60.0) == 0.0
        assert score_dq(DQDimension.FRESHNESS, 120.0) == 0.0

    def test_anomaly_score_direction(self):
        # 离群率越小越健康：0→满分, threshold→0分, 超限→0分
        assert score_dq(DQDimension.ANOMALY, 0.0) == 1.0
        assert score_dq(DQDimension.ANOMALY, 0.01) == 0.0
        assert score_dq(DQDimension.ANOMALY, 0.02) == 0.0

    def test_lower_is_better_flags(self):
        # 仅 FRESHNESS / ANOMALY 为 True，其余默认 False（向后兼容）
        assert DQ_SPECS[DQDimension.FRESHNESS].lower_is_better is True
        assert DQ_SPECS[DQDimension.ANOMALY].lower_is_better is True
        for dim in (
            DQDimension.COMPLETENESS,
            DQDimension.ACCURACY,
            DQDimension.CONSISTENCY,
            DQDimension.TIMELINESS,
            DQDimension.UNIQUENESS,
            DQDimension.VALIDITY,
        ):
            assert DQ_SPECS[dim].lower_is_better is False

    def test_b4_four_dimensions_present(self):
        # B4 SLA 四维度必须在册
        b4 = {DQDimension.COMPLETENESS, DQDimension.CONSISTENCY, DQDimension.FRESHNESS, DQDimension.ANOMALY}
        assert b4.issubset(set(DQDimension))


# ===========================================================================
# 八维 check_func 实现绑定（15_data_feature_layer_spec §6 待裁定项落地）
# ===========================================================================


class TestCheckCompleteness:
    def test_full_df_is_one(self):
        df = pd.DataFrame({"a": [1.0, 2.0], "b": ["x", "y"]})
        assert check_completeness(df) == 1.0

    def test_half_missing(self):
        df = pd.DataFrame({"a": [1.0, np.nan], "b": ["x", "y"]})
        assert check_completeness(df) == pytest.approx(0.75)

    def test_empty_df_is_zero(self):
        # 空表=零完整（防"空表满分"假象）
        assert check_completeness(pd.DataFrame({"a": []})) == 0.0

    def test_columns_subset(self):
        df = pd.DataFrame({"a": [1.0, np.nan], "b": ["x", "y"]})
        # 只看 b 列 → 完整
        assert check_completeness(df, columns=["b"]) == 1.0
        # 只看 a 列 → 0.5
        assert check_completeness(df, columns=["a"]) == pytest.approx(0.5)


class TestCheckAccuracy:
    def test_identical_reference(self):
        df = pd.DataFrame({"c": [10.0, 20.0, 30.0]})
        assert check_accuracy(df, df.copy()) == 1.0

    def test_partial_within_tolerance(self):
        df = pd.DataFrame({"c": [100.0, 200.0]})
        ref = pd.DataFrame({"c": [100.0, 220.0]})
        # 第 2 行相对偏差 10% > 默认 1% → 达标率 0.5
        assert check_accuracy(df, ref) == pytest.approx(0.5)
        # 放宽 tolerance 到 20% → 全达标
        assert check_accuracy(df, ref, tolerance=0.20) == 1.0

    def test_missing_reference_raises(self):
        with pytest.raises(ValueError, match="reference"):
            check_accuracy(pd.DataFrame({"c": [1.0]}), None)

    def test_empty_df_is_zero(self):
        ref = pd.DataFrame({"c": [1.0]})
        assert check_accuracy(pd.DataFrame({"c": []}), ref) == 0.0


class TestCheckAnomaly:
    def test_no_outlier(self):
        rng = np.random.default_rng(0)
        df = pd.DataFrame({"r": rng.normal(0, 1, 500)})
        assert check_anomaly(df) == 0.0

    def test_single_spike(self):
        vals = np.zeros(101)
        vals[:-1] = np.random.default_rng(1).normal(0, 1, 100)
        vals[-1] = 100.0  # 极端离群
        df = pd.DataFrame({"r": vals})
        rate = check_anomaly(df)
        assert rate == pytest.approx(1 / 101, abs=1e-9)

    def test_constant_column_no_crash(self):
        df = pd.DataFrame({"r": [5.0] * 50})
        assert check_anomaly(df) == 0.0

    def test_empty_is_zero(self):
        assert check_anomaly(pd.DataFrame({"r": []})) == 0.0


class TestCheckConsistency:
    def test_reference_exact_match(self):
        df = pd.DataFrame({"c": [1.0, 2.0]})
        assert check_consistency(df, reference=df.copy()) == 1.0

    def test_reference_mismatch(self):
        df = pd.DataFrame({"c": [1.0, 2.0]})
        ref = pd.DataFrame({"c": [1.0, 2.5]})
        assert check_consistency(df, reference=ref) == pytest.approx(0.5)

    def test_internal_ohlc_structure(self):
        df = pd.DataFrame(
            {
                "open": [10.0, 10.0],
                "high": [11.0, 10.5],
                "low": [9.0, 9.5],
                "close": [10.5, 10.2],
            }
        )
        assert check_consistency(df) == 1.0

    def test_internal_ohlc_violation(self):
        df = pd.DataFrame(
            {
                "open": [10.0, 10.0],
                "high": [11.0, 10.0],
                "low": [9.0, 9.5],
                "close": [10.5, 10.6],  # 第2行 close>high 违例
            }
        )
        assert check_consistency(df) == pytest.approx(0.5)

    def test_no_reference_no_ohlc_raises(self):
        with pytest.raises(ValueError, match="OHLC"):
            check_consistency(pd.DataFrame({"x": [1.0]}))


class TestCheckFreshness:
    def test_age_seconds(self):
        now = pd.Timestamp("2026-08-20 12:00:00")
        last = pd.Timestamp("2026-08-20 11:59:30")
        assert check_freshness(last, now=now) == pytest.approx(30.0)

    def test_series_uses_max(self):
        now = pd.Timestamp("2026-08-20 12:00:00")
        s = pd.Series(pd.to_datetime(["2026-08-20 11:00:00", "2026-08-20 11:59:00"]))
        assert check_freshness(s, now=now) == pytest.approx(60.0)

    def test_tz_mixed_handled(self):
        now = pd.Timestamp("2026-08-20 12:00:00", tz="UTC")
        last = pd.Timestamp("2026-08-20 11:59:00")  # naive
        assert check_freshness(last, now=now) == pytest.approx(60.0)

    def test_none_raises(self):
        with pytest.raises((ValueError, TypeError)):
            check_freshness(None)


class TestCheckTimeliness:
    def test_all_within_sla(self):
        ev = pd.Series(pd.to_datetime(["2026-08-20 09:30:00.000", "2026-08-20 09:30:00.100"]))
        pr = pd.Series(pd.to_datetime(["2026-08-20 09:30:00.500", "2026-08-20 09:30:00.600"]))
        assert check_timeliness(ev, pr, sla_ms=1000.0) == 1.0

    def test_half_within_sla(self):
        ev = pd.Series(pd.to_datetime(["2026-08-20 09:30:00", "2026-08-20 09:30:00"]))
        pr = pd.Series(pd.to_datetime(["2026-08-20 09:30:00.500", "2026-08-20 09:30:05.000"]))
        assert check_timeliness(ev, pr, sla_ms=1000.0) == pytest.approx(0.5)

    def test_empty_is_one(self):
        ev = pd.Series(pd.to_datetime([]))
        pr = pd.Series(pd.to_datetime([]))
        assert check_timeliness(ev, pr) == 1.0


class TestCheckUniqueness:
    def test_no_duplicates(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        assert check_uniqueness(df) == 1.0

    def test_half_duplicated(self):
        df = pd.DataFrame({"a": [1, 1, 2, 3]})
        # 4 行中 1 行为重复（keep=first）→ 唯一率 0.75
        assert check_uniqueness(df) == pytest.approx(0.75)

    def test_subset(self):
        df = pd.DataFrame({"a": [1, 1], "b": ["x", "y"]})
        assert check_uniqueness(df, subset=["a"]) == pytest.approx(0.5)
        assert check_uniqueness(df, subset=["a", "b"]) == 1.0

    def test_empty_is_one(self):
        assert check_uniqueness(pd.DataFrame({"a": []})) == 1.0


class TestCheckValidity:
    def test_all_valid(self):
        df = pd.DataFrame({"close": [10.0, 20.0], "vol": [100.0, 200.0]})
        rules = {"close": (0.0, None), "vol": (0.0, 1000.0)}
        assert check_validity(df, rules) == 1.0

    def test_violation_rate(self):
        df = pd.DataFrame({"close": [10.0, -5.0, 20.0, 30.0]})
        rules = {"close": (0.0, None)}
        assert check_validity(df, rules) == pytest.approx(0.75)

    def test_nan_treated_as_violation(self):
        df = pd.DataFrame({"close": [10.0, np.nan]})
        rules = {"close": (0.0, None)}
        assert check_validity(df, rules) == pytest.approx(0.5)

    def test_empty_rules_raises(self):
        with pytest.raises(ValueError, match="rules"):
            check_validity(pd.DataFrame({"close": [1.0]}), {})

    def test_empty_df_is_one(self):
        assert check_validity(pd.DataFrame({"close": []}), {"close": (0.0, None)}) == 1.0


class TestCheckFuncBinding:
    """实现绑定完整性：DQ_SPECS 每个 check_func 名都必须有注册实现（15 号 §6 落地断言）。"""

    def test_every_spec_check_func_bound(self):
        for dim, spec in DQ_SPECS.items():
            assert spec.check_func in DQ_CHECK_FUNCS, f"{dim} 的 check_func '{spec.check_func}' 未绑定实现"

    def test_run_dq_check_routes(self):
        df = pd.DataFrame({"a": [1.0, 2.0]})
        assert run_dq_check(DQDimension.COMPLETENESS, df) == 1.0
        assert run_dq_check(DQDimension.UNIQUENESS, df) == 1.0

    def test_run_dq_check_unknown_dim_raises(self):
        with pytest.raises((KeyError, ValueError)):
            run_dq_check("NOT_A_DIM", pd.DataFrame({"a": [1.0]}))
