# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.dep_version_fixer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只统一版本;不升级major版本;以最高minor/patch为准
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml dep_version_fixer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DepVersionFixError
# [TESTS] tests/auto-fix-engine/test_dep_version_fixer.py
# [A_module] module_id=MOD-INF_dep_version_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    BaseFixer,
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class DepVersionFixer(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="dep_version_fixer",
            action_type="dep_version_fix",
            level=FixLevel.L1_RULE,
            dimension="DIM-DEP-VERSION-001",
            description="修复依赖版本不一致",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        dep_versions: dict[str, list[dict[str, str]]] = defaultdict(list)
        for req_file in repo_root.rglob("requirements*.txt"):
            try:
                content = req_file.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    match = re.match(r"^([A-Za-z0-9_\-]+)\s*([><=!~]+)\s*([0-9][0-9A-Za-z.\-]*)", line)
                    if match:
                        pkg, op, ver = match.groups()
                        dep_versions[pkg.lower()].append(
                            {
                                "file": str(req_file),
                                "operator": op,
                                "version": ver,
                                "line": line,
                            }
                        )
            except Exception:
                continue
        for pkg, entries in dep_versions.items():
            versions = set(e["version"] for e in entries)
            if len(versions) > 1:
                findings.append(
                    {
                        "package": pkg,
                        "versions": list(versions),
                        "locations": entries,
                        "type": "version_conflict",
                    }
                )
        pyproject = repo_root / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8")
                for match in re.finditer(r"([A-Za-z0-9_\-]+)\s*=\s*\"([0-9][0-9A-Za-z.\-]*)\"", content):
                    pkg, ver = match.groups()
                    if pkg.lower() in dep_versions:
                        for entry in dep_versions[pkg.lower()]:
                            if entry["version"] != ver:
                                findings.append(
                                    {
                                        "package": pkg.lower(),
                                        "versions": [ver, entry["version"]],
                                        "locations": [{"file": str(pyproject), "version": ver}, entry],
                                        "type": "pyproject_conflict",
                                    }
                                )
            except Exception as e:
                logger.warning("DepVersionFixer.scan: pyproject.toml parse failed (%s: %s)", type(e).__name__, e)
        return findings

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        action = FixAction(
            action_type=self.action_type,
            level=self.level,
            target=target,
            confidence=FixConfidence.HIGH,
        )
        target_path = Path(target)
        if not target_path.exists():
            action.status = FixStatus.FAILED
            return action
        try:
            content = target_path.read_text(encoding="utf-8")
            original = content
            pkg_versions: dict[str, str] = {}
            lines = content.splitlines()
            for line in lines:
                match = re.match(r"^([A-Za-z0-9_\-]+)\s*([><=!~]+)\s*([0-9][0-9A-Za-z.\-]*)", line.strip())
                if match:
                    pkg, _, ver = match.groups()
                    existing = pkg_versions.get(pkg.lower())
                    if existing is None or self._is_higher(ver, existing):
                        pkg_versions[pkg.lower()] = ver
            new_lines: list[str] = []
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    new_lines.append(line)
                    continue
                match = re.match(r"^([A-Za-z0-9_\-]+)\s*([><=!~]+)\s*([0-9][0-9A-Za-z.\-]*)", stripped)
                if match:
                    pkg, op, ver = match.groups()
                    target_ver = pkg_versions.get(pkg.lower(), ver)
                    if ver != target_ver and self._is_higher(target_ver, ver):
                        new_line = line.replace(f"{op}{ver}", f"=={target_ver}")
                        new_lines.append(new_line)
                        continue
                new_lines.append(line)
            content = "\n".join(new_lines)
            if content != original:
                action.before = original
                action.after = content
                if not dry_run:
                    tmp_path = f"{target}.{os.getpid()}.tmp"
                    try:
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        os.replace(tmp_path, target)
                    except PermissionError:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
                        action.status = FixStatus.FAILED
                        return action
                action.status = FixStatus.COMPLETED
            else:
                action.status = FixStatus.COMPLETED
                action.metadata["note"] = "No version conflicts found"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _is_higher(self, ver_a: str, ver_b: str) -> bool:
        def _parse(v: str) -> tuple[int, ...]:
            parts = re.findall(r"\d+", v)
            return tuple(int(p) for p in parts)

        try:
            return _parse(ver_a) > _parse(ver_b)
        except (ValueError, IndexError):
            return False

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="dep_version_fix", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            pkg_versions: dict[str, list[str]] = defaultdict(list)
            for line in content.splitlines():
                match = re.match(r"^([A-Za-z0-9_\-]+)\s*[><=!~]+\s*([0-9][0-9A-Za-z.\-]*)", line.strip())
                if match:
                    pkg_versions[match.group(1).lower()].append(match.group(2))
            conflicts = {p: vs for p, vs in pkg_versions.items() if len(set(vs)) > 1}
            if conflicts:
                return ValidationResult(
                    valid=False,
                    check_name="dep_version_fix",
                    evidence=f"Conflicts: {conflicts}",
                    error="Version conflicts remain",
                )
            return ValidationResult(valid=True, check_name="dep_version_fix", evidence="No version conflicts")
        except Exception as exc:
            return ValidationResult(valid=False, check_name="dep_version_fix", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
