# [MODULE] tests.zephyr.trading.test_ollama_process_manager
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
"""_OllamaProcessManager.terminate_proc 树杀单测（2026-09-15 孤儿事故补丁）。

Windows 上裸 terminate() 只杀 ollama.exe 父进程，llama-server 子进程全部孤儿化
（9 实例 ≈12GB 撑爆提交内存实证）。验证：先杀子树再杀父、查询失败不阻断收尾、
proc 引用置空。psutil 以 fake module 注入 sys.modules，零真实进程依赖。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.trading.auto_runtime_core import _OllamaProcessManager  # noqa: E402


class FakePsutilEnv:
    """可控 psutil 替身：记录调用序列，可配置子进程集合与 wait_procs 存活集。"""

    def __init__(self):
        self.log: list[str] = []
        self.Error = type("FakePsutilError", (Exception,), {})
        self.children: list[object] = []
        self.alive_after_wait: list[object] = []
        self.lookup_raises = False

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env = self

        class _Parent:
            def children(self, recursive: bool = True) -> list[object]:
                if env.lookup_raises:
                    raise env.Error("parent gone")
                return list(env.children)

        class _Module(types.ModuleType):
            pass

        fake = types.ModuleType("psutil")
        fake.Error = self.Error
        fake.Process = lambda pid: _Parent()
        fake.wait_procs = lambda procs, timeout=None: (procs, env.alive_after_wait)
        monkeypatch.setitem(sys.modules, "psutil", fake)

    def child(self, resist_terminate: bool = False) -> object:
        env = self

        class _Child:
            def terminate(self) -> None:
                if resist_terminate:
                    raise env.Error("terminate refused")
                env.log.append("child-terminate")

            def kill(self) -> None:
                env.log.append("child-kill")

        return _Child()


class _FakePopen:
    def __init__(self, log: list[str]):
        self.pid = 4242
        self._log = log

    def terminate(self) -> None:
        self._log.append("parent-terminate")

    def wait(self, timeout: float | None = None) -> int:
        self._log.append("parent-wait")
        return 0


class _FakeCore:
    def __init__(self, log: list[str]):
        self._ollama_proc: object | None = _FakePopen(log)


def test_children_killed_before_parent(monkeypatch):
    env = FakePsutilEnv()
    env.install(monkeypatch)
    env.children = [env.child(), env.child()]
    core = _FakeCore(env.log)
    _OllamaProcessManager.terminate_proc(core)
    assert env.log == ["child-terminate", "child-terminate", "parent-terminate", "parent-wait"]
    assert core._ollama_proc is None


def test_no_proc_is_noop(monkeypatch):
    env = FakePsutilEnv()
    env.install(monkeypatch)
    core = _FakeCore(env.log)
    core._ollama_proc = None
    _OllamaProcessManager.terminate_proc(core)
    assert env.log == []


def test_parent_lookup_failure_still_terminates_proc(monkeypatch):
    env = FakePsutilEnv()
    env.install(monkeypatch)
    env.lookup_raises = True
    core = _FakeCore(env.log)
    _OllamaProcessManager.terminate_proc(core)
    assert env.log == ["parent-terminate", "parent-wait"]
    assert core._ollama_proc is None


def test_tree_lookup_failure_outside_error_swallows_and_terminates(monkeypatch):
    # 整个树杀块兜底 except Exception：意外异常不阻断父进程收尾
    env = FakePsutilEnv()
    env.install(monkeypatch)
    monkeypatch.setattr(
        sys.modules["psutil"],
        "Process",
        lambda pid: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    core = _FakeCore(env.log)
    _OllamaProcessManager.terminate_proc(core)
    assert env.log == ["parent-terminate", "parent-wait"]


def test_proc_reference_cleared(monkeypatch):
    env = FakePsutilEnv()
    env.install(monkeypatch)
    core = _FakeCore(env.log)
    _OllamaProcessManager.terminate_proc(core)
    assert core._ollama_proc is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
