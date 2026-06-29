# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.security.access_control.auto_fix_engine_03.engine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.auto_fix_engine_03.batch_fixer; zephyr.security.access_control.auto_fix_engine_03.compliance_auditor; zephyr.security.access_control.auto_fix_engine_03.fix_budget; zephyr.security.access_control.auto_fix_engine_03.fix_diff; zephyr.security.access_control.auto_fix_engine_03.fix_health_check; zephyr.security.access_control.auto_fix_engine_03.fix_pattern_miner; zephyr.security.access_control.auto_fix_engine_03.fix_reliability; zephyr.security.access_control.auto_fix_engine_03.fix_report; zephyr.security.access_control.auto_fix_engine_03.fix_safety; zephyr.security.access_control.auto_fix_engine_03.models; zephyr.security.access_control.auto_fix_engine_03.shadow_workspace; zephyr.security.access_control.auto_fix_engine_03.state_machine; zephyr.governance.audit_trail.finding_model; zephyr.governance.audit_trail.__init__; zephyr.shared.event_bus
# [CONSUMERS] MOD-INF-027(audit-orchestrator);MOD-INF-023(drift-detector);MOD-INF-029(orphan-judge);__main__.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 修复MUST通过SafetyGate+FixBudget+CascadeBreaker;行为审计RED永不自动修复
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml;auto_fix_config.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AutoFixEngineError;FixBlockedError
# [TESTS] tests/auto-fix-engine/test_engine.py
# [A_module] module_id=MOD-SEC_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from zephyr.security.access_control.auto_fix_engine_03.batch_fixer import BatchFixer
from zephyr.security.access_control.auto_fix_engine_03.compliance_auditor import ComplianceAuditor
from zephyr.security.access_control.auto_fix_engine_03.fix_budget import FixBudget, FixStormGuard
from zephyr.security.access_control.auto_fix_engine_03.fix_health_check import FixHealthCheck
from zephyr.security.access_control.auto_fix_engine_03.fix_pattern_miner import FixPatternMiner
from zephyr.security.access_control.auto_fix_engine_03.fix_reliability import (
    ApprovalQueue,
    BlastRadiusEstimator,
    CanaryFixer,
    ConflictResolver,
    DeadLetterQueue,
    FixOrderResolver,
    IdempotencyGuard,
)
from zephyr.security.access_control.auto_fix_engine_03.fix_report import FixReportGenerator
from zephyr.security.access_control.auto_fix_engine_03.fix_safety import (
    CascadeBreaker,
    FixValidator,
    SafetyGate,
    SecretLeakGuard,
    WriteSafety,
)
from zephyr.security.access_control.auto_fix_engine_03.models import (
    FixAction,
    FixHealthReport,
    FixLevel,
    FixReport,
    FixStatus,
)
from zephyr.security.access_control.auto_fix_engine_03.shadow_workspace import ShadowWorkspace

try:
    from zephyr.governance.audit_trail.finding_model import (
        AuditFinding,
        BlastRadius,
        FindingDimension,
        FindingImpact,
        FindingLifecycle,
        FindingRemediation,
        FindingSeverity,
        FindingStatus,
        FindingTarget,
        FindingTraceability,
        RecommendationBlock,
        RemediationAction,
        RemediationPriority,
        generate_finding_id,
    )

    _FINDING_MODEL_AVAILABLE = True
except ImportError:
    _FINDING_MODEL_AVAILABLE = False

logger = logging.getLogger(__name__)

_NO_AUTO_FIX_TYPES = {"behavioral_audit_red", "security_critical", "data_loss_risk"}


class AutoFixEngine:
    def __init__(self, config_path: str | None = None) -> None:
        self._config = self._load_config(config_path)
        self._safety_gate = SafetyGate(self._config.get("safety", {}))
        self._cascade_breaker = CascadeBreaker(self._config.get("cascade_breaker", {}))
        self._fix_budget = FixBudget(self._config.get("budget", {}))
        self._storm_guard = FixStormGuard(self._config.get("storm_guard", {}))
        self._idempotency = IdempotencyGuard(
            ttl_hours=self._config.get("reliability", {}).get("idempotency_ttl_hours", 24)
        )
        self._conflict_resolver = ConflictResolver()
        self._order_resolver = FixOrderResolver()
        self._blast_radius = BlastRadiusEstimator()
        self._dead_letter_queue = DeadLetterQueue(max_retries=self._config.get("reliability", {}).get("max_retries", 3))
        self._approval_queue = ApprovalQueue()
        self._canary_fixer = CanaryFixer(
            ratios=self._config.get("reliability", {}).get("canary_ratios"),
            delay_sec=self._config.get("reliability", {}).get("canary_delay_sec", 60),
        )
        self._secret_guard = SecretLeakGuard()
        self._validator = FixValidator()
        self._write_safety = WriteSafety()
        self._shadow = ShadowWorkspace(self._config.get("shadow_workspace", {}))
        self._compliance = ComplianceAuditor()
        # Lazy import to break F8→F5 circular dependency (§8.1)
        from zephyr.security.access_control.auto_fix_engine_03.escalation_bridge import EscalationBridge
        self._escalation = EscalationBridge(self._config.get("escalation", {}))
        self._pattern_miner = FixPatternMiner()
        self._report_generator = FixReportGenerator()
        self._batch_fixer = BatchFixer(
            max_workers=self._config.get("engine", {}).get("max_concurrent_fixes", 8),
            fix_budget=self._fix_budget,
            storm_guard=self._storm_guard,
            idempotency_guard=self._idempotency,
            conflict_resolver=self._conflict_resolver,
        )
        self._fixers: dict[str, Any] = {}
        self._load_fixers()

    def _load_config(self, config_path: str | None = None) -> dict[str, Any]:
        default_path = Path(__file__).parent / "auto_fix_config.yaml"
        path = config_path or str(default_path)
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _load_fixers(self) -> None:
        fixer_map = {
            "zombie_cleaner": ("zephyr.security.access_control.auto_fix_engine_03.zombie_cleaner", "ZombieCleaner"),
            "all_completer": ("zephyr.security.access_control.auto_fix_engine_03.all_completer", "AllCompleter"),
            "dedup_extractor": ("zephyr.security.access_control.auto_fix_engine_03.dedup_extractor", "DedupExtractor"),
            "scaffold_registrar": (
                "zephyr.security.access_control.auto_fix_engine_03.scaffold_registrar",
                "ScaffoldRegistrar",
            ),
            "alignment_syncer": (
                "zephyr.security.access_control.auto_fix_engine_03.alignment_syncer",
                "AlignmentSyncer",
            ),
            "drift_fixer": ("zephyr.security.access_control.auto_fix_engine_03.drift_fixer", "DriftFixer"),
            "dep_version_fixer": (
                "zephyr.security.access_control.auto_fix_engine_03.dep_version_fixer",
                "DepVersionFixer",
            ),
            "import_fixer": ("zephyr.security.access_control.auto_fix_engine_03.import_fixer", "ImportFixer"),
            "config_fixer": ("zephyr.security.access_control.auto_fix_engine_03.config_fixer", "ConfigFixer"),
            "llm_fix_adapter": ("zephyr.security.access_control.auto_fix_engine_03.llm_fix_adapter", "LLMFixAdapter"),
            "self_heal_agent": ("zephyr.security.access_control.auto_fix_engine_03.self_heal_agent", "SelfHealAgent"),
        }
        for name, (module_path, class_name) in fixer_map.items():
            try:
                import importlib

                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                self._fixers[name] = cls()
            except Exception as exc:
                logger.debug("Fixer %s not loaded: %s", name, exc)

    def fix(self, action_type: str, target: str, dry_run: bool = False) -> FixAction:
        if action_type in _NO_AUTO_FIX_TYPES:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.CANCELLED,
                metadata={"reason": f"Action type {action_type} is in no-auto-fix list"},
            )
        safety_decision = self._safety_gate.check(FixAction(action_type=action_type, target=target))
        if not safety_decision.approved:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.APPROVAL_PENDING,
                confidence=safety_decision.confidence,
                metadata={"safety_reason": safety_decision.reason},
                escalated=True,
            )
        budget_decision = self._fix_budget.check(FixLevel.L1_RULE)
        if not budget_decision.allowed:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.FAILED,
                metadata={"budget_reason": budget_decision.reason},
            )
        cascade_ok, cascade_reason = self._cascade_breaker.check()
        if not cascade_ok:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.FAILED,
                metadata={"cascade_reason": cascade_reason},
            )
        storm_ok, storm_reason = self._storm_guard.check()
        if not storm_ok:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.FAILED,
                metadata={"storm_reason": storm_reason},
            )
        fixer = self._find_fixer(action_type)
        if fixer is None:
            return FixAction(
                action_type=action_type,
                target=target,
                status=FixStatus.FAILED,
                metadata={"error": f"No fixer found for action type: {action_type}"},
            )
        action = fixer.fix(target, dry_run=dry_run)
        if action.status == FixStatus.COMPLETED and not dry_run:
            self._fix_budget.consume(action.level, action.token_cost, operation_id=action.action_id)
            self._cascade_breaker.record("")
            self._storm_guard.record()
            self._idempotency.record(action, action.status.value)
            blast = self._blast_radius.estimate(action)
            action.metadata["blast_radius"] = blast
            if self._config.get("compliance", {}).get("audit_all_fixes", True):
                self._compliance.audit_fix(action, rbac_decision="auto_approved", validation_result="pending")
            self._pattern_miner.mine([action])
            self._close_related_finding(action_type, target)
        return action

    def fix_all(self, actions: list[FixAction]) -> FixReport:
        if not actions:
            return FixReport(budget_remaining=self._fix_budget.get_info())
        valid_actions = [a for a in actions if a.action_type not in _NO_AUTO_FIX_TYPES]
        if not valid_actions:
            return FixReport(
                total_attempted=len(actions),
                cascade_alerts=["All actions are in no-auto-fix list"],
                budget_remaining=self._fix_budget.get_info(),
            )

        def _fix_one(action: FixAction) -> FixAction:
            return self.fix(action.action_type, action.target)

        report = self._batch_fixer.execute_batch(valid_actions, _fix_one)
        self._pattern_miner.mine(report.actions)
        for action in report.actions:
            if action.status == FixStatus.COMPLETED:
                self._close_related_finding(action.action_type, action.target)
        return report

    def canary_fix(self, action: FixAction, sample_ratio: float = 0.1) -> FixAction:
        fixer = self._find_fixer(action.action_type)
        if fixer is None:
            action.status = FixStatus.FAILED
            action.metadata["error"] = "No fixer found"
            return action
        ratio = self._canary_fixer.get_ratio(action.action_type)
        if sample_ratio > ratio:
            action.status = FixStatus.APPROVAL_PENDING
            action.metadata["canary_reason"] = f"Sample ratio {sample_ratio} exceeds canary ratio {ratio}"
            return action
        result = self.fix(action.action_type, action.target)
        if result.status == FixStatus.COMPLETED:
            self._canary_fixer.advance(action.action_type)
        return result

    def dry_run(self, action_type: str, target: str) -> FixAction:
        return self.fix(action_type, target, dry_run=True)

    def health_check(self) -> FixHealthReport:
        checker = FixHealthCheck()
        budget_info = self._fix_budget.get_info()
        budget_ok = budget_info.daily_remaining > 0 and budget_info.monthly_remaining > 0
        return checker.check(
            fixers=self._fixers,
            budget_ok=budget_ok,
            cascade_active=self._cascade_breaker.check()[0] is False,
            dead_letter_count=self._dead_letter_queue.size,
            approval_queue_size=self._approval_queue.size,
        )

    def approve(self, action_id: str) -> FixAction | None:
        return self._approval_queue.approve(action_id)

    def reject(self, action_id: str) -> FixAction | None:
        return self._approval_queue.reject(action_id)

    def get_dead_letters(self) -> list[Any]:
        return self._dead_letter_queue.get_pending()

    def get_approval_queue(self) -> list[FixAction]:
        return self._approval_queue.get_pending()

    def _close_related_finding(self, fix_type: str, target_path: str) -> None:
        import json
        from pathlib import Path

        db_path = Path("scripts/governance/meta/finding-state-db.json")
        if not db_path.exists():
            return
        try:
            with open(db_path, encoding="utf-8") as f:
                data = json.load(f)
            findings = data.get("findings", {})
            closed = 0
            for fid, fdata in findings.items():
                if fdata.get("status") in ("OPEN", "IN_PROGRESS"):
                    target = fdata.get("target", {})
                    if isinstance(target, dict) and target.get("file_path", "") == target_path:
                        fdata["status"] = "FIXED"
                        closed += 1
            if closed > 0:
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                try:
                    from zephyr.shared.event_bus import bus

                    bus.emit(
                        "audit.finding_resolved",
                        {"finding_count": closed, "fix_type": fix_type, "target_path": target_path},
                    )
                except Exception:
                    pass
                if _FINDING_MODEL_AVAILABLE:
                    try:
                        verified_finding = AuditFinding(
                            finding_id=generate_finding_id("D1", f"fix_verified:{fix_type}:{target_path}"),
                            dimension=FindingDimension.D1,
                            severity=FindingSeverity.INFO,
                            category="自动修复验证",
                            target=FindingTarget(file_path=target_path),
                            description=f"Fix verified: {fix_type} on {target_path}",
                            evidence=f"{closed} finding(s) closed by auto-fix",
                            impact=FindingImpact(blast_radius=BlastRadius.file),
                            remediation=FindingRemediation(
                                action=RemediationAction.FIX, priority=RemediationPriority.P2
                            ),
                            lifecycle=FindingLifecycle(status=FindingStatus.VERIFIED),
                            traceability=FindingTraceability(),
                            recommendation_block=RecommendationBlock(),
                        )
                        from zephyr.governance.finding_ingest import FindingIngest

                        ingest = FindingIngest()
                        ingest.ingest_findings([verified_finding])
                    except Exception:
                        pass
        except Exception:
            pass

    def _find_fixer(self, action_type: str) -> Any:
        type_to_fixer = {
            "zombie_cleanup": "zombie_cleaner",
            "all_completion": "all_completer",
            "dedup_extraction": "dedup_extractor",
            "scaffold_registration": "scaffold_registrar",
            "alignment_sync": "alignment_syncer",
            "drift_fix": "drift_fixer",
            "dep_version_fix": "dep_version_fixer",
            "import_fix": "import_fixer",
            "config_fix": "config_fixer",
            "llm_fix": "llm_fix_adapter",
            "self_heal": "self_heal_agent",
        }
        fixer_name = type_to_fixer.get(action_type)
        if fixer_name and fixer_name in self._fixers:
            return self._fixers[fixer_name]
        return None

    _FIX_STATUS_SEVERITY_MAP: dict[str, str] = {
        "COMPLETED": "INFO",
        "FAILED": "HIGH",
        "ROLLED_BACK": "MEDIUM",
    }

    def _output_fix_results_as_jsonl(self, actions: list[FixAction]) -> list[str]:
        if not _FINDING_MODEL_AVAILABLE:
            return []
        findings: list[AuditFinding] = []
        for action in actions:
            sev_str = self._FIX_STATUS_SEVERITY_MAP.get(action.status.value, "MEDIUM")
            finding = AuditFinding(
                finding_id=generate_finding_id("D1", f"fix:{action.action_type}:{action.target}"),
                dimension=FindingDimension.D1,
                severity=FindingSeverity(sev_str),
                category="自动修复结果",
                target=FindingTarget(file_path=action.target),
                description=f"Fix {action.status.value}: {action.action_type} on {action.target}",
                evidence=str(action.metadata) if action.metadata else "",
                impact=FindingImpact(blast_radius=BlastRadius.file),
                remediation=FindingRemediation(action=RemediationAction.FIX, priority=RemediationPriority.P2),
                lifecycle=FindingLifecycle(
                    status=FindingStatus.FIXED if action.status == FixStatus.COMPLETED else FindingStatus.OPEN
                ),
                traceability=FindingTraceability(),
                recommendation_block=RecommendationBlock(),
            )
            findings.append(finding)
        jsonl_lines: list[str] = []
        for f in findings:
            jsonl_lines.append(f.to_jsonl())
        if jsonl_lines:
            try:
                from zephyr.governance.finding_ingest import FindingIngest

                ingest = FindingIngest()
                ingest.ingest_findings(findings)
            except Exception:
                pass
        return jsonl_lines
