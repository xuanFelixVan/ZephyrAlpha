# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_script_provenance.py | §
# [MODULE] scripts.governance.meta.validate_script_provenance
# [DOMAIN] D_GOV_SCRIPTS
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
validate_script_provenance.py — 脚本 Provenance 溯源链



对标 B47（Provenance 链）+ SLSA Framework (Supply-chain Levels for Software Artifacts)。

为每个治理脚本生成和维护起源元数据：
- 创建时间 / 最后修改时间
- 创建者（人工/哪个 AI 模型）
- 创建 Session ID
- 修改历史（每次修改记录 model + timestamp + diff hash）
- 关联的 PR/Commit

元数据存储在 meta/script_provenance_db.json 中，
每次脚本变更时由 pre_commit 钩子自动更新。

Usage:
    python scripts/governance/meta/validate_script_provenance.py --register-all
    python scripts/governance/meta/validate_script_provenance.py --check d7_code/validate_test_coverage.py
    python scripts/governance/meta/validate_script_provenance.py --list
    python scripts/governance/meta/validate_script_provenance.py --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import hashlib
import json as json_mod
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_PROVENANCE_DB = _SCRIPTS_DIR / "meta" / "script_provenance_db.json"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_db() -> dict:
    """_load_db implementation."""
    if not _PROVENANCE_DB.exists():
        return {"scripts": {}, "created_at": ""}
    with open(_PROVENANCE_DB, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_db(data: dict) -> None:
    """_save_db implementation."""
    _PROVENANCE_DB.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_PROVENANCE_DB, json_mod.dumps(data, ensure_ascii=False, indent=2))


def _hash_content(content: str) -> str:
    """_hash_content implementation."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _get_git_author(file_path: str) -> str:
    """_get_git_author implementation."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%an", "--", file_path],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip() or "unknown"


def _get_git_commit(file_path: str) -> str:
    """_get_git_commit implementation."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", file_path],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()[:12] or "unknown"


def _is_ai_author(author: str) -> bool:
    """_is_ai_author implementation."""
    ai_names = {"claude", "cursor", "copilot", "windsurf", "glm", "deepseek", "roocode", "trae"}
    return any(name in author.lower() for name in ai_names)


def register_all() -> dict:
    """register_all implementation."""
    db = _load_db()
    scripts_db = db.setdefault("scripts", {})
    now = datetime.now(UTC).isoformat()
    count = 0

    for py_file in _SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = str(py_file.relative_to(_REPO_ROOT))
        current_hash = _hash_content(py_file.read_text(encoding="utf-8"))
        author = _get_git_author(rel)
        commit = _get_git_commit(rel)

        if rel in scripts_db:
            known = scripts_db[rel]
            if known.get("last_content_hash") != current_hash:
                known.setdefault("change_history", []).append(
                    {
                        "timestamp": now,
                        "content_hash": current_hash,
                        "author": author,
                        "commit": commit,
                    }
                )
                known["last_modified_at"] = now
                known["last_modified_by"] = author
                known["modified_by_ai"] = _is_ai_author(author)
                known["last_content_hash"] = current_hash
                known["total_modifications"] = len(known["change_history"])
                count += 1
        else:
            scripts_db[rel] = {
                "path": rel,
                "created_at": now,
                "last_modified_at": now,
                "creator": author,
                "creator_is_ai": _is_ai_author(author),
                "last_modified_by": author,
                "modified_by_ai": _is_ai_author(author),
                "creation_commit": commit,
                "last_content_hash": current_hash,
                "total_modifications": 0,
                "change_history": [],
            }
            count += 1

    db["last_updated_at"] = now
    _save_db(db)
    return {
        "total_scripts": len(scripts_db),
        "newly_registered": count,
        "ai_created": sum(1 for s in scripts_db.values() if s.get("creator_is_ai")),
        "ai_modified": sum(1 for s in scripts_db.values() if s.get("modified_by_ai")),
    }


def check_script(script_path: str) -> dict:
    """Check compliance and report findings."""
    db = _load_db()
    entry = db.get("scripts", {}).get(script_path)
    if not entry:
        return {"status": "UNTRACKED", "script": script_path}
    return entry


def list_provenance(json_output: bool = False) -> list[dict]:
    """list_provenance implementation."""
    db = _load_db()
    result = []
    for path, entry in db.get("scripts", {}).items():
        result.append(
            {
                "path": path,
                "creator": entry.get("creator", ""),
                "ai_created": entry.get("creator_is_ai", False),
                "total_modifications": entry.get("total_modifications", 0),
                "last_modified_by": entry.get("last_modified_by", ""),
            }
        )
    if json_output:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in result:
            ai_tag = "🤖" if r["ai_created"] else "👤"
            print(
                f"  {ai_tag} {r['path']}: by {r['creator']} ({r['total_modifications']} modifications)", file=sys.stderr
            )


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--register-all" in sys.argv:
        result = register_all()
        print(f"[PROVENANCE] ✅ 已注册 {result['total_scripts']} 个脚本", file=sys.stderr)
        print(f"  AI 创建: {result['ai_created']} 个", file=sys.stderr)
    elif "--check" in sys.argv:
        idx = sys.argv.index("--check")
        script = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        if script:
            result = check_script(script)
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    elif "--list" in sys.argv:
        list_provenance("--json" in sys.argv)
    elif "--json" in sys.argv:
        db = _load_db()
        print(json_mod.dumps(db, ensure_ascii=False, indent=2))
    else:
        print(
            "Usage: python validate_script_provenance.py --register-all | --check <path> | --list | --json",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
