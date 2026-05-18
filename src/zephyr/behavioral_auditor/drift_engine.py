# [BLUEPRINT] MOD-INF-033 | 03_modules/_cross_layer/behavioral-auditor/blueprint.md | §

# [MODULE] zephyr.behavioral_auditor.drift_engine

# [INVARIANTS] 39检测器必须全部执行;不可跳过检测器

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] drift_engine;detector_dispatcher;alert_router

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] DriftError;BaselineError

# [TESTS] tests/behavioral_auditor/

"""
Drift Engine — 编排器核心 (SRC-0030 精简后)





module_id: MOD-INF-023


检测器发现 → 调度 → 汇总 → 写入 + 风暴检测 + Evolution Engine 反馈。


从原 1982 行拆分为：编排器 (本文件) + infrastructure + ai_construction_detectors


+ drift_result_types + drift_training。


对标 blueprint.md §2.1/§2.3/§2.4/§2.6/§2.9/§2.10/§2.11/§2.13/§5.1。"""






from __future__ import annotations





import asyncio


import json


import os


import signal


import sqlite3


import uuid


from datetime import UTC, datetime





import yaml





# 导入 SRC-0031~0034 提取的组件


from .drift_infrastructure import (


    CheckpointWriter,


    RecoveryManager,


    check_large_diff,


    consume_budget,


    declare_maintenance_window,


    get_maintenance_window,


)


from .drift_models import (


    BulkDriftEvent,


    Detector,


    DriftEvent,


    DriftReport,


    DriftState,


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








def load_detector_registry(registry_path: str | None = None) -> list[Detector]:


    if not _REGISTRY_PATH:


        _resolve_paths()


    path = registry_path or _REGISTRY_PATH


    if not path or not os.path.exists(path):


        return []


    with open(path, encoding="utf-8") as fh:


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


        detectors.append(


            Detector(


                id=str(entry.get("id", "")),


                drift_dimension=str(entry.get("drift_dimension", "")),


                severity=Severity(str(entry.get("severity", "MEDIUM"))),


                category=str(entry.get("category", "unknown")),


                script=entry.get("script"),


                method=entry.get("method"),


                status=str(entry.get("status", "active")),


                auto_fixable=bool(entry.get("auto_fixable", False)),


                check_dims=[str(d) for d in entry.get("check_dims", []) or []],


            )


        )








# ── Signal Handling ────────────────────────────────────────








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


        event_id=uuid.uuid4(),


        scan_id=scan_id,


        affected_modules=modules,


        dimension_groups=dims,


        is_expected=is_expected,


        is_unexpected=not is_expected,


        child_event_ids=[e.event_id for e in events],


        created_at=datetime.now(UTC),


    )








def _split_bulk_to_individual(bulk: BulkDriftEvent, events: list[DriftEvent]) -> list[DriftEvent]:


    return [e for e in events if e.event_id in bulk.child_event_ids]








# ── Scan Core ───────────────────────────────────────────────








async def scan(


    level: ScanLevel = ScanLevel.STANDARD,


    scope: list[str] | None = None,


    registry_path: str | None = None,


    commit_message: str = "",


) -> ScanResult:


    _resolve_paths()


    _install_signal_handlers()





    recovery = RecoveryManager.on_startup()


    resume_from: dict[str, object] | None = recovery





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


    scan_start = (


        resume_from.get("scan_start_time", datetime.now(UTC).isoformat())


        if resume_from


        else datetime.now(UTC).isoformat()


    )





    sem = asyncio.Semaphore(_max_parallel(level))


    tasks = [_dispatch_detector_with_checkpoint(d, sem, scan_id, completed, scan_start) for d in filtered]


    results: list[dict[str, object]] = list(await asyncio.gather(*tasks))





    for r in results:


        for evt in r.get("events", []) or []:


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


        scan_id=scan_id,


        detectors_run=len(filtered),


        total_drift_events=len(events),


        new_events=[e.event_id for e in events],


        resolved_events=[],


        storm_mode_triggered=storm_mode,


        events=events,


    )








async def _dispatch_detector_with_checkpoint(


    detector: Detector, sem: asyncio.Semaphore, scan_id: uuid.UUID, completed: list[str], scan_start: str


) -> dict[str, object]:


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








def build_report(result: ScanResult, registry_path: str | None = None) -> DriftReport:


    detectors = load_detector_registry(registry_path)


    health_index: dict[str, float] = {}


    dim_counts: dict[str, int] = {}


    for evt in result.events:


        dim_counts[evt.drift_dimension] = dim_counts.get(evt.drift_dimension, 0) + 1


    for d in detectors:


        if d.drift_dimension:


            health_index[d.drift_dimension] = dim_counts.get(d.drift_dimension, 0)


    top = sorted(dim_counts.items(), key=lambda x: x[1], reverse=True)[:5]


    return DriftReport(


        module_health_index=health_index,


        top_drift_dimensions=top,


        active_drift_count=result.total_drift_events,


        scan_summary=f"Scan {result.scan_id}: {result.detectors_run} detectors run, {result.total_drift_events} drift events",


    )








def _filter_detectors_by_level(detectors: list[Detector], level: ScanLevel, scope: list[str] | None) -> list[Detector]:


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


            proc = await asyncio.create_subprocess_exec(


                "python", script_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE


            )


            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)


            if proc.returncode != 0:


                evt = _create_drift_event(


                    detector, f"Detector failed: {stderr.decode('utf-8', errors='replace')[:200]}"


                )


                return {"detector_id": detector.id, "events": [_event_to_dict(evt)]}


            try:


                output = json.loads(stdout.decode("utf-8"))


            except (json.JSONDecodeError, UnicodeDecodeError):


                return {"detector_id": detector.id, "events": []}


            return {"detector_id": detector.id, "events": output}


        except TimeoutError:


            return {


                "detector_id": detector.id,


                "events": [_event_to_dict(_create_drift_event(detector, "Detector timed out after 30s"))],


            }


        except Exception as exc:


            return {


                "detector_id": detector.id,


                "events": [_event_to_dict(_create_drift_event(detector, f"Detector exception: {exc}"))],


            }








def _create_drift_event(detector: Detector, detail: str) -> DriftEvent:


    return DriftEvent(


        event_id=uuid.uuid4(),


        module_id="MOD-INF-023",


        detector_id=detector.id,


        drift_dimension=detector.drift_dimension,


        baseline_version="0.1.0",


        state=DriftState.DETECTED,


        created_at=datetime.now(UTC),


        updated_at=datetime.now(UTC),


        resolution_detail=detail,


    )








def _event_to_dict(event: DriftEvent) -> dict[str, object]:


    return {


        "event_id": str(event.event_id),


        "module_id": event.module_id,


        "detector_id": event.detector_id,


        "drift_dimension": event.drift_dimension,


        "baseline_version": event.baseline_version,


        "state": event.state.value,


        "created_at": event.created_at.isoformat(),


        "updated_at": event.updated_at.isoformat(),


        "resolved_by": event.resolved_by,


        "resolution_detail": event.resolution_detail,


        "auto_fixed": event.auto_fixed,


        "rollback_verified": event.rollback_verified,


    }








def _parse_event(raw: dict[str, object]) -> DriftEvent:


    return DriftEvent(


        event_id=uuid.UUID(str(raw.get("event_id", str(uuid.uuid4())))),


        module_id=str(raw.get("module_id", "")),


        detector_id=str(raw.get("detector_id", "")),


        drift_dimension=str(raw.get("drift_dimension", "")),


        baseline_version=str(raw.get("baseline_version", "")),


        state=DriftState(str(raw.get("state", "DETECTED"))),


        created_at=datetime.fromisoformat(str(raw.get("created_at", datetime.now(UTC).isoformat()))),


        updated_at=datetime.fromisoformat(str(raw.get("updated_at", datetime.now(UTC).isoformat()))),


        resolved_by=raw.get("resolved_by") if raw.get("resolved_by") else None,


        resolution_detail=raw.get("resolution_detail") if raw.get("resolution_detail") else None,


        auto_fixed=bool(raw.get("auto_fixed", False)),


        rollback_verified=bool(raw.get("rollback_verified", False)),


    )








def _write_drift_events(events: list[DriftEvent], db_path: str | None = None) -> int:


    if not events:


        return 0


    if db_path is None:


        _resolve_paths()


        project_root = os.environ.get(


            "ZEPHYR_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(_ENGINE_ROOT)))


        )


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


                    str(event.event_id),


                    event.detector_id,


                    event.module_id,


                    "MEDIUM",


                    event.state.value,


                    event.drift_dimension,


                    event.created_at.isoformat(),


                    1 if event.auto_fixed else 0,


                    event.resolution_detail,


                    event.created_at.isoformat(),


                    event.updated_at.isoformat(),


                ),


            )


            written += 1


        except Exception:


            pass


    conn.commit()


    conn.close()


    return written








# ── Evolution Engine Feedback ──────────────────────────────








def push_to_evolution_engine(result: ScanResult) -> dict[str, object]:


    """Evolution Engine feedback — 3 suggested actions from drift signal."""


    push_data = {


        "source": "drift_engine",


        "scan_id": str(result.scan_id),


        "drift_velocity_30d": result.total_drift_events,


        "storm_mode_triggered": result.storm_mode_triggered,


        "top_dimensions": {},


        "suggested_action": "EVOLVE_BLUEPRINT",


        "pushed_at": datetime.now(UTC).isoformat(),


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


