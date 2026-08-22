"""BoundaryRevisionEngine (MOD-PLAN-006) 施工验证测试（92号清单 §8.3 / 44号 §3 M2 + §9.5）。

覆盖：
- 七降档触发逐一（情绪+宽度/失真 spread/大幅回撤数/IM 贴水急扩/板块 5 状态/虹吸共振/BS-005）
- 升档：三条件全满足→进攻档；缺一不满足→不修正
- 防抖：持续 14min 不触发 / 15min 触发 / 信号中断计时清零
- 冷却：当日第 2 次降档拒发
- 档位映射数值：保守 ×0.5+禁加仓下移 0.5×ATR（2026-08-22 裁定）/ 正常 ×1.0 / 进攻 ×1.2
- 跨日 expired：is_effective_on / with_expired / apply_revision 跨日拒发
- 留痕：plan_revision 事件落 prediction_log（tmp 库注入）
- 全触发源缺失=不修正；输入非法 fail-closed
- 既有文件消费接口：TomorrowBoundary.apply_revision / ClosingSessionDecision 经修正边界
"""

from __future__ import annotations

import datetime
import json

import pytest

from zephyr.plan_engine.boundary_revision_engine import (
    TRIGGER_BS005_SHOCK,
    TRIGGER_DISTORTION_SPREAD,
    TRIGGER_DRAWDOWN_COUNT,
    TRIGGER_IM_BASIS_DISCOUNT,
    TRIGGER_SECTOR_TOP_RISK,
    TRIGGER_SENTIMENT_BREADTH,
    TRIGGER_SIPHON_CHAOS,
    BoundaryRevisionError,
    InMemoryJsonStateStore,
    evaluate_boundary_revision,
)
from zephyr.plan_engine.closing_session_decision import ClosingSessionDecision
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary
from zephyr.reporting.prediction_log_writer import ensure_prediction_log_table, query_predictions
from zephyr.signal_ashare.futures_basis_monitor import FuturesBasisSnapshot, FuturesBasisSymbol
from zephyr.signal_ashare.market_sentiment_analyzer import (
    BreadthAccelerationResult,
    DistortionDetectionResult,
    DrawdownRiskResult,
    MarketSentimentResult,
    VolumeForecastResult,
)
from zephyr.signal_ashare.sector_divergence import SectorDivergenceResult

DATE = "2026-08-21"  # 周五
NEXT_DATE = "2026-08-24"  # 下周一（跨日）


# ══════════════════════════════════════════════════════════════
# 触发源构造（真实 dataclass，缺省=全不激活的中性输入）
# ══════════════════════════════════════════════════════════════


def _sentiment(score: float = 50.0, lu_net: float = 1.0, drawdown_count: int = 0) -> MarketSentimentResult:
    return MarketSentimentResult(
        timestamp=datetime.datetime(2026, 8, 21, 14, 0),
        breadth_status="均衡",
        breadth_score=50.0,
        limit_zeal_status="正常",
        limit_score=50.0,
        profit_effect_status="中",
        profit_effect_score=50.0,
        next_day_risk_status="中风险",
        next_day_risk_score=50.0,
        morale_status="正常",
        morale_score=50.0,
        seal_rate_status="中",
        seal_rate=0.6,
        yesterday_lu_status="中",
        overall_score=score,
        sentiment_phase="主升",
        breadth_acceleration=BreadthAccelerationResult(
            breadth_vel_5m=None, breadth_acc_15m=None, lu_net_rate_5m=lu_net, break_rate_5m=None
        ),
        drawdown_risk=DrawdownRiskResult(
            drawdown_count=drawdown_count, max_drawdown_pct=11.0, chase_buried_warning=drawdown_count >= 7
        ),
    )


def _distortion(flag: bool = False, z: float = 1.0) -> DistortionDetectionResult:
    return DistortionDetectionResult(
        guard_ratio=None,
        guard_illusion=False,
        spread_current=0.01,
        spread_zscore=z,
        spread_widening_30m=True,
        weight_cover=False,
        distortion_flag=flag,
        distortion_score=0.0 if flag else 100.0,
    )


def _futures(vel: float = -0.001, sigma: float = 0.01, degraded: bool = False) -> FuturesBasisSnapshot:
    sym = FuturesBasisSymbol(
        product="IM",
        spot_name="中证1000",
        basis_rate=-0.01,
        basis_vel_30m=vel,
        vel_source="intraday_30m",
        discount_alert=False,
        confirm_flag=True,
        signal_weight=1.0,
        futures_price=7000.0,
        spot_price=7010.0,
        futures_leg="futures_kline_qmt",
        spot_leg="index_quote_intraday",
        sigma_20d=sigma,
        position_surge_pct=None,
        sensitivity="中小盘",
        degraded=False,
    )
    return FuturesBasisSnapshot(
        ts=f"{DATE} 14:00:00", trade_date=DATE, per_symbol={"IM": sym}, degraded=degraded
    )


def _sector(
    state: str = "NEUTRAL_MIXED",
    z: float = 1.0,
    vp: float = 0.5,
    rs: float | None = None,
    degraded: bool = False,
) -> SectorDivergenceResult:
    return SectorDivergenceResult(
        date=DATE,
        rotation_state=state,
        top_risk_flag=state in ("CONSENSUS_CLIMAX", "DISTRIBUTION_RISK"),
        siphon_z=z,
        velocity_percentile=vp,
        rs_ratio=rs,
        degraded=degraded,
    )


def _volume(ratio: float = 1.0) -> VolumeForecastResult:
    return VolumeForecastResult(
        predicted_full_volume=9000.0 * ratio, volume_ratio=ratio, shrink_warning=False, volume_confirm=False
    )


def _eval(store: InMemoryJsonStateStore, slot: str = "14:00", time: str | None = None, **kw):
    """共享 state_store 的评估调用（防抖/冷却跨调用累积）。"""
    return evaluate_boundary_revision(DATE, slot, state_store=store, eval_time=time, **kw)


def _confirmed_downgrade(store: InMemoryJsonStateStore, **kw):
    """14:00 首现（防抖未生效）→ 14:45 确认（生效）两段式，返回 (rev1, rev2)。"""
    rev1 = _eval(store, slot="14:00", **kw)
    rev2 = _eval(store, slot="14:45", **kw)
    return rev1, rev2


def _assert_conservative(rev, trigger_key: str) -> None:
    assert rev.revision_applied is True
    assert rev.direction == "DOWNGRADE"
    assert rev.revised_tier == "CONSERVATIVE"
    assert rev.position_cap_scale == pytest.approx(0.5)
    assert rev.no_add_price_shift == pytest.approx(-0.5)  # 2026-08-22 裁定：保守=下移（更严）
    assert rev.triggers == [trigger_key]
    assert rev.debounce_proof[trigger_key]["confirmed"] is True
    json.dumps(rev.to_dict())  # JSON 可序列化契约


# ══════════════════════════════════════════════════════════════
# 七降档触发逐一（44号 §9.5：任一满足→降档）
# ══════════════════════════════════════════════════════════════


class TestDowngradeTriggers:
    """七降档触发源逐一验证（首现防抖未生效→15min 后确认生效）。"""

    def test_sentiment_breadth(self):
        """①综合情绪分<35 且 lu_net_rate<0（30m 未落地以 5m 口径代理）。"""
        rev1, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), sentiment=_sentiment(score=30.0, lu_net=-2.0))
        assert rev1.revision_applied is False  # 防抖未生效
        assert TRIGGER_SENTIMENT_BREADTH in rev1.pending_triggers
        _assert_conservative(rev2, TRIGGER_SENTIMENT_BREADTH)
        assert rev2.trace["trigger_details"][TRIGGER_SENTIMENT_BREADTH]["rate_proxy_5m"] is True

    def test_distortion_spread(self):
        """②distortion_flag 且 spread>2σ。"""
        rev1, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), distortion=_distortion(flag=True, z=2.5))
        assert rev1.revision_applied is False
        _assert_conservative(rev2, TRIGGER_DISTORTION_SPREAD)

    def test_drawdown_count(self):
        """③大幅回撤数≥7。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), sentiment=_sentiment(drawdown_count=8))
        _assert_conservative(rev2, TRIGGER_DRAWDOWN_COUNT)

    def test_im_basis_discount(self):
        """④IM 基差贴水 30min 急扩>1.5σ。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), futures_basis=_futures(vel=-0.02, sigma=0.01))
        _assert_conservative(rev2, TRIGGER_IM_BASIS_DISCOUNT)

    def test_sector_top_risk(self):
        """⑤板块 5 状态=CONSENSUS_CLIMAX/DISTRIBUTION_RISK。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), sector_divergence=_sector(state="CONSENSUS_CLIMAX"))
        _assert_conservative(rev2, TRIGGER_SECTOR_TOP_RISK)

    def test_siphon_chaos(self):
        """⑥虹吸态 z>1.5σ 且 电风扇速度计>75 分位（共振）。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), sector_divergence=_sector(z=2.0, vp=0.80))
        _assert_conservative(rev2, TRIGGER_SIPHON_CHAOS)

    def test_bs005_shock(self):
        """⑦BS-005 外围冲击盘中触发。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), bs005_triggered=True)
        _assert_conservative(rev2, TRIGGER_BS005_SHOCK)


# ══════════════════════════════════════════════════════════════
# 升档（全部满足→进攻档；缺一→不修正）
# ══════════════════════════════════════════════════════════════


class TestUpgrade:
    """升档三条件（44号 §9.5：全部满足）。"""

    def test_upgrade_all_legs_satisfied(self):
        """情绪>65 且 ŷ_full≥1.1×20日均量 且 rs_ratio>0 → 进攻档 ×1.2。"""
        store = InMemoryJsonStateStore()
        kw = dict(sentiment=_sentiment(score=70.0), volume_forecast=_volume(1.2), rs_ratio=0.5)
        rev1, rev2 = _confirmed_downgrade(store, **kw)  # 两段式同名复用（升档同防抖）
        assert rev1.revision_applied is False
        assert rev2.revision_applied is True
        assert rev2.direction == "UPGRADE"
        assert rev2.revised_tier == "AGGRESSIVE"
        assert rev2.position_cap_scale == pytest.approx(1.2)
        assert rev2.no_add_price_shift == pytest.approx(0.0)

    @pytest.mark.parametrize(
        "kw",
        [
            dict(sentiment=_sentiment(score=60.0), volume_forecast=_volume(1.2), rs_ratio=0.5),  # 情绪不足
            dict(sentiment=_sentiment(score=70.0), volume_forecast=_volume(1.0), rs_ratio=0.5),  # 量能不足
            dict(sentiment=_sentiment(score=70.0), volume_forecast=_volume(1.2), rs_ratio=0.0),  # rs 非正
            dict(sentiment=_sentiment(score=70.0), volume_forecast=_volume(1.2)),  # rs 缺失
        ],
        ids=["score_le_65", "volume_lt_1.1", "rs_not_positive", "rs_missing"],
    )
    def test_upgrade_missing_one_leg_no_revision(self, kw):
        """缺一不满足→不修正（15min 防抖通过后仍不改档）。"""
        _, rev2 = _confirmed_downgrade(InMemoryJsonStateStore(), **kw)
        assert rev2.revision_applied is False
        assert rev2.revised_tier == "NORMAL"
        assert rev2.position_cap_scale == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════
# 防抖（持续≥15min 才生效；中断清零）
# ══════════════════════════════════════════════════════════════


class TestDebounce:
    """防抖规则（44号 §9.5：防单分钟毛刺）。"""

    def test_14min_pending_15min_confirmed(self):
        """14min 不触发 / 15min 触发。"""
        store = InMemoryJsonStateStore()
        kw = dict(bs005_triggered=True)
        rev0 = _eval(store, slot="14:00", time="14:00", **kw)
        rev14 = _eval(store, slot="14:00", time="14:14", **kw)
        rev15 = _eval(store, slot="14:00", time="14:15", **kw)
        assert rev0.revision_applied is False
        assert rev14.revision_applied is False
        assert rev14.debounce_proof[TRIGGER_BS005_SHOCK]["elapsed_min"] == 14
        assert rev14.debounce_proof[TRIGGER_BS005_SHOCK]["confirmed"] is False
        assert rev15.revision_applied is True
        assert rev15.debounce_proof[TRIGGER_BS005_SHOCK]["elapsed_min"] == 15
        assert rev15.debounce_proof[TRIGGER_BS005_SHOCK]["confirmed"] is True

    def test_signal_interrupt_resets_timer(self):
        """信号中断→防抖计时清零（再现后重新计时，不累计）。"""
        store = InMemoryJsonStateStore()
        _eval(store, slot="14:00", time="14:00", bs005_triggered=True)  # 首现
        rev_off = _eval(store, slot="14:00", time="14:10", bs005_triggered=False)  # 中断
        assert any("计时清零" in r for r in rev_off.reasons)
        rev_back = _eval(store, slot="14:00", time="14:25", bs005_triggered=True)  # 再现
        assert rev_back.revision_applied is False  # 重新计时 0min，非累计 25min
        assert rev_back.debounce_proof[TRIGGER_BS005_SHOCK]["elapsed_min"] == 0


# ══════════════════════════════════════════════════════════════
# 冷却（升/降档当日各最多 1 次）
# ══════════════════════════════════════════════════════════════


class TestCooldown:
    """冷却规则（44号 §9.5）。"""

    def test_second_downgrade_rejected_same_day(self):
        """当日第 2 次降档确认→冷却拒发（档位保持保守，不重复改档）。"""
        store = InMemoryJsonStateStore()
        kw = dict(bs005_triggered=True)
        _eval(store, slot="14:00", **kw)  # 首现
        rev2 = _eval(store, slot="14:45", **kw)  # 确认→降档生效（当日 1 次用完）
        assert rev2.revision_applied is True
        rev3 = _eval(store, slot="14:45", time="14:50", **kw)  # 再次确认→冷却拒发
        assert rev3.revision_applied is False
        assert rev3.direction == "NONE"
        assert rev3.original_tier == "CONSERVATIVE"  # 滚动档位：前次修正后
        assert rev3.revised_tier == "CONSERVATIVE"
        assert rev3.triggers == [TRIGGER_BS005_SHOCK]  # 确认事实留痕（含被拒发）
        assert rev3.cooldown["downgrades_used"] == 1
        assert any("冷却" in r and "拒发" in r for r in rev3.reasons)

    def test_new_day_cooldown_resets(self):
        """次日命名空间隔离→冷却自然重置（不跨日累积）。"""
        store = InMemoryJsonStateStore()
        kw = dict(bs005_triggered=True)
        _eval(store, slot="14:00", **kw)
        rev_today = _eval(store, slot="14:45", **kw)
        assert rev_today.revision_applied is True
        # 次日首评估：状态按 trade_date 隔离，防抖重新计时（首现未生效）
        rev_next = evaluate_boundary_revision(NEXT_DATE, "14:00", state_store=store, **kw)
        assert rev_next.revision_applied is False
        assert rev_next.cooldown["downgrades_used"] == 0
        assert rev_next.original_tier == "NORMAL"  # 次日基线重生成覆盖（MOD-PLAN-001）


# ══════════════════════════════════════════════════════════════
# 档位映射数值 / 全触发源缺失 / 输入校验
# ══════════════════════════════════════════════════════════════


class TestTierMappingAndGuards:
    """档位映射数值与守卫。"""

    def test_normal_tier_unchanged(self):
        """正常=不变（无触发源→不修正，映射 ×1.0/位移 0）。"""
        rev = _eval(InMemoryJsonStateStore())
        assert rev.revision_applied is False
        assert rev.direction == "NONE"
        assert rev.original_tier == "NORMAL"
        assert rev.revised_tier == "NORMAL"
        assert rev.position_cap_scale == pytest.approx(1.0)
        assert rev.no_add_price_shift == pytest.approx(0.0)

    def test_all_sources_missing_no_revision(self):
        """全触发源缺失=不修正（缺数据=该源跳过，留痕 skipped）。"""
        rev = _eval(InMemoryJsonStateStore())
        assert rev.revision_applied is False
        assert rev.triggers == []
        skipped = rev.trace["skipped_sources"]
        assert len(skipped) == 7  # 六降档源缺数据 + 升档腿缺失（bs005 布尔不缺）
        json.dumps(rev.to_dict())

    def test_benign_sources_no_revision(self):
        """触发源注入但全不激活→不修正。"""
        rev = _eval(
            InMemoryJsonStateStore(),
            sentiment=_sentiment(),
            distortion=_distortion(),
            futures_basis=_futures(),
            sector_divergence=_sector(),
            volume_forecast=_volume(),
            rs_ratio=-0.1,
        )
        assert rev.revision_applied is False
        assert rev.triggers == []

    def test_degraded_sources_skipped(self):
        """futures_basis/sector_divergence degraded=True→对应源跳过。"""
        rev = _eval(
            InMemoryJsonStateStore(),
            futures_basis=_futures(vel=-0.02, sigma=0.01, degraded=True),  # 本应触发但降级
            sector_divergence=_sector(state="CONSENSUS_CLIMAX", degraded=True),
        )
        assert rev.revision_applied is False
        skipped = " ".join(rev.trace["skipped_sources"])
        assert TRIGGER_IM_BASIS_DISCOUNT in skipped
        assert TRIGGER_SECTOR_TOP_RISK in skipped

    def test_invalid_inputs_fail_closed(self):
        """trade_date/eval_slot/eval_time/baseline_tier 非法→BoundaryRevisionError。"""
        with pytest.raises(BoundaryRevisionError):
            evaluate_boundary_revision("not-a-date", "14:00")
        with pytest.raises(BoundaryRevisionError):
            evaluate_boundary_revision(DATE, "13:30")  # 非评估时点
        with pytest.raises(BoundaryRevisionError):
            evaluate_boundary_revision(DATE, "14:00", eval_time="25:00")
        with pytest.raises(BoundaryRevisionError):
            evaluate_boundary_revision(DATE, "14:00", baseline_tier="WRONG")
        with pytest.raises(ValueError):  # 继承 ValueError 向后兼容
            evaluate_boundary_revision(DATE, "14:61")


# ══════════════════════════════════════════════════════════════
# 跨日 expired + 留痕写入
# ══════════════════════════════════════════════════════════════


class TestExpiryAndLogging:
    """修正仅当日有效 + plan_revision 留痕。"""

    def _applied_revision(self, store: InMemoryJsonStateStore, **kw):
        _eval(store, slot="14:00", **kw)
        return _eval(store, slot="14:45", **kw)

    def test_cross_day_expired(self):
        """is_effective_on 跨日 False；with_expired 标过期（frozen 不改原实例）。"""
        rev = self._applied_revision(InMemoryJsonStateStore(), bs005_triggered=True)
        assert rev.trade_date == DATE
        assert rev.expired is False
        assert rev.is_effective_on(DATE) is True
        assert rev.is_effective_on(NEXT_DATE) is False
        exp = rev.with_expired()
        assert exp.expired is True
        assert rev.expired is False  # frozen 原实例不变
        assert exp.is_effective_on(DATE) is False

    def test_plan_revision_logged(self, tmp_path):
        """实际改档→plan_revision 事件落 prediction_log（时间/触发/原/新档位）。"""
        db = tmp_path / "prediction_log.db"
        ensure_prediction_log_table(db)
        store = InMemoryJsonStateStore()
        _eval(store, slot="14:00", bs005_triggered=True)  # 未改档→不留痕
        assert query_predictions(db_path=db) == []
        rev = evaluate_boundary_revision(DATE, "14:45", bs005_triggered=True, state_store=store, log_db_path=db)
        assert rev.revision_applied is True
        assert rev.logged is True
        rows = query_predictions(
            trade_date=DATE,
            module="plan_engine.boundary_revision_engine",
            prediction_type="plan_revision",
            db_path=db,
        )
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["original_tier"] == "NORMAL"
        assert payload["revised_tier"] == "CONSERVATIVE"
        assert payload["triggers"] == [TRIGGER_BS005_SHOCK]
        assert payload["eval_slot"] == "14:45"
        assert rows[0]["asof_ts"] == f"{DATE}T14:45:00+08:00"

    def test_no_revision_no_log(self, tmp_path):
        """未改档→不写 plan_revision 事件。"""
        db = tmp_path / "prediction_log.db"
        ensure_prediction_log_table(db)
        rev = evaluate_boundary_revision(DATE, "14:00", log_db_path=db)
        assert rev.revision_applied is False
        assert rev.logged is False
        assert query_predictions(db_path=db) == []


# ══════════════════════════════════════════════════════════════
# 既有文件消费接口（零破坏增量）
# ══════════════════════════════════════════════════════════════


def _boundary() -> TomorrowBoundary:
    return TomorrowBoundary(
        symbol="600519",
        box_upper=11.0,
        box_lower=9.0,
        max_add_position=0.30,
        no_add_price=10.78,
        must_exit_price=11.0,
        breakout_confirm="放量站稳10分钟",
    )


class TestConsumerInterfaces:
    """TomorrowBoundary.apply_revision / ClosingSessionDecision 经修正边界。"""

    def _conservative_revision(self):
        store = InMemoryJsonStateStore()
        _eval(store, slot="14:00", bs005_triggered=True)
        return _eval(store, slot="14:45", bs005_triggered=True)

    def test_apply_revision_conservative(self):
        """保守修正：加仓上限×0.5 + 禁加仓价位下移 0.5×ATR(14)（2026-08-22 裁定：44号 §9.5 上移→下移）。"""
        rev = self._conservative_revision()
        revised = _boundary().apply_revision(rev, atr14=0.5, on_date=DATE)
        assert revised.max_add_position == pytest.approx(0.15)
        assert revised.no_add_price == pytest.approx(10.78 - 0.5 * 0.5)
        assert revised.symbol == "600519"  # 其余字段不变

    def test_apply_revision_cross_day_refused(self):
        """跨日消费→拒发 ValueError（仅当日有效）。"""
        rev = self._conservative_revision()
        with pytest.raises(ValueError, match="仅当日有效"):
            _boundary().apply_revision(rev, atr14=0.5, on_date=NEXT_DATE)

    def test_apply_revision_expired_refused(self):
        """expired 修正→拒发 ValueError。"""
        rev = self._conservative_revision().with_expired()
        with pytest.raises(ValueError, match="过期"):
            _boundary().apply_revision(rev, atr14=0.5, on_date=DATE)

    def test_apply_revision_missing_atr_refused(self):
        """保守修正缺 atr14→拒发（无法定价，fail-closed）。"""
        rev = self._conservative_revision()
        with pytest.raises(ValueError, match="atr14"):
            _boundary().apply_revision(rev, on_date=DATE)

    def test_apply_revision_not_applied_returns_self(self):
        """未改档修正→原样返回（零改动）。"""
        rev = _eval(InMemoryJsonStateStore())  # 无触发源→不修正
        b = _boundary()
        assert b.apply_revision(rev, on_date=DATE) is b

    def test_closing_decision_with_revised_boundary(self):
        """尾盘决策在修正后边界内执行：ADD 上限取修正后 max_add_position。"""
        rev = self._conservative_revision()
        revised = _boundary().apply_revision(rev, atr14=0.5, on_date=DATE)
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        advice = dec.decide("600519", inference, {"weight": 0.10}, high_open_prob=0.75, boundary=revised)
        assert advice.action == "ADD"
        assert advice.max_weight == pytest.approx(0.15)  # 修正后保守上限
        assert "经修正边界" in advice.reason

    def test_closing_decision_default_unchanged(self):
        """boundary 缺省→既有硬编码上限 0.30（零破坏）。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        advice = dec.decide("600519", inference, {"weight": 0.10}, high_open_prob=0.75)
        assert advice.action == "ADD"
        assert advice.max_weight == pytest.approx(0.30)
