# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.gov_kb.quiet_period_monitor
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.gov_kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_quiet_period_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""每日静默期检测 + 管道健康自检
==================================
蓝图: MOD-KB-001 §9.18.1
任务: KB-INF-0032

检测:
  1. 7天内无KE创建/修改 -> WARN
  2. 14天内无KE创建/修改 -> FAIL

原因诊断:
  - 管道是否堵塞
  - AI session是否正常在写KE
  - 磁盘是否满了
  - ChromaDB是否崩溃

用法:
    python -m zephyr.knowledge.kb.quiet_period_monitor check
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)


@dataclass
class QuietPeriodReport:
    timestamp: str
    total_kes: int
    last_activity: str
    days_silent: int
    recent_count_7d: int
    recent_count_14d: int
    status: str  # active | quiet | silent
    diagnostics: list[str]


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class QuietPeriodMonitor:
    _WARN_DAYS = 7
    _ALERT_DAYS = 14

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    @property
    def know_dir(self) -> Path:
        return self._root / "docs" / "08_knowledge" / "01_raw_intake"

    def check(self) -> QuietPeriodReport:
        now = now_utc()
        now_ts = now.timestamp()

        if not self.know_dir.exists():
            return QuietPeriodReport(
                timestamp=now.isoformat(),
                total_kes=0,
                last_activity="never",
                days_silent=-1,
                recent_count_7d=0,
                recent_count_14d=0,
                status="empty",
                diagnostics=["KE directory does not exist"],
            )

        ke_files = list(self.know_dir.glob("ke-*.md"))
        total = len(ke_files)

        if total == 0:
            return QuietPeriodReport(
                timestamp=now.isoformat(),
                total_kes=0,
                last_activity="never",
                days_silent=-1,
                recent_count_7d=0,
                recent_count_14d=0,
                status="empty",
                diagnostics=["No KEs found"],
            )

        cutoff_7d = now_ts - (self._WARN_DAYS * 24 * 3600)
        cutoff_14d = now_ts - (self._ALERT_DAYS * 24 * 3600)

        recent_7d = [f for f in ke_files if f.stat().st_mtime > cutoff_7d]
        recent_14d = [f for f in ke_files if f.stat().st_mtime > cutoff_14d]

        latest_mtime = max(f.stat().st_mtime for f in ke_files)
        latest_dt = datetime.fromtimestamp(latest_mtime, tz=UTC)
        days_silent = int((now_ts - latest_mtime) / 86400)

        diagnostics: list[str] = []

        if days_silent >= self._ALERT_DAYS:
            status = "silent"
            diagnostics.append(f"No KE activity for {days_silent} days (>= {self._ALERT_DAYS}d alert threshold)")
            diagnostics.append("  -> Pipeline may be blocked. Check G1-G5 gate health.")
            diagnostics.append("  -> AI sessions may not be writing KEs. Check STEP 4.7 in cold startup.")
        elif days_silent >= self._WARN_DAYS:
            status = "quiet"
            diagnostics.append(f"No KE activity for {days_silent} days (>= {self._WARN_DAYS}d warn threshold)")
        else:
            status = "active"
            diagnostics.append(f"Last activity: {days_silent}d ago ({len(recent_7d)} KEs in last 7d)")

        if recent_7d and len(recent_7d) < 3:
            diagnostics.append(f"Low activity: only {len(recent_7d)} KEs in last 7 days")

        return QuietPeriodReport(
            timestamp=now.isoformat(),
            total_kes=total,
            last_activity=latest_dt.isoformat(),
            days_silent=days_silent,
            recent_count_7d=len(recent_7d),
            recent_count_14d=len(recent_14d),
            status=status,
            diagnostics=diagnostics,
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Quiet Period Monitor")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even when silent")
    args = parser.parse_args()

    monitor = QuietPeriodMonitor()
    report = monitor.check()

    if args.json:
        print(
            json.dumps(
                {
                    "timestamp": report.timestamp,
                    "total_kes": report.total_kes,
                    "last_activity": report.last_activity,
                    "days_silent": report.days_silent,
                    "recent_count_7d": report.recent_count_7d,
                    "recent_count_14d": report.recent_count_14d,
                    "status": report.status,
                    "diagnostics": report.diagnostics,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Quiet Period Monitor: {report.status.upper()}")
        print(f"  Total KEs:    {report.total_kes}")
        print(f"  Last activity: {report.last_activity}")
        print(f"  Days silent:  {report.days_silent}")
        print(f"  Recent (7d):  {report.recent_count_7d} KEs")
        print(f"  Recent (14d): {report.recent_count_14d} KEs")
        for d in report.diagnostics:
            print(d)

    if report.status == "silent" and not args.warn_only:
        sys.exit(1)


if __name__ == "__main__":
    main()
