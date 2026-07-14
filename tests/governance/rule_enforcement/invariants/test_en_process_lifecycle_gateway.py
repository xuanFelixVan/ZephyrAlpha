# [A_test] module_id: SRC-TST-0834 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §2.10
# [MODULE] tests.test_en_process_lifecycle_gateway
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit code reflects pass/fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import ast
from unittest.mock import patch

import pytest

from zephyr.gov_enforcement.rule_enforcement.invariants.en_process_lifecycle_gateway import (
    ALLOWED_FILES,
    GateResult,
    ProcessCreationScanner,
    Violation,
    result,
    scan_directory,
    scan_file,
)


class TestViolation:
    def test_creation(self):
        v = Violation(file="test.py", line=10, call_type="subprocess.Popen", snippet="subprocess.Popen(['cmd'])")
        assert v.file == "test.py"
        assert v.line == 10
        assert v.call_type == "subprocess.Popen"
        assert v.snippet == "subprocess.Popen(['cmd'])"

    def test_default_values(self):
        v = Violation(file="a.py", line=1, call_type="subprocess.call", snippet="")
        assert v.snippet == ""

    def test_equality(self):
        v1 = Violation(file="a.py", line=1, call_type="subprocess.Popen", snippet="x")
        v2 = Violation(file="a.py", line=1, call_type="subprocess.Popen", snippet="x")
        assert v1 == v2


class TestGateResult:
    def test_default_passed(self):
        gr = GateResult(passed=True)
        assert gr.passed is True
        assert gr.violations == []
        assert gr.scanned_files == 0

    def test_with_violations(self):
        v = Violation(file="a.py", line=1, call_type="subprocess.Popen", snippet="x")
        gr = GateResult(passed=False, violations=[v], scanned_files=5)
        assert gr.passed is False
        assert len(gr.violations) == 1
        assert gr.scanned_files == 5

    def test_passed_true_no_violations(self):
        gr = GateResult(passed=True, violations=[], scanned_files=10)
        assert gr.passed is True
        assert gr.scanned_files == 10


class TestAllowedFiles:
    def test_is_set(self):
        assert isinstance(ALLOWED_FILES, set)

    def test_contains_process_pool(self):
        assert "src/zephyr/shared/infra/process_pool.py" in ALLOWED_FILES

    def test_contains_process_lifecycle_gateway(self):
        assert "src/zephyr/shared/infra/process_lifecycle_gateway.py" in ALLOWED_FILES


class TestProcessCreationScanner:
    def test_detect_subprocess_popen(self, tmp_path):
        code = "import subprocess\nsubprocess.Popen(['cmd'])\n"
        py = tmp_path / "test.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert len(scanner.violations) >= 1
        assert scanner.violations[0].call_type == "subprocess.Popen"

    def test_detect_subprocess_call(self, tmp_path):
        code = "import subprocess\nsubprocess.call(['cmd'])\n"
        py = tmp_path / "test.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert len(scanner.violations) >= 1
        assert scanner.violations[0].call_type == "subprocess.call"

    def test_detect_multiprocessing_process(self, tmp_path):
        code = "import multiprocessing\nmultiprocessing.Process(target=func)\n"
        py = tmp_path / "test.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert len(scanner.violations) >= 1
        assert scanner.violations[0].call_type == "multiprocessing.Process"

    def test_no_violations_for_safe_code(self, tmp_path):
        code = "import os\nos.path.join('a', 'b')\n"
        py = tmp_path / "safe.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert len(scanner.violations) == 0

    def test_gateway_import_suppresses_violations(self, tmp_path):
        code = (
            "from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway\n"
            "import subprocess\n"
            "subprocess.Popen(['cmd'])\n"
        )
        py = tmp_path / "gateway_user.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert scanner._imported_gateway is True
        assert len(scanner.violations) >= 1

    def test_resolve_call_path_name(self):
        node = ast.Name(id="func", ctx=ast.Load())
        assert ProcessCreationScanner._resolve_call_path(node) == "func"

    def test_resolve_call_path_attribute(self):
        node = ast.Attribute(
            value=ast.Name(id="subprocess", ctx=ast.Load()),
            attr="Popen",
            ctx=ast.Load(),
        )
        assert ProcessCreationScanner._resolve_call_path(node) == "subprocess.Popen"

    def test_resolve_call_path_nested(self):
        node = ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id="a", ctx=ast.Load()),
                attr="b",
                ctx=ast.Load(),
            ),
            attr="c",
            ctx=ast.Load(),
        )
        assert ProcessCreationScanner._resolve_call_path(node) == "a.b.c"

    def test_resolve_call_path_constant(self):
        node = ast.Constant(value=42)
        result = ProcessCreationScanner._resolve_call_path(node)
        assert result == ""

    def test_forbidden_calls_dict(self):
        assert "subprocess.Popen" in ProcessCreationScanner.FORBIDDEN_CALLS
        assert "subprocess.call" in ProcessCreationScanner.FORBIDDEN_CALLS
        assert "multiprocessing.Process" in ProcessCreationScanner.FORBIDDEN_CALLS

    def test_visit_import_sets_flag(self, tmp_path):
        code = "import zephyr.shared.infra.process_lifecycle_gateway\n"
        py = tmp_path / "imp.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert scanner._imported_gateway is True

    def test_visit_import_from_sets_flag(self, tmp_path):
        code = "from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway\n"
        py = tmp_path / "imp_from.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert scanner._imported_gateway is True

    def test_violation_has_line_number(self, tmp_path):
        code = "import subprocess\nsubprocess.Popen(['cmd'])\n"
        py = tmp_path / "lined.py"
        py.write_text(code, encoding="utf-8")
        tree = ast.parse(code)
        scanner = ProcessCreationScanner(str(py))
        scanner.visit(tree)
        assert scanner.violations[0].line > 0


class TestScanFile:
    def test_detect_bare_popen(self, tmp_path):
        bad_code = tmp_path / "bad.py"
        bad_code.write_text("import subprocess\nsubprocess.Popen(['cmd'])\n", encoding="utf-8")
        violations = scan_file(str(bad_code))
        assert len(violations) >= 1

    def test_allows_gateway_consumer(self, tmp_path):
        good_code = tmp_path / "good.py"
        good_code.write_text(
            "from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway\n"
            "gw = ProcessLifecycleGateway()\n"
            "gw.launch('test', ['python'])\n",
            encoding="utf-8",
        )
        violations = scan_file(str(good_code))
        assert len(violations) == 0

    def test_nonexistent_file(self):
        violations = scan_file("/nonexistent/path/file.py")
        assert violations == []

    def test_empty_file(self, tmp_path):
        py = tmp_path / "empty.py"
        py.write_text("", encoding="utf-8")
        violations = scan_file(str(py))
        assert violations == []

    def test_safe_code_no_violations(self, tmp_path):
        py = tmp_path / "safe.py"
        py.write_text("import os\nprint(os.getcwd())\n", encoding="utf-8")
        violations = scan_file(str(py))
        assert violations == []

    def test_multiple_violations(self, tmp_path):
        py = tmp_path / "multi.py"
        py.write_text(
            "import subprocess\nimport multiprocessing\n"
            "subprocess.Popen(['a'])\nsubprocess.call(['b'])\n"
            "multiprocessing.Process(target=f)\n",
            encoding="utf-8",
        )
        violations = scan_file(str(py))
        assert len(violations) >= 3

    def test_syntax_error_file(self, tmp_path):
        py = tmp_path / "bad_syntax.py"
        py.write_text("def broken(\n", encoding="utf-8")
        with pytest.raises(SyntaxError):
            scan_file(str(py))


class TestScanDirectory:
    def test_empty_directory(self, tmp_path):
        gr = scan_directory(tmp_path)
        assert gr.passed is True
        assert gr.scanned_files == 0

    def test_no_src_dir(self, tmp_path):
        other = tmp_path / "other"
        other.mkdir()
        gr = scan_directory(tmp_path)
        assert gr.passed is True
        assert gr.scanned_files == 0

    def test_with_violations(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr" / "l00-data-source"
        src_dir.mkdir(parents=True)
        bad = src_dir / "bad.py"
        bad.write_text("import subprocess\nsubprocess.Popen(['cmd'])\n", encoding="utf-8")
        gr = scan_directory(tmp_path)
        assert gr.passed is False
        assert gr.scanned_files >= 1

    def test_with_clean_files(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr" / "l00-data-source"
        src_dir.mkdir(parents=True)
        good = src_dir / "good.py"
        good.write_text("import os\nprint('hello')\n", encoding="utf-8")
        gr = scan_directory(tmp_path)
        assert gr.passed is True
        assert gr.scanned_files >= 1

    def test_exclude_dirs(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr" / "bad_pkg"
        src_dir.mkdir(parents=True)
        bad = src_dir / "bad.py"
        bad.write_text("import subprocess\nsubprocess.Popen(['cmd'])\n", encoding="utf-8")
        gr = scan_directory(tmp_path, exclude_dirs=["bad_pkg"])
        assert gr.passed is True

    def test_allowed_files_skipped(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr" / "shared" / "infra"
        src_dir.mkdir(parents=True)
        pool = src_dir / "process_pool.py"
        pool.write_text("import subprocess\nsubprocess.Popen(['cmd'])\n", encoding="utf-8")
        gr = scan_directory(tmp_path)
        assert gr.scanned_files >= 1

    def test_default_exclude_dirs(self, tmp_path):
        src_dir = tmp_path / "src" / "zephyr" / "__pycache__"
        src_dir.mkdir(parents=True)
        bad = src_dir / "bad.py"
        bad.write_text("import subprocess\nsubprocess.Popen(['cmd'])\n", encoding="utf-8")
        gr = scan_directory(tmp_path)
        assert gr.passed is True


class TestResult:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_process_lifecycle_gateway.scan_directory")
    def test_result_delegates(self, mock_scan):
        mock_scan.return_value = GateResult(passed=True, scanned_files=42)
        r = result()
        assert r.passed is True
        assert r.scanned_files == 42

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_process_lifecycle_gateway.scan_directory")
    def test_result_with_violations(self, mock_scan):
        v = Violation(file="a.py", line=1, call_type="subprocess.Popen", snippet="x")
        mock_scan.return_value = GateResult(passed=False, violations=[v], scanned_files=10)
        r = result()
        assert r.passed is False
        assert len(r.violations) == 1
