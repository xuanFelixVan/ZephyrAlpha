# [A_test] module_id: zephyr.ai_layer.redline.sev_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_sev_router
# [MODULE] tests.ai_layer.redline.test_sev_router
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.sev_router
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_sev_router.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：四级事件样例各一可聚合成"开放事件数"；
#              建议不动手断言：route/collect 不触碰 KillSwitch/交易熔断（零 import 零调用面）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_sev_router.py — S6 SEV 探针聚合路由单测（四级聚合/项目安全判定/建议不动手）。"""

from __future__ import annotations

import inspect

from zephyr.ai_layer.redline.sev_router import (
    ROUTE_ACTION_BY_SEV,
    SEV_CLASSES,
    SevSignal,
    aggregate_open_events,
    collect_signals,
    is_project_safe,
    route_signals,
    sev_snapshot,
)


def _one_of_each() -> list[SevSignal]:
    """四级事件样例各一（验收主样例）。"""
    return [
        SevSignal(sev="sev1", source="integrity.verify_chain", open_count=1, detail="mismatch=2"),
        SevSignal(sev="sev2", source="trading_kill_switch", open_count=1, detail="DAILY_LOSS"),
        SevSignal(sev="sev3", source="session_env_guard", open_count=1, detail="QMT" "_REAL_* env"),
        SevSignal(sev="sev4", source="tick_duplication", open_count=1, detail="dup 率越限"),
    ]


def test_four_sev_samples_aggregate_to_open_event_counts():
    open_events = aggregate_open_events(_one_of_each())
    assert open_events == {"sev1": 1, "sev2": 1, "sev3": 1, "sev4": 1, "skipped": 0}


def test_resolved_signal_not_counted():
    signals = [
        SevSignal(sev="sev4", source="x", open_count=3, is_open=True),
        SevSignal(sev="sev4", source="x", open_count=3, is_open=False),
    ]
    assert aggregate_open_events(signals)["sev4"] == 3


def test_malformed_signals_skipped_with_count():
    signals = [
        SevSignal(sev="sev9", source="x", open_count=1),
        SevSignal(sev="sev2", source="x", open_count=-1),
        SevSignal(sev="sev2", source="x", open_count=2),
    ]
    result = aggregate_open_events(signals)
    assert result["sev2"] == 2 and result["skipped"] == 2


def test_project_safe_measurable_definition():
    assert is_project_safe({"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}, chain_mismatch_count=0)
    assert not is_project_safe({"sev1": 1, "sev2": 0, "sev3": 0, "sev4": 0}, chain_mismatch_count=0)
    assert not is_project_safe({"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}, chain_mismatch_count=1), (
        "verify_chain mismatch>0（非 known_loss）=不安全（§3 可度量定义）"
    )


def test_probe_error_counts_conservatively_not_silently_green():
    def broken_probe() -> list[SevSignal]:
        raise RuntimeError("IntegrityVerifier unavailable")

    signals, errors = collect_signals({"sev1": broken_probe})
    assert errors and "RuntimeError" in errors["sev1"]
    open_events = aggregate_open_events(signals)
    assert open_events["sev1"] == 1, "探针异常按保守开放事件计数（fail-closed 不静默绿）"


def test_route_directives_suggestions_not_actions():
    notified: list[dict] = []
    directives = route_signals(_one_of_each(), notify=notified.append)
    assert [d.sev for d in directives] == list(SEV_CLASSES)
    for directive in directives:
        assert directive.notify_owner is True
        assert directive.action == ROUTE_ACTION_BY_SEV[directive.sev]
        assert directive.notes, "每条指令带建议注记"
    assert len(notified) == 4
    sev1 = next(d for d in directives if d.sev == "sev1")
    assert "建议" in sev1.notes[0], "SEV-1 熔断=建议权（纠察/Owner），本模块不动手"
    sev2 = next(d for d in directives if d.sev == "sev2")
    assert "native" in sev2.action, "SEV-2 五级熔断原生动作归 trading 侧自持"


def test_router_module_does_not_touch_native_breakers():
    """五永不触碰避让铁律：聚合路由面零 import 原生熔断模块（结构性不越权）。"""
    from zephyr.ai_layer.redline import sev_router

    source = inspect.getsource(sev_router)
    assert "import kill_switch" not in source
    assert "trading_kill_switch import" not in source
    assert "manual_trip_global(" not in source.replace(
        "manual_trip_global 建议权", ""
    ).replace("killswitch_trip_suggestion", ""), "manual_trip_global 只以建议字样出现"


def test_sev_snapshot_shape():
    snapshot = sev_snapshot(_one_of_each(), chain_mismatch_count=2)
    assert snapshot["sev_incidents"] == {"sev1": 1, "sev2": 1, "sev3": 1, "sev4": 1}
    assert snapshot["project_safe"] is False
    assert snapshot["chain_mismatch_count"] == 2
