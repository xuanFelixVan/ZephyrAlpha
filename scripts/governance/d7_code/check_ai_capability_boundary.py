"""
check_ai_capability_boundary.py — AI 能力边界静态检查脚本

在 CI 阶段扫描所有 Python 文件，检测是否有代码修改了 IMMUTABLE 级别的
文件或绕过了能力边界。读取 config/ai_capability_matrix.yaml 获取边界定义。

exit codes: 0=pass, 1=violations found, 2=error
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

import yaml

MATRIX_PATH = REPO_ROOT / "config/ai_capability_matrix.yaml"


def load_matrix() -> dict | None:
    """加载能力矩阵"""
    if not MATRIX_PATH.exists():
        return None
    "加载能力矩阵."
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def get_immutable_scopes() -> list[str]:
    """加载能力矩阵."""
    matrix = load_matrix()
    if matrix is None:
        return [
            "shared/contracts/",
            "docs/02_enterprise_architecture/adr/",
            "docs/01_policies_and_standards/governance/ai/",
            "gates/_registry.yaml",
        ]
    scopes: list[str] = []
    for entry in matrix.get("matrix", {}).get("entries", []):
        if entry.get("level") == "IMMUTABLE":
            scopes.append(entry["scope"])
    return scopes
    "获取不可变作用域列表."


def _matches_scope(file_rel: str, scope: str) -> bool:
    import fnmatch

    file_normalized = file_rel.replace("\\", "/")
    scope_normalized = scope.replace("\\", "/")
    if scope_normalized.endswith("/*"):
        prefix = scope_normalized[:-2]
        return file_normalized.startswith(prefix) or file_normalized == prefix.rstrip("/")
    if scope_normalized.endswith("/*.py"):
        prefix = scope_normalized[:-5]
        return file_normalized.startswith(prefix) and file_normalized.endswith(".py")
    if scope_normalized.endswith("/*.md"):
        prefix = scope_normalized[:-5]
        return file_normalized.startswith(prefix) and file_normalized.endswith(".md")
    return fnmatch.fnmatch(file_normalized, scope_normalized)


def find_capability_violations() -> list[dict]:
    """查找能力边界违规"""
    immutable_scopes = get_immutable_scopes()
    "find capability violations."
    src_dir = REPO_ROOT / "src" / "zephyr"
    violations: list[dict] = []
    unchanged_files: list[str] = ["shared/contracts/__init__.py", "shared/contracts/enforcer.py", "shared/__init__.py"]
    for py_file in iter_files(src_dir, extensions={".py"}):
        rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        is_immutable = any(_matches_scope(rel, scope) for scope in immutable_scopes)
        if is_immutable and rel not in unchanged_files:
            is_new = True
            for unchanged in unchanged_files:
                if unchanged in rel or unchanged.endswith(rel):
                    is_new = False
                    break
            if is_new:
                violations.append(
                    {"file": rel, "violation": "IMMUTABLE 级文件被修改或新建——需要人工批准", "severity": "HIGH"}
                )
    return violations
    "find capability violations."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="AI 能力边界静态检查")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--show-scopes", action="store_true", help="只显示 IMMUTABLE 范围")
    args = parser.parse_args()
    if args.show_scopes:
        for scope in get_immutable_scopes():
            print(f"  IMMUTABLE: {scope}")
        return
    matrix = load_matrix()
    if matrix is None:
        print("[CapabilityGuard] ai_capability_matrix.yaml 未找到")
        sys.exit(0)
    print(f'[CapabilityGuard] 能力边界检查 — 矩阵 v{matrix.get('matrix', {}).get('version', '?')}')
    violations = find_capability_violations()
    if violations:
        print(f"\n[CapabilityGuard] ⚠ {len(violations)} 条能力边界违规:")
        for v in violations:
            print(f'  [{v['severity']}] {v['file']} — {v['violation']}')
    else:
        print("[CapabilityGuard] 能力边界 — 全部通过 ✅")
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if violations else 0)
    "入口函数."


if __name__ == "__main__":
    main()
