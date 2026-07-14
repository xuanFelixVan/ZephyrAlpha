# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/drafts_zone_archiver.py | §
# [MODULE] scripts.governance.d1_structure.drafts_zone_archiver
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
# [TTL] task_bound
"""
草稿区生命周期归档器 (Drafts Zone Lifecycle Archiver · V-16)


任务编号 : T-V2-013（Wave 1 V-16 兜底）
权限层级 : Human-Gated
创建日期 : 2026-04-27

功能说明
--------
扫描 docs/19_development_workspace/drafts-and-audits/ 下的草稿文件，
根据 frontmatter 中的 audit_status 和 arbitrated_date 判断生命周期：

- audit_status == 'arbitrated' 且距今 ≥30 天 → 警告（warn）
- audit_status == 'arbitrated' 且距今 ≥60 天 → 提议归档（archive proposal）
- 默认 dry-run 模式，需 --confirm 才实际移动文件

归档目标
--------
docs/99_archive/<YYYY-MM>/<draft-name>/

审计日志
--------
.runtime/audit/archive_log.jsonl

用法
----
扫描（dry-run，不移动文件）：
    python scripts/governance/drafts_zone_archiver.py

确认归档（实际移动文件）：
    python scripts/governance/drafts_zone_archiver.py --confirm

仅警告（不提议归档）：
    python scripts/governance/drafts_zone_archiver.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 草稿区归档检查
dimensions:
- D1
- D4
priority: P2
timeout_seconds: 30
warn_only: false
"""

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装，请运行 `pip install pyyaml`", file=sys.stderr)
    sys.exit(EXIT_ERROR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

DRAFTS_ROOT = REPO_ROOT / "docs" / "19_development_workspace" / "drafts-and-audits"
ARCHIVE_ROOT = REPO_ROOT / "docs" / "99_archive"
AUDIT_LOG_DIR = REPO_ROOT / ".runtime" / "audit"
AUDIT_LOG_PATH = AUDIT_LOG_DIR / "archive_log.jsonl"
WARN_DAYS = 30
ARCHIVE_DAYS = 60
STATUS_ARBITRATED = "arbitrated"
from _shared.frontmatter import parse_frontmatter_from_file


def scan_drafts(root: Path, warn_days: int = WARN_DAYS, archive_days: int = ARCHIVE_DAYS) -> list[dict[str, Any]]:
    """scan drafts"""
    results: list[dict[str, Any]] = []
    if not root.exists():
        return results
    for md_file in sorted(root.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        fm = parse_frontmatter_from_file(md_file)
        if fm is None:
            results.append(
                {
                    "path": md_file,
                    "relative": md_file.relative_to(root),
                    "audit_status": None,
                    "arbitrated_date": None,
                    "age_days": None,
                    "action": "skip",
                }
            )
            continue
        audit_status = fm.get("audit_status", "")
        arbitrated_date_str = fm.get("arbitrated_date", "")
        age_days = None
        if arbitrated_date_str:
            try:
                arb_date = datetime.strptime(str(arbitrated_date_str), "%Y-%m-%d").replace(tzinfo=UTC)
                age_days = (datetime.now(UTC) - arb_date).days
            except ValueError:
                pass
        action = "skip"
        if audit_status == STATUS_ARBITRATED and age_days is not None:
            if age_days >= archive_days:
                action = "archive"
            elif age_days >= warn_days:
                action = "warn"
        results.append(
            {
                "path": md_file,
                "relative": md_file.relative_to(root),
                "audit_status": audit_status,
                "arbitrated_date": arbitrated_date_str,
                "age_days": age_days,
                "action": action,
            }
        )
    return results


def compute_archive_target(draft_path: Path, arbitrated_date_str: str) -> Path:
    """compute archive target"""
    try:
        arb_date = datetime.strptime(str(arbitrated_date_str), "%Y-%m-%d")
        month_dir = arb_date.strftime("%Y-%m")
    except ValueError:
        month_dir = "undated"
    draft_name = draft_path.parent.name if draft_path.parent != DRAFTS_ROOT else draft_path.stem
    return ARCHIVE_ROOT / month_dir / draft_name


def write_audit_log(entry: dict[str, Any]) -> None:
    """write audit log"""
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": entry.get("action", "unknown"),
        "source": str(entry.get("relative", "")),
        "audit_status": entry.get("audit_status"),
        "age_days": entry.get("age_days"),
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def execute_archive(drafts: list[dict[str, Any]], confirm: bool = False) -> list[str]:
    """execute archive"""
    actions_taken: list[str] = []
    for draft in drafts:
        if draft["action"] == "warn":
            msg = f"WARN: {draft['relative']} — arbitrated {draft['age_days']} 天前（≥{WARN_DAYS} 天），建议归档"
            actions_taken.append(msg)
            write_audit_log({**draft, "action": "warn"})
        elif draft["action"] == "archive":
            if confirm:
                target = compute_archive_target(draft["path"], draft["arbitrated_date"])
                target.mkdir(parents=True, exist_ok=True)
                dest = target / draft["path"].name
                shutil.move(str(draft["path"]), str(dest))
                msg = f"ARCHIVED: {draft['relative']} → {dest.relative_to(REPO_ROOT)}（arbitrated {draft['age_days']} 天前，≥{ARCHIVE_DAYS} 天）"
            else:
                target = compute_archive_target(draft["path"], draft["arbitrated_date"])
                msg = f"PROPOSED: {draft['relative']} → {target.relative_to(REPO_ROOT)}/{draft['path'].name}（arbitrated {draft['age_days']} 天前，≥{ARCHIVE_DAYS} 天，需 --confirm）"
            actions_taken.append(msg)
            write_audit_log({**draft, "action": "archive" if confirm else "proposed"})
    return actions_taken


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="V-16 草稿区生命周期归档器（Wave 1 终审）")
    parser.add_argument("--confirm", action="store_true", help="确认归档：实际移动文件（默认 dry-run）")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不提议归档")
    parser.add_argument("--warn-days", type=int, default=WARN_DAYS, help=f"警告阈值天数（默认 {WARN_DAYS}）")
    parser.add_argument("--archive-days", type=int, default=ARCHIVE_DAYS, help=f"归档阈值天数（默认 {ARCHIVE_DAYS}）")
    args = parser.parse_args()
    warn_days = args.warn_days
    archive_days = args.archive_days
    if not DRAFTS_ROOT.exists():
        print(f"[drafts_zone_archiver] 草稿区目录不存在: {DRAFTS_ROOT}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)
    drafts = scan_drafts(DRAFTS_ROOT, warn_days=warn_days, archive_days=archive_days)
    if args.warn_only:
        for draft in drafts:
            if draft["action"] == "archive":
                draft["action"] = "warn"
    warn_count = sum(1 for d in drafts if d["action"] == "warn")
    archive_count = sum(1 for d in drafts if d["action"] == "archive")
    skip_count = sum(1 for d in drafts if d["action"] == "skip")
    print(f"[drafts_zone_archiver] 扫描 {len(drafts)} 个草稿文件", file=sys.stderr)
    print(f"  跳过: {skip_count} | 警告: {warn_count} | 归档提议: {archive_count}", file=sys.stderr)
    actions = execute_archive(drafts, confirm=args.confirm)
    for action in actions:
        print(f"  - {action}", file=sys.stderr)
    if not actions:
        print("[drafts_zone_archiver] 无需操作", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if args.warn_only:
        print("[drafts_zone_archiver] WARN-ONLY 模式：发现归档提议但不阻塞", file=sys.stderr)
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
