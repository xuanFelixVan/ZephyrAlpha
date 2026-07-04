# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §8.3 + §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.game_day_scheduler
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.game_day_runner
# [CONSUMERS] cli.py; CI/CD workflow
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Dual trigger: timer-based (daily/weekly/monthly) + webhook-based (git push → per_commit); MUST NOT schedule overlapping game days
# [MODIFY-GUARD] Adding triggers MUST update _TRIGGER_MAP; scheduler state persisted to data/red_blue/scheduler-state.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ScheduleConflictError on overlapping schedules; SchedulerNotInitializedError if state file missing
# [TESTS] tests/red_blue/test_game_day_scheduler.py
# [A_module] module_id=MOD-SEC_game_day_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.game_day_runner import GameDayFrequency, GameDayRunner

logger = logging.getLogger(__name__)

__all__: list[str] = ["GameDayScheduler", "ScheduleConflictError"]

_STATE_PATH: Path = Path("data/red_blue/scheduler-state.yaml")
# 5.79.2 修复：原模块级 os.makedirs 在 import 时执行，在只读文件系统/受限沙箱中 import 直接抛 PermissionError。
# 延迟到 GameDayScheduler.__init__ 中创建。

_TRIGGER_MAP: dict[str, list[GameDayFrequency]] = {
    "git_push": [GameDayFrequency.PER_COMMIT],
    "cron_daily": [GameDayFrequency.DAILY],
    "cron_weekly": [GameDayFrequency.WEEKLY],
    "cron_monthly": [GameDayFrequency.MONTHLY],
    "full_cycle": [
        GameDayFrequency.PER_COMMIT,
        GameDayFrequency.DAILY,
        GameDayFrequency.WEEKLY,
        GameDayFrequency.MONTHLY,
    ],
}


class ScheduleConflictError(RuntimeError):
    pass


class GameDayScheduler:
    def __init__(self, state_path: Path | None = None) -> None:
        self._state_path: Path = state_path or _STATE_PATH
        # 5.79.2 修复：延迟到 __init__ 创建目录，避免 import 时副作用。
        os.makedirs("data/red_blue", exist_ok=True)
        self._runner = GameDayRunner()
        self._state: dict = self._load_state()

    def trigger(self, trigger_name: str) -> list[dict]:
        frequencies = _TRIGGER_MAP.get(trigger_name, [])
        if not frequencies:
            logger.warning("unknown_trigger trigger=%s", trigger_name)
            return []

        if self._is_running():
            raise ScheduleConflictError(f"Cannot trigger {trigger_name}: game day already running")

        results: list[dict] = []
        self._set_running(True)

        try:
            for freq in frequencies:
                if self._should_run(freq):
                    result = self._runner.run_game_day(freq)
                    self._record_run(freq, result)
                    results.append(
                        {
                            "frequency": freq.value,
                            "total": result.total_attacks,
                            "blocked": result.passed,
                            "bypassed": result.bypasses,
                        }
                    )
        finally:
            self._set_running(False)

        return results

    def handle_webhook(self, event_type: str, payload: dict | None = None) -> list[dict]:
        if event_type == "push":
            return self.trigger("git_push")
        elif event_type == "schedule":
            return self.trigger("cron_daily")
        elif event_type == "full_cycle":
            return self.trigger("full_cycle")
        else:
            return self.trigger(event_type)

    def last_run(self, frequency: GameDayFrequency) -> datetime | None:
        last = self._state.get("last_runs", {}).get(frequency.value)
        if last:
            return datetime.fromisoformat(last)
        return None

    def next_scheduled(self, frequency: GameDayFrequency) -> datetime | None:
        last = self.last_run(frequency)
        if last is None:
            return datetime.now(UTC)

        intervals: dict[str, timedelta] = {
            "per_commit": timedelta(minutes=5),
            "daily": timedelta(days=1),
            "weekly": timedelta(days=7),
            "monthly": timedelta(days=30),
        }
        interval = intervals.get(frequency.value, timedelta(days=1))
        return last + interval

    def _should_run(self, frequency: GameDayFrequency) -> bool:
        next_run = self.next_scheduled(frequency)
        if next_run is None:
            return True
        return datetime.now(UTC) >= next_run

    def _is_running(self) -> bool:
        return self._state.get("running", False)

    def _set_running(self, running: bool) -> None:
        self._state["running"] = running
        self._state["updated_at"] = datetime.now(UTC).isoformat()
        self._save_state()

    def _record_run(self, frequency: GameDayFrequency, result) -> None:
        if "last_runs" not in self._state:
            self._state["last_runs"] = {}
        self._state["last_runs"][frequency.value] = datetime.now(UTC).isoformat()

        if "history" not in self._state:
            self._state["history"] = []
        self._state["history"].append(
            {
                "frequency": frequency.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "total": result.total_attacks,
                "blocked": result.passed,
                "bypassed": result.bypasses,
            }
        )
        self._state["history"] = self._state["history"][-50:]
        self._save_state()

    def _load_state(self) -> dict:
        if not self._state_path.exists():
            default = {"running": False, "last_runs": {}, "history": [], "updated_at": ""}
            self._save_state_raw(default)
            return default
        with open(self._state_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_state(self) -> None:
        self._save_state_raw(self._state)

    def _save_state_raw(self, state: dict) -> None:
        tmp = self._state_path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(state, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp, self._state_path)
