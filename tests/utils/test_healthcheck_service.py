# [A_test] module_id: MOD-GOV_healthcheck_service | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-392 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §

# [MODULE] tests.test_healthcheck_service

# [INVARIANTS] HealthcheckService must return HealthReport with 5 components from check_all; HealthStatus must have all 5 fields populated

# [MODIFY-GUARD] reflect source API changes only

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] all tests must pass exit 0

# [TESTS] python -m pytest tests/test_healthcheck_service.py -q
# [TTL] task_bound

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.lifecycle.healthcheck_service import HealthcheckService, HealthReport, HealthStatus

PROJECT_ROOT = REPO_ROOT  # alias 真源


class TestHealthStatus:
    def test_instantiation_all_fields(self):
        hs = HealthStatus(
            component="test-comp",
            healthy=True,
            latency_ms=1.23,
            message="ok",
            last_checked="2026-01-01T00:00:00+00:00",
        )
        assert hs.component == "test-comp"
        assert hs.healthy is True
        assert hs.latency_ms == 1.23
        assert hs.message == "ok"
        assert hs.last_checked == "2026-01-01T00:00:00+00:00"

    def test_instantiation_unhealthy(self):
        hs = HealthStatus(
            component="broken",
            healthy=False,
            latency_ms=0,
            message="fail",
            last_checked="",
        )
        assert hs.healthy is False
        assert hs.message == "fail"


class TestHealthReport:
    def test_instantiation_with_defaults(self):
        hs = HealthStatus(component="c", healthy=True, latency_ms=0, message="m", last_checked="t")
        report = HealthReport(
            timestamp_utc="2026-01-01T00:00:00+00:00",
            overall_healthy=True,
            components=[hs],
            uptime_seconds=42.0,
        )
        assert report.version == "0.6.0"
        assert report.overall_healthy is True
        assert len(report.components) == 1

    def test_instantiation_explicit_version(self):
        report = HealthReport(
            timestamp_utc="t",
            overall_healthy=False,
            components=[],
            uptime_seconds=0,
            version="1.0.0",
        )
        assert report.version == "1.0.0"
        assert report.overall_healthy is False
        assert report.components == []


class TestHealthcheckServiceInit:
    def test_default_project_root_is_cwd(self):
        svc = HealthcheckService()
        assert svc.project_root == Path.cwd()

    def test_explicit_project_root(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        assert svc.project_root == PROJECT_ROOT

    def test_none_project_root_falls_back_to_cwd(self):
        svc = HealthcheckService(project_root=None)
        assert svc.project_root == Path.cwd()

    def test_start_time_recorded(self):
        before = time.time()
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        after = time.time()
        assert before <= svc.start_time <= after


class TestHealthcheckServiceCheckAll:
    def test_returns_health_report(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        assert isinstance(report, HealthReport)

    def test_has_five_components(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        assert len(report.components) == 5

    def test_component_names(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        names = [c.component for c in report.components]
        assert names == ["git", "python", "disk", "network", "filesystem"]

    def test_uptime_positive(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        assert report.uptime_seconds >= 0

    def test_timestamp_not_empty(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        assert len(report.timestamp_utc) > 0

    def test_overall_healthy_true_when_all_healthy(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        if all(c.healthy for c in report.components):
            assert report.overall_healthy is True
        else:
            assert report.overall_healthy is False


class TestHealthcheckServiceCheckGit:
    def test_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_git()
        assert isinstance(status, HealthStatus)

    def test_component_name_is_git(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_git()
        assert status.component == "git"

    def test_git_timeout_returns_unhealthy(self):
        import subprocess as sp

        svc = HealthcheckService(project_root=PROJECT_ROOT)
        with patch(
            "zephyr.shared.lifecycle.healthcheck_service.run_subprocess_hidden",
            side_effect=sp.TimeoutExpired(cmd="git", timeout=5),
        ):
            status = svc.check_git()
            assert status.healthy is False

    def test_git_not_found_returns_unhealthy(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        with patch("zephyr.shared.lifecycle.healthcheck_service.run_subprocess_hidden", side_effect=FileNotFoundError):
            status = svc.check_git()
            assert status.healthy is False


class TestHealthcheckServiceCheckDependencies:
    def test_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_dependencies()
        assert isinstance(status, HealthStatus)

    def test_component_name_is_dependencies(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_dependencies()
        assert status.component == "dependencies"

    def test_healthy_when_imports_succeed(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_dependencies()
        assert status.healthy is True
        assert "importable" in status.message.lower()

    def test_unhealthy_when_import_fails(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            status = svc.check_dependencies()
            assert status.healthy is False
            assert "import failed" in status.message


class TestHealthcheckServicePrivateChecks:
    def test_check_python_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_python()
        assert isinstance(status, HealthStatus)
        assert status.component == "python"

    def test_check_disk_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_disk()
        assert isinstance(status, HealthStatus)
        assert status.component == "disk"
        assert status.healthy is True

    def test_check_disk_unhealthy_on_oserror(self):
        svc = HealthcheckService(project_root=Path("/nonexistent/path/that/does/not/exist"))
        status = svc.check_disk()
        assert status.healthy is False

    def test_check_network_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_network()
        assert isinstance(status, HealthStatus)
        assert status.component == "network"
        assert status.healthy is True

    def test_check_file_system_returns_health_status(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        status = svc.check_file_system()
        assert isinstance(status, HealthStatus)
        assert status.component == "filesystem"

    def test_check_file_system_missing_files(self):
        svc = HealthcheckService(project_root=Path("/nonexistent"))
        status = svc.check_file_system()
        assert status.healthy is False
        assert "Missing" in status.message


class TestHealthcheckServiceBoundary:
    def test_latency_non_negative(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        for c in report.components:
            assert c.latency_ms >= 0

    def test_last_checked_iso_format(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        report = svc.check_all()
        for c in report.components:
            assert len(c.last_checked) > 0

    def test_python_not_found_returns_unhealthy(self):
        svc = HealthcheckService(project_root=PROJECT_ROOT)
        with patch("zephyr.shared.lifecycle.healthcheck_service.run_subprocess_hidden", side_effect=FileNotFoundError):
            status = svc.check_python()
            assert status.healthy is False
            assert status.message == "Python not found"
