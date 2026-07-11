# [BLUEPRINT] SRC-065 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.startup_shutdown_cli
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_startup_shutdown_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import argparse


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zephyr",
        description="ZephyrAlpha 启动/停机 CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="启动系统")
    start.add_argument(
        "--phases",
        type=str,
        default="1-6",
        help="启动阶段范围，如 1-6 (默认: 1-6)",
    )

    stop = sub.add_parser("stop", help="停止系统")
    stop.add_argument(
        "--phases",
        type=str,
        default="6-1",
        help="停机阶段范围，如 6-1 (默认: 6-1)",
    )

    sub.add_parser("status", help="查看系统状态")

    return parser


def parse_phase_range(range_str: str) -> list[int]:
    parts = range_str.split("-")
    if len(parts) != 2:
        return []
    try:
        start = int(parts[0])
        end = int(parts[1])
        if start <= end:
            return list(range(start, end + 1))
        else:
            return list(range(start, end - 1, -1))
    except ValueError:
        return []


def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()

    if args.command == "start":
        phases = parse_phase_range(args.phases)
        print(f"zephyr-start phases: {phases} (from {args.phases})")
    elif args.command == "stop":
        phases = parse_phase_range(args.phases)
        print(f"zephyr-stop phases: {phases} (from {args.phases})")
    elif args.command == "status":
        print("zephyr-status: OK")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
