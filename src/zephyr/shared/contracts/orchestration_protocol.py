# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.orchestration_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.rollback; zephyr.governance.ops_governance; zephyr.infrastructure.rollback; zephyr.orchestrator.chaos_hooks; zephyr.orchestrator.batch_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Protocol MUST NOT import from zephyr.trading; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; all consumers
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError when orchestration layer unavailable; consumers MUST handle
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo 参数
#   fields: 参数 repo，类型注解 object
#   code: orchestration_protocol.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: batch_id 参数
#   fields: 参数 batch_id，类型注解 str
#   code: orchestration_protocol.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: worker_id 参数
#   fields: 参数 worker_id，类型注解 str
#   code: orchestration_protocol.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ShadowCanaryProtocol
#   name_en: ShadowCanaryProtocol
#   intro: Shadow canary deployment protocol - decouples D-RES/D-GOV f…
#   desc: Shadow canary deployment protocol - decouples D-RES/D-GOV from D-ORCH.；公共方法（定义序）: shadow, promote；源码 L110-L115
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ChaosEngineProtocol
#   name_en: ChaosEngineProtocol
#   intro: Chaos fault injection engine protocol - decouples D-RES/D-G…
#   desc: Chaos fault injection engine protocol - decouples D-RES/D-GOV from D-ORCH.；公共方法（定义序）: get_injection_points, i…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ BatchOrchestratorProtocol
#   name_en: BatchOrchestratorProtocol
#   intro: Batch task orchestrator protocol - decouples D-RES/D-GOV fr…
#   desc: Batch task orchestrator protocol - decouples D-RES/D-GOV from D-ORCH.；公共方法（定义序）: claim_next, mark_done, mark_…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ create_shadow_canary
#   name_en: create_shadow_canary
#   intro: create_shadow_canary() 源码 L154-L157
#   desc: 源码 L154-L157
#   inputs: 无参数
#   outputs: ShadowCanaryProtocol
# - id: A5
#   name_zh: ⑤ create_chaos_engine
#   name_en: create_chaos_engine
#   intro: create_chaos_engine() 源码 L160-L163
#   desc: 源码 L160-L163
#   inputs: 无参数
#   outputs: ChaosEngineProtocol
# - id: A6
#   name_zh: ⑥ create_batch_orchestrator
#   name_en: create_batch_orchestrator
#   intro: create_batch_orchestrator(repo, batch_id, worker_id)…
#   desc: 源码 L166-L169
#   inputs: repo batch_id worker_id
#   outputs: BatchOrchestratorProtocol
# 层: 输出
# - id: O1
#   name_zh: ShadowCanaryProtocol
#   name_en: ShadowCanaryProtocol
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.rollback; zephyr.governance.ops_governance; zephyr.infras…
# - id: O2
#   name_zh: ChaosEngineProtocol
#   name_en: ChaosEngineProtocol
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.rollback; zephyr.governance.ops_governance; zephyr.infras…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import importlib
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ShadowCanaryProtocol(Protocol):
    """Shadow canary deployment protocol - decouples D-RES/D-GOV from D-ORCH."""

    def shadow(self, strategy: str, context: str) -> object: ...

    def promote(self, result: object) -> bool: ...


@runtime_checkable
class ChaosEngineProtocol(Protocol):
    """Chaos fault injection engine protocol - decouples D-RES/D-GOV from D-ORCH."""

    def get_injection_points(self) -> list[dict[str, Any]]: ...

    def inject(self, injection_type_or_point: str = "", **kwargs: Any) -> object: ...

    def recover(self, target: str = "") -> object: ...

    def verify(self, target: str = "") -> object: ...

    def cleanup(self) -> None: ...

    def fault_inject(self, target: str, fault_type: str, params: dict[str, Any] | None = None) -> object: ...

    def get_active_faults(self) -> list[Any]: ...

    def is_healthy(self) -> bool: ...


@runtime_checkable
class BatchOrchestratorProtocol(Protocol):
    """Batch task orchestrator protocol - decouples D-RES/D-GOV from D-ORCH."""

    def claim_next(self) -> object | None: ...

    def mark_done(self, task_id: str) -> None: ...

    def mark_failed(self, task_id: str, reason: str = "") -> None: ...

    def recover_stale_claims(self) -> int: ...

    def progress(self) -> object: ...


def create_shadow_canary() -> ShadowCanaryProtocol:
    _mod = importlib.import_module("zephyr.autonomy_core.shadow_canary")
    _ShadowCanary = _mod.ShadowCanary
    return _ShadowCanary()


def create_chaos_engine() -> ChaosEngineProtocol:
    _mod = importlib.import_module("zephyr.orchestrator.fault_tolerance.chaos_engine")
    _ChaosEngine = _mod.ChaosEngine
    return _ChaosEngine()


def create_batch_orchestrator(repo: object, batch_id: str, worker_id: str, **kwargs: Any) -> BatchOrchestratorProtocol:
    _mod = importlib.import_module("zephyr.orchestrator.execution.batch_orchestrator")
    _BatchOrchestrator = _mod.BatchOrchestrator
    return _BatchOrchestrator(repo, batch_id, worker_id, **kwargs)
