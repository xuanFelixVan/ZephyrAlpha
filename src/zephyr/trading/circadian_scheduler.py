# [A_module] module_id=MOD-ORC_circadian_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md

# [MODULE] zephyr.trading.circadian_scheduler

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] auto_runtime_core.py

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] _deep_drift_scan 不抛异常; _dream_cycle_kb_consolidate 不抛异常; _orphan_scan_and_fix 不抛异常; _llm_security_scan 不抛异常; _asset_inventory_refresh 不抛异常; _code_dedup_scan 不抛异常; _orphan_judge_deep 不抛异常; _semantic_audit_scan 不抛异常; _red_blue_daily_drill 不抛异常; _audit_orchestrator_health_check 不抛异常

# [TESTS]

"""
CircadianScheduler — 内置生物钟
=================================
蓝图: ARC-0001 §6.1
借鉴: K8s CronJob + Claude Code Dream Cycle
"""


from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


logger = logging.getLogger(__name__)

try:
    from zephyr.governance.audit_trail.finding_ingest import FindingIngest
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
        BlastRadius,
        RemediationAction,
        RemediationPriority,
        FindingStatus,
        generate_finding_id,
    )
    _FINDING_INGEST_AVAILABLE = True
except ImportError:
    _FINDING_INGEST_AVAILABLE = False


class CircadianPhase(str, Enum):
    MORNING = "MORNING"
    DAY = "DAY"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class ScheduledTask:
    def __init__(self, hour: int, name: str, layer: str, callback: Callable[[], Any] | None = None) -> None:
        self.hour = hour
        self.name = name
        self.layer = layer
        self.callback = callback
        self.last_run_date: str = ""


class CircadianScheduler:
    """内置生物钟——系统节律管理器。"""

    def __init__(self, state_path: Path | None = None) -> None:
        self._state_path = state_path
        self._tasks: list[ScheduledTask] = []
        self._event_listeners: dict[str, list[Callable]] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def register_task(self, hour: int, name: str, layer: str, callback: Callable[[], Any] | None = None) -> None:
        self._tasks.append(ScheduledTask(hour=hour, name=name, layer=layer, callback=callback))

    def register_event_listener(self, event: str, callback: Callable) -> None:
        self._event_listeners.setdefault(event, []).append(callback)

    def trigger_event(self, event: str) -> None:
        for cb in self._event_listeners.get(event, []):
            try:
                cb()
            except Exception:
                pass

    def get_current_phase(self) -> CircadianPhase:
        hour = datetime.now().hour
        if 6 <= hour < 9:
            return CircadianPhase.MORNING
        if 9 <= hour < 18:
            return CircadianPhase.DAY
        if 18 <= hour < 21:
            return CircadianPhase.EVENING
        return CircadianPhase.NIGHT

    def get_next_task(self) -> ScheduledTask | None:
        now = datetime.now()
        current_hour = now.hour
        today = now.strftime("%Y-%m-%d")
        upcoming = [t for t in self._tasks if t.hour > current_hour and t.last_run_date != today]
        if not upcoming:
            return None
        return min(upcoming, key=lambda t: t.hour)

    def start(self) -> None:
        self._register_default_tasks()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="CircadianScheduler")
        self._thread.start()
        from zephyr.trading.resource_optimization import ResourceOptimizationEngine
        try:
            ResourceOptimizationEngine().register_daemon(
                "circadian-scheduler", self.start, self.stop, priority=5,
            )
        except Exception:
            pass

    def _register_default_tasks(self) -> None:
        if any(t.name == "deep_drift_scan" for t in self._tasks):
            return
        self.register_task(hour=22, name="deep_drift_scan", layer="L2", callback=self._deep_drift_scan)
        self.register_task(hour=23, name="dream_cycle_kb_consolidate", layer="L2", callback=self._dream_cycle_kb_consolidate)
        self.register_task(hour=0, name="orphan_scan_and_fix", layer="L2", callback=self._orphan_scan_and_fix)
        self.register_task(hour=1, name="llm_security_scan", layer="L2", callback=self._llm_security_scan)
        self.register_task(hour=2, name="asset_inventory_refresh", layer="L2", callback=self._asset_inventory_refresh)
        self.register_task(hour=2, name="d6_security_daily_scan", layer="L1", callback=self._d6_security_daily_scan)
        self.register_task(hour=3, name="code_dedup_scan", layer="L2", callback=self._code_dedup_scan)
        self.register_task(hour=3, name="d7_code_quality_scan", layer="L1", callback=self._d7_code_quality_scan)
        self.register_task(hour=4, name="orphan_judge_deep", layer="L2", callback=self._orphan_judge_deep)
        self.register_task(hour=4, name="d8_doc_sync_check", layer="L1", callback=self._d8_doc_sync_check)
        self.register_task(hour=5, name="semantic_audit_scan", layer="L1", callback=self._semantic_audit_scan)
        self.register_task(hour=6, name="red_blue_daily_drill", layer="L1", callback=self._red_blue_daily_drill)
        self.register_task(hour=7, name="audit_orchestrator_health_check", layer="L1", callback=self._audit_orchestrator_health_check)

    def _deep_drift_scan(self) -> None:
        try:
            import asyncio
            from zephyr.behavioral_audit.drift_engine import scheduled_deep
            result = asyncio.run(scheduled_deep())
            high_drifts = [d for d in result.drifts if getattr(d, "severity", "").value == "HIGH" or getattr(d, "severity", "") == "HIGH"]
            if high_drifts:
                logger.warning("Dream Cycle deep drift scan: %d HIGH drifts", len(high_drifts))
            self._audit_task_jsonl_output(
                "deep_drift_scan", "D12",
                "HIGH" if high_drifts else "INFO",
                f"Deep drift scan: {len(high_drifts)} HIGH drifts, {result.total_drift_events} total",
                f"total_events={result.total_drift_events}, high={len(high_drifts)}",
            )
        except Exception:
            pass

    def _dream_cycle_kb_consolidate(self) -> None:
        try:
            from zephyr.intelligence.model_evaluation.unified_memory_api import UnifiedMemoryAPI
            api = UnifiedMemoryAPI()
            api.consolidate()
        except Exception:
            pass

    def _orphan_scan_and_fix(self) -> None:
        try:
            from zephyr.security.access_control.orphan_judge import OrphanDetector
            from zephyr.infrastructure.asset_inventory.scanner import Scanner
            from zephyr.infrastructure.asset_inventory.registry_adapter import RegistryAdapter, RegistryManager
            scanner = Scanner()
            scan_result = scanner.scan()
            reg_adapter = RegistryAdapter(RegistryManager())
            cap_registry = reg_adapter.build_capability_registry(scan_result)
            detector = OrphanDetector(scanner, cap_registry)
            report = detector.report()
            if report.orphan_count > 0:
                logger.warning("Orphan scan: %d orphans detected (%.1f%% rate)", report.orphan_count, report.orphan_rate * 100)
                self._auto_fix_orphans(report)
                self._audit_task_jsonl_output(
                    "orphan_scan_and_fix", "D1", "HIGH",
                    f"Orphan scan: {report.orphan_count} orphans ({report.orphan_rate * 100:.1f}%)",
                    f"orphan_count={report.orphan_count}, orphan_rate={report.orphan_rate}",
                )
            else:
                logger.info("Orphan scan: clean (0 orphans)")
                self._audit_task_jsonl_output(
                    "orphan_scan_and_fix", "D1", "INFO",
                    "Orphan scan: clean (0 orphans)",
                    "orphan_count=0",
                )
        except Exception:
            logger.debug("Orphan scan failed", exc_info=True)

    def _auto_fix_orphans(self, report) -> None:
        try:
            from zephyr.security.access_control.auto_fix_engine_03 import AutoFixEngine
            engine = AutoFixEngine()
            orphans = report.orphans[:5] if hasattr(report, "orphans") else []
            for o in orphans:
                target = getattr(o, "relative_path", "") or getattr(o, "path", "") or str(o)
                action = engine.fix("scaffold_registrar", target, dry_run=False)
                if action.status.value == "COMPLETED":
                    logger.info("Orphan auto-fix: registered → %s", target)
                else:
                    logger.warning("Orphan auto-fix: failed → %s (%s)", target, action.status)
        except Exception:
            logger.debug("Orphan auto-fix failed", exc_info=True)

    def _llm_security_scan(self) -> None:
        try:
            from zephyr.security.llm_defense.llm_security.patterns.secrets import scan_secrets
            from pathlib import Path
            src_dir = Path(__file__).resolve().parents[2]
            hits_total = 0
            py_files = list(src_dir.rglob("*.py"))[:200]
            for fp in py_files:
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                    hits = scan_secrets(content)
                    if hits:
                        high_hits = [h for h in hits if h.get("severity") == "high"]
                        if high_hits:
                            logger.warning("LLM security scan: %s — %d high-severity hits", fp.relative_to(src_dir), len(high_hits))
                        hits_total += len(hits)
                except Exception:
                    continue
            if hits_total > 0:
                logger.warning("LLM security scan: %d total hits across %d files", hits_total, len(py_files))
                try:
                    from zephyr.integration.shared_08.event_bus import bus
                    bus.emit(topic="security.secrets_detected", payload={"hits": hits_total})
                except Exception:
                    pass
                self._audit_task_jsonl_output(
                    "llm_security_scan", "D6", "HIGH",
                    f"LLM security scan: {hits_total} hits across {len(py_files)} files",
                    f"hits={hits_total}, files_scanned={len(py_files)}",
                )
            else:
                logger.info("LLM security scan: clean (0 hits)")
                self._audit_task_jsonl_output(
                    "llm_security_scan", "D6", "INFO",
                    "LLM security scan: clean (0 hits)",
                    "hits=0",
                )
        except Exception:
            logger.debug("LLM security scan failed", exc_info=True)

    def _asset_inventory_refresh(self) -> None:
        try:
            from zephyr.infrastructure.asset_inventory.scanner import Scanner
            from zephyr.infrastructure.asset_inventory.classifier import Classifier
            from zephyr.infrastructure.asset_inventory.index_generator import IndexGenerator
            scanner = Scanner()
            scan_result = scanner.scan()
            classifier = Classifier()
            classified = classifier.classify(scan_result)
            generator = IndexGenerator()
            index = generator.generate(classified)
            total = getattr(index, "total_assets", 0) or len(getattr(index, "assets", []))
            health = getattr(index, "health_score", 0.0)
            orphan_rate = getattr(index, "orphan_rate", 0.0)
            orphan_rate_pct = orphan_rate * 100 if isinstance(orphan_rate, (int, float)) and orphan_rate <= 1.0 else orphan_rate
            logger.info("Asset inventory refresh: %d assets, health=%.2f, orphan_rate=%.2f%%", total, health, orphan_rate_pct)
            if isinstance(orphan_rate_pct, (int, float)) and orphan_rate_pct > 5.0:
                try:
                    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge
                    judge = OrphanJudge()
                    report = judge.batch_judge(scope="src/zephyr/", limit=100, dry_run=True)
                    delete_count = report.by_verdict.get("DELETE", 0) if hasattr(report, "by_verdict") else 0
                    logger.warning("Asset inventory: orphan_rate=%.1f%% > 5%% threshold → orphan-judge triggered: %d DELETE verdicts",
                                  orphan_rate_pct, delete_count)
                except Exception:
                    logger.debug("Orphan judge auto-trigger failed", exc_info=True)
        except Exception:
            logger.debug("Asset inventory refresh failed", exc_info=True)

    def _code_dedup_scan(self) -> None:
        try:
            from zephyr.governance.scanner import Scanner as DedupScanner
            from pathlib import Path
            src_dir = Path(__file__).resolve().parents[2]
            py_files = [str(p) for p in src_dir.rglob("*.py") if "_snapshots" not in str(p) and "vector_db_backups" not in str(p)][:300]
            scanner = DedupScanner()
            scanner.scan_files(py_files)
            dup_groups = scanner.find_duplicates()
            if dup_groups:
                high_sim = [g for g in dup_groups if getattr(g, "similarity", 0) >= 0.7]
                if high_sim:
                    logger.warning("Code dedup scan: %d duplicate groups (similarity>=0.7) out of %d total", len(high_sim), len(dup_groups))
                else:
                    logger.info("Code dedup scan: %d groups found, all below 0.7 similarity", len(dup_groups))
            else:
                logger.info("Code dedup scan: clean (0 duplicate groups)")
        except Exception:
            logger.debug("Code dedup scan failed", exc_info=True)

    def _orphan_judge_deep(self) -> None:
        try:
            from zephyr.security.access_control.orphan_judge.judge import OrphanJudge
            judge = OrphanJudge()
            report = judge.batch_judge(scope="src/zephyr/", limit=50, dry_run=True)
            if report.by_verdict.get("DELETE", 0) > 0 or report.by_verdict.get("ESCALATE", 0) > 0:
                logger.warning("Orphan judge deep: %d judgments, %d DELETE, %d ESCALATE",
                              report.total, report.by_verdict.get("DELETE", 0), report.by_verdict.get("ESCALATE", 0))
                self._audit_task_jsonl_output(
                    "orphan_judge_deep", "D1", "HIGH",
                    f"Orphan judge deep: {report.total} judgments, DELETE={report.by_verdict.get('DELETE', 0)}, ESCALATE={report.by_verdict.get('ESCALATE', 0)}",
                    f"total={report.total}, delete={report.by_verdict.get('DELETE', 0)}, escalate={report.by_verdict.get('ESCALATE', 0)}",
                )
            else:
                logger.info("Orphan judge deep: %d judgments, all safe", report.total)
                self._audit_task_jsonl_output(
                    "orphan_judge_deep", "D1", "INFO",
                    f"Orphan judge deep: {report.total} judgments, all safe",
                    f"total={report.total}",
                )
        except Exception:
            logger.debug("Orphan judge deep scan failed", exc_info=True)

    def _semantic_audit_scan(self) -> None:
        try:
            import importlib
            _mod = importlib.import_module("zephyr.governance.semantic_auditor")
            semantic_cli_main = _mod.main
            import sys
            old_argv = sys.argv
            try:
                sys.argv = ["semantic-auditor", "scan", "--target", "src/zephyr/", "--level", "STANDARD"]
                rc = semantic_cli_main()
                if rc != 0:
                    logger.warning("Semantic audit scan: issues found (rc=%d)", rc)
                    self._audit_task_jsonl_output(
                        "semantic_audit_scan", "D12", "MEDIUM",
                        f"Semantic audit scan: issues found (rc={rc})",
                        f"return_code={rc}",
                        "src/zephyr/",
                    )
                else:
                    logger.info("Semantic audit scan: clean")
                    self._audit_task_jsonl_output(
                        "semantic_audit_scan", "D12", "INFO",
                        "Semantic audit scan: clean",
                        "return_code=0",
                        "src/zephyr/",
                    )
            finally:
                sys.argv = old_argv
        except Exception:
            logger.debug("Semantic audit scan failed", exc_info=True)

        try:
            from zephyr.governance.blast_radius import BlastRadiusAnalyzer
            from zephyr.governance.semantic_audit.models import SemanticAuditFinding, Severity
            analyzer = BlastRadiusAnalyzer()
            test_finding = SemanticAuditFinding(
                finding_id="F-SEM-SCHED-CHECK",
                module="circadian_scheduler",
                severity=Severity.INFO,
                dimension="dependson_chain_broken",
                description="Scheduled blast radius self-check",
                source_location="src/zephyr/semantic-auditor/models.py",
            )
            report = analyzer.analyze(test_finding)
            if report.transitive_dependents > 0:
                logger.info(
                    "Blast radius self-check: %d transitive dependents, risk=%s, depth=%d",
                    report.transitive_dependents, report.risk_level, report.cascade_depth,
                )
                self._audit_task_jsonl_output(
                    "blast_radius_self_check", "D12", "INFO",
                    f"Blast radius self-check: {report.transitive_dependents} dependents, risk={report.risk_level}",
                    f"transitive={report.transitive_dependents}, depth={report.cascade_depth}, risk={report.risk_level}",
                    "src/zephyr/semantic-auditor/",
                )
            else:
                logger.info("Blast radius self-check: no dependents found")
        except Exception:
            logger.debug("Blast radius self-check failed", exc_info=True)

    def _red_blue_daily_drill(self) -> None:
        try:
            from zephyr.security.adversarial_validation.game_day_runner import GameDayRunner, GameDayFrequency
            runner = GameDayRunner()
            result = runner.run_game_day(GameDayFrequency.DAILY)
            if result.bypasses > 0:
                logger.warning("Red-blue daily drill: %d attacks, %d bypasses (%.1f%% bypass rate)",
                              result.total_attacks, result.bypasses,
                              (result.bypasses / max(result.total_attacks, 1)) * 100)
                self._audit_task_jsonl_output(
                    "red_blue_daily_drill", "D6", "HIGH",
                    f"Red-blue drill: {result.bypasses} bypasses out of {result.total_attacks} attacks",
                    f"total_attacks={result.total_attacks}, bypasses={result.bypasses}",
                )
            else:
                logger.info("Red-blue daily drill: %d attacks, 0 bypasses — all defenses held",
                           result.total_attacks)
                self._audit_task_jsonl_output(
                    "red_blue_daily_drill", "D6", "INFO",
                    f"Red-blue drill: {result.total_attacks} attacks, 0 bypasses",
                    f"total_attacks={result.total_attacks}, bypasses=0",
                )
        except Exception:
            logger.debug("Red-blue daily drill failed", exc_info=True)

    def _audit_orchestrator_health_check(self) -> None:
        try:
            from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController
            controller = AuditAdmissionController()
            result = controller.check_admission(operation="scheduled_health_check", target_path="*")
            if result.allowed:
                logger.info("Audit orchestrator health check: all %d modules healthy",
                           len(result.checks_passed))
                self._audit_task_jsonl_output(
                    "audit_orchestrator_health_check", "D1", "INFO",
                    f"Health check: all {len(result.checks_passed)} modules healthy",
                    f"passed={len(result.checks_passed)}, failed=0",
                )
            else:
                logger.warning("Audit orchestrator health check: %d modules failed — %s",
                              len(result.checks_failed), result.reason)
                self._audit_task_jsonl_output(
                    "audit_orchestrator_health_check", "D1", "HIGH",
                    f"Health check: {len(result.checks_failed)} modules failed — {result.reason}",
                    f"passed={len(result.checks_passed)}, failed={len(result.checks_failed)}",
                )
        except Exception:
            logger.debug("Audit orchestrator health check failed", exc_info=True)

    def _d6_security_daily_scan(self) -> None:
        try:
            import subprocess
            from pathlib import Path
            scripts_dir = Path(__file__).resolve().parents[2].parent.parent / "scripts" / "governance" / "d6_security"
            if not scripts_dir.exists():
                self._audit_task_jsonl_output("d6_security_daily_scan", "D6", "INFO", "D6 security scan: no scripts directory", "dir_not_found")
                return
            scripts = list(scripts_dir.glob("*.py"))[:20]
            issues = 0
            for script in scripts:
                try:
                    proc = subprocess.run(["python", str(script), "--warn-only"], capture_output=True, text=True, timeout=60)
                    if proc.returncode != 0:
                        issues += 1
                except Exception:
                    issues += 1
            severity = "HIGH" if issues > 0 else "INFO"
            self._audit_task_jsonl_output(
                "d6_security_daily_scan", "D6", severity,
                f"D6 security daily scan: {issues} issues out of {len(scripts)} scripts",
                f"issues={issues}, scripts_run={len(scripts)}",
            )
        except Exception:
            logger.debug("D6 security daily scan failed", exc_info=True)

    def _d7_code_quality_scan(self) -> None:
        try:
            import subprocess
            from pathlib import Path
            scripts_dir = Path(__file__).resolve().parents[2].parent.parent / "scripts" / "governance" / "d7_code_quality"
            if not scripts_dir.exists():
                self._audit_task_jsonl_output("d7_code_quality_scan", "D7", "INFO", "D7 code quality scan: no scripts directory", "dir_not_found")
                return
            scripts = list(scripts_dir.glob("*.py"))[:20]
            issues = 0
            for script in scripts:
                try:
                    proc = subprocess.run(["python", str(script), "--warn-only"], capture_output=True, text=True, timeout=60)
                    if proc.returncode != 0:
                        issues += 1
                except Exception:
                    issues += 1
            severity = "HIGH" if issues > 0 else "INFO"
            self._audit_task_jsonl_output(
                "d7_code_quality_scan", "D7", severity,
                f"D7 code quality scan: {issues} issues out of {len(scripts)} scripts",
                f"issues={issues}, scripts_run={len(scripts)}",
            )
        except Exception:
            logger.debug("D7 code quality scan failed", exc_info=True)

    def _d8_doc_sync_check(self) -> None:
        try:
            import subprocess
            from pathlib import Path
            scripts_dir = Path(__file__).resolve().parents[2].parent.parent / "scripts" / "governance" / "d8_doc_sync"
            if not scripts_dir.exists():
                self._audit_task_jsonl_output("d8_doc_sync_check", "D8", "INFO", "D8 doc sync check: no scripts directory", "dir_not_found")
                return
            scripts = list(scripts_dir.glob("*.py"))[:20]
            issues = 0
            for script in scripts:
                try:
                    proc = subprocess.run(["python", str(script), "--warn-only"], capture_output=True, text=True, timeout=60)
                    if proc.returncode != 0:
                        issues += 1
                except Exception:
                    issues += 1
            severity = "HIGH" if issues > 0 else "INFO"
            self._audit_task_jsonl_output(
                "d8_doc_sync_check", "D8", severity,
                f"D8 doc sync check: {issues} issues out of {len(scripts)} scripts",
                f"issues={issues}, scripts_run={len(scripts)}",
            )
        except Exception:
            logger.debug("D8 doc sync check failed", exc_info=True)

    def _audit_task_jsonl_output(self, task_name: str, dimension: str, severity: str, description: str, evidence: str, target_path: str = "") -> None:
        if not _FINDING_INGEST_AVAILABLE:
            return
        try:
            finding = AuditFinding(
                finding_id=generate_finding_id(dimension, f"scheduled:{task_name}"),
                dimension=FindingDimension(dimension),
                severity=FindingSeverity(severity),
                category="定时审计任务",
                target=FindingTarget(file_path=target_path or f"scheduled_task:{task_name}"),
                description=description,
                evidence=evidence,
                impact=FindingImpact(blast_radius=BlastRadius.module),
                remediation=FindingRemediation(action=RemediationAction.INVESTIGATE, priority=RemediationPriority.P2),
                lifecycle=FindingLifecycle(status=FindingStatus.OPEN),
                traceability=FindingTraceability(),
                recommendation_block=RecommendationBlock(),
            )
            ingest = FindingIngest()
            ingest.ingest_findings([finding])
        except Exception:
            pass

    def stop(self) -> None:
        self._running = False
        self.save_state()

    def _loop(self) -> None:
        last_minute: int = -1
        while self._running:
            now = datetime.now()
            if now.minute == 0 and now.minute != last_minute:
                last_minute = now.minute
                today = now.strftime("%Y-%m-%d")
                for task in self._tasks:
                    if task.hour == now.hour and task.last_run_date != today:
                        task.last_run_date = today
                        if task.callback:
                            try:
                                task.callback()
                            except Exception:
                                pass
            time.sleep(30)

    def save_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "tasks": [
                {"hour": t.hour, "name": t.name, "layer": t.layer, "last_run_date": t.last_run_date}
                for t in self._tasks
            ]
        }
        self._state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
