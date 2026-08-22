# [A_test] module_id: MOD-PLAN-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-005 | 待统筹登记 | 44号 §4 M3-③ + §9.11 + §9.6 末段
# [MODULE] tests.plan_engine.test_scenario_planner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""ScenarioPlanner (MOD-PLAN-005) 施工验证测试。

全 mock CH 数据（ch_client 注入，离线可跑）：
- 9:00 三情景预案：final_shift 各档映射（保守×0.5/偏守×0.8/正常/偏多×1.2/进攻×1.2）
  + boundary 注入/缺省
- 竞价三细节（§9.11）：合成竞价序列——虚假申报 fake_ratio>0.6 作废 / 量缩降信半档 /
  方向背离降信 / 放量确认 / 昨日涨停竞价溢价
- 9:25 二次匹配：HIGH/LOW/FLAT 桶 × REAL/FAKE/WASH 子型，语义对齐 SCENARIO_LIST
- 降级与契约：缺 auction 数据 degraded 不影响三情景段 / 通道异常降级 / JSON 可序列化
"""

from __future__ import annotations

import json

import pytest

from zephyr.plan_engine.overnight_boundary_reviser import OvernightRevision
from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.scenario_planner import (
    ScenarioPlannerConfig,
    compute_scenario_plan,
)
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary

TRADE_DATE = "2026-08-21"


# ══════════════════════════════════════════════════════════════
# mock CH 数据构造
# ══════════════════════════════════════════════════════════════


def _tsv(rows: list[tuple]) -> str:
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _snap_tsv(rows: list[tuple]) -> str:
    """今日竞价末快照行：(symbol, symbol_canonical, match_price, pre_close, vol, amt)。"""
    return _tsv(rows)


def _series_tsv(rows: list[tuple]) -> str:
    """D3 委托量聚合行：(symbol, peak_vol, vol_after, n_pre, n_after)。"""
    return _tsv(rows)


def _hist_tsv(day_vols: dict[str, float]) -> str:
    """历史竞价量行：(trade_date, symbol, v)——单日单标的，Python 侧按日求和=当日总量。"""
    return _tsv([(d, "600000.SH", v) for d, v in day_vols.items()])


def _hist_5d(vol: float = 1000.0) -> dict[str, float]:
    return {
        "2026-08-20": vol,
        "2026-08-19": vol,
        "2026-08-18": vol,
        "2026-08-17": vol,
        "2026-08-14": vol,
    }


def _make_ch(
    snapshot: str = "",
    series: str = "",
    history: str = "",
    limit_up: str = "",
    raise_on: str | None = None,
):
    """路由式假 CH 客户端：按 SQL 标记分派 TSV；raise_on 指定通道抛异常。

    分派标记：maxIf(=D3 委托量聚合 / GROUP BY trade_date, symbol=D2 历史量 /
    stk_limit=昨日涨停名单 JOIN / 其余 auction_book=今日末快照。
    """

    def _ch(sql: str) -> str:
        if "stk_limit" in sql:
            if raise_on == "limit_up":
                raise RuntimeError("limit_up boom")
            return limit_up
        if "auction_book" in sql:
            if "maxIf(" in sql:
                if raise_on == "series":
                    raise RuntimeError("series boom")
                return series
            if "GROUP BY trade_date, symbol" in sql:
                if raise_on == "history":
                    raise RuntimeError("history boom")
                return history
            if raise_on == "snapshot":
                raise RuntimeError("snapshot boom")
            return snapshot
        return ""  # us_index/margin_trading 等（revision 缺省现算时空数据降级）

    return _ch


def _revision(final_shift: float = 0.0, gap_adj: float | None = None) -> OvernightRevision:
    return OvernightRevision(
        date=TRADE_DATE,
        gap_adj=gap_adj,
        gap_adj_degraded=False,
        fund_score=None,
        fund_detail={},
        event_flags={},
        sensitivity_scale=1.0,
        final_shift=final_shift,
        m1_threshold_scale=1.0,
        basis_weight_scale=1.0,
        a50_channel_weight=None,
        reasons=[],
        trace={"channels": {}},
    )


def _boundary() -> TomorrowBoundary:
    return TomorrowBoundary(
        symbol="600000.SH",
        box_upper=11.0,
        box_lower=9.5,
        max_add_position=0.30,
        no_add_price=10.8,
        must_exit_price=11.0,
        breakout_confirm="放量站稳10分钟",
        computed_at=None,
    )


def _compute(ch, revision=None, boundary=None, config=None):
    return compute_scenario_plan(TRADE_DATE, ch_client=ch, config=config, revision=revision, boundary=boundary)


# ══════════════════════════════════════════════════════════════
# 9:00 三情景预案：final_shift 各档映射（44号 §9.5/§9.6）
# ══════════════════════════════════════════════════════════════


class TestThreeScenarios:
    """三情景生成与档位映射（竞价段无数据降级，仅验 9:00 段）。"""

    @pytest.mark.parametrize(
        ("shift", "stance", "max_add"),
        [
            (-1.0, "CONSERVATIVE", 0.15),  # 保守 ×0.5（§9.5）
            (-0.5, "DEFENSIVE", 0.24),  # 偏守 ×0.8（§9.6 半档 -20%）
            (0.0, "NORMAL", 0.30),  # 正常
            (0.5, "OFFENSIVE", 0.36),  # 偏多 ×1.2（§9.6 半档 +20%）
            (1.0, "AGGRESSIVE", 0.36),  # 进攻 ×1.2（§9.5）
        ],
    )
    def test_shift_stance_mapping(self, shift, stance, max_add):
        """final_shift 五档 → 档位名与加仓上限缩放（boundary 注入，基线 0.30）。"""
        plan = _compute(_make_ch(), revision=_revision(final_shift=shift), boundary=_boundary())
        assert len(plan.three_scenarios) == 3
        for sc in plan.three_scenarios:
            assert sc.stance == stance
            assert sc.final_shift == shift
            assert sc.max_add_position == pytest.approx(max_add)

    def test_scenario_names_and_trigger_ranges(self):
        """三情景 HIGH/FLAT/LOW 固定顺序，触发区间 ±2%（与 MOD-PLAN-002 对齐）。"""
        plan = _compute(_make_ch(), revision=_revision(), boundary=_boundary())
        high, flat, low = plan.three_scenarios
        assert (high.name, high.open_pct_min, high.open_pct_max) == ("HIGH_OPEN", 0.02, None)
        assert (flat.name, flat.open_pct_min, flat.open_pct_max) == ("FLAT_OPEN", -0.02, 0.02)
        assert (low.name, low.open_pct_min, low.open_pct_max) == ("LOW_OPEN", None, -0.02)
        # boundary 注入 → 绝对价位填充
        assert high.no_add_price == 10.8
        assert high.reduce_trigger_price == 9.5
        assert flat.must_exit_price == 11.0
        assert all(sc.actions for sc in plan.three_scenarios)

    def test_boundary_missing_prices_none(self):
        """boundary 缺省 → 价位字段 None + 相对参数保留 + degraded 留痕。"""
        plan = _compute(_make_ch(), revision=_revision(final_shift=-1.0))
        high = plan.three_scenarios[0]
        assert high.max_add_position == pytest.approx(0.15)  # 缺省基线 0.30×0.5
        assert high.no_add_price is None
        assert high.reduce_trigger_price is None
        assert high.must_exit_price is None
        assert plan.degraded is True
        assert any("boundary 缺省" in r for r in plan.reasons)


# ══════════════════════════════════════════════════════════════
# 竞价三细节（44号 §9.11）
# ══════════════════════════════════════════════════════════════


class TestAuctionDetails:
    """合成竞价序列：D1 偏离 / D2 量 / D3 撤单 / 昨日涨停溢价。"""

    def test_deviation_amount_weighted(self):
        """D1 成交额加权：A(+10%,amt100)+B(-1%,amt300) → dev=(10-3)/400=+1.75%。"""
        snap = _snap_tsv(
            [
                ("600000.SH", "600000.SH", 11.0, 10.0, 600, 100.0),
                ("000001.SZ", "000001.SZ", 9.9, 10.0, 600, 300.0),
            ]
        )
        series = _series_tsv([("600000.SH", 100, 95, 5, 2), ("000001.SZ", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(), boundary=_boundary())
        av = plan.auction_verification
        assert av is not None and av.deviation == pytest.approx(0.0175)
        assert av.direction == "FLAT"  # |1.75%| < 2%

    def test_volume_confirm_real_up(self):
        """D2 放量≥1.2× 且方向一致 → 确认：dev+3% 高开 → HIGH_OPEN_REAL_UP，信度 1.0。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        av = plan.auction_verification
        assert av.volume_ratio == pytest.approx(1.2)
        assert av.direction_consistent is True
        assert av.confirmed is True
        assert plan.final_scenario == "HIGH_OPEN_REAL_UP"
        assert plan.confidence_scale == 1.0

    def test_volume_shrink_half_confidence(self):
        """D2 量缩（0.5×<1.0×）→ 降信半档；未确认 → HIGH_OPEN_FAKE_UP。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 500, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        av = plan.auction_verification
        assert av.volume_shrink is True
        assert av.confirmed is False
        assert plan.final_scenario == "HIGH_OPEN_FAKE_UP"
        assert plan.confidence_scale == 0.5

    def test_direction_divergence(self):
        """D1 方向背离（gap_adj +1.0% vs deviation -3%）→ 降信半档 + LOW_OPEN_FAKE_DOWN。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 9.7, 10.0, 1300, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        av = plan.auction_verification
        assert av.direction_consistent is False
        assert av.confirmed is False  # 放量但方向不一致 → 不确认
        assert plan.final_scenario == "LOW_OPEN_FAKE_DOWN"
        assert plan.confidence_scale == 0.5  # 背离降信（量未缩不再乘）
        assert any("背离" in r for r in plan.reasons)

    def test_fake_ratio_void(self):
        """D3 虚假申报：fake_ratio=(800+200)/(1000+500)=0.667>0.6 → 方向作废按洗盘。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 1000, 200, 5, 2), ("000001.SZ", 500, 300, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(), boundary=_boundary())
        av = plan.auction_verification
        assert av.fake_ratio == pytest.approx(1000 / 1500)
        assert av.direction_void is True
        assert plan.final_scenario == "HIGH_OPEN_WASH"  # 竞价高开但方向信号作废
        assert plan.confidence_scale == 1.0  # 作废不额外降信（方向整体不采信）

    def test_fake_ratio_below_threshold_no_void(self):
        """fake_ratio=0.05 正常 → 不作废。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        assert plan.auction_verification.direction_void is False
        assert plan.final_scenario == "HIGH_OPEN_REAL_UP"

    def test_series_snapshot_insufficient_skipped(self):
        """9:20 后无快照的标的剔除（防缺数据误判全撤）→ fake_ratio=None 不作废。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 1000, 0, 5, 0)])  # n_after=0
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        av = plan.auction_verification
        assert av.fake_ratio is None
        assert av.direction_void is False
        assert av.detail["fake"]["symbols_skipped"] == 1

    def test_yesterday_limit_up_premium(self):
        """昨日涨停竞价溢价：昨涨停股 600000.SH 竞价 +5% → premium=0.05（注记）。"""
        snap = _snap_tsv(
            [
                ("600000.SH", "600000.SH", 10.5, 10.0, 1200, 500.0),
                ("000001.SZ", "000001.SZ", 10.1, 10.0, 800, 300.0),
            ]
        )
        series = _series_tsv([("600000.SH", 100, 95, 5, 2), ("000001.SZ", 100, 98, 5, 2)])
        limit_up = _tsv([("600000.SH",)])  # JOIN 名单（symbol_canonical）
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)), limit_up=limit_up)
        plan = _compute(ch, revision=_revision(), boundary=_boundary())
        av = plan.auction_verification
        assert av.yesterday_limit_premium == pytest.approx(0.05)
        assert any("打板情绪" in r for r in plan.reasons)

    def test_premium_no_limit_up_list(self):
        """昨日无涨停股 → premium=None 不炸。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.1, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)), limit_up="")
        plan = _compute(ch, revision=_revision(), boundary=_boundary())
        assert plan.auction_verification.yesterday_limit_premium is None


# ══════════════════════════════════════════════════════════════
# 9:25 二次匹配修正（复用 9 情景，语义对齐 MOD-PLAN-002）
# ══════════════════════════════════════════════════════════════


class TestRematch:
    """三桶 × REAL/FAKE/WASH 子型映射。"""

    def _run(self, dev_price, vol, gap_adj, fake=(100, 95)):
        snap = _snap_tsv([("600000.SH", "600000.SH", dev_price, 10.0, vol, 500.0)])
        series = _series_tsv([("600000.SH", fake[0], fake[1], 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        return _compute(ch, revision=_revision(gap_adj=gap_adj), boundary=_boundary())

    def test_flat_bucket_real_up(self):
        """FLAT 桶放量确认+dev>0 → FLAT_OPEN_REAL_UP。"""
        plan = self._run(10.1, 1300, 0.01)  # dev+1%，vol 1.3×
        assert plan.final_scenario == "FLAT_OPEN_REAL_UP"
        assert plan.confidence_scale == 1.0

    def test_flat_bucket_real_down(self):
        """FLAT 桶放量确认+dev<0 → FLAT_OPEN_REAL_DOWN。"""
        plan = self._run(9.9, 1300, -0.01)  # dev-1%，vol 1.3×
        assert plan.final_scenario == "FLAT_OPEN_REAL_DOWN"

    def test_flat_bucket_wash_no_confirm(self):
        """FLAT 桶量缩未确认 → FLAT_OPEN_WASH + 降信半档。"""
        plan = self._run(10.1, 900, 0.01)  # vol 0.9×
        assert plan.final_scenario == "FLAT_OPEN_WASH"
        assert plan.confidence_scale == 0.5

    def test_low_open_real_down(self):
        """LOW 桶放量确认+方向一致向下 → LOW_OPEN_REAL_DOWN。"""
        plan = self._run(9.7, 1300, -0.01)
        assert plan.final_scenario == "LOW_OPEN_REAL_DOWN"

    def test_flat_void_wash(self):
        """FLAT 桶虚假申报作废 → FLAT_OPEN_WASH。"""
        plan = self._run(10.1, 1300, 0.01, fake=(1000, 200))
        assert plan.auction_verification.direction_void is True
        assert plan.final_scenario == "FLAT_OPEN_WASH"

    def test_scenario_membership(self):
        """final_scenario 恒 ∈ SCENARIO_LIST（MOD-PLAN-002 9 情景常量语义对齐）。"""
        for dev_price, vol, gap_adj in [
            (10.3, 1300, 0.01),
            (9.7, 1300, -0.01),
            (10.1, 900, None),
            (9.9, 1300, 0.01),  # 背离
        ]:
            plan = self._run(dev_price, vol, gap_adj)
            assert plan.final_scenario in SCENARIO_LIST


# ══════════════════════════════════════════════════════════════
# 降级与契约
# ══════════════════════════════════════════════════════════════


class TestDegradeAndContract:
    """缺数据降级 + fail-open + 输出契约。"""

    def test_no_auction_data_degraded(self):
        """auction_book 全空 → 竞价段 degraded + final 缺省 FLAT_OPEN_WASH，三情景段不受影响。"""
        plan = _compute(_make_ch(), revision=_revision(final_shift=0.5), boundary=_boundary())
        av = plan.auction_verification
        assert av.status == "degraded:no_data"
        assert av.deviation is None and av.volume_ratio is None and av.fake_ratio is None
        assert plan.final_scenario == "FLAT_OPEN_WASH"
        assert plan.degraded is True
        assert len(plan.three_scenarios) == 3
        assert plan.three_scenarios[0].max_add_position == pytest.approx(0.36)  # 段一正常产出

    def test_snapshot_channel_exception_degrades(self):
        """snapshot 通道抛异常 → 该段降级不炸整体。"""
        plan = _compute(_make_ch(raise_on="snapshot"), revision=_revision(), boundary=_boundary())
        assert plan.auction_verification.status == "degraded:no_data"
        assert plan.trace["channels"]["auction_book"].startswith("error:")
        assert len(plan.three_scenarios) == 3

    def test_history_missing_volume_ratio_none(self):
        """5 日历史缺失 → volume_ratio=None，不确认不降信（无基准），deviation 正常。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history="")
        plan = _compute(ch, revision=_revision(gap_adj=0.01), boundary=_boundary())
        av = plan.auction_verification
        assert av.volume_ratio is None
        assert av.confirmed is False and av.volume_shrink is False
        assert plan.final_scenario == "HIGH_OPEN_FAKE_UP"  # 有方向无确认
        assert plan.confidence_scale == 1.0

    def test_default_revision_inline(self):
        """revision 缺省 → 内联现算 OvernightBoundaryReviser（共用 ch_client，空数据零修正）。"""
        plan = _compute(_make_ch(), boundary=_boundary())
        assert plan.trace["channels"]["overnight_revision"] == "computed_inline"
        assert plan.three_scenarios[0].final_shift == 0.0

    def test_revision_injected(self):
        """revision 注入 → 不现算。"""
        plan = _compute(_make_ch(), revision=_revision(), boundary=_boundary())
        assert plan.trace["channels"]["overnight_revision"] == "injected"

    def test_json_serializable(self):
        """输出纯 frozen dataclass，JSON 可序列化（prediction_log 落库契约）。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 100, 95, 5, 2)])
        limit_up = _tsv([("600000.SH",)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)), limit_up=limit_up)
        plan = _compute(ch, revision=_revision(final_shift=0.5, gap_adj=0.01), boundary=_boundary())
        payload = json.dumps(plan.to_dict(), ensure_ascii=False)
        restored = json.loads(payload)
        assert restored["date"] == TRADE_DATE
        assert restored["final_scenario"] == "HIGH_OPEN_REAL_UP"
        assert restored["auction_verification"]["volume_ratio"] == pytest.approx(1.2)
        assert len(restored["three_scenarios"]) == 3

    def test_config_override(self):
        """阈值 config 化：fake_ratio_void=0.9 覆盖后 0.667 不作废。"""
        snap = _snap_tsv([("600000.SH", "600000.SH", 10.3, 10.0, 1200, 500.0)])
        series = _series_tsv([("600000.SH", 1000, 200, 5, 2), ("000001.SZ", 500, 300, 5, 2)])
        ch = _make_ch(snapshot=snap, series=series, history=_hist_tsv(_hist_5d(1000.0)))
        cfg = ScenarioPlannerConfig(fake_ratio_void=0.9)
        plan = _compute(ch, revision=_revision(gap_adj=0.01), config=cfg)
        assert plan.auction_verification.direction_void is False
        assert plan.final_scenario == "HIGH_OPEN_REAL_UP"

    def test_invalid_trade_date_raises(self):
        """ERROR_CONTRACT：仅 trade_date 非法抛 ValueError。"""
        with pytest.raises(ValueError):
            compute_scenario_plan("not-a-date", ch_client=_make_ch(), revision=_revision())
