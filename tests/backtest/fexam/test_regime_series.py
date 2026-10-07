# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_regime_series.py | regime默认体制源单测（合成面板零DB）
"""regime_series 单测（裁定#489②）：默认源=sma200_default 且零 HMM 触碰；use_hmm=True 显式 opt-in 语义。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

import ch_data  # noqa: E402


def _proxy_panel(n_days=400, seed=7):
    """合成代理指数面板（date×1 symbol），覆盖 2020-01-01 起 400 个交易日。"""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n_days, freq="B")
    return pd.DataFrame({"P": 100.0 + rng.normal(0, 1, n_days).cumsum()}, index=idx)


def test_default_source_is_sma200_and_never_touches_hmm(monkeypatch):
    """默认（use_hmm=False）：来源=sma200_default，且绝不查询 HMM regime 表（未过考禁回用）。"""
    monkeypatch.setattr(ch_data, "load_close", lambda *a, **k: _proxy_panel())

    def _boom(*a, **k):
        raise AssertionError("默认路径禁止查询 HMM regime 表（裁定#489②）")

    monkeypatch.setattr(ch_data, "load_regime_states", _boom)
    regimes, source = ch_data.regime_series("2021-01-01", "2021-03-01")
    assert source == "sma200_default"
    assert regimes.attrs.get("source") == "sma200_default"
    assert len(regimes) > 0
    assert set(regimes.unique()) <= {"trend_up", "trend_down"}


def test_opt_in_hmm_overrides_when_available(monkeypatch):
    """use_hmm=True 显式 opt-in：HMM 覆盖期用 HMM 态，来源如实标注 regime_table。"""
    monkeypatch.setattr(ch_data, "load_close", lambda *a, **k: _proxy_panel())
    idx = pd.date_range("2021-01-01", "2021-03-01", freq="D")
    hmm = pd.Series(["ranging_low_vol"] * len(idx), index=idx, name="regime")
    monkeypatch.setattr(ch_data, "load_regime_states", lambda *a, **k: hmm)
    regimes, source = ch_data.regime_series("2021-01-01", "2021-03-01", use_hmm=True)
    assert source == "regime_table"
    assert regimes.attrs.get("source") == "regime_table"
    assert len(regimes) > 0
    assert (regimes == "ranging_low_vol").all()


def test_opt_in_hmm_empty_falls_back_sma(monkeypatch):
    """use_hmm=True 但 regime 表空：SMA 补洞，来源=sma_fallback（opt-in 语义不冒充默认标签）。"""
    monkeypatch.setattr(ch_data, "load_close", lambda *a, **k: _proxy_panel())
    monkeypatch.setattr(ch_data, "load_regime_states", lambda *a, **k: pd.Series(dtype="object"))
    regimes, source = ch_data.regime_series("2021-01-01", "2021-03-01", use_hmm=True)
    assert source == "sma_fallback"
    assert len(regimes) > 0


def test_default_signature_rejects_positional_use_hmm():
    """use_hmm 必须显式关键字传参——防 positional 误开 HMM（opt-in 纪律的签名级保证）。"""
    import inspect

    sig = inspect.signature(ch_data.regime_series)
    param = sig.parameters["use_hmm"]
    assert param.kind == inspect.Parameter.KEYWORD_ONLY
    assert param.default is False
