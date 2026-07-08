# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.events
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] behavioral_auditor包内所有模块
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 事件定义不可修改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] 定义所有漂移事件类型
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-005 — ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义.

ARCH-034 P3 改名说明（防 AI 重新造轮子）：
  本模块的 DriftState/DriftEvent 已改名为 ManagedDriftState/ManagedDriftEvent，
  与 drift_models.py 的 DriftState(10态)/DriftEvent(12字段 dataclass) 区分。

  两套数据类的职责分工（刚进项目的 AI 必读）：
  - ManagedDriftState(4态)/ManagedDriftEvent(9字段 BaseModel) — 本模块
    用途：G-CT-005 管理事件的漂移状态机（DETECTED->FIXED/MANUAL_REQUIRED/IGNORED）
    消费者：rule_enforcement/drift_detector, infrastructure/rollback/drift_fix 等
  - DriftState(10态)/DriftEvent(12字段 dataclass) — drift_models.py（canonical 真源）
    用途：drift_engine 扫描结果的漂移事件数据载体
    包级 `from drift_detection import DriftState/DriftEvent` 路由到 drift_models canonical 版本

  DriftType(5值) 未改名——本模块是其唯一定义源，无同名冲突。
  model_drift_monitor 的 DriftType(3值) 已改名 ModelDriftType（ARCH-034 P3 批B）。
"""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class DriftType(str, Enum):
    CODE_DIVERGENCE = "CODE_DIVERGENCE"

    CONFIG_DRIFT = "CONFIG_DRIFT"

    SCHEMA_DRIFT = "SCHEMA_DRIFT"

    DEPENDENCY_DRIFT = "DEPENDENCY_DRIFT"

    INTERFACE_DRIFT = "INTERFACE_DRIFT"


class ManagedDriftState(str, Enum):
    DETECTED = "DETECTED"

    FIXED = "FIXED"

    MANUAL_REQUIRED = "MANUAL_REQUIRED"

    IGNORED = "IGNORED"


class ManagedDriftEvent(BaseModel):
    drift_id: str

    detected_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    target: str

    drift_type: DriftType = DriftType.CODE_DIVERGENCE

    fix_suggestion: str = ""

    auto_fixable: bool = False

    state: ManagedDriftState = ManagedDriftState.DETECTED

    agent_id: str = ""

    severity: str = "MEDIUM"

    def mark_fixed(self) -> None:
        self.state = ManagedDriftState.FIXED

    def mark_manual_required(self) -> None:
        self.state = ManagedDriftState.MANUAL_REQUIRED
