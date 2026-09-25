# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_policies
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.policy
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_policies.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 真配置装载成功（config/heritage_policy.yaml——本批交付件）；缺文件/缺键/坏类型/坏正则
#              全部 HeritagePolicyError fail-closed（不静默回退默认值）
# [MODIFY-GUARD] config/heritage_policy.yaml（OBJ_R 流水线）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HeritagePolicyError 断言
# [TESTS] tests/ai_layer/heritage/test_heritage_policies.py
# [TTL] permanent
"""test_heritage_policies - heritage_policy.yaml 装载器验收。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.ai_layer.heritage.policy import HeritagePolicyError, load_policy


def test_load_real_config() -> None:
    policy = load_policy()
    assert policy.policy_id == "heritage_policy_v1"
    assert policy.anti_incest.prior_factor_min == 1.0
    assert policy.anti_incest.prior_factor_max == 2.0
    assert policy.anti_incest.l7_prior_daily_share_max == 0.50
    assert policy.anti_incest.total_cells == 48
    assert policy.forget.defect.compressed_zero_quarters == 4
    assert policy.forget.elite.keep_per_cell == 3
    assert policy.forget.elite.tombstone_windows == 2
    assert policy.forget.elite.compressed_after_months == 12
    assert policy.forget.criteria.keep_per_venue == 3
    assert policy.registration.simhash_hamming_max == 3
    assert "TP-" in policy.registration.source_ref_prefixes, "红蓝 R1-B3 前缀白名单"
    assert policy.closure.kinds_requiring_heritage >= {"incident_fix", "defect_fix", "redblu_finding"}


def test_missing_file_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(HeritagePolicyError, match="policy_file_missing"):
        load_policy(tmp_path / "nope.yaml")


def test_missing_key_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "p.yaml"
    path.write_text("policy_id: x\nregistration: {}\n", encoding="utf-8")
    with pytest.raises(HeritagePolicyError, match="policy_missing_key"):
        load_policy(path)


_REG_OK = (
    "registration:\n"
    "  min_plain_zh_chars: 10\n  min_narrative_chars: 30\n  min_recipe_delta_chars: 20\n"
    "  simhash_hamming_max: 3\n  source_ref_prefixes: [SW-]\n  defect_source_kinds: [work_order]\n"
)


def test_bad_type_and_regex_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "p.yaml"
    path.write_text(
        "policy_id: x\n" + _REG_OK + "  pattern_slug_re: '^[a-z]+$'\n"
        "anti_incest:\n  prior_factor_min: bad_float\n"
        "forget: {}\nclosure: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(HeritagePolicyError, match="policy_bad_type"):
        load_policy(path)
    path2 = tmp_path / "p2.yaml"
    path2.write_text(
        "policy_id: x\n" + _REG_OK + "  pattern_slug_re: '([bad'\n"
        "anti_incest:\n  prior_factor_min: 1.0\n  prior_factor_max: 2.0\n"
        "  l7_prior_daily_share_max: 0.5\n  keyword_groups_min_keep: 1\n"
        "  coverage_freeze_line_pct: 60.0\n  coverage_decline_months: 2\n"
        "  total_cells: 48\n  prior_window_days: 90\n"
        "forget: {}\nclosure: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(HeritagePolicyError, match="policy_bad_regex"):
        load_policy(path2)


def test_forget_required_keys_per_kind(tmp_path: Path) -> None:
    path = tmp_path / "p.yaml"
    path.write_text(
        "policy_id: x\n"
        "registration:\n  min_plain_zh_chars: 10\n  min_narrative_chars: 30\n  min_recipe_delta_chars: 20\n"
        "  simhash_hamming_max: 3\n  source_ref_prefixes: [SW-]\n  defect_source_kinds: [work_order]\n"
        "  pattern_slug_re: '^[a-z]+$'\n"
        "anti_incest:\n  prior_factor_min: 1.0\n  prior_factor_max: 2.0\n  l7_prior_daily_share_max: 0.5\n"
        "  keyword_groups_min_keep: 1\n  coverage_freeze_line_pct: 60.0\n  coverage_decline_months: 2\n"
        "  total_cells: 48\n  prior_window_days: 90\n"
        "forget:\n  defect: {}\n"  # defect 缺 compressed_zero_quarters → 必填键拒收
        "closure:\n  kinds_requiring_heritage: [incident_fix]\n  no_new_pattern_reasons: [dup_of]\n",
        encoding="utf-8",
    )
    with pytest.raises(HeritagePolicyError, match="policy_missing_key:forget.defect"):
        load_policy(path)
