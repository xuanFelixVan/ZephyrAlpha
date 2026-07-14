# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_trust_tier.py | §
# [MODULE] scripts.governance.meta.validate_trust_tier
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
validate_trust_tier.py — Trust-Tier 门禁执行器



对标 B46（Trust-Tier 决策模型）。

在 pre_commit 和 CI 中运行，检查当前变更是否与 trust_tier_policy.yaml 定义
的文件权限一致。如果 AI 通过 T2 文件直接修改了（跳过了"建议→确认"流程），
则阻断提交并提示。

Usage:
    python scripts/governance/meta/validate_trust_tier.py
    python scripts/governance/meta/validate_trust_tier.py --check-changed-files
    python scripts/governance/meta/validate_trust_tier.py --policy-status
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT

__manifest__ = """
args:
  - --policy-status
  - --warn-only
  - --jsonl
description: Trust-Tier 门禁（变更文件路径与策略 YAML 对账）
dimensions:
- D1
- D11
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path

import yaml

_REPO_ROOT = REPO_ROOT
_POLICY_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "trust_tier_policy.yaml"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_policy() -> dict:
    """_load_policy implementation."""
    with open(_POLICY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_changed_files() -> list[str]:
    """_get_changed_files implementation."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 or not result.stdout.strip():
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(_REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def _match_path(file_path: str, glob_patterns: list[str]) -> bool:
    """_match_path implementation."""
    normalized = file_path.replace("\\", "/")
    for pattern in glob_patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def check_changed_files() -> dict:
    """Check compliance and report findings."""
    policy = _load_policy()
    changed = _get_changed_files()
    violations: list[dict] = []

    for fp in changed:
        for perm in policy.get("file_permissions", []):
            if _match_path(fp, perm["paths"]):
                tier = perm["tier"]
                if tier == "T2":
                    violations.append(
                        {
                            "file": fp,
                            "assigned_tier": "T2",
                            "rule": "修改需 Owner 审批",
                            "detail": perm.get("reason", ""),
                        }
                    )
                break

    return {
        "changed_files": len(changed),
        "violations": violations,
        "violation_count": len(violations),
        "clean": len(violations) == 0,
    }


def policy_status() -> None:
    """policy_status implementation."""
    policy = _load_policy()
    tiers = policy.get("tiers", {})
    print("\n[TRUST-TIER] 当前策略:", file=sys.stderr)
    for tier_name, tier_info in tiers.items():
        allowed = len(tier_info.get("allowed_operations", []))
        forbidden = len(tier_info.get("forbidden_operations", []))
        print(f"  {tier_name}: {tier_info['label']} — {allowed} allowed / {forbidden} forbidden ops", file=sys.stderr)

    file_perms = policy.get("file_permissions", [])
    print(f"\n  文件权限映射 ({len(file_perms)} 组):", file=sys.stderr)
    for fp in file_perms:
        print(
            f"    [{fp['tier']}] {fp['paths'][:3]}{'...' if len(fp['paths']) > 3 else ''} — {fp.get('reason', '')[:60]}",
            file=sys.stderr,
        )


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import json

    parser = argparse.ArgumentParser(description="Trust-Tier policy gate against changed files")
    parser.add_argument("--policy-status", action="store_true", help="仅打印策略摘要")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()

    if args.policy_status:
        policy_status()
        if args.jsonl:
            print(
                json.dumps(
                    {"severity": "INFO", "check_id": "TRUST-TIER", "mode": "policy-status"},
                    ensure_ascii=False,
                )
            )
        return

    result = check_changed_files()

    if result["clean"]:
        print(f"[TRUST-TIER] ✅ 当前 {result['changed_files']} 个已变更文件均符合 Trust-Tier 策略", file=sys.stderr)
        if args.jsonl:
            print(
                json.dumps(
                    {"severity": "INFO", "check_id": "TRUST-TIER", "clean": True, "violations": 0},
                    ensure_ascii=False,
                )
            )
        sys.exit(EXIT_PASS)

    print(f"[TRUST-TIER] ⚠ {result['violation_count']} 个文件涉及 Trust-Tier 限制", file=sys.stderr)
    for v in result["violations"]:
        print(f"  [{v['assigned_tier']}] {v['file']}: {v['rule']} — {v['detail']}", file=sys.stderr)
    print("\n  提示: T2 文件需要 Owner 审批后提交。如果是 Owner 本人操作，请确认后继续。", file=sys.stderr)

    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH",
                    "check_id": "TRUST-TIER",
                    "clean": False,
                    "violations": result["violation_count"],
                },
                ensure_ascii=False,
            )
        )

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
