# [A_test] module_id: MOD-GOV_skill_idempotency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_idempotency
# [INVARIANTS] must clear class-level _execution_history between tests to avoid cross-contamination
# [MODIFY-GUARD] skill_idempotency.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass independently; class state cleared in fixture
# [TESTS] pytest tests/test_skill_idempotency.py -q
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.autonomy_core.skills.skill_idempotency import SkillIdempotency


@pytest.fixture(autouse=True)
def _clean_history():
    SkillIdempotency.clear_all()
    yield
    SkillIdempotency.clear_all()


class TestSkillIdempotencyInstantiation:
    def test_class_has_execution_history(self):
        assert hasattr(SkillIdempotency, "_execution_history")
        assert isinstance(SkillIdempotency.execution_history, dict)

    def test_class_has_default_ttl(self):
        assert SkillIdempotency._DEFAULT_TTL_S == 3600.0


class TestHashInput:
    def test_deterministic_hash(self):
        result1 = SkillIdempotency.hash_input("test data")
        result2 = SkillIdempotency.hash_input("test data")
        assert result1 == result2

    def test_different_inputs_different_hashes(self):
        h1 = SkillIdempotency.hash_input("input-a")
        h2 = SkillIdempotency.hash_input("input-b")
        assert h1 != h2

    def test_hash_length_16(self):
        result = SkillIdempotency.hash_input("some data")
        assert len(result) == 16

    def test_empty_string_hash(self):
        result = SkillIdempotency.hash_input("")
        assert len(result) == 16
        assert isinstance(result, str)

    def test_unicode_input_hash(self):
        result = SkillIdempotency.hash_input("中文输入")
        assert len(result) == 16


class TestIsDuplicate:
    def test_first_call_not_duplicate(self):
        result = SkillIdempotency.is_duplicate("skill-1", "hash-a")
        assert result is False

    def test_second_call_is_duplicate(self):
        SkillIdempotency.is_duplicate("skill-1", "hash-a")
        result = SkillIdempotency.is_duplicate("skill-1", "hash-a")
        assert result is True

    def test_different_skill_not_duplicate(self):
        SkillIdempotency.is_duplicate("skill-1", "hash-a")
        result = SkillIdempotency.is_duplicate("skill-2", "hash-a")
        assert result is False

    def test_different_hash_not_duplicate(self):
        SkillIdempotency.is_duplicate("skill-1", "hash-a")
        result = SkillIdempotency.is_duplicate("skill-1", "hash-b")
        assert result is False

    def test_expired_entry_not_duplicate(self):
        SkillIdempotency.mark_executed("skill-1", "hash-old")
        key = "skill-1:hash-old"
        SkillIdempotency.execution_history[key] = ("executed", time.time() - 7200)
        result = SkillIdempotency.is_duplicate("skill-1", "hash-old", ttl_s=3600.0)
        assert result is False

    def test_custom_ttl_respected(self):
        SkillIdempotency.mark_executed("skill-1", "hash-x")
        key = "skill-1:hash-x"
        SkillIdempotency.execution_history[key] = ("executed", time.time() - 10)
        result = SkillIdempotency.is_duplicate("skill-1", "hash-x", ttl_s=5.0)
        assert result is False

    def test_within_ttl_is_duplicate(self):
        SkillIdempotency.mark_executed("skill-1", "hash-y")
        result = SkillIdempotency.is_duplicate("skill-1", "hash-y", ttl_s=3600.0)
        assert result is True


class TestMarkExecuted:
    def test_mark_and_check(self):
        SkillIdempotency.mark_executed("skill-2", "hash-m")
        key = "skill-2:hash-m"
        assert key in SkillIdempotency.execution_history
        result, ts = SkillIdempotency.execution_history[key]
        assert result == "executed"

    def test_mark_with_custom_result(self):
        SkillIdempotency.mark_executed("skill-3", "hash-n", result="failed")
        key = "skill-3:hash-n"
        result, ts = SkillIdempotency.execution_history[key]
        assert result == "failed"

    def test_mark_overwrites_previous(self):
        SkillIdempotency.mark_executed("skill-4", "hash-o", result="first")
        SkillIdempotency.mark_executed("skill-4", "hash-o", result="second")
        key = "skill-4:hash-o"
        result, ts = SkillIdempotency.execution_history[key]
        assert result == "second"


class TestClearExpired:
    def test_clears_expired_entries(self):
        SkillIdempotency.mark_executed("skill-old", "h1")
        key = "skill-old:h1"
        SkillIdempotency.execution_history[key] = ("executed", time.time() - 7200)
        SkillIdempotency.clear_expired(ttl_s=3600.0)
        assert key not in SkillIdempotency.execution_history

    def test_keeps_fresh_entries(self):
        SkillIdempotency.mark_executed("skill-new", "h2")
        SkillIdempotency.clear_expired(ttl_s=3600.0)
        key = "skill-new:h2"
        assert key in SkillIdempotency.execution_history

    def test_clear_expired_with_empty_history(self):
        SkillIdempotency.clear_expired()
        assert SkillIdempotency.execution_history == {}


class TestClearAll:
    def test_clear_all_empties_history(self):
        SkillIdempotency.mark_executed("sk", "h")
        SkillIdempotency.clear_all()
        assert SkillIdempotency.execution_history == {}


class TestStats:
    def test_stats_empty(self):
        result = SkillIdempotency.stats()
        assert result == {"active_entries": 0}

    def test_stats_with_entries(self):
        SkillIdempotency.mark_executed("sk-a", "h1")
        SkillIdempotency.mark_executed("sk-b", "h2")
        result = SkillIdempotency.stats()
        assert result["active_entries"] == 2

    def test_stats_excludes_expired(self):
        SkillIdempotency.mark_executed("sk-old", "h1")
        key = "sk-old:h1"
        SkillIdempotency.execution_history[key] = ("executed", time.time() - 7200)
        result = SkillIdempotency.stats()
        assert result["active_entries"] == 0
