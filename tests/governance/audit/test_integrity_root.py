# [A_test] module_id: SRC-TST-1138 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_integrity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_integrity.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

from zephyr.gov_audit.integrity import IntegrityVerifier, MerkleAggregator


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events),
        encoding="utf-8",
    )


class TestMerkleAggregatorBuild:
    def test_empty_leaves_returns_empty_string(self):
        result = MerkleAggregator.build([])
        assert result == ""

    def test_single_leaf_returns_leaf_hash(self):
        leaf = _sha256_hex(b"test")
        result = MerkleAggregator.build([leaf])
        assert result == leaf

    def test_two_leaves_returns_combined_hash(self):
        h1 = _sha256_hex(b"a")
        h2 = _sha256_hex(b"b")
        result = MerkleAggregator.build([h1, h2])
        expected = hashlib.sha256(bytes.fromhex(h1) + bytes.fromhex(h2)).hexdigest()
        assert result == expected

    def test_odd_number_leaves_pads_last(self):
        h1 = _sha256_hex(b"a")
        h2 = _sha256_hex(b"b")
        h3 = _sha256_hex(b"c")
        result = MerkleAggregator.build([h1, h2, h3])
        assert result != ""
        assert len(result) == 64

    def test_empty_string_leaf_is_skipped(self):
        h1 = _sha256_hex(b"a")
        result = MerkleAggregator.build([h1, ""])
        assert result == h1

    def test_all_empty_strings_returns_empty(self):
        result = MerkleAggregator.build(["", "", ""])
        assert result == ""

    def test_four_leaves_builds_two_levels(self):
        leaves = [_sha256_hex(f"leaf{i}".encode()) for i in range(4)]
        result = MerkleAggregator.build(leaves)
        assert len(result) == 64
        assert MerkleAggregator.verify(leaves, result) is True

    def test_deterministic_output(self):
        leaves = [_sha256_hex(f"x{i}".encode()) for i in range(3)]
        r1 = MerkleAggregator.build(leaves)
        r2 = MerkleAggregator.build(leaves)
        assert r1 == r2


class TestMerkleAggregatorVerify:
    def test_verify_valid_root(self):
        h1 = _sha256_hex(b"a")
        h2 = _sha256_hex(b"b")
        root = MerkleAggregator.build([h1, h2])
        assert MerkleAggregator.verify([h1, h2], root) is True

    def test_verify_invalid_root(self):
        h1 = _sha256_hex(b"a")
        assert MerkleAggregator.verify([h1], "invalid_root_value") is False

    def test_verify_empty_leaves_empty_root(self):
        assert MerkleAggregator.verify([], "") is True

    def test_verify_tampered_leaves(self):
        h1 = _sha256_hex(b"a")
        h2 = _sha256_hex(b"b")
        root = MerkleAggregator.build([h1, h2])
        h2_tampered = _sha256_hex(b"c")
        assert MerkleAggregator.verify([h1, h2_tampered], root) is False

    def test_verify_extra_leaf_fails(self):
        h1 = _sha256_hex(b"a")
        h2 = _sha256_hex(b"b")
        root = MerkleAggregator.build([h1, h2])
        h3 = _sha256_hex(b"c")
        assert MerkleAggregator.verify([h1, h2, h3], root) is False


class TestIntegrityVerifierInit:
    def test_default_path(self):
        # 治本（裁定#6 路径SSoT）：默认路径必须为绝对路径（项目硬约束"禁止相对路径"），
        # 真源为 zephyr.shared.io.paths.AUDIT_DATA_DIR。
        from zephyr.shared.io.paths import AUDIT_DATA_DIR
        verifier = IntegrityVerifier()
        assert verifier._event_log_path == AUDIT_DATA_DIR / "events.jsonl"

    def test_custom_path(self, tmp_path):
        path = tmp_path / "custom.jsonl"
        verifier = IntegrityVerifier(event_log_path=path)
        assert verifier._event_log_path == path

    def test_hmac_key_stored_as_bytes(self):
        verifier = IntegrityVerifier(hmac_key="secret")
        assert verifier._hmac_key == b"secret"

    def test_empty_hmac_key_stored_as_empty_bytes(self):
        verifier = IntegrityVerifier(hmac_key="")
        assert verifier._hmac_key == b""


class TestVerifyChain:
    def test_no_file_returns_no_data(self, tmp_path):
        verifier = IntegrityVerifier(event_log_path=tmp_path / "missing.jsonl")
        result = verifier.verify_chain()
        assert result["status"] == "no_data"
        assert result["events_checked"] == 0
        assert result["issues"] == []

    def test_empty_file_returns_valid(self, tmp_path):
        path = tmp_path / "events.jsonl"
        path.write_text("", encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 0

    def test_single_valid_event(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "timestamp": "2026-01-01", "prev_entry_hash": ""}
        event_str = json.dumps(event, ensure_ascii=False, sort_keys=True, default=str)
        event["entry_hash"] = hashlib.sha256(event_str.encode("utf-8")).hexdigest()
        _write_jsonl(path, [event])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 1
        assert result["issues"] == []

    def test_chain_with_broken_link(self, tmp_path):
        path = tmp_path / "events.jsonl"
        e1 = {"event_type": "a", "timestamp": "2026-01-01", "prev_entry_hash": ""}
        e1_str = json.dumps(e1, ensure_ascii=False, sort_keys=True, default=str)
        e1["entry_hash"] = hashlib.sha256(e1_str.encode("utf-8")).hexdigest()
        e2 = {"event_type": "b", "timestamp": "2026-01-02", "prev_entry_hash": "WRONG_HASH"}
        _write_jsonl(path, [e1, e2])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "compromised"
        assert len(result["issues"]) >= 1

    def test_valid_two_event_chain(self, tmp_path):
        path = tmp_path / "events.jsonl"
        e1 = {"event_type": "a", "timestamp": "2026-01-01", "data": "first"}
        e1_verify = {k: v for k, v in e1.items() if k not in ("entry_hash", "hmac_signature")}
        e1_hash = hashlib.sha256(
            json.dumps(e1_verify, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        e2 = {"event_type": "b", "timestamp": "2026-01-02", "data": "second", "prev_entry_hash": e1_hash}
        _write_jsonl(path, [e1, e2])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 2

    def test_with_hmac_verification(self, tmp_path):
        path = tmp_path / "events.jsonl"
        key = b"test-hmac-key"
        event = {"event_type": "test", "timestamp": "2026-01-01"}
        event_str = json.dumps(event, ensure_ascii=False, sort_keys=True, default=str)
        sig = hmac.new(key, event_str.encode("utf-8"), hashlib.sha256).hexdigest()
        event["hmac_signature"] = sig
        _write_jsonl(path, [event])
        verifier = IntegrityVerifier(event_log_path=path, hmac_key="test-hmac-key")
        result = verifier.verify_chain()
        assert result["status"] == "valid"

    def test_with_invalid_hmac(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "timestamp": "2026-01-01", "hmac_signature": "bad_sig"}
        _write_jsonl(path, [event])
        verifier = IntegrityVerifier(event_log_path=path, hmac_key="test-hmac-key")
        result = verifier.verify_chain()
        assert result["status"] == "compromised"


class TestVerifySingle:
    def test_no_file_returns_no_data(self, tmp_path):
        verifier = IntegrityVerifier(event_log_path=tmp_path / "missing.jsonl")
        result = verifier.verify_single(1)
        assert result["status"] == "no_data"
        assert result["valid"] is False

    def test_index_out_of_range(self, tmp_path):
        path = tmp_path / "events.jsonl"
        _write_jsonl(path, [{"event_type": "test"}])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(99)
        assert result["status"] == "not_found"
        assert result["valid"] is False

    def test_found_event_returns_valid(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "timestamp": "2026-01-01"}
        _write_jsonl(path, [event])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(1)
        assert result["status"] == "found"
        assert result["valid"] is True
        assert "chain_hash" in result

    def test_second_event_in_chain(self, tmp_path):
        path = tmp_path / "events.jsonl"
        e1 = {"event_type": "a", "timestamp": "2026-01-01"}
        e2 = {"event_type": "b", "timestamp": "2026-01-02"}
        _write_jsonl(path, [e1, e2])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(2)
        assert result["status"] == "found"
        assert result["valid"] is True

    def test_index_zero_returns_not_found(self, tmp_path):
        path = tmp_path / "events.jsonl"
        _write_jsonl(path, [{"event_type": "test"}])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(0)
        assert result["status"] == "not_found"
        assert result["valid"] is False


class TestBoundaryConditions:
    def test_file_with_only_blank_lines(self, tmp_path):
        path = tmp_path / "events.jsonl"
        path.write_text("\n\n\n", encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 0

    def test_large_chain_integrity(self, tmp_path):
        path = tmp_path / "events.jsonl"
        events: list[dict] = []
        prev_hash = ""
        for i in range(50):
            event: dict = {"event_type": f"t{i % 5}", "timestamp": f"2026-01-{i + 1:02d}", "prev_entry_hash": prev_hash}
            verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
            prev_hash = hashlib.sha256(
                json.dumps(verify_event, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()
            events.append(event)
        _write_jsonl(path, events)
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 50

    def test_special_characters_in_event_data(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "data": "日本語テスト 🎉", "prev_entry_hash": ""}
        _write_jsonl(path, [event])
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
