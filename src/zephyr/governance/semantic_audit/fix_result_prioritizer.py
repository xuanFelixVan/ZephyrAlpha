# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 8
# [MODULE] zephyr.governance.semantic_audit.fix_result_prioritizer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] blast_radius.py; semantic-auditor/__init__.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 排序键: severity降序->impact降序->urgency降序->dependency_depth降序; 输入输出类型一致; 权重之和=1.0
# [MODIFY-GUARD] blueprint.md §3.1 Stage 8; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on empty input to get_top_n with n<=0; ValueError on invalid weights
# [TESTS] tests/semantic-auditor/test_fix_prioritizer.py
# [A_module] module_id=MOD-SEM_fix_prioritizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
fix_prioritizer — MOD-INF-028 §3.1 Stage 8
============================================
修复优先级排序器：四维排序 severity->impact->urgency->dependency_depth

维度映射（基于 FixResult 模型）:
- severity:  FixResult.severity  (RED=3, YELLOW=2, INFO=1)
- impact:    FixResult.affected_count (受影响项数)
- urgency:   FixResult.certainty (触发确定性 0-1)
- dependency_depth: 外部传入 (finding_id->深度映射)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zephyr.governance.semantic_audit.models import FixResult, Severity

__all__ = ["FixPrioritizer", "PrioritizedFixResult", "PrioritySummary"]

_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.RED: 3,
    Severity.YELLOW: 2,
    Severity.INFO: 1,
}

_DEFAULT_WEIGHTS: dict[str, float] = {
    "severity": 0.40,
    "impact": 0.25,
    "urgency": 0.20,
    "dependency_depth": 0.15,
}


@dataclass
class PrioritizedFixResult:
    """排序后的修复结果 — 附带排序元数据."""

    fix: FixResult = field(compare=False)
    priority_score: float = field(default=0.0, compare=False)
    rank: int = field(default=0, compare=False)
    dependency_depth: int = field(default=0, compare=False)


@dataclass
class PrioritySummary:
    """排序结果摘要."""

    total: int = 0
    red_count: int = 0
    yellow_count: int = 0
    info_count: int = 0
    avg_priority_score: float = 0.0
    top_5: list[dict[str, Any]] = field(default_factory=list)


class FixPrioritizer:
    """修复优先级排序器 — 蓝图 §3.1 Stage 8.

    四维排序规则（降序）:
    1. severity: RED > YELLOW > INFO
    2. impact: affected_count 大 > 小
    3. urgency: certainty 高 > 低
    4. dependency_depth: 深 > 浅

    支持两种排序模式:
    - 字典序排序: 逐维度严格比较（prioritize_lexicographic）
    - 加权评分排序: 四维加权求和后排序（prioritize_weighted）
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        """初始化排序器.

        Args:
            weights: 自定义权重字典，键为 severity/impact/urgency/dependency_depth，
                     值为 0-1 浮点数，四者之和必须为 1.0。None 使用默认权重。
        """
        self._weights = _DEFAULT_WEIGHTS if weights is None else self._validate_weights(weights)

    @staticmethod
    def _validate_weights(weights: dict[str, float]) -> dict[str, float]:
        expected_keys = {"severity", "impact", "urgency", "dependency_depth"}
        actual_keys = set(weights.keys())
        if actual_keys != expected_keys:
            raise ValueError(f"权重键必须为 {sorted(expected_keys)}，实际为 {sorted(actual_keys)}")
        total = sum(weights.values())
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"权重之和必须为 1.0，实际为 {total:.6f}")
        for k, v in weights.items():
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"权重 {k}={v} 不在 [0, 1] 范围内")
        return dict(weights)

    def _compute_weighted_score(
        self,
        fix: FixResult,
        dependency_depth: int,
        max_affected: int,
    ) -> float:
        """计算加权优先级分数.

        各维度归一化到 [0, 1]:
        - severity: RED=1.0, YELLOW=0.5, INFO=0.0
        - impact: affected_count / max(max_affected, 1)
        - urgency: certainty (已在 [0, 1])
        - dependency_depth: depth / max(depth, 1)（单条目时为 1.0）
        """
        severity_norm = {
            Severity.RED: 1.0,
            Severity.YELLOW: 0.5,
            Severity.INFO: 0.0,
        }[fix.severity]
        impact_norm = fix.affected_count / max(max_affected, 1)
        urgency_norm = fix.certainty
        depth_norm = dependency_depth / max(dependency_depth, 1) if dependency_depth > 0 else 0.0

        return (
            self._weights["severity"] * severity_norm
            + self._weights["impact"] * impact_norm
            + self._weights["urgency"] * urgency_norm
            + self._weights["dependency_depth"] * depth_norm
        )

    def prioritize(
        self,
        fixes: list[FixResult],
        dependency_depths: dict[str, int] | None = None,
    ) -> list[PrioritizedFixResult]:
        """按四维加权评分降序排序.

        Args:
            fixes: 待排序的修复结果列表。
            dependency_depths: finding_id->依赖深度映射。None 时所有深度为 0。

        Returns:
            排序后的 PrioritizedFixResult 列表（不修改原列表）。
        """
        if not fixes:
            return []
        depths = dependency_depths or {}
        max_affected = max(f.affected_count for f in fixes)

        results: list[PrioritizedFixResult] = []
        for fix in fixes:
            depth = depths.get(fix.finding.finding_id, 0)
            score = self._compute_weighted_score(fix, depth, max_affected)
            results.append(
                PrioritizedFixResult(
                    fix=fix,
                    priority_score=round(score, 6),
                    dependency_depth=depth,
                )
            )

        results.sort(key=lambda r: r.priority_score, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1
        return results

    def prioritize_lexicographic(
        self,
        fixes: list[FixResult],
        dependency_depths: dict[str, int] | None = None,
    ) -> list[PrioritizedFixResult]:
        """按四维字典序降序排序（严格逐维度比较）.

        排序键优先级: severity -> impact -> urgency -> dependency_depth

        Args:
            fixes: 待排序的修复结果列表。
            dependency_depths: finding_id->依赖深度映射。None 时所有深度为 0。

        Returns:
            排序后的 PrioritizedFixResult 列表（不修改原列表）。
        """
        if not fixes:
            return []
        depths = dependency_depths or {}

        results: list[PrioritizedFixResult] = []
        for fix in fixes:
            depth = depths.get(fix.finding.finding_id, 0)
            results.append(
                PrioritizedFixResult(
                    fix=fix,
                    dependency_depth=depth,
                )
            )

        results.sort(
            key=lambda r: (
                _SEVERITY_ORDER[r.fix.severity],
                r.fix.affected_count,
                r.fix.certainty,
                r.dependency_depth,
            ),
            reverse=True,
        )
        for i, r in enumerate(results):
            r.rank = i + 1
        return results

    def get_top_n(
        self,
        fixes: list[FixResult],
        n: int,
        dependency_depths: dict[str, int] | None = None,
    ) -> list[PrioritizedFixResult]:
        """返回前 N 个最高优先级修复.

        Args:
            fixes: 待排序的修复结果列表。
            n: 返回数量，必须 > 0。
            dependency_depths: finding_id->依赖深度映射。

        Returns:
            排序后的前 N 个修复结果。

        Raises:
            ValueError: n <= 0 时抛出。
        """
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")
        return self.prioritize(fixes, dependency_depths)[:n]

    def batch(
        self,
        prioritized: list[PrioritizedFixResult],
        batch_size: int = 5,
    ) -> list[list[PrioritizedFixResult]]:
        """将排序结果分批输出.

        Args:
            prioritized: 已排序的结果列表。
            batch_size: 每批大小，必须 > 0。

        Returns:
            分批后的列表。

        Raises:
            ValueError: batch_size <= 0 时抛出。
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {batch_size}")
        batches: list[list[PrioritizedFixResult]] = []
        for i in range(0, len(prioritized), batch_size):
            batches.append(prioritized[i : i + batch_size])
        return batches

    def summarize(self, prioritized: list[PrioritizedFixResult]) -> PrioritySummary:
        """生成排序结果摘要.

        Args:
            prioritized: 已排序的结果列表。

        Returns:
            PrioritySummary 摘要对象。
        """
        if not prioritized:
            return PrioritySummary()
        reds = [r for r in prioritized if r.fix.severity is Severity.RED]
        yellows = [r for r in prioritized if r.fix.severity is Severity.YELLOW]
        infos = [r for r in prioritized if r.fix.severity is Severity.INFO]
        avg_score = sum(r.priority_score for r in prioritized) / len(prioritized)
        top_5: list[dict[str, Any]] = [
            {
                "rank": r.rank,
                "finding_id": r.fix.finding.finding_id,
                "severity": r.fix.severity.value,
                "impact": r.fix.affected_count,
                "urgency": r.fix.certainty,
                "dependency_depth": r.dependency_depth,
                "priority_score": r.priority_score,
            }
            for r in prioritized[:5]
        ]
        return PrioritySummary(
            total=len(prioritized),
            red_count=len(reds),
            yellow_count=len(yellows),
            info_count=len(infos),
            avg_priority_score=round(avg_score, 6),
            top_5=top_5,
        )
