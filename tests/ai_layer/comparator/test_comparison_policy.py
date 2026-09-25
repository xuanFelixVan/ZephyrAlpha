"""test_comparison_policy — C1 判据常量文件：真源文件全节齐 + fail-closed 加载 + 头部治理锚定。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.comparator.experiment_store import STATUS_FLOW, VERDICTS
from zephyr.ai_layer.comparator.policy import (
    REQUIRED_SECTIONS,
    TOO_GOOD_TRIGGER_IDS,
    ComparePolicyError,
    load_comparison_policy,
)
from zephyr.ai_layer.comparator.too_good import ATTRIBUTIONS

POLICY_TEXT = Path("config/comparison_policy.yaml").read_text(encoding="utf-8")


def test_real_policy_file_loads_all_sections() -> None:
    policy = load_comparison_policy()
    for section in REQUIRED_SECTIONS:
        assert section in policy, section
    assert policy["policy_id"] == "comparison_policy_v1"
    assert tuple(policy["too_good_triggers"]) == TOO_GOOD_TRIGGER_IDS


def test_significance_values_match_design_anchors() -> None:
    sig = load_comparison_policy()["significance"]
    assert sig["alpha"] == 0.05                       # OBJ_M §4.2
    assert sig["fdr_q"] == 0.10                       # bhy_fdr DEFAULT_Q
    assert sig["icir_min"] == 0.5
    assert sig["effect_win_pp"] == 5.0
    assert sig["effect_cost_cut"] == -0.20
    assert sig["noninferior_pp"] == -5.0
    assert sig["tier_b_min_n"] == 30
    assert sig["bothwin_decay_max"] == 0.5
    t = sig["tournament"]
    assert t["shortlist_trigger_n"] == 5 and t["shortlist_k"] > 0 and t["rounds"] == 2


def test_too_good_trigger_values_match_design() -> None:
    tri = load_comparison_policy()["too_good_triggers"]
    g1 = tri["G1_algo"]
    assert g1["oos_is_decay_negative"] is True
    assert g1["oos_sharpe_sigma"] == 3.0 and g1["batch_sigma"] == 3.0 and g1["dsr_line"] == 0.99
    g2 = tri["G2_model"]
    assert g2["success_gain_pp"] == 20.0 and g2["hallucination_zero"] is True and g2["price_cut"] == -0.50
    g3 = tri["G3_tool"]
    assert g3["pass_rate_perfect"] == 1.0 and g3["require_trap_items"] is True
    g4 = tri["G4_replay"]
    assert g4["jaccard_perfect"] == 1.0 and g4["new_block_zero"] == 0 and g4["new_pass_zero"] == 0
    g5 = tri["G5_generic"]
    assert g5["borderline_streak"] == 3 and 0 < g5["epsilon"] < 1


def test_controlled_vocabularies_align_with_store_and_exits() -> None:
    policy = load_comparison_policy()
    assert set(policy["verdict_values"]) == set(VERDICTS)
    assert tuple(policy["status_flow"]) == STATUS_FLOW
    for reason in ("tie_no_gain", "lost_to_champion", "rejected_too_good", "unfair_conditions"):
        assert reason in policy["rejection_reasons"]
    assert tuple(policy["too_good_attribution"]) == ATTRIBUTIONS
    assert set(policy["too_good_attribution"]) == {"leakage", "hidden_risk", "luck_or_gaming"}
    assert policy["tie_reexam_conditions"] == [
        "criteria_version_changed", "window_rolled_new_data", "fairness_params_changed",
    ]


def test_governance_header_netzero_and_ratification_anchor() -> None:
    head = POLICY_TEXT[:2000]
    assert "净零声明" in head                     # README §3 净零批次
    assert "ROOR 挂接" in head                    # RULE-REGISTRY
    assert "初值追认" in head and "Owner 夜批授权" in head   # L4-#1 已销项批注
    assert "OBJ_R" in head                        # 改动流程锚定
    assert "docs/_working/ai_layer_vision/L4_compare/DESIGN.md" in head


def test_missing_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ComparePolicyError, match="缺文件"):
        load_comparison_policy(tmp_path / "nope.yaml")


def test_missing_section_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "partial.yaml"
    body = {k: v for k, v in yaml.safe_load(POLICY_TEXT).items() if k != "significance"}
    path.write_text(yaml.safe_dump(body), encoding="utf-8")
    with pytest.raises(ComparePolicyError, match="缺节:significance"):
        load_comparison_policy(path)


def test_missing_trigger_group_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "partial.yaml"
    body = yaml.safe_load(POLICY_TEXT)
    del body["too_good_triggers"]["G3_tool"]
    path.write_text(yaml.safe_dump(body), encoding="utf-8")
    with pytest.raises(ComparePolicyError, match="G1-G5 五组"):
        load_comparison_policy(path)


def test_bad_yaml_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "broken.yaml"
    path.write_text("a: [unclosed", encoding="utf-8")
    with pytest.raises(ComparePolicyError, match="坏 YAML"):
        load_comparison_policy(path)


def test_top_level_non_mapping_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ComparePolicyError, match="顶层需映射"):
        load_comparison_policy(path)
