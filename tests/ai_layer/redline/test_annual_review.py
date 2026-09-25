# [A_test] module_id: zephyr.ai_layer.redline.annual_review | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_annual_review
# [MODULE] tests.ai_layer.redline.test_annual_review
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.annual_review
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_annual_review.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：S8 年审=流程挂 OBJ_R 流水线有登记
#              （立案包携带 OBJ_R 四步锚+ruling_registry 回填位）；输出落 tmp_path
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_annual_review.py — S8 负面清单年审流水线挂接单测（三探测口+四固定核对项+立案包）。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.redline.annual_review import (
    AnnualReviewInput,
    AnnualReviewInputError,
    build_annual_review_case,
    check_hmac_era_coverage,
    check_manifest_freshness,
    check_protected_paths_alignment,
    check_real_key_naming,
    detail_refinement_candidates,
    fact_redline_candidates,
    retire_candidates,
    tombstone_consistency,
    write_case,
)


def test_fact_redline_candidate_two_same_kind_not_listed():
    stops = [{"category": "删 .runtime 审计"}, {"category": "删 .runtime 审计"}]
    candidates = fact_redline_candidates(stops, ["付费动作"])
    assert candidates == [
        {"category": "删 .runtime 审计", "events": 2, "reason": "应有而未列（同类人工叫停≥2 次）"}
    ]


def test_fact_redline_single_event_or_listed_not_candidate():
    assert fact_redline_candidates([{"category": "一次性误触"}], []) == []
    assert fact_redline_candidates(
        [{"category": "X"}, {"category": "X"}], ["X"]
    ) == [], "清单已列≠事实红线候选"


def test_detail_refinement_high_freq_warns():
    candidates = detail_refinement_candidates({"NL-5": 12, "NL-2": 3}, threshold_per_quarter=10)
    assert candidates == [{"rule_id": "NL-5", "warns": 12, "threshold_per_quarter": 10}]


def test_retire_candidate_four_zero_quarters():
    triggers = {
        "NL-A": (0, 0, 0, 0),
        "NL-B": (5, 0, 0, 0),
        "NL-C": (0, 0, 0),  # 样本不足不判
    }
    candidates = retire_candidates(triggers)
    assert candidates == [{"rule_id": "NL-A", "quarters_zero": 4}]


def test_real_key_naming_check():
    records = [
        {"key": "QMT" "_REAL_PATH", "is_live": True},
        {"key": "NEW_GATEWAY_LIVE_KEY", "is_live": True},
        {"key": "QMT_SIM_PATH", "is_live": False},
        {"key": "MYSTERY_KEY", "is_live": True},  # 实盘但无命名 → 违例
    ]
    assert check_real_key_naming(records) == ["MYSTERY_KEY"]


def test_protected_paths_alignment_diff():
    result = check_protected_paths_alignment(
        ["AGENTS.md", ".git/**"], ["AGENTS.md", "project_rules.md"]
    )
    assert result["missing"] == ["project_rules.md"]
    assert result["extra"] == [".git/**"]


def test_hmac_era_coverage():
    assert check_hmac_era_coverage(["2026-05-01T00:00:00+00:00"], "2026-05-02T00:00:00+00:00") == []
    issues = check_hmac_era_coverage(["2026-06-01T00:00:00+00:00"], "2026-05-02T00:00:00+00:00")
    assert issues and "era 覆盖缺口" in issues[0]
    assert check_hmac_era_coverage([], "anything") and "eras 空" in check_hmac_era_coverage([], "x")[0]


def test_manifest_freshness(tmp_path: Path):
    manifest = tmp_path / "no_delete_tables.yaml"
    manifest.write_text(
        yaml.safe_dump({"generated_at": "2020-01-01T00:00:00+00:00"}, sort_keys=False),
        encoding="utf-8",
    )
    stale = check_manifest_freshness(manifest, max_age_days=35)
    assert stale["fresh"] is False
    assert check_manifest_freshness(tmp_path / "nope.yaml")["fresh"] is False, "清单缺席=fresh False"
    fresh = check_manifest_freshness(
        manifest,
        max_age_days=35,
        as_of=datetime(2020, 1, 5, tzinfo=timezone.utc),
    )
    assert fresh["fresh"] is True
    assert fresh["age_days"] == 4.0


def test_tombstone_consistency_report_only():
    result = tombstone_consistency({"L6": "deprecated", "library": "deprecated", "mining": None})
    assert result["consistent"] is False
    assert result["domains_missing"] == ["mining"]
    ok = tombstone_consistency({"L6": "deprecated", "library": "deprecated"})
    assert ok["consistent"] is True


def test_build_case_schema_and_obj_r_anchor():
    case = build_annual_review_case(
        AnnualReviewInput(
            review_date="2026-09-23",
            emergency_stops=[{"category": "X"}, {"category": "X"}],
            listed_patterns=(),
            near_miss_warns={"NL-5": 20},
            rule_triggers_by_quarter={"NL-9": (0, 0, 0, 0)},
            fixed_checklist={"real_key_naming": [], "freshness": {"fresh": True}},
            tombstone=tombstone_consistency({"L6": "deprecated"}),
        ),
        proposal_id="NLAR-20260923-001",
    )
    assert case["status"] == "draft", "恒 draft：自动化的是提案与证据，不是裁决"
    assert case["proposal_type"] == "negative_list_annual_review"
    steps = case["obj_r_pipeline"]["steps"]
    assert steps == ["AI 年审报告提案", "治理立案", "Owner 修标", "重考历史（新清单对历史拦截集重放，误拦率不升才准换）"]
    assert case["obj_r_pipeline"]["ruling_registry_ref"] == "", "立案后回填裁定号（RULE-RULING）"
    assert case["probe_fact_redlines"][0]["category"] == "X"
    assert case["probe_detail_refinements"][0]["rule_id"] == "NL-5"
    assert case["probe_retirements"] == [{"rule_id": "NL-9", "quarters_zero": 4}]
    assert "误拦率不升才准换" in case["replay_promise"]


def test_build_case_rejects_empty_proposal_id():
    with pytest.raises(AnnualReviewInputError):
        build_annual_review_case(AnnualReviewInput(review_date="2026-09-23"), proposal_id="  ")


def test_write_case_roundtrip(tmp_path: Path):
    case = build_annual_review_case(
        AnnualReviewInput(review_date="2026-09-23"), proposal_id="NLAR-20260923-001"
    )
    out_path = write_case(case, tmp_path / "proposals")
    loaded = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert loaded["proposal_id"] == "NLAR-20260923-001"
    assert loaded["status"] == "draft"
