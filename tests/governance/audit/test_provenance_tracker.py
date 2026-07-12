# [A_test] module_id: SRC-TST-1416 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-420 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_provenance_tracker
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

from zephyr.gov_audit.provenance_tracker import (
    ProvenanceRecord,
    embed_provenance,
    extract_provenance,
    generate_provenance,
    is_session_owned,
    provenance_key,
)


class TestProvenanceRecord:
    def test_create_record(self):
        rec = ProvenanceRecord(
            module_id="MOD-001",
            source_section="§2",
            agent_session_id="session-001",
            generated_at="2026-01-01T00:00:00Z",
        )
        assert rec.module_id == "MOD-001"
        assert rec.source_section == "§2"
        assert rec.agent_session_id == "session-001"

    def test_record_is_pydantic(self):
        rec = ProvenanceRecord(
            module_id="M",
            source_section="S",
            agent_session_id="A",
            generated_at="2026-01-01",
        )
        assert hasattr(rec, "model_dump")
        d = rec.model_dump()
        assert "module_id" in d


class TestGenerateProvenance:
    def test_generates_record(self):
        rec = generate_provenance(module_id="MOD-001", source_section="§3")
        assert rec.module_id == "MOD-001"
        assert rec.source_section == "§3"
        assert rec.generated_at != ""

    def test_default_session_id(self):
        rec = generate_provenance(module_id="MOD-001", source_section="§1")
        assert "session" in rec.agent_session_id

    def test_custom_session_id(self):
        rec = generate_provenance(
            module_id="MOD-001",
            source_section="§1",
            agent_session_id="custom-session",
        )
        assert rec.agent_session_id == "custom-session"


class TestEmbedProvenance:
    def test_embed_in_dict(self):
        rec = generate_provenance(module_id="MOD-001", source_section="§1")
        target = {"key": "value"}
        result = embed_provenance(target, rec)
        assert "__provenance__" in result
        assert result["__provenance__"]["module_id"] == "MOD-001"

    def test_embed_preserves_existing_keys(self):
        rec = generate_provenance(module_id="MOD-002", source_section="§2")
        target = {"existing": "data"}
        result = embed_provenance(target, rec)
        assert result["existing"] == "data"
        assert "__provenance__" in result


class TestExtractProvenance:
    def test_extract_from_dict_with_provenance(self):
        rec = generate_provenance(module_id="MOD-001", source_section="§1")

        class DictLike:
            __provenance__ = {
                "module_id": "MOD-001",
                "source_section": "§1",
                "agent_session_id": rec.agent_session_id,
                "generated_at": rec.generated_at,
            }

        extracted = extract_provenance(DictLike())
        assert extracted is not None
        assert extracted.module_id == "MOD-001"

    def test_extract_from_object_without_provenance(self):
        class NoProv:
            value = 42

        obj = NoProv()
        result = extract_provenance(obj)
        assert result is None

    def test_extract_from_object_with_zephyr_provenance(self):
        class WithProv:
            _zephyr_provenance = {
                "module_id": "MOD-003",
                "source_section": "§5",
                "agent_session_id": "session-xyz",
                "generated_at": "2026-01-01",
            }

        obj = WithProv()
        result = extract_provenance(obj)
        assert result is not None
        assert result.module_id == "MOD-003"


class TestIsSessionOwned:
    def test_matching_session(self):
        rec = ProvenanceRecord(
            module_id="M",
            source_section="S",
            agent_session_id="session-123",
            generated_at="2026-01-01",
        )
        assert is_session_owned(rec, "session-123") is True

    def test_non_matching_session(self):
        rec = ProvenanceRecord(
            module_id="M",
            source_section="S",
            agent_session_id="session-123",
            generated_at="2026-01-01",
        )
        assert is_session_owned(rec, "session-456") is False


class TestProvenanceKey:
    def test_key_format(self):
        rec = ProvenanceRecord(
            module_id="MOD-001",
            source_section="§2",
            agent_session_id="session-1",
            generated_at="2026-01-01",
        )
        key = provenance_key(rec)
        assert key == "MOD-001/§2"
