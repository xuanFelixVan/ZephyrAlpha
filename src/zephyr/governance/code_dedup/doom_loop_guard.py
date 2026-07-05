# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.doom_loop_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/resilience/test_doom_loop_guard.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_doom_loop_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.

职责：
  - L0 Direct Fix → L1 Partial Fix → L2 Retry Once → L3 Escalate → L4 Stop+Alert
  - 3次失败 → freeze_dup_group → 24h内不重复尝试
  - 冻结列表 doom-loop-freeze-list.json 维护
  - Session Log ALERT 写入
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import IntEnum
from pathlib import Path


class EscalationLevel(IntEnum):
    L0_DIRECT_FIX = 0
    L1_PARTIAL_FIX = 1
    L2_RETRY_ONCE = 2
    L3_ESCALATE = 3
    L4_STOP_ALERT = 4


@dataclass
class FreezeEntry:
    dup_group_id: str
    failed_attempts: int = 0
    last_attempt_utc: str = ""
    escalation_level: int = EscalationLevel.L0_DIRECT_FIX
    reason: str = ""
    frozen_until_utc: str = ""
    affected_files: list[str] = field(default_factory=list)


class DoomLoopGuard:
    """Doom Loop 防护器."""

    _MAX_ATTEMPTS: int = 3
    _FREEZE_HOURS: int = 24

    def __init__(self, freeze_path: str | Path | None = None) -> None:
        if freeze_path is None:
            freeze_path = Path("data/cache/doom-loop-freeze-list.json")
        self._freeze_path = Path(freeze_path)
        self._frozen: dict[str, FreezeEntry] = {}
        self._load_freeze_list()

    # ── 公共 API ──────────────────────────────────────────────

    def escalate(
        self,
        dup_group_id: str,
        current_level: int = 0,
        reason: str = "",
        affected_files: list[str] | None = None,
    ) -> tuple[int, bool, str]:
        """升级到下一级——返回 (new_level, is_frozen, alert_msg)."""
        entry = self._frozen.get(dup_group_id)
        if entry is None:
            entry = FreezeEntry(dup_group_id=dup_group_id, failed_attempts=0)
            self._frozen[dup_group_id] = entry

        entry.failed_attempts += 1
        entry.last_attempt_utc = datetime.now(UTC).isoformat()
        entry.reason = reason
        entry.affected_files = affected_files or []

        if entry.failed_attempts >= self._MAX_ATTEMPTS:
            new_level = EscalationLevel.L4_STOP_ALERT
            frozen_until = datetime.now(UTC) + timedelta(hours=self._FREEZE_HOURS)
            entry.frozen_until_utc = frozen_until.isoformat()
            entry.escalation_level = new_level
            self._save_freeze_list()

            alert_msg = (
                f"ALERT: DUP group {dup_group_id} frozen after {entry.failed_attempts} failed attempts. "
                f"Frozen until {entry.frozen_until_utc}. Reason: {reason}"
            )
            return new_level, True, alert_msg

        new_level = min(current_level + 1, EscalationLevel.L3_ESCALATE)
        entry.escalation_level = new_level
        self._save_freeze_list()

        is_frozen = new_level >= EscalationLevel.L3_ESCALATE
        alert_msg = ""
        if is_frozen:
            alert_msg = (
                f"WARN: DUP group {dup_group_id} escalated to L{new_level}. "
                f"Attempt {entry.failed_attempts}/{self._MAX_ATTEMPTS}. "
                f"Reason: {reason}"
            )

        return new_level, is_frozen, alert_msg

    def is_frozen(self, dup_group_id: str) -> bool:
        """检查 DUP group 是否被冻结."""
        entry = self._frozen.get(dup_group_id)
        if entry is None:
            return False
        if entry.escalation_level < EscalationLevel.L3_ESCALATE:
            return False
        if entry.frozen_until_utc:
            frozen_until = datetime.fromisoformat(entry.frozen_until_utc)
            if datetime.now(UTC) < frozen_until.replace(tzinfo=UTC):
                return True
            self._unfreeze(dup_group_id)
        return False

    def reset_group(self, dup_group_id: str) -> None:
        """手动重置 DUP group（修复成功后调用）."""
        self._frozen.pop(dup_group_id, None)
        self._save_freeze_list()

    def get_frozen_groups(self) -> list[FreezeEntry]:
        """获取所有冻结的 group."""
        return [e for e in self._frozen.values() if e.escalation_level >= EscalationLevel.L3_ESCALATE]

    def get_freeze_report(self) -> dict:
        """冻结列表报告."""
        return {
            "total_frozen": len(self.get_frozen_groups()),
            "frozen_groups": [
                {
                    "dup_group_id": e.dup_group_id,
                    "failed_attempts": e.failed_attempts,
                    "escalation_level": e.escalation_level,
                    "frozen_until": e.frozen_until_utc,
                    "reason": e.reason,
                }
                for e in self.get_frozen_groups()
            ],
        }

    # ── 内部 ──────────────────────────────────────────────────

    def _load_freeze_list(self) -> None:
        self._frozen.clear()
        if not self._freeze_path.exists():
            return
        try:
            data = json.loads(self._freeze_path.read_text(encoding="utf-8"))
            for entry_data in data.get("frozen_groups", []):
                entry = FreezeEntry(**entry_data)
                self._frozen[entry.dup_group_id] = entry
        except (json.JSONDecodeError, OSError):
            pass

    def _save_freeze_list(self) -> None:
        self._freeze_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "frozen_groups": [e.__dict__ for e in self._frozen.values()],
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self._freeze_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _unfreeze(self, dup_group_id: str) -> None:
        entry = self._frozen.pop(dup_group_id, None)
        if entry:
            self._save_freeze_list()
