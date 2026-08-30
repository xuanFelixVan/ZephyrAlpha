# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.offline_resilience
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md;src/zephyr/infrastructure/runtime_integration/a2a_protocol/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: offline_resilience.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: TIFLevel
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: TIFLevel
#   downstream: MOD-INF-027;MOD-INF-018;MOD-INF-022
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class TIFLevel(str, Enum):
    L1 = "L1_<5m"
    L2 = "L2_5-30m"
    L3 = "L3_30m-4h"
    L4 = "L4_4-24h"
    L5 = "L5_24h+"


DECAY_START_HOURS: int = 8
DECAY_RATE_PER_24H: float = 0.25
MAX_DECAY_HOURS: int = 72

E2E_TARGET_MS: int = 460
E2E_BUDGET_BREAKDOWN_MS: dict[str, int] = {
    "MARKETDATA": 405,
    "SIGNAL": 1000,
    "RISK": 50,
}
