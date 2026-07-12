# [A_test] module_id: SRC-TST-0565 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_config_consistency
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_config_consistency.py -q
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from zephyr.gov_drift.config_consistency import (
    SECRET_KEY_INDICATORS,
    ConfigAuditReport,
    ConfigConflict,
    ConfigSource,
    detect_conflicts,
    extract_hardcoded_defaults,
    generate_config_sync,
    parse_env_config,
    parse_yaml_config,
    run_config_audit,
)


class TestConfigSource:
    def test_instantiation_defaults(self):
        cs = ConfigSource(source_type="YAML", source_path="/tmp/test.yaml")
        assert cs.source_type == "YAML"
        assert cs.source_path == "/tmp/test.yaml"
        assert cs.entries == {}

    def test_instantiation_with_entries(self):
        cs = ConfigSource(
            source_type="ENV",
            source_path="/tmp/.env",
            entries={"KEY1": "val1", "KEY2": "val2"},
        )
        assert cs.entries["KEY1"] == "val1"
        assert len(cs.entries) == 2


class TestConfigConflict:
    def test_instantiation_defaults(self):
        cc = ConfigConflict(key="db_host", sources=["YAML", "ENV"], values=["localhost", "remote"])
        assert cc.key == "db_host"
        assert cc.sources == ["YAML", "ENV"]
        assert cc.values == ["localhost", "remote"]
        assert cc.resolved_to is None

    def test_instantiation_with_resolution(self):
        cc = ConfigConflict(key="port", sources=["YAML", "ENV"], values=["8080", "9090"], resolved_to="8080")
        assert cc.resolved_to == "8080"


class TestConfigAuditReport:
    def test_instantiation_defaults(self):
        r = ConfigAuditReport()
        assert r.conflicts == []
        assert r.missing_secrets == []
        assert r.unused_configs == []
        assert r.total_keys == 0
        assert r.ssot_source == "YAML"
        assert isinstance(r.report_time, datetime)

    def test_instantiation_custom(self):
        now = datetime.now(UTC)
        r = ConfigAuditReport(
            conflicts=[ConfigConflict(key="k", sources=["YAML"], values=["v"])],
            missing_secrets=["api_key"],
            unused_configs=["old_setting"],
            total_keys=10,
            ssot_source="YAML",
            report_time=now,
        )
        assert len(r.conflicts) == 1
        assert r.missing_secrets == ["api_key"]
        assert r.total_keys == 10


class TestParseYamlConfig:
    def test_parses_simple_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("db_host: localhost\nport: 8080\ndebug: true\n")
            f.flush()
            cs = parse_yaml_config(f.name)
        os.unlink(f.name)
        assert cs.source_type == "YAML"
        assert cs.entries["db_host"] == "localhost"
        assert cs.entries["port"] == "8080"
        assert cs.entries["debug"] == "true"

    def test_nonexistent_file_returns_empty(self):
        cs = parse_yaml_config("/nonexistent/path/config.yaml")
        assert cs.entries == {}

    def test_skips_comment_keys(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("key1: val1\n#comment: ignored\nkey2: val2\n")
            f.flush()
            cs = parse_yaml_config(f.name)
        os.unlink(f.name)
        assert "#comment" not in cs.entries
        assert "key1" in cs.entries


class TestParseEnvConfig:
    def test_parses_env_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("DB_HOST=localhost\nDB_PORT=5432\n")
            f.flush()
            cs = parse_env_config(f.name)
        os.unlink(f.name)
        assert cs.source_type == "ENV"
        assert cs.entries["DB_HOST"] == "localhost"
        assert cs.entries["DB_PORT"] == "5432"

    def test_nonexistent_file_returns_empty(self):
        cs = parse_env_config("/nonexistent/.env")
        assert cs.entries == {}

    def test_skips_comment_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("#COMMENT=value\nREAL_KEY=real_val\n")
            f.flush()
            cs = parse_env_config(f.name)
        os.unlink(f.name)
        assert "#COMMENT" not in cs.entries
        assert cs.entries["REAL_KEY"] == "real_val"


class TestExtractHardcodedDefaults:
    def test_extracts_from_python_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "sample.py"
            py_file.write_text(
                'import os\ndb_host = os.environ.get("DB_HOST", "localhost")\n',
                encoding="utf-8",
            )
            cs = extract_hardcoded_defaults(tmpdir)
            assert cs.source_type == "CODE_DEFAULTS"
            assert "DB_HOST" in cs.entries
            assert cs.entries["DB_HOST"] == "localhost"

    def test_empty_src_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cs = extract_hardcoded_defaults(tmpdir)
            assert cs.entries == {}


class TestDetectConflicts:
    def test_no_conflicts_when_consistent(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"key1": "val1"})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={"key1": "val1"})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert report.conflicts == []

    def test_detects_value_conflict(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"port": "8080"})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={"port": "9090"})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert len(report.conflicts) == 1
        assert report.conflicts[0].key == "port"
        assert report.conflicts[0].resolved_to == "8080"

    def test_detects_missing_secrets(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"api_key": "secret123"})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert "api_key" in report.missing_secrets

    def test_detects_unused_configs(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={"OLD_VAR": "x"})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert "OLD_VAR" in report.unused_configs

    def test_total_keys_count(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"a": "1", "b": "2"})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={"c": "3"})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert report.total_keys == 3

    def test_same_value_no_conflict(self):
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"k": "v"})
        env_src = ConfigSource(source_type="ENV", source_path="", entries={"k": "v"})
        code_src = ConfigSource(source_type="CODE_DEFAULTS", source_path="", entries={"k": "v"})
        report = detect_conflicts(yaml_src, env_src, code_src)
        assert report.conflicts == []


class TestGenerateConfigSync:
    def test_generates_output_with_conflicts(self):
        report = ConfigAuditReport(
            conflicts=[
                ConfigConflict(key="port", sources=["YAML", "ENV"], values=["8080", "9090"], resolved_to="8080")
            ],
            missing_secrets=[],
            unused_configs=[],
            total_keys=1,
        )
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={"port": "8080"})
        output = generate_config_sync(report, yaml_src)
        assert "port: 8080" in output
        assert "Conflicts resolved: 1" in output

    def test_generates_output_with_missing_secrets(self):
        report = ConfigAuditReport(
            conflicts=[],
            missing_secrets=["api_key"],
            unused_configs=[],
            total_keys=1,
        )
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={})
        output = generate_config_sync(report, yaml_src)
        assert "MISSING_SECRET_WARNING" in output
        assert "api_key" in output

    def test_generates_output_with_unused_configs(self):
        report = ConfigAuditReport(
            conflicts=[],
            missing_secrets=[],
            unused_configs=["old_setting"],
            total_keys=1,
        )
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={})
        output = generate_config_sync(report, yaml_src)
        assert "UNUSED_CONFIG" in output
        assert "old_setting" in output

    def test_empty_report_generates_header(self):
        report = ConfigAuditReport(conflicts=[], missing_secrets=[], unused_configs=[], total_keys=0)
        yaml_src = ConfigSource(source_type="YAML", source_path="", entries={})
        output = generate_config_sync(report, yaml_src)
        assert "config_sync.yaml" in output
        assert "Conflicts resolved: 0" in output


class TestSecretKeyIndicators:
    def test_contains_common_indicators(self):
        assert "secret" in SECRET_KEY_INDICATORS
        assert "password" in SECRET_KEY_INDICATORS
        assert "token" in SECRET_KEY_INDICATORS
        assert "api_key" in SECRET_KEY_INDICATORS

    def test_is_set(self):
        assert isinstance(SECRET_KEY_INDICATORS, set)


class TestRunConfigAudit:
    def test_empty_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_config_audit(tmpdir)
            assert isinstance(result, dict)
            assert "conflicts" in result
            assert "missing_secrets" in result
            assert "unused_configs" in result
            assert "total_keys" in result
            assert "ssot_source" in result

    def test_with_yaml_and_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "config.yaml"
            yaml_path.write_text("db_host: localhost\n", encoding="utf-8")
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("DB_HOST=remote\n", encoding="utf-8")
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            result = run_config_audit(tmpdir)
            assert result["ssot_source"] == "YAML"
