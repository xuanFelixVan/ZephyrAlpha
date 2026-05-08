"""
Core Integrity Guard — 核心文件完整性墙 (盲点 #51)
特性：
  - 启动时校验项目核心文件 hash
  - project_rules.md / AGENTS.md / task-card-template.md 防篡改
"""
import hashlib
import os
from typing import Any, Optional


class CoreIntegrityGuard:
    """
    核心完整性守护 (盲点 #51)
    """

    CORE_FILES = [
        ".trae/rules/project_rules.md",
        "AGENTS.md",
        "docs/01_policies_and_standards/templates/task-card-template.md",
        "src/zephyr/shared/schemas.py",
    ]

    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        self.project_root = project_root
        self._baseline_hashes: dict[str, str] = {}

    def set_baseline(self):
        for rel_path in self.CORE_FILES:
            full_path = os.path.join(self.project_root, rel_path)
            if os.path.exists(full_path):
                with open(full_path, "rb") as f:
                    self._baseline_hashes[rel_path] = hashlib.sha256(f.read()).hexdigest()

    def verify(self) -> dict:
        violations = []
        verified = []
        for rel_path in self.CORE_FILES:
            full_path = os.path.join(self.project_root, rel_path)
            if not os.path.exists(full_path):
                violations.append({"file": rel_path, "issue": "MISSING"})
                continue

            expected_hash = self._baseline_hashes.get(rel_path)
            if expected_hash is None:
                verified.append(rel_path)
                continue

            with open(full_path, "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()

            if current_hash == expected_hash:
                verified.append(rel_path)
            else:
                violations.append({"file": rel_path, "issue": "MODIFIED"})

        return {
            "intact": len(violations) == 0,
            "verified": verified,
            "violations": violations,
        }
