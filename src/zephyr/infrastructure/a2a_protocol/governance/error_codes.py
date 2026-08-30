# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.error_codes
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: error_codes.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: ErrorCode, ErrorSeverity, GovernanceError
#   desc: 数据契约/异常/枚举声明共 3 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（3 类）
#   name_en: data classes
#   intro: ErrorCode, ErrorSeverity, GovernanceError
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class ErrorCode:
    UNKNOWN = "UNKNOWN"
    INVALID_REQUEST = "INVALID_REQUEST"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    PROTOCOL_VIOLATION = "PROTOCOL_VIOLATION"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"


class ErrorSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GovernanceError(Exception):
    error_code = "ZA-IF-0011"

    def __init__(self, code, message, severity=None, error_code: str | None = None):
        self.code = code
        self.message = message
        self.severity = severity or ErrorSeverity.MEDIUM
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code


ERR_GATE_FAILED = "GATE_FAILED"

ERR_INTERNAL_ERROR = "INTERNAL_ERROR"

ERR_INVALID_PARAMS = "INVALID_PARAMS"

ERR_INVALID_REQUEST = "INVALID_REQUEST"

ERR_METHOD_NOT_FOUND = "METHOD_NOT_FOUND"

ERR_PARSE_ERROR = "PARSE_ERROR"
ERR_UNAUTHORIZED = "UNAUTHORIZED"
ERR_FORBIDDEN = "FORBIDDEN"
ERR_CONFLICT = "CONFLICT"
ERR_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
ERR_SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
ERR_VERSION_MISMATCH = "VERSION_MISMATCH"
ERR_QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
ERR_VALIDATION_FAILED = "VALIDATION_FAILED"
ERR_DEPENDENCY_FAILED = "DEPENDENCY_FAILED"
ERR_CIRCUIT_OPEN = "CIRCUIT_OPEN"

ERR_RBAC_DENIED = "RBAC_DENIED"

ERR_TOOL_EXECUTION = "TOOL_EXECUTION"

ERR_TOOL_NOT_FOUND = "TOOL_NOT_FOUND"

ERR_RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"

ERR_PROTOCOL_VIOLATION = "PROTOCOL_VIOLATION"
