# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] tests.experiment_tracking.test_component_adapters
# [DOMAIN] D_INFRA_TELEMETRY
# [A_module] module_id=MOD-TEST-OBS-COMPADAPT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
"""五零件 Adapter 单元测试（50 号 §3 ⑥，M4）——regime/feature/vectorized/strategy_runner/c2c3。

覆盖:
  - 各 adapter 完整流程（FallbackBackend）：产出 run_id + run_meta.json，params/metrics/tags 齐全
  - lineage 字段贯通：上游 run_id 写入 tags（lineage_ 前缀）
  - tracker 关闭（NullBackend）：run_id="null-run"，不抛
  - 边界：shrinkage=None / config=None / nav=None / 空 DataFrame / bull_mean_shrinkage=None
  - 验收口径：每零件跑一次，query.list_runs(component) 能查到对应 run

用 SimpleNamespace/pandas 构造鸭子类型（adapters 运行时全鸭子类型，TYPE_CHECKING 隔离）。
"""
from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import pytest

import zephyr.experiment_tracking.experiment_tracker as et
from zephyr.experiment_tracking.adapters.c2c3_adapter import (
    track_c2_result,
    track_c3_result,
)
from zephyr.experiment_tracking.adapters.feature_adapter import track_feature_build
from zephyr.experiment_tracking.adapters.regime_adapter import track_regime_detection
from zephyr.experiment_tracking.adapters.strategy_runner_adapter import (
    track_strategy_runner_result,
)
from zephyr.experiment_tracking.adapters.vectorized_adapter import (
    track_vectorized_backtest,
)
from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.experiment_tracking.experiment_tracker import ExperimentTracker, reset_tracker
from zephyr.experiment_tracking.query import list_runs


@pytest.fixture(autouse=True)
def _reset_singleton():
    reset_tracker()
    yield
    reset_tracker()


@pytest.fixture
def fb_dir(monkeypatch, tmp_path):
    """强制 FallbackBackend 指向 tmp_path，返回落盘目录。"""
    monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "1")
    d = tmp_path / "fb"
    cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=d)
    monkeypatch.setattr(et, "_tracker_singleton", ExperimentTracker(config=cfg))
    return d


def _read_meta(fb_dir, component, run_id):
    return json.loads((fb_dir / component / run_id / "run_meta.json").read_text("utf-8"))


# ── 鸭子类型构造 ─────────────────────────────────────────────────


def _make_probs():
    return SimpleNamespace(
        probabilities={"r1": 0.1, "r2": 0.2, "r3": 0.4, "r4": 0.1, "r10": 0.1, "r11": 0.05, "r12": 0.05},
        dominant_regime="r3",
        dominant_frequency=0.35,
        confidence=0.4,
    )


def _make_shrinkage(enabled=True):
    return SimpleNamespace(
        value=0.82,
        confidence_signal=0.9,
        risk_signal=0.91,
        shrinkage_enabled=enabled,
    )


def _make_bt_result():
    return SimpleNamespace(
        strategy_id="topn-momentum",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 6, 30),
        sharpe_ratio=1.3,
        max_drawdown=-0.12,
        annual_return=0.25,
        total_return=0.30,
        win_rate=0.55,
        trades_count=42,
    )


def _make_bt_config():
    return SimpleNamespace(
        initial_capital="1000000",
        commission_rate="0.0003",
        slippage_bps="1",
        benchmark_symbol="000300",
        risk_free_rate=0.025,
    )


# ── regime_adapter ───────────────────────────────────────────────


class TestRegimeAdapter:
    def test_full_flow(self, fb_dir):
        run_id = track_regime_detection(
            _make_probs(), _make_shrinkage(),
            feature_stats={"n_features": 12, "missing_rate": 0.01},
            model_params={"n_states": 4},
        )
        meta = _read_meta(fb_dir, "regime-detector", run_id)
        assert meta["tags"]["component"] == "regime-detector"
        assert meta["tags"]["dominant_regime"] == "r3"
        assert meta["params"]["n_states"] == "4"  # FallbackBackend params 字符串化
        assert meta["params"]["feature_n_features"] == "12"
        assert meta["metrics"]["prob_r3"] == pytest.approx(0.4)
        assert meta["metrics"]["shrinkage_value"] == pytest.approx(0.82)
        assert meta["metrics"]["confidence_signal"] == pytest.approx(0.9)

    def test_shrinkage_none_skips_metrics(self, fb_dir):
        run_id = track_regime_detection(_make_probs(), None)
        meta = _read_meta(fb_dir, "regime-detector", run_id)
        assert "shrinkage_value" not in meta["metrics"]
        assert "shrinkage_enabled" not in meta["tags"]
        assert meta["metrics"]["confidence"] == pytest.approx(0.4)

    def test_lineage_tags(self, fb_dir):
        run_id = track_regime_detection(
            _make_probs(), _make_shrinkage(), lineage={"feature_run_id": "frun-1"}
        )
        meta = _read_meta(fb_dir, "regime-detector", run_id)
        assert meta["tags"]["lineage_feature_run_id"] == "frun-1"

    def test_null_backend(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        assert track_regime_detection(_make_probs()) == "null-run"

    def test_list_runs_queryable(self, fb_dir):
        """验收口径：零件跑一次，list_runs(component) 能查到。"""
        run_id = track_regime_detection(_make_probs(), _make_shrinkage())
        runs = list_runs(component="regime-detector", config=ExperimentTrackingConfig(fallback_dir=fb_dir))
        assert any(r.run_id == run_id for r in runs)


# ── feature_adapter ──────────────────────────────────────────────


class TestFeatureAdapter:
    def _df(self):
        return pd.DataFrame(
            {"f1": [1.0, 2.0, None], "f2": [3.0, 4.0, 5.0]},
            index=pd.date_range("2024-01-01", periods=3),
        )

    def test_full_flow(self, fb_dir):
        run_id = track_feature_build(self._df(), builder_info={"start": "2024-01-01"})
        meta = _read_meta(fb_dir, "feature-build", run_id)
        assert meta["metrics"]["rows"] == 3.0
        assert meta["metrics"]["cols"] == 2.0
        assert meta["metrics"]["missing_rate"] == pytest.approx(1 / 6)
        assert meta["params"]["n_features"] == "2"  # FallbackBackend params 字符串化
        assert meta["params"]["start"] == "2024-01-01"
        artifacts = [a["filename"] for a in meta["artifacts"]]
        assert "feature_schema.csv" in artifacts
        assert "feature_snapshot.csv" in artifacts

    def test_empty_dataframe(self, fb_dir):
        """边界：空 DataFrame 仍记录（metrics=0，无 snapshot artifact）。"""
        run_id = track_feature_build(pd.DataFrame())
        meta = _read_meta(fb_dir, "feature-build", run_id)
        assert meta["metrics"]["rows"] == 0.0
        assert meta["metrics"]["missing_rate"] == 0.0
        artifacts = [a["filename"] for a in meta["artifacts"]]
        assert "feature_snapshot.csv" not in artifacts

    def test_snapshot_rows_zero(self, fb_dir):
        run_id = track_feature_build(self._df(), snapshot_rows=0)
        meta = _read_meta(fb_dir, "feature-build", run_id)
        artifacts = [a["filename"] for a in meta["artifacts"]]
        assert "feature_snapshot.csv" not in artifacts
        assert "feature_schema.csv" in artifacts

    def test_null_backend(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        assert track_feature_build(self._df()) == "null-run"

    def test_list_runs_queryable(self, fb_dir):
        run_id = track_feature_build(self._df())
        runs = list_runs(component="feature-build", config=ExperimentTrackingConfig(fallback_dir=fb_dir))
        assert any(r.run_id == run_id for r in runs)


# ── vectorized_adapter ───────────────────────────────────────────


class TestVectorizedAdapter:
    def test_full_flow_with_nav(self, fb_dir):
        nav = pd.Series([1.0, 1.01, 1.02], index=pd.date_range("2024-01-01", periods=3))
        run_id = track_vectorized_backtest(
            _make_bt_result(), config=_make_bt_config(), nav_series=nav,
            lineage={"regime_run_id": "rrun-1"},
        )
        meta = _read_meta(fb_dir, "vectorized-backtest", run_id)
        assert meta["params"]["commission_rate"] == "0.0003"
        assert meta["params"]["slippage_bps"] == "1"
        assert meta["metrics"]["sharpe_ratio"] == pytest.approx(1.3)
        assert meta["metrics"]["trades_count"] == 42.0
        assert meta["tags"]["lineage_regime_run_id"] == "rrun-1"
        artifacts = [a["filename"] for a in meta["artifacts"]]
        assert "nav_curve.csv" in artifacts

    def test_config_and_nav_none(self, fb_dir):
        """边界：config=None + nav=None → 跳过 config params 与 nav artifact。"""
        run_id = track_vectorized_backtest(_make_bt_result())
        meta = _read_meta(fb_dir, "vectorized-backtest", run_id)
        assert "commission_rate" not in meta["params"]
        assert meta["artifacts"] == []

    def test_null_backend(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        assert track_vectorized_backtest(_make_bt_result()) == "null-run"

    def test_list_runs_queryable(self, fb_dir):
        run_id = track_vectorized_backtest(_make_bt_result())
        runs = list_runs(component="vectorized-backtest", config=ExperimentTrackingConfig(fallback_dir=fb_dir))
        assert any(r.run_id == run_id for r in runs)


# ── strategy_runner_adapter ──────────────────────────────────────


class TestStrategyRunnerAdapter:
    def _runner_config(self):
        return SimpleNamespace(
            factor_ids=("momentum_20d", "vol_60d"),
            synthesis_method="equal_weight",
            rebalance_freq="W-FRI",
            pit_shift=1,
            top_n=10,
            max_single=0.10,
            initial_capital=1_000_000.0,
            backtest_config=_make_bt_config(),
        )

    def test_full_flow(self, fb_dir):
        run_id = track_strategy_runner_result(
            _make_bt_result(), runner_config=self._runner_config(),
            lineage={"feature_run_id": "frun-9", "regime_run_id": "rrun-9"},
        )
        meta = _read_meta(fb_dir, "full-chain-backtest", run_id)
        assert meta["params"]["factor_ids"] == "momentum_20d,vol_60d"
        assert meta["params"]["synthesis_method"] == "equal_weight"
        assert meta["params"]["pit_shift"] == "1"  # FallbackBackend params 字符串化
        # 全链路成本细节（滑点/手续费）
        assert meta["params"]["commission_rate"] == "0.0003"
        assert meta["params"]["slippage_bps"] == "1"
        assert meta["tags"]["lineage_feature_run_id"] == "frun-9"
        assert meta["tags"]["lineage_regime_run_id"] == "rrun-9"
        assert meta["metrics"]["sharpe_ratio"] == pytest.approx(1.3)

    def test_config_none(self, fb_dir):
        """边界：runner_config=None → 仅 result 字段。"""
        run_id = track_strategy_runner_result(_make_bt_result())
        meta = _read_meta(fb_dir, "full-chain-backtest", run_id)
        assert "factor_ids" not in meta["params"]
        assert meta["params"]["strategy_id"] == "topn-momentum"

    def test_null_backend(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        assert track_strategy_runner_result(_make_bt_result()) == "null-run"

    def test_list_runs_queryable(self, fb_dir):
        run_id = track_strategy_runner_result(_make_bt_result())
        runs = list_runs(component="full-chain-backtest", config=ExperimentTrackingConfig(fallback_dir=fb_dir))
        assert any(r.run_id == run_id for r in runs)


# ── c2c3_adapter ─────────────────────────────────────────────────


class TestC2C3Adapter:
    def _c2_report(self):
        event = SimpleNamespace(
            name="2020-03 新冠", n_days=20,
            dd_baseline=-0.30, dd_experiment=-0.22, improvement=0.08,
        )
        return SimpleNamespace(
            events=(event,), mean_improvement=0.08, min_improvement=0.08,
            skipped=(), passed=True, summary="# C2 报告",
        )

    def _c3_report(self, bull=0.9):
        state = SimpleNamespace(
            state="r4", days=30, day_share=0.3, mean_shrinkage=0.5,
            mean_ret_baseline=-0.001, mean_ret_experiment=0.0005,
            avoided_return=0.045, contribution_share=0.7,
        )
        return SimpleNamespace(
            states=(state,), total_days=100, total_avoided=0.05,
            defensive_share=0.7, bull_mean_shrinkage=bull,
            passed=True, summary="# C3 报告",
        )

    def test_c2_full_flow(self, fb_dir):
        run_id = track_c2_result(self._c2_report(), lineage={"c1_run_id": "c1run-1"})
        meta = _read_meta(fb_dir, "c2c3-validation", run_id)
        assert meta["tags"]["kind"] == "c2"
        assert meta["tags"]["passed"] == "True"
        assert meta["tags"]["lineage_c1_run_id"] == "c1run-1"
        assert meta["metrics"]["mean_improvement"] == pytest.approx(0.08)
        assert meta["metrics"]["passed"] == 1.0
        artifacts = [a["filename"] for a in meta["artifacts"]]
        assert "c2_summary.md" in artifacts

    def test_c3_full_flow(self, fb_dir):
        run_id = track_c3_result(self._c3_report())
        meta = _read_meta(fb_dir, "c2c3-validation", run_id)
        assert meta["tags"]["kind"] == "c3"
        assert meta["metrics"]["defensive_share"] == pytest.approx(0.7)
        assert meta["metrics"]["bull_mean_shrinkage"] == pytest.approx(0.9)
        assert meta["metrics"]["r4_avoided_return"] == pytest.approx(0.045)

    def test_c3_bull_none(self, fb_dir):
        """边界：bull_mean_shrinkage=None（无 r3 样本）→ NaN 指标不抛。"""
        run_id = track_c3_result(self._c3_report(bull=None))
        meta = _read_meta(fb_dir, "c2c3-validation", run_id)
        assert meta["tags"]["kind"] == "c3"

    def test_null_backend(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_EXPERIMENT_TRACKING", "0")
        assert track_c2_result(self._c2_report()) == "null-run"
        assert track_c3_result(self._c3_report()) == "null-run"

    def test_list_runs_queryable(self, fb_dir):
        r2 = track_c2_result(self._c2_report())
        r3 = track_c3_result(self._c3_report())
        runs = list_runs(component="c2c3-validation", config=ExperimentTrackingConfig(fallback_dir=fb_dir))
        ids = {r.run_id for r in runs}
        assert {r2, r3} <= ids
