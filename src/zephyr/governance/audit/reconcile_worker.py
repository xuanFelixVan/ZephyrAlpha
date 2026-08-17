# [BLUEPRINT] MOD-GOV_RECONCILE_WORKER | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] zephyr.governance.audit.reconcile_worker
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway); zephyr.governance.audit.reconciliation_registry (_log_reconcile_results); zephyr.governance.audit.reconcile_runner (write_status_file, STATUS_*); zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] zephyr.governance.audit.reconcile_runner.launch_reconcile_async (subprocess spawn)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] detached subprocess（父进程退出不影响 worker）；payload file 读取后立即删除；status file 流转 pending→running→done/failed；reconciler 异常降级为 warn 结果不阻断后续；worker 异常→status=failed+errors 持久化
# [MODIFY-GUARD] main 函数签名；payload file JSON schema；status file 写入时机（running 前后/done/failed）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] payload 不存在/JSON 解析失败→status=failed 立即退出；gateway 构造失败→status=failed；reconcile_for 内部异常已在 registry 层捕获
# [TESTS] tests/governance/audit/test_reconcile_async.py
# [A_module] module_id=MOD-GOV_RECONCILE_WORKER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 launch_reconcile_async 事件触发（非 cron/manual）
"""

reconcile_worker.py — 异步 reconciler worker（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）

由 ``reconcile_runner.launch_reconcile_async`` spawn 为 detached subprocess，
独立执行 post-commit reconciler 链路，结果写回 status file + reconcile_execution_log 表。

CLI
---
``python -m zephyr.governance.audit.reconcile_worker --payload <payload_path>``

payload file JSON schema
------------------------
::

    {
      "commit_sha": "abc123",
      "session_id": "sess-xxx",
      "project_root": "d:/ZephyrAlpha",
      "committed_files": ["d:/ZephyrAlpha/src/...", ...],
      "commit_message": "...",
      "started_at": 1234567890
    }

执行流程
--------
1. 读取 payload file（读后删）
2. 写 status=running
3. 构造 GitCommitGateway(project_root)
4. 调用 gateway._run_post_commit_reconcile_sync_worker(...)（不递归 spawn）
   - 内部走 reconcile_for + _log_reconcile_results（与同步路径相同）
5. 写 status=done（含 reconcilers_total/warn/auto_committed 统计）
6. 异常→写 status=failed（含 errors）→ exit 1

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: payload JSON 文件 一次性任务载荷
#   fields: commit_sha + session_id + project_root + committed_files + commit_message + started_at
#   code: --payload CLI 参数 main L362 / _load_payload L62
# 层: 算法
# - id: A1
#   name_zh: ① 载荷读取即焚
#   name_en: _load_payload
#   intro: 读 payload JSON 后立即删除文件，避免残留阻断下次 worker
#   desc: 文件不存在抛 FileNotFoundError；json.loads 后 finally 中 unlink（解析失败也删）
#   inputs: I1
#   outputs: payload dict
#   invariant: 读后即焚
# - id: A2
#   name_zh: ② status 状态机写入
#   name_en: write_status_file
#   intro: 按 pending→running→done/failed 流转写 status file，异常路径写 failed+errors
#   desc: 执行前写 running（含 worker_pid）；成功写 done（含 reconcilers_total/warn/auto_committed 统计）；gateway 构造或 reconcile_for 异常写 failed
#   inputs: A1
#   outputs: status file 状态记录
#   invariant: 状态流转 pending→running→done/failed
# - id: A3
#   name_zh: ③ worker 逻辑会话注册
#   name_en: _register_worker_session / _unregister_worker_session
#   intro: 把 worker 注册为 SessionRegistry 逻辑会话供并发控制，结束注销防泄漏
#   desc: worker_sid=worker-{sha8}-{pid}；注册失败 non-fatal；finally 中注销保持 list_active 准确
#   inputs: A2
#   outputs: worker_session_id
# - id: A4
#   name_zh: ④ 同步执行 reconciler 链路
#   name_en: gateway._run_post_commit_reconcile_sync_worker
#   intro: 构造 GitCommitGateway 后直接走同步 reconciler 链路，不再递归 spawn worker
#   desc: 注入 heartbeat 闭包（每 reconciler 执行前 write_heartbeat 刷新心跳，区分 live/死亡 worker）；走 reconcile_for + _log_reconcile_results
#   inputs: A3
#   outputs: reconcile_results 列表
# - id: A5
#   name_zh: ⑤ 告警自愈 clean 回写
#   name_en: _write_boot_success_clean / _write_stale_healed_clean
#   intro: worker 成功 boot / 超阈值后到达终态时，向 BOOT/STALE gate_id 写 clean 让历史 critical_warn 自动消解
#   desc: boot 成功写 RECONCILE-WORKER-BOOT clean；elapsed > _STALE_THRESHOLD_SECONDS 才写 RECONCILE-WORKER-STALE clean（快 worker 不写避免噪音）
#   inputs: A4
#   outputs: clean 记录
# 层: 输出
# - id: O1
#   name_zh: status file 与心跳
#   name_en: status file
#   intro: .runtime 下的 reconcile 状态与心跳文件，供外部观测 worker 存活与结果统计
#   downstream: reconcile_runner.launch_reconcile_async（[CONSUMERS] spawn 方轮询）
# - id: O2
#   name_zh: reconcile_execution_log 兜底记录
#   name_en: critical_warn / clean 记录
#   intro: worker 启动失败写 RECONCILE-WORKER-BOOT critical_warn；成功写 clean，补全告警生命周期对称
#   downstream: 内部治理告警生命周期（SQL_SELECT_ACTIVE_CRITICAL_WARNS）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A2 --> O1
# A5 --> O2
# A4 --> O1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path


def _load_payload(payload_path: str) -> dict:
    """读取 payload file 并删除（读后即焚，避免残留）。"""
    p = Path(payload_path)
    if not p.exists():
        raise FileNotFoundError(f"payload file not found: {payload_path}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    finally:
        # 读后即焚（即使 JSON 解析失败也删，避免残留阻断下次）
        try:
            p.unlink()
        except OSError:
            pass
    return data


def _write_failed_status(
    project_root: str,
    commit_sha: str,
    session_id: str,
    started_at: int,
    errors: list[str],
) -> None:
    """写 status=failed（worker 异常退出兜底）+ 持久化到 DB。

    #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：
    之前 worker 启动失败只写 status file，不写 reconcile_execution_log 表，
    违反"所有 reconciler 失败结果必须持久化记录"铁律。现补 DB 持久化。
    """
    try:
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_FAILED,
            write_status_file,
        )
        write_status_file(
            project_root, commit_sha, STATUS_FAILED,
            session_id=session_id,
            started_at=started_at,
            finished_at=int(time.time()),
            errors=errors,
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — 兜底日志失败不阻断 exit
        pass

    # 持久化 worker 启动失败到 reconcile_execution_log 表（铁律：失败结果必须持久化）
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        detail = "; ".join(errors) if errors else "worker boot failed (unknown reason)"
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="critical_warn",
                detail=f"reconcile_worker boot failed (commit={commit_sha}): {detail}",
                gate_id="RECONCILE-WORKER-BOOT",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — DB 写入失败不阻断 exit
        pass




def _write_boot_success_clean(
    project_root: str,
    commit_sha: str,
    session_id: str,
) -> None:
    """worker boot 成功 → 对 RECONCILE-WORKER-BOOT gate_id 写 clean 记录（自愈）。

    #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 治本（2026-07-21）：
    之前 worker 成功路径只写 status file（STATUS_DONE），不写 reconcile_execution_log
    clean 记录，导致 RECONCILE-WORKER-BOOT critical_warn 永不自愈（告警生命周期不对称：
    失败写 critical_warn，成功不写 clean）。本函数补全对称性——同样操作（worker boot）
    成功执行证明之前失败已解决，写 clean 记录使活跃告警自动消解。

    语义：仅对 RECONCILE-WORKER-BOOT gate_id 写 clean，不影响其他 gate_id 的告警。
    幂等：多次成功写多条 clean 记录无副作用（SQL_SELECT_ACTIVE_CRITICAL_WARNS 只需
    一条 clean 即可消解对应 critical_warn）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="clean",
                detail=(
                    f"reconcile_worker boot succeeded (commit={commit_sha}) "
                    f"— auto-selfheal of prior RECONCILE-WORKER-BOOT critical_warn"
                ),
                gate_id="RECONCILE-WORKER-BOOT",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — 自愈写入失败不阻断 worker 主流程
        pass

def _write_stale_healed_clean(
    project_root: str,
    commit_sha: str,
    session_id: str,
    started_at: int,
) -> None:
    """worker 到达终态（done/failed）且运行超阈值 → 写 RECONCILE-WORKER-STALE clean（自愈）。

    #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
    补全 RECONCILE-WORKER-STALE gate 的配对 clean 写入器（对齐 _write_boot_success_clean
    先例）。sweep 在 worker 超阈值运行时记 live-timeout critical_warn（真 active threat）；
    worker 到达终态后 stuck 条件结束——写 clean 使 SQL_AUTO_ACK_HEALED_BY_GATE 自然 ack
    历史 critical_warn，补全告警生命周期对称性（死孤儿 clean 由 sweep 收割时写，本函数
    补 worker 自然终态的 clean——两条 clean 路径覆盖 worker 生命周期的两种结束方式）。

    仅当 worker 实际运行超阈值时写——快 worker 不触发 live-timeout，无需 clean
    （避免每 commit 写一条噪音 clean）。幂等：多次写多条 clean 无副作用。
    """
    try:
        # 复用 reconcile_runner 阈值真源（同包私有常量，对齐 reconciler_health_gate
        # 跨模块复用 _check_recent_blocks 的先例，不复制阈值避免双真源漂移）。
        from zephyr.governance.audit.reconcile_runner import _STALE_THRESHOLD_SECONDS
        elapsed = int(time.time()) - started_at
        if elapsed <= _STALE_THRESHOLD_SECONDS:
            return  # 未超阈值，sweep 不会写 live-timeout critical_warn，无需自愈
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="clean",
                detail=(
                    f"reconcile_worker reached terminal state after {elapsed}s "
                    f"(>threshold {_STALE_THRESHOLD_SECONDS}s, commit={commit_sha}) "
                    f"— auto-selfheal of prior RECONCILE-WORKER-STALE live-timeout critical_warn"
                ),
                gate_id="RECONCILE-WORKER-STALE",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async_stale_healed",
        )
    except Exception:  # noqa: BLE001 — 自愈写入失败不阻断 worker 主流程
        pass

def _register_worker_session(project_root: str, commit_sha: str) -> str:
    """Register worker as a logical session in SessionRegistry.

    #ARCH-RECONCILER-WORKER-SESSION-001 Phase C (2026-07-22):
    Workers were not registered as sessions, causing:
    1. No concurrency control (unlimited parallel workers → resource exhaustion)
    2. Worker auto-commits flagged as "session not registered" (warn-only path)

    Returns:
        worker_session_id (worker-{sha8}-{pid}) for later unregister.
        Registration failure is non-fatal (worker still runs, just untracked).
    """
    worker_sid = f"worker-{commit_sha[:8]}-{os.getpid()}"
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        registry.register(worker_sid, pid=os.getpid())
    except Exception:  # noqa: BLE001 — registration failure doesn't block worker
        pass
    return worker_sid


def _unregister_worker_session(project_root: str, worker_sid: str) -> None:
    """Unregister worker session from SessionRegistry (best-effort cleanup).

    #ARCH-RECONCILER-WORKER-SESSION-001 Phase C (2026-07-22):
    Ensures worker sessions don't leak (TTL=3600s is long; explicit unregister
    on completion keeps list_active() accurate for concurrency control).
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        registry.unregister(worker_sid)
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------------------
# T2 worker 启动三证（#ARCH-RECONCILER-AUTO-DELETE-GOV-001，2026-08-14 裁定）
# ---------------------------------------------------------------------------

#: payload 新鲜度阈值（秒）——worker 是 commit 后立即 spawn，正常延迟秒级；
#: 超过 15min 的 payload 视为远古残留（wipe/重建后复活的陈旧负载），拒绝执行。
PAYLOAD_TTL_SECONDS = 15 * 60


def _check_worker_admission(payload: dict) -> tuple[bool, str]:
    """worker 启动三证：锚定存活 / payload 新鲜度 / session 活性（worktree 型）。

    病根（rogue worker PID 26288 实证，2026-08-14）：payload 锚定已删除的
    worktree 仍被 spawn 执行——启动准入零校验。S4 修了锚定解析，未修
    "该不该启动"。三证缺一拒启（写 failed status + 日志），理由：

    - 证1 锚定存活：payload 的 project_root 位于 .worktrees/<sid>/ 内时，
      该 worktree 根目录与 .git 指针文件必须存在（文件系统判定，确定性高）。
    - 证2 payload 新鲜度：now - started_at > PAYLOAD_TTL_SECONDS 拒启。
    - 证3 session 活性（仅 worktree 锚定型）：对应 sid 须在 SessionRegistry
      活跃；主仓 payload 免证3（协调会话 commit 后即退出是常态）。
      registry 读取异常时证3 降级放行（增强项不做底线），证1/证2 异常 fail-closed。

    Returns:
        (allowed, reason)：allowed=False 时 reason 为拒启原因。
    """
    project_root = str(payload.get("project_root", "") or "")
    started_at = int(payload.get("started_at") or 0)
    session_id = str(payload.get("session_id", "") or "")

    # 证2 payload 新鲜度（先做——最便宜且对所有类型生效）
    # epoch 秒比较：now_utc().timestamp() 替代 time.time()（DATETIME-NOW-FORBIDDEN 对齐）
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415 — 避免模块级循环

    now_epoch = int(now_utc().timestamp())
    if started_at and now_epoch - started_at > PAYLOAD_TTL_SECONDS:
        return False, (
            f"证2 payload 过期：started_at 距今 "
            f"{now_epoch - started_at}s > {PAYLOAD_TTL_SECONDS}s（远古负载拒启）"
        )

    # 证1 锚定存活（仅 worktree 锚定型）——判定口径：project_root 本身即
    # .worktrees/<sid> 根目录（父目录名=.worktrees）。禁止用"包含 .worktrees/ 段"
    # 判定：pytest/工具进程的 tmp 路径可能嵌套在宿主 worktree 之下
    # （.../.worktrees/<宿主>/.runtime/tmp/...），段匹配会误判宿主为锚定。
    p_root = Path(project_root)
    anchor_sid = ""
    if p_root.parent.name == ".worktrees":
        anchor_sid = p_root.name
        if not p_root.is_dir():
            return False, f"证1 锚定失效：worktree 目录不存在 {project_root}（疑已 abort/删除）"
        if not (p_root / ".git").exists():
            return False, (
                f"证1 锚定失效：worktree .git 指针不存在 {project_root} "
                f"（wipe/sweeper 机制后遗症，拒启防穿透主仓）"
            )

    # 证3 session 活性（仅 worktree 锚定型；registry 异常降级放行）
    #
    # 判定口径（2026-08-15 一次性进程竞态治本）：活跃 OR 近期活跃（宽限窗内
    # 有心跳记录）。原口径"仅当前活跃"对一次性 commit 进程系统性误杀——
    # claim_file auto-register 以网关 python pid 注册，git_commit.py 退出即
    # PID 死亡→list_active 收割，detached worker 启动（秒级）必然读不到活跃
    # 记录（086d0e24 worker 拒启实证，本任务的 4/5 commit 全部中招）。
    #
    # 安全性论证：证1 管 worktree 删除（文件系统判定），证2 管 payload 陈旧
    # （15min TTL），证3 宽限窗=PAYLOAD_TTL_SECONDS 与证2 对齐——"新鲜 payload
    # + 近期活跃 session"即合法；rogue 场景（锚定已删 worktree=证1 拦；远古
    # payload 复活=证2 拦；从未注册/远古 session 的新鲜 payload=本证拦）不 reopen。
    # 宽限窗取 load() 原始读（list_active 会收割死记录，拿不到"近期活跃"判据）。
    if anchor_sid:
        try:
            from zephyr.security.access_control.session_concurrency import (
                SessionInfo,
                SessionRegistry,
            )

            # 宿主仓根 = .worktrees/<sid> 上两级（与 strip_session_worktree 同义，
            # 但按父目录结构推导——嵌套 worktree 路径（宿主 worktree 内的 tmp
            # fake worktree）下段匹配剥离会锚错宿主）。
            main_root = p_root.parent.parent
            registry = SessionRegistry(main_root)
            raw = registry.load()  # 原始读：list_active 收割死记录后无法判"近期活跃"
            candidates = {anchor_sid, session_id}
            now_epoch_f = float(now_epoch)
            admitted_sids: set[str] = set()
            for sid in candidates & raw.keys():
                info = SessionInfo.from_dict(raw[sid])
                # ①当前活跃（PID 存活/心跳新鲜——长活 daemon 场景直通）
                from zephyr.security.access_control.session_concurrency import (  # noqa: PLC0415
                    _is_session_alive,
                )

                if _is_session_alive(info, now_epoch_f):
                    admitted_sids.add(sid)
                    continue
                # ②近期活跃宽限：心跳在 PAYLOAD_TTL_SECONDS 内（一次性 commit
                # 进程退出后 worker 秒级启动的正常窗口）
                if now_epoch_f - info.last_heartbeat <= PAYLOAD_TTL_SECONDS:
                    admitted_sids.add(sid)
            if not admitted_sids:
                return False, (
                    f"证3 session 无活跃/近期活跃记录：锚定 worktree 的会话 "
                    f"{anchor_sid}/{session_id} 在 registry 中无 {PAYLOAD_TTL_SECONDS}s "
                    f"内心跳（rogue worker 拒启）"
                )
        except Exception:  # noqa: BLE001 — registry 读取异常证3 降级放行
            pass

    return True, "三证齐全"


def _run_worker(payload: dict) -> int:
    """worker 主流程，返回 exit code（0=成功，1=失败）。"""
    from zephyr.governance.audit.reconcile_runner import (
        STATUS_DONE,
        STATUS_RUNNING,
        write_status_file,
    )

    commit_sha: str = payload.get("commit_sha", "")
    session_id: str = payload.get("session_id", "")
    project_root: str = payload.get("project_root", "")
    committed_files: list[str] = payload.get("committed_files", [])
    commit_message: str = payload.get("commit_message", "")
    started_at: int = payload.get("started_at") or int(time.time())

    # 治本 #ARCH-104：worker 经 WMI spawn 时 cwd 未必入 sys.path（通道偶然性），
    # reconciler 函数级 `from scripts.*` 导入（19 处）随即 ImportError
    # （GATE-RUNTIME-CLEANUP 实发失败）。显式装配 project_root，自给自足以绝后患。
    if project_root and project_root not in sys.path:
        sys.path.insert(0, project_root)

    if not commit_sha or not project_root:
        _write_failed_status(
            project_root or ".",
            commit_sha or "unknown",
            session_id,
            started_at,
            ["payload missing commit_sha or project_root"],
        )
        return 1

    # 0.5 T2 启动三证（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：
    #     锚定存活/payload 新鲜度/session 活性（worktree 型），缺一拒启。
    #     rogue worker（锚定已删 worktree 的 payload 仍执行）治本。
    admitted, deny_reason = _check_worker_admission(payload)
    if not admitted:
        from zephyr.shared.io.paths import anchor_main_root

        # status 落点按拒启类型分诊（#109 治本）：
        # - 证1（锚定失效）：worktree 目录可能已不存在 → 落主仓（原行为保留）；
        # - 证2/证3（锚定存活但拒启）：launch 已在 worktree 写 pending，failed 须同址
        #   落 worktree——否则 pending@worktree 永不更新、failed@主仓双文件分裂
        #   （外部观测即「worktree 状态文件未落盘」）。
        # anchor_main_root 单级父目录判定——嵌套 pytest tmp 库不误剥（同族陷阱根治）
        _wt_root = Path(project_root)
        status_root = str(_wt_root) if _wt_root.is_dir() else str(anchor_main_root(_wt_root))
        _write_failed_status(
            status_root, commit_sha, session_id, started_at,
            [f"worker 启动三证拒启: {deny_reason}"],
        )
        sys.stderr.write(f"reconcile_worker: admission denied: {deny_reason}\n")
        return 1

    # 0.6 T1② in-process 删除原语补丁（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：
    #     worker 是独立 python 进程——patch os/shutil 删除原语后，worker 内
    #     任何代码路径（含 40+ reconciler 及其调用链）的裸 stdlib 删除一律
    #     过 ops_guard 判定（保护区硬拦+全量审计），库层生效与进程无关。
    #     安装失败降级放行（reconciler 层 file_ops 上下文强制仍生效兜底）。
    try:
        from scripts.ops_guard import install_inprocess_enforcement

        install_inprocess_enforcement()
    except Exception as e:  # noqa: BLE001 — 补丁安装失败不阻断 worker（reconciler 层声明制兜底）
        sys.stderr.write(f"reconcile_worker: inprocess enforcement install degraded: {e}\n")

    # 1. 写 status=running
    write_status_file(
        project_root, commit_sha, STATUS_RUNNING,
        session_id=session_id,
        started_at=started_at,
        trigger_source="post_commit_async",
        worker_pid=os.getpid(),
    )

    # 1.5 注册为逻辑 session（#ARCH-RECONCILER-WORKER-SESSION-001 Phase C）
    #     使 launch_reconcile_async 能通过 list_active() 计数活跃 worker 实现并发控制。
    worker_sid = _register_worker_session(project_root, commit_sha)

    try:
        # 2. 构造 GitCommitGateway（注册全部 reconciler）
        try:
            # 延迟 import 避免 reconcile_runner import 时拉起 gateway
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
                GitCommitGateway,
            )
            gateway = GitCommitGateway(Path(project_root))
        except Exception as e:  # noqa: BLE001
            _write_failed_status(
                project_root, commit_sha, session_id, started_at,
                [f"GitCommitGateway init failed: {e}", traceback.format_exc()],
            )
            return 1

        # 3. 执行 reconciler 链路（直接调内部同步方法，不递归 spawn）
        #    _run_post_commit_reconcile_sync_worker 是 P2-3 新增的 worker-only 入口，
        #    跳过 async dispatch（避免 worker 自己又 spawn 一个 worker）。
        try:
            # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
            # 注入 heartbeat 闭包——每个 reconciler 执行前刷新 status file 心跳字段，
            # 使外部观测者可区分 live worker（心跳新鲜）与 死亡 worker（心跳陈旧）。
            from zephyr.governance.audit.reconcile_runner import write_heartbeat

            def _hb(gate_id: str, _root=project_root, _sha=commit_sha) -> None:
                write_heartbeat(_root, _sha, gate_id)

            reconcile_results = gateway._run_post_commit_reconcile_sync_worker(
                committed_files, session_id, commit_message,
                heartbeat=_hb,
            )
        except Exception as e:  # noqa: BLE001 — 兜底
            _write_failed_status(
                project_root, commit_sha, session_id, started_at,
                [f"reconcile_for failed: {e}", traceback.format_exc()],
            )
            return 1

        # 4. 统计结果
        total = len(reconcile_results)
        warn_count = sum(1 for r in reconcile_results if getattr(r, "action", "") == "warn")
        auto_count = sum(
            1 for r in reconcile_results if getattr(r, "action", "") == "auto_committed"
        )
        errors: list[str] = [
            getattr(r, "detail", "")
            for r in reconcile_results
            if getattr(r, "action", "") == "warn" and getattr(r, "detail", "")
        ]

        # 4.5 T2 删除/移动类动作全量落盘（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：
        #     worker stdio 已落盘 .runtime/logs/reconcile_worker_<sha>.log（S3），
        #     但原仅 warn 级摘要可见——删除/移动语义动作不论等级全部显式落盘，
        #     消除"clean 动作里藏着文件消失"的观测盲区（19:05 批次死因不可考教训）。
        _DELETE_HINTS = (
            "archiv", "recycl", "delet", "removed", "moved", "prune",
            "归档", "删除", "清理", "回收站",
        )
        for _r in reconcile_results:
            _action = getattr(_r, "action", "")
            _detail = getattr(_r, "detail", "") or ""
            _gate = getattr(_r, "gate_id", "?")
            if _action in ("auto_committed", "fix-in-place") or any(
                h in _detail for h in _DELETE_HINTS
            ):
                sys.stderr.write(
                    f"[DELETE-AUDIT] gate={_gate} action={_action} detail={_detail[:300]}\n"
                )

        # 5. 写 status=done
        write_status_file(
            project_root, commit_sha, STATUS_DONE,
            session_id=session_id,
            started_at=started_at,
            finished_at=int(time.time()),
            reconcilers_total=total,
            reconcilers_warn=warn_count,
            reconcilers_auto_committed=auto_count,
            errors=errors,
            trigger_source="post_commit_async",
            worker_pid=os.getpid(),
        )

        # 5.5 T2③ 审计覆盖率指标落盘（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：
        #     ops_guard in-process 补丁的判定/审计统计随 status 落盘，
        #     RECONCILER-HEALTH 消费校验覆盖率=100%（audit_failed>0 即缺口）。
        try:
            from scripts.ops_guard import get_audit_stats

            _audit_stats = get_audit_stats()
            if _audit_stats.get("judge_calls"):
                _status_path = (
                    Path(project_root) / ".runtime" / "reconcile_reports"
                    / f"reconcile_status_{commit_sha}.json"
                )
                if _status_path.is_file():
                    _data = json.loads(_status_path.read_text(encoding="utf-8"))
                    _data["ops_guard_audit_stats"] = _audit_stats
                    _status_path.write_text(
                        json.dumps(_data, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
        except Exception:  # noqa: BLE001 — 指标落盘失败不阻断 worker 终态
            pass

        # 6. 自愈写入：worker boot 成功 → 对 RECONCILE-WORKER-BOOT 写 clean 记录
        #    #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1：补全告警生命周期对称性
        _write_boot_success_clean(project_root, commit_sha, session_id)
        return 0
    finally:
        # #ARCH-RECONCILER-WORKER-SESSION-001 Phase C：确保 session 注销（防泄漏）
        _unregister_worker_session(project_root, worker_sid)


def main() -> int:
    """CLI 入口：``python -m zephyr.governance.audit.reconcile_worker --payload <path>``"""
    parser = argparse.ArgumentParser(
        prog="zephyr.governance.audit.reconcile_worker",
        description="Post-commit reconciler async worker (P2-3)",
    )
    parser.add_argument(
        "--payload", required=True,
        help="payload file path (JSON, read-once)",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.payload)
    except Exception as e:  # noqa: BLE001
        # payload 加载失败无法写 status（不知道 commit_sha/project_root），
        # 只能 stderr 报错 + exit 1
        sys.stderr.write(f"reconcile_worker: payload load failed: {e}\n")
        return 1

    return _run_worker(payload)


if __name__ == "__main__":
    sys.exit(main())

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def run_worker(payload) -> int:
    """公共接口：run_worker（Stage 4 公共化，委托到 _run_worker）。"""
    return _run_worker(payload)

