# [A_module] module_id=MOD-SEC_code_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-014 | docs/03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.security.llm_defense.llm_security.self_protection.code_integrity

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field


class IntegrityStatus:
    CLEAN = "clean"
    TAMPERED = "tampered"
    UNKNOWN = "unknown"


class FileIntegrityRecord(BaseModel):
    path: str
    sha256: str
    size_bytes: int = 0
    last_verified: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = IntegrityStatus.UNKNOWN


class CodeIntegrityGuard:

    _CRITICAL_DIRS: Tuple[str, ...] = (
        "src/zephyr/llm-security/layers",
        "src/zephyr/llm-security/self_protection",
    )

    def __init__(self, project_root: str = ""):
        self._project_root = project_root or os.getcwd()
        self._baseline: Dict[str, str] = {}
        self._records: Dict[str, FileIntegrityRecord] = {}
        self._lock = threading.Lock()
        self._compromised: bool = False
        self._last_scan_time: float = 0.0
        self._scan_interval_seconds: float = 1800.0

    def compute_baseline_for_directory(self, dir_path: str) -> List[FileIntegrityRecord]:
        records: List[FileIntegrityRecord] = []
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

    def compute_full_baseline(self) -> List[FileIntegrityRecord]:
        all_records: List[FileIntegrityRecord] = []
        for d in self._CRITICAL_DIRS:
            all_records.extend(self.compute_baseline_for_directory(d))
        return all_records

    def verify_single(self, file_path: str) -> FileIntegrityRecord:
        existing = self._records.get(file_path)
        fp = Path(os.path.join(self._project_root, file_path))

        if not fp.exists():
            return FileIntegrityRecord(
                path=file_path, sha256="", size_bytes=0, status=IntegrityStatus.UNKNOWN
            )

        try:
            content = fp.read_bytes()
            current_sha = hashlib.sha256(content).hexdigest()
            expected_sha = existing.sha256 if existing else ""
            status = (
                IntegrityStatus.CLEAN
                if current_sha == expected_sha
                else IntegrityStatus.TAMPERED
            )
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
            return FileIntegrityRecord(
                path=file_path, sha256="", size_bytes=0, status=IntegrityStatus.UNKNOWN
            )

    def verify_all(self) -> Dict[str, Any]:
        results: List[FileIntegrityRecord] = []
        tampered: List[str] = []

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
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }

    def periodic_scan_if_due(self) -> Optional[Dict[str, Any]]:
        if time.time() - self._last_scan_time >= self._scan_interval_seconds:
            return self.verify_all()
        return None

    @property
    def is_compromised(self) -> bool:
        return self._compromised

    @property
    def baseline(self) -> Dict[str, str]:
        return dict(self._baseline)
