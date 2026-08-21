# [A_test] module_id: MOD-GOV_selection_result_contract | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_selection_result_contract
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_selection_result_contract.py
# [TTL] task_bound
"""CTR-P1-018 SelectionResult 统一接口契约测试（CAND-SIG-013 晋升，P0-4① 施工）。

覆盖：
- 契约默认值（SelectionResult() 空结果合法、SignalInput 扩展字段默认空）
- urgency 枚举校验（immediate/next_open/gradual 合法，非法值 ValueError）
- confidence ∈ [0,1] 边界校验
- frozen 不可变不变量
"""

from __future__ import annotations

import dataclasses
from datetime import date

import pytest

from zephyr.shared.contracts.selection_result import (
    URGENCY_GRADUAL,
    URGENCY_IMMEDIATE,
    URGENCY_NEXT_OPEN,
    VALID_URGENCY,
    SelectionResult,
    SignalInput,
    TargetPosition,
)


def test_target_position_valid_urgency_all_accepted():
    """urgency 三合法值（21 号 L255-259 映射表）均可构造。"""
    for urg in VALID_URGENCY:
        tp = TargetPosition(symbol="600519", target_weight=0.1, signal_source="t", urgency=urg)
        assert tp.urgency == urg


def test_target_position_invalid_urgency_raises():
    """urgency 非法值 → ValueError（契约枚举校验）。"""
    with pytest.raises(ValueError, match="urgency"):
        TargetPosition(symbol="600519", target_weight=0.1, signal_source="t", urgency="next_week")


def test_selection_result_defaults():
    """轻量 4 字段全带默认值，SelectionResult() 空结果=合法空仓输出。"""
    res = SelectionResult()
    assert res.target_portfolio == []
    assert res.signals == []
    assert res.confidence == 0.0
    assert res.metadata == {}


def test_selection_result_confidence_bounds():
    """confidence 合法域 [0,1]，越界 ValueError。"""
    SelectionResult(confidence=0.0)
    SelectionResult(confidence=1.0)
    with pytest.raises(ValueError, match="confidence"):
        SelectionResult(confidence=-0.1)
    with pytest.raises(ValueError, match="confidence"):
        SelectionResult(confidence=1.1)


def test_signal_input_defaults():
    """SignalInput 核心 3 字段必填，v1.1.1 扩展 signals/metadata 默认空。"""
    si = SignalInput(as_of_date=date(2026, 8, 21), universe=["600519"], regime_budget=0.5)
    assert si.signals == []
    assert si.metadata == {}
    assert si.regime_budget == 0.5  # 数字，非 regime 状态（21 号 L227）


def test_frozen_invariant():
    """三契约 dataclass 均 frozen 不可变。"""
    tp = TargetPosition(symbol="600519", target_weight=0.1, signal_source="t", urgency=URGENCY_IMMEDIATE)
    with pytest.raises(dataclasses.FrozenInstanceError):
        tp.target_weight = 0.2  # type: ignore[misc]
    res = SelectionResult()
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.confidence = 0.5  # type: ignore[misc]


def test_urgency_constants_match_mapping():
    """urgency 常量与 21 号映射表 sleeve 对应关系自洽（打板/事件/多因子）。"""
    assert (URGENCY_IMMEDIATE, URGENCY_NEXT_OPEN, URGENCY_GRADUAL) == (
        "immediate",
        "next_open",
        "gradual",
    )
