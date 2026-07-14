# [A_test] module_id: SRC-TST-1767 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §4
# [MODULE] tests.test_triple_alignment
# [INVARIANTS] Severity has exactly ERROR/WARN; AlignmentViolation fields immutable after creation; TripleAlignmentResult.passed flips to False on ERROR violation
# [MODIFY-GUARD] zephyr.gov_enforcement.rule_enforcement.triple_alignment
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on field mismatch or logic violation
# [TESTS] tests/test_triple_alignment.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.gov_enforcement.rule_enforcement.triple_alignment import (
    AlignmentViolation,
    Severity,
    TripleAlignmentResult,
    _extract_dep_map_depths,
    _extract_dep_map_modules,
    _load_yaml,
    _parse_code_headers,
    check_triple_alignment,
)


class TestSeverity:
    def test_enum_values(self):
        assert Severity.ERROR == "ERROR"
        assert Severity.WARN == "WARN"

    def test_enum_members_count(self):
        assert len(Severity) == 2

    def test_enum_is_string(self):
        assert isinstance(Severity.ERROR, str)
        assert isinstance(Severity.WARN, str)


class TestAlignmentViolation:
    def test_creation_with_required_fields(self):
        v = AlignmentViolation(
            check="module_id_code_vs_blueprint",
            severity=Severity.ERROR,
            module_id="MOD-GATE_ENGINE",
            source="code [BLUEPRINT] header",
            expected="MOD-GATE_ENGINE",
            actual="MOD-CONTEXT_ENGINE",
        )
        assert v.check == "module_id_code_vs_blueprint"
        assert v.severity == Severity.ERROR
        assert v.module_id == "MOD-GATE_ENGINE"
        assert v.source == "code [BLUEPRINT] header"
        assert v.expected == "MOD-GATE_ENGINE"
        assert v.actual == "MOD-CONTEXT_ENGINE"
        assert v.detail == ""

    def test_creation_with_detail(self):
        v = AlignmentViolation(
            check="attr_stability",
            severity=Severity.WARN,
            module_id="MOD-INF-020",
            source="blueprint vs code",
            expected="stable",
            actual="evolving",
            detail="stability mismatch",
        )
        assert v.detail == "stability mismatch"

    def test_empty_strings(self):
        v = AlignmentViolation(
            check="",
            severity=Severity.ERROR,
            module_id="",
            source="",
            expected="",
            actual="",
        )
        assert v.check == ""
        assert v.module_id == ""

    def test_severity_warn(self):
        v = AlignmentViolation(
            check="dep_map_orphan",
            severity=Severity.WARN,
            module_id="MOD-INF-099",
            source="dep-map",
            expected="in registry",
            actual="NOT FOUND",
        )
        assert v.severity == Severity.WARN


class TestTripleAlignmentResult:
    def test_default_values(self):
        r = TripleAlignmentResult()
        assert r.violations == []
        assert r.checked_modules == 0
        assert r.passed is True

    def test_add_violation_error_flips_passed(self):
        r = TripleAlignmentResult()
        v = AlignmentViolation(
            check="test_check",
            severity=Severity.ERROR,
            module_id="MOD-GATE_ENGINE",
            source="src",
            expected="A",
            actual="B",
        )
        r.add_violation(v)
        assert len(r.violations) == 1
        assert r.passed is False

    def test_add_violation_warn_keeps_passed(self):
        r = TripleAlignmentResult()
        v = AlignmentViolation(
            check="test_check",
            severity=Severity.WARN,
            module_id="MOD-GATE_ENGINE",
            source="src",
            expected="A",
            actual="B",
        )
        r.add_violation(v)
        assert len(r.violations) == 1
        assert r.passed is True

    def test_add_multiple_violations_mixed(self):
        r = TripleAlignmentResult()
        r.add_violation(
            AlignmentViolation(
                check="c1",
                severity=Severity.WARN,
                module_id="M1",
                source="s",
                expected="e",
                actual="a",
            )
        )
        r.add_violation(
            AlignmentViolation(
                check="c2",
                severity=Severity.ERROR,
                module_id="M2",
                source="s",
                expected="e",
                actual="a",
            )
        )
        assert len(r.violations) == 2
        assert r.passed is False

    def test_add_violation_warn_then_error(self):
        r = TripleAlignmentResult()
        r.add_violation(
            AlignmentViolation(
                check="c1",
                severity=Severity.WARN,
                module_id="M1",
                source="s",
                expected="e",
                actual="a",
            )
        )
        assert r.passed is True
        r.add_violation(
            AlignmentViolation(
                check="c2",
                severity=Severity.ERROR,
                module_id="M2",
                source="s",
                expected="e",
                actual="a",
            )
        )
        assert r.passed is False

    def test_summary_no_violations(self):
        r = TripleAlignmentResult(checked_modules=5)
        s = r.summary()
        assert "5 modules checked" in s
        assert "0 ERROR" in s
        assert "0 WARN" in s
        assert "PASS" in s

    def test_summary_with_errors_and_warns(self):
        r = TripleAlignmentResult(checked_modules=10)
        r.add_violation(
            AlignmentViolation(
                check="c1",
                severity=Severity.ERROR,
                module_id="M1",
                source="s",
                expected="e",
                actual="a",
            )
        )
        r.add_violation(
            AlignmentViolation(
                check="c2",
                severity=Severity.WARN,
                module_id="M2",
                source="s",
                expected="e",
                actual="a",
            )
        )
        r.add_violation(
            AlignmentViolation(
                check="c3",
                severity=Severity.ERROR,
                module_id="M3",
                source="s",
                expected="e",
                actual="a",
            )
        )
        s = r.summary()
        assert "10 modules checked" in s
        assert "2 ERROR" in s
        assert "1 WARN" in s
        assert "FAIL" in s

    def test_summary_only_warns(self):
        r = TripleAlignmentResult(checked_modules=3)
        r.add_violation(
            AlignmentViolation(
                check="c1",
                severity=Severity.WARN,
                module_id="M1",
                source="s",
                expected="e",
                actual="a",
            )
        )
        s = r.summary()
        assert "0 ERROR" in s
        assert "1 WARN" in s
        assert "PASS" in s


class TestLoadYaml:
    def test_loads_valid_yaml(self, tmp_path):
        p = tmp_path / "test.yaml"
        p.write_text("key: value\nlist:\n  - a\n  - b\n", encoding="utf-8")
        result = _load_yaml(p)
        assert result == {"key": "value", "list": ["a", "b"]}

    def test_returns_none_for_missing_file(self):
        p = Path("nonexistent_file_abc123.yaml")
        result = _load_yaml(p)
        assert result is None

    def test_loads_empty_yaml(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text("", encoding="utf-8")
        result = _load_yaml(p)
        assert result is None

    def test_loads_list_yaml(self, tmp_path):
        p = tmp_path / "list.yaml"
        p.write_text("- item1\n- item2\n", encoding="utf-8")
        result = _load_yaml(p)
        assert result == ["item1", "item2"]


class TestParseCodeHeaders:
    def test_parses_standard_headers(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "# [BLUEPRINT] MOD-GATE_ENGINE | bp.md | §4\n"
            "# [MODULE] zephyr.gov_enforcement.rule_enforcement.triple_alignment\n"
            "# [STABILITY] evolving\n"
            "# [SAFETY] M\n"
            "# [AI_AUTONOMY] ai_modifiable\n"
            "x = 1\n",
            encoding="utf-8",
        )
        headers = _parse_code_headers(p)
        assert headers["BLUEPRINT"] == "MOD-GATE_ENGINE | bp.md | §4"
        assert headers["MODULE"] == "zephyr.gov_enforcement.rule_enforcement.triple_alignment"
        assert headers["STABILITY"] == "evolving"
        assert headers["SAFETY"] == "M"
        assert headers["AI_AUTONOMY"] == "ai_modifiable"

    def test_returns_empty_for_missing_file(self):
        p = Path("nonexistent_mod_abc123.py")
        headers = _parse_code_headers(p)
        assert headers == {}

    def test_only_scans_first_30_lines(self, tmp_path):
        lines = [f"line {i}\n" for i in range(40)]
        lines[29] = "# [HEADER30] should_be_found\n"
        lines[30] = "# [HEADER31] should_not_be_found\n"
        p = tmp_path / "long.py"
        p.write_text("".join(lines), encoding="utf-8")
        headers = _parse_code_headers(p)
        assert "HEADER30" in headers
        assert "HEADER31" not in headers

    def test_no_headers_returns_empty(self, tmp_path):
        p = tmp_path / "noheaders.py"
        p.write_text("x = 1\ny = 2\n", encoding="utf-8")
        headers = _parse_code_headers(p)
        assert headers == {}

    def test_handles_read_exception(self, tmp_path):
        p = tmp_path / "unreadable.py"
        p.write_text("content", encoding="utf-8")
        with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            headers = _parse_code_headers(p)
            assert headers == {}

    def test_header_with_hyphen_in_name(self, tmp_path):
        p = tmp_path / "hyphen.py"
        p.write_text("# [MODIFY-GUARD] some_guard\n", encoding="utf-8")
        headers = _parse_code_headers(p)
        assert headers["MODIFY-GUARD"] == "some_guard"


class TestExtractDepMapModules:
    """测试从 depgraph.nodes 数据库查询模块（替代原 system-dependency-map.md 解析）。"""

    def test_returns_modules_from_database(self):
        fake_rows = [
            ('MOD-GATE_ENGINE', 'src/zephyr/gov_enforcement/rule_enforcement/triple_alignment.py', 'docs/03_modules/.../blueprint.md'),
            ('MOD-INF-020', 'src/zephyr/audit_trail/audit.py', None),
        ]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = fake_rows
        mock_conn.cursor.return_value = mock_cur

        with patch(
            'zephyr.governance.depgraph_schema.get_depgraph_pg_connection',
            return_value=mock_conn,
        ):
            modules = _extract_dep_map_modules()

        assert 'MOD-GATE_ENGINE' in modules
        assert modules['MOD-GATE_ENGINE']['source_path'] == 'src/zephyr/gov_enforcement/rule_enforcement/triple_alignment.py'
        assert 'MOD-INF-020' in modules
        assert modules['MOD-INF-020']['blueprint_path'] == ''

    def test_deduplicates_by_blueprint_id(self):
        """一个模块有多行（多文件），只保留第一行的路径。"""
        fake_rows = [
            ('MOD-GATE_ENGINE', 'src/file1.py', 'bp.md'),
            ('MOD-GATE_ENGINE', 'src/file2.py', 'bp.md'),
        ]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = fake_rows
        mock_conn.cursor.return_value = mock_cur

        with patch(
            'zephyr.governance.depgraph_schema.get_depgraph_pg_connection',
            return_value=mock_conn,
        ):
            modules = _extract_dep_map_modules()

        assert len(modules) == 1
        assert 'MOD-GATE_ENGINE' in modules
        assert modules['MOD-GATE_ENGINE']['source_path'] == 'src/file1.py'

    def test_returns_empty_on_connection_error(self):
        with patch(
            'zephyr.governance.depgraph_schema.get_depgraph_pg_connection',
            side_effect=Exception('conn failed'),
        ):
            modules = _extract_dep_map_modules()
        assert modules == {}

    def test_returns_empty_when_no_modules(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cur

        with patch(
            'zephyr.governance.depgraph_schema.get_depgraph_pg_connection',
            return_value=mock_conn,
        ):
            modules = _extract_dep_map_modules()
        assert modules == {}


class TestExtractDepMapDepths:
    def test_extracts_depths(self):
        content = "| 1 | MOD-GATE_ENGINE |\n| 2 | MOD-INF-020 |\n| 3 | MOD-INF-025 |\n"
        depths = _extract_dep_map_depths(content)
        assert depths["MOD-GATE_ENGINE"] == "1"
        assert depths["MOD-INF-020"] == "2"
        assert depths["MOD-INF-025"] == "3"

    def test_empty_content(self):
        depths = _extract_dep_map_depths("")
        assert depths == {}

    def test_no_matching_lines(self):
        content = "some text\n| MOD-GATE_ENGINE | Gate |\n"
        depths = _extract_dep_map_depths(content)
        assert depths == {}

    def test_ignores_non_mod_inf(self):
        content = "| 1 | OTHER-001 |\n"
        depths = _extract_dep_map_depths(content)
        assert depths == {}


class TestCheckTripleAlignment:
    def test_returns_result_on_missing_blueprint_registry(self):
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value=None):
            result = check_triple_alignment()
            assert isinstance(result, TripleAlignmentResult)
            assert result.passed is False
            assert len(result.violations) == 1
            assert result.violations[0].check == "registry_load"

    def test_returns_result_on_invalid_blueprint_registry(self):
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value={"other_key": []}):
            result = check_triple_alignment()
            assert isinstance(result, TripleAlignmentResult)
            assert result.passed is False
            assert result.violations[0].check == "registry_load"

    def test_empty_blueprints_list(self):
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value={"blueprints": []}):
            with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._extract_dep_map_modules", return_value={}):
                result = check_triple_alignment()
                assert result.checked_modules == 0
                assert result.passed is True

    def test_warn_only_overrides_passed(self):
        registry_data = {
            "blueprints": [
                {
                    "module_id": "MOD-GATE_ENGINE",
                    "file_path": "nonexistent.md",
                    "construction_progress": "implemented",
                },
            ]
        }
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value=registry_data):
            with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._extract_dep_map_modules", return_value={}):
                result = check_triple_alignment(warn_only=True)
                assert result.passed is True

    def test_specific_module_filters(self):
        registry_data = {
            "blueprints": [
                {"module_id": "MOD-GATE_ENGINE", "file_path": "a.md"},
                {"module_id": "MOD-INF-020", "file_path": "b.md"},
            ]
        }
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value=registry_data):
            with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._extract_dep_map_modules", return_value={}):
                result = check_triple_alignment(specific_module="MOD-GATE_ENGINE")
                assert result.checked_modules == 1

    def test_blueprint_file_missing_violation(self):
        registry_data = {
            "blueprints": [
                {
                    "module_id": "MOD-GATE_ENGINE",
                    "file_path": "nonexistent_dir/fake_blueprint.md",
                    "construction_progress": "implemented",
                },
            ]
        }
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value=registry_data):
            with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._extract_dep_map_modules", return_value={}):
                result = check_triple_alignment()
                bp_missing = [v for v in result.violations if v.check == "blueprint_file_missing"]
                assert len(bp_missing) == 1
                assert bp_missing[0].severity == Severity.ERROR

    def test_dep_map_orphan_module(self):
        registry_data = {"blueprints": []}
        dep_map_modules = {
            "MOD-INF-099": {"source_path": "src/orphan/", "blueprint_path": "bp.md"},
        }
        with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._load_yaml", return_value=registry_data):
            with patch("zephyr.gov_enforcement.rule_enforcement.triple_alignment._extract_dep_map_modules", return_value=dep_map_modules):
                result = check_triple_alignment()
                orphans = [v for v in result.violations if v.check == "dep_map_orphan_module"]
                assert len(orphans) == 1
                assert orphans[0].module_id == "MOD-INF-099"
