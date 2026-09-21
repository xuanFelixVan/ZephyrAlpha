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
    """钩子序契约：close_verify 恒先于 settle；full 含全部 11 段。"""
    post = dloop.PHASE_STAGES["postmarket"]
    assert post.index("close_verify") < post.index("settle")
    assert len(dloop.PHASE_STAGES["full"]) == 16
    assert dloop.PHASE_STAGES["premarket"][0] == "data_readiness"
    # Owner 扩面（2026-09-21）：A 类四段入位
    assert "llm_premarket" in dloop.PHASE_STAGES["premarket"]
    assert {"sentiment_loop", "auction_hit"} <= set(dloop.PHASE_STAGES["intraday"])
    assert {"similar_day", "attribution"} <= set(dloop.PHASE_STAGES["postmarket"])


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
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast", lambda **k: {"action": "ok"}
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
