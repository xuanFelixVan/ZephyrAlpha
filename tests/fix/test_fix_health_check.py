# [A_test] module_id: MOD-GOV_fix_health_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_health_check
# [INVARIANTS] 测试覆盖check/_check_db/_check_config;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.auto_fix_engine.fix_health_check import FixHealthCheck
from zephyr.infrastructure.auto_fix_engine.models import FixHealthReport


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_health.db")


@pytest.fixture
def health_check(tmp_db):
    return FixHealthCheck(db_path=tmp_db)


class TestFixHealthCheckInstantiation:
    def test_creates_instance_with_default_path(self):
        hc = FixHealthCheck()
        assert hc._db_path == "data/auto_fix/auto_fix.db"

    def test_creates_instance_with_custom_path(self, tmp_db):
        hc = FixHealthCheck(db_path=tmp_db)
        assert hc._db_path == tmp_db


class TestCheck:
    def test_check_all_healthy(self, health_check):
        fixer = MagicMock()
        fixer.scan = lambda: []
        report = health_check.check(fixers={"drift_fixer": fixer}, budget_ok=True)
        assert isinstance(report, FixHealthReport)
        assert report.healthy
        assert report.fixers["drift_fixer"] == "healthy"

    def test_check_degraded_fixer_missing_scan(self, health_check):
        fixer = MagicMock(spec=[])
        report = health_check.check(fixers={"bad_fixer": fixer})
        assert report.fixers["bad_fixer"] == "degraded"

    def test_check_unhealthy_fixer_raises(self, health_check):
        fixer = MagicMock()
        fixer.scan = MagicMock(side_effect=RuntimeError("boom"))
        type(fixer).scan = property(lambda self: (_ for _ in ()).throw(RuntimeError("boom")))
        report = health_check.check(fixers={"broken": fixer})
        assert report.fixers["broken"] == "unhealthy"

    def test_check_no_fixers(self, health_check):
        report = health_check.check()
        assert report.fixers == {}
        assert report.healthy

    def test_check_budget_not_ok(self, health_check):
        report = health_check.check(budget_ok=False)
        assert not report.healthy
        assert not report.budget_ok

    def test_check_cascade_active(self, health_check):
        report = health_check.check(cascade_active=True)
        assert not report.healthy
        assert report.cascade_active

    def test_check_dead_letter_count_high(self, health_check):
        report = health_check.check(dead_letter_count=150)
        assert not report.healthy

    def test_check_dead_letter_count_at_threshold(self, health_check):
        report = health_check.check(dead_letter_count=99)
        assert report.healthy

    def test_check_approval_queue_size(self, health_check):
        report = health_check.check(approval_queue_size=5)
        assert report.approval_queue_size == 5

    def test_check_none_fixers(self, health_check):
        report = health_check.check(fixers=None)
        assert report.fixers == {}

    def test_check_empty_fixers(self, health_check):
        report = health_check.check(fixers={})
        assert report.fixers == {}


class TestCheckDb:
    def test_check_db_accessible(self, health_check):
        assert health_check._check_db() is True

    def test_check_db_invalid_path(self, tmp_path):
        db_path = str(tmp_path / "readonly_dir" / "test.db")
        os.makedirs(tmp_path / "readonly_dir", exist_ok=True)
        hc = FixHealthCheck(db_path=db_path)
        with patch(
            "zephyr.infrastructure.auto_fix_engine.fix_health_check.sqlite3.connect",
            side_effect=OSError("permission denied"),
        ):
            result = hc._check_db()
        assert result is False


class TestCheckConfig:
    def test_check_config_returns_bool(self, health_check):
        result = health_check._check_config()
        assert isinstance(result, bool)
