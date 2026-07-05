# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.kill_switch
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
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
# [A_module] module_id=MOD-INF_kill_switch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
KillSwitchManager — 三级 Kill Switch 管理器。

依据: 蓝图 MOD-INF-021 §6.2 B46 + D-021-15

L1 Session Kill: 中断单个 agent session 回滚权限
L2 Skill Kill:   禁用特定模块的自动回滚
L3 Global Kill:   完全禁用所有自动回滚——仅限 token-gated

自动递进升级: L1→L2→L3 逐级升级直到修复。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class KillLevel(str, Enum):
    L1_SESSION = "L1_SESSION"
    L2_SKILL = "L2_SKILL"
    L3_GLOBAL = "L3_GLOBAL"
    NONE = "NONE"


@dataclass
class KillSwitchEntry:
    level: KillLevel
    target: str
    reason: str
    activated_at: str
    expires_at: str
    token_used: str


@dataclass
class KillSwitchStatus:
    global_killed: bool
    skills_killed: list[str]
    sessions_killed: list[str]
    active_entries: int


class KillSwitchManager:
    KILL_SWITCH_FILE: str = ".zephyr/kill_switches.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._kill_path = self._project_root / self.KILL_SWITCH_FILE

    def activate(
        self,
        level: KillLevel,
        target: str,
        reason: str,
        token: str = "",
    ) -> KillSwitchEntry:
        if level is KillLevel.L3_GLOBAL and not token:
            raise ValueError("L3_GLOBAL requires BREAK_GLASS token")

        now = datetime.now(UTC)
        entry = KillSwitchEntry(
            level=level,
            target=target,
            reason=reason,
            activated_at=now.isoformat(),
            expires_at="",
            token_used=token,
        )

        record = {
            "level": entry.level.value,
            "target": entry.target,
            "reason": entry.reason,
            "activated_at": entry.activated_at,
            "expires_at": entry.expires_at,
            "token_used": entry.token_used,
        }

        self._kill_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._kill_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()

        return entry

    def deactivate(self, level: KillLevel, target: str) -> bool:
        if not self._kill_path.exists():
            return False

        entries = self._read_all()
        updated = False
        new_entries: list[dict[str, Any]] = []

        for entry in entries:
            if entry.get("level") == level.value and entry.get("target") == target:
                updated = True
                continue
            new_entries.append(entry)

        if updated:
            tmp_path = f"{self._kill_path}.{os.getpid()}.tmp"
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    for e in new_entries:
                        f.write(json.dumps(e, ensure_ascii=False) + "\n")
                os.replace(tmp_path, self._kill_path)
            except PermissionError:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        return updated

    def is_killed(self, session_id: str = "", skill_id: str = "") -> tuple[bool, KillLevel]:
        status = self.status()

        if status.global_killed:
            return True, KillLevel.L3_GLOBAL

        if skill_id and skill_id in status.skills_killed:
            return True, KillLevel.L2_SKILL

        if session_id and session_id in status.sessions_killed:
            return True, KillLevel.L1_SESSION

        return False, KillLevel.NONE

    def status(self) -> KillSwitchStatus:
        entries = self._read_all()

        global_killed = any(e.get("level") == KillLevel.L3_GLOBAL.value for e in entries)
        skills_killed = [e["target"] for e in entries if e.get("level") == KillLevel.L2_SKILL.value]
        sessions_killed = [e["target"] for e in entries if e.get("level") == KillLevel.L1_SESSION.value]

        return KillSwitchStatus(
            global_killed=global_killed,
            skills_killed=skills_killed,
            sessions_killed=sessions_killed,
            active_entries=len(entries),
        )

    def escalate(self, target: str, reason: str) -> KillSwitchEntry:
        status = self.status()
        if target in status.sessions_killed:
            return self.activate(KillLevel.L2_SKILL, target, f"ESCALATED: {reason}")
        return self.activate(KillLevel.L1_SESSION, target, reason)

    def _read_all(self) -> list[dict[str, Any]]:
        if not self._kill_path.exists():
            return []
        entries: list[dict[str, Any]] = []
        with open(self._kill_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries
