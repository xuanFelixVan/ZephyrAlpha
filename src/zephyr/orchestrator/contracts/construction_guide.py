# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.contracts.construction_guide
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_construction_guide | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
施工指南引擎（Construction Guide）

依据：MOD-MASTER-002 蓝图 §八 施工指南
实现 CT-* mock 策略 + Phase 0 context check 强制执行。

策略：
1. Phase A->D 每个 CT-* 的 mock 实现策略（stub/partial/full）
2. 禁止未完成 Phase 0 context check 进入后续 Phase
3. Mock 模式：开发环境使用 cheap_fast 模型、低 token 预算、跳过飞书通知
"""

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel


class MockStrategy(str, Enum):
    STUB = "stub"
    PARTIAL = "partial"
    FULL = "full"


MOCK_STRATEGIES: Final[dict[str, MockStrategy]] = {
    "CT-ORC-SCRIPT-001": MockStrategy.PARTIAL,
    "CT-ORC-CE-001": MockStrategy.STUB,
    "CT-ORC-VMS-001": MockStrategy.FULL,
    "CT-ORC-GATE-001": MockStrategy.PARTIAL,
    "CT-SCRIPT-KB-001": MockStrategy.STUB,
    "CT-SCRIPT-GATE-001": MockStrategy.PARTIAL,
    "CT-CE-VMS-001": MockStrategy.FULL,
    "CT-CE-LSG-001": MockStrategy.STUB,
    "CT-KB-VMS-001": MockStrategy.FULL,
    "CT-FLE-ORC-001": MockStrategy.STUB,
    "CT-FLE-DB-001": MockStrategy.STUB,
    "CT-TELE-FLE-001": MockStrategy.STUB,
    "CT-PIPE-ORC-001": MockStrategy.PARTIAL,
    "CT-HEALTH": MockStrategy.STUB,
    "CT-CBAC": MockStrategy.STUB,
    "CT-CDC": MockStrategy.STUB,
    "CT-CONFIG": MockStrategy.PARTIAL,
    "CT-FEATUREFLAG": MockStrategy.PARTIAL,
    "CT-CHAOS": MockStrategy.STUB,
    "CT-RECONCILE": MockStrategy.STUB,
    "CT-STARTUP": MockStrategy.STUB,
    "CT-TEARDOWN": MockStrategy.STUB,
    "CT-MODEL-REGISTRY": MockStrategy.PARTIAL,
    "CT-DEPS": MockStrategy.PARTIAL,
    "CT-KNOWLEDGE-FRESHNESS": MockStrategy.STUB,
    "CT-HOUSEKEEPING": MockStrategy.PARTIAL,
    "CT-SESSION-handoff": MockStrategy.PARTIAL,
    "CT-STABILITY": MockStrategy.STUB,
    "CT-CANARY": MockStrategy.STUB,
    "CT-INCIDENT": MockStrategy.STUB,
    "CT-RACE-CONDITIONS": MockStrategy.STUB,
    "CT-COST-BUDGET": MockStrategy.PARTIAL,
    "CT-DISK-GUARD": MockStrategy.STUB,
    "CT-NETWORK-PARTITION": MockStrategy.STUB,
    "CT-BENCH": MockStrategy.STUB,
    "CT-DEPLOY": MockStrategy.STUB,
    "CT-SCHEMA-MIGRATE": MockStrategy.STUB,
    "CT-DEGRADE-CASCADE": MockStrategy.STUB,
    "CT-AUTONOMY": MockStrategy.PARTIAL,
    "CT-AGENT-QUALITY": MockStrategy.PARTIAL,
    "CT-PROMPT-VERSION": MockStrategy.PARTIAL,
    "CT-SESSION-CONFLICT": MockStrategy.STUB,
    "CT-LEAN": MockStrategy.STUB,
    "CT-BLUEPRINT-HEALTH": MockStrategy.PARTIAL,
    "CT-TRANSFER": MockStrategy.STUB,
    "CT-KE-QUALITY": MockStrategy.STUB,
    "CT-DLQ": MockStrategy.STUB,
    "CT-BACKUP": MockStrategy.STUB,
    "CT-BULKHEAD": MockStrategy.PARTIAL,
    "CT-WATCHDOG": MockStrategy.STUB,
    "CT-SLO": MockStrategy.STUB,
    "CT-SECRETS": MockStrategy.PARTIAL,
    "CT-DATA-LIFECYCLE": MockStrategy.STUB,
}


class ConstructionMode(str, Enum):
    DEV = "dev"
    PROD = "prod"


class ConstructionConfig(BaseModel):
    mode: ConstructionMode = ConstructionMode.DEV
    cheap_model: str = "deepseek-chat"
    token_budget: int = 500
    skip_feishu: bool = True
    phase0_check_required: bool = True


class ConstructionGuide:
    def __init__(self, mode: ConstructionMode = ConstructionMode.DEV):
        self._config = ConstructionConfig(mode=mode)

    @property
    def config(self) -> ConstructionConfig:
        return self._config

    def get_mock_strategy(self, contract_id: str) -> MockStrategy:
        return MOCK_STRATEGIES.get(contract_id, MockStrategy.STUB)

    def require_phase0_context_check(self) -> bool:
        return self._config.phase0_check_required

    def is_dev_mode(self) -> bool:
        return self._config.mode is ConstructionMode.DEV
