# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-07 三级判定测试——纯函数模块（无 IO 依赖）。

覆盖：
- judge_factor: 高IC=优秀 / 中IC=合格 / 低IC=淘汰 / 负IC绝对值判定 / 边界值
- judge_batch: 批量判定多因子
"""

from __future__ import annotations

import pytest

from zephyr.factor.core.evaluation.backtest import EvaluationResult

three_level_judgment = pytest.importorskip("zephyr.factor.analysis.three_level_judgment")

judge_factor = three_level_judgment.judge_factor
judge_batch = three_level_judgment.judge_batch


def _make_result(fid: str, ic: float = 0.05) -> EvaluationResult:
    return EvaluationResult(
        factor_id=fid,
        ic_mean=ic,
        ic_std=0.1,
        ir=0.6,
        oos_positive_rate=0.55,
        is_overfitted=False,
        sample_size=50,
    )


class TestJudgeFactor:
    def test_high_ic_excellent(self):
        assert judge_factor(ic=0.15) == "优秀"

    def test_mid_ic_pass(self):
        assert judge_factor(ic=0.07) == "合格"

    def test_low_ic_reject(self):
        assert judge_factor(ic=0.02) == "淘汰"

    def test_zero_ic_reject(self):
        assert judge_factor(ic=0.0) == "淘汰"

    def test_negative_ic_high_abs_excellent(self):
        # |IC| > 0.1 → 优秀
        assert judge_factor(ic=-0.15) == "优秀"

    def test_negative_ic_mid_abs_pass(self):
        # |IC| > 0.05 → 合格
        assert judge_factor(ic=-0.07) == "合格"

    def test_negative_ic_low_abs_reject(self):
        assert judge_factor(ic=-0.02) == "淘汰"

    def test_boundary_excellent(self):
        # IC = 0.1 → |IC| >= 0.1 → 优秀
        assert judge_factor(ic=0.1) == "优秀"
        assert judge_factor(ic=-0.1) == "优秀"

    def test_boundary_pass(self):
        # IC = 0.05 → |IC| >= 0.05 → 合格
        assert judge_factor(ic=0.05) == "合格"
        assert judge_factor(ic=-0.05) == "合格"

    def test_boundary_below_pass(self):
        # IC = 0.049 → 淘汰
        assert judge_factor(ic=0.049) == "淘汰"
        assert judge_factor(ic=-0.049) == "淘汰"

    def test_ir_oos_rate_unused(self):
        # ir / oos_rate 不影响判定，只基于 IC 绝对值
        assert judge_factor(ic=0.15, ir=0.0, oos_rate=0.0) == "优秀"
        assert judge_factor(ic=0.15, ir=-1.0, oos_rate=0.1) == "优秀"
        assert judge_factor(ic=0.02, ir=2.0, oos_rate=0.9) == "淘汰"


class TestJudgeBatch:
    def test_batch_mixed(self):
        results = {
            "mom_5d": _make_result("mom_5d", ic=0.12),  # 优秀
            "value_5d": _make_result("value_5d", ic=0.06),  # 合格
            "junk": _make_result("junk", ic=0.01),  # 淘汰
        }
        verdicts = judge_batch(results)
        assert verdicts["mom_5d"] == "优秀"
        assert verdicts["value_5d"] == "合格"
        assert verdicts["junk"] == "淘汰"
        assert len(verdicts) == 3

    def test_batch_empty(self):
        verdicts = judge_batch({})
        assert verdicts == {}

    def test_batch_negative_ic(self):
        results = {
            "f1": _make_result("f1", ic=-0.15),  # |IC|=0.15 → 优秀
            "f2": _make_result("f2", ic=-0.03),  # 淘汰
        }
        verdicts = judge_batch(results)
        assert verdicts["f1"] == "优秀"
        assert verdicts["f2"] == "淘汰"

    def test_batch_boundary(self):
        results = {
            "b_excellent": _make_result("b_excellent", ic=0.1),
            "b_pass": _make_result("b_pass", ic=0.05),
            "b_reject": _make_result("b_reject", ic=0.049),
        }
        verdicts = judge_batch(results)
        assert verdicts["b_excellent"] == "优秀"
        assert verdicts["b_pass"] == "合格"
        assert verdicts["b_reject"] == "淘汰"
