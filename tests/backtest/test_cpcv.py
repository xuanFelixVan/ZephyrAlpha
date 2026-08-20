# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_cpcv
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_cpcv.py
# [TTL] task_bound
"""CPCV + PBO 单元测试(52号 §6 暂缓项函数级落地).

覆盖: 组合数 C(N,k)、train/test 不相交、purge(t1重叠剔除)、embargo 隔离带、
参数校验、PBO(全过拟合=1/全稳健=0/中间值/同值平局秩/矩阵校验)。
"""
from __future__ import annotations

import numpy as np
import pytest

from zephyr.backtest.core.cpcv import (
    CPCVError,
    compute_pbo,
    expected_n_splits,
    generate_cpcv_splits,
)


# ============== 组合数 ==============


class TestExpectedNSplits:
    def test_comb_values(self):
        assert expected_n_splits(6, 2) == 15
        assert expected_n_splits(4, 1) == 4
        assert expected_n_splits(5, 4) == 5

    def test_invalid(self):
        with pytest.raises(CPCVError):
            expected_n_splits(1, 1)
        with pytest.raises(CPCVError):
            expected_n_splits(4, 0)
        with pytest.raises(CPCVError):
            expected_n_splits(4, 4)


# ============== CPCV 切分 ==============


class TestGenerateCPCVSplits:
    def test_split_count_matches_comb(self):
        splits = generate_cpcv_splits(60, n_groups=6, k_test=2)
        assert len(splits) == 15

    def test_train_test_disjoint(self):
        splits = generate_cpcv_splits(60, n_groups=6, k_test=2)
        for sp in splits:
            assert set(sp.train_indices).isdisjoint(set(sp.test_indices))

    def test_test_groups_cover_all_combos(self):
        splits = generate_cpcv_splits(40, n_groups=4, k_test=2)
        combos = {sp.test_groups for sp in splits}
        assert len(combos) == 6
        assert (0, 1) in combos and (2, 3) in combos

    def test_no_purge_no_embargo_full_cover(self):
        # t1=None 且无 embargo: train ∪ test = 全集(点标签无泄漏窗口)
        splits = generate_cpcv_splits(24, n_groups=4, k_test=1)
        for sp in splits:
            assert len(sp.train_indices) + len(sp.test_indices) == 24

    def test_purge_overlapping_labels(self):
        # t1: 每个样本标签窗口=自身+2(多周期持仓), test=组2(idx 8..15)
        n = 32
        t1 = [min(i + 2, n - 1) for i in range(n)]
        splits = generate_cpcv_splits(n, n_groups=4, k_test=1, t1=t1)
        sp = next(s for s in splits if s.test_groups == (2,))
        # test 区间 [16, 23]; train 中 i∈[14,15] 的 t1>=16 重叠须被 purge
        assert 14 not in sp.train_indices
        assert 15 not in sp.train_indices
        # i=13: t1=15 < 16 不重叠, 保留
        assert 13 in sp.train_indices

    def test_embargo_excludes_after_test(self):
        n = 40
        splits = generate_cpcv_splits(n, n_groups=4, k_test=1, embargo=3)
        sp = next(s for s in splits if s.test_groups == (1,))
        # test 区间 [10,19], embargo 剔除 [20,22]
        for i in (20, 21, 22):
            assert i not in sp.train_indices
        assert 23 in sp.train_indices

    def test_last_group_no_embargo_overflow(self):
        # test 为最后一组时 embargo 截断不越界
        splits = generate_cpcv_splits(20, n_groups=4, k_test=1, embargo=10)
        sp = next(s for s in splits if s.test_groups == (3,))
        assert max(sp.train_indices) < 20

    def test_invalid_params(self):
        with pytest.raises(CPCVError):
            generate_cpcv_splits(0)
        with pytest.raises(CPCVError):
            generate_cpcv_splits(10, n_groups=20, k_test=1)
        with pytest.raises(CPCVError):
            generate_cpcv_splits(10, n_groups=2, k_test=1, embargo=-1)

    def test_invalid_t1(self):
        with pytest.raises(CPCVError):
            generate_cpcv_splits(10, n_groups=2, k_test=1, t1=[1, 2, 3])  # 长度不符
        with pytest.raises(CPCVError):
            generate_cpcv_splits(10, n_groups=2, k_test=1, t1=[0] * 9 + [0])  # t1[9]<9
        with pytest.raises(CPCVError):
            generate_cpcv_splits(
                10, n_groups=2, k_test=1, t1=[5, 4, 4, 5, 6, 7, 8, 9, 9, 9]  # 非单调
            )


# ============== PBO ==============


class TestComputePBO:
    def test_fully_overfit_pbo_one(self):
        # 每折 IS 最优 trial 恰为 OOS 最差 → ω<0.5 恒成立 → PBO=1
        is_perf = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
        oos_perf = np.array([[0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0]])
        r = compute_pbo(is_perf, oos_perf)
        assert r["pbo"] == 1.0
        assert all(x < 0 for x in r["logits"])

    def test_fully_robust_pbo_zero(self):
        # 每折 IS 最优 trial 恰为 OOS 最优 → ω>0.5 → PBO=0
        is_perf = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
        oos_perf = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
        r = compute_pbo(is_perf, oos_perf)
        assert r["pbo"] == 0.0

    def test_intermediate_pbo(self):
        is_perf = np.array([[1.0, 0.0]] * 4)
        oos_perf = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
        r = compute_pbo(is_perf, oos_perf)
        assert r["pbo"] == 0.5
        assert r["n_splits"] == 4
        assert r["n_trials"] == 2

    def test_ties_average_rank(self):
        # OOS 全同值 → 平均秩 → ω=rank/(M+1), M=3, 平均秩=2 → ω=0.5 → logit=0 不计入PBO
        is_perf = np.array([[1.0, 0.5, 0.0]])
        oos_perf = np.array([[0.5, 0.5, 0.5]])
        r = compute_pbo(is_perf, oos_perf)
        assert r["omega"][0] == pytest.approx(0.5)
        assert r["logits"][0] == pytest.approx(0.0)
        assert r["pbo"] == 0.0

    def test_list_input_accepted(self):
        r = compute_pbo([[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [1.0, 0.0]])
        assert r["n_splits"] == 2

    def test_shape_mismatch_raises(self):
        with pytest.raises(CPCVError):
            compute_pbo(np.ones((2, 3)), np.ones((2, 2)))

    def test_not_2d_raises(self):
        with pytest.raises(CPCVError):
            compute_pbo(np.ones(3), np.ones(3))

    def test_single_trial_raises(self):
        with pytest.raises(CPCVError):
            compute_pbo(np.ones((2, 1)), np.ones((2, 1)))

    def test_nan_raises(self):
        with pytest.raises(CPCVError):
            compute_pbo(np.array([[1.0, float("nan")]]), np.array([[1.0, 0.0]]))

    def test_result_keys(self):
        r = compute_pbo(np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]]))
        assert set(r) == {"pbo", "mean_logit", "logits", "omega", "n_splits", "n_trials"}
