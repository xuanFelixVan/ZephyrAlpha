# [BLUEPRINT] MOD-GOV_RECONCILE_RUNNER | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] zephyr.governance.audit.reconcile_runner
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); subprocess; json; pathlib
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway._run_post_commit_reconcile_async; AI 查询 reconcile 状态
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] status file 原子写入（tmp + os.replace）；subprocess 完全 detached（DETACHED_PROCESS on Windows / start_new_session on POSIX）；payload file 路径含 commit_sha 保证唯一；launch_reconcile_async 立即返回不阻塞；query_reconcile_status 失败 fail-open 返回 status=unknown
# [MODIFY-GUARD] launch_reconcile_async 函数签名；status file JSON schema（commit_sha/session_id/status/started_at/finished_at/errors/trigger_source）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] launch_reconcile_async 失败→ok=False 含 error，不抛异常；query_reconcile_status 失败→status=unknown 不抛异常
# [TESTS] tests/governance/audit/test_reconcile_async.py
# [A_module] module_id=MOD-GOV-reconcile_runner | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 commit 事件触发（非 cron/manual）
"""reconcile_runner.py — Reconciler 链路异步化（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）

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
]

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, TypedDict

from zephyr.shared.io.paths import REPO_ROOT

# Status 枚举（字符串常量，避免 enum 序列化复杂度）
STATUS_PENDING: str = "pending"      # 已 spawn subprocess，worker 尚未启动
STATUS_RUNNING: str = "running"      # worker 已启动，正在执行 reconciler
STATUS_DONE: str = "done"            # 全部 reconciler 执行完成
STATUS_FAILED: str = "failed"        # worker 异常退出
STATUS_STALE: str = "stale"          # running 超 30min，疑似僵尸
STATUS_UNKNOWN: str = "unknown"      # status file 不存在（commit 早于 P2-3 / 未触发 async）

# 僵尸判定阈值（秒）——running 状态超此时长视为 stale
_STALE_THRESHOLD_SECONDS: int = 1800  # 30 分钟

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
    status: str               # STATUS_* 常量之一
    started_at: int           # Unix timestamp（spawn 时间）
    finished_at: int          # Unix timestamp（done/failed 时间，未完成=0）
    reconcilers_total: int    # 已执行 reconciler 总数（done 时填）
    reconcilers_warn: int     # warn 结果数
    reconcilers_auto_committed: int  # auto_commit 结果数
    errors: list[str]         # 失败原因列表
    trigger_source: str       # "post_commit_async"
    worker_pid: int           # worker subprocess PID


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
        started = data.get("started_at", 0)
        if started and (int(time.time()) - started > _STALE_THRESHOLD_SECONDS):
            data["status"] = STATUS_STALE
            _log_stale_to_db(project_root, commit_sha, started, data)
    return data  # type: ignore[return-value]


# 已记录到 DB 的 stale commit_sha 集合（内存去重，进程级）
_stale_logged: set[str] = set()


def _log_stale_to_db(
    project_root: Path | str,
    commit_sha: str,
    started_at: int,
    status_data: dict,
) -> None:
    """持久化 stale 状态到 reconcile_execution_log 表（幂等，每个 commit_sha 只记录一次）。

    #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：
    之前 stale 状态只在 read_status_file 返回值中标记，不写 DB，AI 查询
    reconcile_execution_log 表看不到 stale 事件，违反持久化铁律。
    """
    if commit_sha in _stale_logged:
        return
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        elapsed = int(time.time()) - started_at  # noqa: m46-time  M46豁免: 与本文件既有 time.time() 风格一致（5处既有调用），stale 判定需 Unix timestamp 整数差值
        session_id = status_data.get("session_id", "unknown")
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="critical_warn",
                detail=f"reconcile worker stale: running for {elapsed}s "
                       f"(threshold={_STALE_THRESHOLD_SECONDS}s, commit_sha={commit_sha}, "
                       f"worker_pid={status_data.get('worker_pid', 'unknown')})",
                gate_id="RECONCILE-WORKER-STALE",
            )],
            session_id,
            trigger_source="post_commit_async_stale",
        )
        _stale_logged.add(commit_sha)
    except Exception:  # noqa: BLE001 — DB 写入失败不影响 stale 判定
        pass


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
              "worker_pid": 12345,
              "payload_file": "...",
              "status_file": "...",
              "error": "",           # ok=False 时填
            }
    """
    root = Path(project_root) if not isinstance(project_root, Path) else project_root
    root = root.resolve()
    started_at = int(time.time())

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
        json.dumps(payload_data, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    os.replace(payload_tmp, payload_path)

    # 2. 写 pending status file（worker 启动后改为 running）
    status_path = write_status_file(
        root, commit_sha, STATUS_PENDING,
        session_id=session_id,
        started_at=started_at,
        trigger_source="post_commit_async",
    )

    # 3. spawn detached worker subprocess
    cmd = [
        sys.executable, "-m", "zephyr.governance.audit.reconcile_worker",
        "--payload", str(payload_path),
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

    creationflags = 0
    if os.name == "nt":
        # Windows: CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
        # CREATE_NO_WINDOW(0x08000000): 不创建控制台窗口，无闪窗（TRAE-067 铁律2）
        # CREATE_NEW_PROCESS_GROUP(0x00000200): 独立进程组，Ctrl+C 不传播
        # 注：CREATE_NO_WINDOW 与 DETACHED_PROCESS 互斥（MSDN），CREATE_NO_WINDOW
        # 同时满足"无窗口"+"detached 语义"（父退出不影响子，因 close_fds=True）
        creationflags = 0x08000000 | 0x00000200  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(root),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags,
            start_new_session=(os.name != "nt"),  # POSIX: 新 session
        )
        # 治本：保持 proc 引用，避免 GC 触发 Popen.__del__ ResourceWarning
        _WORKER_PROCS[commit_sha] = proc
    except Exception as e:  # noqa: BLE001 — launch 失败 fail-open（sync 兜底）
        # spawn 失败：改 status 为 failed，调用方应回退 sync
        write_status_file(
            root, commit_sha, STATUS_FAILED,
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
        root, commit_sha, STATUS_PENDING,
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
