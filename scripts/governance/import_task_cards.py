"""
import_task_cards.py — .md 任务卡批量导入 SQLite 任务数据库

依据：ADR-0030（SQLite 元数据层）+ ADR-0040（Pydantic V2 契约）
      MOD-INF-006 §5.2-§5.5（状态机 + 门禁）

用法：
    python scripts/governance/import_task_cards.py <source_dir> [--dry-run] [--force]

    --dry-run   解析 + 校验，不写入 DB
    --force     强制覆盖已存在的任务（默认增量模式：跳过已有）

注意：正常路径下任务卡应由 BlueprintDecomposer 生成（参见 task-system/blueprint.md RULE-ZERO-TASK）。
      本脚本仅用于回填 / 迁移场景。
"""

from __future__ import annotations
from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS


import argparse
import sys
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.schema.schemas import (
    TaskStatus,
    Priority,
    TaskNamespace,
    ExecutionModel,
    SafetyLevel,
    Classification,
    EvolutionPolicy,
)
from zephyr.core.models import TaskCard
from zephyr.db.task_repo import TaskRepository
from zephyr.db.sqlite_schema import init_db

try:
    from zephyr.shared.path_resolver import PathResolver
    _HAS_PATH_RESOLVER = True
except ImportError:
    _HAS_PATH_RESOLVER = False

_CST = timezone(timedelta(hours=8))

_PHASE_MAP = {
    "phase_0": 0,
    "phase_0_foundation": 0,
    "phase_1_scaffold": 1,
    "phase_1a_scaffold": 1,
    "phase_1_partial": 1,
    "phase_2_harden": 2,
    "phase_2": 2,
}

_MODEL_MAP = {
    "deepseek": ExecutionModel.deepseek,
    "glm": ExecutionModel.glm,
    "claude": ExecutionModel.claude,
    "kimi": ExecutionModel.kimi,
    "qwen": ExecutionModel.qwen,
}


def _parse_frontmatter(filepath: Path) -> dict:
    """_parse_frontmatter implementation."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError(f"无有效 YAML frontmatter（需要 --- 包围的 YAML 块）")

    raw_yaml = parts[1]
    raw_yaml = raw_yaml.replace("\\", "/")
    return yaml.safe_load(raw_yaml) or {}


def _to_task_status(raw: str) -> TaskStatus:
    """_to_task_status implementation."""
    upper = raw.strip().upper()
    if upper in ("CREATED",):
        return TaskStatus.PENDING
    if upper in ("DONE", "CLOSED", "COMPLETED"):
        return TaskStatus.COMPLETED
    return TaskStatus(upper)


def _to_priority(raw: str) -> Priority:
    """_to_priority implementation."""
    return Priority(raw.strip().upper())


def _to_execution_model(raw: str) -> ExecutionModel:
    """_to_execution_model implementation."""
    return _MODEL_MAP.get(raw.strip().lower(), ExecutionModel.deepseek)


def _to_phase(raw) -> int:
    """_to_phase implementation."""
    if raw is None:
        return EXIT_FINDINGS
    if isinstance(raw, int):
        return max(0, min(raw, 9))
    return _PHASE_MAP.get(str(raw).strip().lower(), 1)


def _parse_datetime(raw: str) -> datetime:
    """_parse_datetime implementation."""
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_CST)
    return dt


def _build_taskcard(fm: dict, seq: int) -> TaskCard:
    """_build_taskcard 实现：从 YAML frontmatter 构造完整 TaskCard。"""
    title = fm.get("title", "Untitled")
    status = _to_task_status(fm.get("status", "pending"))
    priority = _to_priority(fm.get("priority", "P2"))
    phase = _to_phase(fm.get("phase"))
    execution_model = _to_execution_model(fm.get("assigned_model", "deepseek"))

    created_raw = fm.get("created_at")
    now = datetime.now(timezone.utc)
    created_at = _parse_datetime(str(created_raw)) if created_raw else now

    upstream = _to_str_list(fm.get("upstream_files", []))
    downstream = fm.get("downstream_outputs") or []
    if isinstance(downstream, str):
        downstream = [downstream]
    deliverables: list[str] = []
    downstream_dicts: list[dict] = []
    if isinstance(downstream, list):
        for item in downstream:
            if isinstance(item, dict):
                deliverables.append(item.get("path", item.get("description", str(item))))
                downstream_dicts.append(item)
            else:
                deliverables.append(str(item))
                downstream_dicts.append({"path": str(item), "description": ""})

    acceptance = _to_str_list(fm.get("acceptance_criteria") or fm.get("acceptance", []))
    depends_on = _to_str_list(fm.get("dependencies") or fm.get("depends_on", []))
    allowed_touch = _to_str_list(fm.get("allowed_touch", []))
    forbidden_touch = _to_str_list(fm.get("forbidden_touch", []))
    applicable_rules = fm.get("applicable_rules") or []
    context_assembly = fm.get("context_assembly_manifest") or []
    rolled = fm.get("rollback_instructions", "")
    pipeline = fm.get("assigned_pipeline", "A")
    pipeline_mods = _to_str_list(fm.get("pipeline_modules", []))
    blocked_by = _to_str_list(fm.get("blocked_by", []))
    artifact_paths = _to_str_list(fm.get("artifact_paths", []))
    autonomy = fm.get("ai_autonomy_level", "supervised")
    est_hours = float(fm.get("estimate_hours", "0.0")) if fm.get("estimate_hours") else 0.0
    est_tokens = int(fm.get("estimated_tokens", "8000")) if fm.get("estimated_tokens", "8000") else 8000
    timeout_minutes = int(fm.get("timeout_minutes", "30")) if fm.get("timeout_minutes", "30") else 30
    source_blueprint = fm.get("source_blueprint", "unknown")
    source_section = fm.get("source_section", "unknown")
    description = fm.get("description", title)
    files_in_scope = _to_str_list(fm.get("files_in_scope", []))

    tags = _merge_import_tags(fm)

    original_task_id = fm.get("task_id", "")
    if original_task_id:
        tags.append(f"orig:{original_task_id}")

    safety_str = fm.get("safety_level", "M")
    safety_level = SafetyLevel.M
    try:
        safety_level = SafetyLevel(safety_str.upper())
    except ValueError:
        pass

    classification_str = fm.get("classification", "internal")
    classification = Classification.INTERNAL
    try:
        classification = Classification(classification_str.upper())
    except ValueError:
        pass

    evolution_str = fm.get("evolution_policy", "extendable")
    evolution_policy = EvolutionPolicy.EXTENDABLE
    try:
        evolution_policy = EvolutionPolicy(evolution_str.upper())
    except ValueError:
        pass

    task_id = f"SRC-{seq:04d}"

    return TaskCard(
        task_id=task_id,
        namespace=TaskNamespace.SRC,
        seq=seq,
        title=title,
        status=status,
        priority=priority,
        phase=phase,
        execution_model=execution_model,
        safety_level=safety_level,
        classification=classification,
        evolution_policy=evolution_policy,
        estimate_hours=est_hours,
        source_blueprint=source_blueprint,
        source_section=source_section,
        description=description,
        files_in_scope=files_in_scope,
        deliverables=deliverables,
        acceptance=acceptance,
        depends_on=depends_on,
        tags=tags,
        upstream_files=upstream,
        downstream_outputs=downstream_dicts,
        allowed_touch=allowed_touch,
        forbidden_touch=forbidden_touch,
        applicable_rules=applicable_rules,
        context_assembly_manifest=context_assembly,
        rollback_instructions=str(rolled),
        estimated_tokens=est_tokens,
        timeout_minutes=timeout_minutes,
        blocked_by=blocked_by,
        assigned_pipeline=str(pipeline),
        pipeline_modules=pipeline_mods,
        artifact_paths=artifact_paths,
        ai_autonomy_level=str(autonomy),
        created_at=created_at,
        updated_at=created_at,
    )


def _to_str_list(value) -> list[str]:
    """_to_str_list implementation."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _merge_import_tags(fm: dict) -> list[str]:
    """_merge_import_tags implementation."""
    tags: list[str] = []
    raw_tags = fm.get("tags") or []
    if isinstance(raw_tags, str):
        raw_tags = [raw_tags]
    tags.extend(str(t) for t in raw_tags)
    for t in (fm.get("tags_fn") or []):
        if t:
            tags.append(f"fn:{t}")
    ly = fm.get("tags_ly", "")
    if ly:
        tags.append(f"ly:{ly}")
    md = fm.get("tags_md", "")
    if md:
        tags.append(f"md:{md}")
    stm = fm.get("tags_st", "")
    if stm:
        tags.append(f"st:{stm}")
    for t in (fm.get("tags_mo") or []):
        if t:
            tags.append(f"mo:{t}")
    module_id = fm.get("module_id", "")
    if module_id:
        tags.append(f"module:{module_id}")
    return tags


def _validate_taskcard(tc: TaskCard) -> list[str]:
    """_validate_taskcard implementation."""
    errors: list[str] = []
    try:
        TaskCard.model_validate(tc.model_dump())
    except Exception as e:
        errors.append(f"Pydantic 校验失败: {e}")
    return errors


def _validate_paths(tc: TaskCard, project_root: str = None) -> dict:
    """用 PathResolver 校验任务卡的 downstream 路径。返回 {drifted, variants, missing, details}"""
    if not _HAS_PATH_RESOLVER:
        return {"error": "PathResolver 不可用", "drifted": 0, "variants": 0, "missing": 0, "details": []}

    if project_root is None:
        project_root = str(REPO_ROOT)

    resolver = PathResolver(project_root)
    details = []
    drifted = 0
    variants = 0
    missing = 0

    for d_path in (tc.deliverables or []):
        resolution = resolver.validate_path(d_path)
        if resolution.status == "PATH_DRIFT":
            drifted += 1
            details.append(f"PATH_DRIFT: {d_path} → {resolution.suggested_path}")
        elif resolution.status == "NAME_VARIANT":
            variants += 1
            details.append(f"NAME_VARIANT: {d_path} → {resolution.suggested_path}")
        elif resolution.status == "MISSING":
            missing += 1
            details.append(f"MISSING: {d_path} (未在项目中找到)")

    return {"drifted": drifted, "variants": variants, "missing": missing, "details": details}


def _render_result_line(status: str, tc: TaskCard, orig_id: str, detail: str = "") -> str:
    """_render_result_line implementation."""
    icon = {"OK": "✓", "SKIP": "○", "ERR": "✗"}.get(status, "?")
    line = f"  [{icon}] {tc.task_id} <- {orig_id}  \"{tc.title[:55]}\""
    if detail:
        line += f"  ({detail})"
    return line


def import_tasks(
    source_dir: str,
    *,
    dry_run: bool = False,
    force: bool = False,
    validate_paths: bool = False,
) -> int:
    """import_tasks implementation."""
    source_path = Path(source_dir)
    if not source_path.is_dir():
        print(f"[ERROR] 目录不存在: {source_dir}")
        return EXIT_FINDINGS

    md_files = sorted(source_path.glob("TASK-*.md"))
    if not md_files:
        print(f"[ERROR] 目录中无 TASK-*.md 文件: {source_dir}")
        return EXIT_FINDINGS

    print(f"[INFO] 发现 {len(md_files)} 个任务卡文件")
    if dry_run:
        print("[INFO] DRY-RUN 模式：仅解析和校验，不写入数据库")
    if not force:
        print("[INFO] 增量模式：跳过数据库中已存在的任务（--force 可强制覆盖）")

    init_db(DB_PATH)

    existing_ids: set[str] = set()
    with TaskRepository(db_path=DB_PATH, auto_init=False, enable_gate=False) as repo:
        rows = repo._conn.execute("SELECT task_id FROM tasks WHERE is_deleted = 0")
        existing_ids = {r["task_id"] for r in rows.fetchall()}

    results: dict[str, list[dict]] = {"OK": [], "SKIP": [], "ERR": []}

    for i, fp in enumerate(md_files, start=1):
        seq_ref = f"[{i:03d}] {fp.name}"
        try:
            fm = _parse_frontmatter(fp)
        except Exception as e:
            results["ERR"].append({"file": fp.name, "error": f"YAML 解析失败: {e}"})
            print(f"  [✗] {fp.name}  YAML 解析失败: {e}")
            continue

        try:
            tc = _build_taskcard(fm, i)
        except Exception as e:
            results["ERR"].append({"file": fp.name, "error": f"TaskCard 构造失败: {e}"})
            print(f"  [✗] {fp.name}  TaskCard 构造失败: {e}")
            continue

        validation_errors = _validate_taskcard(tc)
        if validation_errors:
            for ve in validation_errors:
                results["ERR"].append({"file": fp.name, "task_id": tc.task_id, "error": ve})
                print(f"  [✗] {fp.name}  {ve}")
            continue

        if validate_paths and tc.deliverables:
            path_report = _validate_paths(tc)
            if path_report.get("drifted", 0) > 0 or path_report.get("variants", 0) > 0:
                for detail in path_report.get("details", []):
                    print(f"  [!] {fp.name}  G8 WARNING: {detail}")

        orig_id = fm.get("task_id", "?")

        if not force and tc.task_id in existing_ids:
            results["SKIP"].append({"task_id": tc.task_id, "title": tc.title})
            print(_render_result_line("SKIP", tc, orig_id, "已存在，跳过"))
            continue

        results["OK"].append({"task": tc, "file": fp.name, "orig_id": orig_id})

    print(f"\n[INFO] 解析完成: 可导入 {len(results['OK'])} / 已跳过 {len(results['SKIP'])} / 错误 {len(results['ERR'])}")

    if dry_run:
        if results["OK"]:
            print("\n[DRY-RUN] 将写入以下任务（未实际写入）：")
            for r in results["OK"]:
                print(_render_result_line("OK", r["task"], r["orig_id"]))
        if results["SKIP"]:
            print(f"\n[DRY-RUN] 跳过 {len(results['SKIP'])} 个已存在的任务")
        if results["ERR"]:
            print(f"\n[ERROR] 以下 {len(results['ERR'])} 个文件存在错误：")
            for r in results["ERR"]:
                print(f"  - {r['file']}: {r['error']}")
            return EXIT_ERROR
        return EXIT_PASS

    if not results["OK"]:
        print("[INFO] 无新任务需要导入")
        return 0 if not results["ERR"] else 2

    print(f"\n[INFO] 写入 SQLite: {DB_PATH}")
    imported = 0
    errors = []

    with TaskRepository(db_path=DB_PATH, auto_init=False, enable_gate=False) as repo:
        for r in results["OK"]:
            try:
                repo.upsert(r["task"])
                imported += 1
                print(_render_result_line("OK", r["task"], r["orig_id"]))
            except Exception as e:
                errors.append((r["file"], r["task"].task_id, str(e)))
                print(f"  [✗] {r['file']}  DB 写入失败: {e}")

    print(f"\n[DONE] 成功导入 {imported} / 跳过 {len(results['SKIP'])} / 错误 {len(results['ERR']) + len(errors)}")

    if errors:
        print(f"\n[ERROR] 写入失败的 {len(errors)} 个任务：")
        for fname, tid, err in errors:
            print(f"  - {fname} ({tid}): {err}")
        return EXIT_ERROR

    return 0 if not results["ERR"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="批量导入 .md 任务卡到 SQLite 任务数据库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  python %(prog)s docs/03_modules/.../changes/MOD-XXX/
  python %(prog)s docs/03_modules/.../changes/MOD-XXX/ --dry-run
  python %(prog)s docs/03_modules/.../changes/MOD-XXX/ --force
""",
    )
    parser.add_argument("source_dir", help="任务卡 .md 文件所在目录")
    parser.add_argument("--dry-run", action="store_true", help="仅解析和校验，不写入数据库")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的任务（默认跳过）")
    parser.add_argument("--validate-paths", action="store_true", help="启用 PathResolver 校验 downstream_outputs 路径漂移")
    args = parser.parse_args()

    sys.exit(import_tasks(
        args.source_dir,
        dry_run=args.dry_run,
        force=args.force,
        validate_paths=args.validate_paths,
    ))


__manifest__ = {
    "dimensions": ["D5", "D3"],
    "priority": "P1",
    "timeout_seconds": 30,
    "args": [
        {"flag": "<source_dir>", "type": "str", "description": "任务卡 .md 文件所在目录"},
        {"flag": "--dry-run", "type": "flag", "description": "仅解析校验，不写入数据库"},
        {"flag": "--force", "type": "flag", "description": "强制覆盖已存在任务"},
    ],
    "warn_only": False,
    "description": (
        "批量导入 .md 任务卡到 SQLite 任务数据库（data/zalpha_metadata.db）。"
        "支持 --dry-run（预览）和 --force（强制覆盖）。"
        "默认增量模式：跳过数据库中已存在的任务。"
        "基于 ADR-0030（SQLite 元数据层）+ ADR-0040（Pydantic V2 契约）。"
    ),
}
