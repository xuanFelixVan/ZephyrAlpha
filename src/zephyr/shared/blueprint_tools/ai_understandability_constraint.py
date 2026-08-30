# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.blueprint_tools.ai_understandability_constraint
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_line_length 参数
#   fields: 参数 max_line_length（无注解）
#   code: ai_understandability_constraint.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_nesting 参数
#   fields: 参数 max_nesting（无注解）
#   code: ai_understandability_constraint.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: min_comment_ratio 参数
#   fields: 参数 min_comment_ratio（无注解）
#   code: ai_understandability_constraint.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AiUnderstandabilityConstraint
#   name_en: AiUnderstandabilityConstraint
#   intro: class AiUnderstandabilityConstraint 源码 L71-L91
#   desc: 公共方法（定义序）: check；源码 L71-L91
#   inputs: max_line_length max_nesting min_comment_ratio
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AiUnderstandabilityConstraint
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UnderstandabilityResult:
    content: str
    score: float
    passed: bool
    violations: list[str]


class AiUnderstandabilityConstraint:
    def __init__(self, max_line_length: int = 120, max_nesting: int = 4, min_comment_ratio: float = 0.0):
        self._max_line_length = max_line_length
        self._max_nesting = max_nesting
        self._min_comment_ratio = min_comment_ratio

    def check(self, content: str) -> UnderstandabilityResult:
        violations = []
        lines = content.split("\n")
        long_lines = sum(1 for l in lines if len(l) > self._max_line_length)
        if long_lines > 0:
            violations.append(f"{long_lines} lines exceed {self._max_line_length} chars")
        max_depth = 0
        for line in lines:
            if line.strip():
                depth = (len(line) - len(line.lstrip())) // 4
                max_depth = max(max_depth, depth)
        if max_depth > self._max_nesting:
            violations.append(f"nesting depth {max_depth} exceeds {self._max_nesting}")
        score = max(0.0, 1.0 - len(violations) * 0.3)
        return UnderstandabilityResult(content, score, len(violations) == 0, violations)
