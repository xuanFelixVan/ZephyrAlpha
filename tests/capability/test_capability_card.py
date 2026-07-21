# [A_test] module_id: MOD-GOV_capability_card | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_capability_card
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_capability_card.py
# [TTL] task_bound

from __future__ import annotations

import pytest
from pydantic import ValidationError

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory


class TestCapabilityCategory:
    def test_all_categories_exist(self):
        expected = [
            "embedding",
            "inference",
            "search",
            "rerank",
            "governance",
            "infra",
            "orchestration",
            "data",
            "security",
            "observability",
            "coordination",
        ]
        actual = [c.value for c in CapabilityCategory]
        for e in expected:
            assert e in actual

    def test_category_is_string_enum(self):
        assert isinstance(CapabilityCategory.EMBEDDING, str)
        assert CapabilityCategory.EMBEDDING == "embedding"


class TestCapabilityCardInit:
    def test_minimal_init(self):
        card = CapabilityCard(
            capability_id="test-card",
            name="Test Card",
            category=CapabilityCategory.INFRA,
            description="A test card",
        )
        assert card.capability_id == "test-card"
        assert card.name == "Test Card"
        assert card.category == CapabilityCategory.INFRA
        assert card.description == "A test card"

    def test_defaults(self):
        card = CapabilityCard(
            capability_id="c1",
            name="C1",
            category=CapabilityCategory.DATA,
            description="d",
        )
        assert card.input_schema == {}
        assert card.output_schema == {}
        assert card.tags == []
        assert card.priority == "P1"
        assert card.runtime_plane == "warm"
        assert card.requires_human is False
        assert card.status == "ACTIVE"
        assert card.examples == []
        assert card.registered_at != ""

    def test_full_init(self):
        card = CapabilityCard(
            capability_id="full-card",
            name="Full Card",
            category=CapabilityCategory.SECURITY,
            description="Full test",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
            tags=["security", "test"],
            priority="P0",
            runtime_plane="hot",
            requires_human=True,
            status="DEGRADED",
            examples=[{"input": "x", "output": "y"}],
        )
        assert card.priority == "P0"
        assert card.runtime_plane == "hot"
        assert card.requires_human is True
        assert card.status == "DEGRADED"
        assert len(card.tags) == 2
        assert len(card.examples) == 1


class TestCapabilityCardValidation:
    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CapabilityCard()

    def test_missing_capability_id(self):
        with pytest.raises(ValidationError):
            CapabilityCard(name="N", category=CapabilityCategory.INFRA, description="d")

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            CapabilityCard(capability_id="c", category=CapabilityCategory.INFRA, description="d")

    def test_missing_category(self):
        with pytest.raises(ValidationError):
            CapabilityCard(capability_id="c", name="N", description="d")

    def test_missing_description(self):
        with pytest.raises(ValidationError):
            CapabilityCard(capability_id="c", name="N", category=CapabilityCategory.INFRA)

    def test_invalid_category(self):
        with pytest.raises(ValidationError):
            CapabilityCard(
                capability_id="c",
                name="N",
                category="nonexistent",
                description="d",
            )


class TestCapabilityCardModelDump:
    def test_model_dump_roundtrip(self):
        card = CapabilityCard(
            capability_id="rt",
            name="Roundtrip",
            category=CapabilityCategory.ORCHESTRATION,
            description="roundtrip test",
            tags=["a"],
        )
        data = card.model_dump()
        assert data["capability_id"] == "rt"
        assert data["category"] == "orchestration"
        assert data["tags"] == ["a"]

    def test_model_dump_json(self):
        card = CapabilityCard(
            capability_id="json-test",
            name="JSON Test",
            category=CapabilityCategory.EMBEDDING,
            description="json test",
        )
        json_str = card.model_dump_json()
        assert "json-test" in json_str
        assert "embedding" in json_str


class TestCapabilityCardEquality:
    def test_same_id_not_equal_by_default(self):
        c1 = CapabilityCard(
            capability_id="eq",
            name="Eq",
            category=CapabilityCategory.INFRA,
            description="d1",
        )
        c2 = CapabilityCard(
            capability_id="eq",
            name="Eq",
            category=CapabilityCategory.INFRA,
            description="d2",
        )
        assert c1 != c2

    def test_identical_cards_equal(self):
        c1 = CapabilityCard(
            capability_id="eq",
            name="Eq",
            category=CapabilityCategory.INFRA,
            description="d",
        )
        c2 = CapabilityCard(
            capability_id="eq",
            name="Eq",
            category=CapabilityCategory.INFRA,
            description="d",
        )
        assert c1 == c2
