# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §4.1
# [MODULE] zephyr.governance.semantic_audit.trigger_engine
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.models; zephyr.governance.semantic_audit.reference_extractor
# [CONSUMERS] alignment_engine; audit-orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 增删改文件时判定是否触发审计；支持 cross_doc_ref_broken 和 dependson_chain_broken 两种触发类型
# [MODIFY-GUARD] 添加触发类型必须同步 models.TriggerResult.trigger_type 枚举
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无变更时返回 should_trigger=False, reason="no_changes"
# [TESTS] tests/semantic-auditor/test_trigger_engine.py
# [A_module] module_id=MOD-GOV_trigger_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 触发器引擎 Stage 2

监听文件变更，判定是否触发语义审计。
"""

from __future__ import annotations

import logging
from pathlib import Path

from zephyr.governance.semantic_audit.models import (
    ExtractedReferences,
    Severity,
    TriggerDecision,
    TriggerResult,
)
from zephyr.governance.semantic_audit.reference_extractor import ReferenceExtractor

logger = logging.getLogger(__name__)


class TriggerEngine:
    def __init__(self) -> None:
        self._extractor = ReferenceExtractor()
        self._baselines: dict[str, ExtractedReferences] = {}

    def build_baseline(self, file_paths: list[str]) -> None:
        self._baselines = self._extractor.extract_batch(file_paths)

    def evaluate(self, changed_files: list[str]) -> TriggerDecision:
        if not changed_files:
            return TriggerDecision(should_trigger=False, reason="no_changes")

        decision = TriggerDecision(should_trigger=False)
        results: list[TriggerResult] = []

        for fp in changed_files:
            current = self._extractor.extract(fp)
            baseline = self._baselines.get(fp)

            if baseline is None:
                results.extend(self._detect_broken_refs(current))
                continue

            results.extend(self._compare_references(baseline, current, fp))

        if results:
            decision.should_trigger = True
            decision.results = results
            decision.trigger_count = len(results)

            reds = sum(1 for r in results if r.severity is Severity.RED)
            yellows = sum(1 for r in results if r.severity is Severity.YELLOW)
            types = set(r.trigger_type for r in results)
            decision.trigger_type = ";".join(sorted(types))
            decision.reason = f"{reds} RED, {yellows} YELLOW triggers from {len(changed_files)} changed files"
        else:
            decision.reason = "no_triggers_detected"

        return decision

    def _detect_broken_refs(self, refs: ExtractedReferences) -> list[TriggerResult]:
        results: list[TriggerResult] = []

        for target in refs.depends_on_targets:
            target_path = self._resolve_relative_path(target.get("target", ""))
            if not target_path:
                continue
            if not target_path.exists():
                results.append(
                    TriggerResult(
                        trigger_type="cross_doc_ref_broken",
                        certainty=0.95,
                        severity=Severity.RED,
                        target_location=target.get("target", ""),
                        evidence=f"Referenced path does not exist: {target_path}",
                    )
                )

        for bid in refs.blueprint_links:
            target_path = self._resolve_relative_path(bid)
            if target_path and not target_path.exists():
                results.append(
                    TriggerResult(
                        trigger_type="cross_doc_ref_broken",
                        certainty=0.85,
                        severity=Severity.YELLOW,
                        target_location=bid,
                        evidence=f"Blueprint link target not found: {bid}",
                    )
                )

        return results

    def _compare_references(
        self,
        baseline: ExtractedReferences,
        current: ExtractedReferences,
        file_path: str,
    ) -> list[TriggerResult]:
        results: list[TriggerResult] = []

        old_paths = set(baseline.file_paths)
        new_paths = set(current.file_paths)
        removed = old_paths - new_paths

        for path in removed:
            results.append(
                TriggerResult(
                    trigger_type="dependson_chain_broken",
                    certainty=0.9,
                    severity=Severity.YELLOW,
                    target_location=path,
                    evidence=f"Dependency removed in {file_path}: {path}",
                )
            )

        old_blueprints = set(baseline.blueprint_links)
        new_blueprints = set(current.blueprint_links)
        broken_bps = old_blueprints - new_blueprints

        for bp in broken_bps:
            results.append(
                TriggerResult(
                    trigger_type="cross_doc_ref_broken",
                    certainty=0.7,
                    severity=Severity.YELLOW,
                    target_location=bp,
                    evidence=f"Blueprint link broken in {file_path}: {bp}",
                )
            )

        return results

    def _resolve_relative_path(self, target: str) -> Path | None:
        target = target.strip()
        if not target:
            return None
        candidates = [
            Path(target),
            Path.cwd() / "src" / "zephyr" / target,
            Path.cwd() / "docs" / target,
        ]
        for c in candidates:
            if c.exists():
                return c
        return candidates[0]
