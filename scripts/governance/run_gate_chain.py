#!/usr/bin/env python3
# [MODULE] scripts.governance.run_gate_chain
# [DOMAIN] D_GOV_SCRIPTS
# [STARTUP] manual
# [MATURITY] prototype
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""run_gate_chain.py — 顺序运行多个门禁脚本，任一失败即整体失败。

用于 pre-commit hook 合并：将多个 GATE 脚本合并为单 hook 时使用。
每个命令用逗号分隔，脚本路径和参数均为逗号分割的 token。

Usage:
    python scripts/governance/run_gate_chain.py script1.py,arg1,arg2 script2.py,arg3
"""
import subprocess
import sys

__manifest__ = """
args: []
description: run_gate_chain.py — 顺序运行多个门禁脚本，任一失败即整体失败。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""



def main() -> int:
    """Entry point: parse args, run scripts in sequence, return worst exit code."""
    cmds = sys.argv[1:]
    if not cmds:
        print("Usage: run_gate_chain.py script1.py,arg1 script2.py,arg2", file=sys.stderr)
        return 2
    code = 0
    for cmd_str in cmds:
        parts = cmd_str.split(",")
        script = parts[0]
        args = parts[1:]
        print(f"\n{'=' * 60}")
        print(f"[run_gate_chain] {script} {' '.join(args)}")
        print(f"{'=' * 60}")
        result = subprocess.run([sys.executable, script] + args)
        if result.returncode:
            code = result.returncode
    return code


if __name__ == "__main__":
    sys.exit(main())
