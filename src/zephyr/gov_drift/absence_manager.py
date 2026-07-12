# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.absence_manager
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py; tests/audit/test_absence_manager.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 缺席管理不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_absence_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Owner Absence Manager — Owner缺席模式 §6.32。


absence_detection: Owener >7天未响应任何drift事件


escalation_logic: 按预定escalation_list派发


time_budget_ratio: 租金值越高越容易休眠


休眠后唤醒: login事件/commit message触发Owner回归


safe_operate: admin可设置severe级别限制


对标 blueprint.md §6.32。"""

from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class OwnerStatus:
    owner_id: str

    last_active: datetime

    is_present: bool = True

    absent_days: int = 0

    escalated_to: str | None = None


@dataclass
class EscalationEntry:
    owner_id: str

    escalated_to: str

    escalated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    reason: str = ""


ABSENCE_THRESHOLD_DAYS: Final[int] = 7


ABSENCE_STATE_FILE: Final[str] = "_absence_state.json"


@dataclass
class AbsenceManagerConfig:
    threshold_days: int = 7

    escalation_list: list[str] = field(default_factory=list)

    state_dir: str = ""


CONFIG: Final[AbsenceManagerConfig] = AbsenceManagerConfig()


def _load_absence_state() -> dict[str, object]:
    path = os.path.join(CONFIG.state_dir, ABSENCE_STATE_FILE)

    if not path or not os.path.exists(path):
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            return json.loads(f.read())

    except Exception:
        return {}


def _save_absence_state(state: dict[str, object]) -> None:
    if not CONFIG.state_dir:
        return

    os.makedirs(CONFIG.state_dir, exist_ok=True)

    path = os.path.join(CONFIG.state_dir, ABSENCE_STATE_FILE)

    tmp = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(dumps(state,  indent=2))

        os.replace(tmp, path)

    except PermissionError:
        try:
            os.remove(tmp)

        except OSError:
            pass


def record_activity(owner_id: str) -> None:
    state = _load_absence_state()

    state["owners"] = state.get("owners", {})

    state["owners"][owner_id] = {
        "last_active": datetime.now(UTC).isoformat(),
    }

    _save_absence_state(state)


def check_absence(owner_id: str) -> OwnerStatus:
    state = _load_absence_state()

    owners = state.get("owners", {})

    owner_data = owners.get(owner_id, {})

    last_active_str = owner_data.get("last_active", "")

    if not last_active_str:
        return OwnerStatus(
            owner_id=owner_id,
            last_active=datetime.now(UTC),
        )

    try:
        last_active = datetime.fromisoformat(last_active_str.replace("Z", "+00:00"))

    except Exception:
        return OwnerStatus(
            owner_id=owner_id,
            last_active=datetime.now(UTC),
        )

    now = datetime.now(UTC)

    absent_days = (now - last_active).days

    status = OwnerStatus(
        owner_id=owner_id,
        last_active=last_active,
        is_present=absent_days < ABSENCE_THRESHOLD_DAYS,
        absent_days=absent_days,
    )

    return status


def escalate_if_absent(status: OwnerStatus) -> EscalationEntry | None:
    if status.is_present:
        return None

    if not CONFIG.escalation_list:
        return None

    next_escalation = CONFIG.escalation_list[0] if CONFIG.escalation_list else None

    if not next_escalation:
        return None

    return EscalationEntry(
        owner_id=status.owner_id,
        escalated_to=next_escalation,
        reason=(f"Owner {status.owner_id} absent {status.absent_days} days (>{CONFIG.threshold_days}d threshold)"),
    )


def detect_owner_return(owner_id: str, last_activity: datetime) -> bool:
    now = datetime.now(UTC)

    return (now - last_activity).days < 1


def set_severity_limit(
    owner_id: str,
    max_severity: str = "MINOR",
    admin: bool = False,
) -> bool:
    if not admin:
        return False

    state = _load_absence_state()

    state.setdefault("severity_limits", {})[owner_id] = {
        "max_severity": max_severity,
        "set_by": "admin",
        "set_at": datetime.now(UTC).isoformat(),
    }

    _save_absence_state(state)

    return True
