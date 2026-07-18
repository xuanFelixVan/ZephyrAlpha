# [A_test] module_id: SRC-TST-1362 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-416 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_path_resolver
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

import os
import tempfile

import pytest

from zephyr.governance.architecture_governance.path_resolver import PathResolution, PathResolver


@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "src", "zephyr")
        os.makedirs(os.path.join(src, "governance"), exist_ok=True)
        os.makedirs(os.path.join(src, "shared"), exist_ok=True)
        with open(os.path.join(src, "governance", "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")
        with open(os.path.join(src, "governance", "test_mod.py"), "w", encoding="utf-8") as f:
            f.write("x = 1")
        with open(os.path.join(src, "shared", "utils.py"), "w", encoding="utf-8") as f:
            f.write("y = 2")
        yield tmp


class TestPathResolution:
    def test_default_status(self):
        pr = PathResolution(expected="/some/path")
        assert pr.status == "UNKNOWN"
        assert pr.exists_at_expected is False
        assert pr.suggested_path is None

    def test_expected_set(self):
        pr = PathResolution(expected="/foo/bar.py")
        assert pr.expected == "/foo/bar.py"


class TestPathResolver:
    def test_init_builds_index(self, temp_project):
        resolver = PathResolver(temp_project)
        assert resolver.project_root == os.path.abspath(temp_project)

    def test_resolve_module_governance(self, temp_project):
        resolver = PathResolver(temp_project)
        results = resolver.resolve_module("governance")
        assert len(results) > 0

    def test_resolve_module_nonexistent(self, temp_project):
        resolver = PathResolver(temp_project)
        results = resolver.resolve_module("nonexistent_xyz")
        assert results == []

    def test_resolve_path_existing_module(self, temp_project):
        resolver = PathResolver(temp_project)
        result = resolver.resolve_path("governance", "test_mod.py")
        assert result is not None
        assert "governance" in result

    def test_resolve_path_nonexistent_module(self, temp_project):
        resolver = PathResolver(temp_project)
        result = resolver.resolve_path("nonexistent_xyz", "file.py")
        assert result is None

    def test_validate_path_existing_file(self, temp_project):
        resolver = PathResolver(temp_project)
        existing = os.path.join(temp_project, "src", "zephyr", "governance", "test_mod.py")
        result = resolver.validate_path(existing)
        assert result.status == "OK"
        assert result.exists_at_expected is True

    def test_validate_path_nonexistent_file(self, temp_project):
        resolver = PathResolver(temp_project)
        missing = os.path.join(temp_project, "src", "zephyr", "governance", "missing.py")
        result = resolver.validate_path(missing)
        assert result.status != "OK"

    def test_validate_path_no_basename(self, temp_project):
        resolver = PathResolver(temp_project)
        result = resolver.validate_path(temp_project + os.sep)
        assert result.status in ("NO_BASENAME", "OK", "MISSING")

    def test_dump_module_tree(self, temp_project):
        resolver = PathResolver(temp_project)
        tree = resolver.dump_module_tree()
        assert isinstance(tree, dict)

    def test_resolve_downstream(self, temp_project):
        resolver = PathResolver(temp_project)
        content = 'downstream_outputs:\n  - path: "/fake/path.py"\n'
        result = resolver.resolve_downstream(content)
        assert "resolved" in result
        assert "corrections" in result
        assert "updated_content" in result
