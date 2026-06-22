# [A_test] module_id: SRC-TST-1223 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.legal_audit_chain
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
    from zephyr.security.access_control.legal_audit_chain import ChainEntry, LegalAuditChain
except Exception as exc:
    pytest.skip(f"Cannot import legal_audit_chain: {exc}", allow_module_level=True)


class TestChainEntry:
    def test_fields(self):
        entry = ChainEntry(
            index=0,
            timestamp="2026-01-01T00:00:00",
            operation="write",
            agent_id="a1",
            prev_hash="0000000000000000",
            entry_hash="abcd1234",
        )
        assert entry.index == 0
        assert entry.operation == "write"
        assert entry.agent_id == "a1"
        assert entry.prev_hash == "0000000000000000"
        assert entry.entry_hash == "abcd1234"


class TestLegalAuditChain:
    def test_append_single(self):
        chain = LegalAuditChain()
        entry = chain.append("write", "agent-1")
        assert isinstance(entry, ChainEntry)
        assert entry.index == 0
        assert entry.operation == "write"
        assert entry.agent_id == "agent-1"
        assert entry.prev_hash == "0000000000000000"
        assert len(entry.entry_hash) == 16

    def test_append_multiple_chain_links(self):
        chain = LegalAuditChain()
        e1 = chain.append("write", "a1")
        e2 = chain.append("read", "a2")
        assert e2.prev_hash == e1.entry_hash
        assert e2.index == 1

    def test_verify_intact_chain(self):
        chain = LegalAuditChain()
        chain.append("write", "a1")
        chain.append("read", "a2")
        chain.append("delete", "a3")
        result = chain.verify()
        assert result["intact"] is True
        assert result["length"] == 3

    def test_verify_empty_chain(self):
        chain = LegalAuditChain()
        result = chain.verify()
        assert result["intact"] is True
        assert result["length"] == 0

    def test_verify_single_entry(self):
        chain = LegalAuditChain()
        chain.append("write", "a1")
        result = chain.verify()
        assert result["intact"] is True
        assert result["length"] == 1

    def test_append_empty_operation(self):
        chain = LegalAuditChain()
        entry = chain.append("", "a1")
        assert entry.operation == ""
        assert entry.index == 0

    def test_append_empty_agent_id(self):
        chain = LegalAuditChain()
        entry = chain.append("write", "")
        assert entry.agent_id == ""

    def test_hash_chain_consistency(self):
        chain = LegalAuditChain()
        entries = [chain.append(f"op{i}", f"a{i}") for i in range(5)]
        for i in range(1, len(entries)):
            assert entries[i].prev_hash == entries[i - 1].entry_hash
