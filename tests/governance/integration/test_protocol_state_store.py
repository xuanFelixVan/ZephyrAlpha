# [A_test] module_id: MOD-GOV_protocol_state_store | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_protocol_state_store
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_protocol_state_store.py -q
# [TTL] task_bound
import json
import os
import shutil

import pytest

from zephyr.governance.persistence.protocol_state_store import ProtocolStateStore


@pytest.fixture
def state_dir(tmp_path):
    d = str(tmp_path / "test_state")
    os.makedirs(d, exist_ok=True)
    yield d
    if os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)


class TestProtocolStateStoreInstantiation:
    def test_creates_instance(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        assert isinstance(store, ProtocolStateStore)

    def test_creates_directory(self, tmp_path):
        new_dir = str(tmp_path / "new_state_dir")
        assert not os.path.exists(new_dir)
        ProtocolStateStore(state_dir=new_dir)
        assert os.path.isdir(new_dir)

    def test_has_save_method(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        assert callable(getattr(store, "save", None))

    def test_has_update_method(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        assert callable(getattr(store, "update", None))


class TestUpdate:
    def test_update_stores_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("key1", "value1")
        assert store.state["key1"] == "value1"

    def test_update_overwrites(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("key1", "old")
        store.update("key1", "new")
        assert store.state["key1"] == "new"

    def test_update_multiple_keys(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("a", 1)
        store.update("b", 2)
        assert store.state["a"] == 1
        assert store.state["b"] == 2

    def test_update_with_dict_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("config", {"mode": "strict", "level": 3})
        assert store.state["config"]["mode"] == "strict"

    def test_update_with_none_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("key", None)
        assert store.state["key"] is None

    def test_update_with_list_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("items", [1, 2, 3])
        assert store.state["items"] == [1, 2, 3]


class TestSave:
    def test_save_creates_file(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("k", "v")
        path = store.save()
        assert os.path.isfile(path)

    def test_save_returns_path(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("k", "v")
        path = store.save()
        assert path == os.path.join(state_dir, "protocol_state.json")

    def test_save_contains_state(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("rule_count", 42)
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["rule_count"] == 42

    def test_save_contains_timestamp(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert "timestamp" in data

    def test_save_overwrites_previous(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("k", "first")
        store.save()
        store.update("k", "second")
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["k"] == "second"

    def test_save_empty_state(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"] == {}

    def test_save_complex_nested_state(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("nested", {"a": {"b": [1, 2, 3]}})
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["nested"]["a"]["b"] == [1, 2, 3]


class TestBoundaryConditions:
    def test_update_empty_key(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("", "empty_key_value")
        assert store.state[""] == "empty_key_value"

    def test_save_with_special_characters_in_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("msg", "Hello 你好 🌍")
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["msg"] == "Hello 你好 🌍"

    def test_save_with_numeric_key(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("123", "numeric_key")
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["123"] == "numeric_key"

    def test_update_with_boolean_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("flag", True)
        assert store.state["flag"] is True

    def test_save_with_boolean_value(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("flag", False)
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["flag"] is False

    def test_save_multiple_times(self, state_dir):
        store = ProtocolStateStore(state_dir=state_dir)
        for i in range(10):
            store.update("counter", i)
            store.save()
        path = store.save()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["counter"] == 9
