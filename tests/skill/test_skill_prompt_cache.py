# [A_test] module_id: MOD-GOV_skill_prompt_cache | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_prompt_cache
# [INVARIANTS] SkillPromptCache.cache is class-level dict; tests must clear between runs
# [MODIFY-GUARD] changes require review of skill_prompt_cache.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get returns Optional[str]; set returns None; purge_expired returns int
# [TESTS] pytest tests/test_skill_prompt_cache.py -q
# [TTL] task_bound


import pytest

from zephyr.autonomy_core.skills.skill_prompt_cache import SkillPromptCache


@pytest.fixture(autouse=True)
def clean_cache():
    SkillPromptCache.clear()
    yield
    SkillPromptCache.clear()


class TestSkillPromptCacheKeyFor:
    def test_key_format(self):
        key = SkillPromptCache.key_for("SKILL-TEST-001", "some input data")
        assert key.startswith("SKILL-TEST-001:")
        parts = key.split(":")
        assert len(parts) == 2
        assert len(parts[1]) == 16

    def test_deterministic_key(self):
        key1 = SkillPromptCache.key_for("SKILL-TEST-001", "same input")
        key2 = SkillPromptCache.key_for("SKILL-TEST-001", "same input")
        assert key1 == key2

    def test_different_input_different_key(self):
        key1 = SkillPromptCache.key_for("SKILL-TEST-001", "input a")
        key2 = SkillPromptCache.key_for("SKILL-TEST-001", "input b")
        assert key1 != key2

    def test_different_skill_different_key(self):
        key1 = SkillPromptCache.key_for("SKILL-TEST-001", "same input")
        key2 = SkillPromptCache.key_for("SKILL-TEST-002", "same input")
        assert key1 != key2

    def test_empty_input(self):
        key = SkillPromptCache.key_for("SKILL-TEST-001", "")
        assert key.startswith("SKILL-TEST-001:")


class TestSkillPromptCacheGetSet:
    def test_set_and_get(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "response data")
        result = SkillPromptCache.get("SKILL-TEST-001", "abc123")
        assert result == "response data"

    def test_get_missing_key_returns_none(self):
        result = SkillPromptCache.get("SKILL-TEST-001", "nonexistent")
        assert result is None

    def test_get_expired_returns_none(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "response data", ttl_s=-1.0)
        result = SkillPromptCache.get("SKILL-TEST-001", "abc123")
        assert result is None

    def test_set_with_custom_ttl(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "response data", ttl_s=3600.0)
        result = SkillPromptCache.get("SKILL-TEST-001", "abc123")
        assert result == "response data"

    def test_overwrite_existing_key(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "first")
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "second")
        result = SkillPromptCache.get("SKILL-TEST-001", "abc123")
        assert result == "second"


class TestSkillPromptCacheInvalidate:
    def test_invalidate_removes_entries(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "data1")
        SkillPromptCache.set("SKILL-TEST-001", "def456", "data2")
        SkillPromptCache.invalidate("SKILL-TEST-001")
        assert SkillPromptCache.get("SKILL-TEST-001", "abc123") is None
        assert SkillPromptCache.get("SKILL-TEST-001", "def456") is None

    def test_invalidate_does_not_affect_other_skills(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "data1")
        SkillPromptCache.set("SKILL-TEST-002", "abc123", "data2")
        SkillPromptCache.invalidate("SKILL-TEST-001")
        assert SkillPromptCache.get("SKILL-TEST-002", "abc123") == "data2"

    def test_invalidate_nonexistent_skill_no_error(self):
        SkillPromptCache.invalidate("SKILL-NONEXISTENT")


class TestSkillPromptCachePurgeExpired:
    def test_purge_removes_expired(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "expired", ttl_s=-1.0)
        SkillPromptCache.set("SKILL-TEST-001", "def456", "valid", ttl_s=3600.0)
        count = SkillPromptCache.purge_expired()
        assert count >= 1
        assert SkillPromptCache.get("SKILL-TEST-001", "def456") == "valid"

    def test_purge_no_expired(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "data", ttl_s=3600.0)
        count = SkillPromptCache.purge_expired()
        assert count == 0


class TestSkillPromptCacheStats:
    def test_stats_returns_dict(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "data")
        stats = SkillPromptCache.stats()
        assert "total_entries" in stats
        assert "max_size" in stats
        assert stats["total_entries"] >= 1

    def test_stats_empty_cache(self):
        stats = SkillPromptCache.stats()
        assert stats["total_entries"] == 0

    def test_stats_purges_before_counting(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "expired", ttl_s=-1.0)
        stats = SkillPromptCache.stats()
        assert stats["total_entries"] == 0


class TestSkillPromptCacheClear:
    def test_clear_empties_cache(self):
        SkillPromptCache.set("SKILL-TEST-001", "abc123", "data1")
        SkillPromptCache.set("SKILL-TEST-002", "def456", "data2")
        SkillPromptCache.clear()
        stats = SkillPromptCache.stats()
        assert stats["total_entries"] == 0
