# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.action_selector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Action Selector — FLE 动作优先级选择与连败熔断退役。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 诊断结果与动作执行反馈
#   fields: diagnosis；ActionRecord(action_type, success)
#   code: ActionSelector.select_action / record_result
# 层: 算法
# - id: A1
#   name_zh: 优先级顺序选动作
#   name_en: priority_order_selection
#   intro: 按 action_priority 顺序返回首个未退役 ActionType，全部退役则 None
#   code: ActionSelector.select_action
# - id: A2
#   name_zh: 连败熔断退役
#   name_en: consecutive_failure_retirement
#   intro: 同动作连败 >=3 次则退役 7 天，到期自动恢复
#   code: ActionSelector.record_result
# 层: 输出
# - id: O1
#   name_zh: 选中动作与执行分发
#   name_en: selected_action_dispatch
#   intro: 选中的 ActionType；execute_action 委托 protocol_adapter 分发执行
#   downstream: zephyr.feedback_loop.protocols.FeedbackProtocolAdapter.dispatch_action
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


@dataclass
class ActionRecord:
    action_type: ActionType
    timestamp: float
    success: bool


@dataclass
class ActionSelector:
    protocol_adapter: FeedbackProtocolAdapter
    action_priority: list[ActionType] = field(
        default_factory=lambda: [
            ActionType.NOTIFY_OWNER,
            ActionType.ADJUST_THRESHOLD,
            ActionType.REPAIR,
            ActionType.DEPLOY,
            ActionType.SELF_UPGRADE,
            ActionType.REBALANCE,
        ]
    )
    history: list[ActionRecord] = field(default_factory=list)
    retired_actions: dict[str, float] = field(default_factory=dict)
    consecutive_failures: dict[str, int] = field(default_factory=dict)
    RETIRE_SECONDS: int = 7 * 24 * 3600
    MAX_CONSECUTIVE_FAILURES: int = 3
    learning_rate: float = 0.1
    discount_factor: float = 0.9

    def select_action(self, diagnosis: object) -> ActionType | None:
        now = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        for at in self.action_priority:
            if at.value in self.retired_actions:
                if now - self.retired_actions[at.value] > self.RETIRE_SECONDS:
                    del self.retired_actions[at.value]
                else:
                    continue
            return at
        return None

    def record_result(self, action_type: ActionType, success: bool) -> None:
        record = ActionRecord(action_type=action_type, timestamp=time.time(), success=success)  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        self.history.append(record)
        if success:
            self.consecutive_failures[action_type.value] = 0
        else:
            self.consecutive_failures[action_type.value] = self.consecutive_failures.get(action_type.value, 0) + 1
            if self.consecutive_failures[action_type.value] >= self.MAX_CONSECUTIVE_FAILURES:
                self.retired_actions[action_type.value] = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
                self.consecutive_failures[action_type.value] = 0

    def execute_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
        return self.protocol_adapter.dispatch_action(action_type, payload)
