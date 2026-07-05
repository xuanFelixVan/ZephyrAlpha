# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §L1
# [MODULE] zephyr.security.access_control.orphan_judge.reference_graph_engine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] orphan-judge.judge._run_layer L1
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AST解析+import链遍历; 不修改任何文件; import扫描范围限 src/zephyr/ + scripts/
# [MODIFY-GUARD] 修改引用检测逻辑必须同步 blueprint.md §3.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AST解析失败时返回 is_reachable=False,不抛异常
# [TESTS] tests/orphan-judge/test_reference_graph_engine.py
# [A_module] module_id=MOD-SEC_reference_graph_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-029 — L1 引用图引擎

AST解析+import链遍历，判断文件是否被其他文件引用。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.security.access_control.orphan_judge.judge import LayerResult

logger = logging.getLogger(__name__)

__all__ = [
    "ReferenceGraphEngine",
]

_IMPORT_FROM_RE = re.compile(
    r"from\s+(zephyr\.[\w.]+)\s+import",
    re.MULTILINE,
)
_IMPORT_DIRECT_RE = re.compile(
    r"import\s+(zephyr\.[\w.]+)",
    re.MULTILINE,
)
_SCAN_DIRS = ["src/zephyr/", "scripts/"]


class ReferenceGraphEngine:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()
        self._cache: dict[str, list[str]] = {}

    def check(self, path: str) -> LayerResult:
        file_path = self._root / path
        module_path = self._path_to_module(file_path)

        referenced_by: list[str] = []
        for scan_rel in _SCAN_DIRS:
            scan_dir = self._root / scan_rel
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                if py_file.resolve() == file_path.resolve():
                    continue
                if self._file_imports_target(py_file, file_path, module_path):
                    rel = str(py_file.relative_to(self._root)).replace("\\", "/")
                    referenced_by.append(rel)
                    if len(referenced_by) >= 20:
                        break
            if len(referenced_by) >= 20:
                break

        is_reachable = len(referenced_by) > 0
        return LayerResult(
            layer="L1",
            passed=is_reachable,
            detail=f"Referenced by {len(referenced_by)} files" if is_reachable else "No references found",
            data={
                "is_reachable": is_reachable,
                "referenced_by": referenced_by,
            },
        )

    def _path_to_module(self, file_path: Path) -> str:
        rel = file_path.relative_to(self._root)
        parts = list(rel.parts)
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        return ".".join(parts)

    def _file_imports_target(self, source: Path, target: Path, target_module: str) -> bool:
        target_name = target.stem
        target_parent = str(target.parent).replace("\\", "/")
        try:
            content = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        if f'"{target_name}"' in content or f"'{target_name}'" in content:
            return True

        if target_parent in content:
            return True

        from_matches = _IMPORT_FROM_RE.findall(content)
        for mod in from_matches:
            if mod.startswith(target_module) or target_module.startswith(mod):
                return True

        direct_matches = _IMPORT_DIRECT_RE.findall(content)
        for mod in direct_matches:
            if mod.startswith(target_module):
                return True

        return False
