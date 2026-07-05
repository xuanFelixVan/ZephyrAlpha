# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_waste_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_context_waste_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
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
