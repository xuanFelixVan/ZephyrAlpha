# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.cli
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.scenario_loader; zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.game_day_runner; zephyr.security.adversarial_validation.game_day_scheduler; zephyr.security.adversarial_validation.convergence_checker; zephyr.security.adversarial_validation.cold_start
# [CONSUMERS] End users; CI/CD; MCP tool wrappers
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] python -m zephyr.security.adversarial_validation is the ONLY entry point; subcommands: run/list/report/status
# [MODIFY-GUARD] Adding subcommands MUST register in main() dispatch
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit on invalid subcommand
# [TESTS] tests/red_blue/test_cli.py
# [A_module] module_id=MOD-SEC_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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


def _run(args: argparse.Namespace) -> None:
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


def _list(args: argparse.Namespace) -> None:
    loader = ScenarioLoader()
    loader.load()
    scenarios = loader.list_all()
    if args.active_only:
        scenarios = loader.list_active()

    for s in scenarios:
        print(f"  {s.scenario_id:20s} [{s.tier.value:8s}] {s.severity.value:8s} {s.name}")


def _report_fn(args: argparse.Namespace) -> None:
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


def _status(args: argparse.Namespace) -> None:
    loader = ScenarioLoader()
    loader.load()
    counts = loader.tier_counts()
    print(f"Scenarios: {loader.scenario_count}")
    for tier, count in sorted(counts.items(), key=lambda x: x[0].name):
        print(f"  {tier.value}: {count}")


def _gameday(args: argparse.Namespace) -> None:
    runner = GameDayRunner()
    freq = GameDayFrequency(args.frequency)
    result = runner.run_game_day(freq)
    print(f"GameDay[{freq.value}]: {result.total_attacks} attacks, blocked={result.passed} bypassed={result.bypasses}")


def _onboard(args: argparse.Namespace) -> None:
    cs = ColdStart()
    sid = cs.onboard_module(args.module_path)
    if sid:
        print(f"Onboarded: {sid}")
    else:
        print("Already registered")


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
        "run": _run,
        "list": _list,
        "report": _report_fn,
        "status": _status,
        "gameday": _gameday,
        "onboard": _onboard,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
