# [A_test] module_id: SRC-TST-1146 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_interactive_diagnosis
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.interactive_diagnosis
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_interactive_diagnosis.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.interactive_diagnosis import InteractiveDiagnosis


class TestInteractiveDiagnosisInstantiation:
    def test_default_instantiation(self):
        diag = InteractiveDiagnosis()
        assert diag.max_rounds == 5

    def test_custom_max_rounds(self):
        diag = InteractiveDiagnosis(max_rounds=10)
        assert diag.max_rounds == 10

    def test_is_dataclass(self):
        diag = InteractiveDiagnosis()
        assert hasattr(diag, "__dataclass_fields__")


class TestProbe:
    def test_probe_returns_string(self):
        diag = InteractiveDiagnosis()
        result = diag.probe("What is the root cause?")
        assert isinstance(result, str)

    def test_probe_empty_question(self):
        diag = InteractiveDiagnosis()
        result = diag.probe("")
        assert isinstance(result, str)

    def test_probe_default_returns_empty(self):
        diag = InteractiveDiagnosis()
        result = diag.probe("any question")
        assert result == ""

    def test_probe_with_various_questions(self):
        diag = InteractiveDiagnosis()
        result1 = diag.probe("Is the database down?")
        result2 = diag.probe("Are there network issues?")
        assert isinstance(result1, str)
        assert isinstance(result2, str)

    def test_probe_with_long_question(self):
        diag = InteractiveDiagnosis()
        long_q = "x" * 10000
        result = diag.probe(long_q)
        assert isinstance(result, str)

    def test_probe_with_special_characters(self):
        diag = InteractiveDiagnosis()
        result = diag.probe("What about <script>alert('xss')</script>?")
        assert isinstance(result, str)

    def test_probe_with_unicode(self):
        diag = InteractiveDiagnosis()
        result = diag.probe("根因是什么？")
        assert isinstance(result, str)
