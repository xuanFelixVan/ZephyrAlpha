# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md | §模拟盘判定台账
# [MODULE] tests.backtest.test_sim_daily_runner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_daily_runner; scripts.backtest.sim_platform_journal
# [CONSUMERS] 模拟盘接电件质量守卫（MODIFY-GUARD: sim_daily_runner/sim_daily_report 表结构）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——CH 写入函数全 monkeypatch，tmp_path 隔离；零真库依赖
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/backtest/test_sim_daily_runner.py
# 覆盖：sim_daily_runner 纯函数+三平面（monkeypatch CH 面，零生产写入）；
#       sim_platform_journal.expected_fresh_date 时点感知（FIX-1 R3）；
#       sim_paper_ledger.ensure_wallet 注册表 SSOT 卫兵（FIX-2 R5）。
# 铁律：测试禁写生产路径——CH 写入函数全 monkeypatch，tmp_path 隔离。
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "backtest"))

import sim_daily_runner as runner  # noqa: E402
import sim_platform_journal as journal  # noqa: E402

# ---------- judgment_id / posture 纯函数 ----------


def test_make_judgment_id_deterministic_and_colon_stripped():
    a = runner.make_judgment_id("2026-09-22", "plan_bridge", "index:000300.SH")
    b = runner.make_judgment_id("2026-09-22", "plan_bridge", "index:000300.SH")
    assert a == b == "SIMP-2026-09-22-plan_bridge-index000300.SH"


def test_posture_for_action_defense_is_flat():
    posture, reason = runner.posture_for_action("stand_aside_defense")
    assert posture == "flat" and "可机械执行" in reason


def test_posture_for_action_unmapped_is_unexecutable():
    # 2026-09-22 委托裁定后：进攻=long_proxy（30% 额度+不追高 1.5%），震荡仍无订单语义
    posture, _ = runner.posture_for_action("trend_follow_no_chase")
    assert posture == "long_proxy"
    for action in ("range_fade_extremes", "unknown_x"):
        posture, reason = runner.posture_for_action(action)
        assert posture == "unexecutable"
        assert "action_not_order_mapped" in reason


def test_state_to_scenario_partial_mapping():
    assert runner.STATE_TO_SCENARIO["防御"] == "S2_defense"
    assert runner.STATE_TO_SCENARIO["进攻"] == "S1_attack"
    assert runner.STATE_TO_SCENARIO["震荡"] == "S3_oscillation"
    # 低迷/亢奋不在计划三场景树内 → 部分映射（如实记 no_matching_scenario，不硬凑）
    assert runner.STATE_TO_SCENARIO.get("亢奋") is None
    assert runner.STATE_TO_SCENARIO.get("低迷") is None


# ---------- plan-bridge 平面（CH 面 monkeypatch） ----------


def _plan_obj():
    return {
        "judgment_id": "01PLAN",
        "asof_ts": "2026-09-20 01:00:00",
        "cutoff": "x",
        "payload": {
            "scenarios": [
                {"scenario_id": "S1_attack", "action": "trend_follow_no_chase"},
                {"scenario_id": "S2_defense", "action": "stand_aside_defense"},
            ]
        },
        "confidence": 0.9,
        "subject": "index:000300.SH",
    }


def test_plan_bridge_unclassified_is_pending(monkeypatch):
    monkeypatch.setattr(runner, "fetch_plan", lambda day: _plan_obj())
    monkeypatch.setattr(runner, "fetch_realized_state", lambda day: None)
    captured = {}
    monkeypatch.setattr(runner, "write_report_row", lambda row: captured.setdefault("row", row))
    out = runner.plan_bridge("2026-09-21")
    assert out["written"] and out["posture"] == "pending_unclassified"
    row = captured["row"]
    assert row[1] == "plan_bridge" and row[10] == 0  # synthetic 恒 0
    assert row[2] == "index:000300.SH"


def test_plan_bridge_defense_state_translates_flat(monkeypatch):
    monkeypatch.setattr(runner, "fetch_plan", lambda day: _plan_obj())
    monkeypatch.setattr(
        runner, "fetch_realized_state", lambda day: {"judgment_id": "01ST", "asof_ts": "x", "state_label": "防御"}
    )
    captured = {}
    monkeypatch.setattr(runner, "write_report_row", lambda row: captured.setdefault("row", row))
    out = runner.plan_bridge("2026-09-21")
    assert out["posture"] == "flat" and out["realized_scenario"] == "S2_defense"


def test_plan_bridge_attack_state_is_unexecutable(monkeypatch):
    monkeypatch.setattr(runner, "fetch_plan", lambda day: _plan_obj())
    monkeypatch.setattr(
        runner, "fetch_realized_state", lambda day: {"judgment_id": "01ST", "asof_ts": "x", "state_label": "进攻"}
    )
    out = runner.plan_bridge("2026-09-21")
    assert out["posture"] == "long_proxy"


def test_plan_bridge_no_plan_no_write(monkeypatch):
    monkeypatch.setattr(runner, "fetch_plan", lambda day: None)
    monkeypatch.setattr(runner, "write_report_row", lambda row: pytest.fail("无计划日禁止落行"))
    assert runner.plan_bridge("2026-09-21")["written"] is False


# ---------- e4-replay 平面 ----------


def test_e4_candidates_match_translated_files(monkeypatch, tmp_path):
    # 表名 SSoT 接线后候选清单复用 forward_post.fetch_passers（patch 其返回，不触真库）
    import forward_post

    monkeypatch.setattr(
        forward_post, "fetch_passers", lambda limit: ["CAND-aaaa0001", "CAND-bbbb0002", "CAND-cccc0003"]
    )
    fake_dir = tmp_path / "translated"
    fake_dir.mkdir()
    (fake_dir / "c4_aaaa0001_pairs.py").write_text("def build(s, e):\n    return None, None\n")
    (fake_dir / "c4_other9999_x.py").write_text("")
    monkeypatch.setattr(runner, "_TRANSLATED_DIR", fake_dir)
    cands = runner.e4_candidates()
    assert [c[0] for c in cands] == ["CAND-aaaa0001"]
    assert cands[0][1].name == "c4_aaaa0001_pairs.py"


def test_replay_one_entry_math_and_fresh_wallet_funding(monkeypatch, tmp_path):
    # 假翻译件：尾行目标仓位 1.0，价格 100.0
    mod_src = (
        "import pandas as pd\n"
        "def build(start, end):\n"
        "    idx = pd.Index([end])\n"
        "    w = pd.DataFrame(1.0, index=idx, columns=['000999'])\n"
        "    p = pd.DataFrame(100.0, index=idx, columns=['000999'])\n"
        "    return w, p\n"
    )
    mod_path = tmp_path / "c4_fake0001_test.py"
    mod_path.write_text(mod_src)
    monkeypatch.setattr(runner, "_observe_position", lambda cid: (0.0, 0.0, "", runner._OBSERVE_NOTIONAL, False))
    captured = {}
    monkeypatch.setattr(runner, "_write_observe", lambda pocket, events: captured.update(pocket=pocket, events=events))
    res = runner.replay_one("CAND-fake0001", mod_path, "2026-09-21", "run-x")
    assert res["signal"] == "entry" and res["events"] == 1
    ev = captured["events"][0]
    expected_shares = runner._OBSERVE_NOTIONAL / 100.0 * (1 - runner.BUY_COST)
    assert abs(ev[4] - expected_shares) < 1e-6  # shares=现金/价*(1-成本)
    assert ev[2] == "000999" and ev[3] == "entry" and ev[9] == "sim_observe"
    pocket = captured["pocket"]
    assert pocket[10] == "sim_observe"
    assert abs(pocket[7] - expected_shares * 100.0) < 1e-6  # equity=持股市值（全仓现金耗尽）


def test_replay_one_flat_wallet_gets_notional_not_zero(monkeypatch, tmp_path):
    mod_src = (
        "import pandas as pd\n"
        "def build(start, end):\n"
        "    idx = pd.Index([end])\n"
        "    return pd.DataFrame(0.0, index=idx, columns=['000999']), pd.DataFrame(1.0, index=idx, columns=['000999'])\n"
    )
    mod_path = tmp_path / "c4_fake0002_test.py"
    mod_path.write_text(mod_src)
    # 既有 bug 态自愈：cash=0 空仓 → 按名义本金补足
    monkeypatch.setattr(runner, "_observe_position", lambda cid: (0.0, 0.0, "", 0.0, True))
    captured = {}
    monkeypatch.setattr(runner, "_write_observe", lambda pocket, events: captured.update(pocket=pocket, events=events))
    res = runner.replay_one("CAND-fake0002", mod_path, "2026-09-21", "run-y")
    assert res["signal"] == "cash" and res["events"] == 0
    assert captured["pocket"][7] == runner._OBSERVE_NOTIONAL  # equity=1M，非 0 假死


def test_e4_replay_all_fail_is_fail_closed(monkeypatch):
    monkeypatch.setattr(runner, "e4_candidates", lambda: [("CAND-x", Path("nope.py"))])
    with pytest.raises(RuntimeError, match="fail-closed"):
        runner.e4_replay("2026-09-21", 5)


# ---------- settle ----------


def test_settle_posture_check_scores_match(monkeypatch):
    payload_json = '{"posture": "flat", "posture_reason": "action=stand_aside_defense 可机械执行"}'
    rows = [
        [
            "2026-09-21",
            "plan_bridge",
            "index:000300.SH",
            "SIMP-X",
            "asof",
            "cut",
            payload_json,
            0.9,
            "refs",
            "run",
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            "",
        ]
    ]
    monkeypatch.setattr(runner, "_q", lambda sql: rows)
    monkeypatch.setattr(runner, "_row_by_id", lambda d, s, sub: rows[0])
    monkeypatch.setattr(
        runner, "fetch_realized_state", lambda d: {"judgment_id": "01ST", "asof_ts": "x", "state_label": "防御"}
    )
    captured = {}
    monkeypatch.setattr(runner, "write_report_row", lambda row: captured.setdefault("row", row))
    out = runner.settle("2026-09-22")
    assert out["settled"] == 1
    row = captured["row"]
    assert row[17] == "sim_settler" and row[14] == "posture_check" and row[15] == 1.0


def test_settle_unmappable_state_is_unresolvable(monkeypatch):
    payload_json = '{"posture": "pending_owner_mapping"}'
    rows = [
        [
            "2026-09-21",
            "plan_bridge",
            "index:000300.SH",
            "SIMP-Y",
            "asof",
            "cut",
            payload_json,
            0.9,
            "refs",
            "run",
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            "",
        ]
    ]
    monkeypatch.setattr(runner, "_q", lambda sql: rows)
    monkeypatch.setattr(runner, "_row_by_id", lambda d, s, sub: rows[0])
    monkeypatch.setattr(
        runner, "fetch_realized_state", lambda d: {"judgment_id": "01ST", "asof_ts": "x", "state_label": "亢奋"}
    )
    captured = {}
    monkeypatch.setattr(runner, "write_report_row", lambda row: captured.setdefault("row", row))
    out = runner.settle("2026-09-22")
    assert out["unresolvable"] == 1
    assert captured["row"][14] == "unresolvable" and captured["row"][15] is None


# ---------- journal 探针时点感知（FIX-1） ----------


def test_expected_fresh_date_trading_day_morning_wants_prev():
    morning = datetime(2026, 9, 21, 8, 42, tzinfo=timezone(timedelta(hours=8)))
    assert journal.expected_fresh_date("2026-09-21", morning) == "2026-09-18"


def test_expected_fresh_date_after_close_wants_same_day():
    evening = datetime(2026, 9, 21, 16, 0, tzinfo=timezone(timedelta(hours=8)))
    assert journal.expected_fresh_date("2026-09-21", evening) == "2026-09-21"


def test_expected_fresh_date_non_trading_day_and_history():
    morning = datetime(2026, 9, 21, 8, 42, tzinfo=timezone(timedelta(hours=8)))
    past = datetime(2026, 9, 22, 2, 0, tzinfo=timezone(timedelta(hours=8)))
    assert journal.expected_fresh_date("2026-09-20", morning) == "2026-09-20"
    assert journal.expected_fresh_date("2026-09-15", past) == "2026-09-15"


# ---------- plan_execute 决策纯函数（② 裁定施工件） ----------


def test_plan_decision_matrix():
    """② 裁定施工件语义矩阵：进攻 30% 建仓+1.5% 不追高+亢奋减半+防御空仓。"""
    d = runner._plan_decision
    # 进攻：空仓且不追高通过 → entry；≥1.5% → wait；已持仓 → hold（不因追高卖出）
    assert d("long_proxy", False, 0.010, True) == "entry"
    assert d("long_proxy", False, 0.020, True) == "wait"
    assert d("long_proxy", True, 0.020, True) == "hold"
    # 阈值数据缺失=观望（fail-visible 不赌）；价格缺失=none（不下单）
    assert d("long_proxy", False, None, True) == "wait"
    assert d("long_proxy", False, 0.010, False) == "none"
    # 防御：持仓→exit；已空仓→none
    assert d("flat", True, 0.0, True) == "exit"
    assert d("flat", False, 0.0, True) == "none"
    # 亢奋减半：持仓→trim_half；空仓→none
    assert d("trim_half", True, 0.0, True) == "trim_half"
    assert d("trim_half", False, 0.0, True) == "none"
    # 未映射姿态：一律 none（不伪造）
    assert d("pending_owner_mapping", False, 0.010, True) == "none"
    assert d("pending_unclassified", True, 0.010, True) == "none"


def test_no_chase_threshold_is_one_point_five_pct():
    assert runner.NO_CHASE_MAX_RET_1D == 0.015
    assert runner.PLAN_ENTRY_FRACTION == 0.30
    assert runner.PLAN_POCKET_ID == "SIM-PLAN-001"
    assert runner.PLAN_SYMBOL == "510300"
