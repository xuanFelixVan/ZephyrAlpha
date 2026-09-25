# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_closure_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.closure_check
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_closure_check.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 合法关单（heritage_ref+三理由）全过；缺登记样本全部被拦且拒因机读；
#              签名匹配命中带出配方；对账器只产违例清单不发火（告警归调用方）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.9
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/heritage/test_heritage_closure_check.py
# [TTL] permanent
"""test_heritage_closure_check - 关单登记机检验收（DESIGN 施工项 6）。"""

from __future__ import annotations

from zephyr.ai_layer.heritage.closure_check import (
    alert_message,
    check_signature_match,
    reconcile_closed_orders,
    validate_receipt,
)


def test_valid_receipt_with_heritage_ref() -> None:
    ok, why = validate_receipt("incident_fix", {"heritage_ref": "HT-20260923-001"})
    assert ok and why == "heritage_ref"


def test_valid_receipt_three_reasons() -> None:
    for payload, reason in (
        ({"no_new_pattern": "known_pattern: HT-20260923-001"}, "known_pattern"),
        ({"no_new_pattern": "mechanical_debt"}, "mechanical_debt"),
        ({"no_new_pattern": "dup_of: CASE-2026-0917-001"}, "dup_of"),
        ({"no_new_pattern": {"reason": "known_pattern", "ref": "HT-20260923-002"}}, "known_pattern"),
    ):
        ok, why = validate_receipt("defect_fix", payload)
        assert ok, why
        assert reason in why


def test_invalid_receipts_rejected() -> None:
    cases = [
        ({}, "missing_heritage_registration"),
        ({"heritage_ref": "WO-123"}, "bad_heritage_ref"),
        ({"no_new_pattern": "bogus"}, "bad_no_new_pattern_reason"),
        ({"no_new_pattern": "known_pattern: WO-1"}, "bad_known_pattern_ref"),
        ({"no_new_pattern": "dup_of: HT-20260923-001"}, "bad_dup_of_ref"),
        ({"no_new_pattern": ""}, "bad_no_new_pattern_reason"),
        ({"heritage_ref": "HT-20260923-001", "no_new_pattern": "mechanical_debt"}, "both_heritage_ref_and_no_new_pattern"),
    ]
    for payload, expected in cases:
        ok, why = validate_receipt("redblu_finding", payload)
        assert not ok and why.startswith(expected), (payload, why)


def test_kind_out_of_scope_passes_through() -> None:
    ok, why = validate_receipt("feature_dev", {})
    assert ok and why == "closure_kind_not_in_scope"


def test_signature_match_returns_recipe() -> None:
    rows = [
        {"entry_id": "HT-20260923-001", "pattern_norm": "pathspec_mixup", "occurrence_count": 2,
         "signature": r"pathspec.*positional", "recipe": "改关键字传参+补 smoke"},
        {"entry_id": "HT-20260923-002", "pattern_norm": "yaml_silent", "occurrence_count": 1,
         "signature": "PyYAML 双根键静默覆盖", "recipe": "写后 parse+根键唯一断言"},
    ]
    matches = check_signature_match("报错 pathspec unexpected positional arg", rows)
    assert [m.entry_id for m in matches] == ["HT-20260923-001"]
    assert matches[0].recipe == "改关键字传参+补 smoke", "命中带配方派工"
    multi = check_signature_match("pathspec positional + PyYAML 双根键静默覆盖", rows)
    assert len(multi) == 2
    assert multi[0].entry_id == "HT-20260923-001", "高频坑优先（occurrence_count 降序）"
    assert check_signature_match("无关症状", rows) == []
    assert check_signature_match("", rows) == []


def test_signature_bad_regex_degrades_to_substring() -> None:
    rows = [{"entry_id": "HT-20260923-003", "pattern_norm": "x", "occurrence_count": 1,
             "signature": "([bad", "recipe": "r"}]
    matches = check_signature_match("see ([bad here", rows)
    assert len(matches) == 1, "坏正则退化子串匹配（fail-open 逐条）"


def test_reconcile_closed_orders_violations() -> None:
    receipts = [
        {"work_order_id": "WO-1", "kind": "incident_fix", "heritage_ref": "HT-20260923-001"},
        {"work_order_id": "WO-2", "kind": "defect_fix", "no_new_pattern": "mechanical_debt"},
        {"work_order_id": "WO-3", "kind": "redblu_finding"},
        {"work_order_id": "WO-4", "kind": "feature_dev"},
    ]
    violations = reconcile_closed_orders(receipts)
    assert [v.work_order_id for v in violations] == ["WO-3"]
    assert violations[0].why == "missing_heritage_registration"
    assert "WO-3" in alert_message(violations)
    assert alert_message([]) == ""
