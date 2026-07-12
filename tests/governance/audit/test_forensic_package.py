# [A_test] module_id: SRC-TST-1027 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_forensic_package
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_forensic_package.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json

from zephyr.gov_audit.forensic_package import ForensicPackage


class TestForensicPackageInstantiation:
    def test_init_creates_empty_events_list(self):
        fp = ForensicPackage()
        assert fp._events == []

    def test_init_creates_empty_chain_list(self):
        fp = ForensicPackage()
        assert fp._chain == []


class TestForensicPackageBundle:
    def test_bundle_single_event_returns_hash(self):
        fp = ForensicPackage()
        event = {"rule_id": "R001", "level": "high"}
        result = fp.bundle(event)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_bundle_appends_event_to_internal_list(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        assert len(fp._events) == 1
        assert fp._events[0]["event"] == {"rule_id": "R001"}

    def test_bundle_event_has_timestamp(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        assert "timestamp" in fp._events[0]
        assert fp._events[0]["timestamp"].startswith("2")

    def test_bundle_event_has_hash_field(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        assert "hash" in fp._events[0]
        assert len(fp._events[0]["hash"]) == 64

    def test_bundle_multiple_events_grows_chain(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        fp.bundle({"rule_id": "R002"})
        fp.bundle({"rule_id": "R003"})
        assert len(fp._chain) == 3

    def test_bundle_first_event_hash_is_sha256_of_serialized(self):
        fp = ForensicPackage()
        event = {"rule_id": "R001", "level": "high"}
        serialized = json.dumps(event, sort_keys=True, default=str)
        expected = hashlib.sha256(serialized.encode()).hexdigest()
        result = fp.bundle(event)
        assert result == expected

    def test_bundle_second_event_hash_incorporates_previous(self):
        fp = ForensicPackage()
        h1 = fp.bundle({"rule_id": "R001"})
        event2 = {"rule_id": "R002"}
        serialized2 = json.dumps(event2, sort_keys=True, default=str)
        expected = hashlib.sha256((h1 + serialized2).encode()).hexdigest()
        h2 = fp.bundle(event2)
        assert h2 == expected

    def test_bundle_empty_event(self):
        fp = ForensicPackage()
        result = fp.bundle({})
        assert isinstance(result, str)
        assert len(result) == 64

    def test_bundle_event_with_nested_dict(self):
        fp = ForensicPackage()
        event = {"rule_id": "R001", "context": {"key": "value", "nested": {"a": 1}}}
        result = fp.bundle(event)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_bundle_deterministic_for_same_event(self):
        fp1 = ForensicPackage()
        fp2 = ForensicPackage()
        event = {"rule_id": "R001", "level": "high"}
        h1 = fp1.bundle(event)
        h2 = fp2.bundle(event)
        assert h1 == h2


class TestForensicPackageVerifyChain:
    def test_verify_chain_empty_package(self):
        fp = ForensicPackage()
        assert fp.verify_chain() is True

    def test_verify_chain_single_event(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        assert fp.verify_chain() is True

    def test_verify_chain_multiple_events(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        fp.bundle({"rule_id": "R002"})
        fp.bundle({"rule_id": "R003"})
        assert fp.verify_chain() is True

    def test_verify_chain_tampered_event_detected(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        fp.bundle({"rule_id": "R002"})
        fp._events[1]["event"] = {"rule_id": "TAMPERED"}
        assert fp.verify_chain() is False

    def test_verify_chain_tampered_hash_detected(self):
        fp = ForensicPackage()
        fp.bundle({"rule_id": "R001"})
        fp.bundle({"rule_id": "R002"})
        fp._chain[1] = "0" * 64
        assert fp.verify_chain() is False

    def test_verify_chain_after_ten_bundles(self):
        fp = ForensicPackage()
        for i in range(10):
            fp.bundle({"rule_id": f"R{i:03d}", "data": i})
        assert fp.verify_chain() is True
