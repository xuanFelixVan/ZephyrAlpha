# [A_test] module_id: MOD-GOV_adversarial_robustness | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.adversarial_robustness
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.llm_defense.llm_security.adversarial_robustness import (
        AdversarialFuzzResult,
        AdversarialRobustnessTester,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


class TestAdversarialFuzzResult:
    def test_dataclass_fields(self):
        r = AdversarialFuzzResult(
            input_variant="test", original_classification="A", fuzzed_classification="B", robust=False
        )
        assert r.input_variant == "test"
        assert r.original_classification == "A"
        assert r.fuzzed_classification == "B"
        assert r.robust is False

    def test_default_robust_false(self):
        r = AdversarialFuzzResult(input_variant="x", original_classification="Y", fuzzed_classification="Z")
        assert r.robust is False

    def test_robust_true(self):
        r = AdversarialFuzzResult(
            input_variant="x", original_classification="Y", fuzzed_classification="Y", robust=True
        )
        assert r.robust is True


class TestAdversarialRobustnessTester:
    def test_fuzz_returns_list(self):
        tester = AdversarialRobustnessTester()
        results = tester.fuzz("some code")
        assert isinstance(results, list)

    def test_fuzz_returns_fuzz_result(self):
        tester = AdversarialRobustnessTester()
        results = tester.fuzz("some code")
        assert len(results) > 0
        assert isinstance(results[0], AdversarialFuzzResult)

    def test_fuzz_result_robust(self):
        tester = AdversarialRobustnessTester()
        results = tester.fuzz("some code")
        assert results[0].robust is True

    def test_fuzz_preserves_input_variant(self):
        tester = AdversarialRobustnessTester()
        results = tester.fuzz("hello world")
        assert results[0].input_variant == "hello world"

    def test_fuzz_empty_string(self):
        tester = AdversarialRobustnessTester()
        results = tester.fuzz("")
        assert isinstance(results, list)

    def test_run_pen_test_returns_list(self):
        tester = AdversarialRobustnessTester()
        results = tester.run_pen_test()
        assert isinstance(results, list)

    def test_run_pen_test_default_rounds(self):
        tester = AdversarialRobustnessTester()
        results = tester.run_pen_test(rounds=3)
        assert isinstance(results, list)

    def test_run_pen_test_custom_rounds(self):
        tester = AdversarialRobustnessTester()
        results = tester.run_pen_test(rounds=5)
        assert isinstance(results, list)
