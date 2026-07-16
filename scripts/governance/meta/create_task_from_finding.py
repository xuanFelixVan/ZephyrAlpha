# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/create_task_from_finding.py | §
# [MODULE] scripts.governance.meta.create_task_from_finding
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.gov_enforcement.rule_enforcement.task_types; zephyr.integration.__init__; zephyr.shared.models; zephyr.governance.persistence.task_repo
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
create_task_from_finding.py — Finding → 任务卡自动创建引擎

对 run_all.py 产出的 findings.jsonl 中的 CRITICAL/HIGH Finding，
自动创建 TaskCard（OPS-{SEQ} 格式），写入 SQLite + 同步级 MD。

Usage:
    python scripts/governance/meta/create_task_from_finding.py
    python scripts/governance/meta/create_task_from_finding.py --findings findings.jsonl
    python scripts/governance/meta/create_task_from_finding.py --dry-run
    python scripts/governance/meta/create_task_from_finding.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Finding→任务卡自动创建引擎（CRITICAL→P0/HIGH→P1 自动 / MEDIUM→建议，输出到 SQLite+MD 同步）
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 60
warn_only: false
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT, SCRIPTS_DIR, DB_PATH
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

REPO_ROOT_DIR = str(REPO_ROOT)
if REPO_ROOT_DIR not in sys.path:
    sys.path.insert(0, REPO_ROOT_DIR)

from zephyr.integration.schema.severity_types import Priority, SafetyLevel

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.shared.io.paths import DB_PATH
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.gov_enforcement.rule_enforcement.task_types import ExecutionModel, TaskNamespace, TaskStatus
from zephyr.shared.foundation.models import TaskCard

DEFAULT_FINDINGS = SCRIPTS_DIR / "reports" / "findings.jsonl"
TASK_CARDS_DIR = (
    REPO_ROOT
    / "docs"
    / "03_modules"
    / "infrastructure_runtime_integration"
    / "script-system"
    / "changes"
    / "MOD-INF-005"
)

SEVERITY_TO_PRIORITY: dict[str, Priority] = {
    "CRITICAL": Priority.P0,
    "HIGH": Priority.P1,
}

EFFORT_MAP: dict[str, float] = {
    "XS": 0.25,
    "S": 0.5,
    "M": 2.0,
    "L": 8.0,
    "XL": 24.0,
}


def load_findings(path: Path) -> list[dict]:
    """load_findings implementation."""
    if not path.exists():
        print(f"[ERROR] Finding 文件不存在: {path}", file=sys.stderr)
        return []
    findings: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return findings


def _taskcard_to_yaml_md(tc: TaskCard) -> str:
    """将 TaskCard 序列化为 YAML frontmatter + Markdown 正文。"""
    created = (
        tc.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(tc.created_at, "strftime") else str(tc.created_at)[:16]
    )
    updated = (
        tc.updated_at.strftime("%Y-%m-%d %H:%M") if hasattr(tc.updated_at, "strftime") else str(tc.updated_at)[:16]
    )

    desc_safe = tc.description.replace('"', '\\"')[:800]
    title_safe = tc.title.replace('"', '\\"')

    upstream_yaml = "\n".join(f'  - "{f}"' for f in tc.upstream_files) if tc.upstream_files else "  - []"
    downstream_yaml = (
        "\n".join(
            f'  - path: "{d.get("path", "")}"'
            + (f'\n    description: "{d.get("description", "")}"' if d.get("description") else "")
            for d in tc.downstream_outputs
        )
        if tc.downstream_outputs
        else "  - []"
    )

    deps_yaml = "\n".join(f'  - "{d}"' for d in tc.depends_on) if tc.depends_on else "  - []"
    acceptance_yaml = "\n".join(f'  - "{a}"' for a in tc.acceptance) if tc.acceptance else "  - []"

    return f"""---
task_id: "{tc.task_id}"
source_blueprint: "{tc.source_blueprint}"
source_section: "{tc.source_section}"
title: "{title_safe}"
description: "{desc_safe}"
priority: "{tc.priority.value}"
upstream_files:
{upstream_yaml}
downstream_outputs:
{downstream_yaml}
allowed_touch:
  - []
forbidden_touch:
  - []
assigned_model: "{tc.execution_model.value if hasattr(tc.execution_model, "value") else tc.execution_model}"
assigned_pipeline: "{tc.assigned_pipeline}"
estimated_tokens: {tc.estimated_tokens}
timeout_minutes: {tc.timeout_minutes}
acceptance_criteria:
{acceptance_yaml}
rollback_instructions: "{tc.rollback_instructions}"
depends_on:
{deps_yaml}
blocked_by:
  - []
status: "{tc.status.value if hasattr(tc.status, "value") else tc.status}"
tags_fn:
  - finding-fix
tags_ly: "infrastructure_runtime_integration"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-005"
completed_gates: []
blocked_gates: {{}}
artifact_paths:
  - []
ai_autonomy_level: "{tc.ai_autonomy_level}"
---

# {tc.title}

## 目标
{tc.description}

## 触发条件
- 来自 Finding 自动生成

## 执行步骤

### 读
{chr(10).join(f"- {f}" for f in tc.upstream_files) if tc.upstream_files else "-（见 upstream_files）"}

### 做
- 按 applicable_rules 修复违规

### 产
{chr(10).join(f"- {d.get('path', str(d))}" if isinstance(d, dict) else f"- {d}" for d in tc.downstream_outputs) if tc.downstream_outputs else "-（见 downstream_outputs）"}

### 检
- 运行对应审计重新扫描

## 验收标准
{chr(10).join(f"- {a}" for a in tc.acceptance) if tc.acceptance else "- 见 acceptance_criteria"}

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 回滚 | {tc.rollback_instructions if tc.rollback_instructions else "git revert"} |

---
*创建: {created} | 更新: {updated}*
*本文件由 create_task_from_finding.py 自动生成（MOD-TASK_SYSTEM TaskCard 格式）。*
"""


def _build_taskcard_from_finding(finding: dict, task_id: str) -> TaskCard:
    """_build_taskcard_from_finding implementation."""
    severity = finding.get("severity", "MEDIUM")
    dimension = finding.get("dimension", "??")
    desc = finding.get("description", "未描述")
    evidence = finding.get("evidence", "")
    target = finding.get("target", {})
    target_file = target.get("file_path", "") if isinstance(target, dict) else str(target)
    finding_id = finding.get("finding_id", "UNKNOWN")

    rec_block = finding.get("recommendation_block", {})
    recommendation = rec_block.get("recommendation", "")
    rec_type = rec_block.get("recommendation_type", "needs_review")
    rec_action = rec_block.get("recommended_action", "create_task")

    phase_num = 0

    priority = SEVERITY_TO_PRIORITY.get(severity, Priority.P2)
    safety = SafetyLevel.H if severity == "CRITICAL" else SafetyLevel.M

    title = f"修复 {severity} Finding: {desc[:60]}"

    description = (
        f"从 {severity} Finding 自动生成。\n\n"
        f"原 Finding: {finding_id}\n"
        f"维度: {dimension}\n"
        f"目标文件: {target_file}\n"
        f"描述: {desc[:200]}\n"
        f"证据: {evidence[:300] if evidence else '无'}\n\n"
        f"修复建议: {recommendation[:300] if recommendation else '无'}\n"
        f"建议类型: {rec_type}\n"
        f"建议动作: {rec_action}"
    )

    acceptance = [
        f"目标文件 {target_file} 的违规已修复",
        f"{dimension} 维度重新扫描无该 Finding 重现",
    ]

    upstream = [target_file] if target_file else []
    downstream = [{"path": target_file, "description": "修复后的目标文件"}] if target_file else []
    deliverables = [target_file] if target_file else []

    rollback = f"git checkout -- {target_file}" if target_file else ""

    tags = [
        "auto-generated",
        "finding-fix",
        severity.lower(),
        f"finding:{finding_id}",
        f"dim:{dimension}",
    ]

    applicable_rules: list[dict] = [
        {"module_id": "MOD-INF-005", "section": "§3.2.1", "reason": f"自动创建自 {severity} Finding {finding_id}"},
    ]
    if target_file:
        applicable_rules.append({"module_id": "MOD-INF-005", "section": "§3.2.1", "reason": f"目标文件: {target_file}"})

    autonomy = "review_required" if severity in ("CRITICAL", "HIGH") else "supervised"

    now = datetime.now(UTC)

    return TaskCard(
        task_id=task_id,
        namespace=TaskNamespace.OPS,
        seq=int(task_id.split("-")[-1]) if "-" in task_id else 1,
        title=title,
        status=TaskStatus.PENDING,
        priority=priority,
        phase=phase_num,
        execution_model=ExecutionModel.deepseek,
        safety_level=safety,
        source_blueprint="MOD-INF-005",
        source_section=f"auto-{finding_id}",
        description=description,
        upstream_files=upstream,
        downstream_outputs=downstream,
        deliverables=deliverables,
        acceptance=acceptance,
        depends_on=[],
        blocked_by=[],
        tags=tags,
        applicable_rules=applicable_rules,
        rollback_instructions=rollback,
        estimated_tokens=4000,
        timeout_minutes=30,
        assigned_pipeline="A",
        pipeline_modules=[],
        artifact_paths=[target_file] if target_file else [],
        ai_autonomy_level=autonomy,
        created_at=now,
        updated_at=now,
    )


def create_task_card(
    finding: dict,
    task_id: str,
    dry_run: bool = False,
) -> str | None:
    """为单个 Finding 创建 TaskCard → SQLite + MD 同步。

    Returns:
        str | None: 创建的文件路径（MD），dry_run 返回 None
    """
    tc = _build_taskcard_from_finding(finding, task_id)
    md_content = _taskcard_to_yaml_md(tc)

    severity = finding.get("severity", "MEDIUM")
    desc = finding.get("description", "未描述")[:200]

    if dry_run:
        print(f"\n[DRY RUN] 将创建 {task_id} 于 {TASK_CARDS_DIR / f'TASK-{task_id}.md'}", file=sys.stderr)
        print(f"  标题: {tc.title}", file=sys.stderr)
        print(f"  优先级: {tc.priority.value}", file=sys.stderr)
        print(f"  safety_level: {tc.safety_level.value}", file=sys.stderr)
        return None

    TASK_CARDS_DIR.mkdir(parents=True, exist_ok=True)

    task_path = TASK_CARDS_DIR / f"TASK-{task_id}.md"
    atomic_write_safe(task_path, md_content)

    write_to_sqlite(tc)

    print(f"  ✅ 已创建 {task_id}: {desc[:80]}", file=sys.stderr)
    return str(task_path)


def write_to_sqlite(tc: TaskCard) -> None:
    """write_to_sqlite implementation."""
    init_db(DB_PATH)
    with TaskRepository(db_path=DB_PATH, auto_init=False, enable_gate=False) as repo:
        repo.upsert(tc)


def generate_task_id() -> str:
    """Generate output from input data."""
    if not TASK_CARDS_DIR.exists():
        return f"OPS-{datetime.now(UTC).strftime('%Y%m%d')}-001"
    max_seq = 0
    for f in TASK_CARDS_DIR.glob("TASK-OPS-*.md"):
        try:
            num = int(f.stem.split("-")[-1])
            if num > max_seq:
                max_seq = num
        except (ValueError, IndexError):
            continue
    next_seq = max_seq + 1
    return f"OPS-{next_seq:04d}"


def process_findings(
    findings_path: Path,
    dry_run: bool = False,
    warn_only: bool = False,
) -> int:
    """process_findings implementation."""
    findings = load_findings(findings_path)
    if not findings:
        print("[CREATE-TASK] 无 Finding 需要处理", file=sys.stderr)
        return EXIT_PASS

    criticals = [f for f in findings if f.get("severity") == "CRITICAL"]
    highs = [f for f in findings if f.get("severity") == "HIGH"]
    mediums = [f for f in findings if f.get("severity") == "MEDIUM"]

    print(
        f"\n[CREATE-TASK] Finding 分布: CRITICAL={len(criticals)}, HIGH={len(highs)}, MEDIUM={len(mediums)}\n",
        file=sys.stderr,
    )

    created: list[str] = []
    suggested: list[str] = []

    for f in criticals + highs:
        task_id = generate_task_id()
        path = create_task_card(f, task_id, dry_run=dry_run)
        if path:
            created.append(path)

    for f in mediums:
        fid = f.get("finding_id", "??")
        desc = f.get("description", "")[:80]
        rec = f.get("recommendation_block", {}).get("recommendation", "请人工评估")
        suggested.append(f"{fid}: {desc} → {rec}")
        print(f"  💡 MEDIUM Finding [{fid}] 建议人工评估: {desc}", file=sys.stderr)

    print(f"\n  自动创建: {len(created)} 张任务卡", file=sys.stderr)
    if suggested:
        print(f"  建议评估: {len(suggested)} 条 MEDIUM Finding", file=sys.stderr)

    if warn_only:
        return EXIT_PASS
    return 0 if not criticals else 1


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Finding → 任务卡自动创建引擎（TaskCard 格式）")
    parser.add_argument(
        "--findings",
        type=str,
        default=str(DEFAULT_FINDINGS),
        help=f"Finding JSONL 文件路径（默认: {DEFAULT_FINDINGS}）",
    )
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    exit_code = process_findings(
        Path(args.findings),
        dry_run=args.dry_run,
        warn_only=args.warn_only,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
