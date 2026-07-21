# [A_test] module_id: MOD-GOV_external_merkle_proof | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §

# [MODULE] tests.test_external_merkle_proof

# [INVARIANTS] ExternalMerkleProof merkle tree root hash is deterministic and verifiable

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from zephyr.infrastructure.rollback.external_merkle_proof import (
    ExternalMerkleProof,
    MerkleProof,
)


def _create_files(tmp_path: Path, file_dict: dict[str, str]) -> list[str]:
    paths: list[str] = []
    for name, content in file_dict.items():
        fpath = tmp_path / name
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
        paths.append(name)
    return paths


class TestExternalMerkleProofInit:
    def test_default_project_root(self, tmp_path: Path):
        emp = ExternalMerkleProof(project_root=tmp_path)
        assert emp._project_root == tmp_path

    def test_none_project_root_uses_cwd(self):
        emp = ExternalMerkleProof(project_root=None)
        assert emp._project_root == Path.cwd()


class TestExternalMerkleProofMerklize:
    def test_merklize_single_file(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "hello"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files, commit_sha="sha1")
        assert tree.root_hash
        assert len(tree.leaves) == 1
        assert tree.leaves[0].file_path == "a.txt"
        assert tree.commit_sha == "sha1"

    def test_merklize_multiple_files(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "aaa", "b.txt": "bbb", "c.txt": "ccc"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        assert len(tree.leaves) == 3
        assert tree.tree_height > 0

    def test_merklize_empty_files_list(self, tmp_path: Path):
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree([], commit_sha="empty")
        assert tree.root_hash == hashlib.sha256(b"").hexdigest()
        assert tree.leaves == []
        assert tree.tree_height == 0

    def test_merklize_nonexistent_file_skipped(self, tmp_path: Path):
        files = _create_files(tmp_path, {"exists.txt": "data"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files + ["missing.txt"])
        assert len(tree.leaves) == 1

    def test_merklize_deterministic_root(self, tmp_path: Path):
        files = _create_files(tmp_path, {"x.txt": "fixed content"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree1 = emp.merklize_file_tree(files)
        tree2 = emp.merklize_file_tree(files)
        assert tree1.root_hash == tree2.root_hash


class TestExternalMerkleProofGenerateAndVerify:
    def test_generate_proof_for_file(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha", "b.txt": "beta"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        proof = emp.generate_proof(tree, "a.txt")
        assert proof is not None
        assert proof.file_path == "a.txt"
        assert proof.leaf_index >= 0
        assert proof.total_leaves == 2

    def test_verify_proof_succeeds(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha", "b.txt": "beta"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        proof = emp.generate_proof(tree, "a.txt")
        assert proof is not None
        result = emp.verify_proof(proof)
        assert result.verified is True

    def test_generate_proof_missing_file_returns_none(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        proof = emp.generate_proof(tree, "nonexistent.txt")
        assert proof is None

    def test_verify_file_in_tree_matches(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        result = emp.verify_file_in_tree("a.txt", tree, b"alpha")
        assert result.verified is True

    def test_verify_file_in_tree_mismatch(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        result = emp.verify_file_in_tree("a.txt", tree, b"tampered")
        assert result.verified is False

    def test_verify_file_in_tree_not_found(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        result = emp.verify_file_in_tree("missing.txt", tree, b"data")
        assert result.verified is False


class TestExternalMerkleProofSignAndExport:
    def test_sign_merkle_root(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files, commit_sha="sha1")
        sig = emp.sign_merkle_root(tree, audit_session="sess-001")
        assert sig["merkle_root"] == tree.root_hash
        assert sig["leaf_count"] == 1
        assert sig["algorithm"] == "SHA256"
        assert sig["audit_session"] == "sess-001"
        assert "signature" in sig

    def test_sign_merkle_root_empty_session(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "data"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        sig = emp.sign_merkle_root(tree)
        assert sig["audit_session"] == ""

    def test_export_merkle_tree(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files, commit_sha="export1")
        output = tmp_path / "output.json"
        result_path = emp.export_merkle_tree(tree, output_path=output)
        assert result_path.exists()
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["root_hash"] == tree.root_hash
        assert len(data["leaves"]) == 1

    def test_export_merkle_tree_default_path(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files, commit_sha="defaultpath")
        result_path = emp.export_merkle_tree(tree, output_path=tmp_path / "merkle_out.json")
        assert result_path.exists()


class TestExternalMerkleProofBoundary:
    def test_merklize_single_file_tree_height(self, tmp_path: Path):
        files = _create_files(tmp_path, {"solo.txt": "only one"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        assert tree.tree_height >= 1

    def test_proof_with_odd_number_of_files(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "1", "b.txt": "2", "c.txt": "3"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        for f in files:
            proof = emp.generate_proof(tree, f)
            assert proof is not None
            result = emp.verify_proof(proof)
            assert result.verified is True

    def test_tampered_proof_fails_verification(self, tmp_path: Path):
        files = _create_files(tmp_path, {"a.txt": "alpha", "b.txt": "beta"})
        emp = ExternalMerkleProof(project_root=tmp_path)
        tree = emp.merklize_file_tree(files)
        proof = emp.generate_proof(tree, "a.txt")
        assert proof is not None
        tampered = MerkleProof(
            root_hash=proof.root_hash,
            leaf_hash=hashlib.sha256(b"fake").hexdigest(),
            proof_hashes=proof.proof_hashes,
            leaf_index=proof.leaf_index,
            total_leaves=proof.total_leaves,
            file_path=proof.file_path,
        )
        result = emp.verify_proof(tampered)
        assert result.verified is False
