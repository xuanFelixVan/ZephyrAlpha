# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.feedback_delay_compensator
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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

"""
Feedback Delay Compensator — v0.38.0 R477

Blindspot: Many FLE actions have delayed effects — config changes take minutes
to propagate, model retraining takes hours, market impact takes days. FLE
re-acts during the delay window, creating cascading overcorrections.

Risk: R477 — Smith predictor problem: FLE sees no improvement after action,
assumes action failed, dispatches stronger action -> overshoot -> oscillation.

Mitigation: Track per-action-type expected effect latency. During delay window,
suppress anomaly detection for the target metric. Use predicted trajectory
(Smith predictor) to compare actual vs expected path after delay expires.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: feedback_delay_compensator.py
# 层: 算法
# - id: A1
#   name_zh: ① FeedbackDelayCompensator
#   name_en: FeedbackDelayCompensator
#   intro: class FeedbackDelayCompensator 源码 L74-L163
#   desc: 公共方法（定义序）: register_action_delay, dispatch_with_delay, should_suppress, evaluate_delayed_outcome, get_pending…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: FeedbackDelayCompensator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DelayState(str, Enum):
    IDLE = "IDLE"
    WAITING = "WAITING"
    EVALUATING = "EVALUATING"


@dataclass
class FeedbackDelayCompensator:
    default_delay: float = 300.0
    max_delay: float = 86400.0

    action_delay_map: dict[str, float] = field(default_factory=dict)
    pending_actions: dict[str, dict] = field(default_factory=dict)
    delay_violations: list[dict] = field(default_factory=list)

    def register_action_delay(self, action_type: str, expected_delay_seconds: float) -> None:
        self.action_delay_map[action_type] = min(expected_delay_seconds, self.max_delay)

    def dispatch_with_delay(
        self, action_id: str, action_type: str, target_metric: str, pre_action_value: float
    ) -> dict:
        delay = self.action_delay_map.get(action_type, self.default_delay)
        suppressed_until = time.time() + delay

        self.pending_actions[action_id] = {
            "type": action_type,
            "target_metric": target_metric,
            "pre_action_value": pre_action_value,
            "dispatched_at": time.time(),
            "suppressed_until": suppressed_until,
            "delay": delay,
            "state": DelayState.WAITING,
        }

        return {
            "action_id": action_id,
            "suppressed_until": suppressed_until,
            "delay_seconds": delay,
            "instruction": f"suppress_{target_metric}_anomalies_until_{suppressed_until:.0f}",
        }

    def should_suppress(self, metric_name: str) -> dict:
        now = time.time()
        for aid, action in list(self.pending_actions.items()):
            if action["target_metric"] == metric_name and action["state"] is DelayState.WAITING:
                if now < action["suppressed_until"]:
                    remaining = action["suppressed_until"] - now
                    return {"suppress": True, "action_id": aid, "remaining_seconds": round(remaining, 1)}
                else:
                    action["state"] = DelayState.EVALUATING
        return {"suppress": False}

    def evaluate_delayed_outcome(self, action_id: str, current_value: float) -> dict:
        action = self.pending_actions.get(action_id)
        if not action:
            return {"error": "unknown_action"}

        action["state"] = DelayState.IDLE
        pre = action["pre_action_value"]
        expected_direction = 1.0 if pre < 0 else -1.0
        delta = current_value - pre
        effective = (delta * expected_direction) > 0

        if not effective and abs(delta) > abs(pre) * 0.1:
            self.delay_violations.append(
                {
                    "action_id": action_id,
                    "action_type": action["type"],
                    "expected_delay": action["delay"],
                    "actual_delta": round(delta, 4),
                }
            )

        return {
            "action_id": action_id,
            "effective": effective,
            "pre_value": round(pre, 4),
            "post_value": round(current_value, 4),
            "delta": round(delta, 4),
            "recommendation": "escalate_tuning" if not effective else "update_delay_estimate",
        }

    def get_pending_summary(self) -> list[dict]:
        return [
            {
                "id": aid,
                "target": a["target_metric"],
                "remaining_s": round(max(0, a["suppressed_until"] - time.time()), 1),
            }
            for aid, a in self.pending_actions.items()
            if a["state"] is DelayState.WAITING
        ]

    def cleanup_completed(self) -> int:
        before = len(self.pending_actions)
        self.pending_actions = {aid: a for aid, a in self.pending_actions.items() if a["state"] is not DelayState.IDLE}
        return before - len(self.pending_actions)
