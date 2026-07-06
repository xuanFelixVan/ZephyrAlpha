# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.cascade_analyzer
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_cascade_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import re
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_IMPORT_PATTERNS = [
    re.compile(r"from\s+([\w.]+)\s+import"),
    re.compile(r"import\s+([\w.]+)"),
]


class CascadeRisk(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CascadeResult(BaseModel):
    path: str
    direct_dependents: list[str] = Field(default_factory=list)
    indirect_dependents: list[str] = Field(default_factory=list)
    safe_to_delete: bool = False
    cascade_risk: CascadeRisk = CascadeRisk.LOW


class CascadeAnalyzerError(Exception):
    error_code = "ZA-SC-0031"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class CascadeAnalyzer:
    """删除级联分析器——分析删除文件对项目的影响。

    基于简化版 import 引用图分析（grep 搜索 import 语句），
    识别直接和间接依赖者，评估级联风险。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        if project_root is None:
            self._root = Path.cwd()
        else:
            self._root = Path(project_root).resolve()
        self._src_dir = self._root / "src" / "zephyr"

    def analyze_cascade(self, path: str | Path) -> CascadeResult:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return CascadeResult(
                path=str(resolved),
                direct_dependents=[],
                indirect_dependents=[],
                safe_to_delete=False,
                cascade_risk=CascadeRisk.HIGH,
            )

        module_path = self._file_to_module(resolved)
        direct = self.find_dependents(str(resolved))
        indirect = self._find_indirect_dependents(direct, module_path)

        risk = self._assess_risk(direct, indirect)
        safe = risk is CascadeRisk.LOW and len(indirect) == 0

        return CascadeResult(
            path=str(resolved),
            direct_dependents=sorted(direct),
            indirect_dependents=sorted(indirect),
            safe_to_delete=safe,
            cascade_risk=risk,
        )

    def find_dependents(self, path: str) -> list[str]:
        resolved = self._resolve_path(path)
        module_path = self._file_to_module(resolved)
        if not module_path:
            return []

        dependents: list[str] = []
        py_files = self._collect_py_files()

        for py_file in py_files:
            if py_file.resolve() == resolved.resolve():
                continue
            if self._file_imports_module(py_file, module_path):
                dependents.append(str(py_file))

        return sorted(dependents)

    def _find_indirect_dependents(self, direct_dependents: list[str], original_module: str) -> list[str]:
        indirect: set[str] = set()
        visited: set[str] = set()

        queue = list(direct_dependents)
        while queue:
            dep_path = queue.pop(0)
            if dep_path in visited:
                continue
            visited.add(dep_path)

            dep_resolved = self._resolve_path(dep_path)
            dep_module = self._file_to_module(dep_resolved)
            if not dep_module:
                continue

            sub_deps = self.find_dependents(dep_path)
            for sub_dep in sub_deps:
                if sub_dep not in visited and sub_dep not in direct_dependents:
                    indirect.add(sub_dep)
                    if len(indirect) < 200:
                        queue.append(sub_dep)

        return sorted(indirect)

    def _assess_risk(self, direct: list[str], indirect: list[str]) -> CascadeRisk:
        total = len(direct) + len(indirect)
        if total == 0:
            return CascadeRisk.LOW
        if len(indirect) > 0 or len(direct) > 5:
            return CascadeRisk.HIGH
        if len(direct) > 2:
            return CascadeRisk.MEDIUM
        return CascadeRisk.LOW

    def _file_to_module(self, resolved: Path) -> str:
        try:
            rel = resolved.relative_to(self._root / "src")
        except ValueError:
            return ""

        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        elif parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        else:
            return ""

        return ".".join(parts)

    def _file_imports_module(self, py_file: Path, module_path: str) -> bool:
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        module_prefix = module_path.split(".")
        for pattern in _IMPORT_PATTERNS:
            for match in pattern.finditer(content):
                imported = match.group(1)
                imported_parts = imported.split(".")
                if len(imported_parts) >= len(module_prefix):
                    if imported_parts[: len(module_prefix)] == module_prefix:
                        return True
                if imported.startswith(module_path):
                    return True
        return False

    def _collect_py_files(self) -> list[Path]:
        if not self._src_dir.exists():
            return []
        files: list[Path] = []
        for py_file in self._src_dir.rglob("*.py"):
            if any(p in py_file.parts for p in ("__pycache__", ".mypy_cache", "_snapshots", ".aidrafts")):
                continue
            files.append(py_file)
        return files

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p.resolve()
        return (self._root / p).resolve()
