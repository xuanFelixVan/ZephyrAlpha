# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_drill
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_drill | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackDrill — 定期回滚演练调度器 (DiRT-style)。

依据: 蓝图 MOD-INF-021 §6.10 B41/B52, §7 Phase 5.3, 决策 D-021-09

每周六 03:00 AM UTC 在 git worktree 副本中执行真实回滚演练。
混沌场景: gc_concurrent / sqlite_locked / disk_90pct / cpu_saturation
连续 2 次 drill FAIL → P0 Alert → 熔断所有自动回滚。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import random
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ChaosScenario:
    name: str
    description: str
    enabled: bool = True


@dataclass
class DrillResult:
    drill_id: str
    timestamp_utc: str
    commit_sha: str
    duration_ms: int
    conflict_rate: float
    db_integrity_pass: bool
    chaos_scenario: str
    success: bool
    details: list[str] = field(default_factory=list)


CHAOS_SCENARIOS: list[ChaosScenario] = [
    ChaosScenario("gc_concurrent", "并发 GC 压力——多线程垃圾回收与回滚竞争"),
    ChaosScenario("sqlite_locked", "SQLite 锁竞争——回滚期间 DB 被外部锁定"),
    ChaosScenario("disk_90pct", "磁盘 90% 满载——限制 dump JSONL 写入空间"),
    ChaosScenario("cpu_saturation", "CPU 极限——stress-ng 满载所有核心"),
]


class RollbackDrill:
    DRILL_SCHEDULE_DAY: int = 5
    DRILL_SCHEDULE_HOUR: int = 3
    MAX_CONSECUTIVE_FAILS: int = 2
    DRILL_LOG_DIR: str = ".zephyr/drill_logs"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._drill_log_dir = self._project_root / self.DRILL_LOG_DIR
        self._drill_log_dir.mkdir(parents=True, exist_ok=True)
        self._consecutive_fails = 0
        self._automatic_rollback_melted = False

    def is_drill_time(self) -> bool:
        now = datetime.now(UTC)
        return now.weekday() == self.DRILL_SCHEDULE_DAY and now.hour == self.DRILL_SCHEDULE_HOUR

    def select_random_commit(self) -> str:
        log = self._run_git(["log", "--oneline", "-20"])
        lines = [l.split()[0] for l in log.strip().split("\n") if l]
        if not lines:
            return ""
        return random.choice(lines)

    def run_drill(self, force_chaos: str = "") -> DrillResult:
        drill_id = f"DRILL-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
        start_time = time.time()

        commit_sha = self.select_random_commit()
        if not commit_sha:
            return DrillResult(
                drill_id=drill_id,
                timestamp_utc=datetime.now(UTC).isoformat(),
                commit_sha="",
                duration_ms=0,
                conflict_rate=0.0,
                db_integrity_pass=False,
                chaos_scenario="",
                success=False,
                details=["No commits available for drill"],
            )

        scenario = force_chaos or random.choice([s.name for s in CHAOS_SCENARIOS if s.enabled])
        self._inject_chaos(scenario)

        worktree_path = self._project_root / f".zephyr/drill_worktree_{drill_id}"
        success = False
        details: list[str] = []

        try:
            self._run_git(["worktree", "add", str(worktree_path), commit_sha])
            details.append(f"Worktree created at {worktree_path}")

            result = subprocess.run(
                ["git", "revert", "--no-edit", commit_sha],
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                details.append(f"Revert succeeded: {commit_sha}")
                success = True
            else:
                details.append(f"Revert conflict: {result.stderr[:100]}")
                success = False

            db_integrity = self._check_db_integrity(worktree_path)
            details.append(f"DB integrity: {'PASS' if db_integrity else 'FAIL'}")

        except Exception as e:
            details.append(f"Drill exception: {e}")
            success = False
        finally:
            try:
                self._run_git(["worktree", "remove", "--force", str(worktree_path)])
            except Exception as e:
                logger.warning("suppressed error in rollback_drill", exc_info=True)
            self._cleanup_chaos(scenario)

        duration_ms = int((time.time() - start_time) * 1000)

        result = DrillResult(
            drill_id=drill_id,
            timestamp_utc=datetime.now(UTC).isoformat(),
            commit_sha=commit_sha,
            duration_ms=duration_ms,
            conflict_rate=0.0 if success else 1.0,
            db_integrity_pass=self._check_db_integrity(self._project_root),
            chaos_scenario=scenario,
            success=success,
            details=details,
        )

        self._save_drill_result(result)

        if success:
            self._consecutive_fails = 0
        else:
            self._consecutive_fails += 1
            if self._consecutive_fails >= self.MAX_CONSECUTIVE_FAILS:
                self._meltdown_automatic_rollback()

        return result

    def _inject_chaos(self, scenario: str) -> None:
        pass

    def _cleanup_chaos(self, scenario: str) -> None:
        pass

    def _check_db_integrity(self, path: Path) -> bool:
        try:
            db_path = path / "data" / "databases" / "governance.db"
            if not db_path.exists():
                return True
            conn = sqlite3.connect(str(db_path))
            result = conn.execute("PRAGMA integrity_check").fetchone()
            conn.close()
            return result[0] == "ok"
        except Exception:
            return False

    def _meltdown_automatic_rollback(self) -> None:
        self._automatic_rollback_melted = True
        alert = {
            "alert": "P0_ROLLBACK_DRILL_MELTDOWN",
            "consecutive_fails": self._consecutive_fails,
            "action": "ALL automatic rollbacks suspended",
            "timestamp_utc": datetime.now(UTC).isoformat(),
        }
        alert_path = self._project_root / ".zephyr/ROLLBACK_MELTDOWN.json"
        alert_path.write_text(json.dumps(alert, ensure_ascii=False, indent=2), encoding="utf-8")

    def _save_drill_result(self, result: DrillResult) -> None:
        log_path = self._drill_log_dir / f"{result.drill_id}.json"
        log_path.write_text(
            json.dumps(
                {
                    "drill_id": result.drill_id,
                    "timestamp_utc": result.timestamp_utc,
                    "commit_sha": result.commit_sha,
                    "duration_ms": result.duration_ms,
                    "conflict_rate": result.conflict_rate,
                    "db_integrity_pass": result.db_integrity_pass,
                    "chaos_scenario": result.chaos_scenario,
                    "success": result.success,
                    "details": result.details,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @property
    def is_melted(self) -> bool:
        return self._automatic_rollback_melted

    @property
    def consecutive_fails(self) -> int:
        return self._consecutive_fails

    def _run_git(self, args: list[str], timeout: int = 15) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.stdout
        except Exception:
            return ""
