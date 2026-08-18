# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] tests.experiment_tracking.test_experiment_tracker
# [DOMAIN] D_INFRA_TELEMETRY
# [A_module] module_id=MOD-TEST-OBS-TRACKER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""ExperimentTracker 单元测试——两 backend（Fallback/Null）选择 / RunContext 语义 / 单例 / 配置。

覆盖:
  - ExperimentTrackingConfig 不可变 + load_config 环境变量覆盖
  - _NullBackend（enable_tracking=False）no-op 行为
  - FallbackBackend JSON 写入（start_run/log_*/end_run 全链路）
  - ExperimentTracker backend 自动选择（单一 JSON 后端，MLflow 已退役）
  - RunContext 正常退出 FINISHED / 异常退出 FAILED 不吞异常
  - RunContext log_* 失败只 stderr 不抛
  - get_tracker 单例 + reset_tracker 重置
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.experiment_tracker import (
    ExperimentTracker,
    FallbackBackend,
    RunContext,
    _NullBackend,
    get_tracker,
    reset_tracker,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    """每个测试前重置 tracker 单例 + 降级 warning 标志。"""
    reset_tracker()
    yield
    reset_tracker()


# ── ExperimentTrackingConfig ──────────────────────────────────────


class TestExperimentTrackingConfig:
    """配置不可变 + 环境变量覆盖。"""

    def test_frozen_dataclass(self):
        """ExperimentTrackingConfig 不可变——赋值抛 FrozenInstanceError。"""
        cfg = ExperimentTrackingConfig()
        with pytest.raises(Exception):
            cfg.enable_tracking = False  # type: ignore[misc]

    def test_defaults(self):
        """默认值：enable_tracking=True + fallback_dir 默认路径。"""
        cfg = ExperimentTrackingConfig()
        assert cfg.enable_tracking is True
        assert "experiment_tracking_fallback" in str(cfg.fallback_dir)

    def test_load_config_env_disable(self, monkeypatch):
        """ZEPHYR_EXPERIMENT_TRACKING=0 → enable_tracking=False。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        cfg = load_config()
        assert cfg.enable_tracking is False

    def test_load_config_env_enable(self, monkeypatch):
        """ZEPHYR_EXPERIMENT_TRACKING=1 → enable_tracking=True。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        cfg = load_config()
        assert cfg.enable_tracking is True


# ── _NullBackend ─────────────────────────────────────────────────


class TestNullBackend:
    """enable_tracking=False 时的 no-op backend。"""

    def test_start_run_returns_null_run(self):
        """start_run 返回 'null-run'，不创建任何文件。"""
        backend = _NullBackend()
        run_id = backend.start_run("test-component", None, {"k": "v"})
        assert run_id == "null-run"

    def test_log_methods_noop(self):
        """所有 log_* 方法不抛、不写文件。"""
        backend = _NullBackend()
        backend.start_run("c", None, None)
        backend.log_params({"a": 1})
        backend.log_metrics({"m": 0.5}, step=0)
        backend.log_artifact("/nonexistent/file.txt", None)
        backend.log_artifact_bytes(b"data", "f.txt", None)
        backend.end_run("FINISHED")
        # 无异常即通过


# ── FallbackBackend ───────────────────────────────────────────────


class TestFallbackBackend:
    """JSON 降级 backend——写 run_meta.json。"""

    def test_start_run_creates_dir(self, tmp_path):
        """start_run 创建 {fallback_dir}/{component}/{run_id}/ 目录。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c1-validation", "test_run", {"mode": "mock"})
        run_dir = tmp_path / "c1-validation" / run_id
        assert run_dir.exists()
        assert run_dir.is_dir()

    def test_log_params_metrics_stored_in_memory(self, tmp_path):
        """log_params/log_metrics 写入内部 dict（end_run 后 del _current）。"""
        backend = FallbackBackend(tmp_path)
        backend.start_run("c1", None, None)
        backend.log_params({"strategy": "momentum", "window": 20})
        backend.log_metrics({"sharpe": 1.5, "maxdd": -0.1}, step=None)
        assert backend._current["params"]["strategy"] == "momentum"
        assert backend._current["metrics"]["sharpe"] == 1.5
        backend.end_run("FINISHED")
        # end_run 后 _current 被 del
        assert not hasattr(backend, "_current")

    def test_end_run_writes_json(self, tmp_path):
        """end_run 写 run_meta.json，含 params/metrics/tags/status。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c1", "run1", {"mode": "mock"})
        backend.log_params({"p1": "v1"})
        backend.log_metrics({"m1": 0.42}, step=None)
        backend.log_artifact_bytes(b"csv,data\n1,2", "nav.csv", artifact_path="nav")
        backend.end_run("FINISHED")

        meta_path = tmp_path / "c1" / run_id / "run_meta.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta["status"] == "FINISHED"
        assert meta["params"]["p1"] == "v1"
        assert meta["metrics"]["m1"] == 0.42
        assert meta["tags"]["mode"] == "mock"
        assert meta["end_time"] is not None
        assert any(a.get("filename") == "nav.csv" for a in meta["artifacts"])

    def test_artifact_bytes_written_to_disk(self, tmp_path):
        """log_artifact_bytes 把 bytes 写为文件（artifact_path 子目录下）。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c", None, None)
        backend.log_artifact_bytes(b"hello world", "report.md", artifact_path="report")
        # artifact_path="report" → 写到 {fallback_dir}/c/{run_id}/report/report.md
        f = tmp_path / "c" / run_id / "report" / "report.md"
        assert f.exists()
        assert f.read_bytes() == b"hello world"
        backend.end_run("FINISHED")

    def test_log_artifact_records_path(self, tmp_path):
        """log_artifact 记录本地路径到 artifacts 列表（不复制文件）。"""
        src = tmp_path / "source.txt"
        src.write_text("source content", encoding="utf-8")

        backend = FallbackBackend(tmp_path / "fb")
        backend.start_run("c", None, None)
        backend.log_artifact(str(src), artifact_path="data")
        # log_artifact 只记录路径，不复制
        assert any(
            a.get("local_path") == str(src) and a.get("artifact_path") == "data"
            for a in backend._current["artifacts"]
        )
        backend.end_run("FINISHED")


# ── ExperimentTracker backend 选择 ────────────────────────────────


class TestExperimentTrackerBackendSelection:
    """ExperimentTracker 自动选择两 backend（Fallback/Null）。"""

    def test_disabled_tracking_uses_null_backend(self, monkeypatch):
        """enable_tracking=False → _NullBackend。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        tracker = ExperimentTracker()
        assert isinstance(tracker._backend, _NullBackend)
        assert tracker.available is False

    def test_enabled_uses_fallback(self, monkeypatch, tmp_path):
        """enable_tracking=True → FallbackBackend（单一 JSON 后端，恒为真）。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        # 用自定义 fallback_dir 避免污染 logs/
        cfg = ExperimentTrackingConfig(
            enable_tracking=True,
            fallback_dir=tmp_path / "fallback",
        )
        tracker = ExperimentTracker(config=cfg)
        assert isinstance(tracker._backend, FallbackBackend)
        assert tracker.available is True

    def test_start_run_returns_run_context(self, monkeypatch, tmp_path):
        """start_run 返回 RunContext 实例。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=tmp_path / "fb")
        tracker = ExperimentTracker(config=cfg)
        with tracker.start_run("test-comp", run_name="rn", tags={"t": "1"}) as run:
            assert isinstance(run, RunContext)
            assert run.run_id  # 非空
            assert run._component == "test-comp"


# ── RunContext 语义 ───────────────────────────────────────────────


class TestRunContext:
    """RunContext 上下文管理器语义。"""

    def test_normal_exit_finished(self, tmp_path):
        """正常退出 → end_run("FINISHED")。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c", "rn", None)
        ctx = RunContext(backend, run_id, "c", "rn")
        with ctx:
            pass
        meta = json.loads((tmp_path / "c" / run_id / "run_meta.json").read_text("utf-8"))
        assert meta["status"] == "FINISHED"

    def test_exception_exit_failed(self, tmp_path):
        """异常退出 → end_run("FAILED")，且异常正常传播（不吞）。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c", "rn", None)
        ctx = RunContext(backend, run_id, "c", "rn")
        with pytest.raises(ValueError, match="boom"):
            with ctx:
                raise ValueError("boom")
        meta = json.loads((tmp_path / "c" / run_id / "run_meta.json").read_text("utf-8"))
        assert meta["status"] == "FAILED"

    def test_log_failure_does_not_raise(self, tmp_path):
        """log_* 内部 backend 抛异常时，RunContext 兜住不抛。"""
        class _BadBackend:
            def log_params(self, params):
                raise RuntimeError("backend broken")
            def log_metrics(self, metrics, step):
                raise RuntimeError("backend broken")
            def log_artifact(self, local_path, artifact_path):
                raise RuntimeError("backend broken")
            def log_artifact_bytes(self, data, filename, artifact_path):
                raise RuntimeError("backend broken")
            def end_run(self, status):
                pass

        ctx = RunContext(_BadBackend(), "fake-id", "c", "rn")
        with ctx:
            ctx.log_params({"a": 1})       # 不抛
            ctx.log_metrics({"m": 1.0})    # 不抛
            ctx.log_artifact("/x", None)   # 不抛
            ctx.log_artifact_bytes(b"x", "f", None)  # 不抛

    def test_log_methods_delegate_to_backend(self, tmp_path):
        """log_params/log_metrics/log_artifact_bytes 正常委托 backend。"""
        backend = FallbackBackend(tmp_path)
        run_id = backend.start_run("c", "rn", None)
        ctx = RunContext(backend, run_id, "c", "rn")
        with ctx:
            ctx.log_params({"strategy": "test"})
            ctx.log_metrics({"sharpe": 1.2})
            ctx.log_artifact_bytes(b"data", "nav.csv", artifact_path="nav")
        meta = json.loads((tmp_path / "c" / run_id / "run_meta.json").read_text("utf-8"))
        assert meta["params"]["strategy"] == "test"
        assert meta["metrics"]["sharpe"] == 1.2
        assert any(a.get("filename") == "nav.csv" for a in meta["artifacts"])


# ── get_tracker / reset_tracker 单例 ─────────────────────────────


class TestSingletonFactory:
    """get_tracker 单例 + reset_tracker 重置。"""

    def test_get_tracker_returns_singleton(self, monkeypatch, tmp_path):
        """get_tracker 两次返回同一实例。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        # 注入 fallback_dir 避免污染——通过 patch load_config
        import zephyr.experiment_tracking.experiment_tracker as et
        original_load = et.load_config
        monkeypatch.setattr(
            et, "load_config",
            lambda: ExperimentTrackingConfig(enable_tracking=True, fallback_dir=tmp_path / "fb")
        )
        t1 = get_tracker()
        t2 = get_tracker()
        assert t1 is t2

    def test_reset_tracker_clears_singleton(self, monkeypatch, tmp_path):
        """reset_tracker 后 get_tracker 返回新实例。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        import zephyr.experiment_tracking.experiment_tracker as et
        monkeypatch.setattr(
            et, "load_config",
            lambda: ExperimentTrackingConfig(enable_tracking=True, fallback_dir=tmp_path / "fb")
        )
        t1 = get_tracker()
        reset_tracker()
        t2 = get_tracker()
        assert t1 is not t2
