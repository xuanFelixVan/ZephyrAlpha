# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_ic_exam.py | IC考试引擎单测（合成面板零DB）
"""ic_exam 单测：秩IC等价性/统计/判定/体制切片/断点续跑幂等（tmp_path 注入）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from ic_exam import (  # noqa: E402
    fast_rank_ic,
    ic_stats,
    judge,
    regime_ic_slice,
    slice_ic,
    turnover_proxy,
)

from zephyr.factor.core.evaluation.metrics import compute_ic_series  # noqa: E402


def _panels(n_days=260, n_sym=40, skill=0.5, seed=11):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2025-01-01", periods=n_days, freq="B")
    cols = [f"S{i:03d}" for i in range(n_sym)]
    skill_vec = pd.Series(rng.normal(size=n_sym), index=cols)
    noise = pd.DataFrame(rng.normal(0, 1.0, (n_days, n_sym)), index=idx, columns=cols)
    panel = noise.add(skill_vec * 2.0, axis=1)
    fwd = panel.shift(-5) * skill + pd.DataFrame(rng.normal(0, 1.0, (n_days, n_sym)), index=idx, columns=cols)
    panel.iloc[:20, :5] = np.nan  # 造 NaN 覆盖路径
    return panel, fwd


def test_fast_rank_ic_matches_kernel():
    panel, fwd = _panels()
    a = compute_ic_series(panel, fwd)
    b = fast_rank_ic(panel, fwd)
    common = a.index.intersection(b.index)
    assert len(common) > 100
    assert (a.loc[common] - b.loc[common]).abs().max() < 1e-6


def test_ic_stats_and_slice():
    panel, fwd = _panels()
    ic = fast_rank_ic(panel, fwd)
    st = ic_stats(ic)
    assert st["ic_mean"] > 0.2 and st["n_obs"] > 100
    head = slice_ic(ic, "2025-10-09", "2026-09-30")
    assert len(head) < len(ic)  # 切片确实变短
    empty = ic_stats(pd.Series(dtype=float))
    assert empty["ic_mean"] == 0.0 and empty["n_obs"] == 0


def test_judge_three_states():
    line = {"abs_ic_min": 0.02, "icir_min": 0.3, "ic_retain_min": 0.5}
    assert judge(ic_h=0.05, icir_h=0.6, retain=0.9, coverage=0.9, direction="long", pass_line=line)[0] == "pass"
    assert judge(ic_h=-0.05, icir_h=-0.6, retain=0.9, coverage=0.9, direction="short", pass_line=line)[0] == "pass"
    assert (
        judge(ic_h=0.001, icir_h=0.05, retain=0.2, coverage=0.9, direction=None, pass_line=line)[0]
        == "retire_candidate"
    )
    assert judge(ic_h=0.01, icir_h=0.2, retain=0.7, coverage=0.9, direction=None, pass_line=line)[0] == "rework"
    assert judge(ic_h=0.05, icir_h=0.6, retain=0.9, coverage=0.3, direction=None, pass_line=line)[0] == "rework"


def test_regime_slice_small_sample_na():
    ic = pd.Series([0.1, -0.1], index=pd.date_range("2025-01-01", periods=2))
    regimes = pd.Series(["trend_up", "trend_down"], index=ic.index)
    out = regime_ic_slice(ic, regimes)
    assert out["trend_up"]["ic_mean"] != out["trend_up"]["ic_mean"]  # NaN=小样本禁结论
    assert out["trend_up"]["n_obs"] == 1


def test_turnover_proxy_range():
    rng = np.random.default_rng(3)
    idx = pd.date_range("2025-01-01", periods=200, freq="B")
    static = pd.DataFrame({f"S{i}": [i] * len(idx) for i in range(30)}, index=idx)  # 秩不变
    t_static = turnover_proxy(static, idx)
    assert t_static < 1e-9  # 零换手
    churn = pd.DataFrame(rng.normal(size=(len(idx), 30)), index=idx)  # 纯噪声
    t_churn = turnover_proxy(churn, idx)
    assert t_churn > 0.8  # 高换手


def test_run_exam_checkpoint_resume(tmp_path, monkeypatch):
    """断点续跑：第一次跑完落 ckpt，二次跑零新增计算（通过 ckpt 复用）。"""
    import ch_data
    import ic_exam

    roster = {
        "factor": [
            {
                "object_id": "FCT-A-001",
                "bucket": "ch_backed",
                "ch_backings": ["c1_market.technical_indicator.ma_5"],
                "direction": "long",
                "regime_valid": [],
            },
            {"object_id": "FCT-A-002", "bucket": "non_quantified", "ch_backings": [], "direction": None},
        ],
    }
    calls = {"n": 0}
    fake = {
        "per_horizon": {
            "5": {
                "holdout": {"ic_mean": 0.05, "icir": 0.6, "n_obs": 200},
                "is_ref": {"ic_mean": 0.06, "icir": 0.7, "n_obs": 240},
                "retain": 0.83,
            }
        },
        "headline": {"coverage_holdout": 0.9, "turnover_proxy": 0.2, "regime_ic": {}, "regime_source": "regime_table"},
    }

    def spy_measure(*a, **k):
        calls["n"] += 1
        return dict(fake)  # 零CH依赖：只验 checkpoint 语义

    monkeypatch.setattr(ic_exam, "_measure_column", spy_measure)
    monkeypatch.setattr(ch_data, "load_close", lambda *a: pd.DataFrame())
    monkeypatch.setattr(ch_data, "regime_series", lambda *a: (pd.Series(dtype="object"), "test"))

    out1 = tmp_path / "book.yaml"
    ck1 = tmp_path / "a.jsonl"
    ic_exam.run_exam(roster, "factor", out1, ck1)
    book1 = yaml.safe_load(out1.read_text(encoding="utf-8"))
    assert book1["counts"]["total"] == 2
    assert calls["n"] == 1  # 同列只算一次

    # 第二次：ckpt 命中，measure 不应再被调用
    calls2 = {"n": 0}

    def spy2(*a, **k):
        calls2["n"] += 1
        return dict(fake)

    monkeypatch.setattr(ic_exam, "_measure_column", spy2)
    out2 = tmp_path / "book2.yaml"
    ic_exam.run_exam(roster, "factor", out2, ck1)
    assert calls2["n"] == 0  # 全部命中 checkpoint
    book2 = yaml.safe_load(out2.read_text(encoding="utf-8"))
    assert book2["counts"] == book1["counts"]
    assert sum(1 for r in book2["results"] if r["verdict"] == "pass") == 1
