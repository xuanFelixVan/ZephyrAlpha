# [BLUEPRINT] MOD-ML-020 | docs/03_modules/_domain_machine_learning_train/reproducibility_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-020 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_reproducibility_manager
# [TESTS] src/zephyr/ml_train/reproducibility_manager.py
"""MOD-ML-020 单元测试：reproducibility_manager 可复现性管理器。

蓝图验收（B13-04338/CAND-MLT-028，A3 D-RESEARCH-05）：
环境快照（采集注入）+ 全局种子登记 + 结果 hash 校验重跑比对 +
复现报告差异清单 + experiment_tracking 注入回调。
采集器/tracking/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.reproducibility_manager",
    reason="reproducibility_manager not importable",
)

from zephyr.ml_train.reproducibility_manager import (  # noqa: E402
    ReproducibilityError,
    ReproducibilityManager,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_ENV = {"python": "3.12.4", "packages": {"numpy": "2.1.0", "pandas": "2.2.2"}}
_RESULT = {"sharpe": 1.83, "crps": 0.041}


def _mgr(**kw) -> ReproducibilityManager:
    kw.setdefault("env_collector", lambda: dict(_ENV))
    kw.setdefault("clock", lambda: _T0)
    return ReproducibilityManager(**kw)


def _registered(mgr: ReproducibilityManager, run_id: str = "run-1") -> str:
    mgr.capture_environment()
    mgr.register_run(run_id, seed=42)
    return mgr.record_result(run_id, _RESULT)


# ──────────────────────────────────────────────────────────────────────────────
# 环境快照（采集注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestCaptureEnvironment:
    def test_capture_ok_sorted_packages(self) -> None:
        mgr = _mgr()
        snap = mgr.capture_environment()
        assert snap.snapshot_id == "env-0001"  # 确定性序号
        assert snap.python_version == "3.12.4"
        assert snap.packages == (("numpy", "2.1.0"), ("pandas", "2.2.2"))  # 排序元组
        assert mgr.environment("env-0001") == snap

    def test_collector_not_injected_fail_closed(self) -> None:
        mgr = ReproducibilityManager(clock=lambda: _T0)
        with pytest.raises(ReproducibilityError):
            mgr.capture_environment()

    def test_invalid_payload_raise(self) -> None:
        with pytest.raises(ReproducibilityError):
            _mgr(env_collector=lambda: {"packages": {}}).capture_environment()  # 缺 python
        with pytest.raises(ReproducibilityError):
            _mgr(env_collector=lambda: {"python": "", "packages": {}}).capture_environment()
        with pytest.raises(ReproducibilityError):
            _mgr(env_collector=lambda: {"python": "3.12", "packages": ["numpy"]}).capture_environment()
        with pytest.raises(ReproducibilityError):
            _mgr(env_collector=lambda: {"python": "3.12", "packages": {"": "1.0"}}).capture_environment()
        with pytest.raises(ReproducibilityError):
            _mgr(env_collector=lambda: {"python": "3.12", "packages": {"numpy": ""}}).capture_environment()

    def test_environment_unknown_raise(self) -> None:
        with pytest.raises(ReproducibilityError):
            _mgr().environment("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 全局种子登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterRun:
    def test_register_defaults_latest_env(self) -> None:
        mgr = _mgr()
        mgr.capture_environment()
        rec = mgr.register_run("run-1", seed=42)
        assert rec.seed == 42
        assert rec.env_snapshot_id == "env-0001"
        assert rec.result_hash is None

    def test_register_invalid_raise(self) -> None:
        mgr = _mgr()
        mgr.capture_environment()
        with pytest.raises(ReproducibilityError):
            mgr.register_run("", seed=1)
        with pytest.raises(ReproducibilityError):
            mgr.register_run("run-1", seed=-1)
        with pytest.raises(ReproducibilityError):
            mgr.register_run("run-1", seed=True)  # bool 非合法种子
        with pytest.raises(ReproducibilityError):
            mgr.register_run("run-1", seed=1, env_snapshot_id="ghost")
        mgr.register_run("run-1", seed=1)
        with pytest.raises(ReproducibilityError):
            mgr.register_run("run-1", seed=2)  # 重复登记

    def test_register_without_env_raise(self) -> None:
        with pytest.raises(ReproducibilityError):
            _mgr().register_run("run-1", seed=1)


# ──────────────────────────────────────────────────────────────────────────────
# 结果 hash 记录
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordResult:
    def test_record_ok_deterministic(self) -> None:
        h1 = _registered(_mgr())
        h2 = _registered(_mgr())
        assert h1 == h2  # 同结果必同 hash
        assert h1

    def test_record_invalid_raise(self) -> None:
        mgr = _mgr()
        mgr.capture_environment()
        with pytest.raises(ReproducibilityError):
            mgr.record_result("ghost", _RESULT)  # 未知运行
        mgr.register_run("run-1", seed=1)
        with pytest.raises(ReproducibilityError):
            mgr.record_result("run-1", {})  # 空结果
        mgr.record_result("run-1", _RESULT)
        with pytest.raises(ReproducibilityError):
            mgr.record_result("run-1", _RESULT)  # 写后不可改


# ──────────────────────────────────────────────────────────────────────────────
# 重跑比对 + 复现报告
# ──────────────────────────────────────────────────────────────────────────────


class TestVerifyRerun:
    def test_match(self) -> None:
        mgr = _mgr()
        _registered(mgr)
        report = mgr.verify_rerun("run-1", "run-1b", dict(_RESULT), rerun_seed=42)
        assert report.matched is True
        assert report.seed_matched is True
        assert report.diffs == ()

    def test_value_diff(self) -> None:
        mgr = _mgr()
        _registered(mgr)
        report = mgr.verify_rerun("run-1", "run-1b", {**_RESULT, "sharpe": 1.5})
        assert report.matched is False
        assert [(d.field, d.expected, d.actual) for d in report.diffs] == [("sharpe", 1.83, 1.5)]

    def test_missing_and_extra_key_diffs_sorted(self) -> None:
        mgr = _mgr()
        _registered(mgr)
        report = mgr.verify_rerun("run-1", "run-1b", {"sharpe": 1.83, "extra": 1})
        assert [d.field for d in report.diffs] == ["crps", "extra"]  # 确定性排序
        assert report.diffs[0].actual == "<MISSING>"
        assert report.diffs[1].expected == "<MISSING>"

    def test_seed_mismatch(self) -> None:
        mgr = _mgr()
        _registered(mgr)
        report = mgr.verify_rerun("run-1", "run-1b", dict(_RESULT), rerun_seed=7)
        assert report.seed_matched is False
        assert report.matched is False  # 种子不一致整体不复现

    def test_verify_invalid_raise(self) -> None:
        mgr = _mgr()
        with pytest.raises(ReproducibilityError):
            mgr.verify_rerun("ghost", "x", dict(_RESULT))  # 未知运行
        mgr.capture_environment()
        mgr.register_run("run-1", seed=1)
        with pytest.raises(ReproducibilityError):
            mgr.verify_rerun("run-1", "x", dict(_RESULT))  # 未记录结果 hash
        mgr.record_result("run-1", _RESULT)
        with pytest.raises(ReproducibilityError):
            mgr.verify_rerun("run-1", "", dict(_RESULT))  # 空 rerun_id
        with pytest.raises(ReproducibilityError):
            mgr.verify_rerun("run-1", "x", {})  # 空重跑结果
        with pytest.raises(ReproducibilityError):
            mgr.verify_rerun("run-1", "x", dict(_RESULT), rerun_seed=-1)

    def test_tracking_sink_and_reports(self) -> None:
        events: list[dict] = []
        mgr = _mgr(tracking_sink=lambda e: events.append(dict(e)))
        _registered(mgr)
        mgr.verify_rerun("run-1", "run-1b", dict(_RESULT))
        assert events == [
            {
                "event": "repro_verify",
                "run_id": "run-1",
                "rerun_id": "run-1b",
                "matched": True,
                "diff_count": 0,
            }
        ]
        assert len(mgr.reports()) == 1
        assert mgr.list_runs() == ("run-1",)

    def test_tracking_sink_exception_not_blocking(self) -> None:
        def _boom(_e) -> None:
            raise RuntimeError("tracking 故障")

        mgr = _mgr(tracking_sink=_boom)
        _registered(mgr)
        assert mgr.verify_rerun("run-1", "run-1b", dict(_RESULT)).matched is True
