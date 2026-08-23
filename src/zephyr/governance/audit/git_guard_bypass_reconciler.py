# [BLUEPRINT] MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §git-guard-bypass-reconciler
# [MODULE] zephyr.governance.audit.git_guard_bypass_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（任何非空 committed_files）；reconciler 永不抛异常（异常降级为 warn）；warn-only 不阻断 commit
# [MODIFY-GUARD] _PRIORITY 优先级；_WINDOW 回溯窗口
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——git reflog/审计日志读取失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_git_guard_bypass_reconciler.py
# [A_module] module_id=MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

git_guard_bypass_reconciler.py — git_guard alias 绕过检测 post-commit reconciler。

#ARCH-GIT-SELF-HARM-GUARD L2.3（2026-08-04）

治本动机
--------
git_guard.py 通过 git alias 拦截危险命令（reset --hard / checkout -- / restore），
但 ``git -c alias.reset= reset --hard`` 可静默绕过 alias（setup_git_guard_aliases.py:129
自述）。L1+L2 的自伤检测只覆盖走 alias 的调用，绕过 alias 的调用完全不受监控。

本 reconciler 是 L2.3 治本——post-commit 事件驱动对比 ``git reflog`` 的 reset 记录
与 ``.runtime/gate_audit/git_guard_self_harm.jsonl`` 审计日志：

    reflog 有 reset 但审计日志无对应记录 = 绕过 alias（疑似）

检测原理
--------
1. **时间窗口**: 取本次 commit（HEAD）与上次 commit（HEAD~1）之间的时间段
2. **reflog 侧**: ``git reflog --format=%ct|%gs`` 筛选 ``reset: moving to`` 条目，
   时间戳落在窗口内的 = 该窗口内发生的 reset 操作
3. **审计侧**: 读 ``.runtime/gate_audit/git_guard_self_harm.jsonl``，筛选 timestamp
   落在窗口内的记录 = 被 git_guard 审计的 reset 操作
4. **对比**: reflog_resets > audited_resets → 疑似绕过

已知局限（warn-only 设计依据）
-----------------------------
- ``reset --soft`` / ``reset --mixed`` 也产生 ``reset: moving to`` reflog 条目，但不
  触发自伤检测（非危险），因此 reflog_resets ≥ audited_resets 是常态。本 reconciler
  报告差值供 AI/人工研判，不阻断 commit（避免误伤合法的 --soft/--mixed）。
- ``restore`` / ``checkout -- <file>`` 不产生 reflog 条目（只动工作区不动 HEAD），
  因此本 reconciler 无法检测这两类命令的绕过。完整检测需 shell 级审计，超出 L2.3 范围。
- 首次 commit（无 HEAD~1）无时间窗口，跳过。

priority: 810（stash_lifecycle=801 之后，gate_inventory_sync=820 之前——与基础设施
清理 reconciler 同组，紧跟 stash lifecycle）

Usage
-----
::

    from zephyr.governance.audit.git_guard_bypass_reconciler import (
        make_git_guard_bypass_reconciler,
    )

    registry.register(make_git_guard_bypass_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: git reflog 与 commit 时间戳 subprocess 数据
#   fields: git log --format=%ct（HEAD/HEAD~1）+ git reflog --format=%ct|%gs 的 reset 条目
#   code: _get_commit_timestamp L86 / _get_reflog_resets_in_window L112
# - id: I2
#   name: git_guard 自伤审计日志 JSONL
#   fields: .runtime/gate_audit/git_guard_self_harm.jsonl 的 timestamp 记录
#   code: _AUDIT_LOG_REL L83
# 层: 算法
# - id: A1
#   name_zh: ① 时间窗口定位
#   name_en: _get_commit_timestamp
#   intro: 取本次 commit（HEAD）与上次 commit（HEAD~1）的时间戳划定检测窗口
#   desc: git log -1 --format=%ct <ref>，失败返回 None；无 HEAD~1（首次 commit）则 skip
#   inputs: I1
#   outputs: 窗口 [prev_ts, head_ts]
# - id: A2
#   name_zh: ② 窗口内 reset 双侧采集
#   name_en: _get_reflog_resets_in_window / _get_audited_resets_in_window
#   intro: 分别统计窗口内 reflog 的 reset 条目数和审计日志的记录数
#   desc: reflog 侧筛 subject 以 "reset:" 开头且 ts 落在窗口（含两端）；审计侧逐行 json.loads 筛 timestamp 落窗
#   inputs: I1 I2 A1
#   outputs: reflog_count 与 audit_count
# - id: A3
#   name_zh: ③ 绕过判定分级
#   name_en: _reconcile
#   intro: reflog 有 reset 而审计空白=疑似 alias 绕过 warn；reflog>审计=弱信号 warn；否则 clean
#   desc: reflog_count==0→skip；audit_count==0→warn（强信号）；diff>0→warn（弱信号，容忍 --soft/--mixed 误报）；否则 clean；异常降级 warn
#   inputs: A2
#   outputs: ReconcileResult（warn-only 不阻断）
#   invariant: reconciler 永不抛异常
# 层: 输出
# - id: O1
#   name_zh: 绕过检测对账结果
#   name_en: ReconcileResult
#   intro: skip/clean/warn 三态结论，报告差值供 AI/人工研判，不阻断 commit
#   invariant: warn-only
#   downstream: GitCommitGateway（[CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)

logger = logging.getLogger(__name__)

_GATE_ID = "GATE-GIT-GUARD-BYPASS"
_PRIORITY = 810

# 审计日志路径（相对 project_root，与 git_guard._audit_self_harm 落盘路径一致）
_AUDIT_LOG_REL = Path(".runtime") / "gate_audit" / "git_guard_self_harm.jsonl"


def _get_commit_timestamp(project_root: Path, ref: str) -> float | None:
    """获取指定 ref 的 commit 时间戳（Unix epoch 秒）。

    Args:
        project_root: 仓库根目录。
        ref: git ref，如 "HEAD" 或 "HEAD~1"。

    Returns:
        时间戳（float）；ref 不存在或 git 失败返回 None。
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", ref],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:  # noqa: BLE001 — reconciler 永不抛异常
        pass
    return None


def _get_reflog_resets_in_window(
    project_root: Path, window_start: float, window_end: float
) -> tuple[list[tuple[float, str]], int]:
    """获取时间窗口内的 reflog reset 条目（same-sha 自指 reset 已排除）。

    CAND-GOVSEC-001 附修（2026-08-23 src 误删取证 §5.3）：``git reset``（mixed/--hard）
    回到当前位置（same-sha）同样产生 ``reset: moving to`` reflog 条目，但 HEAD 未发生
    任何移动、工作区零破坏——计入即误报（事故 session 的 ``git reset -q`` 实证）。
    判定原理：HEAD reflog 按时间倒序，第 i 行记录「从旧位置移动到新位置 %H」，
    其旧位置 = 下一行（更老一行）的 %H——same-sha reset ⟺ 本行 %H == 下一行 %H。
    一次 subprocess 全量判定，零额外 rev-parse 开销。

    Returns:
        (entries, same_sha_excluded)：
        - entries: [(timestamp, subject), ...] 有效 reset 列表，按时间升序；
        - same_sha_excluded: 被排除的 same-sha 自指 reset 条数（全窗口外也统计，供
          detail 可观测——same-sha 永不构成绕过信号，窗口过滤前排除）。
        最老一行无下一行可比对 → 保守计入（warn-only 方向）。
    """
    try:
        result = subprocess.run(
            ["git", "reflog", "--format=%ct|%H|%gs"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=15,
        )
    except Exception:  # noqa: BLE001 — reconciler 永不抛异常
        return [], 0

    if result.returncode != 0:
        return [], 0

    # 1. 全量行解析（倒序链——same-sha 判定依赖「下一行 %H = 本行旧位置」，
    #    故必须先建全量序列再做窗口过滤）
    rows: list[tuple[float, str, str]] = []  # (ts, new_sha, subject) newest-first
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        ts_str, _, rest = line.partition("|")
        new_sha, _, subject = rest.partition("|")
        try:
            ts = float(ts_str)
        except ValueError:
            continue
        rows.append((ts, new_sha, subject))

    # 2. same-sha 排除 + 窗口过滤
    entries: list[tuple[float, str]] = []
    same_sha_excluded = 0
    for i, (ts, new_sha, subject) in enumerate(rows):
        # 只关心 reset 操作（checkout/commit/stash 等不属本 reconciler 范围）
        if not subject.startswith("reset:"):
            continue
        old_sha = rows[i + 1][1] if i + 1 < len(rows) else None
        if old_sha is not None and old_sha == new_sha:
            same_sha_excluded += 1  # 自指 reset（如 `git reset -q` / `reset --hard HEAD`）——无害
            continue
        # 窗口: [window_start, window_end]——含两端。reset 可能与上次 commit 同秒
        # （git log --format=%ct 秒级精度），用 >= 避免漏检（warn-only 容忍少量误报）
        if window_start <= ts <= window_end:
            entries.append((ts, subject))
    return entries, same_sha_excluded


def _get_audited_resets_in_window(audit_log: Path, window_start: float, window_end: float) -> list[dict]:
    """读取审计日志，筛选时间窗口内的记录。

    Returns:
        [record_dict, ...] 列表。
    """
    if not audit_log.exists():
        return []
    records: list[dict] = []
    try:
        with audit_log.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = rec.get("timestamp", 0)
                if isinstance(ts, (int, float)) and window_start <= ts <= window_end:
                    records.append(rec)
    except OSError:  # noqa: BLE001 — 文件读取失败不阻断
        pass
    return records


def make_git_guard_bypass_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-GIT-GUARD-BYPASS post-commit alias 绕过检测 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。
    """
    project_root: Path = gateway.project_root
    audit_log = project_root / _AUDIT_LOG_REL

    def _trigger(committed_files: list[str]) -> bool:
        # 任何非空 commit 都触发——绕过检测与 commit 频率正相关
        return bool(committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            # 1. 确定时间窗口 [HEAD~1 commit 时间, HEAD commit 时间]
            head_ts = _get_commit_timestamp(project_root, "HEAD")
            if head_ts is None:
                return ReconcileResult(
                    action="skip",
                    detail="git-guard-bypass: 无法获取 HEAD 时间戳（空仓库？）",
                    gate_id=_GATE_ID,
                )
            prev_ts = _get_commit_timestamp(project_root, "HEAD~1")
            if prev_ts is None:
                # 首次 commit，无前序窗口可对比
                return ReconcileResult(
                    action="skip",
                    detail="git-guard-bypass: 首次 commit（无 HEAD~1），跳过绕过检测",
                    gate_id=_GATE_ID,
                )

            # 2. 获取窗口内的 reflog reset 条目（same-sha 自指 reset 已排除——误报治本）
            reflog_resets, same_sha_excluded = _get_reflog_resets_in_window(project_root, prev_ts, head_ts)

            # 3. 获取窗口内的审计记录
            audited = _get_audited_resets_in_window(audit_log, prev_ts, head_ts)

            reflog_count = len(reflog_resets)
            audit_count = len(audited)
            excluded_note = (
                f"（已排除 {same_sha_excluded} 次 same-sha 自指 reset——HEAD 未移动的无害操作）"
                if same_sha_excluded
                else ""
            )

            # 4. 对比判定
            if reflog_count == 0:
                return ReconcileResult(
                    action="skip",
                    detail=f"git-guard-bypass: 窗口内无有效 reset 操作{excluded_note}",
                    gate_id=_GATE_ID,
                )

            # reflog 有 reset 但审计日志完全空白 → 强信号：疑似绕过
            if audit_count == 0:
                # 区分: 审计文件不存在（git_guard 从未运行）vs 存在但窗口内无记录
                file_status = "审计文件不存在" if not audit_log.exists() else "审计文件存在但窗口内无记录"
                detail = (
                    f"git-guard-bypass: 窗口内 {reflog_count} 次 reset 但 0 条审计记录"
                    f"（{file_status}）——疑似 alias 绕过"
                    f"（如 `git -c alias.reset= reset --hard`）{excluded_note}"
                )
                logger.warning("GATE-GIT-GUARD-BYPASS: %s", detail)
                return ReconcileResult(
                    action="warn",
                    detail=detail,
                    gate_id=_GATE_ID,
                )

            # reflog 多于审计 → 弱信号：部分绕过（也可能是 --soft/--mixed 合法不触发审计）
            diff = reflog_count - audit_count
            if diff > 0:
                detail = (
                    f"git-guard-bypass: reflog reset={reflog_count} > 审计记录={audit_count}"
                    f"（差值 {diff} 可能是 --soft/--mixed 合法操作，也可能是绕过）{excluded_note}"
                )
                logger.info("GATE-GIT-GUARD-BYPASS: %s", detail)
                return ReconcileResult(
                    action="warn",
                    detail=detail,
                    gate_id=_GATE_ID,
                )

            # reflog ≤ 审计 → 正常（每次 reset --hard 都被审计）
            return ReconcileResult(
                action="clean",
                detail=(
                    f"git-guard-bypass: 窗口内 {reflog_count} 次 reset 全部被审计（audit={audit_count}），"
                    f"无绕过迹象{excluded_note}"
                ),
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("git_guard_bypass reconciler failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"git-guard-bypass 检测失败: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
