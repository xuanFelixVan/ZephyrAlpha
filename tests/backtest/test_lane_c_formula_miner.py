# [BLUEPRINT] MOD-BT-155 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_c_formula_miner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas
# [CONSUMERS] MOD-BT-155 lane_c_formula_miner 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 CH：面板/GP 全不打桩真跑只测纯核；白名单 YAML 为仓库只读真源
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-155 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1C 公式挖掘机纯函数核单测——残差化/秩IC/fitness工厂/白名单交集/出生证，零网络。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.lane_c_formula_miner import (
    BASELINE_TAG,
    build_function_set,
    build_hypothesis,
    load_whitelist,
    make_candidate_id,
    make_incremental_ic_fitness,
    rank_ic,
    residualize,
)


class TestWhitelist:
    def test_load_real_yaml_and_approved_ops(self):
        wl = load_whitelist()
        ops = build_function_set(wl)
        assert {"add", "sub", "mul", "div", "sqrt", "log"} <= set(ops)
        # 禁用项绝不混入引擎算子集
        forbidden = {f["op"] for f in wl["forbidden"]}
        assert not (set(ops) & forbidden)

    def test_function_set_excludes_trig_and_inv(self):
        ops = build_function_set(load_whitelist())
        assert not ({"sin", "cos", "tan", "inv"} & set(ops))

    def test_owner_decisions_recorded(self):
        wl = load_whitelist()
        decided = {d["item"]: d["decision"] for d in wl["decided_by_owner"]}
        assert decided["选型"] == "双轨分期"
        assert "REG-IND-001" in decided["增量IC基座"]
        assert wl["constraints"]["population_size"] == 1000
        assert wl["constraints"]["generations"] == 50


class TestResidualize:
    def test_removes_linear_dependence_on_baseline(self):
        rng = np.random.default_rng(7)
        base = rng.normal(size=(500, 3))
        x = base @ np.array([2.0, -1.0, 0.5]) + 0.3 + rng.normal(scale=0.1, size=500)
        resid = residualize(x, base)
        # 残差与每个基座列的线性相关应接近 0
        for j in range(3):
            assert abs(np.corrcoef(resid, base[:, j])[0, 1]) < 0.1

    def test_nan_rows_masked_out(self):
        base = np.ones((20, 1))
        x = np.arange(20.0)
        x[3] = np.nan
        resid = residualize(x, base)
        assert np.isnan(resid[3])
        assert np.isfinite(resid).sum() == 19

    def test_empty_baseline_returns_copy(self):
        x = np.array([1.0, 2.0, 3.0])
        out = residualize(x, np.empty((0,)))
        assert np.allclose(out, x)


class TestRankIC:
    def test_perfect_monotonic(self):
        a = np.arange(50.0)
        assert rank_ic(a, a * 3 + 1) > 0.99
        assert rank_ic(a, -a) < -0.99

    def test_nan_paired_removal_and_small_sample(self):
        a = np.arange(20.0)
        b = a.copy()
        b[5] = np.nan
        assert rank_ic(a, b) > 0.99  # 只剩 19 对仍算
        assert rank_ic(np.arange(5.0), np.arange(5.0)) == 0.0  # 样本<10 记 0


class TestIncrementalICFitness:
    def test_incremental_beats_raw_when_candidate_is_baseline_combo(self):
        rng = np.random.default_rng(11)
        base = rng.normal(size=(2000, 2))
        fwd = rng.normal(scale=0.02, size=2000)
        base_ic = (base * np.array([0.01, -0.005])).sum(axis=1)  # 基座对 fwd 有真预测力
        fwd = fwd + base_ic
        candidate = base_ic + rng.normal(scale=0.001, size=2000)  # 候选=基座线性组合+微噪
        f = make_incremental_ic_fitness(base, fwd)
        # 候选若只是基座的翻版 → 残差≈噪音 → 增量 IC 应远小于其原始 IC
        raw_ic = rank_ic(candidate, fwd)
        incr_ic = f(fwd, candidate.copy(), np.ones(2000))
        assert incr_ic < raw_ic
        assert abs(incr_ic) < 0.1

    def test_genuine_new_information_keeps_ic(self):
        rng = np.random.default_rng(13)
        base = rng.normal(size=(2000, 2))
        new_signal = rng.normal(size=2000)
        fwd = new_signal * 0.02
        f = make_incremental_ic_fitness(base, fwd)
        assert f(fwd, new_signal.copy(), np.ones(2000)) > 0.5

    def test_nan_pred_tolerated(self):
        rng = np.random.default_rng(3)
        base = rng.normal(size=(100, 1))
        y = rng.normal(size=100)
        y_pred = rng.normal(size=100)
        y_pred[:5] = np.nan
        f = make_incremental_ic_fitness(base, y)
        v = f(y, y_pred, np.ones(100))
        assert np.isfinite(v)


class TestHypothesisAndId:
    def test_hypothesis_deterministic_and_descriptive(self):
        h1 = build_hypothesis("add(ret_1d, div(vol_20d, turnover))", 0.0321, 12345)
        h2 = build_hypothesis("add(ret_1d, div(vol_20d, turnover))", 0.0321, 12345)
        assert h1 == h2
        assert "add(ret_1d" in h1 and BASELINE_TAG in h1 and "0.0321" in h1
        assert "机制待审" in h1  # 评分权不在本车道

    def test_candidate_id_content_addressed(self):
        assert make_candidate_id("a*b") == make_candidate_id("a*b")
        assert make_candidate_id("a*b") != make_candidate_id("a*c")
        assert make_candidate_id(" a*b") == make_candidate_id("a*b")  # 空白 strip 归一


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
