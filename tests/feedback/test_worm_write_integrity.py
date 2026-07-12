# [A_test] module_id: SRC-TST-1807 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_worm_write_integrity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.worm_write_integrity
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_worm_write_integrity.py
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json

import pytest

from zephyr.feedback_loop.forensic.worm_write_integrity import WORMEntry, WORMWriteIntegrity


class TestWORMEntry:
    def test_creation(self):
        entry = WORMEntry(entry_id="e1", content_hash="abc", timestamp="", data="data")
        assert entry.entry_id == "e1"
        assert entry.content_hash == "abc"
        assert entry.data == "data"

    def test_default_timestamp(self):
        entry = WORMEntry(entry_id="e2", content_hash="def", timestamp="", data="d")
        assert entry.timestamp == ""


class TestWORMWriteIntegrity:
    def test_instantiation_defaults(self):
        worm = WORMWriteIntegrity()
        assert worm.entries == []
        assert worm.sealed is False

    def test_instantiation_with_entries(self):
        entries = [WORMEntry(entry_id="e1", content_hash="h", timestamp="", data="d")]
        worm = WORMWriteIntegrity(entries=entries)
        assert len(worm.entries) == 1

    def test_write_creates_entry(self):
        worm = WORMWriteIntegrity()
        data = {"action": "repair", "target": "db"}
        entry = worm.write("e1", data)
        assert entry.entry_id == "e1"
        assert len(worm.entries) == 1
        expected_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        assert entry.content_hash == expected_hash

    def test_write_multiple_entries(self):
        worm = WORMWriteIntegrity()
        worm.write("e1", {"a": 1})
        worm.write("e2", {"b": 2})
        assert len(worm.entries) == 2

    def test_write_deterministic_hash(self):
        worm1 = WORMWriteIntegrity()
        worm2 = WORMWriteIntegrity()
        data = {"key": "value"}
        e1 = worm1.write("e1", data)
        e2 = worm2.write("e1", data)
        assert e1.content_hash == e2.content_hash

    def test_write_after_seal_raises(self):
        worm = WORMWriteIntegrity()
        worm.seal()
        with pytest.raises(PermissionError, match="sealed"):
            worm.write("e1", {"a": 1})

    def test_verify_matching_data(self):
        worm = WORMWriteIntegrity()
        data = {"action": "repair", "target": "db"}
        worm.write("e1", data)
        assert worm.verify("e1", data) is True

    def test_verify_mismatched_data(self):
        worm = WORMWriteIntegrity()
        worm.write("e1", {"action": "repair"})
        assert worm.verify("e1", {"action": "skip"}) is False

    def test_verify_nonexistent_entry(self):
        worm = WORMWriteIntegrity()
        assert worm.verify("nonexistent", {"any": "data"}) is False

    def test_seal_prevents_writes(self):
        worm = WORMWriteIntegrity()
        worm.write("e1", {"a": 1})
        worm.seal()
        assert worm.sealed is True
        with pytest.raises(PermissionError):
            worm.write("e2", {"b": 2})

    def test_seal_does_not_affect_verify(self):
        worm = WORMWriteIntegrity()
        data = {"key": "val"}
        worm.write("e1", data)
        worm.seal()
        assert worm.verify("e1", data) is True

    def test_write_empty_data(self):
        worm = WORMWriteIntegrity()
        entry = worm.write("e1", {})
        assert entry.content_hash == hashlib.sha256(json.dumps({}, sort_keys=True).encode()).hexdigest()

    def test_verify_data_key_order_irrelevant(self):
        worm = WORMWriteIntegrity()
        worm.write("e1", {"a": 1, "b": 2})
        assert worm.verify("e1", {"b": 2, "a": 1}) is True

    def test_write_duplicate_entry_id(self):
        worm = WORMWriteIntegrity()
        worm.write("e1", {"v": 1})
        worm.write("e1", {"v": 2})
        assert len(worm.entries) == 2
        assert worm.verify("e1", {"v": 1}) is True
