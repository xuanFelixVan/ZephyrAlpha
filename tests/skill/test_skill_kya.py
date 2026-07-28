# [A_test] module_id: MOD-GOV_skill_kya | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_kya
# [INVARIANTS] SkillKYA certification must have valid tier and expiry
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] handles missing SkillLoader gracefully
# [TESTS] tests/test_skill_kya.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_kya import RISKY, SkillKYA


class TestSkillKYAInstantiation:
    def test_default_instantiation(self):
        kya = SkillKYA()
        assert isinstance(kya.certs, dict)
        assert len(kya.certs) == 0

    def test_expire_days_constant(self):
        assert SkillKYA.EXPIRE_DAYS == 90


class TestAssess:
    def test_basic_tier_no_risky_few_tools(self):
        kya = SkillKYA()
        tier = kya.assess(["read", "list", "search"])
        assert tier == "basic"

    def test_intermediate_tier_one_risky(self):
        kya = SkillKYA()
        tier = kya.assess(["read", "write_file", "search"])
        assert tier == "intermediate"

    def test_advanced_tier_two_risky(self):
        kya = SkillKYA()
        tier = kya.assess(["write_file", "delete_file", "read", "search"])
        assert tier == "advanced"

    def test_privileged_tier_many_risky(self):
        kya = SkillKYA()
        tools = list(RISKY)
        tier = kya.assess(tools)
        assert tier == "privileged"

    def test_privileged_tier_many_tools(self):
        kya = SkillKYA()
        tools = [f"tool_{i}" for i in range(16)]
        tier = kya.assess(tools)
        assert tier == "privileged"

    def test_empty_tools_is_basic(self):
        kya = SkillKYA()
        tier = kya.assess([])
        assert tier == "basic"

    def test_advanced_tier_many_tools(self):
        kya = SkillKYA()
        tools = [f"tool_{i}" for i in range(11)]
        tier = kya.assess(tools)
        assert tier == "advanced"

    def test_intermediate_tier_many_tools(self):
        kya = SkillKYA()
        tools = [f"tool_{i}" for i in range(6)]
        tier = kya.assess(tools)
        assert tier == "intermediate"


class TestCertify:
    def test_certify_with_tools(self):
        kya = SkillKYA()
        cert = kya.certify("skill-1", tools=["read", "write_file"])
        assert cert["skill_id"] == "skill-1"
        assert cert["certified"] is True
        assert cert["kya_level"] == "intermediate"
        assert cert["tools_count"] == 2
        assert cert["risky_count"] == 1
        assert "expires_at" in cert
        assert "assigned_at" in cert

    def test_certify_without_tools_fallback(self):
        kya = SkillKYA()
        cert = kya.certify("skill-2")
        assert cert["skill_id"] == "skill-2"
        assert cert["certified"] is True
        assert cert["tools_count"] == 0

    def test_certify_stored_in_certs(self):
        kya = SkillKYA()
        kya.certify("skill-3", tools=["read"])
        assert "skill-3" in kya.certs

    def test_certify_expires_in_days(self):
        kya = SkillKYA()
        cert = kya.certify("skill-4", tools=["read"])
        assert cert["expires_in_days"] == 90


class TestRevalidate:
    def test_revalidate_valid_cert(self):
        kya = SkillKYA()
        kya.certify("skill-5", tools=["read"])
        result = kya.revalidate("skill-5")
        assert result["status"] == "still_valid"
        assert result["expires_in_days"] > 0

    def test_revalidate_unknown_skill_recertifies(self):
        kya = SkillKYA()
        result = kya.revalidate("skill-unknown")
        assert "kya_level" in result
        assert result["certified"] is True

    def test_revalidate_returns_cert_for_uncertified(self):
        kya = SkillKYA()
        result = kya.revalidate("new-skill")
        assert result["skill_id"] == "new-skill"
