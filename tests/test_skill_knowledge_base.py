# [A_test] module_id: SRC-TST-1632 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md | §
# [MODULE] tests.test_skill_knowledge_base
# [INVARIANTS] SkillKnowledgeBridge must not corrupt entity dedup map
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises TypeError on invalid input types
# [TESTS] tests/test_skill_knowledge_base.py

import pytest
from zephyr.autonomy_core.skill_knowledge_base import SkillKnowledgeBridge


class TestSkillKnowledgeBridgeInstantiation:
    def test_default_instantiation(self):
        bridge = SkillKnowledgeBridge()
        assert isinstance(bridge._synced, set)
        assert isinstance(bridge._entities, list)
        assert isinstance(bridge._log, list)
        assert isinstance(bridge._map, dict)
        assert len(bridge._synced) == 0
        assert len(bridge._entities) == 0

    def test_kb_synced_false_initially(self):
        bridge = SkillKnowledgeBridge()
        assert bridge.kb_synced is False

    def test_kb_synced_true_after_sync(self):
        bridge = SkillKnowledgeBridge()
        bridge.sync_to_kb("skill-1", "body")
        assert bridge.kb_synced is True


class TestExtractFromSkill:
    def test_extracts_constraint_rule(self):
        bridge = SkillKnowledgeBridge()
        body = "CRITICAL: always validate input\nMUST必须确保: data integrity"
        result = bridge.extract_from_skill("skill-a", body)
        types = [e["type"] for e in result]
        assert "constraint_rule" in types

    def test_extracts_forbidden_behavior(self):
        bridge = SkillKnowledgeBridge()
        body = "不可: delete files\nnever: skip validation"
        result = bridge.extract_from_skill("skill-b", body)
        types = [e["type"] for e in result]
        assert "forbidden_behavior" in types

    def test_extracts_allowed_tool(self):
        bridge = SkillKnowledgeBridge()
        body = "use `grep` and `search` tools"
        result = bridge.extract_from_skill("skill-c", body)
        types = [e["type"] for e in result]
        assert "allowed_tool" in types
        tool_values = [e["value"] for e in result if e["type"] == "allowed_tool"]
        assert "grep" in tool_values
        assert "search" in tool_values

    def test_empty_body_returns_empty(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.extract_from_skill("skill-d", "")
        assert result == []

    def test_no_matching_patterns(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.extract_from_skill("skill-e", "plain text with no patterns")
        assert result == []

    def test_entities_have_source_and_timestamp(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.extract_from_skill("skill-f", "CRITICAL: check input")
        assert len(result) == 1
        assert result[0]["source"] == "skill-f"
        assert "extracted_at" in result[0]


class TestSyncToKb:
    def test_sync_extracts_and_stores(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.sync_to_kb("skill-1", "CRITICAL: validate input")
        assert result["skill_id"] == "skill-1"
        assert result["entities_extracted"] >= 1
        assert result["entities_new"] >= 1
        assert result["kb_synced"] is True

    def test_sync_deduplicates(self):
        bridge = SkillKnowledgeBridge()
        bridge.sync_to_kb("skill-1", "CRITICAL: validate input")
        result = bridge.sync_to_kb("skill-1", "CRITICAL: validate input")
        assert result["entities_new"] == 0

    def test_sync_empty_body(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.sync_to_kb("skill-2", "")
        assert result["entities_extracted"] == 0
        assert result["entities_new"] == 0
        assert result["skill_id"] == "skill-2"

    def test_sync_tracks_total_entities(self):
        bridge = SkillKnowledgeBridge()
        bridge.sync_to_kb("s1", "CRITICAL: rule1")
        result = bridge.sync_to_kb("s2", "CRITICAL: rule2")
        assert result["total"] == 2

    def test_sync_logs_entry(self):
        bridge = SkillKnowledgeBridge()
        bridge.sync_to_kb("skill-x", "CRITICAL: test")
        assert len(bridge._log) == 1
        assert bridge._log[0]["action"] == "sync"
        assert bridge._log[0]["skill"] == "skill-x"


class TestSyncFromKb:
    def test_sync_from_kb_unsynced_skill(self):
        bridge = SkillKnowledgeBridge()
        result = bridge.sync_from_kb("skill-unknown")
        assert result["kb_synced"] is False
        assert result["entities"] == 0

    def test_sync_from_kb_returns_relevant_entities(self):
        bridge = SkillKnowledgeBridge()
        bridge.sync_to_kb("skill-1", "CRITICAL: validate input")
        result = bridge.sync_from_kb("skill-2")
        assert result["kb_synced"] is False
        assert isinstance(result["data"], list)

    def test_sync_from_kb_limits_to_20(self):
        bridge = SkillKnowledgeBridge()
        for i in range(25):
            bridge.sync_to_kb(f"src-{i}", f"CRITICAL: rule{i}")
        bridge._synced.add("target-skill")
        result = bridge.sync_from_kb("target-skill")
        assert result["kb_synced"] is True
        assert len(result["data"]) <= 20
