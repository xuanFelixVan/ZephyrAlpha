# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.gap_analyzer

# [INVARIANTS] 间隙分析不可跳过;事件缺失必须触发告警

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Gap Analyzer — v0.8.0 间隙分析器: escalation覆盖缺口扫描+新操作类型识别。
"""
from __future__ import annotations

class GapAnalyzer:
    def __init__(self):
        self._covered_operations:set[str]=set()
        self._observed_operations:set[str]=set()

    def register_coverage(self, operation_type:str):
        self._covered_operations.add(operation_type)

    def observe_operation(self, operation_type:str):
        self._observed_operations.add(operation_type)

    def find_gaps(self)->list[str]:
        return list(self._observed_operations-self._covered_operations)

    def coverage_ratio(self)->float:
        return len(self._covered_operations)/max(1,len(self._observed_operations))
