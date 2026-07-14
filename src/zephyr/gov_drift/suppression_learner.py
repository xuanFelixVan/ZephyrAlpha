# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.suppression_learner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_analysis.py; tests/audit/test_suppression_learner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 抑制规则必须经3次验证
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_suppression_learner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Suppression Learner — suppression_learner.py


自动学习假阳性模式：同一 pattern_hash 被标记 FALSE_POSITIVE >=3 次 -> 自动创建 suppression_rule。


对标 blueprint.md §2.14（自动学习假阳性模式识别与抑制）。"""

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
