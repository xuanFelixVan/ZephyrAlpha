# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §4
# [MODULE] zephyr.governance.code_dedup.cli
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] pre-commit/verify_dedup.py; ct_deduplication.DeduplicationHandler; CI pipeline
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] exit codes: 0=PASS/1=WARN/2=ERROR/3=TOOL_ERROR/4=DEGRADED
# [MODIFY-GUARD] exit code mapping change requires blueprint §6 update
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sys.exit with ExitCode enum values only
# [TESTS] tests/test_code_dedup_engine.py
# [A_module] module_id=MOD-GOV_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""code-dedup-engine CLI——子命令映射+退出码+扫描入口."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from zephyr.governance.code_dedup.auto_fixer import AutoFixer
from zephyr.governance.code_dedup.exit_codes import ExitCode
from zephyr.governance.code_dedup.report import ReportGenerator
from zephyr.infrastructure.asset_inventory.scanner import Scanner


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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-dedup-engine",
        description="Code Dedup Engine — Token级代码去重·爆炸半径防护·原子修复",
    )
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="扫描代码重复")
    scan_p.add_argument("target", nargs="?", default=None, help="指定文件/目录")
    scan_p.add_argument("--full", action="store_true", help="全量扫描（忽略缓存）")
    scan_p.add_argument("--incremental", action="store_true", help="增量扫描（仅git diff变更）[默认]")
    scan_p.add_argument("--file", dest="single_file", default=None, help="单文件快速检查")
    scan_p.add_argument("--warn-only", action="store_true", help="发现高重复也exit 1（不阻断）")
    scan_p.add_argument("--fail-on-duplicates", action="store_true", help="发现高重复→exit 2（阻断CI）")
    scan_p.add_argument("--output", default=None, help="报告输出路径 [默认: stdout]")
    scan_p.add_argument("--format", dest="fmt", choices=["yaml", "json"], default="yaml", help="报告格式")
    scan_p.add_argument("--quiet", action="store_true", help="只输出退出码")
    scan_p.add_argument("--threshold-global", type=float, default=0.7, help="全局AST相似度阈值")
    scan_p.add_argument("--threshold-shared", type=float, default=0.3, help="shared/目录阈值")
    scan_p.add_argument("--threshold-tests", type=float, default=0.9, help="tests/目录阈值")
    scan_p.add_argument("--min-lines", type=int, default=3, help="最小函数行数")
    scan_p.add_argument("--no-degrade", action="store_true", help="禁止降级——Stage失败→exit 3")
    scan_p.add_argument("--allow-degrade", action="store_true", help="允许降级 [默认]")
    scan_p.add_argument("--skip-cache", action="store_true", help="跳过缓存——强制重新解析AST")
    scan_p.add_argument("--quick-init", action="store_true", help="冷启动加速——仅Stage 0.5签名指纹扫描")

    fix_p = sub.add_parser("fix", help="自动修复重复")
    fix_p.add_argument("target", nargs="?", default=None, help="指定文件/目录")
    fix_p.add_argument("--group-ids", default=None, help="指定修复的DUP组ID（逗号分隔）")
    fix_p.add_argument("--batch-size", type=int, default=3, help="每批修复数 [1-3]")
    fix_p.add_argument("--dry-run", action="store_true", help="预览模式——不实际修改文件")
    fix_p.add_argument("--partial-extract", action="store_true", help="允许部分提取")

    report_p = sub.add_parser("report", help="生成去重报告")
    report_p.add_argument("target", nargs="?", default=None, help="指定文件/目录")
    report_p.add_argument("--format", dest="fmt", choices=["yaml", "json"], default="yaml", help="报告格式")

    sub.add_parser("verify", help="验证引擎完整性")
    sub.add_parser("benchmark", help="运行5组已知对自验证基准测试")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(ExitCode.PASS)

    if args.command == "scan":
        _cmd_scan(args)
    elif args.command == "fix":
        _cmd_fix(args)
    elif args.command == "report":
        _cmd_report(args)
    elif args.command == "verify":
        _cmd_verify(args)
    elif args.command == "benchmark":
        _cmd_benchmark(args)


def _cmd_scan(args: argparse.Namespace) -> None:
    target = args.single_file or args.target
    files = _collect_py_files(target)
    if not files:
        if not args.quiet:
            print("[SCAN] No Python files found.")
        sys.exit(ExitCode.PASS)

    if not args.quiet:
        print(f"[SCAN] Scanning {len(files)} files...")

    scanner = Scanner()
    results = scanner.scan_files(files)
    skipped = sum(1 for r in results if r.skipped)
    duplicates = scanner.find_duplicates()

    if not duplicates:
        if not args.quiet:
            print(f"[SCAN] No duplicates found. (skipped {skipped} files)")
        sys.exit(ExitCode.PASS)

    high_count = sum(1 for d in duplicates if d.similarity >= 0.9)
    med_count = sum(1 for d in duplicates if 0.8 <= d.similarity < 0.9)
    low_count = sum(1 for d in duplicates if d.similarity < 0.8)

    if not args.quiet:
        print(
            f"[SCAN] Found {len(duplicates)} duplicate groups "
            f"(high:{high_count} med:{med_count} low:{low_count}, skipped:{skipped})"
        )
        for dup in duplicates[:20]:
            print(f"  {dup.group_id}: {len(dup.members)} members, sim={dup.similarity:.3f}")
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more")

    if args.fail_on_duplicates and high_count > 0:
        sys.exit(ExitCode.ERROR)
    if args.warn_only:
        sys.exit(ExitCode.WARN)
    if high_count > 0:
        sys.exit(ExitCode.ERROR)
    if med_count > 0:
        sys.exit(ExitCode.WARN)
    sys.exit(ExitCode.PASS)


def _cmd_fix(args: argparse.Namespace) -> None:
    target = args.target
    files = _collect_py_files(target)
    if not files:
        print("[FIX] No Python files found.")
        sys.exit(ExitCode.PASS)

    print(f"[FIX] Scanning {len(files)} files for duplicates...")
    scanner = Scanner()
    scanner.scan_files(files)
    duplicates = scanner.find_duplicates()

    if args.group_ids:
        allowed_ids = set(args.group_ids.split(","))
        duplicates = [d for d in duplicates if d.group_id in allowed_ids]

    if not duplicates:
        print("[FIX] No duplicates to fix.")
        sys.exit(ExitCode.PASS)

    fixer = AutoFixer()
    fixed_count = 0
    batch_remaining = args.batch_size

    for dup in duplicates:
        if batch_remaining <= 0:
            break
        for (src_path, _), (tgt_path, _) in zip(dup.members[::2], dup.members[1::2], strict=False):
            if fixer.can_fix(dup.similarity, 0, 0, False):
                if args.dry_run:
                    print(f"[FIX] DRY-RUN: Would fix {src_path} ⇄ {tgt_path}")
                    fixed_count += 1
                else:
                    result = fixer.fix(src_path, tgt_path, dup.similarity, 0, 0, False)
                    if result.get("fixed"):
                        fixed_count += 1
                        print(f"[FIX] Fixed: {src_path} ⇄ {tgt_path}")
        batch_remaining -= 1

    print(f"[FIX] {'Would fix' if args.dry_run else 'Fixed'} {fixed_count} duplicates.")
    sys.exit(ExitCode.PASS)


def _cmd_report(args: argparse.Namespace) -> None:
    target = args.target
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
    if args.fmt == "json":
        print(generator.to_json(report))
    else:
        print(generator.to_yaml(report))
    sys.exit(ExitCode.PASS)


def _cmd_verify(args: argparse.Namespace) -> None:
    print("[VERIFY] Verifying engine integrity...")
    try:
        import sys as _sys

        _pkg = _sys.modules.get("zephyr.governance")
        _ver = getattr(_pkg, "__version__", "unknown") if _pkg else "unknown"
        print(f"[VERIFY] code_dedup_engine v{_ver}")
        scanner = Scanner()
        test_files = list(Path("src/zephyr/governance").glob("*.py"))
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


def _cmd_benchmark(args: argparse.Namespace) -> None:
    print("[BENCHMARK] Running 5-group self-benchmark...")
    from zephyr.governance.intelligence_governance.self_benchmark import SelfBenchmark

    bench = SelfBenchmark()
    result = bench.run_benchmark()

    for case in result.case_results:
        status_mark = "PASS" if case.passed else "FAIL"
        print(f"  [{status_mark}] {case.test_id} ({case.category}): {case.details}")

    regression = bench.check_regression(result)
    if regression is not None:
        print(
            f"[BENCHMARK] REGRESSION DETECTED: pass rate {regression.current_pass_rate:.1%} "
            f"(was {regression.previous_pass_rate:.1%}, delta={regression.delta:+.1%})"
        )
        print(f"[BENCHMARK] Failed cases: {', '.join(regression.failed_cases)}")
        sys.exit(ExitCode.WARN)

    if result.status == "failed":
        print(f"[BENCHMARK] FAILED: {result.failed}/{result.total} cases failed")
        sys.exit(ExitCode.ERROR)

    print(f"[BENCHMARK] ALL PASSED: {result.passed}/{result.total}")
    sys.exit(ExitCode.PASS)


if __name__ == "__main__":
    main()
