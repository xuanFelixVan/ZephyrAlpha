# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.orphan_collector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.cascade_analyzer; zephyr.security.access_control.orphan_judge.decision_table; zephyr.security.access_control.orphan_judge.safety_fence; zephyr.security.access_control.orphan_judge.deprecation_tracker
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_orphan_collector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
from pathlib import Path

from pydantic import BaseModel

from zephyr.security.access_control.orphan_judge.cascade_analyzer import CascadeAnalyzer
from zephyr.security.access_control.orphan_judge.decision_table import DecisionTable, Verdict
from zephyr.security.access_control.orphan_judge.safety_fence import SafetyFence

logger = logging.getLogger(__name__)


class CollectionResult(BaseModel):
    total: int = 0
    disposed: int = 0
    kept: int = 0
    escalated: int = 0
    errors: int = 0


class Judgment(BaseModel):
    path: str
    verdict: Verdict
    reason: str = ""


class OrphanCollectorError(Exception):
    error_code = "ZA-SC-0033"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class OrphanCollector:
    """孤儿文件收集与处置器——整合 SafetyFence 安全检查后执行处置动作。

    处置策略：
      KEEP / KEEP_AND_REGISTER → 保留（计数 kept）
      DELETE → 通过 SafetyFence + CascadeAnalyzer 后删除（计数 disposed）
      EXTRACT_AND_MERGE → 保留，标记为待合并（计数 kept）
      DEPRECATE → 调用 DeprecationTracker 标记废弃（计数 kept）
      ESCALATE → 上报人工处理（计数 escalated）
    """

    def __init__(
        self,
        project_root: str | Path | None = None,
        safety_fence: SafetyFence | None = None,
        cascade_analyzer: CascadeAnalyzer | None = None,
        decision_table: DecisionTable | None = None,
        dry_run: bool = False,
    ) -> None:
        if project_root is None:
            self._root = Path.cwd()
        else:
            self._root = Path(project_root).resolve()
        self._safety = safety_fence or SafetyFence(project_root=self._root)
        self._cascade = cascade_analyzer or CascadeAnalyzer(project_root=self._root)
        self._table = decision_table or DecisionTable()
        self._dry_run = dry_run

    def collect(self, judgments: list[Judgment]) -> CollectionResult:
        result = CollectionResult(total=len(judgments))

        for judgment in judgments:
            try:
                success = self.execute_disposal(judgment)
                if success:
                    if judgment.verdict in (Verdict.DELETE,):
                        result.disposed += 1
                    elif judgment.verdict == Verdict.ESCALATE:
                        result.escalated += 1
                    else:
                        result.kept += 1
                else:
                    result.errors += 1
            except Exception as exc:
                logger.error("Error processing judgment for %s: %s", judgment.path, exc, exc_info=True)
                result.errors += 1

        return result

    def execute_disposal(self, judgment: Judgment) -> bool:
        verdict = judgment.verdict
        path = judgment.path

        if verdict in (Verdict.KEEP, Verdict.KEEP_AND_REGISTER):
            logger.info("KEEP: %s — %s", path, judgment.reason)
            return True

        if verdict == Verdict.EXTRACT_AND_MERGE:
            logger.info("EXTRACT_AND_MERGE: %s — %s", path, judgment.reason)
            return True

        if verdict == Verdict.DEPRECATE:
            return self._handle_deprecate(path, judgment.reason)

        if verdict == Verdict.ESCALATE:
            logger.warning("ESCALATE: %s — %s", path, judgment.reason)
            return True

        if verdict == Verdict.DELETE:
            return self._handle_delete(path, judgment.reason)

        logger.warning("Unknown verdict %s for %s", verdict, path)
        return False

    def _handle_delete(self, path: str, reason: str) -> bool:
        safety_result = self._safety.check_safety(path, "delete")
        if not safety_result.allowed:
            logger.warning(
                "DELETE blocked by safety fence for %s: %s",
                path,
                safety_result.reason,
            )
            return False

        cascade_result = self._cascade.analyze_cascade(path)
        if not cascade_result.safe_to_delete:
            logger.warning(
                "DELETE blocked by cascade analysis for %s: risk=%s, direct_deps=%d, indirect_deps=%d",
                path,
                cascade_result.cascade_risk.value,
                len(cascade_result.direct_dependents),
                len(cascade_result.indirect_dependents),
            )
            return False

        if self._dry_run:
            logger.info("DRY RUN: would delete %s", path)
            return True

        resolved = Path(path)
        if not resolved.is_absolute():
            resolved = (self._root / path).resolve()

        try:
            if resolved.exists():
                tmp_path = f"{resolved}.{os.getpid()}.deleting"
                os.replace(str(resolved), tmp_path)
                os.remove(tmp_path)
                logger.info("DELETED: %s — %s", path, reason)
                return True
            else:
                logger.warning("File not found for deletion: %s", path)
                return False
        except OSError as exc:
            logger.error("Failed to delete %s: %s", path, exc)
            return False

    def _handle_deprecate(self, path: str, reason: str) -> bool:
        try:
            from zephyr.security.access_control.orphan_judge.deprecation_tracker import DeprecationTracker

            tracker = DeprecationTracker(project_root=self._root)
            tracker.deprecate(path, ttl_days=30, reason=reason)
            logger.info("DEPRECATED: %s — %s", path, reason)
            return True
        except Exception as exc:
            logger.error("Failed to deprecate %s: %s", path, exc, exc_info=True)
            return False