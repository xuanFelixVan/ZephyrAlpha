# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.self_protection.adversarial_mutator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-SEC_adversarial_mutator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import random
import time
from collections import defaultdict
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界


class MutationTechnique(str, Enum):
    ZERO_WIDTH = "zero_width"
    HOMOGLYPH = "homoglyph"
    BASE64_FRAGMENT = "base64_fragment"
    WHITESPACE_SPLIT = "whitespace_split"
    MIXED_CASE = "mixed_case"
    HTML_ENTITY = "html_entity"
    DELIMITER = "delimiter"
    UNICODE_NORMALIZE = "unicode_normalize"
    URL_ENCODE = "url_encode"
    REVERSE = "reverse"


class MutatedPayload(BaseModel):
    original_id: str
    technique: str
    original: str
    mutated: str
    mutation_desc: str = ""


class MutationResult(BaseModel):
    payload_id: str
    technique: str
    original: str
    mutated: str
    decision: str
    blocked: bool
    bypassed: bool
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class MutationReport(BaseModel):
    report_id: str = ""
    total_originals: int = 0
    total_mutations: int = 0
    blocked: int = 0
    bypassed: int = 0
    errors: int = 0
    block_rate_pct: float = 0.0
    by_technique: dict[str, dict[str, int]] = Field(default_factory=dict)
    top_bypassed: list[MutationResult] = Field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0


class AdversarialMutator:
    """对抗变异生成器 — 对 Red Team 载荷施加 10 种变异技术，检验 LSG 抗干扰能力.

    变异技术:
      - zero_width: 关键字符间插入零宽字符 (\\u200b etc.)
      - homoglyph: 同形字替换 (а->a, е->e etc.)
      - base64_fragment: 对载荷中关键片段做 base64 编码
      - whitespace_split: 敏感词间插入换行/制表符
      - mixed_case: 随机大小写绕过
      - html_entity: HTML 实体编码关键字符
      - delimiter: 分隔符插入 bypass 关键词
      - unicode_normalize: NFKC/NFD 规范化绕过
      - url_encode: URL 编码关键片段
      - reverse: 反转关键片段（检验语义层盲点）
    """

    _ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
    _HOMOGLYPH_MAP = {
        "a": "а",
        "e": "е",
        "o": "о",
        "p": "р",
        "c": "с",
        "y": "у",
        "x": "х",
        "i": "і",
        "A": "А",
        "B": "В",
        "E": "Е",
        "H": "Н",
        "K": "К",
        "M": "М",
        "O": "О",
        "P": "Р",
        "C": "С",
        "T": "Т",
        "Y": "У",
        "X": "Х",
    }
    _SENSITIVE_WORDS = [
        "ignore",
        "forget",
        "override",
        "system",
        "prompt",
        "instruction",
        "jailbreak",
        "bypass",
        "hack",
        "exploit",
        "password",
        "secret",
        "unfiltered",
        "unrestricted",
        "uncensored",
        "DAN",
        "developer mode",
    ]
    _HTML_ENTITIES = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;", "&": "&amp;"}

    def __init__(self, enabled_techniques: list[MutationTechnique] | None = None):
        self._techniques = enabled_techniques or list(MutationTechnique)
        self._results: list[MutationResult] = []
        self._started_at: float = 0.0

    def mutate(self, payload_id: str, content: str) -> list[MutatedPayload]:
        mutated: list[MutatedPayload] = []
        for tech in self._techniques:
            fn = getattr(self, f"_mutate_{tech.value}", None)
            if fn is None:
                continue
            result = fn(content)
            if result and result != content:
                mutated.append(
                    MutatedPayload(
                        original_id=payload_id,
                        technique=tech.value,
                        original=content[:200],
                        mutated=result[:500],
                        mutation_desc=f"{tech.value}: {content[:50]}... -> {result[:80]}...",
                    )
                )
        return mutated

    def run(self, payloads_data: dict[str, Any]) -> MutationReport:
        self._started_at = time.time()
        payloads = payloads_data.get("payloads", [])
        total_originals = len(payloads)

        from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

        gateway = LSGSecurityGateway()
        variants_to_scan: list[tuple[str, str, str]] = []

        for entry in payloads:
            pid = entry.get("id", "unknown")
            for variant in entry.get("variants", [])[:3]:
                mutations = self.mutate(pid, variant)
                for m in mutations:
                    variants_to_scan.append((pid, m.technique, m.mutated))

        import asyncio
        import concurrent.futures

        async def _scan_all():
            scan_results = []
            for pid, tech, mutated in variants_to_scan:
                t0 = time.time()
                try:
                    result = await gateway.scan_input(
                        mutated,
                        source="adversarial_mutator",
                        metadata={"request_id": f"am_{pid}_{tech}"},
                    )
                    is_blocked = result.decision.value in ("deny", "block")
                    mr = MutationResult(
                        payload_id=pid,
                        technique=tech,
                        original=mutated[:200],
                        mutated=mutated[:200],
                        decision=result.decision.value,
                        blocked=is_blocked,
                        bypassed=not is_blocked,
                        latency_ms=(time.time() - t0) * 1000,
                    )
                except Exception:
                    mr = MutationResult(
                        payload_id=pid,
                        technique=tech,
                        original="",
                        mutated=mutated[:200],
                        decision="error",
                        blocked=False,
                        bypassed=True,
                        latency_ms=(time.time() - t0) * 1000,
                    )
                scan_results.append(mr)
            return scan_results

        try:
            asyncio.get_running_loop()
            has_loop = True
        except RuntimeError:
            has_loop = False

        if has_loop:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self._results = pool.submit(lambda: run_sync(_scan_all())).result()
        else:
            self._results = run_sync(_scan_all())

        return self._build_report(total_originals)

    def _build_report(self, total_originals: int) -> MutationReport:
        total = len(self._results)
        blocked = sum(1 for r in self._results if r.blocked)
        bypassed = sum(1 for r in self._results if r.bypassed)
        errors = sum(1 for r in self._results if r.decision == "error")

        by_tech: dict[str, dict[str, int]] = defaultdict(lambda: {"blocked": 0, "bypassed": 0, "total": 0})
        for r in self._results:
            by_tech[r.technique]["blocked"] += 1 if r.blocked else 0
            by_tech[r.technique]["bypassed"] += 1 if r.bypassed else 0
            by_tech[r.technique]["total"] += 1

        top_bypassed = sorted(
            [r for r in self._results if r.bypassed],
            key=lambda r: r.latency_ms,
            reverse=True,
        )[:20]

        return MutationReport(
            report_id=f"am_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            total_originals=total_originals,
            total_mutations=total,
            blocked=blocked,
            bypassed=bypassed,
            errors=errors,
            block_rate_pct=round(blocked / max(total, 1) * 100, 2),
            by_technique=dict(by_tech),
            top_bypassed=top_bypassed,
            started_at=datetime.fromtimestamp(self._started_at, tz=UTC).isoformat(),
            completed_at=datetime.now(UTC).isoformat(),
            duration_seconds=round(time.time() - self._started_at, 3),
        )

    def _mutate_zero_width(self, content: str) -> str:
        if len(content) < 5:
            return content
        chars = list(content)
        for i in range(1, len(chars), random.randint(3, 7)):
            chars.insert(i, random.choice(self._ZERO_WIDTH_CHARS))
        return "".join(chars)

    def _mutate_homoglyph(self, content: str) -> str:
        result = []
        for c in content:
            result.append(self._HOMOGLYPH_MAP.get(c, c))
        return "".join(result)

    def _mutate_base64_fragment(self, content: str) -> str:
        import base64

        words = content.split()
        if not words:
            return content
        idx = random.randint(0, len(words) - 1)
        word = words[idx]
        if len(word) > 4:
            encoded = base64.b64encode(word.encode()).decode()
            words[idx] = f"b64:{encoded}"
        return " ".join(words)

    def _mutate_whitespace_split(self, content: str) -> str:
        for word in self._SENSITIVE_WORDS:
            if word in content.lower():
                split = word[: len(word) // 2] + "\n" + word[len(word) // 2 :]
                content = content.replace(word, split, 1)
        return content

    def _mutate_mixed_case(self, content: str) -> str:
        result = []
        for c in content:
            if random.random() < 0.4:
                result.append(c.upper() if c.islower() else c.lower())
            else:
                result.append(c)
        return "".join(result)

    def _mutate_html_entity(self, content: str) -> str:
        result = []
        for c in content:
            result.append(self._HTML_ENTITIES.get(c, c))
        return "".join(result)

    def _mutate_delimiter(self, content: str) -> str:
        for word in self._SENSITIVE_WORDS:
            if len(word) < 3:
                continue
            split = "-".join(list(word))
            if word in content.lower():
                content = content.replace(word, split, 1)
        return content

    def _mutate_unicode_normalize(self, content: str) -> str:
        import unicodedata

        try:
            return unicodedata.normalize("NFKC", content)
        except Exception:
            return content

    def _mutate_url_encode(self, content: str) -> str:
        from urllib.parse import quote

        return quote(content[:100], safe="")

    def _mutate_reverse(self, content: str) -> str:
        mid = len(content) // 2
        return content[mid:] + content[:mid]

    @property
    def results(self) -> list[MutationResult]:
        return list(self._results)
