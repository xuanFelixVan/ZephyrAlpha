# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.llm_security.layers.l1_input

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import base64
import codecs
import re
import unicodedata
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from zephyr.llm_security.patterns.injection_patterns import (
    PRECOMPILED_ENCODING,
    scan_direct,
    scan_encoding_escape,
    scan_indirect,
    scan_jailbreak,
    scan_path_traversal,
    scan_semantic_attacks,
    scan_shell,
    scan_sql,
)
from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class SourceType(str, Enum):
    DIRECT = "direct_input"
    RAG_CONTENT = "rag_content"
    FILE_CONTENT = "file_content"
    URL_CONTENT = "url_content"
    EMAIL_CONTENT = "email_content"
    TOOL_RESULT = "tool_result"


class DefenseResult(BaseModel):
    source_type: SourceType
    injection_hits: int = 0
    jailbreak_hits: int = 0
    encoding_anomalies: int = 0
    total_score: float = 1.0
    audit_log: List[Dict[str, Any]] = Field(default_factory=list)
    blocked: bool = False
    reason: str = ""


class InputDefenseLayer(LLMSecurityProtocol):
    """L1 输入防护层 —— 三层检测 + ToolResultTransform + 编码逃逸防御"""

    def __init__(self):
        self._input_sanitizer = None

    def layer_name(self) -> str:
        return "l1_input"

    def layer_index(self) -> int:
        return 1

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        source = SourceType(ctx.metadata.get("source_type", "direct_input"))
        defense = self.sanitize_and_wrap(ctx.raw_input, source)

        if defense.blocked:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=defense.reason,
                layer_name=self.layer_name(),
                score=0.0,
                details={"defense_result": defense.model_dump()},
            )

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason=f"L1 passed: score={defense.total_score:.2f}",
            layer_name=self.layer_name(),
            score=defense.total_score,
            details={"defense_result": defense.model_dump()},
        )

    def check_direct_injection(self, content: str) -> List[Dict[str, Any]]:
        return scan_direct(content)

    def check_indirect_content(self, content: str, source: SourceType) -> List[Dict[str, Any]]:
        hits = scan_indirect(content)
        if source == SourceType.URL_CONTENT:
            hits = [h for h in hits if h.get("channel") in ("url_payload",)]
        elif source == SourceType.EMAIL_CONTENT:
            hits = [h for h in hits if h.get("channel") in ("email_phishing",)]
        elif source == SourceType.FILE_CONTENT:
            hits = [h for h in hits if h.get("channel") in ("file_content_hijack",)]
        return hits

    def check_jailbreak(self, content: str) -> List[Dict[str, Any]]:
        return scan_jailbreak(content)

    def sanitize_and_wrap(self, content: str, source: SourceType) -> DefenseResult:
        direct_hits = self.check_direct_injection(content)
        indirect_hits = self.check_indirect_content(content, source) if source != SourceType.DIRECT else []
        jailbreak_hits = self.check_jailbreak(content)
        shell_hits = scan_shell(content)
        sql_hits = scan_sql(content)
        path_hits = scan_path_traversal(content)
        semantic_hits = scan_semantic_attacks(content)

        tool_result_hits: List[Dict[str, Any]] = []
        if source == SourceType.TOOL_RESULT:
            guard = ToolResultTransformGuard()
            guard_result = guard.scan(content)
            tool_result_hits = guard_result.get("hits", [])

        encoding_defender = EncodingBypassDefender()
        encoding_result = encoding_defender.scan(content)
        encoding_anomalies = encoding_result.get("anomaly_count", 0)

        total_hits = (
            len(direct_hits) + len(indirect_hits) + len(jailbreak_hits)
            + len(shell_hits) + len(sql_hits) + len(path_hits) + len(tool_result_hits)
            + len(semantic_hits)
        )
        total_score = 1.0 - (total_hits * 0.12 + encoding_anomalies * 0.08)
        total_score = max(0.0, min(1.0, total_score))

        blocked = total_hits > 0 or total_score < 0.55

        return DefenseResult(
            source_type=source,
            injection_hits=len(direct_hits) + len(indirect_hits) + len(shell_hits) + len(sql_hits) + len(path_hits),
            jailbreak_hits=len(jailbreak_hits),
            encoding_anomalies=encoding_anomalies,
            total_score=total_score,
            audit_log=direct_hits + indirect_hits + jailbreak_hits + shell_hits + sql_hits + path_hits + tool_result_hits + semantic_hits,
            blocked=blocked,
            reason="Multiple injection patterns detected" if blocked else "",
        )


class ToolResultTransformGuard:
    """工具执行结果 → LLM上下文之间的注入防御（蓝图 §38）"""

    _WRAP_TEMPLATE = (
        '\n\n<!-- BEGIN EXTERNAL_TOOL_OUTPUT source="{source}" timestamp="{ts}" -->\n'
        "{content}\n"
        "<!-- END EXTERNAL_TOOL_OUTPUT -->\n"
    )

    _INJECTION_INDICATORS = [
        r"(?i)(ignore\s+(all\s+)?previous)",
        r"(?i)(system\s+(prompt|message|instruction))",
        r"(?i)(you\s+are\s+now)",
        r"(?i)(act\s+as\s+(a|an)\s+(unfiltered|unrestricted))",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
    ]

    def __init__(self):
        self._compiled_indicators = [re.compile(p) for p in self._INJECTION_INDICATORS]

    def wrap(self, content: str, source: str = "tool") -> str:
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        return self._WRAP_TEMPLATE.format(source=source, ts=ts, content=content)

    def scan(self, content: str) -> Dict[str, Any]:
        hits = []
        for pattern in self._compiled_indicators:
            for m in pattern.finditer(content):
                hits.append({
                    "pattern": pattern.pattern[:80],
                    "match": m.group()[:120],
                    "start": m.start(),
                })
        return {
            "risk": "high" if len(hits) > 0 else "low",
            "hits": hits,
            "hits_count": len(hits),
        }


class EncodingBypassDefender:
    """编码逃逸防御 —— 递归解码扫描 + Unicode隐形字符检测 + 同形字标准化（蓝图 §59）"""

    _RECURSION_DEPTH = 3
    _DECODE_CHAINS = [
        ["base64"],
        ["rot13"],
        ["base64", "rot13"],
        ["rot13", "base64"],
        ["base64", "base64", "rot13"],
    ]

    _ZERO_WIDTH_CHARS = {
        "\u200b", "\u200c", "\u200d", "\u200e", "\u200f",
        "\u2060", "\u2061", "\u2062", "\u2063", "\u2064",
        "\uFEFF",
    }

    HOMOGLYPH_MAP = {
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
        "у": "y", "х": "x", "і": "i", "А": "A", "В": "B",
        "Е": "E", "Н": "H", "К": "K", "М": "M", "О": "O",
        "Р": "P", "С": "C", "Т": "T", "У": "Y", "Х": "X",
    }

    def scan(self, content: str) -> Dict[str, Any]:
        anomalies = 0
        findings: List[Dict[str, str]] = []

        if not content:
            return {"anomaly_count": 0, "findings": [], "risk": "low"}

        decoded_findings = self._recursive_decode_scan(content)
        findings.extend(decoded_findings)
        anomalies += len(decoded_findings)

        zw_findings = self._scan_zero_width(content)
        findings.extend(zw_findings)
        anomalies += len(zw_findings)

        homo_findings = self._scan_homoglyphs(content)
        findings.extend(homo_findings)
        anomalies += len(homo_findings)

        risk = "critical" if anomalies > 10 else ("high" if anomalies > 3 else "low")

        return {
            "anomaly_count": anomalies,
            "findings": findings,
            "risk": risk,
        }

    def _recursive_decode_scan(self, content: str) -> List[Dict[str, str]]:
        findings = []
        for chain in self._DECODE_CHAINS:
            decoded = content
            chain_desc = " → ".join(chain)
            try:
                for step in chain:
                    decoded = self._apply_decode(decoded, step)
                if decoded != content:
                    direct_hits = scan_direct(decoded)
                    jailbreak_hits = scan_jailbreak(decoded)
                    if direct_hits or jailbreak_hits:
                        findings.append({
                            "chain": chain_desc,
                            "explanation": f"Decoded content contains {len(direct_hits)} injection + {len(jailbreak_hits)} jailbreak patterns",
                            "severity": "high",
                        })
            except Exception:
                findings.append({
                    "chain": chain_desc,
                    "explanation": "Decode failed — possible obfuscation attempt",
                    "severity": "medium",
                })
        return findings

    @staticmethod
    def _apply_decode(content: str, method: str) -> str:
        if method == "base64":
            try:
                decoded = base64.b64decode(content.encode("ascii"), validate=True)
                return decoded.decode("utf-8", errors="replace")
            except Exception:
                return content
        elif method == "rot13":
            return codecs.decode(content, "rot_13") if content else content
        return content

    def _scan_zero_width(self, content: str) -> List[Dict[str, str]]:
        findings = []
        found = [c for c in content if c in self._ZERO_WIDTH_CHARS]
        if found:
            for c in set(found):
                count = found.count(c)
                findings.append({
                    "type": "zero_width_char",
                    "char": f"U+{ord(c):04X}",
                    "count": str(count),
                    "severity": "medium",
                })
        return findings

    def _scan_homoglyphs(self, content: str) -> List[Dict[str, str]]:
        findings = []
        found = [c for c in content if c in self.HOMOGLYPH_MAP]
        if found:
            unique = set(found)
            findings.append({
                "type": "homoglyph",
                "chars": ", ".join(f"U+{ord(c):04X}→{self.HOMOGLYPH_MAP[c]}" for c in unique),
                "count": str(len(found)),
                "severity": "high" if len(unique) >= 3 else "medium",
            })
        return findings

    def normalize_homoglyphs(self, content: str) -> str:
        result = []
        for c in content:
            result.append(self.HOMOGLYPH_MAP.get(c, c))
        return "".join(result)

    def strip_zero_width(self, content: str) -> str:
        return "".join(c for c in content if c not in self._ZERO_WIDTH_CHARS)
