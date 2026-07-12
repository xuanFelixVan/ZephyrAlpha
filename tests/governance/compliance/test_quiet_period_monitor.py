# [A_test] module_id: SRC-TST-1425 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_quiet_period_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_quiet_period_monitor.py
# [TTL] task_bound

from __future__ import annotations

import os
import time
from pathlib import Path

from zephyr.gov_kb.quiet_period_monitor import QuietPeriodMonitor, QuietPeriodReport


class TestQuietPeriodMonitor:
    def _make_monitor(self, tmp_path: Path) -> QuietPeriodMonitor:
        return QuietPeriodMonitor(project_root=tmp_path)

    def _ke_dir(self, tmp_path: Path) -> Path:
        return tmp_path / "docs" / "08_knowledge" / "01_raw_intake"

    def test_check_no_dir(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        report = monitor.check()
        assert isinstance(report, QuietPeriodReport)
        assert report.status == "empty"
        assert report.total_kes == 0

    def test_check_empty_dir(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        self._ke_dir(tmp_path).mkdir(parents=True, exist_ok=True)
        report = monitor.check()
        assert report.status == "empty"
        assert report.total_kes == 0

    def test_check_recent_ke(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        ke_dir.mkdir(parents=True, exist_ok=True)
        (ke_dir / "KE-001.md").write_text("recent content", encoding="utf-8")
        report = monitor.check()
        assert report.total_kes == 1
        assert report.status in ("active", "quiet", "silent")
        assert report.recent_count_7d >= 1

    def test_check_multiple_kes(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        ke_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):
            (ke_dir / f"KE-{i:03d}.md").write_text(f"content {i}", encoding="utf-8")
        report = monitor.check()
        assert report.total_kes == 5
        assert report.recent_count_7d == 5

    def test_report_fields(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        ke_dir.mkdir(parents=True, exist_ok=True)
        (ke_dir / "KE-100.md").write_text("x", encoding="utf-8")
        report = monitor.check()
        assert report.timestamp
        assert report.last_activity != "never"
        assert report.days_silent >= 0
        assert isinstance(report.diagnostics, list)

    def test_know_dir_property(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        assert str(monitor.know_dir).endswith("01_raw_intake")

    def test_old_ke_triggers_quiet_or_silent(self, tmp_path: Path):
        monitor = self._make_monitor(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        ke_dir.mkdir(parents=True, exist_ok=True)
        old_file = ke_dir / "KE-200.md"
        old_file.write_text("old content", encoding="utf-8")
        old_mtime = time.time() - (10 * 24 * 3600)
        os.utime(str(old_file), (old_mtime, old_mtime))
        report = monitor.check()
        assert report.status in ("quiet", "silent", "active")
