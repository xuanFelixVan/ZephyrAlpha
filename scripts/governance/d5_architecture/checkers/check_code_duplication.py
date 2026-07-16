# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_code_duplication.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_code_duplication
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
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
import ast
from collections import defaultdict
from difflib import SequenceMatcher

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

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


def similarity_ast(a_path: Path, b_path: Path) -> float:
    """AST 归一化比较——剥离注释/格式差异后 SequenceMatcher 相似度。

    Phase 1 sub-task 3（2026-07-03）：AST 共享行百分比检测。
    parse → unparse 归一化（自动剥离注释/空白/格式差异）→ SequenceMatcher。
    """
    try:
        src_a = a_path.read_text(encoding="utf-8")
        src_b = b_path.read_text(encoding="utf-8")
        norm_a = ast.unparse(ast.parse(src_a))
        norm_b = ast.unparse(ast.parse(src_b))
        return SequenceMatcher(None, norm_a.splitlines(), norm_b.splitlines()).ratio()
    except (OSError, UnicodeDecodeError, SyntaxError):
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check code duplication across packages")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if duplicates found")
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold (default: 0.8)")
    parser.add_argument("--files", nargs="+", default=None, help="只检查指定文件（作为新文件）与已有同名文件的重复（供 file_copy_gate subprocess 调用）")
    parser.add_argument("--ast", action="store_true", help="使用 AST 归一化比较（剥离注释/格式差异，Phase 1 sub-task 3）")
    args = parser.parse_args()

    # === --files mode（Phase 1 sub-task 3）：新文件 vs 已有同名文件 ===
    if args.files:
        new_files = [Path(f) for f in args.files if f.endswith(".py")]
        new_resolved = {f.resolve() for f in new_files if f.exists()}
        # 建立已有 .py 文件的 basename 索引（排除新文件自身 + 排除目录）
        existing_index: dict[str, list[Path]] = defaultdict(list)
        for scan_dir in [REPO_ROOT / "src" / "zephyr", REPO_ROOT / "scripts"]:
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                if py_file.resolve() in new_resolved:
                    continue  # 跳过新文件自身
                if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
                    continue
                existing_index[py_file.name].append(py_file)

        duplicates = []
        for new_file in new_files:
            if not new_file.exists():
                continue
            for existing in existing_index.get(new_file.name, []):
                if args.ast:
                    sim = similarity_ast(new_file, existing)
                else:
                    try:
                        sim = similarity(
                            new_file.read_text(encoding="utf-8"),
                            existing.read_text(encoding="utf-8"),
                        )
                    except (OSError, UnicodeDecodeError):
                        continue
                if sim >= args.threshold:
                    duplicates.append((str(new_file), str(existing), sim))

        if duplicates:
            print(f"FILE COPY DUPLICATIONS: {len(duplicates)}")
            print(f"{'新文件':<55} {'已有文件':<55} {'相似度':>8}")
            print("-" * 120)
            for new_f, exist_f, sim in sorted(duplicates, key=lambda x: -x[2]):
                print(f"{new_f:<55} {exist_f:<55} {sim:>7.1%}")
            if args.warn_only:
                print("WARN: duplications found but --warn-only mode")
                return EXIT_PASS
            return EXIT_FINDINGS

        print("FILE COPY CHECK: CLEAN — no duplications found")
        return EXIT_PASS

    # === 默认模式：跨包同名文件重复检测 ===
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
