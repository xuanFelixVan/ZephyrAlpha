# [A_test] module_id: SRC-TST-1360 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_path_index
# [INVARIANTS] PathIndex uses module-level PATH_INDEX dict; tests must clean up global state
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_path_index.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.governance.path_index import PATH_INDEX, PathIndex


@pytest.fixture(autouse=True)
def clean_path_index():
    original = dict(PATH_INDEX)
    yield
    PATH_INDEX.clear()
    PATH_INDEX.update(original)


class TestPathIndexLookup:
    def test_lookup_existing_module(self):
        idx = PathIndex()
        PATH_INDEX["test_module"] = ["/path/to/file1.py", "/path/to/file2.py"]
        result = idx.lookup("test_module")
        assert result == ["/path/to/file1.py", "/path/to/file2.py"]

    def test_lookup_nonexistent_module(self):
        idx = PathIndex()
        result = idx.lookup("nonexistent_module")
        assert result == []

    def test_lookup_returns_list(self):
        idx = PathIndex()
        PATH_INDEX["mod"] = ["a.py"]
        result = idx.lookup("mod")
        assert isinstance(result, list)


class TestPathIndexRegister:
    def test_register_new_module(self):
        idx = PathIndex()
        idx.register("new_module", ["/path/to/new.py"])
        assert PATH_INDEX["new_module"] == ["/path/to/new.py"]

    def test_register_overwrites_existing(self):
        idx = PathIndex()
        PATH_INDEX["existing"] = ["/old/path.py"]
        idx.register("existing", ["/new/path.py"])
        assert PATH_INDEX["existing"] == ["/new/path.py"]

    def test_register_empty_paths(self):
        idx = PathIndex()
        idx.register("empty_mod", [])
        assert PATH_INDEX["empty_mod"] == []

    def test_register_multiple_paths(self):
        idx = PathIndex()
        paths = ["/a.py", "/b.py", "/c.yaml"]
        idx.register("multi_mod", paths)
        assert PATH_INDEX["multi_mod"] == paths


class TestPathIndexGlobalState:
    def test_path_index_is_shared(self):
        idx1 = PathIndex()
        idx2 = PathIndex()
        idx1.register("shared_mod", ["/shared.py"])
        assert idx2.lookup("shared_mod") == ["/shared.py"]

    def test_path_index_empty_by_default(self):
        idx = PathIndex()
        PATH_INDEX.clear()
        result = idx.lookup("anything")
        assert result == []
