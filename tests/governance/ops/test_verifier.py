# [A_test] module_id: SRC-TST-1785 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_verifier.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path

from zephyr.gov_code_quality.code_dedup.verifier import Verifier, VerifyResult


class TestVerifyResult:
    def test_default_values(self):
        vr = VerifyResult()
        assert vr.file == ""
        assert vr.imports_ok is False
        assert vr.syntax_ok is False
        assert vr.checks_passed == 0
        assert vr.checks_failed == 0
        assert vr.issues == []

    def test_custom_values(self):
        vr = VerifyResult(file="test.py", syntax_ok=True, checks_passed=1)
        assert vr.file == "test.py"
        assert vr.syntax_ok is True


class TestVerifier:
    def test_instantiation_default(self):
        v = Verifier()
        assert v._root == Path.cwd()

    def test_instantiation_custom_root(self):
        v = Verifier(project_root="/tmp")
        assert v._root == Path("/tmp")

    def test_verify_file_nonexistent(self):
        v = Verifier()
        result = v.verify_file("/nonexistent/file.py")
        assert result.syntax_ok is False
        assert "FILE_NOT_FOUND" in result.issues

    def test_verify_file_valid_syntax(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def hello():\n    return 42\n")
            f.flush()
            path = f.name
        try:
            v = Verifier()
            result = v.verify_file(path)
            assert result.syntax_ok is True
            assert result.imports_ok is True
            assert result.checks_passed >= 1
        finally:
            Path(path).unlink()

    def test_verify_file_syntax_error(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def broken(:\n")
            f.flush()
            path = f.name
        try:
            v = Verifier()
            result = v.verify_file(path)
            assert result.syntax_ok is False
            assert result.checks_failed >= 1
            assert any("SYNTAX_ERROR" in issue for issue in result.issues)
        finally:
            Path(path).unlink()

    def test_verify_file_path_object(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            path = Path(f.name)
        try:
            v = Verifier()
            result = v.verify_file(path)
            assert result.syntax_ok is True
        finally:
            path.unlink()

    def test_verify_module_import_valid(self):
        v = Verifier()
        assert v.verify_module_import("os") is True

    def test_verify_module_import_invalid(self):
        v = Verifier()
        assert v.verify_module_import("nonexistent_module_xyz_12345") is False

    def test_verify_file_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("")
            f.flush()
            path = f.name
        try:
            v = Verifier()
            result = v.verify_file(path)
            assert result.syntax_ok is True
        finally:
            Path(path).unlink()
