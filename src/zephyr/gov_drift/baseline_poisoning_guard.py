# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.baseline_poisoning_guard
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] tests/audit/test_baseline_poisoning_guard.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 投毒防护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Baseline Poisoning Guard — 基线投毒防护 D-023-36 · §6.25。

cross_validation: 基线快照 vs git对应commit原始代码diff，每DEEP scan抽样10%

multi_baseline_voting: 保留3版本，>=2基线同意才信任

git_as_ultimate_truth: baseline_hash_chain=SHA256(prev+current)写入commit message

integrity_manifest: 每DEEP scan签名存Git

对标 blueprint.md §6.25。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: baseline_content 参数
#   fields: 参数 baseline_content，类型注解 str
#   code: baseline_poisoning_guard.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: git_commit 参数
#   fields: 参数 git_commit，类型注解 str
#   code: baseline_poisoning_guard.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 str
#   code: baseline_poisoning_guard.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str
#   code: baseline_poisoning_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① cross_validate_baseline
#   name_en: cross_validate_baseline
#   intro: cross_validate_baseline(baseline_content, git_commit, file_…
#   desc: 源码 L182-L234
#   inputs: baseline_content git_commit file_path project_root
#   outputs: dict[str, object]
# - id: A2
#   name_zh: ② multi_baseline_vote
#   name_en: multi_baseline_vote
#   intro: multi_baseline_vote(snapshots, threshold) 源码 L237-L273
#   desc: 源码 L237-L273
#   inputs: snapshots threshold
#   outputs: list[MultiBaselineVote]
# - id: A3
#   name_zh: ③ build_hash_chain
#   name_en: build_hash_chain
#   intro: build_hash_chain(prev_hash, current_data, index, git_commit…
#   desc: 源码 L276-L301
#   inputs: prev_hash current_data index git_commit
#   outputs: HashChainEntry
# - id: A4
#   name_zh: ④ verify_hash_chain
#   name_en: verify_hash_chain
#   intro: verify_hash_chain(entries) 源码 L304-L321
#   desc: 源码 L304-L321
#   inputs: entries
#   outputs: list[str]
# - id: A5
#   name_zh: ⑤ generate_integrity_manifest
#   name_en: generate_integrity_manifest
#   intro: generate_integrity_manifest(scan_id, file_hashes) 源码 L324-L…
#   desc: 源码 L324-L348
#   inputs: scan_id file_hashes
#   outputs: str
#   （注：A5 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[str, object]
#   name_en: dict[str, object]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/audit/test_baseline_poisoning_guard.py
# - id: O2
#   name_zh: list[MultiBaselineVote]
#   name_en: list[MultiBaselineVote]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/audit/test_baseline_poisoning_guard.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

import hashlib
import json
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
        proc = run_subprocess_hidden(
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

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
