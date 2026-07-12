# [A_test] module_id: SRC-TST-0748 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_diagnosis_kpi
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis_kpi
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_diagnosis_kpi.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis_kpi import DiagnosisKPI


class TestDiagnosisKPIInstantiation:
    def test_default_values(self):
        kpi = DiagnosisKPI()
        assert kpi.total == 0
        assert kpi.effective == 0

    def test_custom_values(self):
        kpi = DiagnosisKPI(total=50, effective=30)
        assert kpi.total == 50
        assert kpi.effective == 30


class TestEffectivenessRate:
    def test_zero_total_returns_zero(self):
        kpi = DiagnosisKPI(total=0, effective=0)
        assert kpi.effectiveness_rate == 0.0

    def test_full_effectiveness(self):
        kpi = DiagnosisKPI(total=10, effective=10)
        assert kpi.effectiveness_rate == 1.0

    def test_partial_effectiveness(self):
        kpi = DiagnosisKPI(total=10, effective=5)
        assert kpi.effectiveness_rate == 0.5

    def test_no_effective_diagnoses(self):
        kpi = DiagnosisKPI(total=10, effective=0)
        assert kpi.effectiveness_rate == 0.0

    def test_effectiveness_rate_between_zero_and_one(self):
        kpi = DiagnosisKPI(total=7, effective=3)
        assert 0.0 <= kpi.effectiveness_rate <= 1.0

    def test_single_total_single_effective(self):
        kpi = DiagnosisKPI(total=1, effective=1)
        assert kpi.effectiveness_rate == 1.0

    def test_effective_exceeds_total(self):
        kpi = DiagnosisKPI(total=5, effective=10)
        assert kpi.effectiveness_rate == 2.0

    def test_large_numbers(self):
        kpi = DiagnosisKPI(total=10000, effective=9500)
        assert abs(kpi.effectiveness_rate - 0.95) < 0.001


class TestDiagnosisKPIMutation:
    def test_increment_total(self):
        kpi = DiagnosisKPI()
        kpi.total += 1
        assert kpi.total == 1

    def test_increment_effective(self):
        kpi = DiagnosisKPI()
        kpi.effective += 1
        assert kpi.effective == 1

    def test_rate_after_increment(self):
        kpi = DiagnosisKPI()
        kpi.total = 4
        kpi.effective = 3
        assert kpi.effectiveness_rate == 0.75
