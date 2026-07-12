# [A_test] module_id: SRC-TST-1335 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_data_lifecycle
# [INVARIANTS] 8 data types; should_purge only True when archive_policy=purge and age>cold_days; unknown type returns None/False
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_policy returns None for unknown type; should_purge returns False for unknown type
# [TESTS] test_orchestrator_data_lifecycle.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.execution.data_lifecycle import DATA_LIFECYCLE, DataLifecycleManager


class TestDataLifecycleConstant:
    def test_data_types_count(self):
        assert len(DATA_LIFECYCLE) == 8

    def test_all_types_have_required_keys(self):
        for dtype, policy in DATA_LIFECYCLE.items():
            assert "hot_days" in policy
            assert "cold_days" in policy
            assert "archive_policy" in policy

    def test_archive_policy_values(self):
        valid_policies = {"compress", "keep", "rollup", "regenerate", "purge"}
        for dtype, policy in DATA_LIFECYCLE.items():
            assert policy["archive_policy"] in valid_policies


class TestDataLifecycleManager:
    @pytest.fixture()
    def manager(self):
        return DataLifecycleManager()

    def test_get_policy_existing(self, manager):
        policy = manager.get_policy("task_cards")
        assert policy is not None
        assert policy["hot_days"] == 7
        assert policy["cold_days"] == 90
        assert policy["archive_policy"] == "compress"

    def test_get_policy_all_types(self, manager):
        for dtype in DATA_LIFECYCLE:
            policy = manager.get_policy(dtype)
            assert policy is not None

    def test_get_policy_unknown(self, manager):
        assert manager.get_policy("nonexistent_type") is None

    def test_get_policy_empty_string(self, manager):
        assert manager.get_policy("") is None

    def test_list_types(self, manager):
        types = manager.list_types()
        assert len(types) == 8
        assert "task_cards" in types
        assert "findings" in types
        assert "knowledge_entries" in types
        assert "audit_logs" in types
        assert "metrics" in types
        assert "vector_embeddings" in types
        assert "dlq_messages" in types
        assert "session_logs" in types

    def test_should_purge_purge_type_old_enough(self, manager):
        assert manager.should_purge("dlq_messages", 31) is True

    def test_should_purge_purge_type_not_old_enough(self, manager):
        assert manager.should_purge("dlq_messages", 30) is False

    def test_should_purge_purge_type_exactly_cold_days(self, manager):
        assert manager.should_purge("dlq_messages", 30) is False

    def test_should_purge_non_purge_type(self, manager):
        assert manager.should_purge("task_cards", 999) is False

    def test_should_purge_compress_type(self, manager):
        assert manager.should_purge("task_cards", 999) is False

    def test_should_purge_keep_type(self, manager):
        assert manager.should_purge("knowledge_entries", 999) is False

    def test_should_purge_unknown_type(self, manager):
        assert manager.should_purge("nonexistent", 100) is False

    def test_should_purge_zero_age(self, manager):
        assert manager.should_purge("dlq_messages", 0) is False

    def test_should_purge_vector_embeddings_regenerate(self, manager):
        assert manager.should_purge("vector_embeddings", 999) is False

    def test_dlq_messages_is_only_purge_type(self, manager):
        for dtype in DATA_LIFECYCLE:
            policy = DATA_LIFECYCLE[dtype]
            if policy["archive_policy"] == "purge":
                assert dtype == "dlq_messages"
