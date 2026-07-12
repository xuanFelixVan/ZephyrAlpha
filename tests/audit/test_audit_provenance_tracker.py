# [A_test] module_id: SRC-TST-0362 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_provenance_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.provenance_tracker import (
    ProvenanceRecord,
    embed_provenance,
    extract_provenance,
    generate_provenance,
    is_session_owned,
    provenance_key,
)


class TestProvenanceRecord:
    def test_create(self):
        record = ProvenanceRecord(
            module_id="MOD-001",
            source_section="§2",
            agent_session_id="session-001",
            generated_at="2026-01-01T00:00:00Z",
        )
        assert record.module_id == "MOD-001"
        assert record.source_section == "§2"
        assert record.agent_session_id == "session-001"

    def test_required_fields(self):
        with pytest.raises(Exception):
            ProvenanceRecord()


class TestGenerateProvenance:
    def test_generates_record(self):
        record = generate_provenance(
            module_id="MOD-002",
            source_section="§3",
            agent_session_id="session-002",
        )
        assert isinstance(record, ProvenanceRecord)
        assert record.module_id == "MOD-002"
        assert record.source_section == "§3"
        assert record.agent_session_id == "session-002"
        assert record.generated_at != ""

    def test_default_session_id(self):
        record = generate_provenance(module_id="MOD-003", source_section="§1")
        assert record.agent_session_id == "session-20260507-005"

    def test_generated_at_is_isoformat(self):
        record = generate_provenance(module_id="MOD-004", source_section="§1")
        assert "T" in record.generated_at


class TestEmbedProvenance:
    def test_embeds_into_dict(self):
        record = generate_provenance(module_id="MOD-005", source_section="§1")
        target = {"key": "value"}
        result = embed_provenance(target, record)
        assert "__provenance__" in result
        assert result["__provenance__"]["module_id"] == "MOD-005"

    def test_preserves_existing_keys(self):
        record = generate_provenance(module_id="MOD-006", source_section="§1")
        target = {"existing": "data"}
        result = embed_provenance(target, record)
        assert result["existing"] == "data"
        assert "__provenance__" in result

    def test_returns_same_dict(self):
        record = generate_provenance(module_id="MOD-007", source_section="§1")
        target = {}
        result = embed_provenance(target, record)
        assert result is target


class TestExtractProvenance:
    def test_extract_from_dict_with_provenance_key(self):
        record = generate_provenance(module_id="MOD-008", source_section="§2")
        target = {}
        embed_provenance(target, record)
        prov = target.get("__provenance__")
        assert prov is not None
        assert prov["module_id"] == "MOD-008"

    def test_extract_from_object_attribute(self):
        class FakeObj:
            _zephyr_provenance = {
                "module_id": "MOD-009",
                "source_section": "§3",
                "agent_session_id": "session-009",
                "generated_at": "2026-01-01T00:00:00Z",
            }

        extracted = extract_provenance(FakeObj())
        assert extracted is not None
        assert extracted.module_id == "MOD-009"

    def test_extract_returns_none_for_missing(self):
        class EmptyObj:
            __dict__ = {}

        extracted = extract_provenance(EmptyObj())
        assert extracted is None

    def test_extract_returns_none_for_non_dict(self):
        class BadObj:
            _zephyr_provenance = "not a dict"

        extracted = extract_provenance(BadObj())
        assert extracted is None


class TestIsSessionOwned:
    def test_matching_session(self):
        record = ProvenanceRecord(
            module_id="M1",
            source_section="§1",
            agent_session_id="session-123",
            generated_at="2026-01-01T00:00:00Z",
        )
        assert is_session_owned(record, "session-123") is True

    def test_non_matching_session(self):
        record = ProvenanceRecord(
            module_id="M1",
            source_section="§1",
            agent_session_id="session-123",
            generated_at="2026-01-01T00:00:00Z",
        )
        assert is_session_owned(record, "session-456") is False


class TestProvenanceKey:
    def test_key_format(self):
        record = ProvenanceRecord(
            module_id="MOD-010",
            source_section="§5",
            agent_session_id="session-010",
            generated_at="2026-01-01T00:00:00Z",
        )
        key = provenance_key(record)
        assert key == "MOD-010/§5"

    def test_different_records_different_keys(self):
        r1 = ProvenanceRecord(
            module_id="M1",
            source_section="§1",
            agent_session_id="s1",
            generated_at="2026-01-01T00:00:00Z",
        )
        r2 = ProvenanceRecord(
            module_id="M2",
            source_section="§2",
            agent_session_id="s2",
            generated_at="2026-01-01T00:00:00Z",
        )
        assert provenance_key(r1) != provenance_key(r2)
