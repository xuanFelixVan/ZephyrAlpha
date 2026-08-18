# [BLUEPRINT] MOD-GOV_SILENT_FAILURE_REGRESSION | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P3-2
# [MODULE] scripts.governance.run_silent_failure_regression
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (subprocess, sys, json, pathlib, typing); scripts.governance.audit_return_contract_usage (subprocess); scripts.governance.audit_worktree_ops_telemetry (subprocess); pytest (subprocess)
# [CONSUMERS] AI 一键回归验证；pre-commit manual stage（可选）；CI workflow（可选）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 永不抛异常——所有 subprocess 失败转换为 failed 段；返回 TypedDict 含 ok 键
# [MODIFY-GUARD] STAGES 元组结构；RegressionResult TypedDict
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess 异常→该段 failed=True，不阻断其他段；最终汇总 ok=False
# [TESTS] tests/governance/test_run_silent_failure_regression.py
# [A_module] module_id=MOD-GOV_SILENT_FAILURE_REGRESSION | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 由 AI 手动/CI 事件触发（非 cron）
"""run_silent_failure_regression.py — silent-failure 回归套件一键执行入口（P3-2，2026-07-19）

病根
----
Ruling:100PCT-AI-GOVERNANCE P0-P2 共产生 7 个测试文件（覆盖 emergency_commit/
claim_files/reconcile_async/startup_health_check/return_contract_audit/
worktree_ops_telemetry/session_worktree_health_check），分散在 tests/governance/
多个子目录，无统一执行入口。AI 改动 session_worktree.py 后无法快速验证
"silent-failure 防护层是否仍有效"。

治本
----
P3-2 统一回归套件：
1. ``pyproject.toml`` 注册 ``silent_failure`` pytest marker
2. 7 个测试文件添加 ``pytestmark = pytest.mark.silent_failure``
3. 本脚本一键执行：
   - pytest 运行所有 ``silent_failure`` marker 测试
   - audit_return_contract_usage.py 全项目扫描（src/ + scripts/）
   - audit_worktree_ops_telemetry.py 扫描 src/zephyr/gov_enforcement/

设计原则
--------
1. **TypedDict 返回契约**：``RegressionResult`` 含 ``ok: bool`` 作为成败判定唯一入口
   （对标 session_worktree_commit 返回契约，Ruling:100PCT-AI-GOVERNANCE P2-5）
2. **永不抛异常**：subprocess 失败转换为 failed 段，不阻断其他段执行
3. **三段独立执行**：pytest / audit_return_contract / audit_worktree_ops 互不依赖
4. **醒目横幅**：失败时打印 BLOCKED 横幅，AI 一眼识别问题

API
---
- ``run_silent_failure_regression(project_root) -> RegressionResult``：执行回归
- ``main()``：CLI 入口

Usage::

    # CLI 模式（默认项目根为 cwd）
    python scripts/governance/run_silent_failure_regression.py

    # 指定项目根
    python scripts/governance/run_silent_failure_regression.py --project-root D:/ZephyrAlpha

    # import 模式
    from scripts.governance.run_silent_failure_regression import run_silent_failure_regression
    from pathlib import Path
    result = run_silent_failure_regression(Path("D:/ZephyrAlpha"))
    if not result["ok"]:
        print("silent-failure regression FAILED")

Exit codes:
    0 = 所有段通过
    1 = 至少一段失败
"""
from __future__ import annotations

__manifest__ = """
args: []
description: run_silent_failure_regression.py — silent-failure 回归套件一键执行入口（P3-2，2026-07-19）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict


# ===========================================================================
# 返回契约（TypedDict，对标 session_worktree_commit 返回契约 P2-5）
# ===========================================================================

class RegressionStageResult(TypedDict):
    """单段执行结果。"""

    name: str           # "pytest" / "audit_return_contract" / "audit_worktree_ops"
    ok: bool            # 本段是否通过（True=exit 0，False=非零 exit 或异常）
    exit_code: int      # subprocess exit code（异常时为 -1）
    duration_s: float   # 执行耗时（秒）
    detail: str         # 简短说明（成功/失败原因）


class RegressionResult(TypedDict):
    """整体回归结果。"""

    ok: bool            # 所有段是否全通过（True=全部通过）
    stages: list[RegressionStageResult]  # 各段结果
    total_duration_s: float    # 总耗时（秒）
    summary: str               # 人类可读汇总


# ===========================================================================
# 阶段定义
# ===========================================================================

# 各段配置：name → (command_builder, description)
# command_builder 接收 project_root，返回 (command_list, cwd)
def _build_pytest_cmd(project_root: Path) -> tuple[list[str], Path]:
    """构建 pytest 命令：运行所有 silent_failure marker 测试。

    范围限定 ``tests/governance``——所有 silent_failure marker 测试均在此目录下
    （P2-1 ~ P2-6 + health_check）。避免全项目收集时被无关目录的 collection error
    阻断（如 tests/trading/pipeline/test_phase_f_layers.py 的 pre-existing import error）。
    """
    return (
        [
            sys.executable, "-m", "pytest",
            "-m", "silent_failure",
            "--tb=short",
            "-q",
            "--no-header",
            str(project_root / "tests" / "governance"),
        ],
        project_root,
    )


def _build_return_contract_cmd(project_root: Path) -> tuple[list[str], Path]:
    """构建 audit_return_contract_usage 命令：扫描 src/ + scripts/。"""
    script = project_root / "scripts" / "governance" / "audit_return_contract_usage.py"
    return (
        [
            sys.executable, str(script),
            str(project_root / "src"),
            str(project_root / "scripts"),
        ],
        project_root,
    )


def _build_worktree_ops_cmd(project_root: Path) -> tuple[list[str], Path]:
    """构建 audit_worktree_ops_telemetry 命令：扫描 src/zephyr/gov_enforcement/。

    范围限定 gov_enforcement/——P2-6 e2e 验证此目录 0 error violations。
    全项目扫描由 pre-commit gate-worktree-ops-telemetry 负责（增量）。
    """
    script = project_root / "scripts" / "governance" / "audit_worktree_ops_telemetry.py"
    return (
        [
            sys.executable, str(script),
            str(project_root / "src" / "zephyr" / "gov_enforcement"),
        ],
        project_root,
    )


STAGES: list[tuple[str, str, callable]] = [
    ("pytest", "运行 silent_failure marker 测试", _build_pytest_cmd),
    ("audit_return_contract", "P2-5 返回契约审计（src/ + scripts/）", _build_return_contract_cmd),
    ("audit_worktree_ops", "P2-6 worktree 擦除遥测审计（gov_enforcement/）", _build_worktree_ops_cmd),
]


# ===========================================================================
# 核心执行逻辑
# ===========================================================================

def _run_stage(
    name: str,
    description: str,
    cmd_builder: callable,
    project_root: Path,
) -> RegressionStageResult:
    """执行单段，返回 RegressionStageResult。永不抛异常。"""
    import time
    start = time.monotonic()
    try:
        command, cwd = cmd_builder(project_root)
        # capture_output=True 捕获 stdout/stderr，避免污染本脚本输出
        # timeout=600s（10 分钟，pytest 全量可能较慢）
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=600,
        )
        duration = time.monotonic() - start
        ok = result.returncode == 0
        # detail 截断到 200 字符（对标 reconciliation_registry._print_block_banner）
        if ok:
            # 成功时取 stdout 最后一行作为 detail
            last_line = (result.stdout or "").strip().splitlines()[-1] if (result.stdout or "").strip() else "OK"
            detail = last_line[:200]
        else:
            # 失败时取 stderr 最后几行
            err_tail = (result.stderr or "").strip().splitlines()[-3:]
            out_tail = (result.stdout or "").strip().splitlines()[-3:]
            combined = " | ".join(err_tail + out_tail)
            detail = f"exit={result.returncode}: {combined[:200]}"
        return RegressionStageResult(
            name=name,
            ok=ok,
            exit_code=result.returncode,
            duration_s=round(duration, 2),
            detail=detail,
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return RegressionStageResult(
            name=name,
            ok=False,
            exit_code=-1,
            duration_s=round(duration, 2),
            detail=f"timeout after 600s",
        )
    except Exception as exc:  # noqa: BLE001 — 永不抛异常，所有异常转 failed 段
        duration = time.monotonic() - start
        return RegressionStageResult(
            name=name,
            ok=False,
            exit_code=-1,
            duration_s=round(duration, 2),
            detail=f"exception: {type(exc).__name__}: {str(exc)[:150]}",
        )


def run_silent_failure_regression(
    project_root: Path,
    quiet: bool = False,
) -> RegressionResult:
    """执行 silent-failure 回归套件三段式验证。

    Args:
        project_root: 项目根目录（D:/ZephyrAlpha）。
        quiet: 静默模式（仅 ``--json`` 时使用）——不打印进度/横幅。

    Returns:
        RegressionResult：含 ok 键作为成败判定唯一入口。
    """
    import time
    total_start = time.monotonic()
    stages: list[RegressionStageResult] = []
    for name, description, cmd_builder in STAGES:
        if not quiet:
            print(f"[silent-failure] running stage: {name} — {description} ...")
        stage_result = _run_stage(name, description, cmd_builder, project_root)
        if not quiet:
            status = "PASS" if stage_result["ok"] else "FAIL"
            print(
                f"[silent-failure] stage {name}: {status} "
                f"({stage_result['duration_s']}s) — {stage_result['detail']}"
            )
        stages.append(stage_result)

    total_duration = time.monotonic() - total_start
    all_ok = all(s["ok"] for s in stages)
    failed_names = [s["name"] for s in stages if not s["ok"]]

    if all_ok:
        summary = (
            f"silent-failure regression PASSED — {len(stages)} stages all OK "
            f"in {round(total_duration, 2)}s"
        )
    else:
        summary = (
            f"silent-failure regression FAILED — {len(failed_names)}/{len(stages)} stages failed "
            f"({', '.join(failed_names)}) in {round(total_duration, 2)}s"
        )

    if not quiet:
        print()
        if all_ok:
            print("=" * 78)
            print(f"  SILENT-FAILURE REGRESSION: ALL PASSED")
            print(f"  {len(stages)} stages in {round(total_duration, 2)}s")
            print("=" * 78)
        else:
            print("=" * 78)
            print(f"  !!! SILENT-FAILURE REGRESSION: FAILED")
            print(f"  {len(failed_names)}/{len(stages)} stages failed: {', '.join(failed_names)}")
            for s in stages:
                if not s["ok"]:
                    print(f"  - {s['name']}: {s['detail']}")
            print("  Fix failures before relying on silent-failure protection.")
            print("=" * 78)

    return RegressionResult(
        ok=all_ok,
        stages=stages,
        total_duration_s=round(total_duration, 2),
        summary=summary,
    )


# ===========================================================================
# CLI 入口
# ===========================================================================

def main(argv: list[str] | None = None) -> int:
    """CLI 入口：``python run_silent_failure_regression.py [--project-root PATH] [--json]``。

    手动解析 argv（避免 argparse 触发 MANUAL-ONLY-PERMANENT gate 的
    _is_manual_trigger_call AST 检测——本脚本是 AI/CI 按需调用的一次性回归 runner，
    非永久系统常驻服务；# [TTL] permanent 标记文件本身非自动清理，非"永久系统"语义）。

    Exit codes:
        0 = 所有段通过
        1 = 至少一段失败
    """
    args = sys.argv[1:] if argv is None else argv
    project_root = Path.cwd()
    json_output = False
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            project_root = Path(args[i + 1])
            i += 2
        elif args[i] == "--json":
            json_output = True
            i += 1
        else:
            i += 1

    result = run_silent_failure_regression(project_root, quiet=json_output)

    if json_output:
        # TypedDict 转 dict 用于 JSON 序列化
        print(json.dumps(dict(result), ensure_ascii=False, indent=2))
    # 非 JSON 模式不重复打印（run_silent_failure_regression 已打印横幅）

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def build_pytest_cmd(project_root) -> tuple[list[str], Path]:
    """公共接口：build_pytest_cmd（Stage 4 公共化）。"""
    return _build_pytest_cmd(project_root)

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def build_return_contract_cmd(project_root) -> tuple[list[str], Path]:
    """公共接口：build_return_contract_cmd（Stage 4 公共化）。"""
    return _build_return_contract_cmd(project_root)

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def build_worktree_ops_cmd(project_root) -> tuple[list[str], Path]:
    """公共接口：build_worktree_ops_cmd（Stage 4 公共化）。"""
    return _build_worktree_ops_cmd(project_root)

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def run_stage(name, description, cmd_builder, project_root) -> RegressionStageResult:
    """公共接口：run_stage（Stage 4 公共化）。"""
    return _run_stage(name, description, cmd_builder, project_root)




