# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.build_reproducibility_verifier
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_build_reproducibility_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Build Reproducibility Verifier — v0.38.0 R484

Blindspot: AI construction produces code that works in the current environment
but cannot be built from source on a clean machine. Missing dependencies,
hardcoded paths, environment-specific assumptions accumulate silently.

Risk: R484 — System works today but cannot be rebuilt tomorrow. Disaster recovery
impossible because build-from-source path is broken. 1-person team discovers
this during actual disaster when it's too late.

Mitigation: Periodically verify build reproducibility. Check that all dependencies
resolve, all import paths exist, CI/CD pipeline produces identical artifacts.
Flag non-reproducible builds before they become critical.
"""

from __future__ import annotations

import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum


class BuildIntegrity(str, Enum):
    REPRODUCIBLE = "REPRODUCIBLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    BROKEN = "BROKEN"


@dataclass
class BuildReproducibilityVerifier:
    max_drift_tolerance: float = 0.05
    build_retention: int = 10

    build_hashes: list[dict] = field(default_factory=list)
    integrity_violations: list[dict] = field(default_factory=list)
    last_verification: float = 0.0

    def hash_directory(self, root_path: str) -> str:
        file_paths: list[str] = []
        for dirpath, _, filenames in os.walk(root_path):
            for fn in sorted(filenames):
                if fn.endswith(".pyc") or fn.startswith("__pycache__"):
                    continue
                file_paths.append(os.path.join(dirpath, fn))

        def _read_file(path: str) -> bytes:
            try:
                with open(path, "rb") as f:
                    return f.read()
            except OSError:
                return b""

        contents: list[bytes] = []
        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(_read_file, p): p for p in file_paths}
            for future in as_completed(futures):
                contents.append(future.result())

        hasher = hashlib.sha256()
        for content in contents:
            hasher.update(content)
        return hasher.hexdigest()

    def record_build_hash(self, label: str, source_hash: str) -> dict:
        entry = {"ts": time.time(), "label": label, "hash": source_hash}
        self.build_hashes.append(entry)
        if len(self.build_hashes) > self.build_retention:
            self.build_hashes = self.build_hashes[-self.build_retention :]

        if len(self.build_hashes) >= 2:
            prev = self.build_hashes[-2]["hash"]
            if prev != source_hash:
                self.integrity_violations.append(
                    {
                        "ts": time.time(),
                        "type": BuildIntegrity.DRIFT_DETECTED.value,
                        "previous": prev[:12],
                        "current": source_hash[:12],
                    }
                )
                return {
                    "integrity": BuildIntegrity.DRIFT_DETECTED.value,
                    "previous_build": prev[:12],
                    "current_build": source_hash[:12],
                    "recommendation": "investigate_source_drift",
                }

        self.last_verification = time.time()
        return {"integrity": BuildIntegrity.REPRODUCIBLE.value, "hash": source_hash[:12]}

    def verify_dependencies(self, required_modules: list[str]) -> dict:
        missing = []
        for mod in required_modules:
            try:
                __import__(mod)
            except ImportError:
                missing.append(mod)
            except Exception:
                missing.append(mod)

        if missing:
            self.integrity_violations.append(
                {
                    "ts": time.time(),
                    "type": BuildIntegrity.BROKEN.value,
                    "missing_modules": missing,
                }
            )

        return {
            "integrity": BuildIntegrity.BROKEN.value if missing else BuildIntegrity.REPRODUCIBLE.value,
            "missing_modules": missing,
            "total_checked": len(required_modules),
            "recommendation": "install_missing_deps" if missing else "build_reproducible",
        }

    def verify_ci_consistency(self, ci_hash: str, local_hash: str) -> dict:
        consistent = ci_hash == local_hash
        if not consistent:
            self.integrity_violations.append(
                {
                    "ts": time.time(),
                    "type": "CI_LOCAL_MISMATCH",
                    "ci_hash": ci_hash[:12],
                    "local_hash": local_hash[:12],
                }
            )
        return {
            "consistent": consistent,
            "ci_hash": ci_hash[:12],
            "local_hash": local_hash[:12],
            "recommendation": "rebuild_ci_environment" if not consistent else "continue",
        }

    def overall_reproducibility_score(self) -> float:
        if not self.build_hashes:
            return 1.0
        unique_hashes = len(set(b["hash"] for b in self.build_hashes))
        return round(1.0 / max(unique_hashes, 1), 3)

    def get_days_since_last_verification(self) -> float:
        if self.last_verification == 0:
            return float("inf")
        return (time.time() - self.last_verification) / 86400.0
