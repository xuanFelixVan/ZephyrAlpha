# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python3
# [MODULE] scripts.governance.run_gate_chain
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants (EXIT_*)
# [CONSUMERS] .pre-commit-config.yaml（gate-vocab / gate-ssot-code / gate-test / gate-c2 / gate-reg-bl / gate-script-q / gate-naming-audit / gate-frontmatter-audit）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 顺序执行不短路（全量跑完再聚合）；聚合 exit 仅由内容判定决定；副作用仅标注不计失败
# [MODIFY-GUARD] 聚合语义变更须同步 tests/governance/test_run_gate_chain.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 0=全 PASS；1=有内容发现；2=子门禁自身异常（含启动失败）；用法错误=2
# [TESTS] tests/governance/test_run_gate_chain.py
# [A_module] module_id=MOD-GOV_GATE_CHAIN | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""run_gate_chain.py — 顺序运行多个门禁脚本，按"内容判定"聚合退出码。

用于 pre-commit hook 合并：将多个 GATE 脚本合并为单 hook 时使用。
每个命令用逗号分隔，脚本路径和参数均为逗号分割的 token。

退出码语义（CAND-GATEMECH-002 治本，2026-08-30）：
  0 = 全部子门禁内容判定 PASS（0 findings）
  1 = 至少一个子门禁有内容发现（findings，子进程 exit 1）
  2 = 至少一个子门禁自身异常（exit >=2 / 信号终止 / 子进程启动失败）

  原实现缺陷：`code = result.returncode` 末位非零覆盖——后一个 exit 1 会掩盖
  前一个 exit 2（异常被降级为 findings）；子进程启动失败（FileNotFoundError
  等）则以未捕获 traceback 退出（exit 1），0-findings 场景被聚合标红。
  修复：按 severity 聚合 ERROR > FINDINGS > PASS，启动失败归类 ERROR。

报告二分（CAND-GATEMECH-001 治本，2026-08-30）：
  - 内容判定区：逐脚本 exit 语义（PASS/FINDINGS/ERROR），聚合 exit 只由本区决定。
  - hook 副作用区：运行期间改动工作区文件的步骤清单（files-modified）——
    hook 副作用与内容判定解耦，仅作干扰标注，不计入内容判定失败。
    副作用检测依赖 git status 快照差分；非 git 环境自动跳过（不阻断）。

Usage:
    python scripts/governance/run_gate_chain.py script1.py,arg1,arg2 script2.py,arg3
"""

from __future__ import annotations

__manifest__ = """
args: []
description: run_gate_chain.py — 顺序运行多个门禁脚本，内容判定聚合退出码 + files-modified 副作用分列报告。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS
from zephyr.shared.infra.process_pool import run_subprocess_hidden

__all__: Final = ["StepResult", "aggregate_exit_code", "main"]

_GIT_SNAPSHOT_TIMEOUT = 15


@dataclass
class StepResult:
    """单个子门禁步骤的执行结果（内容判定与副作用分离）。"""

    name: str
    returncode: int | None
    launch_error: str | None = None
    side_effects: tuple[str, ...] = field(default_factory=tuple)

    @property
    def verdict(self) -> str:
        """内容判定：ERROR（自身异常）/ FINDINGS（有发现）/ PASS。"""
        if self.launch_error is not None or self.returncode is None:
            return "ERROR"
        if self.returncode == EXIT_PASS:
            return "PASS"
        if self.returncode == EXIT_FINDINGS:
            return "FINDINGS"
        return "ERROR"


def _snapshot_worktree(root: Path) -> frozenset[str] | None:
    """git status 快照（副作用检测基线）。git 不可达返回 None（跳过检测，不阻断）。"""
    try:
        result = run_subprocess_hidden(
            ["git", "status", "--porcelain=v1"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(root),
            timeout=_GIT_SNAPSHOT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return frozenset(line for line in result.stdout.splitlines() if line.strip())


def _diff_snapshots(before: frozenset[str] | None, after: frozenset[str] | None) -> tuple[str, ...]:
    """快照差分：返回本步骤新增/变更的文件行。任一快照不可用返回空（跳过）。"""
    if before is None or after is None:
        return ()
    return tuple(sorted(after - before))


def _run_step(script: str, args: list[str]) -> StepResult:
    """执行单个子门禁；启动失败归类为 launch_error（ERROR），不抛 traceback。

    快照 cwd 取进程当前目录（pre-commit 从 repo 根调用）；script token 可为
    "-m"（python -m pytest 形式），故不从 script 路径推导 cwd。
    """
    cwd = Path.cwd()
    before = _snapshot_worktree(cwd)
    try:
        result = run_subprocess_hidden([sys.executable, script] + args)
        after = _snapshot_worktree(cwd)
        return StepResult(
            name=script,
            returncode=result.returncode,
            side_effects=_diff_snapshots(before, after),
        )
    except OSError as exc:
        return StepResult(name=script, returncode=None, launch_error=f"{type(exc).__name__}: {exc}")


def aggregate_exit_code(steps: list[StepResult]) -> int:
    """按内容判定聚合：ERROR(2) > FINDINGS(1) > PASS(0)。副作用不参与聚合。"""
    worst = EXIT_PASS
    for step in steps:
        verdict = step.verdict
        if verdict == "ERROR":
            return EXIT_ERROR
        if verdict == "FINDINGS":
            worst = EXIT_FINDINGS
    return worst


def _print_report(steps: list[StepResult]) -> None:
    """二分报告：内容判定区 + hook 副作用区（files-modified 仅标注）。"""
    print(f"\n{'=' * 60}")
    print("[run_gate_chain] 内容判定（聚合 exit 仅由本区决定）")
    print(f"{'=' * 60}")
    for step in steps:
        detail = step.launch_error or f"exit={step.returncode}"
        print(f"  [{step.verdict:8}] {step.name} ({detail})")
    side_effect_steps = [s for s in steps if s.side_effects]
    print(f"\n{'-' * 60}")
    print("[run_gate_chain] hook 副作用（files-modified，干扰标注，不计失败）")
    print(f"{'-' * 60}")
    if not side_effect_steps:
        print("  （无）")
    for step in side_effect_steps:
        print(f"  {step.name}: {len(step.side_effects)} 个文件被修改")
        for entry in step.side_effects[:10]:
            print(f"    {entry}")


def main() -> int:
    """Entry point: parse args, run scripts in sequence, return aggregated exit code."""
    cmds = sys.argv[1:]
    if not cmds:
        print("Usage: run_gate_chain.py script1.py,arg1 script2.py,arg2", file=sys.stderr)
        return EXIT_ERROR

    steps: list[StepResult] = []
    for cmd_str in cmds:
        parts = cmd_str.split(",")
        script, args = parts[0], parts[1:]
        print(f"\n{'=' * 60}")
        print(f"[run_gate_chain] {script} {' '.join(args)}")
        print(f"{'=' * 60}")
        steps.append(_run_step(script, args))

    _print_report(steps)
    return aggregate_exit_code(steps)


if __name__ == "__main__":
    sys.exit(main())
