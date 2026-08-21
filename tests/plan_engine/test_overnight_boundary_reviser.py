# [A_test] module_id: MOD-PLAN-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-004 | 待统筹登记 | 44号 §9.6/§9.10/§9.12
# [MODULE] tests.plan_engine.test_overnight_boundary_reviser
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""OvernightBoundaryReviser (MOD-PLAN-004) 施工验证测试。

三通道全 mock CH 数据（ch_client 注入，离线可跑）：
- M3-①a 外盘通道：gap 各档映射（不变/半档/整档/BS-005 硬触发）+ 符号空值 degraded
- M3-⑦ 资金面四件套：同向确认 / 反向否决半档 / σ 内不否决 / 分量缺失权重重归一
- M3-⑧ 事件日历：事件夜敏感度升半档 / 期权到期 m1_threshold_scale / 交割周
  basis_weight_scale / A50 交割日规则自算 / 空表 fail-open / 单通道异常降级
"""

from __future__ import annotations

import datetime
import json

import pytest

from zephyr.plan_engine.overnight_boundary_reviser import (
    DEFAULT_CONFIG,
    OvernightRevision,
    compute_overnight_revision,
)

TRADE_DATE = "2026-08-21"  # 周五；A50 交割日=2026-08-28（8/31 周一，倒数第2工作日=28），不干扰


# ══════════════════════════════════════════════════════════════
# mock CH 数据构造
# ══════════════════════════════════════════════════════════════


def _tsv(rows: list[tuple]) -> str:
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _us_index_tsv(ret_spx: float | None, ret_ndx: float | None) -> str:
    """最新两条收盘反推（DESC 序返回，与 SQL ORDER BY trade_date DESC 一致）。"""
    rows = []
    if ret_spx is not None:
        rows += [("2026-08-20", "SPX", 5000 * (1 + ret_spx)), ("2026-08-19", "SPX", 5000)]
    if ret_ndx is not None:
        rows += [("2026-08-20", "IXIC", 20000 * (1 + ret_ndx)), ("2026-08-19", "IXIC", 20000)]
    return _tsv(rows)


def _series_tsv(latest: float, hist_lo: float, hist_hi: float, n: int = 20) -> str:
    """21 行日序列（DESC）：latest + n 个历史点（hist_lo/hist_hi 交替，std>0）。"""
    base = datetime.date(2026, 8, 20)
    rows = [(base, latest)]
    for i in range(1, n + 1):
        rows.append((base - datetime.timedelta(days=i), hist_lo if i % 2 else hist_hi))
    return _tsv(rows)


def _make_ch(
    us_index: str = "",
    margin: str = "",
    money_flow: str = "",
    block_premium: str = "",
    calendar: str = "",
    raise_on: str | None = None,
):
    """路由式假 CH 客户端：按 SQL 中表名分派 TSV；raise_on 指定通道抛异常。"""

    def _ch(sql: str) -> str:
        for name, payload in (
            ("us_index", us_index),
            ("margin_trading", margin),
            ("money_flow", money_flow),
            ("block_trade", block_premium),
            ("calendar_event", calendar),
        ):
            if name in sql:
                if raise_on == name:
                    raise RuntimeError(f"{name} boom")
                return payload
        return ""

    return _ch


def _compute(ch, trade_date: str = TRADE_DATE, bs005: bool = False) -> OvernightRevision:
    return compute_overnight_revision(trade_date, ch_client=ch, bs005_triggered=bs005)


# ══════════════════════════════════════════════════════════════
# M3-①a 外盘通道：gap 各档映射
# ══════════════════════════════════════════════════════════════


class TestGapChannel:
    """外盘隔夜修正档位映射（44号 §9.6）。"""

    def test_small_gap_no_shift(self):
        """|gap_adj| < 0.5% → 不变档。"""
        ch = _make_ch(us_index=_us_index_tsv(0.010, 0.005))  # gap=0.2%*...=0.0035
        rev = _compute(ch)
        assert rev.gap_adj == pytest.approx(0.2 * 0.010 + 0.3 * 0.005)
        assert rev.gap_adj_degraded is False
        assert rev.final_shift == 0.0
        assert any("不变档" in r for r in rev.reasons)

    def test_half_step_shift(self):
        """0.5% ≤ |gap_adj| < 1.5% → +半档（事件日历空表=正常敏感度）。"""
        ch = _make_ch(us_index=_us_index_tsv(0.030, 0.020))  # gap=1.2%
        rev = _compute(ch)
        assert rev.gap_adj == pytest.approx(0.012)
        assert rev.final_shift == 0.5

    def test_full_step_shift(self):
        """|gap_adj| ≥ 1.5% → -整档（负向）。"""
        ch = _make_ch(us_index=_us_index_tsv(-0.040, -0.030))  # gap=-1.7%
        rev = _compute(ch)
        assert rev.final_shift == -1.0

    def test_bs005_hard_trigger(self):
        """BS-005 触发 → ±一档（gap 微负 → 保守迁移 -1）。"""
        ch = _make_ch(us_index=_us_index_tsv(-0.001, -0.001))  # gap=-0.1%
        rev = _compute(ch, bs005=True)
        assert rev.final_shift == -1.0
        assert any("BS-005" in r for r in rev.reasons)

    def test_symbol_null_degraded(self):
        """符号空值缺陷：index_code 无法区分标普/纳指 → 单序列代理 degraded=True。"""
        rows = [
            ("2026-08-20", "", 5100),  # 空符号行
            ("2026-08-19", "", 5000),
            ("2026-08-20", "SPX", 6000),  # 仅剩单序列可区分
            ("2026-08-19", "SPX", 5900),
        ]
        rev = _compute(_make_ch(us_index=_tsv(rows)))
        assert rev.gap_adj_degraded is True
        assert rev.gap_adj == pytest.approx(100 / 5900)
        assert rev.trace["channels"]["us_index"] == "degraded:single_series_proxy"

    def test_no_data_fail_open(self):
        """外盘无数据 → gap_adj=None 不变档不炸。"""
        rev = _compute(_make_ch())
        assert rev.gap_adj is None
        assert rev.final_shift == 0.0


# ══════════════════════════════════════════════════════════════
# M3-⑦ 资金面四件套：确认/否决（44号 §9.10）
# ══════════════════════════════════════════════════════════════


class TestFundChannel:
    """fund_score 对 gap_adj 的确认/否决。"""

    _GAP_HALF = None  # 占位说明：用例内自造 gap

    def _fund_ch(self, direction: str) -> str:
        """direction=up → 各分量 z 强正；down → 强负。"""
        if direction == "up":
            margin = _series_tsv(210.0, 100.0, 120.0)  # z=+10
            mf = _series_tsv(2.1, 1.0, 1.2)
            bt = _series_tsv(0.05, 0.01, -0.01)  # premium 序列
        else:
            margin = _series_tsv(10.0, 100.0, 120.0)  # z=-10
            mf = _series_tsv(0.1, 1.0, 1.2)
            bt = _series_tsv(-0.05, 0.01, -0.01)
        return _make_ch(us_index=_us_index_tsv(0.020, 0.005), margin=margin, money_flow=mf, block_premium=bt)

    def test_fund_confirm_same_direction(self):
        """fund_score 与 gap 同向 → 确认（×1.0，维持 +0.5）。"""
        rev = _compute(self._fund_ch("up"))
        assert rev.gap_adj > 0
        assert rev.fund_score is not None and rev.fund_score > 0
        assert rev.final_shift == 0.5
        assert any("确认" in r for r in rev.reasons)

    def test_fund_veto_opposite(self):
        """fund_score 反向且 |z|>1σ → 否决半档（+0.5→0）。"""
        rev = _compute(self._fund_ch("down"))
        assert rev.fund_score is not None and rev.fund_score < -1.0
        assert rev.final_shift == 0.0
        assert any("否决半档" in r for r in rev.reasons)

    def test_fund_no_veto_within_sigma(self):
        """反向但 |fund_score|≤1σ → 不否决。"""
        # margin z≈-0.5（latest 略低于均值），其余通道空
        margin = _series_tsv(105.0, 100.0, 120.0)  # mean=110, std=10 → z=-0.5
        ch = _make_ch(us_index=_us_index_tsv(0.020, 0.005), margin=margin)
        rev = _compute(ch)
        assert rev.fund_score == pytest.approx(-0.5)
        assert rev.final_shift == 0.5

    def test_fund_partial_renormalize(self):
        """分量缺失 → 剔除+权重重归一（仅 margin 启用时 weight_renormalized=0.4）。"""
        margin = _series_tsv(210.0, 100.0, 120.0)  # z=+10
        rev = _compute(_make_ch(margin=margin))
        assert rev.fund_detail["components_used"] == ["margin_delta"]
        assert rev.fund_detail["weight_renormalized"] == pytest.approx(0.4)
        assert rev.fund_score == pytest.approx(10.0)
        assert "mf_net" in rev.fund_detail["components_skipped"]

    def test_fund_all_empty(self):
        """四件全无数据 → fund_score=None，不炸。"""
        rev = _compute(_make_ch(us_index=_us_index_tsv(0.020, 0.005)))
        assert rev.fund_score is None
        assert rev.final_shift == 0.5  # 外盘半档不受影响

    def test_fund_insufficient_history_degrades(self):
        """历史点不足 → 该分量降级剔除，不炸整体。"""
        margin = _tsv([("2026-08-20", 210.0), ("2026-08-19", 100.0)])  # 仅 2 行
        rev = _compute(_make_ch(margin=margin))
        assert rev.fund_score is None
        assert rev.trace["channels"]["margin_trading"] == "degraded:insufficient_history"


# ══════════════════════════════════════════════════════════════
# M3-⑧ 事件日历联动（44号 §9.12）
# ══════════════════════════════════════════════════════════════


class TestEventCalendar:
    """事件日历联动与 fail-open 铁律。"""

    def test_event_night_sensitivity_up(self):
        """FOMC 事件夜（昨日）→ 敏感度升半档：1.2% gap 触发整档（正常仅半档）。"""
        cal = _tsv([("2026-08-20", "fomc_meeting")])
        ch = _make_ch(us_index=_us_index_tsv(0.030, 0.020), calendar=cal)  # gap=1.2%
        rev = _compute(ch)
        assert rev.event_flags["high_impact_event_night"] is True
        assert rev.sensitivity_scale == 0.5
        assert rev.final_shift == 1.0  # 正常阈值下仅 +0.5（对照 TestGapChannel.test_half_step_shift）

    def test_option_expiry_m1_scale(self):
        """期权到期日当日 → m1_threshold_scale=0.8。"""
        cal = _tsv([("2026-08-21", "index_option_expiry")])
        rev = _compute(_make_ch(calendar=cal))
        assert rev.event_flags["index_option_expiry_today"] is True
        assert rev.m1_threshold_scale == 0.8

    def test_futures_delivery_week_scale(self):
        """股指期货交割当周 → basis_weight_scale=0.5。"""
        cal = _tsv([("2026-08-19", "futures_delivery")])  # 周三，与 8/21 同周
        rev = _compute(_make_ch(calendar=cal))
        assert rev.event_flags["futures_delivery_week"] is True
        assert rev.basis_weight_scale == 0.5

    def test_a50_delivery_rule_derived(self):
        """A50 交割日（规则自算 2026-08-28）→ 敏感度升半档 + A50 权重 0.45。"""
        rev = _compute(_make_ch(), trade_date="2026-08-28")
        assert rev.event_flags["a50_delivery_rule_date"] == "2026-08-28"
        assert rev.event_flags["a50_futures_delivery_today"] is True
        assert rev.sensitivity_scale == 0.5
        assert rev.a50_channel_weight == 0.45

    def test_a50_delivery_eve(self):
        """A50 交割前夜（下一工作日=交割日）→ 敏感度升半档，权重不上调。"""
        rev = _compute(_make_ch(), trade_date="2026-08-27")
        assert rev.event_flags["a50_futures_delivery_eve"] is True
        assert rev.sensitivity_scale == 0.5
        assert rev.a50_channel_weight is None

    def test_calendar_empty_fail_open(self):
        """空表/查询失败 → 静默跳过+留痕，不阻塞主流程。"""
        rev = _compute(_make_ch(calendar=""))
        assert rev.event_flags["calendar_status"] == "empty_or_failed"
        assert rev.event_flags["high_impact_event_night"] is False
        assert rev.m1_threshold_scale == 1.0
        assert rev.basis_weight_scale == 1.0
        assert "calendar_event" in rev.trace["channels"]


# ══════════════════════════════════════════════════════════════
# 降级与契约
# ══════════════════════════════════════════════════════════════


class TestDegradeAndContract:
    """单通道异常降级 + 输出契约。"""

    def test_channel_exception_degrades(self):
        """margin 通道抛异常 → 该通道降级，外盘/日历正常，整体不炸。"""
        ch = _make_ch(us_index=_us_index_tsv(0.030, 0.020), raise_on="margin_trading")
        rev = _compute(ch)
        assert rev.final_shift == 0.5  # 外盘通道正常产出半档
        assert rev.trace["channels"]["margin_trading"].startswith("error:")
        assert rev.fund_score is None  # 资金面其余通道本无数据

    def test_all_channels_empty(self):
        """全部通道无数据 → 零修正 + 全留痕，不抛异常。"""
        rev = _compute(_make_ch())
        assert rev.final_shift == 0.0
        assert rev.gap_adj is None
        assert rev.fund_score is None
        assert rev.sensitivity_scale == 1.0
        assert isinstance(rev.reasons, list) and rev.reasons

    def test_json_serializable(self):
        """输出纯 dataclass，JSON 可序列化（prediction_log 落库契约）。"""
        cal = _tsv([("2026-08-21", "index_option_expiry")])
        rev = _compute(_make_ch(us_index=_us_index_tsv(0.030, 0.020), calendar=cal))
        payload = json.dumps(rev.to_dict(), ensure_ascii=False)
        restored = json.loads(payload)
        assert restored["date"] == TRADE_DATE
        assert restored["final_shift"] == 0.5
        assert restored["m1_threshold_scale"] == 0.8

    def test_config_override(self):
        """权重/阈值 config 化：覆盖后生效。"""
        cfg = DEFAULT_CONFIG.__class__(gap_weight_spx=0.5, gap_weight_ndx=0.5)
        ch = _make_ch(us_index=_us_index_tsv(0.010, 0.030))
        rev = compute_overnight_revision(TRADE_DATE, ch_client=ch, config=cfg)
        assert rev.gap_adj == pytest.approx(0.020)

    def test_invalid_trade_date_raises(self):
        """ERROR_CONTRACT：仅 trade_date 非法抛 ValueError。"""
        with pytest.raises(ValueError):
            _compute(_make_ch(), trade_date="not-a-date")
