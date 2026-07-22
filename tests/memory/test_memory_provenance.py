# [A_test] module_id: MOD-GOV_memory_provenance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_memory_provenance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_memory_provenance.py -q
# [TTL] task_bound

import hashlib

from zephyr.governance.services.memory_provenance import MemoryProvenanceLog


class TestMemoryProvenanceLogInstantiation:
    def test_creates_instance_with_empty_records(self):
        mpl = MemoryProvenanceLog()
        assert isinstance(mpl, MemoryProvenanceLog)
        assert mpl._records == []


class TestRecord:
    def test_record_returns_sha256_hex(self):
        mpl = MemoryProvenanceLog()
        content = "test-content"
        expected = hashlib.sha256(content.encode()).hexdigest()
        result = mpl.record("agent-1", content)
        assert result == expected

    def test_record_stores_entry_with_agent_and_hash(self):
        mpl = MemoryProvenanceLog()
        content = "hello world"
        h = mpl.record("agent-x", content, source_contract="contract-1")
        assert len(mpl._records) == 1
        entry = mpl._records[0]
        assert entry["agent"] == "agent-x"
        assert entry["hash"] == h
        assert entry["contract"] == "contract-1"

    def test_record_appends_multiple_entries(self):
        mpl = MemoryProvenanceLog()
        mpl.record("a1", "content-1")
        mpl.record("a2", "content-2")
        mpl.record("a3", "content-3")
        assert len(mpl._records) == 3

    def test_record_default_contract_is_empty(self):
        mpl = MemoryProvenanceLog()
        mpl.record("agent-1", "data")
        assert mpl._records[0]["contract"] == ""

    def test_record_timestamp_is_iso_format(self):
        mpl = MemoryProvenanceLog()
        mpl.record("agent-1", "data")
        ts = mpl._records[0]["timestamp"]
        assert "T" in ts

    def test_record_same_content_produces_same_hash(self):
        mpl = MemoryProvenanceLog()
        h1 = mpl.record("a1", "identical")
        h2 = mpl.record("a2", "identical")
        assert h1 == h2

    def test_record_unicode_content(self):
        mpl = MemoryProvenanceLog()
        content = "记忆溯源测试"
        h = mpl.record("agent-unicode", content)
        assert h == hashlib.sha256(content.encode()).hexdigest()


class TestTrace:
    def test_trace_finds_existing_record(self):
        mpl = MemoryProvenanceLog()
        h = mpl.record("agent-1", "find-me", source_contract="sc-1")
        result = mpl.trace(h)
        assert result is not None
        assert result["agent"] == "agent-1"
        assert result["contract"] == "sc-1"

    def test_trace_returns_none_for_unknown_hash(self):
        mpl = MemoryProvenanceLog()
        mpl.record("agent-1", "some-content")
        result = mpl.trace("deadbeef" * 8)
        assert result is None

    def test_trace_returns_none_on_empty_log(self):
        mpl = MemoryProvenanceLog()
        result = mpl.trace("any-hash")
        assert result is None

    def test_trace_returns_first_match_when_duplicate_hashes(self):
        mpl = MemoryProvenanceLog()
        mpl.record("first", "same-content")
        mpl.record("second", "same-content")
        h = hashlib.sha256(b"same-content").hexdigest()
        result = mpl.trace(h)
        assert result["agent"] == "first"


class TestBoundary:
    def test_empty_content_hash(self):
        mpl = MemoryProvenanceLog()
        h = mpl.record("agent", "")
        assert h == hashlib.sha256(b"").hexdigest()

    def test_very_long_content(self):
        mpl = MemoryProvenanceLog()
        content = "x" * 1_000_000
        h = mpl.record("agent", content)
        assert len(h) == 64

    def test_special_characters_in_content(self):
        mpl = MemoryProvenanceLog()
        content = "\x00\x01\x02\n\r\t"
        h = mpl.record("agent", content)
        assert h == hashlib.sha256(content.encode()).hexdigest()
