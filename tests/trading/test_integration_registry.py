# [A_test] module_id: MOD-GOV_integration_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_integration_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.trading.integration_registry import IntegrationPoint, IntegrationRegistry, ValidationReport


class TestIntegrationPoint:
    def test_default_values(self) -> None:
        ip = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os:path")
        assert ip.point_id == "ip-1"
        assert ip.source_system == "AutoRuntimeCore"
        assert ip.target_system == "sys-a"
        assert ip.interface == "os:path"
        assert ip.protocol == "python_import"
        assert ip.sla == "best_effort"
        assert ip.status == "DISCONNECTED"

    def test_custom_values(self) -> None:
        ip = IntegrationPoint(
            point_id="ip-2",
            source_system="CustomSource",
            target_system="sys-b",
            interface="jsonpath.core:handler",
            protocol="http",
            sla="guaranteed",
            status="CONNECTED",
        )
        assert ip.source_system == "CustomSource"
        assert ip.protocol == "http"
        assert ip.sla == "guaranteed"
        assert ip.status == "CONNECTED"


class TestValidationReport:
    def test_default_values(self) -> None:
        vr = ValidationReport()
        assert vr.total == 0
        assert vr.connected == 0
        assert vr.degraded == 0
        assert vr.disconnected == 0
        assert vr.details == []


class TestIntegrationRegistryInit:
    def test_init_empty(self) -> None:
        reg = IntegrationRegistry()
        assert reg.points == {}


class TestRegister:
    def test_register_single(self) -> None:
        reg = IntegrationRegistry()
        ip = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os")
        reg.register(ip)
        assert "ip-1" in reg.points

    def test_register_overwrites(self) -> None:
        reg = IntegrationRegistry()
        ip1 = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os", status="DISCONNECTED")
        ip2 = IntegrationPoint(point_id="ip-1", target_system="sys-b", interface="os", status="CONNECTED")
        reg.register(ip1)
        reg.register(ip2)
        assert reg.points["ip-1"].target_system == "sys-b"


class TestValidateAll:
    def test_validate_empty(self) -> None:
        reg = IntegrationRegistry()
        report = reg.validate_all()
        assert report.total == 0
        assert report.connected == 0

    def test_validate_connected(self) -> None:
        reg = IntegrationRegistry()
        ip = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os")
        reg.register(ip)
        report = reg.validate_all()
        assert report.total == 1
        assert report.connected == 1
        assert ip.status == "CONNECTED"

    def test_validate_disconnected(self) -> None:
        reg = IntegrationRegistry()
        ip = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="nonexistent_module_xyz")
        reg.register(ip)
        report = reg.validate_all()
        assert report.disconnected == 1
        assert ip.status == "DISCONNECTED"
        assert len(report.details) == 1

    def test_validate_mixed(self) -> None:
        reg = IntegrationRegistry()
        ip_ok = IntegrationPoint(point_id="ip-ok", target_system="sys-a", interface="os")
        ip_bad = IntegrationPoint(point_id="ip-bad", target_system="sys-b", interface="nonexistent_xyz")
        reg.register(ip_ok)
        reg.register(ip_bad)
        report = reg.validate_all()
        assert report.total == 2
        assert report.connected == 1
        assert report.disconnected == 1


class TestStatusAll:
    def test_status_all_empty(self) -> None:
        reg = IntegrationRegistry()
        assert reg.status_all() == {}

    def test_status_all_returns_statuses(self) -> None:
        reg = IntegrationRegistry()
        ip1 = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os", status="CONNECTED")
        ip2 = IntegrationPoint(point_id="ip-2", target_system="sys-b", interface="xyz", status="DISCONNECTED")
        reg.register(ip1)
        reg.register(ip2)
        statuses = reg.status_all()
        assert statuses == {"ip-1": "CONNECTED", "ip-2": "DISCONNECTED"}


class TestListPoints:
    def test_list_points_empty(self) -> None:
        reg = IntegrationRegistry()
        assert reg.list_points() == []

    def test_list_points_returns_all(self) -> None:
        reg = IntegrationRegistry()
        ip1 = IntegrationPoint(point_id="ip-1", target_system="sys-a", interface="os")
        ip2 = IntegrationPoint(point_id="ip-2", target_system="sys-b", interface="json")
        reg.register(ip1)
        reg.register(ip2)
        points = reg.list_points()
        assert len(points) == 2
        ids = {p.point_id for p in points}
        assert ids == {"ip-1", "ip-2"}
