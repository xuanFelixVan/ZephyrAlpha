# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/refresh_master_entries.py | §
# [MODULE] scripts.governance.generators.refresh_master_entries
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
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
refresh_master_entries.py — 登记表总索引 entries 自动刷新器

读取 registry-master-index.yaml（手工艺富格式），对每个登记的 registry
文件重新计数，将 entries / vr_rules / unresolved / resolved 等派生字段
刷新为实际值。

对标 §6.16 静态清单自动生成铁律。
此脚本解决根因：master-index 的 entries 字段为手工维护快照，随各子注册表
独立滚动后自然过时。接入 pre_commit 后每次 commit 自动校准。

Usage:
    python scripts/governance/generators/refresh_master_entries.py
    python scripts/governance/generators/refresh_master_entries.py --check
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.registry_entry_count import count_primary_registry_entries

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --check, type: bool, description: "仅检测漂移（不写盘）"}
  - {flag: --fix, type: bool, description: "自动刷新 entries（写盘）"}
warn_only: false
description: >
  读取 registry-master-index.yaml，对各行 entries 字段与实际文件条目数比对，漂移时刷新。
"""

MASTER_INDEX_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry-master-index.yaml"
)

SPECIAL_COUNT_FIELDS = ("vr_rules", "unresolved", "resolved")


def _read_yaml(path: Path) -> dict | None:
    """_read_yaml implementation."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _resolve_special_counts(reg_data: dict, stem: str) -> dict[str, int]:
    """_resolve_special_counts implementation."""
    extra: dict[str, int] = {}

    if stem == "architecture_contract":
        tvr = reg_data.get("total_vr_rules")
        if isinstance(tvr, int) and tvr > 0:
            extra["vr_rules"] = tvr

    if stem == "declarative-contract-tracker":
        tc = reg_data.get("total_contracts")
        if isinstance(tc, int) and tc > 0:
            extra["entries"] = tc
        for k in ("unresolved", "resolved"):
            v = reg_data.get(k)
            if isinstance(v, int):
                extra[k] = v

    return extra


def refresh(dry_run: bool = True) -> tuple[bool, list[str]]:
    """读取主索引，逐条比对 entries 字段。返回 (changed, msgs)。"""
    master = _read_yaml(MASTER_INDEX_PATH)
    if master is None:
        return (False, ["ERROR: 无法读取 registry-master-index.yaml"])

    changed = False
    msgs: list[str] = []
    updated_count = 0

    for cat in master.get("categories", []):
        cat_files = cat.get("files", [])
        if not isinstance(cat_files, list):
            continue

        for entry in cat_files:
            if not isinstance(entry, dict):
                continue
            fname = entry.get("file", "")
            if not fname:
                continue
            old_entries = entry.get("entries")
            if not isinstance(old_entries, int):
                continue

            cat_path = Path(cat.get("path", ""))
            full_path = REPO_ROOT / cat_path / fname
            reg_data = _read_yaml(full_path)
            if reg_data is None:
                continue

            stem = full_path.stem
            actual = count_primary_registry_entries(reg_data, stem)

            if actual > 0 and actual != old_entries:
                msgs.append(f"  {entry.get('registry_id', '?')} entries: {old_entries} → {actual}")
                if not dry_run:
                    entry["entries"] = actual
                    entry["last_updated"] = "2026-05-06"
                changed = True
                updated_count += 1

            extra = _resolve_special_counts(reg_data, stem)
            for key, val in extra.items():
                old_val = entry.get(key)
                if isinstance(old_val, int) and old_val != val:
                    msgs.append(f"  {entry.get('registry_id', '?')} {key}: {old_val} → {val}")
                    if not dry_run:
                        entry[key] = val
                    changed = True
                    updated_count += 1

    if not dry_run and changed:
        master["last_auto_refresh"] = "2026-05-06"
        master["entries_auto_refreshed"] = True
        content = yaml.dump(master, allow_unicode=True, default_flow_style=False, sort_keys=False)
        atomic_write_safe(MASTER_INDEX_PATH, content)
        msgs.append(f"  已写盘: {updated_count} 个条目刷新")

    return (changed, msgs)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="刷新 registry-master-index.yaml 的 entries 字段")
    parser.add_argument("--check", action="store_true", help="仅检测漂移")
    parser.add_argument("--fix", action="store_true", help="自动刷新并写盘")
    args = parser.parse_args()

    dry_run = not args.fix
    changed, msgs = refresh(dry_run=dry_run)

    for m in msgs:
        print(m)

    if changed:
        if dry_run:
            print("DRIFT: entries 字段过时——运行 --fix 自动修复")
        else:
            print("OK: entries 已刷新")
        sys.exit(EXIT_FINDINGS)

    print("OK: entries 全部一致")


if __name__ == "__main__":
    main()
