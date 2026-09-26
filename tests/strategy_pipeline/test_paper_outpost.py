# [BLUEPRINT] MOD-BT-225 | docs/03_modules/_domain_backtest/blueprint.md | §模拟盘前哨（FAC-E7）
# [MODULE] tests.strategy_pipeline.test_paper_outpost
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; zephyr.strategy_pipeline.paper_outpost
# [CONSUMERS] paper_outpost 质量守卫（MODIFY-GUARD 锚）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——CH 全走注入假 q，registry/run 档案/判定台账全 monkeypatch
#   或 tmp_path 隔离；零真跑模拟盘/零网络/零 LLM
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-BT-225 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""E7 模拟盘前哨考核器单元测试（tmp_path+假数据替身，零真库依赖）。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.strategy_pipeline import paper_outpost as po  # noqa: E402

# ---------- 假数据替身 ----------

_REG_YAML = """\
strategies:
  - strategy_id: "STR-SIM-001"
    name_zh: "前哨甲"
    code_path: "scripts/backtest/x.py"
    lifecycle_status: "sim"
  - strategy_id: "STR-SIM-002"
    name_zh: "前哨乙"
    code_path: ""
    lifecycle_status: "paper"
  - strategy_id: "STR-CAND-003"
    name_zh: "仍在考试"
    code_path: ""
    lifecycle_status: "candidate"
"""


class FakeQ:
    """按 (sid, day) 供给 pocket/trade/kline 行的假 CH 客户端（零真库）。"""

    def __init__(self, pockets=None, trades=None, kline=None):
        self.pockets = pockets or {}  # (sid, day) -> [row]
        self.trades = trades or {}  # (sid, day) -> [(action, shares, price, cost)]
        self.kline = kline or {}  # (symbol, day) -> close
        self.calls: list[str] = []

    def __call__(self, sql: str):
        self.calls.append(sql)
        if "sim_pocket_daily" in sql:
            sid, day = re.search(r"strategy_id = '([^']+)' AND trade_date = '([^']+)'", sql).groups()
            return self.pockets.get((sid, day), [])
        if "sim_trade_log" in sql:
            sid, day = re.search(r"strategy_id = '([^']+)' AND trade_date = '([^']+)'", sql).groups()
            return self.trades.get((sid, day), [])
        if "GROUP BY trade_date" in sql:
            symbol, day, prev = re.search(
                r"symbol = '([^']+)' AND trade_date IN \('([^']+)', '([^']+)'\)", sql
            ).groups()
            px_d, px_p = self.kline.get((symbol, day)), self.kline.get((symbol, prev))
            if px_d is None or px_p is None:
                return []
            return [(px_p,), (px_d,)]
        raise AssertionError(f"假 q 未识别的 SQL: {sql[:80]}")


@pytest.fixture()
def reg_file(tmp_path: Path) -> Path:
    p = tmp_path / "strategy_registry.yaml"
    p.write_text(_REG_YAML, encoding="utf-8")
    return p


# ---------- 名单 ----------


def test_list_survivors_filters_observing_statuses(reg_file):
    out = po.list_survivors(registry_path=reg_file)
    assert [s["strategy_id"] for s in out] == ["STR-SIM-001", "STR-SIM-002"]
    assert {s["lifecycle_status"] for s in out} == {"sim", "paper"}


def test_list_survivors_statuses_override(reg_file):
    out = po.list_survivors(registry_path=reg_file, statuses=("candidate",))
    assert [s["strategy_id"] for s in out] == ["STR-CAND-003"]


def test_list_survivors_missing_file_raises(reg_file, tmp_path):
    with pytest.raises(OSError):
        po.list_survivors(registry_path=tmp_path / "nope.yaml")


# ---------- 窗口 ----------


def test_outpost_window_trading_days_ascending_end_inclusive():
    days = po.outpost_window("2026-09-25", 4)
    assert days == sorted(days) and days[-1] <= "2026-09-25"
    assert 15 <= len(days) <= 30  # 4 自然周内的 A 股交易日量级


def test_prev_trading_day_is_before_window_head():
    days = po.outpost_window("2026-09-25", 4)
    lead = po.prev_trading_day(days[0])
    assert lead is not None and lead < days[0]


# ---------- 逐日对账 ----------


def test_daily_deviation_no_pocket_row_is_honest_no_data():
    row = po.daily_deviation("STR-X", "2026-09-24", "2026-09-23", q=FakeQ())
    assert row == {"day": "2026-09-24", "has_data": False}


def test_daily_deviation_holding_day_reconciles():
    # 持仓日：前收 10.00 今收 10.15，10 万股，无交易，账面盈亏+15000 → 账实相符 dev=0
    q = FakeQ(
        pockets={("STR-X", "2026-09-24"): [["holding", 1015000.0, "510300", 100000.0, 15000.0]]},
        kline={("510300", "2026-09-24"): 10.15, ("510300", "2026-09-23"): 10.00},
    )
    row = po.daily_deviation("STR-X", "2026-09-24", "2026-09-23", q=q)
    assert row["has_data"] and row["signal"] == "holding"
    assert row["implied_pnl"] == pytest.approx(15000.0)
    assert row["dev"] == pytest.approx(0.0) and row["dev_ratio"] == 0.0


def test_daily_deviation_entry_day_cost_only():
    # 建仓日：收盘 10.0 买入 10 万股成本 25 元 → 隐含盈亏=-25 与账面 equity_change 一致
    q = FakeQ(
        pockets={("STR-X", "2026-09-24"): [["entry", 999975.0, "510300", 100000.0, -25.0]]},
        trades={("STR-X", "2026-09-24"): [("entry", 100000.0, 10.0, 25.0)]},
        kline={("510300", "2026-09-24"): 10.0, ("510300", "2026-09-23"): 10.0},
    )
    row = po.daily_deviation("STR-X", "2026-09-24", "2026-09-23", q=q)
    assert row["shares_prev_close"] == 0.0
    assert row["implied_pnl"] == pytest.approx(-25.0)
    assert row["dev_ratio"] == 0.0


def test_daily_deviation_px_missing_fail_visible():
    q = FakeQ(pockets={("STR-X", "2026-09-24"): [["holding", 1000000.0, "510300", 10.0, 0.0]]})
    row = po.daily_deviation("STR-X", "2026-09-24", "2026-09-23", q=q)
    assert row["px_missing"] is True and "dev_ratio" not in row


def test_daily_deviation_ledger_market_gap_breaches():
    # 账面记 +15000，行情只给 +5000（10.00→10.05）→ 偏差 10000/1000000=1%>0.1% 容忍线
    q = FakeQ(
        pockets={("STR-X", "2026-09-24"): [["holding", 1015000.0, "510300", 100000.0, 15000.0]]},
        kline={("510300", "2026-09-24"): 10.05, ("510300", "2026-09-23"): 10.00},
    )
    row = po.daily_deviation("STR-X", "2026-09-24", "2026-09-23", q=q)
    assert row["dev_ratio"] == pytest.approx(0.01)
    assert row["dev_ratio"] > po.DEV_TOL


# ---------- 期末判定（纯函数） ----------


def _row(day, has_data=True, **kw):
    return {"day": day, "has_data": has_data, **kw}


def test_summarize_insufficient_coverage_not_evaluable():
    rows = [_row(f"2026-09-{d:02d}") for d in range(1, 6)]  # 5/20 覆盖
    s = po.summarize(rows, 20)
    assert s["verdict"] == "not_evaluable" and s["ok"] is False
    assert s["recommendation"] == "extend_observation"


def test_summarize_pass_when_all_reconciled():
    rows = [_row(f"2026-09-{d:02d}", dev_ratio=0.0, cost_paid=1.0) for d in range(1, 21)]
    s = po.summarize(rows, 20)
    assert s["verdict"] == "pass" and s["recommendation"] == "continue_sim"
    assert s["metrics"]["total_cost_paid"] == 20.0


def test_summarize_fail_on_breach_and_px_missing():
    rows = [_row(f"2026-09-{d:02d}", dev_ratio=0.0) for d in range(1, 21)]
    rows[3]["dev_ratio"] = 0.5  # 单日爆表
    rows[7]["px_missing"] = True
    s = po.summarize(rows, 20)
    assert s["verdict"] == "fail" and s["recommendation"] == "demote_shelved"
    assert "账实偏差超限" in s["reason"] and "行情价缺失" in s["reason"]


# ---------- 合法边 ----------


def test_verify_demote_edge_sim_shelved_is_legal():
    assert po.verify_demote_edge("STR-ANY") is True


# ---------- 主流程（dry_run 全程零落册） ----------


def _full_q(sid="STR-SIM-001"):
    days = po.outpost_window("2026-09-25", 4)
    lead = po.prev_trading_day(days[0])
    pockets, kline = {}, {}
    if lead:
        kline[("510300", lead)] = 10.00
    for i, d in enumerate(days):
        pockets[(sid, d)] = [["holding", 1010000.0 * (i + 1) / 1, "510300", 100000.0, 10000.0]]
        kline[("510300", d)] = 10.10 + 0.10 * i  # 每日 +0.10 → 隐含盈亏=100000×0.10=10000=账面
    return FakeQ(pockets=pockets, kline=kline)


def test_run_outpost_dry_run_no_landing(monkeypatch, reg_file):
    monkeypatch.setattr(po, "REGISTRY", reg_file)
    calls = []
    monkeypatch.setattr("zephyr.backtest.run_archive.create_run", lambda *a, **k: calls.append("create"))
    out = po.run_outpost(end_day="2026-09-25", weeks=4, dry_run=True, q=_full_q())
    assert calls == []  # dry_run 零落册
    assert out["survivors"] == 2
    by_id = {r["strategy_id"]: r for r in out["reports"]}
    assert by_id["STR-SIM-001"]["verdict"] == "pass"
    assert by_id["STR-SIM-001"]["evidence"]["ok"] is True
    assert by_id["STR-SIM-001"]["evidence"]["source"]  # 三件套 source 在位
    # 前哨乙零账面（假 q 只给 STR-SIM-001 供数）→ not_evaluable 判不了不许放行
    assert by_id["STR-SIM-002"]["verdict"] == "not_evaluable"


def test_run_outpost_empty_registry_raises(monkeypatch, tmp_path):
    empty = tmp_path / "reg.yaml"
    empty.write_text("strategies: []\n", encoding="utf-8")
    monkeypatch.setattr(po, "REGISTRY", empty)
    with pytest.raises(RuntimeError, match="幸存者"):
        po.run_outpost(end_day="2026-09-25", dry_run=True, q=FakeQ())


def test_run_outpost_ids_filter(monkeypatch, reg_file):
    monkeypatch.setattr(po, "REGISTRY", reg_file)
    out = po.run_outpost(strategy_ids=["STR-SIM-002"], end_day="2026-09-25", dry_run=True, q=FakeQ())
    assert out["survivors"] == 1 and out["reports"][0]["strategy_id"] == "STR-SIM-002"


def test_run_outpost_lands_run_archive_and_ledger(monkeypatch, reg_file):
    monkeypatch.setattr(po, "REGISTRY", reg_file)
    landed = {}
    monkeypatch.setattr(
        "zephyr.backtest.run_archive.create_run",
        lambda run_id, object_id, kind, **k: landed.setdefault("run_id", run_id),
    )
    monkeypatch.setattr(
        "zephyr.backtest.run_archive.write_step",
        lambda run_id, step, content, **k: landed.setdefault("steps", []).append(step),
    )
    monkeypatch.setattr(
        "zephyr.backtest.run_archive.finalize_run", lambda run_id, **k: landed.setdefault("finalized", True)
    )
    ledger_rows = []
    monkeypatch.setattr("scripts.backtest.sim_daily_runner.write_report_row", lambda row: ledger_rows.append(row))
    out = po.run_outpost(end_day="2026-09-25", weeks=4, dry_run=False, q=_full_q())
    assert landed["finalized"] is True and landed["run_id"] == out["run_id"]
    assert "04" in landed["steps"] and "verdict" in landed["steps"]
    assert len(ledger_rows) == 2
    row = ledger_rows[0]
    assert row[1] == po.OUTPOST_SOURCE and row[17] == po.OUTPOST_SOURCE  # source/evaluated_by
    assert row[2] == "STR-SIM-001"
    payload = json.loads(row[6])
    assert payload["verdict"] == "pass" and payload["recommendation"] == "continue_sim"
