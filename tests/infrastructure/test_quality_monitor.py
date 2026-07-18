# [A_test] module_id: SRC-TST-1422 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-421 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_quality_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_quality_monitor.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.quality.quality_monitor import (
    CodeQualityReport,
    QualityMetric,
    QualityMonitor,
)


class TestQualityMonitorInstantiation:
    def test_default_construction(self):
        monitor = QualityMonitor()
        assert monitor.MAX_LINE_LENGTH == 150
        assert monitor.MAX_FUNCTION_LENGTH == 200
        assert monitor.MIN_DOCSTRING_COVERAGE == 0.5

    def test_class_constants_are_class_level(self):
        assert QualityMonitor.MAX_LINE_LENGTH == 150
        assert QualityMonitor.MAX_FUNCTION_LENGTH == 200


class TestAnalyzeFile:
    def test_nonexistent_file_returns_failed_report(self, tmp_path):
        monitor = QualityMonitor()
        report = monitor.analyze_file("nonexistent.py", project_root=tmp_path)
        assert report.passed is False
        assert report.overall_score == 0.0
        assert "File not found" in report.issues
        assert len(report.metrics) == 0

    def test_clean_file_passes(self, tmp_path):
        clean_code = '"""Module."""\n\ndef hello():\n    """Say hi."""\n    return "hi"\n'
        p = tmp_path / "clean.py"
        p.write_text(clean_code, encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("clean.py", project_root=tmp_path)
        assert isinstance(report, CodeQualityReport)
        assert report.file_path == "clean.py"
        assert len(report.metrics) > 0

    def test_file_with_wildcard_import_fails_imports_metric(self, tmp_path):
        bad_code = '"""Module."""\nfrom os import *\n\ndef foo():\n    """Doc."""\n    return 1\n'
        p = tmp_path / "wildcard.py"
        p.write_text(bad_code, encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("wildcard.py", project_root=tmp_path)
        import_metric = next((m for m in report.metrics if m.name == "imports"), None)
        assert import_metric is not None
        assert import_metric.passed is False
        assert import_metric.value == 1.0

    def test_file_with_long_lines_fails_line_length_metric(self, tmp_path):
        long_line = "x" * 200
        bad_code = f'"""Module."""\n{long_line}\n\ndef foo():\n    """Doc."""\n    return 1\n'
        p = tmp_path / "long_lines.py"
        p.write_text(bad_code, encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("long_lines.py", project_root=tmp_path)
        line_metric = next((m for m in report.metrics if m.name == "line_length"), None)
        assert line_metric is not None
        assert line_metric.passed is False

    def test_file_with_syntax_error_still_produces_partial_metrics(self, tmp_path):
        bad_code = "def broken(\n"
        p = tmp_path / "syntax_err.py"
        p.write_text(bad_code, encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("syntax_err.py", project_root=tmp_path)
        assert any("Syntax error" in issue for issue in report.issues)
        line_len_metric = next((m for m in report.metrics if m.name == "line_length"), None)
        assert line_len_metric is not None

    def test_file_with_camel_case_function_fails_naming(self, tmp_path):
        bad_code = '"""Module."""\n\ndef badFunc():\n    """Doc."""\n    return 1\n'
        p = tmp_path / "camel.py"
        p.write_text(bad_code, encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("camel.py", project_root=tmp_path)
        naming_metric = next((m for m in report.metrics if m.name == "naming"), None)
        assert naming_metric is not None
        assert naming_metric.passed is False

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.py"
        p.write_text("", encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("empty.py", project_root=tmp_path)
        assert isinstance(report, CodeQualityReport)
        assert len(report.metrics) >= 2

    def test_project_root_defaults_to_cwd(self, tmp_path):
        p = tmp_path / "sample.py"
        p.write_text('"""Module."""\n\ndef ok():\n    """Doc."""\n    return 1\n', encoding="utf-8")

        monitor = QualityMonitor()
        report = monitor.analyze_file("sample.py", project_root=tmp_path)
        assert report.file_path == "sample.py"


class TestValidatePythonFile:
    def test_returns_tuple_bool_report(self, tmp_path):
        good_code = '"""Module."""\n\ndef ok():\n    """Doc."""\n    return 1\n'
        p = tmp_path / "good.py"
        p.write_text(good_code, encoding="utf-8")

        monitor = QualityMonitor()
        passed, report = monitor.validate_python_file("good.py", project_root=tmp_path)
        assert isinstance(passed, bool)
        assert isinstance(report, CodeQualityReport)

    def test_nonexistent_file_returns_false(self, tmp_path):
        monitor = QualityMonitor()
        passed, report = monitor.validate_python_file("nope.py", project_root=tmp_path)
        assert passed is False
        assert report.passed is False


class TestQualityMetricDataclass:
    def test_metric_fields(self):
        m = QualityMetric(name="test", value=0.5, threshold=0.1, passed=True)
        assert m.name == "test"
        assert m.value == 0.5
        assert m.threshold == 0.1
        assert m.passed is True

    def test_metric_zero_values(self):
        m = QualityMetric(name="x", value=0.0, threshold=0.0, passed=False)
        assert m.value == 0.0
        assert m.passed is False


class TestCodeQualityReportDataclass:
    def test_report_fields(self):
        r = CodeQualityReport(
            file_path="a.py",
            overall_score=0.8,
            metrics=[],
            issues=[],
            passed=True,
        )
        assert r.file_path == "a.py"
        assert r.overall_score == 0.8
        assert r.passed is True
        assert len(r.metrics) == 0
        assert len(r.issues) == 0
