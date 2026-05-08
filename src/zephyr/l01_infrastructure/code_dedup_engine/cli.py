"""code-dedup-engine CLI——子命令映射+退出码+扫描入口."""
from __future__ import annotations

import sys
from pathlib import Path

from zephyr.l01_infrastructure.code_dedup_engine.exit_codes import ExitCode
from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
from zephyr.l01_infrastructure.code_dedup_engine.auto_fixer import AutoFixer
from zephyr.l01_infrastructure.code_dedup_engine.report import ReportGenerator


def _collect_py_files(target: str | None) -> list[str]:
    if target:
        p = Path(target)
        if p.is_file():
            return [target]
        if p.is_dir():
            return [str(f) for f in p.rglob("*.py")]
        return []
    src = Path("src")
    scripts = Path("scripts")
    tests = Path("tests")
    files: list[str] = []
    if src.exists():
        files.extend(str(f) for f in src.rglob("*.py"))
    if scripts.exists():
        files.extend(str(f) for f in scripts.rglob("*.py"))
    if tests.exists():
        files.extend(str(f) for f in tests.rglob("*.py"))
    return files


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("--help", "-h"):
        _print_help()
        sys.exit(ExitCode.PASS)

    subcommand = args[0]

    if subcommand == "scan":
        _cmd_scan(args[1:])
    elif subcommand == "fix":
        _cmd_fix(args[1:])
    elif subcommand == "report":
        _cmd_report(args[1:])
    elif subcommand == "verify":
        _cmd_verify(args[1:])
    else:
        print(f"Unknown subcommand: {subcommand}")
        _print_help()
        sys.exit(ExitCode.TOOL_ERROR)


def _print_help() -> None:
    print("code-dedup-engine CLI")
    print("  scan [target]     — 扫描代码重复（可选指定文件/目录）")
    print("  fix [target]      — 自动修复重复（可选指定文件/目录）")
    print("  report [target]   — 生成去重报告")
    print("  verify            — 验证引擎完整性")


def _cmd_scan(args: list[str]) -> None:
    target = args[0] if args else None
    files = _collect_py_files(target)
    if not files:
        print("[SCAN] No Python files found.")
        sys.exit(ExitCode.PASS)
    print(f"[SCAN] Scanning {len(files)} files...")
    scanner = Scanner()
    scanner.scan_files(files)
    duplicates = scanner.find_duplicates()
    if not duplicates:
        print("[SCAN] No duplicates found.")
        sys.exit(ExitCode.PASS)
    print(f"[SCAN] Found {len(duplicates)} duplicate groups.")
    for dup in duplicates:
        print(f"  {dup.group_id}: {len(dup.members)} members, sim={dup.similarity:.3f}")
    sys.exit(ExitCode.WARN)


def _cmd_fix(args: list[str]) -> None:
    target = args[0] if args else None
    files = _collect_py_files(target)
    if not files:
        print("[FIX] No Python files found.")
        sys.exit(ExitCode.PASS)
    print(f"[FIX] Scanning {len(files)} files for duplicates...")
    scanner = Scanner()
    scanner.scan_files(files)
    duplicates = scanner.find_duplicates()
    if not duplicates:
        print("[FIX] No duplicates to fix.")
        sys.exit(ExitCode.PASS)
    fixer = AutoFixer()
    fixed_count = 0
    for dup in duplicates:
        for (src_path, _), (tgt_path, _) in zip(dup.members[::2], dup.members[1::2]):
            if fixer.can_fix(dup.similarity, 0, 0, False):
                result = fixer.fix(src_path, tgt_path, dup.similarity, 0, 0, False)
                if result.get("fixed"):
                    fixed_count += 1
                    print(f"[FIX] Fixed: {src_path} ⇄ {tgt_path}")
    print(f"[FIX] Fixed {fixed_count} duplicates.")
    sys.exit(ExitCode.PASS)


def _cmd_report(args: list[str]) -> None:
    target = args[0] if args else None
    files = _collect_py_files(target)
    if not files:
        print("[REPORT] No Python files found.")
        sys.exit(ExitCode.PASS)
    print(f"[REPORT] Generating report for {len(files)} files...")
    scanner = Scanner()
    scanner.scan_files(files)
    duplicates = scanner.find_duplicates()
    generator = ReportGenerator()
    report = generator.generate(
        duplicates=duplicates,
        files_scanned=len(files),
        target=target or "project",
    )
    print(generator.to_json(report))
    sys.exit(ExitCode.PASS)


def _cmd_verify(args: list[str]) -> None:
    print("[VERIFY] Verifying engine integrity...")
    try:
        from zephyr.l01_infrastructure.code_dedup_engine import __version__
        print(f"[VERIFY] code_dedup_engine v{__version__}")
        scanner = Scanner()
        test_files = list(Path("src/zephyr/l01_infrastructure/code_dedup_engine").glob("*.py"))
        scanner.scan_files([str(f) for f in test_files[:10]])
        scanner.find_duplicates()
        print("[VERIFY] Engine core components operational — GATE_PASSED")
        sys.exit(ExitCode.PASS)
    except ImportError as e:
        print(f"[VERIFY] GATE_ERROR: 引擎导入失败 — {e}")
        sys.exit(ExitCode.TOOL_ERROR)
    except Exception as e:
        print(f"[VERIFY] GATE_ERROR: 引擎验证失败 — {e}")
        sys.exit(ExitCode.TOOL_ERROR)


if __name__ == "__main__":
    main()
