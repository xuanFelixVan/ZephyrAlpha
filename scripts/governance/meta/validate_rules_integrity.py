# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_rules_integrity.py | §
# [MODULE] scripts.governance.meta.validate_rules_integrity
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
# [TTL] permanent
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
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_INTEGRITY_DB = _SCRIPTS_DIR / "meta" / "rules_integrity_db.json"

# ============================================================
# RULES_MANIFEST 构造（治本3，2026-06-30）：静态条目 + glob 动态条目
# ============================================================
# 第一性原理：保护机制防漏登优先于防误登。
# - 静态条目：核心治理文件 + 治本1② registry YAML + 治本2 配套 commit_gate_registry.py
# - 动态条目：commit_gates/*.py 全量 glob 自动加载（防漏登，新增 gate 自动受保护）
# glob 在模块加载时执行一次，RULES_MANIFEST 仍为稳定 list[dict]，下游消费者透明
# （register/check 仅迭代，不感知静态/动态来源）。

_STATIC_MANIFEST: list[dict] = [
    {"path": "AGENTS.md", "critical": True, "desc": "AI Agent 全局行为约束"},
    {"path": "scripts/governance/quickstart.md", "critical": True, "desc": "AI Session 冷启动卡片"},
    {"path": "scripts/governance/_shared/thresholds.yaml", "critical": True, "desc": "关键阈值 SSoT"},
    {"path": "config/runtime/kill_switch_state.yaml", "critical": True, "desc": "Kill Switch 状态"},
    {"path": "config/runtime/shadow_mode_state.yaml", "critical": False, "desc": "Shadow Mode 状态"},
    {"path": "config/runtime/error_budget_state.yaml", "critical": True, "desc": "Error Budget 状态"},
    {"path": "scripts/governance/quality_standard.md", "critical": True, "desc": "脚本质量标准"},
    {"path": "scripts/governance/script_manifest.yaml", "critical": True, "desc": "脚本注册表"},
    {
        "path": "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py",
        "critical": True,
        "desc": "GATE-ID-UNIQ 检测脚本（A 层 AST 锚点保护 + C 层 golden hash 兜底）",
    },
    # 治本（2026-06-30 病根1 看门人无人看）：治理系统自身的 C 层 golden hash 保护。
    # 红蓝对抗发现 RULES_MANIFEST 9 条清单不含保护机制自身——攻击者篡改 gateway/registry
    # 后 C 层不检测，篡改持久化。本次追加 3 条闭环自指悖论。
    {
        "path": "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
        "critical": True,
        "desc": "GitCommitGateway 主入口(43门禁+串行锁+stash隔离+_commit_auto五重gate)",
    },
    {
        "path": "src/zephyr/gov_audit/reconciliation_registry.py",
        "critical": True,
        "desc": "post-commit reconciler 注册表(17 reconciler+_commit_auto统一入口)",
    },
    {
        "path": "scripts/governance/meta/validate_rules_integrity.py",
        "critical": True,
        "desc": "规则完整性校验器自身(C层golden hash自举保护,防篡改清单本身)",
    },
    # 治本1②（2026-06-30）：capability registry YAML 入保护——
    # 防"删 registry 绕过 create_guard fail-closed"在裸 commit 路径被 C 层检测。
    # critical=True：MISSING（删除）须阻断（防 DoS：攻击者删 registry 锁死全项目 commit）。
    {
        "path": "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
        "critical": True,
        "desc": "capability 索引 + creation_tokens 真源（create_guard/capability_overlap_gate 依赖）",
    },
    # 治本2 配套（2026-06-30）：commit_gate_registry.py 入保护——
    # TEST_EXEMPT_PREFIXES/is_test_exempt 真源将集中于此，是高价值篡改目标
    # （篡改加 \"src/\" 可豁免所有源码绕过 create_guard）。须 C 层 golden hash 保护。
    {
        "path": "src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py",
        "critical": True,
        "desc": "pre-commit 门禁注册表 + tests/豁免真源（TEST_EXEMPT_PREFIXES/is_test_exempt）",
    },
]

# 动态条目：commit_gates/*.py 全量自动加载（治本3，防漏登）。
# 含 __init__.py（保护机制防漏登优先；__init__.py 含 __all__ 声明，篡改可影响包导入）。
# 新增 gate 文件自动受保护——防漏登 > 噪音成本（TAMPERED 是信息性报告，post-commit 自动重基线）。
_GATES_DIR = _REPO_ROOT / "src" / "zephyr" / "governance" / "commit_gates"
_DYNAMIC_GATE_ENTRIES: list[dict] = [
    {
        "path": str(p.relative_to(_REPO_ROOT)).replace("\\", "/"),
        "critical": True,
        "desc": f"pre-commit gate 实现（auto-glob 保护: {p.name}）",
    }
    for p in sorted(_GATES_DIR.glob("*.py"))
]

RULES_MANIFEST: list[dict] = _STATIC_MANIFEST + _DYNAMIC_GATE_ENTRIES

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _normalize_eol(data: bytes) -> bytes:
    """治本（2026-06-30 CRLF/LF 漂移）：normalize CRLF→LF。

    .gitattributes 全局 eol=lf，git HEAD blob 存 LF；但工作树文件可能是
    .gitattributes 生效前 checkout 的（那时 core.autocrlf=true，LF→CRLF），
    git status 因 normalize 比较显示干净，但 Path.read_bytes() 读出 CRLF。
    register() 用 git show HEAD: 返回 LF，check() 用 Path.read_bytes() 返回 CRLF，
    不 normalize 会导致 git 干净的文件被误报 TAMPERED。
    normalize 后两者一致，line ending 差异不再误报为篡改。
    """
    return data.replace(b"\r\n", b"\n")


def _hash_file(file_path: Path) -> str:
    """_hash_file implementation（基于工作树，normalize CRLF→LF 后 hash）。"""
    data = _normalize_eol(file_path.read_bytes())
    return hashlib.sha256(data).hexdigest()[:16]


def _hash_git_head(rel_path: str) -> str | None:
    """基于 git HEAD 状态 hash（红蓝发现3 治本）。

    register() 用此函数而非 _hash_file()，确保基线基于已 commit 状态，
    不基于工作树 WIP——攻击者篡改受保护脚本后 commit 无关文件，
    post-commit --register 不会把 WIP 篡改注册为基线（只注册 HEAD 状态）。
    check() 仍用 _hash_file() 基于工作树状态（检测 WIP 篡改）。

    治本（2026-06-30 CRLF/LF 漂移）：normalize CRLF→LF 后再 hash，
    与 _hash_file() 一致。git show HEAD: 返回 blob 原始字节，若 blob 为
    .gitattributes 前的旧 commit（CRLF），需 normalize 才能与工作树一致。

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
    data = _normalize_eol(result.stdout)
    return hashlib.sha256(data).hexdigest()[:16]


def _load_db() -> dict:
    """_load_db implementation."""
    if not _INTEGRITY_DB.exists():
        return {"files": {}, "registered_at": "", "last_check_at": ""}
    with open(_INTEGRITY_DB, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_db(data: dict) -> None:
    """_save_db implementation."""
    _INTEGRITY_DB.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_INTEGRITY_DB, json_mod.dumps(data, ensure_ascii=False, indent=2))


def register() -> dict:
    """register implementation。

    治本（2026-06-30 自指循环）：仅当 hash 变化或文件数变化时写 db。
    原实现每次都重建 data 并 _save_db，导致 registered_at/last_check_at
    时间戳变化 → db dirty → commit db → reconciler 又跑 register → 循环。
    现改为：读旧 db，计算新 hash，对比；全相同则不写 db（返回 "unchanged"），
    消除自指循环。register 语义从"无条件重写"改为"仅在变化时重写"。
    """
    now = datetime.now(UTC).isoformat()
    old_db = _load_db()
    old_files = old_db.get("files", {})

    new_files: dict = {}
    for entry in RULES_MANIFEST:
        rel = entry["path"]
        # 红蓝发现3 治本：基于 git HEAD 状态 hash，不基于工作树 WIP。
        git_hash = _hash_git_head(rel)
        if git_hash is not None:
            new_files[rel] = {
                "hash": git_hash,
                "critical": entry["critical"],
                "desc": entry["desc"],
            }
        else:
            # 文件不在 git HEAD（新文件/未跟踪）→ 回退到工作树状态
            fp = _REPO_ROOT / rel
            if fp.exists():
                new_files[rel] = {
                    "hash": _hash_file(fp),
                    "critical": entry["critical"],
                    "desc": entry["desc"],
                }

    # 治本（自指循环）：hash 全相同则不写 db，消除 register→commit db→register 循环。
    # registered_at 保留旧值（基线未变）；last_check_at 也保留旧值（register 不是 check）。
    if new_files == old_files:
        return {"status": "unchanged", "count": len(new_files), "at": old_db.get("registered_at", now)}

    data = {
        "files": new_files,
        "registered_at": now,
        "last_check_at": old_db.get("last_check_at", ""),
    }
    _save_db(data)
    return {"status": "registered", "count": len(new_files), "at": now}


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
