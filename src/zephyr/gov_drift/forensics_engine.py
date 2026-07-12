# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.forensics_engine
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; src/zephyr/governance/drift_detection/brain_integration.py; tests/audit/test_forensics_engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 取证结果不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_forensics_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Forensics Engine — 漂移取证引擎 §6.17。





module_id: MOD-INF-023


replay: git checkout还原代码 + drift_events表活跃漂移 + baseline历史重放


forensics_report: timeline + state_diffs + actor_trace + dependency_impact


对标 blueprint.md §6.17。"""

from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

import logging

logger = logging.getLogger(__name__)

import os
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ForensicsTimelineEntry:
    timestamp: datetime

    action: str

    actor: str

    state_before: str

    state_after: str

    file_changed: str

    diff_summary: str


@dataclass
class ForensicsReport:
    report_id: str

    drift_event_id: str

    module: str

    detector_id: str

    severity: str

    state: str

    timeline: list[ForensicsTimelineEntry]

    state_diffs: list[dict[str, str]]

    actor_trace: list[str]

    dependency_impact: dict[str, list[str]]

    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ForensicsConfig:
    state_dir: str = ""

    max_timeline_entries: int = 50

    include_blame: bool = True


FORENSICS_CONFIG: Final[ForensicsConfig] = ForensicsConfig()


def replay_baseline_history(
    file_path: str,
    baseline_history: list[dict[str, str]],
    drift_events: list[dict[str, object]],
) -> ForensicsReport:
    """重放baseline历史，重构时间线。"""

    event_id = Path(file_path).stem

    report_id = f"forensics-{event_id}-{datetime.now(UTC).strftime('%Y%m%d%H%M')}"

    timeline: list[ForensicsTimelineEntry] = []

    states_seen: dict[int, str] = {}

    actors: list[str] = []

    for i, entry in enumerate(baseline_history[: FORENSICS_CONFIG.max_timeline_entries]):
        ts_str = entry.get("timestamp", "")

        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

        except Exception:
            ts = datetime.now(UTC)

        action = entry.get("action", "unknown")

        state_before_val = states_seen.get(i - 1, "UNKNOWN")

        state_after_val = entry.get("state_after", "UNKNOWN")

        actor = "system"

        for evt in drift_events:
            if str(evt.get("source_file", "")) == file_path:
                actor = str(evt.get("detector_id", "unknown"))

                break

        states_seen[i] = state_after_val

        actors.append(actor)

        timeline.append(
            ForensicsTimelineEntry(
                timestamp=ts,
                action=action,
                actor=actor,
                state_before=state_before_val,
                state_after=state_after_val,
                file_changed=file_path,
                diff_summary=entry.get("diff", "N/A"),
            )
        )

    state_diffs: list[dict[str, str]] = []

    for i in range(1, len(timeline)):
        if timeline[i].state_before != timeline[i].state_after:
            state_diffs.append(
                {
                    "timestamp": timeline[i].timestamp.isoformat(),
                    "before": timeline[i].state_before,
                    "after": timeline[i].state_after,
                    "actor": timeline[i].actor,
                }
            )

    unique_actors = list(dict.fromkeys(actors))

    dep_impact: dict[str, list[str]] = {}

    source_path = Path(file_path)

    parent_dir = source_path.parent

    if parent_dir.exists():
        for sibling in parent_dir.iterdir():
            if sibling.is_file() and sibling.suffix == ".py":
                dep_impact.setdefault("sibling_modules", []).append(sibling.name)

    return ForensicsReport(
        report_id=report_id,
        drift_event_id=event_id,
        module=source_path.parts[0] if source_path.parts else "unknown",
        detector_id="forensics_engine",
        severity="MAJOR",
        state="DETECTED",
        timeline=timeline,
        state_diffs=state_diffs,
        actor_trace=unique_actors,
        dependency_impact=dep_impact,
    )


def git_checkout_snapshot(
    commit_hash: str,
    file_path: str,
    project_root: str,
) -> str | None:
    """用git checkout还原代码到指定commit状态。"""

    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root,
        )

        if result.returncode == 0:
            return result.stdout

    except Exception as e:
        logger.warning("suppressed error in forensics_engine", exc_info=True)

    return None


def generate_forensics_report(
    drift_event_id: str,
    source_file: str,
    project_root: str,
    baseline_history: list[dict[str, str]] | None = None,
    drift_events: list[dict[str, object]] | None = None,
) -> ForensicsReport:
    """生成完整的取证报告。"""

    history = baseline_history or []

    events = drift_events or []

    report = replay_baseline_history(source_file, history, events)

    if FORENSICS_CONFIG.include_blame and project_root:
        try:
            blame_result = subprocess.run(
                ["git", "log", "-n", "5", "--oneline", "--", source_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=project_root,
            )

            if blame_result.returncode == 0 and blame_result.stdout.strip():
                commit_lines = blame_result.stdout.strip().split("\n")

                for cl in commit_lines:
                    parts = cl.split(" ", 1)

                    if len(parts) >= 2:
                        report.dependency_impact.setdefault("commits", []).append(parts[0])

        except Exception as e:
            logger.warning("suppressed error in forensics_engine", exc_info=True)

    return report


def serialize_report(report: ForensicsReport, output_dir: str) -> str:
    """序列化取证报告为JSON。"""

    os.makedirs(output_dir, exist_ok=True)

    safe_id = report.report_id.replace("/", "-").replace("\\", "-")

    path = os.path.join(output_dir, f"{safe_id}.json")

    report_dict: dict[str, object] = {
        "report_id": report.report_id,
        "drift_event_id": report.drift_event_id,
        "module": report.module,
        "detector_id": report.detector_id,
        "severity": report.severity,
        "state": report.state,
        "timeline": [
            {
                "timestamp": e.timestamp.isoformat(),
                "action": e.action,
                "actor": e.actor,
                "state_before": e.state_before,
                "state_after": e.state_after,
                "file_changed": e.file_changed,
                "diff_summary": e.diff_summary,
            }
            for e in report.timeline
        ],
        "state_diffs": report.state_diffs,
        "actor_trace": report.actor_trace,
        "dependency_impact": report.dependency_impact,
        "generated_at": report.generated_at.isoformat(),
    }

    content = dumps(report_dict, indent=2,  ensure_ascii=False)

    tmp_path = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        os.replace(tmp_path, path)

    except PermissionError:
        try:
            os.remove(tmp_path)

        except OSError:
            pass

    return path
