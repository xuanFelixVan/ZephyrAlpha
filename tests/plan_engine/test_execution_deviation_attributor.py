# [BLUEPRINT] MOD-PLAN-016 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-26 行）
# [MODULE] tests.plan_engine.test_execution_deviation_attributor
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.execution_deviation_attributor; zephyr.plan_engine.daily_trade_plan
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=执行偏差归因逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-PLAN-016_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-PLAN-016 执行偏差归因器 单元测试（GAP-F-26，合成计划+合成成交）。

覆盖：六类归因封闭（按计划/滑点/流动性/风控/拒单/未执行）、买卖双边滑点
恶化方向口径、部分成交流动性归类、多笔成交 VWAP 聚合、计划外成交留痕、
输入校验 fail-closed（计划须 DailyTradePlan/记录须 ExecutionRecord）、
汇总计数、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.plan_engine.daily_trade_plan import DailyTradePlan, TradePlanItem
from zephyr.plan_engine.execution_deviation_attributor import (
    CATEGORY_LIQUIDITY,
    CATEGORY_ON_PLAN,
    CATEGORY_REJECTED,
    CATEGORY_RISK_BLOCK,
    CATEGORY_SLIPPAGE,
    CATEGORY_UNFILLED,
    DeviationConfig,
    ExecutionRecord,
    VetoRecord,
    attribute_execution_deviation,
)


def _plan(buys: list[TradePlanItem], sells: list[TradePlanItem]) -> DailyTradePlan:
    return DailyTradePlan(
        date="2026-08-21",
        stance="NORMAL",
        position_scale=1.0,
        buy_list=tuple(buys),
        sell_list=tuple(sells),
        notes=(),
    )


def _buy(symbol: str, qty: int, price: float) -> TradePlanItem:
    return TradePlanItem(
        symbol=symbol,
        direction="BUY",
        quantity=qty,
        reference_price=price,
        logic="t",
        trigger_price=None,
        cap_weight=0.05,
    )


def _sell(symbol: str, qty: int, price: float) -> TradePlanItem:
    return TradePlanItem(
        symbol=symbol,
        direction="SELL",
        quantity=qty,
        reference_price=price,
        logic="t",
        trigger_price=price * 1.05,
        cap_weight=0.0,
    )


def _fill(
    symbol: str, direction: str, qty: int, price: float, status: str = "filled", reason: str = ""
) -> ExecutionRecord:
    return ExecutionRecord(
        symbol=symbol,
        direction=direction,
        filled_quantity=qty,
        avg_price=price,
        status=status,
        reason=reason,
    )


def _cfg(**kw) -> DeviationConfig:
    return DeviationConfig(**kw)


PLAN = _plan(
    buys=[_buy("600001.SH", 1000, 10.0), _buy("600002.SH", 500, 20.0), _buy("600003.SH", 800, 15.0)],
    sells=[_sell("000001.SZ", 600, 25.0), _sell("000002.SZ", 400, 30.0), _sell("000003.SZ", 300, 12.0)],
)


# ------------------------------------------------------------------
# 六类归因
# ------------------------------------------------------------------


def test_on_plan_when_full_fill_small_slippage() -> None:
    out = attribute_execution_deviation(PLAN, [_fill("600001.SH", "BUY", 1000, 10.02)], config=_cfg())
    item = next(i for i in out.items if i.symbol == "600001.SH")
    assert item.category == CATEGORY_ON_PLAN
    assert item.slippage_pct == pytest.approx(0.2, abs=1e-3)


def test_slippage_buy_adverse() -> None:
    out = attribute_execution_deviation(
        PLAN,
        [_fill("600001.SH", "BUY", 1000, 10.30)],
        config=_cfg(),  # +3% 买贵
    )
    item = next(i for i in out.items if i.symbol == "600001.SH")
    assert item.category == CATEGORY_SLIPPAGE
    assert item.slippage_pct == pytest.approx(3.0, abs=1e-3)


def test_slippage_sell_adverse_direction() -> None:
    out = attribute_execution_deviation(
        PLAN,
        [_fill("000001.SZ", "SELL", 600, 24.25)],
        config=_cfg(),  # 卖低 3%
    )
    item = next(i for i in out.items if i.symbol == "000001.SZ")
    assert item.category == CATEGORY_SLIPPAGE
    assert item.slippage_pct == pytest.approx(3.0, abs=1e-3)


def test_sell_favorable_price_is_on_plan() -> None:
    out = attribute_execution_deviation(
        PLAN,
        [_fill("000001.SZ", "SELL", 600, 25.30)],
        config=_cfg(),  # 卖高=有利
    )
    item = next(i for i in out.items if i.symbol == "000001.SZ")
    assert item.category == CATEGORY_ON_PLAN
    assert item.slippage_pct < 0


def test_liquidity_partial_fill() -> None:
    out = attribute_execution_deviation(PLAN, [_fill("600002.SH", "BUY", 200, 20.05, status="partial")], config=_cfg())
    item = next(i for i in out.items if i.symbol == "600002.SH")
    assert item.category == CATEGORY_LIQUIDITY
    assert item.filled_quantity == 200
    assert item.fill_ratio == pytest.approx(0.4)


def test_risk_block_via_veto() -> None:
    out = attribute_execution_deviation(
        PLAN, [], vetoes=[VetoRecord(symbol="600003.SH", reason="仓位上限拦截")], config=_cfg()
    )
    item = next(i for i in out.items if i.symbol == "600003.SH")
    assert item.category == CATEGORY_RISK_BLOCK
    assert "仓位上限" in item.note


def test_rejected_via_record() -> None:
    out = attribute_execution_deviation(
        PLAN, [_fill("000002.SZ", "SELL", 0, 0.0, status="rejected", reason="价格笼子")], config=_cfg()
    )
    item = next(i for i in out.items if i.symbol == "000002.SZ")
    assert item.category == CATEGORY_REJECTED
    assert "价格笼子" in item.note


def test_unfilled_no_trace() -> None:
    out = attribute_execution_deviation(PLAN, [], config=_cfg())
    item = next(i for i in out.items if i.symbol == "000003.SZ")
    assert item.category == CATEGORY_UNFILLED


def test_multi_fills_vwap_aggregated() -> None:
    out = attribute_execution_deviation(
        PLAN,
        [_fill("600001.SH", "BUY", 600, 10.0), _fill("600001.SH", "BUY", 400, 10.1)],
        config=_cfg(),
    )
    item = next(i for i in out.items if i.symbol == "600001.SH")
    assert item.filled_quantity == 1000
    assert item.avg_price == pytest.approx((600 * 10.0 + 400 * 10.1) / 1000)
    assert item.category == CATEGORY_ON_PLAN


def test_unplanned_execution_noted() -> None:
    out = attribute_execution_deviation(
        PLAN, [_fill("600001.SH", "BUY", 1000, 10.0), _fill("999999.SH", "BUY", 100, 5.0)], config=_cfg()
    )
    assert any("999999" in n for n in out.notes)


def test_summary_counts_and_values() -> None:
    out = attribute_execution_deviation(
        PLAN,
        [
            _fill("600001.SH", "BUY", 1000, 10.0),
            _fill("600002.SH", "BUY", 200, 20.0, status="partial"),
            _fill("000001.SZ", "SELL", 600, 24.0),
        ],
        vetoes=[VetoRecord(symbol="600003.SH", reason="风控")],
        config=_cfg(),
    )
    assert out.category_counts[CATEGORY_ON_PLAN] == 1
    assert out.category_counts[CATEGORY_LIQUIDITY] == 1
    assert out.category_counts[CATEGORY_SLIPPAGE] == 1  # 000001 卖低 4%
    assert out.category_counts[CATEGORY_RISK_BLOCK] == 1
    assert out.category_counts[CATEGORY_UNFILLED] == 2  # 000002/000003 无记录
    assert out.planned_count == 6
    assert out.executed_value > 0


def test_invalid_plan_fail_closed() -> None:
    with pytest.raises(ValueError, match="plan 非法"):
        attribute_execution_deviation("x", [], config=_cfg())  # type: ignore[arg-type]


def test_invalid_execution_fail_closed() -> None:
    with pytest.raises(ValueError, match="executions 元素非法"):
        attribute_execution_deviation(PLAN, ["x"], config=_cfg())  # type: ignore[list-item]


def test_json_serializable() -> None:
    out = attribute_execution_deviation(PLAN, [_fill("600001.SH", "BUY", 1000, 10.0)], config=_cfg())
    json.dumps(asdict(out), ensure_ascii=False)
