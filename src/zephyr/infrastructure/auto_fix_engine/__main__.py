# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §4.5
# [MODULE] zephyr.infrastructure.auto_fix_engine.__main__
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] CLI用户;CI/CD pipeline
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] CLI MUST可用;子命令MUST返回正确退出码
# [MODIFY-GUARD] blueprint.md §4.5
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CLIError
# [TESTS] tests/auto-fix-engine/test_cli.py
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: args 参数
#   fields: 参数 args，类型注解 argparse.Namespace
#   code: __main__.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① cmd_fix
#   name_en: cmd_fix
#   intro: cmd_fix(args) 源码 L94-L106
#   desc: 源码 L94-L106
#   inputs: args
#   outputs: int
# - id: A2
#   name_zh: ② cmd_scan
#   name_en: cmd_scan
#   intro: cmd_scan(args) 源码 L109-L119
#   desc: 源码 L109-L119
#   inputs: args
#   outputs: int
# - id: A3
#   name_zh: ③ cmd_health
#   name_en: cmd_health
#   intro: cmd_health(args) 源码 L122-L136
#   desc: 源码 L122-L136
#   inputs: args
#   outputs: int
# - id: A4
#   name_zh: ④ cmd_report
#   name_en: cmd_report
#   intro: cmd_report(args) 源码 L139-L149
#   desc: 源码 L139-L149
#   inputs: args
#   outputs: int
# - id: A5
#   name_zh: ⑤ main
#   name_en: main
#   intro: main() 源码 L152-L183
#   desc: 源码 L152-L183
#   inputs: 无参数
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: CLI用户;CI/CD pipeline
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def _get_engine() -> object:
    from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

    return AutoFixEngine()


def cmd_fix(args: argparse.Namespace) -> int:
    engine = _get_engine()
    result = engine.fix(args.action_type, args.target, dry_run=args.dry_run)
    output = {
        "action_id": result.action_id,
        "action_type": result.action_type,
        "status": result.status.value,
        "target": result.target,
        "confidence": result.confidence.value,
        "metadata": result.metadata,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if result.status.value in ("completed", "pending") else 1


def cmd_scan(args: argparse.Namespace) -> int:
    engine = _get_engine()
    findings: list[dict[str, Any]] = []
    for name, fixer in engine._fixers.items():
        try:
            scan_results = fixer.scan()
            findings.extend(scan_results)
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            findings.append({"fixer": name, "error": str(exc)})
    print(json.dumps({"total": len(findings), "findings": findings[:100]}, indent=2, ensure_ascii=False))
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    engine = _get_engine()
    report = engine.health_check()
    output = {
        "healthy": report.healthy,
        "fixers": report.fixers,
        "budget_ok": report.budget_ok,
        "cascade_active": report.cascade_active,
        "dead_letter_count": report.dead_letter_count,
        "approval_queue_size": report.approval_queue_size,
        "db_accessible": report.db_accessible,
        "config_loaded": report.config_loaded,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if report.healthy else 1


def cmd_report(args: argparse.Namespace) -> int:
    engine = _get_engine()
    report_gen = engine._report_generator
    history = report_gen.get_history(limit=args.limit)
    if not history:
        print(json.dumps({"message": "No fix history available"}, indent=2))
        return 0
    latest = history[-1]
    summary = report_gen.generate_summary(latest)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.infrastructure.auto_fix_engine",
        description="Auto Fix Engine CLI — MOD-INF-031",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    fix_parser = subparsers.add_parser("fix", help="Execute a single fix")
    fix_parser.add_argument("--action-type", required=True, help="Fix action type")
    fix_parser.add_argument("--target", required=True, help="Target file/path")
    fix_parser.add_argument("--dry-run", action="store_true", help="Preview only")

    scan_parser = subparsers.add_parser("scan", help="Scan for fixable issues")
    scan_parser.add_argument("--scope", default="", help="Scan scope")

    health_parser = subparsers.add_parser("health", help="Health check")

    report_parser = subparsers.add_parser("report", help="View fix report")
    report_parser.add_argument("--limit", type=int, default=5, help="Number of reports")

    args = parser.parse_args()
    if args.command == "fix":
        return cmd_fix(args)
    elif args.command == "scan":
        return cmd_scan(args)
    elif args.command == "health":
        return cmd_health(args)
    elif args.command == "report":
        return cmd_report(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
