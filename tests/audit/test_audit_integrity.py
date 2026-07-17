# [A_test] module_id: SRC-TST-0356 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_integrity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from zephyr.gov_audit.integrity import IntegrityVerifier, MerkleAggregator


class TestMerkleAggregatorBuild:
    def test_empty_leaves_returns_empty(self):
        result = MerkleAggregator.build([])
        assert result == ""

    def test_single_leaf(self):
        leaf = hashlib.sha256(b"test").hexdigest()
        result = MerkleAggregator.build([leaf])
        assert result == leaf

    def test_two_leaves(self):
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()
        result = MerkleAggregator.build([h1, h2])
        expected = hashlib.sha256(bytes.fromhex(h1) + bytes.fromhex(h2)).hexdigest()
        assert result == expected

    def test_odd_number_leaves_pads(self):
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()
        h3 = hashlib.sha256(b"c").hexdigest()
        result = MerkleAggregator.build([h1, h2, h3])
        assert result != ""

    def test_empty_string_leaf_skipped(self):
        h1 = hashlib.sha256(b"a").hexdigest()
        result = MerkleAggregator.build([h1, ""])
        assert result == h1


class TestMerkleAggregatorVerify:
    def test_verify_valid_root(self):
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()
        root = MerkleAggregator.build([h1, h2])
        assert MerkleAggregator.verify([h1, h2], root) is True

    def test_verify_invalid_root(self):
        h1 = hashlib.sha256(b"a").hexdigest()
        assert MerkleAggregator.verify([h1], "invalid_root") is False

    def test_verify_empty(self):
        assert MerkleAggregator.verify([], "") is True


class TestIntegrityVerifierInit:
    def test_default_path(self):
        from zephyr.shared.io.paths import AUDIT_DATA_DIR
        verifier = IntegrityVerifier()
        assert verifier._event_log_path == AUDIT_DATA_DIR / "events.jsonl"

    def test_custom_path(self, tmp_path):
        path = tmp_path / "custom.jsonl"
        verifier = IntegrityVerifier(event_log_path=path)
        assert verifier._event_log_path == path

    def test_hmac_key(self):
        verifier = IntegrityVerifier(hmac_key="secret")
        assert verifier._hmac_key == b"secret"


class TestVerifyChain:
    def test_no_file_returns_no_data(self, tmp_path):
        verifier = IntegrityVerifier(event_log_path=tmp_path / "missing.jsonl")
        result = verifier.verify_chain()
        assert result["status"] == "no_data"
        assert result["events_checked"] == 0

    def test_empty_file_returns_valid(self, tmp_path):
        path = tmp_path / "events.jsonl"
        path.write_text("", encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 0

    def test_valid_chain(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "timestamp": "2026-01-01", "data": "hello"}
        event_str = json.dumps(event, ensure_ascii=False, sort_keys=True, default=str)
        entry_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()
        event["prev_entry_hash"] = ""
        event["entry_hash"] = entry_hash
        path.write_text(json.dumps(event), encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "valid"
        assert result["events_checked"] == 1

    def test_broken_chain(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "prev_entry_hash": "wrong_hash", "timestamp": "2026-01-01"}
        path.write_text(json.dumps(event), encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_chain()
        assert result["status"] == "compromised"
        assert len(result["issues"]) > 0


class TestVerifySingle:
    def test_no_file(self, tmp_path):
        verifier = IntegrityVerifier(event_log_path=tmp_path / "missing.jsonl")
        result = verifier.verify_single(1)
        assert result["status"] == "no_data"
        assert result["valid"] is False

    def test_index_out_of_range(self, tmp_path):
        path = tmp_path / "events.jsonl"
        path.write_text(json.dumps({"event_type": "test"}), encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(99)
        assert result["status"] == "not_found"
        assert result["valid"] is False

    def test_found_event(self, tmp_path):
        path = tmp_path / "events.jsonl"
        event = {"event_type": "test", "timestamp": "2026-01-01"}
        path.write_text(json.dumps(event), encoding="utf-8")
        verifier = IntegrityVerifier(event_log_path=path)
        result = verifier.verify_single(1)
        assert result["status"] == "found"
        assert result["valid"] is True
        assert "chain_hash" in result
