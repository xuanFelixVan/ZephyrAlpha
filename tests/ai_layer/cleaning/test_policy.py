# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] tests.ai_layer.cleaning.test_policy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.policy
# [CONSUMERS] pytest tests/ai_layer/cleaning/test_policy.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 真 config/cleaning_policy.yaml 只读装载断言（钉住 YAML↔DESIGN §2.2/§2.5 常数一致）；
#              失败用例全走 tmp_path，禁写生产 config/
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.2/§2.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/cleaning/test_policy.py
# [TTL] permanent
"""test_policy - 清洗考尺装载验收（C1 配套）：真值钉住+fail-closed 拒载。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.ai_layer.cleaning.policy import CleaningPolicyError, load_cleaning_policy


def test_load_production_policy_pins_design_values() -> None:
    """真 YAML 只读装载：常数与 DESIGN §2.2/§2.5 预注册值一致（漂移即红）。"""
    policy = load_cleaning_policy()
    assert policy.cold_start_days == 14
    assert policy.cold_start_cards == 100
    assert policy.periodic_rate == 0.20
    assert policy.high_impact_full_check is True
    assert policy.rubric_dimensions == ("fidelity", "completeness", "reproducibility")
    assert policy.rubric_scale_max == 2 and policy.zero_score_fails is True
    assert policy.rewash_max == 1
    assert policy.cascade_upgrade_max_per_card == 1
    assert policy.per_card_token_budget > 0
    assert policy.default_entry_tier == "standard" and policy.upgrade_tier == "premium"
    assert policy.rework_rate_alert == 0.10
    assert policy.forbid_same_vendor and policy.forbid_same_tier and policy.forbid_same_session
    assert policy.task_types == {
        "deep_read": "mining_deep",
        "rewrite": "cleaning_rewrite",
        "translation": "translation_registry",
        "review": "review_judge",
    }
    assert "injection_suspect" in policy.vocab_of("rejection_reasons")
    assert "too_good" in policy.vocab_of("risk_flags")
    assert policy.vocab_of("regime") == frozenset({"趋势", "震荡", "高波", "事件驱动"})
    assert "待填" in policy.placeholder_words


def test_missing_file_rejected(tmp_path: Path) -> None:
    with pytest.raises(CleaningPolicyError, match="文件缺失"):
        load_cleaning_policy(tmp_path / "nope.yaml")


def test_missing_section_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "cleaning_policy.yaml"
    bad.write_text("sampling: {}\n", encoding="utf-8")
    with pytest.raises(CleaningPolicyError, match="缺必填键"):
        load_cleaning_policy(bad)


def test_bad_vocab_type_rejected(tmp_path: Path) -> None:
    body = """
sampling: {cold_start_days: 1, cold_start_cards: 1, periodic_rate: 0.2}
rubric: {dimensions: [fidelity, completeness, reproducibility], scale_max: 2, zero_score_fails: true}
wash: {rewash_max: 1, cascade_upgrade_max_per_card: 1, per_card_token_budget: 1000}
judge: {rework_rate_alert: 0.1}
placeholder_words: [待填]
controlled_vocab: {rejection_reasons: not-a-list}
task_types: {rewrite: cleaning_rewrite}
"""
    bad = tmp_path / "cleaning_policy.yaml"
    bad.write_text(body, encoding="utf-8")
    with pytest.raises(CleaningPolicyError, match="受控枚举须非空序列"):
        load_cleaning_policy(bad)


def test_rubric_dims_must_be_three(tmp_path: Path) -> None:
    body = """
sampling: {cold_start_days: 1, cold_start_cards: 1, periodic_rate: 0.2}
rubric: {dimensions: [fidelity, completeness], scale_max: 2, zero_score_fails: true}
wash: {rewash_max: 1, cascade_upgrade_max_per_card: 1, per_card_token_budget: 1000}
judge: {rework_rate_alert: 0.1}
placeholder_words: [待填]
controlled_vocab:
  rejection_reasons: [wash_failed]
  risk_flags: [too_good]
  regime: [趋势]
  frequency: [日]
  precheck_overall: [pass]
  spec_status: [active]
  review_verdict: [pass]
  stages: [L3]
task_types: {rewrite: cleaning_rewrite}
"""
    bad = tmp_path / "cleaning_policy.yaml"
    bad.write_text(body, encoding="utf-8")
    with pytest.raises(CleaningPolicyError, match="三维"):
        load_cleaning_policy(bad)
