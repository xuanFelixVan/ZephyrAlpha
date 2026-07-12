# [A_test] module_id: SRC-TST-0884 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_external_tool_audit
# [INVARIANTS] ExternalToolCallAuditor chain depth tracking; validation logic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.external_tool_audit import (
    ChainValidationResult,
    ExternalToolCallAuditor,
    ToolCallRecord,
    ToolCallStatus,
)


class TestToolCallStatus:
    def test_enum_values(self):
        assert ToolCallStatus.PENDING == "pending"
        assert ToolCallStatus.SUCCESS == "success"
        assert ToolCallStatus.FAILED == "failed"
        assert ToolCallStatus.TIMEOUT == "timeout"
        assert ToolCallStatus.BLOCKED == "blocked"


class TestToolCallRecord:
    def test_default_values(self):
        record = ToolCallRecord()
        assert record.call_id == ""
        assert record.tool_name == ""
        assert record.status == ToolCallStatus.PENDING
        assert record.chain_depth == 0
        assert record.metadata == {}

    def test_custom_values(self):
        record = ToolCallRecord(
            call_id="TOOL-abc",
            tool_name="shell",
            tool_type="mcp",
            caller_agent="agent-1",
            status=ToolCallStatus.SUCCESS,
        )
        assert record.call_id == "TOOL-abc"
        assert record.status == ToolCallStatus.SUCCESS


class TestChainValidationResult:
    def test_default_values(self):
        result = ChainValidationResult()
        assert result.is_valid is True
        assert result.chain_length == 0
        assert result.issues == []
        assert result.chain == []


class TestExternalToolCallAuditorInstantiation:
    def test_default_max_depth(self):
        auditor = ExternalToolCallAuditor()
        assert auditor._max_chain_depth == 10

    def test_custom_max_depth(self):
        auditor = ExternalToolCallAuditor(max_chain_depth=5)
        assert auditor._max_chain_depth == 5


class TestExternalToolCallAuditorAuditCall:
    def test_audit_call_returns_record(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(
            tool_name="shell",
            tool_type="mcp",
            caller_agent="agent-1",
        )
        assert isinstance(record, ToolCallRecord)
        assert record.tool_name == "shell"
        assert record.tool_type == "mcp"
        assert record.caller_agent == "agent-1"
        assert record.call_id.startswith("TOOL-")
        assert record.chain_depth == 0

    def test_audit_call_with_parent(self):
        auditor = ExternalToolCallAuditor()
        parent = auditor.audit_call(tool_name="shell", tool_type="mcp", caller_agent="a0")
        child = auditor.audit_call(
            tool_name="subprocess",
            tool_type="shell",
            caller_agent="a1",
            parent_call_id=parent.call_id,
        )
        assert child.chain_depth == 1
        assert child.parent_call_id == parent.call_id

    def test_audit_call_with_input_output_hash(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(
            tool_name="tool",
            tool_type="api",
            caller_agent="a1",
            input_data="hello",
            output_data="world",
        )
        assert record.input_hash != ""
        assert record.output_hash != ""

    def test_audit_call_empty_input_no_hash(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(
            tool_name="tool",
            tool_type="api",
            caller_agent="a1",
            input_data="",
            output_data="",
        )
        assert record.input_hash == ""
        assert record.output_hash == ""

    def test_audit_call_custom_status(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(
            tool_name="tool",
            tool_type="api",
            caller_agent="a1",
            status=ToolCallStatus.FAILED,
        )
        assert record.status == ToolCallStatus.FAILED

    def test_audit_call_with_metadata(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(
            tool_name="tool",
            tool_type="api",
            caller_agent="a1",
            metadata={"key": "value"},
        )
        assert record.metadata == {"key": "value"}


class TestExternalToolCallAuditorValidateChain:
    def test_validate_single_call(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(tool_name="tool", tool_type="api", caller_agent="a1")
        result = auditor.validate_chain(record.call_id)
        assert result.is_valid is True
        assert result.chain_length == 1

    def test_validate_chain_with_parent(self):
        auditor = ExternalToolCallAuditor()
        parent = auditor.audit_call(tool_name="p", tool_type="api", caller_agent="a0")
        child = auditor.audit_call(tool_name="c", tool_type="api", caller_agent="a1", parent_call_id=parent.call_id)
        result = auditor.validate_chain(child.call_id)
        assert result.is_valid is True
        assert result.chain_length == 2

    def test_validate_nonexistent_call(self):
        auditor = ExternalToolCallAuditor()
        result = auditor.validate_chain("NONEXISTENT")
        assert result.is_valid is True
        assert result.chain_length == 0

    def test_validate_chain_exceeds_depth(self):
        auditor = ExternalToolCallAuditor(max_chain_depth=2)
        r0 = auditor.audit_call(tool_name="t0", tool_type="api", caller_agent="a0")
        r1 = auditor.audit_call(tool_name="t1", tool_type="api", caller_agent="a1", parent_call_id=r0.call_id)
        r2 = auditor.audit_call(tool_name="t2", tool_type="api", caller_agent="a2", parent_call_id=r1.call_id)
        result = auditor.validate_chain(r2.call_id)
        assert result.is_valid is False
        assert any("exceeds maximum" in issue for issue in result.issues)


class TestExternalToolCallAuditorGetCall:
    def test_get_existing_call(self):
        auditor = ExternalToolCallAuditor()
        record = auditor.audit_call(tool_name="tool", tool_type="api", caller_agent="a1")
        retrieved = auditor.get_call(record.call_id)
        assert retrieved is not None
        assert retrieved.call_id == record.call_id

    def test_get_nonexistent_call(self):
        auditor = ExternalToolCallAuditor()
        assert auditor.get_call("NONEXISTENT") is None


class TestExternalToolCallAuditorGetByAgent:
    def test_get_calls_by_agent(self):
        auditor = ExternalToolCallAuditor()
        auditor.audit_call(tool_name="t1", tool_type="api", caller_agent="a1")
        auditor.audit_call(tool_name="t2", tool_type="api", caller_agent="a1")
        auditor.audit_call(tool_name="t3", tool_type="api", caller_agent="a2")
        calls = auditor.get_calls_by_agent("a1")
        assert len(calls) == 2

    def test_get_calls_by_agent_empty(self):
        auditor = ExternalToolCallAuditor()
        calls = auditor.get_calls_by_agent("nonexistent")
        assert calls == []


class TestExternalToolCallAuditorGetBySession:
    def test_get_calls_by_session(self):
        auditor = ExternalToolCallAuditor()
        auditor.audit_call(tool_name="t1", tool_type="api", caller_agent="a1", session_id="s1")
        auditor.audit_call(tool_name="t2", tool_type="api", caller_agent="a2", session_id="s1")
        auditor.audit_call(tool_name="t3", tool_type="api", caller_agent="a3", session_id="s2")
        calls = auditor.get_calls_by_session("s1")
        assert len(calls) == 2
