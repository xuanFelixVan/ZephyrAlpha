# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.boot_integrity_attestation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_boot_integrity_attestation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Boot Integrity Attestation — v0.38.0 R487

Blindspot: FLE starts up and immediately begins making automated decisions without
verifying its own integrity. If FLE code or config was tampered with (by a rogue
AI session, malware, or accidental corruption), it operates with compromised logic.

Risk: R487 — Compromised FLE silently makes bad decisions; "the watchdog is rabid."
Unauthorized modifications to FLE rules/config go undetected across restarts.

Mitigation: At startup, compute SHA256 hash of all FLE source files and compare
against known-good attestation manifest. Verify config integrity. If any hash
mismatch -> refuse to start in full-auto mode, degrade to observe-only.
Require owner attestation override to proceed.
"""

from __future__ import annotations

import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum


class BootIntegrityResult(str, Enum):
    ATTESTED = "ATTESTED"
    MODIFIED_UNVERIFIED = "MODIFIED_UNVERIFIED"
    CORRUPTED = "CORRUPTED"
    TAMPERED = "TAMPERED"


def _collect_python_files(source_roots: list[str]) -> list[tuple[str, str]]:
    """Walk source_roots and return (full_path, manifest_key) pairs for *.py files."""
    files_to_hash: list[tuple[str, str]] = []
    for root in source_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, start=root)
                files_to_hash.append((full, f"{root}/{rel}"))
    return files_to_hash


def _compute_current_hashes(compute_fn, files_to_hash: list[tuple[str, str]]) -> dict[str, str]:
    """Compute SHA256 for each file in parallel, returning {manifest_key: hash}."""
    current_hashes: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(compute_fn, full): key for full, key in files_to_hash}
        for future in as_completed(futures):
            key = futures[future]
            current_hashes[key] = future.result()
    return current_hashes


def _diff_hashes(
    known_good_hashes: dict[str, str],
    current_hashes: dict[str, str],
) -> tuple[list[dict], list[str], list[str]]:
    """Compare current hashes against known-good; return (mismatches, new_files, deleted_files)."""
    mismatches: list[dict] = []
    new_files: list[str] = []
    deleted_files: list[str] = []
    for path, expected_hash in known_good_hashes.items():
        current = current_hashes.get(path, "")
        if not current:
            deleted_files.append(path)
        elif current != expected_hash:
            mismatches.append({"path": path, "expected": expected_hash[:12], "current": current[:12]})
    for path in current_hashes:
        if path not in known_good_hashes:
            new_files.append(path)
    return mismatches, new_files, deleted_files


def _classify_boot_integrity(deleted_count: int, violation_count: int) -> BootIntegrityResult:
    """Map violation counts to a BootIntegrityResult."""
    if violation_count == 0:
        return BootIntegrityResult.ATTESTED
    if deleted_count > 5:
        return BootIntegrityResult.TAMPERED
    return BootIntegrityResult.MODIFIED_UNVERIFIED


def _build_attestation_result(
    boot_integrity: BootIntegrityResult,
    violation_count: int,
    mismatches: list[dict],
    new_files: list[str],
    deleted_files: list[str],
    auto_degrade_on_failure: bool,
) -> dict:
    """Build the attestation result dict."""
    return {
        "integrity": boot_integrity.value,
        "violation_count": violation_count,
        "mismatches": mismatches[:10],
        "new_files_count": len(new_files),
        "deleted_files_count": len(deleted_files),
        "degraded": boot_integrity is not BootIntegrityResult.ATTESTED and auto_degrade_on_failure,
        "recommendation": (
            "owner_override_required"
            if boot_integrity is BootIntegrityResult.TAMPERED
            else "review_changes"
            if violation_count > 0
            else "proceed_full_auto"
        ),
    }


@dataclass
class BootIntegrityAttestation:
    attestation_manifest_path: str = ".runtime/fle_attestation_manifest.json"
    auto_degrade_on_failure: bool = True

    known_good_hashes: dict[str, str] = field(default_factory=dict)
    boot_integrity: BootIntegrityResult = BootIntegrityResult.ATTESTED
    mismatch_details: list[dict] = field(default_factory=list)
    last_attestation: float = 0.0

    def compute_file_hash(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return ""

    def build_manifest(self, source_roots: list[str]) -> dict:
        files_to_hash: list[tuple[str, str]] = []
        for root in source_roots:
            if not os.path.isdir(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, start=root)
                    files_to_hash.append((full, f"{root}/{rel}"))

        manifest: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(self.compute_file_hash, full): key for full, key in files_to_hash}
            for future in as_completed(futures):
                key = futures[future]
                manifest[key] = future.result()

        self.known_good_hashes = manifest
        return {
            "files_hashed": len(manifest),
            "manifest_root_count": len(source_roots),
            "generated_at": time.time(),
        }

    def attest(self, source_roots: list[str]) -> dict:
        if not self.known_good_hashes:
            return {"integrity": BootIntegrityResult.CORRUPTED.value, "detail": "no known-good manifest — first run?"}

        files_to_hash = _collect_python_files(source_roots)
        current_hashes = _compute_current_hashes(self.compute_file_hash, files_to_hash)
        mismatches, new_files, deleted_files = _diff_hashes(self.known_good_hashes, current_hashes)

        violation_count = len(mismatches) + len(deleted_files) + len(new_files)
        self.boot_integrity = _classify_boot_integrity(len(deleted_files), violation_count)
        self.mismatch_details = mismatches
        self.last_attestation = time.time()

        return _build_attestation_result(
            self.boot_integrity,
            violation_count,
            mismatches,
            new_files,
            deleted_files,
            self.auto_degrade_on_failure,
        )

    def owner_attest_override(self, owner_signature: str) -> dict:
        if self.boot_integrity is BootIntegrityResult.TAMPERED:
            self.boot_integrity = BootIntegrityResult.ATTESTED
            return {"override_accepted": True, "new_integrity": self.boot_integrity.value}
        return {"override_accepted": False, "reason": "no tampering detected — override unnecessary"}

    def get_integrity_status(self) -> dict:
        return {
            "boot_integrity": self.boot_integrity.value,
            "last_attestation_age_s": round(time.time() - self.last_attestation, 1) if self.last_attestation else 0,
            "mismatch_count": len(self.mismatch_details),
            "safe_to_operate": self.boot_integrity is BootIntegrityResult.ATTESTED,
        }
