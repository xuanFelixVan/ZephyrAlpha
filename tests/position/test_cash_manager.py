# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""CashManager 单元测试 (MOD-POS-006)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.cash_manager import (
    CashFlow,
    CashFlowType,
    CashManager,
    CashReserveConfig,
    InvalidCashFlowError,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
INIT = 1_000_000.0


# ── 初始状态 ──────────────────────────────────────────────────────────────────


def test_initial_state():
    mgr = CashManager(initial_cash=INIT)
    state = mgr.compute_state(T0)
    assert state.total_cash == pytest.approx(INIT)
    assert state.pending_settlement == pytest.approx(0.0)
    assert state.available_cash == pytest.approx(INIT)
    # max_investable = 1M - 100K min - 100K opp = 800K
    assert state.max_investable == pytest.approx(800_000.0)


# ── T+1 结算约束 ──────────────────────────────────────────────────────────────


def test_buy_immediately_reduces_available():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_buy(200_000.0, T0)
    state = mgr.compute_state(T0)
    assert state.total_cash == pytest.approx(800_000.0)
    assert state.available_cash == pytest.approx(800_000.0)  # 买入立即扣减


def test_sell_t_plus_1_not_available_today():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_sell(100_000.0, T0)
    state = mgr.compute_state(T0)
    # total_cash 增加 100K (1.1M), 但 pending 100K, available 仍 1M
    assert state.total_cash == pytest.approx(1_100_000.0)
    assert state.pending_settlement == pytest.approx(100_000.0)
    assert state.available_cash == pytest.approx(1_000_000.0)


def test_settle_releases_pending():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_sell(100_000.0, T0)
    mgr.settle()  # 次交易日
    state = mgr.compute_state(T0)
    assert state.pending_settlement == pytest.approx(0.0)
    assert state.available_cash == pytest.approx(1_100_000.0)  # 卖出资金现可用


def test_multiple_sells_accumulate_pending():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_sell(100_000.0, T0)
    mgr.record_sell(50_000.0, T0)
    state = mgr.compute_state(T0)
    assert state.pending_settlement == pytest.approx(150_000.0)


# ── 存取 ──────────────────────────────────────────────────────────────────────


def test_deposit_increases_cash():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_deposit(500_000.0, T0)
    state = mgr.compute_state(T0)
    assert state.total_cash == pytest.approx(1_500_000.0)
    assert state.available_cash == pytest.approx(1_500_000.0)


def test_withdrawal_decreases_cash():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_withdrawal(200_000.0, T0)
    state = mgr.compute_state(T0)
    assert state.total_cash == pytest.approx(800_000.0)


# ── 储备金 ────────────────────────────────────────────────────────────────────


def test_min_reserve_deducted():
    mgr = CashManager(initial_cash=INIT, config=CashReserveConfig(min_reserve=200_000.0, opportunity_reserve_ratio=0.0))
    state = mgr.compute_state(T0)
    assert state.max_investable == pytest.approx(800_000.0)  # 1M - 200K


def test_opportunity_reserve_ratio():
    cfg = CashReserveConfig(min_reserve=0.0, opportunity_reserve_ratio=0.20)
    mgr = CashManager(initial_cash=INIT, config=cfg)
    state = mgr.compute_state(T0)
    assert state.opportunity_reserve == pytest.approx(200_000.0)  # 20% of 1M
    assert state.max_investable == pytest.approx(800_000.0)


def test_holiday_mode_adds_reserve():
    mgr = CashManager(initial_cash=INIT)
    normal = mgr.compute_state(T0, in_holiday_mode=False)
    holiday = mgr.compute_state(T0, in_holiday_mode=True)
    assert holiday.holiday_reserve > 0
    assert normal.holiday_reserve == pytest.approx(0.0)
    assert holiday.max_investable < normal.max_investable


def test_max_investable_never_negative():
    # 储备超过可用时 max_investable = 0
    cfg = CashReserveConfig(min_reserve=2_000_000.0, opportunity_reserve_ratio=0.0)
    mgr = CashManager(initial_cash=INIT, config=cfg)
    state = mgr.compute_state(T0)
    assert state.max_investable == pytest.approx(0.0)


# ── 复合场景 ──────────────────────────────────────────────────────────────────


def test_combined_buy_sell_and_settle():
    mgr = CashManager(initial_cash=INIT)
    mgr.record_buy(300_000.0, T0)  # total 700K, available 700K
    mgr.record_sell(200_000.0, T0)  # total 900K, pending 200K, available 700K
    state1 = mgr.compute_state(T0)
    assert state1.total_cash == pytest.approx(900_000.0)
    assert state1.available_cash == pytest.approx(700_000.0)
    mgr.settle()  # 释放 200K
    state2 = mgr.compute_state(T0)
    assert state2.available_cash == pytest.approx(900_000.0)


def test_total_reserve_property():
    mgr = CashManager(initial_cash=INIT)
    state = mgr.compute_state(T0, in_holiday_mode=True)
    assert state.total_reserve == pytest.approx(state.min_reserve + state.opportunity_reserve + state.holiday_reserve)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_flow_amount_must_be_positive():
    mgr = CashManager(initial_cash=INIT)
    with pytest.raises(InvalidCashFlowError):
        mgr.record(CashFlow(CashFlowType.DEPOSIT, -100.0, T0))


def test_initial_cash_must_be_non_negative():
    with pytest.raises(InvalidCashFlowError):
        CashManager(initial_cash=-1.0)


def test_config_ratio_range():
    with pytest.raises(InvalidCashFlowError):
        CashReserveConfig(opportunity_reserve_ratio=1.5)


# ── 可配置 ────────────────────────────────────────────────────────────────────


def test_custom_config():
    cfg = CashReserveConfig(min_reserve=50_000.0, opportunity_reserve_ratio=0.05, holiday_reserve_ratio=0.15)
    mgr = CashManager(initial_cash=INIT, config=cfg)
    state = mgr.compute_state(T0, in_holiday_mode=True)
    assert state.min_reserve == pytest.approx(50_000.0)
    assert state.opportunity_reserve == pytest.approx(50_000.0)  # 5% of 1M
    assert state.holiday_reserve == pytest.approx(150_000.0)  # 15% of 1M
    assert state.max_investable == pytest.approx(750_000.0)  # 1M - 50K - 50K - 150K


# ── 逆回购收益增强 (B10-01307 / CAND-POS-003, W-P1-20 扩展) ─────────────────────

from zephyr.position.core.cash_manager import (  # noqa: E402
    DEFAULT_REVERSE_REPO_POOL,
    CashFlowType as _CFT,
    FundTransferLedger,
    ScheduledTransfer,
)


def test_reverse_repo_pool_default():
    pool = DEFAULT_REVERSE_REPO_POOL
    assert len(pool) >= 8
    exchanges = {i.exchange for i in pool}
    assert exchanges == {"SH", "SZ"}
    assert all(i.term_days in (1, 2, 3, 4, 7) for i in pool)


def test_plan_reverse_repo_normal_day():
    mgr = CashManager(initial_cash=INIT)  # max_investable = 800K
    plan = mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=0.5)
    assert plan is not None
    assert plan.amount == pytest.approx(400_000.0)  # 800K × 0.5
    assert plan.interest_days == plan.term_days  # 非节假日: 计息=期限
    assert plan.expected_interest == pytest.approx(plan.amount * 0.02 * plan.term_days / 365)


def test_plan_reverse_repo_holiday_prefers_one_day_with_extra_interest():
    mgr = CashManager(initial_cash=INIT)
    plan = mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=0.5,
                                 in_holiday_mode=True, holiday_extra_days=6)
    assert plan is not None
    # 节假日: 1天期计息 1+6=7 天 > 7天期计息7天(同息取短) → 选1天期
    assert plan.term_days == 1
    assert plan.interest_days == 7


def test_plan_reverse_repo_respects_max_investable():
    mgr = CashManager(initial_cash=INIT)
    state = mgr.compute_state(T0)
    plan = mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=1.0)
    assert plan is not None
    assert plan.amount <= state.max_investable + 1e-9


def test_plan_reverse_repo_no_investable_returns_none():
    cfg = CashReserveConfig(min_reserve=2_000_000.0, opportunity_reserve_ratio=0.0)
    mgr = CashManager(initial_cash=INIT, config=cfg)  # max_investable = 0
    assert mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=0.5) is None


def test_plan_reverse_repo_invalid_params():
    mgr = CashManager(initial_cash=INIT)
    with pytest.raises(InvalidCashFlowError):
        mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=0.0)
    with pytest.raises(InvalidCashFlowError):
        mgr.plan_reverse_repo(T0, annualized_rate=-0.01, max_ratio=0.5)
    with pytest.raises(InvalidCashFlowError):
        mgr.plan_reverse_repo(T0, annualized_rate=0.02, max_ratio=0.5, holiday_extra_days=-1)


# ── 出入金台账 (B10-01307 / CAND-POS-003, W-P1-20 扩展) ─────────────────────────

from datetime import date as _date  # noqa: E402

D1 = _date(2026, 8, 3)
D2 = _date(2026, 8, 4)


def test_ledger_schedule_and_entries():
    ledger = FundTransferLedger()
    ledger.schedule(ScheduledTransfer(_CFT.DEPOSIT, 100_000.0, D1, "工资入金"))
    ledger.schedule(ScheduledTransfer(_CFT.WITHDRAWAL, 50_000.0, D2, "还贷"))
    entries = ledger.entries()
    assert len(entries) == 2
    assert entries[0].amount == pytest.approx(100_000.0)


def test_ledger_rejects_buy_sell():
    ledger = FundTransferLedger()
    with pytest.raises(InvalidCashFlowError):
        ledger.schedule(ScheduledTransfer(_CFT.BUY, 100.0, D1))


def test_ledger_rejects_nonpositive_amount():
    ledger = FundTransferLedger()
    with pytest.raises(InvalidCashFlowError):
        ledger.schedule(ScheduledTransfer(_CFT.DEPOSIT, 0.0, D1))


def test_projected_available_with_transfers():
    mgr = CashManager(initial_cash=INIT)  # available 1M
    mgr.schedule_transfer(_CFT.DEPOSIT, 100_000.0, D1, "入金")
    mgr.schedule_transfer(_CFT.WITHDRAWAL, 50_000.0, D1, "出金")
    projected = mgr.projected_available(D1, T0)
    assert projected == pytest.approx(1_050_000.0)


def test_projected_available_ignores_future_transfers():
    mgr = CashManager(initial_cash=INIT)
    mgr.schedule_transfer(_CFT.DEPOSIT, 100_000.0, D2, "后天生效")
    projected = mgr.projected_available(D1, T0)  # target=D1 < D2
    assert projected == pytest.approx(1_000_000.0)
    projected2 = mgr.projected_available(D2, T0)
    assert projected2 == pytest.approx(1_100_000.0)
