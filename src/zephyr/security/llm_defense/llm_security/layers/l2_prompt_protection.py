# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l2_prompt_protection
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l2_prompt_protection
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LeakScanResult:
    """prompt 泄露扫描结果。"""

    is_safe: bool
    leak_hits: list[str] = field(default_factory=list)


# 泄露检测模式（用户试图套出 system prompt）
_LEAK_PATTERNS = [
    r"show\s+me\s+your\s+system\s+prompt",
    r"reveal\s+your\s+(system\s+)?prompt",
    r"your\s+(hidden|secret)\s+instructions",
    r"output\s+your\s+prompt",
    r"what\s+is\s+your\s+prompt",
    r"tell\s+me\s+your\s+prompt",
    r"repeat\s+your\s+system\s+message",
    r"print\s+your\s+instructions",
    r"show\s+me\s+your\s+prompt",
    r"show\s+me\s+your\s+instructions",
    r"your\s+system\s+instructions",
    r"what\s+are\s+your\s+(system\s+)?instructions",
    r"repeat\s+your\s+(initial\s+)?instructions",
]

# 探测模式
_PROBING_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"tell\s+me\s+your\s+prompt",
    r"reveal\s+your\s+(system|instructions)",
    r"what\s+are\s+your\s+rules",
    r"jailbreak",
    r"override\s+(your\s+)?(rules|restrictions)",
    r"what\s+are\s+your\s+(system\s+)?instructions",
    r"show\s+me\s+your\s+prompt",
]

# 禁止话题
_DISALLOWED_TOPICS = [
    r"hack\s+(into|a|the)",
    r"exploit",
    r"malware",
    r"ransomware",
    r"phishing",
    r"create\s+a\s+virus",
    r"ddos",
    r"sql\s+injection",
    r"social\s+engineering\s+attack",
    r"bypass\s+authentication",
    r"crack\s+(passwords|a\s+password)",
]


class PromptProtectionLayer:
    """L2 Prompt 保护层：安全构建 + 泄露扫描 + 探测检测 + 话题边界。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def build_safe_prompt(
        self,
        system: str = "",
        user_input: str = "",
        history: str = "",
        external_data: str = "",
    ) -> str:
        parts = []
        if system:
            parts.append(f"<!-- BEGIN SYSTEM -->\n{system}\n<!-- END SYSTEM -->")
        if history:
            parts.append(f"<!-- BEGIN HISTORY -->\n{history}\n<!-- END HISTORY -->")
        if external_data:
            parts.append(f"<!-- BEGIN EXTERNAL_DATA -->\n{external_data}\n<!-- END EXTERNAL_DATA -->")
        parts.append(f"<!-- BEGIN USER_INPUT -->\n{user_input}\n<!-- END USER_INPUT -->")
        return "\n\n".join(parts)

    def scan_for_leak(self, text: str) -> LeakScanResult:
        lowered = (text or "").lower()
        hits = [p for p in _LEAK_PATTERNS if re.search(p, lowered, re.IGNORECASE)]
        return LeakScanResult(is_safe=len(hits) == 0, leak_hits=hits)

    def detect_prompt_probing(self, text: str) -> list[str]:
        lowered = (text or "").lower()
        return [p for p in _PROBING_PATTERNS if re.search(p, lowered, re.IGNORECASE)]

    def check_topic_boundary(self, text: str) -> list[str]:
        lowered = (text or "").lower()
        return [p for p in _DISALLOWED_TOPICS if re.search(p, lowered, re.IGNORECASE)]

    def layer_name(self) -> str:
        return "l2_prompt_protection"

    def layer_index(self) -> int:
        return 2

    async def evaluate(self, ctx: Any) -> Any:
        """评估 prompt 安全：泄露尝试 -> DENY。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        raw = getattr(ctx, "raw_input", "") or ""
        leak = self.scan_for_leak(raw)
        if not leak.is_safe:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="prompt leak attempt detected",
                layer_name="l2_prompt_protection",
                score=0.0,
                details={"leak_hits": len(leak.leak_hits)},
            )
        probing = self.detect_prompt_probing(raw)
        if len(probing) > 0:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="prompt probing detected",
                layer_name="l2_prompt_protection",
                score=0.2,
                details={"probing_hits": len(probing)},
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="prompt safe",
            layer_name="l2_prompt_protection",
            score=1.0,
        )

    # 兼容旧接口
    def validate(self, prompt):
        return True

    def sanitize(self, prompt):
        return prompt

    def check_injection(self, text):
        return not self.scan_for_leak(text).is_safe
