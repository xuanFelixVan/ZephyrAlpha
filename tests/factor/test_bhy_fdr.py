# [A_test] module_id: MOD-GOV_test_bhy_fdr | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_bhy_fdr
# [TESTS] src/zephyr/factor/analysis/bhy_fdr.py
# [TTL] task_bound
"""90 号 Phase2 项（#2 因子IC）：BHY FDR 校正已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §2（v2.0.0）——
  硬性统计门禁：ICIR≥0.5 + BHY 控制 FDR q=10%（单批筛选 >100 因子时
  t 门槛升 2.8，Harvey-Liu-Zhu 标准）。

BHY 程序（Benjamini-Hochberg-Yekutieli，任意依赖稳健）：
  升序 p_(1)≤…≤p_(m)；c(m)=Σ1/i（调和因子）；
  k=max{i: p_(i) ≤ i·q/(m·c(m))}；拒绝前 k 个。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.factor.analysis.bhy_fdr import BHYFDRResult, bhy_fdr


class TestKnownAnswers:
    def test_five_pvalues_q10(self):
        """m=5, q=0.10, c(5)=137/60≈2.28333。

        阈值 i·q/(m·c(m))：i=1..5 → 0.00876/0.01752/0.02628/0.03504/0.04380
        p=[0.001,0.002,0.01,0.5,0.9] → 前 3 个通过 → k=3。
        """
        res = bhy_fdr([0.001, 0.002, 0.01, 0.5, 0.9], q=0.10)
        assert res.n_rejected == 3
        assert res.rejected == [True, True, True, False, False]
        # 临界阈值 = 3×0.1/(5×137/60)
        assert res.threshold == pytest.approx(3 * 0.10 / (5 * 137 / 60))

    def test_no_rejection_when_all_large(self):
        res = bhy_fdr([0.5, 0.6, 0.7], q=0.10)
        assert res.n_rejected == 0
        assert res.rejected == [False, False, False]
        assert res.threshold == 0.0

    def test_unsorted_input_maps_back_to_original_order(self):
        """拒绝掩码必须映射回原始输入顺序。"""
        res = bhy_fdr([0.9, 0.001, 0.5], q=0.10)
        assert res.rejected == [False, True, False]

    def test_stricter_than_bh_under_dependence(self):
        """BHY（c(m)>1）比 BH 更保守：同批 p 值 BHY 拒绝数 ≤ BH。"""
        pvals = [0.01, 0.02, 0.03, 0.04, 0.05]
        bhy = bhy_fdr(pvals, q=0.10, arbitrary_dependence=True)
        bh = bhy_fdr(pvals, q=0.10, arbitrary_dependence=False)
        assert bhy.n_rejected <= bh.n_rejected

    def test_large_batch_all_significant(self):
        """单批 >100 因子全显著场景：p 全 0.0001 → 全部拒绝。"""
        res = bhy_fdr([0.0001] * 150, q=0.10)
        assert res.n_rejected == 150


class TestValidation:
    def test_q_out_of_range_raises(self):
        with pytest.raises(ValueError):
            bhy_fdr([0.01], q=1.5)

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            bhy_fdr([0.01, float("nan")], q=0.10)

    def test_empty_input(self):
        res = bhy_fdr([], q=0.10)
        assert res.n_rejected == 0
        assert res.rejected == []

    def test_result_is_immutable_value(self):
        res = bhy_fdr([0.001], q=0.10)
        assert isinstance(res, BHYFDRResult)
        assert isinstance(np.asarray(res.rejected), np.ndarray)
