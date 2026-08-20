# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.d1_structure.archive_drafts_zone
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.frontmatter; scripts.governance._shared.constants
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] STATUS_ARBITRATED="arbitrated"(与 frontmatter 值一致);WARN_DAYS=30;ARCHIVE_DAYS=60
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/shared/test_drafts_zone_archiver_unit.py; tests/governance/shared/test_drafts_zone_archiver_governance.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""草稿区生命周期归档器——扫描 arbitrated 草稿，按 age 判定 warn/archive/skip。

判定规则:
  - audit_status == 'arbitrated' 且 age >= 60 天 → archive
  - audit_status == 'arbitrated' 且 age >= 30 天 → warn
  - 其余 → skip
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__manifest__ = """
args: []
description: 草稿区生命周期归档器——扫描/判定/执行
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.frontmatter import parse_frontmatter_from_file  # noqa: E402

ARCHIVE_ROOT = REPO_ROOT / "docs" / "99_archive"
AUDIT_LOG_DIR = REPO_ROOT / ".runtime" / "audit"
AUDIT_LOG_PATH = AUDIT_LOG_DIR / "archive_log.jsonl"
WARN_DAYS = 30
ARCHIVE_DAYS = 60

STATUS_ARBITRATED = "arbitrated"
STATUS_PENDING = "pending"
STATUS_RESOLVED = "resolved"


def scan_drafts(directory: Path, warn_days: int = WARN_DAYS, archive_days: int = ARCHIVE_DAYS) -> list[dict[str, Any]]:
    """扫描 directory 下的 .md 草稿文件，解析 frontmatter 判定生命周期 action。"""
    results: list[dict[str, Any]] = []
    if not directory.exists():
        return results
    for md_file in sorted(directory.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        fm = parse_frontmatter_from_file(md_file)
        if fm is None:
            results.append(
                {
                    "path": md_file,
                    "relative": md_file.relative_to(directory),
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
                "relative": md_file.relative_to(directory),
                "audit_status": audit_status,
                "arbitrated_date": arbitrated_date_str,
                "age_days": age_days,
                "action": action,
            }
        )
    return results


def compute_archive_target(draft_path: Path, arbitrated_date_str: str) -> Path:
    """计算归档目标路径: ARCHIVE_ROOT/<YYYY-MM>/<draft_parent_name>。"""
    try:
        arb_date = datetime.strptime(str(arbitrated_date_str), "%Y-%m-%d")
        month_dir = arb_date.strftime("%Y-%m")
    except ValueError:
        month_dir = "undated"
    draft_name = draft_path.parent.name if draft_path.parent.name else draft_path.stem
    return ARCHIVE_ROOT / month_dir / draft_name


def write_audit_log(entry: dict[str, Any]) -> None:
    """将归档操作记录追加到审计日志 JSONL。"""
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
    """执行归档操作——warn 预警/archive 提议或确认移动/skip 跳过。"""
    actions_taken: list[str] = []
    for draft in drafts:
        if draft["action"] == "warn":
            msg = f"WARN: {draft['relative']} — arbitrated {draft['age_days']} 天前（≥{WARN_DAYS} 天），建议归档"
            actions_taken.append(msg)
            write_audit_log({**draft, "action": "warn"})
        elif draft["action"] == "archive":
            target = compute_archive_target(draft["path"], draft["arbitrated_date"])
            if confirm:
                target.mkdir(parents=True, exist_ok=True)
                dest = target / draft["path"].name
                shutil.move(str(draft["path"]), str(dest))  # ops-guard-exempt: 归档搬移本职（drafts→archive 区归置）
                try:
                    rel_dest = dest.relative_to(REPO_ROOT)
                except ValueError:
                    rel_dest = dest
                msg = f"ARCHIVED: {draft['relative']} → {rel_dest}（arbitrated {draft['age_days']} 天前，≥{ARCHIVE_DAYS} 天）"
            else:
                try:
                    rel_target = target.relative_to(REPO_ROOT)
                except ValueError:
                    rel_target = target
                msg = f"PROPOSED: {draft['relative']} → {rel_target}/{draft['path'].name}（arbitrated {draft['age_days']} 天前，≥{ARCHIVE_DAYS} 天，需 --confirm）"
            actions_taken.append(msg)
            write_audit_log({**draft, "action": "archive" if confirm else "proposed"})
    return actions_taken
