# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""StrategyBook (MOD-POS-020) 单元测试。

覆盖：31_position_sizing §2.2 策略层粗仓位契约——
- 等权 w=budget/N（§2.2.3）
- inverse-vol w∝1/σ（§2.2.2 Morwane 范式）
- σ_i 异常判定 4 检查链 + 部分降级（§2.2.2，2026-08-10 施工流程补充）
- 禁用 Kelly/MVO（§2.7 边界声明）
- TargetPortfolio 契约（§2.2.4）+ budget 裁剪
- 回撤 Protocol 四级（30号 §2.5）+ rebalance_to_budget
"""

from __future__ import annotations

import math
from datetime import date

import pytest

from zephyr.position.core.strategy_book import (
    MIN_LISTING_DAYS,
    MIN_VALID_SAMPLES,
    SIGMA_EXTREME_CAP,
    StrategyBook,
    TargetPortfolio,
    VolatilityInfo,
    scores_to_weights,
)


class _DummyBook(StrategyBook):
    """测试用 StrategyBook：select_stocks 直接返回 alpha_signals['symbols']。"""

    def select_stocks(self, alpha_signals: dict) -> list[str]:
        return list(alpha_signals.get("symbols", []))


def _make_book(sizing: str = "risk_parity", budget: float = 0.90) -> _DummyBook:
    book = _DummyBook("test_strat", sizing_method=sizing)
    book._current_budget = budget
    return book


# ══ inverse-vol / 等权公式（§2.2.2 / §2.2.3）══


class TestSizingFormulas:
    def test_inverse_vol_formula(self) -> None:
        """inverse-vol：w_i = budget × (1/σ_i)/Σ(1/σ_j)。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], {"A": 0.20, "B": 0.40})
        # 1/0.2=5, 1/0.4=2.5 → A: 5/7.5×0.9=0.6, B: 2.5/7.5×0.9=0.3
        assert pos["A"].target_weight == pytest.approx(0.60)
        assert pos["B"].target_weight == pytest.approx(0.30)
        assert "risk_parity" in pos["A"].reason

    def test_inverse_vol_sum_equals_budget(self) -> None:
        book = _make_book(budget=0.80)
        pos = book.size_positions(["A", "B", "C"], {"A": 0.15, "B": 0.25, "C": 0.35})
        total = sum(tw.target_weight for tw in pos.values())
        assert total == pytest.approx(0.80)

    def test_equal_weight_formula(self) -> None:
        """等权：w_i = budget / N。"""
        book = _make_book(sizing="equal_weight", budget=0.80)
        pos = book.size_positions(["A", "B", "C", "D"])
        for tw in pos.values():
            assert tw.target_weight == pytest.approx(0.20)

    def test_no_volatility_data_falls_back_equal_weight(self) -> None:
        """risk_parity 无波动率数据 → 整体等权（旧行为保留）。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], None)
        for tw in pos.values():
            assert tw.target_weight == pytest.approx(0.45)

    def test_kelly_forbidden(self) -> None:
        """§2.7 边界：策略层禁用 Kelly。"""
        with pytest.raises(ValueError, match="禁用"):
            _DummyBook("s", sizing_method="kelly")

    def test_mvo_forbidden(self) -> None:
        """§3.1：禁用 MVO。"""
        with pytest.raises(ValueError, match="禁用"):
            _DummyBook("s", sizing_method="mvo")


# ══ σ_i 异常判定 4 检查链（§2.2.2，本次施工核心）══


class TestSigmaAnomalyDegradation:
    def test_rule1_missing_from_dict(self) -> None:
        """规则1 缺失：标的不在 volatility_data → 部分降级等权 budget/N。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], {"A": 0.20})
        assert pos["B"].target_weight == pytest.approx(0.45)  # 等权 0.9/2
        assert "降级" in pos["B"].reason and "缺失" in pos["B"].reason
        # A 独占剩余 budget×1/2 = 0.45
        assert pos["A"].target_weight == pytest.approx(0.45)

    def test_rule1_zero_negative_nan(self) -> None:
        """规则1：σ=0 / 负 / NaN → 降级。"""
        book = _make_book(budget=0.90)
        for bad in (0.0, -0.2, math.nan):
            pos = book.size_positions(["A", "B"], {"A": 0.20, "B": bad})
            assert pos["B"].target_weight == pytest.approx(0.45), f"σ={bad} 应降级"
            assert "降级" in pos["B"].reason

    def test_rule3_extreme_sigma(self) -> None:
        """规则3 极端值：σ 年化 > 150% → 降级。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], {"A": VolatilityInfo(0.20), "B": VolatilityInfo(1.80)})
        assert pos["B"].target_weight == pytest.approx(0.45)
        assert "极端" in pos["B"].reason
        # 边界值不触发
        pos = book.size_positions(["A", "B"], {"A": VolatilityInfo(0.20), "B": VolatilityInfo(SIGMA_EXTREME_CAP)})
        assert "降级" not in pos["B"].reason

    def test_rule2_insufficient_samples(self) -> None:
        """规则2 样本量门控：有效交易日 < 30 → 降级。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(
            ["A", "B"],
            {"A": VolatilityInfo(0.20), "B": VolatilityInfo(0.30, valid_samples=20)},
        )
        assert pos["B"].target_weight == pytest.approx(0.45)
        assert "样本不足" in pos["B"].reason
        # 边界：30 不触发
        pos = book.size_positions(
            ["A", "B"],
            {"A": VolatilityInfo(0.20), "B": VolatilityInfo(0.30, valid_samples=MIN_VALID_SAMPLES)},
        )
        assert "降级" not in pos["B"].reason

    def test_rule4_new_listing_cold_start(self) -> None:
        """规则4 新股冷启：上市 < 60 交易日 → 降级。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(
            ["A", "B"],
            {"A": VolatilityInfo(0.20), "B": VolatilityInfo(0.30, listing_days=45)},
        )
        assert pos["B"].target_weight == pytest.approx(0.45)
        assert "新股冷启" in pos["B"].reason
        # 边界：60 不触发
        pos = book.size_positions(
            ["A", "B"],
            {"A": VolatilityInfo(0.20), "B": VolatilityInfo(0.30, listing_days=MIN_LISTING_DAYS)},
        )
        assert "降级" not in pos["B"].reason

    def test_metadata_none_skips_rule2_rule4(self) -> None:
        """元数据 None（信息不足）不误判规则2/4，仅规则1/3 可判。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], {"A": 0.20, "B": 0.40})  # float 无元数据
        assert "降级" not in pos["B"].reason
        assert pos["B"].target_weight == pytest.approx(0.30)  # 正常 inverse-vol

    def test_partial_degradation_preserves_inverse_vol_ratio(self) -> None:
        """部分降级：正常标的间 inverse-vol 比例不变，异常标的取等权份额。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(
            ["A", "B", "C"],
            {"A": 0.20, "B": 0.40, "C": VolatilityInfo(2.0)},  # C 极端降级
        )
        # C 取等权 0.9/3 = 0.30；A/B 瓜分剩余 0.6，inverse-vol 比例 5:2.5
        assert pos["C"].target_weight == pytest.approx(0.30)
        assert pos["A"].target_weight == pytest.approx(0.60 * (5.0 / 7.5))
        assert pos["B"].target_weight == pytest.approx(0.60 * (2.5 / 7.5))
        # 总和 = budget
        total = sum(tw.target_weight for tw in pos.values())
        assert total == pytest.approx(0.90)

    def test_all_anomaly_falls_back_equal_weight(self) -> None:
        """全部异常 → 整体等权。"""
        book = _make_book(budget=0.80)
        pos = book.size_positions(["A", "B"], {"A": 0.0, "B": math.nan})
        for tw in pos.values():
            assert tw.target_weight == pytest.approx(0.40)

    def test_float_backward_compatibility(self) -> None:
        """旧调用方式 dict[str, float] 向后兼容。"""
        book = _make_book(budget=0.90)
        pos = book.size_positions(["A", "B"], {"A": 0.25, "B": 0.25})
        assert pos["A"].target_weight == pytest.approx(0.45)
        assert pos["B"].target_weight == pytest.approx(0.45)


# ══ TargetPortfolio 契约（§2.2.4）══


class TestTargetPortfolioContract:
    def test_build_contract_fields(self) -> None:
        """TargetPortfolio 字段完整 + total_weight ≤ budget + cash_ratio。"""
        book = _make_book(sizing="equal_weight", budget=0.80)
        tp = book.build_target_portfolio({"symbols": ["A", "B", "C"]})
        assert isinstance(tp, TargetPortfolio)
        assert tp.strategy_id == "test_strat"
        assert set(tp.positions) == {"A", "B", "C"}
        assert tp.total_weight <= tp.budget + 1e-9
        assert tp.cash_ratio == pytest.approx(tp.budget - tp.total_weight)
        assert tp.sizing_method == "equal_weight"
        assert tp.idempotency_key

    def test_budget_clip_prorata(self) -> None:
        """总权重超 budget → pro-rata 等比缩放。"""
        book = _make_book(sizing="equal_weight", budget=0.50)
        tp = book.build_target_portfolio({"symbols": ["A", "B"]})
        # 等权 0.25×2=0.5 = budget，不触发缩放
        assert tp.total_weight == pytest.approx(0.50)

    def test_empty_signals_empty_portfolio(self) -> None:
        book = _make_book()
        tp = book.build_target_portfolio({"symbols": []})
        assert tp.positions == {}
        assert tp.total_weight == 0.0
        assert tp.cash_ratio == pytest.approx(tp.budget)


# ══ 回撤 Protocol（30号 §2.5）══


class TestDrawdownProtocol:
    def test_l4_liquidate_empty(self) -> None:
        """回撤 ≥25% → L4 清仓空仓。"""
        book = _make_book()
        pnl = [0.05] * 10 + [-0.30]  # 峰值后 -30%
        tp = book.build_target_portfolio({"symbols": ["A"]}, strategy_pnl_history=pnl)
        assert tp.positions == {}
        assert book.get_drawdown_level().level == 4

    def test_l2_position_scaling(self) -> None:
        """回撤 ≥15% 且 <20% → L2 仓位 ×0.75。"""
        book = _make_book(sizing="equal_weight", budget=0.80)
        # 构造峰值 1.16 → 当前 0.97，回撤约 16%
        pnl = [0.04] * 4 + [-0.16]
        tp = book.build_target_portfolio({"symbols": ["A", "B"]}, strategy_pnl_history=pnl)
        assert book.get_drawdown_level().level == 2
        for tw in tp.positions.values():
            # 等权 0.4 × 0.75 = 0.3
            assert tw.target_weight == pytest.approx(0.40 * 0.75)

    def test_no_drawdown_no_scaling(self) -> None:
        book = _make_book(sizing="equal_weight", budget=0.80)
        tp = book.build_target_portfolio({"symbols": ["A", "B"]}, strategy_pnl_history=[0.01] * 5)
        assert book.get_drawdown_level().level == 0
        for tw in tp.positions.values():
            assert tw.target_weight == pytest.approx(0.40)


# ══ rebalance_to_budget（30号 §2.4）══


class TestRebalanceToBudget:
    def test_budget_down_cuts_least_confident(self) -> None:
        """budget 下调 → 砍最不自信仓位。"""
        book = _make_book(sizing="equal_weight", budget=0.80)
        tp = book.build_target_portfolio({"symbols": ["A", "B"]})
        # 人为设置差异化 confidence
        book._last_target_portfolio = TargetPortfolio(
            strategy_id=tp.strategy_id,
            positions={
                s: type(tp.positions[s])(
                    target_weight=tw.target_weight,
                    reason=tw.reason,
                    confidence=0.9 if s == "A" else 0.2,
                )
                for s, tw in tp.positions.items()
            },
            total_weight=tp.total_weight,
            budget=tp.budget,
            cash_ratio=tp.cash_ratio,
            sizing_method=tp.sizing_method,
        )
        new_tp = book.rebalance_to_budget(0.45)
        # B（confidence 0.2）先被砍：保留 A 0.4，B 部分保留 0.05
        assert new_tp.positions["A"].target_weight == pytest.approx(0.40)
        assert new_tp.positions["B"].target_weight == pytest.approx(0.05)
        assert new_tp.total_weight <= 0.45 + 1e-9

    def test_budget_up_no_forced_buy(self) -> None:
        """budget 上调 → 不强制买入，仅更新 budget 字段。"""
        book = _make_book(sizing="equal_weight", budget=0.50)
        book.build_target_portfolio({"symbols": ["A", "B"]})
        new_tp = book.rebalance_to_budget(0.90)
        assert new_tp.budget == 0.90
        assert new_tp.total_weight == pytest.approx(0.50)  # 仓位不变
        assert new_tp.cash_ratio == pytest.approx(0.40)


# ══ PerformanceScore（30号 §2.2）══


class TestPerformanceScore:
    def test_score_bounds(self) -> None:
        book = _make_book()
        # 稳定盈利 → 高分
        score = book.compute_performance_score([0.01] * 60)
        assert 0.5 <= score <= 1.5
        # 稳定亏损 → floor
        score = book.compute_performance_score([-0.01] * 60)
        assert score == pytest.approx(0.5)

    def test_insufficient_samples_floor(self) -> None:
        book = _make_book()
        assert book.compute_performance_score([0.01]) == pytest.approx(0.5)


# ══ 冷启动状态机（30号 §6.7 三段式 + 31号 §2.4.1）══


class TestColdStartStateMachine:
    """30号 §6.7：×30%→×60%→×100% 按上线天数自动晋升，PerformanceScore 稳定锁定满仓。"""

    def test_no_live_start_date_full_position(self) -> None:
        """未传 live_start_date → 非冷启动模式，恒满仓 1.0（既有策略零行为变化）。"""
        book = _DummyBook("s1")
        state = book.get_cold_start_state()
        assert state.stage == "full_position"
        assert state.ratio == pytest.approx(1.0)
        assert state.days_live is None
        assert state.locked_full is True

    def test_cold_start_stage_ratio_030(self) -> None:
        """上线 <30 天 → cold_start ×0.30。"""
        book = _DummyBook("s1", live_start_date=date(2026, 8, 1))
        state = book.get_cold_start_state(today=date(2026, 8, 20))  # 19 天
        assert state.stage == "cold_start"
        assert state.ratio == pytest.approx(0.30)
        assert state.days_live == 19
        assert state.locked_full is False

    def test_half_position_stage_ratio_060(self) -> None:
        """30≤上线<60 天 → half_position ×0.60。"""
        book = _DummyBook("s1", live_start_date=date(2026, 6, 25))
        state = book.get_cold_start_state(today=date(2026, 8, 20))  # 56 天
        assert state.stage == "half_position"
        assert state.ratio == pytest.approx(0.60)

    def test_full_position_after_60_days(self) -> None:
        """上线 ≥60 天 → full_position ×1.00（毕业）。"""
        book = _DummyBook("s1", live_start_date=date(2026, 6, 1))
        state = book.get_cold_start_state(today=date(2026, 8, 20))  # 80 天
        assert state.stage == "full_position"
        assert state.ratio == pytest.approx(1.0)
        assert state.locked_full is True

    def test_stage_boundary_days(self) -> None:
        """边界：恰好 30 天进半仓，恰好 60 天毕业。"""
        book = _DummyBook("s1", live_start_date=date(2026, 7, 21))
        assert book.get_cold_start_state(today=date(2026, 8, 20)).stage == "half_position"  # 恰好 30 天
        book2 = _DummyBook("s2", live_start_date=date(2026, 6, 21))
        assert book2.get_cold_start_state(today=date(2026, 8, 20)).stage == "full_position"  # 恰好 60 天

    def test_perf_stable_locks_full_early(self) -> None:
        """PerformanceScore 稳定（有效观测≥40）→ 冷启动期提前锁定满仓（§6.7）。"""
        book = _DummyBook("s1", live_start_date=date(2026, 8, 10))  # 仅 10 天
        state = book.get_cold_start_state(today=date(2026, 8, 20), perf_valid_observations=40)
        assert state.stage == "full_position"
        assert state.ratio == pytest.approx(1.0)
        assert state.locked_full is True

    def test_perf_observations_below_threshold_no_lock(self) -> None:
        """有效观测 39 < 40 → 不锁定，仍按天数走冷启动。"""
        book = _DummyBook("s1", live_start_date=date(2026, 8, 10))
        state = book.get_cold_start_state(today=date(2026, 8, 20), perf_valid_observations=39)
        assert state.stage == "cold_start"
        assert state.ratio == pytest.approx(0.30)

    def test_get_cold_start_ratio_convenience(self) -> None:
        """get_cold_start_ratio() 便捷接口与 state.ratio 一致。"""
        book = _DummyBook("s1", live_start_date=date(2026, 8, 1))
        assert book.get_cold_start_ratio(today=date(2026, 8, 20)) == pytest.approx(0.30)


# ══ score→weight 显式转换（30号 §2.2 契约③）══


class TestScoresToWeights:
    """composite_score[-3,3] → 粗仓位权重映射（函数级形式化）。"""

    def test_proportional_basic(self) -> None:
        """proportional：线性平移 s+3 后按比例，Σ=budget。"""
        w = scores_to_weights({"A": 3.0, "B": 0.0, "C": -3.0}, budget=0.9)
        # 平移后 6/3/0 → A=0.6, B=0.3, C=0.0
        assert w["A"] == pytest.approx(0.60)
        assert w["B"] == pytest.approx(0.30)
        assert w["C"] == pytest.approx(0.0)
        assert sum(w.values()) == pytest.approx(0.9)

    def test_equal_method(self) -> None:
        """equal：入选标的等权 budget/N。"""
        w = scores_to_weights({"A": 2.0, "B": 1.0}, budget=0.8, method="equal")
        assert w["A"] == pytest.approx(0.40)
        assert w["B"] == pytest.approx(0.40)

    def test_top_n_selection(self) -> None:
        """top_n：评分降序取前 N。"""
        w = scores_to_weights({"A": 1.0, "B": 2.0, "C": 3.0}, budget=0.9, top_n=2, method="equal")
        assert set(w.keys()) == {"B", "C"}
        assert w["B"] == pytest.approx(0.45)

    def test_top_n_exceeds_len(self) -> None:
        """top_n > 标的数 → 全部入选（边界）。"""
        w = scores_to_weights({"A": 1.0, "B": 1.0}, budget=0.6, top_n=10, method="equal")
        assert len(w) == 2

    def test_empty_scores(self) -> None:
        """空评分 → 空权重（退化）。"""
        assert scores_to_weights({}, budget=0.9) == {}

    def test_all_min_score_fallback_equal(self) -> None:
        """全部评分=-3（平移后全 0）→ 等权兜底（退化路径）。"""
        w = scores_to_weights({"A": -3.0, "B": -3.0}, budget=0.8)
        assert w["A"] == pytest.approx(0.40)
        assert w["B"] == pytest.approx(0.40)

    def test_score_out_of_range_raises(self) -> None:
        """评分越出 [-3,3] 契约区间 → ValueError（21号 §3.3 归一化口径）。"""
        with pytest.raises(ValueError, match="契约区间"):
            scores_to_weights({"A": 3.5}, budget=0.9)
        with pytest.raises(ValueError, match="契约区间"):
            scores_to_weights({"A": -3.2}, budget=0.9)

    def test_invalid_params_raise(self) -> None:
        """budget<0 / top_n≤0 / method 未知 → ValueError。"""
        with pytest.raises(ValueError):
            scores_to_weights({"A": 1.0}, budget=-0.1)
        with pytest.raises(ValueError):
            scores_to_weights({"A": 1.0}, budget=0.9, top_n=0)
        with pytest.raises(ValueError, match="未知"):
            scores_to_weights({"A": 1.0}, budget=0.9, method="softmax")

    def test_negative_scores_keep_small_weight(self) -> None:
        """负分标的在 proportional 下仍得小权重（不剔除），正分标的占主导。"""
        w = scores_to_weights({"A": 2.0, "B": -2.0}, budget=1.0)
        # 平移后 5/1 → A≈0.833, B≈0.167
        assert w["A"] > w["B"] > 0
