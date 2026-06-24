# [A_test] module_id: SRC-TST-1756 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_trace_capacity_injector
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_trace_capacity_injector.py

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.trace_capacity_injector", reason="trace_capacity_injector not available"
)
TraceCapacityInjector = mod.TraceCapacityInjector


class TestTraceCapacityInjector:
    def test_instantiation(self):
        tci = TraceCapacityInjector()
        assert tci._error_budget_tier == "L0"
        assert tci._module_count == 0
        assert tci._queue_depth == 0

    def test_set_state(self):
        tci = TraceCapacityInjector()
        tci.set_state("L3", 42, 7)
        assert tci._error_budget_tier == "L3"
        assert tci._module_count == 42
        assert tci._queue_depth == 7

    def test_inject_tracestate(self):
        tci = TraceCapacityInjector()
        tci.set_state("L2", 10, 5)
        result = tci.inject_tracestate()
        assert "zephyr=1" in result
        assert "cap_eb_tier:L2" in result
        assert "cap_mod_cnt:10" in result
        assert "cap_qd:5" in result

    def test_inject_tracestate_default(self):
        tci = TraceCapacityInjector()
        result = tci.inject_tracestate()
        assert "cap_eb_tier:L0" in result
        assert "cap_mod_cnt:0" in result

    def test_get_capacity_headers(self):
        tci = TraceCapacityInjector()
        tci.set_state("L1", 20, 3)
        headers = tci.get_capacity_headers()
        assert "tracestate" in headers
        assert "cap-error-budget-tier" in headers
        assert headers["cap-error-budget-tier"] == "L1"
        assert headers["cap-module-count"] == "20"
        assert headers["cap-queue-depth"] == "3"
