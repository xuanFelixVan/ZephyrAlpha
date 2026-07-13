# [A_test] module_id: SRC-TST-0780 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_result_types
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_drift_result_types.py -q
# [TTL] task_bound

from __future__ import annotations

import yaml

from zephyr.gov_drift.drift_result_types import (
    DBSchemaDriftResult,
    DepVersionDriftResult,
    DocCodeCoevolutionResult,
    KnowledgeGraphSyncResult,
    SecurityPolicyDriftResult,
    SemanticDriftResult,
    _count_entries,
    _get_field,
    detect_concept_cardinality,
    detect_db_schema_drift,
    detect_dep_version_drift,
    detect_doc_code_coevolution,
    detect_enum_value_sync,
    detect_ownership_consistency,
    detect_security_policy_drift,
    detect_test_coverage_drift,
)
from zephyr.gov_drift.drift_result_types import (
    TestCoverageDriftResult as CovDriftResult,
)


class TestSemanticDriftResultInstantiation:
    def test_required_fields_only(self):
        r = SemanticDriftResult(dimension="D5_semantic", concept="agents.models")
        assert r.dimension == "D5_semantic"
        assert r.concept == "agents.models"
        assert r.yaml_a_count == 0
        assert r.yaml_b_count == 0
        assert r.drift_detected is False
        assert r.detail == ""

    def test_all_fields(self):
        r = SemanticDriftResult(
            dimension="D5_semantic",
            concept="test.path",
            yaml_a_count=5,
            yaml_b_count=3,
            drift_detected=True,
            detail="A:5 vs B:3",
        )
        assert r.yaml_a_count == 5
        assert r.yaml_b_count == 3
        assert r.drift_detected is True
        assert r.detail == "A:5 vs B:3"


class TestDetectConceptCardinality:
    def test_no_drift_equal_counts(self, tmp_path):
        data = {"agents": {"models": ["a", "b", "c"]}}
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump(data), encoding="utf-8")
        fb.write_text(yaml.dump(data), encoding="utf-8")
        result = detect_concept_cardinality(str(fa), str(fb), "agents.models")
        assert result.drift_detected is False
        assert result.yaml_a_count == 3
        assert result.yaml_b_count == 3
        assert result.dimension == "D5_semantic"

    def test_drift_different_counts(self, tmp_path):
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump({"agents": {"models": [1, 2, 3]}}), encoding="utf-8")
        fb.write_text(yaml.dump({"agents": {"models": [1, 2]}}), encoding="utf-8")
        result = detect_concept_cardinality(str(fa), str(fb), "agents.models")
        assert result.drift_detected is True
        assert result.yaml_a_count == 3
        assert result.yaml_b_count == 2

    def test_missing_file_a(self, tmp_path):
        fb = tmp_path / "b.yaml"
        fb.write_text(yaml.dump({"k": [1]}), encoding="utf-8")
        result = detect_concept_cardinality("/nonexistent/a.yaml", str(fb), "k")
        assert result.yaml_a_count == 0
        assert result.yaml_b_count == 1
        assert result.drift_detected is True

    def test_both_files_missing(self):
        result = detect_concept_cardinality("/no/a.yaml", "/no/b.yaml", "key")
        assert result.drift_detected is False
        assert result.yaml_a_count == 0
        assert result.yaml_b_count == 0

    def test_empty_yaml_files(self, tmp_path):
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text("", encoding="utf-8")
        fb.write_text("", encoding="utf-8")
        result = detect_concept_cardinality(str(fa), str(fb), "key")
        assert result.drift_detected is False

    def test_nested_path_resolution(self, tmp_path):
        data = {"level1": {"level2": {"items": [1, 2]}}}
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump(data), encoding="utf-8")
        fb.write_text(yaml.dump(data), encoding="utf-8")
        result = detect_concept_cardinality(str(fa), str(fb), "level1.level2.items")
        assert result.drift_detected is False
        assert result.yaml_a_count == 2


class TestDetectEnumValueSync:
    def test_sync_equal_sets(self, tmp_path):
        data = {"config": {"modes": ["fast", "slow"]}}
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump(data), encoding="utf-8")
        fb.write_text(yaml.dump(data), encoding="utf-8")
        result = detect_enum_value_sync(str(fa), str(fb), "config.modes")
        assert result.drift_detected is False
        assert result.dimension == "D5_semantic"
        assert "enum:" in result.concept

    def test_drift_different_sets(self, tmp_path):
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump({"config": {"modes": ["fast", "slow"]}}), encoding="utf-8")
        fb.write_text(yaml.dump({"config": {"modes": ["fast", "medium"]}}), encoding="utf-8")
        result = detect_enum_value_sync(str(fa), str(fb), "config.modes")
        assert result.drift_detected is True

    def test_non_list_field_no_crash(self, tmp_path):
        fa = tmp_path / "a.yaml"
        fb = tmp_path / "b.yaml"
        fa.write_text(yaml.dump({"config": {"modes": "not_a_list"}}), encoding="utf-8")
        fb.write_text(yaml.dump({"config": {"modes": "also_not"}}), encoding="utf-8")
        result = detect_enum_value_sync(str(fa), str(fb), "config.modes")
        assert result.drift_detected is False

    def test_missing_file_handled(self, tmp_path):
        fb = tmp_path / "b.yaml"
        fb.write_text(yaml.dump({"config": {"modes": ["a"]}}), encoding="utf-8")
        result = detect_enum_value_sync("/nonexistent/a.yaml", str(fb), "config.modes")
        assert isinstance(result, SemanticDriftResult)


class TestDetectOwnershipConsistency:
    def test_no_drift_single_owner(self, tmp_path):
        fp = tmp_path / "f.yaml"
        fp.write_text(yaml.dump({"owner": "alice"}), encoding="utf-8")
        results = detect_ownership_consistency([str(fp)])
        assert results == []

    def test_empty_paths_list(self):
        results = detect_ownership_consistency([])
        assert results == []

    def test_nonexistent_path_returns_empty(self):
        results = detect_ownership_consistency(["/nonexistent/file.yaml"])
        assert results == []

    def test_missing_owner_field(self, tmp_path):
        fp = tmp_path / "f.yaml"
        fp.write_text(yaml.dump({"name": "test"}), encoding="utf-8")
        results = detect_ownership_consistency([str(fp)])
        assert results == []

    def test_custom_owner_field(self, tmp_path):
        fp = tmp_path / "f.yaml"
        fp.write_text(yaml.dump({"maintainer": "bob"}), encoding="utf-8")
        results = detect_ownership_consistency([str(fp)], owner_field="maintainer")
        assert results == []


class TestCountEntries:
    def test_list_count(self):
        assert _count_entries({"a": [1, 2, 3]}, "a") == 3

    def test_dict_count(self):
        assert _count_entries({"a": {"x": 1, "y": 2}}, "a") == 2

    def test_missing_key(self):
        assert _count_entries({"a": 1}, "b") == 0

    def test_scalar_value(self):
        assert _count_entries({"a": "hello"}, "a") == 0

    def test_nested_path(self):
        assert _count_entries({"a": {"b": [1, 2]}}, "a.b") == 2

    def test_empty_list(self):
        assert _count_entries({"a": []}, "a") == 0

    def test_empty_dict(self):
        assert _count_entries({"a": {}}, "a") == 0

    def test_deeply_nested(self):
        assert _count_entries({"a": {"b": {"c": [1]}}}, "a.b.c") == 1


class TestGetField:
    def test_simple_key(self):
        assert _get_field({"a": 1}, "a") == 1

    def test_nested_key(self):
        assert _get_field({"a": {"b": 2}}, "a.b") == 2

    def test_missing_key(self):
        assert _get_field({"a": 1}, "x") is None

    def test_non_dict_intermediate(self):
        assert _get_field({"a": 1}, "a.b") is None

    def test_none_value(self):
        assert _get_field({"a": None}, "a") is None

    def test_empty_path(self):
        result = _get_field({"a": 1}, "")
        assert result is None or result == {"a": 1}


class TestDBSchemaDriftResultInstantiation:
    def test_default_fields(self):
        r = DBSchemaDriftResult()
        assert r.detector_name == "db_schema_drift"
        assert r.schema_vs_orm_drifts == []
        assert r.orm_vs_migration_drifts == []
        assert r.index_inconsistencies == []

    def test_custom_fields(self):
        r = DBSchemaDriftResult(
            schema_vs_orm_drifts=[{"table": "users", "diff": "col missing"}],
            orm_vs_migration_drifts=[{"table": "orders"}],
            index_inconsistencies=[{"idx": "idx_users"}],
        )
        assert len(r.schema_vs_orm_drifts) == 1
        assert len(r.orm_vs_migration_drifts) == 1
        assert len(r.index_inconsistencies) == 1


class TestDepVersionDriftResultInstantiation:
    def test_default_fields(self):
        r = DepVersionDriftResult()
        assert r.detector_name == "dep_version_drift"
        assert r.mismatched_packages == []
        assert r.missing_from_requirements == []
        assert r.extra_in_requirements == []

    def test_custom_fields(self):
        r = DepVersionDriftResult(
            mismatched_packages=[{"pkg": "numpy", "expected": "1.24", "actual": "1.25"}],
            missing_from_requirements=["scipy"],
            extra_in_requirements=["pandas"],
        )
        assert len(r.mismatched_packages) == 1
        assert "scipy" in r.missing_from_requirements


class TestSecurityPolicyDriftResultInstantiation:
    def test_default_fields(self):
        r = SecurityPolicyDriftResult()
        assert r.detector_name == "security_policy_drift"
        assert r.input_sanitization_gaps == []
        assert r.auth_middleware_gaps == []
        assert r.secrets_found == []

    def test_custom_fields(self):
        r = SecurityPolicyDriftResult(
            input_sanitization_gaps=["api/routes.py"],
            auth_middleware_gaps=["api/admin.py"],
            secrets_found=["api_key=sk-xxx"],
        )
        assert len(r.input_sanitization_gaps) == 1
        assert len(r.auth_middleware_gaps) == 1
        assert len(r.secrets_found) == 1


class TestDocCodeCoevolutionResultInstantiation:
    def test_default_fields(self):
        r = DocCodeCoevolutionResult()
        assert r.detector_name == "doc_code_coevolution"
        assert r.code_newer_violations == []
        assert r.interface_drifts == []

    def test_custom_fields(self):
        r = DocCodeCoevolutionResult(
            code_newer_violations=["src/module.py"],
            interface_drifts=[{"func": "process", "blueprint": "yes", "code": "no"}],
        )
        assert len(r.code_newer_violations) == 1
        assert len(r.interface_drifts) == 1


class TestCovDriftResultInstantiation:
    def test_default_fields(self):
        r = CovDriftResult()
        assert r.detector_name == "test_coverage_drift"
        assert r.module_coverage_ratio == {}
        assert r.degradation_warnings == []

    def test_custom_fields(self):
        r = CovDriftResult(
            module_coverage_ratio={"zephyr.orchestrator.core": 0.45},
            degradation_warnings=["zephyr.orchestrator.core below 30%"],
        )
        assert r.module_coverage_ratio["zephyr.orchestrator.core"] == 0.45
        assert len(r.degradation_warnings) == 1


class TestKnowledgeGraphSyncResultInstantiation:
    def test_default_fields(self):
        r = KnowledgeGraphSyncResult()
        assert r.detector_name == "knowledge_graph_sync"
        assert r.entities_created == 0
        assert r.relations_created == 0
        assert r.orphans_found == 0

    def test_custom_fields(self):
        r = KnowledgeGraphSyncResult(
            entities_created=5,
            relations_created=3,
            orphans_found=1,
        )
        assert r.entities_created == 5
        assert r.relations_created == 3
        assert r.orphans_found == 1


class TestDetectDbSchemaDriftEmpty:
    def test_empty_project_returns_no_events(self, tmp_path):
        events = detect_db_schema_drift(str(tmp_path))
        assert events == []


class TestDetectDepVersionDriftEmpty:
    def test_empty_project_returns_no_events(self, tmp_path):
        events = detect_dep_version_drift(str(tmp_path))
        assert events == []


class TestDetectSecurityPolicyDriftEmpty:
    def test_empty_project_returns_no_events(self, tmp_path):
        events = detect_security_policy_drift(str(tmp_path))
        assert events == []


class TestDetectDocCodeCoevolutionEmpty:
    def test_empty_project_returns_no_events(self, tmp_path):
        events = detect_doc_code_coevolution(str(tmp_path))
        assert events == []


class TestDetectTestCoverageDriftEmpty:
    def test_no_src_dir_returns_no_events(self, tmp_path):
        events = detect_test_coverage_drift(str(tmp_path))
        assert events == []
