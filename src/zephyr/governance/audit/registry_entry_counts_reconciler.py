# [BLUEPRINT] MOD-GOV_REGISTRY_ENTRY_COUNTS_RECONCILER | docs/03_modules/_domain_governance/blueprint.md | §registry-entry-counts-reconciler
# [MODULE] zephyr.governance.audit.registry_entry_counts_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway（post-commit 事件触发，
#   经 ReconciliationRegistry 外部规格发现钩子注册）；scripts/governance/d3_metadata/check_registry_consistency.py（CR-007/CR-007b 回填工具）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 回填只经 check_registry_consistency.py --update-entry-counts（CR-007 Owner 批"账本数字自动回填"
#   2026-09-06 的 sanctioned landing tool，行级手术保注释、仅动已登记口径 counting_rule 的 STALE 行，
#   口径争点行不机械回填）；本模块不自写 ROOR 任何字节；
#   post-commit 事件触发（ROOR/工具变更才触发），禁 cron/Timer/sleep-loop（宪法 §9.3）；
#   回填后 ROOR 漂移走 gateway._commit_auto 统一入口（DCR gate 覆盖），无 gateway 时留工作区 warn 不静默丢弃；
#   reconciler 永不抛异常（异常降级 ReconcileResult(action="warn")，registry 框架兜底）
# [MODIFY-GUARD] GATE_ID/_PRIORITY/_TRIGGER_RELPATHS 语义
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 工具 subprocess 失败/超时 → warn（不抛）；回填零行 → clean；auto-commit 失败 → warn
# [TESTS] tests/governance/test_registry_entry_counts_reconciler.py
# [A_module] module_id=MOD-GOV_REGISTRY_ENTRY_COUNTS_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""registry_entry_counts_reconciler — ROOR entry_count 实测对账回填 post-commit reconciler（C25 接线）。

病灶与处方（C25/S4 §4 B10-1）
------------------------------
ROOR（``docs/registry_of_registries.yaml``）entry_count 为手工维护面，注册表增减后数字漂移
无人发现（CR-007 病灶，2026-09-06 Owner 批"账本数字自动回填"）。回填工具
``check_registry_consistency.py --update-entry-counts`` 已落地（行级手术保注释，仅回填
已登记 counting_rule 的 STALE 行），但无自动化触发——本模块把该工具挂上 post-commit
事件触发，即 C25 卡"给既有 reconciler 体系挂 --update-entry-counts 触发（1 处接线）"。

注册路径（gateway 静态注册段在途禁碰时的运行时注册，同 schedule_consistency_reconciler W4-4 范式）
--------------------------------------------------------------------------------------------------
``reconciliation_registry._EXTERNAL_SPEC_MODULES`` 增补一行
``"zephyr.governance.audit.registry_entry_counts_reconciler"`` 即通电
（该清单宿主文件他会话在途 MM 时，本模块先行落地+测试就绪，注册行由持钥会话错峰补插）。

对账链
------
1. trigger: committed_files 含 ROOR / 回填工具 / 本模块 → 命中
2. 跑 ``check_registry_consistency.py --update-entry-counts``（subprocess，timeout 90s）
3. 解析 ``[FIXED]`` 行计回填数；回填后 ``git diff --name-only -- <ROOR>`` 检测漂移
4. 有漂移且 gateway 可用 → ``_commit_auto`` 自动提交（chore(registry) 口径）
5. action 映射：回填+提交成功=auto_committed；回填但提交失败/无 gateway=warn；
   零回填=clean；工具失败=warn

Usage::

    from zephyr.governance.audit.registry_entry_counts_reconciler import (
        make_registry_entry_counts_reconciler, make_external_reconciler_spec,
    )
    registry.register(make_registry_entry_counts_reconciler(gateway))
    # 或经外部规格发现钩子：make_external_reconciler_spec(host)

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/audit/registry_entry_counts_reconciler.yaml
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)

logger = logging.getLogger(__name__)

GATE_ID = "GATE-REGISTRY-ENTRY-COUNTS"

#: blueprint_status_transition(825)/schedule_consistency(826) 之后、worktree watchdog(845) 之前
_PRIORITY = 830

#: 回填工具相对路径（CR-007/CR-007b sanctioned landing tool）
_TOOL_REL = "scripts/governance/d3_metadata/check_registry_consistency.py"

#: ROOR 相对路径（回填唯一写面——由工具行级手术，本模块零直写）
ROOR_REL = "docs/registry_of_registries.yaml"

#: 触发路径 = ROOR + 回填工具 + 本模块（改动即触发对账）
_TRIGGER_RELPATHS = (
    ROOR_REL,
    _TOOL_REL,
    "src/zephyr/governance/audit/registry_entry_counts_reconciler.py",
)

#: 工具 subprocess 超时（秒）——全量对账含 CR-007/CR-007b 实测扫描
_TOOL_TIMEOUT_SECONDS = 90

#: 自动提交消息口径（chore(registry)，与 registry_master_index 同族）
_AUTO_COMMIT_MSG = (
    "chore(registry): auto-backfill ROOR entry_count by post-commit reconciler (CR-007 --update-entry-counts)"
)


def _rel_path(f: str, project_root: Path) -> str:
    norm = f.replace("\\", "/")
    if not os.path.isabs(f):
        return norm  # 相对路径输入（已是仓根口径）直接归一分隔符
    try:
        return os.path.relpath(f, str(project_root)).replace("\\", "/")
    except ValueError:
        return norm


def run_entry_counts_backfill(project_root: Path) -> dict[str, object]:
    """执行回填工具并解析结果（检测核心，供 reconciler 与测试复用）。

    Returns:
        {"ok": bool, "fixed": list[str], "stale_left": int, "stderr_tail": str}
        —— ok=工具退出码 0；fixed=[FIXED] 行明细；stale_left=回填后仍 STALE 的行数；
        stderr_tail=工具 stderr 尾部（诊断用，截 400 字）。
    """
    proc = subprocess.run(  # noqa: S603 — 固定 argv 白名单工具调用  # noqa: bare-subprocess  固定argv白名单回填工具调用服务端无控制台交互
        [sys.executable, _TOOL_REL, "--update-entry-counts"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=_TOOL_TIMEOUT_SECONDS,
    )
    err = proc.stderr or ""
    fixed = [ln.strip() for ln in err.splitlines() if "[FIXED]" in ln]
    stale_left = sum(1 for ln in err.splitlines() if "STALE:" in ln)
    return {
        "ok": proc.returncode == 0,
        "fixed": fixed,
        "stale_left": stale_left,
        "stderr_tail": err[-400:],
    }


def make_registry_entry_counts_reconciler(gateway: object | None = None) -> ReconcilerSpec:
    """构造 ROOR entry_count 回填 post-commit reconciler（C25，CR-007 sanctioned 工具触发）。

    Args:
        gateway: GitCommitGateway 实例或 None——取 project_root 与 _commit_auto；
            None 时自解析 REPO_ROOT（回填照跑，漂移留工作区并 warn）。
    """
    if gateway is not None and getattr(gateway, "project_root", None):
        project_root = Path(str(gateway.project_root))
    else:
        from zephyr.shared.io.paths import REPO_ROOT

        project_root = Path(str(REPO_ROOT))

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            if _rel_path(f, project_root) in _TRIGGER_RELPATHS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            result = run_entry_counts_backfill(project_root)
        except Exception as exc:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("%s backfill tool failed: %s", GATE_ID, exc, exc_info=True)
            return ReconcileResult(
                action="warn",
                detail=f"entry_counts backfill tool error: {exc}",
                gate_id=GATE_ID,
            )
        if not result["ok"]:
            return ReconcileResult(
                action="warn",
                detail=(f"entry_counts backfill tool non-zero exit; stderr_tail={result['stderr_tail']}"),
                gate_id=GATE_ID,
            )

        fixed: list[str] = result["fixed"]  # type: ignore[assignment]
        if not fixed:
            return ReconcileResult(
                action="clean",
                detail="ROOR entry_count 对账一致（零回填）",
                gate_id=GATE_ID,
            )

        # 回填发生 → 检测 ROOR 漂移
        diff = subprocess.run(  # noqa: S603 — git 只读查询  # noqa: bare-subprocess  git只读diff查询固定argv无控制台交互
            ["git", "diff", "--name-only", "--", ROOR_REL],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        roor_dirty = bool(diff.stdout.strip())
        if not roor_dirty:
            return ReconcileResult(
                action="clean",
                detail=f"entry_counts 回填 {len(fixed)} 行但 ROOR 无净漂移（幂等回写）",
                gate_id=GATE_ID,
            )

        if gateway is None or not hasattr(gateway, "_commit_auto"):
            return ReconcileResult(
                action="warn",
                detail=(
                    f"entry_counts 回填 {len(fixed)} 行，ROOR 漂移留工作区"
                    f"（无 gateway，auto-commit 不可用）；处置=owner 责任制"
                ),
                gate_id=GATE_ID,
            )

        abs_files = [str(project_root / ROOR_REL)]
        commit_result = gateway._commit_auto(session_id, abs_files, _AUTO_COMMIT_MSG)
        status = getattr(commit_result, "status", "")
        if status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"entry_counts 回填 {len(fixed)} 行并自动提交（CR-007）: {fixed[:4]}",
                gate_id=GATE_ID,
            )
        if status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="entry_counts 回填后 auto-commit 无暂存差异（他写者已收编）",
                gate_id=GATE_ID,
            )
        return ReconcileResult(
            action="warn",
            detail=f"entry_counts 回填 {len(fixed)} 行，auto-commit 失败（{status}）",
            gate_id=GATE_ID,
        )

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),  # 工具行级手术写 ROOR；零删除/移动
    )


def make_external_reconciler_spec(host: object | None = None) -> ReconcilerSpec:
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定：registry/gateway/None 均可）。"""
    return make_registry_entry_counts_reconciler(host)
