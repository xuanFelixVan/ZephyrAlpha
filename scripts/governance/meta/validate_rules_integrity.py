# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_rules_integrity.py | §
# [MODULE] scripts.governance.meta.validate_rules_integrity
# [DOMAIN] D-GOVERNANCE
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
validate_rules_integrity.py — 规则文件完整性保护



对标 B44（规则文件哈希校验）+ Google SRE Config Integrity Verification。

对所有关键规则文件（AGENTS.md / blueprint.md / thresholds.yaml /
kill_switch_state.yaml / shadow_mode_state.yaml / error_budget_state.yaml /
quickstart.md / quality_standard.md）计算 SHA256 哈希，
与之前注册的 known-good hash 对比——不一致 = 被修改 = 告警。

文件修改正常来源：git commit。异常来源：AI session 意外修改 / 投毒 / 规则文件后门注入。

Usage:
    python scripts/governance/meta/validate_rules_integrity.py
    python scripts/governance/meta/validate_rules_integrity.py --register  # 注册当前状态
    python scripts/governance/meta/validate_rules_integrity.py --check     # 验证未被篡改
    python scripts/governance/meta/validate_rules_integrity.py --diff      # 显示差异
    python scripts/governance/meta/validate_rules_integrity.py --json
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


import argparse
import hashlib
import json as json_mod
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# bootstrap: 一次性算 _shared 路径，随后 REPO_ROOT 真源来自 _shared.constants
# （对标 check_precommit_id_uniqueness.py 模式，遵守 REPO_ROOT 真源唯一约束）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402

_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_INTEGRITY_DB = _SCRIPTS_DIR / "meta" / "rules_integrity_db.json"

RULES_MANIFEST: list[dict] = [
    {"path": "AGENTS.md", "critical": True, "desc": "AI Agent 全局行为约束"},
    {"path": "scripts/governance/quickstart.md", "critical": True, "desc": "AI Session 冷启动卡片"},
    {"path": "scripts/governance/_shared/thresholds.yaml", "critical": True, "desc": "关键阈值 SSoT"},
    {"path": "scripts/governance/meta/kill_switch_state.yaml", "critical": True, "desc": "Kill Switch 状态"},
    {"path": "scripts/governance/meta/shadow_mode_state.yaml", "critical": False, "desc": "Shadow Mode 状态"},
    {"path": "scripts/governance/meta/error_budget_state.yaml", "critical": True, "desc": "Error Budget 状态"},
    {"path": "scripts/governance/quality_standard.md", "critical": True, "desc": "脚本质量标准"},
    {"path": "scripts/governance/script_manifest.yaml", "critical": True, "desc": "脚本注册表"},
    {
        "path": "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py",
        "critical": True,
        "desc": "GATE-ID-UNIQ 检测脚本（A 层 AST 锚点保护 + C 层 golden hash 兜底）",
    },
]

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _hash_file(file_path: Path) -> str:
    """_hash_file implementation."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]


def _hash_git_head(rel_path: str) -> str | None:
    """基于 git HEAD 状态 hash（红蓝发现3 治本）。

    register() 用此函数而非 _hash_file()，确保基线基于已 commit 状态，
    不基于工作树 WIP——攻击者篡改受保护脚本后 commit 无关文件，
    post-commit --register 不会把 WIP 篡改注册为基线（只注册 HEAD 状态）。
    check() 仍用 _hash_file() 基于工作树状态（检测 WIP 篡改）。

    Returns:
        hash 字符串 | None（文件不在 git HEAD）
    """
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"],
        capture_output=True,
        cwd=str(_REPO_ROOT),
        timeout=5,
    )
    if result.returncode != 0:
        return None
    return hashlib.sha256(result.stdout).hexdigest()[:16]


def _load_db() -> dict:
    """_load_db implementation."""
    if not _INTEGRITY_DB.exists():
        return {"files": {}, "registered_at": "", "last_check_at": ""}
    with open(_INTEGRITY_DB, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_db(data: dict) -> None:
    """_save_db implementation."""
    _INTEGRITY_DB.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_INTEGRITY_DB}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json_mod.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, _INTEGRITY_DB)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def register() -> dict:
    """register implementation."""
    now = datetime.now(UTC).isoformat()
    data = {"files": {}, "registered_at": now, "last_check_at": now}
    for entry in RULES_MANIFEST:
        rel = entry["path"]
        # 红蓝发现3 治本：基于 git HEAD 状态 hash，不基于工作树 WIP。
        git_hash = _hash_git_head(rel)
        if git_hash is not None:
            data["files"][rel] = {
                "hash": git_hash,
                "critical": entry["critical"],
                "desc": entry["desc"],
            }
        else:
            # 文件不在 git HEAD（新文件/未跟踪）→ 回退到工作树状态
            fp = _REPO_ROOT / rel
            if fp.exists():
                data["files"][rel] = {
                    "hash": _hash_file(fp),
                    "critical": entry["critical"],
                    "desc": entry["desc"],
                }
    _save_db(data)
    return {"status": "registered", "count": len(data["files"]), "at": now}


def check() -> dict:
    """check implementation."""
    db = _load_db()
    now = datetime.now(UTC)
    results: list[dict] = []
    tampered = 0

    for entry in RULES_MANIFEST:
        fp = _REPO_ROOT / entry["path"]
        rel = entry["path"]
        if not fp.exists():
            results.append(
                {
                    "file": rel,
                    "status": "MISSING",
                    "detail": "文件不存在——可能被删除",
                    "critical": entry["critical"],
                }
            )
            if entry["critical"]:
                tampered += 1
            continue

        current_hash = _hash_file(fp)
        known = db.get("files", {}).get(rel, {})
        known_hash = known.get("hash", "")

        if not known_hash:
            results.append(
                {
                    "file": rel,
                    "status": "UNTRACKED",
                    "detail": "未被注册——首次发现",
                    "critical": entry["critical"],
                }
            )
        elif current_hash != known_hash:
            results.append(
                {
                    "file": rel,
                    "status": "TAMPERED",
                    "detail": f"哈希不匹配 (known: {known_hash} → current: {current_hash})",
                    "critical": entry["critical"],
                }
            )
            tampered += 1
        else:
            results.append(
                {
                    "file": rel,
                    "status": "OK",
                    "critical": entry["critical"],
                }
            )

    db["last_check_at"] = now.isoformat()
    _save_db(db)

    return {
        "timestamp": now.isoformat(),
        "total": len(results),
        "ok_count": sum(1 for r in results if r["status"] == "OK"),
        "tampered_count": tampered,
        "results": results,
        "clean": tampered == 0,
    }


def show_diff() -> str:
    """show_diff implementation."""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--",
            "AGENTS.md",
            "scripts/governance/",
            "docs/03_modules/infrastructure_runtime_integration/script_system/",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="规则文件完整性保护")
    parser.add_argument(
        "--register",
        action="store_true",
        help="注册当前文件状态为可信基线（需 ZEPHYR_RECONCILER_MODE=1 门禁）",
    )
    parser.add_argument("--check", action="store_true", help="验证文件未被篡改")
    parser.add_argument("--diff", action="store_true", help="显示 git diff")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--warn-only", action="store_true", help="警告模式不阻断")
    args = parser.parse_args()

    if args.register:
        # 红蓝发现4 治本：--register 重置基线 = 合法化当前状态，是危险操作。
        # 加环境变量门禁：只有 ZEPHYR_RECONCILER_MODE=1（reconciler 设置）才允许注册。
        if os.environ.get("ZEPHYR_RECONCILER_MODE") != "1":
            print(
                "[INTEGRITY] 🔴 --register 被门禁阻断：未设置 ZEPHYR_RECONCILER_MODE=1。"
                "基线重置只能由 GitCommitGateway post-commit reconciler 自动执行，"
                "禁止手动重置（防止篡改合法化）。合法更新规则文件请通过 "
                "GitCommitGateway commit（post-commit 自动注册基线）。",
                file=sys.stderr,
            )
            sys.exit(1)
        result = register()
        print(f"[INTEGRITY] ✅ 已注册 {result['count']} 个规则文件的 Hash", file=sys.stderr)
    elif args.diff:
        diff = show_diff()
        if diff:
            print(diff)
        else:
            print("无差异", file=sys.stderr)
    elif args.check:
        result = check()
        if args.json:
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["clean"]:
                print(f"[INTEGRITY] ✅ 全部 {result['total']} 个规则文件完整", file=sys.stderr)
            else:
                print(f"[INTEGRITY] 🔴 {result['tampered_count']} 个文件被修改/缺失", file=sys.stderr)
                for r in result["results"]:
                    if r["status"] != "OK":
                        tag = "🔴" if r["critical"] else "🟡"
                        print(f"  {tag} [{r['status']}] {r['file']}: {r['detail']}", file=sys.stderr)
        should_block = not args.warn_only and not result["clean"]
        sys.exit(2 if should_block else 0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
