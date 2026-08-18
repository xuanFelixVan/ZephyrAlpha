# [A_test] module_id: MOD-PA-006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PA-006 | docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md | §
# [MODULE] tests.pf_alloc.test_batched_position_builder
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""41_buy_flow 施工验证测试。

覆盖：
- 6 算法：compute_batch_split / detect_breakout_failure / schedule_buy_orders /
  compute_anchor_price / clip_to_available_capital / rank_buy_orders
- 2 dataclass：Batch / BatchedEntryPlan
- BatchedPositionBuilder 编排入口
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, time

import pytest

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    DisciplineGuardError,
    KillSwitchLite,
    OrderRequest,
    ProhibitedBehavior,
)
from zephyr.pf_alloc.batched_position_builder import (
    AGGRESSIVE_THRESHOLD,
    DEFAULT_CONFIRM_BARS,
    DEFAULT_LOOKBACK_DAYS,
    QUALITY_ADJUSTMENT,
    Batch,
    BatchedEntryPlan,
    BatchedPositionBuilder,
    clip_to_available_capital,
    compute_anchor_price,
    compute_batch_split,
    detect_breakout_failure,
    rank_buy_orders,
    schedule_buy_orders,
)

# ── 测试用 Mock 对象 ──


@dataclass
class MockPosition:
    """模拟持仓对象。"""

    entry_price: float = 10.0
    low_prices: list[float] = None
    close_prices: list[float] = None

    def __post_init__(self):
        if self.low_prices is None:
            self.low_prices = [9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4]
        if self.close_prices is None:
            self.close_prices = [10.5, 10.6]


@dataclass
class MockBar:
    """模拟分钟 K 线。"""

    close: float
    volume: float


# ══════════════════════════════════════════════════════════════
# 算法 1：compute_batch_split（41 §3.2.1）
# ══════════════════════════════════════════════════════════════


class TestComputeBatchSplit:
    """C-031 置信度→批次比例映射。"""

    def test_high_confidence_aggressive(self):
        """高置信度→激进建仓，首仓≥70%，实质 1 批。"""
        result = compute_batch_split(0.80, "daban")
        assert result["mode"] == "AGGRESSIVE"
        assert result["batches"] == 1
        assert result["first_pct"] >= 0.70
        assert result["confidence_source"] == 0.80

    def test_low_confidence_scaled(self):
        """低置信度→分批建仓，首仓 30-50%，2 批。"""
        result = compute_batch_split(0.50, "multifactor")
        assert result["mode"] == "SCALED"
        assert result["batches"] == 2
        assert 0.30 <= result["first_pct"] <= 0.50

    def test_sector_quality_a_boost(self):
        """A 类板块回踩→置信度+0.1。"""
        result = compute_batch_split(0.60, "multifactor", sector_quality="A")
        assert result["adjusted_confidence"] == pytest.approx(0.70)
        assert result["mode"] == "AGGRESSIVE"

    def test_sector_quality_c_penalty(self):
        """C 类板块回踩→置信度-0.1。"""
        result = compute_batch_split(0.70, "multifactor", sector_quality="C")
        assert result["adjusted_confidence"] == pytest.approx(0.60)
        assert result["mode"] == "SCALED"

    def test_sector_quality_none_degrade(self):
        """sector_quality=None→不调整（降级兼容）。"""
        result = compute_batch_split(0.70, "multifactor", sector_quality=None)
        assert result["adjusted_confidence"] == 0.70
        assert result["sector_quality"] is None

    def test_confidence_clamped(self):
        """置信度调节后 clamp 到 [0, 1]。"""
        result = compute_batch_split(0.95, "daban", sector_quality="A")
        assert result["adjusted_confidence"] <= 1.0
        result = compute_batch_split(0.05, "daban", sector_quality="C")
        assert result["adjusted_confidence"] >= 0.0

    def test_unknown_strategy_default_threshold(self):
        """未知策略类型→默认阈值 0.70。"""
        result = compute_batch_split(0.70, "unknown_strategy")
        assert result["mode"] == "AGGRESSIVE"

    def test_threshold_boundary(self):
        """阈值边界：恰好等于阈值→激进。"""
        result = compute_batch_split(0.75, "daban")
        assert result["mode"] == "AGGRESSIVE"
        result = compute_batch_split(0.749, "daban")
        assert result["mode"] == "SCALED"


# ══════════════════════════════════════════════════════════════
# 算法 2：detect_breakout_failure（41 §3.3）
# ══════════════════════════════════════════════════════════════


class TestDetectBreakoutFailure:
    """突破失败检测。"""

    def test_no_failure(self):
        """未触发降级→返回 None。"""
        pos = MockPosition(entry_price=10.0, close_prices=[10.5, 10.6])
        assert detect_breakout_failure(pos) is None

    def test_breakout_failed(self):
        """连续 2 根收盘 < 入场价→BREAKOUT_FAILED。"""
        pos = MockPosition(entry_price=10.0, close_prices=[9.8, 9.9])
        result = detect_breakout_failure(pos)
        assert result is not None
        assert result[0] == "BREAKOUT_FAILED"
        assert "暂停确认仓" in result[1]
        assert "BM-SELL-01" in result[2]

    def test_support_broken(self):
        """连续 2 根收盘 < 前低→SUPPORT_BROKEN。"""
        pos = MockPosition(
            entry_price=10.0,
            low_prices=[9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9],
            close_prices=[8.9, 8.8],
        )
        result = detect_breakout_failure(pos)
        assert result is not None
        assert result[0] == "SUPPORT_BROKEN"
        assert "暂停全部后续批次" in result[1]
        assert "BM-SELL-04-B" in result[2]

    def test_single_bar_no_trigger(self):
        """单根 K 线跌破不触发（防假跌破）。"""
        pos = MockPosition(entry_price=10.0, close_prices=[9.8, 10.5])
        assert detect_breakout_failure(pos) is None

    def test_custom_confirm_bars(self):
        """自定义 confirm_bars=3。"""
        pos = MockPosition(entry_price=10.0, close_prices=[9.8, 9.9, 9.7])
        assert detect_breakout_failure(pos, confirm_bars=3) is not None
        assert detect_breakout_failure(pos, confirm_bars=2) is not None

    def test_empty_data_no_misjudgment(self):
        """空数据门禁（AI-R2 红队 ATK-7）：无观测证据 → 不降级（无罪推定）。

        原实现：low_prices 空 → min([]) 崩溃；close_prices 空 → all([])=True
        误触发 SUPPORT_BROKEN 止损卖出（数据缺口被当成有罪证据）。
        """
        # 全空：原 min([]) ValueError 崩溃
        assert detect_breakout_failure(MockPosition(low_prices=[], close_prices=[])) is None
        # 收盘空：原 all([])=True → 误 SUPPORT_BROKEN
        assert detect_breakout_failure(MockPosition(close_prices=[])) is None
        # 前低空
        assert detect_breakout_failure(MockPosition(low_prices=[], close_prices=[8.0, 8.1])) is None

    def test_insufficient_closes_no_trigger(self):
        """收盘样本不足 confirm_bars 根 → 证据不足不判定（防 1 根假跌破即止损）。"""
        pos = MockPosition(entry_price=10.0, close_prices=[8.0])  # 1 根深跌破
        assert detect_breakout_failure(pos, confirm_bars=2) is None


# ══════════════════════════════════════════════════════════════
# 算法 3：schedule_buy_orders（41 §3.4）
# ══════════════════════════════════════════════════════════════


class TestScheduleBuyOrders:
    """买入时序调度。"""

    def _make_plan(self) -> BatchedEntryPlan:
        return BatchedEntryPlan(
            symbol="600519",
            total_weight=0.08,
            batches=[Batch(batch_id=1, weight_fraction=1.0, trigger_conditions=[])],
            confidence_tier="AGGRESSIVE",
        )

    def test_before_window(self):
        """14:50 前→WAIT。"""
        plan = self._make_plan()
        action, msg = schedule_buy_orders(plan, time(14, 30))
        assert action == "WAIT"

    def test_place_limit_window(self):
        """14:50-14:55→PLACE_LIMIT。"""
        plan = self._make_plan()
        action, msg = schedule_buy_orders(plan, time(14, 52))
        assert action == "PLACE_LIMIT"

    def test_check_and_amend_window(self):
        """14:55-14:57→CHECK_AND_AMEND。"""
        plan = self._make_plan()
        action, msg = schedule_buy_orders(plan, time(14, 56))
        assert action == "CHECK_AND_AMEND"

    def test_closing_auction_window(self):
        """14:57-15:00→CLOSING_AUCTION_ONLY。"""
        plan = self._make_plan()
        action, msg = schedule_buy_orders(plan, time(14, 58))
        assert action == "CLOSING_AUCTION_ONLY"

    def test_after_hours(self):
        """15:00 后→AFTER_HOURS。"""
        plan = self._make_plan()
        action, msg = schedule_buy_orders(plan, time(15, 10))
        assert action == "AFTER_HOURS"

    def test_boundary_1450(self):
        """14:50 边界→PLACE_LIMIT。"""
        plan = self._make_plan()
        action, _ = schedule_buy_orders(plan, time(14, 50))
        assert action == "PLACE_LIMIT"

    def test_boundary_1457(self):
        """14:57 边界→CLOSING_AUCTION_ONLY。"""
        plan = self._make_plan()
        action, _ = schedule_buy_orders(plan, time(14, 57))
        assert action == "CLOSING_AUCTION_ONLY"


# ══════════════════════════════════════════════════════════════
# 算法 4：compute_anchor_price（41 §3.5）
# ══════════════════════════════════════════════════════════════


class TestComputeAnchorPrice:
    """买入限价锚定价格计算。"""

    def _make_bars(self) -> list[MockBar]:
        return [
            MockBar(close=10.0, volume=1000),
            MockBar(close=10.1, volume=2000),
            MockBar(close=10.2, volume=1500),
        ]

    def test_breakout_anchor(self):
        """突破买入→锚压力位×[0.99, 1.00]。"""
        bars = self._make_bars()
        price = compute_anchor_price("600519", "BREAKOUT", 10.0, bars, time(14, 50))
        assert 9.90 <= price <= 10.00

    def test_pullback_anchor(self):
        """回踩买入→锚支撑位×[1.00, 1.01]。"""
        bars = self._make_bars()
        price = compute_anchor_price("600519", "PULLBACK", 10.0, bars, time(14, 50))
        assert 10.00 <= price <= 10.10

    def test_fallback_vwap(self):
        """通用兜底→min(目标价, VWAP)。"""
        bars = self._make_bars()
        price = compute_anchor_price("600519", "FALLBACK", 10.5, bars, time(14, 50))
        # VWAP = (10.0*1000 + 10.1*2000 + 10.2*1500) / (1000+2000+1500)
        vwap = (10.0 * 1000 + 10.1 * 2000 + 10.2 * 1500) / 4500
        assert price == min(10.5, vwap)

    def test_empty_bars_fallback(self):
        """无 K 线数据→VWAP=level_price。"""
        price = compute_anchor_price("600519", "FALLBACK", 10.0, [], time(14, 50))
        assert price == 10.0

    def test_zero_volume_fallback(self):
        """成交量为 0→VWAP=level_price。"""
        bars = [MockBar(close=10.0, volume=0)]
        price = compute_anchor_price("600519", "FALLBACK", 10.0, bars, time(14, 50))
        assert price == 10.0


# ══════════════════════════════════════════════════════════════
# 算法 5：clip_to_available_capital（41 §3.6）
# ══════════════════════════════════════════════════════════════


class TestClipToAvailableCapital:
    """资金不足 pro-rata 削减。"""

    def test_sufficient_capital(self):
        """资金充足→原样执行。"""
        holdings = {"600519": 0.08, "000858": 0.06, "CASH": 0.86}
        result = clip_to_available_capital(holdings, 100000, 100000)
        assert result == holdings

    def test_insufficient_capital(self):
        """资金不足→pro-rata 削减。"""
        holdings = {"600519": 0.40, "000858": 0.40, "CASH": 0.20}
        result = clip_to_available_capital(holdings, 40000, 100000)
        # target_invest = 0.80 * 100000 = 80000 > 40000
        # scale = 40000/80000 = 0.5
        assert result["600519"] == pytest.approx(0.20)
        assert result["000858"] == pytest.approx(0.20)
        assert result["CASH"] == pytest.approx(0.60)
        assert "_degrade_reason" in result

    def test_cash_key_preserved(self):
        """CASH 键始终存在。"""
        holdings = {"600519": 0.50, "CASH": 0.50}
        result = clip_to_available_capital(holdings, 30000, 100000)
        assert "CASH" in result
        assert abs(sum(v for k, v in result.items() if not k.startswith("_")) - 1.0) < 1e-9

    def test_all_cash(self):
        """全 CASH→不变。"""
        holdings = {"CASH": 1.0}
        result = clip_to_available_capital(holdings, 100000, 100000)
        assert result == holdings


# ══════════════════════════════════════════════════════════════
# 算法 6：rank_buy_orders（41 §3.6）
# ══════════════════════════════════════════════════════════════


class TestRankBuyOrders:
    """多标的下单排序。"""

    def test_liquidity_first(self):
        """流动性差→先挂。"""
        holdings = {"A": 0.05, "B": 0.05, "CASH": 0.90}
        confidence = {"A": 0.8, "B": 0.8}
        liquidity = {"A": 0.3, "B": 0.7}  # A 流动性差
        result = rank_buy_orders(holdings, confidence, liquidity)
        assert result[0] == "A"

    def test_confidence_second(self):
        """同流动性→高置信度先挂。"""
        holdings = {"A": 0.05, "B": 0.05, "CASH": 0.90}
        confidence = {"A": 0.9, "B": 0.7}
        liquidity = {"A": 0.5, "B": 0.5}
        result = rank_buy_orders(holdings, confidence, liquidity)
        assert result[0] == "A"

    def test_weight_third(self):
        """同流动性同置信度→大仓先挂。"""
        holdings = {"A": 0.08, "B": 0.05, "CASH": 0.87}
        confidence = {"A": 0.8, "B": 0.8}
        liquidity = {"A": 0.5, "B": 0.5}
        result = rank_buy_orders(holdings, confidence, liquidity)
        assert result[0] == "A"

    def test_cash_excluded(self):
        """CASH 不参与排序。"""
        holdings = {"A": 0.05, "CASH": 0.95}
        confidence = {"A": 0.8}
        liquidity = {"A": 0.5}
        result = rank_buy_orders(holdings, confidence, liquidity)
        assert "CASH" not in result

    def test_composite_ordering(self):
        """综合排序：流动性差+高置信度+大仓→最先。"""
        holdings = {"A": 0.08, "B": 0.06, "C": 0.04, "CASH": 0.82}
        confidence = {"A": 0.9, "B": 0.7, "C": 0.8}
        liquidity = {"A": 0.2, "B": 0.8, "C": 0.5}
        result = rank_buy_orders(holdings, confidence, liquidity)
        # A 流动性最差(0.2)→最先; C 次之(0.5); B 最好(0.8)→最后
        assert result == ["A", "C", "B"]


# ══════════════════════════════════════════════════════════════
# Dataclass 契约验证
# ══════════════════════════════════════════════════════════════


class TestDataclassContracts:
    """Batch / BatchedEntryPlan 契约。"""

    def test_batch_fields(self):
        """Batch 字段完整。"""
        batch = Batch(batch_id=1, weight_fraction=0.4, trigger_conditions=["cond1"])
        assert batch.batch_id == 1
        assert batch.weight_fraction == 0.4
        assert batch.status == "PENDING"

    def test_batched_entry_plan_fields(self):
        """BatchedEntryPlan 字段完整。"""
        plan = BatchedEntryPlan(
            symbol="600519",
            total_weight=0.08,
            batches=[Batch(batch_id=1, weight_fraction=1.0, trigger_conditions=[])],
            confidence_tier="AGGRESSIVE",
        )
        assert plan.symbol == "600519"
        assert plan.total_weight == 0.08
        assert len(plan.batches) == 1
        assert plan.degrade_reason is None

    def test_batched_entry_plan_degrade(self):
        """BatchedEntryPlan 降级标记。"""
        plan = BatchedEntryPlan(
            symbol="600519",
            total_weight=0.08,
            batches=[],
            confidence_tier="SCALED",
            degrade_reason="sector_quality=None",
        )
        assert plan.degrade_reason is not None


# ══════════════════════════════════════════════════════════════
# BatchedPositionBuilder 编排入口
# ══════════════════════════════════════════════════════════════


class TestBatchedPositionBuilder:
    """编排入口。"""

    def test_build_plan_aggressive(self):
        """高置信度→激进 1 批。"""
        builder = BatchedPositionBuilder()
        plan = builder.build_plan("600519", 0.08, 0.80, "daban")
        assert plan.confidence_tier == "AGGRESSIVE"
        assert len(plan.batches) == 1

    def test_build_plan_scaled(self):
        """低置信度→分批 2 批。"""
        builder = BatchedPositionBuilder()
        plan = builder.build_plan("600519", 0.08, 0.50, "multifactor")
        assert plan.confidence_tier == "SCALED"
        assert len(plan.batches) == 2
        assert plan.batches[0].weight_fraction + plan.batches[1].weight_fraction == pytest.approx(1.0)

    def test_build_plan_degrade_reason(self):
        """sector_quality=None→degrade_reason 标记。"""
        builder = BatchedPositionBuilder()
        plan = builder.build_plan("600519", 0.08, 0.50, "multifactor", sector_quality=None)
        assert plan.degrade_reason is not None

    def test_check_batch2_release(self):
        """2/3 条件放行检查。"""
        builder = BatchedPositionBuilder()
        plan = builder.build_plan("600519", 0.08, 0.50, "multifactor")
        pos = MockPosition(entry_price=10.0, close_prices=[10.5, 10.6])
        # ① 距首仓≥1交易日 ✅ + ② 不破入场价 ✅ + ③ 量比<1 ✅ → 3/3 放行
        assert builder.check_batch2_release(plan, pos, volume_ratio=0.8, days_since_first_batch=1)
        # ① ✅ + ② ✅ + ③ ❌ → 2/3 放行
        assert builder.check_batch2_release(plan, pos, volume_ratio=1.5, days_since_first_batch=1)
        # ① ❌ + ② ✅ + ③ ✅ → 2/3 放行
        assert builder.check_batch2_release(plan, pos, volume_ratio=0.8, days_since_first_batch=0)
        # ① ❌ + ② ❌ + ③ ✅ → 1/3 不放行
        pos_below = MockPosition(entry_price=10.0, close_prices=[9.8, 9.9])
        assert not builder.check_batch2_release(plan, pos_below, volume_ratio=0.8, days_since_first_batch=0)

    def test_check_degrade(self):
        """突破失败降级检查。"""
        builder = BatchedPositionBuilder()
        pos = MockPosition(entry_price=10.0, close_prices=[9.8, 9.9])
        result = builder.check_degrade(pos)
        assert result is not None
        assert result[0] == "BREAKOUT_FAILED"


# ══════════════════════════════════════════════════════════════
# BM-BUY-08 纪律闸接线（41 §2.3/§3.1，AI-ASM-001 装配批，43 号 §4.3）
# ══════════════════════════════════════════════════════════════


def _tmp_logger(tmp_path) -> ComplianceLogger:
    """测试用合规日志（写 tmp，不污染生产证据链）。"""
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


def _order(**overrides) -> OrderRequest:
    base = {
        "symbol": "600519.SH",
        "price": 100.0,
        "strategy_id": "daban_v1",
        "risk_exposure": 0.03,
        "size": 30000.0,
        "is_add": False,
    }
    base.update(overrides)
    return OrderRequest(**base)


def _ctx(**overrides) -> DisciplineContext:
    """全中性 ctx（默认不触发任何检测）。"""
    base = {
        "signal_ref_price": None,
        "surge_30min_pct": None,
        "position_pnl_pct": None,
        "win_streak": 0,
        "normal_exposure": 0.01,
        "daily_pnl_pct": 0.0,
        "projected_daily_freq": 1.0,
        "freq_baseline_20d": 1.0,
        "size_baseline_20d": 1e9,
    }
    base.update(overrides)
    return DisciplineContext(**base)


class TestGateBatchOrder:
    """每批下单前过 BM-BUY-08 纪律闸（41 §2.3 硬约束，buy_flow 不得绕过）。"""

    def test_no_guard_raises_fail_closed(self):
        """纪律闸未注入 → DisciplineGuardError（Fail-Closed：闸不可用即拒）。"""
        builder = BatchedPositionBuilder()
        with pytest.raises(DisciplineGuardError, match="不得绕过"):
            builder.gate_batch_order(_order(), _ctx())

    def test_pass_verdict(self, tmp_path):
        """全中性 → PASS 放行。"""
        builder = BatchedPositionBuilder(
            discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path))
        )
        verdict = builder.gate_batch_order(_order(), _ctx())
        assert verdict.action is DisciplineAction.PASS

    def test_chasing_hard_block(self, tmp_path):
        """追高命中 → HARD_BLOCK（取消该批及后续批次，41 §3.3 降级表）。"""
        builder = BatchedPositionBuilder(
            discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path))
        )
        verdict = builder.gate_batch_order(
            _order(price=100.0),
            _ctx(signal_ref_price=95.0, surge_30min_pct=0.06),
        )
        assert verdict.action is DisciplineAction.HARD_BLOCK
        assert verdict.behavior is ProhibitedBehavior.CHASING

    def test_overconfidence_warning_not_block(self, tmp_path):
        """盈利骄傲 → WARNING 不阻断。"""
        builder = BatchedPositionBuilder(
            discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path))
        )
        verdict = builder.gate_batch_order(
            _order(risk_exposure=0.03),
            _ctx(win_streak=5, normal_exposure=0.01),
        )
        assert verdict.action is DisciplineAction.WARNING

    def test_kill_switch_blocks_strategy(self, tmp_path):
        """KillSwitchLite 熔断策略当日禁止新开仓（43 号 §4.3）。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_tmp_logger(tmp_path),
        )
        assert ks.trigger("daban_v1", "REVENGE_TRADING", date.today())
        builder = BatchedPositionBuilder(
            discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path)),
            kill_switch=ks,
        )
        verdict = builder.gate_batch_order(_order(), _ctx(), today=date.today())
        assert verdict.action is DisciplineAction.HARD_BLOCK
        assert verdict.kill_switch_triggered

    def test_kill_switch_other_strategy_pass(self, tmp_path):
        """熔断仅策略级——其他策略正常过闸。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_tmp_logger(tmp_path),
        )
        assert ks.trigger("other_strategy", "REVENGE_TRADING", date.today())
        builder = BatchedPositionBuilder(
            discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path)),
            kill_switch=ks,
        )
        verdict = builder.gate_batch_order(_order(), _ctx(), today=date.today())
        assert verdict.action is DisciplineAction.PASS

    def test_revenge_triggers_kill_switch_via_guard(self, tmp_path):
        """报复交易命中：HARD_BLOCK + KillSwitchLite 经 DisciplineGuard 联动触发。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_tmp_logger(tmp_path),
        )
        guard = DisciplineGuard(kill_switch=ks, logger=_tmp_logger(tmp_path))
        builder = BatchedPositionBuilder(discipline_guard=guard, kill_switch=ks)
        verdict = builder.gate_batch_order(
            _order(size=200.0),
            _ctx(daily_pnl_pct=-0.03, size_baseline_20d=100.0),
            today=date.today(),
        )
        assert verdict.action is DisciplineAction.HARD_BLOCK
        assert verdict.behavior is ProhibitedBehavior.REVENGE_TRADING
        # 熔断状态已落盘——同策略下一批直接被熔断闸拦截
        assert ks.is_blocked("daban_v1", date.today())
        verdict2 = builder.gate_batch_order(_order(), _ctx(), today=date.today())
        assert verdict2.action is DisciplineAction.HARD_BLOCK
        assert verdict2.kill_switch_triggered


# ══════════════════════════════════════════════════════════════
# 红队修复守卫（AI-R2-001）
# ══════════════════════════════════════════════════════════════


class TestClipCapitalGuard:
    """clip_to_available_capital 非法 available_cash 入口校验（负/NaN/Inf→按零资金降级）。"""

    def _holdings(self) -> dict[str, float]:
        return {"600519": 0.40, "000858": 0.40, "CASH": 0.20}

    def test_negative_cash_zero_degrade(self):
        """available_cash=-100 → 按零资金降级，不产生负权重（不变相做空）。"""
        result = clip_to_available_capital(self._holdings(), -100.0, 100000)
        assert result["600519"] == pytest.approx(0.0)
        assert result["000858"] == pytest.approx(0.0)
        assert result["CASH"] == pytest.approx(1.0)
        assert all(w >= 0 for k, w in result.items() if not k.startswith("_"))
        assert "_degrade_reason" in result

    def test_nan_cash_zero_degrade(self):
        """available_cash=NaN → 按零资金降级，输出无 NaN 污染。"""
        result = clip_to_available_capital(self._holdings(), float("nan"), 100000)
        assert result["600519"] == pytest.approx(0.0)
        assert result["CASH"] == pytest.approx(1.0)
        assert all(
            math.isfinite(w) for k, w in result.items() if not k.startswith("_")
        )
        assert "_degrade_reason" in result

    def test_inf_cash_zero_degrade(self):
        """available_cash=+Inf → 按零资金降级（Inf 资金视为非法输入）。"""
        result = clip_to_available_capital(self._holdings(), float("inf"), 100000)
        assert result["600519"] == pytest.approx(0.0)
        assert result["CASH"] == pytest.approx(1.0)
        assert all(
            math.isfinite(w) for k, w in result.items() if not k.startswith("_")
        )
        assert "_degrade_reason" in result

    def test_zero_cash_zero_degrade(self):
        """available_cash=0 → scale=0 全削，权重和非负且=1.0。"""
        result = clip_to_available_capital(self._holdings(), 0.0, 100000)
        assert result["600519"] == pytest.approx(0.0)
        assert result["CASH"] == pytest.approx(1.0)
        assert abs(sum(v for k, v in result.items() if not k.startswith("_")) - 1.0) < 1e-9


class TestBatch2ReleaseGuard:
    """check_batch2_release 条件②空证据不计票（Fail-Closed，防空集真空值白送 1 票）。"""

    def _scaled_plan(self) -> BatchedEntryPlan:
        return BatchedPositionBuilder().build_plan("600519", 0.08, 0.50, "multifactor")

    def test_empty_close_prices_not_released(self):
        """close_prices=[] 零价格证据 → 条件②不计票，确认仓不放行。"""
        builder = BatchedPositionBuilder()
        plan = self._scaled_plan()
        pos = MockPosition(entry_price=10.0, close_prices=[])
        # ① ✅(days=1) + ② 无证据不计票 + ③ ❌(量比1.5) → 1/3 不放行
        assert not builder.check_batch2_release(plan, pos, volume_ratio=1.5, days_since_first_batch=1)

    def test_single_close_price_not_counted(self):
        """仅 1 根收盘价证据不足 → 条件②不计票，确认仓不放行。"""
        builder = BatchedPositionBuilder()
        plan = self._scaled_plan()
        pos = MockPosition(entry_price=10.0, close_prices=[10.5])
        # ① ✅ + ② 证据不足 + ③ ❌ → 1/3 不放行
        assert not builder.check_batch2_release(plan, pos, volume_ratio=1.5, days_since_first_batch=1)


class TestConfidenceNanGuard:
    """confidence=NaN 入口归零，保住批次比例和=1.0 不变量。"""

    def test_nan_confidence_treated_as_zero(self):
        """NaN 置信度 → 按 0.0 走 SCALED 分支，first_pct 有限且=0.30。"""
        result = compute_batch_split(float("nan"), "multifactor")
        assert result["mode"] == "SCALED"
        assert result["adjusted_confidence"] == 0.0
        assert math.isfinite(result["first_pct"])
        assert result["first_pct"] == pytest.approx(0.30)
        # 批次比例和不变量：2 批比例和=1.0
        assert result["first_pct"] + (1.0 - result["first_pct"]) == pytest.approx(1.0)

    def test_nan_confidence_batch_invariant(self):
        """NaN 置信度经 build_plan 后批次比例和仍=1.0（不污染不变量）。"""
        builder = BatchedPositionBuilder()
        plan = builder.build_plan("600519", 0.08, float("nan"), "multifactor")
        assert plan.confidence_tier == "SCALED"
        assert all(math.isfinite(b.weight_fraction) for b in plan.batches)
        assert sum(b.weight_fraction for b in plan.batches) == pytest.approx(1.0)
