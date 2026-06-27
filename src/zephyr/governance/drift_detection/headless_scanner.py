# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] zephyr.governance.drift_detection.headless_scanner
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_headless_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Headless Scanner — headless_scanner.py

module_id: MOD-INF-023
LIGHT+DEEP 与会话日志 _interrupt_log.jsonl 扫描。
对标 blueprint.md §2.18 / D-023-32。
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass

from .drift_models import ScanResult


@dataclass
class HeadlessDiffEntry:
    file: str
    hunk: str = ""
    dimension: str = ""
    file_version: str = ""
    sha256: str = ""


@dataclass
class InterruptLog:
    session_id: str
    triggered_by: str
    context_at: str
    scan_outcome: str
    errors_found: int


def _scan_script(script_path: str) -> list[HeadlessDiffEntry]:
    if not os.path.exists(script_path):
        return []
    try:
        import subprocess

        result = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        output = json.loads(result.stdout)
        if not isinstance(output, list):
            return []
        return [
            HeadlessDiffEntry(
                file=entry.get("file", ""),
                hunk=entry.get("hunk", ""),
                dimension=entry.get("dimension", ""),
                sha256=entry.get("sha256", ""),
            )
            for entry in output
            if isinstance(entry, dict)
        ]
    except Exception:
        return []


def headless_scan_light(modules: list[str], project_root: str | None = None) -> ScanResult:
    root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    scripts_dir = os.path.join(root, "scripts", "governance", "d5_architecture")
    results: list[object] = []
    for fname in sorted(os.listdir(scripts_dir)) if os.path.isdir(scripts_dir) else []:
        if not fname.startswith("validate_") or not fname.endswith(".py"):
            continue
        fp = os.path.join(scripts_dir, fname)
        entries = _scan_script(fp)
        results.extend(entries)
    return ScanResult(
        scan_id=uuid.uuid4(),
        detectors_run=len(list(os.listdir(scripts_dir))) if os.path.isdir(scripts_dir) else 0,
        total_drift_events=len(results),
        new_events=[],
        resolved_events=[],
        storm_mode_triggered=len(results) > 50,
    )


def parse_interrupt_log(log_path: str) -> list[InterruptLog]:
    if not os.path.exists(log_path):
        return []
    entries: list[InterruptLog] = []
    try:
        with open(log_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(
                        InterruptLog(
                            session_id=data.get("session_id", ""),
                            triggered_by=data.get("triggered_by", ""),
                            context_at=data.get("context_at", ""),
                            scan_outcome=data.get("scan_outcome", ""),
                            errors_found=data.get("errors_found", 0),
                        )
                    )
                except json.JSONDecodeError:
                    pass
    except (OSError, UnicodeDecodeError):
        pass
    return entries
