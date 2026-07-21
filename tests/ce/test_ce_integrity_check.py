# [A_test] module_id: MOD-GOV_ce_integrity_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.integrity_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.integrity_check import IntegrityCheck, IntegrityReport
except Exception as _exc:
    pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}")


class TestIntegrityCheck:
    def test_verify_matching_hashes(self):
        ic = IntegrityCheck()
        report = ic.verify("layer1", "abc123", "abc123")
        assert isinstance(report, IntegrityReport)
        assert report.hashes_match is True
        assert report.layer == "layer1"
        assert report.order_preserved is True

    def test_verify_mismatched_hashes(self):
        ic = IntegrityCheck()
        report = ic.verify("layer2", "abc123", "def456")
        assert report.hashes_match is False
        assert report.layer == "layer2"

    def test_verify_empty_strings(self):
        ic = IntegrityCheck()
        report = ic.verify("", "", "")
        assert report.hashes_match is True
        assert report.layer == ""

    def test_verify_report_fields_types(self):
        ic = IntegrityCheck()
        report = ic.verify("test_layer", "hash1", "hash2")
        assert isinstance(report.layer, str)
        assert isinstance(report.content_hash, str)
        assert isinstance(report.inject_time, str)
        assert isinstance(report.hashes_match, bool)
        assert isinstance(report.order_preserved, bool)
        assert isinstance(report.missing_items, list)

    def test_verify_missing_items_default_empty(self):
        ic = IntegrityCheck()
        report = ic.verify("x", "h1", "h2")
        assert report.missing_items == []

    def test_verify_different_layers(self):
        ic = IntegrityCheck()
        r1 = ic.verify("L1", "h", "h")
        r2 = ic.verify("L2", "h", "h")
        assert r1.layer != r2.layer
