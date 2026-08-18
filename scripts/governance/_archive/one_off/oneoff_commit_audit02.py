#!/usr/bin/env python
# [MODULE] scripts.governance._archive.one_off.oneoff_commit_audit02
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_COMMIT_AUDIT02 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""One-off: commit 9 config YAML audit-02 fixes via GitCommitGateway escape hatch.

User authorized the allow_non_worktree escape hatch (WORKTREE-REQUIRED gate blocks
non-worktree commit while a live concurrent session is active). Content verified
clean: only these 9 config YAMLs are staged (no 搭便车 of other sessions' WIP).

Scope (audit-02 governance anchor completeness):
  - 7 YAMLs: add missing `ttl: permanent` to B_yaml anchor block (6-field completeness)
  - compression_policy.yaml: ttl + module_id/blueprint GOV-DOC-011 -> MOD-INF-002
  - sla_targets.yaml: ttl + module_id/blueprint SRC-142/MOD-INF_sla_monitor -> MOD-INF-016

Excluded (separate governance-gated handling):
  - rule YAMLs (trae_047 etc.): PROTECTED under docs/01_policies_and_standards/rules/
    (IRN-010, Owner approval required)
  - 5 manual permanent scripts (check_module_id_consistency.py, check_yaml_anchor_consistency.py,
    scan_complexity.py, scan_consumers_accuracy.py, detect_constraint_violations.py):
    blocked by MANUAL-ONLY-PERMANENT gate (not m11-exempt)
  - any_type_inferrer.py: m11-exempt but diff intermixed with concurrent ruff-format pass
  - test_check_yaml_anchor_consistency.py: coupled to uncommitted checker (would break CI)
  - noqa_exempt_registry.yaml: intermixed with concurrent session entries
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

PROJECT_ROOT = str(_REPO_ROOT)
SESSION_ID = "audit02-fixes"

FILES = [
    "config/budget_policy.yaml",
    "config/capabilities.yaml",
    "config/compression_policy.yaml",
    "config/embedding_model_registry.yaml",
    "config/model_pricing.yaml",
    "config/nav_table_mapping.yaml",
    "config/resource_optimization.yaml",
    "config/risk_params.yaml",
    "config/sla_targets.yaml",
]

MESSAGE = """fix(governance): 补全 config YAML 治理锚定 ttl 字段并修正幻影 module_id 引用

审计02 治理锚定一致性（B_yaml 6字段完整性）修复：
- 9 个 config YAML 补全锚定块缺失的 ttl: permanent 字段
- compression_policy.yaml：module_id/blueprint GOV-DOC-011 -> MOD-INF-002
- sla_targets.yaml：module_id/blueprint SRC-142/MOD-INF_sla_monitor -> MOD-INF-016
"""


def main() -> int:
    gw = GitCommitGateway(project_root=PROJECT_ROOT)

    claimed = gw.claim_files(SESSION_ID, FILES, adopt_prior_work=True)
    conflicts = [f for f in FILES if f not in claimed]
    if conflicts:
        print(f"WARN: {len(conflicts)} files held by other session: {conflicts}", file=sys.stderr)
    print(f"Claimed {len(claimed)}/{len(FILES)} files for session={SESSION_ID}")

    try:
        result = gw.commit(
            session_id=SESSION_ID,
            files=FILES,
            message=MESSAGE,
            allow_non_worktree=True,
        )
        print(f"Commit result: status={result.status}, message={result.message}")
        sha = getattr(result, "commit_hash", None) or getattr(result, "sha", None) or getattr(result, "commit_sha", None)
        if sha:
            print(f"Commit SHA: {sha}")
        return 0 if str(result.status) == "OK" else 1
    finally:
        try:
            gw.release_files(SESSION_ID, claimed)
        except Exception as e:  # noqa: BLE001
            print(f"WARN: release_files failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
