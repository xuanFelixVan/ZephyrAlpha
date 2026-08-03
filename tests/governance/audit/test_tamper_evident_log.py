# [A_test] module_id: SRC-TST-1718 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_tamper_evident_log
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] verify returns (bool, int); chain integrity maintained
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import hashlib

import pytest

from zephyr.governance.security_governance.tamper_evident_log import (
    LogEntry,
    TamperEvidentLog,
)


@pytest.fixture
def tmp_log_path(tmp_path):
    return str(tmp_path / "test_tamper_log.jsonl")


@pytest.fixture
def log(tmp_log_path):
    return TamperEvidentLog(log_path=tmp_log_path)


class TestTamperEvidentLog:
    def test_instantiation(self, log):
        assert log.chain_length() == 0
        assert log.tail_hash() == "0" * 64

    def test_append_returns_entry(self, log):
        entry = log.append(action="test_action", data="test_data")
        assert isinstance(entry, LogEntry)
        assert entry.action == "test_action"
        assert entry.data == "test_data"
        assert entry.entry_id == "tel-000001"
        assert entry.hash != ""
        assert entry.prev_hash == "0" * 64

    def test_chain_grows(self, log):
        log.append("action1", "data1")
        log.append("action2", "data2")
        assert log.chain_length() == 2

    def test_verify_intact_chain(self, log):
        log.append("action1", "data1")
        log.append("action2", "data2")
        log.append("action3", "data3")
        valid, length = log.verify()
        assert valid is True
        assert length == 3

    def test_tail_hash_updates(self, log):
        old_hash = log.tail_hash()
        log.append("action", "data")
        new_hash = log.tail_hash()
        assert new_hash != old_hash

    def test_recent(self, log):
        for i in range(25):
            log.append(f"action_{i}", f"data_{i}")
        recent = log.recent(n=10)
        assert len(recent) == 10
        assert recent[-1].action == "action_24"

    def test_recent_default(self, log):
        for i in range(30):
            log.append(f"action_{i}", f"data_{i}")
        recent = log.recent()
        assert len(recent) == 20

    def test_persistence(self, tmp_log_path):
        log1 = TamperEvidentLog(log_path=tmp_log_path)
        log1.append("persist_action", "persist_data")
        log2 = TamperEvidentLog(log_path=tmp_log_path)
        assert log2.chain_length() == 1
        valid, length = log2.verify()
        assert valid is True

    def test_prev_hash_chaining(self, log):
        e1 = log.append("a1", "d1")
        e2 = log.append("a2", "d2")
        assert e2.prev_hash == e1.hash

    def test_hash_deterministic(self, tmp_log_path):
        log_a = TamperEvidentLog(log_path=tmp_log_path)
        e = log_a.append("action", "data")
        raw = f"1:action:data:{e.timestamp}:{'0' * 64}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        assert e.hash == expected


class TestBoundaryCases:
    def test_append_empty_strings(self, log):
        entry = log.append("", "")
        assert isinstance(entry, LogEntry)
        assert entry.action == ""

    def test_verify_empty_chain(self, log):
        valid, length = log.verify()
        assert valid is True
        assert length == 0

    def test_recent_empty_chain(self, log):
        recent = log.recent()
        assert recent == []

    def test_append_unicode(self, log):
        entry = log.append("测试动作", "中文数据 🔒")
        assert entry.action == "测试动作"
        valid, _ = log.verify()
        assert valid is True

    def test_append_large_data(self, log):
        large_data = "X" * 10000
        entry = log.append("large", large_data)
        assert entry.data == large_data
        valid, _ = log.verify()
        assert valid is True
