# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/reset_cbg.py | §
# [MODULE] scripts.governance.d1_structure.reset_cbg
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.circuit_breaker
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
# [TTL] permanent
#!/usr/bin/env python3
"""
CBG 熔断器重置 CLI (CircuitBreakerGateway Reset Command)



任务编号 : T-V2-005 Step 4（GLM-5.1 子任务）
权限层级 : Human-Gated（仅 Owner 可执行）
创建日期 : 2026-04-27

功能说明
--------
Owner 手动重置指定 (caller, target) 对的熔断状态为 CLOSED。

底层调用 CBGManager.reset()，将 state 重置为 CLOSED、
failure_count 归零、opened_at/reason 清空。

用法
----
重置单个熔断器：
    python scripts/governance/reset_cbg.py --caller RI-05 --target L2a

列出所有 OPEN 状态的熔断器：
    python scripts/governance/reset_cbg.py --list

重置所有 OPEN 熔断器：
    python scripts/governance/reset_cbg.py --reset-all
"""

from __future__ import annotations

__manifest__ = """
args: []
description: CBG熔断器重置工具（Owner-Gated——仅 Owner 可执行）
dimensions:
- D1
priority: P2
timeout_seconds: 30
warn_only: true
"""


import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

_warn_only = "--warn-only" in sys.argv
try:
    from zephyr.gov_enforcement.rule_enforcement.circuit_breaker import CBGManager, CircuitBreakerState
except ImportError as e:
    print(f"[SKIP] reset_cbg.py 无法加载 CBGManager（依赖缺失: {e}）", file=sys.stderr)
    print("       此脚本需要 zephyr.governance.gates.circuit_breaker 及相关依赖存在时才能运行", file=sys.stderr)
    sys.exit(0 if _warn_only else 2)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="CBG 熔断器重置 CLI（仅 Owner 可执行）")
    parser.add_argument(
        "--caller",
        type=str,
        help="发起调用的模块标识（如 RI-05）",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="目标模块标识（如 L2a）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_open",
        help="列出所有 OPEN 状态的熔断器",
    )
    parser.add_argument(
        "--reset-all",
        action="store_true",
        dest="reset_all",
        help="重置所有 OPEN 状态的熔断器",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：操作失败不阻塞（exit 0）",
    )
    args = parser.parse_args()

    if args.list_open:
        with CBGManager() as mgr:
            open_circuits = mgr.list_open_circuits()
        if not open_circuits:
            print("[reset_cbg] 无 OPEN 状态的熔断器", file=sys.stderr)
            sys.exit(EXIT_PASS)
        print(f"[reset_cbg] 发现 {len(open_circuits)} 个 OPEN 熔断器:", file=sys.stderr)
        for rec in open_circuits:
            print(
                f"  {rec.caller_module} → {rec.target_module}  "
                f"failures={rec.failure_count}  "
                f"opened_at={rec.opened_at}  "
                f"reason={rec.reason}",
                file=sys.stderr,
            )
        sys.exit(EXIT_PASS)

    if args.reset_all:
        with CBGManager() as mgr:
            open_circuits = mgr.list_open_circuits()
        if not open_circuits:
            print("[reset_cbg] 无 OPEN 状态的熔断器，无需重置", file=sys.stderr)
            sys.exit(EXIT_PASS)
        reset_count = 0
        for rec in open_circuits:
            with CBGManager() as mgr:
                ok = mgr.reset(rec.caller_module, rec.target_module)
            if ok:
                print(f"  RESET: {rec.caller_module} → {rec.target_module}", file=sys.stderr)
                reset_count += 1
        print(f"[reset_cbg] 已重置 {reset_count}/{len(open_circuits)} 个熔断器", file=sys.stderr)
        sys.exit(EXIT_PASS)

    if not args.caller or not args.target:
        if args.warn_only:
            print("[reset_cbg] --warn-only 模式：无操作指定，正常退出", file=sys.stderr)
            sys.exit(EXIT_PASS)
        print(
            "[reset_cbg] 无操作指定——请使用 --list 查看、--reset-all 批量重置，或 --caller/--target 指定单个熔断器",
            file=sys.stderr,
        )
        print("  当前状态: 无 OPEN 熔断器（系统正常）", file=sys.stderr)
        sys.exit(EXIT_PASS)

    with CBGManager() as mgr:
        record = mgr.get_state(args.caller, args.target)
        if record is None:
            print(f"[reset_cbg] 无记录: {args.caller} → {args.target}（无需重置）", file=sys.stderr)
            sys.exit(EXIT_PASS)
        if record.state != CircuitBreakerState.OPEN:
            print(
                f"[reset_cbg] {args.caller} → {args.target} 当前状态={record.state.value}，非 OPEN 无需重置",
                file=sys.stderr,
            )
            sys.exit(EXIT_PASS)
        ok = mgr.reset(args.caller, args.target)

    if ok:
        print(f"[reset_cbg] RESET OK: {args.caller} → {args.target}", file=sys.stderr)
        sys.exit(EXIT_PASS)
    else:
        print(f"[reset_cbg] RESET FAIL: {args.caller} → {args.target}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
