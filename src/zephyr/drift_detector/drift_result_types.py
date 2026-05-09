"""
Drift Detector 结果类型 + 专项检测函数 — drift_result_types.py

module_id: MOD-INF-023 (SRC-0033)
7 个专项检测结果数据类 + 对应的 detect_*() 函数：
语义漂移、DB Schema 三方对账、依赖版本、安全策略、
文档代码共演化、测试覆盖、知识图谱同步。
从 drift_engine.py 提取，对标 blueprint.md §6.3-§6.10。
"""

from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .drift_models import DriftEvent, DriftState, ScanLevel, Severity

# ── §6.2 Semantic Drift ─────────────────────────────────────


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
            with open(yaml_a_path, encoding="utf-8") as fh:
                count_a = _count_entries(yaml.safe_load(fh) or {}, key_path)
        except (yaml.YAMLError, OSError):
            pass
    if os.path.exists(yaml_b_path):
        try:
            with open(yaml_b_path, encoding="utf-8") as fh:
                count_b = _count_entries(yaml.safe_load(fh) or {}, key_path)
        except (yaml.YAMLError, OSError):
            pass
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
            with open(yaml_a_path, encoding="utf-8") as fh:
                v = _get_field(yaml.safe_load(fh) or {}, field_path)
            if isinstance(v, list):
                va = {str(x) for x in v}
        except (yaml.YAMLError, OSError):
            pass
    if os.path.exists(yaml_b_path):
        try:
            with open(yaml_b_path, encoding="utf-8") as fh:
                v = _get_field(yaml.safe_load(fh) or {}, field_path)
            if isinstance(v, list):
                vb = {str(x) for x in v}
        except (yaml.YAMLError, OSError):
            pass
    result.drift_detected = va != vb
    return result


def detect_ownership_consistency(paths: list[str], owner_field: str = "owner") -> list[SemanticDriftResult]:
    import yaml

    results: list[SemanticDriftResult] = []
    owners: dict[str, str] = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                ow = str((yaml.safe_load(fh) or {}).get(owner_field, ""))
            if ow and p in owners and owners[p] != ow:
                results.append(
                    SemanticDriftResult(
                        dimension="D5_semantic",
                        concept=owner_field,
                        drift_detected=True,
                        detail=f"{p}: {owners[p]}→{ow}",
                    )
                )
            if ow:
                owners[p] = ow
        except (yaml.YAMLError, OSError):
            pass
    return results


def _count_entries(data: dict[str, object], key_path: str) -> int:
    v = _get_field(data, key_path)
    if isinstance(v, (list, dict)):
        return len(v)
    return 0


def _get_field(data: dict[str, object], path: str) -> object | None:
    c: object = data
    for p in path.split("."):
        if isinstance(c, dict):
            c = c.get(p)
        else:
            return None
    return c


# ── §6.3 DB Schema Drift ─────────────────────────────────────


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
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' " "AND name NOT LIKE 'sqlite_%'")
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
                                f"DB table {tbl}: schema mismatch. " f"DB={len(db_cols)} cols, ORM={len(orm_cols)} cols"
                            ),
                            details=(f"DB only: {db_only}, ORM only: {orm_only}"),
                            timestamp=datetime.now(UTC),
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
                                description=(f"ORM {tbl_name} missing from " f"latest migration {latest.name}"),
                                timestamp=datetime.now(UTC),
                                state=DriftState.DETECTED,
                                scan_level=ScanLevel.STANDARD,
                                auto_fixable=False,
                            )
                        )
        except Exception:
            continue

    return events


# ── §6.4 Dep Version Drift ──────────────────────────────────


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
            match = re.match(r"^([a-zA-Z0-9_.-]+)\s*([><=!~]+.+)?", line)
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
                    description=(f"Package {pkg_name} in requirements.txt " f"but not installed"),
                    timestamp=datetime.now(UTC),
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
                    description=(f"Package {pkg_name}: expected {constraint}, " f"installed {installed_ver}"),
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=True,
                    fix_description=(f"Update {pkg_name}>= to match " f"installed {installed_ver}"),
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
                        f"Package {pkg_name} installed " f"({installed[pkg_name]}) but not in " f"requirements.txt"
                    ),
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=False,
                )
            )

    return events


# ── §6.5 Security Policy Drift ──────────────────────────────

_SECRET_PATTERNS: list[tuple[str, str]] = [
    (
        r"(?i)(?:api[_-]?key|apikey|secret[_-]?key)" r'\s*[:=]\s*["\'"][^"\']{8,}["\'"]',
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

_INPUT_SANITIZER_KEYWORDS: list[str] = [
    "sanitize",
    "validate_input",
    "escape",
    "strip_tags",
    "bleach",
    "html.escape",
    "markupsafe",
]

_AUTH_KEYWORDS: list[str] = [
    "auth_required",
    "login_required",
    "authenticate",
    "get_current_user",
    "verify_token",
    "depends(get_current_user",
    "jwt_required",
]


@dataclass
class SecurityPolicyDriftResult:
    detector_name: str = "security_policy_drift"
    input_sanitization_gaps: list[str] = field(default_factory=list)
    auth_middleware_gaps: list[str] = field(default_factory=list)
    secrets_found: list[str] = field(default_factory=list)


def detect_security_policy_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    py_files = [
        p
        for p in Path(project_root).rglob("*.py")
        if all(
            s not in str(p).lower()
            for s in (
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
                "_test",
                "test_",
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

        has_sanitizer = any(kw.lower() in content_lower for kw in _INPUT_SANITIZER_KEYWORDS)
        if not has_sanitizer and len(content) > 200:
            events.append(
                DriftEvent(
                    event_id=f"drift-sec-{py_file.stem}-no-sanitizer",
                    detector_id="security_policy_drift",
                    severity=Severity.MAJOR,
                    source_file=str(py_file),
                    description=(f"Endpoint detected in {py_file.name} " f"but no input sanitizer found"),
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.DEEP,
                    auto_fixable=False,
                )
            )

        has_auth = any(kw.lower() in content_lower for kw in _AUTH_KEYWORDS)
        if not has_auth and len(content) > 300:
            events.append(
                DriftEvent(
                    event_id=f"drift-sec-{py_file.stem}-no-auth",
                    detector_id="security_policy_drift",
                    severity=Severity.CRITICAL,
                    source_file=str(py_file),
                    description=(f"Endpoint detected in {py_file.name} " f"but no auth middleware found"),
                    timestamp=datetime.now(UTC),
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
                        event_id=(f"drift-sec-secret-" f"{py_file.stem}-L{line_no}"),
                        detector_id="security_policy_drift",
                        severity=Severity.CRITICAL,
                        source_file=f"{py_file}:{line_no}",
                        description=(f"{desc}: " f"{match.group(0)[:80]}"),
                        timestamp=datetime.now(UTC),
                        state=DriftState.DETECTED,
                        scan_level=ScanLevel.DEEP,
                        auto_fixable=False,
                    )
                )

    return events


# ── §6.6 Doc-Code Coevolution Drift ────────────────────────


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
        blueprint_files = list(Path(project_root).rglob("**/blueprint.md"))

    code_files: list[Path] = []
    if src_root.exists():
        code_files = [
            p
            for p in Path(project_root).rglob("*.py")
            if all(s not in str(p).lower() for s in (".git", "__pycache__", ".venv", "venv"))
        ]

    if not blueprint_files:
        return events

    SEVEN_DAYS: float = 7.0 * 86400.0

    for bp in blueprint_files:
        try:
            bp_mtime = bp.stat().st_mtime
            bp_mtime_dt = datetime.fromtimestamp(bp_mtime, tz=UTC)
        except Exception:
            continue

        bp_dir_parts = list(bp.parent.parts)
        related_code: list[Path] = []
        for cf in code_files:
            cf_parts = list(cf.parent.parts)
            common = sum(1 for a, b in zip(bp_dir_parts, cf_parts, strict=False) if a == b)
            if common >= 3:
                related_code.append(cf)

        if not related_code:
            bp_name_key = bp.parent.name.lower().replace("-detector", "").replace("_", "")
            for cf in code_files:
                if bp_name_key in str(cf).lower():
                    related_code.append(cf)

        for cf in related_code:
            try:
                cf_mtime = cf.stat().st_mtime
                if cf_mtime > bp_mtime + SEVEN_DAYS:
                    cf_mtime_dt = datetime.fromtimestamp(cf_mtime, tz=UTC)
                    events.append(
                        DriftEvent(
                            event_id=(f"drift-doc-{bp.stem}-" f"{cf.stem}-code-newer"),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(cf),
                            description=(f"Code {cf.name} newer than " f"blueprint {bp.name} >7 days"),
                            details=(
                                f"Blueprint mtime: "
                                f"{bp_mtime_dt.isoformat()}, "
                                f"Code mtime: "
                                f"{cf_mtime_dt.isoformat()}"
                            ),
                            timestamp=datetime.now(UTC),
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
        bp_module_name = bp.parent.name.lower().replace("-detector", "").replace("_", "")

        for iface_name, iface_body in sections:
            func_matches = re.findall(r"`(\w+)\(([^)]*)\)`", iface_body)
            for func_name, _func_args in func_matches:
                found_in_code = False
                for cf in code_files:
                    cf_key = str(cf).lower()
                    if bp_module_name in cf_key or bp.stem in cf_key:
                        try:
                            cf_content = cf.read_text(encoding="utf-8")
                            if f"def {func_name}" in cf_content:
                                found_in_code = True
                                break
                        except Exception:
                            continue

                if not found_in_code:
                    events.append(
                        DriftEvent(
                            event_id=(f"drift-doc-iface-" f"{func_name}-missing"),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(bp),
                            description=(f"Blueprint interface " f"{func_name}() not found in code"),
                            timestamp=datetime.now(UTC),
                            state=DriftState.DETECTED,
                            scan_level=ScanLevel.STANDARD,
                            auto_fixable=False,
                        )
                    )

    return events


# ── §6.7 Test Coverage Drift ────────────────────────────────


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
        if any(s in str(py_file).lower() for s in ("__pycache__", ".git", ".venv")):
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
        if any(s in str(py_file).lower() for s in ("__pycache__", ".git", ".venv")):
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
                            f"Module {module}: test coverage ratio " f"{ratio:.1%} ({test_lines}T/{src_lines}S)"
                        ),
                        details="Test-to-source ratio below 30% threshold",
                        timestamp=datetime.now(UTC),
                        state=DriftState.DETECTED,
                        scan_level=ScanLevel.STANDARD,
                        auto_fixable=False,
                    )
                )

    return events


# ── §6.10 Knowledge Graph Sync ──────────────────────────────


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
    # NOTE: load_detector_registry is imported lazily to avoid circular import
    from .drift_engine import load_detector_registry

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
                description=(f"Detector {orphan_id} registered " f"but never produced an event"),
                details="Candidate for removal or deprioritization",
                timestamp=datetime.now(UTC),
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
                    description=(f"Detectors {d1} and {d2} " f"co-occurred {count} times"),
                    details="CORRELATED_WITH candidate for knowledge graph",
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=False,
                )
            )

    return sync_events
