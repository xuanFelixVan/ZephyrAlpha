# [A_test] module_id: SRC-TST-0292 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_agent_skill_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.security.agent_skill_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_agent_skill_guard.py
# [TTL] task_bound


from zephyr.feedback_loop.security.agent_skill_guard import (
    AgentSkillGuard,
    SkillRecord,
    SkillSecurityStatus,
    SkillStatus,
)


class TestAgentSkillGuardInstantiation:
    def test_default_instantiation(self):
        guard = AgentSkillGuard()
        assert guard.skills == {}
        assert "github.com/zephyr" in guard.trusted_sources
        assert "eval(" in guard.blocked_patterns

    def test_custom_instantiation(self):
        guard = AgentSkillGuard(
            trusted_sources={"internal.repo"},
            blocked_patterns={"rm -rf"},
        )
        assert guard.trusted_sources == {"internal.repo"}
        assert guard.blocked_patterns == {"rm -rf"}


class TestRegister:
    def test_register_trusted_source(self):
        guard = AgentSkillGuard(trusted_sources={"github.com"})
        status = guard.register("safe_skill", "https://github.com/zephyr/skill", "clean_code")
        assert status == SkillSecurityStatus.VERIFIED
        assert "safe_skill" in guard.skills

    def test_register_untrusted_source(self):
        guard = AgentSkillGuard(trusted_sources=set())
        status = guard.register("unknown_skill", "https://evil.com/skill", "clean_code")
        assert status == SkillSecurityStatus.SANDBOX_ONLY

    def test_register_blocked_content(self):
        guard = AgentSkillGuard()
        status = guard.register("bad_skill", "https://github.com/zephyr/skill", "eval('malicious')")
        assert status == SkillSecurityStatus.BLOCKED

    def test_register_blocked_subprocess(self):
        guard = AgentSkillGuard()
        status = guard.register("sub_skill", "https://evil.com/s", "import subprocess")
        assert status == SkillSecurityStatus.BLOCKED


class TestVerifyExisting:
    def test_verify_matching_hash(self):
        guard = AgentSkillGuard(trusted_sources={"github.com"})
        guard.register("skill1", "https://github.com/zephyr/skill1", "content")
        record = guard.skills["skill1"]
        status = guard.verify_existing("skill1", record.sha256_hash)
        assert status == SkillSecurityStatus.VERIFIED

    def test_verify_mismatched_hash(self):
        guard = AgentSkillGuard()
        guard.register("skill1", "https://github.com/zephyr/skill1", "content")
        status = guard.verify_existing("skill1", "wrong_hash")
        assert status == SkillSecurityStatus.BLOCKED

    def test_verify_unknown_skill(self):
        guard = AgentSkillGuard()
        status = guard.verify_existing("nonexistent", "any_hash")
        assert status == SkillSecurityStatus.UNKNOWN


class TestSkillRecord:
    def test_skill_record_defaults(self):
        rec = SkillRecord(skill_name="s", source_url="u", sha256_hash="h")
        assert rec.status == SkillSecurityStatus.UNKNOWN
        assert rec.verified_by == ""


class TestSkillStatusAlias:
    def test_skill_status_is_security_status(self):
        assert SkillStatus is SkillSecurityStatus
