# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-DATA_source_health_check_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.data.test_source_health_check
# [DOMAIN] D_DATA
# [CONSUMERS] CI pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/data/test_source_health_check.py -q
# [TTL] task_bound
"""test_source_health_check.py — 数据源健康检查模块单测。

验证 source_health_check 在 scheduler.start() 启动上下文的核心契约：
  1. _run_single_check 各状态分支正确（healthy/empty_data/connect_fail/test_fail/...）
  2. run_source_health_check 任何异常都不传播（不阻塞调度器启动）
  3. _write_log 失败不中断健康检查
  4. 时间戳用 now_utc()（aware UTC），回归保护防回退到 naive datetime.now()

测试隔离：用 sys.modules 注入 FakeProvider，零真实网络/外部依赖。
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import zephyr.data.source_health_check as shc

# ============ Fake providers（零外部依赖）============

class _OkProvider:
    """connect 成功的 provider。"""
    def connect(self) -> None:
        pass


class _ConnectFailProvider:
    """connect 抛异常的 provider。"""
    def connect(self) -> None:
        raise ConnectionError("connect boom")


class _NoConnectProvider:
    """无 connect 方法的 provider（getattr 返回 None → skip）。"""
    pass


def _install(monkeypatch, provider_cls, mod_name: str = "_fake_health_prov_mod") -> str:
    """把 FakeProvider 注入 sys.modules，供 __import__(cfg["module"]) 取回。

    Returns:
        mod_name（供 cfg["module"] 引用）。
    """
    mod = types.ModuleType(mod_name)
    mod.FakeProvider = provider_cls
    monkeypatch.setitem(sys.modules, mod_name, mod)
    return mod_name


def _cfg(
    source: str = "fake",
    test=None,
    env_required: list[str] | None = None,
    test_desc: str = "desc",
    mod_name: str = "_fake_health_prov_mod",
) -> dict:
    """构造 _run_single_check 的 cfg dict。"""
    return {
        "source": source,
        "module": mod_name,
        "class": "FakeProvider",
        "test": test,
        "test_desc": test_desc,
        "env_required": env_required or [],
    }


# ============ TestCheckEnv ============

class TestCheckEnv:
    def test_all_present(self, monkeypatch):
        monkeypatch.setenv("SHC_FOO", "1")
        ok, msg = shc._check_env(["SHC_FOO"])
        assert ok is True
        assert msg == "OK"

    def test_missing(self, monkeypatch):
        monkeypatch.delenv("SHC_NOPE", raising=False)
        ok, msg = shc._check_env(["SHC_NOPE"])
        assert ok is False
        assert "SHC_NOPE" in msg

    def test_partial_missing(self, monkeypatch):
        monkeypatch.setenv("SHC_A", "1")
        monkeypatch.delenv("SHC_B", raising=False)
        ok, msg = shc._check_env(["SHC_A", "SHC_B"])
        assert ok is False
        assert "SHC_B" in msg
        assert "SHC_A" not in msg


# ============ TestRunSingleCheck（核心分支）============

class TestRunSingleCheck:
    def test_env_missing(self, monkeypatch):
        monkeypatch.delenv("SHC_REQUIRED", raising=False)
        cfg = _cfg(env_required=["SHC_REQUIRED"])
        r = shc._run_single_check(cfg)
        assert r["status"] == "env_missing"
        assert r["connect_ok"] is False
        assert "SHC_REQUIRED" in r["error"]

    def test_import_fail(self, monkeypatch):
        monkeypatch.delitem(sys.modules, "_nonexistent_mod_xyz_shc", raising=False)
        cfg = _cfg(mod_name="_nonexistent_mod_xyz_shc")
        r = shc._run_single_check(cfg)
        assert r["status"] == "import_fail"
        assert r["connect_ok"] is False

    def test_connect_fail(self, monkeypatch):
        _install(monkeypatch, _ConnectFailProvider)
        cfg = _cfg()
        r = shc._run_single_check(cfg)
        assert r["status"] == "connect_fail"
        assert r["connect_ok"] is False
        assert "connect boom" in r["error"]

    def test_connect_only(self, monkeypatch):
        """test=None → 只测连接，status=connect_only。"""
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=None)
        r = shc._run_single_check(cfg)
        assert r["status"] == "connect_only"
        assert r["connect_ok"] is True
        assert r["test_ok"] is False

    def test_healthy_list(self, monkeypatch):
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: ["a", "b", "c"])
        r = shc._run_single_check(cfg)
        assert r["status"] == "healthy"
        assert r["test_ok"] is True
        assert r["data_count"] == 3

    def test_empty_data_list(self, monkeypatch):
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: [])
        r = shc._run_single_check(cfg)
        assert r["status"] == "empty_data"
        assert r["test_ok"] is False
        assert r["data_count"] == 0

    def test_test_fail(self, monkeypatch):
        _install(monkeypatch, _OkProvider)

        def _boom(p):
            raise RuntimeError("test boom")

        cfg = _cfg(test=_boom)
        r = shc._run_single_check(cfg)
        assert r["status"] == "test_fail"
        assert r["connect_ok"] is True
        assert r["test_ok"] is False
        assert "test boom" in r["error"]

    def test_healthy_dataframe(self, monkeypatch):
        pd = pytest.importorskip("pandas")
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: pd.DataFrame({"x": [1, 2, 3]}))
        r = shc._run_single_check(cfg)
        assert r["status"] == "healthy"
        assert r["data_count"] == 3

    def test_empty_dataframe(self, monkeypatch):
        pd = pytest.importorskip("pandas")
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: pd.DataFrame())
        r = shc._run_single_check(cfg)
        assert r["status"] == "empty_data"
        assert r["data_count"] == 0

    def test_no_connect_method_skips_connect(self, monkeypatch):
        """provider 无 connect 方法 → getattr 返回 None → skip，仍可进入 test。"""
        _install(monkeypatch, _NoConnectProvider)
        cfg = _cfg(test=lambda p: ["x"])
        r = shc._run_single_check(cfg)
        assert r["status"] == "healthy"
        assert r["connect_ok"] is True

    def test_none_return_treated_as_empty(self, monkeypatch):
        """test 返回 None → data_count=0 → empty_data。"""
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: None)
        r = shc._run_single_check(cfg)
        assert r["status"] == "empty_data"
        assert r["data_count"] == 0

    def test_scalar_return_count_one(self, monkeypatch):
        """test 返回无 __len__ 的标量 → data_count=1 → healthy。"""
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: 42)
        r = shc._run_single_check(cfg)
        assert r["status"] == "healthy"
        assert r["data_count"] == 1

    def test_timestamp_is_aware_utc(self, monkeypatch):
        """回归保护：timestamp 用 now_utc()，aware UTC（非 naive datetime.now()）。"""
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: ["x"])
        r = shc._run_single_check(cfg)
        ts = r["timestamp"]
        # now_utc().isoformat() 含时区后缀（+00:00 或 Z），naive datetime.now() 无
        assert "+" in ts or ts.endswith("Z"), f"timestamp 非 aware: {ts}"

    def test_connect_time_recorded(self, monkeypatch):
        _install(monkeypatch, _OkProvider)
        cfg = _cfg(test=lambda p: ["x"])
        r = shc._run_single_check(cfg)
        assert isinstance(r["connect_time"], float)
        assert r["connect_time"] >= 0.0


# ============ TestRunSourceHealthCheck（整体流程 + 容错契约）============

class TestRunSourceHealthCheck:
    def _stub_write_log(self, monkeypatch):
        """避免真实写 logs/ 目录 + 隔离 streak 状态文件/告警通道（#ARCH-DATA-015）。"""
        monkeypatch.setattr(shc, "_write_log", lambda results: Path("logs/dummy"))
        monkeypatch.setattr(shc, "_update_failure_streaks", lambda results: None)

    def test_returns_dict_keyed_by_source(self, monkeypatch):
        _install(monkeypatch, _OkProvider)
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [
            _cfg(source="s1", test=lambda p: ["x"]),
            _cfg(source="s2", test=None),
        ])
        self._stub_write_log(monkeypatch)
        result = shc.run_source_health_check()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"s1", "s2"}
        assert result["s1"]["status"] == "healthy"
        assert result["s2"]["status"] == "connect_only"

    def test_exception_in_single_check_caught(self, monkeypatch):
        """关键契约：单源检查抛异常 → unexpected_error，不中断整体（不阻塞 scheduler）。"""
        _install(monkeypatch, _OkProvider)
        original = shc._run_single_check

        def _flaky(cfg):
            if cfg["source"] == "s2":
                raise RuntimeError("unexpected boom")
            return original(cfg)

        monkeypatch.setattr(shc, "_run_single_check", _flaky)
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [
            _cfg(source="s1", test=lambda p: ["x"]),
            _cfg(source="s2", test=lambda p: ["x"]),
        ])
        self._stub_write_log(monkeypatch)
        result = shc.run_source_health_check()
        assert result["s1"]["status"] == "healthy"
        assert result["s2"]["status"] == "unexpected_error"
        assert "unexpected boom" in result["s2"]["error"]

    def test_all_connect_failures_do_not_raise(self, monkeypatch):
        """所有源连接失败时 run 仍正常返回（不抛异常，不阻塞 scheduler 启动）。"""
        _install(monkeypatch, _ConnectFailProvider)
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [
            _cfg(source="bad1"),
            _cfg(source="bad2"),
        ])
        self._stub_write_log(monkeypatch)
        result = shc.run_source_health_check()  # 不应抛异常
        assert result["bad1"]["status"] == "connect_fail"
        assert result["bad2"]["status"] == "connect_fail"

    def test_write_log_failure_does_not_break_run(self, monkeypatch):
        """日志写入失败不应中断健康检查（不阻塞 scheduler）。"""
        _install(monkeypatch, _OkProvider)
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [
            _cfg(source="s1", test=lambda p: ["x"]),
        ])

        def _bad_write(results):
            raise OSError("disk full")

        monkeypatch.setattr(shc, "_write_log", _bad_write)
        monkeypatch.setattr(shc, "_update_failure_streaks", lambda results: None)
        result = shc.run_source_health_check()  # 不应抛异常
        assert result["s1"]["status"] == "healthy"

    def test_updates_latest_results(self, monkeypatch):
        _install(monkeypatch, _OkProvider)
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [
            _cfg(source="only", test=lambda p: ["x"]),
        ])
        self._stub_write_log(monkeypatch)
        shc.run_source_health_check()
        cached = shc.get_source_health("only")
        assert cached is not None
        assert cached["status"] == "healthy"

    def test_empty_checks_returns_empty_dict(self, monkeypatch):
        monkeypatch.setattr(shc, "_HEALTH_CHECKS", [])
        self._stub_write_log(monkeypatch)
        result = shc.run_source_health_check()
        assert result == {}


# ============ TestGetSourceHealth ============

class TestGetSourceHealth:
    def test_unknown_source_returns_none(self, monkeypatch):
        monkeypatch.setattr(shc, "_latest_results", {})
        assert shc.get_source_health("nope") is None

    def test_known_source_returns_result(self, monkeypatch):
        monkeypatch.setattr(shc, "_latest_results", {"a": {"status": "healthy"}})
        assert shc.get_source_health("a") == {"status": "healthy"}

    def test_get_all_returns_new_container(self, monkeypatch):
        """get_all_source_health 返回新 dict（浅拷贝容器，非同一对象）。"""
        monkeypatch.setattr(shc, "_latest_results", {"a": {"status": "healthy"}})
        all_h = shc.get_all_source_health()
        assert all_h is not shc._latest_results
        assert all_h == {"a": {"status": "healthy"}}


# ============ TestWriteLog ============

class TestWriteLog:
    def test_writes_log_file_with_summary(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        results = [
            {"source": "ok", "status": "healthy", "connect_ok": True, "test_ok": True,
             "connect_time": 0.1, "test_time": 0.2, "error": "", "data_count": 5, "test_desc": "d"},
            {"source": "bad", "status": "connect_fail", "connect_ok": False, "test_ok": False,
             "connect_time": 0.0, "test_time": 0.0, "error": "boom", "data_count": 0, "test_desc": "d"},
        ]
        path = shc._write_log(results)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "ok" in content
        assert "bad" in content
        assert "boom" in content
        assert "汇总" in content

    def test_log_filename_uses_utc_date(self, tmp_path, monkeypatch):
        """回归保护：日志文件名用 now_utc() 日期。"""
        monkeypatch.chdir(tmp_path)
        path = shc._write_log([])
        # 文件名形如 source_health_YYYYMMDD.log
        name = path.name
        assert name.startswith("source_health_")
        assert name.endswith(".log")
        date_part = name[len("source_health_"):-len(".log")]
        assert len(date_part) == 8 and date_part.isdigit()


# ============ TestFailureStreaks（#ARCH-DATA-015 同源连续失败告警）============

class _FakeAlerter:
    """记录 notify 调用的假告警器。"""

    def __init__(self):
        self.calls = []

    def notify(self, task_id, error, level=None, source=None, extra=None):
        self.calls.append({"task_id": task_id, "error": error, "level": level, "source": source})
        return True


class TestFailureStreaks:
    """连续异常按自然日累计，>=3 天告警一次，恢复自动消警。"""

    def _run(self, monkeypatch, tmp_path, results, today: str, alerter):
        import datetime as dt
        monkeypatch.setattr(shc, "_STREAKS_PATH", tmp_path / "streaks.json")
        monkeypatch.setattr(
            shc, "now_utc",
            lambda: dt.datetime.fromisoformat(today).replace(tzinfo=dt.timezone.utc),
        )
        monkeypatch.setattr("zephyr.data.alerter.Alerter", lambda: alerter)
        shc._update_failure_streaks(results)

    @staticmethod
    def _bad(source="bs", status="connect_fail"):
        return {"source": source, "status": status, "error": "10001011 黑名单用户"}

    @staticmethod
    def _ok(source="bs"):
        return {"source": source, "status": "healthy", "error": ""}

    def test_alert_on_third_consecutive_day(self, monkeypatch, tmp_path):
        alerter = _FakeAlerter()
        self._run(monkeypatch, tmp_path, [self._bad()], "2026-08-14", alerter)
        self._run(monkeypatch, tmp_path, [self._bad()], "2026-08-15", alerter)
        assert not alerter.calls  # 连续 2 天不达阈值
        self._run(monkeypatch, tmp_path, [self._bad()], "2026-08-16", alerter)
        assert len(alerter.calls) == 1
        assert alerter.calls[0]["level"] == "ERROR"
        assert "连续 3 天" in alerter.calls[0]["error"]
        assert "10001011" in alerter.calls[0]["error"]

    def test_no_duplicate_alert_same_episode(self, monkeypatch, tmp_path):
        alerter = _FakeAlerter()
        for day in ("2026-08-14", "2026-08-15", "2026-08-16", "2026-08-17"):
            self._run(monkeypatch, tmp_path, [self._bad()], day, alerter)
        assert len(alerter.calls) == 1  # 第 4 天不重复告警

    def test_same_day_rerun_not_double_counted(self, monkeypatch, tmp_path):
        alerter = _FakeAlerter()
        for _ in range(3):
            self._run(monkeypatch, tmp_path, [self._bad()], "2026-08-14", alerter)
        assert not alerter.calls  # 同一天重跑不累计

    def test_recovery_sends_resolve_and_resets(self, monkeypatch, tmp_path):
        alerter = _FakeAlerter()
        for day in ("2026-08-14", "2026-08-15", "2026-08-16"):
            self._run(monkeypatch, tmp_path, [self._bad()], day, alerter)
        assert len(alerter.calls) == 1
        self._run(monkeypatch, tmp_path, [self._ok()], "2026-08-17", alerter)
        assert len(alerter.calls) == 2
        assert alerter.calls[1]["level"] == "INFO"
        assert "恢复正常" in alerter.calls[1]["error"]
        # 恢复后再异常 → streak 重新从 1 计
        self._run(monkeypatch, tmp_path, [self._bad()], "2026-08-18", alerter)
        assert len(alerter.calls) == 2
