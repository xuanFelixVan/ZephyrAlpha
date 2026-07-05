# [BLUEPRINT] SRC-138 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.session.session_boundary
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.session.session_continuity
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_session_boundary | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Session Boundary — 会话边界管理。

依据：
    蓝图 MOD-TASK_SYSTEM §6.11.4 + v0.6.0
    任务卡 TASK-INF-0126
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class SessionBoundary:
    session_id: str
    start_time: str
    end_time: str = ""
    cards_processed: int = 0
    files_created: int = 0
    files_modified: int = 0
    tokens_used: int = 0


@dataclass
class SessionBudget:
    max_cards: int = 115
    max_tokens: int = 200000
    used_cards: int = 0
    used_tokens: int = 0


class SessionBoundaryManager:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/session")
        self._boundaries: list[SessionBoundary] = []
        self._budget = SessionBudget()

    def open_session(self, session_id: str) -> SessionBoundary:
        boundary = SessionBoundary(
            session_id=session_id,
            start_time=datetime.now(UTC).isoformat(),
        )
        self._boundaries.append(boundary)
        return boundary

    def close_session(self, boundary: SessionBoundary) -> None:
        boundary.end_time = datetime.now(UTC).isoformat()
        self._save_boundary(boundary)

    def record_activity(self, boundary: SessionBoundary, cards: int = 0, files: int = 0, tokens: int = 0) -> None:
        boundary.cards_processed += cards
        boundary.files_created += files
        boundary.tokens_used += tokens
        self._budget.used_cards += cards
        self._budget.used_tokens += tokens

    def check_budget(self) -> tuple[bool, str]:
        if self._budget.used_cards >= self._budget.max_cards:
            return True, f"Card budget exhausted: {self._budget.used_cards}/{self._budget.max_cards}"
        if self._budget.used_tokens >= self._budget.max_tokens:
            return True, f"Token budget exhausted: {self._budget.used_tokens}/{self._budget.max_tokens}"
        return False, "Within budget"

    def get_active_boundary(self) -> SessionBoundary | None:
        active = [b for b in self._boundaries if not b.end_time]
        return active[-1] if active else None

    def clean_old_boundaries(self, max_age_days: int = 30) -> int:
        cleared = 0
        self._data_dir.mkdir(parents=True, exist_ok=True)

        for f in self._data_dir.glob("session_*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                end_time = data.get("end_time", "")
                if end_time:
                    end_dt = datetime.fromisoformat(end_time)
                    if (datetime.now(UTC) - end_dt).days > max_age_days:
                        f.unlink()
                        cleared += 1
            except (json.JSONDecodeError, ValueError):
                pass

        return cleared

    def _save_boundary(self, boundary: SessionBoundary) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        path = self._data_dir / f"session_{boundary.session_id}.json"
        path.write_text(
            json.dumps(
                {
                    "session_id": boundary.session_id,
                    "start_time": boundary.start_time,
                    "end_time": boundary.end_time,
                    "cards_processed": boundary.cards_processed,
                    "files_created": boundary.files_created,
                    "files_modified": boundary.files_modified,
                    "tokens_used": boundary.tokens_used,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
