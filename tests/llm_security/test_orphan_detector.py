# [A_test] module_id: MOD-GOV_orphan_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §5.6
# [MODULE] tests.test_orphan_detector
# [INVARIANTS] must test all public classes and methods of orphan_detector
# [MODIFY-GUARD] orphan_detector.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_orphan_detector.py
# [TTL] task_bound

from unittest.mock import MagicMock

import pytest

from zephyr.security.access_control.orphan_judge.orphan_detector import OrphanDetector, OrphanReport
from zephyr.trading.module_onboarding_scanner import ModuleDiscovery, UnregisteredModule


def _make_discovery(package: str = "test_pkg", module_name: str = "test_mod") -> ModuleDiscovery:
    return ModuleDiscovery(
        module_path=f"zephyr.{package}.{module_name}",
        module_name=module_name,
        package=package,
    )


def _make_orphan(
    package: str = "test_pkg", module_name: str = "orphan_mod", priority: str = "P1"
) -> UnregisteredModule:
    return UnregisteredModule(
        discovery=_make_discovery(package=package, module_name=module_name),
        reason="new",
        priority=priority,
    )


class TestOrphanReport:
    def test_default_values(self):
        r = OrphanReport()
        assert r.total_modules == 0
        assert r.registered_modules == 0
        assert r.orphan_modules == 0
        assert r.orphan_rate == 1.0
        assert r.orphans_by_priority == {}
        assert r.orphans_by_package == {}
        assert r.top_priority_orphans == []
        assert r.goal_gap == 1.0

    def test_custom_values(self):
        orphan = _make_orphan()
        r = OrphanReport(
            total_modules=10,
            registered_modules=7,
            orphan_modules=3,
            orphan_rate=0.3,
            orphans_by_priority={"P0": 1, "P1": 2},
            orphans_by_package={"pkg_a": 3},
            top_priority_orphans=[orphan],
            goal_gap=0.7,
        )
        assert r.total_modules == 10
        assert r.registered_modules == 7
        assert r.orphan_modules == 3
        assert r.orphan_rate == 0.3
        assert r.orphans_by_priority == {"P0": 1, "P1": 2}
        assert r.orphans_by_package == {"pkg_a": 3}
        assert len(r.top_priority_orphans) == 1
        assert r.goal_gap == 0.7


class TestOrphanDetector:
    def _make_detector(self, orphans=None, all_modules=None, registered_count=0):
        scanner = MagicMock()
        scanner.diff_registered.return_value = orphans or []
        scanner.scan_filesystem.return_value = all_modules or []
        registry = MagicMock()
        registry.count.return_value = registered_count
        return OrphanDetector(scanner=scanner, registry=registry)

    def test_instantiation(self):
        detector = self._make_detector()
        assert detector.scanner is not None
        assert detector.registry is not None

    def test_find_orphans_empty(self):
        detector = self._make_detector(orphans=[])
        result = detector.find_orphans()
        assert result == []

    def test_find_orphans_with_items(self):
        orphans = [_make_orphan(priority="P0"), _make_orphan(priority="P1")]
        detector = self._make_detector(orphans=orphans)
        result = detector.find_orphans()
        assert len(result) == 2

    def test_compute_orphan_rate_no_orphans(self):
        disc = _make_discovery()
        detector = self._make_detector(orphans=[], all_modules=[disc], registered_count=1)
        rate = detector.compute_orphan_rate()
        assert rate == 0.0

    def test_compute_orphan_rate_all_orphans(self):
        orphans = [_make_orphan()]
        disc = _make_discovery()
        detector = self._make_detector(orphans=orphans, all_modules=[disc])
        rate = detector.compute_orphan_rate()
        assert rate == 1.0

    def test_compute_orphan_rate_partial(self):
        orphans = [_make_orphan(), _make_orphan()]
        discs = [_make_discovery(), _make_discovery(), _make_discovery(), _make_discovery()]
        detector = self._make_detector(orphans=orphans, all_modules=discs)
        rate = detector.compute_orphan_rate()
        assert rate == pytest.approx(0.5)

    def test_compute_orphan_rate_zero_modules(self):
        detector = self._make_detector(orphans=[], all_modules=[])
        rate = detector.compute_orphan_rate()
        assert rate == 0.0

    def test_prioritize_orphans_by_priority(self):
        p0 = _make_orphan(priority="P0")
        p1 = _make_orphan(priority="P1")
        p2 = _make_orphan(priority="P2")
        detector = self._make_detector()
        result = detector.prioritize_orphans([p2, p0, p1])
        assert result[0].priority == "P0"
        assert result[1].priority == "P1"
        assert result[2].priority == "P2"

    def test_prioritize_orphans_none_calls_find(self):
        orphans = [_make_orphan(priority="P0")]
        detector = self._make_detector(orphans=orphans)
        result = detector.prioritize_orphans(None)
        assert len(result) == 1

    def test_prioritize_orphans_unknown_priority(self):
        unknown = _make_orphan(priority="P99")
        detector = self._make_detector()
        result = detector.prioritize_orphans([unknown])
        assert len(result) == 1

    def test_prioritize_orphans_empty(self):
        detector = self._make_detector()
        result = detector.prioritize_orphans([])
        assert result == []

    def test_report_full(self):
        o1 = _make_orphan(package="pkg_a", priority="P0")
        o2 = _make_orphan(package="pkg_a", priority="P1")
        o3 = _make_orphan(package="pkg_b", priority="P1")
        discs = [_make_discovery() for _ in range(5)]
        detector = self._make_detector(orphans=[o1, o2, o3], all_modules=discs, registered_count=2)
        report = detector.report()
        assert report.total_modules == 5
        assert report.registered_modules == 2
        assert report.orphan_modules == 3
        assert report.orphan_rate == pytest.approx(0.6)
        assert report.orphans_by_priority == {"P0": 1, "P1": 2}
        assert report.orphans_by_package == {"pkg_a": 2, "pkg_b": 1}
        assert len(report.top_priority_orphans) == 3
        assert report.goal_gap == pytest.approx(0.4)

    def test_report_empty(self):
        detector = self._make_detector(orphans=[], all_modules=[], registered_count=0)
        report = detector.report()
        assert report.total_modules == 0
        assert report.orphan_modules == 0
        assert report.orphan_rate == 0.0
        assert report.goal_gap == 1.0

    def test_report_top_priority_orphans_capped_at_10(self):
        orphans = [_make_orphan(module_name=f"mod_{i}", priority="P0") for i in range(15)]
        discs = [_make_discovery() for _ in range(20)]
        detector = self._make_detector(orphans=orphans, all_modules=discs, registered_count=5)
        report = detector.report()
        assert len(report.top_priority_orphans) == 10

    def test_is_goal_met_true(self):
        disc = _make_discovery()
        detector = self._make_detector(orphans=[], all_modules=[disc], registered_count=1)
        assert detector.is_goal_met() is True

    def test_is_goal_met_false(self):
        orphans = [_make_orphan()]
        disc = _make_discovery()
        detector = self._make_detector(orphans=orphans, all_modules=[disc])
        assert detector.is_goal_met() is False
