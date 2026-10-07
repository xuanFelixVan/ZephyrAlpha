# [TESTS] scripts.backtest.grid_stats_engine
# [DOMAIN] D_BACKTEST
# [TTL] permanent
"""G-D 逐格统计引擎单测（C238/C239/C251，2026-10-07）——合成数据零生产数据。

覆盖面：
- 四件套口径：ddof=0、Lo(2002) 修正因子方向（正自相关→压 SR）、Ljung-Box 不可估降级
- INSUFFICIENT-N 30 地板单列；c* 二分=解析解对拍+负期望 0 封底+单调校验
- DSR 委托 SSOT：N_eff 越大 DSR 越低；退化态 fail-closed
- SPA/StepM：强格显著、噪声格不显著；p 值下限 1/(B+1)（禁报 0）
- 分半窗：冠军后半窗翻车=不出 survivors、事件触发任务记录在场
- READY_NOT_FIRED 红证：模块无 __main__ 点火入口（手滑点火=污染统计账本）
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "backtest"))

from grid_stats_engine import (  # noqa: E402
    MIN_SAMPLES_PER_CELL,
    GridStatsConfig,
    GridStatsEngineError,
    breakeven_cost_bp,
    evaluate_grid,
    half_split_reexam,
    lo2002_annualized_sharpe,
    spa_reality_check,
    stepm,
)

MODULE_PATH = REPO / "scripts" / "backtest" / "grid_stats_engine.py"


def _iid(n: int, mu: float, sd: float, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).normal(mu, sd, n)


def _ar1(n: int, phi: float, sd_innov: float, seed: int) -> np.ndarray:
    """AR(1) 序列（正 phi=正自相关）。"""
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    x[0] = rng.normal(0, sd_innov)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(0, sd_innov)
    return x


# ── 夏普口径（⚑-2 B 案四条中的机检两条） ──────────────────────────────────


class TestLo2002Sharpe:
    def test_ddof0_and_244_basis_iid(self):
        """iid 正态：factor=1（LB 不显著），SR=μ/σ₀·√244（ddof=0+244 基准）。"""
        x = _iid(500, 0.001, 0.01, 11)
        sr, factor, p, meta = lo2002_annualized_sharpe(x, periods_per_year=244, ljung_box_alpha=0.05)
        expected = x.mean() / x.std(ddof=0) * math.sqrt(244)
        assert factor == 1.0
        assert sr == pytest.approx(expected)
        assert p is not None and p >= 0.05
        assert meta["lb_testable"] is True

    def test_positive_autocorr_shrinks_sharpe(self):
        """Lo(2002) 方向红证：正自相关序列修正因子<1，修正后 SR<未修正。"""
        x = _ar1(600, phi=0.4, sd_innov=0.01, seed=3)
        raw = float(x.mean() / x.std(ddof=0) * math.sqrt(244))
        sr, factor, p, _m = lo2002_annualized_sharpe(x, periods_per_year=244, ljung_box_alpha=0.05)
        assert p is not None and p < 0.05, "AR(1) φ=0.4 n=600 必须 LB 显著（否则检验实现错）"
        assert factor < 1.0
        assert sr < raw

    def test_short_series_lb_not_testable(self):
        """n≤q：检验不可估→factor=1 且 lb_testable=False（禁把测不了当无自相关）。"""
        x = _ar1(100, phi=0.5, sd_innov=0.01, seed=5)
        sr, factor, p, meta = lo2002_annualized_sharpe(x, periods_per_year=244, ljung_box_alpha=0.05)
        assert p is None and factor == 1.0 and meta["lb_testable"] is False


# ── c* 二分+单调 ──────────────────────────────────────────────────────────


class TestBreakevenCost:
    def test_matches_closed_form(self):
        """turnover=1 时 c*=μ·1e4 bp（线性闭式），二分解析解对拍。"""
        x = _iid(200, 0.0008, 0.01, 21)
        c_star, mono = breakeven_cost_bp(x, turnover_per_period=1.0, max_bp=5000.0, tol_bp=0.01)
        assert mono is True
        assert c_star == pytest.approx(x.mean() * 1e4, abs=0.05)

    def test_turnover_scales_down(self):
        """换手 2×/期 → c* 减半（容差=二分绝对精度 bp，非相对精度）。"""
        x = _iid(200, 0.0008, 0.01, 21)
        c1, _ = breakeven_cost_bp(x, turnover_per_period=1.0, max_bp=5000.0, tol_bp=0.01)
        c2, _ = breakeven_cost_bp(x, turnover_per_period=2.0, max_bp=5000.0, tol_bp=0.01)
        assert c2 == pytest.approx(c1 / 2.0, abs=0.05)

    def test_negative_mean_zero_floor(self):
        """负期望格 c*=0.0（零成本仍亏），不做负数外推。"""
        x = _iid(200, -0.001, 0.01, 22)
        c_star, mono = breakeven_cost_bp(x, turnover_per_period=1.0, max_bp=5000.0, tol_bp=0.01)
        assert c_star == 0.0 and mono is True


# ── 四件套主入口 ──────────────────────────────────────────────────────────


class TestEvaluateGrid:
    def test_four_piece_output_and_insufficient_n(self):
        long_ = _iid(300, 0.002, 0.01, 31)
        short_ = _iid(10, 0.002, 0.01, 32)
        stats = evaluate_grid({"good": long_, "tiny": short_})
        g = stats["good"]
        assert g.status == "OK"
        assert g.n_samples == 300
        assert 0.0 < g.win_rate < 1.0
        assert g.breakeven_cost_bp > 0.0 and g.c_star_monotonic
        assert 0.0 <= g.dsr <= 1.0
        t = stats["tiny"]
        assert t.status == "INSUFFICIENT-N"
        assert t.n_samples == 10 < MIN_SAMPLES_PER_CELL

    def test_dsr_decreases_with_neff(self):
        """N_eff 越大 DSR 越低（多重检验折减方向红证）。"""
        cells = {"a": _iid(400, 0.0015, 0.01, 41)}
        s1 = evaluate_grid(cells, n_eff=1)["a"].dsr
        s50 = evaluate_grid(cells, n_eff=50)["a"].dsr
        assert s1 > s50

    def test_neff_autocompute_panel(self):
        """n_eff=None：面板级 compute_effective_rank 折算（C251 口径），三格全同 N_eff。"""
        base = _iid(300, 0.0, 0.01, 51)
        cells = {"a": base, "b": base * 0.9, "c": base * 1.1}  # 高相关格
        stats = evaluate_grid(cells)
        neffs = {s.n_eff for s in stats.values()}
        assert len(neffs) == 1
        assert next(iter(neffs)) <= 3

    def test_empty_panel_rejected(self):
        with pytest.raises(GridStatsEngineError):
            evaluate_grid({})
        with pytest.raises(GridStatsEngineError):
            evaluate_grid({"bad": [float("nan")] * 50})


# ── G-D.3 多重检验 ────────────────────────────────────────────────────────


class TestSpaAndStepM:
    def _panel(self) -> dict[str, np.ndarray]:
        strong = _iid(400, 0.003, 0.01, 61)
        noise_b = _iid(400, 0.0, 0.01, 62)
        noise_c = _iid(400, 0.0, 0.01, 63)
        return {"strong": strong, "noise_b": noise_b, "noise_c": noise_c}

    def test_spa_strong_cell_significant_noise_not(self):
        out = spa_reality_check(self._panel(), config=GridStatsConfig(spa_n_boot=300))
        cells = out["cells"]
        assert cells["strong"]["spa_p"] < 0.10
        assert cells["noise_b"]["spa_p"] > cells["strong"]["spa_p"]
        floor = 1.0 / (300 + 1.0)
        for v in cells.values():
            assert v["spa_p"] >= floor  # 禁报 0（采样不足≠零概率）

    def test_stepm_identifies_all_significant(self):
        panel = self._panel()
        panel["strong2"] = _iid(400, 0.0025, 0.01, 64)
        out = stepm(panel, config=GridStatsConfig(spa_n_boot=300))
        assert "strong" in out["significant"]
        assert "strong2" in out["significant"]
        assert "noise_b" in out["survivors"] and "noise_c" in out["survivors"]

    def test_spa_requires_two_cells(self):
        with pytest.raises(GridStatsEngineError):
            spa_reality_check({"only": _iid(100, 0.001, 0.01, 65)})


# ── G-D.3 分半窗滚动重考（事件触发） ─────────────────────────────────────


class TestHalfSplitReexam:
    def test_champion_flip_detected_and_task_recorded(self):
        """冠军前半窗赚后半窗亏→survives=False，事件任务记录在场（禁 cron 的数据面）。"""
        rng = np.random.default_rng(71)
        good_then_bad = np.concatenate([rng.normal(0.004, 0.01, 200), rng.normal(-0.003, 0.01, 200)])
        steady = _iid(400, 0.001, 0.01, 72)
        out = half_split_reexam({"flip": good_then_bad, "steady": steady}, grid_id="grid_test")
        assert out["champion_half1"] == "flip"
        assert out["champion_survives_half2"] is False
        assert "flip" in out["sign_flips"]
        task = out["reexam_task"]
        assert task["kind"] == "rolling_reexam" and task["event"] == "grid_evaluated"
        assert "cron" in task["note"] or "Timer" in task["note"]  # 事件触发口径在场

    def test_short_panel_rejected(self):
        with pytest.raises(GridStatsEngineError):
            half_split_reexam({"a": [0.0, 0.1, 0.2], "b": [0.0, 0.1, 0.2]})


# ── READY_NOT_FIRED 红证（10_wave_plan 10.G-D） ──────────────────────────


def test_ready_not_fired_no_main_entrypoint():
    """引擎禁自带点火入口：模块不得含 __main__ 块（手滑点火=污染统计账本）。"""
    src = MODULE_PATH.read_text(encoding="utf-8")
    assert '__name__ == "__main__"' not in src
    assert "__main__" not in src
