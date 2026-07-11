# [BLUEPRINT] (migrated from MOD-INF-021 by ARCH-039 P1, target domain=D_GOVERNANCE)
# [MODULE] zephyr.governance.escalation.owner_absent
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.escalation.__init__
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
# [A_module] module_id=MOD-INF_owner_absent | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Owner Absent — 人力缺席分级处置。

依据：
    蓝图 MOD-INF-021 §6.16 B111 + 决策 D-021-31
    任务卡 TASK-INF-0266 (Part 2)

功能：
    - L3 Owner absent (30min timeout) -> exit 31 -> defer + retry
    - L1 Owner absent (7天无响应) -> exit 32 -> escalate
    - 多层次 Owner absent 分级处置
"""

from __future__ import annotations

from typing import Final
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

EXIT_OWNER_ABSENT_L3: Final[int] = 31
EXIT_OWNER_ABSENT_L1: Final[int] = 32


@dataclass
class OwnerPing:
    timestamp_utc: str
    attempts: int
    last_response: str | None


@dataclass
class AbsentStatus:
    level: int
    absent_since: str
    last_ping_attempt: str
    ping_attempts: int
    exit_code: int
    action: str


class OwnerAbsent:
    L3_TIMEOUT_SECONDS = 1800
    L1_TIMEOUT_DAYS = 7

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/rollback/owner")
        self._state_path = self._data_dir / "owner_absent_state.json"

    def check_owner_status(self, last_owner_interaction: str) -> AbsentStatus:
        try:
            last_ts = datetime.fromisoformat(last_owner_interaction)
        except (ValueError, TypeError):
            last_ts = datetime.now(UTC)

        now = datetime.now(UTC)
        elapsed = now - last_ts

        state = self._load_state()

        if elapsed >= timedelta(days=self.L1_TIMEOUT_DAYS):
            return AbsentStatus(
                level=1,
                absent_since=last_owner_interaction,
                last_ping_attempt=state.get("last_ping_attempt", now.isoformat()),
                ping_attempts=state.get("ping_attempts", 0),
                exit_code=EXIT_OWNER_ABSENT_L1,
                action="ESCALATE: Owner absent for 7+ days. Notify backup contacts.",
            )

        if elapsed >= timedelta(seconds=self.L3_TIMEOUT_SECONDS):
            return AbsentStatus(
                level=3,
                absent_since=last_owner_interaction,
                last_ping_attempt=state.get("last_ping_attempt", now.isoformat()),
                ping_attempts=state.get("ping_attempts", 0),
                exit_code=EXIT_OWNER_ABSENT_L3,
                action="DEFER: Owner absent >30min. Retry with exponential backoff.",
            )

        return AbsentStatus(
            level=0,
            absent_since="",
            last_ping_attempt="",
            ping_attempts=0,
            exit_code=0,
            action="OK: Owner responsive.",
        )

    def record_owner_interaction(self) -> str:
        now = datetime.now(UTC).isoformat()

        self._data_dir.mkdir(parents=True, exist_ok=True)

        state = self._load_state()
        state["last_owner_interaction"] = now
        state["ping_attempts"] = 0
        state["updated_at"] = now

        self._state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return now

    def record_ping_attempt(self, success: bool = False) -> OwnerPing:
        state = self._load_state()
        attempts = state.get("ping_attempts", 0) + 1
        now = datetime.now(UTC).isoformat()

        if success:
            state["last_owner_interaction"] = now
            state["ping_attempts"] = 0
        else:
            attempts = state.get("ping_attempts", 0) + 1

        state["last_ping_attempt"] = now
        state["updated_at"] = now

        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return OwnerPing(
            timestamp_utc=now,
            attempts=attempts,
            last_response=state.get("last_owner_interaction") if success else None,
        )

    def get_absent_status(self) -> AbsentStatus:
        state = self._load_state()
        last_interaction = state.get("last_owner_interaction", "")

        if not last_interaction:
            return AbsentStatus(
                level=0,
                absent_since="",
                last_ping_attempt="",
                ping_attempts=0,
                exit_code=0,
                action="NO_DATA: No owner interaction records.",
            )

        return self.check_owner_status(last_interaction)

    def generate_escalation_message(self, status: AbsentStatus) -> dict[str, Any]:
        return {
            "escalation_id": f"ESC-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "absent_level": status.level,
            "absent_since": status.absent_since,
            "ping_attempts": status.ping_attempts,
            "exit_code": status.exit_code,
            "action": status.action,
            "recommendation": (
                "Autonomous operations suspended. All critical rollbacks require human confirmation."
                if status.level >= 3
                else "Normal operations."
            ),
        }

    def _load_state(self) -> dict[str, Any]:
        if not self._state_path.exists():
            return {
                "created_at": datetime.now(UTC).isoformat(),
                "ping_attempts": 0,
            }

        try:
            return json.loads(self._state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "created_at": datetime.now(UTC).isoformat(),
                "ping_attempts": 0,
            }
