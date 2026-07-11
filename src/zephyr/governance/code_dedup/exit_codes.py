# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.exit_codes
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.code_dedup.cli; tests/code_dedup_engine/test_degradation_edge.py; tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governance/ops/test_exit_codes.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_exit_codes | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑."""

from enum import Enum, IntEnum
from typing import Final


class ExitCode(IntEnum):
    PASS = 0
    WARN = 1
    ERROR = 2
    TOOL_ERROR = 3
    DEGRADED = 4


class RunMode(Enum):
    """运行模式枚举，替代 determine_exit_code 的 (tool_error, degraded) 双布尔参数。"""

    NORMAL = "normal"
    DEGRADED = "degraded"
    TOOL_ERROR = "tool_error"


EXIT_CODE_DESCRIPTIONS: Final[dict] = {
    ExitCode.PASS: "PASS — 扫描范围内零重复组 -> GATE-DEDUP PASS",
    ExitCode.WARN: "WARN — 发现低/中严重度重复（severity≤medium）-> GATE-DEDUP WARN 不阻断",
    ExitCode.ERROR: "ERROR — 发现高/严重重复（severity=high/critical）-> GATE-DEDUP FAIL 阻断commit",
    ExitCode.TOOL_ERROR: "TOOL-ERROR — 扫描器自身故障（AST解析失败/cache损坏且自愈失败/git不可用）-> GATE-DEDUP SKIP 记录审计",
    ExitCode.DEGRADED: "DEGRADED — 降级运行完成（某Stage失败但降级到更低Stage完成扫描）-> GATE-DEDUP PASS with DEGRADED",
}


def determine_exit_code_mode(max_severity: str, mode: RunMode = RunMode.NORMAL) -> ExitCode:
    """根据运行模式和最大严重度判定退出码。

    5.96.4 修复：用 RunMode 枚举替代 (tool_error, degraded) 双布尔参数，消除隐式优先级，提升可读性。
    """
    if mode is RunMode.TOOL_ERROR:
        return ExitCode.TOOL_ERROR
    if mode is RunMode.DEGRADED:
        return ExitCode.DEGRADED
    if max_severity in ("high", "critical"):
        return ExitCode.ERROR
    if max_severity in ("low", "medium"):
        return ExitCode.WARN
    return ExitCode.PASS


def determine_exit_code(max_severity: str, tool_error: bool = False, degraded: bool = False) -> ExitCode:
    """根据最大严重度和运行状态判定退出码（向后兼容入口）。

    5.96.4 修复：内部映射到 RunMode 枚举后委托给 determine_exit_code_mode，
    消除双布尔参数切换返回逻辑的可读性问题。
    """
    if tool_error:
        mode = RunMode.TOOL_ERROR
    elif degraded:
        mode = RunMode.DEGRADED
    else:
        mode = RunMode.NORMAL
    return determine_exit_code_mode(max_severity, mode)
