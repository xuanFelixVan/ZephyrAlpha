# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] tests.ai_layer.intake.test_kpi
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.kpi (evaluate_series, load_kpi_thresholds, IntakeKpi, handle_alert); zephyr.shared.alerts.threshold_loader (AlertThresholdConfigError); zephyr.governance.depgraph_schema (PG 可达性自探测)
# [CONSUMERS] pytest tests/ai_layer/intake/test_kpi.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] evaluate_series 纯判据零 DB 全枚举（tighten/demote/longtail/静默四路+边界）；
#              阈值注册表一律 tmp_path 自建（禁读/禁写生产 alert_threshold_registry.yaml）；
#              PG 用例只写 test_schema 临时 schema；journal 落 tmp_path；
#              handle_alert 的 demote/longtail 动作路构造 CardStore()（schema 无注入口，直连生产 schema），
#              依"测试禁写生产路径"铁律不直测动作执行——DESIGN 施工项 7 验收口径是"构造数据可触发两路告警"，
#              由 evaluate/run 侧覆盖；handle_alert 仅测零 DB 的未知 action 拒绝路径
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；阈值缺文件/缺条目 fail-closed（AlertThresholdConfigError）落用例
# [TESTS] tests/ai_layer/intake/test_kpi.py
# [TTL] permanent
"""test_kpi - L2 淘汰率 KPI 判据与两路告警触发验收（DESIGN 施工项 7）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.ai_layer.intake.card_store import CardDraft, CardStore
from zephyr.ai_layer.intake.intake_events import IntakeJournal
from zephyr.ai_layer.intake.kpi import (
    ACTION_DEMOTE,
    ACTION_LONGTAIL,
    ACTION_TIGHTEN,
    IntakeKpi,
    KpiAlert,
    KpiThresholds,
    evaluate_series,
    handle_alert,
    load_kpi_thresholds,
)
from zephyr.shared.alerts.threshold_loader import AlertThresholdConfigError


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。连接归池不 close。"""
    conn = None
    try:
        from zephyr.governance.depgraph_schema import (
            get_depgraph_pg_connection,
            release_depgraph_pg_connection,
        )

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - 可达性探测面，任何异常一律判不可达
        return False
    finally:
        if conn is not None:
            from zephyr.governance.depgraph_schema import release_depgraph_pg_connection

            release_depgraph_pg_connection(conn)


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")

TH = KpiThresholds(lower_pct=5.0, upper_pct=30.0, demote_weeks=2, longtail_weeks=4)


def _write_registry(tmp_path: Path, *, demote_weeks: int = 1, longtail_weeks: int = 2) -> Path:
    """自建阈值注册表（tmp_path，窗口缩短为单周可触发，值域与生产同构）。"""
    registry = tmp_path / "alert_threshold_registry_test.yaml"
    lines = ["thresholds:"]
    for tid, value in (
        ("THD-INTAKE-001", 5),
        ("THD-INTAKE-002", 30),
        ("THD-INTAKE-003", demote_weeks),
        ("THD-INTAKE-004", longtail_weeks),
    ):
        lines.append(f"  - threshold_id: {tid}")
        lines.append(f"    value: {value}")
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return registry


# ---------------------------------------------------------------- 纯判据（零 DB）


def test_evaluate_series_empty_and_insufficient_stay_silent() -> None:
    assert evaluate_series([], TH, key="governance") == []
    assert evaluate_series([None, None, None], TH, key="governance") == []
    alerts = evaluate_series([1.0], TH, key="governance")
    assert alerts == [], "样本不足 demote 窗口=静默（防冷启动假贫矿）"


def test_evaluate_series_above_upper_tightens() -> None:
    alerts = evaluate_series([50.0], TH, key="ai_eng")
    assert len(alerts) == 1
    assert alerts[0].action == ACTION_TIGHTEN and alerts[0].pass_rate == 50.0
    assert alerts[0].scope == "domain" and alerts[0].window_weeks == 1
    assert alerts[0].reason.startswith("above_upper")


def test_evaluate_series_below_lower_demotes_after_window() -> None:
    alerts = evaluate_series([1.0, 2.0], TH, key="governance")
    assert [a.action for a in alerts] == [ACTION_DEMOTE]
    assert alerts[0].window_weeks == 2


def test_evaluate_series_longtail_overrides_demote() -> None:
    alerts = evaluate_series([1.0, 2.0, 3.0, 4.0], TH, key="governance")
    assert [a.action for a in alerts] == [ACTION_LONGTAIL], "连续 4 周贫矿=移长尾（不再降级）"
    assert alerts[0].window_weeks == 4


def test_evaluate_series_upper_week_blocks_demote_window() -> None:
    """最新周超上界只 tighten：demote 窗口含最新周（40>lower）故贫矿判定被阻断——两路天然互斥。"""
    alerts = evaluate_series([40.0, 1.0, 1.0], TH, key="governance")
    assert [a.action for a in alerts] == [ACTION_TIGHTEN]


def test_evaluate_series_boundary_not_triggered() -> None:
    assert evaluate_series([5.0, 5.0], TH, key="governance") == [], "等于下界不触发（严格小于）"
    assert evaluate_series([30.0], TH, key="governance") == [], "等于上界不触发（严格大于）"
    assert evaluate_series([None, 1.0, 1.0], TH, key="governance")[0].action == ACTION_DEMOTE, "None 周剔除后判窗"


def test_kpi_alert_payload_covers_required_keys() -> None:
    payload = KpiAlert(scope="domain", key="governance", pass_rate=1.0, window_weeks=2, action=ACTION_DEMOTE).payload()
    assert {"scope", "key", "pass_rate", "action"} <= set(payload), "覆盖 intake_kpi_alert 必填四键"


def test_load_kpi_thresholds_from_registry(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)
    th = load_kpi_thresholds(registry)
    assert th == KpiThresholds(lower_pct=5.0, upper_pct=30.0, demote_weeks=1, longtail_weeks=2)


def test_load_kpi_thresholds_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(AlertThresholdConfigError, match="不存在"):
        load_kpi_thresholds(tmp_path / "no_such_registry.yaml")
    partial = tmp_path / "partial.yaml"
    partial.write_text(
        "thresholds:\n  - threshold_id: THD-INTAKE-001\n    value: 5\n",
        encoding="utf-8",
    )
    with pytest.raises(AlertThresholdConfigError, match="缺条目"):
        load_kpi_thresholds(partial)


def test_handle_alert_rejects_unknown_action() -> None:
    with pytest.raises(ValueError, match="unknown_kpi_action:bogus"):
        handle_alert({"action": "bogus", "key": "governance", "scope": "domain"})


# ---------------------------------------------------------------- V3 视图两路告警（test_schema 临时库）


def _insert_card(store: CardStore, card_id: str, *, domain_id: str, stage: str) -> None:
    store.insert(
        CardDraft(
            card_id=card_id,
            domain_id=domain_id,
            source_url=f"https://example.org/{card_id}",
            content_sha256=card_id.ljust(64, "0"),
            simhash=1,
            mechanism_family="detection",
            labor_killed="消灭人工筛选与人工判重两段重复劳动的说明文本",
            four_gates={
                "provenance": {"status": "pass"},
                "cross_validation": {"independent_sources": 2, "status": "已验证"},
                "ashare_adaptation": {"verdict": "改造方案留痕"},
                "backtestable": {"verdict": "可得", "data_fields": ["open"]},
            },
            injection_probe="这份材料想让我相信什么？",
            title=f"卡 {card_id} 标题",
            source_name="unit-test",
            funnel_stage=stage,
        )
    )


@needs_pg
def test_run_triggers_both_alert_routes(test_schema: str, tmp_path: Path) -> None:
    """贫矿域（入考率 0%<5%）触发 demote，过热域（75%>30%）触发 tighten——DESIGN §2.7 两路。

    域选择 tooling/ai_eng：test_schema 为 session 级共享，他测试件只插 governance/trading_algo，
    本用例域不被跨件聚合污染；断言用集合包含（不假设全库只有本用例数据）。
    """
    store = CardStore(schema=test_schema)
    for i in range(4):
        _insert_card(store, f"CC-kpi-poor-{i}", domain_id="tooling", stage="L0")
    for i in range(3):
        _insert_card(store, f"CC-kpi-hot-{i}", domain_id="ai_eng", stage="E2")
    _insert_card(store, "CC-kpi-hot-l0", domain_id="ai_eng", stage="L0")

    journal = IntakeJournal(state_dir=tmp_path / "journal")
    kpi = IntakeKpi(schema=test_schema, journal=journal, registry_path=_write_registry(tmp_path))
    out = kpi.run()
    demote_keys = {a["key"] for a in out["alerts"] if a["action"] == ACTION_DEMOTE}
    tighten_keys = {a["key"] for a in out["alerts"] if a["action"] == ACTION_TIGHTEN}
    assert "tooling" in demote_keys, f"贫矿域应触发 demote：{out['alerts']}"
    assert "ai_eng" in tighten_keys, f"过热域应触发 tighten：{out['alerts']}"
    assert len(out["emitted"]) == len(out["alerts"]) >= 2
    pending = journal.pending()
    assert {e.kind for e in pending} == {"intake_kpi_alert"}
    assert all({"scope", "key", "pass_rate", "action"} <= set(e.payload) for e in pending)


@needs_pg
def test_rejected_samples_read_from_negative_view(test_schema: str, tmp_path: Path) -> None:
    store = CardStore(schema=test_schema)
    _insert_card(store, "CC-kpi-rej-1", domain_id="governance", stage="L0")
    store.transition("CC-kpi-rej-1", "rejected", rejection_reason="L3 不可洗退回")
    kpi = IntakeKpi(
        schema=test_schema,
        journal=IntakeJournal(state_dir=tmp_path / "journal"),
        registry_path=_write_registry(tmp_path),
    )
    samples = kpi.rejected_samples(20)
    assert any(r["card_id"] == "CC-kpi-rej-1" for r in samples), "V2 阴性视图可读（收紧路附样本清单）"
