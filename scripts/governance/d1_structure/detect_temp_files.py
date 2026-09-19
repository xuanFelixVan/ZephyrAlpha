# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/detect_temp_files.py | §
# [MODULE] scripts.governance.d1_structure.detect_temp_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Module docstring — see module-level docstring for details."""

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
[ERROR_CONTRACT] sys.exit(EXIT_FINDINGS)
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

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files, rel_for_display, resolve_scan_dir, tracked_files_set, zero_scan_error

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
    # 裁定#345b（2026-09-19 W1-B）：补 4 类常见临时件模式。
    # 收紧无存量代价：tracked 面命中实测=0（git ls-files | grep -cE '\.tmp$|^_probe_|^commit_msg|^pytest_' = 0），
    # 全盘面命中均为 untracked/gitignored 假债（原子写残留 .tmp / commit_msg 草稿）。
    (re.compile(r"\.tmp$"), ".tmp 后缀临时文件"),
    (re.compile(r"^_probe_"), "_probe_ 前缀探针脚本"),
    (re.compile(r"^commit_msg"), "commit_msg 提交信息草稿"),
    (re.compile(r"^pytest_"), "pytest_ 前缀临时输出"),
    (re.compile(r"~$"), "~ 编辑器备份文件"),
]

TEMP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def scan_temp_files(
    scan_dir: Path | None = None, tracked_set: set[str] | None = None
) -> tuple[list[dict], int]:
    """扫描临时文件与缓存目录，返回 (发现列表, 已扫描文件数)。

    治本（2026-09-19 CF1 F2）：入参先 resolve() 归一为绝对路径，展示路径改走
    rel_for_display()——原实现 `relative_to(REPO_ROOT)` 失败即 continue，
    传相对 --scan-dir 时所有发现被静默丢弃，而 files_scanned 照常计数，
    报"扫了 N 文件 / 无临时文件 / exit 0"＝恒绿假通过。

    裁定#345a（2026-09-19 W1-B）：tracked_set 非 None 时扫描面过滤为 git
    跟踪文件交集（tracked ⊆ 全盘）——.gitignore 白名单模型下"扫得到但提交
    不了"的文件是结构性假债，tracked 口径红数才真实可提交面债务。
    TEMP_DIR_NAMES（__pycache__/.pytest_cache 等）均为 gitignored 构建产物、
    跟踪面恒不含，tracked 口径下目录类发现整类不计。
    tracked_set=None = 现行为零变化（默认关闭）。
    """
    scan_dir = resolve_scan_dir(scan_dir) or REPO_ROOT

    findings = []
    files_scanned = 0

    # 收集临时目录：用 os.walk + prune 替代 rglob（避免遍历 .git 等大目录导致超时）。
    # 注意：__pycache__/.pytest_cache 等自身也在 EXCLUDE_DIRS 中，
    # 必须在 prune 之前收集它们（prune 之后这些目录就不进入下一层了，但当前层仍可见）。
    for dirpath, dirnames, _filenames in os.walk(scan_dir):
        for d in dirnames:
            if d in TEMP_DIR_NAMES:
                if tracked_set is not None:
                    continue  # --tracked-only：目录类发现不计入跟踪面口径（裁定#345a）
                full = Path(dirpath) / d
                rel = rel_for_display(full)
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
        rel = rel_for_display(filepath)
        if tracked_set is not None and rel not in tracked_set:
            continue  # --tracked-only：扫描面过滤为 git 跟踪文件交集（裁定#345a）
        files_scanned += 1

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


def clean_temp_files(
    scan_dir: Path | None = None, dry_run: bool = True, tracked_set: set[str] | None = None
) -> tuple[list[str], int]:
    """清理临时文件与缓存目录，返回 (已清理列表, 已扫描文件数)。

    治本口径与 scan_temp_files 一致：入参 resolve()、展示路径不丢发现。
    裁定#345a：tracked_set 非 None 时扫描面过滤为 git 跟踪文件交集（与
    scan_temp_files 同口径）；None = 现行为零变化。
    """
    scan_dir = resolve_scan_dir(scan_dir) or REPO_ROOT

    cleaned: list[str] = []
    files_scanned = 0

    # 收集要清理的临时目录：os.walk + prune（与 scan_temp_files 一致，避免遍历 .git）
    for dirpath, dirnames, _filenames in os.walk(scan_dir):
        for d in dirnames:
            if d in TEMP_DIR_NAMES:
                if tracked_set is not None:
                    continue  # --tracked-only：目录类不计入跟踪面口径（裁定#345a）
                full = Path(dirpath) / d
                rel = rel_for_display(full)
                if dry_run:
                    cleaned.append(f"[DRY] {rel}/")
                else:
                    import shutil

                    shutil.rmtree(full, ignore_errors=True)  # ops-guard-exempt: 存量非新增，显式 --clean 人工指令路径
                    cleaned.append(f"[DEL] {rel}/")
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]

    for filepath in iter_files(scan_dir):
        rel = rel_for_display(filepath)
        if tracked_set is not None and rel not in tracked_set:
            continue  # --tracked-only：扫描面过滤为 git 跟踪文件交集（裁定#345a）
        files_scanned += 1
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
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="临时文件检测与清理（GOV-TASK-005 §4.2）")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    parser.add_argument("--clean", action="store_true", help="清理模式（删除检测到的临时文件）")
    parser.add_argument("--dry-run", action="store_true", help="模拟清理（不实际删除）")
    # 裁定#345a（2026-09-19 W1-B）：opt-in 口径旗标，默认关闭=现行为零变化
    parser.add_argument(
        "--tracked-only",
        action="store_true",
        help="扫描面过滤为 git ls-files 跟踪文件交集（tracked ⊆ 全盘；git 不可用时降级全盘并告警）",
    )
    args = parser.parse_args()

    scan_dir = resolve_scan_dir(args.scan_dir)

    tracked_set: set[str] | None = None
    if args.tracked_only:
        tracked_set = tracked_files_set()
        if tracked_set is None:
            # 调用方契约（tracked_files_set）：git 失败禁止当空集合滤没全部文件（假绿），
            # 降级全盘口径并出声（与 check_directory_contract.scan_all 降级口径一致）
            print("[TEMP-FILES] WARN: git 不可用，--tracked-only 降级为全盘口径", file=sys.stderr)
            tracked_set = None
        else:
            print(f"[TEMP-FILES] --tracked-only: git 跟踪面 {len(tracked_set)} 文件", file=sys.stderr)

    if args.clean or args.dry_run:
        cleaned, files_scanned = clean_temp_files(scan_dir, dry_run=args.dry_run or False, tracked_set=tracked_set)
        err = zero_scan_error(scan_dir, files_scanned, "TEMP-CLEAN", len(cleaned))
        if err:
            print(err, file=sys.stderr)
            sys.exit(EXIT_ERROR)
        if cleaned:
            print(f"\n[TEMP-CLEAN] {len(cleaned)} 项（扫描 {files_scanned} 文件）:")
            for c in cleaned:
                print(f"  {c}")
        else:
            print(f"[TEMP-CLEAN] 无临时文件（扫描 {files_scanned} 文件）")
        sys.exit(EXIT_PASS)

    findings, files_scanned = scan_temp_files(scan_dir, tracked_set=tracked_set)

    # 治本（2026-09-19 CF1 F2）：显式传了目录却 0 文件进入统计＝入参口径失效，
    # 报 error 退出而不是"无临时文件"exit 0（否则打错路径/目录不在仓内即假绿）。
    err = zero_scan_error(scan_dir, files_scanned, "TEMP-FILES", len(findings))
    if err:
        print(err, file=sys.stderr)
        sys.exit(EXIT_ERROR)

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
