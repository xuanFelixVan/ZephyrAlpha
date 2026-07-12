# [A_test] module_id: SRC-TST-0010 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-205 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_audit_integration_fracture
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""审计链集成断裂面红白对抗测试 — MOD-INF-020 v1.4.0

验证所有审计流已统一接入核心 AuditWriter 不可变审计链，
不存在桩实现绕过或独立审计流逃逸。

攻击向量
--------
  I1: 治理层桩AuditWriter绕过 — governance.contracts.AuditWriter.write() 必须写入核心链
  I2: rollback_executor独立审计流逃逸 — 审计记录必须出现在核心 events.jsonl
  I3: rollback_audit_nexus独立审计流逃逸 — 同上
  I4: drift_hotfix_bypass独立审计流逃逸 — 同上
  I5: mcp_audit_logger独立审计流逃逸 — 同上
  I6: gates_audit_chain_verifier独立审计流逃逸 — 同上
  I7: skill_executor内存审计丢失 — session结束后审计记录必须持久化
  I8: AuditWriter写入失败保护 — 连续5次失败后必须进入readonly模式
  I9: 核心模型强制消费 — event_type必须经过AuditEventType验证
"""

from __future__ import annotations

import json
import shutil

import pytest


@pytest.fixture
def audit_env(tmp_path):
    data_dir = tmp_path / "audit-trail"
    data_dir.mkdir(parents=True, exist_ok=True)
    yield tmp_path, data_dir
    shutil.rmtree(tmp_path, ignore_errors=True)


class TestGovernanceContractsIntegration:
    """I1: 治理层桩AuditWriter必须写入核心链."""

    def test_contracts_writes_to_core_chain(self, audit_env):
        import zephyr.gov_audit.writer as writer_mod
        from zephyr.gov_audit.contracts import AuditWriter as GovAuditWriter
        from zephyr.gov_audit.writer import AuditWriter

        tmp_path, data_dir = audit_env
        writer = AuditWriter(data_dir=data_dir)

        writer_mod._GLOBAL_WRITER = writer

        record = GovAuditWriter.write(
            agent_id="test_agent",
            permission="read",
            resource="test_resource",
            decision_basis="test_decision",
            session_id="test_session",
            granted=True,
        )

        assert "chain_hash" in record, "contracts AuditWriter.write() must return chain_hash"

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after write"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1, "at least one event must be written"

        event = json.loads(lines[-1])
        assert event.get("event_type") == "rbac_decision"
        assert event.get("agent_id") == "test_agent"
        assert "prev_hash" in event, "event must have prev_hash (hash chain)"
        assert "entry_hash" in event, "event must have entry_hash"
        assert "hmac_signature" in event, "event must have hmac_signature"

        writer_mod._GLOBAL_WRITER = None


class TestRollbackExecutorIntegration:
    """I2: rollback_executor审计必须写入核心链."""

    def test_rollback_executor_writes_to_core(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter
        from zephyr.infrastructure.rollback.rollback_executor import DiscardDecision, RollbackExecutor

        writer = AuditWriter(data_dir=data_dir)
        executor = RollbackExecutor(project_root=tmp_path)
        executor._audit_writer = writer

        record = executor._build_discard_audit(
            decision=DiscardDecision.NO_CHANGES,
            files=["test.py"],
            blocked=[],
            reason="test",
            audit_session="test_session",
        )
        executor._write_audit_log(record)

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after rollback audit write"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1

        event = json.loads(lines[-1])
        assert event.get("event_type") == "rollback_discard"


class TestRollbackAuditNexusIntegration:
    """I3: rollback_audit_nexus审计必须写入核心链."""

    def test_nexus_writes_to_core(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter
        from zephyr.infrastructure.rollback.rollback_audit_nexus import AuditEvent, RollbackAuditNexus

        writer = AuditWriter(data_dir=data_dir)
        nexus = RollbackAuditNexus(project_root=tmp_path)
        nexus._core_writer = writer

        event = AuditEvent(
            event_id="test-001",
            event_type="full_revert",
            timestamp_utc="2026-01-01T00:00:00Z",
            operator="test_agent",
            module="MOD-INF-021",
            target_commit="abc123",
            result_commit="def456",
            success=True,
        )
        nexus.publish(event)

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after nexus publish"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1

        core_event = json.loads(lines[-1])
        assert core_event.get("event_type") == "rollback_nexus"
        assert core_event.get("agent_id") == "test_agent"


class TestDriftHotfixBypassIntegration:
    """I4: drift_hotfix_bypass审计必须写入核心链."""

    def test_hotfix_writes_to_core(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_drift.drift_hotfix_bypass import HotfixBypass
        from zephyr.gov_audit.writer import AuditWriter

        writer = AuditWriter(data_dir=data_dir)
        bypass = HotfixBypass(project_root=str(tmp_path))
        bypass._core_writer = writer

        entry = bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] critical fix",
            module_ids=["MOD-INF-020"],
            affected_dimensions=["d5"],
            owner_ack="test_owner",
        )

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after hotfix audit"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1

        core_event = json.loads(lines[-1])
        assert core_event.get("event_type") == "drift_hotfix_bypass"


class TestMCPAuditLoggerIntegration:
    """I5: mcp_audit_logger审计必须写入核心链."""

    def test_mcp_audit_writes_to_core(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter
        from zephyr.integration.mcp.audit_logger import AuditLogger

        writer = AuditWriter(data_dir=data_dir)
        logger = AuditLogger(log_dir=tmp_path / "logs" / "mcp_audit")
        logger._core_writer = writer

        logger.log_call(
            client_session_id="test_session",
            tool_name="test_tool",
            result_status="success",
            duration_ms=100,
        )

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after MCP audit"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1

        core_event = json.loads(lines[-1])
        assert core_event.get("event_type") == "mcp_tool_call"


class TestGatesAuditChainVerifierIntegration:
    """I6: gates_audit_chain_verifier审计必须写入核心链."""

    def test_gate_verifier_writes_to_core(self, audit_env):
        tmp_path, data_dir = audit_env
        import datetime

        from zephyr.gov_audit.writer import AuditWriter
        from zephyr.governance.rule_enforcement.audit_chain_verifier import AuditChainVerifier
        from zephyr.governance.rule_enforcement.gate_engine.gate_context import GateResult, GateStatus

        writer = AuditWriter(data_dir=data_dir)
        verifier = AuditChainVerifier()
        verifier._core_writer = writer

        result = GateResult(
            gate_id="G0",
            status=GateStatus.PASS,
            reasons=["test"],
            timestamp=datetime.datetime.now(datetime.UTC),
        )
        verifier.append("G0", result)

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after gate audit"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1

        core_event = json.loads(lines[-1])
        assert core_event.get("event_type") == "gate_audit"


class TestSkillExecutorIntegration:
    """I7: skill_executor审计必须持久化到核心链."""

    def test_skill_executor_persists_audit(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.autonomy_core.skills.skill_executor import SkillExecutor
        from zephyr.gov_audit.writer import AuditWriter

        writer = AuditWriter(data_dir=data_dir)
        executor = SkillExecutor()
        executor._core_writer = writer

        entry = executor._write_audit("skill_loaded", "test_skill", {"trigger": "test"})

        assert entry is not None
        assert len(executor.audit_log) == 1, "in-memory audit_log must still work"

        events_file = data_dir / "events.jsonl"
        assert events_file.exists(), "events.jsonl must exist after skill audit"

        with open(events_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1, "audit must be persisted to core chain"

        core_event = json.loads(lines[-1])
        assert core_event.get("event_type") == "skill_loaded"


class TestAuditWriterWriteFailureProtection:
    """I8: AuditWriter写入失败保护——连续5次失败后进入readonly."""

    def test_readonly_after_consecutive_failures(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter

        writer = AuditWriter(data_dir=data_dir)
        writer._event_log_path = data_dir / "nonexistent" / "deep" / "events.jsonl"

        for i in range(5):
            try:
                writer.write({"event_type": "test", "agent_id": "test"})
            except Exception:
                pass

        assert writer._readonly is True, "AuditWriter must enter readonly after 5 failures"

        with pytest.raises(RuntimeError, match="readonly mode"):
            writer.write({"event_type": "test", "agent_id": "test"})


class TestCoreModelEnforcement:
    """I9: 核心模型AuditEntryV1强制消费——event_type必须经过验证."""

    def test_event_type_validation(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter

        writer = AuditWriter(data_dir=data_dir)
        writer.write({"event_type": "file_write", "agent_id": "test"})

        events_file = data_dir / "events.jsonl"
        with open(events_file, encoding="utf-8") as f:
            event = json.loads(f.readline())

        assert event.get("event_type") == "file_write"
        assert event.get("provenance") == "direct_agent"

    def test_unknown_event_type_normalized(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter

        writer = AuditWriter(data_dir=data_dir)
        writer.write({"event_type": "completely_invalid_type", "agent_id": "test"})

        events_file = data_dir / "events.jsonl"
        with open(events_file, encoding="utf-8") as f:
            event = json.loads(f.readline())

        assert event.get("event_type") == "unknown", "invalid event_type must be normalized to 'unknown'"


class TestCrossModuleAuditConsistency:
    """跨模块审计一致性验证——所有模块写入的事件必须在同一核心链中."""

    def test_all_modules_share_same_chain(self, audit_env):
        tmp_path, data_dir = audit_env
        from zephyr.gov_audit.writer import AuditWriter
        from zephyr.governance.integrity import IntegrityVerifier

        writer = AuditWriter(data_dir=data_dir)

        writer.write({"event_type": "file_write", "agent_id": "pipeline", "session_id": "s1"})
        writer.write({"event_type": "rbac_decision", "agent_id": "rbac", "session_id": "s1"})
        writer.write({"event_type": "rollback_operation", "agent_id": "rollback", "session_id": "s1"})
        writer.write({"event_type": "mcp_tool_call", "agent_id": "mcp", "session_id": "s1"})
        writer.write({"event_type": "gate_audit", "agent_id": "gate", "session_id": "s1"})

        verifier = IntegrityVerifier(event_log_path=data_dir / "events.jsonl")
        report = verifier.verify_chain()

        assert report.get("status") == "valid", f"chain must be valid after multi-module writes: {report}"
        assert report.get("events_checked") == 5
