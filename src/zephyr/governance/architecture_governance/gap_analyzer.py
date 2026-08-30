# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.gap_analyzer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 间隙分析不可跳过;事件缺失必须触发告警
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Gap Analyzer — v0.8.0 间隙分析器: escalation覆盖缺口扫描+新操作类型识别。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gap_analyzer.py
# 层: 算法
# - id: A1
#   name_zh: ① GapAnalyzer
#   name_en: GapAnalyzer
#   intro: class GapAnalyzer 源码 L51-L87
#   desc: 公共方法（定义序）: covered_operations, observed_operations, register_coverage, observe_operation, find_gaps, coverage…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: GapAnalyzer
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class GapAnalyzer:
    def __init__(self):
        self._covered_operations: set[str] = set()
        self._observed_operations: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def covered_operations(self) -> set[str]:
        """只读：covered_operations（Stage 4 公共化）。"""
        return self._covered_operations

    @covered_operations.setter
    def covered_operations(self, value):
        """写入：covered_operations（Stage 4 公共化）。"""
        self._covered_operations = value

    @property
    def observed_operations(self) -> set[str]:
        """只读：observed_operations（Stage 4 公共化）。"""
        return self._observed_operations

    @observed_operations.setter
    def observed_operations(self, value):
        """写入：observed_operations（Stage 4 公共化）。"""
        self._observed_operations = value

    def register_coverage(self, operation_type: str):
        self._covered_operations.add(operation_type)

    def observe_operation(self, operation_type: str):
        self._observed_operations.add(operation_type)

    def find_gaps(self) -> list[str]:
        return list(self._observed_operations - self._covered_operations)

    def coverage_ratio(self) -> float:
        return len(self._covered_operations) / max(1, len(self._observed_operations))
