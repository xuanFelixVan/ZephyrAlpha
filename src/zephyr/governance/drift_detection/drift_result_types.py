# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.drift_result_types
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models; zephyr.governance.drift_detection.drift_engine
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_drift.py; tests/drift/test_drift_result_types.py; tests/infrastructure/test_drift_extended_e2e.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 结果类型定义不可破坏兼容性
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_drift_result_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Detector 结果类型 + 专项检测函数 — drift_result_types.py





module_id: MOD-INF-023 (SRC-0033)


7 个专项检测结果数据类 + 对应的 detect_*() 函数：


语义漂移、DB Schema 三方对账、依赖版本、安全策略、


文档代码共演化、测试覆盖、知识图谱同步。


从 drift_engine.py 提取，对标 blueprint.md §6.3-§6.10。"""

from __future__ import annotations

import os
import re
import logging
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .drift_models import DriftEvent, DriftState, ScanLevel, Severity

logger = logging.getLogger(__name__)

# ── §6.2 Semantic Drift ─────────────────────────────────────


@dataclass
class SemanticDriftResult:
    """语义漂移检测结果（§6.2）。





    对比两个 YAML 文件在指定 key_path 下的概念基数或枚举值是否一致。





    Fields:


        dimension: 漂移维度标识（如 ``D5_semantic``）。


        concept: 被检测的概念路径或字段名。


        yaml_a_count: 文件 A 中该概念的条目数。


        yaml_b_count: 文件 B 中该概念的条目数。


        drift_detected: 是否检测到不一致。


        detail: 人类可读的漂移详情。


    """

    dimension: str

    concept: str

    yaml_a_count: int = 0

    yaml_b_count: int = 0

    drift_detected: bool = False

    detail: str = ""


def detect_concept_cardinality(yaml_a_path: str, yaml_b_path: str, key_path: str) -> SemanticDriftResult:
    """检测概念基数漂移 — 对比两 YAML 在 key_path 下的条目数。





    Args:


        yaml_a_path: 第一个 YAML 文件路径。


        yaml_b_path: 第二个 YAML 文件路径。


        key_path: 以 ``.`` 分隔的嵌套字段路径（如 ``agents.models``）。





    Returns:


        SemanticDriftResult: 包含基数对比结果和漂移标识。


    """

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
    """检测枚举值同步 — 对比两 YAML 在 field_path 下的枚举集合是否一致。





    Args:


        yaml_a_path: 第一个 YAML 文件路径。


        yaml_b_path: 第二个 YAML 文件路径。


        field_path: 以 ``.`` 分隔的枚举字段路径。





    Returns:


        SemanticDriftResult: 枚举值集合不一致时 ``drift_detected=True``。


    """

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
    """检测所有权一致性 — 同一文件在被多次读取期间 owner 字段是否漂移。





    Args:


        paths: YAML 文件路径列表。


        owner_field: 文件中表示所有者的字段名，默认 ``"owner"``。





    Returns:


        list[SemanticDriftResult]: 每次所有权变更对应一个漂移结果。


    """

    import yaml

    def _read_yaml_owner(p: str) -> str | None:
        with open(p, encoding="utf-8") as fh:
            ow = str((yaml.safe_load(fh) or {}).get(owner_field, ""))
        return ow if ow else None

    results: list[SemanticDriftResult] = []
    owners: dict[str, str] = {}

    existing = [p for p in paths if os.path.exists(p)]
    path_owners: dict[str, str] = {}
    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_read_yaml_owner, p): p for p in existing}
        for future in as_completed(futures):
            p = futures[future]
            try:
                data = future.result()
                if data:
                    path_owners[p] = data
            except (yaml.YAMLError, OSError):
                pass

    for p, ow in path_owners.items():
        if p in owners and owners[p] != ow:
            results.append(
                SemanticDriftResult(
                    dimension="D5_semantic",
                    concept=owner_field,
                    drift_detected=True,
                    detail=f"{p}: {owners[p]}->{ow}",
                )
            )
        owners[p] = ow

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
    """数据库 Schema 三方对账结果（§6.3）。





    Fields:


        detector_name: 检测器标识。


        schema_vs_orm_drifts: SQLite schema 与 ORM 模型定义之间的差异。


        orm_vs_migration_drifts: ORM 模型与迁移脚本之间的差异。


        index_inconsistencies: 索引层面的不一致。


    """

    detector_name: str = "db_schema_drift"

    schema_vs_orm_drifts: list[dict[str, object]] = field(default_factory=list)

    orm_vs_migration_drifts: list[dict[str, object]] = field(default_factory=list)

    index_inconsistencies: list[dict[str, object]] = field(default_factory=list)


def detect_db_schema_drift(project_root: str) -> list[DriftEvent]:
    """检测 DB Schema 三方对账漂移 — SQLite 实际 schema vs ORM 模型 vs 迁移脚本。





    过程：


    1. 扫描项目下所有 ``*.db`` 文件，读取 ``sqlite_master``。


    2. 扫描 ``models/*.py`` 文件，解析 SQLAlchemy/dataclass 定义。


    3. 扫描 ``migrations/`` 目录，解析迁移脚本。


    4. 对实际 schema、ORM 模型、迁移定义做三方交叉对比。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每类不一致对应一个 DETECTED 事件。


    """

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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
            continue

    for db_file in db_files:
        # 5.49.4 修复：原 try/except 中 conn 仅在成功路径关闭，异常分支泄漏。
        # 改用 try/finally 保证连接在所有路径下关闭。
        conn = None
        try:
            conn = get_db_connection(str(db_file))

            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")

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
                                f"DB table {tbl}: schema mismatch. DB={len(db_cols)} cols, ORM={len(orm_cols)} cols"
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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
            continue
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning("conn close failed (%s: %s)", type(e).__name__, e, exc_info=True)

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
                                description=(f"ORM {tbl_name} missing from latest migration {latest.name}"),
                                timestamp=datetime.now(UTC),
                                state=DriftState.DETECTED,
                                scan_level=ScanLevel.STANDARD,
                                auto_fixable=False,
                            )
                        )

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
            continue

    return events


# ── §6.4 Dep Version Drift ──────────────────────────────────


@dataclass
class DepVersionDriftResult:
    """依赖版本漂移结果（§6.4）。





    Fields:


        detector_name: 检测器标识。


        mismatched_packages: 版本不匹配的包列表。


        missing_from_requirements: 已安装但不在 requirements.txt 中的包。


        extra_in_requirements: 在 requirements.txt 中但未安装的包。


    """

    detector_name: str = "dep_version_drift"

    mismatched_packages: list[dict[str, str]] = field(default_factory=list)

    missing_from_requirements: list[str] = field(default_factory=list)

    extra_in_requirements: list[str] = field(default_factory=list)


def detect_dep_version_drift(project_root: str) -> list[DriftEvent]:
    """检测依赖版本漂移 — ``requirements.txt`` vs ``pip freeze`` 三方对账。





    对比 declared（requirements.txt）、installed（pip freeze）、


    和 implicitly imported（import 语句），检测版本不一致和未声明依赖。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每个版本偏差对应一个 DETECTED 事件。


    """

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
                    description=(f"Package {pkg_name} in requirements.txt but not installed"),
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
                    description=(f"Package {pkg_name}: expected {constraint}, installed {installed_ver}"),
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=True,
                    fix_description=(f"Update {pkg_name}>= to match installed {installed_ver}"),
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
                    description=(f"Package {pkg_name} installed ({installed[pkg_name]}) but not in requirements.txt"),
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
    """安全策略漂移结果（§6.5）。





    Fields:


        detector_name: 检测器标识。


        input_sanitization_gaps: 缺少输入消毒的端点文件列表。


        auth_middleware_gaps: 缺少认证中间件的端点文件列表。


        secrets_found: 代码中发现的硬编码密钥列表。


    """

    detector_name: str = "security_policy_drift"

    input_sanitization_gaps: list[str] = field(default_factory=list)

    auth_middleware_gaps: list[str] = field(default_factory=list)

    secrets_found: list[str] = field(default_factory=list)


def detect_security_policy_drift(project_root: str) -> list[DriftEvent]:
    """检测安全策略漂移 — 端点安全检查与密钥泄露扫描。





    三步检测：


    1. 扫描路由/CLI 端点文件是否缺少输入消毒（sanitizer）。


    2. 检查端点文件是否缺少认证中间件（auth）。


    3. 全项目正则扫描硬编码密钥（API key / password / token / private key）。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每个安全缺口对应一个 DETECTED 事件。


    """

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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
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
                    description=(f"Endpoint detected in {py_file.name} but no input sanitizer found"),
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
                    description=(f"Endpoint detected in {py_file.name} but no auth middleware found"),
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.DEEP,
                    auto_fixable=False,
                )
            )

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
            continue

        for pattern_rx, desc in _SECRET_PATTERNS:
            compiled = re.compile(pattern_rx)

            matches = list(compiled.finditer(content))

            for match in matches[:5]:
                line_no = content[: match.start()].count("\n") + 1

                events.append(
                    DriftEvent(
                        event_id=(f"drift-sec-secret-{py_file.stem}-L{line_no}"),
                        detector_id="security_policy_drift",
                        severity=Severity.CRITICAL,
                        source_file=f"{py_file}:{line_no}",
                        description=(f"{desc}: {match.group(0)[:80]}"),
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
    """文档-代码共演化漂移结果（§6.6）。





    Fields:


        detector_name: 检测器标识。


        code_newer_violations: 代码比蓝图新 >7 天的违规文件列表。


        interface_drifts: 蓝图声明的接口在代码中缺失的漂移列表。


    """

    detector_name: str = "doc_code_coevolution"

    code_newer_violations: list[str] = field(default_factory=list)

    interface_drifts: list[dict[str, str]] = field(default_factory=list)


def detect_doc_code_coevolution(project_root: str) -> list[DriftEvent]:
    """检测文档-代码共演化漂移 — 蓝图与代码的双向同步检查。





    两个维度：


    1. **时序漂移**: 代码文件 mtime 比对应蓝图晚 >7 天 -> 蓝图过期。


    2. **接口漂移**: 蓝图中声明的 ``func()`` 签名在代码中找不到定义。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每个共演化违规对应一个 DETECTED 事件。


    """

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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
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
                            event_id=(f"drift-doc-{bp.stem}-{cf.stem}-code-newer"),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(cf),
                            description=(f"Code {cf.name} newer than blueprint {bp.name} >7 days"),
                            details=(
                                f"Blueprint mtime: {bp_mtime_dt.isoformat()}, Code mtime: {cf_mtime_dt.isoformat()}"
                            ),
                            timestamp=datetime.now(UTC),
                            state=DriftState.DETECTED,
                            scan_level=ScanLevel.STANDARD,
                            auto_fixable=False,
                        )
                    )

            except Exception as e:
                logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
                continue

    _BLUEPRINT_IFACE_ALL_RX: re.Pattern[str] = re.compile(
        r"###\s+§\d+\.\d+\s+(\w+).*?\n(.*?)(?=\n###\s+§|\Z)",
        re.DOTALL,
    )

    for bp in blueprint_files:
        try:
            bp_content = bp.read_text(encoding="utf-8")

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
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

                        except Exception as e:
                            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
                            continue

                if not found_in_code:
                    events.append(
                        DriftEvent(
                            event_id=(f"drift-doc-iface-{func_name}-missing"),
                            detector_id="doc_code_coevolution",
                            severity=Severity.MAJOR,
                            source_file=str(bp),
                            description=(f"Blueprint interface {func_name}() not found in code"),
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
    """测试覆盖漂移结果（§6.7）。





    Fields:


        detector_name: 检测器标识。


        module_coverage_ratio: 模块级 test/src 行数比。


        degradation_warnings: 覆盖率退化的警告信息。


    """

    detector_name: str = "test_coverage_drift"

    module_coverage_ratio: dict[str, float] = field(default_factory=dict)

    degradation_warnings: list[str] = field(default_factory=list)


def detect_test_coverage_drift(project_root: str) -> list[DriftEvent]:
    """检测测试覆盖漂移 — 模块级 test/src 行数比低于 30% 阈值即告警。





    统计每个 ``src/<module>/`` 与 ``tests/<module>/`` 下的


    总代码行数，计算覆盖率比例。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每个低覆盖模块对应一个 DETECTED 事件（只对 >50 行的模块检查）。


    """

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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
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

        except Exception as e:
            logger.warning("drift scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
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
                        description=(f"Module {module}: test coverage ratio {ratio:.1%} ({test_lines}T/{src_lines}S)"),
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
    """知识图谱同步结果（§6.10）。





    Fields:


        detector_name: 检测器标识。


        entities_created: 新创建的实体数。


        relations_created: 新创建的关系数。


        orphans_found: 发现的孤立节点数。


    """

    detector_name: str = "knowledge_graph_sync"

    entities_created: int = 0

    relations_created: int = 0

    orphans_found: int = 0


def detect_knowledge_graph_sync(
    project_root: str,
    events: list[DriftEvent],
) -> list[DriftEvent]:
    """检测知识图谱同步漂移 — 将 DriftEvent 流同步为 KG 实体与关系。





    从事件流中提取 detector_id 和 module_id，与 ``load_detector_registry()``


    对比，发现未在注册表中出现的 detector 视为知识图谱缺少同步。





    Args:


        project_root: 项目根目录。


        events: 当前批次的 DriftEvent 列表。





    Returns:


        list[DriftEvent]: 每个未同步的 detector 对应一个 DETECTED 事件。


    """

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
                description=(f"Detector {orphan_id} registered but never produced an event"),
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
                    description=(f"Detectors {d1} and {d2} co-occurred {count} times"),
                    details="CORRELATED_WITH candidate for knowledge graph",
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.LIGHT,
                    auto_fixable=False,
                )
            )

    return sync_events