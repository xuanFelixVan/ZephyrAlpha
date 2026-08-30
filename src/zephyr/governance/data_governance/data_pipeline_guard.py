# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_pipeline_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据管道完整性检查不可跳过;陈旧数据必须检测
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Data Pipeline Guard — v0.10.0 数据管道完整性防护: schema validation+row count check+checksum verify。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: data_pipeline_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① DataPipelineGuard
#   name_en: DataPipelineGuard
#   intro: class DataPipelineGuard 源码 L53-L65
#   desc: 公共方法（定义序）: validate_schema, verify_checksum, check_row_count；源码 L53-L65
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DataPipelineGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib


class DataPipelineGuard:
    def validate_schema(self, actual_columns: list[str], expected_columns: list[str]) -> list[str]:
        return list(set(expected_columns) - set(actual_columns))

    def verify_checksum(self, data: str, expected: str) -> bool:
        actual = hashlib.sha256(data.encode()).hexdigest()[:8]
        return actual == expected

    def check_row_count(self, actual: int, expected: int, tolerance_pct: int = 5) -> bool:
        if expected == 0:
            return actual == 0
        diff = abs(actual - expected) / expected * 100
        return diff <= tolerance_pct
