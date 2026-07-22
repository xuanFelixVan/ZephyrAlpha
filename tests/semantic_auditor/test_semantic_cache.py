# [A_test] module_id: MOD-GOV_semantic_cache | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_semantic_cache
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_semantic_cache.py
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.governance.semantic_audit.semantic_cache import SemanticCache


class TestSemanticCacheInit:
    def test_default_init(self):
        cache = SemanticCache()
        assert cache.size() == 0
        assert cache.hit_rate() == 0.0

    def test_custom_init(self):
        cache = SemanticCache(max_entries=10, ttl=60.0)
        assert cache.size() == 0


class TestPut:
    def test_put_stores_entry(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        assert cache.size() == 1

    def test_put_duplicate_prompt_no_size_increase(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        cache.put("hello", "world2", 0.02)
        assert cache.size() == 1

    def test_put_evicts_lru_when_full(self):
        cache = SemanticCache(max_entries=2)
        cache.put("a", "1", 0.01)
        cache.put("b", "2", 0.01)
        cache.put("c", "3", 0.01)
        assert cache.size() == 2
        assert cache.get("a") is None

    def test_put_empty_prompt(self):
        cache = SemanticCache()
        cache.put("", "empty", 0.0)
        assert cache.size() == 1


class TestGet:
    def test_get_hit(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        result = cache.get("hello")
        assert result == "world"

    def test_get_miss(self):
        cache = SemanticCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_get_case_insensitive_normalized(self):
        cache = SemanticCache()
        cache.put("Hello World", "response", 0.01)
        result = cache.get("hello world")
        assert result == "response"

    def test_get_expired_returns_none(self):
        cache = SemanticCache(ttl=0.01)
        cache.put("hello", "world", 0.01)
        time.sleep(0.05)
        result = cache.get("hello")
        assert result is None

    def test_get_increments_hits(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        cache.get("hello")
        cache.get("hello")
        assert cache.hit_rate() > 0.5


class TestHitRate:
    def test_hit_rate_no_access(self):
        cache = SemanticCache()
        assert cache.hit_rate() == 0.0

    def test_hit_rate_all_misses(self):
        cache = SemanticCache()
        cache.get("a")
        cache.get("b")
        assert cache.hit_rate() == 0.0

    def test_hit_rate_mixed(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        cache.get("hello")
        cache.get("miss")
        assert cache.hit_rate() == pytest.approx(0.5)


class TestTotalSaved:
    def test_total_saved_initially_zero(self):
        cache = SemanticCache()
        assert cache.total_saved() == 0.0

    def test_total_saved_accumulates_on_hit(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.05)
        cache.get("hello")
        assert cache.total_saved() == pytest.approx(0.05)
        cache.get("hello")
        assert cache.total_saved() == pytest.approx(0.10)


class TestClear:
    def test_clear_resets_everything(self):
        cache = SemanticCache()
        cache.put("hello", "world", 0.01)
        cache.get("hello")
        cache.get("miss")
        cache.clear()
        assert cache.size() == 0
        assert cache.hit_rate() == 0.0
        assert cache.total_saved() == 0.0


class TestHashNormalization:
    def test_whitespace_normalized(self):
        cache = SemanticCache()
        cache.put("hello   world", "response", 0.01)
        result = cache.get("hello world")
        assert result == "response"

    def test_long_prompt_truncated(self):
        cache = SemanticCache()
        long_prompt = " ".join(["word"] * 200)
        cache.put(long_prompt, "response", 0.01)
        assert cache.size() == 1
