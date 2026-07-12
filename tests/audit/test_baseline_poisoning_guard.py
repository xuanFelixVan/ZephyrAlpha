# [A_test] module_id: SRC-TST-0414 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_baseline_poisoning_guard
# [INVARIANTS] 投毒防护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI/CD;drift_engine
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_baseline_poisoning_guard.py
# [TTL] task_bound

import hashlib

import zephyr.gov_drift.baseline_poisoning_guard as _bpg_mod
from zephyr.gov_drift.baseline_poisoning_guard import (
    HASH_CHAIN,
    FileBaselineSnapshot,
    HashChainEntry,
    MultiBaselineVote,
    _sha256,
    build_hash_chain,
    cross_validate_baseline,
    generate_integrity_manifest,
    multi_baseline_vote,
    verify_hash_chain,
)


class TestBaselineSnapshot:
    def test_default_fields(self):
        from datetime import datetime

        snap = FileBaselineSnapshot(
            version=1,
            file_path="test.py",
            content_hash="abc123",
            git_commit="deadbeef",
            scan_type="DEEP",
        )
        assert snap.version == 1
        assert snap.cross_validated is False
        assert isinstance(snap.timestamp, datetime)


class TestMultiBaselineVote:
    def test_default_fields(self):
        vote = MultiBaselineVote(
            file_path="test.py",
            snapshot_hashes=["h1", "h2"],
            majority_hash="h1",
        )
        assert vote.voters == 0
        assert vote.dissenters == 0
        assert vote.consensus is False


class TestHashChainEntry:
    def test_default_fields(self):
        entry = HashChainEntry(
            index=0,
            prev_hash="0" * 64,
            current_hash="a" * 64,
            chain_hash="b" * 64,
        )
        assert entry.git_commit == ""
        assert entry.verified is False


class TestSha256:
    def test_known_value(self):
        result = _sha256("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_empty_string(self):
        result = _sha256("")
        assert len(result) == 64

    def test_deterministic(self):
        assert _sha256("test") == _sha256("test")


class TestCrossValidateBaseline:
    def test_invalid_git_commit(self, tmp_path):
        result = cross_validate_baseline(
            baseline_content="hello",
            git_commit="invalid-commit",
            file_path="test.py",
            project_root=str(tmp_path),
        )
        assert result["file_path"] == "test.py"
        assert result["git_verified"] is False
        assert isinstance(result["diff_lines"], list)

    def test_returns_baseline_hash(self, tmp_path):
        result = cross_validate_baseline(
            baseline_content="content",
            git_commit="abc123",
            file_path="test.py",
            project_root=str(tmp_path),
        )
        assert result["baseline_hash"] == _sha256("content")


class TestMultiBaselineVote:
    def test_consensus_reached(self):
        snapshots = [
            FileBaselineSnapshot(version=1, file_path="a.py", content_hash="h1", git_commit="c1", scan_type="DEEP"),
            FileBaselineSnapshot(version=2, file_path="a.py", content_hash="h1", git_commit="c2", scan_type="DEEP"),
            FileBaselineSnapshot(version=3, file_path="a.py", content_hash="h2", git_commit="c3", scan_type="DEEP"),
        ]
        results = multi_baseline_vote(snapshots, threshold=2)
        assert len(results) == 1
        assert results[0].majority_hash == "h1"
        assert results[0].voters == 2
        assert results[0].dissenters == 1
        assert results[0].consensus is True

    def test_no_consensus(self):
        snapshots = [
            FileBaselineSnapshot(version=1, file_path="a.py", content_hash="h1", git_commit="c1", scan_type="DEEP"),
            FileBaselineSnapshot(version=2, file_path="a.py", content_hash="h2", git_commit="c2", scan_type="DEEP"),
        ]
        results = multi_baseline_vote(snapshots, threshold=2)
        assert len(results) == 1
        assert results[0].consensus is False

    def test_empty_snapshots(self):
        results = multi_baseline_vote([], threshold=2)
        assert results == []


class TestBuildHashChain:
    def test_builds_entry(self):
        initial_len = len(HASH_CHAIN)
        entry = build_hash_chain(
            prev_hash="0" * 64,
            current_data="test data",
            index=0,
        )
        assert isinstance(entry, HashChainEntry)
        assert entry.index == 0
        assert entry.current_hash == _sha256("test data")
        assert len(HASH_CHAIN) == initial_len + 1

    def test_chain_hash_with_git_commit(self):
        entry = build_hash_chain(
            prev_hash="0" * 64,
            current_data="data",
            index=1,
            git_commit="abc123",
        )
        expected_input = f"{'0' * 64}:{_sha256('data')}:abc123"
        assert entry.chain_hash == _sha256(expected_input)

    def test_chain_hash_without_git_commit(self):
        entry = build_hash_chain(
            prev_hash="0" * 64,
            current_data="data2",
            index=2,
        )
        expected_input = f"{'0' * 64}:{_sha256('data2')}"
        assert entry.chain_hash == _sha256(expected_input)


class TestVerifyHashChain:
    def test_valid_chain(self):
        entry0 = build_hash_chain(prev_hash="0" * 64, current_data="d0", index=0)
        entry1 = build_hash_chain(prev_hash=entry0.chain_hash, current_data="d1", index=1, git_commit="c1")
        violations = verify_hash_chain([entry0, entry1])
        assert violations == []

    def test_tampered_chain(self):
        entry0 = build_hash_chain(prev_hash="0" * 64, current_data="d0", index=0)
        entry1 = build_hash_chain(prev_hash=entry0.chain_hash, current_data="d1", index=1)
        tampered = HashChainEntry(
            index=1,
            prev_hash=entry1.prev_hash,
            current_hash=entry1.current_hash,
            chain_hash="tampered_hash_" + "0" * 51,
            git_commit="",
        )
        violations = verify_hash_chain([entry0, tampered])
        assert len(violations) == 1

    def test_single_entry_no_violation(self):
        entry = build_hash_chain(prev_hash="0" * 64, current_data="solo", index=0)
        violations = verify_hash_chain([entry])
        assert violations == []


class TestGenerateIntegrityManifest:
    def test_generates_manifest(self):
        result = generate_integrity_manifest(
            scan_id="scan-001",
            file_hashes={"a.py": "hash_a", "b.py": "hash_b"},
        )
        assert "INTEGRITY_MANIFEST_scan-001_" in result
        assert _bpg_mod.INTEGRITY_MANIFEST["scan_id"] == "scan-001"
        assert _bpg_mod.INTEGRITY_MANIFEST["data"]["file_count"] == 2

    def test_empty_file_hashes(self):
        result = generate_integrity_manifest(
            scan_id="scan-002",
            file_hashes={},
        )
        assert "INTEGRITY_MANIFEST_scan-002_" in result
        assert _bpg_mod.INTEGRITY_MANIFEST["data"]["file_count"] == 0
