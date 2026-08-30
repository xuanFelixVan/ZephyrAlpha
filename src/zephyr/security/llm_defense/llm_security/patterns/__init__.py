# [BLUEPRINT] MOD-LLM_SECURITY | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-SEC-patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① PatternRegistry
#   name_en: PatternRegistry
#   intro: class PatternRegistry 源码 L60-L68
#   desc: 公共方法（定义序）: register, match；源码 L60-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PatternRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "PRECOMPILED_ENCODING",
    "InjectionPattern",
    "injection_patterns",
    "scan_direct",
    "scan_encoding_escape",
    "scan_indirect",
    "scan_jailbreak",
    "scan_path_traversal",
    "scan_secrets",
    "scan_semantic_attacks",
    "scan_shell",
    "scan_sql",
    "secrets",
]


class PatternMatch:
    def __init__(self, pattern_type, value, confidence=1.0):
        self.pattern_type = pattern_type
        self.value = value
        self.confidence = confidence


class PatternRegistry:
    def __init__(self):
        self._patterns = []

    def register(self, pattern):
        self._patterns.append(pattern)

    def match(self, text):
        return []
