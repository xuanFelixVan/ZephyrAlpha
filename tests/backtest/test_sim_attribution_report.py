# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_attribution_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_attribution_report
# [CONSUMERS] 收益归因例行件质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 纯函数+fake CH（monkeypatch fetch_*）合成数据测试，不依赖真库；
#   输出一律 tmp_path（测试隔离，禁写生产路径）；成本口径对 sim_paper_ledger 记账函数断言
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-217 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_attribution_report 质量守卫——成本口径一致性/replay 幂等(RMT)/risk_contrib=100%。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_attribution_report", _REPO / "scripts" / "backtest" / "sim_attribution_report.py")
sar = importlib.util.module_from_spec(spec)
sys.modules["sim_attribution_report"] = sar
spec.loader.exec_module(sar)

LEDGER = sar._load_ledger()

BUY = LEDGER.BUY_COST   # (2.5+5.0)/10000 —— 口径真源在账本，逐字一致=import 同一常量
SELL = LEDGER.SELL_COST  # (2.5+10.0+5.0)/10000


# ---------------------------------------------------------------- 合成账本（fake CH 底座）
def _row(d: str, **kw) -> dict:
    base = {"trade_date": d, "strategy_id": "STR-X", "initial_capital": 1_000_000.0,
            "cash": 1_000_000.0, "position_symbol": "", "shares": 0.0,
            "position_value": 0.0, "equity": 1_000_000.0, "daily_pnl": 0.0,
            "signal": "cash", "mode": "replay_demo", "run_id": "r1", "note": ""}
    base.update(kw)
    return base


def _fake_pocket() -> list[dict]:
    """5 天主链（entry/holding/exit 全信号）+ 2 天旁链开户行，含 1 个多策略日。"""
    shares = 1_000_000.0 / 7168.0 * (1 - BUY)  # 与账本 entry 公式同款
    return [
        _row("2026-08-03"),
        # entry 日：equity=100万*(1-BUY)，pnl=-buy_cost（账本口径：成本即日入损益）
        _row("2026-08-04", cash=0.0, position_symbol="000852", shares=shares,
             position_value=round(shares * 7168.0, 2), equity=round(1_000_000 * (1 - BUY), 2),
             daily_pnl=-round(1_000_000 * BUY, 2), signal="entry"),
        # holding 日：涨 1%
        _row("2026-08-05", cash=0.0, position_symbol="000852", shares=shares,
             position_value=round(shares * 7239.68, 2), equity=round(shares * 7239.68, 2),
             daily_pnl=round(shares * (7239.68 - 7168.0), 2), signal="holding"),
        # exit 日：账本行是平仓后快照（shares 归零），notional=1000 股×1050（事件口径）
        # prev equity(08-05)=999250×1.01=1,009,242.50 → daily_pnl=38,920.00（链自洽）
        _row("2026-08-06", cash=1_048_162.50, equity=1_048_162.50,
             daily_pnl=38_920.00, signal="exit"),
        _row("2026-08-07", cash=1_048_162.50, equity=1_048_162.50),
        # 旁链：开户行（多策略日 08-06 并存）
        _row("2026-08-06", strategy_id="STR-Y", mode="sim_daily", signal="open"),
        _row("2026-08-07", strategy_id="STR-Y", mode="sim_daily", signal="open"),
    ]


def _fake_events() -> dict:
    return {
        ("STR-X", "2026-08-04", "entry"): {
            "symbol": "000852", "shares": 1_000_000.0 / 7168.0 * (1 - BUY),
            "price": 7168.0, "cost_paid": round(1_000_000 * BUY, 6), "cash_after": 0.0},
        ("STR-X", "2026-08-06", "exit"): {
            "symbol": "000852", "shares": 1000.0, "price": 1050.0,
            "cost_paid": 1000.0 * 1050.0 * SELL, "cash_after": 1_048_162.50},
    }


def _fake_closes() -> dict:
    return {
        "000852": {f"2026-08-{d:02d}": float(v) for d, v in
                   zip(range(3, 8), (100.0, 101.0, 102.0, 103.0, 104.0))},
        "000300": {f"2026-08-{d:02d}": float(v) for d, v in
                   zip(range(3, 8), (200.0, 200.5, 201.0, 201.5, 202.0))},
    }


@pytest.fixture()
def fake_ch(monkeypatch):
    monkeypatch.setattr(sar, "fetch_pocket_rows", _fake_pocket)
    monkeypatch.setattr(sar, "fetch_trade_events", _fake_events)
    monkeypatch.setattr(sar, "fetch_benchmark_closes",
                        lambda symbols, d0, d1: {s: _fake_closes()[s] for s in symbols})


# ---------------------------------------------------------------- 1) 成本口径一致性
def test_cost_constants_are_ledger_import_not_copy():
    """口径铁律：归因件成本常量必须与账本记账代码同一来源（import，非复制非 config）。"""
    assert BUY == (2.5 + 5.0) / 10000.0
    assert SELL == (2.5 + 10.0 + 5.0) / 10000.0
    # 账本记账函数口径断言：entry buy_cost=cash*BUY_COST；exit cost=shares*px*SELL_COST
    assert abs(1_000_000 * BUY - 750.0) < 1e-9
    assert abs(1000.0 * 1050.0 * SELL - 1837.5) < 1e-9
    # 账本无佣金地板（¥5 地板是做T config 口径，账本路径未实现——归因件同样不引入）
    assert abs(LEDGER.INITIAL_CAPITAL - 1_000_000.0) < 1e-9


def test_cost_of_day_matches_ledger_accounting():
    """entry/exit 单日成本复算 = 账本公式逐位一致；非交易日=0。"""
    chains = sar.build_chains(_fake_pocket())
    chain = chains[("STR-X", "replay_demo")]
    events = _fake_events()
    dec = sar.decompose_chain(chain, events, LEDGER)
    by_sig = {d["_signal"]: d for d in dec}
    assert by_sig["entry"]["pnl_cost"] == pytest.approx(1_000_000 * BUY, abs=1e-6)
    assert by_sig["exit"]["pnl_cost"] == pytest.approx(1000.0 * 1050.0 * SELL, abs=1e-6)
    assert by_sig["cash"]["pnl_cost"] == 0.0
    assert by_sig["holding"]["pnl_cost"] == 0.0
    # 三元分解加总回归成本总额（佣金+滑点+冲击=总成本）
    for d in dec:
        b = d["_cost_breakdown"]
        assert b["commission"] + b["slippage"] + b["impact"] == pytest.approx(d["pnl_cost"], abs=1e-6)


def test_cost_drift_fails_closed():
    """红蓝预登记硬检查：trade_log.cost_paid 与常量复算漂移 >0.01 元 → fail-closed。"""
    chains = sar.build_chains(_fake_pocket())
    events = _fake_events()
    events[("STR-X", "2026-08-06", "exit")]["cost_paid"] += 1.0  # 篡改 1 元
    with pytest.raises(RuntimeError, match="成本口径漂移"):
        sar.decompose_chain(chains[("STR-X", "replay_demo")], events, LEDGER)


# ---------------------------------------------------------------- 2) replay 幂等（RMT 语义）
def test_replay_reconciles_and_is_idempotent(fake_ch, tmp_path):
    """回放对平：sum(pnl_net)=账本 daily_pnl 加总（差=0）；重跑行数不变、逐字节同 TSV。"""
    out1 = sar.replay()
    out2 = sar.replay()
    r1 = out1["recon"]
    assert r1["rows_attrib"] == r1["rows_ledger"] == 7
    assert r1["recon_diff"] == 0.0
    assert r1["identity_check"] == 0.0  # gross-cost-net 恒等
    assert r1["continuity_issues"] == []
    # 幂等：重跑 recon 数字不变 + 行集全等（RMT 同键覆盖语义，行数不增）
    assert {k: r1[k] for k in ("rows_ledger", "attrib_net_sum", "gross_sum", "cost_sum")} == \
        {k: out2["recon"][k] for k in ("rows_ledger", "attrib_net_sum", "gross_sum", "cost_sum")}
    assert out1["rows"] == out2["rows"]
    # TSV 确定性（INSERT 幂等的物理前提），输出进 tmp_path（测试隔离）
    p1, p2 = tmp_path / "a.tsv", tmp_path / "b.tsv"
    p1.write_text(sar.rows_to_tsv(out1["rows"]), encoding="utf-8")
    p2.write_text(sar.rows_to_tsv(out2["rows"]), encoding="utf-8")
    assert p1.read_bytes() == p2.read_bytes()


def test_replay_idempotent_row_count_under_same_key_rewrite(fake_ch):
    """同 (strategy_id, trade_date) 重复产出归因行 → 行数不变（ReplacingMergeTree FINAL 视图）。"""
    rows1 = sar.replay()["rows"]
    rows2 = sar.replay()["rows"]
    keys1 = {(r["strategy_id"], r["trade_date"]) for r in rows1}
    keys2 = {(r["strategy_id"], r["trade_date"]) for r in rows2}
    assert len(rows1) == len(rows2) == len(keys1)  # 无重复键
    assert keys1 == keys2


# ---------------------------------------------------------------- 3) risk_contrib
def test_risk_contrib_single_strategy_is_100_percent(fake_ch):
    """单策略期 risk_contrib=100%（sanity check 内建：每日合计=1.0 fail-closed）。"""
    rows = sar.replay()["rows"]
    by_date: dict[str, list] = {}
    for r in rows:
        by_date.setdefault(r["trade_date"], []).append(r)
    single = [d for d, rs in by_date.items() if len(rs) == 1]
    assert single, "夹具必须含单策略日"
    for d in single:
        assert by_date[d][0]["risk_contrib"] == 1.0


def test_risk_contrib_multi_strategy_sums_to_one(fake_ch):
    """多策略日（开户行并存）占位 1/N 且合计=1.0，占位标记入 detail。"""
    rows = sar.replay()["rows"]
    multi = [r for r in rows if r["trade_date"] == "2026-08-06"]
    assert len(multi) == 2
    assert sum(r["risk_contrib"] for r in multi) == pytest.approx(1.0)
    for r in multi:
        assert json.loads(r["detail"])["risk_contrib_placeholder"] is True


# ---------------------------------------------------------------- 4) 四段答案完整性
def test_benchmark_rel_and_missing_markers(fake_ch):
    """benchmark_rel=策略日收益-000852 日收益；缺数日 NaN→None+missing 标记；次基准入 detail。"""
    rows = sar.replay()["rows"]
    d = {r["trade_date"]: r for r in rows if r["strategy_id"] == "STR-X"}
    r0805 = d["2026-08-05"]
    strat_ret = 9_992.50 / 999_250.00
    b852 = 102.0 / 101.0 - 1
    assert r0805["benchmark_rel"] == pytest.approx(strat_ret - b852, abs=1e-9)
    assert json.loads(r0805["detail"])["benchmark_rel_hs300"] is not None
    # 窗口首日无前收 → 结构性缺基准
    assert d["2026-08-03"]["benchmark_rel"] is None
    assert json.loads(d["2026-08-03"]["detail"])["benchmark_missing"] is True


def test_replay_hard_fails_on_broken_chain(fake_ch, monkeypatch):
    """链连续性漂移（equity 差分≠daily_pnl）→ fail-closed（对不平即不许出报告）。"""
    bad = _fake_pocket()
    for r in bad:
        if r["trade_date"] == "2026-08-05" and r["strategy_id"] == "STR-X":
            r["daily_pnl"] += 5.0  # 破坏 equity 链
    monkeypatch.setattr(sar, "fetch_pocket_rows", lambda: bad)
    with pytest.raises(RuntimeError, match="链连续性漂移"):
        sar.replay()
