# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.absence_manager
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_infrastructure.py ; tests/audit/test_absence_manager.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 缺席管理不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Owner Absence Manager — Owner缺席模式 §6.32。


absence_detection: Owener >7天未响应任何drift事件


escalation_logic: 按预定escalation_list派发


time_budget_ratio: 租金值越高越容易休眠


休眠后唤醒: login事件/commit message触发Owner回归


safe_operate: admin可设置severe级别限制


对标 blueprint.md §6.32。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: owner_id 参数
#   fields: 参数 owner_id，类型注解 str
#   code: absence_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: status 参数
#   fields: 参数 status，类型注解 OwnerStatus
#   code: absence_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: last_activity 参数
#   fields: 参数 last_activity，类型注解 datetime
#   code: absence_manager.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: max_severity 参数
#   fields: 参数 max_severity，类型注解 str
#   code: absence_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① record_activity
#   name_en: record_activity
#   intro: record_activity(owner_id) 源码 L210-L219
#   desc: 源码 L210-L219
#   inputs: owner_id
#   outputs: 返回值
# - id: A2
#   name_zh: ② check_absence
#   name_en: check_absence
#   intro: check_absence(owner_id) 源码 L222-L257
#   desc: 源码 L222-L257
#   inputs: owner_id
#   outputs: OwnerStatus
# - id: A3
#   name_zh: ③ escalate_if_absent
#   name_en: escalate_if_absent
#   intro: escalate_if_absent(status) 源码 L260-L276
#   desc: 源码 L260-L276
#   inputs: status
#   outputs: EscalationEntry | None
# - id: A4
#   name_zh: ④ detect_owner_return
#   name_en: detect_owner_return
#   intro: detect_owner_return(owner_id, last_activity) 源码 L279-L282
#   desc: 源码 L279-L282
#   inputs: owner_id last_activity
#   outputs: bool
# - id: A5
#   name_zh: ⑤ set_severity_limit
#   name_en: set_severity_limit
#   intro: set_severity_limit(owner_id, max_severity, admin) 源码 L285-L…
#   desc: 源码 L285-L303
#   inputs: owner_id max_severity admin
#   outputs: bool
#   （注：A5 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: OwnerStatus
#   name_en: OwnerStatus
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/audit/test_absence_manager.py
# - id: O2
#   name_zh: EscalationEntry | None
#   name_en: EscalationEntry | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/audit/test_absence_manager.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final

from zephyr.shared.io.serialization import dumps


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

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {}


def _save_absence_state(state: dict[str, object]) -> None:
    if not CONFIG.state_dir:
        return

    os.makedirs(CONFIG.state_dir, exist_ok=True)

    path = os.path.join(CONFIG.state_dir, ABSENCE_STATE_FILE)

    tmp = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(dumps(state, indent=2))

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

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
