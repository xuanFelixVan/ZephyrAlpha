# [A_test] module_id: SRC-TST-0508 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_changelog_manager
# [INVARIANTS] CHANGELOG prepend on append; get_latest returns first
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.changelog_manager import (
    CHANGELOG,
    ChangeImpact,
    ChangeRecord,
    append_change,
    get_latest,
    latest_version,
)


class TestChangeImpact:
    def test_enum_values(self):
        assert ChangeImpact.BREAKING == "Breaking"
        assert ChangeImpact.ENHANCEMENT == "Enhancement"
        assert ChangeImpact.FIX == "Fix"


class TestChangeRecord:
    def test_creation(self):
        rec = ChangeRecord(
            date="2026-05-22",
            version="v2.0.0",
            impact=ChangeImpact.ENHANCEMENT,
            sections_affected="§1",
            description="Test change",
        )
        assert rec.date == "2026-05-22"
        assert rec.version == "v2.0.0"
        assert rec.impact == ChangeImpact.ENHANCEMENT
        assert rec.author == "AI-assisted, Owner ratified"

    def test_custom_author(self):
        rec = ChangeRecord(
            date="2026-05-22",
            version="v2.0.0",
            impact=ChangeImpact.FIX,
            sections_affected="§2",
            description="Fix",
            author="custom_author",
        )
        assert rec.author == "custom_author"


class TestAppendChange:
    def test_append_prepends_to_changelog(self):
        original_len = len(CHANGELOG)
        rec = ChangeRecord(
            date="2026-05-22",
            version="v9.9.9",
            impact=ChangeImpact.FIX,
            sections_affected="§99",
            description="Test append",
        )
        append_change(rec)
        assert len(CHANGELOG) == original_len + 1
        assert CHANGELOG[0].version == "v9.9.9"
        CHANGELOG.pop(0)


class TestGetLatest:
    def test_returns_first_record(self):
        result = get_latest()
        assert result is not None
        assert isinstance(result, ChangeRecord)

    def test_returns_none_when_empty(self):
        original = CHANGELOG[:]
        CHANGELOG.clear()
        assert get_latest() is None
        CHANGELOG.extend(original)


class TestLatestVersion:
    def test_returns_first_version(self):
        ver = latest_version()
        assert ver is not None
        assert ver.startswith("v")

    def test_returns_default_when_empty(self):
        original = CHANGELOG[:]
        CHANGELOG.clear()
        assert latest_version() == "v0.1.0"
        CHANGELOG.extend(original)
