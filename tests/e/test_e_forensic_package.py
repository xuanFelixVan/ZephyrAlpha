# [A_test] module_id: SRC-TST-0802 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_forensic_package
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json

from zephyr.gov_audit.forensic_package import ForensicPackage


class TestForensicPackageInit:
    def test_init_events_and_chain_empty(self):
        fp = ForensicPackage()
        assert fp._events == []
        assert fp._chain == []


class TestForensicPackageBundle:
    def test_bundle_single_event(self):
        fp = ForensicPackage()
        event = {"type": "escalation", "level": 1}
        result = fp.bundle(event)
        assert isinstance(result, str)
        assert len(result) == 64
        assert len(fp._events) == 1
        assert len(fp._chain) == 1
        assert fp._events[0]["event"] == event
        assert fp._chain[0] == result

    def test_bundle_multiple_events(self):
        fp = ForensicPackage()
        h1 = fp.bundle({"type": "a", "id": 1})
        h2 = fp.bundle({"type": "b", "id": 2})
        h3 = fp.bundle({"type": "c", "id": 3})
        assert h1 != h2 != h3
        assert len(fp._events) == 3
        assert len(fp._chain) == 3
        expected_h2 = hashlib.sha256(
            (h1 + json.dumps({"type": "b", "id": 2}, sort_keys=True, default=str)).encode()
        ).hexdigest()
        assert h2 == expected_h2

    def test_bundle_non_ascii_event(self):
        fp = ForensicPackage()
        event = {"type": "escalation", "message": "紧急通知", "key": "日本語"}
        result = fp.bundle(event)
        assert isinstance(result, str)
        assert len(result) == 64
        serialized = json.dumps(event, sort_keys=True, default=str)
        expected = hashlib.sha256(serialized.encode()).hexdigest()
        assert result == expected

    def test_bundle_deterministic(self):
        fp = ForensicPackage()
        event = {"type": "escalation", "level": 1}
        h1 = fp.bundle(event)
        fp2 = ForensicPackage()
        h2 = fp2.bundle(event)
        assert h1 == h2


class TestForensicPackageVerifyChain:
    def test_verify_chain_valid(self):
        fp = ForensicPackage()
        fp.bundle({"type": "a", "id": 1})
        fp.bundle({"type": "b", "id": 2})
        fp.bundle({"type": "c", "id": 3})
        assert fp.verify_chain() is True

    def test_verify_chain_single_event(self):
        fp = ForensicPackage()
        fp.bundle({"type": "a", "id": 1})
        assert fp.verify_chain() is True

    def test_verify_chain_tampered_event(self):
        fp = ForensicPackage()
        fp.bundle({"type": "a", "id": 1})
        fp.bundle({"type": "b", "id": 2})
        fp.bundle({"type": "c", "id": 3})
        fp._events[1]["event"]["id"] = 999
        assert fp.verify_chain() is False

    def test_verify_chain_tampered_chain(self):
        fp = ForensicPackage()
        fp.bundle({"type": "a", "id": 1})
        fp.bundle({"type": "b", "id": 2})
        fp.bundle({"type": "c", "id": 3})
        fp._chain[1] = "0" * 64
        assert fp.verify_chain() is False
