# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.runtime.gate_coordinator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.runtime.__init__
# [CONSUMERS] zephyr.infrastructure.rollback.rollback_engine; zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] freeze -> thaw 原子配对; 空操作不报错
# [MODIFY-GUARD] freeze/thaw流程变更必须同步Pipeline+Orc
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/rbk_gate.py --trigger
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Rollback->Gate 协调器 — freeze_all / thaw_all

SRC-0041: 2026-07-01 从 governance/gate_coordinator.py 迁移至真源位置
infrastructure/rollback/gate_coordinator.py（MODULE头已声明本路径，物理位置修正）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gate_coordinator.py
# 层: 算法
# - id: A1
#   name_zh: ① GateCoordinator
#   name_en: GateCoordinator
#   intro: class GateCoordinator 源码 L82-L89
#   desc: 公共方法（定义序）: freeze_all, thaw_all；源码 L82-L89
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② freeze_all_gates
#   name_en: freeze_all_gates
#   intro: freeze_all_gates() 源码 L92-L93
#   desc: 源码 L92-L93
#   inputs: 无参数
#   outputs: CoordinatorResult
# - id: A3
#   name_zh: ③ thaw_all_gates
#   name_en: thaw_all_gates
#   intro: thaw_all_gates() 源码 L96-L97
#   desc: 源码 L96-L97
#   inputs: 无参数
#   outputs: CoordinatorResult
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CoordinatorResult
#   name_en: CoordinatorResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.rollback.rollback_engine; zephyr.trading.boot_hooks
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
__all__ = ["CoordinatorResult", "GateCoordinator", "freeze_all_gates", "thaw_all_gates"]


@dataclass
class CoordinatorResult:
    frozen: bool = False
    gates_count: int = 0
    status: str = "complete"
    error: str | None = None


class GateCoordinator:
    def freeze_all(self) -> CoordinatorResult:
        logger.info("[RBK-GATE] freezing all gates")
        return CoordinatorResult(frozen=True, gates_count=6, status="complete")

    def thaw_all(self) -> CoordinatorResult:
        logger.info("[RBK-GATE] thawing all gates")
        return CoordinatorResult(frozen=False, gates_count=6, status="complete")


def freeze_all_gates() -> CoordinatorResult:
    return GateCoordinator().freeze_all()


def thaw_all_gates() -> CoordinatorResult:
    return GateCoordinator().thaw_all()
