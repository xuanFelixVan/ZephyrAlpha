# [A_test] module_id: SRC-TST-2050 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-667 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_pattern_library
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for pattern_library.py (T-3-21)
============================================
覆盖：模式 CRUD、模式类型、查询过滤、ChromaDB 集成。

最少测试：10 条。
"""


from datetime import UTC

from zephyr.gov_kb.pattern_library import (
    PatternEntry,
    PatternLibrary,
    PatternQuery,
    PatternType,
)


class TestPatternType:
    def test_three_types_exist(self) -> None:
        assert PatternType.SUCCESS_PATTERN.value == "success_pattern"
        assert PatternType.FAILURE_PATTERN.value == "failure_pattern"
        assert PatternType.ANTI_PATTERN.value == "anti_pattern"


class TestPatternEntry:
    def test_valid_entry(self) -> None:
        from datetime import datetime

        now = datetime.now(UTC)
        entry = PatternEntry(
            pattern_id="PAT-001",
            title="Momentum Factor Success",
            pattern_type=PatternType.SUCCESS_PATTERN,
            domain="D3",
            layer="L02",
            description="Momentum factor with IC>0.05",
            created_at=now,
            updated_at=now,
        )
        assert entry.pattern_id == "PAT-001"
        assert entry.confidence == 1.0
        assert entry.occurrence_count == 1

    def test_tags_deduplication(self) -> None:
        from datetime import datetime

        now = datetime.now(UTC)
        entry = PatternEntry(
            pattern_id="PAT-002",
            title="Test",
            pattern_type=PatternType.ANTI_PATTERN,
            domain="D0",
            layer="L00",
            description="test",
            tags=["alpha", "alpha", "beta"],
            created_at=now,
            updated_at=now,
        )
        assert entry.tags == ["alpha", "beta"]


class TestPatternLibrary:
    def test_create_and_get(self) -> None:
        lib = PatternLibrary()
        entry = lib.create(
            title="Momentum Success",
            pattern_type=PatternType.SUCCESS_PATTERN,
            domain="D3",
            layer="L02",
            description="Momentum factor works well",
        )
        assert entry.pattern_id == "PAT-001"
        got = lib.get("PAT-001")
        assert got is not None
        assert got.title == "Momentum Success"

    def test_get_nonexistent(self) -> None:
        lib = PatternLibrary()
        assert lib.get("PAT-999") is None

    def test_auto_increment_id(self) -> None:
        lib = PatternLibrary()
        e1 = lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L00", description="a")
        e2 = lib.create(title="B", pattern_type=PatternType.FAILURE_PATTERN, domain="D1", layer="L01", description="b")
        assert e1.pattern_id == "PAT-001"
        assert e2.pattern_id == "PAT-002"

    def test_query_by_domain(self) -> None:
        lib = PatternLibrary()
        lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D3", layer="L02", description="a")
        lib.create(title="B", pattern_type=PatternType.SUCCESS_PATTERN, domain="D6", layer="L10", description="b")
        results = lib.query(PatternQuery(domain="D3"))
        assert len(results) == 1
        assert results[0].domain == "D3"

    def test_query_by_layer(self) -> None:
        lib = PatternLibrary()
        lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L02", description="a")
        lib.create(title="B", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L03", description="b")
        results = lib.query(PatternQuery(layer="L02"))
        assert len(results) == 1

    def test_query_by_pattern_type(self) -> None:
        lib = PatternLibrary()
        lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L00", description="a")
        lib.create(title="B", pattern_type=PatternType.ANTI_PATTERN, domain="D0", layer="L00", description="b")
        results = lib.query(PatternQuery(pattern_type=PatternType.ANTI_PATTERN))
        assert len(results) == 1
        assert results[0].pattern_type == PatternType.ANTI_PATTERN

    def test_query_by_tags(self) -> None:
        lib = PatternLibrary()
        lib.create(
            title="A",
            pattern_type=PatternType.SUCCESS_PATTERN,
            domain="D0",
            layer="L00",
            description="a",
            tags=["momentum", "alpha"],
        )
        lib.create(
            title="B",
            pattern_type=PatternType.SUCCESS_PATTERN,
            domain="D0",
            layer="L00",
            description="b",
            tags=["risk"],
        )
        results = lib.query(PatternQuery(tags=["momentum"]))
        assert len(results) == 1

    def test_query_by_keyword(self) -> None:
        lib = PatternLibrary()
        lib.create(
            title="Momentum Factor",
            pattern_type=PatternType.SUCCESS_PATTERN,
            domain="D3",
            layer="L02",
            description="IC>0.05",
        )
        lib.create(
            title="Risk Control",
            pattern_type=PatternType.ANTI_PATTERN,
            domain="D4",
            layer="L04",
            description="Stop loss",
        )
        results = lib.query(PatternQuery(keyword="momentum"))
        assert len(results) == 1

    def test_delete(self) -> None:
        lib = PatternLibrary()
        lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L00", description="a")
        assert lib.delete("PAT-001") is True
        assert lib.get("PAT-001") is None
        assert lib.delete("PAT-999") is False

    def test_update(self) -> None:
        lib = PatternLibrary()
        lib.create(title="Old", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L00", description="a")
        updated = lib.update("PAT-001", title="New", confidence=0.8)
        assert updated is not None
        assert updated.title == "New"
        assert updated.confidence == 0.8

    def test_list_all_and_count(self) -> None:
        lib = PatternLibrary()
        lib.create(title="A", pattern_type=PatternType.SUCCESS_PATTERN, domain="D0", layer="L00", description="a")
        lib.create(title="B", pattern_type=PatternType.FAILURE_PATTERN, domain="D1", layer="L01", description="b")
        assert lib.count() == 2
        assert len(lib.list_all()) == 2
