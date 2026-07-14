# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/detect_temp_files.py | §
# [MODULE] scripts.governance.d1_structure.detect_temp_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
# [TTL] task_bound
from __future__ import annotations

"""
[BLUEPRINT] DOM-GOV-001 | D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md | S3
[MODULE] scripts.governance.d1_structure.detect_temp_files
[INVARIANTS] temp files must all be detected
[MODIFY-GUARD] __init__.py;script_manifest.yaml
[CONSUMERS] CI pipeline;governance gate
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] sys.exit(1)
[TESTS] tests/governance/test_d1_structure.py
"""

"""
detect_temp_files.py — 临时文件检测与清理

exit codes: 0=pass, 1=findings, 2=error
"""

__manifest__ = """
args: []
description: 临时文件检测（GOV-TASK-005 §4.2 — temp_*/tmp_*/*.backup/__pycache__）
dimensions:
- D1
priority: P0
timeout_seconds: 30
warn_only: false
"""


import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

TEMP_FILE_PATTERNS = [
    (re.compile(r"^temp_"), "temp_ 前缀临时文件"),
    (re.compile(r"^tmp_"), "tmp_ 前缀临时文件"),
    (re.compile(r"^_tmp_"), "_tmp_ 前缀临时脚本"),
    (re.compile(r"^_debug_"), "_debug_ 前缀调试测试"),
    (re.compile(r"\.backup$"), ".backup 后缀备份文件"),
    # -vN./-roundN. 仅匹配代码/配置文件扩展名，避免误判知识库条目（如 ke-1337-v1.md，-v1 是合法版本号）
    (re.compile(r"-v\d+\.(py|sh|ps1|yaml|yml|json|toml)$"), "-vN 版本后缀文件"),
    (re.compile(r"-round\d+\.(py|sh|ps1|yaml|yml|json|toml)$"), "-roundN 版本后缀文件"),
    (re.compile(r"\.pyc$"), ".pyc 编译缓存文件"),
    (re.compile(r"\.bak$"), ".bak 备份文件"),
    (re.compile(r"\.baseline"), ".baseline 基线备份文件"),
    (re.compile(r"\.orig$"), ".orig 合并残留文件"),
    (re.compile(r"\.swp$"), ".swp Vim 交换文件"),
    (re.compile(r"~$"), "~ 编辑器备份文件"),
]

TEMP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def scan_temp_files(scan_dir: Path | None = None) -> tuple[list[dict], int]:
    """扫描临时文件与缓存目录，返回 (发现列表, 已扫描文件数)。"""
    if scan_dir is None:
        scan_dir = REPO_ROOT

    findings = []
    files_scanned = 0

    # 收集临时目录：用 os.walk + prune 替代 rglob（避免遍历 .git 等大目录导致超时）。
    # 注意：__pycache__/.pytest_cache 等自身也在 EXCLUDE_DIRS 中，
    # 必须在 prune 之前收集它们（prune 之后这些目录就不进入下一层了，但当前层仍可见）。
    for dirpath, dirnames, _filenames in os.walk(scan_dir):
        for d in dirnames:
            if d in TEMP_DIR_NAMES:
                full = Path(dirpath) / d
                try:
                    rel = str(full.relative_to(REPO_ROOT)).replace("\\", "/")
                except ValueError:
                    continue
                findings.append(
                    {
                        "file": rel,
                        "type": "临时目录",
                        "detail": f"{d}/ 目录",
                        "severity": "MEDIUM",
                    }
                )
        # prune：跳过 EXCLUDE_DIRS 与所有 . 开头目录的深入遍历
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]

    for filepath in iter_files(scan_dir):
        files_scanned += 1

        try:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            continue

        for pattern, label in TEMP_FILE_PATTERNS:
            if pattern.search(filepath.name):
                findings.append(
                    {
                        "file": rel,
                        "type": "临时文件",
                        "detail": label,
                        "severity": "MEDIUM",
                    }
                )
                break

    return findings, files_scanned


def clean_temp_files(scan_dir: Path | None = None, dry_run: bool = True) -> tuple[list[str], int]:
    """清理临时文件与缓存目录，返回 (已清理列表, 已扫描文件数)。"""
    if scan_dir is None:
        scan_dir = REPO_ROOT

    cleaned: list[str] = []
    files_scanned = 0

    # 收集要清理的临时目录：os.walk + prune（与 scan_temp_files 一致，避免遍历 .git）
    for dirpath, dirnames, _filenames in os.walk(scan_dir):
        for d in dirnames:
            if d in TEMP_DIR_NAMES:
                full = Path(dirpath) / d
                try:
                    rel = str(full.relative_to(REPO_ROOT)).replace("\\", "/")
                except ValueError:
                    continue
                if dry_run:
                    cleaned.append(f"[DRY] {rel}/")
                else:
                    import shutil

                    shutil.rmtree(full, ignore_errors=True)
                    cleaned.append(f"[DEL] {rel}/")
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]

    for filepath in iter_files(scan_dir):
        files_scanned += 1
        try:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            continue
        for pattern, label in TEMP_FILE_PATTERNS:
            if pattern.search(filepath.name):
                if dry_run:
                    cleaned.append(f"[DRY] {rel}")
                else:
                    try:
                        filepath.unlink(missing_ok=True)
                        cleaned.append(f"[DEL] {rel}")
                    except OSError:
                        cleaned.append(f"[ERR] {rel}")
                break

    return cleaned, files_scanned


def main() -> None:
    parser = argparse.ArgumentParser(description="临时文件检测与清理（GOV-TASK-005 §4.2）")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    parser.add_argument("--clean", action="store_true", help="清理模式（删除检测到的临时文件）")
    parser.add_argument("--dry-run", action="store_true", help="模拟清理（不实际删除）")
    args = parser.parse_args()

    scan_dir = Path(args.scan_dir) if args.scan_dir else None

    if args.clean or args.dry_run:
        cleaned, files_scanned = clean_temp_files(scan_dir, dry_run=args.dry_run or False)
        if cleaned:
            print(f"\n[TEMP-CLEAN] {len(cleaned)} 项（扫描 {files_scanned} 文件）:")
            for c in cleaned:
                print(f"  {c}")
        else:
            print(f"[TEMP-CLEAN] 无临时文件（扫描 {files_scanned} 文件）")
        sys.exit(EXIT_PASS)

    findings, files_scanned = scan_temp_files(scan_dir)

    if findings:
        print(f"\n[TEMP-FILES] {len(findings)} 个临时文件/目录（扫描 {files_scanned} 文件）:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print(f"[TEMP-FILES] 无临时文件（扫描 {files_scanned} 文件）", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
