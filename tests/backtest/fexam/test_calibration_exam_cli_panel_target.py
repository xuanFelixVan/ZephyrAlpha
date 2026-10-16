# [TTL] permanent
# 测试隔离：卡/分数册/试次册全在 tmp_path；信号/目标合成注入（零 CH 零生产路径写）。
"""CLI --target-csv panel 回归：多列目标宽表经 CLI 进 run_card 必须保列（run_card API 同语义）。

缺陷史：calibration_exam.main 曾对 target 无条件 t.iloc[:, 0] 砍单列 ⇒ panel 卡走 CLI 必被
_shape_preflight 拦成 blocked(shape_mismatch)，panel 卡被迫禁走 CLI（只走 run_card API）。
回归钉：CLI 面板三件套（panel 信号 csv + panel 目标 csv + panel 卡）应与 run_card API 同判 pass。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce
from zephyr.backtest.core import n_trial_ledger as _ntl


@pytest.fixture(autouse=True)
def _isolate_trial_ledger(tmp_path, monkeypatch):
    """同域 test_calibration_shape_preflight 同款：本支全篇禁写生产 N 账本（根宪法 §9 条目 6）。"""
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    target = tmp_path / "trial_ledger_registry.yaml"
    TrialLedger(registry_path=target).load_registry(create_if_missing=True)
    monkeypatch.setattr(_ntl, "LEDGER_REGISTRY_PATH", target)
    yield target


def _panel_pair_csvs(tmp_path: Path, n: int = 900, ncols: int = 40, seed: int = 7):
    """合成面板宽表落成两张 CSV（signal / target），fwd[t] 由 panel[t-1] 生成（PIT 同既有模式）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    cols = [f"S{i:04d}" for i in range(ncols)]
    panel = pd.DataFrame(rng.normal(size=(n, ncols)), index=idx, columns=cols)
    fwd = pd.DataFrame(
        0.05 * panel.shift(1).fillna(0).to_numpy() + 0.01 * rng.normal(size=(n, ncols)), index=idx, columns=cols
    )
    sig_p = tmp_path / "signal_panel.csv"
    tgt_p = tmp_path / "target_panel.csv"
    panel.to_csv(sig_p)
    fwd.to_csv(tgt_p)
    return str(sig_p), str(tgt_p), idx


def _panel_card(tmp_path: Path, idx: pd.DatetimeIndex) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/cli_panel/01",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": "panel",
        "window": {"in_sample": ["2020-01-01", "2023-12-31"], "regimes": {}},
        "pillars_numeric": {"ic_mean_min": 0.0, "oos_same_sign": True},
        "oos_window_ref": [str(idx[700].date()), str(idx[-1].date())],
    }
    p = tmp_path / "card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def test_cli_target_csv_keeps_panel_columns(tmp_path, monkeypatch, capsys):
    """panel 卡走 CLI：--target-csv 多列宽表必须整面进 run_card（不得砍单列），
    判分与 run_card API 同语义出 pass；分数册落在 tmp_path 隔离面。"""
    sig_csv, tgt_csv, idx = _panel_pair_csvs(tmp_path)
    card = _panel_card(tmp_path, idx)
    captured: dict = {}
    real_run_card = ce.run_card

    def _run_card_wrapper(*a, **kw):
        captured["args"] = a
        captured["kw"] = kw
        return real_run_card(
            *a,
            **kw,
            scores_path=tmp_path / "s.yaml",
            ledger_registry_path=tmp_path / "led.yaml",
        )

    monkeypatch.setattr(ce, "run_card", _run_card_wrapper)
    monkeypatch.setattr(
        sys, "argv", ["calibration_exam.py", "--card", card, "--signal-csv", sig_csv, "--target-csv", tgt_csv]
    )
    rc = ce.main()
    tgt = captured["kw"]["target"]
    assert isinstance(tgt, pd.DataFrame), f"CLI 把多列 panel target 砍成了 {type(tgt).__name__}"
    assert tgt.shape[1] == 40, f"CLI 只保了 {tgt.shape[1]} 列（应 40 列整面）"
    assert rc == 0, f"CLI 退出码 {rc}，row={captured.get('kw')}"
    out = capsys.readouterr().out
    assert '"verdict": "pass"' in out
