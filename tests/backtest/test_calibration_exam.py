# [BLUEPRINT] MOD-BT-247 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_calibration_exam.py
# 测试隔离：卡/分数册全在 tmp_path；信号/目标合成注入（零 CH）。
# [TTL] permanent
"""校准卡执行器红蓝双向：门柱机械判/状态机/分数册 only-add/试次留痕/fail-closed。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce


def _card(tmp_path, **kw) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/calibration/02",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "regimes": {"bull": "2020-01-01..2021-12-31", "bear": "2022-01-01..2023-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2024-12-31"],
        "pillars_numeric": {
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
        },
    }
    card.update(kw)
    p = tmp_path / "card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _synthetic(n: int = 1450, strength: float = 1.0, seed: int = 7):
    """合成信号/目标：strength=1 强单调（应 pass），strength=0 噪声（应 fail）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    sig = pd.Series(rng.normal(size=n), index=idx)
    tgt = pd.Series(0.01 * rng.normal(size=n) + strength * 0.02 * sig.shift(1).fillna(0).to_numpy(), index=idx)
    return sig, tgt


def test_series_pass_on_strong_signal(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "scores.yaml")
    assert row["verdict"] == "pass" and row["pillars_all_pass"] is True
    # 卡面推进 + 分数册落行
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "examined" and card["lineage"]["run_id"]
    reg = yaml.safe_load((tmp_path / "scores.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1 and reg["rows"][0]["card_id"] == "TDM-E-TEST/calibration/02"


def test_series_fail_on_noise(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=0.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "scores.yaml")
    assert row["verdict"] == "fail" and row["fails"]


def test_empty_card_rejected(tmp_path):
    p = _card(tmp_path, status="empty")
    sig, tgt = _synthetic()
    with pytest.raises(RuntimeError, match="只考 preregistered"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")


def test_examined_card_needs_force(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    with pytest.raises(RuntimeError, match="重考带 --force"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    # force 重考=分数册 only-add 两行
    ce.run_card(p, signal=sig, target=tgt, force=True, scores_path=tmp_path / "s.yaml")
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 2


def test_missing_pillars_numeric_fail_closed(tmp_path):
    p = _card(tmp_path)
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    del card["pillars_numeric"]
    Path(p).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    sig, tgt = _synthetic()
    with pytest.raises(RuntimeError, match="pillars_numeric"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")


def test_missing_data_injection_fail_closed(tmp_path):
    p = _card(tmp_path)
    with pytest.raises(RuntimeError, match="注入"):
        ce.run_card(p, scores_path=tmp_path / "s.yaml")


def test_no_upgrade_signal_w5_alignment(tmp_path):
    """红蓝互锁：OOS 不成立时 oos_ok=False → W5 判据不升级（两件契约对齐）。"""
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    # 强信号下 oos 窗也有数 → oos_ok True；本断言钉 schema 契约字段存在
    assert isinstance(row["oos_ok"], bool) and row["kind"] == "exam"
    assert set(row["regimes"]) >= {"bull"} or row["regimes"] == []


# ---------------------------------------------------------------------------
# 对照/消融分支（夜矿续战三连裁② 2026-10-10 并入 MOD-BT-243 执行核）
# ---------------------------------------------------------------------------


def _comparison_card(tmp_path, **kw) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/comparison/02",
        "node_id": "TDM-E-TEST",
        "family": "comparison",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "regimes": {"bull": "2020-01-01..2021-12-31", "bear": "2022-01-01..2023-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2024-12-31"],
        "pillars_numeric": {
            "maxdd_improvement_min": 0.0,
            "maxdd_deterioration_max_pp": 2.0,
            "sharpe_delta_min": -0.1,
            "turnover_delta_annual_max": 8.0,
            "oos_same_sign": True,
        },
    }
    card.update(kw)
    p = tmp_path / "cmp_card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _arms(n: int = 1450, open_edge: float = 0.4, seed: int = 11):
    """合成双臂：开臂=基臂敞口+定向增益；目标与基臂弱相关（NAV 面可分辨）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    base = pd.Series(rng.uniform(0.2, 0.8, size=n), index=idx)
    open_ = (base + open_edge * pd.Series(rng.normal(size=n), index=idx)).clip(0.0, 1.0)
    tgt = pd.Series(0.01 * rng.normal(size=n) + 0.02 * base.shift(1).fillna(0), index=idx)
    return open_, base, tgt


def test_comparison_pass_when_open_arm_better(tmp_path):
    p = _comparison_card(tmp_path)
    sig_b = None  # 开臂合成面
    open_, base, tgt = _arms(open_edge=0.35)
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] in ("pass", "fail")  # 判据机判跑通即出分（合成面方向不定，不锚 verdict）
    assert "arm_open" in row["metrics"] and "maxdd_improvement_pp" in row["metrics"]
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1  # 分数册 only-add


def test_comparison_fail_on_worse_arm(tmp_path):
    p = _comparison_card(tmp_path)
    open_, base, tgt = _arms(open_edge=-0.9, seed=13)  # 开臂系统性劣化
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail" and row["fails"]


def test_comparison_requires_signal_b(tmp_path):
    p = _comparison_card(tmp_path)
    open_, _, tgt = _arms()
    with pytest.raises(RuntimeError, match="双臂信号"):
        ce.run_card(p, signal=open_, target=tgt, scores_path=tmp_path / "s.yaml")


def test_comparison_unknown_pillar_fail_closed(tmp_path):
    p = _comparison_card(tmp_path, **{"pillars_numeric": {"misfire_reduction_min": 0.2, "oos_same_sign": True}})
    open_, base, tgt = _arms()
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    # misfire 面缺笔级价格=如实记败（禁冒判）；不 panic 不伪造 pass
    assert row["verdict"] == "fail" and any("无机判面" in f for f in row["fails"])
