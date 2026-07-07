# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] zephyr.trading.ide_health_daemon
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.shared.lifecycle.daemon_registry; zephyr.governance.compliance_rule; docs.03_modules._cross_layer.mcp_servers.blueprint.md; zephyr.governance.kb.pipeline.activate; zephyr.trading.feedback_loop.auto_evolution; zephyr.governance.rule_enforcement.adaptive_threshold; docs.03_modules._domain_governance.audit_trail.blueprint.md; docs.03_modules._domain_governance.drift_detector.blueprint.md; docs.03_modules._domain_autonomy_perm.budget_enforcer.blueprint.md; docs.03_modules._domain_autonomy_core.agent_spec.blueprint.md; zephyr.integration.mcp.audit_logger
# [CONSUMERS] zephyr.shared.lifecycle.daemon_registry; zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] scan_ghost_windows 必须零副作用（只读）；kill_ghost_windows 必须日志记录每个 killed PID；track_task_process 线程安全；kill_task_processes 幂等
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-IDE
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] kill_task_processes 对已退出的 PID 不报错；cleanup_completed_tasks TaskRepository 不可用时返回空列表
# [TESTS]
# [A_module] module_id=MOD-ORC_ide_health_daemon | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程
==================================================
全自动后台守护：TRAE 启动时注册到 DaemonRegistry，每 30s 扫描 MainWindowHandle=0
的 TRAE 窗口，发现后 force kill 其全家进程树。零用户干预。
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol

logger = logging.getLogger(__name__)


# 5.97.13 修复：抽取 _collect_drift_metrics 内嵌 try-except 的 helper
def _safe_unlink(path: Any) -> None:
    """安全删除文件，忽略 OSError（文件不存在/权限不足等）。"""
    try:
        path.unlink()
    except OSError:
        pass


__all__ = [
    "IdeHealthDaemon",
    "cleanup_completed_tasks",
    "kill_ghost_windows",
    "kill_task_processes",
    "register_daemon",
    "scan_ghost_windows",
    "track_task_process",
]

_TRAE_PROCESS_NAME = "Trae CN"
_SCAN_INTERVAL_SECONDS = 30.0
_task_process_map: dict[str, set[int]] = {}
_task_map_lock = threading.Lock()


def _get_trae_processes() -> list[dict[str, Any]]:
    procs: list[dict[str, Any]] = []
    try:
        import psutil

        for p in psutil.process_iter(["pid", "name"]):
            try:
                info = p.info
                if info.get("name") == _TRAE_PROCESS_NAME:
                    procs.append(
                        {
                            "pid": info["pid"],
                            "name": info["name"],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass
    return procs


def _get_window_configs_from_cmdlines(pids: list[int]) -> dict[str, set[int]]:
    """
    通过 WMI 查询每个 TRAE 进程的命令行，提取 vscode-window-config UUID。
    返回 {window_config_uuid: {pid, pid, ...}}。
    """
    import re

    windows: dict[str, set[int]] = {}
    for pid in pids:
        try:
            import subprocess

            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f'(Get-WmiObject Win32_Process -Filter "ProcessId={pid}").CommandLine',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            cmdline = result.stdout
            match = re.search(r"vscode-window-config=vscode:([a-f0-9-]+)", cmdline)
            if match:
                config_id = match.group(1)
                windows.setdefault(config_id, set()).add(pid)
        except Exception:
            continue
    return windows


def _get_visible_window_configs() -> set[str]:
    """
    通过 PowerShell 获取 MainWindowTitle 非空的 TRAE 窗口对应的 window-config。
    返回 {config_id, ...}。
    """
    import re

    visible: set[str] = set()
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process -Name 'Trae CN' -ErrorAction SilentlyContinue | "
                "Where-Object { $_.MainWindowTitle -ne '' } | "
                "ForEach-Object { "
                '  try { (Get-WmiObject Win32_Process -Filter \\"ProcessId=$($_.Id)\\").CommandLine } catch {} '
                "}",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        for match in re.finditer(r"vscode-window-config=vscode:([a-f0-9-]+)", result.stdout):
            visible.add(match.group(1))
    except Exception as e:
        logger.warning("suppressed error in ide_health_daemon", exc_info=True)
    return visible


def _get_mainwindow_handle_map() -> dict[int, int]:
    """
    返回 {pid: MainWindowHandle}，仅含 TRAE 进程。
    """
    handle_map: dict[int, int] = {}
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process -Name 'Trae CN' -ErrorAction SilentlyContinue | "
                "Select-Object Id, MainWindowHandle | "
                "ForEach-Object { '{0}:{1}' -f $_.Id, $_.MainWindowHandle }",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                try:
                    pid = int(parts[0])
                    handle = int(parts[1])
                    handle_map[pid] = handle
                except ValueError:
                    continue
    except Exception as e:
        logger.warning("suppressed error in ide_health_daemon", exc_info=True)
    return handle_map


def scan_ghost_windows() -> list[dict[str, Any]]:
    """
    扫描所有 TRAE 幽灵窗口（MainWindowHandle=0 且无对应可见窗口的 window-config）。
    返回 [{config_id, pids, pid_count}]。
    """
    procs = _get_trae_processes()
    if not procs:
        return []

    all_pids = [p["pid"] for p in procs]
    windows = _get_window_configs_from_cmdlines(all_pids)
    visible = _get_visible_window_configs()
    handle_map = _get_mainwindow_handle_map()

    ghosts: list[dict[str, Any]] = []
    for config_id, pids in windows.items():
        if config_id in visible:
            continue
        ghost_pids: list[int] = []
        for pid in pids:
            if pid in handle_map and handle_map[pid] == 0:
                ghost_pids.append(pid)
        if ghost_pids:
            ghosts.append(
                {
                    "config_id": config_id,
                    "pids": sorted(ghost_pids),
                    "pid_count": len(ghost_pids),
                }
            )

    return ghosts


def kill_ghost_windows(ghosts: list[dict[str, Any]] | None = None) -> list[int]:
    """
    Force kill 幽灵窗口进程树。
    不传 ghosts 时自动扫描。
    返回被 kill 的 PID 列表。
    """
    if ghosts is None:
        ghosts = scan_ghost_windows()

    killed: list[int] = []
    for ghost in ghosts:
        for pid in ghost["pids"]:
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append(pid)
                logger.info("ide_health_daemon: killed ghost PID %d (config=%s)", pid, ghost["config_id"])
            except OSError:
                try:
                    import psutil

                    psutil.Process(pid).terminate()
                    killed.append(pid)
                    logger.info("ide_health_daemon: psutil-terminated ghost PID %d", pid)
                except Exception:
                    logger.warning("ide_health_daemon: failed to kill PID %d", pid, exc_info=True)

    return killed


def track_task_process(task_id: str, pids: list[int]) -> None:
    with _task_map_lock:
        _task_process_map.setdefault(task_id, set()).update(pids)
        logger.debug("ide_health_daemon: tracked %d PIDs for task %s", len(pids), task_id)


def untrack_task_process(task_id: str) -> None:
    with _task_map_lock:
        _task_process_map.pop(task_id, None)


def _force_kill_pid(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except OSError:
        try:
            import psutil

            psutil.Process(pid).terminate()
            return True
        except Exception as e:
            logger.warning("_force_kill_pid: failed to terminate process %s (%s: %s)", pid, type(e).__name__, e, exc_info=True)
            return False


def kill_task_processes(task_id: str) -> list[int]:
    with _task_map_lock:
        pids = list(_task_process_map.get(task_id, set()))
        if not pids:
            return []
        _task_process_map.pop(task_id, None)

    killed: list[int] = []
    for pid in pids:
        if _force_kill_pid(pid):
            killed.append(pid)
            logger.info("ide_health_daemon: killed task-residue PID %d (task=%s)", pid, task_id)
        else:
            logger.warning("ide_health_daemon: failed to kill task-residue PID %d (task=%s)", pid, task_id)
    return killed


# 5.97.14 修复：抽取 cleanup_completed_tasks 内嵌 try-except 的 helper
_COMPLETED_STATUSES = ["COMPLETED", "FAILED", "CANCELLED"]


def _list_completed_tasks(repo: Any, statuses: list[str]) -> list[Any]:
    """按状态列表聚合查询已完成任务，单个状态查询失败时记录并继续。"""
    tasks: list[Any] = []
    for s in statuses:
        try:
            tasks.extend(repo.list_by_status(s))
        except Exception:
            logger.debug("suppressed error in ide_health_daemon list_by_status(%s)", s, exc_info=True)
    return tasks


def cleanup_completed_tasks(task_repo: TaskRepositoryProtocol | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    try:
        repo = task_repo
        if repo is None:
            from zephyr.governance.persistence.task_repo import TaskRepository

            repo = TaskRepository()
        tasks = _list_completed_tasks(repo, _COMPLETED_STATUSES)
    except Exception:
        logger.warning("ide_health_daemon: TaskRepository unavailable for cleanup", exc_info=True)
        return results

    with _task_map_lock:
        tracked_ids = list(_task_process_map.keys())

    for task_id in tracked_ids:
        if any(t.task_id == task_id and t.status.value.upper() in _COMPLETED_STATUSES for t in tasks):
            killed = kill_task_processes(task_id)
            results.append(
                {
                    "task_id": task_id,
                    "killed": killed,
                    "killed_count": len(killed),
                }
            )

    return results


class IdeHealthDaemon:
    def __init__(self, project_root: str | Path | None = None) -> None:
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval: float = _SCAN_INTERVAL_SECONDS
        self._ghost_count: int = 0
        self._loop_count: int = 0  # P1-DAE: drift 指标采集节拍计数
        self._project_root: Path = Path(project_root) if project_root else Path.cwd()
        self._lifecycle_lock = threading.Lock()  # 5.142.6 修复: 保护 start/stop 的 check-then-act, 避免 TOCTOU

    def start(self) -> None:
        """P1 修复（2026-07-05）：事件驱动替代 time.sleep daemon。

        订阅 EventBus 事件触发 scan_tick()，不再启动后台轮询线程。
        """
        with self._lifecycle_lock:
            if self._running:
                return
            self._running = True
            try:
                from zephyr.shared.events.event_bus import bus

                bus.subscribe("task.completed", lambda _: self.scan_tick())
                bus.subscribe("task.failed", lambda _: self.scan_tick())
                bus.subscribe("ide.health.check.request", lambda _: self.scan_tick())
                logger.info("IdeHealthDaemon: started (event-driven, no daemon thread)")
            except Exception as e:
                logger.warning("IdeHealthDaemon: EventBus subscribe failed: %s", e, exc_info=True)

    def stop(self) -> None:
        with self._lifecycle_lock:
            self._running = False
        logger.info("IdeHealthDaemon: stopped")

    def scan_tick(self) -> None:
        """事件驱动入口：扫描 ghost 窗口 + drift 指标采集。

        由 EventBus 事件触发或 CI 批量兜底调用。替代原 _loop 的 time.sleep 轮询。
        """
        if not self._running:
            return
        try:
            ghosts = scan_ghost_windows()
            if ghosts:
                logger.warning(
                    "IdeHealthDaemon: detected %d ghost window(s): %s",
                    len(ghosts),
                    [(g["config_id"], g["pid_count"]) for g in ghosts],
                )
                killed = kill_ghost_windows(ghosts)
                if killed:
                    logger.info("IdeHealthDaemon: auto-killed %d processes", len(killed))
            self._ghost_count = len(ghosts)
        except Exception:
            logger.exception("IdeHealthDaemon: scan tick failed", exc_info=True)
        # P1-DAE: 每 10 轮采集一次 drift 健康指标
        self._loop_count += 1
        if self._loop_count % 10 == 0:
            try:
                self._collect_drift_metrics()
            except Exception:
                logger.exception("IdeHealthDaemon: drift metrics collection failed", exc_info=True)

    def _collect_drift_metrics(self) -> None:
        """采集 drift 健康指标，写入 .runtime/drift_health.json（P1-DAE）。

        指标：
        - stash_count: git stash 数量（>5 → warning；P1-STH 时触发自动清理）
        - worktree_changes: git status 变更文件数（>50 → warning，防并行 session 漂移）
        - ghost_count: 幽灵窗口数（本轮回采）
        - timestamp: 采集时间

        设计对标 GitOps 社区：drift detection 是一等 SRE 指标（SLI/SLO）。
        """
        metrics: dict[str, Any] = {
            "timestamp": now_utc().isoformat(),
            "ghost_count": self._ghost_count,
        }
        # stash 数量
        r = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True, text=True,
            cwd=str(self._project_root),
        )
        # 5.75.3 修复：检查 returncode，非零时记录 warning 并标记 metrics 不可用
        if r.returncode != 0:
            logger.warning(
                "drift health: git stash list failed (returncode=%d): %s",
                r.returncode, r.stderr.strip(),
            )
            metrics["stash_count"] = None
        else:
            metrics["stash_count"] = len([l for l in r.stdout.splitlines() if l.strip()])
        # worktree 变更量
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True,
            cwd=str(self._project_root),
        )
        if r.returncode != 0:
            logger.warning(
                "drift health: git status --porcelain failed (returncode=%d): %s",
                r.returncode, r.stderr.strip(),
            )
            metrics["worktree_changes"] = None
        else:
            metrics["worktree_changes"] = len([l for l in r.stdout.splitlines() if l.strip()])
        # 写入 .runtime/drift_health.json（P1-T3: 原子写 RULE-ONE — tmp + os.replace，防多 session 并发采集写损坏）
        runtime_dir = self._project_root / ".runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        health_path = runtime_dir / "drift_health.json"
        tmp_path = runtime_dir / f"drift_health.json.{os.getpid()}.tmp"
        try:
            tmp_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp_path, health_path)
        except PermissionError:
            _safe_unlink(tmp_path)
        # 阈值告警 + 自动清理（P1-STH: stash > 5 时调 cleanup_stash.py --cleanup）
        if metrics["stash_count"] > 5:
            logger.warning("drift health: stash_count=%d > 5, auto-cleanup", metrics["stash_count"])
            # P1-STH: 自动调用 cleanup_stash.py --cleanup（保留 KEEP_COUNT=3 最新，安全）
            try:
                subprocess.run(
                    [sys.executable, "scripts/governance/cleanup_stash.py", "--cleanup"],
                    cwd=str(self._project_root),
                    capture_output=True, text=True, timeout=60,
                )
            except Exception:
                logger.exception("drift health: stash auto-cleanup failed", exc_info=True)
        if metrics["worktree_changes"] is not None and metrics["worktree_changes"] > 50:
            logger.warning("drift health: worktree_changes=%d > 50", metrics["worktree_changes"])

    @property
    def ghost_count(self) -> int:
        return self._ghost_count


_daemon_instance: IdeHealthDaemon | None = None
_daemon_instance_lock = threading.Lock()


def register_daemon() -> None:
    global _daemon_instance
    if _daemon_instance is not None:
        return
    with _daemon_instance_lock:
        if _daemon_instance is not None:
            return
        _daemon_instance = IdeHealthDaemon()
    try:
        from zephyr.shared.lifecycle.daemon_registry import registry

        registry.register(
            name="ide_health_daemon",
            start_fn=_daemon_instance.start,
            stop_fn=_daemon_instance.stop,
            priority=10,
        )
        registry.start("ide_health_daemon")
        logger.info("IdeHealthDaemon: registered and auto-started in DaemonRegistry")
    except Exception:
        logger.warning("IdeHealthDaemon: DaemonRegistry unavailable, starting standalone", exc_info=True)
        _daemon_instance.start()