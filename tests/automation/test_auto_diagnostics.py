# [A_test] module_id: MOD-GOV_auto_diagnostics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §auto_diagnostics
# [MODULE] tests.test_auto_diagnostics
# [INVARIANTS] AutoDiagnostics.diagnose必须返回DiagnosisReport; DiagnosisReport.to_dict必须包含所有字段
# [MODIFY-GUARD] 仅当auto_diagnostics公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_auto_diagnostics.py -q
# [TTL] task_bound

from zephyr.infrastructure.auto_diagnostics import (
    AutoDiagnostics,
    DiagnosisReport,
    DiagnosisSeverity,
    DiagnosisStatus,
)


class TestDiagnosisSeverity:
    def test_values(self):
        assert DiagnosisSeverity.CRITICAL.value == "critical"
        assert DiagnosisSeverity.HIGH.value == "high"
        assert DiagnosisSeverity.MEDIUM.value == "medium"
        assert DiagnosisSeverity.LOW.value == "low"
        assert DiagnosisSeverity.INFO.value == "info"

    def test_is_str_enum(self):
        assert isinstance(DiagnosisSeverity.CRITICAL, str)


class TestDiagnosisStatus:
    def test_values(self):
        assert DiagnosisStatus.HEALTHY.value == "healthy"
        assert DiagnosisStatus.DEGRADED.value == "degraded"
        assert DiagnosisStatus.FAILING.value == "failing"
        assert DiagnosisStatus.UNKNOWN.value == "unknown"

    def test_is_str_enum(self):
        assert isinstance(DiagnosisStatus.HEALTHY, str)


class TestDiagnosisReport:
    def test_default_construction(self):
        report = DiagnosisReport(report_id="DR-0001")
        assert report.report_id == "DR-0001"
        assert report.severity == DiagnosisSeverity.INFO
        assert report.status == DiagnosisStatus.UNKNOWN
        assert report.symptoms == []
        assert report.root_cause == ""
        assert report.evidence == []
        assert report.recommendations == []
        assert report.confidence == 0.0
        assert report.inversion_verified is False
        assert report.metadata == {}

    def test_to_dict_contains_all_fields(self):
        report = DiagnosisReport(
            report_id="DR-0099",
            severity=DiagnosisSeverity.HIGH,
            status=DiagnosisStatus.FAILING,
            component="gate_engine",
            symptoms=["timeout"],
            root_cause="resource contention",
            confidence=0.85,
        )
        d = report.to_dict()
        assert d["report_id"] == "DR-0099"
        assert d["severity"] == "high"
        assert d["status"] == "failing"
        assert d["component"] == "gate_engine"
        assert d["symptoms"] == ["timeout"]
        assert d["root_cause"] == "resource contention"
        assert d["confidence"] == 0.85
        assert "diagnosed_at" in d
        assert "metadata" in d

    def test_to_dict_with_evidence_and_recommendations(self):
        report = DiagnosisReport(
            report_id="DR-0100",
            evidence=[{"key": "val"}],
            recommendations=["fix A", "fix B"],
        )
        d = report.to_dict()
        assert d["evidence"] == [{"key": "val"}]
        assert d["recommendations"] == ["fix A", "fix B"]


class TestAutoDiagnostics:
    def test_instantiation_no_config(self):
        engine = AutoDiagnostics()
        assert engine is not None
        assert len(engine._rules) > 0

    def test_diagnose_matching_timeout(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("操作timeout超时", component="pipeline")
        assert report.severity == DiagnosisSeverity.HIGH
        assert report.status == DiagnosisStatus.FAILING
        assert report.confidence > 0.0
        assert len(report.recommendations) > 0

    def test_diagnose_matching_import_error(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("ModuleNotFoundError: No module named 'xxx'")
        assert report.severity == DiagnosisSeverity.CRITICAL
        assert report.status == DiagnosisStatus.FAILING

    def test_diagnose_matching_permission(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("PermissionError: 拒绝访问")
        assert report.severity == DiagnosisSeverity.HIGH

    def test_diagnose_matching_encoding(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("UnicodeDecodeError encoding 乱码")
        assert report.severity == DiagnosisSeverity.MEDIUM
        assert report.status == DiagnosisStatus.DEGRADED

    def test_diagnose_matching_orphan(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("文件是orphan未注册")
        assert report.severity == DiagnosisSeverity.MEDIUM

    def test_diagnose_no_match(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("一切正常", component="health")
        assert report.severity == DiagnosisSeverity.INFO
        assert report.confidence == 0.0
        assert report.root_cause == "未知"

    def test_diagnose_dict_event(self):
        engine = AutoDiagnostics()
        report = engine.diagnose({"error": "timeout exceeded"}, component="worker")
        assert isinstance(report, DiagnosisReport)

    def test_diagnose_empty_string(self):
        engine = AutoDiagnostics()
        report = engine.diagnose("")
        assert isinstance(report, DiagnosisReport)
        assert report.severity == DiagnosisSeverity.INFO

    def test_diagnose_none_converted_to_string(self):
        engine = AutoDiagnostics()
        report = engine.diagnose(str(None))
        assert isinstance(report, DiagnosisReport)

    def test_diagnose_increments_count(self):
        engine = AutoDiagnostics()
        engine.diagnose("timeout")
        engine.diagnose("import failed")
        assert engine._diagnosis_count == 2

    def test_diagnose_nonexistent_config_path_falls_back(self):
        engine = AutoDiagnostics(config_path="/nonexistent/path/rules.yaml")
        assert len(engine._rules) > 0
        report = engine.diagnose("timeout")
        assert report.confidence > 0.0
