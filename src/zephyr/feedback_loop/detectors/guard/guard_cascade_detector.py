# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.guard_cascade_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
R520: GuardCascadeDetector
守卫触发级联检测与熔断 — G1->G2->G3->... 连锁反应

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: guard_cascade_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① GuardCascadeDetector
#   name_en: GuardCascadeDetector
#   intro: class GuardCascadeDetector 源码 L62-L116
#   desc: 公共方法（定义序）: record_trigger, detect_cascade, is_suppressed, clear_suppression；源码 L62-L116
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: GuardCascadeDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import time
from dataclasses import dataclass, field


@dataclass
class GuardTriggerEvent:
    guard_id: str
    triggered_by: str | None
    timestamp: float


@dataclass
class GuardCascadeDetector:
    trigger_history: list[GuardTriggerEvent] = field(default_factory=list)
    max_history: int = 300
    cascade_depth_threshold: int = 4
    cascade_window_seconds: float = 5.0
    suppressed_guards: set[str] = field(default_factory=set)

    def record_trigger(self, guard_id: str, triggered_by: str | None = None) -> None:
        self.trigger_history.append(
            GuardTriggerEvent(
                guard_id=guard_id,
                triggered_by=triggered_by,
                timestamp=time.time(),
            )
        )
        if len(self.trigger_history) > self.max_history:
            self.trigger_history = self.trigger_history[-self.max_history :]

    def detect_cascade(self) -> dict:
        now = time.time()
        recent = [e for e in self.trigger_history if now - e.timestamp < self.cascade_window_seconds]

        if len(recent) < self.cascade_depth_threshold:
            return {"cascade_detected": False, "depth": len(recent)}

        triggered_ids = [e.guard_id for e in recent]
        unique_triggered = []
        for gid in triggered_ids:
            if gid not in unique_triggered:
                unique_triggered.append(gid)

        is_cascade = len(unique_triggered) >= self.cascade_depth_threshold

        result = {
            "cascade_detected": is_cascade,
            "depth": len(unique_triggered),
            "triggered_guards": unique_triggered,
            "window_seconds": round(now - recent[0].timestamp, 3),
        }

        if is_cascade:
            downstream = unique_triggered[self.cascade_depth_threshold - 1 :]
            self.suppressed_guards.update(downstream)
            result["suppressed"] = list(downstream)

        return result

    def is_suppressed(self, guard_id: str) -> bool:
        return guard_id in self.suppressed_guards

    def clear_suppression(self, guard_id: str | None = None) -> None:
        if guard_id is None:
            self.suppressed_guards.clear()
        else:
            self.suppressed_guards.discard(guard_id)
