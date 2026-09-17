# [BLUEPRINT] MOD-CD-001 | tests/backtest/test_cash_ledger_cli_wiring.py
# [MODULE] tests.backtest.test_cash_ledger_cli_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.run_backtest; zephyr.backtest.core.portfolio
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] E2（S1-T1）：CLI run_one 产物 metrics 必含 cash_ledger_reconciliation
#   （schema=cash_ledger_reconciliation/v1，复用 reconcile_cash_ledger 真源）；
#   缺 cash_history → within_tolerance=False（fail-closed）；删一笔成交的注入反例
#   必须翻 False（不红=对账器假绿）。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/backtest/test_cash_ledger_cli_wiring.py
# [TTL] permanent
"""E2 CLI 现金对账接线钉测试（GT-15 结构闸同族，不触 CH/不写生产路径）。

判据（S12 规格 §E2 写死）：
- run_one 产物 metrics 增 cash_ledger_reconciliation（结构钉：源码接线点存在 +
  helper 行为钉）；
- 缺 cash_history → fail-closed False；
- 反例=删掉一笔成交后必须 within_tolerance=False。
"""

from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from zephyr.backtest.core.portfolio import reconcile_cash_ledger


def _load_run_backtest():
    """按路径加载 scripts/run_backtest.py（同 test_h3h4 GT-15 的 spec 加载姿势）。"""
    path = Path(__file__).resolve().parents[2] / "scripts" / "run_backtest.py"
    spec = importlib.util.spec_from_file_location("run_backtest_under_test_e2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _good_portfolio(pd_module):
    """闭合账本替身：初始 10 万，买 100 股@100 佣金 5（total_cost=10005）→ 现金 89995。"""
    d1 = pd_module.Timestamp("2026-01-05")
    d2 = pd_module.Timestamp("2026-01-06")
    return SimpleNamespace(
        cash_history=[(None, Decimal("100000")), (d1, Decimal("89995")), (d2, Decimal("89995"))],
        trades_log=[
            {
                "date": d1,
                "symbol": "600519",
                "side": "BUY",
                "price": 100.0,
                "quantity": 100,
                "commission": 5.0,
                "total_cost": 10005.0,
            }
        ],
        initial_capital=Decimal("100000"),
    )


class _FakeEngine:
    def __init__(self, portfolio) -> None:
        self.last_portfolio = portfolio


def test_cli_reconciliation_helper_closes_good_ledger() -> None:
    """闭合账本 → within_tolerance=True 且 schema 正确（CLI helper 直钉）。"""
    rb = _load_run_backtest()
    recon = rb._cash_ledger_reconciliation(_FakeEngine(_good_portfolio(pd)))
    assert recon["schema"] == "cash_ledger_reconciliation/v1"
    assert recon["within_tolerance"] is True
    assert float(recon["max_abs_residual"]) <= 0.01


def test_cli_reconciliation_missing_cash_history_fail_closed() -> None:
    """缺 cash_history / 缺引擎 → within_tolerance=False（fail-closed，禁静默缺字段）。"""
    rb = _load_run_backtest()
    empty_pf = SimpleNamespace(cash_history=[], trades_log=[], initial_capital=Decimal("100000"))
    assert rb._cash_ledger_reconciliation(_FakeEngine(empty_pf))["within_tolerance"] is False
    assert rb._cash_ledger_reconciliation(None)["within_tolerance"] is False
    no_portfolio = rb._cash_ledger_reconciliation(SimpleNamespace(last_portfolio=None))
    assert no_portfolio["within_tolerance"] is False


def test_cli_reconciliation_counterexample_dropped_trade_red() -> None:
    """注入反例：删掉一笔成交后重算必须 within_tolerance=False（不红=假绿）。

    规格验收反例（§E2）：删掉一笔成交后重跑必须 False。本钉在 helper 层复现
    同一语义（真 CLI 反例=冒烟节手工验证，见 lane_reports/E.md）。
    """
    rb = _load_run_backtest()
    pf = _good_portfolio(pd)
    tampered = SimpleNamespace(
        cash_history=pf.cash_history,
        trades_log=[],  # 删掉唯一一笔买入（现金快照 89995 已含其效应）
        initial_capital=pf.initial_capital,
    )
    recon = rb._cash_ledger_reconciliation(_FakeEngine(tampered))
    assert recon["within_tolerance"] is False, "删一笔成交后仍闭合=对账器假绿"


def test_run_one_wires_reconciliation_into_artifact_metrics() -> None:
    """结构钉：run_one 产物装配段必须把 cash_ledger_reconciliation 写进 artifact.metrics。

    GT-15 名册只管时序键；本键是 dict 章，走独立断言（防"造了没落"同族回归）。
    """
    import inspect

    rb = _load_run_backtest()
    src = inspect.getsource(rb.run_one)
    assert 'artifact.metrics["cash_ledger_reconciliation"]' in src, (
        "run_one 未把 cash_ledger_reconciliation 写进 artifact.metrics（接线被移除=静默回退）"
    )
    assert "_cash_ledger_reconciliation(" in src


def test_reconcile_truth_source_unchanged_semantics() -> None:
    """真源钉：reconcile_cash_ledger 对空样本 fail-closed（CLI helper 依赖此语义）。"""
    recon = reconcile_cash_ledger([], [], Decimal("100000"))
    assert recon["within_tolerance"] is False
