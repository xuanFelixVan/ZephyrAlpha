# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §3.4
# [MODULE] scripts.clone_guard_audit
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.orchestrator (CloneGuardOrchestrator); pathlib; sys
# [CONSUMERS] 事件触发（手动 / CI push 事件 / MCP audit_status 查询前预先跑）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] L2 周期审计触发入口——事件触发非 cron（守 AGENTS.md 永久系统四要素"禁止时间触发"）；
#              审计结果为派生产物写 .runtime/clone_guard_audit/（不入 git）；脚本只触发+打印，不写 depgraph 不新增 reconciler
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] orchestrator.audit() 守 ERROR_CONTRACT；脚本捕获异常打印非零退出，不抛
# [TESTS] 手动触发验证（.runtime/clone_guard_audit/ 产 JSON 即通过）
# [A_module] module_id=MOD-CLONE_GUARD | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuard L2 周期审计触发脚本（事件驱动，非 cron）。

守 AGENTS.md 永久系统四要素：禁止时间触发（cron/Timer/sleep-loop）。
本脚本由以下事件触发：
  - 手动：python scripts/clone_guard_audit.py
  - CI push 事件：GitHub Actions on push（事件触发，非 schedule）
  - MCP 查询前：clone_guard.audit_status 只读历史 JSON，需先经本脚本产出基线

输出：审计 JSON 持久化到 .runtime/clone_guard_audit/audit_<ts>.json（派生产物，不入 git）。
退出码：0=审计完成（含降级），1=审计异常，2=无可审计文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 包外 bootstrap：一次性极简 sys.path 注入（仅此一次，后续路径常量必须用 REPO_ROOT）
REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.clone_guard.orchestrator import AuditResult, CloneGuardOrchestrator  # noqa: E402


def _collect_py_files(repo_root: Path) -> list[str]:
    """收集 src/ 下全部 .py 文件（相对路径，正斜杠归一化）。

    orchestrator._filter_files 会进一步排除测试/忽略路径，故此处全量收集即可。
    """
    src_dir = repo_root / "src"
    if not src_dir.exists():
        return []
    files: list[str] = []
    for p in sorted(src_dir.rglob("*.py")):
        rel = str(p.relative_to(repo_root)).replace("\\", "/")
        files.append(str(rel))
    return files


def _print_summary(result: AuditResult) -> None:
    """打印审计摘要（stdout，供 CI 日志/MCP 消费）。"""
    print("=" * 60)
    print(f"CloneGuard L2 审计完成 @ {result.timestamp}")
    print("=" * 60)
    print(f"健康评分      : {result.health_score} (A=无债, F=extract 级债严重)")
    print(f"检测文件数    : {result.checked_files}")
    print(f"findings 总数 : {len(result.findings)}")
    print(f"活跃引擎数    : {result.active_engine_count}")
    if result.degraded_engines:
        print(f"降级引擎      : {', '.join(result.degraded_engines)}")
    else:
        print("降级引擎      : 无")
    if result.refactoring_plan:
        print(f"重构建议      : {len(result.refactoring_plan)} 条")
        for i, plan in enumerate(result.refactoring_plan[:5], 1):
            print(f"  [{i}] {plan}")
        if len(result.refactoring_plan) > 5:
            print(f"  ... 余 {len(result.refactoring_plan) - 5} 条见 JSON")
    print(f"持久化路径    : {result.persisted_path or '(未持久化)'}")
    print("=" * 60)
    # 按严重性统计
    sev_counts: dict[str, int] = {}
    for f in result.findings:
        sev = getattr(f, "severity", "unknown")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
    if sev_counts:
        print("严重性分布    : " + ", ".join(f"{k}={v}" for k, v in sorted(sev_counts.items())))


def main() -> int:
    """审计入口。返回退出码（0=完成, 1=异常, 2=无可审计文件）。"""
    files = _collect_py_files(REPO_ROOT)
    if not files:
        print("CloneGuard audit: src/ 下无可审计 .py 文件", file=sys.stderr)
        return 2

    print(f"CloneGuard audit: 收集到 {len(files)} 个 .py 文件，启动 L2 全量审计...")

    try:
        orch = CloneGuardOrchestrator(REPO_ROOT)
        result = orch.audit(files)
    except Exception as e:  # noqa: BLE001  脚本层兜底，不抛
        print(f"CloneGuard audit 异常: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    _print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
