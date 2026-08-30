# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.exit_codes
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.gov_code_quality.code_dedup.cli; tests/gov_code_dedup/test_degradation_edge.py; tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governance/ops/test_exit_codes.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_severity 参数
#   fields: 参数 max_severity，类型注解 str
#   code: exit_codes.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: mode 参数
#   fields: 参数 mode，类型注解 RunMode
#   code: exit_codes.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: tool_error 参数
#   fields: 参数 tool_error，类型注解 bool
#   code: exit_codes.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: degraded 参数
#   fields: 参数 degraded，类型注解 bool
#   code: exit_codes.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① determine_exit_code_mode
#   name_en: determine_exit_code_mode
#   intro: 根据运行模式和最大严重度判定退出码。
#   desc: 根据运行模式和最大严重度判定退出码。 5.96.4 修复：用 RunMode 枚举替代 (tool_error, degraded) 双布尔参数，消除隐式优先级，提升可读性。；源码 L101-L114
#   inputs: max_severity mode
#   outputs: ExitCode
# - id: A2
#   name_zh: ② determine_exit_code
#   name_en: determine_exit_code
#   intro: 根据最大严重度和运行状态判定退出码（向后兼容入口）。
#   desc: 根据最大严重度和运行状态判定退出码（向后兼容入口）。 5.96.4 修复：内部映射到 RunMode 枚举后委托给 determine_exit_code_mode， 消除双布尔…；源码 L117-L129
#   inputs: max_severity tool_error degraded
#   outputs: ExitCode
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ExitCode
#   name_en: ExitCode
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_code_quality.code_dedup.cli; tests/gov_code_dedup/test_degradation_e…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

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
