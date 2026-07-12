# [A_test] module_id: SRC-TST-0747 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_diagnosis_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_diagnosis_engine.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis_engine import Diagnosis, DiagnosisEngine


class TestDiagnosisDataclass:
    def test_creation_with_all_fields(self):
        d = Diagnosis(
            diagnosis_id="abc123",
            root_cause="cpu_spike",
            confidence=0.85,
            evidence_chain=["metric=cpu", "z_score=3.5"],
        )
        assert d.diagnosis_id == "abc123"
        assert d.root_cause == "cpu_spike"
        assert d.confidence == 0.85
        assert d.evidence_chain == ["metric=cpu", "z_score=3.5"]

    def test_default_evidence_chain_is_empty(self):
        d = Diagnosis(diagnosis_id="x", root_cause="y", confidence=0.5)
        assert d.evidence_chain == []

    def test_evidence_chain_independent_across_instances(self):
        d1 = Diagnosis(diagnosis_id="a", root_cause="b", confidence=0.5)
        d2 = Diagnosis(diagnosis_id="c", root_cause="d", confidence=0.6)
        d1.evidence_chain.append("item")
        assert d2.evidence_chain == []


class TestDiagnosisEngineInstantiation:
    def test_default_instantiation(self):
        engine = DiagnosisEngine()
        assert engine is not None

    def test_is_dataclass(self):
        engine = DiagnosisEngine()
        assert hasattr(engine, "__dataclass_fields__")


class TestDiagnose:
    def test_returns_diagnosis_instance(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "cpu", "z_score": 3.0})
        assert isinstance(result, Diagnosis)

    def test_diagnosis_id_is_string(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "cpu", "z_score": 3.0})
        assert isinstance(result.diagnosis_id, str)
        assert len(result.diagnosis_id) > 0

    def test_root_cause_contains_metric_name(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "memory", "z_score": 2.5})
        assert "memory" in result.root_cause

    def test_root_cause_contains_z_score(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "cpu", "z_score": 4.2})
        assert "4.20" in result.root_cause

    def test_confidence_increases_with_z_score(self):
        engine = DiagnosisEngine()
        low = engine.diagnose("a", {"metric_name": "m", "z_score": 1.0})
        high = engine.diagnose("b", {"metric_name": "m", "z_score": 8.0})
        assert high.confidence > low.confidence

    def test_confidence_capped_at_095(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("a", {"metric_name": "m", "z_score": 100.0})
        assert result.confidence <= 0.95

    def test_evidence_chain_has_entries(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "cpu", "z_score": 3.0})
        assert len(result.evidence_chain) >= 1

    def test_missing_metric_name_defaults_to_unknown(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"z_score": 2.5})
        assert "unknown" in result.root_cause

    def test_missing_z_score_defaults(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {"metric_name": "cpu"})
        assert isinstance(result.confidence, float)

    def test_empty_evidence_dict(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("anom-1", {})
        assert isinstance(result, Diagnosis)
        assert "unknown" in result.root_cause

    def test_negative_z_score_abs_used(self):
        engine = DiagnosisEngine()
        result = engine.diagnose("a", {"metric_name": "m", "z_score": -5.0})
        assert "5.00" in result.root_cause

    def test_unique_diagnosis_ids(self):
        engine = DiagnosisEngine()
        r1 = engine.diagnose("a", {"metric_name": "m", "z_score": 2.0})
        r2 = engine.diagnose("b", {"metric_name": "m", "z_score": 2.0})
        assert r1.diagnosis_id != r2.diagnosis_id
