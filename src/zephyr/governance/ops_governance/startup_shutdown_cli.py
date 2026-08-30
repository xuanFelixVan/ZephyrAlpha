# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.startup_shutdown_cli
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: range_str 参数
#   fields: 参数 range_str，类型注解 str
#   code: startup_shutdown_cli.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_argparser
#   name_en: build_argparser
#   intro: build_argparser() 源码 L74-L99
#   desc: 源码 L74-L99
#   inputs: 无参数
#   outputs: argparse.ArgumentParser
# - id: A2
#   name_zh: ② parse_phase_range
#   name_en: parse_phase_range
#   intro: parse_phase_range(range_str) 源码 L102-L114
#   desc: 源码 L102-L114
#   inputs: range_str
#   outputs: list[int]
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: main() 源码 L117-L130
#   desc: 源码 L117-L130
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: argparse.ArgumentParser
#   name_en: argparse.ArgumentParser
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: list[int]
#   name_en: list[int]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

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
