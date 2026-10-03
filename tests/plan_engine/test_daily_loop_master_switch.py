# [BLUEPRINT] MOD-PLAN-033 | docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md（§5 缺口①；段D 失败注入用例载体）
# [MODULE] tests.plan_engine.test_daily_loop_master_switch
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.daily_loop_master_switch(run_daily_loop/PHASE_STAGES)
# [INVARIANTS] 测试隔离零生产路径（monkeypatch 全部 CH/子进程触面）；fail-open 逐段断言；数据就绪门 fail-closed 断言
# [TTL] permanent

"""daily_loop_master_switch 单测：段序/幂等委托/逐段 fail-open/就绪门 fail-closed。"""

from __future__ import annotations

import pytest

from zephyr.plan_engine import daily_loop_master_switch as dloop


def _patch_ch(monkeypatch: pytest.MonkeyPatch, kline_max: str, regime_max: str) -> None:
    def fake_query(sql: str) -> str:
        if "regime_snapshot_history" in sql:
            return regime_max
        if "trade_calendar" in sql:
            return "2026-09-17"
        return kline_max

    monkeypatch.setattr(dloop, "_ch_query", fake_query)


def test_phase_stage_plan_contract() -> None:
    """钩子序契约：close_verify 恒先于 settle；full 含全部 17 段。"""
    post = dloop.PHASE_STAGES["postmarket"]
    assert post.index("close_verify") < post.index("settle")
    assert len(dloop.PHASE_STAGES["full"]) == 17
    assert dloop.PHASE_STAGES["premarket"][0] == "data_readiness"
    # Owner 扩面（2026-09-21）：A 类四段入位
    assert "llm_premarket" in dloop.PHASE_STAGES["premarket"]
    # F42 G42-1 接线（st-c9-f42）：P1 持仓体检棒入 premarket（晨间预案后、LLM 分析前）
    assert "position_checkup" in dloop.PHASE_STAGES["premarket"]
    assert dloop.PHASE_STAGES["premarket"].index("position_checkup") < dloop.PHASE_STAGES["premarket"].index(
        "llm_premarket"
    )
    assert {"sentiment_loop", "auction_hit"} <= set(dloop.PHASE_STAGES["intraday"])
    assert {"similar_day", "attribution"} <= set(dloop.PHASE_STAGES["postmarket"])


def test_position_checkup_stage_skips_without_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """投放面缺席=skipped 留痕（fail-open，禁伪造持仓数据）。"""
    monkeypatch.setattr("zephyr.position.core.position_checkup_orchestrator.default_positions_loader", lambda d: [])
    out = dloop._stage_position_checkup("2026-09-18")
    assert out["status"] == "skipped"
    assert out["reason"] == "no_checkup_inputs"


def test_position_checkup_stage_ok_passes_params(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """编排触发+参数传递：data_date 直传体检棒，报告摘要回流段结果。"""
    captured: dict = {}

    def fake_run(positions, *, data_date, **kw):
        captured["data_date"] = data_date
        captured["n"] = len(positions)
        return {"summary": {"actions": {"HOLD": 1}}, "audit_path": str(tmp_path / "a.jsonl"), "positions": []}

    monkeypatch.setattr(
        "zephyr.position.core.position_checkup_orchestrator.default_positions_loader",
        lambda d: [{"symbol": "600519.SH"}],
    )
    monkeypatch.setattr("zephyr.position.core.position_checkup_orchestrator.run_position_checkup", fake_run)
    out = dloop._stage_position_checkup("2026-09-18")
    assert out["status"] == "ok"
    assert captured == {"data_date": "2026-09-18", "n": 1}
    assert out["summary"] == {"actions": {"HOLD": 1}}


def test_position_checkup_stage_fail_open(monkeypatch: pytest.MonkeyPatch) -> None:
    """体检棒炸=异常上抛由循环壳收敛为该段 error（fail-open 契约同其他段）。"""
    monkeypatch.setattr(
        "zephyr.position.core.position_checkup_orchestrator.default_positions_loader",
        lambda d: [{"symbol": "x"}],
    )

    def boom(positions, *, data_date, **kw):
        raise RuntimeError("注入失败:checkup")

    monkeypatch.setattr("zephyr.position.core.position_checkup_orchestrator.run_position_checkup", boom)
    with pytest.raises(RuntimeError, match="注入失败:checkup"):
        dloop._stage_position_checkup("2026-09-18")


def test_input_validation_fail_closed() -> None:
    with pytest.raises(ValueError):
        dloop.run_daily_loop("20260918")
    with pytest.raises(ValueError):
        dloop.run_daily_loop("2026-09-18", phase="noon")


def test_dry_run_lists_without_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_ch(monkeypatch, "2026-09-18", "2026-09-18")
    monkeypatch.setattr(dloop, "_pp001_snapshot", lambda: {"plan_id": "PP-001"})
    out = dloop.run_daily_loop("2026-09-18", dry_run=True)
    assert out["dry_run"] is True
    assert out["planned_stages"] == dloop.PHASE_STAGES["full"]
    assert "stages" not in out


def test_data_readiness_gate_blocks_everything(monkeypatch: pytest.MonkeyPatch) -> None:
    """行情缺日=fail-closed：整圈 blocked，后续段不执行。"""
    _patch_ch(monkeypatch, "2026-09-17", "2026-09-18")  # kline 缺 09-18
    monkeypatch.setattr(dloop, "_pp001_snapshot", lambda: {})
    out = dloop.run_daily_loop("2026-09-18")
    assert out.get("blocked")
    assert "daily_plan" not in out["stages"]


def test_stage_fail_open_continues(monkeypatch: pytest.MonkeyPatch) -> None:
    """单段炸=留痕继续（fail-open），summary 如实计 error。"""
    _patch_ch(monkeypatch, "2026-09-18", "2026-09-18")
    monkeypatch.setattr(dloop, "_pp001_snapshot", lambda: {})
    monkeypatch.setattr(dloop, "ensure_regime_fresh", lambda d: {"status": "ok"})
    monkeypatch.setattr(dloop, "_stage_warroom", lambda d, p: (_ for _ in ()).throw(RuntimeError("注入失败:warroom")))
    monkeypatch.setattr("zephyr.plan_engine.daily_plan.maybe_emit_daily_plan", lambda **k: {"action": "ok"})
    monkeypatch.setattr(
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast", lambda **k: {"action": "emitted"}
    )
    monkeypatch.setattr("zephyr.strategy_pipeline.pipeline_events.maybe_emit_pf_alloc_daily", lambda **k: {"rc": 0})
    monkeypatch.setattr(
        "zephyr.plan_engine.intraday_l1_tracker.maybe_track_intraday_state", lambda **k: {"action": "ok"}
    )
    monkeypatch.setattr(
        "zephyr.plan_engine.scenario_classifier.maybe_classify_intraday_scenario", lambda **k: {"action": "ok"}
    )
    monkeypatch.setattr("zephyr.plan_engine.close_verifier.verify_for_session", lambda d, **k: {"verified": 0})
    monkeypatch.setattr("zephyr.plan_engine.judgment_settler.settle_all", lambda **k: {})
    monkeypatch.setattr(dloop, "_stage_llm_premarket", lambda d: {"status": "ok"})
    monkeypatch.setattr(dloop, "_stage_sentiment_loop", lambda d: {"status": "ok"})
    monkeypatch.setattr(
        dloop, "_stage_auction_hit", lambda d: {"status": "skipped", "reason": "outside_auction_window"}
    )
    monkeypatch.setattr(dloop, "_stage_similar_day", lambda d: {"status": "ok"})
    monkeypatch.setattr(dloop, "_stage_attribution", lambda d: {"status": "ok"})
    monkeypatch.setattr(
        "zephyr.strategy_pipeline.daily_decision_orchestrator.run_daily_decision",
        lambda d, **k: {"action": "adjudicated", "brief": "x"},
    )
    out = dloop.run_daily_loop("2026-09-18")
    assert out["stages"]["warroom"]["status"] == "error"
    assert "注入失败:warroom" in out["stages"]["warroom"]["error"]
    assert out["stages"]["settle"]["status"] == "ok"
    assert out["summary"]["error"] == 1
    assert out["summary"]["ok"] >= 12


# ── D13-20/D13-44 回归（EXEC-3 2026-10-04，fig13 簿09 Y-4）──────────────────────


def test_auction_hit_stage_late_eval_at_1615_circle(monkeypatch: pytest.MonkeyPatch) -> None:
    """D13-20 回归：16:45 dloop_post 圈（走势窗已闭合）不再恒 skipped——回看补判
    照常落库且 late_eval=True 留痕（判定输入恒≤10:00，PIT 口径不变）。"""
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo as _zi

    captured: dict = {}

    def fake_record(trade_date, *, late_eval=False, **kw):
        captured["trade_date"] = trade_date
        captured["late_eval"] = late_eval

        class _Out:
            hit = True

        return _Out()

    monkeypatch.setattr("zephyr.plan_engine.auction_hit_recorder.record_auction_hit", fake_record)
    now = _dt(2026, 10, 2, 16, 45, tzinfo=_zi("Asia/Shanghai"))  # 16:45 圈时刻
    out = dloop._stage_auction_hit("2026-10-02", now=now)
    assert out["status"] == "ok"
    assert out["late_eval"] is True
    assert out["hit"] is True
    assert captured == {"trade_date": "2026-10-02", "late_eval": True}


def test_auction_hit_stage_still_skips_before_window_close(monkeypatch: pytest.MonkeyPatch) -> None:
    """窗未闭合（<10:00，走势数据未齐）仍 skipped——不提前判定（PIT 卫生保留）。"""
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo as _zi

    called: list = []
    monkeypatch.setattr(
        "zephyr.plan_engine.auction_hit_recorder.record_auction_hit", lambda *a, **k: called.append(k) or a
    )
    now = _dt(2026, 10, 2, 9, 0, tzinfo=_zi("Asia/Shanghai"))
    out = dloop._stage_auction_hit("2026-10-02", now=now)
    assert out["status"] == "skipped"
    assert out["reason"] == "auction_window_not_closed"
    assert called == []  # 零落库


def test_next_day_stage_surfaces_handover_gap(monkeypatch: pytest.MonkeyPatch) -> None:
    """D13-44 回归：发射钩子 data_insufficient 段状态如实计 error（原硬编码 ok 是
    断供真静默位）——dloop_post 圈 summary.error>0 即触发告警（缺口可见）。"""
    monkeypatch.setattr(
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast",
        lambda **k: {"action": "data_insufficient", "trade_date": "2026-10-02", "reason": "历史统计样本为空"},
    )
    out = dloop._stage_next_day("2026-10-02")
    assert out["status"] == "error"
    assert out["action"] == "data_insufficient"
    assert "日界交接缺口" in out["error"]


def test_next_day_stage_ok_actions(monkeypatch: pytest.MonkeyPatch) -> None:
    """emitted/already_emitted/skipped_wake_point 三态仍 ok（不误报）。"""
    monkeypatch.setattr(
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast",
        lambda **k: {"action": "already_emitted", "trade_date": "2026-10-02"},
    )
    out = dloop._stage_next_day("2026-10-02")
    assert out["status"] == "ok"
