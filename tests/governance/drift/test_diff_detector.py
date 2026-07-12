# [A_test] module_id: SRC-TST-0749 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_diff_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_diff_detector.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path

from zephyr.gov_code_quality.code_dedup.diff_detector import (
    ChangedFunction,
    DiffDetector,
    DiffResult,
)


class TestChangedFunction:
    def test_default_values(self):
        cf = ChangedFunction(file="a.py", name="foo", lineno=1, end_lineno=5)
        assert cf.file == "a.py"
        assert cf.name == "foo"
        assert cf.source == ""


class TestDiffResult:
    def test_default_values(self):
        dr = DiffResult()
        assert dr.changed_files == []
        assert dr.changed_functions == []
        assert dr.staged_files == []
        assert dr.unstaged_files == []


class TestDiffDetector:
    def test_instantiation_default(self):
        dd = DiffDetector()
        assert dd._repo_root == Path.cwd()

    def test_instantiation_custom_root(self):
        dd = DiffDetector(repo_root="/tmp")
        assert dd._repo_root == Path("/tmp")

    def test_extract_functions_valid_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def hello():\n    return 42\n\ndef world(x: int) -> int:\n    return x + 1\n")
            f.flush()
            path = Path(f.name)
        try:
            funcs = DiffDetector._extract_functions(path)
            assert len(funcs) == 2
            assert funcs[0].name == "hello"
            assert funcs[1].name == "world"
        finally:
            path.unlink()

    def test_extract_functions_syntax_error(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def broken(:\n")
            f.flush()
            path = Path(f.name)
        try:
            funcs = DiffDetector._extract_functions(path)
            assert funcs == []
        finally:
            path.unlink()

    def test_extract_functions_nonexistent(self):
        funcs = DiffDetector._extract_functions(Path("/nonexistent/file.py"))
        assert funcs == []

    def test_extract_functions_async(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("async def async_handler():\n    await something()\n")
            f.flush()
            path = Path(f.name)
        try:
            funcs = DiffDetector._extract_functions(path)
            assert len(funcs) == 1
            assert funcs[0].name == "async_handler"
        finally:
            path.unlink()

    def test_extract_functions_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("")
            f.flush()
            path = Path(f.name)
        try:
            funcs = DiffDetector._extract_functions(path)
            assert funcs == []
        finally:
            path.unlink()

    def test_detect_returns_diff_result(self):
        dd = DiffDetector(repo_root=".")
        result = dd.detect()
        assert isinstance(result, DiffResult)
        assert isinstance(result.changed_files, list)
        assert isinstance(result.changed_functions, list)

    def test_detect_changed_files_returns_list(self):
        dd = DiffDetector(repo_root=".")
        result = dd.detect_changed_files()
        assert isinstance(result, list)

    def test_detect_changed_functions_returns_list(self):
        dd = DiffDetector(repo_root=".")
        result = dd.detect_changed_functions()
        assert isinstance(result, list)

    def test_git_diff_files_no_repo(self):
        dd = DiffDetector(repo_root="/nonexistent/repo")
        try:
            result = dd._git_diff_files(cached=True)
            assert isinstance(result, list)
        except (OSError, NotADirectoryError):
            pass

    def test_git_diff_files_unstaged_no_repo(self):
        dd = DiffDetector(repo_root="/nonexistent/repo")
        try:
            result = dd._git_diff_files(cached=False)
            assert isinstance(result, list)
        except (OSError, NotADirectoryError):
            pass
