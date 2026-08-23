# [BLUEPRINT] MOD-RK-24 | docs/03_modules/MOD-RK-24/ | §test
# [MODULE] tests.risk.core.test_risk_veto_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.risk_veto_engine
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_risk_veto_engine.py
# [A_test] module_id: MOD-RK-24 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-24 单元测试: RiskVetoEngine — 风险否决引擎。

覆盖: 硬规则清单（缺价/停牌/T+1/超持仓卖出/单仓限额/总杠杆/限额缺失）、
优先级排序、结构化否决理由、规则异常 fail-closed、自定义规则注入、
非法请求校验。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.risk_veto_engine",
    reason="risk_veto_engine not importable",
)

from zephyr.risk.core.risk_data_pipeline import (  # noqa: E402
    RiskSnapshotInput,
    assemble_risk_snapshot,
)
from zephyr.risk.core.risk_veto_engine import (  # noqa: E402
    InvalidVetoRequestError,
    OrderRiskRequest,
    RiskVetoEngine,
    evaluate_vetoes,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide  # noqa: E402
from zephyr.shared.contracts.market_data import NormalizedMarketData  # noqa: E402
from zephyr.shared.contracts.position import PositionSnapshot  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402

_NOW = datetime(2026, 8, 21, 14, 0, tzinfo=UTC)

# ── 夹具 ─────────────────────────────────────────────────────────────


def _quote(symbol: str, close: str, *, suspended: bool = False) -> NormalizedMarketData:
    return NormalizedMarketData(
        symbol=symbol,
        timestamp=_NOW,
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=Decimal("1000"),
        data_source="stub",
        idempotency_key=f"q-{symbol}",
        is_suspended=suspended,
    )


def _snapshot(
    *,
    holdings: dict[str, str] | None = None,
    prices: dict[str, str] | None = None,
    cash: str = "100000",
    limits: RiskLimits | None = None,
    suspended: tuple[str, ...] = (),
    sellable: dict[str, str] | None = None,
):
    holdings = holdings or {}
    prices = prices or {}
    if limits is None:
        limits = RiskLimits(
            as_of_date=_NOW,
            idempotency_key="lim-1",
            max_single_position=0.10,
            max_gross_leverage=1.0,
        )
    pos = PositionSnapshot(
        portfolio_id="pf-1",
        as_of_timestamp=_NOW,
        idempotency_key="pos-1",
        cash=Decimal(cash),
        holdings={s: Decimal(q) for s, q in holdings.items()},
        market_values={},
        total_market_value=Decimal("0"),
    )
    quotes = {
        s: _quote(s, p, suspended=(s in suspended)) for s, p in prices.items()
    }
    return assemble_risk_snapshot(
        RiskSnapshotInput(
            position_snapshot=pos,
            quotes=quotes,
            fills=(),
            limits=limits,
            as_of=_NOW,
            sellable_quantities=(
                {s: Decimal(v) for s, v in sellable.items()} if sellable else None
            ),
        )
    )


def _request(
    symbol: str = "600519.SH",
    side: OrderSide = OrderSide.BUY,
    quantity: str = "10",
    price: str | None = "1700",
) -> OrderRiskRequest:
    return OrderRiskRequest(
        symbol=symbol,
        side=side,
        quantity=Decimal(quantity),
        price=Decimal(price) if price is not None else None,
        strategy_id="st-1",
    )


# ── 硬规则: 放行路径 ─────────────────────────────────────────────────


class TestApprovePath:
    def test_small_buy_approved(self):
        # nav=100000+17000=117000, 买 10*1700=17000 → post weight≈0.15>0.10? 重算:
        # 现持仓 600519 10股 mv=17000, 再买 5 股 mv+8500 → 25500/117000≈0.218 超限
        # 用小额: 买 1 股 → 18700/117000≈0.16 仍超限 → 调限额 0.3
        limits = RiskLimits(
            as_of_date=_NOW, idempotency_key="lim-x",
            max_single_position=0.30, max_gross_leverage=1.0,
        )
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"}, limits=limits,
        )
        decision = evaluate_vetoes(_request(quantity="1"), snap)
        assert decision.approved
        assert decision.vetoes == ()
        assert decision.rules_evaluated > 0

    def test_sell_within_position_approved(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="5"), snap,
        )
        assert decision.approved

    def test_decision_immutable(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(_request(side=OrderSide.SELL, quantity="5"), snap)
        with pytest.raises(AttributeError):
            decision.approved = False  # type: ignore[misc]


# ── 硬规则: 否决路径 ─────────────────────────────────────────────────


class TestVetoRules:
    def test_single_position_limit_veto(self):
        # 持仓 10 股 mv=17000, nav=117000; 买 5 股 → 25500/117000≈0.218 > 0.10
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(_request(quantity="5"), snap)
        assert not decision.approved
        codes = [v.reason_code for v in decision.vetoes]
        assert "SINGLE_POSITION_LIMIT" in codes

    def test_symbol_override_limit(self):
        # override 0.25: post weight 0.218 < 0.25 → 单仓规则放行
        limits = RiskLimits(
            as_of_date=_NOW, idempotency_key="lim-1",
            max_single_position=0.10, max_gross_leverage=1.0,
            symbol_overrides={"600519.SH": 0.25},
        )
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"}, limits=limits,
        )
        decision = evaluate_vetoes(_request(quantity="5"), snap)
        codes = [v.reason_code for v in decision.vetoes]
        assert "SINGLE_POSITION_LIMIT" not in codes

    def test_gross_leverage_veto(self):
        # 已满仓附近: mv=90000 cash=10000 nav=100000 leverage 0.9;
        # 买 20 股 (+34000) → post leverage 1.24 > 1.0
        limits = RiskLimits(
            as_of_date=_NOW, idempotency_key="lim-1",
            max_single_position=0.95, max_gross_leverage=1.0,
        )
        snap = _snapshot(
            holdings={"600519.SH": "52"}, prices={"600519.SH": "1700"},
            cash="11600", limits=limits,
        )
        # nav=11600+88400=100000; post mv=88400+34000=122400 → 1.224
        decision = evaluate_vetoes(_request(quantity="20"), snap)
        codes = [v.reason_code for v in decision.vetoes]
        assert "GROSS_LEVERAGE_LIMIT" in codes

    def test_sell_exceeds_position_veto(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="20"), snap,
        )
        codes = [v.reason_code for v in decision.vetoes]
        assert "SELL_EXCEEDS_POSITION" in codes

    def test_sell_unheld_symbol_veto(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(
            _request(symbol="000001.SZ", side=OrderSide.SELL, quantity="1", price="15"),
            snap,
        )
        codes = [v.reason_code for v in decision.vetoes]
        assert "SELL_EXCEEDS_POSITION" in codes

    def test_t1_sellable_exceeded_veto(self):
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"},
            sellable={"600519.SH": "4"},
        )
        decision = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="6"), snap,
        )
        codes = [v.reason_code for v in decision.vetoes]
        assert "T1_SELLABLE_EXCEEDED" in codes

    def test_t1_sellable_sufficient_passes(self):
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"},
            sellable={"600519.SH": "10"},
        )
        decision = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="6"), snap,
        )
        codes = [v.reason_code for v in decision.vetoes]
        assert "T1_SELLABLE_EXCEEDED" not in codes

    def test_suspended_symbol_veto_both_sides(self):
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"},
            suspended=("600519.SH",),
        )
        for side in (OrderSide.BUY, OrderSide.SELL):
            decision = evaluate_vetoes(
                _request(side=side, quantity="1"), snap,
            )
            codes = [v.reason_code for v in decision.vetoes]
            assert "SUSPENDED_SYMBOL" in codes

    def test_missing_price_veto(self):
        # 持仓但无行情 → 缺价; 该标的新订单一律否决
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={})
        decision = evaluate_vetoes(_request(quantity="1"), snap)
        codes = [v.reason_code for v in decision.vetoes]
        assert "MISSING_PRICE" in codes

    def test_limits_unavailable_vetoes_buy_allows_sell(self):
        snap = _snapshot(
            holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"},
            limits=None,
        )
        # _snapshot 默认补 limits; 显式造 limits=None 快照
        pos = PositionSnapshot(
            portfolio_id="pf-1", as_of_timestamp=_NOW, idempotency_key="pos-1",
            cash=Decimal("83000"),
            holdings={"600519.SH": Decimal("10")},
            market_values={}, total_market_value=Decimal("0"),
        )
        snap = assemble_risk_snapshot(
            RiskSnapshotInput(
                position_snapshot=pos,
                quotes={"600519.SH": _quote("600519.SH", "1700")},
                fills=(), limits=None, as_of=_NOW,
            )
        )
        buy = evaluate_vetoes(_request(quantity="1"), snap)
        assert "LIMITS_UNAVAILABLE" in [v.reason_code for v in buy.vetoes]
        sell = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="5"), snap,
        )
        assert sell.approved  # 减仓放行（风险收敛方向不拦）

    def test_vetoes_sorted_by_priority(self):
        # 同时触发 MISSING_PRICE(优先级高) 与其他规则时按优先级升序
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={})
        decision = evaluate_vetoes(
            _request(side=OrderSide.SELL, quantity="100"), snap,
        )
        priorities = [v.priority for v in decision.vetoes]
        assert priorities == sorted(priorities)
        assert len(decision.vetoes) >= 2  # MISSING_PRICE + SELL_EXCEEDS_POSITION

    def test_verdict_structure(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = evaluate_vetoes(_request(quantity="50"), snap)
        verdict = decision.vetoes[0]
        assert verdict.rule_id
        assert verdict.reason_code
        assert verdict.message
        assert isinstance(verdict.priority, int)


# ── 引擎编排 ─────────────────────────────────────────────────────────


class _ExplodingRule:
    rule_id = "exploding"
    priority = 5

    def check(self, request, snapshot):
        raise RuntimeError("boom")


class TestEngineOrchestration:
    def test_rule_exception_fail_closed(self):
        engine = RiskVetoEngine(rules=[_ExplodingRule()])
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        decision = engine.evaluate(_request(quantity="1"), snap)
        assert not decision.approved
        assert decision.vetoes[0].reason_code == "RULE_ERROR"
        assert decision.vetoes[0].rule_id == "exploding"

    def test_default_rules_loaded(self):
        engine = RiskVetoEngine()
        assert len(engine.rules) >= 5

    def test_invalid_quantity_raises(self):
        snap = _snapshot()
        with pytest.raises(InvalidVetoRequestError):
            evaluate_vetoes(_request(quantity="0"), snap)

    def test_negative_price_raises(self):
        snap = _snapshot()
        with pytest.raises(InvalidVetoRequestError):
            evaluate_vetoes(_request(quantity="1", price="-3"), snap)

    def test_decision_carries_ids(self):
        snap = _snapshot(holdings={"600519.SH": "10"}, prices={"600519.SH": "1700"})
        req = _request(side=OrderSide.SELL, quantity="1")
        decision = evaluate_vetoes(req, snap)
        assert decision.snapshot_id == snap.snapshot_id
        assert decision.request_id == req.request_id
