# [A_test] module_id: MOD-GOV_ce_explain_cli | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §

# [MODULE] tests.test_ce_explain_cli

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] pytest tests/test_ce_explain_cli.py -q
# [TTL] task_bound

from __future__ import annotations

import json

import pytest

from zephyr.autonomy_core.context.ce_explain_cli import InclusionRationale, explain_ke


class TestInclusionRationale:
    def test_instantiation_with_all_fields(self):
        r = InclusionRationale(
            ke_id="KE-0001",
            similarity_score=0.9,
            keyword_match=True,
            authority_boost=1.5,
            freshness_score=0.8,
            final_weight=0.95,
        )
        assert r.ke_id == "KE-0001"
        assert r.similarity_score == pytest.approx(0.9)
        assert r.keyword_match is True
        assert r.authority_boost == pytest.approx(1.5)
        assert r.freshness_score == pytest.approx(0.8)
        assert r.final_weight == pytest.approx(0.95)

    def test_instantiation_with_zero_values(self):
        r = InclusionRationale(
            ke_id="",
            similarity_score=0.0,
            keyword_match=False,
            authority_boost=0.0,
            freshness_score=0.0,
            final_weight=0.0,
        )
        assert r.ke_id == ""
        assert r.similarity_score == 0.0
        assert r.keyword_match is False
        assert r.authority_boost == 0.0
        assert r.freshness_score == 0.0
        assert r.final_weight == 0.0

    def test_instantiation_missing_field_raises(self):
        with pytest.raises(TypeError):
            InclusionRationale(ke_id="KE-0001")

    def test_dataclass_dict_roundtrip(self):
        r = InclusionRationale(
            ke_id="KE-0042",
            similarity_score=0.5,
            keyword_match=False,
            authority_boost=0.3,
            freshness_score=0.6,
            final_weight=0.4,
        )
        d = r.__dict__
        r2 = InclusionRationale(**d)
        assert r == r2


class TestExplainKe:
    def test_returns_valid_json(self):
        result = explain_ke("KE-0127")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_output_contains_ke_id(self):
        result = explain_ke("KE-0127")
        parsed = json.loads(result)
        assert parsed["ke_id"] == "KE-0127"

    def test_output_has_all_rationale_fields(self):
        result = explain_ke("KE-0127")
        parsed = json.loads(result)
        expected_keys = {
            "ke_id",
            "similarity_score",
            "keyword_match",
            "authority_boost",
            "freshness_score",
            "final_weight",
        }
        assert set(parsed.keys()) == expected_keys

    def test_with_query_kwarg(self):
        result = explain_ke("KE-0099", query="test query")
        parsed = json.loads(result)
        assert parsed["ke_id"] == "KE-0099"

    def test_empty_ke_id(self):
        result = explain_ke("")
        parsed = json.loads(result)
        assert parsed["ke_id"] == ""

    def test_none_ke_id_produces_null_in_json(self):
        result = explain_ke(None)
        parsed = json.loads(result)
        assert parsed["ke_id"] is None

    def test_numeric_scores_are_floats(self):
        result = explain_ke("KE-0001")
        parsed = json.loads(result)
        for key in ("similarity_score", "authority_boost", "freshness_score", "final_weight"):
            assert isinstance(parsed[key], float), f"{key} should be float"
        assert isinstance(parsed["keyword_match"], bool)
