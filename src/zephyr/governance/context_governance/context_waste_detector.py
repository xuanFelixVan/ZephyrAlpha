# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_waste_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_context 参数
#   fields: 参数 max_context（无注解）
#   code: context_waste_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: waste_threshold 参数
#   fields: 参数 waste_threshold（无注解）
#   code: context_waste_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContextWasteDetector
#   name_en: ContextWasteDetector
#   intro: class ContextWasteDetector 源码 L69-L130
#   desc: 公共方法（定义序）: feed, analyze, context_fill_ratio, reset；源码 L69-L130
#   inputs: max_context waste_threshold
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextWasteDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class WasteReport:
    wasted_tokens: int
    waste_ratio: float
    unique_content_ratio: float
    redundancy_score: float
    actionable: bool
    advice: str


class ContextWasteDetector:
    def __init__(self, max_context: int = 32000, waste_threshold: float = 0.5):
        self._max_context = max_context
        self._waste_threshold = waste_threshold
        self._seen_chunks: OrderedDict[str, int] = OrderedDict()
        self._total_tokens: int = 0

    def feed(self, context_text: str) -> None:
        chunk_size = 200
        total_len = len(context_text)
        for i in range(0, total_len, chunk_size):
            chunk = context_text[i : i + chunk_size]
            self._seen_chunks[chunk] = self._seen_chunks.get(chunk, 0) + 1
        self._total_tokens += total_len // 4
        while len(self._seen_chunks) > 500:
            self._seen_chunks.popitem(last=False)

    def analyze(self) -> WasteReport:
        if not self._seen_chunks:
            return WasteReport(
                wasted_tokens=0,
                waste_ratio=0.0,
                unique_content_ratio=1.0,
                redundancy_score=0.0,
                actionable=False,
                advice="无上下文数据",
            )

        total_chunks = sum(self._seen_chunks.values())
        unique_chunks = len(self._seen_chunks)
        unique_ratio = unique_chunks / total_chunks if total_chunks else 1.0

        duplicated = sum(c - 1 for c in self._seen_chunks.values() if c > 1)
        redundancy = duplicated / total_chunks if total_chunks else 0.0

        wasted = int(self._total_tokens * redundancy)
        actionable = redundancy > self._waste_threshold

        if redundancy > 0.7:
            advice = "严重冗余: 建议 /compact 或重置对话"
        elif redundancy > 0.4:
            advice = "中度浪费: 建议摘要历史消息并截断"
        elif redundancy > 0.15:
            advice = "轻微重复: 监控中"
        else:
            advice = "上下文利用率良好"

        return WasteReport(
            wasted_tokens=wasted,
            waste_ratio=redundancy,
            unique_content_ratio=unique_ratio,
            redundancy_score=redundancy,
            actionable=actionable,
            advice=advice,
        )

    def context_fill_ratio(self) -> float:
        return self._total_tokens / self._max_context if self._max_context else 0.0

    def reset(self) -> None:
        self._seen_chunks.clear()
        self._total_tokens = 0
