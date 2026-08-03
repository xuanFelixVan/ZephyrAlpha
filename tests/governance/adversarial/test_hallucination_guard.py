# [A_test] module_id: SRC-TST-1088 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_hallucination_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] HallucinationGuard.MAX_ROUNDS==3; EXIT_CODE_HALLUCINATION==11
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import hashlib
from pathlib import Path

from zephyr.infrastructure.rollback.hallucination_guard import (
    FileState,
    HallucinationGuard,
)


class TestFileState:
    def test_default_values(self):
        fs = FileState(path="foo.py")
        assert fs.path == "foo.py"
        assert fs.md5 == ""
        assert fs.sha256 == ""
        assert fs.line_count == 0
        assert fs.function_signatures == []
        assert fs.class_names == []

    def test_custom_values(self):
        fs = FileState(
            path="bar.py",
            md5="abc",
            sha256="def",
            line_count=42,
            function_signatures=["foo()"],
            class_names=["Bar"],
        )
        assert fs.md5 == "abc"
        assert fs.line_count == 42


class TestHallucinationGuardInstantiation:
    def test_default_project_root(self, tmp_path):
        guard = HallucinationGuard()
        assert guard.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        assert guard.project_root == tmp_path

    def test_initial_rounds_empty(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        assert guard.rounds == []


class TestComputeActualState:
    def test_empty_file_list(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        result = guard.compute_actual_state(files=[])
        assert result == []

    def test_nonexistent_files_skipped(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        result = guard.compute_actual_state(files=["nonexistent.py"])
        assert result == []

    def test_existing_file_computed(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        py_file = src_dir / "sample.py"
        content = "def hello():\n    pass\n"
        py_file.write_text(content, encoding="utf-8")

        guard = HallucinationGuard(project_root=tmp_path)
        result = guard.compute_actual_state(files=[str(py_file)])
        assert len(result) == 1
        state = result[0]
        expected_md5 = hashlib.md5(content.encode()).hexdigest()
        assert state.md5 == expected_md5
        assert state.line_count == 2
        assert "hello()" in state.function_signatures

    def test_none_files_uses_glob(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        result = guard.compute_actual_state(files=None)
        assert isinstance(result, list)


class TestVerifyRound:
    def test_matching_states_pass(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        py_file = src_dir / "mod.py"
        content = "class Foo:\n    def bar(self):\n        return 1\n"
        py_file.write_text(content, encoding="utf-8")

        guard = HallucinationGuard(project_root=tmp_path)
        actual = guard.compute_actual_state(files=[str(py_file)])
        claimed = [
            {
                "path": s.path,
                "md5": s.md5,
                "sha256": s.sha256,
                "line_count": s.line_count,
                "function_signatures": s.function_signatures,
                "class_names": s.class_names,
            }
            for s in actual
        ]

        vr = guard.verify_round(claimed, files=[str(py_file)])
        assert vr.passed is True
        assert vr.mismatches == []
        assert vr.round_number == 1

    def test_md5_mismatch_fails(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        py_file = src_dir / "mod.py"
        py_file.write_text("x = 1\n", encoding="utf-8")

        guard = HallucinationGuard(project_root=tmp_path)
        claimed = [
            {
                "path": str(py_file.relative_to(tmp_path)),
                "md5": "bad_md5",
                "sha256": "",
                "line_count": 1,
                "function_signatures": [],
                "class_names": [],
            }
        ]

        vr = guard.verify_round(claimed, files=[str(py_file)])
        assert vr.passed is False
        assert any("MD5 mismatch" in m for m in vr.mismatches)

    def test_missing_file_in_claim(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        claimed = [
            {
                "path": "ghost.py",
                "md5": "abc",
                "sha256": "",
                "line_count": 0,
                "function_signatures": [],
                "class_names": [],
            }
        ]
        vr = guard.verify_round(claimed, files=[])
        assert vr.passed is False
        assert len(vr.mismatches) > 0
        assert any("ghost.py" in m for m in vr.mismatches)

    def test_empty_claimed_state(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        vr = guard.verify_round([], files=[])
        assert vr.passed is True
        assert vr.mismatches == []

    def test_line_count_mismatch(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        py_file = src_dir / "mod.py"
        py_file.write_text("x = 1\ny = 2\n", encoding="utf-8")

        guard = HallucinationGuard(project_root=tmp_path)
        actual = guard.compute_actual_state(files=[str(py_file)])
        claimed = [
            {
                "path": s.path,
                "md5": s.md5,
                "sha256": s.sha256,
                "line_count": 999,
                "function_signatures": s.function_signatures,
                "class_names": s.class_names,
            }
            for s in actual
        ]

        vr = guard.verify_round(claimed, files=[str(py_file)])
        assert vr.passed is False
        assert any("line count" in m for m in vr.mismatches)


class TestRunFullVerification:
    def test_all_rounds_pass(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        py_file = src_dir / "mod.py"
        content = "x = 1\n"
        py_file.write_text(content, encoding="utf-8")

        guard = HallucinationGuard(project_root=tmp_path)
        actual = guard.compute_actual_state(files=[str(py_file)])
        claimed = [
            {
                "path": s.path,
                "md5": s.md5,
                "sha256": s.sha256,
                "line_count": s.line_count,
                "function_signatures": s.function_signatures,
                "class_names": s.class_names,
            }
            for s in actual
        ]

        result = guard.run_full_verification([claimed, claimed, claimed], files=[str(py_file)])
        assert result.detected is False
        assert result.rounds_passed == 3
        assert result.rounds_failed == 0
        assert result.final_verdict == "STATE_VERIFIED"
        assert result.exit_code == 0

    def test_all_rounds_fail_triggers_hallucination(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        bad_claim = [
            {
                "path": "fake.py",
                "md5": "wrong",
                "sha256": "",
                "line_count": 0,
                "function_signatures": [],
                "class_names": [],
            }
        ]

        result = guard.run_full_verification([bad_claim, bad_claim, bad_claim], files=[])
        assert result.detected is True
        assert result.rounds_failed == 3
        assert result.final_verdict == "HALLUCINATION_DETECTED"
        assert result.exit_code == 11

    def test_max_rounds_capped_at_three(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        bad_claim = [
            {
                "path": "fake.py",
                "md5": "wrong",
                "sha256": "",
                "line_count": 0,
                "function_signatures": [],
                "class_names": [],
            }
        ]

        result = guard.run_full_verification([bad_claim] * 5, files=[])
        assert result.rounds_executed == 3

    def test_inconclusive_when_no_passes_but_not_all_fail(self, tmp_path):
        guard = HallucinationGuard(project_root=tmp_path)
        good_claim: list[dict] = []
        bad_claim = [
            {
                "path": "fake.py",
                "md5": "wrong",
                "sha256": "",
                "line_count": 0,
                "function_signatures": [],
                "class_names": [],
            }
        ]

        result = guard.run_full_verification([bad_claim, bad_claim], files=[])
        assert result.final_verdict == "INCONCLUSIVE"
        assert result.detected is False


class TestExtractHelpers:
    def test_extract_functions_valid(self):
        src = "def foo(x, y):\n    pass\n\ndef bar():\n    pass\n"
        funcs = HallucinationGuard.extract_functions(src)
        assert "foo(x, y)" in funcs
        assert "bar()" in funcs

    def test_extract_functions_syntax_error(self):
        funcs = HallucinationGuard.extract_functions("def (broken")
        assert funcs == []

    def test_extract_classes_valid(self):
        src = "class Foo:\n    pass\n\nclass Bar(Foo):\n    pass\n"
        classes = HallucinationGuard.extract_classes(src)
        assert "Foo" in classes
        assert "Bar" in classes

    def test_extract_classes_syntax_error(self):
        classes = HallucinationGuard.extract_classes("class (broken")
        assert classes == []

    def test_extract_functions_async(self):
        src = "async def fetch():\n    pass\n"
        funcs = HallucinationGuard.extract_functions(src)
        assert "fetch()" in funcs
