# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l1_input
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l1_input_defense
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(Enum):
    """输入来源类型。"""

    DIRECT = "direct_input"
    TOOL_RESULT = "tool_result"
    URL_CONTENT = "url_content"
    RAG_CONTENT = "rag_content"
    # 兼容旧别名
    USER = "direct_input"
    API = "direct_input"
    FILE = "tool_result"
    NETWORK = "url_content"
    MCP = "tool_result"
    AGENT = "tool_result"


@dataclass
class SanitizeResult:
    """sanitize_and_wrap 的返回结果。"""

    blocked: bool
    total_score: float
    # 5.107.4 修复: =None 改为 field(default_factory=list),消除类型注解与默认值不一致
    hits: list[str] = field(default_factory=list)


# 直接注入模式
_DIRECT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"disregard\s+(the\s+)?above",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"system\s+prompt",
    r"system\s+message",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"forget\s+(all|everything)",
    r"forget\s+(your\s+)?(rules|instructions)",
    r"new\s+instructions?\s*:",
    r"you\s+are\s+now\s+in\s+maintenance",
]

# 越狱模式
_JAILBREAK_PATTERNS = [
    r"dan\s+mode",
    r"you\s+are\s+(now\s+)?dan\b",
    r"unfiltered\s+bot",
    r"unrestricted",
    r"developer\s+mode",
    r"act\s+as\s+(an?\s+)?(dark|evil|unfiltered|unrestricted)",
    r"pretend\s+to\s+be",
    r"dark\s+persona",
    r"jailbreak",
    r"switch\s+to\s+(developer|admin)\s+mode",
    r"repeat\s+after\s+me",
    r"i\s+am\s+compromised",
    r"no\s+restrictions?",
    r"no\s+safety",
    r"bypass\s+all\s+safety",
]

# 间接注入模式（URL/工具结果）
_INDIRECT_INJECTION_PATTERNS = [
    r"data:text/html",
    r"<script",
    r"javascript:",
    r"ignore\s+previous",
    r"output\s+the\s+following",
    r"reveal\s+your\s+(system|instructions)",
]

# 零宽字符
_ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u200e", "\u200f", "\ufeff"]
_ZERO_WIDTH_RE = re.compile("[" + "".join(_ZERO_WIDTH_CHARS) + "]")

# 同形字映射（西里尔→拉丁）
_HOMOGLYPH_MAP = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "Х": "X", "і": "i", "ї": "i", "ё": "e",
    "0": "o",  # 数字0冒充o（仅在特定上下文）
}
_HOMOGLYPH_RE = re.compile("[" + "".join(re.escape(k) for k in _HOMOGLYPH_MAP if k.isalpha()) + "]")


class InputDefense:
    """兼容旧接口。"""

    def __init__(self, config=None):
        self.config = config or {}

    def validate(self, input_data):
        return True

    def sanitize(self, input_data):
        return input_data

    def check_injection(self, text):
        return len(re.findall("|".join(_DIRECT_INJECTION_PATTERNS), text, re.IGNORECASE)) > 0


class InputDefenseLayer:
    """L1 输入防御层：直接注入/越狱/间接注入检测 + 编码绕过防御。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._encoder = EncodingBypassDefender()
        self._tool_guard = ToolResultTransformGuard()

    def check_direct_injection(self, text: str) -> list[str]:
        lowered = text.lower()
        hits = []
        for pat in _DIRECT_INJECTION_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                hits.append(pat)
        return hits

    def check_indirect_content(self, text: str, source: SourceType) -> list[str]:
        lowered = text.lower()
        hits = []
        # URL 内容总是检查注入模式
        if source in (SourceType.URL_CONTENT, SourceType.NETWORK):
            for pat in _INDIRECT_INJECTION_PATTERNS:
                if re.search(pat, lowered, re.IGNORECASE):
                    hits.append(pat)
        # 工具结果也检查注入
        if source in (SourceType.TOOL_RESULT, SourceType.FILE, SourceType.MCP):
            for pat in _INDIRECT_INJECTION_PATTERNS + _DIRECT_INJECTION_PATTERNS[:3]:
                if re.search(pat, lowered, re.IGNORECASE):
                    hits.append(pat)
                    break
        return hits

    def check_jailbreak(self, text: str) -> list[str]:
        lowered = text.lower()
        hits = []
        for pat in _JAILBREAK_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                hits.append(pat)
        # 检查编码混淆（hex 转义的 ignore）
        if "\\x69\\x67\\x6e\\x6f\\x72\\x65" in text:
            hits.append("hex_obfuscation")
        return hits

    def sanitize_and_wrap(self, text: str, source: SourceType) -> SanitizeResult:
        direct_hits = self.check_direct_injection(text)
        jailbreak_hits = self.check_jailbreak(text)
        indirect_hits = self.check_indirect_content(text, source)
        encoding = self._encoder.scan(text)

        total_hits = len(direct_hits) + len(jailbreak_hits) + len(indirect_hits)
        if encoding["anomaly_count"] > 0:
            total_hits += encoding["anomaly_count"]

        # 评分：每个 hit 扣分
        total_score = max(0.0, 1.0 - total_hits * 0.15)
        # jailbreak 或 direct_injection 任何命中即阻断（高危类别不应依赖阈值）
        blocked = (
            len(jailbreak_hits) > 0
            or len(direct_hits) > 0
            or total_hits >= 3
            or total_score < 0.5
        )

        all_hits = direct_hits + jailbreak_hits + indirect_hits
        return SanitizeResult(blocked=blocked, total_score=total_score, hits=all_hits)

    def layer_name(self) -> str:
        return "l1_input"

    def layer_index(self) -> int:
        return 1

    async def evaluate(self, ctx: Any) -> Any:
        """评估输入安全：恶意注入 → DENY。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        raw = getattr(ctx, "raw_input", "") or ""
        meta = getattr(ctx, "metadata", {}) or {}
        src_str = meta.get("source_type", "direct_input")
        try:
            source = SourceType(src_str)
        except ValueError:
            source = SourceType.DIRECT

        result = self.sanitize_and_wrap(raw, source)
        if result.blocked:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="malicious input detected",
                layer_name="l1_input",
                score=result.total_score,
                details={"hits": len(result.hits)},
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="input clean",
            layer_name="l1_input",
            score=result.total_score,
        )

    # 兼容旧接口
    def validate(self, input_data):
        return True

    def sanitize(self, input_data):
        return input_data

    def check_injection(self, text):
        return len(self.check_direct_injection(text)) > 0


class EncodingBypassDefender:
    """编码绕过防御器：检测零宽字符 + 同形字混淆。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan(self, text: str) -> dict[str, Any]:
        zero_width = len(_ZERO_WIDTH_RE.findall(text))
        homoglyphs = len(_HOMOGLYPH_RE.findall(text))
        anomaly_count = zero_width + homoglyphs
        risk = "high" if anomaly_count >= 3 else ("medium" if anomaly_count > 0 else "low")
        return {
            "risk": risk,
            "anomaly_count": anomaly_count,
            "zero_width_count": zero_width,
            "homoglyph_count": homoglyphs,
        }

    def normalize_homoglyphs(self, text: str) -> str:
        result = text
        for cyr, lat in _HOMOGLYPH_MAP.items():
            if cyr.isalpha():
                result = result.replace(cyr, lat)
        return result

    def strip_zero_width(self, text: str) -> str:
        return _ZERO_WIDTH_RE.sub("", text)

    # 兼容旧接口
    def detect_encoding_attack(self, text: str):
        r = self.scan(text)
        return DefenseResult(passed=r["anomaly_count"] == 0, confidence=r["anomaly_count"] / 10)

    def normalize_encoding(self, text: str) -> str:
        return self.strip_zero_width(self.normalize_homoglyphs(text))


class ToolResultTransformGuard:
    """工具结果转换守卫：包裹分隔符 + 注入扫描。"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def wrap(self, content: str, source: str = "external") -> str:
        return (
            f"<!-- BEGIN EXTERNAL_TOOL_OUTPUT source={source} -->\n"
            f"{content}\n"
            f"<!-- END EXTERNAL_TOOL_OUTPUT -->"
        )

    def scan(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        hits = 0
        for pat in _DIRECT_INJECTION_PATTERNS + _INDIRECT_INJECTION_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                hits += 1
        risk = "high" if hits > 0 else "low"
        return {"hits_count": hits, "risk": risk}

    # 兼容旧接口
    def validate_tool_result(self, result: Any):
        r = self.scan(str(result))
        return DefenseResult(passed=r["hits_count"] == 0)

    def sanitize_tool_output(self, output: str) -> str:
        return output


class DefenseResult:
    """兼容旧接口的检测结果。"""

    def __init__(
        self,
        passed: bool = True,
        threat_type: str = "",
        confidence: float = 0.0,
        details: dict[str, Any] | None = None,
    ):
        self.passed = passed
        self.threat_type = threat_type
        self.confidence = confidence
        self.details = details or {}
