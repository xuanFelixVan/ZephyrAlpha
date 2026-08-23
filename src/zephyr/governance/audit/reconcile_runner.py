# [BLUEPRINT] MOD-GOV_RECONCILE_RUNNER | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] zephyr.governance.audit.reconcile_runner
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); subprocess; json; pathlib; zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway._run_post_commit_reconcile_async; AI 查询 reconcile 状态
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] status file 原子写入（tmp + os.replace）；subprocess 完全 detached（DETACHED_PROCESS on Windows / start_new_session on POSIX）；payload file 路径含 commit_sha 保证唯一；launch_reconcile_async 立即返回不阻塞；query_reconcile_status 失败 fail-open 返回 status=unknown
# [MODIFY-GUARD] launch_reconcile_async 函数签名；status file JSON schema（commit_sha/session_id/status/started_at/finished_at/errors/trigger_source）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] launch_reconcile_async 失败→ok=False 含 error，不抛异常；query_reconcile_status 失败→status=unknown 不抛异常
# [TESTS] tests/governance/audit/test_reconcile_async.py
# [A_module] module_id=MOD-GOV_RECONCILE_RUNNER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 commit 事件触发（非 cron/manual）
"""

reconcile_runner.py — Reconciler 链路异步化（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）

治本痛点
--------
post-commit reconciler 链路（30+ 个 reconciler）在 Windows 上同步执行耗时 30s-2min，
超过 AI 工具超时阈值被强制终止，但 git commit 本身已成功——导致 AI 误判为提交失败、
重复提交、触发 POST-COMMIT-GUARD 高基数阻断。

治本方案
--------
1. commit 成功后**立即返回**，reconciler 链路在 detached subprocess 后台执行
2. status file（``.runtime/reconcile_reports/reconcile_status_<sha>.json``）持久化执行状态
3. AI 可通过 ``query_reconcile_status`` API 查询执行进度，不阻塞主流程

API
---
- ``launch_reconcile_async``：spawn detached worker subprocess
- ``query_reconcile_status``：读取 status file，返回执行状态
- ``write_status_file`` / ``read_status_file``：底层 helper（worker 内部用）

Worker 入口
-----------
``python -m zephyr.governance.audit.reconcile_worker --payload <payload_path>``

设计裁定
--------
- **status file 而非 DB**：reconcile_execution_log 表记历史结果，status file 记运行时
  状态（running/done/failed），两者互补。DB 写入有锁开销，status file 更轻量。
- **payload file 而非 CLI args**：committed_files 列表可能很长，CLI args 有长度限制。
  payload file 路径含 commit_sha 保证唯一，worker 读取后立即删除。
- **DETACHED_PROCESS**：父进程（AI session）退出不影响 worker；worker 通过
  SessionRegistry 文件共享读父 session 的注册信息（但 PID 不同，session PID liveness
  检查可能失败——这是已知限制，worker auto-commit 会走 warn-only 路径）。
- **不获取 _GlobalCommitLock**：worker 内部 reconciler auto-commit 通过 gateway 走
  正常锁流程，不绕过；这是 P2-3 与 P2-1 emergency_commit 的关键区别。

已知限制（非 P2-3 范围）
------------------------
- 父 AI session 在 worker 完成前 unregister 会导致 worker auto-commit 被判为
  "session 未注册"（warn-only，仍记录到 reconcile_execution_log）。
- worker crash 在 status file 未更新到 done/failed 时，下次 query 返回 "stale"。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: commit 上下文参数
#   fields: project_root/commit_sha/session_id/committed_files/commit_message
#   code: launch_reconcile_async 参数 L487-493
# - id: I2
#   name: reconcile 状态文件
#   fields: .runtime/reconcile_reports/reconcile_status_*.json（status/started_at/last_heartbeat_at/worker_pid 等）
#   code: _status_file_path L145
# - id: I3
#   name: SessionRegistry 活跃会话
#   fields: worker-* 前缀的逻辑 session 列表
#   code: _count_inflight_workers L706
# 层: 算法
# - id: A1
#   name_zh: ① 孤儿 worker 清扫
#   name_en: sweep_stale_workers
#   intro: 扫描 running/pending 状态文件，进程已死的改写为 stale，超龄终态文件顺带删除
#   desc: running 且超 30min：PID 死→改 stale+落 DB 记 clean（自愈），PID 活→仅落 DB 记 critical_warn 不改文件；pending 超 120s 且 PID 死→改 stale（spawn 即死兜底观测，#ARCH-SPAWN-JOB-KILL-001）；done/failed/stale 超 7d 删除
#   inputs: I2
#   outputs: 本次 sweep 标记 stale 的文件数
# - id: A2
#   name_zh: ② 并发闸门
#   name_en: _count_inflight_workers
#   intro: 在途 worker（已注册 ∪ 新鲜 pending/running status）达到上限就跳过本次 spawn，防止进程爆炸
#   desc: 计数口径=SessionRegistry worker-* 会话 ∪ launcher 锁内同步写的新鲜 pending status（按 sha8 去重），CAND-GOVSEC-001 ④ 闭合 spawn 前 TOCTOU 缝隙；>=MAX_CONCURRENT_WORKERS(2) → status=skipped 返回；查询失败 fail-open 归 0；launch 临界区整体由 _acquire_launch_lock 跨进程文件锁互斥
#   inputs: I1 I3
#   outputs: 活跃 worker 计数
# - id: A3
#   name_zh: ③ 原子状态写入
#   name_en: write_status_file
#   intro: 用临时文件加原子替换写 status/payload，杜绝半写状态
#   desc: tmp.write + os.replace 原子落盘；payload 文件路径含 commit_sha 保证唯一
#   inputs: I1
#   outputs: status/payload 文件路径
#   invariant: status file 原子写入（tmp + os.replace）
# - id: A4
#   name_zh: ④ detached worker 启动
#   name_en: launch_reconcile_async
#   intro: commit 后立即返回，reconciler 链路丢给完全脱离的子进程后台跑
#   desc: 先 sweep 再并发闸门 → 写 payload+pending → spawn_python_hidden 启动 reconcile_worker；ZEPHYR_RECONCILE_SYNC=1 + ZEPHYR_RECONCILE_WORKER=1 防递归重跑；spawn 失败改 failed 供调用方回退 sync
#   inputs: I1 A1 A2 A3
#   outputs: 启动结果 dict（ok/status/worker_pid/payload_file/status_file）
#   invariant: 立即返回不阻塞；subprocess 完全 detached
# - id: A5
#   name_zh: ⑤ 僵尸判定读取
#   name_en: read_status_file
#   intro: 读状态文件时对超时 running 做死活判定，死孤儿改判 stale
#   desc: reference=heartbeat 或 started_at 超 30min：PID 活→落 DB critical_warn 不改文件，PID 死→改 stale 落 DB clean；双 set 去重保自愈闭环
#   inputs: I2
#   outputs: ReconcileStatus（含 stale 改判）
# - id: A6
#   name_zh: ⑥ 执行状态查询
#   name_en: query_reconcile_status
#   intro: AI 查 reconciler 链路跑到哪了，不阻塞主流程
#   desc: 读 status file 组装查询结果；elapsed=finished-started 或 now-started；文件缺失 fail-open 返回 status=unknown
#   inputs: A5
#   outputs: 状态查询结果 dict
#   invariant: 查询失败 fail-open 返回 unknown
# 层: 输出
# - id: O1
#   name_zh: 异步启动结果 dict
#   name_en: launch_reconcile_async 返回值
#   intro: ok/pending/skipped/failed 启动回执，commit 流程据此立即继续
#   downstream: GitCommitGateway._run_post_commit_reconcile_async MOD-INF-035
# - id: O2
#   name_zh: 状态文件与查询结果
#   name_en: reconcile_status_*.json / query_reconcile_status 返回值
#   intro: status file 持久化运行时状态，payload 供 worker 读取后自删，AI 可查询进度
#   downstream: reconcile_worker 子进程（读 payload 自删）+ AI 查询 reconcile 状态
# [/ALGO_FLOW]
#
# 边:
# I1 --> A2
# I1 --> A3
# I2 --> A1
# I2 --> A5
# I3 --> A2
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> O1
# A3 --> O2
# A5 --> A6
# A6 --> O2
"""

from __future__ import annotations

__all__ = [
    "STATUS_DONE",
    "STATUS_FAILED",
    "STATUS_PENDING",
    "STATUS_RUNNING",
    "STATUS_STALE",
    "STATUS_UNKNOWN",
    "ReconcileStatus",
    "launch_reconcile_async",
    "query_reconcile_status",
    "read_status_file",
    "write_status_file",
    "write_heartbeat",  # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）
    "sweep_stale_workers",  # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）
]

import contextlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, TypedDict

from zephyr.shared.infra.process_pool import is_pid_alive, spawn_python_hidden
from zephyr.shared.io.paths import REPO_ROOT

# #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
# 跨平台进程探活真源唯一（process_pool.is_pid_alive），此处仅做私有别名供
# sweep_stale_workers 使用 + 测试通过 _is_pid_alive 导入验证语义。禁止重复造轮子。
_is_pid_alive = is_pid_alive

# Status 枚举（字符串常量，避免 enum 序列化复杂度）
STATUS_PENDING: str = "pending"  # 已 spawn subprocess，worker 尚未启动
STATUS_RUNNING: str = "running"  # worker 已启动，正在执行 reconciler
STATUS_DONE: str = "done"  # 全部 reconciler 执行完成
STATUS_FAILED: str = "failed"  # worker 异常退出
STATUS_STALE: str = "stale"  # running 超 30min，疑似僵尸
STATUS_UNKNOWN: str = "unknown"  # status file 不存在（commit 早于 P2-3 / 未触发 async）

# 僵尸判定阈值（秒）——running 状态超此时长视为 stale
_STALE_THRESHOLD_SECONDS: int = 1800  # 30 分钟

# #ARCH-SPAWN-JOB-KILL-001（2026-08-14）：pending 即死检测阈值。
# spawn 成功的 worker 应在数秒内把 status 翻为 running；超 120s 仍 pending
# 且 worker_pid 已死 = spawn 传输层失败（如 Job Object kill-on-close 连坐）。
# 120s 对齐"worker 启动 + import zephyr 依赖链"的最坏耗时，避免误判慢启动。
_PENDING_DEAD_THRESHOLD_SECONDS: int = 120

# #ARCH-RECONCILER-WORKER-SESSION-001 Phase C（2026-07-22）：
# 并发 worker 上限——防止每次 commit spawn 一个 worker 导致资源耗尽。
# worker 注册为逻辑 session（worker-{sha8}-{pid}），launch_reconcile_async
# 通过 SessionRegistry.list_active() 计数活跃 worker，超限则跳过 spawn（fail-open）。
MAX_CONCURRENT_WORKERS: int = 2

# Status / payload 文件目录
_REPORTS_SUBDIR: str = ".runtime/reconcile_reports"

# 治本（#ARCH-HEARTBEAT-001-TEST-FAIL 同类）：保持 detached worker Popen 引用，
# 避免 GC 回收触发 Popen.__del__ ResourceWarning（pytest filterwarnings=error 转为失败）。
# worker 是 detached 进程，不应 wait——只需保持引用防止 GC。
_WORKER_PROCS: dict[str, "subprocess.Popen[bytes]"] = {}


class ReconcileStatus(TypedDict, total=False):
    """reconciler 链路异步执行状态（status file JSON schema）。"""

    commit_sha: str
    session_id: str
    status: str  # STATUS_* 常量之一
    started_at: int  # Unix timestamp（spawn 时间）
    finished_at: int  # Unix timestamp（done/failed 时间，未完成=0）
    reconcilers_total: int  # 已执行 reconciler 总数（done 时填）
    reconcilers_warn: int  # warn 结果数
    reconcilers_auto_committed: int  # auto_commit 结果数
    errors: list[str]  # 失败原因列表
    trigger_source: str  # "post_commit_async"
    worker_pid: int  # worker subprocess PID


def _reports_dir(project_root: Path | str) -> Path:
    """获取 reports 目录（自动创建）。"""
    root = Path(project_root) if not isinstance(project_root, Path) else project_root
    d = root / _REPORTS_SUBDIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _status_file_path(project_root: Path | str, commit_sha: str) -> Path:
    """status file 路径（不创建）。"""
    root = Path(project_root) if not isinstance(project_root, Path) else project_root
    # commit_sha 可能是短 SHA（7-12 字符）或长 SHA（40 字符），统一原样使用
    safe_sha = commit_sha.replace("/", "_").replace("\\", "_").strip()
    return root / _REPORTS_SUBDIR / f"reconcile_status_{safe_sha}.json"


def _payload_file_path(project_root: Path | str, commit_sha: str) -> Path:
    """payload file 路径（worker 读取后删除）。"""
    root = Path(project_root) if not isinstance(project_root, Path) else project_root
    safe_sha = commit_sha.replace("/", "_").replace("\\", "_").strip()
    return root / _REPORTS_SUBDIR / f"reconcile_payload_{safe_sha}.json"


def write_status_file(
    project_root: Path | str,
    commit_sha: str,
    status: str,
    *,
    session_id: str = "",
    started_at: int = 0,
    finished_at: int = 0,
    reconcilers_total: int = 0,
    reconcilers_warn: int = 0,
    reconcilers_auto_committed: int = 0,
    errors: list[str] | None = None,
    trigger_source: str = "post_commit_async",
    worker_pid: int = 0,
) -> Path:
    """原子写入 status file（tmp + os.replace）。

    Args:
        project_root: 项目根目录。
        commit_sha: commit SHA（用于文件名）。
        status: STATUS_* 常量之一。
        其余字段：见 ``ReconcileStatus`` TypedDict。

    Returns:
        status file Path（已写入）。
    """
    _reports_dir(project_root)  # 确保 dir 存在
    path = _status_file_path(project_root, commit_sha)
    payload: ReconcileStatus = {
        "commit_sha": commit_sha,
        "session_id": session_id,
        "status": status,
        "started_at": started_at or int(time.time()),
        "finished_at": finished_at,
        "reconcilers_total": reconcilers_total,
        "reconcilers_warn": reconcilers_warn,
        "reconcilers_auto_committed": reconcilers_auto_committed,
        "errors": errors or [],
        "trigger_source": trigger_source,
        "worker_pid": worker_pid,
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)  # 原子替换
    return path


def read_status_file(project_root: Path | str, commit_sha: str) -> ReconcileStatus | None:
    """读取 status file，不存在返回 None。

    含僵尸判定：status=running 且 started_at 超过 ``_STALE_THRESHOLD_SECONDS``
    自动改判为 ``STATUS_STALE``（不修改文件，仅返回值变更）。

    #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：
    僵尸判定时持久化到 reconcile_execution_log 表（铁律：所有 reconciler
    失败结果必须持久化记录，且错误详情不允许截断）。用内存 set 去重避免
    重复写入（每个 commit_sha 只记录一次）。
    """
    path = _status_file_path(project_root, commit_sha)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    # 僵尸判定
    if data.get("status") == STATUS_RUNNING:
        # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
        # 优先看心跳（更精确），无心跳回退看 started_at；超阈值时探测进程存活——
        # live worker（如慢 reconciler 重建 72 域文档需 9 分钟）不算 stale，
        # 与 sweep_stale_workers 判定逻辑一致。无 worker_pid 或进程已死才标 stale。
        # #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
        # live-over-threshold（PID 存活）虽不标 stale（worker 仍在运行），但落 DB
        # 记 critical_warn（真 active threat）——原此处静默放行是 fail-silent。
        heartbeat_at = data.get("last_heartbeat_at", 0)
        started = data.get("started_at", 0)
        reference_time = heartbeat_at or started
        if reference_time and (int(time.time()) - reference_time > _STALE_THRESHOLD_SECONDS):
            worker_pid = data.get("worker_pid", 0)
            if worker_pid and _is_pid_alive(worker_pid):
                # 活进程超时：不标记 stale（worker 仍在运行），落 DB 记 critical_warn
                _log_stale_to_db(project_root, commit_sha, started, data)
            else:
                # 死孤儿：标记 stale + 落 DB（clean 自愈）
                data["status"] = STATUS_STALE
                _log_stale_to_db(project_root, commit_sha, started, data)
    return data  # type: ignore[return-value]


# 已记录到 DB 的 stale commit_sha 集合（内存去重，进程级）
# #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
# dedup 按 action 分裂——同一 sha 生命周期可先 live-timeout（critical_warn）后
# dead-orphan/终态（clean），单 set 会使 clean 被 critical_warn 去重跳过，断裂
# 自愈闭环。双 set 允许同一 sha 各记一次 critical_warn + clean，配对自愈。
_stale_live_logged: set[str] = set()  # 活进程超时 critical_warn 去重
_stale_dead_logged: set[str] = set()  # 死孤儿 clean 去重


def _log_stale_to_db(
    project_root: Path | str,
    commit_sha: str,
    started_at: int,
    status_data: dict,
) -> None:
    """持久化 stale 状态到 reconcile_execution_log 表（幂等，按 action 各记一次）。

    #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：
    之前 stale 状态只在 read_status_file 返回值中标记，不写 DB，AI 查询
    reconcile_execution_log 表看不到 stale 事件，违反持久化铁律。

    #ARCH-RECONCILE-WORKER-STALE-SEVERITY-001 治本（2026-08-01）：
    严重度按 PID 存活分裂——死孤儿记 ``clean``（自愈成功，不进 critical_warn
    banner），活进程超时记 ``critical_warn``（真 active threat）。

    #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
    激活活进程超时检测路径——read_status_file / sweep_stale_workers 对 live-over-
    threshold worker 调本函数（命中活进程分支→critical_warn），打通原防御性死代码。
    dedup 拆双 set（_stale_live_logged / _stale_dead_logged）：同一 sha 可先
    critical_warn（live）后 clean（dead-orphan 收割 / worker 终态 _write_stale_healed_clean），
    单 set 会断自愈闭环。配对 clean 由 reconcile_worker 终态写入器补全（对齐 BOOT 先例）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )

        elapsed = int(time.time()) - started_at  # noqa: m46-time  M46豁免: 与本文件既有 time.time() 风格一致（5处既有调用），stale 判定需 Unix timestamp 整数差值
        session_id = status_data.get("session_id", "unknown")
        worker_pid = status_data.get("worker_pid", 0)
        # R1 治本（#ARCH-RECONCILE-WORKER-HEARTBEAT-001，2026-08-01）：
        # 区分死进程孤儿 vs 活进程超时，消除"running for {elapsed}s"误导——
        # 死进程不可能"running"，实际是"died {elapsed}s ago"。
        # #ARCH-RECONCILE-WORKER-STALE-SEVERITY-001 / -LIVE-TIMEOUT-001 治本：
        # 严重度按 PID 存活分裂——活进程=真 active threat（critical_warn），
        # 死孤儿=已自愈（clean）。两调用方（read_status_file / sweep_stale_workers）
        # 均对 live-over-threshold + dead-orphan 两类调本函数（LIVE-TIMEOUT-001 激活）。
        if worker_pid and _is_pid_alive(worker_pid):
            # 活进程超时：真正的 active threat（慢/卡死 reconciler）。
            # #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
            # 此分支原为防御性死代码（调用方仅 PID 已死才调），现激活——sweep/
            # read_status_file 对 live-over-threshold worker 调本函数命中此分支。
            # critical_warn 是正确严重度（真威胁）；配对 clean 在 worker 到达终态
            # （done/failed）且超阈值时由 _write_stale_healed_clean 写入，自愈闭环。
            if commit_sha in _stale_live_logged:
                return
            detail = (
                f"live worker timeout (pid={worker_pid}, running {elapsed}s, "
                f"threshold={_STALE_THRESHOLD_SECONDS}s, commit_sha={commit_sha}) — "
                f"investigate slow reconciler"
            )
            stale_action = "critical_warn"
            dedup_set = _stale_live_logged
        else:
            # 死进程孤儿：收割即自愈完成——status file 已改写为 stale，瞬时陈旧
            # 由下轮 reconcile 覆盖（reconciler 幂等，按当前态重算）。
            # #ARCH-RECONCILE-WORKER-STALE-SEVERITY-001 治本（2026-08-01）：
            # 记 critical_warn 是语义倒置（"问题已自愈那一刻当严重失败上报"），
            # 违反"告警 MUST 精确"与"永久系统必须全自动"。降为 clean（自愈成功，
            # 对齐 RECONCILE-WORKER-BOOT 先例）：不进 banner，且 SQL_AUTO_ACK_HEALED_BY_GATE
            # 会自然 ack 该 gate 历史 critical_warn——补全自愈闭环。
            if commit_sha in _stale_dead_logged:
                return
            detail = (
                f"self-heal: orphaned worker reaped (dead pid={worker_pid}, "
                f"died {elapsed}s ago, threshold={_STALE_THRESHOLD_SECONDS}s, "
                f"commit_sha={commit_sha}) — status file cleaned, no active threat; "
                f"transient artifact staleness covered by next reconcile cycle"
            )
            stale_action = "clean"
            dedup_set = _stale_dead_logged
        _log_reconcile_results(
            project_root,
            [
                ReconcileResult(
                    action=stale_action,
                    detail=detail,
                    gate_id="RECONCILE-WORKER-STALE",
                )
            ],
            session_id,
            trigger_source="post_commit_async_stale",
        )
        dedup_set.add(commit_sha)
    except Exception:  # noqa: BLE001 — DB 写入失败不影响 stale 判定
        pass


def write_heartbeat(
    project_root: Path | str,
    commit_sha: str,
    current_reconciler: str,
) -> None:
    """#ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）。

    刷新 status file 的心跳字段（``last_heartbeat_at`` + ``current_reconciler``），
    其余字段从现有文件读取保持不变（避免覆盖 worker 期间由其他路径写入的字段）。
    心跳只在 ``status=running`` 期间写入；文件不存在 / 非 running / 解析失败时静默跳过
    （心跳是 best-effort liveness 信号，不能阻断 reconciler 主流程）。
    """
    try:
        path = _status_file_path(project_root, commit_sha)
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status") != STATUS_RUNNING:
            return  # 仅 running 期间刷新心跳
        data["last_heartbeat_at"] = int(time.time())
        data["current_reconciler"] = current_reconciler
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)
    except Exception:  # noqa: BLE001 — 心跳是 best-effort，不阻断主流程
        pass


def sweep_stale_workers(project_root: Path | str) -> int:
    """主动扫描 + 改写孤儿 worker status file。

    #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
    之前的僵尸检测是惰性的（仅 ``read_status_file`` 被调用时触发，且不改文件），
    且 ``launch_reconcile_async`` 不遍历已有 running 文件——导致一个 worker 死亡后
    它的 status file 永久停留 running，无人 query 即永不标 stale（孤儿累积）。

    本函数遍历所有 ``reconcile_status_*.json``，对 running 且超阈值的 worker：
    1. 探测 ``worker_pid`` 是否存活（``_is_pid_alive``）
    2. 进程已死 → 改写 status file 为 ``stale``（errors 含 ``orphaned_worker_dead``）+ 落 DB
    3. 进程存活但心跳超时 → 不改写（live worker 正在执行慢 reconciler，误判会破坏正在运行的 worker）

    #ARCH-SPAWN-JOB-KILL-001（2026-08-14）增补 pending 分支：
    pending 超 ``_PENDING_DEAD_THRESHOLD_SECONDS`` 且 worker_pid 已死 → 改写 stale
    （errors 含 ``spawn_dead_pending``）+ 落 DB——spawn 传输层失败（Job Object
    kill-on-close 连坐等）的兜底观测，消除"pending 永驻不可见"静默缺失。

    在 ``launch_reconcile_async`` 入口调用（每次新 commit 顺带清扫，O(n) n 小）。

    Returns:
        本次 sweep 标记为 stale 的文件数。
    """
    try:
        reports_dir = _reports_dir(project_root)
    except Exception:  # noqa: BLE001 — 目录不可创建等
        return 0

    swept = 0
    now = int(time.time())
    for status_path in reports_dir.glob("reconcile_status_*.json"):
        try:
            data = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("status") == STATUS_PENDING:
            # #ARCH-SPAWN-JOB-KILL-001 治本（2026-08-14）：pending 即死检测。
            # spawn 传输层失败（Job Object kill-on-close 连坐等）时 worker 从未
            # 启动，status 永驻 pending——原 sweep 只扫 running，此类失败完全
            # 不可见（2026-08-13~14 实证 10+ commit 静默缺失）。此处兜底观测：
            # pending 超阈值 + worker_pid 已死 → 标 stale + 落 DB（死孤儿=clean
            # 自愈语义，#ARCH-RECONCILE-WORKER-STALE-SEVERITY-001）。
            pending_started = data.get("started_at", 0)
            if not pending_started or now - pending_started <= _PENDING_DEAD_THRESHOLD_SECONDS:
                continue  # 无时间基准 / 未超阈值（worker 可能正在启动），跳过
            pending_pid = data.get("worker_pid", 0)
            if pending_pid and _is_pid_alive(pending_pid):
                continue  # PID 存活（含 PID 复用）——不碰
            pending_sha = data.get("commit_sha", "")
            pending_errors = list(data.get("errors", []))
            pending_errors.append(
                f"spawn_dead_pending: worker never flipped to running, "
                f"pid={pending_pid} dead, started={pending_started}, "
                f"pending_threshold={_PENDING_DEAD_THRESHOLD_SECONDS}s"
            )
            write_status_file(
                project_root,
                pending_sha,
                STATUS_STALE,
                session_id=data.get("session_id", ""),
                started_at=pending_started,
                finished_at=now,
                reconcilers_total=data.get("reconcilers_total", 0),
                reconcilers_warn=data.get("reconcilers_warn", 0),
                reconcilers_auto_committed=data.get("reconcilers_auto_committed", 0),
                errors=pending_errors,
                trigger_source=data.get("trigger_source", "post_commit_async"),
                worker_pid=pending_pid,
            )
            swept += 1
            _log_stale_to_db(project_root, pending_sha, pending_started, data)
            continue
        if data.get("status") != STATUS_RUNNING:
            continue
        # 判定是否超阈值：优先看心跳（更精确），无心跳回退看 started_at
        heartbeat_at = data.get("last_heartbeat_at", 0)
        started_at = data.get("started_at", 0)
        reference_time = heartbeat_at or started_at
        if not reference_time:
            continue  # 无时间基准，跳过
        if now - reference_time <= _STALE_THRESHOLD_SECONDS:
            continue  # 未超阈值，跳过
        # 超阈值：探测进程是否存活
        worker_pid = data.get("worker_pid", 0)
        commit_sha = data.get("commit_sha", "")
        if not worker_pid:
            continue  # 无 PID，无法判定存活，跳过
        if _is_pid_alive(worker_pid):
            # #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
            # 活进程超时：不改写 status file（不破坏运行中 worker），仅落 DB 记
            # critical_warn（真 active threat）。原此处 continue 静默放行是 fail-silent。
            _log_stale_to_db(project_root, commit_sha, started_at, data)
            continue
        # 进程已死 → 改写为 stale
        session_id = data.get("session_id", "")
        existing_errors = list(data.get("errors", []))
        existing_errors.append(
            f"orphaned_worker_dead: pid={worker_pid} dead, "
            f"last_heartbeat={heartbeat_at}, started={started_at}, "
            f"stale_threshold={_STALE_THRESHOLD_SECONDS}s"
        )
        write_status_file(
            project_root,
            commit_sha,
            STATUS_STALE,
            session_id=session_id,
            started_at=started_at,
            finished_at=now,
            reconcilers_total=data.get("reconcilers_total", 0),
            reconcilers_warn=data.get("reconcilers_warn", 0),
            reconcilers_auto_committed=data.get("reconcilers_auto_committed", 0),
            errors=existing_errors,
            trigger_source=data.get("trigger_source", "post_commit_async"),
            worker_pid=worker_pid,
        )
        swept += 1
        # 落 DB（与 read_status_file 的 _log_stale_to_db 一致，幂等去重）
        _log_stale_to_db(project_root, commit_sha, started_at, data)

    # R2 治本（#ARCH-RECONCILE-WORKER-HEARTBEAT-001，2026-08-01）：
    # 清理超龄的终态 status 文件（done/failed/stale），防止无限累积。
    # 当前 259+ 文件只增不减，每次 launch_reconcile_async 顺带清理（O(n)，n 小）。
    _DONE_RETENTION_SECONDS = 86400 * 7  # 7 天
    for status_path in reports_dir.glob("reconcile_status_*.json"):
        try:
            ttl_data = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if ttl_data.get("status") not in (STATUS_DONE, STATUS_FAILED, STATUS_STALE):
            continue  # 只清理终态文件，不碰 running/pending
        finished = ttl_data.get("finished_at", 0)
        if not finished:
            continue  # 无完成时间，保守不删
        if now - finished > _DONE_RETENTION_SECONDS:
            try:
                status_path.unlink(missing_ok=True)
            except OSError:
                pass  # fail-open，清理失败不阻断 launch
    return swept


# ----------------------------------------------------------------------------
# CAND-GOVSEC-001 ④（2026-08-23 src 误删取证 §5.5）：worker 并发闸门文件锁互斥
#
# 病根（worker A/B 并发重叠 61 秒实证）：旧闸门只数 SessionRegistry 已注册
# worker，而注册发生在 worker 子进程启动之后——两笔 commit 间隔小于 worker
# 启动注册耗时时双双通过闸门（TOCTOU 缝隙）。治本两层：
#   1. launch 临界区（计数+写 pending+spawn）跨进程文件锁互斥——第二个
#      launcher 在锁内必看到第一个刚写的 pending status；
#   2. 计数口径扩为「已注册 worker ∪ 新鲜 pending/running status file」——
#      pending status 是 launcher 在锁内同步写的（spawn 前），计数不依赖
#      worker 子进程的注册时机，缝隙物理闭合。
# ----------------------------------------------------------------------------

#: launch 临界区互斥锁文件（相对 project_root；.runtime 已 gitignore）
_LAUNCH_LOCK_REL: str = ".runtime/reconcile_launch.lock"

#: 锁获取超时（秒）——持锁进程崩溃时 OS 随句柄关闭自动释放，超时只是慢路径
#: 兜底；超时后 fail-open 继续 launch（post-commit best-effort 不阻断 commit）。
_LAUNCH_LOCK_TIMEOUT_SECONDS: float = 10.0


@contextlib.contextmanager
def _acquire_launch_lock(root: Path):
    """跨进程文件锁（launch 临界区互斥）。

    Windows=msvcrt.locking 非阻塞重试；POSIX=fcntl.flock LOCK_EX|LOCK_NB。
    持锁进程崩溃时句柄随进程消亡由 OS 释放（无永久死锁）。
    fail-open：锁文件不可创建/超时未拿到 → yield False（降级无锁继续，
    不阻断 commit——与旧行为同平面，不差于现状）。

    Yields:
        bool: True=本次真正持锁；False=降级无锁。
    """
    fh = None
    locked = False
    try:
        lock_path = root / _LAUNCH_LOCK_REL
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(lock_path, "a+b")  # noqa: SIM115 — 锁句柄生命周期随本 with 块
        deadline = time.monotonic() + _LAUNCH_LOCK_TIMEOUT_SECONDS
        while not locked and time.monotonic() < deadline:
            try:
                if os.name == "nt":
                    import msvcrt

                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except OSError:
                time.sleep(0.05)  # 锁被持有——短重试直至超时
    except OSError:
        fh = None  # 锁文件不可创建（权限/盘满）→ 降级无锁
    try:
        yield locked
    finally:
        if fh is not None:
            if locked:
                try:
                    if os.name == "nt":
                        import msvcrt

                        fh.seek(0)
                        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
            fh.close()


def _count_inflight_workers(project_root: str) -> int:
    """并发闸门计数（CAND-GOVSEC-001 ④）：已注册 worker ∪ 新鲜 pending/running status。

    旧口径只数 SessionRegistry 已注册 worker，注册发生在 worker 子进程启动后，
    两笔紧邻 commit 双双过闸（A/B 重叠 61s 实证）。新口径把 launcher 在锁内
    同步写的 pending status file 计入——spawn 前的注册窗口缝隙物理闭合。

    计数规则（按 commit_sha[:8] 去重，防注册+status 双记同一 worker）：
    - SessionRegistry 活跃 worker-* 会话（worker-{sha8}-{pid}）→ 计 sha8；
    - status=pending 且 age < _PENDING_DEAD_THRESHOLD_SECONDS：无 pid（spawn 前
      窗口，缝隙本体）或 pid 存活 → 计入；超龄/死 pid 由 sweep_stale_workers
      处置，不计；
    - status=running 且 worker_pid 存活 → 计入；死 pid/无 pid 不计（sweep 兜底）；
    - 一切读取异常 fail-open 跳过该条（宁可少计放过，不可多计误杀——闸门
      本就是 best-effort 资源保护）。
    """
    shas: set[str] = set()
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(project_root)
        for s in registry.list_active():
            sid = s.session_id
            if sid.startswith("worker-"):
                parts = sid.split("-")
                if len(parts) >= 2 and parts[1]:
                    shas.add(parts[1])
    except Exception:  # noqa: BLE001 — fail-open
        pass
    try:
        reports = Path(project_root) / _REPORTS_SUBDIR
        now = time.time()
        for status_path in reports.glob("reconcile_status_*.json"):
            try:
                data = json.loads(status_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            status = data.get("status")
            if status not in (STATUS_PENDING, STATUS_RUNNING):
                continue
            started = float(data.get("started_at", 0) or 0)
            pid = int(data.get("worker_pid", 0) or 0)
            if status == STATUS_PENDING:
                if not started or now - started > _PENDING_DEAD_THRESHOLD_SECONDS:
                    continue  # 无时间基准/超龄 pending 由 sweep 处置，不计
                if pid and not _is_pid_alive(pid):
                    continue  # pending 即死（spawn 传输层失败）——sweep 会清
                # 新鲜 pending（含无 pid 的 spawn 前窗口）→ 计入
            else:  # STATUS_RUNNING
                if not pid or not _is_pid_alive(pid):
                    continue  # 死 worker 尸体不计（sweep 兜底清理）
            sha = str(data.get("commit_sha", "")).strip()
            if sha:
                shas.add(sha[:8])
    except OSError:  # noqa: BLE001 — fail-open
        pass
    return len(shas)


def launch_reconcile_async(
    project_root: Path | str,
    commit_sha: str,
    session_id: str,
    committed_files: list[str],
    commit_message: str = "",
) -> dict:
    """异步启动 reconciler 链路（spawn detached worker subprocess）。

    Args:
        project_root: 项目根目录。
        commit_sha: 本次 commit 的 SHA（短或长）。
        session_id: commit session_id（worker 复用，auto-commit 标记 [GW:<sid>:auto]）。
        committed_files: 本次 commit 的文件列表（触发 reconciler trigger）。
        commit_message: commit message（审计追溯用）。

    Returns:
        dict::

            {
              "ok": True/False,
              "commit_sha": "...",
              "status": "pending",   # spawn 后立即返回 pending
              "status": "skipped",   # 并发上限达限，跳过 spawn（#ARCH-RECONCILER-WORKER-SESSION-001）
              "worker_pid": 12345,
              "payload_file": "...",
              "status_file": "...",
              "error": "",           # ok=False 时填
            }
    """
    root = Path(project_root) if not isinstance(project_root, Path) else project_root
    root = root.resolve()
    started_at = int(time.time())

    # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
    # 每次新 commit 顺带清扫已死的 running status file，防止孤儿累积。
    # best-effort：清扫失败不阻断 launch（fail-open）。
    try:
        sweep_stale_workers(root)
    except Exception:  # noqa: BLE001 — 清扫失败不阻断 launch
        pass

    # CAND-GOVSEC-001 ④（2026-08-23）：launch 临界区（并发计数 + 写 pending
    # status + spawn）整体跨进程文件锁互斥——第二个 launcher 在锁内必看到第一个
    # 刚写的 pending status，TOCTOU 缝隙物理闭合。锁获取失败/超时降级无锁继续
    # （fail-open，post-commit best-effort 不阻断 commit，与旧行为同平面）。
    with _acquire_launch_lock(root):
        return _launch_worker_locked(
            root, commit_sha, session_id, committed_files, commit_message, started_at
        )


def _launch_worker_locked(
    root: Path,
    commit_sha: str,
    session_id: str,
    committed_files: list[str],
    commit_message: str,
    started_at: int,
) -> dict:
    """launch 临界区本体——必须在 ``_acquire_launch_lock`` 持锁内调用。

    锁内序列：并发计数（inflight 口径）→ 写 payload → 写 pending status →
    spawn worker → 回填 worker_pid。pending status 在锁内落盘是缝隙闭合的
    关键：后续 launcher 持锁计数时必见到它（CAND-GOVSEC-001 ④）。
    """
    # 0. 并发控制（#ARCH-RECONCILER-WORKER-SESSION-001 Phase C, 2026-07-22；
    #    CAND-GOVSEC-001 ④ 扩口径为 inflight=已注册 worker ∪ 新鲜 pending/running
    #    status，spawn 前注册窗口由锁内同步写的 pending status 计入闭合）。
    #    超过 MAX_CONCURRENT_WORKERS 时跳过 spawn——fail-open 不阻断 commit，
    #    reconciler 结果缺失本次 commit（可接受：post-commit 审计是 best-effort）。
    active_workers = _count_inflight_workers(str(root))
    if active_workers >= MAX_CONCURRENT_WORKERS:
        return {
            "ok": True,
            "commit_sha": commit_sha,
            "status": "skipped",
            "worker_pid": 0,
            "payload_file": "",
            "status_file": "",
            "error": f"max concurrent workers ({MAX_CONCURRENT_WORKERS}) reached, {active_workers} active",
        }

    # 1. 写 payload file（worker 读取后自删）
    payload_path = _payload_file_path(root, commit_sha)
    payload_data = {
        "commit_sha": commit_sha,
        "session_id": session_id,
        "project_root": str(root),
        "committed_files": committed_files,
        "commit_message": commit_message,
        "started_at": started_at,
    }
    payload_tmp = payload_path.with_suffix(".json.tmp")
    payload_tmp.write_text(
        json.dumps(payload_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(payload_tmp, payload_path)

    # 2. 写 pending status file（worker 启动后改为 running）
    status_path = write_status_file(
        root,
        commit_sha,
        STATUS_PENDING,
        session_id=session_id,
        started_at=started_at,
        trigger_source="post_commit_async",
    )

    # 3. spawn detached worker subprocess
    cmd = [
        sys.executable,
        "-m",
        "zephyr.governance.audit.reconcile_worker",
        "--payload",
        str(payload_path),
    ]
    env = os.environ.copy()
    # 确保 PYTHONPATH 含 src/（worker import zephyr.* 需要）
    src_dir = str(root / "src") if (root / "src").is_dir() else ""
    if src_dir:
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing}" if existing else src_dir
    # P2-3 关键：worker 内部强制 sync 模式，阻断递归 spawn。
    # worker 内 reconciler 可能调 _commit_auto → commit() → _run_post_commit_reconcile
    # dispatcher 默认 async → 又 spawn worker → 无限递归。
    # 设 ZEPHYR_RECONCILE_SYNC=1 让 worker 内所有 commit 走 sync 路径。
    env["ZEPHYR_RECONCILE_SYNC"] = "1"
    # #ARCH-REGEN-CASCADE-001 治本（2026-08-05 CPU 爆炸事故）：
    # 标记 worker 进程身份。GitCommitGateway.run_post_commit_reconcile 检测到此标志
    # → 跳过 reconciler 链重跑。病根：ZEPHYR_RECONCILE_SYNC=1 让 worker 内 auto-commit
    # 走 sync 路径，同步递归重跑 32 reconciler，每个 apply_depgraph-calling reconciler
    # fire reconcile_async → N× 编排器并发爆炸。worker 主循环已覆盖全部 reconciler，
    # auto-commit 仅持久化，无需重跑链路。
    env["ZEPHYR_RECONCILE_WORKER"] = "1"

    try:
        # TRAE-067 铁律2：复用 process_pool 统一无窗口 spawn 入口
        # spawn_python_hidden 自动处理 CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP
        # (Windows) / start_new_session (POSIX) + close_fds=True
        # S3 观测层（2026-08-14 worktree wipe 裁定书）：stdio 从 DEVNULL 改落盘
        # .runtime/logs/reconcile_worker_<sha>.log——wipe 事故 4 个 worker 启动即死
        # 无日志可查的治本。日志目录创建失败时降级 DEVNULL（不阻断 launch）。
        log_dir = root / ".runtime" / "logs"
        worker_log: str | None = None
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            worker_log = str(log_dir / f"reconcile_worker_{commit_sha}.log")
        except OSError:
            worker_log = None
        proc = spawn_python_hidden(
            cmd,
            cwd=str(root),
            env=env,
            stdout_path=worker_log,
            stderr_path=worker_log,
        )
        # 治本：保持 proc 引用，避免 GC 触发 Popen.__del__ ResourceWarning
        _WORKER_PROCS[commit_sha] = proc
    except Exception as e:  # noqa: BLE001 — launch 失败 fail-open（sync 兜底）
        # spawn 失败：改 status 为 failed，调用方应回退 sync
        write_status_file(
            root,
            commit_sha,
            STATUS_FAILED,
            session_id=session_id,
            started_at=started_at,
            finished_at=int(time.time()),
            errors=[f"launch_reconcile_async spawn failed: {e}"],
            trigger_source="post_commit_async",
        )
        return {
            "ok": False,
            "commit_sha": commit_sha,
            "status": STATUS_FAILED,
            "worker_pid": 0,
            "payload_file": str(payload_path),
            "status_file": str(status_path),
            "error": f"spawn failed: {e}",
        }

    # 4. 更新 status file 记录 worker_pid（仍 pending，worker 启动后改 running）
    write_status_file(
        root,
        commit_sha,
        STATUS_PENDING,
        session_id=session_id,
        started_at=started_at,
        trigger_source="post_commit_async",
        worker_pid=proc.pid,
    )

    return {
        "ok": True,
        "commit_sha": commit_sha,
        "status": STATUS_PENDING,
        "worker_pid": proc.pid,
        "payload_file": str(payload_path),
        "status_file": str(status_path),
        "error": "",
    }


def query_reconcile_status(
    project_root: Path | str,
    commit_sha: str,
) -> dict:
    """查询 reconciler 链路执行状态（AI 公开 API）。

    Args:
        project_root: 项目根目录。
        commit_sha: commit SHA（与 launch 时传入一致）。

    Returns:
        dict::

            {
              "ok": True/False,        # status file 存在=True
              "commit_sha": "...",
              "status": "running"|"done"|"failed"|"stale"|"unknown",
              "started_at": 123,
              "finished_at": 0,
              "reconcilers_total": 30,
              "reconcilers_warn": 2,
              "reconcilers_auto_committed": 1,
              "errors": [...],
              "worker_pid": 12345,
              "elapsed_seconds": 12,    # done 时 = finished-started，否则 = now-started
              "error": "",              # ok=False 时填
            }
    """
    data = read_status_file(project_root, commit_sha)
    if data is None:
        return {
            "ok": False,
            "commit_sha": commit_sha,
            "status": STATUS_UNKNOWN,
            "started_at": 0,
            "finished_at": 0,
            "reconcilers_total": 0,
            "reconcilers_warn": 0,
            "reconcilers_auto_committed": 0,
            "errors": [],
            "worker_pid": 0,
            "elapsed_seconds": 0,
            "error": "status file not found (commit may predate P2-3 or async not triggered)",
        }
    now = int(time.time())
    started = data.get("started_at", 0)
    finished = data.get("finished_at", 0)
    if finished:
        elapsed = finished - started
    elif started:
        elapsed = now - started
    else:
        elapsed = 0
    return {
        "ok": True,
        "commit_sha": data.get("commit_sha", commit_sha),
        "status": data.get("status", STATUS_UNKNOWN),
        "started_at": started,
        "finished_at": finished,
        "reconcilers_total": data.get("reconcilers_total", 0),
        "reconcilers_warn": data.get("reconcilers_warn", 0),
        "reconcilers_auto_committed": data.get("reconcilers_auto_committed", 0),
        "errors": data.get("errors", []),
        "worker_pid": data.get("worker_pid", 0),
        "elapsed_seconds": elapsed,
        "error": "",
    }
