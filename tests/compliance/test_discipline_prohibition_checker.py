# [BLUEPRINT] MOD-CMP-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-CMP-002 四项严禁检测 + KillSwitchLite 单元测试（43 号 §4，BM-BUY-08-B）。"""

from __future__ import annotations

from datetime import date

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    DisciplineThresholds,
    KillSwitchLite,
    OrderRequest,
    ProhibitedBehavior,
)


def _order(**kw) -> OrderRequest:
    base = dict(symbol="600519", price=100.0, strategy_id="s1", risk_exposure=0.01, size=10_000.0, is_add=False)
    return OrderRequest(**{**base, **kw})


def _ctx(**kw) -> DisciplineContext:
    base = dict(
        signal_ref_price=100.0,
        surge_30min_pct=0.0,
        position_pnl_pct=None,
        win_streak=0,
        normal_exposure=0.01,
        daily_pnl_pct=0.0,
        projected_daily_freq=3.0,
        freq_baseline_20d=5.0,
        size_baseline_20d=10_000.0,
    )
    return DisciplineContext(**{**base, **kw})


def _guard(tmp_path, **kw) -> DisciplineGuard:
    return DisciplineGuard(logger=ComplianceLogger(tmp_path / "c.jsonl"), **kw)


# ── 踏空追高 ──


def test_chasing_hard_block(tmp_path):
    """追涨幅度 +3% > +2% 且近 30min 涨幅 +6% > +5% → Hard Block。"""
    v = _guard(tmp_path).check(_order(price=103.0), _ctx(surge_30min_pct=0.06))
    assert v.behavior is ProhibitedBehavior.CHASING
    assert v.action is DisciplineAction.HARD_BLOCK


def test_chasing_no_surge_pass(tmp_path):
    """有追高幅度但无急剧拉升 → 放行（两层条件缺一不可）。"""
    v = _guard(tmp_path).check(_order(price=103.0), _ctx(surge_30min_pct=0.03))
    assert v.action is DisciplineAction.PASS


def test_chasing_no_signal_anchor_skipped(tmp_path):
    """信号锚缺失 → 追高检测跳过（无锚不可判）。"""
    v = _guard(tmp_path).check(_order(price=103.0), _ctx(signal_ref_price=None, surge_30min_pct=0.06))
    assert v.action is DisciplineAction.PASS


def test_chasing_boundary_not_block(tmp_path):
    """恰好 +2% 不超阈值 → 放行。"""
    v = _guard(tmp_path).check(_order(price=102.0), _ctx(surge_30min_pct=0.06))
    assert v.action is DisciplineAction.PASS


# ── 被套补仓 ──


def test_adding_to_loser_hard_block(tmp_path):
    v = _guard(tmp_path).check(_order(is_add=True), _ctx(position_pnl_pct=-0.06))
    assert v.behavior is ProhibitedBehavior.ADDING_TO_LOSER
    assert v.action is DisciplineAction.HARD_BLOCK


def test_add_within_threshold_pass(tmp_path):
    v = _guard(tmp_path).check(_order(is_add=True), _ctx(position_pnl_pct=-0.03))
    assert v.action is DisciplineAction.PASS


def test_not_add_no_position_check(tmp_path):
    """非加仓单不触发补仓检测。"""
    v = _guard(tmp_path).check(_order(is_add=False), _ctx(position_pnl_pct=-0.20))
    assert v.action is DisciplineAction.PASS


# ── 盈利骄傲 ──


def test_overconfidence_warning_not_block(tmp_path):
    """连盈 5 笔 + 敞口 1.6×常规 → Warning 不阻断。"""
    v = _guard(tmp_path).check(_order(risk_exposure=0.016), _ctx(win_streak=5, normal_exposure=0.01))
    assert v.behavior is ProhibitedBehavior.OVERCONFIDENCE
    assert v.action is DisciplineAction.WARNING


def test_overconfidence_streak_below_pass(tmp_path):
    v = _guard(tmp_path).check(_order(risk_exposure=0.016), _ctx(win_streak=4, normal_exposure=0.01))
    assert v.action is DisciplineAction.PASS


# ── 亏损报复 ──


def test_revenge_freq_abnormal_triggers_kill_switch(tmp_path):
    """当日 -3% + 频率 2.5×基线 → Hard Block + KillSwitchLite 触发。"""
    ks = KillSwitchLite(tmp_path / "ks.json", logger=ComplianceLogger(tmp_path / "c.jsonl"))
    g = DisciplineGuard(kill_switch=ks, logger=ComplianceLogger(tmp_path / "c.jsonl"))
    v = g.check(_order(), _ctx(daily_pnl_pct=-0.03, projected_daily_freq=12.5))
    assert v.behavior is ProhibitedBehavior.REVENGE_TRADING
    assert v.action is DisciplineAction.HARD_BLOCK
    assert v.kill_switch_triggered
    assert ks.is_blocked("s1", date.today())


def test_revenge_size_abnormal(tmp_path):
    v = _guard(tmp_path).check(_order(size=16_000.0), _ctx(daily_pnl_pct=-0.03, size_baseline_20d=10_000.0))
    assert v.behavior is ProhibitedBehavior.REVENGE_TRADING


def test_revenge_loss_not_reached_pass(tmp_path):
    v = _guard(tmp_path).check(_order(), _ctx(daily_pnl_pct=-0.01, projected_daily_freq=12.5))
    assert v.action is DisciplineAction.PASS


def test_revenge_priority_over_overconfidence(tmp_path):
    """报复（Hard Block）优先于骄傲（Warning）。"""
    v = _guard(tmp_path).check(
        _order(risk_exposure=0.016, size=16_000.0),
        _ctx(win_streak=6, daily_pnl_pct=-0.03),
    )
    assert v.behavior is ProhibitedBehavior.REVENGE_TRADING
    assert v.action is DisciplineAction.HARD_BLOCK


# ── KillSwitchLite ──


def test_kill_switch_expiry_auto_reset_next_day(tmp_path):
    ks = KillSwitchLite(tmp_path / "ks.json", logger=ComplianceLogger(tmp_path / "c.jsonl"))
    d1 = date(2026, 8, 14)
    assert ks.trigger("s1", "REVENGE_TRADING", d1)
    assert ks.is_blocked("s1", d1)
    assert not ks.is_blocked("s1", date(2026, 8, 15))  # 次日自动复位


def test_kill_switch_manual_reset(tmp_path):
    ks = KillSwitchLite(tmp_path / "ks.json", logger=ComplianceLogger(tmp_path / "c.jsonl"))
    d1 = date(2026, 8, 14)
    ks.trigger("s1", "R", d1)
    assert ks.reset("s1")
    assert not ks.is_blocked("s1", d1)


def test_kill_switch_corrupted_state_fail_closed(tmp_path):
    """状态损坏 → is_blocked=True（保守）+ trigger 升级全局回调。"""
    p = tmp_path / "ks.json"
    p.write_text("{broken", encoding="utf-8")
    escalated: list[tuple[str, str]] = []
    ks = KillSwitchLite(
        p,
        on_escalate=lambda sid, reason: escalated.append((sid, reason)),
        logger=ComplianceLogger(tmp_path / "c.jsonl"),
    )
    assert ks.is_blocked("s1", date.today())  # Fail-Closed
    assert not ks.trigger("s1", "R", date.today())  # 触发失败
    assert escalated and escalated[0][0] == "s1"  # 已升级全局


def test_verdict_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    DisciplineGuard(logger=log).check(_order(price=103.0), _ctx(surge_30min_pct=0.06))
    records = log.read_all()
    assert records[-1].event_type == "DISCIPLINE_VERDICT"
    assert records[-1].payload["behavior"] == "CHASING"


def test_custom_thresholds(tmp_path):
    """阈值可注入（校准通道）。"""
    t = DisciplineThresholds(chase_max_deviation=0.05)
    g = DisciplineGuard(thresholds=t, logger=ComplianceLogger(tmp_path / "c.jsonl"))
    v = g.check(_order(price=103.0), _ctx(surge_30min_pct=0.06))
    assert v.action is DisciplineAction.PASS
