# [A_test] module_id: MOD-GOV_pipeline_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_pipeline_models
# [INVARIANTS] PipelineDAG.resolve_execution_order must detect cycles; ModuleInput.validate must return bool
# [MODIFY-GUARD] only when zephyr.infrastructure.pipeline.models public API changes
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import failure -> skip; validation error -> fail
# [TESTS] pytest tests/test_pipeline_models.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.infrastructure.pipeline.models import (
    A_DAG,
    B_DAG,
    ArtifactType,
    CircuitBreakerState,
    CostRecord,
    DeadLetterEntry,
    EmergencyFallbackPlan,
    ExecutionMode,
    GenericModuleOutput,
    M1ParseOutput,
    M3GenerateOutput,
    M6DiffOutput,
    M7ReviewOutput,
    M8ComplianceOutput,
    M9RiskOutput,
    M10ReportOutput,
    M11GatingOutput,
    ModelConfidence,
    ModuleInput,
    ModuleResult,
    ModuleStatus,
    PipelineArtifact,
    PipelineArtifactManifest,
    PipelineDAG,
    PipelineLineageChain,
    PipelineLineageEntry,
    PipelineOrchestratorConfig,
    PipelineResult,
    PipelineStage,
    PipelineStatus,
    PreemptionRecord,
    StageContext,
    StageOnFailure,
    validate_module_output,
)


class TestPipelineStatus:
    def test_enum_values(self):
        assert PipelineStatus.PENDING.value == "pending"
        assert PipelineStatus.RUNNING.value == "running"
        assert PipelineStatus.SUCCESS.value == "success"
        assert PipelineStatus.PARTIAL_FAILURE.value == "partial_failure"
        assert PipelineStatus.FAILURE.value == "failure"
        assert PipelineStatus.CLAUDE_RESCUE.value == "claude_rescue"
        assert PipelineStatus.LOCKED.value == "locked"
        assert PipelineStatus.G6_BLOCKED.value == "g6_blocked"

    def test_is_str_enum(self):
        assert isinstance(PipelineStatus.PENDING, str)
        assert PipelineStatus.PENDING == "pending"


class TestModuleStatus:
    def test_enum_values(self):
        assert ModuleStatus.PENDING.value == "pending"
        assert ModuleStatus.RUNNING.value == "running"
        assert ModuleStatus.SUCCESS.value == "success"
        assert ModuleStatus.FAILURE.value == "failure"
        assert ModuleStatus.SKIPPED.value == "skipped"

    def test_is_str_enum(self):
        assert isinstance(ModuleStatus.SUCCESS, str)


class TestExecutionMode:
    def test_enum_values(self):
        assert ExecutionMode.TRAE.value == "trae"
        assert ExecutionMode.LOCAL.value == "local"
        assert ExecutionMode.API.value == "api"

    def test_is_str_enum(self):
        assert isinstance(ExecutionMode.TRAE, str)


class TestModuleResult:
    def test_default_construction(self):
        r = ModuleResult(module_id="M1", pipeline="A", model="deepseek")
        assert r.module_id == "M1"
        assert r.pipeline == "A"
        assert r.model == "deepseek"
        assert r.status == ModuleStatus.PENDING
        assert r.output == {}
        assert r.errors == []
        assert r.tokens_used == 0
        assert r.duration_ms == 0
        assert r.fallback_from is None
        assert r.blind_review_role is None
        assert r.confidence is None

    def test_full_construction(self):
        r = ModuleResult(
            module_id="M3",
            pipeline="A",
            model="deepseek",
            status=ModuleStatus.SUCCESS,
            output={"key": "val"},
            errors=["e1"],
            tokens_used=500,
            duration_ms=1200,
            fallback_from="glm",
            blind_review_role="generator",
        )
        assert r.status == ModuleStatus.SUCCESS
        assert r.tokens_used == 500
        assert r.fallback_from == "glm"
        assert r.blind_review_role == "generator"

    def test_invalid_module_id_pattern(self):
        with pytest.raises(Exception):
            ModuleResult(module_id="X99", pipeline="A", model="deepseek")

    def test_invalid_pipeline_pattern(self):
        with pytest.raises(Exception):
            ModuleResult(module_id="M1", pipeline="D", model="deepseek")

    def test_with_confidence(self):
        conf = ModelConfidence(score=0.85, source="logprob")
        r = ModuleResult(module_id="M3", pipeline="A", model="deepseek", confidence=conf)
        assert r.confidence.score == 0.85


class TestPipelineResult:
    def test_default_construction(self):
        r = PipelineResult(task_id="T-001", pipeline="A")
        assert r.task_id == "T-001"
        assert r.pipeline == "A"
        assert r.execution_mode == ExecutionMode.TRAE
        assert r.overall_status == PipelineStatus.PENDING
        assert r.modules_executed == []
        assert r.needs_claude_rescue is False
        assert r.is_dry_run is False

    def test_with_modules(self):
        m = ModuleResult(module_id="M1", pipeline="A", model="deepseek", status=ModuleStatus.SUCCESS)
        r = PipelineResult(task_id="T-002", pipeline="A", modules_executed=[m], overall_status=PipelineStatus.SUCCESS)
        assert len(r.modules_executed) == 1
        assert r.overall_status == PipelineStatus.SUCCESS

    def test_with_cost_records(self):
        cr = CostRecord(model="deepseek", tokens_input=1000, tokens_output=500, cost_usd=0.01)
        r = PipelineResult(task_id="T-003", pipeline="A", cost_records=[cr], cost_total_usd=0.01)
        assert r.cost_total_usd == 0.01
        assert len(r.cost_records) == 1


class TestPipelineDAG:
    def test_linear_dag(self):
        dag = PipelineDAG(
            dag_id="test-linear",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
                PipelineStage(stage_id="s2", module_id="M2", depends_on=["s1"]),
                PipelineStage(stage_id="s3", module_id="M3", depends_on=["s2"]),
            ],
        )
        order = dag.resolve_execution_order()
        assert order == [["s1"], ["s2"], ["s3"]]

    def test_diamond_dag(self):
        dag = PipelineDAG(
            dag_id="test-diamond",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
                PipelineStage(stage_id="s2", module_id="M2", depends_on=["s1"]),
                PipelineStage(stage_id="s3", module_id="M3", depends_on=["s1"]),
                PipelineStage(stage_id="s4", module_id="M4", depends_on=["s2", "s3"]),
            ],
        )
        order = dag.resolve_execution_order()
        assert order[0] == ["s1"]
        assert sorted(order[1]) == ["s2", "s3"]
        assert order[2] == ["s4"]

    def test_cycle_detection(self):
        dag = PipelineDAG(
            dag_id="test-cycle",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=["s2"]),
                PipelineStage(stage_id="s2", module_id="M2", depends_on=["s1"]),
            ],
        )
        with pytest.raises(ValueError, match="cycle detected"):
            dag.resolve_execution_order()

    def test_unknown_dependency_rejected(self):
        with pytest.raises(Exception):
            PipelineDAG(
                dag_id="test-bad-dep",
                stages=[
                    PipelineStage(stage_id="s1", module_id="M1", depends_on=["nonexistent"]),
                ],
            )

    def test_resolve_entry_stages_auto(self):
        dag = PipelineDAG(
            dag_id="test-entry",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
                PipelineStage(stage_id="s2", module_id="M2", depends_on=["s1"]),
            ],
        )
        assert dag.resolve_entry_stages() == ["s1"]

    def test_resolve_entry_stages_explicit(self):
        dag = PipelineDAG(
            dag_id="test-entry-explicit",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
                PipelineStage(stage_id="s2", module_id="M2", depends_on=["s1"]),
            ],
            entry_stages=["s1"],
        )
        assert dag.resolve_entry_stages() == ["s1"]

    def test_get_stage_found(self):
        dag = PipelineDAG(
            dag_id="test-get",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
            ],
        )
        s = dag.get_stage("s1")
        assert s is not None
        assert s.module_id == "M1"

    def test_get_stage_not_found(self):
        dag = PipelineDAG(
            dag_id="test-get-miss",
            stages=[
                PipelineStage(stage_id="s1", module_id="M1", depends_on=[]),
            ],
        )
        assert dag.get_stage("nonexistent") is None

    def test_a_dag_execution_order(self):
        order = A_DAG.resolve_execution_order()
        assert len(order) == 5
        assert order[0] == ["parse"]

    def test_b_dag_execution_order(self):
        order = B_DAG.resolve_execution_order()
        assert len(order) >= 4
        assert order[0] == ["diff"]


class TestStageContext:
    def test_evaluate_skip_true(self):
        dag = PipelineDAG(
            dag_id="test-ctx",
            stages=[PipelineStage(stage_id="s1", module_id="M1", depends_on=[])],
        )
        ctx = StageContext(dag=dag, metadata={"skip": True})
        assert ctx.evaluate_skip("ctx.metadata.get('skip', False)") is True

    def test_evaluate_skip_false(self):
        dag = PipelineDAG(
            dag_id="test-ctx2",
            stages=[PipelineStage(stage_id="s1", module_id="M1", depends_on=[])],
        )
        ctx = StageContext(dag=dag, metadata={"skip": False})
        assert ctx.evaluate_skip("ctx.metadata.get('skip', False)") is False

    def test_evaluate_skip_invalid_expression(self):
        dag = PipelineDAG(
            dag_id="test-ctx3",
            stages=[PipelineStage(stage_id="s1", module_id="M1", depends_on=[])],
        )
        ctx = StageContext(dag=dag)
        assert ctx.evaluate_skip("invalid$$$expr") is False

    def test_evaluate_skip_empty_condition(self):
        dag = PipelineDAG(
            dag_id="test-ctx4",
            stages=[PipelineStage(stage_id="s1", module_id="M1", depends_on=[])],
        )
        ctx = StageContext(dag=dag)
        assert ctx.evaluate_skip("") is False

    def test_aborted_flag(self):
        dag = PipelineDAG(
            dag_id="test-ctx5",
            stages=[PipelineStage(stage_id="s1", module_id="M1", depends_on=[])],
        )
        ctx = StageContext(dag=dag, aborted=True)
        assert ctx.aborted is True


class TestPipelineArtifactManifest:
    def _make_manifest(self):
        a1 = PipelineArtifact(
            artifact_key="M3_code",
            artifact_type=ArtifactType.CODE,
            produced_by="M3",
            content="print('hi')",
        )
        a2 = PipelineArtifact(
            artifact_key="M7_report",
            artifact_type=ArtifactType.AUDIT_REPORT,
            produced_by="M7",
            content="ok",
        )
        a3 = PipelineArtifact(
            artifact_key="M3_doc",
            artifact_type=ArtifactType.DOC,
            produced_by="M3",
            content="readme",
        )
        return PipelineArtifactManifest(
            run_id="R-001",
            pipeline_id="A_DAG",
            task_id="T-001",
            artifacts=[a1, a2, a3],
        )

    def test_get_found(self):
        m = self._make_manifest()
        a = m.get("M3_code")
        assert a is not None
        assert a.produced_by == "M3"

    def test_get_not_found(self):
        m = self._make_manifest()
        assert m.get("nonexistent") is None

    def test_by_module(self):
        m = self._make_manifest()
        m3_artifacts = m.by_module("M3")
        assert len(m3_artifacts) == 2

    def test_by_module_empty(self):
        m = self._make_manifest()
        assert m.by_module("M99") == []

    def test_by_type(self):
        m = self._make_manifest()
        code_artifacts = m.by_type(ArtifactType.CODE)
        assert len(code_artifacts) == 1
        assert code_artifacts[0].artifact_key == "M3_code"

    def test_by_type_empty(self):
        m = self._make_manifest()
        assert m.by_type(ArtifactType.DIFF) == []

    def test_empty_manifest(self):
        m = PipelineArtifactManifest(run_id="R-002")
        assert m.get("any") is None
        assert m.by_module("M1") == []
        assert m.by_type(ArtifactType.CODE) == []


class TestPipelineLineageChain:
    def test_add_entry_and_verify(self):
        chain = PipelineLineageChain(run_id="R-001")
        e1 = PipelineLineageEntry(
            module_id="M1",
            pipeline="A",
            produced_artifact_keys=["M1_plan"],
        )
        h1 = chain.add_entry(e1)
        assert h1 != ""
        assert len(chain.entries) == 1
        assert chain.entries[0].lineage_hash == h1

    def test_chain_integrity(self):
        chain = PipelineLineageChain(run_id="R-002")
        e1 = PipelineLineageEntry(module_id="M1", pipeline="A", produced_artifact_keys=["M1_plan"])
        e2 = PipelineLineageEntry(module_id="M2", pipeline="A", produced_artifact_keys=["M2_ctx"])
        chain.add_entry(e1)
        chain.add_entry(e2)
        assert chain.verify_integrity() is True

    def test_tampered_integrity_fails(self):
        chain = PipelineLineageChain(run_id="R-003")
        e1 = PipelineLineageEntry(module_id="M1", pipeline="A", produced_artifact_keys=["M1_plan"])
        chain.add_entry(e1)
        chain.entries[0].lineage_hash = "tampered_hash"
        assert chain.verify_integrity() is False

    def test_empty_chain_integrity(self):
        chain = PipelineLineageChain(run_id="R-004")
        assert chain.verify_integrity() is True

    def test_entry_without_hash_passes(self):
        chain = PipelineLineageChain(run_id="R-005")
        e1 = PipelineLineageEntry(module_id="M1", pipeline="A", produced_artifact_keys=["M1_plan"], lineage_hash="")
        chain.entries.append(e1)
        assert chain.verify_integrity() is True


class TestValidateModuleOutput:
    def test_m1_valid(self):
        result = validate_module_output("M1", {"task_id": "T-001", "estimated_steps": 5})
        assert result.get("_schema_validated") is True

    def test_m1_invalid(self):
        result = validate_module_output("M1", {"task_id": "T-001"})
        assert result.get("_schema_validated") is False

    def test_m3_valid(self):
        result = validate_module_output("M3", {"module_id": "M3", "generated_files": ["a.py"]})
        assert result.get("_schema_validated") is True

    def test_unknown_module_uses_generic(self):
        result = validate_module_output("M2", {"module_id": "M2", "summary": "test"})
        assert result.get("_schema_validated") is True

    def test_m6_valid(self):
        result = validate_module_output("M6", {"has_changes": True, "changed_files": ["x.py"]})
        assert result.get("_schema_validated") is True

    def test_m11_valid(self):
        result = validate_module_output("M11", {"module_id": "M11", "g5_passed": True, "g6_passed": False})
        assert result.get("_schema_validated") is True


class TestModuleInput:
    def test_validate_satisfied(self):
        a1 = PipelineArtifact(
            artifact_key="M3_code",
            artifact_type=ArtifactType.CODE,
            produced_by="M3",
        )
        mi = ModuleInput(module_id="M6", consumes=["M3_code"], previous_artifacts=[a1])
        assert mi.validate() is True

    def test_validate_unsatisfied(self):
        a1 = PipelineArtifact(
            artifact_key="M3_code",
            artifact_type=ArtifactType.CODE,
            produced_by="M3",
        )
        mi = ModuleInput(module_id="M6", consumes=["M3_code", "M3_doc"], previous_artifacts=[a1])
        assert mi.validate() is False

    def test_validate_no_consumes(self):
        mi = ModuleInput(module_id="M1", consumes=[])
        assert mi.validate() is True

    def test_validate_empty_previous_artifacts_with_consumes(self):
        mi = ModuleInput(module_id="M6", consumes=["M3_code"], previous_artifacts=[])
        assert mi.validate() is False


class TestCostRecord:
    def test_default_construction(self):
        cr = CostRecord(model="deepseek")
        assert cr.model == "deepseek"
        assert cr.tokens_input == 0
        assert cr.tokens_output == 0
        assert cr.cost_usd == 0.0
        assert cr.estimated is True

    def test_full_construction(self):
        cr = CostRecord(model="claude", tokens_input=2000, tokens_output=1000, cost_usd=0.05, estimated=False)
        assert cr.cost_usd == 0.05
        assert cr.estimated is False


class TestDeadLetterEntry:
    def test_default_construction(self):
        e = DeadLetterEntry(task_id="T-001")
        assert e.task_id == "T-001"
        assert e.failure_reason == ""
        assert e.retry_count == 0
        assert e.last_error == ""

    def test_full_construction(self):
        e = DeadLetterEntry(task_id="T-002", failure_reason="timeout", retry_count=3, last_error="503")
        assert e.failure_reason == "timeout"
        assert e.retry_count == 3


class TestEmergencyFallbackPlan:
    def test_default_construction(self):
        p = EmergencyFallbackPlan()
        assert p.activated is False
        assert p.all_models_failed == []
        assert p.recommended_action == "WAIT_AND_RETRY"
        assert p.wait_before_retry_s == 300

    def test_activated(self):
        p = EmergencyFallbackPlan(
            activated=True, all_models_failed=["deepseek", "glm", "claude"], recommended_action="ESCALATE_TO_HUMAN"
        )
        assert p.activated is True
        assert len(p.all_models_failed) == 3


class TestPreemptionRecord:
    def test_construction(self):
        r = PreemptionRecord(preempted_task_id="T-001", preempted_by_task_id="T-002", preempted_priority="P0")
        assert r.preempted_task_id == "T-001"
        assert r.preempted_by_task_id == "T-002"
        assert r.resumed_at is None

    def test_with_state_snapshot(self):
        r = PreemptionRecord(
            preempted_task_id="T-001",
            preempted_by_task_id="T-002",
            preempted_priority="P0",
            state_snapshot={"progress": 0.5},
        )
        assert r.state_snapshot["progress"] == 0.5


class TestPipelineOrchestratorConfig:
    def test_default_config(self):
        cfg = PipelineOrchestratorConfig()
        assert cfg.max_retries == 3
        assert cfg.claude_rescue_threshold == 3
        assert cfg.glm_rejection_threshold == 2
        assert cfg.default_timeout_s == 300
        assert cfg.circuit_breaker_enabled is True
        assert cfg.g6_enabled is True
        assert cfg.cache_enabled is False

    def test_custom_config(self):
        cfg = PipelineOrchestratorConfig(max_retries=5, cache_enabled=True, cache_ttl_s=7200)
        assert cfg.max_retries == 5
        assert cfg.cache_enabled is True
        assert cfg.cache_ttl_s == 7200

    def test_model_versions(self):
        cfg = PipelineOrchestratorConfig()
        assert len(cfg.model_versions) == 3
        names = {mv.model_name for mv in cfg.model_versions}
        assert "deepseek" in names
        assert "glm" in names
        assert "claude" in names

    def test_rate_limit_defaults(self):
        cfg = PipelineOrchestratorConfig()
        assert "deepseek" in cfg.rate_limit_per_model
        assert cfg.rate_limit_per_model["deepseek"] == 10.0


class TestM1ParseOutput:
    def test_valid(self):
        o = M1ParseOutput(task_id="T-001", estimated_steps=3)
        assert o.task_id == "T-001"
        assert o.estimated_steps == 3

    def test_estimated_steps_bounds(self):
        with pytest.raises(Exception):
            M1ParseOutput(task_id="T-001", estimated_steps=0)
        with pytest.raises(Exception):
            M1ParseOutput(task_id="T-001", estimated_steps=51)


class TestM3GenerateOutput:
    def test_default(self):
        o = M3GenerateOutput()
        assert o.module_id == "M3"
        assert o.generated_files == []
        assert o.verdict == "ok"

    def test_with_files(self):
        o = M3GenerateOutput(generated_files=["a.py", "b.py"], diffs=["diff1"], tokens_used=1500)
        assert len(o.generated_files) == 2
        assert o.tokens_used == 1500


class TestM6DiffOutput:
    def test_default(self):
        o = M6DiffOutput()
        assert o.has_changes is False
        assert o.changed_files == []

    def test_with_changes(self):
        o = M6DiffOutput(has_changes=True, changed_files=["x.py"], added_lines=10, removed_lines=5)
        assert o.has_changes is True
        assert o.added_lines == 10


class TestM7ReviewOutput:
    def test_default(self):
        o = M7ReviewOutput()
        assert o.module_id == "M7"
        assert o.issues_found == 0
        assert o.verdict == "ok"

    def test_with_issues(self):
        o = M7ReviewOutput(reviewed_files=["a.py"], issues_found=2, verdict="needs_fix")
        assert o.issues_found == 2


class TestM8ComplianceOutput:
    def test_default(self):
        o = M8ComplianceOutput()
        assert o.module_id == "M8"
        assert o.violations == []

    def test_with_violations(self):
        o = M8ComplianceOutput(standards_checked=["PS-STD-001"], violations=["V-001"], verdict="fail")
        assert len(o.violations) == 1


class TestM9RiskOutput:
    def test_default(self):
        o = M9RiskOutput()
        assert o.module_id == "M9"
        assert o.risk_level == "low"

    def test_high_risk(self):
        o = M9RiskOutput(risk_level="high", owasp_items=["OWASP-01"])
        assert o.risk_level == "high"


class TestM10ReportOutput:
    def test_default(self):
        o = M10ReportOutput()
        assert o.module_id == "M10"
        assert o.finding_count == 0

    def test_with_findings(self):
        o = M10ReportOutput(finding_count=3, findings=[{"id": "F-001"}])
        assert o.finding_count == 3


class TestM11GatingOutput:
    def test_default(self):
        o = M11GatingOutput()
        assert o.module_id == "M11"
        assert o.g5_passed is False
        assert o.g6_passed is False
        assert o.verdict == "blocked"

    def test_passed(self):
        o = M11GatingOutput(g5_passed=True, g6_passed=True, verdict="passed")
        assert o.verdict == "passed"


class TestGenericModuleOutput:
    def test_construction(self):
        o = GenericModuleOutput(module_id="M2", summary="done", tokens_used=100)
        assert o.module_id == "M2"
        assert o.simulated is False
        assert o.dry_run is False


class TestCircuitBreakerState:
    def test_enum_values(self):
        assert CircuitBreakerState.CLOSED.value == "closed"
        assert CircuitBreakerState.OPEN.value == "open"
        assert CircuitBreakerState.HALF_OPEN.value == "half_open"


class TestModelConfidence:
    def test_default(self):
        c = ModelConfidence()
        assert c.score == 0.0
        assert c.source == ""

    def test_score_bounds(self):
        c = ModelConfidence(score=1.0)
        assert c.score == 1.0
        with pytest.raises(Exception):
            ModelConfidence(score=1.5)
        with pytest.raises(Exception):
            ModelConfidence(score=-0.1)


class TestStageOnFailure:
    def test_enum_values(self):
        assert StageOnFailure.ABORT.value == "abort"
        assert StageOnFailure.SKIP.value == "skip"
        assert StageOnFailure.RETRY.value == "retry"
        assert StageOnFailure.CLAUDE_RESCUE.value == "claude_rescue"
