# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.brain_integration
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] tests/audit/test_brain_integration_root.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 大脑集成不可断开
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_brain_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ProbeHierarchy - K8s 3-Probe + Terraform Reconciliation"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from zephyr.shared.utils.async_utils import run_sync

if TYPE_CHECKING:
    from zephyr.gov_drift.cold_start import ColdStartResult

logger = logging.getLogger(__name__)


# 5.155.20 修复：原独立计算项目根（重复SSoT），改用REPO_ROOT
from zephyr.shared.io.paths import REPO_ROOT
_PROJECT_ROOT = str(REPO_ROOT)


class ProbeStatus:
    PASS = "PASS"

    WARN = "WARN"

    FAIL = "FAIL"

    SKIPPED = "SKIPPED"


@dataclass
class L0StartupResult:
    phase: str = "L0_STARTUP"

    status: str = ProbeStatus.SKIPPED

    env_ok: bool = False

    env_details: str = ""

    core_integrity_ok: bool = False

    core_integrity_checks: int = 0

    core_integrity_failed: int = 0

    db_ok: bool = False

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


@dataclass
class L1ReadinessResult:
    phase: str = "L1_READINESS"

    status: str = ProbeStatus.SKIPPED

    startup_check_ok: bool = False

    startup_checks_passed: int = 0

    startup_checks_total: int = 0

    gate_selfcheck_ok: bool = False

    gate_checks_passed: int = 0

    gate_checks_total: int = 0

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


@dataclass
class L2LivenessResult:
    phase: str = "L2_LIVENESS"

    status: str = ProbeStatus.SKIPPED

    scan_events_found: int = 0

    orphan_resources: int = 0

    credibility_scores: int = 0

    correlation_findings: int = 0

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


@dataclass
class L3ReconcileResult:
    phase: str = "L3_RECONCILE"

    status: str = ProbeStatus.SKIPPED

    forensics_reports: int = 0

    fix_applied: int = 0

    fix_failed: int = 0

    cascade_alerts: int = 0

    verify_events_remaining: int = -1

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


@dataclass
class FullProbeResult:
    probe_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    completed_at: str = ""

    l0: L0StartupResult = field(default_factory=L0StartupResult)

    l1: L1ReadinessResult = field(default_factory=L1ReadinessResult)

    l2: L2LivenessResult = field(default_factory=L2LivenessResult)

    l3: L3ReconcileResult = field(default_factory=L3ReconcileResult)

    classification: str = "PENDING"

    total_errors: int = 0

    total_warnings: int = 0

    def mark_completed(self):
        self.completed_at = datetime.now(UTC).isoformat()

        self.total_errors = sum(len(r.errors) for r in [self.l0, self.l1, self.l2, self.l3])

        self.total_warnings = sum(len(r.warnings) for r in [self.l0, self.l1, self.l2, self.l3])

        if self.l0.status == ProbeStatus.FAIL:
            self.classification = "STARTUP_FAILED"

        elif self.l1.status == ProbeStatus.FAIL:
            self.classification = "NOT_READY"

        elif self.l2.scan_events_found == 0:
            self.classification = "HEALTHY"

        elif self.l3.verify_events_remaining == 0:
            self.classification = "RECOVERED"

        elif self.l3.fix_applied > 0:
            self.classification = "PARTIALLY_RECOVERED"

        elif self.l3.fix_failed > 0 and self.l3.fix_applied == 0:
            self.classification = "RECOVERY_FAILED"

        elif self.l2.scan_events_found > 0:
            self.classification = "UNRESOLVED"

        else:
            self.classification = "HEALTHY"

    def summary(self):
        return (
            "probe=" + self.probe_id[:8] + " "
            "L0=" + self.l0.status + " L1=" + self.l1.status + " "
            "L2="
            + str(self.l2.scan_events_found)
            + "events L3="
            + str(self.l3.fix_applied)
            + "fixed/"
            + str(self.l3.verify_events_remaining)
            + "remain ->"
            + self.classification
        )


def _run_async(coro):
    # 5.16.9 修复：移除废弃的 get_event_loop fallback，run_sync 已处理所有场景
    return run_sync(coro)


def _l0_startup_probe(project_root, result):
    try:
        from pathlib import Path as _Path

        from zephyr.gov_drift.self_check import (
            bootstrap_self_check,
            check_core_files,
            check_registry_parsable,
        )

        base = _Path(__file__).parent

        core_results = check_core_files(base)

        missing_files = [k for k, v in core_results.items() if v == "MISSING"]

        result.core_integrity_checks = len(core_results)

        result.core_integrity_failed = len(missing_files)

        result.core_integrity_ok = result.core_integrity_failed == 0

        if not result.core_integrity_ok:
            result.errors.append("core_integrity: MISSING " + ", ".join(missing_files[:5]))

        registry_ok = check_registry_parsable(base)

        if not registry_ok:
            result.errors.append("registry: _detector-registry.yaml not parsable")

        db_ok = bootstrap_self_check(base)

        result.db_ok = db_ok

        if not db_ok:
            result.errors.append("db_self_check: files or registry failed")

        env_check_path = Path(project_root) / "scripts" / "governance" / "env_check.py"

        if env_check_path.exists():
            proc = subprocess.run(
                [os.sys.executable, str(env_check_path)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root,
                encoding="utf-8",
                errors="replace",
            )

            result.env_ok = proc.returncode == 0

            result.env_details = proc.stdout.strip()[:500]

        else:
            result.env_ok = True

            result.warnings.append("env_check.py not found, skipping")

    except ImportError as exc:
        result.errors.append("ImportError: " + str(exc))

    except Exception as exc:
        result.errors.append("L0 exception: " + str(exc))

        logger.exception("probe failed with exception", exc_info=True)
        result.errors.append("internal error")

    if result.errors:
        result.status = ProbeStatus.FAIL

    elif result.warnings:
        result.status = ProbeStatus.WARN

    else:
        result.status = ProbeStatus.PASS


def _l1_readiness_probe(project_root, result):
    import re

    try:
        session_check_path = Path(project_root) / "scripts" / "governance" / "session_startup_check.py"

        if session_check_path.exists():
            proc = subprocess.run(
                [os.sys.executable, str(session_check_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_root,
                encoding="utf-8",
                errors="replace",
            )

            result.startup_check_ok = proc.returncode == 0

            output = proc.stdout.strip()

            passed_m = re.search(r"PASSED[:\s]+(\d+)", output, re.IGNORECASE)

            total_m = re.search(r"TOTAL[:\s]+(\d+)", output, re.IGNORECASE)

            result.startup_checks_passed = int(passed_m.group(1)) if passed_m else 0

            result.startup_checks_total = int(total_m.group(1)) if total_m else 14

            if not result.startup_check_ok:
                failed_lines = [l for l in output.splitlines() if "FAIL" in l or "ERROR" in l]

                result.warnings.extend(failed_lines[:5])

        else:
            result.startup_check_ok = False

            result.warnings.append("session_startup_check.py not found")

        gate_check_path = Path(project_root) / "scripts" / "governance" / "gate_engine_selfcheck.py"

        if gate_check_path.exists():
            proc = subprocess.run(
                [os.sys.executable, str(gate_check_path)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root,
                encoding="utf-8",
                errors="replace",
            )

            result.gate_selfcheck_ok = proc.returncode == 0

        else:
            result.gate_selfcheck_ok = False

            result.warnings.append("gate_engine_selfcheck.py not found")

    except Exception as exc:
        result.errors.append("L1 exception: " + str(exc))

        logger.exception("probe failed with exception", exc_info=True)
        result.errors.append("internal error")

    if result.errors:
        result.status = ProbeStatus.FAIL

    elif result.warnings:
        result.status = ProbeStatus.WARN

    else:
        result.status = ProbeStatus.PASS


def _l2_liveness_probe(result):
    try:
        from zephyr.gov_drift.drift_engine import ScanLevel, scan

        scan_result = _run_async(scan(level=ScanLevel.LIGHT))

        result.scan_events_found = scan_result.total_drift_events

        try:
            from zephyr.gov_drift.orphan_scanner import OrphanScanner

            scanner = OrphanScanner()

            orphans = scanner.scan()

            result.orphan_resources = len(orphans)

        except Exception as e:
            logger.debug("suppressed error in brain_integration", exc_info=True)

        try:
            from zephyr.gov_drift.credibility_engine import CredibilityEngine

            engine = CredibilityEngine()

            for evt in getattr(scan_result, "events", [])[:10]:
                engine.compute(
                    detector_id=getattr(evt, "detector_id", "unknown"),
                    is_proven=False,
                    fp_count=0,
                    total_alerts=1,
                    last_seen=None,
                )

            result.credibility_scores = len(engine._scores)

        except Exception as e:
            logger.warning("suppressed error in brain_integration", exc_info=True)

        try:
            from zephyr.gov_drift.correlation_engine import CorrelationEngine

            corr_engine = CorrelationEngine()

            co_occurrence = corr_engine.compute_co_occurrence()

            result.correlation_findings = len(co_occurrence)

        except Exception as e:
            logger.warning("suppressed error in brain_integration", exc_info=True)

    except Exception as exc:
        result.errors.append("L2 exception: " + str(exc))

        logger.exception("probe failed with exception", exc_info=True)
        result.errors.append("internal error")

    if result.errors:
        result.status = ProbeStatus.FAIL

    elif result.scan_events_found > 0:
        result.status = ProbeStatus.WARN

    else:
        result.status = ProbeStatus.PASS


def _l3_reconcile(result, scan_level="LIGHT"):
    try:
        try:
            from zephyr.gov_drift.forensics_engine import ForensicsConfig, ForensicsEngine

            forensics = ForensicsEngine(ForensicsConfig())

            forensics.build_timeline()

            result.forensics_reports = len(forensics.timeline_entries)

        except Exception as e:
            logger.warning("suppressed error in brain_integration", exc_info=True)

        import importlib as _il

        _gd = _il.import_module("zephyr.gov_enforcement.rule_enforcement.drift_detector")
        trigger_recovery = _gd.trigger_recovery

        recovery = trigger_recovery(
            {
                "module_id": "MOD-INF-023",
                "changed_files": [],
                "commit_message": "",
                "scan_level": scan_level,
            }
        )

        fix_results = recovery.get("fix_results", []) or []

        for fr in fix_results:
            status = fr.get("status", "")

            if status in ("AUTO_FIXED", "ROLLBACK_EXECUTED", "MANUAL_REQUIRED"):
                result.fix_applied += 1

            else:
                result.fix_failed += 1

        cascade_alerts = recovery.get("cascade_alerts", []) or []

        result.cascade_alerts = len(cascade_alerts)

        from zephyr.gov_drift.drift_engine import ScanLevel, scan

        verify_result = _run_async(scan(level=ScanLevel.LIGHT))

        result.verify_events_remaining = verify_result.total_drift_events

    except Exception as exc:
        result.errors.append("L3 exception: " + str(exc))

        logger.exception("probe failed with exception", exc_info=True)
        result.errors.append("internal error")

    if result.verify_events_remaining == 0:
        result.status = ProbeStatus.PASS

    elif result.fix_applied > 0:
        result.status = ProbeStatus.WARN

    else:
        result.status = ProbeStatus.FAIL


def execute_full_probe(project_root: str = "", scan_level: str = "LIGHT") -> FullProbeResult:
    root = project_root or _PROJECT_ROOT

    result = FullProbeResult()

    _l0_startup_probe(root, result.l0)

    if result.l0.status == ProbeStatus.FAIL:
        logger.error("L0 STARTUP failed, aborting probe chain")

        result.mark_completed()

        return result

    _l1_readiness_probe(root, result.l1)

    _l2_liveness_probe(result.l2)

    if result.l2.scan_events_found > 0:
        _l3_reconcile(result.l3, scan_level)

    else:
        result.l3.status = ProbeStatus.SKIPPED

    result.mark_completed()

    logger.info("FullProbe: %s", result.summary())

    return result


def session_entry_full_probe(project_root: str = "") -> tuple[ColdStartResult, FullProbeResult | None]:
    from zephyr.gov_drift.cold_start import session_entry_activate

    cold_result = session_entry_activate(project_root)

    probe_result = None

    try:
        probe_result = execute_full_probe(project_root=project_root, scan_level="LIGHT")

        logger.info("STEP 4.9 full probe: %s", probe_result.summary())

    except Exception as exc:
        logger.warning("STEP 4.9 full probe failed: %s", exc, exc_info=True)

    return cold_result, probe_result


execute_closed_loop = execute_full_probe


session_entry_closed_loop = session_entry_full_probe


ClosedLoopResult = FullProbeResult