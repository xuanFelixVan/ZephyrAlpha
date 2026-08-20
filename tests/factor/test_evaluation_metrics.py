# [A_test] module_id: MOD-GOV_evaluation_metrics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_evaluation_metrics
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_evaluation_metrics.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D-FACTOR-03 因子评估指标测试——纯函数模块（无 IO 依赖）。

覆盖：
- compute_ic: 完全正相关 / 完全负相关 / 无相关 / 数据不足 / 空输入 / NaN
- compute_ic_series: 面板 → IC 时间序列
- compute_ir: 正常 / 空 / 常数（std=0）
- compute_oos_positive_rate: 全正 / 混合 / 空
- check_overfitting: 正常 / 过拟合 / IS=0
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

metrics = pytest.importorskip("zephyr.factor.core.evaluation.metrics")

compute_ic = metrics.compute_ic
compute_ic_series = metrics.compute_ic_series
compute_ir = metrics.compute_ir
compute_oos_positive_rate = metrics.compute_oos_positive_rate
check_overfitting = metrics.check_overfitting


class TestComputeIc:
    def test_perfect_positive(self):
        fv = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=list("ABCDE"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], index=list("ABCDE"))
        assert abs(compute_ic(fv, fr) - 1.0) < 1e-10

    def test_perfect_negative(self):
        fv = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=list("ABCDE"))
        fr = pd.Series([50.0, 40.0, 30.0, 20.0, 10.0], index=list("ABCDE"))
        assert abs(compute_ic(fv, fr) - (-1.0)) < 1e-10

    def test_no_correlation(self):
        rng = np.random.default_rng(42)
        fv = pd.Series(rng.standard_normal(100), index=range(100))
        fr = pd.Series(rng.standard_normal(100), index=range(100))
        ic = compute_ic(fv, fr)
        assert -0.3 < ic < 0.3

    def test_insufficient_data(self):
        fv = pd.Series([1.0], index=["A"])
        fr = pd.Series([2.0], index=["A"])
        assert compute_ic(fv, fr) == 0.0

    def test_empty_input(self):
        assert compute_ic(pd.Series([], dtype=float), pd.Series([], dtype=float)) == 0.0

    def test_no_common_index(self):
        fv = pd.Series([1.0, 2.0], index=["A", "B"])
        fr = pd.Series([1.0, 2.0], index=["C", "D"])
        assert compute_ic(fv, fr) == 0.0

    def test_nan_dropped(self):
        fv = pd.Series([1.0, float("nan"), 3.0, 4.0, 5.0], index=list("ABCDE"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], index=list("ABCDE"))
        # 去掉 B 后 4 个点完全正相关
        assert abs(compute_ic(fv, fr) - 1.0) < 1e-10

    def test_range_minus_one_to_one(self):
        fv = pd.Series([1.0, 2.0, 3.0], index=list("ABC"))
        fr = pd.Series([3.0, 1.0, 2.0], index=list("ABC"))
        ic = compute_ic(fv, fr)
        assert -1.0 <= ic <= 1.0


class TestComputeIcSeries:
    def test_empty_panels(self):
        fp = pd.DataFrame()
        rp = pd.DataFrame()
        ic_series = compute_ic_series(fp, rp)
        assert ic_series.empty

    def test_single_date(self):
        # index=date, columns=symbol（对齐 docstring）
        fp = pd.DataFrame({"A": [1.0], "B": [2.0], "C": [3.0]}, index=[1])
        rp = pd.DataFrame({"A": [10.0], "B": [20.0], "C": [30.0]}, index=[1])
        ic_series = compute_ic_series(fp, rp)
        assert len(ic_series) == 1
        assert abs(ic_series.iloc[0] - 1.0) < 1e-10

    def test_multiple_dates(self):
        fp = pd.DataFrame(
            {"A": [1.0, 3.0], "B": [2.0, 2.0], "C": [3.0, 1.0]},
            index=[1, 2],
        )
        rp = pd.DataFrame(
            {"A": [10.0, 30.0], "B": [20.0, 20.0], "C": [30.0, 10.0]},
            index=[1, 2],
        )
        ic_series = compute_ic_series(fp, rp)
        assert len(ic_series) == 2
        assert ic_series.name == "ic"

    def test_common_dates_only(self):
        fp = pd.DataFrame({"A": [1.0, 2.0, 3.0]}, index=[1, 2, 3])
        rp = pd.DataFrame({"A": [2.0, 3.0]}, index=[2, 3])
        ic_series = compute_ic_series(fp, rp)
        # 仅交集日期 2 和 3
        assert len(ic_series) == 2


class TestComputeIr:
    def test_normal(self):
        ic = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5])
        ir = compute_ir(ic)
        assert ir > 0

    def test_empty(self):
        assert compute_ir(pd.Series([], dtype=float)) == 0.0

    def test_single_value(self):
        assert compute_ir(pd.Series([0.5])) == 0.0

    def test_constant_zero_std(self):
        ic = pd.Series([0.3, 0.3, 0.3, 0.3])
        assert compute_ir(ic) == 0.0

    def test_negative_mean(self):
        ic = pd.Series([-0.1, -0.2, -0.3, -0.4])
        ir = compute_ir(ic)
        assert ir < 0


class TestComputeOosPositiveRate:
    def test_all_positive(self):
        ic = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        assert compute_oos_positive_rate(ic, oos_ratio=0.3) == 1.0

    def test_all_negative(self):
        ic = pd.Series([-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9, -1.0])
        assert compute_oos_positive_rate(ic, oos_ratio=0.3) == 0.0

    def test_mixed(self):
        ic = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0])
        # 后 30% = 后 3 个: [1.0, -1.0, -1.0] → 1/3 正
        rate = compute_oos_positive_rate(ic, oos_ratio=0.3)
        assert abs(rate - 1.0 / 3.0) < 1e-10

    def test_empty(self):
        assert compute_oos_positive_rate(pd.Series([], dtype=float)) == 0.0

    def test_custom_ratio(self):
        ic = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0])
        # oos_ratio=0.1 → 后 1 个: [-1.0] → 0 正
        assert compute_oos_positive_rate(ic, oos_ratio=0.1) == 0.0


class TestCheckOverfitting:
    def test_normal(self):
        # OOS/IS = 0.8/0.5 = 1.6 > 0.5 → 不过拟合
        assert check_overfitting(is_ic=0.5, oos_ic=0.8) is False

    def test_overfit(self):
        # OOS/IS = 0.1/0.5 = 0.2 < 0.5 → 过拟合
        assert check_overfitting(is_ic=0.5, oos_ic=0.1) is True

    def test_zero_is_ic(self):
        assert check_overfitting(is_ic=0.0, oos_ic=0.5) is True

    def test_custom_threshold(self):
        # 默认阈值 0.5 下不過拟合，阈值 0.9 下过拟合
        assert check_overfitting(is_ic=0.5, oos_ic=0.4, threshold=0.5) is False
        assert check_overfitting(is_ic=0.5, oos_ic=0.4, threshold=0.9) is True

    def test_negative_ic(self):
        # IS=-0.5, OOS=-0.4 → ratio=0.8 > 0.5 → 不过拟合
        assert check_overfitting(is_ic=-0.5, oos_ic=-0.4) is False

    def test_equal_ic(self):
        # OOS/IS = 1.0 → 不过拟合
        assert check_overfitting(is_ic=0.3, oos_ic=0.3) is False
