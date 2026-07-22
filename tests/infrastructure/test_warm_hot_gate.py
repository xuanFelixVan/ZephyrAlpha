# [A_test] module_id: MOD-GOV_warm_hot_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §warm_hot_gate
# [MODULE] tests.test_warm_hot_gate
# [INVARIANTS] WarmHotGate.check必须返回GateCheckResult; BLOCKING问题必须导致BLOCKED状态
# [MODIFY-GUARD] 仅当warm_hot_gate公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_warm_hot_gate.py -q
# [TTL] task_bound

from zephyr.infrastructure.warm_hot_gate import (
    GateCheckResult,
    WarmHotGate,
    WarmHotStatus,
)


class TestWarmHotStatus:
    def test_values(self):
        assert WarmHotStatus.PASSED.value == "passed"
        assert WarmHotStatus.BLOCKED.value == "blocked"
        assert WarmHotStatus.REQUIRES_APPROVAL.value == "requires_approval"
        assert WarmHotStatus.SKIPPED.value == "skipped"


class TestGateCheckResult:
    def test_default_passed(self):
        result = GateCheckResult(status=WarmHotStatus.PASSED)
        assert result.blocked is False
        assert result.requires_approval is False

    def test_blocked_status(self):
        result = GateCheckResult(status=WarmHotStatus.BLOCKED)
        assert result.blocked is True
        assert result.requires_approval is True

    def test_requires_approval_status(self):
        result = GateCheckResult(status=WarmHotStatus.REQUIRES_APPROVAL)
        assert result.blocked is False
        assert result.requires_approval is True


class TestWarmHotGate:
    def test_instantiation(self):
        gate = WarmHotGate()
        assert gate is not None

    def test_check_passes_with_empty_context(self):
        gate = WarmHotGate()
        result = gate.check({})
        assert result.status == WarmHotStatus.PASSED
        assert result.checks_performed >= 1

    def test_check_blocks_on_missing_dependency(self):
        gate = WarmHotGate()
        result = gate.check(
            {"required_modules": ["nonexistent_module_xyz_123"]},
            verify_contracts=False,
            verify_configs=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.BLOCKED
        assert len(result.blocking_issues) > 0

    def test_check_passes_with_available_dependency(self):
        gate = WarmHotGate()
        result = gate.check(
            {"required_modules": ["json"]},
            verify_contracts=False,
            verify_configs=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.PASSED

    def test_check_blocks_on_nonexistent_contract(self):
        gate = WarmHotGate()
        result = gate.check(
            {"contracts": ["/nonexistent/contract.yaml"]},
            verify_configs=False,
            verify_dependencies=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.BLOCKED

    def test_check_blocks_on_invalid_config(self):
        gate = WarmHotGate()
        result = gate.check(
            {"configs": ["/nonexistent/config.yaml"]},
            verify_contracts=False,
            verify_dependencies=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.BLOCKED

    def test_check_skip_verifications(self):
        gate = WarmHotGate()
        result = gate.check(
            {},
            verify_contracts=False,
            verify_configs=False,
            verify_dependencies=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.PASSED
        assert result.checks_performed == 0

    def test_check_not_require_all_with_non_blocking_failure(self):
        gate = WarmHotGate(require_all_passed=False)
        result = gate.check(
            {},
            verify_contracts=False,
            verify_configs=False,
            verify_dependencies=False,
            verify_resources=False,
        )
        assert result.status == WarmHotStatus.PASSED

    def test_checks_performed_counter(self):
        gate = WarmHotGate()
        gate.check({})
        gate.check({})
        assert gate.checks_performed == 2

    def test_check_disk_resources(self):
        gate = WarmHotGate()
        result = gate.check(
            {"min_disk_free_mb": 1},
            verify_contracts=False,
            verify_configs=False,
            verify_dependencies=False,
        )
        assert result.status == WarmHotStatus.PASSED
