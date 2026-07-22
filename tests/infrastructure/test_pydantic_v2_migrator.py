# [A_test] module_id: MOD-GOV_pydantic_v2_migrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §pydantic_v2_migrator
# [MODULE] tests.test_pydantic_v2_migrator
# [INVARIANTS] PydanticV2Migrator.scan必须返回MigrationReport; skip=True的pattern不应出现在findings中
# [MODIFY-GUARD] 仅当pydantic_v2_migrator公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_pydantic_v2_migrator.py -q
# [TTL] task_bound

from zephyr.infrastructure.pydantic_v2_migrator import (
    MigrationFinding,
    MigrationReport,
    PydanticV2Migrator,
)


class TestMigrationFinding:
    def test_default_construction(self):
        finding = MigrationFinding(
            file_path="test.py",
            line=10,
            pattern="class Config:",
        )
        assert finding.file_path == "test.py"
        assert finding.line == 10
        assert finding.pattern == "class Config:"
        assert finding.severity == "medium"
        assert finding.v1_code == ""
        assert finding.v2_suggestion == ""


class TestMigrationReport:
    def test_default_construction(self):
        report = MigrationReport()
        assert report.files_scanned == 0
        assert report.findings == []
        assert report.error_files == []

    def test_total_findings(self):
        report = MigrationReport(
            findings=[
                MigrationFinding(file_path="a.py", line=1, pattern="x"),
                MigrationFinding(file_path="b.py", line=2, pattern="y"),
            ]
        )
        assert report.total_findings == 2

    def test_critical_count(self):
        report = MigrationReport(
            findings=[
                MigrationFinding(file_path="a.py", line=1, pattern="x", severity="critical"),
                MigrationFinding(file_path="b.py", line=2, pattern="y", severity="high"),
                MigrationFinding(file_path="c.py", line=3, pattern="z", severity="critical"),
            ]
        )
        assert report.critical_count == 2


class TestPydanticV2Migrator:
    def test_instantiation(self):
        migrator = PydanticV2Migrator()
        assert migrator is not None

    def test_scan_empty_directory(self, tmp_path):
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        assert isinstance(report, MigrationReport)
        assert report.files_scanned == 0

    def test_scan_nonexistent_directory(self):
        migrator = PydanticV2Migrator()
        report = migrator.scan("/nonexistent/path")
        assert report.files_scanned == 0

    def test_scan_finds_v1_patterns(self, tmp_path):
        test_file = tmp_path / "model.py"
        test_file.write_text(
            "from pydantic import BaseModel\n\n"
            "class MyModel(BaseModel):\n"
            "    name: str\n\n"
            "    class Config:\n"
            "        orm_mode = True\n",
            encoding="utf-8",
        )
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        assert report.files_scanned == 1
        assert report.total_findings >= 2
        patterns = [f.pattern for f in report.findings]
        assert "class Config:" in patterns
        assert "orm_mode" in patterns

    def test_scan_skips_marked_patterns(self, tmp_path):
        test_file = tmp_path / "model2.py"
        test_file.write_text(
            "from pydantic import BaseModel\n",
            encoding="utf-8",
        )
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        base_import_findings = [f for f in report.findings if f.pattern == "from pydantic import BaseModel"]
        assert len(base_import_findings) == 0

    def test_scan_finds_validator(self, tmp_path):
        test_file = tmp_path / "validators.py"
        test_file.write_text(
            "from pydantic import validator\n\n@validator('name')\ndef validate_name(cls, v):\n    return v\n",
            encoding="utf-8",
        )
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        patterns = [f.pattern for f in report.findings]
        assert "@validator" in patterns

    def test_apply_migrations_dry_run(self, tmp_path):
        test_file = tmp_path / "model3.py"
        test_file.write_text(
            "class Config:\n    orm_mode = True\n",
            encoding="utf-8",
        )
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        result = migrator.apply_migrations(report, dry_run=True)
        assert result["dry_run"] is True
        assert result["files_modified"] >= 1
        original = test_file.read_text(encoding="utf-8")
        assert "orm_mode" in original

    def test_apply_migrations_real(self, tmp_path):
        test_file = tmp_path / "model4.py"
        test_file.write_text(
            "class Config:\n    orm_mode = True\n",
            encoding="utf-8",
        )
        migrator = PydanticV2Migrator()
        report = migrator.scan(str(tmp_path))
        result = migrator.apply_migrations(report, dry_run=False)
        assert result["files_modified"] >= 1

    def test_generate_migration_checklist_empty(self):
        migrator = PydanticV2Migrator()
        report = MigrationReport()
        checklist = migrator.generate_migration_checklist(report)
        assert len(checklist) > 0

    def test_generate_migration_checklist_with_findings(self):
        migrator = PydanticV2Migrator()
        report = MigrationReport(
            findings=[
                MigrationFinding(file_path="a.py", line=1, pattern="x", severity="high"),
            ]
        )
        checklist = migrator.generate_migration_checklist(report)
        assert any("1" in item for item in checklist)

    def test_scan_handles_unreadable_file(self, tmp_path):
        locked = tmp_path / "locked.py"
        locked.write_text("content", encoding="utf-8")
        locked.chmod(0o000)
        try:
            migrator = PydanticV2Migrator()
            report = migrator.scan(str(tmp_path))
            assert isinstance(report, MigrationReport)
        finally:
            locked.chmod(0o644)
