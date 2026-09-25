"""test_too_good — C6 too-good 三查执行器：G1-G5 触发线全枚举 + 三查三值 + 三出口路由 + EX-R1 销账。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.ai_layer.comparator.policy import load_comparison_policy
from zephyr.ai_layer.comparator.too_good import (
    ATTRIBUTIONS,
    CHECK_IDS,
    CHECK_ITEM_CATALOG,
    CONCLUSIONS,
    EXITS,
    SPEC_GAMING_CITATION,
    CheckConclusion,
    borderline_value,
    detect_triggers,
    max_borderline_run,
    route_exit,
    run_check,
)

TRIGGERS = load_comparison_policy()["too_good_triggers"]


# ---------------------------------------------------------------------------
# G1 算法/策略
# ---------------------------------------------------------------------------

def test_g1_oos_better_than_is() -> None:
    hit = detect_triggers("G1_algo", {"oos_is_decay": -0.1}, TRIGGERS)
    assert hit.tripped and hit.hits[0].rule == "oos_better_than_is"
    ok = detect_triggers("G1_algo", {"oos_is_decay": 0.12}, TRIGGERS)
    assert not ok.tripped
    skip = detect_triggers("G1_algo", {}, TRIGGERS)
    assert not skip.tripped and "G1.oos_is_decay" in skip.skipped_rules  # 诚实条款：缺证据跳过留痕


def test_g1_sharpe_sigma_and_batch_outlier_and_dsr() -> None:
    m = {"oos_sharpe": 2.0, "is_sharpe": 1.0, "is_sharpe_sigma": 0.3,
         "score": 5.0, "batch_mean": 1.0, "batch_sigma": 1.0, "dsr": 0.995}
    hit = detect_triggers("G1_algo", m, TRIGGERS)
    rules = {h.rule for h in hit.hits}
    assert {"oos_sharpe_exceeds_is_sigma", "batch_outlier", "dsr_too_high"} <= rules
    # 边界：恰在 3σ 内不触发；DSR 0.99 恰等于线触发（>=）
    edge = detect_triggers(
        "G1_algo",
        {"oos_sharpe": 1.9, "is_sharpe": 1.0, "is_sharpe_sigma": 0.3,
         "score": 3.99, "batch_mean": 1.0, "batch_sigma": 1.0, "dsr": 0.99},
        TRIGGERS,
    )
    assert {h.rule for h in edge.hits} == {"dsr_too_high"}


# ---------------------------------------------------------------------------
# G2 模型 / G3 工具 / G4 重放 / G5 通用
# ---------------------------------------------------------------------------

def test_g2_model_triggers() -> None:
    hit = detect_triggers(
        "G2_model",
        {"success_rate": 0.90, "champion_success_rate": 0.65,
         "hallucination_rate": 0.0, "price_cut_ratio": -0.6, "success_noninferior": True},
        TRIGGERS,
    )
    assert {h.rule for h in hit.hits} == {"success_gain_pp", "hallucination_zero", "price_cut_noninferior"}
    no = detect_triggers(
        "G2_model",
        {"success_rate": 0.70, "champion_success_rate": 0.65,
         "hallucination_rate": 0.02, "price_cut_ratio": -0.6, "success_noninferior": False},
        TRIGGERS,
    )
    assert not no.tripped  # 降幅够但非劣不成立 → 不触发


def test_g3_tool_requires_both_conditions() -> None:
    hit = detect_triggers("G3_tool", {"pass_rate": 1.0, "has_trap_items": True}, TRIGGERS)
    assert hit.tripped
    no_trap = detect_triggers("G3_tool", {"pass_rate": 1.0, "has_trap_items": False}, TRIGGERS)
    assert not no_trap.tripped  # 任务集无陷阱题 → 不构成 G3
    unknown_trap = detect_triggers("G3_tool", {"pass_rate": 1.0, "has_trap_items": None}, TRIGGERS)
    assert not unknown_trap.tripped and unknown_trap.skipped_rules == ("G3.pass_rate_perfect",)
    imperfect = detect_triggers("G3_tool", {"pass_rate": 0.98, "has_trap_items": True}, TRIGGERS)
    assert not imperfect.tripped


def test_g4_replay_perfect_delta() -> None:
    hit = detect_triggers("G4_replay", {"jaccard": 1.0, "new_block": 0, "new_pass": 0}, TRIGGERS)
    assert hit.tripped and hit.hits[0].rule == "perfect_delta"  # stub 失真嫌疑优先于庆祝
    near = detect_triggers("G4_replay", {"jaccard": 0.999, "new_block": 0, "new_pass": 0}, TRIGGERS)
    assert not near.tripped
    dirty = detect_triggers("G4_replay", {"jaccard": 1.0, "new_block": 1, "new_pass": 0}, TRIGGERS)
    assert not dirty.tripped
    skip = detect_triggers("G4_replay", {"jaccard": 1.0}, TRIGGERS)
    assert skip.skipped_rules == ("G4.perfect_delta",)


def test_g5_borderline_streak_and_helpers() -> None:
    assert detect_triggers("G5_generic", {"borderline_streak": 3}, TRIGGERS).tripped
    assert not detect_triggers("G5_generic", {"borderline_streak": 2}, TRIGGERS).tripped
    assert borderline_value(0.975, 0.98, 0.01) is True     # 恰好压线带（严格 <）
    assert borderline_value(0.9695, 0.98, 0.01) is False
    assert max_borderline_run([0.001, 0.009, 0.5, 0.002, 0.003, 0.004], 0.01) == 3
    assert max_borderline_run([], 0.01) == 0


# ---------------------------------------------------------------------------
# 配置化（读常量层）与 fail-closed 校验
# ---------------------------------------------------------------------------

def test_triggers_are_configurable_not_hardcoded() -> None:
    custom = {"G5_generic": {"borderline_streak": 5, "epsilon": 0.001}}
    assert not detect_triggers("G5_generic", {"borderline_streak": 3}, custom).tripped
    assert detect_triggers("G5_generic", {"borderline_streak": 5}, custom).tripped


def test_unknown_group_and_missing_keys_rejected() -> None:
    with pytest.raises(ValueError, match="unknown_trigger_group"):
        detect_triggers("G9_x", {}, TRIGGERS)
    with pytest.raises(ValueError, match="trigger_group_missing_keys"):
        detect_triggers("G5_generic", {"borderline_streak": 3}, {"G5_generic": {"borderline_streak": 3}})


# ---------------------------------------------------------------------------
# 三查：三值枚举全枚举（found/cleared/inconclusive）
# ---------------------------------------------------------------------------

def test_run_check_conclusion_matrix() -> None:
    items = CHECK_ITEM_CATALOG["leakage"]
    all_clear = run_check("leakage", {k: True for k in items})
    assert all_clear.conclusion == "cleared"
    found = run_check("leakage", {**{k: True for k in items}, "window_overlap": False})
    assert found.conclusion == "found"
    partial = run_check("leakage", {k: True for k in items[:-1]})  # 缺键=inconclusive（诚实条款）
    assert partial.conclusion == "inconclusive"
    assert CONCLUSIONS == ("found", "cleared", "inconclusive")


def test_run_check_rejects_unknown_check_or_items() -> None:
    with pytest.raises(ValueError, match="unknown_check_id"):
        run_check("gossip", {})
    with pytest.raises(ValueError, match="unknown_check_items"):
        run_check("leakage", {"not_an_item": True})


def test_check_catalog_covers_leakage_taxonomy_and_gaming() -> None:
    # Kapoor & Narayanan 八类分类学的本仓落点 + 钻营三问（DESIGN §2.5）
    assert "window_overlap" in CHECK_ITEM_CATALOG["leakage"]
    assert "preprocessing_leak" in CHECK_ITEM_CATALOG["leakage"]
    assert "question_contamination" in CHECK_ITEM_CATALOG["leakage"]
    assert "exam_hash_consistent" in CHECK_ITEM_CATALOG["leakage"]
    assert set(CHECK_ITEM_CATALOG) == set(CHECK_IDS)
    assert "spec_gaming_reviewed" in CHECK_ITEM_CATALOG["luck_or_gaming"]


# ---------------------------------------------------------------------------
# 三出口路由（建议制，裁定权=评估者）
# ---------------------------------------------------------------------------

def _conclusion(cid: str, conclusion: str) -> CheckConclusion:
    return CheckConclusion(check_id=cid, conclusion=conclusion)


def test_route_exit_priority_and_honesty() -> None:
    cleared = {cid: _conclusion(cid, "cleared") for cid in CHECK_IDS}
    assert route_exit(cleared).recommended_exit is None
    leak = {**cleared, "leakage": _conclusion("leakage", "found")}
    route = route_exit(leak)
    assert (route.recommended_exit, route.attribution) == ("E1", "leakage")
    gaming = {**cleared, "luck_or_gaming": _conclusion("luck_or_gaming", "found")}
    assert route_exit(gaming).recommended_exit == "E3"
    hidden = {**cleared, "hidden_risk": _conclusion("hidden_risk", "found")}
    assert route_exit(hidden).recommended_exit == "E2"
    # 泄漏优先于钻营（可修复泄漏唯一出路=E1）
    both = {**gaming, "leakage": _conclusion("leakage", "found")}
    assert route_exit(both).recommended_exit == "E1"
    # 全部证据不足 → E2 加监控（不硬判）
    uncertain = {cid: _conclusion(cid, "inconclusive") for cid in CHECK_IDS}
    honest = route_exit(uncertain)
    assert honest.recommended_exit == "E2" and honest.attribution is None


def test_empty_conclusions_map_is_none_route() -> None:
    route = route_exit({})
    assert route.recommended_exit is None and "正常流转" in route.rationale


# ---------------------------------------------------------------------------
# EX-R1 销账：specification gaming 引文补核在档（机器可读常量）
# ---------------------------------------------------------------------------

def test_spec_gaming_citation_verified_on_record() -> None:
    assert "Specification gaming" in SPEC_GAMING_CITATION
    assert "deepmind.google" in SPEC_GAMING_CITATION
    assert "Krakovna" in SPEC_GAMING_CITATION and "2020" in SPEC_GAMING_CITATION


def test_exit_and_attribution_enums_aligned_with_policy() -> None:
    assert EXITS == ("E1", "E2", "E3")
    assert ATTRIBUTIONS == ("leakage", "hidden_risk", "luck_or_gaming")
