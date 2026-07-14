# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py | §
# [MODULE] scripts.governance.d5_architecture.validators.session.validate_session_log_index_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.session.__init__
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
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

#!/usr/bin/env python3
import os

"""
validate_session_log_index_integrity.py — session_logs 索引 ↔ 磁盘对账 + 自动汇总
=====================================================================================
依据：GOV-AI-007（session-log-schema.yaml v2.2.0）+ PS-REG-011
对标：AGENTS.md §5.2 审计协议 + RULE-ZERO 锁协议

功能
----
1. validate 模式（默认）：
   - index.yaml 中每条 session 引用 → 对应 .yaml 文件必须磁盘存在
   - total_sessions 必须等于实际文件数
   - 检测 index.yaml 中是否仍有手动编写的 blind_spot_timeline（v1.3 后禁止）

2. generate 模式（--generate）：
   - 扫描所有 session log YAML → 提取 blind_spots_discovered
   - 自动生成 session_logs/_auto/blind_spot_timeline.yaml
   - 自动更新 index.yaml 的 by_date / total_sessions / stats

设计原则
--------
- index.yaml 的 by_date/by_module/by_contract 由本脚本从 session log YAML 自动派生
- 禁止 AI 手动在上述索引区添加条目——AI 只需写 session log 文件
- blind_spot_timeline 完全由 _auto/blind_spot_timeline.yaml 承载

Usage:
    python validate_session_log_index_integrity.py              # 仅校验
    python validate_session_log_index_integrity.py --generate   # 校验 + 汇总生成
    python validate_session_log_index_integrity.py --warn-only  # 警告模式
"""

__manifest__ = {
    "args": ["--generate", "--warn-only"],
    "description": "session_logs/index.yaml 与磁盘对账 + 自动生成盲点时间线",
    "dimensions": ["D5", "D11"],
    "priority": "P0",
    "timeout_seconds": 30,
    "warn_only": False,
}

import argparse
import sys
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

import yaml

SESSION_LOGS_DIR = REPO_ROOT / "session_logs"
INDEX_FILE = SESSION_LOGS_DIR / "index.yaml"
AUTO_DIR = SESSION_LOGS_DIR / "_auto"
BLIND_SPOT_FILE = AUTO_DIR / "blind_spot_timeline.yaml"

CAPTURED_IN_INDEX_PREFIX = "captured-in-index-"


def _collect_disk_sessions() -> dict[str, Path]:
    """_collect_disk_sessions implementation."""
    sessions: dict[str, Path] = {}
    for yaml_file in SESSION_LOGS_DIR.rglob("*.yaml"):
        if yaml_file.parent.name == "_auto":
            continue
        if yaml_file.name == "index.yaml":
            continue
        stem = yaml_file.stem
        if stem.startswith("session-"):
            sessions[stem] = yaml_file
    return sessions


def _parse_index() -> dict | None:
    """_parse_index implementation."""
    if not INDEX_FILE.exists():
        return None
    with open(INDEX_FILE, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _extract_blind_spots_from_session(file_path: Path) -> list[dict]:
    """_extract_blind_spots_from_session implementation."""
    try:
        with open(file_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception:
        return []
    if isinstance(data, dict):
        spots = data.get("blind_spots_discovered", [])
        if isinstance(spots, list):
            return spots
    return []


def _extract_modules_from_session(file_path: Path) -> list[str]:
    """_extract_modules_from_session implementation."""
    try:
        with open(file_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception:
        return []
    if isinstance(data, dict):
        mods = data.get("modules_touched", [])
        if isinstance(mods, list):
            return mods
    return []


def generate_blind_spot_timeline(disk_sessions: dict[str, Path]) -> tuple[list[dict], int, int]:
    """Generate output from input data."""
    timeline: list[dict] = []
    for session_id, file_path in sorted(disk_sessions.items()):
        spots = _extract_blind_spots_from_session(file_path)
        for spot in spots:
            entry = {
                "blind_spot_id": spot.get("blind_spot_id", "?"),
                "discovered": _extract_date_from_session_id(session_id),
                "discovered_in_session": session_id,
                "description": spot.get("description", ""),
                "severity": spot.get("severity", "medium"),
                "status": spot.get("status", "open"),
            }
            if spot.get("resolution"):
                entry["resolution"] = spot.get("resolution")
            timeline.append(entry)

    resolved = sum(1 for b in timeline if b.get("status") == "resolved")
    open_count = len(timeline) - resolved
    return timeline, resolved, open_count


def _extract_date_from_session_id(session_id: str) -> str:
    """_extract_date_from_session_id implementation."""
    try:
        parts = session_id.split("-")
        date_str = parts[1]
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except (IndexError, ValueError):
        return datetime.now().strftime("%Y-%m-%d")


def write_blind_spot_timeline(timeline: list[dict], resolved: int, open_count: int) -> None:
    """write_blind_spot_timeline implementation."""
    AUTO_DIR.mkdir(parents=True, exist_ok=True)
    content = {
        "auto_generated_version": "1.1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_by": "validate_session_log_index_integrity.py --generate",
        "total_blind_spots": len(timeline),
        "resolved": resolved,
        "open": open_count,
        "blind_spot_timeline": timeline,
    }
    atomic_write_safe(
        BLIND_SPOT_FILE,
        yaml.dump(content, allow_unicode=True, default_flow_style=False, sort_keys=False),
    )


def update_index_by_date(index_data: dict, disk_sessions: dict[str, Path]) -> dict:
    """update_index_by_date implementation."""
    by_date: dict[str, list[str]] = {}
    for session_id in sorted(disk_sessions.keys()):
        date_str = _extract_date_from_session_id(session_id)
        by_date.setdefault(date_str, []).append(session_id)
    for date_list in by_date.values():
        date_list.sort()
    index_data["by_date"] = by_date
    index_data["total_sessions"] = len(disk_sessions)
    return index_data


def write_index(index_data: dict) -> None:
    """write_index implementation."""
    prefix_lines: list[str] = []
    suffix_content = ""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, encoding="utf-8") as fh:
            raw = fh.read()
    else:
        raw = ""

    lines = raw.split("\n")
    header_ended = False
    for line in lines:
        if not header_ended and (line.startswith("#") or line.strip() == ""):
            prefix_lines.append(line)
        else:
            header_ended = True
            break

    if header_ended:
        remaining = lines[len(prefix_lines) :]
        found_schema = False
        for i, line in enumerate(remaining):
            if not line.startswith("#") and line.strip():
                remaining = remaining[i:]
                found_schema = True
                break
        if not found_schema:
            remaining = remaining[len(prefix_lines) :] if len(remaining) > len(prefix_lines) else remaining

        suffix_start = -1
        for i, line in enumerate(remaining):
            if line.strip() == "# 盲点发现时间线" or "已迁移至" in line:
                suffix_start = i
                break
        if suffix_start > 0:
            suffix_content = "\n".join(remaining[suffix_start:])
            remaining = remaining[:suffix_start]
    else:
        remaining = lines

    header_text = "\n".join(prefix_lines) + "\n"

    data_lines = yaml.dump(index_data, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120).split(
        "\n"
    )

    body_lines = []
    for line in data_lines:
        body_lines.append(line)

    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()

    body_text = "\n".join(body_lines)

    if suffix_content:
        final = header_text + body_text + "\n\n" + suffix_content.strip() + "\n"
    else:
        final = header_text + body_text + "\n"

    atomic_write_safe(INDEX_FILE, final)


def validate(index_data: dict, disk_sessions: dict[str, Path], warn_only: bool) -> int:
    """validate implementation."""
    errors: list[str] = []

    by_date: dict = index_data.get("by_date", {})
    for date_str, session_list in by_date.items():
        for sid in session_list:
            if sid not in disk_sessions:
                errors.append(f"GHOST-REF in by_date[{date_str}]: {sid} → 磁盘无此文件")

    by_module: dict = index_data.get("by_module", {})
    for module_id, session_list in by_module.items():
        for sid in session_list:
            if sid not in disk_sessions:
                errors.append(f"GHOST-REF in by_module[{module_id}]: {sid} → 磁盘无此文件")

    by_contract: dict = index_data.get("by_contract", {})
    for contract_id, session_list in by_contract.items():
        for sid in session_list:
            if sid not in disk_sessions:
                errors.append(f"GHOST-REF in by_contract[{contract_id}]: {sid} → 磁盘无此文件")

    declared_total = index_data.get("total_sessions", 0)
    actual_total = len(disk_sessions)
    if declared_total != actual_total:
        errors.append(f"TOTAL-COUNT-MISMATCH: index={declared_total}, disk={actual_total}")

    raw = INDEX_FILE.read_text(encoding="utf-8") if INDEX_FILE.exists() else ""
    if "blind_spot_timeline:" in raw and "- blind_spot_id:" in raw:
        errors.append(
            "MANUAL-BLIND-SPOTS: index.yaml 中仍有手动编写的 blind_spot_timeline 条目。"
            "请删除——盲点应写入 session log YAML 的 blind_spots_discovered 字段，由 --generate 自动汇总。"
        )

    if errors:
        print(f"\n[SESSION-INDEX] {len(errors)} 个问题:\n", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
    else:
        print(f"[SESSION-INDEX] OK: {actual_total} sessions on disk, index passes")

    if warn_only:
        if errors:
            print("\n[--warn-only] suppressed", file=sys.stderr)
        return EXIT_PASS
    return 1 if errors else 0


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="session_logs 索引 ↔ 磁盘对账 + 自动汇总（GOV-AI-007 v2.2）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断）")
    parser.add_argument(
        "--generate", action="store_true", help="自动从 session log YAML 汇总生成 blind_spot_timeline + by_date"
    )
    args = parser.parse_args()

    disk_sessions = _collect_disk_sessions()
    index_data = _parse_index()

    if args.generate:
        if index_data is None:
            index_data = {
                "index_version": "2.0",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "total_sessions": 0,
                "by_module": {},
                "by_contract": {},
                "by_date": {},
            }

        existing_blind_spots: list[dict] = []
        if BLIND_SPOT_FILE.exists():
            try:
                with open(BLIND_SPOT_FILE, encoding="utf-8") as fh:
                    existing = yaml.safe_load(fh) or {}
                existing_blind_spots = existing.get("blind_spot_timeline", [])
            except Exception:
                pass

        new_timeline, resolved, open_count = generate_blind_spot_timeline(disk_sessions)

        existing_ids = {b.get("blind_spot_id") for b in existing_blind_spots}
        for entry in new_timeline:
            bid = entry.get("blind_spot_id")
            if bid and bid not in existing_ids:
                existing_blind_spots.append(entry)

        merged_resolved = sum(1 for b in existing_blind_spots if b.get("status") == "resolved")
        merged_open = len(existing_blind_spots) - merged_resolved
        write_blind_spot_timeline(existing_blind_spots, merged_resolved, merged_open)

        index_data = update_index_by_date(index_data, disk_sessions)
        index_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        write_index(index_data)
        print(
            f"[GENERATE] OK: {len(disk_sessions)} sessions → by_date synced, "
            f"{len(existing_blind_spots)} blind spots ({merged_resolved} resolved, {merged_open} open) → {BLIND_SPOT_FILE}"
        )

    if index_data is None:
        print("SESSION-INDEX-MISSING: index.yaml not found", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    exit_code = validate(index_data, disk_sessions, args.warn_only)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
