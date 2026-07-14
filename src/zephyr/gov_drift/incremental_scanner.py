# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.incremental_scanner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_scanners.py; tests/audit/test_incremental_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 增量扫描不可遗漏变更
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_incremental_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Incremental Scanner — incremental_scanner.py


git diff 驱动的增量扫描器，变更影响范围计算与检测器匹配。


对标 blueprint.md §2.4（增量扫描与性能 SLO）。"""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass, field


@dataclass
class FileChange:
    path: str

    status: str

    sha256: str = ""


@dataclass
class ChangeSet:
    changed_files: list[FileChange] = field(default_factory=list)

    affected_detectors: list[str] = field(default_factory=list)

    affected_modules: list[str] = field(default_factory=list)

    is_storm: bool = False

    total_changes: int = 0


@dataclass
class DetectorFileMapping:
    _map: dict[str, list[str]] = field(default_factory=dict)

    def register(self, detector_id: str, file_pattern: str) -> None:
        self._map.setdefault(file_pattern, []).append(detector_id)

    def find_detectors(self, changed_files: list[str]) -> list[str]:
        matched: set[str] = set()

        for fp in changed_files:
            for pattern, detectors in self._map.items():
                if pattern in fp or fp.endswith(pattern.lstrip("*")):
                    matched.update(detectors)

        return list(matched)


class IncrementalScanner:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._mapping = DetectorFileMapping()

        self._cache: dict[str, str] = {}

    def get_changed_files(self, base_ref: str = "HEAD~1") -> list[FileChange]:
        try:
            result = subprocess.run(
                ["git", "diff", base_ref, "--name-status"],
                capture_output=True,
                text=True,
                cwd=self._project_root,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            files: list[FileChange] = []

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")

                if len(parts) >= 2:
                    files.append(FileChange(path=parts[1], status=parts[0]))

                elif len(parts) == 1:
                    files.append(FileChange(path=parts[0], status="M"))

            return files

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def compute_impact(self, changed_files: list[str] | None = None) -> ChangeSet:
        changes = self.get_changed_files()

        if changed_files:
            changes = [c for c in changes if c.path in changed_files]

        change_set = ChangeSet(
            changed_files=changes,
            total_changes=len(changes),
            is_storm=len(changes) > 50,
        )

        file_paths = [c.path for c in changes]

        change_set.affected_detectors = self._mapping.find_detectors(file_paths)

        change_set.affected_modules = list(set(self._extract_module(c.path) for c in changes))

        return change_set

    def _extract_module(self, filepath: str) -> str:
        if filepath.startswith("src/zephyr/") or filepath.startswith("docs/03_modules/"):
            parts = filepath.split("/")

            if len(parts) >= 3:
                return parts[2]

        return "unknown"

    def register_mapping(self, detector_id: str, patterns: list[str]) -> None:
        for p in patterns:
            self._mapping.register(detector_id, p)

    def file_hash(self, filepath: str) -> str:
        full = os.path.join(self._project_root, filepath)

        if not os.path.exists(full):
            return ""

        try:
            with open(full, "rb") as fh:
                return hashlib.sha256(fh.read()).hexdigest()

        except OSError:
            return ""
