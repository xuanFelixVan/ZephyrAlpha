# [BLUEPRINT] MOD-DATA_GOV-003 | (auto-injected by S4 reconciler) | §D-DATA-GOV
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-003 | layer=test | stability=volatile | safety=L
# [MODULE] tests.data_governance.test_metadata_registry
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/data_governance/test_metadata_registry.py
# [TTL] task_bound
"""D-DATA-GOV Metadata Registry 测试。"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.metadata_registry import (
    MetadataEntry,
    MetadataRegistry,
)


class TestRegisterAndGet:
    def test_register_and_get(self):
        reg = MetadataRegistry()
        reg.register("table.t1", {"source": "tushare", "rows": 1000}, "table")
        entry = reg.get("table.t1")
        assert isinstance(entry, MetadataEntry)
        assert entry.key == "table.t1"
        assert entry.value["source"] == "tushare"
        assert entry.value["rows"] == 1000
        assert entry.category == "table"

    def test_register_idempotent_updates(self):
        reg = MetadataRegistry()
        reg.register("k1", {"v": 1})
        reg.register("k1", {"v": 2}, "updated")
        entry = reg.get("k1")
        assert entry.value["v"] == 2
        assert entry.category == "updated"

    def test_get_unregistered_raises(self):
        reg = MetadataRegistry()
        with pytest.raises(KeyError, match="未注册"):
            reg.get("unknown")

    def test_get_value_with_default(self):
        reg = MetadataRegistry()
        reg.register("k1", {"source": "tushare"})
        assert reg.get_value("k1", "source") == "tushare"
        assert reg.get_value("k1", "nonexistent") is None
        assert reg.get_value("k1", "nonexistent", "default") == "default"
        assert reg.get_value("unknown", "x") is None


class TestListAndSearch:
    def test_list_keys_empty(self):
        reg = MetadataRegistry()
        assert reg.list_keys() == []

    def test_list_keys(self):
        reg = MetadataRegistry()
        reg.register("k1", {})
        reg.register("k2", {})
        assert set(reg.list_keys()) == {"k1", "k2"}

    def test_list_by_category(self):
        reg = MetadataRegistry()
        reg.register("t1", {}, "table")
        reg.register("f1", {}, "factor")
        reg.register("t2", {}, "table")
        tables = reg.list_by_category("table")
        assert len(tables) == 2
        factors = reg.list_by_category("factor")
        assert len(factors) == 1

    def test_search_prefix(self):
        reg = MetadataRegistry()
        reg.register("table.market.kline", {})
        reg.register("table.market.tick", {})
        reg.register("factor.momentum", {})
        results = reg.search("table.market.")
        assert len(results) == 2
        results = reg.search("factor.")
        assert len(results) == 1
        results = reg.search("nonexistent.")
        assert results == []

    def test_has(self):
        reg = MetadataRegistry()
        reg.register("k1", {})
        assert reg.has("k1") is True
        assert reg.has("unknown") is False


class TestRemoveAndCount:
    def test_remove_existing(self):
        reg = MetadataRegistry()
        reg.register("k1", {})
        assert reg.remove("k1") is True
        assert reg.has("k1") is False

    def test_remove_nonexistent(self):
        reg = MetadataRegistry()
        assert reg.remove("unknown") is False

    def test_count(self):
        reg = MetadataRegistry()
        assert reg.count() == 0
        reg.register("k1", {})
        reg.register("k2", {})
        assert reg.count() == 2
        reg.remove("k1")
        assert reg.count() == 1
