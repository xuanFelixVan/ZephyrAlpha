# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_code_duplication.py | §
"""
[BLUEPRINT] MOD-INF-005 | 03_modules/l01_infrastructure/governance-automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_code_duplication
[INVARIANTS] 扫描 src/zephyr/ 下所有包; 检测跨包同名文件代码重复
[MODIFY-GUARD] script_manifest.yaml
[CONSUMERS] CI pipeline; AI session 冷启动
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=DUPLICATES, exit 2=ERROR
[TESTS] tests/governance/test_check_code_duplication.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()

import argparse
from difflib import SequenceMatcher

from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR, REPO_ROOT

__manifest__ = """
args: [--warn-only, --threshold]
description: 跨包代码重复检测——检测两个包中是否存在同名同功能的文件
dimensions:
- D5
priority: P2
timeout_seconds: 120
warn_only: false
"""

SRC_DIR = REPO_ROOT / "src" / "zephyr"


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.splitlines(), b.splitlines()).ratio()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check code duplication across packages")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if duplicates found")
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold (default: 0.8)")
    args = parser.parse_args()

    if not SRC_DIR.exists():
        print("ERROR: src/zephyr/ not found")
        return EXIT_ERROR

    packages: dict[str, dict[str, str]] = {}
    for pkg_dir in sorted(SRC_DIR.iterdir()):
        if pkg_dir.is_dir() and not pkg_dir.name.startswith("_"):
            files: dict[str, str] = {}
            for py_file in pkg_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8")
                    files[py_file.name] = content
                except Exception:
                    pass
            if files:
                packages[pkg_dir.name] = files

    duplicates = []
    pkg_names = sorted(packages.keys())
    for i in range(len(pkg_names)):
        for j in range(i + 1, len(pkg_names)):
            pkg_a, pkg_b = pkg_names[i], pkg_names[j]
            common_files = set(packages[pkg_a].keys()) & set(packages[pkg_b].keys())
            for fname in common_files:
                sim = similarity(packages[pkg_a][fname], packages[pkg_b][fname])
                if sim >= args.threshold:
                    duplicates.append((pkg_a, pkg_b, fname, sim))

    if duplicates:
        print(f"CODE DUPLICATIONS: {len(duplicates)}")
        print(f"{'包A':<30} {'包B':<30} {'文件':<30} {'相似度':>8}")
        print("-" * 100)
        for a, b, fname, sim in sorted(duplicates, key=lambda x: -x[3]):
            print(f"{a:<30} {b:<30} {fname:<30} {sim:>7.1%}")
        if args.warn_only:
            print("WARN: duplications found but --warn-only mode")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("CODE DUPLICATION CHECK: CLEAN — no duplications found")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
