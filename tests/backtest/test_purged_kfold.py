# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_purged_kfold
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_purged_kfold.py
# [TTL] task_bound
"""Purged K-Fold 单元测试(52号 §6 BM-BT-04-C 函数级落地).

覆盖: K折连续块无重叠全覆盖、train/test不相交、purge(t1重叠剔除)、
embargo 隔离带(含末折截断)、参数/t1 校验、退化(点标签退化为普通K折+embargo)。
"""
from __future__ import annotations

import pytest

from zephyr.backtest.core.purged_kfold import (
    PurgedKFoldError,
    purged_kfold_split,
)


class TestBasicKFold:
    def test_fold_count(self):
        splits = purged_kfold_split(20, n_splits=4)
        assert len(splits) == 4

    def test_test_folds_cover_all_no_overlap(self):
        n = 21
        splits = purged_kfold_split(n, n_splits=5)
        all_test = sorted(i for _, test in splits for i in test)
        assert all_test == list(range(n))  # 全覆盖无重叠

    def test_train_test_disjoint(self):
        for train, test in purged_kfold_split(30, n_splits=5):
            assert set(train).isdisjoint(set(test))

    def test_point_label_full_cover_no_embargo(self):
        # t1=None 且 embargo=0: 退化为普通 K-Fold, train ∪ test = 全集
        n = 24
        for train, test in purged_kfold_split(n, n_splits=4):
            assert len(train) + len(test) == n

    def test_fold_sizes_remainder_first(self):
        # 21 / 5 = 4 余 1 → 首折 5 样本, 其余 4
        splits = purged_kfold_split(21, n_splits=5)
        assert [len(t) for _, t in splits] == [5, 4, 4, 4, 4]


class TestPurge:
    def test_overlapping_labels_purged(self):
        # n=20, 5折各4样本; 折2=test[idx 8..12), t1=i+3
        n = 20
        t1 = [min(i + 3, n - 1) for i in range(n)]
        splits = purged_kfold_split(n, n_splits=5, t1=t1)
        train, test = splits[2]
        assert test == (8, 9, 10, 11)
        # train 中 i∈{5,6,7} 的 t1∈{8,9,10} >= 8 重叠须 purge
        for i in (5, 6, 7):
            assert i not in train
        # i=4: t1=7 < 8 不重叠, 保留
        assert 4 in train

    def test_label_reaching_into_test_from_left_only(self):
        # purge 语义: 仅剔除窗口与 test 区间重叠者(左侧长标签)
        n = 12
        # 单调不减且 t1[i]>=i; 样本2的标签窗口 [2,5] 与折1 test [3,6) 重叠
        t1 = [2, 2, 5, 5, 6, 7, 8, 9, 10, 11, 11, 11]
        splits = purged_kfold_split(n, n_splits=4, t1=t1)
        train, test = splits[1]
        assert test == (3, 4, 5)
        assert 2 not in train  # 窗口 [2,5] 重叠 → purge
        assert 0 in train  # 窗口 [0,2] 止于 test 之前 → 保留
        assert 1 in train


class TestEmbargo:
    def test_embargo_after_test(self):
        splits = purged_kfold_split(20, n_splits=4, embargo=2)
        train, test = splits[1]
        assert test == (5, 6, 7, 8, 9)
        # embargo 剔除 [10, 11]
        assert 10 not in train
        assert 11 not in train
        assert 12 in train

    def test_last_fold_embargo_truncated(self):
        splits = purged_kfold_split(12, n_splits=4, embargo=100)
        train, test = splits[-1]
        assert test == (9, 10, 11)
        assert all(i < 12 for i in train)  # 截断不越界

    def test_first_fold_embargo_drops_head_of_remaining(self):
        splits = purged_kfold_split(12, n_splits=4, embargo=1)
        train, test = splits[0]
        assert test == (0, 1, 2)
        assert 3 not in train  # [e, e+embargo) = [3,4)
        assert 4 in train


class TestValidation:
    def test_invalid_n_samples(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(0)

    def test_invalid_n_splits(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(10, n_splits=1)

    def test_samples_less_than_splits(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(3, n_splits=5)

    def test_negative_embargo(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(10, n_splits=2, embargo=-1)

    def test_t1_length_mismatch(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(10, n_splits=2, t1=[1, 2])

    def test_t1_before_self(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(10, n_splits=2, t1=[0] * 10)  # t1[1]=0 < 1

    def test_t1_non_monotonic(self):
        with pytest.raises(PurgedKFoldError):
            purged_kfold_split(10, n_splits=2, t1=[5, 4, 4, 5, 6, 7, 8, 9, 9, 9])

    def test_error_code(self):
        assert PurgedKFoldError("x").error_code == "ZA-BT-0034"
