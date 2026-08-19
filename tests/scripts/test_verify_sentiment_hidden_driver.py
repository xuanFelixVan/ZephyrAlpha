# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.7.4
# [TTL] permanent
"""Hawkes+block-bootstrap 隐形驱动验证脚本测试（合成模式 + CSV 模式 + 退化输入）。"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "verify_sentiment_hidden_driver",
    _ROOT / "scripts" / "verify_sentiment_hidden_driver.py",
)
verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verifier)


class TestSyntheticMode:
    def test_main_synthetic_exit_zero_and_report(self, capsys: pytest.CaptureFixture):
        rc = verifier.main(["--n-days", "120", "--n-bootstrap", "50", "--seed", "7"])
        assert rc == 0
        report = json.loads(capsys.readouterr().out)
        assert report["source"] == "synthetic"
        assert report["n_days"] == 120
        assert report["n_bootstrap"] == 50
        assert set(report["driver_verdict"]) == {"daban", "event_driven", "multifactor"}
        # 合成数据打板为强驱动设计 → ρ 应显著高于多因子
        assert (
            report["driver_verdict"]["daban"]["rho"]
            > report["driver_verdict"]["multifactor"]["rho"]
        )
        # 分层结果覆盖 5 阶段
        assert len(report["stratification"]) == 5

    def test_hawkes_simulation_produces_events(self):
        events = verifier.simulate_hawkes_events(100, 0.6, 0.45, 0.9, seed=1)
        assert len(events) > 0
        assert all(0.0 <= t < 100 for t in events)
        assert events == sorted(events)

    def test_daily_intensity_positive(self):
        from zephyr.signal_ashare.sentiment_cycle import SentimentHawkesParams

        params = SentimentHawkesParams(lambda_0=0.6, alpha=0.45, beta=0.9, critical_ratio=0.5)
        series = verifier.daily_intensity_series([1.0, 2.5, 3.0], params, 10)
        assert len(series) == 10
        assert all(v >= params.lambda_0 for v in series)
        assert series[2] > series[9]  # 事件近端强度高于远端（指数衰减）


class TestCsvMode:
    def _write_csv(self, path: pathlib.Path, n: int = 60, with_phase: bool = True):
        lines = ["daban,multifactor,event_driven,intensity,phase" if with_phase
                 else "daban,multifactor,event_driven,intensity"]
        for i in range(n):
            lam = 0.5 + (i % 10) * 0.1
            phase = ["冰点", "反核", "主升", "疯狂", "退潮"][i % 5]
            row = f"{lam * 0.01:.5f},{0.001:.5f},{lam * 0.005:.5f},{lam:.3f}"
            lines.append(f"{row},{phase}" if with_phase else row)
        path.write_text("\n".join(lines), encoding="utf-8")

    def test_csv_with_phase(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        csv_path = tmp_path / "data.csv"
        self._write_csv(csv_path, n=60, with_phase=True)
        rc = verifier.main(["--csv", str(csv_path), "--n-bootstrap", "30"])
        assert rc == 0
        report = json.loads(capsys.readouterr().out)
        assert report["source"].startswith("csv:")
        assert report["driver_verdict"]["daban"]["rho"] > 0.9  # 完全线性构造
        assert report["stratification"]  # 有 phase 列 → 分层输出非空

    def test_csv_without_phase(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        csv_path = tmp_path / "data.csv"
        self._write_csv(csv_path, n=60, with_phase=False)
        rc = verifier.main(["--csv", str(csv_path), "--n-bootstrap", "30"])
        assert rc == 0
        report = json.loads(capsys.readouterr().out)
        assert report["stratification"] == {}

    def test_csv_missing_column_exit_2(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        bad = tmp_path / "bad.csv"
        bad.write_text("daban,intensity\n0.01,0.5\n", encoding="utf-8")
        rc = verifier.main(["--csv", str(bad)])
        assert rc == 2
        assert "缺列" in capsys.readouterr().err

    def test_csv_too_short_exit_2(self, tmp_path: pathlib.Path):
        short = tmp_path / "short.csv"
        self._write_csv(short, n=5)
        rc = verifier.main(["--csv", str(short)])
        assert rc == 2
