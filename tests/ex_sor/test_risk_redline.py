# [BLUEPRINT] MOD-AUTO-L6-001(暂编号) | docs/_working/automation/campaign/blueprints/risk_redline_blueprint.md | §测试
# [MODULE] tests.ex_sor.test_risk_redline
# [DOMAIN] D_EX_SOR
# [INVARIANTS] 纯函数合成数据直喷，零 IO 零时钟（宪法 §9.6）
# [TTL] permanent
"""risk_redline 红线引擎测试：黄线/日线红线/周月红线/黑天鹅缓冲/回测最差日倍数。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.ex_sor.risk_redline import DayRecord, RedlineConfig, evaluate  # noqa: E402

CFG = RedlineConfig()


def test_empty_records_no_actions():
    assert evaluate([], CFG) == []


def test_yellow_then_red_daily():
    recs = [DayRecord("2026-09-01", -0.025), DayRecord("2026-09-02", -0.05)]
    acts = evaluate(recs, CFG)
    assert acts[0].level == "YELLOW" and acts[0].rule == "daily_yellow"
    # -5% 单日触日线红线；同周累计 -7.5% 同日触发周红线（周月线前置不被 continue 吞）
    rules = [(a.date, a.rule) for a in acts]
    assert ("2026-09-02", "daily_red") in rules and ("2026-09-02", "weekly_red") in rules


def test_backtest_worst_day_multiple_triggers_red():
    recs = [DayRecord("2026-09-01", -0.03)]
    acts = evaluate(recs, CFG, backtest_worst_day=0.012)  # 0.03 ≥ 0.012*2 → RED
    assert acts[0].level == "RED" and "回测最差日" in acts[0].detail


def test_blackswan_grace_window():
    recs = [
        DayRecord("2026-09-01", -0.06, market_crash=True),   # 市场性暴跌→GRACE 开窗
        DayRecord("2026-09-02", -0.05, market_crash=True),   # 窗内暂缓（月线 -11% 照触发）
        DayRecord("2026-09-03", -0.05, market_crash=True),   # 超窗→日线 RED
    ]
    acts = evaluate(recs, CFG)
    assert acts[0].level == "GRACE" and acts[0].rule == "blackswan_buffer"
    assert any(a.rule == "monthly_red" for a in acts)  # 月线不被 GRACE 吞（红队 P1-3 修复）
    assert acts[-1].level == "RED" and acts[-1].rule == "daily_red"


def test_market_crash_grace_only_once():
    recs = [
        DayRecord("2026-09-01", -0.06, market_crash=True),
        DayRecord("2026-09-02", -0.02),  # 非市场性轻亏：episode 结束，窗自动关
        DayRecord("2026-09-03", -0.05),  # 非市场性红线：直接 RED，无窗可开
    ]
    acts = evaluate(recs, CFG)
    assert sum(1 for a in acts if a.level == "GRACE") == 1  # 缓冲窗全 episode 只开一次
    assert acts[-1].level == "RED"


def test_weekly_red():
    recs = [DayRecord("2026-09-01", -0.02), DayRecord("2026-09-02", -0.02), DayRecord("2026-09-03", -0.015)]
    acts = evaluate(recs, CFG)
    # 前两日各黄线，第三日周累计 -5.5% → weekly_red
    assert any(a.rule == "weekly_red" for a in acts)


def test_monthly_red():
    recs = [DayRecord("2026-09-01", -0.034), DayRecord("2026-09-08", -0.034), DayRecord("2026-09-15", -0.034)]
    acts = evaluate(recs, CFG)
    # 单日 3.4% 只触黄线；月累计 -10.2% 触月红线
    assert any(a.rule == "monthly_red" for a in acts)


def test_gains_produce_no_actions():
    recs = [DayRecord("2026-09-01", 0.03), DayRecord("2026-09-02", 0.01)]
    assert evaluate(recs, CFG) == []
