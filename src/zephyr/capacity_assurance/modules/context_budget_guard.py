"""
Context Budget Guard — Context 预算慢泄漏检测 (盲点 #17)
特性：
  - SLI CAP-CTX-001: Context 使用率 > 80% → WARNING, > 95% → CRITICAL
  - 水位线告警 + 自动截断建议
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


class ContextBudgetGuard:
    """
    Context 预算守护 (盲点 #17)
    """

    WARN_THRESHOLD = 0.80
    CRITICAL_THRESHOLD = 0.95
    SLI_ID = "CAP-CTX-001"

    def __init__(self, max_context_tokens: int = 128000):
        self.max_context_tokens = max_context_tokens

    def check(self, current_tokens: int) -> dict:
        usage = current_tokens / self.max_context_tokens
        level = "HEALTHY"
        if usage > self.CRITICAL_THRESHOLD:
            level = "CRITICAL"
        elif usage > self.WARN_THRESHOLD:
            level = "WARNING"

        return {
            "sli_id": self.SLI_ID,
            "current_tokens": current_tokens,
            "max_tokens": self.max_context_tokens,
            "usage_pct": round(usage * 100, 1),
            "level": level,
            "suggestion": "Consider truncation or summarization" if level != "HEALTHY" else "",
            "timestamp": time.time(),
        }
