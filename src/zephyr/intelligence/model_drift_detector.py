# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.intelligence.model_drift_detector
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.shared.io.paths
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-021-model_drift_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModelDriftDetector — LLM 模型行为漂移检测。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B113 + exit code 34

检测 LLM 模型版本的静默行为变化（无版本号变更但输出分布漂移）。
建立基线输出 feature vector -> 定期采样 -> KL 散度/JS 距离 -> 超过阈值 -> exit 34。
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT


@dataclass
class DriftResult:
    drift_detected: bool
    model_name: str
    divergence_score: float
    threshold: float
    exit_code: int
    details: list[str] = field(default_factory=list)


class ModelDriftDetector:
    EXIT_CODE_DRIFT: int = 34
    # JS散度阈值: 基于JS divergence公式 0.5*(KL(P||M)+KL(Q||M)), 范围[0, ln2≈0.693]
    # 0.15≈最大散度的21.6%, 轻微漂移JS≈0.01(不触发), 显著漂移JS≈0.37(触发)
    DIVERGENCE_THRESHOLD: float = 0.15
    BASELINE_FILE: str = ".zephyr/model_baseline.json"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or REPO_ROOT
        self._baseline_path = self._project_root / self.BASELINE_FILE

    def establish_baseline(self, sample_outputs: list[dict[str, Any]]) -> bool:
        feature_vector = self._compute_feature_vector(sample_outputs)
        baseline = {
            "established_at": datetime.now(UTC).isoformat(),
            "feature_vector": feature_vector,
            "sample_count": len(sample_outputs),
        }
        self._baseline_path.parent.mkdir(parents=True, exist_ok=True)
        self._baseline_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def detect_drift(self, current_outputs: list[dict[str, Any]]) -> DriftResult:
        if not self._baseline_path.exists():
            return DriftResult(
                drift_detected=False,
                model_name="unknown",
                divergence_score=0.0,
                threshold=self.DIVERGENCE_THRESHOLD,
                exit_code=0,
                details=["No baseline established yet"],
            )

        try:
            baseline_data = json.loads(self._baseline_path.read_text(encoding="utf-8"))
            baseline_fv = baseline_data.get("feature_vector", {})
        except json.JSONDecodeError:
            return DriftResult(
                drift_detected=False,
                model_name="unknown",
                divergence_score=0.0,
                threshold=self.DIVERGENCE_THRESHOLD,
                exit_code=0,
                details=["Baseline file corrupted"],
            )

        current_fv = self._compute_feature_vector(current_outputs)
        divergence = self._js_divergence(baseline_fv, current_fv)
        drifted = divergence > self.DIVERGENCE_THRESHOLD

        details: list[str] = []
        details.append(f"Divergence score: {divergence:.4f} (threshold: {self.DIVERGENCE_THRESHOLD})")
        if drifted:
            details.append("MODEL_DRIFT_DETECTED: LLM behavior has silently changed")

        return DriftResult(
            drift_detected=drifted,
            model_name="default",
            divergence_score=divergence,
            threshold=self.DIVERGENCE_THRESHOLD,
            exit_code=self.EXIT_CODE_DRIFT if drifted else 0,
            details=details,
        )

    def _compute_feature_vector(self, outputs: list[dict[str, Any]]) -> dict[str, float]:
        features: dict[str, float] = {}
        if not outputs:
            return features

        total = len(outputs)
        for i, output in enumerate(outputs):
            text = json.dumps(output, ensure_ascii=False, sort_keys=True)
            key = hashlib.sha256(text.encode()).hexdigest()[:16]
            features[key] = features.get(key, 0.0) + 1.0 / total

        return features

    def _js_divergence(self, p: dict[str, float], q: dict[str, float]) -> float:
        all_keys = set(p.keys()) | set(q.keys())
        if not all_keys:
            return 0.0

        m: dict[str, float] = {}
        for k in all_keys:
            m[k] = 0.5 * (p.get(k, 0.0) + q.get(k, 0.0))

        kl_pm = 0.0
        kl_qm = 0.0
        for k in all_keys:
            pk = p.get(k, 1e-10)
            qk = q.get(k, 1e-10)
            mk = m.get(k, 1e-10)
            if pk > 0 and mk > 0:
                kl_pm += pk * math.log(pk / mk)
            if qk > 0 and mk > 0:
                kl_qm += qk * math.log(qk / mk)

        return 0.5 * (kl_pm + kl_qm)
