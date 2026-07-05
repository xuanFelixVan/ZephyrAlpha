# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3,§4
# [MODULE] zephyr.governance.semantic_audit.orchestrator
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] audit_orchestrator; cli; gates
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 9阶段管道顺序执行; audit()返回SemanticAuditReport; audit_batch()使用ThreadPoolExecutor并行; health_check()返回HealthStatus
# [MODIFY-GUARD] blueprint.md §3,§4; semantic_audit/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] audit() never raises; individual stage failures are logged and skipped; returns partial report
# [TESTS] tests/test_semantic_auditor.py
# [A_module] module_id=MOD-GOV_semantic_audit_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SemanticAuditor 编排器——9阶段管道统一调度.

依据蓝图 MOD-INF-028 §3 架构设计:
- Stage 1: ReferenceExtractor — 9种引用维度提取
- Stage 2: TriggerEngine — F+G 两类纯语义触发检测
- Stage 3: SafetyBoundary — 禁碰规则过滤+置信度阈值
- Stage 4: AlignmentEngine — 注册表↔磁盘双向对齐(6对)
- Stage 5: IssueAggregator — 去重聚合问题清单
- Stage 6: LLMBridge — LLM修复文本生成+模板降级
- Stage 7: SelfHealer — 自愈闭环(修复→自测→回滚)
- Stage 8: FixPrioritizer — 修复优先级排序+批处理分组
- Stage 9: BlastRadius — 影响爆炸半径+级联过时检测(可选)
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = [
    "AuditMode",
    "SemanticAuditor",
]


class AuditMode(str):
    """审计模式枚举。"""

    FULL = "full"
    INCREMENTAL = "incremental"
    DETECT_ONLY = "detect-only"


class SemanticAuditor:
    """语义审计主类——2类纯语义触发+9阶段管道.

    依据蓝图 MOD-INF-028 §4.1 公共API契约:
    - audit(doc_path, mode): 审计单个规则文档
    - audit_batch(doc_paths, mode): 批量审计(增量模式默认)
    - health_check(): 自身健康检查
    """

    def __init__(
        self,
        project_root: str | Path = ".",
        llm_api_available: bool = False,
        max_workers: int = 4,
    ) -> None:
        self._root = Path(project_root).resolve()
        self._max_workers = max_workers
        self._llm_available = llm_api_available
        self._init_stages()

    def _init_stages(self) -> None:
        """初始化9阶段管道组件。"""
        try:
            from zephyr.governance.semantic_audit.reference_extractor import ReferenceExtractor
            self._extractor = ReferenceExtractor()
        except Exception as exc:
            logger.warning("ReferenceExtractor init failed: %s", exc)
            self._extractor = None

        try:
            from zephyr.governance.semantic_audit.trigger_engine import TriggerEngine
            self._trigger_engine = TriggerEngine()
        except Exception as exc:
            logger.warning("TriggerEngine init failed: %s", exc)
            self._trigger_engine = None

        try:
            from zephyr.governance.semantic_audit.safety_boundary import SafetyBoundary
            self._safety_boundary = SafetyBoundary()
        except Exception as exc:
            logger.warning("SafetyBoundary init failed: %s", exc)
            self._safety_boundary = None

        try:
            from zephyr.governance.semantic_audit.alignment_engine import AlignmentEngine
            self._alignment_engine = AlignmentEngine(project_root=self._root)
        except Exception as exc:
            logger.warning("AlignmentEngine init failed: %s", exc)
            self._alignment_engine = None

        try:
            from zephyr.governance.semantic_audit.issue_aggregator import IssueAggregator
            self._aggregator = IssueAggregator()
        except Exception as exc:
            logger.warning("IssueAggregator init failed: %s", exc)
            self._aggregator = None

        try:
            from zephyr.governance.semantic_audit.llm_bridge import LLMBridge
            self._llm_bridge = LLMBridge(api_available=self._llm_available)
        except Exception as exc:
            logger.warning("LLMBridge init failed: %s", exc)
            self._llm_bridge = None

        try:
            from zephyr.governance.semantic_audit.self_healer import SelfHealer
            self._self_healer = SelfHealer()
        except Exception as exc:
            logger.warning("SelfHealer init failed: %s", exc)
            self._self_healer = None

        try:
            from zephyr.governance.semantic_audit.fix_prioritizer import FixPrioritizer
            self._fix_prioritizer = FixPrioritizer()
        except Exception as exc:
            logger.warning("FixPrioritizer init failed: %s", exc)
            self._fix_prioritizer = None

        try:
            from zephyr.governance.semantic_audit.self_health import SelfHealth
            self._self_health = SelfHealth(project_root=self._root)
        except Exception as exc:
            logger.warning("SelfHealth init failed: %s", exc)
            self._self_health = None

    def audit(self, doc_path: Path | str, mode: str = "full") -> BaseModel:
        """审计单个规则文档.

        输入: doc_path 规则文档路径, mode=full/incremental/detect-only
        输出: SemanticAuditReport 含所有触发+对齐+修复结果
        核心逻辑: 9阶段管道顺序执行
        """
        from zephyr.governance.semantic_audit.models import (
            AlignmentReport,
            HealResult,
            LLMFixResult,
            SemanticAuditReport,
            TriggerResult,
        )

        start_time = time.monotonic()
        doc_path = Path(doc_path)
        audit_id = f"audit-{uuid.uuid4().hex[:8]}"
        total_token = 0

        if not doc_path.exists():
            logger.warning("Document not found: %s", doc_path)
            return SemanticAuditReport(
                audit_id=audit_id,
                rule_document=str(doc_path),
                duration_ms=0,
            )

        # Stage 1: ReferenceExtractor
        references = None
        if self._extractor is not None:
            try:
                references = self._extractor.extract(doc_path)
            except Exception as exc:
                logger.warning("Stage 1 extract failed for %s: %s", doc_path, exc)

        # Stage 2: TriggerEngine
        triggers: list[TriggerResult] = []
        if self._trigger_engine is not None:
            try:
                decision = self._trigger_engine.evaluate([str(doc_path)])
                triggers = list(decision.results) if decision.should_trigger else []
            except Exception as exc:
                logger.warning("Stage 2 trigger failed for %s: %s", doc_path, exc)

        # Stage 3: SafetyBoundary
        filtered_triggers = triggers
        if self._safety_boundary is not None and triggers:
            try:
                filtered = self._safety_boundary.filter(triggers)
                filtered_triggers = [t.trigger for t in filtered if hasattr(t, "trigger")]
            except Exception as exc:
                logger.warning("Stage 3 safety filter failed for %s: %s", doc_path, exc)

        # Stage 4: AlignmentEngine
        alignments: list[AlignmentReport] = []
        if self._alignment_engine is not None and mode != "detect-only":
            try:
                module_id = self._extract_module_id(doc_path)
                if module_id:
                    report = self._alignment_engine.align(module_id)
                    alignments = [report]
            except Exception as exc:
                logger.warning("Stage 4 alignment failed for %s: %s", doc_path, exc)

        # Stage 6: LLMBridge (skip in detect-only mode)
        fixes: list[LLMFixResult] = []
        if mode != "detect-only" and self._llm_bridge is not None and filtered_triggers:
            try:
                fixes = self._llm_bridge.generate_fix_batch(filtered_triggers)
                total_token += sum(f.token_used for f in fixes)
            except Exception as exc:
                logger.warning("Stage 6 LLM bridge failed for %s: %s", doc_path, exc)

        # Stage 7: SelfHealer (skip in detect-only mode)
        heals: list[HealResult] = []
        if mode == "full" and self._self_healer is not None and fixes:
            try:
                for fix, trigger in zip(fixes, filtered_triggers, strict=False):
                    if fix.success:
                        heal = self._self_healer.heal(
                            target_path=str(doc_path),
                            issue_description=trigger.evidence,
                            fix_suggestion=fix.fix_text,
                        )
                        heals.append(heal)
            except Exception as exc:
                logger.warning("Stage 7 self heal failed for %s: %s", doc_path, exc)

        # Stage 5: IssueAggregator
        report = SemanticAuditReport(audit_id=audit_id, rule_document=str(doc_path))
        if self._aggregator is not None:
            try:
                duration_ms = int((time.monotonic() - start_time) * 1000)
                report = self._aggregator.aggregate(
                    audit_id=audit_id,
                    rule_document=str(doc_path),
                    triggers=filtered_triggers,
                    alignments=alignments,
                    fixes=fixes,
                    heals=heals,
                    duration_ms=duration_ms,
                    token_used=total_token,
                )
            except Exception as exc:
                logger.warning("Stage 5 aggregate failed for %s: %s", doc_path, exc)

        return report

    def audit_batch(self, doc_paths: list[Path | str], mode: str = "incremental") -> list[BaseModel]:
        """批量审计(增量模式默认).

        输入: doc_paths 变更文档列表
        输出: 每个文档的审计报告
        核心逻辑: ThreadPoolExecutor 并行审计
        """
        if not doc_paths:
            return []

        results: list[BaseModel] = []
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_path = {
                executor.submit(self.audit, Path(p), mode): p for p in doc_paths
            }
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    report = future.result()
                    results.append(report)
                except Exception as exc:
                    logger.warning("Batch audit failed for %s: %s", path, exc)
        return results

    def health_check(self) -> BaseModel:
        """自身健康检查.

        输入: 无
        输出: HealthStatus 含 7 SLI + 5 容量 SLI
        核心逻辑: 黄金数据集回归 + 禁碰规则完整性 + Token 趋势
        """
        if self._self_health is not None:
            try:
                return self._self_health.check(force=True)
            except Exception as exc:
                logger.warning("Health check failed: %s", exc)

        # 降级: 返回最小健康状态
        from zephyr.governance.semantic_audit.self_health import HealthStatus, HealthLevel
        return HealthStatus(level=HealthLevel.DEGRADED, reason="self_health unavailable")

    def _extract_module_id(self, doc_path: Path) -> str:
        """从文档路径提取 module_id."""
        try:
            content = doc_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                if "module_id:" in line.lower():
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        return parts[1].strip().strip('"').strip("'")
                if line.startswith("> module_id:"):
                    parts = line.split(":", 2)
                    if len(parts) > 2:
                        return parts[2].strip().split()[0]
        except Exception as e:
            logger.warning("suppressed error in orchestrator", exc_info=True)
        return doc_path.stem


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m zephyr.governance.semantic_audit.orchestrator <doc_path> [mode]")
        sys.exit(1)

    doc_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    auditor = SemanticAuditor()
    report = auditor.audit(doc_path, mode=mode)
    print(f"audit_id: {report.audit_id}")
    print(f"rule_document: {report.rule_document}")
    print(f"total_triggers: {report.total_triggers}")
    print(f"red_issues: {len(report.red_issues)}")
    print(f"yellow_issues: {len(report.yellow_issues)}")
    print(f"duration_ms: {report.duration_ms}")
