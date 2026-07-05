# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §4.1
# [MODULE] zephyr.security.access_control.orphan_judge.__main__
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] python -m zephyr.security.access_control.orphan_judge; audit-orchestrator.cli
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] CLI是orphan_judge的唯一入口; judge/scan/report三条子命令
# [MODIFY-GUARD] 新增子命令必须注册到__init__.py __all__; 修改参数必须同步blueprint.md §4.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1) on FileNotFound/invalid subcommand; exit 0 on success
# [TESTS] tests/orphan-judge/test_main.py
# [A_module] module_id=MOD-SEC___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

__all__: list[str] = ["main"]


def _cmd_judge(args: argparse.Namespace) -> int:
    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

    path = args.path
    if not Path(path).exists():
        print(json.dumps({"error": f"File not found: {path}"}, indent=2))
        return 1

    judge = OrphanJudge(jsonl_output=args.jsonl)
    result = judge.judge(path, dry_run=args.dry_run)
    output = {
        "path": result.path,
        "verdict": result.verdict.value,
        "confidence": result.confidence.value,
        "reason": result.reason,
        "layers": [{"layer": l.layer, "passed": l.passed, "detail": l.detail} for l in result.layers],
    }
    print(json.dumps(output, indent=2, default=str))
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

    root = Path(args.directory)
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {args.directory}"}, indent=2))
        return 1

    py_files = sorted(root.rglob("*.py"))
    if args.limit:
        py_files = py_files[: args.limit]

    judge = OrphanJudge(jsonl_output=args.jsonl)
    results = []
    for fpath in py_files:
        rel_path = str(fpath).replace("\\", "/")
        try:
            result = judge.judge(rel_path, dry_run=args.dry_run)
            results.append(
                {
                    "path": rel_path,
                    "verdict": result.verdict.value,
                    "confidence": result.confidence.value,
                    "reason": result.reason,
                }
            )
        except Exception as exc:
            results.append({"path": rel_path, "error": str(exc)})

    summary = {}
    for r in results:
        v = r.get("verdict", "ERROR")
        summary[v] = summary.get(v, 0) + 1

    print(json.dumps({"total": len(results), "summary": summary, "results": results}, indent=2, default=str))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

    root = Path(args.directory)
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {args.directory}"}, indent=2))
        return 1

    py_files = sorted(root.rglob("*.py"))
    judge = OrphanJudge()
    results = []
    for fpath in py_files:
        rel_path = str(fpath).replace("\\", "/")
        try:
            result = judge.judge(rel_path, dry_run=args.dry_run)
            results.append(
                {
                    "path": rel_path,
                    "verdict": result.verdict.value,
                    "confidence": result.confidence.value,
                    "reason": result.reason,
                }
            )
        except Exception as exc:
            results.append({"path": rel_path, "error": str(exc)})

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    elif args.format == "csv":
        print("path,verdict,confidence,reason")
        for r in results:
            print(
                f'{r.get("path", "")},{r.get("verdict", "ERROR")},{r.get("confidence", "unknown")},"{r.get("reason", r.get("error", ""))}"'
            )
    elif args.format == "markdown":
        print("| 文件 | 判决 | 置信度 | 原因 |")
        print("|------|------|--------|------|")
        for r in results:
            print(
                f"| {r.get('path', '')} | {r.get('verdict', 'ERROR')} | {r.get('confidence', 'unknown')} | {r.get('reason', r.get('error', ''))} |"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="orphan-judge", description="Orphan Judge — 孤儿文件五层判定引擎")
    sub = parser.add_subparsers(dest="subcommand")

    p_judge = sub.add_parser("judge", help="单文件判定")
    p_judge.add_argument("path", help="目标文件路径")
    p_judge.add_argument("--dry-run", action="store_true", default=True, help="仅判定不执行(默认)")
    p_judge.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="执行处置")
    p_judge.add_argument("--jsonl", action="store_true", help="JSONL格式输出")

    p_scan = sub.add_parser("scan", help="批量扫描目录")
    p_scan.add_argument("directory", help="目标目录")
    p_scan.add_argument("--dry-run", action="store_true", default=True)
    p_scan.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    p_scan.add_argument("--jsonl", action="store_true")
    p_scan.add_argument("--limit", type=int, help="限制扫描文件数")

    p_report = sub.add_parser("report", help="生成报告")
    p_report.add_argument("directory", help="目标目录")
    p_report.add_argument("--dry-run", action="store_true", default=True)
    p_report.add_argument("--format", choices=["json", "csv", "markdown"], default="json", help="输出格式")

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        return 1

    if args.subcommand == "judge":
        return _cmd_judge(args)
    elif args.subcommand == "scan":
        return _cmd_scan(args)
    elif args.subcommand == "report":
        return _cmd_report(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
