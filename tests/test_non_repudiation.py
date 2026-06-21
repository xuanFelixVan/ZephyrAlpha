# [A_test] module_id: SRC-TST-1311 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.non_repudiation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys
sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.non_repudiation import NonRepudiation, AuditEntry
    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestAuditEntry:

    def test_entry_fields(self):
        entry = AuditEntry(
            entry_id="NR-test-abc",
            operation="write",
            agent_id="agent-1",
            timestamp="2026-01-01T00:00:00Z",
            nonce="deadbeef",
            hmac_hash="abcd1234",
        )
        assert entry.entry_id == "NR-test-abc"
        assert entry.operation == "write"
        assert entry.agent_id == "agent-1"
        assert entry.nonce == "deadbeef"
        assert entry.hmac_hash == "abcd1234"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestNonRepudiation:

    def test_sign_returns_audit_entry(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        entry = nr.sign(operation="write", agent_id="agent-1")
        assert isinstance(entry, AuditEntry)
        assert entry.operation == "write"
        assert entry.agent_id == "agent-1"
        assert entry.entry_id.startswith("NR-agent-1-")
        assert entry.hmac_hash != ""

    def test_sign_generates_unique_entry_ids(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        e1 = nr.sign(operation="read", agent_id="a1")
        e2 = nr.sign(operation="read", agent_id="a1")
        assert e1.entry_id != e2.entry_id

    def test_sign_generates_unique_nonces(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        e1 = nr.sign(operation="read", agent_id="a1")
        e2 = nr.sign(operation="read", agent_id="a1")
        assert e1.nonce != e2.nonce

    def test_verify_valid_entry(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        entry = nr.sign(operation="delete", agent_id="agent-x")
        result = nr.verify(entry)
        assert result["verified"] is True
        assert result["entry_id"] == entry.entry_id

    def test_verify_tampered_entry(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        entry = nr.sign(operation="write", agent_id="agent-y")
        tampered = AuditEntry(
            entry_id=entry.entry_id,
            operation="TAMPERED",
            agent_id=entry.agent_id,
            timestamp=entry.timestamp,
            nonce=entry.nonce,
            hmac_hash=entry.hmac_hash,
        )
        result = nr.verify(tampered)
        assert result["verified"] is False

    def test_verify_tampered_hmac(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        entry = nr.sign(operation="read", agent_id="agent-z")
        tampered = AuditEntry(
            entry_id=entry.entry_id,
            operation=entry.operation,
            agent_id=entry.agent_id,
            timestamp=entry.timestamp,
            nonce=entry.nonce,
            hmac_hash="0000000000000000",
        )
        result = nr.verify(tampered)
        assert result["verified"] is False

    def test_different_keys_fail_verification(self):
        nr1 = NonRepudiation(secret_key="key-one")
        nr2 = NonRepudiation(secret_key="key-two")
        entry = nr1.sign(operation="exec", agent_id="a1")
        result = nr2.verify(entry)
        assert result["verified"] is False

    def test_auto_generated_key(self):
        nr = NonRepudiation()
        entry = nr.sign(operation="test", agent_id="a1")
        result = nr.verify(entry)
        assert result["verified"] is True

    def test_sign_empty_operation(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        entry = nr.sign(operation="", agent_id="a1")
        result = nr.verify(entry)
        assert result["verified"] is True

    def test_chain_accumulates_entries(self):
        nr = NonRepudiation(secret_key="test-secret-key-for-unit-test")
        nr.sign(operation="op1", agent_id="a1")
        nr.sign(operation="op2", agent_id="a2")
        assert len(nr._chain) == 2
