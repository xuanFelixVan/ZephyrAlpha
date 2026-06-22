# [A_module] module_id=MOD-ORC_ide_health_daemon | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-032 | docs/03_modules/_cross_layer/resource-optimization-engine/blueprint.md | §new-IDE
# [MODULE] zephyr.trading.ide_health_daemon
# [INVARIANTS] scan_ghost_windows 必须零副作用（只读）；kill_ghost_windows 必须日志记录每个 killed PID；track_task_process 线程安全；kill_task_processes 幂等
# [MODIFY-GUARD] MOD-INF-032 §new-IDE
# [CONSUMERS] zephyr.integration.shared_08.lifecycle.daemon_registry; zephyr.trading.boot_hooks
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] kill_task_processes 对已退出的 PID 不报错；cleanup_completed_tasks TaskRepository 不可用时返回空列表
# [TESTS]

"""
ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程
==================================================
全自动后台守护：TRAE 启动时注册到 DaemonRegistry，每 30s 扫描 MainWindowHandle=0
的 TRAE 窗口，发现后 force kill 其全家进程树。零用户干预。
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import threading
from typing import Any

logger = logging.getLogger(__name__)

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
    except Exception:
        pass
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
    except Exception:
        pass
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
                    logger.warning("ide_health_daemon: failed to kill PID %d", pid)

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
        except Exception:
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


def cleanup_completed_tasks() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    try:
        from zephyr.governance.persistence.task_repo import TaskRepository

        repo = TaskRepository()
        completed_statuses = ["COMPLETED", "FAILED", "CANCELLED"]
        tasks: list[dict[str, Any]] = []
        for s in completed_statuses:
            try:
                tasks.extend(repo.list_by_status(s))
            except Exception:
                pass
    except Exception:
        logger.warning("ide_health_daemon: TaskRepository unavailable for cleanup")
        return results

    with _task_map_lock:
        tracked_ids = list(_task_process_map.keys())

    for task_id in tracked_ids:
        if any(t.task_id == task_id and t.status.value.upper() in completed_statuses for t in tasks):
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
    def __init__(self) -> None:
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval: float = _SCAN_INTERVAL_SECONDS
        self._ghost_count: int = 0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ide-health-daemon")
        self._thread.start()
        logger.info("IdeHealthDaemon: started (interval=%ds)", self._interval)

    def stop(self) -> None:
        self._running = False
        logger.info("IdeHealthDaemon: stopped")

    def _loop(self) -> None:
        import time

        while self._running:
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
                logger.exception("IdeHealthDaemon: scan tick failed")
            time.sleep(self._interval)

    @property
    def ghost_count(self) -> int:
        return self._ghost_count


_daemon_instance: IdeHealthDaemon | None = None


def register_daemon() -> None:
    global _daemon_instance
    if _daemon_instance is not None:
        return
    _daemon_instance = IdeHealthDaemon()
    try:
        from zephyr.integration.shared_08.lifecycle.daemon_registry import registry

        registry.register(
            name="ide_health_daemon",
            start_fn=_daemon_instance.start,
            stop_fn=_daemon_instance.stop,
            priority=10,
        )
        registry.start("ide_health_daemon")
        logger.info("IdeHealthDaemon: registered and auto-started in DaemonRegistry")
    except Exception:
        logger.warning("IdeHealthDaemon: DaemonRegistry unavailable, starting standalone")
        _daemon_instance.start()
