# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/backup_runtime_state.py | §
# [MODULE] scripts.governance.meta.backup_runtime_state
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__; zephyr.governance.depgraph_schema (_build_pg_dsn, backup_pg_depgraph 函数)
# [CONSUMERS] scripts.governance.apply_depgraph (backup_pg_depgraph 事件触发入口)
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
backup_runtime_state.py — 运行时状态备份（蓝图 §33 灾备）

DEPRECATED（ARCH-041）：git history 已是 yaml/jsonl 文件真源（directory_contract L740），
物理快照违反真源唯一原则。本脚本默认输出路径已从 meta/_backups/（deprecated）改为
tmp/runtime_backups/（临时目录，不进 git）。

PG depgraph 备份已实现（ARCH-041 §5.33.1 治本）：backup_pg_depgraph() 函数。
触发方式：apply_depgraph.py 成功修改 depgraph 后自动调用（事件触发）。

YAML/JSONL 快照功能仍保留（向后兼容），但已标记 DEPRECATED。

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


# ── PG depgraph 备份（ARCH-041 §5.33.1 治本）──────────────────────────────
# pg_dump 不可用时的 fallback：用 psycopg2 查询导出为 JSON。
# 触发方式：apply_depgraph.py 成功修改 depgraph 后自动调用（事件触发，非时间触发）。
# 自动清理：保留最近 max_backups 个备份。

def backup_pg_depgraph(max_backups: int = 10) -> str | None:
    """备份 PG depgraph 数据（nodes + edges 表）到 tmp/pg_backups/。

    ARCH-041 §5.33.1 治本：PG depgraph 无备份脚本，此处补强。
    使用 psycopg2 查询导出为 JSON（pg_dump 不可用时的 fallback）。
    自动清理旧备份（保留最近 max_backups 个）。

    Args:
        max_backups: 保留的备份数量

    Returns:
        备份文件路径，失败返回 None
    """
    import psycopg2

    # _build_pg_dsn 在 src/ 下，需要 sys.path
    src_path = str(REPO_ROOT / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from zephyr.governance.depgraph_schema import _build_pg_dsn

    backup_dir = REPO_ROOT / "tmp" / "pg_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"depgraph_{timestamp}.json"

    try:
        conn = psycopg2.connect(**_build_pg_dsn())
        cur = conn.cursor()

        # 导出 nodes 表
        cur.execute("SELECT * FROM nodes ORDER BY node_id")
        columns = [desc[0] for desc in cur.description]
        nodes = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]

        # 导出 edges 表
        cur.execute("SELECT * FROM edges ORDER BY edge_id")
        columns = [desc[0] for desc in cur.description]
        edges = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]

        conn.close()

        backup_data = {
            "timestamp": timestamp,
            "source": "depgraph (PostgreSQL)",
            "tables": {
                "nodes": {"count": len(nodes), "rows": nodes},
                "edges": {"count": len(edges), "rows": edges},
            },
        }

        backup_path.write_text(
            json.dumps(backup_data, default=str, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 自动清理旧备份
        backups = sorted(backup_dir.glob("depgraph_*.json"))
        if len(backups) > max_backups:
            for old in backups[:-max_backups]:
                try:
                    old.unlink()
                except OSError:
                    pass

        print(
            f"[BACKUP-PG] depgraph 备份完成: {backup_path.relative_to(REPO_ROOT)} "
            f"(nodes={len(nodes)}, edges={len(edges)})",
            file=sys.stderr,
        )
        return str(backup_path)
    except Exception as e:
        print(f"[BACKUP-PG] ERROR: {e}", file=sys.stderr)
        return None


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

    # ARCH-041: 运行时 DEPRECATED 警告——防止新 AI 误用过时脚本
    import warnings
    warnings.warn(
        "backup_runtime_state.py YAML/JSONL 快照已 DEPRECATED（ARCH-041）。"
        "git history 已是 yaml/jsonl 文件真源。"
        "PG depgraph 备份请用 backup_pg_depgraph() 函数（apply_depgraph.py 自动调用）。",
        DeprecationWarning,
        stacklevel=1,
    )
    print(
        "\n⚠ DEPRECATED (ARCH-041): YAML/JSONL 快照已过时。"
        "git history 是 YAML/JSONL 真源。PG 备份用 backup_pg_depgraph()。\n",
        file=sys.stderr,
    )

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
