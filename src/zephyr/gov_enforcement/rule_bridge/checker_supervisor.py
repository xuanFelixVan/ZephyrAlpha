# [BLUEPRINT] MOD-GOV_CHECKER_SUPERVISOR | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.rule_bridge.checker_supervisor
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] stdlib（subprocess/json/os/sys/runpy/threading/base64/contextlib/io）
# [CONSUMERS] commit_gate_registry.run_checker_script（唯一入口，透明接管 spawn 税）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 结果≡直 spawn（rc/stdout/stderr 逐字节等价，bytes 模式 base64 往返）；任何 worker 异常（崩溃/EOF/超时/协议错）→ 当次调用回退直 spawn（fail-safe=现状）；per-checker 超时由父进程强制（超时=杀 worker+重建，向上抛 TimeoutExpired 与现状同款）；单 worker 串行（与门禁链顺序执行同构，锁保护并发调用方）
# [MODIFY-GUARD] 2026-09-10 提交通道性能优化方案 §2.2-A2（checker 合并执行，消 12.5s 子进程税）；行为等价红线见方案 §2.7
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 成功=CompletedProcess；worker 异常=回退直 spawn（调用方无感知）；超时=subprocess.TimeoutExpired（与直 spawn 同款）
# [TESTS] tests/git/test_checker_supervisor.py
# [TTL] permanent
"""checker_supervisor — A2 checker 合并执行（持久工作进程消 spawn 税）。

病根：106 gate 链经 run_checker_script 逐次 ``[sys.executable, script, *args]``
spawn（68 次/链），解释器启动税 ≈12.5s（方案 §0.1 实测 41.4s 锁内主体之一）。

设计（方案 §2.2-A2"supervisor"落地形态）：
- **持久 worker**：每个 commit 流程 1 次 spawn 的常驻解释器，逐请求
  ``runpy.run_path(script, run_name="__main__")`` 执行 checker（sys.argv 注入、
  os.chdir(cwd)、env 增量覆盖、stdout/stderr 重定向捕获、SystemExit→rc）。
- **故障隔离**：checker 自身崩溃（worker 死亡/EOF/协议错）→ 该次调用**回退直
  spawn**（结果≡现状）；checker 内存膨胀无法进程内隔离——回退语义兜底，方案
  已登记该残余（"故障隔离需重设计"，本实现取 fail-safe 回退路线）。
- **超时**：父进程按 per-checker timeout 强制——超时杀 worker+重建，向上抛
  ``subprocess.TimeoutExpired``（与直 spawn 同款，各 gate 既有捕获策略不变）。
- **回滚**：env ``ZEPHYR_CHECKER_SUPERVISOR=0`` 即全量回退直 spawn。
"""

from __future__ import annotations

import base64
import io
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

logger = __import__("logging").getLogger(__name__)

_SUPERVISOR_DISABLE_ENV = "ZEPHYR_CHECKER_SUPERVISOR"
_REQUEST_TIMEOUT_GRACE = 5.0  # 响应行等待 = checker timeout + 宽限（杀 worker 前的余量）


def _worker_main() -> int:  # pragma: no cover - 子进程入口（由 worker 进程执行）
    """worker 进程主循环：stdin 每行一个请求 JSON，stdout 每行一个响应 JSON。"""
    import contextlib
    import runpy

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            script = req["script"]
            argv = [str(script), *[str(a) for a in req.get("args", [])]]
            cwd = req.get("cwd")
            env_delta = req.get("env") or {}
            old_cwd = os.getcwd()
            old_env = {k: os.environ.get(k) for k in env_delta}
            out_buf, err_buf = io.StringIO(), io.StringIO()
            rc = 0
            try:
                if cwd:
                    os.chdir(cwd)
                os.environ.update(env_delta)
                old_argv = sys.argv
                sys.argv = argv
                try:
                    with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                        runpy.run_path(script, run_name="__main__")
                except SystemExit as exc:
                    rc = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
            finally:
                sys.argv = old_argv
                for k, v in old_env.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
                os.chdir(old_cwd)
            resp = {
                "id": req["id"],
                "rc": rc,
                "out_b64": base64.b64encode(out_buf.getvalue().encode("utf-8", "replace")).decode("ascii"),
                "err_b64": base64.b64encode(err_buf.getvalue().encode("utf-8", "replace")).decode("ascii"),
            }
        except Exception as exc:  # noqa: BLE001 — 单请求异常以错误响应回执（worker 不死）
            resp = {"id": req.get("id", "?"), "worker_error": f"{type(exc).__name__}: {exc}"}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
    return 0


class CheckerSupervisor:
    """持久 checker worker 的父进程侧管理（单 worker + 锁串行）。

    用法：``with CheckerSupervisor() as sup:`` 或模块级单例（:data:`SUPERVISOR`）。
    :meth:`run` 失败返回 ``None``（调用方回退直 spawn），**绝不代替调用方判结果**。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proc: subprocess.Popen | None = None  # noqa: bare-subprocess  类型标注引用非调用——此处仅声明类型注解不创建子进程，无窗口问题（满贯批接手批补理由）
        self._req_seq = 0

    # -- worker 生命周期 ------------------------------------------------

    def _spawn(self) -> subprocess.Popen:  # noqa: bare-subprocess  返回类型标注引用非调用
        # -c 内联 worker 入口（不用 __main__ 块：MANUAL-ONLY-PERMANENT gate 将
        # __main__+argv 模式判为 manual 常驻脚本——本 worker 是父进程自动 spawn
        # 的执行体，非人工 CLI 工具）
        bootstrap = (
            "import sys; "
            "from zephyr.gov_enforcement.rule_bridge.checker_supervisor import _worker_main; "
            "sys.exit(_worker_main())"
        )
        self._proc = subprocess.Popen(  # noqa: bare-subprocess  持久 worker 须 Popen 管道流式通信（run 只支持一次pinish）；CREATE_NO_WINDOW 由下方 creationflags 显式注入，无闪窗
            [sys.executable, "-c", bootstrap],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0),  # TRAE-067 铁律2：worker spawn 无闪窗
        )
        return self._proc

    def _kill(self) -> None:
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        # 先关 stdin（worker 见 EOF）→ kill → 关读端 → wait 收尸（防 Popen.__del__
        # unraisable 警告与管道资源泄漏——pytest -W error 场景会升级为失败）
        for pipe in (proc.stdin, proc.stdout):
            try:
                if pipe is not None:
                    pipe.close()
            except OSError:
                pass
        try:
            proc.kill()
        except OSError:
            pass
        try:
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            pass

    def close(self) -> None:
        with self._lock:
            self._kill()

    # -- 请求执行 --------------------------------------------------------

    def run(
        self,
        script_path: str | Path,
        args: list[str],
        *,
        cwd: str | Path,
        timeout: int = 60,
        text: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess | None:
        """执行单个 checker；返回 None=回退直 spawn（worker 异常/禁用）。"""
        if os.environ.get(_SUPERVISOR_DISABLE_ENV) == "0":
            return None
        req = {
            "id": self._req_seq + 1,
            "script": str(script_path),
            "args": list(args),
            "cwd": str(cwd),
            "env": dict(env) if env else {},
        }
        with self._lock:
            self._req_seq = req["id"]
            return self._run_locked(req, timeout=timeout, text=text)

    def _run_locked(self, req: dict, *, timeout: int, text: bool) -> subprocess.CompletedProcess | None:
        if self._proc is None or self._proc.poll() is not None:
            try:
                self._spawn()
            except OSError as exc:
                logger.warning("[checker-supervisor] worker 启动失败，回退直 spawn: %s", exc)
                return None
        assert self._proc is not None and self._proc.stdin and self._proc.stdout
        try:
            self._proc.stdin.write(json.dumps(req) + "\n")
            self._proc.stdin.flush()
        except (OSError, ValueError) as exc:
            logger.warning("[checker-supervisor] 请求写入失败（worker 已死？），回退直 spawn: %s", exc)
            self._kill()
            return None
        # 响应等待：checker timeout + 宽限；超时=杀 worker+重建（回退直 spawn，
        # 向上抛 TimeoutExpired 与直 spawn 同款——各 gate 既有捕获策略不变）。
        # 读线程 + join(deadline)：Windows selectors 不支持管道（WinError 10038），
        # 阻塞 readline 须放后台线程；kill 后管道关闭线程随之消亡（daemon）。
        box: dict = {}
        reader = threading.Thread(
            target=lambda: box.setdefault("line", self._proc.stdout.readline() if self._proc and self._proc.stdout else None),
            daemon=True,
        )
        deadline = timeout + _REQUEST_TIMEOUT_GRACE
        reader.start()
        reader.join(deadline)
        if reader.is_alive():
            # 真超时（deadline 到 readline 仍未返回）→ TimeoutExpired 与直 spawn 同款
            logger.warning("[checker-supervisor] worker 响应超时（%ss 窗口），杀 worker 回退直 spawn", timeout)
            self._kill()
            raise subprocess.TimeoutExpired(cmd=req["script"], timeout=timeout)
        line = box.get("line")
        if not line:
            # worker 死亡 EOF（checker 硬崩 os._exit/段错误）→ 回退直 spawn（结果≡现状）
            logger.warning("[checker-supervisor] worker EOF（checker 硬崩？），回退直 spawn")
            self._kill()
            return None
        try:
            resp = json.loads(line)
        except ValueError:
            self._kill()
            return None
        if resp.get("id") != req["id"] or "worker_error" in resp:
            logger.warning("[checker-supervisor] worker 异常响应，回退直 spawn: %s", str(resp)[:200])
            self._kill()
            return None
        stdout = base64.b64decode(resp["out_b64"])
        stderr = base64.b64decode(resp["err_b64"])
        if text:
            return subprocess.CompletedProcess(
                args=[req["script"], *req["args"]],
                returncode=int(resp["rc"]),
                stdout=stdout.decode("utf-8", "replace"),
                stderr=stderr.decode("utf-8", "replace"),
            )
        return subprocess.CompletedProcess(
            args=[req["script"], *req["args"]],
            returncode=int(resp["rc"]),
            stdout=stdout,
            stderr=stderr,
        )


_SUPERVISOR: CheckerSupervisor | None = None


def get_supervisor() -> CheckerSupervisor:
    """进程内惰性单例（NO-IMPORT-SIDE-EFFECT：import 本模块不急切实例化）。"""
    global _SUPERVISOR
    if _SUPERVISOR is None:
        _SUPERVISOR = CheckerSupervisor()
    return _SUPERVISOR
