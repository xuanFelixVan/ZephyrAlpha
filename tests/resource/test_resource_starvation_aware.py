# [A_test] module_id: SRC-TST-1456 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_resource_starvation_aware
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.resource_starvation_aware
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_resource_starvation_aware.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.resource_starvation_aware import (
    ResourceBudget,
    ResourceStarvationAware,
)


class TestResourceStarvationAwareInstantiation:
    def test_default_instantiation(self):
        rsa = ResourceStarvationAware()
        assert rsa.cpu_min_pct == 10.0
        assert rsa.mem_min_mb == 512.0
        assert rsa.disk_min_mb == 1024.0

    def test_custom_instantiation(self):
        rsa = ResourceStarvationAware(cpu_min_pct=20.0, mem_min_mb=1024.0)
        assert rsa.cpu_min_pct == 20.0
        assert rsa.mem_min_mb == 1024.0


class TestCanProceed:
    def test_sufficient_resources(self):
        rsa = ResourceStarvationAware()
        budget = ResourceBudget(cpu_available_pct=50.0, mem_available_mb=4096.0, disk_available_mb=50000.0)
        assert rsa.can_proceed(budget) is True

    def test_insufficient_cpu(self):
        rsa = ResourceStarvationAware()
        budget = ResourceBudget(cpu_available_pct=5.0, mem_available_mb=4096.0, disk_available_mb=50000.0)
        assert rsa.can_proceed(budget) is False

    def test_insufficient_memory(self):
        rsa = ResourceStarvationAware()
        budget = ResourceBudget(cpu_available_pct=50.0, mem_available_mb=100.0, disk_available_mb=50000.0)
        assert rsa.can_proceed(budget) is False

    def test_insufficient_disk(self):
        rsa = ResourceStarvationAware()
        budget = ResourceBudget(cpu_available_pct=50.0, mem_available_mb=4096.0, disk_available_mb=100.0)
        assert rsa.can_proceed(budget) is False

    def test_exact_minimum(self):
        rsa = ResourceStarvationAware(cpu_min_pct=10.0, mem_min_mb=512.0, disk_min_mb=1024.0)
        budget = ResourceBudget(cpu_available_pct=10.0, mem_available_mb=512.0, disk_available_mb=1024.0)
        assert rsa.can_proceed(budget) is True

    def test_zero_resources(self):
        rsa = ResourceStarvationAware()
        budget = ResourceBudget(cpu_available_pct=0.0, mem_available_mb=0.0, disk_available_mb=0.0)
        assert rsa.can_proceed(budget) is False


class TestResourceBudget:
    def test_budget_defaults(self):
        budget = ResourceBudget()
        assert budget.cpu_available_pct == 100.0
        assert budget.mem_available_mb == 8192.0
        assert budget.disk_available_mb == 102400.0
