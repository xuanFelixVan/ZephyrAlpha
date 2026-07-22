# [A_test] module_id: MOD-GOV_skill_ontology | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_ontology
# [INVARIANTS] SkillOntology methods are classmethods; no state mutation between tests
# [MODIFY-GUARD] changes require review of skill_ontology.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] extract_entities returns list; match_entities returns dict; detect_gaps returns dict
# [TESTS] pytest tests/test_skill_ontology.py -q
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.skills.skill_ontology import SkillOntology


class TestSkillOntologyExtractEntities:
    def test_extracts_module_ids(self):
        content = "This relates to MOD-INF-019 and MOD-INF-003."
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "module"]
        assert "MOD-INF-019" in values
        assert "MOD-INF-003" in values

    def test_extracts_gates(self):
        content = "Gate G12 failed and G34 passed."
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "gate"]
        assert "G12" in values
        assert "G34" in values

    def test_extracts_skill_ids(self):
        content = "SKILL-DOM-ONTOLOGY-001 is active."
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "skill"]
        assert "SKILL-DOM-ONTOLOGY-001" in values

    def test_extracts_phase(self):
        content = "Phase: deployment and Phase#build"
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "phase"]
        assert "deployment" in values
        assert "build" in values

    def test_extracts_api_endpoint(self):
        content = "API: /v1/skills and endpoint: /v2/gates"
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "api_endpoint"]
        assert "/v1/skills" in values
        assert "/v2/gates" in values

    def test_empty_input_returns_empty_list(self):
        result = SkillOntology.extract_entities("")
        assert result == []

    def test_no_entities_returns_empty_list(self):
        result = SkillOntology.extract_entities("just plain text with no patterns")
        assert result == []

    def test_deduplication(self):
        content = "MOD-INF-019 and again MOD-INF-019"
        result = SkillOntology.extract_entities(content)
        module_entries = [e for e in result if e["type"] == "module"]
        assert len(module_entries) == 1

    def test_extracts_database_table(self):
        content = "Table: `users` and table: orders"
        result = SkillOntology.extract_entities(content)
        values = [e["value"] for e in result if e["type"] == "database_table"]
        assert "users" in values
        assert "orders" in values


class TestSkillOntologyMatchEntities:
    def test_match_with_kb_entities(self):
        extracted = [
            {"type": "module", "value": "MOD-INF-019"},
            {"type": "gate", "value": "G12"},
        ]
        kb_entities = [
            {"type": "module", "value": "MOD-INF-019"},
        ]
        result = SkillOntology.match_entities(extracted, kb_entities)
        assert result["matched_count"] == 1
        assert result["unmatched_count"] == 1
        assert result["total_extracted"] == 2

    def test_match_without_kb_entities(self):
        extracted = [
            {"type": "module", "value": "MOD-INF-019"},
        ]
        result = SkillOntology.match_entities(extracted, kb_entities=None)
        assert result["matched_count"] == 1
        assert result["unmatched_count"] == 0
        assert result["match_rate"] == 100.0

    def test_empty_extracted(self):
        result = SkillOntology.match_entities([], kb_entities=None)
        assert result["total_extracted"] == 0
        assert result["matched_count"] == 0
        assert result["match_rate"] == 0.0

    def test_match_rate_calculation(self):
        extracted = [
            {"type": "module", "value": "MOD-INF-019"},
            {"type": "gate", "value": "G12"},
            {"type": "phase", "value": "build"},
        ]
        kb_entities = [
            {"type": "module", "value": "MOD-INF-019"},
            {"type": "gate", "value": "G12"},
        ]
        result = SkillOntology.match_entities(extracted, kb_entities)
        assert result["match_rate"] == pytest.approx(66.7, abs=0.1)
        assert result["confidence"] == pytest.approx(0.67, abs=0.01)

    def test_empty_kb_entities_list(self):
        extracted = [{"type": "module", "value": "MOD-INF-019"}]
        result = SkillOntology.match_entities(extracted, kb_entities=[])
        assert result["matched_count"] == 0
        assert result["unmatched_count"] == 1


class TestSkillOntologyDetectGaps:
    def test_detect_gaps_with_missing_kb_entities(self):
        body = "Uses MOD-INF-019 and G12"
        kb_entities = [{"type": "module", "value": "MOD-INF-019"}]
        result = SkillOntology.detect_gaps("SKILL-TEST-001", body, kb_entities)
        assert result["skill_id"] == "SKILL-TEST-001"
        assert result["gaps_found"] >= 1
        assert result["aligned"] is False

    def test_detect_gaps_fully_aligned(self):
        body = "Uses MOD-INF-019"
        kb_entities = [{"type": "module", "value": "MOD-INF-019"}]
        result = SkillOntology.detect_gaps("SKILL-TEST-002", body, kb_entities)
        assert result["alignment_score"] >= 70.0
        assert result["aligned"] is True

    def test_detect_gaps_no_kb(self):
        body = "Uses MOD-INF-019 and G12"
        result = SkillOntology.detect_gaps("SKILL-TEST-003", body, kb_entities=None)
        assert result["alignment_score"] == 100.0
        assert result["aligned"] is True
        assert result["gaps_found"] == 0

    def test_detect_gaps_empty_body(self):
        result = SkillOntology.detect_gaps("SKILL-TEST-004", "", kb_entities=None)
        assert result["entities_extracted"] == 0
        assert result["alignment_score"] == 0.0

    def test_gap_has_correct_kb_category(self):
        body = "G12 failed"
        kb_entities = []
        result = SkillOntology.detect_gaps("SKILL-TEST-005", body, kb_entities)
        gate_gaps = [g for g in result["gaps"] if g["type"] == "gate"]
        assert len(gate_gaps) == 1
        assert gate_gaps[0]["kb_category"] == "Gate"
