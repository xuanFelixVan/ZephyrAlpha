# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.contract
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_contract | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CT-RBK-GATE-001 集成契约落地——Rollback System Exit Code 完整定义。

依据: 蓝图 MOD-INF-021 §9 + MOD-MASTER_BLUEPRINT §4

全部 46 个 exit code 枚举 + Gate 判定映射 + Pipeline 行为映射。
"""

from enum import IntEnum


class RollbackExitCode(IntEnum):
    SUCCESS = 0
    PREFLIGHT_GIT_UNAVAILABLE = 1
    PREFLIGHT_DIRTY_TREE = 2
    PREFLIGHT_DETACHED_HEAD = 3
    PREFLIGHT_REBASE_IN_PROGRESS = 4
    PREFLIGHT_MERGE_IN_PROGRESS = 5
    PREFLIGHT_REMOTE_AHEAD = 6
    ROLLBACK_TARGET_STALE = 7
    ROLLBACK_LOCK_ACQUIRE_FAILED = 8
    ROLLBACK_LOCK_TIMEOUT = 9
    ROLLBACK_BUDGET_EXCEEDED = 10
    GIT_REVERT_CONFLICT = 11
    MORPHING_DETECTED = 12
    VULN_REINTRODUCED = 13
    DB_INTEGRITY_FAILED = 14
    DB_RESTORE_FAILED = 15
    G0_VERIFY_FAILED = 16
    G1_VERIFY_FAILED = 17
    G2_VERIFY_FAILED = 18
    G3_VERIFY_FAILED = 19
    G4_VERIFY_FAILED = 20
    G5_VERIFY_FAILED = 21
    G6_SECRETS_LEAK = 22
    DRIFT_DETECTED_BY_GUARD = 23
    HALLUCINATION_DETECTED = 24
    SANDBOX_BREACH = 25
    AGENT_COOLDOWN_ACTIVE = 26
    KILL_SWITCH_L1_SESSION = 27
    KILL_SWITCH_L2_SKILL = 28
    KILL_SWITCH_L3_GLOBAL = 29
    LOOP_DETECTED = 30
    ROLLBACK_ABUSE_DETECTED = 31
    FORWARD_FIX_FAILED_2X = 32
    DRILL_MELTDOWN = 33
    MODEL_DRIFT_DETECTED = 34
    IN_FLIGHT_CRASH_RECOVERY = 35
    REBASE_IN_PROGRESS = 36
    LOW_CONFIDENCE_CONSEC = 37
    COMPLEXITY_OVER_BUDGET = 38
    SANDBOX_BREACH_DETECTED = 39
    CONNECTION_POOL_FAILED = 40
    PROMPT_INJECTION_FILTERED = 41
    TARGET_STALE_OVER_30D = 42
    CREDENTIAL_LEAK_DETECTED = 43
    ROLLBACK_ABUSE_DETECTED_44 = 44
    ROLLBACK_WAL_INCOMPLETE = 45
    INTENT_ARCHIVE_PRUNE = 46
    MCP_IRREVERSIBLE = 47
    NOTIFICATION_THROTTLED = 48
    SELF_AUDIT_CONFLICT = 49
    GIT_BINARY_MISMATCH = 50


ExitCode = RollbackExitCode


EXIT_CODE_TO_GATE_ACTION: dict[int, tuple[str, str]] = {
    0: ("PASS", "No action needed"),
    1: ("FAIL", "Defer rollback - git unavailable"),
    2: ("FAIL", "Defer rollback - stash/clean first"),
    3: ("WARN", "Detached HEAD - manual checkout recommended"),
    4: ("BLOCK", "Rebase in progress - abort or complete first"),
    5: ("BLOCK", "Merge in progress - abort or complete first"),
    6: ("WARN", "Remote ahead - pull-merge before rollback"),
    7: ("WARN", "Rollback target >30 days old"),
    8: ("RETRY", "Lock acquisition retry"),
    9: ("RETRY", "Lock timeout - queue and retry"),
    10: ("WARN", "Budget exceeded - switch to forward-fix"),
    11: ("FAIL", "Revert conflict - manual resolution required"),
    12: ("L2_KILL", "Morphing detected - L2 Skill Kill"),
    13: ("DEFER_HUMAN", "CVE reintroduced - manual evaluation"),
    14: ("WARN", "DB integrity failed - attempt self-heal"),
    15: ("RETRY", "DB restore retry"),
    16: ("WARN", "G0 file/syntax check failed"),
    17: ("WARN", "G1 lint check failed"),
    18: ("WARN", "G2 type check failed"),
    19: ("WARN", "G3 test check failed"),
    20: ("WARN", "G4 security check failed"),
    21: ("WARN", "G5 audit check failed"),
    22: ("L3_KILL", "G6 secrets leak - L3 Global Kill"),
    23: ("ROLLBACK", "Drift detected - auto-rollback triggered"),
    24: ("PAUSE_AGENT", "Hallucination detected - suspend agent"),
    25: ("L3_KILL", "Sandbox breach - L3 Global Kill"),
    26: ("BLOCK", "Agent cooldown active - wait 5min"),
    27: ("BLOCK", "L1 Session Kill - no writes allowed"),
    28: ("BLOCK", "L2 Skill Kill - file-type restriction"),
    29: ("BLOCK", "L3 Global Kill - hard stop"),
    30: ("PAUSE_AUTO", "Rollback loop detected - disable auto-rollback"),
    31: ("L2_KILL", "Rollback abuse pattern detected"),
    32: ("FALLBACK_REVERT", "Forward-fix failed 2x - revert now"),
    33: ("BLOCK_AUTO", "Drill meltdown - ALL automatic rollback suspended"),
    34: ("WARN", "Model behavior drift detected"),
    35: ("WARN", "In-flight crash recovery needed"),
    36: ("BLOCK", "Rebase in progress detected"),
    37: ("REDUCE_TIER", "Low confidence consecutive - tier reduction"),
    38: ("WARN", "Complexity budget exceeded"),
    39: ("L3_KILL", "Sandbox breach - L3 Global Kill"),
    40: ("RETRY", "Connection pool failed - retry with backoff"),
    41: ("BLOCK", "Prompt injection filtered - operation blocked"),
    42: ("WARN", "Target >30 days stale"),
    43: ("L3_KILL", "Credential leak detected"),
    44: ("L2_KILL", "Rollback abuse - L2 Skill Kill"),
    45: ("WARN", "Rollback WAL incomplete"),
    46: ("L2_KILL", "Intent archive pruned - L2 Skill Kill"),
    47: ("BLOCK", "MCP irreversible command detected"),
    48: ("WARN", "Notification throttled - rate limit"),
    49: ("WARN", "Self-audit conflict detected"),
    50: ("BLOCK", "Git binary integrity mismatch"),
}


PIPELINE_ACTIONS: dict[str, str] = {
    "PASS": "Continue pipeline execution normally.",
    "FAIL": "Stop pipeline immediately. Require manual intervention.",
    "WARN": "Log warning. Continue pipeline but increment caution counter.",
    "BLOCK": "Block current operation. Do not proceed until resolved.",
    "RETRY": "Automatically retry with backoff (max 3 attempts).",
    "L2_KILL": "Activate L2 Skill Kill Switch. Stop all same-type operations.",
    "L3_KILL": "Activate L3 Global Kill Switch. Stop ALL automated operations.",
    "DEFER_HUMAN": "Suspend automated decision. Route to human operator.",
    "ROLLBACK": "Initiate immediate auto-rollback to previous stable state.",
    "PAUSE_AGENT": "Pause the offending AI agent session.",
    "PAUSE_AUTO": "Pause automatic rollback for this target combination.",
    "BLOCK_AUTO": "Block all automatic rollbacks across the system.",
    "REDUCE_TIER": "Reduce AI agent autonomy tier from current to one level lower.",
    "FALLBACK_REVERT": "Abort forward-fix path. Fallback to git revert.",
}


def get_gate_action(exit_code: int) -> tuple[str, str]:
    return EXIT_CODE_TO_GATE_ACTION.get(exit_code, ("UNKNOWN", "Unknown exit code"))


def get_pipeline_action(gate_action: str) -> str:
    return PIPELINE_ACTIONS.get(gate_action, "Unknown pipeline action")


def resolve_exit_code(exit_code: int) -> dict[str, str]:
    gate, desc = get_gate_action(exit_code)
    pipeline = get_pipeline_action(gate)
    return {
        "exit_code": str(exit_code),
        "gate_action": gate,
        "description": desc,
        "pipeline_action": pipeline,
    }
