# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.extraction_safety
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/security/test_extraction_safety.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_extraction_safety | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""安全提取适配性评估器 — Suitability Score 0-100 + 不安全提取模式检测.

职责：
  - 7维评估 → Suitability Score 0-100
  - 4档 verdict：<40 NEVER_EXTRACT / 40-69 NEEDS_REVIEW / 70-89 SAFE_EXTRACT / ≥90 SAFE_AUTO_EXTRACT
  - 7类不安全提取模式目录
  - 部分共享提取计划（LCS 公共核心 60% + 差异保留）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SuitabilityScore:
    caller_count: int = 10
    call_depth: int = 5
    is_public_api: bool = False
    is_hot_path: bool = False
    is_codegen: bool = False
    is_vendored: bool = False
    has_independent_test: bool = False
    total: int = 0
    verdict: str = "NEEDS_REVIEW"


@dataclass
class ExtractionImpact:
    affected_callers: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    risk_level: str = "LOW"
    recommended_action: str = ""


@dataclass
class PartialExtractionPlan:
    shared_core: str = ""
    diff_preserved: list[str] = field(default_factory=list)
    lcs_ratio: float = 0.0
    source_file: str = ""
    target_file: str = ""


class ExtractionSafety:
    """安全提取评估器."""

    UNSAFE_PATTERNS: list[dict[str, Any]] = [
        {"name": "high_caller_count", "threshold": 10, "desc": "调用方>10"},
        {"name": "platform_code", "pattern": "__init__", "desc": "__init__.py入口"},
        {"name": "public_api", "flag": "is_public_api", "desc": "公开API"},
        {"name": "hot_path", "flag": "is_hot_path", "desc": "性能热点"},
        {"name": "codegen", "flag": "is_codegen", "desc": "生成代码"},
        {"name": "vendored", "flag": "is_vendored", "desc": "Vendored代码"},
        {"name": "stub_function", "pattern": "NotImplementedError|pass", "desc": "Stub函数"},
    ]

    # ── 公共 API ──────────────────────────────────────────────

    def compute_suitability(
        self,
        caller_count: int = 0,
        call_depth: int = 0,
        is_public_api: bool = False,
        is_hot_path: bool = False,
        is_codegen: bool = False,
        is_vendored: bool = False,
        has_independent_test: bool = False,
        body: str = "",
    ) -> SuitabilityScore:
        """7维评估 → Suitability Score."""
        score = SuitabilityScore(
            caller_count=caller_count,
            call_depth=call_depth,
            is_public_api=is_public_api,
            is_hot_path=is_hot_path,
            is_codegen=is_codegen,
            is_vendored=is_vendored,
            has_independent_test=has_independent_test,
        )

        unsafe_count = 0
        if caller_count > 10:
            unsafe_count += 1
        if is_public_api:
            unsafe_count += 1
        if is_hot_path:
            unsafe_count += 1
        if is_codegen:
            unsafe_count += 1
        if is_vendored:
            unsafe_count += 1
        if call_depth > 5:
            unsafe_count += 1

        base = 100
        deductions = (
            min(caller_count * 3, 30)
            + (call_depth * 2 if call_depth > 3 else 0)
            + (20 if is_public_api else 0)
            + (20 if is_hot_path else 0)
            + (30 if is_codegen else 0)
            + (30 if is_vendored else 0)
            - (10 if has_independent_test else 0)
            + (10 if self._is_stub(body) else 0)
        )
        score.total = max(0, min(100, base - deductions))
        score.verdict = self._classify_verdict(score.total)
        return score

    def check_unsafe_patterns(
        self,
        caller_count: int = 0,
        file_path: str = "",
        is_public_api: bool = False,
        is_hot_path: bool = False,
        is_codegen: bool = False,
        is_vendored: bool = False,
        body: str = "",
    ) -> list[str]:
        """检测匹配的不安全提取模式."""
        matched: list[str] = []

        if caller_count > 10:
            matched.append("high_caller_count")
        if "__init__" in file_path.lower():
            matched.append("platform_code")
        if is_public_api:
            matched.append("public_api")
        if is_hot_path:
            matched.append("hot_path")
        if is_codegen:
            matched.append("codegen")
        if is_vendored:
            matched.append("vendored")
        if self._is_stub(body):
            matched.append("stub_function")

        return matched

    def analyze_impact(
        self,
        caller_files: list[str],
        caller_counts: list[int],
    ) -> ExtractionImpact:
        """提取影响分析."""
        total_callers = sum(caller_counts) if caller_counts else len(caller_files)

        if total_callers >= 10:
            risk = "HIGH"
            action = "NEEDS_REVIEW"
        elif total_callers >= 5:
            risk = "MEDIUM"
            action = "SAFE_WITH_CAUTION"
        else:
            risk = "LOW"
            action = "SAFE_EXTRACT"

        return ExtractionImpact(
            affected_callers=caller_files,
            affected_files=list(set(caller_files)),
            risk_level=risk,
            recommended_action=action,
        )

    def generate_partial_extraction(self, source_a: str, source_b: str) -> PartialExtractionPlan | None:
        """LCS 部分共享提取计划."""
        lines_a = source_a.strip().splitlines()
        lines_b = source_b.strip().splitlines()

        lcs_lines = self._lcs(lines_a, lines_b)
        if not lcs_lines:
            return None

        lcs_ratio = len(lcs_lines) / max(len(lines_a), len(lines_b))
        if lcs_ratio < 0.4:
            return None

        shared_core = "\n".join(lcs_lines)
        diff_a = [l for l in lines_a if l.strip() not in {x.strip() for x in lcs_lines}]
        diff_b = [l for l in lines_b if l.strip() not in {x.strip() for x in lcs_lines}]

        return PartialExtractionPlan(
            shared_core=shared_core,
            diff_preserved=diff_a + diff_b,
            lcs_ratio=round(lcs_ratio, 3),
        )

    def is_auto_extractable(self, suitability: SuitabilityScore) -> bool:
        """判断是否可自动提取."""
        return suitability.verdict == "SAFE_AUTO_EXTRACT"

    # ── 内部 ──────────────────────────────────────────────────

    @staticmethod
    def _classify_verdict(total: int) -> str:
        if total >= 90:
            return "SAFE_AUTO_EXTRACT"
        if total >= 70:
            return "SAFE_EXTRACT"
        if total >= 40:
            return "NEEDS_REVIEW"
        return "NEVER_EXTRACT"

    @staticmethod
    def _is_stub(body: str) -> bool:
        stripped = body.strip().lower()
        if not stripped:
            return True
        return any(kw in stripped for kw in ["notimplementederror", "pass", "raise notimplementederror"])

    @staticmethod
    def _lcs(a: list[str], b: list[str]) -> list[str]:
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i - 1].strip() == b[j - 1].strip():
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        result: list[str] = []
        i, j = m, n
        while i > 0 and j > 0:
            if a[i - 1].strip() == b[j - 1].strip():
                result.append(a[i - 1])
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            else:
                j -= 1

        return list(reversed(result))
