# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.canary_controller
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_infrastructure.py ; tests/ba/test_ba_canary_controller.py ; tests/canary/test_canary_controller.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 金丝雀保护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Detector Canary Controller — 检测器金丝雀部署 §6.11。


v2独立ID运行，不入drift_events，对比v1分类NEW_FINDING/LOST_FINDING/CHANGED_SEVERITY


auto_rollback: v2 FP率>2×v1自动回退


对标 blueprint.md §6.11。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: v1_id 参数
#   fields: 参数 v1_id，类型注解 str
#   code: canary_controller.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: v2_ids 参数
#   fields: 参数 v2_ids，类型注解 set[str]
#   code: canary_controller.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: v1_events 参数
#   fields: 参数 v1_events，类型注解 list[dict[str, object]]
#   code: canary_controller.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: v2_events 参数
#   fields: 参数 v2_events，类型注解 list[dict[str, object]]
#   code: canary_controller.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① classify_event_id
#   name_en: classify_event_id
#   intro: 将单事件分类为NEW/LOST/CHANGED/IDENTICAL。
#   desc: 将单事件分类为NEW/LOST/CHANGED/IDENTICAL。；源码 L227-L259
#   inputs: v1_id v2_ids v1_events v2_events classification
#   outputs: 返回值
# - id: A2
#   name_zh: ② run_canary
#   name_en: run_canary
#   intro: 执行金丝雀运行：v1+v2独立运行，对比结果。
#   desc: 执行金丝雀运行：v1+v2独立运行，对比结果。；源码 L262-L319
#   inputs: v1_detector_id v2_detector_id v1_run_fn v2_run_fn
#   outputs: CanaryRun
# - id: A3
#   name_zh: ③ promote_detector
#   name_en: promote_detector
#   intro: Owner审查通过后将v2全量切换。
#   desc: Owner审查通过后将v2全量切换。；源码 L322-L342
#   inputs: canary_run
#   outputs: bool
# - id: A4
#   name_zh: ④ rollback_detector
#   name_en: rollback_detector
#   intro: 回退v2，恢复v1。
#   desc: 回退v2，恢复v1。；源码 L345-L362
#   inputs: canary_run reason
#   outputs: bool
# - id: A5
#   name_zh: ⑤ get_canary_history
#   name_en: get_canary_history
#   intro: 获取指定检测器的金丝雀历史。
#   desc: 获取指定检测器的金丝雀历史。；源码 L365-L375
#   inputs: detector_id
#   outputs: list[dict[str, object]]
#   （注：A5 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CanaryRun
#   name_en: CanaryRun
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/ba/test_ba_canary_controller.py…
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/ba/test_ba_canary_controller.py…
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
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from zephyr.shared.io.serialization import dumps


class CanaryComparison(str, Enum):
    NEW_FINDING = "NEW_FINDING"

    LOST_FINDING = "LOST_FINDING"

    CHANGED_SEVERITY = "CHANGED_SEVERITY"

    IDENTICAL = "IDENTICAL"


class CanaryResult(str, Enum):
    PROMOTE = "PROMOTE"

    REJECT = "REJECT"

    PENDING = "PENDING"

    AUTO_ROLLBACK = "AUTO_ROLLBACK"


@dataclass
class CanaryRun:
    run_id: str = field(default_factory=lambda: f"canary-{uuid.uuid4().hex[:8]}")

    v1_detector_id: str = ""

    v2_detector_id: str = ""

    v1_events: list[dict[str, object]] = field(default_factory=list)

    v2_events: list[dict[str, object]] = field(default_factory=list)

    comparison: dict[str, list[str]] = field(
        default_factory=lambda: {
            "NEW_FINDING": [],
            "LOST_FINDING": [],
            "CHANGED_SEVERITY": [],
            "IDENTICAL": [],
        }
    )

    run_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    result: CanaryResult = CanaryResult.PENDING

    review_required: bool = True


@dataclass
class CanaryConfig:
    state_dir: str = ""

    max_runs_before_review: int = 5

    fp_threshold: float = 2.0

    auto_approve_identical_rate: float = 0.95


_CANARY_STATE_FILE: str = "_canary_state.json"


CONFIG: Final[CanaryConfig] = CanaryConfig()


def _load_state() -> dict[str, object]:
    path = os.path.join(CONFIG.state_dir, _CANARY_STATE_FILE)

    if not path or not os.path.exists(path):
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            return json.loads(f.read())

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {}


def _save_state(state: dict[str, object]) -> None:
    if not CONFIG.state_dir:
        return

    os.makedirs(CONFIG.state_dir, exist_ok=True)

    path = os.path.join(CONFIG.state_dir, _CANARY_STATE_FILE)

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


def classify_event_id(
    v1_id: str,
    v2_ids: set[str],
    v1_events: list[dict[str, object]],
    v2_events: list[dict[str, object]],
    classification: dict[str, list[str]],
) -> None:
    """将单事件分类为NEW/LOST/CHANGED/IDENTICAL。"""

    v1_id_set: set[str] = {str(e.get("event_id", "")) for e in v1_events}

    v2_id_set: set[str] = {str(e.get("event_id", "")) for e in v2_events}

    for eid in v2_id_set - v1_id_set:
        classification["NEW_FINDING"].append(eid)

    for eid in v1_id_set - v2_id_set:
        classification["LOST_FINDING"].append(eid)

    v1_map: dict[str, dict[str, object]] = {str(e["event_id"]): e for e in v1_events if "event_id" in e}

    v2_map: dict[str, dict[str, object]] = {str(e["event_id"]): e for e in v2_events if "event_id" in e}

    for eid in v1_id_set & v2_id_set:
        v1_sev = str(v1_map.get(eid, {}).get("severity", ""))

        v2_sev = str(v2_map.get(eid, {}).get("severity", ""))

        if v1_sev != v2_sev and v1_sev and v2_sev:
            classification["CHANGED_SEVERITY"].append(f"{eid}: {v1_sev}->{v2_sev}")

        else:
            classification["IDENTICAL"].append(eid)


def run_canary(
    v1_detector_id: str,
    v2_detector_id: str,
    v1_run_fn: Callable[[], list[dict[str, object]]],
    v2_run_fn: Callable[[], list[dict[str, object]]],
) -> CanaryRun:
    """执行金丝雀运行：v1+v2独立运行，对比结果。"""

    cr = CanaryRun(
        v1_detector_id=v1_detector_id,
        v2_detector_id=v2_detector_id,
    )

    cr.v1_events = v1_run_fn()

    cr.v2_events = v2_run_fn()

    v1_ids: set[str] = set()

    v2_ids: set[str] = set()

    v1_id_set: set[str] = {str(e.get("event_id", "")) for e in cr.v1_events}

    v2_id_set: set[str] = {str(e.get("event_id", "")) for e in cr.v2_events}

    for eid, _evt_data in ((eid, {"v1": None, "v2": None}) for eid in v2_id_set - v1_id_set):
        cr.comparison["NEW_FINDING"].append(eid)

    for eid, _evt_data in ((eid, {"v1": None, "v2": None}) for eid in v1_id_set - v2_id_set):
        cr.comparison["LOST_FINDING"].append(eid)

    common = v1_id_set & v2_id_set

    cr.comparison["IDENTICAL"] = list(common)

    for eid in common:
        pass

    new_count = len(cr.comparison["NEW_FINDING"])

    total = max(len(cr.v1_events), 1)

    fp_rate = new_count / total

    if fp_rate > CONFIG.fp_threshold * 0.1:
        cr.result = CanaryResult.AUTO_ROLLBACK

    elif new_count == 0 and len(cr.comparison["LOST_FINDING"]) == 0:
        cr.review_required = False

        cr.result = CanaryResult.PROMOTE

    else:
        cr.result = CanaryResult.PENDING

    _save_state(cr.__dict__)

    return cr


def promote_detector(canary_run: CanaryRun) -> bool:
    """Owner审查通过后将v2全量切换。"""

    if canary_run.result is CanaryResult.AUTO_ROLLBACK:
        return False

    canary_run.result = CanaryResult.PROMOTE

    state = _load_state()

    state.setdefault("promoted", []).append(
        {
            "v1": canary_run.v1_detector_id,
            "v2": canary_run.v2_detector_id,
            "promoted_at": datetime.now(UTC).isoformat(),
        }
    )

    _save_state(state)

    return True


def rollback_detector(canary_run: CanaryRun, reason: str = "") -> bool:
    """回退v2，恢复v1。"""

    canary_run.result = CanaryResult.AUTO_ROLLBACK

    state = _load_state()

    state.setdefault("rollbacks", []).append(
        {
            "v2": canary_run.v2_detector_id,
            "rolled_back_at": datetime.now(UTC).isoformat(),
            "reason": reason or "FP rate exceeded threshold",
        }
    )

    _save_state(state)

    return True


def get_canary_history(detector_id: str | None = None) -> list[dict[str, object]]:
    """获取指定检测器的金丝雀历史。"""

    state = _load_state()

    runs = state.get("runs", [])

    if detector_id:
        return [r for r in runs if str(r.get("detector_id", "")) == detector_id]

    return runs
