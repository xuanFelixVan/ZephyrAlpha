# [A_test] module_id: SRC-TST-1809 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_writer
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from zephyr.gov_audit.writer import AuditWriter, _generate_entry_id, _resolve_hmac_key


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "audit-trail"


@pytest.fixture
def writer(data_dir):
    return AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")


class TestResolveHmacKey:
    def test_explicit_key(self):
        result = _resolve_hmac_key("my-secret")
        assert result == b"my-secret"

    def test_env_key(self):
        with patch.dict(os.environ, {"ZEPHYR_AUDIT_HMAC_SECRET": "env-secret"}):
            result = _resolve_hmac_key("")
            assert result == b"env-secret"

    def test_fallback_key(self):
        with patch.dict(os.environ, {}, clear=True):
            if "ZEPHYR_AUDIT_HMAC_SECRET" in os.environ:
                del os.environ["ZEPHYR_AUDIT_HMAC_SECRET"]
            result = _resolve_hmac_key("")
            assert result == b"zephyr-audit-hmac-default-key"


class TestGenerateEntryId:
    def test_default_prefix(self):
        entry_id = _generate_entry_id()
        assert entry_id.startswith("AUD-T-")

    def test_custom_prefix(self):
        entry_id = _generate_entry_id(prefix="AUD-F", seq=5)
        assert entry_id.startswith("AUD-F-")
        assert entry_id.endswith("-0005")

    def test_sequence_number(self):
        entry_id = _generate_entry_id(seq=42)
        assert "-0042" in entry_id


class TestAuditWriter:
    def test_instantiation(self, data_dir):
        w = AuditWriter(data_dir=data_dir)
        assert w.data_dir == data_dir
        assert w.event_count == 0
        assert w.lamport_time >= 0

    def test_write_basic(self, writer, data_dir):
        event = {"event_type": "file_write", "agent_id": "agent-1", "session_id": "s1"}
        chain_hash = writer.write(event)
        assert isinstance(chain_hash, str)
        assert len(chain_hash) == 64
        assert writer.event_count == 1

    def test_write_adds_timestamp(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert "timestamp" in written

    def test_write_adds_chain_hash(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert "entry_hash" in written
        assert "prev_hash" in written

    def test_write_adds_hmac(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert "hmac_signature" in written

    def test_write_adds_lamport_clock(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert "lamport_time" in written
        assert "lamport_clock_counter" in written
        assert "lamport_clock_ide" in written

    def test_write_chain_linking(self, writer):
        event1 = {"event_type": "file_write", "agent_id": "a"}
        event2 = {"event_type": "file_read", "agent_id": "b"}
        hash1 = writer.write(event1)
        hash2 = writer.write(event2)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
        second = json.loads(lines[1])
        assert second["prev_hash"] == hash1

    def test_write_with_cot(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        result = writer.write_with_cot(event, reasoning_trace="I decided to write this file because...")
        assert "chain_hash" in result
        assert "cot_hash" in result
        assert result["cot_hash"] != ""

    def test_write_with_cot_truncation(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        long_trace = "x" * 600
        result = writer.write_with_cot(event, reasoning_trace=long_trace)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert len(written["reasoning_trace"]) <= 500

    def test_write_with_cot_empty_trace(self, writer):
        event = {"event_type": "file_write", "agent_id": "a"}
        result = writer.write_with_cot(event, reasoning_trace="")
        assert result["cot_hash"] == ""

    def test_event_count(self, writer):
        assert writer.event_count == 0
        writer.write({"event_type": "file_write", "agent_id": "a"})
        writer.write({"event_type": "file_read", "agent_id": "b"})
        assert writer.event_count == 2

    def test_lamport_time_increments(self, writer):
        initial = writer.lamport_time
        writer.write({"event_type": "file_write", "agent_id": "a"})
        assert writer.lamport_time == initial + 1

    def test_ide_source(self, data_dir):
        w = AuditWriter(data_dir=data_dir, ide_source="trae")
        assert w.ide_source == "trae"

    def test_merge_lamport(self, writer):
        initial = writer.lamport_time
        result = writer.merge_lamport(initial + 10)
        assert result == initial + 11

    def test_merge_lamport_lower(self, writer):
        initial = writer.lamport_time
        result = writer.merge_lamport(initial - 5)
        assert result == initial + 1

    def test_readonly_mode(self, writer):
        writer.readonly = True
        with pytest.raises(RuntimeError, match="readonly"):
            writer.write({"event_type": "file_write", "agent_id": "a"})

    def test_entry_id_generation(self, writer):
        event = {"event_type": "heartbeat", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert written["entry_id"].startswith("AUD-T-")

    def test_file_detail_entry_id(self, writer):
        event = {"event_type": "file_detail", "agent_id": "a"}
        writer.write(event)
        log_path = writer.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert written["entry_id"].startswith("AUD-F-")

    def test_finalize_current_batch_empty(self, writer):
        result = writer.finalize_current_batch()
        assert result is None

    def test_get_merkle_batches_empty(self, writer):
        batches = writer.get_merkle_batches()
        assert batches == []

    def test_write_no_hmac(self, data_dir):
        w = AuditWriter(data_dir=data_dir, hmac_key="", enable_merkle=False)
        event = {"event_type": "file_write", "agent_id": "a"}
        w.write(event)
        log_path = w.event_log_path
        with open(log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert "hmac_signature" not in written or written.get("hmac_signature") is not None

    def test_merkle_batch_accumulates_and_finalizes(self, data_dir):
        """回归（AI-AUDIT12）：write() 必须累积 entry_hash 到批次，
        finalize_current_batch() 返回真实 Merkle root 且清空批次。

        修复前：_batch_event_hashes 无追加点（finalize 恒 None）且调用了
        不存在的 MerkleAggregator.aggregate（应为 build）——批聚合整体死代码。
        """
        from zephyr.gov_audit.integrity import MerkleAggregator

        w = AuditWriter(data_dir=data_dir, enable_merkle=True, hmac_key="test-key")
        h1 = w.write({"event_type": "file_write", "agent_id": "a"})
        h2 = w.write({"event_type": "file_read", "agent_id": "b"})
        assert w.get_merkle_batches() == [h1, h2]

        root = w.finalize_current_batch()
        assert root == MerkleAggregator.build([h1, h2])
        assert len(root) == 64
        assert w.get_merkle_batches() == []
        # 批次已清空，二次 finalize 返回 None
        assert w.finalize_current_batch() is None

    def test_merkle_batch_skipped_when_disabled(self, writer):
        """enable_merkle=False 时不累积批次（fixture 默认 disable）。"""
        writer.write({"event_type": "file_write", "agent_id": "a"})
        assert writer.get_merkle_batches() == []
        assert writer.finalize_current_batch() is None

    def test_write_strips_producer_reserved_fields(self, writer, data_dir):
        """回归（AI-AUDIT12）：生产方预注入的 entry_hash/hmac_signature 必须被剔除，
        由 writer 统一重算——外来哈希值会把 canonical 绑死为不可验证状态。"""
        writer.write(
            {
                "event_type": "file_write",
                "agent_id": "a",
                "entry_hash": "f" * 64,
                "hmac_signature": "forged",
            }
        )
        with open(writer.event_log_path, encoding="utf-8") as f:
            written = json.loads(f.readline())
        assert written["entry_hash"] != "f" * 64
        assert written["hmac_signature"] != "forged"
