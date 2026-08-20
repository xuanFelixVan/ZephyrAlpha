# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.process_pool
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.lifecycle.resource_optimization_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
process_pool.py - Shared process pool for MCP servers and subprocess tasks
=============================================================================

SSoT: MOD-RESOURCE_OPTIMIZATION_ENGINE resource-optimization-engine/blueprint.md §7.2

Design:
  - Max process limit (default 30) to prevent resource exhaustion
  - Process reuse: same MCP server shares one subprocess across conversations
  - Zombie detection: periodic scan for dead processes
  - Graceful shutdown: terminate all pooled processes on engine stop
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field

from zephyr.shared.lifecycle.resource_optimization_models import ProcessPoolStats

__all__ = [
    "MCPProcessPool",
    "PooledProcess",
    "is_pid_alive",
    "run_subprocess_hidden",
    "spawn_python_hidden",
]

logger = logging.getLogger(__name__)


# ============================================================================
# Hidden subprocess helpers (TRAE-067 / RULE-EIGHTEEN SSoT 入口)
# ============================================================================
# 病根（2026-07-20 裁定 #ARCH-RUNCOMMAND-WINDOW-FLASH-001 Phase 1.5）：
# Windows 控制台子系统程序（python.exe/powershell.exe）在无父控制台时会
# 创建新控制台窗口 → 闪窗。DETACHED_PROCESS(0x8) 不继承父控制台但仍会
# 创建新控制台；CREATE_NO_WINDOW(0x08000000) 才真正无窗口。两者互斥
# （MSDN 明确），故 hidden helper 用 CREATE_NO_WINDOW 替代 DETACHED_PROCESS。
#
# Job Object 逃逸（#ARCH-SPAWN-JOB-KILL-001，2026-08-14 探针实证）：
# IDE 终端把每条命令跑在 KILL_ON_JOB_CLOSE Job Object 内，命令退出拆 job
# 连坐杀死成员进程——detached spawn（worker/daemon）必须逃逸 job：
# 首选 CREATE_BREAKAWAY_FROM_JOB（job 允许时零依赖）；WinError 5（job 禁
# breakaway）降级 WMI Win32_Process.Create（WMI 服务在 job 外创建进程）。
#
# 调用方（真源唯一，禁止重复造轮子）：
#   - reconciliation_registry._run_subprocess（36 处 reconciler subprocess 统一入口）
#   - reconcile_runner.launch_reconcile_async（worker spawn）
#   - session_worktree._spawn_heartbeat_daemon（daemon spawn）
#   - ide_health_daemon 6 处 powershell/git/python 调用
#   - trigger_router / script_runner / action_dispatcher / gpu_monitor / diff_detector
#   - process_sandbox / l2a_process_sandbox / auto_runtime_core
# ============================================================================


def _hidden_creationflags() -> int:
    """返回 Windows 无窗口 creationflags；POSIX 返回 0。

    CREATE_NO_WINDOW(0x08000000)：子进程不创建控制台窗口，无闪窗。
    CREATE_NEW_PROCESS_GROUP(0x00000200)：独立进程组，Ctrl+C 不传播
    （保留 detached 语义，与原 DETACHED_PROCESS 行为对齐）。

    注意：CREATE_NO_WINDOW 与 DETACHED_PROCESS 互斥（MSDN），不可叠加。
    """
    if os.name == "nt":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200
        )
    return 0


# ============================================================================
# Job Object 逃逸（#ARCH-SPAWN-JOB-KILL-001，2026-08-14）
# ============================================================================
# 病根：IDE 终端把每条命令跑在 Windows Job Object 内，命令退出拆 job 时
# 连坐杀死全部成员进程。CREATE_NO_WINDOW/CREATE_NEW_PROCESS_GROUP 只隔离
# 控制台/进程组，对 job 成员身份无效（无条件继承）。逃逸须
# CREATE_BREAKAWAY_FROM_JOB，且需 job 开了 BREAKAWAY_OK 才合法；
# 禁 breakaway 的 job（Trae 终端实测 WinError 5）只能走 WMI
# Win32_Process.Create——进程由 WMI 服务在调用方 job 外创建，天然逃逸。
# ============================================================================

_CREATE_BREAKAWAY_FROM_JOB = 0x01000000  # Win32: 子进程脱离父 Job Object

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_PROCESS_TERMINATE = 0x0001
_SYNCHRONIZE = 0x00100000
_STILL_ACTIVE = 259
_WAIT_OBJECT_0 = 0
_WAIT_TIMEOUT = 0x00000102
_INFINITE = 0xFFFFFFFF


class _WmiDetachedProcess:
    """Popen 兼容 shim（WMI 降级路径）——WMI 创建的进程只有 PID 可观测。

    poll/wait/terminate/kill 经 ctypes OpenProcess 实现；不持有 CreateProcess
    句柄，不存在 Popen.__del__ ResourceWarning。stdio 不可继承（WMI 路径等价
    全 DEVNULL——CREATE_NO_WINDOW 下无控制台），调用方需输出请写日志文件。
    """

    def __init__(self, pid: int, args: object = None) -> None:
        self.pid = pid
        self.args = args
        self.returncode: int | None = None

    def _open(self, access: int) -> int:
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(access, False, self.pid)
        if not handle:
            raise ProcessLookupError(f"pid={self.pid} gle={ctypes.GetLastError()}")
        return handle

    def poll(self) -> int | None:
        """对齐 Popen.poll：运行中返回 None，已退出返回退出码（不可取码时 -1）。"""
        if self.returncode is not None:
            return self.returncode
        import ctypes

        kernel32 = ctypes.windll.kernel32
        try:
            handle = self._open(_PROCESS_QUERY_LIMITED_INFORMATION)
        except ProcessLookupError:
            self.returncode = -1  # 进程已消失且退出码不可取
            return self.returncode
        exit_code = ctypes.c_ulong(0)
        kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        kernel32.CloseHandle(handle)
        if exit_code.value == _STILL_ACTIVE:
            return None
        self.returncode = exit_code.value
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        """对齐 Popen.wait：阻塞至退出或超时（超时抛 subprocess.TimeoutExpired）。"""
        import ctypes

        kernel32 = ctypes.windll.kernel32
        if self.returncode is not None:
            return self.returncode
        try:
            handle = self._open(_SYNCHRONIZE | _PROCESS_QUERY_LIMITED_INFORMATION)
        except ProcessLookupError:
            self.returncode = -1
            return self.returncode
        timeout_ms = _INFINITE if timeout is None else max(0, int(timeout * 1000))
        rc = kernel32.WaitForSingleObject(handle, timeout_ms)
        if rc == _WAIT_TIMEOUT:
            kernel32.CloseHandle(handle)
            raise subprocess.TimeoutExpired(self.args, timeout)
        exit_code = ctypes.c_ulong(0)
        kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        kernel32.CloseHandle(handle)
        self.returncode = exit_code.value if rc == _WAIT_OBJECT_0 else -1
        return self.returncode

    def terminate(self) -> None:
        """对齐 Popen.terminate；进程已死时静默（best-effort）。"""
        import ctypes

        kernel32 = ctypes.windll.kernel32
        try:
            handle = self._open(_PROCESS_TERMINATE)
        except ProcessLookupError:
            return
        kernel32.TerminateProcess(handle, 1)
        kernel32.CloseHandle(handle)

    def kill(self) -> None:
        """Windows 上与 terminate 等价（对齐 Popen.kill 语义）。"""
        self.terminate()


def _ps_single_quote(value: str) -> str:
    """PowerShell 单引号字符串字面量（内嵌单引号双写转义）。"""
    return "'" + value.replace("'", "''") + "'"


# 敏感键剥离名单（#ARCH-105）：WMI 传输通道不携带令牌/密钥语义变量。
# 病史：全量 env 内联 -Command 脚本，TimeoutExpired.args 携带完整命令喷入
# reconcile status JSON——GITHUB_TOKEN 等明文落盘。WMI 通道经系统服务
# （Winmgmt）中转，本身亦不宜接触凭据。主 Popen 通道（CreateProcess 直传、
# 无第三方中转）保留完整继承语义——四调用方（reconcile_worker/drift
# watchdog/session_worktree/ollama）均无凭据需求，剥离行为差异可接受。
_SECRET_ENV_KEY_RE = re.compile(
    r"TOKEN|SECRET|PASSWORD|CREDENTIAL|COOKIE|API_?KEY|PRIVATE_?KEY|ACCESS_?KEY",
    re.IGNORECASE,
)


def _spawn_detached_via_wmi(
    cmd: list[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    stdout_path: str | None = None,
    stderr_path: str | None = None,
) -> _WmiDetachedProcess:
    """WMI Win32_Process.Create 降级 spawn（job 禁 breakaway 时的逃逸通道）。

    进程由 WMI 服务（Winmgmt）创建，不属于调用方所在 Job Object——父命令
    退出拆 job 时不被连坐（#ARCH-SPAWN-JOB-KILL-001 探针实证）。

    - 环境变量（env=None 时物化当前 os.environ，对齐 Popen 继承语义）先经
      _SECRET_ENV_KEY_RE 剥离敏感键，再经临时文件（utf-8-sig）传输给
      Win32_ProcessStartup.EnvironmentVariables（#ARCH-105）——不内联
      -Command 脚本：脚本恒定小体量（通道慢时不再解析数万字符），且任何
      异常路径（TimeoutExpired.args 等）都不再携带 env 内容
    - ShowWindow=SW_HIDE 保持 TRAE-067 无闪窗铁律（CreateFlags 被 WMI 拒
      ReturnValue=21；ShowWindow 是 WMI 合法通道，探针实证）
    - WMI ReturnValue != 0 → RuntimeError（2=access denied / 9=path not found /
      21=invalid parameter 等，见 MSDN Win32_Process.Create）
    - stdout_path/stderr_path（S3 观测层，2026-08-14）：WMI 路径 stdio 句柄
      不可继承，改用 cmd.exe 壳层追加重定向（``cmd.exe /c <cmd> >> "log" 2>&1``）
      实现日志落盘——比句柄继承覆盖面更全（连解释器启动期错误也落盘）。
      两路径相同则合并 ``2>&1``，不同则分别 ``2>>``。
    """
    env_dict = dict(os.environ) if env is None else dict(env)
    env_dict = {k: v for k, v in env_dict.items() if not _SECRET_ENV_KEY_RE.search(k)}
    cmdline = subprocess.list2cmdline(list(cmd))
    # S3：cmd 壳层重定向包装（cmd /c 后字符串含 >>/& 特殊符 → 不触发 cmd 去引号规则）
    if stdout_path or stderr_path:
        out_p = stdout_path or stderr_path
        err_p = stderr_path or stdout_path
        if out_p == err_p:
            redir = f' >> "{out_p}" 2>&1'
        else:
            redir = f' >> "{out_p}" 2>> "{err_p}"'
        cmdline = f"cmd.exe /c {cmdline}{redir}"
    # env 文件传输（#ARCH-105）：utf-8-sig BOM 保 PS5.1 Get-Content 对
    # 非 ASCII 值（如中文用户名/路径）正确解码；PS finally 与 Python finally
    # 双侧清理（timeout 时 run 已杀子进程，Python 侧兜底）。
    env_fd, env_file = tempfile.mkstemp(prefix="zephyr_wmi_env_", suffix=".txt")
    try:
        with os.fdopen(env_fd, "w", encoding="utf-8-sig", newline="\n") as fh:
            for key, value in env_dict.items():
                fh.write(f"{key}={value}\n")
        ps_script = (
            f"$envFile = {_ps_single_quote(env_file)}\n"
            "try {\n"
            "$cls = Get-CimClass -ClassName Win32_ProcessStartup\n"
            "$startup = New-CimInstance -CimClass $cls -ClientOnly\n"
            "$startup.EnvironmentVariables = [string[]](Get-Content -LiteralPath $envFile -Encoding UTF8)\n"
            "$startup.ShowWindow = [uint16]0\n"  # SW_HIDE（TRAE-067 无闪窗）
            "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{\n"
            f"  CommandLine = {_ps_single_quote(cmdline)}\n"
            f"  CurrentDirectory = {_ps_single_quote(cwd or os.getcwd())}\n"
            "  ProcessStartupInformation = $startup\n"
            "}\n"
            'Write-Output "ZEPHYR_WMI_SPAWN|$($r.ReturnValue)|$($r.ProcessId)"\n'
            "} finally {\n"
            "Remove-Item -LiteralPath $envFile -Force -ErrorAction SilentlyContinue\n"
            "}\n"
        )
        try:
            completed = run_subprocess_hidden(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            # 脱敏（#ARCH-105）：不回传 TimeoutExpired——其 args 含完整命令，
            # 病史为全量 env 随之喷入 reconcile status JSON 明文落盘。
            raise RuntimeError("WMI spawn probe timed out after 60s (powershell CIM channel busy/hung)") from None
        for line in (completed.stdout or "").splitlines():
            if line.startswith("ZEPHYR_WMI_SPAWN|"):
                _, return_value, pid_text = line.strip().split("|", 2)
                if return_value == "0" and pid_text.isdigit():
                    return _WmiDetachedProcess(int(pid_text), args=cmd)
                raise RuntimeError(f"WMI Win32_Process.Create failed: ReturnValue={return_value} (cmd={cmdline[:120]})")
        raise RuntimeError(
            "WMI spawn probe sentinel missing; "
            f"stdout={(completed.stdout or '')[:200]!r} stderr={(completed.stderr or '')[:200]!r}"
        )
    finally:
        try:
            os.unlink(env_file)
        except OSError:
            pass


def run_subprocess_hidden(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """统一无窗口 subprocess.run 入口（TRAE-067 铁律2 落地）。

    与原 subprocess.run 行为一致，唯一区别：Windows 下加 CREATE_NO_WINDOW
    消除闪窗。默认 errors='replace' 避免非 UTF-8 字符抛 UnicodeDecodeError
    （5.59.5 修复策略继承）。

    Args:
        cmd: 命令列表（如 [sys.executable, "scripts/foo.py"]）
        **kwargs: 透传给 subprocess.run（capture_output/text/encoding/errors/cwd/env/timeout 等）

    Returns:
        subprocess.CompletedProcess
    """
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    # 仅在 text 模式下设 errors——Python subprocess 在 errors 被设时会强制
    # text 模式（即使 text=False），导致 stdout 返回 str 而非 bytes，
    # 破坏调用方的 .decode() 逻辑（如 git show 字节比较场景）。
    if kwargs.get("text", True):
        kwargs.setdefault("errors", "replace")
    if os.name == "nt":
        # 调用方可能已设 creationflags（如需 DETACHED_PROCESS）——不覆盖，
        # 仅在未设时注入 hidden flags
        kwargs.setdefault("creationflags", _hidden_creationflags())
    return subprocess.run(cmd, **kwargs)


def spawn_python_hidden(
    cmd: list[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    stdin_to_devnull: bool = True,
    stdout_to_devnull: bool = True,
    stderr_to_devnull: bool = True,
    stdout_path: str | None = None,
    stderr_path: str | None = None,
) -> subprocess.Popen:
    """无窗口 spawn python 子进程（daemon/reconciler worker/scheduler 用）。

    与 subprocess.Popen 行为一致，区别：
    1. Windows 下用 CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP（无窗口 + 独立进程组）
    2. 默认 stdin/stdout/stderr 重定向到 DEVNULL（daemon 无 IO 依赖）
    3. close_fds=True（子进程不继承父 FD，detached 语义）
    4. Job Object 逃逸（#ARCH-SPAWN-JOB-KILL-001）：detached spawn 追加
       CREATE_BREAKAWAY_FROM_JOB——IDE 终端等把命令跑在 KILL_ON_JOB_CLOSE
       Job Object 内时，不加此 flag 的子进程会随父命令退出被连坐杀死
       （job 成员身份无条件继承，CREATE_NO_WINDOW 等控制台 flag 无效）。
       job 允许 breakaway 或不在 job 中时该 flag 为空操作（零成本）；
       job 禁 breakaway（WinError 5）→ 降级 WMI Win32_Process.Create
       （WMI 服务在 job 外创建进程，天然逃逸），返回 _WmiDetachedProcess
       shim（pid/poll/wait/terminate/kill 对齐 Popen；stdio 句柄不可继承，
       stdout_to_devnull=False 的调试诉求在降级路径失效；但 stdout_path/
       stderr_path 日志落盘诉求经 cmd 壳层重定向在降级路径同样生效）。
    5. stdout_path/stderr_path（S3 观测层，2026-08-14 worktree wipe 裁定书）：
       提供则 stdio 落盘到指定日志文件（append 模式，父进程句柄 spawn 后即关，
       子进程持有 duplicate 句柄继续写；WMI 降级路径走 cmd 壳层重定向）——
       worker "启动即死无日志" 治本。与 *_to_devnull 互斥：path 优先，
       对应 devnull 标志被忽略。

    Args:
        cmd: 命令列表（如 [sys.executable, "-m", "zephyr.foo.daemon", sid])
        cwd: 工作目录
        env: 环境变量（None 则继承父）
        stdin_to_devnull: True 则 stdin=subprocess.DEVNULL
        stdout_to_devnull: True 则 stdout=subprocess.DEVNULL（stdout_path 提供时忽略）
        stderr_to_devnull: True 则 stderr=subprocess.DEVNULL（stderr_path 提供时忽略）
        stdout_path: stdout 落盘日志文件路径（append）；WMI 降级路径走 cmd 壳层重定向
        stderr_path: stderr 落盘日志文件路径（append）；WMI 降级路径走 cmd 壳层重定向

    Returns:
        subprocess.Popen（已启动，pid 可读）；WMI 降级路径返回 _WmiDetachedProcess
    """
    popen_kwargs: dict = {
        "close_fds": True,
        "cwd": cwd,
        "env": env,
    }
    # S3：stdio 落盘句柄（spawn 后父进程关闭，子进程持有 duplicate 继续写）
    _log_handles: list = []
    if stdin_to_devnull:
        popen_kwargs["stdin"] = subprocess.DEVNULL
    if stdout_path:
        _h = open(stdout_path, "ab")  # noqa: r144-open 句柄须随 Popen 调用传递，finally 块统一关闭，with 语义不兼容
        _log_handles.append(_h)
        popen_kwargs["stdout"] = _h
    elif stdout_to_devnull:
        popen_kwargs["stdout"] = subprocess.DEVNULL
    if stderr_path:
        _h = open(stderr_path, "ab")  # noqa: r144-open 同上——句柄生命周期由 finally 显式管理
        _log_handles.append(_h)
        popen_kwargs["stderr"] = _h
    elif stderr_to_devnull:
        popen_kwargs["stderr"] = subprocess.DEVNULL
    if os.name == "nt":
        popen_kwargs["creationflags"] = _hidden_creationflags() | _CREATE_BREAKAWAY_FROM_JOB
    else:
        popen_kwargs["start_new_session"] = True  # POSIX: 新 session（setsid）
    try:
        try:
            return subprocess.Popen(cmd, **popen_kwargs)
        except PermissionError:
            if os.name != "nt":
                raise
            # WinError 5：父进程在禁 breakaway 的 Job Object 内（IDE 终端
            # KILL_ON_JOB_CLOSE 实测）——CreateProcess 无法逃逸 job，降级 WMI。
            # S3：stdout_path/stderr_path 透传——WMI 路径改用 cmd 壳层重定向
            # 落盘（句柄继承不可用），覆盖面更全（含解释器启动期错误）。
            logger.warning(
                "spawn_python_hidden: CREATE_BREAKAWAY_FROM_JOB denied (job object "
                "forbids breakaway), falling back to WMI Win32_Process.Create"
            )
            return _spawn_detached_via_wmi(
                cmd,
                cwd=cwd,
                env=env,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
            )
    finally:
        # 父进程句柄即刻关闭——CreateProcess/ fork 已把句柄 duplicate 给子进程，
        # 父关闭不影响子继续写；不关闭则父进程句柄泄漏（长驻 gateway 场景）。
        for _h in _log_handles:
            try:
                _h.close()
            except OSError:
                pass


def is_pid_alive(pid: int) -> bool:
    """检查 PID 对应进程是否存活（跨平台，僵尸锁/PID 文件清理真源唯一）。

    根因：进程崩溃（kill/异常退出）时锁文件/PID 文件残留。仅靠 TTL 过期太慢
    （如 gateway 全局锁 TTL=1800s），僵尸锁在超时窗口内永远等不到 TTL 过期
    （实测阻塞 3min+）。本函数在 TTL 检查前先查 PID 存活，僵尸锁立即清理
    （零窗口期）。

    调用方（真源唯一，禁止重复造轮子——曾三处分裂，红蓝对抗归一）：
      - zephyr.gov_enforcement.rule_bridge.git_commit_gateway._GlobalCommitLock（僵尸锁检测）
      - scripts.ide_health_service（daemon PID 文件 stale 清理）
      - scripts.governance.meta._concurrency.ProcessLock（L0 全局锁 stale 清理）

    红蓝对抗修复：防御性类型检查——None/str/float 等非法类型直接返回 False
    （_concurrency 调用点 holder.get("pid", -1) 可能返回非 int，无此检查会
    TypeError 中断）。Win32 GetLastError 区分"进程不存在"
    (ERROR_INVALID_PARAMETER 87) vs "权限不足"(ERROR_ACCESS_DENIED 5，
    如 PID 4 System)-> 算存活。
    """
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        if sys.platform == "win32":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            err = kernel32.GetLastError()
            return err == 5  # ERROR_ACCESS_DENIED
        else:
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, PermissionError, OSError, ValueError):
        return False


@dataclass
class PooledProcess:
    name: str
    process: subprocess.Popen
    created_at: float = field(default_factory=time.monotonic)
    reuse_count: int = 0
    last_used_at: float = field(default_factory=time.monotonic)

    @property
    def is_alive(self) -> bool:
        return self.process.poll() is None

    @property
    def pid(self) -> int | None:
        return self.process.pid


class MCPProcessPool:
    def __init__(
        self, max_processes: int = 30, zombie_check_interval: float = 60.0, idle_timeout_s: float = 600.0
    ) -> None:
        self._max_processes = max_processes
        self._zombie_check_interval = zombie_check_interval
        self._idle_timeout_s = idle_timeout_s
        self._pool: dict[str, PooledProcess] = {}
        self._lock = threading.Lock()
        self._zombie_thread: threading.Thread | None = None
        self._zombie_running = False
        # W2 治本: stop 事件让扫描循环即时退出（替代 sleep 长等待），stop 可 join
        self._zombie_stop = threading.Event()

    def reap_zombies(self) -> int:
        """公共接口：reap_zombies（Stage 4 公共化）。"""
        return self._reap_zombies()

    # ----- Stage 4 公共化：属性 getter -----
    @property
    def idle_timeout_s(self) -> float:
        """只读：idle_timeout_s（Stage 4 公共化）。"""
        return self._idle_timeout_s

    @idle_timeout_s.setter
    def idle_timeout_s(self, value):
        """写入：idle_timeout_s（Stage 4 公共化）。"""
        self._idle_timeout_s = value

    @property
    def lock(self) -> threading.Lock:
        """只读：lock（Stage 4 公共化）。"""
        return self._lock

    @lock.setter
    def lock(self, value):
        """写入：lock（Stage 4 公共化）。"""
        self._lock = value

    @property
    def pool(self) -> dict[str, PooledProcess]:
        """只读：pool（Stage 4 公共化）。"""
        return self._pool

    @pool.setter
    def pool(self, value):
        """写入：pool（Stage 4 公共化）。"""
        self._pool = value

    def get_or_create(
        self,
        name: str,
        cmd: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> PooledProcess | None:
        with self.lock:
            entry = self.pool.get(name)
            if entry is not None:
                if entry.is_alive:
                    entry.reuse_count += 1
                    entry.last_used_at = time.monotonic()
                    return entry
                else:
                    self._remove_entry(name)

            if len(self.pool) >= self._max_processes:
                logger.warning(
                    "MCPProcessPool: max processes (%d) reached, cannot create '%s'",
                    self._max_processes,
                    name,
                )
                return None

            if cmd is None:
                return None

            try:
                proc_env = {**os.environ, **(env or {})}
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=proc_env,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.exception("MCPProcessPool: failed to create process '%s'", name, exc_info=True)
                return None

            entry = PooledProcess(name=name, process=proc)
            self.pool[name] = entry
            logger.info("MCPProcessPool: created process '%s' (pid=%d)", name, proc.pid)
            return entry

    def terminate(self, name: str) -> bool:
        with self.lock:
            entry = self.pool.get(name)
            if entry is None:
                return False
            self._remove_entry(name)
            return True

    def terminate_all(self) -> int:
        with self.lock:
            count = len(self.pool)
            for name in list(self.pool.keys()):
                self._remove_entry(name)
            return count

    def get_stats(self) -> ProcessPoolStats:
        with self.lock:
            active = sum(1 for e in self.pool.values() if e.is_alive)
            zombies = sum(1 for e in self.pool.values() if not e.is_alive)
            reuse = sum(e.reuse_count for e in self.pool.values())
            now = time.monotonic()
            idle = sum(
                1
                for e in self.pool.values()
                if e.is_alive and self.idle_timeout_s > 0 and (now - e.last_used_at) > self.idle_timeout_s
            )
            return ProcessPoolStats(
                active_processes=active,
                max_processes=self._max_processes,
                reuse_count=reuse,
                zombie_count=zombies,
                idle_count=idle,
            )

    def start_zombie_scanner(self) -> None:
        if self._zombie_running:
            return
        self._zombie_stop.clear()
        self._zombie_running = True
        self._zombie_thread = threading.Thread(
            target=self._zombie_scan_loop,
            daemon=True,
            name="process-pool-zombie-scanner",
        )
        self._zombie_thread.start()

    def stop_zombie_scanner(self, timeout: float = 5.0) -> None:
        self._zombie_running = False
        # W2 治本: 唤醒等待中的扫描线程并 join，确保线程真正退出而非仅置标志
        self._zombie_stop.set()
        thread = self._zombie_thread
        if thread is not None and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=timeout)
            if thread.is_alive():
                logger.warning(
                    "MCPProcessPool: zombie scanner thread did not stop within %.1fs",
                    timeout,
                )
        self._zombie_thread = None

    def _zombie_scan_loop(self) -> None:
        while self._zombie_running:
            try:
                self._reap_zombies()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.exception("MCPProcessPool: zombie scan failed", exc_info=True)
            # W2 治本: Event.wait 替代 sleep，stop_zombie_scanner 可即时唤醒
            self._zombie_stop.wait(self._zombie_check_interval)

    def _reap_zombies(self) -> int:
        with self.lock:
            zombie_names = [name for name, entry in self.pool.items() if not entry.is_alive]
            now = time.monotonic()
            idle_names = [
                name
                for name, entry in self.pool.items()
                if entry.is_alive and self.idle_timeout_s > 0 and (now - entry.last_used_at) > self.idle_timeout_s
            ]
            for name in zombie_names:
                self._remove_entry(name)
                logger.info("MCPProcessPool: reaped zombie process '%s'", name)
            for name in idle_names:
                self._remove_entry(name)
                logger.info(
                    "MCPProcessPool: reaped idle process '%s' (idle_timeout=%.0fs)",
                    name,
                    self.idle_timeout_s,
                )
            return len(zombie_names) + len(idle_names)

    def _remove_entry(self, name: str) -> None:
        entry = self.pool.pop(name, None)
        if entry is not None:
            # 5.144.3 修复: 先 terminate()->wait()->关闭管道（申请逆序释放）
            # 原顺序：先关管道再 terminate, 子进程写日志触发 BrokenPipeError, 关 stdin 发 EOF 让子进程提前退出跳过自身清理
            try:
                entry.process.terminate()
                entry.process.wait(timeout=5.0)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                try:
                    entry.process.kill()
                    entry.process.wait(timeout=2.0)
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("suppressed error in process_pool", exc_info=True)
            for stream in (entry.process.stdin, entry.process.stdout, entry.process.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.debug("suppressed error in process_pool", exc_info=True)
