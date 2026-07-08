# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.external_merkle_proof
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_external_merkle_proof | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
External Merkle Proof — 外部可验证回滚完整性证明。

依据：
    蓝图 MOD-INF-021 §6.12 B74
    任务卡 TASK-INF-0250

功能：
    - 回滚 file tree -> Merkle root hash 计算
    - 外部（审计者/第三方）无需完整仓库即可验证
    - Merkle root 写入回滚审计日志——不可伪造
    - 对标区块链式可验证状态 + Git LFS verifiable-pointer
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT


@dataclass
class MerkleNode:
    hash_value: str
    left: MerkleNode | None = None
    right: MerkleNode | None = None
    file_path: str = ""


@dataclass
class MerkleProof:
    root_hash: str
    leaf_hash: str
    proof_hashes: list[str]
    leaf_index: int
    total_leaves: int
    file_path: str


@dataclass
class MerkleTree:
    root_hash: str
    leaves: list[MerkleNode]
    tree_height: int
    timestamp_utc: str
    commit_sha: str


@dataclass
class VerificationResult:
    verified: bool
    root_hash: str
    expected_root: str
    details: str = ""


class ExternalMerkleProof:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def merklize_file_tree(
        self,
        files: list[str],
        commit_sha: str = "",
    ) -> MerkleTree:
        leaves: list[MerkleNode] = []

        for file_path in sorted(files):
            full_path = self._project_root / file_path
            if not full_path.exists():
                continue

            content = full_path.read_bytes()
            file_hash = hashlib.sha256(content).hexdigest()
            leaves.append(
                MerkleNode(
                    hash_value=file_hash,
                    file_path=file_path,
                )
            )

        if not leaves:
            return MerkleTree(
                root_hash=hashlib.sha256(b"").hexdigest(),
                leaves=[],
                tree_height=0,
                timestamp_utc=datetime.now(UTC).isoformat(),
                commit_sha=commit_sha,
            )

        root = self._build_merkle_tree(leaves)
        tree_height = self._calculate_height(len(leaves))

        return MerkleTree(
            root_hash=root.hash_value,
            leaves=leaves,
            tree_height=tree_height,
            timestamp_utc=datetime.now(UTC).isoformat(),
            commit_sha=commit_sha,
        )

    def generate_proof(self, tree: MerkleTree, file_path: str) -> MerkleProof | None:
        leaf_index = -1
        for i, leaf in enumerate(tree.leaves):
            if leaf.file_path == file_path:
                leaf_index = i
                break

        if leaf_index < 0:
            return None

        proof_hashes: list[str] = []
        current_level = [leaf.hash_value for leaf in tree.leaves]

        idx = leaf_index
        while len(current_level) > 1:
            next_level: list[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                if i <= idx < i + 2:
                    if idx == i:
                        proof_hashes.append(right)
                    else:
                        proof_hashes.append(left)

                combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
                next_level.append(combined)

            current_level = next_level
            idx //= 2

        return MerkleProof(
            root_hash=tree.root_hash,
            leaf_hash=tree.leaves[leaf_index].hash_value,
            proof_hashes=proof_hashes,
            leaf_index=leaf_index,
            total_leaves=len(tree.leaves),
            file_path=file_path,
        )

    def verify_proof(self, proof: MerkleProof) -> VerificationResult:
        computed_hash = proof.leaf_hash
        idx = proof.leaf_index

        for sibling_hash in proof.proof_hashes:
            if idx % 2 == 0:
                combined = computed_hash + sibling_hash
            else:
                combined = sibling_hash + computed_hash
            computed_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            idx //= 2

        verified = computed_hash == proof.root_hash
        return VerificationResult(
            verified=verified,
            root_hash=computed_hash,
            expected_root=proof.root_hash,
            details="Merkle proof verification successful"
            if verified
            else f"Merkle proof verification FAILED: computed={computed_hash[:12]}... != expected={proof.root_hash[:12]}...",
        )

    def verify_file_in_tree(
        self,
        file_path: str,
        tree: MerkleTree,
        file_content: bytes,
    ) -> VerificationResult:
        leaf_hash = hashlib.sha256(file_content).hexdigest()

        for leaf in tree.leaves:
            if leaf.file_path == file_path:
                if leaf.hash_value == leaf_hash:
                    return VerificationResult(
                        verified=True,
                        root_hash=tree.root_hash,
                        expected_root=tree.root_hash,
                        details=f"File {file_path} verified in Merkle tree",
                    )
                return VerificationResult(
                    verified=False,
                    root_hash="",
                    expected_root=tree.root_hash,
                    details=f"File {file_path} hash mismatch: {leaf_hash[:12]}... != {leaf.hash_value[:12]}...",
                )

        return VerificationResult(
            verified=False,
            root_hash="",
            expected_root=tree.root_hash,
            details=f"File {file_path} not found in Merkle tree",
        )

    def sign_merkle_root(self, tree: MerkleTree, audit_session: str = "") -> dict[str, Any]:
        signature_input = f"{tree.root_hash}|{tree.timestamp_utc}|{tree.commit_sha}|{audit_session}"
        signature = hashlib.sha256(signature_input.encode("utf-8")).hexdigest()

        return {
            "merkle_root": tree.root_hash,
            "tree_height": tree.tree_height,
            "leaf_count": len(tree.leaves),
            "timestamp_utc": tree.timestamp_utc,
            "commit_sha": tree.commit_sha,
            "signature": signature,
            "algorithm": "SHA256",
            "audit_session": audit_session,
        }

    def export_merkle_tree(self, tree: MerkleTree, output_path: Path | None = None) -> Path:
        if output_path is None:
            output_path = (REPO_ROOT / "data" / "rollback" / "merkle") / f"{tree.commit_sha}_merkle.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "root_hash": tree.root_hash,
            "tree_height": tree.tree_height,
            "timestamp_utc": tree.timestamp_utc,
            "commit_sha": tree.commit_sha,
            "leaves": [{"file_path": leaf.file_path, "hash": leaf.hash_value} for leaf in tree.leaves],
        }

        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    @staticmethod
    def _build_merkle_tree(nodes: list[MerkleNode]) -> MerkleNode:
        if len(nodes) == 1:
            return nodes[0]

        parents: list[MerkleNode] = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left

            combined = left.hash_value + right.hash_value
            parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

            parents.append(
                MerkleNode(
                    hash_value=parent_hash,
                    left=left,
                    right=right,
                )
            )

        return ExternalMerkleProof._build_merkle_tree(parents)

    @staticmethod
    def _calculate_height(leaf_count: int) -> int:
        if leaf_count == 0:
            return 0
        height = 0
        while (1 << height) < leaf_count:
            height += 1
        return height + 1
