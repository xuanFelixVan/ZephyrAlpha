# [A_test] module_id: MOD-GOV_cold_stub | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] tests.test_cold_stub
# [INVARIANTS] TTL分级策略严格执行;成本超限→三级降级;SQLite backup使用RULE-ONE原子写入
# [MODIFY-GUARD] archive/cold_stub.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] gzip失败→跳过压缩保留原文;SQLite backup失败→日志warning不阻塞
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

cs = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.archive.cold_stub",
    reason="cold_stub import failed",
)


@pytest.fixture(autouse=True)
def _reset_config():
    original_archive_dir = cs._DEFAULT_ARCHIVE_DIR
    original_db_path = cs._DB_PATH
    original_backup_dir = cs._BACKUP_DIR
    original_cost_limit = cs._COST_LIMIT_GB
    original_policy = cs._policy
    yield
    cs._DEFAULT_ARCHIVE_DIR = original_archive_dir
    cs._DB_PATH = original_db_path
    cs._BACKUP_DIR = original_backup_dir
    cs._COST_LIMIT_GB = original_cost_limit
    cs._policy = original_policy


class TestRetentionPolicy:
    def test_defaults(self):
        p = cs.RetentionPolicy()
        assert p.metrics_days == 30
        assert p.logs_days == 30
        assert p.traces_days == 7
        assert p.auto_cleanup is True

    def test_custom_values(self):
        p = cs.RetentionPolicy(metrics_days=60, traces_days=14)
        assert p.metrics_days == 60
        assert p.traces_days == 14


class TestConfigure:
    def test_configure_archive_dir(self, tmp_path):
        cs.configure(archive_dir=tmp_path / "archive")
        assert tmp_path / "archive" == cs._DEFAULT_ARCHIVE_DIR

    def test_configure_cost_limit(self):
        cs.configure(cost_limit_gb=20.0)
        assert cs._COST_LIMIT_GB == 20.0

    def test_configure_policy_overrides(self):
        cs.configure(policy_overrides={"metrics_days": 90})
        assert cs._policy.metrics_days == 90


class TestNextArchiveBatchId:
    def test_default_prefix(self):
        batch_id = cs.next_archive_batch_id()
        assert batch_id.startswith("batch-")

    def test_custom_prefix(self):
        batch_id = cs.next_archive_batch_id(prefix="arc")
        assert batch_id.startswith("arc-")

    def test_contains_timestamp(self):
        batch_id = cs.next_archive_batch_id()
        assert len(batch_id) > len("batch-")


class TestCompressDir:
    def test_nonexistent_dir(self, tmp_path):
        result = cs.compress_dir(tmp_path / "definitely_nonexistent_xyz", "test")
        assert result is None

    def test_compress_empty_dir(self, tmp_path):
        empty = tmp_path / "empty_src"
        empty.mkdir()
        cs.configure(archive_dir=tmp_path / "archive")
        result = cs.compress_dir(empty, "test_empty")
        assert result is not None
        assert result.suffix == ".gz"


class TestRotateByTtl:
    def test_nonexistent_dir(self):
        result = cs.rotate_by_ttl(Path("/nonexistent"), max_age_days=30)
        assert result == 0

    def test_removes_old_files(self, tmp_path):
        old_file = tmp_path / "old.txt"
        old_file.write_text("old data", encoding="utf-8")
        import os
        import time

        old_time = time.time() - 100 * 86400
        os.utime(old_file, (old_time, old_time))
        removed = cs.rotate_by_ttl(tmp_path, max_age_days=30)
        assert removed == 1
        assert not old_file.exists()

    def test_keeps_recent_files(self, tmp_path):
        recent_file = tmp_path / "recent.txt"
        recent_file.write_text("recent data", encoding="utf-8")
        removed = cs.rotate_by_ttl(tmp_path, max_age_days=30)
        assert removed == 0
        assert recent_file.exists()


class TestCostStatus:
    def test_returns_dict(self):
        status = cs.cost_status()
        assert isinstance(status, dict)
        assert "total_gb" in status
        assert "budget_gb" in status
        assert "usage_pct" in status
        assert "level" in status

    def test_level_ok_when_empty(self, tmp_path):
        cs.configure(archive_dir=tmp_path / "empty_archive", cost_limit_gb=10.0)
        status = cs.cost_status()
        assert status["level"] == "OK"


class TestApplyCostDegradation:
    def test_returns_list(self):
        actions = cs.apply_cost_degradation()
        assert isinstance(actions, list)


class TestBoundary:
    def test_next_batch_id_empty_prefix(self):
        batch_id = cs.next_archive_batch_id(prefix="")
        assert batch_id.startswith("-")

    def test_rotate_empty_dir(self, tmp_path):
        removed = cs.rotate_by_ttl(tmp_path, max_age_days=0)
        assert removed == 0

    def test_cost_status_zero_budget(self):
        cs.configure(cost_limit_gb=0.0)
        status = cs.cost_status()
        assert status["usage_pct"] == 0.0
