# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/backup_runtime_state.py | §
# [MODULE] scripts.governance.meta.backup_runtime_state
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta.__init__
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
backup_runtime_state.py — 运行时状态备份（蓝图 §33 灾备）

DEPRECATED（ARCH-041）：git history 已是 yaml/jsonl 文件真源（directory_contract L740），
物理快照违反真源唯一原则。本脚本默认输出路径已从 meta/_backups/（deprecated）改为
tmp/runtime_backups/（临时目录，不进 git）。脚本本身仍按 SQLite 时代设计，PG 迁移后
未更新（architecture_debt_registry §5.33.2），后续应重写或归档。

将脚本系统动态状态导出为可 git commit 的快照：
- YAML 配置文件 → 时间戳快照
- 产出归档 → commit

Usage:
    python scripts/governance/meta/backup_runtime_state.py
    python scripts/governance/meta/backup_runtime_state.py --output-dir tmp/runtime_backups/
    python scripts/governance/meta/backup_runtime_state.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 运行时状态备份 — SQLite导出JSON+YAML快照→commit（灾备 §33）
dimensions:
- D1
priority: P1
timeout_seconds: 60
warn_only: true
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

from _shared.constants import EXIT_PASS, REPO_ROOT, SCRIPTS_DIR

META_DIR = SCRIPTS_DIR / "meta"
# ARCH-041: 默认输出路径从 meta/_backups/（deprecated）改为 tmp/runtime_backups/（不进 git）
DEFAULT_BACKUP_DIR = REPO_ROOT / "tmp" / "runtime_backups"


def backup_yaml_files(backup_dir: Path) -> list[str]:
    """备份所有 meta/ 下的 YAML 状态文件。

    Args:
        backup_dir: 备份输出目录

    Returns:
        list[str]: 备份的文件列表
    """
    backed_up: list[str] = []
    yaml_files = list(META_DIR.glob("*.yaml"))
    for yf in yaml_files:
        if yf.name.startswith("_"):
            continue
        dst = backup_dir / yf.name
        try:
            content = yf.read_bytes()
            tmp = f"{dst}.tmp"
            with open(tmp, "wb") as f:
                f.write(content)
            os.replace(tmp, str(dst))
            backed_up.append(str(yf.relative_to(SCRIPTS_DIR)))
        except OSError:
            continue
    return backed_up


def backup_jsonl_files(backup_dir: Path) -> list[str]:
    """备份所有 meta/ 下的 JSONL 文件。

    Args:
        backup_dir: 备份输出目录

    Returns:
        list[str]: 备份的文件列表
    """
    backed_up: list[str] = []
    jsonl_files = list(META_DIR.glob("*.jsonl"))
    for jf in jsonl_files:
        dst = backup_dir / jf.name
        try:
            content = jf.read_bytes()
            tmp = f"{dst}.tmp"
            with open(tmp, "wb") as f:
                f.write(content)
            os.replace(tmp, str(dst))
            backed_up.append(str(jf.relative_to(SCRIPTS_DIR)))
        except OSError:
            continue
    return backed_up


def create_manifest(backup_dir: Path, backed_up: list[str]) -> None:
    """创建备份 manifest。

    Args:
        backup_dir: 备份目录
        backed_up: 备份文件列表
    """
    manifest = {
        "timestamp": datetime.now(UTC).isoformat(),
        "backup_type": "runtime_state_snapshot",
        "files": backed_up,
        "source": str(META_DIR.relative_to(REPO_ROOT)),
    }
    manifest_path = backup_dir / "backup_manifest.json"
    tmp = f"{manifest_path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, str(manifest_path))


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="运行时状态备份")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_BACKUP_DIR),
        help=f"备份输出目录（默认: {DEFAULT_BACKUP_DIR}）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    backup_dir = Path(args.output_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    snapshot_dir = backup_dir / f"snapshot_{timestamp}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = backup_yaml_files(snapshot_dir)
    jsonl_files = backup_jsonl_files(snapshot_dir)
    all_files = yaml_files + jsonl_files

    create_manifest(snapshot_dir, all_files)

    print(f"\n[BACKUP] {len(all_files)} 文件已备份到 {snapshot_dir.relative_to(REPO_ROOT)}\n", file=sys.stderr)
    for f in all_files:
        print(f"  ✅ {f}", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
