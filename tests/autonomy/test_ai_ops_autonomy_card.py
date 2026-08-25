# [BLUEPRINT] MOD-AU-013 | docs/03_modules/_domain_autonomy_core/ai_ops_autonomy_card/blueprint.md | §test
# [A_test] module_id: MOD-AU-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AiOpsAutonomyCard 单元测试 (MOD-AU-013, MVP)。

覆盖: C-008 能力卡声明（四阶段闭环/7类检测源/四路诊断/AUT-001~008 策略库）/
B-014/015/016 禁区硬编码（交易时段强制人工）/ 修复策略选择（未知→OBSERVE+
Learn）/ TNR 可撤销修复（无快照或不可逆策略→人工；恶化→ROLLBACK）/ 自治
分级门禁（策略级别超卡级别→人工）/ 输入与配置 Fail-Closed / 回调异常不阻断 /
双审计 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.ai_ops_autonomy_card import (
    CAPABILITY_CARD,
    FORBIDDEN_ZONES,
    REPAIR_STRATEGIES,
    AiOpsAutonomyCard,
    AutonomyGrade,
    DetectorSource,
    DiagnosisRoute,
    ForbiddenZone,
    InvalidAutonomyCardConfigError,
    InvalidOpsIncidentError,
    OpsIncident,
    RemediateAction,
    RemediateVerdict,
)


def _incident(
    incident_id: str = "INC-1",
    source=DetectorSource.PROCESS_HEALTH,
    action_tag: str = "dlq_replay",
    severity: str = "P2",
    in_trading_session: bool = False,
    snapshot_ref: str = "snap-001",
    diagnosis_route=DiagnosisRoute.RULE,
) -> OpsIncident:
    return OpsIncident(
        incident_id=incident_id,
        source=source,
        action_tag=action_tag,
        severity=severity,
        in_trading_session=in_trading_session,
        snapshot_ref=snapshot_ref,
        diagnosis_route=diagnosis_route,
    )


def _card(**kw) -> AiOpsAutonomyCard:
    return AiOpsAutonomyCard(**kw)


# ── 能力卡声明 ───────────────────────────────────────────────────────────────


class TestCapabilityCard:
    def test_card_identity(self) -> None:
        assert CAPABILITY_CARD["card_id"] == "C-008"
        assert CAPABILITY_CARD["name"] == "AI自治运维能力卡片"

    def test_closed_loop_four_phases(self) -> None:
        assert CAPABILITY_CARD["closed_loop"] == ["detect", "diagnose", "remediate", "learn"]

    def test_seven_detector_sources(self) -> None:
        assert len(CAPABILITY_CARD["detector_sources"]) == 7
        assert len(set(DetectorSource)) == 7

    def test_four_diagnosis_routes(self) -> None:
        assert CAPABILITY_CARD["diagnosis_routes"] == ["rule", "correlation", "llm", "causal"]
        assert len(set(DiagnosisRoute)) == 4

    def test_forbidden_zones_hardcoded(self) -> None:
        zones = CAPABILITY_CARD["forbidden_zones"]
        assert set(zones) == {"B-014", "B-015", "B-016"}
        assert "重启" in zones["B-014"]
        assert "升级" in zones["B-015"]
        assert "清理" in zones["B-016"]

    def test_boundary_vs_c023(self) -> None:
        assert "C-023" in CAPABILITY_CARD["boundary"]


# ── 修复策略库 ───────────────────────────────────────────────────────────────


class TestStrategyLibrary:
    def test_eight_strategies(self) -> None:
        assert len(REPAIR_STRATEGIES) == 8
        ids = [s.strategy_id for s in REPAIR_STRATEGIES]
        assert ids == [f"AUT-{i:03d}" for i in range(1, 9)]

    def test_strategy_grades_in_range(self) -> None:
        for s in REPAIR_STRATEGIES:
            assert 1 <= int(s.grade) <= 4

    def test_at_least_one_irreversible(self) -> None:
        assert any(not s.reversible for s in REPAIR_STRATEGIES)

    def test_action_tags_unique(self) -> None:
        tags: list[str] = []
        for s in REPAIR_STRATEGIES:
            tags.extend(s.action_tags)
        assert len(tags) == len(set(tags))


# ── 禁区硬编码 ───────────────────────────────────────────────────────────────


class TestForbiddenZones:
    def test_zone_registry(self) -> None:
        assert set(FORBIDDEN_ZONES) == {ForbiddenZone.B_014, ForbiddenZone.B_015, ForbiddenZone.B_016}

    def test_b014_restart_core_in_session_escalate(self) -> None:
        action = _card().evaluate(_incident(action_tag="restart_core_process", in_trading_session=True))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN
        assert "B-014" in action.reason

    def test_b015_upgrade_dependency_in_session_escalate(self) -> None:
        action = _card().evaluate(_incident(action_tag="upgrade_dependency", in_trading_session=True))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN
        assert "B-015" in action.reason

    def test_b016_purge_unarchived_in_session_escalate(self) -> None:
        action = _card().evaluate(_incident(action_tag="purge_unarchived_logs", in_trading_session=True))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN
        assert "B-016" in action.reason

    def test_zone_action_off_session_proceeds(self) -> None:
        # 非交易时段不触发禁区硬编码，走常规分级门禁（restart_core_process=AUT-001 L2）
        action = _card().evaluate(_incident(action_tag="restart_core_process", in_trading_session=False))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR

    def test_zone_hardcoded_not_configurable(self) -> None:
        # 卡级别抬到 L4 也不可绕过交易时段禁区
        card = _card(grade=AutonomyGrade.A_L4)
        action = card.evaluate(_incident(action_tag="restart_core_process", in_trading_session=True))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN


# ── 修复策略选择与分级门禁 ───────────────────────────────────────────────────


class TestEvaluate:
    def test_known_action_execute(self) -> None:
        action = _card().evaluate(_incident(action_tag="dlq_replay"))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR
        assert action.strategy_id == "AUT-002"
        assert action.restore_snapshot_ref == "snap-001"

    def test_unknown_action_observe_and_learn(self) -> None:
        action = _card().evaluate(_incident(action_tag="never_seen_action"))
        assert action.verdict == RemediateVerdict.OBSERVE
        kinds = [r["kind"] for r in action.audit_records]
        assert "learn_candidate" in kinds

    def test_strategy_above_card_grade_escalate(self) -> None:
        # readonly_failover=AUT-004 L3，卡默认 L2 → 人工
        action = _card().evaluate(_incident(action_tag="readonly_failover"))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN
        assert "L3" in action.reason or "分级" in action.reason

    def test_raise_grade_allows(self) -> None:
        card = _card(grade=AutonomyGrade.A_L3)
        action = card.evaluate(_incident(action_tag="readonly_failover"))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR

    def test_irreversible_strategy_escalate_even_l4(self) -> None:
        # schema_migrate=AUT-008 不可逆：TNR 不满足，任何级别都人工
        card = _card(grade=AutonomyGrade.A_L4)
        action = card.evaluate(_incident(action_tag="schema_migrate"))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN
        assert "TNR" in action.reason or "可撤销" in action.reason

    def test_empty_snapshot_escalate(self) -> None:
        # 可逆策略但无 restore 快照 → TNR 无法保证 → 人工
        action = _card().evaluate(_incident(action_tag="dlq_replay", snapshot_ref=""))
        assert action.verdict == RemediateVerdict.ESCALATE_HUMAN

    def test_repair_sink_called(self) -> None:
        got: list[tuple] = []
        card = _card(repair_sink=lambda inc, st: got.append((inc, st)))
        action = card.evaluate(_incident(action_tag="dlq_replay"))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR
        assert len(got) == 1
        assert got[0][1].strategy_id == "AUT-002"

    def test_pure_evaluate(self) -> None:
        card = _card()
        inc = _incident(action_tag="dlq_replay")
        a1 = card.evaluate(inc)
        a2 = card.evaluate(inc)
        assert a1 == a2


# ── TNR 修复后评估（恶化自动回滚） ───────────────────────────────────────────


class TestPostRepair:
    def test_worsening_rollback(self) -> None:
        rollbacks: list[tuple] = []
        card = _card(rollback_trigger=lambda inc, st: rollbacks.append((inc, st)))
        action = card.evaluate_post_repair(_incident(action_tag="dlq_replay"), health_delta=-0.5)
        assert action.verdict == RemediateVerdict.ROLLBACK
        assert action.rollback_signaled is True
        assert len(rollbacks) == 1

    def test_improving_observe(self) -> None:
        card = _card()
        action = card.evaluate_post_repair(_incident(action_tag="dlq_replay"), health_delta=0.3)
        assert action.verdict == RemediateVerdict.OBSERVE
        assert action.rollback_signaled is False

    def test_zero_delta_observe(self) -> None:
        action = _card().evaluate_post_repair(_incident(action_tag="dlq_replay"), health_delta=0.0)
        assert action.verdict == RemediateVerdict.OBSERVE


# ── Fail-Closed 校验 ─────────────────────────────────────────────────────────


class TestFailClosed:
    @pytest.mark.parametrize("bad_id", ["", "  "])
    def test_empty_incident_id(self, bad_id: str) -> None:
        with pytest.raises(InvalidOpsIncidentError):
            _card().evaluate(_incident(incident_id=bad_id))

    def test_bad_source(self) -> None:
        with pytest.raises(InvalidOpsIncidentError):
            _card().evaluate(_incident(source="cctv"))

    def test_bad_route(self) -> None:
        with pytest.raises(InvalidOpsIncidentError):
            _card().evaluate(_incident(diagnosis_route="vibes"))

    @pytest.mark.parametrize("bad_sev", ["", "P0", "P4", "p1"])
    def test_bad_severity(self, bad_sev: str) -> None:
        with pytest.raises(InvalidOpsIncidentError):
            _card().evaluate(_incident(severity=bad_sev))

    @pytest.mark.parametrize("bad_tag", ["", "  "])
    def test_empty_action_tag(self, bad_tag: str) -> None:
        with pytest.raises(InvalidOpsIncidentError):
            _card().evaluate(_incident(action_tag=bad_tag))

    def test_bad_grade_config(self) -> None:
        with pytest.raises(InvalidAutonomyCardConfigError):
            _card(grade=9)


# ── 回调异常不阻断 ───────────────────────────────────────────────────────────


class TestCallbackResilience:
    def test_repair_sink_exception_not_blocking(self) -> None:
        def _boom(inc, st) -> None:
            raise RuntimeError("sink down")

        action = _card(repair_sink=_boom).evaluate(_incident(action_tag="dlq_replay"))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR

    def test_rollback_trigger_exception_not_blocking(self) -> None:
        def _boom(inc, st) -> None:
            raise RuntimeError("trigger down")

        action = _card(rollback_trigger=_boom).evaluate_post_repair(
            _incident(action_tag="dlq_replay"), health_delta=-1.0
        )
        assert action.verdict == RemediateVerdict.ROLLBACK
        assert action.rollback_signaled is False

    def test_audit_sink_exception_not_blocking(self) -> None:
        def _boom(rec) -> None:
            raise RuntimeError("audit down")

        action = _card(audit_sink=_boom).evaluate(_incident(action_tag="dlq_replay"))
        assert action.verdict == RemediateVerdict.EXECUTE_REPAIR


# ── 审计与 frozen ────────────────────────────────────────────────────────────


class TestAuditAndFrozen:
    def test_execute_double_audit(self) -> None:
        got: list[dict] = []
        card = _card(audit_sink=got.append)
        card.evaluate(_incident(action_tag="dlq_replay"))
        kinds = [r["kind"] for r in got]
        assert "remediate_decision" in kinds
        assert "repair_execute" in kinds

    def test_escalate_audit(self) -> None:
        got: list[dict] = []
        card = _card(audit_sink=got.append)
        card.evaluate(_incident(action_tag="restart_core_process", in_trading_session=True))
        kinds = [r["kind"] for r in got]
        assert "remediate_decision" in kinds
        assert "escalate" in kinds

    def test_rollback_audit(self) -> None:
        got: list[dict] = []
        card = _card(audit_sink=got.append)
        card.evaluate_post_repair(_incident(action_tag="dlq_replay"), health_delta=-0.1)
        kinds = [r["kind"] for r in got]
        assert "rollback" in kinds

    def test_incident_frozen(self) -> None:
        inc = _incident()
        with pytest.raises(dataclasses.FrozenInstanceError):
            inc.severity = "P1"  # type: ignore[misc]

    def test_action_type(self) -> None:
        action = _card().evaluate(_incident(action_tag="dlq_replay"))
        assert isinstance(action, RemediateAction)
