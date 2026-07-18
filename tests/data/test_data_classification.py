# [A_test] module_id: SRC-TST-0696 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-373 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_data_classification
# [INVARIANTS] classify respects level ordering; max_level_from_list returns highest
# [MODIFY-GUARD] Changes must sync with data_classification.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_data_classification.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.data_classification import (
    DATA_CLASSIFICATION,
    LEVEL_ORDER,
    DataLevel,
    LevelAttributes,
    classify,
    get_level,
    max_level_from_list,
)


class TestDataLevel:
    def test_enum_values(self):
        assert DataLevel.L1_PUBLIC.value == "L1_PUBLIC"
        assert DataLevel.L2_INTERNAL.value == "L2_INTERNAL"
        assert DataLevel.L3_CONFIDENTIAL.value == "L3_CONFIDENTIAL"
        assert DataLevel.L4_RESTRICTED.value == "L4_RESTRICTED"

    def test_enum_count(self):
        assert len(DataLevel) == 4


class TestLevelAttributes:
    def test_creation(self):
        la = LevelAttributes(
            level=DataLevel.L1_PUBLIC,
            label="Public",
            encryption_required=False,
            access_control=[],
            audit_log=False,
            retention_days=0,
        )
        assert la.level == DataLevel.L1_PUBLIC
        assert la.encryption_required is False

    def test_l4_requires_encryption(self):
        la = DATA_CLASSIFICATION[DataLevel.L4_RESTRICTED]
        assert la.encryption_required is True

    def test_l4_requires_audit(self):
        la = DATA_CLASSIFICATION[DataLevel.L4_RESTRICTED]
        assert la.audit_log is True


class TestDataClassification:
    def test_keys_match_data_level(self):
        assert set(DATA_CLASSIFICATION.keys()) == set(DataLevel)

    def test_all_entries_are_level_attributes(self):
        for level, attr in DATA_CLASSIFICATION.items():
            assert isinstance(attr, LevelAttributes), f"{level} is not LevelAttributes"

    def test_l1_no_encryption(self):
        assert DATA_CLASSIFICATION[DataLevel.L1_PUBLIC].encryption_required is False

    def test_l3_encryption_required(self):
        assert DATA_CLASSIFICATION[DataLevel.L3_CONFIDENTIAL].encryption_required is True

    def test_l1_no_audit(self):
        assert DATA_CLASSIFICATION[DataLevel.L1_PUBLIC].audit_log is False

    def test_l3_audit_required(self):
        assert DATA_CLASSIFICATION[DataLevel.L3_CONFIDENTIAL].audit_log is True


class TestLevelOrder:
    def test_keys_match_data_level(self):
        assert set(LEVEL_ORDER.keys()) == set(DataLevel)

    def test_ordering(self):
        assert LEVEL_ORDER[DataLevel.L1_PUBLIC] < LEVEL_ORDER[DataLevel.L2_INTERNAL]
        assert LEVEL_ORDER[DataLevel.L2_INTERNAL] < LEVEL_ORDER[DataLevel.L3_CONFIDENTIAL]
        assert LEVEL_ORDER[DataLevel.L3_CONFIDENTIAL] < LEVEL_ORDER[DataLevel.L4_RESTRICTED]


class TestGetLevel:
    def test_existing(self):
        result = get_level(DataLevel.L1_PUBLIC)
        assert result is not None
        assert result.level == DataLevel.L1_PUBLIC

    def test_all_levels_accessible(self):
        for level in DataLevel:
            result = get_level(level)
            assert result is not None


class TestClassify:
    def test_same_level_allowed(self):
        assert classify(DataLevel.L3_CONFIDENTIAL, DataLevel.L3_CONFIDENTIAL) is True

    def test_higher_accessing_lower_allowed(self):
        assert classify(DataLevel.L4_RESTRICTED, DataLevel.L1_PUBLIC) is True

    def test_lower_accessing_higher_denied(self):
        assert classify(DataLevel.L1_PUBLIC, DataLevel.L4_RESTRICTED) is False

    def test_l1_accessing_l1(self):
        assert classify(DataLevel.L1_PUBLIC, DataLevel.L1_PUBLIC) is True

    def test_l1_accessing_l2(self):
        assert classify(DataLevel.L1_PUBLIC, DataLevel.L2_INTERNAL) is False

    def test_l4_accessing_any(self):
        for target in DataLevel:
            assert classify(DataLevel.L4_RESTRICTED, target) is True


class TestMaxLevelFromList:
    def test_single_level(self):
        assert max_level_from_list([DataLevel.L1_PUBLIC]) == DataLevel.L1_PUBLIC

    def test_mixed_levels(self):
        result = max_level_from_list([DataLevel.L1_PUBLIC, DataLevel.L4_RESTRICTED, DataLevel.L2_INTERNAL])
        assert result == DataLevel.L4_RESTRICTED

    def test_all_same(self):
        result = max_level_from_list([DataLevel.L2_INTERNAL, DataLevel.L2_INTERNAL])
        assert result == DataLevel.L2_INTERNAL

    def test_ordered_list(self):
        result = max_level_from_list([DataLevel.L1_PUBLIC, DataLevel.L2_INTERNAL, DataLevel.L3_CONFIDENTIAL])
        assert result == DataLevel.L3_CONFIDENTIAL
