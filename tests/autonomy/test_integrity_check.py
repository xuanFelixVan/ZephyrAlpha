# [A_test] module_id: MOD-GOV_integrity_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §

# [MODULE] tests.test_integrity_check

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest exit 0 on pass

# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.context.integrity_check import IntegrityCheck, IntegrityReport


class TestIntegrityReport:
    def test_instantiation_defaults(self):
        report = IntegrityReport(
            layer="kb",
            content_hash="abc123",
            inject_time="2026-05-07",
            hashes_match=True,
            order_preserved=True,
        )
        assert report.layer == "kb"
        assert report.content_hash == "abc123"
        assert report.inject_time == "2026-05-07"
        assert report.hashes_match is True
        assert report.order_preserved is True
        assert report.missing_items == []

    def test_instantiation_with_missing_items(self):
        report = IntegrityReport(
            layer="gate",
            content_hash="deadbeef",
            inject_time="2026-05-07T12:00:00",
            hashes_match=False,
            order_preserved=False,
            missing_items=["item_a", "item_b"],
        )
        assert report.missing_items == ["item_a", "item_b"]
        assert report.hashes_match is False
        assert report.order_preserved is False

    def test_instantiation_empty_strings(self):
        report = IntegrityReport(
            layer="",
            content_hash="",
            inject_time="",
            hashes_match=False,
            order_preserved=False,
        )
        assert report.layer == ""
        assert report.content_hash == ""
        assert report.inject_time == ""

    def test_instantiation_none_accepted(self):
        report = IntegrityReport(
            layer=None,
            content_hash=None,
            inject_time=None,
            hashes_match=None,
            order_preserved=None,
        )
        assert report.layer is None
        assert report.content_hash is None


class TestIntegrityCheck:
    def test_instantiation(self):
        checker = IntegrityCheck()
        assert checker is not None

    def test_verify_hashes_match(self):
        checker = IntegrityCheck()
        report = checker.verify("kb", "sha256:abc", "sha256:abc")
        assert isinstance(report, IntegrityReport)
        assert report.layer == "kb"
        assert report.hashes_match is True
        assert report.order_preserved is True

    def test_verify_hashes_mismatch(self):
        checker = IntegrityCheck()
        report = checker.verify("gate", "sha256:aaa", "sha256:bbb")
        assert isinstance(report, IntegrityReport)
        assert report.layer == "gate"
        assert report.hashes_match is False

    def test_verify_empty_strings(self):
        checker = IntegrityCheck()
        report = checker.verify("", "", "")
        assert isinstance(report, IntegrityReport)
        assert report.layer == ""
        assert report.content_hash == ""
        assert report.hashes_match is True

    def test_verify_returns_integrity_report(self):
        checker = IntegrityCheck()
        report = checker.verify("runtime", "h1", "h2")
        assert hasattr(report, "layer")
        assert hasattr(report, "content_hash")
        assert hasattr(report, "inject_time")
        assert hasattr(report, "hashes_match")
        assert hasattr(report, "order_preserved")
        assert hasattr(report, "missing_items")
