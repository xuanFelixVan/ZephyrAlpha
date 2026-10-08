# [MODULE] tests.strategy_pipeline.test_redblue
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.*; tests.strategy_pipeline.test_intake
# [CONSUMERS] 完成标准③红蓝对抗（伪造事件/FSM 越权/FDR 挑尾/并发双触发/KillSwitch/CAS 冲突
#   +收尾清欠扩展：毒丸正门/重放风控闸禁旁路）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 红队姿势必须全拦；测试隔离零生产 IO；本件=跨模块对抗套件，不声明单一 module_id
#   （守卫对象=MOD-BT-189/190/192 三件，module_id 各归其主文件+主测试）
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [TTL] permanent
"""红蓝对抗——C6 管线新代码八姿势（完成标准③+收尾清欠扩展）。发现即修复的历史：见各用例注释。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import intake  # noqa: E402
from zephyr.strategy_pipeline import pipeline_events as pe
from zephyr.strategy_pipeline.bh_fdr import bh_filter  # noqa: E402
from zephyr.strategy_pipeline.lifecycle_fsm import (  # noqa: E402
    PRODUCTION,
    build_strategy_fsm,
)


class TestRedBlue:
    def test_1_forged_event_replay_zero_diff(self, tmp_path, monkeypatch):
        """红：同一 c4_batch_completed 事件伪造重放两次。蓝：第二次全 skipped、created 零新增。"""
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: True)
        reg_store = {"strategies": []}
        monkeypatch.setattr(intake, "_load_registry", lambda: reg_store)
        item = {
            "key": "CAND-x@c4_x.py",
            "source_file": "scripts/backtest/translated/c4_x.py",
            "is_sharpe": 1.0,
            "turnover": 0.2,
            "max_drawdown": -0.1,
            "segments": [{"batch": "OOS", "sharpe": 0.4, "decay": 0.1}],
        }
        passed = {"CAND-x@c4_x.py": 0.001}
        r1 = intake.run_intake("E1", passed, {}, dry_run=True, items=[item])
        assert len(r1["created_sids"]) == 1
        # 把第一次的产物写进"注册表"（模拟第一次真实落库）
        for e in r1["created"]:
            reg_store["strategies"].append({"strategy_id": e["strategy_id"], "code_path": e["code_path"]})
        r2 = intake.run_intake("E1", passed, {}, dry_run=True, items=[item])
        assert r2["created_sids"] == [] and "已入库" in r2["skipped"]["CAND-x@c4_x.py"]

    def test_2_fsm_forbidden_direct_jump(self):
        """红：candidate→production 越权直跳。蓝：必抛 InvalidTransitionError。"""
        fsm = build_strategy_fsm("STR-RB-001")
        with pytest.raises(Exception) as ei:
            fsm.transition(PRODUCTION, {})
        assert "InvalidTransition" in type(ei.value).__name__

    def test_3_fdr_tail_cherry_rejected(self):
        """红：挑尾（尾档 p 单独看达标，但步进断点在其前）。蓝：beyond last pass 必拒。
        （BHY 依赖稳健校正上线后会话 st-patmine：常相关语境阈值更保守，整体语义只会更严。）"""
        keep, report = bh_filter({"a": 0.02, "b": 0.5, "c": 0.09}, q=0.10)
        assert "c" not in keep  # 尾档挑尾必拒
        assert report["c"]["passed"] is False

    def test_3b_fdr_null_family_all_rejected(self):
        """红：真 H0 均匀族伪造"总有几个看着显著"。蓝：BH 全拒。"""
        passed = {f"CAND-{i}": (i + 1) / 20 for i in range(20)}
        keep, _ = bh_filter(passed, q=0.10)
        assert keep == set()

    def test_4_concurrent_double_trigger_idempotent(self, tmp_path, monkeypatch):
        """红：同批事件并发双触发（两条同 payload 事件先后消费）。蓝：第二次零副作用。"""
        monkeypatch.setattr(pe, "STATE_DIR", tmp_path)
        monkeypatch.setattr(pe, "JOURNAL", tmp_path / "journal.jsonl")
        monkeypatch.setattr(pe, "RECEIPT", tmp_path / "receipt.json")
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: True)
        reg_store = {"strategies": []}
        monkeypatch.setattr(intake, "_load_registry", lambda: reg_store)
        receipts = []

        def handler(evt):
            item = {
                "key": "CAND-y@c4_y.py",
                "source_file": "scripts/backtest/translated/c4_y.py",
                "is_sharpe": 1.0,
                "turnover": 0.2,
                "max_drawdown": -0.1,
                "segments": [{"batch": "OOS", "sharpe": 0.4, "decay": 0.1}],
            }
            r = intake.run_intake(evt["id"], {"CAND-y@c4_y.py": 0.001}, {}, dry_run=True, items=[item])
            for e in r["created"]:  # 模拟真实落库（第一次消费的写入后果）
                reg_store["strategies"].append({"strategy_id": e["strategy_id"], "code_path": e["code_path"]})
            receipts.append(r)
            return r

        pe.record("c4_batch_completed", {"batch": "B"})
        pe.record("c4_batch_completed", {"batch": "B"})
        r = pe.drain(handler=handler)
        assert r["pending_left"] == 0 and len(receipts) == 2
        assert len(receipts[0]["created_sids"]) == 1  # 第一次：正常入库
        assert receipts[1]["created_sids"] == []  # 第二次：全 skipped（零副作用）

    def test_5_killswitch_midflight_retains(self, tmp_path, monkeypatch):
        """红：KillSwitch 中途触发（intake 层 RuntimeError 被事件层捕获）。蓝：事件保留+attempts 计数，
        恢复后重放成功零丢失。"""
        monkeypatch.setattr(pe, "STATE_DIR", tmp_path)
        monkeypatch.setattr(pe, "JOURNAL", tmp_path / "journal.jsonl")
        monkeypatch.setattr(pe, "RECEIPT", tmp_path / "receipt.json")
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: False)  # intake 层熔断中
        pe.record("c4_batch_completed", {"batch": "B"})
        r = pe.drain(allow_heavy=False, handler=lambda e: intake.run_intake("K", {"a": 0.001}, {}, dry_run=True))
        assert r["failed"] and r["pending_left"] == 1  # 事件保留（不丢）
        assert pe.pending()[0]["attempts"] == 1
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: True)  # Owner reset 恢复
        r2 = pe.drain(allow_heavy=False, handler=lambda e: {"recovered": True})
        assert r2["processed"] and r2["pending_left"] == 0

    def test_6_cas_conflict_fails_closed_with_selfheal(self, tmp_path, monkeypatch):
        """红：地图写入 CAS 竞争（他会话先写地图）。蓝：挂图失败降级为告警回执（注册表条目已入库
        不回滚），下批重放自愈补挂（only-add 幂等）。"""
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: True)
        monkeypatch.setattr(intake, "EVIDENCE", tmp_path / "ev.md")
        (tmp_path / "ev.md").write_text("x", encoding="utf-8")
        monkeypatch.setattr(intake, "_load_registry", lambda: {"strategies": []})

        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/backtest"))
        import auto_mount as am

        import zephyr.shared.io.file_utils as fu

        class _R:
            written = False

        def cas_conflict(path, text, **kw):
            return _R()

        monkeypatch.setattr(fu, "safe_write_text", cas_conflict)
        # 让 ops>0（走到 CAS 写入步），并把地图/报告面隔离进 tmp
        monkeypatch.setattr(
            am,
            "load_registry_entries",
            lambda: [{"sid": "STR-X-001", "cls": "trend_timing", "code_path": "x.py", "lifecycle": "candidate"}],
        )
        monkeypatch.setattr(am, "load_dominant", lambda: None)
        monkeypatch.setattr(
            am,
            "_plan_inserts",
            lambda entries, dom, only: (
                [{"kind": "sleeve", "sid": "STR-X-001", "activation": ["expansion"]}],
                "before",
                "{}",
                [],
            ),
        )
        monkeypatch.setattr(am, "apply_ops", lambda ops, before: "after")
        monkeypatch.setattr(am, "only_add_assert", lambda b, a: None)
        monkeypatch.setattr(am, "MAP_YAML", tmp_path / "map.yaml")
        monkeypatch.setattr(am, "REPORT_DIR", tmp_path)

        def fake_append(entries, path, dry_run):
            return {"new_sids": [e["strategy_id"] for e in entries]}

        monkeypatch.setattr("zephyr.strategy_pipeline.registry_writer.append_entries", fake_append)
        r = intake.run_intake("C1", {"CAND-z@c4_z.py": 0.001}, {}, dry_run=False)
        assert "error" in r["mount"] and r["registry"]["new_sids"]  # 条目已入库+挂图失败降级回执

    def test_7_poison_event_held_and_repair_doorway(self, tmp_path, monkeypatch):
        """红：毒丸事件（attempts≥MAX_ATTEMPTS）滞队——若 drain 继续自动消费=队头饿死全管线。
        蓝：drain 跳过（poison_held，零 handler 触碰，留档待人处置）；repair --unpoison
        摘标+attempts 归零（last_error 留审计痕）后重放正门打通。"""
        monkeypatch.setattr(pe, "STATE_DIR", tmp_path)
        monkeypatch.setattr(pe, "JOURNAL", tmp_path / "journal.jsonl")
        monkeypatch.setattr(pe, "RECEIPT", tmp_path / "receipt.json")
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        pe.record("c4_batch_completed", {"batch": "POISON"})
        evts = pe.pending()
        evts[0]["attempts"] = pe.MAX_ATTEMPTS
        evts[0]["poison"] = True
        evts[0]["last_error"] = "ValueError: synthetic poison"
        pe._rewrite(evts)

        calls: list[dict] = []
        r = pe.drain(allow_heavy=False, handler=lambda e: calls.append(e) or {})
        assert calls == [] and r["processed"] == []  # 毒丸零消费
        assert [s["why"] for s in r["skipped"]] == ["poison_held"]
        assert r["pending_left"] == 1  # 不静默清除，留档待人处置

        listed = pe.repair("list")
        assert listed["n"] == 1 and listed["poison_events"][0]["id"] == evts[0]["id"]
        pe.repair("unpoison", listed["poison_events"][0]["id"])
        after = pe.pending()[0]
        assert "poison" not in after and int(after["attempts"]) == 0
        assert after["last_error"] == "ValueError: synthetic poison"  # 审计痕迹保留

        r2 = pe.drain(allow_heavy=False, handler=lambda e: {"ok": True})
        assert r2["processed"] and r2["pending_left"] == 0  # 重放正门打通

    def test_8_risk_gate_blocks_replay_fill(self, tmp_path, monkeypatch):
        """红：回撤破线（equity 较峰值 -50%）后重放仍照常建仓=风控旁路。
        蓝：六态机 KILL 唯一仲裁 → replay_one 返回 signal=risk_blocked 零成交事件
        （熔断清算腿落 risk_blocked 钱包行留痕，禁旁路钉）。"""
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "backtest"))
        import sim_daily_runner as runner

        from zephyr.shared.state_store import JsonStateStore  # noqa: PLC0415

        mod_src = (
            "import pandas as pd\n"
            "def build(start, end):\n"
            "    idx = pd.Index([end])\n"
            "    return pd.DataFrame(1.0, index=idx, columns=['000999']), pd.DataFrame(100.0, index=idx, columns=['000999'])\n"
        )
        mod_path = tmp_path / "c4_fakerb0001_test.py"
        mod_path.write_text(mod_src)
        risk_dir = tmp_path / "riskstate"
        JsonStateStore(risk_dir).save(runner._SIM_PEAK_EQUITY_NS, {"peak": runner._OBSERVE_NOTIONAL * 2})
        monkeypatch.setattr(runner, "_observe_position", lambda cid: (0.0, 0.0, "", runner._OBSERVE_NOTIONAL, False))
        captured: dict = {}
        monkeypatch.setattr(
            runner, "_write_observe", lambda pocket, events: captured.update(pocket=pocket, events=events)
        )

        res = runner.replay_one("CAND-fakerb0001", mod_path, "2026-09-21", "run-rb", state_dir=risk_dir)
        assert res["signal"] == "risk_blocked" and res["events"] == 0
        assert res["risk"]["allow_new_position"] is False and res["risk"]["state"] == "KILL"
        assert res["liquidation"]["events"] == 0 and res["liquidation"]["t_plus_1_rejected"] == []
        assert captured["events"] == []  # 零成交事件（建仓被闸）
        assert captured["pocket"][9] == "risk_blocked"  # 熔断清算腿钱包行如实留痕
