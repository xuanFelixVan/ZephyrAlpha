# [BLUEPRINT] MOD-INF-053 | docs/03_modules/MOD-INF-053/
# [MODULE] tests.security.ops.test_incident_pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/security/ops/test_incident_pipeline.py -q
# [TTL] permanent

"""统一事件流消费→诊断→三通道判决管线（MOD-INF-053）测试。

验收对照（16号文 §4.3 P1-1~P1-4 + 12号文 §4.4 涌现介入接线）：
- P1-1 探针事件触发诊断记录；不可自动修的判决走 escalation 通道落盘；
- P1-2 结构/语义/行为三类故障各一条探针全链路走通；行为类探针 100% 不触发
  自动修复（不变量验证）；语义类必经 LLM Bridge（LSG 闸）不直通模板化；
- P1-3 知识库文件存在且 schema 经校验；每次修复动作自动向库写一条记录
  （记录优先，不做匹配；append-only）；
- P1-4 白名单变更走 human_gated 审批留痕；未经审批的豁免 0 条；
- 涌现介入：消费 MOD-RK-14 is_breached 告警 → 人工介入处置工单
  （告警→工单→人审→关闭）。

LLM/DB/网络全 mock：修复引擎以 stub 注入，告警通道以 stub 注入，
所有落盘路径指向 tmp_path。
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from zephyr.security.ops.incident_pipeline import (
    COLD_START_LEDGER_FILENAME,
    FIXER_REGISTRY_FILENAME,
    PATTERN_INDEX_FILENAME,
    ChannelDecision,
    FaultClass,
    FixPatternStore,
    FixPatternStoreError,
    IncidentPipeline,
    IncidentPipelineError,
    InterventionStatus,
    PipelineConfig,
    WhitelistApprovalGate,
)
from zephyr.security.security_event_bus import SCHEMA_VERSION, SecurityEvent


def _event(
    *,
    threat_category: str = "resource_abuse",
    severity: str = "medium",
    evidence_ref: str = "runtime://probe/target",
    detail: dict | None = None,
) -> SecurityEvent:
    return SecurityEvent.from_raw(
        {
            "source_domain": "runtime",
            "threat_category": threat_category,
            "severity": severity,
            "evidence_ref": evidence_ref,
            "session_ref": "sess-probe",
            "schema_version": SCHEMA_VERSION,
            "detail": detail or {},
        }
    )


class _StubEngine:
    """修复引擎 stub——记录调用，返回可配置状态的 action。"""

    def __init__(self, status: str = "completed") -> None:
        self.calls: list[tuple[str, str, bool]] = []
        self._status = status

    def fix(self, action_type: str, target: str, dry_run: bool = False):
        self.calls.append((action_type, target, dry_run))
        return SimpleNamespace(
            action_id=f"act-{len(self.calls)}",
            action_type=action_type,
            target=target,
            status=self._status,
        )


class _StubAlerter:
    def __init__(self) -> None:
        self.events: list[SecurityEvent] = []

    def send(self, event: SecurityEvent) -> bool:
        self.events.append(event)
        return True


def _pipeline(tmp_path, *, engine=None, alerter=None) -> IncidentPipeline:
    config = PipelineConfig(
        store_dir=tmp_path / "fix_patterns",
        runtime_dir=tmp_path / "ops_runtime",
    )
    return IncidentPipeline(
        config,
        engine=engine if engine is not None else _StubEngine(),
        alerter=(alerter if alerter is not None else _StubAlerter()).send,
    )


def _read_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


STRUCTURAL_PROBE = {"error": "ModuleNotFoundError: no module named 'zephyr.foo_bar'"}
SEMANTIC_PROBE = {"error": "AssertionError: logic error in signal synthesis"}
BEHAVIORAL_PROBE = {
    "detector": "ai_agent_monitor",
    "state": "CRITICAL",
    "risk_score": 0.91,
    "is_breached": True,
}


class TestThreeChannelProbes:
    """P1-2：三类故障各一条探针全链路走通。"""

    def test_structural_probe_full_chain(self, tmp_path):
        engine = _StubEngine()
        pipe = _pipeline(tmp_path, engine=engine)
        record = pipe.consume_event(_event(detail=STRUCTURAL_PROBE))
        assert record.fault_class is FaultClass.STRUCTURAL
        assert record.channel is ChannelDecision.AUTO_TEMPLATE
        assert engine.calls, "结构类 MUST 直通模板化修复通道"
        action_type, target, _dry = engine.calls[0]
        assert action_type != "llm_fix", "结构类 MUST NOT 走 LLM 通道"
        assert target == "runtime://probe/target"
        assert record.action_status == "completed"
        assert not record.escalated
        assert record.kb_record_id, "修复动作 MUST 自动写知识库记录"

    def test_semantic_probe_full_chain_via_llm_bridge(self, tmp_path):
        engine = _StubEngine()
        pipe = _pipeline(tmp_path, engine=engine)
        record = pipe.consume_event(_event(detail=SEMANTIC_PROBE))
        assert record.fault_class is FaultClass.SEMANTIC
        assert record.channel is ChannelDecision.AUTO_LLM
        assert engine.calls, "语义类 MUST 过 LLM Bridge 修复通道"
        action_type, _target, _dry = engine.calls[0]
        assert action_type == "llm_fix", "语义类 MUST 走 LLM Bridge 入口（必经 LSG 闸）"
        assert record.action_status == "completed"

    def test_behavioral_probe_block_alert_never_auto_fix(self, tmp_path):
        engine = _StubEngine()
        alerter = _StubAlerter()
        pipe = _pipeline(tmp_path, engine=engine, alerter=alerter)
        record = pipe.consume_event(
            _event(threat_category="emergence", severity="high", detail=BEHAVIORAL_PROBE)
        )
        assert record.fault_class is FaultClass.BEHAVIORAL
        assert record.channel is ChannelDecision.BLOCK_ALERT
        assert engine.calls == [], "行为类探针 MUST NOT 触发自动修复（不变量）"
        assert record.alert_sent, "行为类 MUST Block+Alert"
        assert record.escalated, "行为类不可自动修 MUST 走 escalation 落盘"


class TestBehavioralInvariant:
    """P1-2 不变量：行为类探针 100% 不触发自动修复。"""

    @pytest.mark.parametrize(
        "threat_category",
        ["collusion", "emergence", "memory_poisoning", "privilege_violation"],
    )
    def test_behavioral_threats_never_call_engine(self, tmp_path, threat_category):
        engine = _StubEngine()
        pipe = _pipeline(tmp_path, engine=engine)
        record = pipe.consume_event(
            _event(threat_category=threat_category, severity="high", detail=BEHAVIORAL_PROBE)
        )
        assert record.fault_class is FaultClass.BEHAVIORAL
        assert record.channel is ChannelDecision.BLOCK_ALERT
        assert engine.calls == []


class TestDiagnosisAndEscalation:
    """P1-1：探针事件触发诊断记录；不可自动修的判决走 escalation 通道落盘。"""

    def test_probe_triggers_diagnosis_record(self, tmp_path):
        pipe = _pipeline(tmp_path)
        record = pipe.consume_event(_event(detail=STRUCTURAL_PROBE))
        incidents = _read_jsonl(tmp_path / "ops_runtime" / "incidents.jsonl")
        assert len(incidents) == 1
        diag = incidents[0]["diagnosis"]
        assert diag["event_id"] == record.event_id
        assert diag["suggestion"], "诊断记录 MUST 含纠正建议"
        assert diag["fault_class"] == "structural"

    def test_unfixable_verdict_goes_escalation(self, tmp_path):
        engine = _StubEngine(status="failed")
        pipe = _pipeline(tmp_path, engine=engine)
        record = pipe.consume_event(_event(detail=STRUCTURAL_PROBE))
        assert record.escalated
        entries = _read_jsonl(tmp_path / "ops_runtime" / "escalations.jsonl")
        assert len(entries) == 1
        assert entries[0]["incident_id"] == record.incident_id
        assert entries[0]["reason"], "escalation 落盘 MUST 含原因"

    def test_engine_exception_also_escalates(self, tmp_path):
        class _BoomEngine:
            def fix(self, action_type, target, dry_run=False):
                raise RuntimeError("engine exploded")

        pipe = _pipeline(tmp_path, engine=_BoomEngine())
        record = pipe.consume_event(_event(detail=STRUCTURAL_PROBE))
        assert record.escalated
        assert record.action_status == "engine_error"
        entries = _read_jsonl(tmp_path / "ops_runtime" / "escalations.jsonl")
        assert len(entries) == 1


class TestFixPatternStore:
    """P1-3：库文件存在且 schema 经校验；每次修复动作自动写一条记录。"""

    def test_kb_files_created_with_valid_schema(self, tmp_path):
        store = FixPatternStore(tmp_path / "fix_patterns")
        store.ensure_files()
        assert (tmp_path / "fix_patterns" / PATTERN_INDEX_FILENAME).exists()
        assert (tmp_path / "fix_patterns" / FIXER_REGISTRY_FILENAME).exists()
        index = store.read_pattern_index()
        registry = store.read_fixer_registry()
        store.validate_pattern_index(index)
        store.validate_fixer_registry(registry)

    def test_every_fix_action_appends_kb_record(self, tmp_path):
        pipe = _pipeline(tmp_path)
        pipe.consume_event(_event(detail=STRUCTURAL_PROBE, evidence_ref="runtime://probe/a"))
        pipe.consume_event(_event(detail=SEMANTIC_PROBE, evidence_ref="runtime://probe/b"))
        index = pipe.store.read_pattern_index()
        records = index["records"]
        assert len(records) == 2, "每次修复动作 MUST 自动写一条记录"
        assert records[0]["channel"] == "auto_template"
        assert records[1]["channel"] == "auto_llm"
        assert records[1]["lsg_gate"] is True, "语义类修复记录 MUST 标记 LSG 闸必经"
        for rec in records:
            assert rec["action_status"] == "completed"
            assert rec["record_id"] and rec["ts"] and rec["incident_id"]
        pipe.store.validate_pattern_index(index)

    def test_behavioral_block_writes_no_fix_record(self, tmp_path):
        pipe = _pipeline(tmp_path)
        pipe.consume_event(_event(threat_category="collusion", severity="high", detail=BEHAVIORAL_PROBE))
        index = pipe.store.read_pattern_index()
        assert index["records"] == [], "行为类无修复动作 MUST NOT 写修复记录"

    def test_schema_validation_rejects_bad_index(self):
        with pytest.raises(FixPatternStoreError):
            FixPatternStore.validate_pattern_index({"kind": "fix_pattern_index"})
        with pytest.raises(FixPatternStoreError):
            FixPatternStore.validate_pattern_index({"schema_version": "1.0", "records": "not-a-list"})

    def test_schema_validation_rejects_bad_registry(self):
        with pytest.raises(FixPatternStoreError):
            FixPatternStore.validate_fixer_registry({"schema_version": "1.0"})
        with pytest.raises(FixPatternStoreError):
            FixPatternStore.validate_fixer_registry(
                {"schema_version": "1.0", "fixers": [{"fixer_id": "x"}]}
            )


class TestWhitelistApproval:
    """P1-4：白名单变更走 human_gated 审批；未经审批的豁免 0 条。"""

    def test_unapproved_exemption_denied(self, tmp_path):
        pipe = _pipeline(tmp_path)
        granted = pipe.whitelist.request_exemption(
            path="src/zephyr/security/access_control/kill_switch.py",
            reason="probe exemption without approval",
        )
        assert granted is False, "未经审批的豁免 MUST 拒绝"
        entries = pipe.whitelist.entries()
        granted_entries = [e for e in entries if e["kind"] == "exemption_granted"]
        assert granted_entries == [], "未经审批的豁免 MUST 为 0 条"
        denied = [e for e in entries if e["kind"] == "exemption_denied"]
        assert len(denied) == 1, "拒绝 MUST 留痕"

    def test_approved_exemption_granted_with_audit(self, tmp_path):
        pipe = _pipeline(tmp_path)
        pipe.whitelist.approve(
            "APR-001",
            approver="owner",
            scope="protected_path_exemption",
            reason="人工审批留痕",
        )
        granted = pipe.whitelist.request_exemption(
            path="config/drift_thresholds.yaml",
            reason="approved probe",
            approval_id="APR-001",
        )
        assert granted is True
        entries = pipe.whitelist.entries()
        kinds = [e["kind"] for e in entries]
        assert "approval" in kinds and "exemption_granted" in kinds, "审批与豁免均 MUST 留痕"

    def test_approve_requires_approver(self, tmp_path):
        pipe = _pipeline(tmp_path)
        with pytest.raises(IncidentPipelineError):
            pipe.whitelist.approve("APR-002", approver="", scope="s", reason="r")

    def test_unknown_approval_id_denied(self, tmp_path):
        pipe = _pipeline(tmp_path)
        granted = pipe.whitelist.request_exemption(
            path="x", reason="r", approval_id="APR-NOT-EXIST"
        )
        assert granted is False


class TestEmergenceIntervention:
    """12号文 §4.4：is_breached 告警 → 人工介入处置工单（告警→工单→人审→关闭）。"""

    def _alert_event(self) -> SecurityEvent:
        return _event(threat_category="emergence", severity="high", detail=BEHAVIORAL_PROBE)

    def test_is_breached_alert_creates_ticket_via_pipeline(self, tmp_path):
        pipe = _pipeline(tmp_path)
        pipe.consume_event(self._alert_event())
        tickets = pipe.tickets.tickets()
        assert len(tickets) == 1, "涌现 is_breached 告警 MUST 产人工介入处置工单"
        ticket = tickets[0]
        assert ticket.status is InterventionStatus.TICKET_OPEN
        assert ticket.detector == "ai_agent_monitor"
        assert ticket.risk_score == pytest.approx(0.91)
        assert len(ticket.source_refs) == 3, "工单 MUST 含状态机/轨迹/指纹三源明细指针"

    def test_consume_emergence_alert_direct_and_idempotent(self, tmp_path):
        pipe = _pipeline(tmp_path)
        event = self._alert_event()
        t1 = pipe.consume_emergence_alert(event)
        t2 = pipe.consume_emergence_alert(event)
        assert t1.ticket_id == t2.ticket_id, "同一事件 MUST 幂等（不重复开工单）"

    def test_sop_flow_ticket_review_close(self, tmp_path):
        pipe = _pipeline(tmp_path)
        ticket = pipe.consume_emergence_alert(self._alert_event())
        reviewed = pipe.advance_intervention(
            ticket.ticket_id, to_status=InterventionStatus.HUMAN_REVIEW, actor="owner"
        )
        assert reviewed.status is InterventionStatus.HUMAN_REVIEW
        closed = pipe.advance_intervention(
            ticket.ticket_id, to_status=InterventionStatus.CLOSED, actor="owner"
        )
        assert closed.status is InterventionStatus.CLOSED
        persisted = pipe.tickets.get(ticket.ticket_id)
        assert persisted is not None and persisted.status is InterventionStatus.CLOSED

    def test_close_requires_human_actor(self, tmp_path):
        pipe = _pipeline(tmp_path)
        ticket = pipe.consume_emergence_alert(self._alert_event())
        pipe.advance_intervention(ticket.ticket_id, to_status=InterventionStatus.HUMAN_REVIEW, actor="owner")
        with pytest.raises(IncidentPipelineError):
            pipe.advance_intervention(ticket.ticket_id, to_status=InterventionStatus.CLOSED, actor="")

    def test_invalid_transition_rejected(self, tmp_path):
        pipe = _pipeline(tmp_path)
        ticket = pipe.consume_emergence_alert(self._alert_event())
        with pytest.raises(IncidentPipelineError):
            pipe.advance_intervention(ticket.ticket_id, to_status=InterventionStatus.CLOSED, actor="owner")
        with pytest.raises(IncidentPipelineError):
            pipe.advance_intervention("ticket-not-exist", to_status=InterventionStatus.HUMAN_REVIEW, actor="owner")

    def test_non_emergence_or_low_severity_rejected(self, tmp_path):
        pipe = _pipeline(tmp_path)
        with pytest.raises(IncidentPipelineError):
            pipe.consume_emergence_alert(_event(threat_category="injection", severity="high"))
        with pytest.raises(IncidentPipelineError):
            pipe.consume_emergence_alert(_event(threat_category="emergence", severity="low"))


class TestColdStartPatternImport:
    """P1-3①：failure_matcher 内置故障模式导出为 pattern_index 冷启动内容（幂等+留痕）。"""

    def test_cold_start_imports_builtin_patterns_when_empty(self, tmp_path):
        store = FixPatternStore(tmp_path / "fix_patterns")
        imported = store.ensure_cold_start_patterns()
        assert imported > 0, "空库 MUST 导入 failure_matcher 内置模式"
        index = store.read_pattern_index()
        patterns = index["patterns"]
        assert len(patterns) == imported
        names = {p["pattern_name"] for p in patterns}
        assert "iterative_retry_loop" in names, "FailurePatternMatcher 命名模式 MUST 导出"
        assert "category:syntax" in names, "FailureMatcher 九类分类模式 MUST 导出"
        matchers = {p["matcher"] for p in patterns}
        assert matchers == {"FailurePatternMatcher", "FailureMatcher"}
        for pat in patterns:
            assert pat["record_id"] and pat["ts"], "冷启动条目 MUST 含 record_id/ts"
            assert pat["kind"] == "cold_start_pattern"
            assert pat["source"] == "failure_matcher"
            assert pat["regex"] and pat["suggestion"]
        store.validate_pattern_index(index)

    def test_cold_start_import_event_audited(self, tmp_path):
        store = FixPatternStore(tmp_path / "fix_patterns")
        imported = store.ensure_cold_start_patterns()
        ledger = _read_jsonl(tmp_path / "fix_patterns" / COLD_START_LEDGER_FILENAME)
        assert len(ledger) == 1, "导入事件 MUST 落盘留痕"
        entry = ledger[0]
        assert entry["kind"] == "cold_start_import"
        assert entry["source"] == "zephyr.orchestrator.resilience.failure_matcher"
        assert entry["imported"] == imported
        assert entry["ts"]

    def test_cold_start_idempotent_non_empty_no_reimport(self, tmp_path):
        store = FixPatternStore(tmp_path / "fix_patterns")
        first = store.ensure_cold_start_patterns()
        second = store.ensure_cold_start_patterns()
        assert first > 0
        assert second == 0, "库非空 MUST NOT 重复导入（幂等）"
        index = store.read_pattern_index()
        assert len(index["patterns"]) == first
        ledger = _read_jsonl(tmp_path / "fix_patterns" / COLD_START_LEDGER_FILENAME)
        assert len(ledger) == 1, "幂等：重复调用 MUST NOT 重复留痕"

    def test_pipeline_init_triggers_cold_start_and_records_stay_clean(self, tmp_path):
        pipe = _pipeline(tmp_path)
        index = pipe.store.read_pattern_index()
        assert index.get("patterns"), "管线初始化 MUST 触发故障模式库冷启动"
        assert index["records"] == [], "冷启动内容 MUST NOT 混入修复记录（records 只装修复动作）"


class TestAuthorityRegistryGate:
    """P1-4：GOV-AI-001 实质对接——在册校验 + immutable 拒批 + 注册表不可读 fail-closed。"""

    @staticmethod
    def _gate(tmp_path, registry_path=None) -> WhitelistApprovalGate:
        kwargs = {} if registry_path is None else {"registry_path": registry_path}
        return WhitelistApprovalGate(tmp_path / "whitelist_ledger.jsonl", **kwargs)

    def test_registered_human_gated_target_granted_with_approval(self, tmp_path):
        gate = self._gate(tmp_path)
        gate.approve("APR-100", approver="owner", scope="protected_path_exemption", reason="r")
        granted = gate.request_exemption(
            path="config/drift_thresholds.yaml",
            reason="registered human-gated target",
            approval_id="APR-100",
        )
        assert granted is True, "在册 Human-Gated 目标 + 有效审批 MUST 授予"
        kinds = [e["kind"] for e in gate.entries()]
        assert "exemption_granted" in kinds

    def test_registered_human_gated_directory_prefix_match(self, tmp_path):
        gate = self._gate(tmp_path)
        gate.approve("APR-101", approver="owner", scope="s", reason="r")
        granted = gate.request_exemption(
            path="src/zephyr/shared/alerts/alert_precision_tracker.py",
            reason="dir prefix match",
            approval_id="APR-101",
        )
        assert granted is True, "目录前缀命中在册 Human-Gated 条目（src/zephyr/shared/）MUST 可批"

    def test_immutable_core_target_denied_even_with_approval(self, tmp_path):
        gate = self._gate(tmp_path)
        gate.approve("APR-102", approver="owner", scope="s", reason="r")
        granted = gate.request_exemption(
            path="src/zephyr/risk/engine.py", reason="immutable probe", approval_id="APR-102"
        )
        assert granted is False, "Immutable Core 目标豁免请求 MUST 一律拒"
        denied = [e for e in gate.entries() if e["kind"] == "exemption_denied"]
        assert len(denied) == 1
        assert denied[0]["denial_reason"] == "immutable_core_target"
        granted_entries = [e for e in gate.entries() if e["kind"] == "exemption_granted"]
        assert granted_entries == [], "immutable 目标 MUST 0 条授予"

    def test_unregistered_target_denied(self, tmp_path):
        gate = self._gate(tmp_path)
        gate.approve("APR-103", approver="owner", scope="s", reason="r")
        granted = gate.request_exemption(
            path="src/zephyr/not_registered/x.py", reason="r", approval_id="APR-103"
        )
        assert granted is False, "豁免目标 MUST 在 GOV-AI-001 注册表在册"
        denied = [e for e in gate.entries() if e["kind"] == "exemption_denied"]
        assert len(denied) == 1
        assert denied[0]["denial_reason"] == "target_not_in_authority_registry"

    def test_registry_unavailable_fail_closed(self, tmp_path):
        gate = self._gate(tmp_path, registry_path=tmp_path / "missing_registry.yaml")
        gate.approve("APR-104", approver="owner", scope="s", reason="r")
        granted = gate.request_exemption(
            path="config/drift_thresholds.yaml", reason="r", approval_id="APR-104"
        )
        assert granted is False, "注册表不可读 MUST fail-closed 拒批"
        denied = [e for e in gate.entries() if e["kind"] == "exemption_denied"]
        assert len(denied) == 1
        assert denied[0]["denial_reason"] == "authority_registry_unavailable"

    def test_registry_malformed_fail_closed(self, tmp_path):
        bad = tmp_path / "bad_registry.yaml"
        bad.write_text("- this\n- is a list not a registry\n", encoding="utf-8")
        gate = self._gate(tmp_path, registry_path=bad)
        gate.approve("APR-105", approver="owner", scope="s", reason="r")
        granted = gate.request_exemption(
            path="config/drift_thresholds.yaml", reason="r", approval_id="APR-105"
        )
        assert granted is False, "注册表解析结果非 mapping MUST fail-closed 拒批"

    def test_pipeline_config_overrides_registry_path(self, tmp_path):
        config = PipelineConfig(
            store_dir=tmp_path / "fix_patterns",
            runtime_dir=tmp_path / "ops_runtime",
            authority_registry_path=tmp_path / "missing.yaml",
        )
        pipe = IncidentPipeline(config, engine=_StubEngine())
        pipe.whitelist.approve("APR-106", approver="owner", scope="s", reason="r")
        granted = pipe.whitelist.request_exemption(
            path="config/drift_thresholds.yaml", reason="r", approval_id="APR-106"
        )
        assert granted is False, "管线注入的注册表路径不可读时 MUST fail-closed"
