# [MODULE] tests.backtest.test_cost_gate_tier_wiring
# [TTL] permanent
"""成本考尺档位传参契约钉（哑门回归）。

案卷（2026-09-23 st-e2e-20260924 实测，非推演）：
`run_cost_tier_scan` 原以**位置**方式调 `net_fn(weights, px_close, bp)`，而生产
调用方注入的是 `_c4_engine.daily_net_returns(weights, px_close, gate_limits=True,
slippage_bp=None)`——第三个位置参是 `gate_limits`，不是滑点档。后果：
①五档 Sharpe 逐位相同（合成带换手面板实测恒 10.6211），"五档滑点单调性"门从未
  真正测过滑点；②bp=0.0 落进 gate_limits 是假值，"零成本对照档"顺手把涨跌停
  可成交闸一起关掉；③原道自带的注入桩签名是 `(w, px_, slip_bp)`，与引擎不同构，
  所以 9 例全绿也照不出这个洞（测试桩自己就是第二个错）。

本文件逐条钉死：调用必须以关键字传滑点，且 gate_limits 不得被档值污染。
红证：把 exam_cost_gate 的调用改回位置传参，本文件前两例必红。
"""

from __future__ import annotations

import importlib.util
import inspect
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.regime_validation.exam_cost_gate import CostGateConfig, run_cost_tier_scan

ENGINE = Path("scripts/backtest/translated/_c4_engine.py")


def _engine():
    spec = importlib.util.spec_from_file_location("_c4_engine_for_pin", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _turnover_panel(n_days: int = 180, n_sym: int = 12):
    """**必须带换手**：静态持仓下面板对滑点不敏感，探针会失去判据力
    （2026-09-23 首版探针即栽在此，已作废重做）。"""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2025-01-02", periods=n_days)
    cols = [f"S{i}" for i in range(n_sym)]
    block = np.arange(n_days) // 5
    hold = (block[:, None] + np.arange(n_sym)[None, :]) % 3 == 0
    w = pd.DataFrame(hold.astype(float), index=idx, columns=cols)
    w = w.div(w.sum(axis=1), axis=0)
    px = pd.DataFrame(
        100.0 * np.cumprod(1.0 + rng.normal(0.0008, 0.010, (n_days, n_sym)), axis=0),
        index=idx,
        columns=cols,
    )
    return w, px


CFG = CostGateConfig()


def test_engine_signature_has_slippage_kw_and_third_positional_is_gate_limits():
    """真身签名是契约的一部分：位置传参的第 3 槽叫 gate_limits。"""
    params = list(inspect.signature(_engine().daily_net_returns).parameters)
    assert params[:4] == ["weights", "px_close", "gate_limits", "slippage_bp"]


def test_tier_scan_passes_bp_as_keyword_only():
    seen: list[tuple] = []

    def spy(weights, px_close, gate_limits=True, slippage_bp=None):
        seen.append((gate_limits, slippage_bp))
        return pd.Series(0.001, index=weights.index)

    w, px = _turnover_panel()
    run_cost_tier_scan(w, px, spy, CFG)
    assert len(seen) == len(CFG.tiers_bp)
    assert [s[1] for s in seen] == list(CFG.tiers_bp), "滑点档未逐项送达"
    assert all(s[0] is True for s in seen), "gate_limits 被滑点档值污染=传参错位复发"


def test_tier_scan_erosion_is_strictly_monotone_on_real_engine():
    """真引擎下档间必须拉开：全等即哑门（旧行为）。"""
    eng = _engine()
    w, px = _turnover_panel()
    out = run_cost_tier_scan(w, px, eng.daily_net_returns, CFG)
    vals = [out[b] for b in sorted(out)]
    assert len(set(vals)) == len(vals), f"五档 Sharpe 全等/欠分={out}——滑点未进入计算"
    assert all(b < a for a, b in itertools.pairwise(vals)), f"档间非严格下降={out}"


def test_missing_config_file_fails_closed(tmp_path, monkeypatch):
    """预注册册缺失必须拒考，不得静默回落代码默认档。"""
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader("f06pin", loader=None))
    src = Path("scripts/backtest/f06_e4_wfa_exam.py").read_text(encoding="utf-8")
    fn_src = src[src.index("def _load_cost_gate_config():") :]
    fn_src = fn_src[: fn_src.index("\ndef ")]
    ns: dict = {"_REPO": tmp_path}
    exec(compile(fn_src, "<f06pin>", "exec"), ns)  # noqa: S102 — 取函数源码片段在 tmp 环境下复算
    with pytest.raises(FileNotFoundError, match="预注册册缺失"):
        ns["_load_cost_gate_config"]()
