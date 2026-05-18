# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.runtime.boot_cron_jobs

# [INVARIANTS] register_boot_cron_jobs is idempotent; duplicate hour+name ignored by CircadianScheduler

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.runtime.auto_runtime_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] returns None; logs warning on failure; never raises

# [TESTS]

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.runtime.circadian_scheduler import CircadianScheduler
    from zephyr.runtime.work_orchestrator import WorkOrchestrator

logger = logging.getLogger(__name__)


def register_boot_cron_jobs(
    circadian_scheduler: CircadianScheduler,
    work_orchestrator: WorkOrchestrator,
    project_root: Path,
) -> None:
    try:
        from zephyr.db.task_repo import TaskRepository
        from zephyr.gates.task_completion_gate import TaskCompletionGate
        task_repo = TaskRepository()
        completion_gate = TaskCompletionGate(scan_dir=project_root)

        def _check_all_escalations() -> None:
            try:
                tasks = task_repo.search(status="BLOCKED")
                for t in (tasks or []):
                    task_repo.check_escalation(t["task_id"] if isinstance(t, dict) else t.task_id)
            except Exception:
                pass

        def _check_all_timeouts() -> None:
            try:
                for status in ("IN_PROGRESS", "SUSPENDED"):
                    tasks = task_repo.search(status=status)
                    for t in (tasks or []):
                        task_repo.check_task_timeout(t["task_id"] if isinstance(t, dict) else t.task_id)
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=0, name="task_escalation_check", layer="L1",
            callback=_check_all_escalations,
        )
        circadian_scheduler.register_task(
            hour=0, name="task_timeout_check", layer="L1",
            callback=_check_all_timeouts,
        )
        circadian_scheduler.register_task(
            hour=2, name="orphan_task_scan", layer="L1",
            callback=completion_gate.scan,
        )
        circadian_scheduler.register_task(
            hour=3, name="daily_code_dedup", layer="L2",
            callback=lambda: work_orchestrator.submit_dag("daily_code_dedup"),
        )

        def _dedup_monthly_audit() -> None:
            from datetime import datetime as _dt
            if _dt.now().day != 1:
                return
            try:
                from zephyr.l01_infrastructure.code_dedup_engine.false_negative_auditor import FalseNegativeAuditor
                FalseNegativeAuditor().run_full_audit()
            except Exception:
                pass
            try:
                from zephyr.l01_infrastructure.code_dedup_engine.simplicity_auditor import SimplicityAuditor
                SimplicityAuditor().run_monthly()
            except Exception:
                pass
            try:
                from zephyr.l01_infrastructure.code_dedup_engine.sensitivity_sweeper import SensitivitySweeper
                SensitivitySweeper().sweep()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=3, name="dedup_monthly_audit", layer="L2",
            callback=_dedup_monthly_audit,
        )

        def _skill_freshness_scan() -> None:
            try:
                from zephyr.agent_spec.skill_freshness_ext import scan_all_freshness
                scan_all_freshness()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=1, name="skill_freshness_scan", layer="L1",
            callback=_skill_freshness_scan,
        )

        try:
            from zephyr.shared.event_bus import bus
            def _on_freshness_critical(payload: dict) -> None:
                try:
                    from zephyr.agent_spec.skill_freshness_ext import auto_deprecate_skill
                    from zephyr.agent_spec.skill_lifecycle import SkillLifecycle
                    sl = SkillLifecycle()
                    for item in payload.get("criticals", []):
                        skill_id = item.get("skill_id", "")
                        score = item.get("freshness_score", 0.0)
                        if skill_id:
                            auto_deprecate_skill(sl, skill_id, score, reason="freshness_critical_auto")
                except Exception:
                    pass
            bus.subscribe("skill.freshness_critical", _on_freshness_critical)
        except Exception:
            pass

        def _ide_skill_watch() -> None:
            try:
                from zephyr.agent_spec.ide_watcher import IDEWatcher
                IDEWatcher().scan()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=2, name="ide_skill_watch", layer="L2",
            callback=_ide_skill_watch,
        )

        def _budget_health_check() -> None:
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "scripts/governance/d5_architecture/check_budget_health.py", "--warn-only"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning("Budget health check returned %d: %s", result.returncode, result.stdout[-200:] if result.stdout else "")
            except Exception as e:
                logger.warning("Budget health check failed: %s", e)

        def _budget_alignment_check() -> None:
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "scripts/governance/d5_architecture/check_blueprint_code_alignment.py", "--warn-only"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning("Budget alignment check returned %d: %s", result.returncode, result.stdout[-200:] if result.stdout else "")
            except Exception as e:
                logger.warning("Budget alignment check failed: %s", e)

        circadian_scheduler.register_task(
            hour=4, name="budget_health_check", layer="L1",
            callback=_budget_health_check,
        )
        circadian_scheduler.register_task(
            hour=5, name="budget_blueprint_alignment", layer="L2",
            callback=_budget_alignment_check,
        )

        def _pricing_sync() -> None:
            try:
                from zephyr.budget_enforcer.pricing_sync import PricingSync
                ps = PricingSync()
                updated = ps.sync_from_litellm()
                if updated > 0:
                    logger.info("Pricing sync: %d models updated", updated)
            except Exception as e:
                logger.warning("Pricing sync failed: %s", e)

        circadian_scheduler.register_task(
            hour=2, name="pricing_sync", layer="L1",
            callback=_pricing_sync,
        )

        def _temp_file_cleanup() -> None:
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "scripts/governance/d1_structure/detect_temp_files.py", "--clean"],
                    capture_output=True, text=True, timeout=120,
                    cwd=str(project_root),
                )
                if result.stdout:
                    logger.info("Temp file cleanup: %s", result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)
            except Exception as e:
                logger.warning("Temp file cleanup failed: %s", e)

        circadian_scheduler.register_task(
            hour=6, name="temp_file_cleanup", layer="L2",
            callback=_temp_file_cleanup,
        )

        def _triple_alignment_check() -> None:
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "src/zephyr/gates/triple_alignment.py"],
                    capture_output=True, text=True, timeout=300,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning("Triple alignment check returned %d: %s", result.returncode, result.stdout[-300:] if result.stdout else "")
                else:
                    logger.info("Triple alignment check: PASS")
            except Exception as e:
                logger.warning("Triple alignment check failed: %s", e)

        circadian_scheduler.register_task(
            hour=7, name="triple_alignment_check", layer="L1",
            callback=_triple_alignment_check,
        )

        def _escalation_self_test() -> None:
            try:
                from zephyr.escalation_engine.self_test import run_self_test
                report = run_self_test()
                if report.health.name != "HEALTHY":
                    logger.warning("Escalation self-test: %s", report.health.name)
            except Exception as e:
                logger.warning("Escalation self-test failed: %s", e)

        circadian_scheduler.register_task(
            hour=3, name="escalation_self_test", layer="L1",
            callback=_escalation_self_test,
        )
        logger.info("Task system cron jobs registered: escalation/timeout/orphan_scan/daily_dedup/budget_health/budget_alignment/temp_cleanup/triple_alignment/escalation_self_test")
    except Exception as e:
        logger.warning("Failed to register task system cron jobs: %s", e)
