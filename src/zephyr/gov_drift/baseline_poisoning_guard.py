# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.baseline_poisoning_guard
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; tests/audit/test_baseline_poisoning_guard.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 投毒防护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_baseline_poisoning_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Baseline Poisoning Guard — 基线投毒防护 D-023-36 · §6.25。


cross_validation: 基线快照 vs git对应commit原始代码diff，每DEEP scan抽样10%


multi_baseline_voting: 保留3版本，>=2基线同意才信任


git_as_ultimate_truth: baseline_hash_chain=SHA256(prev+current)写入commit message


integrity_manifest: 每DEEP scan签名存Git


对标 blueprint.md §6.25。"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class FileBaselineSnapshot:
    version: int

    file_path: str

    content_hash: str

    git_commit: str

    scan_type: str

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    cross_validated: bool = False


@dataclass
class MultiBaselineVote:
    file_path: str

    snapshot_hashes: list[str]

    majority_hash: str

    voters: int = 0

    dissenters: int = 0

    consensus: bool = False


@dataclass
class HashChainEntry:
    index: int

    prev_hash: str

    current_hash: str

    chain_hash: str

    git_commit: str = ""

    verified: bool = False


HASH_CHAIN: Final[list[HashChainEntry]] = []


INTEGRITY_MANIFEST: Final[dict[str, object]] = {}


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def cross_validate_baseline(
    baseline_content: str,
    git_commit: str,
    file_path: str,
    project_root: str,
) -> dict[str, object]:
    result: dict[str, object] = {
        "file_path": file_path,
        "baseline_hash": _sha256(baseline_content),
        "git_verified": False,
        "diff_lines": [],
    }

    try:
        proc = subprocess.run(
            ["git", "show", f"{git_commit}:{file_path}"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root,
        )

        if proc.returncode == 0:
            git_content = proc.stdout

            git_hash = _sha256(git_content)

            if git_hash == result["baseline_hash"]:
                result["git_verified"] = True

            else:
                diff_lines: list[str] = []

                baseline_lines = baseline_content.splitlines()

                git_lines = git_content.splitlines()

                max_lines = max(len(baseline_lines), len(git_lines))

                for i in range(min(max_lines, 100)):
                    b_line = baseline_lines[i] if i < len(baseline_lines) else ""

                    g_line = git_lines[i] if i < len(git_lines) else ""

                    if b_line != g_line:
                        diff_lines.append(f"L{i + 1}: baseline vs git: {b_line[:40]} <> {g_line[:40]}")

                result["diff_lines"] = diff_lines[:20]

    except Exception as e:
        logger.warning("suppressed error in baseline_poisoning_guard", exc_info=True)

    return result


def multi_baseline_vote(
    snapshots: list[FileBaselineSnapshot],
    threshold: int = 2,
) -> list[MultiBaselineVote]:
    votes: dict[str, dict[str, int]] = {}

    for snap in snapshots:
        votes.setdefault(snap.file_path, {})[snap.content_hash] = (
            votes.get(snap.file_path, {}).get(snap.content_hash, 0) + 1
        )

    results: list[MultiBaselineVote] = []

    for file_path, hash_counts in votes.items():
        sorted_hashes = sorted(hash_counts.items(), key=lambda x: -x[1])

        if not sorted_hashes:
            continue

        majority_hash = sorted_hashes[0][0]

        voters = sorted_hashes[0][1]

        dissenters = sum(c for _h, c in sorted_hashes[1:])

        results.append(
            MultiBaselineVote(
                file_path=file_path,
                snapshot_hashes=list(hash_counts.keys()),
                majority_hash=majority_hash,
                voters=voters,
                dissenters=dissenters,
                consensus=voters >= threshold,
            )
        )

    return results


def build_hash_chain(
    prev_hash: str,
    current_data: str,
    index: int = 0,
    git_commit: str = "",
) -> HashChainEntry:
    current_hash = _sha256(current_data)

    chain_input = f"{prev_hash}:{current_hash}"

    if git_commit:
        chain_input += f":{git_commit}"

    chain_hash = _sha256(chain_input)

    entry = HashChainEntry(
        index=index,
        prev_hash=prev_hash,
        current_hash=current_hash,
        chain_hash=chain_hash,
        git_commit=git_commit,
    )

    HASH_CHAIN.append(entry)

    return entry


def verify_hash_chain(entries: list[HashChainEntry]) -> list[str]:
    violations: list[str] = []

    for i, entry in enumerate(entries):
        if i == 0:
            continue

        expected_input = f"{entry.prev_hash}:{entry.current_hash}"

        if entry.git_commit:
            expected_input += f":{entry.git_commit}"

        expected_chain = _sha256(expected_input)

        if expected_chain != entry.chain_hash:
            violations.append(f"Chain break at index {i}: expected {expected_chain[:12]} got {entry.chain_hash[:12]}")

    return violations


def generate_integrity_manifest(
    scan_id: str,
    file_hashes: dict[str, str],
) -> str:
    manifest_data: dict[str, object] = {
        "scan_id": scan_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "file_count": len(file_hashes),
        "files": {fpath: {"sha256": fhash} for fpath, fhash in file_hashes.items()},
        "integrity_chain_head": (HASH_CHAIN[-1].chain_hash if HASH_CHAIN else ""),
    }

    manifest_content = json.dumps(manifest_data, indent=2, sort_keys=True)

    manifest_hash = _sha256(manifest_content)

    global INTEGRITY_MANIFEST

    INTEGRITY_MANIFEST = {
        "scan_id": scan_id,
        "hash": manifest_hash,
        "data": manifest_data,
    }

    return f"INTEGRITY_MANIFEST_{scan_id}_{manifest_hash[:12]}"
