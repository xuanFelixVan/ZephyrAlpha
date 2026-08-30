# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.suppression_learner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_analysis.py ; tests/audit/test_suppression_learner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 抑制规则必须经3次验证
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Suppression Learner — suppression_learner.py


自动学习假阳性模式：同一 pattern_hash 被标记 FALSE_POSITIVE >=3 次 -> 自动创建 suppression_rule。


对标 blueprint.md §2.14（自动学习假阳性模式识别与抑制）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: suppression_learner.py
# 层: 算法
# - id: A1
#   name_zh: ① SuppressionLearner
#   name_en: SuppressionLearner
#   intro: class SuppressionLearner 源码 L88-L242
#   desc: 公共方法（定义序）: patterns, shadow_observations, compute_pattern_hash, record_false_positive, should_suppress, shado…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SuppressionLearner
#   downstream: src/zephyr/gov_drift/_analysis.py ; tests/audit/test_suppression_learner.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class SuppressionRule:
    rule_id: uuid.UUID

    detector_id: str

    module_id: str

    pattern_hash: str

    drift_dimension: str

    false_positive_count: int

    created_at: datetime

    last_false_positive_at: datetime

    is_active: bool = True

    suppressed_count: int = 0

    last_reviewed_at: datetime | None = None


class SuppressionLearner:
    SUPPRESSION_THRESHOLD: int = 3

    REVIEW_INTERVAL_DAYS: int = 30

    def __init__(self) -> None:
        self._patterns: dict[str, SuppressionRule] = {}

        self._shadow_observations: dict[str, list[str]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def patterns(self) -> dict[str, SuppressionRule]:
        """只读：patterns（Stage 4 公共化）。"""
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        """写入：patterns（Stage 4 公共化）。"""
        self._patterns = value

    @property
    def shadow_observations(self) -> dict[str, list[str]]:
        """只读：shadow_observations（Stage 4 公共化）。"""
        return self._shadow_observations

    @shadow_observations.setter
    def shadow_observations(self, value):
        """写入：shadow_observations（Stage 4 公共化）。"""
        self._shadow_observations = value

    def compute_pattern_hash(
        self,
        detector_id: str,
        drift_dimension: str,
        diff_signature: str,
    ) -> str:
        raw = f"{detector_id}:{drift_dimension}:{diff_signature}"

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_false_positive(
        self,
        detector_id: str,
        module_id: str,
        drift_dimension: str,
        diff_signature: str,
    ) -> SuppressionRule | None:
        pattern_hash = self.compute_pattern_hash(detector_id, drift_dimension, diff_signature)

        key = f"{detector_id}:{module_id}:{pattern_hash}"

        if key in self._patterns:
            rule = self._patterns[key]

            rule.false_positive_count += 1

            rule.last_false_positive_at = datetime.now(UTC)

            if rule.false_positive_count >= self.SUPPRESSION_THRESHOLD and not rule.is_active:
                rule.is_active = True

                return rule

        else:
            rule = SuppressionRule(
                rule_id=uuid.uuid4(),
                detector_id=detector_id,
                module_id=module_id,
                pattern_hash=pattern_hash,
                drift_dimension=drift_dimension,
                false_positive_count=1,
                created_at=datetime.now(UTC),
                last_false_positive_at=datetime.now(UTC),
            )

            self._patterns[key] = rule

        return None

    def should_suppress(
        self,
        detector_id: str,
        module_id: str,
        drift_dimension: str,
        diff_signature: str,
    ) -> bool:
        pattern_hash = self.compute_pattern_hash(detector_id, drift_dimension, diff_signature)

        key = f"{detector_id}:{module_id}:{pattern_hash}"

        rule = self._patterns.get(key)

        if rule and rule.is_active:
            rule.suppressed_count += 1

            return True

        return False

    def shadow_observe(
        self,
        detector_id: str,
        module_id: str,
        drift_dimension: str,
        diff_signature: str,
    ) -> None:
        pattern_hash = self.compute_pattern_hash(detector_id, drift_dimension, diff_signature)

        key = f"{detector_id}:{module_id}:{pattern_hash}"

        rule = self._patterns.get(key)

        if rule and rule.is_active:
            self._shadow_observations.setdefault(key, []).append(diff_signature)

    def check_pattern_change(self, detector_id: str, module_id: str, drift_dimension: str, diff_signature: str) -> bool:
        pattern_hash = self.compute_pattern_hash(detector_id, drift_dimension, diff_signature)

        key = f"{detector_id}:{module_id}:{pattern_hash}"

        rule = self._patterns.get(key)

        if rule and rule.is_active:
            obs = self._shadow_observations.get(key, [])

            if obs and obs[-1] != diff_signature:
                rule.is_active = False

                return True

        return False

    def get_rules_needing_review(self) -> list[SuppressionRule]:
        cutoff = datetime.now(UTC) - timedelta(days=self.REVIEW_INTERVAL_DAYS)

        needs_review: list[SuppressionRule] = []

        for rule in self._patterns.values():
            if not rule.is_active:
                continue

            last = rule.last_reviewed_at or rule.created_at

            if last < cutoff:
                needs_review.append(rule)

        return needs_review

    def mark_reviewed(self, rule_id: uuid.UUID) -> None:
        for rule in self._patterns.values():
            if rule.rule_id == rule_id:
                rule.last_reviewed_at = datetime.now(UTC)

                return
