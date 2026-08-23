# [A_test] module_id: MOD-PLAN-014 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-014 | 待统筹登记 | 缺口总账 GAP-F-05 + 45号 §4 W5
# [MODULE] tests.plan_engine.test_sit_out_list
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""SitOutList (MOD-PLAN-014) 施工验证测试。

覆盖：
- 事件禁交易：blackout 级事件当日生效（market/sector/symbol 三 scope）；
  窗口期（event_date~end_date）覆盖判定；caution 级不进清单仅计数留痕；非当日不生效。
- 止损禁反手：当日止损标的 NO_REVERSE 条目；非当日止损不生效。
- 跌停不撬板：limit_down 标的 NO_BUY 条目。
- 池外不碰：war_pool 注入 → 毯式 OUT_OF_POOL 规则激活+池清单留痕；
  is_sit_out 池外标的命中、池内不命中；war_pool=None → 规则不激活。
- is_sit_out 综合查询：market 级事件全覆盖、symbol 级精确命中、action 过滤。
- 契约：to_dict JSON 可序列化；非法输入 fail-closed（日期/scope/severity/强度）。
全程内存构造，无 DB 无 CH。
"""

from __future__ import annotations

import json

import pytest

from zephyr.plan_engine.sit_out_list import (
    RULE_EVENT_BLACKOUT,
    RULE_LIMIT_DOWN_NO_DIP,
    RULE_OUT_OF_POOL,
    RULE_STOP_LOSS_NO_REVERSE,
    CalendarEvent,
    SitOutList,
    StoppedSymbol,
    build_sit_out_list,
)

TRADE_DATE = "2026-08-24"


def _event(**over) -> CalendarEvent:
    base = dict(
        event_date=TRADE_DATE,
        event_type="MACRO_FOMC",
        scope="market",
        target=None,
        severity="blackout",
        name="美联储议息决议",
    )
    base.update(over)
    return CalendarEvent(**base)


# ── 输入校验 ──


def test_event_date_invalid() -> None:
    with pytest.raises(ValueError):
        _event(event_date="2026/08/24")


def test_event_scope_invalid() -> None:
    with pytest.raises(ValueError):
        _event(scope="planet")


def test_event_severity_invalid() -> None:
    with pytest.raises(ValueError):
        _event(severity="panic")


def test_event_end_before_start() -> None:
    with pytest.raises(ValueError):
        _event(end_date="2026-08-20")


def test_stopped_symbol_invalid_date() -> None:
    with pytest.raises(ValueError):
        StoppedSymbol(symbol="600000.SH", stopped_at="not-a-date", reason="x")


def test_trade_date_invalid() -> None:
    with pytest.raises(ValueError):
        build_sit_out_list("20260824")


# ── 事件禁交易 ──


def test_blackout_market_event_same_day() -> None:
    result = build_sit_out_list(TRADE_DATE, events=[_event()])
    assert len(result.entries) == 1
    e = result.entries[0]
    assert e.rule == RULE_EVENT_BLACKOUT
    assert e.scope == "market"
    assert e.action == "NO_TRADE"
    assert "议息" in e.reason


def test_blackout_symbol_event() -> None:
    ev = _event(scope="symbol", target="600000.SH", event_type="EARNINGS_DISCLOSURE", name="财报披露日")
    result = build_sit_out_list(TRADE_DATE, events=[ev])
    assert result.entries[0].target == "600000.SH"
    assert result.is_sit_out("600000.SH") is True
    assert result.is_sit_out("600001.SH") is False


def test_event_window_coverage() -> None:
    ev = _event(event_date="2026-08-22", end_date="2026-08-25", name="交割周窗口")
    hit = build_sit_out_list(TRADE_DATE, events=[ev])
    assert len(hit.entries) == 1
    miss = build_sit_out_list("2026-08-26", events=[ev])
    assert len(miss.entries) == 0


def test_caution_event_not_sit_out_but_counted() -> None:
    ev = _event(severity="caution", name="宏观数据发布")
    result = build_sit_out_list(TRADE_DATE, events=[ev])
    assert len(result.entries) == 0
    assert any("caution" in n or "提示" in n for n in result.notes)


def test_market_scope_blanket_hit() -> None:
    result = build_sit_out_list(TRADE_DATE, events=[_event()])
    assert result.is_sit_out("600000.SH") is True  # market 级全覆盖
    assert result.is_sit_out("任何.SH") is True


# ── 止损禁反手 ──


def test_stop_loss_same_day_no_reverse() -> None:
    stopped = [StoppedSymbol(symbol="600000.SH", stopped_at=TRADE_DATE, reason="破必出价止损")]
    result = build_sit_out_list(TRADE_DATE, stopped_symbols=stopped)
    e = result.entries[0]
    assert e.rule == RULE_STOP_LOSS_NO_REVERSE
    assert e.action == "NO_REVERSE"
    assert e.target == "600000.SH"
    assert result.is_sit_out("600000.SH", action="NO_REVERSE") is True
    assert result.is_sit_out("600000.SH", action="NO_BUY") is False  # 禁反手≠禁买动作


def test_stop_loss_other_day_inactive() -> None:
    stopped = [StoppedSymbol(symbol="600000.SH", stopped_at="2026-08-21", reason="旧止损")]
    result = build_sit_out_list(TRADE_DATE, stopped_symbols=stopped)
    assert len(result.entries) == 0


# ── 跌停不撬板 ──


def test_limit_down_no_dip() -> None:
    result = build_sit_out_list(TRADE_DATE, limit_down_symbols=["600001.SH", "600002.SH"])
    assert len(result.entries) == 2
    assert all(e.rule == RULE_LIMIT_DOWN_NO_DIP for e in result.entries)
    assert all(e.action == "NO_BUY" for e in result.entries)
    assert result.is_sit_out("600001.SH", action="NO_BUY") is True


# ── 池外不碰 ──


def test_out_of_pool_blanket_rule() -> None:
    result = build_sit_out_list(TRADE_DATE, war_pool_symbols=["600001.SH", "600002.SH"])
    assert result.pool_rule_active is True
    assert result.is_sit_out("600099.SH") is True  # 池外
    assert result.is_sit_out("600001.SH") is False  # 池内
    pool_entries = [e for e in result.entries if e.rule == RULE_OUT_OF_POOL]
    assert len(pool_entries) == 1
    assert "2" in pool_entries[0].reason  # 池规模留痕


def test_empty_war_pool_means_all_sit_out() -> None:
    result = build_sit_out_list(TRADE_DATE, war_pool_symbols=[])
    assert result.pool_rule_active is True
    assert result.is_sit_out("600001.SH") is True  # 空池=全禁（池外不碰日）


def test_no_war_pool_rule_inactive() -> None:
    result = build_sit_out_list(TRADE_DATE)
    assert result.pool_rule_active is False
    assert result.is_sit_out("600099.SH") is False


# ── 合成与契约 ──


def test_three_sources_combined() -> None:
    result = build_sit_out_list(
        TRADE_DATE,
        events=[_event(scope="sector", target="880001.SH", name="行业政策窗口")],
        stopped_symbols=[StoppedSymbol(symbol="600000.SH", stopped_at=TRADE_DATE, reason="止损")],
        limit_down_symbols=["600003.SH"],
        war_pool_symbols=["600001.SH"],
    )
    rules = {e.rule for e in result.entries}
    assert rules == {RULE_EVENT_BLACKOUT, RULE_STOP_LOSS_NO_REVERSE, RULE_LIMIT_DOWN_NO_DIP, RULE_OUT_OF_POOL}


def test_to_dict_json_serializable() -> None:
    result = build_sit_out_list(
        TRADE_DATE,
        events=[_event()],
        war_pool_symbols=["600001.SH"],
    )
    payload = result.to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["trade_date"] == TRADE_DATE
    assert isinstance(result, SitOutList)
    assert payload["pool_symbols"] == ["600001.SH"]


def test_empty_list_annotations() -> None:
    result = build_sit_out_list(TRADE_DATE)
    assert result.entries == []
    assert any("空" in a or "无" in a for a in result.annotations)
