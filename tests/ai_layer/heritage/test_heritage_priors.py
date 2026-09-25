# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_priors
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.priors; zephyr.ai_layer.heritage.policy
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_priors.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] factor 越界拒收（不截断）；排除词表每单保底 1 组；冻结判定三态全枚举；
#              覆盖率/前两月链全部注入（纯函数面零 DB），DB 读数面不进单测
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.6（D-L7-03 四约束）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PriorFactorOutOfRange 断言；全滤词场景保底第一组
# [TESTS] tests/ai_layer/heritage/test_heritage_priors.py
# [TTL] permanent
"""test_heritage_priors - L1 先验四约束验收（DESIGN 施工项 4）。"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.heritage.priors import (
    PriorFactorOutOfRange,
    HeritagePriors,
    apply_exclusion,
    daily_share_exceeded,
    diversity_freeze,
    validate_prior_factor,
)
from zephyr.ai_layer.heritage.policy import load_policy

POLICY = load_policy()


def test_factor_out_of_range_rejected() -> None:
    assert validate_prior_factor(1.0, POLICY) == 1.0
    assert validate_prior_factor(2.0, POLICY) == 2.0
    assert validate_prior_factor(1.35, POLICY) == 1.35
    for bad in (0.9, 2.01, -1.0, 3.0):
        with pytest.raises(PriorFactorOutOfRange):
            validate_prior_factor(bad, POLICY)


def test_apply_exclusion_keeps_at_least_one_group() -> None:
    kept, dropped = apply_exclusion([["alpha"], ["bad_word", "beta"]], ["bad_word"])
    assert kept == [["alpha"]] and dropped == [["bad_word", "beta"]]
    all_hit_kept, all_hit_dropped = apply_exclusion([["bad_word"], ["bad_word", "x"]], ["bad_word"])
    assert all_hit_kept == [["bad_word"]], "全滤场景保底保留第一组（只滤词不灭矿脉）"
    assert all_hit_dropped == [["bad_word", "x"]]
    no_excl_kept, no_excl_dropped = apply_exclusion([["a"], ["b"]], [])
    assert no_excl_kept == [["a"], ["b"]] and no_excl_dropped == []


def test_diversity_freeze_three_states() -> None:
    frozen, why = diversity_freeze(59.0, None, None, POLICY)
    assert frozen and "coverage=" in why, "低于 60% 冻结线→冻结"
    healthy, _ = diversity_freeze(61.0, 60.0, 59.0, POLICY)
    assert not healthy, "上升趋势不冻结"
    declined, why2 = diversity_freeze(62.0, 63.0, 64.0, POLICY)
    assert declined and "declined_2" in why2, "连续 2 月下降→冻结"
    no_hist, _ = diversity_freeze(70.0, None, None, POLICY)
    assert not no_hist, "无历史+高于冻结线=正常态"


def test_daily_share_exceeded() -> None:
    assert not daily_share_exceeded(4, 10, POLICY), "40%≤50% 未超"
    assert daily_share_exceeded(6, 10, POLICY), "60%>50% 超限"
    assert not daily_share_exceeded(3, 0, POLICY), "零开单日不算超限"


def test_build_prior_response_assembly_and_freeze() -> None:
    priors = HeritagePriors("ai_heritage", policy=POLICY)
    row = {"prior_factor": 1.3, "rationale_refs": ["HT-20260923-001"]}
    resp = priors.build_prior_response(row, ["evil_kw"], coverage_pct=65.0)
    assert resp == {
        "prior_factor": 1.3,
        "rationale_refs": ["HT-20260923-001"],
        "exclusion_keywords": ["evil_kw"],
        "frozen": False,
    }
    frozen_resp = priors.build_prior_response(row, [], coverage_pct=50.0)
    assert frozen_resp["prior_factor"] == 1.0 and frozen_resp["frozen"], "冻结态 factor 钳回 1.0"
    with pytest.raises(PriorFactorOutOfRange):
        priors.build_prior_response({"prior_factor": 2.5, "rationale_refs": []}, [], coverage_pct=65.0)
    empty = priors.build_prior_response(None, [], coverage_pct=None)
    assert empty["prior_factor"] == 1.0 and empty["rationale_refs"] == [], "格缺席=空先验正常态"


def test_apply_exclusion_word_matching_semantics() -> None:
    kept, _ = apply_exclusion([["kline_gap"], ["volume"]], ["kline_gap"])
    assert kept == [["volume"]]
