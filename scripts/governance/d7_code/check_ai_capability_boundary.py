# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_ai_capability_boundary.py | §
# [MODULE] scripts.governance.d7_code.check_ai_capability_boundary
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
行为说明
--------
- 合并三类路径：merge-base...HEAD（若可解析）、工作区相对 HEAD、暂存区。
- 若变更路径落入矩阵中任一 IMMUTABLE scope，则判违规（须 Owner 审批）。
- 写入 allow/deny 仍以 config/capabilities.yaml（CBAC）为准；本脚本不替代 CBAC。

manifest（供 script_manifest 登记）: dimensions D7, priority P2, warn_only 由 CLI 决定。

exit codes: 0=pass, 1=violations
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  AI 能力边界检查——对比 git 变更与 config/ai_capability_matrix.yaml 中的 IMMUTABLE 路径，
  变更路径落入 IMMUTABLE scope 则判违规。
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: false
"""


import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import yaml

MATRIX_PATH = REPO_ROOT / "config/ai_capability_matrix.yaml"


def _run_git(*args: str, timeout: int = 30) -> tuple[int, str, str]:
    """_run_git implementation."""
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return -1, "", str(exc)


def load_matrix() -> dict | None:
    """load_matrix implementation."""
    if not MATRIX_PATH.exists():
        return None
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def get_immutable_scopes() -> list[str]:
    """get_immutable_scopes implementation."""
    matrix = load_matrix()
    if matrix is None:
        return [
            "src/zephyr/shared/contracts/**/*.py",
            "docs/02_enterprise_architecture/ssot-authority-map.md",
            "docs/01_policies_and_standards/governance/ai/**/*.md",
            "src/zephyr/governance/rule_enforcement/_registry.yaml",
        ]
    scopes: list[str] = []
    for entry in matrix.get("matrix", {}).get("entries", []):
        if entry.get("level") == "IMMUTABLE":
            scopes.append(entry["scope"])
    return scopes


def _matches_scope(file_rel: str, scope: str) -> bool:
    """_matches_scope implementation."""
    import fnmatch

    f = file_rel.replace("\\", "/").strip()
    s = scope.replace("\\", "/").strip()

    if s.endswith("/**"):
        root = s[:-3].rstrip("/")
        return f == root or f.startswith(root + "/")
    if s.endswith("/**/*.md"):
        root = s[:-7].rstrip("/")
        return f.endswith(".md") and (f == root or f.startswith(root + "/"))
    if s.endswith("/**/*.py"):
        root = s[:-7].rstrip("/")
        return f.endswith(".py") and (f == root or f.startswith(root + "/"))
    if s.endswith("/*"):
        prefix = s[:-2].rstrip("/")
        if not f.startswith(prefix + "/"):
            return f == prefix
        rest = f[len(prefix) + 1 :]
        return "/" not in rest
    if s.endswith("/*.py"):
        prefix = s[:-5].rstrip("/")
        if not f.endswith(".py") or not f.startswith(prefix + "/"):
            return f == prefix + ".py"
        rest = f[len(prefix) + 1 :]
        return "/" not in rest and rest.endswith(".py")
    if s.endswith("/*.md"):
        prefix = s[:-5].rstrip("/")
        if not f.endswith(".md") or not f.startswith(prefix + "/"):
            return f == prefix + ".md"
        rest = f[len(prefix) + 1 :]
        return "/" not in rest and rest.endswith(".md")
    return fnmatch.fnmatch(f, s)


def _default_merge_base() -> str | None:
    """_default_merge_base implementation."""
    for remote_base in ("origin/main", "origin/master"):
        rc, _, _ = _run_git("rev-parse", "--verify", remote_base)
        if rc != 0:
            continue
        rc_mb, out, _ = _run_git("merge-base", "HEAD", remote_base)
        if rc_mb == 0 and out.strip():
            return out.strip()
    return None


def get_changed_paths(merge_base: str | None) -> list[str]:
    """合并 PR 范围 diff、未提交与暂存区变更路径（去重）。"""
    chunks: list[str] = []
    if merge_base:
        rc, out, _ = _run_git("diff", "--name-only", "--diff-filter=ACMRT", f"{merge_base}...HEAD")
        if rc == 0 and out.strip():
            chunks.extend(out.splitlines())
    for args in (
        ("diff", "--name-only", "--diff-filter=ACMRT", "HEAD"),
        ("diff", "--cached", "--name-only", "--diff-filter=ACMRT"),
    ):
        rc, out, _ = _run_git(*args)
        if rc == 0 and out.strip():
            chunks.extend(out.splitlines())

    seen: set[str] = set()
    unique: list[str] = []
    for p in chunks:
        norm = p.replace("\\", "/").strip()
        if norm and norm not in seen:
            seen.add(norm)
            unique.append(norm)
    return unique


def find_capability_violations(merge_base: str | None) -> list[dict]:
    """find_capability_violations implementation."""
    immutable = get_immutable_scopes()
    changed = get_changed_paths(merge_base)
    if not changed:
        return []

    violations: list[dict] = []
    for rel in changed:
        rel_n = rel.replace("\\", "/")
        if any(_matches_scope(rel_n, scope) for scope in immutable):
            violations.append(
                {
                    "file": rel_n,
                    "violation": "IMMUTABLE 路径出现在当前变更集中，须 Owner 审批后再合并",
                    "severity": "HIGH",
                }
            )
    return violations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="AI 能力边界（git diff vs IMMUTABLE 矩阵）")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--show-scopes", action="store_true", help="只打印 IMMUTABLE 作用域")
    parser.add_argument(
        "--merge-base",
        default=None,
        help="merge-base 提交：git diff <merge-base>...HEAD（默认自动探测与 origin/main 的 merge-base）",
    )
    args = parser.parse_args()

    if args.show_scopes:
        for scope in get_immutable_scopes():
            print(f"  IMMUTABLE: {scope}")
        return

    matrix = load_matrix()
    if matrix is None:
        print("[CapabilityGuard] ai_capability_matrix.yaml 未找到 — 跳过")
        sys.exit(EXIT_PASS)

    merge_base = args.merge_base if args.merge_base else _default_merge_base()
    if merge_base:
        print(f"[CapabilityGuard] merge-base: {merge_base}")
    else:
        print("[CapabilityGuard] 未找到 origin/main|master — 仅检查工作区与暂存区 diff")

    ver = matrix.get("matrix", {}).get("version", "?")
    print(f"[CapabilityGuard] 能力边界检查 — 矩阵 v{ver}")
    violations = find_capability_violations(merge_base)
    if violations:
        print(f"\n[CapabilityGuard] {len(violations)} 条 IMMUTABLE 路径变更:")
        for v in violations:
            print(f"  [{v['severity']}] {v['file']} — {v['violation']}")
    else:
        print("[CapabilityGuard] 无 IMMUTABLE 路径变更 — 通过")
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
