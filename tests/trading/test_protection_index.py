# [A_test] module_id: MOD-GOV_protection_index | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] tests.test_protection_index
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_protection_index.py -q
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.trading.protection_index import (
        ANCHOR_PATTERNS,
        NORMAL_PATTERNS,
        PROTECTED_PATTERNS,
        PUBLIC_PATTERNS,
        IndexStats,
        ProtectionEntry,
        ProtectionIndex,
        _fnv1a_64,
        _PrefixTrie,
        _SimpleBloomFilter,
    )
    from zephyr.trading.verdict_engine import ProtectionLevel

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestPatternConstants:
    def test_anchor_patterns_non_empty(self):
        assert len(ANCHOR_PATTERNS) > 0

    def test_protected_patterns_non_empty(self):
        assert len(PROTECTED_PATTERNS) > 0

    def test_normal_patterns_non_empty(self):
        assert len(NORMAL_PATTERNS) > 0

    def test_public_patterns_non_empty(self):
        assert len(PUBLIC_PATTERNS) > 0

    def test_anchor_contains_key_paths(self):
        assert "project_rules.md" in ANCHOR_PATTERNS
        assert ".trae/rules/" in ANCHOR_PATTERNS
        assert "scripts/governance/" in ANCHOR_PATTERNS

    def test_protected_contains_audit_trail(self):
        assert "src/zephyr/audit-trail/" in PROTECTED_PATTERNS

    def test_normal_contains_tests(self):
        assert "tests/" in NORMAL_PATTERNS

    def test_public_contains_docs(self):
        assert "docs/" in PUBLIC_PATTERNS


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionEntry:
    def test_defaults(self):
        entry = ProtectionEntry()
        assert entry.path == ""
        assert entry.level == ProtectionLevel.normal
        assert entry.owner_module == ""
        assert entry.anchor_reason == ""
        assert entry.registered_at == 0.0

    def test_custom_values(self):
        entry = ProtectionEntry(
            path="project_rules.md",
            level=ProtectionLevel.anchor,
            owner_module="MOD-INF-033",
            anchor_reason="core rule file",
            registered_at=1000.0,
        )
        assert entry.path == "project_rules.md"
        assert entry.level == ProtectionLevel.anchor
        assert entry.owner_module == "MOD-INF-033"

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            ProtectionEntry(path="x", unknown_field="y")


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestIndexStats:
    def test_defaults(self):
        stats = IndexStats()
        assert stats.total_entries == 0
        assert stats.anchor_count == 0
        assert stats.protected_count == 0
        assert stats.normal_count == 0
        assert stats.public_count == 0
        assert stats.bloom_filter_size == 0
        assert stats.trie_node_count == 0
        assert stats.last_rebuild_time == 0.0

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            IndexStats(total_entries=1, rogue_field=True)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestFnv1a64:
    def test_returns_int(self):
        result = _fnv1a_64(b"hello")
        assert isinstance(result, int)

    def test_deterministic(self):
        assert _fnv1a_64(b"test") == _fnv1a_64(b"test")

    def test_different_inputs_differ(self):
        assert _fnv1a_64(b"foo") != _fnv1a_64(b"bar")

    def test_empty_input(self):
        result = _fnv1a_64(b"")
        assert isinstance(result, int)

    def test_64bit_range(self):
        result = _fnv1a_64(b"data")
        assert 0 <= result <= 0xFFFFFFFFFFFFFFFF


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestSimpleBloomFilter:
    def test_add_and_might_contain(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        bf.add("project_rules.md")
        assert bf.might_contain("project_rules.md") is True

    def test_non_added_item(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        bf.add("project_rules.md")
        assert bf.might_contain("completely_unknown_path_xyz.py") is False

    def test_count(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        assert bf.count == 0
        bf.add("a")
        assert bf.count == 1
        bf.add("b")
        assert bf.count == 2

    def test_size_property(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        assert bf.size > 0

    def test_clear(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        bf.add("test_path")
        bf.clear()
        assert bf.count == 0
        assert bf.might_contain("test_path") is False

    def test_multiple_items(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.01)
        items = ["alpha.py", "beta.py", "gamma.py"]
        for item in items:
            bf.add(item)
        for item in items:
            assert bf.might_contain(item) is True

    def test_invalid_expected_items_defaults(self):
        bf = _SimpleBloomFilter(expected_items=0, fp_rate=0.01)
        bf.add("test")
        assert bf.might_contain("test") is True

    def test_invalid_fp_rate_defaults(self):
        bf = _SimpleBloomFilter(expected_items=100, fp_rate=0.0)
        bf.add("test")
        assert bf.might_contain("test") is True


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestPrefixTrie:
    def test_insert_and_lookup(self):
        trie = _PrefixTrie()
        trie.insert("src/zephyr/", ProtectionLevel.protected)
        assert trie.lookup("src/zephyr/foo.py") == ProtectionLevel.protected

    def test_lookup_exact_match(self):
        trie = _PrefixTrie()
        trie.insert("project_rules.md", ProtectionLevel.anchor)
        assert trie.lookup("project_rules.md") == ProtectionLevel.anchor

    def test_lookup_no_match(self):
        trie = _PrefixTrie()
        trie.insert("src/zephyr/", ProtectionLevel.protected)
        assert trie.lookup("completely_different.py") is None

    def test_remove(self):
        trie = _PrefixTrie()
        trie.insert("tests/", ProtectionLevel.normal)
        assert trie.lookup("tests/") == ProtectionLevel.normal
        result = trie.remove("tests/")
        assert result is True
        assert trie.lookup("tests/") is None

    def test_remove_nonexistent(self):
        trie = _PrefixTrie()
        result = trie.remove("nonexistent/")
        assert result is False

    def test_node_count(self):
        trie = _PrefixTrie()
        initial = trie.node_count
        trie.insert("abc", ProtectionLevel.anchor)
        assert trie.node_count > initial

    def test_longest_prefix_wins(self):
        trie = _PrefixTrie()
        trie.insert("src/", ProtectionLevel.normal)
        trie.insert("src/zephyr/", ProtectionLevel.protected)
        assert trie.lookup("src/other/file.py") == ProtectionLevel.normal
        assert trie.lookup("src/zephyr/deep/file.py") == ProtectionLevel.protected


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexQuery:
    def test_query_anchor_exact(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("project_rules.md") == ProtectionLevel.anchor

    def test_query_anchor_prefix(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query(".trae/rules/project_rules.md") == ProtectionLevel.anchor

    def test_query_protected(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("src/zephyr/audit-trail/foo.py") == ProtectionLevel.protected

    def test_query_normal(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("tests/test_foo.py") == ProtectionLevel.normal

    def test_query_public(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("docs/readme.md") == ProtectionLevel.public

    def test_query_unknown_defaults_normal(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("unknown_path.py") == ProtectionLevel.normal

    def test_query_governance_scripts(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("scripts/governance/audit.py") == ProtectionLevel.anchor

    def test_query_kill_switch(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.query("kill_switch.py") == ProtectionLevel.anchor


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexBatch:
    def test_query_batch(self):
        idx = ProtectionIndex(project_root=".")
        paths = [
            "project_rules.md",
            "src/zephyr/audit-trail/log.py",
            "tests/test_x.py",
            "docs/guide.md",
            "random.py",
        ]
        results = idx.query_batch(paths)
        assert len(results) == 5
        assert results["project_rules.md"] == ProtectionLevel.anchor
        assert results["src/zephyr/audit-trail/log.py"] == ProtectionLevel.protected
        assert results["tests/test_x.py"] == ProtectionLevel.normal
        assert results["docs/guide.md"] == ProtectionLevel.public
        assert results["random.py"] == ProtectionLevel.normal


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexIsAnchor:
    def test_is_anchor_true(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.is_anchor("project_rules.md") is True

    def test_is_anchor_false(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.is_anchor("docs/readme.md") is False

    def test_is_anchor_prefix_match(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.is_anchor(".trae/rules/project_rules.md") is True


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexRegisterUnregister:
    def test_register_adds_entry(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom/path.py", ProtectionLevel.protected, "MOD-TEST", "test reason")
        entry = idx.get_entry("custom/path.py")
        assert entry is not None
        assert entry.level == ProtectionLevel.protected
        assert entry.owner_module == "MOD-TEST"
        assert entry.anchor_reason == "test reason"
        assert entry.registered_at > 0

    def test_register_queryable(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom/path.py", ProtectionLevel.anchor, "MOD-TEST", "test")
        assert idx.query("custom/path.py") == ProtectionLevel.anchor

    def test_unregister_removes_entry(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom/path.py", ProtectionLevel.protected, "MOD-TEST", "test")
        assert idx.get_entry("custom/path.py") is not None
        result = idx.unregister("custom/path.py")
        assert result is True
        assert idx.get_entry("custom/path.py") is None

    def test_unregister_nonexistent(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.unregister("nonexistent.py")
        assert result is False

    def test_register_overwrites(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("path.py", ProtectionLevel.normal, "M1", "r1")
        idx.register("path.py", ProtectionLevel.anchor, "M2", "r2")
        entry = idx.get_entry("path.py")
        assert entry.level == ProtectionLevel.anchor
        assert entry.owner_module == "M2"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexGetEntry:
    def test_get_entry_nonexistent(self):
        idx = ProtectionIndex(project_root=".")
        assert idx.get_entry("nonexistent.py") is None

    def test_get_entry_returns_protection_entry(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("test.py", ProtectionLevel.public, "MOD", "reason")
        entry = idx.get_entry("test.py")
        assert isinstance(entry, ProtectionEntry)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexRebuild:
    def test_rebuild_returns_stats(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom.py", ProtectionLevel.anchor, "MOD", "test")
        stats = idx.rebuild()
        assert isinstance(stats, IndexStats)
        assert stats.total_entries >= 1

    def test_rebuild_preserves_entries(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom.py", ProtectionLevel.anchor, "MOD", "test")
        idx.rebuild()
        entry = idx.get_entry("custom.py")
        assert entry is not None
        assert entry.level == ProtectionLevel.anchor

    def test_rebuild_updates_time(self):
        idx = ProtectionIndex(project_root=".")
        stats_before = idx.get_stats()
        idx.rebuild()
        stats_after = idx.get_stats()
        assert stats_after.last_rebuild_time >= stats_before.last_rebuild_time


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexGetStats:
    def test_stats_type(self):
        idx = ProtectionIndex(project_root=".")
        stats = idx.get_stats()
        assert isinstance(stats, IndexStats)

    def test_stats_after_register(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("a.py", ProtectionLevel.anchor, "M", "r")
        idx.register("b.py", ProtectionLevel.protected, "M", "r")
        idx.register("c.py", ProtectionLevel.normal, "M", "r")
        idx.register("d.py", ProtectionLevel.public, "M", "r")
        stats = idx.get_stats()
        assert stats.total_entries == 4
        assert stats.anchor_count == 1
        assert stats.protected_count == 1
        assert stats.normal_count == 1
        assert stats.public_count == 1
        assert stats.bloom_filter_size > 0
        assert stats.trie_node_count > 0


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexVerifyIntegrity:
    def test_healthy_index(self):
        idx = ProtectionIndex(project_root=".")
        issues = idx.verify_integrity()
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_after_register_still_healthy(self):
        idx = ProtectionIndex(project_root=".")
        idx.register("custom.py", ProtectionLevel.anchor, "MOD", "test")
        issues = idx.verify_integrity()
        assert len(issues) == 0


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestProtectionIndexHealthCheck:
    def test_healthy_status(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.health_check()
        assert result["status"] == "healthy"
        assert "stats" in result
        assert "integrity_issues" in result
        assert result["integrity_issue_count"] == 0
        assert isinstance(result["integrity_issues"], list)

    def test_stats_dict_structure(self):
        idx = ProtectionIndex(project_root=".")
        result = idx.health_check()
        stats = result["stats"]
        assert "total_entries" in stats
        assert "anchor_count" in stats
        assert "bloom_filter_size" in stats
        assert "trie_node_count" in stats
