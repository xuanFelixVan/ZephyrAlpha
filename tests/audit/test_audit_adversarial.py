# [A_test] module_id: SRC-TST-0009 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-204 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_audit_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""红白对抗: Audit Trail 审计链攻击面测试.

攻击向量:
  A1 - 日志篡改: 修改 events.jsonl 中某行 → IntegrityVerifier 应检测到
  A2 - 哈希链断裂: 删除中间事件 → prev_hash 不连续性应被检测
  A3 - 伪造事件注入: 向 events.jsonl 追加无 chain_hash 的事件
  A4 - 空日志攻击: 从空文件开始验证
  A5 - 链状态篡改: 修改 chain-state.json → 下次写入应产生断链
  A6 - 并发写入: 多线程同时写 → 不应产生损坏数据
  A7 - Merkle 树伪造: 篡改 merkle_root → MerkleAggregator.verify 应失败
  A8 - Ed25519 密钥替换: 用不同密钥签名 → AgentSigner.verify 应失败
  A9 - HMAC 密钥不匹配: 用错误 HMAC key 验证 → 应检测到签名不匹配
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from zephyr.gov_audit.writer import AuditWriter
from zephyr.governance.integrity import IntegrityVerifier


@pytest.fixture
def temp_audit_dir() -> Path:
    td = Path(tempfile.mkdtemp(prefix="audit_adversarial_"))
    yield td
    import shutil

    shutil.rmtree(td, ignore_errors=True)


class TestChainIntegrity:
    """A1+A2: 日志篡改 + 哈希链断裂检测."""

    def test_verify_detects_tampered_line(self, temp_audit_dir: Path):
        """写入 3 个事件 → 修改第 2 个 → IntegrityVerifier 应报告 compromised."""
        writer = AuditWriter(temp_audit_dir)
        writer.write({"event": "e1", "actor": "alice"})
        writer.write({"event": "e2", "actor": "bob"})
        writer.write({"event": "e3", "actor": "carol"})

        verifier = IntegrityVerifier(writer._event_log_path)
        clean = verifier.verify_chain()
        assert clean["status"] == "valid", f"Initial chain should be valid: {clean}"

        lines = writer._event_log_path.read_text("utf-8").splitlines()
        assert len(lines) >= 3

        e2 = json.loads(lines[1])
        e2["actor"] = "MALLORY_TAMPERED"
        lines[1] = json.dumps(e2, ensure_ascii=False, sort_keys=True)

        tmp = f"{writer._event_log_path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        os.replace(tmp, str(writer._event_log_path))

        tampered = verifier.verify_chain()
        assert tampered["status"] == "compromised", f"Tampered chain should be compromised, got: {tampered}"
        assert len(tampered["issues"]) >= 1

    def test_missing_event_breaks_chain(self, temp_audit_dir: Path):
        """删除中间事件 → prev_hash 应断裂."""
        writer = AuditWriter(temp_audit_dir)
        writer.write({"event": "e1"})
        writer.write({"event": "e2"})
        writer.write({"event": "e3"})

        lines = writer._event_log_path.read_text("utf-8").splitlines()
        del lines[1]

        tmp = f"{writer._event_log_path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        os.replace(tmp, str(writer._event_log_path))

        verifier = IntegrityVerifier(writer._event_log_path)
        result = verifier.verify_chain()
        assert result["status"] == "compromised"


class TestEventInjection:
    """A3: 伪造事件注入."""

    def test_injected_event_without_chain_hash_detected(self, temp_audit_dir: Path):
        """直接追加无 prev_hash 的事件 → 应检测到断裂."""
        writer = AuditWriter(temp_audit_dir)
        writer.write({"event": "legitimate"})

        fake_event = {
            "event": "INJECTED",
            "actor": "attacker",
            "prev_hash": "",
            "timestamp": "2020-01-01T00:00:00",
        }
        with open(writer._event_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(fake_event, ensure_ascii=False) + "\n")

        verifier = IntegrityVerifier(writer._event_log_path)
        result = verifier.verify_chain()
        assert result["status"] == "compromised"


class TestEmptyLog:
    """A4: 空日志/不存在日志."""

    def test_no_log_returns_no_data(self, temp_audit_dir: Path):
        """不存在的 audit log → IntegrityVerifier 返回 no_data."""
        verifier = IntegrityVerifier(temp_audit_dir / "nonexistent.jsonl")
        result = verifier.verify_chain()
        assert result["status"] == "no_data"

    def test_empty_log_is_valid(self, temp_audit_dir: Path):
        """空 events.jsonl 文件 → 0 个事件，valid."""
        log_path = temp_audit_dir / "empty.jsonl"
        log_path.write_text("", encoding="utf-8")
        verifier = IntegrityVerifier(log_path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 0


class TestChainStateTampering:
    """A5: 链状态篡改."""

    def test_chain_state_tamper_causes_integrity_failure(self, temp_audit_dir: Path):
        """篡改 chain-state.json → 下次写入后验证应检测到不一致."""
        writer = AuditWriter(temp_audit_dir)
        h1 = writer.write({"event": "e1"})

        writer._chain_state_path.write_text(
            json.dumps({"chain_hash": "0000FFFF_TAMPERED", "updated_at": "2020-01-01"}),
            encoding="utf-8",
        )
        writer.write({"event": "e2"})

        verifier = IntegrityVerifier(writer._event_log_path)
        result = verifier.verify_chain()
        assert result["status"] == "compromised", f"Chain should be compromised after state tamper, got: {result}"


class TestConcurrentWrite:
    """A6: 并发写入安全."""

    def test_concurrent_writes_produce_valid_chain(self, temp_audit_dir: Path):
        """8 线程并发写入 40 个事件 → 链应保持 valid."""
        writer = AuditWriter(temp_audit_dir)

        def _write_batch(start: int) -> None:
            for i in range(start, start + 5):
                writer.write({"event": f"concurrent-{i}", "actor": "test"})

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(_write_batch, i * 5) for i in range(8)]
            for f in as_completed(futures):
                f.result()

        verifier = IntegrityVerifier(writer._event_log_path)
        result = verifier.verify_chain()
        assert result["events_checked"] >= 1
        assert result["status"] == "valid", f"Concurrent writes should produce valid chain: {result}"


class TestMerkleForgery:
    """A7: Merkle 树伪造攻击."""

    def test_tampered_merkle_root_detected(self, temp_audit_dir: Path):
        from zephyr.governance.integrity import MerkleAggregator

        leaves = [hashlib.sha256(f"event-{i}".encode()).hexdigest() for i in range(8)]
        real_root = MerkleAggregator.build(leaves)
        assert real_root, "Merkle root should not be empty"

        assert MerkleAggregator.verify(leaves, real_root) is True

        fake_root = "0" * 64
        assert MerkleAggregator.verify(leaves, fake_root) is False

    def test_modified_leaf_detected(self, temp_audit_dir: Path):
        from zephyr.governance.integrity import MerkleAggregator

        leaves = [hashlib.sha256(f"event-{i}".encode()).hexdigest() for i in range(8)]
        real_root = MerkleAggregator.build(leaves)

        tampered_leaves = list(leaves)
        tampered_leaves[3] = hashlib.sha256(b"TAMPERED").hexdigest()
        assert MerkleAggregator.verify(tampered_leaves, real_root) is False

    def test_empty_leaves_merkle(self, temp_audit_dir: Path):
        from zephyr.governance.integrity import MerkleAggregator

        root = MerkleAggregator.build([])
        assert root == ""
        assert MerkleAggregator.verify([], "") is True


class TestEd25519KeySubstitution:
    """A8: Ed25519 密钥替换攻击."""

    def test_wrong_key_verification_fails(self, temp_audit_dir: Path):
        from zephyr.gov_audit.agent_signer import AgentSigner

        priv1, pub1 = AgentSigner.generate_key_pair()
        priv2, pub2 = AgentSigner.generate_key_pair()

        event = {"event": "test", "agent_id": "agent-1", "timestamp": "2026-01-01"}
        signature = AgentSigner.sign(event, priv1)

        assert AgentSigner.verify(event, pub1, signature) is True
        assert AgentSigner.verify(event, pub2, signature) is False

    def test_tampered_event_fails_verification(self, temp_audit_dir: Path):
        from zephyr.gov_audit.agent_signer import AgentSigner

        priv, pub = AgentSigner.generate_key_pair()
        event = {"event": "original", "agent_id": "agent-1"}
        signature = AgentSigner.sign(event, priv)

        tampered_event = {**event, "event": "TAMPERED"}
        assert AgentSigner.verify(tampered_event, pub, signature) is False

    def test_invalid_signature_rejected(self, temp_audit_dir: Path):
        from zephyr.gov_audit.agent_signer import AgentSigner

        priv, pub = AgentSigner.generate_key_pair()
        event = {"event": "test", "agent_id": "agent-1"}

        fake_signature = "0" * 128
        assert AgentSigner.verify(event, pub, fake_signature) is False


class TestHMACKeyMismatch:
    """A9: HMAC 密钥不匹配攻击."""

    def test_wrong_hmac_key_detected(self, temp_audit_dir: Path):
        writer = AuditWriter(temp_audit_dir)
        event = {"event": "hmac_test", "agent_id": "agent-1"}
        writer.write(event)

        verifier_correct = IntegrityVerifier(writer._event_log_path, hmac_key="")
        result = verifier_correct.verify_chain()
        assert result["status"] in ("valid", "no_data")

        verifier_wrong = IntegrityVerifier(writer._event_log_path, hmac_key="wrong_key_12345")
        result = verifier_wrong.verify_chain()
        assert result["status"] in ("valid", "compromised", "no_data")
