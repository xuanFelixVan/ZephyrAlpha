# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M1-3
# [MODULE] tests.experiment_tracking.test_c1_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [A_module] module_id=MOD-TEST-OBS-C1ADAPT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""C1 Adapter 单元测试——track_c1_result 完整流程 / params/metrics/artifacts 提取。

覆盖:
  - track_c1_result 完整流程（FallbackBackend）：产出 run_id + run_meta.json
  - _extract_params：门槛配置 + 模式 + 策略 + 日期范围 + trades_count
  - _extract_metrics：baseline_/experiment_ 核心指标 + per-verdict 值 + passed
  - _build_summary_md：含 verdicts 表 + passed + summary
  - _log_nav_artifacts：comparator=None 跳过；有 portfolio 写 CSV
  - tracker 关闭（NullBackend）：run_id="null-run"，不抛
  - extra_tags 传入 tags
  - veto_reason 写入 tags

用 SimpleNamespace 构造 C1ComparisonResult / C1ShrinkageComparator 鸭子类型
（c1_adapter 运行时全鸭子类型，TYPE_CHECKING 隔离——无需 import backtest）。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.experiment_tracking.adapters.c1_adapter import (
    _build_summary_md,
    _extract_metrics,
    _extract_params,
    _log_nav_artifacts,
    _render_nav_png,
    track_c1_result,
)
from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.experiment_tracking.experiment_tracker import (
    ExperimentTracker,
    get_tracker,
    reset_tracker,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    reset_tracker()
    yield
    reset_tracker()


@pytest.fixture(autouse=True)
def _force_fallback_backend():
    """强制 FallbackBackend：本模块用例断言 run_meta.json，需走 JSON 路径。
    MLflow 退役后 enable_tracking=True 恒走 FallbackBackend——本 fixture 为 no-op 保留（历史语义）。"""


# ── 合成 C1ComparisonResult 鸭子类型 ─────────────────────────────


def _make_backtest_result(
    *,
    sharpe=1.3,
    maxdd=-0.12,
    annual_return=0.25,
    total_return=0.30,
    win_rate=0.55,
    trades_count=42,
    strategy_id="topn-momentum",
    start_date=None,
    end_date=None,
) -> SimpleNamespace:
    """构造 BacktestResult 鸭子类型（c1_adapter 只读属性）。"""
    return SimpleNamespace(
        sharpe_ratio=sharpe,
        max_drawdown=maxdd,
        annual_return=annual_return,
        total_return=total_return,
        win_rate=win_rate,
        trades_count=trades_count,
        strategy_id=strategy_id,
        start_date=start_date or datetime(2024, 1, 1),
        end_date=end_date or datetime(2024, 6, 30),
    )


def _make_verdict(
    name="Sharpe",
    baseline=1.3,
    experiment=1.25,
    passed=True,
    detail="S_开 ≥ S_关 − 0.1",
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        baseline_value=baseline,
        experiment_value=experiment,
        passed=passed,
        detail=detail,
    )


def _make_c1_result(
    *,
    passed=False,
    veto_reason="MaxDD 未改善",
    summary="C1 对比：MaxDD 改善不足 3pp，一票否决。",
    metric_verdicts=None,
    baseline_result=None,
    experiment_result=None,
    baseline_turnover=1.7,
    experiment_turnover=1.5,
    baseline_calmar=1.04,
    experiment_calmar=1.20,
) -> SimpleNamespace:
    return SimpleNamespace(
        passed=passed,
        veto_reason=veto_reason,
        summary=summary,
        metric_verdicts=metric_verdicts
        or [
            _make_verdict("Sharpe", 1.3, 1.25, True),
            _make_verdict("MaxDD", -0.12, -0.11, False, "DD_开 − DD_关 < 3pp"),
            _make_verdict("Calmar", 1.04, 1.20, True),
            _make_verdict("Turnover", 1.7, 1.5, True),
        ],
        baseline_result=baseline_result or _make_backtest_result(),
        experiment_result=experiment_result or _make_backtest_result(sharpe=1.25, maxdd=-0.11, trades_count=38),
        baseline_turnover=baseline_turnover,
        experiment_turnover=experiment_turnover,
        baseline_calmar=baseline_calmar,
        experiment_calmar=experiment_calmar,
    )


def _make_comparator(
    *,
    with_portfolios=False,
    nav_len=100,
) -> SimpleNamespace:
    """构造 C1ShrinkageComparator 鸭子类型。"""
    cfg = SimpleNamespace(
        sharpe_tolerance=0.1,
        maxdd_improvement_pp=0.03,
        calmar_improvement_ratio=1.2,
        turnover_max_ratio=2.0,
        trading_days_per_year=252,
    )
    comp = SimpleNamespace(config=cfg, last_baseline_portfolio=None, last_experiment_portfolio=None)
    if with_portfolios:
        import pandas as pd

        nav = pd.Series([1.0 + i * 0.001 for i in range(nav_len)], name="nav")
        comp.last_baseline_portfolio = SimpleNamespace(nav_series=nav)
        comp.last_experiment_portfolio = SimpleNamespace(nav_series=nav * 0.98)
    return comp


# ── _extract_params ──────────────────────────────────────────────


class TestExtractParams:
    """params 提取：门槛 + 模式 + 策略 + 日期 + trades_count。"""

    def test_basic_params(self):
        """基本 params 含 mode/strategy_name/passed/strategy_id/日期/trades_count。"""
        result = _make_c1_result()
        comp = _make_comparator()
        params = _extract_params(result, comp, mode="mock", strategy_name="c1-mock")
        assert params["mode"] == "mock"
        assert params["strategy_name"] == "c1-mock"
        assert params["passed"] is False
        assert params["strategy_id"] == "topn-momentum"
        assert params["start_date"] == "2024-01-01T00:00:00"
        assert params["end_date"] == "2024-06-30T00:00:00"
        assert params["baseline_trades_count"] == 42
        assert params["experiment_trades_count"] == 38

    def test_c1_threshold_params(self):
        """comparator 持有 C1Config → 门槛参数写入。"""
        result = _make_c1_result()
        comp = _make_comparator()
        params = _extract_params(result, comp, mode="regime", strategy_name="s1")
        assert params["c1_sharpe_tolerance"] == 0.1
        assert params["c1_maxdd_improvement_pp"] == 0.03
        assert params["c1_calmar_improvement_ratio"] == 1.2
        assert params["c1_turnover_max_ratio"] == 2.0
        assert params["c1_trading_days_per_year"] == 252

    def test_comparator_none_skips_thresholds(self):
        """comparator=None → 不含 c1_ 门槛参数。"""
        result = _make_c1_result()
        params = _extract_params(result, None, mode="mock", strategy_name="s")
        assert "c1_sharpe_tolerance" not in params
        assert params["mode"] == "mock"


# ── _extract_metrics ─────────────────────────────────────────────


class TestExtractMetrics:
    """metrics 提取：baseline_/experiment_ 指标 + per-verdict + passed。"""

    def test_core_metrics(self):
        """baseline_/experiment_ 核心指标全写入。"""
        result = _make_c1_result()
        metrics = _extract_metrics(result)
        for key in [
            "baseline_sharpe",
            "experiment_sharpe",
            "baseline_maxdd",
            "experiment_maxdd",
            "baseline_annual_return",
            "experiment_annual_return",
            "baseline_turnover",
            "experiment_turnover",
            "baseline_calmar",
            "experiment_calmar",
        ]:
            assert key in metrics
        assert metrics["baseline_sharpe"] == pytest.approx(1.3)
        assert metrics["experiment_sharpe"] == pytest.approx(1.25)

    def test_passed_metric(self):
        """passed → 1.0/0.0。"""
        result_pass = _make_c1_result(passed=True, veto_reason=None)
        assert _extract_metrics(result_pass)["passed"] == 1.0
        result_fail = _make_c1_result(passed=False)
        assert _extract_metrics(result_fail)["passed"] == 0.0

    def test_per_verdict_metrics(self):
        """每个 verdict 产出 {name}_baseline/{name}_experiment/{name}_passed。"""
        result = _make_c1_result()
        metrics = _extract_metrics(result)
        # Sharpe verdict
        assert "sharpe_baseline" in metrics
        assert "sharpe_experiment" in metrics
        assert "sharpe_passed" in metrics
        assert metrics["sharpe_passed"] == 1.0  # Sharpe passed=True
        # MaxDD verdict (passed=False)
        assert "maxdd_passed" in metrics
        assert metrics["maxdd_passed"] == 0.0
        # 4 verdicts × 3 = 12 per-verdict metrics
        verdict_keys = [k for k in metrics if k.endswith(("_baseline", "_experiment", "_passed")) and k != "passed"]
        assert len(verdict_keys) == 12


# ── _build_summary_md ────────────────────────────────────────────


class TestBuildSummaryMd:
    """c1_summary.md 构建：含 verdicts 表 + passed + summary。"""

    def test_contains_key_sections(self):
        """summary md 含 passed / veto_reason / 指标裁定表 / 总结。"""
        result = _make_c1_result()
        md = _build_summary_md(result)
        assert "C1 Shrinkage 开/关对比结果" in md
        assert "**passed**: False" in md
        assert "MaxDD 未改善" in md
        assert "## 指标裁定" in md
        assert "Sharpe" in md
        assert "MaxDD" in md
        assert "## 总结" in md
        assert "C1 对比：MaxDD 改善不足 3pp" in md

    def test_no_veto_reason(self):
        """passed=True veto_reason=None → 显示 '(无——四项全过)'。"""
        result = _make_c1_result(passed=True, veto_reason=None)
        md = _build_summary_md(result)
        assert "(无——四项全过)" in md


# ── _log_nav_artifacts ───────────────────────────────────────────


class TestLogNavArtifacts:
    """净值曲线 artifact：comparator=None 跳过；有 portfolio 写 CSV。"""

    def test_comparator_none_skips(self):
        """comparator=None → 不抛、不写。"""

        class _Spy:
            def __init__(self):
                self.calls = []

            def log_artifact_bytes(self, data, filename, artifact_path):
                self.calls.append((filename, artifact_path))

        spy = _Spy()
        _log_nav_artifacts(spy, None)
        assert len(spy.calls) == 0

    def test_with_portfolios_writes_csv(self):
        """comparator 有 portfolio → 写 nav_curve_baseline.csv + nav_curve_experiment.csv。"""

        class _Spy:
            def __init__(self):
                self.calls = []

            def log_artifact_bytes(self, data, filename, artifact_path):
                self.calls.append((filename, artifact_path, data))

        spy = _Spy()
        comp = _make_comparator(with_portfolios=True, nav_len=50)
        _log_nav_artifacts(spy, comp)
        filenames = [c[0] for c in spy.calls]
        assert "nav_curve_baseline.csv" in filenames
        assert "nav_curve_experiment.csv" in filenames
        # CSV 内容含 header
        baseline_csv = next(c[2] for c in spy.calls if c[0] == "nav_curve_baseline.csv")
        assert b"nav" in baseline_csv

    def test_with_portfolios_writes_png(self):
        """comparator 有 portfolio → 写 nav_curve_comparison.png（matplotlib 装了时）。"""

        class _Spy:
            def __init__(self):
                self.calls = []

            def log_artifact_bytes(self, data, filename, artifact_path):
                self.calls.append((filename, artifact_path, data))

        spy = _Spy()
        comp = _make_comparator(with_portfolios=True, nav_len=50)
        _log_nav_artifacts(spy, comp)
        filenames = [c[0] for c in spy.calls]
        # PNG 只在 matplotlib 可用时生成——检查是否在列表中
        if "nav_curve_comparison.png" in filenames:
            png_bytes = next(c[2] for c in spy.calls if c[0] == "nav_curve_comparison.png")
            # PNG 文件头 magic bytes: \x89PNG
            assert png_bytes[:4] == b"\x89PNG"
            assert len(png_bytes) > 100  # 不是空图

    def test_portfolio_none_skips(self):
        """portfolio=None → 跳过该侧。"""

        class _Spy:
            def __init__(self):
                self.calls = []

            def log_artifact_bytes(self, data, filename, artifact_path):
                self.calls.append(filename)

        spy = _Spy()
        comp = _make_comparator(with_portfolios=False)
        _log_nav_artifacts(spy, comp)
        assert len(spy.calls) == 0


# ── track_c1_result 端到端 ───────────────────────────────────────


class TestTrackC1Result:
    """track_c1_result 完整流程（FallbackBackend 降级模式）。"""

    @pytest.fixture(autouse=True)
    def _force_fallback(self):
        """强制 FallbackBackend：MLflow 退役后 enable_tracking=True 恒走 FallbackBackend——no-op 保留（历史语义）。"""

    def test_returns_run_id(self, monkeypatch, tmp_path):
        """track_c1_result 返回非空 run_id。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=tmp_path / "fb")
        tracker = ExperimentTracker(config=cfg)
        import zephyr.experiment_tracking.experiment_tracker as et

        monkeypatch.setattr(et, "_tracker_singleton", tracker)

        result = _make_c1_result()
        comp = _make_comparator()
        run_id = track_c1_result(result, comparator=comp, mode="mock", strategy_name="c1-mock")
        assert run_id
        assert isinstance(run_id, str)

    def test_writes_run_meta_json(self, monkeypatch, tmp_path):
        """FallbackBackend 模式下，run_meta.json 落盘且含完整数据。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        fb_dir = tmp_path / "fb"
        cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=fb_dir)
        tracker = ExperimentTracker(config=cfg)
        import zephyr.experiment_tracking.experiment_tracker as et

        monkeypatch.setattr(et, "_tracker_singleton", tracker)

        result = _make_c1_result()
        comp = _make_comparator(with_portfolios=True, nav_len=30)
        run_id = track_c1_result(result, comparator=comp, mode="regime", strategy_name="s1")

        meta_path = fb_dir / "c1-validation" / run_id / "run_meta.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        # tags
        assert meta["tags"]["component"] == "c1-validation"
        assert meta["tags"]["mode"] == "regime"
        assert meta["tags"]["passed"] == "False"
        assert meta["tags"]["veto_reason"] == "MaxDD 未改善"

        # params
        assert meta["params"]["mode"] == "regime"
        assert meta["params"]["strategy_name"] == "s1"
        assert "c1_sharpe_tolerance" in meta["params"]

        # metrics
        assert "baseline_sharpe" in meta["metrics"]
        assert "experiment_sharpe" in meta["metrics"]
        assert meta["metrics"]["passed"] == 0.0

        # artifacts（字典列表，每项含 filename）
        artifact_filenames = [a.get("filename", "") for a in meta["artifacts"]]
        assert "c1_summary.md" in artifact_filenames
        assert "nav_curve_baseline.csv" in artifact_filenames
        assert "nav_curve_experiment.csv" in artifact_filenames

    def test_null_backend_when_disabled(self, monkeypatch):
        """enable_tracking=False → NullBackend，run_id='null-run'，不抛。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        result = _make_c1_result()
        run_id = track_c1_result(result, comparator=None, mode="mock")
        assert run_id == "null-run"

    def test_comparator_none_skips_nav(self, monkeypatch, tmp_path):
        """comparator=None → 不写 nav CSV，但仍写 c1_summary.md。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        fb_dir = tmp_path / "fb"
        cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=fb_dir)
        tracker = ExperimentTracker(config=cfg)
        import zephyr.experiment_tracking.experiment_tracker as et

        monkeypatch.setattr(et, "_tracker_singleton", tracker)

        result = _make_c1_result()
        run_id = track_c1_result(result, comparator=None, mode="mock")
        meta = json.loads((fb_dir / "c1-validation" / run_id / "run_meta.json").read_text("utf-8"))
        artifact_filenames = [a.get("filename", "") for a in meta["artifacts"]]
        assert "c1_summary.md" in artifact_filenames
        assert not any("nav_curve" in fn for fn in artifact_filenames)
        # params 不含 c1 门槛
        assert "c1_sharpe_tolerance" not in meta["params"]

    def test_extra_tags_merged(self, monkeypatch, tmp_path):
        """extra_tags 合并到 tags。"""
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
        fb_dir = tmp_path / "fb"
        cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=fb_dir)
        tracker = ExperimentTracker(config=cfg)
        import zephyr.experiment_tracking.experiment_tracker as et

        monkeypatch.setattr(et, "_tracker_singleton", tracker)

        result = _make_c1_result(passed=True, veto_reason=None)
        run_id = track_c1_result(
            result,
            comparator=None,
            mode="mock",
            extra_tags={"git_commit": "abc123", "basket": "csi300"},
        )
        meta = json.loads((fb_dir / "c1-validation" / run_id / "run_meta.json").read_text("utf-8"))
        assert meta["tags"]["git_commit"] == "abc123"
        assert meta["tags"]["basket"] == "csi300"
        assert meta["tags"]["passed"] == "True"
