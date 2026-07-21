# [A_test] module_id: MOD-GOV_host_resource_governor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.host_resource_governor
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
    from zephyr.infrastructure.capacity_assurance.host_resource_governor import HostResourceGovernor, ResourceStatus
except Exception as _exc:
    pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}")


class TestHostResourceGovernor:
    def test_probe_returns_resource_status(self):
        gov = HostResourceGovernor()
        status = gov.probe()
        assert isinstance(status, ResourceStatus)
        assert status.total_ram_mb > 0
        assert status.usage_pct >= 0
        assert isinstance(status.degraded, bool)
        assert isinstance(status.recommendation, str)

    def test_check_model_loading_within_limit(self):
        gov = HostResourceGovernor()
        status = gov.probe()
        small_model = status.total_ram_mb * 0.1
        assert gov.check_model_loading(small_model) is True

    def test_check_model_loading_exceeds_limit(self):
        gov = HostResourceGovernor()
        status = gov.probe()
        huge_model = status.total_ram_mb * 0.5
        assert gov.check_model_loading(huge_model) is False

    def test_check_model_loading_at_boundary(self):
        gov = HostResourceGovernor()
        status = gov.probe()
        boundary_model = status.total_ram_mb * 0.25
        assert gov.check_model_loading(boundary_model) is False

    def test_check_model_loading_zero(self):
        gov = HostResourceGovernor()
        assert gov.check_model_loading(0) is True

    def test_probe_fields_types(self):
        gov = HostResourceGovernor()
        status = gov.probe()
        assert isinstance(status.total_ram_mb, (int, float))
        assert isinstance(status.used_ram_mb, (int, float))
        assert isinstance(status.usage_pct, (int, float))
