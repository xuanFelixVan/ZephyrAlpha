# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md | §plan-execute 风控闸
# [MODULE] tests.backtest.test_sim_plan_execute_risk_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_daily_runner; zephyr.shared.state_store
# [CONSUMERS] 整装回测备战W1 风控接线质量守卫（sim_daily_runner plan-execute 风控闸：
#   _evaluate_sim_risk 六态机唯一仲裁+kill switch 禁旁路+熔断清算台账行落 _write_observe）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——state_dir 全 tmp_path；DB 面（_q/_row_by_id/
#   _plan_position/write_report_row/_write_observe）全 monkeypatch，零真实库接触
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/backtest/test_sim_plan_execute_risk_gate.py
# 覆盖（[整装回测备战W1] 验收 3 测）：25% 回撤序列→当日禁开仓+kill_switch_liquidation
#   台账行落 _write_observe/健康放行零误拦。
# 铁律：不连真实券商、不连任何业务数据库、不写 data/ 生产路径。
import json
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "backtest"))

import sim_daily_runner as runner  # noqa: E402

from zephyr.shared.state_store import JsonStateStore  # noqa: E402

_DAY = "2026-09-28"
# plan_bridge 判定行（subject=index:000300.SH，posture=long_proxy 进攻建仓）
_PLAN_ROW = [
    date.fromisoformat(_DAY),
    "plan_bridge",
    "index:000300.SH",
    runner.make_judgment_id(_DAY, "plan_bridge", "index:000300.SH"),
    f"{_DAY} 07:00:00",
    f"{_DAY} 07:00:00",
    json.dumps({"posture": "long_proxy", "posture_reason": "action=trend_follow_no_chase 可机械执行"}),
    0.8,
    "judgment_daily_plan:X",
    "test-run",
    0,
    None,
    None,
    None,
    None,
    None,
    None,
    "",
]


def _wire_db(monkeypatch, *, cash: float = 1_000_000.0, shares: float = 0.0):
    """DB 面全替身：plan 行在册/000300 ret_1d=0（不追高通过）/ETF 收盘 4.0/台账面捕获。"""
    captured = {"report_rows": [], "observe": []}
    monkeypatch.setattr(runner, "_row_by_id", lambda day, source, subject: list(_PLAN_ROW))
    monkeypatch.setattr(runner, "_plan_position", lambda cid: (cash, shares, cash + shares * 4.0, True))
    monkeypatch.setattr(runner, "write_report_row", lambda row: captured["report_rows"].append(row))
    monkeypatch.setattr(runner, "_write_observe", lambda pocket, events: captured["observe"].append((pocket, events)))

    def _fake_q(sql: str):
        if "510300%" in sql:  # SQL_PLAN_ETF_CLOSE：ETF 收盘价
            return [(4.0,)]
        return [  # SQL_PLAN_INDEX_2D：000300 今收=昨收 → ret_1d=0（<1.5% 不追高通过）
            (date.fromisoformat(_DAY), 4000.0, 4000.0),
            ("2026-09-14", 4000.0, 4000.0),
        ]

    monkeypatch.setattr(runner, "_q", _fake_q)
    return captured


# ── 测1：25% 回撤序列 → 当日禁开仓 ──


def test_drawdown_25pct_sequence_blocks_new_entry_that_day(monkeypatch, tmp_path):
    """dd 26%>kill_dd 25% → 六态机 KILL 合流 kill switch → plan-execute 当日禁开仓。"""
    captured = _wire_db(monkeypatch)
    state_dir = tmp_path / "state"
    risk = runner._evaluate_sim_risk(_DAY, drawdown_pct=0.26, state_dir=state_dir)
    assert risk["state"] == "KILL"
    assert risk["kill_switch_active"] is True  # 单一仲裁点合流（禁旁路）
    assert risk["allow_new_position"] is False
    out = runner.plan_execute(_DAY, state_dir=state_dir)
    assert out["executed"] is False
    assert out["why"] == "risk_blocked"
    # 落 risk_blocked 判定行（当日禁开仓留痕）
    row = captured["report_rows"][-1]
    assert row[1] == "plan_execute"
    payload = json.loads(row[6])
    assert payload["action"] == "risk_blocked" and payload["risk_blocked"] is True
    # 零开仓：无 entry 事件落 observe
    assert all(ev[3] != "entry" for _p, evs in captured["observe"] for ev in evs)


# ── 测2：kill_switch_liquidation 台账行落 _write_observe ──


def test_kill_switch_liquidation_ledger_rows_written_via_write_observe(monkeypatch, tmp_path):
    """KILL+有仓钱包 → 清算腿 exit 事件与 kill_switch_liquidation 钱包行落 _write_observe。"""
    captured = _wire_db(monkeypatch, cash=400_000.0, shares=150_000.0)
    state_dir = tmp_path / "state"
    runner._evaluate_sim_risk(_DAY, drawdown_pct=0.30, state_dir=state_dir)  # → KILL
    out = runner.plan_execute(_DAY, state_dir=state_dir)
    assert out["why"] == "risk_blocked"
    assert out["liquidation"] is not None and out["liquidation"]["liquidated"] is True
    assert len(captured["observe"]) == 1  # 恰一次 _write_observe（清算台账，无普通成交）
    pocket, events = captured["observe"][0]
    assert pocket[9] == "kill_switch_liquidation"  # 钱包行 signal 列
    assert pocket[5] == 0.0  # 清算后零持仓
    assert len(events) == 1
    assert events[0][2] == "510300" and events[0][3] == "exit"  # 事件行=平仓 exit
    assert str(events[0][8]).startswith("kill_switch_liquidation")  # reason 留痕


# ── 测3：健康放行零误拦 ──


def test_healthy_state_passes_through_with_zero_false_block(monkeypatch, tmp_path):
    """NORMAL+无熔断 → plan-execute 正常 entry 执行，零 risk_blocked 误拦。"""
    captured = _wire_db(monkeypatch)
    out = runner.plan_execute(_DAY, state_dir=tmp_path / "state")
    assert out["executed"] is True
    assert out["action"] == "entry"  # long_proxy+ret_1d=0<1.5%+空仓 → 正常建仓
    assert out.get("why") != "risk_blocked"
    payload = json.loads(captured["report_rows"][-1][6])
    assert payload["action"] == "entry"
    assert payload.get("risk_blocked") is None
    pocket, events = captured["observe"][-1]
    assert pocket[9] == "entry" and len(events) == 1  # 健康放行零误拦
