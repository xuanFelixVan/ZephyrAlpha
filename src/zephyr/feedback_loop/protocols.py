# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.protocols
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: protocols.py
# 层: 算法
# - id: A1
#   name_zh: ① FeedbackProtocolAdapter
#   name_en: FeedbackProtocolAdapter
#   intro: class FeedbackProtocolAdapter 源码 L67-L68
#   desc: 公共方法（定义序）: dispatch_action；源码 L67-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: FeedbackProtocolAdapter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from enum import Enum
from typing import Any, Protocol

# 治本（裁定#18 G8）：AgentCapability 原为桩类（name/level/description），与测试契约
# (agent_id/capabilities/version + Pydantic model_dump) 完全不符。现改为从
# zephyr.shared.contracts.protocols 重新导出正确的 Pydantic BaseModel 版本。
from zephyr.shared.contracts.protocols import AgentCapability  # noqa: F401 — re-export


class ActionType(str, Enum):
    NOTIFY_OWNER = "NOTIFY_OWNER"
    ADJUST_THRESHOLD = "ADJUST_THRESHOLD"
    REPAIR = "REPAIR"
    DEPLOY = "DEPLOY"
    SELF_UPGRADE = "SELF_UPGRADE"
    REBALANCE = "REBALANCE"


class FeedbackProtocolAdapter(Protocol):
    def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool: ...
