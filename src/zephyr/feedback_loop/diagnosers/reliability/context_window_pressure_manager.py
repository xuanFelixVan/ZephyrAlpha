# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.context_window_pressure_manager
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_context_window_pressure_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R506: ContextWindowPressureManager
上下文窗口压力主动预防 — 检测压力/压缩/优先级排序
对标: Anthropic Context Engineering Guide — proactive capacity management
"""

import time
from dataclasses import dataclass, field


@dataclass
class ContextEntry:
    content: str
    priority: float
    timestamp: float
    source: str
    token_estimate: int


@dataclass
class ContextWindowPressureManager:
    entries: list[ContextEntry] = field(default_factory=list)
    max_window_tokens: int = 8000
    pressure_threshold: float = 0.7
    max_entries: int = 100
    compress_ratio: float = 0.5

    def add_entry(self, content: str, priority: float, source: str, token_estimate: int) -> None:
        self.entries.append(
            ContextEntry(
                content=content,
                priority=priority,
                timestamp=time.time(),
                source=source,
                token_estimate=token_estimate,
            )
        )
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

    def check_pressure(self) -> dict:
        total_tokens = sum(e.token_estimate for e in self.entries)
        usage_ratio = total_tokens / self.max_window_tokens

        status = "normal"
        if usage_ratio >= 0.9:
            status = "critical"
        elif usage_ratio >= self.pressure_threshold:
            status = "pressured"

        return {
            "status": status,
            "total_tokens": total_tokens,
            "window_max": self.max_window_tokens,
            "usage_ratio": round(usage_ratio, 3),
            "entry_count": len(self.entries),
            "needs_compression": usage_ratio >= self.pressure_threshold,
        }

    def compress(self) -> int:
        remaining_tokens = sum(e.token_estimate for e in self.entries)
        if remaining_tokens <= self.max_window_tokens * self.pressure_threshold:
            return 0

        self.entries.sort(key=lambda e: (e.priority, e.timestamp), reverse=True)

        kept = []
        kept_tokens = 0
        removed_count = 0
        for entry in self.entries:
            if kept_tokens + entry.token_estimate <= self.max_window_tokens * self.compress_ratio:
                kept.append(entry)
                kept_tokens += entry.token_estimate
            else:
                removed_count += 1

        self.entries = kept
        return removed_count

    def prioritize(self) -> None:
        self.entries.sort(key=lambda e: (e.priority, e.timestamp), reverse=True)
        total = 0
        kept = []
        for entry in self.entries:
            if total + entry.token_estimate <= self.max_window_tokens:
                kept.append(entry)
                total += entry.token_estimate
        self.entries = kept

    def get_summary(self) -> dict:
        sources = {}
        for e in self.entries:
            sources[e.source] = sources.get(e.source, 0) + e.token_estimate
        return {
            "total_entries": len(self.entries),
            "total_tokens": sum(e.token_estimate for e in self.entries),
            "avg_priority": round(sum(e.priority for e in self.entries) / max(len(self.entries), 1), 2),
            "by_source": sources,
        }
