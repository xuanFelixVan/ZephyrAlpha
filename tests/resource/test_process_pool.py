# [A_test] module_id: MOD-GOV_process_pool | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-551 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_process_pool
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_process_pool.py - MCPProcessPool unit tests
=================================================

TASK-INF-0142 Phase 4 verification.
"""


import sys
import time

from zephyr.shared.infra.process_pool import MCPProcessPool


class TestProcessPoolBasic:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_empty_pool(self):
        pool = self._make_pool()
        stats = pool.get_stats()
        assert stats.active_processes == 0
        assert stats.max_processes == 30

    def test_create_process(self):
        pool = self._make_pool()
        entry = pool.get_or_create("echo-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert entry is not None
        assert entry.is_alive
        stats = pool.get_stats()
        assert stats.active_processes == 1

    def test_reuse_process(self):
        pool = self._make_pool()
        entry1 = pool.get_or_create("reuse-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        entry2 = pool.get_or_create("reuse-test")
        assert entry1 is entry2
        assert entry2.reuse_count == 1

    def test_max_processes_limit(self):
        pool = self._make_pool(max_processes=2)
        pool.get_or_create("p1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("p2", [sys.executable, "-c", "import time; time.sleep(60)"])
        result = pool.get_or_create("p3", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert result is None

    def test_terminate_process(self):
        pool = self._make_pool()
        pool.get_or_create("term-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert pool.terminate("term-test") is True
        stats = pool.get_stats()
        assert stats.active_processes == 0

    def test_terminate_nonexistent(self):
        pool = self._make_pool()
        assert pool.terminate("nope") is False

    def test_terminate_all(self):
        pool = self._make_pool()
        pool.get_or_create("t1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("t2", [sys.executable, "-c", "import time; time.sleep(60)"])
        count = pool.terminate_all()
        assert count == 2
        assert pool.get_stats().active_processes == 0


class TestProcessPoolZombie:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_dead_process_detected(self):
        pool = self._make_pool()
        entry = pool.get_or_create("quick-die", [sys.executable, "-c", "pass"])
        time.sleep(1.0)
        assert not entry.is_alive
        reaped = pool.reap_zombies()
        assert reaped >= 1

    def test_get_or_create_replaces_dead(self):
        pool = self._make_pool()
        pool.get_or_create("replace-test", [sys.executable, "-c", "pass"])
        time.sleep(1.0)
        new_entry = pool.get_or_create("replace-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert new_entry is not None
        assert new_entry.is_alive


class TestProcessPoolStats:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_stats_with_active(self):
        pool = self._make_pool()
        pool.get_or_create("s1", [sys.executable, "-c", "import time; time.sleep(60)"])
        stats = pool.get_stats()
        assert stats.active_processes == 1
        assert stats.reuse_count == 0

    def test_reuse_count_increments(self):
        pool = self._make_pool()
        pool.get_or_create("r1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("r1")
        pool.get_or_create("r1")
        stats = pool.get_stats()
        assert stats.reuse_count == 2


class TestSpawnJobEscape:
    """#ARCH-SPAWN-JOB-KILL-001：detached spawn 的 Job Object 逃逸。

    IDE 终端把命令跑在 KILL_ON_JOB_CLOSE Job 内——子进程不逃逸会随父命令
    退出被连坐杀死（spawn 返回 PID 但进程从未真实运行的病根）。
    """

    def test_creationflags_include_breakaway_on_nt(self, monkeypatch):
        """Windows detached spawn 必须带 CREATE_BREAKAWAY_FROM_JOB（逃逸首选通道）。"""
        import subprocess

        import zephyr.shared.infra.process_pool as pp

        captured: dict = {}

        class _FakePopen:
            def __init__(self, cmd, **kwargs):
                captured.update(kwargs)
                self.pid = 43210

        monkeypatch.setattr(pp.os, "name", "nt")
        monkeypatch.setattr(subprocess, "Popen", _FakePopen)
        proc = pp.spawn_python_hidden([sys.executable, "-c", "pass"])
        assert proc.pid == 43210
        assert captured["creationflags"] & pp._CREATE_BREAKAWAY_FROM_JOB, (
            f"creationflags 缺 CREATE_BREAKAWAY_FROM_JOB：{captured['creationflags']:#x}"
        )
        # 无闪窗铁律不破：CREATE_NO_WINDOW 仍在
        assert captured["creationflags"] & 0x08000000

    def test_permission_error_falls_back_to_wmi(self, monkeypatch):
        """job 禁 breakaway（WinError 5）→ 降级 _spawn_detached_via_wmi。"""
        import subprocess

        import zephyr.shared.infra.process_pool as pp

        def _denied_popen(cmd, **kwargs):
            raise PermissionError(5, "拒绝访问", None, 5)

        sentinel = object()
        monkeypatch.setattr(pp.os, "name", "nt")
        monkeypatch.setattr(subprocess, "Popen", _denied_popen)
        monkeypatch.setattr(pp, "_spawn_detached_via_wmi", lambda cmd, **kw: sentinel)
        assert pp.spawn_python_hidden([sys.executable, "-c", "pass"]) is sentinel

    def test_permission_error_reraised_on_posix(self, monkeypatch):
        """POSIX 无 Job Object 语义——PermissionError 不降级，直接抛。"""
        import subprocess

        import pytest

        import zephyr.shared.infra.process_pool as pp

        def _denied_popen(cmd, **kwargs):
            raise PermissionError(13, "Permission denied")

        monkeypatch.setattr(pp.os, "name", "posix")
        monkeypatch.setattr(subprocess, "Popen", _denied_popen)
        with pytest.raises(PermissionError):
            pp.spawn_python_hidden([sys.executable, "-c", "pass"])


class TestWmiSpawnHelpers:
    """_spawn_detached_via_wmi / _ps_single_quote 纯逻辑单测（mock powershell 出口）。"""

    def test_ps_single_quote_escapes(self):
        from zephyr.shared.infra.process_pool import _ps_single_quote

        assert _ps_single_quote("abc") == "'abc'"
        assert _ps_single_quote("it's") == "'it''s'"
        assert _ps_single_quote("") == "''"

    def _fake_completed(self, stdout: str):
        import subprocess

        return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

    def test_wmi_spawn_parses_sentinel(self, monkeypatch):
        import zephyr.shared.infra.process_pool as pp

        monkeypatch.setattr(
            pp,
            "run_subprocess_hidden",
            lambda cmd, **kw: self._fake_completed("ZEPHYR_WMI_SPAWN|0|4242\r\n"),
        )
        proc = pp._spawn_detached_via_wmi(["python.exe", "-c", "pass"], env={"A": "1"})
        assert isinstance(proc, pp._WmiDetachedProcess)
        assert proc.pid == 4242

    def test_wmi_spawn_nonzero_return_value_raises(self, monkeypatch):
        import pytest

        import zephyr.shared.infra.process_pool as pp

        monkeypatch.setattr(
            pp,
            "run_subprocess_hidden",
            lambda cmd, **kw: self._fake_completed("ZEPHYR_WMI_SPAWN|9|\r\n"),
        )
        with pytest.raises(RuntimeError, match="ReturnValue=9"):
            pp._spawn_detached_via_wmi(["python.exe", "-c", "pass"])

    def test_wmi_spawn_missing_sentinel_raises(self, monkeypatch):
        import pytest

        import zephyr.shared.infra.process_pool as pp

        monkeypatch.setattr(
            pp,
            "run_subprocess_hidden",
            lambda cmd, **kw: self._fake_completed("some powershell error"),
        )
        with pytest.raises(RuntimeError, match="sentinel missing"):
            pp._spawn_detached_via_wmi(["python.exe", "-c", "pass"])

    def test_wmi_spawn_script_contents(self, monkeypatch):
        """脚本契约（#ARCH-105 新版）：ShowWindow=SW_HIDE、env 经临时文件传输
        （脚本不内联 env 内容）、cwd 落 CurrentDirectory、返回后 env 文件已清。"""
        import re

        import zephyr.shared.infra.process_pool as pp

        captured: dict = {}

        def _fake_run(cmd, **kw):
            captured["script"] = cmd[-1]
            m = re.search(r"\$envFile = '([^']+)'", cmd[-1])
            assert m, "脚本应经 $envFile 引用传输 env"
            captured["env_file"] = m.group(1)
            with open(captured["env_file"], "rb") as fh:
                captured["env_bytes"] = fh.read()
            return self._fake_completed("ZEPHYR_WMI_SPAWN|0|1\n")

        monkeypatch.setattr(pp, "run_subprocess_hidden", _fake_run)
        pp._spawn_detached_via_wmi(
            ["python.exe", "-m", "foo"],
            cwd="d:/work",
            env={"ZW_TEST": "v1", "QUOTE": "it's"},
        )
        script = captured["script"]
        assert "$startup.ShowWindow = [uint16]0" in script
        assert "CreateFlags" not in script  # WMI 拒 CreateFlags（RV=21 实证）
        assert "Get-Content -LiteralPath $envFile -Encoding UTF8" in script
        assert "CurrentDirectory = 'd:/work'" in script
        # env 不内联进脚本——任何异常路径（TimeoutExpired.args）都不再携带 env
        assert "ZW_TEST=v1" not in script
        assert "QUOTE" not in script
        # env 文件：utf-8-sig BOM（保 PS5.1 对非 ASCII 值正确解码）+ 全量条目
        assert captured["env_bytes"].startswith(b"\xef\xbb\xbf")
        env_text = captured["env_bytes"].decode("utf-8-sig")
        assert "ZW_TEST=v1\n" in env_text
        assert "QUOTE=it's\n" in env_text
        # 双侧清理：函数返回后 env 文件不残留
        import os

        assert not os.path.exists(captured["env_file"])

    def test_wmi_spawn_secret_keys_stripped(self, monkeypatch):
        """敏感键剥离（#ARCH-105）：令牌/密钥语义变量不进 WMI 传输通道。"""
        import re

        import zephyr.shared.infra.process_pool as pp

        captured: dict = {}

        def _fake_run(cmd, **kw):
            captured["script"] = cmd[-1]
            m = re.search(r"\$envFile = '([^']+)'", cmd[-1])
            with open(m.group(1), encoding="utf-8-sig") as fh:
                captured["env_text"] = fh.read()
            return self._fake_completed("ZEPHYR_WMI_SPAWN|0|1\n")

        monkeypatch.setattr(pp, "run_subprocess_hidden", _fake_run)
        pp._spawn_detached_via_wmi(
            ["python.exe", "-c", "pass"],
            env={
                "GITHUB_TOKEN": "ghp_secret",
                "DEEPSEEK_API_KEY": "sk-secret",
                "MY_PASSWORD": "pw",
                "ZW_NORMAL": "keep",
                "ZEPHYR_SESSION_ID": "ai-test",
            },
        )
        assert "ghp_secret" not in captured["env_text"]
        assert "sk-secret" not in captured["env_text"]
        assert "pw" not in captured["env_text"]
        assert "ghp_secret" not in captured["script"]
        assert "ZW_NORMAL=keep\n" in captured["env_text"]
        assert "ZEPHYR_SESSION_ID=ai-test\n" in captured["env_text"]

    def test_wmi_spawn_timeout_sanitized(self, monkeypatch):
        """超时脱敏（#ARCH-105）：TimeoutExpired 不回传——其 args 含完整命令，
        病史为全量 env 随异常喷入 reconcile status JSON 明文落盘。"""
        import subprocess

        import pytest

        import zephyr.shared.infra.process_pool as pp

        def _timeout_run(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=60)

        monkeypatch.setattr(pp, "run_subprocess_hidden", _timeout_run)
        with pytest.raises(RuntimeError, match="timed out") as exc_info:
            pp._spawn_detached_via_wmi(
                ["python.exe", "-c", "pass"],
                env={"GITHUB_TOKEN": "ghp_secret"},
            )
        assert "ghp_secret" not in str(exc_info.value)
        assert "GITHUB_TOKEN" not in str(exc_info.value)


class TestWmiDetachedProcessShim:
    """_WmiDetachedProcess 的 Popen 兼容语义（真实进程集成验证）。"""

    def test_poll_wait_terminate_lifecycle(self):
        import subprocess

        import zephyr.shared.infra.process_pool as pp

        if pp.os.name != "nt":
            import pytest

            pytest.skip("shim 仅 Windows 语义")
        real = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            shim = pp._WmiDetachedProcess(real.pid)
            assert shim.poll() is None  # 存活
            shim.terminate()
            rc = shim.wait(timeout=10)
            assert rc is not None
            assert shim.poll() == rc  # 退出码缓存
        finally:
            real.wait(timeout=10)  # 回收真实句柄

    def test_wait_timeout_raises(self):
        import subprocess

        import pytest

        import zephyr.shared.infra.process_pool as pp

        if pp.os.name != "nt":
            pytest.skip("shim 仅 Windows 语义")
        real = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            shim = pp._WmiDetachedProcess(real.pid)
            with pytest.raises(subprocess.TimeoutExpired):
                shim.wait(timeout=0.2)
        finally:
            real.terminate()
            real.wait(timeout=10)

    def test_poll_dead_pid_returns_minus_one(self):
        import zephyr.shared.infra.process_pool as pp

        if pp.os.name != "nt":
            import pytest

            pytest.skip("shim 仅 Windows 语义")
        shim = pp._WmiDetachedProcess(99999999)  # 不存在
        assert shim.poll() == -1
        assert shim.wait(timeout=1) == -1  # 幂等（缓存）

    def test_no_resource_warning_on_gc(self):
        """shim 无 CreateProcess 句柄——GC 回收不触发 Popen.__del__ ResourceWarning。"""
        import warnings

        import zephyr.shared.infra.process_pool as pp

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            shim = pp._WmiDetachedProcess(99999999)
            del shim
        assert not [w for w in caught if issubclass(w.category, ResourceWarning)]
