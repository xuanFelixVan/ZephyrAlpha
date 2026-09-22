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
    CUSTOM_OPS,
    build_function_set,
    build_hypothesis,
    gloss_for_expr,
    load_whitelist,
    make_candidate_id,
    make_incremental_ic_fitness,
    make_panel_operators,
    rank_ic,
    residualize,
)


class TestWhitelist:
    def test_load_real_yaml_and_function_set_mixed(self):
        wl = load_whitelist()
        fs = build_function_set(wl, date_codes=np.zeros(10, dtype=int), symbol_codes=np.tile([0, 1], 5))
        names = {getattr(f, "name", f) for f in fs}
        assert {"add", "sub", "mul", "div", "sqrt", "log"} <= names
        assert {"rank_cs", "ts_delta_5", "ts_zscore_20", "ts_corr_20"} <= names
        # 禁用项绝不混入引擎算子集
        forbidden = {f["op"] for f in wl["forbidden"]}
        assert not (names & forbidden)

    def test_custom_ops_require_group_codes(self):
        with pytest.raises(RuntimeError, match="分组码"):
            build_function_set(load_whitelist())

    def test_function_set_excludes_trig_and_inv(self):
        fs = build_function_set(load_whitelist(), date_codes=np.zeros(10, dtype=int), symbol_codes=np.tile([0, 1], 5))
        names = {getattr(f, "name", f) for f in fs}
        assert not ({"sin", "cos", "tan", "inv"} & names)

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


class TestPanelOperators:
    """日期主序面板（每日 N=2 标的）合成数据上的分组语义验证。"""

    def _ops(self):
        # 分组码：8 交易日 × 2 标的（日期主序交替行）
        return {
            f.name: f
            for f in make_panel_operators(
                np.repeat(np.arange(8), 2), np.tile([0, 1], 8), ["rank_cs", "ts_delta_5", "ts_zscore_20", "ts_corr_20"]
            )
        }

    def _panel(self):
        # 8 个交易日 × 2 标的，日期主序：A=1..8，B=2,4,..,16 → 展平 [1,2,3,4,...]
        a = np.arange(1.0, 9.0)
        b = np.arange(2.0, 17.0, 2.0)
        return np.stack([a, b], axis=1).ravel()

    def test_rank_cs_per_date(self):
        out = self._ops()["rank_cs"](self._panel())
        assert len(out) == 16
        assert np.allclose(out[0::2], 0.5)  # A 每日都小 → 秩 0.5
        assert np.allclose(out[1::2], 1.0)  # B 每日都大 → 秩 1.0

    def test_ts_delta_5_symbolwise(self):
        out = self._ops()["ts_delta_5"](self._panel()).reshape(-1, 2)
        assert np.allclose(out[:5], 0.0)  # 段首无历史=0
        assert out[5, 0] == 5.0 and out[5, 1] == 10.0  # A:6-1=5; B:12-2=10（跨标的零污染）

    def test_ts_zscore_20_finite_and_head_zero(self):
        out = self._ops()["ts_zscore_20"](self._panel()).reshape(-1, 2)
        assert np.isfinite(out).all()
        assert np.allclose(out[:4], 0.0)  # min_periods=5 → 前 4 日无历史=0
        assert out[4, 0] > 0  # 第 5 日起可算（上斜序列 z 为正）

    def test_ts_corr_self_finite(self):
        x = self._panel()
        out = self._ops()["ts_corr_20"](x, x).reshape(-1, 2)
        assert np.isfinite(out).all()
        assert np.allclose(out[:7], 0.0)  # min_periods=8 → 前 7 日=0
        assert np.allclose(out[7], 1.0)  # 第 8 日起自相关=1


class TestTradeWhen:
    """工单 #10：WorldQuant trade_when 语义（退出优先/触发换仓/区间保持）。"""

    def _tw(self):
        dc = np.zeros(6, dtype=int)  # 单标的 6 日（symbol=0 单组）
        return make_panel_operators(dc, dc, ["trade_when"])[0]

    def test_trigger_hold_exit_semantics(self):
        tw = self._tw()
        t = np.array([1, 0, 0, 1, 0, 0], dtype=float)
        a = np.array([10, 99, 99, 20, 99, 99], dtype=float)
        e = np.array([0, 0, 1, 0, 0, 0], dtype=float)
        out = tw(t, a, e)
        assert np.allclose(out, [10, 10, 0, 20, 20, 20])
        assert np.isfinite(out).all()

    def test_exit_priority_over_same_day_trigger(self):
        tw = self._tw()
        out = tw(np.array([1.0, 1.0]), np.array([7.0, 9.0]), np.array([1.0, 0.0]))
        assert np.allclose(out, [0.0, 9.0])  # 首日退出优先清零；次日触发开新仓

    def test_no_event_head_neutral(self):
        tw = self._tw()
        out = tw(np.zeros(5), np.ones(5), np.zeros(5))
        assert np.allclose(out, 0.0)  # 全程无触发=0（段首中性语义）

    def test_whitelist_engine_bidirectional_intersection(self):
        wl = load_whitelist()
        approved = {op["op"] for grp in wl["approved"].values() for op in grp}
        assert "trade_when" in approved  # 白名单命中
        assert set(CUSTOM_OPS) <= approved  # 引擎自定义算子全集⊆白名单（反向 fail-closed）
        fs = build_function_set(wl, date_codes=np.zeros(10, dtype=int), symbol_codes=np.zeros(10, dtype=int))
        assert any(getattr(f, "__name__", "") == "trade_when" or getattr(f, "name", "") == "trade_when" for f in fs)


class TestHypothesisAndId:
    def test_hypothesis_deterministic_and_descriptive(self):
        h1 = build_hypothesis("add(ret_1d, div(vol_20d, turnover))", 0.0321, 12345)
        h2 = build_hypothesis("add(ret_1d, div(vol_20d, turnover))", 0.0321, 12345)
        assert h1 == h2
        assert "add(ret_1d" in h1 and BASELINE_TAG in h1 and "0.0321" in h1
        assert "机制自述要求" in h1  # 评分权不在本车道

    def test_hypothesis_v2_gloss_injection(self):
        wl = load_whitelist()
        expr = "log(abs(ts_delta_5(ret_5d)))"
        h = build_hypothesis(expr, 0.05, 999, gloss=gloss_for_expr(expr, wl))
        assert "log=保护对数" in h and "ts_delta_5=5日差分" in h
        assert "reject_tautology" in h  # 给 E2 可判的理由码框架

    def test_candidate_id_content_addressed(self):
        assert make_candidate_id("a*b") == make_candidate_id("a*b")
        assert make_candidate_id("a*b") != make_candidate_id("a*c")
        assert make_candidate_id(" a*b") == make_candidate_id("a*b")  # 空白 strip 归一


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
