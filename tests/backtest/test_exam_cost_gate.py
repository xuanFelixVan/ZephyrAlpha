# [A_test] module_id: zephyr.backtest.regime_validation.exam_cost_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-IBT-COSTGATE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_exam_cost_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.backtest.regime_validation.exam_cost_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/backtest/test_exam_cost_gate.py
# [MATURITY] testing
# [INVARIANTS] 纯函数测试零 IO；判定只收数字证据；fail-closed 语义（缺证据=不通过）；4440 照妖镜复形=高换手必拦
# [MODIFY-GUARD] 批C 考尺成本门（st-ibt-remedy-cf-20260923）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_exam_cost_gate.py — E4 考尺成本门（批C）正反例。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.regime_validation.exam_cost_gate import (
    CostGateConfig,
    evaluate_exam_cost_gate,
    run_cost_tier_scan,
)

CFG = CostGateConfig()

#: 规模维测试谱（40bp 档微正=旧门"纸面存活"；末段斜率 -0.02/bp 供规模外推翻案）
_SCALE_CURVE = {0.0: 0.90, 5.0: 0.75, 10.0: 0.62, 20.0: 0.42, 40.0: 0.02}


def _monotone_tier_sharpes() -> dict[float, float]:
    return {0.0: 0.80, 5.0: 0.62, 10.0: 0.45, 20.0: 0.18, 40.0: -0.05}


class TestConfigValidation:
    def test_rejects_non_ascending_tiers(self):
        with pytest.raises(ValueError):
            CostGateConfig(tiers_bp=(0.0, 10.0, 5.0, 20.0, 40.0))

    def test_rejects_missing_zero_cost_tier(self):
        with pytest.raises(ValueError):
            CostGateConfig(tiers_bp=(5.0, 10.0, 20.0, 40.0))

    def test_rejects_nonpositive_cap(self):
        with pytest.raises(ValueError):
            CostGateConfig(turnover_cap_annual_x=0.0)


class TestEvaluateCostGate:
    def test_pass_case(self):
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.016, 400, CFG)
        # 0.016×244=3.904x ≤ 8x；40bp 档 -0.05 < 0 → 存活地板不过
        assert v.passed is False and v.monotonic is True and v.full_cost_survived is False

    def test_pass_surviving_monotone_low_turnover(self):
        tiers = {0.0: 0.80, 5.0: 0.70, 10.0: 0.60, 20.0: 0.45, 40.0: 0.30}
        v = evaluate_exam_cost_gate(tiers, 0.02, 400, CFG)  # 4.88x
        assert v.passed is True and v.turnover_within_cap is True
        assert v.reasons and "成本门通过" in v.reasons[-1]

    def test_monotonicity_violation_fails(self):
        tiers = {0.0: 0.40, 5.0: 0.50, 10.0: 0.60, 20.0: 0.70, 40.0: 0.90}  # 成本升收益升=前视嫌疑
        v = evaluate_exam_cost_gate(tiers, 0.01, 400, CFG)
        assert v.passed is False and v.monotonic is False
        assert any("单调性破缺" in r for r in v.reasons)

    def test_e7_turnover_gate_blocks_high_turnover(self):
        """照妖镜复形：4440 型超短高频（年化 30x+）必被换手门拦截。"""
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.13, 400, CFG)  # 0.13×244≈31.7x
        assert v.passed is False and v.turnover_within_cap is False
        assert any("E7 换手门" in r for r in v.reasons)
        assert v.annual_turnover_x > 30

    def test_insufficient_days_fail_closed(self):
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.01, 30, CFG)
        assert v.passed is False
        assert any("证据不足" in r for r in v.reasons)


class TestTierScan:
    def test_scan_uses_injected_net_fn(self):
        idx = pd.date_range("2024-01-01", periods=120, freq="B")
        weights = pd.DataFrame({"A": [0.5] * 120}, index=idx)
        px = pd.DataFrame({"A": np.linspace(10, 12, 120)}, index=idx)

        calls: list[float] = []

        def fake_net(w, px_, gate_limits=True, slippage_bp=None):
            # 形参序/默认值刻意与引擎 daily_net_returns 同构：原桩 (w, px_, slip_bp)
            # 三个位置参恰好掩盖了调用方位置传参的缺陷（哑门由此漏网）。
            assert gate_limits is True, "gate_limits 被滑点档污染=传参错位复发"
            slip_bp = slippage_bp
            calls.append(float(slip_bp))
            base = pd.Series(0.001, index=w.index)
            return base - float(slip_bp) * 1e-4  # 滑点越高净收益越低（单调）

        out = run_cost_tier_scan(weights, px, fake_net, CFG)
        assert calls == list(CFG.tiers_bp) and 0.0 in out
        vals = [out[b] for b in sorted(out)]
        assert vals == sorted(vals, reverse=True), "注入单调函数应产出单调递减 sharpe"

    def test_nets_by_tier_injection_matches_net_fn_path(self):
        """st-ddup-20260925 去重改造①证尺：注入预算档净值与逐档 net_fn 两路同值。"""
        import sys as _sys
        from pathlib import Path as _Path

        _repo = _Path(__file__).resolve().parents[2]
        _sys.path.insert(0, str(_repo / "scripts" / "backtest" / "translated"))
        from _c4_engine import daily_net_returns as _dnr
        from _c4_engine import net_returns_by_tiers as _nbt

        idx = pd.bdate_range("2024-01-02", periods=150)
        rng = np.random.default_rng(9)
        px = pd.DataFrame(
            100 * np.cumprod(1 + rng.normal(0, 0.02, size=(150, 3)), axis=0),
            index=idx,
            columns=[f"{600000 + i}" for i in range(3)],
        )
        w = pd.DataFrame(rng.uniform(0, 0.4, size=(150, 3)), index=idx, columns=px.columns)
        tiers = tuple(CFG.tiers_bp)
        nets = _nbt(w, px, tiers)
        via_injection = run_cost_tier_scan(w, px, _dnr, CFG, tiers_bp=tiers, nets_by_tier=nets)
        via_net_fn = run_cost_tier_scan(w, px, _dnr, CFG, tiers_bp=tiers)
        assert via_injection == via_net_fn

    def test_nets_by_tier_missing_tier_fail_closed(self):
        idx = pd.date_range("2024-01-01", periods=80, freq="B")
        weights = pd.DataFrame({"A": [0.5] * 80}, index=idx)
        px = pd.DataFrame({"A": np.linspace(10, 11, 80)}, index=idx)
        with pytest.raises(ValueError, match="缺档"):
            run_cost_tier_scan(
                weights,
                px,
                lambda w, p, *, slippage_bp=None: pd.Series(0.0, index=idx),
                CFG,
                tiers_bp=tuple(CFG.tiers_bp),
                nets_by_tier={0.0: pd.Series(0.0, index=idx)},
            )


class TestScaleAwareGate:
    """裁-4 item5（st-zcloseout-20260928）：成本档规模维——门必须能 fail。"""

    def test_size_blind_pass_now_fails_at_inflated_scale(self):
        """红→绿证尺：旧门恒过的规模盲输入，注入 20% ADV 参与率后必须 FAIL。

        旧判：40bp 锚 sharpe=0.02>=0 → 全档存活 → pass（与格点成交规模无关=橡皮图章）。
        新判：参与率 0.20/锚 0.05 → 开方律乘数 2.0 → 有效档 80bp，末段斜率 -0.02/bp
        外推 sharpe=0.02-0.80=-0.78 <0 → 规模存活门拦截。
        """
        legacy = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG)
        assert legacy.passed is True and legacy.full_cost_survived is True
        scaled = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=0.20)
        assert scaled.passed is False, "规模盲旧过案在通胀规模下必须转红（裁-4：门必须能 fail）"
        assert scaled.scale_adjusted_survived is False
        assert scaled.scale_multiplier == pytest.approx(2.0)
        assert scaled.effective_top_bp == pytest.approx(80.0)
        assert any("规模存活门" in r for r in scaled.reasons)
        # 三门原判证据不回写变脸：单调解剖逐门可读
        assert scaled.monotonic is True and scaled.turnover_within_cap is True

    def test_anchor_scale_preserves_legacy_verdict(self):
        """40bp 锚语义不动：参与率=校准锚(5%)处 m=1，判定与缺省逐字一致。"""
        legacy = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG)
        anchored = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=0.05)
        assert anchored.passed is legacy.passed
        assert anchored.scale_multiplier == pytest.approx(1.0)
        assert anchored.effective_top_bp == pytest.approx(40.0)
        assert anchored.scale_adjusted_survived == legacy.full_cost_survived

    def test_small_scale_gets_no_discount(self):
        """单边只罚不奖：参与率低于锚 → m=1（不产生比冻结档更便宜的判定）。"""
        v = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=0.005)
        assert v.scale_multiplier == pytest.approx(1.0)
        assert v.passed is True

    def test_scale_verdict_monotone_no_improvement(self):
        """单调性：参与率升 → 乘数不降 → 有效档 sharpe 不升 → 判定不改善。"""
        mults = [
            evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=p).scale_multiplier
            for p in (0.02, 0.05, 0.08, 0.20, 0.45)
        ]
        assert mults == sorted(mults) and all(m >= 1.0 for m in mults)
        passed_flags = [
            evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=p).passed
            for p in (0.02, 0.08, 0.20)
        ]
        assert passed_flags[0] and not passed_flags[1] and not passed_flags[2], "更大规模不得复活判定"

    def test_multiplier_capped_at_cap(self):
        assert CostGateConfig().scale_multiplier_cap == 2.0
        v = evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=0.90)
        assert v.scale_multiplier == pytest.approx(2.0), "参与率 90% 不得突破乘数上限（防无限外推）"

    def test_nonpositive_participation_fail_closed(self):
        """fail-closed：participation 非正（含 NaN）=ValueError；None=合法禁用维。"""
        for bad in (0.0, -0.1, float("nan")):
            with pytest.raises(ValueError):
                evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG, participation_rate=bad)
        assert evaluate_exam_cost_gate(_SCALE_CURVE, 0.02, 400, CFG).scale_multiplier is None

    def test_scale_config_validation(self):
        with pytest.raises(ValueError):
            CostGateConfig(scale_participation_ref=0.0)
        with pytest.raises(ValueError):
            CostGateConfig(scale_exponent=0.0)
        with pytest.raises(ValueError):
            CostGateConfig(scale_exponent=1.5)
        with pytest.raises(ValueError):
            CostGateConfig(scale_multiplier_cap=0.5)

    def test_disabled_dimension_zero_drift_fields(self):
        """缺省调用：规模维三证据字段=None，行为零变化（消费方零改动兼容）。"""
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.016, 400, CFG)
        assert v.scale_adjusted_survived is None
        assert v.scale_multiplier is None
        assert v.effective_top_bp is None


# ---------------------------------------------------------------------------
# ⚑-2② B案机器门 v2（G-COST-BREAKEVEN-40BP）——闭式解/分池/五道门三态（W2-T2 2026-09-30）

from zephyr.backtest.regime_validation.exam_cost_gate import (  # noqa: E402
    BreakevenGateConfig,
    breakeven_cost_star_from_net_line,
    evaluate_breakeven_cost_gate,
    monotonic_grid_violations,
    solve_breakeven_cost_star,
)

BE = BreakevenGateConfig()


def _linear_sharpe_fn(mu: float, to: float, sigma: float = 0.01):
    """引擎线性成本线合成面: net(c)=gross−turnover·(15+2c)/1e4 → sharpe(c) 年化。"""

    def fn(c_bp: float) -> float:
        return (mu - to * (15.0 + 2.0 * c_bp) / 1e4) / sigma * np.sqrt(244)

    return fn


class TestBreakevenCostStar:
    def test_closed_form_equals_bisection_on_linear_line(self):
        """闭式解与案卷二分伪代码在线性成本线上逐位等价（容差=tol）。

        入参契约：mean_net_at_ref=档案序列（ref 档净收益）均值，非毛收益均值——
        gross μ=3e-4、turnover 0.03 时 ref(5bp) 档净值均值=μ−to·25/1e4。
        """
        mu, to, sigma = 3.0e-4, 0.03, 0.01
        fn = _linear_sharpe_fn(mu, to, sigma)
        bisected = solve_breakeven_cost_star(fn, BE)
        mean_at_ref = mu - to * (15.0 + 2.0 * BE.ref_bp) / 1e4
        closed = breakeven_cost_star_from_net_line(mean_at_ref, to, BE)
        assert abs(bisected - closed) <= BE.bisect_tol_bp
        # 独立真值: c* = (mu*1e4/to − 15)/2
        truth = (mu * 1e4 / to - 15.0) / 2.0
        assert abs(closed - truth) < 1e-9

    def test_monotonic_grid_clean_on_linear_line(self):
        assert monotonic_grid_violations(_linear_sharpe_fn(3.0e-4, 0.03), BE) == []

    def test_degenerate_zero_turnover_nan(self):
        assert np.isnan(breakeven_cost_star_from_net_line(1e-3, 0.0, BE))
        assert np.isnan(breakeven_cost_star_from_net_line(1e-3, float("nan"), BE))


class TestBreakevenPools:
    def test_pool_semantics_clamp_over_degenerate(self):
        cells = {
            "dead_zero": -12.0,  # 零成本即亏→钳0非幸存者
            "alive": 55.0,  # 幸存者有效
            "tiny": 0.5,  # 幸存者有效（<40bp 拉中位数）
            "beyond": 260.0,  # >200 越界单列
            "broken": float("nan"),  # 退化单列
        }
        v = evaluate_breakeven_cost_gate(cells, candidates_n=5, config=BE)
        assert v.over_hi_pool == ("beyond",)
        assert v.degenerate_pool == ("broken",)
        assert v.non_survivors_clamped0 == 1
        assert v.survivors_k == 2  # alive+tiny
        assert v.candidates_n == 5

    def test_explicit_over_label_string_pool(self):
        v = evaluate_breakeven_cost_gate({"a": 50.0, "b": BE.over_hi_label}, config=BE)
        assert v.over_hi_pool == ("b",)
        assert v.survivors_k == 1


class TestBreakevenFiveGates:
    def _pass_cells(self, n_low: int = 10, n_mid: int = 50, mid: float = 45.0, low: float = 10.0):
        cells = {}
        for i in range(n_mid):
            cells[f"m{i}"] = mid
        for i in range(n_low):
            cells[f"l{i}"] = low
        return cells

    def test_p1_p2_pass_and_fail_directions(self):
        v_pass = evaluate_breakeven_cost_gate(self._pass_cells(), config=BE)
        assert v_pass.p1_median["state"] == "PASS"  # median=45>=40
        assert v_pass.p2_p10["state"] == "PASS"  # P10=10>=0
        cells_fail = self._pass_cells(n_low=50, n_mid=10)  # 中位数跌到 10bp
        v_fail = evaluate_breakeven_cost_gate(cells_fail, config=BE)
        assert v_fail.p1_median["state"] == "FAIL"
        assert v_fail.tri_state == "FAIL"

    def test_p2_anchor_gate_boundary_semantics(self):
        """P2=案卷"Sharpe≥0 语义锚"：域=定义分布（钳零并入，§一 c*=0），P10>=0 边界。"""
        cells = {f"a{i}": 60.0 for i in range(95)}
        cells.update({f"z{i}": -5.0 for i in range(5)})  # 5% 钳零 <10% → P10 仍在幸存者域
        v = evaluate_breakeven_cost_gate(cells, config=BE)
        assert v.p2_p10["state"] == "PASS" and v.p2_p10["measured"] == 60.0
        assert v.non_survivors_clamped0 == 5
        assert v.p1_median["state"] == "PASS"
        cells11 = {f"b{i}": 60.0 for i in range(89)}
        cells11.update({f"z{i}": -5.0 for i in range(11)})  # 11% 钳零 → P10 恰落 0 边界
        v_edge = evaluate_breakeven_cost_gate(cells11, config=BE)
        assert v_edge.p2_p10["state"] == "PASS" and v_edge.p2_p10["measured"] == 0.0
        assert v_edge.quantiles_all_defined["median"] == 60.0  # 钳零不改幸存者中位数披露

    def test_p3_layer_keys_absent_indeterm(self):
        v = evaluate_breakeven_cost_gate(self._pass_cells(), layer_keys=None, config=BE)
        assert v.p3_stratified["state"] == "INDETERM"
        assert v.tri_state == "INDETERM"

    def test_p3_pass_ratio_and_insufficient_n(self):
        cells = self._pass_cells()
        keys = {f"m{i}": ("T2", "famA", "up") for i in range(50)}
        keys.update({f"l{i}": ("T1", "famB", "down") for i in range(10)})
        v_ok = evaluate_breakeven_cost_gate(cells, layer_keys=keys, config=BE)
        # T1 层 n=10<30 → INSUFFICIENT-N → INDETERM（禁算绿）
        assert v_ok.p3_stratified["state"] == "INDETERM"
        big = {**{f"m{i}": 50.0 for i in range(40)}, **{f"l{i}": 50.0 for i in range(40)}}
        keys2 = {**{f"m{i}": ("A", "f1", "up") for i in range(40)}, **{f"l{i}": ("B", "f2", "dn") for i in range(40)}}
        v_pass = evaluate_breakeven_cost_gate(big, layer_keys=keys2, config=BE)
        assert v_pass.p3_stratified["state"] == "PASS"
        mixed = {**{f"m{i}": 50.0 for i in range(40)}, **{f"l{i}": 5.0 for i in range(40)}}
        v_fail = evaluate_breakeven_cost_gate(mixed, layer_keys=keys2, config=BE)
        assert v_fail.p3_stratified["state"] == "FAIL"  # 一层达标一层不达标→占比 0.5

    def test_p4_scale_absent_indeterm_measured_directions(self):
        v_absent = evaluate_breakeven_cost_gate(self._pass_cells(), scale_c_star=None, config=BE)
        assert v_absent.p4_scale["state"] == "INDETERM"
        v_ok = evaluate_breakeven_cost_gate(
            {"a": 50.0}, scale_c_star={"a": {1.0: 50.0, 5.0: 52.0, 10.0: 55.0}}, config=BE
        )
        assert v_ok.p4_scale["state"] == "PASS"
        v_bad = evaluate_breakeven_cost_gate(
            {"a": 50.0}, scale_c_star={"a": {1.0: 50.0, 5.0: 52.0, 10.0: 70.0}}, config=BE
        )
        assert v_bad.p4_scale["state"] == "FAIL"

    def test_p5_data_version_fields(self):
        dv_ok = {
            "adjustment_basis": "hfq",
            "snapshot_date": "2026-09-30",
            "snapshot_sha256": "ab" * 32,
            "n_trials": 3700,
        }
        v_ok = evaluate_breakeven_cost_gate(self._pass_cells(), data_version=dv_ok, config=BE)
        assert v_ok.p5_data_version["state"] == "PASS"
        v_missing = evaluate_breakeven_cost_gate(self._pass_cells(), data_version={"n_trials": 3700}, config=BE)
        assert v_missing.p5_data_version["state"] == "INDETERM"

    def test_tri_state_all_pass_requires_p3_p4_p5(self):
        dv = {"adjustment_basis": "hfq", "snapshot_date": "d", "snapshot_sha256": "s", "n_trials": 1}
        cells = {**{f"m{i}": 50.0 for i in range(40)}, **{f"l{i}": 50.0 for i in range(40)}}
        keys = {**{f"m{i}": ("A", "f", "up") for i in range(40)}, **{f"l{i}": ("B", "g", "dn") for i in range(40)}}
        scale = {g: {1.0: cells[g], 5.0: cells[g] * 1.02, 10.0: cells[g] * 1.05} for g in cells}
        v = evaluate_breakeven_cost_gate(cells, layer_keys=keys, scale_c_star=scale, data_version=dv, config=BE)
        assert v.tri_state == "PASS" and v.passed


class TestBreakevenConfigValidation:
    def test_rejects_bad_bounds(self):
        with pytest.raises(ValueError):
            BreakevenGateConfig(ref_bp=300.0, hi_bp=200.0)
        with pytest.raises(ValueError):
            BreakevenGateConfig(p1_median_bp_min=-1.0)
        with pytest.raises(ValueError):
            BreakevenGateConfig(p3_ratio_min=1.5)
        with pytest.raises(ValueError):
            BreakevenGateConfig(p3_layer_min_n=0)
        with pytest.raises(ValueError):
            BreakevenGateConfig(p4_scale_sensitivity_max=0.0)
        with pytest.raises(ValueError):
            BreakevenGateConfig(bisect_tol_bp=0.0)
