# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_abs001_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_abs001_gate
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_abs001_gate.py
# [TTL] task_bound
"""D-FACTOR-GOV-02 ABS001 上线门禁测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- check_factor_quality: 全过 / IC不足 / IR不足 / OOS不足 / 过拟合 / 多项失败detail
  / 负IC按abs判定通过
- get_gate_spec: 结构 / 字段完整性 / 检查项指标名
"""

from __future__ import annotations

import pytest

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.abs001_gate import (
    GATE_ID,
    check_factor_quality,
    get_gate_spec,
)


def _passing_result() -> EvaluationResult:
    """构造全部门禁通过的评估结果。"""
    return EvaluationResult("test", 0.05, 0.1, 0.6, 0.55, False, 50)


class TestCheckFactorQuality:
    def test_all_pass(self):
        passed, detail = check_factor_quality(_passing_result())
        assert passed is True
        assert detail == ""

    def test_ic_below_threshold(self):
        result = EvaluationResult("test", 0.02, 0.1, 0.6, 0.55, False, 50)
        passed, detail = check_factor_quality(result)
        assert passed is False
        assert "IC" in detail

    def test_ir_below_threshold(self):
        result = EvaluationResult("test", 0.05, 0.1, 0.4, 0.55, False, 50)
        passed, detail = check_factor_quality(result)
        assert passed is False
        assert "IR" in detail

    def test_oos_below_threshold(self):
        result = EvaluationResult("test", 0.05, 0.1, 0.6, 0.45, False, 50)
        passed, detail = check_factor_quality(result)
        assert passed is False
        assert "OOS" in detail

    def test_overfitted(self):
        result = EvaluationResult("test", 0.05, 0.1, 0.6, 0.55, True, 50)
        passed, detail = check_factor_quality(result)
        assert passed is False
        assert "过拟合" in detail

    def test_detail_contains_all_failure_items(self):
        result = EvaluationResult("test", 0.01, 0.1, 0.3, 0.4, True, 50)
        passed, detail = check_factor_quality(result)
        assert passed is False
        assert "IC" in detail
        assert "IR" in detail
        assert "OOS" in detail
        assert "过拟合" in detail

    def test_negative_ic_passes_on_abs(self):
        # abs(-0.05) = 0.05 > 0.03 → IC 通过
        result = EvaluationResult("test", -0.05, 0.1, 0.6, 0.55, False, 50)
        passed, detail = check_factor_quality(result)
        assert passed is True
        assert detail == ""

    def test_boundary_ic_equal_passes(self):
        # abs(0.03) == 0.03, 使用 < 判定 → 不触发失败（边界值通过，对应 op=">="）
        result = EvaluationResult("test", 0.03, 0.1, 0.6, 0.55, False, 50)
        passed, detail = check_factor_quality(result)
        assert passed is True
        assert detail == ""


class TestGetGateSpec:
    def test_structure(self):
        spec = get_gate_spec()
        assert spec["gate_id"] == GATE_ID
        assert spec["gate_id"] == "ABS001"
        assert "description" in spec
        assert isinstance(spec["checks"], list)
        assert len(spec["checks"]) == 4

    def test_checks_have_required_fields(self):
        spec = get_gate_spec()
        for check in spec["checks"]:
            assert "metric" in check
            assert "op" in check
            assert "threshold" in check

    def test_check_metrics(self):
        spec = get_gate_spec()
        metrics = {c["metric"] for c in spec["checks"]}
        assert metrics == {"ic_mean", "ir", "oos_positive_rate", "is_overfitted"}

    def test_thresholds_match_config(self):
        spec = get_gate_spec()
        by_metric = {c["metric"]: c["threshold"] for c in spec["checks"]}
        assert by_metric["ic_mean"] == 0.03
        assert by_metric["ir"] == 0.5
        assert by_metric["oos_positive_rate"] == 0.5
        assert by_metric["is_overfitted"] is False
