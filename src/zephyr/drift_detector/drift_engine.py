"""
Drift Detector 核心引擎 — drift_engine.py

module_id: MOD-INF-023
实现检测器发现→调度→汇总→写入 + 5触发策略 + 维护窗口 + 预算 + 检查点 + 风暴 + 环境感知。
对标 blueprint.md §2.1/§2.3/§2.4/§2.6/§2.9/§2.10/§2.11/§2.13/§5.1。
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import signal
import sys
import sqlite3
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import yaml

from .drift_models import (
    BulkDriftEvent,
    Detector,
    DriftBudget,
    DriftEvent,
    DriftReport,
    DriftState,
    OrphanClassification,
    ScanLevel,
    ScanResult,
    Severity,
)

_REGISTRY_PATH: str = ""
_ENGINE_ROOT: str = ""
_shutting_down: bool = False


def _resolve_paths() -> None:
    global _REGISTRY_PATH, _ENGINE_ROOT
    _ENGINE_ROOT = os.path.dirname(os.path.abspath(__file__))
    _REGISTRY_PATH = os.path.join(_ENGINE_ROOT, "_detector_registry.yaml")


def load_detector_registry(registry_path: Optional[str] = None) -> list[Detector]:
    if not _REGISTRY_PATH:
        _resolve_paths()
    path = registry_path or _REGISTRY_PATH
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, object] = yaml.safe_load(fh) or {}
    detectors_raw: dict[str, object] = raw.get("detectors", {}) or {}
    detectors: list[Detector] = []
    _parse_detector_list(detectors_raw.get("existing", []), detectors)
    _parse_detector_list(detectors_raw.get("new", []), detectors)
    return detectors


def _parse_detector_list(raw_list: object, detectors: list[Detector]) -> None:
    if not isinstance(raw_list, list):
        return
    for entry in raw_list:
        if not isinstance(entry, dict):
            continue
        detectors.append(Detector(
            id=str(entry.get("id", "")),
            drift_dimension=str(entry.get("drift_dimension", "")),
            severity=Severity(str(entry.get("severity", "MEDIUM"))),
            category=str(entry.get("category", "unknown")),
            script=entry.get("script"),
            method=entry.get("method"),
            status=str(entry.get("status", "active")),
            auto_fixable=bool(entry.get("auto_fixable", False)),
            check_dims=[str(d) for d in entry.get("check_dims", []) or []],
        ))


@dataclass
class MaintenanceWindow:
    start_time: datetime
    end_time: datetime
    is_shadow_mode: bool = True
    triggered_by_auto: bool = False

    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.start_time <= now <= self.end_time

    def time_remaining(self) -> timedelta:
        return max(self.end_time - datetime.now(timezone.utc), timedelta(0))


_last_window: Optional[MaintenanceWindow] = None
_budgets: dict[str, DriftBudget] = {}
_checkpoints_dir: str = ""


def get_maintenance_window() -> Optional[MaintenanceWindow]:
    return _last_window


def declare_maintenance_window(hours: int = 2, triggered_by_auto: bool = False) -> MaintenanceWindow:
    global _last_window
    now = datetime.now(timezone.utc)
    _last_window = MaintenanceWindow(start_time=now, end_time=now + timedelta(hours=hours), triggered_by_auto=triggered_by_auto)
    return _last_window


def check_large_diff(threshold: int = 50) -> bool:
    try:
        result = subprocess.run(["git", "diff", "--stat", "HEAD~1"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split("\n")
        return (len(lines) - 1) > threshold
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# ── Budget ─────────────────────────────────────────────────

def get_or_create_budget(module_id: str, tier: str = "P0") -> DriftBudget:
    key = f"{module_id}:{tier}"
    if key not in _budgets:
        _budgets[key] = DriftBudget(
            module_id=module_id, tier=tier,
            monthly_budget=DriftBudget.tier_budget(tier),
            remaining=DriftBudget.tier_budget(tier),
            reset_date=date.today().replace(day=1),
        )
    return _budgets[key]


def consume_budget(module_id: str, tier: str = "P0") -> bool:
    budget = get_or_create_budget(module_id, tier)
    budget.consume(1)
    return budget.is_exhausted()


def check_budget_for_gate(module_id: str, tier: str = "P0", break_glass: bool = False) -> dict[str, object]:
    if break_glass:
        return {"allowed": True, "reason": "BREAK_GLASS", "requires": "Owner approval + audit chain"}
    budget = get_or_create_budget(module_id, tier)
    if budget.is_exhausted():
        if tier == "P0":
            return {"allowed": False, "reason": "HARD_LIMIT_P0"}
        elif tier == "P1":
            return {"allowed": False, "reason": "DOWNGRADED_P3"}
        else:
            return {"allowed": True, "reason": "WARNING_P2"}
    return {"allowed": True, "reason": "OK"}


# ── Checkpoint + Recovery ───────────────────────────────────

class CheckpointWriter:

    @staticmethod
    def write(scan_id: uuid.UUID, completed_detectors: list[str], scan_start_time: str, project_root: Optional[str] = None) -> None:
        root = project_root or _ENGINE_ROOT
        if not root:
            return
        ckpt_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(root))), "data", "drift_checkpoints") if "drift_detector" in root else os.path.join(root, "data", "drift_checkpoints")
        os.makedirs(ckpt_dir, exist_ok=True)
        global _checkpoints_dir
        _checkpoints_dir = ckpt_dir
        ckpt_path = os.path.join(ckpt_dir, f"{scan_id}.json")
        data = {"scan_id": str(scan_id), "completed_detectors": completed_detectors, "last_checkpoint_time": datetime.now(timezone.utc).isoformat(), "scan_start_time": scan_start_time}
        tmp_path = f"{ckpt_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_path, ckpt_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    @staticmethod
    def cleanup(scan_id: uuid.UUID) -> None:
        if _checkpoints_dir:
            ckpt_path = os.path.join(_checkpoints_dir, f"{scan_id}.json")
            if os.path.exists(ckpt_path):
                os.remove(ckpt_path)


class RecoveryManager:

    @staticmethod
    def check_orphaned(_project_root: Optional[str] = None) -> list[str]:
        ckpt_dir = _checkpoints_dir
        if not ckpt_dir or not os.path.isdir(ckpt_dir):
            return []
        orphaned: list[str] = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        for fname in os.listdir(ckpt_dir):
            if not fname.endswith(".json"):
                continue
            full = os.path.join(ckpt_dir, fname)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=timezone.utc)
                if mtime < cutoff:
                    orphaned.append(fname.replace(".json", ""))
            except OSError:
                pass
        return orphaned

    @staticmethod
    def on_startup(_project_root: Optional[str] = None) -> Optional[dict[str, object]]:
        ckpt_dir = _checkpoints_dir
        if not ckpt_dir or not os.path.isdir(ckpt_dir):
            return None
        try:
            for fname in sorted(os.listdir(ckpt_dir)):
                if not fname.endswith(".json"):
                    continue
                full = os.path.join(ckpt_dir, fname)
                with open(full, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=timezone.utc)
                if (datetime.now(timezone.utc) - mtime) > timedelta(hours=24):
                    continue
                return data
        except (json.JSONDecodeError, OSError):
            pass
        return None


def _install_signal_handlers() -> None:
    def _handler(_signum: int, _frame: object) -> None:
        global _shutting_down
        _shutting_down = True
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handler)
        except (ValueError, OSError):
            pass


# ── Storm Detection ─────────────────────────────────────────

STORM_THRESHOLD: int = 50
_expected_storm_keywords: set[str] = {"REFACTOR", "MIGRATION", "REFORMAT", "RENAME"}


def _detect_expected_storm(commit_message: str) -> bool:
    return any(kw in commit_message.upper() for kw in _expected_storm_keywords)


def _create_bulk_event(scan_id: uuid.UUID, events: list[DriftEvent], commit_message: str = "") -> BulkDriftEvent:
    modules = list({e.module_id for e in events})
    dims: dict[str, int] = {}
    for e in events:
        dims[e.drift_dimension] = dims.get(e.drift_dimension, 0) + 1
    is_expected = _detect_expected_storm(commit_message)
    return BulkDriftEvent(
        event_id=uuid.uuid4(), scan_id=scan_id, affected_modules=modules, dimension_groups=dims,
        is_expected=is_expected, is_unexpected=not is_expected,
        child_event_ids=[e.event_id for e in events], created_at=datetime.now(timezone.utc),
    )


def _split_bulk_to_individual(bulk: BulkDriftEvent, events: list[DriftEvent]) -> list[DriftEvent]:
    return [e for e in events if e.event_id in bulk.child_event_ids]


# ── Environment Awareness ──────────────────────────────────

_module_env_tags: dict[str, dict[str, str]] = {}


def register_env_tags(module_id: str, tags: dict[str, str]) -> None:
    _module_env_tags[module_id] = tags


@dataclass
class EnvDiffReport:
    module_id: str
    diff_type: str
    env_tags: dict[str, str] = field(default_factory=dict)
    is_true_drift: bool = True


def differential_detection(module_id: str, diffs: list[dict[str, object]], env_tags: Optional[dict[str, str]] = None) -> EnvDiffReport:
    tags = env_tags or _module_env_tags.get(module_id, {})
    env_diff_count = 0
    drift_count = 0
    for d in diffs:
        dim = str(d.get("drift_dimension", ""))
        if "env" in dim.lower() or "config_profile" in dim or "python_version" in dim:
            env_diff_count += 1
        else:
            drift_count += 1
    is_drift = drift_count > 0 or (env_diff_count > 0 and not tags)
    return EnvDiffReport(
        module_id=module_id,
        diff_type="ENV_DIFF" if not is_drift else "DRIFT",
        env_tags=tags,
        is_true_drift=is_drift,
    )


@dataclass
class PartialDeploymentRecord:
    module_a: str
    module_b: str
    started_at: datetime
    is_stalled: bool = False


_partial_deployments: dict[str, PartialDeploymentRecord] = {}


def detect_partial_deployment(module_ids: list[str]) -> Optional[PartialDeploymentRecord]:
    if len(module_ids) < 2:
        return None
    key = "_".join(sorted(module_ids[:2]))
    now = datetime.now(timezone.utc)
    if key not in _partial_deployments:
        rec = PartialDeploymentRecord(module_a=module_ids[0], module_b=module_ids[1], started_at=now)
        _partial_deployments[key] = rec
        return rec
    rec = _partial_deployments[key]
    if (now - rec.started_at).total_seconds() > 86400:
        rec.is_stalled = True
    return rec


# ── Scan Core ───────────────────────────────────────────────

async def scan(
    level: ScanLevel = ScanLevel.STANDARD,
    scope: Optional[list[str]] = None,
    registry_path: Optional[str] = None,
    commit_message: str = "",
) -> ScanResult:
    _resolve_paths()
    _install_signal_handlers()

    recovery = RecoveryManager.on_startup()
    resume_from: Optional[dict[str, object]] = recovery

    window = get_maintenance_window()
    in_shadow = window is not None and window.is_active() and window.is_shadow_mode

    if not in_shadow and check_large_diff():
        declare_maintenance_window(hours=2, triggered_by_auto=True)

    detectors = load_detector_registry(registry_path)

    if resume_from is not None:
        completed_ids: list[str] = resume_from.get("completed_detectors", []) or []
        remaining = [d for d in detectors if d.id not in completed_ids]
        scan_id = uuid.UUID(str(resume_from.get("scan_id", str(uuid.uuid4()))))
    else:
        completed_ids = []
        filtered = _filter_detectors_by_level(detectors, level, scope)
        remaining = filtered
        scan_id = uuid.uuid4()

    filtered = _filter_detectors_by_level(remaining, level, scope) if resume_from is not None else remaining

    events: list[DriftEvent] = []
    completed: list[str] = list(completed_ids)
    scan_start = (resume_from.get("scan_start_time", datetime.now(timezone.utc).isoformat())
                   if resume_from else datetime.now(timezone.utc).isoformat())

    sem = asyncio.Semaphore(_max_parallel(level))
    tasks = [_dispatch_detector_with_checkpoint(d, sem, scan_id, completed, scan_start) for d in filtered]
    results: list[dict[str, object]] = list(await asyncio.gather(*tasks))

    for r in results:
        for evt in (r.get("events", []) or []):
            parsed = _parse_event(evt)
            events.append(parsed)
            if parsed.state != DriftState.FALSE_POSITIVE:
                consume_budget(parsed.module_id, "P0")

    _write_drift_events(events)

    storm_mode = len(events) > STORM_THRESHOLD
    if storm_mode:
        _create_bulk_event(scan_id, events, commit_message)

    CheckpointWriter.cleanup(scan_id)

    return ScanResult(
        scan_id=scan_id, detectors_run=len(filtered), total_drift_events=len(events),
        new_events=[e.event_id for e in events], resolved_events=[],
        storm_mode_triggered=storm_mode, events=events,
    )


async def _dispatch_detector_with_checkpoint(detector: Detector, sem: asyncio.Semaphore, scan_id: uuid.UUID, completed: list[str], scan_start: str) -> dict[str, object]:
    if _shutting_down:
        return {"detector_id": detector.id, "events": []}
    result = await _dispatch_detector(detector, sem)
    completed.append(detector.id)
    CheckpointWriter.write(scan_id, completed, scan_start)
    return result


async def scan_on_commit(changed_files: list[str]) -> ScanResult:
    return await scan(level=ScanLevel.LIGHT, scope=changed_files)


async def scheduled_light() -> ScanResult:
    return await scan(level=ScanLevel.STANDARD)


async def scheduled_deep() -> ScanResult:
    return await scan(level=ScanLevel.DEEP)


async def scan_phase_gate(module_id: str) -> ScanResult:
    return await scan(level=ScanLevel.DEEP, scope=[module_id])


def build_report(result: ScanResult, registry_path: Optional[str] = None) -> DriftReport:
    detectors = load_detector_registry(registry_path)
    health_index: dict[str, float] = {}
    dim_counts: dict[str, int] = {}
    for evt in result.events:
        dim_counts[evt.drift_dimension] = dim_counts.get(evt.drift_dimension, 0) + 1
    for d in detectors:
        if d.drift_dimension:
            health_index[d.drift_dimension] = dim_counts.get(d.drift_dimension, 0)
    top = sorted(dim_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return DriftReport(module_health_index=health_index, top_drift_dimensions=top, active_drift_count=result.total_drift_events,
                       scan_summary=f"Scan {result.scan_id}: {result.detectors_run} detectors run, {result.total_drift_events} drift events")


def _filter_detectors_by_level(detectors: list[Detector], level: ScanLevel, scope: Optional[list[str]]) -> list[Detector]:
    if scope:
        return [d for d in detectors if d.id in scope]
    if level == ScanLevel.LIGHT:
        return [d for d in detectors if d.severity == Severity.HIGH]
    elif level == ScanLevel.STANDARD:
        return [d for d in detectors if d.severity in (Severity.HIGH, Severity.MEDIUM)]
    return detectors


def _max_parallel(level: ScanLevel) -> int:
    return {"LIGHT": 2, "STANDARD": 4, "DEEP": 8}.get(level.name, 4)


async def _dispatch_detector(detector: Detector, sem: asyncio.Semaphore) -> dict[str, object]:
    global _shutting_down
    async with sem:
        if _shutting_down:
            return {"detector_id": detector.id, "events": []}
        script = detector.script
        if not script:
            return {"detector_id": detector.id, "events": []}
        scripts_dir = os.path.join(os.path.dirname(_ENGINE_ROOT), "..", "..", "scripts", "governance")
        script_path = os.path.join(scripts_dir, script)
        if not os.path.exists(script_path):
            return {"detector_id": detector.id, "events": []}
        try:
            proc = await asyncio.create_subprocess_exec("python", script_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode != 0:
                evt = _create_drift_event(detector, f"Detector failed: {stderr.decode('utf-8', errors='replace')[:200]}")
                return {"detector_id": detector.id, "events": [_event_to_dict(evt)]}
            try:
                output = json.loads(stdout.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {"detector_id": detector.id, "events": []}
            return {"detector_id": detector.id, "events": output}
        except asyncio.TimeoutError:
            return {"detector_id": detector.id, "events": [_event_to_dict(_create_drift_event(detector, "Detector timed out after 30s"))]}
        except Exception as exc:
            return {"detector_id": detector.id, "events": [_event_to_dict(_create_drift_event(detector, f"Detector exception: {exc}"))]}


def _create_drift_event(detector: Detector, detail: str) -> DriftEvent:
    return DriftEvent(event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id=detector.id,
                      drift_dimension=detector.drift_dimension, baseline_version="0.1.0", state=DriftState.DETECTED,
                      created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), resolution_detail=detail)


def _event_to_dict(event: DriftEvent) -> dict[str, object]:
    return {"event_id": str(event.event_id), "module_id": event.module_id, "detector_id": event.detector_id,
            "drift_dimension": event.drift_dimension, "baseline_version": event.baseline_version,
            "state": event.state.value, "created_at": event.created_at.isoformat(), "updated_at": event.updated_at.isoformat(),
            "resolved_by": event.resolved_by, "resolution_detail": event.resolution_detail,
            "auto_fixed": event.auto_fixed, "rollback_verified": event.rollback_verified}


def _parse_event(raw: dict[str, object]) -> DriftEvent:
    return DriftEvent(
        event_id=uuid.UUID(str(raw.get("event_id", str(uuid.uuid4())))), module_id=str(raw.get("module_id", "")),
        detector_id=str(raw.get("detector_id", "")), drift_dimension=str(raw.get("drift_dimension", "")),
        baseline_version=str(raw.get("baseline_version", "")), state=DriftState(str(raw.get("state", "DETECTED"))),
        created_at=datetime.fromisoformat(str(raw.get("created_at", datetime.now(timezone.utc).isoformat()))),
        updated_at=datetime.fromisoformat(str(raw.get("updated_at", datetime.now(timezone.utc).isoformat()))),
        resolved_by=raw.get("resolved_by") if raw.get("resolved_by") else None,
        resolution_detail=raw.get("resolution_detail") if raw.get("resolution_detail") else None,
        auto_fixed=bool(raw.get("auto_fixed", False)), rollback_verified=bool(raw.get("rollback_verified", False)))


def _write_drift_events(events: list[DriftEvent], db_path: str | None = None) -> int:
    if not events:
        return 0
    if db_path is None:
        _resolve_paths()
        project_root = os.environ.get("ZEPHYR_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(_ENGINE_ROOT))))
        db_path = os.path.join(project_root, "data", "drift", "drift_events.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS drift_events (
            event_id TEXT PRIMARY KEY,
            detector_id TEXT NOT NULL,
            module_id TEXT DEFAULT 'MOD-INF-023',
            severity TEXT NOT NULL,
            state TEXT DEFAULT 'DETECTED',
            source_file TEXT,
            description TEXT,
            details TEXT,
            fix_description TEXT,
            timestamp TEXT NOT NULL,
            scan_level TEXT DEFAULT 'STANDARD',
            auto_fixable INTEGER DEFAULT 0,
            resolution_detail TEXT,
            roi_score REAL DEFAULT 0.0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_drift_detector ON drift_events(detector_id);
        CREATE INDEX IF NOT EXISTS idx_drift_state ON drift_events(state);
        CREATE INDEX IF NOT EXISTS idx_drift_severity ON drift_events(severity);
        CREATE INDEX IF NOT EXISTS idx_drift_timestamp ON drift_events(timestamp);
    """)
    written = 0
    for event in events:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO drift_events (event_id, detector_id, module_id, severity, state, "
                "description, timestamp, auto_fixable, resolution_detail, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(event.event_id), event.detector_id, event.module_id, "MEDIUM", event.state.value,
                    event.drift_dimension, event.created_at.isoformat(),
                    1 if event.auto_fixed else 0, event.resolution_detail,
                    event.created_at.isoformat(), event.updated_at.isoformat(),
                ),
            )
            written += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    return written


# ── AI Construction Detectors ─────────────────────────────

class AIConstructionDetectors:

    def detect_ai_hallucination_import(self, module_dir: str) -> list[DriftEvent]:
        import ast, importlib.util, sys, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        stdlib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
        safe_prefixes = ("__future__", "builtins")
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    tree = ast.parse(fh.read(), filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if top in stdlib or top.startswith(".") or top.startswith(safe_prefixes):
                            continue
                        if importlib.util.find_spec(top) is None:
                            events.append(DriftEvent(
                                event_id=uuid.uuid4(), module_id="MOD-INF-023",
                                detector_id="ai_hallucination_import",
                                drift_dimension="AI_import_hallucination", baseline_version="0.1.0",
                                state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                                updated_at=datetime.now(timezone.utc),
                                resolution_detail=f"Hallucinated import: {alias.name} in {fname}"))
                if isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue
                    if node.level and node.level > 0:
                        continue
                    top = node.module.split(".")[0]
                    if top in stdlib or top in ("__future__",):
                        continue
                    if importlib.util.find_spec(top) is None:
                        events.append(DriftEvent(
                            event_id=uuid.uuid4(), module_id="MOD-INF-023",
                            detector_id="ai_hallucination_import",
                            drift_dimension="AI_import_hallucination", baseline_version="0.1.0",
                            state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc),
                            resolution_detail=f"Hallucinated from import: {node.module} in {fname}"))
        return events


    def detect_ai_dead_code(self, module_dir: str) -> list[DriftEvent]:
        import ast, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        defined_classes: set[str] = set()
        defined_funcs: set[str] = set()
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    source = fh.read()
                    tree = ast.parse(source, filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    defined_classes.add(node.name)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        defined_funcs.add(node.name)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and all(
                    isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis)
                    for s in node.body
                ):
                    events.append(DriftEvent(
                        event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_dead_code",
                        drift_dimension="AI_dead_code", baseline_version="0.1.0", state=DriftState.DETECTED,
                        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                        resolution_detail=f"Dead code: {node.name}() body is only pass/... in {fname}"))
                if isinstance(node, ast.ClassDef) and all(
                    isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis)
                    for s in node.body
                ):
                    events.append(DriftEvent(
                        event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_dead_code",
                        drift_dimension="AI_dead_code", baseline_version="0.1.0", state=DriftState.DETECTED,
                        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                        resolution_detail=f"Dead code: class {node.name} body is only pass/... in {fname}"))
        return events

    def detect_ai_broken_logic(self, module_dir: str) -> list[DriftEvent]:
        import ast, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    source = fh.read()
                    tree = ast.parse(source, filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            lines = source.split("\n")
            total_lines = len(lines)
            todo_lines = sum(1 for line in lines if "TODO" in line.upper())
            if total_lines > 0 and todo_lines / total_lines > 0.05:
                evt = DriftEvent(
                    event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_broken_logic",
                    drift_dimension="AI_broken_logic", baseline_version="0.1.0", state=DriftState.DETECTED,
                    created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                    resolution_detail=f"High TODO ratio {todo_lines}/{total_lines} in {fname}")
                events.append(evt)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    arg_count = len(node.args.args)
                    body_count = len(node.body)
                    if arg_count > 5 and body_count < 3:
                        evt = DriftEvent(
                            event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_broken_logic",
                            drift_dimension="AI_broken_logic", baseline_version="0.1.0", state=DriftState.DETECTED,
                            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                            resolution_detail=f"Context truncation: {node.name}({arg_count} args, {body_count} lines) in {fname}")
                        events.append(evt)
        return events

    def detect_ai_duplicate_functionality(self, module_dir: str) -> list[DriftEvent]:
        import ast, hashlib, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        file_funcs: dict[str, list[tuple[str, str, str]]] = {}
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    tree = ast.parse(fh.read(), filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            file_funcs[fname] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body_hash = hashlib.sha256(ast.dump(node, annotate_fields=False).encode()).hexdigest()[:12]
                    file_funcs[fname].append((node.name, body_hash, fname))
        for fname, funcs in file_funcs.items():
            for other_fname, other_funcs in file_funcs.items():
                if fname >= other_fname:
                    continue
                for fn, fh, _ in funcs:
                    for ofn, ofh, _ in other_funcs:
                        if fn == ofn and fh == ofh and fn not in ("__init__", "__repr__", "__str__", "__post_init__"):
                            events.append(DriftEvent(
                                event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_duplicate_functionality",
                                drift_dimension="AI_duplicate_functionality", baseline_version="0.1.0",
                                state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                                updated_at=datetime.now(timezone.utc),
                                resolution_detail=f"Duplicate: {fn}() identical AST in {fname} and {other_fname}"))
        return events

    def detect_ai_session_style_drift(self, module_dir: str) -> list[DriftEvent]:
        import ast, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        has_dataclass = False
        has_direct_init = False
        has_async = False
        has_sync_equivalent = False
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    tree = ast.parse(fh.read(), filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "dataclass":
                            has_dataclass = True
                    if any(isinstance(n, ast.FunctionDef) and n.name == "__init__" for n in node.body):
                        has_direct_init = True
                if isinstance(node, ast.AsyncFunctionDef):
                    has_async = True
                if isinstance(node, ast.FunctionDef):
                    has_sync_equivalent = True
        if has_dataclass and has_direct_init:
            events.append(DriftEvent(
                event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_session_style_drift",
                drift_dimension="AI_style_drift", baseline_version="0.1.0", state=DriftState.DETECTED,
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                resolution_detail="Style drift: dataclass and __init__ mixed"))
        if has_async and has_sync_equivalent:
            events.append(DriftEvent(
                event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_session_style_drift",
                drift_dimension="AI_style_drift", baseline_version="0.1.0", state=DriftState.DETECTED,
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                resolution_detail="Style drift: async/sync mixed"))
        return events

    def detect_ai_knowledge_pollution(self, module_dir: str) -> list[DriftEvent]:
        import ast, os
        events: list[DriftEvent] = []
        if not os.path.isdir(module_dir):
            return events
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            fp = os.path.join(module_dir, fname)
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    source = fh.read()
                    tree = ast.parse(source, filename=fname)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            func_names: set[str] = set()
            class_names: set[str] = set()
            snake_case = 0
            camel_case = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_names.add(node.name)
                    if "_" in node.name and node.name.lower() == node.name:
                        snake_case += 1
                    elif node.name[0].isupper():
                        camel_case += 1
                if isinstance(node, ast.ClassDef):
                    class_names.add(node.name)
            if class_names & func_names:
                common = class_names & func_names
                detail = f"Name collision between class and function: {', '.join(common)} in {fname}"
                events.append(DriftEvent(
                    event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_knowledge_pollution",
                    drift_dimension="AI_knowledge_pollution", baseline_version="0.1.0",
                    state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc), resolution_detail=detail))
            if snake_case > 0 and camel_case > 0:
                detail = f"Naming convention conflict: {snake_case} snake_case + {camel_case} CamelCase funcs in {fname}"
                events.append(DriftEvent(
                    event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="ai_knowledge_pollution",
                    drift_dimension="AI_knowledge_pollution", baseline_version="0.1.0",
                    state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc), resolution_detail=detail))
        return events

    def detect_cross_session_repair_conflict(self, active_events: list[DriftEvent]) -> list[DriftEvent]:
        events: list[DriftEvent] = []
        seen: dict[str, int] = {}
        for evt in active_events:
            key = f"{evt.detector_id}:{evt.drift_dimension}:{evt.resolved_by or 'none'}"
            seen[key] = seen.get(key, 0) + 1
        for key, count in seen.items():
            if count > 1:
                evt = DriftEvent(
                    event_id=uuid.uuid4(), module_id="MOD-INF-023", detector_id="cross_session_repair_conflict",
                    drift_dimension="D5_cross_session_conflict", baseline_version="0.1.0",
                    state=DriftState.DETECTED, created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    resolution_detail=f"Cross-session conflict: {key} repaired by {count} sessions")
                events.append(evt)
        return events


# ── Top-level: Evolution Engine Feedback ─────────────────

def push_to_evolution_engine(result: ScanResult) -> dict[str, object]:
    """Evolution Engine feedback — 3 suggested actions from drift signal."""
    push_data = {
        "source": "drift_engine", "scan_id": str(result.scan_id),
        "drift_velocity_30d": result.total_drift_events,
        "storm_mode_triggered": result.storm_mode_triggered,
        "top_dimensions": {}, "suggested_action": "EVOLVE_BLUEPRINT",
        "pushed_at": datetime.now(timezone.utc).isoformat(),
    }
    dims: dict[str, int] = {}
    for evt in result.events:
        dims[evt.drift_dimension] = dims.get(evt.drift_dimension, 0) + 1
    push_data["top_dimensions"] = dict(sorted(dims.items(), key=lambda x: x[1], reverse=True)[:5])
    if result.storm_mode_triggered:
        push_data["suggested_action"] = "ADD_CONTRACT"
    elif result.total_drift_events > 20:
        push_data["suggested_action"] = "SPLIT_MODULE"
    return push_data


# ── Top-level: Semantic Drift Detection ──────────────────

@dataclass
class SemanticDriftResult:
    dimension: str
    concept: str
    yaml_a_count: int = 0
    yaml_b_count: int = 0
    drift_detected: bool = False
    detail: str = ""


def detect_concept_cardinality(yaml_a_path: str, yaml_b_path: str, key_path: str) -> SemanticDriftResult:
    import yaml
    result = SemanticDriftResult(dimension="D5_semantic", concept=key_path)
    count_a = count_b = 0
    if os.path.exists(yaml_a_path):
        try:
            with open(yaml_a_path, "r", encoding="utf-8") as fh:
                count_a = _count_entries(yaml.safe_load(fh) or {}, key_path)
        except (yaml.YAMLError, OSError): pass
    if os.path.exists(yaml_b_path):
        try:
            with open(yaml_b_path, "r", encoding="utf-8") as fh:
                count_b = _count_entries(yaml.safe_load(fh) or {}, key_path)
        except (yaml.YAMLError, OSError): pass
    result.yaml_a_count, result.yaml_b_count = count_a, count_b
    result.drift_detected = count_a != count_b
    result.detail = f"A:{count_a} vs B:{count_b} at {key_path}"
    return result


def detect_enum_value_sync(yaml_a_path: str, yaml_b_path: str, field_path: str) -> SemanticDriftResult:
    import yaml
    result = SemanticDriftResult(dimension="D5_semantic", concept=f"enum:{field_path}")
    va: set[str] = set()
    vb: set[str] = set()
    if os.path.exists(yaml_a_path):
        try:
            with open(yaml_a_path, "r", encoding="utf-8") as fh:
                v = _get_field(yaml.safe_load(fh) or {}, field_path)
            if isinstance(v, list): va = {str(x) for x in v}
        except (yaml.YAMLError, OSError): pass
    if os.path.exists(yaml_b_path):
        try:
            with open(yaml_b_path, "r", encoding="utf-8") as fh:
                v = _get_field(yaml.safe_load(fh) or {}, field_path)
            if isinstance(v, list): vb = {str(x) for x in v}
        except (yaml.YAMLError, OSError): pass
    result.drift_detected = va != vb
    return result


def detect_ownership_consistency(paths: list[str], owner_field: str = "owner") -> list[SemanticDriftResult]:
    import yaml
    results: list[SemanticDriftResult] = []
    owners: dict[str, str] = {}
    for p in paths:
        if not os.path.exists(p): continue
        try:
            with open(p, "r", encoding="utf-8") as fh:
                ow = str((yaml.safe_load(fh) or {}).get(owner_field, ""))
            if ow and p in owners and owners[p] != ow:
                results.append(SemanticDriftResult(dimension="D5_semantic", concept=owner_field, drift_detected=True, detail=f"{p}: {owners[p]}→{ow}"))
            if ow: owners[p] = ow
        except (yaml.YAMLError, OSError): pass
    return results


def _count_entries(data: dict[str, object], key_path: str) -> int:
    v = _get_field(data, key_path)
    if isinstance(v, (list, dict)): return len(v)
    return 0


def _get_field(data: dict[str, object], path: str) -> Optional[object]:
    c: object = data
    for p in path.split("."):
        if isinstance(c, dict): c = c.get(p)
        else: return None
    return c


# ============================================================================
# §6.3 DB Schema 三方对账漂移检测
# ============================================================================

@dataclass
class DBSchemaDriftResult:
    detector_name: str = "db_schema_drift"
    schema_vs_orm_drifts: list[dict[str, object]] = field(default_factory=list)
    orm_vs_migration_drifts: list[dict[str, object]] = field(default_factory=list)
    index_inconsistencies: list[dict[str, object]] = field(default_factory=list)


def detect_db_schema_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    db_files = list(Path(project_root).rglob("*.db"))
    orm_model_files = list(Path(project_root).rglob("**/models/*.py"))
    migration_dirs = list(Path(project_root).glob("**/migrations"))

    orm_tables: dict[str, set[str]] = {}
    for mf in orm_model_files:
        try:
            content = mf.read_text(encoding="utf-8")
            for match in re.finditer(
                r"class\s+(\w+)\s*\(.*?(?:Model|Base).*?\):",
                content,
                re.DOTALL,
            ):
                class_name = match.group(1)
                pos = match.end()
                depth = 0
                body = ""
                for ch in content[pos:]:
                    body += ch
                    if ch == ":":
                        depth += 1
                    elif ch == "\n" and depth == 0:
                        break
                fields: set[str] = set()
                for fm in re.finditer(
                    r"(\w+)\s*=\s*Column\(|(\w+)\s*:\s*Mapped\[",
                    body,
                ):
                    fname = fm.group(1) or fm.group(2)
                    if fname and not fname.startswith("_"):
                        fields.add(fname)
                orm_tables[class_name.lower()] = fields
        except Exception:
            continue

    for db_file in db_files:
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            db_tables = {row[0].lower() for row in cursor.fetchall()}

            for tbl in db_tables:
                cursor.execute(f"PRAGMA table_info({tbl})")
                db_cols = {row[1].lower() for row in cursor.fetchall()}
                orm_cols = orm_tables.get(tbl, set())
                if orm_cols and db_cols != orm_cols:
                    db_only = db_cols - orm_cols
                    orm_only = orm_cols - db_cols
                    events.append(
                        DriftEvent(
                            event_id=f"drift-db-{tbl}-schema",
                            detector_id="db_schema_drift",
                            severity=Severity.MAJOR,
                            source_file=str(db_file),
                            description=(
                                f"DB table {tbl}: schema mismatch. "
                                f"DB={len(db_cols)} cols, ORM={len(orm_cols)} cols"
                            ),
                            details=(
                                f"DB only: {db_only}, ORM only: {orm_only}"
                            ),
                            timestamp=datetime.now(timezone.utc),
                            state=DriftState.DETECTED,
                            scan_level=ScanLevel.STANDARD,
                            auto_fixable=False,
                        )
                    )

                cursor.execute(f"PRAGMA index_list({tbl})")
                db_indexes = {row[1].lower() for row in cursor.fetchall()}
                for field_name, _field_set in orm_tables.items():
                    if field_name == tbl:
                        pass

            conn.close()
        except Exception:
            continue

    for mdir in migration_dirs:
        try:
            migration_files = sorted(
                mdir.glob("*.py"),
                key=lambda p: p.name,
                reverse=True,
            )
            if migration_files:
                latest = migration_files[0]
                content = latest.read_text(encoding="utf-8")
                for tbl_name in orm_tables:
                    if tbl_name not in content.lower():
                        events.append(
                            DriftEvent(
                                event_id=f"drift-mig-{tbl_name}-missing",
                                detector_id="db_schema_drift",
                                severity=Severity.MAJOR,
                                source_file=str(latest),
                                description=(
                                    f"ORM {tbl_name} missing from "
                                    f"latest migration {latest.name}"
                                ),
                                timestamp=datetime.now(timezone.utc),
                                state=DriftState.DETECTED,
                                scan_level=ScanLevel.STANDARD,
                                auto_fixable=False,
                            )
                        )
        except Exception:
            continue

    return events


# ============================================================================
# §6.4 依赖版本漂移检测
# ============================================================================

@dataclass
class DepVersionDriftResult:
    detector_name: str = "dep_version_drift"
    mismatched_packages: list[dict[str, str]] = field(default_factory=list)
    missing_from_requirements: list[str] = field(default_factory=list)
    extra_in_requirements: list[str] = field(default_factory=list)


def detect_dep_version_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    req_file = Path(project_root) / "requirements.txt"
    if not req_file.exists():
        candidates = list(Path(project_root).glob("**/requirements*.txt"))
        req_file = candidates[0] if candidates else None
        if not req_file:
            return events

    defined: dict[str, str] = {}
    try:
        for line in req_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            match = re.match(
                r"^([a-zA-Z0-9_.-]+)\s*([><=!~]+.+)?", line
            )
            if match:
                pkg = match.group(1).lower().replace("_", "-")
                constraint = match.group(2) or ""
                defined[pkg] = constraint
    except Exception:
        return events

    installed: dict[str, str] = {}
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                pkg, ver = line.split("==", 1)
                installed[pkg.lower().replace("_", "-")] = ver.strip()
    except Exception:
        return events

    for pkg_name, constraint in defined.items():
        if pkg_name not in installed:
            events.append(
                DriftEvent(
                    event_id=f"drift-dep-{pkg_name}-missing",
                    detector_id="dep_version_drift",
                    severity=Severity.MINOR,
                    source_file=str(req_file),
                    description=(
                        f"Package {pkg_name} in requirements.txt "
                        f"but not installed"
                    ),
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=True,
                )
            )
        elif constraint and not constraint.startswith("=="):
            installed_ver = installed[pkg_name]
            events.append(
                DriftEvent(
                    event_id=f"drift-dep-{pkg_name}-version",
                    detector_id="dep_version_drift",
                    severity=Severity.INFO,
                    source_file=str(req_file),
                    description=(
                        f"Package {pkg_name}: expected {constraint}, "
                        f"installed {installed_ver}"
                    ),
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=True,
                    fix_description=(
                        f"Update {pkg_name}>= to match "
                        f"installed {installed_ver}"
                    ),
                )
            )

    for pkg_name in installed:
        if pkg_name not in defined:
            events.append(
                DriftEvent(
                    event_id=f"drift-dep-{pkg_name}-undeclared",
                    detector_id="dep_version_drift",
                    severity=Severity.MAJOR,
                    source_file=str(req_file),
                    description=(
                        f"Package {pkg_name} installed "
                        f"({installed[pkg_name]}) but not in "
                        f"requirements.txt"
                    ),
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=False,
                )
            )

    return events


# ============================================================================
# §6.5 安全策略漂移检测
# ============================================================================

_SECRET_PATTERNS: list[tuple[str, str]] = [
    (
        r"(?i)(?:api[_-]?key|apikey|secret[_-]?key)"
        r'\s*[:=]\s*["\'"][^"\']{8,}["\'"]',
        "API key in code",
    ),
    (
        r'(?i)(?:password|passwd)\s*[:=]\s*["\'"][^"\']+["\'"]',
        "Hardcoded password",
    ),
    (
        r'(?i)(?:token|jwt)\s*[:=]\s*["\'"][A-Za-z0-9._=-]{20,}["\'"]',
        "Hardcoded token",
    ),
    (
        r"(?i)(?:private[_-]?key|-----BEGIN\s+(?:RSA|EC|DSA|OPENSSH)\s+PRIVATE\s+KEY)",
        "Private key in code",
    ),
]


@dataclass
class SecurityPolicyDriftResult:
    detector_name: str = "security_policy_drift"
    input_sanitization_gaps: list[str] = field(default_factory=list)
    auth_middleware_gaps: list[str] = field(default_factory=list)
    secrets_found: list[str] = field(default_factory=list)


_INPUT_SANITIZER_KEYWORDS: list[str] = [
    "sanitize", "validate_input", "escape", "strip_tags",
    "bleach", "html.escape", "markupsafe",
]

_AUTH_KEYWORDS: list[str] = [
    "auth_required", "login_required", "authenticate",
    "get_current_user", "verify_token",
    "depends(get_current_user", "jwt_required",
]


def detect_security_policy_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    py_files = [
        p
        for p in Path(project_root).rglob("*.py")
        if all(
            s not in str(p).lower()
            for s in (
                ".git", "__pycache__", "node_modules",
                ".venv", "venv", "_test", "test_",
            )
        )
    ]

    endpoint_rx = re.compile(
        r"@\w+(?:router|app|route)\."
        r"(?:get|post|put|delete|patch)\("
        r"|def\s+main\s*\(|__name__\s*==\s*['\"]__main__['\"]"
        r"|@click\.\w+",
    )

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        if not endpoint_rx.search(content):
            continue

        content_lower = content.lower()

        has_sanitizer = any(
            kw.lower() in content_lower
            for kw in _INPUT_SANITIZER_KEYWORDS
        )
        if not has_sanitizer and len(content) > 200:
            events.append(
                DriftEvent(
                    event_id=f"drift-sec-{py_file.stem}-no-sanitizer",
                    detector_id="security_policy_drift",
                    severity=Severity.MAJOR,
                    source_file=str(py_file),
                    description=(
                        f"Endpoint detected in {py_file.name} "
                        f"but no input sanitizer found"
                    ),
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.DEEP,
                    auto_fixable=False,
                )
            )

        has_auth = any(
            kw.lower() in content_lower for kw in _AUTH_KEYWORDS
        )
        if not has_auth and len(content) > 300:
            events.append(
                DriftEvent(
                    event_id=f"drift-sec-{py_file.stem}-no-auth",
                    detector_id="security_policy_drift",
                    severity=Severity.CRITICAL,
                    source_file=str(py_file),
                    description=(
                        f"Endpoint detected in {py_file.name} "
                        f"but no auth middleware found"
                    ),
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.DEEP,
                    auto_fixable=False,
                )
            )

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for pattern_rx, desc in _SECRET_PATTERNS:
            compiled = re.compile(pattern_rx)
            matches = list(compiled.finditer(content))
            for match in matches[:5]:
                line_no = content[: match.start()].count("\n") + 1
                events.append(
                    DriftEvent(
                        event_id=(
                            f"drift-sec-secret-"
                            f"{py_file.stem}-L{line_no}"
                        ),
                        detector_id="security_policy_drift",
                        severity=Severity.CRITICAL,
                        source_file=f"{py_file}:{line_no}",
                        description=(
                            f"{desc}: "
                            f"{match.group(0)[:80]}"
                        ),
                        timestamp=datetime.now(timezone.utc),
                        state=DriftState.DETECTED,
                        scan_level=ScanLevel.DEEP,
                        auto_fixable=False,
                    )
                )

    return events


# ============================================================================
# §6.6 文档-代码共演化漂移检测
# ============================================================================

@dataclass
class DocCodeCoevolutionResult:
    detector_name: str = "doc_code_coevolution"
    code_newer_violations: list[str] = field(default_factory=list)
    interface_drifts: list[dict[str, str]] = field(default_factory=list)


def detect_doc_code_coevolution(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    docs_root = Path(project_root) / "docs"
    src_root = Path(project_root) / "src"

    blueprint_files: list[Path] = []
    if docs_root.exists():
        blueprint_files = list(
            Path(project_root).rglob("**/blueprint.md")
        )

    code_files: list[Path] = []
    if src_root.exists():
        code_files = [
            p
            for p in Path(project_root).rglob("*.py")
            if all(
                s not in str(p).lower()
                for s in (".git", "__pycache__", ".venv", "venv")
            )
        ]

    if not blueprint_files:
        return events

    SEVEN_DAYS: float = 7.0 * 86400.0

    for bp in blueprint_files:
        try:
            bp_mtime = bp.stat().st_mtime
            bp_mtime_dt = datetime.fromtimestamp(
                bp_mtime, tz=timezone.utc
            )
        except Exception:
            continue

        bp_dir_parts = list(bp.parent.parts)
        related_code: list[Path] = []
        for cf in code_files:
            cf_parts = list(cf.parent.parts)
            common = sum(
                1
                for a, b in zip(bp_dir_parts, cf_parts)
                if a == b
            )
            if common >= 3:
                related_code.append(cf)

        if not related_code:
            bp_name_key = bp.parent.name.lower().replace(
                "-detector", ""
            ).replace("_", "")
            for cf in code_files:
                if bp_name_key in str(cf).lower():
                    related_code.append(cf)

        for cf in related_code:
            try:
                cf_mtime = cf.stat().st_mtime
                if cf_mtime > bp_mtime + SEVEN_DAYS:
                    cf_mtime_dt = datetime.fromtimestamp(
                        cf_mtime, tz=timezone.utc
                    )
                    events.append(
                        DriftEvent(
                            event_id=(
                                f"drift-doc-{bp.stem}-"
                                f"{cf.stem}-code-newer"
                            ),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(cf),
                            description=(
                                f"Code {cf.name} newer than "
                                f"blueprint {bp.name} >7 days"
                            ),
                            details=(
                                f"Blueprint mtime: "
                                f"{bp_mtime_dt.isoformat()}, "
                                f"Code mtime: "
                                f"{cf_mtime_dt.isoformat()}"
                            ),
                            timestamp=datetime.now(timezone.utc),
                            state=DriftState.DETECTED,
                            scan_level=ScanLevel.STANDARD,
                            auto_fixable=False,
                        )
                    )
            except Exception:
                continue

    _BLUEPRINT_IFACE_ALL_RX: re.Pattern[str] = re.compile(
        r"###\s+§\d+\.\d+\s+(\w+).*?\n(.*?)(?=\n###\s+§|\Z)",
        re.DOTALL,
    )

    for bp in blueprint_files:
        try:
            bp_content = bp.read_text(encoding="utf-8")
        except Exception:
            continue

        sections = _BLUEPRINT_IFACE_ALL_RX.findall(bp_content)
        bp_module_name = bp.parent.name.lower().replace(
            "-detector", ""
        ).replace("_", "")

        for iface_name, iface_body in sections:
            func_matches = re.findall(
                r"`(\w+)\(([^)]*)\)`", iface_body
            )
            for func_name, _func_args in func_matches:
                found_in_code = False
                for cf in code_files:
                    cf_key = str(cf).lower()
                    if bp_module_name in cf_key or bp.stem in cf_key:
                        try:
                            cf_content = cf.read_text(
                                encoding="utf-8"
                            )
                            if f"def {func_name}" in cf_content:
                                found_in_code = True
                                break
                        except Exception:
                            continue

                if not found_in_code:
                    events.append(
                        DriftEvent(
                            event_id=(
                                f"drift-doc-iface-"
                                f"{func_name}-missing"
                            ),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(bp),
                            description=(
                                f"Blueprint interface "
                                f"{func_name}() not found in code"
                            ),
                            timestamp=datetime.now(timezone.utc),
                            state=DriftState.DETECTED,
                            scan_level=ScanLevel.STANDARD,
                            auto_fixable=False,
                        )
                    )

    return events


# ============================================================================
# §6.7 测试覆盖漂移检测
# ============================================================================

@dataclass
class TestCoverageDriftResult:
    detector_name: str = "test_coverage_drift"
    module_coverage_ratio: dict[str, float] = field(default_factory=dict)
    degradation_warnings: list[str] = field(default_factory=list)


def detect_test_coverage_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    src_root = Path(project_root) / "src"
    test_root = Path(project_root) / "tests"

    if not src_root.exists() or not test_root.exists():
        return events

    module_loc: dict[str, int] = {}
    for py_file in src_root.rglob("*.py"):
        if any(
            s in str(py_file).lower()
            for s in ("__pycache__", ".git", ".venv")
        ):
            continue
        try:
            loc = len(py_file.read_text(encoding="utf-8").splitlines())
        except Exception:
            continue
        parts = py_file.relative_to(src_root).parts
        module = parts[0] if len(parts) > 0 else "root"
        module_loc[module] = module_loc.get(module, 0) + loc

    test_loc: dict[str, int] = {}
    for py_file in test_root.rglob("test_*.py"):
        if any(
            s in str(py_file).lower()
            for s in ("__pycache__", ".git", ".venv")
        ):
            continue
        try:
            loc = len(py_file.read_text(encoding="utf-8").splitlines())
        except Exception:
            continue
        parts = py_file.relative_to(test_root).parts
        module = parts[0] if len(parts) > 0 else "root"
        test_loc[module] = test_loc.get(module, 0) + loc

    for module, src_lines in module_loc.items():
        test_lines = test_loc.get(module, 0)
        if src_lines > 50:
            ratio = test_lines / max(src_lines, 1)
            if ratio < 0.3:
                events.append(
                    DriftEvent(
                        event_id=f"drift-test-cov-{module}-low",
                        detector_id="test_coverage_drift",
                        severity=Severity.MAJOR,
                        source_file=str(src_root / module),
                        description=(
                            f"Module {module}: test coverage ratio "
                            f"{ratio:.1%} ({test_lines}T/{src_lines}S)"
                        ),
                        details="Test-to-source ratio below 30% threshold",
                        timestamp=datetime.now(timezone.utc),
                        state=DriftState.DETECTED,
                        scan_level=ScanLevel.STANDARD,
                        auto_fixable=False,
                    )
                )

    return events


# ============================================================================
# §6.10 知识图谱实体化集成
# ============================================================================

@dataclass
class KnowledgeGraphSyncResult:
    detector_name: str = "knowledge_graph_sync"
    entities_created: int = 0
    relations_created: int = 0
    orphans_found: int = 0


def detect_knowledge_graph_sync(
    project_root: str,
    events: list[DriftEvent],
) -> list[DriftEvent]:
    sync_events: list[DriftEvent] = []
    detector_ids: set[str] = set()
    module_ids: set[str] = set()

    for evt in events:
        detector_ids.add(evt.detector_id)
        source_path = Path(evt.source_file)
        parts = source_path.parts
        for i, part in enumerate(parts):
            if part == "src" and i + 1 < len(parts):
                module_ids.add(parts[i + 1])
                break
            if part == "docs" and i + 2 < len(parts):
                module_ids.add(parts[i + 2])
                break

    registry = load_detector_registry()
    registered_ids: set[str] = {d.detector_id for d in registry}

    orphan_detectors = registered_ids - detector_ids
    for orphan_id in orphan_detectors:
        sync_events.append(
            DriftEvent(
                event_id=f"drift-kg-detector-orphan-{orphan_id}",
                detector_id="knowledge_graph_sync",
                severity=Severity.INFO,
                source_file="knowledge_graph",
                description=(
                    f"Detector {orphan_id} registered "
                    f"but never produced an event"
                ),
                details="Candidate for removal or deprioritization",
                timestamp=datetime.now(timezone.utc),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.LIGHT,
                auto_fixable=False,
            )
        )

    co_occurrence: dict[tuple[str, str], int] = {}
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            e1, e2 = events[i], events[j]
            m1 = e1.detector_id
            m2 = e2.detector_id
            if m1 != m2:
                key = (m1, m2) if m1 < m2 else (m2, m1)
                co_occurrence[key] = co_occurrence.get(key, 0) + 1

    for (d1, d2), count in co_occurrence.items():
        if count >= 3:
            sync_events.append(
                DriftEvent(
                    event_id=f"drift-kg-corelation-{d1}-{d2}",
                    detector_id="knowledge_graph_sync",
                    severity=Severity.INFO,
                    source_file="knowledge_graph",
                    description=(
                        f"Detectors {d1} and {d2} "
                        f"co-occurred {count} times"
                    ),
                    details="CORRELATED_WITH candidate for knowledge graph",
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=False,
                )
            )

    return sync_events


# ============================================================================
# §6.12 漂移作为AI训练数据闭环
# ============================================================================

@dataclass
class DriftTrainingPattern:
    pattern_id: str
    detector_id: str
    frequency: int
    dimension: str
    commit_diff_pattern: str
    root_cause_summary: str
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    injected: bool = False
    effectiveness: Optional[float] = None


@dataclass
class AITrainingLoopResult:
    detector_name: str = "ai_training_loop"
    patterns_extracted: int = 0
    patterns_injected: int = 0
    patterns_suppressed: int = 0


def extract_training_patterns(project_root: str, days: int = 30) -> list[DriftTrainingPattern]:
    patterns: list[DriftTrainingPattern] = []
    drift_data_dir = Path(project_root) / "data" / "drift"

    if not drift_data_dir.exists():
        return patterns

    threshold = datetime.now(timezone.utc) - timedelta(days=days)
    dim_freq: dict[str, int] = {}
    dim_events: dict[str, list[dict[str, object]]] = {}

    for json_file in drift_data_dir.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(json_file.stat().st_mtime, tz=timezone.utc)
            if mtime < threshold:
                continue
            data = json.loads(json_file.read_text(encoding="utf-8"))
            events_data = data if isinstance(data, list) else data.get("events", [])
            for evt in events_data:
                dim = str(evt.get("detector_id", "unknown"))
                dim_freq[dim] = dim_freq.get(dim, 0) + 1
                dim_events.setdefault(dim, []).append(evt)
        except Exception:
            continue

    for dim, freq in dim_freq.items():
        if freq >= 3 and dim in dim_events:
            events_sample = dim_events[dim][:10]
            descriptions = [
                str(e.get("description", "")) for e in events_sample
            ]
            root_cause = descriptions[0][:200] if descriptions else "Pattern analysis pending"

            patterns.append(
                DriftTrainingPattern(
                    pattern_id=f"pattern-{dim}-{freq}",
                    detector_id=dim,
                    frequency=freq,
                    dimension=dim,
                    commit_diff_pattern="git diff analysis pending",
                    root_cause_summary=root_cause,
                )
            )

    return patterns


def inject_patterns_to_prompt(
    patterns: list[DriftTrainingPattern],
) -> str:
    lines: list[str] = ["## AI Error-Prone Patterns (from drift training loop)", ""]
    for p in patterns[:5]:
        lines.append(
            f"- **[{p.detector_id}]** freq={p.frequency}: "
            f"{p.root_cause_summary[:150]}"
        )
    lines.append("")
    lines.append(
        f"> These {len(patterns)} patterns were extracted from "
        f"drift events. Avoid repeating them."
    )
    return "\n".join(lines)


def track_training_effectiveness(
    pattern: DriftTrainingPattern,
    post_injection_freq: int,
) -> float:
    if pattern.frequency == 0:
        return 0.0
    reduction = 1.0 - (post_injection_freq / pattern.frequency)
    return max(0.0, reduction)


def detect_ai_training_loop(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    patterns = extract_training_patterns(project_root, days=30)

    if not patterns:
        return events

    for p in patterns:
        events.append(
            DriftEvent(
                event_id=f"drift-train-pattern-{p.pattern_id}",
                detector_id="ai_training_loop",
                severity=Severity.INFO,
                source_file="drift_training_loop",
                description=(
                    f"AI error pattern [{p.detector_id}] "
                    f"recurred {p.frequency} times in 30 days"
                ),
                details=(
                    f"Root cause: {p.root_cause_summary[:200]}. "
                    f"Injected: {p.injected}, "
                    f"Effectiveness: {p.effectiveness or 'untracked'}"
                ),
                timestamp=datetime.now(timezone.utc),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.STANDARD,
                auto_fixable=False,
            )
        )

    injected_count = sum(1 for p in patterns if p.injected)
    if injected_count > 0:
        effective = [
            p
            for p in patterns
            if p.injected
            and p.effectiveness is not None
            and p.effectiveness > 0.5
        ]
        for p in effective:
            events.append(
                DriftEvent(
                    event_id=f"drift-train-suppressed-{p.pattern_id}",
                    detector_id="ai_training_loop",
                    severity=Severity.INFO,
                    source_file="AGENTS.md",
                    description=(
                        f"Pattern {p.pattern_id} suppressed "
                        f"by {p.effectiveness:.0%} after prompt injection"
                    ),
                    details=f"Candidate for permanent inclusion in AGENTS.md",
                    timestamp=datetime.now(timezone.utc),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.STANDARD,
                    auto_fixable=False,
                )
            )

    return events


# ============================================================================
# §6.18 跨语言漂移检测框架
# ============================================================================

LANGUAGE_AGNOSTIC_DIMENSIONS: list[str] = [
    "D5-YAML-DISK",
    "D5-DIRTY-GIT",
    "D5-EVOLUTION",
    "D5-SEMANTIC",
    "D5-SECURITY",
    "D5-DEPENDENCY",
    "D5-TEST-COV",
    "D5-CASCADE",
    "D5-DOC-COEVOL",
]

LANGUAGE_SPECIFIC_INTERFACES: dict[str, list[str]] = {
    "Python": ["parse_python_imports", "parse_python_public_api", "detect_python_dead_code"],
    "TypeScript": [],
    "Go": [],
    "Rust": [],
}


@dataclass
class CrossLanguageConfig:
    enabled_languages: list[str] = field(default_factory=lambda: ["Python"])
    agnostic_dimensions: list[str] = field(default_factory=LANGUAGE_AGNOSTIC_DIMENSIONS.copy)
    fallback_on_unsupported: bool = True


CROSS_LANG_CONFIG = CrossLanguageConfig()


def parse_python_imports(file_path: str) -> list[str]:
    imports: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return imports
    for match in re.finditer(
        r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))",
        content,
        re.MULTILINE,
    ):
        imp = match.group(1) or match.group(2)
        if imp:
            imports.append(imp)
    return imports


def parse_python_public_api(file_path: str) -> list[str]:
    apis: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return apis
    for match in re.finditer(
        r"^def\s+(\w[\w_]*)\s*\(",
        content,
        re.MULTILINE,
    ):
        name = match.group(1)
        if not name.startswith("_"):
            apis.append(name)
    return apis


def detect_python_dead_code(file_path: str) -> list[str]:
    dead: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return dead
    functions = re.findall(
        r"def\s+(\w[\w_]*)\s*\(([^)]*)\)",
        content,
    )
    for func_name, _func_args in functions:
        if func_name.startswith("_"):
            continue
        func_escaped = re.escape(func_name)
        calls = len(re.findall(
            rf"\b{func_escaped}\s*\(",
            content,
        ))
        definition_count = content.count(f"def {func_name}")
        if calls <= definition_count and definition_count == 1:
            dead.append(func_name)
    return dead


LANG_INTERFACE_IMPL: dict[str, object] = {
    "parse_python_imports": parse_python_imports,
    "parse_python_public_api": parse_python_public_api,
    "detect_python_dead_code": detect_python_dead_code,
}


def detect_cross_language_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    src_root = Path(project_root) / "src"

    if not src_root.exists():
        return events

    language_extensions: dict[str, list[str]] = {
        "Python": ["*.py"],
        "TypeScript": ["*.ts", "*.tsx"],
        "Go": ["*.go"],
        "Rust": ["*.rs"],
    }

    for lang in CROSS_LANG_CONFIG.enabled_languages:
        extensions = language_extensions.get(lang, [])
        if not extensions:
            continue

        lang_files: list[Path] = []
        for ext in extensions:
            lang_files.extend(src_root.rglob(ext))

        if not lang_files:
            continue

        events.append(
            DriftEvent(
                event_id=f"drift-crosslang-{lang.lower()}-coverage",
                detector_id="cross_language_drift",
                severity=Severity.INFO,
                source_file=str(src_root),
                description=(
                    f"Cross-language check: {lang} has "
                    f"{len(lang_files)} files, "
                    f"{len(CROSS_LANG_CONFIG.agnostic_dimensions)} "
                    f"agnostic dimensions"
                ),
                details=(
                    f"Language-agnostic dims: "
                    f"{CROSS_LANG_CONFIG.agnostic_dimensions}"
                ),
                timestamp=datetime.now(timezone.utc),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.STANDARD,
                auto_fixable=False,
            )
        )

    return events
