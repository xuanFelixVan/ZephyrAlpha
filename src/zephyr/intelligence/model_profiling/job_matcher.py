# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.job_matcher
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport
# [CONSUMERS] MOD-INF-034
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 岗位匹配矩阵真源=data/brain/job_matrix.yaml;幻觉率正常评分非硬门
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] JobMatcherError
# [TESTS] tests/test_job_matcher.py
# [TTL] permanent

"""
JobMatcher --- 模型岗位匹配器

基于 QuickProfile 的能力分级 + 幻觉率六维细分, 匹配预定义岗位矩阵,
输出 Top-N 推荐岗位。

设计原则:
    - 幻觉率正常评分 (非硬门): 任何模型都有幻觉, Claude 也不例外
    - 岗位级幻觉期望: 每岗位自定 max_hallucination, 超过则 match_score 衰减但不淘汰
    - required 是硬性: 不满足 required = qualified=False (但仍计算分数用于排序)
    - bonus 是加分: 命中越多 match_score 越高

match_score 公式 (0-1, 四维加权):
    qualified 时:  0.45 (required) + bonus_ratio * 0.25 + hallu_score * 0.20 + cost_score * 0.10
    不 qualified:  bonus_ratio * 0.25 + hallu_score * 0.20 + cost_score * 0.10  (无 required 基础分)
    D-MCE-07: 成本是维度非硬门; claude 贵但必要时仍可用 (cost 仅占 10%)

用法:
    matcher = JobMatcher()
    profile = QuickProfile(...)
    recs = matcher.match_top(profile, n=3)
    # recs[0].job_title, recs[0].match_score, recs[0].qualified
"""

from __future__ import annotations

from typing import Final
import logging
from pathlib import Path
from typing import Any

import yaml

from zephyr.intelligence.model_profiling.capability_passport import (
    GRADE_LEVEL,
    CostBreakdown,
    HallucinationBreakdown,
    JobRecommendation,
    QuickProfile,
    compute_grade_simple,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源 (SSoT)

_log = logging.getLogger(__name__)

JOB_MATRIX_PATH: Final[Path] = REPO_ROOT / "data" / "brain" / "job_matrix.yaml"


class JobMatcherError(Exception):
    """岗位匹配器错误。"""
    error_code = "ZA-IT-0001"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class JobMatcher:
    """模型岗位匹配器 — 基于 QuickProfile 匹配 job_matrix.yaml 中的岗位。

    用法:
        matcher = JobMatcher()
        recs = matcher.match_top(profile, n=3)
        for r in recs:
            print(f"{r.job_title}: {r.match_score:.0%} (qualified={r.qualified})")
    """

    def __init__(self, matrix_path: Path | None = None) -> None:
        self._matrix_path = matrix_path or JOB_MATRIX_PATH
        self._jobs: dict[str, dict[str, Any]] = {}
        self._hallu_dims: dict[str, float] = {}
        # P2 Cost 轴 (D-MCE-07: 成本是维度非硬门)
        self._cost_weight: float = 0.10
        self._cost_free: float = 0.01
        self._cost_expensive: float = 1.0
        self._load_matrix()

    def _load_matrix(self) -> None:
        """加载 job_matrix.yaml 真源。"""
        if not self._matrix_path.exists():
            raise JobMatcherError(
                f"job matrix not found: {self._matrix_path}"
            )
        try:
            with self._matrix_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise JobMatcherError(f"yaml parse error: {e}") from e

        self._jobs = data.get("jobs", {}) or {}
        # 幻觉六维权重 (用于计算加权幻觉率)
        dims = data.get("hallucination_dimensions", {}) or {}
        self._hallu_dims = {
            name: float(d.get("weight", 0.0))
            for name, d in dims.items()
        }
        # P2 Cost 轴配置 (D-MCE-07: 成本是维度非硬门)
        cost_dim = data.get("cost_dimension", {}) or {}
        self._cost_weight = float(cost_dim.get("weight", 0.10))
        self._cost_free = float(cost_dim.get("free_threshold", 0.01))
        self._cost_expensive = float(cost_dim.get("expensive_threshold", 1.0))
        _log.debug(
            "JobMatcher: loaded %d jobs, %d hallu dims, cost_weight=%.2f from %s",
            len(self._jobs), len(self._hallu_dims), self._cost_weight, self._matrix_path,
        )

    # ── 公开 API ──────────────────────────────────────────

    def match(self, profile: QuickProfile) -> list[JobRecommendation]:
        """对全部岗位计算匹配度, 返回按 match_score 降序的列表。"""
        recs: list[JobRecommendation] = []
        for job_id, job_def in self._jobs.items():
            rec = self._match_one(profile, job_id, job_def)
            recs.append(rec)
        recs.sort(key=lambda r: r.match_score, reverse=True)
        return recs

    def match_top(self, profile: QuickProfile, n: int = 3) -> list[JobRecommendation]:
        """返回 Top-N 推荐岗位 (按 match_score 降序)。"""
        return self.match(profile)[:n]

    @property
    def job_count(self) -> int:
        return len(self._jobs)

    @property
    def job_ids(self) -> list[str]:
        return list(self._jobs.keys())

    # ── 内部: 单岗位匹配 ─────────────────────────────────

    def _match_one(
        self,
        profile: QuickProfile,
        job_id: str,
        job_def: dict[str, Any],
    ) -> JobRecommendation:
        """计算一个岗位的匹配度。"""
        required = job_def.get("required", {}) or {}
        bonus = job_def.get("bonus", {}) or {}
        max_hallu = float(job_def.get("max_hallucination", 0.5))
        max_cost = float(job_def.get("max_cost", 1.0))

        # 1. 检查 required
        qualified, missing = self._check_required(profile.capability_grades, required)

        # 2. 计算 bonus 命中率
        bonus_ratio, bonus_summary = self._compute_bonus(
            profile.capability_grades, bonus
        )

        # 3. 计算幻觉率得分 (正常评分, 非硬门)
        hallu_score = self._compute_hallucination_score(
            profile.hallucination, max_hallu
        )
        # 幻觉率是否低于岗位期望 (参考值, 非淘汰)
        hallu_passed = profile.hallucination.overall_rate <= max_hallu

        # 4. 计算成本得分 (D-MCE-07: 成本是维度非硬门)
        cost_score = self._compute_cost_score(profile.cost, max_cost)

        # 5. match_score 四维加权
        #    qualified: 0.45(required) + 0.25(bonus) + 0.20(hallu) + 0.10(cost)
        #    cost 仅占 10% — claude 贵但必要时仍可用
        if qualified:
            score = 0.45 + bonus_ratio * 0.25 + hallu_score * 0.20 + cost_score * 0.10
        else:
            # 不合格: 无 required 基础分, 但仍计算用于排序参考
            score = bonus_ratio * 0.25 + hallu_score * 0.20 + cost_score * 0.10
        score = max(0.0, min(1.0, score))

        return JobRecommendation(
            job_id=job_id,
            job_title=job_def.get("title", job_id),
            match_score=round(score, 3),
            qualified=qualified,
            hallucination_passed=hallu_passed,
            missing_required=missing,
            bonus_summary=bonus_summary,
            description=job_def.get("description", ""),
        )

    def _check_required(
        self,
        grades: dict[str, str],
        required: dict[str, str],
    ) -> tuple[bool, list[str]]:
        """检查能力分级是否满足 required。

        Args:
            grades: {capability: "A"|"B"|...}
            required: {capability: "C"}  要求该能力至少 C 级
        Returns:
            (qualified, missing_list)
        """
        missing: list[str] = []
        for cap, need_grade in required.items():
            actual = grades.get(cap, "F")
            if GRADE_LEVEL.get(actual, 0) < GRADE_LEVEL.get(need_grade, 0):
                missing.append(f"{cap}(need>={need_grade},got={actual})")
        return (len(missing) == 0, missing)

    def _compute_bonus(
        self,
        grades: dict[str, str],
        bonus: dict[str, str],
    ) -> tuple[float, str]:
        """计算 bonus 命中率。

        Returns:
            (ratio 0-1, summary_text)
        """
        if not bonus:
            return 0.0, ""
        hits: list[str] = []
        for cap, need_grade in bonus.items():
            actual = grades.get(cap, "F")
            if GRADE_LEVEL.get(actual, 0) >= GRADE_LEVEL.get(need_grade, 0):
                hits.append(f"{cap}={actual}")
        ratio = len(hits) / len(bonus)
        return round(ratio, 3), ", ".join(hits) if hits else "none"

    def _compute_hallucination_score(
        self,
        hallu: HallucinationBreakdown,
        max_hallu: float,
    ) -> float:
        """计算幻觉率得分 (0-1, 越高越好)。

        策略 (正常评分, 非硬门):
            - overall_rate <= max_hallu: 满分区间, 线性给分 0.7~1.0
            - overall_rate > max_hallu: 超出期望, 衰减但归零下限 0.0
            - 任何模型都有幻觉, 不做一票否决
        """
        rate = hallu.overall_rate
        if max_hallu <= 0:
            # 岗位要求零幻觉 (不可能), 用绝对分
            return round(1.0 - rate, 3)
        if rate <= max_hallu:
            # 满足期望: 0.7 ~ 1.0 线性 (越低越好)
            return round(0.7 + 0.3 * (1.0 - rate / max_hallu), 3)
        # 超出期望: 0.7 ~ 0.0 线性衰减 (超 2 倍归零)
        excess = (rate - max_hallu) / max_hallu
        return round(max(0.0, 0.7 - 0.7 * min(1.0, excess)), 3)

    def _compute_cost_score(
        self,
        cost: CostBreakdown,
        max_cost: float,
    ) -> float:
        """计算成本得分 (0-1, 越高越好 = 越便宜)。

        策略 (D-MCE-07: 成本是维度非硬门):
            - local 模型: 直接用 cost.cost_score (通常 1.0, 成本≈0)
            - api 模型:
                - cost <= max_cost: 满分区间, 0.7~1.0 线性 (越便宜越好)
                - cost > max_cost: 衰减但归零下限 0.0 (超 2 倍归零)
            - 任何模型都不因成本一票否决 (claude 贵但必要时仍可用)
        """
        if cost.deployment_mode == "local":
            # 本地模型成本≈0, 直接返回 cost_score (通常 1.0)
            return cost.cost_score
        actual_cost = cost.estimated_cost_usd
        if max_cost <= 0:
            # 岗位要求零成本 (只接受本地), 用 cost.cost_score 绝对分
            return cost.cost_score
        if actual_cost <= max_cost:
            # 满足期望: 0.7 ~ 1.0 线性 (越便宜越好)
            return round(0.7 + 0.3 * (1.0 - actual_cost / max_cost), 3)
        # 超出期望: 0.7 ~ 0.0 线性衰减 (超 2 倍归零)
        excess = (actual_cost - max_cost) / max_cost
        return round(max(0.0, 0.7 - 0.7 * min(1.0, excess)), 3)


# ── 便捷函数 ──────────────────────────────────────────────

def match_jobs(
    profile: QuickProfile,
    n: int = 3,
    matrix_path: Path | None = None,
) -> list[JobRecommendation]:
    """便捷函数: 一行调用获取 Top-N 岗位推荐。"""
    matcher = JobMatcher(matrix_path=matrix_path)
    return matcher.match_top(profile, n=n)


def grades_from_scores(scores: dict[str, float]) -> dict[str, str]:
    """便捷函数: 从原始分 dict 转为分级 dict。"""
    return {cap: compute_grade_simple(s) for cap, s in scores.items()}
