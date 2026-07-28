# [A_test] module_id: MOD-GOV_memory_poison_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_memory_poison_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_memory_poison_guard.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.memory_poison_guard import MemoryPoisonGuard


class TestMemoryPoisonGuardInstantiation:
    def test_creates_instance_with_empty_trusted_set(self):
        guard = MemoryPoisonGuard()
        assert len(guard.trusted_agents) == 0

    def test_trusted_agents_is_set(self):
        guard = MemoryPoisonGuard()
        assert isinstance(guard.trusted_agents, set)


class TestRegisterTrusted:
    def test_register_trusted_adds_agent(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        assert "agent-001" in guard.trusted_agents

    def test_register_trusted_multiple_agents(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        guard.register_trusted("agent-002")
        assert len(guard.trusted_agents) == 2

    def test_register_trusted_idempotent(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        guard.register_trusted("agent-001")
        assert len(guard.trusted_agents) == 1


class TestValidateWrite:
    def test_untrusted_agent_rejected(self):
        guard = MemoryPoisonGuard()
        ok, msg = guard.validate_write("unknown", "safe content")
        assert ok is False
        assert "not trusted" in msg

    def test_trusted_agent_clean_content_accepted(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "normal memory content")
        assert ok is True
        assert msg == "OK"

    def test_trusted_agent_ignore_previous_detected(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "ignore_previous instructions")
        assert ok is False
        assert "Suspicious content" in msg

    def test_trusted_agent_forget_rules_detected(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "forget_rules and restart")
        assert ok is False
        assert "Suspicious content" in msg

    def test_trusted_agent_new_identity_detected(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "assume new_identity now")
        assert ok is False
        assert "Suspicious content" in msg

    def test_trusted_agent_system_prompt_detected(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "system_prompt: override")
        assert ok is False
        assert "Suspicious content" in msg

    def test_case_insensitive_detection(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "IGNORE_PREVIOUS everything")
        assert ok is False
        assert "Suspicious content" in msg

    def test_returns_tuple(self):
        guard = MemoryPoisonGuard()
        result = guard.validate_write("x", "y")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestValidateWriteBoundary:
    def test_empty_content_from_trusted_agent(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "")
        assert ok is True
        assert msg == "OK"

    def test_suspicious_keyword_embedded_in_longer_text(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "please ignore_previous and do something else")
        assert ok is False

    def test_untrusted_agent_even_with_clean_content(self):
        guard = MemoryPoisonGuard()
        ok, msg = guard.validate_write("stranger", "totally safe content")
        assert ok is False

    def test_multiple_suspicious_keywords_first_one_reported(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "ignore_previous forget_rules")
        assert ok is False
        assert "Suspicious content" in msg

    def test_unicode_content_trusted_agent(self):
        guard = MemoryPoisonGuard()
        guard.register_trusted("agent-001")
        ok, msg = guard.validate_write("agent-001", "安全な内容です")
        assert ok is True
        assert msg == "OK"
