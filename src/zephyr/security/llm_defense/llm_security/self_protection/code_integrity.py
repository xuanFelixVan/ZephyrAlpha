# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.self_protection.code_integrity
# [DOMAIN] D_SECURITY
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
# [A_module] module_id=MOD-SEC_code_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import hashlib
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class IntegrityStatus:
    CLEAN = "clean"
    TAMPERED = "tampered"
    UNKNOWN = "unknown"


class FileIntegrityRecord(BaseModel):
    path: str
    sha256: str
    size_bytes: int = 0
    last_verified: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = IntegrityStatus.UNKNOWN


class CodeIntegrityGuard:
    _CRITICAL_DIRS: tuple[str, ...] = (
        "src/zephyr/security/llm_defense/llm_security/layers",
        "src/zephyr/security/llm_defense/llm_security/self_protection",
    )

    def __init__(self, project_root: str = ""):
        self._project_root = project_root or os.getcwd()
        self._baseline: dict[str, str] = {}
        self._records: dict[str, FileIntegrityRecord] = {}
        self._lock = threading.Lock()
        self._compromised: bool = False
        self._last_scan_time: float = 0.0
        self._scan_interval_seconds: float = 1800.0

    def compute_baseline_for_directory(self, dir_path: str) -> list[FileIntegrityRecord]:
        records: list[FileIntegrityRecord] = []
        base = Path(os.path.join(self._project_root, dir_path))
        if not base.exists():
            return records

        for root, _, files in os.walk(str(base)):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fp = Path(root) / fname
                try:
                    content = fp.read_bytes()
                    sha = hashlib.sha256(content).hexdigest()
                    record = FileIntegrityRecord(
                        path=str(fp.relative_to(self._project_root)),
                        sha256=sha,
                        size_bytes=len(content),
                        status=IntegrityStatus.CLEAN,
                    )
                    records.append(record)
                    with self._lock:
                        self._baseline[record.path] = sha
                        self._records[record.path] = record
                except (OSError, PermissionError):
                    pass

        self._last_scan_time = time.time()
        return records

    def compute_full_baseline(self) -> list[FileIntegrityRecord]:
        all_records: list[FileIntegrityRecord] = []
        for d in self._CRITICAL_DIRS:
            all_records.extend(self.compute_baseline_for_directory(d))
        return all_records

    def verify_single(self, file_path: str) -> FileIntegrityRecord:
        existing = self._records.get(file_path)
        fp = Path(os.path.join(self._project_root, file_path))

        if not fp.exists():
            return FileIntegrityRecord(path=file_path, sha256="", size_bytes=0, status=IntegrityStatus.UNKNOWN)

        try:
            content = fp.read_bytes()
            current_sha = hashlib.sha256(content).hexdigest()
            expected_sha = existing.sha256 if existing else ""
            status = IntegrityStatus.CLEAN if current_sha == expected_sha else IntegrityStatus.TAMPERED
            record = FileIntegrityRecord(
                path=file_path,
                sha256=current_sha,
                size_bytes=len(content),
                status=status,
            )
            with self._lock:
                self._records[file_path] = record
                if status == IntegrityStatus.TAMPERED:
                    self._compromised = True
            return record
        except (OSError, PermissionError):
            return FileIntegrityRecord(path=file_path, sha256="", size_bytes=0, status=IntegrityStatus.UNKNOWN)

    def verify_all(self) -> dict[str, Any]:
        results: list[FileIntegrityRecord] = []
        tampered: list[str] = []

        for file_path in list(self._baseline.keys()):
            record = self.verify_single(file_path)
            results.append(record)
            if record.status == IntegrityStatus.TAMPERED:
                tampered.append(file_path)

        return {
            "total": len(results),
            "clean": len(results) - len(tampered),
            "tampered": len(tampered),
            "tampered_files": tampered,
            "compromised": self._compromised,
            "scanned_at": datetime.now(UTC).isoformat(),
        }

    def periodic_scan_if_due(self) -> dict[str, Any] | None:
        if time.time() - self._last_scan_time >= self._scan_interval_seconds:
            return self.verify_all()
        return None

    @property
    def is_compromised(self) -> bool:
        return self._compromised

    @property
    def baseline(self) -> dict[str, str]:
        return dict(self._baseline)

    def register_baseline(self, file_path: str, sha256: str) -> None:
        """Register an externally-computed baseline hash for a file path.

        Supports both absolute and relative paths. Stores the expected
        sha256 so ``check_integrity`` can later verify the current content.
        """
        with self._lock:
            self._baseline[file_path] = sha256
            self._records[file_path] = FileIntegrityRecord(
                path=file_path,
                sha256=sha256,
                size_bytes=0,
                status=IntegrityStatus.CLEAN,
            )

    def check_integrity(self, file_path: str) -> Any:
        """Verify the current on-disk content hash against the registered baseline.

        Returns an object with ``passed`` (bool) and ``actual_sha256`` (str)
        attributes. A file is ``passed`` only if its current sha256 matches
        the registered baseline. Missing baseline or tampered content yields
        ``passed=False``.
        """
        import hashlib as _hashlib
        from pathlib import Path as _Path
        from types import SimpleNamespace as _NS

        fp = _Path(file_path)
        if not fp.exists():
            return _NS(passed=False, actual_sha256="")
        try:
            content = fp.read_bytes()
            actual = _hashlib.sha256(content).hexdigest()
        except (OSError, PermissionError):
            return _NS(passed=False, actual_sha256="")
        with self._lock:
            expected = self._baseline.get(file_path)
        passed = bool(expected) and actual == expected
        return _NS(passed=passed, actual_sha256=actual)
