# [A_test] module_id: SRC-TST-0653 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_cross_session_knowledge_integrity
# [INVARIANTS] verify_continuity detects hash chain breaks
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cross_session_knowledge_integrity.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.cross_session_knowledge_integrity import (
    CrossSessionKnowledgeIntegrity,
    SessionAnchor,
)


class TestCrossSessionKnowledgeIntegrityInstantiation:
    def test_default_construction(self):
        cski = CrossSessionKnowledgeIntegrity()
        assert cski.anchors == []
        assert cski.genesis_kb_hash == ""

    def test_custom_genesis_hash(self):
        cski = CrossSessionKnowledgeIntegrity(genesis_kb_hash="genesis123")
        assert cski.genesis_kb_hash == "genesis123"


class TestAnchor:
    def test_anchor_first_session(self):
        cski = CrossSessionKnowledgeIntegrity(genesis_kb_hash="genesis")
        anchor = cski.anchor("session-1", {"key": "value"})
        assert isinstance(anchor, SessionAnchor)
        assert anchor.session_id == "session-1"
        assert anchor.prev_anchor_hash == "genesis"
        assert len(anchor.kb_hash) > 0

    def test_anchor_chain(self):
        cski = CrossSessionKnowledgeIntegrity()
        kb1 = {"fact": "A"}
        kb2 = {"fact": "B"}
        a1 = cski.anchor("session-1", kb1)
        a2 = cski.anchor("session-2", kb2)
        assert a2.prev_anchor_hash == a1.kb_hash

    def test_anchor_same_knowledge_same_hash(self):
        cski = CrossSessionKnowledgeIntegrity()
        a1 = cski.anchor("s1", {"k": "v"})
        a2 = cski.anchor("s2", {"k": "v"})
        assert a1.kb_hash == a2.kb_hash

    def test_anchor_empty_knowledge(self):
        cski = CrossSessionKnowledgeIntegrity()
        anchor = cski.anchor("s1", {})
        assert len(anchor.kb_hash) > 0


class TestVerifyContinuity:
    def test_no_anchors(self):
        cski = CrossSessionKnowledgeIntegrity()
        assert cski.verify_continuity() == []

    def test_single_anchor_no_breaks(self):
        cski = CrossSessionKnowledgeIntegrity()
        cski.anchor("s1", {"k": "v"})
        assert cski.verify_continuity() == []

    def test_continuous_chain(self):
        cski = CrossSessionKnowledgeIntegrity()
        cski.anchor("s1", {"k": "v1"})
        cski.anchor("s2", {"k": "v2"})
        assert cski.verify_continuity() == []

    def test_broken_chain(self):
        cski = CrossSessionKnowledgeIntegrity()
        cski.anchor("s1", {"k": "v1"})
        cski.anchor("s2", {"k": "v2"})
        cski.anchors[-1].prev_anchor_hash = "tampered"
        breaks = cski.verify_continuity()
        assert len(breaks) == 1
        assert breaks[0] == 1
