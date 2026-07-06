# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.judge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.duplicate_detector; zephyr.governance.rule_enforcement.gate_types
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_judge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import importlib
import json
import logging
import re
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field

try:
    from zephyr.governance.audit_trail.finding_model import (
        AuditFinding,
        FindingDimension,
        FindingImpact,
        FindingLifecycle,
        FindingRemediation,
        FindingSeverity,
        FindingTarget,
        FindingTraceability,
        RecommendationBlock,
        RemediationAction,
        RemediationPriority,
        generate_finding_id,
    )

    _FINDING_AVAILABLE = True
except ImportError:
    _FINDING_AVAILABLE = False

logger = logging.getLogger(__name__)

__all__ = [
    "Confidence",
    "Judgment",
    "LayerResult",
    "OrphanJudge",
    "OrphanJudgeError",
    "OrphanJudgeReport",
    "Verdict",
]

_SYSTEM_CRITICAL_PATTERNS = [
    "src/zephyr/security/access_control/orphan_judge/",
    "src/zephyr/governance/rule_enforcement/phase_manager.py",
    "src/zephyr/governance/rule_enforcement/phase_check_registry.py",
    "src/zephyr/agent-rbac/",
    "src/zephyr/escalation/",
    "src/zephyr/behavioral-auditor/",
    "src/zephyr/asset-inventory/",
    "src/zephyr/kb/",
    "src/zephyr/mcp/governance_server.py",
    "scripts/scaffold.py",
    "scripts/lock_files.py",
    "docs/registry_of_registries.yaml",
]

_MAX_BATCH_SIZE = 200
_MAX_WORKERS = 8
_SAFETY_FENCE_MAX_DELETE_SIZE = 10000
_SAFETY_FENCE_RECENT_DAYS = 7

_DEGRADATION_DEFAULTS: dict[str, dict[str, Any]] = {
    "L0": {"passed": False, "data": {"is_registered": False}},
    "L1": {"passed": False, "data": {"is_reachable": False, "referenced_by": []}},
    "L2": {"passed": False, "data": {"is_duplicate": False, "is_uncertain": False}},
    "L3": {"passed": True, "data": {"has_unique": True, "is_uncertain": False}},
    "L4": {"passed": False, "data": {"has_value": False, "is_uncertain": True}},
}


class OrphanJudgeError(Exception):
    """OrphanJudge 模块基础异常"""

    error_code = "ZA-SC-0032"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class Verdict(str, Enum):
    KEEP = "KEEP"
    DELETE = "DELETE"
    EXTRACT_AND_MERGE = "EXTRACT_AND_MERGE"
    DEPRECATE = "DEPRECATE"
    ESCALATE = "ESCALATE"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerResult(BaseModel):
    layer: str
    passed: bool = False
    detail: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


class Judgment(BaseModel):
    judgment_id: str = Field(default_factory=lambda: f"j-{uuid.uuid4().hex[:12]}")
    path: str
    verdict: Verdict = Verdict.ESCALATE
    confidence: Confidence = Confidence.LOW
    layers: list[LayerResult] = Field(default_factory=list)
    reason: str = ""
    evidence: dict[str, Any] = Field(default_factory=dict)
    safety_blocked: bool = False
    requires_review: bool = False


class OrphanJudgeReport(BaseModel):
    total: int = 0
    by_verdict: dict[str, int] = Field(default_factory=dict)
    judgments: list[Judgment] = Field(default_factory=list)
    execution_time_ms: float = 0.0


class _CheckerProto(Protocol):
    def check(self, path: str) -> LayerResult: ...


class _DuplicateDetectorAdapter:
    """适配已有 DuplicateDetector.detect() → LayerResult check() 协议"""

    def __init__(self, detector: Any) -> None:
        self._detector = detector

    def check(self, path: str) -> LayerResult:
        result = self._detector.detect(path)
        return LayerResult(
            layer="L2",
            passed=result.has_duplicates,
            detail=f"Duplicate detection: {len(result.top_matches)} matches found",
            data={
                "is_duplicate": result.has_duplicates,
                "top_matches": [(p, s) for p, s in result.top_matches],
                "search_duration_ms": result.search_duration_ms,
                "is_uncertain": False,
            },
        )


def _try_import_checker(module_path: str, class_name: str) -> Any:
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name, None)
        if cls is not None:
            return cls()
    except Exception:
        logger.debug("Checker %s.%s not available, skipping", module_path, class_name, exc_info=True)
    return None


def _create_l2_checker() -> Any:
    try:
        from zephyr.security.access_control.orphan_judge.duplicate_detector import DuplicateDetector

        return _DuplicateDetectorAdapter(DuplicateDetector())
    except Exception:
        logger.debug("DuplicateDetector not available for L2, skipping", exc_info=True)
        return None


class OrphanJudge:
    """孤儿判定主控类——五层判定→决策路由→安全围栏→处置建议

    编排 L0(注册检查)→L1(引用图)→L2(重复检测)→L3(独特价值)→L4(独立价值)
    五层判定，经12行决策表路由，安全围栏兜底，输出确定性处置建议。
    """

    def __init__(
        self,
        *,
        l0_checker: Any | None = None,
        l1_checker: Any | None = None,
        l2_checker: Any | None = None,
        l3_checker: Any | None = None,
        l4_checker: Any | None = None,
        jsonl_output: bool = False,
    ) -> None:
        self.jsonl_output = jsonl_output
        self._l0 = l0_checker or _try_import_checker(
            "zephyr.security.access_control.orphan_judge.registration_checker", "RegistrationChecker"
        )
        self._l1 = l1_checker or _try_import_checker(
            "zephyr.security.access_control.orphan_judge.reference_graph_engine", "ReferenceGraphEngine"
        )
        self._l2 = l2_checker or _create_l2_checker()
        self._l3 = l3_checker or _try_import_checker(
            "zephyr.security.access_control.orphan_judge.unique_analyzer", "UniqueValueAnalyzer"
        )
        self._l4 = l4_checker or _try_import_checker(
            "zephyr.security.access_control.orphan_judge.standalone_evaluator", "StandaloneEvaluator"
        )

    def _output_findings_as_jsonl(self, judgments: list[Judgment]) -> None:
        if not _FINDING_AVAILABLE:
            return
        verdict_severity: dict[Verdict, FindingSeverity] = {
            Verdict.DELETE: FindingSeverity.CRITICAL,
            Verdict.ESCALATE: FindingSeverity.HIGH,
            Verdict.DEPRECATE: FindingSeverity.MEDIUM,
            Verdict.EXTRACT_AND_MERGE: FindingSeverity.LOW,
            Verdict.KEEP: FindingSeverity.INFO,
        }
        for j in judgments:
            severity = verdict_severity.get(j.verdict, FindingSeverity.MEDIUM)
            finding = AuditFinding(
                finding_id=generate_finding_id("D1", j.reason),
                dimension=FindingDimension.D1,
                severity=severity,
                category="孤儿判定",
                target=FindingTarget(file_path=j.path),
                description=j.reason,
                evidence=json.dumps(j.evidence, ensure_ascii=False) if j.evidence else "",
                remediation=FindingRemediation(
                    action=RemediationAction.INVESTIGATE if j.verdict == Verdict.ESCALATE else RemediationAction.FIX,
                    priority=RemediationPriority.P1
                    if severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH)
                    else RemediationPriority.P2,
                ),
            )
            sys.stdout.write(finding.to_jsonl())

    def _jsonl_judgment(self, judgment: Judgment) -> Judgment:
        if self.jsonl_output and _FINDING_AVAILABLE:
            self._output_findings_as_jsonl([judgment])
        return judgment

    def judge(self, path: str, dry_run: bool = True) -> Judgment:
        """单文件判定：L0→L1→L2→L3→L4→决策表→安全围栏→处置建议"""
        target = Path(path)
        if not target.exists():
            raise OrphanJudgeError("File not found")

        layers: list[LayerResult] = []

        l0 = self._run_layer(self._l0, path, "L0")
        layers.append(l0)
        if l0.data.get("is_registered", l0.passed):
            return self._jsonl_judgment(
                Judgment(
                    path=path,
                    verdict=Verdict.KEEP,
                    confidence=Confidence.HIGH,
                    layers=layers,
                    reason="File is registered in at least one registry",
                    evidence={"registered_in": l0.data.get("registered_in", [])},
                )
            )

        l1 = self._run_layer(self._l1, path, "L1")
        layers.append(l1)
        if l1.data.get("is_reachable", l1.passed):
            return self._jsonl_judgment(
                Judgment(
                    path=path,
                    verdict=Verdict.KEEP,
                    confidence=Confidence.HIGH,
                    layers=layers,
                    reason="File is reachable via import chain but not registered",
                    evidence={"referenced_by": l1.data.get("referenced_by", [])},
                )
            )

        l2 = self._run_layer(self._l2, path, "L2")
        layers.append(l2)

        l3 = self._run_layer(self._l3, path, "L3")
        layers.append(l3)

        l4 = self._run_layer(self._l4, path, "L4")
        layers.append(l4)

        if l4.data.get("is_uncertain", False) and "not available" in l4.detail:
            return self._jsonl_judgment(
                Judgment(
                    path=path,
                    verdict=Verdict.ESCALATE,
                    confidence=Confidence.LOW,
                    layers=layers,
                    reason="L4 standalone evaluator unavailable, cannot determine value",
                    requires_review=True,
                )
            )

        verdict, confidence, reason = self._decision_route(l2, l3, l4)

        safety_blocked = self._safety_fence(path, verdict)
        if safety_blocked:
            original_reason = reason
            verdict = Verdict.ESCALATE
            confidence = Confidence.LOW
            reason = f"Safety fence blocked: {original_reason}"

        return self._jsonl_judgment(
            Judgment(
                path=path,
                verdict=verdict,
                confidence=confidence,
                layers=layers,
                reason=reason,
                safety_blocked=safety_blocked,
                requires_review=verdict == Verdict.ESCALATE or confidence is not Confidence.HIGH,
            )
        )

    def batch_judge(
        self,
        scope: str = "src/zephyr/",
        limit: int = 200,
        dry_run: bool = True,
    ) -> OrphanJudgeReport:
        """批量判定（RULE-SEVEN: ThreadPoolExecutor max_workers=8）"""
        start = time.monotonic()
        scope_path = Path(scope)
        if not scope_path.is_dir():
            scope_path = Path.cwd() / scope

        candidates: list[str] = []
        if scope_path.is_dir():
            for py_file in scope_path.rglob("*.py"):
                if any(p in py_file.parts for p in ("__pycache__", ".mypy_cache", "_snapshots", ".aidrafts")):
                    continue
                candidates.append(str(py_file))
                if len(candidates) >= min(limit, _MAX_BATCH_SIZE):
                    break

        judgments: list[Judgment] = []
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            futures = {pool.submit(self.judge, p, dry_run): p for p in candidates}
            for future in as_completed(futures):
                path = futures[future]
                try:
                    judgments.append(future.result())
                except Exception as exc:
                    logger.warning("Judge failed for %s: %s", path, exc, exc_info=True)
                    judgments.append(
                        Judgment(
                            path=path,
                            verdict=Verdict.ESCALATE,
                            confidence=Confidence.LOW,
                            reason=f"Judge failed: {exc}",
                        )
                    )

        by_verdict: dict[str, int] = {}
        for j in judgments:
            key = j.verdict.value
            by_verdict[key] = by_verdict.get(key, 0) + 1

        elapsed_ms = (time.monotonic() - start) * 1000
        return OrphanJudgeReport(
            total=len(judgments),
            by_verdict=by_verdict,
            judgments=judgments,
            execution_time_ms=round(elapsed_ms, 2),
        )

    def quick_scan(self) -> Any:
        """快速扫描（Phase Gate用，仅L0+L1快速路径判定）

        返回 GateResult:
          GREEN(无孤儿)/YELLOW(有孤儿无ESCALATE)/RED(有ESCALATE)
        """
        try:
            from zephyr.governance.rule_enforcement.gate_types import GateResult, GateViolation
        except ImportError:
            raise OrphanJudgeError(
                "GateResult not available; ensure zephyr.governance.rule_enforcement.gate_types is importable"
            )

        report = self.batch_judge(limit=50, dry_run=True)
        escalate_count = report.by_verdict.get(Verdict.ESCALATE.value, 0)
        delete_count = report.by_verdict.get(Verdict.DELETE.value, 0)
        keep_count = report.by_verdict.get(Verdict.KEEP.value, 0)
        orphan_count = report.total - keep_count

        violations: list[GateViolation] = []
        if orphan_count > 0:
            severity = "P0" if escalate_count > 0 else "P1"
            violations.append(
                GateViolation(
                    check_id="orphan_judge_quick_scan",
                    check_name="orphan-judge",
                    severity=severity,
                    message=(f"Found {orphan_count} orphan files ({escalate_count} ESCALATE, {delete_count} DELETE)"),
                )
            )

        return GateResult(
            gate_id="gate_orphan_judge",
            task_id="quick_scan",
            passed=orphan_count == 0,
            violations=violations,
            details={"by_verdict": report.by_verdict, "total": report.total},
        )

    @staticmethod
    def _run_layer(checker: Any, path: str, layer_name: str) -> LayerResult:
        """执行单层判定，checker不可用时按蓝图§6降级原则返回默认值"""
        if checker is None:
            default = _DEGRADATION_DEFAULTS.get(layer_name, {"passed": False, "data": {}})
            return LayerResult(
                layer=layer_name,
                passed=default["passed"],
                detail=f"{layer_name} checker not available, using degradation default",
                data=dict(default["data"]),
            )
        try:
            result = checker.check(path)
            if isinstance(result, LayerResult):
                return result
            return LayerResult(
                layer=layer_name,
                passed=bool(result),
                detail=f"{layer_name} checker returned non-LayerResult",
            )
        except Exception as exc:
            logger.warning("%s checker failed for %s: %s", layer_name, path, exc, exc_info=True)
            default = _DEGRADATION_DEFAULTS.get(layer_name, {"passed": False, "data": {}})
            return LayerResult(
                layer=layer_name,
                passed=default["passed"],
                detail=f"{layer_name} checker error: {exc}",
                data=dict(default["data"]),
            )

    @staticmethod
    def _decision_route(
        l2: LayerResult,
        l3: LayerResult,
        l4: LayerResult,
    ) -> tuple[Verdict, Confidence, str]:
        """12行决策表路由（蓝图特有§B3）

        输入: L2(重复检测)/L3(独特价值)/L4(独立价值) 的判定结果
        输出: (Verdict, Confidence, reason)
        """
        is_dup = l2.data.get("is_duplicate", False)
        l2_uncertain = l2.data.get("is_uncertain", False)
        has_unique = l3.data.get("has_unique", False)
        l3_uncertain = l3.data.get("is_uncertain", False)
        has_value = l4.data.get("has_value", False)
        l4_uncertain = l4.data.get("is_uncertain", False)
        value_confidence = l4.data.get("value_confidence", "low")

        if l2_uncertain:
            return Verdict.ESCALATE, Confidence.LOW, "L2 duplicate detection uncertain"

        if is_dup and l3_uncertain:
            return Verdict.ESCALATE, Confidence.LOW, "Duplicate with uncertain unique value"

        if is_dup and has_unique:
            if l3.data.get("unique_confidence") == "low":
                return (
                    Verdict.EXTRACT_AND_MERGE,
                    Confidence.MEDIUM,
                    "Duplicate with few unique elements, extract and merge with deprecation",
                )
            return (
                Verdict.EXTRACT_AND_MERGE,
                Confidence.HIGH,
                "Duplicate with unique elements, extract and merge",
            )

        if is_dup and not has_unique:
            return Verdict.DELETE, Confidence.HIGH, "Duplicate with no unique value"

        if not is_dup and l4_uncertain:
            return Verdict.ESCALATE, Confidence.LOW, "Not duplicate but standalone value uncertain"

        if not is_dup and has_value and value_confidence in ("high", "medium"):
            return (
                Verdict.KEEP,
                Confidence.HIGH,
                "Not duplicate with standalone value, needs registration",
            )

        if not is_dup and has_value and value_confidence == "low":
            return (
                Verdict.DEPRECATE,
                Confidence.MEDIUM,
                "Not duplicate with low-confidence value, deprecate first",
            )

        if not is_dup and not has_value:
            return Verdict.DELETE, Confidence.MEDIUM, "Not duplicate with no standalone value"

        return (
            Verdict.ESCALATE,
            Confidence.LOW,
            "Unable to determine verdict with sufficient confidence",
        )

    @staticmethod
    def _safety_fence(path: str, verdict: Verdict) -> bool:
        """安全围栏：不删除 frozen/H 文件、系统关键文件、大文件、近期修改文件"""
        if verdict not in (Verdict.DELETE, Verdict.DEPRECATE):
            return False

        normalized = Path(path).as_posix()
        for pattern in _SYSTEM_CRITICAL_PATTERNS:
            if pattern.endswith("/"):
                if normalized.startswith(pattern):
                    return True
            elif normalized == pattern:
                return True

        target = Path(path)
        try:
            content = target.read_text(encoding="utf-8")
            stability_match = re.search(r"\[STABILITY\]\s*(\w+)", content)
            if stability_match and stability_match.group(1) == "frozen":
                return True
            safety_match = re.search(r"\[SAFETY\]\s*(\w+)", content)
            if safety_match and safety_match.group(1) == "H":
                return True
        except (OSError, UnicodeDecodeError):
            pass

        try:
            stat_info = target.stat()
            if stat_info.st_size > _SAFETY_FENCE_MAX_DELETE_SIZE:
                logger.info(
                    "Safety fence: large file (%d bytes) blocked for %s",
                    stat_info.st_size,
                    path,
                )
                return True
            age_days = (time.time() - stat_info.st_mtime) / 86400
            if age_days < _SAFETY_FENCE_RECENT_DAYS:
                logger.info(
                    "Safety fence: recently modified (%.1f days) blocked for %s",
                    age_days,
                    path,
                )
                return True
        except OSError:
            pass

        return False