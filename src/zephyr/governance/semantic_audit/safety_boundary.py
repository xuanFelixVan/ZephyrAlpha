# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 3
# [MODULE] zephyr.governance.semantic_audit.safety_boundary
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.semantic_audit.models
# [CONSUMERS] issue_aggregator; alignment_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 禁碰规则过滤; 置信度 < threshold -> HOLD; FORBIDDEN 规则 100% 阻断
# [MODIFY-GUARD] 修改过滤逻辑必须同步 forbidden_patterns.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 配置加载失败时默认 HOLD 所有 TriggerResult
# [TESTS] tests/semantic-auditor/test_safety_boundary.py
# [A_module] module_id=MOD-GOV_safety_boundary | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 安全边界 Stage 3

禁碰规则过滤 + 置信度阈值。输入 TriggerResult 列表,输出 SafetyDecision 分类。
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from zephyr.governance.semantic_audit.models import SafetyDecision, TriggerResult

logger = logging.getLogger(__name__)

__all__ = [
    "FilteredTrigger",
    "SafetyBoundary",
]

_FORBIDDEN_PATTERNS_PATH = Path(__file__).parent / "forbidden_patterns.yaml"


class FilteredTrigger:
    def __init__(self, trigger: TriggerResult, decision: SafetyDecision) -> None:
        self.trigger = trigger
        self.decision = decision


class SafetyBoundary:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config_path = Path(config_path) if config_path else _FORBIDDEN_PATTERNS_PATH
        self._forbidden_paths: list[str] = []
        self._forbidden_modules: list[str] = []
        self._forbidden_keywords: list[str] = []
        self._confidence_threshold: float = 0.95
        self._config_loaded = False

    def filter(self, triggers: list[TriggerResult]) -> list[FilteredTrigger]:
        if not self._config_loaded:
            self._load_config()
        results: list[FilteredTrigger] = []
        for t in triggers:
            decision = self._classify(t)
            results.append(FilteredTrigger(t, decision))
            if decision is not SafetyDecision.PROCEED:
                logger.debug(
                    "Trigger %s:%s -> %s (certainty=%.2f)",
                    t.trigger_type,
                    t.target_location,
                    decision,
                    t.certainty,
                )
        return results

    def _classify(self, trigger: TriggerResult) -> SafetyDecision:
        target = trigger.target_location.lower()
        for fp in self._forbidden_paths:
            if fp.lower() in target:
                return SafetyDecision.FORBIDDEN
        for mod in self._forbidden_modules:
            if mod.lower() in target:
                return SafetyDecision.FORBIDDEN
        for kw in self._forbidden_keywords:
            if kw.lower() in trigger.evidence.lower() or kw.lower() in target:
                return SafetyDecision.FORBIDDEN
        if trigger.certainty < self._confidence_threshold:
            return SafetyDecision.HOLD
        return SafetyDecision.PROCEED

    def _load_config(self) -> None:
        try:
            raw = self._config_path.read_text(encoding="utf-8")
            config = yaml.safe_load(raw) or {}
        except (OSError, yaml.YAMLError) as exc:
            # 修复 fail-open：配置加载失败时标记，_classify 将 HOLD 所有触发
            logger.warning("无法加载禁碰规则配置: %s, 默认 HOLD 所有触发", exc)
            self._config_load_failed = True
            self._config_loaded = True
            return
        self._forbidden_paths = config.get("forbidden_paths", [])
        self._forbidden_modules = config.get("forbidden_modules", [])
        self._forbidden_keywords = config.get("forbidden_keywords", [])
        self._confidence_threshold = float(config.get("confidence_threshold", 0.95))
        self._config_loaded = True
        logger.debug(
            "禁碰规则已加载: %d paths, %d modules, %d keywords, threshold=%.2f",
            len(self._forbidden_paths),
            len(self._forbidden_modules),
            len(self._forbidden_keywords),
            self._confidence_threshold,
        )

    def summary(self, filtered: list[FilteredTrigger]) -> dict[str, int]:
        counts: dict[str, int] = {"PROCEED": 0, "HOLD": 0, "FORBIDDEN": 0}
        for f in filtered:
            counts.setdefault(f.decision.value, 0)
            counts[f.decision.value] += 1
        return counts
