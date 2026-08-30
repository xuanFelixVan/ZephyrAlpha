# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.cli
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.scenario_loader; zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.game_day_runner; zephyr.security.adversarial_validation.game_day_scheduler; zephyr.security.adversarial_validation.convergence_checker; zephyr.security.adversarial_validation.cold_start
# [CONSUMERS] End users; CI/CD; MCP tool wrappers
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] python -m zephyr.security.adversarial_validation is the ONLY entry point; subcommands: run/list/report/status
# [MODIFY-GUARD] Adding subcommands MUST register in main() dispatch
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit on invalid subcommand
# [TESTS] tests/red_blue/test_cli.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: args 参数
#   fields: 参数 args，类型注解 argparse.Namespace
#   code: cli.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run
#   name_en: run
#   intro: run(args) 源码 L111-L135
#   desc: 源码 L111-L135
#   inputs: args
#   outputs: 返回值
# - id: A2
#   name_zh: ② list_scenarios
#   name_en: list_scenarios
#   intro: list_scenarios(args) 源码 L138-L146
#   desc: 源码 L138-L146
#   inputs: args
#   outputs: 返回值
# - id: A3
#   name_zh: ③ report_fn
#   name_en: report_fn
#   intro: report_fn(args) 源码 L149-L159
#   desc: 源码 L149-L159
#   inputs: args
#   outputs: 返回值
# - id: A4
#   name_zh: ④ status
#   name_en: status
#   intro: status(args) 源码 L162-L168
#   desc: 源码 L162-L168
#   inputs: args
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ gameday
#   name_en: gameday
#   intro: gameday(args) 源码 L171-L175
#   desc: 源码 L171-L175
#   inputs: args
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ onboard
#   name_en: onboard
#   intro: onboard(args) 源码 L178-L184
#   desc: 源码 L178-L184
#   inputs: args
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ main
#   name_en: main
#   intro: main() 源码 L196-L236
#   desc: 源码 L196-L236
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: run, list_scenarios, report_fn, status, gameday, onboard, main
#   downstream: End users; CI/CD; MCP tool wrappers
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import argparse
import json
import sys

from zephyr.security.adversarial_validation.cold_start import ColdStart
from zephyr.security.adversarial_validation.game_day_runner import GameDayFrequency, GameDayRunner
from zephyr.security.adversarial_validation.models import AttackTier, BlastRadiusLevel
from zephyr.security.adversarial_validation.scenario_loader import ScenarioLoader
from zephyr.security.adversarial_validation.validator import RedBlueValidator

__all__: list[str] = ["main"]


def run(args: argparse.Namespace) -> None:
    validator = RedBlueValidator()
    tier = None
    if args.tier:
        tier = AttackTier.from_label(args.tier)
    radius = BlastRadiusLevel(args.blast_radius) if args.blast_radius else BlastRadiusLevel.FILE

    report = validator.run_adversarial_session(
        session_name=args.name or "cli-session",
        tier=tier,
        blast_radius=radius,
    )
    print(
        json.dumps(
            {
                "session_id": report.session_id,
                "total": report.total,
                "blocked": report.blocked,
                "bypassed": report.bypassed,
                "blocked_rate": report.blocked_rate,
                "duration_ms": report.duration_ms,
            },
            indent=2,
        )
    )


def list_scenarios(args: argparse.Namespace) -> None:
    loader = ScenarioLoader()
    loader.load()
    scenarios = loader.list_all()
    if args.active_only:
        scenarios = loader.list_active()

    for s in scenarios:
        print(f"  {s.scenario_id:20s} [{s.tier.value:8s}] {s.severity.value:8s} {s.name}")


def report_fn(args: argparse.Namespace) -> None:
    validator = RedBlueValidator()
    report = validator.run_adversarial_session(
        session_name=args.name or "report",
        tier=AttackTier.TIER_1 if not args.tier else AttackTier.from_label(args.tier),
    )
    print(f"Session: {report.session_id}")
    print(f"Total: {report.total}  Blocked: {report.blocked}  Bypassed: {report.bypassed}")
    print(f"Blocked Rate: {report.blocked_rate:.1%}")
    print(f"Duration: {report.duration_ms:.0f}ms")
    print(f"Cleanup: {'OK' if report.cleanup_verified else 'FAILED'}")


def status(args: argparse.Namespace) -> None:
    loader = ScenarioLoader()
    loader.load()
    counts = loader.tier_counts()
    print(f"Scenarios: {loader.scenario_count}")
    for tier, count in sorted(counts.items(), key=lambda x: x[0].name):
        print(f"  {tier.value}: {count}")


def gameday(args: argparse.Namespace) -> None:
    runner = GameDayRunner()
    freq = GameDayFrequency(args.frequency)
    result = runner.run_game_day(freq)
    print(f"GameDay[{freq.value}]: {result.total_attacks} attacks, blocked={result.passed} bypassed={result.bypasses}")


def onboard(args: argparse.Namespace) -> None:
    cs = ColdStart()
    sid = cs.onboard_module(args.module_path)
    if sid:
        print(f"Onboarded: {sid}")
    else:
        print("Already registered")


# Backward-compatible aliases (R5: reverse hierarchy)
_run = run
_list = list_scenarios
_report_fn = report_fn
_status = status
_gameday = gameday
_onboard = onboard


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.security.adversarial_validation",
        description="Red-Blue Adversarial Validator CLI",
    )
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run adversarial session")
    run_p.add_argument("--name", help="Session name")
    run_p.add_argument("--tier", choices=["L1", "L2", "L3", "L4", "L5", "L6", "L7"], help="Attack tier")
    run_p.add_argument("--blast-radius", choices=["FILE", "MODULE", "CROSS_MODULE", "SYSTEM"])

    list_p = sub.add_parser("list", help="List scenarios")
    list_p.add_argument("--active-only", action="store_true")

    report_p = sub.add_parser("report", help="Generate report")
    report_p.add_argument("--name")
    report_p.add_argument("--tier")

    sub.add_parser("status", help="Show scenario counts")

    gd_p = sub.add_parser("gameday", help="Run game day")
    gd_p.add_argument("--frequency", choices=["per_commit", "daily", "weekly", "monthly"], default="per_commit")

    ob_p = sub.add_parser("onboard", help="Onboard new module")
    ob_p.add_argument("module_path")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "run": run,
        "list": list_scenarios,
        "report": report_fn,
        "status": status,
        "gameday": gameday,
        "onboard": onboard,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
