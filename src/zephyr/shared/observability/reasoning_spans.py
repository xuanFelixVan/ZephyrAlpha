# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.observability.reasoning_spans
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.feedback_loop.__init___from_obs
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: reasoning_spans.py
# 层: 算法
# - id: A1
#   name_zh: ① ReasoningSpan
#   name_en: ReasoningSpan
#   intro: class ReasoningSpan 源码 L63-L74
#   desc: 公共方法（定义序）: duration_ms；源码 L63-L74
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ReasoningSpans
#   name_en: ReasoningSpans
#   intro: class ReasoningSpans 源码 L77-L94
#   desc: 公共方法（定义序）: start, end, get_trace；源码 L77-L94
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ReasoningSpan, ReasoningSpans
#   downstream: zephyr.feedback_loop.__init___from_obs
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ReasoningSpan:
    span_id: str
    operation: str
    start_time: float
    end_time: float = 0.0
    parent_id: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000


class ReasoningSpans:
    def __init__(self):
        self._spans: list[ReasoningSpan] = []

    def start(self, operation: str, parent_id: str = "", **metadata: str) -> ReasoningSpan:
        span = ReasoningSpan(str(uuid.uuid4())[:8], operation, time.time(), parent_id=parent_id, metadata=metadata)
        self._spans.append(span)
        return span

    def end(self, span_id: str) -> ReasoningSpan | None:
        for s in self._spans:
            if s.span_id == span_id:
                s.end_time = time.time()
                return s
        return None

    def get_trace(self, root_span_id: str) -> list[ReasoningSpan]:
        return [s for s in self._spans if s.span_id == root_span_id or s.parent_id == root_span_id]
