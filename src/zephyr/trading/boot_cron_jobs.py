# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md
# [MODULE] zephyr.trading.boot_cron_jobs
# [DOMAIN] D-TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.rule_enforcement.task_completion_gate; zephyr.integration.shared_08.event_bus; zephyr.autonomy_core.__init__; zephyr.governance.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] register_boot_cron_jobs is idempotent; duplicate hour+name ignored by CircadianScheduler
# [DEPRECATED] 定时调度已废除（2026-06-26裁定）：CircadianScheduler.register_task() 已改为 no-op。
# 本函数保留签名兼容现有调用链，但所有 register_task 调用不再注册任何定时任务。
# 审计/治理任务改由 pre-commit GATE（commit事件）和 boot_hooks（状态变更事件）触发。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns None; logs warning on failure; never raises
# [TESTS]
# [A_module] module_id=MOD-ORC_boot_cron_jobs | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.trading.circadian_scheduler import CircadianScheduler
    from zephyr.trading.work_orchestrator import WorkOrchestrator

logger = logging.getLogger(__name__)


def register_boot_cron_jobs(
    circadian_scheduler: CircadianScheduler,
    work_orchestrator: WorkOrchestrator,
    project_root: Path,
) -> None:
    try:
        from zephyr.governance.persistence.task_repo import TaskRepository
        from zephyr.governance.rule_enforcement.task_completion_gate import TaskCompletionGate

        task_repo = TaskRepository()
        completion_gate = TaskCompletionGate(scan_dir=project_root)

        def _check_all_escalations() -> None:
            try:
                tasks = task_repo.search(status="BLOCKED")
                for t in tasks or []:
                    task_repo.check_escalation(t["task_id"] if isinstance(t, dict) else t.task_id)
            except Exception:
                pass

        def _check_all_timeouts() -> None:
            try:
                for status in ("IN_PROGRESS", "SUSPENDED"):
                    tasks = task_repo.search(status=status)
                    for t in tasks or []:
                        task_repo.check_task_timeout(t["task_id"] if isinstance(t, dict) else t.task_id)
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=0,
            name="task_escalation_check",
            layer="L1",
            callback=_check_all_escalations,
        )
        circadian_scheduler.register_task(
            hour=0,
            name="task_timeout_check",
            layer="L1",
            callback=_check_all_timeouts,
        )

        # DM-400 修复2: stale_claim_recovery 已合并到下方的 stale_task_recovery
        circadian_scheduler.register_task(
            hour=2,
            name="orphan_task_scan",
            layer="L1",
            callback=completion_gate.scan,
        )
        circadian_scheduler.register_task(
            hour=3,
            name="daily-code-dedup",
            layer="L2",
            callback=lambda: work_orchestrator.submit_dag("daily-code-dedup"),
        )

        def _dedup_monthly_audit() -> None:
            from datetime import datetime as _dt

            if _dt.now().day != 1:
                return
            try:
                import importlib

                _mod = importlib.import_module("zephyr.testing.code_dedup.false_negative_auditor")
                FalseNegativeAuditor = _mod.FalseNegativeAuditor
                FalseNegativeAuditor().run_full_audit()
            except Exception:
                pass
            try:
                _mod2 = importlib.import_module("zephyr.testing.code_dedup.simplicity_auditor")
                SimplicityAuditor = _mod2.SimplicityAuditor
                SimplicityAuditor().run_monthly()
            except Exception:
                pass
            try:
                _mod3 = importlib.import_module("zephyr.testing.code_dedup.sensitivity_sweeper")
                SensitivitySweeper = _mod3.SensitivitySweeper
                SensitivitySweeper().sweep()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=3,
            name="dedup_monthly_audit",
            layer="L2",
            callback=_dedup_monthly_audit,
        )

        def _skill_freshness_scan() -> None:
            try:
                from zephyr.autonomy_core.skill_freshness_ext import scan_all_freshness

                scan_all_freshness()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=1,
            name="skill_freshness_scan",
            layer="L1",
            callback=_skill_freshness_scan,
        )

        try:
            from zephyr.shared.event_bus import bus

            def _on_freshness_critical(payload: dict) -> None:
                try:
                    from zephyr.autonomy_core.skill_freshness_ext import auto_deprecate_skill
                    from zephyr.autonomy_core.skill_lifecycle import SkillLifecycle

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
                from zephyr.autonomy_core.ide_watcher import IDEWatcher

                IDEWatcher().scan()
            except Exception:
                pass

        circadian_scheduler.register_task(
            hour=2,
            name="ide_skill_watch",
            layer="L2",
            callback=_ide_skill_watch,
        )

        def _budget_health_check() -> None:
            try:
                import subprocess

                result = subprocess.run(
                    [sys.executable, "scripts/governance/d5_architecture/check_budget_health.py", "--warn-only"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning(
                        "Budget health check returned %d: %s",
                        result.returncode,
                        result.stdout[-200:] if result.stdout else "",
                    )
            except Exception as e:
                logger.warning("Budget health check failed: %s", e)

        def _budget_alignment_check() -> None:
            try:
                import subprocess

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/governance/d5_architecture/check_blueprint_code_alignment.py",
                        "--warn-only",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning(
                        "Budget alignment check returned %d: %s",
                        result.returncode,
                        result.stdout[-200:] if result.stdout else "",
                    )
            except Exception as e:
                logger.warning("Budget alignment check failed: %s", e)

        circadian_scheduler.register_task(
            hour=4,
            name="budget_health_check",
            layer="L1",
            callback=_budget_health_check,
        )
        circadian_scheduler.register_task(
            hour=5,
            name="budget_blueprint_alignment",
            layer="L2",
            callback=_budget_alignment_check,
        )

        def _pricing_sync() -> None:
            try:
                from zephyr.governance.pricing_sync import PricingSync

                ps = PricingSync()
                updated = ps.sync_from_litellm()
                if updated > 0:
                    logger.info("Pricing sync: %d models updated", updated)
            except Exception as e:
                logger.warning("Pricing sync failed: %s", e)

        circadian_scheduler.register_task(
            hour=2,
            name="pricing_sync",
            layer="L1",
            callback=_pricing_sync,
        )

        def _temp_file_cleanup() -> None:
            try:
                import subprocess

                result = subprocess.run(
                    [sys.executable, "scripts/governance/d1_structure/detect_temp_files.py", "--clean"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(project_root),
                )
                if result.stdout:
                    logger.info(
                        "Temp file cleanup: %s", result.stdout[-300:] if len(result.stdout) > 300 else result.stdout
                    )
            except Exception as e:
                logger.warning("Temp file cleanup failed: %s", e)

        circadian_scheduler.register_task(
            hour=6,
            name="temp_file_cleanup",
            layer="L2",
            callback=_temp_file_cleanup,
        )

        def _triple_alignment_check() -> None:
            try:
                import subprocess

                result = subprocess.run(
                    [sys.executable, "src/zephyr/gates/triple_alignment.py"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(project_root),
                )
                if result.returncode != 0:
                    logger.warning(
                        "Triple alignment check returned %d: %s",
                        result.returncode,
                        result.stdout[-300:] if result.stdout else "",
                    )
                else:
                    logger.info("Triple alignment check: PASS")
            except Exception as e:
                logger.warning("Triple alignment check failed: %s", e)

        circadian_scheduler.register_task(
            hour=7,
            name="triple_alignment_check",
            layer="L1",
            callback=_triple_alignment_check,
        )

        def _escalation_self_test() -> None:
            try:
                from zephyr.governance.self_test import run_self_test

                report = run_self_test()
                if report.health.name != "HEALTHY":
                    logger.warning("Escalation self-test: %s", report.health.name)
            except Exception as e:
                logger.warning("Escalation self-test failed: %s", e)

        circadian_scheduler.register_task(
            hour=3,
            name="escalation_self_test",
            layer="L1",
            callback=_escalation_self_test,
        )

        # DM-400 修复2: 每小时释放超时未完成的 IN_PROGRESS 任务
        def _recover_stale_tasks() -> None:
            try:
                from zephyr.governance.persistence.task_repo import TaskRepository as _TR

                _repo = _TR()
                # 遍历所有活跃 batch_id，释放超时任务
                batches = _repo._conn.execute(
                    "SELECT DISTINCT batch_id FROM tasks WHERE status = 'IN_PROGRESS' AND is_deleted = 0 AND batch_id IS NOT NULL"
                ).fetchall()
                total_recovered = 0
                for (bid,) in batches:
                    n = _repo.recover_stale_claims(batch_id=bid, timeout_minutes=30)
                    total_recovered += n
                if total_recovered > 0:
                    logger.warning(
                        "DM-400: recovered %d stale IN_PROGRESS tasks across %d batches", total_recovered, len(batches)
                    )
            except Exception as e:
                logger.warning("DM-400 stale task recovery failed: %s", e)

        # 每小时整点执行（hour=-1 表示每小时）
        circadian_scheduler.register_task(
            hour=-1,
            name="stale_task_recovery",
            layer="L1",
            callback=_recover_stale_tasks,
        )

        # MCP 集群定时健康检查（每小时自愈）：检测死亡进程并自动重启
        def _mcp_health_check() -> None:
            try:
                import importlib.util

                launcher_path = project_root / "scripts" / "mcp" / "launcher.py"
                if not launcher_path.exists():
                    logger.debug("MCP health check: launcher.py not found")
                    return

                spec = importlib.util.spec_from_file_location("launcher_health", launcher_path)
                if spec is None or spec.loader is None:
                    logger.warning("MCP health check: launcher spec creation failed")
                    return
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                gateway = getattr(mod, "_gateway", None)
                if gateway is None:
                    logger.debug("MCP health check: _gateway is None (cluster not started)")
                    return

                server_scripts = getattr(mod, "SERVER_SCRIPTS", {})
                if not server_scripts:
                    logger.debug("MCP health check: SERVER_SCRIPTS empty")
                    return

                healthy = 0
                recovered = 0
                failed = 0
                for server_id in server_scripts:
                    try:
                        if mod.check_server_health(server_id, gateway):
                            healthy += 1
                        else:
                            if mod.restart_server(server_id, gateway):
                                recovered += 1
                                logger.info("MCP health check: recovered server '%s'", server_id)
                            else:
                                failed += 1
                                logger.warning("MCP health check: failed to recover server '%s'", server_id)
                    except Exception as exc:
                        failed += 1
                        logger.warning("MCP health check: error checking '%s': %s", server_id, exc)

                logger.info(
                    "MCP health check: %d servers (healthy=%d, recovered=%d, failed=%d)",
                    len(server_scripts),
                    healthy,
                    recovered,
                    failed,
                )
            except Exception as e:
                logger.warning("MCP health check failed: %s", e)

        circadian_scheduler.register_task(
            hour=-1,
            name="mcp_health_check",
            layer="L1",
            callback=_mcp_health_check,
        )

        # DM-201247: SLA 每小时报告
        def _sla_hourly_report() -> None:
            """生成 SLA 报告 — DM-201247.

            每小时收集健康状态 + 指标快照，输出到日志。
            """
            try:
                from zephyr.trading.health_monitor import HealthMonitor

                hm = HealthMonitor()
                report = hm.reconcile()
                logger.info(
                    "SLA hourly report: active=%d degraded=%d inactive=%d orphan_rate=%.2f",
                    report.active,
                    report.degraded,
                    report.inactive,
                    report.orphan_rate,
                )
                if report.actions_taken:
                    logger.info("SLA actions: %s", "; ".join(report.actions_taken))
            except Exception as e:
                logger.warning("SLA hourly report failed: %s", e)

        circadian_scheduler.register_task(
            hour=-1,
            name="sla_hourly_report",
            layer="L1",
            callback=_sla_hourly_report,
        )

        logger.info(
            "Task system cron jobs registered: escalation/timeout/orphan_scan/daily_dedup/budget_health/budget_alignment/temp_cleanup/triple_alignment/escalation_self_test/stale_task_recovery/mcp_health_check/sla_hourly_report"
        )
    except Exception as e:
        logger.warning("Failed to register task system cron jobs: %s", e)
