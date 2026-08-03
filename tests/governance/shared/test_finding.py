# [A_test] module_id: MOD-GOV_finding | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] tests.test_finding
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] Finding ID deterministic from dimension+severity+target+description; LIFECYCLE_STATUS_VALUES SSoT
# [MODIFY-GUARD] script_system/finding.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError→fail on invalid enum
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json

import pytest

fmod = pytest.importorskip(
    "zephyr.infrastructure.script_system.finding",
    reason="finding import failed",
)


class TestDimension:
    def test_all_values(self):
        expected = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12"]
        for d in expected:
            assert fmod.Dimension(d).value == d

    def test_label(self):
        assert fmod.Dimension.D3.label == "元数据合规"
        assert fmod.Dimension.D6.label == "安全漏洞"


class TestSeverity:
    def test_all_values(self):
        for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            assert fmod.Severity(s).value == s


class TestBlastRadius:
    def test_values(self):
        assert fmod.BlastRadius.FILE.value == "file"
        assert fmod.BlastRadius.MODULE.value == "module"
        assert fmod.BlastRadius.LAYER.value == "layer"
        assert fmod.BlastRadius.SYSTEM.value == "system"


class TestRemediationAction:
    def test_values(self):
        expected = ["FIX", "DELETE", "MOVE", "UPDATE_REF", "CREATE", "INVESTIGATE"]
        for v in expected:
            assert fmod.RemediationAction(v).value == v


class TestLifecycleStatus:
    def test_all_values(self):
        expected = [
            "OPEN",
            "IN_PROGRESS",
            "FIXED",
            "VERIFIED",
            "FALSE_POSITIVE",
            "WONTFIX",
            "ACCEPTED_RISK",
            "CLOSED",
            "OVERDUE",
            "DEFERRED",
        ]
        for v in expected:
            assert fmod.LifecycleStatus(v).value == v

    def test_lifecycle_status_values_tuple(self):
        assert tuple(m.value for m in fmod.LifecycleStatus) == fmod.LIFECYCLE_STATUS_VALUES
        assert len(fmod.LIFECYCLE_STATUS_VALUES) == 10


class TestRecommendationType:
    def test_values(self):
        assert fmod.RecommendationType.AUTO_FIXABLE.value == "auto_fixable"
        assert fmod.RecommendationType.MANUAL_ONLY.value == "manual_only"
        assert fmod.RecommendationType.NEEDS_REVIEW.value == "needs_review"


class TestRecommendedAction:
    def test_values(self):
        assert fmod.RecommendedAction.MODIFY_FILE.value == "modify_file"
        assert fmod.RecommendedAction.CREATE_TASK.value == "create_task"


class TestFinding:
    def test_creation(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="元数据合规",
            target_file="docs/test.md",
            description="缺少必填字段",
        )
        assert f.dimension == fmod.Dimension.D3
        assert f.severity == fmod.Severity.HIGH
        assert f.category == "元数据合规"
        assert f.finding_id.startswith("FIND-D3-")

    def test_custom_finding_id(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
            finding_id="CUSTOM-ID",
        )
        assert f.finding_id == "CUSTOM-ID"

    def test_deterministic_id(self):
        f1 = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="same desc",
        )
        f2 = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="same desc",
        )
        assert f1.finding_id == f2.finding_id

    def test_to_dict(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test desc",
            evidence="evidence text",
        )
        d = f.to_dict()
        assert d["dimension"] == "D3"
        assert d["severity"] == "HIGH"
        assert d["description"] == "test desc"
        assert d["target"]["file_path"] == "test.py"
        assert d["evidence"] == "evidence text"

    def test_to_json(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
        )
        j = f.to_json()
        parsed = json.loads(j)
        assert parsed["dimension"] == "D3"

    def test_to_jsonl_line(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
        )
        line = f.to_jsonl_line()
        assert line.endswith("\n")
        parsed = json.loads(line)
        assert parsed["dimension"] == "D3"

    def test_repr(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
        )
        r = repr(f)
        assert "FIND-D3-" in r
        assert "SEV=HIGH" in r

    def test_from_result_dict(self):
        f = fmod.Finding.from_result_dict(
            rule_id="RULE-001",
            file_path="test.py",
            message="violation found",
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.MEDIUM,
        )
        assert f.category == "元数据合规 — RULE-001"
        assert f.target_file == "test.py"

    def test_recommendation_block(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
            recommendation="fix it",
            recommendation_type=fmod.RecommendationType.AUTO_FIXABLE,
        )
        d = f.to_dict()
        assert "recommendation_block" in d
        assert d["recommendation_block"]["recommendation"] == "fix it"

    def test_no_recommendation_block(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
        )
        d = f.to_dict()
        assert "recommendation_block" not in d


class TestFindingCollection:
    def test_creation(self):
        fc = fmod.FindingCollection()
        assert fc.total == 0
        assert len(fc) == 0

    def test_add(self):
        fc = fmod.FindingCollection()
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="test",
        )
        fc.add(f)
        assert fc.total == 1

    def test_extend(self):
        fc = fmod.FindingCollection()
        findings = [
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.HIGH,
                category="test",
                target_file=f"file{i}.py",
                description=f"desc{i}",
            )
            for i in range(3)
        ]
        fc.extend(findings)
        assert fc.total == 3

    def test_by_dimension(self):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.HIGH,
                category="test",
                target_file="a.py",
                description="d3 finding",
            )
        )
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D6,
                severity=fmod.Severity.CRITICAL,
                category="test",
                target_file="b.py",
                description="d6 finding",
            )
        )
        d3 = fc.by_dimension(fmod.Dimension.D3)
        assert d3.total == 1

    def test_by_severity(self):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.CRITICAL,
                category="test",
                target_file="a.py",
                description="crit",
            )
        )
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.LOW,
                category="test",
                target_file="b.py",
                description="low",
            )
        )
        crit = fc.by_severity(fmod.Severity.CRITICAL)
        assert crit.total == 1

    def test_critical_only(self):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.CRITICAL,
                category="test",
                target_file="a.py",
                description="crit",
            )
        )
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.LOW,
                category="test",
                target_file="b.py",
                description="low",
            )
        )
        crit = fc.critical_only()
        assert crit.total == 1

    def test_summary(self):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.HIGH,
                category="test",
                target_file="a.py",
                description="test",
            )
        )
        s = fc.summary()
        assert s["total"] == 1
        assert s["by_severity"]["HIGH"] == 1
        assert s["by_dimension"]["D3"] == 1

    def test_to_jsonl(self):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.HIGH,
                category="test",
                target_file="a.py",
                description="test",
            )
        )
        jsonl = fc.to_jsonl()
        assert jsonl.endswith("\n")

    def test_iter(self):
        fc = fmod.FindingCollection()
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="a.py",
            description="test",
        )
        fc.add(f)
        items = list(fc)
        assert len(items) == 1

    def test_write_jsonl(self, tmp_path):
        fc = fmod.FindingCollection()
        fc.add(
            fmod.Finding(
                dimension=fmod.Dimension.D3,
                severity=fmod.Severity.HIGH,
                category="test",
                target_file="a.py",
                description="test",
            )
        )
        out_path = str(tmp_path / "findings.jsonl")
        fc.write_jsonl(out_path)
        with open(out_path, encoding="utf-8") as fh:
            content = fh.read()
        assert "D3" in content


class TestBoundary:
    def test_finding_empty_description(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="test.py",
            description="",
        )
        assert f.description == ""

    def test_finding_empty_target_file(self):
        f = fmod.Finding(
            dimension=fmod.Dimension.D3,
            severity=fmod.Severity.HIGH,
            category="test",
            target_file="",
            description="test",
        )
        assert f.target_file == ""

    def test_collection_empty_jsonl(self):
        fc = fmod.FindingCollection()
        assert fc.to_jsonl() == ""

    def test_collection_summary_empty(self):
        fc = fmod.FindingCollection()
        s = fc.summary()
        assert s["total"] == 0
