# [A_test] module_id: MOD-GOV_skill_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_model
# [INVARIANTS] skill_id must match pattern; freshness_score in [0,100]
# [MODIFY-GUARD] changes require review of skill_model.py schema
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError on invalid skill_id or out-of-range freshness_score
# [TESTS] pytest tests/test_skill_model.py -q
# [TTL] task_bound

from datetime import datetime

import pytest
from pydantic import ValidationError

from zephyr.autonomy_core.skills.skill_model import (
    ProgressiveLevel,
    SkillModel,
    SkillStatus,
    SkillTier,
    SkillType,
)

_VALID_KWARGS = {
    "skill_id": "SKILL-DOM-TS-001",
    "name": "Test Skill",
    "description": "A test skill",
    "skill_type": SkillType.DOMAIN,
    "tier": SkillTier.L1_DOMAIN,
    "allowed_tools": ["read_file", "grep"],
    "path": "skills/domain/test.md",
}


class TestSkillTier:
    def test_all_tiers_exist(self):
        assert SkillTier.L0_CONSTITUTION == "L0"
        assert SkillTier.L1_DOMAIN == "L1"
        assert SkillTier.L2_ROLE == "L2"
        assert SkillTier.L3_COLD_MEMORY == "L3"

    def test_tier_is_str(self):
        assert isinstance(SkillTier.L0_CONSTITUTION, str)


class TestSkillType:
    def test_types(self):
        assert SkillType.DOMAIN == "domain"
        assert SkillType.ROLE == "role"


class TestSkillStatus:
    def test_all_statuses(self):
        assert SkillStatus.DRAFT == "draft"
        assert SkillStatus.ACTIVE == "active"
        assert SkillStatus.DEPRECATED == "deprecated"
        assert SkillStatus.RETIRED == "retired"
        assert SkillStatus.REMOVED == "removed"


class TestProgressiveLevel:
    def test_all_levels(self):
        assert ProgressiveLevel.L1_METADATA == "L1"
        assert ProgressiveLevel.L2_BODY == "L2"
        assert ProgressiveLevel.L3_REFERENCES == "L3"


class TestSkillModelInstantiation:
    def test_valid_creation(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.skill_id == "SKILL-DOM-TS-001"
        assert model.name == "Test Skill"

    def test_default_status_is_active(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.status == SkillStatus.ACTIVE

    def test_default_freshness_score(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.freshness_score == 100.0

    def test_default_version(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.version == "0.1.0"

    def test_default_author(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.author == "factory-agent"

    def test_default_token_budgets(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.token_budget_l1 == 50
        assert model.token_budget_l2 == 500

    def test_default_references_empty(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.references == []

    def test_default_upstream_modules_empty(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.upstream_modules == []

    def test_created_at_auto_set(self):
        model = SkillModel(**_VALID_KWARGS)
        assert isinstance(model.created_at, datetime)

    def test_updated_at_auto_set(self):
        model = SkillModel(**_VALID_KWARGS)
        assert isinstance(model.updated_at, datetime)


class TestSkillModelInvalidSkillId:
    def test_empty_skill_id_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "skill_id": ""})

    def test_wrong_format_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "skill_id": "INVALID"})

    def test_lowercase_skill_id_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "skill_id": "skill-dom-ts-001"})

    def test_missing_numbers_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "skill_id": "SKILL-DOM-TS-"})


class TestSkillModelFreshnessScore:
    def test_zero_is_valid(self):
        model = SkillModel(**{**_VALID_KWARGS, "freshness_score": 0.0})
        assert model.freshness_score == 0.0

    def test_hundred_is_valid(self):
        model = SkillModel(**{**_VALID_KWARGS, "freshness_score": 100.0})
        assert model.freshness_score == 100.0

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "freshness_score": -1.0})

    def test_over_hundred_raises(self):
        with pytest.raises(ValidationError):
            SkillModel(**{**_VALID_KWARGS, "freshness_score": 101.0})


class TestSkillModelMissingRequired:
    def test_missing_name_raises(self):
        kw = {k: v for k, v in _VALID_KWARGS.items() if k != "name"}
        with pytest.raises(ValidationError):
            SkillModel(**kw)

    def test_missing_description_raises(self):
        kw = {k: v for k, v in _VALID_KWARGS.items() if k != "description"}
        with pytest.raises(ValidationError):
            SkillModel(**kw)

    def test_missing_path_raises(self):
        kw = {k: v for k, v in _VALID_KWARGS.items() if k != "path"}
        with pytest.raises(ValidationError):
            SkillModel(**kw)

    def test_missing_allowed_tools_raises(self):
        kw = {k: v for k, v in _VALID_KWARGS.items() if k != "allowed_tools"}
        with pytest.raises(ValidationError):
            SkillModel(**kw)


class TestSkillModelOptionalFields:
    def test_model_hint_none(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.model_hint is None

    def test_model_hint_set(self):
        model = SkillModel(**{**_VALID_KWARGS, "model_hint": "deepseek-v3"})
        assert model.model_hint == "deepseek-v3"

    def test_last_validated_none(self):
        model = SkillModel(**_VALID_KWARGS)
        assert model.last_validated is None

    def test_last_validated_set(self):
        now = datetime(2026, 1, 1)
        model = SkillModel(**{**_VALID_KWARGS, "last_validated": now})
        assert model.last_validated == now


class TestSkillModelStatusTransitions:
    def test_set_status_deprecated(self):
        model = SkillModel(**{**_VALID_KWARGS, "status": SkillStatus.DEPRECATED})
        assert model.status == SkillStatus.DEPRECATED

    def test_set_status_retired(self):
        model = SkillModel(**{**_VALID_KWARGS, "status": SkillStatus.RETIRED})
        assert model.status == SkillStatus.RETIRED

    def test_set_status_draft(self):
        model = SkillModel(**{**_VALID_KWARGS, "status": SkillStatus.DRAFT})
        assert model.status == SkillStatus.DRAFT
