# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.broker_resilience
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: broker_resilience.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: BrokerLevel, BrokerFailure
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: BrokerLevel, BrokerFailure
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class BrokerLevel(str, Enum):
    P0_PRIMARY = "P0"
    P1_FALLBACK = "P1"
    P2_EMERGENCY = "P2"


class BrokerFailure(str, Enum):
    API_LOST = "API_LOST"
    REJECT_ERROR = "REJECT_ERROR"
    GAP_FILL = "GAP_FILL"
    EXCHANGE_HALT = "EXCHANGE_HALT"


BROKER_FAILOVER: Final[dict[BrokerLevel, str]] = {
    BrokerLevel.P0_PRIMARY: "主API Primary",
    BrokerLevel.P1_FALLBACK: "自动故障转移 P1",
    BrokerLevel.P2_EMERGENCY: "应急平仓 only",
}

EMERGENCY_LIQUIDATION_STEPS: Final[list[str]] = [
    "检测P0故障>容忍(90sP0/120sP1)",
    "简报Owner(new pending L0+unique brief)",
    "P2 20% Exposure->每15min再降20%",
    "P0恢复->5min转P0 / 未恢复->Owner 3×Go/No-go",
]
